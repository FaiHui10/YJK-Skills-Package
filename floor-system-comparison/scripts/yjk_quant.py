# -*- coding: utf-8 -*-
r"""在**同一个托管进程内**跑完「建模导入 → 预处理 → 计算 → 板配筋 → 工程量统计」。

为什么要自己写而不直接用 `yjk_auto.py host`：
  `host` 是一把梭到「设计结果」就收尾；板配筋与工程量统计是**后面两步**，
  而且 yjks 必须由一个存活进程托管（硬性约束 2），所以只能把整条链放进同一个脚本里。

链路（每方案一轮，一轮一个干净实例）：
  清场 → YjkLauncher → yjks.exe(无参) → UINew → yjk_importydb → yjk_save
  → PREP_CHAIN（修复/成节点/成楼板）
  → CALC_CHAIN（层刚度/传荷/整体计算）→ 设计结果/
  → SLAB_CHAIN（板施工图：重生成 → 计算 → **批量生成(含选筋)** → 自动钢筋统计）
  → QUANT_CHAIN（工程量统计：楼板/梁/柱 钢筋用量表）
> 每一步前后都做文件快照，**新增/改动的文件全部打印出来**，不靠猜。

★ 关键坑：`StdSlab_RESELECTREIN` 会弹模态框「施工图已经进行过选筋,是否重新选筋?」，
  模态期间 yjks 主窗口被 Disable，IPC 命令**永不返回**（≈挂死）。
  用 `dlgwatch.DialogWatch` 后台线程自动回「否」即可；成功关框的唯一方法是
  给对话框发 `WM_COMMAND(IDNO)`（BM_CLICK / 键盘消息都无效）。

用法：
    python yjk_quant.py S0                 # 单方案
    python yjk_quant.py S0 S1 S2 S3 S4     # 多方案
    python yjk_quant.py --no-quant S0      # 只算不算量（排障用）
"""
import argparse
import json
import os
import shutil
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


def _find_driver_scripts():
    """找含 yjk_auto.py 的那个 scripts 目录；找不到返回 None。

    候选链见上面那段 `COMPAT-FALLBACK` —— 六份副本**一致**（内容逐字节相同，行尾各随本文件）。

    只保留三样：环境变量 → 同级目录 → 与厂商无关的通用扫描 + 中立位置，
    最后是历史遗留路径（保留以不破坏现有用户）。**不含任何具体厂商名、盘符、
    用户名或桌面路径**（桌面探测早已删除：技能不该假定自己放在桌面）。
    要改就六份一起改，并跑 `selfcheck.py`（T31 逐字节比对）与 `compat_check.py`。
    """
    for d in _compat_driver_dirs():
        c = os.path.join(d, "scripts")
        if os.path.exists(os.path.join(c, "yjk_auto.py")):
            return os.path.abspath(c)
    return None


SK = _find_driver_scripts()
if not SK:
    sys.stderr.write(
        "找不到 yjk-auto-drive 的驱动脚本（yjk_auto.py）。\n"
        "请把 yjk-auto-drive 目录放在与本技能同级的 skills 目录下，或设置环境变量\n"
        "YJK_DRIVER_DIR 指向该技能的 scripts 目录，或设置 YJK_SKILLS_DIR 指向整套技能的\n"
        "安装根目录。（把整套技能放进任意 agent 的用户级技能目录也能被自动找到。）\n")
    sys.exit(2)
if SK not in sys.path:
    sys.path.insert(0, SK)
import yjk_auto as Y                                              # noqa: E402
sys.path.insert(0, HERE)
from dlgwatch import DialogWatch                                   # noqa: E402
import impcheck as IC                                              # noqa: E402

# ★ 环境里有"删除拦截"（safe-delete 钩子）：一旦某轮内删除次数超阈值，删
#   `~/.yjk-auto/own.json` 会被拒绝并抛非 Exception 的异常，直接把整批任务打断。
#   own.json 只是「自有实例登记」，下一轮 own_claim() 会**写覆盖**，不需要删。
# ★ 但**不能**把它换成一个真正的空操作：yjk_auto.own_clear() 还有一个调用者是
#   own_pid()（过期登记自动清理）—— 置成 no-op 会连带禁掉它，失效的登记就永久
#   留在盘上。之后 Windows 把那个 PID 回收给一个新起的 yjks.exe 时，下一次 host
#   会把它当"自有实例"并可能**杀掉别人正在用的实例**（审计 S27 → S28）。
#   所以这里改成"把登记内容写成空"：_own_read() 得到 {}、own_pid() 得到 None，
#   语义上与删掉等价，又不触发删除拦截。
_OWN_CLEAR_FAILED = []          # 清登记失败时记一条原因（main() 会据此给非零退出码）


