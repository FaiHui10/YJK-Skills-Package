# -*- coding: utf-8 -*-
"""稳健解析 YJK-F桩承载力验算.out：逐桩各组合 Nk，输出 8x7 网格。"""
import re, sqlite3, os, sys

if len(sys.argv) < 2:
    sys.exit("usage: bp_grid.py <工程目录>")
base = sys.argv[1]
out = os.path.join(base, "基础计算及结果输出", "YJK-F桩承载力验算.out")
L = open(out, encoding="gbk", errors="replace").read().splitlines()

row_re = re.compile(r"^[W E]?\s*\(\s*(\d+)\s*\)\s+([-\d.]+)\s+([-\d.]+)")
cur, mx, ra, ncom = None, {}, {}, {}
for l in L:
    s = l.strip()
    if re.fullmatch(r"ZH-\d+", s):
        cur = s; mx[s] = []; ncom[s] = 0; continue
    if s.startswith(("一、", "二、", "三、")):
        cur = None; continue
    if cur:
        m = row_re.match(s)
        if m:
            mx[cur].append(float(m.group(2))); ra[cur] = float(m.group(3)); ncom[cur] += 1

print("桩数 %d | 组合数 %s" % (len(mx), sorted(set(ncom.values()))))
con = sqlite3.connect(os.path.join(base, "Jccad_0.ydb"))
pts = con.execute("select x,y from app_Pile where DaisFlag=-1 order by ID").fetchall()
con.close()
ids = list(mx.keys())
vals = [max(mx[k]) for k in ids]
R = ra[ids[0]]
print("Ra %.0f | 1.2Ra %.0f | Nk 平均 %.0f 最大 %.0f 最小 %.0f | 超1.2Ra %d 根 | 超R %d 根"
      % (R, 1.2 * R, sum(vals) / len(vals), max(vals), min(vals),
         sum(1 for v in vals if v > 1.2 * R), sum(1 for v in vals if v > R)))
print("总反力 %.0f kN" % sum(vals))
xs = sorted({round(p[0], 1) for p in pts})
ys = sorted({round(p[1], 1) for p in pts}, reverse=True)
g = {(round(p[0], 1), round(p[1], 1)): v for p, v in zip(pts, vals)}
print("      " + "".join("%9.2f" % (x / 1000) for x in xs))
for y in ys:
    print("%7.2f %s" % (y / 1000, "".join("%9.0f" % g.get((x, y), float("nan")) for x in xs)))
print("列平均:", " ".join("%.0f" % (sum(g[(x, y)] for y in ys if (x, y) in g) / len([y for y in ys if (x, y) in g])) for x in xs))
print("行平均:", " ".join("%.0f" % (sum(g[(x, y)] for x in xs if (x, y) in g) / len([x for x in xs if (x, y) in g])) for y in ys))
