# -*- coding: utf-8 -*-
"""柱截面形式造价模型：钢筋混凝土柱 vs 矩形钢管混凝土柱 vs 圆钢管混凝土柱。

计价依据（广州地区）
  广东省房屋建筑与装饰工程综合定额(2018) —— 见 gz_quota.py（定额编号/基价/人工/材料/机具）
  广州市 2026年6月 建设工程常用材料税前综合价格（穗建造价〔2026〕62号）
  管理费分摊费率：混凝土及钢筋混凝土 28.75% / 模板 26.35% / 金属结构 28.94% / 油漆涂料 15.07%
  利润：(人工费+施工机具费)×20%       增值税：9%

工程量口径（三方案完全相同，仅形式不同）
  · 柱段按「自然层」分段，共 480 段（30 层 ×16 柱），层高取 tblFloor.Height（与 wmass.out 一致）
  · RC：混凝土按全截面 b×h；纵筋按 YJK 实配 As；箍筋按 Rsv×核心区体积；
        模板按柱周长选子目 + 支模超过3.6m 每增1m 叠加
  · CFST：钢管按 As×段长（钢板信息价×(1+下料损耗)+制作加工费，另加节点附件系数）；
        管内混凝土按钢管内径面积×段长；防火涂料按外表面展开面积；
        套用「超高层钢结构钢柱安装」子目，按每根构件质量选档

估值/估算项（已在报告中标注）
  · 节点板、加强环、内衬管、牛腿按 GB 50936 工程量规则并入钢管柱质量 → 附件系数 1.08
  · 钢材制作加工费取市场行情（无缝/焊接钢管柱 1300 元/t），敏感性 1100~1600
  · 防火涂料按一级耐火等级柱 3.0h 选子目（厚型H 30mm），CFST 专项方案敏感性另计

用法
  python cost_model.py [--data <柱设计数据.json>] [--out <造价对比.json>]
  输入/输出默认都在**当前工作目录**（--data 在当前工作目录找不到时回退脚本目录），
  不再写进技能包自身的 scripts/ 目录。
"""
import argparse
import json
import math
import os
import sys

import cfst_design as C
import gz_quota as G

ROOT = os.path.dirname(os.path.abspath(__file__))

# ------------------------------------------------------------------ 参数
P = dict(
    attach=1.08,          # 钢管节点附件系数（加强环/内衬管/牛腿/节点板并入钢管质量）
    fab_cost=1300.0,      # 钢管柱制作加工费 元/t（市场行情，含除锈、车间底漆）
    tube_loss=0.05,       # 钢板下料损耗
    fire_code="A1-15-135",  # 金属面厚型H防火涂料 3.0h(30mm)
    rebar_long="A1-5-106",   # 柱纵筋 Φ25以内
    rebar_stir="A1-5-105",   # 箍筋 Φ10以内
    rebar_spec_long="Φ12-25",
    rebar_spec_stir="Φ10内",
    theta_min=0.50,
    target=0.90,
    conc_pump=True,
    labor_index=1.0,
    steel="Q355",
    collect=None,
)


def pricer(p):
    return G.Pricer(labor_index=p["labor_index"], conc_pump=p["conc_pump"])


def _fire_unit(pr, p):
    """防火涂料 元/m²（除税）；fire_code=None/'NONE' 表示不计。"""
    fc = p.get("fire_code")
    if not fc or fc == "NONE":
        return 0.0
    return pr.fire_unit(fc)[0]


