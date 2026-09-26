# -*- coding: utf-8 -*-
r"""把**内存模型**（官方建模接口的 `Hi_DbModelData`）按表结构序列化进 YJK 模型库(.ydb)。

为什么要有这个模块
==================
`frame_build.py` 的**默认**写盘路径是官方入口
`CsToYjk.Hi_AddProjectToYjk.CreateYDB(dir, name)` —— 它能用就一定用它（那是 YJK 自己写的库）。
本模块是**显式可选**的第二条路：给了 `--scaffold <空工程 .ymd>` 就把内存模型直接写进
骨架库的 SQLite 表里，**完全不依赖 .NET 写盘程序集**。

它什么时候有用（都不是"CreateYDB 坏了"）：
  * 要**可复现、可审查**的落盘：本模块产物逐字节确定（同一输入两次跑 SHA256 相同），
    每张表写了哪些列都能直接从代码/数据里核对，便于做回归和 diff。
    ★ 反过来说，官方 `CreateYDB` 的产物**并不是逐字节可复现**的：实测同一配置连跑三次，
      `tblSlab` 的 `SingleSeamB / PairSeamB / PairSeamBMax` 三列写的是**未初始化的内存残值**
      （三次分别拿到 0 / 889、1819239279 / 889、3、755441520 这类数；同一份文件里各行还不一样）。
      这三列是**预制叠合板接缝**参数，现浇板用不到，YJK 就没去初始化它们。
      本模块显式写 0 / 300 / 500 —— 所以拿两份官方产物做 diff 时，
      这几个列是纯噪声，别把它们当成"模型变了"。
  * 官方写盘程序集在当前环境里凑不齐或配不上对（需要 `Hi_AddProjectToYjk` 与**同目录**的
    `ClrYJKAPI.dll`），而建模接口 `DataFunc` 本身是可用的；
  * 只做数据加工/自检时，可以在没有 pythonnet 的进程里拼出模型库 —— 本模块只依赖 sqlite3。

★ 历史教训（根因**不在** CreateYDB，别再把锅扣给它）
------------------------------------------------------
曾经一度断定"CreateYDB 在本机不可用"。症状是：YJK 用它**自己的 MessageBox** 弹
「未能加载到yjkTransYDB.dll或其依赖项」，模态框一弹，进程**永久挂住** ——
不是托管异常，`try/except` 拦不住，超时也杀不干净。
真因是 `column-section-opt\scripts\driver.py` 里那句 `os.add_dll_directory(sdir)`
**没有接返回值**：`DllDirectory` 对象在 CPython 里一被回收就 `RemoveDllDirectory`，
于是目录立刻离开 DLL 搜索路径，原生代码 `LoadLibrary("yjkTransYDB.dll")` 找不到文件。
（同一份知识在 `floor-system-comparison\scripts\yjk_api.py` 里一直是对的 ——
它用模块级 `_DLL_HANDLES` 保活 —— 只是没传到 `driver.py`。）
`driver.py` 现在用 `pin_native_dll_dir()` 保活句柄，并叠加 `SetDllDirectoryW` 与
ctypes 按绝对路径预加载原生依赖，默认路径恢复正常。

★ 先探测，别猜：`python <本技能>\scripts\driver.py createydb`
  它在**子进程**里试一次 CreateYDB（子进程崩/挂都不影响你），给出
  OK / CRASH / TIMEOUT / ERROR 四种结论；`OK` 就说明官方入口能用，用默认路径即可。

★ 本模块为什么不做"自动回退"：上面的两种失败（弹窗、access violation）**都拦不住**，
  "回退"那行代码永远轮不到执行。所以写盘路径是**开工前二选一**的硬约定：
  **给了 `--scaffold` 就绝不调用 CreateYDB；不给就只用 CreateYDB。**

做法（参照 coretube 参考实现，已产出 28 层框筒模型并被 YJK 成功求解 9 次）：
  1. 拿 **YJK 自己新建空工程 save 出来的 `.ymd/.ydb`** 当骨架（77 张表齐全、
     `tblProjectPara` 上千行）—— 参数表不用我们造，风险只落在几何表上；
  2. `DataFunc` 的内存对象（`Mdl_Joint/Grid/ColSeg/BeamSeg/WallSeg/Slab`）字段与
     ydb 表列几乎一一对应，ID 与拓扑都已经算好，落盘只需补 `idNew` 这类交叉引用；
  3. 本模块按 **`PRAGMA table_info` 的真实列**拼 INSERT：没给的列按列类型填
     0 / 0.0 / ''，**给了表里没有的列则当场报错**（见 `YdbWriter.add`）。

字段实测结论（全是"不报错、但结果错"的坑，务必保留）
====================================================
1. **`No_` 是「每个标准层内、每张表各自」从 1 开始的构件序号**，不是全楼连续号。
   实测两处：
     * 真实工程 0807 塔楼：7 个标准层，每个标准层的 `tblColSeg.No_` 都是 1..16；
     * YJK 自己的 CreateYDB 产物（本包 `colopt.py build` 的 10 层框架示例）：
       每个标准层 `tblJoint` 都是 1..16、`tblBeamSeg` 都是 1..24。
   跨标准层连续编号**导入不报错**，但 `设计结果\wpj*.out` 里的 `N-C=<号>` 会和库里
   对不上 —— 分组/取数整片错位，且**不报错**，后面每一步复核都建立在错位上。
   截面表（`tblBeamSect/tblColSect/tblWallSect`）没有 `StdFlrID`，`No_` 是全局 1..N
   （实测 CreateYDB 的 30 个柱截面就是 1..30）。

2. **只有 `tblLoadSect` / `tblLoadSeg` 的序号列叫 `No`，其余几何表都叫 `No_`。**
   写错列名不会报错：`INSERT` 里少了那一列 → 被当成"没给" → 填默认值 0。
   后果实测：**784 条梁上均布线荷载在 `yjk_importydb` 时整批被丢弃**，
   模型照样算得出来，但柱轴力偏小一整块（约 20%）—— 优化的输入就错了。

3. **荷载必须写。** 不写 `tblLoadSect/tblLoadSeg`，梁上的填充墙线荷载静默丢失：
   本项目 8kN/m × 201.6m ≈ 1600kN/层，柱轴力偏小、截面偏小，且不报错。
   实测字段形状（对真实模型逐列核对；本项目 0807 塔楼）：
     `tblLoadSect(ID, No, ElementKind=12, ShapeVal="1.000,<q>,0.000,0.000,0.000,0.000,0.000,",
                  strName, idNew, StateFlag=0)`
     `tblLoadSeg(ID, No, SectID, Type=1, ElementID=<梁段的物理 ID>,
                 strParas1="0.00,0.00,0.00,0.00,0.00,", nPtCnt=0,
                 strParasX/Y/Z="", StdFlrID, idNew, idNewBzc,
                 idElement=<梁段的 idNew>, idDef=<荷载截面的 idNew>, StateFlag=0, idNode=0)`
     且 **`tblLoadSeg.No` 等于该荷载截面自己的 `No`**（不是逐条递增）。
   注：YJK 7.1 的 `CreateYDB` 对同一条梁荷载写的是 `Type=0`，与真实工程实测的 1 不同。
   本模块取 **1**（真实工程口径：参考实现用它产出的 28 层框筒模型被 YJK 成功求解 9 次）。
   实测对照：本模块产物与官方 `CreateYDB` 产物逐表比对时，**这是 15 张表里唯一的差异**
   （其余 14 张表的坐标/尺寸/编号/荷载图形全部逐条相同）。

4. **`idNew` 必须全模型唯一**（不只是本表内）。撞号时 YJK 按 idNew 去重/别名，
   「柱段 → 截面」映射整体错乱 → 大批柱被静默丢弃 → 计算报
   `刚度矩阵不定` + `节点…缺少约束` → `分析失败[-1]`，而导入照样回 OK。
   所以这里的 `idNew` 用**一个全局分配器**，从骨架现有最大值之上开始发号。

5. **骨架的表结构因 YJK 版本而异**：实测同一份建模代码，7.1 的 `CreateYDB` 写出的
   `tblBeamSeg/tblWallSeg` 没有 `NoSlab`、`tblLoadSeg` 没有 `idNode`、`tblSlab`
   没有 `idPreStressHollowSlab*`，而 8.x 空工程保存出来的骨架有。
   骨架的表结构**就是**目标表结构，所以这几列「有就写、没有就跳过」（见 `OPTIONAL_COLS`）；
   其余列名写错一律报错，不许静默。

6. **写盘要么全成、要么别动目标文件。** 中途报错留下"表已清空、行没写进去"的半成品
   ydb，导入后表现为 `fea.dat-ERR.txt: 模型中没有单元数据` + `分析失败[-45]`，
   极难回溯。所以 `serialize()` 先写 `*.tmp`，全部成功才 `os.replace` 到目标。
"""
from __future__ import annotations

