# -*- coding: utf-8 -*-
r"""本技能与 `yjk-auto-drive` 技能之间的桥：定位驱动技能、准备官方 API、调用驱动。

为什么要拆成两个技能
--------------------
「驱动 YJK」与「优化柱截面」是两件独立的事：前者要处理 IPC 通道、单实例、
Config.ini；后者要处理轴压比限值、造价、工程量、报告。混在一起会让两边都难维护，
也没法把"驱动"复用到别的优化目标（梁、墙、基础）上。

因此本技能**不含**任何 IPC / 启动逻辑，只通过本模块调用 `yjk-auto-drive`。

本模块提供三件事
----------------
  find_driver()     找 `yjk-auto-drive` 技能目录（候选链，无写死路径）
  scripts_dir()     它的 scripts 目录
  ensure_api()      把官方 YJKAPI.dll 准备成可 import 的模块（给 frame_build.py 用）
  host(...)         调它的 yjk_auto.py host 做「导入 + 预处理 + 计算」
  dll_path()        拿官方客户端 DLL 路径

查找顺序（无写死路径；实现就是下面那段 COMPAT-FALLBACK 块）
----------------------------------------------------------
  1) 环境变量（三个都认）：YJK_DRIVER_DIR → YJK_AUTO_DRIVE_DIR → YJK_SKILLS_DIR
  2) 同级目录：<技能>/../.. 与 <技能>/..  —— 装机默认形态，最可靠
  3) 当前目录：<cwd>/<技能> 与 <cwd>/../<技能>
  4) **通用扫描**（与厂商无关）：枚举 ~ 与 ~/.config 的一级子目录 D，逐个探
     D/skills/<技能>、D/<技能>；再探中立位置 ~/.agent-skills、~/.skills、<cwd>/.skills
  5) ~/.workbuddy-ai/skills/<技能> —— **历史遗留路径，保留以不破坏现有用户**
     （唯一带厂商名的一档；去掉它其余各档照样工作，所以它不是"前提"）

  这一套链在本包里被**故意复制成六份**（业务技能在找到驱动目录之前没法 import 它的
  paths.py，鸡生蛋），每一份都带同一段 `COMPAT-FALLBACK` 块，**改一处就得六份一起改**：
  `selfcheck.py` 的 T31 会逐条比对（块内容、候选顺序、块外不许另起一套、不许写死桌面），
  `compat_check.py` 再从"能力"角度兜一遍。
"""
from __future__ import annotations

import glob
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(HERE)

USER_CACHE = os.path.join(os.path.expanduser("~"), ".yjk-auto")
SKILL_NAME = "yjk-auto-drive"

# ---------------------------------------------------------------- 原生 DLL 搜索路径
# ★★ 这里曾经是个**会挂死进程**的坑，务必保持现状：
#   `os.add_dll_directory(d)` 返回一个 `DllDirectory` 对象，**它被回收时就会
#   RemoveDllDirectory**。如果写成 `os.add_dll_directory(d)` 而不接返回值，
#   CPython 在该语句结束时立刻把它回收 → 目录瞬间被移出搜索路径 → 后面
#   YJK 原生代码 `LoadLibrary("yjkTransYDB.dll")` 找不到文件，它会用**自己的
#   MessageBox** 报「未能加载到yjkTransYDB.dll或其依赖项」。
#   模态框一弹，进程**永久挂住**：不是托管异常，try/except 拦不住，超时也杀不干净。
#   （`floor-system-comparison/scripts/yjk_api.py` 里的 `_DLL_HANDLES` 是对的，
#     这里原来漏了保活 —— 同一份知识没在两个技能之间传播。）
_DLL_HANDLES = []          # ★ 必须模块级保活，不能回收
_PINNED_DIRS = set()


def pin_native_dll_dir(*dirs):
    """把目录钉进本进程的原生 DLL 搜索路径，返回实际钉住的目录列表。

    三重保险：① 保住 add_dll_directory 的句柄；② SetDllDirectoryW（进程级默认目录，
    老式 LoadLibrary 也认）；③ 追加 PATH。
    """
    import ctypes
    good = []
    for d in dirs:
        if d and os.path.isdir(d):
            d = os.path.abspath(d)
            if d not in good:
                good.append(d)
    k32 = None
    try:
        k32 = ctypes.WinDLL("kernel32", use_last_error=True)
    except Exception:                                           # noqa: BLE001
        pass
    for d in good:
        if d not in _PINNED_DIRS:
            _PINNED_DIRS.add(d)
            try:
                _DLL_HANDLES.append(os.add_dll_directory(d))
            except Exception:                                   # noqa: BLE001
                pass
            if k32 is not None:
                try:
                    k32.SetDllDirectoryW(d)
                except Exception:                               # noqa: BLE001
                    pass
    if good:
        os.environ["PATH"] = os.pathsep.join(good + [os.environ.get("PATH", "")])
    return good