# ------------------------------------------------------------------ RC
def rc_scheme(rows, p):
    """钢筋混凝土柱方案造价（除税）。"""
    pr = pricer(p)
    tot = dict(conc=0.0, rebar_l=0.0, rebar_s=0.0, form=0.0)
    qty = dict(V=0.0, Wl=0.0, Ws=0.0, A=0.0)
    detail = []
    for r in rows:
        b, h, L, cov = r["b"], r["h"], r["层高_m"], r["cover"]
        grade = r["混凝土"]
        V = r["V_con_m3"]
        conc_u = pr.conc_unit(grade)[0]
        # 纵筋：As(mm²) × 段长
        wl = r["Ast"] / 1e6 * L * 7.85
        if r["Rsv"] and r["Rsv"] > 0:
            acore = (b - 2 * cov) * (h - 2 * cov) / 1e6
            ws = r["Rsv"] / 100.0 * acore * L * 7.85
        else:
            ws = 0.0
        A = r["A_form_m2"]
        perim = r["perim_mm"] / 1000.0
        form_u = pr.form_unit(perim, L)[0]
        rl_u = pr.rebar_unit(p["rebar_long"], p["rebar_spec_long"])[0]
        rs_u = pr.rebar_unit(p["rebar_stir"], p["rebar_spec_stir"])[0]
        c = dict(conc=V * conc_u, rebar_l=wl * rl_u, rebar_s=ws * rs_u,
                 form=A * form_u)
        for k in tot:
            tot[k] += c[k]
        qty["V"] += V; qty["Wl"] += wl; qty["Ws"] += ws; qty["A"] += A
        detail.append(dict(自然层=r["自然层"], 标准层=r["标准层"], 柱号=r["柱号"], 组=r["组"],
                           形式="RC", b=b, h=h, 等级=grade, 层高=L,
                           V_m3=round(V, 4), 纵筋_t=round(wl, 4), 箍筋_t=round(ws, 4),
                           模板_m2=round(A, 3), 造价=round(sum(c.values()), 1)))
    tot["base"] = sum(tot.values())
    tot["vat"] = tot["base"] * (1 + G.VAT)
    return dict(名称="S1 钢筋混凝土柱（现状R2优化方案）", 汇总=tot, 工程量=qty, 明细=detail)


# ------------------------------------------------------------------ CFST
def _envelope(segs):
    return dict(
        b=segs[0]["b"], h=segs[0]["h"], grade=segs[0]["混凝土"],
        N=max(abs(r["Nu"]) for r in segs),
        M=max(r["Mmax"] for r in segs),
        L0x=max(r["L0x_m"] for r in segs) * 1000.0,
        L0y=max(r["L0y_m"] for r in segs) * 1000.0,
    )


def size_group(kind, env, p, D_mode="fixed"):
    """为一个设计点(标准层×组)选截面；D_mode='optimal' 时按单方造价最小扫描外轮廓。

    D_mode:
      fixed      矩形——沿用原柱外轮廓 b×h
      equal_area 圆形——外径 D=√(4bh/π)（与原柱等外轮廓面积）
      optimal    扫描外轮廓取「单位长度造价」最低（圆形扫 D 400~2400@25；
                 矩形保持原柱长宽比扫等效短边 400~1800@50）
    """
    cfg = dict(C.DEFAULT_CFG, steel=p["steel"], target=p["target"],
               theta_min=p["theta_min"])
    b, h, grade = env["b"], env["h"], env["grade"]
    args = (env["N"], env["M"], env["L0x"], env["L0y"])
    if D_mode != "optimal":
        D = None
        if kind == "circle" and D_mode == "equal_area":
            D = math.sqrt(4.0 * b * h / math.pi)
        t, st = C.thinnest(kind, b, h, grade, *args, cfg=cfg, D_mm=D)
        if t is None:
            raise SystemExit("无解 %s %s D=%s" % (kind, env, D))
        return t, st
    # 扫描外轮廓，取「单位长度造价」最低者
    pr = pricer(p)
    best = None
    if kind == "circle":
        cand = [(D, D) for D in _frange(400.0, 2400.0, 25.0)]
    else:
        ar = float(max(b, h)) / float(min(b, h))    # 保持原柱长宽比
        cand = [(round(s), round(s * ar)) for s in _frange(400.0, 1800.0, 50.0)]
    for bb, hh in cand:
        D = bb if kind == "circle" else None
        t, st = C.thinnest(kind, bb, hh, grade, *args, cfg=cfg, D_mm=D)
        if t is not None:
            cost = _cfst_unit_cost(st, grade, 1.0, p, pr)   # 每米造价
            if best is None or cost < best[2]:
                best = (t, st, cost)
    if best is None:
        raise SystemExit("%s 无解 %s" % (kind, env))
    return best[0], best[1]


def _frange(a, b, step):
    out, x = [], a
    while x <= b + 1e-9:
        out.append(x)
        x += step
    return out


def _cfst_unit_cost(st, grade, L_m, p, pr):
    """一根柱段（长 L_m）的 CFST 造价（除税）。"""
    As, Ac, t = st["As"], st["Ac"], st["t"]
    w_tube = As / 1e6 * L_m * 7.85
    w_tot = w_tube * p["attach"]
    mat_u = G.plate_price(t) * (1 + p["tube_loss"]) + p["fab_cost"]
    _, erect_u, _ = pr.steel_erect_unit(w_tot * 1000.0)
    conc_u = pr.conc_unit(grade)[0]
    fire_u = _fire_unit(pr, p)
    return (w_tot * mat_u + w_tot * erect_u + Ac / 1e6 * L_m * conc_u
            + st["perim_out_m"] * L_m * fire_u)


