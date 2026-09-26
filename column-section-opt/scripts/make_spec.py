# -*- coding: utf-8 -*-
r"""生成「分组折减」的柱截面清单：以模型现状截面为底，只对指定分组套用优化尺寸。

用途：某分组（如 G3 角柱）优化后出现配筋率/轴压比超限时，可以让它保持现状，
其余分组照常折减，避免整轮方案作废。

用法:
  python make_spec.py <现状模型.ydb|.ymd> <优化截面清单.json> <输出.json>
                      [--keep 角柱] [--keep 角柱,边柱]

读取现状截面的方式：按 `tblColSeg.idNewDef -> tblColSect.idNew` 反查
（这才是 YJK 认的键，见 write_sections.py 的 set_sections docstring）。

★★ 分组名从数据里读，**不写死柱号**
------------------------------------
不写死 `GROUP_OF` 这类按柱号硬编码的分组表 —— 那种表只在特定柱网成立，
16 柱的编号规律，换个柱网就把柱子分错组，而分错组**不会报错**，只会把截面
写到错误的柱子上。现在 `expand_plan.py` 会把 `"组"` 字段写进每个块，
本脚本直接读它；万一输入是手写的、没有 `"组"` 字段，就按块的出现顺序
退化为 G1/G2/G3（并在输出里提示）。
"""
import argparse
import json
import os
import sqlite3
import sys


def _die(msg):
    """「工具没跑成」→ **退出码 2**（与"做完了但结论/产物不合格"的 1 分开）。"""
    try:
        sys.stderr.reconfigure(errors="replace")   # GBK 控制台下也不崩
    except (AttributeError, ValueError):
        pass
    sys.stderr.write(msg.rstrip("\n") + "\n")
    sys.exit(2)


def load_current(path):
    """返回 {(标准层No_, 柱号): (b, h)}——按 idNewDef 反查的真实截面。

    ★ 打开前先守卫（存在/不是目录/非 0 字节/真的是 sqlite）：`mode=ro` 对错路径
      抛的是裸 `OperationalError: unable to open database file`（不说路径也不说原因），
      而 0 字节/非 sqlite 的文件 connect **成功**、报错推迟到第一条查询。
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
    try:
        flr = {r[0]: r[1] for r in con.execute("SELECT ID,No_ FROM tblStdFlr")}
        sect = {r[0]: (r[1], r[2]) for r in
                con.execute("SELECT idNew,b,h FROM tblColSect")}
        cur = {}
        for fid, no, defid in con.execute(
                "SELECT StdFlrID,No_,idNewDef FROM tblColSeg"):
            std = flr.get(fid)
            if std is not None and defid in sect:
                cur[(std, no)] = sect[defid]
        return cur
    finally:
        con.close()


def group_label(block, index):
    """块的组名：优先读 `组` 字段，否则按出现顺序退化 G1/G2/G3。"""
    g = block.get("组")
    if g:
        return str(g)
    return "G%d" % (index + 1)


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
    ap = argparse.ArgumentParser()
    ap.add_argument("model")
    ap.add_argument("spec")
    ap.add_argument("out")
    ap.add_argument("--keep", default="",
                    help="保持现状截面的分组名，如 角柱 或 角柱,边柱（也接受 G3/G2,G3）")
    a = ap.parse_args()

    keep = {s.strip() for s in a.keep.split(",") if s.strip()}
    keep_upper = {s.upper() for s in keep}          # 兼容 G1/G2/G3 写法
    current = load_current(a.model)
    spec = json.load(open(a.spec, encoding="utf-8"))
    out = {}
    nsame = nchg = 0
    degraded = False
    for std_key in sorted(spec, key=int):
        std = int(std_key)
        blocks = []
        for i, grp in enumerate(spec[std_key]):
            g = group_label(grp, i)
            if "组" not in grp:
                degraded = True
            hit = (g in keep) or (g.upper() in keep_upper)
            if hit:
                b, h = current.get((std, grp["cols"][0]), (grp["b"], grp["h"]))
                if (round(b), round(h)) == (round(grp["b"]), round(grp["h"])):
                    nsame += 1
                else:
                    nchg += 1
                blocks.append({**grp, "组": g, "b": float(b), "h": float(h),
                               "来源": "现状(未折减)"})
            else:
                blocks.append({**grp, "组": g, "来源": "优化"})
        out[std_key] = blocks
    json.dump(out, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("已写出 %s" % a.out)
    print("  保持现状的分组 %s -> %d 个分组改了尺寸 / %d 个原本就与优化值相同"
          % (sorted(keep) or "无", nchg, nsame))
    if degraded:
        print("  ！输入清单里没有「组」字段，已按出现顺序退化为 G1/G2/G3 —— "
              "建议改用 expand_plan.py 生成的清单（组名随数据走，换柱网不会分错组）")
    for std_key in sorted(out, key=int):
        print("   std%-3s %s" % (std_key, "  ".join(
            "%s=%g×%g(%s)" % (x["组"], x["b"], x["h"], x["来源"])
            for x in out[std_key])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
