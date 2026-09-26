# -*- coding: utf-8 -*-
"""裙楼楼盖「次梁布置方式」比选 —— 参数化方案定义。

柱网 8.4m x 8.4m，长向 8 跨（X），短向 4 跨（Y）。
楼面均布荷载 10 kN/m2（附加恒载 + 活载）。

五种次梁布置（bay = 一个 8.4x8.4 柱网区格）：
    S0 无次梁        —— 8.4x8.4 双向板
    S1 单向 1 道次梁 —— 每格 1 道，顺 X 向，位于 Y 向跨中  -> 2 块 8.4x4.2
    S2 单向 2 道次梁 —— 每格 2 道，顺 X 向，位于 Y 向 1/3、2/3 -> 3 块 8.4x2.8
    S3 十字梁        —— X、Y 各 1 道，跨中十字      -> 4 块 4.2x4.2
    S4 井字梁        —— X、Y 各 2 道（1/3、2/3）    -> 9 块 2.8x2.8
"""
import argparse
import json
import os
import sys

# ------------------------------------------------------------------ 全局假定
BASE = dict(
    几何=dict(跨度X=8400, 跨数X=8, 跨度Y=8400, 跨数Y=4, 层数=3, 层高=4800),
    荷载=dict(附加恒载=5.0, 活载=5.0),          # 合计 10 kN/m2
    柱=dict(边长=700, 等级="C40"),
    板=dict(等级="C30"),
    # ★ 主梁上还有**梁间线荷载**（隔墙/幕墙等），它不进楼面均布荷载，YJK 是分开
    #   存在 tblLoadSect/tblLoadSeg 里的（make_ydb.py 会把它们序列化出去）。
    #   默认 0 = 不布梁间荷载 —— 老配置不改也能照常加载、结果与本条加入前一致。
    主梁=dict(宽=300, 高=800, 等级="C30", 均布荷载kN每m=0.0),
    材料=dict(主筋级别=3, 箍筋级别=3),            # 3=HRB400
)

# 方案：次梁_X 向每跨道数（沿 X 走、支承于 Y 向主梁）、次梁_Y 向每跨道数
LAYOUTS = {
    "S0_无次梁": dict(
        名称="无次梁（双向板）", 次梁_X向每跨道数=0, 次梁_Y向每跨道数=0,
        板厚=180, 次梁=None),
    "S1_单向1道次梁": dict(
        名称="单向 1 道次梁", 次梁_X向每跨道数=1, 次梁_Y向每跨道数=0,
        板厚=120, 次梁=dict(宽=250, 高=550, 等级="C30")),
    "S2_单向2道次梁": dict(
        名称="单向 2 道次梁", 次梁_X向每跨道数=2, 次梁_Y向每跨道数=0,
        板厚=100, 次梁=dict(宽=250, 高=500, 等级="C30")),
    "S3_十字梁": dict(
        名称="十字梁", 次梁_X向每跨道数=1, 次梁_Y向每跨道数=1,
        板厚=100, 次梁=dict(宽=250, 高=500, 等级="C30")),
    "S4_井字梁": dict(
        名称="井字梁", 次梁_X向每跨道数=2, 次梁_Y向每跨道数=2,
        板厚=100, 次梁=dict(宽=250, 高=450, 等级="C30")),
}
ORDER = ["S0_无次梁", "S1_单向1道次梁", "S2_单向2道次梁", "S3_十字梁", "S4_井字梁"]


def load(path=None):
    """取基准配置（可被外部 json 覆盖）。

    `path` 给了就必须读到：文件不存在时**当场失败**，不回落成一个字都不说的内置默认配置。
    老版本是 `if path and os.path.exists(path)` —— 路径拼错 / 换了目录 / 文件还没生成时，
    它静默返回默认配置，于是调用方（build_floor.py / make_ydb.py）照常建模、照常打印模型构成、
    退出码 0，唯独用户想要的荷载/截面/层数**一样都没生效**；错的东西看起来完全正常。
    （对照：json 内容损坏会抛 JSONDecodeError，是响亮的 —— 只有"文件不存在"这一支是静默的。）
    没传 `path` 时才用内置默认值。

    读法用 utf-8-sig：这份 json 是给人改的（记事本存过就会带 BOM）。
    """
    cfg = json.loads(json.dumps(BASE))          # deep copy
    if not path:
        return cfg
    if not os.path.exists(path):
        raise SystemExit(
            "配置文件不存在：%s\n"
            "  --config 给了路径就必须能读到；本脚本**不会**回退到内置默认配置\n"
            "  （回退的后果是：荷载/截面/层数不是你要的那套，而整条链照样报成功）。\n"
            "  想用内置默认值就别传 --config。当前目录：%s"
            % (os.path.abspath(path), os.getcwd()))
    if os.path.isdir(path):
        raise SystemExit("--config 给的是目录，不是 json 文件：%s" % os.path.abspath(path))
    if os.path.getsize(path) == 0:
        raise SystemExit("--config 指定的文件是 0 字节（内容为空）：%s\n"
                         "  怎么办：补上内容，或别传 --config 用内置默认值。"
                         % os.path.abspath(path))
    try:
        with open(path, encoding="utf-8-sig") as fh:
            ext = json.load(fh)
    except UnicodeDecodeError as e:
        raise SystemExit("--config 不是 UTF-8 文本（%s）：%s" % (e, os.path.abspath(path)))
    except json.JSONDecodeError as e:
        raise SystemExit("--config 不是合法的 json（第 %d 行第 %d 列：%s）：%s\n"
                         "  怎么办：改回合法 json；损坏的配置不会回退成默认值。"
                         % (e.lineno, e.colno, e.msg, os.path.abspath(path)))
    except OSError as e:
        raise SystemExit("--config 读不出来（%s）：%s" % (e, os.path.abspath(path)))
    if not isinstance(ext, dict):
        raise SystemExit("配置文件顶层必须是 json 对象：%s" % os.path.abspath(path))
    for k, v in ext.items():
        if isinstance(v, dict):
            cfg.setdefault(k, {}).update(v)
        else:
            cfg[k] = v
    return cfg


