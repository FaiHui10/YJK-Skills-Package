# -*- coding: utf-8 -*-
r"""YJK 模态对话框看门狗（后台线程）。

为什么需要它
------------
YJK 有些命令会弹一个模态确认框（例如 `StdSlab_batgenstl` 弹
「施工图已经进行过选筋,是否重新选筋?」）。模态期间 yjks 主窗口被 `Disable`，
IPC 命令从此不返回 —— 表面症状就是"命令挂死"。

（YJKS 7.1.0 / Windows）
  * 这类框是标准 Win32 对话框：窗口类 `#32770`，子控件类 `Button`，
    控件 ID 是标准 `IDYES=6` / `IDNO=7`；
  * `BM_CLICK`、`WM_KEYDOWN`、`WM_CLOSE`、给按钮发键盘消息全都无效；
  * 唯一有效：向对话框发 `WM_COMMAND`，wParam=控件ID，lParam=按钮 hwnd。

作用范围（改这个文件之前先读这一段）
------------------------------------
看门狗只允许在**自有实例**的窗口上动作：

  * `DialogWatch(pid)`：只扫该 pid 的对话框，命中 `RULES` 才答复；
  * `DialogWatch(pid=None)`：**只登记不动手**。pid 未知时无法判断一个框属于
    哪个实例，此时它一个按钮都不点，只把看到的框写进 `noted` 与日志；
  * 拿到自有实例的 pid 之后调用 `narrow(pid)` 收窄范围，此后才答复。

为什么必须这样：`pid=None` 若同时"盯全机所有 yjks.exe"并且"对未命中规则的框
一律回默认答复"，后果就是 —— 同一台机器上**别人正在用**的那个 YJK，只要弹出
保存 / 覆盖 / 重生成一类的确认框，就会被本工具按「是」答掉（审计 S55）。
看门狗看不懂那些框在问什么，也没有资格替用户回答。

未命中规则时**默认不应答**（`DEFAULT = None`）：框留在那里由人处理，
比盲答一个看不懂的框安全。已知的框一律写进 `RULES` 显式答复。

用法
----
    # 启动 yjks 之前就拉起：那时还不知道 pid，所以它只登记不动手
    watch = DialogWatch(log=print)          # 等价于 DialogWatch(None, log=print)
    watch.start()
    pid, ok = boot_yjks(...)                # 拿到自有实例的 pid
    watch.narrow(pid)                       # 收窄之后才开始答复
    ...发命令...
    watch.stop()

    watch = DialogWatch(pid_of_yjks, log=print)   # 也可以直接只盯某个 pid

`DialogWatch` 只处理 `#32770` 顶层可见窗口，避免误点系统对话框。
"""
import ctypes
import sys
import threading
import time
from ctypes import wintypes

_u = ctypes.windll.user32

WM_COMMAND = 0x0111
IDYES, IDNO, IDOK, IDCANCEL = 6, 7, 1, 2

# 关键字 -> 要点的按钮（按顺序匹配，先命中先算）
RULES = [
    ("重新选筋", IDNO),      # batgenstl 已经选过筋，不必重做
    ("是否删除", IDNO),
    ("是否退出", IDNO),
    ("是否补充楼层连接关系分析", IDNO),   # 空模型才会问，别补
    # 「文件不存在」= 命令参数（通常是路径）错了，必须当错误处理，不要点「是」放行。
    # yjk_importydb 收到相对路径时会弹此框，点「是」会**导入空模型**且照样返回 OK，
    # 直到计算阶段才以「模型中没有单元数据」暴露，极难回溯。
    ("文件不存在", IDCANCEL),
    ("不存在", IDCANCEL),
    ("读取错误", IDNO),
]

# 未命中 RULES 时的答复：None = 不自动应答（只登记、只记日志）。
#
# 不要改回 IDYES：YJK 的确认框在问什么只有它自己知道，对一个从来没见过的框回
# 「是」等于替用户确认了一件本包没有理解过的事。宁可让框挂着（命令超时并报出来），
# 也不要盲答 —— 要让某个框自动应答，就把它写进上面的 RULES。
DEFAULT = None

# 命中这些关键字 => 记录为错误（供上层在收工后判定 / 立即判失败）
ERROR_KW = ("文件不存在", "不存在", "读取错误", "非法数据", "出错", "失败")

# 授权/许可类对话框：一律不自动应答，只登记，交给上层"暂停并让用户处理"。
#
# 为什么不能盲答 —— 实测现场：网络许可不可达时 YJK 每约 2 秒弹一次「授权」框，
# 看门狗按默认规则回「是」，YJK 于是被引导去走「单机码激活」，紧接着又弹
# 「序列号输入不正确」，再一次次回「是」—— 对话框循环到 IPC 通道永远起不来，
# 整轮 150s 超时失败，而现场只看到一串「回是」，完全看不出真因是**许可没连上**。
# 授权该由人来决定（连 VPN / 找管理员），机器没有任何依据替用户选「是」还是「否」。
LICENSE_KW = ("授权", "许可", "网络版服务器", "单机码", "序列号", "激活",
              "license", "Licence", "授权码", "SN：", "加密锁", "USB锁")

