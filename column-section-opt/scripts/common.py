# -*- coding: utf-8 -*-
"""公共：读配置、柱位分组、量纲换算。

分组规则（与建模脚本的节点编号一致：先 X 后 Y，nc = i*NY + j + 1）
  角柱：两个方向都靠边；边柱：只有一个方向靠边；中柱：都不靠边。
"""
import json
import os
import sqlite3
import sys

# 混凝土轴心抗压强度设计值（N/mm²）——配置里没有时的兜底
FC_DEFAULT = {"C25": 11.9, "C30": 14.3, "C35": 16.7, "C40": 19.1, "C45": 21.1,
              "C50": 23.1, "C55": 25.3, "C60": 27.5}


def load_config(path):
    cfg = json.load(open(path, encoding="utf-8"))
    g = cfg.setdefault("几何", {})
    g.setdefault("跨度X", 6000)
    g.setdefault("跨度Y", 6000)
    g.setdefault("层高", 3600)
    cfg.setdefault("截面", {}).setdefault("步长", 50)
    cfg["截面"].setdefault("最小边长", 400)
    cfg["截面"].setdefault("最大边长", 1200)
    cfg["截面"].setdefault("分组", ["中柱", "边柱", "角柱"])
    cfg.setdefault("抗震", {}).setdefault("轴压比限值", 0.75)
    cfg["抗震"].setdefault("轴压比目标", cfg["抗震"]["轴压比限值"] * 0.96)
    cfg.setdefault("混凝土", {}).setdefault("候选等级", ["C30"])
    cfg["混凝土"].setdefault("轴心抗压强度设计值", {})
    cfg.setdefault("造价", {})
    cfg["造价"].setdefault("模板单价元每m2", 65)
    cfg["造价"].setdefault("钢筋单价元每t", 4000)
    cfg["造价"].setdefault("钢筋密度kg每m3", 7850)
    cfg["造价"].setdefault("纵筋最小配筋率", 0.006)
    return cfg


def fc_of(cfg, grade):
    return cfg["混凝土"]["轴心抗压强度设计值"].get(grade, FC_DEFAULT.get(grade, 14.3))


def price_of(cfg, grade):
    return cfg["混凝土"]["单价元每m3"].get(grade, 500.0)


def node_count(cfg):
    return (cfg["几何"]["跨数X"] + 1, cfg["几何"]["跨数Y"] + 1)


def group_of_nc(cfg, nc):
    """按柱号（标准层内建模序号，从 1 起、先 X 后 Y）判定分组。

    ★ 适用范围：**由 `frame_build.py` 生成的模型**（模式 A）——节点编号就是本函数
      与 `frame_build` 约定的 `i*NY + j + 1`，且跨数来自 config，所以不是写死某个工程。
      对**任意真实工程**（模式 B，柱号规律未知），请用 `expand_plan.py` 的
      `classify()`：它按柱的**平面坐标**判定，与编号无关。

    ★★ 真实模型请直接用本模块的 `groups_from_model(db, std_no)`（按坐标分组）；
      本函数只对**纯框架**成立：框-筒/抽柱模型在核心筒范围内没有柱，柱号会跳号，
      照 `nc = i*NY + j + 1` 算会**把柱分错组，而且分错组不报错**（只是把截面
      写到错误的柱子上）。调用前先用 `assert_pure_frame()` 把柱数卡住。
    """
    nx, ny = node_count(cfg)
    i, j = (nc - 1) // ny, (nc - 1) % ny
    ex, ey = (i in (0, nx - 1)), (j in (0, ny - 1))
    if ex and ey:
        return "角柱"
    if ex or ey:
        return "边柱"
    return "中柱"


def groups_from_model(db, std_no):
    """按**柱坐标**现算某标准层的分组：{"中柱": [柱号…], "边柱": […], "角柱": […]}
    （只返回非空的组）。

    ★ 为什么必须有它：`group_of_nc` 的 `nc = i*NY + j + 1` 只在 `frame_build.py`
      建出的**纯框架**里成立。框-筒模型在核心筒范围内没有柱，柱号会跳号，
      照 `group_of_nc` 算就会把柱分错组 —— 而**分错组不报错**，只是把截面写到错误的
      柱子上（这类错误往往只在对比实算结果时才暴露，代价很大）。
    ★ 判据复用 `expand_plan.classify()`（按柱的平面坐标：两个方向都在内部 = 中柱、
      只有一个在内部 = 边柱、都在边缘 = 角柱），对任意正交柱网都成立；
      口径与 `verify_results.groups_from_db` 一致，所以"选型"与"复核"不会分岔。
    ★ `expand_plan` 用**延迟导入**：调用方（section_opt/cost）也在同目录，
      放文件头会形成循环导入。
    """
    import expand_plan                                            # 同目录，延迟导入
    d = expand_plan.read_columns(db).get(int(std_no))
    if not d:
        return {}
    cls = expand_plan.classify(d["cols"])
    return {k: sorted(cls[k]) for k in ("中柱", "边柱", "角柱") if cls.get(k)}


