# -*- coding: utf-8 -*-
"""柱位 / 楼层的"骨架生成"与"一致性校验"。

解决的问题：`scheme.json` 里的 `std_floors`（楼层）与 `groups`（柱位分组）以前只能手写，
写错柱号会被静默少算、写错层号会直接算偏。本模块提供两件事：

  make_scheme(...)  —— 从模型自动填出 std_floors（定义层高、各自然层实际层高、首个自然层号）
                       与 sections（现有截面），groups 由人工传入
  check(...)        —— 校验方案里的标准层号、柱号、层高是否与模型对得上、有没有漏柱

归并组（柱位分组）**一律由人工指定**，不从模型反推：`tblGroup` 的成员 BLOB 语义未公开
（既不是柱号也不是柱段 idNew，实测各组偏移量还不一致），靠它反推不可靠。
"""
import copy

import grades as G


def read_model(model_dir):
    """读模型里与"选柱位/楼层"有关的事实。

    返回 {标准层号: {"std_id", "height_mm", "nat_floors", "nat_heights", "cols"}}
    其中 cols = {柱号: {"text": 截面文本, "geo": 方案用几何}}，只含该标准层实际有柱段的柱。
    """
    K = G._load_yjkio()
    if K is None:
        raise SystemExit("找不到 yjk-colmodel 技能里的 yjkio.py，无法读取模型。"
                         "请确认两个技能都装在同一个 skills 根目录下。")
    files = K.model_files(model_dir)
    if not files["calc"]:
        raise SystemExit("在 %s 里找不到 g-of.ymd" % model_dir)
    con = K.connect(files["calc"])
    try:
        std = K.std_floors(con)
        nats = K.std_floor_natural(con)
        hgt = {f["no"]: f["height_mm"] for f in K.floors(con)}
        sects = K.load_sects(con)
        out = {}
        for no, info in sorted(std.items()):
            if no < 0:
                continue
            fl = sorted(nats.get(info["id"], []))
            cols = {}
            if fl:
                for s in K.load_segs(con, [info["id"]]):
                    row = sects.get(s["SectID"])
                    if row:
                        cols[s["No_"]] = {"text": K.sect_text(row),
                                          "geo": norm_geo(K.sect_geo(row))}
            out[no] = {"std_id": info["id"], "height_mm": info["height_mm"],
                       "nat_floors": fl,
                       "nat_heights": [hgt.get(n) for n in fl], "cols": cols}
        return out
    finally:
        con.close()


def norm_geo(g):
    """把 yjkio.sect_geo 的结果收敛成 scheme 里的几何写法。"""
    k = g["kind"]
    if k == 12:
        return {"kind": 12, "D": g["D"], "tw": g["tw"]}
    if k == 15:
        return {"kind": 15, "b": g["b"], "f": g["f"], "tw": g["tw"], "d": g["d"]}
    if k == 102:
        return {"kind": 102, "b": g["b"], "D": g["D"], "tw": g["tw"]}
    return {"kind": 1, "b": g["b"]}


def parse_groups(spec):
    """解析 --groups 字符串："Z1=15,16;Z2=14" -> {"Z1":[15,16], "Z2":[14]}"""
    out = {}
    for part in str(spec).replace("；", ";").replace("，", ",").split(";"):
        part = part.strip()
        if not part:
            continue
        if "=" not in part:
            raise SystemExit("--groups 格式应为 名称=柱号,柱号;名称2=…，收到 %r" % part)
        name, cols = part.split("=", 1)
        out[name.strip()] = [int(x) for x in cols.replace("、", ",").split(",") if x.strip()]
    if not out:
        raise SystemExit("--groups 为空")
    return out


