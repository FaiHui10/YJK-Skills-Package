# -*- coding: utf-8 -*-
"""抗浮板下桩「移 + 补」：把 |N| 小的闲桩搬到峰值处，池子用完再补新桩。

用于"荷载变了、旧布置又缺又闲"的情形：先移（不涨桩数）再补，比直接加桩省。

用法：
    python af_relayout.py --dir <工程目录> --f2 "1:400,0:2200" --combo 1-51 --rounds 2

前置：模型已带完整组合与上部内力（见 yjk-auto-drive 的 foundation 文档 §2.1）；
      没有别的 yjks 在跑；已装 yjk-auto-drive（可用 YJK_DRIVER_DIR / YJK_SKILLS_DIR 指定）。
"""
from __future__ import annotations

import argparse
import math
import os
import shutil
import sqlite3
import struct
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))


def find_driver():
    cands = []
    if os.environ.get('YJK_DRIVER_DIR'):
        cands.append(os.environ['YJK_DRIVER_DIR'])
    base = os.environ.get('YJK_SKILLS_DIR')
    if base:
        cands.append(os.path.join(base, 'yjk-auto-drive', 'scripts'))
    cands += [os.path.join(HERE, '..', '..', 'yjk-auto-drive', 'scripts'),
              os.path.join(HERE, '..', 'yjk-auto-drive', 'scripts'),
              os.path.join(os.getcwd(), 'yjk-auto-drive', 'scripts')]
    for c in cands:
        p = os.path.abspath(c)
        if os.path.isfile(os.path.join(p, 'yjk_auto.py')):
            return p
    raise SystemExit('!! 找不到 yjk-auto-drive/scripts，试过：\n  ' + '\n  '.join(map(os.path.abspath, cands)))


sys.path.insert(0, find_driver())
import yjk_auto as YA                                            # noqa: E402


def log(m):
    print('[%s] %s' % (time.strftime('%H:%M:%S'), m), flush=True)


class Ctx:
    def __init__(self, proj, combo, f2, spacing, edge):
        self.proj = proj
        self.combo = combo
        self.f2 = f2
        self.spacing = spacing
        self.edge = edge
        self.ydb = os.path.join(proj, 'Jccad_0.ydb')
        self.res = os.path.join(proj, '基础计算及结果输出', 'jccad.ydb')
        self.yjks = [f for f in os.listdir(proj) if f.lower().endswith('.yjk')]
        if len(self.yjks) != 1:
            raise SystemExit('!! 工程目录里的 .yjk 不是恰好一个：%s' % self.yjks)
        self.yjk = os.path.join(proj, self.yjks[0])

    def ro(self, p):
        return sqlite3.connect('file:%s?mode=ro' % p.replace('\\', '/'), uri=True)

    def state(self):
        r = self.ro(self.res)
        piles = {x[0]: dict(cap=x[1], kind=x[2], x=x[3], y=x[4]) for x in
                 r.execute('select ID,nRaft_CT,kind,xx,yy from tblPileApp')}
        d = {}
        for pid, cid, ct, blob in r.execute(
                'select PileID,CombID,CombType,N from tblPileNL where CombType=? and CombID=?', self.combo):
            d[pid] = struct.unpack('<9f', blob)[0]
        r.close()
        return piles, d

    def poly(self):
        c = self.ro(self.ydb)
        p = [(x[0], x[1]) for x in c.execute('select ptx,pty from RaftCornerPoint order by ID')]
        c.close()
        return p


def _dseg(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy
    if L2 <= 0:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L2))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def inside(px, py, poly, margin):
    ins = False
    n = len(poly)
    for i in range(n):
        ax, ay = poly[i]
        bx, by = poly[(i + 1) % n]
        if (ay > py) != (by > py) and ax + (py - ay) * (bx - ax) / (by - ay) > px:
            ins = not ins
    if not ins:
        return False
    return all(_dseg(px, py, poly[i][0], poly[i][1], poly[(i + 1) % n][0], poly[(i + 1) % n][1]) >= margin
               for i in range(n))


