# -*- coding: utf-8 -*-
r"""把「施工图 + 工程量」的产出汇总成一份可交付的 Excel。

输入（都在 <留档目录>/ 下，由 draw_quant.py 生成）：
    工程量统计.ini              YJK 混凝土工程量（GBK）
    全楼楼板钢筋用量.xlsx        YJK 板钢筋
    全楼梁钢筋用量(钢筋规格与类别).xlsx
    全楼柱钢筋用量(钢筋规格与类别).xlsx
    全楼墙钢筋用量.xlsx
    run_manifest.json           运行清单

输出：<留档目录>/<工程>_施工图与工程量汇总.xlsx，6 页
    1.汇总          —— 混凝土 / 钢筋 分构件小计 + 单位面积指标
    2.混凝土工程量   —— 逐层 × 构件，体积 m3
    3.钢筋工程量     —— 逐构件 × 直径，kg（含全楼合计）
    4.施工图清单     —— 生成的 DWG 文件一览（含每个文件的状态）
    5.计算口径       —— 口径说明与校核依据
    6.自检          —— 交叉校核

退出码与自检
------------
第 6 页每行按级别写结论：硬问题用 ★ 开头，提示用 "!" 开头（各层构件不同、
DWG 疑似截断这类正常差异），陈述不带标记。有一个 ★ 就返回 2 —— 交付物照旧
写出，但结论不可信。旧版无论自检整页 ★ 都返回 0，于是"指错了目录"与
"完整留档"在退出码上完全同形。

  --area   每层楼面面积（m2），不是全楼面积；全楼 = 每层 × 层数
  --floors 自然层数（默认从 ini 的 Gcl-Hnt-ZrcNum / 逐层段数 / 钢筋表逐层行推断）
  --allow-incomplete  明知留档不全也返回 0（问题照旧打印，★ 照旧写进第 6 页）

单方指标的全楼面积：默认把钢筋表的逐层楼面面积**求和**（不拿层数换算），
只有显式给了 --area 才用"每层 × 层数"。旧版写死 ×3，层数不是 3 的工程
单方指标会偏好几倍（S47）。

用法：
    python summary_xlsx.py <留档目录> [--name 工程名]
"""
import argparse
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from openpyxl import Workbook, load_workbook                       # noqa: E402
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side  # noqa: E402
from openpyxl.utils import get_column_letter                       # noqa: E402

import gcl_ini                                                     # noqa: E402
import read_yjk_xlsx as R                                          # noqa: E402

F_TITLE = Font(name="微软雅黑", size=14, bold=True, color="1F3864")
F_H1 = Font(name="微软雅黑", size=10, bold=True, color="FFFFFF")
F_H2 = Font(name="微软雅黑", size=10, bold=True, color="1F3864")
F_TXT = Font(name="微软雅黑", size=10)
F_BOLD = Font(name="微软雅黑", size=10, bold=True)
F_NOTE = Font(name="微软雅黑", size=9, color="808080")
FILL_H = PatternFill("solid", fgColor="4472C4")
FILL_H2 = PatternFill("solid", fgColor="D9E2F3")
FILL_TOT = PatternFill("solid", fgColor="FFF2CC")
THIN = Side(style="thin", color="BFBFBF")
BORD = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
CEN = Alignment(horizontal="center", vertical="center")
LEFT = Alignment(horizontal="left", vertical="center", wrap_text=True)
RIGHT = Alignment(horizontal="right", vertical="center")
N0, N1, N2, N3 = "#,##0", "#,##0.0", "#,##0.00", "#,##0.000"


def title(ws, text, ncol, sub=None):
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=ncol)
    c = ws.cell(1, 1, text)
    c.font, c.alignment = F_TITLE, CEN
    ws.row_dimensions[1].height = 30
    if sub:
        ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=ncol)
        c = ws.cell(2, 1, sub)
        c.font, c.alignment = F_NOTE, LEFT
        ws.row_dimensions[2].height = 18
        return 4
    return 3


def put(ws, row, vals, fmts=None, fonts=None, fill=None, h=20, aligns=None):
    for i, v in enumerate(vals):
        c = ws.cell(row, i + 1, v)
        c.font = (fonts[i] if fonts and i < len(fonts) else F_TXT)
        c.alignment = (aligns[i] if aligns and i < len(aligns) else CEN)
        c.border = BORD
        if fmts and i < len(fmts) and fmts[i] and isinstance(v, (int, float)):
            c.number_format = fmts[i]
        if fill:
            c.fill = fill
    ws.row_dimensions[row].height = h


def head(ws, row, vals, widths=None, h=26):
    put(ws, row, vals, fonts=[F_H1] * len(vals), fill=FILL_H, h=h)
    if widths:
        for i, w in enumerate(widths):
            ws.column_dimensions[get_column_letter(i + 1)].width = w
    return row + 1


