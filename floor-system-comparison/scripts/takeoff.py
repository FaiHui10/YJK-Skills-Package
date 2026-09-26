# -*- coding: utf-8 -*-
r"""裙楼楼盖工程量统计（按**广东省2018定额**的计算规则）。

数据来源分两层：
  * 几何/截面  ← 我们自己生成的 `models/<S>.ydb`（轴线、节点、梁段、板）
  * 配筋        ← YJK 实算产物（`YJK_run/<S>/设计结果/wpj*.out`；板筋另取）

★★ 关键定额规则（正文见 `refs/gd2018*.pkl`，已抽原文核对）：
  ── 混凝土（上册 p.250 第10/11条、p.255）──
  10. **有梁板（包括主、次梁与板）按梁、板体积之和计算**；
      无梁板按板与柱帽体积之和计算。
  11. **没有与板相连的梁按梁体积计算，执行梁项目**。—— 本工程所有梁都与板相连，
      故全部并入「有梁板」子目 A1-5-14。
      楼板混凝土体积应扣除墙、柱混凝土体积。
      梁与柱连接时梁长算至柱内侧面；主梁与次梁连接时次梁长算至主梁内侧面。
  ── 模板（下册 p.49）──
   ① 按混凝土与模板接触面积以 ㎡ 计算；
   ② **梁与梁、梁与墙、梁与柱交接处，净空长度以 m 计算，不扣减接合处的模板面积**；
   ⑤ **板模板工程量应扣除混凝土柱、梁、墙所占的面积**。
  => 物理上（"接触面积"口径）：
      梁模板 = [2×(梁高-板厚) + 梁宽] × 梁净长
      板模板 = 楼盖水平投影面积 - 梁底占面积 - 柱占面积
  ── 支模高度（下册 p.45 说明五）──
       **支模高度指楼层高度**（不是净高）。本工程层高 4.8 m > 3.6 m，
       故梁、板各按「3.6m 基价子目 + 2 × 每增 1m 增量」计（每超 1m 计一次，不足 1m 按 1m）。

单位约定：ydb 内坐标是 **mm**，函数返回 **m / m2 / m3**。

★ 口径守卫（不要绕过）
----------------------
本脚本的数据来源写明是「我们自己生成的**单标准层**楼盖模型」（`make_ydb.py` 的产物）。
把**整楼模型**喂进来时，`formwork()` 里
`板模板 = 楼盖投影面积 - 梁底占面积 - 柱占面积` 会算出**负的模板面积**
（实测：`每层模板: 梁 6179.0 板 -967.3 m2`）—— 梁段/柱段是**全楼**累加的，
而板面积只按一个标准层算，两个口径根本不匹配。
负面积物理上不可能，却被 `build_report.py` 直接乘单价变成**负造价**，全程无断言。
所以 `concrete()` / `formwork()` 现在对任一负值当场报错（见 `_guard_nonneg`），
并在报错里点明「本脚本按单标准层模型设计」。

用法
----
    python takeoff.py                          # 默认方案 S0..S4（读 <技能>/models）
    python takeoff.py S3 --models-dir <目录>    # 指定模型目录（--models-dir 以前不可传）
"""
import argparse
import collections
import math
import os
import sqlite3
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))

NONE_ID = 4294967295
DEFAULT_SCHEMES = ["S0", "S1", "S2", "S3", "S4"]


# ------------------------------------------------------------------ 读模型
def _shapeval(sv):
    """`"1,<b>,<h>,<Mat>,<ID>,"` -> (b, h, Mat)。尺寸**只**存在于这里。"""
    p = [x for x in (sv or "").split(",") if x != ""]
    if len(p) < 4:
        return 0, 0, 0
    return int(float(p[1])), int(float(p[2])), int(float(p[3]))


