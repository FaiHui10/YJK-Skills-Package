# -*- coding: utf-8 -*-
r"""把「混凝土等级」与「优化柱截面」写回 YJK 模型库(.ydb/.ymd)。

两个关键点：

1) 逐层混凝土等级的**有效字段**是 `tblStdFlr.Para`（逗号串）下标 2/4/5/6
   = 板/柱/梁/墙 强度×10（300 = C30）。
   `tblStdFlrPara(StdFlrID,Kind,ParaVal)` 只是它的展开表。
   `tblProperty` 里 Name='HNTDJ' 的行（每构件一条，ShapeVal=-等级）
   **单独改它不影响计算**：只改 HNTDJ 时 YJK 仍按原等级算 ——
   由 `fc = Nu*1000/(b*h*Uc)` 反算即可看出（比值 ≈ 强度比）。三个字段一起改才稳妥。

2) 「柱段→截面」的**有效外键**是 `tblColSeg.idNewDef` → `tblColSect.idNew`。
   `tblColSeg.SectID` 在 yjk_importydb 时被完全无视（只改 SectID 会整体回退）。
   详见 set_sections() 的 docstring。

用法：
  python write_sections.py <src> <dst> [--grade] [--sections 优化截面清单.json]
                          [--grades "1-3:60,4-5:50,6:45,7:40"]
  两者都不给时只做拷贝。
"""
import argparse
import collections
import json
import os
import shutil
import sqlite3
import sys

# tblStdFlr.Para 里 板/柱/梁/墙 的强度×10 所在下标（主用字段）
PARA_IDX = (2, 4, 5, 6)

# ★ 这里**不内置任何工程的等级表**：内置默认表换工程后会让等级全错却不报错。
#   不给 --grades 就**保持模型现有等级不变**。

# 这些表的 `ID` **不是实体号**，是参数键 / 配置键，不能算进实体号空间。
# ★★ 为什么必须排除：`tblProjectPara` 是「键 -> 值」表，
#    ID 最大可达 81199（还有 100000 哨兵）。若把它算进去，新号会跑到 8 万级，
#    远超真实实体号范围，YJK 导入时直接丢弃这些行。
PARA_TABLES = ("tblProjectPara",        # 键->值：最大 81199
               "tblStdFlrPara",         # (StdFlrID,Kind,ParaVal)，无 ID 列
               "tblChildRaftSeg", "tblCraneLoad", "tblPileInDaisSect",
               "tblSubSectionSect")
ID_LIMIT = 100000
SENTINEL = 4294967295

# 这些表的 idNew 不参与「idNew -> 实体」的全局解析，撞号是**正常现象**
# （YJK 自己建的模型里 tblProperty 就有重复 idNew）。
IDNEW_EXEMPT = ("tblProperty",)


def entity_ids(con):
    """收集**全模型**已用的实体 ID / idNew（跳过参数表与哨兵值）。

    ★★ 为什么新截面取号必须全局扫描
    ------------------------------------------------------------
    新建 `tblColSect` 行时若只按 `max(tblColSect.idNew)+1` 取号，很容易撞上
    别的表已经用掉的 idNew（例如 `tblBeamSeg` 占用的号段，恰好被新截面拿到）。
    后果：YJK 导入时按 idNew 去重 / 别名，**柱段 → 截面的映射整体错乱** →
    **大批柱被静默丢弃**。FE 里单元数只剩梁，
    计算报「刚度矩阵不定 / 节点缺少约束」→ 分析失败[-1]。
    而 `yjk_importydb` 照样回 OK(0.5s)、save 也正常落盘、`check_sections()`
    自检还全过 —— 极难排查。所以取号必须基于**全模型实体 idNew 的最大值**。
    """
    used_id, used_new = set(), set()
    for (t,) in con.execute("SELECT name FROM sqlite_master WHERE type='table'"):
        if t in PARA_TABLES:
            continue
        cols = [c[1] for c in con.execute("PRAGMA table_info([%s])" % t)]
        if "ID" in cols:
            used_id |= {r[0] for r in con.execute("SELECT ID FROM [%s]" % t)
                        if isinstance(r[0], int) and 0 < r[0] < ID_LIMIT}
        if "idNew" in cols:
            used_new |= {r[0] for r in con.execute("SELECT idNew FROM [%s]" % t)
                         if isinstance(r[0], int) and 0 < r[0] != SENTINEL}
    return used_id, used_new