# ------------------------------------------------------------------ 数据
REBAR_FILES = [
    ("楼板", "全楼楼板钢筋用量*.xlsx"),
    ("梁", "全楼梁钢筋用量*.xlsx"),
    ("柱", "全楼柱钢筋用量*.xlsx"),
    ("墙", "全楼墙钢筋用量*.xlsx"),
]


def parse_rebar(path):
    """读 YJK 钢筋用量表 -> {直径str: kg}（**全楼合计**行）。

    布局（YJKS 7.1.0，三种构件列数不同）：

      板 (9×11):  r2 表头 ['','楼层','楼面面积(m2)','HRB400',…,'合计(kg)','单位面积量']
                  r3 直径行 [6,8,10,14,16,18] 位于第 4~9 列
                  r4~r6 每层一行；r7 '合计' 行；r8 尾部重复总计行
      梁 (21×15): r2 表头含 '钢筋类别'；r3 直径行 [6,8,12,18,20,22,25,28,32]
                  r4~r18 每层 5 行（上部纵筋/下部纵筋/箍筋/腰筋/腰筋拉结筋）
                  r19 '全楼' 行
      柱 (13×9):  r3 直径行 [8,18,20]；r11 '全楼' 行

    ★ 两个坑：
      1. **直径行在表头行的下一行**（表头行只有 'HRB400' 这个合并标题，没有数字）。
         在表头行上找直径会一无所获。
      2. 表尾还有一行**只重复总计数字**（r8 / r20 / r12），第一列是空的 ——
         不能用"第一个数字行"来当合计，必须认 '全楼' / '合计' / '总计' 文字。
    """
    try:
        wb = R.load(path)
    except Exception as e:                                         # noqa: BLE001
        return {}, "读取失败 %r" % e
    ws = wb[wb.sheetnames[0]]
    rows = [[c for c in r] for r in ws.iter_rows(values_only=True)]

    # 1) 直径行：前 10 行里出现 >=2 个 4~50 的数值
    dia = None
    for r in rows[:10]:
        nums = [(j, int(v)) for j, v in enumerate(r)
                if isinstance(v, (int, float)) and not isinstance(v, bool)
                and 4 <= v <= 50]
        if len(nums) >= 2:
            dia = {j: str(v) for j, v in nums}
            break

    # 2) 全楼行：**楼层列（第2列）精确等于** '全楼'/'合计'/'总计'
    #    ★ 坑：不能在前几列里做「包含」匹配 —— 板的标题行是
    #      ['', '全楼楼板钢筋用量', ...]，含「全楼」二字，会被误当合计行
    #      （那一行的直径列全是空 → 结果读成 0）。必须精确等于。
    TOTAL_WORDS = {"全楼", "合计", "总计"}
    for r in rows:
        key = str(r[1]).strip() if len(r) > 1 and r[1] is not None else ""
        if key not in TOTAL_WORDS:
            continue
        if dia is None:
            return {}, None            # 无直径列 = 该构件没有钢筋（合法，例如无墙）
        out = {}
        for j, d in dia.items():
            if j < len(r) and isinstance(r[j], (int, float)):
                out[d] = out.get(d, 0.0) + float(r[j])
        if out:
            return out, None
    return {}, "未找到全楼合计行"


def sum_rows(rows, keys=("全楼", "合计", "总计")):
    """在任意行里找第一个**楼层列精确等于**合计关键字的行并返回该行。"""
    kw = set(keys)
    for r in rows:
        key = str(r[1]).strip() if len(r) > 1 and r[1] is not None else ""
        if key in kw:
            return r
    return None


def _utf8_console():
    """把 stdout / stderr 的编码错误策略改成 errors='replace'。

    为什么必须做（实测踩过）：本脚本跑在 Windows 默认的 GBK 控制台上时，
    `print` 一旦遇到 cp936 编不出的字符就抛 UnicodeEncodeError。
    当时的症状很坑：源码里有 m 加 U+00B3 / m 加 U+00B2 写的体积/面积单位，
    **xlsx 已经 save 成功（见 main 末尾 wb.save）之后**才在打印摘要时崩，
    进程退出码却是 1 —— 任何按退出码判定的上层编排会把"成功"当成"失败"。
    源码里那些字符已全部换成 ASCII（m3 / m2），这一层只是兜底：
    以后谁再往输出里加非 cp936 字符（U+2705 的对勾、希腊字母 Phi、U+33A1 的
    平方符号），最坏也只是显示成 '?'，不会中断进程、更不会污染退出码。

    注意：`reconfigure` 只在真正的 TextIOWrapper 上有；被重定向成
    io.StringIO 之类（测试里很常见）时就跳过，不能因为这个把脚本搞崩。
    """
    for st in (sys.stdout, sys.stderr):
        try:
            st.reconfigure(errors="replace")
        except (AttributeError, ValueError, OSError):              # noqa: PERF203
            pass


