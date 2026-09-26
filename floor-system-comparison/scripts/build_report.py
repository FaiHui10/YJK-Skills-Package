# -*- coding: utf-8 -*-
r"""读 `out/quantities.json` + `scripts/quota_gd.py`，按**广东省2018定额 + 广州市
2026年6月信息价**计价，输出多页 Excel 经济对比报告。

用法:
    python build_report.py                      # 缺省输出 out/裙楼楼盖次梁布置比选经济对比报告.xlsx
    python build_report.py --out xxx.xlsx
"""
import argparse
import glob
import json
import os
import sqlite3
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
import quota_gd as Q                                               # noqa: E402
from openpyxl import Workbook                                      # noqa: E402
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side  # noqa: E402
from openpyxl.utils import get_column_letter                       # noqa: E402

SCHEMES = ["S0", "S1", "S2", "S3", "S4"]
COL = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O"]

# 本文件收集到的**判定失败**项：出报告的同时给非零退出码。
# 老版本第 9 页是一堆写死的"已通过"，退出码恒 0 —— 屏幕/报告上写着结论、
# 调用方却只看得到 0，等于把没核对过的东西当核对过了交出去。
PROBLEMS = []


def flag(msg):
    """记一条判定为假/无法核对的项（会进退出码，也会打印在末尾）。"""
    PROBLEMS.append(msg)
    return msg

# ------------------------------------------------------------------ 样式
F_TITLE = Font(name="微软雅黑", size=15, bold=True, color="FF1F3864")
F_H1 = Font(name="微软雅黑", size=11, bold=True, color="FFFFFFFF")
F_H2 = Font(name="微软雅黑", size=10, bold=True, color="FF1F3864")
F_TXT = Font(name="微软雅黑", size=10)
F_BOLD = Font(name="微软雅黑", size=10, bold=True)
F_NOTE = Font(name="微软雅黑", size=9, color="FF595959")
FILL_H = PatternFill("solid", fgColor="FF2E5C8A")
FILL_H2 = PatternFill("solid", fgColor="FFDCE6F1")
FILL_HL = PatternFill("solid", fgColor="FFFFF2CC")
FILL_BEST = PatternFill("solid", fgColor="FFD9EAD3")
THIN = Side(style="thin", color="FFB4C6E7")
BORD = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
CEN = Alignment(horizontal="center", vertical="center", wrap_text=True)
LEFT = Alignment(horizontal="left", vertical="center", wrap_text=True)
RIGHT = Alignment(horizontal="right", vertical="center")

N0 = "#,##0"
N1 = "#,##0.0"
N2 = "#,##0.00"
N3 = "#,##0.000"
PCT = "0.0%"


def head(ws, row, vals, widths=None, fill=FILL_H, font=F_H1, h=26):
    for j, v in enumerate(vals):
        c = ws.cell(row=row, column=j + 1, value=v)
        c.font = font
        c.fill = fill
        c.alignment = CEN
        c.border = BORD
    ws.row_dimensions[row].height = h
    if widths:
        for j, w in enumerate(widths):
            ws.column_dimensions[COL[j]].width = w


def put(ws, row, vals, fmts=None, fonts=None, fill=None, h=None, aligns=None):
    for j, v in enumerate(vals):
        c = ws.cell(row=row, column=j + 1, value=v)
        c.font = (fonts[j] if fonts and fonts[j] else F_TXT)
        c.border = BORD
        c.alignment = (aligns[j] if aligns and aligns[j] else
                       (RIGHT if isinstance(v, (int, float)) else LEFT))
        if fill:
            c.fill = fill
        if fmts and fmts[j]:
            c.number_format = fmts[j]
    if h:
        ws.row_dimensions[row].height = h
    return row + 1


def title(ws, text, ncol, sub=None):
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=ncol)
    c = ws.cell(row=1, column=1, value=text)
    c.font = F_TITLE
    c.alignment = Alignment(horizontal="left", vertical="center")
    ws.row_dimensions[1].height = 30
    r = 3
    if sub:
        ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=ncol)
        c = ws.cell(row=2, column=1, value=sub)
        c.font = F_NOTE
        c.alignment = Alignment(horizontal="left", vertical="center")
    return r


# ------------------------------------------------------------------ 计价
def unit_prices(pricer):
    """返回常用综合单价字典（除税、含税）。"""
    up = {}
    up["conc_c30"] = pricer.conc_unit("A1-5-14", "C30")        # 元/m³ 有梁板
    up["conc_col_c40"] = pricer.conc_unit("A1-5-5", "C40")     # 元/m³ 柱
    up["form_25in"] = pricer.form_unit("beam", b_mm=250)       # 元/m²
    up["form_25out"] = pricer.form_unit("beam", b_mm=300)
    up["form_slab"] = pricer.form_unit("slab")
    for d in (6, 8, 10, 12, 14, 16, 18, 20, 22, 25, 28, 32):
        up["rebar_%d" % d] = pricer.rebar_unit(d)              # 元/t
    return up


def rebar_cost(d, up, up_key="rebar"):
    """按 Φ 分档综合单价算钢筋费（元）。**没拿到数据就返回 None**，不返回 0。

    ★ 老版本把这一层写成 `for k, v in (d["钢筋梁"] or {}).items()`：缺数据时
      循环走 0 次，钢筋费静默变成 0，总计里一点钢筋都没有，报告却只显示
      "钢筋 0 kg / 0 元" —— 缺数据与用量为 0 完全不可区分。
    """
    if not d:
        return None
    tot = 0.0
    for k, v in d.items():
        dd = int(float(k))
        tot += v / 1000.0 * up["%s_%d" % (up_key, dd)][0]
    return tot


def rebar_sum(d):
    """梁+板钢筋合计（kg）。任一项未取得就返回 None（不是 0）。"""
    a, b = d.get("钢筋梁合计"), d.get("钢筋板合计")
    if a is None or b is None:
        return None
    return a + b


def scheme_cost(d, up):
    """按方案工程量算造价（除税、含税），返回 dict。"""
    conc = d["砼有梁板"] * up["conc_c30"][0]
    col = d["砼柱"] * up["conc_col_c40"][0]
    fb = (d["模板梁_25内"] * up["form_25in"][0]
          + d["模板梁_25外"] * up["form_25out"][0])
    fs = d["模板板"] * up["form_slab"][0]
    rb = rebar_cost(d["钢筋梁"], up)
    rs = rebar_cost(d["钢筋板"], up)
    rc = rebar_cost(d["钢筋柱"], up)
    missing = [k for k, v in (("梁", rb), ("板", rs), ("柱", rc)) if v is None]
    net = conc + fb + fs + (rb or 0.0) + (rs or 0.0)
    return {"砼有梁板": conc, "模板梁": fb, "模板板": fs,
            "钢筋梁": rb, "钢筋板": rs, "合计": net,
            "柱砼": col, "柱钢筋": rc, "含柱合计": net + col + (rc or 0.0),
            # ★ 缺钢筋时"合计"是**不含钢筋的合计**，必须能被下游看出来
            "钢筋缺失": missing,
            "合计口径": ("未含%s钢筋（YJK 钢筋用量表没取到）" % "/".join(missing)
                     if missing else "梁板含钢筋")}


def str_d(x):
    return int(x)


def _rebar_claim(Q_):
    """第 1 页副标题里"钢筋由 YJK 实算取得"这句——**没取到就不能这么写**。

    ★ 老版本无条件写「全部配筋由盈建科 YJK 7.1.0 实算取得」，与第 2 页的「未取得」自相矛盾。
    """
    miss = [s for s in SCHEMES if rebar_sum(Q_[s]) is None]
    if miss:
        return ("★ 钢筋用量：YJK 实算——但 %s 未取到（见第 2 页「未取得」，不要当 0）"
                % "、".join(miss))
    return "全部配筋由盈建科 YJK 7.1.0 实算取得"