def load(scheme, models_dir=None):
    """读 `<模型目录>/<方案>.ydb`，返回几何字典（长度已是 m）。

    `models_dir` 默认 `<技能>/models`；以前这个参数**永远拿不到实参**
    （`__main__` 里写死 `load(scheme, models_dir=None)`），用户没法指向别的模型目录。
    现在由命令行 `--models-dir` 传进来。

    模型缺失时要给**可读**提示：以前直接
    `sqlite3.OperationalError: unable to open database file`（什么都不说明）。
    """
    mdir = models_dir or os.path.join(ROOT, "models")
    ydb = os.path.join(mdir, scheme + ".ydb")
    if not os.path.exists(ydb):
        raise SystemExit(
            "找不到模型：%s\n"
            "  - 本脚本读的是 <模型目录>/<方案>.ydb，默认模型目录 = %s\n"
            "  - 模型由 make_ydb.py 生成（python make_ydb.py --all，或 --scheme S3_十字梁）\n"
            "  - 模型在别处就用 --models-dir <目录> 指过来\n"
            "  - 注意口径：本脚本按**单标准层**楼盖模型设计，别拿整楼模型来跑（见 --help）。"
            % (ydb, mdir))
    try:
        con = sqlite3.connect("file:%s?mode=ro" % ydb.replace("\\", "/"), uri=True)
    except sqlite3.Error as e:
        raise SystemExit("打不开模型 %s：%s" % (ydb, e))
    try:
        jt = {r[0]: (float(r[1]) / 1000.0, float(r[2]) / 1000.0)
              for r in con.execute("select idNew,X,Y from tblJoint")}

        # 截面
        bsec = {}
        for r in con.execute("select idNew,ShapeVal from tblBeamSect"):
            b, h, m = _shapeval(r[1])
            bsec[r[0]] = {"b": b / 1000.0, "h": h / 1000.0, "mat": m}
        csec = {}
        for r in con.execute("select idNew,ShapeVal from tblColSect"):
            b, h, m = _shapeval(r[1])
            csec[r[0]] = {"b": b / 1000.0, "h": h / 1000.0, "mat": m}

        # 网格（= 梁段所在轴线）
        grid = {}
        for r in con.execute("select idNew,idNode1,idNode2 from tblGrid"):
            if r[1] in jt and r[2] in jt:
                grid[r[0]] = (r[1], r[2])

        # 梁段：一条梁段 = 一个网格 + 一个截面
        segs = []
        for r in con.execute("select idDef,idGrid from tblBeamSeg"):
            if r[1] in grid and r[0] in bsec:
                segs.append({"sec": r[0], "grid": r[1]})

        # 柱：节点集合 + 柱截面
        col_nodes = set()
        col_secs = set()
        ncol = 0
        for r in con.execute("select idNewNode,idNewDef from tblColSeg"):
            if r[0] is not None and r[0] != NONE_ID:
                col_nodes.add(r[0])
            col_secs.add(r[1])
            ncol += 1

        # 板
        thicks = [r[0] for r in con.execute("select Thickness from tblSlab")]
        slab_th = collections.Counter(int(t) / 1000.0 for t in thicks)

        # 楼盖水平投影面积 = 相邻坐标围成的所有格子之和 = (xmax-xmin)*(ymax-ymin)
        xs = sorted({p[0] for p in jt.values()})
        ys = sorted({p[1] for p in jt.values()})
        span_x, span_y = xs[-1] - xs[0], ys[-1] - ys[0]

        # 标准层与楼层
        std = con.execute("select Height,Dead,Para from tblStdFlr").fetchone()
        stdh = float(std[0]) / 1000.0
        nfloor = con.execute("select count(*) from tblFloor").fetchone()[0]

        # 柱截面尺寸（统一取第一种）
        cb, chh = 0.0, 0.0
        if col_secs:
            s = sorted(col_secs)[0]
            if s in csec:
                cb, chh = csec[s]["b"], csec[s]["h"]
    except sqlite3.Error as e:
        raise SystemExit(
            "模型读不动：%s\n  原因：%s\n"
            "  本脚本需要这些表：tblJoint/tblGrid/tblBeamSeg/tblBeamSect/tblColSeg/"
            "tblColSect/tblSlab/tblStdFlr/tblFloor。\n"
            "  要么这不是 ydb（SQLite）文件，要么是别的技能/别的版本写出来的模型。"
            % (ydb, e))
    finally:
        con.close()

    return {
        "scheme": scheme, "jt": jt, "grid": grid, "segs": segs, "bsec": bsec,
        "csec": csec, "col_nodes": col_nodes, "ncol": ncol,
        "slab_th": slab_th, "nslab": len(thicks),
        "slab_area": span_x * span_y, "span_x": span_x, "span_y": span_y,
        "std_h": stdh, "nfloor": nfloor,
        "col_b": cb, "col_h": chh,
        "nx": len(xs), "ny": len(ys),
    }


