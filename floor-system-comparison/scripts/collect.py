# -*- coding: utf-8 -*-
r"""汇总 5 个方案的工程量 -> `quantities.json`（默认写到**当前工作目录**）。

两个来源，职责分明：
  * 几何 / 混凝土 / 模板 —— `takeoff.py`（严格按**广东省2018定额**计算规则，
    见 takeoff 模块头部的规则摘录）。YJK 不出模板，所以模板只能这样算。
  * 钢筋 —— **YJK 实算**的钢筋用量表（`results/<S>/全楼*钢筋用量*.xlsx`），
    按 HRB400 规格（Φ6~Φ32）逐档给出，直接可套定额 A1-5-105/106/107。

层高 4.8m、3 个自然层、柱网 8.4m×8.4m（长向 8 跨 × 短向 4 跨）。

用法：
    python collect.py                       # 全部 5 个方案 -> ./quantities.json
    python collect.py --out D:\out\q.json   # 指定输出文件
    python collect.py S0 S3                 # 只汇总指定方案

★ 输出位置（实测修复）：以前这里把路径写死成 `<技能>/out/quantities.json`
  （ROOT 由脚本位置算出），**跑一次就在技能包里新建 out\\ 目录并落盘**。
  现在默认落到 CWD，绝不再往技能包里写东西。
"""
import argparse
import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
import takeoff as T                                                # noqa: E402
import read_yjk_xlsx as R                                          # noqa: E402

SCHEMES = ["S0", "S1", "S2", "S3", "S4"]

INFO = {
    "S0": {"name": "无次梁（仅主梁）", "主梁": "300×800", "次梁": "—",
           "板厚": 180, "做法": "8.4m×8.4m 双向板，仅周边框架梁"},
    "S1": {"name": "单向1道次梁", "主梁": "300×800", "次梁": "250×550",
           "板厚": 120, "做法": "每柱网格 Y 向中部设 1 道次梁（8.4m 一分为二）"},
    "S2": {"name": "单向2道次梁", "主梁": "300×800", "次梁": "250×500",
           "板厚": 100, "做法": "每柱网格 Y 向设 2 道次梁（8.4m 三等分）"},
    "S3": {"name": "十字梁", "主梁": "300×800", "次梁": "250×500",
           "板厚": 100, "做法": "每柱网格中部设 X+Y 各 1 道次梁（十字）"},
    "S4": {"name": "井字梁", "主梁": "300×800", "次梁": "250×450",
           "板厚": 100, "做法": "每柱网格双向各 2 道次梁（井字，板 2.8m×2.8m）"},
}

GRADE_BEAMSLAB = "C30"
GRADE_COLUMN = "C40"


def parse_yjk_probe(path):
    """读 YJK「钢筋用量(钢筋规格与类别)」表 -> (数据, 说明)。

    `说明`（ASCII 标记）把"没拿到数据"的三种原因分开，供下游判断：
      yjk        —— 取到了
      no_file    —— 文件不存在（本轮没跑量测/路径不对）
      no_header  —— 文件在，但找不到 HRB400 表头（表结构变了）
      no_total   —— 文件在，但找不到「全楼/合计」行（只有逐层行）
    老版本把后三种一律变成 None，调用方（build_report.py）再用 `or {}` 变成 0，
    报告于是写出"钢筋 0 kg / 0 元"这种**看起来正常的假数**。
    """
    if not os.path.exists(path):
        return None, "no_file"
    try:
        ws = R.load(path).active
    except Exception as e:                                     # noqa: BLE001
        # 文件在、但读不动（半写的 xlsx / 被占用 / 不是表格）：仍然算"没取到"，
        # 但要**说出来**并计入 flags（缺数据必须与非零退出挂钩），不能抛裸 traceback。
        print("!! 读不动这个表（按「没取到」处理）：%s —— %s" % (path, e))
        return None, "unreadable"
    rows = [list(r) for r in ws.iter_rows(values_only=True)]
    hdr = None
    for i, r in enumerate(rows):
        if any(isinstance(c, str) and "HRB400" in c for c in r):
            hdr = i
            break
    if hdr is None:
        return None, "no_header"
    diam_col = {}
    for j, c in enumerate(rows[hdr + 1] if hdr + 1 < len(rows) else []):
        if isinstance(c, (int, float)) and 4 <= float(c) <= 40:
            diam_col[float(c)] = j
    tot = None
    for r in rows:
        if len(r) > 1 and isinstance(r[1], str) and r[1] in ("全楼", "合计"):
            tot = r
            break
    if tot is None:
        return None, "no_total"
    out = {}
    for d, j in diam_col.items():
        v = tot[j] if j < len(tot) else None
        if isinstance(v, (int, float)) and v:
            out[str(int(d))] = float(v)        # 键统一成 "6"/"8"/"10"…，避免 "6.0"
    if not out:
        return None, "no_rows"
    return out, "yjk"


