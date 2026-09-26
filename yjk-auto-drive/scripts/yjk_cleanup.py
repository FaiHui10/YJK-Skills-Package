# -*- coding: utf-8 -*-
"""清理 YJKAPI 拉起的"无主窗口"yjks 残留实例（多实例会把主窗口顶崩）。

背景
----
`import YJKAPI` 会自动初始化，并**直接拉起一个 yjks.exe**（绕过 YjkLauncher 的启动流程）。
每跑一次带 YJKAPI 的脚本就多一个无窗口实例；累积后互相抢事件，主实例会"莫名其妙被关掉"。
本脚本只处理**没有主窗口**的 yjks 进程，绝不碰你正在用的那个界面。

"有没有主窗口"只有一份判据
--------------------------
一律复用 `yjk_auto.instances()` 的分类（它内部用 `has_main_window()`：只看该进程有没有
`yjks` 类顶层窗口，**不看窗口可见性**），与 `references/ipc-protocol.md` 写的一致。
理由见 `yjk_auto.has_main_window()` 的注释：宁可把无名实例判成"你在用的"（于是不碰），
也不要误判成残留去清。
老版这里用的是 `yjkw._yjks_windows()`，它要求 `IsWindowVisible` —— **判据比 yjk_auto 弱**，
而会动手杀进程的偏偏是本脚本：窗口刚创建还在渲染、或处于隐藏状态时它读不到那个实例，
于是把你自己的实例当"无窗口残留"杀掉。

用法
----
    python yjk_cleanup.py            # 预演：只列出将清理哪些
    python yjk_cleanup.py --apply     # 真正结束

退出码
------
    0 = 预演完成；或有 --apply 且确认清干净了
    1 = 有实例**没清掉**（终止请求被拒 / 超时仍在）
    2 = 实例**枚举不可用**：此时"有没有残留"无从判断，绝不打印"没有需要清理…"了事
"""
from __future__ import annotations

import argparse
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

KIND_TAG = {"own": "自有登记", "foreign": "有主窗口/带工程（你在用）",
            "orphan": "残留(无主窗口)", "dead": "残壳(已终止待回收)"}


def _start_times():
    """{pid: 启动时间}。psutil 是**可选**依赖，只用来看时间，不参与判定。"""
    try:
        import psutil
    except Exception as e:                                     # noqa: BLE001
        print("（未装 psutil：不显示启动时间，不影响清理判定；要装可运行 setup_env.py）%r" % e)
        return {}
    out = {}
    try:
        for pr in psutil.process_iter(["pid", "name", "create_time"]):
            if (pr.info.get("name") or "").lower() == "yjks.exe":
                out[pr.info["pid"]] = pr.info.get("create_time")
    except Exception as e:                                     # noqa: BLE001
        print("!! psutil 枚举失败（只影响启动时间的显示）：%s" % e)
    return out


def _fallback_rows():
    """yjk_auto 不可用时的退回路径：psutil 列进程 + yjkw 按**同一条窗口判据**分类。"""
    try:
        import psutil
    except Exception as e:                                     # noqa: BLE001
        return [], "psutil 也不可用（%r）—— 枚举不了 yjks 进程" % e
    try:
        import yjkw                                            # 同目录，纯 Win32
        titled = {pid for pid, _ in yjkw._yjks_windows(visible_only=False)}
    except Exception as e:                                     # noqa: BLE001
        return [], "yjkw 窗口探测不可用（%r）" % e
    rows = []
    try:
        for pr in psutil.process_iter(["pid", "name", "create_time"]):
            if (pr.info.get("name") or "").lower() != "yjks.exe":
                continue
            pid = pr.info["pid"]
            rows.append({"pid": pid, "kind": "foreign" if pid in titled else "orphan",
                         "haswin": pid in titled, "proj": None,
                         "started": pr.info.get("create_time")})
    except Exception as e:                                     # noqa: BLE001
        return [], "psutil 枚举失败（%r）" % e
    return rows, ""


def gather():
    """→ (rows, err)。rows = [{pid, kind, haswin, proj, started}]。

    `kind` 与 `yjk_auto.instances()` 完全一致（own / foreign / orphan / dead）；
    只有 **orphan**（无主窗口、无工程命令行、非自有、非残壳）才是清理对象。
    `err` 非空 = **枚举不可用**：既不能说"有残留"，也不能说"没有残留"。
    """
    try:
        import yjk_auto as YA
    except Exception as e:                                     # noqa: BLE001
        print("!! 无法 import yjk_auto（%r）—— 退回自带的 psutil + 窗口判据" % e)
        return _fallback_rows()
    try:
        ins = YA.instances()
    except Exception as e:                                     # noqa: BLE001
        print("!! yjk_auto.instances() 抛异常（%r）—— 退回自带的 psutil + 窗口判据" % e)
        return _fallback_rows()
    started = _start_times()
    rows = []
    for i in ins:
        try:
            haswin = bool(YA.has_main_window(i["pid"]))
        except Exception:                                      # noqa: BLE001
            haswin = i["kind"] == "foreign"
        rows.append({"pid": i["pid"], "kind": i["kind"], "haswin": haswin,
                     "proj": i.get("proj"), "started": started.get(i["pid"])})
    return rows, ""


