# -*- coding: utf-8 -*-
"""柱型方案用量 / 造价 / 结构占用面积统计，并输出**公式驱动**的 Excel 工作簿。

对外只需一个函数 build(scheme, out_path)。

方案 JSON（scheme.json）格式
---------------------------
{
  "project": "项目名",
  "std_floors": {                       # 键为标准层号
     "3": {"height_mm": 6000, "nat_heights": [6000, 5500]},
     "4": {"height_mm": 7500, "nat_heights": [7500, 4500, 4500]},
     "5": {"height_mm": 4500, "nat_heights": [4500,4500,4500,4500,4500,4500,4500]}
  },
  # height_mm   = 标准层定义层高（"标准层一层"口径）
  # nat_heights = 该标准层覆盖的各自然层实际层高（"代表楼层"口径，可不等）
  # 若只给 height_mm + n_floors，则按等层高处理
  "groups": {"Z1": [15, 16], "Z2": [14]},        # 归并组 → 柱号（设计单位是"组"）
  "types": ["普通RC", "加芯RC", "型钢SRC", "钢管叠合柱", "圆钢管混凝土柱"],
  "sections": {                                  # 柱型 → 标准层 → 组 → 几何
     "普通RC": { "3": { "Z1": {"kind": 1, "b": 1350} } },
     "圆钢管混凝土柱": { "3": { "Z1": {"kind": 12, "D": 1200, "tw": 16} } }
  }
}

几何字段（长度 mm）
    kind 1   矩形RC                b
    kind 12  圆钢管混凝土柱        D(外径) tw(壁厚)
    kind 15  型钢SRC(十字型钢)     b, f(翼缘宽), tw(板厚), d(腹板高)
    kind 102 钢管混凝土叠合柱      b, D(内管外径), tw(内管壁厚)

口径（与工程惯例一致，均可在"单价与假定"表里改）
------------------------------------------------
* 混凝土量：矩形/型钢/叠合柱 = 全截面×层高；圆钢管混凝土柱 = 管内净面积×层高
* 钢筋量  = (纵筋率 + 体积配箍率) × 结构占用面积 × 层高 × 7.85
* 型钢/钢管量 = 钢材截面面积 × 层高 × 7.85
* 模板量  = 柱周长 × 层高；圆钢管混凝土柱钢管兼作模板，不另计
* 防腐防火 = 圆钢管混凝土柱按含防火涂层的钢管外表面 π(D+2a)，其余柱型外包混凝土不另计
* 结构占用面积 = 圆钢管混凝土柱 π/4×(D+2a)²（钢管+涂料），其余柱型 = 柱外轮廓面积
  （是"每层"量，代表楼层口径要乘该标准层的自然层数）
"""
import datetime
import math
import os
import zipfile

FIRE_T = 30.0            # 防火涂料厚度 mm
RHO = 7.85               # 钢材密度 t/m³
BASE_TYPE = "普通RC"      # 对比基准柱型
TOTAL_SHEET = "合计"


def base_of(types):
    """相对指标的基准柱型。用 --types 只留一个柱型时基准可能不在其中，退回第一个柱型。"""
    types = list(types)
    return BASE_TYPE if BASE_TYPE in types else (types[0] if types else BASE_TYPE)

DEFAULT_PRICES = {
    "C60混凝土": (530.0, "元/m³"),
    "HRB400钢筋": (4050.0, "元/t(制安)"),
    "Q355十字型钢骨": (7500.0, "元/t(制作+安装)"),
    "Q355焊接钢管": (7800.0, "元/t(卷制+安装)"),
    "矩形柱模板": (60.0, "元/m²"),
    "钢管柱防腐+厚型防火": (85.0, "元/m²(按涂料外表面)"),
}
# 纵筋率 / 体积配箍率(含芯箍)，按柱型给
DEFAULT_REBAR = {"普通RC": 0.008, "加芯RC": 0.016, "型钢SRC": 0.008,
                 "钢管叠合柱": 0.008, "圆钢管混凝土柱": 0.0}
