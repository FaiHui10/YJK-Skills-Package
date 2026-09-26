# -*- coding: utf-8 -*-
r"""跨 agent 兼容性守卫：六份「查找实现」的能力矩阵 + frontmatter 体检。

为什么需要它
------------
"找驱动技能/找技能根目录"这段逻辑在本包里被**复制了六份**（各技能必须能独立安装，
所以在找到驱动目录之前没法 import 它的 paths.py，只能各留一份最小回退）。复制本身
可以接受，**但它们会漂移** —— 实际就漂移过：

* 有一段时期，同一个厂商的路径出现在部分副本里、通用扫描只在另一部分副本里；
* 于是"能不能找到"取决于用户恰好跑了哪个脚本；
* 更要命的是**本机之所以一直"看着能用"，是因为家目录里正好有一份
  `~/.workbuddy-ai/skills/yjk-auto-drive/`**（别人装的旧副本）—— 换台机器就全崩。

所以有了这个守卫：**六份副本必须都具备同一组最低能力**，少一项就报错。
它只做静态检查（读源码文本），不需要 YJK、不需要 pythonnet，秒级。

判据（六份副本**每一份**都必须满足）
--------------------------------
1. **环境变量兜底**：至少认两个 `YJK_*`（`YJK_SKILLS_DIR` / `YJK_AUTO_DRIVE_DIR` /
   `YJK_DRIVER_DIR`）。没有它就"技能不在预期位置时完全没法救"。
2. **同级/相对路径**：能从"本技能旁边"找到（`dirname`/`parent`/`..` 之类）。
3. **与厂商无关的通用扫描**：至少出现 `.agent-skills`、`.skills`、`.config` 之一。
4. **找不到时明确报错**：出现 `SystemExit` 或"退出码 2"式的显式失败，不许静默返回空。
5. **不写死桌面**：不得出现 `Desktop` / `桌面` 作为**查找路径**。

另外顺带体检 5 个 `SKILL.md` 的 YAML frontmatter（多数 agent 靠它发现技能）。

还守一类**技能之间的重复副本**：有些文件在两个技能里各存一份完整拷贝、本应
逐字节相同，只改一份就会静默行为分叉（见 `DUPLICATE_COPIES`，整文件 sha256 比对）。
它与 `selfcheck.py` 的 T31 互补 —— T31 只比那一段 `COMPAT-FALLBACK` 块，这里比整个文件。

用法
----
    python compat_check.py                # 体检整包（自动定位包根）
    python compat_check.py --root <包根>
退出码 0 = 全部满足；1 = 有缺项（会逐条点名）。
"""
from __future__ import annotations

import argparse
import hashlib
import os
import re
import sys
import time

# 六份查找实现（相对包根）。新增副本时请一并加进来 —— 否则它不受守卫保护。
FINDERS = [
    ("column-section-opt", "scripts/driver.py"),
    ("floor-system-comparison", "scripts/yjk_api.py"),
    ("floor-system-comparison", "scripts/draw_quant.py"),
    ("floor-system-comparison", "scripts/yjk_quant.py"),
    ("floor-system-comparison", "scripts/run_all_yjk.py"),
    ("yjk-draw-takeoff", "scripts/draw_quant.py"),
]

# 技能之间的「逐字节相同的重复副本」（**整文件**，不是片段）。
# 为什么需要：这些文件在两个技能里各存一份完整拷贝（为了两个技能都能独立安装），
# 本应逐字节相同。只改其中一份，行为就**静默分叉** —— 而且两份都还能跑，
# 于是「结果对不对取决于用户恰好用了哪个技能」，极难回溯。
#
# 与 selfcheck.py 的 T31 的区别：T31 比的是每个文件里那一段 `COMPAT-FALLBACK` 块
# （行尾归一化后逐字节），只管「找驱动技能」那一段；这里比的是**整个文件**，
# 并且覆盖 read_yjk_xlsx / dlgwatch / impcheck 这些 T31 根本不看的文件。
# 新增重复副本时请一并加进来 —— 否则它不受守卫保护。
DUPLICATE_COPIES = [
    ("scripts/draw_quant.py", "floor-system-comparison", "yjk-draw-takeoff"),
    ("scripts/read_yjk_xlsx.py", "floor-system-comparison", "yjk-draw-takeoff"),
    ("scripts/dlgwatch.py", "floor-system-comparison", "yjk-draw-takeoff"),
    ("scripts/impcheck.py", "floor-system-comparison", "yjk-draw-takeoff"),
]

