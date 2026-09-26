# -*- coding: utf-8 -*-
r"""按 (楼层 × 柱位分组) 生成框架 / 框架-核心筒 ydb：每层一个标准层，各层可有自己的柱截面与混凝土等级。

用法：
    python frame_build.py --config config.json --sections s.json --out model.ydb
    python frame_build.py --config c.json --sections s.json --out m.ydb --dll <YJKAPI.dll>
    python frame_build.py --config c.json --sections s.json --out m.ydb --scaffold 空工程.ymd

sections.json 形如（grade 省略按 C30）：
    {"1": {"grade": "C50", "中柱": 650, "边柱": 500, "角柱": 400}, "2": {...}, ...}

两条写盘路径
------------
* **默认（不给 `--scaffold`）**：走官方 `CsToYjk...CreateYDB()` —— 与以前完全一样。
  YJK 自己能写就让它写，口径最省心。
* **给了 `--scaffold <YJK 新建空工程保存出来的 .ymd>`**：走 `ydb_serialize.py`
  把模型**直接序列化进 SQLite**，这条路径**绝不调用** CreateYDB ——
  它不依赖 .NET 写盘程序集，产物逐字节可复现、每张表写了什么列都能直接审。

★ 为什么是"二选一"的硬约定，而不是"先试 CreateYDB、失败再回退"：
  这条路上失败有两种样子，**一种 Python 都拦不住** ——
    ① YJK 原生代码用**它自己的 MessageBox** 报错（模态框一弹进程永久挂住）；
    ② access violation 直接把进程干掉。
  两者都让"回退"那行代码永远轮不到执行，所以只能在**开工前**决定走哪条。
  运行 `--scaffold` 时绝不调用 CreateYDB，就是为了不给自己留这个不确定性。
  ★ 排查默认路径：`python <本技能>\scripts\driver.py createydb`
    （它在**子进程**里试一次 CreateYDB，崩/挂都只是子进程的事；见 SKILL.md「写盘的两条路」）。
  骨架从哪来：用 yjk-auto-drive 起一个 YJK，新建空工程后 `yjk_save`，
  把那个 .ymd 拿过来当 `--scaffold`（表结构和参数表都是 YJK 自己写的，我们只填几何）。

依赖：官方**建模接口**（`Hi_AddToAndReadYjk` / `DataFunc` / `BzcPara`），来自 YJKAPI.dll。
DLL 位置由 `driver.ensure_api()` 跨机器自动定位（见同目录 driver.py），
不需要把 DLL 放在本目录，也不写死任何路径。

注意：建标准层必须带 BzcPara 参数串（混凝土等级、保护层、钢筋级别），
      否则标准层参数全为 0 → 混凝土等级变 C0、保护层 0，设计结果会出现假的"轴压比 Uc=inf"。

配置里新增的可选键（都不给 = 与以前逐字一样的行为）
--------------------------------------------------
    "几何": {..., "首层层高": 4500}          # 不给则首层也用 "层高"
    "楼面等级": {"1-6": "C40", "*": "C30"}    # 板/梁等级；不给则跟柱等级
    "核心筒": {"x0":7200,"x1":21600,"y0":7200,"y1":21600,
               "墙厚":   {"1-10": 500, "11-18": 450, "*": 400},
               "墙等级": {"1-10": "C60", "*": "C40"}}
    "总信息": {"101": "10103", "302": "30202"}   # 改写 tblProjectPara（ID 含义见 ydb_serialize）
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import counts_by_group, load_config  # noqa: E402
import driver                                                  # noqa: E402
import ydb_serialize as ydb                                    # noqa: E402

_ap = argparse.ArgumentParser(add_help=False)
_ap.add_argument("--dll", default=None)
_known, _ = _ap.parse_known_args()

# ★ 不要写 `from YJKAPI import *` —— YJKAPI.dll 里没有叫 YJKAPI 的**命名空间**
#   （程序集名是 YJKAPI，根命名空间却是 DataFuncApplication / CsToYjk）。
#   统一由 driver.load_modeling_api() 处理：它还会挑对「两代」写 ydb 入口
#   （老式 Hi_AddProjectToYjk / 新式 Hi_AddToAndReadYjk），细节见 driver.py。
_API = driver.load_modeling_api(_known.dll, verbose=True)
DataFunc = _API["DataFunc"]                          # noqa: E402
BzcPara = _API["BzcPara"]                            # noqa: E402
SlabCreateInfo = _API["SlabCreateInfo"]              # noqa: E402
YdbWriter = _API["writer"]                           # noqa: E402

GRADE_CODE = {25: 250, 30: 300, 35: 350, 40: 400, 45: 450, 50: 500, 55: 550, 60: 600}
DEFAULT_WALL_THK = 200      # 核心筒没给 墙厚 时的兜底（会打印醒目提示，不静默）


def grade_code(grade, floor, what):
    """等级串/数字 -> YJK 的强度×10 编码（C30 -> 300）。

    ★ 认不出就**报错退出**，绝不退化成 C30：等级写错会让 `Uc` 直接按错的 fc 算，
      而 `wpj*.out` 不报错，白跑一轮计算还看不出来。
    """
    try:
        return GRADE_CODE[int(str(grade).lstrip("Cc"))]
    except (KeyError, ValueError):
        raise SystemExit("第 %d 层 %s 的混凝土等级 %r 无法识别（可用 %s）"
                         % (floor, what, grade, sorted(GRADE_CODE)))


def zone_value(spec, floor, what):
    """分区表取值：`{"1-10": 500, "11-18": 450}` / `{"*": "C30"}` / 也可以直接给标量。

    ★ 分区没覆盖到该层、又没有 `*` 兜底时**报错退出**：
      静默取个默认值会让墙厚/等级与设计意图不符，而模型照样算得出来。
    """
    if spec is None:
        return None
    if not isinstance(spec, dict):
        return spec
    for k, v in spec.items():
        if str(k) == "*":
            continue
        if "-" in str(k):
            a, b = str(k).split("-", 1)
            if int(a) <= floor <= int(b):
                return v
        elif int(k) == floor:
            return v
    if "*" in spec:
        return spec["*"]
    raise SystemExit("%s 的分区表没覆盖第 %d 层，也没有 '*' 兜底：%r" % (what, floor, spec))


def _netlist(seq, elem_type=None):
    """Python list -> .NET List<T>。

    ★ pythonnet 不会把 Python list 隐式转成 `List<Mdl_Grid>`，
      带重载的方法（如 DataFunc.beam_arrange）会以
      "'list' value cannot be converted to APIData.Mdl_Grid" 报错。
      这里按首个元素的真实类型建 List<T>。

    ★★ 空序列**必须**显式给 `elem_type` —— 这是实测修掉的一个缺陷（D1）：
      老版本对空序列直接 `return seq`，返回的是 **Python list**。于是
      「该层一根梁都没有」的模型（纯剪力墙、无梁楼层、被洞切掉全部梁段）走到
          beams = dataFunc.beam_arrange(_netlist(gl), defbeam)
      会抛
          TypeError: No method matches given arguments for DataFunc.beam_arrange:
                     (<class 'list'>, <class 'APIData.Mdl_BeamSect'>)
      报错点在 YJK 调用里，看起来像官方接口的问题，实际是这里退化了。
      空的**有类型** List 是可以构造的（`List[Mdl_Grid]()` 实测可用），
      所以现在要求调用方给出类型；**给不出就直接抛错**，不再静默退化成 Python list。
    """
    from System.Collections.Generic import List
    if not seq:
        if elem_type is None:
            raise ValueError(
                "_netlist() 收到空序列却没给 elem_type：空的有类型 List 必须显式指定元素类型，"
                "否则会退回 Python list 并在带重载的官方方法上抛 TypeError（历史缺陷 D1）")
        return List[elem_type]()
    L = List[type(seq[0])]()
    for x in seq:
        L.Add(x)
    return L


# ---- 跨版本适配 --------------------------------------------------------------
# 同一个逻辑操作，7.1 与 8.1 的建模接口**形参个数/方法名不一样**：
#   操作            7.1（老式）                       8.1（新式）
#   梁截面          BeamSect_Def(mat,kind,ShapeVal)   …,name      ← 少一个 name
#   柱截面          ColSect_Def(mat,kind,ShapeVal)    …,name
#   荷载定义        def_load(kind, shapeval)          Load_Def(kind, shapeval, name)  ← 名字也不同
#   标准层          StdFlr_Generate(h,dl,ll,para)     …,Name
#   楼层组装        Floor_Assemb(...)                 Floors_Assemb(...)             ← 名字不同
# 所以这里从「形参多」到「形参少」依次试，并允许若干候选方法名；
# 不用写死版本判断（版本号本身也未必可靠）。
def _first_attr(obj, *names):
    """取第一个存在的方法（跨版本方法名不同时用）。"""
    for n in names:
        fn = getattr(obj, n, None)
        if fn is not None:
            return fn
    raise SystemExit("这些方法名一个都不存在：%s" % (names,))


def _try_call(fn, variants, what):
    """按候选实参依次尝试调用，返回第一个成功的结果。

    老式接口不认多出来的 name 实参，会抛
    `TypeError: No method matches given arguments`（错误后再试短的即可）。
    """
    last = None
    for args in variants:
        try:
            return fn(*args)
        except TypeError as e:
            last = e
    raise SystemExit("%s 调用失败（试过 %d 种形参）：%s" % (what, len(variants), last))


def _get_model(dataFunc):
    """取出 DataFunc 里已组装好的 `Hi_DbModelData`。

    ★ 这是两代接口最后一个差异：
        新式(8.1)：`GetDbModelData()` 返回值语义，直接返回 Hi_DbModelData
        老式(7.1)：`GetDbModelData()` 返回 **`Hi_DbModelData&`**（引用），
                  而 .NET 的 `MethodInfo.Invoke` **不支持 ByRef 返回值**，
                  pythonnet 会抛：
                    System.NotSupportedException: 反射调用中不支持 ByRef 返回值。
                  → 改读同名实例字段 `model`（两代都有，老式下是 public 字段）。
    """
    try:
        return dataFunc.GetDbModelData()
    except Exception:                                           # noqa: BLE001
        pass
    import clr
    import System.Reflection as R
    ct = clr.GetClrType(DataFunc)
    for flags in (R.BindingFlags.Public, R.BindingFlags.NonPublic):
        f = ct.GetField("model", flags | R.BindingFlags.Instance)
        if f is not None:
            return f.GetValue(dataFunc)
    raise SystemExit("取不出模型：GetDbModelData() 是 ByRef 返回值（.NET 不支持），"
                     "又没有可读的 `model` 字段。请换一份 YJKAPI.dll。")


# ============================================================== 布置计划（纯几何）
def plan_layout(cfg):
    """算出这一层的布置计划：柱位 / 墙段 / 梁段 / 板块（全部按坐标推导，不写死柱号）。

    * 没有 `核心筒`：**满堂框架** —— 每个节点布柱、每条网格线布梁、每个网格单元布板。
      （与加核心筒之前逐项一致，兼容性靠这条守住。）
    * 有 `核心筒`（即"外围框架 + 中央核心筒"）：
        - 柱：**外圈所有节点**（两面靠边的那一圈网格交点）；核心筒范围里不布柱 ——
          那里是墙，柱墙重叠会被 YJK 判成重复构件；
        - 墙：核心筒四边，**按每跨一段**布墙（YJK 导入时会并成整片墙）；
        - 梁：所有网格线上的分段，**除了**与墙重合的段、以及严格在核心筒内部的段
          （筒内那两道网格线上下都没有构件，布了梁就成了"悬空梁"）；
        - 板：核心筒以外的每个网格单元一块板；**井道单元不布板**。
    """
    g = cfg["几何"]
    nx, ny = g["跨数X"], g["跨数Y"]
    sx, sy = g["跨度X"], g["跨度Y"]
    core = cfg.get("核心筒")
    xs = [i * sx for i in range(nx + 1)]
    ys = [j * sy for j in range(ny + 1)]

    # 全部网格段：先竖（沿 X 的每条线上逐跨）后横（沿 Y 的每条线上逐跨）——
    # 顺序与加核心筒之前的脚本**逐条一致**（竖段 x 外层、横段也是先定 x 线再逐行 y），
    # 这样不给 核心筒 时建出来的节点/轴线/网格/梁连 `No_` 编号顺序都完全相同。
    segs = []
    for x in xs:
        for j in range(ny):
            segs.append((x, ys[j], x, ys[j + 1]))
    for i in range(nx):
        for y in ys:
            segs.append((xs[i], y, xs[i + 1], y))

    cells = []
    for i in range(nx):
        for j in range(ny):
            xa, xb, ya, yb = xs[i], xs[i + 1], ys[j], ys[j + 1]
            corners = [(xa, ya), (xb, ya), (xb, yb), (xa, yb)]
            edges = [((xa, ya), (xb, ya)), ((xb, ya), (xb, yb)),
                     ((xb, yb), (xa, yb)), ((xa, yb), (xa, ya))]
            cells.append((corners, edges, (xa, xb, ya, yb)))

    if not core:
        plan = dict(xs=xs, ys=ys, nx=nx, ny=ny, sx=sx, sy=sy, core=None,
                    wall=[], beam=list(segs),
                    node=[(x, y) for x in xs for y in ys],
                    col=[(x, y) for x in xs for y in ys],
                    cells=[(c, e) for (c, e, _b) in cells], core_cells=[],
                    x_index={x: i for i, x in enumerate(xs)},
                    y_index={y: j for j, y in enumerate(ys)})
        return plan

    X0, X1, Y0, Y1 = int(core["x0"]), int(core["x1"]), int(core["y0"]), int(core["y1"])
    if X0 >= X1 or Y0 >= Y1:
        raise SystemExit("核心筒坐标不对：x0<x1、y0<y1 必须成立，现在 %r" % (core,))
    for v, axis in ((X0, "x"), (X1, "x"), (Y0, "y"), (Y1, "y")):
        if v not in (xs if axis == "x" else ys):
            raise SystemExit("★ 核心筒 %s=%d 不落在网格线上（%s 方向的网格线：%s）"
                             % (axis, v, axis, xs if axis == "x" else ys))

    def is_wall(x1, y1, x2, y2):
        if x1 == x2 and x1 in (X0, X1):
            return Y0 <= min(y1, y2) and max(y1, y2) <= Y1
        if y1 == y2 and y1 in (Y0, Y1):
            return X0 <= min(x1, x2) and max(x1, x2) <= X1
        return False

    def is_inner(x1, y1, x2, y2):
        """严格在核心筒**内部**的网格段（不是墙上，也不该有梁）。"""
        if x1 == x2:
            return X0 < x1 < X1 and Y0 <= min(y1, y2) and max(y1, y2) <= Y1
        if y1 == y2:
            return Y0 < y1 < Y1 and X0 <= min(x1, x2) and max(x1, x2) <= X1
        return False

    wall_plan = [s for s in segs if is_wall(*s)]
    beam_plan = [s for s in segs if not is_wall(*s) and not is_inner(*s)]
    # 节点：核心筒**内部**的节点不建（柱墙都没有，建了就是悬空节点）
    node_plan = [(x, y) for x in xs for y in ys
                 if not (X0 < x < X1 and Y0 < y < Y1)]
    # 柱位：外圈那一圈网格交点 —— 与核心筒（含边界）不相交的节点
    col_plan = [(x, y) for (x, y) in node_plan
                if not (X0 <= x <= X1 and Y0 <= y <= Y1)]

    core_cells = [(c, e) for (c, e, (xa, xb, ya, yb)) in cells
                  if X0 <= xa and xb <= X1 and Y0 <= ya and yb <= Y1]
    out_cells = [(c, e) for (c, e, (xa, xb, ya, yb)) in cells
                 if not (X0 <= xa and xb <= X1 and Y0 <= ya and yb <= Y1)]

    plan = dict(xs=xs, ys=ys, nx=nx, ny=ny, sx=sx, sy=sy, core=core,
                wall=wall_plan, beam=beam_plan, node=node_plan, col=col_plan,
                cells=out_cells, x_index={x: i for i, x in enumerate(xs)},
                y_index={y: j for j, y in enumerate(ys)}, core_cells=core_cells)
    if not wall_plan:
        raise SystemExit("★ 一个墙段都没有 —— 检查 核心筒 坐标是否落在网格线上")
    return plan


def plan_group(plan, x, y):
    """按**平面坐标**定柱位分组：两方向都在边缘=角柱、只一个方向在边缘=边柱、都在内部=中柱。

    ★ 判据与 `expand_plan.classify()` 同源（都看柱自己在网格线上的**序号**是否在内部区间），
      所以本脚本生成的模型与"读模型现算分组"的 `write_sections/verify_results` 口径一致。
      对满堂柱网，它与 `common.group_of_nc`（按柱号）给出完全相同的结果；
      但框筒的柱号不再覆盖满网格，按柱号判会分错组 —— 而**分错组不报错**，
      只是把截面写到错的柱子上。
    """
    xi = plan["x_index"][x]
    yi = plan["y_index"][y]
    inx = 0 < xi < len(plan["xs"]) - 1
    iny = 0 < yi < len(plan["ys"]) - 1
    if inx and iny:
        return "中柱"
    if inx or iny:
        return "边柱"
    return "角柱"


def pick_group(grp, sects):
    """取该柱用的截面分组：本组没给截面就**往内退一档**（角柱→边柱→中柱）。

    为什么允许退档：`截面.分组` 常只给两级（如 ["边柱","角柱"]），角柱实际并进边柱。
    找不到就往里退，与 `expand_plan.resolve()` 的口径一致；一个都退不到就**报错退出** ——
    静默挑一个会把截面写到错的柱子上，而且不报错。
    """
    if grp in sects:
        return grp
    order = ["中柱", "边柱", "角柱"]                 # 由内到外
    if grp in order:
        for g in reversed(order[:order.index(grp) + 1]):
            if g in sects:
                return g
    raise SystemExit("柱位分组 %r 在 截面.分组 %s 里没有对应截面，也没法往内退档；"
                     "请把 %r 加进 截面.分组。" % (grp, sorted(sects), grp))


# ============================================================== 建模（内存）
def build_in_memory(cfg, sections, verbose=True):
    """在内存里把模型建出来（不写盘），返回 meta（plan / model / stds / cfg）。"""
    plan = plan_layout(cfg)
    g = cfg["几何"]
    nstory = g["层数"]
    h_first = g.get("首层层高", g["层高"])
    h_std = g["层高"]
    beam, slab = cfg["梁"], cfg["板"]
    groups = cfg["截面"]["分组"]
    has_wall = bool(plan["wall"])
    if has_wall and not (cfg.get("核心筒") or {}).get("墙厚"):
        print("   !! 核心筒 没给 墙厚，本次按 %d mm 处理（请在配置里写清楚）" % DEFAULT_WALL_THK)

    dataFunc = DataFunc()
    _bshape = "%d,%d" % (beam["宽"], beam["高"])
    defbeam = _try_call(dataFunc.BeamSect_Def,
                        [(6, 1, _bshape, "KL"), (6, 1, _bshape)], "BeamSect_Def")
    # ★★ 梁上均布荷载：**q <= 0 时不建荷载定义、也不布置荷载**（实测缺陷 D2）。
    #   老版本无条件建一个 `Load_Def(12, "1.00,0.00")` 并给每根梁都挂一条 0 值线荷载。
    #   实测后果不是「多几条无用荷载」这么轻 —— **YJK 的 `yjk_importydb` 会把值为 0 的
    #   荷载整批丢弃**：源 ydb `tblLoadSeg = 48`，导入后 `.ymd` 里 `tblLoadSeg = 0`，
    #   连 `tblLoadSect` 也一起归零。于是本包的导入闸门（`impcheck` 把 tblLoadSeg 列为
    #   必判表）判定「必判表不一致」并**主动中止整轮**（`yjk_auto.py` 退出码 2）：
    #   也就是说「不加梁上荷载」这种很普通的配置，模型**根本进不了 YJK**。
    #   注意这与 Type=0 是**同一族**机制（无效荷载被丢弃），只是触发条件不同。
    _q = beam["均布荷载kN每m"]
    if _q and float(_q) > 0:
        _lshape = "1.00,%.2f" % _q
        beamload = _try_call(_first_attr(dataFunc, "Load_Def", "def_load"),
                             [(12, _lshape, "LL"), (12, _lshape)], "Load_Def")
    else:
        beamload = None
        print("   !! 梁上均布荷载 = %g ≤ 0：本次**不建荷载定义、也不布置梁上荷载**。" % _q)
        print("      （理由：YJK 会把值为 0 的荷载整批丢弃，源 ydb 里偏偏留下了 0 值荷载行，")
        print("        导入后必判表 tblLoadSeg 会对不上，导入闸门会中止整轮 —— 实测缺陷 D2）")

    if verbose:
        print("布置计划：节点 %d（柱位 %d）｜墙段 %d｜梁段 %d｜板块 %d"
              % (len(plan["node"]), len(plan["col"]), len(plan["wall"]),
                 len(plan["beam"]), len(plan["cells"])))

    stds = []            # [(floor, std_obj, para, height, col_sect_of_grp, wall_thk)]
    h_start = 0
    for f in range(1, nstory + 1):
        s = sections[str(f)]
        # 柱等级：优化对象；板/梁/墙等级分别可配（不给就跟柱等级 —— 与旧行为一致）
        gc = grade_code(s.get("grade", cfg["混凝土"]["候选等级"][0]), f, "柱")
        g_slab = zone_value(cfg.get("楼面等级"), f, "楼面等级")
        gc_slab = grade_code(g_slab, f, "楼面等级") if g_slab is not None else gc
        gc_wall = gc
        t_wall = None
        if has_wall:
            g_wall = zone_value((cfg.get("核心筒") or {}).get("墙等级"), f, "核心筒.墙等级")
            gc_wall = grade_code(g_wall, f, "核心筒.墙等级") if g_wall is not None else gc_slab
            tw = zone_value((cfg.get("核心筒") or {}).get("墙厚"), f, "核心筒.墙厚")
            t_wall = DEFAULT_WALL_THK if tw is None else int(tw)
        h = h_first if f == 1 else h_std

        para = BzcPara()
        para.setVal(0, 9999)        # 梁钢筋保护层：按规范自动
        para.setVal(14, 9999)       # 柱钢筋保护层：按规范自动
        para.setVal(1, slab["厚"])
        para.setVal(3, 15)
        para.setVal(22, 15)
        para.setVal(2, gc_slab)     # 板
        para.setVal(4, gc)          # 柱  ← 优化对象
        para.setVal(5, gc_slab)     # 梁
        para.setVal(6, gc_wall)     # 墙
        para.setVal(15, 250)        # 支撑
        for idx in (7, 8, 12, 23, 16, 17, 18, 19, 20):
            para.setVal(idx, cfg["材料"].get("主筋级别", 3) if idx in (7, 8, 12, 23)
                        else cfg["材料"].get("箍筋级别", 3))
        para.setVal(21, 235)
        para.setVal(24, 5)
        para.setVal(25, 2)
        para.setVal(9, 50)
        para.setVal(10, 100)
        para.setVal(11, 200)

        _pstr = para.GetValString()
        std = _try_call(dataFunc.StdFlr_Generate,
                        [(h, 5.0, 2.0, _pstr, "F%d" % f), (h, 5.0, 2.0, _pstr)],
                        "StdFlr_Generate")

        sects = {}
        for grp in groups:
            side = int(s[grp])
            _sshape = "%d,%d" % (side, side)
            sects[grp] = _try_call(dataFunc.ColSect_Def,
                                   [(6, 1, _sshape, "%sF%d" % (grp, f)),
                                    (6, 1, _sshape)], "ColSect_Def")

        wsect = None
        if has_wall:
            # ★ 墙截面按**每层**给（厚度逐层变），厚度取配置而不是内存对象 ——
            #   内存对象的墙厚字段不可靠，写进去会变成 0 厚墙。
            wsect = dataFunc.WallSect_Def(6, 1, int(t_wall))
            if wsect is None:
                raise SystemExit("第 %d 层 WallSect_Def(6,1,%d) 返回空" % (f, t_wall))

        node = {p_: dataFunc.Joint_Generate(std.ID, p_[0], p_[1])
                for p_ in plan["node"]}
        grid = {}

        def mk(a, b):
            ax = dataFunc.Axis_Generate(std.ID, node[a].ID, node[b].ID)
            grid[(a, b)] = dataFunc.Grid_Generate(std.ID, node[a].ID, node[b].ID, ax.ID)

        for seg in plan["wall"] + plan["beam"]:
            mk((seg[0], seg[1]), (seg[2], seg[3]))

        # 逐节点按分组布柱（分组按坐标判，见 plan_group）
        for (x, y) in plan["col"]:
            grp = pick_group(plan_group(plan, x, y), sects)
            dataFunc.column_arrange(node[(x, y)], sects[grp])

        nwall = 0
        for (xa, ya, xb, yb) in plan["wall"]:
            # wall_arrange(grid, wallSect, Ecc, HDiff1, HDiff2, HDiffB, sloping,
            #              EccDown, offset1, offset2) —— 后 8 个形参默认 0，这里显式写出来
            r = dataFunc.wall_arrange(grid[((xa, ya), (xb, yb))], wsect,
                                      0, 0, 0, 0, 0, 0, 0, 0)
            if r is not None:
                nwall += 1
        if nwall != len(plan["wall"]):
            raise SystemExit("第 %d 层墙只建了 %d/%d 段" % (f, nwall, len(plan["wall"])))

        gl = [grid[((s_[0], s_[1]), (s_[2], s_[3]))] for s_ in plan["beam"]]
        # ★★ 该层一根梁都没有时**不要调 beam_arrange**（实测缺陷 D1）。
        #   `_netlist([])` 拿不到元素类型，而 `beam_arrange` 只接受
        #   `List<Mdl_Grid>` 或单个 `Mdl_Grid`，Python list 绑不上 →
        #   `TypeError: No method matches given arguments`。
        #   典型触发：核心筒放大到整个平面（纯剪力墙形式）、被洞切光梁段的楼层。
        #   没有梁就没有东西可布置，直接跳过比"传一个空 List 试试"更安全
        #   （YJK 对空 List 的行为没有实测依据）。
        beams = dataFunc.beam_arrange(_netlist(gl), defbeam) if gl else None
        # ★ load_arrange 是**泛型方法**：
        #     Void load_arrange[T](List<T> member_list, Mdl_LoadSect loadsect, Int32 type)
        #     Void load_arrange[T](T member,        Mdl_LoadSect loadsect, Int32 type)
        #   pythonnet 推不出 T，必须显式给出：方法[类型](实参)；
        #   ★ 而且必须**直接用 beam_arrange 返回的那个 .NET List**（再包一层会被当成 T=List<...>）
        #
        # ★★ 第 3 个实参（type）**必须是 1，不能是 0** —— 这是实测出来的硬约束：
        #   该实参会被原样写进 `tblLoadSeg.Type`。而 `yjk_importydb` 会把
        #   **`Type=0` 的荷载整批静默丢弃**（不报错、不提示，源 ydb 里 240 条、
        #   导入后 .ymd 里 0 条），结果模型照样算得出来，但柱轴力少掉梁上隔墙线荷载
        #   那一整块（本包量级约 20%）→ 柱截面会选偏小。
        #   对照实验（同一份模型、同一 schema，只改这一个字段）：
        #       Type=0 → 导入后 tblLoadSeg = 0    （丢弃）
        #       Type=1 → 导入后 tblLoadSeg = 240  （存活）
        #   真实工程的模型里也都是 1。type=0 更像是"未赋值"，被导入当成无效数据清掉。
        #   ★ 另外 `beamload is None`（q<=0 的情况）时也**不调**：见上面 D2 的说明。
        if beams is not None and len(beams) and beamload is not None:
            dataFunc.load_arrange[type(beams[0])](beams, beamload, 1)

        for (corners, _e) in plan["cells"]:
            info = (SlabCreateInfo()
                    .SetCentroid(cell_center(corners, 0), cell_center(corners, 1))
                    .SetThick(slab["厚"]).SetStdFlr(std).SetCc(0)
                    .SetDeadLive(slab["附加恒载"], slab["活载"]))
            dataFunc.slab_arrange(info)

        _try_call(_first_attr(dataFunc, "Floors_Assemb", "Floor_Assemb"),
                  [(h_start, std, 1, h)], "Floors_Assemb")
        h_start += h

        stds.append(dict(floor=f, std=std, para=_pstr, height=h, col_sect=sects,
                         wall_thk=t_wall, wsec=wsect, gc_col=gc, gc_slab=gc_slab,
                         gc_wall=gc_wall, groups=list(groups)))
        if verbose:
            extra = " 墙C%-2d t=%d" % (gc_wall // 10, t_wall) if has_wall else ""
            print("第 %2d 层：C%-2d  h=%-5d%s  " % (f, gc // 10, h, extra)
                  + " / ".join("%s %d" % (grp, s[grp]) for grp in groups))

    dataFunc.DbModel_Assign()
    model = _get_model(dataFunc)

    # ★ 构件数必须等于「布置计划 × 层数」。对不上说明 API 静默丢了构件
    #   （最典型的是柱/墙重叠：YJK 判重复构件后丢弃，不报错，只在算的时候露馅）。
    exp = (len(plan["node"]) * nstory, len(plan["col"]) * nstory,
           len(plan["beam"]) * nstory, len(plan["wall"]) * nstory,
           len(plan["cells"]) * nstory)
    got = (len(model.m_Joint), len(model.m_ColSeg), len(model.m_BeamSeg),
           len(model.m_WallSeg), len(model.m_Slab))
    summary = ("标准层 %d | 自然层 %d | 节点 %d | 柱段 %d | 梁段 %d"
               % (len(model.m_StdFlr), len(model.m_Floor), len(model.m_Joint),
                  len(model.m_ColSeg), len(model.m_BeamSeg)))
    if len(model.m_WallSeg):
        summary += " | 墙段 %d" % len(model.m_WallSeg)
    summary += " | 板 %d" % len(model.m_Slab)
    print(summary)
    if exp != got:
        raise SystemExit("★ 构件数对不上：期望 节点/柱/梁/墙/板 = %s，实际 = %s\n"
                         "  （期望 = 布置计划 × %d 层）" % (exp, got, nstory))

    # ★★ 荷载条数校验：几何全对、荷载一条没有，在上面的 exp/got 里是**合法**的成功结果
    #    —— 那五个数只比几何，不含荷载。
    #    `load_arrange` 的实参是**泛型方法**且返回 Void（见上面 476-491 行的说明）：
    #    它不抛异常时本脚本无从察觉"到底布上了没有"。而它一旦静默没布上，
    #    写出的库几何完整、`tblLoadSeg` 为 0，`yjk_importydb` 回 OK、计算也跑得完，
    #    但柱轴力少了梁上填充墙线荷载那一整块（本包量级约 20%）→ 柱截面选偏小。
    check_beam_loads(model, beamload, _q)
    return dict(plan=plan, model=model, stds=stds, cfg=cfg, sections=sections)


def _std_of(obj):
    """内存模型对象的「所属标准层」。

    ★ 属性名在 .NET 包装器里**不统一**（实机踩过，别再想当然写一个）：
        `Mdl_LoadSeg`  → `stdFlrID`（**小写 s**）
        Joint / Axis / Grid / BeamSeg / ColSeg / WallSeg / Slab → `StdFlrID`
      依据不是猜的：本包 `ydb_serialize.write_load_seg` 一直写的就是
      `int(o.stdFlrID)`（见那里的注释与 `tblLoadSeg` 的字段形状），
      而 `write_beam_seg` 用的是 `s.StdFlrID`。两个类的包装器命名不一致。
      所以这里**两种拼写都认**，顺序为先大写（多数类）后小写。

    ★ 两种都取不到时**显式失败**并点名对象类型：绝不能让它以 AttributeError 冒出去 ——
      那样 dll/包装器名一变，整条建模链会在最后一刻崩掉，而报告里看不出是"荷载校验
      取不到属性"还是"模型真的建坏了"。
    """
    for name in ("StdFlrID", "stdFlrID"):
        try:
            v = getattr(obj, name)
        except AttributeError:
            continue
        if v is not None:
            return int(v)
    raise SystemExit(
        "!! 从内存模型对象 %s 上取不到「所属标准层」—— 试过 StdFlrID 与 stdFlrID 两种\n"
        "   拼写都没有。要么这份 YJKAPI.dll 的包装器改了属性名，要么该对象不是构件段。\n"
        "   本项（梁上荷载是否真的布上了）是几何校验**查不到**的失败形态，\n"
        "   所以这里不跳过、不静默，请核对包装器属性名后再跑。"
        % type(obj).__name__)


def check_beam_loads(model, beamload, q):
    """按**标准层**核对：有梁段的层里，必须至少有一条梁上荷载。

    ★ 为什么必须单独查一次：`exp/got`（节点/柱/梁/墙/板）只比几何，不含荷载，
      于是"几何全对、荷载一条没有"在这个脚本里是**合法**的成功结果。
      而 `load_arrange` 是泛型方法、返回 Void，它静默没布上时脚本无从察觉 ——
      写出的库几何完整、`tblLoadSeg` = 0，`yjk_importydb` 回 OK、计算也跑得完，
      但柱轴力少了梁上填充墙线荷载那一整块（本包量级约 20%）→ 柱截面选偏小。
      `beamload is None`（配置里 q≤0，见上面 D2 的说明）时不检查：那本来就不布置荷载。

    ★ 取「所属标准层」用 `_std_of()`：`Mdl_LoadSeg` 的属性名是 `stdFlrID`（小写），
      与 `Mdl_BeamSeg.StdFlrID` 不同；写死一个名字会让**带荷载的建模整体失败**。
    """
    if beamload is None:
        return
    fl_beam = {_std_of(b) for b in model.m_BeamSeg}
    fl_load = {_std_of(l) for l in model.m_LoadSeg}
    lost = sorted(fl_beam - fl_load)
    if not lost:
        return
    raise SystemExit(
        "★ 有梁的层里这些标准层**一条梁上荷载都没有**：%s\n"
        "  内存模型：梁段 %d 条、荷载段 %d 条；配置 梁.均布荷载kN每m = %s。\n"
        "  几何校验（节点/柱/梁/墙/板）**不含荷载**，所以"
        "「几何全对、荷载全丢」本来是一个静默的成功结果：\n"
        "  导入回 OK、计算跑得完，但柱轴力偏小约 20%%，柱截面会选偏小。\n"
        "  处置：① 确认这些层确实有梁段（gl 非空 → beams 非 None）；\n"
        "        ② 确认 load_arrange 收到的是 `beam_arrange` 返回的那个 .NET List "
        "（再包一层会被当成 T=List<...>）；\n"
        "        ③ 第 3 个实参必须是 1（Type=0 的荷载会被导入整批丢弃）。"
        % (lost[:10], len(model.m_BeamSeg), len(model.m_LoadSeg), q))


def cell_center(corners, which):
    """板块中心坐标：`which=0` 取 x 中点、`which=1` 取 y 中点。

    （与旧版的 `xs[i] + 跨度X//2` 等价：`(xa+xb)//2 == xa + (xb-xa)//2`，
      所以板块中心逐点不变，板的定位不受影响。）
    """
    if which == 0:
        return (corners[0][0] + corners[1][0]) // 2
    return (corners[0][1] + corners[3][1]) // 2


# ============================================================== 写盘
def write_out(meta, out_ydb, scaffold=None, project_para=None, verbose=True):
    """落盘。**给了 scaffold 就一定走序列化，绝不调用 CreateYDB**（见模块 docstring）。"""
    model = meta["model"]
    if scaffold:
        print("写盘：序列化进骨架 %s（不调用 CreateYDB）" % scaffold)
        stat = ydb.serialize(meta, out_ydb, scaffold, verbose=verbose)
        print("写出 %s  %d bytes" % (out_ydb, os.path.getsize(out_ydb)))
        for k in sorted(stat):
            print("   %-16s %d" % (k, stat[k]))
    else:
        if os.path.exists(out_ydb):
            os.remove(out_ydb)
        # ★ 这里**没有**"失败就自动改走序列化"的回退 —— 见模块 docstring：
        #   这条路上的两种失败（YJK 自己的 MessageBox / access violation）都拦不住，
        #   回退代码根本轮不到执行。所以下面这个 try 只负责把**可捕获**的失败
        #   （托管异常，例如 FileNotFoundException: ClrYJKAPI）说成人话，行为与改动前一致：
        #   出错就非零退出，绝不写出半个库。
        try:
            my = YdbWriter(model)          # 老式/新式入口都是 .ctor(Hi_DbModelData)
            ok = my.CreateYDB(os.path.dirname(os.path.abspath(out_ydb)),
                              os.path.basename(out_ydb))
        except Exception as e:                                  # noqa: BLE001
            raise SystemExit(
                "CreateYDB 抛了可捕获的异常：%s\n"
                "→ 先跑一次探测看官方写盘入口在本机到底行不行：\n"
                "     python <本技能>\\scripts\\driver.py createydb\n"
                "  若探测不是 OK，可显式改用序列化路径（不依赖 .NET 写盘程序集）：\n"
                "     frame_build.py ... --scaffold <YJK 新建空工程 save 出来的 .ymd>" % e)
        if not os.path.exists(out_ydb) or os.path.getsize(out_ydb) == 0:
            raise SystemExit(
                "CreateYDB 返回 %s，但 %s 没生成/为空 —— 建模失败。\n"
                "→ 先跑 `driver.py createydb` 探测；也可显式改用序列化路径："
                "加 `--scaffold <YJK 空工程保存出来的 .ymd>`。" % (ok, out_ydb))
        print("CreateYDB -> %s  %s (%d bytes)" % (ok, out_ydb, os.path.getsize(out_ydb)))

    if project_para:
        # 骨架是空工程，结构体系默认"框架结构"：框筒模型不改这一项，
        # 轴压比限值/抗震等级就按框架结构取，而结果文件不会报错。
        ydb.apply_project_para(out_ydb, project_para, verbose=verbose)
    return 0


def build(cfg, sections, out_ydb, scaffold=None, project_para=None, quiet=False):
    """建模型并写盘。新增的都是关键字实参，老调用方式含义不变。"""
    meta = build_in_memory(cfg, sections, verbose=not quiet)
    return write_out(meta, out_ydb, scaffold=scaffold,
                     project_para=project_para or cfg.get("总信息"),
                     verbose=not quiet)


def _utf8_console():
    """让输出在任何控制台编码下都不崩（GBK 下把不可编码字符替换掉）。

    为什么**必须**在本脚本里也加一处 —— 实测（修复缺陷 X8 时发现）：

        默认 GBK 控制台（不设 PYTHONIOENCODING）下跑
            frame_build.py --config ... --out model.ydb --scaffold <骨架>
        会崩在**被它调用的库**里，而不是它自己：
            File "ydb_serialize.py", line 808, in check_numbering
                print("No_ 自检：...✅")
            UnicodeEncodeError: 'gbk' codec can't encode character '\u2705'
        结果是 **exit=1 且模型根本没写出来**（不是"文件已生成却报错"，是白跑）。

    ★ 关键点：`ydb_serialize.py` 里的打印是在**调用方进程**的 stdout 上执行的，
      所以它自己 `__main__` 里的兜底**保护不到**本脚本 —— 每个 CLI 入口都要自己兜。

    只在实际执行时调用（`main()` 开头），不在 import 时改 stdout：本模块会被
    `colopt.py` 等 import 当库用，污染别人的 stdout 是不对的。
    """
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass


def main():
    _utf8_console()          # ★ 必须在 argparse 之前：--help 也是写到 stdout 的
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--sections", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--dll", default=None, help="官方 YJKAPI.dll（默认自动定位）")
    ap.add_argument("--scaffold", default=None,
                    help="显式改用序列化写盘：给一个 YJK 新建空工程 save 出来的 .ymd/.ydb，"
                         "模型直接写进这个骨架库，**完全不调用 CreateYDB**"
                         "（默认仍是 CreateYDB；先用 driver.py createydb 探测它行不行）")
    a = ap.parse_args()
    cfg = load_config(a.config)
    # 截面清单是人会手工改的输入（也是 section_opt 的产物）：utf-8-sig 两者都认
    sections = json.load(open(a.sections, encoding="utf-8-sig"))
    if "sections" in sections:
        sections = sections["sections"]
    missing = [f for f in range(1, cfg["几何"]["层数"] + 1) if str(f) not in sections]
    if missing:
        raise SystemExit("截面配置缺少第 %s 层" % missing)
    if "核心筒" in cfg:
        print("核心筒：%s" % cfg["核心筒"])
    else:
        print("每层柱数：%s" % counts_by_group(cfg))
    return build(cfg, sections, a.out, scaffold=a.scaffold)


if __name__ == "__main__":
    sys.exit(main())
