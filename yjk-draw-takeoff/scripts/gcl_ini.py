# -*- coding: utf-8 -*-
r"""解析 YJK「工程量统计.ini」—— 上部结构的混凝土工程量。

来源
----
在「楼层组装」标签（`IDModule_Layer`）下执行 `yjkconcreteStat_statCom` 后生成：

    <工程目录>\计算书\工程量统计\工程量统计.ini

格式（YJKS 7.1.0）：

    [INFO]
    VERSION=7.1.0
    Gcl-Hnt-ZrcNum=3        ← 混凝土统计的自然层数
    Gcl-Steel-ZrcNum=0      ← 钢结构统计的自然层数
    RC-SLAB-FLOORNUM=3 / RC-BEAM-FLOORNUM=3 / RC-COLUMN-FLOORNUM=3 / RC-WALL-FLOORNUM=3
    [Gcl-Hnt-Zrc1]          ← 第 1 自然层
    Name=1
    Cap=构件种类,个数,材料,材料级别,体积
    Item-1=梁,76,6,30,140.448
    Item-2=柱,45,6,40,105.840
    Item-3=楼板,32,6,30,374.573
    Item-Num=3
    Item-Sum=620.861

编码：这个文件是 GBK（不是 UTF-16）；`Cap` 行给出列名，按列名取值才稳。

口径提醒
--------
* 柱体积 = 个数 × 截面面积 × 层高（45 × 0.7×0.7 × 4.8 = 105.840）
* 楼板体积 = 扣除梁占位后的净板面积 × 板厚
  （轴线 2257.92 m2 - 梁占位 ≈ 2081 m2；2081 × 0.18 = 374.6）
  这与"板伸至梁外皮"的模型板面积（2288.25 m2）不是一个口径，别混用。
* 梁体积按梁净长（扣柱）算，与本技能 takeoff.py 的手算结果一致。

数据问题与退出码
----------------
解析中每一处"读不到 / 被丢弃 / 对不上"都记进 `parse()["problems"]`，`summarize()`
把它带出去，`dump_text()` 打印它。要点：

* `_num()` 不再把非数值静默当成 0（旧版 `except ValueError: return 0.0`）——
  千分位、空值、列名错位、格式变更现在都留痕。
* `Cap` 行缺失时不再静默丢弃整层明细（旧版 `if not cap: continue`）——
  丢弃行数被记成问题，该层明细为空也记成问题。
* 一层明细被丢光时，旧版会汇总成 `{"按构件种类": {}, "合计": 0}` 并以 0 退出，
  看起来像"本工程没有混凝土"；现在是问题清单 + 退出码 2。

命令行退出码：0 = 无数据问题；2 = 有数据问题（数值仍给出，但结论不可信）。

用法
----
命令行：
    python gcl_ini.py <工程量统计.ini> [<输出.json>]
    python gcl_ini.py --help        # 用法 + 本文档（退出码 0）
    python gcl_ini.py               # 同 --help（无参只是"想看用法"，不是出错）

当库用：
    from gcl_ini import parse, summarize, dump_text
    d = parse(r"...\计算书\工程量统计\工程量统计.ini")
    print(summarize(d))
"""
import argparse
import io
import json
import os
import re
import sys

SECTION = re.compile(r"^\[([^\]]+)\]\s*$")
KV = re.compile(r"^([^=]+)=(.*)$")

# 材料代号 -> 名称（6 = 混凝土）
MAT = {"6": "混凝土", "1": "钢", "2": "砌体", "3": "木", "9": "其他"}

# Cap 行必须给出的列名；少一个，该层的数值就取不到（旧版会静默填 None -> 0.0）
REQUIRED_COLS = ("构件种类", "个数", "材料", "材料级别", "体积")

# Item-Sum 与明细之和的允许偏差（真实 ini 逐层精确相等，这里只容忍打印/求和误差）
SUM_TOL = 0.05

# 问题清单里逐条列出的上限（其余折成一行计数，避免几百行刷屏）
PROB_HEAD = 5