# 命中 LICENSE_KW 时不发送任何消息（不点任何按钮），让框留在那里等用户处理。
LICENSE_ACTION = None


def yjks_pids():
    """当前所有 yjks.exe 的 pid。不依赖 psutil（用 tasklist）。"""
    import subprocess
    # tasklist 的输出跟随系统 OEM 代码页（本包面向的中文机器上是 GBK），
    # 所以这里指定 gbk；列名/提示行本地化也不影响下面的按列解析。
    try:
        out = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq yjks.exe", "/FO", "CSV", "/NH"],
            capture_output=True, text=True, encoding="gbk", errors="ignore").stdout
    except Exception:                                              # noqa: BLE001
        return []
    pids = []
    for ln in out.splitlines():
        parts = [x.strip('"') for x in ln.split('","')]
        if len(parts) >= 2 and parts[0].lower().startswith("yjks"):
            try:
                pids.append(int(parts[1]))
            except ValueError:
                pass
    return pids


def _text(h):
    n = _u.GetWindowTextLengthW(h)
    b = ctypes.create_unicode_buffer(n + 1)
    _u.GetWindowTextW(h, b, n + 1)
    return b.value


def _class(h):
    b = ctypes.create_unicode_buffer(256)
    _u.GetClassNameW(h, b, 256)
    return b.value


def _children(h):
    out = []

    @ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
    def cb(c, _l):
        out.append(c)
        return True

    _u.EnumChildWindows(h, cb, 0)
    return out


def find_dialogs(pid):
    """返回 [(dlg_hwnd, 标题, 正文)]，只看该 pid 的可见 #32770。"""
    found = []

    @ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
    def cb(h, _l):
        if _class(h) != "#32770" or not _u.IsWindowVisible(h):
            return True
        p = wintypes.DWORD()
        _u.GetWindowThreadProcessId(h, ctypes.byref(p))
        if p.value != pid:
            return True
        body = []
        for c in _children(h):
            if _class(c) == "Static":
                t = _text(c).strip()
                if t:
                    body.append(t)
        found.append((h, _text(h), " ".join(body)))
        return True

    _u.EnumWindows(cb, 0)
    return found


def _decide(title, body):
    """返回 (答复, 是否授权类, 是否错误类)。答复为 None = 不要自动应答。"""
    blob = title + " " + body
    if any(k in blob for k in LICENSE_KW):
        return LICENSE_ACTION, True, False
    for kw, v in RULES:
        if kw in blob:
            return v, False, any(k in blob for k in ERROR_KW)
    return DEFAULT, False, any(k in blob for k in ERROR_KW)


def dismiss(pid, log=None, offset=1.0):
    """关掉该 pid 当前所有模态框；返回扫到的框数。

    授权类与"未命中规则"的框**不点任何按钮**（只在日志里报出来），
    见 `LICENSE_KW` 与 `DEFAULT` 的说明。
    """
    n = 0
    for h, title, body in find_dialogs(pid):
        n += 1
        ans, is_lic, _is_err = _decide(title, body)
        if is_lic or ans is None:
            if log:
                log("  [对话框]%s %r / %r -> 不自动应答（%s）"
                    % ("[授权]" if is_lic else "", title[:30], body[:70],
                       "等用户处理" if is_lic else "未命中规则，等人工处理"))
            continue
        btn = _u.GetDlgItem(h, ans)
        ok = bool(_u.PostMessageW(h, WM_COMMAND, ans & 0xFFFF, btn or 0))
        if log:
            log("  [对话框] %r / %r -> 回%s (%s)"
                % (title[:30], body[:70], "是" if ans == IDYES else "否",
                   "已发" if ok else "发送失败"))
        time.sleep(offset)
    return n


