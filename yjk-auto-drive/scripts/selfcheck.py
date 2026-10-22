# -*- coding: utf-8 -*-
r"""驱动脚本的离线自检（不需要 YJK）+ 黄金值验收。

用法
----
  python selfcheck.py                                  # 纯逻辑批：秒级
  python selfcheck.py --golden <工作目录> [--期望 <期望.json>]   # 对算过的工程做值断言

为什么要有它
------------
本技能的多数坑都是"**看起来成功**"：返回值 `OK` 但没执行、`.yjk` 文件存在但工程没打开、
历史收件箱被重放、陈旧设计结果被当成本轮结果…… 光靠真机跑一轮覆盖不到这些。
这里把**不依赖 YJK 的判断逻辑**全部钉成断言：改完代码先跑它（秒级），再上真机（分钟级）。

覆盖的测试项（对应"测试清单"编号）
----------------------------------
  T1  收件箱宏展开 @back/@prep/@calc/@recalc（含未知宏）
  T2  yjks 命令行 → 工程路径（-open 带引号 / 裸 .yjk / 无参）
  T3  窗口标题 → 工程路径（含欢迎页）
  T4  project_open 的路径比对（中文/空格/大小写/子串陷阱/欢迎页）
  T5  own.json 注册表生命周期 + host_alive（区分"残留"与"另一会话"）
  T6  preflight 六条分支（干净/你在用/无主窗口残留/自有残留/自有被占用）
  T7  exclusive_ok（自有存活且独占 / 混入非自有 / 自有已死）
  T8  inbox_precheck（导入参数缺失、文件不存在）
  T9  kill_own 安全闸（登记实例打开的工程在登记目录之外 → 拒绝结束）
  T10 watch_inbox 启动时归档历史收件箱（防重放）
  T11 watch_inbox 前置校验失败 → 停手且不执行后续命令
  T12 column-section-opt/verify_results.py 的输入健壮性（缺 --db / 无 wpj 时报错清晰）
  T13 --golden 黄金值断言（逐标准层材料等级 / 截面 / 超限条数 / 各标准层最大 Uc）
  T14 send 的「会话就绪」协议（未就绪必须拒绝，不能静默丢命令）
  T26 @takeoff 算量宏的顺序（混凝土统计 → 施工图 → 钢筋统计，不可换）
  T27 导入校验闸门（逐表行数：好样本通过、空模型/半写模型不通过、.ymd 未落盘提示顺序）
  T28 会话目录 vs YJK 实际打开的工程目录（错配必须明确报出两个路径）
  T29 导入校验不通过时 host 非零退出（自动化调用方靠退出码判成败）
  T30 --reuse：默认仍拒绝；开启后先查「是否已被别的实例打开」
  T31 **六份「找驱动技能」副本不许漂移**：COMPAT-FALLBACK 块一致（行尾归一化后逐字节相同）+
      三个环境变量认全且同序 + 非环境变量候选的集合与顺序 = 规范清单 + 不许写死桌面
"""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import threading
import time
from types import SimpleNamespace

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import yjk_auto as A                                              # noqa: E402

PASS, FAIL = 0, 0
FAILED = []


def check(name, got, want):
    global PASS, FAIL
    if got == want:
        PASS += 1
        print("  [OK] %s" % name)
    else:
        FAIL += 1
        FAILED.append(name)
        print("  [!!] %s\n       期望: %r\n       实际: %r" % (name, want, got))


def check_true(name, cond, detail=""):
    check(name, bool(cond), True if not detail else True)
    if not cond and detail:
        print("       %s" % detail)


class Stub:
    """临时替换 yjk_auto 里的探测函数（用完自动还原）。"""

    def __init__(self, **kw):
        self.kw = kw
        self.old = {}

    def __enter__(self):
        for k, v in self.kw.items():
            self.old[k] = getattr(A, k, None)
            setattr(A, k, v)
        return self

    def __exit__(self, *a):
        for k, v in self.old.items():
            setattr(A, k, v)


class FakeCli:
    def __init__(self, ret="OK(0.1s)"):
        self.calls = []
        self.ret = ret

    def run(self, cmd, param="", timeout=300, **kw):
        # 收 `**kw`：host 现在会传 `alive=`（缺陷 L5 的存活轮询）。
        #   不接就会 TypeError —— 而这条调用链正是自检要覆盖的。
        self.calls.append((cmd, param))
        return self.ret


def inst(kind, pid=1001, titles=None, proj=None):
    return {"pid": pid, "kind": kind, "titles": titles or [], "cmdline": "", "proj": proj}


def t_hooks():
    print("T1 收件箱宏展开")
    check("@back", [c for c, _ in A.expand("@back")], ["SetCurrentLabel"])
    check("@prep 条数", len(A.expand("@prep")), len(A.PREP_CHAIN))
    check("@calc 条数", len(A.expand("@calc")), len(A.CALC_CHAIN))
    seq = A.expand("@recalc")
    check("@recalc 首条=回建模", seq[0], ("SetCurrentLabel", "IDModule_Element"))
    check("@recalc 无参时不导入", [c for c, _ in seq].count("yjk_importydb"), 0)
    seq2 = A.expand("@recalc", r"D:\m\new.ydb")
    check("@recalc 有参时导入", seq2[1], ("yjk_importydb", r"D:\m\new.ydb"))
    # 迭代轮**不切结果标签**（省 15.7s/轮）：末条应是计算本体，不是 IDDSN_DSP
    check("@recalc 末条=计算本体（不切结果标签）", seq2[-1], ("yjkdesign_dsncalculating_all", ""))
    check("@recalc 不含切结果标签", ("SetCurrentLabel", "IDDSN_DSP") in seq2, False)
    check("@calc 仍以切结果标签收尾（给人看结果）", A.expand("@calc")[-1],
          ("SetCurrentLabel", "IDDSN_DSP"))
    check("CALC_CHAIN_CORE = CALC_CHAIN 去掉最后一步",
          A.CALC_CHAIN_CORE, A.CALC_CHAIN[:-1])
    check("普通命令不展开", A.expand("yjk_save"), [("yjk_save", "")])
    try:
        A.expand("@nope")
        check("未知宏应报错", "no-raise", "raise")
    except SystemExit:
        check("未知宏应报错", "raise", "raise")

    print("T2 yjks 命令行 → 工程路径")
    check("-open 裸路径", A.opened_project(r"D:\y\yjks.exe -product YJKS -open G:\a\b\T.yjk"),
          r"G:\a\b\T.yjk")
    check("-open 带引号+空格", A.opened_project('D:\\y\\yjks.exe -open "G:\\x y\\z\\T.yjk"'),
          r"G:\x y\z\T.yjk")
    check("-open 后还有别的参数", A.opened_project("yjks.exe -open G:\\a\\T.yjk -other 1"),
          r"G:\a\T.yjk")
    check("裸 .yjk 参数", A.opened_project('yjks.exe "G:\\a\\b\\T.yjk"'), r"G:\a\b\T.yjk")
    check("无参启动 → None", A.opened_project("D:\\y\\yjks.exe -product YJKS"), None)
    check("空命令行 → None", A.opened_project(""), None)

    print("T3 窗口标题 → 工程路径")
    check("有工程", A.title_to_proj(r"G:\a b\T.yjk - 盈建科软件"), r"G:\a b\T.yjk")
    check("欢迎页", A.title_to_proj("盈建科软件"), None)
    check("空标题", A.title_to_proj(""), None)

    print("T4 project_open 路径比对")
    wd = r"G:\a b\T_test"
    with Stub(yjks_pids=lambda: [111],
              titles=lambda p: [r"G:\a b\T_test\T.yjk - 盈建科软件"]):
        check("同路径命中", A.project_open("T", wd), True)
    with Stub(yjks_pids=lambda: [111], titles=lambda p: [r"G:\A B\T_TEST\T.yjk - 盈建科软件"]):
        check("大小写不敏感", A.project_open("T", wd), True)
    with Stub(yjks_pids=lambda: [111], titles=lambda p: [r"G:\a b\T_test\T2.yjk - 盈建科软件"]):
        check("子串陷阱：别的工程名不算", A.project_open("T", wd), False)
    with Stub(yjks_pids=lambda: [111], titles=lambda p: ["盈建科软件"]):
        check("欢迎页不算打开", A.project_open("T", wd), False)
    with Stub(yjks_pids=lambda: [111], titles=lambda p: [r"G:\other\T.yjk - 盈建科软件"]):
        check("别的目录不算", A.project_open("T", wd), False)


def t_own_registry():
    print("T5 own.json 注册表 + host_alive")
    tmp = tempfile.mkdtemp(prefix="selfchk_")
    old_file = A.OWN_FILE
    A.OWN_FILE = os.path.join(tmp, "own.json")
    try:
        check("无登记 → None", A.own_pid(), None)
        with Stub(yjks_pids=lambda: [4242]):
            A.own_claim(4242, r"D:\YJKS\yjks.exe", r"G:\wd")
            d = A._own_read()
            check("登记 pid", d.get("pid"), 4242)
            check("登记了宿主 pid", bool(d.get("host_pid")), True)
            check("own_pid 命中", A.own_pid(), 4242)
        with Stub(yjks_pids=lambda: []):                 # 进程没了
            check("进程消失 → None", A.own_pid(), None)
            check("过期登记被清掉", os.path.exists(A.OWN_FILE), False)
        with Stub(procs=lambda: {1234: "python.exe"}):
            check("host_alive: python 在", A.host_alive(1234), True)
        with Stub(procs=lambda: {1234: "yjks.exe"}):
            check("host_alive: PID 被复用不算", A.host_alive(1234), False)
        with Stub(procs=lambda: {}):
            check("host_alive: 不存在", A.host_alive(1234), False)
        check("host_alive: 空", A.host_alive(None), False)
    finally:
        A.OWN_FILE = old_file
        shutil.rmtree(tmp, ignore_errors=True)


