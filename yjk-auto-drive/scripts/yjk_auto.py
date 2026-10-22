# -*- coding: utf-8 -*-
r"""YJK 全自动驱动工具（官方 IPC 通道；跨机器自适应，无任何写死路径）。

已验证的完整链路（YJK 6.1+ / 7.x）
----------------------------------
  kill 全部 yjks → 确保 YjkLauncher 在跑 → yjks.exe 无参启动
  → 等 IPC 通道自动就绪（Config.ini [YJKSControl] Flag=True，无需键入 yjksipccontrol）
  → UINew <路径>.yjk 在指定路径新建工程  ← 关键：UINew 认路径，UIOpen 不认
  → yjk_importydb <模型>.ydb 导入待算模型
  → 官方计算链 → 读 设计结果\wpj*.out 复核

为什么需要常驻托管
------------------
  **yjks 不受宿主进程生命周期约束** —— host 退出后 yjks 仍存活，
  残留实例会在下一轮抢 Global\ 事件（硬性约束 3）。故本工具：
    * 每轮开工先 kill（清自己的残留，也清上一次的）；
    * 每轮收尾也 kill（本文件末尾，别指望"子进程自动回收"）；
    * 需要连续下命令时用 host 模式常驻 + 附「指令收件箱」，免得反复重启（每次 12s + 启动开销）：
      其他进程往 <workdir>\_yjk_inbox.txt 追加 "HHMMSS|命令|参数" 行，
      host 执行后把结果（含目录内文件变更清单）写到 <workdir>\_yjk_outbox.txt。

跨机器自适应（本文件不含任何盘符/用户名）
------------------------------------------
  * YJK 安装目录：环境变量 → 运行中进程 → 注册表/卸载信息 → 扫盘兜底（见 paths.py）
  * 官方客户端 DLL：命令参数 --dll → 环境变量 YJKAPI_DLL → 技能 assets/ → 用户缓存
                    → YJK 安装目录 STCAD/ → 用户目录检出 → 报错并给出取件指引
  * 客户端签名自适应：`YJKIPC.YJKSControl`(RunCmd 2参) 与安装目录 `YJKSControl`(3参含 out)
    都能用，自动挑重载。
  * 版本探测：目录名 / Config.ini，仅作提示用（不阻断）
  * 先 `python yjk_probe.py` 自检环境；缺什么它会明确告诉你

用法
----
  python yjk_auto.py probe                      # = yjk_probe.py，环境自检（建议先跑）
  python yjk_auto.py status                     # 实例分类（自有/你在用/无窗口残留）/窗口/IPC 通道
  python yjk_auto.py close --pid <PID> [--yes]  # 精确关闭某个实例（关"你在用的"必须 --yes）
  python yjk_auto.py kill                       # ⚠ 无差别杀掉全部 yjks（人工逃生口，自动化不得调用）
  python yjk_auto.py host --dir <工作目录> --name <工程名>
                          [--import x.ydb] [--prep] [--calc] [--stay N] [--inbox]
                          [--exit-when-idle N] [--wait-others N] [--clean-orphans] [--keep]
                          [--reuse]      # 允许复用目录里已存在的 <工程名>.yjk（默认拒绝）
  python yjk_auto.py send <命令> [参数] [--dir <工作目录>]
  python yjk_auto.py send @recalc [新模型.ydb] --dir <工作目录>    # 一整轮迭代（宏）
  python yjk_auto.py send @takeoff --dir <工作目录>               # 混凝土统计→施工图→钢筋统计

  导入后**必须**过一遍逐表校验（`impcheck.py`，见「导入校验闸门」一节）：
    半写的 .ydb / 相对路径导入都会让 `yjk_importydb` 返回成功而实际导入空模型，
    失败要到计算阶段才以 fea.dat-ERR.txt「模型中没有单元数据」+ 分析失败[-45] 现形。

  遇到"你在用的"实例时：先**提示关哪个、怎么关**（给出可粘贴的 close 命令），
     默认**拒绝开工且不碰它**；加 `--wait-others 600` 可让它等你关掉后自动继续。
  send 要求"会话已就绪"：host 走完启动→建工程→导入→预处理（约 60s）才会打开收件箱并写
     <工作目录>\_yjk_inbox.ready；未就绪时 send **拒绝写入**（否则会被启动时归档丢掉）。

收件箱宏（迭代闭环用；一轮 ≈5 分钟，不必重启 YJK）
--------------------------------------------------
  @back    回到「构件布置（建模调整界面）」——计算链末尾停在设计结果标签，
           而 yjk_importydb/yjk_repair 等属建模模块命令，改模型前必须先切回来
  @prep    预处理链：工程修复 → 保存 → 形成节点(2) → 形成楼板
  @calc    官方计算链：建模→前处理过渡 → 生成数据+全部计算 → 切到设计结果
  @recalc  一整轮：@back → [yjk_importydb 新模型.ydb（给了参数才导）] → @prep → @calc
  @takeoff 算量链：混凝土工程量 → 施工图 → 钢筋工程量（★顺序不可换，见 TAKEOFF_CHAIN）

导入校验闸门（★ 导入后自动跑，不通过就别往下算）
--------------------------------------------------
  判据不是"字节数"也不是"返回 OK"，而是**逐表行数**：`yjk_importydb` + `yjk_save` 之后
  用 `impcheck.py` 核对源 `.ydb` 与写出的 `.ymd`。必判表（tblJoint/tblColSeg/tblBeamSeg/
  tblWallSeg/tblFloor/tblStdFlr）必须逐表相等；tblSlab/tblAxis/tblProperty/tblProjectPara
  会**合法地变**（合并共线轴、拆板、展开参数表），只打印不判死。
  host 与收件箱宏（@recalc 的导入步）都自动跑；不通过时 host **以非零退出码收尾**，
  免得自动化调用方把"导入空模型 + 白算一轮"当成成功。

会话目录错配闸门（★ 收件箱每轮命令前自动判定）
----------------------------------------------
  收件箱盯的是 `--dir`，但 YJK 里"当前打开的工程"是它自己的事：用 `UINew` 在**别的目录**
  开了第二个工程后，`yjk_importydb` 返回 `OK(6.4s)`，而文件变更闸门（只看 `--dir`）什么都
  没看到 → 把导入报成失败并**跳过本轮剩余 11 条命令**，且提示指向导入而不是目录。
  现在判定"文件变化"之前先读窗口标题里的工程路径，不一致就明确报出两个路径与处置办法。

实例隔离（只操作自有实例）
--------------------------
  命令**无法按 PID 定向**（Global 事件谁抢谁执行），所以多实例共存 = 结果不可信。
  本工具的策略是「独占租约 + 只动自有实例」：
    * 只操作并只清理登记在 ~/.yjk-auto/own.json 里的**自有**实例；收尾 kill_own()
    * 发现**你在用**的实例（有主窗口）→ 拒绝开工/立即停手，**绝不替你关闭**
    * 无主窗口残留默认也不碰；要清需显式 `--clean-orphans`（或 yjk_cleanup.py --apply）
    * 收件箱每条命令执行前都校验：自有实例存活 且 无其它实例

命令速查（官方《命令说明文档》）
  工程界面: UINew(带.yjk) / UIOpen(带.yjk，6.1/7.1 会忽略路径)
  建模:     yjk_new(不带.yjk) / yjk_opennew(不带.yjk) / yjk_importydb(带.ydb)
            yjk_repair / yjk_save / yjk_formnode(1|2) / yjk_formslab_alllayer
            yjk_exportydbdefault
  计算链:   yjk_setlayersupport → yjkspre_genmodrel → yjktransload_tlplan
            → yjktransload_tlvert → SetCurrentLabel IDSPRE_ROOT
            → yjkdesign_dsncalculating_all → SetCurrentLabel IDDSN_DSP
  设计结果: yjkdisplay_dspdrawmenuzyb(轴压比) / yjkdisplay_dspdrawmenu2(配筋简图)
            yjkdesign_dsnExportDB_NoDlg(导出 dsnmodel.ydb)
"""
from __future__ import annotations

import argparse
import atexit
import ctypes
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
from ctypes import wintypes

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths as P                                              # noqa: E402
import impcheck as IC                                          # noqa: E402

FLAGS_DETACH = 0x00000008 | 0x00000200 | 0x01000000  # DETACHED|NEW_GROUP|BREAKAWAY
FLAGS_LADDER = (0x1000208, 0x208, 0x200, 0)          # 逐档降级（取第一个不被拒的）

# host 收尾用的退出码（供编排区分不同性质的非零）：
#   2 = 本轮**确认为失败**          （_HOST_ERRORS 非空）
#   3 = 预检拒绝，一个动作都没做
#   5 = 本轮**无法判定**（证据缺失：本文件里当前只有一种 —— 模态框看门狗没起来，
#       于是"没有错误弹框"这句话无法成立）
#   6 = 授权/许可问题（见 LICENSE_EXIT_CODE）
UNVERIFIED_EXIT_CODE = 5

EV_SHARE = r"Global\ShareMemoryEvent"
EV_WAIT = r"Global\WaitResaultEvent"

CALC_CHAIN = [
    ("yjk_setlayersupport", ""),
    ("yjkspre_genmodrel", ""),
    ("yjktransload_tlplan", ""),
    ("yjktransload_tlvert", ""),
    ("SetCurrentLabel", "IDSPRE_ROOT"),
    ("yjkdesign_dsncalculating_all", ""),
    ("SetCurrentLabel", "IDDSN_DSP"),
]
# 迭代轮用这条：**去掉最后"切到设计结果"那一步**。
# 理由：结果文件是计算过程写盘的，机器读结果读的是文件；而在迭代里切到结果标签纯属多余，
# 下一轮还要切回建模（来回切标签约 15s/轮）。
CALC_CHAIN_CORE = CALC_CHAIN[:-1]
PREP_CHAIN = [
    ("yjk_repair", ""),
    ("yjk_save", ""),
    ("yjk_formnode", "2"),
    ("yjk_formslab_alllayer", ""),
]

# 算量链：混凝土工程量 → 施工图 → 钢筋工程量。
# 顺序**固定不可换**（不是风格问题，换了就静默零产出）：
#    `yjkconcreteStat_statCom`（混凝土统计）归属**建模模块**（它的 HelpRef 是
#    「楼层组装\18工程量统计」），切过去会**冲掉施工图上下文**；若它排在出图之后，
#    之后所有 `DtlRC_*` 钢筋统计命令会退化成 `OK(0.0s)`（看着像成功），
#    且**一个文件都不产出、一条错误都不报**。
#    所以只能：先切建模模块做混凝土统计 → 再依次出图（板/梁/柱/墙）→ 最后在
#    工程量统计模块里做钢筋统计，中途不得再切回建模模块。
TAKEOFF_CHAIN = [
    ("SetCurrentLabel", "IDModule_Layer"),               # ① 混凝土工程量（建模模块）
    ("yjkconcreteStat_statCom", ""),
    ("SetCurrentLabel", "IDDTL_DETAIL_SLAB"),            # ② 施工图：板
    ("StdSlab_RedrawNceng", ""),
    ("StdSlab_AUTOCAL", ""),
    ("StdSlab_batgenstl", ""),                           # 会弹模态框（看门狗应答）
    ("stdslab_AutoStatstl", ""),                         # ★ 缺这步板钢筋出量全 0
    ("SetCurrentLabel", "IDDTL_DETAIL_BEAM"),            # ② 施工图：梁
    ("DtlRC_RegenReinsUpdateBeamPlan", ""),
    ("SetCurrentLabel", "IDDTL_DETAIL_COLUMN"),          # ② 施工图：柱
    ("DtlRC_DrawNewColPlan", ""),
    ("SetCurrentLabel", "IDDTL_DETAIL_WALL"),            # ② 施工图：墙
    ("DtlRC_WallPlanRegenNew", ""),
    ("SetCurrentLabel", "IDQUANTITYLIST_DETAIL"),        # ③ 钢筋工程量
    ("DtlRC_SSSE", ""),
    ("DtlRC_StatBuildingBeamSteelSpecExcel", ""),
    ("DtlRC_SSCE", ""),
    ("DtlRC_SSWE", ""),
    ("dtlrc_ColSumGJ", ""),
]

k32 = ctypes.WinDLL("kernel32", use_last_error=True)
u32 = ctypes.WinDLL("user32", use_last_error=True)
psapi = ctypes.WinDLL("psapi")
k32.OpenProcess.restype = wintypes.HANDLE
k32.OpenEventW.restype = wintypes.HANDLE
k32.QueryFullProcessImageNameW.restype = wintypes.BOOL
psapi.EnumProcesses.restype = wintypes.BOOL
u32.EnumWindows.argtypes = [ctypes.c_void_p, wintypes.LPARAM]
CB = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)


class FILETIME(ctypes.Structure):
    _fields_ = [("dwLowDateTime", wintypes.DWORD),
                ("dwHighDateTime", wintypes.DWORD)]


k32.GetProcessTimes.restype = wintypes.BOOL
k32.GetProcessTimes.argtypes = [wintypes.HANDLE, ctypes.POINTER(FILETIME),
                                ctypes.POINTER(FILETIME), ctypes.POINTER(FILETIME),
                                ctypes.POINTER(FILETIME)]

# FILETIME 的零点（1601-01-01 UTC）与 Unix epoch（1970-01-01 UTC）相差的秒数，
# 单位是秒；FILETIME 本身是 100ns 计数，所以换算时还要除 1e7。
FILETIME_EPOCH_DIFF = 11644473600.0

KILL_NAMES = ("yjks.exe", "yjkslauncher.exe", "yjkserver.exe")

# 运行期解析结果（首次使用时填充）
_RT = {"yjk": None, "dll": None}


def log(msg: str) -> None:
    print("%s  %s" % (time.strftime("%H:%M:%S"), msg), flush=True)


def rt_yjk():
    if _RT["yjk"] is None:
        _RT["yjk"] = P.find_yjk_install()
    return _RT["yjk"]