def parse_yjk(path):
    """读 YJK 钢筋用量表 -> {直径mm: kg} 或 None（无法判断时宁可为 None，不做 0）。"""
    return parse_yjk_probe(path)[0]


def slab_area_probe(scheme):
    """从 YJK《全楼梁钢筋用量…》表读**每层**楼面面积 -> (面积或 None, 说明)。

    说明取值同 `parse_yjk_probe`。

    YJK 的板伸至周边梁外皮，故 2288.25 m2/层 > 轴网 67.2×33.6 = 2257.92 m2。
    定额说「楼板按图示面积」，用模型面积更贴合。
    ★ 表里同时有「第N层」行和「全楼/合计」行 —— 必须取**逐层**那个，
      否则会当成每层面积重复乘层数（口径差 3 倍）。
    """
    p = os.path.join(ROOT, "results", scheme, "全楼梁钢筋用量(钢筋规格与类别).xlsx")
    if not os.path.exists(p):
        return None, "no_file"
    try:
        ws = R.load(p).active
    except Exception as e:                                     # noqa: BLE001
        print("!! 读不动这张表（板面积按「未取得」处理）：%s —— %s" % (p, e))
        return None, "unreadable"
    for r in ws.iter_rows(values_only=True):
        if len(r) > 2 and isinstance(r[1], str) and r[1].startswith("第"):
            if isinstance(r[2], (int, float)) and r[2] > 1:
                return float(r[2]), "yjk"
    return None, "no_row"


def slab_area_from_yjk(scheme):
    """只取面积（读不到返回 None）。"""
    return slab_area_probe(scheme)[0]


