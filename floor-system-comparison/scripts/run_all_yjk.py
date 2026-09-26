# -*- coding: utf-8 -*-
r"""把 5 个方案依次送进 YJK 实算，或只复核既有结果。

每个方案一次独立 host 调用（清理→启动→UINew→importydb→预处理→官方计算链→收尾）。
为什么不共用一个常驻实例：常驻收件箱可能中途停摆，
一次一跑虽然多花 ~30s 启动，但**每一轮都是干净的**，排障成本低得多。

★ 判据（只认客观证据，三条全过才算成功）：
  1. **导入忠实度**：源 ydb 与算后 ymd 的**逐表行数完全一致**
     （早期版本拿"save 后 .ymd 字节数 == 源 ydb"判断 —— 不可靠：
      文件页分配会差 ±1 页(4096B)，而偶发的表重建也会改变体积。行数才是硬证据。）
  2. `设计结果/check.out`（UTF-16）包含"未发现问题"；
  3. `设计结果/wpj*.out` 的 mtime 必须晚于本轮开工时间。

用法：
  python run_all_yjk.py --all           # ★ 实跑全部 5 个方案（必须显式给 --all）
  python run_all_yjk.py S0 S1           # 实跑指定方案
  python run_all_yjk.py --verify        # ★ 不复算，只复核既有结果（只读，无参=复核全部）
  python run_all_yjk.py --help          # 只打印帮助 —— 绝不启动任何 YJK

★ 安全约定（本文件 main 的注释里有完整来龙去脉）：**没显式指定方案就什么都不跑**。
  敲 --help / 敲错选项都不该变成「实跑全套 YJK、覆盖工程目录」。
"""
import argparse
import os
import re
import sqlite3
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))


#>>> COMPAT-FALLBACK BEGIN —— 六份副本必须**一致**：内容逐字节相同，行尾各随本文件自身
# 约定（本包既有 LF 也有 CRLF 文件，比对时按行尾归一化，不算漂移）。selfcheck.py 的 T31 守着。
# 为什么这六份是**故意**重复的：业务技能在找到驱动技能目录之前，没法 import 它的
# paths.py（鸡生蛋），所以每份必须自带一段最小回退。按本包契约
# `yjk-auto-drive/scripts/paths.py` 才是"唯一找东西的地方"，因此这段回退**只保留三样**：
#   ① 环境变量（三个都认） ② 同级目录 ③ 与厂商无关的通用扫描 + 中立位置
# 其余一切（YJK 安装位置 / Config.ini / 官方 DLL / 解释器）一律委托给 paths.py ——
# **别往这里加东西**，加了就又少一处"只维护一次"。
#
# 为什么需要这道守卫：这六份**漂移过**。曾经同一个厂商的路径出现在部分副本里、通用扫描
# 只在另一部分副本里，于是"能不能找到驱动"取决于用户恰好跑了哪个脚本；更隐蔽的是本机
# 一直"看着能用"，只不过因为家目录里正好有一份别人装的旧副本 —— 换台机器就全崩。
#
# 产出的是 **<技能> 目录**（不含 scripts），调用方自己拼 "scripts"。做成生成器是有意的：
# 候选链"命中即停"，最后那档家目录扫描只在前面几档都落空时才付费。
_COMPAT_SCAN_CAP = 40           # 只取前 N 个一级子目录：家目录塞满几万个条目也不能拖慢启动


def _compat_subdirs(base, cap=_COMPAT_SCAN_CAP):
    """`base` 下的一级子目录名 —— **先全量排序、再取前 cap 个**。

    为什么必须先排序再截断：`os.scandir` 的返回顺序是文件系统的顺序（换机器、增删文件都会
    变），若"边扫边收满 cap 就停"，留下的那批就是随机的 —— 同一台机器两次跑可能命中不同
    目录。排序后再截断才是**确定的子集**：候选顺序可复现，故障也可复现。
    只列一级、**不递归**（递归家目录在大机器上要几十秒，定位一个技能不该这么贵）。

    目录不存在 / 无权限一律返回 []：这是"猜位置"，猜不到就该继续走下一档候选，
    绝不能因为某个目录读不了就让整条定位链崩掉。
    """
    try:
        with os.scandir(base) as it:
            names = []
            for e in it:
                try:
                    if e.is_dir():
                        names.append(e.name)
                except OSError:                 # 断链 / 权限：单个条目读不了就跳过
                    continue
    except OSError:                             # 目录本身不存在或无权限
        return []
    names.sort()
    return names[:cap]


