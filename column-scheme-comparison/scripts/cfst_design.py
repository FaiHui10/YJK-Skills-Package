# -*- coding: utf-8 -*-
"""GB 50936-2014《钢管混凝土结构技术规范》承载力计算库（钢管混凝土柱截面选型）。

设计目标
    承载力利用率 U = N / Nu ≤ target（用户指定 0.90）
    —— N = YJK 实算轴力设计值(kN)，Nu = 轴压稳定承载力设计值(kN)。
    —— 规范 4.2.3-2 对地震组合取 Sd ≤ Rd/γRE，γRE=0.80(稳定验算)，
       即规范本身允许 U ≤ 1/0.80 = 1.25；取 0.90 明显偏安全。

强制校核
    ① 轴力利用率 U_ax = N/Nu                     ≤ target
    ①' 压弯综合利用率 式(5.3.1-4)/(5.3.1-5)      ≤ target ← 用户"承载力利用率≤0.9"按本条从严执行
    ② 矩形柱轴压比 式(4.3.10)                    ≤ 0.80（框架-核心筒 二级）
    ③ 套箍系数 θ ∈ [theta_min, 2.0]  GB 50936 4.3.2（宜 0.5~2.0）
    ④ 壁厚 ≥ 6mm（4.3.1）；圆管 D/t ≤ 100、方管 b/t ≤ 60（常用构造）

★ 圆管口径（易踩的坑）
    shape="circle" 且**未给** D_mm 时，外径按「等外轮廓面积圆」D = √(4bh/π) 取，
    与「指定外径」是两个不同截面：600×600 默认得到 D=677.0 而不是 φ600
    （As 33226.9 / Nu 17670.1 vs φ600 的 29355.0 / 14517.5，差 13% / 22%）。
    此时 analyse() 会打印一行口径提示，返回结果的 口径 / D_source 字段标明口径，
    thinnest() 同样标注。要按指定外径计算，必须显式传 D_mm。

公式（已逐条比对 refs/GB50936.pdf 原文）
    N0  = Asc·fsc                                            (5.1.2-1)
    fsc = (1.212 + Bθ + Cθ²)·fc ; θ = αsc·fy/fc ; αsc = As/Asc (5.1.2-2~4)
    Nu  = φ·N0                                               (5.1.10-1)
    φ   = 1/(2λ̄sc²)·[(λ̄sc²+1+0.25λ̄sc) − √((λ̄sc²+1+0.25λ̄sc)² − 4λ̄sc²)] (5.1.10-2)
    λ̄sc = 0.01·λsc·(0.001fy + 0.781)                          (5.1.10-3；与表5.1.10逐点复核)
    Mu  = γm·Wsc·fsc ; Wsc = πr0³/4 ; r0 = √(Asc/π)           (5.1.6-1~2)
    γm  = 1.2（圆形）；γm = −0.483θ + 1.926√θ（其他截面）        (5.1.6-3 + 符号说明)
    Esc = 1.3·kE·fsc ; N'E = 11.6·kE·fsc·Asc/λsc²             (5.1.7-2, 5.3.1-3)

形状系数（表5.1.2，实心；矩形按等效正方形 √(b·h)）
    圆形/正十六边形  B = 0.176fy/213+0.974  C = −0.104fc/14.4+0.031
    正八边形         B = 0.140fy/213+0.778  C = −0.070fc/14.4+0.026
    正方形           B = 0.131fy/213+0.723  C = −0.070fc/14.4+0.026
"""
import math

# ---------------------------------------------------------------- 材料
FY16 = {"Q235": 215.0, "Q345": 305.0, "Q355": 305.0, "Q390": 345.0, "Q420": 375.0}
FY40 = {"Q235": 205.0, "Q345": 295.0, "Q355": 295.0, "Q390": 330.0, "Q420": 355.0}
KE = {"Q235": 918.9, "Q345": 719.6, "Q355": 705.8, "Q390": 657.5, "Q420": 626.9}
# 混凝土轴心抗压强度设计值 fc (N/mm²)，GB 50010-2010 表4.1.4-1
FC = {"C30": 14.3, "C35": 16.7, "C40": 19.1, "C45": 21.1, "C50": 23.1,
      "C55": 25.3, "C60": 27.5, "C70": 31.8, "C80": 35.9}
EC = {"C30": 30000, "C35": 31500, "C40": 32500, "C45": 33500, "C50": 34500,
      "C55": 35500, "C60": 36000}
ES = 206000.0
RHO_STEEL = 7.85e-9          # t/mm³

