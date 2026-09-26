# -*- coding: utf-8 -*-
r"""对某个 设计结果 目录做实算复核，输出 JSON + 控制台报告。

复核项（对应报告 sheet5）：
  1 轴压比     逐柱 Uc ≤ 限值（限值来自 --config 的 抗震.轴压比限值，短柱 −0.05）
  2 超限条数   wpj*.out 中「超限」行数
  3 层间位移角 wdisp.out  Max-Dx/h、Max-Dy/h ≤ 1/800
  4 层刚度比   wmass.out  Ratx1/Raty1、Ratx2/Raty2
  5 短柱       λc ≤ 2 的柱数
用法: python verify_results.py <设计结果目录> --db <模型.ydb> [--config c.json]
                              [--json out.json]
"""
import argparse
import collections
import json
import os
import re
import struct
import sqlite3
import sys

HDR = re.compile(r"第\s*(\d+)\s*层\(标准层\s*(\d+)")
NCHDR = re.compile(r"N-C=(\d+)\s*\(I=\d+,\s*J=\d+\)\s*\((\d+)\)\s*([^\r\n]*)")


def _utf8_console():
    """让输出在任何控制台编码下都不崩（GBK 下把不可编码字符替换掉）。

    为什么需要（实测缺陷 X8）：本文件会打印 `−`(U+2212 数学减号) 与 `⚠`，
    这两个字符**不在 cp936 里**。默认 GBK 控制台下 `print` 会抛
    `UnicodeEncodeError: 'gbk' codec can't encode character '\u2212'`，
    并且**以退出码 1 中断** —— 连 `--help` 都打不出来：
        python verify_results.py --help
        UnicodeEncodeError: 'gbk' codec can't encode character '\u2212' in position 407
    （argparse 的 help 也是写到 sys.stdout 的，所以同样受影响。）

    `errors="replace"` 在 UTF-8 控制台下原样输出、在 GBK 下退化成 `?`，都不崩。
    只在实际执行时调用（`main()` 开头），**不在 import 时改 stdout** ——
    这个脚本会被别的脚本当模块 import，污染别人的 stdout 是不对的。
    """
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass
# ★ 这里**不内置任何工程的分组表与等级表**（写死就换不了工程）：
#   `GROUPS`（16 柱编号分组）与 `STD_GRADE`（C60/C50/…），换工程后分组错、
#   "真值砼"整列错，却照样打印"满足"。现在 --db 是**必填**：
#   分组按柱坐标现算（groups_from_db），等级取模型 tblStdFlr.Para[4]（grades_from_db）。
# ★ 轴压比**限值**同理不能内置：限值随 结构体系 + 抗震等级 变（框架二级 0.75、
#   框架-核心筒二级 0.85、三级 0.85…），写死一个数就等于替用户假定体系。
#   所以限值一律取自 --config 的 抗震.轴压比限值（与 section_opt.py 同一份配置）；
#   没给 --config 时只能用框架-核心筒二级的 0.85 兜底，并**打印醒目警告**。
FC = {"C25": 11.9, "C30": 14.3, "C35": 16.7, "C40": 19.1, "C45": 21.1,
      "C50": 23.1, "C55": 25.3, "C60": 27.5, "C65": 29.7, "C70": 31.8}

# tblStdFlr.Para 里 柱 强度×10 的下标（板/柱/梁/墙 = 2/4/5/6，取 4）
PARA_IDX_COL = 4

# 没给 --config 时假定的轴压比限值（框架-核心筒 二级）。**这只是兜底**，
# 会给结论带来偏松的风险，所以用到它时必须打印警告（见 main）。
LIMIT_ASSUMED = 0.85

# 规范限值（新增为常量：原来这两个数散在 print 里写死，判定逻辑要复用它们）
DRIFT_LIMIT = 800       # 层间位移角限值 1/800（框架-核心筒，JGD3-2010）
STIFF_LIMIT = 1.0       # 层刚度比限值（YJK 定义：≥1.0 满足）
# 短柱折减：JGJ3-2010 表6.4.2 注 —— 剪跨比 λ≤2 的短柱，轴压比限值减小 0.05
SHORT_COL_DEDUCT = 0.05