def _grade(s):
    """材料级别 30 -> C30；已是字符串就原样返回。"""
    s = (s or "").strip()
    if not s:
        return ""
    try:
        return "C%d" % int(float(s))
    except ValueError:
        return s


def _num(s):
    """字符串 -> float；**转不出来返回 None**，不再静默当成 0.0。

    旧实现在 `except ValueError: return 0.0`，于是"读不到"与"真的是 0"在产物里
    完全同形（S52）：一份列名对不上/带千分位的 ini 会汇总成合计 0 而退出码仍是 0。
    """
    if s is None or isinstance(s, bool):
        return None
    if isinstance(s, (int, float)):
        return float(s)
    t = str(s).strip().replace(" ", "").replace("\u00a0", "")
    if not t:
        return None
    try:
        return float(t)
    except ValueError:
        return None


def _flr(sec):
    """`Gcl-Hnt-Zrc3` -> `第3层`（只用于消息）。"""
    n = sec[len("Gcl-Hnt-Zrc"):]
    return "第%s层" % n if n else sec


def _read_text(path, problems):
    """按 GBK 读（YJK 写的是 GBK）；只有解不出来才降级，并把降级记成问题。"""
    for enc in ("gbk", "utf-8-sig", "utf-8"):
        try:
            with open(path, encoding=enc) as fh:
                return fh.read()
        except UnicodeDecodeError:
            continue
    with open(path, encoding="gbk", errors="replace") as fh:
        txt = fh.read()
    problems.append("%s：不是 GBK/UTF-8 能干净解码的文本，已按 gbk+errors=replace "
                    "解码，中文可能不可靠" % os.path.basename(path))
    return txt


