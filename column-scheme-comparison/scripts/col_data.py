# -*- coding: utf-8 -*-
"""从 YJK 设计结果 wpj*.out 提取逐柱段设计数据（两种柱形式的共同荷载输入）。

数据源（全部来自 YJK 实算结果，非假定）：
  <设计结果>/wpj<自然层>.out  —— 每层每根柱：b,h,等级,层高Lc,λc,Nu,Uc,Rs,Rsv,四边配筋,短柱标记
  <模型>.ydb                 —— tblFloor.StdFlrID + tblStdFlr.No_ 给出 自然层→标准层 映射；
                                tblColSeg JOIN tblJoint 给出柱平面坐标（用于分组）

用法:
  python col_data.py [--res <设计结果目录>] [--ydb <模型.ydb>] [--out <输出.json>]

★ 不写死任何工程的路径与柱号分组
--------------------------------
不把任何工程的路径与柱号分组写死在文件里（写死就只能跑那一个工程）。
路径由 `--res` / `--ydb`（或环境变量 `YJK_COL_RES` / `YJK_COL_YDB`）给出，
分组按柱**平面坐标**现算（判据与 column-section-opt/expand_plan.py 一致）。

★ 输出路径
  默认写到**当前工作目录**（--out 可覆盖），不再写进技能包自身的 scripts/ 目录。
  输入全部来自命令行参数，没有写到脚本目录的输出。

输出：柱设计数据.json

缺数据不算成功
  关键字段（Nu/Uc/Rs/Rsv、Ast/弯矩、层高、计算长度）任何一项缺失，或某个自然层没有
  wpj 文件、整层解析不出柱段时：打印缺项明细并以非零退出码结束，**不写出 JSON**
  （兜底成 0 会让下游算出一个更便宜、更细的方案；留下半成品会被下游按"文件存在"取用）。
  柱位分组映射缺失（柱号在模型库里没有对应柱段）不是致命项：醒目提示并记入 meta
  （分组缺失段数 / 分组缺失自然层），下游按独立设计点处理；加 --strict 可按失败退出。
"""
import argparse
import json
import math
import os
import re
import sqlite3
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(ROOT)
# 设计结果目录：可用 --res 或环境变量 YJK_COL_RES 覆盖
RES = os.environ.get("YJK_COL_RES") or os.path.join(PROJ, "设计结果")
# 模型库**没有合理默认值**（每个工程不同）→ 必须用 --ydb 显式给出，否则报错退出
YDB = os.environ.get("YJK_COL_YDB") or ""

# 柱位分组：组号顺序与 column-section-opt/expand_plan.py 的 DEFAULT_GROUPS 一致
#   G1 = 中柱（X、Y 都在内部） / G2 = 边柱（只一个方向在内部） / G3 = 角柱
GROUPS = ["G1", "G2", "G3"]
GROUP_NAME = {"G1": "G1 中柱", "G2": "G2 边柱", "G3": "G3 角柱"}

RE_COL = re.compile(r"^\s*N-C=(\d+)\s+\(I=\d+,\s*J=\d+\)(?:\(\d+\))?B\*H\(mm\)=\s*(\d+)\*(\d+)")
# 注意：wpj 的 Cx/Cy 是 X/Y 向「计算长度系数」，Lcx/Lcy 是 X/Y 向「柱段设计长度(m)」。
# 跃层柱的 Lcx/Lcy 等于所跨多个自然层层高之和（如 柱5 在自然层1 Lcy=11.00=6.0+5.0），
# 因此 计算长度 L0 = 系数 × 本方向长度，两个方向必须各取各的，不能混用 Lcx。
RE_GEO = re.compile(r"Cover=\s*([\d.]+)\(mm\)\s*Cx=\s*([\d.]+)\s*Cy=\s*([\d.]+)\s*"
                    r"Lcx=\s*([\d.]+)\(m\)\s*Lcy=\s*([\d.]+)\(m\)")
