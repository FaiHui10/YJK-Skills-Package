# -*- coding: utf-8 -*-
"""把模型按自然层拆标准层：使每个标准层的混凝土等级唯一，从而能写进模型库。

设计要点
--------
* 目标：把"按自然层变化、但跨了标准层"的柱混凝土等级，变成"每个标准层一份等级"。
  - --mode zone（默认）：只在**等级分界处**拆，N 个自然层 → 若干标准层。
  - --mode all      ：每个自然层一个标准层。
* 等级来源：`--zones "1-5:60,6:30"` 显式指定；不给则从源模型
  `tblStdFlr.Para[4]`（柱强度×10）**现读**；两者都没有就报错退出 ——
  **绝不套用别的工程的写死分区**。
* 只改「柱」等级（Para 下标 4）；板/梁/墙保持源模型原值（`--wall-follow-col` 可让墙跟随柱）。
* 柱截面：原样复制 → 同一原标准层下的柱截面保持一致。
* ID 与 idNew 是**全模型共享的编号空间**，因此：
  - 给所有被复制的行分配新的 ID / idNew，并维护**按 (源标准层, 覆盖自然层) 分开**的
    `id_map` / `in_map`（用全局单张表会在 `--mode all` 下被反复覆盖，见第二步注释）；
  - 逐表按**显式列名**重映射引用（ID/节点 idNew/逗号列表等），不盲目替换数字。
* 只新增、不删除：原有标准层保留，只把"要注意等级的那几层"迁到新标准层上。
"""
import argparse
import collections
import os
import shutil
import sqlite3
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC_DEFAULT = os.environ.get("YJK_SPLIT_SRC", "")      # 不写死路径；请用 --src 指定
DST_DEFAULT = os.path.join(os.getcwd(), "split.ydb")

# 自然层 -> 柱混凝土等级：**从源模型现读**（tblFloor.StdFlrID -> tblStdFlr.Para[4]），
# ★ 不写死任何工程的等级分区 —— 写死分区后换工程会**悄悄**按别的工程的口径
#   拆标准层，极难发现。等级来源：① 优先 --zones 显式覆盖；
#   ② 否则读源模型真值；③ 都没有就**报错**。
BEAM_GRADE, SLAB_GRADE = 300, 300          # C30×10
PARA_IDX_COL = 4                           # tblStdFlr.Para 里「柱强度×10」的下标

# 每个"段表"：自身主键列、idNew 列、ID 引用列、idNew 引用列、逗号列表(列, 类型)
SEG_TABLES = {
    "tblJoint":    {"refs_id": [], "refs_new": [],
                    "lists": [("ListGJidNew", "idNew"), ("ListLoadidNew", "idNew")]},
    "tblAxis":     {"refs_id": ["Jt1ID", "Jt2ID"], "refs_new": ["idNode1", "idNode2"]},
    "tblGrid":     {"refs_id": ["Jt1ID", "Jt2ID", "AxisID"],
                    "refs_new": ["idNode1", "idNode2", "idAxis", "idCen"]},
    "tblColSeg":   {"refs_id": ["JtID"], "refs_new": ["idNewNode"]},
    "tblBeamSeg":  {"refs_id": ["GridID"], "refs_new": ["idGrid"]},
    "tblWallSeg":  {"refs_id": ["GridID"], "refs_new": ["idGrid"]},
    "tblWallHole": {"refs_id": ["GridID", "FillWallId"],
                    "refs_new": ["idGrid", "idFillWall"]},
    "tblSlab":     {"refs_id": [], "refs_new": [],
                    "lists": [("GridsID", "ID"), ("idGridStr", "idNew")]},
    "tblLoadSeg":  {"refs_id": ["ElementID"], "refs_new": ["idElement", "idNode"]},
}
# 这些列在每个段表里都要指向"新标准层"的 idNew
BZC_COLS = ["idNewBzc"]

# 引用自检用：每个「引用列 -> 它应当指向的表」。两种号空间必须分开查：
#   * 逻辑引用（idNode1/idAxis/idGrid/idNewNode/idElement/…）按 **idNew** 查
#   * 物理引用（Jt1ID/AxisID/GridID/JtID/FillWallId/…）按 **ID** 查
# ★ 用来验证"同一标准层的几何只引用同一标准层的节点/轴线"（见第二步半）。
REF_TARGET_NEW = {
    ("tblAxis", "idNode1"): "tblJoint",
    ("tblAxis", "idNode2"): "tblJoint",
    ("tblGrid", "idNode1"): "tblJoint",
    ("tblGrid", "idNode2"): "tblJoint",
    ("tblGrid", "idAxis"): "tblAxis",
    ("tblGrid", "idCen"): "tblAxis",
    ("tblColSeg", "idNewNode"): "tblJoint",
    ("tblBeamSeg", "idGrid"): "tblGrid",
    ("tblWallSeg", "idGrid"): "tblGrid",
    ("tblWallHole", "idGrid"): "tblGrid",
    ("tblWallHole", "idFillWall"): "tblWallSeg",
    ("tblLoadSeg", "idNode"): "tblJoint",
}
REF_TARGET_ID = {
    ("tblAxis", "Jt1ID"): "tblJoint",
    ("tblAxis", "Jt2ID"): "tblJoint",
    ("tblGrid", "Jt1ID"): "tblJoint",
    ("tblGrid", "Jt2ID"): "tblJoint",
    ("tblGrid", "AxisID"): "tblAxis",
    ("tblColSeg", "JtID"): "tblJoint",
    ("tblBeamSeg", "GridID"): "tblGrid",
    ("tblWallSeg", "GridID"): "tblGrid",
    ("tblWallHole", "GridID"): "tblGrid",
    ("tblWallHole", "FillWallId"): "tblWallSeg",
}
LIST_TARGET_NEW = {("tblSlab", "idGridStr"): "tblGrid",
                   ("tblJoint", "ListGJidNew"): "tblLoadSeg"}