def _compat_cwd():
    """当前目录（进程的工作目录被删掉时 `os.getcwd()` 会抛 OSError）。"""
    try:
        return os.getcwd()
    except OSError:
        return None


def _compat_driver_dirs(skill="yjk-auto-drive", cap=_COMPAT_SCAN_CAP):
    """`<技能>` 目录的候选链；顺序即优先级，命中即止。

    为什么要"枚举"而不是"再抄一个厂商名"：本包原来只认一个厂商的技能目录，换到别的
    agent/IDE 上那个目录**根本不存在**，而用户最自然的装法恰恰是"把整套技能丢进我的技能
    目录"—— 于是底座明明就在旁边，却报「找不到 yjk-auto-drive」。再抄第二个厂商名只是把
    问题推迟到第三个 agent，所以改成**扫家目录下的一级子目录**：任何
    `~/.<任意名>/skills/` 都能命中，且不需要知道对方叫什么。
    """
    v = os.environ.get("YJK_DRIVER_DIR")            # ① 环境变量：指向 <技能>/scripts
    if v:
        yield os.path.dirname(v)
    v = os.environ.get("YJK_AUTO_DRIVE_DIR")        #               指向 <技能>
    if v:
        yield v
    v = os.environ.get("YJK_SKILLS_DIR")            #               指向整套技能的根
    if v:
        yield os.path.join(v, skill)
    yield os.path.join(HERE, "..", "..", skill)     # ② 同级目录：装机默认形态，最可靠
    yield os.path.join(HERE, "..", skill)
    cwd = _compat_cwd()                             # ③ 当前目录
    if cwd:
        yield os.path.join(cwd, skill)
        yield os.path.join(cwd, "..", skill)
    home = os.path.expanduser("~")                  # ④ 与厂商无关：各 agent 的技能家目录
    for base in (home, os.path.join(home, ".config")):
        for d in _compat_subdirs(base, cap):
            p = os.path.join(base, d)
            yield os.path.join(p, "skills", skill)  #    `~/.<任意名>/skills/<技能>`
            yield os.path.join(p, skill)            #    `~/.<任意名>/<技能>`
    yield os.path.join(home, ".agent-skills", skill)    # ⑤ 中立约定位置
    yield os.path.join(home, ".skills", skill)
    if cwd:
        yield os.path.join(cwd, ".skills", skill)
    # ⑥ 历史遗留路径：保留以不破坏现有用户（这是**兼容项**，不是厂商假设，别当例子抄）
    yield os.path.join(home, ".workbuddy-ai", "skills", skill)
#<<< COMPAT-FALLBACK END


def _find_driver_yjk_auto():
    """找 yjk-auto-drive/scripts/yjk_auto.py；找不到返回 None。

    候选链见上面那段 `COMPAT-FALLBACK` —— 六份副本**一致**（内容逐字节相同，行尾各随本文件）。

    只保留三样：环境变量 → 同级目录 → 与厂商无关的通用扫描 + 中立位置，
    最后是历史遗留路径（保留以不破坏现有用户）。**不含任何具体厂商名、盘符、
    用户名或桌面路径**（桌面探测早已删除：技能不该假定自己放在桌面）。
    要改就六份一起改，并跑 `selfcheck.py`（T31 逐字节比对）与 `compat_check.py`。
    """
    for d in _compat_driver_dirs():
        p = os.path.join(d, "scripts", "yjk_auto.py")
        if os.path.exists(p):
            return os.path.abspath(p)
    return None


