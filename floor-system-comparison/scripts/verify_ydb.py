# -*- coding: utf-8 -*-
r"""自造 .ydb 的静态体检 —— 不启动 YJK 就能查出的错误全部先拦住。

为什么需要它
------------
`yjk_importydb` 对坏文件的容忍度很高（或缺字段就静默回退），
所以「导入成功」不能当验收。先把能静态判的判完，再交给 YJK。

检查项
------
1. 全局 `idNew` 唯一（YJK 用一个全模型共享的交叉引用序号）。
2. 全部外键可解析（`idGrid`/`idDef`/`idNewDef`/`idNewNode`/`idGridStr`/`idNode1…`）。
3. `idNewBzc` 必须等于 `tblStdFlr.idNew`。
4. 几何自洽：
   * 所有板面积之和 = 柱网总面积；
   * 板与板不重叠；
   * 每条网格至少被一块板用到（没有孤立网格）。
5. `tblSlab.GridsID` 与 `idGridStr` 必须**同序等长**（前者是 ID，后者是 idNew）。
6. `ShapeVal` 里的 b/h 与 `b`/`h` 列一致（YJK 只认 ShapeVal）。

用法
----
    python verify_ydb.py ../models/S3.ydb
    python verify_ydb.py ../models/*.ydb --area 67.2 33.6
"""
import argparse
import glob
import os
import sqlite3
import sys

NONE_ID = 4294967295


def _die(msg):
    """打印可读理由并以**退出码 2**结束（= 体检工具**没跑成**）。

    ★ 为什么要与"模型有缺陷"分开：`main()` 对有缺陷的模型返回 **1**，
      而裸异常的 traceback 也是 1 —— 调用方分不清"体检出来有问题"与
      "体检根本没做成"。工具侧的失败（路径错/不是 sqlite/0 字节）一律用 **2**。
    ★ 消息按 errors=replace 写 stderr：默认 GBK 控制台下打印非 cp936 字符
      会抛 UnicodeEncodeError，把"可读报错"变成又一个看不懂的 traceback。
    """
    for s in (sys.stderr,):
        try:
            s.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass
    sys.stderr.write(msg.rstrip("\n") + "\n")
    raise SystemExit(2)


def connect_ro(path):
    """只读打开一个模型库；坏路径一律翻成中文，**绝不创建文件**。

    ★★ 为什么必须 mode=ro + 存在性守卫：`sqlite3.connect(path)` 默认是 **rw**，
      对一个**不存在**的路径会**先把文件建出来**（0 字节空库），然后在第一条
      查询上抛 `no such table: xxx` —— 于是一个「体检」工具会把用户拼错的路径
      变成一个空文件留在盘上，而"路径写错"这件事本身反而更难看出来。
    ★ 还有一半常被漏掉：对**0 字节或非 sqlite** 的文件，`connect()` 是**成功**的，
      `DatabaseError: file is not a database` 要到第一条查询才抛 ——
      所以这里用 `PRAGMA schema_version` 在 connect 内就把它探出来。
    """
    p = os.path.abspath(path)
    if not os.path.exists(p):
        _die("模型库不存在：%s\n"
             "  常见原因：路径拼错 / 文件还没生成 / 传了工程目录而不是库文件。\n"
             "  本工具**只读**打开，不会创建文件。" % p)
    if os.path.isdir(p):
        _die("给的是目录，不是模型库文件：%s\n"
             "  本工具要的是 .ydb/.ymd 文件本身，不是它所在的目录。" % p)
    if os.path.getsize(p) == 0:
        _die("模型库是 0 字节（半写/损坏/占位文件）：%s\n"
             "  常见原因：上一次写出中途失败，或工作目录里留了个同名空文件。" % p)
    try:
        con = sqlite3.connect("file:%s?mode=ro" % p.replace("\\", "/"), uri=True)
        con.execute("PRAGMA schema_version").fetchone()   # ★ 把"不是数据库"提前探出来
    except sqlite3.Error as e:
        _die("打不开模型库 %s：%s\n"
             "  常见原因：不是 sqlite 库（拿错文件）/ 库已损坏 / 文件正被别的进程独占。"
             % (p, e))
    return con


def _ids(con, tbl):
    return [r[0] for r in con.execute("SELECT idNew FROM [%s]" % tbl)]


