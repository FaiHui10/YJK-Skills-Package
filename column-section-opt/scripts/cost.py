# -*- coding: utf-8 -*-
"""从 YJK 设计结果 wpj*.out 解析柱配筋，按单价算混凝土/模板/纵筋/箍筋造价。

口径（默认"只算柱"）
  混凝土 = 全截面面积 × 柱段长 × 单价(按该柱所在层的等级)
  模板   = 柱周长 × 柱段长 × 单价
  纵筋   = 各组合中四边计算配筋之和的最大值（不低于构造最小配筋率）× 柱段长 × 密度
  箍筋   = 体积配箍率 Rsv × 核心区面积 × 柱段长 × 密度

用法：
    python cost.py --config c.json --res <工程目录或设计结果> [--json cost.json]
                   [--db <模型.ydb>]     # 真实工程（框-筒等）必给：分组按柱坐标现算

★ `--db` 只影响每行/每组的**分组标签**（中柱/边柱/角柱），钱的算法完全不变：
  造价按每根柱段的截面、配筋、层高逐条累加，与分组无关；分组只决定"按组汇总"那张表
  怎么归类。不给 `--db` 时按柱号 `group_of_nc` 分组（**只对 frame_build.py 生成的纯框架
  成立**），此时先用 `assert_pure_frame` 卡柱数，对不上就报错退出。
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (assert_pure_frame, find_wpj, group_of_nc,  # noqa: E402
                    groups_from_model, layer_segment_map, load_config, price_of,
                    resolve_res_dir, std_of_floor)

RE_COL = re.compile(r"^\s*N-C=(\d+)\s+\(I=\d+,\s*J=\d+\)(?:\(\d+\))?B\*H\(mm\)=\s*(\d+)\*(\d+)")
RE_COVER = re.compile(r"Cover=\s*([\d.]+)\(mm\)")
RE_RCC = re.compile(r"Rcc=\s*([\d.]+)")
RE_UC = re.compile(r"Nu=\s*([-\d.]+)\s+Uc=\s*([-\d.]+)\s+Rs=\s*([\d.]+)\(%\)\s+Rsv=\s*([\d.]+)\(%\)")
RE_COMBO = re.compile(r"^\s*\(\s*(\d+)\)\s*N=")
RE_AS = re.compile(r"(As[xy][tyb]=)\s*(\d+)")


def parse_wpj(path):
    rows, cur, combo = {}, None, {}
    # ★ YJK 的 .out 就是 GBK 写的：按 gbk 解码（errors="replace" 只影响非法字节，
    #   不会像 utf-8 那样"读出乱码却不报错、只是一条都解析不到"）。
    for line in open(path, "rb").read().decode("gbk", "replace").splitlines():
        m = RE_COL.match(line)
        if m:
            if cur:
                cur["Ast"] = max(combo.values()) if combo else 0
                rows[cur["nc"]] = cur
            cur = {"nc": int(m.group(1)), "B": int(m.group(2)), "H": int(m.group(3)),
                   "cover": None, "grade": None, "Nu": None, "Uc": None,
                   "Rs": None, "Rsv": None, "Ast": 0}
            combo = {}
            continue
        if cur is None:
            continue
        m = RE_RCC.search(line)
        if m and cur["grade"] is None:
            cur["grade"] = "C%d" % int(round(float(m.group(1))))
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


def heights_of(res):
    """从 wmass.out 的「层高m」表取各结构层层高（m）。

    返回 `(heights, src)`：
      heights = {结构层: 层高m}
      src     = `wmass.out`  真读到了
                `无文件`     wmass.out 不在（计算链没跑到写结果那一步 / 结果目录给错）
                `读不出`     文件在，但「层高m」表一条都没解析出来（截断 / 格式变了）

    ★ 为什么要把"读不到"分成两种并报出来：造价是 `柱截面面积 × 柱段长 × 单价`，
      柱段长 = 层高。老版在 wmass.out 缺失时**静默**返回 `{}`，调用方逐层退回配置里
      "假定"的层高 —— 于是算出一份**看起来完全合理**的钱，没有任何提示。
      本包在别处对"读不到"都是硬失败的，这里是唯一一处"回退成功"。
    """
    out = {}
    p = os.path.join(res, "wmass.out")
    if not os.path.exists(p):
        return out, "无文件"
    lines = open(p, "rb").read().decode("gbk", "replace").splitlines()
    for i, line in enumerate(lines):
        if "层高m" in line:
            for nxt in lines[i + 1:]:
                parts = nxt.split()
                if len(parts) < 2 or not parts[0].isdigit():
                    break
                try:
                    out[int(parts[0])] = float(parts[1])
                except ValueError:
                    break
            break
    return out, ("wmass.out" if out else "读不出")


def compute(cfg, proj_or_res, db=None, allow_assumed_height=False):
    """逐柱段算造价。`db` 给了就按**柱坐标**给每行打分组标签（不给则按柱号口径）。

    ★ 返回值不变（rows/total），加 `db` 只是多一个可选的**分组来源**：
      金额逐条按截面/配筋/层高算，分组不进任何一条金额 —— 所以两种模式的钱必然相同。

    ★ `allow_assumed_height=False`（默认）：读不到层高就**直接退出**，绝不静默用
      配置里的假定层高顶替。理由见 `heights_of`：层高错了总价仍是"合理"的数，
      调用方只看 rc 就会当真。要按假定层高估算，必须由调用方显式传 True。
    """
    res = resolve_res_dir(proj_or_res)
    wpj = find_wpj(res)
    heights, hsrc = heights_of(res)
    pc = cfg["造价"]
    rho_min = pc["纵筋最小配筋率"]
    parsed = {f: parse_wpj(p) for f, p in sorted(wpj.items())}

    # ★ 层高守卫：放这里（compute 内），因为 `colopt.cmd_iterate` 是**直接调 compute()**
    #   的，绕过 CLI 的 main()。
    missing_h = [f for f in sorted(parsed) if f not in heights]
    if missing_h and not allow_assumed_height:
        raise SystemExit(
            "!! 读不到 %s 的层高（%s）→ 拒绝用配置里的假定层高 %g mm 顶替。\n"
            "   缺层高的结构层：%s%s\n"
            "   造价 = 截面面积 × **柱段长** × 单价，柱段长就是层高；层高一旦是假定的，\n"
            "   总价会是一个**看起来完全合理**的错数，调用方只看退出码就会当真。\n"
            "   处置：① 确认本轮计算真的写出了 %s\\wmass.out（或 设计结果\\wmass.out）；\n"
            "         ② 结果目录里若是**上一轮**留下的文件，层高可能与本轮不同，别当本轮用；\n"
            "         ③ 确实要按假定层高估算：CLI 加 --assume-height，"
            "或调用 compute(..., allow_assumed_height=True)。"
            % (res, hsrc, cfg["几何"]["层高"], missing_h[:10],
               "…" if len(missing_h) > 10 else "", res))
    if missing_h:
        print("!! 这些结构层读不到层高（%s），按**配置假定值** %g mm 计算：%s%s"
              % (hsrc, cfg["几何"]["层高"], missing_h[:10],
                 "…" if len(missing_h) > 10 else ""))

    units = {}
    bad_layers = []
    if db:
        for f in sorted(parsed):
            # 自然层 -> 标准层：不硬假设 f 就是标准层号（一个标准层可被多层复用，
            # 只有 frame_build.py 的产出才恰好 1:1）
            std = std_of_floor(db, f) or f
            gs = groups_from_model(db, std)
            if not gs:
                raise SystemExit(
                    "!! 从 %s 读不到标准层 %d（自然层 %d）的柱分组（tblColSeg/tblJoint 为空？）\n"
                    "   也可能本工程的自然层与标准层对应关系缺失 —— 本工具用 tblFloor 查，"
                    "查不到就只能退出，不猜" % (db, std, f))
            gof = {c: g for g, cols in gs.items() for c in cols}
            # 段号 -> 模型柱号（多段层折回）；对不上就只影响**标签**，不动金额，
            # 所以这里不退出，而是把那些柱段标成"未归组"并大声警告。
            sm = layer_segment_map(gof, parsed[f])
            if sm is None:
                bad_layers.append(f)
                units[f] = {}
            else:
                units[f] = {nc: gof[col] for nc, col in sm.items()}
    elif parsed:
        # 不给 --db：分组只能按柱号口径，先确认柱数确实是纯框架的柱数
        assert_pure_frame(cfg, max(len(v) for v in parsed.values()))
        print("★ 未给 --db：分组按柱号 `group_of_nc`（柱号 = i*NY+j+1）—— **只对 "
              "frame_build.py 生成的纯框架成立**；真实工程请加 --db 按坐标分组。")

    rows = []
    unmapped = 0
    total = {k: 0.0 for k in ("混凝土", "模板", "纵筋", "箍筋", "合计",
                              "纵筋量t", "箍筋量t", "混凝土量m3", "模板量m2")}
    for f in sorted(parsed):
        L = heights.get(f, cfg["几何"]["层高"] / 1000.0)
        for nc, c in parsed[f].items():
            if db:
                # ★ 关键：**所有**柱段都要算钱（老版逐条算，删掉任何一条都会让合计变小）。
                #   认不出分组的就标"未归组"，钱照算 —— 分组只影响汇总表的归类。
                group = units[f].get(nc)
                if group is None:
                    unmapped += 1
                    group = "未归组"
            else:
                group = group_of_nc(cfg, nc)
            B, H = c["B"], c["H"]
            cov = c["cover"] or 20.0
            grade = c["grade"] or cfg["混凝土"]["候选等级"][0]
            Ac = B * H / 1e6
            core = max(B - 2 * cov, 0) * max(H - 2 * cov, 0) / 1e6
            v_con = Ac * L
            v_form = 2 * (B + H) / 1000.0 * L
            as_long = max(c["Ast"], rho_min * B * H) / 1e6
            v_long = as_long * L
            v_stir = (c["Rsv"] or 0) / 100.0 * core * L
            m_long = v_long * pc["钢筋密度kg每m3"] / 1000.0
            m_stir = v_stir * pc["钢筋密度kg每m3"] / 1000.0
            cost = {"混凝土": v_con * price_of(cfg, grade),
                    "模板": v_form * pc["模板单价元每m2"],
                    "纵筋": m_long * pc["钢筋单价元每t"],
                    "箍筋": m_stir * pc["钢筋单价元每t"]}
            cost["合计"] = sum(cost.values())
            rec = {"floor": f, "nc": nc, "group": group, "L": L,
                   "B": B, "H": H, "cover": cov, "grade": grade,
                   "Uc": c["Uc"], "Rs": c["Rs"], "Rsv": c["Rsv"],
                   "纵筋率%": as_long * 1e6 / (B * H) * 100,
                   "纵筋量t": m_long, "箍筋量t": m_stir,
                   "混凝土量m3": v_con, "模板量m2": v_form, **cost}
            rows.append(rec)
            for k in total:
                total[k] += rec[k] if k in rec else cost[k]
    # ★★ 空结果守卫 —— **必须放在 compute() 里**，不能只写在 CLI 包装 main() 里：
    #    `colopt.cmd_iterate` 是**直接调 compute()** 的（见 colopt.py），绕过了 main()，
    #    于是"什么都没算"会被写成一份「超限 0 条 / 造价 0 元」的**格式完整、
    #    看起来成功**的迭代记录，并且 rc=0。
    #    判据：rows 为空 = 一条柱段都没读到 = **没有实算记录** → 不可能有造价。
    if not rows:
        raise SystemExit(
            "!! 没有实算记录 → 不可能有造价：在 %s 里没解析到任何柱结果\n"
            "   判据：wpj*.out 要么不在（计算链没跑到写结果那一步），\n"
            "         要么在但里面没有可解析的 N-C= 柱行（截断 / 拿错文件）。\n"
            "   此时返回 ([], 全 0) 会把「什么都没算」伪装成「超限 0 条 / 造价 0 元」\n"
            "   的完整结果（调用方只看 rc 就会当真）。\n"
            "   处置：① 确认本轮计算真的写出了 设计结果/wpj*.out；\n"
            "         ② 目录里是**上一轮**留下的结果时，别当本轮用；\n"
            "         ③ 只想复核历史结果，就对那一轮的工程目录跑。" % res)
    if bad_layers:
        print("⚠ 警告：这些层的 wpj 柱号与 --db 模型对不上（段号折算失败），"
              "本层柱段的 group 标为「未归组」：%s" % bad_layers[:10])
        print("   （金额不受影响；但分组汇总表里这些层会归到「未归组」，"
              "请核对 --db 与 wpj 是否同一模型、标准层编号口径是否一致）")
    elif unmapped:
        print("⚠ 警告：%d 条柱段的柱号在本层模型分组里找不到，已标为「未归组」"
              "（金额照算，分组汇总表里单独一列）" % unmapped)
    return rows, total


def main():
    _utf8_console()          # ★ 必须在 argparse 之前：--help 也是写到 stdout 的
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--res", required=True)
    ap.add_argument("--json")
    ap.add_argument("--assume-height", action="store_true",
                    help="读不到 wmass.out 的层高时，允许用配置文件里的「几何.层高」顶替"
                         "（默认**拒绝**：层高错时总价仍是看起来合理的错数，"
                         "调用方只看退出码不会发现）")
    ap.add_argument("--db", default=None,
                    help="模型库(.ydb/.ymd)：给了就**按柱坐标**分组（common.groups_from_model），"
                         "真实工程/框-筒必给；不给则按柱号分组（只对 frame_build.py 的纯框架成立）。"
                         "★ 只影响分组标签，金额算法不变")
    a = ap.parse_args()
    cfg = load_config(a.config)
    if a.db:
        print("★ 分组来源：--db %s（按柱坐标现算；金额与分组无关，两种模式合计必然相同）"
              % os.path.basename(a.db))
    rows, total = compute(cfg, a.res, a.db, allow_assumed_height=a.assume_height)
    # 空结果守卫现在**已经搬进 compute()**（colopt.cmd_iterate 直接调它，绕不过去）。
    # 这一处保留作双保险：万一将来 compute() 的返回值语义被改动，CLI 也不会静默出一份 0 元。
    if not rows:
        raise SystemExit("没解析到柱结果，确认目录下有 设计结果\\wpj*.out")

    print("口径：%s｜混凝土单价 %s 元/m³｜模板 %.0f 元/m²｜钢筋 %.0f 元/t"
          % (cfg["造价"].get("口径", "只算柱"),
             cfg["混凝土"]["单价元每m3"], cfg["造价"]["模板单价元每m2"],
             cfg["造价"]["钢筋单价元每t"]))
    print("\n=== 按 (结构层, 分组) 汇总 ===")
    print("  %-6s %-6s %-6s %-10s %-8s %-10s %-6s %s" %
          ("结构层", "分组", "等级", "截面", "Uc最大", "纵筋率最大%", "根数", "小计元"))
    agg = {}
    for r_ in rows:
        k = (r_["floor"], r_["group"])
        x = agg.setdefault(k, {"n": 0, "Uc": 0.0, "rho": 0.0, "cost": 0.0,
                               "sec": set(), "grade": set()})
        x["n"] += 1
        x["Uc"] = max(x["Uc"], r_["Uc"] or 0)
        x["rho"] = max(x["rho"], r_["纵筋率%"] or 0)
        x["cost"] += r_["合计"]
        x["sec"].add("%d×%d" % (r_["B"], r_["H"]))
        x["grade"].add(r_["grade"])
    for k in sorted(agg):
        x = agg[k]
        print("  %-6d %-6s %-6s %-10s %-8.2f %-10.2f %-6d %.0f"
              % (k[0], k[1], "/".join(sorted(x["grade"])), "/".join(sorted(x["sec"])),
                 x["Uc"], x["rho"], x["n"], x["cost"]))

    n_col = len(rows)
    print("\n=== 合计（%d 根柱段）===" % n_col)
    for k in ("混凝土", "模板", "纵筋", "箍筋"):
        print("  %-6s %10.0f 元" % (k, total[k]))
    print("  %-6s %10.0f 元   （纵筋 %.2f t，箍筋 %.2f t；混凝土 %.2f m³，模板 %.2f m²）"
          % ("合计", total["合计"], total["纵筋量t"], total["箍筋量t"],
             total["混凝土量m3"], total["模板量m2"]))

    if a.json:
        json.dump({"rows": rows, "total": total}, open(a.json, "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        print("已写出 -> %s" % a.json)
    return 0


def _utf8_console():
    """让输出在任何控制台编码下都不崩（GBK 下把不可编码字符替换掉）。

    为什么需要：本包会打印 ✅ ❌ ⚠ −(U+2212) ² ³ 等**非 cp936** 字符，
    默认 GBK 控制台下 print 会抛 UnicodeEncodeError 并**以退出码 1 中断**，
    于是一个其实已经成功的任务（比如文件已经落盘）会被上层判成失败。
    errors=replace 让它在 UTF-8 控制台下原样输出、在 GBK 下退化成 ?，都不崩。

    ★ 在 `main()` 开头调用一次（而不是只在 `if __name__ == "__main__"` 里）：
      本文件会被别的脚本 import 当库用，那些调用方同样要在 GBK 控制台下打印本文件
      的输出。重复调用无害（函数内已有 try/except）。
    """
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(errors="replace")
        except Exception:
            pass


if __name__ == "__main__":
    sys.exit(main())