# ---------------------------------------------------------------- 进程/窗口
def procs() -> dict:
    arr = (wintypes.DWORD * 4096)()
    need = wintypes.DWORD()
    psapi.EnumProcesses(arr, ctypes.sizeof(arr), ctypes.byref(need))
    out = {}
    for i in range(need.value // 4):
        pid = arr[i]
        if not pid:
            continue
        h = k32.OpenProcess(0x1000, False, pid)
        if not h:
            continue
        buf = ctypes.create_unicode_buffer(1024)
        sz = wintypes.DWORD(1024)
        if k32.QueryFullProcessImageNameW(h, 0, buf, ctypes.byref(sz)):
            out[pid] = buf.value.rsplit("\\", 1)[-1]
        k32.CloseHandle(h)
    return out


def yjks_pids() -> list:
    return [p for p, v in procs().items() if v.lower() == "yjks.exe"]


def proc_created(pid: int):
    """进程创建时刻（epoch 秒，UTC 基准）；读不到返回 None。

    为什么需要：PID 会被系统回收再利用。`own.json` 里只记 PID 时，"上次会话被硬杀
    留下的登记"遇上"PID 恰好被回收给一个新起的 yjks.exe"，就会把**别人的实例**
    当成自有实例去清。对照 `host_alive()`：它对宿主 PID 做了复用防护（进程名要像
    python），实例 PID 一直没有。
    `GetProcessTimes` 是纯 Win32 调用：不依赖 psutil / WMI，读不到就返回 None（不猜）。
    """
    h = k32.OpenProcess(0x1000, False, pid)          # PROCESS_QUERY_LIMITED_INFORMATION
    if not h:
        return None
    try:
        c = FILETIME()
        e = FILETIME()
        k = FILETIME()
        u = FILETIME()
        ok = k32.GetProcessTimes(h, ctypes.byref(c), ctypes.byref(e),
                                 ctypes.byref(k), ctypes.byref(u))
        if not ok:
            return None
        ticks = (c.dwHighDateTime << 32) | c.dwLowDateTime
        return ticks / 1e7 - FILETIME_EPOCH_DIFF
    finally:
        k32.CloseHandle(h)


def titles(pid: int) -> list:
    out = []

    def cb(h, l):
        p = wintypes.DWORD()
        u32.GetWindowThreadProcessId(h, ctypes.byref(p))
        if p.value == pid and u32.IsWindowVisible(h):
            c = ctypes.create_unicode_buffer(64)
            u32.GetClassNameW(h, c, 64)
            if c.value == "yjks":
                t = ctypes.create_unicode_buffer(400)
                u32.GetWindowTextW(h, t, 400)
                if t.value:
                    out.append(t.value)
        return True
    u32.EnumWindows(CB(cb), 0)
    return out


def events_alive() -> list:
    r = []
    for name in (EV_SHARE, EV_WAIT):
        h = k32.OpenEventW(0x00100000, False, name)
        r.append(bool(h))
        if h:
            k32.CloseHandle(h)
    return r


def kill_all(verbose: bool = True) -> None:
    """无差别结束**全部** yjks 实例（人工逃生口；自动化流程不得调用）。"""
    ins = instances()
    dead = [i["pid"] for i in ins if i["kind"] == "dead"]
    ids = [i["pid"] for i in ins if i["kind"] != "dead"]      # 取并集（含 psapi 看不到的）；残壳跳过
    if not ids:
        if verbose:
            log("无残留 yjks 实例")
        if dead and verbose:
            log("  另有残壳 %s：0 线程已终止，TerminateProcess/taskkill 均被拒（管理员也一样），"
                "只能重启清理" % dead)
        return
    if verbose:
        log("杀掉: %s" % [(i["pid"], KIND_TAG.get(i["kind"], i["kind"])) for i in instances()])
    for p in ids:
        kill_pid(p, verbose=verbose)
    left = wait_gone(ids, timeout=25)
    own_clear()
    if verbose:
        if left:
            log("!! 清场不彻底：%s 仍在（TerminateProcess err=5 = 权限被拒/被安全软件拦截，"
                "请用管理员权限或在其窗口里关闭）" % left)
        else:
            log("清场完成")


# ---------------------------------------------------------------- 实例归属
_PS_EXE = None
_PS_WARNED = []


def powershell_exe() -> str:
    """定位 powershell.exe。

    PATH 里**不一定有** powershell（`shutil.which('powershell')` 可能返回 None），
    于是 `subprocess.run(["powershell", ...])` 抛 FileNotFoundError —— 而调用方若把异常吞掉，
    所有依赖 PowerShell 的探测（命令行、注册表等）就会**静默失效**。故这里按 SystemRoot 拼全路径。
    """
    global _PS_EXE
    if _PS_EXE is None:
        sysroot = os.environ.get("SystemRoot") or r"C:\Windows"
        cands = [shutil.which("powershell"),
                 os.path.join(sysroot, "System32", "WindowsPowerShell", "v1.0", "powershell.exe"),
                 r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"]
        _PS_EXE = next((c for c in cands if c and os.path.exists(c)), "powershell")
    return _PS_EXE


def ps(cmd: str, timeout: int = 30) -> str:
    """跑一条 PowerShell 取文本。失败**只警告一次**并返回空串（不静默）。"""
    try:
        r = subprocess.run([powershell_exe(), "-NoProfile", "-Command", cmd],
                           capture_output=True, text=True, timeout=timeout,
                           encoding="utf-8", errors="replace")
        if r.returncode != 0 and not _PS_WARNED:
            _PS_WARNED.append(1)
            log("!! PowerShell 返回码 %s（后续只提示一次）：%s" % (r.returncode, (r.stderr or "")[:200]))
        return r.stdout or ""
    except Exception as e:                                     # noqa: BLE001
        if not _PS_WARNED:
            _PS_WARNED.append(1)
            log("!! PowerShell 调用失败（后续只提示一次）: %r" % e)
            log("   影响：读不到 yjks 命令行/注册表信息 → 实例归属判断会退化到只看「有没有窗口」")
        return ""


def yjks_info() -> dict:
    """一次 WMI 查询拿到 {pid: {"threads": n, "cmdline": s}}。

    `ThreadCount == 0` 的 yjks 是**已终止但内核还没回收的残壳**：它不能再执行任何代码
    （因此不抢 IPC 事件、不干扰任何东西），但 PID 还在。所以"PID 存在"**不等于**"实例活着"。
    """
    out = {}
    txt = ps("Get-CimInstance Win32_Process -Filter \"Name='yjks.exe'\" | "
             "ForEach-Object { \"$($_.ProcessId)|$($_.ThreadCount)|$($_.CommandLine)\" }")
    for ln in txt.splitlines():
        parts = ln.strip().split("|", 2)
        if len(parts) < 2 or not parts[0].strip().isdigit():
            continue
        try:
            th = int(parts[1])
        except ValueError:
            continue
        out[int(parts[0].strip())] = {"threads": th,
                                      "cmdline": (parts[2] if len(parts) > 2 else "").strip()}
    return out


def dead_shells() -> set:
    """已终止待回收的残壳 PID 集合（不该阻断开工，也不必去杀，重启即清）。"""
    return {p for p, v in yjks_info().items() if v.get("threads") == 0}


def yjks_cmdlines() -> dict:
    """{pid: 命令行} —— 判断某个实例是否正打开**别的**工程。"""
    return {p: v["cmdline"] for p, v in yjks_info().items()}


def opened_project(cmdline: str):
    """从 yjks 命令行里取它指定的工程路径（-open <path> 或裸 *.yjk 参数）。"""
    if not cmdline:
        return None
    m = re.search(r"-open\s+\"?([^\"]+?)\"?(?=\s+-|$)", cmdline, re.I)
    if m:
        return m.group(1).strip().rstrip(".")
    for tok in cmdline.split():
        t = tok.strip('"')
        if t.lower().endswith(".yjk"):
            return t
    return None


def foreign_instances(workdir=None) -> list:
    """列出「正打开其它工程目录」的 yjks 实例（无参启动的残留不算）。

    仅用于**报出**；真正的隔离策略见下面的 instances()/exclusive_ok()。
    """
    out = []
    cwd = os.path.normcase(os.path.abspath(workdir)) if workdir else None
    for pid, cl in yjks_cmdlines().items():
        proj = opened_project(cl)
        if not proj:
            continue
        d = os.path.normcase(os.path.dirname(os.path.abspath(proj)))
        if cwd and d == cwd:
            continue
        out.append({"pid": pid, "proj": proj, "cmdline": cl})
    return out


# ---------------------------------------------------------------- 实例隔离（只操作自有实例）
# 能力边界（见 references/ipc-protocol.md §4）：
#   * 发命令 **不能定向到某个 PID** —— 两个事件是 Global\ 命名对象，谁先抢谁执行；
#     所以"多实例共存还能安全操作"**不成立**，多实例 = 命令应答不可信。
#   * 能按 PID 定向的只有两件事：**结束进程**、**读窗口标题/命令行**。
# 因此策略是「独占租约 + 只动自有实例」：
#   ① own     自有（登记在 ~/.yjk-auto/own.json 的 PID）—— 只用它、收尾只杀它
#   ② foreign 有主窗口的实例（你在用的界面）—— **一律不碰**，出现即拒绝/停手
#   ③ orphan  无主窗口残留（YJKAPI.init / WinExec 拉起的）—— 默认也不碰，
#             需 --clean-orphans 显式允许才清
OWN_FILE = os.path.join(P.USER_CACHE, "own.json")


def _own_read() -> dict:
    try:
        return json.load(open(OWN_FILE, encoding="utf-8"))
    except Exception:                                          # noqa: BLE001
        return {}


def own_pid():
    """登记的自有 PID；**身份对不上（PID 被回收）就不认它**，并返回 None。

    两道判据（缺一不可）：

    ① 存在性取 **psapi ∪ WMI**：`procs()` 用 `QueryFullProcessImageNameW`，
       该调用失败时会**静默丢弃**那个进程（见 `instances()` 的注释）。只信 psapi
       会把**还活着的**自有实例判成"已消失"，顺手删掉登记 —— 此后它既不被认作
       自有实例，也不会被收尾清掉（审计 S29）。

    ② 身份靠**创建时刻**：登记时把 `proc_created(pid)` 记进 own.json，这里比对。
       对不上说明这个 PID 现在属于**另一个**进程（PID 回收），此时绝不动它：
       老版只判"这个 PID 现在是个 yjks.exe"，于是可能去结束别人的实例（审计 S28）。
       登记里没有 `created`（旧版 own.json）时无法校验，保持老行为，只提示一次。
    """
    d = _own_read()
    pid = d.get("pid")
    if not pid:
        return None
    pid = int(pid)
    if pid not in yjks_pids():
        if pid not in yjks_info():
            if d:
                own_clear()
            return None
        # psapi 漏了它（QueryFullProcessImageNameW 失败），但 WMI 看得到 → 它还在，
        # 不能删登记（删了就永远不会再被收尾清理）。
        _warn_once("psapi 没列出自有实例 pid=%s，但 WMI 看得到 → 判定它仍活着，保留登记" % pid)
    rec = d.get("created")
    now = proc_created(pid)
    if rec and now and abs(float(rec) - now) > 2.0:
        log("!! own.json 里登记的实例 pid=%s **身份对不上**：创建时刻 %s ≠ %s。"
            % (pid, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(float(rec))),
               time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(now))))
        log("   这是 PID 被系统回收后的**另一个进程**（不是我们的实例）—— 不会去动它。")
        log("   登记已作废；若该进程是你自己的，用 `status` 看它、用 close 明确关闭。")
        own_clear()
        return None
    if not rec and d:
        _warn_once("own.json 没有记实例创建时刻（旧版登记）—— 无法校验 PID 是否被回收")
    return pid


def _warn_once(msg: str) -> None:
    """同一句提示每个进程只打一次（这些检查在收件箱循环里会被反复调用）。"""
    if msg in _WARNED_ONCE:
        return
    _WARNED_ONCE.append(msg)
    log("（提示，只报一次）%s" % msg)


_WARNED_ONCE = []


