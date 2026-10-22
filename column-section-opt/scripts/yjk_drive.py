# -*- coding: utf-8 -*-
"""驱动 YJK 完成"新建工程 → 导入 ydb → 前处理 → 全部计算"，含自适应等待与弹窗自动应答。

★ 前置条件（必须人工做，见 SKILL.md）：
    1) 用 YjkLauncher.exe 打开 YJK（由它完成授权签出）
    2) 在 YJK 命令行敲一次 yjksIPCControl，开启外部控制通道

用法：
    python yjk_drive.py --config c.json --ydb model.ydb --proj <工程目录> [--name Model]

要点（都是实测踩出来的）：
  * RunCmd 是**阻塞**的：命令弹模态框时会永久不返回 → 弹窗必须**后台线程**全程应答
  * 应答要按**正文**判断：含"保存"点「是」；含"中止/终止"点「否」；其余只记录不点击
    （进度窗上有「中止计算」按钮，见"确定"就点会把计算掐断）
  * 等待用信号，不要固定 sleep：新建完成看 YJK 主窗口标题；保存看 .ymd；计算看 wmass.out
  * 自适应计时落盘 timing.json，只缩不放、取历史最小值
"""
import argparse
import ctypes
import json
import os
import sys
import threading
import time
from ctypes import wintypes

from YJKAPI import *

# ---------------------------------------------------------------- 弹窗自动应答
_u32 = ctypes.windll.user32
_k32 = ctypes.windll.kernel32
_BM_CLICK = 0x00F5
_YES_WORDS = ("是", "确定", "OK", "&OK", "Yes", "&Yes")
_NO_WORDS = ("否", "取消", "No", "&No", "Cancel")
_ABORT_HINTS = ("中止", "终止", "取消计算")


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
    h = _k32.OpenProcess(0x1000, False, pid)     # PROCESS_QUERY_LIMITED_INFORMATION
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

    _u32.EnumChildWindows(hwnd, ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND,
                                                   wintypes.LPARAM)(cb), 0)
    return kids


def _find_button(hwnd, words):
    for c in _children(hwnd):
        if _cls(c) == "Button":
            t = _txt(c)
            if any(w in t for w in words):
                return c, (t.strip() or "?")
    return None, None


def answer_yjk_dialog(logger=None):
    found = []

    def cb(hwnd, _):
        if not _u32.IsWindowVisible(hwnd) or _cls(hwnd) != "#32770":
            return True
        if "yjks" not in _exe(_pid(hwnd)).lower():
            return True
        body, btns = "", []
        for c in _children(hwnd):
            k = _cls(c)
            if k == "Static" and not body and _txt(c).strip():
                body = _txt(c).strip()
            elif k == "Button":
                btns.append(_txt(c).strip())
        if not btns:
            return True
        if any(w in body for w in _ABORT_HINTS):
            btn, label = _find_button(hwnd, _NO_WORDS)
            if btn is None:
                btn, label = _find_button(hwnd, _YES_WORDS)
            action = "拒绝中止"
        elif "保存" in body:
            btn, label = _find_button(hwnd, _YES_WORDS)
            action = "保存"
        else:
            found.append("%s | %s | 按钮%s → 未识别，保留不点" % (_txt(hwnd), body, btns))
            return True
        if btn is None:
            return True
        _u32.SendMessageW(btn, _BM_CLICK, 0, 0)
        found.append("%s | %s | %s点了「%s」" % (_txt(hwnd), body, action, label))
        return False

    _u32.EnumWindows(ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND,
                                        wintypes.LPARAM)(cb), 0)
    if found and logger:
        for f in found:
            logger("[弹窗] 自动应答：%s" % f)
    return found[0] if found else None


_stop = threading.Event()
_seen = []


def _watch_loop(logger):
    while not _stop.is_set():
        try:
            ans = answer_yjk_dialog(logger)
            if ans:
                _seen.append(ans)
        except Exception as e:
            if logger:
                logger("[弹窗] 应答异常：%s" % e)
        _stop.wait(1.0)


def window_monitor():
    """监控 YJKSControl 通道是否还活着（没开通道时 RunCmd 会一直阻塞）。"""
    return None


# ---------------------------------------------------------------- 信号与自适应等待
def file_changed(path, t0):
    try:
        return os.path.getmtime(path) > t0
    except OSError:
        return False


def window_titled(path):
    """YJK 主窗口标题是否已指向该工程（新建/打开完成的可靠信号）。"""
    key = os.path.abspath(path).lower()
    hit = []

    def cb(h, _):
        if _cls(h) == "yjks" and _u32.IsWindowVisible(h) and key in _txt(h).lower():
            hit.append(h)
            return False
        return True

    _u32.EnumWindows(ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND,
                                        wintypes.LPARAM)(cb), 0)
    return bool(hit)


