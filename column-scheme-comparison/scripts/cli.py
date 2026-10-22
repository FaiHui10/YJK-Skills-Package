# -*- coding: utf-8 -*-
"""column-scheme-comparison 命令行入口。

    python cli.py init     --model <模型目录> --groups "Z1=15,16;Z2=14;…" --std 3,4,5
                           [--types …] [--sec-type 圆钢管混凝土柱] [--out scheme.json] [--apply]
    python cli.py scope    --scheme s.json --model <模型目录> [--std 3,4,5]
    python cli.py limits   [--seismic 2] [--structure ...]
    python cli.py design   --scheme s.json --forces res.json [--config cfg.json]
                           [--wmass 00_输入/wmass.out | --model-json export.json]
                           [--types 普通RC] [--std 3,4,5] [--cols 1,7]
                           [--out s2.json] [--apply] [--excel 表.xlsx]
    python cli.py check    --scheme s.json --forces res.json [--config cfg.json] [...]
    python cli.py excel    --scheme s.json --forces res.json [--config cfg.json] [...]
                           --out 截面设计表.xlsx
    python cli.py import-excel --xlsx 截面设计表.xlsx --scheme s.json [--out s2.json] [--apply]
    python cli.py quantity --scheme s.json --out 用量统计.xlsx [--types …] [--std …] [--cols …]
    python cli.py io       --scheme s.json [--types …] [--std …] [--cols …]
    python cli.py scaffold --root <计算根目录> --scheme s.json [--seed <种子模型目录>]
                           [--forces res.json] [--config cfg.json] [--mode slim|full|none] [--dry-run]

柱位（groups）与楼层（std_floors）的来源：
  * `init` 从模型自动填 std_floors 与 sections，**groups 由 --groups 人工指定**
  * `scope` 校验柱号/层号是否与模型对得上、有没有漏柱
  * `--std` / `--cols` 只用于限定核对范围（会裁减组内成员，改变控制轴力，不要用来定案）
"""
import argparse
import copy
import json
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import codes
import design
import editable
import grades as G
import quantity as Q
import scaffold as SC
import scope as S

FRAME = "框架-剪力墙/板柱-剪力墙/框架-核心筒/筒中筒"


def _load(p):
    return json.load(open(p, encoding="utf-8-sig"))


