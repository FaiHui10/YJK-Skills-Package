# -*- coding: utf-8 -*-
"""结构柱截面设计用规范公式与限值库（单位统一：mm / N / N·mm² / kN）。

覆盖四种柱型
------------
1. 普通钢筋混凝土柱 RC          JGJ3-2010 6.4.2、GB50010
2. 加芯钢筋混凝土柱 RC-Core     JGJ3-2010 6.4.2 注 5
3. 型钢混凝土柱 SRC             JGJ3-2010 11.4.4 / 11.4.5
4. 钢管混凝土叠合柱 CFST-RC     CECS188-2019（叠合柱规程）
5. 圆钢管混凝土柱 CFST          CECS28 / JGJ138，含 YJK 验算口径反标定式

轴压比口径统一为
    Uc = Nu / (fc·Ac + fa·Aa)
其中 Ac 为混凝土截面面积、Aa 为型钢/钢管面积（RC 柱 Aa=0）。
"""
import math

# ---------------------------------------------------------------- 材料强度
FC = {  # 混凝土轴心抗压强度设计值 N/mm²（GB50010 表4.1.4-1）
    "C30": 14.3, "C35": 16.7, "C40": 19.1, "C45": 21.1, "C50": 23.1,
    "C55": 25.3, "C60": 27.5, "C65": 29.7, "C70": 31.8, "C75": 33.8, "C80": 35.9,
}
FT = {  # 轴心抗拉强度设计值，需要时用
    "C30": 1.43, "C35": 1.57, "C40": 1.71, "C45": 1.80, "C50": 1.89,
    "C55": 1.96, "C60": 2.04, "C65": 2.09, "C70": 2.14, "C75": 2.18, "C80": 2.22,
}


def fa_of(grade="Q355", t=None):
    """钢材抗压强度设计值 N/mm²（GB50017 表4.4.1）。t 为板厚 mm。"""
    g = grade.upper()
    if g == "Q235":
        return 215.0 if (t is None or t <= 16) else 205.0
    if g == "Q355":
        return 305.0 if (t is None or t <= 16) else 295.0
    if g == "Q390":
        return 345.0 if (t is None or t <= 16) else 330.0
    raise ValueError("未收录的钢号 %s" % grade)


def fc_of(grade):
    g = grade.upper()
    if g not in FC:
        raise ValueError("未收录的混凝土等级 %s（可选 %s）" % (grade, sorted(FC)))
    return FC[g]


def _rn(x, step=50.0):
    return int(math.ceil(x / step - 1e-9) * step)


# ---------------------------------------------------------------- 1/2 混凝土柱
# JGJ3-2010 表 6.4.2 柱轴压比限值
UC_RC_TABLE = {
    ("框架结构", 1): 0.65, ("框架结构", 2): 0.75, ("框架结构", 3): 0.85,
    ("框架-剪力墙/板柱-剪力墙/框架-核心筒/筒中筒", 1): 0.75,
    ("框架-剪力墙/板柱-剪力墙/框架-核心筒/筒中筒", 2): 0.85,
    ("框架-剪力墙/板柱-剪力墙/框架-核心筒/筒中筒", 3): 0.90,
    ("部分框支剪力墙", 1): 0.60, ("部分框支剪力墙", 2): 0.70,
}
UC_RC_MIN = 0.65          # 表 6.4.2 注 6 的最低要求
UC_ABS_MAX = 1.00         # 绝对上限：轴压比超过 1.0 已无物理意义


def uc_limit_rc(structure="框架-剪力墙/板柱-剪力墙/框架-核心筒/筒中筒", seismic=2,
                short_col=False, densify_hoop=False, core_column=False,
                core_ratio=0.0):
    """JGJ3-2010 6.4.2 轴压比限值（含各注的修正）。

    short_col    剪跨比不大于 2（短柱）          → −0.05           注4
    densify_hoop 沿柱全高采用井字复合箍等加密措施 → +0.10           注5
    core_column  加芯柱（芯柱截面≥柱面积的25%）  → +0.05           注5

    注5 原文是"采用下列措施**之一**"，严格说各项不宜叠加；本函数按可叠加处理
    （工程上常见做法），并以 UC_ABS_MAX 封顶。是否可叠加请以项目抗震审查意见为准。
    """
    base = UC_RC_TABLE.get((structure, seismic))
    if base is None:
        raise ValueError("查不到结构类型/抗震等级 = %s/%s" % (structure, seismic))
    lim = base
    if short_col:
        lim -= 0.05
    if densify_hoop:
        lim += 0.10
    if core_column:
        lim += 0.05 if core_ratio >= 0.25 else 0.0
    return min(max(lim, UC_RC_MIN), UC_ABS_MAX)


def design_rc(Nu_kN, fc, uc_lim, step=50.0):
    """矩形混凝土柱：定 A 求 b。返回 (b, A_required_mm2)。"""
    A = Nu_kN * 1000.0 / (uc_lim * fc)
    return _rn(math.sqrt(A), step), A


def uc_rc(Nu_kN, b, fc):
    return Nu_kN * 1000.0 / (fc * b * b)