def make_scheme(model_info, stds, groups, types, sec_type=None, project=""):
    """生成 scheme 骨架。返回 (scheme, 提示列表)。"""
    tips = []
    stds = [int(x) for x in stds]
    lack = [s for s in stds if s not in model_info]
    if lack:
        raise SystemExit("模型里没有这些标准层：%s（可选：%s）"
                         % (lack, sorted(model_info)))
    sections = {t: {} for t in types}
    sec_type = sec_type or types[0]
    if sec_type not in types:
        raise SystemExit("--sec-type 必须是 --types 之一（收到 %r）" % sec_type)

    std_floors = {}
    for no in stds:
        info = model_info[no]
        if not info["nat_floors"]:
            tips.append("标准层%s 在模型里没有柱段/自然层，已跳过" % no)
            continue
        nh = info["nat_heights"]
        if any(h is None for h in nh):
            tips.append("标准层%s 有自然层取不到层高，已用定义层高补齐" % no)
            nh = [h if h else (info["height_mm"] or 0) for h in nh]
        std_floors[str(no)] = {
            "height_mm": info["height_mm"] or nh[0],
            "nat_heights": nh,
            "first_nat": min(info["nat_floors"]),
        }
        for gname, members in groups.items():
            miss = [c for c in members if c not in info["cols"]]
            if miss:
                tips.append("标准层%s 的 %s 里这些柱号模型里没有：%s" % (no, gname, miss))
                continue
            geos = {c: tuple(sorted(info["cols"][c]["geo"].items())) for c in members}
            if len(set(geos.values())) > 1:
                tips.append("标准层%s 的 %s 组内现有截面不一致（%s），骨架取了首根柱的截面，"
                            "请核对分组 %s" % (no, gname,
                                          "/".join(info["cols"][c]["text"] for c in members),
                                          members))
            sections[sec_type].setdefault(str(no), {})[gname] = \
                copy.deepcopy(info["cols"][members[0]]["geo"])

    scheme = {"project": project or "（请填写项目名）",
              "std_floors": std_floors, "groups": groups, "types": list(types),
              "sections": sections}
    others = [t for t in types if t != sec_type]
    if others:
        tips.append("sections 只填了 %s（取模型现有截面）；%s 需要跑 design 生成截面"
                    % (sec_type, "、".join(others)))
    return scheme, tips


def check(scheme, model_info):
    """校验方案的柱位/楼层，返回 (errors, warns, 明细行)。"""
    errors, warns, detail = [], [], []
    stds = sorted(int(x) for x in scheme["std_floors"])
    for std in stds:
        cfg = scheme["std_floors"][str(std)]
        if std not in model_info:
            errors.append("标准层%s 在模型里不存在（模型有 %s）"
                          % (std, sorted(model_info)))
            continue
        info = model_info[std]
        n_model, n_scheme = len(info["nat_floors"]), len(cfg.get("nat_heights") or [])
        if n_model != n_scheme:
            warns.append("标准层%s 的 nat_heights 有 %d 个，模型里该标准层覆盖 %d 个自然层 %s"
                         "（代表楼层总高会算错）" % (std, n_scheme, n_model, info["nat_floors"]))
        if info["nat_floors"]:
            if cfg.get("first_nat") != min(info["nat_floors"]):
                warns.append("标准层%s 的 first_nat=%s，模型实际首层是 %s"
                             "（会影响从 wmass.out 取材料等级）"
                             % (std, cfg.get("first_nat"), min(info["nat_floors"])))
        if info["height_mm"] and cfg.get("height_mm") and \
                abs(float(cfg["height_mm"]) - float(info["height_mm"])) > 1e-6:
            warns.append("标准层%s 的定义层高 %s 与模型 tblStdFlr.Height=%s 不一致"
                         % (std, cfg["height_mm"], info["height_mm"]))
        for nat, h in zip(info["nat_floors"], info["nat_heights"]):
            if h and abs(float(cfg["height_mm"]) - float(h)) > 1e-6:
                pass                                     # 定义层高与自然层层高本就可能不等，不提示

        covered = set()
        for gname, members in scheme["groups"].items():
            miss = [c for c in members if c not in info["cols"]]
            if miss:
                errors.append("标准层%s 的 %s 组里有模型不存在的柱号：%s（该层实际柱号 %s）"
                              % (std, gname, miss, sorted(info["cols"])))
            covered |= {c for c in members if c in info["cols"]}
        allcols = set(info["cols"])
        uncovered = sorted(allcols - covered)
        extra = sorted(covered - allcols)
        detail.append({"std": std, "模型柱数": len(allcols), "方案覆盖": len(covered & allcols),
                       "未覆盖": uncovered, "多余": extra,
                       "自然层": info["nat_floors"], "定义层高": info["height_mm"]})
        if uncovered:
            warns.append("标准层%s 有 %d 根柱没进方案（不会参与统计）：%s"
                         % (std, len(uncovered), uncovered))

    # 截面是否齐（按柱型汇总，避免刷屏）
    missing = {}
    for t in scheme["types"]:
        n = 0
        for std in stds:
            for gname in scheme["groups"]:
                if gname not in scheme["sections"].get(t, {}).get(str(std), {}):
                    n += 1
        if n:
            missing[t] = n
    if missing:
        warns.append("缺少截面：%s（共 %d 处，跑 design 即可生成）"
                     % ("、".join("%s %d 处" % kv for kv in missing.items()),
                        sum(missing.values())))
    return errors, warns, detail
