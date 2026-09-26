# 官方命令全表（YJKSControl 可调用）

来源：YJK 官方《命令说明文档》。**参数带不带扩展名是有讲究的，见每节的「参数」列。**
未列出的命令可在 YJK 里点按钮，再从命令行读到对应命令名。

调用方式统一是（本技能的 `Client` 已封装）：

```python
cli.run("<命令名>", "<参数>")      # 无参命令传空串 ""
```

> 注意：`RunCmd` 是**阻塞**的。命令弹模态框时会**永久不返回** ——
> 所以 `Client.run()` 用后台线程 + 超时（默认抛 `TIMEOUT`）。别以为卡死了就重启 YJK。

---

## 0. 工程界面

| 命令 | 含义 | 参数 |
|---|---|---|
| `UIOpen` | 项目打开 | `.yjk` 文件所在地址，**带 `.yjk`** |
| `UINew` | 项目新建 | `.yjk` 创建地址，**带 `.yjk`** |

**行为说明**（7.1）：

- `UINew` **认路径**，能在指定目录建出真工程（约 5.4s，窗口标题含完整路径）。
- `UIOpen` **忽略路径** —— 只开出空工程，且此后所有命令退化成 `0.0s` 秒回无效。
  → **要"打开模型"，请用 `UINew` 建工程 + `yjk_importydb` 导入模型。**

## 1. 建模模块

| 命令 | 含义 | 参数 |
|---|---|---|
| `yjk_new` | 新建工程 | `.yjk` 地址，**不带 `.yjk`** |
| `yjk_opennew` | 打开已有结构模型 | `.yjk` 地址，**不带 `.yjk`** |
| `yjk_importydb` | **导入 ydb 文件** | `.ydb` 地址，**带 `.ydb`** |
| `yjk_exportydbdefault` | 导出 ydb（生成在施工图文件夹下） | 无 |
| `yjk_repair` | 工程修复 | 无 |
| `yjk_formnode` | 形成节点 | `1`=本层，`2`=全楼 |
| `yjk_formslab_alllayer` | 形成楼板 | 无 |
| `yjk_save` | **模型保存** | 无 |
| `yjk_setlayersupport` | 由建模切到前处理前的相关命令 | 无 |
| `yjkspre_genmodrel` | 由建模切到前处理前的相关命令 | 无 |
| `yjktransload_tlplan` | 由建模切到前处理前的相关命令 | 无 |
| `yjktransload_tlvert` | 由建模切到前处理前的相关命令 | 无 |
| `yjk_node` | 绘制节点 | 详官方案例 test03 |
| `yjk_line2ps` | 绘制直线 | 详官方案例 test03 |
| `yjk_arc3p` | 绘制圆弧 | 详官方案例 test03 |
| `yjk_circle` | 绘制圆 | 详官方案例 test03 |
| `yjk_rectangle` | 绘制矩形 | 详官方案例 test03 |

**注意**：`yjk_opennew` 返回假的 `OK(0.0s)` 且**不打开工程**，别用。

## 2. 前处理模块

| 命令 | 含义 | 参数 |
|---|---|---|
| `yjkdesign_dsncalculating_all` | **生成数据 + 全部计算** | 无 |
| `yjkdesign_dsncalculating_cal_design` | 全部计算（计算 + 设计） | 无 |
| `yjkdesign_dsncalculating_cal` | 只计算（无设计） | 无 |
| `yjkdesign_dsncalculating_design` | 只设计（不计算） | 无 |

## 3. 设计结果模块

| 命令 | 含义 |
|---|---|
| `yjkdesign_dsnExportDB_NoDlg` | 导出 `dsnmodel.ydb` |
| `yjkdisplay_dspdrawmenu1` | 构件编号 |
| `yjkdisplay_dspdrawmenu2` | 配筋简图 |
| `yjkdisplay_dspdrawmenuzyb` | **轴压比** |
| `yjkdisplay_dspdrawmenujkb` | 剪跨比 |
| `yjkdisplay_dspdrawmenubeamdeflection` | 梁挠度 |
| `yjkdisplay_dspdrawmenuzcq` | 柱冲切 |
| `yjkdisplay_dspdrawmenubeamcrack` | 组合梁裂缝 |
| `yjkdisplay_dspdrawmenuedge` | 边缘构件 |
| `yjkdisplay_dspdrawvercompl` | 偏拉验算 |
| `yjkdisplay_dspdrawstdnlbeamm` / `...beamv` | 梁 M / 梁 V |
| `yjkdisplay_dspdrawstdnlcolup` / `...coldown` | 柱顶 / 柱底 |
| `yjkdisplay_dspdrawdsnnlbeamm` / `...beamv` | 弯矩 / 剪力 |
| `yjkdisplay_dspdrawstdnl3d` | 三维内力 |
| `yjkdisplay_dspdrawpj3d` | 三维配筋 |
| `yjkdisplay_dspdrawinquirie3d` | 三维查询 |
| `yjkdisplay_dspdrawprop3d` | 三维属性 |
| `yjkdisplay_dspdrawmenu10` | 三维位移 |
| `yjkdisplay_dspdrawmenu13` | 振型 |
| `yjkdisplay_dspdrawbuckling` | 屈曲 |
| `yjkdisplay_dspdrawmenu12` | 质心振动 |
| `yjkdisplay_dspdrawmenu9` | 楼层结果 |

