# -*- coding: utf-8 -*-
"""YJK 二次开发 API 引导（pythonnet 3.x + **安装目录自带**的 STCAD 程序集）。

★ 硬性约束 1（本节最重要）
    必须使用 `<YJK安装目录>\\STCAD` 下**同一套**程序集：
        YAPIData.dll / YJKAPI.dll / CsToYjk.dll / ClrYJKAPI.dll
    **不要**用 `yjk-auto-drive/assets/YJKAPI.dll`。那份 DLL 取自官方开源仓库
    `gitee.com/yjk-opensource/csharp-yjks` 的 7.1 分支，它引用
    `RevitYjkND.Hi_MdlToCYjk` 类型 —— 该类型在**任何已安装的盈建科版本**里都不存在
    （7.1/8.1 的 ClrYJKAPI.dll 都没有），必然抛
    `System.TypeLoadException: 未能从程序集"ClrYJKAPI…"中加载类型"RevitYjkND.Hi_MdlToCYjk"`。
    安装版自带的是 `CsToYjk.Hi_AddProjectToYjk`（不是 `Hi_AddToAndReadYjk`）。

★ 硬性约束 2
    `YJKS_7_1_0\\STCAD` 与 `YJKS_8_1_0\\STCAD` 的这 4 个 DLL **逐字节相同**（md5 一致），
    所以建模 API 与 7.1 / 8.1 无关，两版可通用；生成的 ydb 也是同一个 SQLite 结构。

★ 硬性约束 3
    `ClrYJKAPI.dll` 是 C++/CLI 混合模式程序集，加载时需要原生依赖
    （jcResultPort.dll / jccadPort.dll / yjkCadNewData.dll / yjkSPara.dll / ypGeo.dll）
    在同目录或 PATH 上。所以必须把 STCAD 加进 `os.add_dll_directory` 与 PATH。
    ※ 只能用 `STCAD\\ClrYJKAPI.dll`（6.64 MB，可正常加载）；
      **安装根目录**下那份 `ClrYJKAPI.dll`（约 9.8 MB）会直接 native crash（段错误），
      属官方文档所说"8.x 原生库与 7.1 互斥"的混用陷阱，禁止加载。

★ 硬性约束 4
    pythonnet 3.x 以**命名空间**为导入单位，不以程序集名为单位：
        clr.AddReference(<dll 全路径>)
        import DataFuncApplication as D
        import CsToYjk as C
    没有 `from YJKAPI import *` 这种写法（老技能里的写法已失效）。
"""
import glob
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

_DLL_HANDLES = []           # 保持 os.add_dll_directory 句柄存活，不能回收
_STCAD = None


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


def _driver_paths():
    """复用 yjk-auto-drive/scripts/paths.py —— 跨机器定位逻辑只维护那一处。

    候选链见上面那段 `COMPAT-FALLBACK` —— 六份副本**一致**（内容逐字节相同，行尾各随本文件）。

    只保留三样：环境变量 → 同级目录 → 与厂商无关的通用扫描 + 中立位置，
    最后是历史遗留路径（保留以不破坏现有用户）。**不含任何具体厂商名、盘符、
    用户名或桌面路径**（桌面探测早已删除：技能不该假定自己放在桌面）。
    要改就六份一起改，并跑 `selfcheck.py`（T31 逐字节比对）与 `compat_check.py`。
    """
    for d in _compat_driver_dirs():
        c = os.path.join(d, "scripts")
        if os.path.isfile(os.path.join(c, "paths.py")):
            c = os.path.abspath(c)
            if c not in sys.path:
                sys.path.append(c)
            try:
                import paths as P
                return P
            except Exception:                                    # noqa: BLE001
                return None
    return None


def _fallback_roots():
    """兜底：枚举本机**所有**盘符下的常见安装位置（不写死 C:/D:/E:）。"""
    out = []
    drives = []
    sysd = os.environ.get("SystemDrive")
    if sysd:
        drives.append(sysd.rstrip("\\/") + os.sep)
    for L in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        d = "%s:\\" % L
        if d not in drives and os.path.isdir(d):
            drives.append(d)
    for d in drives:
        for sub in ("YJKS", "YJK", "盈建科", "Program Files",
                    "Program Files (x86)", "ProgramData"):
            p = os.path.join(d, sub)
            if os.path.isdir(p):
                out.append(p)
    return out


