# -*- coding: utf-8 -*-
"""贪心集合覆盖（抽稀）：按"移除代价"从低到高删板下桩，再用 YJK 实算校核。

影响模型（径向近似）：删一根桩，其拔力按 1/距离分给 R 内的邻居；只有预测邻居都不超过
TARGET 才允许删。实测预测精度约 0.1~1%（预测 417 vs 实算 416.6）。

用法：
    python af_greedy.py --dir <工程目录> --combo 1-51 --target 380 --max-remove 200 --run

前置：模型带完整组合与上部荷载（见 yjk-auto-drive 的 foundation 文档 §2.1）；无其它 yjks 在跑。
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
    raise SystemExit('!! 找不到 yjk-auto-drive/scripts')


sys.path.insert(0, find_driver())
import yjk_auto as YA                                            # noqa: E402


def log(m):
    print('[%s] %s' % (time.strftime('%H:%M:%S'), m), flush=True)


class Ctx:
    def __init__(self, proj, combo):
        self.proj = proj
        self.combo = combo
        self.ydb = os.path.join(proj, 'Jccad_0.ydb')
        self.res = os.path.join(proj, '基础计算及结果输出', 'jccad.ydb')
        yjks = [f for f in os.listdir(proj) if f.lower().endswith('.yjk')]
        if len(yjks) != 1:
            raise SystemExit('!! 工程目录里的 .yjk 不是恰好一个：%s' % yjks)
        self.yjk = os.path.join(proj, yjks[0])

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
    snap = ctx.ydb + '.snap_greedy'
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
    ap = argparse.ArgumentParser(description='贪心集合覆盖（抽稀板下桩）')
    ap.add_argument('--dir', required=True)
    ap.add_argument('--f2', default='1:400,0:2200')
    ap.add_argument('--combo', default='1-51')
    ap.add_argument('--target', type=float, default=380.0, help='允许的邻居预测上限（kN）')
    ap.add_argument('--max-remove', type=int, default=300)
    ap.add_argument('--neigh-r', type=float, default=6000.0, help='影响半径（mm）')
    ap.add_argument('--min-n', type=float, default=5.0, help='拔力小于此值的桩不作为删除对象')
    ap.add_argument('--run', action='store_true')
    ap.add_argument('--root', default='')
    args = ap.parse_args()

    proj = os.path.abspath(args.dir)
    combo = tuple(int(x) for x in args.combo.replace('-', ' ').split())
    f2 = {}
    for part in args.f2.split(','):
        k, v = part.split(':')
        f2[int(k)] = float(v)
    ctx = Ctx(proj, combo)

    piles, d = ctx.state()
    board = [k for k in d if piles[k]['cap'] == 0]
    pts = [(piles[k]['x'], piles[k]['y']) for k in board]
    N = [abs(d[k]) if d[k] < 0 else 0.0 for k in board]
    log('板下 %d 根，平均 %.0f，最大 %.0f' % (len(board), sum(N) / len(N), max(N)))

    cell = args.neigh_r
    g = {}
    for i, (x, y) in enumerate(pts):
        g.setdefault((int(x // cell), int(y // cell)), []).append(i)

    def neigh(i):
        x, y = pts[i]
        kx, ky = int(x // cell), int(y // cell)
        out = []
        for a in (-1, 0, 1):
            for b in (-1, 0, 1):
                for j in g.get((kx + a, ky + b), ()):
                    if j == i:
                        continue
                    dd = math.hypot(pts[j][0] - x, pts[j][1] - y)
                    if dd <= args.neigh_r:
                        out.append((j, dd))
        return out

    alive = [True] * len(board)
    removed = []
    while len(removed) < args.max_remove:
        best = None
        for i in range(len(board)):
            if not alive[i] or N[i] < args.min_n:
                continue
            nb = [(j, dd) for j, dd in neigh(i) if alive[j]]
            if not nb:
                continue
            w = [1.0 / max(dd, 1.0) for _, dd in nb]
            sw = sum(w)
            share = [(j, N[i] * wi / sw) for (j, _), wi in zip(nb, w)]
            if any(N[j] + s > args.target for j, s in share):
                continue
            if best is None or N[i] < best[0]:
                best = (N[i], i, share)
        if best is None:
            break
        _, i, share = best
        for j, s in share:
            N[j] += s
        N[i] = -1.0
        alive[i] = False
        removed.append(i)

    remain = sum(alive)
    log('贪心结束：删 %d 根，剩 %d 根，预测最大 %.0f，预测平均 %.0f'
        % (len(removed), remain, max(v for v in N if v >= 0), sum(v for v in N if v >= 0) / max(1, remain)))
    if not removed:
        return 0

    shutil.copy2(ctx.ydb, ctx.ydb + '.bak_greedy')
    c = sqlite3.connect(ctx.ydb)
    cur = c.cursor()
    for i in removed:
        x, y = pts[i]
        cur.execute('delete from app_Pile where DaisFlag<0 and abs(x-?)<1 and abs(y-?)<1', (x, y))
    c.commit()
    log('app_Pile -> %s' % (cur.execute('select count(*), sum(DaisFlag<0) from app_Pile').fetchone(),))
    c.close()

    if args.run:
        import paths as P
        ins = P.find_yjk_install()
        root = os.path.abspath(args.root) if args.root else (ins.get('root') or '')
        if not root or not os.path.exists(os.path.join(root, 'yjks.exe')):
            log('!! 没找到 yjks.exe，用 --root 指定')
            return 3
        if not run_yjk(ctx, root, os.path.join(root, 'YJKAPI.dll')):
            return 2
        piles, d = ctx.state()
        brd = {k: v for k, v in d.items() if piles[k]['cap'] == 0}
        over = [k for k, v in d.items() if v < -f2[piles[k]['kind']] - 3]
        idle = sum(1 for v in brd.values() if abs(v) < 200)
        log('=== 实算：桩 %d（板下 %d）超限 %d（%.1f%%），D500 max %.1f，平均 %.0f，闲桩 %d'
            % (len(d), len(brd), len(over), 100.0 * len(over) / len(d),
               min(brd.values()), sum(brd.values()) / len(brd), idle))
    return 0


if __name__ == '__main__':
    sys.exit(main())
