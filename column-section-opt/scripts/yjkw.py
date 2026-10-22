# -*- coding: utf-8 -*-
"""YJK 弹窗看护 / 等待 —— 只用 Win32 API，不 import YJKAPI。

这样它可以后台长时间运行，需要停时直接结束进程也不会影响 YJK 的连接。

  python yjkw.py probe                    列出 yjks 窗口与对话框
  python yjkw.py watch --timeout 1800     后台看护：自动应答模态框，日志写文件
  python yjkw.py wait --file <路径> --timeout 1800   等文件 mtime 变化
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


def _yjks_windows():
    out = []

    def cb(hwnd, _):
        if _u32.IsWindowVisible(hwnd) and _cls(hwnd) == "yjks":
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
        _u32.SendMessageW(target, _BM_CLICK, 0, 0)
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


def cmd_wait(a):
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
                return
        except OSError:
            pass
        time.sleep(a.poll)
    print("超时未更新", flush=True)


def main():
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
    a.func(a)
    sys.stdout.flush()


if __name__ == "__main__":
    main()