def collect(scheme):
    m = T.load(scheme)
    ln = T.beam_lengths(m)
    sa, sa_src = slab_area_probe(scheme)
    if sa is None:
        # ★ 兜底值进的是**同一个键名** `板面积每层_YJK`，而报告把它标成"模型实测值"。
        #   所以这里额外记下来源（sources），并计入 flags：缺数据必须与"数值如此"分开。
        sa = m["slab_area"]
    c = T.concrete(m, per_floor=True, slab_area=sa)
    f = T.formwork(m, per_floor=True, slab_area=sa)
    nf = m["nfloor"]
    th = m["slab_th"].most_common(1)[0][0]

    # 梁模板按梁宽分档（A1-20-33 梁宽≤25cm / A1-20-34 梁宽＞25cm）
    fw_small = fw_big = 0.0
    beam_detail = []
    for (b, h, kind), v in sorted(ln.items(), key=lambda kv: -kv[1]["net"]):
        a = (2.0 * (h - th) + b) * v["net"]
        if round(b * 1000) <= 250:
            fw_small += a
        else:
            fw_big += a
        beam_detail.append({
            "截面": "%d×%d" % (round(b * 1000), round(h * 1000)), "类型": kind,
            "段数": v["n"], "轴线长": v["geo"] * nf, "净长": v["net"] * nf,
            "体积": b * h * v["net"] * nf, "模板": a * nf,
            "梁宽档": "25cm以内" if round(b * 1000) <= 250 else "25cm以外",
        })

    rdir = os.path.join(ROOT, "results", scheme)
    rb, rb_src = parse_yjk_probe(os.path.join(rdir, "全楼梁钢筋用量(钢筋规格与类别).xlsx"))
    rc, rc_src = parse_yjk_probe(os.path.join(rdir, "全楼柱钢筋用量(钢筋规格与类别).xlsx"))
    rs, rs_src = parse_yjk_probe(os.path.join(rdir, "全楼楼板钢筋用量.xlsx"))

    def ssum(d):
        return round(sum(d.values()), 3) if d else None

    sources = {"slab_area": sa_src, "rebar_beam": rb_src,
               "rebar_column": rc_src, "rebar_slab": rs_src}
    flags = []
    if sa_src != "yjk":
        flags.append("SLAB_AREA_FALLBACK:%s" % sa_src)
    for key, st in (("REBAR_BEAM", rb_src), ("REBAR_COLUMN", rc_src),
                    ("REBAR_SLAB", rs_src)):
        if st != "yjk":
            flags.append("%s_MISSING:%s" % (key, st))

    return {
        "scheme": scheme, "info": INFO[scheme], "层数": nf, "层高": m["std_h"],
        "板厚": round(th * 1000), "柱截面": "%d×%d" % (round(m["col_b"] * 1000),
                                                     round(m["col_h"] * 1000)),
        "柱数": m["ncol"], "节点数": len(m["jt"]), "梁段数": len(m["segs"]),
        "板块数": m["nslab"], "楼盖面积每层": round(m["slab_area"], 2),
        "楼盖面积全楼": round(m["slab_area"] * nf, 2),
        "板面积每层_YJK": round(sa, 2), "板面积全楼_YJK": round(sa * nf, 2),
        # ★ 新增（不改上面任何已有键）：数据来源与缺失标记（ASCII，便于脚本判定）
        "sources": sources, "flags": flags,
        "板面积每层来源": ("YJK 模型实测" if sa_src == "yjk" else
                       "轴网包络兜底（未取得 YJK 面积表：%s）" % sa_src),
        # —— 混凝土（每层 / 全楼）——
        "砼梁": round(c["beam_v"] * nf, 3),
        "砼板": round(c["slab_v"] * nf, 3),
        "砼有梁板": round(c["youliangban_v"] * nf, 3),
        "砼柱": round(c["col_v"] * nf, 3),
        # —— 模板（全楼）——
        "模板梁_25内": round(fw_small * nf, 2),
        "模板梁_25外": round(fw_big * nf, 2),
        "模板梁": round((fw_small + fw_big) * nf, 2),
        "模板板": round(f["slab_fw"] * nf, 2),
        "模板合计": round((fw_small + fw_big + f["slab_fw"]) * nf, 2),
        # —— 钢筋（YJK 实算，全楼 kg）——
        "钢筋梁": rb, "钢筋柱": rc, "钢筋板": rs,
        "钢筋梁合计": ssum(rb), "钢筋柱合计": ssum(rc), "钢筋板合计": ssum(rs),
        "梁明细": beam_detail,
        "混凝土级别": {"梁板": GRADE_BEAMSLAB, "柱": GRADE_COLUMN},
    }


def _safe_console():
    """stdout / stderr 编码错误策略改成 errors='replace'（与 summary_xlsx.py 同一套路）。

    本脚本原来在打印结果时直接用 m3 的上标字符（U+00B3，cp936 编不出），
    GBK 控制台下算完却因为一行打印抛 UnicodeEncodeError、退出码变 1。
    源码里已换成 ASCII（m3），这层只是兜底。
    """
    for st in (sys.stdout, sys.stderr):
        try:
            st.reconfigure(errors="replace")
        except (AttributeError, ValueError, OSError):
            pass


