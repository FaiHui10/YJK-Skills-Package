# -*- coding: utf-8 -*-
"""把各轮迭代结果汇总成 Excel 汇报（支持任意层数、分等级单价）。

用法：
    python report.py --config c.json --out 汇报.xlsx iter_*.json

「单价与假定」表可编辑；造价列全部用公式（按等级查表），改单价即自动重算。
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import load_config  # noqa: E402

from openpyxl import Workbook  # noqa: E402
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side  # noqa: E402
from openpyxl.utils import get_column_letter  # noqa: E402

TITLE = Font(bold=True, size=14)
HEAD = Font(bold=True, color="FFFFFF")
HEAD_FILL = PatternFill("solid", fgColor="4F6228")
SUB_FILL = PatternFill("solid", fgColor="D8E4BC")
BAD = PatternFill("solid", fgColor="FFC7CE")
OK = PatternFill("solid", fgColor="E2EFDA")
EDIT = PatternFill("solid", fgColor="FFF2CC")
THIN = Side(style="thin", color="999999")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
MONEY, NUM3, NUM2 = "#,##0", "0.000", "0.00"


def head(ws, row, titles, widths=None):
    for c, t in enumerate(titles, start=1):
        cell = ws.cell(row=row, column=c, value=t)
        cell.font, cell.fill = HEAD, HEAD_FILL
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = BORDER
    if widths:
        for c, w in enumerate(widths, start=1):
            ws.column_dimensions[get_column_letter(c)].width = w
    ws.row_dimensions[row].height = 30


def put(ws, row, values, fmts=None):
    for c, v in enumerate(values, start=1):
        cell = ws.cell(row=row, column=c, value=v)
        cell.border = BORDER
        if fmts and c - 1 < len(fmts) and fmts[c - 1]:
            cell.number_format = fmts[c - 1]
    return row + 1


def floors_of(cfg):
    return sorted(int(k) for k in cfg if str(k).isdigit())


def grade_seq(sections):
    fs, out, run_g, run_s = floors_of(sections), [], None, None
    for f in fs:
        g = sections[str(f)].get("grade", "?")
        if g != run_g:
            if run_g is not None:
                out.append((run_s, prev, run_g))
            run_g, run_s = g, f
        prev = f
    out.append((run_s, prev, run_g))
    return "; ".join(("第%d层:%s" % (a, g)) if a == b else ("第%d-%d层:%s" % (a, b, g))
                     for a, b, g in out)


def sec_seq(sections, groups):
    return "；".join("F%d %s" % (f, "/".join("%s%d" % (g, sections[str(f)][g]) for g in groups))
                     for f in floors_of(sections))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("iters", nargs="+")
    a = ap.parse_args()
    cfg = load_config(a.config)
    iters = [json.load(open(p, encoding="utf-8")) for p in a.iters]
    final = iters[-1]
    groups = cfg["截面"]["分组"]
    nf = cfg["几何"]["层数"]
    grades = list(cfg["混凝土"]["候选等级"])

    wb = Workbook()

    # 1 说明
    ws = wb.active
    ws.title = "1-说明"
    ws.column_dimensions["A"].width = 20
    ws.column_dimensions["B"].width = 105
    ws.cell(row=1, column=1, value="柱截面与混凝土等级优化汇报").font = TITLE
    r = 3
    g = cfg["几何"]
    rows = [
        ("优化目标", "在全部构件不超限的前提下，使柱的混凝土+模板+钢筋总造价最低"),
        ("结构模型", "%d 层框架，%d跨×%d跨，每跨 %dm×%dm，层高 %.2fm，总高 %.1fm"
                     % (nf, g["跨数X"], g["跨数Y"], g["跨度X"] // 1000, g["跨度Y"] // 1000,
                        g["层高"] / 1000, nf * g["层高"] / 1000)),
        ("构件", "柱：优化对象；梁 %d×%d、板 %dmm（保持不变）"
                 % (cfg["梁"]["宽"], cfg["梁"]["高"], cfg["板"]["厚"])),
        ("优化变量", "① 每层 × 每个柱位分组的柱截面边长\n② 每层的混凝土强度等级（层内统一）"),
        ("单 价", "混凝土：%s；模板 %.0f 元/m²；钢筋 %.0f 元/t"
                  % ("、".join("%s %.0f 元/m³" % (k, v)
                              for k, v in cfg["混凝土"]["单价元每m3"].items()),
                     cfg["造价"]["模板单价元每m2"], cfg["造价"]["钢筋单价元每t"])),
        ("造价口径", cfg["造价"].get("口径", "只算柱")),
        ("钢筋取数", "纵筋 = wpj 四边计算配筋之和的最大值（不低于构造最小配筋率 %.2f%%）；"
                     "箍筋 = Rsv × 核心区面积 × 柱段长。"
                     % (cfg["造价"]["纵筋最小配筋率"] * 100)),
        ("约束条件", "轴压比 Uc ≤ %.2f（选型取目标 %.2f 留余量）；边长 ≥ %dmm；"
                     "其余按规范由 YJK 自检（超限/位移角等）"
                     % (cfg["抗震"]["轴压比限值"], cfg["抗震"]["轴压比目标"],
                        cfg["截面"]["最小边长"])),
        ("优化过程", "每轮：按(截面,等级)重建模型 → 导入 YJK → 前处理+全部计算 → 查超限 → "
                     "由配筋数据算造价；选型用上一轮实算轴力解析求解，再实算复核（不动点收敛）"),
        ("结论", "共 %d 轮。最终方案：%s" % (len(iters), grade_seq(final["sections"]))),
    ]
    for k, v in rows:
        c1 = ws.cell(row=r, column=1, value=k)
        c1.font = Font(bold=True)
        c1.fill, c1.border = SUB_FILL, BORDER
        c1.alignment = Alignment(vertical="top")
        c2 = ws.cell(row=r, column=2, value=v)
        c2.alignment = Alignment(vertical="top", wrap_text=True)
        c2.border = BORDER
        ws.row_dimensions[r].height = max(18, 15 * (v.count("\n") + 1))
        r += 1

    # 4 柱明细（先建，供 2/3 引用）
    ws4 = wb.create_sheet("4-柱明细")
    ws4.cell(row=1, column=1, value="各轮每根柱的设计结果与造价（造价列＝按等级查表×单价）").font = TITLE
    head(ws4, 3, ["轮次", "结构层", "柱号", "分组", "等级", "截面(mm)", "轴压比 Uc",
                  "纵筋率%", "纵筋 t", "箍筋 t", "混凝土 m³", "模板 m²",
                  "混凝土费", "模板费", "纵筋费", "箍筋费", "小计"],
         [12, 8, 7, 7, 7, 11, 10, 9, 9, 9, 10, 9, 10, 9, 9, 9, 10])
    r4 = 4
    for it in iters:
        for x in it["明细"]:
            r4 = put(ws4, r4, [it["tag"], x["floor"], "N%d" % x["nc"], x["group"],
                               x.get("grade") or "?", "%d×%d" % (x["B"], x["H"]),
                               round(x["Uc"] or 0, 3), round(x["纵筋率%"] or 0, 2),
                               round(x["纵筋量t"], 4), round(x["箍筋量t"], 4),
                               round(x["混凝土量m3"], 4), round(x["模板量m2"], 3),
                               "=VLOOKUP(E%d,'6-单价与假定'!$A$4:$B$%d,2,0)*K%d" % (r4, 3 + len(grades), r4),
                               "='6-单价与假定'!$B$%d*L%d" % (4 + len(grades), r4),
                               "='6-单价与假定'!$B$%d*I%d" % (5 + len(grades), r4),
                               "='6-单价与假定'!$B$%d*J%d" % (5 + len(grades), r4),
                               "=SUM(M%d:P%d)" % (r4, r4)],
                     fmts=[None] * 12 + [MONEY, MONEY, MONEY, MONEY, MONEY])
    ws4.freeze_panes = "A4"

    # 2 迭代汇总
    ws2 = wb.create_sheet("2-迭代汇总", 1)
    ws2.cell(row=1, column=1, value="各轮迭代对比（造价列汇总自「4-柱明细」）").font = TITLE
    head(ws2, 3, ["轮次", "混凝土等级分布", "截面方案", "超限条数", "是否可行",
                  "混凝土 m³", "模板 m²", "纵筋 t", "箍筋 t",
                  "混凝土费", "模板费", "纵筋费", "箍筋费", "合计造价"],
         [12, 26, 46, 9, 9, 10, 9, 9, 9, 10, 10, 10, 10, 12])
    r = 4
    for it in iters:
        t, feasible = it["造价"], it["超限条数"] == 0
        rng = "'4-柱明细'!$A$4:$A$%d" % (r4 - 1)
        vals = [it["tag"], grade_seq(it["sections"]), sec_seq(it["sections"], groups),
                it["超限条数"], "可行" if feasible else "不可行",
                t.get("混凝土量m3"), t.get("模板量m2"), t.get("纵筋量t"), t.get("箍筋量t")]
        put(ws2, r, vals, fmts=[None, None, None, None, None, NUM3, NUM2, NUM3, NUM3])
        for c, col in ((10, "M"), (11, "N"), (12, "O"), (13, "P")):
            ws2.cell(row=r, column=c,
                     value="=SUMIF(%s,$A%d,'4-柱明细'!$%s$4:$%s$%d)"
                           % (rng, r, col, col, r4 - 1)).number_format = MONEY
        cell = ws2.cell(row=r, column=14, value="=SUM(J%d:M%d)" % (r, r))
        cell.number_format, cell.font = MONEY, Font(bold=True)
        ws2.cell(row=r, column=5).fill = OK if feasible else BAD
        if not feasible:
            ws2.cell(row=r, column=4).fill = BAD
        for c in range(1, 15):
            ws2.cell(row=r, column=c).border = BORDER
        ws2.row_dimensions[r].height = 30
        r += 1

    # 3 最终方案
    ws3 = wb.create_sheet("3-最终方案", 2)
    ws3.cell(row=1, column=1, value="推荐方案：按结构层 × 柱位分组").font = TITLE
    head(ws3, 3, ["结构层", "柱位分组", "混凝土等级", "截面(mm)", "根数", "轴压比 Uc 最大",
                  "纵筋率 最大%", "纵筋 t", "箍筋 t", "混凝土 m³", "模板 m²",
                  "混凝土费", "模板费", "纵筋费", "箍筋费", "小计"],
         [8, 9, 10, 11, 6, 12, 10, 9, 9, 10, 9, 10, 10, 10, 10, 11])
    agg = {}
    for x in final["明细"]:
        k = (x["floor"], x["group"])
        z = agg.setdefault(k, {"n": 0, "Uc": 0.0, "rho": 0.0, "long": 0.0, "stir": 0.0,
                               "con": 0.0, "form": 0.0, "sec": set(), "grade": set()})
        z["n"] += 1
        z["Uc"] = max(z["Uc"], x["Uc"] or 0)
        z["rho"] = max(z["rho"], x["纵筋率%"] or 0)
        for key, src in (("long", "纵筋量t"), ("stir", "箍筋量t"),
                         ("con", "混凝土量m3"), ("form", "模板量m2")):
            z[key] += x[src]
        z["sec"].add("%d×%d" % (x["B"], x["H"]))
        z["grade"].add(x.get("grade") or "?")
    r = 4
    for k in sorted(agg):
        z = agg[k]
        put(ws3, r, [k[0], k[1], "/".join(sorted(z["grade"])), "/".join(sorted(z["sec"])),
                     z["n"], round(z["Uc"], 3), round(z["rho"], 2), z["long"], z["stir"],
                     z["con"], z["form"],
                     "=VLOOKUP($C%d,'6-单价与假定'!$A$4:$B$%d,2,0)*J%d" % (r, 3 + len(grades), r),
                     "='6-单价与假定'!$B$%d*K%d" % (4 + len(grades), r),
                     "='6-单价与假定'!$B$%d*H%d" % (5 + len(grades), r),
                     "='6-单价与假定'!$B$%d*I%d" % (5 + len(grades), r),
                     "=SUM(L%d:O%d)" % (r, r)],
            fmts=[None, None, None, None, None, NUM2, NUM2, NUM3, NUM3, NUM3, NUM2,
                  MONEY, MONEY, MONEY, MONEY, MONEY])
        r += 1
    last = r - 1
    put(ws3, r, ["合计", "", "", "", "=SUM(E4:E%d)" % last, "", "",
                 "=SUM(H4:H%d)" % last, "=SUM(I4:I%d)" % last, "=SUM(J4:J%d)" % last,
                 "=SUM(K4:K%d)" % last, "=SUM(L4:L%d)" % last, "=SUM(M4:M%d)" % last,
                 "=SUM(N4:N%d)" % last, "=SUM(O4:O%d)" % last, "=SUM(P4:P%d)" % last],
        fmts=[None] * 7 + [NUM3, NUM3, NUM3, NUM2, MONEY, MONEY, MONEY, MONEY, MONEY])
    for c in range(1, 17):
        ws3.cell(row=r, column=c).font = Font(bold=True)
        ws3.cell(row=r, column=c).fill = SUB_FILL

    # 5 超限明细
    ws5 = wb.create_sheet("5-超限明细")
    ws5.cell(row=1, column=1, value="各轮超限记录").font = TITLE
    head(ws5, 3, ["轮次", "结构层", "超限内容"], [14, 9, 90])
    r = 4
    for it in iters:
        if not it["超限明细"]:
            r = put(ws5, r, [it["tag"], "-", "无超限"])
        else:
            for f, txt in it["超限明细"]:
                r = put(ws5, r, [it["tag"], f, txt])
                ws5.cell(row=r - 1, column=3).fill = BAD

    # 6 单价与假定
    ws6 = wb.create_sheet("6-单价与假定")
    ws6.cell(row=1, column=1, value="单价与假定（只改 B 列，其它表自动重算）").font = TITLE
    head(ws6, 3, ["项目", "单价/数值", "单位", "说明"], [16, 12, 12, 60])
    r = 4
    items = [(gr, cfg["混凝土"]["单价元每m3"].get(gr, 0), "元/m³",
              "混凝土按等级取价，名称须与明细表等级列一致") for gr in grades]
    items += [("模板", cfg["造价"]["模板单价元每m2"], "元/m²", "柱侧模，按周长×柱段长计"),
              ("钢筋", cfg["造价"]["钢筋单价元每t"], "元/t", "纵筋与箍筋同价"),
              ("钢筋密度", cfg["造价"]["钢筋密度kg每m3"], "kg/m³", "用量换算"),
              ("纵筋最小配筋率", cfg["造价"]["纵筋最小配筋率"], "-", "构造下限")]
    for name, val, unit, note in items:
        r = put(ws6, r, [name, val, unit, note],
                fmts=[None, NUM3 if "率" in name else NUM2, None, None])
        c = ws6.cell(row=r - 1, column=2)
        c.fill, c.font = EDIT, Font(bold=True)
    ws6.cell(row=r + 1, column=1,
             value="造价列均引用本表，改价即全表联动（打开时自动重算）。").font = Font(italic=True)

    wb.calculation.fullCalcOnLoad = True
    wb.save(a.out)
    print("已生成汇报：%s（%d 轮，%d 层）" % (a.out, len(iters), nf))
    return 0


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
    sys.exit(main())
