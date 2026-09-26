# -*- coding: utf-8 -*-
r"""解析 YJK `设计结果/wpj<N>.out`（梁、柱配筋设计结果）。

文件格式（GBK 编码）：
  梁:  `N-B=1 (I=1000001, J=1000006)(1)B*H(mm)=300*800`
       `Lb=8.40(m) Cover= 20(mm) Nfb=2 ... Rcb=30.0 Fy=360 Fyv=360`
       九截面表：-M/LoadCase/Top Ast/% Steel，+M/…/Btm Ast，V/…/Asv/Rsv
  柱:  `N-C=1  (I=1000001, J=1)(1)B*H(mm)=700*700`
       `Cover= 20(mm) Cx=1.00 Cy=1.00 Lcx=4.80(m) Lcy=4.80(m) ... Rcc=40.0`
       `( 30)Nu= -1264.7 Uc= 0.14 Rs= 0.85(%) Rsv= 0.60(%) Asc= 254`
       `(  1)N= ... Asxt= 1295 Asxt0= 0`  ×4（Asxt/Asyt/Asxb/Asyb）
       `( 28)N= ... Asvx= 190 ...` / `Asvy`

单位：Ast/Asv 为 mm2；Lb 为 m；Uc 为轴压比；Rs/Rsv 为 %。

口径提醒（柱）—— 别把「柱段」当「柱根」
--------------------------------------
`N-C=k` 是**柱段**编号，不是柱根编号。实测（Core28，`YJK_run4\设计结果`）：

    wpj1.out  32 个 N-C（首层）   —— 首层层高 4500 ≠ 标准层 3600，
                                     每根柱被 YJK 拆成**两个高度段**，编号连续 2k-1/2k：
                                     N-C=1 (I=1000001,J=1000025) 与
                                     N-C=2 (I=1000025,J=1) 是同一根柱的上下两段
    wpj2.out  16 个 N-C（标准层） —— 每根柱一段

于是首层"柱数"是 2 × 每标准层柱数（32 vs 16），照字面读会以为首层柱是多了一倍。
所以本文件同时给出两个数：
    * **柱段数** = `N-C` 编号个数（YJK 报的就是这个）
    * **柱根数** = 按柱段端点（I/J 节点号）连通归并出的根数
只在**同一层内**归并，不改变任何解析结果（`parse()` 一个字节没动）。
"""
import collections
import os
import re
import sys

RE_BEAM = re.compile(
    r"N-B=(\d+)\s*\(I=(-?\d+),\s*J=(-?\d+)\)\s*\(\d+\)B\*H\(mm\)=(\d+)\*(\d+)")
RE_BEAM_L = re.compile(
    r"Lb=([\d.]+)\(m\)\s+Cover=\s*(\d+)\(mm\).*?Rcb=([\d.]+)")
RE_COL = re.compile(
    r"N-C=(\d+)\s*\(I=(-?\d+),\s*J=(-?\d+)\)\s*\(\d+\)B\*H\(mm\)=(\d+)\*(\d+)")
RE_COL_L = re.compile(
    r"Cover=\s*(\d+)\(mm\)\s+Cx=([\d.-]+)\s+Cy=([\d.-]+)\s+Lcx=([\d.]+)\(m\)"
    r"\s+Lcy=([\d.]+)\(m\).*?Rcc=([\d.]+)")
RE_COL_U = re.compile(
    r"\(\s*\d+\)\s*Nu=\s*(-?[\d.]+)\s+Uc=\s*([\d.]+)\s+Rs=\s*([\d.]+)\(%\)"
    r"\s+Rsv=\s*([\d.]+)\(%\)\s+Asc=\s*(-?[\d.]+)")
RE_NUM9 = re.compile(r"([\d.-]+)")


def _nums(line, n=9):
    """从一行里取 n 个数字（跳过 LoadCase 那种括号行）。"""
    vals = [float(v) for v in RE_NUM9.findall(line)]
    return (vals + [0.0] * n)[:n]


