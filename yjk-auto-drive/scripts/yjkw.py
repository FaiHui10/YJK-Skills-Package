# -*- coding: utf-8 -*-
"""YJK 弹窗看护 / 等待 —— 只用 Win32 API，不 import YJKAPI。

这样它可以后台长时间运行，需要停时直接结束进程也不会影响 YJK 的连接。

  python yjkw.py probe                    列出 yjks 窗口与对话框
  python yjkw.py watch --timeout 1800     后台看护：自动应答模态框，日志写文件
  python yjkw.py wait --file <路径> --timeout 1800   等文件 mtime 变化
      （`wait` 等到了退出码 0；**超时退出码 1** —— 否则 `wait && 下一步` 会把
        "超时没等到"当成成功串下去）
"""
import argparse
import ctypes
import os
import sys
import time
from ctypes import wintypes

_u32 = ctypes.windll.user32
_k32 = ctypes.windll.kernel32
_BM_CLICK = 0x00F5
_WM_COMMAND = 0x0111
CB = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

HERE = os.path.dirname(os.path.abspath(__file__))


def _cls(h):
    b = ctypes.create_unicode_buffer(256)
    _u32.GetClassNameW(h, b, 256)
    return b.value


def _txt(h):
    n = _u32.GetWindowTextLengthW(h)
    b = ctypes.create_unicode_buffer(n + 1)
    _u32.GetWindowTextW(h, b, n + 1)
    return b.value


def _pid(h):
    p = wintypes.DWORD()
    _u32.GetWindowThreadProcessId(h, ctypes.byref(p))
    return p.value


def _exe(pid):
    h = _k32.OpenProcess(0x1000, False, pid)
    if not h:
        return ""
    b = ctypes.create_unicode_buffer(1024)
    sz = wintypes.DWORD(1024)
    ok = _k32.QueryFullProcessImageNameW(h, 0, b, ctypes.byref(sz))
    _k32.CloseHandle(h)
    return b.value if ok else ""


def _children(hwnd):
    kids = []

    def cb(c, _):
        kids.append(c)
        return True

    _u32.EnumChildWindows(hwnd, CB(cb), 0)
    return kids


def _dialogs():
    out = []

    def cb(hwnd, _):
        if not _u32.IsWindowVisible(hwnd) or _cls(hwnd) != "#32770":
            return True
        if "yjks" not in _exe(_pid(hwnd)).lower():
            return True
        title = _txt(hwnd)
        body, btns = "", {}
        for c in _children(hwnd):
            k = _cls(c)
            if k == "Static" and not body:
                body = _txt(c).strip()
            elif k == "Button":
                btns[_txt(c).strip()] = c
        out.append({"hwnd": hwnd, "pid": _pid(hwnd), "title": title, "body": body,
                    "btns": btns})
        return True

    _u32.EnumWindows(CB(cb), 0)
    return out


def _yjks_windows(visible_only: bool = True):
    """[(pid, 标题)] —— `yjks` 类顶层窗口。

    `visible_only=False` 时**不看 `IsWindowVisible`**。判据必须与
    `yjk_auto.has_main_window()` 一致：窗口刚创建还在渲染、或被隐藏时
    `IsWindowVisible` 为假，若据此判"没有主窗口"，会把你自己的实例当成
    "无窗口残留"（`yjk_cleanup.py --apply` 会照此杀进程）。
    默认值保持 True：探测/列窗口这类只读用途行为不变。
    """
    out = []

    def cb(hwnd, _):
        if _cls(hwnd) != "yjks":
            return True
        if visible_only and not _u32.IsWindowVisible(hwnd):
            return True
        out.append((_pid(hwnd), _txt(hwnd)))
        return True

    _u32.EnumWindows(CB(cb), 0)
    return out


