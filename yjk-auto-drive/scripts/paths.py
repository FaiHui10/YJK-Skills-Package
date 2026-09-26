# -*- coding: utf-8 -*-
r"""跨机器自适应定位：YJK 安装目录 / 可执行文件 / Config.ini / 官方客户端 DLL / 带 clr 的 Python。

设计原则
--------
**一个本机路径都不写死。** 所有定位都按"优先级候选链"逐个试，命中即用；
每条链的最后都有一档"扫盘兜底"（限制深度，避免慢）。找不到时**不抛异常**，
而是返回 None 并把「该做什么」写进 notes，交给调用方打印给用户。

覆盖的场景：
  * 用户把 YJK 装在 C:/D:/E: 任意盘、任意目录名（YJKS_7_1_0 / YJK2024 / 盈建科…）
  * 只装了 8.x、没装 7.1（会提示版本不匹配）
  * 用户从未运行过 YJK（安装位置只能靠注册表/扫盘）
  * 官方客户端 DLL 放在技能 assets / 用户缓存 / 官方仓库检出目录 / YJK 安装目录
  * Python 解释器没有 pythonnet（提示用 setup_env.py 建隔离环境）
  * **技能被装进任意 agent/IDE 的用户级技能目录**（不写死厂商名，见 skill_dir_candidates）

对外主要函数
------------
  find_yjk_install()      -> dict(exe, launcher, root, version, source)
  find_config_inis()      -> [(path, {flag: 'True'/'False'/None, has_section: bool}), ...]
  find_yjkapi_dll()       -> dict(path, kind, source, notes)
  python_candidates()     -> [解释器候选路径, ...]（含各 agent 托管环境，不写死厂商名）
  find_python()           -> dict(exe, has_clr, source, candidates)
  skill_dir_candidates()  -> [技能目录候选, ...]（跨 agent 找底座用）
  find_skill_dir()        -> 技能目录 或 None
  doctor()                -> 汇总字典（供 yjk_probe.py 打印）
"""
from __future__ import annotations

import glob
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(HERE)
ASSETS = os.path.join(SKILL_DIR, "assets")

# 用户级缓存目录（跨技能共用；放 DLL / 环境记录，不污染技能目录的只读副本）
USER_CACHE = os.path.join(os.path.expanduser("~"), ".yjk-auto")

EXE_NAMES = ("yjks.exe",)
LAUNCHER_NAMES = ("YjkLauncher.exe", "YjkLauncher")

# 扫描兜底时用到的目录名特征（不区分大小写，含中文常见命名）
DIR_HINTS = ("yjks", "yjk", "盈建科")

# 官方客户端类型名候选（不同来源的 DLL 命名空间不同）
CONTROL_TYPES = ("YJKIPC.YJKSControl", "YJKSControl")


def _dedup(seq):
    out, seen = [], set()
    for x in seq:
        if not x:
            continue
        k = os.path.normcase(os.path.abspath(x))
        if k in seen:
            continue
        seen.add(k)
        out.append(os.path.abspath(x))
    return out