def parse(path):
    """返回 {"info": {...}, "层": {...}, "problems": [...]}。

    problems 非空表示"这份 ini 的数值不完整或格式已变"，不要当成正常结果用。
    """
    problems, detail = [], []
    if not os.path.exists(path):
        raise IOError("找不到 %s" % path)
    txt = _read_text(path, problems)

    info, out = {}, {}
    cur = None
    cap = None
    dropped = {}
    for line in txt.splitlines():
        line = line.rstrip()
        if not line.strip():
            continue
        m = SECTION.match(line.strip())
        if m:
            cur = m.group(1)
            cap = None
            if cur.startswith("Gcl-Hnt-Zrc"):
                out[cur[len("Gcl-Hnt-Zrc"):]] = {"构件": [], "合计": None}
            continue
        m = KV.match(line.strip())
        if not m:
            continue
        k, v = m.group(1).strip(), m.group(2).strip()
        if cur and cur.startswith("Gcl-Hnt-Zrc"):
            fid = out[cur[len("Gcl-Hnt-Zrc"):]]
            if k == "Cap":
                cap = [x.strip() for x in v.split(",")]
                miss = [c for c in REQUIRED_COLS if c not in cap]
                if miss:
                    problems.append("%s：Cap 行缺列 %s（实际列名=%r）—— 该层数值不可信"
                                    % (_flr(cur), "、".join(miss), v))
            elif k.startswith("Item-") and k[5:].isdigit():
                if not cap:
                    dropped[cur] = dropped.get(cur, 0) + 1
                    continue
                cells = [x.strip() for x in v.split(",")]
                row = dict(zip(cap, cells))
                kind = row.get("构件种类", "")
                n = _num(row.get("个数"))
                vol = _num(row.get("体积"))
                grade = (row.get("材料级别") or "").strip()
                if len(cells) != len(cap):
                    # 少字段 = 行被截断；多字段 = 值里带了逗号（千分位 "620,861" 会被
                    # split 拆成两个单元格，zip 之后体积静默取到 "620" —— 1000 倍误差）
                    detail.append("%s %s：字段数 %d %s 列数 %d（内容=%r）"
                                  % (_flr(cur), k, len(cells),
                                     "少于" if len(cells) < len(cap) else "多于",
                                     len(cap), v))
                if not kind:
                    detail.append("%s %s：构件种类为空（列名错位？内容=%r）"
                                  % (_flr(cur), k, v))
                if n is None:
                    detail.append("%s %s：个数=%r 不是数值" % (_flr(cur), k,
                                                               row.get("个数")))
                if vol is None:
                    detail.append("%s %s：体积=%r 不是数值" % (_flr(cur), k,
                                                               row.get("体积")))
                if not grade:
                    detail.append("%s %s：材料级别为空（强度等级会缺失）"
                                  % (_flr(cur), k))
                fid["构件"].append({
                    "种类": kind,
                    "个数": 0.0 if n is None else n,
                    "材料": MAT.get(row.get("材料", ""), row.get("材料", "")),
                    "级别": _grade(grade),
                    "体积": 0.0 if vol is None else vol,
                })
            elif k == "Item-Sum":
                s = _num(v)
                if s is None:
                    detail.append("%s：Item-Sum=%r 不是数值" % (_flr(cur), v))
                else:
                    fid["合计"] = s
            elif k == "Name":
                fid["层"] = v
        elif cur == "INFO" or cur is None:
            info[k] = v

    if not out:
        problems.append("没有解析到任何自然层（[Gcl-Hnt-Zrc*] 段）—— 这不是"
                        "混凝土工程量统计 ini，或格式已变")
    for f, blk in out.items():
        items = blk["构件"]
        if not items:
            if dropped.get("Gcl-Hnt-Zrc" + f):
                problems.append("第%s层：%d 行 Item-* 因缺 Cap 行被丢弃，明细为空"
                                % (f, dropped["Gcl-Hnt-Zrc" + f]))
            else:
                problems.append("第%s层：明细为空（一行 Item-* 都没读到）" % f)
            continue
        if blk["合计"] is not None:
            s = sum(it["体积"] for it in items)
            if abs(s - blk["合计"]) > max(SUM_TOL, 1e-6 * abs(blk["合计"])):
                problems.append("第%s层：Item-Sum=%.3f 与明细之和 %.3f 差 %.3f"
                                "（容差 %.2f）—— 明细不完整"
                                % (f, blk["合计"], s, blk["合计"] - s, SUM_TOL))
    problems.extend(detail[:PROB_HEAD])
    if len(detail) > PROB_HEAD:
        problems.append("…… 另有 %d 处同类字段问题（未逐条列出）"
                        % (len(detail) - PROB_HEAD))
    return {"info": info, "层": out, "problems": problems}


def summarize(d):
    """汇总成 {构件种类: 全楼体积} + 逐层明细 + problems。

    多出来的键（层数 / 声明层数 / problems）是新增的：老调用方只读
    "按构件种类" / "合计" / "逐层"，不受影响。
    """
    per_kind = {}
    floors = {}
    problems = list(d.get("problems") or [])
    for f, blk in sorted(d["层"].items(),
                         key=lambda x: int(x[0]) if x[0].isdigit() else 0):
        kk = {}
        for it in blk.get("构件", []):
            kk[it["种类"]] = kk.get(it["种类"], 0.0) + it["体积"]
            per_kind[it["种类"]] = per_kind.get(it["种类"], 0.0) + it["体积"]
        tot = blk.get("合计")
        if tot is None:
            tot = sum(kk.values())
            if blk.get("构件"):
                problems.append("第%s层：没有 Item-Sum，小计改用明细求和 %.3f" % (f, tot))
        floors[f] = {"明细": blk.get("构件", []), "小计": tot, "按种类": kk}
    return {"按构件种类": per_kind, "合计": sum(per_kind.values()),
            "逐层": floors, "层数": len(floors),
            "声明层数": _declared_floors(d.get("info") or {}),
            "problems": problems}


def _declared_floors(info):
    """INFO 段 `Gcl-Hnt-ZrcNum`（混凝土统计的自然层数）-> int 或 None。"""
    v = _num(info.get("Gcl-Hnt-ZrcNum"))
    if v is None:
        return None
    n = int(v)
    return n if n > 0 else None