def parse(path):
    """解析 wpj 文件 -> {"beams": [...], "cols": [...], "stats": {...}}。

    ★ `stats` 记的是**解析覆盖率**，用来把"没有数据"与"数值为 0"分开：
      `柱模式` / `柱丢弃`（有 N-C 行但取不到 Uc 控制组合行）、
      `梁模式` / `梁无Lb`、`抓取未命中`（九截面表 / -M / +M / V 一条都没匹配上的梁数）。
      老版本把这些"没匹配上"直接变成空列表 / 0.0 输出（整根柱被静默丢弃、
      梁钢筋合计 0.0 kg），与"真的没有"不可区分。
    """
    try:
        with open(path, "rb") as fh:
            t = fh.read().decode("gbk", errors="replace")
    except OSError as e:
        # 用户给的输入路径：读不出来要给可读报错，不能抛裸 traceback
        raise SystemExit("读不动这个文件（%s）：%s\n"
                         "  怎么办：确认路径、权限，以及它是不是被别的程序占着。" % (e, path))
    beams, cols = [], []
    n_col_pat = n_beam_pat = 0
    col_no_uc = 0                 # 有 N-C 行但没有 Uc 控制组合行（格式变了/文件被截断）
    beam_no_lb = 0                # 有 N-B 行但取不到 Lb 行
    grab_miss = {}                # 标签 -> 未匹配上的梁数

    # ---------- 柱 ----------
    for m in RE_COL.finditer(t):
        n_col_pat += 1
        seg = t[m.start():m.start() + 2600]
        hm = RE_COL_L.search(seg)
        um = RE_COL_U.search(seg)
        c = {"No": int(m.group(1)), "I": int(m.group(2)), "J": int(m.group(3)),
             "B": int(m.group(4)), "H": int(m.group(5))}
        if hm:
            c.update(cover=int(hm.group(1)), Cx=float(hm.group(2)),
                     Cy=float(hm.group(3)), Lcx=float(hm.group(4)),
                     Lcy=float(hm.group(5)), Rcc=float(hm.group(6)))
        if um:
            c.update(Nu=float(um.group(1)), Uc=float(um.group(2)),
                     Rs=float(um.group(3)), Rsv=float(um.group(4)),
                     Asc=float(um.group(5)))
        for key in ("Asxt", "Asyt", "Asxb", "Asyb", "Asvx", "Asvy"):
            mm = re.search(key + r"=\s*([\d.-]+)", seg)
            c[key] = float(mm.group(1)) if mm else 0.0
        if c.get("Uc") is not None:
            cols.append(c)
        else:
            col_no_uc += 1

    # ---------- 梁 ----------
    for m in RE_BEAM.finditer(t):
        n_beam_pat += 1
        seg = t[m.start():m.start() + 3200]
        lm = RE_BEAM_L.search(seg)
        b = {"No": int(m.group(1)), "I": int(m.group(2)), "J": int(m.group(3)),
             "B": int(m.group(4)), "H": int(m.group(5))}
        if lm:
            b.update(Lb=float(lm.group(1)), cover=int(lm.group(2)),
                     Rcb=float(lm.group(3)))
        else:
            b["Lb"] = 0.0
            beam_no_lb += 1
        # 砼梁 C30 框架梁 …  → 抗震等级 Nfb
        mm = re.search(r"砼梁\s+C(\d+)", seg)
        if mm:
            b["grade"] = int(mm.group(1))
        mm = re.search(r"Nfb=(\d+)", seg)
        if mm:
            b["Nfb"] = int(mm.group(1))
        b["is_frame"] = "框架梁" in seg[:400]

        def grab(tag):
            r = re.search(r"^\s*" + tag + r"\s+([-\d.\s]+)$", seg, re.M)
            if r is None:
                grab_miss[tag] = grab_miss.get(tag, 0) + 1
                return [0.0] * 9
            return _nums(r.group(1))

        b["TopAst"] = grab(r"Top Ast")
        b["BtmAst"] = grab(r"Btm Ast")
        b["Asv"] = grab(r"Asv")
        b["Rsv"] = grab(r"Rsv")
        b["Mneg"] = grab(r"-M\(kNm\)")
        b["Mpos"] = grab(r"\+M\(kNm\)")
        b["V"] = grab(r"V\(kN\)")
        beams.append(b)

    stats = {"柱模式": n_col_pat, "柱丢弃": col_no_uc,
             "梁模式": n_beam_pat, "梁无Lb": beam_no_lb,
             "抓取未命中": grab_miss}

    # ★ 下限守卫：模式匹配到了却一条都没留下 = 格式变了或文件被截断，
    #   绝不是"这个模型没有柱/梁"。老版本会让它走到输出端变成
    #   「柱段数 0 柱根数 0 / 每根柱 1 段…（0）/ 梁钢筋合计 0.0 kg」并返回 0。
    if n_col_pat and not cols:
        raise SystemExit(
            "解析不出任何柱段：文件里有 %d 个 N-C= 柱段行，却没有一行能取到 Uc 控制组合行"
            "（`( 30)Nu= … Uc= … Rs= …`）。\n"
            "  文件：%s\n"
            "  这通常意味着文件被截断、或该行格式与解析规则不符 —— "
            "两种情况下输出的柱指标都会是 0，别拿它当结果。" % (n_col_pat, path))
    if n_beam_pat and not beams:
        raise SystemExit("解析不出任何梁：文件里有 %d 个 N-B= 梁行，但都没有解析成功：%s"
                         % (n_beam_pat, path))
    if not n_col_pat and not n_beam_pat:
        raise SystemExit(
            "文件里既没有 N-B= 梁行也没有 N-C= 柱行：%s\n"
            "  本脚本解析 YJK 工程「设计结果」目录下的 `wpj<N>.out`（注意扩展名是 .out，"
            "不是 .wpj），先确认文件是不是拿错了。" % path)
    if not beams and not cols:
        raise SystemExit("没解析出任何梁/柱配筋数据：%s" % path)

    return {"beams": beams, "cols": cols, "stats": stats}