def seg_dir(seg, jt):
    a = jt[seg["_n1"]]
    b = jt[seg["_n2"]]
    if abs(a[1] - b[1]) < 1e-6:
        return "X"
    if abs(a[0] - b[0]) < 1e-6:
        return "Y"
    return "D"


# ------------------------------------------------- 梁净长（定额：算至支承内侧面）
def beam_lengths(m):
    """返回按截面分组的净长统计。

    净长规则（上册 p.250）：
      * 梁与柱连接 → 梁长算至柱内侧面 => 该端扣 柱宽/2
      * 主梁与次梁连接 → 次梁长算至主梁内侧面 => 次梁端扣 主梁宽/2
      * 次梁与次梁相交 → 互扣被交梁宽/2
      * 主梁贯通次梁 → **不扣**（规则只要求次梁缩短）
    """
    jt, bsec = m["jt"], m["bsec"]
    # 准备梁段
    segs = []
    for s in m["segs"]:
        n1, n2 = m["grid"][s["grid"]]
        a, b = jt[n1], jt[n2]
        L = math.dist(a, b)
        segs.append({"n1": n1, "n2": n2, "L": L, "sec": s["sec"]})
    # 每个节点的入射梁段（按方向）
    at = collections.defaultdict(list)
    for i, s in enumerate(segs):
        a, b = jt[s["n1"]], jt[s["n2"]]
        d = "X" if abs(a[1] - b[1]) < 1e-6 else "Y"
        s["dir"] = d
        at[s["n1"]].append(i)
        at[s["n2"]].append(i)
    # 主梁 = 断面面积最大的截面
    areas = {k: v["b"] * v["h"] for k, v in bsec.items()}
    main_sec = max(areas, key=lambda k: areas[k])
    for s in segs:
        s["is_main"] = (s["sec"] == main_sec)
    # 被交梁宽度：按「哪个截面」取（同类取最宽）
    def _ded(node, idx):
        s = segs[idx]
        if node in m["col_nodes"]:
            return m["col_b"] / 2.0
        best = 0.0
        for k in at[node]:
            if k == idx or segs[k]["dir"] == s["dir"]:
                continue
            pb = bsec[segs[k]["sec"]]
            w = pb["b"] / 2.0
            if segs[k]["is_main"]:
                best = max(best, w)              # 主梁优先：次梁算至主梁内侧面
            elif not s["is_main"]:
                best = max(best, w)              # 次梁遇次梁：互扣半宽
            # 主梁遇次梁：不扣
        return best

    for i, s in enumerate(segs):
        s["net"] = max(0.0, s["L"] - _ded(s["n1"], i) - _ded(s["n2"], i))

    out = collections.defaultdict(lambda: {"n": 0, "geo": 0.0, "net": 0.0})
    for s in segs:
        sec = bsec[s["sec"]]
        key = (sec["b"], sec["h"], "主" if s["is_main"] else "次")
        o = out[key]
        o["n"] += 1
        o["geo"] += s["L"]
        o["net"] += s["net"]
    m["_segs"] = segs
    m["main_sec"] = main_sec
    return dict(out)


# ---------------------------------------------------------------- 口径守卫
SINGLE_FLOOR_HINT = (
    "本脚本按**单标准层**楼盖模型设计（数据来源：make_ydb.py 生成的 "
    "<模型目录>/<方案>.ydb）。当前模型的层数/板块数/构件数不像单标准层模型 —— "
    "请改用 make_ydb 产出的模型，或用 --models-dir 指向正确的模型目录。")