def _slab_area_note(Q_):
    """第 1 页第 9 条：板投影面积的**来源**必须与实际取值一致。

    ★ 老版本无条件写"模型板投影面积取模型实际值 …… 板伸至周边梁外皮，比轴网面积
      每边大约半个梁宽（300/2=150mm）"。而 collect.py 在取不到 YJK 面积表时用
      `or m["slab_area"]` 兜底成**轴网包络值**，却仍进同一个键名 —— 于是这段解释
      在描述一个并不存在的差异。
    """
    s0 = Q_["S0"]
    sa, area = s0["板面积每层_YJK"], s0["楼盖面积每层"]
    src = (s0.get("sources") or {}).get("slab_area")
    if src == "yjk":
        return ("9. 板投影面积取**模型实际值** %.2f m²/层（全楼 %.2f m²）：板伸至周边梁外皮，"
                "比轴网面积 67.2×33.6=%.2f m² 每边大约半个梁宽（300/2=150mm）；"
                "定额要求按「图示面积」，故采用模型值。"
                % (sa, s0["板面积全楼_YJK"], area))
    if src is None:
        return ("9. ★ 这份 quantities.json **没有记数据来源**（多半是旧版 collect.py 生成的）："
                "%.2f m²/层 到底是 YJK 模型实测值还是轴网包络兜底值**无法判定**。"
                "请重跑 collect.py 生成带来源标记的 JSON，再出报告。" % sa)
    why = ("results/S0/ 下缺《全楼梁钢筋用量(钢筋规格与类别).xlsx》"
           if src == "no_file" else
           "《全楼梁钢筋用量(钢筋规格与类别).xlsx》在，但里面找不到「第N层」行（原因 %s）" % src)
    return ("9. ★ 板投影面积**没取到 YJK 模型实测值**：%s，本页与第 2/7 页的板面积类指标用的是"
            "**轴网包络值** %.2f m²/层（全楼 %.2f m²，与 67.2×33.6=%.2f m² 同源，"
            "不含「板伸至梁外皮」那半个梁宽）。跑完 yjk_quant.py 取得面积表后重跑 "
            "collect.py + build_report.py 会自动改回模型实测值。"
            % (why, sa, s0["板面积全楼_YJK"], area))


def normalize_rebar(Q_):
    """把"没有钢筋数据"的**两种历史形状**统一成 `None`。

    * 新版 `collect.py` 写 `None`（"没取到"）；
    * 旧版 `collect.py` 在"表在、但表头/合计行解析不出来"时写的是 **`{}`**。
    两者含义相同（都没有数据），但 `{}` 会让 `is None` 判据漏掉 → 又渲染成 0。
    这里在入口统一成 None，并补一条来源标记（旧版 JSON 本来就没有 sources）。
    """
    key2src = {"钢筋梁": "rebar_beam", "钢筋柱": "rebar_column",
               "钢筋板": "rebar_slab"}
    for s in SCHEMES:
        d = Q_.get(s) or {}
        for k, src in key2src.items():
            if d.get(k) == {}:                     # 空表 ≠ 0 kg
                d[k] = None
                d.setdefault("sources", {})[src] = "empty_table"
    return Q_


# ------------------------------------------------------------------ 页 1
def sheet_overview(wb, Q_):
    ws = wb.create_sheet("1.方案概况")
    r = title(ws, "裙楼楼盖次梁布置方式 经济对比分析 · 方案概况", 6,
              "柱网 8.4m×8.4m（长向 8 跨 × 短向 4 跨）｜楼面均布荷载 10 kN/m²（附加恒载 5.0 + 活载 5.0）"
              "｜层高 4.80m × 3 层｜%s｜计价按广东省2018定额 + 广州市2026年6月信息价"
              % _rebar_claim(Q_))
    ws.column_dimensions["A"].width = 20
    for c in "BCDEF":
        ws.column_dimensions[c].width = 15
    r = 4
    ws.cell(row=r, column=1, value="一、工程条件").font = F_H2
    r += 1
    r = put(ws, r, ["项目", "取值", "", "项目", "取值"], fonts=[F_H2, F_H2, F_H2, F_H2, F_H2],
            fill=FILL_H2)
    cond = [
        ("柱网（长向×短向）", "8.4 m × 8.4 m", "楼面均布荷载", "10 kN/m²（附加恒载 5.0 + 活载 5.0）"),
        ("柱网跨数", "长向 8 跨 × 短向 4 跨", "楼盖平面尺寸", "67.2 m × 33.6 m"),
        ("楼盖面积（每层）", "%.2f m²" % Q_["S0"]["楼盖面积每层"], "层高", "4.80 m"),
        ("楼盖面积（全楼）", "%.2f m²" % Q_["S0"]["楼盖面积全楼"], "层数", "3 层"),
        ("模型板投影面积（每层）", "%.2f m²" % Q_["S0"]["板面积每层_YJK"], "模型板投影面积（全楼）",
         "%.2f m²" % Q_["S0"]["板面积全楼_YJK"]),
        ("计算程序", "盈建科 YJK 7.1.0（建模→数检→整体计算→板配筋）", "砼/钢筋", "梁板 C30；柱 C40；HRB400"),
        ("造价依据", "《广东省房屋建筑与装饰工程综合定额(2018)》", "信息价", "穗建造价〔2026〕62 号（2026年6月）"),
    ]
    for k1, v1, k2, v2 in cond:
        r = put(ws, r, [k1, v1, "", k2, v2], None, [F_BOLD, None, None, F_BOLD, None])
    r += 1
    ws.cell(row=r, column=1, value="二、比选方案与构件截面").font = F_H2
    r += 1
    r = put(ws, r, ["方案", "名称", "主梁截面(mm)", "次梁截面(mm)", "板厚(mm)", "次梁布置做法"],
            None, fill=FILL_H2)
    ws.cell(row=r - 1, column=1).font = F_H2
    for s in SCHEMES:
        d = Q_[s]
        r = put(ws, r, [s, d["info"]["name"], d["info"]["主梁"], d["info"]["次梁"],
                        d["info"]["板厚"], d["info"]["做法"]])
    r += 1
    ws.cell(row=r, column=1, value="三、口径说明").font = F_H2
    r += 1
    for t in [
        "1. 比选范围＝**楼盖（梁 + 板）**。柱在各方案中柱网、荷载与截面相同（700×700，C40），"
        "故单列作参考，不计入比选合计。",
        "2. 混凝土按定额「有梁板（包括主、次梁与板）按梁、板体积之和计算」（上册 p.250 第10条）合并为 A1-5-14 一个子目。",
        "3. 模板为 YJK 不提供的项目，按定额下册 p.49 计算规则自算：梁模板=〔2×(梁高−板厚)+梁宽〕×梁净长；"
        "板模板=楼盖投影面积−梁底占面积−柱占面积（第⑤条）。",
        "4. 梁净长按定额：梁与柱连接算至柱内侧面；次梁算至主梁内侧面。",
        "5. 支模高度按「楼层高度」（下册 p.45 说明五）=4.80m > 3.6m，故梁、板各按「3.6m 子目 + 2×每增1m 子目」计。",
        "6. 钢筋用量取自 YJK「工程量统计」模块输出的《全楼梁/柱/板钢筋用量(钢筋规格与类别)》，按 HRB400 规格分档。"
        + ("" if rebar_sum(Q_["S0"]) is not None else
           " ★ 但 %s 的该表**没取到**（第 2/7/10 页显示「未取得」，不是 0 kg）"
           % "、".join(s for s in SCHEMES if rebar_sum(Q_[s]) is None)),
        "7. 综合单价＝定额基价 + 利润[(人工+机具)×20%] + 主材信息价（替换定额内被替换主材）；管理费已含在定额基价内；增值税 9%。",
        "8. 混凝土按泵送预拌混凝土，含损耗 1.0%（定额消耗量 10.100 m³/10m³）。",
        _slab_area_note(Q_),
    ]:
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=6)
        c = ws.cell(row=r, column=1, value=t)
        c.font = F_TXT
        c.alignment = LEFT
        ws.row_dimensions[r].height = 16
        r += 1
    return ws


