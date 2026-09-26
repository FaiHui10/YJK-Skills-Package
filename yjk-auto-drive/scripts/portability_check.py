# -*- coding: utf-8 -*-
r"""可移植性自检：扫描整套 YJK 技能，找出「依赖特定设备 / 特定工程」的写法。

为什么需要它
------------
这套技能的目标是**放到任何一台机器、任何工程上都能跑**。破坏可移植性的写法
通常不会报错，只会在换机器/换工程后静默出错，极难排查。典型：

  * 写死盘符 / 用户名 / 桌面路径（`C:\Users\xxx\...`、`~/Desktop/...`）
  * 写死 YJK 安装位置（`C:/YJKS`）而不是探测
  * 写死解释器路径（某个具体 python.exe）
  * 写死某个工程的参数（固定柱号分组表、逐层等级表、具体模型文件名…）
  * **SQL 列名是"猜"的**（P7，警告级）：手写 `INSERT INTO <表> (...)` / `UPDATE <表> SET <列>`
    里的列名没有按表定义（`PRAGMA table_info`）核对过

本脚本把这些模式列出来，配合**显式白名单**（说明为什么某处可以例外），
当作**回归护栏**：允许现状，但不允许新增。

判定只针对**真实代码**：注释与文档字符串里的举例、设计说明不算耦合。
文档（.md）另有一套「死引用」检查。

扫描范围
--------
`yjk-dev-refs/` **不扫**：那是 YJK 官方随盘给的案例与接口文档（第三方素材），
里面必然带着厂商自己机器的盘符（`C:\Users\10497\Desktop\...`、`E:\MyProject\...`）。
它们不是本技能包的可移植性契约对象，也不归本技能改 —— 扫它只会让退出码永远为 1，
把真正的回归信号淹掉。

严重级
------
* **高 / 中**：阻断级 —— 出现在报告里就会让退出码变 1。
* **警告**：只提示、**不阻断**（`P7` 用它）。这类写法"可能对、也可能是错"，静态判不出来
  （列名到底是不是实列要看库），所以不能拿它卡住流水线；但允许用白名单
  **逐条记录已核对的例外**（`ALLOW`，每条都要写理由）。

用法
----
  python portability_check.py                # 扫描本技能所在的整套 skills 目录
  python portability_check.py --root <dir>   # 指定扫描根
  python portability_check.py --quiet        # 只打印问题与结论
  python portability_check.py --list-allow   # 打印白名单

退出码：0 = 无新增**阻断级**问题；1 = 发现未在白名单里的高/中级写法。
"""
from __future__ import annotations

import argparse
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(HERE)                 # .../yjk-auto-drive
DEFAULT_ROOT = os.path.dirname(SKILL_DIR)         # .../skills

# ----------------------------------------------------------------- 扫描规则
# (规则号, 严重级, 正则, 说明)  —— 只对 .py 的**真实代码行**生效
RULES = [
    ("P1", "高",
     re.compile(r"(?<![A-Za-z0-9_$%])[A-Za-z]:[\\/]"),
     "写死的盘符绝对路径（换机器/换盘符即失效）"),
    ("P2", "高",
     re.compile(r"/(?:Users|home)/[A-Za-z0-9_.\-]+"),
     "写死的 POSIX 用户目录"),
    ("P3", "高",
     re.compile(r"Desktop[\\/]+yjk|[\"']Desktop[\"']", re.I),
     "依赖「桌面」目录（技能不应假定放在桌面）"),
    ("P4", "中",
     re.compile(r"(?i)anaconda"),
     "假定用户装了 Anaconda（不是所有机器都有）"),
    ("P5", "高",
     re.compile(r"0807|新会|银海|YJK工程_R2|R2_opt|M3_g"),
     "写死某个具体工程的名称/模型名"),
    ("P6", "高",
     re.compile(r"\b(?:GRADE_ZONES|STD_GRADE|GROUP_OF)\b\s*=\s*[{\[]"),
     "写死某工程的等级表/柱号分组表（换工程静默出错）"),
    ("P7", "警告",
     re.compile(r"(?i)\bINSERT\s+(?:OR\s+\w+\s+)?INTO\s*[\[\"'`]?\w+[\]\"'`]?\s*"
                r"\(\s*[A-Za-z_]\w*\s*(?:,\s*[A-Za-z_]\w*\s*)*\)"),
     "手写 INSERT 列名表：列名是猜的（没有按 PRAGMA table_info 派生）"),
    ("P7", "警告",
     re.compile(r"(?i)\bUPDATE\s+[\[\"'`]?\w+[\]\"'`]?\s+SET\s+[A-Za-z_]\w*\s*="),
     "手写 UPDATE SET 列名：列名是猜的（没有按 PRAGMA table_info 派生）"),
]