DEFAULT_CFG = dict(steel="Q355", target=0.90, beta_m=1.0,
                   theta_min=0.50, theta_max=2.00,
                   t_min=6, t_max=40, t_step=2,
                   d_over_t_max=100.0, b_over_t_max=60.0,
                   u_axial_max_rect=0.80)


def fy_of(steel, t_mm):
    return (FY16 if t_mm <= 16 else FY40).get(steel, 305.0)


# ---------------------------------------------------------------- 几何
def geom(shape, b_mm, h_mm, t_mm, D_mm=None):
    """截面几何量（组合截面按纯几何计，与 GB 50936 附录A 一致）。

    shape="rect"  外轮廓 b×h 的矩形钢管，壁厚 t
    shape="circle" 外径 D（默认 √(4bh/π) 等外轮廓面积）、壁厚 t

    ★ 口径：shape="circle" 且未给 D_mm 时，D = √(4bh/π) 是「等外轮廓面积圆」，
      与「指定外径」是两个不同截面（600×600 → D=677 而不是 φ600）。
      返回值里的 D_source 标明口径："explicit"（显式给 D_mm）/ "equal_area"（等效面积圆）。
    """
    if shape == "circle":
        D_from = "explicit" if D_mm else "equal_area"
        D = float(D_mm) if D_mm else math.sqrt(4.0 * b_mm * h_mm / math.pi)
        Di = D - 2.0 * t_mm
        As = math.pi / 4.0 * (D * D - Di * Di)
        Ac = math.pi / 4.0 * Di * Di
        Ix = Iy = math.pi / 64.0 * D ** 4
        return dict(D=D, Di=Di, B_out=D, H_out=D, be=D, As=As, Ac=Ac,
                    Ix=Ix, Iy=Iy, perim_out=math.pi * D, aspect=1.0,
                    steel_perim=math.pi * (D - t_mm), D_source=D_from)
    As = b_mm * h_mm - (b_mm - 2.0 * t_mm) * (h_mm - 2.0 * t_mm)
    Ac = (b_mm - 2.0 * t_mm) * (h_mm - 2.0 * t_mm)
    Ix = (b_mm * h_mm ** 3 - (b_mm - 2.0 * t_mm) * (h_mm - 2.0 * t_mm) ** 3) / 12.0
    Iy = (h_mm * b_mm ** 3 - (h_mm - 2.0 * t_mm) * (b_mm - 2.0 * t_mm) ** 3) / 12.0
    return dict(D=None, Di=None, B_out=float(b_mm), H_out=float(h_mm),
                be=math.sqrt(float(b_mm) * float(h_mm)), As=As, Ac=Ac,
                Ix=Ix, Iy=Iy, perim_out=2.0 * (b_mm + h_mm),
                aspect=max(b_mm, h_mm) / min(b_mm, h_mm),
                steel_perim=2.0 * (b_mm + h_mm - 2.0 * t_mm), D_source=None)


def caliber_text(shape, g, b_mm, h_mm):
    """口径说明文字（写进 analyse 结果，便于下游/报告标注）。"""
    if shape != "circle":
        return None
    if g["D_source"] == "explicit":
        return "显式外径 φ%.1f mm（调用时给了 D_mm）" % g["D"]
    return "等效面积圆 D=%.1f mm＝√(4×%g×%g/π)，非指定外径" % (g["D"], b_mm, h_mm)


def warn_equal_area(b_mm, h_mm, D):
    """圆管未给 D_mm 时的醒目口径提示（只提示，不改变任何计算结果）。"""
    if b_mm == h_mm:
        hint = "若想要 φ%g 请显式传 D_mm=%g" % (b_mm, b_mm)
    else:
        hint = ("若要指定外径（例如按外轮廓短边 %g）请显式传 D_mm=%g"
                % (min(b_mm, h_mm), min(b_mm, h_mm)))
    print("[cfst_design] ★口径提示：shape=circle 未给 D_mm → 按「等外轮廓面积圆」"
          "D＝√(4×%g×%g/π)＝%.1f mm 计算；%s（当前结果不是 φ%g，As 与 Nu 会偏大）。"
          % (b_mm, h_mm, D, hint, b_mm))


def shape_BC(shape, fy, fc):
    """GB 50936-2014 表5.1.2（实心）截面形状系数 B、C。"""
    if shape == "circle":
        return 0.176 * fy / 213.0 + 0.974, -0.104 * fc / 14.4 + 0.031
    if shape == "octagon":
        return 0.140 * fy / 213.0 + 0.778, -0.070 * fc / 14.4 + 0.026
    return 0.131 * fy / 213.0 + 0.723, -0.070 * fc / 14.4 + 0.026