def check_idnew_global(con, verbose=True):
    """全模型 idNew 唯一性自检。撞号会让 YJK 静默丢构件，必须当硬错误。

    判据：同一个 idNew 被 **两张及以上「非豁免表」** 的行使用，或在同一张
    非豁免表里出现多次 → 有害。只被豁免表（见 `IDNEW_EXEMPT`）用到则不算。
    返回有害的撞号列表。
    """
    tabs_using = collections.defaultdict(set)      # idNew -> 用到它的表集合
    bad_rows = collections.Counter()               # idNew -> 非豁免表的行数
    for (t,) in con.execute("SELECT name FROM sqlite_master WHERE type='table'"):
        if t in PARA_TABLES:
            continue
        cols = [c[1] for c in con.execute("PRAGMA table_info([%s])" % t)]
        if "idNew" not in cols:
            continue
        for (v,) in con.execute("SELECT idNew FROM [%s]" % t):
            if isinstance(v, int) and 0 < v != SENTINEL:
                tabs_using[v].add(t)
                if t not in IDNEW_EXEMPT:
                    bad_rows[v] += 1
    dup = sorted(v for v, n in bad_rows.items() if n > 1)
    exempt = sorted(v for v in tabs_using if not bad_rows.get(v))
    if verbose:
        print("    全局 idNew 自检：有害撞号 %d 个 %s；豁免表(%s)内撞号 %d 个 %s"
              % (len(dup), dup[:10] if dup else "",
                 "/".join(IDNEW_EXEMPT), len(exempt), exempt[:5] if exempt else ""))
    return dup


def parse_grades(spec):
    """解析等级写法，返回 {标准层: 等级数字}。

    支持两种写法：
      "1-3:60,4-5:50,6:45,7:40"            （紧凑，段用逗号，区间用短横线）
      '{"1":60,"2":60,"4":50}'             （JSON 对象；值可为 60 / "C60" / "c60"）
    """
    spec = (spec or "").strip()
    if not spec:
        return {}
    if spec.startswith("{"):
        raw = json.loads(spec)
    else:
        raw = {}
        for part in spec.split(","):
            part = part.strip()
            if not part:
                continue
            seg, _, val = part.partition(":")
            if not val:
                raise SystemExit("等级写法有误：%r（应为 标准层:等级，如 4-5:50）" % part)
            v = int(str(val).lstrip("Cc"))
            if "-" in seg:
                a, b = seg.split("-", 1)
                for i in range(int(a), int(b) + 1):
                    raw[str(i)] = v
            else:
                raw[str(seg)] = v
    out = {}
    for k, v in raw.items():
        out[int(k)] = int(str(v).lstrip("Cc"))
    return out


def _die(msg):
    """「工具没跑成」→ **退出码 2**（与"跑完了但没写全/校验不过"的 1 分开）。"""
    try:
        sys.stderr.reconfigure(errors="replace")   # GBK 控制台下也不崩
    except (AttributeError, ValueError):
        pass
    sys.stderr.write(msg.rstrip("\n") + "\n")
    sys.exit(2)


def open_rw(path):
    """以**可写**方式打开目标模型库；坏输入给中文报错，**绝不新建一个空库**。

    ★★ 为什么必须守卫：`sqlite3.connect(path)` 默认是 **rw**，对一个**不存在**的
      路径会**先把它建出来**（0 字节空库），然后在第一条查询上抛
      `no such table: tblStdFlr` —— 比"文件不存在"更难查（盘上多了个假库）。
      另外 0 字节/非 sqlite 的文件 connect 也是**成功**的，报错同样推迟。
      `main()` 已经先 `shutil.copy2(src, dst)`，所以正常路径下这里必然通过。
    """
    p = os.path.abspath(str(path))
    if not os.path.exists(p):
        _die("目标模型库不存在：%s\n"
             "  （本脚本先按 src 复制出 dst，这一步没成功就不会开写）" % p)
    if os.path.isdir(p):
        _die("目标路径是目录，不是模型库文件：%s" % p)
    if os.path.getsize(p) == 0:
        _die("目标模型库是 0 字节（复制不完整/源库是半写的）：%s" % p)
    try:
        con = sqlite3.connect(p)
        con.execute("PRAGMA schema_version").fetchone()   # 把"不是数据库"提前探出来
    except sqlite3.Error as e:
        _die("打不开目标模型库 %s：%s\n"
             "  常见原因：不是 sqlite 库（拿错文件）/ 库已损坏。" % (p, e))
    con.text_factory = lambda b: b.decode("gbk", "replace")
    return con