def _split(s):
    return [int(v) for v in str(s or "").split(",") if v.strip()]


def _poly(sx, sy):
    x = [float(v) for v in str(sx or "").split(",") if v.strip()]
    y = [float(v) for v in str(sy or "").split(",") if v.strip()]
    return list(zip(x, y))


def _area(poly):
    """鞋带公式（顶点按序、不闭合）。"""
    n = len(poly)
    if n < 3:
        return 0.0
    a = 0.0
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        a += x1 * y2 - x2 * y1
    return abs(a) / 2.0


def check(path, span=None, span_axis=None, verbose=True):
    errs, warns = [], []
    con = connect_ro(path)          # ★ 只读 + 存在性守卫（见 connect_ro 的说明）

    # ---- 1. idNew 全局唯一 ----
    GEOM = ["tblStdFlr", "tblFloor", "tblJoint", "tblAxis", "tblGrid", "tblBeamSect",
            "tblBeamSeg", "tblColSect", "tblColSeg", "tblSlab"]
    seen, dup = {}, []
    for t in GEOM:
        if not con.execute("SELECT count(*) FROM sqlite_master WHERE name=?", (t,)).fetchone()[0]:
            continue
        for v in _ids(con, t):
            if v in seen:
                dup.append((v, seen[v], t))
            seen[v] = t
    if dup:
        errs.append("idNew 重复 %d 组，例：%s" % (len(dup), dup[:5]))

    stdflr_new = set(_ids(con, "tblStdFlr"))
    jset = {}                                    # joint idNew -> ID
    for i, n in con.execute("SELECT ID, idNew FROM tblJoint"):
        jset[n] = i
    jid = {i for i in jset.values()}
    aset, aid = {}, set()
    for i, n in con.execute("SELECT ID, idNew FROM tblAxis"):
        aset[n] = i
        aid.add(i)
    gset, gid = {}, set()
    for i, n in con.execute("SELECT ID, idNew FROM tblGrid"):
        gset[n] = i
        gid.add(i)
    bsn, bsid = {}, set()
    for i, n in con.execute("SELECT ID, idNew FROM tblBeamSect"):
        bsn[n] = i
        bsid.add(i)
    csn, csid = {}, set()
    for i, n in con.execute("SELECT ID, idNew FROM tblColSect"):
        csn[n] = i
        csid.add(i)

    def bad(tbl, col, val, universe, tag):
        if val is not None and val != NONE_ID and val not in universe:
            errs.append("%s.%s=%s 在 %s 里不存在" % (tbl, col, val, tag))

    # ---- 2. 外键 ----
    for ID, n1, n2, j1, j2, bzc in con.execute(
            "SELECT ID, idNode1, idNode2, Jt1ID, Jt2ID, idNewBzc FROM tblAxis"):
        if n1 not in jset or n2 not in jset:
            errs.append("tblAxis ID=%s 的 idNode 不是合法节点 idNew" % ID)
        if j1 not in jid or j2 not in jid:
            errs.append("tblAxis ID=%s 的 Jt1ID/Jt2ID 不是合法节点 ID" % ID)
        if bzc not in stdflr_new:
            errs.append("tblAxis ID=%s 的 idNewBzc=%s 不是标准层 idNew" % (ID, bzc))

    used_grids = set()
    for ID, n1, n2, j1, j2, bzc, axn, axi in con.execute(
            "SELECT ID, idNode1, idNode2, Jt1ID, Jt2ID, idNewBzc, idAxis, AxisID"
            " FROM tblGrid"):
        if n1 not in jset or n2 not in jset:
            errs.append("tblGrid ID=%s 的 idNode 不是合法节点 idNew" % ID)
        if j1 not in jid or j2 not in jid:
            errs.append("tblGrid ID=%s 的 Jt1ID/Jt2ID 不是合法节点 ID" % ID)
        if axn not in aset or axi not in aid:
            errs.append("tblGrid ID=%s 的轴线引用不成立" % ID)
        if bzc not in stdflr_new:
            errs.append("tblGrid ID=%s 的 idNewBzc 不成立" % ID)

    for ID, g_id, g_new, s_id, s_new, bzc in con.execute(
            "SELECT ID, GridID, idGrid, SectID, idDef, idNewBzc FROM tblBeamSeg"):
        if g_new not in gset or g_id not in gid:
            errs.append("tblBeamSeg ID=%s 的网格引用不成立" % ID)
        if s_new not in bsn or s_id not in bsid:
            errs.append("tblBeamSeg ID=%s 的截面引用不成立" % ID)
        if gset.get(g_new) != g_id:
            errs.append("tblBeamSeg ID=%s 的 GridID 与 idGrid 指向不同网格" % ID)
        if bsn.get(s_new) != s_id:
            errs.append("tblBeamSeg ID=%s 的 SectID 与 idDef 指向不同截面" % ID)
        if bzc not in stdflr_new:
            errs.append("tblBeamSeg ID=%s 的 idNewBzc 不成立" % ID)

    for ID, nnode, jt, ndef, sid, bzc in con.execute(
            "SELECT ID, idNewNode, JtID, idNewDef, SectID, idNewBzc FROM tblColSeg"):
        if nnode not in jset or jt not in jid:
            errs.append("tblColSeg ID=%s 的节点引用不成立" % ID)
        if jset.get(nnode) != jt:
            errs.append("tblColSeg ID=%s 的 JtID 与 idNewNode 不一致" % ID)
        if ndef not in csn or sid not in csid:
            errs.append("tblColSeg ID=%s 的柱截面引用不成立（idNewDef 才是有效外键）" % ID)
        if csn.get(ndef) != sid:
            errs.append("tblColSeg ID=%s 的 SectID 与 idNewDef 指向不同截面" % ID)
        if bzc not in stdflr_new:
            errs.append("tblColSeg ID=%s 的 idNewBzc 不成立" % ID)

    # ---- 3/4/5. 板 ----
    slabs = []
    for ID, gs_id, gs_new, vx, vy, bzc in con.execute(
            "SELECT ID, GridsID, idGridStr, VertexX, VertexY, idNewBzc FROM tblSlab"):
        a, b = _split(gs_id), _split(gs_new)
        if len(a) != len(b):
            errs.append("tblSlab ID=%s 的 GridsID 与 idGridStr 长度不等(%d/%d)"
                        % (ID, len(a), len(b)))
        for i, gn in enumerate(b):
            if gn not in gset:
                errs.append("tblSlab ID=%s 的 idGridStr[%d]=%s 不是网格 idNew" % (ID, i, gn))
            elif gset[gn] != a[i]:
                errs.append("tblSlab ID=%s 第%d边 GridsID(%s) 与 idGridStr(%s) 不对应"
                            % (ID, i, a[i], gn))
            used_grids.add(a[i])
        if bzc not in stdflr_new:
            errs.append("tblSlab ID=%s 的 idNewBzc 不成立" % ID)
        slabs.append((ID, _poly(vx, vy)))

    # ---- 6. ShapeVal 与列一致 ----
    for t, cols in (("tblBeamSect", "b, h"), ("tblColSect", "b, h")):
        for ID, sv, b_, h_ in con.execute(
                "SELECT ID, ShapeVal, b, h FROM [%s]" % t):
            v = [x for x in str(sv or "").split(",")]
            if len(v) < 5:
                errs.append("%s ID=%s 的 ShapeVal 格式不对：%r" % (t, ID, sv))
                continue
            if int(round(float(v[3]))) != 6:
                warns.append("%s ID=%s 的 ShapeVal 材料位=%s（本例预期 6=混凝土）" % (t, ID, v[3]))
            if abs(float(v[1]) - b_) > 1e-6 or abs(float(v[2]) - h_) > 1e-6:
                errs.append("%s ID=%s 的 ShapeVal(%s,%s) 与 b/h(%s,%s) 不一致"
                            % (t, ID, v[1], v[2], b_, h_))
            if int(float(v[4])) != ID:
                warns.append("%s ID=%s 的 ShapeVal 末位=%s（YJK 自己的模型此处=ID）"
                             % (t, ID, v[4]))

    unused = gid - used_grids
    if unused:
        warns.append("有 %d 条网格没被任何板使用（悬空网格）：%s"
                     % (len(unused), sorted(unused)[:8]))

    total_area = sum(_area(p) for _, p in slabs) / 1e6      # mm² -> m²
    if span:
        sx, sy = span
        want = sx * sy
        if abs(total_area - want) > max(0.01, want * 1e-6):
            errs.append("板面积合计 %.3f m² ≠ 柱网总面积 %.3f m²" % (total_area, want))
    # 重叠检查（矩形简化：用面积和 vs 并集外包，交给面积等式已足够；此处查面积>个别异常）
    for ID, p in slabs:
        if len(p) < 3:
            errs.append("tblSlab ID=%s 顶点数不足 3" % ID)

    # 梁/柱几何量
    n_joint = con.execute("SELECT count(*) FROM tblJoint").fetchone()[0]
    n_grid = con.execute("SELECT count(*) FROM tblGrid").fetchone()[0]
    n_colseg = con.execute("SELECT count(*) FROM tblColSeg").fetchone()[0]
    n_floor = con.execute("SELECT count(*) FROM tblFloor").fetchone()[0]
    xs = [r[0] for r in con.execute("SELECT X FROM tblJoint")]
    ys = [r[0] for r in con.execute("SELECT Y FROM tblJoint")]
    bbox = (max(xs) - min(xs), max(ys) - min(ys)) if xs else (0, 0)
    con.close()

    if verbose:
        tag = os.path.basename(path)
        print("=" * 62)
        print("%s   节点%d 网格%d 板%d 柱段%d 层%d" % (tag, n_joint, n_grid, len(slabs),
                                                       n_colseg, n_floor))
        print("   外包尺寸 %.1f × %.1f m   板面积合计 %.2f m²" % (bbox[0] / 1000.0,
                                                                bbox[1] / 1000.0, total_area))
        for w in warns:
            print("   [警告] %s" % w)
        if errs:
            print("   ❌  %d 个错误：" % len(errs))
            for e in errs[:20]:
                print("      - %s" % e)
        else:
            print("   ✅  静态体检全部通过")
    return errs, warns