# ------------------------------------------------------------------ 页 2
def sheet_qty(wb, Q_):
    ws = wb.create_sheet("2.工程量对比")
    r = title(ws, "二、工程量对比（全楼 3 层，YJK 实算 + 定额计算规则）", 7)
    ws.column_dimensions["A"].width = 30
    for c in "BCDEFG":
        ws.column_dimensions[c].width = 14
    r = 4
    r = put(ws, r, ["项目", "单位"] + SCHEMES,
            fonts=[F_H2] * 7, fill=FILL_H2)
    hdr = r - 1
    def block(name, rows, fmt=N3):
        nonlocal r
        ws.cell(row=r, column=1, value=name).font = F_H2
        r += 1
        for label, unit, f, _ in rows:
            vals = [label, unit] + [f(Q_[s]) for s in SCHEMES]
            r = put(ws, r, vals, [None, None] + [fmt] * 5)
        return r

    def g(k):
        return lambda d: d[k]

    def miss(k):
        """该方案这一项没取到 -> 显示「未取得」；取到了就显示数值。

        ★ 老版本这里写 `or 0`：缺数据被渲染成 0，"梁板钢筋合计 0 kg" 与真实的
          "这批梁板没有钢筋" 长得一模一样，方案排名也照样出。
        """
        return lambda d: ("未取得" if d.get(k) is None else d[k])

    def ratio(num_key, den_key):
        """单方指标：分母在、分子缺时返回「未取得」，绝不返回 0。"""
        def f(d):
            if d.get(num_key) is None:
                return "未取得"
            return d[num_key] / d[den_key]
        return f

    r = block("混凝土（m³）", [
        ("梁体积", "m³", g("砼梁"), None),
        ("板体积", "m³", g("砼板"), None),
        ("有梁板合计（A1-5-14 口径）", "m³", g("砼有梁板"), None),
        ("柱（参考，不计入比选）", "m³", g("砼柱"), None),
    ], N2)
    r = block("模板（m²，接触面积）", [
        ("梁模板（梁宽25cm以内）", "m²", g("模板梁_25内"), None),
        ("梁模板（梁宽25cm以外）", "m²", g("模板梁_25外"), None),
        ("梁模板小计", "m²", g("模板梁"), None),
        ("板模板", "m²", g("模板板"), None),
        ("模板合计", "m²", g("模板合计"), None),
    ], N1)
    r = block("钢筋（kg，YJK 实算）", [
        ("梁钢筋", "kg", miss("钢筋梁合计"), None),
        ("板钢筋", "kg", miss("钢筋板合计"), None),
        ("梁板钢筋合计", "kg", lambda d: ("未取得" if rebar_sum(d) is None
                                     else rebar_sum(d)), None),
        ("柱钢筋（参考）", "kg", miss("钢筋柱合计"), None),
    ], N0)
    r = block("单位指标（按楼盖面积 %.0f m² 全楼）" % Q_["S0"]["楼盖面积全楼"], [
        ("混凝土（有梁板）", "m³/m²", lambda d: d["砼有梁板"] / d["楼盖面积全楼"], None),
        ("模板", "m²/m²", lambda d: d["模板合计"] / d["楼盖面积全楼"], None),
        ("梁板钢筋含量", "kg/m²", lambda d: ("未取得" if rebar_sum(d) is None
                                       else rebar_sum(d) / d["楼盖面积全楼"]), None),
        ("板钢筋含量", "kg/m²", ratio("钢筋板合计", "楼盖面积全楼"), None),
    ], "0.0000")
    r += 1
    ws.cell(row=r, column=1, value="注：柱工程量与配筋各方案基本相同，仅作参考，不参与比选。").font = F_NOTE
    r += 1
    miss_schemes = [s for s in SCHEMES if rebar_sum(Q_[s]) is None]
    if miss_schemes:
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=7)
        ws.cell(row=r, column=1, value="★ 钢筋行显示「未取得」= YJK 钢筋用量表没取到，"
                                       "**不是 0 kg**：%s。缺钢筋时下面各页的造价合计"
                                       "都不含钢筋，方案之间不可直接比价。"
                % "、".join(miss_schemes)).font = F_NOTE
        ws.cell(row=r, column=1).alignment = LEFT
    return ws


# ------------------------------------------------------------------ 页 3
def sheet_unit(wb, up, pricer):
    ws = wb.create_sheet("3.综合单价分析")
    r = title(ws, "三、综合单价分析（除税，元/计价单位）", 8,
              "综合单价 = 定额基价 + 利润[(人工+机具)×20%] + 信息价主材；管理费已含于定额基价内；增值税 9%")
    ws.column_dimensions["A"].width = 12
    ws.column_dimensions["B"].width = 42
    for c in "CDEFGH":
        ws.column_dimensions[c].width = 13
    r = 4
    r = put(ws, r, ["定额编号", "子目名称", "单位", "定额基价", "利润", "主材信息价",
                    "综合单价(除税)", "综合单价(含税)"], fill=FILL_H2)
    for c in range(1, 9):
        ws.cell(row=r - 1, column=c).font = F_H2

    n, t, de = up["conc_c30"]
    r = put(ws, r, ["A1-5-14", "现浇混凝土 平板、有梁板、无梁板（C30 泵送）", "m³",
                    de["定额基价/10"], round(de["利润"], 2), round(de["混凝土"], 2),
                    round(n, 2), round(t, 2)])
    n2, t2, de2 = up["conc_col_c40"]
    r = put(ws, r, ["A1-5-5", "现浇混凝土 矩形柱（C40 泵送，参考）", "m³",
                    de2["定额基价/10"], round(de2["利润"], 2), round(de2["混凝土"], 2),
                    round(n2, 2), round(t2, 2)])
    for key, code, label in [("form_25in", "A1-20-33", "单梁、连续梁模板 梁宽25cm以内 支模3.6m"),
                             ("form_25out", "A1-20-34", "单梁、连续梁模板 梁宽25cm以外 支模3.6m"),
                             ("form_slab", "A1-20-75", "有梁板模板 支模3.6m")]:
        n_, t_, de_ = up[key]
        r = put(ws, r, [code, label + "（含超高 %d 次）" % de_["超高次数"], "m²",
                        round(de_["基价"], 2),
                        round(de_["利润"] + de_.get("超高利润", 0), 2), "—",
                        round(n_, 2), round(t_, 2)])
    for d in (8, 10, 12, 14, 16, 18, 20, 22, 25, 28, 32):
        n_, t_, de_ = up["rebar_%d" % d]
        r = put(ws, r, [de_["定额"], "现浇构件带肋钢筋 Φ%d（%s HRB400E）" % (d, de_["信息价类别"]),
                        "t", Q.QUOTA[de_["定额"]][2], round(de_["利润"], 2),
                        round(de_["钢筋材料"], 2), round(n_, 2), round(t_, 2)])
    r += 1
    ws.cell(row=r, column=1, value="取费与价格来源").font = F_H2
    r += 1
    for t in ["管理费率：混凝土及钢筋混凝土 28.75%、模板 26.35%（已含于定额基价）",
              "利润：定额人工费与施工机具费之和 × 20%（附录四）",
              "增值税：综合单价 × 9%",
              "混凝土：泵送预拌砼税前综合价 C30 382.5 元/m³、C40 416.5 元/m³（穗建造价〔2026〕62 号）",
              "钢筋：HRB400E Φ10内 3168 / Φ10外 3143 / Φ12-25 3089 / Φ25外 3147 元/t",
              "人工费价格指数 109.13%（敏感性分析用）"]:
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=8)
        c = ws.cell(row=r, column=1, value="· " + t)
        c.font = F_NOTE
        c.alignment = LEFT
        r += 1
    return ws


# ------------------------------------------------------------------ 页 4
def sheet_cost(wb, Q_, costs, costs_ki):
    ws = wb.create_sheet("4.造价对比")
    r = title(ws, "四、造价对比（全楼 3 层，除税口径）", 8,
              "比选范围＝楼盖（梁+板）；柱单列参考。含税价＝除税×1.09")
    ws.column_dimensions["A"].width = 26
    ws.column_dimensions["B"].width = 9
    for c in "CDEFG":
        ws.column_dimensions[c].width = 15
    ws.column_dimensions["H"].width = 13
    r = 4
    r = put(ws, r, ["分项", "单位"] + SCHEMES + ["S0 基准=100"],
            fill=FILL_H2)
    for c in range(1, 9):
        ws.cell(row=r - 1, column=c).font = F_H2
    ws.cell(row=r - 1, column=8).alignment = CEN

    def line(label, unit, f, fmt=N0, hl=False):
        """一行分项。缺数据的方案显示「未取得」而不是 0（0 会被读成"这项不花钱"）。

        ★ 最后一列「S0 基准=100」比的是 S0 与 S4 的**比值**：任一侧缺数据就必须写「未取得」
          —— 直接除会 `TypeError: NoneType / float`，整份报告生不出来
          （实测：S0 有钢筋、S4 缺钢筋时，报告直接崩）。基准为 0 时也不做除法。
        """
        nonlocal r
        v0, v4 = f(costs["S0"]), f(costs["S4"])
        vals = [label, unit] + [("未取得" if f(costs[s]) is None else round(f(costs[s]), 2))
                                for s in SCHEMES]
        if v0 is None or v4 is None:
            vals.append("未取得")
        elif not v0:
            vals.append(0)
        else:
            vals.append(v4 / v0)
        r = put(ws, r, vals[:8], [None, None] + [fmt] * 5 + [fmt], fill=FILL_HL if hl else None)
        return r

    for lab, key in [("混凝土（有梁板）", "砼有梁板"), ("模板（梁）", "模板梁"),
                     ("模板（板）", "模板板"), ("钢筋（梁）", "钢筋梁"),
                     ("钢筋（板）", "钢筋板")]:
        line(lab, "元", lambda c, k=key: c[k])
    line("楼盖造价合计（梁+板）", "元", lambda c: c["合计"], N0, hl=True)
    line("单方造价（按楼盖面积）", "元/m²",
         lambda c: c["合计"] / Q_["S0"]["楼盖面积全楼"], N2, hl=True)
    line("相对造价指数", "—", lambda c: c["合计"] / costs["S0"]["合计"] * 100.0, N1)
    r += 1
    ws.cell(row=r, column=1, value="参考：含柱口径").font = F_H2
    r += 1
    line("柱混凝土造价", "元", lambda c: c["柱砼"])
    line("柱钢筋造价", "元", lambda c: c["柱钢筋"])
    line("全楼合计（含柱）", "元", lambda c: c["含柱合计"], N0, hl=True)
    r += 1
    ws.cell(row=r, column=1, value="（含税口径，元）").font = F_H2
    r += 1
    for lab, key in [("楼盖造价合计（含税）", "合计"), ("全楼合计（含税）", "含柱合计")]:
        vals = [lab, "元"] + [round(costs[s][key] * 1.09, 2) for s in SCHEMES]
        r = put(ws, r, vals[:7], [None, None] + [N0] * 5)
    r += 1
    ws.cell(row=r, column=1, value="注：各方案柱的柱网、荷载与截面相同，柱仅作参考，不参与比选排序。").font = F_NOTE
    r += 1
    bad = [(s, costs[s]["钢筋缺失"]) for s in SCHEMES if costs[s]["钢筋缺失"]]
    if bad:
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=8)
        c = ws.cell(row=r, column=1, value="★ 下列方案的 YJK 钢筋用量表没取到（%s）："
                                           "「钢筋」分项与「楼盖造价合计」**不含钢筋**，"
                                           "与其它方案不可直接比价，排名仅供参考。"
                    % "；".join("%s 缺%s" % (s, "/".join(m)) for s, m in bad))
        c.font = F_NOTE
        c.alignment = LEFT
        r += 1
    ws.cell(row=r, column=1, value="敏感性：人工费按广州市人工费价格指数 109.13% 调整后，"
                                   "楼盖造价合计（除税，元）：").font = F_H2
    r += 1
    vals = ["人工×109.13%", "元"] + [round(costs_ki[s]["合计"], 2) for s in SCHEMES]
    r = put(ws, r, vals[:7], [None, None] + [N0] * 5)
    vals = ["相对指数（人工×109.13%）", "—"] + \
           [round(costs_ki[s]["合计"] / costs_ki["S0"]["合计"] * 100, 1) for s in SCHEMES]
    r = put(ws, r, vals[:7], [None, None] + [N1] * 5)
    return ws