import os
import shutil
import sqlite3
import sys

# tblProjectPara 里 100000 是哨兵；实体 ID 必须 < 100000（ydb_lint 的判据 ①）
ID_LIMIT = 100000
SENTINEL = 4294967295
NONE_ID = SENTINEL              # 表里表示"无"的引用值
PARA_N = 26                     # tblStdFlrPara 只存 Para 串的下标 0..25

# 本模块负责写的 15 张表（其余 60 余张参数/其它构件表由骨架原样带过来）
WRITTEN_TABLES = ("tblStdFlr", "tblStdFlrPara", "tblFloor", "tblJoint", "tblAxis",
                  "tblGrid", "tblBeamSect", "tblColSect", "tblWallSect",
                  "tblBeamSeg", "tblColSeg", "tblWallSeg", "tblSlab",
                  "tblLoadSect", "tblLoadSeg")

# 每表主键的**起始基数**：各表号段彼此错开，避免不同表的物理 ID 撞在一起
# （物理 ID 是**全模型**一个号空间：ydb_lint 把所有表的 ID 并成一个集合查引用）。
# 全部 < ID_LIMIT，落在这个区间里 YJK 才会认。
BASE_ID = {"tblStdFlr": 1001, "tblFloor": 2001, "tblJoint": 3000, "tblAxis": 6000,
           "tblGrid": 7000, "tblBeamSect": 1186, "tblBeamSeg": 9000,
           "tblColSect": 1050, "tblWallSect": 1080, "tblColSeg": 11000,
           "tblWallSeg": 15000, "tblSlab": 13000,
           "tblLoadSect": 17000, "tblLoadSeg": 18000}
BASE_IDNEW = 1000               # 全局 idNew 的最小起点（骨架里 idNew 都远小于它）

# 这些表的 `ID` **不是实体号**而是参数键，不能算进实体号空间。
# ★ 为什么必须排除：`tblProjectPara` 的 ID 最大到 81199，还有 100000 哨兵；
#   把它算进去，新号会跑到 8 万级，YJK 导入时直接丢弃这些行。
PARA_TABLES = ("tblProjectPara", "tblStdFlrPara", "tblChildRaftSeg",
               "tblCraneLoad", "tblPileInDaisSect", "tblSubSectionSect")

# ★ 这些列**不是每个 YJK 版本的表里都有**（实测：7.1 的 CreateYDB 没有、8.x 骨架有）。
#   骨架给什么表结构就写什么列 —— 有则写、无则跳过；其余列名写错仍然报错。
OPTIONAL_COLS = {
    "tblBeamSeg": ("NoSlab",),
    "tblWallSeg": ("NoSlab",),
    "tblLoadSeg": ("idNode",),
    "tblSlab": ("idPreStressHollowSlab", "idDefPreStressHollowSlabStr",
                "idPreStressHollowSlabAngle"),
}


class YdbSchemaError(Exception):
    """要写的列在表里不存在 —— 必须当场报错，绝不能静默填默认值。

    为什么用异常而不是打印告警：见模块 docstring 结论 2 ——
    列名写错（典型是 `tblLoadSeg` 的 `No` 写成 `No_`）只会被填成 0，
    整批荷载静默失效，模型照样算得出来，事后极难回溯。
    """


# ============================================================ 骨架
def _require_scaffold(scaffold):
    if not scaffold:
        raise SystemExit("没给骨架模型。请用 YJK 新建一个空工程并保存"
                         "（`yjk_auto.py send yjk_save --dir <工程目录>`），"
                         "把那个 .ymd/.ydb 当 --scaffold 传进来。")
    if not os.path.exists(scaffold):
        raise SystemExit("骨架模型不存在：%s\n"
                         "（骨架 = YJK 自己新建空工程保存出来的 .ymd；不是我们自己造的库。）"
                         % scaffold)
    if os.path.getsize(scaffold) == 0:
        raise SystemExit("骨架模型是空文件：%s（0 字节）" % scaffold)


def scaffold_tables(scaffold):
    """读骨架的表名集合（顺带验证它确实是个模型库）。"""
    try:
        con = sqlite3.connect("file:%s?mode=ro" % str(scaffold).replace("\\", "/"),
                              uri=True)
    except sqlite3.Error as e:
        raise SystemExit("骨架模型打不开（不是 SQLite 库？）：%s\n  %s" % (scaffold, e))
    try:
        return {r[0] for r in con.execute(
            "SELECT name FROM sqlite_master WHERE type='table'")}
    finally:
        con.close()


def copy_scaffold(scaffold, out_ydb):
    """把骨架复制成目标 ydb，并检查骨架是否可用；返回目标路径。

    ★ 为什么不"就地改骨架"：骨架是 YJK 存出来的**空工程**，是所有模型的共同底本，
      被改过一次以后所有后续模型都带上上一次的残留行（YJK 会静默吃进去）。
    """
    _require_scaffold(scaffold)
    ts = scaffold_tables(scaffold)
    missing = [t for t in WRITTEN_TABLES if t not in ts]
    if missing:
        raise SystemExit(
            "骨架模型 %s 缺这些表：%s\n"
            "（共 %d 张表，应有 %d 张。）骨架应当是 **YJK 自己新建空工程后 save 出来的**"
            ".ymd/.ydb；8.x 之前的空工程表少，`tblWallSect/tblSlab` 不全就会写不出模型。"
            % (scaffold, missing, len(ts), 77))
    out_dir = os.path.dirname(os.path.abspath(out_ydb))
    if out_dir and not os.path.isdir(out_dir):
        os.makedirs(out_dir, exist_ok=True)
    if os.path.exists(out_ydb):
        os.remove(out_ydb)
    shutil.copyfile(scaffold, out_ydb)
    return out_ydb


