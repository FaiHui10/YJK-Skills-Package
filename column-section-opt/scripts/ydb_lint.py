# -*- coding: utf-8 -*-
"""模型库（*.ymd / *.ydb）自检：实体 ID 范围、引用完整性、楼层与截面结构摘要。

外部改过模型库后**必跑**。四条判据：
  1. 实体 ID 全部 < 100000（`tblProjectPara.ID=100000` 是哨兵；越界行会被 YJK 静默丢弃）
  2. 引用不悬空（节点/网格/轴线/构件段/荷载/属性之间的 ID 与 idNew 引用都能落地）
  3. 楼层组装自洽（标准层数、自然层数、每个标准层的柱截面分布、Para 里的等级）
  4. **每个标准层内的 `No_` 必须是 1..N**（无重号、无缺号）—— 理由见 SEQ_TABLES 的说明

用法：
    python ydb_lint.py <模型文件> [--base <原模型>]

退出码：**0** = 通过；**1** = 模型有问题（ID 越界/引用悬空/编号不合规）；
        **2** = 工具没跑成（路径错 / 不是 sqlite / 0 字节 / 给了目录）。
        后两者必须分得开，否则"体检发现有问题"与"体检根本没做成"在自动化里同形。
"""
import argparse
import collections
import os
import sqlite3
import sys

ID_LIMIT = 100000
SKIP = {0, -1, 4294967295}

# ④ 检查"每标准层 No_ = 1..N"的表：凡是**同时带 StdFlrID 与 No_** 的几何表都在内。
# ★ 为什么必须查（实机教训）：YJK 几何表的 `No_` 是**每个标准层内**从 1 重新开始的建模
#   序号（StdFlrID 作用域）；`wpj*.out` 里印的 `N-C=<柱号>` 用的就是它。
#   一个把 `No_` 整模连续编号的模型照样能导入、前处理也不报错，但 N-C 从此对不上
#   `tblColSeg.No_`：所有按柱号分组的复核/优化都会**静默错位**（分组整体错位、
#   甚至整层漏报）。所以按"每标准层 1..N"判，与"ID 越界/引用悬空"同级硬失败。
SEQ_TABLES = ("tblJoint", "tblAxis", "tblGrid", "tblColSeg", "tblBeamSeg",
              "tblWallSeg", "tblSlab")

# 各表的引用列：ID 引用 / idNew 引用 / 逗号列表(列, 'i'|'n')
REFS = {
    "tblJoint":    ([], [], [("ListGJidNew", "n"), ("ListLoadidNew", "n")]),
    "tblAxis":     (["Jt1ID", "Jt2ID"], ["idNode1", "idNode2"], []),
    "tblGrid":     (["Jt1ID", "Jt2ID", "AxisID"],
                    ["idNode1", "idNode2", "idAxis"], []),
    "tblColSeg":   (["JtID", "SectID"], ["idNewNode", "idNewDef"], []),
    "tblBeamSeg":  (["GridID", "SectID"], ["idGrid", "idDef"], []),
    "tblWallSeg":  (["GridID", "SectID"], ["idGrid", "idDef"], []),
    "tblWallHole": (["GridID", "SectID"], ["idGrid", "idDef"], []),
    "tblSlab":     ([], [], [("GridsID", "i"), ("idGridStr", "n")]),
    "tblLoadSeg":  (["ElementID", "SectID"], ["idElement", "idDef", "idNode"], []),
    "tblProperty": (["ID"], [], []),
}


def _die(msg):
    """「工具没跑成」→ **退出码 2**（与"模型有缺陷"的 1 分开）。

    ★ 为什么要分开：main() 对"模型有问题"返回 **1**，而裸异常的 traceback 也是 1 ——
      调用方分不清"体检出来有问题"与"体检根本没做成"。工具侧的失败一律用 2。
    ★ 消息按 errors=replace 写 stderr：默认 GBK 控制台下打印非 cp936 字符会抛
      UnicodeEncodeError，把"可读报错"变成又一个看不懂的 traceback。
    """
    for s in (sys.stderr,):
        try:
            s.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass
    sys.stderr.write(msg.rstrip("\n") + "\n")
    sys.exit(2)