# ---------------------------------------------------------------- 3 型钢混凝土柱
# JGJ3-2010 表 11.4.4 型钢混凝土柱轴压比限值
UC_SRC_TABLE = {1: 0.70, 2: 0.80, 3: 0.90}
SRC_COVER_MIN = 150.0        # 11.4.5-3 型钢表面至柱面 ≥150mm
SRC_ROA_MIN = 0.04           # 11.4.5-6 含钢率 ≥4%


def uc_limit_src(seismic=2, short_col=False, densify_hoop=False):
    """11.4.4 限值；剪跨比≤2 减 0.05；采用加密措施可 +0.10（同上表注）。"""
    lim = UC_SRC_TABLE[seismic]
    if short_col:
        lim -= 0.05
    if densify_hoop:
        lim += 0.10
    return lim


def aa_cross(f, t, d):
    """十字型钢截面积：4 片翼缘 f×t + 2 片腹板 d×t，扣重叠 t²。"""
    return 4.0 * f * t + 2.0 * d * t - t * t


def design_src(Nu_kN, fc, fa, uc_lim, roa=0.045, steel=None, family=None,
               cover=SRC_COVER_MIN, step=50.0):
    """型钢混凝土柱选型。

    Uc = Nu/(fc·Ac + fa·Aa)，Aa = ρ·A，Ac = A − Aa
       → A ≥ Nu / (uc_lim · (fc·(1−ρ) + fa·ρ))

    steel : 直接指定 (f, t, d)，全柱同一型钢
    family: 候选 [(f, t, d), …]，取满足 保护层≥cover 且 ρa∈[0.04,0.05] 的最小 b
    返回 dict(b, f, t, d, Aa, A, rhoa, Uc) 或 None
    """
    rho = roa
    A = Nu_kN * 1000.0 / (uc_lim * (fc * (1 - rho) + fa * rho))
    b = _rn(math.sqrt(A), step)
    if steel:
        fam = [tuple(steel)]
    elif family:
        fam = list(family)
    else:
        fam = _auto_src_family(b)          # 经验比例：f≈0.25b, d≈0.65b

    for _ in range(40):                    # 逐步加大柱截面直到有可用型钢
        for (f, t, d) in fam:
            if (b - max(f, d)) / 2.0 < cover:
                continue
            Aa = aa_cross(f, t, d)
            rhoa = Aa / (b * b)
            if not (SRC_ROA_MIN <= rhoa <= 0.05):
                continue
            uc = Nu_kN * 1000.0 / (fc * (b * b - Aa) + fa * Aa)
            if uc <= uc_lim:
                return dict(b=b, f=f, t=t, d=d, A=b * b, Aa=Aa, rhoa=rhoa, Uc=uc)
        b += step
    return None


def _auto_src_family(b, ts=(18, 20, 22, 25, 26, 28, 30, 32, 35, 36)):
    """经验比例生成候选十字型钢：翼缘宽≈0.25b、腹板高≈0.65b，板厚按标准档。"""
    f = _rn(b * 0.25)
    d = _rn(b * 0.65)
    return [(f, t, d) for t in ts]


# ---------------------------------------------------------------- 4 钢管混凝土叠合柱
UC_DIEHE = 0.85              # CECS188 4.2.14 管外轴压比限值
ROA_DIEHE_MIN = 0.03         # 4.2.13-4 含管率 ≥3%
THETA_DIEHE_MAX = 2.0        # 套箍指标上限（规程 3.0，工程上按 2.0 控更稳）
DT_DIEHE_MAX = 89.37         # 径厚比限值（Q355）
GAP_DEFAULT = 650.0          # 内管外径比柱截面小 650mm（方便梁筋绕过）


def design_diehe(Nu_kN, fc_out, fc_in, fa, gap=GAP_DEFAULT, gap_min=600.0, b_min=None,
                 uc_lim=UC_DIEHE, th_max=THETA_DIEHE_MAX, t_cap=36.0,
                 ts=(12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36),
                 step=50.0):
    """钢管混凝土叠合柱选型。

    约束（全部满足）：
        Uc  = Nu/(fc外·A + fa·Aa) ≤ uc_lim
        Roa = Aa/A ≥ 3%                      （4.2.13-4）
        θ   = fa·Aa/(fc内·Ac内) ≤ th_max
        D   = b − gap，gap 优先取 gap，取不到时逐级放宽到 gap_min（管外到柱边≥300mm）
        D/t ≤ 89.37

    搜索顺序：柱截面 b 从小到大，净距 gap 从大到小，壁厚从小到大，
    返回第一个可行组合（即"最小柱截面 + 尽可能大的净距"）。
    """
    b = _rn(b_min if b_min else math.sqrt(
        Nu_kN * 1000.0 / (uc_lim * (fc_out + fa * ROA_DIEHE_MIN))), step)
    gaps = []
    g = float(gap)
    while g >= gap_min - 1e-9:
        gaps.append(g)
        g -= step
    for _ in range(80):
        for gx in gaps:
            D = b - gx
            if D <= 100:
                continue
            for t in ts:
                if t > t_cap or D / t > DT_DIEHE_MAX:
                    continue
                Aa = math.pi / 4.0 * (D * D - (D - 2 * t) ** 2)
                A = b * b
                rhoa = Aa / A
                if rhoa < ROA_DIEHE_MIN:
                    continue
                Ac_in = math.pi / 4.0 * (D - 2 * t) ** 2
                theta = fa * Aa / (fc_in * Ac_in)
                if theta > th_max:
                    continue
                uc = Nu_kN * 1000.0 / (fc_out * A + fa * Aa)
                if uc <= uc_lim:
                    return dict(b=b, D=D, t=t, Aa=Aa, rhoa=rhoa, theta=theta, Uc=uc,
                                gap=b - D, 净距=(b - D) / 2.0)
        b += step
    return None