# ============================================================ 写库
class YdbWriter:
    """按真实表结构往 ydb 里写行。

    四件事由它统一管住（这四件都是"错了不报错"的坑）：
      * `add()`  —— 列名必须是表里真有的列（见 `YdbSchemaError`）；
      * `new()`  —— 全局 `idNew` 分配器，从骨架现有最大值之上开始发；
      * `nxt(t)` —— 每表主键分配器，基数见 `BASE_ID`，并跳过已被占用的号；
      * `no(t, 层)` —— `No_` 在**每个标准层内、每张表各自**从 1 起（见模块 docstring 结论 1）。
    """

    def __init__(self, con, verbose=False):
        self.con = con
        self.verbose = verbose
        self._cols = {}
        self._nomap = {}
        self._idnext = {}
        self._used_id = set()
        self._max_id = {}
        self._new = BASE_IDNEW
        self._scan_existing()

    # -------------------------------------------------- 表结构
    def cols(self, t):
        """[(列名, 列类型)]，按表定义顺序（INSERT 也按这个顺序拼，列不全就填默认值）。"""
        if t not in self._cols:
            rows = list(self.con.execute("PRAGMA table_info([%s])" % t))
            if not rows:
                raise YdbSchemaError("库里没有这张表：%s" % t)
            self._cols[t] = [(r[1], r[2]) for r in rows]
        return self._cols[t]

    def colnames(self, t):
        return [c for c, _ in self.cols(t)]

    # -------------------------------------------------- 取号
    def _scan_existing(self):
        """扫**全模型**已用的实体 ID / idNew，作为分配器的起点。

        ★ 为什么新号必须"从现有最大值之上"取：见模块 docstring 结论 4 —— idNew 撞号
          会让 YJK 按 idNew 去重/别名，构件被静默丢弃。
        """
        for (t,) in self.con.execute("SELECT name FROM sqlite_master WHERE type='table'"):
            if t in PARA_TABLES:
                continue
            names = self.colnames(t)
            if "ID" in names:
                m = self.con.execute("SELECT max(ID) FROM [%s]" % t).fetchone()[0]
                if isinstance(m, int) and 0 < m < ID_LIMIT:
                    self._max_id[t] = m
                self._used_id |= {
                    r[0] for r in self.con.execute("SELECT ID FROM [%s]" % t)
                    if isinstance(r[0], int) and 0 < r[0] < ID_LIMIT}
            if "idNew" in names:
                m = self.con.execute("SELECT max(idNew) FROM [%s]" % t).fetchone()[0]
                if isinstance(m, int) and 0 < m != SENTINEL and m > self._new:
                    self._new = m

    def new(self):
        """下一个全局 `idNew`（跨全部表唯一）。"""
        self._new += 1
        return self._new

    def nxt(self, t):
        """下一个本表主键 `ID`（基数见 `BASE_ID`，跳过已被别的表占用的号）。"""
        if t not in BASE_ID:
            raise YdbSchemaError("表 %s 没有配主键基数（BASE_ID）" % t)
        c = self._idnext.get(t)
        if c is None:
            c = max(BASE_ID[t], self._max_id.get(t, 0) + 1)
        while c in self._used_id:
            c += 1
        self._used_id.add(c)
        self._idnext[t] = c + 1
        return c

    def no(self, t, layer):
        """本表在某个标准层内的下一个 `No_`（从 1 起，逐标准层独立）。

        `layer` 传该标准层在**本库里的 ID**；没有标准层归属的表（梁/柱/墙截面）
        传任意常量（如 `0`）即得全局 1..N —— 与实测的 CreateYDB 产物一致。
        """
        k = (t, layer)
        self._nomap[k] = self._nomap.get(k, 0) + 1
        return self._nomap[k]

    # -------------------------------------------------- 写行
    @staticmethod
    def default_for(coltype):
        t = (coltype or "").upper()
        if "INT" in t:
            return 0
        if any(k in t for k in ("REAL", "FLOA", "DOUB", "NUM", "DEC")):
            return 0.0
        return ""

    def add(self, t, row):
        """按表的真实列写一行：没给的列填类型默认值，给了表里没有的列 → 报错。"""
        cols = self.cols(t)
        names = {c for c, _ in cols}
        unknown = [k for k in row if k not in names]
        if unknown:
            opt = OPTIONAL_COLS.get(t, ())
            miss_opt = [k for k in unknown if k in opt]
            unknown = [k for k in unknown if k not in opt]
            if unknown:
                hint = ""
                if "No_" in unknown and "No" in names:
                    hint = ("\n  ★ 本表的序号列叫 `No`（不是 `No_`）。写错列名不会报错，"
                            "只会被填成 0 —— 后果见 ydb_serialize 模块 docstring 结论 2。")
                elif "No" in unknown and "No_" in names:
                    hint = "\n  ★ 本表的序号列叫 `No_`（不是 `No`）。"
                raise YdbSchemaError(
                    "表 %s 里没有这些列：%s\n  该表的列：%s%s"
                    % (t, unknown, sorted(names), hint))
            # 版本可选的列：骨架的表结构就是目标结构，没有就不写（见 OPTIONAL_COLS）
            if miss_opt:
                row = {k: v for k, v in row.items() if k not in miss_opt}
        self.con.execute(
            "INSERT INTO [%s] (%s) VALUES (%s)"
            % (t, ",".join("[%s]" % c for c, _ in cols), ",".join(["?"] * len(cols))),
            [row.get(c, self.default_for(ty)) for c, ty in cols])

    # -------------------------------------------------- 清表 / 统计
    def clear(self, t):
        self.con.execute("DELETE FROM [%s]" % t)

    def clear_all(self, tables=WRITTEN_TABLES):
        """清空本模块要重写的表。

        ★ 不清的话，骨架自带的 1 行 `tblStdFlr` + 26 行 `tblStdFlrPara` 会留下，
          于是模型里多出一个"没有自然层、没有几何"的标准层 ——
          导入后表现为楼层组装错乱，而表结构上完全看不出来。
        """
        for t in tables:
            self.clear(t)

    def counts(self, tables=WRITTEN_TABLES):
        return {t: self.con.execute("SELECT count(*) FROM [%s]" % t).fetchone()[0]
                for t in tables}


def _wh(shapeval):
    """从 ShapeVal "1,<b>,<h>,<mat>,<ID>," 里取 (b, h)。"""
    v = str(shapeval or "").split(",")
    if len(v) < 3:
        raise SystemExit("ShapeVal 解析失败：%r" % shapeval)
    return int(round(float(v[1]))), int(round(float(v[2])))


