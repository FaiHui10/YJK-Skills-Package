# -*- coding: utf-8 -*-
"""YJK 工程环境自适应探测：**不写死任何目录结构 / 文件名**。

从工程目录与本机推导：
  * 计算模型文件名 —— 扫 *.ymd（含 g-of.ymd）挑出含 tblColSect 的那个
  * 施工图模型     —— 施工图\\dtlmodel.ydb（若存在）
  * YJK 版本       —— 「工程名称_*--建模版本号.txt」的建模版本号；退回 wmass.out 的"版本："
  * YJK 安装位置   —— 运行中的 yjks.exe / YjkLauncher.exe 路径；退回注册表 / 常见目录
  * 运行实例 / 该工程是否正被打开（写盘前必须为「否」，否则会把 yjks 弄崩）

用法：
    python env.py [--proj-dir <工程目录>] [--json env.json]
"""
import argparse
import glob
import json
import os
import re
import sqlite3
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
KEY_TABLE = "tblColSect"                      # 有它才像"模型库"
YMD_GENERIC = ["g-of.ymd"]
ID_LIMIT = 100000                             # 实体 ID 上限（100000 是 tblProjectPara 哨兵）


# ---------------------------------------------------------------- 基础
def _tables(path):
    con = sqlite3.connect("file:%s?mode=ro" % path.replace("\\", "/"), uri=True)
    try:
        return {r[0] for r in con.execute(
            "SELECT name FROM sqlite_master WHERE type='table'")}
    finally:
        con.close()


def _stat(path):
    st = os.stat(path)
    return {"size": st.st_size, "mtime": st.st_mtime}


# ---------------------------------------------------------------- 模型文件
def detect_models(proj_dir):
    out, seen = [], set()
    for pat in ("*.ymd", "*.YMD", "*.ydb", "*.YDB"):
        for p in glob.glob(os.path.join(proj_dir, pat)):
            if p in seen:
                continue
            seen.add(p)
            rec = {"file": os.path.basename(p), "path": p, "sqlite": False,
                   "has_col_sect": False, "kind": None}
            try:
                ts = _tables(p)
                rec["sqlite"] = True
                rec["has_col_sect"] = KEY_TABLE in ts
                rec["tables"] = len(ts)
                if "tblStdFlr" in ts and "tblFloor" in ts:
                    rec["kind"] = "计算/模型库"
            except sqlite3.Error:
                pass
            rec.update(_stat(p))
            out.append(rec)
    out.sort(key=lambda r: (not r["has_col_sect"], r["file"]))
    return out


def pick_calc_model(proj_dir):
    """优先 g-of.ymd；否则取与目录同名的 <目录名>.ymd；否则第一个含柱截面表的。"""
    cands = [r for r in detect_models(proj_dir) if r["has_col_sect"]]
    if not cands:
        return None
    for name in YMD_GENERIC:
        for r in cands:
            if r["file"].lower() == name.lower():
                return r["path"]
    proj_name = os.path.basename(os.path.normpath(proj_dir))
    for r in cands:
        if os.path.splitext(r["file"])[0].lower() == proj_name.lower():
            return r["path"]
    return cands[0]["path"]


def detect_dtl_model(proj_dir):
    p = os.path.join(proj_dir, "施工图", "dtlmodel.ydb")
    return p if os.path.exists(p) else None


# ---------------------------------------------------------------- 版本 / 安装位置
def detect_version(proj_dir):
    info = {"version": None, "source": None, "project_name": None}
    for p in glob.glob(os.path.join(proj_dir, "工程名称_*--建模版本号.txt")):
        try:
            txt = open(p, "rb").read().decode("gbk", "replace")
        except OSError:
            continue
        m = re.search(r"建模版本号\s*=\s*([\d.]+)", txt)
        n = re.search(r"工程名称\s*=\s*(.+)", txt)
        if m:
            info["version"], info["source"] = m.group(1).strip(), os.path.basename(p)
        if n:
            info["project_name"] = n.group(1).strip()
        if info["version"]:
            return info
    wm = os.path.join(proj_dir, "设计结果", "wmass.out")
    if os.path.exists(wm):
        txt = open(wm, "rb").read().decode("gbk", "replace")
        m = re.search(r"版本：\s*([\d.]+)", txt)
        if m:
            info["version"], info["source"] = m.group(1), "设计结果\\wmass.out"
    return info


def _from_ps(cmd):
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command", cmd],
                           capture_output=True, text=True, timeout=30,
                           encoding="utf-8", errors="replace")
        return r.stdout
    except Exception:                                          # noqa: BLE001
        return ""


def detect_yjk_install():
    """YJK 安装位置：运行中的进程路径 -> 注册表 -> 常见目录。"""
    info = {"exe": None, "root": None, "launcher": None, "source": None,
            "candidates": []}
    exes = []
    try:
        import psutil
        for pr in psutil.process_iter(["name", "exe"]):
            if (pr.info.get("name") or "").lower() in ("yjks.exe", "yjklauncher.exe"):
                if pr.info.get("exe"):
                    exes.append(pr.info["exe"])
        if exes:
            info["source"] = "psutil"
    except Exception:                                          # noqa: BLE001
        pass
    if not exes:
        out = _from_ps("Get-CimInstance Win32_Process -Filter \"Name='yjks.exe' or "
                       "Name='YjkLauncher.exe'\" | ForEach-Object { $_.ExecutablePath }")
        exes = [x.strip() for x in out.splitlines() if x.strip()]
        if exes:
            info["source"] = "WMI"
    if not exes:
        out = _from_ps(r"(Get-ItemProperty 'HKLM:\SOFTWARE\WOW6432Node\yjkSoft\*' "
                       r"-ErrorAction SilentlyContinue).InstallPath")
        info["candidates"] += [x.strip() for x in out.splitlines() if x.strip()]
    for e in exes:
        if os.path.basename(e).lower() == "yjks.exe":
            info["exe"], info["root"] = e, os.path.dirname(e)
            break
    if not info["root"] and exes:
        info["root"] = os.path.dirname(exes[0])
    if info["root"]:
        lap = os.path.join(info["root"], "YjkLauncher.exe")
        info["launcher"] = lap if os.path.exists(lap) else None
    return info