SKILL = _find_driver_yjk_auto()
if not SKILL:
    sys.stderr.write(
        "找不到 yjk-auto-drive/scripts/yjk_auto.py。\n"
        "请把 yjk-auto-drive 目录放在与本技能同级的 skills 目录下，或设置环境变量\n"
        "YJK_DRIVER_DIR 指向该技能的 scripts 目录，或设置 YJK_SKILLS_DIR 指向整套技能的\n"
        "安装根目录。（把整套技能放进任意 agent 的用户级技能目录也能被自动找到。）\n")
    sys.exit(2)
PY = sys.executable
MODELS = os.path.join(ROOT, "models")
RUN = os.path.join(ROOT, "YJK_run")
ORDER = ["S0", "S1", "S2", "S3", "S4"]

# 逐表行数比对的表（覆盖几何 + 截面 + 层）
TABLES = ["tblStdFlr", "tblFloor", "tblJoint", "tblAxis", "tblGrid",
          "tblBeamSect", "tblBeamSeg", "tblColSect", "tblColSeg", "tblSlab"]


def _decode_check(path):
    """check.out 是 UTF-16LE（带 BOM），别用 GBK 读。"""
    with open(path, "rb") as fh:
        raw = fh.read()
    for enc in ("utf-16", "utf-8-sig", "gbk"):
        try:
            return raw.decode(enc)
        except (UnicodeDecodeError, UnicodeError):
            continue
    return raw.decode("utf-8", errors="replace")


def _die(msg):
    """「工具没跑成」→ **退出码 2**（与"做完了但结论/产物不合格"的 1 分开）。"""
    try:
        sys.stderr.reconfigure(errors="replace")   # GBK 控制台下也不崩
    except (AttributeError, ValueError):
        pass
    sys.stderr.write(msg.rstrip("\n") + "\n")
    sys.exit(2)


def _rows(path, tables=TABLES):
    """逐表行数；打开前先守卫 —— 源模型缺失时给中文报错，不抛裸 OperationalError。

    ★ 为什么：本函数对 `ydb`（**源模型**）没有存在性守卫（`ymd` 那一侧有），
      源模型缺失时 `mode=ro` 抛的是 `sqlite3.OperationalError: unable to open
      database file` —— 复核脚本里冒出一个裸 traceback，看不出是哪个文件、
      也看不出是"路径写错"还是"库损坏"。另外 0 字节/非 sqlite 的文件
      `connect()` 是**成功**的，报错会推迟到第一条查询 —— 所以四件事一次做完。
    """
    p = os.path.abspath(str(path))
    if not os.path.exists(p):
        _die("模型库不存在：%s\n"
             "  常见原因：源模型还没建（先跑 make_ydb.py/build_floor.py）或路径拼错。\n"
             "  本脚本**只读**打开，不会创建文件。" % p)
    if os.path.isdir(p):
        _die("给的是目录，不是模型库文件：%s" % p)
    if os.path.getsize(p) == 0:
        _die("模型库是 0 字节（半写/损坏）：%s" % p)
    try:
        con = sqlite3.connect("file:%s?mode=ro" % p.replace("\\", "/"), uri=True)
        con.execute("PRAGMA schema_version").fetchone()   # 把"不是数据库"提前探出来
    except sqlite3.Error as e:
        _die("打不开模型库 %s：%s\n"
             "  常见原因：不是 sqlite 库（拿错文件）/ 库已损坏。" % (p, e))
    out = {}
    try:
        for t in tables:
            try:
                out[t] = con.execute("select count(*) from %s" % t).fetchone()[0]
            except sqlite3.Error:
                out[t] = None
    finally:
        con.close()
    return out