## 4. 施工图模块

**4.1 板施工图**

> 下表沿用官方文档的小写写法；**实际调用建议用 `YJK.CUI` 里的原始大小写**
> （如 `StdSlab_RedrawNceng` / `StdSlab_AUTOCAL` / `StdSlab_batgenstl` /
> `stdslab_AutoStatstl` / `StdSlab_RESELECTREIN`）。
> 命令名以 `C:\YJKS\YJKS_7_1_0\YJK.CUI` 为准 —— 那是 3514 条 `<Command>` 的权威注册表，
> 用正则 `<MenuMacro UID="([^"]*)"[^>]*>(.*?)</MenuMacro>` + `<Command>([^<]*)</Command>` 挖即可。

| 命令 | 含义 |
|---|---|
| `stdslab_redrawnceng` | 绘新图 |
| `stdslab_opendrawplan` | 打开旧图 |
| `stdslab_autocal` | 计算 |
| `stdslab_dispcal` | 计算结果 |
| `stdslab_quantity` | 本层楼板钢筋统计 |
| `stdslab_autostatstl` | **全楼楼板钢筋统计（出量的关键一步）** |

**4.2 梁施工图**

| 命令 | 含义 |
|---|---|
| `dtlrc_newbeamplanload` | 由现有配筋结果绘新图 |
| `dtlrc_beamtext` | 单跨计算书 |
| `dtlrc_statbeam` | 本层梁钢筋统计 |
| `dtlrc_statbuildingbeamsteelspecexcel` | 全楼梁钢筋统计（按钢筋规格和类别） |

**4.3 柱施工图**

| 命令 | 含义 |
|---|---|
| `dtlrc_drawnewcolplan` | 由现有配筋结果绘新图 |
| `dtlrc_colsumgj` | 全楼柱钢筋统计文本 |
| `dtlrc_ssce` | **全楼柱钢筋统计 excel** |

**4.4 墙施工图**

| 命令 | 含义 |
|---|---|
| `dtlrc_wallplanregennew` | 重新归并选筋并绘新图 |
| `dtlrc_stwbarj` | 本层墙钢筋统计 |
| `dtlrc_ssw` | 全楼墙钢筋统计文本 |
| `dtlrc_sswe` | 全楼墙钢筋统计 excel |

## 5. 其它

| 命令 | 含义 | 参数 |
|---|---|---|
| `SetCurrentLabel` | 切换标签 | 标签栏 ID（见表下） |
| `yjks_pyload` | 加载 py 文件（需先替换相关文件） | `.py` 地址，带 `.py` |
| `yjks_csload` | 加载 dll（需先替换相关文件） | `.dll` 地址，带 `.dll` |

### 标签栏 ID（`SetCurrentLabel` 用）

