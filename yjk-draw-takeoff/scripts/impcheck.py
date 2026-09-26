# -*- coding: utf-8 -*-
r"""导入校验闸门（底座自带）—— 逐表核对 `yjk_importydb` 是否**真的**把几何导进来了。

为什么底座必须自带这一关
------------------------
实测（现场）：一个**半写完**的 `.ydb`（序列化器清完表之后中途抛异常）拿去导入，
`yjk_importydb` **照样返回成功**，失败要等到两步之后才现形：

    fea.dat-ERR.txt = 「模型中没有单元数据」   +   分析失败[-45]

—— 一整轮计算白跑。同类现场还有：给 `yjk_importydb` 传**相对路径**时，YJK 按自己的工作
目录解析 → 找不到文件 → 弹「文件不存在」框，若被应答放行，导入的是**空模型**，命令同样 OK。

**字节数不能当判据**：`save` 会重写模型库（通常多 1 个 sqlite 页），`tblSlab` 的合法增删
也会改变库大小。所以判据只能是**逐表行数**。

判据（两级，别搞混）
--------------------
* **必判表 MUST_MATCH** —— 必须逐表相等，差一行就说明模型没真的进来：
  `tblJoint` `tblColSeg` `tblBeamSeg` `tblWallSeg` `tblFloor` `tblStdFlr`
* **参考表 INFO_TABLES** —— 只打印、不判死。它们**本来就会合法地变**：

      tblAxis      源 1008 → 导入后 280    YJK 会把共线轴网合并
      tblSlab      源  336 → 导入后 364    YJK 会拆分/补板（现场实测值）
      tblProperty  源    2 → 导入后 5518   save 时展开参数表
      tblProjectPara 源 1169 → 导入后 1172 save 时展开总信息表

  ★ 若把 `tblSlab`/`tblAxis` 也当"必须相等"，**一对完全正确的导入会被判成失败**
  （这个坑底座上真的踩过：拿 336→364 的好样本去校验，死活不通过）。

★ 还有一条**下限**（空集闸门，fail-closed）
------------------------------------------
判据是「源 == 工程」，所以必须要求**源里真的有几何数据**：源里必判表合计 0 行时
（源是空骨架，或根本拿错了文件/换成了别的 .sqlite），逐表比对会**全部跳过** →
`bad` 恒空 → 会打印"通过"，而调用方随后还会打印一句**断言了从未发生的比较**的话
（「几何表与源 .ydb 一致」）→ 在空模型上白算一整轮。
现在这种情形一律判**不通过**，并把「源里根本没有这张表」与「源里有表但一行都没有」
**分开**说清（`-1` 与 `0` 含义不同）。

顺序要点
--------
`<工程>.ymd` 是 `yjk_save` 写出来的：**导入刚返回时该文件还不存在**，
所以校验必须排在 `yjk_save` **之后**（早于 save 会得到"打不开数据库文件"）。

用法
----
    import impcheck as IC

    ydb = IC.abs_ydb("models/S0.ydb")      # ★ 一律先转绝对路径
    cli.run("yjk_importydb", ydb, 600)
    cli.run("yjk_save", "", 300)           # ★ .ymd 是 save 才写出的
    ok, rep = IC.check(ydb, os.path.join(wd, "S0.ymd"), strict=False)
    if not ok:
        ...                                # 不通过就**别往下算**

只依赖 sqlite3（不引第三方库），因为底座要能在任何机器上单独跑。
"""
import os
import sqlite3
import time

# 必须逐表相等：这几张表决定"模型是空的还是有东西"
# ★ `tblLoadSeg` 也放在这里：**荷载条数必须逐条落地**。
#   实测过一个非常隐蔽的失败——源 ydb 里有 240 条梁上荷载，导入后 .ymd 里 0 条，
#   而 `yjk_importydb` 照样回 OK、模型也照样算得出来，只是柱轴力少掉
#   梁上隔墙线荷载那一整块（本包量级约 20%）→ 柱截面会选偏小。
#   触发条件是 `tblLoadSeg.Type`：**Type=0 会被导入整批静默丢弃，Type=1 才保留**
#   （同一模型、同一 schema，只改这一个字段：0 → 导入后 0 条；1 → 导入后 240 条）。
#   所以建梁上荷载时必须 `load_arrange(..., 1)`，见 frame_build.py。
MUST_MATCH = [
    "tblJoint", "tblColSeg", "tblBeamSeg", "tblWallSeg", "tblFloor", "tblStdFlr",
    "tblLoadSeg",
]
# 仅供参考：导入/save 会合法地改动它们（合并共线轴、拆板、展开参数表，
# 荷载定义表也会因为"每层一份"被并成一份，所以 tblLoadSect 只做参考）
INFO_TABLES = [
    "tblAxis", "tblGrid", "tblSlab", "tblBeamSect", "tblColSect",
    "tblLoadSect", "tblProperty", "tblProjectPara",
]
# 兼容旧调用点：`yjk-draw-takeoff/scripts/impcheck.py` 里同名常量含这些表
GEOM_TABLES = MUST_MATCH + INFO_TABLES