# ------------------------------------------------------------------ 页 5
def sheet_detail(wb, Q_, costs, up):
    ws = wb.create_sheet("5.造价明细")
    r = title(ws, "五、分方案造价明细（除税）", 8)
    ws.column_dimensions["A"].width = 26
    for c in "BCDEFGH":
        ws.column_dimensions[c].width = 15
    for s in SCHEMES:
        d = Q_[s]
        c = costs[s]
        r += 1
        ws.cell(row=r, column=1,
                value="%s  %s" % (s, d["info"]["name"])).font = F_H2
        r += 1
        r = put(ws, r, ["分项", "工程量", "单位", "定额编号", "综合单价(除税)",
                        "合价(除税)", "增值税", "合价(含税)"], fill=FILL_H2)
        for cc in range(1, 9):
            ws.cell(row=r - 1, column=cc).font = F_H2

        def ln(label, qty, unit, code, rate, cost):
            nonlocal r
            if cost is None:                       # 缺数据：绝不写 0（0 = "这项不花钱"）
                r = put(ws, r, [label, qty, unit, code, rate, "未取得", "未取得", "未取得"])
                return
            r = put(ws, r, [label, qty, unit, code, rate, cost, cost * Q.VAT, cost * (1 + Q.VAT)],
                    [None, N3, None, None, N2, N2, N2, N2])
        ln("混凝土 有梁板", d["砼有梁板"], "m³", "A1-5-14", up["conc_c30"][0], c["砼有梁板"])
        ln("模板 梁（25cm以内）", d["模板梁_25内"], "m²", "A1-20-33",
           up["form_25in"][0], d["模板梁_25内"] * up["form_25in"][0])
        ln("模板 梁（25cm以外）", d["模板梁_25外"], "m²", "A1-20-34",
           up["form_25out"][0], d["模板梁_25外"] * up["form_25out"][0])
        ln("模板 板（有梁板）", d["模板板"], "m²", "A1-20-75",
           up["form_slab"][0], c["模板板"])
        # ★ 缺钢筋时明细里要留一行说明，否则"没有钢筋行"读起来像"这个方案没有钢筋"。
        if d["钢筋梁"] is None:
            ln("钢筋 梁（未取得 YJK 钢筋用量表）", "", "", "", "", None)
        for k, v in sorted((d["钢筋梁"] or {}).items(), key=lambda kv: float(kv[0])):
            dd = int(float(k))
            ln("钢筋 梁 Φ%d" % dd, v / 1000.0, "t",
               up["rebar_%d" % dd][2]["定额"], up["rebar_%d" % dd][0],
               v / 1000.0 * up["rebar_%d" % dd][0])
        if d["钢筋板"] is None:
            ln("钢筋 板（未取得 YJK 钢筋用量表）", "", "", "", "", None)
        for k, v in sorted((d["钢筋板"] or {}).items(), key=lambda kv: float(kv[0])):
            dd = int(float(k))
            ln("钢筋 板 Φ%d" % dd, v / 1000.0, "t",
               up["rebar_%d" % dd][2]["定额"], up["rebar_%d" % dd][0],
               v / 1000.0 * up["rebar_%d" % dd][0])
        r = put(ws, r, ["楼盖合计" + ("（不含钢筋）" if c["钢筋缺失"] else ""), "", "", "", "",
                        round(c["合计"], 2),
                        round(c["合计"] * Q.VAT, 2), round(c["合计"] * (1 + Q.VAT), 2)],
                fonts=[F_BOLD] * 8, fill=FILL_HL)
        r = put(ws, r, ["柱（参考）", d["砼柱"], "m³", "A1-5-5", up["conc_col_c40"][0],
                        (("未取得" if c["柱钢筋"] is None
                          else round(c["柱砼"] + c["柱钢筋"], 2))), "", ""], [None] * 8)
    return ws


# ------------------------------------------------------------------ 页 6
def sheet_beamcalc(wb, Q_):
    ws = wb.create_sheet("6.计算书-梁")
    r = title(ws, "六、计算书 · 梁工程量（全楼 3 层）", 8,
              "净长规则：梁与柱连接算至柱内侧面；次梁算至主梁内侧面；主梁贯通次梁不扣（上册 p.250）")
    for c, w in zip("ABCDEFGH", [10, 14, 8, 13, 13, 13, 13, 13]):
        ws.column_dimensions[c].width = w
    for s in SCHEMES:
        r += 1
        ws.cell(row=r, column=1, value="%s  %s" % (s, Q_[s]["info"]["name"])).font = F_H2
        r += 1
        r = put(ws, r, ["截面(mm)", "类型", "段数", "轴线长(m)", "净长(m)",
                        "体积(m³)", "模板(m²)", "梁宽档"], fill=FILL_H2)
        for cc in range(1, 9):
            ws.cell(row=r - 1, column=cc).font = F_H2
        for b in Q_[s]["梁明细"]:
            r = put(ws, r, [b["截面"], b["类型"], b["段数"], round(b["轴线长"], 2),
                            round(b["净长"], 2), round(b["体积"], 3),
                            round(b["模板"], 2), b["梁宽档"]],
                    [None, None, N0, N2, N2, N3, N2, None])
        d = Q_[s]
        r = put(ws, r, ["合计", "", d["梁段数"], "", "", round(d["砼梁"], 3),
                        round(d["模板梁"], 2), ""], fonts=[F_BOLD] * 8, fill=FILL_HL)
    return ws