| 标签栏 | ID | 标签栏 | ID |
|---|---|---|---|
| 轴线网格 | `IDModule_Axis` | 基础建模 | `JCCAD_BUILDING` |
| 构件布置 | `IDModule_Element` | 基础计算及结果输出 | `JCCAD_RESULT` |
| 楼板布置 | `IDModule_Slab` | 基础施工图 | `IDDTL_DETAIL_JC` |
| 模型转换 | `IDModule_RecastModel_DC` | 地质资料 | `ID_DZZL_MENU` |
| 荷载输入 | `IDModule_Load` | 通用编辑 | `IDDTL_DETAIL_EDIT` |
| 自定义工况 | `IDModule_LoadEx` | 板施工图 | `IDDTL_DETAIL_SLAB` |
| 楼层组装 | `IDModule_Layer` | 梁施工图 | `IDDTL_DETAIL_BEAM` |
| 空间结构 | `IDModule_SPACE` | 柱施工图 | `IDDTL_DETAIL_COLUMN` |
| 鉴定加固 | `IDModule_JDJG` | 墙施工图 | `IDDTL_DETAIL_WALL` |
| 预制构件 | `IDModule_YZGJ` | 梁柱墙施工图 | `IDDTL_DETAIL_INTEGRITY` |
| 预制构件拆分 | `IDModule_PcGraph` | 楼梯施工图 | `IDDTL_DETAIL_LT` |
| DWG 转换 | `IDModule_RecastModel` | 加固施工图 | `IDDTL_DETAIL_STRENGTHENING` |
| 梁配筋转换 | `ID_RC_IMPORT_BEAM` | 平面钢筋编辑 | `IDDTL_DETAIL_PRECAST` |
| 柱配筋转换 | `ID_RC_IMPORT_COLUMN` | 预制构件深化设计 | `IDDTL_DETAIL_PRECAST3d` |
| 墙配筋转换 | `ID_RC_IMPORT_WALL` | 叠合板施工图 | `IDDTL_PCTRUSSDETAIL` |
| 板配筋转换 | `ID_RC_IMPORT_SLAB` | 单构件详图设计 | `IDDTL_PCDETAILGRAPH` |
| 楼梯配筋转换 | `ID_RC_IMPORT_STAIR` | 钢结构施工图 | `IDDTL_STEEL_FRAME` |
| **前处理及计算** | **`IDSPRE_ROOT`** | 网架网壳施工图 | `IDDTL_STEEL_FRAME` |
| **设计结果** | **`IDDSN_DSP`** | 钢结构识图 | `YJK_XSTEEL_RecoCad` |
| 工程校审 | `IDAUDIT_BASE` | 工程量统计 | `IDQUANTITYLIST_DETAIL` |
| 砌体 | `IDQT_MASONRY` | | |
| 底框结果 | `IDDSN_DSP_QT` | | |
| 砼构件结果 | `IDDSN_DSP_QTCON` | | |

---

## 本技能实际使用的链条

**预处理（`--prep`）** —— 导入 ydb 后先跑，把模型"收拾干净"：

```python
PREP_CHAIN = [
    ("yjk_repair", ""),               # 工程修复
    ("yjk_save", ""),                 # 保存（写盘，用 mtime 判定）
    ("yjk_formnode", "2"),            # 形成节点（全楼）
    ("yjk_formslab_alllayer", ""),    # 形成楼板
]
```

**计算（`--calc`）** —— 官方"建模 → 前处理 → 计算 → 设计结果"顺序：

```python
CALC_CHAIN = [
    ("yjk_setlayersupport", ""),            # 建模 → 前处理 的过渡命令
    ("yjkspre_genmodrel", ""),
    ("yjktransload_tlplan", ""),
    ("yjktransload_tlvert", ""),
    ("SetCurrentLabel", "IDSPRE_ROOT"),     # 切到「前处理及计算」
    ("yjkdesign_dsncalculating_all", ""),   # 生成数据 + 全部计算
    ("SetCurrentLabel", "IDDSN_DSP"),       # 切到「设计结果」
]
```