# 判据出处（写在报错里，让看日志的人知道为什么这几张表是"必判"）
WHY = ("必判表 = 证明「模型真的进来了」的最小集合；tblSlab/tblAxis/tblProperty/tblProjectPara "
       "在 save/导入时会合法变化，只做参考")


class ImportFailed(RuntimeError):
    """导入校验不通过。"""


def abs_ydb(path):
    """★ 必须用绝对路径：YJK 按自己的工作目录解析相对路径，相对路径=导入空模型。"""
    p = os.path.abspath(path)
    if not os.path.exists(p):
        raise ImportFailed("源模型不存在：%s" % p)
    return p


def _connect(p):
    return sqlite3.connect("file:%s?mode=ro" % p.replace("\\", "/"), uri=True)


def _tables(con):
    return {r[0] for r in con.execute(
        "select name from sqlite_master where type='table'")}


def counts(db, tables=None):
    """返回 {表名: 行数}；表不存在记 -1（-1 与 0 含义不同：没有表 ≠ 空表）。"""
    tables = list(tables or GEOM_TABLES)
    out = {}
    con = _connect(db)
    try:
        have = _tables(con)
        for t in tables:
            if t not in have:
                out[t] = -1
                continue
            out[t] = con.execute('select count(*) from "%s"' % t).fetchone()[0]
    finally:
        con.close()
    return out


def find_ymd(workdir):
    """在工程目录里找"计算模型库"（含 tblStdFlr 的 `*.ymd`）；找不到返回 None。

    收件箱会话里没有 `--name`，只能靠库结构认它（有 tblStdFlr 才像模型库，
    与 `env.py` 的判据一致）。优先 `g-of.ymd`（YJK 的通用名）。
    """
    try:
        names = sorted(f for f in os.listdir(workdir)
                       if f.lower().endswith(".ymd"))
    except OSError:
        return None
    for f in names:
        if f.lower() == "g-of.ymd":
            return os.path.join(workdir, f)
    for f in names:
        p = os.path.join(workdir, f)
        try:
            con = _connect(p)
            try:
                ok = "tblStdFlr" in _tables(con)
            finally:
                con.close()
        except sqlite3.Error:
            continue
        if ok:
            return p
    return None


def _loadseg_by_floor(db):
    """按**自然层层号**统计梁上荷载条数 {层号: 条数}；取不到返回 None。

    ★ 为什么要按层比而不是比总数：
      导入 + save 会把"每层一份的荷载定义表"并成一份，标准层 ID 也**重新编号**
      （实测源 1001.. 与工程重排后的 ID 根本不是同一套），条数还会被重排
      （源 4576 条 → 工程 10488 条，而逐层都是 104 → 104，一条没丢）。
      只比总数会把这种正常重排**误判成"模型没进来"**，白打断一整轮；
      而按层号比（而不是按标准层 ID）才既拦得住"整批丢失"、也不冤枉正常重排。
    """
    try:
        con = _connect(db)
    except sqlite3.Error:
        return None
    try:
        if "tblLoadSeg" not in _tables(con):
            return None
        cols = {r[1] for r in con.execute("PRAGMA table_info(tblLoadSeg)")}
        if "StdFlrID" not in cols or "tblStdFlr" not in _tables(con):
            return None
        return {r[0]: r[1] for r in con.execute(
            "select f.No_, count(*) from tblLoadSeg l "
            "join tblStdFlr f on f.ID = l.StdFlrID group by f.No_")}
    except sqlite3.Error:
        return None
    finally:
        con.close()


def _verdict_lines(a, b):
    """逐表判定。返回 (必判不一致表, 必判"整表为空"表, 参考表里有变化的表,
    源里根本没有的必判表, 源里有但整表为空的必判表)。

    ★ 后两项是**给空集闸门用**的：`-1`（表不存在）与 `0`（空表）含义不同，
      两种都要能说清 —— 前者是「拿错文件/换了别的库」，后者是「空骨架/半写」。
    """
    bad, empty, info = [], [], []
    src_absent, src_empty = [], []
    for t in MUST_MATCH:
        if a.get(t, -1) < 0:
            src_absent.append(t)     # 源里根本没有这张表（≠ 空表）
            continue                 # 源里就没有这张表，不追
        if a[t] == 0:
            src_empty.append(t)      # 源里有这张表，但一行都没有
        if b.get(t, -1) < 0:
            bad.append(t)            # 源有、工程没有 —— 也是不一致
            continue
        if b[t] != a[t]:
            bad.append(t)
            if b[t] == 0 and a[t] > 0:
                empty.append(t)
    for t in INFO_TABLES:
        if a.get(t, -1) >= 0 and b.get(t, -1) != a.get(t):
            info.append(t)
    return bad, empty, info, src_absent, src_empty


