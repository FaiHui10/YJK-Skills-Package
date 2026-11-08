# -*- coding: utf-8 -*-
"""BP 核心区灌注桩布置寻优（等荷载分带布桩）。

以实测逐桩 Nk 构造筏板荷载强度场：
  1) 沿 x 分成 cols 个等荷载竖带；
  2) 每带内按荷载质量自适应确定桩数（低荷载带少桩、高荷载带多桩）；
  3) 带内沿 y 再等荷载细分，桩位取子单元的质量重心。
→ 低荷载区桩距自动拉大、高荷载区压到 2500 下限。

约束：最小桩距 2500 mm，桩距筏板边 >= 900 mm，桩顶 z 沿用最近原桩。

用法:
  python bp_optim.py --n 56 --cols 8 --tag bp56
  python bp_optim.py --n 56 --cols 8 --tag bp56 --make
"""
import argparse, os, re, shutil, sqlite3
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("--src", required=True, help="基准工程目录（须含 Jccad_0.ydb 与 基础计算及结果输出/YJK-F桩承载力验算.out）")
ap.add_argument("--work", default=None, help="输出/试验目录（默认当前目录）")
ap.add_argument("--n", type=int, default=56, help="目标板下桩数")
ap.add_argument("--cols", type=int, default=8, help="x 向分带数")
ap.add_argument("--tag", default="bp56", help="试验子目录名")
ap.add_argument("--make", action="store_true", help="同时复制工程并写入 layout.csv")
ap.add_argument("--step", type=float, default=50.0, help="强度场积分步长 mm")
ap.add_argument("--dens", default=None, help="实测强度场 csv: x,y,dens")
ap.add_argument("--min", dest="d_min", type=float, default=2500.0, help="最小桩距 mm")
ap.add_argument("--edge", type=float, default=900.0, help="桩距筏板边最小距离 mm")
args = ap.parse_args()

PRJ = os.path.abspath(args.src)
WORK = os.path.abspath(args.work or os.getcwd())
D_MIN = args.d_min
EDGE = args.edge


def load_nk(base):
    out = os.path.join(base, "基础计算及结果输出", "YJK-F桩承载力验算.out")
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
    return ids, [max(mx[k]) for k in ids]


def equal_split(coord, w, count):
    """在权重 w 上把 coord 分成 count 段（每段荷载相等），返回段边界。"""
    cum = np.cumsum(w); cum = cum / cum[-1]
    q = np.linspace(0, 1, count + 1)[1:-1]
    return np.interp(q, cum, coord)


def centroid(coord_x, coord_y, w):
    s = w.sum()
    if s <= 0:
        return coord_x.mean(), coord_y.mean()
    return (coord_x * w).sum() / s, (coord_y * w).sum() / s


con = sqlite3.connect(os.path.join(args.src, "Jccad_0.ydb"))
cols = [r[1] for r in con.execute('PRAGMA table_info("app_Pile")')]
rows = [dict(zip(cols, r)) for r in con.execute("select * from app_Pile where DaisFlag=-1 order by ID")]
rect = con.execute("select ptx, pty from RaftCornerPoint").fetchall()
ids, nk = load_nk(args.src)
assert len(ids) == len(rows)
old = np.array([[r["x"], r["y"]] for r in rows])
oldz = np.array([r["z"] for r in rows])
xmin, xmax = min(p[0] for p in rect), max(p[0] for p in rect)
ymin, ymax = min(p[1] for p in rect), max(p[1] for p in rect)
print("基准 %d 桩 | Nk 合计 %.0f | 筏板 x[%.0f,%.0f] y[%.0f,%.0f]"
      % (len(rows), sum(nk), xmin, xmax, ymin, ymax))

bx = np.array(sorted({round(r["x"], 0) for r in rows}))
by = np.array(sorted({round(r["y"], 0) for r in rows}, reverse=True))

# 各桩的从属面积（矩形近似：到相邻桩/板边的中分线），强度 = Nk / 面积
def tributary(i):
    x, y = old[i]
    k = int(np.argmin(abs(bx - round(x, 0))))
    j = int(np.argmin(abs(by - round(y, 0))))
    x_lo = (bx[k - 1] + bx[k]) / 2 if k > 0 else xmin
    x_hi = (bx[k] + bx[k + 1]) / 2 if k < len(bx) - 1 else xmax
    y_hi = (by[j - 1] + by[j]) / 2 if j > 0 else ymax      # by 为降序
    y_lo = (by[j] + by[j + 1]) / 2 if j < len(by) - 1 else ymin
    return (x_hi - x_lo) * (y_hi - y_lo)