def assert_pure_frame(cfg, n_cols):
    """纯框架自检：柱数必须 = (跨数X+1)×(跨数Y+1)，否则 `group_of_nc` 的口径不成立。

    ★ 为什么必须**硬失败**而不是警告：`group_of_nc` 假设柱号 = `i*NY + j + 1`
      （frame_build.py 的节点编号）。真实工程（框-筒、抽柱、核心筒范围内无柱）柱号会
      跳号，照这个口径分组不会报错，只会把截面写到错的柱子上。
      所以给不出 `--db`（无法按坐标分组）时，先把柱数卡住。
    """
    nx, ny = node_count(cfg)
    if int(n_cols) != nx * ny:
        raise SystemExit(
            "!! wpj 里解析到 %d 根柱，而 config 的纯框架柱数是 (%d+1)×(%d+1)=%d ——\n"
            "   `group_of_nc`（柱号 = i*NY+j+1）只对 `frame_build.py` 生成的纯框架成立；\n"
            "   本模型柱号跳号或含多段柱段，按柱号分组会**算错且不报错**。\n"
            "   请改用按坐标分组：加 `--db <模型.ydb/.ymd>`（common.groups_from_model）。"
            % (int(n_cols), cfg["几何"]["跨数X"], cfg["几何"]["跨数Y"], nx * ny))


def _die(msg):
    """「工具没跑成」→ 退出码 2（与"模型有缺陷"的 1 分开），消息走 stderr 且不崩编码。"""
    for s in (sys.stderr,):
        try:
            s.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass
    sys.stderr.write(msg.rstrip("\n") + "\n")
    sys.exit(2)


def require_ro(path):
    """只读打开模型库的**前置守卫**：存在 / 不是目录 / 非 0 字节 / 真的是 sqlite。

    ★★ 为什么不直接 `sqlite3.connect(...mode=ro...)` 就完事：
      * 路径不存在 / 给的是目录 → 裸 `OperationalError: unable to open database file`
        （既不说是哪个路径，也不说为什么）；
      * **0 字节或非 sqlite** 的文件 → `connect()` 是**成功**的，
        `DatabaseError: file is not a database` 要到第一条查询才抛 ——
        所以这里用 `PRAGMA schema_version` 在 connect 内就把它探出来。
    ★ 本模块（common）是造价/选型/复核三条链的共同入口，`--db` 指错时
      调用方都没有接异常 → 用户看到的是 traceback。翻成人话的收益最大。
    """
    p = os.path.abspath(str(path))
    if not os.path.exists(p):
        _die("模型库不存在：%s\n"
             "  常见原因：--db 路径拼错 / 文件还没生成 / 传了工程目录。\n"
             "  本工具**只读**打开，不会创建文件。" % p)
    if os.path.isdir(p):
        _die("--db 给的是目录，不是模型库文件：%s" % p)
    if os.path.getsize(p) == 0:
        _die("模型库是 0 字节（半写/损坏）：%s" % p)
    try:
        con = sqlite3.connect("file:%s?mode=ro" % p.replace("\\", "/"), uri=True)
        con.execute("PRAGMA schema_version").fetchone()
    except sqlite3.Error as e:
        _die("打不开模型库 %s：%s\n"
             "  常见原因：不是 sqlite 库（拿错文件）/ 库已损坏 / 文件被别的进程独占。"
             % (p, e))
    return con