def _guard_nonneg(m, vals, where):
    """结果里出现负值 = 口径用错了，当场报错，绝不把负数算下去。

    为什么必须有这道守卫（实测事故）：整楼模型喂进 `formwork()` 时，
    `板模板 = 楼盖投影面积 - 梁底占面积 - 柱占面积` 得到
    **负的模板面积**（`每层模板: 梁 6179.0 板 -967.3 m2`）。
    根因是两个口径不匹配：整楼模型的梁段/柱段是**全楼**累加（还含层高不同的
    首层拆分段），而板投影面积只按一个标准层算。负面积物理上不可能，
    但它会被 build_report.py 直接乘单价变成**负造价**，全程没有任何断言 ——
    所以这里改成硬失败（SystemExit），并把"该用哪种模型"写清楚。

    `vals` 是 [(名字, 数值), ...]；`where` 是函数名，便于定位。
    """
    bad = [(k, float(v)) for k, v in vals if float(v) < 0]
    if bad:
        raise SystemExit(
            "%s() 算出负值：%s\n"
            "  %s\n"
            "  当前模型：%s（自然层 %s 层 / 板块 %s 块 / 梁段 %s 段 / 柱段 %s 段，"
            "层高 %.2f m）"
            % (where, "，".join("%s = %.3f" % (k, v) for k, v in bad),
               SINGLE_FLOOR_HINT, m.get("scheme"), m.get("nfloor"),
               m.get("nslab"), len(m.get("segs") or []), m.get("ncol"),
               m.get("std_h", 0.0)))


# ---------------------------------------------------------------- 混凝土
def concrete(m, per_floor=False, slab_area=None):
    """混凝土体积（m3/层）：有梁板 = 梁 + 板；柱另计。

    板体积 = 板投影面积×板厚 - 柱占体积（定额：楼板砼体积应扣除墙、柱）。

    `slab_area` 用于覆盖轴网面积：YJK 的《全楼…钢筋用量》表给出**模型实际**
    楼面面积 2288.25 m2/层（板伸至周边梁外皮，比轴网 67.2×33.6=2257.92 大
    约半个梁宽），按模型口径取值更贴合「图示面积」。
    """
    ln = beam_lengths(m)
    beam_v = sum(k[0] * k[1] * v["net"] for k, v in ln.items())
    th = m["slab_th"].most_common(1)[0][0]
    area = slab_area or m["slab_area"]
    slab_area_empty = m["slab_area"]
    slab_v = area * th - m["ncol"] * m["col_b"] * m["col_h"] * th
    col_v = m["ncol"] * m["col_b"] * m["col_h"] * m["std_h"]
    d = {"beam_v": beam_v, "slab_v": slab_v, "youliangban_v": beam_v + slab_v,
         "col_v": col_v, "by_sec": ln, "slab_area_used": area,
         "slab_area_axis": slab_area_empty}
    _guard_nonneg(m, [(k, d[k]) for k in
                      ("beam_v", "slab_v", "youliangban_v", "col_v")], "concrete")
    if not per_floor:
        for k in ("beam_v", "slab_v", "youliangban_v", "col_v"):
            d[k] *= m["nfloor"]
    return d


# ---------------------------------------------------------------- 模板
def formwork(m, per_floor=False, slab_area=None):
    """模板接触面积（m2/层）。

    梁：`[2×(梁高-板厚) + 梁宽] × 梁净长`
    板：`板投影面积 - 梁底占面积 - 柱占面积`（定额下册 p.49 第⑤条）
    """
    ln = beam_lengths(m)
    th = m["slab_th"].most_common(1)[0][0]
    area = slab_area or m["slab_area"]
    beam_fw = 0.0
    beam_foot = 0.0
    for (b, h, _kind), v in ln.items():
        beam_fw += (2.0 * (h - th) + b) * v["net"]
        beam_foot += b * v["net"]
    slab_fw = area - beam_foot - m["ncol"] * m["col_b"] * m["col_h"]
    d = {"beam_fw": beam_fw, "slab_fw": slab_fw, "total": beam_fw + slab_fw,
         "slab_th": th, "n": ln, "slab_area_used": area}
    _guard_nonneg(m, [("beam_fw", beam_fw), ("slab_fw", slab_fw)], "formwork")
    if not per_floor:
        for k in ("beam_fw", "slab_fw", "total"):
            d[k] *= m["nfloor"]
    return d


