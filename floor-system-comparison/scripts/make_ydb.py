# -*- coding: utf-8 -*-
r"""把 DataFunc 建出的 YJK 模型**序列化**成 .ydb（SQLite），不需要 YJK 运行。

为什么不是直接调 API 写盘
-------------------------
对照（YJKS 7.1 + STCAD 自带程序集）：

* `CsToYjk.Hi_AddProjectToYjk.CreateYDB(path, name)` —— **永久阻塞**
  （换 CWD / 带不带扩展名 / 保活 DataFunc 实例都试过，30s+ 不返回，不生成文件）。
  与技能文档一致：这套「建模接口」依赖官方建模接口与运行环境匹配。
* `Hi_AddProjectToYjk.IPC_ToYJK()` —— 返回 `True`（0.1s）但**模型并未进入** YJK：
  `yjk_save` 后 `S3_probe.ymd` 里 tblJoint/tblBeamSeg 全为 0。
  即技能里说的「Success 应答一文不值，只认客观证据」。

所以改成：**DataFunc 负责几何推理，本脚本负责落盘**。

依据（两条）
------------
1. 内存对象 `Mdl_*` 的字段与 ydb 表列**几乎一一对应**
   （`Mdl_Joint.X/Y/ID/StdFlrID`、`Mdl_BeamSect.b/h/ShapeVal/idNew`、
     `Mdl_BeamSeg.SectID/GridID/Ecc/HDiff1/HDiff2/Rotation/JYDef`、
     `Mdl_Slab.GridsID/VertexX/VertexY/Thickness/dead/live/xc/yc` …），
   DataFunc 已经算好了 ID、板块边界、节点-网格拓扑，本脚本只补 `idNew` 这类外键。
2. 骨架用 **YJK 自己建的**空工程（`YJK_run\S3_probe.ymd`）：77 张表齐全、
   `tblProjectPara` 1169 行、`tblStdFlrPara` 由 `Para` 展开而来 —— 这些都不用我们造，
   风险只在几何表上。

idNew 规则（自真实模型反推）
--------------------------
* `idNew` 是**全模型共享**的一个交叉引用序号（节点 76/77…、轴线 157…、网格 197…、
  截面 41/65…、梁段 397…、柱段 325…、板 476… 互不重叠），不是各表自增。
* `idNewBzc` = 所属`tblStdFlr.idNew`。
* `tblGrid.idNode1/idNode2` = 节点 idNew；`idAxis` = 轴线 idNew；`idCen` = 4294967295(无)。
* `tblBeamSeg`：`GridID`+`idGrid`、`SectID`+`idDef` 两套键都要写。
* `tblColSeg`：`idNewNode` = 节点 idNew，`idNewDef` = 柱截面 idNew（**有效外键**）。
* `tblSlab`：`GridsID` = 边界网格 **ID** 串，`idGridStr` = 同一批网格的 **idNew** 串，
  两者都带尾逗号。

荷载两表（`tblLoadSect` / `tblLoadSeg`）—— ★ 列名陷阱
----------------------------------------------------
* **这两张表的序号列叫 `No`，不是 `No_`**（其余几何表都是 `No_`）。写成 `No_` 时
  旧版 `_Writer` 会"照单全收"：真正的 `No` 留 0、多出来的键被默默丢掉，
  YJK 导入时会把**整批荷载静默丢弃**（不报错、不警告）。现在 `_Writer` 有未知列守卫，
  写错列名会当场报错（见 `_Writer.add`）。
* 字段对应（自真实模型 784 条梁间荷载反推）：
  `ElementKind=12`；`ShapeVal="1.000,<q>,0.000,0.000,0.000,0.000,0.000,"`；
  `tblLoadSeg.Type=1`、`ElementID` = 梁段的物理 `ID`、`idElement` = 该梁段 `idNew`、
  `idDef` = 荷载定义(`tblLoadSect`)的 `idNew`、`SectID` = 荷载定义的物理 ID、
  `strParas1="0.00,0.00,0.00,0.00,0.00,"`、`nPtCnt=0`、`idNode=0`，
  且 `tblLoadSeg.No` 等于所属**荷载定义自己的 `No`**（真实模型里 784 条全是 1）。
* 荷载来源：config 的 `主梁.均布荷载kN每m`（默认 0 = 不布，与旧行为一致；
  0 时完全不写这两张表）。楼面荷载走板（`slab_arrange` 的 dead/live），不在这里。

用法
----
    python make_ydb.py --scheme S3_十字梁 --out ../models/S3.ydb
    python make_ydb.py --all --outdir ../models
    python make_ydb.py --scheme S0_无次梁 --dump        # 只打印将写入的行
"""
import argparse
import os
import shutil
import sqlite3
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import yjk_api                                                     # noqa: E402
from spec import LAYOUTS, ORDER, grids, load                       # noqa: E402

import clr                                                         # noqa: E402
import System                                                      # noqa: E402
from System.Reflection.Emit import DynamicMethod, OpCodes          # noqa: E402

D, C = [None, None]
SCAFFOLD = os.path.join(HERE, "..", "refs", "scaffold.ydb")
NONE_ID = 4294967295                     # "无" 的哨兵（外键列）

GRADE_CODE = {25: 250, 30: 300, 35: 350, 40: 400, 45: 450, 50: 500, 55: 550, 60: 600}

# YJK 自己写出的默认标准层参数串（取自 YJK 新建空工程的 tblStdFlr.Para）。
# 用它当模板只改关心下标，长度/格式必然与 YJK 一致 —— 比让 BzcPara 拼串安全。
TEMPLATE_PARA = ("9999,100,300,15,300,300,300,3,3,50,100,200,3,0,9999,250,3,3,3,3,3,235,"
                 "15,3,235,235,235,235,60614,60614,60614,60614,60614,0,0,")
PARA_N = 26          # tblStdFlrPara 只存下标 0..25（空工程骨架即 26 行）


# --------------------------------------------------------------------- API 工具
def check_out_path(out_ydb):
    """输出路径的落盘前检查：给的是目录 / 父目录建不出来 → 可读报错（不是 Errno 栈）。"""
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