ENV_VARS = ("YJK_SKILLS_DIR", "YJK_AUTO_DRIVE_DIR", "YJK_DRIVER_DIR")
GENERIC_MARKERS = (".agent-skills", ".skills", ".config")
RELATIVE_MARKERS = ("dirname", "SKILL_DIR", "HERE", "parent", '".."', "'..'")

# 退出码纪律（见 check_exit_discipline()）：收集了 problems 的脚本必须能给出非零退出码。
# ★ 三种形态都算「非零退出路径」：`sys.exit(非0)` / `sys.exit(main())` / `raise SystemExit(...)`。
#   最后一种最容易漏判：col_data.py 用的是 `raise SystemExit(1)`，
#   只认 sys.exit 会把它误报成「只打印 !! 就收场，退出码仍是 0」。
NONZERO_EXIT = re.compile(r"sys\.exit\(\s*(?!0\s*\))[^)]*\)")
EXIT_MAIN = re.compile(r"sys\.exit\(\s*main\(\)\s*\)")
RAISE_EXIT = re.compile(r"raise\s+SystemExit\(\s*(?![0)\s]*\))[^)]*\)")

SKILLS = ["yjk-auto-drive", "column-section-opt", "floor-system-comparison",
          "column-scheme-comparison", "yjk-draw-takeoff"]


def pkg_root(start=None):
    """从本脚本位置往上找到含 5 个技能目录的那一层。"""
    d = os.path.abspath(start or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
    for _ in range(4):
        if all(os.path.isdir(os.path.join(d, s)) for s in SKILLS):
            return d
        d = os.path.dirname(d)
    return None


def check_finder(root, skill, rel):
    """返回 (问题列表, 能力标记 dict)。"""
    p = os.path.join(root, skill, rel)
    if not os.path.exists(p):
        return ["文件不存在"], {}
    txt = open(p, encoding="utf-8", errors="replace").read()
    caps = {
        # 三个环境变量是 README 明确承诺的（缺任何一个，就会出现
        # 「只设这一个变量时，有的脚本找得到、有的找不到」的不一致）
        "环境变量": all(v in txt for v in ENV_VARS),
        "同级相对": any(m in txt for m in RELATIVE_MARKERS),
        "通用扫描": any(m in txt for m in GENERIC_MARKERS),
        "明确报错": ("SystemExit" in txt) or ("退出码 2" in txt) or ("exit(2)" in txt),
        "无桌面写死": not re.search(r'["\'][^"\']*Desktop|桌面[\\/]|["\']桌面', txt),
    }
    bad = [k for k, ok in caps.items() if not ok]
    # 环境变量用了哪些（仅信息，不判死）
    used = [v for v in ENV_VARS if v in txt]
    return [("缺能力：%s" % "、".join(bad))] if bad else [], {
        "caps": caps, "envs": used}


def check_frontmatter(root):
    out = []
    for s in SKILLS:
        p = os.path.join(root, s, "SKILL.md")
        if not os.path.exists(p):
            out.append((s, "**缺 SKILL.md**", 0))
            continue
        lines = open(p, encoding="utf-8").read().splitlines()
        if not lines or lines[0].strip() != "---":
            out.append((s, "**无 frontmatter**", 0))
            continue
        keys, desc = [], ""
        for l in lines[1:]:
            if l.strip() == "---":
                break
            if ":" in l:
                k, v = l.split(":", 1)
                k = k.strip()
                keys.append(k)
                if k == "description":
                    desc = v.strip()
        miss = [k for k in ("name", "description") if k not in keys]
        note = "OK（desc %d 字）" % len(desc) if not miss else "**缺 %s**" % ",".join(miss)
        endswith = desc.rstrip().endswith(("时使用", "时使用。", "使用。"))
        if desc and not endswith:
            note += "  ← 结尾不是触发句，靠结尾路由的 agent 可能漏掉"
        out.append((s, note, len(desc)))
    return out


def _ts(t):
    """mtime -> 好读的本地时间。"""
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t))