DEFAULT_TIE = {"普通RC": 1.20, "加芯RC": 2.20, "型钢SRC": 1.20,
               "钢管叠合柱": 1.50, "圆钢管混凝土柱": 0.0}
STEEL_KIND = {"型钢SRC": "Q355十字型钢骨", "钢管叠合柱": "Q355焊接钢管",
              "圆钢管混凝土柱": "Q355焊接钢管"}


# ---------------------------------------------------------------- 几何
def geom(geo):
    """几何 -> 各项指标（长度 mm，面积 m²，周长/表面 m）。

    返回的 b/h/u/t/d/f 是**归一化后的表格字段**（各柱型都要能直接写进 Excel 公式）：
        kind 1   : b, h
        kind 12  : b=D外径, h=D内径
        kind 15  : b=h=柱边长, u=t=板厚, d=腹板高, f=翼缘宽
        kind 102 : b=h=柱边长, u=内管外径, t=内管内径
    """
    k = int(geo.get("kind", 1))
    fire_t = float(geo.get("fire_t", FIRE_T))
    if k == 12:
        D, tw = float(geo["D"]), float(geo["tw"])
        Din = D - 2 * tw
        b = D                           # 表格字段：b=外径，h=内径
        h = Din
        u = t = d = f = 0.0
        Aconc = math.pi / 4 * (Din / 1000.0) ** 2
        Asteel = math.pi / 4 * ((D / 1000.0) ** 2 - (Din / 1000.0) ** 2)
        peri, fire = 0.0, math.pi * (D / 1000.0 + 2 * fire_t / 1000.0)
        occ = math.pi / 4 * (D / 1000.0 + 2 * fire_t / 1000.0) ** 2
        sec, rhoa = "Φ%d×%d" % (round(D), round(tw)), None
    elif k == 15:
        b, f, tw, d = float(geo["b"]), float(geo["f"]), float(geo["tw"]), float(geo["d"])
        h, u, t = b, tw, tw
        Aconc = b * b / 1e6
        Asteel = (4 * f * tw + 2 * d * tw - tw * tw) / 1e6
        peri, fire, occ = 2 * (b + b) / 1000.0, 0.0, b * b / 1e6
        rhoa = Asteel / Aconc
        sec = "%d×%d+翼%d×%d×4+腹%d×%d×2" % (round(b), round(b), round(f), round(tw),
                                              round(d), round(tw))
    elif k == 102:
        b, D, tw = float(geo["b"]), float(geo["D"]), float(geo["tw"])
        Din = D - 2 * tw
        h, u, t, d, f = b, D, Din, 0.0, 0.0
        Aconc = b * b / 1e6
        Asteel = math.pi / 4 * ((D / 1000.0) ** 2 - (Din / 1000.0) ** 2)
        peri, fire, occ = 2 * (b + b) / 1000.0, 0.0, b * b / 1e6
        rhoa = Asteel / Aconc
        sec = "%d×%d+内管Φ%d×%d" % (round(b), round(b), round(D), round(tw))
    else:
        b = float(geo.get("b"))
        h = float(geo.get("h", b))
        u = t = d = f = 0.0
        Aconc = b * h / 1e6
        Asteel, peri, fire, occ = 0.0, 2 * (b + h) / 1000.0, 0.0, b * h / 1e6
        rhoa = None
        sec = "%d×%d" % (round(b), round(h)) if b != h else "%d×%d" % (round(b), round(b))
    return {"k": k, "b": b, "h": h, "u": u, "t": t, "d": d, "f": f,
            "Aconc": Aconc, "Asteel": Asteel, "rhoa": rhoa, "peri": peri,
            "fire": fire, "occ": occ, "sec": sec}


# ---------------------------------------------------------------- 方案读取
def load_scheme(path):
    import json
    s = json.load(open(path, encoding="utf-8-sig"))
    s.setdefault("types", list(s["sections"].keys()))
    s.setdefault("project", "")
    return s