跑完检查 `<工作目录>\设计结果\` 里的文件（30 层框筒约 70 个）。
**判断"算完没有"优先看 `_yjk_outbox.txt` 的回执**（命令级、带时间戳，还能区分成功与失败），不要只看 `RunCmd` 返回值；用 `wmass.out` 的 mtime 轮询也可以，但每轮都要过冲几秒，而且分不清"算完了"和"算失败了"（失败也写文件）。

---

## 要"具体配筋量"（板/梁/柱钢筋 kg）时补的链条

上面 CALC_CHAIN 只出内力与设计结果，**不产出钢筋用量统计表**。要拿到"全楼××钢筋用量.xlsx"，再加下面两段（顺序不能换）。

### 板钢筋（最坑，必须先跑，缺一步就全 0）

```python
SLAB_CHAIN = [
    ("SetCurrentLabel", "IDDTL_DETAIL_SLAB"),   # 切到「板施工图」
    ("StdSlab_RedrawNceng", ""),   # 1~12s  绘新图，写 DSevData_*.xml ×19
    ("StdSlab_AUTOCAL", ""),       # 0.3~2s 计算
    ("StdSlab_batgenstl", ""),     # 10~26s 批量生成全部楼层板施工图，含计算+选筋
    ("stdslab_AutoStatstl", ""),   # 2~7s  全楼楼板钢筋统计 —— 就是它让钢筋非 0
]
```

判据：`stdslab_AutoStatstl` 必须写出 **`全楼楼板钢筋用量.dat`**（按层×直径的表格）和 `SlabStlQuantity1.dat`。**没有它，表格只有表头、合计 = 0。**

- `StdSlab_Quantity`（本层统计）**不够** —— 只写 `SlabStlQuantity3.dat`。
- `StdSlab_batgenstl` 会弹模态框 `「施工图已经进行过选筋,是否重新选筋?」` → **必须答「否」**，否则 `RunCmd` 永久不返回。后台应答见 `troubleshooting.md` §12。
- `StdSlab_RESELECTREIN` 单独用是死路（只重新选筋 + 弹框，不产出文件）。

### 梁/柱/墙钢筋

```python
QUANT_CHAIN = [
    ("SetCurrentLabel", "IDQUANTITYLIST_DETAIL"),        # 切到「工程量统计」
    ("DtlRC_SSSE", ""),                                  # 全楼板钢筋统计 excel
    ("DtlRC_StatBuildingBeamSteelSpecExcel", ""),        # 全楼梁钢筋用量(按钢筋规格与类别)
    ("DtlRC_SSCE", ""),                                  # 全楼柱钢筋用量
    ("DtlRC_SSWE", ""),                                  # 全楼墙钢筋用量
]
```

产物落在 `<工程目录>\施工图\`：

| 文件 | 内容 |
|---|---|
| `全楼楼板钢筋用量.xlsx` | 每层一行 + 合计行；直径 6/8/10/14/16/18 |
| `全楼梁钢筋用量(钢筋规格与类别).xlsx` | 每层 5 行（上部纵筋/下部纵筋/箍筋/腰筋/腰筋拉结筋）+ 全楼总计；直径 6/8/12/18/20/22/25/28/32 |
| `全楼柱钢筋用量(钢筋规格与类别).xlsx` | 纵筋/箍筋/基础插筋；直径 8/18/20 |
| `全楼墙钢筋用量(钢筋规格与类别).xlsx` | 同梁格式 |

- **取「第N层」那一行算单层面积/用量，不要取「全楼/合计」行** —— 拿合计行当单层值会把面积和用量放大 **3 倍**（层数倍），非常隐蔽。
- 这些 xlsx 用 openpyxl 直接开会报 `ValueError: Colors must be aRGB hex values`。需先修 `xl/styles.xml`（把 `rgb` 规范成 8 位十六进制、去掉 `theme=` / `indexed=`），再用 `BytesIO` 打开。
- **YJK 不出模板量**，模板必须按定额计算规则手算（接触面积），别等 YJK 给。

---

## 顺序约束：混凝土 → 施工图 → 钢筋

这三段**顺序不能换**。上面分了两小节，容易被误读成"先后随意"，实际不是：

```
① 混凝土工程量（IDModule_Layer）  ← 必须最先
② 施工图出图（板/梁/柱/墙 绘新图）
③ 钢筋工程量（IDQUANTITYLIST_DETAIL）
```

> **底座已把整条链做成宏：`send @takeoff`**（见 `yjk_auto.py` 的 `TAKEOFF_CHAIN`）。
> 它是**唯一**推荐的下法 —— 顺序不靠"读者细心"，而是写死在链里；下面的分段说明是给你**查证与改动**用的。

根因：`yjkconcreteStat_statCom` 归属**建模模块**（`HelpRef = 楼层组装\18工程量统计`，不是 `IDQUANTITYLIST_DETAIL`）。切到 `IDModule_Layer` 会**冲掉施工图上下文** —— 若它排在出图链**之后**，后续所有 `DtlRC_*` 命令退化成 `OK(0.0s)` 且**不产出任何文件、也不报错**。症状极具欺骗性："命令全成功，Excel 一个都没有"。

> 说明：`yjkconcreteStat_statCom` **不是**空操作 —— 但它只在 `IDModule_Layer` 标签下有效；挂在 `IDQUANTITYLIST_DETAIL` 下会退化成 `OK(0.0s)` 零产出。判断一条命令是否有效时，先确认标签对不对。

### ① 混凝土工程量

```python
CONC_CHAIN = [("SetCurrentLabel", "IDModule_Layer"),        # 「楼层组装」＝建模模块
              ("yjkconcreteStat_statCom", "")]              # 统计并显示上部结构的工程量
```

产物 `<工程目录>\计算书\工程量统计\工程量统计.ini`（**GBK**，不是 UTF-16）：

```ini
[INFO]
VERSION=7.1.0
Gcl-Hnt-ZrcNum=3            ; 混凝土统计的自然层数
Gcl-Steel-ZrcNum=0          ; 钢结构统计的自然层数
RC-SLAB-FLOORNUM=3 / RC-BEAM-FLOORNUM=3 / RC-COLUMN-FLOORNUM=3 / RC-WALL-FLOORNUM=3