# ------------------------------------------------------------------ 页 7
def sheet_mat(wb, Q_):
    ws = wb.create_sheet("7.材料用量指标")
    r = title(ws, "七、材料用量与单方指标", 7)
    ws.column_dimensions["A"].width = 30
    for c in "BCDEFG":
        ws.column_dimensions[c].width = 14
    r = 4
    r = put(ws, r, ["指标", "单位"] + SCHEMES, fill=FILL_H2)
    for cc in range(1, 8):
        ws.cell(row=r - 1, column=cc).font = F_H2

    def ln(label, unit, f, fmt=N2):
        """一行指标。缺数据的方案填「未取得」（老版本是 `or 0` -> 直接写 0）。"""
        nonlocal r
        vals = []
        for s in SCHEMES:
            v = f(Q_[s])
            vals.append("未取得" if v is None else round(v, 4))
        r = put(ws, r, [label, unit] + vals, [None, None] + [fmt] * 5)

    def nz(v, div=None):
        """v 缺 -> None（不是 0）；给了 div 就返回比值。"""
        if v is None:
            return None
        return v if div is None else v / div

    A = lambda d: d["楼盖面积全楼"]
    ln("混凝土（有梁板）总量", "m³", lambda d: d["砼有梁板"], N2)
    ln("混凝土单方", "m³/m²", lambda d: d["砼有梁板"] / A(d), "0.0000")
    ln("模板总量", "m²", lambda d: d["模板合计"], N1)
    ln("模板单方", "m²/m²", lambda d: d["模板合计"] / A(d), "0.0000")
    ln("钢筋总量（梁板）", "kg", rebar_sum, N0)
    ln("钢筋含量（梁板）", "kg/m²", lambda d: nz(rebar_sum(d), A(d)), N2)
    ln("  其中：梁钢筋含量", "kg/m²", lambda d: nz(d["钢筋梁合计"], A(d)), N2)
    ln("  其中：板钢筋含量", "kg/m²", lambda d: nz(d["钢筋板合计"], A(d)), N2)
    ln("混凝土含钢量（梁板）", "kg/m³",
       lambda d: nz(rebar_sum(d), d["砼有梁板"]), N1)
    r += 1
    ws.cell(row=r, column=1,
            value="钢筋按规格明细（梁/板，kg，全楼 3 层，YJK 实算）").font = F_H2
    r += 1
    dias = sorted({int(float(k)) for s in SCHEMES
                   for k in list((Q_[s]["钢筋梁"] or {}).keys()) +
                   list((Q_[s]["钢筋板"] or {}).keys())})
    r = put(ws, r, ["钢筋规格", "部位"] + SCHEMES,
            fonts=[F_H2] * (2 + len(SCHEMES)), fill=FILL_H2)
    for d_ in dias:
        for part in ("钢筋梁", "钢筋板"):
            vals = ["Φ%d" % d_, "梁" if part == "钢筋梁" else "板"] + \
                   [("未取得" if Q_[s][part] is None
                     else round(Q_[s][part].get(str(d_), 0) or 0, 1)) for s in SCHEMES]
            r = put(ws, r, vals, [None, None] + [N1] * len(SCHEMES))
    def _tot(key):
        return [("未取得" if Q_[s][key] is None else round(Q_[s][key], 1)) for s in SCHEMES]

    r = put(ws, r, ["梁合计", "梁"] + _tot("钢筋梁合计"),
            fonts=[F_BOLD] * (2 + len(SCHEMES)), fill=FILL_HL)
    r = put(ws, r, ["板合计", "板"] + _tot("钢筋板合计"),
            fonts=[F_BOLD] * (2 + len(SCHEMES)), fill=FILL_HL)
    r = put(ws, r, ["梁板总计", "梁+板"] + [("未取得" if rebar_sum(Q_[s]) is None
                                        else round(rebar_sum(Q_[s]), 1)) for s in SCHEMES],
            fonts=[F_BOLD] * (2 + len(SCHEMES)), fill=FILL_HL)
    return ws


# ------------------------------------------------------------------ 页 8
def sheet_quota(wb):
    ws = wb.create_sheet("8.定额依据")
    r = title(ws, "八、定额依据与取费标准", 8,
              "数据逐条与《广东省房屋建筑与装饰工程综合定额(2018)》扫描件原文核对")
    ws.column_dimensions["A"].width = 12
    ws.column_dimensions["B"].width = 44
    for c, w in zip("CDEFGH", [10, 11, 11, 11, 11, 11]):
        ws.column_dimensions[c].width = w
    r = 4
    r = put(ws, r, ["定额编号", "子目名称", "单位", "基价", "人工费", "材料费", "机具费", "管理费"],
            fill=FILL_H2)
    for c in range(1, 9):
        ws.cell(row=r - 1, column=c).font = F_H2
    for code in ["A1-5-9", "A1-5-14", "A1-5-5", "A1-5-105", "A1-5-106", "A1-5-107",
                 "A1-20-33", "A1-20-34", "A1-20-40", "A1-20-75", "A1-20-79"]:
        nm, u, base, lab, mat, mac, mgr = Q.QUOTA[code]
        r = put(ws, r, [code, nm, u, base, lab, mat, mac, mgr],
                [None, None, None, N2, N2, N2, N2, N2])
    r += 1
    for t in ["A1-5-9/A1-5-14 材料费中「80210180 预拌混凝土」为**未计价主材**，定额列消耗量 (10.100) m³/10m³，"
              "故计价时以信息价×1.010 替换；",
              "A1-5-105/106/107 钢筋消耗量 1.020/1.025/1.025 t/t，定额内钢筋单价 3738.53/3547.15/3547.15 元/t，"
              "计价时以信息价替换；",
              "A1-20-* 模板子目材料费为周转材料（胶合板、钢支撑等），按定额原值计，未作信息价替换。",
              "管理费率：混凝土及钢筋混凝土 28.75%，模板 26.35%（=（人工+机具）×费率，已含于基价）。",
              "利润：定额人工费 + 施工机具费之和 × 20%。",
              "增值税：9%。"]:
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=8)
        c = ws.cell(row=r, column=1, value="· " + t)
        c.font = F_NOTE
        c.alignment = LEFT
        ws.row_dimensions[r].height = 15
        r += 1
    return ws


# ------------------------------------------------------------------ 页 9
# 逐表行数比对的判据：**直接采用 impcheck.py 的 MUST_MATCH / INFO_TABLES 划分**，
# 免得"导入校验说一致、报告却说不可能一致"。那份划分是有实证的：
#   tblSlab 源 336 → 导入后 364（YJK 会拆分/补板，现场实测值），tblAxis 会被合并共线轴，
#   tblProperty/tblProjectPara 会在 save 时展开 —— 把这几张表当"必须相等"，
#   会把一次**完全正确的导入**判成失败。
MUST_EQUAL = ("tblJoint", "tblColSeg", "tblBeamSeg", "tblWallSeg", "tblFloor",
              "tblStdFlr", "tblLoadSeg")
INFO_TABLES = ("tblAxis", "tblGrid", "tblSlab", "tblBeamSect", "tblColSect")


def _run_dirs(scheme):
    """该方案的候选计算工作目录。

    `run_all_yjk.py` 用 `<技能>/YJK_run/`，`yjk_quant.py` 用 `<技能>/YJK_run_q/`
    —— 两个入口都要能核到，否则"没找到"会被误报成"没算过"。
    """
    return [os.path.join(ROOT, "YJK_run_q", scheme), os.path.join(ROOT, "YJK_run", scheme)]


def _find(paths):
    for p in paths:
        if os.path.exists(p):
            return p
    return None


def _rows_of(db, tables=None):
    """只读打开模型库取各表行数；缺表记 None（不猜 0）。"""
    tables = tables or (MUST_EQUAL + INFO_TABLES)
    con = sqlite3.connect("file:%s?mode=ro" % db.replace("\\", "/"), uri=True)
    try:
        out = {}
        for t in tables:
            try:
                out[t] = con.execute("SELECT count(*) FROM [%s]" % t).fetchone()[0]
            except sqlite3.Error:
                out[t] = None
        return out
    finally:
        con.close()


def _decode_check(path):
    """读 `check.out`：**它是 UTF-16LE（带 BOM）**，按 GBK 硬读只会得到乱码且不报错。

    判据与 `run_all_yjk.py:_decode_check()` 一致（同一份文件、同一套编码顺序），
    免得两个脚本对同一份 check.out 给出不同结论。
    """
    with open(path, "rb") as fh:
        raw = fh.read()
    for enc in ("utf-16", "utf-8-sig", "gbk"):
        try:
            return raw.decode(enc)
        except (UnicodeDecodeError, UnicodeError):
            continue
    return raw.decode("utf-8", errors="replace")


def _check_out_pass(path):
    """check.out 里有没有「未发现问题」。"""
    return "未发现问题" in _decode_check(path)