CODE_EXT = (".py",)
DOC_EXT = (".md",)
# 不扫的目录：
#   * 缓存/虚拟环境 —— 不是源码；
#   * `yjk-dev-refs` —— **YJK 官方随盘的案例与接口文档**（第三方素材），
#     必然带厂商机器的盘符（实测 17 处），扫它只会让退出码永远为 1、淹掉真信号。
SKIP_DIRS = ("__pycache__", ".git", ".venv", "venv", "yjk-dev-refs")
# 警告级：只提示、不影响退出码（判定不了"对/错"，只能提示去核对）
WARN_SEV = "警告"
# 文档里连「死引用」都不该有的字符串（这些路径已经废弃）
DOC_DEAD = [
    (re.compile(r"Desktop[\\/]+yjk-auto-drive"), "文档里残留已废弃的桌面路径引用"),
    (re.compile(r"Users[\\/]+<user>"), "文档里残留写死的用户名占位路径"),
    (re.compile(r"[A-Za-z]:[\\/]yjkapi"), "文档里残留写死的文档盘符路径"),
]

# ----------------------------------------------------------------- 白名单
# (文件名/路径 子串, 行内子串 或 None=整文件豁免, 理由)
# ★ 新增例外必须写清理由 —— 白名单不是「消除告警」，而是「记录已评估的例外」。
ALLOW = [
    ("portability_check.py", None,
     "自检脚本本身：规则定义、示例字符串、白名单条目"),
    ("selfcheck.py", None,
     "自检测试向量：用 D:\\ / G:\\ / Z:\\ 等假路径构造用例，不依赖真实设备"),
    ("paths.py", "WindowsPowerShell",
     "PowerShell 路径兜底（优先 SystemRoot 环境变量）"),
    ("paths.py", "SystemRoot",
     "Windows 目录兜底（优先读 SystemRoot 环境变量）"),
    ("paths.py", "C:\\Python3*",
     "解释器探测的通用 glob 兜底（全技能唯一维护处）"),
    ("paths.py", "Program Files\\Python3*",
     "解释器探测的通用 glob 兜底（全技能唯一维护处）"),
    ("paths.py", "ProgramData",
     "解释器 / Config.ini 的常见位置兜底（探测优先于兜底）"),
    ("paths.py", "anaconda3",
     "解释器探测的常见安装位兜底（不是运行时依赖）"),
    ("paths.py", "miniconda3",
     "解释器探测的常见安装位兜底（不是运行时依赖）"),
    ("paths.py", "C:/D:/E:",
     "文档字符串：说明「任意盘符都支持」这一设计目标"),
    ("yjk_auto.py", "WindowsPowerShell",
     "PowerShell 路径兜底（优先 SystemRoot）"),
    ("yjk_auto.py", "SystemRoot",
     "Windows 目录兜底（优先读 SystemRoot 环境变量）"),
    ("env.py", "HKLM",
     "注册表键名（不是文件路径）"),
    ("yjk_api.py", "%s:\\",
     "按本机盘符**枚举**常见安装位置（不写死具体盘）"),
    ("yjk_api.py", "不写死 C:/D:/E:",
     "文档字符串：说明该函数不写死盘符"),
    ("verify_results.py", 'r"X:\\s*λc=',
     "正则表达式字面量：匹配 wpj 文本里的「X: λc=」，不是路径"),
    ("verify_results.py", 'r"Y:\\s*λc=',
     "正则表达式字面量：匹配 wpj 文本里的「Y: λc=」，不是路径"),
    ("yjk_quant.py", "YJK.CUI",
     "注释：说明命令名取自 YJK.CUI（举例，非运行时依赖）"),
    ("real-project.md", None,
     "真实工程作业指引：示例与表格均为通用口径，不是运行依赖"),
    ("report-spec.md", None,
     "报告规格文档：以某工程为例说明页签结构"),
    ("setup-checklist.md", None,
     "装机清单：路径均以「如 / 例」形式举例"),
    ("commands.md", None,
     "命令登记表：引用 YJK.CUI 的路径作为出处说明"),
    ("troubleshooting.md", "窗口标题",
     "排查文档：窗口标题举例（示意目录级标题，非依赖）"),
    # ---- P7（SQL 列名是猜的，警告级）已逐条核对过的例外 ------------------------
    # 核对方法：对真实模型库执行 `PRAGMA table_info(<表>)`（见各自的理由），
    # 确认列名确实是该表的实列。**没有核对过的别往这里加** —— 加白名单不是消警告，
    # 是记录"已经评估过"。真实教训：某序列化器把 `tblLoadSeg.No` 写成 `No_`，
    # 一句都不报错，784 条梁上均布线荷载在导入时整批被丢弃。
    ("split_stdflr.py", "UPDATE tblFloor SET",
     "列名 StdFlrID/idNewBzc/No_ 经 PRAGMA 核对为 tblFloor 实列"),
    ("split_stdflr.py", "UPDATE tblStdFlr SET Height",
     "Height/ID 经 PRAGMA 核对为 tblStdFlr 实列"),
    ("split_stdflr.py", "UPDATE tblStdFlr SET Para",
     "Para/ID 经 PRAGMA 核对为 tblStdFlr 实列"),
    ("split_stdflr.py", "UPDATE tblStdFlr SET No_",
     "No_/ID 经 PRAGMA 核对为 tblStdFlr 实列（本表序列列就叫 No_）"),
    ("split_stdflr.py", "UPDATE tblStdFlrPara SET ParaVal",
     "ParaVal/StdFlrID/Kind 经 PRAGMA 核对为 tblStdFlrPara 实列"),
    ("split_stdflr.py", "INSERT INTO tblStdFlrPara",
     "(StdFlrID, Kind, ParaVal) 经 PRAGMA 核对为 tblStdFlrPara 的全部实列"),
    ("write_sections.py", "UPDATE tblProperty SET ShapeVal",
     "ShapeVal/ID/Name 经 PRAGMA 核对为 tblProperty 实列"),
    ("write_sections.py", "UPDATE tblStdFlr SET Para",
     "Para/ID 经 PRAGMA 核对为 tblStdFlr 实列"),
    ("write_sections.py", "UPDATE tblStdFlrPara SET ParaVal",
     "ParaVal/StdFlrID/Kind 经 PRAGMA 核对为 tblStdFlrPara 实列"),
    ("write_sections.py", "UPDATE tblColSeg SET SectID",
     "SectID/idNewDef 经 PRAGMA 核对为 tblColSeg 实列"),
    ("ydb_serialize.py", "UPDATE tblProjectPara SET ParaVal",
     "ParaVal/ID 经 PRAGMA 核对为 tblProjectPara 实列（该模块的 INSERT 是列全集派生，见 add()）"),
    ("projpara.py", "UPDATE tblProjectPara SET ParaVal",
     "ParaVal/ID 经 PRAGMA 核对为 tblProjectPara 实列（本技能唯一一处写参数表）"),
]