LIST_TARGET_ID = {("tblSlab", "GridsID"): "tblGrid"}


def grades_from_model(con):
    """{自然层No_: 柱等级×10} —— 读源模型的真值，换工程自动跟随。

    ★ 等级的有效字段是 `tblStdFlr.Para` 的下标 4（柱强度×10，300=C30）。
      该字段是 YJK 计算时**真正使用**的；`tblProperty.Name='HNTDJ'` 单独改不生效。
    """
    para = {}
    for sid, p in con.execute("SELECT ID, Para FROM tblStdFlr"):
        parts = str(p or "").split(",")
        if PARA_IDX_COL >= len(parts):
            continue
        try:
            para[sid] = int(float(parts[PARA_IDX_COL].strip()))
        except (TypeError, ValueError):
            continue
    out = {}
    for no, sid in con.execute("SELECT No_, StdFlrID FROM tblFloor"):
        if sid in para:
            out[int(no)] = para[sid]
    return out


def grade_of(floor, zones=None, from_model=None):
    """自然层 -> 柱等级×10。

    ① --zones 显式覆盖；② 源模型现读的真值；③ 都没有则**报错**。
    绝不悄悄套用某个工程的写死分区。
    """
    if zones:
        for lo, hi, g in zones:
            if lo <= floor <= hi:
                return int(str(g).lstrip("Cc")) * 10
        raise SystemExit("--zones 没有覆盖自然层 %s，请补全分区" % floor)
    if from_model and floor in from_model:
        return from_model[floor]
    raise SystemExit(
        "自然层 %s 的柱混凝土等级无法确定：源模型 tblStdFlr.Para[%d] 里读不到，\n"
        "且没有给 --zones。请显式指定，例如 --zones \"1-5:60,6:30\"。"
        % (floor, PARA_IDX_COL))


def parse_zones(spec):
    """把 "1-5:60,6:30" 解析成 [(1,5,'C60'),(6,6,'C30')]。

    ★ 分区不在模块里写死（写死就换不了工程）；用这个开关按工程显式指定。
    """
    out = []
    for part in (spec or "").split(","):
        part = part.strip()
        if not part:
            continue
        seg, _, val = part.partition(":")
        if not val:
            raise SystemExit("--zones 写法有误：%r（应为 自然层:等级，如 6:30）" % part)
        lo, _, hi = seg.partition("-")
        out.append((int(lo), int(hi or lo), "C%s" % str(val).lstrip("Cc")))
    return out


def col_names(con, t):
    return [r[1] for r in con.execute("PRAGMA table_info([%s])" % t)]


# 这些表的 `ID` **不是实体号**，是参数键 / 配置键，不能算进实体号空间。
# ★★ 为什么必须排除
#   `tblProjectPara` 是「键 -> 值」表（字段只有 ID、ParaVal），其 ID 可达
#   五位数（**81199** 这类参数键），远超真实实体号范围。扫全部表求 max(ID)
#   会把新标准层 ID 抬到 8 万级 —— YJK 导入时**丢弃这些行**：标准层被重建、
#   **楼层组装塌掉**（`tblFloor=0`）、自然层没了 → 柱梁板几何全部归零；
#   而 `yjk_importydb` 照样回 OK，`write_sections.py` 自检也全过，直到计算才报
#   「模型中没有单元数据 / 计算分析失败[-45]」。
#   即 `tblProjectPara` **整张表的 ID 都不能参与取号**。
PARA_TABLES = ("tblProjectPara",       # 键->值：最大 81199
               "tblStdFlrPara",        # (StdFlrID,Kind,ParaVal)，无 ID
               "tblChildRaftSeg", "tblCraneLoad", "tblPileInDaisSect",
               "tblSubSectionSect")


def entity_ids(con):
    """收集全模型已用的实体 ID / idNew（跳过参数表与哨兵值）。"""
    ID_LIMIT = 100000
    used_id, used_new = set(), set()
    ts = [r[0] for r in con.execute(
        "SELECT name FROM sqlite_master WHERE type='table'")]
    for t in ts:
        if t in PARA_TABLES:
            continue
        cols = col_names(con, t)
        if "ID" in cols:
            used_id |= {r[0] for r in con.execute("SELECT ID FROM [%s]" % t)
                        if isinstance(r[0], int) and 0 < r[0] < ID_LIMIT}
        if "idNew" in cols:
            used_new |= {r[0] for r in con.execute("SELECT idNew FROM [%s]" % t)
                         if isinstance(r[0], int) and 0 < r[0] != 4294967295}
    return used_id, used_new


def free_low_ids(used, n):
    """取 n 个**最小可用**的正整数 ID。

    ★ 已知的真实约束：
      实体 ID 必须落在模型的真实实体号范围内。若把 `tblProjectPara`
      （键->值表，ID 可达 8 万级）算进实体号扫描，新标准层 ID 会被抬到 8 万级，
      远超真实实体号范围 → YJK 导入时丢弃这些行、
      楼层组装塌掉（`tblFloor=0`）、柱梁板几何全归零。
      所以分配必须基于 `entity_ids()`（已排除参数表）给出的真实范围。

    ⚠️ 这里"挑最小可用"只是为了 ID 单调、贴近 YJK 自己的分配习惯；
      **不要**把"只有首尾标准层留住几何"归因于 ID 大小 —— 那个现象的真因是
      **复制几何行时漏改行内引用**（见第二步半的自检），与 ID 大小无关。
    """
    out, i = [], 1
    while len(out) < n:
        while i in used:
            i += 1
        out.append(i)
        used.add(i)
        i += 1
    return out


def free_ids_between(used, lo, hi, n):
    """在 [lo, hi) 区间里取 n 个最小可用 ID；不够就返回 None。

    ★ 新标准层的 ID 优先落在「**已有标准层 ID 之后、自然层 ID 之前**」这一段：
      这是 YJK 自己的习惯（标准层与自然层按建立顺序交错递增）。区间不够时
      由调用方退回 `free_low_ids()`。
    ⚠️ 不要把"标准层只剩首尾"归因于这里的 ID 取值 —— 真因是行内引用没重映射
      （见第二步半）。
    """
    out, i = [], max(lo, 1)
    while len(out) < n and i < hi:
        if i not in used:
            out.append(i)
            used.add(i)
        i += 1
    return out if len(out) == n else None