def connect(path):
    """只读打开模型库；坏输入一律翻成中文，**绝不创建文件、绝不抛裸 traceback**。

    ★★ 四件事必须一次做完（缺任何一件都会给用户一个看不懂的 traceback）：
      1. **存在**：`mode=ro` 打不开不存在的文件，抛的是
         `sqlite3.OperationalError: unable to open database file` —— 连路径都不说；
      2. **不是目录**：给一个目录同样是上面那句 OperationalError；
      3. **非 0 字节**：0 字节文件 `connect()` 是**成功**的，报错推迟到第一条查询；
      4. **真的是 sqlite**：非 sqlite 的文件 `connect()` 也**成功**，
         `DatabaseError: file is not a database` 同样推迟到第一条查询 ——
         所以这里用 `PRAGMA schema_version` 在 connect 内就把它探出来。
    """
    p = os.path.abspath(path)
    if not os.path.exists(p):
        _die("模型库不存在：%s\n"
             "  常见原因：路径拼错 / 文件还没生成（.ymd 由 yjk_save 写出）/ 传了目录。\n"
             "  本工具**只读**打开，不会创建文件。" % p)
    if os.path.isdir(p):
        _die("给的是目录，不是模型库文件：%s\n"
             "  本工具要的是 .ydb/.ymd 文件本身，不是它所在的目录。" % p)
    if os.path.getsize(p) == 0:
        _die("模型库是 0 字节（半写/损坏/占位文件）：%s\n"
             "  常见原因：上一次序列化/写出中途失败，或工作目录里留了个同名空文件。\n"
             "  这种库拿来导入会得到「模型中没有单元数据」，先把库重新写出来再体检。" % p)
    try:
        con = sqlite3.connect("file:%s?mode=ro" % p.replace("\\", "/"), uri=True)
        con.execute("PRAGMA schema_version").fetchone()   # ★ 把"不是数据库"提前探出来
    except sqlite3.Error as e:
        _die("打不开模型库 %s：%s\n"
             "  常见原因：不是 sqlite 库（拿错文件）/ 库已损坏 / 文件正被别的进程独占。"
             % (p, e))
    con.text_factory = lambda b: b.decode("gbk", "replace")
    return con