def cfst_scheme(rows, p, kind, D_mode, name):
    pr = pricer(p)
    groups = sorted({(r["标准层"], r["组"]) for r in rows})
    sec_of = {}
    for g in groups:
        segs = [r for r in rows if r["标准层"] == g[0] and r["组"] == g[1]]
        env = _envelope(segs)
        t, st = size_group(kind, env, p, D_mode)
        st = dict(st); st["控制"] = "N=%.0f kN, M=%.0f kN·m, 段数=%d" % (env["N"], env["M"], len(segs))
        st["env"] = env
        sec_of[g] = st

    tot = dict(tube_mat=0.0, tube_erect=0.0, conc=0.0, fire=0.0)
    qty = dict(W=0.0, V=0.0, A=0.0)
    detail = []
    for r in rows:
        st = sec_of[(r["标准层"], r["组"])]
        L = r["层高_m"]
        t = st["t"]
        w_tube = st["As"] / 1e6 * L * 7.85
        w_tot = w_tube * p["attach"]
        mat_u = G.plate_price(t) * (1 + p["tube_loss"]) + p["fab_cost"]
        _, erect_u, _ = pr.steel_erect_unit(w_tot * 1000.0)
        conc_u = pr.conc_unit(r["混凝土"])[0]
        fire_u = _fire_unit(pr, p)
        V = st["Ac"] / 1e6 * L
        A = st["perim_out_m"] * L
        c = dict(tube_mat=w_tot * mat_u, tube_erect=w_tot * erect_u,
                 conc=V * conc_u, fire=A * fire_u)
        for k in tot:
            tot[k] += c[k]
        qty["W"] += w_tot; qty["V"] += V; qty["A"] += A
        detail.append(dict(自然层=r["自然层"], 标准层=r["标准层"], 柱号=r["柱号"], 组=r["组"],
                           形式=kind, t=t,
                           外轮廓=("%.0f" % st["D"]) if kind == "circle" else
                           ("%d×%d" % (st["B_out"], st["H_out"])),
                           等级=r["混凝土"], 层高=L, theta=round(st["theta"], 3),
                           U=round(st["U_ax"], 3),
                           钢管_t=round(w_tot, 4), 管内砼_m3=round(V, 4),
                           外表面积_m2=round(A, 3), 造价=round(sum(c.values()), 1)))
    tot["base"] = sum(tot.values())
    tot["vat"] = tot["base"] * (1 + G.VAT)
    secs = []
    for g in groups:
        st = sec_of[g]
        secs.append(dict(标准层=g[0], 组=g[1], t=st["t"],
                         D=(round(st["D"], 1) if st["D"] else None),
                         外轮廓=("%.0f" % st["D"]) if kind == "circle" else
                         ("%d×%d" % (st["B_out"], st["H_out"])),
                         D_over_t=round(st["D_over_t"], 1),
                         As=round(st["As"]), Ac=round(st["Ac"]),
                         alpha=round(st["alpha"], 4), theta=round(st["theta"], 3),
                         fsc=round(st["fsc"], 2), phi=round(st["phi"], 4),
                         Nu_kN=round(st["Nu_kN"], 1), N_kN=st["env"]["N"],
                         M_kNm=st["env"]["M"], U_ax=round(st["U_ax"], 3),
                         U_NM=round(st["U_NM"], 3),
                         轴压比=round(st["u_axial_rect"], 3),
                         lam_sc=round(st["lam_sc"], 2), 控制=st["控制"]))
    return dict(名称=name, 汇总=tot, 工程量=qty, 截面表=secs, 明细=detail)


# ------------------------------------------------------------------ 敏感性
def _totals(rows, patches):
    """按给定参数补丁重算 S1 / S2 / S4 / S6，返回四者除税合计（元）。"""
    p = dict(P)
    G.PLATE_F = 1.0
    for k, v in patches.items():
        if k == "plate_f":
            G.PLATE_F = v
        else:
            p[k] = v
    try:
        s1 = rc_scheme(rows, p)["汇总"]["base"]
        s2 = cfst_scheme(rows, p, "rect", "fixed", "S2")["汇总"]["base"]
        s4 = cfst_scheme(rows, p, "circle", "optimal", "S4")["汇总"]["base"]
        s6 = cfst_scheme(rows, p, "rect", "optimal", "S6")["汇总"]["base"]
    finally:
        G.PLATE_F = 1.0
    return s1, s2, s4, s6