def detect_running():
    out = []
    try:
        import psutil
        for pr in psutil.process_iter(["pid", "name", "exe", "cmdline", "create_time"]):
            if (pr.info.get("name") or "").lower() != "yjks.exe":
                continue
            out.append({"pid": pr.info["pid"], "exe": pr.info.get("exe"),
                        "cmdline": " ".join(pr.info.get("cmdline") or []),
                        "started": pr.info.get("create_time")})
    except Exception:                                          # noqa: BLE001
        pass
    return sorted(out, key=lambda r: r["pid"])


def detect_open_project():
    """从 yjks 主窗口标题取当前打开的工程：'{工程目录}\\{工程名} - 盈建科软件'。"""
    try:
        sys.path.insert(0, HERE)
        import yjkw                                            # 同目录的纯 Win32 工具
        wins = yjkw._yjks_windows()
    except Exception:                                          # noqa: BLE001
        wins = []
    res = []
    for pid, title in wins:
        m = re.match(r"^(.*?)\s*-\s*盈建科软件", title)
        path = m.group(1).strip() if m else None
        proj_dir, name = ((os.path.dirname(path), os.path.basename(path))
                          if path else (None, None))
        res.append({"pid": pid, "title": title,
                    "project_dir": proj_dir, "project": name})
    return res


def project_is_open(proj_dir, opened=None):
    """该工程是否正被 YJK 打开（写盘前必须为 False）。"""
    opened = opened if opened is not None else detect_open_project()
    key = os.path.normcase(os.path.abspath(proj_dir))
    for o in opened:
        if o["project_dir"] and \
                os.path.normcase(os.path.abspath(o["project_dir"])) == key:
            return o
    return None


# ---------------------------------------------------------------- 汇总
def detect(proj_dir, save=None):
    proj_dir = os.path.abspath(proj_dir)
    ver = detect_version(proj_dir)
    env = {
        "proj_dir": proj_dir,
        "proj_name": ver.get("project_name") or os.path.basename(os.path.normpath(proj_dir)),
        "yjk_version": ver["version"],
        "version_source": ver["source"],
        "calc_model": pick_calc_model(proj_dir),
        "dtl_model": detect_dtl_model(proj_dir),
        "models": detect_models(proj_dir),
        "yjk": detect_yjk_install(),
        "running": detect_running(),
        "opened": detect_open_project(),
    }
    env["model_open"] = bool(project_is_open(proj_dir, env["opened"]))
    if save:
        with open(save, "w", encoding="utf-8") as f:
            json.dump(env, f, ensure_ascii=False, indent=1)
    return env


def show(env):
    print("工程目录   : %s" % env["proj_dir"])
    print("工程名称   : %s" % env["proj_name"])
    print("YJK 版本   : %s   (%s)" % (env["yjk_version"], env["version_source"]))
    print("计算模型   : %s" % (env["calc_model"] or "!! 未找到含 tblColSect 的模型文件"))
    print("施工图模型 : %s" % (env["dtl_model"] or "（无，方案阶段正常）"))
    y = env["yjk"]
    print("YJK 安装   : %s" % (y["root"] or "未探测到"))
    print("  启动器   : %s" % (y["launcher"] or "未找到 YjkLauncher.exe"))
    print("模型文件候选：")
    for m in env["models"]:
        print("   %-26s %10d B  sqlite=%-5s 柱截面表=%-5s %s"
              % (m["file"], m["size"], m["sqlite"], m["has_col_sect"], m["kind"] or ""))
    print("运行中的 yjks（无主窗口的是 YJKAPI 拉起的残留，建议清理）：")
    for r in env["running"]:
        titled = any(o["pid"] == r["pid"] for o in env["opened"])
        print("   pid=%-7d %s %s" % (r["pid"], "有窗口" if titled else "无窗口",
                                     r["cmdline"][:90]))
    if not env["running"]:
        print("   （无）")
    print("当前打开的工程：")
    for o in env["opened"]:
        print("   pid=%-7d %s" % (o["pid"], o["title"]))
    if not env["opened"]:
        print("   （无）")
    print("本工程是否正被打开：%s"
          % ("是 —— 此时写盘会把 yjks 弄崩，先关工程" if env["model_open"] else "否（可安全写盘）"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--proj-dir", default=None, help="工程目录（不给则用当前目录）")
    ap.add_argument("--json", help="把探测结果写到该 json")
    a = ap.parse_args()
    env = detect(a.proj_dir or os.getcwd(), save=a.json)
    show(env)
    if a.json:
        print("\n-> %s" % a.json)


if __name__ == "__main__":
    main()
