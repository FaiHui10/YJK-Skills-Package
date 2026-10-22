# -*- coding: utf-8 -*-
r"""真实工程柱截面选型（模式 B）—— 读现有 YJK 工程的设计结果，按轴压比给出每
(标准层 × 柱位组) 的最小可行柱截面，可选直接产出"截面 + 等级都改好"的可导入 ydb。

为什么要单独一个脚本
--------------------
`section_opt.py`（模式 A）假设**规则柱网**：从 config.json 的 跨数/层数/单一层高 推出
柱位分组（中/边/角柱）。真实工程不满足：柱网不规则、层高逐层不同、混凝土等级按自然层
分区（分区边界还常与标准层边界不重合）。本脚本把这些全部改成**从工程自己读出来**。

算法（与 references/real-project.md 一致）
------------------------------------------
  1) 现状：解析 设计结果\wpj*.out（GBK）→ 每根柱的 截面/材料/短柱标记/Nu/Uc/配筋
  2) 分组：读计算模型库，同一标准层内**截面相同**的柱归为一组；也可 --groups 手工指定
  3) 目标面积（判断轴压比是逐柱局部约束，给定 N 有闭式解）：
         A_req(std,组) = max over 该组所有自然层所有柱 of  |Nu|·1000 / (目标系数 · 限值 · fc)
     限值分短柱/非短柱（框筒二级：非短柱 0.85、短柱 0.80）；fc 取该柱材料对应的设计值。
  4) 竖向单调包络（不出现下小上大）：A(std) = max(A_req(std … 最上层))
  5) 取 50mm 模数、边长 ≥ 最小边长、保持原矩形 b:h 方向，且**不允许比原截面大**
  6) 等级：默认用 wpj 读到的真实等级；给 --grade-map 则按写回口径（保守等价模型）

★ 保守等价模型：`tblStdFlr.Para` 的等级是"标准层"层面的，跨区的标准层只能取本区**偏弱**
  等级，模型因此偏保守（Uc 偏高、位移角偏大）。结论方向安全，但不是原工程的交付替身。
  细节见 references/real-project.md 第二节。

用法
----
  # 只读：出选型表（推荐先跑）
  python real_opt.py --proj <工程目录> [--out sections.json]

  # 生成可导入模型库（截面 + 各标准层等级一起写）
  python real_opt.py --proj <工程目录> --write-ydb out\model.ydb --write-grades

  # 收敛判定（拿上一轮的 sections.json 比）
  python real_opt.py --proj <新工程目录> --compare sections.json

  # 保守等价口径（等级按标准层取偏弱值，与写回模型自洽）
  python real_opt.py --proj <工程目录> --grade-map "1-3:C60,4:C50,5:C45,6-7:C40"

依赖：无（只用标准库）。`--write-ydb` 需要 yjk-colmodel 技能的 scripts/yjkio.py。
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sqlite3
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

FC_DEFAULT = {"C25": 11.9, "C30": 14.3, "C35": 16.7, "C40": 19.1, "C45": 21.1,
              "C50": 23.1, "C55": 25.3, "C60": 27.5}
GRADE_CODE = {g: int(g[1:]) for g in FC_DEFAULT}

RE_HEAD = re.compile(r"N-C=(\d+)\s*\(I=\d+,\s*J=\d+\)\s*\((\d+)\)")
RE_GEO = re.compile(r"B\*H\(mm\)=\s*([\d.]+)\*([\d.]+)")
RE_UC = re.compile(r"\(\s*(\d+)\s*\)\s*Nu=\s*(-?[\d.]+)\s+Uc=\s*([\d.]+)")
RE_FACE = re.compile(r"(As[xy][tyb]=)\s*(\d+)")
RE_MAT = re.compile(r"砼柱\s+(C\d+)")
RE_LAM = re.compile(r"λc=\s*([\d.]+)")


def log(msg: str) -> None:
    print(msg, flush=True)


# ---------------------------------------------------------------- 读设计结果
def resolve_res_dir(proj_or_res: str) -> str:
    if os.path.basename(os.path.normpath(proj_or_res)) == "设计结果":
        return proj_or_res
    return os.path.join(proj_or_res, "设计结果")


def parse_wpj(res_dir: str) -> list:
    """解析 wpj*.out → 每自然层每柱一条记录。"""
    rows = []
    for n in range(1, 60):
        p = os.path.join(res_dir, "wpj%d.out" % n)
        if not os.path.exists(p):
            continue
        txt = open(p, "rb").read().decode("gbk", "replace")
        h = re.search(r"第\s*(\d+)\s*层\(标准层\s*(\d+)", txt)
        if not h:
            continue
        nat, std = int(h.group(1)), int(h.group(2))
        marks = [m.start() for m in re.finditer(r"N-C=", txt)]
        for a, b in zip(marks, marks[1:] + [len(txt)]):
            blk = txt[a:b]
            m, g, u = RE_HEAD.match(blk), RE_GEO.search(blk), RE_UC.findall(blk)
            if not (m and g and u):
                continue
            best = max(u, key=lambda x: float(x[2]))
            ast = 0
            for line in blk.splitlines():
                if re.match(r"^\s*\(\s*\d+\s*\)N=", line):
                    f = RE_FACE.findall(line)
                    if f:
                        ast = max(ast, sum(int(v) for _, v in f))
            mt = RE_MAT.search(blk)
            lam = [float(x) for x in RE_LAM.findall(blk)]
            rows.append({
                "自然层": nat, "标准层": std, "柱号": int(m.group(1)),
                "b": float(g.group(1)), "h": float(g.group(2)),
                "Nu": float(best[1]), "Uc": float(best[2]),
                "材料": mt.group(1) if mt else None,
                "短柱": ("短柱" in blk),
                "λc": min(lam) if lam else None,
                "As": ast,
                "超限": ("轴压比超限" in blk),
            })
    return rows


def parse_wmass_grades(res_dir: str) -> dict:
    """{自然层: 柱混凝土等级} —— 从 wmass.out 的「混凝土构件」小节读（真值）。"""
    p = os.path.join(res_dir, "wmass.out")
    if not os.path.exists(p):
        return {}
    txt = open(p, "rb").read().decode("gbk", "replace")
    out = {}
    started = False
    for ln in txt.splitlines():
        if "混凝土构件：" in ln:
            started = True
            continue
        if not started:
            continue
        if "型钢混凝土构件" in ln or "箍筋（墙分布筋）" in ln:
            break
        m = re.match(r"\s*(\d+)\s+\d+\s+\d+\((.+?)\)\s+\d+\((.+?)\)", ln)
        if m:
            nat, _, col = int(m.group(1)), m.group(2), m.group(3)
            mm = re.search(r"(C\d+)", col)
            if mm:
                out[nat] = mm.group(1)
    return out


# ---------------------------------------------------------------- 模型库
def find_model_db(proj_dir: str):
    """找计算模型库：优先 <工程名>.ymd，再任意含 tblColSect 的 .ymd，最后 施工图\\dtlmodel.ydb。"""
    cands = []
    name = os.path.basename(os.path.normpath(proj_dir))
    for f in sorted(os.listdir(proj_dir)):
        if f.lower().endswith(".ymd"):
            cands.append(os.path.join(proj_dir, f))
    cands.sort(key=lambda p: 0 if os.path.basename(p)[:-4] == name else 1)
    dtl = os.path.join(proj_dir, "施工图", "dtlmodel.ydb")
    if os.path.exists(dtl):
        cands.append(dtl)
    for p in cands:
        if not os.path.exists(p):
            continue
        try:
            con = _ro(p)
            has = con.execute("SELECT 1 FROM sqlite_master WHERE type='table' "
                              "AND name='tblColSect'").fetchone()
            nseg = con.execute("SELECT COUNT(*) FROM tblColSeg").fetchone()[0] if has else 0
            con.close()
            if has and nseg:
                return p
        except sqlite3.Error:
            continue
    return None


def _ro(path: str):
    return sqlite3.connect("file:%s?mode=ro" % path.replace("\\", "/"), uri=True)


def groups_from_db(db: str, verbose=True) -> dict:
    """同一标准层内截面相同的柱归一组。返回 {组名: [柱号…]}（取分组最细的那个标准层为基准）。"""
    con = _ro(db)
    sf = {r[0]: r[1] for r in con.execute("SELECT No_,ID FROM tblStdFlr")}
    inv = {v: k for k, v in sf.items()}
    per = {}
    for nc, sid, sect in con.execute("SELECT No_,StdFlrID,SectID FROM tblColSeg ORDER BY No_"):
        per.setdefault(inv.get(sid, sid), {}).setdefault(sect, []).append(nc)
    heights = {}
    for sid, h in con.execute("SELECT StdFlrID,Height FROM tblFloor"):
        heights[sid] = heights.get(sid, 0.0) + (h or 0) / 1000.0
    con.close()

    pattern = {std: frozenset(frozenset(v) for v in d.values()) for std, d in per.items()}
    ref = max(per, key=lambda s: len(per[s]))
    groups, i = {}, 0
    for sect, ncs in sorted(per[ref].items(), key=lambda kv: min(kv[1])):
        i += 1
        groups["G%d" % i] = sorted(ncs)
    if verbose and len(set(pattern.values())) > 1:
        log("!! 注意：各标准层的截面分组不一致，已按标准层 %s 的分组为基准：" % ref)
        for std in sorted(pattern):
            if pattern[std] != pattern[ref]:
                log("     标准层%s 的分组 = %s" % (std, [sorted(v) for v in pattern[std]]))
    return groups, heights


def groups_from_rows(rows: list) -> dict:
    """兜底：拿不到模型库时，按"同标准层内截面相同"从 wpj 结果里分组。"""
    std = sorted({r["标准层"] for r in rows})[0]
    seen, groups, i = {}, {}, 0
    for r in rows:
        if r["标准层"] != std:
            continue
        k = (r["b"], r["h"])
        if k not in seen:
            i += 1
            seen[k] = "G%d" % i
        groups.setdefault(seen[k], []).append(r["柱号"])
    for v in groups.values():
        v.sort()
    return groups


# ---------------------------------------------------------------- 选型
def parse_grade_map(s: str) -> dict:
    """'1-3:C60,4:C50,6-7:C40' → {1:'C60',2:'C60',3:'C60',4:'C50',6:'C40',7:'C40'}"""
    out = {}
    for item in (s or "").split(","):
        item = item.strip()
        if not item:
            continue
        key, _, grade = item.partition(":")
        grade = grade.strip().upper()
        if not grade:
            raise SystemExit("--grade-map 格式应为 1-3:C60,4:C50，收到 %r" % item)
        for part in key.split("+"):
            if "-" in part:
                a, b = part.split("-", 1)
                for i in range(int(a), int(b) + 1):
                    out[i] = grade
            else:
                out[int(part)] = grade
    return out


def lim_of(row, args):
    return args.limit_short if row["短柱"] else args.limit_normal


def fc_of(grade):
    return FC_DEFAULT.get((grade or "").upper(), 14.3)


def fit_section(b0, h0, a_need, side_min, step):
    """按面积需求缩放 b×h（保持方向），取模数；不小于 side_min，且**不允许比原截面大**。"""
    if a_need >= b0 * h0:
        return b0, h0
    k = (a_need / (b0 * h0)) ** 0.5
    b2 = max(side_min, int(round(b0 * k / step)) * step)
    h2 = max(side_min, int(round(h0 * k / step)) * step)
    while b2 * h2 < a_need:
        if b2 <= h2:
            b2 += step
        else:
            h2 += step
    if b2 * h2 > b0 * h0:                     # 模数上取可能反而变大 → 保持原截面
        return b0, h0
    return b2, h2


def select(rows, groups, args, grade_of_std=None):
    """返回 (plan, detail)。plan={(std,组):(b,h)}，detail=[每行 (std,组,控制行,新b,新h,新Uc)]"""
    stds = sorted({r["标准层"] for r in rows})
    ctrl, a_req = {}, {}
    for std in stds:
        for gname, ncs in groups.items():
            sub = [r for r in rows if r["标准层"] == std and r["柱号"] in ncs]
            if not sub:
                continue
            c = max(sub, key=lambda r: r["Uc"])
            ctrl[(std, gname)] = c
            a = 0.0
            for r in sub:
                g = (grade_of_std or {}).get(std) or r["材料"]
                a = max(a, abs(r["Nu"]) * 1000.0 / (args.target * lim_of(r, args) * fc_of(g)))
            a_req[(std, gname)] = a

    plan, detail = {}, []
    for gname in groups:
        am, env = 0.0, {}
        for std in reversed(stds):                     # 竖向单调包络：上不大于下
            am = max(am, a_req.get((std, gname), 0.0))
            env[std] = am
        for std in stds:
            key = (std, gname)
            if key not in ctrl:
                continue
            c = ctrl[key]
            b2, h2 = fit_section(c["b"], c["h"], env[std], args.side_min, args.step)
            plan[key] = (b2, h2)
            g = (grade_of_std or {}).get(std) or c["材料"]
            detail.append((std, gname, c, b2, h2,
                           abs(c["Nu"]) * 1000.0 / (fc_of(g) * b2 * h2)))
    return plan, detail


# ---------------------------------------------------------------- 写模型库
def find_yjkio():
    cands = []
    if os.environ.get("YJK_COLMODEL_DIR"):
        cands.append(os.environ["YJK_COLMODEL_DIR"])
    cands.append(os.path.join(os.path.dirname(os.path.dirname(HERE)), "yjk-colmodel"))
    home = os.path.expanduser("~")
    for d in (".trae-cn", ".trae"):
        cands.append(os.path.join(home, d, "skills", "yjk-colmodel"))
    for c in cands:
        for sub in ("scripts", ""):
            p = os.path.join(c, sub) if sub else c
            if os.path.exists(os.path.join(p, "yjkio.py")):
                return p
    return None


def write_grades(path, grade_of_std, verbose=True):
    """把各标准层的等级写进 tblStdFlr.Para(idx4=柱, idx6=墙) 与 tblStdFlrPara(Kind 4/6)。"""
    con = sqlite3.connect(path)
    sf = {r[0]: r[1] for r in con.execute("SELECT No_,ID FROM tblStdFlr")}
    done = []
    for std, sid in sorted(sf.items()):
        g = (grade_of_std or {}).get(std)
        if not g:
            continue
        v = GRADE_CODE.get(g.upper())
        if v is None:
            raise SystemExit("未知等级 %r（可选：%s）" % (g, sorted(GRADE_CODE)))
        row = con.execute("SELECT Para FROM tblStdFlr WHERE ID=?", (sid,)).fetchone()
        parts = (row[0] or "").split(",")
        if len(parts) > 6:
            parts[4] = str(v)                     # 柱
            parts[6] = str(v)                     # 墙
            con.execute("UPDATE tblStdFlr SET Para=? WHERE ID=?", (",".join(parts), sid))
        for kind in (4, 6):
            con.execute("UPDATE tblStdFlrPara SET ParaVal=? WHERE StdFlrID=? AND Kind=?",
                        (v, sid, kind))
        done.append((std, g))
    con.commit()
    ok = con.execute("PRAGMA integrity_check").fetchone()[0]
    con.close()
    if verbose:
        log("  已写等级: %s   integrity_check=%s"
            % (" ".join("标准层%d=%s" % (s, g) for s, g in done), ok))
    return done


def write_ydb(base, out, groups, plan, grade_of_std=None, do_grades=True):
    yk = find_yjkio()
    if not yk:
        raise SystemExit("未找到 yjk-colmodel/scripts/yjkio.py —— 设 YJK_COLMODEL_DIR，"
                         "或把 yjk-colmodel 技能装在默认 skills 目录下")
    sys.path.insert(0, yk)
    import yjkio as K

    _orig = K.geo_to_row_fields
    def patched(geo):
        if geo.get("kind") == 1:                  # ★ 矩形柱：b、h 分别写，别退化成方形
            f = {k: 0.0 for k in ("b", "h", "u", "t", "d", "f", "l", "p")}
            f["b"], f["h"] = geo["b"], geo["h"]
            return f
        return _orig(geo)
    K.geo_to_row_fields = patched

    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    shutil.copy2(base, out)
    changes = {}
    for (std, gname), (b, h) in plan.items():
        changes.setdefault(str(std), []).append({"cols": groups[gname], "b": b, "h": h})
    rep = K.apply_to_db(out, changes, do_write=True)
    log("  写截面: 新增 %d 个 / 复用 %d 个 / 改动柱段 %d / 缺失 %d"
        % (len(rep["created"]), len(rep["reused"]), rep["segments"], len(rep["missing"])))
    if rep.get("integrity") not in (None, "ok"):
        raise SystemExit("!! ydb 写入后 integrity_check=%s" % rep.get("integrity"))
    if do_grades and grade_of_std:
        write_grades(out, grade_of_std)
    log("  已生成: %s (%d B)" % (out, os.path.getsize(out)))
    return rep


# ---------------------------------------------------------------- 主流程
def _utf8_console():
    """非 GBK 控制台下输出不崩（库调用与 CLI 都适用）。"""
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(errors="replace")
        except Exception:                                      # noqa: BLE001
            pass


def main(argv=None) -> int:
    _utf8_console()
    ap = argparse.ArgumentParser(description="真实工程柱截面选型（模式 B）")
    ap.add_argument("--proj", required=True, help="工程目录（或 设计结果 目录）")
    ap.add_argument("--out", help="选型结果写到哪里（sections.json）")
    ap.add_argument("--compare", help="与上一轮的 sections.json 比较（收敛判定）")
    ap.add_argument("--limit-short", type=float, default=0.80, help="短柱轴压比限值")
    ap.add_argument("--limit-normal", type=float, default=0.85, help="非短柱轴压比限值")
    ap.add_argument("--target", type=float, default=0.95, help="目标利用率系数（×限值）")
    ap.add_argument("--side-min", type=int, default=400, help="最小边长 mm")
    ap.add_argument("--step", type=int, default=50, help="边长模数 mm")
    ap.add_argument("--groups", help="手工分组 json：{\"上长边\":[1,2,3,4], ...}")
    ap.add_argument("--grade-map", help="写回口径的等级分区，如 1-3:C60,4:C50,5:C45,6-7:C40")
    ap.add_argument("--write-ydb", help="生成可导入的模型库（截面 + 等级）")
    ap.add_argument("--base-ydb", help="--write-ydb 的基准库（默认 施工图\\dtlmodel.ydb 或 <工程名>.ymd）")
    ap.add_argument("--write-grades", action="store_true", help="同时写各标准层等级（见 --grade-map）")
    ap.add_argument("--quantities", action="store_true", help="附带打印 混凝土/模板/纵筋 量差")
    a = ap.parse_args(argv)

    proj = os.path.normpath(a.proj)
    res = resolve_res_dir(proj)
    rows = parse_wpj(res)
    if not rows:
        raise SystemExit("没解析到柱结果，确认 %s 下有 wpj*.out" % res)
    stds = sorted({r["标准层"] for r in rows})
    log("工程 %s" % proj)
    log("解析到 %d 条柱记录（%d 自然层 × %d 柱 × %d 标准层）；超限记录 %d 条"
        % (len(rows), len({r["自然层"] for r in rows}), len({r["柱号"] for r in rows}),
           len(stds), sum(1 for r in rows if r["超限"])))

    # 分组
    if a.groups:
        groups = json.load(open(a.groups, encoding="utf-8"))
        db = None
    else:
        db = find_model_db(proj)
        if db:
            groups, _ = groups_from_db(db)
            log("分组（按模型库 %s 里「同标准层内截面相同」自动归并）：%s"
                % (os.path.basename(db), {k: v for k, v in groups.items()}))
        else:
            groups = groups_from_rows(rows)
            log("!! 未找到计算模型库，分组退化为「按 wpj 结果里截面相同」：%s" % groups)

    # 等级口径
    true_grades = parse_wmass_grades(res)
    gmap = parse_grade_map(a.grade_map) if a.grade_map else None
    if gmap:
        grade_of_std = {s: gmap[s] for s in stds if s in gmap}
        log("等级口径：--grade-map 指定（写回模型的保守等价口径）")
    else:
        grade_of_std = {}
        for std in stds:
            gs = [true_grades.get(r["自然层"]) or r["材料"] for r in rows if r["标准层"] == std]
            gs = [g for g in gs if g]
            if gs:                                  # 取该标准层内**最弱**等级（保守）
                grade_of_std[std] = sorted(gs, key=lambda g: FC_DEFAULT.get(g, 0))[0]
        log("等级口径：从结果读出（各标准层取最弱等级，保守）")

    plan, detail = select(rows, groups, a, grade_of_std)

    # ---- 出表 ----
    log("")
    log("目标利用率 %.3f（限值 短柱 %.2f / 非短柱 %.2f）｜边长 %d~模数 %d｜最小 %d"
        % (a.target, a.limit_short, a.limit_normal, a.step, a.step, a.side_min))
    log("%-5s %-6s %-5s %-11s %-11s %-8s %-8s %-7s %s"
        % ("标准层", "组", "柱数", "原截面", "建议截面", "原Uc", "新Uc", "限值", "判定"))
    bad = tight = 0
    for std, gname, c, b2, h2, uc2 in detail:
        lim = lim_of(c, a)
        same = (b2, h2) == (c["b"], c["h"])
        if uc2 <= lim + 1e-9:
            tag, mark = "OK", ""
        elif same:
            # 本脚本只缩不放：原截面在该等级口径下已不满足目标 → 报出来，别装成 OK
            tag, mark = "保持(原截面不足)", "  <-- 需放大截面或调整等级口径"
            tight += 1
        else:
            tag, mark = "!!超限", ""
            bad += 1
        log("%-5d %-6s %-5d %-11s %-11s %-8.3f %-8.3f %-7.2f %s%s%s"
            % (std, gname, len(groups[gname]), "%g×%g" % (c["b"], c["h"]),
               "%g×%g" % (b2, h2), c["Uc"], uc2, lim, tag,
               "   (短柱)" if c["短柱"] else "", mark))
    log("超限残留 = %d；保持但已超目标 = %d（本脚本只缩不放，这两类需放大截面或调整等级口径）"
        % (bad, tight))

    # ---- 收敛判定 ----
    changed = None
    if a.compare:
        old = json.load(open(a.compare, encoding="utf-8"))
        old = old.get("sections", old)
        cur = {str(std): {g: list(plan[(std, g)]) for g in groups if (std, g) in plan}
               for std in stds}
        diff = [(s, g, old.get(s, {}).get(g), cur[s][g])
                for s in cur for g in cur[s] if old.get(s, {}).get(g) != cur[s][g]]
        if diff:
            log("\n与 %s 相比建议改动 %d 处：" % (a.compare, len(diff)))
            for s, g, o, n in diff:
                log("   标准层%-3s %-6s %s -> %s"
                    % (s, g, o and "%d×%d" % tuple(o), "%d×%d" % tuple(n)))
        else:
            log("\n与 %s 相比：无改动 —— 已收敛（当前方案即本模型下的最优）" % a.compare)
        changed = len(diff)

    # ---- 量差 ----
    if a.quantities:
        db = db or find_model_db(proj)
        if db:
            con = _ro(db)
            sf = {r[0]: r[1] for r in con.execute("SELECT No_,ID FROM tblStdFlr")}
            tot = {}
            for sid, h in con.execute("SELECT StdFlrID,Height FROM tblFloor"):
                tot[sid] = tot.get(sid, 0.0) + (h or 0) / 1000.0
            con.close()
            vo = vn = fo = fn = so = sn = 0.0
            for std, gname, c, b2, h2, _ in detail:
                H = tot.get(sf.get(std), 0.0)
                n = len(groups[gname])
                vo += c["b"] * c["h"] / 1e6 * H * n
                vn += b2 * h2 / 1e6 * H * n
                fo += 2 * (c["b"] + c["h"]) / 1000 * H * n
                fn += 2 * (b2 + h2) / 1000 * H * n
                so += max(c["As"], 0.006 * c["b"] * c["h"]) / 1e6 * H * n
                sn += max(c["As"], 0.006 * b2 * h2) / 1e6 * H * n
            log("\n量差（柱构件）：混凝土 %.1f -> %.1f m³ (%+.1f%%)｜模板 %.0f -> %.0f m² (%+.1f%%)"
                "｜纵筋 %.1f -> %.1f t (%+.1f%%)"
                % (vo, vn, (vn / vo - 1) * 100, fo, fn, (fn / fo - 1) * 100,
                   so * 7.85, sn * 7.85, (sn / so - 1) * 100))
        else:
            log("!! 没有模型库，无法算量差")

    # ---- 写出 ----
    if a.out:
        obj = {
            "工程": proj,
            "限值": {"短柱": a.limit_short, "非短柱": a.limit_normal,
                     "目标系数": a.target, "最小边长": a.side_min, "步长": a.step},
            "分组": groups,
            "等级": {str(k): v for k, v in sorted(grade_of_std.items())},
            "sections": {str(std): {g: list(plan[(std, g)]) for g in groups if (std, g) in plan}
                         for std in stds},
        }
        os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
        json.dump(obj, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        log("\n已写出 -> %s" % a.out)

    # ---- 写 ydb ----
    if a.write_ydb:
        base = a.base_ydb or find_model_db(proj)
        if not base:
            raise SystemExit("找不到基准库，请用 --base-ydb 指定")
        log("\n写模型库（基准 %s）：" % base)
        write_ydb(base, a.write_ydb, groups, plan,
                  grade_of_std=grade_of_std if (a.write_grades or gmap) else None,
                  do_grades=(a.write_grades or bool(gmap)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