dens = np.array([nk[i] / tributary(i) for i in range(len(rows))])
print("强度场 %.3f~%.3f kN/m2（边桩修正后）" % (dens.min(), dens.max()))
v = np.zeros((len(by), len(bx)))
for i, r in enumerate(rows):
    v[int(np.argmin(abs(by - round(r["y"], 0)))), int(np.argmin(abs(bx - round(r["x"], 0))))] = dens[i]

if args.dens:
    D = np.loadtxt(args.dens, delimiter=",", skiprows=1)
    bx = np.array(sorted({round(q, 0) for q in D[:, 0]}))
    by = np.array(sorted({round(q, 0) for q in D[:, 1]}, reverse=True))
    v = np.zeros((len(by), len(bx)))
    for x, y, dv in D:
        v[int(np.argmin(abs(by - round(y, 0)))), int(np.argmin(abs(bx - round(x, 0))))] = dv
    print("改用 %s 的实测强度场：%d 点" % (os.path.basename(args.dens), len(D)))


def field(gx, gy):
    ix = np.clip(np.searchsorted(bx, gx) - 1, 0, len(bx) - 2)
    tx = (gx - bx[ix]) / (bx[ix + 1] - bx[ix])
    uy = by[::-1]
    iy = np.clip(np.searchsorted(uy, gy) - 1, 0, len(uy) - 2)
    ty = (gy - uy[iy]) / (uy[iy + 1] - uy[iy])
    TX, TY = tx[None, :], ty[:, None]
    return (v[np.ix_(iy, ix)] * (1 - TX) * (1 - TY) + v[np.ix_(iy, ix + 1)] * TX * (1 - TY)
            + v[np.ix_(iy + 1, ix)] * (1 - TX) * TY + v[np.ix_(iy + 1, ix + 1)] * TX * TY)


step = args.step
gx = np.arange(xmin + step / 2, xmax, step)
gy = np.arange(ymin + step / 2, ymax, step)
F = field(gx, gy) * step * step          # 全筏板范围，单位 kN/单元
total = F.sum()
xlo, xhi = xmin + EDGE, xmax - EDGE
ylo, yhi = ymin + EDGE, ymax - EDGE

# ---- x 等荷载分带 ----
xb = np.r_[xmin, equal_split(gx, F.sum(axis=0), args.cols), xmax]
print("分带 x 边界:", " ".join("%.0f" % b for b in xb))

# ---- 每带内桩数（按荷载比例，最大余数法） ----
segs = []
for j in range(args.cols):
    m = ((gx >= xb[j]) & (gx <= xb[j + 1])).astype(float)
    mass = (F * m[None, :]).sum()
    segs.append([mass, m, (xb[j], xb[j + 1])])
target = total / args.n
frac = np.array([s[0] / target for s in segs])
base_n = np.floor(frac).astype(int)
rest = args.n - base_n.sum()
if rest > 0:
    order = np.argsort(-(frac - base_n))[:rest]
    base_n[order] += 1
elif rest < 0:
    order = np.argsort(frac - base_n)[: -rest]
    base_n[order] -= 1
print("各带荷载占比 %:", np.round(frac * 100, 1).tolist())
print("各带桩数:", base_n.tolist(), "合计", base_n.sum())

# ---- 带内沿 y 等荷载细分 ----
pts, cell = [], []
for j, (mass, m, xr) in enumerate(segs):
    nj = int(base_n[j])
    if nj == 0:
        continue
    w_y = (F * m[None, :]).sum(axis=1)
    yb = np.r_[ymin, equal_split(gy, w_y, nj), ymax]
    for k in range(nj):
        sel = ((gy >= yb[k]) & (gy <= yb[k + 1])).astype(float)
        w2 = F * (m[None, :] * sel[:, None])
        cx, cy = centroid(np.broadcast_to(gx, w2.shape),
                          np.broadcast_to(gy[:, None], w2.shape), w2)
        pts.append([cx, cy]); cell.append(w2.sum())

pts = np.array(pts)
cell = np.array(cell)

