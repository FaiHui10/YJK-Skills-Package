# -*- coding: utf-8 -*-
"""生成「可手工调整」的截面设计表（Excel），并能把它读回成方案。

用途
----
程序算完截面后不直接定案，而是导出一张 Excel：
  * 「截面参数」表是**可编辑区**——设计人直接改 b/h/u/t/d/f 与材料等级；
  * 几何、面积、含钢率、占用面积、用量造价全是公式，改完立刻看到新结果；
  * 改完用 `cli.py import-excel` 读回，生成新的 scheme.json（并给出与程序方案的差异）。

写出用标准库拼 OOXML（不依赖 openpyxl）；**读回**用户改过的文件需要 openpyxl。
"""
import datetime
import os

from quantity import (DEFAULT_PRICES, FIRE_T, RHO, STEEL_KIND, BASE_TYPE, base_of,
                      DEFAULT_REBAR, DEFAULT_TIE, colname, esc, geom, price,
                      rebar_of, tie_of, write_wb, nat_heights, n_floors, total_height_m)

# 截面参数表列顺序（0 基）。E 列起为公式列，其余为可编辑区/文本。
COLS = ["柱型", "标准层", "归并组", "柱号", "柱数", "Kind",
        "b", "h", "u", "t", "d", "f", "混凝土等级", "钢材牌号",
        "混凝土面积m²", "钢材面积m²", "含钢率", "模板周长m", "防火表面m²/m", "结构占用面积m²",
        "截面", "复核", "纵筋率", "体积配箍率", "钢材单价元/t"]
EDITABLE = list(range(0, 14))          # A..N 允许人工修改
R0 = 3                                  # 数据首行
KIND_HINT = {1: "矩形RC：填 b", 12: "圆钢管混凝土：填 b=外径、h=内径(外径−2×壁厚)",
             15: "十字型钢：b=柱边长、u=t=板厚、d=腹板高、f=翼缘宽",
             102: "叠合柱：b=柱边长、u=内管外径、t=内管内径(外径−2×壁厚)"}


def _f(x):
    return ("f", "=" + x, None)