# yjkTransYDB.dll 的直接依赖（PE 导入表实测）；按绝对路径预加载最稳
TRANSYDB_DEPS = ("ypGeo.dll", "yjkSPara.dll", "YJK_SQL.dll",
                 "yjkCadNewData.dll", "yjkTransYDB.dll")


def preload_native(dll_dir, names=TRANSYDB_DEPS):
    """用 ctypes 把原生依赖按**绝对路径**先加载一遍，避免运行期再去搜。"""
    import ctypes
    ok, bad = [], []
    for n in names:
        p = os.path.join(dll_dir, n)
        if not os.path.exists(p):
            bad.append((n, "文件不存在"))
            continue
        try:
            ctypes.WinDLL(p)
            ok.append(n)
        except OSError as e:
            bad.append((n, str(e)))
    return ok, bad


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


def _candidates():
    """yjk-auto-drive 技能目录的候选位置（生成器，命中即止）。

    实现就是上面那段 `COMPAT-FALLBACK`；传 SKILL_NAME 以保持"技能名只写一处"。
    """
    for c in _compat_driver_dirs(SKILL_NAME):
        yield c


def find_driver(verbose=False):
    """返回 `yjk-auto-drive` 技能目录（含 scripts/yjk_auto.py 的那个）。"""
    for c in _candidates():
        if not c:
            continue
        c = os.path.abspath(c)
        if os.path.exists(os.path.join(c, "scripts", "yjk_auto.py")):
            if verbose:
                print("驱动技能目录：%s" % c)
            return c
    return None


def scripts_dir(verbose=False):
    d = find_driver(verbose)
    return os.path.join(d, "scripts") if d else None


def require_driver():
    d = find_driver()
    if not d:
        raise SystemExit(
            "找不到 `yjk-auto-drive` 技能（需要它来驱动 YJK）。\n"
            "四种解决办法（任选其一）：\n"
            "  1) 把 yjk-auto-drive 目录放在与本技能同级的 skills 目录下\n"
            "  2) 设环境变量 YJK_AUTO_DRIVE_DIR=<yjk-auto-drive 的绝对路径>\n"
            "  3) 设环境变量 YJK_SKILLS_DIR=<整套技能的安装根目录>\n"
            "  4) 把整套技能放进**本 agent 的用户级技能目录**即可 —— 本模块会枚举\n"
            "     ~ 与 ~/.config 的一级子目录去找 <D>/skills/yjk-auto-drive，"
            "不写死任何厂商目录\n"
            "查找过的位置：\n  " + "\n  ".join(
                os.path.abspath(c) for c in _candidates() if c))
    return d


# ---------------------------------------------------------------- 官方 API
def _driver_paths_mod():
    """复用驱动技能的 paths.py（跨机器定位都集中在那一处）。"""
    d = scripts_dir()
    if not d:
        return None
    if d not in sys.path:
        sys.path.insert(0, d)
    try:
        import paths as P
        return P
    except Exception:                                          # noqa: BLE001
        return None


def dll_path(explicit=None):
    """官方客户端 DLL 路径（用于确定 YJKAPI.dll 所在目录）。"""
    P = _driver_paths_mod()
    if P is None:
        return explicit
    info = P.find_yjkapi_dll(explicit)
    return info["path"]


def ensure_api(explicit=None, verbose=True):
    """把官方 DLL 准备成「可 `from YJKAPI import *`」的状态，返回其所在目录。

    frame_build.py 依赖官方**建模接口**（`Hi_AddToAndReadYjk` / `DataFunc` / `BzcPara`），
    这些类型在 `YJKAPI.dll` 里。不同来源的 DLL 文件名可能不同，
    所以统一**复制/链接到 `~/.yjk-auto/YJKAPI.dll`**，再把该目录放进 sys.path ——
    这样 import 名字永远是 `YJKAPI`，与来源无关。
    """
    os.makedirs(USER_CACHE, exist_ok=True)
    target = os.path.join(USER_CACHE, "YJKAPI.dll")
    src = dll_path(explicit)
    if not src:
        raise SystemExit(
            "未找到官方 YJKAPI.dll。请先跑 `yjk-auto-drive/scripts/yjk_probe.py` 按提示准备，"
            "或设环境变量 YJKAPI_DLL=<路径>。")
    if os.path.normcase(os.path.abspath(src)) != os.path.normcase(target):
        try:
            shutil.copy2(src, target)
        except OSError as e:
            raise SystemExit("无法把 %s 复制到 %s：%s" % (src, target, e))
    # 依赖件一起带过来（有的版本需要）
    sdir = os.path.dirname(src)
    for extra in ("YAPIData.dll",):
        s, t = os.path.join(sdir, extra), os.path.join(USER_CACHE, extra)
        if os.path.exists(s) and not os.path.exists(t):
            try:
                shutil.copy2(s, t)
            except OSError:
                pass
    if USER_CACHE not in sys.path:
        sys.path.insert(0, USER_CACHE)
    if verbose:
        print("官方 API 就绪：%s -> %s" % (src, USER_CACHE))
    return USER_CACHE


