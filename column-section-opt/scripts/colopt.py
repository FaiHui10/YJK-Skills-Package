# -*- coding: utf-8 -*-
"""柱截面 + 混凝土等级优选：统一入口。

    python colopt.py build   --config c.json --sections s.json --out model.ydb
    python colopt.py drive   --config c.json --ydb model.ydb --proj <工程目录> [--name Model]
    python colopt.py opt     --config c.json --res <工程目录> --out s_next.json [--only C30]
                             [--db 模型.ydb]     # 真实工程按柱坐标分组（框-筒必给）
    python colopt.py cost    --config c.json --res <工程目录> [--json cost.json] [--db 模型.ydb]
    python colopt.py iterate --config c.json --sections s.json --tag 01 --proj <工程目录>
    python colopt.py report  --config c.json --out 汇报.xlsx iter_*.json

典型流程（2~3 轮即收敛）：
    1) 用一份保守起点跑 iterate 得到基线（拿真实轴力）
    2) opt 解析选型 → build → drive → cost
    3) 用新结果再跑一次 opt，若"建议改动为空"即收敛

驱动部分（drive）委托给 `yjk-auto-drive` 技能 —— 本技能只做选型、写回、复核、报告。
"""
import argparse
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def _run(script, argv, py=None):
    cmd = [py or sys.executable, "-X", "utf8", "-u", "-B", os.path.join(HERE, script)] + argv
    return subprocess.run(cmd).returncode


def _run_build(script, argv):
    """frame_build.py 需要 **pythonnet**（官方建模接口是 .NET 程序集）。

    ★ 不能用 sys.executable：本脚本可能被一个没装 pythonnet 的解释器启动，
      那样 `from ... ` 加载 YJKAPI.dll 会以 ModuleNotFoundError 收场，
      症状看着像「dll 找不到」，其实是解释器不对。
      这里统一改问 driver.python_exe()（跨机器自动找带 clr 的那个）。
    """
    import driver
    py = driver.python_exe()
    if os.path.normcase(py) != os.path.normcase(sys.executable):
        print("（建模用解释器：%s）" % py)
    return _run(script, argv, py=py)


def cmd_build(a):
    # ★ `--scaffold` 透传给 frame_build.py：**显式**改用「骨架库 + 序列化」写盘，
    #   这条路径完全不调用 CreateYDB（不依赖 .NET 写盘程序集，产物逐字节可复现）。
    #   默认仍走 CreateYDB；它到底行不行，先跑 `driver.py createydb` 探测
    #   （弹窗/access violation 这类失败 Python 拦不住，所以不做"失败再回退"）。
    argv = ["--config", a.config, "--sections", a.sections, "--out", a.out]
    scaf = getattr(a, "scaffold", None)      # iterate 里构造的 Namespace 没有这个字段
    if scaf:
        argv += ["--scaffold", scaf]
    return _run_build("frame_build.py", argv)


def cmd_drive(a):
    """驱动 YJK：**委托给 yjk-auto-drive 技能**（本技能不含 IPC / 启动逻辑）。

    怎么找到那个技能：与本技能**同级**（装机默认形态）、或设环境变量
    `YJK_DRIVER_DIR` / `YJK_AUTO_DRIVE_DIR` / `YJK_SKILLS_DIR`、或整套技能落在
    任意 agent 的用户级技能目录下（`driver.py` 会**通用扫描**，不认某个具体厂商名）。
    ★ 桌面不再是一个候选位置 —— 技能不该假定自己放在桌面，那条候选早已删除。
    """
    import driver                                              # 同目录
    rc, _ = driver.host(os.path.abspath(a.proj), a.name or "Model",
                        ydb=os.path.abspath(a.ydb), prep=True, calc=True)
    return rc


def cmd_opt(a):
    argv = ["--config", a.config, "--res", a.res, "--out", a.out]
    if a.only:
        argv += ["--only", a.only]
    if a.compare:
        argv += ["--compare", a.compare]
    if getattr(a, "db", None):
        # 真实工程（框-筒/抽柱）必须给：否则柱号分组会算错且不报错
        argv += ["--db", a.db]
    return _run("section_opt.py", argv)


def cmd_cost(a):
    argv = ["--config", a.config, "--res", a.res]
    if a.json:
        argv += ["--json", a.json]
    if getattr(a, "db", None):
        argv += ["--db", a.db]
    return _run("cost.py", argv)


def _count_exceed(res_dir, max_floor):
    """统计 wpj*.out 里含'超限'的行。"""
    total, items = 0, []
    for f in range(1, max_floor + 1):
        p = os.path.join(res_dir, "wpj%d.out" % f)
        if not os.path.exists(p):
            continue
        for line in open(p, "rb").read().decode("gbk", "ignore").splitlines():
            if "超限" in line:
                total += 1
                items.append([f, line.strip()[:100]])
    return total, items