def answer_once():
    """应答一轮，返回说明列表。"""
    msgs = []
    for d in _dialogs():
        btns = d["btns"]
        if not btns:
            continue
        if any("中止" in t for t in btns):
            continue                                          # 计算进度窗，绝不点
        text = "%s %s" % (d["title"], d["body"])
        target = None
        if "是否保存" in text or ("保存" in text and "否" in "".join(btns)):
            target = next((c for t, c in btns.items() if "否" in t), None)
        elif "保存" in text:
            target = next((c for t, c in btns.items() if "是" in t or "确定" in t), None)
        else:
            target = next((c for t, c in btns.items() if "确定" in t), None)
        if target is None:
            msgs.append("未应答：标题=%r 正文=%r 按钮=%s" % (d["title"], d["body"],
                                                             list(btns)))
            continue
        # 唯一有效的应答方式：向**对话框**发 WM_COMMAND，
        #    wParam = 控件ID，lParam = 按钮 hwnd。
        #    BM_CLICK / 键盘消息 / WM_CLOSE 对 YJK 的模态框都不起作用。
        #    等价实现见同目录 dlgwatch.py
        #    （`host` 已内建自动拉起，正常不用手跑本脚本）。
        cid = _u32.GetDlgCtrlID(target)
        _u32.PostMessageW(d["hwnd"], _WM_COMMAND, cid & 0xFFFF, target)
        msgs.append("应答：标题=%r 正文=%r -> 「%s」" % (d["title"], d["body"],
                                                       _txt(target).strip()))
    return msgs


def cmd_probe(a):
    print("yjks 主窗口：")
    for pid, t in _yjks_windows() or []:
        print("   pid=%-6d title=%r" % (pid, t))
    print("对话框：")
    for d in _dialogs():
        print("   pid=%-6d 标题=%r 正文=%r 按钮=%s"
              % (d["pid"], d["title"], d["body"], list(d["btns"])))
    if not _dialogs():
        print("   （无）")


def cmd_watch(a):
    log_path = a.log or os.path.join(HERE, "ywatch.log")
    t_end = time.time() + a.timeout
    with open(log_path, "a", encoding="utf-8") as f:
        f.write("=== watch start %s timeout=%ss ===\n"
                % (time.strftime("%H:%M:%S"), a.timeout))
        seen = set()
        while time.time() < t_end:
            for m in answer_once():
                if m not in seen:
                    seen.add(m)
                    line = "%s  %s\n" % (time.strftime("%H:%M:%S"), m)
                    f.write(line)
                    f.flush()
                    print(line.rstrip(), flush=True)
            time.sleep(1.0)
        f.write("=== watch end %s ===\n" % time.strftime("%H:%M:%S"))
    print("watch 结束", flush=True)


def cmd_wait(a) -> int:
    """等文件 mtime 变化。等到 → 0；超时没等到 → 1。

    "等到"与"超时没等到"以前都返回 0：调用方（`&&` 链、编排脚本）无法区分，
    会把"文件始终没产出"当成成功往下走。
    """
    target = a.file
    t0 = os.path.getmtime(target) if os.path.exists(target) else 0.0
    if a.after:
        t0 = a.after
    end = time.time() + a.timeout
    print("等待 %s mtime > %s（基线 %s）" % (target, t0,
                                           time.strftime("%H:%M:%S", time.localtime(t0))),
          flush=True)
    while time.time() < end:
        try:
            if os.path.getmtime(target) > t0:
                print("已更新：%s" % time.strftime("%H:%M:%S"), flush=True)
                return 0
        except OSError:
            pass
        time.sleep(a.poll)
    print("超时未更新", flush=True)
    print("!! 退出码 1 = 没等到更新（%.0fs 内 %s 没有变化）：这不是成功，别往下串"
          % (a.timeout, target), flush=True)
    return 1


def main() -> int:
    # 控制台兜底：窗口标题/对话框正文是运行期字符串，可能是非 cp936 字符；
    # 在 main() 里调用，被 import 当库用（不走 `__main__` 分支）也覆盖得到。
    _utf8_console()
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("probe")
    p.set_defaults(func=cmd_probe)
    w = sub.add_parser("watch")
    w.add_argument("--timeout", type=float, default=1800)
    w.add_argument("--log")
    w.set_defaults(func=cmd_watch)
    t = sub.add_parser("wait")
    t.add_argument("--file", required=True)
    t.add_argument("--after", type=float, default=0.0)
    t.add_argument("--timeout", type=float, default=1800)
    t.add_argument("--poll", type=float, default=3)
    t.set_defaults(func=cmd_wait)
    a = ap.parse_args()
    rc = a.func(a)
    sys.stdout.flush()
    return int(rc or 0)


def _utf8_console():
    """让输出在任何控制台编码下都不崩（GBK 下把不可编码字符替换掉）。

    窗口标题/对话框正文是 YJK 给的运行期字符串，可能是非 cp936 字符，
    默认 GBK 控制台下 print 会抛 UnicodeEncodeError 并以退出码 1 中断。
    """
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(errors="replace")
        except Exception:                                      # noqa: BLE001
            pass


if __name__ == "__main__":
    _utf8_console()
    sys.exit(main())