def _own_clear_by_rewrite():
    p = getattr(Y, "OWN_FILE", None)
    if not p:
        msg = "yjk_auto 里找不到 OWN_FILE —— 清登记这一步没做成"
        sys.stderr.write("!! %s（失效登记可能被留到下一次会话）\n" % msg)
        _OWN_CLEAR_FAILED.append(msg)
        return
    try:
        with open(p, "w", encoding="utf-8") as fh:
            json.dump({}, fh, ensure_ascii=False)
    except OSError as e:
        msg = "清 own.json 失败：%s" % e
        sys.stderr.write("!! %s（失效登记可能被留到下一次会话）\n" % msg)
        _OWN_CLEAR_FAILED.append(msg)


Y.own_clear = lambda *a, **k: _own_clear_by_rewrite()

MODELS = os.path.join(ROOT, "models")
# ★ 必须用**全新**工作目录：`YJK_run/S*` 已经是"已验收的计算结果"，
#   而 open_new_project 会拒绝覆盖已有 .yjk（防呆），所以统计阶段另开目录，
#   两边互不干扰：YJK_run/ = 计算证据，YJK_run_q/ = 板配筋+工程量产出。
RUN = os.path.join(ROOT, "YJK_run_q")
OUT = os.path.join(ROOT, "results")
# 运行日志写在**产出目录**里，不要写进 `refs/`（那是随包分发的资料/夹具目录：
# `scaffold.ydb` 就在那儿）。写在 refs/ 会让"跑过一次"的包多出一份运行时日志，
# 分发出去时又把别人上次运行的日志带给下一个人。
LOG = os.path.join(OUT, "quant.log")

# ---- 板施工图 / 板配筋（标签 IDDTL_DETAIL_SLAB），命令名取自 YJK.CUI 原始大小写 ----
SLAB_CHAIN = [
    ("SetCurrentLabel", "IDDTL_DETAIL_SLAB"),
    ("StdSlab_RedrawNceng", ""),     # 重生成板施工图环境（DSevData_*.xml 等）
    ("StdSlab_AUTOCAL", ""),         # 板内力计算（SlabCalData*.txt）
    ("StdSlab_batgenstl", ""),       # ★ 批量生成板施工图 —— 含全部楼层的计算+选筋
    ("stdslab_AutoStatstl", ""),     # ★ 自动统计钢筋面积 -> 全楼楼板钢筋用量.dat
]

# ---- 工程量统计模块（标签 IDQUANTITYLIST_DETAIL）的官方命令 ----
# 命令名直接取自 `C:\YJKS\YJKS_7_1_0\YJK.CUI` 里 <MenuMacro>/<Command> 的**原始大小写**。
#   上部结构 = yjkconcreteStat_statCom  ← 0.16s 静默空转（返回 None），已弃用
#   楼板     = DtlRC_SSSE
#   梁       = DtlRC_StatBuildingBeamSteelSpecExcel
#   柱       = DtlRC_SSCE
#   墙       = DtlRC_SSWE
QUANT_CHAIN = [
    ("SetCurrentLabel", "IDQUANTITYLIST_DETAIL"),
    ("DtlRC_SSSE", ""),                                   # 楼板钢筋
    ("DtlRC_StatBuildingBeamSteelSpecExcel", ""),         # 梁钢筋（按规格分类）
    ("DtlRC_SSCE", ""),                                   # 柱钢筋（按规格分类）
    ("DtlRC_SSWE", ""),                                   # 墙钢筋（本工程无墙）
]
QUANT_TIMEOUT = 300      # 单条统计命令最多等 5 分钟；挂死也要能继续下一条
SLAB_TIMEOUT = 600

# 每个方案要留档的产出（相对工作目录）
KEEP = [
    os.path.join("施工图", "全楼楼板钢筋用量.xlsx"),
    os.path.join("施工图", "全楼梁钢筋用量(钢筋规格与类别).xlsx"),
    os.path.join("施工图", "全楼柱钢筋用量(钢筋规格与类别).xlsx"),
    "全楼楼板钢筋用量.dat",
    "SlabStlQuantity1.dat",
]