def yjk_evidence(Q_):
    """第 9 页第 3 节的**实测证据**。

    ★ 老版本这一节是四条**写死的声明**（"五方案均已通过数检"、"逐表行数一致"、
      "wpj 均在本轮之后刷新"、"钢筋取自工程量统计模块"），函数体里没有任何文件访问
      —— 在从未算过任何模型的机器上跑，报告照旧宣称全部通过。
      现在每条都要拿盘上的东西说话，拿不到就写「未核对」并计入退出码。
    """
    rows = []

    # ① 数检 check.out
    ok, miss, bad = [], [], []
    for s in SCHEMES:
        p = _find([os.path.join(d, "设计结果", "check.out") for d in _run_dirs(s)])
        if not p:
            miss.append(s)
        elif _check_out_pass(p):
            ok.append(s)
        else:
            bad.append(s)
    n1 = len(ok)
    rows.append(("① 各方案「数检未发现问题」(设计结果/check.out)",
                 "已核对 %d/%d" % (n1, len(SCHEMES)),
                 "通过：%s；未通过：%s；缺 check.out：%s" %
                 (",".join(ok) or "无", ",".join(bad) or "无", ",".join(miss) or "无")))
    if n1 != len(SCHEMES):
        flag("第9页①：数检证据不足 —— 通过 %d/%d（未通过 %s / 缺文件 %s）"
             % (n1, len(SCHEMES), ",".join(bad) or "无", ",".join(miss) or "无"))

    # ② 源模型 .ydb 与计算后 .ymd 逐表行数
    same, diff, unver, info = [], [], [], []
    for s in SCHEMES:
        ydb = _find([os.path.join(ROOT, "models", s + ".ydb")])
        ymd = _find([os.path.join(d, s + ".ymd") for d in _run_dirs(s)])
        if not ydb or not ymd:
            unver.append("%s(缺%s)" % (s, ".ydb" if not ydb else ".ymd"))
            continue
        try:
            a, b = _rows_of(ydb), _rows_of(ymd)
        except sqlite3.Error as e:
            unver.append("%s(打不开：%s)" % (s, e))
            continue
        # ★ 缺表（None）**不是"相等"**：两张空壳库（表都不在）以前会因为 None == None
        #   被判成"逐表一致 5/5 + rc 0" —— 与老版本"空集恒真"是同一个洞。
        diffs = []
        for t in MUST_EQUAL:
            ta, tb = a.get(t), b.get(t)
            if ta is None or tb is None:
                diffs.append("%s 缺表(源%s/工程%s)" % (t.replace("tbl", ""), ta, tb))
            elif ta != tb:
                diffs.append("%s %s->%s" % (t.replace("tbl", ""), ta, tb))
        # 源模型自己的必判表合计必须 > 0，否则"两边一样空"什么也没证明（空集闸门）
        src_total = sum(v for v in (a.get(t) or 0 for t in MUST_EQUAL) if v > 0)
        if src_total <= 0:
            unver.append("%s(源模型必判表合计 0 行：空骨架/拿错文件)" % s)
            continue
        (same if not diffs else diff).append(
            s if not diffs else "%s[%s]" % (s, ",".join(diffs)))
        chg = ["%s %s->%s" % (t.replace("tbl", ""), a[t], b[t])
               for t in INFO_TABLES if a.get(t) != b.get(t)]
        if chg:
            info.append("%s[%s]" % (s, ",".join(chg)))
    note2 = "一致：%s；不符：%s；未核对：%s" % (
        ",".join(same) or "无", ",".join(diff) or "无", ",".join(unver) or "无")
    if info:
        note2 += "；参考表有变化（save/导入会合法改动，不算失败）：%s" % ",".join(info)
    rows.append(("② 源模型 .ydb 与计算后 .ymd 逐表行数一致（必判表 %d 张）"
                 % len(MUST_EQUAL),
                 "已核对 %d/%d" % (len(same), len(SCHEMES)), note2))
    if diff or unver:
        flag("第9页②：逐表行数比对不完整 —— 不符 %s / 未核对 %s"
             % (",".join(diff) or "无", ",".join(unver) or "无"))

    # ③ 各方案 设计结果/ 下的 wpj*.out 个数
    wpj_note = []
    wpj_bad = []
    for s in SCHEMES:
        res = _find([os.path.join(d, "设计结果") for d in _run_dirs(s)])
        if not res:
            wpj_note.append("%s：缺 设计结果\\" % s)
            wpj_bad.append(s)
            continue
        f = sorted(glob.glob(os.path.join(res, "wpj*.out")))
        nf = Q_[s].get("层数") or 0
        new = max((os.path.getmtime(x) for x in f), default=None)
        wpj_note.append("%s：%d 个（层数 %s）%s" % (
            s, len(f), nf, time.strftime("最新 %Y-%m-%d %H:%M:%S", time.localtime(new))
            if new else "无"))
        if not f or (nf and len(f) != nf):
            wpj_bad.append(s)
    rows.append(("③ 各方案 设计结果/ 下 wpj*.out 个数 = 层数",
                 "已核对 %d/%d" % (len(SCHEMES) - len(wpj_bad), len(SCHEMES)),
                 "；".join(wpj_note)))
    if wpj_bad:
        flag("第9页③：wpj*.out 个数/存在性不符：%s" % ",".join(wpj_bad))

    # ④ 钢筋数据来源（用量表是否真取到）
    src_note = []
    src_bad = []
    for s in SCHEMES:
        src = Q_[s].get("sources") or {}
        if not src:
            src_note.append("%s：quantities.json 没记来源（旧版 JSON）" % s)
            src_bad.append(s)
            continue
        bad = [k for k in ("rebar_beam", "rebar_column", "rebar_slab")
               if src.get(k) != "yjk"]
        src_note.append("%s：%s" % (s, "已取得" if not bad else
                                  "未取得 %s" % ",".join(bad)))
        if bad:
            src_bad.append(s)
    rows.append(("④ 梁/板/柱钢筋用量取自 YJK 工程量统计模块输出",
                 "已核对 %d/%d" % (len(SCHEMES) - len(src_bad), len(SCHEMES)),
                 "；".join(src_note)))
    if src_bad:
        flag("第9页④：钢筋用量表未取得：%s" % ",".join(src_bad))

    return rows


def _add(a, b):
    """缺任一项就返回 None（用于"分项之和"这类核对，别把缺数据当 0 相加）。"""
    if a is None or b is None:
        return None
    return a + b


def _cmp_row(label, hand, prog, tol, unit="", note=""):
    """手算 vs 程序值：真的比一次，并给出偏差（老版本两侧是同一个变量）。"""
    if hand is None:
        return (label, "—", "—" if prog is None else "%.6g" % prog,
                "★未核对（缺数据）%s" % note)
    if prog is None:
        return (label, "%.6g" % hand, "—", "★未核对（程序值缺）%s" % note)
    d = abs(hand - prog)
    okk = d <= tol
    return (label, "%.6g" % hand, "%.6g" % prog,
            "%s%s%s（偏差 %.6g%s）" % ("一致" if okk else "★不符", note,
                                 "" if okk else " ← 手算与程序值对不上",
                                 d, unit))