def check_duplicate_copies(root):
    """整文件 sha256 比对「技能间的重复副本」。

    返回 (rows, problems)：rows 供打印（rel, 技能A, 技能B, 说明, 是否一致）；
    problems 供判死。

    本函数**只报警、绝不自动同步**：两份不一致时，从这里无法判断哪一份才是
    「对」的（也可能两份都不对），所以它不改任何文件，只把两份的哈希与改动
    时间并排摆出来，让人自己定。替别人挑一份覆盖另一份，可能把对的那份冲掉。
    """
    rows, problems = [], []
    for rel, skill_a, skill_b in DUPLICATE_COPIES:
        pa = os.path.join(root, skill_a, rel)
        pb = os.path.join(root, skill_b, rel)
        miss = [s for s, p in ((skill_a, pa), (skill_b, pb)) if not os.path.exists(p)]
        if miss:
            rows.append((rel, skill_a, skill_b,
                         "**副本缺失**：%s" % "、".join(miss), False))
            problems.append("%s：副本缺失（%s）—— 两个技能本该各存一份"
                            % (rel, "、".join(miss)))
            continue
        ba = open(pa, "rb").read()
        bb = open(pb, "rb").read()
        if ba == bb:
            rows.append((rel, skill_a, skill_b,
                         "一致（%d 字节 sha256=%s）"
                         % (len(ba), hashlib.sha256(ba).hexdigest()[:12]), True))
            continue
        ha = hashlib.sha256(ba).hexdigest()
        hb = hashlib.sha256(bb).hexdigest()
        ma, mb = os.path.getmtime(pa), os.path.getmtime(pb)
        newer = skill_b if mb > ma else skill_a
        rows.append((rel, skill_a, skill_b,
                     "**分叉**（%s vs %s）" % (ha[:12], hb[:12]), False))
        problems.append(
            "%s：两份重复副本已分叉（整文件不一致）\n"
            "        %-24s %7d 字节  sha256=%s  改动时间=%s\n"
            "        %-24s %7d 字节  sha256=%s  改动时间=%s\n"
            "        → 最近被改的是「%s」。先用 fc /L（或 diff -u）看差异，"
            "确认哪一份才是对的，\n"
            "          再把对的那份整文件覆盖另一份。"
            "本守卫**不替你决定**改哪一份；\n"
            "          若两份都该改，就两份一起改成一样；改完重跑 compat_check.py。"
            % (rel, skill_a, len(ba), ha[:16], _ts(ma),
               skill_b, len(bb), hb[:16], _ts(mb), newer))
    return rows, problems


def check_exit_discipline(root):
    """退出码纪律：**收集了 problems 的脚本必须有非零退出路径**。

    为什么需要（同一族缺陷踩了两次，第二次后果特别重）
    ------------------------------------------------
    调用方（agent / 编排器 / colopt）**只认退出码**，所以「屏幕上报了问题、
    退出码却是 0」= 把坏东西当成功交出去：

    * `write_sections.py` 老版把三个自检的返回值丢掉 → 「一层都没写」照样打印
      「完成。」+ 退出码 0；
    * `split_stdflr.py` 老版的最后一条自检（`idNewBzc` 必须逐行等于所属标准层的
      `idNew`）不通过时**只 print 一行 `!!`**，退出码仍是 0 —— 而那条自检的后果
      是「YJK 导入丢弃自然层（`tblFloor=0`）→ 楼层组装塌掉 → 几何全丢」。
      实测：把 `tblFloor.idNewBzc` 全写坏后，老版 **rc=0**（文件照写），修好后 rc=1。

    判据（静态，读源码文本）：出现 `problems.append(` 的文件，必须同时存在
    `sys.exit(非0)` 或 `sys.exit(main())` 这类**非零退出路径**。
    """
    rows, problems = [], []
    for dp, _dn, fn in os.walk(root):
        if "__pycache__" in dp:
            continue
        for f in sorted(fn):
            if not f.endswith(".py"):
                continue
            p = os.path.join(dp, f)
            try:
                t = open(p, encoding="utf-8").read()
            except OSError:
                continue
            if "problems.append(" not in t:
                continue
            rel = os.path.relpath(p, root)
            n = len(re.findall(r"problems\.append\(", t))
            ok = bool(NONZERO_EXIT.search(t) or EXIT_MAIN.search(t)
                      or RAISE_EXIT.search(t))
            rows.append((rel, n, ok))
            if not ok:
                problems.append(
                    "%s：收集了 %d 处 problems 却**没有任何非零退出路径**"
                    "（只打印 !! 就收场，退出码仍是 0）" % (rel, n))
    return rows, problems