def set_grades(con, grade_map=None, verbose=True):
    """按标准层写入混凝土等级。

    真正起作用的是 `tblStdFlr.Para`（逗号分隔文本）下标 2/4/5/6 = 板/柱/梁/墙
    强度×10（300 = C30）——实算复核已证：只改 tblProperty.HNTDJ 不影响计算结果，
    YJK 仍按原等级算（由 `fc = Nu*1000/(b*h*Uc)` 反算即可看出）。
    `tblStdFlrPara`(Kind=下标, ParaVal) 是 Para 的展开表，一并改写。

    参数 grade_map：{标准层No_: 等级数字}；**不给则保持模型现有等级不变**
    （不套用任何工程的写死默认表）。

    ★★ 返回 dict（调用方**必须判定**，不能丢掉 —— 老版丢掉了三个自检的返回值，
       于是"一层都没写"照样打印"完成。"+ rc 0）：
         {"HNTDJ": 行数, "Para": 行数, "ParaVal": 行数,
          "缺标准层": [等级表里有、模型里没有的标准层],
          "Para 缺下标": [Para 字段放不下 板/柱/梁/墙 四个下标的层]}
    ★ 行数一律用 **rowcount**（真命中行数），不是"我执行了几条语句"。
    """
    if not grade_map:
        if verbose:
            print("    （未指定 --grades：保持模型现有混凝土等级不变）")
        return {"HNTDJ": 0, "Para": 0, "ParaVal": 0, "缺标准层": [], "Para 缺下标": []}
    G = dict(grade_map)
    flr = {r[0]: r[1] for r in con.execute("SELECT ID,No_ FROM tblStdFlr")}
    missing = sorted(set(G) - set(flr.values()))     # 等级表里的层，模型里没有
    std_of = {}          # 构件段ID -> 标准层No_
    for t in ("tblColSeg", "tblBeamSeg", "tblWallSeg"):
        try:
            for sid, fid in con.execute("SELECT ID,StdFlrID FROM %s" % t):
                std_of[sid] = flr.get(fid)
        except sqlite3.OperationalError:
            pass
    n = 0
    for pid, in con.execute("SELECT ID FROM tblProperty WHERE Name='HNTDJ'"):
        std = std_of.get(pid)
        if std is None or std not in G:
            continue
        cur = con.execute("UPDATE tblProperty SET ShapeVal=? WHERE ID=? AND Name='HNTDJ'",
                          ("-%d.000000" % G[std], pid))
        n += cur.rowcount          # ★ rowcount：命中 0 行不能算"改写了 1 行"
    # ---- 主用字段：tblStdFlr.Para[2,4,5,6] ----
    k = 0
    short = []                     # Para 字段不够长 → 该层等级**没写全**
    for fid, std in flr.items():
        if std not in G:
            continue
        row = con.execute("SELECT Para FROM tblStdFlr WHERE ID=?", (fid,)).fetchone()
        if not row or row[0] is None:
            short.append(std)
            continue
        parts = str(row[0]).split(",")
        if any(i >= len(parts) for i in PARA_IDX):
            # ★ 老版把"字段不存在"当成"不用改"，还照样 +1 报"改写 1 行"。
            #   下标 2/4/5/6 里缺任何一个，这一层的等级就没写全（Para 才是计算真正用的字段）。
            short.append(std)
        for i in PARA_IDX:
            if i < len(parts):
                parts[i] = str(G[std] * 10)
        cur = con.execute("UPDATE tblStdFlr SET Para=? WHERE ID=?", (",".join(parts), fid))
        k += cur.rowcount          # ★ rowcount：列全缺时这条 UPDATE 其实什么也没改
    # ---- 展开表 tblStdFlrPara ----
    # ★ 这里用 `rowcount` 是对的，但"改了几行"不等于"该改的都改了"：
    #   展开表里某个 Kind 的行**本来就不存在**时，`UPDATE` 命中 0 行、老版照样报
    #   "tblStdFlrPara 改写 N 行" —— 于是 tblStdFlr.Para（计算真正用的字段）与展开表
    #   **不一致**，属于"写了一半却报成功"。对照 split_stdflr.py:612（缺 Kind 就 INSERT），
    #   这里只改不补，所以必须把"缺哪一行"点名报出来。
    m = 0
    miss_kind = []                 # (标准层No_, Kind)：展开表里没有这一行
    n_target = len([1 for s in flr.values() if s in G])
    for fid, std in flr.items():
        if std not in G:
            continue
        for kind in PARA_IDX:
            cur = con.execute("UPDATE tblStdFlrPara SET ParaVal=? WHERE StdFlrID=? AND Kind=?",
                              (G[std] * 10, fid, kind))
            m += cur.rowcount
            if cur.rowcount == 0:
                miss_kind.append((std, kind))
    if verbose:
        print("    HNTDJ 改写 %d 行；tblStdFlr.Para 改写 %d 行；tblStdFlrPara 改写 %d 行"
              % (n, k, m))
        if missing:
            print("    !! 等级表里这些标准层**不在模型中**，该层等级一个都没改：%s"
                  % ", ".join(str(x) for x in missing))
        if short:
            print("    !! 这些标准层的 tblStdFlr.Para 字段放不下 板/柱/梁/墙 下标"
                  "（该层等级没写全）：%s" % ", ".join(str(x) for x in short))
        if miss_kind:
            print("    !! tblStdFlrPara 里这些 (标准层, Kind) 行**不存在**（只改不补）→"
                  " 展开表与 tblStdFlr.Para 不一致：应改 %d 行、实际只改了 %d 行；%s"
                  % (n_target * len(PARA_IDX), m, miss_kind[:8]))
    return {"HNTDJ": n, "Para": k, "ParaVal": m, "缺标准层": missing,
            "Para 缺下标": short, "缺 Kind": miss_kind,
            "应改行数": n_target * len(PARA_IDX)}