def sheet_check(wb, Q_, costs, up):
    ws = wb.create_sheet("9.自检与校核")
    r = title(ws, "九、自检与手算校核", 6)
    ws.column_dimensions["A"].width = 34
    for c in "BCDEF":
        ws.column_dimensions[c].width = 15
    r = 4
    ws.cell(row=r, column=1, value="1. 造价明细自检（分项之和 ＝ 合计）").font = F_H2
    r += 1
    r = put(ws, r, ["方案", "分项之和(元)", "合计(元)", "偏差", "结论"], fill=FILL_H2)
    for c in range(1, 6):
        ws.cell(row=r - 1, column=c).font = F_H2
    for s in SCHEMES:
        c = costs[s]
        # ★ 独立重算：从**工程量(json)+综合单价**重算五个分项再求和，_而不是_
        #   照抄 costs 里的分项（老版本两侧是同一组加数按同一顺序求和，偏差恒 0、
        #   结论恒「通过」——同义反复）。缺钢筋时无法核对，明确写出来。
        parts = [Q_[s]["砼有梁板"] * up["conc_c30"][0],
                 Q_[s]["模板梁_25内"] * up["form_25in"][0]
                 + Q_[s]["模板梁_25外"] * up["form_25out"][0],
                 Q_[s]["模板板"] * up["form_slab"][0],
                 rebar_cost(Q_[s]["钢筋梁"], up),
                 rebar_cost(Q_[s]["钢筋板"], up)]
        if any(p is None for p in parts):
            r = put(ws, r, [s, "未核对", round(c["合计"], 2), "—",
                            "★ 缺钢筋数据，无法核对（合计未含%s钢筋）"
                            % "/".join(c["钢筋缺失"])],
                    [None, None, N2, "0.000000", None])
            flag("第9页1：%s 分项之和无法核对（缺 %s 钢筋）"
                 % (s, "/".join(c["钢筋缺失"])))
            continue
        tot = sum(parts)
        dev = tot - c["合计"]
        okk = abs(dev) < 1e-6
        r = put(ws, r, [s, round(tot, 2), round(c["合计"], 2), round(dev, 6),
                        "通过" if okk else "★不符"],
                [None, N2, N2, "0.000000", None])
        if not okk:
            flag("第9页1：%s 分项之和 %.2f != 合计 %.2f（偏差 %.6f）"
                 % (s, tot, c["合计"], dev))
    r += 1
    ws.cell(row=r, column=1, value="2. 工程量手算校核（S0 无次梁）").font = F_H2
    r += 1
    d0 = Q_["S0"]
    nf = d0.get("层数") or 0
    area = d0.get("楼盖面积每层")
    sa = d0.get("板面积每层_YJK")
    sa_src = (d0.get("sources") or {}).get("slab_area")
    th_m = (d0.get("板厚") or 0) / 1000.0
    try:
        cb, ch = [int(v) / 1000.0 for v in str(d0["柱截面"]).split("×")]
    except (KeyError, ValueError):
        cb = ch = None
    ncol = d0.get("柱数") or 0
    # 缺字段/格式不对就别硬算：那一行显示「未核对」，不要让整份报告崩掉。
    try:
        hand_beam_v = sum(float(str(b["截面"]).split("×")[0]) / 1000.0
                          * float(str(b["截面"]).split("×")[1]) / 1000.0
                          * float(b["净长"]) for b in d0["梁明细"])
    except (KeyError, ValueError, TypeError, IndexError):
        hand_beam_v = None
    _sa_txt = "—" if sa is None else "%.2f m²" % sa
    checks = [
        # ① 轴网面积：手算用图纸尺寸，程序值取 json 里的模型轴网面积
        _cmp_row("轴网面积 = 67.2×33.6", 67.2 * 33.6, area, 0.05),
        # ② 板投影面积：来源必须说清（缺 YJK 面积表时程序值是兜底值）
        ("模型板投影面积（YJK 实测）",
         "—" if (sa is None or sa_src != "yjk") else "%.2f m²" % sa,
         _sa_txt,
         "取用值（板伸至梁外皮）" if sa_src == "yjk"
         else ("★ 这份 quantities.json 没记来源（多半是旧版 collect.py 生成），"
               "无法判定此处是模型实测值还是轴网兜底值" if sa_src is None
               else "★ 未取得 YJK 面积表，程序值是**轴网包络兜底值**，"
                    "上面第 1 页第 9 条已注明")),
        # ③ 板体积 = 板面积×板厚 − 柱占体积（用 json 的原始字段重算）
        _cmp_row("板体积（每层）= 板面积×板厚 − 柱占体积",
                 None if (cb is None or sa is None) else (sa - ncol * cb * ch) * th_m,
                 (d0.get("砼板") / nf) if (nf and d0.get("砼板") is not None) else None,
                 0.01, " m³"),
        # ④ 梁体积：明细逐行 截面×净长 求和
        _cmp_row("S0 梁体积 = 0.3×0.8×净长×层数（明细逐行求和）",
                 hand_beam_v, d0.get("砼梁"), 0.01, " m³"),
        # ⑤ 有梁板 = 梁 + 板
        _cmp_row("有梁板混凝土 = 梁体积 + 板体积",
                 _add(d0.get("砼梁"), d0.get("砼板")), d0.get("砼有梁板"), 0.01, " m³"),
        # ⑥ 模板小计 = 25内 + 25外
        _cmp_row("梁模板小计 = 25cm内 + 25cm外",
                 _add(d0.get("模板梁_25内"), d0.get("模板梁_25外")),
                 d0.get("模板梁"), 0.5, " m²"),
        # ⑦ 模板合计 = 梁模板小计 + 板模板
        _cmp_row("模板合计 = 梁模板小计 + 板模板",
                 _add(d0.get("模板梁"), d0.get("模板板")), d0.get("模板合计"),
                 0.5, " m²"),
    ]
    r = put(ws, r, ["校核项", "手算/理论值", "程序值", "结论"], fill=FILL_H2)
    for c in range(1, 5):
        ws.cell(row=r - 1, column=c).font = F_H2
    for row in checks:
        r = put(ws, r, list(row))
        if "★" in str(row[3]):
            flag("第9页2：%s —— %s" % (row[0], row[3]))
    r += 1
    ws.cell(row=r, column=1, value="3. YJK 计算验收（客观证据）").font = F_H2
    r += 1
    r = put(ws, r, ["核对项", "结论", "明细"], fill=FILL_H2)
    for c in range(1, 4):
        ws.cell(row=r - 1, column=c).font = F_H2
    for item, verdict, note in yjk_evidence(Q_):
        r = put(ws, r, [item, verdict, note])
    return ws


# ------------------------------------------------------------------ 页 10
def sheet_concl(wb, Q_, costs):
    ws = wb.create_sheet("10.结论与建议")
    r = title(ws, "十、结论与建议", 7)
    ws.column_dimensions["A"].width = 8
    ws.column_dimensions["B"].width = 16
    ws.column_dimensions["C"].width = 15
    for c in "DEFG":
        ws.column_dimensions[c].width = 14
    r = 4
    order = sorted(SCHEMES, key=lambda s: costs[s]["合计"])
    base = costs["S0"]["合计"]
    r = put(ws, r, ["排名", "方案", "楼盖造价(元)", "相对 S0", "模板(m²)",
                    "梁板钢筋(kg)", "板厚(mm)"], fill=FILL_H2)
    for c in range(1, 8):
        ws.cell(row=r - 1, column=c).font = F_H2
    for i, s in enumerate(order, 1):
        d = Q_[s]
        rs_ = rebar_sum(d)
        rr = put(ws, r, [i, "%s %s" % (s, d["info"]["name"]), round(costs[s]["合计"], 2),
                         costs[s]["合计"] / base, d["模板合计"],
                         ("未取得" if rs_ is None else round(rs_, 1)), d["info"]["板厚"]],
                 [N0, None, N0, PCT, N1, N0, N0],
                 fill=FILL_BEST if i == 1 else None)
        r = rr
    r += 1
    best = order[0]
    worst = order[-1]
    save = costs[worst]["合计"] - costs[best]["合计"]
    # ★ 下面两条（3/4）以前是**上一次运行时的字面量**（"25.5 kg/m²"、"421 m³"、
    #   "以单向 2 道次梁的平衡点最佳"），没有任何代码核对它们与第 2/7/10 页的数字是否一致：
    #   数据一变（例如钢筋没取到、或改了 config 重算），同一页的动态第 1/2 条与
    #   静态第 3/4 条就会互相矛盾。现在全部现算。
    def rng(key, unit, fmt="%.0f"):
        """某个工程量在五个方案上的区间（缺数据就说缺，不编）。"""
        vals = [Q_[s].get(key) for s in SCHEMES]
        if any(v is None for v in vals):
            return "（%s 有方案缺数据，未取得）" % key
        return "%s ~ %s %s" % (fmt % min(vals), fmt % max(vals), unit)

    def slab_rebar_density(s):
        v = Q_[s].get("钢筋板合计")
        return None if v is None else v / Q_[s]["楼盖面积全楼"]

    with_beam = [s for s in SCHEMES if s != "S0"] or list(SCHEMES)
    dens = [slab_rebar_density(s) for s in with_beam]
    if any(v is None for v in dens):
        slab_dens_txt = "（板钢筋含量有方案未取得，见第 2 页「未取得」）"
    else:
        slab_dens_txt = "%.1f ~ %.1f kg/m²" % (min(dens), max(dens))
    thick_txt = "%d ~ %d mm" % (min(Q_[s]["info"]["板厚"] for s in with_beam),
                                max(Q_[s]["info"]["板厚"] for s in with_beam))
    s0_dens = slab_rebar_density("S0")
    cheaper = costs[best]["合计"] < costs["S0"]["合计"]
    txt = [
        "结论：",
        "1. 在柱网、荷载、材料强度与构件截面均合理的前提下，五个次梁布置方案的楼盖造价（梁+板，除税）排序为：%s。"
        % " ＞ ".join("%s(%s)" % (s, Q_[s]["info"]["name"]) for s in reversed(order)),
        "2. 最经济方案为 **%s（%s）**，楼盖造价 %.0f 元（单方 %.2f 元/m²）；"
        "最不经济方案为 **%s（%s）**，%.0f 元（单方 %.2f 元/m²）；两者相差 %.0f 元，约 %.1f%%。"
        % (best, Q_[best]["info"]["name"], costs[best]["合计"],
           costs[best]["合计"] / Q_["S0"]["楼盖面积全楼"],
           worst, Q_[worst]["info"]["name"], costs[worst]["合计"],
           costs[worst]["合计"] / Q_["S0"]["楼盖面积全楼"],
           save, save / costs[best]["合计"] * 100),
        "3. 次梁越密，梁与梁模板越多（本次：梁混凝土 %s、梁模板 %s），"
        "板厚越小（本次：%s），板钢筋也越小（本次：板钢筋含量 %s）；"
        "造价胜负取决于「梁的模板与混凝土增量」与「板的混凝土与钢筋减量」的对比。"
        % (rng("砼梁", "m³"), rng("模板梁", "m²"), thick_txt, slab_dens_txt),
        "4. 加密次梁后「减」的是板：板厚由 %d 降到 %s；板钢筋含量由 %s kg/m² 降到 %s。"
        "「增」的是梁与梁模板：梁混凝土由 %.0f m³ 增到 %s；梁模板由 %.0f m² 增到 %s。"
        "本次比选中「减量」%s「增量」，故%s；最优方案为 %s。"
        % (Q_["S0"]["info"]["板厚"], thick_txt,
           "未取得" if s0_dens is None else "%.1f" % s0_dens, slab_dens_txt,
           Q_["S0"]["砼梁"], rng("砼梁", "m³"),
           Q_["S0"]["模板梁"], rng("模板梁", "m²"),
           "略大于" if cheaper else "不大于",
           "设次梁反而更省" if cheaper else "设次梁并不更省",
           best),
        "5. 支模高度已按层高 4.80m 计入 2 次超高（%s 元/m² 与 %s 元/m² 增量），"
        "次梁越密、梁模板越大，超高增量被同步放大。"
        % (Q.QUOTA["A1-20-40"][2] / 100.0 * (1 + Q.PROFIT * 0.7),
           Q.QUOTA["A1-20-79"][2] / 100.0 * (1 + Q.PROFIT * 0.7)),
        "",
        "建议：",
        "· 若以造价最低为目标，优先采用排名靠前的方案；同时应校核楼板裂缝与挠度（板厚减小后长期刚度下降）。",
        "· 无次梁方案（板厚 %d）板钢筋用量与板厚相关，需注意其砼量与板模板的关系；"
        "次梁方案则应注意支模超高（层高 4.80m > 3.6m，每方案均计 2 次超高）。"
        % Q_["S0"]["info"]["板厚"],
        "· 若施工周期与模板周转是约束，可结合模板面积（模板合计）一并权衡。",
    ]
    for i, t in enumerate(txt):
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=7)
        c = ws.cell(row=r, column=1, value=t)
        c.font = F_H2 if t.endswith("：") else F_TXT
        c.alignment = LEFT
        ws.row_dimensions[r].height = 30 if len(t) > 60 else 16
        r += 1
    return ws