def check_diehe(Nu_kN, b, D, t, fc_out, fc_in, fa, uc_lim=UC_DIEHE):
    Aa = math.pi / 4.0 * (D * D - (D - 2 * t) ** 2)
    Ac_in = math.pi / 4.0 * (D - 2 * t) ** 2
    A = b * b
    return {"Uc": Nu_kN * 1000.0 / (fc_out * A + fa * Aa),
            "Roa": Aa / A,
            "theta": fa * Aa / (fc_in * Ac_in),
            "Dt": D / t,
            "净距mm": (b - D) / 2.0}


# ---------------------------------------------------------------- 5 圆钢管混凝土柱
def cfst_alpha(fc):
    """套箍提高系数：C55~C80 取 1.8，C50 及以下取 2.0。"""
    return 1.8 if fc >= FC["C55"] else 2.0


CFST_LAMBDA = {("C60", "Q355"): 0.9044, ("C55", "Q355"): 0.9073,
               ("C30", "Q235"): 0.9087, ("C60", "Q235"): 0.9044}


def cfst_geom(D, t):
    Ac = math.pi / 4.0 * (D - 2 * t) ** 2
    As = math.pi / 4.0 * (D * D - (D - 2 * t) ** 2)
    return Ac, As


def cfst_N0(D, t, fc, fa, alpha=None):
    """轴心受压承载力 N0（kN）。N0 = Ac·fc·(1+α·θ)。"""
    alpha = alpha if alpha is not None else cfst_alpha(fc)
    Ac, As = cfst_geom(D, t)
    theta = As * fa / (Ac * fc)
    return Ac * fc * (1 + alpha * theta) / 1000.0, theta


def cfst_R(N_kN, D, t, fc, fa, lam=None, alpha=None, concrete_grade="C60", steel="Q355"):
    """YJK 验算口径的承载力利用率 R_F1（忽略附件弯矩时）。

    R_F1 = (|N| + M/(0.25D)) / (λ·N0)，λ 为反标定得到的计算长度折减系数。
    """
    if lam is None:
        lam = CFST_LAMBDA.get((concrete_grade.upper(), steel.upper()), 0.905)
    N0, theta = cfst_N0(D, t, fc, fa, alpha)
    return N_kN / (lam * N0), theta


def design_cft(N_kN, D, fc, fa, lo=0.80, hi=0.88, concrete_grade="C60", steel="Q355",
               ts=(12, 14, 16, 18, 20, 22, 25, 28, 30, 32, 35, 36, 40),
               d_options=(900, 1000, 1100, 1200, 1300, 1400, 1500),
               dt_max=89.37, theta_min=0.5, theta_max=2.5):
    """圆钢管混凝土柱选型。

    在给定直径候选集内枚举 (D, t)，筛选 θ∈[theta_min, theta_max]、D/t≤dt_max
    且 R_F1 ≤ hi 的组合，**取钢材用量最省者**（同钢材量时取薄壁）。
    若没有 R_F1 ≥ lo 的组合，返回其中最接近 lo 的一个并标记 status='偏低'。

    D 传数值则只在该直径下找壁厚；传列表则视为建筑允许的直径候选。
    返回 (D, t, R_F1, theta, status)；完全无解返回 None。
    候选直径按升序去重。
    """
    d_list = sorted({float(x) for x in ([D] if isinstance(D, (int, float)) else d_options)})
    ok, low = [], []
    for Dx in d_list:
        for t in ts:
            if Dx / t > dt_max:
                continue
            R, theta = cfst_R(N_kN, Dx, t, fc, fa,
                              concrete_grade=concrete_grade, steel=steel)
            if not (theta_min <= theta <= theta_max):
                continue
            if R > hi:
                continue
            Ac, As = cfst_geom(Dx, t)
            item = (As, t, Dx, R, theta)          # 先比钢材面积，再比壁厚
            if R >= lo:
                ok.append(item)
            else:
                low.append(item)
    if ok:
        As, t, Dx, R, theta = min(ok)
        return Dx, t, R, theta, "ok"
    if low:
        As, t, Dx, R, theta = max(low, key=lambda x: x[3])   # R 最接近 lo
        return Dx, t, R, theta, "偏低"
    return None