def _safe_console():
    """stdout / stderr 编码错误策略改成 errors='replace'（与 summary_xlsx.py 同一套路）。

    本脚本原来在打印里直接用 m2/m3 的上标字符（U+00B2 / U+00B3，cp936 编不出），
    GBK 控制台下 `print` 会抛 UnicodeEncodeError —— 数字都算对了，却因为一行
    打印崩掉、退出码变 1。源码里已全部换成 ASCII（m3 / m2），这层只是兜底。
    """
    for st in (sys.stdout, sys.stderr):
        try:
            st.reconfigure(errors="replace")
        except (AttributeError, ValueError, OSError):
            pass


# ------------------------------------------------------------------ 报告
def summary(scheme, models_dir=None, slab_area=None):
    m = load(scheme, models_dir)
    ln = beam_lengths(m)
    c = concrete(m, per_floor=True, slab_area=slab_area)
    f = formwork(m, per_floor=True, slab_area=slab_area)
    print("=" * 78)
    print("%s  梁段 %d  节点 %d  柱 %d  板 %d 块 (厚 %s)  层高 %.2f m × %d 层"
          % (scheme, len(m["segs"]), len(m["jt"]), m["ncol"], m["nslab"],
             m["slab_th"].most_common(1)[0][0] * 1000, m["std_h"], m["nfloor"]))
    for k, v in sorted(ln.items(), key=lambda kv: -kv[1]["net"]):
        print("   梁 %s  %3d 段  轴线长 %8.1f m  净长 %8.1f m"
              % ("%d×%d %s梁" % (k[0] * 1000, k[1] * 1000, k[2]),
                 v["n"], v["geo"], v["net"]))
    print("   【每层】砼 梁 %8.2f + 板 %8.2f = 有梁板 %8.2f m3 ；柱 %8.2f m3"
          % (c["beam_v"], c["slab_v"], c["youliangban_v"], c["col_v"]))
    print("   【每层】模板 梁 %8.1f + 板 %8.1f = %8.1f m2"
          % (f["beam_fw"], f["slab_fw"], f["total"]))
    return m, ln, c, f


def main(argv=None):
    """命令行入口。

    ★ 为什么要把 `models_dir` 暴露出来：以前 `__main__` 里是
      `summary(s)` -> `load(scheme, models_dir=None)`，那个 `models_dir`
      **永远拿不到实参**，于是模型只能放在 <技能>/models 下 —— 用户想指向
      别处（例如 make_ydb.py 刚写到某个临时目录里的模型）没有任何办法。
    """
    _safe_console()
    ap = argparse.ArgumentParser(
        prog="takeoff.py",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="裙楼楼盖工程量统计（广东省2018定额口径）。",
        epilog=__doc__)
    ap.add_argument("schemes", nargs="*", metavar="方案",
                    help="方案标签，对应 <模型目录>/<方案>.ydb；默认 %s"
                         % " ".join(DEFAULT_SCHEMES))
    ap.add_argument("--models-dir", default=None,
                    help="模型目录（默认 <技能>/models）；指向 make_ydb 产出的模型")
    ap.add_argument("--slab-area", type=float, default=None,
                    help="覆盖每层楼盖投影面积 m2（默认按轴网包络算）")
    a = ap.parse_args(argv)
    for s in (a.schemes or DEFAULT_SCHEMES):
        summary(s, a.models_dir, a.slab_area)
    return 0


if __name__ == "__main__":
    sys.exit(main())