# ============================================================ 整模型落库
class ModelWriter(YdbWriter):
    """把「一次建模的内存模型」逐表落库。

    `meta` 的形状（由建模脚本给出，本模块只认这几个键）：
        meta["model"]  Hi_DbModelData（m_StdFlr/m_Floor/m_Joint/m_Axis/m_Grid/
                       m_BeamSect/m_ColSect/m_BeamSeg/m_ColSeg/m_WallSeg/m_Slab/
                       m_LoadSect/m_LoadSeg）
        meta["stds"]   [{"floor": 自然层号, "std": Mdl_StdFlr, "para": 参数串,
                         "height": 层高, "wall_thk": 墙厚, ...}, ...]
        meta["plan"]   布置计划（**写板必须有**：`tblSlab.GridsID/idGridStr` 要按板块
                       四条边反查网格号，光有板块中心坐标凑不出来）
        meta["cfg"]    配置（取梁均布荷载）
    """

    def __init__(self, con, verbose=False):
        super().__init__(con, verbose=verbose)
        self._std_id = {}       # 内存标准层 ID -> 本库 tblStdFlr.ID
        self._std_new = {}      # 内存标准层 ID -> 本库 tblStdFlr.idNew
        self._jid, self._jnew = {}, {}
        self._aid, self._anew = {}, {}
        self._gid, self._gnew = {}, {}
        self._bsid, self._bsnew = {}, {}
        self._csid, self._csnew = {}, {}
        self._lsid, self._lsnew, self._lsno = {}, {}, {}
        self._beamseg_id, self._beamseg_new = {}, {}
        self.stds = []

    # ------------------------------------------------ 小工具
    def _sid(self, obj_or_id):
        """内存里的标准层 ID -> 本库 tblStdFlr.ID。"""
        k = int(obj_or_id)
        if k not in self._std_id:
            raise YdbSchemaError("这个标准层不在本次写入里：内存 StdFlrID=%s" % k)
        return self._std_id[k]

    # ------------------------------------------------ 标准层
    def write_std_flr(self, stds):
        """tblStdFlr：一个自然层一个标准层（逐层可不同截面/等级）。"""
        self.stds = list(stds)
        for st in self.stds:
            f = st["floor"]
            st["id"] = self.nxt("tblStdFlr")
            st["idNew"] = self.new()
            k = int(st["std"].ID)
            self._std_id[k] = st["id"]
            self._std_new[k] = st["idNew"]
            self.add("tblStdFlr", dict(
                ID=st["id"], No_=f, Height=int(st["height"]),
                Dead=float(st["std"].DeadLoad), Live=float(st["std"].LiveLoad),
                DPara="0,1,0", Para=st["para"], Name="",
                idNew=st["idNew"], StateFlag=0))
            self.write_std_flr_para(st)

    def write_std_flr_para(self, st):
        """tblStdFlrPara：`Para` 串的展开表，**只存下标 0..25**（实测 CreateYDB 26 行）。

        ★ 必须整套写满 26 行：缺的 Kind 会被 YJK 用它**自己的默认值**补齐 ——
          等级/保护层静默偏离，而 `Para` 串看上去是对的。
        """
        parts = st["para"].split(",")
        for k in range(PARA_N):
            v = parts[k] if k < len(parts) else ""
            self.add("tblStdFlrPara", dict(
                StdFlrID=st["id"], Kind=k,
                ParaVal=int(float(v)) if str(v).strip() else 0))

    # ------------------------------------------------ 节点 / 轴线 / 网格
    def register_topology(self, joints, axes, grids):
        """先给节点/轴线/网格**统一发号**，再写行。

        ★ 顺序不能反：`tblAxis` 要引用节点的 ID 与 idNew，`tblGrid` 还要引用轴线，
          所以三张表的号必须**先全部发完**（三张表各一个独立的主键号段），
          后面写行时才有号可引用。分开发号、边发边写会让后写的表引用到空号。
        """
        for ob in joints:
            k = int(ob.ID)
            self._jnew[k], self._jid[k] = self.new(), self.nxt("tblJoint")
        for ob in axes:
            k = int(ob.ID)
            self._anew[k], self._aid[k] = self.new(), self.nxt("tblAxis")
        for ob in grids:
            k = int(ob.ID)
            self._gnew[k], self._gid[k] = self.new(), self.nxt("tblGrid")
        self.joints = list(joints)
        self.grids = list(grids)

    def write_joint(self):
        # 节点的 ListGJidNew = 挂在该节点上的**网格 idNew** 列表
        touch = {}
        for gr in self.grids:
            for j in (int(gr.Jt1ID), int(gr.Jt2ID)):
                touch.setdefault(j, []).append(self._gnew[int(gr.ID)])
        for ob in self.joints:
            k = int(ob.ID)
            sid = self._sid(ob.StdFlrID)
            self.add("tblJoint", dict(
                ID=self._jid[k], No_=self.no("tblJoint", sid), StdFlrID=sid,
                X=float(ob.X), Y=float(ob.Y), HDiff=int(ob.HDiff),
                idNew=self._jnew[k],
                ListGJidNew="".join("%d," % v for v in touch.get(k, [])),
                ListLoadidNew="", StateFlag=0))

    def write_axis(self, axes):
        for ob in axes:
            k = int(ob.ID)
            sid = self._sid(ob.StdFlrID)
            self.add("tblAxis", dict(
                ID=self._aid[k], No_=self.no("tblAxis", sid), StdFlrID=sid,
                Jt1ID=self._jid[int(ob.Jt1ID)], Jt2ID=self._jid[int(ob.Jt2ID)],
                Name=ob.Name or "", idNew=self._anew[k],
                idNewBzc=self._std_new[int(ob.StdFlrID)],
                idNode1=self._jnew[int(ob.Jt1ID)],
                idNode2=self._jnew[int(ob.Jt2ID)], StateFlag=0))

    def write_grid(self):
        for ob in self.grids:
            k = int(ob.ID)
            sid = self._sid(ob.StdFlrID)
            self.add("tblGrid", dict(
                ID=self._gid[k], No_=self.no("tblGrid", sid), StdFlrID=sid,
                Jt1ID=self._jid[int(ob.Jt1ID)], Jt2ID=self._jid[int(ob.Jt2ID)],
                AxisID=self._aid[int(ob.AxisID)], idNew=self._gnew[k],
                idNewBzc=self._std_new[int(ob.StdFlrID)],
                idNode1=self._jnew[int(ob.Jt1ID)],
                idNode2=self._jnew[int(ob.Jt2ID)],
                idAxis=self._anew[int(ob.AxisID)], idCen=NONE_ID, StateFlag=0))

    # ------------------------------------------------ 截面
    def write_beam_sect(self, sects):
        """tblBeamSect：ShapeVal 用规范串 `1,<b>,<h>,<mat>,<ID>,`（实测 CreateYDB 同形）。"""
        for i, ob in enumerate(sects):
            k = int(ob.ID)
            rid, rnew = self.nxt("tblBeamSect"), self.new()
            self._bsid[k], self._bsnew[k] = rid, rnew
            b_, h_ = _wh(ob.ShapeVal)
            sv = "1,%d,%d,%d,%d," % (b_, h_, int(ob.Mat), rid)
            self.add("tblBeamSect", dict(
                ID=rid, No_=i + 1, Name="", Mat=int(ob.Mat), Kind=int(ob.Kind),
                ShapeVal=sv, ShapeVal1=sv,          # 梁：ShapeVal1 与 ShapeVal 同值
                idNew=rnew, StateFlag=0, ShapeFVal="", b=float(b_), h=float(h_)))

    def write_col_sect(self, sects):
        for i, ob in enumerate(sects):
            k = int(ob.ID)
            rid, rnew = self.nxt("tblColSect"), self.new()
            self._csid[k], self._csnew[k] = rid, rnew
            b_, h_ = _wh(ob.ShapeVal)
            sv = "1,%d,%d,%d,%d," % (b_, h_, int(ob.Mat), rid)
            self.add("tblColSect", dict(
                ID=rid, No_=i + 1, Name="", Mat=int(ob.Mat), Kind=int(ob.Kind),
                ShapeVal=sv, ShapeVal1="",            # 柱：ShapeVal1 实测为空串
                idNew=rnew, StateFlag=0, ShapeFVal="", b=float(b_), h=float(h_)))

    def write_wall_sect(self, stds=None):
        """tblWallSect：厚度取自配置（内存对象字段不可靠），每标准层一个墙截面。

        ★ 没有墙的标准层（纯框架模型）**一行都不写**：凭空造出墙截面不会报错，
          但 YJK 会认为库里存在墙截面，`ydb_lint` 的截面统计也会跟着偏。
        """
        n = 0
        for st in (stds if stds is not None else self.stds):
            thk = st.get("wall_thk")
            if not thk:
                continue
            n += 1
            k = int(st["std"].ID)
            rid, rnew = self.nxt("tblWallSect"), self.new()
            st["wsec_id"], st["wsec_new"] = rid, rnew
            self.add("tblWallSect", dict(
                ID=rid, No_=n, Mat=6, Kind=1, B=int(thk), H=0, T2=0,
                Dis=150.0, Name="", idNew=rnew, StateFlag=0))
        return n

    # ------------------------------------------------ 构件段
    def write_beam_seg(self, segs):
        none4 = ",".join([str(NONE_ID)] * 4) + ","
        for s in segs:
            g_, sec = int(s.GridID), int(s.SectID)
            sid = self._sid(s.StdFlrID)
            rid, rnew = self.nxt("tblBeamSeg"), self.new()
            # ★ 必须同时记下「模型内 ID -> 本库 ID / idNew」：梁上荷载靠它挂上去
            self._beamseg_id[int(s.ID)], self._beamseg_new[int(s.ID)] = rid, rnew
            self.add("tblBeamSeg", dict(
                ID=rid, No_=self.no("tblBeamSeg", sid), StdFlrID=sid,
                SectID=self._bsid[sec], GridID=self._gid[g_],
                Ecc=int(s.Ecc), HDiff1=int(s.HDiff1), HDiff2=int(s.HDiff2),
                Rotation=float(s.Rotation), JYDef=(s.JYDef or "0,0,0,0,"),
                idNew=rnew, idNewBzc=self._std_new[int(s.StdFlrID)],
                idGrid=self._gnew[g_], idDef=self._bsnew[sec],
                defYidNew=none4, StateFlag=0, Ecc2=0, NoSlab=0))

    def write_col_seg(self, segs):
        for s in segs:
            jt, sec = int(s.JtID), int(s.SectID)
            sid = self._sid(s.StdFlrID)
            self.add("tblColSeg", dict(
                ID=self.nxt("tblColSeg"), No_=self.no("tblColSeg", sid), StdFlrID=sid,
                SectID=self._csid[sec], JtID=self._jid[jt],
                EccX=int(s.EccX), EccY=int(s.EccY), Rotation=float(s.Rotation),
                HDiffB=int(s.HDiffB), ColcapId=0, Cut_Col="", Cut_Cap="",
                Cut_Slab="", FootDefID=0, idNew=self.new(),
                idNewBzc=self._std_new[int(s.StdFlrID)], idNewNode=self._jnew[jt],
                idNewDef=self._csnew[sec], idNewCap=NONE_ID, idNewFoot=NONE_ID,
                idNewYZGJ=NONE_ID, idNewJG=NONE_ID, StateFlag=0, ExtLength=0))

    def write_wall_seg(self, segs):
        of_std = {int(st["std"].ID): st for st in self.stds}
        for s in segs:
            g_ = int(s.GridID)
            st = of_std[int(s.StdFlrID)]
            self.add("tblWallSeg", dict(
                ID=self.nxt("tblWallSeg"), No_=self.no("tblWallSeg", st["id"]),
                StdFlrID=st["id"], SectID=st["wsec_id"], GridID=self._gid[g_],
                Ecc=int(getattr(s, "Ecc", 0) or 0),
                HDiff1=int(getattr(s, "HDiff1", 0) or 0),
                HDiff2=int(getattr(s, "HDiff2", 0) or 0),
                HDiffB=int(getattr(s, "HDiffB", 0) or 0),
                sloping=int(getattr(s, "sloping", 0) or 0),
                EccDown=int(getattr(s, "EccDown", 0) or 0),
                offset1=int(getattr(s, "offset1", 0) or 0),
                offset2=int(getattr(s, "offset2", 0) or 0),
                idNew=self.new(), idNewBzc=self._std_new[int(s.StdFlrID)],
                idGrid=self._gnew[g_], idDef=st["wsec_new"], HDiffB2=0,
                WallJY="0,", StateFlag=0, NoSlab=0))

    # ------------------------------------------------ 板
    def write_slab(self, slabs, plan=None):
        """写板：一个网格单元一块板，边界 4 条边都是网格（墙也建在网格上）。

        `tblSlab.GridsID` 是**物理 ID**、`idGridStr` 是 **idNew** —— 两种号空间必须分开查；
        板块对象本身只给中心坐标，四角/四边得由布置计划的板块信息来，
        ★ 但**一块板都没有**时要直接返回：纯剪力墙（把核心筒放大到整个平面）这类模型
          本来就没有板块，`plan["cells"]` 就是空的。实测踩到过（缺陷 D1 的第二处）：
          老代码拿「plan 里没有板块」当成「不知道板在哪」而报 YdbSchemaError，
          于是一个 0 块板的模型被拒之门外。
          要区分的是两件事：**「没有板要写」**（正常，直接返回）与
          **「有板但不知道板在哪」**（真错，必须报错）—— 后者仍由下面的检查兜住。
        """
        if not slabs:
            return
        grids = self.grids
        pair = {}
        for gr in grids:
            pair[frozenset((int(gr.Jt1ID), int(gr.Jt2ID)))] = int(gr.ID)
        node_id_by_xy = {}
        for ob in self.joints:
            node_id_by_xy[(int(ob.StdFlrID), round(float(ob.X)),
                           round(float(ob.Y)))] = int(ob.ID)
        by_center = {}
        for s in slabs:
            by_center[(int(s.StdFlrID), int(round(float(s.xc))),
                       int(round(float(s.yc))))] = s

        if not (plan and plan.get("cells")):
            raise YdbSchemaError(
                "写板必须给布置计划（meta['plan']['cells']）：tblSlab 的 GridsID/idGridStr "
                "要按**板块四条边**反查网格号，光有板块中心坐标凑不出来。")
        cells = []
        for corners, edges in plan["cells"]:
            cx = int(round((corners[0][0] + corners[1][0]) / 2.0))
            cy = int(round((corners[0][1] + corners[3][1]) / 2.0))
            cells.append((cx, cy, corners, edges))

        for st in self.stds:
            sid_mem = int(st["std"].ID)
            for (cx, cy, corners, edges) in cells:
                s = by_center.get((sid_mem, cx, cy))
                if s is None:
                    raise SystemExit("第%d层 板块中心(%d,%d) 在内存模型里找不到板对象"
                                     % (st["floor"], cx, cy))
                eg = []
                for (a, b) in edges:
                    ja = node_id_by_xy[(sid_mem, round(a[0]), round(a[1]))]
                    jb = node_id_by_xy[(sid_mem, round(b[0]), round(b[1]))]
                    gk = pair.get(frozenset((ja, jb)))
                    if gk is None:
                        raise SystemExit("第%d层 板块(%d,%d) 有一条边没有网格"
                                         % (st["floor"], cx, cy))
                    eg.append(gk)
                self.add("tblSlab", dict(
                    ID=self.nxt("tblSlab"), No_=self.no("tblSlab", st["id"]),
                    StdFlrID=st["id"],
                    GridsID="".join("%d," % self._gid[g] for g in eg),
                    VertexX="".join("%.3f," % float(x) for x, _ in corners),
                    VertexY="".join("%.3f," % float(y) for _, y in corners),
                    VertexZ="".join(["0.000,"] * len(corners)),
                    RoomIsHole=0, Thickness=int(s.Thickness),
                    cc=int(getattr(s, "cc", 0) or 0),
                    dead=float(s.dead), live=float(s.live), TransWay=0, Ang1=0.0,
                    Ang2=0.0, nEdge=0, EdgeSupport="", Shape=1,
                    xc=float(s.xc), yc=float(s.yc), HollowSlabID=0,
                    PrecastSlabID="0,0,0,", PrecastSlabRebarPara="",
                    SingleSeamB=0, SingleSeamBMax=100, PairSeamB=300,
                    PairSeamBMax=500, TwoWaySlab=0, PrecastSlabLastL=0.0,
                    PrecastSlabRotate=0, PrecastSlabStyle_PK=0, PrecastSlabOffsetX=0,
                    PrecastSlabOffsetY=0, PrecastSlabX="", PrecastSlabY="",
                    PrecastSlabIndex=0, PrecastSlabCount=0, PrecastSlabArrangeNo="",
                    PrecastSlabArrangeWidth="", precastSlabSpace="",
                    PrecastSlabParaArr="", ProfilSlabDefId=0, ProfilSlabAng=0.0,
                    ProfilSlabConcertW=25.0, ProfilSlabWorkLoad=1.5,
                    ProfilSlabbhou=100.0, HollowBoxPtNum=None, HollowBoxPtX=None,
                    HollowBoxPtY=None, HollowBoxPtZ=None,
                    idNew=self.new(), idNewBzc=self._std_new[sid_mem],
                    idGridStr="".join("%d," % self._gnew[g] for g in eg),
                    idDefHollowSlab=NONE_ID,
                    idPrecastSlabStr=",".join([str(NONE_ID)] * 3) + ",",
                    idDefProfilSlab=NONE_ID,
                    HollowPtOrig="0.00, 0.00, 0.00", HollowVX="0.00, 0.00, 0.00",
                    HollowVY="0.00, 0.00, 0.00",
                    HollowOhterData="0,0,0,0,0,0,-2,-2,0,0,4,",
                    PcSlabStPt="0.00, 0.00, 0.00", PcSlabEdPt="0.00, 0.00, 0.00",
                    idPreStressHollowSlab=0,
                    idDefPreStressHollowSlabStr=NONE_ID,
                    idPreStressHollowSlabAngle=0, StateFlag=0))

    # ------------------------------------------------ 荷载
    def write_load_sect(self, sects, q_beam=None):
        """tblLoadSect：**序号列是 `No` 不是 `No_`**（见模块 docstring 结论 2）。"""
        for i, o in enumerate(sects):
            k = int(o.ID)
            self._lsid[k], self._lsnew[k] = self.nxt("tblLoadSect"), self.new()
            self._lsno[k] = i + 1
            sv = getattr(o, "ShapeVal", None) or ""
            if q_beam is not None:
                sv = "1.000,%.3f,0.000,0.000,0.000,0.000,0.000," % float(q_beam)
            self.add("tblLoadSect", dict(
                ID=self._lsid[k], No=i + 1, ElementKind=int(o.ElementKind),
                ShapeVal=sv, strName=getattr(o, "strName", "") or "",
                idNew=self._lsnew[k], StateFlag=0))

    def write_load_seg(self, segs):
        """tblLoadSeg：把梁上的线荷载挂到梁段上（不写 = 荷载静默丢失）。

        只写挂在**梁**上的线荷载：`ElementID` 指向 `tblBeamSeg.ID`，
        `idElement` 指向 `tblBeamSeg.idNew`，`idDef` 指向 `tblLoadSect.idNew`。
        指向别的构件（墙/板/节点）的行这里跳过 —— 本模块只负责梁上线荷载，
        多写反而会造出悬空引用（`ydb_lint` 判据 ②）。
        """
        n = 0
        for o in segs:
            eid = int(o.ElementID)
            if eid not in self._beamseg_id:
                continue
            sid = self._sid(int(o.stdFlrID))
            sect = int(o.SectID)
            self.add("tblLoadSeg", dict(
                ID=self.nxt("tblLoadSeg"), No=self._lsno[sect], SectID=self._lsid[sect],
                Type=1, ElementID=self._beamseg_id[eid],
                strParas1=getattr(o, "strParas1", "") or "0.00,0.00,0.00,0.00,0.00,",
                nPtCnt=int(o.nPtCnt), strParasX=getattr(o, "strParasX", "") or "",
                strParasY=getattr(o, "strParasY", "") or "",
                strParasZ=getattr(o, "strParasZ", "") or "",
                StdFlrID=sid, idNew=self.new(),
                idNewBzc=self._std_new[int(o.stdFlrID)],
                idElement=self._beamseg_new[eid], idDef=self._lsnew[sect],
                StateFlag=0, idNode=0))
            n += 1
        return n

    # ------------------------------------------------ 自然层
    def write_floor(self, floors):
        """tblFloor：一个标准层一个自然层（逐层变截面/变等级）。

        `LevelB` 直接取内存层对象的标高 —— 它来自建模时 `Floor_Assemb` 的起始标高，
        所以建模那边必须**按累计层高**给（首层层高不同时尤其要）。
        """
        by_std = {}
        for fl in floors:
            by_std.setdefault(int(fl.StdFlrID), []).append(fl)
        for st in self.stds:
            sid_mem = int(st["std"].ID)
            lst = by_std.get(sid_mem) or []
            if not lst:
                raise SystemExit("第%d层 在内存模型里没有对应的自然层（楼层组装没做？）"
                                 % st["floor"])
            fl = lst[0]
            self.add("tblFloor", dict(
                ID=self.nxt("tblFloor"), No_=int(fl.No),
                Name=getattr(fl, "Name", "") or "", StdFlrID=st["id"],
                LevelB=float(fl.LevelB), Height=float(fl.Height), idNew=self.new(),
                idNewBzc=self._std_new[sid_mem], StateFlag=None))

    # ------------------------------------------------ 总调度
    def write_model(self, meta, verbose=True):
        model = meta["model"]
        stds = meta["stds"]
        plan = meta.get("plan")
        cfg = meta.get("cfg") or {}

        self.clear_all()
        self.write_std_flr(stds)
        self.write_beam_sect(list(model.m_BeamSect))
        self.write_col_sect(list(model.m_ColSect))
        self.write_wall_sect(stds)
        # 节点/轴线/网格三张表先统一发号，再按依赖顺序写行
        self.register_topology(list(model.m_Joint), list(model.m_Axis),
                               list(model.m_Grid))
        self.write_joint()
        self.write_axis(list(model.m_Axis))
        self.write_grid()
        self.write_beam_seg(list(model.m_BeamSeg))
        self.write_col_seg(list(model.m_ColSeg))
        self.write_wall_seg(list(model.m_WallSeg))
        self.write_slab(list(model.m_Slab), plan=plan)
        q = ((cfg.get("梁") or {}).get("均布荷载kN每m"))
        self.write_load_sect(list(model.m_LoadSect),
                             q_beam=q if q is not None else None)
        nload = self.write_load_seg(list(model.m_LoadSeg))
        self.write_floor(list(model.m_Floor))
        self.con.commit()
        if verbose:
            total = len(model.m_LoadSeg)
            print("梁上线荷载 %d 条（内存模型里共 %d 条荷载段）" % (nload, total))
            if nload != total:
                print("   ！有 %d 条荷载段不是挂在梁上的（墙/板/节点荷载），本模块不写它们 ——"
                      " 需要时请在骨架里补，别让它们悄悄消失。" % (total - nload))
        return self.counts()


