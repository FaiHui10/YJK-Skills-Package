# -*- coding: utf-8 -*-
"""把 layout.csv 写入已有试验工程的 Jccad_0.ydb（复用同一个拷贝目录，省去重复复制 1.2GB）。"""
import os, sqlite3, shutil, sys
import numpy as np

case = sys.argv[1]
lay = sys.argv[2]
backup = sys.argv[3] if len(sys.argv) > 3 else None

P = np.loadtxt(lay, delimiter=",", skiprows=1)
con = sqlite3.connect(os.path.join(case, "Jccad_0.ydb"))
cur = con.cursor()
colsn = [r[1] for r in cur.execute('PRAGMA table_info("app_Pile")')]
tmpl = dict(zip(colsn, cur.execute("select * from app_Pile where DaisFlag=-1 limit 1").fetchone()))
cur.execute("delete from app_Pile where DaisFlag=-1")
base = cur.execute("select max(ID) from app_Pile").fetchone()[0] or 0
for i, (x, y, z) in enumerate(P, 1):
    d = dict(tmpl)
    d["ID"] = base + i; d["x"] = float(x); d["y"] = float(y); d["z"] = float(z); d["DaisFlag"] = -1
    cur.execute("insert into app_Pile (%s) values (%s)"
                % (",".join('"%s"' % c for c in colsn), ",".join("?" for _ in colsn)),
                [d[c] for c in colsn])
con.commit()
print("写入 %d 根板下桩，总桩数 %d" % (len(P), cur.execute("select count(*) from app_Pile").fetchone()[0]))
con.close()

res = os.path.join(case, "基础计算及结果输出")
if backup and os.path.exists(os.path.join(res, "YJK-F桩承载力验算.out")):
    shutil.copy2(os.path.join(res, "YJK-F桩承载力验算.out"), backup)
for f in os.listdir(res):
    p = os.path.join(res, f)
    # 只删 .out 不够：jccad.result/jccad.ydb/Jccad_1.ydb/jccad.pre/element.data/中间数据
    # 都会让 YJK 复用上一版模型的网格与结果（实测会导致改桩后反力仍是旧值）
    if f in ("jccad.result", "jccad.ydb", "Jccad_1.ydb", "jccad.pre", "element.data") or f.endswith(".out"):
        os.remove(p)
    elif f == "中间数据" and os.path.isdir(p):
        shutil.rmtree(p)
print("已清理旧结果")