def std_of_floor(db, floor_no):
    """自然层号 -> 标准层号（tblFloor.StdFlrID -> tblStdFlr.No_）；读不到返回 None。

    ★ 为什么要查而**不是直接假设 f 就是标准层号**：`frame_build.py` 的产出是 1:1
      （所以两者相等），但真实工程里一个标准层可以被多个自然层复用
      （例：`model_00.ydb` 只有 1 个标准层，6 个自然层全用它，wpj*.out 里
       每一层都写"标准层 1"），这时拿自然层号当标准层号就会"读不到分组"而误报错。
    """
    con = require_ro(db)          # ★ 坏路径给中文报错，不再抛裸 OperationalError
    try:
        row = con.execute("SELECT StdFlrID FROM tblFloor WHERE No_=?", (int(floor_no),)).fetchone()
        if not row:
            return None
        row2 = con.execute("SELECT No_ FROM tblStdFlr WHERE ID=?", (row[0],)).fetchone()
        return int(row2[0]) if row2 else None
    finally:
        con.close()


def layer_segment_map(model_cols, wpj_cols):
    """算某标准层的「wpj 柱段号 -> 模型柱号」折算表；对不上返回 None。

    ★ 为什么需要折算（实机验证 Core28 首层）
      YJK 会把一根柱沿高度切成多段，wpj 里就**以柱为单位、段号连续**地多印几条：
      Core28 的 4.5 m 首层是 16 根柱印 32 段，柱 k 的段号是 `2k-1`、`2k`
      （逐条用截面核对过：两段的截面与模型 `tblColSeg.No_` 1..16 的顺序完全对应，
      段号也首尾相接 —— N-C=1 的上节点就是 N-C=2 的下节点）。
      所以折算规则是 `模型柱号 = (段号-1)//k + 1`，k = 段数 / 模型柱数。
    ★ 判据（两条都满足才算"多段"）：段数是模型柱数的**整数倍**，且模型柱号**全都被覆盖**。
      不满足就返回 None —— 调用方**必须报错**：那说明 wpj 的 N-C 与模型 tblColSeg.No_
      不是同一套编号（例如模型整模连续编号、wpj 每层各自从 1 编），
      再算下去只会得到"分组整体错位、却不报错"的结果。
    """
    model_cols, wpj_cols = set(model_cols), set(wpj_cols)
    if not model_cols or not wpj_cols:
        return None
    if not model_cols <= wpj_cols:
        return None
    if len(wpj_cols) % len(model_cols):
        return None
    k = len(wpj_cols) // len(model_cols)
    out = {}
    for nc in wpj_cols:
        col = (int(nc) - 1) // k + 1
        if col not in model_cols:
            return None
        out[int(nc)] = col
    return out


def counts_by_group(cfg):
    """每个分组在这一层里有多少根柱。"""
    nx, ny = node_count(cfg)
    out = {}
    for nc in range(1, nx * ny + 1):
        g = group_of_nc(cfg, nc)
        out[g] = out.get(g, 0) + 1
    return out


def sides(cfg):
    s = cfg["截面"]
    return list(range(s["最小边长"], s["最大边长"] + 1, s["步长"]))


def floor_list(cfg):
    return list(range(1, cfg["几何"]["层数"] + 1))


def find_wpj(res_dir):
    """返回 {层号: wpj 文件路径}"""
    import re
    out = {}
    for f in os.listdir(res_dir):
        m = re.match(r"wpj(\d+)\.out$", f)
        if m:
            out[int(m.group(1))] = os.path.join(res_dir, f)
    return out


def resolve_res_dir(proj_or_res):
    """传工程目录或设计结果目录都行。"""
    if os.path.basename(os.path.normpath(proj_or_res)) == "设计结果":
        return proj_or_res
    return os.path.join(proj_or_res, "设计结果")


def _utf8_console():
    """让输出在任何控制台编码下都不崩（GBK 下把不可编码字符替换掉）。

    为什么需要：本包会打印 ✅ ❌ ⚠ −(U+2212) ² ³ 等**非 cp936** 字符，
    默认 GBK 控制台下 print 会抛 UnicodeEncodeError 并**以退出码 1 中断**，
    于是一个其实已经成功的任务（比如文件已经落盘）会被上层判成失败。
    errors=replace 让它在 UTF-8 控制台下原样输出、在 GBK 下退化成 ?，都不崩。

    ★ 本模块是本包最常被 import 的库（cost.py / section_opt.py / report.py /
      frame_build.py 都 import 它），所以**绝不能**在模块顶层调用它 ——
      那会改掉 import 它的那个进程的 stdout。下面只在 __main__ 里调用。
    """
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(errors="replace")
        except Exception:
            pass


if __name__ == "__main__":
    _utf8_console()