def check(src_ydb, ymd, verbose=True, strict=True, wait=20.0):
    """比对源 `.ydb` 与导入后 `.ymd` 的几何表行数。

    `wait` 秒内轮询等 `.ymd` 出现（它是 `yjk_save` 写出的，导入刚返回时可能还没有）。
    返回 (ok, 报告文本)；`strict=True` 且不通过时抛 `ImportFailed`。
    """
    t0 = time.time()
    while not os.path.exists(ymd) and time.time() - t0 < wait:
        time.sleep(0.5)
    if not os.path.exists(ymd):
        msg = ("导入校验：★不通过★ 找不到 %s\n"
               "  .ymd 由 `yjk_save` 写出 —— 校验必须排在 save 之后；"
               "若已 save 仍无此文件，说明工程根本没建立。" % ymd)
        if verbose:
            print(msg)
        if strict:
            raise ImportFailed(msg)
        return False, msg

    a, b = counts(src_ydb, GEOM_TABLES), counts(ymd, GEOM_TABLES)
    bad, empty, info, src_absent, src_empty = _verdict_lines(a, b)
    # ★ tblLoadSeg 单独放宽：导入/save 会把每层一份的荷载定义并成一份、标准层 ID
    #   重新编号、条数被重排/展开（实测 44 层塔楼：源 4576 条、每层 104 →
    #   工程 10488 条、逐层 104~240，一条没丢）。只比总数会把正常重排
    #   **误判成"模型没进来"**、白打断一整轮。这里改成**逐层**判：
    #   只要"源有荷载的层在工程里也有荷载"就放过 —— 仍拦得住 Type 写错
    #   导致的"整批静默丢弃"（那种情况工程里一条都没有）。
    load_note = None
    if "tblLoadSeg" in bad:
        la, lb = _loadseg_by_floor(src_ydb), _loadseg_by_floor(ymd)
        src_has = a.get("tblLoadSeg", 0) > 0
        dst_has = b.get("tblLoadSeg", 0) > 0
        if src_has and not dst_has:
            empty.append("tblLoadSeg")          # 整批丢失 —— 维持不通过
        elif not (src_has and dst_has):
            bad.remove("tblLoadSeg")            # 源里本来就没荷载
        else:
            bad.remove("tblLoadSeg")
            # 逐层只要"源有荷载的层，工程也有荷载"就放过：
            # 条数本身会被重排/展开（实测 44 层塔楼源每层 104，工程 104~240），
            # 真正要拦的是"整批静默丢失"（Type 写错时工程里一条都没有）。
            per = sorted(set(la or {}) | set(lb or {}))
            zero = [k for k in per if (la or {}).get(k, 0) > 0
                    and (lb or {}).get(k, 0) == 0]
            if zero:
                bad.append("tblLoadSeg")
                load_note = "这些层源有荷载、工程为 0：%s" % zero[:8]
            else:
                load_note = ("逐层都有荷载（%d 层，源每层 %s 条 → 工程 %s~%s 条，"
                             "条数被导入展开属正常）"
                             % (len(per), sorted(set((la or {}).values()))[:3],
                                min((lb or {}).values()), max((lb or {}).values())))
    # ★★ 空集闸门（fail-closed）—— 判据是「源 == 工程」，那就必须有**下限**：
    #    源里必判表合计 0 行时，逐表比对会**全部 continue** → `bad` 恒空 →
    #    本函数会打印「通过」，而调用方（yjk_auto.verify_import）随后还会打印一句
    #    **断言了从未发生的比较**的话（「几何表与源 .ydb 一致」）→ 在空模型上白算一整轮。
    #    所以先卡住下限：源里必须真的有几何数据，否则按**不通过**处理。
    src_total = sum(v for v in (a.get(t, 0) for t in MUST_MATCH) if v > 0)
    vacuous = src_total <= 0
    ok = (not bad) and (not vacuous)
    lines = ["导入校验：%s" % ("通过" if ok else "★不通过★"),
             "  %-4s %-14s %10s %10s" % ("级别", "表", "源", "工程")]
    for t in GEOM_TABLES:
        if a.get(t, -1) < 0:
            continue
        lvl = "必判" if t in MUST_MATCH else "参考"
        mark = "" if a.get(t) == b.get(t) else "   <<<"
        if mark and t in INFO_TABLES:
            mark += "（合法变化：save/导入会合并轴网、拆分板、展开参数表）"
        if mark and t == "tblLoadSeg" and t not in bad and load_note:
            mark += "（已按逐层条数复核：%s）" % load_note
        lines.append("  %-4s %-14s %10d %10d%s"
                     % (lvl, t, a.get(t, 0), b.get(t, 0), mark))
    sz_a = os.path.getsize(src_ydb) if os.path.exists(src_ydb) else -1
    sz_b = os.path.getsize(ymd) if os.path.exists(ymd) else -1
    lines.append("  字节数 %d -> %d（差 %+d，仅参考：save 会重写库）"
                 % (sz_a, sz_b, sz_b - sz_a))
    if vacuous:
        lines += [
            "=" * 68,
            "!! 导入校验 ★不通过★ —— 源模型里**没有任何几何数据**，无法判定导入是否生效",
            "!! 源里必判表合计行数 = 0：逐表比对会**全部跳过**，「通过」只说明两边一样空，",
            "!! 什么也没证明 —— 所以按不通过处理（fail-closed，不放行）。",
        ]
        if src_absent:
            lines.append("!! 源里**根本没有**这些表（拿错文件/传了结果库或别的 .sqlite）：%s"
                         % ", ".join(src_absent))
        if src_empty:
            lines.append("!! 源里**有这些表但一行都没有**（空骨架/半写状态）：%s"
                         % ", ".join(src_empty))
        lines += [
            "!! 处置：① 确认给 yjk_importydb 的是**要导的那个模型**（不是结果库、不是别的文件）；",
            "!!       ② 源模型自己就是空的 → 先把几何写进源模型，再导入；",
            "!!       ③ 重导入 + yjk_save 之后再校验一次",
            "!! 判据说明：" + WHY,
            "=" * 68,
        ]
    elif bad:
        lines += [
            "=" * 68,
            "!! 导入校验 ★不通过★ —— 模型**没有真的进来**，不许往下算",
            "!! 必判表不一致：%s" % ", ".join(
                "%s(源 %d → 工程 %d)" % (t, a.get(t, -1), b.get(t, -1)) for t in bad),
        ]
        if empty:
            lines.append("!! 整表为空：%s" % ", ".join(empty))
            lines.append("!!   典型原因：导入路径是相对路径（YJK 按自己的 CWD 解析）/ "
                         "文件不存在被放行 / 源 .ydb 本身就是半写状态")
        lines += [
            "!! 硬往下跑的后果：直到计算阶段才报 设计结果 里 fea.dat-ERR.txt"
            "「模型中没有单元数据」+ 分析失败[-45]，一整轮计算白跑",
            "!! 处置：① 重新序列化源模型（确认不是半写的库）；"
            "② yjk_importydb 一律给**绝对路径**；③ 重导入 + yjk_save 后再校验一次",
            "!! 判据说明：" + WHY,
            "=" * 68,
        ]
    elif info:
        lines.append("  （参考表变化 %s —— 正常，不算失败）" % ", ".join(info))
    if (not vacuous) and (src_absent or src_empty):
        # 通过时也要留痕：源里哪些表**本来就没有**、哪些**本来就是空表** —— 两者含义不同
        # （不通过那一支已经把这两类逐条打在上面的失败块里了，不重复）
        note = []
        if src_absent:
            note.append("源里没有这些表（未参与判定）：%s" % ", ".join(src_absent))
        if src_empty:
            note.append("源里这些表本来就是空表（未参与判定）：%s" % ", ".join(src_empty))
        lines.append("  · %s" % "；".join(note))
    txt = "\n".join(lines)
    if verbose:
        print(txt)
    if strict and not ok:
        raise ImportFailed(txt)
    return ok, txt