def set_sections(con, spec_path, verbose=True):
    """按 {标准层: [{cols,b,h}, ...]} 写回柱截面。

    ★★ 关键点 ★★
      「柱段 → 截面」的真正外键是 `tblColSeg.idNewDef`，它指向
      `tblColSect.idNew`（**不是** `tblColSeg.SectID`，也不是 `tblColSect.ID`）。
      只改 SectID 时，`yjk_importydb` 完全无视，导入结果一律按 idNewDef 还原，
      表现为「截面写不进 / 整体回退到基准截面」。
      实证：输入模型里 SectID 解释 = 优化后尺寸，idNewDef 解释 = 基准尺寸，
            而导入后的 .ymd 与 idNewDef 解释逐格完全一致。

    其它必须遵守的细节：
      * 新建 tblColSect 行要给出互不重复的 ID / No_ / idNew，
        ShapeVal 写成 YJK 规范形式 "1,<b>,<h>,6,<ID>,"，Name=''；
        idNew 若与既有行重复，YJK 导入时按 idNew 去重/别名，映射整体错乱。
        ★★ 而且**必须与全模型**（不只是 tblColSect 表内）不重复 —— 撞号
           会让大批柱被静默丢弃，详见 entity_ids() 的注释。
      * 同类表命名不统一：tblBeamSeg 用 idDef/defYidNew，tblWallSeg 用 idDef，
        tblColSeg 用 idNewDef —— 改梁/墙时同理。
    """
    # 清单可能被人用记事本改过（带 BOM），utf-8-sig 两种都认
    spec = json.load(open(spec_path, encoding="utf-8-sig"))
    flr = {r[0]: r[1] for r in con.execute("SELECT ID,No_ FROM tblStdFlr")}
    by_no = {v: k for k, v in flr.items()}
    cols = [r[1] for r in con.execute("PRAGMA table_info(tblColSect)")]
    # ★ 取号基准：ID 沿用 tblColSect 的低号段（只是习惯），idNew 取**全模型**最大值。
    used_id, used_new = entity_ids(con)
    max_id = con.execute("SELECT max(ID) FROM tblColSect").fetchone()[0] or 0
    max_no = con.execute("SELECT max(No_) FROM tblColSect").fetchone()[0] or 0
    max_in = max(used_new) if used_new else 0
    created = []                     # 新建行的 (ID, idNew)，供撞号自检
    # 现有截面索引：(b,h) -> (ID, idNew)
    idx = {}
    for sid, inn, b, h in con.execute("SELECT ID,idNew,b,h FROM tblColSect ORDER BY ID"):
        idx.setdefault((round(b), round(h)), (sid, inn))

    def get_sect(b, h, tmpl):
        key = (round(b), round(h))
        if key in idx:
            return idx[key]
        nonlocal max_id, max_no, max_in
        max_id += 1
        while max_id in used_id:                 # 低号段若被占则往后挪
            max_id += 1
        max_no += 1
        max_in += 1                              # max_in 起点已是全模型 idNew 最大值
        used_id.add(max_id)
        used_new.add(max_in)
        vals = dict(tmpl)
        vals.update(ID=max_id, No_=max_no, idNew=max_in,
                    b=float(b), h=float(h), Name="",
                    ShapeVal="1,%d,%d,6,%d," % (round(b), round(h), max_id),
                    ShapeVal1="", ShapeFVal="")
        cs = [c for c in cols if c in vals]
        con.execute("INSERT INTO tblColSect (%s) VALUES (%s)"
                    % (",".join(cs), ",".join("?" * len(cs))),
                    [vals[c] for c in cs])
        idx[key] = (max_id, max_in)
        created.append((max_id, max_in))
        return max_id, max_in

    changed = 0
    done_std = []                    # 真的改到了行的标准层
    skipped = []                     # 清单里有、模型里没有的标准层（**整层没写**）
    zero_std = []                    # 一条 UPDATE 都没命中的标准层
    miss_cols = []                   # 命中 0 行的 (标准层, 柱号)
    for std_key in sorted(spec, key=int):
        std = int(std_key)
        fid = by_no.get(std)
        if fid is None:
            print("   !! 标准层 %s 不在模型中 —— **整层柱截面一个都没改**" % std_key)
            skipped.append(std_key)
            continue
        n_this = 0
        for grp in spec[std_key]:
            gcols = grp["cols"]
            row = con.execute(
                "SELECT %s FROM tblColSect WHERE ID=(SELECT SectID FROM tblColSeg "
                "WHERE StdFlrID=? AND No_=? LIMIT 1)" % ",".join(cols),
                (fid, gcols[0])).fetchone()
            if row is None:
                # 老版在这里会 `dict(zip(cols, None))` → TypeError（难懂的崩），
                # 且整层被跳过却没有任何"没写"的记录。这里明确点名并记为问题。
                print("   !! 标准层 %s 的柱 %s 在模型中找不到 → 该分组跳过"
                      "（清单与模型不是同一套柱号？）" % (std_key, gcols[0]))
                miss_cols.append((std_key, gcols[0]))
                continue
            tmpl = dict(zip(cols, row))
            nsid, nnew = get_sect(grp["b"], grp["h"], tmpl)
            for c in gcols:
                # SectID 与 idNewDef 必须同时写：前者供人读，后者才是 YJK 认的键
                cur = con.execute(
                    "UPDATE tblColSeg SET SectID=?, idNewDef=? "
                    "WHERE StdFlrID=? AND No_=?", (nsid, nnew, fid, c))
                # ★ 老版是 `changed += 1`（无条件）→ 命中 0 行也报"柱段改写 16 个"。
                #   同文件 set_grades 早就用了 rowcount —— 这里一并对齐。
                changed += cur.rowcount
                n_this += cur.rowcount
                if cur.rowcount == 0:
                    miss_cols.append((std_key, c))
        if n_this:
            done_std.append(std)
        else:
            zero_std.append(std_key)
    if verbose:
        print("    柱段改写 %d 个（%d 个标准层真的改了；清单里共 %d 个标准层）"
              % (changed, len(done_std), len(spec)))
        if skipped:
            print("    !! 清单里这些标准层**不在模型中**，整层没写：%s"
                  % ", ".join(str(x) for x in skipped))
        if zero_std:
            print("    !! 这些标准层一条 UPDATE 都没命中（柱号与模型对不上）：%s"
                  % ", ".join(str(x) for x in zero_std))
        if miss_cols:
            print("    !! 这些柱号在模型里找不到（UPDATE 命中 0 行）：%s%s"
                  % (miss_cols[:8], " …共 %d 个" % len(miss_cols) if len(miss_cols) > 8 else ""))
        if created:
            print("    新建截面 %d 个：%s（idNew 取自全模型最大值之上）"
                  % (len(created), ["ID=%d/idNew=%d" % c for c in created]))
    return {"改写": changed, "写入标准层": done_std, "缺标准层": skipped,
            "零命中标准层": zero_std, "未命中柱号": miss_cols}


