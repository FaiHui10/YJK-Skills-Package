# -*- coding: utf-8 -*-
"""混凝土强度 / 钢号的来源解析。

优先级
------
1. `--model <模型目录>` 或 `--wmass <wmass.out 路径>`：从种子模型的 **wmass.out** 读取
   各自然层柱的材料等级，再按标准层归并（取该标准层最底层有记录的自然层）。
2. `--model-json <export.json>`：读 yjk-colmodel `yjk.py export --json` 的输出，
   里面已含逐标准层 `column_grade`。
3. config 里的 `concrete` / `steel_grade`：全部标准层用同一个值。

**叠合柱的管内（核心）混凝土等级读不到**：YJK 的 wmass.out 对叠合柱只报一个
混凝土等级（测得是管外那一档），管内等级存在模型的 .yjk 二进制里，脚本既读不到
也写不进去。所以本模块对叠合柱一律给出提醒，并允许用 config 的 `diehe.fc_in`
显式指定；未指定时按"与管外相同"处理，但**必须由人在 YJK 里确认并设置**。
"""
import json
import os
import sys


def _load_yjkio():
    """优先用同机其它技能里的 yjkio；找不到就返回 None（不影响其它功能）。

    本文件在 <skills根>/column-scheme-comparison/scripts/ 下，
    所以 <skills根> = 上溯三级；同级的 yjk-colmodel/scripts 里就是 yjkio.py。
    """
    try:
        import yjkio
        return yjkio
    except ImportError:
        pass
    here = os.path.abspath(__file__)
    root = os.path.dirname(os.path.dirname(os.path.dirname(here)))
    sib = os.path.join(root, "yjk-colmodel", "scripts")
    if os.path.isdir(sib):
        sys.path.insert(0, sib)
        try:
            import yjkio
            return yjkio
        except ImportError:
            return None
    return None


def _resolve_wmass(spec):
    """spec 可以是 wmass.out 文件、含 设计结果\\wmass.out 的模型目录。"""
    if os.path.isdir(spec):
        return os.path.join(spec, "设计结果", "wmass.out")
    return spec


def load_grades(spec=None, scheme=None, cfg=None):
    """返回 (grades, warnings)。

    grades = {标准层号(int): {"混凝土": "C60", "钢号": "355", "来源": "…",
                               "管内混凝土": "C60", "管内来源": "…"}}
    """
    cfg = cfg or {}
    warn = []
    grades, src = {}, None

    if spec:
        path = _resolve_wmass(spec)
        if path.lower().endswith(".out") or os.path.exists(path):
            K = _load_yjkio()
            if K is None:
                warn.append("找不到 yjk-colmodel 技能里的 yjkio.py，无法直接解析 wmass.out；"
                            "请改用 `--model-json <export.json>`（先跑 "
                            "yjk-colmodel 的 `yjk.py export --json`）")
            else:
                wm = K.parse_wmass(os.path.dirname(path))
                if wm is None:
                    warn.append("未找到 %s" % path)
                else:
                    src = "wmass.out(%s)" % os.path.basename(os.path.dirname(path))
                    nats = _std_to_nat(scheme)
                    for std, fl in nats.items():
                        g = None
                        for nat in fl:
                            gg = K.wmass_column_grade(wm, nat)
                            if gg:
                                g = (nat, gg)
                                break
                        if g:
                            nat, gg = g
                            grades[std] = {"混凝土": gg.get("混凝土"),
                                           "钢号": _steel_grade(gg.get("钢号")),
                                           "来源": "wmass.out 结构层%d" % nat}
        elif os.path.exists(spec):
            data = json.load(open(spec, encoding="utf-8-sig"))
            for f in data.get("std_floors", []):
                if f.get("column_grade"):
                    g = f["column_grade"]
                    grades[int(f["std"])] = {"混凝土": g.get("混凝土"),
                                             "钢号": _steel_grade(g.get("钢号")),
                                             "来源": "export.json"}
            src = os.path.basename(spec)

    if not grades:
        g = cfg.get("concrete", "C60")
        s = cfg.get("steel_grade", "Q355")
        for std in (scheme or {}).get("std_floors", {}):
            grades[int(std)] = {"混凝土": g, "钢号": s, "来源": "config 默认值"}
        if spec:
            warn.append("未能从 %s 读到材料等级，已回退到 config 默认值" % spec)
        else:
            warn.append("未指定材料来源（--model/--wmass/--model-json），全部按 config "
                        "默认值 %s / %s 取值" % (g, s))

    # 叠合柱管内混凝土：读不到，只能提醒
    diehe_in = cfg.get("diehe", {}).get("fc_in")
    for std, g in grades.items():
        if diehe_in:
            g["管内混凝土"] = diehe_in
            g["管内来源"] = "config.diehe.fc_in（用户指定）"
        else:
            g["管内混凝土"] = g["混凝土"]
            g["管内来源"] = "按管外取值（未确认）"
    if any(t in ("钢管叠合柱", "叠合柱") for t in (scheme or {}).get("types", [])):
        warn.append("叠合柱的**管内（核心）混凝土等级无法从 wmass.out 读取**"
                    "（YJK 对叠合柱只报一个混凝土等级），且它保存在模型 .yjk 二进制里，"
                    "脚本读不到也写不进去。本程序按“%s”参与计算，"
                    "**请在 YJK 里确认并设置管内混凝土等级**，或用 config 的 "
                    "diehe.fc_in 显式指定。" % (diehe_in or "与管外相同"))
    return grades, warn, src


def _std_to_nat(scheme):
    """{标准层号: [自然层号…]}；scheme 里没写 first_nat 就按 n_floors 顺序推。"""
    out = {}
    for std, f in (scheme or {}).get("std_floors", {}).items():
        n = len(f.get("nat_heights") or [0] * int(f.get("n_floors", 1)))
        first = f.get("first_nat")
        out[int(std)] = [first + i for i in range(n)] if first else list(range(1, n + 1))
    return out


def _steel_grade(num):
    """wmass 里钢材写的是数值（355/235/360），转成牌号。"""
    if not num:
        return None
    s = str(num)
    return {"235": "Q235", "355": "Q355", "390": "Q390", "420": "Q420", "345": "Q345"}.get(s, s)