def lint(path, verbose=True):
    con = connect(path)
    ts = [r[0] for r in con.execute(
        "SELECT name FROM sqlite_master WHERE type='table'")]
    ids, news = set(), set()
    for t in ts:
        cols = [r[1] for r in con.execute("PRAGMA table_info([%s])" % t)]
        if "ID" in cols:
            ids |= {r[0] for r in con.execute("SELECT ID FROM [%s]" % t)
                    if isinstance(r[0], int)}
        if "idNew" in cols:
            news |= {r[0] for r in con.execute("SELECT idNew FROM [%s]" % t)
                     if isinstance(r[0], int)}

    # 1) ID 越界（`tblProjectPara.ID = 100000` 是哨兵本身，不算越界；>100000 才是）
    over = []
    for t in ts:
        cols = [r[1] for r in con.execute("PRAGMA table_info([%s])" % t)]
        if "ID" in cols:
            n = con.execute("SELECT COUNT(*) FROM [%s] WHERE ID>%d" % (t, ID_LIMIT)
                            ).fetchone()[0]
            if n:
                over.append((t, n))

    # 2) 引用悬空
    dangling = collections.Counter()
    skipped = []                 # 实际 schema 里不存在的引用列（按版本差异跳过）
    for t, (idc, newc, lists) in REFS.items():
        if t not in ts:
            continue
        # ★ 不同 YJK 版本的表结构并不完全一样：例如 7.1 的 tblLoadSeg **没有 idNode 列**，
        #   而 8.x 空工程骨架里有。无条件照 REFS 拼列名，会让 SELECT 直接抛
        #   `sqlite3.OperationalError: no such column: idNode` ——
        #   于是 linter 对**官方 CreateYDB 写出的库**整个崩掉（本机实测）。
        #   这里按实际 schema 过滤掉不存在的列再查，缺列不影响其它列的检查。
        real = {r[1] for r in con.execute("PRAGMA table_info([%s])" % t)}
        missing = [c for c in idc + newc + [c for c, _ in lists] if c not in real]
        idc = [c for c in idc if c in real]
        newc = [c for c in newc if c in real]
        lists = [(c, k) for c, k in lists if c in real]
        cols = [c for c in idc + newc + [c for c, _ in lists]]
        if not cols:
            continue
        if missing:
            skipped.append((t, missing))
        for row in con.execute("SELECT %s FROM [%s]"
                               % (",".join("[%s]" % c for c in cols), t)):
            v = list(row)
            for i, c in enumerate(idc):
                if isinstance(v[i], int) and v[i] not in SKIP and v[i] not in ids:
                    dangling["%s.%s" % (t, c)] += 1
            for i, c in enumerate(newc):
                x = v[len(idc) + i]
                if isinstance(x, int) and x not in SKIP and x not in news:
                    dangling["%s.%s" % (t, c)] += 1
            for i, (c, kind) in enumerate(lists):
                s = v[len(idc) + len(newc) + i]
                if not s:
                    continue
                for part in str(s).split(","):
                    part = part.strip()
                    if not part.isdigit():
                        continue
                    x = int(part)
                    if x in SKIP:
                        continue
                    if (x not in ids) if kind == "i" else (x not in news):
                        dangling["%s.%s" % (t, c)] += 1

    # 3) 结构摘要
    stds = {}
    for sid, no, h, para in con.execute(
            "SELECT ID,No_,Height,Para FROM tblStdFlr ORDER BY No_"):
        p = (para or "").split(",")
        stds[sid] = {"no": no, "h": h,
                     "等级": [p[i] if i < len(p) else "?" for i in (2, 4, 5, 6)]}
    sid2no = {k: v["no"] for k, v in stds.items()}

    # 4) 每标准层 No_ = 1..N（重号 / 缺号）—— 见文件头 SEQ_TABLES 的说明
    seqbad = []                                    # [(表, 标准层, 重号, 缺号, 行数)]
    for t in SEQ_TABLES:
        if t not in ts:
            continue
        cols = [r[1] for r in con.execute("PRAGMA table_info([%s])" % t)]
        if "StdFlrID" not in cols or "No_" not in cols:
            continue
        byflr = collections.defaultdict(list)
        for sid, no in con.execute("SELECT StdFlrID,No_ FROM [%s]" % t):
            byflr[sid].append(no)
        for sid in sorted(byflr, key=lambda s: (sid2no.get(s, 10 ** 6), s)):
            nums = byflr[sid]
            if not nums:
                continue
            cnt = collections.Counter(nums)
            dup = sorted(n for n, c in cnt.items() if c > 1)
            top = max(nums)
            miss = sorted(set(range(1, top + 1)) - set(nums))
            if dup or miss or min(nums) != 1:
                seqbad.append((t, sid2no.get(sid, sid), dup[:10], miss[:10], len(nums)))

    floors = collections.defaultdict(list)
    for no, sid, lb in con.execute("SELECT No_,StdFlrID,LevelB FROM tblFloor ORDER BY No_"):
        floors[sid].append(no)
    sects = {r[0]: r[1] for r in con.execute("SELECT ID,ShapeVal FROM tblColSect")}
    dist = collections.defaultdict(collections.Counter)
    for sid, sect in con.execute("SELECT StdFlrID,SectID FROM tblColSeg"):
        sv = (sects.get(sect) or "").split(",")
        dist[sid]["%s×%s" % (sv[1], sv[2]) if len(sv) > 2 else "?"] += 1
    counts = {t: con.execute("SELECT COUNT(*) FROM [%s]" % t).fetchone()[0]
              for t in ("tblStdFlr", "tblFloor", "tblColSect", "tblColSeg",
                        "tblJoint", "tblBeamSeg", "tblWallSeg", "tblSlab",
                        "tblLoadSeg", "tblProperty") if t in ts}

    if verbose:
        print("=" * 78)
        print(path)
        print("  表数=%d  实体 ID 数=%d  idNew 数=%d" % (len(ts), len(ids), len(news)))
        print("  ① 实体 ID >%d 的行：%s" % (ID_LIMIT, over or "无 ✅"))
        if skipped:
            print("  · 按版本跳过的引用列（本库没有这些列，不影响其它检查）：%s"
                  % ", ".join("%s.%s" % (t, ",".join(cs)) for t, cs in skipped))
        print("  ② 引用悬空：%d %s" % (sum(dangling.values()),
                                      ("→ " + ", ".join(
                                          "%s×%d" % (k, v)
                                          for k, v in dangling.most_common(8)))
                                      if dangling else "✅"))
        print("  ③ 每标准层 No_=1..N（%d 张几何表）：%s"
              % (len(SEQ_TABLES), "%d 处不合规 ❌" % len(seqbad) if seqbad else "✅"))
        for t, std, dup, miss, n in seqbad[:12]:
            print("     %-11s 标准层%-3s 重号=%s 缺号=%s（%d 行）"
                  % (t, std, dup or "无", miss or "无", n))
        if len(seqbad) > 12:
            print("     …还有 %d 处" % (len(seqbad) - 12))
        print("  ④ 结构：标准层 %d（自然层 %d）柱截面 %d 柱段 %d"
              % (len(stds), sum(len(v) for v in floors.values()),
                 len(sects), counts.get("tblColSeg", 0)))
        for sid in sorted(stds, key=lambda s: stds[s]["no"]):
            fs = sorted(floors.get(sid, []))
            rng = "%s-%s(%d层)" % (fs[0], fs[-1], len(fs)) if fs else "无自然层 ⚠"
            print("     标准层%-3s 层高=%-5s 自然层=%-12s 板/柱/梁/墙=%s  %s"
                  % (stds[sid]["no"], stds[sid]["h"], rng,
                     "/".join(stds[sid]["等级"]), dict(dist.get(sid, {}))))
        print("  构件行数：%s" % counts)
    con.close()
    return {"over": over, "dangling": sum(dangling.values()), "stds": len(stds),
            # 新键（旧键一个没动）：违规处数，main 里与 over/dangling 同级判"不通过"
            "编号": len(seqbad), "编号明细": seqbad}


