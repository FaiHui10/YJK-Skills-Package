# -*- coding: utf-8 -*-
"""从一个已完成计算结果（case + .out）导出强度场 csv: x,y,dens（dens = Nk / 从属面积）。"""
import re, sqlite3, os, sys
import numpy as np

case = sys.argv[1]
out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(case, "基础计算及结果输出", "YJK-F桩承载力验算.out")
dst = sys.argv[3] if len(sys.argv) > 3 else os.path.join(case, "dens.csv")

L = open(out, encoding="gbk", errors="replace").read().splitlines()
cur, mx, ids = None, {}, []
row = re.compile(r"^[W E]?\s*\(\s*(\d+)\s*\)\s+([-\d.]+)\s+([-\d.]+)")
for l in L:
    s = l.strip()
    if re.fullmatch(r"ZH-\d+", s):
        cur = s; mx[s] = []; ids.append(s); continue
    if s.startswith(("一、", "二、", "三、")):
        cur = None; continue
    if cur:
        m = row.match(s)
        if m:
            mx[cur].append(float(m.group(2)))
nk = np.array([max(mx[k]) for k in ids])

con = sqlite3.connect(os.path.join(case, "Jccad_0.ydb"))
if len(sys.argv) > 4:
    P = np.loadtxt(sys.argv[4], delimiter=",", skiprows=1)
    pts = P[:, :2]
    R = np.array(sorted({round(q, 0) for q in pts[:, 0]}))
    C = np.array(sorted({round(q, 0) for q in pts[:, 1]}, reverse=True))
    rect = con.execute("select ptx,pty from RaftCornerPoint").fetchall()
else:
    pts = np.array(con.execute("select x,y from app_Pile where DaisFlag=-1 order by ID").fetchall())
    R = np.array(sorted({round(x, 0) for x, y in pts}))
    C = np.array(sorted({round(y, 0) for x, y in pts}, reverse=True))
    rect = con.execute("select ptx,pty from RaftCornerPoint").fetchall()
con.close()
xmin, xmax = min(p[0] for p in rect), max(p[0] for p in rect)
ymin, ymax = min(p[1] for p in rect), max(p[1] for p in rect)
assert len(pts) == len(nk)

rowout = []
areas = []
for (x, y), q in zip(pts, nk):
    k = int(np.argmin(abs(R - round(x, 0)))); j = int(np.argmin(abs(C - round(y, 0))))
    x_lo = (R[k - 1] + R[k]) / 2 if k > 0 else xmin
    x_hi = (R[k] + R[k + 1]) / 2 if k < len(R) - 1 else xmax
    y_hi = (C[j - 1] + C[j]) / 2 if j > 0 else ymax
    y_lo = (C[j] + C[j + 1]) / 2 if j < len(C) - 1 else ymin
    a = (x_hi - x_lo) * (y_hi - y_lo) / 1e6
    areas.append(a)
    rowout.append((x, y, q / a))
np.savetxt(dst, np.array(rowout), fmt="%.5f", delimiter=",", header="x,y,dens", comments="")
print("导出 %s：%d 点，强度 %.0f~%.0f kN/m2，从属面积 %.2f~%.2f m2"
      % (dst, len(rowout), min(r[2] for r in rowout), max(r[2] for r in rowout),
         min(areas), max(areas)))
print("按行/列汇总：")
for j in range(len(C)):
    m = [i for i, p in enumerate(pts) if abs(p[1] - C[j]) < 50]
    print("  y=%.0f 桩 %d 根 均值 %5.0f 强度均值 %5.0f" %
          (C[j], len(m), np.mean([nk[i] for i in m]), np.mean([rowout[i][2] for i in m])))
