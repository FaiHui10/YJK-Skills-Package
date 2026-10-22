# -*- coding: utf-8 -*-
"""按规范限值与设计轴力自动选柱截面（四种柱型）。

输入
----
设计轴力需求（forces）：YJK 结果解析得到的记录列表，每条含
    {"标准层": 3, "柱号": 15, "Nu": -57864.0, …}
（用 yjk-colmodel 技能的 `yjk.py res --json` 导出即可）

方案骨架（scheme）：至少要有 std_floors 与 groups（见 quantity.py 的说明）

配置（cfg）示例
--------------
{
  "concrete": "C60",
  "steel_grade": "Q355",
  "rc":    {"structure": "框架-剪力墙/板柱-剪力墙/框架-核心筒/筒中筒", "seismic": 2,
            "short_col": false, "densify_hoop": true},
  "core":  {"core_ratio": 0.25},
  "src":   {"seismic": 2, "short_col": false, "densify_hoop": true,
            "roa": 0.045, "steel": null, "family": null},
  "diehe": {"gap": 650, "fc_in": "C60"},
  "cft":   {"D": [1000, 1100, 1200, 1300, 1400], "lo": 0.80, "hi": 0.88}
}
"""
import codes


def ctrl_Nu(forces, members, std, agg="max"):
    """取该标准层、该归并组各柱在所有自然层上的控制轴力（kN，正值）。

    轴力取绝对值最大者（压力为正号表达，方便直接代入承载力公式）。
    """
    vals = [abs(f["Nu"]) for f in forces
            if f.get("标准层") == std and f.get("柱号") in members and f.get("Nu")]
    if not vals:
        return None
    return max(vals) if agg == "max" else sum(vals) / len(vals)


def design_one(kind_name, Nu_kN, cfg, fc, fa, prev=None, grade=None):
    """按柱型选截面，返回 geo dict 或 None。

    fc / fa 为该标准层的混凝土与钢材强度设计值；grade 为该标准层的材料等级信息
    （含"管内混凝土"，仅叠合柱用得上）。
    """
    grade = grade or {}
    if kind_name == "普通RC":
        c = cfg.get("rc", {})
        lim = codes.uc_limit_rc(c.get("structure", "框架-剪力墙/板柱-剪力墙/框架-核心筒/筒中筒"),
                                int(c.get("seismic", 2)), bool(c.get("short_col")),
                                bool(c.get("densify_hoop")))
        b, _ = codes.design_rc(Nu_kN, fc, lim)
        return {"kind": 1, "b": b}

    if kind_name in ("加芯RC", "加芯柱", "芯柱RC"):
        c = dict(cfg.get("rc", {}))
        c.update(cfg.get("core", {}))
        lim = codes.uc_limit_rc(c.get("structure", "框架-剪力墙/板柱-剪力墙/框架-核心筒/筒中筒"),
                                int(c.get("seismic", 2)), bool(c.get("short_col")),
                                bool(c.get("densify_hoop")), core_column=True,
                                core_ratio=float(c.get("core_ratio", 0.25)))
        b, _ = codes.design_rc(Nu_kN, fc, lim)
        return {"kind": 1, "b": b}

    if kind_name in ("型钢SRC", "SRC"):
        c = cfg.get("src", {})
        lim = codes.uc_limit_src(int(c.get("seismic", 2)), bool(c.get("short_col")),
                                 bool(c.get("densify_hoop")))
        steel = tuple(c["steel"]) if c.get("steel") else None
        fam = [tuple(x) for x in c["family"]] if c.get("family") else None
        r = codes.design_src(Nu_kN, fc, fa, lim, roa=float(c.get("roa", 0.045)),
                             steel=steel, family=fam)
        if not r:
            return None
        return {"kind": 15, "b": r["b"], "f": r["f"], "tw": r["t"], "d": r["d"]}

    if kind_name in ("钢管叠合柱", "叠合柱"):
        c = cfg.get("diehe", {})
        fc_in = codes.fc_of(grade.get("管内混凝土") or c.get("fc_in")
                            or cfg.get("concrete", "C60"))
        r = codes.design_diehe(Nu_kN, fc, fc_in, fa, gap=float(c.get("gap", codes.GAP_DEFAULT)),
                               gap_min=float(c.get("gap_min", 600.0)))
        if not r:
            return None
        geo = {"kind": 102, "b": r["b"], "D": r["D"], "tw": r["t"]}
        if grade.get("管内来源", "").startswith("按管外"):
            geo["_note"] = ("管内混凝土按 %s 计算，请在 YJK 中确认并设置管内等级"
                            % grade.get("管内混凝土"))
        return geo

    if kind_name in ("圆钢管混凝土柱", "CFT", "钢管混凝土柱"):
        c = cfg.get("cft", {})
        Ds = c.get("D") or [900, 1000, 1100, 1200, 1300, 1400, 1500]
        if isinstance(Ds, (int, float)):
            Ds = [Ds]
        if prev and prev.get("D"):        # 竖向连续：直径不低于下一层
            Ds = [d for d in Ds if d >= prev["D"]] or [prev["D"]]
        r = codes.design_cft(Nu_kN, None, fc, fa, lo=float(c.get("lo", 0.80)),
                             hi=float(c.get("hi", 0.88)),
                             concrete_grade=grade.get("混凝土") or cfg.get("concrete", "C60"),
                             steel=grade.get("钢号") or cfg.get("steel_grade", "Q355"),
                             d_options=sorted(Ds))
        if not r:
            return None
        geo = {"kind": 12, "D": r[0], "tw": r[1]}
        if r[4] != "ok":
            geo["_note"] = ("承载力利用率 %.3f 低于目标 %.2f（该组轴力偏小，θ 已到下限）"
                            % (r[3], float(c.get("lo", 0.80))))
        return geo
    raise ValueError("未知柱型 %s" % kind_name)


