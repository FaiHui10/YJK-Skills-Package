# -*- coding: utf-8 -*-
"""布桩成果核验：模型桩数/桩位/桩距/桩顶标高 + 结果反力限值判定。

用法:
  python check_layout.py --dir <工程目录> [--layout layout.csv] [--ra 9500] [--min 2500]
"""
import argparse, os, re, sqlite3
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("--dir", required=True, help="YJK 基础工程目录")
ap.add_argument("--layout", default=None, help="对照用的 layout.csv（表头 x,y,z）")
ap.add_argument("--ra", type=float, default=None, help="单桩承载力 Ra(kN)；缺省取 DEF_Pile")
ap.add_argument("--min", dest="d_min", type=float, default=2500.0, help="最小允许桩距 mm")
ap.add_argument("--out", default=None, help="结果文件，缺省 基础计算及结果输出/YJK-F桩承载力验算.out")
args = ap.parse_args()

P = os.path.abspath(args.dir)
db = os.path.join(P, "Jccad_0.ydb")
con = sqlite3.connect("file:" + db + "?mode=ro", uri=True)

cols = [r[1] for r in con.execute('PRAGMA table_info("app_Pile")')]
idx = {k: i for i, k in enumerate(cols)}
tot = con.execute("select count(*) from app_Pile").fetchone()[0]
rows = con.execute("select * from app_Pile where DaisFlag=-1 order by ID").fetchall()
xy = np.array([[r[idx["x"]], r[idx["y"]]] for r in rows], dtype=float)
z = np.array([r[idx["z"]] for r in rows], dtype=float)

ra = args.ra
if ra is None:
    try:
        ra = con.execute("select max(F1) from DEF_Pile").fetchone()[0]
        print("（未给 --ra，取 DEF_Pile 中最大 F1 = %.0f 作 Ra）" % ra)
    except Exception:
        ra = None
con.close()

print("总桩 %d | 板下桩 %d | 承台桩 %d" % (tot, len(rows), tot - len(rows)))
print("z 分布:", {float(v): int((z == v).sum()) for v in np.unique(z)})
if len(xy) > 1:
    d = np.sqrt(((xy[:, None, :] - xy[None, :, :]) ** 2).sum(-1))
    np.fill_diagonal(d, 1e9)
    i, j = np.unravel_index(d.argmin(), d.shape)
    ok = d.min() >= args.d_min - 1.0
    print("最小桩距 %.0f mm（要求 >= %.0f）%s  (%s)" % (
        d.min(), args.d_min, "OK" if ok else "不满足", (int(xy[i, 0]), int(xy[i, 1]), int(xy[j, 0]), int(xy[j, 1]))))
print("x 列:", sorted(set(np.round(xy[:, 0]).astype(int))))
print("y 行:", sorted(set(np.round(xy[:, 1]).astype(int)), reverse=True))

if args.layout:
    L = np.loadtxt(args.layout, delimiter=",", skiprows=1, ndmin=2)
    sa = set(map(tuple, np.round(np.hstack([xy, z[:, None]]), 0)))
    sb = set(map(tuple, np.round(L[:, :3], 0)))
    print("与 %s 对照: %s（仅模型多 %d，仅 CSV 多 %d）" % (
        os.path.basename(args.layout), sa == sb, len(sa - sb), len(sb - sa)))

out = args.out or os.path.join(P, "基础计算及结果输出", "YJK-F桩承载力验算.out")
if os.path.exists(out):
    row_re = re.compile(r"^([W E]?)\s*\(\s*(\d+)\s*\)\s+([-\d.]+)\s+([-\d.]+)")
    per, cn, cw, cur = {}, {}, {}, None      # cn/cw：非地震 / 地震 各组合的逐桩反力
    for line in open(out, encoding="gbk", errors="replace"):
        s = line.strip()
        if re.fullmatch(r"ZH-\d+", s):
            cur = s
            per.setdefault(cur, {"n": {}, "w": {}})
            continue
        if s.startswith(("一、", "二、", "三、", "四、")) or s.startswith("桩号"):
            cur = None
            continue
        if cur:
            m = row_re.match(s)
            if m:
                pre, k, nk = m.group(1), int(m.group(2)), float(m.group(3))
                key = "w" if pre == "E" else "n"       # W/无前缀=非地震(1.2Ra)，E=地震(1.5Ra)
                per[cur][key][k] = nk
                (cw if pre == "E" else cn).setdefault(k, []).append(nk)
    if per:
        print("结果 .out: %d 根桩 / %d 个组合（其中地震 %d）" % (len(per), len(cn) + len(cw), len(cw)))
        if ra:
            bad = []
            for tag, cd, k_peak, k_avg in (("非地震", cn, 1.2, 1.0), ("地震", cw, 1.5, 1.25)):
                if not cd:
                    continue
                mx = {p: max(v["n" if tag == "非地震" else "w"].get(k, -1e9) for k in cd)
                      for p, v in per.items()}
                mx = {p: v for p, v in mx.items() if v > -1e8}
                avg = max(sum(v) / len(v) for v in cd.values())
                over = sorted([p for p, v in mx.items() if v > k_peak * ra], key=lambda s: -mx[s])
                ok = not over and avg <= k_avg * ra
                print("  %s: 峰值 %.0f（%d%% × %.1fRa=%.0f）| 均值 %.0f（%d%% × %.2fRa）| 超限 %d 根 %s → %s" % (
                    tag, max(mx.values()), 100 * max(mx.values()) / (k_peak * ra), k_peak, k_peak * ra,
                    avg, 100 * avg / (k_avg * ra), k_avg, len(over), over[:3], "OK" if ok else "超限"))
                if not ok:
                    bad.append(tag)
            print("  判定: %s（Ra=%.0f）" % ("通过" if not bad else "不通过（%s超限）" % "/".join(bad), ra))
        else:
            mxa = max(max(v["n"].values(), default=0) for v in per.values())
            print("  峰值 Nk %.0f（未给 Ra，未做限值判定）" % mxa)
    else:
        print("  未见有效桩反力数据")
else:
    print("未见结果文件:", out)
