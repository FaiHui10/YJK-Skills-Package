# -*- coding: utf-8 -*-
r"""把"未随仓库分发"的厂商资料补回本地：官方客户端 DLL + YJK 官方二次开发参考集。

为什么这些文件不在仓库里
------------------------
* `yjk-auto-drive/assets/*.dll`：**厂商二进制**（盈建科官方客户端 `YJKAPI.dll`）。
  二进制不适合放进他人仓库，而它本来就能从官方公开仓库或本机 YJK 安装目录取到。
* `yjk-dev-refs/`：YJK 官方二次开发文档与示例源码的**转载**。其中
  `csharp-yjks`（木兰宽松许可证 v2）、`py-yjks`（Apache-2.0）允许再分发，
  但 `yjkapi_-python` 仓库**未见 LICENSE 声明**，因此本仓库只带索引与来源说明，
  正文请按下面第 2 步从官方公开仓库取。

用法
----
    python fetch_vendor_refs.py --check          # 只体检：缺什么、能不能取
    python fetch_vendor_refs.py --dll            # 只补 DLL
    python fetch_vendor_refs.py --refs           # 只克隆官方参考仓库
    python fetch_vendor_refs.py                  # 两样都补

取不到也能用
------------
* 没有 `assets/YJKAPI.dll`：`scripts/paths.py` 会继续往后面找（环境变量 `YJKAPI_DLL` →
  用户缓存 `~/.yjk-auto/YJKAPI.dll` → YJK 安装目录）。命中哪个 `yjk_probe.py` 会打印。
* 没有 `yjk-dev-refs/`：技能照常运行，只是少一份离线查阅资料。
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "yjk-auto-drive", "assets")
REFS = os.path.join(HERE, "yjk-dev-refs")

# 官方公开仓库（gitee）。按"允许再分发"优先排列。
REPOS = [
    ("csharp-yjks", "https://gitee.com/yjk-opensource/csharp-yjks", "木兰宽松许可证 v2"),
    ("py-yjks", "https://gitee.com/yjk-opensource/py-yjks", "Apache-2.0"),
    # yjkapi_-python 仓库内没有 LICENSE：默认不克隆，需要时自行执行下面打印的命令
]
NO_LICENSE_REPO = ("yjkapi_-python", "https://gitee.com/yjk-opensource/yjkapi_-python")

DLL_REL = os.path.join("不依赖YJK案例", "dll", "YJKAPI.dll")


def find_yjk_dir():
    """找 YJK 安装目录（版本子目录，如 <盘>:\\YJKS\\YJKS_7_1_0）。

    先环境变量，再**枚举本机所有盘符**下的常见位置 —— 不写死盘符
    （与包内 `yjk_api.py::_fallback_roots` 同一口径）。
    """
    for k in ("YJK_DIR", "YJK_HOME"):
        v = os.environ.get(k)
        if v and os.path.isdir(v):
            return v
    drives = []
    sysd = os.environ.get("SystemDrive")
    if sysd:
        drives.append(sysd.rstrip("\\/") + os.sep)
    for L in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        d = "%s:\\" % L
        if d not in drives and os.path.isdir(d):
            drives.append(d)
    cands = []
    for d in drives:
        for sub in ("YJKS", "YJK", "盈建科", "Program Files", "Program Files (x86)"):
            root = os.path.join(d, sub)
            if not os.path.isdir(root):
                continue
            cands.append(root)
            for name in sorted(os.listdir(root)):
                p = os.path.join(root, name)
                if os.path.isdir(p) and name.upper().startswith("YJK"):
                    cands.append(p)
    for p in sorted(cands, reverse=True):          # 版本号大的在前
        if os.path.isdir(os.path.join(p, "STCAD")):
            return p
    return cands[0] if cands else None


def do_dll(verbose=True):
    dst = os.path.join(ASSETS, "YJKAPI.dll")
    if os.path.exists(dst):
        print("[跳过] 已有 %s" % dst)
        return 0
    # 1) 本机 YJK 安装目录（官方控制客户端可能在 STCAD 下）
    yjk = find_yjk_dir()
    if yjk:
        for rel in (os.path.join("STCAD", "YJKAPI.dll"),
                    os.path.join("STCAD", "YJKSControl.dll")):
            src = os.path.join(yjk, rel)
            if os.path.exists(src):
                os.makedirs(ASSETS, exist_ok=True)
                shutil.copy2(src, dst)
                print("[OK] 从本机 YJK 安装目录复制：%s" % src)
                print("     注意：安装目录那份可能不含 YJKSControl 类型，")
                print("     跑一次 yjk_probe.py 看它是否命中可用的那份。")
                return 0
    # 2) 用户缓存
    cache = os.path.join(os.path.expanduser("~"), ".yjk-auto", "YJKAPI.dll")
    if os.path.exists(cache):
        os.makedirs(ASSETS, exist_ok=True)
        shutil.copy2(cache, dst)
        print("[OK] 从用户缓存复制：%s" % cache)
        return 0
    print("[缺] 没找到 YJKAPI.dll。三种办法（任选）：")
    print("     1) 从官方仓库取：git clone https://gitee.com/yjk-opensource/csharp-yjks")
    print("        然后复制 `%s` 到 %s" % (DLL_REL, ASSETS))
    print("     2) 设环境变量 YJKAPI_DLL=<你手上那份 YJKAPI.dll 的完整路径>")
    print("     3) 找人在 Windows 上从 YJK 安装目录 STCAD 下取一份")
    return 1


def do_refs(verbose=True):
    if not shutil.which("git"):
        print("[缺] 没有 git，无法克隆官方参考仓库。")
        return 1
    rc = 0
    for name, url, lic in REPOS:
        dst = os.path.join(REFS, "_src", name)
        if os.path.isdir(os.path.join(dst, ".git")):
            print("[跳过] 已存在 %s" % dst)
            continue
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        print("[克隆] %s（%s）-> %s" % (url, lic, dst))
        r = subprocess.run(["git", "clone", "--depth", "1", url, dst],
                           text=True, encoding="utf-8", errors="replace")
        if r.returncode != 0:
            print("       失败：git clone 返回 %d（网络不通？）" % r.returncode)
            rc = 1
    print("")
    print("提示：`%s` 仓库内**没有 LICENSE 文件**，本脚本默认不取。" % NO_LICENSE_REPO[0])
    print("      需要 8.x 新 API 文档/案例时请自行确认授权后执行：")
    print("        git clone --depth 1 %s %s"
          % (NO_LICENSE_REPO[1], os.path.join(REFS, "_src", NO_LICENSE_REPO[0])))
    print("")
    print("参考集正文的整理口径与来源清单见 %s" % os.path.join(REFS, "README.md"))
    return rc


def do_check():
    dll = os.path.join(ASSETS, "YJKAPI.dll")
    print("YJKAPI.dll        : %s" % ("有" if os.path.exists(dll) else "缺"))
    print("yjk-dev-refs/     : %s" % ("有" if os.path.isdir(os.path.join(REFS, "04-接口说明"))
                                      else "缺（仓库内只带索引与来源说明）"))
    print("YJK 安装目录      : %s" % (find_yjk_dir() or "未找到"))
    print("git               : %s" % (shutil.which("git") or "未安装"))
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dll", action="store_true", help="只补官方客户端 DLL")
    ap.add_argument("--refs", action="store_true", help="只克隆官方参考仓库")
    ap.add_argument("--check", action="store_true", help="只体检")
    a = ap.parse_args()
    if a.check:
        return do_check()
    rc = 0
    if a.dll or not (a.dll or a.refs):
        rc |= do_dll()
    if a.refs or not (a.dll or a.refs):
        rc |= do_refs()
    return rc


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:                                         # noqa: BLE001
            pass
    sys.exit(main())