def check_sections(con, spec_path, verbose=True):
    """自检：按 idNewDef 反查截面尺寸，与目标清单逐格比对。

    ★★ 返回 (ok, bad, missing)：`missing` = 清单里有、模型里没有的标准层。
       老版对这类层直接 `continue` → 既不进 `ok` 也不进 `bad` →
       一个被完全忽略的标准层在**改写摘要与自检两处都不留痕**。
       现在 `ok` 把 missing 也算作不通过（fail-closed），调用方据此非零退出。
    """
    spec = json.load(open(spec_path, encoding="utf-8-sig"))
    by_new = {r[0]: (r[1], r[2]) for r in
              con.execute("SELECT idNew,b,h FROM tblColSect")}
    flr = {r[0]: r[1] for r in con.execute("SELECT ID,No_ FROM tblStdFlr")}
    by_no = {v: k for k, v in flr.items()}
    bad = ok = 0
    missing = []
    for std_key in sorted(spec, key=int):
        fid = by_no.get(int(std_key))
        if fid is None:
            missing.append(std_key)
            if verbose:
                print("    !! 自检：标准层 %s **不在模型中** —— 该层柱截面根本没写" % std_key)
            continue
        for grp in spec[std_key]:
            want = (float(grp["b"]), float(grp["h"]))
            for c in grp["cols"]:
                r = con.execute("SELECT idNewDef FROM tblColSeg WHERE StdFlrID=? AND No_=?",
                                (fid, c)).fetchone()
                got = by_new.get(r[0]) if r else None
                if got and abs(got[0] - want[0]) < .5 and abs(got[1] - want[1]) < .5:
                    ok += 1
                else:
                    bad += 1
                    if bad <= 6:
                        print("    !! std%s 柱%d 期望 %g×%g，idNewDef 反查得 %s"
                              % (std_key, c, want[0], want[1], got))
    if verbose:
        extra = ("；另有 %d 个标准层不在模型里，未参与自检" % len(missing)) if missing else ""
        print("    截面自检：符合 %d / 不符 %d%s" % (ok, bad, extra))
    return (bad == 0 and not missing), bad, missing


