# -*- coding: utf-8 -*-
r"""改基础模型前的前置清理：把 YJK 会用来恢复旧模型的文件移出工程目录。

移出对象（都在工程根下）：
  基础备份\                      YJK 自动/人工备份，恢复源
  <工程名>_F.yjc / .tmp / .yg / .ygt / .ygjcbak   基础模块自己的模型与图形数据
  Jccad_0_ydb.dat                ydb 的保存前自动备份
  <工程名>_F*.yjc.*              任何残留的归档副本

用法：
  python prep_model.py --dir <工程目录> [--dry-run]

移出位置默认 <工程目录上级>\\_备份移出\\<工程名>-<YYYYMMDD-HHMM>，绝不留在工程目录内。
"""
import argparse, os, shutil, time, glob

ap = argparse.ArgumentParser()
ap.add_argument("--dir", required=True)
ap.add_argument("--dry-run", action="store_true")
ap.add_argument("--archive", default=None)
args = ap.parse_args()

P = os.path.abspath(args.dir)
name = os.path.basename(P)
ts = time.strftime("%Y%m%d-%H%M")
arc = args.archive or os.path.join(os.path.dirname(P), "_备份移出", "%s-%s" % (name, ts))

targets = []
d = os.path.join(P, "基础备份")
if os.path.isdir(d):
    targets.append(d)
for pat in ("*_F.yjc", "*_F.tmp", "*_F.yg", "*_F.ygt", "*_F.ygjcbak", "Jccad_0_ydb.dat",
            "*_F.yjc.*", "*_F.tmp.*"):
    targets += [f for f in glob.glob(os.path.join(P, pat)) if os.path.isfile(f)]

if not targets:
    print("无需清理：工程目录里没有恢复源文件")
else:
    print("移出 %d 项 -> %s" % (len(targets), arc))
    for t in targets:
        print("  %s" % os.path.basename(t))
    if not args.dry_run:
        os.makedirs(arc, exist_ok=True)
        for t in targets:
            dst = os.path.join(arc, os.path.basename(t))
            if os.path.exists(dst):
                dst = os.path.join(arc, os.path.basename(t) + "." + ts)
            shutil.move(t, dst)
        print("完成。若要回退，把文件移回工程目录即可。")

ydb = os.path.join(P, "Jccad_0.ydb")
if os.path.exists(ydb):
    print("提醒：改桩前先确认没有 yjks.exe 在跑（写入会被内存副本覆盖）")
