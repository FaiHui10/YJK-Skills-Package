# -*- coding: utf-8 -*-
r"""YJK：算完 → 自动生成施工图 → 自动统计工程量（构件算量）。

承接 `yjk-auto-drive`：本脚本在一个**托管进程内**把整条链跑完
（yjks 必须由存活进程托管 —— 硬性约束 2）。

链路
----
  清场 → YjkLauncher → yjks.exe(无参) → UINew → yjk_importydb → yjk_save
  → ★ 导入校验（几何表逐表核对，空模型立刻中止）
  → PREP_CHAIN（修复/成节点/成楼板）
  → CALC_CHAIN（层刚度/传荷/整体计算）→ 设计结果/
  → 【混凝土工程量】yjkconcreteStat_statCom（★ 必须切「楼层组装」IDModule_Layer）
  → 【施工图】板 / 梁 / 柱 / 墙  逐模块「绘新图」
  → 【钢筋工程量】工程量统计模块：板/梁/柱/墙
  → 留档 + 写清单

★ 顺序约束
  1. 「建模模块」(IDModule_Layer) 会**冲掉施工图上下文** ——
     `yjkconcreteStat_statCom` 之后所有 `DtlRC_*` 钢筋统计命令会退化成
     `OK(0.0s)` 且**不产出任何文件**。所以顺序必须是：
     **混凝土统计 → 施工图 → 钢筋统计**。
  2. `yjk_importydb` 必须收到**绝对路径**。传相对路径时 YJK 按自己的 CWD 解析 →
     弹「文件不存在」→ 若被放行则**导入空模型**，命令照样返回 OK，
     直到计算才报「模型中没有单元数据」。
  3. 板钢筋出量的关键一步是 `stdslab_AutoStatstl`，缺它就全 0。
  4. `StdSlab_batgenstl` 会弹模态框，靠 `dlgwatch.DialogWatch` 后台回「否」。
     看门狗在**启动 yjks 之前**就拉起，但那时还不知道自有实例的 pid，所以它
     只登记不动手（`pid=None`）；拿到 pid 后立刻 `narrow(pid)` 收窄到自有实例，
     此后才应答。**不要**让它对全机实例动手 —— 同机别人正在用的 YJK 弹任何
     确认框都会被按「是」答掉（审计 S55）。

用法
----
    python draw_quant.py --ydb models\S0.ydb --proj S0
    python draw_quant.py --ydb models\S0.ydb --proj S0 --out results\S0
    python draw_quant.py --ydb models\S0.ydb --proj S0 --no-conc   # 跳过混凝土统计

默认把工作目录放在**当前工作目录**下（`<cwd>\YJK_run_dq\<proj>`），
留档放在 `<cwd>\results\<proj>`；用 `--root` / `--workdir` / `--out` 可改。

接着出汇总 Excel：
    python summary_xlsx.py <留档目录> --name <工程名>
"""
import argparse
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

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