def grades_from_db(db):
    """从模型库读各标准层的**柱**混凝土等级：{标准层No_: "C50"}。

    权威来源是 `tblStdFlr.Para` 下标 4（柱 强度×10，300=C30）——那才是
    YJK 真正用来算的字段（见 write_sections.set_grades 的 docstring）。
    """
    con = sqlite3.connect("file:%s?mode=ro" % os.path.abspath(db), uri=True)
    try:
        out = {}
        for no, para in con.execute("SELECT No_, Para FROM tblStdFlr"):
            if not para:
                continue
            parts = str(para).split(",")
            if len(parts) <= PARA_IDX_COL:
                continue
            try:
                out[int(no)] = "C%d" % (int(float(parts[PARA_IDX_COL])) // 10)
            except ValueError:
                continue
        return out
    finally:
        con.close()


def groups_from_db(db):
    """按**柱坐标**现算各标准层的 中柱/边柱/角柱 分组：{标准层No_: OrderedDict}。

    ★ 不能写死柱号（老 GROUP_OF 就是写死的，换个柱网全错）。判据与
      expand_plan.classify() 一致：X、Y 都在内部 = 中柱；只有一个在内部 = 边柱；
      都在外圈 = 角柱。
    """
    import expand_plan                                          # 同目录
    cols_by_std = expand_plan.read_columns(db)
    out = collections.OrderedDict()
    for std, d in sorted(cols_by_std.items()):
        cls = expand_plan.classify(d["cols"])
        out[std] = collections.OrderedDict(
            (k, cls[k]) for k in ("中柱", "边柱", "角柱") if cls.get(k))
    return out


def limit_from_config(path):
    """读 `--config` 里的轴压比**基准**限值：{"抗震": {"轴压比限值": 0.85, ...}}。

    ★ 这是与 `section_opt.py` 同一份配置（同一键），所以"选型用的限值"与
      "复核用的限值"必然一致 —— 否则会出现"选型说满足、复核说超限"的假分歧。
      短柱折减不在这里做（是逐柱的，见 main 里的 `lim`）。
    """
    # config.json 是**人可能用记事本改过**的输入：用 utf-8-sig 读，带不带 BOM 都认
    # （按 utf-8 读时 BOM 会留在第一个键名里，表现为"配置里的键找不到"）。
    cfg = json.load(open(path, encoding="utf-8-sig"))
    v = cfg.get("抗震", {}).get("轴压比限值")
    if v is None:
        raise SystemExit("!! %s 里没有 抗震.轴压比限值（复核必需的限值不能凭空假定）"
                         % path)
    return float(v)


def rd(p):
    return open(p, "rb").read().decode("gbk", "replace")


def parse_wpj(path):
    txt = rd(path)
    hm = HDR.search(txt)
    if not hm:
        return []
    nat, stdno = int(hm.group(1)), int(hm.group(2))
    marks = [m.start() for m in re.finditer(r"N-C=", txt)]
    out = []
    for a, b in zip(marks, marks[1:] + [len(txt)]):
        blk = txt[a:b]
        m = NCHDR.match(blk)
        if not m:
            continue
        col, geo = int(m.group(1)), m.group(3).strip()
        mx = re.match(r"B\*H\*U\*T\*D\*F\(mm\)=\s*([\d.]+)\*([\d.]+)", geo)
        mb = re.match(r"B\*H\(mm\)=\s*([\d.]+)\*([\d.]+)", geo)
        if mx:
            b, h = float(mx.group(1)), float(mx.group(2))
        elif mb:
            b, h = float(mb.group(1)), float(mb.group(2))
        else:
            continue
        uc = re.search(r"\(\s*(\d+)\s*\)\s*Nu=\s*(-?[\d.]+)\s+Uc=\s*([\d.]+)", blk)
        rcc = re.search(r"Rcc=\s*([\d.]+)", blk)
        lamx = re.search(r"X:\s*λc=\s*([\d.]+)", blk)
        lamy = re.search(r"Y:\s*λc=\s*([\d.]+)", blk)
        over = re.findall(r"\*\*[^\r\n]*超限[^\r\n]*", blk)
        # 配筋率超限（原文形如 "**上截面，位置:9 最大配筋率超限 3.62%>2.75% 《高规》6.3.3"）
        pr = re.findall(r"\*\*([^\r\n]*?配筋率[^\r\n]*?)([\d.]+)%>([\d.]+)%", blk)
        pr_max = max((float(x[1]) for x in pr), default=None)
        out.append({
            "自然层": nat, "标准层": stdno, "柱号": col,
            "截面": "%d×%d" % (round(b), round(h)), "b": b, "h": h,
            "短柱": "短柱" in blk,
            "材料": ("C%d" % round(float(rcc.group(1)))) if rcc else "?",
            "Nu": float(uc.group(2)) if uc else None,
            "Uc": float(uc.group(3)) if uc else None,
            "lamX": float(lamx.group(1)) if lamx else None,
            "lamY": float(lamy.group(1)) if lamy else None,
            "超限": bool(over), "超限文": over[:1],
            "配筋率实算": pr_max, "配筋率限值": float(pr[0][2]) if pr else None,
            "配筋率超限": bool(pr),
        })
    return out


def parse_wdisp(res):
    """层间位移角：wdisp.out 以 `1/N` 分数形式给出（N 越大力越安全）。

    注意 `1/9999` 是 YJK 的哨兵值（该层位移近似为 0），必须剔除，
    否则会被当成"最不利 1/1"（旧版解析就踩了这个坑）。

    ★★ 但「剔完什么都不剩」与「一点都没解析到」是**两件完全不同的事**，
       老版本把两者都打成「（未解析到）」并且都静默返回，调用方无法区分
       「位移角 ≈ 0、远小于限值（**满足**）」和「解析失败、这一项**根本没核**」。
       实测缺陷 D3：16 个算例里有 4 个（低层 + 大刚度 + 弱抗震）位移小到
       YJK 对**每个工况的每一层**都输出 9999，于是复核结果看起来像"没做这项检查"；
       自动调用方按退出码判定时会把「没核」当成「通过」。

    返回 `(best, src)`：
      best = `{工况名: 最不利的 N}`（1/N 中最小的 N，已剔除 9999）
      src  = `实测`      有实数可用
             `全部哨兵`  文件在，且所有 `1/N` 都是 9999（位移≈0，远小于限值）
             `未解析到`  文件在，但没有任何 `1/N` 形式的位移角（解析口径可能变了）
             `无文件`    wdisp.out 不存在（没算，或结果目录给错了）
    """
    p = os.path.join(res, "wdisp.out")
    if not os.path.exists(p):
        return {}, "无文件"
    txt = rd(p)
    best = {}
    seen = 0
    for m in re.finditer(r"===\s*工况\d+\s*===\s*([^\r\n]*)", txt):
        seg = txt[m.end(): m.end() + 60000]
        nxt = seg.find("===")
        if nxt > 0:
            seg = seg[:nxt]
        vals = [int(v) for v in re.findall(r"1/(\d+)", seg)]
        seen += len(vals)
        real = [v for v in vals if v != 9999]
        if real:
            best[m.group(1).strip()] = min(real)
    if best:
        return best, "实测"
    # 有 `1/N` 但全是哨兵 → 位移确实小到不可测；一个都没有 → 解析口径对不上
    return {}, ("全部哨兵" if seen else "未解析到")


def crosscheck_wdisp_sentinel(res, limit=DRIFT_LIMIT):
    """把「全部哨兵」这个**结论**用同文件里的原始位移量**交叉印证**一遍。

    ★ 为什么必须交叉印证（不要只信哨兵值）
    --------------------------------------
    `verify_results.py` 把「1/N 全是 9999」判为**满足**（理由：9999 是 YJK 的
    "比值优于 1/9999" 上限，即位移≈0）。这个判断一旦错，就是一条**静默成功路径**
    （把"没算/没输出"当成"满足"）。所以不能只凭哨兵自证，要用**同一份文件里
    另一列的数**去验：wdisp.out 每层两行，第一行给层高 `h`，第二行给
    `Max-Dx`/`Max-Dy`（最大层间位移，mm）与 `Max-Dx/h`（就是那个 1/9999）。
    于是可以现算 `h / Max-Dx`，看它是不是真的 > 限值。

    返回 `(结论, 最不利N, 行数, 说明)`：
      结论 = True  哨兵与位移量**一致**（现算的最不利 1/N > limit）→ 满足可信
             False 哨兵与位移量**矛盾**（现算的最不利 1/N ≤ limit）→ 不能判满足
             None  **无法交叉印证**（这一列解析不出来）→ 只能说"按哨兵判定"
    """
    p = os.path.join(res, "wdisp.out")
    if not os.path.exists(p):
        return None, 0, 0, "无 wdisp.out"
    txt = rd(p)
    worst = None
    n = 0
    lines = txt.splitlines()
    for i, l in enumerate(lines):
        toks = l.split()
        if not toks or "1/9999" not in l:
            continue
        # 数据行形如：     6000025      0.21     0.19       1/9999     11.89%    1.00
        try:
            j = [k for k, t in enumerate(toks) if t.startswith("1/")]
            if not j:
                continue
            k = j[0]
            maxd = float(toks[k - 2])          # Max-Dx（或 Max-Dy）
        except (ValueError, IndexError):
            continue
        # 层高 h 在**上一行**的最后一个数字
        h = None
        for back in (1, 2):
            if i - back >= 0:
                pt = [t for t in lines[i - back].split()
                      if re.fullmatch(r"\d+(\.\d+)?", t)]
                if pt:
                    try:
                        hv = float(pt[-1])
                    except ValueError:
                        continue
                    if hv > 100:                # 层高（mm），排除位移/比值列
                        h = hv
                        break
        if not h or maxd <= 0:
            continue
        r = h / maxd                            # = 1/(Max-Dx/h)
        n += 1
        if worst is None or r < worst:
            worst = r
    if not n or worst is None:
        return None, 0, 0, "解析不出「最大层间位移 / 层高」列，无法交叉印证"
    w = int(worst)
    if w > limit:
        return True, w, n, ("现算最不利 1/%d（%d 层）> 1/%d，与哨兵一致" % (w, n, limit))
    return False, w, n, ("现算最不利 **1/%d**（%d 层）**不优于** 1/%d —— 哨兵值与"
                        "位移量矛盾，不能判满足" % (w, n, limit))


def parse_wmass_stiff(res):
    """刚度比：wmass.out 每个「Floor No.」块给一组 Ratx1/Raty1/Ratx2/Raty2。
    YJK 原文定义 —— Ratx1 = 本层塔侧移刚度与上一层相应刚度的 70% 之比、
    或与上三层平均刚度的 80% 之比，取小者；故 **≥1.0 即满足**。
    Ratx2 同理（与上层 90%/110%/150% 之比）。
    返回 {字段: [(层号, 值), ...]}
    """
    p = os.path.join(res, "wmass.out")
    if not os.path.exists(p):
        return {}
    txt = rd(p)
    keys = ("Ratx1", "Raty1", "Ratx2", "Raty2")
    out = {k: [] for k in keys}
    for m in re.finditer(r"Floor No\.\s*(\d+)\s+Tower No\.\s*(\d+)(.*?)(?=Floor No\.|$)",
                         txt, re.S):
        fl, body = int(m.group(1)), m.group(3)
        for k in keys:
            mm = re.search(k + r"\s*=\s*(-?[\d.]+)", body)
            if mm:
                out[k].append((fl, float(mm.group(1))))
    return out


def main():
    _utf8_console()          # ★ 必须在 argparse 之前：--help 也是写到 stdout 的
    ap = argparse.ArgumentParser()
    ap.add_argument("res")
    ap.add_argument("--json", default=None)
    ap.add_argument("--strict", action="store_true",
                    help="按规范结论给退出码：有项没取到值 → 3；规范指标不满足 → 4；"
                         "否则 0。★ 自动化编排务必加：'算完了'与'没问题'是两回事，"
                         "不加这个开关，一份超限的设计和一份通过的设计都返回 0"
                         "（实测：示例同构配置 Uc=1.066、超限 20 条，而所有自动闸门都放行）")
    ap.add_argument("--db", required=True,
                    help="模型库(.ydb/.ymd)：分组按柱坐标现算、等级取 tblStdFlr.Para[4]。"
                         "★ 必填 —— 分组与等级无法凭空推断，写死某工程的口径会给出错误结论")
    ap.add_argument("--config", default=None,
                    help="config.json（与 section_opt.py 同一份）：轴压比**限值**取它的 "
                         "抗震.轴压比限值（短柱再 −0.05，JGJ3-2010 表6.4.2 注）。"
                         "★ 不给就用兜底的 %.2f 并打印警告 —— 限值随结构体系/抗震等级变，"
                         "不该由本脚本替用户假定" % LIMIT_ASSUMED)
    a = ap.parse_args()
    res = a.res

    rows = []
    for n in range(1, 80):
        p = os.path.join(res, "wpj%d.out" % n)
        if os.path.exists(p):
            rows.extend(parse_wpj(p))
    if not rows:
        # ★ 区分「结果目录给错/没算」与「这个模型根本没有柱」。
        #   实测情形（缺陷 D1 修好后才走得到的路径）：纯剪力墙模型
        #   （核心筒放大到整个平面）`tblColSeg = 0`，YJK 自然不产出 wpj*.out，
        #   老代码只喊一句「没解析到 wpj*.out」，看起来像路径写错了。
        #   本脚本的复核项里有几项是**柱专属**的（轴压比、配筋率、短柱），
        #   对没有柱的模型不适用 —— 直接说清楚，比让人去查路径强。
        ncol = None
        try:
            con = sqlite3.connect("file:%s?mode=ro" % os.path.abspath(a.db), uri=True)
            try:
                ncol = con.execute("select count(*) from tblColSeg").fetchone()[0]
            finally:
                con.close()
        except sqlite3.Error:
            ncol = None
        if ncol == 0:
            # ★ 注意别把话说错：实测 C09（纯剪力墙）**是有 wpj*.out 的**
            #   （4 个文件、每个约 17 KB），只是里面 `N-C=` 柱记录为 0 条 ——
            #   因为模型根本没有柱。所以不能说「没有 wpj 是正常的」。
            nwpj = len([i for i in range(1, 80)
                        if os.path.exists(os.path.join(res, "wpj%d.out" % i))])
            raise SystemExit(
                "!! 本模型**没有柱**（%s 的 tblColSeg = 0）→ wpj 里也就没有柱记录。\n"
                "   实测：%s 下确实有 %d 个 wpj*.out，但里面 `N-C=` 柱记录 0 条。\n"
                "   本脚本的复核项里 **轴压比 / 配筋率 / 短柱 都是柱专属的**，"
                "对纯剪力墙这类无柱结构不适用；\n"
                "   仍然适用的只有**层间位移角**与**层刚度比**（整体指标），"
                "它们不在 wpj 里 ——\n"
                "   请直接读 %s\\wdisp.out 与 wmass.out，或换一个有柱的模型跑本脚本。"
                % (a.db, res, nwpj, res))
        extra = ("（%s 的 tblColSeg = %d，模型里是有柱的）" % (a.db, ncol)) if ncol else ""
        nwpj = len([i for i in range(1, 80)
                    if os.path.exists(os.path.join(res, "wpj%d.out" % i))])
        raise SystemExit(
            "!! %s 下没解析到 wpj*.out 的柱记录%s\n"
            "   该目录里有 %d 个 wpj*.out —— 所以不是「没算」，而是**解析不出来**。\n"
            "   常见原因：结果目录给错（应给 `设计结果` 子目录）/ 计算中止没写结果 / "
            "wpj 的格式变了（见 SKILL.md 的解析口径）。" % (res, extra, nwpj))

    stds = sorted({r["标准层"] for r in rows})
    print("=" * 96)
    print("实算复核：%s" % res)
    print("=" * 96)
    print("  柱段记录 %d 条 | 标准层 %s | 自然层 %d..%d"
          % (len(rows), stds, min(r["自然层"] for r in rows), max(r["自然层"] for r in rows)))

    # ---- 轴压比限值：优先 --config，其次兜底 + 警告（见文件头的说明） ----
    if a.config:
        base_lim = limit_from_config(a.config)
        print("  轴压比限值 %.2f（来自 %s 的 抗震.轴压比限值；短柱再 −%.2f，"
              "JGJ3-2010 表6.4.2 注）" % (base_lim, os.path.basename(a.config),
                                          SHORT_COL_DEDUCT))
    else:
        base_lim = LIMIT_ASSUMED
        print("")
        print("  " + "!" * 88)
        print("  !! 未给 --config：轴压比限值按 **框架-核心筒 二级 %.2f**（短柱 %.2f）假定。"
              % (base_lim, base_lim - SHORT_COL_DEDUCT))
        print("  !! 限值随 结构体系 + 抗震等级 变（框架二级 0.75、框架-核心筒二级 0.85…），"
              "用错限值会让“满足”变成假结论。")
        print("  !! 请用 --config <config.json>（键 抗震.轴压比限值）覆盖后重跑。")
        print("  " + "!" * 88)

    # ---- 分组与等级：一律从 --db 现算（换工程自动跟随，不套用任何写死口径） ----
    by_std = groups_from_db(a.db)
    GRADE = grades_from_db(a.db)
    if not by_std:
        raise SystemExit("!! 从 %s 读不到柱分组（tblColSeg/tblJoint 为空？）" % a.db)
    if not GRADE:
        raise SystemExit("!! 从 %s 读不到柱混凝土等级（tblStdFlr.Para[4] 为空？）" % a.db)
    print("  分组/等级来源：--db（按柱坐标现算 中柱/边柱/角柱；"
          "等级取 tblStdFlr.Para[4] 柱强度×10）")
    print("     %s" % {k: len(v) for k, v in GRADE.items()})

    # 柱号 -> 组（按标准层分开，因为柱号是标准层内的建模序号）
    group_of_std = {}
    for std, gs in by_std.items():
        for g, cols in gs.items():
            for c in cols:
                group_of_std[(std, c)] = g

    def groups_for(std):
        gs = by_std.get(std)
        if not gs:
            raise SystemExit(
                "!! 标准层 %s 在 %s 里没有柱分组记录（wpj 与模型对不上？）" % (std, a.db))
        return gs

    # ---- wpj 覆盖性：逐标准层核对"wpj 里的柱号"与"模型里的柱号" ----
    # ★★ 这一段是补的**硬伤**：老版本这里是 `if not rs: continue`，一旦 wpj 的
    #    N-C 与模型 tblColSeg.No_ 对不上，28 个标准层只会报出 1 个，其余 27 个
    #    **静默消失**，报告照样打印"满足"—— 看不到、也不报错。现在一律"响"。
    model_cols = {std: {c for cols in gs.values() for c in cols}
                  for std, gs in by_std.items()}
    wpj_cols = collections.OrderedDict()
    for r in rows:
        wpj_cols.setdefault(r["标准层"], set()).add(r["柱号"])
    all_model_cols = set().union(*model_cols.values()) if model_cols else set()

    n_cov = len([s for s in by_std if s in wpj_cols])
    print("\n  wpj 覆盖：标准层 %d..%d（%d/%d），柱号并集 %d 个"
          % (min(stds), max(stds), n_cov, len(by_std), len(all_model_cols)))

    # 有模型柱、wpj 里却一条记录都没有的标准层：报告会缺层，必须说出来再退出
    lost = [s for s in sorted(by_std) if s not in wpj_cols]
    if lost:
        print("\n  ⚠ 警告：这些标准层在模型里有柱，但 wpj 里一条记录都没有：%s%s"
              % (lost[:20], "…" if len(lost) > 20 else ""))
        print("     （共 %d 层；复核报告会缺少这些层，所以这里直接退出而不是照常打印）"
              % len(lost))
        print("     先确认 设计结果\\wpj*.out 是否齐、标准层的编号口径是否一致。")
        sys.exit(3)

    # 逐层核对柱号：对不上就**当场退出**，不许静默少报。
    # 同时把"每柱多段"的段号折回模型柱号（见 common.layer_segment_map 的说明）。
    import common                                                 # 同目录
    col_of = {}                    # (标准层, wpj 柱号) -> 模型柱号
    seg_k = {}                     # 标准层 -> 每柱段数
    for std in sorted(wpj_cols):
        wcols, mcols = wpj_cols[std], model_cols.get(std, set())
        m = common.layer_segment_map(mcols, wcols)
        if m is None:
            extra = sorted(wcols - mcols)          # wpj 有、模型本层没有
            miss = sorted(mcols - wcols)           # 模型本层有、wpj 没有
            nowhere = sorted(wcols - all_model_cols)   # 全模型都没有的柱号
            sys.exit(
                "!! 标准层 %d 的 wpj 柱号与模型对不上：wpj %d 段 / 模型 %d 柱\n"
                "   wpj 里本层模型没有的柱号：%s（共 %d 个，只列前 10）\n"
                "   本层模型有、wpj 里没有的柱号：%s（共 %d 个，只列前 10）\n"
                "   其中有 %d 个柱号在**全部**标准层的模型柱号里都不存在：%s\n"
                "   本层模型柱号：%s …\n"
                "   wpj 的 N-C 与模型 tblColSeg.No_ 对不上：检查是否按标准层各自从 1 "
                "开始编号 / 分组是否按坐标算"
                % (std, len(wcols), len(mcols),
                   extra[:10], len(extra), miss[:10], len(miss),
                   len(nowhere), nowhere[:10] or "无", sorted(mcols)[:10]))
        seg_k[std] = (len(wcols) // len(mcols)) if mcols else 1
        for nc, col in m.items():
            col_of[(std, nc)] = col

    multi = [(std, len(wpj_cols[std]), len(model_cols[std]), seg_k[std])
             for std in sorted(seg_k) if seg_k[std] > 1]
    if multi:
        print("  （这些标准层的 wpj 柱段数大于模型柱数：YJK 把柱沿高切成了多段。"
              "段号按柱连续编号，已按 `(段号-1)//k+1` 折回模型柱号 —— 两段都算该柱）")
        for std, nw, nm, k in multi[:6]:
            print("     标准层%-3d wpj %d 段 / 模型 %d 柱（每柱 %d 段）" % (std, nw, nm, k))

    # ---- 逐 (标准层, 组) 控制值 ----
    cnt = collections.Counter()
    # ★ 记录「哪些复核项**没有真的核**」。这是缺陷 D3 的正面修法：
    #   老版本「位移角全是哨兵值」与「解析失败」都打成「（未解析到）」且静默返回 0，
    #   调用方分不出「满足」与「没核」。现在这项机械可判，并可用 --strict 升级成硬失败。
    not_evaluated = []
    # ★ 不满足项清单必须**在这里**就建好：下面「层间位移角」那一段会往里追加
    #   「哨兵值与位移量矛盾」。老版把 `problems = []` 写在最后的总判定之前，
    #   而那一段在它之前执行 —— 一旦真的走到矛盾分支就是 NameError 崩掉，
    #   本该判「不满足」的场景反而变成看不懂的 traceback（rc=1 但不是 4）。
    problems = []
    print("\n  各标准层 × 柱位组 控制轴压比（材料取 YJK 实算值）")
    print("  %-5s %-4s %-11s %-5s %-5s %-5s %-11s %-9s %-8s %s"
          % ("标准层", "组", "截面", "实算砼", "真值砼", "限值", "Nu(kN)", "Uc实算", "Uc真值", "判定"))
    tbl = {}
    worst_all = 0.0
    worst_desc = ""
    for std in stds:
        for g, gc in groups_for(std).items():
            # 柱段号先折回模型柱号（多段的首层要靠这一步才不会整层落空）
            rs = [r for r in rows if r["标准层"] == std
                  and col_of.get((std, r["柱号"]), r["柱号"]) in gc]
            if not rs:
                # 模型说这一层有这个组（柱号来自 tblColSeg.No_），wpj 却一条都没有 ——
                # 这正是"整层被静默跳过"的入口，必须报错而不是 continue
                sys.exit("!! 标准层 %d 的「%s」组在模型里有 %d 根柱（%s…），wpj 里却一条"
                         "记录都没有\n"
                         "   拒绝静默跳过（老版 `if not rs: continue` 会把整层漏掉，"
                         "报告少层却不报警）\n"
                         "   多半是 wpj 的 N-C 与模型 tblColSeg.No_ 对不上：检查是否按"
                         "标准层各自从 1 开始编号 / 分组是否按坐标算"
                         % (std, g, len(gc), sorted(gc)[:10]))
            w = max(rs, key=lambda r: r["Uc"] or 0)
            # 限值 = config 基准 − 短柱折减（JGJ3-2010 表6.4.2 注）
            lim = base_lim - (SHORT_COL_DEDUCT if w["短柱"] else 0.0)
            gr = GRADE.get(std)
            if gr is None or gr not in FC:
                gr, fc_real = None, None
            else:
                fc_real = FC[gr]
            uc_real = (abs(w["Nu"]) * 1000.0 / (w["b"] * w["h"] * fc_real)
                       if (w["Nu"] and fc_real) else None)
            ok = (uc_real is not None and uc_real <= lim + 1e-9)
            if uc_real and uc_real > worst_all:
                worst_all = uc_real
                colno = col_of.get((std, w["柱号"]), w["柱号"])
                worst_desc = "标准层%d %s 柱%d%s (自然层%d)" % (
                    std, g, w["柱号"],
                    "" if colno == w["柱号"] else "→模型柱号%d" % colno, w["自然层"])
            tbl["%d|%s" % (std, g)] = {
                "截面": w["截面"], "实算砼": w["材料"], "真值砼": gr,
                "Nu": w["Nu"], "Uc实算": w["Uc"], "Uc真值": uc_real,
                "限值": lim, "短柱": w["短柱"], "控制柱": w["柱号"],
                # ★ 新键（不改动上面任何旧键）：多段层的 wpj 段号 ≠ 模型柱号，
                #   报告里要能看出到底是哪根柱控制
                "控制柱号": col_of.get((std, w["柱号"]), w["柱号"]),
                "控制自然层": w["自然层"], "判定": "满足" if ok else "**超限**"
            }
            print("  %-5d %-4s %-11s %-5s %-5s %-5.2f %-11.1f %-9.3f %-8.3f %s"
                  % (std, g, w["截面"], w["材料"], gr or "-", lim, w["Nu"] or 0,
                     w["Uc"] or 0, uc_real or 0,
                     "满足" if ok else ("**超限**" if ok is False else "无法判定")))
            cnt["超限组"] += 0 if ok else 1

    # ---- 超限条数 ----
    nover = sum(1 for r in rows if r["超限"])
    print("\n  超限条数（wpj 原文）：%d 条（柱段总数 %d）" % (nover, len(rows)))
    cnt["超限条数"] = nover

    # ---- 短柱 ----
    nshort = sum(1 for r in rows if r["短柱"])
    print("  短柱标记柱段：%d 条" % nshort)
    cnt["短柱条数"] = nshort

    # ---- 层间位移角 ----
    disp, disp_src = parse_wdisp(res)
    print("\n  层间位移角（wdisp.out，限值 1/800）")
    for k in sorted(disp):
        n = disp[k]
        print("    %-44s 最不利 1/%-5d %s" % (k, n, "满足" if n >= 800 else "**超限**"))
    if not disp:
        # ★ 三种情况必须分开说（缺陷 D3）：把「位移≈0」说成「未解析到」，
        #   读者会以为这项没做检查；而把「未解析到」说成「满足」更是错。
        if disp_src == "全部哨兵":
            print("    全部工况的 1/N 都是哨兵值 9999 = **每层位移都近似为 0**，")
            print("    远小于 1/800 限值 → **视为满足**（这与「没有数据」不同：位移确实小到不可测）")
        elif disp_src == "未解析到":
            print("    **未解析到**：wdisp.out 在，但里面没有 `1/N` 形式的位移角。")
            print("    ★ 这是**本项没有核**，不是「满足」—— 请检查 wdisp.out 的格式是否变了")
        else:
            print("    **无 wdisp.out**（结果目录给错？还是没跑计算？）—— 本项没有核")
    if disp_src == "全部哨兵":
        # ★★ 「全部哨兵」**不是「未取到」，而是一个有据的结论**：YJK 用 `1/9999`
        #   表示"该层位移近似为 0"，所以它等价于「位移角远小于限值 → 满足」。
        #   以前这里把它和「未解析到/无文件」一起塞进 not_evaluated，
        #   于是 `--strict` 在**低层/刚度大**的模型上恒返 3 —— 实测 50 案例里
        #   24 次 verify 落在这里，过半数的复核被报成"这项没核"，
        #   噪声大到让 `--strict` 失去意义（缺陷 L6）。
        #   现在：哨兵 → 计入"满足"并**保留来源**；只有"未解析到/无文件"才算没核。
        #
        #   ★★ 但"满足"这个结论**不能只靠哨兵自证**：万一把"没输出"读成哨兵，
        #      就是一条静默成功路径。所以这里用同文件里的 `h` 与 `Max-Dx` 列
        #      **现算**一遍位移角来交叉印证（见 crosscheck_wdisp_sentinel）。
        xok, xworst, xn, xwhy = crosscheck_wdisp_sentinel(res)
        disp_satisfied_by_sentinel = True
        if xok is True:
            print("    ★ 交叉印证：%s" % xwhy)
        elif xok is None:
            print("    ★ **无法交叉印证**（%s）—— 本项按哨兵值判定为满足，"
                  "但请留意这一列的格式是否变了" % xwhy)
        else:
            # 哨兵与位移量矛盾 → 不许判满足（这是最危险的形态：假满足）
            disp_satisfied_by_sentinel = False
            print("    !! %s" % xwhy)
            problems.append("位移角：wdisp.out 报的 1/9999 与同文件位移量矛盾"
                            "（现算 %d 层最不利 1/%d）—— 本项**不能判满足**"
                            % (xn, xworst))
    else:
        disp_satisfied_by_sentinel = False
        xok, xworst, xn, xwhy = None, 0, 0, ""
    if disp_src in ("未解析到", "无文件"):
        # 让调用方能机械判别「哪些指标没取到」，而不是靠读中文
        not_evaluated.append("位移角(%s)" % disp_src)

    # ---- 刚度比 ----
    stiff = parse_wmass_stiff(res)
    print("\n  层刚度比（wmass.out，取全楼最小；YJK 定义 ≥1.0 满足）")
    if stiff:
        for k in ("Ratx1", "Raty1", "Ratx2", "Raty2"):
            if not stiff.get(k):
                continue
            f, v = min(stiff[k], key=lambda x: x[1])
            print("    %-6s 最小 %.3f @自然层%-3d %s"
                  % (k, v, f, "满足" if v >= 1.0 else "**不满足**"))
    else:
        print("    （未解析到）")
        not_evaluated.append("层刚度比(未解析到)")

    # ---- 配筋率超限 ----
    npr = sum(1 for r in rows if r["配筋率超限"])
    if npr:
        agg = collections.Counter(
            "标准层%d-%s" % (r["标准层"],
                            group_of_std.get((r["标准层"],
                                              col_of.get((r["标准层"], r["柱号"]),
                                                         r["柱号"])), "?"))
            for r in rows if r["配筋率超限"])
        worst_pr = max((r for r in rows if r["配筋率超限"]),
                       key=lambda r: r["配筋率实算"] or 0)
        print("\n  最大配筋率超限：%d 条柱段（限值 %.2f%%）"
              % (npr, worst_pr["配筋率限值"] or 0))
        print("    最不利 %.2f%% @自然层%d 柱%d %s"
              % (worst_pr["配筋率实算"], worst_pr["自然层"], worst_pr["柱号"],
                 worst_pr["截面"]))
        for k, v in sorted(agg.items()):
            print("      %-12s %d 条" % (k, v))
    else:
        print("\n  最大配筋率超限：无")

    print("\n  结论：最不利轴压比 Uc = %.3f @ %s" % (worst_all, worst_desc))
    print("        轴压比限值 %.2f%s（超限组 %d 个）"
          % (base_lim, "（来自 --config）" if a.config
             else "（**假定值**，未经 --config 覆盖）", cnt["超限组"]))
    if npr:
        print("        最大配筋率超限 %d 条（最不利 %.2f%% > %.2f%%）"
              % (npr, worst_pr["配筋率实算"], worst_pr["配筋率限值"] or 0))
    else:
        print("        最大配筋率：无超限")

    stiff_min = {}
    for k, v in stiff.items():
        if v:
            f, val = min(v, key=lambda x: x[1])
            stiff_min[k] = {"最小": val, "层号": f}

    # ---- 规范指标总判定（缺陷 D4 的正面修法）----
    # 为什么需要这一段：**「算完了」与「没问题」之间原来没有自动的桥**。
    # 随包示例配置 + 一个很自然的起始柱截面（600×600 C40）建出来的 10 层框架，
    # 实测最不利 Uc = 1.066、wpj 超限 20 条，而 `ydb_lint`、导入闸门、计算链路
    # **全部一路绿灯** —— 它们查的是「模型自洽」和「跑通了」，不是「截面够不够」。
    # 真正把超限翻出来的是本脚本，但本脚本对「超限」也返回 0，所以自动化编排
    # 依然可能把一份超限的设计当成通过。
    # 现在把判定显式打出来、写进 JSON，并让 `--strict` 能把它升级成硬失败。
    # （`problems` 已在上面「位移角」那一段之前初始化，那里会往里追加矛盾项。）
    if cnt.get("超限条数"):
        problems.append("wpj 超限 %d 条" % cnt["超限条数"])
    if npr:
        problems.append("配筋率超限 %d 条" % npr)
    if base_lim and worst_all > base_lim:
        problems.append("最不利 Uc %.3f > 限值 %.2f" % (worst_all, base_lim))
    if disp:
        d = min(disp.values())
        if d < DRIFT_LIMIT:
            problems.append("位移角 1/%d < 1/%d" % (d, DRIFT_LIMIT))
    for k, v in stiff_min.items():
        if v["最小"] < STIFF_LIMIT:
            problems.append("%s %.3f < %.1f" % (k, v["最小"], STIFF_LIMIT))
    if problems:
        verdict = "不满足"
    elif not_evaluated:
        verdict = "要素未核"
    else:
        verdict = "满足"
    print("\n" + "=" * 96)
    print("  规范指标判定：%s" % verdict)
    if problems:
        print("    不满足项：%s" % "、".join(problems))
    if not_evaluated:
        print("    未取到（没真的核）的项：%s" % "、".join(not_evaluated))
    if not problems and not not_evaluated:
        print("    全部复核项都取到值且满足")
    print("    （★ 「算完了」不等于「没问题」：本行才是规范层面的结论。）")
    print("=" * 96)

    # ---- S26：不加 --strict 时，结论**不进退出码**，必须把这件事说出来 ----------
    # 老版的问题不是"判定算错了"，而是"判定没接到任何调用方能看见的地方"：
    # 一份超限 20 条的设计与一份全通过的设计都返回 0，编排脚本不读 JSON 就分辨不出。
    # 退出码语义（0/3/4，且 4 优先于 3）是既定契约，这里**不改**；改成把这件事
    # 显式打出来，并把同一份结论写进 JSON 的「判定」/「不满足项」/「未取到」三个键。
    if not a.strict and (problems or not_evaluated):
        print("\n!! 未加 --strict：上面这个结论**没有**反映到退出码 —— 本次退出码仍是 0。")
        print("   自动化编排必须二者取一：① 加 --strict（不满足 4 / 要素未核 3）；")
        print("   ② 读 JSON 的「判定」（满足/不满足/要素未核）与「不满足项」「未取到」键。")

    out = {"res": res, "rows": len(rows), "tbl": tbl, "cnt": dict(cnt),
           # ★ 报告要能引用"用了哪个限值"：写进 JSON，免得事后无从解释判定依据
           "轴压比限值": base_lim,
           "轴压比限值来源": (os.path.abspath(a.config) if a.config
                              else "假定（框架-核心筒 二级 %.2f，未经 --config 覆盖）"
                                   % LIMIT_ASSUMED),
           "短柱折减": SHORT_COL_DEDUCT,
           "最不利Uc": worst_all, "最不利位置": worst_desc,
           "配筋率超限条数": npr,
           "配筋率最不利": ({"实测": worst_pr["配筋率实算"], "限值": worst_pr["配筋率限值"],
                             "自然层": worst_pr["自然层"], "柱号": worst_pr["柱号"],
                             "截面": worst_pr["截面"]} if npr else None),
           "位移角": disp,
           # ★ 让调用方能机械判别位移角这一项的**可信来源**（缺陷 D3）：
           #   实测 / 全部哨兵（位移≈0，视为满足）/ 未解析到（没核）/ 无文件（没核）
           "位移角来源": disp_src,
           # ★ 「全部哨兵」= 位移≈0，**算满足**（不是"没核"）。这里单独标出来，
           #   免得事后有人看到 `位移角: {}` 就以为这项没做（缺陷 L6）。
           "位移角全部哨兵": bool(disp_satisfied_by_sentinel),
           # ★ 哨兵结论的**交叉印证**结果（用同文件的 h 与 Max-Dx 现算）：
           #   通过=True/矛盾=False/无法印证=None —— 让调用方知道"满足"是怎么来的。
           "位移角哨兵交叉印证": ({"通过": xok, "现算最不利": xworst, "层数": xn,
                                   "说明": xwhy} if disp_src == "全部哨兵" else None),
           "刚度比": stiff_min,
           # ★ 本次**没有真的核**的复核项清单（空 = 全部核过）。
           #   自动调用方应当据此判定，而不是只看退出码 —— 老版本两者都返回 0。
           "未取到": list(not_evaluated),
           # ★ 规范层面的一句话结论，供调用方直接读（缺陷 D4）
           "判定": verdict,
           "不满足项": list(problems),
           "超限明细": [r for r in rows if r["超限"]][:60]}
    if a.json:
        json.dump(out, open(a.json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("-> %s" % a.json)
    # ★ 「不满足」(4) 优先于「要素未核」(3)：前者是已确认的问题，后者只是没核到。
    if a.strict and problems:
        print("\n!! --strict：规范指标不满足 → %s" % "、".join(problems))
        sys.exit(4)
    if a.strict and not_evaluated:
        print("\n!! --strict：有复核项没取到值 → %s" % "、".join(not_evaluated))
        sys.exit(3)
    return out


if __name__ == "__main__":
    main()