# ---- 官方「建模接口」类型的正确加载方式 -------------------------------------
# ★ 坑 1：为什么不能 `from YJKAPI import *`
#   YJKAPI.dll 的**程序集名**确实叫 `YJKAPI`，但它的**根命名空间**是
#   `DataFuncApplication` / `CsToYjk` / `YJKIPC` —— 里面根本没有叫 `YJKAPI`
#   的命名空间。pythonnet 是按「命名空间」暴露模块的，所以 `import YJKAPI`
#   永远是 ModuleNotFoundError，无论把 dll 放哪、复制成什么名字。
#       DataFuncApplication.DataFunc      ← 建模主体
#       DataFuncApplication.BzcPara       ← 标准层参数串
#       DataFuncApplication.SlabCreateInfo
#       CsToYjk.<写 ydb 的入口>           ← 见坑 3
# ★ 坑 2：必须**先 `import clr`** 再 `clr.AddReference(<dll 绝对路径>)`；
#   少了 import clr，pythonnet 的 DLL 导入钩子压根没装上，一样是
#   ModuleNotFoundError（症状与「dll 不在」几乎一样）。
# ★ 坑 3：写 ydb 的入口有**两代**，必须配对，配错必炸：
#     老式（YJK 7.x）：CsToYjk.Hi_AddProjectToYjk   —— 只要 STCAD\YJKAPI.dll
#     新式（YJK 8.x）：CsToYjk.Hi_AddToAndReadYjk   —— 还要同代的 ClrYJKAPI.dll
#   对照（7.1 与 8.1 并存时）：
#     <7_1_0>\STCAD\YJKAPI.dll    (约 183 KB) 有 Hi_AddProjectToYjk  ★ 能用
#     <8_1_0>\YJKAPI.dll          (约 515 KB) 有 Hi_AddToAndReadYjk
#     <8_1_0>\ClrYJKAPI.dll       (约 9.8 MB) 有 RevitYjkND.Hi_MdlToCYjk
#     ⚠ 那份约 9.8MB 的 ClrYJKAPI 在 pythonnet 里 **AddReference / LoadFile 都会
#       直接让进程 access violation 崩掉**（无法 try/except 捕获）→ 新式路线
#       可能整体不可用。技能 assets 里带的 YJKAPI.dll 是**新式**的，
#       拿它去建模会在最后写 ydb 那一步报 FileNotFoundException: ClrYJKAPI，
#       此时模型已经建好了（节点/柱段/梁段/板都齐），特别容易被误判成"建模失败"。
#   → 所以这里**优先挑带 `Hi_AddProjectToYjk` 的那份**（安装目录 STCAD 下）。
MODELING_TYPES = (("DataFuncApplication", "DataFunc"),
                  ("DataFuncApplication", "BzcPara"),
                  ("DataFuncApplication", "SlabCreateInfo"))
WRITERS = (("CsToYjk", "Hi_AddProjectToYjk"),      # 老式：不需要 ClrYJKAPI
           ("CsToYjk", "Hi_AddToAndReadYjk"))      # 新式：需要同代 ClrYJKAPI
MODEL_CACHE = os.path.join(USER_CACHE, "model")
_LAST_MODEL_SRC = None          # 上次选中的 YJKAPI.dll 原路径（配 ClrYJKAPI 用）


def _install_roots():
    """YJK 安装目录候选（当前安装 + 同级其它版本），去重、无写死盘符。"""
    roots = []
    P = _driver_paths_mod()
    if P is not None:
        try:
            info = P.find_yjk_install() or {}
        except Exception:                                       # noqa: BLE001
            info = {}
        for r in [info.get("root")] + list(info.get("candidates") or []):
            r = os.path.abspath(r) if r else None
            if r and os.path.isdir(r) and r not in roots:
                roots.append(r)
    for r in list(roots):                                       # 同级安装（多版本并存）
        try:
            for d in glob.glob(os.path.join(os.path.dirname(r), "*")):
                if os.path.isdir(d) and d not in roots:
                    roots.append(d)
        except Exception:                                       # noqa: BLE001
            pass
    return roots


def _api_candidates(explicit=None):
    """YJKAPI.dll 候选链：显式/环境变量 → 各安装目录 → 驱动技能 assets → 缓存。"""
    out = []
    for v in (explicit, os.environ.get("YJKAPI_DLL")):
        if v:
            out.append(os.path.abspath(v))
    for r in _install_roots():
        out += [os.path.join(r, "STCAD", "YJKAPI.dll"), os.path.join(r, "YJKAPI.dll")]
    d = find_driver()
    if d:
        out.append(os.path.join(d, "assets", "YJKAPI.dll"))
    out += [os.path.join(MODEL_CACHE, "YJKAPI.dll"), os.path.join(USER_CACHE, "YJKAPI.dll")]
    seen, res = set(), []
    for p in out:
        if not p or not os.path.exists(p):
            continue
        k = os.path.normcase(os.path.abspath(p))
        if k in seen:
            continue
        seen.add(k)
        res.append(os.path.abspath(p))
    return res


