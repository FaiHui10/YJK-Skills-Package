# -*- coding: utf-8 -*-
"""框架柱截面形式经济比选 —— 生成 Excel 分析报告。

用法： python report_xlsx.py [--project <工程名>] [--out <xlsx>]
                            [--system <结构体系>] [--seismic <抗震等级>]
                            [--data <柱设计数据.json>] [--cost <造价对比.json>]
输入： 造价对比.json、柱设计数据.json（默认取当前工作目录，找不到时回退脚本目录）
输出： 柱形式比选经济对比报告.xlsx（默认写到当前工作目录，可用 --out 改名）

计价依据：广东省房屋建筑与装饰工程综合定额(2018) + 广州市信息价；
          钢管混凝土承载力按 GB 50936-2014。

★ 工程名、结构体系、抗震等级等**由参数给出**（默认从 `柱设计数据.json` 的
  meta 里取模型名），不写死任何具体工程。

★ X12 铁律（报告不许说假话）
  正文里凡是**能从本次数据算出来**的数字（柱段数、设计点数、各组倍数、面积、
  利用率极值、θ/径厚比/壁厚极值、敏感性差距…）一律现算，禁止写死；
  凡**确实推不出来**或**属于人工判断/规范给定的外部值**，必须紧挨着数字标注
  `MANUAL`（＝「人工填写/待确认」），与算出来的数分开，绝不用看起来像结论的假数字。
"""
import argparse
import collections
import json
import math
import os
import re
import sys

from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

import cfst_design as C
import gz_quota as G

ROOT = os.path.dirname(os.path.abspath(__file__))
# ★ 默认输出到「当前工作目录」，不写进技能包自身（可 --out 覆盖）
OUT_NAME = "柱形式比选经济对比报告.xlsx"

# 人工填写/待确认标记：只用于「推不出来」或「人工判断/规范给定」的内容
MANUAL = "【人工填写/待确认】"

TITLE = Font(bold=True, size=14)
HEAD = Font(bold=True, color="FFFFFF", size=10)
HEAD_FILL = PatternFill("solid", fgColor="4F6228")
SUB_FILL = PatternFill("solid", fgColor="D8E4BC")
OK = PatternFill("solid", fgColor="E2EFDA")
WARN = PatternFill("solid", fgColor="FFF2CC")
BAD = PatternFill("solid", fgColor="FFC7CE")
THIN = Side(style="thin", color="999999")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
N0, N2, N3, PCT = "#,##0", "#,##0.00", "0.000", "0.0%"

ORDER = ["S1", "S2", "S3", "S4", "S5", "S6"]
SHORT = {"S1": "S1 钢筋混凝土柱（现状实配方案）",
         "S2": "S2 矩形钢管混凝土（外轮廓=原柱 b×h）",
         "S3": "S3 圆钢管混凝土（等外轮廓面积 D=√(4bh/π)）",
         "S4": "S4 圆钢管混凝土（外径造价最优）",
         "S5": "S5 圆钢管混凝土（不限θ，理论下限）",
         "S6": "S6 矩形钢管混凝土（边长造价最优）"}


def head(ws, row, titles, widths, h=32):
    for c, t in enumerate(titles, start=1):
        cell = ws.cell(row=row, column=c, value=t)
        cell.font, cell.fill = HEAD, HEAD_FILL
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = BORDER
    for c, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(c)].width = w
    ws.row_dimensions[row].height = h


def put(ws, row, values, fmts=None, fill=None):
    for c, v in enumerate(values, start=1):
        cell = ws.cell(row=row, column=c, value=v)
        cell.border = BORDER
        cell.font = Font(size=10)
        cell.alignment = Alignment(vertical="center")
        if fmts and c - 1 < len(fmts) and fmts[c - 1]:
            cell.number_format = fmts[c - 1]
        if fill:
            cell.fill = fill
    return row + 1


def _outline_area(txt):
    """'1350×1000' 或 '1000' -> 外轮廓面积 m²。"""
    m = re.match(r"^(\d+)×(\d+)$", str(txt))
    if m:
        return int(m.group(1)) * int(m.group(2)) / 1e6
    return math.pi / 4.0 * float(txt) ** 2 / 1e6


def _min_side(txt):
    """'1350×1000' -> 1000；'600' -> 600（矩形截面的短边，用于 b/t 校核）。"""
    m = re.match(r"^(\d+)×(\d+)$", str(txt))
    if m:
        return float(min(int(m.group(1)), int(m.group(2))))
    return float(txt)


def _resolve_input(explicit, name):
    """输入 JSON 的解析顺序：显式路径 > 当前工作目录 > 脚本所在目录。

    ★ 上游 col_data.py / cost_model.py 默认把结果写到「当前工作目录」，
      因此这里默认也从当前工作目录读；老用法（把 json 放在脚本目录里跑）仍可用。
    """
    if explicit:
        return explicit
    cwd_p = os.path.join(os.getcwd(), name)
    if os.path.exists(cwd_p):
        return cwd_p
    return os.path.join(ROOT, name)


def _utf8_console():
    """让输出在任何控制台编码下都不崩（GBK 下把不可编码字符替换掉）。

    为什么需要：本包会打印 ✅ ❌ ⚠ −(U+2212) ² ³ 等**非 cp936** 字符，
    默认 GBK 控制台下 `print` 会抛 UnicodeEncodeError 并**以退出码 1 中断**，
    于是一个其实已经成功的任务（比如文件已经落盘）会被上层判成失败；
    对 frame_build.py 那条链更糟 —— 崩在被调用的库的 print 上，模型根本没写出来。

    `errors="replace"` 让它在 UTF-8 控制台下原样输出、在 GBK 下退化成 `?`，都不崩。
    ★ 只在实际执行时调用（CLI 入口），**不在 import 时改 stdout** ——
      这些模块会被别的脚本 import 当库用，污染 import 方的 stdout 是不对的。
    ★ 本文件还要替**被它 import 的纯库**兜底：`cfst_design.py`（`★口径提示` /
      `thinnest 选型口径` 两处 print）与 `gz_quota.py` 都是库、没有 `__main__`，
      它们的 print 跑在**本进程**的 stdout 上，所以只能在调用方（这里）兜。
    """
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass


def main():
    _utf8_console()          # ★ 必须在 argparse 之前：--help 也是写到 stdout 的
    ap = argparse.ArgumentParser(description="生成柱截面形式经济比选 Excel 报告")
    ap.add_argument("--project", default=None,
                    help="工程名（报告标题用）；默认取 柱设计数据.json 的模型名")
    ap.add_argument("--out", default=None,
                    help="输出 xlsx 路径；默认写到当前工作目录")
    ap.add_argument("--system", default=None, help="结构体系（如 框筒 / 框架），可不填")
    ap.add_argument("--seismic", default=None, help="框架抗震等级（如 二级），可不填")
    ap.add_argument("--data", default=None,
                    help="柱设计数据.json 路径；默认取当前工作目录下的同名文件，"
                         "找不到时回退脚本所在目录")
    ap.add_argument("--cost", default=None,
                    help="造价对比.json 路径；默认取当前工作目录下的同名文件，"
                         "找不到时回退脚本所在目录")
    a = ap.parse_args()

    out_path = a.out or os.path.join(os.getcwd(), OUT_NAME)
    DATA = _resolve_input(a.data, "柱设计数据.json")
    COST = _resolve_input(a.cost, "造价对比.json")
    D = json.load(open(COST, encoding="utf-8"))
    SRC = json.load(open(DATA, encoding="utf-8"))
    print("读入：%s\n      %s" % (DATA, COST))
    print("输出：%s" % out_path)
    rows = SRC["rows"]
    meta = SRC["meta"]
    project = a.project or os.path.splitext(meta.get("模型", ""))[0] or "本工程"
    sche = D["方案"]
    det = D["明细"]
    base = sche["S1"]["汇总"]["base"]
    SN = sum(abs(r["Nu"]) for r in rows)          # Σ|Nu| (kN)
    TOTLEN = sum(r["层高_m"] for r in rows)       # 总柱段长 (m)

    # ---------------- 汇总聚合：按 (标准层,组) ----------------
    def agg(key, field):
        d = collections.defaultdict(float)
        for r in det[key]:
            d[(r["标准层"], r["组"])] += r[field]
        return d

    rc_cost = agg("S1", "造价")
    rc_V = agg("S1", "V_m3")
    rc_Wl = agg("S1", "纵筋_t")
    rc_Ws = agg("S1", "箍筋_t")
    rc_A = agg("S1", "模板_m2")
    cf_cost = {k: agg(k, "造价") for k in ("S2", "S3", "S4", "S5", "S6")}
    cf_W = {k: agg(k, "钢管_t") for k in ("S2", "S3", "S4", "S5", "S6")}

    # 逐柱段 CFST 造价 / 截面 索引
    cf_seg = {k: {(r["自然层"], r["柱号"]): r for r in det[k]}
              for k in ("S2", "S4", "S6")}
    sec_of = {k: {(r["标准层"], r["组"]): r for r in sche[k]["截面表"]}
              for k in ("S2", "S3", "S4", "S5", "S6")}

    # 逐柱段聚合：应力比类字段（Uc / ρ纵% / Rsv）与 Mmax 缺就是缺 —— 不留 0.0
    # （0.0 会被渲染成「max Uc = 0.000」这种看起来正常的数），缺项按组计数后写「无数据」。
    src_grp = collections.defaultdict(lambda: dict(n=0, hs=set(), secs=set(), g=set(),
                                                   Nu=None, Uc=None, Rs=None, Rsv=None,
                                                   sh=0, Lc=0.0, pos="", M=None,
                                                   miss=collections.Counter()))
    for r in rows:
        k = (r["标准层"], r["组"])
        grp = src_grp[k]                      # ★ 不可命名为 a：a 是 argparse Namespace
        grp["n"] += 1
        grp["hs"].add(r["层高_m"])
        grp["secs"].add("%d×%d" % (r["b"], r["h"]))
        grp["g"].add(r["混凝土"])
        nu = r.get("Nu")
        if nu is None:
            grp["miss"]["Nu"] += 1
        elif grp["Nu"] is None or abs(nu) > abs(grp["Nu"]):
            grp["Nu"], grp["pos"] = nu, "柱%d 自然层%d" % (r["柱号"], r["自然层"])
        for field, key in (("Uc", "Uc"), ("ρ纵%", "Rs"), ("Rsv", "Rsv"), ("Mmax", "M")):
            v = r.get(field)
            if v is None:
                grp["miss"][field] += 1
            elif grp[key] is None or v > grp[key]:
                grp[key] = v
        grp["sh"] += 1 if r["短柱"] else 0
        grp["Lc"] += r["层高_m"]
    KEYS = sorted(src_grp)

    def _rnum(v, nd=None):
        """逐柱段数值单元格：缺该字段时写「无数据」（不写 0），有值时仍是数字。"""
        if v is None:
            return "无数据"
        return round(v, nd) if nd is not None else v

    def _grp_cell(grp, key, fmt="%.3f", nd=None):
        """按组取聚合值：数据完整时返回数值（单元格仍是数字），有缺项/全缺时返回说明文字。

        全缺 → 「无数据」；部分缺 → 「0.790（1/16 段缺）」—— 都不写 0。
        """
        v = grp[key]
        miss = sum(grp["miss"].values())
        if v is None:
            return "无数据"
        if miss:
            return (fmt % v) + "（%d/%d 段缺）" % (miss, grp["n"])
        return round(v, nd) if nd is not None else v

    # ================================================================== X12 现算块
    # 报告正文里凡能从本次数据算出来的数字，都在这里算，文案只引用这些变量。
    PRM = D.get("参数") or {}
    NSEC = int(meta.get("柱段数", len(rows)))              # 柱段数
    NFLR = int(meta.get("自然层数", 0) or 0)               # 自然层数
    NDP = len(KEYS)                                        # 设计点数 = 标准层 × 柱位组
    GRP_NAME = meta.get("分组") or {}
    CF4 = ("S2", "S3", "S4", "S6")                         # 「4-截面选型」页列出的方案
    CFALL = tuple(k for k in ("S2", "S3", "S4", "S5", "S6") if k in sche)
    # 设计控制参数（来自造价对比.json 的参数 + cfst_design 默认值，非文案写死）
    target = float(PRM.get("target", C.DEFAULT_CFG["target"]))
    theta_min = float(PRM.get("theta_min", C.DEFAULT_CFG["theta_min"]))
    theta_max = float(C.DEFAULT_CFG["theta_max"])
    t_min_cfg = float(C.DEFAULT_CFG["t_min"])
    dt_max_cfg = float(C.DEFAULT_CFG["d_over_t_max"])
    bt_max_cfg = float(C.DEFAULT_CFG["b_over_t_max"])
    uax_max_cfg = float(C.DEFAULT_CFG["u_axial_max_rect"])
    steel = PRM.get("steel", "Q355")
    attach = float(PRM.get("attach", 1.08))
    fab_cost = float(PRM.get("fab_cost", 1300.0))
    tube_loss = float(PRM.get("tube_loss", 0.05))
    fire_code = PRM.get("fire_code")
    fire_name = G.QUOTA[fire_code][0] if fire_code in G.QUOTA else str(fire_code)

    SEC = {k: {g: sec_of[k][g] for g in KEYS if g in sec_of.get(k, {})} for k in CFALL}

    def V(k, f):
        """方案 k 各设计点的某字段值列表。"""
        return [v[f] for v in SEC.get(k, {}).values()]

    # —— 柱位组图例（按柱段数现算，组名取 柱设计数据.json 的 meta.分组）
    grp_seg = collections.Counter(r["组"] for r in rows)
    grp_legend = " / ".join(
        "%s（%d 段）" % (GRP_NAME.get(g, g if g != "?" else "未归组"), grp_seg[g])
        for g in sorted(grp_seg))

    # —— 逐自然层柱数（meta 里的「每层柱数」是各层最大值，不能当"每层"用）
    _flr_n = collections.Counter(r["自然层"] for r in rows)
    NF_MIN = min(_flr_n.values()) if _flr_n else 0
    NF_MAX = max(_flr_n.values()) if _flr_n else 0
    FLR_N = ("每层 %d 根框架柱（共 %d 个柱段）" % (NF_MAX, NSEC) if NF_MIN == NF_MAX
             else "每层 %d~%d 根框架柱（最多 %d 根，各层柱数不等，共 %d 个柱段）"
                  % (NF_MIN, NF_MAX, NF_MAX, NSEC))
    # 柱位分组映射缺失：柱号在模型库里没有对应柱段，被记为 "?"（未归组）
    N_UNGRP = sum(1 for r in rows if r.get("组") == "?")
    UNGRP_NOTE = ("\n★ 未归组：%d 个柱段的柱号在模型库 tblColSeg 里找不到对应柱段（组记为「?」），"
                  "已按独立设计点参与选型与造价 —— 这是柱号口径不一致，须核对。" % N_UNGRP
                  if N_UNGRP else "")

    # —— 造价倍数与差距（全部现算）
    RAT = {k: sche[k]["汇总"]["base"] / base for k in ORDER}
    cf_max_k = max(CFALL, key=lambda k: RAT[k])            # 最贵的钢管混凝土方案
    cf_min_k = min(CFALL, key=lambda k: RAT[k])            # 最经济的钢管混凝土方案
    gap_lo = (min(RAT[k] for k in CFALL) - 1.0) * 100.0    # 钢管混凝土最有利vs S1
    gap_hi = (max(RAT[k] for k in CFALL) - 1.0) * 100.0

    # —— 承载力利用率极值
    # 截面表里没有数据时极值必须是 None（无数据）：兜底成 0.0 会被渲染成
    # "最大 U_ax = 0.000 → 均满足 ≤ 0.9"，那是对空表作出的合规结论。
    def _vals(k, f):
        """方案 k 各设计点该字段的值（跳过缺该字段的项）。"""
        return [v[f] for v in SEC.get(k, {}).values() if v.get(f) is not None]

    def _extreme(f, pick=max, schemes=None):
        xs = [x for k in (schemes or CFALL) for x in _vals(k, f)]
        return pick(xs) if xs else None

    def U_NUM(ax, nm):
        """「最大 U_ax = …、最大 U_NM = …」数值串；无数据时明写无数据。"""
        if ax is None or nm is None:
            return "最大 U_ax / U_NM 无数据（截面表为空或没有 U 值）"
        return "最大 U_ax = %.3f、最大 U_NM = %.3f" % (ax, nm)

    U_ax_max = _extreme("U_ax")
    U_NM_max = _extreme("U_NM")
    U_ax_max4 = _extreme("U_ax", schemes=CF4)
    U_NM_max4 = _extreme("U_NM", schemes=CF4)
    U_DATA = (U_ax_max is not None and U_NM_max is not None)
    U_DATA4 = (U_ax_max4 is not None and U_NM_max4 is not None)
    U_ok = bool(U_DATA and U_ax_max <= target + 1e-9 and U_NM_max <= target + 1e-9)
    U_ok4 = bool(U_DATA4 and U_ax_max4 <= target + 1e-9 and U_NM_max4 <= target + 1e-9)
    # 「均满足」要求数据完整：缺任何一个「方案 × 设计点」的 U 值，结论就只能是"未校验"
    U_MISS = sum(1 for k in CFALL for g in KEYS if g not in SEC.get(k, {}))
    U_MISS4 = sum(1 for k in CF4 for g in KEYS if g not in SEC.get(k, {}))

    def _u_verdict(ok, data, miss, ok_txt):
        if not data:
            return "★ 无数据，该项未校验（不得当满足用）"
        if miss:
            return ("★ 数据不完整（%d 个「方案 × 设计点」缺 U 值），该项未校验，不得当满足用"
                    % miss)
        return ok_txt if ok else "★ 有设计点超限，须重选截面"

    U_NUM_ALL = U_NUM(U_ax_max, U_NM_max)
    U_NUM_4 = U_NUM(U_ax_max4, U_NM_max4)
    U_VERDICT = _u_verdict(U_ok, U_DATA, U_MISS, "均满足 ≤ %.2f" % target)
    U_VERDICT2 = _u_verdict(U_ok, U_DATA, U_MISS, "满足目标 ≤ %.2f" % target)
    U_VERDICT4 = _u_verdict(U_ok4, U_DATA4, U_MISS4, "均满足 ≤ %.2f" % target)

    # —— 套箍系数 / 径厚比 / 壁厚（没有对应截面表数据时一律 None，不兜底 0）
    theta_lo = _extreme("theta", min)
    theta_hi = _extreme("theta", max)
    theta_lo_k = (min((k for k in CFALL if _vals(k, "theta")),
                      key=lambda k: min(_vals(k, "theta")))
                  if theta_lo is not None else None)
    th_s4_lo = _extreme("theta", min, schemes=("S4",))
    th_s4_hi = _extreme("theta", max, schemes=("S4",))
    THETA_NUM_TXT = ("θ %.3f~%.3f" % (theta_lo, theta_hi) if theta_lo is not None
                     else "θ 无数据")
    t_lo, t_lo_k, t_lo_g = None, None, None
    for k in CFALL:
        for g, v in SEC[k].items():
            if v.get("t") is None:
                continue
            if t_lo is None or v["t"] < t_lo:
                t_lo, t_lo_k, t_lo_g = v["t"], k, g
    _dt4 = [v["D_over_t"] for v in SEC.get("S4", {}).values()
            if v.get("D_over_t") is not None]
    dt_lo_dt = max(_dt4) if _dt4 else None
    dt_where = (max(SEC.get("S4", {}).items(), key=lambda kv: kv[1].get("D_over_t") or 0.0,
                    default=(None, None))[0] if _dt4 else None)
    for v in SEC.get("S6", {}).values():                   # b/t = 短边 / t
        if v.get("t"):
            v["_bt"] = _min_side(v["外轮廓"]) / v["t"]
    _bt6 = [v["_bt"] for v in SEC.get("S6", {}).values() if v.get("_bt") is not None]
    bt_lo_bt = max(_bt6) if _bt6 else None
    bt_where = (max(SEC.get("S6", {}).items(), key=lambda kv: kv[1].get("_bt") or 0.0,
                    default=(None, None))[0] if _bt6 else None)

    # —— 实配截面 / 长细比 / 收缩（按规范判据需另加规范值，见文案）
    # 截面表里没有这类截面时留 None（= 无数据），不留 0.0：0 会被渲染成
    # "最大圆管外径 0 mm < 2000mm" 这种对**不存在**的截面作出的合规结论。
    _circ_d = [v["D"] for k in CFALL for v in SEC[k].values() if v.get("D")]
    D_ext_max = max(_circ_d) if _circ_d else None
    rect_side_max = max((_min_side(v["外轮廓"]) for k in CF4 for v in SEC[k].values()
                         if k in ("S2", "S6")), default=0.0)
    _rect_long = []
    for k in ("S2", "S6"):
        for v in SEC.get(k, {}).values():
            m = re.match(r"^(\d+)×(\d+)$", str(v["外轮廓"]))
            if m:
                _rect_long.append(float(max(int(m.group(1)), int(m.group(2)))))
    rect_long_max = max(_rect_long) if _rect_long else None
    lam_lo, lam_where = 0.0, None
    for r in rows:
        g = (r["标准层"], r["组"])
        Dmm = SEC.get("S4", {}).get(g, {}).get("D")
        if not Dmm:
            continue
        lam = r["L0_m"] * 1000.0 / (Dmm / 4.0)             # 圆管 i = D/4
        if lam > lam_lo:
            lam_lo, lam_where = lam, (r["自然层"], r["柱号"], Dmm, r["L0_m"])

    # —— 柱平面占用面积（Σ 各柱段外轮廓面积；等价于「逐层累加」，此处按柱段现算）
    # 只把「截面表非空」的方案纳入：空截面表算出来是 0.0，会渲染成"占用减少 100%"这种假结论。
    PLAN_S1 = sum(r["b"] * r["h"] / 1e6 for r in rows)
    PLAN = {k: sum(_outline_area(v["外轮廓"]) * src_grp[g]["n"]
                   for g, v in SEC[k].items())
            for k in ("S2", "S3", "S4", "S6") if SEC.get(k)}

    def _cut(k):
        """方案 k 相对 S1 的柱平面占用差（%）。算不出来时返回 None（无数据）。"""
        p = PLAN.get(k)
        if not PLAN_S1 or p is None:
            return None
        return (1.0 - p / PLAN_S1) * 100.0

    PLAN_S4 = PLAN.get("S4")
    CUT_S2 = _cut("S2")
    CUT_S3 = _cut("S3")
    CUT_S4 = _cut("S4")
    CUT_S6 = _cut("S6")
    PER_FLR_CUT = ((PLAN_S1 - PLAN_S4) / NFLR
                   if (NFLR and PLAN_S1 and PLAN_S4 is not None) else None)
    PLAN_NODATA = "本次数据无法现算柱平面占用（截面表缺少该方案的外轮廓），该值未计算"

    # 逐柱段应力比类字段的极值：原写法 `r.get("Uc") or 0.0` 会把"缺该字段"渲染成
    # 0.000（看起来满足），这里改为缺就是缺，并给出缺项段数。
    def _row_extreme(field, pick=max):
        vs = [r.get(field) for r in rows]
        vs = [v for v in vs if v is not None]
        return (pick(vs) if vs else None), (len(rows) - len(vs))

    def _row_txt(name, v, miss, fmt="%.2f", unit=""):
        if v is None:
            return "%s 无数据（%d 段缺该字段）" % (name, miss)
        s = "%s = %s%s" % (name, fmt % v, unit)
        return s + ("（另有 %d 段缺该字段，未计入）" % miss if miss else "")

    max_uc, miss_uc = _row_extreme("Uc")
    max_rs, miss_rs = _row_extreme("ρ纵%")
    max_rsv, miss_rsv = _row_extreme("Rsv")
    UC_TXT = _row_txt("max Uc", max_uc, miss_uc, "%.3f")
    RS_TXT = _row_txt("max Rs", max_rs, miss_rs, "%.2f", "%")
    RSV_TXT = _row_txt("max Rsv", max_rsv, miss_rsv, "%.2f", "%")
    grade_set = sorted({r["混凝土"] for r in rows if r.get("混凝土")})
    _secs_of_dp = collections.defaultdict(set)
    for _r in rows:
        _secs_of_dp[(_r["标准层"], _r["组"])].add((_r["b"], _r["h"]))
    mixed_dp = sum(1 for v in _secs_of_dp.values() if len(v) > 1)   # 跨多种原柱截面的设计点
    mixed_example = sorted({"%d×%d" % s for v in _secs_of_dp.values() if len(v) > 1
                            for s in v})

    def DP(g):
        """设计点标签：'标准层 3 / G1 中柱'。"""
        if not g:
            return "（未定位）"
        return "标准层 %s / %s" % (g[0], GRP_NAME.get(g[1], g[1]))

    # —— 钢材综合单价（元/t，现算）
    tube_unit = {k: (sche[k]["汇总"]["tube_mat"] + sche[k]["汇总"]["tube_erect"])
                 / sche[k]["工程量"]["W"]
                 for k in CFALL if sche[k]["工程量"].get("W")}
    rebar_l_unit = sche["S1"]["汇总"]["rebar_l"] / sche["S1"]["工程量"]["Wl"]
    rebar_s_unit = sche["S1"]["汇总"]["rebar_s"] / sche["S1"]["工程量"]["Ws"]
    tube_unit_lo = min(tube_unit.values()) if tube_unit else None
    tube_unit_hi = max(tube_unit.values()) if tube_unit else None
    steel_gap_lo = (tube_unit_lo / max(rebar_l_unit, rebar_s_unit) - 1.0
                    if tube_unit_lo is not None else None)
    steel_gap_hi = (tube_unit_hi / min(rebar_l_unit, rebar_s_unit) - 1.0
                    if tube_unit_hi is not None else None)
    TUBE_UNIT_TXT = ("%.0f~%.0f 元/t" % (tube_unit_lo, tube_unit_hi)
                     if tube_unit_lo is not None else "无数据（各方案都没有钢管工程量）")
    STEEL_GAP_LINE = ("  即单位质量钢材做钢管比做钢筋贵 %.0f%%~%.0f%%，"
                      "且钢管方案用钢量并不比钢筋方案少。\n"
                      % (steel_gap_lo * 100, steel_gap_hi * 100)
                      if steel_gap_lo is not None else
                      "  钢管与钢筋的单位质量综合单价比较：无数据（缺少可比的钢管工程量）。\n")
    tube_share = {k: (sche[k]["汇总"]["tube_mat"] + sche[k]["汇总"]["tube_erect"])
                  / sche[k]["汇总"]["base"] * 100.0
                  for k in CF4 if sche[k]["汇总"]["base"]}
    tube_share_lo = min(tube_share.values()) if tube_share else None
    tube_share_hi = max(tube_share.values()) if tube_share else None
    _ts = (lambda k: ("%.0f%%" % tube_share[k]) if k in tube_share else "无数据")
    TUBE_SHARE_LINE = (
        ("· 钢管混凝土各方案中「钢管材料 + 钢管安装」占该方案造价的 %.0f%%~%.0f%%：\n"
         "  S2 %s、S3 %s、S4 %s、S6 %s\n"
         % (tube_share_lo, tube_share_hi, _ts("S2"), _ts("S3"), _ts("S4"), _ts("S6")))
        if tube_share else
        "· 钢管混凝土各方案中「钢管材料 + 钢管安装」占该方案造价：无数据（无可比的分项造价）\n")
    # 方案行文字（含「最贵 / 最经济」标记，均为现算）
    CF_LINE_NAME = {"S2": "S2 矩形钢管混凝土（等外轮廓）",
                    "S3": "S3 圆形钢管混凝土（等外轮廓）",
                    "S4": "S4 圆形钢管混凝土（造价最优）",
                    "S5": "S5 圆形钢管混凝土（不限 θ 下限）",
                    "S6": "S6 矩形钢管混凝土（造价最优）"}
    cf_lines = []
    for _k in CFALL:
        _tag = ""
        if _k == cf_max_k:
            _tag = "  ← 最贵"
        if _k == cf_min_k:
            _tag = "  ← 钢管混凝土中最经济"
        cf_lines.append("  %-32s %8.1f 万元 = %5.0f%%%s"
                        % (CF_LINE_NAME.get(_k, _k), sche[_k]["汇总"]["base"] / 1e4,
                           RAT[_k] * 100.0, _tag))
    cf_lines = "\n".join(cf_lines)

    # —— 防火涂料：单价 元/m²（= 该方案 fire 造价 / 展开面积）、占 CFST 造价比例
    fire_share = [(sche[k]["汇总"]["fire"] / sche[k]["汇总"]["base"] * 100.0)
                  for k in CF4 if sche[k]["汇总"]["base"]]
    fire_share_lo = min(fire_share) if fire_share else None
    fire_share_hi = max(fire_share) if fire_share else None
    _fa = sche["S4"]["工程量"]["A"] if "S4" in sche else None
    fire_unit = (sche["S4"]["汇总"]["fire"] / _fa) if _fa else None
    _fu = ("%.0f 元/m²" % fire_unit) if fire_unit is not None else "单价 无数据"
    FIRE_LINE = (("· 防火涂料占钢管混凝土造价 %.0f%%~%.0f%%（%s，约 %s）。\n"
                  % (fire_share_lo, fire_share_hi, fire_name, _fu))
                 if fire_share else
                 "· 防火涂料占钢管混凝土造价：无数据（缺少可比的防火涂料造价或展开面积）。\n")

    # —— 敏感性分析统计
    # 没有敏感性数据时必须显示为「无数据」：兜底成 0 会写出
    # "最低仍贵 0%（出现在「（无）」时）"，并把结论翻成相反的话。
    sens = D.get("敏感性") or []
    NSENS = len(sens)

    def _gap(s):
        cf = [s.get("S2_万元"), s.get("S4_万元"), s.get("S6_万元")]
        cf = [x for x in cf if x is not None]
        return (min(cf) / s["S1_万元"] - 1.0) if (cf and s.get("S1_万元")) else None

    _sg = [(_gap(s), s) for s in sens]
    _sg = [(g, s) for g, s in _sg if g is not None]
    SENS_OK = bool(_sg)                    # 有可用的敏感性对比数据
    SENS_LACK = "造价对比.json 的「敏感性」为空，或缺少可比的 S1/S2/S4/S6 数值"
    if SENS_OK:
        sens_lo, sens_lo_s = min(_sg, key=lambda x: x[0])
        sens_hi, sens_hi_s = max(_sg, key=lambda x: x[0])
        sens_all_pricier = all(g > 0 for g, _ in _sg)
    else:
        sens_lo = sens_hi = None
        sens_lo_s = sens_hi_s = {}
        sens_all_pricier = False
    _pg = [(g, s) for g, s in _sg if s.get("类别") == "价格与构造"]
    PLATE_OK = bool(_pg)
    plate_lo, plate_lo_s = min(_pg, key=lambda x: x[0]) if PLATE_OK else (None, {})

    # 敏感性相关的现算文案：有数据才算结论，无数据一律明写「无数据」
    if SENS_OK:
        _verdict = ("该结论始终成立" if sens_all_pricier else "★ 存在该结论不成立的情形")
        SENS_STMT = ("敏感性分析覆盖了 %d 种假设组合，%s（最低仍贵 %.0f%%，出现在「%s」时）。"
                     % (NSENS, _verdict, sens_lo * 100, sens_lo_s.get("情形", "（无）")))
        SENS_BEST = ("敏感性中最有利情形的差距仍为 %.0f%%（见「6-敏感性分析」）"
                     % (sens_lo * 100))
        SENS_RANGE_TXT = ("敏感性 %d 种情形，差距 %.0f%%~%.0f%%"
                          % (NSENS, sens_lo * 100, sens_hi * 100))
        SENS_FOOT = ("★ %d 种情形下%s。钢管混凝土相对 S1 的差距（各情形取最便宜的钢管混凝土"
                     "方案，现算）：最低 %.0f%%（「%s」情形），最高 %.0f%%（「%s」情形）。结论%s。"
                     % (NSENS,
                        "钢管混凝土方案均贵于钢筋混凝土柱" if sens_all_pricier
                        else "存在钢管混凝土方案不贵于钢筋混凝土柱的情形",
                        sens_lo * 100, sens_lo_s.get("情形", "（无）"),
                        sens_hi * 100, sens_hi_s.get("情形", "（无）"),
                        "稳健" if sens_all_pricier else "★ 不成立"))
    else:
        SENS_STMT = ("★ 敏感性分析未做：%s。缺失不按 0%% 计，上述「仍贵」只代表本页基准情形。"
                     % SENS_LACK)
        SENS_BEST = "本次无敏感性数据，最有利情形未做评价（见「6-敏感性分析」）"
        SENS_RANGE_TXT = "敏感性 无数据（未做该项评价）"
        SENS_FOOT = ("★ 本次输入无敏感性数据（%s）：缺失不按 0%% 计，本页不做任何敏感性结论，"
                     "请补齐数据后重跑。" % SENS_LACK)
    PLATE_TXT = (("（敏感性「价格与构造」类最有利情形「%s」下，S4 仍贵 %.0f%%）"
                  % (plate_lo_s.get("情形", "（无）"), plate_lo * 100)) if PLATE_OK
                 else "（敏感性「价格与构造」类无数据，该项未做评价）")
    # 正文里凡引用「敏感性」的地方，都必须按是否真有数据分别措辞（不得宣称做过没有的对比）
    SENS_REF_LABOR = ("做了敏感性对比（见「6-敏感性分析」）" if SENS_OK
                      else "本次无敏感性数据，该项未做对比")
    SENS_REF_THETA = ("（敏感性已给出 θ≥0.70 的结果）" if SENS_OK
                      else "（本次无敏感性数据，未做 θ≥0.70 的对比）")
    SENS_REF_FIRE = ("（见「6-敏感性分析」的最省情形）" if SENS_OK
                     else "（本次无敏感性数据，该情形未做对比）")

    # —— 其余「现算」文案里的无数据分支（一律明写无数据/未校验，不兜底成数字）
    U_NUM_SRC = ("最大 U_ax %.3f、最大 U_NM %.3f" % (U_ax_max, U_NM_max) if U_DATA
                 else "最大 U_ax / 最大 U_NM 无数据")
    T_TXT = ("%gmm" % t_lo) if t_lo is not None else "无数据"
    DT_TXT = ("%.1f" % dt_lo_dt) if dt_lo_dt is not None else "无数据"
    BT_TXT = ("%.1f" % bt_lo_bt) if bt_lo_bt is not None else "无数据"
    PLAN_SRC = ("%.1f→%.1f m²" % (PLAN_S1, PLAN_S4) if PLAN_S4 is not None
                else "无数据（截面表缺少方案外轮廓）")
    CUT4_TXT = (("（实测 S4 可减少 %.0f%% 柱平面占用）" % CUT_S4) if CUT_S4 is not None
                else "（S4 柱平面占用：%s）" % PLAN_NODATA)
    if PLAN_S4 is not None and CUT_S4 is not None and PER_FLR_CUT is not None:
        _s6t = ("；S6 亦可减少 %.1f%%" % CUT_S6) if CUT_S6 is not None else "；S6 无数据"
        PLAN_ROW = ("实测（现算，Σ 各柱段外轮廓面积，共 %d 段 / %d 自然层）：S4 = %.1f m² vs 现状 "
                    "S1 = %.1f m²，累计少占 %.1f m²、平均每层少占 %.2f m²%s。"
                    "（S4/S6 按「设计点截面 × 柱段数」累计；%d 个设计点跨两种原柱截面，按首段截面计）"
                    "若折算为可售/可使用面积价值，可能扭转经济性对比 —— 建议按项目实际单价单独评价。"
                    % (NSEC, NFLR, PLAN_S4, PLAN_S1, PLAN_S1 - PLAN_S4, PER_FLR_CUT, _s6t,
                       mixed_dp))
        PLAN2_LINE = ("2) 圆形钢管混凝土（S4）可把柱平面占用面积（Σ 各柱段外轮廓面积，共 %d 段 / "
                      "%d 自然层）\n   从现状 %.1f m² 降到 %.1f m²，平均每层少占 %.2f m²，折合约 "
                      "%.1f%% 的柱截面缩减，\n   可转化为使用面积或减小结构自重。此收益本报告未折算"
                      "金额（只比工程量属用户要求 %s），\n   需在方案决策时单独评价。\n"
                      % (NSEC, NFLR, PLAN_S1, PLAN_S4, PER_FLR_CUT, CUT_S4, MANUAL))
    else:
        PLAN_ROW = ("实测（现算）：%s。若折算为可售/可使用面积价值，可能扭转经济性对比 —— "
                    "建议按项目实际单价单独评价。" % PLAN_NODATA)
        PLAN2_LINE = ("2) 柱平面占用：%s。该收益未评价（只比工程量属用户要求 %s）。\n"
                      % (PLAN_NODATA, MANUAL))
    # 套箍系数 / 径厚比：无数据时写「无数据，该项未校验」
    if theta_lo is None:
        THETA_ROW = ("实测（现算）：本次截面表为空（或没有 θ 数据），套箍系数 无数据，该项未校验；"
                     "θ 下限 %.2f 为参数值 %s。" % (theta_min, MANUAL))
    else:
        _s4t = ("；其中 S4 的 θ ∈ [%.3f, %.3f]" % (th_s4_lo, th_s4_hi)
                if th_s4_lo is not None else "；其中 S4 本次无截面数据")
        THETA_ROW = ("实测（现算）：全部方案 θ ∈ [%.3f, %.3f]%s（下限 %.2f 为参数值 %s）。"
                     "θ 偏小会降低钢管对混凝土的套箍约束作用与延性，若结构对延性要求高，"
                     "应提高 θ 下限%s。"
                     % (theta_lo, theta_hi, _s4t, theta_min, MANUAL, SENS_REF_THETA))
    if dt_lo_dt is None and bt_lo_bt is None:
        RATIO_ROW = ("实测（现算）：本次截面表为空（或没有 D/t、b/t 数据），径厚比 无数据，"
                     "该项未校验。")
    else:
        _dt_t = (("S4 最大 D/t = %.1f（%s）" % (dt_lo_dt, DP(dt_where))) if dt_lo_dt is not None
                 else "S4 最大 D/t 无数据（该方案无截面数据）")
        _bt_t = (("S6 最大 b/t = %.1f（%s）" % (bt_lo_bt, DP(bt_where))) if bt_lo_bt is not None
                 else "S6 最大 b/t 无数据（该方案无截面数据）")
        _mg = (("距限值余量 %.1f%% 与 %.1f%%"
                % ((1 - dt_lo_dt / dt_max_cfg) * 100, (1 - bt_lo_bt / bt_max_cfg) * 100))
               if (dt_lo_dt is not None and bt_lo_bt is not None)
               else "距限值余量 无数据（缺上述截面）")
        RATIO_ROW = ("实测（现算）：%s、%s；%s，须在加工图阶段核对局部稳定与焊接变形控制。"
                     % (_dt_t, _bt_t, _mg))

    # —— 定额/费率（从 gz_quota 现算，不写死）
    def _mgr_rate(code):
        q = G.QUOTA[code]
        base_lm = q[3] + q[5]
        return q[6] / base_lm * 100.0 if base_lm else 0.0

    mgr_conc = _mgr_rate("A1-5-5")          # 混凝土及钢筋混凝土
    mgr_form = _mgr_rate("A1-20-14")        # 模板工程
    mgr_steel = _mgr_rate("A1-7-30")        # 金属结构工程
    mgr_paint = _mgr_rate("A1-15-126")      # 油漆涂料

    wb = Workbook()

    # ================================================================== 1-说明
    ws = wb.active
    ws.title = "1-说明"
    ws.column_dimensions["A"].width = 20
    ws.column_dimensions["B"].width = 118
    ws.cell(row=1, column=1,
            value="%s · 框架柱截面形式经济比选报告" % project).font = TITLE
    ws.cell(row=2, column=1,
            value="钢筋混凝土柱 vs 矩形/圆形钢管混凝土柱 ｜ 按广州地区现行定额与信息价 ｜ "
                  "钢管混凝土承载力利用率 ≤ %.2f" % target
            ).font = Font(italic=True, size=10, color="555555")
    # 跃层柱统计（用于说明文案，从数据现算，不写死工程口径）
    nover = sum(1 for r in rows if r["跃层"])
    over_floors = sorted({r["自然层"] for r in rows if r["跃层"]})
    max_l0_over = max((r["L0_m"] for r in rows if r["跃层"]), default=0.0)

    r = 4
    items = [
        ("工程概况",
         "结构体系 %s ｜ %d 自然层 / %d 结构标准层 ｜ %s\n"
         "总高 %.1f m（取自模型 tblFloor.Height 的逐层实际层高之和；"
         "「已与 wmass.out 逐层核对」为外部核对项，本报告未做 %s）%s\n"
         "来源模型：%s"
         % (a.system or "（未注明）", meta["自然层数"], meta["标准层数"], FLR_N,
            meta["总高_m"], MANUAL,
            ("｜ 框架抗震等级 %s" % a.seismic) if a.seismic else "",
            meta.get("模型", "（未记录）"))),
        ("比选范围",
         "只比选「柱」这一竖向构件的截面形式。梁、板、墙、基础、荷载一律不变，\n"
         "各方案采用完全相同的内力输入（同一模型、同一组合的轴力 Nu 与柱端弯矩包络 M）与\n"
         "相同的工程量口径（%d 个柱段、按自然层实际层高累计，总柱段长 %.1f m）。\n"
         "因此差异全部来自「截面形式」本身，属于可比的同口径对比。" % (meta["柱段数"], TOTLEN)),
        ("内力输入（关键口径）",
         "· 轴力 N：取自 wpj*.out 中该柱「最大轴力控制组合」的 Nu（实算值，非估算）\n"
         "· 弯矩 M：取自 wpj*.out 中该柱全部设计组合四边配筋行的柱端弯矩包络，\n"
         "  按合弯矩 M = √(Mx²+My²) 取包络（同组合柱两端弯矩不同，须逐条取包络）\n"
         "· 计算长度：L0x = Cx × Lcx、L0y = Cy × Lcy（Cx/Cy 为计算长度系数，Lcx/Lcy 为本方向柱段长）\n"
         "  跃层柱按实际跨越层数取长度（本工程共 %d 个跃层柱段，出现在自然层 %s，最大 L0 = %.1f m）\n"
         "· 逐组设计取值：ΣN、max M、max L0 —— 对同组多个柱段取包络，偏安全"
         % (nover, "、".join(str(x) for x in over_floors) or "无", max_l0_over)),
        ("钢筋混凝土柱（S1）",
         "即现状模型的实配方案，作为比选基准。\n"
         "工程量全部取自实算结果：混凝土按 b×h×层高；纵筋按 wpj 实配 As；\n"
         "箍筋按 wpj 的体积配箍率 Rsv × 核心区体积；模板按柱周长选子目并叠加支模超高子目。\n"
         "★ 「S1 = 上一轮柱截面优化的结果」这一来源说明%s（本次数据只能给出实配结果本身）。"
         % MANUAL),
        ("钢管混凝土柱",
         "按 GB 50936-2014《钢管混凝土结构技术规范》第 5 章设计。钢材 %s，管内混凝土强度\n"
         "等级沿用原柱（不降级）。%d 种子方案：\n"
         "  S2 矩形，外轮廓 = 原柱 b×h（不动建筑柱位，柱宽不变）\n"
         "  S3 圆形，外径 D = √(4bh/π)（与原柱等外轮廓面积，占用面积不变）\n"
         "  S4 圆形，外径在 %s 内扫描取「单位长度造价」最低者（允许缩小柱截面）\n"
         "  S5 同 S4 但取消套箍系数 θ≥%.2f 的推荐要求（理论下限，仅供参考）\n"
         "  S6 矩形，保持原柱长宽比、短边在 %s 内扫描取造价最低者"
         % (steel, len(CFALL), MANUAL + " 400~2400mm@25mm，见 cost_model.size_group",
            theta_min, MANUAL + " 400~1800mm@50mm，见 cost_model.size_group")),
        ("承载力控制（目标值）",
         "① 轴力利用率 U_ax = N / Nu ≤ %.2f（Nu 为轴压稳定承载力设计值，式 5.1.10）\n"
         "② 压弯综合利用率 式(5.3.1-4)/(5.3.1-5) ≤ %.2f（从严，把「承载力利用率≤%.2f」同时施加于压弯）\n"
         "③ 套箍系数 θ = αsc·fy/fc ∈ [%.2f, %.2f]（GB 50936 第 4.3.2 条「宜为 0.5~2.0」）\n"
         "④ 壁厚 ≥ %gmm；圆管 D/t ≤ %g、方管 b/t ≤ %g；矩形柱轴压比 ≤ %.2f\n"
         "★ 说明：GB 50936 第 4.2.3-2 条对地震组合允许 Sd ≤ Rd/γRE，γRE = 0.80（稳定验算，%s），\n"
         "  即规范本身允许 U ≤ 1.25。取 %.2f 已明显偏安全，属用户指定的更严控制（%s）。\n"
         "★ 实测结果（按本次数据现算）：全部 %d 个设计点 × %d 种方案，%s → %s。"
         % (target, target, target, theta_min, theta_max, t_min_cfg, dt_max_cfg, bt_max_cfg,
            uax_max_cfg, MANUAL, target, MANUAL, NDP, len(CFALL), U_NUM_ALL, U_VERDICT)),
        ("计价依据",
         "① 定额：《广东省房屋建筑与装饰工程综合定额（2018）》—— 见「7-定额与价格依据」页\n"
         "② 信息价：《2026 年 6 月广州地区建设工程常用材料税前综合价格》（穗建造价〔2026〕62 号）\n"
         "③ 人工费、机具费按定额基价原值计取；另按穗建造价〔2026〕62 号人工费价格指数 %.2f%%\n"
         "   %s\n"
         "④ 管理费 =（定额人工费 + 定额施工机具费）× 分摊费率。按 gz_quota.py 定额子目现算：\n"
         "   混凝土及钢筋混凝土 %.2f%% / 模板工程 %.2f%% / 金属结构工程 %.2f%% / 油漆涂料 %.2f%%\n"
         "   （已含于定额基价）\n"
         "⑤ 利润 =（定额人工费 + 定额施工机具费）× %.2f%%\n"
         "⑥ 增值税 = 综合单价 × %.0f%%（定额基价与信息价均为不含税口径）；混凝土损耗率 %.1f%%\n"
         "★ 定额名称、文号、信息价口径属外部计价依据，无法由本次输入数据推出：%s。"
         % (G.LABOR_INDEX * 100, SENS_REF_LABOR, mgr_conc, mgr_form, mgr_steel, mgr_paint,
            G.PROFIT * 100, G.VAT * 100, (G.CONC_LOSS - 1.0) * 100, MANUAL)),
        ("口径提醒：除税/含税",
         "全文「除税」= 不含增值税可抵扣进项税额的综合单价；「含税」= 除税 × 1.09。\n"
         "广州市信息价为税前综合价格，故除税口径与信息价口径一致，可直接相加。"),
        ("主要结论",
         "在同等内力、同等工程量口径下，以现状钢筋混凝土柱（%.1f 万元除税）为 100%%：\n"
         "%s\n"
         "即：本工程在现行广州价格下，钢管混凝土柱方案比钢筋混凝土柱贵 %.0f%%~%.0f%%，\n"
         "最经济的钢管混凝土方案（%s）仍贵 %.0f%%。%s"
         % (base / 1e4, cf_lines, gap_lo, gap_hi, cf_min_k, (RAT[cf_min_k] - 1) * 100,
            SENS_STMT)),
        ("造价构成要点（敏感性之外的解释）",
         "· 钢筋混凝土柱（S1）造价构成：混凝土 %.1f%% / 纵筋 %.1f%% / 箍筋 %.1f%% / 模板 %.1f%%\n"
         "%s"
         "  实测钢管综合单价（钢板信息价×(1+%.0f%%损耗) + 制作加工费 %.0f 元/t + 安装）\n"
         "  %s，而钢筋综合单价 %.0f 元/t（纵筋）、%.0f 元/t（箍筋）；\n"
         "%s"
         "%s"
         "· 结论（人工判断 %s）：在现行广州价格体系下，「钢材单价高 + 用钢量不减 + 防火涂料」\n"
         "  三项叠加，决定了钢管混凝土柱在本工程不具造价优势。%s。"
         % (sche["S1"]["汇总"]["conc"] / base * 100, sche["S1"]["汇总"]["rebar_l"] / base * 100,
            sche["S1"]["汇总"]["rebar_s"] / base * 100, sche["S1"]["汇总"]["form"] / base * 100,
            TUBE_SHARE_LINE,
            tube_loss * 100, fab_cost, TUBE_UNIT_TXT,
            rebar_l_unit, rebar_s_unit, STEEL_GAP_LINE, FIRE_LINE, MANUAL, SENS_BEST)),
        ("钢管混凝土的有利之处（须一并权衡）",
         "1) 本项目钢筋混凝土柱箍筋用量 %.1f t（本次数据混凝土等级 %s；实测 %s）。\n"
         "   %s：GB 50011-2010 表 6.3.9 的体积配箍率要求（1.2%%~1.3%%）与「1350×1000 柱约\n"
         "   128 kg/m」均为外部规范/经验值，本次数据推不出来。\n"
         "   钢管混凝土无箍筋，这部分材料与人工全部省去 —— 已计入本报告对比。\n"
         "%s"
         "3) 柱自重大幅下降（管内混凝土 %.1f m³ vs 混凝土柱 %.1f m³），对基础与桩有利。"
         % (sche["S1"]["工程量"]["Ws"], "/".join(grade_set), RSV_TXT, MANUAL, PLAN2_LINE,
            sche["S4"]["工程量"]["V"], sche["S1"]["工程量"]["V"])),
        ("★ 限制与风险",
         "1) 本报告为「形式比选」的方案阶段分析，未对钢管混凝土方案做整体结构实算。\n"
         "   柱截面形式改变会影响柱抗弯刚度（进而内力重分布）、层间位移角、层刚度比与自振周期，\n"
         "   必须重算验证后方可定论。\n"
         "2) 各方案均采用「原钢筋混凝土模型的柱内力」作为输入。钢管混凝土柱刚度与混凝土柱不同，\n"
         "   实际内力会有差异；由于同组取包络（ΣN、max M、max L0）设计，偏于安全。\n"
         "3) 造价中的以下项目为市场估值、非定额项（%s），已在「7-定额与价格依据」注明并在敏感性中覆盖：\n"
         "   钢材制作加工费（%.0f 元/t）、钢板下料损耗（%.0f%%）、节点附件系数（%.2f，含加强环/内衬管/\n"
         "   牛腿/节点板，按 GB 50936 工程量规则并入钢管柱质量）。\n"
         "4) 未计入的费用：钢管柱除锈油漆（贯穿式油漆另计）、焊缝探伤、大型吊装机械进出场、\n"
         "   管端封堵与临时支撑、梁柱节点处梁纵筋与钢管的连接构造（穿心板/焊接连接件）、\n"
         "   管内混凝土浇筑的泵送与振捣特殊措施、钢管混凝土收缩徐变控制措施。\n"
         "   这些多为「钢管混凝土方更贵」方向，即本报告对钢管混凝土偏有利。\n"
         "5) 防火涂料按子目 %s「%s」计取，占钢管混凝土造价 %.0f%%~%.0f%%（「一级耐火等级柱\n"
         "   3.0h」为外部假定 %s）。若建筑专业同意以包覆或其他措施满足耐火要求，此项可大幅下降。\n"
         "6) 未含基础/桩基造价变化。钢管混凝土柱自重更轻，可能减少桩基用量，属未计入的有利因素。\n"
         "7) 未含工期与施工难度差异（钢管柱需工厂加工、现场吊装焊接，对超高层工期通常有利）。"
         % (MANUAL, fab_cost, tube_loss * 100, attach, fire_code, fire_name,
            fire_share_lo, fire_share_hi, MANUAL)),
        ("结论建议",
         "以下为人工判断（%s），不属于本报告算出来的数：\n"
         "在本次广州地区定额与 2026 年 6 月信息价口径下，钢管混凝土柱方案不具造价优势。\n"
         "若仅以工程量/造价为决策依据，建议维持钢筋混凝土柱方案（现状实配方案）。\n"
         "若因以下原因需改用钢管混凝土，推荐圆形截面（S4 型）而非矩形：\n"
         "  · 建筑/使用要求缩小柱截面%s\n"
         "  · 施工工期紧、要求工厂化预制与快速吊装\n"
         "  · 钢材价格下行%s\n"
         "  · 业主明确要求大跨/超高层采用钢管混凝土\n"
         "决策时建议按「柱平面占用面积每减少 1 m² 的价值」做等价换算（本报告未做该折算）。"
         % (MANUAL, CUT4_TXT, PLATE_TXT)),
        ("★ 数据来源与人工填写项清单",
         "【现算，来自 %s / %s】柱段数 %d ｜ 设计点数 %d ｜ 自然层 %d ｜ 总柱段长 %.1f m ｜ "
         "各方案造价与倍数 ｜\n"
         "  %s ｜ %s ｜ 最小壁厚 %s ｜ 最大 D/t %s ｜ "
         "最大 b/t %s ｜\n"
         "  柱平面占用 %s ｜ %s ｜ 钢管与钢筋综合单价。\n"
         "  平面占用口径：按各方案「设计点截面 × 该组柱段数」累计；其中 %d 个设计点跨两种原柱截面"
         "（%s），截面表按首段截面取，会低估这些设计点的占用面积。\n"
         "  柱位分组：%s。\n"
         "【人工填写/待确认（推不出来或人工判断，不得当结论用）】\n"
         "  · 目标利用率 %.2f、套箍系数下限 %.2f、扫描区间（圆形 D 400~2400mm@25mm、矩形短边 400~1800mm@50mm）\n"
         "  · 市场估值参数：制作加工费 %.0f 元/t、下料损耗 %.0f%%、节点附件系数 %.2f\n"
         "  · 规范/定额外部值：γRE=0.80、[λ]≤80、外径/边长≥168mm、壁厚≥3mm、直径>2m、边长>1.5m、\n"
         "    体积配箍率 1.2%%~1.3%%、耐火极限 3.0h、定额名称与文号\n"
         "  · 人工判断：结论建议、S1 方案来源说明、节点构造与管内浇筑的定性评价"
         % (os.path.basename(DATA), os.path.basename(COST), NSEC, NDP, NFLR, TOTLEN,
            U_NUM_SRC, THETA_NUM_TXT, T_TXT, DT_TXT, BT_TXT,
            PLAN_SRC, SENS_RANGE_TXT,
            mixed_dp, "/".join(mixed_example) or "（无）",
            "未归组 %d 段（柱号在模型库中无对应柱段，按独立设计点处理）" % N_UNGRP
            if N_UNGRP else "全部柱段均按平面坐标归组",
            target, theta_min, fab_cost, tube_loss * 100, attach)),
    ]
    for k, v in items:
        c1 = ws.cell(row=r, column=1, value=k)
        c1.font, c1.fill = Font(bold=True, size=10), SUB_FILL
        c1.alignment, c1.border = Alignment(vertical="top", wrap_text=True), BORDER
        c2 = ws.cell(row=r, column=2, value=v)
        c2.alignment, c2.border = Alignment(vertical="top", wrap_text=True), BORDER
        ws.row_dimensions[r].height = max(18, 14.5 * (v.count("\n") + 1))
        r += 1
    ws.freeze_panes = "A4"

    # ================================================================== 2-造价汇总对比
    ws2 = wb.create_sheet("2-造价汇总对比")
    ws2.cell(row=1, column=1,
             value="柱截面形式造价汇总对比（广东省2018综合定额 + 广州市2026年6月信息价）"
             ).font = TITLE
    ws2.cell(row=2, column=1,
             value="单位：万元 ｜「除税」为不含增值税可抵扣进项税额的综合单价 ｜「含税」= 除税 × 1.09"
             ).font = Font(italic=True, size=9, color="555555")
    cols = [("混凝土", "conc"), ("钢管材料", "tube_mat"), ("钢管安装", "tube_erect"),
            ("纵筋", "rebar_l"), ("箍筋", "rebar_s"), ("防火涂料", "fire"), ("模板", "form")]
    head(ws2, 4, ["方案"] + [c[0] for c in cols] + ["除税合计", "含税合计", "相对S1", "元/kN", "元/延米柱"] + ["组合说明"],
         [34] + [11] * 7 + [12, 12, 10, 9, 11, 46])
    r = 5
    # 组合说明：全部由数据现算（含 S4/S6 实测缩减幅度、S5 实测 θ 下限）
    s5_th = _extreme("theta", min, schemes=("S5",))
    notes = {
        "S1": "现状模型实配，比选基准",
        "S2": "柱宽/柱位不变（外轮廓 = 原柱 b×h）；平面占用 Σ 现算比 S1 少 %.1f%%"
              "（%d 个设计点跨两种原柱截面、截面表按首段取），可与 S1 直接比"
              % (CUT_S2, mixed_dp) if CUT_S2 is not None else
              "柱宽/柱位不变（外轮廓 = 原柱 b×h）；平面占用为 无数据（未做该项比较）",
        "S3": ("柱平面占用现算比 S1 %s %.2f%%（等外轮廓面积圆按设计点首段截面取、外径取整，"
               "故不严格相等），可与 S1 直接比"
               % ("多" if CUT_S3 < 0 else "少", abs(CUT_S3))) if CUT_S3 is not None
              else "柱平面占用为 无数据（未做该项比较）",
        "S4": ("柱平面占用实测减少 %.1f%%，含「省面积」以外的全部造价" % CUT_S4)
              if CUT_S4 is not None else "柱平面占用为 无数据（未做该项比较）",
        "S5": ("仅供参考：实测 θ 最低 %.3f（推荐下限 %.2f %s）" % (s5_th, theta_min, MANUAL))
              if s5_th is not None else
              "仅供参考：本次截面表没有 S5 的 θ 数据（该项未校验）",
        "S6": ("柱平面占用实测减少 %.1f%%" % CUT_S6) if CUT_S6 is not None
              else "柱平面占用为 无数据（未做该项比较）",
    }
    for k in ORDER:
        t = sche[k]["汇总"]
        vals = [SHORT[k]] + [round(t.get(c[1], 0.0) / 1e4, 1) for c in cols]
        vals += [round(t["base"] / 1e4, 1), round(t["vat"] / 1e4, 1),
                 t["base"] / base, round(t["base"] / SN, 3), round(t["base"] / TOTLEN, 1)]
        vals.append(notes[k])
        fill = OK if k == "S1" else None
        r = put(ws2, r, vals,
                fmts=[None] + [N2] * 7 + [N2, N2, PCT, N3, N2, None], fill=fill)
    r = put(ws2, r, ["合计校验"] + [round(sum(sche[k]["汇总"].get(c[1], 0.0) for k in ORDER) / 1e4, 1)
                                  for c in cols] + [None] * 5 + [""],
            fmts=[None] + [N2] * 7 + [None] * 5 + [None])
    for cc in range(1, 15):
        ws2.cell(row=r - 1, column=cc).font = Font(bold=True, size=10)
        ws2.cell(row=r - 1, column=cc).fill = SUB_FILL
    ws2.freeze_panes = "B5"

    ch = BarChart()
    ch.type, ch.style = "col", 10
    ch.title = "各柱截面形式造价对比（除税，万元）"
    ch.y_axis.title = "万元"
    data = Reference(ws2, min_col=9, max_col=9, min_row=4, max_row=4 + len(ORDER))
    cats = Reference(ws2, min_col=1, min_row=5, max_row=4 + len(ORDER))
    ch.add_data(data, titles_from_data=True)
    ch.set_categories(cats)
    ch.height, ch.width = 9, 22
    ws2.add_chart(ch, "A%d" % (r + 2))

    # ================================================================== 3-工程量对比
    ws3 = wb.create_sheet("3-工程量对比")
    ws3.cell(row=1, column=1,
             value="工程量对比（%d 个柱段，按自然层实际层高累计）" % NSEC).font = TITLE
    head(ws3, 3, ["方案", "主要工程量", "单位", "数量",
                  "分项造价(万元)", "占该方案造价", "单位造价(元/单位)"],
         [34, 30, 8, 14, 14, 12, 15])
    r = 4
    q1 = sche["S1"]["工程量"]
    qrows = [("S1", "混凝土（现浇柱）", "m³", q1["V"], "conc"),
             ("S1", "纵筋（HRB400E）", "t", q1["Wl"], "rebar_l"),
             ("S1", "箍筋（HPB300/HRB400）", "t", q1["Ws"], "rebar_s"),
             ("S1", "柱模板（含支模超高）", "m²", q1["A"], "form")]
    for k in ("S2", "S3", "S4", "S5", "S6"):
        q = sche[k]["工程量"]
        qrows += [(k, "钢管（含节点附件 %.2f）" % attach, "t", q["W"], "tube"),
                  (k, "管内混凝土", "m³", q["V"], "conc"),
                  (k, "钢管外表面（防火涂料面积）", "m²", q["A"], "fire")]
    for k, nm, u, v, tag in qrows:
        t = sche[k]["汇总"]
        c = (t.get("tube_mat", 0.0) + t.get("tube_erect", 0.0)) if tag == "tube" \
            else t.get(tag, 0.0)
        r = put(ws3, r, [SHORT[k], nm, u, round(v, 1), round(c / 1e4, 1),
                         (c / t["base"]), (c / v if v else None)],
                fmts=[None, None, None, N2, N2, PCT, N2])
    # 追加：按分项造价补充
    ws3.cell(row=r, column=1,
             value="注：混凝土柱无钢管与防火涂料；钢管混凝土柱无纵筋、箍筋与模板。"
             ).font = Font(italic=True, size=9, color="555555")
    ws3.freeze_panes = "A4"

    # ---- 3b 分项造价构成（放在右侧 J 列起，避免列宽冲突）----
    C0 = 10

    def head_at(row, col0, titles, widths):
        for i, t in enumerate(titles):
            cell = ws3.cell(row=row, column=col0 + i, value=t)
            cell.font, cell.fill = HEAD, HEAD_FILL
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            cell.border = BORDER
            ws3.column_dimensions[get_column_letter(col0 + i)].width = widths[i]
        ws3.row_dimensions[row].height = 32

    def put_at(row, col0, values, fmts=None):
        for i, v in enumerate(values):
            cell = ws3.cell(row=row, column=col0 + i, value=v)
            cell.border = BORDER
            cell.font = Font(size=10)
            if fmts and i < len(fmts) and fmts[i]:
                cell.number_format = fmts[i]
        return row + 1

    hr = r + 2
    head_at(hr, C0, ["方案（分项造价构成）"] + [c[0] for c in cols] + ["除税合计"],
            [30] + [11] * 7 + [12])
    rr = hr + 1
    for k in ORDER:
        t = sche[k]["汇总"]
        rr = put_at(rr, C0, [SHORT[k]] + [round(t.get(c[1], 0.0) / 1e4, 1) for c in cols]
                    + [round(t["base"] / 1e4, 1)],
                    fmts=[None] + [N2] * 7 + [N2])
    GRAND = sum(sche[k]["汇总"]["base"] for k in ORDER)
    rr = put_at(rr, C0, ["各方案合计占比（按造价）"]
                + [sum(sche[k]["汇总"].get(c[1], 0.0) for k in ORDER) / GRAND
                   for c in cols] + [1.0],
                fmts=[None] + [PCT] * 8)
    ch2 = BarChart()
    ch2.type, ch2.style = "col", 10
    ch2.title = "分项造价构成（除税，万元）"
    ch2.y_axis.title = "万元"
    data = Reference(ws3, min_col=C0 + 1, max_col=C0 + 7, min_row=hr, max_row=rr - 2)
    cats = Reference(ws3, min_col=C0, min_row=hr + 1, max_row=rr - 2)
    ch2.add_data(data, titles_from_data=True)
    ch2.set_categories(cats)
    ch2.height, ch2.width = 10, 24
    ws3.add_chart(ch2, "J%d" % (rr + 2))

    # ================================================================== 4-钢管混凝土选型
    ws4 = wb.create_sheet("4-钢管混凝土截面选型")
    ws4.cell(row=1, column=1,
             value=("钢管混凝土柱截面选型结果（%d 个设计点 × %d 种方案；实测%s，%s）"
                    % (NDP, len(CF4), U_NUM_4, U_VERDICT4))
             ).font = TITLE
    ws4.cell(row=2, column=1,
             value="设计点 = 结构标准层 × 柱位分组。同组多柱段按 ΣN、max M、max L0 取包络设计。"
                   "本次柱位组（按柱段数现算）：" + grp_legend + UNGRP_NOTE
             ).font = Font(italic=True, size=9, color="555555")
    ws4.cell(row=3, column=1,
             value="外轮廓：S2 沿用原柱 b×h；S3/S4 为圆管外径(mm)；S6 矩形按「短边×长边」给出"
                   "（保持原柱长宽比）。U_ax = N/Nu 轴力利用率；U_NM = 压弯综合利用率（式 5.3.1-4/5）；"
                   "θ = 套箍系数。本页限值 U ≤ %.2f 属用户指定目标 %s；最大值为本次数据现算。"
                   % (target, MANUAL)
             ).font = Font(italic=True, size=9, color="555555")
    ttl = ["标准层", "组", "原柱截面", "混凝土等级", "柱段数", "控制 N(kN)", "控制 M(kN·m)", "最大 L0(m)"]
    for k in ("S2", "S3", "S4", "S6"):
        ttl += ["%s 外轮廓" % k, "%s t(mm)" % k, "%s θ" % k,
                "%s U_ax" % k, "%s U_NM" % k, "%s 造价(万元)" % k]
    head(ws4, 4, ttl, [8, 6, 11, 10, 8, 12, 13, 10] + [12, 9, 8, 9, 9, 12], h=42)
    r = 5
    for k in KEYS:
        sn, g = k
        grp = src_grp[k]
        vals = [sn, g, "/".join(sorted(grp["secs"])), "/".join(sorted(grp["g"])), grp["n"],
                _grp_cell(grp, "Nu", "%.0f", 0), _grp_cell(grp, "M", "%.0f", 0),
                round(max(r_["L0_m"] for r_ in rows
                          if r_["标准层"] == sn and r_["组"] == g), 2)]
        for kk in CF4:
            x = sec_of[kk].get(k)                  # 该方案这个设计点没有截面数据时留 None
            if x is None:
                vals += ["无数据"] * 5 + [round(cf_cost[kk][k] / 1e4, 2)]
                continue
            vals += [x["外轮廓"], x["t"], round(x["theta"], 3),
                     round(x["U_ax"], 3), round(x["U_NM"], 3),
                     round(cf_cost[kk][k] / 1e4, 2)]
        r = put(ws4, r, vals,
                fmts=[None] * 8 + [None, N0, N3, N3, N3, N2] * 4)
    ws4.freeze_panes = "C5"

    # ================================================================== 5-现状RC基准
    ws5 = wb.create_sheet("5-现状钢筋混凝土柱(基准)")
    ws5.cell(row=1, column=1,
             value="S1 现状钢筋混凝土柱（实配方案）逐设计点工程量与造价 —— 比选基准"
             ).font = TITLE
    head(ws5, 3, ["标准层", "组", "截面", "混凝土等级", "柱段数", "层高(m)", "累计柱长(m)",
                  "控制 N(kN)", "控制柱位", "max Uc", "max Rs(%)", "max Rsv(%)",
                  "短柱段数", "混凝土(m³)", "纵筋(t)", "箍筋(t)", "模板(m²)", "造价(万元)"],
         [8, 6, 11, 10, 8, 12, 12, 12, 16, 9, 10, 11, 9, 12, 10, 10, 11, 12])
    r = 4
    for k in KEYS:
        grp = src_grp[k]
        r = put(ws5, r, [k[0], k[1], "/".join(sorted(grp["secs"])), "/".join(sorted(grp["g"])),
                         grp["n"], "/".join("%.1f" % h for h in sorted(grp["hs"])),
                         round(grp["Lc"], 2), _grp_cell(grp, "Nu", "%.1f", 1), grp["pos"],
                         _grp_cell(grp, "Uc", "%.3f", 3), _grp_cell(grp, "Rs", "%.2f"),
                         _grp_cell(grp, "Rsv", "%.2f"), grp["sh"],
                         round(rc_V[k], 1), round(rc_Wl[k], 2), round(rc_Ws[k], 2),
                         round(rc_A[k], 1), round(rc_cost[k] / 1e4, 2)],
                fmts=[None, None, None, None, N0, None, N2, N2, None, N3, N2, N2,
                      N0, N2, N2, N2, N2, N2])
    r = put(ws5, r, ["合计", "", "", "", sum(src_grp[k]["n"] for k in KEYS), "", round(TOTLEN, 1),
                     "", "", "", "", "", sum(src_grp[k]["sh"] for k in KEYS),
                     round(sum(rc_V.values()), 1), round(sum(rc_Wl.values()), 2),
                     round(sum(rc_Ws.values()), 2), round(sum(rc_A.values()), 1),
                     round(sum(rc_cost.values()) / 1e4, 2)],
            fmts=[None] * 4 + [N0, None, N2] + [None] * 3 + [None] * 2 + [N0] + [N2] * 5)
    for c in range(1, 19):
        ws5.cell(row=r - 1, column=c).font = Font(bold=True, size=10)
        ws5.cell(row=r - 1, column=c).fill = SUB_FILL
    ws5.freeze_panes = "A4"
    ws5.cell(row=r + 1, column=1,
             value="注：Uc / Rs / Rsv 取自 wpj*.out 实算值；Rs 为全截面纵筋配筋率(%%)，"
                   "Rsv 为体积配箍率(%%)。本次数据实测（现算）：混凝土等级 %s，%s，%s，%s。\n"
                   "%s GB 50011-2010 表 6.3.9 对高强混凝土柱的体积配箍率要求（1.2%%~1.3%%）"
                   "为外部规范值，是钢筋混凝土柱箍筋用量偏大的主要原因。"
                   % ("/".join(grade_set), UC_TXT, RS_TXT, RSV_TXT, MANUAL)
             ).font = Font(italic=True, size=9, color="555555")

    # ================================================================== 6-敏感性分析
    ws6 = wb.create_sheet("6-敏感性分析")
    ws6.cell(row=1, column=1,
             value=("敏感性分析 —— %d 种价格 / 构造 / 控制标准假设下的除税总造价对比" % NSENS
                    if sens else
                    "敏感性分析 —— 本次输入无敏感性数据（造价对比.json 的「敏感性」为空）")
             ).font = TITLE
    ws6.cell(row=2, column=1,
             value="所有情形均重新执行截面选型（含约束校核），非简单系数折算。单位：万元"
             ).font = Font(italic=True, size=9, color="555555")
    head(ws6, 4, ["类别", "情形", "S1 钢筋混凝土", "S2 矩形等轮廓", "S6 矩形最优",
                  "S4 圆形最优", "S4 / S1", "S6 / S1", "S2 / S1"],
         [13, 46, 14, 14, 13, 13, 10, 10, 10])
    r = 5
    for s in sens:                      # 键缺失时按空处理，与下文统计口径一致
        r = put(ws6, r, [s["类别"], s["情形"], s["S1_万元"], s["S2_万元"], s["S6_万元"],
                         s["S4_万元"], s["S4相对S1"] + 1, s["S6相对S1"] + 1, s["S2_万元"] / s["S1_万元"]],
                fmts=[None, None, N2, N2, N2, N2, PCT, PCT, PCT])
    if not sens:                        # 没有数据就明写"无数据"，不留空白表格让人当"0 种情形"读
        r = put(ws6, r, ["（无）", "本次输入没有敏感性数据：造价对比.json 的「敏感性」为空。"
                         "缺失不按 0% 计，本页不做任何敏感性结论。"])
        for cc in (1, 2):
            ws6.cell(row=r - 1, column=cc).fill = BAD
    ws6.freeze_panes = "A5"
    ws6.cell(row=r + 1, column=1, value=SENS_FOOT
             ).font = Font(bold=True, size=10, color="C00000")

    # ================================================================== 7-定额与价格依据
    ws7 = wb.create_sheet("7-定额与价格依据")
    ws7.cell(row=1, column=1,
             value="计价依据明细：广东省房屋建筑与装饰工程综合定额(2018) 定额子目 + 广州市 2026 年 6 月信息价"
             ).font = TITLE
    head(ws7, 3, ["定额编号", "定额名称", "单位", "基价(元)", "人工费", "材料费", "机具费", "管理费"],
         [12, 46, 8, 12, 11, 11, 11, 11])
    r = 4
    for code in QUOTA_ORDER:
        nm, u, b, lab, mat, mac, mgr = G.QUOTA[code]
        r = put(ws7, r, [code, nm, u, b, lab, mat, mac, mgr],
                fmts=[None, None, None, N2, N2, N2, N2, N2])
    r += 1
    ws7.cell(row=r, column=1, value="取费与换算规则").font = Font(bold=True, size=11)
    r += 1
    rules = [
        "利润 =（定额人工费 + 定额施工机具费）× %.2f%%（gz_quota.PROFIT，现算）" % (G.PROFIT * 100),
        "管理费 =（定额人工费 + 定额施工机具费）× 分摊费率；按 gz_quota 定额子目现算："
        "混凝土及钢筋混凝土 %.2f%% / 模板工程 %.2f%% / 金属结构工程 %.2f%% / 油漆涂料 %.2f%%（已含于定额基价）"
        % (mgr_conc, mgr_form, mgr_steel, mgr_paint),
        "增值税 = 综合单价 × %.0f%%（gz_quota.VAT，现算）；定额基价与广州市信息价均为不含税口径"
        % (G.VAT * 100),
        "现浇柱混凝土（A1-5-5）：定额基价不含混凝土材料，混凝土按广州市信息价 ×（1+%.1f%% 损耗，"
        "gz_quota.CONC_LOSS 现算）另计" % ((G.CONC_LOSS - 1.0) * 100),
        "柱模板：按柱周长选子目（1.2m内 / 1.8m内 / 1.8m外），支模高度超 3.6m 者每增 1m 叠加 A1-20-19（不足 1m 按 1m 计）",
        "带肋钢筋：按定额内含钢筋用量（%.3f~%.3f t/t，gz_quota.REBAR_DOSE 现算）从材料费中扣除定额钢筋价，"
        "再按信息价换入" % (min(G.REBAR_DOSE.values()), max(G.REBAR_DOSE.values())),
        "钢柱安装：钢柱为「未计价主材」，需另计钢管材料费（钢板信息价 × (1+%.0f%% 下料损耗) + 制作加工费 "
        "%.0f 元/t；损耗与加工费为参数值 %s）；定额不含除锈油漆与探伤"
        % (tube_loss * 100, fab_cost, MANUAL),
        "钢管混凝土工程量规则（GB 50936）：节点板、加强环、内衬管、牛腿并入钢管柱质量；管内混凝土体积按钢管内径计算",
    ]
    for t in rules:
        c = ws7.cell(row=r, column=1, value=t)
        c.alignment = Alignment(wrap_text=True, vertical="top")
        ws7.merge_cells(start_row=r, start_column=1, end_row=r, end_column=8)
        ws7.row_dimensions[r].height = max(16, 14.0 * (1 + len(t) // 78))
        r += 1
    r += 1
    ws7.cell(row=r, column=1, value="广州市 2026 年 6 月信息价（税前，不含销项税；穗建造价〔2026〕62 号）"
             ).font = Font(bold=True, size=11)
    r += 1
    head(ws7, r, ["材料", "规格", "单位", "价格(元)", "口径", "", "", ""],
         [22, 22, 8, 12, 30, 10, 10, 10], h=20)
    r += 1
    for g, v in G.CONC_PRICE_PUMP.items():
        r = put(ws7, r, ["预拌混凝土（泵送）", g, "m³", v, "税前综合价格"] + [""] * 3,
                fmts=[None, None, None, N2])
    for g, v in G.CONC_PRICE.items():
        r = put(ws7, r, ["预拌混凝土（非泵送）", g, "m³", v, "税前综合价格"] + [""] * 3,
                fmts=[None, None, None, N2])
    for g, v in G.REBAR_PRICE.items():
        r = put(ws7, r, ["螺纹钢 HRB400E", g, "t", v, "税前综合价格"] + [""] * 3,
                fmts=[None, None, None, N2])
    for lo, hi, p in G.PLATE_PRICE_Q355:
        r = put(ws7, r, ["热轧厚钢板 Q355", "%g~%g mm" % (lo, hi), "t", p, "税前综合价格"]
                + [""] * 3, fmts=[None, None, None, N2])
    r = put(ws7, r, ["人工费价格指数", "穗建造价〔2026〕62号", "—", G.LABOR_INDEX,
                     "用于敏感性分析（基准取 1.000）"] + [""] * 3,
            fmts=[None, None, None, "0.0000"])
    r += 1
    ws7.cell(row=r, column=1, value="非定额项（市场估值，已在敏感性分析中覆盖）").font = Font(bold=True, size=11)
    r += 1
    for t in ["钢管柱制作加工费 %.0f 元/t（取自 造价对比.json 的参数，市场行情估值 %s；"
              "敏感性另覆盖 1100~1600 元/t %s）" % (fab_cost, MANUAL, MANUAL),
              "钢板下料损耗 %.0f%%（参数值 %s）" % (tube_loss * 100, MANUAL),
              "节点附件系数 %.2f（加强环、内衬管、牛腿、节点板并入钢管柱质量；参数值，"
              "敏感性另覆盖 1.00~1.15 %s）" % (attach, MANUAL)]:
        c = ws7.cell(row=r, column=1, value=t)
        c.alignment = Alignment(wrap_text=True, vertical="top")
        ws7.merge_cells(start_row=r, start_column=1, end_row=r, end_column=8)
        r += 1
    ws7.freeze_panes = "A4"

    # ================================================================== 8-逐柱明细
    ws8 = wb.create_sheet("8-逐柱明细(%d段)" % NSEC)
    ws8.cell(row=1, column=1,
             value="逐柱段明细（%d 段 = %d 自然层，每层最多 %s 根柱）：内力输入 + S1 钢筋混凝土造价 "
                   "+ S2/S4/S6 钢管混凝土造价"
                   % (NSEC, NFLR, meta.get("每层柱数", "?"))
             ).font = TITLE
    ttl = ["自然层", "标准层", "柱号", "组", "层高(m)", "跃层", "Nu(kN)", "M(kN·m)",
           "L0x(m)", "L0y(m)",
           "S1 截面", "S1 等级", "S1 Uc", "S1 混凝土(m³)", "S1 纵筋(t)", "S1 箍筋(t)",
           "S1 模板(m²)", "S1 造价(万元)",
           "S2 外轮廓", "S2 t", "S2 θ", "S2 U_NM", "S2 造价(万元)",
           "S4 外径", "S4 t", "S4 θ", "S4 U_NM", "S4 造价(万元)",
           "S6 外轮廓", "S6 t", "S6 θ", "S6 U_NM", "S6 造价(万元)"]
    head(ws8, 3, ttl, [7, 7, 6, 5, 8, 6, 10, 10, 8, 8] + [10, 8, 8, 11, 10, 10, 10, 11]
         + [11, 6, 7, 8, 11] * 3, h=44)
    r = 4
    rc_seg = {(x["自然层"], x["柱号"]): x for x in det["S1"]}
    for x in sorted(rows, key=lambda y: (y["自然层"], y["柱号"])):
        c = rc_seg[(x["自然层"], x["柱号"])]
        vals = [x["自然层"], x["标准层"], "N%d" % x["柱号"], x["组"], x["层高_m"],
                "是" if x["跃层"] else "", _rnum(x.get("Nu"), 1), _rnum(x.get("Mmax"), 1),
                x["L0x_m"], x["L0y_m"],
                "%d×%d" % (x["b"], x["h"]), x["混凝土"], _rnum(x.get("Uc"), 3),
                c["V_m3"], c["纵筋_t"], c["箍筋_t"], c["模板_m2"], round(c["造价"] / 1e4, 3)]
        fmts = [None] * 10 + [None, None, N3, N3, N3, N3, N2, N3]
        for kk in ("S2", "S4", "S6"):
            s = cf_seg[kk][(x["自然层"], x["柱号"])]
            vals += [s["外轮廓"], s["t"], round(s["theta"], 3), round(s["U"], 3),
                     round(s["造价"] / 1e4, 3)]
            fmts += [None, N0, N3, N3, N3]
        r = put(ws8, r, vals, fmts=fmts)
    r = put(ws8, r, ["合计"] + [""] * 4 + [round(TOTLEN, 1)] + [""] * 4
            + [""] * 3 + [round(sum(rc_V.values()), 1), round(sum(rc_Wl.values()), 2),
                          round(sum(rc_Ws.values()), 2), round(sum(rc_A.values()), 1),
                          round(sum(rc_cost.values()) / 1e4, 2)]
            + [""] * 4 + [round(sum(cf_cost["S2"].values()) / 1e4, 2)]
            + [""] * 4 + [round(sum(cf_cost["S4"].values()) / 1e4, 2)]
            + [""] * 4 + [round(sum(cf_cost["S6"].values()) / 1e4, 2)],
            fmts=[None] * 6 + [None] * 4 + [None] * 3 + [N2, N2, N2, N2, N2]
            + [None, None, None, None, N2] * 3)
    for c in range(1, len(ttl) + 1):
        ws8.cell(row=r - 1, column=c).font = Font(bold=True, size=10)
        ws8.cell(row=r - 1, column=c).fill = SUB_FILL
    ws8.freeze_panes = "E4"

    # ================================================================== 9-复核与决策
    ws9 = wb.create_sheet("9-复核与决策清单")
    ws9.column_dimensions["A"].width = 7
    ws9.column_dimensions["B"].width = 26
    ws9.column_dimensions["C"].width = 40
    ws9.column_dimensions["D"].width = 66
    ws9.cell(row=1, column=1, value="复核清单与决策要点").font = TITLE
    head(ws9, 3, ["序号", "项目", "判据 / 目标（外部判据 %s）" % MANUAL, "说明"], [7, 26, 40, 66])
    # 长细比 / 收缩 / 壁厚的现算文案：判据是「现算值 vs 规范限值」的比较结果，
    # 不是写死的「< 80 → 满足」；没有对应截面时明写「无数据」，不按 0mm 作结论。
    if lam_where:
        lam_text = ("圆管 i = D/4。实测最不利（现算）：λ = %.1f，出现在自然层 %d 柱 %d"
                    "（L0 = %.1f m，D = %.0f mm）→ %s。"
                    % (lam_lo, lam_where[0], lam_where[1], lam_where[3], lam_where[2],
                       "满足 [λ] = 80" if lam_lo <= 80 else
                       "★ 超过 [λ] = 80，须加大圆管外径或减小计算长度"))
    else:
        lam_text = "本次数据无可用圆管截面，该值（本报告未计算）。"
    _circ_txt = ("最大圆管外径 %.0f mm" % D_ext_max) if D_ext_max is not None \
        else "本次截面表没有圆管截面（最大圆管外径：无数据）"
    _rect_txt = ("矩形最大边长 %.0f mm" % rect_long_max) if rect_long_max is not None \
        else "本次截面表没有矩形钢管截面（矩形最大边长：无数据）"
    thick_text = ("实测（现算）：本报告最小壁厚 %gmm（%s %s；配置下限 %gmm 为参数值 %s）；"
                  "%s、%s。"
                  % (t_lo, t_lo_k, DP(t_lo_g), t_min_cfg, MANUAL, _circ_txt, _rect_txt)) \
        if t_lo is not None else \
        "实测（现算）：本次截面表为空，最小壁厚 无数据（本报告未计算）；配置下限 %gmm 为参数值 %s。" \
        % (t_min_cfg, MANUAL)
    _shrink = []
    if D_ext_max is not None:
        _shrink.append("最大圆管外径 %.0f mm%s2000mm"
                       % (D_ext_max, " > " if D_ext_max > 2000 else " < "))
    if rect_long_max is not None:
        _shrink.append("矩形最大边长 %.0f mm%s1500mm"
                       % (rect_long_max, " > " if rect_long_max > 1500 else " < "))
    _over = ((D_ext_max is not None and D_ext_max > 2000)
             or (rect_long_max is not None and rect_long_max > 1500))
    _shr_miss = [t for t, v in (("无圆管截面数据", D_ext_max),
                                ("无矩形钢管截面数据", rect_long_max)) if v is None]
    if not _shrink:
        shrink_text = "实测（现算）：本次截面表没有圆管/矩形钢管截面，该值（本报告未计算）。"
    else:
        shrink_text = ("实测（现算）：%s → %s%s。"
                       % ("；".join(_shrink),
                          "★ 已超过 GB 50936 第 4.1.11 条的界限，需采取收缩控制专项措施"
                          if _over else
                          ("已校验的截面均不需专项措施" if _shr_miss else "均不需专项措施"),
                          ("（%s，该部分未校验）" % "、".join(_shr_miss)) if _shr_miss else ""))
    checks = [
        ("整体实算复核", "层间位移角、层刚度比、周期满足规范",
         "柱截面形式改变会改变抗弯刚度 → 内力重分布、位移角与刚度比变化。本报告未做实算，"
         "必须用 YJK 重新「生成数据 + 全部计算」后核对 wdisp.out / wmass.out。"
         "（各项限值取自规范，%s）" % MANUAL),
        ("承载力利用率", "U_ax ≤ %.2f 且 U_NM ≤ %.2f（用户指定目标 %s）" % (target, target, MANUAL),
         "实测（现算，%d 个设计点 × %d 种方案）：%s，%s。"
         "若实算内力变化，需按新内力重选截面。"
         % (NDP, len(CFALL), U_NUM_ALL, U_VERDICT2)),
        ("套箍系数", "θ ∈ [%.2f, %.2f]（GB 50936 第 4.3.2 条推荐值 %s）" % (theta_min, theta_max, MANUAL),
         THETA_ROW),
        ("径厚比", "圆管 D/t ≤ %g；方管 b/t ≤ %g（构造要求 %s）" % (dt_max_cfg, bt_max_cfg, MANUAL),
         RATIO_ROW),
        ("壁厚构造", "外径/边长 ≥ 168mm、壁厚 ≥ 3mm（GB 50936 第 4.3.1 条，外部规范值 %s）" % MANUAL,
         thick_text),
        ("长细比", "框架柱容许长细比 [λ] = 80（GB 50936 第 4.1.7 条，外部规范值 %s）" % MANUAL,
         lam_text),
        ("收缩影响", "直径 > 2m 或边长 > 1.5m 需采取措施（GB 50936 第 4.1.11 条，外部规范值 %s）" % MANUAL,
         shrink_text),
        ("节点构造", "梁纵筋与钢管连接、加强环/内衬管/穿心板",
         "本报告按附件系数 %.2f 粗估并入钢管质量（参数值 %s），未做节点专项设计。"
         "%s结构梁柱节点处梁纵筋密集，钢管柱节点构造往往是造价与工期的控制因素，须单独深化。"
         % (attach, MANUAL, a.system or "本工程（结构体系未注明）")),
        ("防火涂料", "一级耐火等级柱耐火极限 3.0h（外部假定 %s）" % MANUAL,
         ("按子目 %s「%s」计取（子目选择 %s），实测占钢管混凝土造价 %.0f%%~%.0f%%。"
          "若建筑同意包覆方案可大幅降低%s。"
          % (fire_code, fire_name, MANUAL, fire_share_lo, fire_share_hi, SENS_REF_FIRE))
         if fire_share else
         ("按子目 %s「%s」计取（子目选择 %s），本次无防火涂料造价占比数据（该项未做评价）。"
          % (fire_code, fire_name, MANUAL))),
        ("管内混凝土浇筑", "泵送、振捣、密实度与收缩控制",
         "钢管内混凝土浇筑需专用工艺（免振自密实或导管法），本报告混凝土单价沿用现浇柱定额，"
         "未含特殊措施费，可能低估。"),
        ("基础影响", "柱自重下降对桩基的有利影响",
         "钢管混凝土柱自重显著小于钢筋混凝土柱（管内混凝土 %.1f m³ vs %.1f m³，现算），"
         "可能减少桩基用量。本报告不含基础，属未计入的对钢管混凝土有利因素。"
         % (sche["S4"]["工程量"]["V"], sche["S1"]["工程量"]["V"])),
        ("柱平面占用",
         ("S4 可减少柱平面占用（实测 %.0f%%）" % CUT_S4) if CUT_S4 is not None
         else "S4 可减少柱平面占用（实测 无数据，该项未校验）",
         PLAN_ROW),
        ("决策建议", "以工程量/造价为唯一依据 → 维持钢筋混凝土柱（人工判断 %s）" % MANUAL,
         "实测（现算）：最经济的钢管混凝土方案（%s）造价为 S1 的 %.2f 倍（贵 %.0f%%）。"
         "若需缩小柱截面、缩短工期或业主指定，推荐圆形截面（S4 型）而非矩形。"
         % (cf_min_k, RAT[cf_min_k], (RAT[cf_min_k] - 1) * 100)),
    ]
    r = 4
    for i, (item, judge, note) in enumerate(checks, start=1):   # ★ 不可用 a：a 是 argparse Namespace
        r = put(ws9, r, [i, item, judge, note])
        for cc in (3, 4):
            ws9.cell(row=r - 1, column=cc).alignment = Alignment(wrap_text=True, vertical="top")
        ws9.cell(row=r - 1, column=2).alignment = Alignment(wrap_text=True, vertical="top")
        ws9.row_dimensions[r - 1].height = max(28, 13.0 * (1 + len(note) // 60))

    wb.calculation.fullCalcOnLoad = True
    wb.save(out_path)
    print("已生成：%s" % out_path)


# 定额子目输出顺序
QUOTA_ORDER = [
    "A1-5-5",
    "A1-5-105", "A1-5-106", "A1-5-107",
    "A1-20-14", "A1-20-15", "A1-20-16", "A1-20-19",
    "A1-7-30", "A1-7-31", "A1-7-32", "A1-7-33",
    "A1-15-126", "A1-15-127", "A1-15-128", "A1-15-129", "A1-15-130",
    "A1-15-131", "A1-15-132", "A1-15-133", "A1-15-134", "A1-15-135",
]

if __name__ == "__main__":
    main()