def _api():
    global D, C
    if D is None:
        D, C = yjk_api.bootstrap()
    return D, C


def _aslist(items):
    t = clr.GetClrType(type(items[0]))
    lt = System.Collections.Generic.List[t]()
    for it in items:
        lt.Add(it)
    return lt


def _byvalue_getter(t, name):
    """pythonnet 的反射调用不支持 ByRef 返回值，用 IL 包一个按值返回的方法。"""
    mi = t.GetMethod(name)
    rt = mi.ReturnType
    if not rt.IsByRef:
        return None
    mt = rt.GetElementType()
    dm = DynamicMethod("_bv_" + name, mt, [t], t, True)
    il = dm.GetILGenerator()
    il.Emit(OpCodes.Ldarg_0)
    il.Emit(OpCodes.Call, mi)
    il.Emit(OpCodes.Ldobj, mt)
    il.Emit(OpCodes.Ret)
    return dm


def _bzc_para(cfg, t_slab, grade_slab, grade_col, grade_beam):
    """标准层参数串（下标含义见技能 write_sections.py：2/4/5/6 = 板/柱/梁/墙 等级×10）。"""
    D, _ = _api()
    p = D.BzcPara()
    p.setVal(0, 9999)        # 梁保护层：按规范自动
    p.setVal(14, 9999)       # 柱保护层
    p.setVal(1, int(t_slab))                 # 板厚
    p.setVal(2, GRADE_CODE[int(str(grade_slab).lstrip("Cc"))])    # 板等级
    p.setVal(4, GRADE_CODE[int(str(grade_col).lstrip("Cc"))])     # 柱等级
    p.setVal(5, GRADE_CODE[int(str(grade_beam).lstrip("Cc"))])    # 梁等级
    p.setVal(6, GRADE_CODE[int(str(grade_beam).lstrip("Cc"))])    # 墙等级
    p.setVal(3, 15)
    p.setVal(22, 15)
    p.setVal(15, 250)        # 支撑
    for idx in (7, 8, 12, 23):
        p.setVal(idx, cfg["材料"]["主筋级别"])
    for idx in (16, 17, 18, 19, 20):
        p.setVal(idx, cfg["材料"]["箍筋级别"])
    p.setVal(21, 235)        # 钢号
    p.setVal(24, 5)
    p.setVal(25, 2)
    p.setVal(9, 50)
    p.setVal(10, 100)
    p.setVal(11, 200)
    return p


def _grade_code(g):
    return GRADE_CODE[int(str(g).lstrip("Cc"))]


def _first_attr(obj, *names):
    """取第一个存在的方法（跨版本方法名不同时用：7.1 `def_load` / 8.1 `Load_Def`）。"""
    for n in names:
        fn = getattr(obj, n, None)
        if fn is not None:
            return fn
    raise SystemExit("这些方法名一个都不存在：%s" % (names,))


def _try_call(fn, variants, what):
    """按候选实参依次调用，返回第一个成功的结果（老式接口不认多出来的 name 实参）。"""
    last = None
    for args in variants:
        try:
            return fn(*args)
        except TypeError as e:
            last = e
    raise SystemExit("%s 调用失败（试过 %d 种形参）：%s" % (what, len(variants), last))


def _load_def(df, kind, shapeval, name="LL"):
    """定义一种构件荷载（`tblLoadSect` 那一行）。跨版本：8.1 是 `Load_Def(k,v,name)`。

    ★ `def_load` 会**自己在末尾补一个逗号**：给 `"1.000,8.000,0.000,…,0.000"`（7 项、
      不带尾逗号）存下来正好是真实模型的 `"1.000,8.000,0.000,0.000,0.000,0.000,0.000,"`；
      若自己带上尾逗号会存成两个连续逗号（实测）。
    """
    return _try_call(_first_attr(df, "Load_Def", "def_load"),
                     [(kind, shapeval, name), (kind, shapeval)], "Load_Def")


def _load_arrange(df, members, loadsect, kind=1):
    """把荷载布置到构件上（`tblLoadSeg` 那些行）。

    ★ `kind`（第 3 个实参）会被原样写进 `Mdl_LoadSeg.Type`（实测：给 0 -> Type=0，
      给 1 -> Type=1）。实机验证过的可用模型里梁间荷载是 **Type=1**，所以默认给 1
      （`frame_build.py` 那里给的是 0，两处口径不同，别混用）。
    ★ 8.1 的 `load_arrange` 是**泛型**方法，pythonnet 推不出 T，必须显式给
      `方法[类型](实参)`；7.1 是普通方法 `load_arrange(List<Mdl_BeamSeg>, Mdl_LoadSect,
      Int32)`，用 `[]` 索引反而抛 TypeError。所以两种都试（与 frame_build.py 同一套路）。
    """
    try:
        df.load_arrange[type(members[0])](members, loadsect, kind)
        return
    except TypeError:
        pass
    df.load_arrange(members, loadsect, kind)


def _para_string(cfg, t_slab, g_slab, g_col, g_beam):
    """标准层参数串 —— 直接用官方 `BzcPara.GetValString()`。

    逐下标 setVal 777 反查可确认：`setVal(i)` 与 `Para` 的第 i 项
    **一一对应**（0/1/2/4/5/6/14/15/21/24/25 全部验证命中同下标）。
    所以 GetValString() 就是权威串。

    ⚠️ 不要拿 YJK-UI 默认串当模板去改写：官方 BzcPara 对下标 24/25 给 5/2，
    而 UI 默认串该两位是 235/235 —— 两者都自洽，混用会写出四不像。
    有效等级字段仍是下标 2/4/5/6（板/柱/梁/墙），见 write_sections.py 的说明。
    """
    return _bzc_para(cfg, t_slab, g_slab, g_col, g_beam).GetValString()


