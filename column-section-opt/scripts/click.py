# -*- coding: utf-8 -*-
"""点掉指定文字的按钮（只动 yjks 自己的对话框）。

用法： python click.py <按钮文字包含的子串> [--dry]
"""
import ctypes
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import yjkw                                                       # noqa: E402

BM_CLICK = 0x00F5
key = sys.argv[1]
dry = "--dry" in sys.argv

hit = 0
for _ in range(3):
    ds = yjkw._dialogs()
    if not ds:
        break
    for d in ds:
        print("对话框：标题=%r 正文=%r 按钮=%s" % (d["title"], d["body"], list(d["btns"])))
        for t, c in d["btns"].items():
            if key in t:
                print("  -> 点击「%s」%s" % (t.strip(), "(预演)" if dry else ""))
                if not dry:
                    ctypes.windll.user32.SendMessageW(c, BM_CLICK, 0, 0)
                hit += 1
                time.sleep(1.0)
                break
        else:
            continue
    time.sleep(1.0)
print("完成，共点击 %d 次" % hit)