# ------------------------------------------------------------------ 自检级别与判定
LEVEL_FAIL = "fail"        # 硬问题：输入缺 / 读不出 / 算不出来 -> 退出码 2
LEVEL_WARN = "warn"        # 提示：正常差异（各层构件不同、DWG 疑似截断）
LEVEL_INFO = "info"        # 陈述：结论本身

SHEETS = ["1.汇总", "2.混凝土工程量", "3.钢筋工程量",
          "4.施工图清单", "5.计算口径", "6.自检"]

# DWG 文件头 6 字节应为 AC10xx（AC1015=R2000 … AC1032=2018）
DWG_MAGIC = b"AC10"
# 比这个还小的 DWG 不可能是真图（实图几 KB 起）；只提示，不判死
DWG_MIN_BYTES = 1024


def ck_row(ck, item, value, concl, level=LEVEL_INFO):
    """往自检表加一行并带级别。级别不写进工作簿，只决定退出码。"""
    ck.append((item, value, concl, level))


def dwg_scan(d, names):
    """逐个 DWG 读大小与文件头 -> (清单 rows, 硬问题 bad, 提示 tiny)。

    只数"glob 到几个文件"会把绘制中断留下的 0 字节文件算成正常施工图（S53）：
    数量与"能不能用"是两件事，所以这里真打开文件读头 6 字节。
    """
    sd = os.path.join(d, "施工图")
    rows, bad, tiny = [], [], []
    for f in names:
        p = os.path.join(sd, f)
        if not os.path.exists(p):
            p = os.path.join(d, f)
        if not os.path.exists(p):
            rows.append((f, None, "★读不到"))
            bad.append("%s：清单里有、但两个目录都找不到" % f)
            continue
        size = os.path.getsize(p)
        if size == 0:
            rows.append((f, 0, "★0 字节"))
            bad.append("%s：0 字节（绘制中断或被拦下留下的空文件）" % f)
            continue
        try:
            with open(p, "rb") as fh:
                head = fh.read(6)
        except OSError as e:
            rows.append((f, size, "★读不到"))
            bad.append("%s：打不开（%s）" % (f, e))
            continue
        if not head.startswith(DWG_MAGIC):
            rows.append((f, size, "★不是 DWG"))
            bad.append("%s：不是 DWG（头部=%r，%d 字节）" % (f, head, size))
        elif size < DWG_MIN_BYTES:
            rows.append((f, size, "疑似截断"))
            tiny.append("%s：%d 字节（< %d），疑似截断" % (f, size, DWG_MIN_BYTES))
        else:
            rows.append((f, size, "正常"))
    return rows, bad, tiny


def sheet_areas(path):
    """钢筋表里的逐层楼面面积（第 2 列以"第"开头、第 3 列是数值）。读不到返回 []。"""
    out = []
    try:
        wb = R.load(path)
        ws = wb[wb.sheetnames[0]]
        for r in ws.iter_rows(values_only=True):
            sv = str(r[1]) if len(r) > 1 and r[1] is not None else ""
            if sv.startswith("第") and len(r) > 2 and \
                    isinstance(r[2], (int, float)) and not isinstance(r[2], bool):
                out.append(float(r[2]))
    except Exception:                                              # noqa: BLE001
        return []
    return out


def verify_written(path):
    """写盘后把 xlsx 读回来复检 -> (ok, why)。

    `wb.save()` 返回 None，"调用过 save"不等于"内容完整"；旧版写完就打
    "已生成"并返回 0，从不复检（S54）。
    """
    try:
        wb2 = load_workbook(path, read_only=True, data_only=True)
    except Exception as e:                                         # noqa: BLE001
        return False, "读不回来：%r" % e
    got = list(wb2.sheetnames)
    if got != SHEETS:
        wb2.close()
        return False, "页不对：%s" % got
    has_total = False
    for row in wb2["1.汇总"].iter_rows(min_col=1, max_col=1, values_only=True):
        if row and str(row[0]).strip() == "合计":
            has_total = True
            break
    wb2.close()
    if not has_total:
        return False, "1.汇总 里没有合计行"
    return True, "%d 页 / %d B" % (len(got), os.path.getsize(path))