def kill_one(pid: int) -> bool:
    """结束一个 PID，返回"终止请求是否被接受"。

    优先用 `yjk_auto.kill_pid`：它检查 `TerminateProcess` 的返回值，
    err=5（对方权限更高/被安全软件拦截）时**不报成功**；yjk_auto 不可用时退回 psutil。
    """
    try:
        import yjk_auto as YA
        return bool(YA.kill_pid(pid, verbose=True))
    except Exception as e:                                     # noqa: BLE001
        print("   （退回 psutil.kill：yjk_auto.kill_pid 不可用 %r）" % e)
    try:
        import psutil
        psutil.Process(pid).kill()
        return True
    except Exception as e:                                     # noqa: BLE001
        print("   pid=%d 结束失败：%s" % (pid, e))
        return False


def wait_gone(pids, timeout: float = 10.0):
    """等这些 PID 真的消失，返回仍活着的那些。"""
    try:
        import yjk_auto as YA
        return YA.wait_gone(list(pids), timeout=timeout)
    except Exception:                                          # noqa: BLE001
        end = time.time() + timeout
        left = list(pids)
        while left and time.time() < end:
            try:
                import psutil
                left = [p for p in left if psutil.pid_exists(p)]
            except Exception:                                  # noqa: BLE001
                return left
            if left:
                time.sleep(1)
        return left


def main() -> int:
    # 控制台兜底：实例分类里的窗口标题是运行期字符串，可能是非 cp936 字符；
    # 在 main() 里调用，被 import 当库用（不走 `__main__` 分支）也覆盖得到。
    _utf8_console()
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="真正结束（默认只预演）")
    a = ap.parse_args()

    rows, err = gather()
    if err:
        print("!! yjks 实例**枚举不可用**：%s" % err)
        print("   后果：既不能说「有残留」也不能说「没有残留」——本次**没有**清理任何实例。")
        return 2

    print("yjks 进程 %d 个；其中有主窗口的 %s"
          % (len(rows), sorted(r["pid"] for r in rows if r["haswin"]) or "无"))
    victims = [r for r in rows if r["kind"] == "orphan"]
    kept = [r for r in rows if r["kind"] != "orphan"]
    if kept:
        print("以下实例**不动**（判据与 yjk_auto.instances() 完全一致）：")
        for r in kept:
            print("   pid=%-7d [%s]%s" % (r["pid"], KIND_TAG.get(r["kind"], r["kind"]),
                                         "  打开=%s" % r["proj"] if r.get("proj") else ""))
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

    problems = []
    for r in victims:
        if not kill_one(r["pid"]):
            problems.append("pid=%d 的终止请求被拒（见上面的 err）" % r["pid"])
    left = [p for p in wait_gone([r["pid"] for r in victims])]
    for r in victims:
        if r["pid"] in left:
            print("!! pid=%d **仍在**（终止请求被拒或超时）—— 没有清掉，别当成功" % r["pid"])
        else:
            print("   已结束 pid=%d" % r["pid"])
    rows2, err2 = gather()
    if err2:
        print("!! 复核失败（%s）——无法确认清干净" % err2)
        problems.append("复核时枚举不可用：%s" % err2)
    else:
        print("剩余无窗口实例：%s"
              % ([r["pid"] for r in rows2 if r["kind"] == "orphan"] or "无"))
        problems += ["pid=%d 仍是残留" % r["pid"] for r in rows2 if r["kind"] == "orphan"]
    if problems:
        print("!! 本次**没有全部清干净**（退出码 1）：")
        for p in problems:
            print("     · %s" % p)
        return 1
    return 0


def _utf8_console():
    """让输出在任何控制台编码下都不崩（GBK 下把不可编码字符替换掉）。

    窗口标题是运行期字符串，可能是非 cp936 字符；默认 GBK 控制台下 print
    会抛 UnicodeEncodeError 并以退出码 1 中断。
    """
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(errors="replace")
        except Exception:                                      # noqa: BLE001
            pass


if __name__ == "__main__":
    _utf8_console()
    sys.exit(main())