def _utf8_console():
    """让输出在任何控制台编码下都不崩（GBK 下把不可编码字符替换掉）。

    为什么需要：本包会打印 ✅ ❌ ⚠ −(U+2212) ² ³ 等**非 cp936** 字符，
    默认 GBK 控制台下 `print` 会抛 UnicodeEncodeError 并**以退出码 1 中断**，
    于是一个其实已经成功的任务（比如文件已经落盘）会被上层判成失败；
    对 frame_build.py 那条链更糟 —— 崩在被调用的库的 print 上，模型根本没写出来。

    `errors="replace"` 让它在 UTF-8 控制台下原样输出、在 GBK 下退化成 `?`，都不崩。
    ★ 只在实际执行时调用（CLI 入口），**不在 import 时改 stdout** ——
      这些模块会被别的脚本 import 当库用，污染 import 方的 stdout 是不对的。
    """
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass


def main():
    _utf8_console()          # ★ 必须在 argparse 之前：--help 也是写到 stdout 的
    ap = argparse.ArgumentParser(
        description="把「混凝土等级」与「优化柱截面」写回 YJK 模型库(.ydb/.ymd)")
    ap.add_argument("src", help="源模型库（.ydb/.ymd，不会被改）")
    ap.add_argument("dst", help="目标模型库（会先按 src 复制再改）")
    ap.add_argument("--grade", action="store_true",
                    help="写入逐标准层混凝土等级（给了 --grades/--grades-file 时自动开启）")
    ap.add_argument("--grades", default=None,
                    help='等级表，紧凑写法 "1-3:60,4-5:50,6:45,7:40" 或 JSON '
                         '\'{"1":60,...}\'（不给则保持模型现有等级不变）')
    ap.add_argument("--grades-file", default=None, help="等级表 JSON 文件")
    ap.add_argument("--sections", default=None, help="按 json 写入柱截面")
    a = ap.parse_args()

    # 源库先守卫：`shutil.copy2` 对不存在的路径抛的是裸 FileNotFoundError（看不出是哪个参数）
    if not os.path.exists(a.src):
        _die("源模型库不存在：%s\n"
             "  常见原因：路径拼错 / 文件还没生成 / 传了工程目录。\n"
             "  本脚本只读源库、只写 dst，不会创建源文件。" % os.path.abspath(a.src))
    if os.path.isdir(a.src):
        _die("源路径是目录，不是模型库文件：%s" % os.path.abspath(a.src))

    if os.path.abspath(a.src) != os.path.abspath(a.dst):
        shutil.copy2(a.src, a.dst)
    print("源  :", a.src)
    print("目标:", a.dst, "(%d 字节)" % os.path.getsize(a.dst))

    gmap = {}
    if a.grades_file:
        # 等级表是**人写的**输入（记事本存过就会带 BOM，BOM 被当正文会让第一条解析不出来）
        gmap = parse_grades(open(a.grades_file, encoding="utf-8-sig").read())
    elif a.grades:
        gmap = parse_grades(a.grades)

    # ★ 给了等级表就一定要写 —— `set_grades` 不能被单独的 `--grade` 开关挡着，
    #   只传 `--grades "1:50,..."` 会被**静默忽略**（等级没写进模型，实算仍按原等级），
    #   而 `verify_results` 会照实报"实算砼 = 原等级"，看起来像"优化没效果"。
    con = open_rw(a.dst)
    problems = []
    try:
        if a.grade or gmap:
            if gmap and not a.grade:
                print("    （检测到 --grades/--grades-file：自动写入等级）")
            g = set_grades(con, gmap or None)
            # ★★ 返回值**必须判定**：老版把它丢掉，于是"一层都没写"也打印"完成。"+ rc 0
            for k in g["缺标准层"]:
                problems.append("等级表里的标准层 %s 在模型中不存在 —— 该层混凝土等级"
                                "**没有**改写" % k)
            for k in g["Para 缺下标"]:
                problems.append("标准层 %s 的 tblStdFlr.Para 字段放不下 板/柱/梁/墙 "
                                "四个下标（2/4/5/6）—— 该层等级实际没生效" % k)
            if g["缺 Kind"]:
                problems.append("tblStdFlrPara 里有 %d 个 (标准层, Kind) 行不存在"
                                "（只改不补：应改 %d 行、实际只改到 %d 行）——"
                                " 展开表与 tblStdFlr.Para 不一致；前几处：%s"
                                % (len(g["缺 Kind"]), g["应改行数"], g["ParaVal"],
                                   g["缺 Kind"][:6]))
        if a.sections:
            s = set_sections(con, a.sections)
            for k in s["缺标准层"]:
                problems.append("截面清单里的标准层 %s 在模型中不存在 —— 该层柱截面"
                                "**一个都没改**" % k)
            for k in s["零命中标准层"]:
                problems.append("标准层 %s 一条 UPDATE 都没命中（清单的柱号与模型对不上）"
                                % k)
            if s["改写"] == 0:
                problems.append("柱段改写 **0 个** —— 截面清单一条都没写进模型")
        con.commit()
        # 自检：idNew 必须**全局**唯一，否则 YJK 导入会静默丢构件
        dup = check_idnew_global(con)
        if dup:
            print("!! 全局 idNew 撞号 %d 个（前 10：%s）—— YJK 会按 idNew 去重/别名，"
                  "构件可能被静默丢弃，请先处理" % (len(dup), dup[:10]))
            sys.exit(1)
        if a.sections:
            # ★ check_sections 是**真校验**（逐格反查 idNewDef）；老版把它的返回值
            #   丢掉，于是 bad>0 时屏幕上几行 !! 之后照样"完成。"+ rc 0，
            #   而本脚本是纯 CLI，上层（colopt.py）只看退出码。
            ok, bad, missing = check_sections(con, a.sections)
            if missing:
                problems.append("截面自检跳过了 %d 个不在模型里的标准层：%s"
                                % (len(missing), ", ".join(str(x) for x in missing)))
            if bad:
                problems.append("截面自检**不符 %d 处** —— 写进模型的截面与清单不一致"
                                "（上面逐处点了名）" % bad)
    finally:
        con.close()
    if problems:
        print("\n!! 本次**没有全部写成功**（退出码 1）—— 逐条：")
        for p in problems:
            print("   · %s" % p)
        print("   （磁盘上的 %s 已按上面的内容写入；请修正输入后重跑）" % a.dst)
        sys.exit(1)
    print("完成。")


if __name__ == "__main__":
    main()