def _save(o, p):
    o = {k: v for k, v in o.items() if not k.startswith("_")}
    json.dump(o, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def _load_forces(p):
    d = _load(p)
    return d["rows"] if isinstance(d, dict) and "rows" in d else d


def _int_list(s):
    if not s:
        return None
    return [int(x) for x in str(s).replace("，", ",").split(",") if x.strip()]


def _apply_type_filter(scheme, spec):
    """--types 只保留指定柱型（用于"每种柱型一个计算目录"的场景）。"""
    if not spec:
        return scheme, None
    want = [t.strip() for t in spec.replace("，", ",").split(",") if t.strip()]
    lack = [t for t in want if t not in scheme["types"]]
    if lack:
        raise SystemExit("scheme 里没有这些柱型：%s（可选：%s）" % (lack, scheme["types"]))
    scheme = copy.deepcopy(scheme)
    scheme["types"] = want
    scheme["sections"] = {t: scheme["sections"][t] for t in want}
    return scheme, want


def _apply_scope_filter(scheme, stdspec, colspec):
    """--std / --cols 限定统计范围（改的是组内成员，会影响每组的控制轴力，只作范围核对用）。"""
    if not stdspec and not colspec:
        return scheme, False
    scheme = copy.deepcopy(scheme)
    stds = _int_list(stdspec)
    cols = _int_list(colspec)
    if stds:
        want = {str(x) for x in stds}
        lack = sorted(want - set(scheme["std_floors"]), key=int)
        if lack:
            raise SystemExit("scheme 里没有这些标准层：%s（可选：%s）"
                             % (lack, sorted(scheme["std_floors"], key=int)))
        scheme["std_floors"] = {k: v for k, v in scheme["std_floors"].items() if k in want}
        scheme["sections"] = {t: {k: v for k, v in d.items() if k in want}
                              for t, d in scheme["sections"].items()}
    if cols:
        keep = set(cols)
        newg = {}
        for g, mem in scheme["groups"].items():
            inter = [c for c in mem if c in keep]
            if inter:
                newg[g] = inter
        if not newg:
            raise SystemExit("--cols 与任何归并组都不相交（可选柱号：%s）"
                             % sorted({c for m in scheme["groups"].values() for c in m}))
        scheme["groups"] = newg
    return scheme, True


def _grades(a, scheme, cfg):
    spec = a.wmass or getattr(a, "model_json", None) or getattr(a, "model", None)
    return G.load_grades(spec, scheme, cfg)


def _print_grades(grades, src):
    print("材料等级来源: %s" % (src or "—"))
    print("  %-8s %-8s %-8s %-8s %-8s %s" % ("标准层", "混凝土", "钢号", "管内混凝土",
                                             "fc", "来源"))
    for std in sorted(grades):
        g = grades[std]
        fc = codes.FC.get((g.get("混凝土") or "").upper(), "?")
        print("  %-8s %-8s %-8s %-8s %-8s %s" % (std, g.get("混凝土"), g.get("钢号"),
                                                 g.get("管内混凝土"), fc, g.get("来源")))


# ---------------------------------------------------------------- limits
def cmd_limits(a):
    print("JGJ3-2010 表 6.4.2 混凝土柱轴压比限值")
    print("  %-42s %s" % ("结构类型", "一级/二级/三级"))
    for st in sorted({k[0] for k in codes.UC_RC_TABLE}):
        vals = [codes.UC_RC_TABLE.get((st, s), "-") for s in (1, 2, 3)]
        print("  %-42s %s" % (st, vals))
    print("  注4 剪跨比≤2(短柱) −0.05 ；注5 全高加密/加芯柱 +0.10/+0.05 ；注6 不低于 0.65")
    print()
    print("JGJ3-2010 表 11.4.4 型钢混凝土柱轴压比限值：%s" % codes.UC_SRC_TABLE)
    print("   11.4.5 含钢率≥4%，型钢保护层≥150mm")
    print()
    print("CECS188 钢管混凝土叠合柱：轴压比≤%.2f，含管率≥%.0f%%，套箍指标 θ≤%.1f，D/t≤%.2f"
          % (codes.UC_DIEHE, codes.DIEHE and codes.ROA_DIEHE_MIN * 100,
             codes.THETA_DIEHE_MAX, codes.DT_DIEHE_MAX))
    print()
    print("按当前参数展开（结构类型=%s，抗震等级=%s）" % (a.structure, a.seismic))
    print("  %-30s %-8s %-8s %-8s %s" % ("情形", "限值", "短柱", "加密箍", "加芯"))
    for short in (False, True):
        for dens in (False, True):
            for core in (False, True):
                lim = codes.uc_limit_rc(a.structure, a.seismic, short, dens, core, 0.25)
                print("  %-30s %-8.3f %-8s %-8s %s" %
                      ("", lim, "是" if short else "否", "是" if dens else "否",
                       "是" if core else "否"))
    print("  SRC: 二级 %.2f（短柱 %.2f，加密 %.2f）"
          % (codes.uc_limit_src(2), codes.uc_limit_src(2, True),
             codes.uc_limit_src(2, False, True)))
    return 0


# ---------------------------------------------------------------- design
def cmd_design(a):
    scheme = Q.load_scheme(a.scheme)
    scheme, _ = _apply_type_filter(scheme, a.types)
    scheme, scoped = _apply_scope_filter(scheme, a.std, a.cols)
    if scoped:
        print("⚠ 已按 --std/--cols 限定范围：柱号被裁减后，每组的控制轴力会变小，"
              "整组截面可能偏小——范围核对可以，**不要用它定案**。\n")
    forces = _load_forces(a.forces)
    cfg = _load(a.config) if a.config else {}
    grades, warns, src = _grades(a, scheme, cfg)
    _print_grades(grades, src)
    print()
    sections, report, w2 = design.make_sections(scheme, forces, cfg, grades)
    warns = warns + w2
    print("按规范限值与设计轴力选截面（混凝土/钢材按上表逐标准层取值）")
    print("  %-16s %-8s %-8s %-11s %-30s %s" %
          ("柱型", "标准层", "组", "Nu(kN)", "选定截面", "复核"))
    bad = 0
    for r in report:
        if not r["ok"]:
            bad += 1
            print("  %-16s %-8s %-8s %-11s %-30s ★%s" %
                  (r["type"], r["std"], r["group"], r.get("Nu", "-"), "-", r["msg"]))
            continue
        geo = r["geo"]
        fmt = {1: lambda g: "%d×%d" % (g["b"], g["b"]),
               12: lambda g: "Φ%d×%d" % (g["D"], g["tw"]),
               15: lambda g: "%d×%d+翼%d×%d×4+腹%d×%d×2" % (g["b"], g["b"], g["f"], g["tw"],
                                                           g["d"], g["tw"]),
               102: lambda g: "%d×%d+内管Φ%d×%d" % (g["b"], g["b"], g["D"], g["tw"])}
        print("  %-16s %-8s %-8s %-11s %-30s %s%s" %
              (r["type"], r["std"], r["group"], r["Nu"], fmt[geo["kind"]](geo), r["check"],
               "  ★" + r["note"] if r.get("note") else ""))
    for w in warns:
        print("  ⚠ %s" % w)
    scheme["sections"] = {t: {s: {g: {k: v for k, v in geo.items() if not k.startswith("_")}
                                  for g, geo in gg.items()}
                              for s, gg in v.items()} for t, v in sections.items()}
    out = a.out or a.scheme.replace(".json", "_design.json")
    print("\n未能求解 %d 处。可用截面 -> %s" % (bad, out))
    if a.excel:
        r = editable.write_design_book(scheme, forces, report, grades, a.excel, cfg, notes=warns)
        print("已导出可手工调整的设计表 -> %s（%d 行截面；改完用 import-excel 读回）"
              % (a.excel, r["rows"]))
    if a.apply:
        _save(scheme, out)
        print("已写出。")
    else:
        print("（预演模式，未写文件；加 --apply 写出）")
    return 0 if not bad else 1


# ---------------------------------------------------------------- check
def cmd_check(a):
    scheme = Q.load_scheme(a.scheme)
    scheme, _ = _apply_type_filter(scheme, a.types)
    scheme, scoped = _apply_scope_filter(scheme, a.std, a.cols)
    if scoped:
        print("⚠ 已按 --std/--cols 限定范围（只影响复核对象，不改结论）\n")
    forces = _load_forces(a.forces)
    cfg = _load(a.config) if a.config else {}
    grades, warns, src = _grades(a, scheme, cfg)
    _print_grades(grades, src)
    print()
    print("  %-16s %-8s %-8s %-11s %-13s %-30s %s" %
          ("柱型", "标准层", "组", "Nu(kN)", "材料", "现有截面", "复核"))
    for t in scheme["types"]:
        for std in sorted(int(x) for x in scheme["std_floors"]):
            g = grades.get(std, {})
            fc = codes.fc_of(g.get("混凝土") or cfg.get("concrete", "C60"))
            fa = codes.fa_of(g.get("钢号") or cfg.get("steel_grade", "Q355"), 20)
            for gname, members in scheme["groups"].items():
                geo = scheme["sections"].get(t, {}).get(str(std), {}).get(gname)
                if not geo:
                    continue
                Nu = design.ctrl_Nu(forces, members, std)
                if Nu is None:
                    continue
                print("  %-16s %-8s %-8s %-11.0f %-13s %-30s %s" %
                      (t, std, gname, Nu, g.get("混凝土", "?"), Q.geom(geo)["sec"],
                       design._check(t, geo, Nu, cfg, fc, fa, g)))
    for w in warns:
        print("  ⚠ %s" % w)
    return 0


# ---------------------------------------------------------------- excel 导出
def cmd_excel(a):
    scheme = Q.load_scheme(a.scheme)
    scheme, _ = _apply_type_filter(scheme, a.types)
    scheme, scoped = _apply_scope_filter(scheme, a.std, a.cols)
    forces = _load_forces(a.forces)
    cfg = _load(a.config) if a.config else {}
    grades, warns, src = _grades(a, scheme, cfg)
    _print_grades(grades, src)
    _, report, w2 = design.make_sections(scheme, forces, cfg, grades)
    r = editable.write_design_book(scheme, forces, report, grades, a.out, cfg,
                                   notes=warns + w2)
    print("\n已导出截面设计表 -> %s" % a.out)
    print("  %d 行截面；「截面参数」表 A~N 列可直接改，O 列以后为公式自动重算。" % r["rows"])
    print("  改完运行: cli.py import-excel --xlsx \"%s\" --scheme \"%s\" --out 新scheme.json"
          % (a.out, a.scheme))
    for w in warns + w2:
        print("  ⚠ %s" % w)
    return 0


# ---------------------------------------------------------------- excel 读回
def cmd_import_excel(a):
    scheme = Q.load_scheme(a.scheme)
    book = editable.read_design_book(a.xlsx)
    new, diffs = editable.apply_to_scheme(scheme, book)
    for w in book["warnings"]:
        print("  ⚠ %s" % w)
    if not diffs:
        print("读回成功，截面与现有方案**完全一致**（无差异）。")
    else:
        print("读回成功，相对现有方案共 %d 处差异：" % len(diffs))
        print("  %-16s %-8s %-8s %-30s -> %s" % ("柱型", "标准层", "组", "原截面", "新截面"))
        for t, std, gname, old, newc in diffs:
            print("  %-16s %-8s %-8s %-30s -> %s" % (t, std, gname, old, newc))
    if book["grades"]:
        print("\n读回的材料等级（以设计表为准）：")
        _print_grades(book["grades"], "截面设计表")
    out = a.out or a.scheme.replace(".json", "_edited.json")
    new.pop("_grades", None)
    if a.apply:
        _save(new, out)
        print("\n已写出 -> %s" % out)
    else:
        print("\n（预演模式，未写文件；加 --apply 写出到 %s）" % out)
    return 0


# ---------------------------------------------------------------- init
def cmd_init(a):
    info = S.read_model(a.model)
    groups = S.parse_groups(a.groups)
    types = [t.strip() for t in a.types.replace("，", ",").split(",") if t.strip()]
    stds = _int_list(a.std) or [s for s in sorted(info) if info[s]["cols"]]
    print("从模型读到的事实:")
    print("  %-8s %-10s %-10s %-8s %s" % ("标准层", "定义层高mm", "自然层数", "柱数", "自然层(层高mm)"))
    for s in sorted(info):
        i = info[s]
        mark = "  ← 选用" if s in stds else ""
        print("  %-8s %-10s %-10s %-8s %s%s" %
              (s, i["height_mm"], len(i["nat_floors"]), len(i["cols"]),
               "、".join("%d(%s)" % (n, h) for n, h in zip(i["nat_floors"], i["nat_heights"])),
               mark))
    print("\n人工指定的柱位分组:")
    for g, mem in groups.items():
        print("  %-6s %s" % (g, "、".join("N%d" % c for c in mem)))
    scheme, tips = S.make_scheme(info, stds, groups, types,
                                 sec_type=a.sec_type, project=a.project)
    errs, warns, detail = S.check(scheme, info)
    print("\n骨架自检:")
    print("  %-8s %-10s %-10s %s" % ("标准层", "模型柱数", "方案覆盖", "未覆盖的柱号"))
    for d in detail:
        print("  %-8s %-10s %-10s %s" % (d["std"], d["模型柱数"], d["方案覆盖"],
                                         d["未覆盖"] or "无"))
    for e in errs:
        print("  ★错误 %s" % e)
    for w in warns + tips:
        print("  ⚠ %s" % w)
    if errs:
        print("\n★ 有硬错误，未写出 scheme。请先修正 --groups / --std。")
        return 1
    out = a.out or "scheme.json"
    if a.apply:
        _save(scheme, out)
        print("\n已写出 -> %s" % out)
        print("下一步: 用 yjk-colmodel 导出设计轴力，再跑 design 生成各柱型截面。")
    else:
        print("\n（预演模式，未写文件；加 --apply 写出到 %s）" % out)
    return 0


# ---------------------------------------------------------------- scope
def cmd_scope(a):
    scheme = Q.load_scheme(a.scheme)
    info = S.read_model(a.model)
    if a.std:
        want = {str(x) for x in _int_list(a.std)}
        scheme = copy.deepcopy(scheme)
        scheme["std_floors"] = {k: v for k, v in scheme["std_floors"].items() if k in want}
    errs, warns, detail = S.check(scheme, info)
    print("方案与模型的一致性校验（模型: %s）" % os.path.abspath(a.model))
    print("  %-8s %-10s %-10s %-26s %s" % ("标准层", "模型柱数", "方案覆盖", "未覆盖的柱号",
                                           "模型自然层"))
    for d in detail:
        print("  %-8s %-10s %-10s %-26s %s" % (d["std"], d["模型柱数"], d["方案覆盖"],
                                               str(d["未覆盖"] or "无"), d["自然层"]))
    print()
    for e in errs:
        print("  ★错误 %s" % e)
    for w in warns:
        print("  ⚠ %s" % w)
    if not errs and not warns:
        print("  ✓ 柱位与楼层与模型完全对得上。")
    print("\n结论: %d 个错误、%d 个提醒" % (len(errs), len(warns)))
    return 1 if errs else 0


# ---------------------------------------------------------------- scaffold
def cmd_scaffold(a):
    scheme = Q.load_scheme(a.scheme)
    forces = _load_forces(a.forces) if a.forces else None
    cfg = _load(a.config) if a.config else None
    if a.dry_run:
        types = scheme.get("types", [])
        print("将建立的计算目录（预演，未创建）:")
        print("  %s\\00_输入\\  (scheme/forces/config/wmass)" % a.root)
        for t in types:
            print("  %s\\%s\\  ← 柱型 %s" % (a.root, SC.SLOT.get(t, t), t))
        print("  %s\\99_汇总\\" % a.root)
        print("  %s\\README.txt" % a.root)
        print("  种子模型 %s，复制模式 %s" % (a.seed or "未指定", a.mode))
        return 0
    made, tips = SC.make_workspace(a.root, scheme, seed=a.seed, forces=forces, cfg=cfg,
                                   wmass=a.wmass, mode=a.mode)
    print("已建立计算目录 -> %s" % a.root)
    for m in made:
        print("  + %s" % m)
    for t in tips:
        print("  ⚠ %s" % t)
    print("\n流程见 %s\\README.txt" % a.root)
    return 0



# ---------------------------------------------------------------- quantity
def cmd_quantity(a):
    scheme = Q.load_scheme(a.scheme)
    scheme, _ = _apply_type_filter(scheme, a.types)
    scheme, scoped = _apply_scope_filter(scheme, a.std, a.cols)
    if scoped:
        print("⚠ 已按 --std/--cols 限定范围，统计结果只覆盖被选中的柱/层\n")
    r = Q.build(scheme, a.out)
    T = r["totals"]
    rc = T[Q.base_of(scheme["types"])]
    print("[%s] 合计（%d 条柱段记录）" % (os.path.basename(a.out), r["rows"]))
    print("  %-16s %10s %9s %9s %10s %10s %10s %12s %9s %9s" %
          ("柱型", "砼m³", "钢筋t", "型钢t", "模板m²", "防火m²", "占用m²", "造价元",
           "Δ造价", "Δ占用"))
    for t in scheme["types"]:
        o = T[t]
        print("  %-16s %10.1f %9.2f %9.2f %10.1f %10.1f %10.2f %12.0f %+9.1f%% %+9.1f%%" %
              (t, o["conc"], o["rebar"], o["steel"], o["form"], o["fire"], o["occ"],
               o["cost"], (o["cost"] / rc["cost"] - 1) * 100, (o["occ"] / rc["occ"] - 1) * 100))
    print("\n[投入产出比]")
    for row in r["io"][1:]:
        v = [x[2] if isinstance(x, tuple) else x for x in row]
        print("  %-16s 造价%11.0f(%+7.1f%%)  占用%8.2f(%+7.1f%%)  换回楼面%7.2f m²  "
              "造价增量%11.0f  投入产出比 %8.0f 元/m²" %
              (v[0], v[1], v[2] * 100, v[3], v[4] * 100, v[5], v[6], v[7]))
    print("\n输出 -> %s" % a.out)
    return 0


# ---------------------------------------------------------------- io
def cmd_io(a):
    scheme = Q.load_scheme(a.scheme)
    scheme, _ = _apply_type_filter(scheme, a.types)
    scheme, _ = _apply_scope_filter(scheme, a.std, a.cols)
    T = Q.totals(scheme)
    rc = T[Q.base_of(scheme["types"])]
    print("  %-16s %12s %10s %12s %10s %12s %12s %12s" %
          ("柱型", "造价元", "Δ造价", "占用m²", "Δ占用", "换回楼面m²", "造价增量元", "投入产出比"))
    for t in scheme["types"]:
        o = T[t]
        d_occ, d_cost = rc["occ"] - o["occ"], o["cost"] - rc["cost"]
        io = "--" if abs(d_occ) < 1e-9 else "%.0f" % (d_cost / d_occ)
        print("  %-16s %12.0f %9.1f%% %12.2f %9.1f%% %12.2f %12.0f %12s" %
              (t, o["cost"], (o["cost"] / rc["cost"] - 1) * 100, o["occ"],
               (o["occ"] / rc["occ"] - 1) * 100, d_occ, d_cost, io))
    return 0


def _utf8_console():
    """非 GBK 控制台下输出不崩（库调用与 CLI 都适用）。"""
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(errors="replace")
        except Exception:                                      # noqa: BLE001
            pass


def main():
    _utf8_console()
    p = argparse.ArgumentParser(description="柱型方案比选：截面设计 + 用量造价统计")
    sub = p.add_subparsers(dest="cmd", required=True)

    l = sub.add_parser("limits", help="打印各柱型轴压比/构造限值")
    l.add_argument("--structure", default=FRAME)
    l.add_argument("--seismic", type=int, default=2)
    l.set_defaults(fn=cmd_limits)

    d = sub.add_parser("design", help="按规范与设计轴力自动选截面")
    d.add_argument("--scheme", required=True)
    d.add_argument("--forces", required=True, help="yjk-colmodel 的 res --json 输出")
    d.add_argument("--config")
    d.add_argument("--wmass", help="种子模型的 wmass.out（从中读混凝土强度/钢号）")
    d.add_argument("--model-json", help="yjk-colmodel 的 export --json 输出（含逐标准层材料）")
    d.add_argument("--model", help="种子模型目录（自动找 设计结果\\wmass.out）")
    d.add_argument("--types", help="只设计这些柱型，如 钢管叠合柱（每种柱型一个计算目录时用）")
    d.add_argument("--std", help="只设计这些标准层，如 3,5")
    d.add_argument("--cols", help="只设计这些柱号（会裁减组内成员，仅作范围核对）")
    d.add_argument("--out")
    d.add_argument("--excel", help="同时导出可手工调整的截面设计表 xlsx")
    d.add_argument("--apply", action="store_true")
    d.set_defaults(fn=cmd_design)

    c = sub.add_parser("check", help="复核现有方案截面的轴压比/含钢率等")
    c.add_argument("--scheme", required=True)
    c.add_argument("--forces", required=True)
    c.add_argument("--config")
    c.add_argument("--wmass")
    c.add_argument("--model-json")
    c.add_argument("--model")
    c.add_argument("--types")
    c.add_argument("--std")
    c.add_argument("--cols")
    c.set_defaults(fn=cmd_check)

    x = sub.add_parser("excel", help="导出可手工调整的截面设计表（Excel）")
    x.add_argument("--scheme", required=True)
    x.add_argument("--forces", required=True)
    x.add_argument("--config")
    x.add_argument("--wmass")
    x.add_argument("--model-json")
    x.add_argument("--model")
    x.add_argument("--types")
    x.add_argument("--std")
    x.add_argument("--cols")
    x.add_argument("--out", required=True)
    x.set_defaults(fn=cmd_excel)

    ini = sub.add_parser("init", help="从模型生成 scheme.json 骨架（柱位分组人工指定）")
    ini.add_argument("--model", required=True, help="模型目录（含 g-of.ymd）")
    ini.add_argument("--groups", required=True,
                     help="柱位分组，形如 \"Z1=15,16;Z2=14;Z3=13;Z4=1,7;Z5=2,3,4,9,10\"")
    ini.add_argument("--std", help="参与对比的标准层，如 3,4,5；不给则取模型里有柱的全部标准层")
    ini.add_argument("--types", default="普通RC,加芯RC,型钢SRC,钢管叠合柱,圆钢管混凝土柱",
                     help="柱型清单")
    ini.add_argument("--sec-type", help="把模型现有截面作为哪个柱型的初始截面（默认第一个柱型）")
    ini.add_argument("--project", help="项目名")
    ini.add_argument("--out", help="输出文件，默认 scheme.json")
    ini.add_argument("--apply", action="store_true", help="真正写出（默认预演）")
    ini.set_defaults(fn=cmd_init)

    sc = sub.add_parser("scope", help="校验方案的柱位/楼层是否与模型一致、有没有漏柱")
    sc.add_argument("--scheme", required=True)
    sc.add_argument("--model", required=True)
    sc.add_argument("--std", help="只校验这些标准层")
    sc.set_defaults(fn=cmd_scope)

    ix = sub.add_parser("import-excel", help="读回手工改过的截面设计表")
    ix.add_argument("--xlsx", required=True)
    ix.add_argument("--scheme", required=True)
    ix.add_argument("--out")
    ix.add_argument("--apply", action="store_true")
    ix.set_defaults(fn=cmd_import_excel)

    sf = sub.add_parser("scaffold", help="为每种柱型建立独立计算目录")
    sf.add_argument("--root", required=True, help="计算根目录")
    sf.add_argument("--scheme", required=True)
    sf.add_argument("--seed", help="种子模型目录（复制到各柱型目录）")
    sf.add_argument("--forces")
    sf.add_argument("--config")
    sf.add_argument("--wmass")
    sf.add_argument("--mode", default="slim", choices=["slim", "full", "none"],
                    help="slim=跳过中间数据等可重生成目录(默认)；full=全量；none=只建目录")
    sf.add_argument("--dry-run", action="store_true")
    sf.set_defaults(fn=cmd_scaffold)

    q = sub.add_parser("quantity", help="生成公式驱动的用量/造价/占用统计 Excel")
    q.add_argument("--scheme", required=True)
    q.add_argument("--out", required=True)
    q.add_argument("--types")
    q.add_argument("--std")
    q.add_argument("--cols")
    q.set_defaults(fn=cmd_quantity)

    i = sub.add_parser("io", help="打印投入产出比")
    i.add_argument("--scheme", required=True)
    i.add_argument("--types")
    i.add_argument("--std")
    i.add_argument("--cols")
    i.set_defaults(fn=cmd_io)

    a = p.parse_args()
    sys.exit(a.fn(a))


if __name__ == "__main__":
    main()