def main(argv=None):
    """命令行入口。

    ★ 为什么要有 `--out`（实测缺陷）：以前这里写死
      `od = os.path.join(ROOT, "out")` + `os.makedirs(od, exist_ok=True)`
      （ROOT = <技能>/floor-system-comparison），于是**只要跑一次**就在技能包里
      新建 `out\\` 目录并写进 quantities.json：
        · 技能包被运行结果污染（别人同步/打包/自检时会带上你的数据）；
        · 技能目录常常是只读的（装到 agent 的用户级技能目录、或 Program Files 下），
          失败信息会变成跟业务毫无关系的权限错误；
        · 对照本包其它脚本的口径：产物一律落在**调用者的 CWD**，技能目录只放代码。
      现在默认写 CWD，要别的位置就 `--out`。
    """
    _safe_console()
    ap = argparse.ArgumentParser(
        prog="collect.py",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="汇总 5 个方案的工程量 -> quantities.json（默认写到当前目录）。",
        epilog=__doc__)
    ap.add_argument("schemes", nargs="*", metavar="方案",
                    help="只汇总这些方案（%s）；默认全部 %d 个"
                         % (" ".join(SCHEMES), len(SCHEMES)))
    ap.add_argument("--out", default=None,
                    help="输出 json 的路径（默认：当前工作目录下的 quantities.json）")
    a = ap.parse_args(argv)

    unknown = [s for s in a.schemes if s not in SCHEMES]
    if unknown:
        ap.error("不认识的方案：%s（本技能只有：%s）"
                 % (", ".join(unknown), " ".join(SCHEMES)))
    schemes = list(a.schemes) or list(SCHEMES)

    out = {}
    problems = []
    for s in schemes:
        d = collect(s)
        out[s] = d
        print("%s %-12s 砼有梁板 %8.2f m3  模板 %8.1f m2  钢筋 梁 %s 板 %s 柱 %s"
              % (s, d["info"]["name"], d["砼有梁板"], d["模板合计"],
                 d["钢筋梁合计"], d["钢筋板合计"], d["钢筋柱合计"]))
        for f in d["flags"]:
            problems.append("%s %s" % (s, f))

    # ★ 缺 YJK 数据时报出来并给非零退出码：JSON 里那些 null / 兜底值会被
    #   build_report.py 渲染成 0（"钢筋 0 kg"、"板面积 = 轴网值"），报告看不出问题。
    #   在这里拦住，调用方就不会拿一份缺实测数据的 JSON 去出报告。
    if problems:
        print()
        print("!! 有 %d 项 YJK 实测数据没取到（JSON 里是 null 或兜底值，不是 0）：" % len(problems))
        for p in problems:
            print("   · %s" % p)
        print("   关键：%s" % os.path.join(ROOT, "results"))
        print("   处置：先跑 yjk_quant.py 出量测结果（results/<方案>/ 下应有"
              "《全楼梁/柱/板钢筋用量…xlsx》），再重跑 collect.py。")

    # ★ 默认落 CWD（不再落技能包）；目录按需创建
    p = os.path.abspath(a.out or os.path.join(os.getcwd(), "quantities.json"))
    if os.path.isdir(p):
        sys.exit("--out 给的是目录，不是文件名：%s\n"
                 "  怎么办：给一个文件名，例如 %s" % (p, os.path.join(p, "quantities.json")))
    parent = os.path.dirname(p)
    if parent and not os.path.isdir(parent):
        try:
            os.makedirs(parent, exist_ok=True)
        except OSError as e:
            sys.exit("--out 的目录建不出来（%s）：%s" % (e, parent))
    try:
        with open(p, "w", encoding="utf-8") as fh:
            json.dump(out, fh, ensure_ascii=False, indent=1)
    except OSError as e:
        sys.exit("写不出 %s（%s）\n"
                 "  常见原因：无写权限 / 文件被占用 / 磁盘满。" % (p, e))
    print("-> %s" % p)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
