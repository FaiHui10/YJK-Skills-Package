# -*- coding: utf-8 -*-
"""参数化生成「裙楼楼盖 + 次梁布置」YJK 模型（外部生成 ydb，不依赖 YJK 运行）。

用法
----
    python build_floor.py --layout S0_无次梁 --out ../models/S0.ydb
    python build_floor.py --layout S3_十字梁 --out ../models/S3.ydb --mini

★ API 引导全部交给 `yjk_api.py`（内部含「必须用安装目录自带 STCAD 程序集」等 4 条硬性约束）。
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import yjk_api                                                     # noqa: E402

D, C = None, None           # 由 _api() 惰性加载：参数解析完成前不碰官方 DLL
import clr                                                         # noqa: E402
from spec import LAYOUTS, grids, load                              # noqa: E402


def _api():
    """取 YJK 建模 API（首次用到才 bootstrap）。

    为什么惰性：bootstrap 会加载官方 STCAD 程序集。老版本在**模块导入**时就做这件事，
    于是连 `--help`（只想看用法、不该有任何副作用）也先把 DLL 装进进程；
    参数解析出错要退出时，DLL 也已经被加载了。
    """
    global D, C
    if D is None:
        D, C = yjk_api.bootstrap(verbose=True)
    return D, C

GRADE_CODE = {25: 250, 30: 300, 35: 350, 40: 400, 45: 450, 50: 500, 55: 550, 60: 600}


def _aslist(items):
    """把 Python list 转成**强类型** .NET List<T>（T = 首元素的 .NET 类型）。

    不能用 List<Object>：`beam_arrange` / `column_arrange` 的形参是
    `List<Mdl_Grid>` / `List<Mdl_Joint>`，List<Object> 无法转换。
    """
    import System
    if not items:
        return items
    t = clr.GetClrType(type(items[0]))
    lt = System.Collections.Generic.List[t]()
    for it in items:
        lt.Add(it)
    return lt


def build(cfg, key, out_ydb, mini=False):
    lay = LAYOUTS[key]
    g = cfg["几何"]
    if mini:
        g = dict(g, 跨数X=2, 跨数Y=1)
        cfg = dict(cfg, 几何=g)

    xlv, ylv, zhux, zhuy = grids(cfg, lay)
    D, C = _api()
    df = D.DataFunc()

    # ---------------- 标准层参数（混凝土等级/保护层/钢筋级别，缺一不可） -------
    def _para(t_slab):
        gc = GRADE_CODE[int(cfg["柱"]["等级"].lstrip("Cc"))]
        p = D.BzcPara()
        p.setVal(0, 9999)                 # 梁保护层：按规范自动
        p.setVal(14, 9999)                # 柱保护层：按规范自动
        p.setVal(1, t_slab)               # 板厚
        p.setVal(3, 15)
        p.setVal(22, 15)
        p.setVal(2, gc)                   # 板
        p.setVal(4, gc)                   # 柱
        p.setVal(5, gc)                   # 梁
        p.setVal(6, gc)                   # 墙
        p.setVal(15, 250)                 # 支撑
        for idx in (7, 8, 12, 23):
            p.setVal(idx, cfg["材料"]["主筋级别"])
        for idx in (16, 17, 18, 19, 20):
            p.setVal(idx, cfg["材料"]["箍筋级别"])
        p.setVal(21, 235)                 # 钢号
        p.setVal(24, 5)
        p.setVal(25, 2)
        p.setVal(9, 50)
        p.setVal(10, 100)
        p.setVal(11, 200)
        return p

    # 板/梁/柱可各自等级 —— 用两个标准层参数串分别建 板 与 构件？
    # 简化：一个标准层一套参数，板与梁取同等级（本工程均为 C30），柱另按柱等级。
    # YJK 的 Para 里 板/柱/梁/墙 各有槽位，柱等级单独占 4 号位。
    def _para_full(t_slab, grade_slab, grade_col):
        p = _para(t_slab)
        p.setVal(2, GRADE_CODE[int(grade_slab.lstrip("Cc"))])       # 板
        p.setVal(5, GRADE_CODE[int(grade_slab.lstrip("Cc"))])       # 梁
        p.setVal(4, GRADE_CODE[int(grade_col.lstrip("Cc"))])        # 柱
        return p

    std = df.StdFlr_Generate(
        int(g["层高"]), float(cfg["荷载"]["附加恒载"]), float(cfg["荷载"]["活载"]),
        _para_full(lay["板厚"], cfg["板"]["等级"], cfg["柱"]["等级"]).GetValString())

    # ---------------- 节点 ----------------
    node = {}
    for x in xlv:
        for y in ylv:
            node[(x, y)] = df.Joint_Generate(std.ID, x, y, 0)

    # ---------------- 网格 / 梁线 ----------------
    zhux_set, zhuy_set = set(zhux), set(zhuy)
    grids_main, grids_sec = [], []
    for yy in ylv:                                   # 沿 X 走的梁（位于 y=yy）
        ax = df.Axis_Generate(std.ID, node[(xlv[0], yy)].ID, node[(xlv[-1], yy)].ID)
        for i in range(len(xlv) - 1):
            gr = df.Grid_Generate(std.ID, node[(xlv[i], yy)].ID,
                                  node[(xlv[i + 1], yy)].ID, ax.ID)
            (grids_main if yy in zhuy_set else grids_sec).append(gr)
    for xx in xlv:                                   # 沿 Y 走的梁（位于 x=xx）
        ax = df.Axis_Generate(std.ID, node[(xx, ylv[0])].ID, node[(xx, ylv[-1])].ID)
        for j in range(len(ylv) - 1):
            gr = df.Grid_Generate(std.ID, node[(xx, ylv[j])].ID,
                                  node[(xx, ylv[j + 1])].ID, ax.ID)
            (grids_main if xx in zhux_set else grids_sec).append(gr)

    # ---------------- 截面定义 ----------------
    mb = cfg["主梁"]
    sec_main = df.BeamSect_Def(6, 1, "%d,%d" % (mb["宽"], mb["高"]))
    if grids_main:
        df.beam_arrange(_aslist(grids_main), sec_main, 0, 0, 0, 0.0)

    if lay["次梁"] and grids_sec:
        sb = lay["次梁"]
        sec_sec = df.BeamSect_Def(6, 1, "%d,%d" % (sb["宽"], sb["高"]))
        df.beam_arrange(_aslist(grids_sec), sec_sec, 0, 0, 0, 0.0)

    # ---------------- 柱（仅柱网交点） ----------------
    cs = cfg["柱"]
    sec_col = df.ColSect_Def(6, 1, "%d,%d" % (cs["边长"], cs["边长"]))
    cnodes = [node[(x, y)] for x in zhux for y in zhuy]
    df.column_arrange(_aslist(cnodes), sec_col, 0, 0, 0.0, 0)

    # ---------------- 板（每个次梁/主梁围成的格子一块） ----------------
    nslab = 0
    for i in range(len(xlv) - 1):
        for j in range(len(ylv) - 1):
            info = (D.SlabCreateInfo()
                    .SetCentroid((xlv[i] + xlv[i + 1]) // 2, (ylv[j] + ylv[j + 1]) // 2)
                    .SetThick(int(lay["板厚"])).SetStdFlr(std).SetCc(0)
                    .SetDeadLive(float(cfg["荷载"]["附加恒载"]),
                                 float(cfg["荷载"]["活载"])))
            df.slab_arrange(info)
            nslab += 1

    # ---------------- 楼层组装 ----------------
    df.Floor_Assemb(0, std, int(g["层数"]), int(g["层高"]))

    df.DbModel_Assign()
    model = df.GetDbModelData()
    stat = dict(标准层=len(model.m_StdFlr), 自然层=len(model.m_Floor),
                节点=len(model.m_Joint), 网格=len(model.m_Grid), 轴线=len(model.m_Axis),
                柱段=len(model.m_ColSeg), 梁段=len(model.m_BeamSeg), 板=len(model.m_Slab))
    print("模型构成：%s" % stat)

    # ★ 内存模型为空就当场失败：DataFunc 一个构件都没建出来时，CreateYDB 照样可能
    #   写出（或写出一个）文件，下游只按"文件在不在"判定，会把它当成品送去算。
    empty = [k for k in ("自然层", "节点", "网格", "梁段", "柱段", "板") if not stat.get(k)]
    if empty:
        raise SystemExit(
            "内存模型是空的：%s 为 0（模型构成 %s）\n"
            "  DataFunc 没有把几何建出来（荷载/板厚 等参数不合理、或本版本 API 形参不匹配）。\n"
            "  此时写出的 .ydb 只是空壳，YJK 导入后会报「模型中没有单元数据」。"
            % ("、".join(empty), stat))

    if os.path.exists(out_ydb):
        os.remove(out_ydb)
    my = C.Hi_AddProjectToYjk(model)
    ok = my.CreateYDB(os.path.dirname(os.path.abspath(out_ydb)),
                      os.path.basename(out_ydb))
    size = os.path.getsize(out_ydb) if os.path.exists(out_ydb) else -1
    print("CreateYDB -> %s  %s  (%d bytes)" % (ok, out_ydb, size))
    # ★ 老版本把 `ok` 只交给这行 print：CreateYDB 返回 False（或没写出文件）时
    #   main() 仍 return 0，调用方（run_all_yjk.py 只按"文件是否存在"判定）
    #   会拿着退出码 0 进入下一阶段，错误被推迟到那时才暴露。
    #   正确写法在本包已有样板（column-section-opt/frame_build.py:577-581）。
    if not ok:
        raise SystemExit(
            "CreateYDB 返回失败：ok=%r（%s）\n"
            "  模型已在内存里建好（%s），但没能落盘。\n"
            "  常见原因：输出目录不存在 / 无写权限 / 同名文件被别的进程占着。"
            % (ok, out_ydb, stat))
    if size <= 0:
        raise SystemExit(
            "CreateYDB 声称成功，但产物不存在或是 0 字节：%s（%d bytes）\n"
            "  绝不能把这种文件当模型交给下一阶段。" % (out_ydb, size))
    return stat


def _utf8_console():
    """让输出在任何控制台编码下都不崩（GBK 下把不可编码字符替换掉）。

    为什么需要：本脚本会把**用户给的** `--out` 路径打出来（`CreateYDB -> …` 与报错信息），
    路径里可能含 cp936 编不出的字符；GBK 控制台下 `print` 抛 UnicodeEncodeError 会
    **以退出码 1 中断**一个其实已经成功的任务。
    ★ 只在 CLI 入口调用，**不在 import 时改 stdout**。
    """
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass


def check_out_path(out_ydb):
    """输出路径的落盘前检查：给的是目录 / 父目录建不出来 → 可读报错。

    放在**建模型之前**：以前 `--out D:\\不存在\\S0.ydb` 会先把整套几何建完、
    再在写盘那一步失败（而 `CreateYDB` 的失败以前还只打一行日志、退出码 0）。
    """
    p = os.path.abspath(out_ydb)
    if os.path.isdir(p):
        raise SystemExit("--out 给的是目录，不是 .ydb 文件名：%s\n"
                         "  怎么办：给一个文件名，例如 %s" % (p, os.path.join(p, "S0.ydb")))
    d = os.path.dirname(p)
    if d and not os.path.isdir(d):
        try:
            os.makedirs(d, exist_ok=True)
        except OSError as e:
            raise SystemExit("输出目录建不出来（%s）：%s" % (e, d))
    return p


def main():
    _utf8_console()          # ★ 必须在 argparse 之前：--help 也是写到 stdout 的
    ap = argparse.ArgumentParser()
    ap.add_argument("--layout", required=True, choices=list(LAYOUTS))
    ap.add_argument("--out", required=True)
    ap.add_argument("--config", default=None)
    ap.add_argument("--mini", action="store_true", help="只建 2x1 跨的小模型用于自检")
    a = ap.parse_args()
    cfg = load(a.config)
    out = check_out_path(a.out)
    print("【%s】%s  板厚 %d  次梁 %s"
          % (a.layout, LAYOUTS[a.layout]["名称"], LAYOUTS[a.layout]["板厚"],
             LAYOUTS[a.layout]["次梁"]))
    build(cfg, a.layout, out, mini=a.mini)
    return 0


if __name__ == "__main__":
    sys.exit(main())