def stability(lam_bar):
    """式(5.1.10-2) 轴压稳定系数 φ。"""
    a = lam_bar ** 2 + 1.0 + 0.25 * lam_bar
    return (a - math.sqrt(max(a * a - 4.0 * lam_bar ** 2, 0.0))) / (2.0 * lam_bar ** 2)


# ---------------------------------------------------------------- 承载力
def analyse(shape, b_mm, h_mm, t_mm, grade, N_kN, M_kNm, l0x_mm, l0y_mm,
            cfg=None, D_mm=None, _warn=True):
    """给定截面与内力，输出全部承载力指标与利用率。

    ★ 圆管口径：shape="circle" 而 D_mm 为 None 时按「等外轮廓面积圆」
      D = √(4bh/π) 计算（600×600 → D=677，不是 φ600），此时会打印一行口径提示，
      结果里 口径 / D_source 两个字段标明所用口径；显式给 D_mm 时行为与以前完全一致。
      _warn=False 供本模块 thinnest() 内部批量调用时抑制重复提示（私有参数）。
    """
    cfg = dict(DEFAULT_CFG, **(cfg or {}))
    steel = cfg["steel"]
    g = geom(shape, b_mm, h_mm, t_mm, D_mm)
    if shape == "circle" and g["D_source"] == "equal_area" and _warn:
        warn_equal_area(b_mm, h_mm, g["D"])
    As, Ac = g["As"], g["Ac"]
    Asc = As + Ac
    fy, fc_ = fy_of(steel, t_mm), FC[grade]
    alpha = As / Asc
    theta = alpha * fy / fc_
    B, C = shape_BC(shape, fy, fc_)
    fsc = (1.212 + B * theta + C * theta * theta) * fc_
    N0 = Asc * fsc
    if shape == "circle":
        ix = iy = g["D"] / 4.0
    else:
        ix, iy = math.sqrt(g["Ix"] / Asc), math.sqrt(g["Iy"] / Asc)
    lamx, lamy = l0x_mm / ix, l0y_mm / iy
    lams = max(lamx, lamy)
    lam_bar = 0.01 * lams * (0.001 * fy + 0.781)
    phi = stability(lam_bar)
    Nu = phi * N0
    r0 = math.sqrt(Asc / math.pi)
    Wsc = math.pi * r0 ** 3 / 4.0
    gm = 1.2 if shape == "circle" else -0.483 * theta + 1.926 * math.sqrt(theta)
    Mu = gm * Wsc * fsc
    Esc = 1.3 * KE[steel] * fsc
    NE = math.pi ** 2 * Esc * Asc / (1.1 * lams ** 2)
    N = abs(N_kN) * 1000.0
    M = abs(M_kNm) * 1e6
    U_ax = N / Nu
    denom = max(1.0 - 0.4 * N / NE, 0.05)
    if U_ax >= 0.255:
        U_NM = U_ax + cfg["beta_m"] * M / (1.5 * Mu * denom)
        nm_branch = 1
    else:
        U_NM = -N / (2.17 * Nu) + cfg["beta_m"] * M / (Mu * denom)
        nm_branch = 2
    return dict(
        shape=shape, t=t_mm, D=g["D"], Di=g["Di"], B_out=g["B_out"], H_out=g["H_out"],
        D_source=g["D_source"], 口径=caliber_text(shape, g, b_mm, h_mm),
        be=g["be"], aspect=g["aspect"], perim_out_m=g["perim_out"] / 1000.0,
        steel_perim_m=g["steel_perim"] / 1000.0,
        As=As, Ac=Ac, Asc=Asc, alpha=alpha, theta=theta, B=B, C=C,
        fsc=fsc, N0_kN=N0 / 1000.0, lam_sc=lams, lam_bar=lam_bar, phi=phi,
        Nu_kN=Nu / 1000.0, Mu_kNm=Mu / 1e6, gm=gm, NE_kN=NE / 1000.0,
        Esc=Esc, U_ax=U_ax, U_NM=U_NM, nm_branch=nm_branch,
        u_axial_rect=N / (fc_ * Ac + fy * As), i_min=min(ix, iy),
        D_over_t=(g["B_out"] / t_mm), grade=grade, fc=fc_, fy=fy,
    )