# ★ 判别「这份 YJKAPI.dll 能不能建模」的客观标志（在 DLL 元数据字符串堆里搜，
#   比反射快，且不怕依赖缺失）。
_NEEDLE_OLD = b"Hi_AddProjectToYjk"
_NEEDLE_NEW = b"Hi_AddToAndReadYjk"


def _has_needle(path, needle):
    try:
        with open(path, "rb") as f:
            return needle in f.read()
    except OSError:
        return False


def ensure_model_api(explicit=None, verbose=False):
    """挑一份**能建模**的 YJKAPI.dll，返回它的**原路径**（不复制）。

    ★ 为什么**不能**复制到别处再引用
      `YJKAPI.dll` 与 `ClrYJKAPI.dll` 是**成对**的：CLR 解析
      `ClrYJKAPI` 引用时是按"**发起程序集所在目录**"探测的。
      一旦把 YJKAPI.dll 复制到 `~/.yjk-auto/model/`（那里没有 ClrYJKAPI），
      再去 `AddReference` 另一目录的 ClrYJKAPI，pythonnet 会直接
      **access violation 进程崩溃**（try/except 拦不住）。
      → 就地引用安装目录里的那一对，最稳。
    ★ 也不要用 `~/.yjk-auto/` 里那份缓存：那是给 IPC 客户端
      （`YJKIPC.YJKSControl`）用的，与建模需求的入口不同，不要互相覆盖。
    """
    cands = _api_candidates(explicit)

    picked, notes = None, []
    for needle, label in ((_NEEDLE_OLD, "老式 Hi_AddProjectToYjk"),
                          (_NEEDLE_NEW, "新式 Hi_AddToAndReadYjk")):
        for p in cands:
            if _has_needle(p, needle):
                picked = p
                notes.append("%s ← %s" % (label, p))
                break
        if picked:
            break
        notes.append("%s：%d 个候选里都没有" % (label, len(cands)))

    if picked is None:
        raise SystemExit(
            "找不到可用于建模的 YJKAPI.dll。\n查过的候选：\n  " +
            "\n  ".join(cands or ["(一个都没有)"]))
    global _LAST_MODEL_SRC
    _LAST_MODEL_SRC = picked                                    # 供 _add_clr_yjkapi 配同目录
    sdir = os.path.dirname(picked)
    # ★ 同目录的原生依赖（YAPIData / yjkTransYDB 等）：必须**保住句柄**，见模块顶部说明
    pinned = pin_native_dll_dir(sdir)
    ok, bad = preload_native(sdir)
    if verbose:
        print("原生 DLL 目录已钉住：%s" % pinned)
        print("原生依赖预加载：OK %s%s" % (ok, ("  失败 %s" % bad) if bad else ""))
    if sdir not in sys.path:
        sys.path.insert(0, sdir)
    if verbose:
        print("建模 API：%s" % "；".join(notes))
    return picked


def load_modeling_api(explicit=None, verbose=False):
    """加载官方建模接口，返回 {类型名: .NET 类型, "writer": 写 ydb 的类}。

    `writer` 是二选一的：`Hi_AddProjectToYjk`（老式）或 `Hi_AddToAndReadYjk`（新式），
    两者都用 `w = writer(model)` → `w.CreateYDB(目录, 文件名)`。
    """
    dll = ensure_model_api(explicit, verbose=verbose)           # 安装目录里的原路径
    if not os.path.exists(dll):
        raise SystemExit("YJKAPI.dll 不在 %s。先跑 `driver.py api` 或设 YJKAPI_DLL=<路径>。" % dll)
    try:
        import clr                                              # noqa: F401
    except ImportError:
        info = None
        P = _driver_paths_mod()
        if P is not None:
            try:
                info = P.find_python()
            except Exception:                                   # noqa: BLE001
                info = None
        hint = (info or {}).get("exe")
        raise SystemExit(
            "当前解释器没有 pythonnet（`import clr` 失败），无法加载官方建模接口。\n"
            "  当前解释器：%s\n"
            "  应改用：%s\n"
            "（`colopt.py build` 已自动处理；手工跑 frame_build.py 时请用上面那个）"
            % (sys.executable, hint or "<带 pythonnet 的解释器>"))
    clr.AddReference(dll)
    # 写 ydb 的实现程序集，**两代都需要**；优先用与上面同目录的那份
    _add_clr_yjkapi(clr, verbose=verbose, prefer_dir=os.path.dirname(_LAST_MODEL_SRC or dll))

    out, missing = {}, []
    for ns, tname in MODELING_TYPES:
        got = None
        try:
            got = getattr(__import__(ns), tname, None)
        except Exception:                                       # noqa: BLE001
            got = None
        if got is None:
            try:
                got = getattr(__import__("YJKAPI"), tname, None)
            except Exception:                                   # noqa: BLE001
                got = None
        if got is None:
            missing.append("%s.%s" % (ns, tname))
        else:
            out[tname] = got
    if missing:
        raise SystemExit("在 %s 里找不到这些建模接口类型：%s\n"
                         "（根命名空间或许变了，跑 `driver.py sig` 看实际类型）" % (dll, missing))

    writer, wname = None, None
    for ns, tname in WRITERS:
        try:
            got = getattr(__import__(ns), tname, None)
        except Exception:                                       # noqa: BLE001
            got = None
        if got is None:
            continue
        writer, wname = got, "%s.%s" % (ns, tname)
        break
    if writer is None:
        raise SystemExit(
            "这份 YJKAPI.dll（%s）里没有可用的写 ydb 入口（%s 都没有）。\n"
            "老式入口只存在于安装目录的 STCAD\\YJKAPI.dll 里；\n"
            "新式入口需要同代的 ClrYJKAPI.dll（体积大的那份会让进程崩溃）。"
            % (dll, "/".join(t for _, t in WRITERS)))
    out["writer"] = writer
    out["writer_name"] = wname
    if verbose:
        print("建模接口就绪：%s  写 ydb 用 %s"
              % (", ".join(sorted(k for k in out if k.isascii() and k[0].isupper())), wname))
    return out