def main():
    _utf8_console()
    ap = argparse.ArgumentParser()
    ap.add_argument("dir", help="draw_quant.py 的留档目录")
    ap.add_argument("--name", default=None, help="工程名（默认取目录名）")
    ap.add_argument("--area", type=float, default=None,
                    help="每层楼面面积 m2，不是全楼面积（默认把钢筋表逐层面积求和；"
                         "给了它则全楼 = 每层 × 层数）")
    ap.add_argument("--floors", type=int, default=None,
                    help="自然层数（默认从 ini 的 Gcl-Hnt-ZrcNum / 逐层段数 / "
                         "钢筋表逐层行数推断）")
    ap.add_argument("--allow-incomplete", action="store_true",
                    help="自检有硬问题也返回 0（问题照旧打印并写进第 6 页）")
    a = ap.parse_args()

    d = os.path.abspath(a.dir)
    if not os.path.isdir(d):
        sys.exit("目录不存在：%s" % d)
    if a.area is not None and a.area <= 0:
        sys.exit("--area 必须是正数：%r" % a.area)
    if a.floors is not None and a.floors < 1:
        sys.exit("--floors 必须是正整数：%r" % a.floors)
    name = a.name or os.path.basename(d)
    ck = []

    # ---- 混凝土 ----
    ini = os.path.join(d, "工程量统计.ini")
    conc = None
    if os.path.exists(ini):
        conc = gcl_ini.summarize(gcl_ini.parse(ini))
        conc_probs = list(conc.get("problems") or [])
        if conc["逐层"]:
            ck_row(ck, "混凝土工程量来源", "工程量统计.ini（YJK 上部结构统计）", "已读取")
        else:
            # 文件在、一层明细都没有：以前这里照旧打印"已读取"并给出合计 0（S52）
            ck_row(ck, "混凝土工程量来源", "工程量统计.ini",
                   "★读到了文件，却一层明细都没解析出来", LEVEL_FAIL)
        for i, p in enumerate(conc_probs[:6], 1):
            ck_row(ck, "混凝土 ini 问题 %d" % i, p, "★数据不完整", LEVEL_FAIL)
        if len(conc_probs) > 6:
            ck_row(ck, "混凝土 ini 问题", "另有 %d 项（详见 gcl_ini.py 输出）"
                   % (len(conc_probs) - 6), "★数据不完整", LEVEL_FAIL)
    else:
        ck_row(ck, "混凝土工程量来源", "工程量统计.ini", "★缺失", LEVEL_FAIL)

    # ---- 钢筋 ----
    # 三态：读到数据 / 文件里确实 0（本工程无该类构件）/ 读取失败
    rebar, rebar_note, rebar_zero = {}, {}, []
    for kind, pat in REBAR_FILES:
        hits = glob.glob(os.path.join(d, pat))
        if not hits:
            hits = glob.glob(os.path.join(d, "施工图", pat))
        if not hits:
            rebar_note[kind] = "未找到文件"
            continue
        v, err = parse_rebar(hits[0])
        if err:
            rebar_note[kind] = err
        elif not v or sum(v.values()) == 0:
            rebar_zero.append(kind)        # 合法：本工程没有该构件
            rebar[kind] = {}
        else:
            rebar[kind] = v

    # ---- 施工图 ----
    sd = os.path.join(d, "施工图")
    dwgs = sorted(os.path.basename(x)
                  for x in (glob.glob(os.path.join(sd, "*.dwg")) +
                            glob.glob(os.path.join(d, "*.dwg"))))
    dwg_rows, dwg_bad, dwg_tiny = dwg_scan(d, dwgs)

    # ---- 面积与层数 ----
    # 旧版把全楼面积写死成"每层 × 3"，层数不是 3 的工程单方指标会错好几倍（S47）；
    # 层数在同一个脚本里就有（ini 的 Gcl-Hnt-ZrcNum / 逐层段数 / 钢筋表逐层行数）。
    floor_areas = []
    for _kind, pat in REBAR_FILES:
        hits = glob.glob(os.path.join(d, pat)) or \
            glob.glob(os.path.join(d, "施工图", pat))
        if hits:
            floor_areas = sheet_areas(hits[0])
            if floor_areas:
                break
    declared = (conc or {}).get("声明层数")
    conc_floors = len((conc or {}).get("逐层") or {})
    if a.floors:
        floors, floor_src = int(a.floors), "--floors"
    elif declared:
        floors, floor_src = int(declared), "ini Gcl-Hnt-ZrcNum"
    elif conc_floors:
        floors, floor_src = conc_floors, "ini 逐层段数"
    elif floor_areas:
        floors, floor_src = len(floor_areas), "钢筋表逐层行数"
    else:
        floors, floor_src = None, "推断不出"
    if declared and conc_floors and int(declared) != conc_floors:
        ck_row(ck, "层数口径", "ini 声明 %d 层 vs 逐层段数 %d" % (declared, conc_floors),
               "! 两处不一致（按 %s 计）" % floor_src, LEVEL_WARN)
    if floors and floor_areas and len(floor_areas) != floors:
        ck_row(ck, "层数口径", "推断 %d 层（%s）vs 钢筋表 %d 行楼面面积"
               % (floors, floor_src, len(floor_areas)),
               "! 两处不一致（全楼面积按逐层求和）", LEVEL_WARN)

    if a.area:
        per_floor = float(a.area)
        full_area = per_floor * floors if floors else None
        area_src = "--area（每层）× %s" % (floors if floors else "层数未知")
    elif floor_areas:
        full_area = sum(floor_areas)
        per_floor = full_area / len(floor_areas)
        area_src = "钢筋表逐层楼面面积求和（%d 行）" % len(floor_areas)
    else:
        per_floor, full_area, area_src = None, None, "钢筋表里没有逐层楼面面积"
    if not full_area:
        ck_row(ck, "单方指标", "%s；层数 %s（%s）" % (area_src, floors, floor_src),
               "★没算出单方指标（用 --area 给每层面积，必要时加 --floors）",
               LEVEL_FAIL)
    else:
        ck_row(ck, "单方指标口径", "每层 %.2f m2、全楼 %.2f m2（%s）"
               % (per_floor, full_area, area_src),
               "层数 %s（%s）" % (floors, floor_src))

    # ================================================== 建工作簿
    wb = Workbook()
    wb.remove(wb.active)

    # ---------- 1. 汇总 ----------
    ws = wb.create_sheet("1.汇总")
    r0 = title(ws, "%s · 施工图与工程量汇总" % name, 6,
               "数据来源：YJK 实算（施工图生成 + 工程量统计模块）")
    rows_h = ["构件", "个数", "混凝土 (m3)", "钢筋 (kg)", "钢筋 (t)", "备注"]
    r0 = head(ws, r0, rows_h, widths=[14, 10, 16, 16, 12, 30])

    conc_kind = (conc or {}).get("按构件种类", {})
    conc_kinds = {k: v for k, v in conc_kind.items() if v}
    conc_cnt = {}
    if conc:
        for f, blk in conc["逐层"].items():
            for it in blk["明细"]:
                conc_cnt[it["种类"]] = max(conc_cnt.get(it["种类"], 0), int(it["个数"]))

    rebar_tot = {}
    for kind, v in rebar.items():
        rebar_tot[kind] = sum(v.values())

    for kind in ("梁", "柱", "楼板", "墙"):
        c = conc_kind.get(kind, 0.0)
        b = rebar_tot.get(kind, 0.0)
        if not c and not b and kind not in rebar_zero:
            continue
        note = "混凝土来自 工程量统计.ini" if c else "—"
        if kind in rebar_zero:
            note = "本工程无此构件钢筋" if not c else note + "；无钢筋"
        put(ws, r0, [kind, conc_cnt.get(kind, ""), c, b, b / 1000.0 if b else "", note],
            fmts=[None, None, N3, N1, N3, None],
            fonts=[F_BOLD, F_TXT, F_TXT, F_TXT, F_TXT, F_NOTE])
        r0 += 1
    tc, tb = sum(conc_kind.values()), sum(rebar_tot.values())
    put(ws, r0, ["合计", "", tc, tb, tb / 1000.0, "混凝土+钢筋"],
        fmts=[None, None, N3, N1, N3, None],
        fonts=[F_BOLD] * 6, fill=FILL_TOT)
    r0 += 1

    if full_area:
        r0 += 1
        put(ws, r0, ["指标（按每层楼面面积 %.2f m2，全楼 %.2f m2）"
                     % (per_floor, full_area),
                     "", "", "", "", ""], fonts=[F_H2] * 6, fill=FILL_H2)
        r0 += 1
        put(ws, r0, ["混凝土单方", "m3/m2", tc / full_area, "", "", ""],
            fmts=[None, None, N3, None, None, None])
        r0 += 1
        put(ws, r0, ["钢筋单方", "kg/m2", tb / full_area, "", "", ""],
            fmts=[None, None, N2, None, None, None])
        r0 += 2
    else:
        # 面积/层数取不到时不能编一个数字出来（旧版写死 ×3，见 S47）
        r0 += 1
        put(ws, r0, ["★ 没取到楼面面积/层数 —— 未给出单方指标"
                     "（用 --area 每层面积、必要时加 --floors）",
                     "", "", "", "", ""], fonts=[F_NOTE] * 6, aligns=[LEFT] * 6)
        r0 += 2
    put(ws, r0, ["说明：钢筋为 YJK 工程量统计模块输出的《全楼…钢筋用量》表，"
                 "含量已含损耗前的净用量。", "", "", "", "", ""],
        fonts=[F_NOTE] * 6, aligns=[LEFT] * 6)

    # ---------- 2. 混凝土 ----------
    ws = wb.create_sheet("2.混凝土工程量")
    r0 = title(ws, "混凝土工程量（逐层 × 构件）", 6,
               "来源：<工程目录>\\计算书\\工程量统计\\工程量统计.ini")
    r0 = head(ws, r0, ["层", "构件种类", "个数", "材料", "强度等级", "体积 (m3)"],
              widths=[12, 14, 10, 10, 12, 16])
    if conc:
        for f in sorted(conc["逐层"], key=lambda x: int(x) if x.isdigit() else 0):
            blk = conc["逐层"][f]
            for it in blk["明细"]:
                put(ws, r0, ["第%s层" % f, it["种类"], int(it["个数"]),
                             it["材料"], it["级别"], it["体积"]],
                    fmts=[None, None, None, None, None, N3])
                r0 += 1
            put(ws, r0, ["", "小计", "", "", "", blk["小计"]],
                fmts=[None, None, None, None, None, N3],
                fonts=[F_BOLD] * 6, fill=FILL_H2)
            r0 += 1
        put(ws, r0, ["全楼", "合计", "", "", "", conc["合计"]],
            fmts=[None, None, None, None, None, N3],
            fonts=[F_BOLD] * 6, fill=FILL_TOT)
        r0 += 2
        put(ws, r0, ["口径：柱体积 = 个数 × 截面面积 × 层高；"
                     "楼板体积按扣除梁占位后的净板面积 × 板厚；梁按净长（扣柱）。",
                     "", "", "", "", ""], fonts=[F_NOTE] * 6, aligns=[LEFT] * 6)
    else:
        put(ws, r0, ["★ 未找到 工程量统计.ini —— 混凝土统计未执行成功", "", "", "", "", ""],
            fonts=[F_TXT] * 6, aligns=[LEFT] * 6)

    # ---------- 3. 钢筋 ----------
    ws = wb.create_sheet("3.钢筋工程量")
    all_d = sorted({d for v in rebar.values() for d in v}, key=lambda x: int(x))
    r0 = title(ws, "钢筋工程量（按构件 × 直径）", max(4, len(all_d) + 3),
               "来源：YJK 工程量统计模块《全楼…钢筋用量(钢筋规格与类别)》")
    hdr = ["构件"] + ["HRB400[Φ%s]" % x for x in all_d] + ["合计 (kg)", "占比"]
    r0 = head(ws, r0, hdr, widths=[12] + [14] * len(all_d) + [16, 10])
    for kind in ("楼板", "梁", "柱", "墙"):
        if kind not in rebar:
            continue
        v = rebar[kind]
        tot = sum(v.values())
        vals = [kind] + [v.get(x, 0.0) for x in all_d] + \
               [tot, (tot / tb if tb else 0)]
        put(ws, r0, vals,
            fmts=[None] + [N1] * len(all_d) + [N1, "0.0%"],
            fonts=[F_BOLD] + [F_TXT] * len(all_d) + [F_BOLD, F_TXT])
        r0 += 1
    put(ws, r0, ["合计"] + [sum(rebar[k].get(x, 0.0) for k in rebar) for x in all_d] +
        [tb, 1.0],
        fmts=[None] + [N1] * len(all_d) + [N1, "0.0%"],
        fonts=[F_BOLD] * (len(all_d) + 3), fill=FILL_TOT)
    r0 += 2
    if rebar_note:
        put(ws, r0, ["未读取到：" + "；".join("%s（%s）" % (k, v) for k, v in rebar_note.items()),
                     "", "", "", "", ""], fonts=[F_NOTE] * 6, aligns=[LEFT] * 6)

    # ---------- 4. 施工图清单 ----------
    ws = wb.create_sheet("4.施工图清单")
    r0 = title(ws, "生成的施工图文件", 4, "来源：<工程目录>\\施工图\\")
    r0 = head(ws, r0, ["序号", "文件名", "大小 (B)", "状态"],
              widths=[8, 52, 14, 16])
    # 只写 "getsize if exists else 0" 会把"读不到"与"0 字节"混成同一个 0（S53）；
    # 这里逐个真读文件头，状态写进第 4 列。
    for i, (f, size, st) in enumerate(dwg_rows, 1):
        put(ws, r0, [i, f, size if size is not None else "", st],
            fmts=[None, None, N0, None], aligns=[CEN, LEFT, RIGHT, CEN])
        r0 += 1
    n_bad = sum(1 for _f, _s, st in dwg_rows if st.startswith("★"))
    put(ws, r0, ["", "共 %d 个 DWG" % len(dwgs), "",
                 ("★不可用 %d 个" % n_bad) if n_bad else "全部可用"],
        fonts=[F_BOLD] * 4, fill=FILL_TOT)

    # ---------- 5. 计算口径 ----------
    ws = wb.create_sheet("5.计算口径")
    r0 = title(ws, "计算口径与生成链条", 2)
    r0 = head(ws, r0, ["项目", "说明"], widths=[24, 88])
    for k, v in [
        ("驱动方式", "官方 IPC 通道（YJKSControl.RunCmd），yjks 无参启动 + 常驻进程托管"),
        ("模型导入", "UINew 建工程 → yjk_importydb 导入 .ydb → **几何表逐表校核**（防空模型）"),
        ("计算", "yjk_setlayersupport → yjkspre_genmodrel → yjktransload_tlplan/tlvert → "
                 "SetCurrentLabel IDSPRE_ROOT → yjkdesign_dsncalculating_all → SetCurrentLabel IDDSN_DSP"),
        ("混凝土工程量", "切「楼层组装」IDModule_Layer → yjkconcreteStat_statCom "
                        "→ 计算书\\工程量统计\\工程量统计.ini"),
        ("板施工图", "SetCurrentLabel IDDTL_DETAIL_SLAB → StdSlab_RedrawNceng → StdSlab_AUTOCAL "
                    "→ StdSlab_batgenstl（批量出图+选筋）→ stdslab_AutoStatstl（全楼钢筋统计）"),
        ("梁施工图", "SetCurrentLabel IDDTL_DETAIL_BEAM → DtlRC_RegenReinsUpdateBeamPlan"),
        ("柱施工图", "SetCurrentLabel IDDTL_DETAIL_COLUMN → DtlRC_DrawNewColPlan"),
        ("墙施工图", "SetCurrentLabel IDDTL_DETAIL_WALL → DtlRC_WallPlanRegenNew"),
        ("钢筋工程量", "SetCurrentLabel IDQUANTITYLIST_DETAIL → DtlRC_SSSE（板）/ "
                      "DtlRC_StatBuildingBeamSteelSpecExcel（梁）/ DtlRC_SSCE（柱）/ "
                      "DtlRC_SSWE（墙）"),
        ("★ 顺序约束", "混凝土统计必须在施工图**之前**：切「建模模块」会冲掉施工图上下文，"
                      "之后所有 DtlRC_* 统计命令退化为 OK(0.0s) 且不产出任何文件。"
                      "正确顺序 = 混凝土 → 施工图 → 钢筋。"),
        ("模态框", "StdSlab_batgenstl 会弹「施工图已经进行过选筋,是否重新选筋?」，"
                  "DialogWatch 后台线程回「否」；唯一有效方法是 PostMessageW(WM_COMMAND,IDNO=7)"),
        ("面积口径", "钢筋表的楼面面积按**板伸至梁外皮**计；混凝土体积按**扣除梁占位后的净板面积**计，"
                    "两者口径不同，别混用。"),
    ]:
        put(ws, r0, [k, v], aligns=[LEFT, LEFT], h=None)
        ws.row_dimensions[r0].height = 32
        r0 += 1

    # ---------- 6. 自检 ----------
    ws = wb.create_sheet("6.自检")
    r0 = title(ws, "自检与校核", 3)
    r0 = head(ws, r0, ["校核项", "值 / 依据", "结论"], widths=[28, 56, 20])
    # 逐层混凝土一致性
    if conc:
        zs = [b["小计"] for b in conc["逐层"].values()]
        ok = len(set(round(z, 3) for z in zs)) == 1
        # 各层构件不同在真实工程里正常（裙房/收进），只提示，不判死
        ck_row(ck, "各层混凝土小计是否一致",
               "、".join("%.3f" % z for z in zs),
               "一致" if ok else "! 不一致（各层构件不同？）",
               LEVEL_INFO if ok else LEVEL_WARN)
        same = abs(sum(zs) - conc["合计"]) < 0.01
        ck_row(ck, "混凝土逐层之和 = 全楼合计",
               "%.3f vs %.3f" % (sum(zs), conc["合计"]),
               "通过" if same else "★偏差",
               LEVEL_INFO if same else LEVEL_FAIL)
        # 柱体积手算
        cnt = conc_cnt.get("柱")
        if cnt:
            for it in conc["逐层"][sorted(conc["逐层"])[0]]["明细"]:
                if it["种类"] == "柱":
                    ck_row(ck, "柱体积 = 个数 × b × h × 层高（示意：按 0.7×0.7×4.8）",
                           "%d × 0.7 × 0.7 × 4.8 = %.3f" % (cnt, cnt * 0.49 * 4.8),
                           "与 %.3f 对比" % it["体积"])
                    break
    for kind in ("楼板", "梁", "柱", "墙"):
        if kind in rebar_zero:
            # 表在、值全 0：ini 说这类构件有混凝土量时就属于异常，不是"本工程没有"
            if kind in conc_kinds:
                ck_row(ck, "%s钢筋" % kind, "0（表中无数据）",
                       "★ini 显示本类混凝土 %.3f m3，钢筋表却全为 0"
                       % conc_kinds[kind], LEVEL_FAIL)
            else:
                ck_row(ck, "%s钢筋" % kind, "0（表中无数据）", "本工程无此构件，正常")
        elif kind in rebar:
            n = len([x for x in rebar[kind] if rebar[kind][x] > 0])
            ck_row(ck, "%s钢筋：非零直径档数" % kind, "%d 档" % n,
                   "正常" if n else "★全为 0（统计未生效）",
                   LEVEL_INFO if n else LEVEL_FAIL)
        else:
            note = rebar_note.get(kind, "未读取")
            if kind in conc_kinds:
                ck_row(ck, "%s钢筋" % kind, note,
                       "★ini 显示本类混凝土 %.3f m3，却没有钢筋用量表"
                       % conc_kinds[kind], LEVEL_FAIL)
            elif rebar:
                # 有别的钢筋表、就是没有这一类的，且 ini 也没说这类有混凝土量
                ck_row(ck, "%s钢筋" % kind, note,
                       "本工程无此构件（ini 里也没有该类混凝土量）" if conc
                       else "本工程无此构件（没有 ini 可比对，只据钢筋表判断）")
            else:
                ck_row(ck, "%s钢筋" % kind, note,
                       "★一张钢筋用量表都没有（钢筋统计阶段未生效？）", LEVEL_FAIL)
    if dwgs:
        if dwg_bad:
            lvl, concl = LEVEL_FAIL, "★见下（%d 个不可用）" % len(dwg_bad)
        elif dwg_tiny:
            lvl, concl = LEVEL_WARN, "! 见下（%d 个疑似截断）" % len(dwg_tiny)
        else:
            lvl, concl = LEVEL_INFO, "正常"
        ck_row(ck, "施工图 DWG 数量", "%d 个" % len(dwgs), concl, lvl)
    else:
        ck_row(ck, "施工图 DWG 数量", "0", "★未生成", LEVEL_FAIL)
    for f, size, st in dwg_rows:
        if st.startswith("★"):
            ck_row(ck, "DWG %s" % f,
                   "%s 字节" % (size if size is not None else "-"), st, LEVEL_FAIL)
    for t in dwg_tiny:
        ck_row(ck, "DWG 截断", t, "疑似截断", LEVEL_WARN)
    for k, v, res, _lv in ck:
        put(ws, r0, [k, v, res], aligns=[LEFT, LEFT, CEN])
        r0 += 1

    # ---- 收尾：落盘、复检、按自检结论给退出码 ----
    out = os.path.join(d, "%s_施工图与工程量汇总.xlsx" % name)
    wb.save(out)
    ok_written, why = verify_written(out)
    print("=" * 64)
    print("工程：%s" % name)
    if conc:
        for k, v in conc["按构件种类"].items():
            print("  混凝土 %-6s %10.3f m3" % (k, v))
        print("  混凝土 合计   %10.3f m3" % conc["合计"])
    for k in ("楼板", "梁", "柱", "墙"):
        if k in rebar:
            print("  钢筋   %-6s %10.1f kg" % (k, sum(rebar[k].values())))
    print("  钢筋   合计   %10.1f kg" % tb)
    print("  施工图 DWG %d 个" % len(dwgs))
    print("-> %s" % out)
    # 交付物在磁盘上复检（页数 + 合计行）——save() 返回 None，"调用过 save"不是判据
    print("  写盘复检：%s" % ("通过（%s）" % why if ok_written else "失败：%s" % why))
    hard = [x for x in ck if x[3] == LEVEL_FAIL]
    warns = [x for x in ck if x[3] == LEVEL_WARN]
    if not ok_written:
        hard = hard + [("交付物写盘复检", why, "★交付物不完整", LEVEL_FAIL)]
    print("  自检：硬问题 %d 项，提示 %d 项" % (len(hard), len(warns)))
    for k, v, res, _lv in hard:
        print("   !! %s：%s —— %s" % (k, v, res))
    for k, v, res, _lv in warns:
        print("   ~  %s：%s —— %s" % (k, v, res))
    if hard and not a.allow_incomplete:
        # 交付物已经写出（可交付性不受影响），但结论不可信：退出码必须反映出这一点，
        # 否则"指错目录"与"完整留档"对调用方完全同形（S54）。
        print("!! 自检未通过：交付物已写出，但上面的结论不可信（退出码 2）")
        print("   明知留档不全仍要返回 0：加 --allow-incomplete")
        return 2
    if hard:
        print("!! 自检未通过（--allow-incomplete：本次仍返回 0）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