def _utf8_console():
    """让输出在任何控制台编码下都不崩（GBK 下把不可编码字符替换掉）。

    为什么需要：本包会打印 ✅ ❌ ⚠ −(U+2212) ² ³ 等**非 cp936** 字符，
    默认 GBK 控制台下 `print` 会抛 UnicodeEncodeError 并**以退出码 1 中断**，
    于是一个其实已经成功的任务（比如文件已经落盘）会被上层判成失败；
    对 frame_build.py 那条链更糟 —— 崩在被调用的库的 print 上，模型根本没写出来。

    `errors="replace"` 让它在 UTF-8 控制台下原样输出、在 GBK 下退化成 `?`，都不崩。
    ★ 只在实际执行时调用（CLI 入口），**不在 import 时改 stdout** ——
      这些模块会被别的脚本 import 当库用，污染 import 方的 stdout 是不对的。
    ★ 本文件实测**真的会触发**：main() 末行汇总打印 `元/m²`（U+00B2 不在 cp936 里），
      而 xlsx 在那之前**已经 save 落盘** → 退出码 1，上层会把已经成功的任务判成失败。
    ★ 本文件还要替被它 import 的纯库 `quota_gd.py`（无 `__main__`、无 print）兜底。
    """
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass


# ------------------------------------------------------------------
def load_qty(path):
    """读 `quantities.json`（**用户给的输入路径**）→ dict。

    任何一种读不出来都必须是**可读报错 + 非零退出**，不能抛裸 traceback：
    本包的口径见 `ydb_lint.connect()`（文件名、原因、怎么办三件都说清楚）。
    老版本直接 `open(a.qty)`：路径拼错就抛 `FileNotFoundError: [Errno 2] …`，
    用户看到的是栈，而不是"该做什么"。
    """
    p = os.path.abspath(path)
    if not os.path.exists(p):
        sys.exit("找不到 --qty 指定的文件：%s\n"
                 "  --qty 读的是 quantities.json（由 collect.py 生成，默认落在**它运行时**的"
                 "当前目录）。\n"
                 "  怎么办：先跑 `python collect.py`（或用 --out 指到你看得见的位置），"
                 "再把这个路径传给 --qty。" % p)
    if os.path.isdir(p):
        sys.exit("--qty 给的是目录，不是 json 文件：%s\n"
                 "  怎么办：传文件本身，例如 %s" % (p, os.path.join(p, "quantities.json")))
    if os.path.getsize(p) == 0:
        sys.exit("--qty 指定的文件是 0 字节（半写/内容为空）：%s\n"
                 "  怎么办：重新跑一次 collect.py 生成它。" % p)
    try:
        with open(p, encoding="utf-8-sig") as fh:
            doc = json.load(fh)
    except UnicodeDecodeError as e:
        sys.exit("--qty 不是 UTF-8 文本（%s）：%s\n"
                 "  怎么办：重新跑 collect.py；这个文件应当是本包写出的 UTF-8 json。"
                 % (e, p))
    except json.JSONDecodeError as e:
        sys.exit("--qty 不是合法的 json（第 %d 行第 %d 列：%s）：%s\n"
                 "  怎么办：多半是文件被手工改坏或写了一半 —— 重新跑 collect.py。"
                 % (e.lineno, e.colno, e.msg, p))
    except OSError as e:
        sys.exit("--qty 读不出来（%s）：%s" % (e, p))
    if not isinstance(doc, dict):
        sys.exit("--qty 的顶层必须是 json 对象（方案 → 数据）：%s" % p)
    miss = [s for s in SCHEMES if not isinstance(doc.get(s), dict)]
    if miss:
        sys.exit("--qty 里缺这些方案的数据：%s（本报告需要 %s）：%s\n"
                 "  怎么办：确认这份 json 是**本技能**的 collect.py 生成的"
                 "（别的技能的产物名字可能也像）。"
                 % (",".join(miss), "/".join(SCHEMES), p))
    return doc


def prepare_out(path):
    """`--out` 落盘前的检查：给的是目录 / 父目录建不出来 → 可读报错。"""
    p = os.path.abspath(path)
    if os.path.isdir(p):
        sys.exit("--out 给的是目录，不是文件名：%s\n"
                 "  怎么办：给一个文件名，例如 %s" % (p, os.path.join(p, "报告.xlsx")))
    d = os.path.dirname(p)
    if d and not os.path.isdir(d):
        try:
            os.makedirs(d, exist_ok=True)
        except OSError as e:
            sys.exit("--out 的目录建不出来（%s）：%s" % (e, d))
    return p


def main(argv=None):
    _utf8_console()          # ★ 必须在 argparse 之前：--help 也是写到 stdout 的
    ap = argparse.ArgumentParser()
    ap.add_argument("--qty", default=os.path.join(ROOT, "out", "quantities.json"))
    ap.add_argument("--out", default=os.path.join(
        ROOT, "out", "裙楼楼盖次梁布置比选经济对比报告.xlsx"))
    a = ap.parse_args(argv)

    Q_ = normalize_rebar(load_qty(a.qty))     # 旧版 collect 写的 `{}` 也算"没数据"，不是 0
    out_path = prepare_out(a.out)

    pricer = Q.Pricer()
    pricer_ki = Q.Pricer(labor_index=Q.LABOR_INDEX)
    up = unit_prices(pricer)
    up_ki = unit_prices(pricer_ki)
    global Q_PRICER_REF
    Q_PRICER_REF = up
    costs = {s: scheme_cost(Q_[s], up) for s in SCHEMES}
    costs_ki = {s: scheme_cost(Q_[s], up_ki) for s in SCHEMES}

    del PROBLEMS[:]                 # 可重复调用（被当库用时不留脏状态）
    wb = Workbook()
    wb.remove(wb.active)
    sheet_overview(wb, Q_)
    sheet_qty(wb, Q_)
    sheet_unit(wb, up, pricer)
    sheet_cost(wb, Q_, costs, costs_ki)
    sheet_detail(wb, Q_, costs, up)
    sheet_beamcalc(wb, Q_)
    sheet_mat(wb, Q_)
    sheet_quota(wb)
    sheet_check(wb, Q_, costs, up)
    sheet_concl(wb, Q_, costs)
    try:
        wb.save(out_path)
    except OSError as e:
        sys.exit("报告写不出来（%s）：%s\n"
                 "  常见原因：文件正被 Excel 打开着 / 无写权限 / 磁盘满。" % (e, out_path))
    print("-> %s" % a.out)
    for s in SCHEMES:
        print("  %s  %-14s 楼盖造价 %12.2f 元  单方 %7.2f 元/m²  指数 %5.1f"
              % (s, Q_[s]["info"]["name"], costs[s]["合计"],
                 costs[s]["合计"] / Q_["S0"]["楼盖面积全楼"],
                 costs[s]["合计"] / costs["S0"]["合计"] * 100))
    # ★ 第 9 页报了问题就必须让调用方看见：屏幕/报告上写着结论、退出码却是 0，
    #   等于把"没核对过"当"核对通过"交出去（本文件老版本正是如此：第 9 页
    #   全是写死的"已通过"，退出码恒 0）。
    if PROBLEMS:
        print()
        print("!! 第 9 页「自检与校核」有 %d 项不通过或无法核对：" % len(PROBLEMS))
        for p in PROBLEMS:
            print("   · %s" % p)
        print("   xlsx 已生成（%s），但**不要**当作「已校核」的成品交付。" % a.out)
        return 1
    print("第 9 页「自检与校核」全部通过（分项×合计、手算×程序、YJK 证据均核对）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
