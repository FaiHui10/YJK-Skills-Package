# -*- coding: utf-8 -*-
r"""把「按分组的优化方案」展开成「按柱号的优化截面清单」。

这是技能循环里缺的一环：

    sections_XX.json           （section_opt 产出：每层一个等级 + 每个分组一个边长）
          │  expand_plan.py
          ▼
    优化截面清单.json            （write_sections.py --sections 要的形式）
          │  write_sections.py
          ▼
    model_XX.ydb                （写回模型）

为什么必须有这一步
------------------
`section_opt.py` 的产出是**按分组**的（中柱/边柱/角柱 各一个边长），
而 `write_sections.py` 的 `set_sections()` 要的是**按柱号**的
`{标准层: [{"cols":[柱号...], "b":…, "h":…}]}`。
两者之间没有桥 —— 以前只能手写，本脚本补上。

★★ 分组归属**从几何推导，不写死编号**（真实教训）
------------------------------------------------
`make_spec.py` 里曾写死 `GROUP_OF = {1-4:"G1", 5-12:"G2", 13-16:"G3"}`，
那种按柱号硬编码的分组只在特定柱网成立。换成别的柱网（例如 4×3 跨 = 20 柱）
就会**把柱子分错组**，而分错组不会报错，只会把截面写到错误的柱子上。
本脚本改为：按柱子的**平面坐标**判定
    中柱 = X、Y 两个方向都在内部
    边柱 = 只有一个方向在内部
    角柱 = 两个方向都在边缘
这样对任意正交柱网都成立，也与 `column-section-opt` 模式 A 建模时
`frame_build.py` 用的判据一致。

用法:
  python expand_plan.py <模型.ydb> <sections_XX.json> <输出清单.json>
                        [--groups 中柱,边柱,角柱] [--kind 1]

另外会把 `--grades` 参数串一起打印出来（等级也得同步写回模型，
只改截面不改等级，`section_opt` 下一轮会再提出改等级，来回震荡）。
"""
import argparse
import json
import os
import sqlite3
import sys

# 几何分组名（按「由内到外」排列）。可用 --groups 覆盖以匹配 config.json 的 截面.分组。
DEFAULT_GROUPS = ("中柱", "边柱", "角柱")


def _die(msg):
    """「工具没跑成」→ **退出码 2**（与"做完了但结论/产物不合格"的 1 分开）。"""
    try:
        sys.stderr.reconfigure(errors="replace")   # GBK 控制台下也不崩
    except (AttributeError, ValueError):
        pass
    sys.stderr.write(msg.rstrip("\n") + "\n")
    sys.exit(2)


def open_ro(path):
    """只读打开模型库：存在 / 不是目录 / 非 0 字节 / 真的是 sqlite，逐条给中文报错。

    ★ 为什么不能直接 connect：`mode=ro` 对不存在的路径抛的是
      `OperationalError: unable to open database file`（不说路径、不说原因）；
      而**0 字节或非 sqlite** 的文件 `connect()` 竟然**成功**，
      `file is not a database` 要到第一条查询才抛 —— 所以四件事一次做完。
    """
    p = os.path.abspath(str(path))
    if not os.path.exists(p):
        _die("模型库不存在：%s\n"
             "  常见原因：路径拼错 / 文件还没生成 / 传了工程目录。\n"
             "  本工具**只读**打开，不会创建文件。" % p)
    if os.path.isdir(p):
        _die("给的是目录，不是模型库文件：%s" % p)
    if os.path.getsize(p) == 0:
        _die("模型库是 0 字节（半写/损坏）：%s" % p)
    try:
        con = sqlite3.connect("file:%s?mode=ro" % p.replace("\\", "/"), uri=True)
        con.execute("PRAGMA schema_version").fetchone()   # 把"不是数据库"提前探出来
    except sqlite3.Error as e:
        _die("打不开模型库 %s：%s\n"
             "  常见原因：不是 sqlite 库（拿错文件）/ 库已损坏。" % (p, e))
    con.text_factory = lambda b: b.decode("gbk", "replace")
    return con