class Grid:
    def __init__(self, cell):
        self.cell = cell
        self.d = {}

    def key(self, x, y):
        return (int(math.floor(x / self.cell)), int(math.floor(y / self.cell)))

    def add(self, x, y):
        self.d.setdefault(self.key(x, y), set()).add((x, y))

    def remove(self, x, y):
        self.d.get(self.key(x, y), set()).discard((x, y))

    def min_dist(self, x, y):
        kx, ky = self.key(x, y)
        best = 1e18
        for i in (-1, 0, 1):
            for j in (-1, 0, 1):
                for (px, py) in self.d.get((kx + i, ky + j), ()):
                    d2 = (px - x) ** 2 + (py - y) ** 2
                    if d2 < best:
                        best = d2
        return math.sqrt(best) if best < 1e17 else 1e9


def free_spot(x, y, grid, poly, spacing, edge):
    for rr in (1750, 2000, 2300, 2600, 3000, 3400, 3800, 4200):
        for a in range(0, 360, 12):
            th = math.radians(a)
            px, py = x + rr * math.cos(th), y + rr * math.sin(th)
            if not inside(px, py, poly, edge):
                continue
            if grid.min_dist(px, py) < spacing:
                continue
            return px, py
    return None


def run_yjk(ctx, root, dll):
    for i in [i for i in YA.instances() if i.get('kind') not in ('dead',)]:
        YA.kill_pid(i['pid'])
    time.sleep(5)
    before = set(YA.yjks_pids())
    for fl in YA.FLAGS_LADDER:
        try:
            subprocess.Popen([os.path.join(root, 'yjks.exe'), '-product', 'YJKS', '-open', ctx.yjk],
                             cwd=ctx.proj, creationflags=fl, stdin=subprocess.DEVNULL,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            break
        except OSError:
            continue
    t0 = time.time()
    pid = None
    while time.time() - t0 < 300:
        new = set(YA.yjks_pids()) - before
        if new:
            pid = max(new)
            break
        time.sleep(2)
    if not pid:
        return False
    YA.own_claim(pid, os.path.join(root, 'yjks.exe'), ctx.proj)
    name = os.path.splitext(os.path.basename(ctx.yjk))[0]
    t1 = time.time()
    while time.time() - t1 < 300:
        if name in ''.join(YA.titles(pid)):
            break
        time.sleep(2)
    cli = YA.Client(dll)
    cli.configure('8.1.0', invisible=False, pid=pid)
    alive = lambda: pid in YA.yjks_pids()
    snap = ctx.ydb + '.snap_af'
    shutil.copy2(ctx.ydb, snap)
    try:
        cli.run('SetCurrentLabel', 'JCCAD_RESULT', 300, alive=alive)
        time.sleep(2)
        imp = cli.run('jccad_read_by_ydb', '', 300, alive=alive)
        time.sleep(2)
        shutil.copy2(snap, ctx.ydb)
        g = cli.run('BaseDraw_GenData_script', '', 1200, alive=alive)
        a = cli.run('BaseDraw_BaseAnalysis', '', 3000, alive=alive)
        log('  计算: import=%s gen=%s ana=%s' % (imp, g, a))
        return True
    finally:
        try:
            YA.kill_pid(pid, verbose=True)
        finally:
            YA.own_clear()
            time.sleep(3)
            shutil.copy2(snap, ctx.ydb)


def main():
    ap = argparse.ArgumentParser(description='抗浮板下桩：移闲桩 + 补峰值')
    ap.add_argument('--dir', required=True)
    ap.add_argument('--f2', default='1:400,0:2200')
    ap.add_argument('--combo', default='1-51')
    ap.add_argument('--pool-n', type=float, default=200.0, help='|N| 低于此值的板下桩可搬')
    ap.add_argument('--move-cap', type=int, default=320)
    ap.add_argument('--add-cap', type=int, default=300)
    ap.add_argument('--spacing', type=float, default=1750.0)
    ap.add_argument('--edge', type=float, default=300.0)
    ap.add_argument('--rounds', type=int, default=2)
    ap.add_argument('--root', default='')
    args = ap.parse_args()

    proj = os.path.abspath(args.dir)
    f2 = {}
    for part in args.f2.split(','):
        k, v = part.split(':')
        f2[int(k)] = float(v)
    combo = tuple(int(x) for x in args.combo.replace('-', ' ').split())

    import paths as P
    ins = P.find_yjk_install()
    root = os.path.abspath(args.root) if args.root else (ins.get('root') or '')
    if not root or not os.path.exists(os.path.join(root, 'yjks.exe')):
        log('!! 没找到 yjks.exe，用 --root 指定')
        return 3
    dll = os.path.join(root, 'YJKAPI.dll')
    ctx = Ctx(proj, combo, f2, args.spacing, args.edge)

    for rd in range(1, args.rounds + 1):
        piles, d = ctx.state()
        brd = {k: v for k, v in d.items() if piles[k]['cap'] == 0}
        over = sorted([(k, v) for k, v in d.items() if v < -f2[piles[k]['kind']] - 3], key=lambda t: t[1])
        log('第 %d 轮前: 桩 %d（板下 %d）超限 %d，D500 max %.1f，板下平均 %.0f'
            % (rd, len(d), len(brd), len(over), min(brd.values()), sum(brd.values()) / len(brd)))
        if len(over) <= 10:
            break
        pool = sorted([(k, v) for k, v in brd.items() if abs(v) < args.pool_n], key=lambda t: abs(t[1]))
        poly = ctx.poly()
        grid = Grid(args.spacing)
        for v in piles.values():
            grid.add(v['x'], v['y'])
        moves, adds = [], []
        pi = 0
        for k, v in over:
            need = max(1, int((abs(v) - 370) // 130) + 1)
            got = 0
            while got < need:
                if pi < len(pool) and len(moves) < args.move_cap:
                    pk, _ = pool[pi]
                    pi += 1
                    ppos = (piles[pk]['x'], piles[pk]['y'])
                    grid.remove(*ppos)
                    spot = free_spot(piles[k]['x'], piles[k]['y'], grid, poly, args.spacing, args.edge)
                    if not spot:
                        grid.add(*ppos)
                        continue
                    grid.add(*spot)
                    moves.append((ppos, spot))
                    got += 1
                    continue
                if len(adds) < args.add_cap:
                    spot = free_spot(piles[k]['x'], piles[k]['y'], grid, poly, args.spacing, args.edge)
                    if not spot:
                        break
                    grid.add(*spot)
                    adds.append(spot)
                    got += 1
                    continue
                break
            if pi >= len(pool) and len(adds) >= args.add_cap:
                break
        log('  移动 %d 根、新增 %d 根' % (len(moves), len(adds)))
        if not moves and not adds:
            break
        c = sqlite3.connect(ctx.ydb)
        cur = c.cursor()
        cols = [x[1] for x in cur.execute('pragma table_info(app_Pile)')]
        tmpl = dict(zip(cols, cur.execute('select * from app_Pile where DaisFlag<0 limit 1').fetchone()))
        maxid = cur.execute('select max(ID) from app_Pile').fetchone()[0]
        for (ox, oy), (nx, ny) in moves:
            cur.execute('update app_Pile set x=?, y=? where DaisFlag<0 and abs(x-?)<1 and abs(y-?)<1',
                        (nx, ny, ox, oy))
        n = 0
        for (nx, ny) in adds:
            n += 1
            r = dict(tmpl)
            r.update(ID=maxid + n, x=nx, y=ny, z=-12600, kind=1, DaisFlag=-1, idaispilelen=11.9)
            cur.execute('insert into app_Pile (%s) values (%s)' % (','.join(cols), ','.join('?' * len(cols))),
                        [r[q] for q in cols])
        c.commit()
        log('  app_Pile -> %s' % (cur.execute('select count(*), sum(DaisFlag<0) from app_Pile').fetchone(),))
        c.close()
        if not run_yjk(ctx, root, dll):
            return 2

    piles, d = ctx.state()
    brd = {k: v for k, v in d.items() if piles[k]['cap'] == 0}
    over = [k for k, v in d.items() if v < -f2[piles[k]['kind']] - 3]
    log('=== 结束: 桩 %d（板下 %d）超限 %d，D500 max %.1f，板下平均 %.0f'
        % (len(d), len(brd), len(over), min(brd.values()), sum(brd.values()) / len(brd)))
    return 0 if not over else 1


if __name__ == '__main__':
    sys.exit(main())