# ---- 新式入口的 ClrYJKAPI 依赖（只有走 Hi_AddToAndReadYjk 时才需要）---------
# `CsToYjk.Hi_AddToAndReadYjk..ctor` 内部要用 `RevitYjkND.Hi_MdlToCYjk`，
# 该类型只存在于**某些** ClrYJKAPI 里。用错会报：
#   System.TypeLoadException: 未能从程序集"ClrYJKAPI"中加载类型"RevitYjkND.Hi_MdlToCYjk"
# 对照（7.1 与 8.1 并存时）：
#   <8_1_0>\ClrYJKAPI.dll        (约 9.8 MB)  有该类型 ← 但加载必崩（见上）
#   <7_1_0>\STCAD\ClrYJKAPI.dll  (约 6.6 MB)  无
#   <8_1_0>\STCAD\ClrYJKAPI.dll  (约 6.6 MB)  无
# 注意：正解**不在** STCAD 下——直觉（"STCAD 才是接口目录"）在这里是错的。
_CLR_NEEDLE = b"Hi_MdlToCYjk"


def _add_clr_yjkapi(clr, verbose=False, prefer_dir=None):
    """引用 `ClrYJKAPI.dll` —— 写 ydb 的实现程序集（**两代都需要**）。

    ★ 为什么非它不可
      `YJKAPI.dll` 里只有**签名**（`Hi_AddProjectToYjk` / `Hi_AddToAndReadYjk`），
      实现在 `ClrYJKAPI.dll`。不引用它，`.ctor(model)` 会报
      FileNotFoundException: ClrYJKAPI。
      而这发生在**最后一步**——此时模型已经建好了（节点/柱段/梁段/板都齐），
      特别容易被误判成"建模失败"。

    ★ 为什么不"多试几个目录"、为什么只认**同目录**
      YJKAPI 与 ClrYJKAPI 是**成对编译**的，必须同版本。跨版本混用会踩三种坑：
        FileNotFoundException → TypeLoadException → **进程 access violation**。
      最后那种是**进程级崩溃，try/except 拦不住**，跑一次就是一次 segfault，
      没法靠"挨个试"兜底。所以：只在 `prefer_dir`（选中 YJKAPI.dll 的同目录）
      里取配对的那份；取不到就干脆报错，让用户把 `--dll` / `YJKAPI_DLL`
      指到一个**完整的安装目录**（同时有 YJKAPI.dll 和 ClrYJKAPI.dll），
      而不是拿错误版本的组合去撞崩溃。
      （8.1 根目录那份约 9.8MB 会崩；7.1 STCAD 那份约 6.6MB 正常。
        两者都含 RevitYjkND，所以"按类型名筛选"区分不出它们——
        唯一可靠的办法就是**同目录**。）
    ★ 另外注意：新式接口需要的类型是 `RevitYjkND.Hi_MdlToCYjk`，老式的配对
      ClrYJKAPI 里**没有**这个名字 —— 用"有没有 Hi_MdlToCYjk"去筛，会把 7.1
      的正确配对错杀、反而选中必崩的 8.1 那份。所以这里不做类型名筛选。
    """
    env = os.environ.get("YJK_CLRAPI_DLL")
    cands = []
    if env:
        cands.append(os.path.abspath(env))
    if prefer_dir:
        cands.append(os.path.join(prefer_dir, "ClrYJKAPI.dll"))
    tried = []
    for c in cands:
        if not os.path.exists(c):
            tried.append((c, "文件不存在"))
            continue
        # ★ 同目录的原生依赖：句柄必须保活（见模块顶部说明），别写成不接返回值的调用
        pin_native_dll_dir(os.path.dirname(c))
        try:
            clr.AddReference(c)
        except Exception as e:                                  # noqa: BLE001
            tried.append((c, str(e)[:100]))
            continue
        if verbose:
            print("ClrYJKAPI 就绪：%s" % c)
        return c
    raise SystemExit(
        "找不到与 YJKAPI.dll 配对的 ClrYJKAPI.dll —— 它俩必须同目录（同版本）。\n"
        "  选中的 YJKAPI.dll：%s\n"
        "  期望的 ClrYJKAPI.dll：%s\n"
        "请把 YJKAPI.dll 指向一个**完整安装目录**里的那份（同时含两个 dll），\n"
        "例如 <YJK安装目录>\\STCAD\\YJKAPI.dll；或设环境变量\n"
        "  YJKAPI_DLL=<完整目录里的 YJKAPI.dll>\n"
        "  YJK_CLRAPI_DLL=<同目录的 ClrYJKAPI.dll>\n"
        "已试过：\n  %s"
        % (_LAST_MODEL_SRC, os.path.join(prefer_dir or "-", "ClrYJKAPI.dll"),
           "\n  ".join("%s  <%s>" % (p, w) for p, w in tried)))