def check_dir(src_ydb, workdir, verbose=True, strict=True, wait=20.0):
    """工程目录版：自己找 `<工程>.ymd`（收件箱会话没有 --name 时用它）。"""
    ymd = find_ymd(workdir)
    if not ymd:
        msg = ("导入校验：★不通过★ 在 %s 里找不到模型库 `*.ymd`\n"
               "  导入 + `yjk_save` 之后工程目录里应当出现它；没有 = 工程没建立/没保存。"
               % workdir)
        if verbose:
            print(msg)
        if strict:
            raise ImportFailed(msg)
        return False, msg
    return check(src_ydb, ymd, verbose=verbose, strict=strict, wait=wait)


if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 3:
        # ★★ 命令行必须把判定**反映到退出码**上。
        #   以前这里调完 `check(..., strict=False)` 就结束 —— 于是屏幕上明明是
        #   「导入校验：★不通过★ …… 不许往下算」，**退出码却是 0**。
        #   任何按退出码判定的编排（包括 shell 的 `&&`）都会把"导入没生效"
        #   当成成功，接着在空模型上白跑一整轮。
        _ok, _ = check(sys.argv[1], sys.argv[2], strict=False)
        sys.exit(0 if _ok else 1)
    else:
        print(__doc__)
        sys.exit(0)
