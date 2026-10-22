# -*- coding: utf-8 -*-
"""清理 YJKAPI 拉起的"无主窗口"yjks 残留实例（多实例会把主窗口顶崩）。

背景
----
`import YJKAPI` 会自动初始化，并**直接拉起一个 yjks.exe**（绕过 YjkLauncher 的授权签出）。
每跑一次带 YJKAPI 的脚本就多一个无窗口实例；累积后互相抢授权，主实例会"莫名其妙被关掉"。
本脚本只处理**没有主窗口**的 yjks 进程，绝不碰你正在用的那个界面。

用法
----
    python yjk_cleanup.py            # 预演：只列出将清理哪些
    python yjk_cleanup.py --apply     # 真正结束
"""
import argparse
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def list_yjks():
    rows = []
    try:
        import psutil
        for pr in psutil.process_iter(["pid", "name", "exe", "create_time"]):
            if (pr.info.get("name") or "").lower() != "yjks.exe":
                continue
            rows.append({"pid": pr.info["pid"], "exe": pr.info.get("exe"),
                         "started": pr.info.get("create_time"), "proc": pr})
    except Exception as e:                                     # noqa: BLE001
        print("需要 psutil（先 pip install psutil）：%s" % e)
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="真正结束（默认只预演）")
    a = ap.parse_args()

    import yjkw                                                # 纯 Win32，取窗口标题
    titled = {pid for pid, _ in yjkw._yjks_windows()}
    rows = list_yjks()
    print("yjks 进程 %d 个；其中有主窗口的 %s" % (len(rows), sorted(titled) or "无"))
    victims = [r for r in rows if r["pid"] not in titled]
    if not victims:
        print("没有需要清理的无窗口实例。")
        return 0
    print("将清理（无主窗口）：")
    for r in victims:
        print("   pid=%-7d 启动=%s" % (r["pid"], time.strftime(
            "%H:%M:%S", time.localtime(r["started"] or 0))))
    if not a.apply:
        print("\n（预演）加 --apply 才会真正结束。")
        return 0
    for r in victims:
        try:
            r["proc"].kill()
            print("   已结束 pid=%d" % r["pid"])
        except Exception as e:                                 # noqa: BLE001
            print("   pid=%d 结束失败：%s" % (r["pid"], e))
    time.sleep(2)
    left = [x for x in list_yjks() if x["pid"] not in titled]
    print("剩余无窗口实例：%s" % ([x["pid"] for x in left] or "无"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