class DialogWatch(threading.Thread):
    """后台线程：每 interval 秒扫一次**自有实例**的模态框，按规则答复。

    `errors` 收集所有正文命中 `ERROR_KW` 的弹框 —— 这些是**真错误**，
    上层应在关键步骤后检查它。绝不能只看 `RunCmd` 的返回值。
    """

    def __init__(self, pid=None, log=None, interval=1.2, offset=0.8):
        """`pid=None` = 实例未知：**只登记不动手**，等 `narrow(pid)` 收窄。

        不要在这里"顺手"改成盯住所有 yjks.exe 并应答：那会把同一台机器上
        别人的 YJK 的对话框也答掉 —— 见模块开头的「作用范围」。
        """
        threading.Thread.__init__(self, daemon=True)
        self.pid = pid
        self.log = log
        self.interval = interval
        self.offset = offset
        self._stop = threading.Event()
        # seen: 所有登记过的框 [(标题, 正文, 答复)]，答复为 None = 没有自动应答。
        #       只有 PostMessage 真的发出去了，这里才记答复值 —— 记"打算答复"
        #       会让发送失败也看起来像"已处理"（审计 S22）。
        self.seen = []
        self.errors = []        # 正文命中 ERROR_KW 的，单独留一份
        self.license = []       # 授权/许可类：不自动应答，交上层暂停等用户
        self.failed = []        # 应答发送失败（PostMessage 返回 0）：框可能还挂着
        self.unanswered = []    # 已收窄，但未命中规则、按默认不自动应答的框
        self.noted = []         # pid 未知（未收窄）阶段只登记的框：[(pid, 标题, 正文)]
        self._noted_k = set()   # 上面那份的去重键 (pid, hwnd)，避免每轮重复登记

    def narrow(self, pid):
        """把监视范围收窄到**自有实例**。

        为什么必须收窄：`pid=None` 时范围是"所有 yjks.exe"，而在那之前本文件
        对实例归属一无所知。拿到自有 pid 之后立刻收窄，才不会碰到别人的窗口。
        启动阶段不得不 `pid=None`（那时 pid 还不知道），那段时间只登记不动手。
        """
        if pid:
            self.pid = int(pid)

    def _note_only(self, pid, h, title, body):
        """pid 未收窄时的兜底：只登记，不点任何按钮。同一个框只登记一次。"""
        k = (pid, h)
        if k in self._noted_k:
            return
        self._noted_k.add(k)
        self.noted.append((pid, title, body))
        if self.log:
            self.log("  [对话框][只登记] pid=%s %r / %r -> 未收窄，不动作（等人工处理）"
                     % (pid, title[:30], body[:70]))

    def _answer(self, h, title, body):
        ans, is_lic, is_err = _decide(title, body)
        if is_lic:
            self.license.append((title, body))
            self.seen.append((title, body, None))
            if self.log:
                self.log("  [对话框][授权] %r -> 不自动应答（等用户处理）" % body[:80])
            return
        if is_err:
            self.errors.append((title, body))
        if ans is None:
            if not is_err:
                self.unanswered.append((title, body))
            self.seen.append((title, body, None))
            if self.log:
                self.log("  [对话框]%s %r / %r -> 默认不自动应答（未命中规则，等人工处理）"
                         % ("[错误]" if is_err else "", title[:30], body[:70]))
            return
        if is_err:
            if self.log:
                self.log("  [对话框][错误] %r -> 回%s"
                         % (body[:80], "是" if ans == IDYES else "否"))
        elif self.log:
            self.log("  [对话框] %r / %r -> 回%s"
                     % (title[:30], body[:70], "是" if ans == IDYES else "否"))
        btn = _u.GetDlgItem(h, ans)
        ok = bool(_u.PostMessageW(h, WM_COMMAND, ans & 0xFFFF, btn or 0))
        if ok:
            self.seen.append((title, body, ans))
        else:
            # 旧版在这里不看返回值，还先把"打算答复"记进 seen —— 框没关掉也会
            # 表现为"已处理 N 条、0 错误"（审计 S22）。现在只有真发出去了才在
            # seen 里记答复值，失败单独进 failed 并写一行显式日志。
            self.seen.append((title, body, None))
            self.failed.append((title, body, ans))
            if self.log:
                self.log("  [对话框][应答失败] %r -> PostMessage 返回 0（框可能还挂着）"
                         % body[:70])

    def _scan_once(self):
        """扫一轮。已收窄 -> 按规则答复；未收窄 -> 只登记。"""
        if self.pid:
            for h, title, body in find_dialogs(self.pid):
                self._answer(h, title, body)
                time.sleep(self.offset)
        else:
            for p in yjks_pids():
                for h, title, body in find_dialogs(p):
                    self._note_only(p, h, title, body)
                    time.sleep(self.offset)

    def run(self):
        while not self._stop.is_set():
            try:
                self._scan_once()
            except Exception as e:                                 # noqa: BLE001
                if self.log:
                    self.log("  [对话框] 看门狗异常 %r" % e)
            self._stop.wait(self.interval)

    def stop(self):
        self._stop.set()


def _utf8_console():
    """让输出在任何控制台编码下都不崩（GBK 下把编不出的字符替换掉）。

    为什么需要：本文件会把**窗口标题与对话框正文**原样打印出来（`%r`），
    那是 YJK 自己的字符串，本包管不了；默认 GBK 控制台下 print 遇到 cp936
    编不出的字符会抛 UnicodeEncodeError，一个诊断命令不该因为日志字符而崩掉。

    只在 CLI 入口（`main()`）调用：本模块会被别的脚本 import 当库用，
    模块顶层改 stdout 会污染调用方进程。
    """
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass


def main():
    _utf8_console()
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("pid", type=int, nargs="?",
                    help="yjks.exe 的 pid；省略则列出当前所有 yjks.exe 及其对话框")
    a = ap.parse_args()
    if a.pid:
        for h, t, b in find_dialogs(a.pid):
            print("dlg %s  title=%r  body=%r" % (h, t, b))
        print("dismiss ->", dismiss(a.pid, print))
    else:
        ps = yjks_pids()
        print("yjks.exe pids:", ps or "（没有在跑）")
        for p in ps:
            for h, t, b in find_dialogs(p):
                print("  pid=%s dlg %s  title=%r  body=%r" % (p, h, t, b))
    return 0


if __name__ == "__main__":
    sys.exit(main())