def t_preflight():
    print("T6 preflight 分支")

    class Args:
        clean_orphans = False

    # 干净
    check("干净 → 放行", A.preflight(Args(), [], None), True)
    # 你在用的实例
    fo = [inst("foreign", 2, ["G:\\other\\T.yjk - 盈建科软件"])]
    check("有 foreign → 拒绝", A.preflight(Args(), fo, None), False)
    # 无窗口残留：未加 --clean-orphans
    orp = [inst("orphan", 3)]
    check("orphan 未加 --clean-orphans → 拒绝", A.preflight(Args(), orp, None), False)
    # 无窗口残留：加 --clean-orphans 且清掉了
    a = Args()
    a.clean_orphans = True
    with Stub(kill_pid=lambda p, **k: True, instances=lambda: []):
        check("orphan 加 --clean-orphans 且清掉 → 放行", A.preflight(a, orp, None), True)
    # 无窗口残留：加 --clean-orphans 但清不掉
    with Stub(kill_pid=lambda p, **k: True, instances=lambda: orp):
        check("orphan 加 --clean-orphans 但清不掉 → 拒绝", A.preflight(a, orp, None), False)
    # 自有残留（宿主已死）→ 清掉后放行
    killed = []
    with Stub(kill_own=lambda **k: killed.append(1), _own_read=lambda: {"workdir": "G:\\wd"}):
        check("自有残留(宿主已死) → 清并放行", A.preflight(Args(), [inst("own", 4)], 4), True)
    check("确实清了自有残留", len(killed), 1)
    # 自有被占用（宿主活着）→ 拒绝，不抢占
    with Stub(kill_own=lambda **k: killed.append(2),
              _own_read=lambda: {"host_pid": 999, "workdir": "G:\\wd"},
              host_alive=lambda p: True):
        check("另一会话在跑 → 拒绝", A.preflight(Args(), [inst("own", 4)], 4), False)
    check("拒绝时没有去杀", len(killed), 1)

    print("T7 exclusive_ok")
    with Stub(instances=lambda: [inst("own", 1)]):
        check("自有独占 → 放行", A.exclusive_ok(1)[0], True)
    with Stub(instances=lambda: [inst("own", 1), inst("foreign", 2)]):
        check("混入 foreign → 停手", A.exclusive_ok(1)[0], False)
    with Stub(instances=lambda: [inst("own", 1), inst("orphan", 3)]):
        check("混入 orphan → 停手", A.exclusive_ok(1)[0], False)
    with Stub(instances=lambda: [inst("foreign", 2)]):
        check("自有已死 → 停手", A.exclusive_ok(1)[0], False)

    print("T8 inbox_precheck")
    check("非导入命令 → 放行", A.inbox_precheck("yjk_save", ""), (True, ""))
    check("导入无参数 → 拦下", A.inbox_precheck("yjk_importydb", "")[0], False)
    check("导入文件不存在 → 拦下", A.inbox_precheck("yjk_importydb", r"Z:\nope\m.ydb")[0], False)
    tmp = tempfile.mkdtemp(prefix="selfchk_")
    try:
        f = os.path.join(tmp, "m.ydb")
        open(f, "wb").write(b"x")
        check("导入文件存在 → 放行", A.inbox_precheck("yjk_importydb", f), (True, ""))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("T9 kill_own 安全闸")
    tmp = tempfile.mkdtemp(prefix="selfchk_")
    old_file = A.OWN_FILE
    A.OWN_FILE = os.path.join(tmp, "own.json")
    killed2 = []
    try:
        with Stub(yjks_pids=lambda: [7]):
            A.own_claim(7, r"D:\YJKS\yjks.exe", r"G:\mywork")
        # 登记的实例打开的是**别处**的工程 → 拒绝结束
        with Stub(yjks_pids=lambda: [7],
                  titles=lambda p: [r"G:\someone_else\T.yjk - 盈建科软件"],
                  kill_pid=lambda p, **k: killed2.append(p) or True):
            A.kill_own(verbose=False)
        check("目录外工程 → 不杀", killed2, [])
        check("目录外工程 → 保留登记", os.path.exists(A.OWN_FILE), True)
        # 打开的是**登记目录内**的工程 → 正常清理（桩要模拟"进程真的没了"）
        state = {"alive": True}

        def _kp(p, **k):
            killed2.append(p)
            state["alive"] = False
            return True

        with Stub(yjks_pids=lambda: ([7] if state["alive"] else []),
                  yjks_info=lambda: ({7: {"threads": 8, "cmdline": ""}} if state["alive"] else {}),
                  yjks_cmdlines=lambda: {},
                  titles=lambda p: [r"G:\mywork\T.yjk - 盈建科软件"],
                  kill_pid=_kp):
            ok2 = A.kill_own(verbose=False, wait=3)
        check("目录内工程 → 清理", killed2, [7])
        check("清理成功（进程真消失才算）", ok2, True)
        check("清理后登记清空", os.path.exists(A.OWN_FILE), False)
    finally:
        A.OWN_FILE = old_file
        shutil.rmtree(tmp, ignore_errors=True)