def write_design_book(scheme, forces, report, grades, out_path, cfg=None, notes=None):
    """导出截面设计表。report 需含 design.make_sections 的 report 列表。"""
    cfg = cfg or {}
    types = scheme["types"]
    base = base_of(types)
    stds = sorted(int(x) for x in scheme["std_floors"])
    groups = scheme["groups"]

    # ---------- 单价
    s_price = [["项目", "数值", "单位/说明"]]
    for k, (v, u) in DEFAULT_PRICES.items():
        s_price.append([k, price(scheme, k), u])
    s_price += [["钢材密度", RHO, "t/m³"],
                ["防火涂料厚度", FIRE_T, "mm（圆钢管混凝土柱占用面积按 钢管外径+2×该值）"],
                ["对比基准柱型", base, "相对造价/占用的分母"]]
    row_fire = 2 + len(DEFAULT_PRICES) + 1
    row_rho = 2 + len(DEFAULT_PRICES)
    FT_C = "'单价'!$B$%d" % row_fire
    RHO_C = "'单价'!$B$%d" % row_rho
    P_CON, P_RB = "'单价'!$B$2", "'单价'!$B$3"
    P_FORM, P_FIRE = "'单价'!$B$6", "'单价'!$B$7"

    # ---------- 设计参数
    s_par = [["标准层", "自然层", "定义层高mm", "代表楼层总高m", "覆盖自然层数",
              "混凝土等级", "钢材牌号", "材料来源", "管内混凝土等级", "管内来源", "层高明细mm"]]
    for std in stds:
        c = scheme["std_floors"][str(std)]
        g = (grades or {}).get(std, {})
        s_par.append([std, "/".join(str(x) for x in _nats(c)), c["height_mm"],
                      round(total_height_m(c), 3), n_floors(c),
                      g.get("混凝土", cfg.get("concrete", "C60")),
                      g.get("钢号", cfg.get("steel_grade", "Q355")),
                      g.get("来源", "config 默认"),
                      g.get("管内混凝土", g.get("混凝土", "")),
                      g.get("管内来源", "按管外取值（未确认）"),
                      "+".join("%g" % h for h in nat_heights(c))])

    # ---------- 截面参数（可编辑）
    head = ["截面参数 —— A~N 列可直接改；O 列以后为公式，改完自动重算"] + [""] * (len(COLS) - 1)
    s_sec = [head, list(COLS)]
    rpt = {(r["type"], r["std"], r["group"]): r for r in report if r.get("ok")}
    nrow = 0
    for t in types:
        for std in stds:
            for gname, members in groups.items():
                geo = scheme["sections"].get(t, {}).get(str(std), {}).get(gname)
                if geo is None:
                    continue
                g = geom(geo)
                i = len(s_sec) + 1
                r = rpt.get((t, std, gname), {})
                conc = "IF($F{r}=12,PI()/4*($H{r}/1000)^2,$G{r}/1000*$H{r}/1000)".format(r=i)
                steel = ("IF($F{r}=12,PI()/4*(($G{r}/1000)^2-($H{r}/1000)^2),"
                         "IF($F{r}=15,(4*$L{r}*$J{r}+2*$K{r}*$J{r}-$J{r}^2)/1000000,"
                         "IF($F{r}=102,PI()/4*(($I{r}/1000)^2-($J{r}/1000)^2),0)))".format(r=i))
                peri = "IF($F{r}=12,0,2*($G{r}+$H{r})/1000)".format(r=i)
                fire = "IF($F{r}=12,PI()*($G{r}/1000+2*{ft}/1000),0)".format(r=i, ft=FT_C)
                occ = ("IF($F{r}=12,PI()/4*($G{r}/1000+2*{ft}/1000)^2,"
                       "$G{r}/1000*$H{r}/1000)".format(r=i, ft=FT_C))
                rhoa = 'IF($F{r}=12,"",$P{r}/($G{r}*$H{r}/1000000))'.format(r=i)
                ck = r.get("check") or {}
                s_sec.append([
                    t, "标准层%d" % std, gname,
                    "/".join("N%s" % c for c in members), len(members), g["k"],
                    g["b"], g["h"], g["u"], g["t"], g["d"], g["f"],
                    (grades or {}).get(std, {}).get("混凝土", cfg.get("concrete", "C60")),
                    (grades or {}).get(std, {}).get("钢号", cfg.get("steel_grade", "Q355")),
                    _f(conc), _f(steel), _f(rhoa), _f(peri), _f(fire), _f(occ),
                    g["sec"],
                    "；".join("%s=%s" % (k, v) for k, v in ck.items()) or "-",
                    rebar_of(scheme, t), tie_of(scheme, t) / 100.0,
                    price(scheme, STEEL_KIND[t]) if t in STEEL_KIND else 0.0,
                ])
                nrow += 1
    last = R0 + nrow - 1

    # ---------- 用量造价（全公式，引用截面参数）
    def spm(t, std, cols):
        """SUMPRODUCT(柱型=…)*(标准层=…)*(柱数)×(各列乘积) —— 列名须完全限定。"""
        parts = ["('截面参数'!$A$%d:$A$%d=\"%s\")" % (R0, last, t),
                 "('截面参数'!$B$%d:$B$%d=\"标准层%d\")" % (R0, last, std),
                 "'截面参数'!$E$%d:$E$%d" % (R0, last)]
        for c in cols:
            parts.append("'截面参数'!$%s$%d:$%s$%d" % (c, R0, c, last))
        return "SUMPRODUCT(%s)" % "*".join(parts)

    nkg = len(types) * len(stds)
    klo, khi = 2, 1 + nkg                                   # 用量表数据行范围
    s_qty = [["柱型", "标准层", "代表楼层总高m", "自然层数",
              "混凝土m³", "钢筋t", "型钢/钢管t", "模板m²", "防腐防火m²",
              "结构占用面积m²", "造价元", "相对%s造价%%" % base,
              "相对%s占用%%" % base]]
    for t in types:
        for std in stds:
            i = len(s_qty) + 1
            hr = 2 + stds.index(std)                         # 设计参数表对应行
            s_qty.append([
                t, "标准层%d" % std,
                _f("='设计参数'!$D$%d" % hr), _f("='设计参数'!$E$%d" % hr),
                _f("=%s*$C%d" % (spm(t, std, ["O"]), i)),
                _f("=(%s+%s)*$C%d*%s" % (spm(t, std, ["T", "W"]), spm(t, std, ["T", "X"]),
                                         i, RHO_C)),
                _f("=%s*$C%d*%s" % (spm(t, std, ["P"]), i, RHO_C)),
                _f("=%s*$C%d" % (spm(t, std, ["R"]), i)),
                _f("=%s*$C%d" % (spm(t, std, ["S"]), i)),
                _f("=%s*$D%d" % (spm(t, std, ["T"]), i)),
                _f("=$E%d*%s+$F%d*%s+$G%d*%s+$H%d*%s+$I%d*%s"
                   % (i, P_CON, i, P_RB, i, spm(t, std, ["P", "Y"]), i, P_FORM, i, P_FIRE)),
                _f("=$K%d/(SUMIFS($K$%d:$K$%d,$A$%d:$A$%d,\"%s\",$B$%d:$B$%d,$B%d))-1"
                   % (i, klo, khi, klo, khi, base, klo, khi, i)),
                _f("=$J%d/(SUMIFS($J$%d:$J$%d,$A$%d:$A$%d,\"%s\",$B$%d:$B$%d,$B%d))-1"
                   % (i, klo, khi, klo, khi, base, klo, khi, i)),
            ])
    s_qty.append([])
    i0 = len(s_qty) + 1
    s_qty.append(["柱型", "总造价元", "相对%s造价%%" % base, "总占用面积m²",
                  "相对%s占用%%" % base, "换回楼面面积m²", "造价增量元",
                  "投入产出比元/m²"])
    for k, t in enumerate(types):
        i = len(s_qty) + 1
        lo, hi = klo + k * len(stds), khi - (len(types) - 1 - k) * len(stds)
        s_qty.append([
            t, _f("=SUM($K$%d:$K$%d)" % (lo, hi)),
            _f("=$B%d/$B$%d-1" % (i, i0 + 1)),
            _f("=SUM($J$%d:$J$%d)" % (lo, hi)),
            _f("=$D%d/$D$%d-1" % (i, i0 + 1)),
            _f("=$D$%d-$D%d" % (i0 + 1, i)),
            _f("=$B%d-$B$%d" % (i, i0 + 1)),
            _f('=IF(ABS($F%d)<0.0001,"--",$G%d/$F%d)' % (i, i, i)),
        ])

    # ---------- 说明
    note = [["项目", scheme.get("project", "")],
            ["生成时间", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            ["怎么改", "在「截面参数」表改 G~N 列（b/h/u/t/d/f、混凝土等级、钢材牌号），"
                       "O 列以后自动重算；「设计参数」表可改各标准层的混凝土等级。"],
            ["各 Kind 怎么填", "；".join("%s → %s" % (k, v) for k, v in KIND_HINT.items())],
            ["改完怎么办", "运行 `cli.py import-excel --xlsx 本文件 --scheme 原scheme.json "
                           "--out 新scheme.json`，程序会读回截面并与原方案比对差异。"],
            ["公式说明", "所有几何/面积/占用/用量/造价均为公式；改单价请改「单价」表。"],
            ["口径", "结构占用面积为“每层”量，合计时乘自然层数；"
                     "圆钢管混凝土柱占用面积 = π/4×(外径+2×涂料厚)²。"],
            ["造价口径", "方案阶段综合单价（含材料+制作安装，不含税），"
                         "不含基础、节点加劲与吊装措施费。"]]
    # 叠合柱提醒：管内混凝土读不到
    diehe = [t for t in types if t in ("钢管叠合柱", "叠合柱")]
    if diehe:
        note.append(["★叠合柱管内混凝土",
                     "管内（核心）混凝土等级**无法从 wmass.out 读取**，它保存在模型 .yjk "
                     "二进制里，脚本读不到也写不进去。本表按「设计参数」表的“管内混凝土等级”"
                     "计算，**请务必到 YJK 里确认并设置该等级**；修改本表该列并重新导入即可。"
                     "管外混凝土按 wmass.out 读到的等级参与计算。"])
    for w in (notes or []):
        note.append(["提示", w])

    sheets = [("说明", note), ("设计参数", s_par), ("单价", s_price),
              ("截面参数", s_sec), ("用量造价", s_qty)]
    write_wb(out_path, sheets)
    return {"out": out_path, "rows": nrow, "sheets": [n for n, _ in sheets]}


def _nats(cfg):
    first = cfg.get("first_nat")
    n = len(nat_heights(cfg))
    return [first + i for i in range(n)] if first else list(range(1, n + 1))


# ---------------------------------------------------------------- 读回
def read_design_book(path):
    """读回用户改过的设计表。返回 {"sections":…, "grades":…, "warnings":[…]}

    sections = {柱型: {标准层: {组: geo}}}；grades = {标准层: {混凝土, 钢号, 管内混凝土}}
    """
    try:
        import openpyxl
    except ImportError:
        raise SystemExit("读回 Excel 需要 openpyxl（先 pip install openpyxl）。"
                         "若确实没有，请人工改 scheme.json。")
    wb = openpyxl.load_workbook(path, data_only=False)
    warnings = []
    if "截面参数" not in wb.sheetnames:
        raise SystemExit("文件里没有「截面参数」表，确认这是本工具导出的设计表。")
    ws = wb["截面参数"]
    hdr = [c.value for c in ws[2]]
    if hdr[:2] != ["柱型", "标准层"]:
        raise SystemExit("「截面参数」表头不是预期的第 2 行，请勿调整表头位置。")
    idx = {name: i for i, name in enumerate(hdr) if name}

    sections = {}
    for row in ws.iter_rows(min_row=R0, values_only=True):
        if not row or not row[0]:
            continue
        t, std = str(row[idx["柱型"]]).strip(), str(row[idx["标准层"]]).strip()
        gname = str(row[idx["归并组"]]).strip()
        kind = int(float(row[idx["Kind"]]))
        v = lambda n: row[idx[n]]
        if kind == 1:
            geo = {"kind": 1, "b": float(v("b"))}
        elif kind == 12:
            geo = {"kind": 12, "D": float(v("b")), "tw": (float(v("b")) - float(v("h"))) / 2.0}
        elif kind == 15:
            geo = {"kind": 15, "b": float(v("b")), "f": float(v("f")),
                   "tw": float(v("t")), "d": float(v("d"))}
        elif kind == 102:
            geo = {"kind": 102, "b": float(v("b")), "D": float(v("u")),
                   "tw": (float(v("u")) - float(v("t"))) / 2.0}
        else:
            warnings.append("跳过未知 Kind=%s（%s/标准层%s/%s）" % (kind, t, std, gname))
            continue
        sections.setdefault(t, {}).setdefault(std.replace("标准层", ""), {})[gname] = geo

    grades = {}
    if "设计参数" in wb.sheetnames:
        wp = wb["设计参数"]
        ph = [c.value for c in wp[1]]
        pi = {n: i for i, n in enumerate(ph) if n}
        for row in wp.iter_rows(min_row=2, values_only=True):
            if not row or row[pi["标准层"]] is None:
                continue
            std = int(row[pi["标准层"]])
            rec = {"混凝土": row[pi["混凝土等级"]],
                   "钢号": row[pi["钢材牌号"]],
                   "来源": "设计表（人工确认）"}
            if "管内混凝土等级" in pi and row[pi["管内混凝土等级"]]:
                rec["管内混凝土"] = row[pi["管内混凝土等级"]]
                rec["管内来源"] = "设计表（人工确认）"
            grades[std] = rec
    return {"sections": sections, "grades": grades, "warnings": warnings}


def apply_to_scheme(scheme, book):
    """把读回的内容写进 scheme 的副本，返回 (新scheme, 差异列表)。"""
    import copy
    new = copy.deepcopy(scheme)
    diffs = []
    for t, bystd in book["sections"].items():
        if t not in new["sections"]:
            new["sections"][t] = {}
            diffs.append(("新增柱型", t, "", ""))
        for std, bygrp in bystd.items():
            for gname, geo in bygrp.items():
                old = new["sections"].get(t, {}).get(std, {}).get(gname)
                if old != geo:
                    diffs.append((t, std, gname,
                                  geom(old)["sec"] if old else "-", geom(geo)["sec"]))
                new["sections"].setdefault(t, {}).setdefault(std, {})[gname] = geo
    new["_grades"] = book["grades"]
    return new, diffs