# ---- 桩距下限修正：只对不足 2500 的相邻桩做最小位移 ----
for _ in range(60):
    moved = False
    for i in range(len(pts)):
        d = np.hypot(pts[:, 0] - pts[i, 0], pts[:, 1] - pts[i, 1])
        d[i] = 1e9
        q = int(np.argmin(d))
        if d[q] < D_MIN - 0.5:
            moved = True
            v = pts[q] - pts[i]
            L = np.hypot(*v) or 1.0
            push = (D_MIN - L + 1.0) / 2 / L
            v = v / L
            pts[i] -= v * (D_MIN - L + 1.0) / 2
            pts[q] += v * (D_MIN - L + 1.0) / 2
    pts[:, 0] = np.clip(pts[:, 0], xlo, xhi)
    pts[:, 1] = np.clip(pts[:, 1], ylo, yhi)
    if not moved:
        break

zs = []
for p in pts:
    zs.append(oldz[int(np.argmin(np.hypot(old[:, 0] - p[0], old[:, 1] - p[1])))])
zs = np.array(zs)

# ---- 最小桩距校核 ----
dd = np.hypot(pts[:, None, 0] - pts[None, :, 0], pts[:, None, 1] - pts[None, :, 1])
np.fill_diagonal(dd, 1e9)
dmin = dd.min()
print("\n桩数 %d | 最小桩距 %.0f mm | 子单元荷载 %.0f~%.0f（均值 %.0f，离散 %.1f%%）"
      % (len(pts), dmin, cell.min(), cell.max(), cell.mean(),
         (cell.std() / cell.mean() * 100)))
print("x %.0f~%.0f | y %.0f~%.0f | 最小边距 %.0f mm"
      % (pts[:, 0].min(), pts[:, 0].max(), pts[:, 1].min(), pts[:, 1].max(),
         min(pts[:, 0].min() - xmin, xmax - pts[:, 0].max(),
             pts[:, 1].min() - ymin, ymax - pts[:, 1].max())))

if dmin < D_MIN:
    i, q = np.unravel_index(np.argmin(dd), dd.shape)
    print("!! 桩距不足: (%.0f,%.0f)-(%.0f,%.0f) = %.0f mm"
          % (pts[i, 0], pts[i, 1], pts[q, 0], pts[q, 1], dmin))

order = np.lexsort((pts[:, 0], -pts[:, 1]))
print("\n桩位（行优先，y 由北向南）:")
for k in order:
    print("  %9.1f %9.1f  z=%.0f  单元 %6.0f kN" % (pts[k, 0], pts[k, 1], zs[k], cell[k]))

outdir = os.path.join(WORK, args.tag)
os.makedirs(outdir, exist_ok=True)
np.savetxt(os.path.join(outdir, "layout.csv"), np.c_[pts[order], zs[order]], fmt="%.3f",
           delimiter=",", header="x,y,z", comments="")

# ---- 生成试验工程 ----
if args.make:
    dst = outdir
    tmp = dst + "_tmp"
    if os.path.exists(tmp):
        shutil.rmtree(tmp)
    if os.path.exists(os.path.join(dst, "Jccad_0.ydb")):
        os.remove(os.path.join(dst, "Jccad_0.ydb"))
    shutil.copytree(args.src, tmp)
    res = os.path.join(tmp, "基础计算及结果输出")
    for f in os.listdir(res):
        if f in ("jccad.result", "jccad.ydb") or f.endswith(".out"):
            os.remove(os.path.join(res, f))

    con2 = sqlite3.connect(os.path.join(tmp, "Jccad_0.ydb"))
    cur = con2.cursor()
    cur.execute("delete from app_Pile where DaisFlag=-1")
    base = cur.execute("select max(ID) from app_Pile").fetchone()[0] or 0
    colsn = [r[1] for r in cur.execute('PRAGMA table_info("app_Pile")')]
    for i, k in enumerate(order, 1):
        d = dict(rows[0])
        d["ID"] = base + i; d["x"] = float(pts[k, 0]); d["y"] = float(pts[k, 1])
        d["z"] = float(zs[k]); d["DaisFlag"] = -1
        cur.execute("insert into app_Pile (%s) values (%s)"
                    % (",".join('"%s"' % c for c in colsn), ",".join("?" for _ in colsn)),
                    [d[c] for c in colsn])
    con2.commit()
    n1 = cur.execute("select count(*) from app_Pile where DaisFlag=-1").fetchone()[0]
    print("\n已生成 %s：板下桩 %d 根，总桩数 %d"
          % (args.tag, n1, cur.execute("select count(*) from app_Pile").fetchone()[0]))
    con2.close()
    shutil.copy2(os.path.join(dst, "layout.csv"), os.path.join(tmp, "layout.csv"))
    shutil.rmtree(dst)
    shutil.move(tmp, dst)
con.close()