# ============================================================ 自检
def check_numbering(con, verbose=True):
    """硬自检：**每个标准层内、每张几何表各自** `No_` 从 1 起连续。

    这是"导入不报错、但 wpj*.out 的 N-C=<号> 全错位"的那条（模块 docstring 结论 1），
    所以在写盘时就把它当错误挡住，而不是等出报告时才发现对不上。
    返回不满足的表清单。

    ★ `tblWallSeg`（纯框架本就为空）为空是正常的，而 `tblJoint/tblBeamSeg` 为空
      必然是失败 —— 本函数**区分不出这两者**，所以对空表只能 `continue`（空集恒真），
      并把"跳过了哪几张空表"打印出来，不再给出一句无条件的"每张表都从 1 起 ✅"。
      空表到底是不是问题，由 `verify_written()`（与内存模型逐表比行数）判定。
    """
    bad = []
    empty = []
    for t in ("tblJoint", "tblAxis", "tblGrid", "tblBeamSeg", "tblColSeg",
              "tblWallSeg", "tblSlab"):
        cols = [r[1] for r in con.execute("PRAGMA table_info([%s])" % t)]
        if "StdFlrID" not in cols or "No_" not in cols:
            continue
        n_rows = con.execute("SELECT count(*) FROM [%s]" % t).fetchone()[0]
        if not n_rows:
            empty.append(t)
            continue
        rows = list(con.execute("SELECT DISTINCT StdFlrID FROM [%s]" % t))
        for (sid,) in rows:
            g = con.execute("SELECT min(No_), max(No_), count(DISTINCT No_) "
                            "FROM [%s] WHERE StdFlrID=?" % t, (sid,)).fetchone()
            cnt = con.execute("SELECT count(*) FROM [%s] WHERE StdFlrID=?" % t,
                              (sid,)).fetchone()[0]
            if g[0] != 1 or g[1] != cnt or g[2] != cnt:
                bad.append((t, sid, g[0], g[1], cnt))
    if verbose:
        if empty:
            print("   （这些表**一行都没有**，No_ 自检对它们恒真：%s —— "
                  "空表是不是问题由写回校验判定）" % ", ".join(empty))
        if bad:
            print("!! No_ 自检不过（要求：每个标准层内从 1 起、连续、不重号）：")
            for t, sid, a, b, n in bad[:10]:
                print("     %s  std=%s  范围=%s..%s  行数=%d" % (t, sid, a, b, n))
        else:
            print("No_ 自检：每个标准层内、每张表都从 1 起 ✅")
    return bad