def dump_text(d):
    s = summarize(d)
    L = ["混凝土工程量（YJK 上部结构工程量统计）",
         "=" * 58,
         "%-10s %8s %8s %10s %14s" % ("层", "构件", "个数", "级别", "体积(m3)")]
    for f in sorted(s["逐层"], key=lambda x: int(x) if x.isdigit() else 0):
        blk = s["逐层"][f]
        for it in blk["明细"]:
            L.append("%-10s %8s %8d %10s %14.3f"
                     % ("第%s层" % f, it["种类"], int(it["个数"]), it["级别"], it["体积"]))
        L.append("%-10s %8s %8s %10s %14.3f" % ("", "小计", "", "", blk["小计"]))
    L.append("-" * 58)
    for k, v in s["按构件种类"].items():
        L.append("%-10s %8s %8s %10s %14.3f" % ("全楼", k, "", "", v))
    L.append("%-10s %8s %8s %10s %14.3f" % ("全楼", "合计", "", "", s["合计"]))
    if s["problems"]:
        L.append("-" * 58)
        L.append("!! 数据问题 %d 项（以下数值不可信）：" % len(s["problems"]))
        for p in s["problems"]:
            L.append("   " + p)
    return "\n".join(L)


def _utf8_console():
    """stdout / stderr 的编码错误策略改成 errors='replace'。

    Windows 默认 GBK 控制台下，`--help` 一旦打印出 cp936 编不出的字符就抛
    UnicodeEncodeError，退出码变成 1 —— "想看帮助"被上层判成"脚本崩了"。
    本文件输出里的非 ASCII 字符都是 cp936 可编码的，这层兜底保证以后再加字符
    也只是显示成 '?'，不会中断进程、更不会污染退出码。

    注意：`reconfigure` 只在真正的 TextIOWrapper 上有；被重定向成 io.StringIO
    之类（测试里很常见）时跳过，不能因为这个把脚本搞崩。
    """
    for st in (sys.stdout, sys.stderr):
        try:
            st.reconfigure(errors="replace")
        except (AttributeError, ValueError, OSError):
            pass


def main(argv=None):
    """命令行入口。

    为什么用 argparse：以前这里是 `sys.exit(__doc__)`，而无参调用时
    `sys.exit(<字符串>)` 的语义是"错误退出"（消息打到 stderr、返回 1），
    不是"打印帮助"。现在：`--help` 打印到 stdout 并退出 0；无参也打印用法并
    退出 0（纯信息性用法说明，不是错误）。

    退出码：找不到文件 = 1（人话提示，不抛 traceback）；解析出数据问题 = 2；
    正常 = 0。
    """
    _utf8_console()
    ap = argparse.ArgumentParser(
        prog="gcl_ini.py",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="解析 YJK「工程量统计.ini」—— 上部结构的混凝土工程量。",
        epilog=__doc__)
    ap.add_argument("ini", nargs="?", help="工程量统计.ini 的路径（GBK 编码）")
    ap.add_argument("json_out", nargs="?",
                    help="可选：把 info + 汇总另存为该 json 文件（utf-8）")
    a = ap.parse_args(argv)
    if not a.ini:
        # 无参 = 想看用法，不是出错：用法打到 stdout，退出码 0
        ap.print_help(sys.stdout)
        return 0
    if not os.path.isfile(a.ini):
        print("找不到 ini 文件：%s" % a.ini, file=sys.stderr)
        return 1
    d = parse(a.ini)
    print(dump_text(d))
    if a.json_out:
        with io.open(a.json_out, "w", encoding="utf-8") as fh:
            json.dump({"info": d["info"], "汇总": summarize(d)}, fh,
                      ensure_ascii=False, indent=2)
        print("\n-> %s" % a.json_out)
    probs = summarize(d)["problems"]
    if probs:
        print("\n!! 解析发现 %d 项数据问题 —— 退出码 2（上面的数值不可信）"
              % len(probs), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