def nat_heights(cfg):
    """该标准层各自然层的实际层高(mm) 列表。

    优先用 nat_heights（各自然层层高可以不同，例如标准层3 = 6000+5500）；
    没给就退化成 [定义层高] × n_floors。
    """
    if cfg.get("nat_heights"):
        return [float(x) for x in cfg["nat_heights"]]
    return [float(cfg["height_mm"])] * int(cfg.get("n_floors", 1))


def n_floors(cfg):
    return len(nat_heights(cfg))


def total_height_m(cfg):
    """代表楼层总高(m) = 该标准层所覆盖全部自然层的层高之和。"""
    return sum(nat_heights(cfg)) / 1000.0


def expand(scheme):
    """展开成逐柱行：[(柱型, 标准层号, 柱号, 归并组, geo), …]

    只展开"截面表里有、且 groups 里也还在"的组——用 --cols 裁剪过组内成员时，
    截面表里可能残留已被裁掉的组，这里按交集处理，不会 KeyError。
    """
    rows = []
    for t in scheme["types"]:
        for std in sorted(scheme["sections"].get(t, {}), key=lambda x: int(x)):
            for gname, geo in scheme["sections"][t][std].items():
                members = scheme["groups"].get(gname)
                if not members:
                    continue
                for c in members:
                    rows.append((t, int(std), c, gname, geo))
    return rows


def price(scheme, key):
    return float(scheme.get("prices", {}).get(key, DEFAULT_PRICES[key][0]))


def rebar_of(scheme, t):
    return float(scheme.get("rebar", {}).get(t, DEFAULT_REBAR.get(t, 0.008)))


def tie_of(scheme, t):
    return float(scheme.get("tie", {}).get(t, DEFAULT_TIE.get(t, 1.2)))


# ---------------------------------------------------------------- Python 侧计算
def qty(scheme, t, std, height_m):
    """某柱型某标准层 一层 的用量（该标准层所有柱合计）。"""
    o = dict(conc=0.0, rebar=0.0, steel=0.0, form=0.0, fire=0.0, occ=0.0, cost=0.0)
    rho_rb = rebar_of(scheme, t) + tie_of(scheme, t) / 100.0
    p_con, p_rb, p_form, p_fire = (price(scheme, "C60混凝土"), price(scheme, "HRB400钢筋"),
                                   price(scheme, "矩形柱模板"), price(scheme, "钢管柱防腐+厚型防火"))
    p_steel = price(scheme, STEEL_KIND[t]) if t in STEEL_KIND else 0.0
    for tt, ss, c, g, geo in expand(scheme):
        if tt != t or ss != std:
            continue
        m = geom(geo)
        o["conc"] += m["Aconc"] * height_m
        o["steel"] += m["Asteel"] * height_m * RHO
        o["rebar"] += rho_rb * m["occ"] * height_m * RHO
        o["form"] += m["peri"] * height_m
        o["fire"] += m["fire"] * height_m
        o["occ"] += m["occ"]
        o["cost"] += (m["Aconc"] * p_con + rho_rb * m["occ"] * RHO * p_rb
                      + m["Asteel"] * RHO * p_steel + m["peri"] * p_form
                      + m["fire"] * p_fire) * height_m
    return o


def totals(scheme):
    """结构层合计：按标准层覆盖的**每个自然层实际层高**逐层累加。"""
    out = {}
    for t in scheme["types"]:
        o = dict(conc=0.0, rebar=0.0, steel=0.0, form=0.0, fire=0.0, occ=0.0, cost=0.0)
        for std, cfg in scheme["std_floors"].items():
            for h in nat_heights(cfg):
                x = qty(scheme, t, int(std), h / 1000.0)
                for k in o:
                    o[k] += x[k]
        out[t] = o
    return out


# ---------------------------------------------------------------- OOXML 写入
def colname(n):
    s = ""
    n += 1
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def esc(v):
    return (str(v).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))


