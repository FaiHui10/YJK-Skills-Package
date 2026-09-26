# -*- coding: utf-8 -*-
"""按上一轮实算轴力，为每 (结构层 × 柱位分组) 选造价最小的 (混凝土等级, 柱边长)。

原理：选型的硬约束是轴压比 Uc = N/(A·fc) ≤ 限值，它是**逐柱局部**约束，
给定 N 就有闭式解 side ≥ √(N/(限值·fc))，所以每层只需枚举等级（层内统一），
组内取最小可行边长 —— 是"闭式求解 + 小枚举"，不是组合搜索。

用法：
    python section_opt.py --config c.json --res <工程目录或设计结果> --out s_next.json
                         [--only C30]   # 强制全楼单一等级，用于做等级对照
                         [--db m.ydb]   # 真实工程（框-筒等）必给：分组按柱坐标现算

输出：sections.json（可直接喂给 frame_build.py），并把选型表打到屏幕。

★ 分组从哪来（区分模式 A / 模式 B）
    --db 不给：按柱号 `group_of_nc`（柱号 = i*NY+j+1），**只对 frame_build.py 生成的
               纯框架成立**；此时先用 `assert_pure_frame` 卡柱数，对不上就报错退出。
    --db 给了：逐标准层用 `common.groups_from_model`（按柱坐标）现算，框-筒/抽柱也能用。
"""
import argparse
import collections
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (assert_pure_frame, counts_by_group, find_wpj, floor_list,  # noqa: E402
                    group_of_nc, groups_from_model, layer_segment_map, load_config,
                    price_of, fc_of, resolve_res_dir, sides, std_of_floor)

RE_COL = re.compile(r"^\s*N-C=(\d+)\s+\(I=\d+,\s*J=\d+\)(?:\(\d+\))?B\*H\(mm\)=\s*(\d+)\*(\d+)")
RE_UC = re.compile(r"Nu=\s*([-\d.]+)\s+Uc=\s*([-\d.]+)\s+Rs=\s*([\d.]+)\(%\)\s+Rsv=\s*([\d.]+)\(%\)")
RE_COVER = re.compile(r"Cover=\s*([\d.]+)\(mm\)")
RE_COMBO = re.compile(r"^\s*\(\s*(\d+)\)\s*N=")
RE_AS = re.compile(r"(As[xy][tyb]=)\s*(\d+)")


def parse_wpj(path):
    """返回 {nc: {Nu, Uc, Rs, Rsv, Ast, cover}}；Uc/Nu 取最不利组合。"""
    rows, cur, combo = {}, None, {}
    for line in open(path, "rb").read().decode("gbk", "replace").splitlines():
        m = RE_COL.match(line)
        if m:
            if cur:
                cur["Ast"] = max(combo.values()) if combo else 0
                rows[cur["nc"]] = cur
            cur = {"nc": int(m.group(1)), "B": int(m.group(2)), "H": int(m.group(3)),
                   "cover": None, "Nu": None, "Uc": None, "Rs": None, "Rsv": None, "Ast": 0}
            combo = {}
            continue
        if cur is None:
            continue
        m = RE_COVER.search(line)
        if m and cur["cover"] is None:
            cur["cover"] = float(m.group(1))
        m = RE_UC.search(line)
        if m:
            nu, uc, rs, rsv = (float(m.group(i)) for i in range(1, 5))
            if cur["Uc"] is None or uc > cur["Uc"]:
                cur.update(Nu=nu, Uc=uc, Rs=rs, Rsv=rsv)
        mc = RE_COMBO.match(line)
        if mc:
            faces = RE_AS.findall(line)
            if faces:
                cid = int(mc.group(1))
                combo[cid] = combo.get(cid, 0) + sum(int(v) for _, v in faces)
    if cur:
        cur["Ast"] = max(combo.values()) if combo else 0
        rows[cur["nc"]] = cur
    return rows