def python_exe():
    """推荐用来跑驱动脚本的解释器（带 pythonnet）。"""
    P = _driver_paths_mod()
    if P is not None:
        info = P.find_python()
        if info["exe"]:
            return info["exe"]
    return sys.executable


def _child_env():
    """子进程的环境：强制 UTF-8 stdio（与本包"调用自家脚本加 `-X utf8`"的约定配套）。

    子进程跑的也是本包自己的脚本，输出里有 ✅ ❌ ⚠ 这类非 cp936 字符；
    不显式指定时它们的 stdout 编码跟随控制台，GBK 控制台下 print 会抛
    UnicodeEncodeError 并以退出码 1 中断 —— 一个其实已经做完的动作会被上层判成失败。
    """
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    return env


def host(workdir, name, ydb=None, prep=True, calc=True, extra=None,
         timeout=None, verbose=True):
    """调用驱动技能的 yjk_auto.py host：新建工程 → 导入 → 预处理 → 计算。

    返回 (returncode, 命令列表)。**注意：判成功要看 设计结果 里的文件 mtime，
    不要看 RunCmd 的返回值**（详见 yjk-auto-drive 技能）。**
    """
    d = require_driver()
    script = os.path.join(d, "scripts", "yjk_auto.py")
    cmd = [python_exe(), "-X", "utf8", "-B", script, "host",
           "--dir", workdir, "--name", name]
    if ydb:
        cmd += ["--import", ydb]
    if prep:
        cmd += ["--prep"]
    if calc:
        cmd += ["--calc"]
    cmd += list(extra or [])
    if verbose:
        print("调用驱动：%s" % " ".join('"%s"' % c if " " in c else c for c in cmd))
    if timeout is None:
        timeout = 5400          # 30 层框筒全算约需十几分钟
    try:
        rc = subprocess.run(cmd, timeout=timeout, env=_child_env()).returncode
    except subprocess.TimeoutExpired:
        print("!! 驱动超时（>%ds）。检查 设计结果 目录是否仍在增长；"
              "必要时提高 timeout 或改用 --inbox 常驻模式。" % timeout)
        rc = -1
    return rc, cmd


def probe_env(verbose=True):
    """跑驱动技能的环境自检（新机器先跑这个）。"""
    d = find_driver()
    if not d:
        return 1
    cmd = [python_exe(), "-X", "utf8", "-B",
           os.path.join(d, "scripts", "yjk_probe.py")]
    if verbose:
        print("环境自检：%s" % " ".join(cmd))
    return subprocess.run(cmd, env=_child_env()).returncode