def read_columns(path):
    """返回 {标准层No_: {"cols": {柱号: (x,y)}, "sect": {柱号: (b,h,kind)}}}。

    截面尺寸按 `idNewDef -> tblColSect.idNew` 反查——这才是 YJK 认的键
    （详见 write_sections.py 的 set_sections docstring）。
    """
    con = open_ro(path)
    try:
        flr = {r[0]: r[1] for r in con.execute("SELECT ID,No_ FROM tblStdFlr")}
        sect = {r[0]: (r[1], r[2], r[3]) for r in
                con.execute("SELECT idNew,b,h,Kind FROM tblColSect")}
        out = {}
        for fid, no, x, y, defid in con.execute(
                "SELECT s.StdFlrID, s.No_, j.X, j.Y, s.idNewDef "
                "FROM tblColSeg s JOIN tblJoint j ON j.ID = s.JtID"):
            std = flr.get(fid)
            if std is None:
                continue
            d = out.setdefault(std, {"cols": {}, "sect": {}})
            d["cols"][no] = (float(x), float(y))
            d["sect"][no] = sect.get(defid, (None, None, 1))
        return out
    finally:
        con.close()


def classify(cols):
    """按坐标把柱号分成 中柱/边柱/角柱。返回 {类别: [柱号...]}（柱号已排序）。

    ★ 判据只看柱子**本身**的坐标是否落在网格线的内部区间上，
      所以对任意正交柱网都成立，不依赖柱网跨数（不像写死编号那样会错）。
    """
    xs = sorted({round(x, 1) for x, _ in cols.values()})
    ys = sorted({round(y, 1) for _, y in cols.values()})
    xi = {v: i for i, v in enumerate(xs)}
    yi = {v: i for i, v in enumerate(ys)}
    g = {"中柱": [], "边柱": [], "角柱": []}
    for no, (x, y) in cols.items():
        inx = 0 < xi[round(x, 1)] < len(xs) - 1
        iny = 0 < yi[round(y, 1)] < len(ys) - 1
        if inx and iny:
            g["中柱"].append(no)
        elif inx or iny:
            g["边柱"].append(no)
        else:
            g["角柱"].append(no)
    for k in g:
        g[k].sort()
    return g


def side_of(val, what):
    """方案里的一个分组值 -> (b, h)。支持 450 或 {"b":450,"h":600}。"""
    if isinstance(val, dict):
        b, h = val.get("b"), val.get("h", val.get("b"))
        if b is None:
            raise SystemExit("%s 写成字典时必须有 b（可只给 b，按方柱处理）：%r" % (what, val))
        return float(b), float(h)
    if val is None:
        raise SystemExit("%s 没有给出边长（该分组可能不是柱分组？）" % what)
    return float(val), float(val)


def resolve(name, plan, groups):
    """在方案里找 name 这一组；找不到就往下一档退（角柱→边柱→中柱）。

    为什么允许退档：有些工程的 `截面.分组` 只给两级（如 ["中柱","边柱"]），
    角柱没有单独给值，实际是并进边柱的。退档把这件事自动化，
    免得手工改方案时漏掉一层。
    """
    order = list(groups)
    try:
        i = order.index(name)
    except ValueError:
        i = 0
    for k in order[i:]:
        if k in plan:
            return k, plan[k]
    raise SystemExit("方案里这些分组名一个都没有：%s（方案里实际有：%s）"
                     % (groups, [k for k in plan if k != "grade"]))


def grade_str(plan):
    """从方案里抽出 {标准层: 等级数字}，生成 write_sections.py 的 --grades 紧凑串。"""
    out = []
    for k in sorted(plan, key=int):
        g = plan[k].get("grade")
        if not g:
            continue
        n = int(str(g).lstrip("Cc"))
        if out and out[-1][1] == n and out[-1][2] + 1 == int(k):
            out[-1] = (out[-1][0], n, int(k))        # 与上一段同等级 -> 并区间
        else:
            out.append((int(k), n, int(k)))
    parts = []
    for a, n, b in out:
        parts.append("%s:%d" % (a if a == b else "%d-%d" % (a, b), n))
    return ",".join(parts)


