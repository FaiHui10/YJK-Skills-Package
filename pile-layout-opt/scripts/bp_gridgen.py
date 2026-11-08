# -*- coding: utf-8 -*-
"""按给定 x/y 间距生成规则网格桩位（z：西列与南行沿用 -10000，其余 -13700）。

用法: python bp_gridgen.py --prj <工程目录> --work <输出目录> --tag L2 --xg 3.5,3.1,2.9,2.75,2.7,2.5 --yg ... --mg 1.0
"""
import argparse, os, sqlite3
import numpy as np

# 工程目录 / 输出目录由 --prj / --work 传入

ap = argparse.ArgumentParser()
ap.add_argument("--tag", required=True)
ap.add_argument("--prj", required=True, help="工程目录（含 Jccad_0.ydb）")
ap.add_argument("--work", required=True, help="布局输出目录")
ap.add_argument("--xg", required=True, help="西→东 7 个间距(m)")
ap.add_argument("--yg", required=True, help="北→南 6 个间距(m)")
ap.add_argument("--mgw", type=float, default=1.0)
ap.add_argument("--mgs", type=float, default=1.0)
ap.add_argument("--mge", type=float, default=None)
ap.add_argument("--mgn", type=float, default=None)
a = ap.parse_args()
PRJ = a.prj
WORK = a.work

con = sqlite3.connect(os.path.join(PRJ, "Jccad_0.ydb"))
rect = con.execute("select ptx, pty from RaftCornerPoint").fetchall()
con.close()
xmin, xmax = min(p[0] for p in rect) / 1000, max(p[0] for p in rect) / 1000
ymin, ymax = min(p[1] for p in rect) / 1000, max(p[1] for p in rect) / 1000

xg = [float(v) for v in a.xg.split(",")]
yg = [float(v) for v in a.yg.split(",")]
mge = a.mge if a.mge is not None else a.mgw
mgn = a.mgn if a.mgn is not None else a.mgs
xs = [xmin + a.mgw]
for g in xg:
    xs.append(xs[-1] + g)
ys = [ymax - mgn]                      # 北端
for g in yg:
    ys.append(ys[-1] - g)

print("x:", " ".join("%.2f" % v for v in xs))
print("y:", " ".join("%.2f" % v for v in ys))
print("边距 西%.2f 东%.2f 北%.2f 南%.2f" % (xs[0] - xmin, xmax - xs[-1], ymax - ys[0], ys[-1] - ymin))
dx = np.diff(xs); dy = -np.diff(ys)
print("x 间距 %.2f~%.2f | y 间距 %.2f~%.2f" % (dx.min(), dx.max(), dy.min(), dy.max()))
d = np.hypot(dx.min(), dy.min())
print("对角最小间距 %.0f mm" % (d * 1000))

rows = []
for j, y in enumerate(ys):
    for i, x in enumerate(xs):
        z = -10000.0 if (i == 0 or j == len(ys) - 1) else -13700.0
        rows.append((x * 1000, y * 1000, z))

out = os.path.join(WORK, a.tag)
os.makedirs(out, exist_ok=True)
np.savetxt(os.path.join(out, "layout.csv"), np.array(rows), fmt="%.3f", delimiter=",",
           header="x,y,z", comments="")
print("写入 %s/layout.csv：%d 根" % (out, len(rows)))