# --------------------------------------------------- CreateYDB 可用性探测
# ★ 为什么必须**开子进程**试：
#   这条路径上的两种失败都**拦不住**：
#     ① YJK 用自己的**模态 MessageBox** 报错（如「未能加载到yjkTransYDB.dll或其依赖项」）
#        —— 模态期间主窗口被 Disable，之后 IPC/调用**永久挂住**，不是托管异常；
#     ② 进程级 access violation（历史上出现过）。
#   所以只能在子进程里探：崩了/挂了都只是子进程的事。
#
# ★ 更正一段曾经写在这里、后来被证伪的判断：
#   曾有结论说「`CreateYDB()` 在本机根本不可用，空模型也崩（clr.dll 0xc0000005）」。
#   **那是个误判。** 真正的根因是本文件里 `os.add_dll_directory(sdir)` **没有保存返回值**
#   —— `DllDirectory` 对象一被回收就 `RemoveDllDirectory`，目录立刻离开搜索路径，
#   于是 YJK 原生代码 `LoadLibrary("yjkTransYDB.dll")` 找不到文件，弹出上面那个
#   MessageBox 把进程挂死；早期观察到的 AV 是这条链上的次生现象。
#   修法就是本文件顶部的 `pin_native_dll_dir()`（保住句柄 + SetDllDirectoryW + 预加载）。
#   修复后同一条 `CreateYDB()` 在**同一个进程、同一份程序集**下正常写出 ydb
#   （`driver.py createydb` 实测：OK，925696 字节）。
#   对照复现：把 pin/preload 换回空操作 → MessageBox + 挂死。
_CREATEYDB_CODE = r'''
import os, sys, tempfile
sys.path.insert(0, %(here)r)
import driver
api = driver.load_modeling_api(verbose=False)
DF, BP, W = api["DataFunc"], api["BzcPara"], api["writer"]
d = DF()
para = BP()
for k, v in ((0, 9999), (14, 9999), (1, 120), (2, 300), (4, 300), (5, 300), (6, 300)):
    para.setVal(k, v)
std = driver._probe_try(d.StdFlr_Generate, [(3000, 5.0, 2.0, para.GetValString())])
n1 = d.Joint_Generate(std.ID, 0.0, 0.0, 0.0)
n2 = d.Joint_Generate(std.ID, 6000.0, 0.0, 0.0)
ax = d.Axis_Generate(std.ID, n1.ID, n2.ID)
g = d.Grid_Generate(std.ID, n1.ID, n2.ID, ax.ID)
cs = d.ColSect_Def(6, 1, "500,500")
d.column_arrange(n1, cs, 0, 0, 0.0, 0)
d.column_arrange(n2, cs, 0, 0, 0.0, 0)
bs = d.BeamSect_Def(6, 1, "300,600")
d.beam_arrange(g, bs, 0, 0, 0, 0.0)
d.Floor_Assemb(0, std, 1, 3000)
d.DbModel_Assign()
import clr, System.Reflection as R
ct = d.GetType()
f = None
for fl in (R.BindingFlags.NonPublic, R.BindingFlags.Public):
    f = ct.GetField("model", fl | R.BindingFlags.Instance)
    if f is not None:
        break
m = f.GetValue(d)
out = tempfile.mkdtemp(prefix="yjk_createydb_probe_")
print("PROBE_BUILT joints=%%d cols=%%d" %% (len(m.m_Joint), len(m.m_ColSeg)), flush=True)
w = W(m)
ok = w.CreateYDB(out, "probe.ydb")
print("PROBE_RESULT %%s" %% ok, flush=True)
'''


def _probe_try(fn, variants):
    """子进程里用：按候选实参试（7.1/8.1 形参个数不同）。"""
    last = None
    for args in variants:
        try:
            return fn(*args)
        except TypeError as e:
            last = e
    raise SystemExit("StdFlr_Generate 调用失败：%s" % last)