[Gcl-Hnt-Zrc1]              ; 第 1 自然层
Name=1
Cap=构件种类,个数,材料,材料级别,体积     ; 按列名取值才稳
Item-1=梁,76,6,30,140.448
Item-2=柱,45,6,40,105.840
Item-3=楼板,32,6,30,374.573
Item-Num=3
Item-Sum=620.861
```

材料代号：`6` = 混凝土；材料级别 `30` = C30。解析器见 `yjk-draw-takeoff/scripts/gcl_ini.py`。

口径校核（示例参数：3 层 / 45 柱 / 柱网 8.4×8.4m / 层高 4.8m，可作数量级参照）：

| 构件 | YJK | 手算 | 说明 |
|---|---|---|---|
| 柱 | 105.840 | 45 × 0.7×0.7 × 4.8 = **105.840** | 个数×截面×层高，精确相等 |
| 楼板 | 374.573 | 净板面积 ≈2081 m² × 0.18 = **374.6** | **扣梁占位后的净体积**，不是模型板面积 2288.25 |
| 梁 | 140.448 | 梁净长（扣柱） | 与手算口径一致 |

全楼 3 层合计 **1862.583 m³**（梁 421.344 / 柱 317.520 / 楼板 1123.719）。

### ② 施工图出图（板 / 梁 / 柱 / 墙）

```python
SLAB_CHAIN = [("SetCurrentLabel", "IDDTL_DETAIL_SLAB"),
              ("StdSlab_RedrawNceng", ""), ("StdSlab_AUTOCAL", ""),
              ("StdSlab_batgenstl", ""), ("stdslab_AutoStatstl", "")]
BEAM_CHAIN = [("SetCurrentLabel", "IDDTL_DETAIL_BEAM"),
              ("DtlRC_RegenReinsUpdateBeamPlan", "")]   # 使用已有连续梁组重选钢筋并更新图面
COL_CHAIN  = [("SetCurrentLabel", "IDDTL_DETAIL_COLUMN"),
              ("DtlRC_DrawNewColPlan", "")]             # 柱「绘新图」
WALL_CHAIN = [("SetCurrentLabel", "IDDTL_DETAIL_WALL"),
              ("DtlRC_WallPlanRegenNew", "")]           # 墙「重新归并选筋并绘制新图」
```

产物 `<工程目录>\施工图\`：DWG（典型 3 层模型约 20 个）—— `BeamPlan1` / `ColPlan1` / `WallT1` / `SlabPm1,2,3` / `SlabJt1,3` / `楼板弯矩|挠度|裂缝|计算面积简图1,2,3` 共 12 个）+ `SlabCalData*.txt` / `SlabCalPara*.txt` + `dtlRcBeam.ydb` / `dtlRcCol.ydb` / `dtlRcWall.ydb` / `dtlSlabPub.ydb` 等中间库。

### ③ 钢筋工程量（5 条，全楼口径）

```python
REBAR_CHAIN = [("SetCurrentLabel", "IDQUANTITYLIST_DETAIL"),
               ("DtlRC_SSSE", ""),                            # 板
               ("DtlRC_StatBuildingBeamSteelSpecExcel", ""),  # 梁
               ("DtlRC_SSCE", ""),                            # 柱
               ("DtlRC_SSWE", ""),                            # 墙
               ("dtlrc_ColSumGJ", "")]                        # 柱 txt 补充
```

### 确认为「空操作」的命令（别浪费时间）

同一标签 `IDQUANTITYLIST_DETAIL` 下，以下命令全部 `OK(0.0s)` 且零产出：

`DtlRC_SS`（全楼工程量汇总）、`DtlRC_AutoStat`、`DtlRC_AutoStatExcel`、`DtlRC_MpcAutoStatSteel`、`DtlRC_SSBE`、`DtlRC_SSB`、`DtlRC_SSW`、`DtlRC_STWBar`。

另：`yjkdesignexport_dsnQuantityStatisticsReport`（`IDDSN_DSP` 下）只写出 `SPara.par`，无用。

### 完整实现

可直接复用 **`yjk-draw-takeoff`** 技能（本技能的下游）：`scripts/draw_quant.py` 把「导入校验 → 预处理 → 计算 → 混凝土 → 施工图 → 钢筋 → 留档 → 汇总」整条串起来，`scripts/summary_xlsx.py` 出 6 页交付 Excel。