def grids(cfg, lay):
    """返回 (x 向梁线 y 坐标集, y 向梁线 x 坐标集, 主梁 x 线, 主梁 y 线)。

    ★ 命名约定（务必按此理解，否则整张布置会错）：
      - 「X 向梁」= 沿 X 方向走的梁，它位于某个 y 上  -> 由 YLEVELS 指定
      - 「Y 向梁」= 沿 Y 方向走的梁，它位于某个 x 上  -> 由 XLEVELS 指定
    """
    g = cfg["几何"]
    sx, sy = g["跨度X"], g["跨度Y"]
    nx, ny = g["跨数X"], g["跨数Y"]

    zhux = [i * sx for i in range(nx + 1)]        # 主梁在 X 上的位置（Y 向梁）
    zhuy = [j * sy for j in range(ny + 1)]        # 主梁在 Y 上的位置（X 向梁）

    xlv = list(zhux)
    ylv = list(zhuy)
    kx = lay["次梁_Y向每跨道数"]                   # 增加 x 上的梁线 -> Y 向次梁
    ky = lay["次梁_X向每跨道数"]                   # 增加 y 上的梁线 -> X 向次梁
    for j in range(ny):
        for k in range(1, ky + 1):
            ylv.append(zhuy[j] + k * sy // (ky + 1))
    for i in range(nx):
        for k in range(1, kx + 1):
            xlv.append(zhux[i] + k * sx // (kx + 1))
    return sorted(set(xlv)), sorted(set(ylv)), zhux, zhuy


def summary(cfg, key):
    lay = LAYOUTS[key]
    xlv, ylv, zhux, zhuy = grids(cfg, lay)
    ncell = (len(xlv) - 1) * (len(ylv) - 1)
    # 梁段数：X 向 = 每条 y 线上 (len(xlv)-1) 段；Y 向 = 每条 x 线上 (len(ylv)-1) 段
    nbx = len(ylv) * (len(xlv) - 1)
    nby = len(xlv) * (len(ylv) - 1)
    return dict(
        方案=key, 名称=lay["名称"], 板厚=lay["板厚"],
        x线=len(xlv), y线=len(ylv), 节点=len(xlv) * len(ylv),
        梁段=dict(X向=nbx, Y向=nby, 合计=nbx + nby),
        板块=ncell,
        次梁=lay["次梁"],
        平均板块尺寸="%.1f x %.1f m" % (
            (cfg["几何"]["跨度X"] * cfg["几何"]["跨数X"]) / (len(xlv) - 1) / 1000.0,
            (cfg["几何"]["跨度Y"] * cfg["几何"]["跨数Y"]) / (len(ylv) - 1) / 1000.0),
    )


def _utf8_console():
    """让输出在任何控制台编码下都不崩（GBK 下把不可编码字符替换掉）。

    为什么需要：`--config` 会把用户给的路径打出来，而路径里可能有 cp936 编不出的字符；
    GBK 控制台下 `print` 抛 UnicodeEncodeError 会**以退出码 1 中断**一个其实成功的任务。
    ★ 只在 CLI 入口调用，**不在 import 时改 stdout**（本模块会被 build_floor/make_ydb 当库 import）。
    """
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass


def main(argv=None):
    _utf8_console()          # ★ 必须在 argparse 之前：--help 也是写到 stdout 的
    ap = argparse.ArgumentParser(
        description="打印柱网/荷载与五个次梁布置方案的几何摘要。")
    ap.add_argument("--config", default=None,
                    help="外部 json 配置（与 build_floor.py / make_ydb.py 的 --config 同一份）；"
                         "给了就必须能读到，否则报错退出（不回退默认值）")
    a = ap.parse_args(argv)

    cfg = load(a.config)
    if a.config:
        print("配置：%s" % os.path.abspath(a.config))
    print("柱网 %d x %d mm，%d 跨 x %d 跨，层数 %d，层高 %d"
          % (cfg["几何"]["跨度X"], cfg["几何"]["跨度Y"],
             cfg["几何"]["跨数X"], cfg["几何"]["跨数Y"],
             cfg["几何"]["层数"], cfg["几何"]["层高"]))
    print("楼面荷载：附加恒载 %.1f + 活载 %.1f = %.1f kN/m2"
          % (cfg["荷载"]["附加恒载"], cfg["荷载"]["活载"],
             cfg["荷载"]["附加恒载"] + cfg["荷载"]["活载"]))
    print()
    for k in ORDER:
        s = summary(cfg, k)
        print("%-16s %-14s 板厚%3d  线%dx%d  节点%4d  梁段%4d(X%d/Y%d)  板块%4d  均格 %s"
              % (s["方案"], s["名称"], s["板厚"], s["x线"], s["y线"], s["节点"],
                 s["梁段"]["合计"], s["梁段"]["X向"], s["梁段"]["Y向"],
                 s["板块"], s["平均板块尺寸"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