RE_GRADE = re.compile(r"砼柱\s+(C\d+)")
RE_LC = re.compile(r"([XY]):\s*λc=\s*([\d.]+)")
RE_CTRL = re.compile(r"\(\s*(\d+)\)\s*Nu=\s*([-\d.]+)\s+Uc=\s*([-\d.]+)\s+"
                     r"Rs=\s*([\d.]+)\(%\)\s+Rsv=\s*([\d.]+)\(%\)\s+Asc=\s*(\d+)")
RE_AS = re.compile(r"^\s*\(\s*(\d+)\)\s*N=\s*([-\d.]+)\s+Mx=\s*([-\d.]+)\s+My=\s*([-\d.]+)\s+"
                   r"(As[xy][tb])=\s*(\d+)")


def _utf8_console():
    """让输出在任何控制台编码下都不崩（GBK 下把不可编码字符替换掉）。

    为什么需要：本文件的收尾统计里有 m³、m² 等非 cp936 字符，默认 GBK 控制台下
    `print` 会抛 UnicodeEncodeError 并以非零退出码中断 —— 文件其实已经写出，
    但命令以失败收场，容易被上层误判。`errors="replace"` 让它在 UTF-8 控制台下
    原样输出、在 GBK 下退化成 `?`，都不崩。

    只在 main() 开头调用一次，不在 import 时改 stdout（本模块会被别的脚本 import 当库用）。
    """
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass


def _ro(path):
    return sqlite3.connect("file:%s?mode=ro" % path.replace("\\", "/"), uri=True)


def std_floor_map(ydb=None):
    """自然层 -> 标准层号，来自 tblStdFlr.No_ / tblFloor.StdFlrID。"""
    con = _ro(ydb or YDB)
    ids = {r[0]: r[1] for r in con.execute("select ID,No_ from tblStdFlr")}
    out = {}
    for no, sid in con.execute("select No_,StdFlrID from tblFloor"):
        out[int(no)] = int(ids[sid])
    con.close()
    return out


def floor_height_map(ydb=None):
    """自然层 -> 实际层高(m)，来自 tblFloor.Height。

    ★ 必须用 tblFloor.Height（自然层实际层高），不能用 tblStdFlr.Height：
      后者只是标准层代表值，同标准层的各自然层实际层高可能不同，
      拿代表值算工程量会偏。
    """
    con = _ro(ydb or YDB)
    out = {int(no): float(h) / 1000.0 for no, h in
           con.execute("select No_,Height from tblFloor")}
    con.close()
    return out


def col_groups(ydb=None):
    """{标准层No_: {柱号: "G1"|"G2"|"G3"}} —— 按柱**平面坐标**分组。

    中柱 = X、Y 两个方向都在内部；边柱 = 只有一个方向在内部；角柱 = 两个都在边缘。
    判据只看柱子自身坐标是否落在网格线内部区间上，对任意正交柱网都成立。

    ★ 为什么不写死柱号：`GROUP_OF = {1-4:G1, 5-12:G2, 13-16:G3}` 这类表
      只在特定柱网成立。换柱网会把柱子分错组，而分错组**不会报错**，
      只会把截面与造价算到错的柱子上，结论全错还看不出来。
    """
    con = _ro(ydb or YDB)
    flr = {r[0]: r[1] for r in con.execute("SELECT ID,No_ FROM tblStdFlr")}
    pts = {}
    for fid, no, x, y in con.execute(
            "SELECT s.StdFlrID, s.No_, j.X, j.Y "
            "FROM tblColSeg s JOIN tblJoint j ON j.ID = s.JtID"):
        std = flr.get(fid)
        if std is None:
            continue
        pts.setdefault(std, {})[int(no)] = (float(x), float(y))
    con.close()
    out = {}
    for std, cols in pts.items():
        xs = sorted({round(x, 1) for x, _ in cols.values()})
        ys = sorted({round(y, 1) for _, y in cols.values()})
        xi = {v: i for i, v in enumerate(xs)}
        yi = {v: i for i, v in enumerate(ys)}
        g = {}
        for no, (x, y) in cols.items():
            inx = 0 < xi[round(x, 1)] < len(xs) - 1
            iny = 0 < yi[round(y, 1)] < len(ys) - 1
            g[no] = "G1" if (inx and iny) else ("G2" if (inx or iny) else "G3")
        out[std] = g
    return out