def cost_one(cfg, side, grade, ast_base, rsv_base, cover, L):
    pc = cfg["造价"]
    rho_min = pc["纵筋最小配筋率"]
    Ac = side * side / 1e6
    core = max(side - 2 * cover, 0) ** 2 / 1e6
    v_con = Ac * L
    v_form = 4 * side / 1000.0 * L
    # 纵筋：计算配筋（或构造下限）是"面积"，乘柱段长才是体积
    v_long = max(ast_base, rho_min * side * side) / 1e6 * L
    v_stir = (rsv_base / 100.0) * core * L
    return (v_con * price_of(cfg, grade) + v_form * pc["模板单价元每m2"]
            + (v_long + v_stir) * pc["钢筋密度kg每m3"] / 1000.0 * pc["钢筋单价元每t"])


def optimize(cfg, ctrl, grade_choices, counts_by_floor=None):
    """逐层枚举等级、组内闭式求最小可行边长。

    counts_by_floor：{层: {组: 根数}} —— 按**真实柱数**给该层造价加权（--db 模式用
    模型按坐标数出来的柱数）。不传则退回纯框架口径 `counts_by_group(cfg)`（老行为）。
    ★ 为什么要传：等级是"按该层造价最小"选的，权重（每组几根柱）错了，选出的等级就可能
      不是真最优 —— 框-筒里按 `i*NY+j+1` 数出来的柱数与实际差得很远。
    """
    uc_lim = cfg["抗震"]["轴压比目标"]
    cand = sides(cfg)
    frame_counts = counts_by_group(cfg)
    out, total, detail = {}, 0.0, []
    for f in floor_list(cfg):
        counts = (counts_by_floor or {}).get(f) or frame_counts
        best = None
        for grade in grade_choices:
            picked, cfloor, ucmax, ok = {}, 0.0, 0.0, True
            for grp in cfg["截面"]["分组"]:
                r = ctrl.get((f, grp))
                if r is None:
                    # 不要 KeyError：这多半是 config 的 截面.分组 与本工程的实际分组
                    # 对不上（比如框-筒里根本没有"中柱"这一组），必须说清楚
                    raise SystemExit(
                        "!! 第 %d 层没有「%s」分组的实算记录 —— config 的 截面.分组=%s，"
                        "而本层实际拿到的分组只有 %s\n"
                        "   检查 --db 与 --config 是不是同一个工程；分组名要与模型对得上"
                        % (f, grp, cfg["截面"]["分组"],
                           sorted({g for (ff, g) in ctrl if ff == f}) or "无"))
                nu = abs(r["Nu"] or 0) * 1000.0                    # kN -> N
                pick = None
                for side in cand:
                    uc = nu / (side * side * fc_of(cfg, grade))
                    if uc <= uc_lim:
                        pick = (side, uc)
                        break
                if pick is None:
                    ok = False
                    break
                picked[grp] = pick[0]
                ucmax = max(ucmax, pick[1])
                cfloor += cost_one(cfg, pick[0], grade, r["Ast"], r["Rsv"],
                                   r["cover"] or 20.0, cfg["几何"]["层高"] / 1000.0) \
                    * counts.get(grp, 1)
            if ok and (best is None or cfloor < best[0]):
                best = (cfloor, grade, dict(picked), ucmax)
        if best is None:
            raise SystemExit("第 %d 层在候选等级/截面下无可行解" % f)
        cfloor, grade, picked, ucmax = best
        total += cfloor
        out[str(f)] = {"grade": grade, **picked}
        detail.append((f, grade, picked, ucmax, cfloor))
    return out, total, detail