def sheet_xml(rows):
    """cell = 数值 | 字符串 | ("f", 公式, 缓存值)"""
    out = []
    for ri, row in enumerate(rows, 1):
        cs = []
        for ci, v in enumerate(row):
            ref = "%s%d" % (colname(ci), ri)
            if v is None or v == "":
                continue
            if isinstance(v, tuple):
                f, val = v[1], v[2]
                if f.startswith("="):              # OOXML <f> 不带前导 '='
                    f = f[1:]
                body = "<f>%s</f>" % esc(f)
                if isinstance(val, (int, float)):
                    body += "<v>%s</v>" % repr(round(float(val), 6))
                cs.append('<c r="%s">%s</c>' % (ref, body))
            elif isinstance(v, (int, float)):
                cs.append('<c r="%s"><v>%s</v></c>' % (ref, repr(round(float(v), 6))))
            else:
                cs.append('<c r="%s" t="inlineStr"><is><t>%s</t></is></c>' % (ref, esc(v)))
        out.append('<row r="%d">%s</row>' % (ri, "".join(cs)))
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><worksheet '
            'xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
            '<sheetData>%s</sheetData></worksheet>' % "".join(out))


def write_wb(path, sheets):
    """sheets: [(表名, [行…]), …]；fullCalcOnLoad 保证 Excel 一打开就重算。"""
    z = zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED)
    z.writestr("[Content_Types].xml",
               '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://'
               'schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" '
               'ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
               '<Default Extension="xml" ContentType="application/xml"/><Override '
               'PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-'
               'officedocument.spreadsheetml.sheet.main+xml"/>%s</Types>' %
               "".join('<Override PartName="/xl/worksheets/sheet%d.xml" ContentType="application/'
                       'vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>' % i
                       for i in range(1, len(sheets) + 1)))
    z.writestr("_rels/.rels",
               '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns='
               '"http://schemas.openxmlformats.org/package/2006/relationships"><Relationship '
               'Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/'
               'relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>')
    z.writestr("xl/workbook.xml",
               '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><workbook xmlns="http://'
               'schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.'
               'openxmlformats.org/officeDocument/2006/relationships"><sheets>%s</sheets>'
               '<calcPr calcId="171027" fullCalcOnLoad="1"/></workbook>' %
               "".join('<sheet name="%s" sheetId="%d" r:id="rId%d"/>' % (nm, i, i)
                       for i, (nm, _) in enumerate(sheets, 1)))
    z.writestr("xl/_rels/workbook.xml.rels",
               '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns='
               '"http://schemas.openxmlformats.org/package/2006/relationships">%s</Relationships>' %
               "".join('<Relationship Id="rId%d" Type="http://schemas.openxmlformats.org/'
                       'officeDocument/2006/relationships/worksheet" Target="worksheets/sheet%d.xml"/>'
                       % (i, i) for i in range(1, len(sheets) + 1)))
    for i, (_, rows) in enumerate(sheets, 1):
        z.writestr("xl/worksheets/sheet%d.xml" % i, sheet_xml(rows))
    z.close()


# ---------------------------------------------------------------- 工作簿组织
Q, R, H = "'单价与假定'", "'截面参数'", "'层高'"