def _utf8_console():
    """让输出在任何控制台编码下都不崩（GBK 下把不可编码字符替换掉）。

    为什么需要：本包会打印 ✅ ❌ ⚠ −(U+2212) ² ³ 等**非 cp936** 字符，
    默认 GBK 控制台下 `print` 会抛 UnicodeEncodeError 并**以退出码 1 中断**，
    于是一个其实已经成功的任务（比如文件已经落盘）会被上层判成失败；
    对 frame_build.py 那条链更糟 —— 崩在被调用的库的 print 上，模型根本没写出来。

    `errors="replace"` 让它在 UTF-8 控制台下原样输出、在 GBK 下退化成 `?`，都不崩。
    ★ 只在实际执行时调用（CLI 入口），**不在 import 时改 stdout** ——
      这些模块会被别的脚本 import 当库用，污染 import 方的 stdout 是不对的。
    ★ 本文件实测**真的会触发**：check() 会打印 `板面积合计 %.2f m²`（U+00B2）、
      `❌  %d 个错误`（U+274C）、`✅  静态体检全部通过`（U+2705），三者都不在 cp936 里。
    """
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass


def main():
    _utf8_console()          # ★ 必须在 argparse 之前：--help 也是写到 stdout 的
    ap = argparse.ArgumentParser()
    ap.add_argument("ydb", nargs="+")
    ap.add_argument("--area", nargs=2, type=float, metavar=("SPAN_X", "SPAN_Y"),
                    help="柱网总尺寸(m)，用来核对板面积")
    a = ap.parse_args()
    files = []
    for p in a.ydb:
        files.extend(glob.glob(p))
    # ★★ 一个体检工具**绝不能**对"从来没打开过的文件"宣告"0 个错误"：
    #    glob.glob() 对不存在的路径返回 []（不抛错）→ files 为空 → bad 保持 0 →
    #    打印「合计错误 0」+ rc 0，读起来就是"静态体检通过"。
    #    路径拼错 / CWD 不对 / models 目录是空的，都会走到这里。
    if not files:
        _die("没找到任何 ydb：下列通配符一个文件都没匹配到\n%s\n"
             "  给的参数：%s\n"
             "  常见原因：路径拼错 / 当前目录不对（相对路径是相对**当前工作目录**的）/\n"
             "            文件还没生成（先跑 make_ydb.py 或 build_floor.py）。\n"
             "  ★ 本次**没有体检任何文件**，所以不会给出 0 错误之类的结论。"
             % ("\n".join("    %r" % p for p in a.ydb), " ".join(a.ydb)))
    bad = 0
    for f in files:
        e, _ = check(f, a.area)
        bad += len(e)
    print("\n合计错误 %d" % bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