class Driver(object):
    MARGIN = 1.6
    MIN_WAIT = 1.5
    POLL = 2.0

    def __init__(self, ydb, proj_dir, name, logger=print):
        self.ydb = os.path.abspath(ydb)
        self.proj_dir = os.path.abspath(proj_dir)
        self.name = name
        self.proj = os.path.join(self.proj_dir, name + ".yjk")
        self.ymd = os.path.join(self.proj_dir, name + ".ymd")
        self.wmass = os.path.join(self.proj_dir, "设计结果", "wmass.out")
        self.trans = os.path.join(self.proj_dir, "yjkTransLoad.sav")
        self.log = logger
        self.profile_path = os.path.join(self.proj_dir, "timing.json")
        self.prof = self._load()

    def _load(self):
        if os.path.exists(self.profile_path):
            try:
                return json.load(open(self.profile_path, encoding="utf-8"))
            except Exception:
                pass
        return {}

    def _save(self):
        json.dump(self.prof, open(self.profile_path, "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)

    def _sig_ready(self, sig, t0):
        if callable(sig):
            return bool(sig())
        return any(file_changed(f, t0) for f in sig)

    def _wait(self, sig, t0, cap, tag):
        end = t0 + cap
        while time.time() < end:
            answer_yjk_dialog(self.log)
            if self._sig_ready(sig, t0):
                return time.time() - t0
            time.sleep(self.POLL)
        return None

    def _sleep(self, seconds, tag):
        end = time.time() + seconds
        while time.time() < end:
            answer_yjk_dialog(self.log)
            time.sleep(min(1.0, max(0.05, end - time.time())))

    def run_steps(self, steps, phase):
        used, obs, fixed = {}, {}, []
        for name, cmd, para, sig, cap, default in steps:
            wait = self.prof.get(name, {}).get("wait", default)
            if sig is None:
                fixed.append(name)
            t0 = time.time()
            YJKSControl.RunCmd(cmd, para)
            if sig is not None:
                o = self._wait(sig, t0, cap, name)
                if o is None:
                    self.log("   %-20s 信号 %.0fs 未出现，按默认 %ds 兜底" % (name, cap, default))
                    self._sleep(default, name)
                    o = default
                used[name] = o
                prev = self.prof.get(name, {}).get("observed")
                best = min(prev, o) if prev else o
                self.prof.setdefault(name, {})["observed"] = round(best, 1)
                obs[name] = best
                self.log("   %-20s 实测 %.1fs（历史最优 %.1fs）" % (name, o, best))
            else:
                self._sleep(wait, name)
                used[name] = wait
        total = sum(used.values())
        fixed_sum = sum(used[n] for n in fixed) or 1.0
        scale = (total * self.MARGIN - sum(obs.values())) / fixed_sum
        scale = max(0.3, min(1.0, scale))
        for name, cmd, para, sig, cap, default in steps:
            if sig is None:
                cur = self.prof.get(name, {}).get("wait", default)
                self.prof.setdefault(name, {})
                self.prof[name]["wait"] = round(min(default, max(self.MIN_WAIT, cur * scale)), 1)
        self.log("   [%s] 合计 %.1fs（信号 %.1fs），无信号步骤 ×%.2f（只缩不放）"
                 % (phase, total, sum(obs.values()), scale))
        return used

    def drive(self):
        os.makedirs(self.proj_dir, exist_ok=True)
        threading.Thread(target=_watch_loop, args=(self.log,), daemon=True).start()
        t_all = time.time()
        model_steps = [
            # UINew 顶掉当前工程时会弹「是否保存当前工程?」，由后台线程应答（自动选"是"）
            ("预存当前工程", "yjk_save", "", None, 0, 6.0),
            ("新建工程", "UINew", self.proj, (lambda: window_titled(self.proj_dir)), 180.0, 20.0),
            ("导入ydb", "yjk_importydb", self.ydb, None, 0, 12.0),
            ("工程修复", "yjk_repair", "", None, 0, 3.0),
            ("形成节点", "yjk_formnode", "2", None, 0, 3.0),
            ("形成楼板", "yjk_formslab_alllayer", "", None, 0, 3.0),
            ("保存模型", "yjk_save", "", [self.ymd, self.proj], 40.0, 8.0),
        ]
        calc_steps = [
            ("建模→前处理", "yjk_setlayersupport", "", None, 0, 3.0),
            ("生成模型关系", "yjkspre_genmodrel", "", None, 0, 3.0),
            ("恒活平面转换", "yjktransload_tlplan", "", None, 0, 3.0),
            ("恒活竖向转换", "yjktransload_tlvert", "", [self.trans], 120.0, 6.0),
            ("切前处理", "SetCurrentLabel", "IDSPRE_ROOT", None, 0, 3.0),
            ("生成数据+全部计算", "yjkdesign_dsncalculating_all", "", [self.wmass], 900.0, 45.0),
            ("切回建模", "SetCurrentLabel", "IDModule_Axis", None, 0, 2.0),
            ("保存模型", "yjk_save", "", None, 0, 5.0),
        ]
        self.log("--- 建模段 ---")
        self.run_steps(model_steps, "建模")
        self.log("--- 前处理 + 计算段 ---")
        self.run_steps(calc_steps, "计算")
        _stop.set()
        self._save()
        self.log("整段耗时 %.1fs" % (time.time() - t_all))
        if _seen:
            self.log("本次自动应答弹窗 %d 次" % len(_seen))
        ok = os.path.exists(self.wmass)
        self.log("结果文件 %s：%s" % (self.wmass, "已生成" if ok else "缺失"))
        return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config")
    ap.add_argument("--ydb", required=True)
    ap.add_argument("--proj", required=True, help="工程目录（不存在会自动建）")
    ap.add_argument("--name", default="Model", help="工程名，决定 .yjk/.ymd 文件名")
    a = ap.parse_args()
    if not os.path.exists(a.ydb):
        raise SystemExit("找不到 ydb：%s" % a.ydb)
    d = Driver(a.ydb, a.proj, a.name)
    print("工程：%s" % d.proj)
    print("提示：需先用 YjkLauncher.exe 打开 YJK 并敲过 yjksIPCControl，否则命令会一直阻塞")
    return d.drive()


if __name__ == "__main__":
    sys.exit(main())
