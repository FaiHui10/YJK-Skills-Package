# -*- coding: utf-8 -*-
r"""在新电脑上一键准备运行环境：建隔离 venv + 装依赖（pythonnet / openpyxl / psutil）。

为什么要隔离环境
----------------
驱动 YJK 用到 pythonnet（clr）去反射调用官方 DLL。系统 Python 未必有，直接往系统里
装包也可能污染用户环境。本脚本在 `~/.yjk-auto/venv` 建一个专用环境，只装三件事。

用法
----
  python setup_env.py                 # 自动找基础 Python → 建 venv → 装依赖 → 自检
  python setup_env.py --python <exe>  # 指定基础解释器
  python setup_env.py --check         # 只体检，不安装

完成后它会打印「该用哪个 python 跑 yjk_auto.py」，并把这个路径写进
`~/.yjk-auto/python.txt`，后续脚本会优先复用它。
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import paths as P                                              # noqa: E402

PKGS = ["pythonnet", "openpyxl", "psutil"]
VENV = os.path.join(P.USER_CACHE, "venv")
PY_RECORD = os.path.join(P.USER_CACHE, "python.txt")


def _run(cmd, **kw):
    kw.setdefault("capture_output", True)
    kw.setdefault("text", True)
    kw.setdefault("encoding", "utf-8")
    kw.setdefault("errors", "replace")
    kw.setdefault("timeout", 900)
    return subprocess.run(cmd, **kw)


def base_pythons(explicit=None):
    out = []
    if explicit:
        out.append(explicit)
    for k in ("YJK_BASE_PY", "PYTHON"):
        if os.environ.get(k):
            out.append(os.environ[k])
    # 候选链复用 paths.py（那里统一维护：自建 venv / 托管环境 / PATH / 常见安装位）
    out += P.python_candidates()
    # py 启动器（Windows）能报告所有已装版本
    py = shutil.which("py")
    if py:
        try:
            r = _run([py, "-0p"])
            for ln in (r.stdout or "").splitlines():
                for tok in ln.replace("\t", " ").split():
                    if tok.lower().endswith("python.exe") and os.path.exists(tok):
                        out.append(tok)
        except Exception:                                      # noqa: BLE001
            pass
    seen, res = set(), []
    for p in out:
        if not p:
            continue
        k = os.path.normcase(os.path.abspath(p))
        if k in seen or not os.path.exists(p):
            continue
        seen.add(k)
        res.append(os.path.abspath(p))
    return res


def venv_python():
    for p in (os.path.join(VENV, "Scripts", "python.exe"),
              os.path.join(VENV, "bin", "python")):
        if os.path.exists(p):
            return p
    return None


def has_clr(exe):
    try:
        r = _run([exe, "-X", "utf8", "-B", "-c", "import clr;print('CLR-OK')"], timeout=120)
        return "CLR-OK" in (r.stdout or "")
    except Exception:                                          # noqa: BLE001
        return False


def check_only():
    print("=== 体检 ===")
    vp = venv_python()
    print("隔离环境 : %s" % (vp or "（尚未创建）%s" % VENV))
    if vp:
        print("  clr    : %s" % ("有" if has_clr(vp) else "无"))
        for m in ("openpyxl", "psutil"):
            # -X utf8：子进程按 UTF-8 输出，与本文件 `_run()` 的 encoding="utf-8" 对齐
            r = _run([vp, "-X", "utf8", "-c",
                      "import %s;print(getattr(%s,'__version__','?'))" % (m, m)], timeout=60)
            txt = (r.stdout or r.stderr or "?").strip().splitlines()
            print("  %-9s: %s" % (m, txt[0] if txt else "?"))
    if os.path.exists(PY_RECORD):
        # utf-8-sig：这个记录文件**是给人看的**，用户很可能用记事本打开/另存过，
        # 而记事本存 UTF-8 会带 BOM —— 用 utf-8 读会把 BOM 当成路径的第一个字符。
        print("记录     : %s -> %s"
              % (PY_RECORD, open(PY_RECORD, encoding="utf-8-sig").read().strip()))
    print()
    print("现有解释器候选：")
    for p in base_pythons():
        print("  %-70s clr=%s" % (p, has_clr(p)))
    return 0


def main():
    _utf8_console()
    ap = argparse.ArgumentParser()
    ap.add_argument("--python", help="基础解释器路径")
    ap.add_argument("--check", action="store_true", help="只体检不安装")
    ap.add_argument("--force", action="store_true", help="已存在也重建")
    a = ap.parse_args()

    if a.check:
        return check_only()

    os.makedirs(P.USER_CACHE, exist_ok=True)

    # 1) 已有可用环境直接复用
    vp = venv_python()
    if vp and has_clr(vp) and not a.force:
        print("已存在可用隔离环境：%s\n（如需重建加 --force）" % vp)
        open(PY_RECORD, "w", encoding="utf-8").write(vp)
        return 0

    # 2) 挑基础解释器
    base = a.python
    if not base:
        cands = base_pythons()
        if not cands:
            print("!! 机器上找不到任何 Python。请先安装 Python 3.10+ "
                  "（https://www.python.org/downloads/，勾选 Add to PATH）")
            return 2
        # 优先 3.10~3.13（pythonnet 对新版支持有滞后）
        def score(p):
            r = _run([p, "-X", "utf8", "-c",
                      "import sys;print('%d%d'%sys.version_info[:2])"], timeout=60)
            v = (r.stdout or "").strip()
            return (v not in ("310", "311", "312", "313"), p)
        cands.sort(key=score)
        base = cands[0]
        print("选用基础解释器：%s" % base)

    if a.force and os.path.isdir(VENV):
        print("重建：删除 %s" % VENV)
        shutil.rmtree(VENV, ignore_errors=True)

    # 3) 建 venv
    print("创建隔离环境：%s" % VENV)
    r = _run([base, "-m", "venv", VENV], timeout=600)
    if r.returncode != 0:
        print("!! 建 venv 失败：\n%s\n%s" % (r.stdout, r.stderr))
        return 3
    vp = venv_python()
    if not vp:
        print("!! venv 建好了但找不到 python.exe")
        return 3

    # 4) 装依赖
    print("安装依赖：%s" % " ".join(PKGS))
    r = _run([vp, "-m", "pip", "install", "--disable-pip-version-check",
              "--upgrade", "pip"], timeout=900)
    r = _run([vp, "-m", "pip", "install", "--disable-pip-version-check"] + PKGS,
             timeout=1800)
    print((r.stdout or "")[-1500:])
    if r.returncode != 0:
        print("!! 安装失败：\n%s" % (r.stderr or "")[-1500:])
        print("   离线机器可用国内镜像：%s -m pip install -i "
              "https://pypi.tuna.tsinghua.edu.cn/simple %s" % (vp, " ".join(PKGS)))
        return 4

    # 5) 自检
    print("\n=== 自检 ===")
    ok = has_clr(vp)
    print("pythonnet(clr): %s" % ("可用" if ok else "不可用"))
    if not ok:
        print("!! clr 仍不可用。若基础解释器是 3.14+，pythonnet 可能尚未支持，"
              "请改用 3.10~3.13 的解释器：python setup_env.py --python <3.13的python.exe>")
        return 5
    open(PY_RECORD, "w", encoding="utf-8").write(vp)      # 无 BOM：别的脚本按 utf-8 读它
    print()
    print("*** 环境就绪 ***")
    print("后续请用这个解释器：")
    print('  "%s" yjk_probe.py' % vp)
    print('  "%s" yjk_auto.py host --dir <工作目录> --name <工程名> --import <模型.ydb> --prep --calc' % vp)
    print("（本路径已记入 %s，其他脚本会自动优先复用）" % PY_RECORD)
    return 0


def _utf8_console():
    """让输出在任何控制台编码下都不崩（GBK 下把不可编码字符替换掉）。

    pip / python 的输出是用 `errors="replace"` 解码的，其中可能含 U+FFFD 等
    非 cp936 字符；默认 GBK 控制台下 print 会抛 UnicodeEncodeError 并以退出码 1
    中断 —— 那时环境其实已经装好了，调用方却判成失败。
    """
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(errors="replace")
        except Exception:                                      # noqa: BLE001
            pass


if __name__ == "__main__":
    sys.exit(main())