def cmd_iterate(a):
    from common import load_config  # noqa
    cfg = load_config(a.config)
    sections = json.load(open(a.sections, encoding="utf-8"))
    if "sections" in sections:
        sections = sections["sections"]
    work = a.work or os.path.dirname(os.path.abspath(a.config))
    proj = a.proj or os.path.join(work, "工程_%s" % a.tag)
    ydb = a.ydb or os.path.join(work, "model_%s.ydb" % a.tag)

    print("=== 迭代 %s ===" % a.tag)
    print("1) 生成模型 -> %s" % ydb)
    if cmd_build(argparse.Namespace(config=a.config, sections=a.sections, out=ydb)) != 0:
        return 1
    print("2) 驱动 YJK -> %s" % proj)
    if cmd_drive(argparse.Namespace(ydb=ydb, proj=proj, config=a.config,
                                    name=a.name or "Model")) != 0:
        return 1

    print("3) 查超限")
    res = os.path.join(proj, "设计结果")
    n_exc, items = _count_exceed(res, cfg["几何"]["层数"])
    print("   超限条数：%d" % n_exc)
    for f, t in items[:6]:
        print("     第%d层 %s" % (f, t))

    print("4) 算造价")
    import cost as cost_mod
    rows, total = cost_mod.compute(cfg, proj)
    out = {"tag": a.tag, "sections": sections, "超限条数": n_exc, "超限明细": items,
           "造价": total, "明细": rows, "工程目录": proj}
    jp = os.path.join(work, "iter_%s.json" % a.tag)
    json.dump(out, open(jp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("   合计 %.0f 元（混凝土 %.0f / 模板 %.0f / 纵筋 %.0f / 箍筋 %.0f）"
          % (total["合计"], total["混凝土"], total["模板"], total["纵筋"], total["箍筋"]))
    print("结果 -> %s" % jp)
    return 0


def cmd_report(a):
    argv = ["--config", a.config, "--out", a.out] + a.iters
    return _run("report.py", argv)


def _utf8_console():
    """让输出在任何控制台编码下都不崩（GBK 下把不可编码字符替换掉）。

    为什么需要：本包会打印 ✅ ❌ ⚠ −(U+2212) ² ³ 等**非 cp936** 字符，
    默认 GBK 控制台下 `print` 会抛 UnicodeEncodeError 并**以退出码 1 中断**，
    于是一个其实已经成功的任务（比如文件已经落盘）会被上层判成失败；
    对 frame_build.py 那条链更糟 —— 崩在被调用的库的 print 上，模型根本没写出来。

    `errors="replace"` 让它在 UTF-8 控制台下原样输出、在 GBK 下退化成 `?`，都不崩。
    ★ 只在实际执行时调用（CLI 入口），**不在 import 时改 stdout** ——
      这些模块会被别的脚本 import 当库用，污染 import 方的 stdout 是不对的。
    """
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass


def main():
    _utf8_console()          # ★ 必须在 argparse 之前：--help 也是写到 stdout 的
    ap = argparse.ArgumentParser(description="柱截面 + 混凝土等级优选")
    sub = ap.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("build", help="按截面配置生成框架 / 框架-核心筒 ydb")
    b.add_argument("--config", required=True)
    b.add_argument("--sections", required=True)
    b.add_argument("--out", required=True)
    b.add_argument("--scaffold", default=None,
                   help="显式改用序列化写盘：给一个 YJK 新建空工程 save 出来的 .ymd，"
                        "模型直接写进这个骨架库、不调用 CreateYDB（默认仍走 CreateYDB，"
                        "可先用 `driver.py createydb` 探测）")
    b.set_defaults(fn=cmd_build)

    d = sub.add_parser("drive", help="驱动 YJK：新建工程→导入→前处理→计算")
    d.add_argument("--config")
    d.add_argument("--ydb", required=True)
    d.add_argument("--proj", required=True)
    d.add_argument("--name", default="Model")
    d.set_defaults(fn=cmd_drive)

    o = sub.add_parser("opt", help="按实算轴力解析选型（输出 sections.json）")
    o.add_argument("--config", required=True)
    o.add_argument("--res", required=True, help="工程目录或 设计结果 目录")
    o.add_argument("--out", required=True)
    o.add_argument("--only", help="强制全楼单一等级，如 C30")
    o.add_argument("--compare", help="与给定 sections.json 对比，判断是否收敛")
    o.add_argument("--db", help="模型库(.ydb/.ymd)：按柱坐标分组（真实工程/框-筒必给）")
    o.set_defaults(fn=cmd_opt)

    c = sub.add_parser("cost", help="按配筋数据算造价")
    c.add_argument("--config", required=True)
    c.add_argument("--res", required=True)
    c.add_argument("--json")
    c.add_argument("--db", help="模型库(.ydb/.ymd)：按柱坐标分组（真实工程/框-筒必给）")
    c.set_defaults(fn=cmd_cost)

    it = sub.add_parser("iterate", help="跑一轮：build + drive + 查超限 + 算造价")
    it.add_argument("--config", required=True)
    it.add_argument("--sections", required=True)
    it.add_argument("--tag", required=True)
    it.add_argument("--proj", help="工程目录（默认 <工作目录>/工程_<tag>）")
    it.add_argument("--ydb", help="ydb 路径（默认 <工作目录>/model_<tag>.ydb）")
    it.add_argument("--work", help="工作目录（默认配置文件所在目录）")
    it.add_argument("--name", help="YJK 工程名（默认 Model）")
    it.set_defaults(fn=cmd_iterate)

    rp = sub.add_parser("report", help="生成 Excel 汇报")
    rp.add_argument("--config", required=True)
    rp.add_argument("--out", required=True)
    rp.add_argument("iters", nargs="+")
    rp.set_defaults(fn=cmd_report)

    a = ap.parse_args()
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
