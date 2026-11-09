# -*- coding: utf-8 -*-
"""JCCAD 结果一致性闸门 —— 判定「这批结果是不是这版模型算的」。

不启动 YJK，秒级。用法：

    python af_gate.py --dir <工程目录>
    python af_gate.py --dir <工程目录> --combos 52 --caps 208 --dead-load 1164014

判定 5 项（任一 FAIL 退出码 2）：
  1 模型/结果 板下桩位坐标集合一致
  2 承台数一致且等于 --caps
  3 组合数一致且等于 --combos
  4 模型 Loads 的 Sum(data0) = --dead-load（上部恒载，丢了就会明显偏小）
  5 结果 Dead 工况总支反力 ≈ 基础自重 + 上部恒载（只剩自重 = 荷载没进去）

退出码：0 通过 / 2 不通过 / 3 输入缺失。
"""
from __future__ import annotations
import argparse
import os
import sqlite3
import sys
import time


def _ro(path):
    return sqlite3.connect('file:%s?mode=ro' % path.replace('\\', '/'), uri=True)


def loadcase_reactions(path):
    """CAL_MID.LoadCases.txt -> {序号: (总荷载Z, 总支反力Z)}（GBK 文本）。"""
    try:
        with open(path, 'r', encoding='gbk', errors='replace') as fh:
            lines = fh.read().splitlines()
    except OSError:
        return {}
    start = next((i for i, ln in enumerate(lines) if '工况荷载校验' in ln), None)
    if start is None:
        return {}

    def isint(s):
        try:
            int(s); return True
        except Exception:
            return False

    def isnum(s):
        try:
            float(s); return True
        except Exception:
            return False

    out, i = {}, start
    while i < len(lines) - 2:
        a = lines[i].split()
        if len(a) == 2 and all(isint(x) for x in a):
            b, c = lines[i + 1].split(), lines[i + 2].split()
            if len(b) == 6 and len(c) == 6 and all(isnum(x) for x in b + c):
                out[int(a[0])] = (float(b[2]), float(c[2]))
                i += 3
                continue
        i += 1
    return out


def main():
    ap = argparse.ArgumentParser(description='JCCAD 模型/结果 一致性闸门')
    ap.add_argument('--dir', required=True, help='工程目录（含 Jccad_0.ydb）')
    ap.add_argument('--ydb', default='Jccad_0.ydb')
    ap.add_argument('--result', default=os.path.join('基础计算及结果输出', 'jccad.ydb'))
    ap.add_argument('--cases', default=os.path.join('基础计算及结果输出', '中间数据', '中间数据',
                                                    'YjkCAL_MID', 'CAL_MID.LoadCases.txt'))
    ap.add_argument('--caps', type=int, default=208, help='承台数（结果与模型都应等于它）')
    ap.add_argument('--combos', type=int, default=52, help='组合数')
    ap.add_argument('--dead-load', type=float, default=1164014.0, help='上部恒载 Sum(data0)（kN）')
    ap.add_argument('--tolerance', type=float, default=0.15, help='Dead 反力允许相对偏差')
    args = ap.parse_args()

    proj = os.path.abspath(args.dir)
    ydb = os.path.join(proj, args.ydb)
    res = os.path.join(proj, args.result)
    cases = os.path.join(proj, args.cases)
    for p in (ydb, res):
        if not os.path.exists(p):
            print('!! 缺文件: %s' % p)
            return 3

    c = _ro(ydb)
    m_board = {(round(x, 1), round(y, 1)) for x, y in
               c.execute('select x,y from app_Pile where DaisFlag<0')}
    m_caps = c.execute('select count(*) from app_dais').fetchone()[0]
    m_combos = c.execute('select count(*) from LoadZhuHe').fetchone()[0]
    m_load = c.execute('select round(sum(data0)) from Loads').fetchone()[0] or 0
    c.close()

    r = _ro(res)
    r_board = {(round(x, 1), round(y, 1)) for x, y in
               r.execute('select xx,yy from tblPileApp where nRaft_CT=0')}
    r_caps = r.execute('select count(*) from tblDaisApp').fetchone()[0]
    r_combos = r.execute('select count(distinct CombType||"-"||CombID) from tblPileNL').fetchone()[0]
    r.close()

    dead = loadcase_reactions(cases).get(1, (None, None))[1]
    # Dead 反力 = 基础自重 + 上部恒载；自重取 Sum(data0) 的 0~40% 作为合理区间
    lo = args.dead_load * (1 - args.tolerance)
    hi = args.dead_load * (1 + 0.45)
    checks = [
        ('模型/结果 板下桩位', '%d / %d' % (len(m_board), len(r_board)),
         'PASS' if m_board == r_board else 'FAIL'),
        ('承台数 模型/结果', '%d / %d' % (m_caps, r_caps),
         'PASS' if m_caps == r_caps == args.caps else 'FAIL'),
        ('组合数 模型/结果', '%d / %d' % (m_combos, r_combos),
         'PASS' if m_combos == r_combos == args.combos else 'FAIL'),
        ('模型 Sum(data0) (kN)', '%.0f' % m_load,
         'PASS' if abs(m_load - args.dead_load) < max(50.0, args.dead_load * 1e-4) else 'FAIL'),
        ('Dead 工况总反力 (kN)', '%.0f' % (dead or 0),
         'PASS' if dead and lo <= dead <= hi else 'FAIL'),
        ('结果 mtime', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime(res))), '-'),
    ]
    print('%-24s %-24s %s' % ('检查项', '值', '判定'))
    print('-' * 64)
    bad = 0
    for name, val, verdict in checks:
        print('%-24s %-24s %s' % (name, val, verdict))
        if verdict == 'FAIL':
            bad += 1
    print('-' * 64)
    print('结论：%s' % ('PASS，模型与结果一致' if bad == 0 else 'FAIL，%d 项不通过，结果不可用' % bad))
    return 0 if bad == 0 else 2


if __name__ == '__main__':
    sys.exit(main())