def next_ids(con):
    """分配新的 ID / idNew。

    ★ 实体编号空间里不能出现超出实体号范围的值——新分配的 ID 一旦被
    `tblProjectPara` 的参数键带到 8 万级，YJK 导入时会丢弃这些行
    （标准层被重建、楼层组装塌掉）。所以扫描时**只统计实体表**，
    并跳过 `PARA_TABLES` 与 >=100000 的哨兵值，从真实实体 ID 之上继续分配。
    """
    ID_LIMIT = 100000
    used_id, used_new = entity_ids(con)
    nid = max(used_id) + 1
    if nid >= ID_LIMIT:
        raise SystemExit("实体 ID 已接近上限 100000（%d），需要改用更复杂的分配策略" % nid)
    return nid, max(used_new) + 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=SRC_DEFAULT)
    ap.add_argument("--dst", default=DST_DEFAULT)
    ap.add_argument("--mode", choices=("zone", "all"), default="zone")
    ap.add_argument("--zones", default=None,
                    help='自然层->柱等级 分区（紧凑写法 "1-5:60,6:30"）。'
                         '不给则从源模型 tblStdFlr.Para[4] 现读；读不到会报错')
    ap.add_argument("--wall-follow-col", action="store_true",
                    help="墙等级跟随柱（默认：墙保持源模型原值，只改柱）")
    a = ap.parse_args()
    # ★★ 自检必须**变成退出码**：本脚本是纯 CLI，上层（agent / 编排器 / colopt）
    #    只认退出码。老版把下面两条自检的结论只 print 出来、照样以 0 收场 ——
    #    idNewBzc 写错时 YJK 导入会把自然层全丢掉（tblFloor=0、几何全丢），
    #    而调用方看到的是「退出码 0 = 成功」，属于本包最危险的一类误导。
    #    这里统一收集，全部写盘动作做完后再给退出码（文件已落盘，但不算成功）。
    problems = []
    zones = parse_zones(a.zones) if a.zones else None
    if zones:
        print("等级分区（--zones）：%s" % zones)

    if os.path.exists(a.dst):
        os.remove(a.dst)
    shutil.copy2(a.src, a.dst)
    con = sqlite3.connect(a.dst)
    con.text_factory = lambda b: b.decode("gbk", "replace")

    stds = {r[0]: {"no": r[1], "h": r[2], "dead": r[3], "live": r[4],
                   "dpara": r[5], "para": r[6], "idnew": r[7]}
            for r in con.execute("SELECT ID,No_,Height,Dead,Live,DPara,Para,idNew "
                                 "FROM tblStdFlr")}
    floors = [dict(id=r[0], no=r[1], std=r[2], levelb=r[3], h=r[4], idnew=r[5])
              for r in con.execute("SELECT ID,No_,StdFlrID,LevelB,Height,idNew "
                                   "FROM tblFloor ORDER BY No_")]
    print("原模型：%d 个标准层，%d 个自然层" % (len(stds), len(floors)))

    # 等级来源：--zones 优先；否则读源模型真值（换工程自动跟随）
    model_grades = {} if zones else grades_from_model(con)
    if zones:
        print("等级来源：--zones（显式指定）")
    elif model_grades:
        seen = sorted(set(model_grades.values()))
        print("等级来源：源模型 tblStdFlr.Para[%d] 现读（出现 %s）"
              % (PARA_IDX_COL, "、".join("C%d" % (v // 10) for v in seen)))
    else:
        print("等级来源：源模型读不到 —— 若下面报错请用 --zones 显式指定")

    # ---- 规划：每个自然层 -> 目标标准层（沿用原标准层 ID 或新建） ----------------
    nid, nnew = next_ids(con)
    # ★★ 引用重映射必须**按"这一次复制"分开记**，键 = (源标准层, 覆盖的自然层元组)。
    #    {(src, flt): {旧 ID -> 新 ID}} / {(src, flt): {旧 idNew -> 新 idNew}}
    #    若用**全局单张** map（键只有旧 ID/idNew），`--mode all` 下一个源标准层
    #    会分裂成 N 个新标准层，键完全相同 → 反复覆盖，最后只剩**最后一次**复制
    #    （= 最后一个新标准层）的映射。于是所有新标准层的网格/柱段/梁段/楼板
    #    **全部指向最后一个标准层的节点与轴线** → YJK 判定非法引用 → 把中间
    #    的标准层几何**静默丢弃**，只剩第一个（未动过、自洽）和最后一个
    #    （恰好自洽）—— 症状就是"多个标准层只剩首尾"。
    id_map, in_map = {}, {}
    plan = []            # (新标准层ID, 源标准层ID, [自然层号], 是否新建)
    if a.mode == "zone":
        for sid, s in sorted(stds.items(), key=lambda kv: kv[1]["no"]):
            fs = [f["no"] for f in floors if f["std"] == sid]
            grp = collections.OrderedDict()
            for f in fs:
                grp.setdefault(grade_of(f, zones, model_grades), []).append(f)
            for i, (g, fl) in enumerate(grp.items()):
                plan.append((sid if i == 0 else None, sid, fl, i != 0))
    else:
        # ★★ `--mode all` 必须让**每个源标准层的第一个自然层留在原标准层上**。
        #    若"每个自然层都新建标准层"，原标准层会一个自然层都不剩，
        #    进而被清掉 —— 而**删原标准层正是导入塌陷的根因**（见第四步半注释）。
        #    等价于 `--mode zone` 把每个自然层都当成一个分区。
        seen_src = set()
        for f in floors:
            src = f["std"]
            if src not in seen_src:
                seen_src.add(src)
                plan.append((src, src, [f["no"]], False))     # 首个自然层留在原标准层
            else:
                plan.append((None, src, [f["no"]], True))

    # ★ 注意：新建的标准层 `p[0]` 是 None（ID 待分配），所以不能用 set 去重计数 ——
    #   `{p[0] for p in plan if p[3]}` 会塌成 {None}，把"新建 5 个"打印成 1 个。
    created = [p for p in plan if p[3]]
    print("将新建 %d 个标准层（%s 模式）；原有标准层保留"
          % (len(created), a.mode))

    # ---- 第一步：登记所有需要复制的行的 新ID / 新idNew ------------------------
    keys = [(src, tuple(fl)) for _, src, fl, is_new in plan if is_new]
    new_std_ids = {}
    # ★ 标准层的 ID 与 idNew **都**要用「最小可用」值（不是 max+1），见 free_low_ids()：
    #   ID  要早于自然层 ID  —— 否则自然层会被整批丢弃（tblFloor=0）。
    #   idNew 要早于自然层 idNew —— YJK 的 idNew 是按建立顺序分配的：
    #   标准层 -> 自然层 -> 构件，两者紧挨着。若把新标准层 idNew 给成
    #   比自然层**还大**的值，顺序反了 → 导入后柱/梁/板/墙几何
    #   全部塌到最后一个标准层上（每表只剩一个标准层的量）。
    _used_id, _used_new = entity_ids(con)
    # 新标准层 ID 落在「已有标准层 ID 之后、自然层 ID 之前」，保证 ID 单调且早于自然层
    _std_ids = [r[0] for r in con.execute("SELECT ID FROM tblStdFlr")]
    _floor_ids = [r[0] for r in con.execute("SELECT ID FROM tblFloor")]
    _lo = max(_std_ids) + 1 if _std_ids else 1
    _hi = min(_floor_ids) if _floor_ids else _lo + 10000
    _id_pool = free_ids_between(_used_id, _lo, _hi, len(keys))
    if _id_pool is None:
        print("  （标准层 ID 区间 [%d,%d) 不够放 %d 个，退回最小可用）" % (_lo, _hi, len(keys)))
        _id_pool = free_low_ids(_used_id, len(keys))
    _new_pool = free_low_ids(_used_new, len(keys))
    for k, i in zip(keys, _id_pool):
        new_std_ids[k] = i
    print("新建标准层 ID：%s（挑最小可用，须小于自然层 ID）" % dict(new_std_ids))
    print("新建标准层 idNew：%s（挑最小可用，须小于自然层 idNew）"
          % dict(zip((k[1] for k in keys), _new_pool)))

    # ★★ `idNewBzc` 必须记「本次复制对应的那个新标准层」的 idNew —— 不能用 in_map 查！
    #    in_map 是**多对一**的（键 = 源 idNew），而 `--mode all` 下一个源标准层会
    #    分裂成 N 个新标准层，键相同就被反复覆盖，最后只剩**最后一个**值。
    #    后果：所有构件/自然层的 idNewBzc 全写成同一个值（最后一个
    #    标准层的 idNew），与各自的 StdFlrID 对不上 → YJK 导入时**把自然层全部
    #    丢弃**（tblFloor=0），自然层没了 → 楼层组装塌掉 → 连柱梁板几何一起归零，
    #    而 `yjk_importydb` 照样回 OK，要到计算才报
    #    「模型中没有单元数据 / 计算分析失败[-45]」，极难排查。
    #    键必须带上"迁往哪个新标准层"这一维度，所以用 (src, flt) 双键。
    new_std_idnew = {}          # (源标准层ID, 覆盖的自然层元组) -> 新标准层 idNew

    # 计算每条待复制记录的新 ID / idNew
    copies = []          # (table, src_std, floors, old_row, new_id, new_idnew)
    std_rows = {r[0]: r for r in con.execute("SELECT * FROM tblStdFlr")}
    std_cols = col_names(con, "tblStdFlr")
    for ki, (src, flt) in enumerate(keys):
        row = list(std_rows[src])
        new_id = new_std_ids[(src, flt)]
        new_new = _new_pool[ki]                          # 低位 idNew，见上
        id_map.setdefault((src, flt), {})[new_id] = new_id
        new_std_idnew[(src, flt)] = new_new
        copies.append(("tblStdFlr", src, flt, row, new_id, new_new,
                       std_rows[src][std_cols.index("idNew")]))

    for t, spec in SEG_TABLES.items():
        cols = col_names(con, t)
        for src, flt in keys:
            k = (src, flt)
            id_map.setdefault(k, {})
            in_map.setdefault(k, {})
            for r in con.execute("SELECT * FROM [%s] WHERE StdFlrID=?" % t, (src,)):
                row = list(r)
                old_id = row[cols.index("ID")]
                old_new = row[cols.index("idNew")] if "idNew" in cols else None
                new_id, new_new = nid, nnew
                nid += 1
                nnew += 1
                id_map[k][old_id] = new_id            # ★ 按 (src, flt) 分开记，勿用全局键
                if old_new is not None:
                    in_map[k][old_new] = new_new
                copies.append((t, src, flt, row, new_id, new_new, old_new))
        # 属性表：按构件 ID 挂的记录
    prop_cols = col_names(con, "tblProperty")
    for src, flt in keys:
        for t in SEG_TABLES:
            cols = col_names(con, t)
            ids = [r[0] for r in con.execute(
                "SELECT ID FROM [%s] WHERE StdFlrID=?" % t, (src,))]
            for oid in ids:
                for r in con.execute("SELECT * FROM tblProperty WHERE ID=?", (oid,)):
                    row = list(r)
                    copies.append(("tblProperty", src, flt, row, None, nnew, None))
                    nnew += 1

    print("已登记：ID 到 %d，idNew 到 %d，待写入记录 %d 条"
          % (nid, nnew, len(copies)))

    # ---- 第二步：写库 ---------------------------------------------------------
    def remap_val(v, kind, key):
        """把行内引用按**本次复制**的映射表换号；映射表里没有的值原样保留
        （哨兵 4294967295、以及指向共享定义表如 tblColSect 的 idNewDef 等）。"""
        if isinstance(v, int):
            m = id_map.get(key, {}) if kind == "ID" else in_map.get(key, {})
            return m.get(v, v)
        return v

    def remap_list(s, kind, key):
        if not s:
            return s
        out = []
        for x in str(s).split(","):
            x = x.strip()
            if x == "":
                continue
            try:
                out.append(str(remap_val(int(x), kind, key)))
            except ValueError:
                out.append(x)
        return ",".join(out) + ("," if str(s).rstrip().endswith(",") else "")

    ins = collections.Counter()
    for t, src, flt, row, new_id, new_new, old_new in copies:
        cols = col_names(con, t)
        r = list(row)
        k = (src, flt)                       # ★ 本次复制对应的映射表键
        if "ID" in cols and new_id is not None:
            r[cols.index("ID")] = new_id
        if "idNew" in cols:
            r[cols.index("idNew")] = new_new
        spec = SEG_TABLES.get(t, {})
        for c in spec.get("refs_id", []):
            if c in cols:
                r[cols.index(c)] = remap_val(r[cols.index(c)], "ID", k)
        for c in spec.get("refs_new", []):
            if c in cols:
                r[cols.index(c)] = remap_val(r[cols.index(c)], "idNew", k)
        for c, kind in spec.get("lists", []):
            if c in cols:
                r[cols.index(c)] = remap_list(r[cols.index(c)], kind, k)
        if t in ("tblStdFlr",) or "StdFlrID" in cols:
            if t == "tblStdFlr":
                r[cols.index("No_")] = 0                      # 稍后统一重排
                new_std_id = new_id
            else:
                new_std_id = new_std_ids[(src, flt)]
                r[cols.index("StdFlrID")] = new_std_id
        for c in BZC_COLS:
            if c in cols:
                # ★ 必须按 (src, flt) 取，取不到才退回原值（见上面 new_std_idnew 的注释：
                #   用 in_map 查会把所有行写成同一个（最后一个）标准层的 idNew）
                r[cols.index(c)] = new_std_idnew.get((src, flt),
                                                     r[cols.index(c)])
        con.execute("INSERT INTO [%s] (%s) VALUES (%s)"
                    % (t, ",".join("[%s]" % c for c in cols),
                       ",".join("?" * len(cols))), r)
        ins[t] += 1
    print("已写入：%s" % dict(ins))

    # ---- 第二步半：引用自检（本脚本最关键的一道闸） ---------------------------
    # ★★ 为什么必须有这道闸
    #   复制几何行时只改行自身的 ID/idNew 是不够的，**行内引用**也必须按本次复制
    #   重映射。漏掉时 YJK 的表现是"静默丢几何"：import 回 OK、save 正常落盘、
    #   逐表计数在 .ydb 里全对，但导入后的 Model.ymd 里只有**第一个和最后一个**
    #   标准层还剩柱/梁/板，中间的全空 → 计算跑很久后才报
    #   「模型中没有单元数据 / 计算分析失败[-45]」。
    #   这里直接把"引用的 idNew 是否属于同一标准层"验一遍，几秒钟就能定位。
    owner_new, owner_id = {}, {}                 # idNew / ID -> StdFlrID
    for t in SEG_TABLES:
        cols = col_names(con, t)
        if "StdFlrID" not in cols:
            continue
        if "idNew" in cols:
            for v, sid in con.execute("SELECT idNew, StdFlrID FROM [%s]" % t):
                if isinstance(v, int):
                    owner_new[v] = sid
        if "ID" in cols:
            for v, sid in con.execute("SELECT ID, StdFlrID FROM [%s]" % t):
                if isinstance(v, int):
                    owner_id[v] = sid

    def _scan(con, t, c, own, sep):
        """逐行核对 t.c 里的引用是否都落在本行所属标准层内。"""
        cols = col_names(con, t)
        if c not in cols:
            return []
        out = []
        for sid, s in con.execute(
                "SELECT StdFlrID, [%s] FROM [%s] WHERE [%s] IS NOT NULL" % (c, t, c)):
            for x in str(s).split(sep):
                x = x.strip()
                if not x.isdigit():
                    continue
                v = int(x)
                if v in (0, 4294967295):
                    continue
                if own.get(v) != sid:
                    out.append("%s.%s 含 %d（属标准层 %s）但本行属标准层 %s"
                               % (t, c, v, own.get(v), sid))
                    break
        return out

    bad = []
    for tgt_map, own, sep in ((REF_TARGET_NEW, owner_new, None),
                              (REF_TARGET_ID, owner_id, None),
                              (LIST_TARGET_NEW, owner_new, ","),
                              (LIST_TARGET_ID, owner_id, ",")):
        for (t, c), tgt in sorted(tgt_map.items()):
            if tgt not in SEG_TABLES:
                continue
            bad += _scan(con, t, c, own, sep if sep else "\x00")
    if bad:
        print("!! 引用自检不通过：%d 处跨标准层引用（样例 5 条）" % len(bad))
        for b in bad[:5]:
            print("     ", b)
        raise SystemExit(1)
    print("引用自检通过：各标准层的节点/轴线/网格/构件引用均自洽")

    # ---- 第三步：把迁走的自然层指向新标准层 -----------------------------------
    for _, src, fl, is_new in plan:
        if not is_new:
            continue
        new_sid = new_std_ids[(src, tuple(fl))]
        new_sidnew = new_std_idnew[(src, tuple(fl))]
        for f in fl:
            # StdFlrID -> 标准层的 **ID**；idNewBzc -> 标准层的 **idNew**（两个不同的键，
            # 见 工程_00/Model.ymd 实证：ID=1001 / idNew=2 时，floor 写的就是
            # StdFlrID=1001 且 idNewBzc=2）
            con.execute("UPDATE tblFloor SET StdFlrID=?, idNewBzc=? WHERE No_=?",
                        (new_sid, new_sidnew, f))
    # 新标准层的层高/恒活按它覆盖的最后一层（自然层实际层高可不同，取首层）
    for _, src, fl, is_new in plan:
        if not is_new:
            continue
        new_sid = new_std_ids[(src, tuple(fl))]
        h = [f["h"] for f in floors if f["no"] == fl[0]][0]
        con.execute("UPDATE tblStdFlr SET Height=? WHERE ID=?", (h, new_sid))

    # ---- 第三步半：整套复制 tblStdFlrPara ------------------------------------
    # ★ 为什么必须整套复制（不只是要改的那 4 个 Kind）
    #   `tblStdFlrPara` 是"每标准层一套"的等级表，共 26 个 Kind（0..25）。
    #   第四步只会写 板/柱/梁/墙 = Kind 2/4/5/6 这 4 个；若只靠它，
    #   新标准层就只有 4 行，其余 22 个 Kind 缺失。
    #   YJK 导入时会自己补齐到 26 行，**但补的是它自己的默认值**，
    #   等于把梁/板/墙之外的参数（保护层、钢筋级别等）悄悄改成默认 —— 静默偏差。
    #   直接从源标准层整套复制最稳。
    n_para = 0
    para_zero = []                       # 复制到 0 行的新标准层（"每层一套"变成空话）
    for _, src, fl, is_new in plan:
        if not is_new:
            continue
        new_sid = new_std_ids[(src, tuple(fl))]
        con.execute(
            "INSERT INTO tblStdFlrPara (StdFlrID, Kind, ParaVal) "
            "SELECT ?, Kind, ParaVal FROM tblStdFlrPara WHERE StdFlrID=?",
            (new_sid, src))
        one = con.execute("SELECT count(*) FROM tblStdFlrPara WHERE StdFlrID=?",
                          (new_sid,)).fetchone()[0]
        n_para += one
        # ★ 老版只报**跨所有新标准层的总和**：某个新层复制到 0 行时总额仍可能 > 0，
        #   于是打印的"每标准层一套 26 个 Kind"在说谎，而该层的参数会被 YJK
        #   用它自己的默认值补齐（保护层/钢筋级别静默偏离）。
        if not one:
            para_zero.append((src, new_sid))
    if n_para:
        print("复制 tblStdFlrPara：%d 行（每标准层一套 26 个 Kind）" % n_para)
    if para_zero:
        print("!! 这些新标准层一行 tblStdFlrPara 都没复制到：%s"
              % ["源标准层%d→新ID%d" % (s, i) for s, i in para_zero[:6]])
        print("   后果：该层的等级/保护层/钢筋级别会被 YJK 用自己的默认值补齐，"
              "参数静默偏离。")
        problems.append("%d 个新标准层没复制到任何 tblStdFlrPara 行（%s）—— "
                        "来源标准层的展开表本来就是空的？"
                        % (len(para_zero), ["源%d" % s for s, _ in para_zero[:6]]))

    # ---- 第四步：给每个标准层写正确的等级（板/柱/梁/墙 = idx 2/4/5/6） --------
    std_of_floor = {}
    for r in con.execute("SELECT No_,StdFlrID FROM tblFloor"):
        std_of_floor[r[0]] = r[1]
    floor_of_std = collections.defaultdict(list)
    for f, sid in std_of_floor.items():
        floor_of_std[sid].append(f)

    def set_grade(para, idx, val):
        p = (para or "").split(",")
        while len(p) <= idx:
            p.append("")
        p[idx] = str(val)
        return ",".join(p)

    # ★ 只改「柱」等级（idx 4），板/梁/墙**保持源模型原值**。
    #   不把 板/梁 强制写成 C30、也不把墙写成与柱同等级 —— 那样换工程会把
    #   板/梁等级悄悄改错。需要墙跟着柱走时显式加 `--wall-follow-col`。
    wrote = 0
    for sid, fs in floor_of_std.items():
        if not fs:
            continue
        g = grade_of(min(fs), zones, model_grades)
        row = con.execute("SELECT Para,No_ FROM tblStdFlr WHERE ID=?", (sid,)).fetchone()
        if row is None:
            continue
        para, no_ = row
        para = set_grade(para, PARA_IDX_COL, g)
        if a.wall_follow_col:
            para = set_grade(para, 6, g)
        con.execute("UPDATE tblStdFlr SET Para=? WHERE ID=?", (para, sid))
        # tblStdFlrPara 同步（该表是 Para 的展开表，Kind = 下标）
        kinds = {r[0] for r in con.execute(
            "SELECT Kind FROM tblStdFlrPara WHERE StdFlrID=?", (sid,))}
        upd = [(PARA_IDX_COL, g)] + ([(6, g)] if a.wall_follow_col else [])
        for kind, val in upd:
            if kind in kinds:
                con.execute("UPDATE tblStdFlrPara SET ParaVal=? "
                            "WHERE StdFlrID=? AND Kind=?", (val, sid, kind))
            else:
                con.execute("INSERT INTO tblStdFlrPara (StdFlrID,Kind,ParaVal) "
                            "VALUES (?,?,?)", (sid, kind, val))
        wrote += 1
    if wrote:
        print("第四步：写入 %d 个标准层的柱等级（idx %d）%s"
              % (wrote, PARA_IDX_COL,
                 "，墙同步" if a.wall_follow_col else "；板/梁/墙保持源模型原值"))
    else:
        # ★ 老版对 `wrote == 0`（一个标准层的等级都没写）不加 `else`、不报错，
        #   直接进第五步 —— 与"全部写成功"在下游完全同形。
        print("!! 第四步：**一个标准层的柱等级都没写** —— tblFloor 为空？")
        print("   后果：模型里一层等级都没改，实算仍按原等级，"
              "看起来像「优化了但没效果」。")
        problems.append("第四步柱等级写入 **0** 个标准层（tblFloor 为空或 StdFlrID 悬空？）")

    # ---- 第四步半：无自然层的空标准层 —— **只警告，不删除** -------------------
    # ★★ 绝对不要删原标准层
    #   把"没有自然层"的标准层连几何一起 DELETE 掉的后果：YJK 导入后
    #   **自然层全部丢失**（`tblFloor=0`）、
    #   柱/梁/板/墙几何全部归零（每表只剩一个标准层的量），而
    #   `yjk_importydb` 照样回 OK，`write_sections.py` 自检也全过 ——
    #   直到计算才报「模型中没有单元数据 / 计算分析失败[-45]」。
    #   所以 `--mode all` 已改成"首个自然层留在原标准层上"，本步骤正常应为空。
    #   万一真出现，也**只把 No_ 挪到后面**避免与新建标准层撞号（撞号会让
    #   `write_sections.py` 把截面写到错误的层），绝不删除。
    used_std = set(std_of_floor.values())
    dead = [r[0] for r in con.execute("SELECT ID FROM tblStdFlr")
            if r[0] not in used_std]
    if dead:
        max_no = con.execute("SELECT max(No_) FROM tblStdFlr").fetchone()[0] or 0
        for i, sid in enumerate(dead, start=1):
            con.execute("UPDATE tblStdFlr SET No_=? WHERE ID=?", (max_no + i, sid))
        con.commit()
        print("!! 有 %d 个标准层没有自然层（ID %s）：已把它们的 No_ 挪到 %s 之后以避免撞号，"
              "**未删除**。" % (len(dead), ",".join(str(x) for x in dead), max_no))
        print("   正常流程（--mode zone / --mode all）不会出现；若出现请检查 --zones 设置。")
        # ★ 这条同样是「输入没覆盖全模型」的信号：脚本会自动挪号，但模型里多出了
        #   一个没有自然层的空标准层，且层号被改过 —— 不该让调用方以为一切正常。
        problems.append("有 %d 个标准层没有自然层（ID %s），已自动挪号"
                        "（模型里留了一个空标准层）—— 请检查 --zones/--mode 设置"
                        % (len(dead), ",".join(str(x) for x in dead)))

    # ---- 第五步：标准层按标高重排 No_ 1..N -----------------------------------
    rows = list(con.execute(
        "SELECT s.ID, MIN(f.LevelB) lb FROM tblStdFlr s "
        "JOIN tblFloor f ON f.StdFlrID=s.ID GROUP BY s.ID ORDER BY lb"))
    # ★ 这条 JOIN 在 `tblFloor` 为空（或 `tblFloor.StdFlrID` 全是悬空值）时返回空集，
    #   老版于是"循环体一次都不执行、无任何提示"，随后照常打印各层**旧** No_ ——
    #   而 No_ 正是 write_sections.py 定位柱段的键（WHERE StdFlrID=? AND No_=?），
    #   层号没重排过就会把截面写到错误的层上。
    if not rows:
        print("\n!! 第五步：**没有任何标准层参与 No_ 重排** —— "
              "tblFloor 为空，或它的 StdFlrID 全部悬空。")
        print("   No_ 是下游写截面/取结果时的层定位键：层号没排过，"
              "write_sections.py 会把柱截面写到错误的层上。")
        problems.append("第五步 No_ 重排 0 个标准层（tblFloor 为空或 StdFlrID 悬空）")
    for i, (sid, _) in enumerate(rows, start=1):
        con.execute("UPDATE tblStdFlr SET No_=? WHERE ID=?", (i, sid))
    # 读回校验：重排之后必须恰好是 1..N（写号和读回是两件事）
    if rows:
        nos = sorted(r[0] for r in con.execute("SELECT No_ FROM tblStdFlr"))
        n_std = con.execute("SELECT count(*) FROM tblStdFlr").fetchone()[0]
        if nos != list(range(1, n_std + 1)):
            print("\n!! 第五步读回校验：tblStdFlr.No_ 不是 1..%d，实际 %s%s"
                  % (n_std, nos[:20], "…" if len(nos) > 20 else ""))
            print("   层号有重号或断号 —— 下游按 No_ 定位会写错层。")
            problems.append("tblStdFlr.No_ 重排后不是 1..%d（实际 %s）—— 层号重号/断号"
                            % (n_std, nos[:20]))
    con.commit()

    # ---- 校验 ---------------------------------------------------------------
    print("\n拆分后：%d 个标准层" % con.execute(
        "SELECT COUNT(*) FROM tblStdFlr").fetchone()[0])
    print("%-5s %-8s %-26s %-6s %s"
          % ("标准层", "ID", "覆盖自然层", "层高", "板/柱/梁/墙 等级×10"))
    for sid, no in con.execute("SELECT ID,No_ FROM tblStdFlr ORDER BY No_"):
        fs = sorted(f for f, s in std_of_floor.items() if s == sid)
        row = con.execute("SELECT Height,Para FROM tblStdFlr WHERE ID=?", (sid,)).fetchone()
        p = (row[1] or "").split(",")
        g = [p[i] if i < len(p) else "?" for i in (2, 4, 5, 6)]
        # ★ 空覆盖是**正常**的：--mode all 下所有自然层都迁到新标准层，
        #   原标准层会剩 0 个自然层（脚本刻意"只新增、不删除"）。
        #   直接取 fs[0]/fs[-1] 会 IndexError 崩在这里，
        #   而那时模型**已经写好了**——极易被误判成"拆分失败"。
        cover = "%s-%s (%d层)" % (fs[0], fs[-1], len(fs)) if fs else "（无自然层，空转）"
        print("%-5s %-8s %-26s %-6s %s" % (no, sid, cover, row[0], "/".join(g)))
    print("\n柱截面分布（应保持与原标准层一致）：")
    d = collections.defaultdict(collections.Counter)
    sects = {r[0]: r[1] for r in con.execute("SELECT ID,ShapeVal FROM tblColSect")}
    for seg in con.execute("SELECT StdFlrID,SectID FROM tblColSeg"):
        sv = (sects.get(seg[1]) or "").split(",")
        d[seg[0]]["%s×%s" % (sv[1], sv[2]) if len(sv) > 2 else "?"] += 1
    for sid, no in con.execute("SELECT ID,No_ FROM tblStdFlr ORDER BY No_"):
        print("   标准层%-3s %s" % (no, dict(d[sid])))
    # ---- 校验：idNewBzc 必须逐行等于它所属标准层的 idNew ---------------------
    # ★★ 这条**必须**查。idNewBzc 写错时本脚本不报错、`write_sections.py` 不报错、
    #    `yjk_importydb` 还回 OK——只有导入后 `tblFloor=0`（自然层全被丢）才会暴露，
    #    而那时要等到计算才报「模型中没有单元数据 / 计算分析失败[-45]」。
    #    一旦所有行 idNewBzc 全被写成同一个值（最后一个
    #    标准层的 idNew），与各自的 StdFlrID 对不上，整栋模型全部归零。
    bad_bzc = []
    bzc_blind = []                    # StdFlrID 悬空 → INNER JOIN 看不到的行
    bzc_empty = []                    # 一行都没有的表：这条自检对它们恒真
    for t in ("tblFloor", "tblAxis", "tblGrid", "tblColSeg", "tblBeamSeg",
              "tblWallSeg", "tblWallHole", "tblSlab", "tblLoadSeg"):
        cols = col_names(con, t)
        if "idNewBzc" not in cols or "StdFlrID" not in cols:
            continue
        n = con.execute(
            "SELECT count(*) FROM [%s] x JOIN tblStdFlr s ON s.ID = x.StdFlrID "
            "WHERE x.idNewBzc <> s.idNew" % t).fetchone()[0]
        tot = con.execute("SELECT count(*) FROM [%s]" % t).fetchone()[0]
        joined = con.execute(
            "SELECT count(*) FROM [%s] x JOIN tblStdFlr s ON s.ID = x.StdFlrID"
            % t).fetchone()[0]
        if n:
            bad_bzc.append("%s %d/%d 行" % (t, n, tot))
        if not tot:
            # ★ 空集恒真：`tblFloor` 为空**正是这条自检要防的塌陷症状**，
            #   而 INNER JOIN 在空集上恒得 0 → 老版会打印成功的 ✓/[OK]。
            bzc_empty.append(t)
            continue
        if joined < tot:
            bzc_blind.append("%s %d/%d 行" % (t, tot - joined, tot))
    if bad_bzc:
        print("\n!! idNewBzc 与所属标准层的 idNew 不一致：%s" % "，".join(bad_bzc))
        print("   后果：YJK 导入时丢弃自然层（tblFloor=0）→ 楼层组装塌掉 → 几何全丢。")
        problems.append("idNewBzc 与所属标准层的 idNew 不一致：%s（YJK 导入会丢自然层）"
                        % "，".join(bad_bzc))
    if bzc_blind:
        print("\n!! idNewBzc 自检**覆盖不到**这些行（StdFlrID 在 tblStdFlr 里找不到）：%s"
              % "，".join(bzc_blind))
        print("   本自检用的是 INNER JOIN，引用悬空的行被整批排除在比较之外 —— "
              "它们同样会让 YJK 丢自然层/丢几何。")
        problems.append("idNewBzc 自检覆盖不到 %s（StdFlrID 悬空）"
                        % "，".join(bzc_blind))
    if bzc_empty:
        print("\n!! 这些表**一行都没有**，idNewBzc 自检对它们恒真（恒等于通过）：%s"
              % "，".join(bzc_empty))
        if "tblFloor" in bzc_empty:
            print("   tblFloor = 0 是**楼层组装塌掉**的症状（自然层全丢）："
                  "导入后柱/梁/板/墙几何一起归零，\n"
                  "   而 yjk_importydb 照样回 OK，要到计算才报"
                  "「模型中没有单元数据 / 计算分析失败[-45]」。")
            problems.append("tblFloor 为 0 行（自然层全丢）—— idNewBzc 自检对空表恒真，"
                            "老版会在这里打印「全部一致」")
    # ★ 只要 `tblFloor` 为空，这条自检就**没有真正核过任何东西**，不能打印成功字样。
    #   （其余表（tblWallSeg/tblLoadSeg…）为空的场合是正常的，那时照旧打印。）
    if not bad_bzc and not bzc_blind and "tblFloor" not in bzc_empty:
        print("\nidNewBzc 自检：全部与所属标准层的 idNew 一致 [OK]")

    print("\nintegrity_check: %s" % con.execute("PRAGMA integrity_check").fetchone()[0])
    con.close()
    print("-> %s" % a.dst)
    if problems:
        print("\n!! 本次**没有全部通过自检**（退出码 1）—— 逐条：")
        for p in problems:
            print("   · %s" % p)
        print("   （磁盘上的 %s 已写出；请修正输入后重跑，**不要**直接拿去导入/计算）"
              % a.dst)
        sys.exit(1)
    print("完成。")


def _utf8_console():
    """让输出在任何控制台编码下都不崩（GBK 下把不可编码字符替换掉）。

    为什么需要：本包会打印 ✅ ❌ ⚠ −(U+2212) ² ³ 等**非 cp936** 字符，
    默认 GBK 控制台下 print 会抛 UnicodeEncodeError 并**以退出码 1 中断**，
    于是一个其实已经成功的任务（比如文件已经落盘）会被上层判成失败。
    errors=replace 让它在 UTF-8 控制台下原样输出、在 GBK 下退化成 ?，都不崩。

    ★ 只在真正的 CLI 入口调用：本文件会被别人 import 当库用，
      在模块顶层无条件改 stdout 会污染 import 它的进程。
    """
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(errors="replace")
        except Exception:
            pass


if __name__ == "__main__":
    _utf8_console()
    main()