def find_driver():
    """找 yjk-auto-drive/scripts（含 yjk_auto.py 的那个目录）。

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


SK = find_driver()
if not SK:
    sys.stderr.write(
        "找不到 yjk-auto-drive 的驱动脚本（yjk_auto.py）。\n"
        "请把 yjk-auto-drive 目录放在与本技能同级的 skills 目录下，或设置环境变量\n"
        "YJK_DRIVER_DIR 指向该技能的 scripts 目录，或设置 YJK_SKILLS_DIR 指向整套技能的\n"
        "安装根目录。（把整套技能放进任意 agent 的用户级技能目录也能被自动找到。）\n")
    sys.exit(2)
sys.path.insert(0, SK)
import yjk_auto as Y                                              # noqa: E402
import impcheck as IC                                              # noqa: E402


# 看门狗用**本技能目录里这一份** dlgwatch，不用 `import dlgwatch`。
#
# 为什么：上面把驱动技能目录 `SK` 插到了 sys.path 最前面，`import dlgwatch`
# 命中的是驱动技能里的同名副本；那份在 pid=None 时盯**全机**所有 yjks.exe，并对
# 未命中规则的框一律回默认答复 —— 同一台机器上别人正在用的 YJK 只要弹出保存 /
# 覆盖 / 重生成一类的框，就会被它按「是」答掉（审计 S55）。本目录这一份在 pid
# 未知时只登记不动手。两份文件必须逐字节相同（compat_check.py 守着），但这里要
# 用的是"能限定到自有实例"的那一份，所以按文件路径显式加载。
_DLGWATCH_MOD = None


def _local_dlgwatch():
    """按文件路径加载本目录的 dlgwatch.py（绕开 sys.path 上的同名副本）。"""
    global _DLGWATCH_MOD
    if _DLGWATCH_MOD is None:
        import importlib.util
        p = os.path.join(HERE, "dlgwatch.py")
        spec = importlib.util.spec_from_file_location("dq_dlgwatch", p)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        _DLGWATCH_MOD = m
    return _DLGWATCH_MOD


# 这里原本有一句猴补丁 `Y.own_clear = lambda *a, **k: None`（注释说"躲避
# safe-delete 拦截"）。已经去掉：它把 kill_own() 成功后的登记清理、以及
# own_pid() 里"过期登记自动清理"一起禁掉了，失效的 own.json 会永久留在盘上 ——
# 那是"PID 被系统回收给新起的 yjks.exe，被当成自有实例，于是误杀别人实例"的
# 触发器（审计 S27/S28）。而 own_clear() 自己已经吞掉 OSError，不需要替它兜底。

# ---------------------------------------------------------------- 命令链
# (标签, 命令, 参数, 超时, 说明)；标签为 None 表示沿用上一条
CONC_CHAIN = [
    ("IDModule_Layer", "yjkconcreteStat_statCom", "", 300,
     "混凝土工程量 → 计算书/工程量统计/工程量统计.ini"),
]

SLAB_CHAIN = [
    ("IDDTL_DETAIL_SLAB", "StdSlab_RedrawNceng", "", 600, "板-绘新图"),
    (None, "StdSlab_AUTOCAL", "", 600, "板-计算"),
    (None, "StdSlab_batgenstl", "", 900, "板-批量出图（含全部楼层选筋，会弹模态框）"),
    (None, "stdslab_AutoStatstl", "", 600, "★板-全楼钢筋统计（缺此步出量为 0）"),
]

BEAM_CHAIN = [
    ("IDDTL_DETAIL_BEAM", "DtlRC_RegenReinsUpdateBeamPlan", "", 900,
     "梁-绘新图（重选钢筋并更新图面）"),
]

COL_CHAIN = [
    ("IDDTL_DETAIL_COLUMN", "DtlRC_DrawNewColPlan", "", 900, "柱-绘新图"),
]

WALL_CHAIN = [
    ("IDDTL_DETAIL_WALL", "DtlRC_WallPlanRegenNew", "", 900,
     "墙-重新归并选筋并绘新图"),
]

# ★ 钢筋算量：必须在施工图之后、且中途不能切回建模模块
REBAR_CHAIN = [
    ("IDQUANTITYLIST_DETAIL", "DtlRC_SSSE", "", 300, "板-全楼钢筋用量 Excel"),
    (None, "DtlRC_StatBuildingBeamSteelSpecExcel", "", 300,
     "梁-全楼钢筋用量 Excel（规格与类别）"),
    (None, "DtlRC_SSCE", "", 300, "柱-全楼钢筋用量 Excel"),
    (None, "DtlRC_SSWE", "", 300, "墙-全楼钢筋用量 Excel"),
    (None, "dtlrc_ColSumGJ", "", 300, "柱-全楼钢筋用量 txt（补充）"),
]

# 施工图（板/梁/柱/墙）
DRAW_CHAIN = SLAB_CHAIN + BEAM_CHAIN + COL_CHAIN + WALL_CHAIN

# 留档清单（相对工程目录）；含通配
KEEP_PAT = [
    "计算书/工程量统计/工程量统计.ini",
    "全楼楼板钢筋用量.dat",
    "SlabStlQuantity1.dat",
    "施工图/全楼楼板钢筋用量.xlsx",
    "施工图/全楼梁钢筋用量(钢筋规格与类别).xlsx",
    "施工图/全楼柱钢筋用量(钢筋规格与类别).xlsx",
    "施工图/全楼墙钢筋用量(钢筋规格与类别).xlsx",
    "施工图/柱钢筋统计.txt",
    "施工图/墙钢筋统计.txt",
]
# 留档这些目录下的全部文件
KEEP_DIRS = ["施工图"]

NOISE = ("DSevData_", "YJKDisplayData.ydb", "dsnctrl.ini", "shared_memory",
         "CustomSteelReinforcement.CSV", "CustomSteelReinforceMentLibrary.ydb",
         "SteelDim_GB.CSV", ".yjk", "工程名称_", ".yg", ".ygt", ".yjb",
         "SPara.par", ".rel", "backup/")


def log(msg, path=None):
    line = "%s %s" % (time.strftime("%H:%M:%S"), msg)
    print(line)
    sys.stdout.flush()
    if path:
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(line + "\n")


def real_new(before, after):
    out = []
    for k in Y.diff(before, after):
        b = os.path.basename(k)
        if any(n in k or n in b for n in NOISE):
            continue
        out.append(k)
    return sorted(out)


def run_chain(cli, wd, chain, lg, title):
    """执行一段链，逐步打印产出。返回 (统计 list, 问题 list)。

    问题清单里放的是"这一步没有跑完"的证据：切标签失败、命令返回值不是 OK。
    旧版把 `SetCurrentLabel` 的返回值直接丢掉，于是"整段钢筋统计退化成
    OK(0.0s) 且零产出"与"真的算完了"在返回值上完全一样（审计 S14）。
    """
    log("-" * 70, lg)
    log("【%s】%d 条命令" % (title, len(chain)), lg)
    stat, problems = [], []
    for label, cmd, param, to, desc in chain:
        if label:
            lr = str(cli.run("SetCurrentLabel", label, 120))
            stat.append({"命令": "SetCurrentLabel", "说明": "切到 %s" % label,
                         "返回": lr, "产物": []})
            if not lr.startswith("OK"):
                problems.append("[%s] 切标签 %s 失败：%s" % (title, label, lr))
                log("  !! 切标签 %s -> %s（该阶段可能秒回 OK 而零产出）"
                    % (label, lr), lg)
        before = Y.snap(wd)
        t0 = time.time()
        try:
            r = cli.run(cmd, param, to)
        except Exception as e:                                     # noqa: BLE001
            r = "EXC %r" % e
        new = real_new(before, Y.snap(wd))
        log("  %-40s %-30s -> %-14s [%4.1fs] %s"
            % (cmd, desc, r, time.time() - t0,
               ("产出 %d 项: %s" % (len(new), ", ".join(
                   os.path.basename(x) for x in new[:4]))) if new else "无产出"))
        for x in new:
            log("       + %s" % x, lg)
        stat.append({"命令": cmd, "说明": desc, "返回": str(r),
                     "产物": [os.path.basename(x) for x in new]})
        if not str(r).startswith("OK"):
            problems.append("[%s] %s 返回 %s（这一步没有正常跑完）" % (title, cmd, r))
    return stat, problems


def collect(wd, out):
    """把产出留档到 out/，并返回清单。"""
    os.makedirs(out, exist_ok=True)
    lst = []
    for rel in KEEP_PAT:
        src = os.path.join(wd, rel.replace("/", os.sep))
        if os.path.exists(src):
            dst = os.path.join(out, os.path.basename(rel))
            shutil.copy2(src, dst)
            lst.append((os.path.basename(rel), os.path.getsize(dst)))
    for d in KEEP_DIRS:
        sd = os.path.join(wd, d)
        if not os.path.isdir(sd):
            continue
        od = os.path.join(out, d)
        os.makedirs(od, exist_ok=True)
        for f in sorted(os.listdir(sd)):
            p = os.path.join(sd, f)
            if os.path.isfile(p):
                shutil.copy2(p, os.path.join(od, f))
                lst.append((d + "/" + f, os.path.getsize(p)))
    return lst


def judge_products(keep, watch, ini_path, want_conc=True, want_draw=True,
                   want_rebar=True):
    """判定本轮产量与弹框是否达标，返回 (未达标项 list, dwg list, xlsx list)。

    为什么必须判：旧版把"施工图 DWG：0 个 / 钢筋用量 Excel：—— 无 / 其中错误 1 条"
    只写进日志，然后无条件 return 0，调用方无从区分"图画出来了"与"一条都没出来"。
    同一个文件对"设计结果/"是有硬闸门的（一个文件都没有就直接 return 1），
    所以这不是"设计如此"，是漏了（审计 S14）。

    判据只认产物的**数量**与弹框，不看 RunCmd 的返回值 —— 本包反复实测：
    命令秒回 `OK(0.0s)` 而零产出，返回值一文不值。
    """
    problems = []
    dwg = sorted(f for f in (keep or []) if f.lower().endswith(".dwg"))
    xls = sorted(f for f in (keep or []) if f.lower().endswith(".xlsx"))
    if want_draw and not dwg:
        problems.append("施工图阶段跑过了，但留档里一个 DWG 都没有")
    if want_rebar and not xls:
        problems.append("钢筋统计阶段跑过了，但一个钢筋用量 Excel 都没有")
    if want_conc and not os.path.exists(ini_path):
        problems.append("混凝土统计阶段跑过了，但工程目录里没有 工程量统计.ini")
    for _t, b in (getattr(watch, "errors", None) or []):
        problems.append("真错误弹框：%s" % str(b)[:90])
    for it in (getattr(watch, "failed", None) or []):
        b = it[1] if isinstance(it, (tuple, list)) and len(it) > 1 else it
        problems.append("对话框应答未送达（框可能还挂着）：%s" % str(b)[:90])
    for _t, b in (getattr(watch, "unanswered", None) or []):
        problems.append("对话框未自动应答（未命中规则，等人工处理）：%s" % str(b)[:90])
    return problems, dwg, xls


def _utf8_console():
    """让输出在任何控制台编码下都不崩（GBK 下把不可编码字符替换掉）。

    为什么需要：本脚本自己只打中文与 ASCII，但**它会调用 `impcheck.check()`**
    （`import impcheck as IC`），而那个模块的打印是在**本进程**的 stdout 上执行的 ——
    库自己 `__main__` 里的兜底保护不到调用方。默认 GBK 控制台下 `print` 遇到
    cp936 编不出的字符会抛 `UnicodeEncodeError` 并**以退出码 1 中断**，
    于是一个其实已经成功的任务会被上层按退出码判成失败。

    ★ 只在实际执行时调用（`main()` 第一行），**不在 import 时改 stdout** ——
      本模块会被别的脚本 import 当库用。
    ★★ `draw_quant.py` 在 `floor-system-comparison` 与 `yjk-draw-takeoff` 两个技能里
       各有一份**必须逐字节相同**的副本（`compat_check.py` 有专门的守护）。
       改这里就必须**同步另一份**，否则两个技能的行为会静默分叉。
    """
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass


def main():
    _utf8_console()          # ★ 必须在 argparse 之前：--help 也是写到 stdout 的
    ap = argparse.ArgumentParser()
    ap.add_argument("--ydb", required=True, help="源模型 .ydb（绝对或相对路径）")
    ap.add_argument("--proj", required=True, help="工程名（英文/数字，别用中文）")
    ap.add_argument("--root", default=None,
                    help="工作根目录，默认当前目录（工作目录/留档目录都放它下面）")
    ap.add_argument("--workdir", default=None, help="工作目录，默认 <root>\\YJK_run_dq\\<proj>")
    ap.add_argument("--out", default=None, help="留档目录，默认 <root>\\results\\<proj>")
    ap.add_argument("--no-conc", action="store_true", help="跳过混凝土工程统计")
    ap.add_argument("--no-draw", action="store_true", help="跳过施工图生成")
    ap.add_argument("--no-rebar", action="store_true", help="跳过钢筋工程统计")
    ap.add_argument("--timeout", type=int, default=1800)
    a = ap.parse_args()

    # ★ 工作根目录默认取当前目录 —— 技能要能拿到任何工程上直接用，
    #   不能把工作目录写在技能自己的安装路径里（那样会在技能目录里拉屎）。
    root = os.path.abspath(a.root or os.getcwd())
    ydb = IC.abs_ydb(a.ydb)                     # ★ 必须绝对路径
    wd = a.workdir or os.path.join(root, "YJK_run_dq", a.proj)
    out = a.out or os.path.join(root, "results", a.proj)
    os.makedirs(wd, exist_ok=True)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    lg = os.path.join(wd, "_draw_quant.log")
    if os.path.exists(lg):
        os.remove(lg)

    log("=" * 70, lg)
    log("YJK 施工图 + 工程量统计", lg)
    log("  模型   %s" % ydb, lg)
    log("  工程   %s" % a.proj, lg)
    log("  工作目录 %s" % wd, lg)
    log("  留档   %s" % out, lg)

    stat = {"模型": ydb, "工程": a.proj, "阶段": []}
    problems = []                      # 本轮未达标项；非空 -> 退出码 1（见收尾）
    watch = None
    try:
        try:
            if Y.own_pid():
                Y.kill_own()
                time.sleep(1)
        except Exception as e:                                     # noqa: BLE001
            log("  清场告警 %r（继续）" % e, lg)
        Y.ensure_launcher()

        # 看门狗在**启动之前**就位（启动过程本身也可能弹框），但那时还不知道自有
        # 实例的 pid，所以它处于"只登记不动手"状态：pid=None 时一个按钮都不点，
        # 只把看到的框记进日志。绝不能让它在这一段盯全机实例并应答别人的对话框。
        watch = _local_dlgwatch().DialogWatch(None, log=lambda m: log(m, lg))
        watch.start()
        log("启动 yjks.exe（无参）；等待 IPC 通道，最多 150s ...", lg)
        t0 = time.time()
        pid, ok = Y.boot_yjks(wd, verbose=False)
        if ok:
            log("  IPC 通道就绪（%.0fs，pid=%s）" % (time.time() - t0, pid), lg)
        else:
            log("!! 启动失败 / IPC 未就绪（%.0fs）" % (time.time() - t0), lg)
            log("   排查：两处 Config.ini 的 [YJKSControl] Flag=True？"
                "是否弹了没人应答的对话框（看下面「对话框」记录）？"
                "是否还有别的 yjks.exe 残留？", lg)
            return 1
        Y.own_claim(pid, Y.rt_yjk().get("exe") or "", wd)
        # 拿到自有 pid 后立刻收窄：此后看门狗只在自己的实例上动作，同机其它
        # YJK 实例的对话框一律不碰（审计 S55）。
        if watch is not None:
            watch.narrow(pid)
            log("看门狗已收窄到自有实例 pid=%s（不再触碰别人的对话框）" % pid, lg)
        cli = Y.Client()
        log("客户端就绪（%s）" % cli.kind, lg)

        proj_yjk = os.path.join(wd, a.proj + ".yjk")
        if not Y.open_new_project(cli, proj_yjk, wd):
            log("!! 建工程失败（工作目录里可能已有同名 .yjk，请换 --proj 或清目录）", lg)
            return 1

        log("导入 %s" % os.path.basename(ydb), lg)
        log("  yjk_importydb -> %s" % cli.run("yjk_importydb", ydb, 600), lg)
        log("  yjk_save -> %s" % cli.run("yjk_save", "", 300), lg)
        ymd = os.path.join(wd, a.proj + ".ymd")
        ok, rep = IC.check(ydb, ymd, verbose=False, strict=False)
        for ln in rep.splitlines():
            log("  " + ln, lg)
        if not ok:
            log("!! 导入校验不通过 —— 中止（源模型为空，或导入路径/状态异常）", lg)
            return 1

        log("预处理", lg)
        for c, p in Y.PREP_CHAIN:
            log("  %-24s -> %s" % (c, cli.run(c, p, 600)), lg)
        log("计算", lg)
        for c, p in Y.CALC_CHAIN:
            t0 = time.time()
            log("  %-28s -> %s  [%.0fs]"
                % (c, cli.run(c, p, a.timeout), time.time() - t0), lg)
        res = os.path.join(wd, "设计结果")
        n = len(os.listdir(res)) if os.path.isdir(res) else 0
        log("  设计结果/ %d 个文件" % n, lg)
        if n == 0:
            log("!! 没有设计结果 —— 计算失败，中止。请看 设计结果/check.out 与 fea.dat-ERR.txt", lg)
            return 1

        if not a.no_conc:
            st, pr = run_chain(cli, wd, CONC_CHAIN, lg, "混凝土工程量")
            stat["阶段"] += st
            problems += pr
        if not a.no_draw:
            st, pr = run_chain(cli, wd, DRAW_CHAIN, lg, "施工图生成")
            stat["阶段"] += st
            problems += pr
        if not a.no_rebar:
            st, pr = run_chain(cli, wd, REBAR_CHAIN, lg, "钢筋工程量统计")
            stat["阶段"] += st
            problems += pr

        log("留档", lg)
        lst = collect(wd, out)
        for k, sz in lst:
            log("  %-58s %9d B" % (k, sz), lg)
        stat["留档"] = [k for k, _ in lst]

        # ---- 汇总报告 ----
        log("=" * 70, lg)
        log("汇总", lg)
        ini = os.path.join(wd, "计算书", "工程量统计", "工程量统计.ini")
        if os.path.exists(ini):
            import gcl_ini
            d = gcl_ini.parse(ini)
            txt = gcl_ini.dump_text(d)
            for ln in txt.splitlines():
                log("   " + ln, lg)
            with open(os.path.join(out, "混凝土工程量汇总.txt"), "w",
                      encoding="utf-8") as fh:
                fh.write(txt + "\n")
            with open(os.path.join(out, "混凝土工程量汇总.json"), "w",
                      encoding="utf-8") as fh:
                json.dump({"info": d["info"], "汇总": gcl_ini.summarize(d)},
                          fh, ensure_ascii=False, indent=2)
            stat["混凝土"] = gcl_ini.summarize(d)["按构件种类"]
            log("   -> 混凝土工程量汇总.txt / .json", lg)
        else:
            log("   ！没有 工程量统计.ini（混凝土统计未生效，用 --no-conc 跳过时会如此）", lg)
        # 产量与弹框的判定（旧版只打印，无条件 return 0 —— 审计 S14）
        prd, dwg, xls = judge_products(stat["留档"], watch, ini,
                                       want_conc=not a.no_conc,
                                       want_draw=not a.no_draw,
                                       want_rebar=not a.no_rebar)
        problems += prd
        log("施工图 DWG：%d 个" % len(dwg), lg)
        log("钢筋用量 Excel：%s" % (", ".join(xls) if xls else "—— 无（钢筋统计可能未生效）"), lg)
        if watch:
            log("模态框留档 %d 条，其中错误 %d 条" % (len(watch.seen), len(watch.errors)), lg)
            for t, b in watch.errors:
                log("   [错误框] %s" % b[:90], lg)
            if getattr(watch, "noted", None):
                log("   另有 %d 个框在 pid 未收窄阶段只登记未动作（见上面 [只登记] 行）"
                    % len(watch.noted), lg)

        stat["问题"] = problems
        with open(os.path.join(out, "run_manifest.json"), "w", encoding="utf-8") as fh:
            json.dump(stat, fh, ensure_ascii=False, indent=2)
        log("清单 -> %s" % os.path.join(out, "run_manifest.json"), lg)
        if problems:
            log("!! 本轮有 %d 项未达标，退出码 1：" % len(problems), lg)
            for x in problems:
                log("   - %s" % x, lg)
            return 1
        return 0
    finally:
        if watch:
            watch.stop()
        time.sleep(0.5)
        try:
            if Y.own_pid():
                Y.kill_own()
        except Exception as e:                                     # noqa: BLE001
            log("清场异常 %r" % e, lg)


if __name__ == "__main__":
    sys.exit(main())