def check_load_refs(con, verbose=True):
    """硬自检：荷载段的两个引用都必须落地。

    `tblLoadSeg.ElementID` → `tblBeamSeg.ID`（物理号），
    `tblLoadSeg.idElement` → `tblBeamSeg.idNew`（idNew 号）。
    ★ 实测症状：这两个键写错时 `yjk_importydb` **回 OK、不报错**，
      只是整批荷载消失 —— 柱轴力偏小约 20%。
    """
    bad = {}
    n = con.execute("SELECT count(*) FROM tblLoadSeg").fetchone()[0]
    bad["ElementID 悬空"] = con.execute(
        "SELECT count(*) FROM tblLoadSeg l LEFT JOIN tblBeamSeg b "
        "ON b.ID=l.ElementID WHERE b.ID IS NULL").fetchone()[0]
    bad["idElement 悬空"] = con.execute(
        "SELECT count(*) FROM tblLoadSeg l LEFT JOIN tblBeamSeg b "
        "ON b.idNew=l.idElement WHERE b.ID IS NULL").fetchone()[0]
    bad["idDef 悬空"] = con.execute(
        "SELECT count(*) FROM tblLoadSeg l LEFT JOIN tblLoadSect s "
        "ON s.idNew=l.idDef WHERE s.ID IS NULL").fetchone()[0]
    bad = {k: v for k, v in bad.items() if v}
    if verbose:
        if not n:
            print("!! tblLoadSeg 一条都没有 —— 梁上荷载会静默丢失（柱轴力偏小）")
        elif bad:
            print("!! 荷载引用悬空：%s" % bad)
        else:
            print("荷载自检：%d 条荷载段，ElementID/idElement/idDef 全部落地 ✅" % n)
    return n, bad