def _strip_comment(s):
    """去掉 `#` 之后的注释（粗略处理字符串内的 # 与转义）。"""
    quote = None
    for k, ch in enumerate(s):
        if quote:
            if ch == quote and s[k - 1] != "\\":
                quote = None
        elif ch in "'\"":
            quote = ch
        elif ch == "#":
            return s[:k]
    return s


def code_only(txt):
    """返回 {行号: 去注释、去三引号字符串后的代码} —— 只对真实代码判定。"""
    out = {}
    open_q = None
    for i, raw in enumerate(txt.splitlines(), 1):
        s = raw
        if open_q:
            j = s.find(open_q)
            if j < 0:
                out[i] = ""
                continue
            s = " " * (j + 3) + s[j + 3:]
            open_q = None
        while True:
            m = re.search(r"'''|\"\"\"", s)
            if not m:
                break
            q = m.group(0)
            j = s.find(q, m.end())
            if j < 0:
                open_q = q
                s = s[:m.start()]
                break
            s = s[:m.start()] + " " * (j + 3 - m.start()) + s[j + 3:]
        out[i] = _strip_comment(s)
    return out


def _allowed(rel, line):
    for pat, needle, _why in ALLOW:
        if pat in rel and (needle is None or needle in line):
            return True
    return False


def scan_file(path, rel):
    """返回 [(行号, 规则号, 严重级, 说明, 行内容)]。"""
    try:
        txt = io.open(path, encoding="utf-8", errors="replace").read()
    except OSError:
        return []
    ext = os.path.splitext(path)[1].lower()
    lines = txt.splitlines()
    hits = []
    if ext in CODE_EXT:
        code = code_only(txt)
        for i, line in enumerate(lines, start=1):
            if _allowed(rel, line):
                continue
            c = code.get(i, "")
            if not c.strip():
                continue                     # 注释 / 文档字符串：不算耦合
            for rid, sev, rx, note in RULES:
                if rx.search(c):
                    hits.append((i, rid, sev, note, line.strip()))
    elif ext in DOC_EXT:
        for i, line in enumerate(lines, start=1):
            if _allowed(rel, line):
                continue
            for rx, note in DOC_DEAD:
                if rx.search(line):
                    hits.append((i, "D1", "高", note, line.strip()))
    return hits