def _utf8_console():
    """让输出在任何控制台编码下都不崩（GBK 下把不可编码字符替换掉）。

    为什么需要：本包会打印 ✅ ❌ ⚠ −(U+2212) ² ³ 等**非 cp936** 字符，
    默认 GBK 控制台下 `print` 会抛 UnicodeEncodeError 并**以退出码 1 中断**，
    于是一个其实已经成功的任务（比如文件已经落盘）会被上层判成失败；
    对 frame_build.py 那条链更糟 —— 崩在被调用的库的 print 上，模型根本没写出来。

    `errors="replace"` 让它在 UTF-8 控制台下原样输出、在 GBK 下退化成 `?`，都不崩。
    ★ 只在实际执行时调用（CLI 入口），**不在 import 时改 stdout** ——
      这些模块会被别的脚本 import 当库用（common.py / verify_results.py 就 import
      本模块的 classify/read_columns），污染 import 方的 stdout 是不对的。
    """
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass


def main():
    _utf8_console()          # ★ 必须在 argparse 之前：--help 也是写到 stdout 的
    ap = argparse.ArgumentParser(
        description="把按分组的优化方案展开成 write_sections.py 要的按柱号截面清单")
    ap.add_argument("model", help="现状模型库(.ydb/.ymd)，用来读柱网与柱号")
    ap.add_argument("plan", help="优化方案 sections_XX.json（section_opt 的产出）")
    ap.add_argument("out", help="输出的优化截面清单.json")
    ap.add_argument("--groups", default=",".join(DEFAULT_GROUPS),
                    help="分组名，由内到外，逗号分隔（默认 中柱,边柱,角柱）")
    ap.add_argument("--kind", type=int, default=1, help="截面类型（默认 1=矩形）")
    a = ap.parse_args()

    groups = tuple(s.strip() for s in a.groups.split(",") if s.strip())
    if len(groups) < 3:
        groups = groups + DEFAULT_GROUPS[len(groups):]

    columns = read_columns(a.model)
    plan = json.load(open(a.plan, encoding="utf-8"))

    out = {}
    total = 0
    fallbacks = []
    print("展开 %s -> %s" % (a.plan, a.out))
    for std in sorted(columns, key=int):
        key = str(std)
        if key not in plan:
            print("  std%-3s !! 方案里没有这一层，跳过" % key)
            continue
        p = plan[key]
        cats = classify(columns[std]["cols"])
        blocks = []
        for name in DEFAULT_GROUPS:
            nocols = cats[name]
            if not nocols:
                continue
            used, val = resolve(name, p, groups)
            if used != name:
                fallbacks.append("std%s %s->%s" % (key, name, used))
            b, h = side_of(val, "std%s %s" % (key, used))
            cur = columns[std]["sect"].get(nocols[0], (None, None, a.kind))
            blocks.append({
                "cols": nocols,
                "kind": a.kind if cur[2] in (None, 0) else int(cur[2]),
                "b": b, "h": h,
                "原": ("%g×%g" % (cur[0], cur[1])) if cur[0] else "?",
                "优化": "%g×%g" % (b, h),
                # ★ 分组名随数据一起走：下游（make_spec.py 的 --keep 等）直接读它，
                #   不必再靠「柱号 -> 组」的写死映射反查（那种映射只在特定柱网成立，
                #   换柱网就分错组，且分错组不报错，只把截面写到错的柱子上）。
                "组": name,
            })
            total += len(nocols)
        # 兜底：几何上分不进三档的柱子（不应发生）也要有个交代
        got = {c for blk in blocks for c in blk["cols"]}
        miss = sorted(set(columns[std]["cols"]) - got)
        if miss:
            print("  std%-3s !! 这些柱号没被分组覆盖：%s" % (key, miss))
        out[key] = blocks
        print("  std%-3s 等级 %-4s %s" % (
            key, p.get("grade", "?"),
            "  ".join("%s=%g×%g(%d根 %s)" % (
                blk["组"], blk["b"], blk["h"], len(blk["cols"]), blk["原"])
                for blk in blocks)))

    json.dump(out, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print()
    print("已写出 %s（%d 个标准层 / %d 个柱段）" % (a.out, len(out), total))
    if fallbacks:
        print("退档取值：%s" % "，".join(fallbacks))
    gs = grade_str(plan)
    if gs:
        print()
        print("★ 等级也要一起写回，否则下一轮会来回震荡。完整命令：")
        print('  write_sections.py <src.ydb> <dst.ydb> --grades "%s" \\' % gs)
        print('                    --sections %s' % a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