def parse_wpj(path):
    """解析一层 wpj，返回 {柱号: 记录}。"""
    rows, cur = {}, None
    edge = {}       # 组合号 -> 四边配筋之和
    cmom = {}       # 组合号 -> (Mx, My)
    txt = open(path, encoding="gbk", errors="replace").read()
    for line in txt.splitlines():
        m = RE_COL.match(line)
        if m:
            if cur:
                _finish(cur, edge, cmom)
                rows[cur["nc"]] = cur
            cur = {"nc": int(m.group(1)), "B": int(m.group(2)), "H": int(m.group(3)),
                   "cover": 20.0, "grade": None, "Lc": None, "short": False,
                   "lamX": None, "lamY": None, "Cx": None, "Cy": None,
                   "Lcx": None, "Lcy": None,
                   "Nu": None, "Uc": None,
                   "Rs": None, "Rsv": None, "Asc": 0, "Ast": 0,
                   "M_comp_absmax": 0.0, "M_res_absmax": 0.0,
                   "MyAtNmax": 0.0}
            edge, cmom = {}, {}
            continue
        if cur is None:
            continue
        if "短柱" in line:
            cur["short"] = True
        m = RE_GRADE.search(line)
        if m and cur["grade"] is None:
            cur["grade"] = m.group(1)
        m = RE_GEO.search(line)
        if m:
            cur["cover"] = float(m.group(1))
            cur["Cx"] = float(m.group(2))
            cur["Cy"] = float(m.group(3))
            cur["Lc"] = float(m.group(4))       # 保留 = Lcx（兼容旧字段名）
            cur["Lcx"] = float(m.group(4))
            cur["Lcy"] = float(m.group(5))
        m = RE_LC.match(line.strip())
        if m:
            cur["lamX" if m.group(1) == "X" else "lamY"] = float(m.group(2))
        m = RE_CTRL.search(line)
        if m:
            nu, uc, rs, rsv, asc = (float(m.group(i)) for i in (2, 3, 4, 5, 6))
            if cur["Uc"] is None or uc > cur["Uc"]:
                cur.update(Nu=nu, Uc=uc, Rs=rs, Rsv=rsv, Asc=asc)
        m = RE_AS.match(line)
        if m:
            cid = int(m.group(1))
            mx, my = float(m.group(3)), float(m.group(4))
            edge[cid] = edge.get(cid, 0) + int(m.group(6))
            cmom[cid] = (mx, my)
            # 弯矩包络：同一组合的柱两端弯矩不同，必须逐条取包络，不能只留最后一次
            cur["M_comp_absmax"] = max(cur["M_comp_absmax"], abs(mx), abs(my))
            cur["M_res_absmax"] = max(cur["M_res_absmax"], math.hypot(mx, my))
    if cur:
        _finish(cur, edge, cmom)
        rows[cur["nc"]] = cur
    return rows


def _finish(cur, edge, cmom):
    """四边配筋之和 - 4×角筋 即为纵筋总面积（角筋在相邻两边各计 1 次）。

    本柱段一条配筋行都没匹配到时，**不把纵筋面积与弯矩兜底成 0**：
    置 0 会让下游 Mmax=0 → 截面选得更小、纵筋造价算成 0（S1 偏便宜），
    报告只会显示一个更便宜、更细的方案，而看不出「这层没解析到配筋」。
    改为留 None + 打「配筋缺失」标记，由 main() 汇总后显式失败。
    """
    if not edge:
        cur["Ast"] = None
        cur["M_comp_absmax"] = None
        cur["M_res_absmax"] = None
        cur["Mmax"] = None
        cur["配筋缺失"] = True
        return
    cid = max(edge, key=lambda k: edge[k])
    cur["Ast_raw"] = edge[cid]
    cur["Ast"] = max(edge[cid] - 4 * cur["Asc"], 0)
    cur["Ast_combo"] = cid
    # 弯矩包络已在解析时逐条累计（同一组合的柱两端 Mx/My 不同，不能用最后一条）：
    #   M_comp_absmax = 各方向分量绝对值的最大值（偏保守的正交双偏压分向包络）
    #   M_res_absmax  = 各组合合弯矩 √(Mx²+My²) 的最大值（单向压弯验算用，偏安全）
    cur["Mmax"] = cur["M_res_absmax"]
    cur["Mx_sum"] = cmom[cid][0]
    cur["My_sum"] = cmom[cid][1]