def main():
    ap = argparse.ArgumentParser(description="YJK 技能可移植性自检")
    ap.add_argument("--root", default=DEFAULT_ROOT, help="扫描根目录（默认：整套 skills）")
    ap.add_argument("--quiet", action="store_true", help="只打印问题与结论")
    ap.add_argument("--list-allow", action="store_true", help="打印白名单后退出")
    a = ap.parse_args()

    if a.list_allow:
        print("白名单（已评估的例外）：")
        for pat, needle, why in ALLOW:
            print("  %-26s %-30s %s" % (pat, needle if needle else "(整文件)", why))
        return 0

    root = os.path.abspath(a.root)
    if not os.path.isdir(root):
        raise SystemExit("扫描根不存在：%s" % root)

    if not a.quiet:
        print("=" * 92)
        print("可移植性自检：%s" % root)
        print("=" * 92)
        for rid, sev, _rx, note in RULES:
            print("  %s [%s] %s" % (rid, sev, note))
        print()

    nfile = 0
    bad, warn = [], []
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in SKIP_DIRS]
        for f in sorted(fn):
            if os.path.splitext(f)[1].lower() not in CODE_EXT + DOC_EXT:
                continue
            p = os.path.join(dp, f)
            rel = os.path.relpath(p, root).replace("\\", "/")
            nfile += 1
            for h in scan_file(p, rel):
                (warn if h[2] == WARN_SEV else bad).append((rel,) + h)

    # ---- 结构自检：业务技能必须能跨机器找到驱动 -------------------------------
    struct = []
    for sk in ("column-section-opt", "floor-system-comparison", "yjk-draw-takeoff"):
        d = os.path.join(root, sk, "scripts")
        if not os.path.isdir(d):
            continue
        joined = ""
        for f in os.listdir(d):
            if f.endswith(".py"):
                try:
                    joined += io.open(os.path.join(d, f), encoding="utf-8",
                                      errors="replace").read()
                except OSError:
                    pass
        if "YJK_SKILLS_DIR" not in joined and "YJK_AUTO_DRIVE_DIR" not in joined:
            struct.append("%s：脚本里没有 YJK_SKILLS_DIR / YJK_AUTO_DRIVE_DIR 兜底定位" % sk)

    print("扫描 %d 个文件（.py + .md）" % nfile)
    if bad:
        print("\n发现 %d 处未列入白名单的写法（阻断级）：" % len(bad))
        cur = None
        for rel, ln, rid, sev, note, txt in bad:
            if rel != cur:
                cur = rel
                print("\n  %s" % rel)
            print("    %4d  [%s/%s] %s" % (ln, rid, sev, note))
            print("          %s" % (txt[:110]))
    else:
        print("\n[OK] 未发现未列入白名单的设备/工程耦合写法")

    if warn:
        print("\n警告 %d 处（**不阻断退出码**，但请按提示核对，或改成从 "
              "PRAGMA table_info 派生列名）：" % len(warn))
        cur = None
        for rel, ln, rid, sev, note, txt in warn:
            if rel != cur:
                cur = rel
                print("\n  %s" % rel)
            print("    %4d  [%s/%s] %s" % (ln, rid, sev, note))
            print("          %s" % txt[:110])
        print("  说明：这类写法静态判不出对错（列名到底是不是实列要看库），所以只提示；")
        print("        核对无误的请**逐条**加进 ALLOW 并写明理由（别整文件豁免）。")
    else:
        print("[OK] 无警告级写法（SQL 列名都已核对，或已逐条列入白名单）")

    if struct:
        print("\n结构自检未通过：")
        for s in struct:
            print("  ! %s" % s)
    else:
        print("[OK] 结构自检通过（业务技能都能跨机器定位驱动）")

    print("\n结论：%s" % ("**不通过**" if (bad or struct) else "通过"))
    return 1 if (bad or struct) else 0


if __name__ == "__main__":
    sys.exit(main())