def find_stcad(explicit=None):
    """定位可用的 STCAD 目录（含 YAPIData/YJKAPI/CsToYjk/ClrYJKAPI 四件套）。"""
    global _STCAD
    cands = []
    if explicit:
        cands.append(explicit)
    if os.environ.get("YJK_STCAD_DIR"):
        cands.append(os.environ["YJK_STCAD_DIR"])
    for env in ("YJK_DIR", "YJK_ROOT", "YJK_HOME", "YJKS_DIR", "YJK_INSTALL"):
        if os.environ.get(env):
            cands.append(os.path.join(os.environ[env], "STCAD"))
    # 运行中的 yjks.exe 所在目录（最可靠）
    for p in _running_yjks():
        cands.append(os.path.join(os.path.dirname(p), "STCAD"))
    # 安装根目录：优先复用驱动技能的跨机器探测（环境变量→运行进程→注册表→扫盘）
    P = _driver_paths()
    roots = []
    if P is not None:
        try:
            roots = P.all_install_roots()
        except Exception:                                        # noqa: BLE001
            roots = []
    if not roots:
        roots = _fallback_roots()
    for root in roots:
        cands += sorted(glob.glob(os.path.join(root, "*", "STCAD")))
        cands += sorted(glob.glob(os.path.join(root, "STCAD")))
    need = ("YAPIData.dll", "YJKAPI.dll", "CsToYjk.dll", "ClrYJKAPI.dll")
    for c in cands:
        if c and all(os.path.isfile(os.path.join(c, f)) for f in need):
            _STCAD = os.path.abspath(c)
            return _STCAD
    return None


def _running_yjks():
    out = []
    try:
        import ctypes
        from ctypes import wintypes
        k32 = ctypes.WinDLL("kernel32", use_last_error=True)
        psapi = ctypes.WinDLL("psapi", use_last_error=True)
        arr = (wintypes.DWORD * 4096)()
        need = wintypes.DWORD()
        if psapi.EnumProcesses(ctypes.byref(arr), ctypes.sizeof(arr), ctypes.byref(need)):
            n = need.value // ctypes.sizeof(wintypes.DWORD)
            for i in range(n):
                h = k32.OpenProcess(0x1000, False, arr[i])       # QUERY_LIMITED_INFORMATION
                if not h:
                    continue
                buf = ctypes.create_unicode_buffer(1024)
                sz = wintypes.DWORD(len(buf))
                if k32.QueryFullProcessImageNameW(h, 0, buf, ctypes.byref(sz)):
                    if os.path.basename(buf.value).lower() == "yjks.exe":
                        out.append(buf.value)
                k32.CloseHandle(h)
    except Exception:                                            # noqa: BLE001
        pass
    return out


def bootstrap(stcad=None, verbose=False):
    """加载 API 程序集并返回 (D, C) —— DataFuncApplication / CsToYjk 两个模块。"""
    st = find_stcad(stcad)
    if not st:
        raise SystemExit("找不到 YJK 安装目录下的 STCAD（需含 YAPIData/YJKAPI/CsToYjk/ClrYJKAPI）")

    os.environ["PATH"] = st + os.pathsep + os.environ.get("PATH", "")
    _DLL_HANDLES.append(os.add_dll_directory(st))
    root = os.path.dirname(st)
    if os.path.isdir(root):
        _DLL_HANDLES.append(os.add_dll_directory(root))
        os.environ["PATH"] = root + os.pathsep + os.environ["PATH"]
    # ★ 追加到 sys.path 末尾（绝不能 insert(0)：安装根目录的 8.x YJKAPI.dll 会抢先解析）
    for d in (st, root):
        if d and d not in sys.path:
            sys.path.append(d)

    import clr
    for f in ("YAPIData.dll", "YJKAPI.dll", "CsToYjk.dll"):
        clr.AddReference(os.path.join(st, f))
    # ClrYJKAPI 由 YJKAPI/CsToYjk 的原生-托管边界按需加载；显式加一次更稳
    try:
        clr.AddReference(os.path.join(st, "ClrYJKAPI.dll"))
    except Exception as e:                                       # noqa: BLE001
        if verbose:
            print("[yjk_api] ClrYJKAPI 直接加载失败（可忽略）：%s" % e)

    import DataFuncApplication as D
    import CsToYjk as C
    if verbose:
        print("[yjk_api] STCAD = %s" % st)
    return D, C


def stcad():
    return _STCAD or find_stcad()


if __name__ == "__main__":
    D, C = bootstrap(verbose=True)
    print("DataFuncApplication.DataFunc ->", D.DataFunc)
    print("CsToYjk.Hi_AddProjectToYjk  ->", C.Hi_AddProjectToYjk)
    df = D.DataFunc()
    print("DataFunc 实例 OK")