def main():
    _utf8_console()          # ★ 必须在 argparse 之前：--help 也是写到 stdout 的
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--res", required=True, help="工程目录或 设计结果 目录")
    ap.add_argument("--out", required=True)
    ap.add_argument("--only", help="强制全楼单一等级（如 C30）")
    ap.add_argument("--compare", help="与给定 sections.json 对比，用于判断是否收敛")
    ap.add_argument("--db", default=None,
                    help="模型库(.ydb/.ymd)：给了就**按柱坐标**分组（common.groups_from_model），"
                         "真实工程/框-筒必给；不给则按柱号分组（只对 frame_build.py 的纯框架成立）")
    a = ap.parse_args()

    cfg = load_config(a.config)
    res = resolve_res_dir(a.res)
    wpj = find_wpj(res)

    # 先把各层 wpj 解析出来：不给 --db 时要拿"每层柱数"去卡纯框架口径
    parsed = {f: parse_wpj(p) for f, p in sorted(wpj.items())}
    if not any(parsed.values()):
        raise SystemExit("没解析到柱结果，确认 %s 下有 wpj*.out" % res)

    units = {}
    counts_by_floor = {}
    if a.db:
        # 逐层按柱坐标算分组。★ 自然层 -> 标准层用 tblFloor 查（frame_build.py 的产出
        #   恰好 1:1，所以两者相等；但一个标准层可以被多个自然层复用，那时不能假设相等）。
        #   读不到就明确退出，不猜（猜就是分组错位且不报错）。
        for f in sorted(parsed):
            std = std_of_floor(a.db, f) or f
            gs = groups_from_model(a.db, std)
            if not gs:
                raise SystemExit(
                    "!! 从 %s 读不到标准层 %d（自然层 %d）的柱分组（tblColSeg/tblJoint 为空？）\n"
                    "   也可能是 tblFloor 里没有这个自然层的对应关系 —— 查不到就退出，不猜"
                    % (a.db, std, f))
            gof = {c: g for g, cols in gs.items() for c in cols}
            # wpj 柱段号 -> 模型柱号（首层被切成多段时按 (段号-1)//k+1 折回）。
            # ★ 这里**必须**成功：section_opt 是要写回模型的，段号对不上就会被静默漏算，
            #   选出偏小的截面（不安全方向），所以对不上直接报错。
            sm = layer_segment_map(gof, parsed[f])
            if sm is None:
                raise SystemExit(
                    "!! 自然层 %d（标准层 %d）的 wpj 柱号与模型对不上：wpj 柱号 %s…，"
                    "模型柱号 %s…\n"
                    "   把差集：%s\n"
                    "   wpj 的 N-C 与模型 tblColSeg.No_ 口径不一致（是否按标准层各自从 1 "
                    "开始编号？）；--db 与 wpj 是不是同一个模型？"
                    % (f, std, sorted(parsed[f])[:10], sorted(gof)[:10],
                       sorted(set(parsed[f]) - set(gof))[:10]))
            units[f] = {nc: gof[col] for nc, col in sm.items()}
            counts_by_floor[f] = {g: len(cols) for g, cols in gs.items()}
        print("★ 分组来源：--db %s（按柱坐标现算，逐标准层）" % os.path.basename(a.db))
        mism = [f for f in sorted(parsed) if (std_of_floor(a.db, f) or f) != f]
        if mism:
            print("  （自然层与标准层不是同名：%s -> 标准层 %s；一个标准层被多个自然层复用）"
                  % (mism[:6], [std_of_floor(a.db, f) for f in mism[:6]]))
        # config 的 截面.分组 里没列到的分组 = 那些柱子这一轮不会被优化（保持现状），
        # 这种事不说出来就没人知道，所以打一句
        in_cfg = set(cfg["截面"]["分组"])
        extra = sorted({g for d in counts_by_floor.values() for g in d} - in_cfg)
        if extra:
            print("⚠ 警告：模型里有这些分组，但 config 的 截面.分组=%s 没列出：%s —— "
                  "它们不会被优化（保持现状）。要一起优化就把它们加进 截面.分组。"
                  % (cfg["截面"]["分组"], extra))
    else:
        n_cols = max(len(v) for v in parsed.values())
        assert_pure_frame(cfg, n_cols)
        print("★ 未给 --db：分组按柱号 `group_of_nc`（柱号 = i*NY+j+1）—— **只对 "
              "frame_build.py 生成的纯框架成立**；真实工程请加 --db 按坐标分组。")

    ctrl = {}
    unmapped = collections.Counter()
    for f in sorted(parsed):
        rows_f = parsed[f]
        for nc, r in rows_f.items():
            if a.db:
                g = units[f].get(nc)
                if g is None:
                    unmapped[f] += 1
                    continue
            else:
                g = group_of_nc(cfg, nc)
            k = (f, g)
            if k not in ctrl or (r["Uc"] or 0) > (ctrl[k]["Uc"] or 0):
                ctrl[k] = r
    if unmapped:
        # --db 模式下 layer_segment_map 已经保证"要么全折得出、要么直接报错"，
        # 所以走到这里说明是别的原因（例如某柱段在模型里确实没有）—— 照样说清楚
        raise SystemExit(
            "!! 这些层的 wpj 柱号在模型分组里找不到：%s\n"
            "   （section_opt 要写回模型，漏算柱段会选出偏小的截面，所以这里直接退出）"
            % dict(sorted(unmapped.items())))
    if not ctrl:
        raise SystemExit("没解析到柱结果，确认 %s 下有 wpj*.out" % res)

    grades = [a.only] if a.only else list(cfg["混凝土"]["候选等级"])
    sections, total, detail = optimize(cfg, ctrl, grades,
                                      counts_by_floor=counts_by_floor or None)

    print("轴压比目标 %.2f（限值 %.2f）｜候选边长 %d~%d 步长 %d｜等级 %s"
          % (cfg["抗震"]["轴压比目标"], cfg["抗震"]["轴压比限值"],
             cfg["截面"]["最小边长"], cfg["截面"]["最大边长"], cfg["截面"]["步长"], grades))
    if counts_by_floor:
        print("每层柱数（模型按坐标数）：%s"
              % {f: counts_by_floor[f] for f in sorted(counts_by_floor)[:3]}
              + ("…" if len(counts_by_floor) > 3 else ""))
    else:
        print("每层柱数（按柱号口径）：%s" % counts_by_group(cfg))
    print("\n  %-4s %-5s %-6s %-22s %-7s %s" %
          ("层", "等级", "Uc最大", "截面(组)", "该层造价", "控制轴力kN"))
    for f, grade, picked, ucmax, cfloor in detail:
        desc = " ".join("%s%d" % (g, picked[g]) for g in cfg["截面"]["分组"])
        nus = "/".join("%.0f" % abs(ctrl[(f, g)]["Nu"] or 0) for g in cfg["截面"]["分组"])
        print("  %-4d %-5s %-6.2f %-22s %-9.0f %s" % (f, grade, ucmax, desc, cfloor, nus))

    json.dump(sections, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("\n解析预估总造价（口径：%s）：%.0f 元" % (cfg["造价"].get("口径", "只算柱"), total))
    print("已写出 -> %s" % a.out)

    if a.compare:
        cur = json.load(open(a.compare, encoding="utf-8-sig"))
        if "sections" in cur:
            cur = cur["sections"]
        diff = [(f, cur.get(f), sections.get(f)) for f in sections if cur.get(f) != sections.get(f)]
        if diff:
            print("\n与 %s 相比建议改动 %d 处：" % (a.compare, len(diff)))
            for f, before, after in diff:
                print("   第%-3s 层：%s  ->  %s" % (f, before, after))
        else:
            print("\n与 %s 相比：无改动 —— 已收敛（当前方案即本模型下的最优）" % a.compare)
    return 0


def _utf8_console():
    """让输出在任何控制台编码下都不崩（GBK 下把不可编码字符替换掉）。

    为什么需要：本包会打印 ✅ ❌ ⚠ −(U+2212) ² ³ 等**非 cp936** 字符，
    默认 GBK 控制台下 print 会抛 UnicodeEncodeError 并**以退出码 1 中断**，
    于是一个其实已经成功的任务（比如文件已经落盘）会被上层判成失败。
    errors=replace 让它在 UTF-8 控制台下原样输出、在 GBK 下退化成 ?，都不崩。

    ★ 在 `main()` 开头调用一次（而不是只在 `if __name__ == "__main__"` 里）：
      本文件会被别的脚本 import 当库用，那些调用方同样要在 GBK 控制台下打印本文件的
      输出（本文件会打印 ⚠ 警告）。重复调用无害。
    """
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(errors="replace")
        except Exception:
            pass


if __name__ == "__main__":
    sys.exit(main())