def make_sections(scheme, forces, cfg, grades=None):
    """为 scheme 的每个 (柱型, 标准层, 组) 生成截面；返回 (sections, report, warnings)。

    grades: {标准层号: {"混凝土": "C60", "钢号": "Q355", "管内混凝土": …, "来源": …}}
            由 grades.load_grades(...) 提供；不给则全部按 cfg 的默认值。
    report 记录每条的 Nu / 结果 / 复核值，便于人工确认。
    """
    warn = []
    grades = grades or {}
    stds = sorted(int(x) for x in scheme["std_floors"])
    sections = {t: {} for t in scheme["types"]}
    report = []
    for t in scheme["types"]:
        prev = {}      # 每个归并组单独维护"上一层截面"，避免跨组互相抬高
        # 从下往上（标准层号小 = 下部）逐层设计，保证同组截面不出现下小上大
        for std in stds:
            g = grades.get(std, {})
            try:
                fc = codes.fc_of(g.get("混凝土") or cfg.get("concrete", "C60"))
                fa = codes.fa_of(g.get("钢号") or cfg.get("steel_grade", "Q355"), 20)
            except ValueError as e:
                warn.append("标准层%s 材料等级无法识别（%s），已按 config 默认值处理" % (std, e))
                fc = codes.fc_of(cfg.get("concrete", "C60"))
                fa = codes.fa_of(cfg.get("steel_grade", "Q355"), 20)
            for gname, members in scheme["groups"].items():
                Nu = ctrl_Nu(forces, members, std)
                if Nu is None:
                    report.append({"type": t, "std": std, "group": gname, "ok": False,
                                   "msg": "取不到设计轴力"})
                    continue
                geo = design_one(t, Nu, cfg, fc, fa, prev=prev.get(gname), grade=g)
                if geo is None:
                    report.append({"type": t, "std": std, "group": gname, "Nu": Nu, "ok": False,
                                   "msg": "无可行截面"})
                    continue
                if prev.get(gname):           # 不许下大上小：取不小于同组下一层
                    geo = _not_smaller(geo, prev[gname])
                sections[t].setdefault(str(std), {})[gname] = geo
                prev[gname] = geo
                report.append({"type": t, "std": std, "group": gname, "Nu": round(Nu, 1),
                               "ok": True, "geo": geo,
                               "check": _check(t, geo, Nu, cfg, fc, fa, g),
                               "note": geo.get("_note"),
                               "材料": "%s/%s" % (g.get("混凝土", cfg.get("concrete", "C60")),
                                                 g.get("钢号", cfg.get("steel_grade", "Q355")))})
    return sections, report, warn


def _not_smaller(geo, prev):
    if geo["kind"] == 12 and prev.get("D") and geo["D"] < prev["D"]:
        return dict(geo, D=prev["D"], tw=max(geo["tw"], prev.get("tw", geo["tw"])))
    if geo["kind"] in (1, 15, 102) and prev.get("b") and geo["b"] < int(prev["b"]):
        new = dict(geo)
        new["b"] = int(prev["b"])
        return new
    return geo


def _check(kind_name, geo, Nu_kN, cfg, fc, fa, grade=None):
    grade = grade or {}
    try:
        if geo["kind"] == 12:
            R, th = codes.cfst_R(Nu_kN, geo["D"], geo["tw"], fc, fa,
                                 concrete_grade=grade.get("混凝土")
                                 or cfg.get("concrete", "C60"),
                                 steel=grade.get("钢号") or cfg.get("steel_grade", "Q355"))
            return {"R_F1": round(R, 3), "theta": round(th, 3), "Dt": round(geo["D"] / geo["tw"], 1)}
        if geo["kind"] == 102:
            fc_in = codes.fc_of(grade.get("管内混凝土")
                                or cfg.get("diehe", {}).get("fc_in")
                                or cfg.get("concrete", "C60"))
            c = codes.check_diehe(Nu_kN, geo["b"], geo["D"], geo["tw"], fc, fc_in, fa)
            return {k: (round(v, 4) if isinstance(v, float) else v) for k, v in c.items()}
        if geo["kind"] == 15:
            Aa = codes.aa_cross(geo["f"], geo["tw"], geo["d"])
            A = geo["b"] ** 2
            return {"Uc": round(Nu_kN * 1000.0 / (fc * (A - Aa) + fa * Aa), 3),
                    "rhoa": round(Aa / A, 4),
                    "cover": round((geo["b"] - max(geo["f"], geo["d"])) / 2.0, 0)}
        return {"Uc": round(Nu_kN * 1000.0 / (fc * geo["b"] ** 2), 3)}
    except Exception as e:                     # 校验只作提示，不影响设计
        return {"err": str(e)}