def _missing_fields(rec):
    """返回该柱段缺失的必备字段名；空列表表示齐全。

    这些字段全部来自 wpj 的实算行，缺任何一项都不能兜底（兜底成 0 会让下游
    算出偏便宜、偏细的方案，或直接崩溃）。
    """
    lack = [k for k in ("Nu", "Uc", "Rs", "Rsv", "Ast", "Mmax", "L0_m", "层高_m")
            if rec.get(k) is None]
    if not rec.get("混凝土"):
        lack.append("混凝土")
    return lack


def main():
    _utf8_console()          # 必须在 argparse 之前：--help 也写到 stdout
    ap = argparse.ArgumentParser(description="从 wpj*.out + 模型库提取逐柱段设计数据")
    ap.add_argument("--res", default=RES, help="设计结果目录（含 wpj*.out）")
    ap.add_argument("--ydb", required=not YDB, default=YDB,
                    help="模型库(.ydb/.ymd)：读楼层映射与柱平面坐标。★ 必填"
                         "（每个工程的模型都不同，没有可用的默认值）")
    ap.add_argument("--out", default=None,
                    help="输出 柱设计数据.json 的路径；默认写到当前工作目录")
    ap.add_argument("--strict", action="store_true",
                    help="柱位分组映射缺失（柱号在模型库中没有对应柱段）也按失败退出；"
                         "默认只醒目提示并记入 meta（真实工程常见，下游按独立设计点处理）")
    a = ap.parse_args()
    if not os.path.isdir(a.res):
        raise SystemExit("找不到设计结果目录：%s\n请用 --res 指定" % a.res)
    if not a.ydb or not os.path.exists(a.ydb):
        raise SystemExit("找不到模型库：%s\n请用 --ydb 指定" % (a.ydb or "(未给)"))
    out_path = a.out or os.path.join(os.getcwd(), "柱设计数据.json")

    s2f = std_floor_map(a.ydb)
    fh = floor_height_map(a.ydb)
    cg = col_groups(a.ydb)          # {标准层: {柱号: 组}}，按坐标现算
    problems = []                   # 致命：关键数据缺失 -> 打印明细后非零退出，不写 JSON
    warnings = []                   # 非致命：柱位分组映射缺失 -> 醒目提示并记入 meta
    ungrp_by_flr = {}
    out = []
    for nat in sorted(s2f):
        p = os.path.join(a.res, "wpj%d.out" % nat)
        if not os.path.exists(p):
            problems.append("自然层 %d：缺 %s（该层没有设计结果文件）"
                            % (nat, os.path.basename(p)))
            continue
        H = fh.get(nat)                              # 实际层高(m)，用于工程量
        if H is None:
            problems.append("自然层 %d：模型库 tblFloor 里没有该层层高" % nat)
            continue
        rows_n = parse_wpj(p)
        if not rows_n:
            problems.append("自然层 %d：%s 未解析出任何柱段（文件被截断或格式不符）"
                            % (nat, os.path.basename(p)))
            continue
        gmap = cg.get(s2f[nat], {})
        for nc, r in sorted(rows_n.items()):
            # r["Ast"] 已是 四边配筋之和 − 4×角筋（角筋在相邻两边各计 1 次）；缺配筋行时为 None
            ast_total = r["Ast"]
            if None in (r["Cx"], r["Cy"], r["Lcx"], r["Lcy"]):
                L0x = L0y = None                     # 缺 Cover/Cx/Lcx 行 -> 缺就是缺，不猜
            else:
                L0x = round(r["Cx"] * r["Lcx"], 3)   # 计算长度 = 计算长度系数 × 本方向柱段长
                L0y = round(r["Cy"] * r["Lcy"], 3)
            grp = gmap.get(nc)                       # 柱号对不上模型库柱段号时为 None
            if not grp:
                ungrp_by_flr[nat] = ungrp_by_flr.get(nat, 0) + 1
            rec = {
                "自然层": nat, "标准层": s2f[nat], "柱号": nc, "组": grp or "?",
                "b": r["B"], "h": r["H"], "混凝土": r["grade"], "Lc": r["Lc"],
                "cover": r["cover"], "短柱": r["short"],
                "lamX": r["lamX"], "lamY": r["lamY"],
                "Cx": r["Cx"], "Cy": r["Cy"],
                "Lcx": r["Lcx"], "Lcy": r["Lcy"],
                "层高_m": H,
                "L0x_m": L0x, "L0y_m": L0y,
                "L0_m": max(L0x, L0y) if (L0x is not None and L0y is not None) else None,
                "跃层": (bool(max(r["Lcx"], r["Lcy"]) > H * 1.05)
                         if (r["Lcx"] is not None and r["Lcy"] is not None) else None),
                "Nu": r["Nu"], "Uc": r["Uc"], "Rs": r["Rs"], "Rsv": r["Rsv"],
                "Asc": r["Asc"], "Ast_四边和": r.get("Ast_raw"), "Ast": ast_total,
                "ρ纵%": (round(ast_total / (r["B"] * r["H"]) * 100, 3)
                         if ast_total is not None else None),
                "ρ_Rs%": r["Rs"],
                "Ast_Rs": (round(r["Rs"] / 100.0 * r["B"] * r["H"])
                           if r["Rs"] is not None else None),
                "Mmax": round(r["Mmax"], 1) if r.get("Mmax") is not None else None,
                "M合_kNm": (round(r["M_res_absmax"], 1)
                            if r.get("M_res_absmax") is not None else None),
                "M分向_kNm": (round(r["M_comp_absmax"], 1)
                              if r.get("M_comp_absmax") is not None else None),
                "Mx_控制组合": r.get("Mx_sum"), "My_控制组合": r.get("My_sum"),
                "A_con_mm2": r["B"] * r["H"],
                "perim_mm": 2 * (r["B"] + r["H"]),
                # 工程量按「实际层高」计（跃层柱在每个自然层各计一段，不重复）
                "V_con_m3": round(r["B"] * r["H"] / 1e6 * H, 4),
                "A_form_m2": round(2 * (r["B"] + r["H"]) / 1000.0 * H, 4),
            }
            if r.get("配筋缺失"):
                rec["配筋缺失"] = True
            if not grp:
                rec["分组缺失"] = True      # 组号对不上模型库柱段号：缺就是缺，逐行留痕
            out.append(rec)

    # 关键字段缺失：按自然层汇总（逐段打印会把屏幕刷满），不做任何兜底
    miss_by = {}
    for rec in out:
        lack = _missing_fields(rec)
        if not lack:
            continue
        m = miss_by.setdefault(rec["自然层"], {"n": 0, "fields": {}})
        m["n"] += 1
        for k in lack:
            m["fields"][k] = m["fields"].get(k, 0) + 1
    for nat in sorted(miss_by):
        m = miss_by[nat]
        problems.append("自然层 %d：%d 个柱段缺 %s（wpj%d.out 里没有对应的控制行/配筋行/几何行）"
                        % (nat, m["n"],
                           "、".join("%s %d 段" % (k, v)
                                     for k, v in sorted(m["fields"].items())), nat))
    if ungrp_by_flr:
        warnings.append("柱位分组映射缺失：%d 个柱段的柱号在模型库 tblColSeg 里找不到对应柱段，"
                        "组记为「?」（未归组），下游按独立设计点参与选型与造价 —— "
                        "根因是 wpj 的 N-C= 与模型库柱段号不一致，须核对柱号口径"
                        % sum(ungrp_by_flr.values()))
        warnings.append("　　分布（自然层: 段数）：%s"
                        % "，".join("自然层%d: %d 段" % (k, v)
                                   for k, v in sorted(ungrp_by_flr.items())))
    for w in warnings:
        print("!! %s" % w)
    for q in problems:
        print("!! %s" % q)
    if problems or (a.strict and warnings):
        # 缺数据不算成功：缺项不按 0 兜底，也不留下半成品 JSON（下游会按"文件存在"取用）
        print("!! 本次未写出 %s：缺数据不按 0 兜底，请补齐后重跑。" % out_path)
        raise SystemExit(1)

    out.sort(key=lambda x: (x["自然层"], x["柱号"]))
    ncols = max((sum(1 for r in out if r["自然层"] == nat)
                 for nat in sorted(s2f)), default=0)
    meta = {
        "源": "%s/wpj*.out" % os.path.basename(os.path.normpath(a.res)),
        "模型": os.path.basename(a.ydb),
        "自然层数": max(s2f), "标准层数": max(s2f.values()),
        "柱段数": len(out), "每层柱数": ncols,
        "自然层→标准层": {str(k): v for k, v in sorted(s2f.items())},
        "自然层→层高m": {str(k): v for k, v in sorted(fh.items())},
        "总高_m": round(sum(fh.values()), 3),
        "跃层柱段数": sum(1 for r in out if r["跃层"]),
        "分组": {g: GROUP_NAME[g] for g in GROUPS},
        # 柱位分组映射缺失（缺就是缺，不掩盖成合法组号）
        "分组缺失段数": sum(ungrp_by_flr.values()),
        "分组缺失自然层": {str(k): v for k, v in sorted(ungrp_by_flr.items())},
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"meta": meta, "rows": out}, f, ensure_ascii=False, indent=1)

    print("柱段数 = %d（%d 层 × 最多 %d 柱），总高 %.1f m，跃层柱段 %d 个"
          % (len(out), max(s2f), ncols, sum(fh.values()), meta["跃层柱段数"]))
    print("\n标准层 | 组 | 截面 | 等级 | 层高区间 | Nu_max(kN) | 控制柱 | Uc | Rs% | 短柱 | L0max")
    agg = {}
    for r in out:
        k = (r["标准层"], r["组"])
        a = agg.setdefault(k, {"n": 0, "sec": set(), "g": set(), "Nu": 0, "Uc": 0,
                               "Rs": 0, "Rsv": 0, "sh": 0, "pos": None,
                               "hs": set(), "L0": 0, "V": 0.0, "F": 0.0})
        a["n"] += 1
        a["sec"].add("%d×%d" % (r["b"], r["h"]))
        a["g"].add(r["混凝土"])
        if abs(r["Nu"]) > abs(a["Nu"]):
            a["Nu"] = r["Nu"]
            a["pos"] = "柱%d 自然层%d" % (r["柱号"], r["自然层"])
        a["Uc"] = max(a["Uc"], r["Uc"])
        a["Rs"] = max(a["Rs"], r["ρ纵%"])
        a["Rsv"] = max(a["Rsv"], r["Rsv"])
        a["sh"] += 1 if r["短柱"] else 0
        a["hs"].add(r["层高_m"])
        a["L0"] = max(a["L0"], r["L0_m"])
        a["V"] += r["V_con_m3"]
        a["F"] += r["A_form_m2"]
    totV = totF = 0.0
    for k in sorted(agg):
        a = agg[k]
        totV += a["V"]; totF += a["F"]
        print("  %d   %s  %-10s %-5s %-11s %10.1f  %-13s %.2f %.2f  %d/%d  %.2fm"
              % (k[0], k[1], "/".join(sorted(a["sec"])), "/".join(sorted(a["g"])),
                 "/".join("%.1f" % h for h in sorted(a["hs"])), a["Nu"], a["pos"],
                 a["Uc"], a["Rs"], a["sh"], a["n"], a["L0"]))
    print("\n混凝土体积合计 %.1f m³（仅柱），柱模板面积合计 %.1f m²" % (totV, totF))
    print("已写出 -> %s" % out_path)


if __name__ == "__main__":
    main()
