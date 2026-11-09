# -*- coding: utf-8 -*-
"""抗浮板下桩迭代：抽低效桩 → 补峰值 → 每轮过闸门。

一轮 = 【抽稀】删掉 |N| 低于阈值且周边有余量的板下桩 → 重算 → 【补桩】在超限点附近
找 ≥间距 的空位补桩 → 重算。可重复多轮，直到超限归零或不再改善。

用法：
    python af_iterate.py --dir <工程目录> --f2 "1:400,0:2200" --prune-below 250 --rounds 2

前置（缺一不可）：
  * `<工程>/Jccad_0.ydb` 带**完整组合**与**完整上部荷载**（Loads 行序必须节点优先）
  * 没有其它 yjks 实例在跑（本脚本不会去杀别人的实例）
  * 已装 yjk-auto-drive（用其 IPC 客户端；可用 YJK_DRIVER_DIR / YJK_SKILLS_DIR 指定）
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
    for k in ('YJK_DRIVER_DIR',):
        if os.environ.get(k):
            cands.append(os.environ[k])
    base = os.environ.get('YJK_SKILLS_DIR')
    if base:
        cands.append(os.path.join(base, 'yjk-auto-drive', 'scripts'))
    cands += [
        os.path.join(HERE, '..', '..', 'yjk-auto-drive', 'scripts'),
        os.path.join(HERE, '..', 'yjk-auto-drive', 'scripts'),
        os.path.join(os.getcwd(), 'yjk-auto-drive', 'scripts'),
    ]
    for c in cands:
        p = os.path.abspath(c)
        if os.path.isfile(os.path.join(p, 'yjk_auto.py')):
            return p
    raise SystemExit('!! 找不到 yjk-auto-drive/scripts，试过：\n  ' + '\n  '.join(map(os.path.abspath, cands)))


sys.path.insert(0, find_driver())
import yjk_auto as YA                                            # noqa: E402


def log(m):
    print('[%s] %s' % (time.strftime('%H:%M:%S'), m), flush=True)


# ---------------------------------------------------------------- 模型/结果
def ro(p):
    return sqlite3.connect('file:%s?mode=ro' % p.replace('\\', '/'), uri=True)


def read_model(ydb):
    c = ro(ydb)
    cols = [d[1] for d in c.execute('pragma table_info(app_Pile)')]
    rows = [dict(zip(cols, r)) for r in c.execute('select * from app_Pile')]
    poly = [(r[0], r[1]) for r in c.execute('select ptx,pty from RaftCornerPoint order by ID')]
    c.close()
    return cols, rows, poly


def read_result(res, combo):
    c = ro(res)
    piles = {r[0]: (r[1], r[2], r[3], r[4]) for r in
             c.execute('select ID,nRaft_CT,kind,xx,yy from tblPileApp')}
    d = {}
    for pid, cid, ct, blob in c.execute(
            'select PileID,CombID,CombType,N from tblPileNL where CombType=? and CombID=?',
            (combo[0], combo[1])):
        d[pid] = struct.unpack('<9f', blob)[0]
    caps = c.execute('select count(*) from tblDaisApp').fetchone()[0]
    nzh = c.execute('select count(distinct CombType||"-"||CombID) from tblPileNL').fetchone()[0]
    c.close()
    return piles, d, caps, nzh


# ---------------------------------------------------------------- 几何
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


def free_spot(x, y, pos, poly, spacing, margin, rings=(1750, 2000, 2300, 2600, 3000, 3400, 3800)):
    for r in rings:
        if isinstance(r, (int, float)):
            rr = float(r)
        for a in range(0, 360, 10):
            th = math.radians(a)
            px, py = x + rr * math.cos(th), y + rr * math.sin(th)
            if not inside(px, py, poly, margin):
                continue
            if any((px - qx) ** 2 + (py - qy) ** 2 < spacing ** 2 for qx, qy in pos):
                continue
            return px, py
    return None


# ---------------------------------------------------------------- 一轮计算
def run_round(proj, yjk, root, dll, tag):
    """开 YJK → 导入 → 覆盖回 ydb → 生成数据 → 基础计算 → 关。"""
    ydb = os.path.join(proj, 'Jccad_0.ydb')
    snap = os.path.join(proj, '.af_iter_%s.ydb' % tag)
    shutil.copy2(ydb, snap)
    for i in [i for i in YA.instances() if i.get('kind') not in ('dead',)]:
        log('  关闭已有实例 pid=%s' % i['pid'])
        YA.kill_pid(i['pid'])
    time.sleep(5)
    before = set(YA.yjks_pids())
    for fl in YA.FLAGS_LADDER:
        try:
            subprocess.Popen([os.path.join(root, 'yjks.exe'), '-product', 'YJKS', '-open', yjk],
                             cwd=proj, creationflags=fl, stdin=subprocess.DEVNULL,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            break
        except OSError:
            continue
    t0 = time.time()
    pid = None
    while time.time() - t0 < 240:
        new = set(YA.yjks_pids()) - before
        if new:
            pid = max(new)
            break
        time.sleep(2)
    if not pid:
        return False
    YA.own_claim(pid, os.path.join(root, 'yjks.exe'), proj)
    want = os.path.normcase(os.path.abspath(yjk))
    t1 = time.time()
    while time.time() - t1 < 240:
        if any((YA.title_to_proj(t) and os.path.normcase(os.path.abspath(YA.title_to_proj(t))) == want)
               or os.path.splitext(os.path.basename(yjk))[0].lower() in (t or '').lower()
               for t in YA.titles(pid)):
            break
        time.sleep(2)
    cli = YA.Client(dll)
    ver = '.'.join((os.path.basename(root).replace('YJKS_', '').split('_') + ['0', '0', '0'])[:3])
    cli.configure(ver, invisible=False, pid=pid)
    alive = lambda: pid in YA.yjks_pids()
    try:
        log('  label -> %s' % cli.run('SetCurrentLabel', 'JCCAD_RESULT', 300, alive=alive))
        time.sleep(2)
        log('  import -> %s' % cli.run('jccad_read_by_ydb', '', 300, alive=alive))
        time.sleep(2)
        shutil.copy2(snap, ydb)                    # 导入会回写，必须补回
        log('  gen -> %s' % cli.run('BaseDraw_GenData_script', '', 1200, alive=alive))
        log('  ana -> %s' % cli.run('BaseDraw_BaseAnalysis', '', 2400, alive=alive))
        return True
    finally:
        try:
            YA.kill_pid(pid, verbose=True)
        finally:
            YA.own_clear()
            time.sleep(3)
            shutil.copy2(snap, ydb)


def gate(proj, combo, f2, caps_expect, dead_expect, tag):
    ydb = os.path.join(proj, 'Jccad_0.ydb')
    res = os.path.join(proj, '基础计算及结果输出', 'jccad.ydb')
    cases = os.path.join(proj, '基础计算及结果输出', '中间数据', '中间数据',
                         'YjkCAL_MID', 'CAL_MID.LoadCases.txt')
    c = ro(ydb)
    mb = {(round(r[0], 1), round(r[1], 1)) for r in c.execute('select x,y from app_Pile where DaisFlag<0')}
    mcaps = c.execute('select count(*) from app_dais').fetchone()[0]
    mzh = c.execute('select count(*) from LoadZhuHe').fetchone()[0]
    mload = c.execute('select round(sum(data0)) from Loads').fetchone()[0] or 0
    c.close()
    piles, d, rcap, rzh = read_result(res, combo)

    def dead():
        try:
            lines = open(cases, encoding='gbk', errors='replace').read().splitlines()
        except OSError:
            return None
        i = next((k for k, ln in enumerate(lines) if '工况荷载校验' in ln), None)
        while i is not None and i < len(lines) - 2:
            a = lines[i].split()
            if len(a) == 2 and all(x.isdigit() for x in a):
                b, cc = lines[i + 1].split(), lines[i + 2].split()
                if len(b) == 6 and len(cc) == 6:
                    try:
                        if int(a[0]) == 1:
                            return float(cc[2])
                    except ValueError:
                        pass
                    i += 3
                    continue
            i += 1
        return None

    dr = dead()
    ok = (mb == {(round(v[2], 1), round(v[3], 1)) for v in piles.values() if v[0] == 0}
          and mcaps == rcap == caps_expect and mzh == rzh == 52
          and abs(mload - dead_expect) < max(50, dead_expect * 1e-4)
          and dr and dead_expect * 0.85 <= dr <= dead_expect * 1.45)
    log('  闸门[%s]: 桩位 %d/%d · 承台 %d/%d · 组合 %d/%d · Σ载 %.0f · Dead %.0f -> %s'
        % (tag, len(mb), len(piles), mcaps, rcap, mzh, rzh, mload, dr or 0, 'PASS' if ok else 'FAIL'))
    return ok, piles, d


def main():
    ap = argparse.ArgumentParser(description='抗浮板下桩：抽稀 + 补峰值 迭代')
    ap.add_argument('--dir', required=True)
    ap.add_argument('--f2', default='1:400,0:2200', help='桩型:抗拔承载力特征值，如 "1:400,0:2200"')
    ap.add_argument('--combo', default='1-51', help='控制组合 CombType-CombID（默认 1-51）')
    ap.add_argument('--prune-below', type=float, default=250.0, help='|N| 低于此值的板下桩可抽')
    ap.add_argument('--guard-radius', type=float, default=5000.0, help='抽桩时的保护区半径（mm）')
    ap.add_argument('--guard-n', type=float, default=300.0, help='保护区内有 |N| 超过此值的桩则不抽')
    ap.add_argument('--spacing', type=float, default=1750.0)
    ap.add_argument('--edge', type=float, default=300.0, help='新桩距筏板边最小距离（mm）')
    ap.add_argument('--caps', type=int, default=208)
    ap.add_argument('--dead-load', type=float, default=1164014.0, help='上部恒载 Σdata0（kN）')
    ap.add_argument('--rounds', type=int, default=2)
    ap.add_argument('--root', default='', help='YJK 安装目录（默认自动探测）')
    args = ap.parse_args()

    proj = os.path.abspath(args.dir)
    ydb = os.path.join(proj, 'Jccad_0.ydb')
    res = os.path.join(proj, '基础计算及结果输出', 'jccad.ydb')
    if not os.path.exists(ydb):
        log('!! 缺 Jccad_0.ydb'); return 3
    yjks = [f for f in os.listdir(proj) if f.lower().endswith('.yjk')]
    if len(yjks) != 1:
        log('!! 工程目录里的 .yjk 不是恰好一个：%s' % yjks); return 3
    yjk = os.path.join(proj, yjks[0])

    import paths as P
    ins = P.find_yjk_install()
    root = os.path.abspath(args.root) if args.root else (ins.get('root') or '')
    if not root or not os.path.exists(os.path.join(root, 'yjks.exe')):
        log('!! 没找到 yjks.exe，请用 --root 指定'); return 3
    dll = os.path.join(root, 'YJKAPI.dll')

    f2 = {}
    for part in args.f2.split(','):
        k, v = part.split(':')
        f2[int(k)] = float(v)
    ct, cid = [int(x) for x in args.combo.replace('-', ' ').split()]
    combo = (ct, cid)

    ok, piles, d = gate(proj, combo, f2, args.caps, args.dead_load, '前置')
    if not ok:
        log('!! 前置闸门不通过：先按 foundation-jccad-8.1-api.md §2 把模型修好'); return 2

    for rd in range(1, args.rounds + 1):
        # ---- 抽稀
        pos_all = [(v[2], v[3]) for v in piles.values()]
        low = []
        for k, v in d.items():
            if piles[k][0] != 0 or abs(v) >= args.prune_below:
                continue
            x, y = piles[k][2], piles[k][3]
            if any((x - qx) ** 2 + (y - qy) ** 2 <= args.guard_radius ** 2 and abs(d2) > args.guard_n
                   for kk, d2 in d.items() for qx, qy in [(piles[kk][2], piles[kk][3])] if kk != k):
                continue
            low.append((x, y))
        log('第 %d 轮：可抽 %d 根（|N|<%.0f）' % (rd, len(low), args.prune_below))
        if low:
            c = sqlite3.connect(ydb)
            cur = c.cursor()
            n = 0
            for x, y in low:
                cur.execute('delete from app_Pile where DaisFlag<0 and abs(x-?)<1 and abs(y-?)<1', (x, y))
                n += cur.rowcount
            c.commit(); c.close()
            log('  删除 %d 根，重算' % n)
            if not run_round(proj, yjk, root, dll, 'R%dP' % rd):
                return 2
            ok, piles, d = gate(proj, combo, f2, args.caps, args.dead_load, 'R%dP' % rd)
            if not ok:
                return 2

        # ---- 补峰值
        over = [(piles[k][2], piles[k][3], d[k]) for k in d if d[k] < -f2[piles[k][1]] - 3]
        log('  超限 %d 根，最大 %.1f' % (len(over), min(d.values())))
        if not over:
            continue
        cols, rows, poly = read_model(ydb)
        c = sqlite3.connect(ydb)
        cur = c.cursor()
        tmpl = next(r for r in rows if r['DaisFlag'] < 0)
        pos = [(v[2], v[3]) for v in piles.values()]
        maxid = max(r['ID'] for r in rows)
        nd = 0
        for x, y, v in sorted(over, key=lambda t: t[2]):
            need = max(1, int((abs(v) - 370) // 120) + 1)
            for _ in range(need):
                spot = free_spot(x, y, pos, poly, args.spacing, args.edge)
                if not spot:
                    break
                nd += 1
                pos.append(spot)
                r = dict(tmpl)
                r.update(ID=maxid + nd, x=spot[0], y=spot[1], z=-12600, kind=1, DaisFlag=-1)
                cur.execute('insert into app_Pile (%s) values (%s)'
                            % (','.join(cols), ','.join('?' * len(cols))), [r[k] for k in cols])
        c.commit(); c.close()
        log('  补桩 %d 根，重算' % nd)
        if nd:
            if not run_round(proj, yjk, root, dll, 'R%dA' % rd):
                return 2
            ok, piles, d = gate(proj, combo, f2, args.caps, args.dead_load, 'R%dA' % rd)
            if not ok:
                return 2

    over = [k for k in d if d[k] < -f2[piles[k][1]] - 3]
    brd = [v for k, v in d.items() if piles[k][0] == 0]
    log('=== 结束：桩 %d（板下 %d），超限 %d，D500 最大 %.1f，板下平均 %.0f'
        % (len(d), len(brd), len(over), min(brd), sum(brd) / len(brd)))
    return 0 if not over else 1


if __name__ == '__main__':
    sys.exit(main())