def build(scheme, out_path):
    rows = expand(scheme)
    types = scheme["types"]
    base = base_of(types)
    stds = sorted(int(x) for x in scheme["std_floors"])
    nrow = len(rows)
    R0, R1 = 3, 2 + nrow                       # 截面参数表数据行

    # ---- 1 单价与假定
    s1 = [["项目", "数值", "单位/说明"]]
    for k, (v, u) in DEFAULT_PRICES.items():
        s1.append([k, price(scheme, k), u])
    s1 += [["钢材密度", RHO, "t/m³"],
           ["防火涂料厚度", FIRE_T, "mm(钢管柱占用面积按 钢管外径+2×该值)"],
           ["", "", ""], ["配筋假定(可按实配替换)", "", ""]]
    for t in types:
        s1.append(["纵筋率-%s" % t, rebar_of(scheme, t), "占结构占用面积比例"])
        s1.append(["体积配箍率(含芯箍)-%s" % t, tie_of(scheme, t) / 100.0, "占结构占用面积比例"])
    s1 += [["", "", ""], ["对比基准柱型", BASE_TYPE, "相对造价/占用的分母"]]
    # 行号(1基)：1 表头 → 2..(1+np) 单价 → 密度/防火 → … 逐个定位
    row_fire = 2 + len(DEFAULT_PRICES) + 1                 # 防火涂料厚度所在行
    row_rho = 2 + len(DEFAULT_PRICES)                      # 钢材密度所在行
    row_con, row_rb = 2, 3
    row_form = 2 + 4                                        # 矩形柱模板
    row_firep = 2 + 5                                       # 防腐防火单价
    P_CON = "%s!$B$%d" % (Q, row_con)
    P_RB = "%s!$B$%d" % (Q, row_rb)
    P_FORM = "%s!$B$%d" % (Q, row_form)
    P_FIRE = "%s!$B$%d" % (Q, row_firep)
    RHO_C = "%s!$B$%d" % (Q, row_rho)
    FT_C = "%s!$B$%d" % (Q, row_fire)

    # ---- 2 截面参数（全部公式驱动）
    s2 = [[u"截面参数（改本表 b/h/u/t/d/f 即可全局自动重算；长度单位 mm）"] + [""] * 26,
          ["柱型", "标准层", "柱号", "类型Kind", "b", "h", "u", "t", "d", "f",
           "混凝土面积m²", "钢材面积m²", "含钢率", "模板周长m", "防火表面m²/m", "结构占用面积m²",
           "纵筋率", "体积配箍率(含芯箍)", "钢材单价元/t", "混凝土m³/m", "钢筋t/m",
           "型钢(钢管)t/m", "模板m²/m", "防腐防火m²/m", "造价元/m", "截面", "归并组"]]
    for (t, std, c, gname, geo) in rows:
        g = geom(geo)
        i = len(s2) + 1
        conc = "IF($D{r}=12,PI()/4*($F{r}/1000)^2,$E{r}/1000*$F{r}/1000)".format(r=i)
        steel = ("IF($D{r}=12,PI()/4*(($E{r}/1000)^2-($F{r}/1000)^2),"
                 "IF($D{r}=15,(4*$J{r}*$H{r}+2*$I{r}*$H{r}-$H{r}^2)/1000000,"
                 "IF($D{r}=102,PI()/4*(($G{r}/1000)^2-($H{r}/1000)^2),0)))".format(r=i))
        peri = "IF($D{r}=12,0,2*($E{r}+$F{r})/1000)".format(r=i)
        fire = "IF($D{r}=12,PI()*($E{r}/1000+2*{ft}/1000),0)".format(r=i, ft=FT_C)
        occ = ("IF($D{r}=12,PI()/4*($E{r}/1000+2*{ft}/1000)^2,$E{r}/1000*$F{r}/1000)"
               .format(r=i, ft=FT_C))
        rhoa = 'IF($D{r}=12,"",$L{r}/($E{r}*$F{r}/1000000))'.format(r=i)
        s2.append([
            t, "标准层%d" % std, "N%d" % c, g["k"], g["b"], g["h"], g["u"], g["t"],
            g["d"], g["f"],
            ("f", "=" + conc, g["Aconc"]), ("f", "=" + steel, g["Asteel"]),
            ("f", "=" + rhoa, g["rhoa"] if g["rhoa"] else ""),
            ("f", "=" + peri, g["peri"]), ("f", "=" + fire, g["fire"]),
            ("f", "=" + occ, g["occ"]),
            rebar_of(scheme, t), tie_of(scheme, t) / 100.0,
            price(scheme, STEEL_KIND[t]) if t in STEEL_KIND else 0.0,
            ("f", "=$K%d*$C{hr}" % i, g["Aconc"]),
            ("f", "=($Q%d+$R%d)*$P%d*%s" % (i, i, i, RHO_C),
             (rebar_of(scheme, t) + tie_of(scheme, t) / 100.0) * g["occ"] * RHO),
            ("f", "=$L%d*%s" % (i, RHO_C), g["Asteel"] * RHO),
            ("f", "=$N%d" % i, g["peri"]), ("f", "=$O%d" % i, g["fire"]),
            ("f", "=$T%d*%s+$U%d*%s+$V%d*$S%d+$W%d*%s+$X%d*%s"
                  % (i, P_CON, i, P_RB, i, i, i, P_FORM, i, P_FIRE),
             g["Aconc"] * price(scheme, "C60混凝土")
             + (rebar_of(scheme, t) + tie_of(scheme, t) / 100.0) * g["occ"] * RHO
             * price(scheme, "HRB400钢筋")
             + g["Asteel"] * RHO * (price(scheme, STEEL_KIND[t]) if t in STEEL_KIND else 0)
             + g["peri"] * price(scheme, "矩形柱模板") + g["fire"] * price(scheme, "钢管柱防腐+厚型防火")),
            g["sec"], gname])

    # ---- 3 层高
    s3 = [["标准层", "自然层", "层高mm", "层高m"]]
    nat_rows = 0
    for std in stds:
        cfg = scheme["std_floors"][str(std)]
        nat0 = cfg.get("first_nat")
        for j, hh in enumerate(nat_heights(cfg)):
            i = len(s3) + 1
            s3.append(["标准层%d" % std, (nat0 + j) if nat0 else j + 1, hh,
                       ("f", "=C%d/1000" % i, hh / 1000.0)])
            nat_rows += 1
    s3 += [["", "", "", ""], ["标准层", "标准层定义层高mm", "覆盖自然层数", "代表楼层总高m"]]
    h_def = len(s3) + 1
    for std in stds:
        cfg = scheme["std_floors"][str(std)]
        i = len(s3) + 1
        s3.append(["标准层%d" % std, cfg["height_mm"], n_floors(cfg),
                   ("f", "=SUMIF($A$2:$A$%d,$A%d,$C$2:$C$%d)/1000" % (1 + nat_rows, i, 1 + nat_rows),
                    total_height_m(cfg))])
    # 截面参数表引用标准层层高：第 T 列用层高表"标准层汇总块"的 B 列
    hrow = {std: h_def + k for k, std in enumerate(stds)}
    for j, r in enumerate(s2[2:]):
        i = 3 + j
        col_t = r[19]
        r[19] = (col_t[0], col_t[1].replace("{hr}", "%s!$B$%d" % (H, hrow[int(r[1][3:])])),
                 col_t[2])

    # ---- 4 各标准层分组截面
    w_head = ["标准层", "归并组", "柱"]
    for t in types:
        w_head += ["%s 截面" % t, "%s 占用m²" % t]
    s8 = [w_head]
    for std in stds:
        for gname, members in scheme["groups"].items():
            i = len(s8) + 1
            rec = ["标准层%d" % std, gname, "/".join("N%d" % c for c in members)]
            for t in types:
                geo = scheme["sections"][t].get(str(std), {}).get(gname)
                if geo is None:
                    rec += ["--", 0.0]
                    continue
                rec.append(geom(geo)["sec"])
                rec.append(("f", "=SUMPRODUCT(({r}!$A${a}:$A${b}=\"{nm}\")*({r}!$B${a}:$B${b}=$A{rw})"
                                 "*({r}!$AA${a}:$AA${b}=$B{rw})*{r}!$P${a}:$P${b})"
                                 .format(r=R, a=R0, b=R1, rw=i, nm=t),
                             sum(geom(scheme["sections"][t][str(std)][gname])["occ"]
                                 for _ in members)))
            s8.append(rec)

    # ---- 5/6 标准层一层 + 代表楼层
    def make_summary(name, mode):
        head = ["柱型", "标准层", "标准层层高m" if mode == "std" else "代表楼层总高m",
                "混凝土m³", "钢筋t", "型钢/钢管t", "模板m²", "防腐防火m²",
                "结构占用面积m²", "造价元", "相对%s造价%%" % base,
                "相对%s占用%%" % base]
        body = [head]
        last = 1 + len(types) * len(stds)
        for t in types:
            for std in stds:
                i = len(body) + 1
                hr = hrow[std]
                hcol = "B" if mode == "std" else "D"
                hf = "%s!%s%d%s" % (H, hcol, hr, "/1000" if mode == "std" else "")
                hv = (scheme["std_floors"][str(std)]["height_mm"] / 1000.0 if mode == "std"
                      else total_height_m(scheme["std_floors"][str(std)]))
                rec = [t, "标准层%d" % std, ("f", "=" + hf, hv)]
                for c in ("T", "U", "V", "W", "X", "P", "Y"):
                    if c == "P" and mode != "std":
                        f = ("=SUMPRODUCT(({r}!$A${a}:$A${b}=$A{rw})*({r}!$B${a}:$B${b}=$B{rw})*"
                             "{r}!$P${a}:$P${b})*%s" % hf).format(r=R, a=R0, b=R1, rw=i)
                    else:
                        tail = "*$C%d" % i if c != "P" else "*1"
                        f = ("=SUMPRODUCT(({r}!$A${a}:$A${b}=$A{rw})*({r}!$B${a}:$B${b}=$B{rw})*"
                             "{r}!${c}${a}:${c}${b}){t}"
                             .format(r=R, a=R0, b=R1, c=c, rw=i, t=tail))
                    rec.append(("f", f, None))
                rec.append(("f", "=$J%d/(SUMPRODUCT(($A$2:$A$%d=\"%s\")*($B$2:$B$%d=$B%d)*"
                                 "$J$2:$J$%d))-1" % (i, last, base, last, i, last), None))
                rec.append(("f", "=$I%d/(SUMPRODUCT(($A$2:$A$%d=\"%s\")*($B$2:$B$%d=$B%d)*"
                                 "$I$2:$I$%d))-1" % (i, last, base, last, i, last), None))
                body.append(rec)
        return body

    s_one = make_summary("标准层一层", "std")
    s_rep = make_summary("标准层代表楼层", "rep")
    # 用 Python 结果填公式缓存
    T = totals(scheme)
    for body, mode in ((s_one, "std"), (s_rep, "rep")):
        for r in body[1:]:
            t, std = r[0], int(r[1][3:])
            cfg = scheme["std_floors"][str(std)]
            h = (cfg["height_mm"] / 1000.0 if mode == "std" else total_height_m(cfg))
            o = qty(scheme, t, std, h)
            base_q = qty(scheme, base, std, h)
            nf = 1 if mode == "std" else n_floors(cfg)
            for j, v in enumerate([o["conc"], o["rebar"], o["steel"], o["form"], o["fire"],
                                   o["occ"] * nf, o["cost"]]):
                r[3 + j] = (r[3 + j][0], r[3 + j][1], v)
            r[10] = (r[10][0], r[10][1], o["cost"] / base_q["cost"] - 1 if base_q["cost"] else 0)
            r[11] = (r[11][0], r[11][1], o["occ"] / base_q["occ"] - 1 if base_q["occ"] else 0)

    # ---- 7 合计
    tot_head = ["柱型", "混凝土m³", "钢筋t", "型钢/钢管t", "模板m²", "防腐防火m²",
                "结构占用面积m²", "造价元", "相对%s造价%%" % base,
                "相对%s占用%%" % base]
    s6 = [tot_head]
    for t in types:
        i = len(s6) + 1
        o = T[t]
        rc = T[base]
        rec = [t]
        for c, key in zip("DEFGHI", ("conc", "rebar", "steel", "form", "fire", "occ")):
            rec.append(("f", "=SUMIF('标准层代表楼层'!$A:$A,$A%d,'标准层代表楼层'!$%s:$%s)"
                        % (i, c, c), o[key]))
        rec.append(("f", "=SUMIF('标准层代表楼层'!$A:$A,$A%d,'标准层代表楼层'!$J:$J)" % i, o["cost"]))
        rec.append(("f", "=$H%d/$H$2-1" % i, o["cost"] / rc["cost"] - 1))
        rec.append(("f", "=$G%d/$G$2-1" % i, o["occ"] / rc["occ"] - 1))
        s6.append(rec)

    # ---- 8 投入产出比
    s7 = [["柱型", "造价元", "相对%s造价%%" % base, "结构占用面积m²",
           "相对%s占用%%" % base, "换回楼面面积m²", "造价增量元", "投入产出比元/m²", "说明"]]
    rc = T[base]
    for idx, t in enumerate(types):
        i = len(s7) + 1
        o = T[t]
        d_occ, d_cost = rc["occ"] - o["occ"], o["cost"] - rc["cost"]
        s7.append([t,
                   ("f", "='%s'!$H$%d" % (TOTAL_SHEET, 1 + idx), o["cost"]),
                   ("f", "=$B%d/$B$2-1" % i, o["cost"] / rc["cost"] - 1),
                   ("f", "='%s'!$G$%d" % (TOTAL_SHEET, 1 + idx), o["occ"]),
                   ("f", "=$D%d/$D$2-1" % i, o["occ"] / rc["occ"] - 1),
                   ("f", "=$D$2-$D%d" % i, d_occ),
                   ("f", "=$B%d-$B$2" % i, d_cost),
                   ("f", ('="--"' if abs(d_occ) < 1e-9 else "=$G%d/$F%d" % (i, i)),
                    0.0 if abs(d_occ) < 1e-9 else d_cost / d_occ),
                   "投入产出比 = 相对%s造价增量 ÷ 换回的楼面面积(结构占用面积减少量)"
                   % base if idx else "基准"])

    # ---- 0 说明
    note = [["项目", scheme.get("project", "")],
            ["统计范围", "标准层 %s 的 %d 根框架柱，共 %d 条柱段记录"
             % ("/".join(str(s) for s in stds), sum(len(v) for v in scheme["groups"].values()),
                nrow)],
            ["标准层→自然层",
             "；".join("标准层%s→%d个自然层(定义层高%.0fmm, 实际层高 %s)"
                      % (s, n_floors(scheme["std_floors"][str(s)]),
                         scheme["std_floors"][str(s)]["height_mm"],
                         "+".join("%g" % h for h in nat_heights(scheme["std_floors"][str(s)])))
                      for s in stds)],
            ["归并组", "；".join("%s{%s}" % (k, ",".join(str(c) for c in v))
                                for k, v in scheme["groups"].items())],
            ["对比基准柱型", base],
            ["结构占用面积", "圆钢管混凝土柱 = π/4×(钢管外径+2×%.0fmm防火涂料)²；其余柱型 = 柱截面外轮廓面积" % FIRE_T],
            ["混凝土量", "矩形/型钢/叠合柱按全截面×层高；圆钢管混凝土柱按管内净面积×层高"],
            ["钢筋量", "(纵筋率+体积配箍率)×结构占用面积×层高×%.2f t/m³；圆钢管混凝土柱不配钢筋" % RHO],
            ["型钢/钢管量", "钢材截面面积×层高×%.2f t/m³（十字型钢 4ft+2dt−t²；钢管 π/4(D²−Din²)）" % RHO],
            ["模板量", "柱周长×层高；圆钢管混凝土柱钢管兼作模板，不另计"],
            ["防腐防火", "圆钢管混凝土柱按含防火涂层的钢管外表面 π(D+2a)×层高；其余柱型外包混凝土，不另计"],
            ["公式说明", "本表所有数量/造价/投入产出比均为 Excel 公式，改“单价与假定”或“截面参数”即自动重算"],
            ["造价口径", "方案阶段综合单价(含材料+制作安装, 不含税)，不含基础、节点加劲与吊装措施费"],
            ["生成时间", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")]]

    sheets = [("说明", note), ("单价与假定", s1), ("截面参数", s2), ("层高", s3),
              ("各标准层分组截面", s8), ("标准层一层", s_one),
              ("标准层代表楼层", s_rep), (TOTAL_SHEET, s6), ("投入产出比", s7)]
    write_wb(out_path, sheets)
    return {"rows": nrow, "totals": T, "io": s7, "sections": s2, "out": out_path}