def _ps_exe():
    """定位 powershell.exe。

    PATH 里不一定有 powershell（`shutil.which` 可能返回 None），
    直接 `subprocess.run(["powershell", ...])` 会抛 FileNotFoundError —— 若被吞掉，
    注册表等探测就静默失效。故按 SystemRoot 拼全路径兜底。
    """
    cands = [shutil.which("powershell")]
    sysroot = os.environ.get("SystemRoot") or r"C:\Windows"
    cands.append(os.path.join(sysroot, "System32", "WindowsPowerShell", "v1.0", "powershell.exe"))
    cands.append(r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe")
    return next((c for c in cands if c and os.path.exists(c)), "powershell")


def _from_ps(cmd, timeout=30):
    try:
        r = subprocess.run([_ps_exe(), "-NoProfile", "-Command", cmd],
                           capture_output=True, text=True, timeout=timeout,
                           encoding="utf-8", errors="replace")
        return r.stdout or ""
    except Exception:                                          # noqa: BLE001
        return ""


# ================================================================ YJK 安装目录
def _roots_from_env():
    out = []
    for k in ("YJK_DIR", "YJK_ROOT", "YJK_HOME", "YJKS_DIR", "YJK_PATH", "YJK_INSTALL"):
        v = os.environ.get(k)
        if v:
            out.append(v)
    return out


def _roots_from_running():
    """运行中的 yjks.exe / YjkLauncher.exe 所在目录 —— 最可靠的来源。"""
    out = []
    try:
        import psutil
        for pr in psutil.process_iter(["name", "exe"]):
            n = (pr.info.get("name") or "").lower()
            if n in ("yjks.exe", "yjklauncher.exe"):
                e = pr.info.get("exe")
                if e:
                    out.append(os.path.dirname(e))
    except Exception:                                          # noqa: BLE001
        pass
    if not out:
        txt = _from_ps(
            "Get-CimInstance Win32_Process -Filter \"Name='yjks.exe' or "
            "Name='YjkLauncher.exe'\" | ForEach-Object { $_.ExecutablePath }")
        out += [os.path.dirname(x.strip()) for x in txt.splitlines() if x.strip()]
    return _dedup(out)


def _roots_from_registry():
    out = []
    keys = [
        r"HKLM:\SOFTWARE\WOW6432Node\yjkSoft\*",
        r"HKLM:\SOFTWARE\yjkSoft\*",
        r"HKCU:\SOFTWARE\yjkSoft\*",
    ]
    for k in keys:
        txt = _from_ps("(Get-ItemProperty '%s' -ErrorAction SilentlyContinue)"
                       ".InstallPath" % k)
        out += [x.strip() for x in txt.splitlines() if x.strip()]
    # 卸载信息里常带 InstallLocation
    txt = _from_ps(
        "Get-ItemProperty 'HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\"
        "Uninstall\\*','HKLM:\\SOFTWARE\\WOW6432Node\\Microsoft\\Windows\\"
        "CurrentVersion\\Uninstall\\*' -ErrorAction SilentlyContinue | "
        "Where-Object { $_.DisplayName -match 'YJK|盈建科' } | "
        "ForEach-Object { $_.InstallLocation }")
    out += [x.strip() for x in txt.splitlines() if x.strip()]
    return _dedup(out)


def _roots_by_scan(max_depth=3, max_entries=4000):
    """扫盘兜底：在各盘根下按目录名特征找含 yjks.exe 的目录。"""
    out, seen = [], 0
    drives = [d + ":\\" for d in "CDEFGH" if os.path.isdir(d + ":\\")]
    common = []
    for d in drives:
        common += [os.path.join(d, "YJKS"), os.path.join(d, "YJK"),
                   os.path.join(d, "盈建科"),
                   os.path.join(d, "Program Files"),
                   os.path.join(d, "Program Files (x86)"),
                   os.path.join(d, "ProgramData")]
    roots0 = [c for c in common if os.path.isdir(c)]
    for base in roots0:
        for dp, dn, fn in os.walk(base):
            seen += 1
            if seen > max_entries:
                return _dedup(out)
            depth = dp[len(base):].count(os.sep)
            if depth >= max_depth:
                dn[:] = []
            # 命中：就是安装目录本体
            if any(f.lower() in EXE_NAMES for f in fn):
                out.append(dp)
                dn[:] = []
                continue
            # 剪枝：与 YJK 无关的目录不再深入
            if depth >= 1:
                dn[:] = [x for x in dn
                         if any(h in x.lower() for h in DIR_HINTS)]
    return _dedup(out)


def _version_of(root):
    """从目录名或 Config.ini / AuthInformation.ini 里推版本号。"""
    m = re.search(r"(\d+)[._]?(\d+)[._]?(\d+)", os.path.basename(root))
    if m:
        return "%s.%s.%s" % m.groups()
    m = re.search(r"(\d+)\.(\d+)", os.path.basename(root))
    if m:
        return "%s.%s" % m.groups()
    for pat in ("*.ini", "*.INI"):
        for p in glob.glob(os.path.join(root, pat))[:6]:
            try:
                t = open(p, "rb").read().decode("gbk", "replace")
            except OSError:
                continue
            mm = re.search(r"(?:Version|版本)\s*=\s*([\d.]+)", t)
            if mm:
                return mm.group(1)
    return None


def all_install_roots():
    """所有候选安装根（**不提前返回**，四条链全跑）。

    给「需要遍历多个版本目录」的场景用（例如找 STCAD 程序集：
    环境变量指定的那个版本未必装全，扫盘扫到的另一个版本反而齐）。
    """
    out = []
    for fn in (_roots_from_env, _roots_from_running,
               _roots_from_registry, _roots_by_scan):
        try:
            out += fn()
        except Exception:                                      # noqa: BLE001
            pass
    return _dedup(out)


def find_yjk_install():
    """返回 {exe, launcher, root, version, source, candidates}。

    root 可能命中"安装目录"或"安装目录的上级"（扫盘时只认含 yjks.exe 的目录，
    所以 root 一定是可直接 Popen yjks.exe 的那一级）。
    """
    info = {"exe": None, "launcher": None, "root": None,
            "version": None, "source": None, "candidates": []}
    chains = [("环境变量", _roots_from_env),
              ("运行中的进程", _roots_from_running),
              ("注册表", _roots_from_registry),
              ("扫盘兜底", _roots_by_scan)]

    for label, fn in chains:
        try:
            roots = fn()
        except Exception:                                      # noqa: BLE001
            roots = []
        info["candidates"] += roots
        for r in roots:
            exe = os.path.join(r, "yjks.exe")
            if os.path.exists(exe):
                info.update(root=r, exe=exe, source=label)
                info["version"] = _version_of(r)
                for ln in LAUNCHER_NAMES:
                    lp = os.path.join(r, ln)
                    if os.path.exists(lp):
                        info["launcher"] = lp
                        break
                return info
        # 该链未直接命中：候选目录可能指向"上级"，再补一层常见子目录名
        for r in roots:
            for sub in ("", "YJKS_7_1_0", "YJKS_8_1_0"):
                exe = os.path.join(r, sub, "yjks.exe")
                if os.path.exists(exe):
                    root = os.path.join(r, sub)
                    info.update(root=root, exe=exe, source=label + "(子目录)")
                    info["version"] = _version_of(root)
                    lp = os.path.join(root, "YjkLauncher.exe")
                    info["launcher"] = lp if os.path.exists(lp) else None
                    return info
            # 该目录下所有一级子目录再试一遍
            try:
                subs = [d for d in os.listdir(r)
                        if os.path.isdir(os.path.join(r, d))]
            except OSError:
                subs = []
            for d in subs:
                root = os.path.join(r, d)
                exe = os.path.join(root, "yjks.exe")
                if os.path.exists(exe):
                    info.update(root=root, exe=exe, source=label + "(子目录名未知)")
                    info["version"] = _version_of(root)
                    lp = os.path.join(root, "YjkLauncher.exe")
                    info["launcher"] = lp if os.path.exists(lp) else None
                    return info
    return info


# ================================================================ Config.ini
def find_config_inis():
    """返回 [(path, {flag, has_section})] —— 逐个列出所有候选 Config.ini 及其 Flag。

    位置链：环境变量 YJK_CONFIG -> 安装目录/Config.ini ->
            %ProgramData%\\yjkSoft\\*\\Config.ini 与 \\*\\YJKS\\Config.ini -> 扫 ProgramData。
    """
    cands = []
    v = os.environ.get("YJK_CONFIG")
    if v:
        cands.append(v)
    ins = find_yjk_install()
    if ins["root"]:
        cands.append(os.path.join(ins["root"], "Config.ini"))
    for base in filter(None, [os.environ.get("ProgramData"),
                              r"C:\ProgramData"]):
        if not os.path.isdir(base):
            continue
        root = os.path.join(base, "yjkSoft")
        if os.path.isdir(root):
            for d in sorted(os.listdir(root)):
                dd = os.path.join(root, d)
                if not os.path.isdir(dd):
                    continue
                cands.append(os.path.join(dd, "Config.ini"))
                cands.append(os.path.join(dd, "YJKS", "Config.ini"))
                cands += glob.glob(os.path.join(dd, "*", "Config.ini"))

    out = []
    for p in _dedup(cands):
        if not os.path.exists(p):
            continue
        try:
            t = open(p, "rb").read().decode("gbk", "replace")
        except OSError:
            continue
        sec = re.search(r"\[YJKSControl\]", t)
        fl = re.search(r"\[YJKSControl\][^\[]*?Flag\s*=\s*(\w+)", t, re.S)
        out.append((p, {"has_section": bool(sec),
                        "flag": fl.group(1) if fl else None}))
    return out


def config_flag_ok():
    """是否存在任一 Flag=True 的 Config.ini（= 启动 yjks 即自动开 IPC）。"""
    for p, st in find_config_inis():
        if st["flag"] and st["flag"].lower() == "true":
            return True, p
    return False, None


def write_config_flag(value="True"):
    """把 [YJKSControl] Flag=... 写进所有已发现的 Config.ini（没有就补整段）。"""
    done = []
    for p, st in find_config_inis():
        try:
            t = open(p, "rb").read().decode("gbk", "replace")
        except OSError:
            continue
        if "[YJKSControl]" in t:
            if re.search(r"(\[YJKSControl\][^\[]*?Flag\s*=\s*)\w+", t, re.S):
                t = re.sub(r"(\[YJKSControl\][^\[]*?Flag\s*=\s*)\w+",
                           r"\g<1>" + value, t, flags=re.S)
            else:
                t = re.sub(r"(\[YJKSControl\][^\[]*?\n)",
                           r"\1Flag = " + value + "\n", t, count=1, flags=re.S)
        else:
            t = t.rstrip("\r\n") + "\n\n[YJKSControl]\nFlag = " + value + "\n"
        try:
            open(p, "wb").write(t.encode("gbk", "replace"))
            done.append(p)
        except OSError:
            pass
    return done


# ================================================================ 官方客户端 DLL
def _dll_kind(path):
    """判断该 DLL 是否含可用的 YJKSControl 类型；返回 (kind, types)。"""
    try:
        import clr                                            # noqa: F401
        from System.Reflection import Assembly
        asm = Assembly.LoadFile(path)
        names = [t.FullName for t in asm.GetTypes()]
    except Exception:                                          # noqa: BLE001
        return None, []
    for ct in CONTROL_TYPES:
        if ct in names:
            return ct, names
    return None, names


def find_yjkapi_dll(explicit=None, verify=True):
    """定位官方客户端 YJKAPI.dll。

    优先级：显式传入 -> 环境变量 YJKAPI_DLL -> 技能 assets/ -> 用户缓存
            -> YJK 安装目录 STCAD/ -> 官方仓库检出目录 -> 全盘浅扫。

    kind == 'YJKIPC.YJKSControl' 是官方仓库（csharp-yjks 7.1 分支）版本，首选；
    kind == 'YJKSControl' 是 YJK 安装目录自带的 STCAD 版本，RunCmd 是 3 参（含 out），
    作为兜底（yjk_auto.Client 会自动适配签名）。
    """
    info = {"path": None, "kind": None, "source": None, "notes": []}
    cands = []
    if explicit:
        cands.append(("命令参数", explicit))
    if os.environ.get("YJKAPI_DLL"):
        cands.append(("环境变量 YJKAPI_DLL", os.environ["YJKAPI_DLL"]))
    cands.append(("技能 assets", os.path.join(ASSETS, "YJKAPI.dll")))
    cands.append(("用户缓存", os.path.join(USER_CACHE, "YJKAPI.dll")))
    ins = find_yjk_install()
    if ins["root"]:
        # 安装目录自带件只作兜底：STCAD\YJKSControl.dll 含类型 `YJKSControl`
        # （RunCmd 为 3 参含 out），STCAD\YJKAPI.dll **没有**控制类型。
        cands.append(("YJK 安装目录 STCAD/控制件",
                      os.path.join(ins["root"], "STCAD", "YJKSControl.dll")))
        cands.append(("YJK 安装目录 STCAD", os.path.join(ins["root"], "STCAD", "YJKAPI.dll")))
        cands.append(("YJK 安装目录", os.path.join(ins["root"], "YJKAPI.dll")))
    for base in (os.path.expanduser("~"),):
        for pat in ("*/csharp-yjks*/**/YJKAPI.dll", "*/yjk*/**/YJKAPI.dll",
                    "*/*/不依赖YJK案例/dll/YJKAPI.dll"):
            cands += [("用户目录检出", p) for p in glob.glob(
                os.path.join(base, pat), recursive=True)[:10]]

    seen = set()
    for src, p in cands:
        if not p or not os.path.exists(p):
            continue
        k = os.path.normcase(os.path.abspath(p))
        if k in seen:
            continue
        seen.add(k)
        if not verify:
            info.update(path=p, kind="unverified", source=src)
            return info
        kind, names = _dll_kind(p)
        if kind:
            info.update(path=p, kind=kind, source=src)
            if kind == "YJKSControl":
                info["notes"].append(
                    "该 DLL 来自 YJK 安装目录（%s），RunCmd 为 3 参重载；"
                    "官方仓库 7.1 分支的 YJKIPC.YJKSControl 更稳，建议放到 %s"
                    % (src, os.path.join(ASSETS, "YJKAPI.dll")))
            return info
        info["notes"].append("跳过 %s（%s）：无 YJKSControl 类型" % (p, src))
    info["notes"].append(
        "未找到可用客户端 DLL。请取 gitee yjk-opensource/csharp-yjks **7.1 分支**的 "
        "不依赖YJK案例/dll/YJKAPI.dll，放到 %s（或设环境变量 YJKAPI_DLL）"
        % os.path.join(ASSETS, "YJKAPI.dll"))
    return info


# ================================================ 家目录一级子目录 / 各 agent 的技能家（与厂商无关）
# 为什么必须「枚举」而不是「再抄一个厂商名」：
#   本包原来只认一个厂商的家目录布局（`~/.workbuddy-ai/skills/`、
#   `~/.workbuddy-ai/binaries/python/...`）。换到别的 agent/IDE 上那些目录**根本不存在**，
#   而用户最自然的装法恰恰是"把整套技能丢进我的 agent 技能目录"——于是底座明明就在旁边，
#   却报「找不到 yjk-auto-drive」；用户明明已经在自己的 agent 环境里装好了 pythonnet，
#   却报「没找到带 pythonnet 的解释器」，白重装一遍。再抄第二个厂商名只是把问题推迟到
#   第三个 agent，所以这里改成**扫家目录下的一级子目录**：任何 `~/.<任意 agent>/…`
#   都能命中，且不需要知道对方叫什么。
_HOME_SCAN_CAP = 40             # 只取前 N 个一级子目录：家目录很大时也不能拖慢自检


def _home_subdirs(base, cap=_HOME_SCAN_CAP):
    """`base` 下的一级子目录名 —— **先全量排序、再取前 cap 个**。

    为什么必须先排序再截断：`os.scandir` 的返回顺序是文件系统的顺序（换机器、加删文件
    都会变），若"边扫边收满 cap 就停"，被留下的那 40 个是随机的 —— 同一台机器两次跑
    可能命中不同目录。排序后再截断才是**确定的子集**：候选顺序可复现，故障可复现。
    只列一级、**不递归**（递归家目录在大机器上要几十秒，定位一个技能/解释器不该这么贵）。

    目录不存在 / 无权限一律返回 []：这里是"猜位置"，猜不到就继续走下一档候选，
    绝不能因为某个目录读不了而让整条定位链崩掉。
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


def _cwd():
    """当前目录（进程的工作目录被删掉时 os.getcwd() 会抛 OSError）。"""
    try:
        return os.getcwd()
    except OSError:
        return None


def skill_dir_candidates(skill_name):
    """**与厂商无关**地猜某个技能装在哪，返回候选目录（大多不存在，交给调用方判定）。

    覆盖 `~/.<任意 agent>/skills/<技能名>` 这一类用户级装法，外加
    `~/.config/<任意 agent>/skills/<技能名>`（XDG 风格）、
    `~/.agent-skills`、`~/.skills`、`<cwd>/.skills`（项目级装法）。
    业务技能要靠它找到底座 `yjk-auto-drive`，所以这里**不写死任何厂商目录名**。
    """
    home = os.path.expanduser("~")
    out = []
    for base in (home, os.path.join(home, ".config")):
        for d in _home_subdirs(base):
            p = os.path.join(base, d)
            out.append(os.path.join(p, "skills", skill_name))       # .<agent>/skills/<名>
            out.append(os.path.join(p, skill_name))                 # .<agent>/<名>
            for x in _home_subdirs(os.path.join(p, "skills")):      # .<agent>/skills/<分类>/<名>
                out.append(os.path.join(p, "skills", x, skill_name))
    out.append(os.path.join(home, ".agent-skills", skill_name))
    out.append(os.path.join(home, ".skills", skill_name))
    cwd = _cwd()
    if cwd:
        out.append(os.path.join(cwd, ".skills", skill_name))
    return _dedup(out)


def find_skill_dir(skill_name, marker="SKILL.md"):
    """按候选链找某个技能目录（判据：目录里同时有 `marker` 与 `scripts/`）。

    找不到返回 None —— 与别的定位函数一致，不抛异常，由调用方打印「该做什么」。
    """
    for c in skill_dir_candidates(skill_name):
        if os.path.isfile(os.path.join(c, marker)) and \
                os.path.isdir(os.path.join(c, "scripts")):
            return c
    return None


# ================================================================ Python 解释器
def _has_clr(exe):
    try:
        r = subprocess.run([exe, "-X", "utf8", "-B", "-c", "import clr;print('CLR-OK')"],
                           capture_output=True, text=True, timeout=60,
                           encoding="utf-8", errors="replace")
        return "CLR-OK" in (r.stdout or "")
    except Exception:                                          # noqa: BLE001
        return False


def _agent_env_python_candidates(home):
    """各 agent 托管环境的 python.exe —— 形状照抄实测过的目录布局，但不写死厂商名。

    覆盖三种实测/常见的布局：
      * `<家>/.<agent>/venv/Scripts/python.exe`            —— 自建 venv
      * `<家>/.<agent>/binaries/python/<ver>/Scripts/python.exe`
      * `<家>/.<agent>/binaries/python/envs/<env>/Scripts/python.exe`
    以及 POSIX 侧的 `bin/python`（同机 WSL/Git-Bash 装的解释器也能用）。
    """
    out = []
    for d in _home_subdirs(home):
        base = os.path.join(home, d)
        out.append(os.path.join(base, "venv", "Scripts", "python.exe"))
        out.append(os.path.join(base, "venv", "bin", "python"))
        pydir = os.path.join(base, "binaries", "python")
        for sub in _home_subdirs(pydir):            # <ver> / envs 同级
            out.append(os.path.join(pydir, sub, "Scripts", "python.exe"))
            out.append(os.path.join(pydir, sub, "bin", "python"))
            for env in _home_subdirs(os.path.join(pydir, sub)):   # envs/<env>
                out.append(os.path.join(pydir, sub, env, "Scripts", "python.exe"))
                out.append(os.path.join(pydir, sub, env, "bin", "python"))
    return out


def _python_candidates():
    out = []
    for k in ("YJK_PY", "YJK_PYTHON"):
        if os.environ.get(k):
            out.append(os.environ[k])
    # 本技能自建环境（setup_env.py 会装到这里）
    for p in (os.path.join(USER_CACHE, "venv", "Scripts", "python.exe"),
              os.path.join(USER_CACHE, "venv", "bin", "python")):
        out.append(p)
    # 各 agent 托管环境（与厂商无关地枚举；通常已装 pythonnet）
    home = os.path.expanduser("~")
    out += _agent_env_python_candidates(home)
    # 历史遗留路径，保留以不破坏现有用户（唯一带厂商名的一档，去掉它其余各档照样工作）
    out.append(os.path.join(home, ".workbuddy-ai", "binaries", "python",
                            "envs", "default", "Scripts", "python.exe"))
    out.append(os.path.join(home, ".workbuddy-ai", "binaries", "python",
                            "envs", "default", "bin", "python"))
    out.append(sys.executable)
    out.append(shutil.which("python"))
    out.append(shutil.which("python3"))
    for pat in (r"C:\Python3*\python.exe", r"C:\ProgramData\anaconda3\python.exe",
                os.path.join(home, "anaconda3", "python.exe"),
                os.path.join(home, "miniconda3", "python.exe"),
                r"C:\Program Files\Python3*\python.exe"):
        out += glob.glob(pat)
    return _dedup(out)


def python_candidates():
    """公开版：所有候选解释器（环境变量 → 自建 venv → 各 agent 托管环境 → PATH → 常见安装位）。

    整条候选链**只在这里维护一处**；setup_env.py 等脚本应当复用它，
    不要各自再抄一份写死的路径表。
    """
    return _python_candidates()


def find_python(probe=True):
    """找带 pythonnet(clr) 的解释器。probe=False 时只按路径存在性返回第一个。"""
    info = {"exe": None, "has_clr": False, "source": None, "candidates": []}
    for p in _python_candidates():
        if not p or not os.path.exists(p):
            continue
        info["candidates"].append(p)
        if p == sys.executable:
            info["source"] = "当前解释器"
        if not probe:
            info["exe"] = p
            return info
        if info["exe"] is None:
            info["exe"] = p                              # 记下第一个存在的，作兜底
        if _has_clr(p):
            info.update(exe=p, has_clr=True,
                        source=info["source"] or "候选链命中")
            return info
    return info


# ================================================================ 汇总
def doctor(proj_dir=None, dll=None):
    ins = find_yjk_install()
    cfgs = find_config_inis()
    api = find_yjkapi_dll(dll)
    py = find_python()
    has_flag, flag_path = config_flag_ok()
    running = []
    try:
        import psutil
        running = [pr.info["pid"] for pr in psutil.process_iter(["name"])
                   if (pr.info.get("name") or "").lower() == "yjks.exe"]
    except Exception:                                          # noqa: BLE001
        pass
    return {
        "yjk": ins, "config_inis": cfgs, "config_flag_ok": has_flag,
        "config_flag_path": flag_path, "yjkapi": api, "python": py,
        "yjks_running": running, "proj_dir": proj_dir,
        "user_cache": USER_CACHE, "assets": ASSETS,
    }


if __name__ == "__main__":
    import json
    print(json.dumps(doctor(), ensure_ascii=False, indent=1))