def own_claim(pid: int, exe: str = "", workdir: str = "") -> None:
    """登记自有实例 —— 此后"我们的实例"只认这个 PID。

    同时记下：
    * **本宿主进程**的 PID：用来区分"上次会话的残留"与"另一个正在跑的会话"；
    * **被登记进程的创建时刻**（`proc_created`）：PID 会被系统回收，只有它能证明
      "这个 PID 还是当初那个进程"，own_pid() 据此拒绝被回收后的陌生进程。
    """
    os.makedirs(P.USER_CACHE, exist_ok=True)
    json.dump({"pid": int(pid), "exe": exe, "workdir": os.path.abspath(workdir or ""),
               "host_pid": os.getpid(),
               "created": proc_created(pid),
               "started": time.strftime("%Y-%m-%d %H:%M:%S")},
              open(OWN_FILE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def host_alive(pid) -> bool:
    """登记里的宿主进程是否还活着（进程名要像 python，避免 PID 复用误判）。"""
    if not pid:
        return False
    n = (procs().get(int(pid)) or "").lower()
    return n.startswith("python") or n in ("py.exe", "pyw.exe")


def own_clear() -> None:
    try:
        os.remove(OWN_FILE)
    except OSError:
        pass


def has_main_window(pid: int) -> bool:
    """该 pid 是否持有 yjks 类顶层窗口（不看可见性、不看标题）。

    比"标题非空"更保守：宁可把无名实例判成"你在用的"（于是不碰），也不要误判成残留去清。
    """
    hit = []

    def cb(h, l):
        p = wintypes.DWORD()
        u32.GetWindowThreadProcessId(h, ctypes.byref(p))
        if p.value == pid:
            c = ctypes.create_unicode_buffer(64)
            u32.GetClassNameW(h, c, 64)
            if c.value == "yjks":
                hit.append(True)
        return True
    u32.EnumWindows(CB(cb), 0)
    return bool(hit)


def instances() -> list:
    """把所有 yjks 实例分成 own / foreign / orphan 三类。

    PID 取 **psapi ∪ WMI** 两个来源的并集：
      有的实例 `OpenProcess` 成功但 `QueryFullProcessImageNameW`
      返回 0（err=31），于是被 `procs()` **静默丢弃**；而 WMI（Get-CimInstance）能看到它。
      只靠 psapi 会让隔离闸门漏掉这类实例 —— 那就等于"以为独占，其实两个实例在抢事件"。
    """
    own = own_pid()
    info = yjks_info()
    ids = sorted(set(yjks_pids()) | set(info.keys()))
    out = []
    for p in ids:
        v = info.get(p) or {}
        cl = v.get("cmdline", "")
        if v.get("threads") == 0:
            # 已终止但内核还没回收的残壳：PID 还在，但**0 线程意味着它不能再执行任何代码**
            #   （不抢全局事件、不干扰任何东西），且 TerminateProcess/taskkill 一律被拒
            #   （管理员也一样）—— 只能等系统回收或重启。所以它既不该阻断开工，也不必去杀。
            kind = "dead"
        elif own and p == own:
            kind = "own"
        elif has_main_window(p):
            kind = "foreign"
        elif cl and opened_project(cl):
            # 没有主窗口、但**命令行里带着工程**（-open <x>.yjk）→ 是人为拉起的，别当残留清。
            # 真正的残留是 YJKAPI.init/WinExec 那种**无参**拉起的无窗口实例。
            kind = "foreign"
        else:
            kind = "orphan"
        out.append({"pid": p, "kind": kind, "titles": titles(p),
                    "cmdline": cl, "proj": opened_project(cl)})
    return out


def id_sources() -> dict:
    """诊断用：两个 PID 来源各看到谁（不一致时说明有进程被 psapi 漏掉）。"""
    a, b = set(yjks_pids()), set(yjks_cmdlines())
    return {"psapi": sorted(a), "wmi": sorted(b), "psapi漏掉": sorted(b - a), "wmi看不到": sorted(a - b)}


KIND_TAG = {"own": "自有", "foreign": "你的(有窗口)",
            "orphan": "残留(无窗口)", "dead": "残壳(已终止待回收)"}


def window_text(i: dict) -> str:
    """实例的窗口描述。

    `titles()` 要求窗口**可见且标题非空**，比 `has_main_window()` 严格（后者只看有没有
    yjks 类顶层窗口）；窗口刚创建、还在渲染时会出现"分类说有窗口、标题却读不到"的情况，
    这里如实写清楚，别自相矛盾地显示"无窗口"。
    """
    if i.get("titles"):
        return i["titles"][0][:70]
    if i.get("kind") == "orphan":
        return "（无主窗口）"
    return "（有主窗口，标题暂不可读）"


def describe(ins: list) -> str:
    if not ins:
        return "无"
    parts = []
    for i in ins:
        s = "pid=%s[%s]" % (i["pid"], KIND_TAG.get(i["kind"], i["kind"]))
        if i.get("proj"):
            s += " 打开=%s" % i["proj"]
        parts.append(s)
    return "; ".join(parts)


def close_hint(pid) -> str:
    """给出"精确关闭某个实例"的可粘贴命令（只认 PID，不做模糊匹配）。"""
    return 'yjk_auto.py close --pid %s --yes' % pid


def print_close_howto(i: dict) -> None:
    """把"关哪个、关了会怎样、怎么关"一次说清 —— 光说"请先自行关闭"不够。"""
    log("     · pid=%s [%s] %s" % (i["pid"], KIND_TAG.get(i["kind"], i["kind"]), window_text(i)))
    if i.get("proj"):
        log("       正打开的工程: %s" % i["proj"])
    if i.get("cmdline"):
        log("       命令行: %s" % i["cmdline"][:160])
    log("       关闭方式（会中断该会话，未保存内容会丢）：")
    log("         %s" % close_hint(i["pid"]))
    log("       （也可以直接在 YJK 窗口里关；本工具不会替你关）")


def kill_pid(pid: int, verbose: bool = False) -> bool:
    """结束某个 PID。**返回是否真的发出成功**；失败会给出 err 与常见原因。

    注意：`OpenProcess(PROCESS_TERMINATE)` 可能成功，但 `TerminateProcess` 返回 0、err=5
    （拒绝访问）—— 因为目标进程权限更高（例如以管理员身份启动），或被安全软件拦截。
    这时**不能报"已关闭"**，否则又是一次"假成功"。
    """
    h = k32.OpenProcess(0x0001, False, pid)
    if not h:
        if verbose:
            log("  OpenProcess(TERMINATE) 失败 pid=%s err=%s" % (pid, ctypes.get_last_error()))
        return False
    ok = bool(k32.TerminateProcess(h, 1))
    err = ctypes.get_last_error()
    k32.CloseHandle(h)
    if not ok and verbose:
        log("  TerminateProcess 失败 pid=%s err=%s%s"
            % (pid, err, "（5=拒绝访问：对方权限更高，或被安全软件拦截）" if err == 5 else ""))
    return ok


def alive_pids() -> set:
    """**真正活着**的 yjks PID（0 线程的残壳不算）。"""
    info = yjks_info()
    alive = {p for p, v in info.items() if v.get("threads") != 0}
    return alive | (set(yjks_pids()) - set(info))       # psapi 有而 WMI 没列出的，按活着算


def wait_gone(pids, timeout: float = 10.0, interval: float = 2.0) -> list:
    """等这些 PID 真的消失；**已终止的残壳算消失**（它不能再执行任何代码）。"""
    pids = list(pids)
    t0 = time.time()
    while True:
        alive = alive_pids()
        left = [p for p in pids if p in alive]
        if not left or time.time() - t0 >= timeout:
            return left
        time.sleep(interval)


def kill_own(verbose: bool = True, wait: float = 20.0) -> bool:
    """只清**自有**实例（own.json 里那个），绝不碰别的实例。返回是否真的清掉了。

    返回 False 有两条路径，都意味着"此刻**不能**报清理成功"：
    * 登记实例还在（终止请求被拒 / 超时）；
    * **登记已失效，但无法确认那个实例不是我们的** —— 见下面 no-pid 分支。
    """
    d = _own_read()
    pid = own_pid()
    if not pid:
        # 这里以前直接 own_clear() + "无自有实例需要清理" + return True：
        #   "没有登记"与"登记已失效"被当成"清理成功"。而 own_pid() 判"失效"的依据
        #   曾是 psapi（它会静默漏进程），于是可能出现：实例还活着、登记却被删掉、
        #   调用方收到"清理成功"，此后这个实例既不被认作自有、也永远不会被收尾清掉。
        #   现在：psapi 漏掉的进程仍会被 WMI 看到 → own_pid() 保留登记；
        #   万一两处都看不到，只要 WMI 报出"psapi 漏过进程"，就不报成功。
        lost = (id_sources().get("psapi漏掉") or []) if d else []
        if lost:
            log("!! own.json 里登记过实例，但现在按 psapi 找不到它；"
                "而 WMI 看到 psapi **漏掉**的实例 %s" % lost)
            log("   → 无法确认它不是我们自己的实例，**不报「清理成功」**，也不删登记。")
            log("   处置：先 `yjk_auto.py status` 看这些 PID 是什么，再人工处理。")
            return False
        if verbose:
            log("无自有实例需要清理")
        own_clear()
        return True
    # 安全闸：登记的实例若正打开**登记工作目录之外**的工程，说明 own.json 不可信
    # （被手改过、或 PID 被复用），此时拒绝结束它，交给人判断。
    wd = (d.get("workdir") or "").strip()
    if wd:
        for t in titles(pid):
            p = title_to_proj(t)
            if not p:
                continue
            if not os.path.normcase(os.path.abspath(p)).startswith(
                    os.path.normcase(os.path.abspath(wd))):
                log("!! 登记的实例 pid=%s 正打开的工程不在登记目录内：" % pid)
                log("     工程: %s" % p)
                log("     登记 workdir: %s" % wd)
                log("   own.json 可能被改动或 PID 被复用 → **拒绝结束该实例**，请人工确认。")
                return False
        if not any(title_to_proj(t) for t in titles(pid)):
            # 标题解析不出工程路径（欢迎页/正在渲染）：安全闸这一条**无从判定**。
            # 身份校验（own_pid 里的创建时刻）在前，这里只如实说明闸门没生效。
            _warn_once("pid=%s 的窗口标题读不出工程路径（欢迎页/渲染中）→ "
                       "「工程是否在登记目录内」这条闸门本次无法判定" % pid)
    if verbose:
        log("清理自有实例: pid=%s（exe=%s，登记于 %s，workdir=%s）"
            % (pid, d.get("exe") or "?", d.get("started") or "?", wd or "?"))
    ok = kill_pid(pid, verbose=verbose)
    left = wait_gone([pid], timeout=wait) if ok else [pid]
    if left:
        log("!! 自有实例 pid=%s 没清掉（终止请求被拒或超时）—— 保留登记，请人工处理" % pid)
        return False
    own_clear()
    if verbose:
        log("自有实例已清")
    return True


def exclusive_ok(own=None):
    """命令前的排他性检查 → (ok, 原因)。

    任何**非自有**实例出现都算"命令不可信"（全局事件会被抢）：此时停手，而不是去杀它。
    """
    ins = instances()
    if own and not any(i["pid"] == own and i["kind"] == "own" for i in ins):
        return False, "自有实例 pid=%s 已不存在（被关闭/崩溃/变成残壳）" % own
    # 残壳(dead)不参与：它 0 线程、不可能抢事件
    others = [i for i in ins if i["kind"] not in ("own", "dead")]
    if others:
        return False, ("出现非自有实例 %s —— 全局事件会被抢、命令应答不可信，已停手"
                       "（未杀任何实例）" % [(i["pid"], i["kind"]) for i in others])
    return True, ""


def _file_size(path: str):
    try:
        return os.path.getsize(path)
    except OSError:
        return None


# ---------------------------------------------------------------- 文件快照
def snap(root: str) -> dict:
    d = {}
    if not os.path.isdir(root):
        return d
    for dp, dn, fn in os.walk(root):
        for f in fn:
            fp = os.path.join(dp, f)
            try:
                st = os.stat(fp)
                d[fp] = (st.st_size, st.st_mtime)
            except OSError:
                pass
    return d


def diff(before: dict, after: dict) -> list:
    return sorted(k for k, v in after.items() if before.get(k) != v)


def wait_until(pred, timeout: float = 10.0, interval: float = 0.5) -> float:
    """条件等待：pred() 一旦为真立刻返回，最多等 timeout 秒。返回实际等待秒数。

    用来替掉固定 `sleep`：盲等要么浪费（条件早就满足了），要么不够（还没就绪就走）。
    """
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            if pred():
                break
        except Exception:                                      # noqa: BLE001
            pass
        time.sleep(interval)
    return time.time() - t0


# ---------------------------------------------------------------- 官方客户端
class Client:
    """官方控制客户端。自动适配 6/7/8 三代 DLL 与多种 RunCmd 签名。

    * 6.x/7.x：`YJKIPC.YJKSControl`(RunCmd(kw,param)->string)
      或安装目录 `YJKSControl`(RunCmd(kw,param,out string))
    * 8.x：安装根 `YJKAPI.dll` 的 `YJKIPC.YJKSControl`
      — RunCmd 返回 void；新增静态方法
        `initConfig(ControlConfig)` / `RunYJK(exe)` / `exit()` /
        `SelectYjkProcess()` / `IPC_Pipe` / `IPC_ShareMem` /
        `GetWorkPath()` / `SetWorkPath(path)` / `startprocess(exe,args)`。
      **8.x 必须先 initConfig 再发命令**（官方 test04），否则命令可能静默不执行。

    **绝不调用 init()** —— 7.x 的 init 会 WinExec 再拉起一个无窗口 yjks；
    8.x 用 initConfig +（可选）RunYJK，二者都受 ControlConfig.Pid/Invisible 控制。
    """

    def __init__(self, dll: str | None = None):
        import clr                                             # noqa: F401
        from System import Array, Object, Activator
        from System.Reflection import Assembly
        info = P.find_yjkapi_dll(dll)
        if not info["path"]:
            raise RuntimeError("未找到可用的控制 DLL：\n  " + "\n  ".join(info["notes"]))
        self.dll = info["path"]
        self.kind = info["kind"]
        self.caps = info.get("caps") or {}
        # 8.1 安装根 DLL 依赖同目录原生库，必须 chdir + LoadFrom（LoadFile 会抛
        # ReflectionTypeLoadException）
        cwd = os.getcwd()
        try:
            os.chdir(os.path.dirname(os.path.abspath(self.dll)))
            if os.path.dirname(os.path.abspath(self.dll)) not in sys.path:
                sys.path.insert(0, os.path.dirname(os.path.abspath(self.dll)))
            asm = Assembly.LoadFrom(self.dll)
        finally:
            try:
                os.chdir(cwd)
            except OSError:
                pass
        T = asm.GetType(self.kind)
        if T is None:
            raise RuntimeError("DLL 内无类型 %s: %s" % (self.kind, self.dll))
        self._asm, self._T = asm, T
        self._Activator = Activator
        ms = [m for m in T.GetMethods() if m.Name == "RunCmd"]
        if not ms:
            raise RuntimeError("该 DLL 的 %s 无 RunCmd 方法: %s" % (self.kind, self.dll))
        self._m = min(ms, key=lambda m: len(m.GetParameters()))
        self._n = len(self._m.GetParameters())
        self._Array, self._Object = Array, Object
        names = {m.Name for m in T.GetMethods()}
        self.has_init_config = "initConfig" in names
        self.has_run_yjk = "RunYJK" in names
        self.has_exit = "exit" in names
        self.has_select_process = "SelectYjkProcess" in names

    def capabilities(self) -> dict:
        return {"dll": self.dll, "kind": self.kind,
                "initConfig": self.has_init_config, "RunYJK": self.has_run_yjk,
                "exit": self.has_exit, "SelectYjkProcess": self.has_select_process}

    def _config_type(self):
        for n in ("YJKIPC.ControlConfig", "ControlConfig"):
            try:
                t = self._asm.GetType(n)
            except Exception:                                  # noqa: BLE001
                t = None
            if t is not None:
                return t
        return None

    def configure(self, version=None, invisible=False, pid=-1):
        """8.x：initConfig(ControlConfig{Version,Invisible,Pid})。失败返回说明串。"""
        if not self.has_init_config:
            return "SKIP(该 DLL 无 initConfig，按 6/7 路径继续)"
        ct = self._config_type()
        if ct is None:
            return "SKIP(找不到 ControlConfig 类型)"
        cfg = self._Activator.CreateInstance(ct)
        cfg.Version = version or "8.0.0"
        cfg.Invisible = bool(invisible)
        cfg.Pid = int(pid)
        try:
            return self._T.GetMethod("initConfig").Invoke(None, [cfg])
        except Exception as e:                                 # noqa: BLE001
            return "异常:" + repr(e)

    def run_yjk(self, exe_path):
        """8.x：由官方 API 启动 yjks（等价于 run. 之前官方要求先 configure）。"""
        if not self.has_run_yjk:
            return "SKIP(该 DLL 无 RunYJK)"
        try:
            return self._T.GetMethod("RunYJK").Invoke(None, [exe_path])
        except Exception as e:                                 # noqa: BLE001
            return "异常:" + repr(e)

    def close(self):
        """8.x：exit() 让静默启动的 yjks 自行退出（6/7 无此能力）。"""
        if not self.has_exit:
            return "SKIP(该 DLL 无 exit)"
        try:
            self._T.GetMethod("exit").Invoke(None, None)
            return "OK"
        except Exception as e:                                 # noqa: BLE001
            return "异常:" + repr(e)

    def call(self, cmd: str, param: str = ""):
        args = (cmd, param) if self._n <= 2 else (cmd, param, "")
        try:
            arr = self._Array[self._Object](args)
        except Exception:                                      # noqa: BLE001
            arr = args
        return self._m.Invoke(None, arr)

    def run(self, cmd: str, param: str = "", timeout: int = 300,
            alive=None, poll: float = 2.0) -> str:
        """执行一条命令并等结果。

        `alive`：实例中途死掉时必须**立刻**放弃等待（缺陷 L5「收尾卡住」）
        ------------------------------------------------------------------
        `yjks` 被硬杀（或自己崩）时，结果事件永远不会来。老版会一直阻塞到 `timeout`
        （host 传的正是 **900s**）才返回 —— 而**收件箱循环正卡在这条命令里**，
        后面写进收件箱的 `exit` 也读不到，于是"收尾"被推迟到超时之后。50 案例
        F01/F02 的实测现场就是：`session_close` 报「★ 未响应 exit，已强制收尾」，
        各耗 **180.1s**（而实例其实早已不存在）。

        现在每 `poll` 秒查一次 `alive()`：实例一没就立刻返回 `实例已退出(...)`，
        循环随即回到收件箱去处理 `exit` —— 收尾延迟从"等到超时"压到 **~2s**。

        `alive=None`（默认）保持老行为：用于"实例身份未知"的探测类调用。
        """
        res = {}

        def work():
            t0 = time.time()
            try:
                res["ret"] = self.call(cmd, param)
                res["dt"] = time.time() - t0
            except Exception as e:                             # noqa: BLE001
                res["err"] = repr(e)
        th = threading.Thread(target=work, daemon=True)
        th.start()
        t0 = time.time()
        while True:
            th.join(poll)
            if not th.is_alive():
                break
            el = time.time() - t0
            if alive is not None and not alive():
                return "实例已退出(%.1fs，放弃等结果)" % el
            if el >= timeout:
                return "TIMEOUT(>%ds)" % timeout
        if "err" in res:
            return "异常:" + res["err"]
        return "OK(%.1fs)" % res.get("dt", -1)


# ---------------------------------------------------------------- 启动/引导
def spawn(exe, cwd, flags=None):
    """逐档降级启动：CREATE_BREAKAWAY_FROM_JOB 可能被拒（WinError 5）。"""
    for fl in (flags or FLAGS_LADDER):
        try:
            return subprocess.Popen([exe], cwd=cwd, creationflags=fl,
                                    stdin=subprocess.DEVNULL,
                                    stdout=subprocess.DEVNULL,
                                    stderr=subprocess.DEVNULL)
        except OSError:
            continue
    raise RuntimeError("无法启动 %s（尝试过 flags=%s）" % (exe, flags or FLAGS_LADDER))


def ensure_launcher(verbose: bool = True) -> bool:
    ins = rt_yjk()
    if [p for p, v in procs().items() if v.lower() == "yjklauncher.exe"]:
        if verbose:
            log("YjkLauncher 已在运行")
        return True
    if not ins["launcher"]:
        if verbose:
            log("!! 未找到 YjkLauncher.exe（安装位置=%s）；"
                "可手动先打开一次 YJK" % (ins["root"] or "未探测到"))
        return False
    if verbose:
        log("启动 YjkLauncher.exe ...")
    spawn(ins["launcher"], ins["root"])
    time.sleep(15)
    ok = bool([p for p, v in procs().items() if v.lower() == "yjklauncher.exe"])
    if verbose:
        log("YjkLauncher %s" % ("就绪" if ok else "未起来"))
    return ok


_DLGWATCH = None
# 非空 = **本该拉起看门狗却起不来**的原因（import 失败）。为什么必须记下来：
# `dlgwatch_errors()` 返回空列表有**两种**完全不同的含义 ——「确实没有错误弹框」
# 与「根本没人看着弹框」。以前两者不可区分，`cmd_host` 收尾据它判"本轮是否有真失败"
# 就会把后者当成前者，而这个校验的失效方向是**偏松**的（本包反复强调：RunCmd 的 OK
# 一文不值，真错误只在弹框里）。
_DLGWATCH_FAIL = []


def start_dlgwatch(verbose: bool = True):
    """拉起模态框看门狗（后台线程）。必须在启动 `yjks.exe` **之前**调用。

    为什么必须有它
    --------------
    YJK 在出错时会弹一个模态确认框（例如「计算分析失败」）。模态期间 yjks
    主窗口被 Disable，IPC 命令从此不返回 —— 表现为"命令挂死"。
    计算失败（分析失败[-1]）时，host --import --prep --calc 会卡在
    SetCurrentLabel('IDSPRE_ROOT') 长时间无输出、无退出。
    看门狗把这些框按规则答掉，流程才能正常收尾并给出错误信息。

    启动阶段**不得盲答**（审计 S55）
    --------------------------------
    host 必须在启动 yjks 之前就拉起看门狗（那时还不知道 pid），而"pid 未知"意味着
    无法判断一个对话框属于哪个实例：若此时仍对未命中规则的框一律回「是」，同机**别人
    正在用**的 YJK 弹的任何确认框都会被答掉。
    所以 `DialogWatch(None)` 在收窄之前**只登记、不点任何按钮**（见 dlgwatch 的
    「作用范围」），拿到自有实例 pid 后由 `_host` 立刻 `narrow(pid)` 才开始应答。

    实现见同目录 dlgwatch.py（唯一有效应答 = 向对话框发 WM_COMMAND；
    BM_CLICK / 键盘消息 / WM_CLOSE 对 YJK 的模态框都不起作用）。
    """
    global _DLGWATCH
    if _DLGWATCH is not None:
        return _DLGWATCH
    try:
        import dlgwatch
    except Exception as e:                                         # noqa: BLE001
        del _DLGWATCH_FAIL[:]
        _DLGWATCH_FAIL.append(repr(e))
        if verbose:
            log("!! 看门狗不可用（%r）：出错弹框时命令会挂到超时" % e)
            log("   后果：本轮**无法判定**有没有真错误弹框（收尾会以退出码 %d 说明这点）"
                % UNVERIFIED_EXIT_CODE)
        return None
    # pid=None：**收窄之前只登记不动手**（不会碰别人的 YJK 的对话框）
    _DLGWATCH = dlgwatch.DialogWatch(None, log=log)
    _DLGWATCH.start()
    atexit.register(stop_dlgwatch)
    if verbose:
        log("模态框看门狗已拉起（启动阶段只登记不动手；拿到自有实例 pid 后收窄并开始应答）")
    return _DLGWATCH


def dlgwatch_unavailable():
    """看门狗**没在看弹框**的原因（它正在运行 → 返回 []）。

    与 `dlgwatch_running()` 配对使用：`dlgwatch_errors()` 返回空列表时，用它区分
    「确实没有错误弹框」与「根本没人看着弹框」。
    """
    if _DLGWATCH is not None:
        return []
    return list(_DLGWATCH_FAIL)


def stop_dlgwatch():
    global _DLGWATCH
    if _DLGWATCH is not None:
        try:
            _DLGWATCH.stop()
        except Exception:                                          # noqa: BLE001
            pass
        _DLGWATCH = None


def dlgwatch_errors():
    """看门狗收集到的**真错误**弹框：[(标题, 正文)]。关键步骤后应当检查。"""
    return list(_DLGWATCH.errors) if _DLGWATCH is not None else []


def dlgwatch_failed():
    """应答**发送失败**的弹框（`PostMessageW` 返回 0 → 框可能还挂着）。

    不能当"已处理"：框还在，那条命令的结果就不可信（审计 S22）。
    收尾时据此给"无法判定"的退出码。
    """
    return list(getattr(_DLGWATCH, "failed", [])) if _DLGWATCH is not None else []


def dlgwatch_unanswered():
    """已收窄、但**未命中规则因而没有应答**的框：[(标题, 正文)]。

    这是新口径（`DEFAULT = None`）下的正常结果：看不懂的框一律留给人工。它意味着
    "这条命令可能正被一个框挡住（会走到超时）"，所以收尾要如实报出来。
    """
    return list(getattr(_DLGWATCH, "unanswered", [])) if _DLGWATCH is not None else []


def dlgwatch_noted():
    """**未收窄阶段**只登记、未动作的框：[(pid, 标题, 正文)]。

    这些框属于"当时还不知道归属"的实例（可能是**别人**正在用的 YJK）——
    本工具刻意不碰它们；这里只把它们报出来供人判断。
    """
    return list(getattr(_DLGWATCH, "noted", [])) if _DLGWATCH is not None else []


def dlgwatch_license():
    """看门狗看到的**授权/许可类**对话框：[(标题, 正文)]。

    看门狗对这类框**不点任何按钮**（见 `dlgwatch.LICENSE_KW`），只登记，
      由这里驱动「暂停 + 提示用户处理」，而不是让机器替用户猜「是/否」。
    """
    return list(getattr(_DLGWATCH, "license", [])) if _DLGWATCH is not None else []


def dlgwatch_running() -> bool:
    """看门狗到底起没起来。

    为什么单独看这个：`dlgwatch_errors()` 返回空列表有**两种**完全不同的含义 ——
      「确实没有错误弹框」与「根本没人看着弹框」。以前两者不可区分，
      收尾时据它判"本轮是否有真失败"就会把后者当成前者。
    """
    return _DLGWATCH is not None


# 授权阻塞状态（`boot_yjks` 里置位；`_host` 据此决定暂停还是失败）
_LICENSE_BLOCKED = []
LICENSE_EXIT_CODE = 6          # 授权/许可问题：与"本轮确认为失败"(2)、"预检拒绝"(3) 区分开


def license_blocked():
    return list(_LICENSE_BLOCKED)


def license_marker(workdir: str) -> str:
    """给编排器/用户看的「授权待处理」标志文件。"""
    return os.path.join(workdir, "_yjk_license.need_user")


def license_state(workdir: str):
    """读某个工作目录的「授权暂停」标志，返回 `(blocked, 对话框内容, 已写多少秒)`。

    为什么必须有这个**读口**（只有写、没有读等于没做成机制）
    ----------------------------------------------------------
    `--on-license pause` 时宿主进程把标志写到 `<工作目录>/_yjk_license.need_user`
    并**继续等待**。可是宿主内存里的 `_LICENSE_BLOCKED` 只存在于**那个进程**里 ——
    另一个 agent / 另一个会话 / 用户自己，若不去读这个文件，看到的只有
    「收件箱未就绪（rc=2）」，**完全不知道是授权问题**，于是会去反复重试、
    或者以为模型/脚本坏了。

    所以：标志文件是本机制**跨进程唯一的信道**，这里把它读出来，
    由 `status`（人看）与 `send`（编排看）两个入口暴露。
    """
    p = license_marker(workdir)
    if not os.path.exists(p):
        return False, "", 0.0
    try:
        # utf-8-sig：这个标志**是给人看的，用户很可能用记事本打开/改过**，
        # 而记事本存 UTF-8 会带 BOM —— 用 utf-8 读会把 BOM 当成正文打出来（一个乱码方块）。
        txt = open(p, encoding="utf-8-sig").read().strip()
    except OSError as e:
        return True, "（标志读不出来：%s）" % e, 0.0
    try:
        age = time.time() - os.path.getmtime(p)
    except OSError:
        age = 0.0
    return True, txt, age


LICENSE_DONE_HINT = ("     许可恢复后**不用改脚本**：直接重跑 host 即可"
                     "（会话就绪时会自动清掉这个标志）。")


def _license_hint() -> str:
    return ("★ 这是**授权/许可**问题，不是模型或脚本的问题。请人工处理，例如：\n"
            "     · 连接/重连公司 VPN（网络许可服务器常在 VPN 内网）\n"
            "     · 确认许可服务器可达：lic.yjk.cn:8081\n"
            "     · 检查许可是否被占满（多开/残留会话会占名额）\n"
            "     · 确认本机 YJK 的授权配置（网络版服务器/授权码）没有被改动\n"
            "   处理完不用改脚本：工具会**继续等待**，通道一通就自动往下走。\n"
            "   若不想等，用 `--on-license fail` 让它立刻以退出码 %d 结束。"
            % LICENSE_EXIT_CODE)


def _boot_yjks_8x(ins: dict, workdir: str, wait_ipc: int = 150,
                  verbose: bool = True, invisible: bool = False):
    """8.x 启动路径：`initConfig(pid=-1)` → `RunYJK(exe)` → `initConfig(pid)`。

    与 6/7 的区别（实测 8.1）：8.x 不再存在 `Global\\ShareMemoryEvent` /
    `Global\\WaitResaultEvent`，通道由 `initConfig` 建立、由 `RunYJK` 拉起进程，
    所以 6/7 的"等命名事件"判就绪在 8.x 上会一直等到超时（必须单独走这里）。
    """
    try:
        cli = Client()
    except Exception as e:                                     # noqa: BLE001
        log("!! 8.x 控制 DLL 不可用：%s" % e)
        return None, False
    if not getattr(cli, "has_init_config", False):
        log("!! 该 DLL 无 initConfig，无法按 8.x 官方流程启动")
        return None, False
    ver = P.version_xyz(ins["version"]) or "8.0.0"
    r0 = cli.configure(ver, invisible=invisible, pid=-1)
    if verbose:
        log("  initConfig(%s, Invisible=%s, Pid=-1) -> %s" % (ver, invisible, r0))
    if isinstance(r0, str) and (r0.startswith("异常") or r0.startswith("SKIP")):
        return None, False
    r1 = cli.run_yjk(ins["exe"])
    if verbose:
        log("  RunYJK(%s) -> %s" % (ins["exe"], r1))
    if isinstance(r1, str) and (r1.startswith("异常") or r1.startswith("SKIP")):
        return None, False
    t0 = time.time()
    pid = None
    while time.time() - t0 < wait_ipc:
        ps = yjks_pids()
        if ps:
            pid = ps[0]
            break
        time.sleep(1)
    if not pid:
        log("!! %.0fs 内 RunYJK 没有拉起 yjks（多为授权/许可问题；也见 `_yjk_license.need_user`）"
            % wait_ipc)
        return None, False
    time.sleep(1)
    r2 = cli.configure(ver, invisible=invisible, pid=pid)
    if verbose:
        log("  initConfig 绑定 Pid=%s -> %s（8.x 通道就绪，无需 yjksipccontrol）" % (pid, r2))
    bad = isinstance(r2, str) and (r2.startswith("异常") or r2.startswith("SKIP"))
    return pid, not bad


def boot_yjks(workdir: str, wait_ipc: int = 150, verbose: bool = True,
              on_license: str = "pause", license_timeout: int = 1800,
              invisible: bool = False):
    """无参启动 yjks（欢迎页），等 IPC 通道自动就绪。返回 (pid, ok)。

    授权/许可问题的处理（`on_license`）
    ----------------------------------
    * `pause`（默认）：一旦看门狗看到**授权类对话框**，就打印醒目提示、
      在工作目录写 `_yjk_license.need_user` 标志，然后**继续等**
      （最多 `license_timeout` 秒）。用户把许可修好之后 YJK 不再弹框、通道随即就绪，
      流程**自动继续** —— 不需要重跑、不需要改任何东西。
    * `fail`：立刻以失败返回，由上层以退出码 6 收尾（供无人值守的编排快速失败）。
    """
    ins = rt_yjk()
    if not ins["exe"]:
        log("!! 未探测到 yjks.exe。请设置环境变量 YJK_DIR 指向 YJK 安装目录，"
            "或先手动打开一次 YJK（运行中的进程是最好的线索）。")
        return None, False
    if verbose:
        log("YJK 安装=%s（来源：%s，版本 %s）" % (ins["root"], ins["source"], ins["version"]))
    major = P.version_major(ins["version"]) or P.version_major(ins["root"])
    if (major or 0) >= 8:
        return _boot_yjks_8x(ins, workdir, wait_ipc=wait_ipc,
                             verbose=verbose, invisible=invisible)
    ok_flag, cfgp = P.config_flag_ok()
    if not ok_flag:
        if verbose:
            log("!! 警告：所有 Config.ini 的 [YJKSControl] Flag 都不是 True —— "
                "IPC 通道不会自动开启。执行 `python yjk_probe.py --fix-config` 可自动补上。")
    if verbose:
        log("启动 yjks.exe（无参，CWD=%s）" % workdir)
    spawn(ins["exe"], workdir)
    t0 = time.time()
    pid = None
    while time.time() - t0 < 90:
        ps = yjks_pids()
        if ps:
            pid = ps[0]
            break
        time.sleep(2)
    if not pid:
        if verbose:
            log("!! yjks 未启动")
        return None, False
    if verbose:
        log("yjks pid=%s，等待 IPC 通道 ..." % pid)
    warned_at = None
    pause_t0 = None
    while True:
        now = time.time()
        # 正常上限还是 wait_ipc；**只有在真的进入授权暂停之后**才把窗口延到
        # pause_t0 + license_timeout（不能无条件延长，否则没有授权问题时也会白等
        # wait_ipc + license_timeout）。
        limit = t0 + wait_ipc
        if pause_t0 is not None:
            limit = max(limit, pause_t0 + license_timeout)
        if now >= limit:
            break
        # 必须判"长度够 + 全为真"：`events_alive()` 正常返回两个布尔，
        #   但 `all([])` 是 **True** —— 万一它将来返回空列表（比如事件名改了、
        #   被裁剪成一个循环），`all(...)` 会让 boot **在通道根本没起来时报成功**。
        _ev = events_alive()
        if len(_ev) >= 2 and all(_ev):
            if verbose:
                log("IPC 通道就绪（%.0fs，Flag=True 自动开启，无需键入 yjksipccontrol）"
                    % (time.time() - t0))
            try:
                os.remove(license_marker(workdir))
            except OSError:
                pass
            if pause_t0 is not None:
                # 这里**只能写 cp936 能编码的字符**：本函数会被当库调用
                #   （selfcheck 直接 import yjk_auto），而库不做 _utf8_console 兜底。
                #   我刚才在这里写了 `✓`（U+2713）→ 默认 GBK 下 log() 直接崩，
                #   正是上一轮修掉的那类缺陷，自己又犯了一次。
                log("   [OK] 授权已恢复，继续执行（此前暂停了 %.0fs）" % (time.time() - pause_t0))
            return pid, True
        if pid not in yjks_pids():
            if verbose:
                log("!! yjks 在 %.0fs 退出" % (time.time() - t0))
            return pid, False
        # ---- 授权类对话框：暂停并提示用户，**不替用户应答**
        lic = dlgwatch_license()
        if lic and pause_t0 is None:
            pause_t0 = time.time()
            _LICENSE_BLOCKED.append(lic[0][1][:200] or lic[0][0])
            log("")
            log("=" * 78)
            log("★ 检测到 YJK **授权/许可**对话框，已暂停等待人工处理：")
            log("    %s | %s" % (lic[0][0][:40], lic[0][1][:120]))
            log(_license_hint())
            log("  （看门狗**不会**替你对授权框点「是」——盲答会把 YJK 引导到"
                "「单机码激活」，然后无限循环）")
            log("=" * 78)
            log("")
            try:
                with open(license_marker(workdir), "w", encoding="utf-8") as f:
                    f.write("%s\n%s\n%s\n"
                            % (time.strftime("%Y-%m-%d %H:%M:%S"), lic[0][0], lic[0][1]))
            except OSError:
                pass
            if on_license == "fail":
                log("!! --on-license fail：不等待，直接以退出码 %d 结束" % LICENSE_EXIT_CODE)
                return pid, False
        if pause_t0 is not None:
            el = time.time() - pause_t0
            if warned_at is None or time.time() - warned_at > 60:
                warned_at = time.time()
                log("  [授权暂停中 %.0fs] 仍在等许可恢复；处理完会自动继续"
                    "（上限 %ds）" % (el, license_timeout))
            if el > license_timeout:
                log("!! 授权暂停已超过 %ds，放弃等待" % license_timeout)
                return pid, False
        time.sleep(2)
    if verbose:
        if pause_t0 is not None:
            log("!! 授权**始终没有恢复**（暂停等待了 %.0fs），放弃；这不是模型/脚本的问题"
                % (time.time() - pause_t0))
            log(_license_hint())
        else:
            log("!! %.0fs 内 IPC 未就绪；可能是 Flag 未设、或 YJK 弹了提示/更新对话框"
                % wait_ipc)
    return pid, False


def title_to_proj(title: str):
    """从窗口标题取工程全路径；**欢迎页/非路径标题一律返回 None**。

    标题格式：`<工程全路径> - 盈建科软件` / 欢迎页 `盈建科软件`。
    必须判"像不像绝对路径"：欢迎页标题没有分隔符，若直接按分隔符切，
      会把 `盈建科软件` 当成一个相对路径返回（相对谁？），
      进而让 kill_own 的安全闸把自己的欢迎页实例误判成"打开着别处工程"而拒绝清理，
      结果残留实例 + 下次再起一个 —— 正好制造出要避免的多实例。
    """
    if not title or " - " not in title:
        return None
    head = title.split(" - ", 1)[0].strip()
    if not head:
        return None
    return head if (":\\" in head or head.startswith("\\\\")) else None


def project_open(name: str, workdir: str) -> bool:
    """本实例是否**真的**打开了 `<workdir>\\<name>.yjk`（按窗口标题判断，不靠文件是否存在）。"""
    want = os.path.normcase(os.path.join(os.path.abspath(workdir), name + ".yjk"))
    for p in yjks_pids():
        for t in titles(p):
            path = title_to_proj(t)
            if path and os.path.normcase(os.path.abspath(path)) == want:
                return True
    return False


def open_project_dirs(pids=None) -> list:
    """本机 yjks 窗口标题里带的工程 → [(pid, 工程全路径, 工程所在目录)]。

    标题格式 `<工程全路径> - 盈建科软件`；欢迎页/无路径标题被 `title_to_proj` 过滤掉
    （它判"像不像绝对路径"，避免把 `盈建科软件` 当成相对路径）。
    """
    out = []
    for p in (list(pids) if pids is not None else yjks_pids()):
        for t in titles(p):
            path = title_to_proj(t)
            if path:
                out.append((p, path, os.path.dirname(os.path.abspath(path))))
                break
    return out


def project_dir_mismatch(workdir: str, pids=None):
    """「会话监视的目录」与「YJK 里真正打开的那个工程所在目录」是否一致。

    为什么必须有（现场）：常驻收件箱盯的是 `--dir`，但"当前打开哪个工程"是 YJK 自己的
    状态。有人用 `UINew` 在**别的目录**开了第二个工程，于是 `yjk_importydb` 返回
    `OK(6.4s)`（它确实成功了，只是成功在**另一个目录**），而文件变更闸门盯着 `--dir`
    什么都没看到 → 报成"导入没生效"并**跳过本轮剩余 11 条命令**。排查很久，因为提示
    指向导入，而不是指向目录错配。

    返回 `(pid, 工程全路径, 目录)`；一致、或读不到任何工程路径（欢迎页/标题暂不可读）时
    返回 None —— **读不到就不猜**，交给后面的文件变更闸门兜底。
    """
    want = os.path.normcase(os.path.abspath(workdir))
    for pid, path, d in open_project_dirs(pids):
        if os.path.normcase(os.path.abspath(d)) != want:
            return (pid, path, d)
    return None


def print_dir_mismatch(workdir: str, hit) -> None:
    """把"会话盯 A、YJK 开着 B"这件事说清楚，并给出可照做的处置（不静默降级）。"""
    pid, path, d = hit
    log("=" * 68)
    log("!! 会话目录与 YJK 打开的工程目录**不一致** —— 本轮命令不可信，已停手")
    log("!!   会话监视的目录 (--dir): %s" % os.path.abspath(workdir))
    log("!!   YJK 实际打开的工程     : %s（pid=%s）" % (path, pid))
    log("!!   工程所在目录            : %s" % d)
    log("!! 后果：命令确实作用在那个工程上（返回值正常），但文件变更闸门只看 --dir，")
    log("!!       于是「没有文件变化」→ 被判成「导入没生效」并跳过本轮剩余命令。")
    log("!! 处置（二选一，别续用这个会话）：")
    log("!!   ① 结束本会话（收件箱发 exit），改到工程自己的目录重开：")
    log("!!        host --dir \"%s\" --name <工程名> ..." % d)
    log("!!   ② 或让 YJK 回到 --dir：在欢迎页用 UINew 建到 --dir（host 就是这么做的）")
    log("=" * 68)


# 非空 = 最近一次「该工程是否被别的实例打开」的探测**没跑成**（原因）。
# 为什么必须分开记：探测失败时下面的函数只能返回 None，而 None 与"探测成功、且没有别的
# 实例打开它"**同形**。老版因此 fail-open（按「未打开」继续），随后还打印
# 「确认没有另一个实例打开它（已查：无）」—— 断言了一个**从未运行过**的检查。
# 这条检查要防的是：UINew 覆盖一个正被别的实例打开着的工程 = 两实例同抢一个库，
# 或在 YJK 打开它时从外部改库 → yjks 崩溃。
_HELD_PROBE_ERR = []


def _project_held_by_other(workdir: str):
    """该目录里的工程是否**正被某个实例打开**；返回 {"pid","title"} 或 None。

    `--reuse` 真正要防的危险不是"文件存在"，而是"这个工程正被另一个实例打开"：
    两实例同抢一个库、且在 YJK 打开它时从外部重建它 = 界面/库不一致甚至崩溃。
    这个判断不用另写 —— `env.py` 已经有它（`detect_open_project` /
    `project_is_open`），这里只是复用（放在函数里延迟导入，免得拖慢启动）。

    返回 None **有两种含义**：探测跑成了且没人打开；探测没跑成。后者会把原因记进
    `_HELD_PROBE_ERR`，调用方（`open_new_project`）据此 **fail-closed**（拒绝复用），
    不能当成"没打开"。
    """
    del _HELD_PROBE_ERR[:]
    try:
        import env as E                     # 同目录（sys.path 已在模块顶部插好）
        opened = E.detect_open_project()
        if getattr(E, "WIN_PROBE_ERR", []):
            # 窗口枚举本身不可用（例如 yjkw 导入失败）：`opened` 恒为空，
            # 那种"空"不是"没有实例在开工程"，必须当成探测失败。
            raise RuntimeError("窗口探测不可用：%s" % E.WIN_PROBE_ERR[0])
        hit = E.project_is_open(workdir, opened)
    except Exception as e:                                     # noqa: BLE001
        _HELD_PROBE_ERR.append(repr(e))
        log("   （--reuse 的「是否被别的实例打开」探测**不可用**：%r）" % e)
        return None
    if not hit:
        return None
    title = hit.get("title") or ""
    return {"pid": hit.get("pid"), "title": title}


def open_new_project(cli: Client, proj_yjk: str, workdir: str, verbose=True,
                     reuse=False):
    """UINew 在指定路径新建工程（UINew 认路径；UIOpen 不认）。

    只有"本实例确实已打开该工程"才跳过 UINew。**不能只看文件在不在**：
      yjks 每次都是新进程、停在欢迎页，此时文件存在 ≠ 工程已打开；
      若照旧跳过 UINew，后续命令会在"无工程"状态全部退化成 0.0s 秒回，
      而结果目录里还留着上一次的旧文件 —— 极易被误读成本轮结果。

    `reuse=True`（`--reuse`）显式允许**复用**目录里已存在的 `<工程名>.yjk`：
      没有它时上面那条安全规则会拒绝开工（防覆盖模型、防误读陈旧结果），
      实测代价是迭代活动被迫为每轮新建目录（YJK_run / YJK_base / YJK_run2…）。
      开了它必须**如实**说清"找到已有工程、将被打开/覆盖"，并检查该工程
      是否正被**另一个实例**打开 —— 那才是原规则真正要防的危险（`env.py` 能判）。
    """
    proj_yjk = os.path.normpath(proj_yjk)
    name = os.path.splitext(os.path.basename(proj_yjk))[0]
    if project_open(name, workdir):
        if verbose:
            log("工程已在本次实例中打开: %s（跳过 UINew）" % proj_yjk)
        return True
    if os.path.exists(proj_yjk):
        if not reuse:
            if verbose:
                cur = titles(yjks_pids()[0]) if yjks_pids() else None
                log("!! 工作目录里已有 %s，但本实例并没有打开它（当前窗口标题=%s）"
                    % (os.path.basename(proj_yjk), cur))
                log("   在这里直接 UINew 会**覆盖**已有模型；而带文档启动无法建立 IPC 通道（硬性约束 1）。")
                log("   处置：换一个干净的工作目录重跑；做迭代请用常驻实例的 `send @recalc`，"
                    "不要重跑 host。")
                log("   （确实要复用这个目录就加 `--reuse`：会明说「打开/覆盖已有工程」，"
                    "并先检查它有没有正被别的实例打开）")
            return False
        # ---- --reuse：先查"正被别的实例打开"这个真危险，再明说会被打开/覆盖 ----
        held = _project_held_by_other(workdir)
        if held is None and _HELD_PROBE_ERR:
            # 探测没跑成 → **不能**当成"没打开"（老版就是这么 fail-open 的）。
            if verbose:
                log("!! --reuse 检查**无法完成**（探测不可用：%s）—— 保守处理：拒绝开工"
                    % _HELD_PROBE_ERR[0])
                log("   要防的是「UINew 覆盖一个正被别的实例打开着的工程」：两实例同抢一个库，")
                log("   或在 YJK 打开它时从外部改库 → yjks 崩溃。探测不可用时不能当作「没打开」。")
                log("   处置：先 `yjk_auto.py status` 确认没有别的实例在用这个工程；"
                    "或换一个干净的工作目录重跑。本次未做任何操作。")
            return False
        if held:
            if verbose:
                log("!! --reuse 检查未通过：该工程**正被另一个实例打开**（pid=%s 标题=%s）"
                    % (held["pid"], held["title"][:70]))
                log("   此时再 UINew 打开/覆盖同一个工程 = 两实例同抢一个库；")
                log("   且 YJK 正打开某工程时从外部改它的库会导致 yjks 崩溃。")
                log("   处置：先关掉那个实例（`yjk_auto.py status` 看 pid → "
                    "`close --pid <PID> --yes`），或换个 --name。本次未做任何操作。")
            return False
        if verbose:
            log("--reuse：工作目录里已有 %s —— 将**打开/覆盖**这个已有工程"
                % os.path.basename(proj_yjk))
            log("   现有文件: %s（%s，%d 字节）"
                % (proj_yjk, time.strftime("%Y-%m-%d %H:%M:%S",
                                           time.localtime(os.path.getmtime(proj_yjk))),
                   _file_size(proj_yjk) or 0))
            log("   ★ 这一步之后该工程会被 UINew 重新建/打开，旧模型与旧设计结果可能被覆盖；")
            # 这句话现在只在"探测真的跑过、且没人打开"时才会打印（探测没跑成就已 fail-closed 拒绝）。
            log("     确认没有另一个实例打开它（已查：无）。")
    if verbose:
        log("UINew -> %s" % proj_yjk)
    r = cli.run("UINew", proj_yjk, 200)
    if verbose:
        log("  %s" % r)
    t0 = time.time()
    while time.time() - t0 < 90:
        ps = yjks_pids()
        if ps and any(name in t for t in titles(ps[0])):
            if verbose:
                log("  工程已建立（%.0fs）标题=%s" % (time.time() - t0, titles(ps[0])))
            return True
        time.sleep(3)
    if verbose:
        log("  未确认工程窗口，标题=%s" % (titles(yjks_pids()[0]) if yjks_pids() else None))
    return False


# ---------------------------------------------------------------- 导入校验闸门
# host 的失败台账：**只要非空，host 就以非零退出码收尾**。
# 为什么必须这样：导入空模型时 yjk_importydb 返回 OK、预处理/计算也照跑，
# 自动化调用方（如 floor-system-comparison/run_all_yjk.py 会看 host 的 rc）只看
# 返回值 + 退出码，不给出非零码它就当成功。
_HOST_ERRORS = []

# 「**无法判定**」台账：不是"确认为失败"，而是"关键证据拿不到，这一轮不能当成功"。
# 当前唯一来源：模态框看门狗没起来 → "没有错误弹框"这句话不成立（审计 S23）。
# 与 _HOST_ERRORS 分开，是为了让编排能区分"确知失败(2)"与"无法判定(5)"。
_HOST_UNVERIFIED = []


def host_fail(why: str) -> None:
    """登记一条"本轮确实失败"的理由（收尾时据此给非零退出码 2）。"""
    _HOST_ERRORS.append(why)


def host_unverified(why: str) -> None:
    """登记一条"本轮无法判定"的理由（收尾时据此给退出码 %d）。"""
    _HOST_UNVERIFIED.append(why)


def verify_import(ydb: str, workdir: str, name: str | None = None,
                  verbose: bool = True) -> bool:
    """逐表核对导入是否真的生效（判据见 `impcheck.py`）。返回是否通过。

    只用几何表行数判定：`tblJoint/tblColSeg/tblBeamSeg/tblWallSeg/tblFloor/tblStdFlr`
    必须逐表相等；`tblSlab`（save 会拆/补板，实测 336→364）、`tblAxis`（合并共线轴）、
    `tblProperty/tblProjectPara`（save 展开参数表）**本来就会变**，只打印不判死 ——
    把这几张当"必须相等"会把一对完全正确的导入判成失败。
    """
    try:
        if name:                                   # host：工程名已知，直接点 `<工程名>.ymd`
            ymd = os.path.join(workdir, name + ".ymd")
            ok, _rep = IC.check(os.path.abspath(ydb), ymd,
                                verbose=verbose, strict=False)
        else:                                      # 收件箱：没有 --name，靠库结构认模型库
            ok, _rep = IC.check_dir(os.path.abspath(ydb), workdir,
                                    verbose=verbose, strict=False)
    except Exception as e:                                     # noqa: BLE001
        log("!! 导入校验无法执行（%r）—— 当成**未通过**处理（宁可停手，不能默认成功）" % e)
        return False
    if ok:
        log("  ★ 导入校验通过（逐表核对：几何表与源 .ydb 一致）")
    else:
        log("  ★ 导入校验 ★不通过★ —— 见上面的表；这不是「再等等」能好的问题")
    return ok


# ---------------------------------------------------------------- 收件箱
def inbox_paths(workdir: str):
    return (os.path.join(workdir, "_yjk_inbox.txt"),
            os.path.join(workdir, "_yjk_outbox.txt"))


def ready_path(workdir: str):
    """「收件箱正在服务」的标志文件（host 打开收件箱时写、收尾时删）。"""
    return os.path.join(workdir, "_yjk_inbox.ready")


# 就绪标志的**心跳**容忍时间（秒）。`watch_inbox` 的轮询是 2s 一轮，
# 这里给足余量（用户把机器忙住/断点调试也不至于误判），但必须远小于"一整轮迭代"的量级。
READY_STALE = 120.0


def session_ready(workdir: str):
    """该目录是否有**正在服务**的收件箱会话。返回 `(ok, why)`。

    为什么不能只看文件是否存在（缺陷 L2 / 审计 S10）
    ------------------------------------------------
    `send` 以前只做 `os.path.exists(ready)`，而 ready 文件是**会残留的**：
    host 被硬杀（taskkill / 断电 / 我们自己 human_kill）时 `finally` 不执行，
    文件就留在那里。于是：

        send  →  rc=0，命令**写进了收件箱**，但**没有任何进程在读它**
              →  命令石沉大海，调用方以为发出去了

    实测对照（案例 G03）：目录里**没有** ready → `send` rc=2 明确拒绝且不写入；
    放一个**陈旧** ready → `send` rc=0 且写入、永远无人执行。
    后者是最危险的形态：静默丢弃。

    判据（**全部失败都判「未就绪」，fail-closed**）：
      ① 文件读不出来 / 首字段不是数字 → 未就绪
      ② 里面记的 host PID 不是活着的 python 系进程 → 未就绪（残留）
      ③ 心跳太旧（`mtime` 超过 `READY_STALE` 秒没更新）→ 未就绪（会话卡死/已死）
      ④ 文件新鲜 → 就绪

    心跳由 `watch_inbox` 的轮询循环每轮 `os.utime` 续写；它还能覆盖 PID 校验
    **查不出**的一类：宿主还活着、但收件箱循环已经退出（卡在别处）。
    """
    p = ready_path(workdir)
    if not os.path.exists(p):
        return False, "没有就绪标志（%s 不存在）：会话还没打开收件箱，或已正常收尾" % (
            os.path.basename(p))
    try:
        with open(p, encoding="utf-8") as f:
            first = (f.read().split() or [""])[0]
    except OSError as e:
        return False, "就绪标志读不出来（%s）" % e
    if not first.isdigit():
        return False, ("就绪标志内容不合法（首字段 %r 不是 PID）—— 像是被人工改过或写坏了"
                       % first[:20])
    pid = int(first)
    if not host_alive(pid):
        return False, ("%s 里记的 host PID=%d **已经不是活着的本包宿主进程** —— "
                       "这是上次会话崩溃/被杀留下的**残留**标志" % (os.path.basename(p), pid))
    try:
        age = time.time() - os.path.getmtime(p)
    except OSError:
        age = 0.0
    if age > READY_STALE:
        return False, ("就绪标志 **%.0f 秒**没有心跳（>%.0f）—— 宿主进程还在，"
                       "但收件箱循环多半已经卡住或退出" % (age, READY_STALE))
    return True, "会话在服务（host pid=%d，心跳 %.0fs 前）" % (pid, age)


# ---------------------------------------------------------------- 收件箱宏
# 迭代闭环要反复发同一串命令，逐条 send 很容易漏；这里把常用序列包成 @ 宏：
#   @back    回到「构件布置（建模调整界面）」——注意计算链最后停在设计结果标签，
#            要改模型必须先切回来（yjk_importydb / yjk_repair 等属建模模块命令）
#   @prep    预处理链（工程修复 → 保存 → 形成节点 → 形成楼板）
#   @calc    官方计算链（含切到「前处理及计算」与算完切到「设计结果」）
#   @recalc  一整轮迭代：@back → [导入新 ydb（给参数时）] → @prep → @calc
#   @takeoff 算量链：混凝土统计 → 施工图 → 钢筋统计（顺序固定，见 TAKEOFF_CHAIN 注释）
MACROS = {
    "back": [("SetCurrentLabel", "IDModule_Element")],
    "prep": list(PREP_CHAIN),
    "calc": list(CALC_CHAIN),
    "takeoff": list(TAKEOFF_CHAIN),
}
MACRO_HELP = ("@back / @prep / @calc / @recalc [新模型.ydb] / "
              "@takeoff（混凝土统计→施工图→钢筋统计，顺序固定）")


def expand(cmd: str, param: str = "") -> list:
    """把 @宏 展开成 [(命令, 参数), …]；非宏命令原样返回一条。"""
    if not cmd.startswith("@"):
        return [(cmd, param)]
    name = cmd[1:].lower()
    if name == "recalc":
        # 迭代轮：回建模 → 导入新 ydb → 预处理 → **不算完切结果标签的计算链**（省 15.7s/轮）
        seq = [("SetCurrentLabel", "IDModule_Element")]
        if param:
            seq.append(("yjk_importydb", param))
        return seq + list(PREP_CHAIN) + list(CALC_CHAIN_CORE)
    if name not in MACROS:
        raise SystemExit("未知宏 %s（可用：%s）" % (cmd, MACRO_HELP))
    return list(MACROS[name])


def send_to_inbox(cmd: str, param: str = "", workdir: str | None = None) -> str:
    workdir = workdir or os.getcwd()
    inbox, _ = inbox_paths(workdir)
    seq = expand(cmd, param)
    with open(inbox, "a", encoding="utf-8") as f:
        for c, p in seq:
            f.write("%s|%s|%s\n" % (time.strftime("%H%M%S"), c, p))
    return inbox


def inbox_precheck(cmd: str, param: str):
    """发命令前的校验 → (ok, 原因)。现在只覆盖"要导入的 ydb 在不在"。

    为什么要它：`yjk_importydb` 参数写错时返回值照样可能是 OK，
    而后续的预处理+计算会拿**旧模型**算一轮 —— 结果看起来完全正常，实则跑错了对象。
    """
    if cmd == "yjk_importydb":
        if not param:
            return False, "yjk_importydb 没有给参数（应为 .ydb 路径）"
        if not os.path.exists(param):
            return False, "要导入的 ydb 不存在: %s" % param
    return True, ""


def _skipped_note(n: int) -> None:
    """把"跳过 = 永久消费"讲清楚。

    闸门拦住的这一批命令会被循环末尾的 `done = len(lines)` 标成已消费（这是**有意**的：
    会话要继续，不能因为一条坏命令就反复重放整批）。但那意味着**修正之后不会自动重放**，
    必须重发 —— 只说"已跳过"容易被读成"等一下就会再试一次"（审计 S31）。跳过的
    每一条都已逐条写进 outbox（带原因），可据此核对。
    """
    if n <= 0:
        return
    log("   注：被跳过的这 %d 条**不会自动重放**（本轮已消费，逐条记在 outbox 里）；"
        "修正后请重发。" % n)


def watch_inbox(cli: Client, workdir: str, stop_after: int | None,
                poll: float = 2.0, own=None, idle_exit: int = 0) -> None:
    inbox, outbox = inbox_paths(workdir)
    # 归档历史收件箱：send 是"追加写"，若不归档，上一轮留下的命令会在本次会话被逐条重放
    #   （风险：连跑几轮迭代会攒下几十行，重启后会把它们当新命令逐条重放一遍）
    rdy = ready_path(workdir)
    if os.path.exists(rdy):
        try:
            os.remove(rdy)                     # 本会话还没就绪前，先让 send 拒绝
        except OSError:
            pass
    if os.path.exists(inbox) and os.path.getsize(inbox) > 0:
        bak = "%s.%s.bak" % (inbox, time.strftime("%Y%m%d_%H%M%S"))
        try:
            os.replace(inbox, bak)
            log("收件箱里有历史命令，已归档 -> %s（避免重放上一轮）" % os.path.basename(bak))
        except OSError as e:                                   # noqa: BLE001
            log("!! 归档历史收件箱失败: %s（继续，但历史命令可能被重放）" % e)
    open(inbox, "a", encoding="utf-8").close()
    with open(rdy, "w", encoding="utf-8") as f:        # ★ 就绪标志：此后 send 才放行
        f.write("%s %s\n" % (os.getpid(), time.strftime("%Y-%m-%d %H:%M:%S")))
    done = 0
    log("收件箱已开启: %s（结果 -> %s）" % (inbox, os.path.basename(outbox)))
    log("  实例隔离：每条命令执行前校验「自有实例 %s 存活 且 无其它实例」" % own)
    if idle_exit:
        log("  空闲 %ds 无新命令将自动收尾（--exit-when-idle，0 表示一直等）" % idle_exit)
    t0 = last_active = last_beat = time.time()
    # 跨批次记住"导入了哪个 .ydb"：@recalc 的导入与 `yjk_save` 同批，
    # 但单独发 `yjk_importydb` 再发 `yjk_save` 时它们是两批，所以状态放在循环外。
    pending_ydb = None

    def inst_alive() -> bool:
        """目标实例还活着吗（缺陷 L5：实例没了就不要再等结果）。

        用 `yjks_pids()`（psapi 枚举，几毫秒）而不是 `instances()`/`yjks_info()`
          —— 后者要起一次 PowerShell 查 WMI，放进"每 2 秒轮询"里代价太大。
        已知边界：**0 线程的残壳**（`threads==0`，PID 还在）在 psapi 里仍看得见，
          会被当成"活着"，于是那一种情况下仍退回到 `timeout` 兜底（不会更差）；
          实测的硬杀场景（F01/F02）进程直接从进程表消失，这里能立刻发现。
        """
        if own:
            return own in yjks_pids()
        return bool(yjks_pids())

    while True:
        now = time.time()
        if stop_after and now - t0 > stop_after:
            log("已到 --stay 时限，退出收件箱循环")
            return
        if idle_exit and now - last_active > idle_exit:
            log("空闲 %.0fs 无新命令（--exit-when-idle %ds）→ 自动收尾，不再空等"
                % (now - last_active, idle_exit))
            return
        # 心跳：每轮续写 ready 的 mtime。`send` 侧据此判断会话是否还活着
        #   （只看"文件在不在"会把崩溃残留当成就绪 —— 缺陷 L2）。
        try:
            os.utime(rdy, None)
        except OSError:
            pass
        try:
            with open(inbox, "r", encoding="utf-8") as f:
                lines = [ln.rstrip("\n") for ln in f if ln.strip()]
        except OSError:
            lines = []
        if len(lines) > done:
            last_active = time.time()
            for ln in lines[done:]:
                parts = ln.split("|", 2)
                seq = parts[0].strip()
                cmd = parts[1].strip() if len(parts) > 1 else ""
                param = parts[2] if len(parts) > 2 else ""
                # 行格式校验：收件箱在模块 docstring 里是**公开的跨进程接口**
                #   （"其他进程往 _yjk_inbox.txt 追加 HHMMSS|命令|参数"），格式写错是预期内的事：
                #   别的进程少写一个 `|`、或崩溃在 f.write 中途留下半行。
                #   没有这道校验时 `cmd` 会是空串，而隔离闸门/前置校验都不拦空命令
                #   （它们只特判 yjk_importydb）→ 空命令被发给 YJK，还在 outbox 里
                #   记成一条"正常执行"的回执（变更=-），看起来像跑过了。
                #   这里**不执行**它，并把这件事写进 outbox 与失败台账。
                if not cmd:
                    log("!! 收件箱第 %d 行**格式非法**（应形如 HHMMSS|命令|参数，"
                        "行=%r）—— 不当成命令执行" % (done + 1, ln[:120]))
                    log("   空命令发下去只会得到一条假的「正常执行」回执；"
                        "请写命令的进程按格式重发。")
                    with open(outbox, "a", encoding="utf-8") as f:
                        f.write("%s|(格式非法)|收件箱行没有命令字段，已跳过未执行|变更=-\n"
                                % seq)
                    host_fail("收件箱有格式非法的行（没有 `|` 分隔的命令字段），已跳过未执行：%r"
                              % ln[:80])
                    continue
                # exit 先判：它只结束**我们自己的**会话，不需要通道可信，
                #   不能被隔离闸门一起拦掉（否则有外部实例时会话永远退不出，只能干等）
                if cmd.lower() in ("exit", "quit"):
                    log("收到退出指令（优先于隔离闸门处理）")
                    return
                ok, why = exclusive_ok(own)          # 每条命令前的隔离闸门
                if not ok:
                    log("!! %s" % why)
                    log("!! 本轮剩余 %d 条已跳过（**会话继续**，修正后可再发新命令；"
                        "未杀任何实例）" % (len(lines) - done))
                    _skipped_note(len(lines) - done)
                    with open(outbox, "a", encoding="utf-8") as f:
                        f.write("%s|%s|%s|变更=-\n" % (seq, cmd, why))
                    break
                pre_ok, why2 = inbox_precheck(cmd, param)   # 发命令前的前置校验
                if not pre_ok:
                    log("!! %s" % why2)
                    log("!! 本轮剩余 %d 条已跳过（**会话继续**；修正后可再发新命令）"
                        % (len(lines) - done))
                    _skipped_note(len(lines) - done)
                    with open(outbox, "a", encoding="utf-8") as f:
                        f.write("%s|%s|%s|变更=-\n" % (seq, cmd, why2))
                    break
                # 导入校验闸门**自触发**（缺陷 S11）
                #   老版只把待校验的 .ydb 记在 `pending_ydb` 里，**等 `yjk_save` 才核**。
                #   而 `CALC_CHAIN` 里没有 `yjk_save`：调用方若发
                #   `yjk_importydb x.ydb` 紧接 `@calc`，`pending_ydb` 永远不被消费 ——
                #   校验**静默地从未运行**，而文档却承诺"导入后自动跑，不通过就别往下算"。
                #   现在：只要下一条命令不是 `yjk_save`，就**先补一步保存再核**，
                #   校验不过照旧跳过本轮剩余命令（不拿空模型跑一整轮计算）。
                if pending_ydb and cmd != "yjk_save":
                    log("★ 检测到「已导入但链条里没有 yjk_save」→ 自动补一步保存并跑导入校验"
                        "（否则校验会**静默地从未运行**，缺陷 S11）")
                    rs = cli.run("yjk_save", "", 300, alive=inst_alive)
                    log("   自动 yjk_save -> %s" % rs)
                    with open(outbox, "a", encoding="utf-8") as f:
                        f.write("%s|yjk_save(自动补)|%s|变更=-\n" % (seq, rs))
                    if not verify_import(pending_ydb, workdir):
                        log("!! 导入校验不通过 → 本轮剩余 %d 条已跳过"
                            "（不拿空模型跑一整轮计算）" % (len(lines) - done - 1))
                        _skipped_note(len(lines) - done - 1)
                        with open(outbox, "a", encoding="utf-8") as f:
                            f.write("%s|%s|导入校验不通过|变更=-\n" % (seq, cmd))
                        pending_ydb = None
                        break
                    pending_ydb = None
                # 目录错配闸门：**在拿"有没有文件变化"当判据之前**先确认
                #   "YJK 里开着的是不是本目录的工程"。否则会像现场那样：
                #   命令其实成功在**另一个目录**，却因为 --dir 没变化被报成"导入没生效"。
                dm = project_dir_mismatch(workdir, [own] if own else None)
                if dm:
                    print_dir_mismatch(workdir, dm)
                    log("!! 本轮剩余 %d 条已跳过（**会话继续**；换到工程自己的目录重开会话）"
                        % (len(lines) - done))
                    _skipped_note(len(lines) - done)
                    with open(outbox, "a", encoding="utf-8") as f:
                        f.write("%s|%s|目录错配(会话 %s / 工程 %s)|变更=-\n"
                                % (seq, cmd, workdir, dm[2]))
                    break
                before = snap(workdir)
                r = cli.run(cmd, param, 900, alive=inst_alive)
                after = snap(workdir)
                # 实例在执行途中消失（被硬杀/崩了）：命令永远不会有结果。
                #   这里必须**立刻**结束本轮并回到收件箱循环 —— 否则 `exit` 也读不到，
                #   现场表现就是"不响应 exit，只能强制收尾"（缺陷 L5）。
                if r.startswith("实例已退出"):
                    log("!! 执行 %s 途中目标实例（yjks）已消失 → 放弃等结果" % cmd)
                    log("   已写入收件箱结果行；随后回到循环处理 exit/新命令")
                    with open(outbox, "a", encoding="utf-8") as f:
                        f.write("%s|%s|%s|变更=-\n" % (seq, cmd, r))
                    host_fail("执行 %s 途中 yjks 实例退出（被硬杀或自己崩了）：%s"
                              % (cmd, r))
                    log("!! 本轮剩余 %d 条已跳过（实例没了，后续命令没有意义）"
                        % (len(lines) - done - 1))
                    _skipped_note(len(lines) - done - 1)
                    break
                changed = [os.path.basename(k) for k in diff(before, after)]
                line = "%s|%s|%s|变更=%s" % (seq, cmd, r,
                                             ",".join(changed) if changed else "-")
                log("  执行 %s(%r) -> %s" % (cmd, param[:60], r))
                with open(outbox, "a", encoding="utf-8") as f:
                    f.write(line + "\n")
                # 导入类命令：没有任何文件变化 = 大概率没生效（返回值照样是 OK）
                if cmd in ("yjk_importydb",) and not changed:
                    dm2 = project_dir_mismatch(workdir, [own] if own else None)
                    if dm2:
                        # 现场的真因就是它：不是导入失败，是**目录错配**。
                        # 老代码在这里只喊"导入很可能没生效"，把排查带偏了。
                        print_dir_mismatch(workdir, dm2)
                        log("   （上面这条才是真因：导入确实生效了，只是生效在另一个工程里）")
                    else:
                        log("!! %s 返回 %s 但**没有任何文件变化** —— 导入很可能没生效" % (cmd, r))
                    log("!! 本轮剩余 %d 条已跳过（会话继续；修正后可再发新命令）"
                        % (len(lines) - done - 1))
                    _skipped_note(len(lines) - done - 1)
                    break
                if cmd == "yjk_importydb" and param:
                    pending_ydb = param            # 等下一步 yjk_save 写出 .ymd 后逐表核对
                elif cmd == "yjk_save" and pending_ydb:
                    # 导入校验闸门（必须排在 yjk_save 之后）：半写的 .ydb /
                    #   相对路径导入都会"成功"地导入空模型，若放它过去，
                    #   下一轮预处理+计算会在一整轮之后才报「模型中没有单元数据」。
                    if not verify_import(pending_ydb, workdir):
                        log("!! 导入校验不通过 → 本轮剩余 %d 条已跳过"
                            "（不拿空模型跑一整轮计算）" % (len(lines) - done - 1))
                        with open(outbox, "a", encoding="utf-8") as f:
                            f.write("%s|%s|导入校验不通过|变更=-\n" % (seq, cmd))
                        pending_ydb = None
                        break
                    pending_ydb = None
            done = len(lines)
            # 空闲从"这一批跑完"开始算，而不是"这批开始的时间"。
            #   否则一个 5 分钟的计算轮跑完，会立刻被算成"已空闲 5 分钟"而马上收尾。
            last_active = time.time()
        if not yjks_pids():
            log("!! yjks 已退出，收件箱循环结束")
            return
        if idle_exit and time.time() - last_beat > 60:
            last_beat = time.time()
            idle = time.time() - last_active
            log("  [空闲 %.0fs] 队列 %d 条；距自动收尾 %.0fs"
                % (idle, max(0, len(lines) - done), max(0, idle_exit - idle)))
        time.sleep(poll)


# ---------------------------------------------------------------- 子命令
def cmd_status(args) -> None:
    ins = rt_yjk()
    log("YJK 安装: %s（%s，版本 %s）" % (ins["root"], ins["source"], ins["version"]))
    log("yjk 相关进程:")
    for p, v in sorted(procs().items()):
        if "yjk" in v.lower():
            log("  pid=%-6d %s" % (p, v))
    yj = instances()
    log("yjks 实例数=%d %s" % (len(yj), [i["pid"] for i in yj]))
    if not yj:
        log("  （无实例；本工具会自建并登记一个自有实例）")
    for i in yj:
        log("  [%s] pid=%-6d %s" % (KIND_TAG.get(i["kind"], i["kind"]), i["pid"],
                                    window_text(i)))
        if i["cmdline"]:
            log("        命令行: %s" % i["cmdline"][:160])
        if i["proj"]:
            log("        打开工程: %s" % i["proj"])
    kinds = {i["kind"] for i in yj}
    if "foreign" in kinds:
        log("!! 有**你在用**的实例（有主窗口）——本工具一律不碰；开工会被拒绝。怎么关掉它：")
        for i in yj:
            if i["kind"] == "foreign":
                print_close_howto(i)
    if "orphan" in kinds:
        log("!! 有无主窗口残留（YJKAPI.init/WinExec 拉起）——默认不碰；"
            "要清需显式 `yjk_cleanup.py --apply` 或 host 加 `--clean-orphans`")
    if len(yj) > 1:
        log("!! 多实例会互相抢 Global 事件（应答来自错误实例）—— 硬性约束 3：全机只应有 1 个")
    es = events_alive()
    log("IPC 事件 %s = %s" % (EV_SHARE, es[0]))
    log("IPC 事件 %s = %s" % (EV_WAIT, es[1]))
    if (P.version_major(rt_yjk().get("version")) or 0) >= 8:
        log("  （8.x 不用这两个命名事件，通道由 initConfig 建立：上面 False 属正常）")
    dead = [i["pid"] for i in yj if i["kind"] == "dead"]
    if dead:
        log("  残壳 %s：0 线程（已终止待回收）→ 不阻断开工，也无法终止，重启即清" % dead)
    src = id_sources()
    if src["psapi漏掉"] or src["wmi看不到"]:
        log("  诊断：两个 PID 来源不一致 — psapi=%s / WMI=%s（已取并集）"
            % (src["psapi"], src["wmi"]))
        log("        psapi 漏掉 %s（QueryFullProcessImageNameW 失败时会静默丢）；"
            "WMI 看不到 %s" % (src["psapi漏掉"], src["wmi看不到"]))

    # ---- 授权暂停标志：这是「为什么没就绪」最需要人来处理的一类原因 ----------
    # 宿主进程里的 _LICENSE_BLOCKED 只在本进程内存里，别的会话看不到；
    #   标志文件是跨进程唯一的信道（见 license_state 的注释）。
    dirs = []
    if getattr(args, "dir", None):
        dirs.append(os.path.normpath(args.dir))
    wd = (_own_read() or {}).get("workdir") or ""
    if wd and wd not in dirs:
        dirs.append(wd)
    if not dirs:
        log("授权暂停标志：**未知工作目录**（own.json 里没有 workdir）；"
            "用 `status --dir <工作目录>` 指定即可查")
    for d in dirs:
        blk, txt, age = license_state(d)
        if blk:
            log("!! 授权暂停标志：%s" % license_marker(d))
            log("   （%.0f 秒前写入）%s" % (age, txt[:200] or "（标志内容为空）"))
            log("   → 上次会话在这里**等用户处理许可**；本工具不代答授权对话框。")
            log(LICENSE_DONE_HINT)
        else:
            log("授权暂停标志：无（%s）" % d)


def cmd_kill(_args) -> None:
    kill_all()


def cmd_close(args) -> None:
    """精确关掉**指定 PID** 的 yjks（人工确认用）。

    与 `kill`（无差别全清）的区别：这里必须点名 PID，且先把"关的是哪个、它开着什么"打出来；
    对**非自有**实例（你自己在用的）还要求加 `--yes` 才动手 —— 工具只在你明确允许后关它。
    """
    try:
        pid = int(args.pid)
    except (TypeError, ValueError):
        log("!! --pid 需要整数（用 yjk_auto.py status 看 PID）")
        raise SystemExit(2)
    hit = [i for i in instances() if i["pid"] == pid]
    if not hit:
        log("找不到 pid=%s 的 yjks 实例（可能已经退出了）" % pid)
        return
    i = hit[0]
    if i["kind"] == "dead":
        log("pid=%s 是**已终止的残壳**（0 线程/无窗口）：它不能再执行任何代码，也不抢事件；" % pid)
        log("  且对它的 TerminateProcess/taskkill 一律返回 Access denied（管理员也一样）。")
        log("  无需也无法结束它 —— 重启即清，或等系统回收。**本工具不做无谓的尝试。**")
        return
    log("待关闭的实例：")
    print_close_howto(i)
    if i["kind"] == "own":
        log("  这是本工具的**自有**实例 → 直接清理")
        kill_own()                                   # 登记里已指向它，无需重新登记
        return
    if not args.yes:
        log("!! 这是**你自己的**实例：关它会中断该会话（未保存内容会丢）。")
        log("   确认要关就加 --yes 再跑一次：")
        log("     %s" % close_hint(pid))
        return
    ok = kill_pid(pid, verbose=True)
    if not ok:
        log("!! 结束请求被拒（见上面的 err）。常见原因：")
        log("     · 该实例权限更高（例如以**管理员**身份启动）→ 请用管理员权限运行本命令，")
        log("       或直接在那个 YJK 窗口里关闭；")
        log("     · 被安全软件拦截。")
        log("   本次**没有**关掉它：%s" % describe(instances()))
        return
    left = wait_gone([pid], timeout=10)
    if left:
        log("!! 终止请求已发出，但 pid=%s 仍在（%s）—— 按上面两条排查" % (left, describe(instances())))
    else:
        log("已确认关闭 pid=%s（剩余实例：%s）" % (pid, describe(instances())))


def cmd_send(args) -> None:
    workdir = os.path.normpath(args.dir or os.getcwd())
    ok, why = session_ready(workdir)
    if not ok:
        log("!! 该目录没有**正在服务**的收件箱会话，本次**没有写入**（否则命令会被启动归档丢掉）。")
        log("   具体原因：%s" % why)
        # 先判「是不是授权暂停」：这是最需要**人来处理**的一类原因，
        #   而调用方（另一个 agent / 用户）光看「未就绪」是猜不出来的。
        blk, txt, age = license_state(workdir)
        if blk:
            log("   ★★ 该目录上次是**因授权/许可问题暂停**的"
                "（标志 %s，%.0f 秒前写入）：" % (os.path.basename(license_marker(workdir)), age))
            if txt:
                log("       当时对话框内容：%s" % txt[:200])
            log("       请**用户**先处理许可（VPN / lic.yjk.cn:8081 可达 / 许可名额有没有被占满 / "
                "网络版服务器配置），再继续 —— 本工具**不代答**授权对话框。")
            log(LICENSE_DONE_HINT)
            raise SystemExit(2)
        log("   收件箱要等 host 走完「启动→建工程→导入→预处理」才打开（约 60s）。请：")
        log("     1) 先启动： host --dir \"%s\" --name <工程名> --inbox" % workdir)
        log("     2) 等日志出现「收件箱已开启」，再 send")
        if "残留" in why:
            log("   ★ 若是上次会话**崩溃/被杀**留下的残留标志：直接重跑一次 host 即可"
                "（会话开始时会把旧收件箱归档、并重写就绪标志）。")
        raise SystemExit(2)
    seq = expand(args.cmd, args.param or "")
    p = send_to_inbox(args.cmd, args.param or "", args.dir)
    if len(seq) > 1:
        log("宏 %s 展开为 %d 条 -> %s" % (args.cmd, len(seq), p))
        for c, pa in seq:
            log("    %s(%s)" % (c, pa))
    else:
        log("已追加 1 条到收件箱 %s" % p)


def cmd_probe(args) -> None:
    import yjk_probe
    yjk_probe.main(["--fix-config"] if args.fix_config else [])


def cmd_host(args) -> None:
    """host 入口：先做实例隔离预检，再跑主流程；收尾只清**自有**实例。

    策略见「实例隔离」一节：命令无法定向到 PID，所以**不共处**——
    发现你在用的实例就拒绝；发现无主窗口残留就提供显式清理开关。全程不碰非自有实例。

    收尾时若失败台账非空（如导入校验不通过），**以非零退出码结束**：
    否则"导入空模型 + 白算一轮"在自动化调用方眼里和成功没有区别
    （`run_all_yjk.py` 这类调用方就是拿 host 的 rc 当判据的）。
    若只是"关键证据拿不到"（模态框看门狗没起来 → 无法确认有没有错误弹框），
    则以退出码 5（`UNVERIFIED_EXIT_CODE`）结束（见 `_HOST_UNVERIFIED`）。
    """
    workdir = os.path.normpath(args.dir)
    os.makedirs(workdir, exist_ok=True)
    attach_pid = getattr(args, "pid", None)
    if attach_pid:
        log("=== 0) attach 模式：只接管 pid=%s（不杀、不启动、不登记自有实例）===" % attach_pid)
        if int(attach_pid) not in yjks_pids():
            log("!! 目标 pid=%s 不是正在运行的 yjks（现有：%s）" % (attach_pid, yjks_pids()))
            raise SystemExit(3)
        attach_pid = int(attach_pid)
        log("  当前实例：%s" % describe([i for i in instances() if i["pid"] == attach_pid]))
    else:
        log("=== 0) 实例隔离预检（本工具只操作自有实例）===")
        ins = instances()
        own = own_pid()
        log("  当前实例：%s" % describe(ins))
    if not attach_pid and not preflight(args, ins, own):
        # 预检拒绝**必须**给非零退出码。
        #   以前这里直接 `return` → `main()` 返回 None → 进程退出码 **0**，
        #   而日志清清楚楚写着「本次未做任何操作」。任何按退出码判定的编排
        #   （以及本包自己的 driver.host / run_all_yjk）都会把「什么都没做」
        #   当成「成功」—— 实测就是这个后果（缺陷 L3 / 审计 S01·S02）。
        log("!! 预检未通过：**本轮一个动作都没做**（未开工、未登记、未杀任何实例）")
        log("   退出码 3 = 预检拒绝，供编排区分「拒绝开工」与「干活但失败(2)」")
        raise SystemExit(3)
    try:
        _host(args)
    finally:
        log("=== 9) 收尾 ===")
        errs = dlgwatch_errors()
        if errs:
            log("!! 本轮共拦下 %d 个**错误弹框**（说明有步骤真的失败了，别只看 OK 应答）："
                % len(errs))
            for t, b in errs[:5]:
                log("     %s | %s" % (t[:30], b[:90]))
        # 看门狗没起来 → "没有错误弹框"这句话**不成立**：账本为空只说明"没人看"。
        # 这条判据必须在 stop_dlgwatch() **之前**问。
        unav = dlgwatch_unavailable()
        if unav:
            log("!! 本轮**没有**模态框看门狗（%s）：'没有错误弹框'与'没人看着弹框'无法区分"
                % unav[0])
            log("   后果：RunCmd 返回的 OK 不能当成功证据，本轮结论不可信。")
            host_unverified("看门狗未运行（%s）：无法确认有没有真错误弹框" % unav[0])
        # 应答**发不出去**（PostMessage 返回 0）→ 框可能还挂着，那条命令的结果不可信。
        fld = dlgwatch_failed()
        if fld:
            log("!! 有 %d 个对话框的应答**发送失败**（PostMessage 返回 0）：框可能还挂着"
                % len(fld))
            for t, b, ans in fld[:5]:
                log("     %s | %s -> 本想回 %s" % (t[:30], b[:70], ans))
            host_unverified("有 %d 个对话框的应答发送失败（PostMessage 返回 0）"
                            "：框可能还挂着，相关命令的结果不可信" % len(fld))
        # 按新口径（DEFAULT=None）"看不懂的框一律不答"：如实报出来 —— 命令可能正被它挡住。
        unas = dlgwatch_unanswered()
        if unas:
            log("   另有 %d 个对话框**未命中规则、按设计没有应答**（框可能还挂着，"
                "需要人处理）：" % len(unas))
            for t, b in unas[:5]:
                log("     %s | %s" % (t[:30], b[:70]))
        # 未收窄阶段只登记的框：属于"当时还不知道归属"的实例（可能是别人的 YJK），
        #   本工具刻意不碰，只报出来。
        ntd = dlgwatch_noted()
        if ntd:
            log("   启动阶段（pid 未知）只登记、未动作的框 %d 个（可能是**别人**的实例）："
                % len(ntd))
            for p, t, b in ntd[:5]:
                log("     pid=%s %s | %s" % (p, t[:30], b[:70]))
        stop_dlgwatch()
        try:
            os.remove(ready_path(workdir))      # 会话结束 → send 重新变成"拒绝"
        except OSError:
            pass
        if attach_pid:
            log("attach 模式：不动目标实例 pid=%s（也不会关闭它）" % attach_pid)
        elif getattr(args, "keep", False):
            log("--keep：保留自有实例（不清理）。下次 host 会把登记里的它当残留清掉")
        else:
            kill_own()
        log("host 结束（只清理了自有实例；yjks 不会随宿主退出而自动回收，"
            "所以必须显式清，否则残留会抢 Global 事件）")
    # 收尾之后（不在 finally 里）判台账：放 finally 里会在 _host 抛异常时
    #   用 SystemExit 顶掉原始异常，反而丢掉排查线索。
    if _HOST_ERRORS:
        lic = [w for w in _HOST_ERRORS if w.startswith("授权/许可问题")]
        code = LICENSE_EXIT_CODE if lic else 2
        log("!! 本轮有 %d 项**确认为失败**（退出码 %d，别把这次当成功）："
            % (len(_HOST_ERRORS), code))
        for w in _HOST_ERRORS:
            log("     · %s" % w)
        if lic:
            log("")
            log(_license_hint())
        raise SystemExit(code)
    if _HOST_UNVERIFIED:
        log("!! 本轮有 %d 项**无法判定**（退出码 %d，别把这次当成功）："
            % (len(_HOST_UNVERIFIED), UNVERIFIED_EXIT_CODE))
        for w in _HOST_UNVERIFIED:
            log("     · %s" % w)
        log("   退出码 %d = 证据不足（区别于「确认为失败」的 2）：这一轮的产物可以看，"
            "但「没有错误弹框」这类结论不成立。" % UNVERIFIED_EXIT_CODE)
        raise SystemExit(UNVERIFIED_EXIT_CODE)


def preflight(args, ins, own) -> bool:
    """实例隔离预检：返回 True 才可以开工。**任何分支都不杀非自有实例。**"""
    foreign = [i for i in ins if i["kind"] == "foreign"]
    orphan = [i for i in ins if i["kind"] == "orphan"]
    dead = [i["pid"] for i in ins if i["kind"] == "dead"]
    if dead:
        log("  提示：%s 是**已终止的残壳**（0 线程、无窗口、不可执行、不抢事件；"
            "终止请求一律被 Windows 拒绝）。不阻断本次开工，重启后自会消失。" % dead)

    if own:
        d = _own_read()
        hp = d.get("host_pid")
        if host_alive(hp):
            # 不是残留，是**另一个正在跑的会话** —— 抢占会把它从半途踢掉
            log("  !! 另一个 host 会话仍在运行：host_pid=%s，自有实例 pid=%s，工作目录=%s"
                % (hp, own, d.get("workdir") or "?"))
            log("     并发两个会话会互相抢全局事件（结果都不可信），故**拒绝启动、不抢占**。")
            log("     请等它结束（收件箱发 exit），或人工确认后再处理。本次未做任何操作。")
            return False
        log("  发现上次会话残留的自有实例 pid=%s（其宿主已退出）—— 属本工具，先清掉再重开" % own)
        kill_own()

    foreign = [i for i in ins if i["kind"] == "foreign"]

    # 先提示"关哪个、怎么关"，可选等待：你关掉就自动继续，不必重跑
    if foreign and getattr(args, "wait_others", 0):
        t0 = time.time()
        while foreign and time.time() - t0 < args.wait_others:
            log("  等你关闭下面这个实例（已等 %.0fs，最多 %ds；关掉即自动继续）："
                % (time.time() - t0, args.wait_others))
            print_close_howto(foreign[0])
            time.sleep(15)
            foreign = [i for i in instances() if i["kind"] == "foreign"]
        if not foreign:
            log("  已关闭，继续开跑。")
            ins = instances()
            orphan = [i for i in ins if i["kind"] == "orphan"]

    if foreign:
        log("  !! 检测到 %d 个**你在用**的实例（有主窗口）——本工具不会替你关闭：" % len(foreign))
        for i in foreign:
            print_close_howto(i)
        log("  全局事件不能按 PID 定向，两实例会互相抢命令（应答来自错误实例）→ 结果不可信。")
        log("  关掉之后重跑本命令即可；也可以加 `--wait-others 600` 让它等你自己关。")
        log("  本次未做任何操作（未开工、未登记、未杀任何实例）。")
        return False

    if orphan:
        pids = [i["pid"] for i in orphan]
        log("  检测到 %d 个无主窗口残留实例（多由 YJKAPI.init/WinExec 拉起）：" % len(orphan))
        for i in orphan:
            log("     · pid=%s %s%s" % (i["pid"], window_text(i),
                                       "  打开=" + i["proj"] if i["proj"] else ""))
            if i["cmdline"]:
                log("       命令行: %s" % i["cmdline"][:160])
        if args.clean_orphans:
            log("  --clean-orphans 已允许：只清上面这些无主窗口实例（有窗口/带工程的一概不动）")
            for p in pids:
                kill_pid(p)
            time.sleep(2)
            left = [i for i in instances() if i["kind"] == "orphan"]
            log("  清理后剩余残留：%s" % ([i["pid"] for i in left] or "无"))
            if left:
                log("  !! 仍有残留未清干净，为免命令被抢，中止。")
                return False
        else:
            log("  它们同样会抢事件 → 命令不可信。三条出路（默认都不动手）：")
            log("     1) 自行清理： python <本技能>\\scripts\\yjk_cleanup.py --apply")
            log("     2) 允许本工具清： host ... --clean-orphans（先核对上面列出的命令行！）")
            log("     3) 若确认是你自己拉起的（例如带 -open），请在它的窗口里关闭")
            return False
    return True


def _host(args) -> None:
    workdir = os.path.normpath(args.dir)
    os.makedirs(workdir, exist_ok=True)
    name = args.name
    proj_yjk = os.path.normpath(os.path.join(workdir, name + ".yjk"))

    log("=== 工作目录 %s / 工程 %s ===" % (workdir, name))
    attach_pid = getattr(args, "pid", None)
    if attach_pid:
        log("=== 1) attach 模式：不清场、不启动 ===")
        log("=== 2) 跳过 YjkLauncher（接管已有实例）===")
        log("=== 3) 跳过启动，直接接管 pid=%s ===" % attach_pid)
        pid, ok = int(attach_pid), True
    else:
        log("=== 1) 清场（仅限自有实例；隔离预检已在第 0 步完成）===")
        if own_pid():
            kill_own()
            time.sleep(1)
        else:
            log("无自有实例需要清理")
        log("=== 2) 确保 YjkLauncher ===")
        ensure_launcher()
        log("=== 3) 启动 yjks（欢迎页）并等 IPC 通道 ===")
        # 看门狗必须在**启动 yjks 之前**拉起：启动过程本身也可能弹框（无人应答就卡到超时）
        start_dlgwatch()
        pid, ok = boot_yjks(workdir, wait_ipc=getattr(args, "wait_ipc", 150),
                            on_license=getattr(args, "on_license", "pause"),
                            license_timeout=getattr(args, "license_timeout", 1800),
                            invisible=getattr(args, "invisible", False))
    if not ok:
        # 每一条中止路径都要进失败台账：否则 host 返回 0，
        #   而自动化调用方只看退出码 → 会把"一个动作都没做"当成成功（缺陷 L3/S01/S02）。
        if license_blocked():
            host_fail("授权/许可问题：%s（已按 --on-license=%s 处理）"
                      % (license_blocked()[0][:120], getattr(args, "on_license", "pause")))
        else:
            host_fail("IPC 通道未就绪（yjks 没能起来/连不上）")
        log("!! 通道未就绪，终止。先跑 `python yjk_probe.py` 看缺什么")
        return
    if attach_pid:
        log("  attach 模式：不登记自有实例（收尾也不会关它）")
    else:
        own_claim(pid, rt_yjk().get("exe") or "", workdir)     # 登记自有实例
        log("  已登记自有实例 pid=%s -> %s" % (pid, OWN_FILE))
    if _DLGWATCH is not None and not attach_pid:
        # 拿到自有 pid 后立刻把看门狗收窄到本实例。启动阶段只能 pid=None（那时还不知道
        #   pid），而那时**只登记不动手**（见 dlgwatch 的「作用范围」与审计 S55）：
        #   收窄之前它一个按钮都不点，所以不会碰到别人的 YJK。
        _DLGWATCH.narrow(pid)
        log("  看门狗已收窄到自有实例 pid=%s（此后才开始按规则应答；不会触碰别人的对话框）"
            % pid)
    time.sleep(1)
    try:
        cli = Client(args.dll)
    except Exception as e:                                     # noqa: BLE001
        host_fail("官方客户端初始化失败: %s" % e)
        log("!! 客户端初始化失败: %s" % e)
        return
    log("官方客户端就绪（%s，%s）" % (cli.kind, cli.dll))
    # 8.x：先 initConfig(ControlConfig) 绑定本实例，否则首条命令可能静默不执行
    if getattr(cli, "has_init_config", False):
        ver = P.version_xyz(rt_yjk().get("version")) or "8.0.0"
        res = cli.configure(ver, invisible=getattr(args, "invisible", False), pid=pid)
        log("  8.x initConfig(Version=%s, Pid=%s) -> %s" % (ver, pid, res))

    log("=== 4) 在指定路径新建工程 ===")
    if not open_new_project(cli, proj_yjk, workdir,
                            reuse=getattr(args, "reuse", False)):
        host_fail("工程未就位（工作目录被占用或已有工程未被本实例打开）")
        log("!! 工程未就位，中止：避免在「无工程」状态下把 0.0s 秒回当成成功，"
            "并误读上一次留下的陈旧设计结果")
        return

    if args.import_file:
        ydb = os.path.normpath(args.import_file)
        src_size = _file_size(ydb)
        log("=== 5) 导入模型 ydb: %s ===" % ydb)
        before = snap(workdir)
        log("  yjk_importydb -> %s" % cli.run("yjk_importydb", ydb, 600))
        # 条件等待（不用固定 sleep）：save 之前 .ymd 一般不落盘，
        # 所以这里最多等 3s 拿"导入判据"，拿不到就交给 save 后的字节数
        wt = wait_until(lambda: bool(diff(before, snap(workdir))), 3.0, 0.5)
        log("    等写盘 %.1fs（条件等待）" % wt)
        # 判据必须在 save **之前**取：save 会把 ymd 重写，通常比源 ydb 多 1 个 sqlite 页
        imm = _file_size(os.path.join(workdir, name + ".ymd"))
        if src_size and imm is not None:
            d = imm - src_size
            if d == 0:
                verdict = "一致"
            elif abs(d) <= 4096:
                verdict = "差 %+d B（≤1 个 sqlite 页 4096 B，视为一致）" % d
            else:
                verdict = "偏差 %+d B，请核查" % d
            log("  导入判据（save 前）: %s.ymd = %d B，源 ydb = %d B -> %s"
                % (name, imm, src_size, verdict))
        elif src_size:
            log("  导入判据（save 前）：%s.ymd 尚未落盘，只能看 save 后的字节数" % name)
        log("  yjk_save -> %s" % cli.run("yjk_save", "", 300))
        wp = os.path.join(workdir, name + ".ymd")
        wt2 = wait_until(lambda: _file_size(wp) not in (None, imm), 5.0, 0.5)
        log("    等保存 %.1fs（条件等待）" % wt2)
        ch = [os.path.basename(k) for k in diff(before, snap(workdir))]
        log("  写盘文件: %s" % (sorted(set(ch)) or "无"))
        fin = _file_size(wp)
        if fin is not None:
            log("  %s.ymd = %d 字节（save 后；比源 ydb 大一页左右属正常）" % (name, fin))
        # 导入校验闸门（必须排在 yjk_save **之后**：.ymd 是 save 才写出的，
        #    早于 save 去开它只会得到"打不开数据库文件"）。
        #    字节数只能当参考（save 会重写库），判据是**逐表行数**：
        #    半写的 .ydb / 相对路径导入都会让 yjk_importydb 返回成功而导入空模型，
        #    失败要到计算阶段才以「模型中没有单元数据」+ 分析失败[-45] 现形。
        if not verify_import(ydb, workdir, name=name):
            host_fail("导入校验不通过：模型没有真的进来（%s）" % name)
            log("!! 已中止：不进入预处理/计算链（否则就是在空模型上白算一轮）")
            return

    if args.prep:
        log("=== 6) 预处理（修复/成节点/成楼板）===")
        for c, p in PREP_CHAIN:
            log("  %s(%r) -> %s" % (c, p, cli.run(c, p, 600)))

    if args.calc:
        ok, why = exclusive_ok(pid)
        if not ok:
            host_fail("计算链前发现实例不干净：%s" % why)
            log("!! %s；已中止计算链（不产生不可信结果）" % why)
            return
        log("=== 7) 官方计算链 ===")
        for c, p in CALC_CHAIN:
            t0 = time.time()
            log("  %s(%r) -> %s" % (c, p, cli.run(c, p, 1800)))
            log("    耗时 %.0fs" % (time.time() - t0))

    log("=== 8) 结果文件 ===")
    res_dir = os.path.join(workdir, "设计结果")
    if os.path.isdir(res_dir):
        fs = sorted(os.listdir(res_dir))
        newest = max((os.path.getmtime(os.path.join(res_dir, f)) for f in fs), default=0)
        log("  设计结果/ 共 %d 个：%s" % (len(fs), fs[:12]))
        log("  最新文件时间: %s%s" % (time.strftime("%H:%M:%S", time.localtime(newest)),
                                     "" if args.calc else
                                     "   ← 本次没跑 --calc，这些是**上一次**的结果，别当本轮用"))
    else:
        log("  无 设计结果 目录（未计算或路径不同）")

    if args.inbox:
        watch_inbox(cli, workdir, args.stay, own=pid,
                    idle_exit=getattr(args, "exit_when_idle", 0))
    elif args.stay:
        log("保持 yjks 存活 %ds ..." % args.stay)
        t0 = time.time()
        while time.time() - t0 < args.stay:
            log("  存活=%s 标题=%s" % (pid in yjks_pids(),
                                      titles(pid) if pid in yjks_pids() else None))
            time.sleep(20)
    # 收尾清理统一由 cmd_host 的 finally 负责（别在这里再清一次）


def main() -> None:
    # 控制台兜底：本文件会被别的脚本 import 当库用（那时不走 `__main__` 分支），
    # 而 log() 会打印 ★/≤ 以及 YJK 给的弹框正文等非 cp936 字符。
    _utf8_console()
    ap = argparse.ArgumentParser(description="YJK 全自动驱动工具（自适应，无写死路径）")
    ap.add_argument("--dll", default=None, help="指定官方客户端 DLL（默认自动探测）")
    sub = ap.add_subparsers(dest="mode", required=True)

    st = sub.add_parser("status", help="查看实例分类/窗口/命令行/IPC 通道状态")
    st.add_argument("--dir", default=None,
                    help="顺带查这个工作目录有没有「授权待处理」标志"
                         "（`_yjk_license.need_user`）；不给则查 own.json 里登记的工作目录")
    sub.add_parser("kill", help="杀掉全部 yjks 实例（人工逃生口）")
    cl = sub.add_parser("close", help="精确关闭指定 PID 的 yjks（关你自己的实例需加 --yes）")
    cl.add_argument("--pid", required=True, help="要关闭的 yjks PID（见 status）")
    cl.add_argument("--yes", action="store_true", help="确认关闭非自有实例（会中断该会话）")
    pr = sub.add_parser("probe", help="环境自检（推荐第一步）")
    pr.add_argument("--fix-config", action="store_true",
                    help="自动把 Config.ini 的 [YJKSControl] Flag 写成 True")

    h = sub.add_parser("host", help="常驻托管：清理→启动→建工程→导入→计算→收件箱")
    h.add_argument("--dir", required=True, help="工作目录")
    h.add_argument("--name", required=True, help="工程名（不含扩展名）")
    h.add_argument("--import", dest="import_file", default="", help="要导入的 .ydb")
    h.add_argument("--prep", action="store_true", help="先做修复/成节点/成楼板")
    h.add_argument("--calc", action="store_true", help="执行官方计算链")
    h.add_argument("--inbox", action="store_true", help="开启指令收件箱常驻")
    h.add_argument("--stay", type=int, default=0, help="存活秒数（0=不等待）")
    h.add_argument("--exit-when-idle", type=int, default=900, dest="exit_when_idle",
                   help="收件箱空闲多少秒后自动收尾（默认 900=15 分钟；0=一直等）")
    h.add_argument("--wait-others", type=int, default=0, dest="wait_others",
                   help="发现你在用的实例时，先提示+等你关闭最多 N 秒（每 15s 报一次，关掉即自动继续）")
    h.add_argument("--clean-orphans", action="store_true",
                   help="允许清理「无主窗口」的 yjks 残留实例（有主窗口的一概不动）")
    h.add_argument("--keep", action="store_true",
                   help="收尾保留自有实例（默认收尾清掉；保留的会被下次 host 当残留清）")
    h.add_argument("--reuse", action="store_true",
                   help="允许复用目录里已存在的 <工程名>.yjk（默认**拒绝**开工）："
                        "会明说「找到已有工程、将被打开/覆盖」，并先检查它有没有"
                        "正被另一个实例打开（那才是原规则真正要防的危险）")
    h.add_argument("--wait-ipc", type=int, default=150, dest="wait_ipc",
                   help="等 IPC 通道就绪的秒数（默认 150）")
    h.add_argument("--on-license", choices=("pause", "fail"), default="pause",
                   dest="on_license",
                   help="碰到 YJK **授权/许可**对话框时怎么办："
                        "pause（默认）= 打印醒目提示 + 写 "
                        "`_yjk_license.need_user` 标志 + **继续等**，"
                        "用户把许可修好（连 VPN 等）后通道一通就自动继续，不用重跑；"
                        "fail = 立刻以退出码 6 结束（无人值守编排用）")
    h.add_argument("--license-timeout", type=int, default=1800, dest="license_timeout",
                   help="授权暂停最多等多少秒（默认 1800=30 分钟）")
    h.add_argument("--pid", type=int, default=None,
                   help="attach 到已在运行的 yjks（8.x 会 initConfig 定向到该 Pid；不杀不启动）")
    h.add_argument("--invisible", action="store_true",
                   help="8.x：initConfig(Invisible=True) 静默计算（需 8.x DLL 支持）")

    s = sub.add_parser("send", help="把命令追加到收件箱")
    s.add_argument("cmd")
    s.add_argument("param", nargs="?", default="")
    s.add_argument("--dir", default=None, help="工作目录（默认当前目录）")

    args = ap.parse_args()
    {"status": cmd_status, "kill": cmd_kill, "close": cmd_close, "host": cmd_host,
     "send": cmd_send, "probe": cmd_probe}[args.mode](args)


def _utf8_console():
    """让输出在任何控制台编码下都不崩（GBK 下把不可编码字符替换掉）。

    为什么需要：本包会打印 ✅ ❌ ⚠ −(U+2212) ² ³ 等**非 cp936** 字符，
    默认 GBK 控制台下 print 会抛 UnicodeEncodeError 并**以退出码 1 中断**，
    于是一个其实已经成功的任务（比如文件已经落盘）会被上层判成失败。
    errors=replace 让它在 UTF-8 控制台下原样输出、在 GBK 下退化成 ?，都不崩。

    只在真正的 CLI 入口调用：本文件会被别人 import 当库用，
      在模块顶层无条件改 stdout 会污染 import 它的进程。
    """
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(errors="replace")
        except Exception:
            pass


if __name__ == "__main__":
    _utf8_console()
    main()
