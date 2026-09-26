# -*- coding: utf-8 -*-
r"""YJK「前处理计算参数」（俗称**总信息**）的按名读写与**回读校验**。

为什么必须有这个脚本
--------------------
`tblProjectPara` 是 `(ID, ParaVal)` 的纯数值表，**没有名字**；YJK 新建空工程的
默认值是：
    结构体系=框架结构、设防烈度=6度(0.05g)、场地类别=Ⅰ1、地面粗糙度=A、
    修正后基本风压=**0.10 kN/m²**、剪力墙抗震等级=三级 …
拿这套默认值去算一栋 28 层框架-核心筒，等于**基本不算抗震、不算风**，
而结果表面上完全正常 —— 属于最危险的一类静默错误。而官方 API
`DataFunc.ProjectPara_Set(id, val)` 只有 ID、没有表可查，所以以前只能靠
"改一行跑一轮、回读 wmass.out" 逐条猜。

现在这张表来自 **YJK 官方二次开发资料**里的宏定义头文件
`前处理计算参数宏定义.h`（见技能包 `yjk-dev-refs/06-总信息参数ID表/`），
本脚本把常用项固化成"名字 → ID → 枚举码"。

编码规则（★ 记住这一条就够）
--------------------------
    枚举型参数值 = 参数ID × 100 + 枚举序号
    数值型参数值 = 直接写数值

例如：结构体系 `101`，框筒结构是第 3 个枚举 ⇒ `101×100+3 = 10103`；
地面粗糙度 `201`，B 类 ⇒ `20102`。本脚本里所有枚举都按此规则算出，
与官方头文件逐条核对过（我此前靠 49 行 diff + 逐项回读反推出来的 12 个 ID
与官方宏定义**完全一致**）。

三种用法
--------
    # 1) 列出手册里收录的参数
    python projpara.py list
    # 2) 读某个模型库当前的总信息（枚举会翻成中文）
    python projpara.py read   --db 模型.ydb
    # 3) 按名改总信息（改完必须回读校验！）
    python projpara.py set    --db 模型.ydb \\
        --set 结构体系=框筒结构 --set 设防烈度="7 (0.1g)" --set 场地类别=III \\
        --set 地面粗糙度=B --set 基本风压=0.60 --set 周期折减系数=0.90 \\
        --set 特征周期=0.45 --set 多遇地震影响系数最大值=0.08 \\
        --set 考虑偶然偏心=1 --set 考虑双向地震作用=1 \\
        --set 框架抗震等级=二级 --set 剪力墙抗震等级=二级
    # 4) ★ 回读校验：模型里写的值，YJK 算的时候真的用上了吗？
    python projpara.py check  --db 模型.ydb --res 工程目录

★ 第 4 步不是可选项。实测教训：`tblProjectPara` 里某一项写对了、YJK 也照常
出结果，但那一项**根本没被采用**（我当时把"结构体系"写到了 ID=201，
结果 wmass.out 里仍然是"框架结构"，直到逐条回读才发现）。
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import sys

# ============================================================ 参数表（官方宏定义）
# 结构： 名称 -> (ID, {枚举名: 序号} 或 None)
#   None 表示数值型（直接写数值/字符串）
PARAMS = {
    # ---- 基本信息 ----
    "结构体系": (101, {"框架结构": 1, "框剪结构": 2, "框筒结构": 3, "筒中筒结构": 4,
                       "剪力墙结构": 5, "框支剪力墙结构": 6, "板柱-剪力墙结构": 7,
                       "异形柱框架结构": 8, "异形柱框剪结构": 9,
                       "钢框架-中心支撑结构": 13, "钢框架-偏心支撑结构": 14,
                       "单层工业厂房": 15, "多层钢结构厂房": 16}),
    "结构所在地区": (102, {"全国": 1, "广东": 2, "上海": 3}),
    "结构材料": (103, {"钢筋混凝土": 1, "钢与混凝土混合结构": 2, "钢结构": 3,
                       "砌体结构": 4}),
    "裙房层数": (104, None),
    "转换层号": (105, None),
    "地下室层数": (106, None),
    "加强层所在层号": (107, None),
    "嵌固端所在层号": (108, None),
    "与基础相连最大构件底标高": (109, None),
    "采用通用规范": (126, {"否": "0", "是": "1"}),
    # ---- 风荷载信息 ----
    "地面粗糙度": (201, {"A": 1, "B": 2, "C": 3, "D": 4}),
    "基本风压": (202, None),                    # 修正后的基本风压 kN/m2
    "结构X向基本周期": (203, None),              # s
    "结构Y向基本周期": (204, None),              # s
    "风荷载计算用阻尼比": (205, None),
    "是否考虑风振系数": (206, {"否": "0", "是": "1"}),
    "是否考虑横风向风振": (207, {"否": "0", "是": "1"}),
    "风荷载体型系数分段数": (212, None),
    "风荷载体型系数分段层号": (213, None),
    "风荷载体型系数": (214, None),
    "设缝多塔背风面体型系数": (215, None),
    # ---- 地震信息 ----
    "设计地震分组": (301, {"一组": "1", "二组": "2", "三组": "3"}),
    "设防烈度": (302, {"6 (0.05g)": 1, "7 (0.1g)": 2, "7 (0.15g)": 3,
                       "8 (0.2g)": 4, "8 (0.3g)": 5, "9 (0.4g)": 6}),
    "场地类别": (303, {"I0": 1, "I1": 2, "II": 3, "III": 4, "IV": 5}),
    "考虑偶然偏心": (304, {"否": "0", "是": "1"}),
    "X向偶然偏心": (305, None),
    "Y向偶然偏心": (306, None),
    "考虑双向地震作用": (307, {"否": "0", "是": "1"}),
    "计算振型个数": (308, None),
    "活荷载重力荷载代表值组合系数": (309, None),
    "周期折减系数": (310, None),
    "结构阻尼比": (311, None),                  # %
    "特征周期": (312, None),                    # s
    "多遇地震影响系数最大值": (313, None),
    "罕遇地震影响系数最大值": (314, None),
    "偶然偏心算法": (318, {"等效扭矩法(传统法)": 1, "瑞利-里兹投影反射谱法(新算法)": 2}),
    "是否自动设定振型个数": (319, {"否": "0", "是": "1"}),
    # ---- 设计信息 ----
    # ★ 这三个的枚举码都基于 701（见 ENUM_BASE），不是各自的 ID
    "框架抗震等级": (701, {"特一级": 1, "一级": 2, "二级": 3, "三级": 4, "四级": 5,
                           "非抗震": 6}),
    "钢框架抗震等级": (702, {"特一级": 1, "一级": 2, "二级": 3, "三级": 4, "四级": 5,
                             "非抗震": 6}),
    "剪力墙抗震等级": (703, {"特一级": 1, "一级": 2, "二级": 3, "三级": 4, "四级": 5,
                             "非抗震": 6}),
    "抗震构造措施的抗震等级提高": (704, {"不改变": "0", "提高一级": "1"}),
}

# 用于 check：参数名 -> wmass.out「设计参数输出」里的行标签
WMASS_LABEL = {
    "结构体系": "结构体系:",
    "地下室层数": "地下室层数:",
    "裙房层数": "裙房层数:",
    "转换层号": "转换层所在层号:",
    "加强层所在层号": "加强层所在层号:",
    "嵌固端所在层号": "嵌固端所在层号(层顶嵌固):",
    "地面粗糙度": "地面粗糙程度 :",
    "基本风压": "修正后的基本风压 (kN/m2):",
    "结构X向基本周期": "结构X向基本周期（秒）:",
    "结构Y向基本周期": "结构Y向基本周期（秒）:",
    "设计地震分组": "设计地震分组:",
    "设防烈度": "地震烈度:",
    "场地类别": "场地类别:",
    "特征周期": "特征周期:",
    "周期折减系数": "周期折减系数:",
    "框架抗震等级": "框架的抗震等级:",
    "剪力墙抗震等级": "剪力墙的抗震等级:",
    "考虑偶然偏心": "是否考虑偶然偏心:",
    "考虑双向地震作用": "是否考虑双向地震扭转效应:",
}

_ROMAN = {"Ⅰ0": "I0", "Ⅰ1": "I1", "Ⅱ": "II", "Ⅲ": "III", "Ⅳ": "IV",
          "I0": "I0", "I1": "I1", "II": "II", "III": "III", "IV": "IV"}
# 抗震等级：YJK 在 wmass.out 里印的是**等级数字**（0=特一级 … 4=四级）
GRADE_PRINT = {"0": "特一级", "1": "一级", "2": "二级", "3": "三级", "4": "四级"}
_GRADE_NAMES = ("框架抗震等级", "钢框架抗震等级", "剪力墙抗震等级")
_SEISGP = {"一": "1", "二": "2", "三": "3",
           "一组": "1", "二组": "2", "三组": "3"}


# 枚举基ID：少数参数族的枚举码并不以自己的 ID 为基（官方头文件如此定义）
# ★ 这一条是**实测**出来的，与"ID×100+序号"的机械推导冲突：
#   官方头文件只在 YP_KJKZDJ(701) 下定义了 YPV_KZDJ_*（特一/一/二/三/四级/非抗震），
#   702 钢框架 / 703 剪力墙 都没有各自成组的枚举宏 —— 三者**共用 701 的枚举码**，
#   区别只在"写哪一行 ID"。所以 703 + 二级 == 70103，而不是 70303。
#   证据：改 ID=703 为 "70103" → `projpara.py check` 回读到「剪力墙的抗震等级: 2」；
#         YJK 默认值是 "70104" → 回读到 3（三级）。
#   交叉参考：yjk-dev-refs/06-总信息参数ID表/参数ID速查.md 的「★★ 702/703」一节。
ENUM_BASE = {
    702: 701,       # 钢框架抗震等级：枚举沿用 YP_KJKZDJ(701) 的 70101..70106
    703: 701,       # 剪力墙抗震等级：同上（实测 703 写 70103 = 二级）
}


def _enum_base(pid):
    return ENUM_BASE.get(pid, pid)


def _norm(v):
    """把两边的写法归一到可比较的字符串。"""
    if isinstance(v, (bytes, bytearray)):
        return "<二进制 %d 字节>" % len(v)
    s = str(v).strip().strip("。").rstrip(":").strip()
    s = s.replace("（", "(").replace("）", ")")
    s = _ROMAN.get(s, s)
    return s


def _norm_val(name, v):
    """按参数语义再归一层：YJK 输出里 是/否、等级数字、组号的写法各不相同。"""
    s = _norm(v)
    if name in _GRADE_NAMES:
        return GRADE_PRINT.get(s, s)
    if s in ("是", "1"):
        return "1"
    if s in ("否", "0"):
        return "0"
    if name == "设计地震分组":
        return _SEISGP.get(s, s)
    return s


def encode(name, value):
    """把"人写的值"编成 tblProjectPara.ParaVal。

    ★ 两种编码形态（**别想当然**，这是逐条实测出来的）：
      · 编码型：值 = 枚举基ID×100 + 序号（例如 结构体系 101 -> 框筒 10103）
      · 直写型：表里直接存 0/1 或 1/2/3（例如 考虑偶然偏心、设计地震分组、采用通用规范）
      本脚本用"映射表的值是 str 还是 int"来区分：str=直写，int=编码。
    ★ 枚举基ID 未必等于参数ID：抗震等级族（701 框架 / 702 钢框架 / 703 剪力墙）
      在官方头文件里**共用 701 作枚举基**（70101 特一 … 70105 四级），
      所以 703 + 二级 要写成 70103。只按"ID×100+序号"算会写错。
    """
    pid, enum = PARAMS[name]
    if enum is None:
        return str(value)
    key = _norm(value)
    if key in enum:
        v = enum[key]
        return v if isinstance(v, str) else str(_enum_base(pid) * 100 + v)
    try:
        iv = int(str(value).strip())
    except ValueError:
        raise SystemExit("%s 的取值 %r 不认识；可选：%s（或直接给枚举序号）"
                         % (name, value, "、".join(enum)))
    base = _enum_base(pid)
    if base * 100 <= iv < base * 100 + 100:      # 已经是完整码 / 直写值
        return str(iv)
    hit = [k for k, v in enum.items() if v == iv]
    if not hit:
        raise SystemExit("%s 没有序号 %d 这个枚举；可选：%s"
                         % (name, iv, "、".join(enum)))
    return str(base * 100 + iv)


def decode(name, paraval):
    """把 ParaVal 翻回人能读的写法（枚举翻名字，数值原样）。"""
    pid, enum = PARAMS[name]
    if enum is None:
        return _norm(paraval)
    raw = _norm(paraval)
    if all(isinstance(v, str) for v in enum.values()):
        for k, v in enum.items():
            if v == raw:
                return k
        return raw
    try:
        iv = int(float(raw))
    except ValueError:
        return raw
    base = _enum_base(pid)
    if base * 100 <= iv < base * 100 + 100:
        want = iv - base * 100
        for k, v in enum.items():
            if v == want:
                return k
        return "%d(未收录的枚举 %d)" % (iv, want)
    return raw


# ============================================================ 读写
def _con(db):
    if not os.path.exists(db):
        raise SystemExit("模型库不存在：%s" % db)
    return sqlite3.connect("file:%s?mode=rw" % os.path.abspath(db).replace("\\", "/"),
                           uri=True)


def read_params(db, only=None):
    """返回 {名称: (原始串, 人读写法)}"""
    con = _con(db)
    try:
        rows = {r[0]: r[1] for r in
                con.execute("SELECT ID, ParaVal FROM tblProjectPara")}
    finally:
        con.close()
    out = {}
    for name, (pid, _e) in PARAMS.items():
        if only and name not in only:
            continue
        if pid in rows:
            out[name] = (rows[pid], decode(name, rows[pid]))
    return out


def set_params(db, **kw):
    """按名改总信息，返回 [(名称, ID, 改前, 改后)]。"""
    want = {}
    for name, val in kw.items():
        if name not in PARAMS:
            raise SystemExit("手册里没有参数 %r；用 `projpara.py list` 看可用名字。"
                             "\n（完整参数表见 yjk-dev-refs/06-总信息参数ID表/）" % name)
        want[PARAMS[name][0]] = (name, encode(name, val))
    con = _con(db)
    changed = []
    try:
        for pid, (name, val) in sorted(want.items()):
            cur = con.execute("SELECT ParaVal FROM tblProjectPara WHERE ID=?",
                              (pid,)).fetchone()
            if cur is None:
                raise SystemExit("模型库里没有 ID=%d（%s）这一行 —— 骨架模型不对？"
                                 % (pid, name))
            if str(cur[0]) == val:
                continue
            con.execute("UPDATE tblProjectPara SET ParaVal=? WHERE ID=?", (val, pid))
            changed.append((name, pid, cur[0], val))
        con.commit()
    finally:
        con.close()
    return changed


# ============================================================ 回读校验
def parse_wmass(res_dir):
    """从 设计结果\\wmass.out 的「设计参数输出」里取总信息（GBK）。

    ★ 必须**按行取第一个冒号**来切"标签 : 值"，不能用 `re.search(标签)`：
      否则查 "周期折减系数:" 会先命中
      "计算地震位移时不考虑周期折减系数:" 那一行，拿回一个"否"，
      于是把本来正确的一项误报成不一致。
    """
    p = os.path.join(res_dir, "wmass.out")
    if not os.path.exists(p):
        raise SystemExit("找不到 %s —— 需要先算过一轮" % p)
    txt = open(p, "rb").read().decode("gbk", "replace")
    i = txt.find("设计参数输出")
    if i < 0:
        raise SystemExit("%s 里没有「设计参数输出」（YJK 版本差异？）" % p)
    seg = txt[i:i + 30000]
    table = {}
    for line in seg.splitlines():
        s = line.strip()
        if not s:
            continue
        for sep in (":", "："):
            k = s.find(sep)
            if 0 < k < 60:                     # 标签不会太长
                table.setdefault(s[:k].strip(), s[k + 1:].strip())
                break
    return {name: table[label.rstrip(":： ").strip()]
            for name, label in WMASS_LABEL.items()
            if label.rstrip(":： ").strip() in table}


def check(db, res_dir, verbose=True):
    """★ 核心校验：模型里写的总信息，实算时真的生效了吗？"""
    written = read_params(db)
    solved = parse_wmass(res_dir)
    ok, bad, unknown = [], [], []
    for name, actual in sorted(solved.items()):
        if name not in written:
            unknown.append(name)
            continue
        _, mine = written[name]
        a, b = _norm_val(name, mine), _norm_val(name, actual)
        if a == b:
            ok.append((name, actual))
            continue
        # 数值型允许 1e-6 级别差异
        try:
            if abs(float(a) - float(b)) < 1e-6:
                ok.append((name, actual))
                continue
        except ValueError:
            pass
        bad.append((name, mine, actual))
    if verbose:
        print("=" * 78)
        print("总信息回读校验：%s  ←→  %s" % (os.path.basename(db), res_dir))
        print("=" * 78)
        print("\n【一致】%d 项" % len(ok))
        for n, v in ok:
            print("   %-26s %s" % (n, v))
        if bad:
            print("\n【★ 不一致】%d 项 —— 说明**写进了库但没被采用**，必须查！" % len(bad))
            for n, mine, actual in bad:
                print("   %-26s 库里=%s   实算=%s" % (n, mine, actual))
        else:
            print("\n【不一致】无")
    return ok, bad, unknown


def main(argv=None):
    ap = argparse.ArgumentParser(description="YJK 总信息（前处理计算参数）按名读写与回读校验")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("list", help="列出手册收录的参数")
    p.add_argument("--json", action="store_true")

    p = sub.add_parser("read", help="读模型库当前总信息")
    p.add_argument("--db", required=True)
    p.add_argument("--json", action="store_true")

    p = sub.add_parser("set", help="按名修改总信息")
    p.add_argument("--db", required=True)
    p.add_argument("--set", action="append", required=True,
                   metavar="名称=值", help="可重复；枚举可给名字或序号")

    p = sub.add_parser("check", help="★回读 wmass.out 校验总信息是否真的生效")
    p.add_argument("--db", required=True)
    p.add_argument("--res", required=True, help="工程目录或 设计结果 目录")

    a = ap.parse_args(argv)

    if a.cmd == "list":
        if a.json:
            print(json.dumps({k: {"ID": v[0], "枚举": v[1]} for k, v in PARAMS.items()},
                             ensure_ascii=False, indent=1))
            return 0
        print("%-30s %-6s %s" % ("名称", "ID", "取值"))
        for k, (pid, enum) in PARAMS.items():
            print("%-30s %-6d %s" % (k, pid,
                                     "、".join(enum) if enum else "数值"))
        print("\n★ 编码规则：枚举型 = 参数ID×100 + 枚举序号；数值型直接写数值。")
        print("  完整参数表（1800+ 行宏定义）见 yjk-refs/06-总信息参数ID表/。")
        return 0

    if a.cmd == "read":
        got = read_params(a.db)
        if a.json:
            print(json.dumps({k: {"原始": v[0], "人读": v[1]} for k, v in got.items()},
                             ensure_ascii=False, indent=1))
            return 0
        print("%-30s %-14s %s" % ("名称", "原始值", "解读"))
        for k, (raw, human) in got.items():
            print("%-30s %-14s %s" % (k, raw, human))
        return 0

    if a.cmd == "set":
        kw = {}
        for s in a.set:
            if "=" not in s:
                raise SystemExit("--set 要写成 名称=值，收到 %r" % s)
            k, v = s.split("=", 1)
            kw[k.strip()] = v.strip()
        ch = set_params(a.db, **kw)
        if not ch:
            print("无需改动（这些项本来就是目标值）")
        for n, pid, old, new in ch:
            print("  %-26s ID=%-5d %s -> %s   （%s）"
                  % (n, pid, old, new, decode(n, new)))
        print("\n★ 改完请务必回读校验：")
        print("    python projpara.py check --db %s --res <工程目录>" % a.db)
        return 0

    if a.cmd == "check":
        res = a.res if os.path.basename(os.path.normpath(a.res)) == "设计结果" \
            else os.path.join(a.res, "设计结果")
        ok, bad, unknown = check(a.db, res)
        return 1 if bad else 0

    return 0


def _utf8_console():
    """让输出在任何控制台编码下都不崩（GBK 下把不可编码字符替换掉）。

    为什么需要：本包会打印 ✅ ❌ ⚠ −(U+2212) ² ³ 等**非 cp936** 字符，
    默认 GBK 控制台下 print 会抛 UnicodeEncodeError 并**以退出码 1 中断**，
    于是一个其实已经成功的任务（比如文件已经落盘）会被上层判成失败。
    errors=replace 让它在 UTF-8 控制台下原样输出、在 GBK 下退化成 ?，都不崩。

    ★ 只在真正的 CLI 入口调用：本文件会被别人 import 当库用，
      在模块顶层无条件改 stdout 会污染 import 它的进程。
    """
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(errors="replace")
        except Exception:
            pass


if __name__ == "__main__":
    _utf8_console()
    sys.exit(main())