def sensitivity(rows):
    """多组价格/取值假设下的除税合计对比。"""
    cases = [
        ("价格与构造", [
            ("基准：θ≥0.5 / 钢板信息价 / 加工费1300元/t", {}),
            ("钢板价格 −20%", dict(plate_f=0.80)),
            ("钢板价格 −10%", dict(plate_f=0.90)),
            ("钢板价格 +10%", dict(plate_f=1.10)),
            ("钢板价格 +20%", dict(plate_f=1.20)),
            ("制作加工费 1100 元/t", dict(fab_cost=1100.0)),
            ("制作加工费 1600 元/t", dict(fab_cost=1600.0)),
            ("节点附件系数 1.00（不计加强环/牛腿等）", dict(attach=1.00)),
            ("节点附件系数 1.15", dict(attach=1.15)),
        ]),
        ("防火涂料子目", [
            ("超薄型CB 2.0h(2.5mm) A1-15-128", dict(fire_code="A1-15-128")),
            ("薄型B 2.0h(5.5mm) A1-15-131", dict(fire_code="A1-15-131")),
            ("厚型H 2.0h(20mm) A1-15-133", dict(fire_code="A1-15-133")),
            ("不计防火涂料（假设由建筑包覆解决）", dict(fire_code=None)),
        ]),
        ("套箍系数 θ", [
            ("不限 θ（仅承载力控制，理论下限）", dict(theta_min=0.0)),
            ("θ≥0.70（套箍更充分）", dict(theta_min=0.70)),
        ]),
        ("目标利用率", [
            ("目标利用率 0.80", dict(target=0.80)),
            ("目标利用率 0.85", dict(target=0.85)),
            ("目标利用率 1.00（=规范 γRE=0.80 对应上限）", dict(target=1.00)),
        ]),
        ("取费口径", [
            ("混凝土按非泵送信息价", dict(conc_pump=False)),
            ("人工费×穗建造价〔2026〕62号指数 109.13%", dict(labor_index=G.LABOR_INDEX)),
        ]),
    ]
    out = []
    for gname, vs in cases:
        for label, pa in vs:
            if pa.get("fire_code", "x") is None:
                pa = dict(pa)
                pa["fire_code"] = "NONE"
            s1, s2, s4, s6 = _totals(rows, pa)
            out.append(dict(类别=gname, 情形=label,
                            S1_万元=round(s1 / 1e4, 1),
                            S2_万元=round(s2 / 1e4, 1),
                            S4_万元=round(s4 / 1e4, 1),
                            S6_万元=round(s6 / 1e4, 1),
                            S4相对S1=round(s4 / s1 - 1.0, 4),
                            S6相对S1=round(s6 / s1 - 1.0, 4)))
    return out


# ------------------------------------------------------------------ 主流程
def _resolve_input(explicit, name):
    """输入 JSON 的解析顺序：显式路径 > 当前工作目录 > 脚本所在目录。"""
    if explicit:
        return explicit
    cwd_p = os.path.join(os.getcwd(), name)
    if os.path.exists(cwd_p):
        return cwd_p
    return os.path.join(ROOT, name)


def _utf8_console():
    """让输出在任何控制台编码下都不崩（GBK 下把不可编码字符替换掉）。

    为什么需要：本文件与它调用的 cfst_design.py 会打印 m³、m² 等非 cp936 字符，
    默认 GBK 控制台下 `print` 会抛 UnicodeEncodeError 并以非零退出码中断 ——
    JSON 其实已经写出，命令却以失败收场。`errors="replace"` 让它在 UTF-8 控制台下
    原样输出、在 GBK 下退化成 `?`，都不崩。

    只在 main() 开头调用一次，不在 import 时改 stdout（本模块会被别的脚本 import 当库用）。
    """
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass


def main():
    _utf8_console()          # 必须在 argparse 之前：--help 也写到 stdout
    # 用法: python cost_model.py [--data 柱设计数据.json] [--out 造价对比.json]
    # 默认从当前工作目录读输入、写到当前工作目录，不再写进技能包自身的 scripts/ 目录
    ap = argparse.ArgumentParser(description="柱截面形式造价模型（RC vs 矩形/圆形钢管混凝土）")
    ap.add_argument("--data", default=None,
                    help="输入 柱设计数据.json 路径；默认取当前工作目录下的同名文件，"
                         "找不到时回退脚本所在目录")
    ap.add_argument("--out", default=None,
                    help="输出 造价对比.json 路径；默认写到当前工作目录")
    a = ap.parse_args()
    data_path = _resolve_input(a.data, "柱设计数据.json")
    out_path = a.out or os.path.join(os.getcwd(), "造价对比.json")
    print("读入：%s" % data_path)
    src = json.load(open(data_path, encoding="utf-8"))
    rows = src["rows"]

    schemes = {}
    schemes["S1"] = rc_scheme(rows, P)
    variants = [
        ("S2", "rect", "fixed", "S2 矩形钢管混凝土柱（外轮廓=原柱 b×h）"),
        ("S3", "circle", "equal_area", "S3 圆钢管混凝土柱（等外轮廓面积 D=√(4bh/π)）"),
        ("S4", "circle", "optimal", "S4 圆钢管混凝土柱（外径造价最优选型）"),
        ("S6", "rect", "optimal", "S6 矩形钢管混凝土柱（边长造价最优选型）"),
    ]
    for k, kind, dm, nm in variants:
        schemes[k] = cfst_scheme(rows, P, kind, dm, nm)
    # S5：理论下限（不限套箍系数 θ，仅满足利用率≤0.9 与压弯≤1.0）
    schemes["S5"] = cfst_scheme(rows, dict(P, theta_min=0.0), "circle", "optimal",
                                "S5 圆钢管混凝土柱（不限θ，理论下限）")

    sens = sensitivity(rows)
    out = dict(参数=P, 敏感性=sens,
               方案={k: {kk: vv for kk, vv in v.items() if kk != "明细"}
                    for k, v in schemes.items()},
               明细={k: v["明细"] for k, v in schemes.items()})
    json.dump(out, open(out_path, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    print("=" * 122)
    print("柱截面形式造价对比（广东省2018综合定额 + 广州市2026年6月信息价，除税综合单价，单位：万元）")
    print("=" * 122)
    order = ["S1", "S2", "S3", "S4", "S5", "S6"]
    names = {k: schemes[k]["名称"] for k in order}
    comp = [("conc", "混凝土"), ("tube_mat", "钢管材料"), ("tube_erect", "钢管安装"),
            ("rebar_l", "纵筋"), ("rebar_s", "箍筋"), ("fire", "防火涂料"), ("form", "模板")]
    print("方案".ljust(46) + "".join(c[1].rjust(11) for c in comp)
          + "除税合计".rjust(12) + "含税合计".rjust(12) + "相对S1".rjust(10))
    for k in order:
        t = schemes[k]["汇总"]
        line = names[k][:44].ljust(46)
        for key, _ in comp:
            line += ("%11.1f" % (t.get(key, 0.0) / 1e4))
        line += "%12.1f" % (t["base"] / 1e4)
        line += "%12.1f" % (t["vat"] / 1e4)
        line += "%10s" % ("%.0f%%" % (t["base"] / schemes["S1"]["汇总"]["base"] * 100))
        print(line)
    print("-" * 122)
    print("工程量：")
    q = schemes["S1"]["工程量"]
    print("  S1  RC  : 混凝土 %.1f m³  纵筋 %.1f t  箍筋 %.1f t  模板 %.1f m²"
          % (q["V"], q["Wl"], q["Ws"], q["A"]))
    for k in ("S2", "S3", "S4", "S5", "S6"):
        q = schemes[k]["工程量"]
        print("  %s %-4s: 钢管(含附件) %6.1f t  管内混凝土 %7.1f m³  防火展开面积 %7.1f m²"
              % (k, "矩形" if k in ("S2", "S6") else "圆形", q["W"], q["V"], q["A"]))
    print("\n敏感性分析（除税合计，万元）：")
    print("  " + "类别".ljust(12) + "情形".ljust(44) + "S1_RC".rjust(9)
          + "S2_矩形等轮廓".rjust(13) + "S6_矩形最优".rjust(12)
          + "S4_圆形最优".rjust(12) + "S4/S1".rjust(9))
    for s in sens:
        print("  %-10s %-42s %9.1f %13.1f %12.1f %12.1f %8.0f%%"
              % (s["类别"], s["情形"], s["S1_万元"], s["S2_万元"], s["S6_万元"],
                 s["S4_万元"], s["S4相对S1"] * 100))
    print("\n已写出 -> %s" % out_path)


if __name__ == "__main__":
    main()