def ch6_circle(D, t_mm, grade, N_kN, M_kNm, l0_mm, steel="Q355"):
    """GB 50936-2014 第6章 实心圆形钢管混凝土轴压承载力（参考校核，非控制）。"""
    rc = (D - 2.0 * t_mm) / 2.0
    Ac = math.pi * rc ** 2
    As = math.pi / 4.0 * (D ** 2 - (D - 2.0 * t_mm) ** 2)
    fy, fc_ = fy_of(steel, t_mm), FC[grade]
    theta = As * fy / (Ac * fc_)
    alpha = 2.00 if grade in ("C30", "C35", "C40", "C45", "C50") else 1.80
    if theta <= 1.0 / (alpha - 1.0) ** 2:
        N0c = 0.9 * Ac * fc_ * (1.0 + theta)
    else:
        N0c = 0.9 * Ac * fc_ * (1.0 + math.sqrt(theta) + theta)
    N = abs(N_kN) * 1000.0
    e_over = (abs(M_kNm) * 1e6 / N) / rc if N else 0.0
    phie = 1.0 / (1.0 + 1.85 * e_over) if e_over <= 1.55 else \
        3.92 - 5.16 / (1.0 + 1.85 * e_over)
    k = (1.0 - 0.625 * e_over) if e_over <= 0.8 else 0.5
    r_d = k * l0_mm / D
    phil = 1.0 if r_d <= 4.0 else (1.0 - 0.0226 * (r_d - 4.0) if r_d <= 30.0
                                   else 1.0 - 0.115 * math.sqrt(r_d - 4.0))
    phil = max(phil, 0.0)
    Nu = phie * phil * N0c
    return dict(theta=theta, N0_kN=N0c / 1000.0, phie=phie, phil=phil,
                Le_m=k * l0_mm / 1000.0, Le_over_D=r_d, Nu_kN=Nu / 1000.0,
                U=N / Nu if Nu else None)


# ---------------------------------------------------------------- 约束判定
def check(st, cfg=None):
    """返回 (是否满足全部约束, {约束名: 是否通过})。"""
    cfg = dict(DEFAULT_CFG, **(cfg or {}))
    c = {
        "轴力利用率≤%.2f" % cfg["target"]: st["U_ax"] <= cfg["target"] + 1e-9,
        # 用户要求"承载力利用率 0.9 以内"，对压弯综合利用率同样从严按 target 控制
        "压弯利用率≤%.2f" % cfg["target"]: st["U_NM"] <= cfg["target"] + 1e-9,
        "θ≥%.2f" % cfg["theta_min"]: st["theta"] >= cfg["theta_min"] - 1e-9,
        "θ≤%.2f" % cfg["theta_max"]: st["theta"] <= cfg["theta_max"] + 1e-9,
        "壁厚≥%dmm" % cfg["t_min"]: st["t"] >= cfg["t_min"],
        "D/t≤%.0f" % cfg["d_over_t_max"]: st["D_over_t"] <= cfg["d_over_t_max"] + 1e-9,
    }
    if st["shape"] == "rect":
        c["轴压比≤%.2f" % cfg["u_axial_max_rect"]] = \
            st["u_axial_rect"] <= cfg["u_axial_max_rect"] + 1e-9
        c["b/t≤%.0f" % cfg["b_over_t_max"]] = \
            (min(st["B_out"], st["H_out"]) / st["t"]) <= cfg["b_over_t_max"] + 1e-9
    return all(c.values()), c


def thinnest(shape, b_mm, h_mm, grade, N_kN, M_kNm, l0x_mm, l0y_mm,
             cfg=None, D_mm=None):
    """返回满足全部约束的最小壁厚及截面指标 (t, st)；无解返回 (None, None)。

    ★ 圆管口径：shape="circle" 且 D_mm 为 None 时，全程按「等外轮廓面积圆」
      D = √(4bh/π) 选型（600×600 → D=677，不是 φ600），函数会打印一次口径提示，
      并在选中壁厚后打印实际选型口径；返回的 st 里 口径 / D_source 标明所用口径。
      显式给 D_mm 时行为与以前完全一致（不打提示、按指定外径选型）。
    """
    cfg = dict(DEFAULT_CFG, **(cfg or {}))
    ea_warn = (shape == "circle" and not D_mm)
    found = None
    for t in range(cfg["t_min"], cfg["t_max"] + 1, cfg["t_step"]):
        st = analyse(shape, b_mm, h_mm, t, grade, N_kN, M_kNm, l0x_mm, l0y_mm,
                     cfg, D_mm, _warn=False)
        ok, _ = check(st, cfg)
        if ok:
            found = (t, st)
            break
    if ea_warn:
        warn_equal_area(b_mm, h_mm, math.sqrt(4.0 * b_mm * h_mm / math.pi))
    if found is None:
        return None, None
    t, st = found
    if shape == "circle":
        print("[cfst_design] thinnest 选型口径：%s → t=%d mm" % (st["口径"], t))
    return t, st