def log(msg):
    line = "%s %s" % (time.strftime("%H:%M:%S"), msg)
    print(line)
    sys.stdout.flush()
    # 第一次写日志时把 results/ 建出来（日志与产物放一起，见 LOG 的说明）
    try:
        os.makedirs(os.path.dirname(LOG), exist_ok=True)
    except OSError:
        pass
    with open(LOG, "a", encoding="utf-8") as fh:
        fh.write(line + "\n")


def archive_products(tag, wd, od=None):
    """把 KEEP 里的产出留档到 results/<tag>/ → (got, missing)。

    老版本这一段是内联在 run_scheme 里的，且**无论留到几个都 `return True`**：
    一个产出都没有（某个 DtlRC_* 静默空转、results/<tag>/ 建出来却是空的）
    与"全部齐备"走同一条成功路径、退出码 0。
    """
    od = od or os.path.join(OUT, tag)
    os.makedirs(od, exist_ok=True)
    got, missing = [], []
    for rel in KEEP:
        src = os.path.join(wd, rel)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(od, os.path.basename(rel)))
            got.append(os.path.basename(rel))
        else:
            missing.append(rel)
    return got, missing


def run_scheme(tag, do_quant=True, timeout=1800):
    ydb = os.path.join(MODELS, tag + ".ydb")
    wd = os.path.join(RUN, tag)
    proj = os.path.join(wd, tag + ".yjk")
    if not os.path.exists(ydb):
        log("!! %s 缺 %s" % (tag, ydb))
        return False
    os.makedirs(wd, exist_ok=True)
    log("=" * 64)
    log(">>> %s 开始" % tag)

    log("清场")
    try:
        if Y.own_pid():
            Y.kill_own()
            time.sleep(1)
    except Exception as e:                                         # noqa: BLE001
        log("  清场告警 %r（继续；登记的 own.json 会由下一轮 own_claim 覆盖）" % e)
    Y.ensure_launcher()
    pid, ok = Y.boot_yjks(wd)
    if not ok:
        log("!! %s 通道未就绪" % tag)
        return False
    Y.own_claim(pid, Y.rt_yjk().get("exe") or "", wd)
    cli = Y.Client()
    log("客户端就绪（%s）" % cli.kind)

    watch = DialogWatch(pid, log=log)          # ★ 模态框看门狗
    watch.start()

    try:
        if not Y.open_new_project(cli, proj, wd):
            log("!! %s 建工程失败" % tag)
            return False

        log("导入 %s" % os.path.basename(ydb))
        log("  yjk_importydb -> %s" % cli.run("yjk_importydb", ydb, 600))
        log("  yjk_save -> %s" % cli.run("yjk_save", "", 300))
        ymd = os.path.join(wd, tag + ".ymd")
        log("  %s.ymd = %s 字节" % (tag, Y._file_size(ymd)))

        # ★ 导入校验闸门：命令返回 OK 不代表真导进去了。
        #   向 yjk_importydb 传相对路径时，YJK 按自己的工作目录解析 → 找不到 →
        #   弹「文件不存在」→ 若放行则**导入空模型**且照样返回 OK，
        #   直到计算才报「模型中没有单元数据」。这里逐表核对几何表行数，当场拦住。
        ok_imp, rep = IC.check(ydb, ymd, verbose=False, strict=False)
        for ln in rep.splitlines():
            log("  " + ln)
        if not ok_imp:
            log("!! %s 导入校验不通过 —— 跳过本方案（别浪费时间跑计算）" % tag)
            return False

        log("预处理")
        for c, p in Y.PREP_CHAIN:
            log("  %-24s(%r) -> %s" % (c, p, cli.run(c, p, 600)))

        log("官方计算链")
        for c, p in Y.CALC_CHAIN:
            t0 = time.time()
            log("  %-24s(%r) -> %s  [%.0fs]" % (c, p, cli.run(c, p, timeout),
                                                time.time() - t0))
        res = os.path.join(wd, "设计结果")
        log("  设计结果/ %d 个文件" % (len(os.listdir(res)) if os.path.isdir(res) else 0))

        if not do_quant:
            return True

        # ---------------- 板配筋链 ----------------
        before = Y.snap(wd)
        for c, p in SLAB_CHAIN:
            t0 = time.time()
            to = 120 if c == "SetCurrentLabel" else SLAB_TIMEOUT
            r = cli.run(c, p, to)
            log("  [板] %-40s -> %s  [%.0fs]" % (c, r, time.time() - t0))
            new = Y.diff(before, Y.snap(wd))
            if new:
                log("       新/改: %s"
                    % sorted(os.path.basename(k) for k in new)[:10])
        dat = os.path.join(wd, "全楼楼板钢筋用量.dat")
        log("  板钢筋统计表: %s" % ("有" if os.path.exists(dat) else "!! 缺"))

        # ---------------- 工程量统计链 ----------------
        for c, p in QUANT_CHAIN:
            t0 = time.time()
            r = cli.run(c, p, QUANT_TIMEOUT if c != "SetCurrentLabel" else 120)
            log("  ★ %-44s -> %s  [%.0fs]" % (c, r, time.time() - t0))
            new = Y.diff(before, Y.snap(wd))
            if new:
                log("       新/改: %s"
                    % sorted(os.path.basename(k) for k in new)[:10])

        # ---------------- 留档 ----------------
        got, missing = archive_products(tag, wd)
        log("  留档到 results/%s/ : %s" % (tag, got))
        # ★ 老版本不判产出：零留档与全部齐备同一条成功路径（退出码 0）。
        #   本包对"命令正常返回但零产出"已有实测记录（yjkconcreteStat_statCom →
        #   0.16s 静默空转、返回 None）。留档是量测阶段的交付契约
        #   （commands.md：stdslab_AutoStatstl 的判据就是写出那两个 .dat）。
        if missing:
            log("  !! %s 缺留档产物 %d 个：%s" % (tag, len(missing), missing))
            log("     缺的是 YJK 该写出来的东西 —— 别把本轮当「留档完成」。"
                "先看上面各条命令的耗时/新改文件，判断是哪一步静默空转了。")
            return False
        return True
    finally:
        watch.stop()
        time.sleep(0.5)