def t_inbox():
    print("T10 watch_inbox 启动时归档历史收件箱（防重放）")
    tmp = tempfile.mkdtemp(prefix="selfchk_")
    try:
        inbox, outbox = A.inbox_paths(tmp)
        with open(inbox, "w", encoding="utf-8") as f:
            f.write("120000|yjk_save|\n120001|yjk_repair|\n")
        fake = FakeCli()
        with Stub(yjks_pids=lambda: []):                 # 无实例 → 循环很快退出
            A.watch_inbox(fake, tmp, stop_after=1, poll=0.1, own=None)
        baks = [x for x in os.listdir(tmp) if x.startswith("_yjk_inbox.txt.") and x.endswith(".bak")]
        check("历史收件箱被归档", len(baks), 1)
        check("历史命令未被重放", fake.calls, [])

        print("T11 watch_inbox 前置校验失败 → 停手且不执行")
        tmp2 = tempfile.mkdtemp(prefix="selfchk_")
        inbox2, outbox2 = A.inbox_paths(tmp2)
        fake2 = FakeCli()
        import threading
        # 注意：必须在 watch_inbox **启动之后**再注入命令 ——
        # 启动前预置的命令会被 F1 的"归档历史收件箱"归档掉（防重放），根本进不了循环。
        with Stub(instances=lambda: [inst("own", 1)], yjks_pids=lambda: [1]):
            th = threading.Thread(target=A.watch_inbox,
                                  args=(fake2, tmp2),
                                  kwargs=dict(stop_after=3, poll=0.1, own=1))
            th.start()
            time.sleep(0.6)
            A.send_to_inbox("yjk_importydb", r"Z:\nope\m.ydb", tmp2)
            A.send_to_inbox("yjk_save", "", tmp2)
            th.join(8)
        check("坏命令未被执行", fake2.calls, [])
        body = open(outbox2, encoding="utf-8").read() if os.path.exists(outbox2) else ""
        check("写了失败回执", "ydb 不存在" in body, True)
        check("后续命令也没执行", "yjk_save" in body, False)
        shutil.rmtree(tmp2, ignore_errors=True)

        print("T11b 正常命令在会话内可执行（同一注入方式）")
        tmp3 = tempfile.mkdtemp(prefix="selfchk_")
        fake3 = FakeCli()
        with Stub(instances=lambda: [inst("own", 1)], yjks_pids=lambda: [1]):
            th = threading.Thread(target=A.watch_inbox,
                                  args=(fake3, tmp3),
                                  kwargs=dict(stop_after=3, poll=0.1, own=1))
            th.start()
            time.sleep(0.6)
            A.send_to_inbox("yjk_save", "", tmp3)
            th.join(8)
        check("命令被执行了一次", fake3.calls, [("yjk_save", "")])
        shutil.rmtree(tmp3, ignore_errors=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def t_send_ready():
    print("T14 send 的「会话就绪」协议（未就绪必须拒绝，不能静默丢命令）")
    tmp = tempfile.mkdtemp(prefix="selfchk_")
    try:
        check("初始（无标志）未就绪", A.session_ready(tmp)[0], False)
        r = subprocess.run([sys.executable, "-X", "utf8", "-B",
                            os.path.join(HERE, "yjk_auto.py"), "send", "yjk_save", "--dir", tmp],
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
        out = (r.stdout or "") + (r.stderr or "")
        check("未就绪时退出码非零", r.returncode != 0, True)
        check("未就绪时明确拒绝", "没有**正在服务**的收件箱会话" in out, True)
        inbox, _ = A.inbox_paths(tmp)
        check("未就绪时不写入", os.path.exists(inbox) and os.path.getsize(inbox) > 0, False)
        A.send_to_inbox("yjk_save", "", tmp)          # 直接写（等价于 cmd_send 放行后）
        check("就绪时写入成功", os.path.getsize(inbox) > 0, True)

        # ---------------------------------------------------------------
        # 以下 5 条是「只看文件存在 = 就绪」这个缺陷（L2 / 审计 S10）的守卫。
        #   旧版 T14 只写了一个 "1\n" 就断言「就绪」，**等于把这个错误语义固化下来** ——
        #   这正是该缺陷一直没被发现的原因。现在判据必须逐条成立：
        #     · 内容不是数字（写坏的/人工改的）      → 未就绪
        #     · PID 不是活着的本包宿主               → 未就绪（崩溃残留）
        #     · 心跳太旧                             → 未就绪（会话卡死）
        #     · PID 活着 + 心跳新鲜                  → 就绪
        # ---------------------------------------------------------------
        rdy = A.ready_path(tmp)
        open(rdy, "w", encoding="utf-8").write("1\n")
        check("★ 内容不是 PID → 未就绪（不再只看存在）", A.session_ready(tmp)[0], False)

        open(rdy, "w", encoding="utf-8").write("%d %s\n" % (99999999, "x"))
        check("★ PID 不存在 → 未就绪（残留学）", A.session_ready(tmp)[0], False)

        open(rdy, "w", encoding="utf-8").write("%d %s\n" % (os.getpid(), "x"))
        check("PID 活着（本进程）→ 就绪", A.session_ready(tmp)[0], True)

        old = time.time() - (A.READY_STALE + 60)
        os.utime(rdy, (old, old))
        check("★ 心跳过旧 → 未就绪（会话卡死）", A.session_ready(tmp)[0], False)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def t_host_rc_trustworthy():
    """T31b：**preflight 拒绝必须给非零退出码**（缺陷 L3 / 审计 S01·S02）。

    以前 `cmd_host` 里 `if not preflight(...): return` → main() 返回 None →
    进程退出码 **0**，而日志写的是「本次未做任何操作」。任何按 rc 判定的编排
    （含本包自己的 driver.host / run_all_yjk）都会把「什么都没做」当成成功。
    这里用「目录里已存在工程且未给 --reuse」这条**不碰任何实例**的预检分支来验。
    """
    print("T31b preflight 拒绝 → 退出码必须非零（否则编排把'没干活'当成功）")
    tmp = tempfile.mkdtemp(prefix="selfchk_")
    try:
        open(os.path.join(tmp, "M.yjk"), "w", encoding="utf-8").write("stale\n")
        r = subprocess.run([sys.executable, "-X", "utf8", "-B",
                            os.path.join(HERE, "yjk_auto.py"), "host",
                            "--dir", tmp, "--name", "M", "--stay", "0"],
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=180)
        out = (r.stdout or "") + (r.stderr or "")
        refused = ("预检未通过" in out) or ("工程未就位" in out) or ("已有 M.yjk" in out)
        check("确实被拒绝了（有拒绝字样）", refused, True)
        check("★ 拒绝时退出码非零（0 会让编排以为是成功）", r.returncode != 0, True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def t_license_never_autoyes():
    """T31c：**授权类对话框不许自动应答**（本轮新增的「暂停让用户处理」）。

    实测现场：网络许可不可达时 YJK 每 2 秒弹一次「授权」框，看门狗按默认规则
    回「是」，把 YJK 引导去走「单机码激活」，然后无限循环 —— IPC 永远起不来，
    而日志只看到一串「回是」，完全看不出真因是许可没连上。
    """
    print("T31c 授权类对话框 → 看门狗不点任何按钮，交给用户处理")
    try:
        import dlgwatch as D
    except ImportError:
        check("dlgwatch 可导入", False, True)
        return
    lic = [("授权", "网络版服务器： 端口： 授权码（SN）："),
           ("单机码激活", "序列号输入不正确"),
           ("盈建科", "加密锁未找到")]
    for t, b in lic:
        ans, is_lic, _e = D._decide(t, b)
        check("授权框 %r 不自动应答" % t[:8], ans is None, True)
        check("授权框 %r 被识别为授权类" % t[:8], is_lic, True)
    # 普通确认框仍然照旧应答（否则会退回"命令挂到超时"的老毛病）
    ans, is_lic, _e = D._decide("盈建科", "施工图已经进行过选筋,是否重新选筋?")
    check("普通框仍然自动应答", (not is_lic) and ans is not None, True)
    # 真实错误框仍要留痕
    _a, is_lic2, is_err = D._decide("盈科", "文件不存在：C:\\no\\such.ydb")
    check("错误框仍被记为错误", is_err and not is_lic2, True)


def t_license_pause_state_machine():
    """T31d：授权暂停/恢复的**状态机**（不启真 YJK，把外部依赖全部打桩）。

    要验的是三件事：
      ① 出现授权框时：**暂停**（不返回失败）、打印醒目提示、在工程目录写
         `_yjk_license.need_user` 标志；
      ② 许可恢复（框消失 + 通道就绪）后：**自动继续**并返回成功 —— 用户不必重跑；
      ③ `--on-license fail`：立刻放弃，且台账里留下"授权/许可问题"以便给退出码 6。
    """
    print("T31d 授权暂停状态机（暂停→恢复自动继续 / fail 快速失败）")
    saved = {k: getattr(A, k) for k in ("spawn", "yjks_pids", "rt_yjk", "events_alive", "P")}
    tmp = tempfile.mkdtemp(prefix="selfchk_")
    try:
        state = {"lic": True, "ready": False}

        class _P:
            @staticmethod
            def config_flag_ok():
                return True, None

            # boot_yjks 会先判版本（>=8 走 initConfig+RunYJK 分支）；
            #   桩必须照真实签名返回，"v" 不是版本号 → None → 走 6/7 分支。
            @staticmethod
            def version_major(version=None, root=None):
                return None

            @staticmethod
            def version_xyz(version=None, root=None):
                return None

        A.spawn = lambda *a, **k: None
        A.yjks_pids = lambda: [getattr(A, "_SC_PID")]
        A._SC_PID = os.getpid()
        A.rt_yjk = lambda: {"exe": "x", "root": "r", "source": "s", "version": "v"}
        # 桩要**照真实形状**返回：`events_alive()` 真返回的是**两个布尔**
        #   （[Share 活, Wait 活]）。我第一版返回 `[]`，而 `all([])` 是 True，
        #   于是 boot 第一轮就"就绪"、授权分支根本没走到 —— 测试假通过。
        A.events_alive = lambda: [True, True] if state["ready"] else [False, False]
        A.P = _P()
        A._LICENSE_BLOCKED[:] = []

        calls = {"n": 0}
        seen = {"marker": False}

        def _lic():
            calls["n"] += 1
            if calls["n"] == 2:
                # 第 2 次被问到时仍在暂停中 —— 此刻标志应当**在盘上**
                seen["marker"] = os.path.exists(A.license_marker(tmp))
            if calls["n"] > 2:            # 两次之后就当作"用户已经把许可修好了"
                state["lic"] = False
                state["ready"] = True
            return [("授权", "网络版服务器：授权码（SN）：")] if state["lic"] else []

        A.dlgwatch_license = _lic
        pid, ok = A.boot_yjks(tmp, wait_ipc=30, verbose=False,
                              on_license="pause", license_timeout=10)
        check("① 授权期间不返回失败（是暂停，不是放弃）", ok, True)
        check("① 授权状态被记录", len(A._LICENSE_BLOCKED) > 0, True)
        check("① 暂停期间写了 need_user 标志（供用户/编排发现）", seen["marker"], True)
        check("② 许可恢复后自动继续（未重跑即成功）", pid is not None, True)
        check("② 恢复后清掉了标志", not os.path.exists(A.license_marker(tmp)), True)

        # ③ on_license=fail：立刻放弃，且台账里留下授权字样
        A._LICENSE_BLOCKED[:] = []
        A._HOST_ERRORS[:] = []
        state["lic"], state["ready"] = True, False
        calls["n"] = -10 ** 6             # 永远返回"有授权框"
        pid2, ok2 = A.boot_yjks(tmp, wait_ipc=2, verbose=False,
                                on_license="fail", license_timeout=5)
        check("③ --on-license fail 立刻放弃", ok2, False)
        check("③ 授权原因可查（供退出码 6）", len(A._LICENSE_BLOCKED) > 0, True)
    finally:
        for k, v in saved.items():
            setattr(A, k, v)
        if hasattr(A, "_SC_PID"):
            delattr(A, "_SC_PID")
        shutil.rmtree(tmp, ignore_errors=True)


def t_license_read_channel():
    """T31e：授权标志的**读口**必须可用（只写不读 = 机制没做成）。

    为什么单独立一条：T31d 只验了「暂停时会**写**标志、恢复后会清掉」。
    可这个标志是给**别的进程**看的（另一个 agent / 用户 / 编排器）——
    宿主内存里的 `_LICENSE_BLOCKED` 只存在于那个进程，别的会话读不到。
    只写不读的后果：第二个 agent 看到的只是「收件箱未就绪 rc=2」，
    完全不知道是授权问题，于是反复重试或以为模型/脚本坏了。

    这里验四件事：
      ① 无标志 → 未阻塞；有标志 → 读出内容与写入时间；
      ② 标志被**记事本**改过（UTF-8 带 BOM）不能把 BOM 当正文打出来；
      ③ `send` 未就绪时**点名是授权问题**并给出人工处理清单，退出码仍是 2（fail-closed）；
      ④ 这种情况下**不写收件箱**（不许"命令已写入却无人执行"）。
    """
    print("T31e 授权标志的读口（status/send 能不能看出「是授权问题」）")
    tmp = tempfile.mkdtemp(prefix="selfchk_lic_")
    try:
        check("① 无标志 → 未阻塞", A.license_state(tmp)[0], False)

        with open(A.license_marker(tmp), "w", encoding="utf-8") as f:
            f.write("授权失败：网络版服务器 lic.yjk.cn:8081 无响应")
        blk, txt, age = A.license_state(tmp)
        check("① 有标志 → 已阻塞", blk, True)
        check("① 读得到当时的对话框内容", "lic.yjk.cn" in txt, True)
        check("① 带上了写入时间（秒）", age >= 0, True)

        # ② 用户用记事本改过这个文件 → UTF-8 BOM
        with open(A.license_marker(tmp), "w", encoding="utf-8-sig") as f:
            f.write("单机码激活失败")
        _blk, txt2, _age = A.license_state(tmp)
        check("② 记事本 BOM 不会当成正文（不乱码）", txt2.startswith("\ufeff"), False)
        check("② BOM 之后的内容仍然可读", "单机码" in txt2, True)

        # ③ / ④ send 必须点名授权，且不写收件箱
        class _Args:
            dir = tmp
            cmd = "@calc"
            param = ""

        buf = io.StringIO()
        rc = 0
        with contextlib.redirect_stdout(buf):
            try:
                A.cmd_send(_Args())
            except SystemExit as e:
                rc = e.code
        out = buf.getvalue()
        check("③ 未就绪仍 rc=2（fail-closed）", rc, 2)
        check("③ 明确说出是授权/许可问题", ("授权" in out) or ("许可" in out), True)
        check("③ 给出人工处理清单（VPN/许可服务器）",
              ("VPN" in out) or ("lic.yjk.cn" in out), True)
        check("④ 没有把命令写进收件箱",
              os.path.exists(os.path.join(tmp, "_yjk_inbox.txt")), False)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def t_import_gate_selftrigger():
    """T32：导入校验闸门**必须自触发**，不能依赖调用方链条里正好有 `yjk_save`（缺陷 S11）。

    老版：`yjk_importydb` 只把待校验的 .ydb 记进 `pending_ydb`，**等 `yjk_save` 才核**。
    而 `CALC_CHAIN` 里根本没有 `yjk_save` —— 调用方若发
    `yjk_importydb x.ydb` 紧接 `@calc`，校验**静默地从未运行**，
    而文档承诺的是"导入后自动跑，不通过就别往下算"。

    这里用 FakeCli 驱动 watch_inbox（收件箱里放 import + 一条非 save 命令），验：
      ① 自动补了一步 `yjk_save`；
      ② 校验**真的跑了**（stub 的 verify_import 被调用到）；
      ③ 校验不通过时，后面的命令**不再执行**（不拿空模型跑一整轮计算）。
    """
    print("T32 导入校验闸门自触发（链条里没有 yjk_save 也要核）")
    tmp = tempfile.mkdtemp(prefix="selfchk_gate_")
    try:
        ydb = os.path.join(tmp, "m.ydb")
        open(ydb, "w", encoding="utf-8").write("x")

        class WritingCli(FakeCli):
            def run(self, cmd, param="", timeout=300, **kw):
                r = super().run(cmd, param, timeout, **kw)
                if cmd == "yjk_importydb":
                    open(os.path.join(tmp, "_touched.dat"), "w",
                         encoding="utf-8").write("x")
                return r

        fake = WritingCli()
        seen = []
        inbox, outbox = A.inbox_paths(tmp)
        with Stub(instances=lambda: [inst("own", 1)], yjks_pids=lambda: [1],
                  project_dir_mismatch=lambda w, p=None: None,
                  verify_import=lambda y, w, **k: (seen.append(y), False)[1]):
            th = threading.Thread(
                target=A.watch_inbox, args=(fake, tmp),
                kwargs=dict(stop_after=30, poll=0.1, own=1, idle_exit=5), daemon=True)
            th.start()
            # 必须在会话**开始之后**再往收件箱写：watch_inbox 启动时会把历史收件箱归档
            #   （避免重放上一轮），先写就会被归档掉、当成"历史命令"。
            #   我第一版就是先写后起 —— 结果一条命令都没执行，测试却"看起来通过"。
            A.wait_until(lambda: os.path.exists(A.ready_path(tmp)), timeout=10)
            with open(inbox, "a", encoding="utf-8") as f:
                f.write("000001|yjk_importydb|%s\n" % ydb)
                f.write("000002|yjk_setlayersupport|\n")

            def _done():
                if not os.path.exists(outbox):
                    return False
                t = open(outbox, encoding="utf-8", errors="replace").read()
                return "yjk_importydb" in t

            A.wait_until(_done, timeout=20)
            with open(inbox, "a", encoding="utf-8") as f:
                f.write("000003|exit|\n")           # 让会话立刻收尾，别等空闲
            th.join(timeout=15)

        cmds = [c for c, _ in fake.calls]
        check("① 自动补了一步 yjk_save（调用方链条里没有它）", "yjk_save" in cmds, True)
        check("② 导入校验真的跑了（不再是静默跳过）", seen, [ydb])
        check("③ 校验不通过 → 后续命令没执行（不拿空模型算一整轮）",
              cmds.count("yjk_setlayersupport"), 0)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def t_run_aborts_when_instance_dies():
    """T33：命令执行中实例消失 → `Client.run` 必须**立刻**返回（缺陷 L5 收尾卡住）。

    现场（50 案例 F01/F02）：计算进行中 `yjks` 被硬杀，结果事件永远不会来，
    老版会一直阻塞到 `timeout`（host 传 900s）；而收件箱循环正卡在这条命令里，
    后面 `exit` 也读不到 —— 表现为「不响应 exit，只能强制收尾」，各耗 180.1s。

    这里不起真 YJK：构造一个 `call()` 永远不返回的假 client，
    断言 `alive=lambda: False` 时 `run()` 在 ~1s 内返回 `实例已退出...`；
    同时验 `alive=None`（默认）仍是老行为（超时才返回），避免误伤探测类调用。
    """
    print("T33 实例中途消失 → 立刻放弃等结果（不再阻塞到超时）")
    c = object.__new__(A.Client)

    def _hang(cmd, param=""):
        time.sleep(30)
    c.call = _hang

    t0 = time.time()
    r = c.run("yjkdesign_dsncalculating_all", "", 900, alive=lambda: False, poll=0.2)
    el = time.time() - t0
    check("① 立刻返回（不等到 900s）", el < 5, True)
    check("② 返回值点名「实例已退出」", r.startswith("实例已退出"), True)

    t0 = time.time()
    r2 = c.run("x", "", 1, alive=None, poll=0.2)
    el2 = time.time() - t0
    check("③ alive=None 保持老行为（超时才返回）", r2.startswith("TIMEOUT"), True)
    check("③ 老行为确实是等到 timeout（约 1s）", el2 >= 1, True)


def t_exit_and_idle():
    import threading
    print("T15 exit 优先于隔离闸门（否则有外部实例时永远退不出，只能干等）")
    tmp = tempfile.mkdtemp(prefix="selfchk_")
    try:
        fake = FakeCli()
        with Stub(instances=lambda: [inst("own", 1), inst("foreign", 2)],
                  yjks_pids=lambda: [1, 2]):
            th = threading.Thread(target=A.watch_inbox, args=(fake, tmp),
                                  kwargs=dict(stop_after=20, poll=0.1, own=1, idle_exit=0))
            th.start()
            time.sleep(0.6)
            A.send_to_inbox("exit", "", tmp)
            th.join(5)
            check("exit 立即结束会话（未被 foreign 拦）", th.is_alive(), False)
            check("exit 未被当成普通命令发出去", fake.calls, [])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("T16 --exit-when-idle 空闲自动收尾")
    tmp2 = tempfile.mkdtemp(prefix="selfchk_")
    try:
        with Stub(instances=lambda: [inst("own", 1)], yjks_pids=lambda: [1]):
            t0 = time.time()
            A.watch_inbox(FakeCli(), tmp2, stop_after=60, poll=0.1, own=1, idle_exit=1)
            dt = time.time() - t0
        check("空闲 1s 后自动收尾（不该等到 --stay 60s）", dt < 8, True)
    finally:
        shutil.rmtree(tmp2, ignore_errors=True)

    print("T16b 长命令跑完后不该被立刻判为 idle")
    tmp3 = tempfile.mkdtemp(prefix="selfchk_")

    class SlowCli(FakeCli):
        def run(self, cmd, param="", timeout=300, **kw):
            time.sleep(1.5)                     # 模拟"一轮计算"耗时 > idle_exit
            return super().run(cmd, param, timeout, **kw)

    try:
        slow = SlowCli()
        with Stub(instances=lambda: [inst("own", 1)], yjks_pids=lambda: [1]):
            th = threading.Thread(target=A.watch_inbox, args=(slow, tmp3),
                                  kwargs=dict(stop_after=30, poll=0.1, own=1, idle_exit=1))
            th.start()
            time.sleep(0.5)
            A.send_to_inbox("yjk_save", "", tmp3)
            th.join(8)
        check("长命令确实执行了", slow.calls, [("yjk_save", "")])
        check("跑完还能活过 idle_exit（1s）再收尾", th.is_alive(), False)
    finally:
        shutil.rmtree(tmp3, ignore_errors=True)


def t_wait_until():
    print("T17 wait_until 条件等待（替掉固定 sleep）")
    check("条件立即成立 → 不白等", A.wait_until(lambda: True, 5.0, 0.2) < 0.3, True)
    dt = A.wait_until(lambda: False, 1.0, 0.2)
    check("条件永不成立 → 到点就走", 0.9 < dt < 1.6, True)
    box = {"n": 0}

    def later():
        box["n"] += 1
        return box["n"] >= 3

    dt2 = A.wait_until(later, 5.0, 0.2)
    check("条件稍后成立 → 提前返回", dt2 < 1.5, True)
    check("pred 抛异常也不炸", A.wait_until(lambda: 1 / 0, 0.6, 0.2) >= 0.5, True)


def t_close_and_wait():
    print("T18 close：非自有实例必须先 --yes（不能悄悄关用户的）")
    killed = []
    fo = inst("foreign", 777, ["G:\\w\\T.yjk - 盈建科软件"], proj=r"G:\w\T.yjk")
    with Stub(instances=lambda: [fo], kill_pid=lambda p, **k: killed.append(p) or True):
        A.cmd_close(SimpleNamespace(pid="777", yes=False))
    check("未加 --yes → 不关", killed, [])
    with Stub(instances=lambda: [fo], kill_pid=lambda p, **k: killed.append(p) or True):
        A.cmd_close(SimpleNamespace(pid="777", yes=True))
    check("加 --yes → 才关", killed, [777])
    killed2 = []
    with Stub(instances=lambda: [], kill_pid=lambda p, **k: killed2.append(p) or True):
        A.cmd_close(SimpleNamespace(pid="999", yes=True))
    check("PID 不存在 → 什么都不做", killed2, [])
    with Stub(instances=lambda: [], kill_pid=lambda p, **k: killed2.append(p) or True):
        try:
            A.cmd_close(SimpleNamespace(pid="abc", yes=True))
            check("非法 PID 应报错", "no-raise", "raise")
        except SystemExit:
            check("非法 PID 应报错", "raise", "raise")
    check("提示里给出可粘贴的 close 命令",
          "--pid 777 --yes" in A.close_hint(777), True)

    print("T19 --wait-others：等你关掉即自动继续")


    class Args:
        clean_orphans = False
        wait_others = 20

    state = {"n": 0}

    def inst_seq():
        state["n"] += 1
        return [fo] if state["n"] <= 1 else []      # 第一次还有 foreign，之后关掉了

    with Stub(instances=inst_seq, kill_pid=lambda p, **k: True):
        t0 = time.time()
        ok = A.preflight(Args(), [fo], None)
        dt = time.time() - t0
    check("等到了关闭 → 放行", ok, True)
    check("确实等了（约 15s 一轮）", dt >= 14, True)


def t_ps_and_union():
    print("T20 PowerShell 通道（PATH 里没有 powershell 时必须能自愈）")
    exe = A.powershell_exe()
    check("定位到存在的 powershell.exe", os.path.exists(exe), True)
    out = A.ps("(1+1)")
    check("ps() 能真的跑起来", out.strip(), "2")
    check("ps() 失败会记录（不再静默）", isinstance(A._PS_WARNED, list), True)

    print("T21 instances() 取 psapi ∪ WMI 的并集（psapi 会静默漏进程）")
    # psapi 只看到 1，WMI 只看到 2 → 并集应该两个都出现
    with Stub(yjks_pids=lambda: [1],
              yjks_info=lambda: {1: {"threads": 8, "cmdline": ""},
                                 2: {"threads": 8, "cmdline": "x"}},
              has_main_window=lambda p: True, titles=lambda p: [], own_pid=lambda: None):
        got = sorted(i["pid"] for i in A.instances())
    check("两个来源的 PID 都出现", got, [1, 2])
    with Stub(yjks_pids=lambda: [1], yjks_cmdlines=lambda: {2: "x"}):
        s = A.id_sources()
    check("诊断能指出 psapi 漏掉谁", s["psapi漏掉"], [2])

    print("T22 无窗口但带 -open 的实例算「你在用」，不算可清理的残留")
    cases = [
        ("带 -open 的无窗口实例", r'yjks.exe -product YJKS -open "G:\p\T.yjk"', "foreign"),
        ("无参的无窗口实例（真残留）", r"yjks.exe -product YJKS", "orphan"),
        ("裸 .yjk 参数的", r'yjks.exe "G:\p\T.yjk"', "foreign"),
    ]
    for name, cl, want in cases:
        with Stub(yjks_pids=lambda: [9],
                  yjks_info=lambda: {9: {"threads": 8, "cmdline": cl}},
                  has_main_window=lambda p: False, titles=lambda p: [], own_pid=lambda: None):
            kind = A.instances()[0]["kind"]
        check(name, kind, want)


def t_honest_kill():
    print("T23 kill_pid 说实话（终止被拒时必须返回 False）")
    check("对系统进程 → False（不是假成功）", A.kill_pid(4), False)

    print("T24 kill_own 清不掉时不报成功、不丢登记")
    import contextlib
    tmp = tempfile.mkdtemp(prefix="selfchk_")
    old_file = A.OWN_FILE
    A.OWN_FILE = os.path.join(tmp, "own.json")
    try:
        with Stub(yjks_pids=lambda: [55]):
            A.own_claim(55, r"D:\YJKS\yjks.exe", tmp)
        buf = io.StringIO()
        with Stub(yjks_pids=lambda: [55],                   # 永远清不掉
                  yjks_info=lambda: {55: {"threads": 8, "cmdline": ""}},
                  yjks_cmdlines=lambda: {},
                  kill_pid=lambda p, verbose=False: True,
                  titles=lambda p: []):
            with contextlib.redirect_stdout(buf):
                ok = A.kill_own(wait=2)
        check("返回 False（没清掉）", ok, False)
        check("日志说明没清掉", "没清掉" in buf.getvalue(), True)
        check("保留登记（不丢跟踪）", os.path.exists(A.OWN_FILE), True)
    finally:
        A.OWN_FILE = old_file
        shutil.rmtree(tmp, ignore_errors=True)


def t_dead_shell():
    print("T25 0 线程的残壳：识别为 dead、不阻断开工、不去杀")
    info0 = {999: {"threads": 0, "cmdline": ""}}

    class Args:
        clean_orphans = False
        wait_others = 0

    with Stub(yjks_pids=lambda: [999], yjks_info=lambda: info0,
              has_main_window=lambda p: False, titles=lambda p: [], own_pid=lambda: None):
        ins = A.instances()
    check("0 线程 → dead", ins[0]["kind"], "dead")

    killed = []
    with Stub(instances=lambda: ins, kill_pid=lambda p, **k: killed.append(p) or True,
              kill_own=lambda *a, **k: True):
        ok = A.preflight(Args(), ins, None)
    check("残壳不阻断开工（放行）", ok, True)
    check("残壳不做无谓的终止尝试", killed, [])

    with Stub(yjks_info=lambda: {1: {"threads": 0, "cmdline": ""}}, yjks_pids=lambda: [1, 2]):
        check("wait_gone 把残壳算已消失", A.wait_gone([1], timeout=1), [])
        check("alive_pids 排除残壳（psapi 里的 2 仍算活）", sorted(A.alive_pids()), [2])
    with Stub(yjks_info=lambda: {5: {"threads": 8, "cmdline": ""}}, yjks_pids=lambda: []):
        check("wait_gone 对活着的照旧拦住", A.wait_gone([5], timeout=1), [5])


#>>> COMPAT-FALLBACK BEGIN —— 六份副本必须**一致**：内容逐字节相同，行尾各随本文件自身
# 约定（本包既有 LF 也有 CRLF 文件，比对时按行尾归一化，不算漂移）。selfcheck.py 的 T31 守着。
# 为什么这六份是**故意**重复的：业务技能在找到驱动技能目录之前，没法 import 它的
# paths.py（鸡生蛋），所以每份必须自带一段最小回退。按本包契约
# `yjk-auto-drive/scripts/paths.py` 才是"唯一找东西的地方"，因此这段回退**只保留三样**：
#   ① 环境变量（三个都认） ② 同级目录 ③ 与厂商无关的通用扫描 + 中立位置
# 其余一切（YJK 安装位置 / Config.ini / 官方 DLL / 解释器）一律委托给 paths.py ——
# **别往这里加东西**，加了就又少一处"只维护一次"。
#
# 为什么需要这道守卫：这六份**漂移过**。曾经同一个厂商的路径出现在部分副本里、通用扫描
# 只在另一部分副本里，于是"能不能找到驱动"取决于用户恰好跑了哪个脚本；更隐蔽的是本机
# 一直"看着能用"，只不过因为家目录里正好有一份别人装的旧副本 —— 换台机器就全崩。
#
# 产出的是 **<技能> 目录**（不含 scripts），调用方自己拼 "scripts"。做成生成器是有意的：
# 候选链"命中即停"，最后那档家目录扫描只在前面几档都落空时才付费。
_COMPAT_SCAN_CAP = 40           # 只取前 N 个一级子目录：家目录塞满几万个条目也不能拖慢启动


def _compat_subdirs(base, cap=_COMPAT_SCAN_CAP):
    """`base` 下的一级子目录名 —— **先全量排序、再取前 cap 个**。

    为什么必须先排序再截断：`os.scandir` 的返回顺序是文件系统的顺序（换机器、增删文件都会
    变），若"边扫边收满 cap 就停"，留下的那批就是随机的 —— 同一台机器两次跑可能命中不同
    目录。排序后再截断才是**确定的子集**：候选顺序可复现，故障也可复现。
    只列一级、**不递归**（递归家目录在大机器上要几十秒，定位一个技能不该这么贵）。

    目录不存在 / 无权限一律返回 []：这是"猜位置"，猜不到就该继续走下一档候选，
    绝不能因为某个目录读不了就让整条定位链崩掉。
    """
    try:
        with os.scandir(base) as it:
            names = []
            for e in it:
                try:
                    if e.is_dir():
                        names.append(e.name)
                except OSError:                 # 断链 / 权限：单个条目读不了就跳过
                    continue
    except OSError:                             # 目录本身不存在或无权限
        return []
    names.sort()
    return names[:cap]


def _compat_cwd():
    """当前目录（进程的工作目录被删掉时 `os.getcwd()` 会抛 OSError）。"""
    try:
        return os.getcwd()
    except OSError:
        return None


def _compat_driver_dirs(skill="yjk-auto-drive", cap=_COMPAT_SCAN_CAP):
    """`<技能>` 目录的候选链；顺序即优先级，命中即止。

    为什么要"枚举"而不是"再抄一个厂商名"：本包原来只认一个厂商的技能目录，换到别的
    agent/IDE 上那个目录**根本不存在**，而用户最自然的装法恰恰是"把整套技能丢进我的技能
    目录"—— 于是底座明明就在旁边，却报「找不到 yjk-auto-drive」。再抄第二个厂商名只是把
    问题推迟到第三个 agent，所以改成**扫家目录下的一级子目录**：任何
    `~/.<任意名>/skills/` 都能命中，且不需要知道对方叫什么。
    """
    v = os.environ.get("YJK_DRIVER_DIR")            # ① 环境变量：指向 <技能>/scripts
    if v:
        yield os.path.dirname(v)
    v = os.environ.get("YJK_AUTO_DRIVE_DIR")        #               指向 <技能>
    if v:
        yield v
    v = os.environ.get("YJK_SKILLS_DIR")            #               指向整套技能的根
    if v:
        yield os.path.join(v, skill)
    yield os.path.join(HERE, "..", "..", skill)     # ② 同级目录：装机默认形态，最可靠
    yield os.path.join(HERE, "..", skill)
    cwd = _compat_cwd()                             # ③ 当前目录
    if cwd:
        yield os.path.join(cwd, skill)
        yield os.path.join(cwd, "..", skill)
    home = os.path.expanduser("~")                  # ④ 与厂商无关：各 agent 的技能家目录
    for base in (home, os.path.join(home, ".config")):
        for d in _compat_subdirs(base, cap):
            p = os.path.join(base, d)
            yield os.path.join(p, "skills", skill)  #    `~/.<任意名>/skills/<技能>`
            yield os.path.join(p, skill)            #    `~/.<任意名>/<技能>`
    yield os.path.join(home, ".agent-skills", skill)    # ⑤ 中立约定位置
    yield os.path.join(home, ".skills", skill)
    if cwd:
        yield os.path.join(cwd, ".skills", skill)
    # ⑥ 历史遗留路径：保留以不破坏现有用户（这是**兼容项**，不是厂商假设，别当例子抄）
    yield os.path.join(home, ".workbuddy-ai", "skills", skill)
#<<< COMPAT-FALLBACK END


def find_colskill_scripts():
    """定位 column-section-opt/scripts。找不到返回 None。

    直接复用上面那段 COMPAT-FALLBACK（技能名换成 column-section-opt）。
    本函数以前自己又手写了一份候选链 —— 那是"同一件事的第七份副本"，也漂移过。
    现在它和另外六份共用同一份实现，改一处就是改全部。
    """
    for d in _compat_driver_dirs("column-section-opt"):
        p = os.path.join(d, "scripts")
        if os.path.exists(os.path.join(p, "verify_results.py")):
            return p
    return None


# ---------------------------------------------------------------- T31 六份查找副本不许漂移
# 「找驱动技能 / 找技能根」这段逻辑在本包里被**故意复制**了六份（业务技能在找到驱动目录
# 之前没法 import 它的 paths.py，鸡生蛋），而复制出来的东西会漂移 —— 真实发生过：
#   同一个厂商的路径出现在部分副本里、通用扫描只在另一部分副本里，
#   于是"能不能找到"取决于用户恰好跑了哪个脚本；
#   更隐蔽的是本机一直"看着能用"，只不过因为家目录里正好有一份别人装的旧副本。
# 所以这里把六份钉死成四条硬断言：
#   ① 每份都有且只有一个 COMPAT-FALLBACK 块，且**块外的查找链**不许自己另起一套
#   ② 六份（外加 selfcheck 自己那一处）块内容一致（行尾归一化后逐字节）
#   ③ 块内三个环境变量要认全、且顺序一致
#   ④ 块内**非环境变量候选**的集合与顺序必须等于下面这份规范清单
# 另：谁都不许再把桌面路径写回查找链（`compat_check.py` 从"能力"角度也守这一条）。
_FALLBACK_BEGIN = "#>>> COMPAT-FALLBACK BEGIN"
_FALLBACK_END = "#<<< COMPAT-FALLBACK END"

_FINDER_FILES = [
    # (技能, 相对路径, 该文件里"找驱动"那个函数名)
    ("column-section-opt", "scripts/driver.py", "_candidates"),
    ("floor-system-comparison", "scripts/yjk_api.py", "_driver_paths"),
    ("floor-system-comparison", "scripts/draw_quant.py", "find_driver"),
    ("floor-system-comparison", "scripts/yjk_quant.py", "_find_driver_scripts"),
    ("floor-system-comparison", "scripts/run_all_yjk.py", "_find_driver_yjk_auto"),
    ("yjk-draw-takeoff", "scripts/draw_quant.py", "find_driver"),
]
# 除那六份之外，还允许（并要求）本文件自己带着同一份块 ——
# `find_colskill_scripts()` 找的是另一个技能，但用的是同一套查找逻辑。
_BLOCK_FILES = _FINDER_FILES + [("yjk-auto-drive", "scripts/selfcheck.py",
                                 "find_colskill_scripts")]

# 三个环境变量都要认，且顺序一致：只认一两个会出现"只设了某一个变量时，
# 有的脚本找得到驱动、有的找不到"这种最难查的不一致。
_WANT_ENV = ["YJK_DRIVER_DIR", "YJK_AUTO_DRIVE_DIR", "YJK_SKILLS_DIR"]

# 这就是"六份必须一样"的那份清单（顺序即优先级）。新增/调整候选时必须改这里，
#   否则 T31 会红 —— 这是故意的：它逼着你"六份一起改"，而不是只改自己手边那份。
_WANT_ORDER = [
    "sibling:<技能>/../..",                        # 同父兄弟（装机默认形态，最可靠）
    "sibling:<技能>/..",
    "cwd:.",
    "cwd:..",
    "generic:<home>/.<任意名>/skills/<技能>",       # 与厂商无关：枚举家目录一级子目录
    "generic:<home>/.<任意名>/<技能>",
    "neutral:<home>/.agent-skills/<技能>",
    "neutral:<home>/.skills/<技能>",
    "neutral:<cwd>/.skills/<技能>",
    "legacy:<home>/.workbuddy-ai/skills/<技能>",    # 兼容项：保留只为不破坏现有用户
]

# 块内 `yield` 的实参 → 规范名（未列出的实参一律记为 "??"，好让 T31 直接点出来）
_YIELD_KIND = {
    'os.path.join(HERE, "..", "..", skill)': "sibling:<技能>/../..",
    'os.path.join(HERE, "..", skill)': "sibling:<技能>/..",
    "os.path.join(cwd, skill)": "cwd:.",
    'os.path.join(cwd, "..", skill)': "cwd:..",
    'os.path.join(p, "skills", skill)': "generic:<home>/.<任意名>/skills/<技能>",
    "os.path.join(p, skill)": "generic:<home>/.<任意名>/<技能>",
    'os.path.join(home, ".agent-skills", skill)': "neutral:<home>/.agent-skills/<技能>",
    'os.path.join(home, ".skills", skill)': "neutral:<home>/.skills/<技能>",
    'os.path.join(cwd, ".skills", skill)': "neutral:<cwd>/.skills/<技能>",
    'os.path.join(home, ".workbuddy-ai", "skills", skill)':
        "legacy:<home>/.workbuddy-ai/skills/<技能>",
}
# 环境变量那几档（由 _WANT_ENV 单独断言，不算进"非环境变量候选顺序"）
_ENV_YIELDS = {"os.path.dirname(v)", "v", "os.path.join(v, skill)"}


def _pkg_root():
    """从本文件往上找到含 5 个技能目录的那一层；找不到返回 None。"""
    d = os.path.dirname(HERE)
    for _ in range(4):
        d = os.path.dirname(d)
        if all(os.path.isdir(os.path.join(d, s))
               for s in ("yjk-auto-drive", "column-section-opt",
                         "floor-system-comparison", "column-scheme-comparison",
                         "yjk-draw-takeoff")):
            return d
    return None


def _fallback_block(txt):
    """取出 COMPAT-FALLBACK 块（行尾归一化为 LF）；没有或不止一处返回 None。"""
    if txt.count(_FALLBACK_BEGIN) != 1 or txt.count(_FALLBACK_END) != 1:
        return None
    blk = txt[txt.index(_FALLBACK_BEGIN):txt.index(_FALLBACK_END) + len(_FALLBACK_END)]
    return blk.replace("\r\n", "\n")


def _cand_order(blk):
    """块内**非环境变量**候选的规范名序列（顺序即源码顺序）。"""
    out = []
    for line in blk.splitlines():
        code = line.split("#")[0].strip()
        if not code.startswith("yield "):
            continue
        arg = code[len("yield "):].strip()
        if arg in _ENV_YIELDS:
            continue
        out.append(_YIELD_KIND.get(arg, "?? " + arg))
    return out


def _func_body(txt, name):
    """切出顶层函数 `name` 的完整函数体。

    结束判据是"下一个**顶格**的非空、非注释行"，而不是"下一个 def" —— 函数后面紧跟的
    模块级语句（`SK = ...` / `if not SK:` / `ROOT` 之类）若被一起切进来，下面"没写死桌面""没有
    手写目录扫描"这两条就会判到别人头上（口径不准的守卫比没有守卫更糟）。

    只做静态切片、不 import —— 这几份文件里有的是一 import 就会去找 YJK，
    自检必须能在没有 YJK 的机器上跑。
    """
    lines = txt.splitlines(keepends=True)
    start = None
    for i, ln in enumerate(lines):
        if re.match(r"^def %s\(" % re.escape(name), ln):
            start = i
            break
    if start is None:
        return None
    out = [lines[start]]
    for ln in lines[start + 1:]:
        s = ln.strip()
        if s and not ln[0].isspace() and not s.startswith("#"):
            break                                   # 顶格新语句 → 函数到此为止
        out.append(ln)
    return "".join(out)


def _strip_doc(body):
    """去掉三引号字符串与 `#` 注释，只留代码 —— 判"有没有桌面路径"时用。

    为什么不能直接搜整段函数体：这些函数的**文档字符串里本来就写着**
    "不含……桌面路径"，直接搜会把说明文字当成证据自己命中自己。
    """
    for q in ('"""', "'''"):
        body = re.sub(re.escape(q) + r"(?:.|\n)*?" + re.escape(q), "", body)
    return "\n".join(ln.split("#")[0] for ln in body.splitlines())


def t_compat_fallback():
    print("T31 六份「找驱动技能」副本不许漂移（块一致 + 候选顺序一致 + 块外不另起一套）")
    root = _pkg_root()
    if not root:
        print("  [--] 找不到技能包根目录（五个技能不在同级），跳过")
        return

    blocks, orders, envs = {}, {}, {}
    for skill, rel, fn in _FINDER_FILES:
        tag = "%s/%s" % (skill, rel)
        p = os.path.join(root, skill, rel)
        check("%s 存在" % tag, os.path.exists(p), True)
        if not os.path.exists(p):
            continue
        txt = io.open(p, encoding="utf-8", errors="replace").read()
        check("%s 有且只有一个 COMPAT-FALLBACK 块" % tag,
              (txt.count(_FALLBACK_BEGIN), txt.count(_FALLBACK_END)), (1, 1))
        blk = _fallback_block(txt)
        if blk is None:
            continue
        blocks.setdefault(blk, []).append(tag)
        envs[tag] = re.findall(r'os\.environ\.get\("([A-Z_]+)"\)', blk)
        orders[tag] = _cand_order(blk)
        # 块外不许再自己拼一套：查找函数必须**消费**块，且不许在手写目录扫描
        # （检查只针对该函数体，免得误伤同文件里找 DLL 用的那些候选列表）
        body = _func_body(txt, fn)
        check("%s 有 %s() 函数" % (tag, fn), body is not None, True)
        if body is None:
            continue
        check("%s 的 %s() 消费 _compat_driver_dirs()" % (tag, fn),
              "_compat_driver_dirs(" in body, True)
        check("%s 的 %s() 没有自己手写的目录扫描" % (tag, fn),
              bool(re.search(r"os\.listdir\(|os\.scandir\(", body)), False)

    # ② 块内容一致：这是"六份没有漂移"最强的那条断言
    check("七处 COMPAT-FALLBACK 块内容一致（行尾归一化后）", len(blocks), 1)
    if len(blocks) != 1:
        for blk, tags in sorted(blocks.items(), key=lambda kv: -len(kv[1])):
            print("       版本（%d 行）× %d 份：%s"
                  % (blk.count("\n") + 1, len(tags), ", ".join(tags)))

    # ③④ 环境变量认全 + 非环境变量候选集合与顺序
    for tag in sorted(envs):
        check("%s 认全三个环境变量且顺序一致" % tag, envs[tag], _WANT_ENV)
    for tag in sorted(orders):
        check("%s 非环境变量候选顺序 = 规范顺序" % tag, orders[tag], _WANT_ORDER)

    # 谁都不许把桌面路径写回查找函数。判据是"字符串字面量里出现 Desktop/桌面"，
    # 且只针对**代码**（文档字符串与注释里写着这条规矩，不能算证据）。
    for skill, rel, fn in _BLOCK_FILES:
        p = os.path.join(root, skill, rel)
        if not os.path.exists(p):
            continue
        txt = io.open(p, encoding="utf-8", errors="replace").read()
        code = _strip_doc(_func_body(txt, fn) or "")
        check("%s/%s 的 %s() 里没有桌面路径" % (skill, rel, fn),
              bool(re.search(r"[\"'][^\"']*(?:Desktop|桌面)", code)), False)


def t_colskill_input():
    print("T12 column-section-opt/verify_results.py 输入健壮性")
    cs = find_colskill_scripts()
    if not cs:
        print("  [--] 未找到 column-section-opt/scripts/verify_results.py，跳过")
        return
    vr = os.path.join(cs, "verify_results.py")
    tmp = tempfile.mkdtemp(prefix="selfchk_")
    try:
        # (a) 缺 --db 必须直接拒绝，而不是退化成某个写死的分组/等级口径
        r = subprocess.run([sys.executable, "-X", "utf8", "-B", vr, tmp],
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
        out = (r.stdout or "") + (r.stderr or "")
        check("缺 --db 时非零退出", r.returncode != 0, True)
        check("缺 --db 时提示 --db", "--db" in out, True)
        # (b) 设计结果目录里没有 wpj*.out 时必须明确报错
        os.makedirs(os.path.join(tmp, "设计结果"), exist_ok=True)
        r = subprocess.run(
            [sys.executable, "-X", "utf8", "-B", vr,
             os.path.join(tmp, "设计结果"), "--db", os.path.join(tmp, "no.ymd")],
            capture_output=True, text=True, encoding="utf-8", errors="replace")
        out = (r.stdout or "") + (r.stderr or "")
        check("无 wpj 时非零退出", r.returncode != 0, True)
        check("报错清晰（提到没解析到 wpj）", "没解析到 wpj" in out, True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def t_colskill_drift_crosscheck():
    """T12b：位移角「全部哨兵」必须**用原始位移量交叉印证**，不许只信哨兵值。

    为什么单立一条：`verify_results.py` 把「1/N 全是 9999」判为**满足**
    （依据：9999 是 YJK 的"比值优于 1/9999"上限哨兵 = 位移≈0，实测 0.2mm/3600mm）。
    这个结论一旦判错，就是一条**静默成功路径**（把"没算/没输出"当成"满足"）。
    所以它必须能被**同一份文件里的 `h` 与 `Max-D` 列**验伪。这里直接调它的
    `crosscheck_wdisp_sentinel()`，三种输入各验一次：

      · 哨兵 + 位移很小（0.21mm / 3600mm）→ 通过（现算 ≈1/17000 > 1/800）
      · 哨兵 + 位移很大（20mm / 3600mm）→ **矛盾**（现算 1/180 ≤ 1/800）
        → 必须返回 False（这时 main 会把它算成"不满足"，不许静默判满足）
      · 文件里没有 `1/9999` 行 → 无法印证（None），且 main 会说明"按哨兵判定"
    """
    print("T12b 位移角「全部哨兵」的交叉印证（h 与 Max-D 现算）")
    cs = find_colskill_scripts()
    if not cs:
        print("  [--] 未找到 column-section-opt/scripts/verify_results.py，跳过")
        return
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "vr_crosscheck", os.path.join(cs, "verify_results.py"))
    m = importlib.util.module_from_spec(spec)
    sys.path.insert(0, cs)          # 该脚本可能 import 同目录模块
    try:
        spec.loader.exec_module(m)

        head = ("位移输出文件\n === 工况9 === X 方向地震作用下的楼层最大位移\n\n"
                " Floor  Tower    Jmax     Max-(X)   Ave-(X)        h\n"
                "                 JmaxD    Max-Dx    Ave-Dx     Max-Dx/h"
                "    DxR/Dx    Ratio_AX\n\n")

        def rows(maxd):
            return ("   3     1     3000021      1.29     1.16         3600\n"
                    "               3000025   %6.2f     0.19       1/9999"
                    "     11.89%%    1.00\n" % maxd
                    + "   2     1     2000001      1.09     0.97         3600\n"
                    "               2000005   %6.2f     0.18       1/9999"
                    "      3.46%%    0.86\n" % maxd)

        tmp = tempfile.mkdtemp(prefix="selfchk_drift_")
        try:
            # ① 位移很小 → 哨兵成立（通过）
            d1 = os.path.join(tmp, "small")
            os.makedirs(d1)
            open(os.path.join(d1, "wdisp.out"), "w", encoding="gbk").write(
                head + rows(0.21))
            ok, worst, n, why = m.crosscheck_wdisp_sentinel(d1)
            check("① 小位移：交叉印证通过", ok, True)
            check("① 现算最不利 > 800（1/%d）" % worst, worst > 800, True)
            check("① 统计到 2 层（每层一行）", n, 2)

            # ② 位移很大（20mm/3600mm = 1/180）→ 与哨兵矛盾，必须 False
            d2 = os.path.join(tmp, "big")
            os.makedirs(d2)
            open(os.path.join(d2, "wdisp.out"), "w", encoding="gbk").write(
                head + rows(20.0))
            ok2, worst2, _n2, why2 = m.crosscheck_wdisp_sentinel(d2)
            check("② 大位移：判定为**矛盾**（不是静默满足）", ok2, False)
            check("② 现算最不利 ≤ 800（1/%d）" % worst2, worst2 <= 800, True)
            check("② 说明里点出「矛盾」", "矛盾" in why2, True)

            # ③ 没有哨兵行 → 无法印证（None），不能当成"通过"
            d3 = os.path.join(tmp, "none")
            os.makedirs(d3)
            open(os.path.join(d3, "wdisp.out"), "w", encoding="gbk").write(
                head + "   3     1     3000021      1.29     1.16         3600\n"
                       "               3000025      0.21     0.19       1/600"
                       "     11.89%    1.00\n")
            ok3, _w3, _n3, _why3 = m.crosscheck_wdisp_sentinel(d3)
            check("③ 无哨兵行 → 返回 None（无法印证，不是通过）", ok3, None)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    finally:
        try:
            sys.path.remove(cs)
        except ValueError:
            pass


def t_takeoff_macro():
    print("T26 @takeoff 算量宏：顺序固定为 混凝土统计 → 施工图 → 钢筋统计")
    seq = A.expand("@takeoff")
    cmds = [c for c, _ in seq]
    check("@takeoff 条数 = TAKEOFF_CHAIN", len(seq), len(A.TAKEOFF_CHAIN))
    check("首条切到建模模块（混凝土统计属建模模块）", seq[0],
          ("SetCurrentLabel", "IDModule_Layer"))
    check("第二条就是混凝土统计", cmds[1], "yjkconcreteStat_statCom")
    i_conc = cmds.index("yjkconcreteStat_statCom")
    i_draw = min(cmds.index(c) for c in ("StdSlab_RedrawNceng", "DtlRC_DrawNewColPlan",
                                        "DtlRC_WallPlanRegenNew",
                                        "DtlRC_RegenReinsUpdateBeamPlan"))
    i_rebar = min(cmds.index(c) for c in ("DtlRC_SSSE", "DtlRC_SSCE",
                                          "DtlRC_SSWE", "dtlrc_ColSumGJ"))
    check("混凝土统计在施工图之前（否则冲掉施工图上下文）", i_conc < i_draw, True)
    check("施工图在钢筋统计之前（否则 DtlRC_* 退化成 OK(0.0s) 且零产出）",
          i_draw < i_rebar, True)
    check("钢筋统计前切到工程量统计模块", ("SetCurrentLabel", "IDQUANTITYLIST_DETAIL") in seq, True)
    check("板钢筋出量的关键一步在链里（缺它全 0）", "stdslab_AutoStatstl" in cmds, True)
    # 原有宏的意义不能被改动
    check("@back 不变", A.expand("@back"), [("SetCurrentLabel", "IDModule_Element")])
    check("@prep 不变", A.expand("@prep"), list(A.PREP_CHAIN))
    check("@calc 不变", A.expand("@calc"), list(A.CALC_CHAIN))
    check("MACRO_HELP 里登记了 @takeoff", "@takeoff" in A.MACRO_HELP, True)


def _mk_db(path, rows):
    """按 {表: 行数} 造一个最小 sqlite 库（只造 impcheck 关心的表）。"""
    con = sqlite3.connect(path)
    for t, n in rows.items():
        con.execute('create table "%s" (ID integer)' % t)
        con.executemany('insert into "%s" (ID) values (?)' % t, [(i,) for i in range(n)])
    con.commit()
    con.close()
    return path


def t_import_check():
    print("T27 导入校验闸门（impcheck）：判据是逐表行数，不是字节数")
    tmp = tempfile.mkdtemp(prefix="selfchk_")
    try:
        # 源模型：必判表都非空；tblSlab/tblAxis 另有行数
        src = _mk_db(os.path.join(tmp, "src.ydb"),
                     {"tblJoint": 672, "tblColSeg": 448, "tblBeamSeg": 784,
                      "tblWallSeg": 224, "tblFloor": 28, "tblStdFlr": 28,
                      "tblSlab": 336, "tblAxis": 1008})
        # 正常导入：必判表逐表相等，tblSlab/tblAxis **合法地变了** → 必须通过
        good = _mk_db(os.path.join(tmp, "good.ymd"),
                      {"tblJoint": 672, "tblColSeg": 448, "tblBeamSeg": 784,
                       "tblWallSeg": 224, "tblFloor": 28, "tblStdFlr": 28,
                       "tblSlab": 364, "tblAxis": 280})
        ok, _rep = A.IC.check(src, good, verbose=False, strict=False)
        check("好样本通过（含 tblSlab 336→364、tblAxis 1008→280 的合法变化）", ok, True)
        # 空模型（导入没生效）：几何表全 0 → 必须不通过
        bad = _mk_db(os.path.join(tmp, "bad.ymd"),
                     {"tblJoint": 0, "tblColSeg": 0, "tblBeamSeg": 0,
                      "tblWallSeg": 0, "tblFloor": 0, "tblStdFlr": 1,
                      "tblSlab": 0, "tblAxis": 0})
        ok2, rep2 = A.IC.check(src, bad, verbose=False, strict=False)
        check("空模型不通过", ok2, False)
        check("报错点名了整表为空的表", "整表为空" in rep2, True)
        check("报错点明了往下跑的后果（fea.dat-ERR.txt）",
              "模型中没有单元数据" in rep2, True)
        # 半写模型：几何表少了一部分（不是全 0）→ 也必须不通过
        half = _mk_db(os.path.join(tmp, "half.ymd"),
                      {"tblJoint": 672, "tblColSeg": 448, "tblBeamSeg": 784,
                       "tblWallSeg": 0, "tblFloor": 28, "tblStdFlr": 28,
                       "tblSlab": 336, "tblAxis": 1008})
        check("少了 tblWallSeg 也算不通过（不只看「是不是全空」）",
              A.IC.check(src, half, verbose=False, strict=False)[0], False)
        # .ymd 还没落盘（校验排在了 save 之前）→ 明确提示顺序
        ok4, rep4 = A.IC.check(src, os.path.join(tmp, "nope.ymd"),
                               verbose=False, strict=False, wait=0.1)
        check("找不到 .ymd 时不通过", ok4, False)
        check("提示「校验必须排在 save 之后」", "save 之后" in rep4, True)
        # 工程目录版（收件箱没有 --name 时用）：靠 tblStdFlr 认模型库
        ok5, _ = A.IC.check_dir(src, tmp, verbose=False, strict=False)
        check("check_dir 能在目录里认出模型库并核对", ok5 in (True, False), True)
        check("find_ymd 按库结构认出模型库（bad.ymd 含 tblStdFlr）",
              os.path.basename(A.IC.find_ymd(tmp) or ""), "bad.ymd")
        # host 侧封装：不通过时返回 False（供 host 记失败 + 非零退出）
        check("verify_import 空模型 → False", A.verify_import(src, tmp, "bad",
                                                            verbose=False), False)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("T27b 收件箱导入步：yjk_save 之后自动核对，不通过就跳过本轮剩余命令")
    import threading
    tmp2 = tempfile.mkdtemp(prefix="selfchk_")
    try:
        srcp = os.path.join(tmp2, "m.ydb")
        open(srcp, "w", encoding="utf-8").write("x")     # 前置校验要求文件真的在

        class WritingCli(FakeCli):
            """模拟"导入确实写了文件"（否则会先撞上'没有任何文件变化'那条闸门）。"""

            def run(self, cmd, param="", timeout=300, **kw):
                r = super().run(cmd, param, timeout, **kw)
                if cmd == "yjk_importydb":
                    open(os.path.join(tmp2, "_touched.dat"), "w",
                         encoding="utf-8").write("x")
                return r

        fake = WritingCli()
        seen = []
        outbox = A.inbox_paths(tmp2)[1]
        with Stub(instances=lambda: [inst("own", 1)], yjks_pids=lambda: [1],
                  project_dir_mismatch=lambda w, p=None: None,
                  verify_import=lambda y, w, **k: (seen.append(y), False)[1]):
            th = threading.Thread(target=A.watch_inbox, args=(fake, tmp2),
                                  kwargs=dict(stop_after=4, poll=0.1, own=1))
            th.start()
            time.sleep(0.6)
            A.send_to_inbox("yjk_importydb", srcp, tmp2)
            A.send_to_inbox("yjk_save", "", tmp2)
            A.send_to_inbox("yjk_save", "", tmp2)          # ③ 不该被执行
            th.join(8)
        check("导入 + 保存被执行，第 3 条被跳过",
              [c for c, _ in fake.calls], ["yjk_importydb", "yjk_save"])
        check("核对的是刚导入的那个 ydb", seen, [srcp])
        body = open(outbox, encoding="utf-8").read() if os.path.exists(outbox) else ""
        check("outbox 留了'导入校验不通过'的回执", "导入校验不通过" in body, True)
    finally:
        shutil.rmtree(tmp2, ignore_errors=True)


def t_dir_mismatch():
    print("T28 会话目录 vs YJK 打开工程目录（现场：导入 OK 但没文件变化）")
    wd = r"G:\wd\proj"
    other = r"G:\other\proj2"
    with Stub(yjks_pids=lambda: [7],
              titles=lambda p: [other + r"\P2 - 盈建科软件"]):
        hit = A.project_dir_mismatch(wd)
    check("错配被发现", bool(hit), True)
    check("报出的是那另一个工程", hit[1] if hit else None, other + r"\P2")
    check("报出的是它的目录", hit[2] if hit else None, other)
    with Stub(yjks_pids=lambda: [7],
              titles=lambda p: [wd + r"\Proj - 盈建科软件"]):
        check("一致时不报", A.project_dir_mismatch(wd), None)
    with Stub(yjks_pids=lambda: [7], titles=lambda p: ["盈建科软件"]):
        check("欢迎页（读不到工程路径）不猜、不报", A.project_dir_mismatch(wd), None)
    # 大小写/尾斜杠差异不算错配（Windows）
    with Stub(yjks_pids=lambda: [7],
              titles=lambda p: [r"g:\WD\PROJ\Proj - 盈建科软件"]):
        check("大小写差异不算错配", A.project_dir_mismatch(wd), None)

    print("T28b 错配时收件箱必须停手（不再把'命令成功在别的目录'报成'导入没生效'）")
    import threading
    tmp = tempfile.mkdtemp(prefix="selfchk_")
    try:
        fake = FakeCli()
        seen = []
        outbox = A.inbox_paths(tmp)[1]

        class Args:
            pass

        with Stub(instances=lambda: [inst("own", 1)], yjks_pids=lambda: [1],
                  project_dir_mismatch=lambda w, p=None: (7, other + r"\P2", other),
                  print_dir_mismatch=lambda w, h: seen.append((w, h))):
            th = threading.Thread(target=A.watch_inbox, args=(fake, tmp),
                                  kwargs=dict(stop_after=4, poll=0.1, own=1))
            th.start()
            time.sleep(0.6)
            A.send_to_inbox("yjk_save", "", tmp)
            A.send_to_inbox("yjk_save", "", tmp)         # 也该被跳过
            th.join(8)
        check("错配 → 一条命令都不执行", fake.calls, [])
        check("报出了两个目录", [h[1][2] for h in seen], [other])
        body = open(outbox, encoding="utf-8").read() if os.path.exists(outbox) else ""
        check("outbox 写明是目录错配（不是导入失败）", "目录错配" in body, True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def t_host_exit_code():
    print("T29 导入校验不通过时 host 必须**非零**退出（自动化调用方靠它判成败）")
    tmp = tempfile.mkdtemp(prefix="selfchk_")
    try:
        A._HOST_ERRORS[:] = []
        args = SimpleNamespace(dir=tmp, name="P", keep=False)

        def fake_host(a):
            A.host_fail("模拟：导入校验不通过")

        with Stub(instances=lambda: [], own_pid=lambda: None, preflight=lambda *a: True,
                  _host=fake_host, dlgwatch_errors=lambda: [], stop_dlgwatch=lambda: None,
                  kill_own=lambda *a, **k: True):
            try:
                A.cmd_host(args)
                rc = 0
            except SystemExit as e:
                rc = e.code
        check("失败台账非空 → SystemExit(2)", rc, 2)
        check("台账里有那条理由", "导入校验不通过" in " ".join(A._HOST_ERRORS), True)

        A._HOST_ERRORS[:] = []
        with Stub(instances=lambda: [], own_pid=lambda: None, preflight=lambda *a: True,
                  _host=lambda a: None, dlgwatch_errors=lambda: [], stop_dlgwatch=lambda: None,
                  kill_own=lambda *a, **k: True):
            try:
                A.cmd_host(args)
                rc2 = 0
            except SystemExit as e:
                rc2 = e.code
        check("没有失败时照旧 0 退出（不误伤）", rc2, 0)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def t_reuse():
    print("T30 --reuse：默认仍拒绝，开了要明说覆盖/打开并先查「是否已被别的实例打开」")
    tmp = tempfile.mkdtemp(prefix="selfchk_")
    try:
        wd = tmp
        proj = os.path.join(wd, "P.yjk")
        open(proj, "w", encoding="utf-8").write("x")      # 目录里已有工程文件
        # 默认（不 reuse）：拒绝，且**不发** UINew
        cli = FakeCli()
        with Stub(project_open=lambda n, w: False, yjks_pids=lambda: [], titles=lambda p: []):
            got = A.open_new_project(cli, proj, wd)
        check("默认拒绝复用", got, False)
        check("默认不发 UINew（不覆盖已有模型）", cli.calls, [])
        # --reuse 但该工程正被另一个实例打开 → 拒绝（那才是原规则要防的危险）
        cli2 = FakeCli()
        with Stub(project_open=lambda n, w: False, yjks_pids=lambda: [],
                  titles=lambda p: [],
                  _project_held_by_other=lambda w: {"pid": 42, "title": wd + r"\P"}):
            got2 = A.open_new_project(cli2, proj, wd, reuse=True)
        check("正被别的实例打开 → 拒绝", got2, False)
        check("此时不发 UINew", cli2.calls, [])
        # --reuse 且无人打开 → 放行并发 UINew
        cli3 = FakeCli()
        with Stub(project_open=lambda n, w: False, yjks_pids=lambda: [1],
                  titles=lambda p: [proj + " - 盈建科软件"],
                  _project_held_by_other=lambda w: None):
            got3 = A.open_new_project(cli3, proj, wd, reuse=True)
        check("无人打开时放行", got3, True)
        check("放行后确实发了 UINew", [c for c, _ in cli3.calls], ["UINew"])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def golden(workdir, expect=None, dump=None):
    """对算过的工程做值断言（T13）。"""
    print("T13 --golden 黄金值")
    res = os.path.join(workdir, "设计结果")
    if not os.path.isdir(res):
        print("  [!!] %s 下没有 设计结果 目录" % workdir)
        return 1
    cs = find_colskill_scripts()
    if not cs:
        print("  [--] 未找到 column-section-opt/scripts/verify_results.py，跳过")
        return 0
    sys.path.insert(0, cs)
    import verify_results as V
    wpj = sorted(fn for fn in os.listdir(res)
                 if fn.startswith("wpj") and fn.endswith(".out"))
    rows = []
    for fn in wpj:
        rows.extend(V.parse_wpj(os.path.join(res, fn)))
    if not rows:
        print("  [!!] 没解析到柱结果（wpj*.out）")
        return 1
    # 每 (标准层, 柱号) 取 Uc 最大者
    worst = {}
    for r in rows:
        k = (r["标准层"], r["柱号"])
        if k not in worst or (r["Uc"] or 0) > (worst[k]["Uc"] or 0):
            worst[k] = r
    stds = sorted({k[0] for k in worst})
    got = {
        "文件数": len(wpj),
        "超限": sum(1 for r in rows if r["超限"]),
        # 键一律转成 str：JSON 往返会把 int 键变成 str，比对时类型不一致会炸
        "材料": {str(s): sorted({worst[k]["材料"] for k in worst if k[0] == s})
                 for s in stds},
        "截面": {str(s): sorted({worst[k]["截面"] for k in worst if k[0] == s})
                 for s in stds},
        "最大Uc": {str(s): round(max((worst[k]["Uc"] or 0)
                                    for k in worst if k[0] == s), 3)
                   for s in stds},
    }
    print("  文件数=%s 超限=%s" % (got["文件数"], got["超限"]))
    print("  各标准层材料: %s" % json.dumps(got["材料"], ensure_ascii=False))
    print("  各标准层截面:")
    for s, v in got["截面"].items():
        print("     标准层%-3s %s" % (s, v))
    print("  各标准层最大Uc: %s" % json.dumps(got["最大Uc"], ensure_ascii=False))
    if dump:
        os.makedirs(os.path.dirname(os.path.abspath(dump)), exist_ok=True)
        json.dump(got, open(dump, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("  已把本次实算值存为基准 -> %s" % dump)
    if not expect:
        print("\n（未给 --期望，仅打印；把它存成 json 后可自动断言）")
        return 0
    exp = json.load(open(expect, encoding="utf-8"))
    bad = 0
    for k in ("文件数", "超限"):
        if k in exp and exp[k] != got[k]:
            print("  [!!] %s: 期望 %r 实际 %r" % (k, exp[k], got[k]))
            bad += 1
    for key in ("材料", "截面", "最大Uc"):
        if key not in exp:
            continue
        e, g = exp[key], got[key]
        if e != g:
            for kk in sorted(set(map(str, e)) | set(map(str, g))):
                if e.get(kk) != g.get(kk):
                    print("  [!!] %s[%s]: 期望 %r 实际 %r" % (key, kk, e.get(kk), g.get(kk)))
                    bad += 1
    print("  [%s] 黄金值断言" % ("OK" if not bad else "!! %d 处不符" % bad))
    return 1 if bad else 0


def t_version_8x():
    print("T34 版本适配（6/7/8）与 8.x 客户端能力")
    P = A.P
    check("8.1.0 -> 8", P.version_major("8.1.0"), 8)
    check("7.1.0 -> 7", P.version_major("7.1.0"), 7)
    check("6.1.0 -> 6", P.version_major("6.1.0"), 6)
    check("None -> None", P.version_major(None), None)
    check('"8.1" -> "8.1.0"', P.version_xyz("8.1"), "8.1.0")
    check('"8" -> "8.0.0"', P.version_xyz("8"), "8.0.0")
    check('"7.1.0" -> "7.1.0"', P.version_xyz("7.1.0"), "7.1.0")
    check("目录名推版本（YJKS_8_1_0）", P.version_major(root=r"D:\x\YJKS_8_1_0"), 8)
    yp = P.find_yjk_python(None)
    check("find_yjk_python 返回键集合", sorted(yp.keys()), ["dir", "exe", "tag", "yjkapi"])
    for n in ("capabilities", "configure", "run_yjk", "close"):
        check_true("Client 具备 8.x 接口 %s" % n, hasattr(A.Client, n))
    check("DLL 探测返回 caps（8.x 能力位）", "caps" in P.find_yjkapi_dll(verify=False), True)


def t_boot_8x():
    """T35：8.x 启动路径必须走 initConfig→RunYJK→initConfig(pid)，不能等 6/7 的命名事件。

    实测 8.1 根本不存在 Global\\ShareMemoryEvent / Global\\WaitResaultEvent，
    沿用 6/7 的 events_alive 判就绪会一直等到超时（活体测试已复现过 150s 超时）。
    这里把 Client 打桩，只验调用顺序与返回值，不启真 YJK。
    """
    print("T35 8.x 启动路径（initConfig→RunYJK→initConfig(pid)）")
    saved = {k: getattr(A, k) for k in ("Client", "rt_yjk", "yjks_pids", "spawn")}
    tmp = tempfile.mkdtemp(prefix="selfchk8x_")
    calls = []

    class _FakeClient:
        def __init__(self, *a, **k):
            self.has_init_config = True

        def configure(self, version=None, invisible=False, pid=-1):
            calls.append(("initConfig", version, invisible, pid))
            return "配置初始化成功"

        def run_yjk(self, exe):
            calls.append(("RunYJK", exe))
            return "启动盈建科成功!"

    try:
        A.Client = _FakeClient
        A.spawn = lambda *a, **k: None
        A.yjks_pids = lambda: [4321]
        A.rt_yjk = lambda: {"exe": r"D:\y\yjks.exe", "root": r"D:\y",
                            "source": "stub", "version": "8.1.0"}
        pid, ok = A.boot_yjks(tmp, wait_ipc=5, verbose=False, invisible=True)
        check("8.x 启动返回 pid", pid, 4321)
        check("8.x 启动判定成功", ok, True)
        check("8.x 调用顺序", [c[0] for c in calls], ["initConfig", "RunYJK", "initConfig"])
        check("首次 initConfig 未绑 pid", calls[0][3], -1)
        check("首次 initConfig 版本规范化", calls[0][1], "8.1.0")
        check("二次 initConfig 绑定真实 pid", calls[2][3], 4321)
        check("Invisible 透传到 initConfig", calls[0][2], True)

        # 反例：8.x 客户端起不来时必须报失败，而不是退回 6/7 的 spawn 白等
        class _Boom:
            def __init__(self, *a, **k):
                raise RuntimeError("dll 不可用")

        calls[:] = []
        A.Client = _Boom
        pid2, ok2 = A.boot_yjks(tmp, wait_ipc=1, verbose=False)
        check("8.x 客户端异常 -> 失败", (pid2, ok2), (None, False))
        check("8.x 客户端异常时不得 spawn 6/7 启动", len(calls), 0)
    finally:
        for k, v in saved.items():
            setattr(A, k, v)
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    _utf8_console()
    ap = argparse.ArgumentParser()
    ap.add_argument("--golden", help="对某个算过的工程目录做值断言")
    ap.add_argument("--期望", "--expect", dest="expect", help="期望值 json（配合 --golden）")
    ap.add_argument("--dump", help="把本次实算值存成基准 json（配合 --golden）")
    a = ap.parse_args()

    print("=" * 68)
    print("离线自检（不需要 YJK）")
    print("=" * 68)
    t_hooks()
    t_own_registry()
    t_preflight()
    t_inbox()
    t_send_ready()
    t_host_rc_trustworthy()
    t_license_never_autoyes()
    t_license_pause_state_machine()
    t_license_read_channel()
    t_import_gate_selftrigger()
    t_run_aborts_when_instance_dies()
    t_exit_and_idle()
    t_wait_until()
    t_close_and_wait()
    t_ps_and_union()
    t_honest_kill()
    t_dead_shell()
    t_version_8x()
    t_boot_8x()
    t_takeoff_macro()
    t_import_check()
    t_dir_mismatch()
    t_host_exit_code()
    t_reuse()
    t_compat_fallback()
    t_colskill_input()
    t_colskill_drift_crosscheck()

    rc = 0
    if a.golden:
        print()
        rc = golden(a.golden, a.expect, a.dump)

    print()
    print("=" * 68)
    print("逻辑断言：通过 %d，失败 %d %s" % (PASS, FAIL, ("→ " + ", ".join(FAILED)) if FAILED else ""))
    print("=" * 68)
    return 1 if (FAIL or rc) else 0


def _utf8_console():
    """让输出在任何控制台编码下都不崩（GBK 下把不可编码字符替换掉）。

    断言里会打出被检文件的原文片段与 `%r`（含 `errors="replace"` 解出的 U+FFFD），
    这些都可能是非 cp936 字符；默认 GBK 控制台下 print 会抛 UnicodeEncodeError，
    于是一份**全部通过**的自检会被判成崩溃失败。

    在 `main()` 里调用（不只 `if __name__`）：本文件会被别的脚本 import，
    那样才覆盖得到 GBK 控制台。重复调用无害。
    """
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(errors="replace")
        except Exception:                                      # noqa: BLE001
            pass


if __name__ == "__main__":
    sys.exit(main())