def verify_one(tag, t0=None):
    """复核单方案：行数一致 + 数检 + wpj。t0=None 时跳过 mtime 新鲜性检查。"""
    ydb = os.path.join(MODELS, tag + ".ydb")
    ymd = os.path.join(RUN, tag, tag + ".ymd")
    res = os.path.join(RUN, tag, "设计结果")
    prob = []

    # 1) 逐表行数
    if not os.path.exists(ymd):
        prob.append("缺 %s.ymd" % tag)
        a = {}
    else:
        a = _rows(ydb)
        b = _rows(ymd)
        diff = ["%s %s->%s" % (t.replace("tbl", ""), a[t], b[t])
                for t in TABLES if a.get(t) != b.get(t)]
        if diff:
            prob.append("行数不符: " + ", ".join(diff))

    # 2) 数检
    chk = os.path.join(res, "check.out")
    if not os.path.exists(chk):
        prob.append("缺 check.out")
    elif "未发现问题" not in _decode_check(chk):
        prob.append("数检未通过")

    # 3) 配筋文件
    wpj = sorted(f for f in (os.listdir(res) if os.path.isdir(res) else [])
                 if f.startswith("wpj") and f.endswith(".out"))
    if not wpj:
        prob.append("无 wpj*.out")
    elif t0 is not None:
        stale = [f for f in wpj
                 if os.path.getmtime(os.path.join(res, f)) <= t0]
        if stale:
            prob.append("wpj 陈旧: " + ",".join(stale))

    info = "梁/柱段 %s/%s 板 %s wpj %d 个" % (
        a.get("tblBeamSeg"), a.get("tblColSeg"), a.get("tblSlab"), len(wpj))
    return (not prob), info, prob


# host 的退出码语义（与 `yjk_auto.py:122-128` 的契约一一对应）：
#   2 = 本轮**确认为失败**（_HOST_ERRORS 非空）；
#   3 = **预检拒绝**（一个动作都没做）；
#   5 = **无法判定**（证据不足 → 结果不可信、需人工看。当前只有一种情形：
#       模态框看门狗没起来，于是"没有错误弹框"这句话无法成立）；
#   6 = 授权/许可问题。
# ★ 非零一律不算成功（下面 `rc != 0 → ok=False` 的判据**不放松**）；这张表只回答
#   "为什么非零"，免得 5 与 2/3/6 在屏幕上长得一样 —— 5 的产物其实还能看，
#   但"本轮没有真错误"这类结论不成立，处置是与 2 不同的。
HOST_RC_MEANING = {
    2: "确认为失败",
    3: "预检拒绝（未做任何动作）",
    5: "无法判定：证据不足，结果不可信，需人工看",
    6: "授权/许可问题",
}

# 本轮各方案的 host 退出码（run_one 记、main 统计）。
# ★ 用模块级列表而不是改 `run_one` 的返回签名：别处可能按 `ok, why = run_one(t)`
#   解包，加一个返回值会把那种调用方直接拆包失败。
_RC_LOG = []


def host_rc_why(rc):
    """host 退出码 → 一句人话（未知码只报数字，不猜）。"""
    try:
        m = HOST_RC_MEANING.get(int(rc))
    except (TypeError, ValueError):
        m = None
    return "host rc=%s：%s" % (rc, m) if m else "host rc=%s" % rc


def run_one(tag):
    ydb = os.path.join(MODELS, tag + ".ydb")
    wd = os.path.join(RUN, tag)
    if not os.path.exists(ydb):
        return False, "缺 %s" % ydb
    os.makedirs(wd, exist_ok=True)
    log = os.path.join(ROOT, "refs", "host_%s.log" % tag)
    t0 = time.time()
    with open(log, "w", encoding="utf-8") as fh:
        rc = subprocess.call(
            [PY, "-u", SKILL, "host", "--dir", wd, "--name", tag,
             "--import", ydb, "--prep", "--calc"],
            stdout=fh, stderr=subprocess.STDOUT)
    dt = time.time() - t0
    _RC_LOG.append((tag, rc))
    ok, info, prob = verify_one(tag, t0=t0)
    if rc != 0:
        prob.insert(0, host_rc_why(rc))          # 带上"为什么非零"，rc 本身仍在里面
        ok = False
    why = "%s | %s | 用时%.0fs" % (info, "全部通过" if ok else "; ".join(prob), dt)
    return ok, why