def probe_createydb(timeout=120, verbose=True):
    """在子进程里试一次 `CreateYDB()`，返回 (状态, 说明)。

    状态取值：
      "OK"      —— 真的写出了 ydb（可以把模型落盘交给官方接口）
      "CRASH"   —— 子进程被干掉（access violation）：**绝不能在本进程里调用**
      "TIMEOUT" —— 卡死（模态框或永久阻塞）
      "ERROR"   —— 抛了可捕获的异常
    """
    import tempfile
    code = _CREATEYDB_CODE % {"here": HERE}
    wrapper = ("import tempfile,os\n" + code +
               "\nimport os as _o\n"
               "print('PROBE_FILE', _o.path.getsize(_o.path.join(out,'probe.ydb'))"
               " if _o.path.exists(_o.path.join(out,'probe.ydb')) else 0, flush=True)\n")
    tmp = tempfile.NamedTemporaryFile("w", suffix=".py", delete=False,
                                      encoding="utf-8")
    tmp.write(wrapper)
    tmp.close()
    try:
        r = subprocess.run([python_exe(), "-X", "utf8", "-u", "-B", tmp.name],
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=timeout, env=_child_env())
    except subprocess.TimeoutExpired:
        if verbose:
            print("CreateYDB 探测：**超时 %ds**（卡死/模态框）—— 不要在本进程里调用它"
                  % timeout)
        return "TIMEOUT", "超时 %ds 未返回" % timeout
    finally:
        try:
            os.remove(tmp.name)
        except OSError:
            pass
    out = (r.stdout or "") + (r.stderr or "")
    if r.returncode != 0:
        kind = "CRASH" if r.returncode in (-1073741819, 3221225477, -11) else "ERROR"
        if verbose:
            print("CreateYDB 探测：**%s**（退出码 %s）" % (kind, r.returncode))
            tail = [l for l in out.strip().splitlines() if l.strip()][-3:]
            for l in tail:
                print("   %s" % l[:160])
            print("   → 请改用「骨架 ydb + 序列化」落盘（frame_build.py --scaffold）")
        return kind, "退出码 %s" % r.returncode
    if "PROBE_RESULT" not in out:
        if verbose:
            print("CreateYDB 探测：未拿到结果标记，输出如下：")
            for l in out.strip().splitlines()[-5:]:
                print("   %s" % l[:160])
        return "ERROR", "没有结果标记"

    # ★ 判定只能落在**返回值与产物**上，不能落在"stdout 里出现过某个字符串"上。
    #   子进程打印的是 `PROBE_RESULT <CreateYDB 的返回值>`，老版那句
    #   `if "PROBE_RESULT" in out` 把 `PROBE_RESULT False` 也判成 **OK**；
    #   而 `size`（probe.ydb 的字节数）只进提示语、从不参与判定 ——
    #   文件根本不存在（0 字节）时照样打印 "写出了 0 字节" 并返回 OK。
    #   后果是探测替用户断言"官方建模接口可用"，于是走默认 CreateYDB 路径，
    #   直到写盘那一步才发现库没生成（`frame_build.write_out` 的 577 行才是对的做法：
    #   既接住返回值，又把"文件不存在 / 0 字节"当失败）。
    ok_tok, size = None, 0
    for l in out.splitlines():
        if l.startswith("PROBE_RESULT"):
            parts = l.split(None, 1)
            ok_tok = parts[1].strip() if len(parts) > 1 else ""
        elif l.startswith("PROBE_FILE"):
            try:
                size = int(l.split()[-1])
            except (IndexError, ValueError):
                size = 0
    if ok_tok is None:
        if verbose:
            print("CreateYDB 探测：未拿到结果标记，输出如下：")
            for l in out.strip().splitlines()[-5:]:
                print("   %s" % l[:160])
        return "ERROR", "没有结果标记"
    if ok_tok.lower() not in ("true", "1", "yes"):
        if verbose:
            print("CreateYDB 探测：**失败**（子进程返回 %s，probe.ydb %d 字节）"
                  % (ok_tok or "空", size))
        return "ERROR", "CreateYDB 返回 %s，写出 %d 字节" % (ok_tok or "空", size)
    if size <= 0:
        if verbose:
            print("CreateYDB 探测：**失败**（返回 %s，但 probe.ydb 只有 %d 字节 —— "
                  "没真的写出文件）" % (ok_tok, size))
        return "ERROR", "返回 %s 但只写出 %d 字节" % (ok_tok, size)
    if verbose:
        print("CreateYDB 探测：**OK**（写出了 %d 字节的 probe.ydb）" % size)
    return "OK", "写出 %d 字节" % size


def _utf8_console():
    """让输出在任何控制台编码下都不崩（GBK 下把不可编码字符替换掉）。

    为什么需要：本包会打印 ✅ ❌ ⚠ −(U+2212) ² ³ 等**非 cp936** 字符，
    默认 GBK 控制台下 print 会抛 UnicodeEncodeError 并**以退出码 1 中断**，
    于是一个其实已经成功的任务（比如文件已经落盘）会被上层判成失败。
    errors=replace 让它在 UTF-8 控制台下原样输出、在 GBK 下退化成 ?，都不崩。

    ★ 只在真正的 CLI 入口调用：本文件是**两用**的（既当 CLI 又被 import），
      在模块顶层无条件改 stdout 会污染 import 它的进程（frame_build.py 等）。
    """
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(errors="replace")
        except Exception:
            pass


if __name__ == "__main__":
    _utf8_console()
    import argparse
    ap = argparse.ArgumentParser(description="定位驱动技能 / 准备官方 API / 环境自检")
    ap.add_argument("action",
                    choices=["where", "api", "probe", "python", "createydb",
                             "modelapi"])
    ap.add_argument("--timeout", type=int, default=120,
                    help="createydb 探测的超时（秒）")
    a = ap.parse_args()
    if a.action == "where":
        d = find_driver()
        print("驱动技能目录：%s" % d if d else
              "!! 未找到 yjk-auto-drive 技能\n查找过的位置：\n  " +
              "\n  ".join(os.path.abspath(c) for c in _candidates() if c))
    elif a.action == "api":
        print(ensure_api())
    elif a.action == "python":
        print(python_exe())
    elif a.action == "modelapi":
        print(ensure_model_api(verbose=True))
    elif a.action == "createydb":
        st, why = probe_createydb(timeout=a.timeout)
        print("\n结论：%s（%s）" % (st, why))
        if st != "OK":
            print("→ 官方建模接口在本机写不了盘。建模请走「骨架 ydb + 序列化」路径：")
            print("   python frame_build.py --config ... --sections ... "
                  "--out model.ydb --scaffold <空工程save出的.ymd>")
        sys.exit(0 if st == "OK" else 1)
    else:
        sys.exit(probe_env())