# ============================================================ 写回校验
def expected_rows(meta, nload):
    """每张表**应当**写多少行 —— 期望值全部来自内存模型/写入器本身。

    用它跟"从库里读回来的行数"逐表比对，就能把两类失败一次挡住：
      * 空表：`check_numbering` 对空表直接 `continue`（空集恒真），
        于是"几何表全空"这个最严重的失败形态恰好是自检最容易通过的一种；
      * 少写：任何 `write_*` 因上游空集合/异常而没写全，行数就会对不上。

    注意 `tblFloor` 期望的是**标准层数**而不是 `len(m_Floor)`：`write_floor`
    刻意"一个标准层一个自然层"（取该标准层的第一个自然层），见它的 docstring。
    """
    model = meta["model"]
    stds = list(meta.get("stds") or [])
    return {
        "tblStdFlr": len(stds),
        "tblStdFlrPara": PARA_N * len(stds),
        "tblFloor": len(stds),
        "tblJoint": len(model.m_Joint),
        "tblAxis": len(model.m_Axis),
        "tblGrid": len(model.m_Grid),
        "tblBeamSect": len(model.m_BeamSect),
        "tblColSect": len(model.m_ColSect),
        "tblWallSect": len([st for st in stds if st.get("wall_thk")]),
        "tblBeamSeg": len(model.m_BeamSeg),
        "tblColSeg": len(model.m_ColSeg),
        "tblWallSeg": len(model.m_WallSeg),
        "tblSlab": len(model.m_Slab),
        "tblLoadSect": len(model.m_LoadSect),
        "tblLoadSeg": nload,
    }


def verify_written(con, meta, nload, verbose=True):
    """写回校验：库里的行数必须等于内存模型该有的行数，否则**不落盘**。

    ★ 为什么必须有
      `write_model()` 返回的 `stat` 是从库里真读回来的行数（这点做对了），
      但调用方只是 `for k in sorted(stat): print(...)` —— **从不与"应写多少"比对**，
      于是"每张表都是 0"与"每张表都对"在返回值与退出码上完全同形。
      另外 `check_load_refs()` 的 `nload` 被解包后从未使用：
      `!! tblLoadSeg 一条都没有 —— 梁上荷载会静默丢失（柱轴力偏小）` 只在屏幕上闪一下，
      库照样 `os.replace` 落盘、rc=0 —— 而"整批荷载消失、柱轴力偏小约 20%"
      正是本模块 docstring 反复强调的头号静默缺陷。
      这里两件事一起补齐：行数比对 + 荷载缺失的硬失败。
    """
    exp = expected_rows(meta, nload)
    got = {t: con.execute("SELECT count(*) FROM [%s]" % t).fetchone()[0] for t in exp}
    diff = [(t, exp[t], got[t]) for t in sorted(exp) if exp[t] != got[t]]
    if verbose:
        if diff:
            print("!! 写回校验：%d/%d 张表的行数与内存模型对不上" % (len(diff), len(exp)))
            for t, e, g in diff:
                print("     %-16s 期望 %-6d 实际 %-6d" % (t, e, g))
        else:
            print("写回校验：%d 张表的行数与内存模型逐表一致 ✅" % len(exp))

    # 荷载单独判：有梁段却一条荷载都没有（这才是静默丢荷载的形态）。
    # 顺序不能反着写：纯剪力墙模型本来没有梁，那种情况不该报。
    q = ((meta.get("cfg") or {}).get("梁") or {}).get("均布荷载kN每m")
    lost_load = bool(exp["tblBeamSeg"] and not got.get("tblLoadSeg")
                     and q and float(q) > 0)
    if lost_load and verbose:
        print("!! 有 %d 条梁段，却一条梁上荷载都没写进库 —— 本次不落盘"
              % exp["tblBeamSeg"])

    if diff or lost_load:
        msg = ["写回校验失败：库里读回的行数与内存模型对不上 / 荷载整块丢失 —— "
               "本次**不落盘**", "   目标文件一个字节都没动（本函数在 os.replace 之前调用）。"]
        if diff:
            msg.append("   行数对不上的表：")
            msg += ["     %-16s 期望 %-6d 实际 %-6d" % d for d in diff]
            msg.append("   常见原因：某张几何表被上游空集合写成 0 行（导入后会报"
                       "「模型中没有单元数据」+ 分析失败[-45]）；"
                       "或某个 write_* 中途抛错只写了一半。")
        if lost_load:
            msg.append(
                "   荷载：有 %d 条梁段、却 0 条 tblLoadSeg；配置 梁.均布荷载kN每m = %s。\n"
                "   后果：梁上填充墙线荷载整块丢失，模型照样算得出来，但柱轴力偏小"
                "（本包量级约 20%%）→ 柱截面会选偏小，且结果文件一个错都不报。\n"
                "   检查：建模那边 `load_arrange` 是否真的布上了（beamload 是否为 None / "
                "该层有没有梁段）。" % (exp["tblBeamSeg"], q))
        raise SystemExit("\n".join(msg))
    return got