def main(argv=None):
    """命令行入口 —— ★ 参数必须先于任何 YJK 动作被解析（这是一条安全修复）。

    改前的写法（实测事故）：
        args = [a for a in sys.argv[1:]]
        only_verify = "--verify" in args
        tags = [a for a in args if not a.startswith("-")] or ORDER
    `--help` 以 `-` 开头 → 被那行过滤掉 → `tags` 空 → **回落成 ORDER**
    → 敲 `--help`（或任何拼错的选项，如 `--verfiy`）的后果是：
    直接实跑 S0..S4 四个方案的完整 YJK 流程，**并且覆盖工程目录**。
    对"只想看帮助"的人来说，这条命令是破坏性的。

    现在：
      * `--help` 由 argparse 正常处理，打印帮助并退出 0；
      * **任何未知的 `-` 开头参数一律报错退出 2**，不再被静默吞掉；
      * `tags` 只来自真正给出的位置参数，**默认不再回落成全量 ORDER**；
        要跑全部必须显式 `--all`（只读的 `--verify` 无参时才默认全部，安全）；
      * 方案标签必须是本技能已知的（拼错就报错，而不是去跑一个不存在的模型）。
    """
    ap = argparse.ArgumentParser(
        prog="run_all_yjk.py",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="把 5 个方案依次送进 YJK 实算，或只复核既有结果。",
        epilog=__doc__)
    ap.add_argument("tags", nargs="*", metavar="方案",
                    help="要处理的方案标签，可给多个（如 S0 S1）；默认不处理任何方案")
    ap.add_argument("--all", action="store_true",
                    help="实跑全部 %d 个方案：%s" % (len(ORDER), " ".join(ORDER)))
    ap.add_argument("--verify", action="store_true",
                    help="不复算，只复核既有结果（只读，不启动任何 YJK 进程）")
    a = ap.parse_args(argv)

    only_verify = a.verify
    tags = list(a.tags)
    if a.all:
        if tags:
            ap.error("--all 与方案标签不能同时给（--all 就是全部：%s）" % " ".join(ORDER))
        tags = list(ORDER)
    elif not tags and only_verify:
        tags = list(ORDER)              # 只读复核：无参默认复核全部，不会跑 YJK
    if not tags:
        ap.error("没给要处理的方案。请给方案标签（如 %s），"
                 "或用 --all 实跑全部；只想复核既有结果用 --verify。"
                 % " ".join(ORDER))
    unknown = [t for t in tags if t not in ORDER]
    if unknown:
        ap.error("不认识的方案标签：%s（本技能只有：%s）"
                 % (", ".join(unknown), " ".join(ORDER)))

    del _RC_LOG[:]                       # 每次运行自己统计，不留上一次的
    bad = 0
    for t in tags:
        print("=" * 64)
        if only_verify:
            ok, info, prob = verify_one(t)
            print("%s %s  %s | 复核（未复算）" % ("OK  " if ok else "FAIL", t, info))
            if prob:
                print("     问题：" + "; ".join(prob))
        else:
            print(">>> %s 开始 %s" % (t, time.strftime("%H:%M:%S")))
            sys.stdout.flush()
            ok, why = run_one(t)
            print("%s %s  %s" % ("OK  " if ok else "FAIL", t, why))
        sys.stdout.flush()
        if not ok:
            bad += 1
    print("=" * 64)
    print("完成：%d/%d 成功" % (len(tags) - bad, len(tags)))
    # ★ 把"确认为失败"与"无法判定"分开报：两者都非零、都**不算成功**（bad 与 return 1
    #   的判据不变），但处置不同 —— 5 的产物还能看，只是"本轮没有真错误"这类结论不成立。
    #   只在真有非零码时多打这一行：全是 0 的时候输出与以前逐字相同。
    failed = sum(1 for _tag, rc in _RC_LOG if rc not in (0, 5))
    unverified = sum(1 for _tag, rc in _RC_LOG if rc == 5)
    if failed or unverified:
        print("      失败 %d 轮 / 无法判定 %d 轮%s"
              % (failed, unverified,
                 "（无法判定 = host rc=5：证据不足，结果不可信，需人工看）"
                 if unverified else ""))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