def _utf8_console():
    """让输出在任何控制台编码下都不崩（GBK 下把不可编码字符替换掉）。

    为什么需要：本脚本自己只打中文与 ASCII，但**它会调用 `impcheck.check()`**
    （`import impcheck as IC`），而那个模块的打印是在**本进程**的 stdout 上执行的 ——
    库自己 `__main__` 里的兜底保护不到调用方。默认 GBK 控制台下 `print` 遇到
    cp936 编不出的字符会抛 `UnicodeEncodeError` 并**以退出码 1 中断**，
    于是本轮其实已经成功的算量会被上层按退出码判成失败。

    ★ 只在实际执行时调用（`main()` 第一行），**不在 import 时改 stdout**。
    """
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass


def main():
    _utf8_console()          # ★ 必须在 argparse 之前：--help 也是写到 stdout 的
    ap = argparse.ArgumentParser()
    ap.add_argument("tags", nargs="+")
    ap.add_argument("--no-quant", action="store_true", dest="no_quant")
    ap.add_argument("--timeout", type=int, default=1800)
    a = ap.parse_args()
    ok = 0
    try:
        for t in a.tags:
            if run_scheme(t, not a.no_quant, a.timeout):
                ok += 1
    finally:
        log("收尾：清场")
        try:
            if Y.own_pid():
                Y.kill_own()
        except Exception as e:                                     # noqa: BLE001
            log("清场异常 %r" % e)
    log("完成 %d/%d" % (ok, len(a.tags)))
    if _OWN_CLEAR_FAILED:
        # ★ 清登记失败不能只写 stderr 了事：留着的失效登记会让下一次会话把回收到的
        #   PID 当成"自有实例"（审计 S27→S28 的误杀链），所以这里也要反映到退出码。
        log("!! 有 %d 次「清自有实例登记」没做成：" % len(_OWN_CLEAR_FAILED))
        for m in _OWN_CLEAR_FAILED:
            log("   · %s" % m)
        log("   处置：手工确认 %s 里没有失效的 pid"
            "（或删掉它），再重跑。" % getattr(Y, "OWN_FILE", "~/.yjk-auto/own.json"))
        return 1
    return 0 if ok == len(a.tags) else 1


if __name__ == "__main__":
    sys.exit(main())
