# -*- coding: utf-8 -*-
"""布桩优化一键固化流程：kill → 移出恢复源 → 写入布局 → YJK 重算 → 核验。

用法：
  python run_layout.py --dir <工程目录> --layout layout.csv --root E:\\YJKS\\YJKS_8_1_0

必须用 YJK 驱动用的解释器：%USERPROFILE%\\.yjk-auto\\venv\\Scripts\\python.exe
任一步失败即停止，不会带着半成品继续往下跑。
"""
import argparse, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
YJK = os.environ.get("YJK_SKILL_DIR", r"c:\Users\Administrator\.trae-cn\skills\yjk-auto-drive\scripts")

ap = argparse.ArgumentParser()
ap.add_argument("--dir", required=True)
ap.add_argument("--layout", required=True, help="layout.csv（表头 x,y,z，单位 mm）")
ap.add_argument("--root", required=True, help="YJK 8.x 安装目录，如 E:\\YJKS\\YJKS_8_1_0")
ap.add_argument("--ra", type=float, default=None)
ap.add_argument("--min", dest="d_min", type=float, default=2500.0)
ap.add_argument("--skip-calc", action="store_true")
args = ap.parse_args()

PY = sys.executable


def stage(title, cmd):
    print("\n==== %s ====" % title)
    print("  " + " ".join(os.path.basename(c) if os.path.isabs(c) else c for c in cmd))
    r = subprocess.run([PY, "-X", "utf8"] + cmd, capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
    out = (r.stdout or "") + (r.stderr or "")
    print("\n".join("  " + l for l in out.strip().splitlines()[-8:]))
    if r.returncode != 0:
        sys.exit("失败：%s（退出码 %d）" % (title, r.returncode))


# 1 关掉 YJK，否则写入会被内存副本覆盖
stage("kill YJK", [os.path.join(YJK, "yjk_auto.py"), "kill"])
# 2 把基础模块的备份/图形文件移出工程，否则保存时会把旧桩写回来
stage("移出恢复源", [os.path.join(HERE, "prep_model.py"), "--dir", args.dir])
# 3 写入新桩位并清理旧结果
stage("写入布局", [os.path.join(HERE, "apply_layout.py"), args.dir, args.layout])
# 4 实算
if not args.skip_calc:
    stage("YJK 重算", [os.path.join(YJK, "jc.py"), "--dir", args.dir, "--root", args.root, "--output"])
# 5 核验
cmd = [os.path.join(HERE, "check_layout.py"), "--dir", args.dir, "--layout", args.layout, "--min", str(args.d_min)]
if args.ra:
    cmd += ["--ra", str(args.ra)]
stage("核验", cmd)