# ============================================================ 对外入口
def serialize(meta, out_ydb, scaffold, check=True, verbose=True):
    """骨架 -> 目标 ydb，把 meta 里的内存模型写进去；返回各表行数。

    ★ 先写 `*.tmp`、全部成功后再 `os.replace` 到目标 —— 中途报错宁可没有文件，
      也不留"表已清空、行没写进去"的半成品（导入后会报
      `模型中没有单元数据` + `分析失败[-45]`，很难回溯到是写库失败）。
    """
    # ★ 本函数的自检输出里有 ✅ ❌ 这类非 cp936 字符，而它是在**调用方进程**里
    #   打印的（本模块被 frame_build.py 等 import 当库用）。所以兜底必须在这里也调
    #   一次，不能只放在 `if __name__ == "__main__"` 里 —— GBK 控制台下那些 print
    #   会抛 UnicodeEncodeError 并以退出码 1 中断。重复调用无害。
    _utf8_console()
    _require_scaffold(scaffold)
    tmp = out_ydb + ".tmp"
    if os.path.exists(tmp):
        os.remove(tmp)
    copy_scaffold(scaffold, tmp)
    try:
        con = sqlite3.connect(tmp)
        try:
            w = ModelWriter(con, verbose=verbose)
            stat = w.write_model(meta, verbose=verbose)
            if check:
                bad = check_numbering(con, verbose=verbose)
                nload, badref = check_load_refs(con, verbose=verbose)
                if bad:
                    raise SystemExit("No_ 编号自检失败，不写出这个库（见上面清单）")
                if badref:
                    raise SystemExit("荷载引用自检失败，不写出这个库（见上面清单）")
                verify_written(con, meta, nload, verbose=verbose)
        finally:
            con.close()
    except BaseException:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise
    if os.path.exists(out_ydb):
        os.remove(out_ydb)
    os.replace(tmp, out_ydb)
    return stat


# 总信息 `tblProjectPara` 的 ID 含义（**逐条核对过**：拿默认空工程与真实框筒工程
# 的 tblProjectPara 逐行对比出 49 行差异，再用「改一行 → 发一轮 @recalc →
# 读 wmass.out 的设计参数输出」确认）。
# ★ 这里**不内置任何工程的取值** —— 内置默认表换工程后会让结构体系/抗震等级全错
#   却不报错，而这两项直接决定轴压比限值。要改哪些由配置文件的 `总信息` 给。
PROJECT_PARA_NAME = {
    101: "结构体系（'10101'=框架结构，'10103'=框架-核心筒）",
    201: "地面粗糙程度",
    202: "修正后的基本风压(kN/m2)",
    203: "结构X向基本周期(s)",
    204: "结构Y向基本周期(s)",
    302: "地震烈度",
    303: "场地类别",
    304: "考虑偶然偏心",
    307: "考虑双向地震扭转效应",
    310: "周期折减系数",
    312: "特征周期",
    313: "地震影响系数最大值",
    703: "剪力墙的抗震等级",
}


def apply_project_para(out_ydb, overrides, verbose=True):
    """按 {ParaID: 值} 改写 `tblProjectPara`（结构体系/地震参数/抗震等级）。

    ★ 为什么必须能改：骨架是**空工程**，结构体系默认是"框架结构"。
      框筒模型不改这一项，`wmass.out` 的轴压比限值/抗震等级就按框架结构取，
      而 `wpj*.out` 不会报任何错 —— 优化的判据从一开始就是错的。
      （ID 含义见 `PROJECT_PARA_NAME`；本项目实测：703 从 '70104' 三级 →
        '70103' 二级 → '70102' 一级，与 JGJ3-2010 表 3.9.3 对得上。）

    ★ 改写没落地一律**显式失败**（抛 SystemExit），不靠返回值提醒调用方：
      骨架来自"空工程"，`tblProjectPara` 少一行（例如空工程里没有墙、
      于是很可能没有 703 剪力墙抗震等级）时，老版只打印一句 `(缺行)` 就继续，
      `frame_build.write_out` 连返回值都不接 —— 抗震等级没改、rc 仍为 0，
      而抗震等级/轴压比限值**直接决定优化判据**。
      这里同时补上写回校验（逐项读回来比对），"执行了 UPDATE"不等于"值真的变了"。
    """
    changed, missing, mismatch = [], [], []
    con = sqlite3.connect(out_ydb)
    try:
        for k, v in dict(overrides or {}).items():
            cur = con.execute("SELECT ParaVal FROM tblProjectPara WHERE ID=?",
                              (int(k),)).fetchone()
            if cur is None:
                missing.append(int(k))
                continue
            con.execute("UPDATE tblProjectPara SET ParaVal=? WHERE ID=?",
                        (str(v), int(k)))
            changed.append((int(k), cur[0], v))
        con.commit()
        for k, _old, v in changed:                  # 写回校验
            row = con.execute("SELECT ParaVal FROM tblProjectPara WHERE ID=?",
                              (k,)).fetchone()
            if row is None or str(row[0]) != str(v):
                mismatch.append((k, str(v), None if row is None else str(row[0])))
    finally:
        con.close()
    if verbose:
        # 「改写 N 项」只数**真的落地了**的项：老版把 "(缺行)"（根本没写）也算进去，
        # 于是"改了 3 项"里可能一项都没生效。
        print("总信息改写 %d 项：" % len(changed))
        for k, a, b in changed:
            print("   ID=%-6s %-28s %r -> %r"
                  % (k, PROJECT_PARA_NAME.get(k, ""), a, b))
        for k in missing:
            print("   !! ID=%-6s %-28s **库里没有这一行，该项一个字节都没改**"
                  % (k, PROJECT_PARA_NAME.get(k, "")))
        for k, want, got in mismatch:
            print("   !! ID=%-6s 写回校验不符：期望 %r，读回 %r" % (k, want, got))
    if missing or mismatch:
        raise SystemExit(
            "!! 总信息改写没落地 —— %s 的 tblProjectPara 里缺这些 ID 的行：%s"
            "%s\n"
            "   抗震等级 / 结构体系 / 地震参数直接决定轴压比限值与优化判据：\n"
            "   改不动却继续跑，优化的目标从一开始就是错的，而结果文件不会报任何错。\n"
            "   该库已经写出（%s），**不要**拿它去做导入/计算。\n"
            "   处置：① 从配置的 `总信息` 里删掉这些 ID（骨架本来没有这一项）；\n"
            "         ② 或换一个与目标 YJK 版本一致的空工程骨架（骨架的表结构决定它有哪些项）。"
            % (out_ydb, missing,
               ("；写回校验不符：%s" % mismatch) if mismatch else "", out_ydb))
    return changed


def _utf8_console():
    """让输出在任何控制台编码下都不崩（GBK 下把不可编码字符替换掉）。

    为什么需要：本包会打印 ✅ ❌ ⚠ −(U+2212) ² ³ 等**非 cp936** 字符，
    默认 GBK 控制台下 print 会抛 UnicodeEncodeError 并**以退出码 1 中断**，
    于是一个其实已经成功的任务（比如文件已经落盘）会被上层判成失败。
    errors=replace 让它在 UTF-8 控制台下原样输出、在 GBK 下退化成 ?，都不崩。

    ★ 只在真正的 CLI 入口调用：本模块是**库**（frame_build.py 等 import 它），
      在模块顶层无条件改 stdout 会污染 import 它的进程。

    ⚠ 已知局限：本模块的 ✅ 自检输出（如 serialize 的 No_ 自检、荷载自检）是在
      **调用方进程**里 print 的，所以真正保护那些行的是**调用方的入口兜底**。
      本文件的兜底只覆盖「直接把本文件当脚本跑」这一种情形。
    """
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(errors="replace")
        except Exception:
            pass


if __name__ == "__main__":
    _utf8_console()
