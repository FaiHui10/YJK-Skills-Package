# 命令登记表（施工图 + 工程量统计）

只登记本技能实际用到的命令。底座（启动/导入/计算）见 `yjk-auto-drive/references/commands.md`。

---

## 一、执行顺序（不可换）

```
导入(yjk_importydb, 绝对路径) → yjk_save → ★导入校验
→ 预处理 → 计算 → 设计结果/
→ ① 混凝土工程量（IDModule_Layer）
→ ② 施工图出图（板 → 梁 → 柱 → 墙）
→ ③ 钢筋工程量（IDQUANTITYLIST_DETAIL）
```

顺序不能换的原因：`yjkconcreteStat_statCom` 归属**建模模块**（`IDModule_Layer`），切过去会冲掉
施工图上下文。它若排在②之后，③里所有 `DtlRC_*` 会退化成 `OK(0.0s)` 且零产出、零报错。

---

## 二、命令明细

### ① 混凝土工程量

| 命令 | 标签 | 耗时 | 产物 |
|---|---|---|---|
| `yjkconcreteStat_statCom` | `IDModule_Layer` | ~20s | `计算书/工程量统计/工程量统计.ini` |

- `HelpString` = 统计并显示上部结构的工程量
- `HelpRef` = `楼层组装\18工程量统计`（这就是它属于建模模块的证据）
- 文件为 GBK 编码，`Cap=` 行给出列名（`构件种类,个数,材料,材料级别,体积`）
- 材料代号：`6` = 混凝土；级别 `30` = C30

### ② 施工图出图

| 命令 | 标签 | 说明 | 主要产物 |
|---|---|---|---|
| `StdSlab_RedrawNceng` | `IDDTL_DETAIL_SLAB` | 板-绘新图 | `DSevData_*.xml`×19 |
| `StdSlab_AUTOCAL` | （沿用） | 板-计算 | `SlabCalData*.txt` / `SlabCalPara*.txt` |
| `StdSlab_batgenstl` | （沿用） | 板-批量出图（**会弹模态框**） | `SlabPm1-3.dwg` / `SlabJt1,3.dwg` |
| `stdslab_AutoStatstl` | （沿用） | ★ 板-全楼钢筋统计 | `全楼楼板钢筋用量.dat` / `SlabStlQuantity1.dat` |
| `DtlRC_RegenReinsUpdateBeamPlan` | `IDDTL_DETAIL_BEAM` | 梁-用已有连续梁组重选钢筋并更新图面 | `BeamPlan1.dwg` |
| `DtlRC_DrawNewColPlan` | `IDDTL_DETAIL_COLUMN` | 柱-绘新图 | `ColPlan1.dwg` |
| `DtlRC_WallPlanRegenNew` | `IDDTL_DETAIL_WALL` | 墙-重新归并选筋并绘新图 | `WallT1.dwg` |

合计约 **20 个 DWG**（随层数增减）：`BeamPlan1` / `ColPlan1` / `WallT1` / `SlabPm1,2,3` / `SlabJt1,3` /
`楼板弯矩简图1-3` / `楼板挠度简图1-3` / `楼板裂缝简图1-3` / `楼板计算面积简图1-3`。

> `StdSlab_batgenstl` 会弹「施工图已经进行过选筋,是否重新选筋?」—— 模态期间主窗口被 Disable，
> IPC **永不返回**。必须由 `dlgwatch.DialogWatch` 回「否」。

### ③ 钢筋工程量

| 命令 | 标签 | 构件 | 产物 |
|---|---|---|---|
| `DtlRC_SSSE` | `IDQUANTITYLIST_DETAIL` | 板 | `施工图/全楼楼板钢筋用量.xlsx` |
| `DtlRC_StatBuildingBeamSteelSpecExcel` | （沿用） | 梁 | `施工图/全楼梁钢筋用量(钢筋规格与类别).xlsx` |
| `DtlRC_SSCE` | （沿用） | 柱 | `施工图/全楼柱钢筋用量(钢筋规格与类别).xlsx` |
| `DtlRC_SSWE` | （沿用） | 墙 | `施工图/全楼墙钢筋用量(钢筋规格与类别).xlsx` |
| `dtlrc_ColSumGJ` | （沿用） | 柱 | `施工图/柱钢筋统计.txt`（补充） |

### 空操作命令 —— 不要用

在 `IDQUANTITYLIST_DETAIL` 下这些命令全部 `OK(0.0s)`、零产出：

`DtlRC_SS`、`DtlRC_AutoStat`、`DtlRC_AutoStatExcel`、`DtlRC_MpcAutoStatSteel`、
`DtlRC_SSBE`、`DtlRC_SSB`、`DtlRC_SSW`、`DtlRC_STWBar`、`StdSlab_Quantity`（只出本层）、
`StdSlab_RESELECTREIN`（只弹框）。

`yjkdesignexport_dsnQuantityStatisticsReport`（`IDDSN_DSP`）只写 `SPara.par`，无用。

---

## 三、钢筋表布局（读表必看）

| 构件 | 尺寸 | 直径行列号 | 直径值 | 合计行 |
|---|---|---|---|---|
| 板 | 9 行 × 11 列 | 第 3 行（第 4~9 列） | 6,8,10,14,16,18 | r7 `合计` |
| 梁 | 21 行 × 15 列 | 第 3 行（第 4~12 列） | 6,8,12,18,20,22,25,28,32 | r19 `全楼` |
| 柱 | 13 行 × 9 列 | 第 3 行（第 4~6 列） | 8,18,20 | r11 `全楼` |
| 墙 | 6 行 × 6 列 | — | — | r4 `全楼`/`总计`（无墙时合法为 0） |

**三个要点**

1. **直径行在表头行的下一行**。表头行只有合并的 `'HRB400'` 标题，没有数字。
2. **表尾有一行只重复总计数字**（板 r8 / 梁 r20 / 柱 r12），第一列是空的 ——
   不能用"第一个数字行"当合计。
3. **不能用「包含」匹配** —— 板标题行 `['', '全楼楼板钢筋用量', …]` 含「全楼」，
   会被误当合计行（该行直径列全空 → 读成 0，伪装成"统计未生效"）。
   必须让**楼层列（索引 1）精确等于** `全楼` / `合计` / `总计`。

实现见 `scripts/summary_xlsx.parse_rebar()`。

---

## 四、编码与读取

| 文件 | 编码 | 读法 |
|---|---|---|
| `工程量统计.ini` | **GBK** | 直读，`Cap=` 给列名 |
| `全楼*钢筋用量*.xlsx` | — | **不能**直接 openpyxl 开（`Colors must be aRGB hex values`）→ 先修 `xl/styles.xml`，见 `read_yjk_xlsx.py` |
| `设计结果/wpj*.out` | **GBK** | 逐柱文本 |
| `YJK.CUI` | **UTF-8**（不是 GBK！） | 按 GBK 读会得到 `鍥惧眰璁剧疆` 这类乱码 |

---

## 五、工作量参考

典型参数（3 层 / 45 柱 / 76 梁 / 32 板，柱网 8.4×8.4m，层高 4.8m）：

```
预处理 + 计算                 ~55s
① 混凝土统计                  ~20s
② 施工图出图（20 DWG）         ~35s
③ 钢筋统计（4 表 + 1 txt）      ~5s
----------------------------------
合计                           约 1 分 55 秒
```

模态框看门狗留档应为 **0 条错误**。若 `watch.errors` 非空，先读它再读别的。
