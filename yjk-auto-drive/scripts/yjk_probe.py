# -*- coding: utf-8 -*-
r"""环境自检 / 一键修复（新电脑上先跑这个）。

输出分三段：
  [1] 检查项 —— 每项给 OK / 警告 / 失败，并直接写出「怎么修」
  [2] 结论   —— 能不能跑全自动，不能的话缺哪一步
  [3] 下一步 —— 可直接复制的命令

用法
----
  python yjk_probe.py                     # 只检查
  python yjk_probe.py --fix-config        # 顺手把 Config.ini 的 Flag 改成 True
  python yjk_probe.py --json env.json     # 同时落盘机器可读结果
  python yjk_probe.py --runtime           # 额外做一次「真连一次」的活体测试
                                          # （会启动 yjks；用 yjk_save 的 mtime 判定）
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths as P                                              # noqa: E402

OK, WARN, BAD = "OK  ", "警告", "失败"


def _line(tag, title, detail="", fix=""):
    print("  [%s] %s" % (tag, title))
    if detail:
        for ln in str(detail).splitlines():
            print("         %s" % ln)
    if fix:
        for ln in str(fix).splitlines():
            print("      -> %s" % ln)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--fix-config", action="store_true",
                    help="把 Config.ini 的 [YJKSControl] Flag 写成 True")
    ap.add_argument("--json", help="把结果写到该 json")
    ap.add_argument("--runtime", action="store_true", help="额外做一次活体连接测试")
    ap.add_argument("--proj-dir", help="工程目录（活体测试与写盘判定用）")
    a = ap.parse_args(argv)

    print("=" * 78)
    print("YJK 自动驱动 —— 环境自检")
    print("=" * 78)
    print("本技能目录  : %s" % P.SKILL_DIR)
    print("用户缓存    : %s" % P.USER_CACHE)
    print("Python      : %s" % sys.executable)
    print()

    d = P.doctor(a.proj_dir)
    blocking = []          # 必须解决才能跑
    warn = []              # 可跑但要注意

    print("[1] 检查项")
    print("-" * 78)

    # ---- 1. Python + pythonnet ----
    py = d["python"]
    if py["has_clr"]:
        _line(OK, "Python 有 pythonnet(clr)", py["exe"])
    else:
        _line(BAD, "Python 缺 pythonnet(clr)",
              "当前解释器：%s\n候选：%s" % (sys.executable,
                                          "\n".join(py["candidates"][:6]) or "（无）"),
              "python %s\n"
              "  （会建一个隔离环境 %s 并安装 pythonnet + openpyxl + psutil）"
              % (os.path.join(P.SKILL_DIR, "scripts", "setup_env.py"),
                 os.path.join(P.USER_CACHE, "venv")))
        blocking.append("pythonnet")
    print()

    # ---- 2. YJK 安装 ----
    ins = d["yjk"]
    if ins["root"]:
        _line(OK, "YJK 安装位置", "%s\n版本=%s  来源=%s"
              % (ins["root"], ins["version"], ins["source"]))
    else:
        _line(BAD, "未找到 yjks.exe",
              "候选目录：%s" % ("\n".join(ins["candidates"]) or "（无）"),
              "设环境变量 YJK_DIR=<安装目录>，或先手动打开一次 YJK")
        blocking.append("yjk-install")
    if ins["launcher"]:
        _line(OK, "YjkLauncher.exe", ins["launcher"])
    elif ins["root"]:
        _line(WARN, "同目录未见 YjkLauncher.exe",
              fix="全自动启动前需先手动打开一次 YJK")
        warn.append("launcher")
    print()

    # ---- 3. Config.ini Flag ----
    cfgs = d["config_inis"]
    if not cfgs:
        _line(BAD, "未找到任何 Config.ini",
              fix="确认 YJK 至少启动过一次；或用 --fix-config 让脚本按安装目录补一份")
        blocking.append("config-ini")
    else:
        good = [p for p, st in cfgs if (st["flag"] or "").lower() == "true"]
        if good:
            _line(OK, "Config.ini 已开 [YJKSControl] Flag=True", "\n".join(good))
        else:
            _line(BAD, "Config.ini 的 Flag 不是 True（IPC 不会自动开）",
                  "\n".join("%s  ->  %s" % (p, st) for p, st in cfgs[:6]),
                  "python %s --fix-config   （或照 below 手改两处）"
                  % os.path.join(P.SKILL_DIR, "scripts", "yjk_probe.py"))
            blocking.append("config-flag")
    print()

    # ---- 4. 官方客户端 DLL ----
    api = d["yjkapi"]
    if api["path"]:
        tag = OK if api["kind"] == "YJKIPC.YJKSControl" else WARN
        _line(tag, "控制客户端 DLL", "%s\n类型=%s  来源=%s"
              % (api["path"], api["kind"], api["source"]))
        for n in api["notes"]:
            print("         注意：%s" % n)
        if tag is WARN:
            warn.append("dll-fallback")
    else:
        _line(BAD, "未找到可用的控制 DLL", "\n".join(api["notes"]),
              "取 gitee yjk-opensource/csharp-yjks **7.1 分支** 的\n"
              "  不依赖YJK案例/dll/YJKAPI.dll\n"
              "放到 %s（或设环境变量 YJKAPI_DLL）"
              % os.path.join(P.ASSETS, "YJKAPI.dll"))
        blocking.append("dll")
    print()

    # ---- 5. 单实例 ----
    n = len(d["yjks_running"])
    if n == 0:
        _line(OK, "当前无 yjks 实例（全自动启动前应为 0）", "pid=%s" % d["yjks_running"])
    elif n == 1:
        _line(WARN, "已有 1 个 yjks 在跑",
              "pid=%s；全自动流程会先 kill 再重启" % d["yjks_running"])
        warn.append("already-running")
    else:
        _line(BAD, "有 %d 个 yjks 实例 —— 会互抢 Global 事件，命令静默失效" % n,
              "pid=%s" % d["yjks_running"],
              "python %s kill" % os.path.join(P.SKILL_DIR, "scripts", "yjk_auto.py"))
        blocking.append("multi-instance")
    print()

    # ---- 自动修复 ----
    if a.fix_config:
        print("[1b] --fix-config：写入 Flag=True")
        done = P.write_config_flag("True")
        for p in done:
            print("  已改 %s" % p)
        if not done:
            print("  没有可写的 Config.ini（先确认 YJK 装好并启动过一次）")
        print()

    # ---- 结论 ----
    print("[2] 结论")
    print("-" * 78)
    if not blocking:
        print("  环境齐备 —— 可直接跑全自动流程：")
        print("     python yjk_auto.py host --dir <工作目录> --name <工程名> \\")
        print("            --import <模型.ydb> --prep --calc")
        if warn:
            print("  注意项：%s" % "、".join(warn))
    else:
        print("  还缺 %d 项，按上面的 -> 提示处理后重跑本脚本：" % len(blocking))
        for b in blocking:
            print("     - %s" % b)

    # ---- 活体测试 ----
    if a.runtime:
        print()
        print("[3] 活体测试（真启动 → 真建工程 → 真连一次）")
        print("-" * 78)
        import shutil
        import tempfile
        import yjk_auto as Y
        Y.kill_all()
        time.sleep(2)
        Y.ensure_launcher()
        # 用一个临时目录做真实验证，测完删掉，不污染用户工程
        tmp = os.path.join(os.path.abspath(a.proj_dir or os.getcwd()),
                           "_yjkc_probe_tmp")
        os.makedirs(tmp, exist_ok=True)
        pid, ok = Y.boot_yjks(tmp)
        if not ok:
            print("  !! 启动失败，无法做活体测试")
        else:
            try:
                cli = Y.Client()
                print("  客户端就绪：%s（%s）" % (cli.dll, cli.kind))
                print("  UINew 建临时工程 ...")
                print("    -> %s" % cli.run("UINew", os.path.join(tmp, "Probe.yjk"), 200))
                t0 = time.time()
                while time.time() - t0 < 90:
                    ps = Y.yjks_pids()
                    if ps and any("Probe" in t for t in Y.titles(ps[0])):
                        print("    工程已建立（%.0fs）" % (time.time() - t0))
                        break
                    time.sleep(3)
                before = Y.snap(tmp)
                print("  yjk_save -> %s" % cli.run("yjk_save", "", 180))
                changed, t0 = [], time.time()
                while time.time() - t0 < 90:
                    time.sleep(2)
                    changed = [os.path.basename(k) for k in Y.diff(before, Y.snap(tmp))
                               if os.path.basename(k) != "shared_memory"]
                    if changed:
                        break
                if changed:
                    print("  *** 通过：IPC 通道工作正常，yjk_save 已实际写盘")
                    print("      变更文件：%s" % sorted(set(changed)))
                else:
                    print("  >>> 未通过：有应答但 90s 内无文件变化 —— 见")
                    print("      references/troubleshooting.md §5（多实例冲突）")
            except Exception as e:                             # noqa: BLE001
                print("  !! 客户端初始化失败: %s" % e)
            finally:
                Y.kill_all(verbose=False)
                shutil.rmtree(tmp, ignore_errors=True)
                print("  （测试结束：yjks 已清理，临时目录已删除）")

    if a.json:
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump({"doctor": d, "blocking": blocking, "warn": warn},
                      f, ensure_ascii=False, indent=1)
        print("\n-> %s" % a.json)
    return 0 if not blocking else 1


if __name__ == "__main__":
    sys.exit(main())