def col_chain_stats(cols):
    """柱计数口径：把**柱段**归并成**柱根**（只读 I/J，不改解析逻辑）。

    ★ 为什么需要它（实测误导）：`wpj1.out` 报 32 根柱（`N-C=1..32`，无重号），
      而模型每个标准层恒为 16 根柱段。根因已查明：该工程**首层层高 4500 ≠
      标准层 3600**，YJK 把首层每根柱拆成两个高度段，编号连续 2k-1/2k：
        N-C=1 (I=1000001, J=1000025) + N-C=2 (I=1000025, J=1)  = 同一根柱的上下段
      其余 27 层各 16 段（`wpj2.out` = 16）。所以 32 是「柱段」数，
      字面当成「柱根」会以为首层柱多了一倍。

    归并方法：同一根柱的各段首尾相接，段端点都是全局节点号
    => 以节点号为顶点、每段连一条边，**连通分量个数 = 柱根数**。

    返回 {"段数": int, "根数": int, "每根段数": {段数: 根数}}。
    """
    parent = {}

    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]          # 路径压缩
            x = parent[x]
        return x

    for c in cols:
        a, b = find(c["I"]), find(c["J"])
        if a != b:
            parent[a] = b

    per_root = collections.Counter(find(c["I"]) for c in cols)
    return {"段数": len(cols), "根数": len(per_root),
            "每根段数": dict(sorted(collections.Counter(per_root.values()).items()))}


def _ast_len(vals, L):
    """Σ(相邻截面均值 × 段长) —— 相邻截面之间线性插值积分，单位 mm2·m。"""
    if len(vals) < 2 or L <= 0:
        return 0.0
    n = len(vals) - 1
    dl = L / n
    return sum((vals[i] + vals[i + 1]) / 2.0 * dl for i in range(n))


def rebar_kg(one, steel=7850.0):
    """按「配筋面积法」估钢筋重量(kg)：体积 = 面积(mm2)×1e-6 × 长度(m)。

    纵筋：Top/Btm 各 9 截面线性插值积分。
    箍筋：Asv(mm2) 是**单肢**面积口径的截面含箍量 —— 这里用 Asv 的最大值
          沿全长计（保守且与各方案同口径，比较公平）。
    """
    L = one.get("Lb", 0.0)
    a_long = _ast_len(one["TopAst"], L) + _ast_len(one["BtmAst"], L)
    av = max(one["Asv"]) if one["Asv"] else 0.0
    a_stir = av * L * 2.0            # 双肢箍，按双肢计
    return (a_long + a_stir) * 1e-6 * steel, a_long, a_stir


def _parse_coverage_note(st, path):
    """把解析覆盖率变成**显式问题**：非空即说明下面的数字被低估了。

    这几条都是"模式匹配到了、但没解析出来"的情形 —— 老版本一律静默转成 0
    （梁无 Lb -> 0，九截面表抓不到 -> 全 0），输出的「梁钢筋合计 0.0 kg」
    与"这批梁真的没配筋"完全同形。
    """
    prob = []
    if st.get("柱丢弃"):
        prob.append("%s：有 %d 个 N-C= 柱段行没取到 Uc 控制组合行，这些柱段已被丢弃"
                    % (os.path.basename(path), st["柱丢弃"]))
    if st.get("梁无Lb"):
        prob.append("%s：有 %d 根梁没取到 Lb= 行（长度按 0 计，梁钢筋合计会偏小）"
                    % (os.path.basename(path), st["梁无Lb"]))
    miss = st.get("抓取未命中") or {}
    if miss:
        prob.append("%s：九截面表未命中的标签 %s（对应项按 0 计，合计偏小）"
                    % (os.path.basename(path),
                       "、".join("%s x%d" % (k, v) for k, v in sorted(miss.items()))))
    return prob


def _utf8_console():
    """让输出在任何控制台编码下都不崩（GBK 下把不可编码字符替换掉）。

    为什么需要：打印的是**用户给的**文件名（可能含 cp936 编不出的字符）；
    GBK 控制台下 `print` 抛 UnicodeEncodeError 会**以退出码 1 中断**。
    ★ 只在 CLI 入口调用，**不在 import 时改 stdout**（本模块会被当库 import 用）。
    """
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass


def main(argv=None):
    _utf8_console()
    # ★ 无参 / --help 要给人看用法，**不能把 `--help` 当成文件名去打开**。
    #   不这么写的话 `parse_wpj.py --help` 会走到 parse() 里报「找不到文件 --help」
    #   并以退出码 1 结束 —— 用户想看帮助，却得到一个错误。
    #   （GBK 全包扫振时抓到的：本脚本是唯一一个 `--help` 返回非 0 的入口。）
    args = list(sys.argv[1:] if argv is None else argv)
    if not args or any(a in ("-h", "--help") for a in args):
        print("用法：python parse_wpj.py <wpj1.out> [wpj2.out ...]")
        print()
        print("解析 YJK 的 wpj*.out（构件设计结果），报「梁数 / 柱段数 / 柱根数」"
              "与梁钢筋合计。")
        print()
        print("★ 文件扩展名：工程「设计结果」目录里的真实文件名是 `wpj<N>.out`，"
              "不是 `wpj<N>.wpj`。")
        print("★ 柱计数口径：YJK 报的 N-C 是**柱段**数；首层层高与标准层不同时，"
              "每根柱会被拆成 2 段")
        print("  （编号连续 2k-1 / 2k），所以首层的柱段数 ≈ 2 x 每标准层柱数。"
              "本脚本同时给出「柱段数」")
        print("  与「柱根数」（按柱段端点连通归并），引用时请写清是哪一个。")
        return 0
    problems = []
    for p in args:
        # ★ 文件不存在时给可读错误，不要抛裸 FileNotFoundError traceback
        #   （与本包 X7/X9 的口径一致：用户看到的是「该做什么」，不是栈）。
        if not os.path.exists(p):
            sys.exit("!! 找不到文件：%s\n"
                     "   本脚本解析 YJK 工程「设计结果」目录下的 `wpj<N>.out`"
                     "（注意扩展名是 .out）。\n"
                     "   用法：python parse_wpj.py <wpj1.out> [wpj2.out ...]" % p)
        if os.path.isdir(p):
            sys.exit("!! 给的是目录，不是 wpj 文件：%s\n"
                     "   本脚本只解析文件；要批量解析就把「设计结果」目录下的"
                     " wpj*.out 逐个（或用通配符）传给本脚本。" % p)
        d = parse(p)
        st = col_chain_stats(d["cols"])
        print("=" * 60)
        # ★ 口径改了：报「柱段数」+「柱根数」，不再含混地只写「柱」
        print("%s  梁 %d  柱段数 %d  柱根数 %d"
              % (os.path.basename(p), len(d["beams"]), st["段数"], st["根数"]))
        print("  柱计数口径：柱段数 = N-C 编号个数（YJK 报的就是它）；"
              "柱根数 = 按柱段端点连通归并")
        print("  每根柱含几段：%s"
              % "、".join("%d 段 x %d 根" % (k, v)
                          for k, v in st["每根段数"].items()))
        if st["段数"] != st["根数"]:
            print("  ★ 柱段数(%d) != 柱根数(%d)：本层有柱被拆成多段（层高与标准层不同）。"
                  % (st["段数"], st["根数"]))
            print("    柱段数可能 ≈ 2 x 每标准层柱数 —— 引用这个数时必须写「柱段」，"
                  "别当成柱根数（按柱号分组做复核/优化时会整层错位）。")
        else:
            print("  每根柱 1 段：柱段数 = 柱根数 = 每标准层柱数（%d）" % st["根数"])
        tot = 0.0
        for b in d["beams"]:
            kg, al, as_ = rebar_kg(b)
            tot += kg
        print("  梁钢筋合计 %.1f kg" % tot)
        if d["beams"]:
            b = d["beams"][0]
            print("  例：N-B=%s %sx%s Lb=%s TopAst=%s" %
                  (b["No"], b["B"], b["H"], b.get("Lb"), b["TopAst"]))
            print("       BtmAst=%s Asv=%s" % (b["BtmAst"], b["Asv"]))
        if d["cols"]:
            c = d["cols"][0]
            print("  例：N-C=%s %sx%s Uc=%s Rs=%s Rsv=%s Asxt=%s Asvx=%s" %
                  (c["No"], c["B"], c["H"], c.get("Uc"), c.get("Rs"),
                   c.get("Rsv"), c.get("Asxt"), c.get("Asvx")))
        # ★ 覆盖率提示：上面那些 0 到底是真的 0，还是"没解析出来"？说清楚。
        prob = _parse_coverage_note(d.get("stats") or {}, p)
        for msg in prob:
            print("  !! %s" % msg)
        problems.extend(prob)
    if problems:
        print()
        print("!! 共 %d 项解析未命中：上面的梁/柱指标是被低估的，不能当结果用。"
              % len(problems))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
