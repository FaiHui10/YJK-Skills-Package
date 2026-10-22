# -*- coding: utf-8 -*-
"""为每种柱型建立独立的计算目录。

大型 YJK 模型在同一个目录里只能有一种柱截面定义，所以"五种柱型比选"通常的做法是
把种子模型复制成 5 份副本，各自改写自己那套柱截面、分别计算、最后汇总对比。
本模块把那套目录骨架建出来，避免每次手工新建。

目录结构
--------
<root>/
    00_输入/           scheme.json、forces.json、config.json、wmass.out
    01_RC/             柱型 = 普通RC      （种子模型副本 + 截面设计表.xlsx）
    02_RC_Core/        柱型 = 加芯RC
    03_SRC/            柱型 = 型钢SRC
    04_Diehe/          柱型 = 钢管叠合柱
    05_CFST/           柱型 = 圆钢管混凝土柱
    99_汇总/           五型柱对比表
    README.txt         流程说明（含叠合柱管内混凝土的人工确认提醒）
"""
import json
import os
import shutil

# 柱型 → 目录名（可被 --slots 覆盖）
SLOT = {"普通RC": "01_RC", "加芯RC": "02_RC_Core", "型钢SRC": "03_SRC",
        "钢管叠合柱": "04_Diehe", "圆钢管混凝土柱": "05_CFST"}
# slim 模式跳过的大目录（都可重新生成）
SKIP_DIRS = {"中间数据", "基础计算及结果输出", "基础备份", "backup", "设计结果", "__pycache__"}

MODEL_MARKERS = ("g-of.ymd", "g-of.yjk", "g-of.yjb")


def _copy_model(seed, dst, mode):
    os.makedirs(dst, exist_ok=True)
    if mode == "none":
        return 0
    n = 0
    for name in os.listdir(seed):
        s = os.path.join(seed, name)
        d = os.path.join(dst, name)
        if os.path.isdir(s):
            if mode == "slim" and name in SKIP_DIRS:
                continue
            shutil.copytree(s, d, dirs_exist_ok=True)
            n += sum(len(f) for _, _, f in os.walk(d))
        else:
            shutil.copy2(s, d)
            n += 1
    return n


def make_workspace(root, scheme, seed=None, forces=None, cfg=None, wmass=None,
                   mode="slim", slots=None, dry=False):
    """建目录骨架。返回 (创建/命中的路径列表, 提示信息列表)。"""
    slots = slots or SLOT
    types = scheme.get("types") or list(scheme["sections"].keys())
    made, tips = [], []
    os.makedirs(root, exist_ok=True)

    inp = os.path.join(root, "00_输入")
    os.makedirs(inp, exist_ok=True)
    made.append(inp)
    _write(inp, "scheme.json", scheme)
    if forces is not None:
        _write(inp, "forces.json", forces)
    if cfg is not None:
        _write(inp, "config.json", cfg)
    if wmass and os.path.isfile(wmass):
        shutil.copy2(wmass, os.path.join(inp, os.path.basename(wmass)))
    elif seed:
        cand = os.path.join(seed, "设计结果", "wmass.out")
        if os.path.isfile(cand):
            shutil.copy2(cand, os.path.join(inp, "wmass.out"))
            tips.append("已把种子模型的 wmass.out 拷到 00_输入/，混凝土强度以它为准")
        else:
            tips.append("种子模型里没找到 设计结果\\wmass.out，材料等级将回退到 config 默认值")

    for t in types:
        sub = os.path.join(root, slots.get(t, t))
        os.makedirs(sub, exist_ok=True)
        made.append(sub)
        if seed:
            cnt = _copy_model(seed, sub, mode)
            made.append("%s（%s 模式，%d 个文件）" % (sub, mode, cnt))
        else:
            tips.append("%s 只建了目录；把该柱型的种子模型放进去后再跑 design/apply" % sub)

    sm = os.path.join(root, "99_汇总")
    os.makedirs(sm, exist_ok=True)
    made.append(sm)

    _write_text(os.path.join(root, "README.txt"), _readme(scheme, types, slots, seed, mode))
    return made, tips


def _write(folder, name, obj):
    with open(os.path.join(folder, name), "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)


def _write_text(path, text):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def _readme(scheme, types, slots, seed, mode):
    L = []
    L.append("柱型比选计算目录")
    L.append("=" * 60)
    L.append("项目: %s" % scheme.get("project", ""))
    L.append("种子模型: %s（复制模式 %s）" % (seed or "未指定", mode))
    L.append("")
    L.append("目录对应关系")
    for t in types:
        L.append("    %-14s -> %s" % (slots.get(t, t), t))
    L.append("")
    L.append("流程")
    L.append("  0) 定柱位与楼层（如果 00_输入/scheme.json 还没生成）")
    L.append("       python cli.py init --model <种子模型目录> \\")
    L.append("              --groups \"Z1=15,16;Z2=14;Z3=13;Z4=1,7;Z5=2,3,4,9,10\" \\")
    L.append("              --std 3,4,5 --out 00_输入/scheme.json --apply")
    L.append("       python cli.py scope --scheme 00_输入/scheme.json --model <种子模型目录>")
    L.append("     （groups 一律人工指定，不从 tblGroup 反推；scope 会报柱号写错与漏柱）")
    L.append("  1) 每个柱型目录里，用 column-scheme-comparison 生成该柱型的截面")
    L.append("       python cli.py design --scheme 00_输入/scheme.json \\")
    L.append("              --forces 00_输入/forces.json --config 00_输入/config.json \\")
    L.append("              --wmass 00_输入/wmass.out --types <单个柱型> --out <该目录>/scheme.json")
    L.append("  2) 用 yjk-colmodel 把该柱型的截面写进目录中的模型")
    L.append("       python yjk.py apply <该目录> --changes <该目录>/changes.json --apply")
    L.append("  3) 回 YJK 重算，再用 yjk.py res / verify 复核")
    L.append("  4) 汇总：")
    L.append("       python cli.py quantity --scheme 00_输入/scheme.json --out 99_汇总/五型柱对比.xlsx")
    L.append("")
    L.append("★ 必须人工确认的一项")
    L.append("  叠合柱的**管内（核心）混凝土等级无法从 wmass.out 读取**，它保存在模型")
    L.append("  .yjk 二进制里，脚本读不到也写不进去。请到 YJK 里逐层确认并设置管内")
    L.append("  混凝土等级；或在 config.json 里用 diehe.fc_in 显式指定，并在报告中说明。")
    L.append("")
    L.append("其它约定")
    L.append("  * 计算模型 g-of.ymd 与施工图 施工图\\dtlmodel.ydb 会被同步改写（yjk.py apply）")
    L.append("  * 每次写入前自动备份 *.bak_时间戳")
    L.append("  * 材料单价口径见 column-scheme-comparison/references/pricing.md，换地区换年份要替换")
    return "\n".join(L) + "\n"