# ------------------------------------------------------------------ 建模（内存）
def build_model(scheme, cfg):
    """用 DataFunc 建出内存模型，返回 (model, meta)。

    meta 里带回落盘需要的辅助信息（各对象的 python 编号 -> .NET 对象）。
    """
    D, _ = _api()
    lay = LAYOUTS[scheme]
    g = cfg["几何"]
    xlv, ylv, zhux, zhuy = grids(cfg, lay)
    df = D.DataFunc()

    para = _para_string(cfg, lay["板厚"], cfg["板"]["等级"], cfg["柱"]["等级"],
                        cfg["主梁"]["等级"])
    std = df.StdFlr_Generate(
        int(g["层高"]), float(cfg["荷载"]["附加恒载"]), float(cfg["荷载"]["活载"]), para)
    # 主梁的**梁间线荷载**（隔墙/幕墙等）：楼面荷载走板，这部分 YJK 单独存
    # tblLoadSect/tblLoadSeg。默认 0 = 不布（与"加这条之前"的行为一致）。
    q_main = float(cfg["主梁"].get("均布荷载kN每m", 0) or 0)
    # ShapeVal 用**真实模型那一套 7 项写法**（`def_load` 会补尾逗号，这里不带）
    def_load = (_load_def(df, 12, "1.000,%.3f,0.000,0.000,0.000,0.000,0.000" % q_main)
                if q_main > 0 else None)
    meta = {"df": df, "std": std, "scheme": scheme, "lay": lay, "cfg": cfg, "para": para,
            "xlv": xlv, "ylv": ylv, "zhux": zhux, "zhuy": zhuy,
            "q_main": q_main, "def_load": def_load}

    # ---- 节点 ----
    node = {}
    for x in xlv:
        for y in ylv:
            node[(x, y)] = df.Joint_Generate(std.ID, x, y, 0)
    meta["node"] = node

    # ---- 轴线 + 网格（沿 X 的梁位于某 y；沿 Y 的梁位于某 x）----
    zhux_set, zhuy_set = set(zhux), set(zhuy)
    main, sec = [], []
    for yy in ylv:
        ax = df.Axis_Generate(std.ID, node[(xlv[0], yy)].ID, node[(xlv[-1], yy)].ID)
        for i in range(len(xlv) - 1):
            gr = df.Grid_Generate(std.ID, node[(xlv[i], yy)].ID,
                                  node[(xlv[i + 1], yy)].ID, ax.ID)
            (main if yy in zhuy_set else sec).append(gr)
    for xx in xlv:
        ax = df.Axis_Generate(std.ID, node[(xx, ylv[0])].ID, node[(xx, ylv[-1])].ID)
        for j in range(len(ylv) - 1):
            gr = df.Grid_Generate(std.ID, node[(xx, ylv[j])].ID,
                                  node[(xx, ylv[j + 1])].ID, ax.ID)
            (main if xx in zhux_set else sec).append(gr)

    # ---- 截面 + 布置 ----
    mb = cfg["主梁"]
    sec_main = df.BeamSect_Def(6, 1, "%d,%d" % (mb["宽"], mb["高"]))
    sb = lay["次梁"]
    main_beams = []
    if main:
        main_beams = df.beam_arrange(_aslist(main), sec_main, 0, 0, 0, 0.0)
    sec_sec = None
    if sb and sec:
        sec_sec = df.BeamSect_Def(6, 1, "%d,%d" % (sb["宽"], sb["高"]))
        df.beam_arrange(_aslist(sec), sec_sec, 0, 0, 0, 0.0)
    if def_load is not None:
        # ★ 必须在 beam_arrange 之后：load_arrange 吃的是**梁段对象**（不是网格）。
        #   只给主梁 —— 次梁上的线荷载本工程没有，要加就在此按需要再加一个定义。
        #   kind=1 与实机验证过的模型一致（写进 tblLoadSeg.Type）。
        _load_arrange(df, main_beams, def_load, 1)

    cs = cfg["柱"]
    sec_col = df.ColSect_Def(6, 1, "%d,%d" % (cs["边长"], cs["边长"]))
    df.column_arrange(_aslist([node[(x, y)] for x in zhux for y in zhuy]),
                      sec_col, 0, 0, 0.0, 0)

    # ---- 板 ----
    for i in range(len(xlv) - 1):
        for j in range(len(ylv) - 1):
            df.slab_arrange(D.SlabCreateInfo()
                            .SetCentroid((xlv[i] + xlv[i + 1]) // 2,
                                         (ylv[j] + ylv[j + 1]) // 2)
                            .SetThick(int(lay["板厚"])).SetStdFlr(std).SetCc(0)
                            .SetDeadLive(float(cfg["荷载"]["附加恒载"]),
                                         float(cfg["荷载"]["活载"])))
    df.Floor_Assemb(0, std, int(g["层数"]), int(g["层高"]))
    df.DbModel_Assign()

    gv = _byvalue_getter(clr.GetClrType(D.DataFunc), "GetDbModelData")
    model = gv.Invoke(None, [df]) if gv else df.GetDbModelData()
    meta["model"] = model
    return model, meta


# ------------------------------------------------------------------- 序列化
def _id_alloc():
    """按表分配主键 ID 与全局 idNew。"""
    st = {"id": {}, "new": 1000}
    BASE = {"tblStdFlr": 1001, "tblFloor": 2001, "tblJoint": 3000, "tblAxis": 6000,
            "tblGrid": 7000, "tblBeamSect": 1186, "tblBeamSeg": 9000,
            "tblColSect": 1050, "tblColSeg": 11000, "tblSlab": 13000,
            # 荷载两表也要有各自的 ID 段（ID 必须全模型唯一且 < 100000）
            "tblLoadSect": 15000, "tblLoadSeg": 16000}

    def nxt(tag):
        st["id"][tag] = st["id"].get(tag, 0) + 1
        return BASE[tag] + st["id"][tag] - 1

    def new():
        st["new"] += 1
        return st["new"]

    return nxt, new


def _f3(v):
    return "%.3f" % float(v)


def _ints(s):
    return [int(v) for v in str(s or "").split(",") if v.strip()]


def _floats(s, fmt="%.3f"):
    return [fmt % float(v) for v in str(s or "").split(",") if v.strip()]


def _wh(shapeval):
    """从 `'1,<b>,<h>,<Mat>,<ID>,'` 里取 (b, h)。

    注意 Mdl_BeamSect/Mdl_ColSect 的 `b`/`h` 字段恒为 0，尺寸只存在 ShapeVal 里。
    """
    v = [x for x in str(shapeval or "").split(",")]
    if len(v) < 3:
        raise SystemExit("ShapeVal 解析失败：%r" % shapeval)
    return int(round(float(v[1]))), int(round(float(v[2])))


class _Writer:
    """按表结构自动拼 INSERT：没给出的列按列类型填 0 / 0.0 / ''。

    列名与列序直接从数据库读，不会因为我们手抄漏列（例如 tblSlab 66 列里的
    HollowBoxPt* 4 列）而把文件写坏。

    ★★ 但"没给出的列填默认值"有个致命副作用：**列名写错时不会报错**。
      实机踩过：`tblLoadSect/tblLoadSeg` 的序号列叫 `No` 而非 `No_`（其余几何表都是
      `No_`），写成 `No_` 时真正的 `No` 留 0、多出来的键被默默丢掉，
      YJK 导入时把整批梁间荷载**静默丢弃**。所以 `add()` 现在先查一遍列名，
      有不存在的列就当场报错，并把这表的列名全列出来。
    """

    def __init__(self, con):
        self.con = con
        self._cols = {}

    def cols(self, tbl):
        if tbl not in self._cols:
            self._cols[tbl] = [(r[1], r[2]) for r in
                               self.con.execute("PRAGMA table_info([%s])" % tbl)]
        return self._cols[tbl]

    def clear(self, tbl):
        self.con.execute("DELETE FROM [%s]" % tbl)

    @staticmethod
    def _dflt(t):
        t = (t or "").upper()
        if "INT" in t:
            return 0
        if any(k in t for k in ("REAL", "FLOA", "DOUB", "NUM", "DEC")):
            return 0.0
        return ""

    def add(self, tbl, row):
        cols = self.cols(tbl)
        # ★ names 必须保持**列表**（顺序 = 表列顺序，与下面 values 一一对应）；
        #   只另外做一个集合用于查"未知列"，绝不能拿集合去拼 SQL（集合是无序的，
        #   列名顺序一乱，值就装错列 —— 症状会是莫名其妙的 UNIQUE 冲突）。
        names = [c for c, _ in cols]
        unknown = [k for k in row if k not in set(names)]
        if unknown:
            # 未知列 = 写错了列名（或该表本就没有这个字段）—— 绝不静默接受
            raise SystemExit("表 %s 里没有这些列：%s（该表列名：%s）"
                             % (tbl, unknown, names))
        sql = "INSERT INTO [%s] (%s) VALUES (%s)" % (
            tbl, ",".join("[%s]" % c for c in names), ",".join(["?"] * len(names)))
        self.con.execute(sql, [row.get(c, self._dflt(t)) for c, t in cols])


def _slab_cells(meta, grids):
    """由网格布局反推每块板的 4 条边。

    DataFunc 的 `Mdl_Slab` **不带** GridsID/VertexX/VertexY（全空），
    所以板块边界只能自己推：每跨一个网格就是一块矩形板，4 条边必定都有网格。
    返回 [(4 个角点坐标, 4 条边的 grid.ID), ...]，顺序与建模时 i(沿X)×j(沿Y) 一致。
    """
    node_by_xy = {k: int(v.ID) for k, v in meta["node"].items()}
    pair = {}
    for gr in grids:
        pair[frozenset((int(gr.Jt1ID), int(gr.Jt2ID)))] = int(gr.ID)
    xlv, ylv = meta["xlv"], meta["ylv"]
    cells = []
    for i in range(len(xlv) - 1):
        for j in range(len(ylv) - 1):
            c = [(xlv[i], ylv[j]), (xlv[i + 1], ylv[j]),
                 (xlv[i + 1], ylv[j + 1]), (xlv[i], ylv[j + 1])]
            ids = [node_by_xy[p] for p in c]
            gs = []
            for k in range(4):
                g = pair.get(frozenset((ids[k], ids[(k + 1) % 4])))
                if g is None:
                    raise SystemExit("板块 i=%d j=%d 第 %d 条边找不到网格" % (i, j, k))
                gs.append(g)
            cells.append((c, gs))
    return cells


def serialize(meta, out_ydb, scaffold=None, verbose=True):
    scaffold = scaffold or SCAFFOLD
    if not os.path.exists(scaffold):
        # ★ 可操作的报错（实测：以前只有一句"缺骨架 ydb"，没人知道去哪儿弄）。
        #   骨架 = YJK「新建空工程」后 save 出来的库（77 张表齐全，
        #   tblProjectPara / tblStdFlrPara 这些都不用我们造），它必须能被 SQLite 打开。
        raise SystemExit(
            "缺骨架 ydb：%s\n"
            "  骨架是什么：由「YJK 新建空工程 → save」得到的空模型（77 张表齐全，\n"
            "  tblStdFlrPara 由 Para 展开而来）—— 本脚本只往几何表里写数据，其余整表沿用骨架。\n"
            "  怎么放：把该文件放在 <本技能目录>/refs/scaffold.ydb\n"
            "  （本包已自带一份：refs/scaffold.ydb；若被删掉，按上面办法重新导一份）\n"
            "  或者：用 --scaffold <路径> 显式指定任何一份可用的空工程库\n"
            "  注意：骨架必须是 SQLite 文件（YJK 的 .ymd/.ydb 都是），且含 "
            "tblStdFlr/tblJoint/tblBeamSeg/tblSlab 等几何表。"
            % scaffold)
    # 先把旧产物删掉：本函数失败时（抛 SystemExit）**不能让上一次的文件留在原地**
    # ——调用方（run_all_yjk.py 只按"文件在不在"判定）会拿旧模型当本轮结果。
    # 这也是老版本的行为，只是老版本紧接着就把骨架拷到最终路径上，于是失败时留下的
    # 是一份"表齐全、几何表 0 行"的新半成品（见下面 ★ 那段）。现在只删不建。
    if os.path.exists(out_ydb):
        os.remove(out_ydb)
    # ★ 先落盘、后校验的顺序问题：骨架（约 987 KB、几何表全空）以前是**直接拷到
    #   out_ydb**的，此后逐表清空+INSERT，直到 commit() 才完事。中间任何 raise
    #   （板块数不符 / 找不到板对象 / 悬空荷载）都会在磁盘上留下一份
    #   「77 张表齐全、几何表行数为 0」的库 —— 只按"文件在不在"判就绪的下游
    #   （再叠加 impcheck 的"空集判通过"）会把它当成建好的模型。
    #   现在整段都写临时文件，**只有全部写完才 os.replace 到最终文件名**：
    #   失败时最终路径上不会出现半成品。
    tmp = out_ydb + ".part"
    if os.path.exists(tmp):
        os.remove(tmp)
    try:
        shutil.copyfile(scaffold, tmp)
    except OSError as e:
        raise SystemExit("写不出临时文件 %s（%s）\n"
                         "  常见原因：无写权限 / 目录不存在 / 磁盘满。" % (tmp, e))

    model = meta["model"]
    std = meta["std"]
    para = str(meta["para"])
    nxt, new = _id_alloc()
    con = sqlite3.connect(tmp)
    w = _Writer(con)

    # ---------------- 标准层 ----------------
    std_new = new()
    sid = nxt("tblStdFlr")
    w.clear("tblStdFlr")
    w.clear("tblStdFlrPara")
    w.add("tblStdFlr", dict(ID=sid, No_=1, Height=int(std.Height),
                            Dead=float(std.DeadLoad), Live=float(std.LiveLoad),
                            DPara="0,1,0", Para=para, Name="", idNew=std_new, StateFlag=0))
    parts = para.split(",")
    for k in range(PARA_N):                      # 与 YJK 一致：只存下标 0..25
        v = parts[k] if k < len(parts) else ""
        w.add("tblStdFlrPara", dict(StdFlrID=sid, Kind=k,
                                    ParaVal=int(float(v)) if v.strip() else 0))

    # ---------------- 节点 ----------------
    joints = list(model.m_Joint)
    grids = list(model.m_Grid)
    jid_new, jid_id = {}, {}
    for ob in joints:
        k = int(ob.ID)
        jid_new[k] = new()
        jid_id[k] = nxt("tblJoint")
    grid_new, grid_id_of = {}, {}
    for gr in grids:
        k = int(gr.ID)
        grid_new[k] = new()
        grid_id_of[k] = nxt("tblGrid")
    touch = {}                                   # 节点 -> 相邻网格 idNew
    for gr in grids:
        for j in (int(gr.Jt1ID), int(gr.Jt2ID)):
            touch.setdefault(j, []).append(grid_new[int(gr.ID)])

    w.clear("tblJoint")
    for i, ob in enumerate(joints):
        k = int(ob.ID)
        w.add("tblJoint", dict(ID=jid_id[k], No_=i + 1, StdFlrID=sid,
                               X=float(ob.X), Y=float(ob.Y), HDiff=int(ob.HDiff),
                               idNew=jid_new[k],
                               ListGJidNew="".join("%d," % v for v in touch.get(k, [])),
                               ListLoadidNew="", StateFlag=0))

    # ---------------- 轴线 / 网格 ----------------
    axes = list(model.m_Axis)
    ax_new, ax_id = {}, {}
    for ax in axes:
        k = int(ax.ID)
        ax_new[k] = new()
        ax_id[k] = nxt("tblAxis")
    w.clear("tblAxis")
    for i, ax in enumerate(axes):
        k = int(ax.ID)
        w.add("tblAxis", dict(ID=ax_id[k], No_=i + 1, StdFlrID=sid,
                              Jt1ID=jid_id[int(ax.Jt1ID)], Jt2ID=jid_id[int(ax.Jt2ID)],
                              Name=ax.Name or "", idNew=ax_new[k], idNewBzc=std_new,
                              idNode1=jid_new[int(ax.Jt1ID)],
                              idNode2=jid_new[int(ax.Jt2ID)], StateFlag=0))

    w.clear("tblGrid")
    for i, gr in enumerate(grids):
        k = int(gr.ID)
        w.add("tblGrid", dict(ID=grid_id_of[k], No_=i + 1, StdFlrID=sid,
                              Jt1ID=jid_id[int(gr.Jt1ID)], Jt2ID=jid_id[int(gr.Jt2ID)],
                              AxisID=ax_id[int(gr.AxisID)], idNew=grid_new[k],
                              idNewBzc=std_new, idNode1=jid_new[int(gr.Jt1ID)],
                              idNode2=jid_new[int(gr.Jt2ID)],
                              idAxis=ax_new[int(gr.AxisID)], idCen=NONE_ID, StateFlag=0))

    # ---------------- 截面 ----------------
    # ⚠️ DataFunc 的对象 ID 只在**它自己的表内**有意义（且跨表可能撞号），
    #    所以每张表的主键我们自己重新分配，凡是引用 tbl*.ID 的外键都要过一层映射表。
    w.clear("tblBeamSect")
    w.clear("tblColSect")
    sect_new, sect_id_of = {}, {}
    colsect_new, colsect_id_of = {}, {}
    for i, bs in enumerate(model.m_BeamSect):
        k = int(bs.ID)
        r, n = nxt("tblBeamSect"), new()
        sect_new[k], sect_id_of[k] = n, r
        b_, h_ = _wh(bs.ShapeVal)
        sv = "1,%d,%d,%d,%d," % (b_, h_, int(bs.Mat), r)
        w.add("tblBeamSect", dict(ID=r, No_=i + 1, Name="", Mat=int(bs.Mat),
                                  Kind=int(bs.Kind), ShapeVal=sv, ShapeVal1=sv,
                                  idNew=n, StateFlag=0, ShapeFVal="",
                                  b=float(b_), h=float(h_)))
    for i, cs_ in enumerate(model.m_ColSect):
        k = int(cs_.ID)
        r, n = nxt("tblColSect"), new()
        colsect_new[k], colsect_id_of[k] = n, r
        b_, h_ = _wh(cs_.ShapeVal)
        sv = "1,%d,%d,%d,%d," % (b_, h_, int(cs_.Mat), r)
        w.add("tblColSect", dict(ID=r, No_=i + 1, Name="", Mat=int(cs_.Mat),
                                 Kind=int(cs_.Kind), ShapeVal=sv, ShapeVal1="",
                                 idNew=n, StateFlag=0, ShapeFVal="",
                                 b=float(b_), h=float(h_)))

    # ---------------- 梁段 ----------------
    w.clear("tblBeamSeg")
    none4 = ",".join([str(NONE_ID)] * 4) + ","
    # 荷载表要用梁段的两个键：物理 ID（ElementID）与 idNew（idElement）——
    # 所以这里把映射存下来（DataFunc 的梁段 ID 只在它自己的表内有效）
    beamseg_id_of, beamseg_new = {}, {}
    for i, s in enumerate(model.m_BeamSeg):
        gid, sec = int(s.GridID), int(s.SectID)
        k = int(s.ID)
        beamseg_id_of[k], beamseg_new[k] = nxt("tblBeamSeg"), new()
        w.add("tblBeamSeg", dict(ID=beamseg_id_of[k], No_=i + 1, StdFlrID=sid,
                                 SectID=sect_id_of[sec], GridID=grid_id_of[gid],
                                 Ecc=int(s.Ecc),
                                 HDiff1=int(s.HDiff1), HDiff2=int(s.HDiff2),
                                 Rotation=float(s.Rotation),
                                 JYDef=s.JYDef or "0,0,0,0,",
                                 idNew=beamseg_new[k], idNewBzc=std_new,
                                 idGrid=grid_new[gid],
                                 idDef=sect_new[sec], defYidNew=none4,
                                 StateFlag=0, Ecc2=0, NoSlab=0))

    # ---------------- 柱段 ----------------
    w.clear("tblColSeg")
    for i, s in enumerate(model.m_ColSeg):
        jt, sec = int(s.JtID), int(s.SectID)
        w.add("tblColSeg", dict(ID=nxt("tblColSeg"), No_=i + 1, StdFlrID=sid,
                                SectID=colsect_id_of[sec], JtID=jid_id[jt],
                                EccX=int(s.EccX), EccY=int(s.EccY),
                                Rotation=float(s.Rotation), HDiffB=int(s.HDiffB),
                                ColcapId=0, Cut_Col="", Cut_Cap="", Cut_Slab="",
                                FootDefID=0, idNew=new(), idNewBzc=std_new,
                                idNewNode=jid_new[jt], idNewDef=colsect_new[sec],
                                idNewCap=NONE_ID, idNewFoot=NONE_ID,
                                idNewYZGJ=NONE_ID, idNewJG=NONE_ID,
                                StateFlag=0, ExtLength=0))

    # ---------------- 板 ----------------
    # 板块几何自推（Mdl_Slab 不带边界），用"形心"跟 DataFunc 的板对象对号，
    # 对不上就直接报错 —— 宁可失败也不要写出一份错的 ydb。
    w.clear("tblSlab")
    cells = _slab_cells(meta, grids)
    by_center = {}
    for s in model.m_Slab:
        by_center[(int(round(float(s.xc))), int(round(float(s.yc))))] = s
    if len(by_center) != len(cells):
        raise SystemExit("板块数不符：DataFunc %d 块 / 网格推出 %d 块"
                         % (len(by_center), len(cells)))
    for i, (corners, egrids) in enumerate(cells):
        cx = int(round((corners[0][0] + corners[1][0]) / 2.0))
        cy = int(round((corners[0][1] + corners[3][1]) / 2.0))
        s = by_center.get((cx, cy))
        if s is None:
            raise SystemExit("板块中心 (%d,%d) 在 DataFunc 里找不到对应板对象" % (cx, cy))
        w.add("tblSlab", dict(
            ID=nxt("tblSlab"), No_=i + 1, StdFlrID=sid,
            GridsID="".join("%d," % grid_id_of[g] for g in egrids),
            VertexX="".join("%.3f," % float(x) for x, _ in corners),
            VertexY="".join("%.3f," % float(y) for _, y in corners),
            VertexZ="".join(["0.000,"] * len(corners)),
            RoomIsHole=0, Thickness=int(s.Thickness), cc=int(s.cc or 0),
            dead=float(s.dead), live=float(s.live), TransWay=0, Ang1=0.0, Ang2=0.0,
            nEdge=0, EdgeSupport="", Shape=1, xc=float(s.xc), yc=float(s.yc),
            HollowSlabID=0, PrecastSlabID="0,0,0,", PrecastSlabRebarPara="",
            SingleSeamB=0, SingleSeamBMax=100, PairSeamB=300, PairSeamBMax=500,
            TwoWaySlab=0, PrecastSlabLastL=0.0, PrecastSlabRotate=0,
            PrecastSlabStyle_PK=0, PrecastSlabOffsetX=0, PrecastSlabOffsetY=0,
            PrecastSlabX="", PrecastSlabY="", PrecastSlabIndex=0, PrecastSlabCount=0,
            PrecastSlabArrangeNo="", PrecastSlabArrangeWidth="", precastSlabSpace="",
            PrecastSlabParaArr="", ProfilSlabDefId=0, ProfilSlabAng=0.0,
            ProfilSlabConcertW=25.0, ProfilSlabWorkLoad=1.5, ProfilSlabbhou=100.0,
            HollowBoxPtNum=None, HollowBoxPtX=None, HollowBoxPtY=None,
            HollowBoxPtZ=None,
            idNew=new(), idNewBzc=std_new,
            idGridStr="".join("%d," % grid_new[g] for g in egrids),
            idDefHollowSlab=NONE_ID,
            idPrecastSlabStr=",".join([str(NONE_ID)] * 3) + ",",
            idDefProfilSlab=NONE_ID,
            HollowPtOrig="0.00, 0.00, 0.00", HollowVX="0.00, 0.00, 0.00",
            HollowVY="0.00, 0.00, 0.00",
            HollowOhterData="0,0,0,0,0,0,-2,-2,0,0,4,",
            PcSlabStPt="0.00, 0.00, 0.00", PcSlabEdPt="0.00, 0.00, 0.00",
            idPreStressHollowSlab=0, idDefPreStressHollowSlabStr=NONE_ID,
            idPreStressHollowSlabAngle=0, StateFlag=0))

    # ---------------- 荷载：梁间线荷载（tblLoadSect / tblLoadSeg） ----------------
    # ★★ 列名陷阱：这两张表的序号列是 **`No`**，不是 `No_`（其余几何表都是 `No_`）。
    #    写成 `No_` 以前不会报错 —— 真正的 No 留 0、多出来的键被默默丢掉，
    #    YJK 导入时把整批荷载**静默丢弃**。现在 `_Writer.add` 会当场报错。
    # ★ 这两张表的内容**只能**来自 `load_arrange`（`model.m_LoadSect/m_LoadSeg`）；
    #   我们只负责把 DataFunc 算好的对象落盘 + 补 idNew 这类外键。
    w.clear("tblLoadSect")
    w.clear("tblLoadSeg")
    loadsects = list(getattr(model, "m_LoadSect", None) or [])
    loadsegs = list(getattr(model, "m_LoadSeg", None) or [])
    loadsect_new, loadsect_id_of, loadsect_no = {}, {}, {}
    for ls in loadsects:
        k = int(ls.ID)
        loadsect_new[k], loadsect_id_of[k] = new(), nxt("tblLoadSect")
        loadsect_no[k] = int(ls.No)
        w.add("tblLoadSect", dict(ID=loadsect_id_of[k], No=int(ls.No),
                                  ElementKind=int(ls.ElementKind),
                                  ShapeVal=str(ls.ShapeVal or ""),
                                  strName=str(ls.strName or ""),
                                  idNew=loadsect_new[k], StateFlag=0))
    for ls in loadsegs:
        el, sec = int(ls.ElementID), int(ls.SectID)
        if el not in beamseg_id_of:
            raise SystemExit("荷载 %s 指向的梁段 ElementID=%s 不在梁段表里（DataFunc 的 ID "
                             "映射缺失）—— 宁可失败也不要写出悬空荷载" % (int(ls.ID), el))
        if sec not in loadsect_id_of:
            raise SystemExit("荷载 %s 指向的荷载定义 SectID=%s 不在 tblLoadSect 里"
                             % (int(ls.ID), sec))
        w.add("tblLoadSeg", dict(
            # ★ 实测的真实模型：`tblLoadSeg.No` **等于所属荷载定义自己的 `No`**
            #   （784 条梁间荷载全是 1，与 ls.No 的 1..784 不同）—— 所以这里不用 ls.No。
            ID=nxt("tblLoadSeg"), No=loadsect_no[sec], SectID=loadsect_id_of[sec],
            Type=int(ls.Type), ElementID=beamseg_id_of[el],
            # DataFunc 把 strParas1 留成 None，而真实模型里是这串全零（表示无偏心/无附加
            # 参数）—— 为空时补上它，尽量与"能正常导入的模型"逐字段一致。
            strParas1=str(ls.strParas1 or "0.00,0.00,0.00,0.00,0.00,"),
            nPtCnt=int(ls.nPtCnt),
            strParasX=str(ls.strParasX or ""), strParasY=str(ls.strParasY or ""),
            strParasZ=str(ls.strParasZ or ""),
            # DataFunc 的对象里是 stdFlrID（小写 s），值是它内部的标准层 ID；
            # 本脚本只建一个标准层，所以直接用我们自己分配的 sid（免得内外 ID 混用）
            StdFlrID=sid, idNew=new(), idNewBzc=std_new,
            idElement=beamseg_new[el], idDef=loadsect_new[sec],
            StateFlag=0, idNode=0))

    # ---------------- 自然层 ----------------
    w.clear("tblFloor")
    for i, fl in enumerate(model.m_Floor):
        w.add("tblFloor", dict(ID=nxt("tblFloor"), No_=int(fl.No),
                               Name=getattr(fl, "Name", "") or "", StdFlrID=sid,
                               LevelB=float(fl.LevelB), Height=float(fl.Height),
                               idNew=new(), idNewBzc=std_new, StateFlag=None))
    con.commit()

    stat = {t: con.execute("SELECT count(*) FROM [%s]" % t).fetchone()[0]
            for t in ("tblStdFlr", "tblStdFlrPara", "tblFloor", "tblJoint", "tblAxis",
                      "tblGrid", "tblBeamSect", "tblBeamSeg", "tblColSect", "tblColSeg",
                      "tblSlab", "tblLoadSect", "tblLoadSeg")}
    con.close()

    # ★ 荷载守卫：**不看请求只看落盘行数**。判据是 config 里要求布（q>0），
    #   而 tblLoadSeg 一条都没有 —— 这时老版本把它归入"无"分支并打印
    #   「梁间线荷载：无（config … = 8.00）」（自相矛盾的同一行），既无断言也 rc=0。
    #   后果不是说错一句话：YJK 导入后整批梁上荷载消失、柱轴力偏小
    #   （本包已有实测记录，同类事故约 20%），而模型照样算得出来。
    #   ★ 位置：必须在 os.replace **之前** —— 否则守卫触发时最终路径上已经躺着
    #     一份"几何齐全但荷载为空"的成品库，只按"文件在不在"判定的下游会拿去用。
    q_req = float(meta.get("q_main") or 0)
    if q_req > 0 and not stat.get("tblLoadSeg"):
        raise SystemExit(
            "配置要求布梁间线荷载 q=%.2f kN/m，但**一条都没有落盘**"
            "（tblLoadSect=%d / tblLoadSeg=%d）：%s\n"
            "  后果：YJK 导入后整批梁上荷载消失，柱轴力偏小，而计算照样给出结果。\n"
            "  常见原因：load_arrange 没真正布上（或返回的 Type 不是 1，荷载被静默丢弃）。\n"
            "  处置：确认 Load_Def/load_arrange 的形参与本版本 YJKAPI 匹配；"
            "若本工程确实不要梁间荷载，就把 config 的 主梁.均布荷载kN每m 改回 0.0"
            "（那才是「不布」的明确表达）。"
            % (q_req, stat.get("tblLoadSect", 0), stat.get("tblLoadSeg", 0), out_ydb))
    os.replace(tmp, out_ydb)          # ★ 到这里才算"写出来了"，此前最终文件名不存在

    if verbose:
        print("  %-16s -> %s" % (meta["scheme"], os.path.basename(out_ydb)))
        print("     %s" % stat)
        q = float(meta.get("q_main") or 0)
        if stat.get("tblLoadSeg"):
            print("     梁间线荷载 q=%.2f kN/m：荷载定义 %d 条 / 荷载布置 %d 条"
                  % (q, stat["tblLoadSect"], stat["tblLoadSeg"]))
        else:
            print("     梁间线荷载：无（config 主梁.均布荷载kN每m = %.2f）" % q)
    return stat


FIELDS = {
    "m_Joint": ["ID", "No", "X", "Y", "HDiff", "StdFlrID"],
    "m_Axis": ["ID", "No", "Jt1ID", "Jt2ID", "Name", "StdFlrID"],
    "m_Grid": ["ID", "No", "Jt1ID", "Jt2ID", "AxisID", "StdFlrID"],
    "m_BeamSect": ["ID", "No", "Mat", "Kind", "b", "h", "ShapeVal"],
    "m_BeamSeg": ["ID", "No", "SectID", "GridID", "Ecc", "HDiff1", "HDiff2",
                  "Rotation", "JYDef", "StdFlrID"],
    "m_ColSect": ["ID", "No", "Mat", "Kind", "b", "h", "ShapeVal"],
    "m_ColSeg": ["ID", "No", "SectID", "JtID", "EccX", "EccY", "Rotation",
                 "HDiffB", "StdFlrID"],
    "m_Slab": ["ID", "No", "GridsID", "VertexX", "VertexY", "Thickness", "cc",
               "dead", "live", "xc", "yc", "StdFlrID"],
    "m_LoadSect": ["ID", "No", "ElementKind", "ShapeVal", "strName"],
    "m_LoadSeg": ["ID", "No", "SectID", "Type", "ElementID", "strParas1", "nPtCnt",
                  "strParasX", "strParasY", "strParasZ", "stdFlrID"],
    "m_Floor": ["ID", "No", "Name", "StdFlrID", "LevelB", "Height"],
}


def inspect_model(model, scheme):
    """打印各集合的对象数与首行字段值，确认内存对象真的带数据。"""
    print("【%s】" % scheme)
    for name, flds in FIELDS.items():
        col = getattr(model, name, None)
        if col is None:
            print("  %-12s <无此集合>" % name)
            continue
        items = list(col)
        print("  %-12s n=%d" % (name, len(items)))
        if not items:
            continue
        ob = items[0]
        got = []
        for f in flds:
            try:
                v = getattr(ob, f)
            except Exception as e:                       # noqa: BLE001
                v = "<ERR %s>" % type(e).__name__
            got.append("%s=%r" % (f, v))
        print("      [0] " + "  ".join(got))


def _utf8_console():
    """让输出在任何控制台编码下都不崩（GBK 下把不可编码字符替换掉）。

    为什么需要：本包会打印 ✅ ❌ ⚠ −(U+2212) ² ³ 等**非 cp936** 字符，
    默认 GBK 控制台下 `print` 会抛 UnicodeEncodeError 并**以退出码 1 中断**，
    于是一个其实已经成功的任务（比如文件已经落盘）会被上层判成失败；
    对 frame_build.py 那条链更糟 —— 崩在被调用的库的 print 上，模型根本没写出来。

    `errors="replace"` 让它在 UTF-8 控制台下原样输出、在 GBK 下退化成 `?`，都不崩。
    ★ 只在实际执行时调用（CLI 入口），**不在 import 时改 stdout** ——
      这些模块会被别的脚本 import 当库用，污染 import 方的 stdout 是不对的。
    ★ 本文件当前入口**不触发**（print 站点全是中文 + ASCII；文件里的 ⚠️ 只在注释里），
      加它是纵深防御：正式写盘的路径要在装了官方 DLL 的机器上跑，那里一样是 GBK 控制台。
    """
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass


def main():
    _utf8_console()          # ★ 必须在 argparse 之前：--help 也是写到 stdout 的
    ap = argparse.ArgumentParser()
    ap.add_argument("--scheme")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--out")
    ap.add_argument("--outdir", default=os.path.join(HERE, "..", "models"))
    ap.add_argument("--scaffold", default=None)
    ap.add_argument("--config", default=None)
    ap.add_argument("--dump", action="store_true", help="只打印对象数")
    ap.add_argument("--inspect", action="store_true", help="打印首行字段值")
    a = ap.parse_args()

    cfg = load(a.config)
    schemes = ORDER if a.all else [a.scheme]
    if not a.all and not a.scheme:
        raise SystemExit("给 --scheme 或 --all")
    os.makedirs(a.outdir, exist_ok=True)
    # ★ 输出路径先检查（**在建模型之前**）：给成目录 / 父目录建不出来时，
    #   用户应当看到"该给什么"，而不是要么空跑一遍建模、要么最后抛 Errno 栈。
    outs = {}
    for k in schemes:
        outs[k] = check_out_path(
            a.out if (a.out and not a.all)
            else os.path.join(a.outdir, k.split("_")[0] + ".ydb"))
    for k in schemes:
        model, meta = build_model(k, cfg)
        if a.inspect:
            inspect_model(model, k)
            continue
        if a.dump:
            print("【%s】节点%d 轴线%d 网格%d 梁截面%d 柱截面%d 梁段%d 柱段%d 板%d 层%d"
                  % (k, len(model.m_Joint), len(model.m_Axis), len(model.m_Grid),
                     len(model.m_BeamSect), len(model.m_ColSect), len(model.m_BeamSeg),
                     len(model.m_ColSeg), len(model.m_Slab), len(model.m_Floor)))
            continue
        out = outs[k]
        try:
            serialize(meta, out, a.scaffold)
        except BaseException:
            # 写库中途失败：最终文件名（out）不会出现半成品，但临时文件要清掉。
            try:
                os.remove(out + ".part")
            except OSError:
                pass
            raise
    return 0


if __name__ == "__main__":
    sys.exit(main())