def main():
    _utf8_console()          # ★ 必须在 argparse 之前：--help 也是写到 stdout 的
    ap = argparse.ArgumentParser()
    ap.add_argument("model")
    ap.add_argument("--base", help="原模型，用于对比基线（可选）")
    a = ap.parse_args()
    r = lint(a.model)
    if a.base:
        print("\n=== 基线对比 ===")
        lint(a.base)
    bad = bool(r["over"]) or r["dangling"] > 0 or r["编号"] > 0
    if r["编号"]:
        print("\n  标准层内 No_ 编号不合规 %d 处 —— wpj*.out 的 N-C 会与 "
              "tblColSeg.No_ 对不上，按柱号分组的复核/优化会静默错位。"
              % r["编号"])
    print("\n结论：%s" % ("❌ 有问题，别拿去导入/计算" if bad else "✅ 通过"))
    return 1 if bad else 0


def _utf8_console():
    """让输出在任何控制台编码下都不崩（GBK 下把不可编码字符替换掉）。

    为什么需要：本包会打印 ✅ ❌ ⚠ −(U+2212) ² ³ 等**非 cp936** 字符，
    默认 GBK 控制台下 print 会抛 UnicodeEncodeError 并**以退出码 1 中断**，
    于是一个其实已经成功的任务（比如文件已经落盘）会被上层判成失败。
    errors=replace 让它在 UTF-8 控制台下原样输出、在 GBK 下退化成 ?，都不崩。

    ★ 在 `main()` 开头调用一次（而不是只在 `if __name__ == "__main__"` 里）：
      本文件会被别的脚本 import 当库用（`lint()` 的 ① ② ③ ④ 与"结论：✅ 通过"
      都是带非 GBK 字符的），那些调用方同样需要这层兜底。重复调用无害。
    """
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(errors="replace")
        except Exception:
            pass


if __name__ == "__main__":
    sys.exit(main())