def main():
    # 控制台兜底必须在 main() 里调用：本文件会被别的脚本 import 当库用
    # （那时不会走 `if __name__ == "__main__"` 分支），而下面会打印 ✅/❌ ——
    # 默认 GBK 控制台下 print 会抛 UnicodeEncodeError，一个其实"全部通过"的
    # 检查会被判成崩溃失败。重复调用无害（内部有 try/except）。
    _utf8_console()
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=None)
    a = ap.parse_args()
    root = pkg_root(a.root)
    if not root:
        print("!! 找不到包根（其下应有 5 个技能目录）。用 --root 指定。")
        return 2

    print("=" * 96)
    print("跨 agent 兼容性守卫：%s" % root)
    print("=" * 96)

    problems = []
    print("\n[1] 六份「查找实现」的能力矩阵（缺任一项即失败）")
    hdr = "   %-46s %-6s %-6s %-6s %-6s %-7s  %s" % (
        "文件", "环境变量", "同级相对", "通用扫描", "明确报错", "无桌面写死", "认得的 YJK_* 变量")
    print(hdr)
    print("   " + "-" * 92)
    for skill, rel in FINDERS:
        bad, info = check_finder(root, skill, rel)
        label = "%s/%s" % (skill, rel)
        if not info:
            print("   %-46s  !! %s" % (label, bad[0]))
            problems.append("%s：%s" % (label, bad[0]))
            continue
        c = info["caps"]
        mark = lambda b: "OK" if b else "**缺**"
        print("   %-46s %-6s %-6s %-6s %-6s %-7s  %s" % (
            label, mark(c["环境变量"]), mark(c["同级相对"]), mark(c["通用扫描"]),
            mark(c["明确报错"]), mark(c["无桌面写死"]), ",".join(info["envs"]) or "（无）"))
        for b in bad:
            problems.append("%s：%s" % (label, b))

    print("\n[2] 5 个 SKILL.md 的 frontmatter（多数 agent 靠它发现技能）")
    for s, note, n in check_frontmatter(root):
        print("   %-28s %s" % (s, note))
        if "缺" in note or "无 frontmatter" in note:
            problems.append("%s/SKILL.md：%s" % (s, note))

    print("\n[3] 技能间重复副本：整文件逐字节一致（只改一份就会静默分叉）")
    dup_rows, dup_problems = check_duplicate_copies(root)
    for rel, skill_a, skill_b, note, _ok in dup_rows:
        print("   %-26s %-24s == %-24s  %s" % (rel, skill_a, skill_b, note))
    problems.extend(dup_problems)

    print("\n[4] 退出码纪律：收集了 problems 的脚本必须有非零退出路径")
    ex_rows, ex_problems = check_exit_discipline(root)
    for rel, n, ok in ex_rows:
        print("   %-56s problems×%-3d %s" % (rel, n, "OK" if ok else "**无非零退出**"))
    if not ex_rows:
        print("   （没有这类脚本）")
    problems.extend(ex_problems)

    print("\n" + "=" * 96)
    if problems:
        print("结论：❌ %d 项不合格 —— 换 agent/换机器时行为会不一致：" % len(problems))
        for p in problems:
            print("   · %s" % p)
        print("\n（六份副本必须都具备同一组最低能力；只修其中几份，"
              "就会出现「能不能找到取决于跑了哪个脚本」。）")
        print("（技能间重复副本必须**两份一起改**：只改一份，行为就会静默分叉"
              "—— 结果取决于用户恰好用了哪个技能。）")
        print("（收集了 problems 的脚本必须给非零退出码：调用方只认退出码，"
              "「报了问题却 rc=0」等于把坏模型当成功交出去。）")
        return 1
    print("结论：✅ 通过 —— 六份查找实现能力一致、%d 组重复副本逐字节一致、"
          "%d 个 reporter 脚本退出码纪律合规，5 个 SKILL.md 均可被发现"
          % (len(DUPLICATE_COPIES), len(ex_rows)))
    return 0


def _utf8_console():
    """让输出在任何控制台编码下都不崩（GBK 下把不可编码字符替换掉）。

    为什么需要：本包会打印 ✅ ❌ ⚠ −(U+2212) ² ³ 等**非 cp936** 字符，
    默认 GBK 控制台下 print 会抛 UnicodeEncodeError 并**以退出码 1 中断**，
    于是一个其实已经成功的任务（比如文件已经落盘）会被上层判成失败。
    errors=replace 让它在 UTF-8 控制台下原样输出、在 GBK 下退化成 ?，都不崩。

    只在 `main()` 里调用一次，**不在模块顶层**调用：本文件会被别人 import 当库用，
    在模块顶层无条件改 stdout 会污染 import 它的进程。重复调用无害。
    """
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(errors="replace")
        except Exception:
            pass


if __name__ == "__main__":
    _utf8_console()
    sys.exit(main())
