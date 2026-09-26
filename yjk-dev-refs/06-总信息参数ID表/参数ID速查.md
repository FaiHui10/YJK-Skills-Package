# 前处理计算参数 —— 参数ID速查

> **本文档是二次开发时最常查的一张表。**
> 全部 `#define` 均**逐字转录**自官方头文件说明 `06-总信息参数ID表/前处理计算参数宏定义.md`
> （原文件来源：gitee 仓库 `yjk-opensource/csharp-yjks`，说明文档目录）。
> 宏名、数值、枚举序号、中文注释一律保持原文，**未做任何改写、补全或“纠错”**。
> 原文中确有的笔误与重复值已在末尾《原文疑似笔误》一节中如实列出，正文保留原样。

---

## 一、编码规则（必读）

```c
#define YP_RES_SIZE		100
```

### ⭐ 参数值 = 参数ID × 100 + 枚举序号

原文用宏把这条规则写死了：

```c
// 参数ID宏：参数号本身
#define YP_JGTX				101		// 结构体系
// 枚举值宏：参数ID * YP_RES_SIZE + 枚举序号
#define YPV_KJIA		 (YP_JGTX*YP_RES_SIZE+1)	// 框架结构
#define YPV_KJIAN		 (YP_JGTX*YP_RES_SIZE+2)	// 框剪结构
```

展开后：

- `YPV_KJIA`  = `101 * 100 + 1` = **10101** → 结构体系 = 框架结构
- `YPV_KJIAN` = `101 * 100 + 2` = **10102** → 结构体系 = 框剪结构
- `YPV_SFLD_8` = `302 * 100 + 4` = **30204** → 设防烈度 = 8 度 (0.2g)

也就是说：**参数ID 是“哪一个参数”，`ID*100+n` 是“该参数的第 n 个选项”。**
每个参数预留 **100** 个枚举槽位（`YP_RES_SIZE`），所以枚举序号只用到 1~99。

### 用法

官方 Python 案例 `02-Python-API案例/案例14_前处理计算参数设置/kj.py` 里的写法：

```python
from YJKAPI import *
dataFunc = DataFunc()
# 截面形状：228 是参数ID，22804 = 228*100+4 -> 圆形
dataFunc.ProjectPara_Set(228, "22804")
# 考虑横风向风振：布尔型参数直接给值
dataFunc.ProjectPara_Set(207, "1")
```

规则小结：

| 参数类型 | 传什么值 | 例 |
|---|---|---|
| **选项型**（原文给出 `YPV_*` 枚举的） | `参数ID × 100 + 枚举序号` | `22804` = 截面形状→圆形 |
| **数值/布尔型**（原文只给 `YP_*`，无 `YPV_*`） | 直接给实际数值 | `207` ← `"1"`（考虑横风向风振） |
| **数组型**（原文注明 int/float 数组） | 串成逗号分隔字符串，首位通常是数组大小 | `ProjectPara_Set(213, "2,3,4,6")` |

> 上表中“传什么值”的列依据原文宏定义与官方案例 14 的实际调用；数组约定见原文各参数注释（大量参数标注了
> `data[0]存数组大小` 之类）。具体 API 名称随 SDK 版本而变（C# 为 `yjkSetSPara`/`CSParaData` 一族，
> Python 为 `DataFunc.ProjectPara_Set`），但**ID 与取值编码是同一套**。

---

## 二、常用参数速查（高频 21 项）

以下宏名、参数含义、枚举中文注释**逐字取自原文**；“应传的值”一列是按上述规则
`参数ID × 100 + 枚举序号` 展开得到的整数。

### 基本信息

| 参数ID | 宏名 | 参数含义 | 应传的值 |
|---|---|---|---|
| 101 | `YP_JGTX` | 结构体系 | `10101`（`YPV_KJIA` → 框架结构） |
| 101 | `YP_JGTX` | 结构体系 | `10102`（`YPV_KJIAN` → 框剪结构） |
| 101 | `YP_JGTX` | 结构体系 | `10103`（`YPV_KTONG` → 框筒结构） |
| 101 | `YP_JGTX` | 结构体系 | `10104`（`YPV_TZT` → 筒中筒结构） |
| 101 | `YP_JGTX` | 结构体系 | `10105`（`YPV_JLQ` → 剪力墙结构） |
| 104 | `YP_QFCS` | 裙房层数 | 直接给数值（无枚举） |
| 105 | `YP_ZHC` | 转换层号 | 直接给数值（无枚举） |
| 106 | `YP_DXS` | 地下室层数 | 直接给数值（无枚举） |
| 107 | `YP_JQC` | 加强层所在层号 | 直接给数值（无枚举） |
| 108 | `YP_KGC` | 嵌固端所在层号 | 直接给数值（无枚举） |

- **结构体系（`YP_JGTX`）**：…枚举共 43 项（框架-支撑、门刚、PEC、BCFT、光伏支架等），全表见第三节。
- **裙房层数（`YP_QFCS`）**：标量。
- **转换层号（`YP_ZHC`）**：标量。
- **地下室层数（`YP_DXS`）**：标量。
- **加强层所在层号（`YP_JQC`）**：标量。
- **嵌固端所在层号（`YP_KGC`）**：标量。

### 风荷载信息

| 参数ID | 宏名 | 参数含义 | 应传的值 |
|---|---|---|---|
| 201 | `YP_DMCCD` | 地面粗糙度类别 | `20101`（`YPV_DMCCD_A` → A） |
| 201 | `YP_DMCCD` | 地面粗糙度类别 | `20102`（`YPV_DMCCD_B` → B） |
| 201 | `YP_DMCCD` | 地面粗糙度类别 | `20103`（`YPV_DMCCD_C` → C） |
| 201 | `YP_DMCCD` | 地面粗糙度类别 | `20104`（`YPV_DMCCD_D` → D） |
| 202 | `YP_JBFY` | 修正后的基本风压（kN/m2） | 直接给数值（无枚举） |
| 203 | `YP_JBZQX` | 结构X向基本周期（s） | 直接给数值（无枚举） |
| 204 | `YP_JBZQY` | 结构Y向基本周期（s） | 直接给数值（无枚举） |

- **修正后的基本风压（kN/m2）（`YP_JBFY`）**：数值，单位 kN/m²。
- **结构X向基本周期（s）（`YP_JBZQX`）**：数值，单位 s。
- **结构Y向基本周期（s）（`YP_JBZQY`）**：数值，单位 s。

### 地震信息

| 参数ID | 宏名 | 参数含义 | 应传的值 |
|---|---|---|---|
| 302 | `YP_SFLD` | 设防烈度 | `30201`（`YPV_SFLD_6` → 6 (0.05g)） |
| 302 | `YP_SFLD` | 设防烈度 | `30202`（`YPV_SFLD_7` → 7 (0.1g)） |
| 302 | `YP_SFLD` | 设防烈度 | `30203`（`YPV_SFLD_75` → 7 (0.15g)） |
| 302 | `YP_SFLD` | 设防烈度 | `30204`（`YPV_SFLD_8` → 8 (0.2g)） |
| 302 | `YP_SFLD` | 设防烈度 | `30205`（`YPV_SFLD_85` → 8 (0.3g)） |
| 302 | `YP_SFLD` | 设防烈度 | `30206`（`YPV_SFLD_9` → 9 (0.4g)） |
| 303 | `YP_CDLB` | 场地类别 | `30301`（`YPV_CD_I0` → I0） |
| 303 | `YP_CDLB` | 场地类别 | `30302`（`YPV_CD_I1` → I1） |
| 303 | `YP_CDLB` | 场地类别 | `30303`（`YPV_CD_II` → II） |
| 303 | `YP_CDLB` | 场地类别 | `30304`（`YPV_CD_III` → III） |
| 303 | `YP_CDLB` | 场地类别 | `30305`（`YPV_CD_IV` → VI） |
| 303 | `YP_CDLB` | 场地类别 | `30306`（`YPV_CD_SH` → 上海(建模用?)） |
| 304 | `YP_ORPX` | 考虑偶然偏心 | 直接给数值（无枚举） |
| 307 | `YP_SXDZ` | 考虑双向地震作用 | 直接给数值（无枚举） |
| 310 | `YP_ZQZJ` | 周期折减系数 | 直接给数值（无枚举） |
| 312 | `YP_TG` | 特征周期Tg（s） | 直接给数值（无枚举） |
| 313 | `YP_AMAX` | 多遇地震影响系数最大值 | 直接给数值（无枚举） |
| 314 | `YP_AMAXHY` | 罕遇地震影响系数最大值 | 直接给数值（无枚举） |

- **场地类别（`YP_CDLB`）**：原文 30305 的枚举注释写作 `VI`（宏名为 `YPV_CD_IV`），此处逐字保留；语义即 IV 类场地。
- **考虑偶然偏心（`YP_ORPX`）**：布尔/选项。
- **考虑双向地震作用（`YP_SXDZ`）**：布尔/选项。
- **周期折减系数（`YP_ZQZJ`）**：数值。
- **特征周期Tg（s）（`YP_TG`）**：数值，单位 s。
- **多遇地震影响系数最大值（`YP_AMAX`）**：数值（αmax，多遇）。
- **罕遇地震影响系数最大值（`YP_AMAXHY`）**：数值（αmax，罕遇）。

### 设计信息

| 参数ID | 宏名 | 参数含义 | 应传的值 |
|---|---|---|---|
| 701 | `YP_KJKZDJ` | 框架抗震等级 | `70101`（`YPV_KZDJ_T1` → 特一级） |
| 701 | `YP_KJKZDJ` | 框架抗震等级 | `70102`（`YPV_KZDJ_1` → 一级） |
| 701 | `YP_KJKZDJ` | 框架抗震等级 | `70103`（`YPV_KZDJ_2` → 二级） |
| 701 | `YP_KJKZDJ` | 框架抗震等级 | `70104`（`YPV_KZDJ_3` → 三级） |
| 701 | `YP_KJKZDJ` | 框架抗震等级 | `70105`（`YPV_KZDJ_4` → 四级） |
| 701 | `YP_KJKZDJ` | 框架抗震等级 | `70106`（`YPV_KZDJ_NO` → 非抗震） |
| 702 | `YP_GKJKZDJ` | 钢框架抗震等级 | `70101`（`YPV_KZDJ_T1` → 特一级） |
| 702 | `YP_GKJKZDJ` | 钢框架抗震等级 | `70102`（`YPV_KZDJ_1` → 一级） |
| 702 | `YP_GKJKZDJ` | 钢框架抗震等级 | `70103`（`YPV_KZDJ_2` → 二级） |
| 702 | `YP_GKJKZDJ` | 钢框架抗震等级 | `70104`（`YPV_KZDJ_3` → 三级） |
| 702 | `YP_GKJKZDJ` | 钢框架抗震等级 | `70105`（`YPV_KZDJ_4` → 四级） |
| 702 | `YP_GKJKZDJ` | 钢框架抗震等级 | `70106`（`YPV_KZDJ_NO` → 非抗震） |
| 703 | `YP_JLQKZDJ` | 剪力墙抗震等级 | `70101`（`YPV_KZDJ_T1` → 特一级） |
| 703 | `YP_JLQKZDJ` | 剪力墙抗震等级 | `70102`（`YPV_KZDJ_1` → 一级） |
| 703 | `YP_JLQKZDJ` | 剪力墙抗震等级 | `70103`（`YPV_KZDJ_2` → 二级） |
| 703 | `YP_JLQKZDJ` | 剪力墙抗震等级 | `70104`（`YPV_KZDJ_3` → 三级） |
| 703 | `YP_JLQKZDJ` | 剪力墙抗震等级 | `70105`（`YPV_KZDJ_4` → 四级） |
| 703 | `YP_JLQKZDJ` | 剪力墙抗震等级 | `70106`（`YPV_KZDJ_NO` → 非抗震） |

- **框架抗震等级（`YP_KJKZDJ`）**：原文只在 701 下定义了 `YPV_KZDJ_*` 这一套取值宏。
- **钢框架抗震等级（`YP_GKJKZDJ`）**：702 在原文中**没有**自己的枚举宏定义。
- **剪力墙抗震等级（`YP_JLQKZDJ`）**：703 在原文中**没有**自己的枚举宏定义。

> ### ★★ 702 / 703 的取值列**不是** `702xx / 703xx`，而是**共用 701 的枚举基**
>
> 原文只在 `YP_KJKZDJ`(701) 下给出了 `YPV_KZDJ_*`（特一/一/二/三/四级/非抗震）这一套枚举宏，
> 702 `YP_GKJKZDJ` 与 703 `YP_JLQKZDJ` **没有**各自成组的枚举宏。
>
> **按"参数ID × 100 + 枚举序号"机械推导会得到 `70303 = 二级`，这是错的。**
> 实测（本机 YJKS_7_1_0，用"改一行 `tblProjectPara` → 跑一轮实算 → 回读 `wmass.out`
> 的「设计参数输出」"逐条核对，并用二分法定位到 ID）：
>
> | 需求 | `tblProjectPara` 里真正要写的值 | wmass.out 回读结果 |
> |---|---|---|
> | 剪力墙抗震等级 = 二级 | `ID=703  →  "70103"` | `剪力墙的抗震等级: 2` ✓ |
> | 剪力墙抗震等级 = 三级（YJK 默认） | `ID=703  →  "70104"` | `剪力墙的抗震等级: 3` ✓ |
>
> 也就是说：**等级族（701/702/703）共用同一套枚举码 `70101…70106`，
> 区别只在"写哪一行 ID"。** 本表 702/703 两列已按实测结果修正。
>
> 结论同样适用于其它"同一族参数共用取值宏"的情形：**文档给的是宏定义，
> 落库值要以实算回读为准**。技能包里的 `yjk-auto-drive/scripts/projpara.py`
> 已把这条规则固化为 `ENUM_BASE`，并用 `projpara.py check` 做回读校验。

---

## 三、全部参数ID（按原文分节逐字转录）

分组标题即原文的分节注释行，**逐字保留**。表格列含义：

- **宏名**：`#define` 的名字，原样
- **取值**：原文的数值（参数ID），或原文的取值表达式（枚举）
- **= 实际值**：按 `参数ID*100+序号` 展开后的整数
- **原文注释**：`//` 之后的原文注释，原样

### 1. 基本信息

原文节注释行（逐字）：

```c
//////////////////////////////////////////////////////////////////////////
//	基本信息
```

| 宏名 | 取值 | = 实际值 | 原文注释 |
|---|---|---|---|
| `YP_RES_SIZE` | `100` | 100 |  |
| `YP_JGTX` | `101` | 101 | 结构体系 |
| ↳ `YPV_KJIA` | `( YP_JGTX*YP_RES_SIZE+1 )` | 10101 | 框架结构 |
| ↳ `YPV_KJIAN` | `( YP_JGTX*YP_RES_SIZE+2 )` | 10102 | 框剪结构 |
| ↳ `YPV_KTONG` | `( YP_JGTX*YP_RES_SIZE+3 )` | 10103 | 框筒结构 |
| ↳ `YPV_TZT` | `( YP_JGTX*YP_RES_SIZE+4 )` | 10104 | 筒中筒结构 |
| ↳ `YPV_JLQ` | `( YP_JGTX*YP_RES_SIZE+5 )` | 10105 | 剪力墙结构 |
| ↳ `YPV_KZJLQ` | `( YP_JGTX*YP_RES_SIZE+6 )` | 10106 | 框支剪力墙结构 |
| ↳ `YPV_BZJLQ` | `( YP_JGTX*YP_RES_SIZE+7 )` | 10107 | 板柱-剪力墙结构 |
| ↳ `YPV_YXZKJIA` | `( YP_JGTX*YP_RES_SIZE+8 )` | 10108 | 异形柱框架结构 |
| ↳ `YPV_YXZKJIAN` | `( YP_JGTX*YP_RES_SIZE+9 )` | 10109 | 异形柱框剪结构 |
| ↳ `YPV_QK` | `( YP_JGTX*YP_RES_SIZE+10 )` | 10110 | 配筋砌块砌体结构 |
| ↳ `YPV_QT` | `( YP_JGTX*YP_RES_SIZE+11 )` | 10111 | 砌体结构 |
| ↳ `YPV_DK` | `( YP_JGTX*YP_RES_SIZE+12 )` | 10112 | 底框结构 |
| ↳ `YPV_GKJZX` | `( YP_JGTX*YP_RES_SIZE+13 )` | 10113 | 钢框架-中心支撑结构 |
| ↳ `YPV_GKJPX` | `( YP_JGTX*YP_RES_SIZE+14 )` | 10114 | 钢框架-偏心支撑结构 |
| ↳ `YPV_DANCCF` | `( YP_JGTX*YP_RES_SIZE+15 )` | 10115 | 单层工业厂房 |
| ↳ `YPV_DUOCCF` | `( YP_JGTX*YP_RES_SIZE+16 )` | 10116 | 多层钢结构厂房 |
| ↳ `YPV_SXKPJ` | `( YP_JGTX*YP_RES_SIZE+17 )` | 10117 | 竖向框排架 |
| ↳ `YPV_TUS_JLQ` | `( YP_JGTX*YP_RES_SIZE+18 )` | 10118 | TUS剪力墙结构 |
| ↳ `YPV_ETOWER` | `( YP_JGTX*YP_RES_SIZE+19 )` | 10119 | 变电构架结构 |
| ↳ `YPV_GREENHOUSE` | `( YP_JGTX*YP_RES_SIZE+20 )` | 10120 | 温室结构 |
| ↳ `YPV_DCLWBBFW` | `( YP_JGTX*YP_RES_SIZE+21 )` | 10121 | 低层冷弯薄壁房屋 |
| ↳ `YPV_BWGBZHKJ` | `( YP_JGTX*YP_RES_SIZE+22 )` | 10122 | 波纹钢板组合框架 |
| ↳ `YPV_BWGBZHKJZC` | `( YP_JGTX*YP_RES_SIZE+23 )` | 10123 | 波纹钢板组合框架-支撑 |
| ↳ `YPV_QKZJLQ` | `( YP_JGTX*YP_RES_SIZE+24 )` | 10124 | 全框支剪力墙结构 |
| ↳ `YPV_JXZZHKJ_YJ` | `( YP_JGTX*YP_RES_SIZE+25 )` | 10125 | 矩形柱组合框架结构(渝建) |
| ↳ `YPV_JXZZHKJZC_YJ` | `( YP_JGTX*YP_RES_SIZE+26 )` | 10126 | 矩形柱组合框架结构_支撑(渝建) |
| ↳ `YPV_MENGANG` | `( YP_JGTX*YP_RES_SIZE+27 )` | 10127 | 门式刚架结构 |
| ↳ `YPV_GFZJ` | `( YP_JGTX*YP_RES_SIZE+28 )` | 10128 | 光伏支架结构 |
| ↳ `YPV_GHNTZHGJLQ` | `( YP_JGTX*YP_RES_SIZE+29 )` | 10129 | 钢混凝土组合管剪力墙结构 |
| ↳ `YPV_KJGHNTZHGJLQ` | `( YP_JGTX*YP_RES_SIZE+30 )` | 10130 | 框架钢混凝土组合管剪力墙结构 |
| ↳ `YPV_NKJ` | `( YP_JGTX*YP_RES_SIZE+31 )` | 10131 | 内框架结构 |
| ↳ `YPV_BCFTCCKJ` | `( YP_JGTX*YP_RES_SIZE+32 )` | 10132 | BCFT组合柱框架结构 |
| ↳ `YPV_BCFTCCKJ_ZC` | `( YP_JGTX*YP_RES_SIZE+33 )` | 10133 | BCFT组合柱框架-支撑结构 |
| ↳ `YPV_BCFTCCKJ_GBQ` | `( YP_JGTX*YP_RES_SIZE+34 )` | 10134 | BCFT组合柱框架-钢板墙结构 |
| ↳ `YPV_BCFTCCKJ_JLQ` | `( YP_JGTX*YP_RES_SIZE+35 )` | 10135 | BCFT组合柱框架-剪力墙结构 |
| ↳ `YPV_BCFTCJLQ` | `( YP_JGTX*YP_RES_SIZE+36 )` | 10136 | BCFT组合剪力墙结构 |
| ↳ `YPV_GZCHNTKJ` | `( YP_JGTX*YP_RES_SIZE+37 )` | 10137 | 钢支撑-混凝土框架结构 |
| ↳ `YPV_PECKJ` | `( YP_JGTX*YP_RES_SIZE+38 )` | 10138 | PEC框架结构 |
| ↳ `YPV_PECKJJLQ` | `( YP_JGTX*YP_RES_SIZE+39 )` | 10139 | PEC框架剪力墙结构 |
| ↳ `YPV_PECJLQ` | `( YP_JGTX*YP_RES_SIZE+40 )` | 10140 | PEC剪力墙结构 |
| ↳ `YPV_PECKJZC` | `( YP_JGTX*YP_RES_SIZE+41 )` | 10141 | PEC框架支撑结构 |
| ↳ `YPV_PECKJ_GJHNTJLQ` | `( YP_JGTX*YP_RES_SIZE+42 )` | 10142 | PEC框架-钢筋混凝土剪力墙结构 |
| ↳ `YPV_PECKJ_GJHNTHXT` | `( YP_JGTX*YP_RES_SIZE+43 )` | 10143 | PEC框架-钢筋混凝土核心筒结构 |
| `YP_AREA` | `102` | 102 | 结构所在地区 |
| ↳ `YPV_AREA_CN` | `( YP_AREA*YP_RES_SIZE+1 )` | 10201 | 全国 |
| ↳ `YPV_AREA_GD` | `( YP_AREA*YP_RES_SIZE+2 )` | 10202 | 广东 |
| ↳ `YPV_AREA_SH` | `( YP_AREA*YP_RES_SIZE+3 )` | 10203 | 上海 |
| ↳ `YPV_AREA_B89CN` | `( YP_AREA*YP_RES_SIZE+4 )` | 10204 | B类建筑（89规范全国） |
| ↳ `YPV_AREA_B89SH` | `( YP_AREA*YP_RES_SIZE+5 )` | 10205 | B类建筑（89规范上海） |
| ↳ `YPV_AREA_A` | `( YP_AREA*YP_RES_SIZE+6 )` | 10206 | A类建筑 |
| ↳ `YPV_AREA_GD2020` | `( YP_AREA*YP_RES_SIZE+7 )` | 10207 | 新版广东高规 |
| ↳ `YPV_AREA_SZ` | `( YP_AREA*YP_RES_SIZE+8 )` | 10208 | 深圳高规 |
| ↳ `YPV_AREA_SH2023` | `( YP_AREA*YP_RES_SIZE+9 )` | 10209 | 上海抗规 2023 |
| `YP_JGCL` | `103` | 103 | 结构材料 |
| ↳ `YPV_CL_GJHNT` | `( YP_JGCL*YP_RES_SIZE+1 )` | 10301 | 钢筋混凝土 |
| ↳ `YPV_CL_G_HNT` | `( YP_JGCL*YP_RES_SIZE+2 )` | 10302 | 钢与混凝土混合结构 |
| ↳ `YPV_CL_G` | `( YP_JGCL*YP_RES_SIZE+3 )` | 10303 | 钢结构 |
| ↳ `YPV_CL_QTJG` | `( YP_JGCL*YP_RES_SIZE+4 )` | 10304 | 砌体结构 |
| `YP_QFCS` | `104` | 104 | 裙房层数 |
| `YP_ZHC` | `105` | 105 | 转换层号 |
| `YP_DXS` | `106` | 106 | 地下室层数 |
| `YP_JQC` | `107` | 107 | 加强层所在层号 |
| `YP_KGC` | `108` | 108 | 嵌固端所在层号 |
| `YP_FIXELE` | `109` | 109 | 与基础相连最大构件底标高 |
| `YP_NJQC` | `110` | 110 | 加强层所在层号数 |
| `YP_IJQC` | `111` | 111 | 加强层所在层号(数组) |
| `YP_JS_SCFX` | `112` | 112 | 是否弹性时程分析 |
| `YP_JS_WDHZ` | `113` | 113 | 计算温度荷载 |
| `YP_JS_DZX` | `114` | 114 | 生成绘等值线用节点应力数据 (0~1) 默认0 |
| `YP_WDZJXS` | `115` | 115 | 考虑收缩徐变的混凝土构件温度效应折减系数 (0.1, 1) 默认0.3 |
| `YP_JS_JCGDFLR` | `116` | 116 | 选中生成传给基础的刚度时，凝聚局部楼层刚度时考虑的底部层数，0表示全部楼层 （0~n） n为楼层数 |
| `YP_REGULARFLR` | `117` | 117 | 采用普通方式楼层组装(未采用广义层方式) (0~1) 默认0 |
| `YP_ESLABLOAD` | `118` | 118 | 弹性楼板荷载计算方式(默认1) |
| ↳ `YPV_ESLABLOAD_TRANS` | `( YP_ESLABLOAD*YP_RES_SIZE+1 )` | 11801 | 平面导荷 |
| ↳ `YPV_ESLABLOAD_FEA` | `( YP_ESLABLOAD*YP_RES_SIZE+2 )` | 11802 | 有限元计算 |
| `YP_LLWAC` | `119` | 119 | 按普通梁建模的连梁材料强度同墙(默认1) |
| `YP_ESLABCOND` | `120` | 120 | 弹性板单元是否凝聚(默认1) |
| `YP_TLOPT1` | `121` | 121 | 楼板导荷边被打断时荷载类型简化为均布(默认1) |
| `YP_QGDKLXBSS` | `122` | 122 | 砼墙轴向刚度考虑徐变、收缩的影响  (默认0) |
| `YP_QGDZJXS` | `123` | 123 | 墙轴向刚度折减系数（默认0.6） |
| `YP_JSKLJC` | `124` | 124 | 上部结构计算考虑基础结构 |
| `YP_JSKLYYL` | `125` | 125 | 考虑预应力等效荷载工况 |
| `YP_TYGF` | `126` | 126 | 采用通用规范 |
| `YP_JS_KFHZGK` | `127` | 127 | 生成抗浮恒载工况（结构自重、其他荷载） |
| `YP_WDZJXS_HHGJ` | `128` | 128 | 考虑收缩徐变的混合构件温度效应折减系数 (0.1, 1) 默认1 240520wx |
| `YP_IS_100YEAR` | `129` | 129 | 是否执行《百年住宅建筑设计规程》 |
| `YP_SJNX` | `130` | 130 | 设计年限 70年or100年 |
| ↳ `YPV_SJNF_70` | `( YP_SJNX*YP_RES_SIZE+1 )` | 13001 | 70年 |
| ↳ `YPV_SJNF_100` | `( YP_SJNX*YP_RES_SIZE+2 )` | 13002 | 100年 |
| `YP_IS_HNTJGSJBZ` | `131` | 131 | 是否执行《混凝土结构设计标准》 |

### 2. 风荷载信息

原文节注释行（逐字）：

```c
//////////////////////////////////////////////////////////////////////////
//	风荷载信息
```

| 宏名 | 取值 | = 实际值 | 原文注释 |
|---|---|---|---|
| `YP_DMCCD` | `201` | 201 | 地面粗糙度类别 |
| ↳ `YPV_DMCCD_A` | `( YP_DMCCD*YP_RES_SIZE+1 )` | 20101 | A |
| ↳ `YPV_DMCCD_B` | `( YP_DMCCD*YP_RES_SIZE+2 )` | 20102 | B |
| ↳ `YPV_DMCCD_C` | `( YP_DMCCD*YP_RES_SIZE+3 )` | 20103 | C |
| ↳ `YPV_DMCCD_D` | `( YP_DMCCD*YP_RES_SIZE+4 )` | 20104 | D |
| `YP_JBFY` | `202` | 202 | 修正后的基本风压（kN/m2） |
| `YP_JBZQX` | `203` | 203 | 结构X向基本周期（s） |
| `YP_JBZQY` | `204` | 204 | 结构Y向基本周期（s） |
| `YP_WINDZNB` | `205` | 205 | 风荷载计算用阻尼比 |
| `YP_FZXS` | `206` | 206 | 是否考虑风振系数 |
| `YP_HXFZ` | `207` | 207 | 是否考虑横风向风振 |
| `YP_WINDMG` | `208` | 208 | 对风荷载敏感的高层建筑(承载力计算时的风荷载内力放大) |
| `YP_NHORITX` | `209` | 209 | 水平风体型系数分段数(无用) |
| `YP_HORITXC` | `200` | 200 | 水平风体型系数分段层号(无用) |
| `YP_HORITX` | `211` | 211 | 水平风体型系数(无用) |
| `YP_NTSFTX` | `212` | 212 | 风荷载体型系数分段数 |
| `YP_TSFTXC` | `213` | 213 | 风荷载体型系数分段层号 |
| `YP_TSFTX` | `214` | 214 | 风荷载体型系数 |
| `YP_BFTX` | `215` | 215 | 设缝多塔背风面体型系数 |
| `YP_NDFXF` | `216` | 216 | 多方向风方向数 |
| `YP_DFXF` | `217` | 217 | 多方向风各方向角度 |
| `YP_TCQGJG` | `218` | 218 | 有填充墙钢结构 |
| `YP_SSDFY` | `219` | 219 | 用于舒适度验算的风压(kN/m2) |
| `YP_SSDWDZNB` | `220` | 220 | 用于舒适度验算的结构阻尼比(%) |
| `YP_WINDCODE` | `221` | 221 | 风荷载规范 |
| ↳ `YPV_WINDCODE_2002` | `( YP_WINDCODE*YP_RES_SIZE+1 )` | 22101 | 2002规范 |
| ↳ `YPV_WINDCODE_2012` | `( YP_WINDCODE*YP_RES_SIZE+2 )` | 22102 | 2012规范 |
| `YP_NZFZ` | `222` | 222 | 是否考虑扭转风振 |
| `YP_WINDHOLE` | `223` | 223 | 使用直接指定的风洞试验结果 |
| `YP_WINDHOLEDATA` | `224` | 224 | 风洞试验数据 |
| `YP_WINDDB` | `225` | 225 | 自动计算横扭风振使用的建筑尺寸 |
| `YP_WINDBX` | `226` | 226 | 指定的建筑X向宽度 |
| `YP_WINDBY` | `227` | 227 | 指定的建筑Y向宽度 |
| `YP_WINDSECT` | `228` | 228 | 截面形状 |
| ↳ `YPV_WINDSECT_RECT` | `( YP_WINDSECT*YP_RES_SIZE+1 )` | 22801 | 矩形 |
| ↳ `YPV_WINDSECT_AJRECT` | `( YP_WINDSECT*YP_RES_SIZE+2 )` | 22802 | 凹角矩形 |
| ↳ `YPV_WINDSECT_XJRECT` | `( YP_WINDSECT*YP_RES_SIZE+3 )` | 22803 | 削角矩形 |
| ↳ `YPV_WINDSECT_ROUND` | `( YP_WINDSECT*YP_RES_SIZE+4 )` | 22804 | 圆形 |
| `YP_WINDJYX` | `229` | 229 | X向角沿尺寸 |
| `YP_WINDJYY` | `230` | 230 | Y向角沿尺寸 |
| `YP_WINDT2` | `231` | 231 | 结构二阶平动周期(横向风振用) |
| `YP_WINDTT` | `232` | 232 | 结构一阶扭转周期(扭转风振用) |
| `YPE_VB` | `233` | 233 | (欧)基本风速(basic wind velocity) |
| `YPE_TERRAIN` | `234` | 234 | (欧)地形类别(terrain category)(共5类:0 Ⅰ Ⅱ Ⅲ Ⅳ) |
| `YPE_CPEORCF` | `235` | 235 | 20170607改为X向   YPE_CPEWINDY为Y向 |
| ↳ `YPEV_CPE` | `( YPE_CPEORCF*YP_RES_SIZE+1 )` | 23501 | 考虑外部压力系数(external pressure coefficient) |
| ↳ `YPEV_CF` | `( YPE_CPEORCF*YP_RES_SIZE+2 )` | 23502 | 考虑力系数cf(force coefficient) |
| `YPE_CPEWIND` | `236` | 236 | (欧)迎风面压力系数	20170607改为X向   YPE_CPEWINDY为Y向 |
| `YPE_CPELEE` | `237` | 237 | (欧)背风面压力系数	20170607改为X向   YPE_CPELEEY为Y向 |
| `YPE_CPEFR` | `238` | 238 | (欧)摩擦系数 |
| `YPE_CF` | `239` | 239 | (欧)力系数cf(force coefficient)	20170607改为X向   YPE_CFY为Y向 |
| `YPE_K1` | `240` | 240 | (欧)湍流系数(turbulence factor)1.0 |
| `YPE_ROUA` | `241` | 241 | (欧)空气密度(kg/m3)1.25 |
| `YPE_COZ` | `242` | 242 | (欧)是否考虑地形系数co(z)(orography factor) |
| `YPE_SLOPET` | `243` | 243 | (欧)山地地形类别(hill or cliff) |
| ↳ `YPEV_SLOPET_HILL` | `( YPE_SLOPET*YP_RES_SIZE+1 )` | 24301 | hill |
| ↳ `YPEV_SLOPET_CLIFF` | `( YPE_SLOPET*YP_RES_SIZE+2 )` | 24302 | cliff |
| `YPE_SLOPED` | `244` | 244 | (欧)斜坡方向 |
| ↳ `YPEV_SLOPED_X` | `( YPE_SLOPED*YP_RES_SIZE+1 )` | 24401 | X |
| ↳ `YPEV_SLOPED_Y` | `( YPE_SLOPED*YP_RES_SIZE+2 )` | 24402 | Y |
| `YPE_SLOPEH` | `245` | 245 | (欧)地形高度 |
| `YPE_SLOPEL` | `246` | 246 | (欧)地形左侧长度 |
| `YPE_SLOPER` | `247` | 247 | (欧)地形右侧长度 |
| `YPE_SLOPEX` | `248` | 248 | (欧)建筑物相对于峰顶水平长度 |
| `YPE_CSCD` | `249` | 249 | (欧)是否考虑结构系数(structural factor) |
| `YPE_DELTA` | `250` | 250 | (欧)δ总的对数阻尼衰减(the total logarithmic decrement of damping) |
| `YP_COLLDEQ` | `251` | 251 | 精细计算方式下对柱按柱间均布风荷加载 (0-1) |
| `YP_TSFTXY` | `252` | 252 | 风荷载体型系数(Y向) |
| `YPU_VB` | `253` | 253 | (美)基本风速(Basic Wind Speed (mi/h)) |
| `YPU_EXP` | `254` | 254 | (美)暴露等级(Exposure Category) |
| ↳ `YPUV_EXP_B` | `( YPU_EXP*YP_RES_SIZE+1 )` | 25401 | B |
| ↳ `YPUV_EXP_C` | `( YPU_EXP*YP_RES_SIZE+2 )` | 25402 | C |
| ↳ `YPUV_EXP_D` | `( YPU_EXP*YP_RES_SIZE+3 )` | 25403 | D |
| `YPU_KZT` | `255` | 255 | (美)地形系数(Topographic Factor) |
| `YPU_G` | `256` | 256 | (美)阵风系数(Gust-Effect Factor) |
| `YPU_KD` | `257` | 257 | (美)风向系数(Wind Directionality Factor) |
| `YPU_CPW` | `258` | 258 | (美)X迎风细数(Windward Coefficient)		20170425 应刘建永要求改含义为X向迎风系数  YPU_CPWY为Y向 |
| `YPU_CPL` | `259` | 259 | (美)X背风系数(Leeward Coefficient)		20170425 应刘建永要求改含义为X向背风系数  YPU_CPLY为Y向 |
| `YPU_WIND_E1` | `260` | 260 | (美)偶然偏心1(e1 ratio) |
| `YPU_WIND_E2` | `261` | 261 | (美)偶然偏心2(e2 ratio) |
| `YP_GF_CLTYPE` | `262` | 262 | 门刚封闭类型 |
| ↳ `YPV_GF_CLOSED` | `( YP_GF_CLTYPE*YP_RES_SIZE+1 )` | 26201 | 封闭式 |
| ↳ `YPV_GF_PCLOSED` | `( YP_GF_CLTYPE*YP_RES_SIZE+2 )` | 26202 | 部分封闭式 |
| ↳ `YPV_GF_OPEN` | `( YP_GF_CLTYPE*YP_RES_SIZE+3 )` | 26203 | 部分封闭式 |
| `YP_GF_WIDTHDIR` | `263` | 263 | 门刚结构横向 |
| ↳ `YPV_GF_WIDTHDIRY` | `( YP_GF_WIDTHDIR*YP_RES_SIZE+1 )` | 26301 | Y向 |
| ↳ `YPV_GF_WIDTHDIRX` | `( YP_GF_WIDTHDIR*YP_RES_SIZE+2 )` | 26302 | X向 |
| `YP_GF_DFX` | `264` | 264 | 门刚结构X向挡风系数 |
| `YP_GF_DFY` | `265` | 265 | 门刚结构Y向挡风系数 |
| `YPU_CPWY` | `266` | 266 | (美)Y迎风细数(Windward Coefficient)		20170425 应刘建永要求改含义为X向迎风系数  YPU_CPWY为Y向 |
| `YPU_CPLY` | `267` | 267 | (美)Y背风系数(Leeward Coefficient)		20170425 应刘建永要求改含义为X向背风系数  YPU_CPLY为Y向 |
| `YPE_CPEORCFY` | `268` | 268 | Y向 含义同YPE_CPEORCF 值为YPEV_CPE 或 YPEV_CF |
| `YPE_CPEWINDY` | `269` | 269 | (欧)迎风面压力系数 为Y向 |
| `YPE_CPELEEY` | `270` | 270 | (欧)背风面压力系数 为Y向 |
| `YPE_CFY` | `271` | 271 | (欧)力系数cf(force coefficient)	为Y向 |
| `YPE_RECTPLAN` | `272` | 272 | (欧)矩形平面(Rectangular Plan)   风压沿高度矩形分布 |
| `YP_WINDHOLEWCS` | `273` | 273 | 多方向风洞定义使用世界坐标系 |
| `YP_ISQSBG` | `274` | 274 | 是否考虑风荷载起算标高 |
| `YP_QSBG` | `275` | 275 | 风荷载起算标高(m) |

### 3. 地震信息

原文节注释行（逐字）：

```c
//////////////////////////////////////////////////////////////////////////
//	地震信息
```

| 宏名 | 取值 | = 实际值 | 原文注释 |
|---|---|---|---|
| `YP_SEISGP` | `301` | 301 | 设计地震分组 |
| `YP_SFLD` | `302` | 302 | 设防烈度 |
| ↳ `YPV_SFLD_6` | `( YP_SFLD*YP_RES_SIZE+1 )` | 30201 | 6 (0.05g) |
| ↳ `YPV_SFLD_7` | `( YP_SFLD*YP_RES_SIZE+2 )` | 30202 | 7 (0.1g) |
| ↳ `YPV_SFLD_75` | `( YP_SFLD*YP_RES_SIZE+3 )` | 30203 | 7 (0.15g) |
| ↳ `YPV_SFLD_8` | `( YP_SFLD*YP_RES_SIZE+4 )` | 30204 | 8 (0.2g) |
| ↳ `YPV_SFLD_85` | `( YP_SFLD*YP_RES_SIZE+5 )` | 30205 | 8 (0.3g) |
| ↳ `YPV_SFLD_9` | `( YP_SFLD*YP_RES_SIZE+6 )` | 30206 | 9 (0.4g) |
| `YP_CDLB` | `303` | 303 | 场地类别 |
| ↳ `YPV_CD_I0` | `( YP_CDLB*YP_RES_SIZE+1 )` | 30301 | I0 |
| ↳ `YPV_CD_I1` | `( YP_CDLB*YP_RES_SIZE+2 )` | 30302 | I1 |
| ↳ `YPV_CD_II` | `( YP_CDLB*YP_RES_SIZE+3 )` | 30303 | II |
| ↳ `YPV_CD_III` | `( YP_CDLB*YP_RES_SIZE+4 )` | 30304 | III |
| ↳ `YPV_CD_IV` | `( YP_CDLB*YP_RES_SIZE+5 )` | 30305 | VI |
| ↳ `YPV_CD_SH` | `( YP_CDLB*YP_RES_SIZE+6 )` | 30306 | 上海(建模用?) |
| `YP_ORPX` | `304` | 304 | 考虑偶然偏心 |
| `YP_ORPXX` | `305` | 305 | X向偶然偏心 |
| `YP_ORPXY` | `306` | 306 | Y向偶然偏心 |
| `YP_SXDZ` | `307` | 307 | 考虑双向地震作用 |
| `YP_MODENUM` | `308` | 308 | 计算振型个数		//2011.1210将参数含义改为 用户指定的振型个数 |
| `YP_HHDBZXS` | `309` | 309 | 活荷载重力荷载代表值组合系数 |
| `YP_ZQZJ` | `310` | 310 | 周期折减系数 |
| `YP_DAMP` | `311` | 311 | 结构阻尼比（%） |
| `YP_TG` | `312` | 312 | 特征周期Tg（s） |
| `YP_AMAX` | `313` | 313 | 多遇地震影响系数最大值 |
| `YP_AMAXHY` | `314` | 314 | 罕遇地震影响系数最大值 |
| `YP_NXJKCL` | `315` | 315 | 斜交抗侧力构件方向数 |
| `YP_XJKCL` | `316` | 316 | 斜交抗侧力构件方向角度 |
| `YP_IZBLDZFX` | `317` | 317 | 自动计算最不利地震方向的地震作用 |
| `YP_ORPXM` | `318` | 318 | 偶然偏心算法 |
| ↳ `YPV_ORPXM_TRAD` | `( YP_ORPXM*YP_RES_SIZE+1 )` | 31801 | 等效扭矩法(传统法) |
| ↳ `YPV_ORPXM_NEW` | `( YP_ORPXM*YP_RES_SIZE+2 )` | 31802 | 瑞利-里兹投影反射谱法(新算法) |
| `YP_AUTOMODENUM` | `319` | 319 | 2011.1210参数含义为是否自动设定振型个数  0为用户定义，1为程序自动设定 |
| `YP_SXDZDXZ` | `320` | 320 | 竖向地震作用系数底线值 《抗规》5.3.3   (0.08f) 原(0.1f) |
| `YP_ZLCYXS` | `321` | 321 | 自动设定振型个数时 质量参与系数(%) 默认90，(0, 100) |
| `YP_CUSTOM_MAXMODENUM` | `322` | 322 | 自动设定振型个数时 是否指定最大振型个数 |
| `YP_MAXMODENUM` | `323` | 323 | 自动设定振型个数时 最大振型个数(150) |
| `YP_TZZTYPE` | `324` | 324 | 特征值分析类型 |
| ↳ `YPV_TZZ_LANCZOS` | `( YP_TZZTYPE*YP_RES_SIZE+1 )` | 32401 | 1：迭代的LANCZOS方法 |
| ↳ `YPV_TZZ_WYDRITZ` | `( YP_TZZTYPE*YP_RES_SIZE+2 )` | 32402 | 2：WYD-RITZ方法 |
| ↳ `YPV_TZZ_ZKKDD` | `( YP_TZZTYPE*YP_RES_SIZE+3 )` | 32403 | 3：子空间迭代法 |
| ↳ `YPV_TZZ_RITZ` | `( YP_TZZTYPE*YP_RES_SIZE+4 )` | 32404 | 4：Ritz向量法 |
| `YP_DAMPTYPE` | `325` | 325 | 阻尼比设置类型 |
| ↳ `YPV_DAMP_TOTAL` | `( YP_DAMPTYPE*YP_RES_SIZE+1 )` | 32501 | 全楼统一   按全楼统一时，阻尼比为YP_DAMP |
| ↳ `YPV_DAMP_BYMAT` | `( YP_DAMPTYPE*YP_RES_SIZE+2 )` | 32502 | 按材料设置阻尼比 按材料设置时， YP_DAMPMATIDS应与YP_DAMPMATDAMPS一一对应，数组大小应为YP_DAMPMATNUM+1 |
| `YP_DAMPMATNUM` | `328` | 328 | 分材料阻尼比时材料种类数 目前为三类：钢、砼、型钢混凝土 |
| `YP_DAMPMATIDS` | `329` | 329 | 分材料阻尼比时各材料ID(int数组，第一个为数组大小) 暂按yjkidkind.h中标准材料号记录 如钢--IDM_Steel  砼--IDM_Concrete |
| `YPV_DAMPMATID_STEEL` | `5` | 5 | 钢  阻尼比数组中用的材料ID，尽量与梁工的一致 ==IDM_Steel |
| `YPV_DAMPMATID_CONCRETE` | `6` | 6 | 砼  阻尼比数组中用的材料ID，尽量与梁工的一致 ==IDM_Concrete |
| `YPV_DAMPMATID_GH` | `56` | 56 | 型钢砼  阻尼比数组中用的材料ID |
| `YP_DAMPMATDAMPS` | `330` | 330 | 分材料阻尼比时各材料阻尼比值(%)(float数组，第一个为数组大小) |
| `YP_ICUSTALPHA` | `331` | 331 | 使用自定义地震影响系数曲线 |
| `YP_CUSTA_STEP` | `332` | 332 | 自定义地震影响系数曲线数据步长(s) |
| `YP_CUSTA_NSTEP` | `333` | 333 | 自定义地震影响系数曲线数据步数 |
| `YP_CUSTALPHA` | `334` | 334 | 自定义地震影响系数曲线 |
| `YP_DZNLFH` | `335` | 335 | 按主振型确定地震内力符号 |
| `YP_ADDDMPMETHOD` | `336` | 336 | 减震隔震附加阻尼比算法 |
| ↳ `YPV_ADDDMPMETHOD_DECOUPLING` | `( YP_ADDDMPMETHOD*YP_RES_SIZE+1 )` | 33601 | 强制解耦  1 |
| ↳ `YPV_ADDDMPMETHOD_ENERGY` | `( YP_ADDDMPMETHOD*YP_RES_SIZE+2 )` | 33602 | 能量法 |
| `YP_MAXADDDMPRATIO` | `337` | 337 | 最大附加阻尼比，强行解耦法有效(0, 100)  0.25 |
| `YPE_GROUND` | `338` | 338 | 场地类别 1-5 |
| `YPE_SPECTRUM` | `339` | 339 | 反应谱类别 1-2 |
| `YPE_ALPHAHG` | `340` | 340 | 场地横向加速度 |
| `YPE_ALPHAVG` | `341` | 341 | 场地竖向加速度 |
| `YPE_BETA` | `342` | 342 | 下界系数 |
| `YPE_QH` | `343` | 343 | Behavior factor for horizontal seism	结构性能系数(横向) |
| `YPE_QV` | `344` | 344 | Behavior factor for horizontal seism	结构性能系数(竖向) |
| `YP_DXSKZDJ` | `345` | 345 | 地下一层以下抗震构件措施的抗震等级逐层降低	 抗震规范6.1.3-3 |
| `YP_ZZBKLDXZL` | `346` | 346 | 在计算自振周期时不考虑地面以下的结构质量(0~1) 默认0 |
| `YPE_DC` | `347` | 347 | 延性等级 |
| ↳ `YPEV_DCH` | `( YPE_DC*YP_RES_SIZE+1 )` | 34701 |  |
| ↳ `YPEV_DCM` | `( YPE_DC*YP_RES_SIZE+2 )` | 34702 |  |
| ↳ `YPEV_DCL` | `( YPE_DC*YP_RES_SIZE+3 )` | 34703 |  |
| ↳ `YPEV_SEC` | `( YPE_DC*YP_RES_SIZE+4 )` | 34704 |  |
| `YPE_MUFAI` | `348` | 348 | 曲率延性系数 |
| `YPUS_DC` | `349` | 349 | 抗震设计类别（SDC） Seismic Design Category |
| ↳ `YPUSV_DCA` | `( YPUS_DC*YP_RES_SIZE+1 )` | 34901 |  |
| ↳ `YPUSV_DCB` | `( YPUS_DC*YP_RES_SIZE+2 )` | 34902 |  |
| ↳ `YPUSV_DCC` | `( YPUS_DC*YP_RES_SIZE+3 )` | 34903 |  |
| ↳ `YPUSV_DCD` | `( YPUS_DC*YP_RES_SIZE+4 )` | 34904 |  |
| ↳ `YPUSV_DCE` | `( YPUS_DC*YP_RES_SIZE+5 )` | 34905 |  |
| ↳ `YPUSV_DCF` | `( YPUS_DC*YP_RES_SIZE+6 )` | 34906 |  |
| `YP_SPJZXS` | `350` | 350 | 调整后的水平向减震系数(β/ψ) 默认1  (0, ∞) |
| `YPUS_SEISX` | `351` | 351 | 考虑X向地震 （美国规范）BOOL	暂时无效 |
| `YPUS_SEISY` | `352` | 352 | 考虑Y向地震 （美国规范）BOOL	暂时无效 |
| `YPUS_XECCP` | `353` | 353 | 考虑X正向偏心 （美国规范）BOOL	暂时无效 |
| `YPUS_XECCN` | `354` | 354 | 考虑X负向偏心 （美国规范）BOOL	暂时无效 |
| `YPUS_YECCP` | `355` | 355 | 考虑Y正向偏心 （美国规范）BOOL	暂时无效 |
| `YPUS_YECCN` | `356` | 356 | 考虑Y负向偏心 （美国规范）BOOL	暂时无效 |
| `YPUS_ECCRATIO` | `357` | 357 | Ecc. Ratio(All Diaph.)  偏心率 float	暂时无效 默认取0.05 |
| `YPUS_SEISTOPFLR` | `359` | 359 | Top Story for Seismic Loads  受地震作用的最高层  int		暂时无效 |
| `YPUS_SEISBTMFLR` | `360` | 360 | Bottom Story for Seismic Loads  受地震作用的最底层  int	暂时无效 |
| `YPUS_FYTZXS` | `361` | 361 | Response Modification. R 反应调整系数 float 默认为3 |
| `YPUS_XTCQXS` | `362` | 362 | System Overstrength. Omega 系统超强度系数 float 默认为3 |
| `YPUS_BXFDXS` | `363` | 363 | Deflection Amplification.Cd 变形放大系数 float  默认为5.5 |
| `YPUS_ZYXXS` | `364` | 364 | Occupancy Importance.I  重要性系数 float  默认为1 |
| `YPUS_JSD02` | `365` | 365 | 0.2 Sec Spectral Accel.Ss 0.2秒的谱加速度 float |
| `YPUS_JSD1` | `366` | 366 | 1 Sec Spectral Accel.S1   1秒的谱加速度 float |
| `YPUS_CZQ` | `367` | 367 | Long-Period Transition Period 长周期转型周期 float |
| `YPUS_CDLB` | `368` | 368 | Site Class  场地类别 int |
| ↳ `YPUV_CD_A` | `( YPUS_CDLB*YP_RES_SIZE+1 )` | 36801 | Site Class  场地类别 A |
| ↳ `YPUV_CD_B` | `( YPUS_CDLB*YP_RES_SIZE+2 )` | 36802 | Site Class  场地类别 B |
| ↳ `YPUV_CD_C` | `( YPUS_CDLB*YP_RES_SIZE+3 )` | 36803 | Site Class  场地类别 C |
| ↳ `YPUV_CD_D` | `( YPUS_CDLB*YP_RES_SIZE+4 )` | 36804 | Site Class  场地类别 D |
| ↳ `YPUV_CD_E` | `( YPUS_CDLB*YP_RES_SIZE+5 )` | 36805 | Site Class  场地类别 E |
| ↳ `YPUV_CD_F` | `( YPUS_CDLB*YP_RES_SIZE+6 )` | 36806 | Site Class  场地类别 F 用户输入 |
| `YPUS_SITEFA` | `369` | 369 | Site Coefficient. Fa float |
| `YPUS_SITEFV` | `370` | 370 | Site Coefficient. Fv float |
| `YPUS_COMBMETHOD` | `371` | 371 | Modal Combination Method 模态组合方法 暂时无效，默认取CQC |
| ↳ `YPUV_COMBMETHOD_CQC` | `( YPUS_COMBMETHOD*YP_RES_SIZE+1 )` | 37101 | CQC |
| ↳ `YPUV_COMBMETHOD_SRSS` | `( YPUS_COMBMETHOD*YP_RES_SIZE+2 )` | 37102 | SRSS |
| `YPUS_YDXS` | `372` | 372 | 赘余度系数 Redundancy factor  (0, ~) 默认1 |
| `YP_JBMXFYPKLSPZL` | `373` | 373 | 局部模型反应谱法计算竖向地震时考虑水平质量 (0/1) |
| `YP_USENEWQHT` | `374` | 374 | 按新区划图计算 GB18306-2015    (0/1) |
| `YP_LINKUSETH` | `375` | 375 | 连接单元的有效刚度和阻尼自动采用直接积分法时程计算结果 |
| `YPUS_JLQYXDJ` | `376` | 376 | 剪力墙延性等级		Ductility Classs of Shear Walls |
| ↳ `YPUV_JLQYXDJ_ORDINARY` | `( YPUS_JLQYXDJ*YP_RES_SIZE+1 )` | 37601 | Ordinary |
| ↳ `YPUV_JLQYXDJ_INTERMEDIATE` | `( YPUS_JLQYXDJ*YP_RES_SIZE+2 )` | 37602 | Intermediate |
| ↳ `YPUV_JLQYXDJ_SPECIAL` | `( YPUS_JLQYXDJ*YP_RES_SIZE+3 )` | 37603 | Special |
| `YPUS_HNTKJYXDJ` | `377` | 377 | 混凝土框架延性等级	Ductility Classs of Concrete Frames |
| ↳ `YPUV_HNTKJYXDJ_ORDINARY` | `( YPUS_HNTKJYXDJ*YP_RES_SIZE+1 )` | 37701 | ordinary |
| ↳ `YPUV_HNTKJYXDJ_INTERMEDIATE` | `( YPUS_HNTKJYXDJ*YP_RES_SIZE+2 )` | 37702 | Intermediate |
| ↳ `YPUV_HNTKJYXDJ_SPECIAL` | `( YPUS_HNTKJYXDJ*YP_RES_SIZE+3 )` | 37703 | special |
| `YPUS_STLKJYXDJ` | `378` | 378 | 钢结构框架延性等级	Ductility Classs of Steel Frames |
| ↳ `YPUV_STLKJYXDJ_ORDINARY` | `( YPUS_STLKJYXDJ*YP_RES_SIZE+1 )` | 37801 | ordinary |
| ↳ `YPUV_STLKJYXDJ_INTERMEDIATE` | `( YPUS_STLKJYXDJ*YP_RES_SIZE+2 )` | 37802 | Intermediate |
| ↳ `YPUV_STLKJYXDJ_SPECIAL` | `( YPUS_STLKJYXDJ*YP_RES_SIZE+3 )` | 37803 | special |
| `YPE_SXDZTYPE` | `379` | 379 | (欧、美)考虑双向地震作用时组合方式 |
| ↳ `YPEV_SXDZTYPE_SRSS` | `( YPE_SXDZTYPE*YP_RES_SIZE+1 )` | 37901 | (欧、美)考虑双向地震作用时组合方式  SRSS |
| ↳ `YPEV_SXDZTYPE_103` | `( YPE_SXDZTYPE*YP_RES_SIZE+2 )` | 37902 | (欧、美)考虑双向地震作用时组合方式 1 "+" 3 |
| `YPUS_ZQSXCT` | `380` | 380 | (美)基底剪力法周期上限系数Ct (默认0.0488)  (0,1) upper limit factor of period for equivalent lateral force procedure |
| `YPUS_ZQSXX` | `381` | 381 | (美)基底剪力法周期上限系数x  (默认0.75)  (0,1)upper limit factor of period for equivalent lateral force procedure |
| `YP_SEISCLASS` | `382` | 382 | 抗震设防类别 Classification of seismic fortification |
| ↳ `YPV_SEISCLASS_1` | `( YP_SEISCLASS*YP_RES_SIZE+1 )` | 38201 | 抗震设防类别 甲 |
| ↳ `YPV_SEISCLASS_2` | `( YP_SEISCLASS*YP_RES_SIZE+2 )` | 38202 | 抗震设防类别 乙 |
| ↳ `YPV_SEISCLASS_3` | `( YP_SEISCLASS*YP_RES_SIZE+3 )` | 38203 | 抗震设防类别 丙 |
| ↳ `YPV_SEISCLASS_4` | `( YP_SEISCLASS*YP_RES_SIZE+4 )` | 38204 | 抗震设防类别 丁 |
| `YPUS_SITESDS` | `387` | 387 | (美)计算系数 SDS = (2/3)*Fa*Ss |
| `YPUS_SITESD1` | `388` | 388 | (美)计算系数 SD1 = (2/3)*Fv*S1 |
| `YPUS_CQCELF` | `389` | 389 | (美)CQC/ELF |
| `YPUS_ZXX` | `390` | 390 | (美)X方向基本周期对应的振型号 |
| `YPUS_ZXY` | `391` | 391 | (美)Y方向基本周期对应的振型号 |
| `YP_CUSTA_TG` | `383` | 383 | 特征周期 |
| `YP_CUSTA_AMAX` | `384` | 384 | 地震影响系数最大值 |
| `YP_CUSTA_DAMP` | `385` | 385 | 结构阻尼比 |
| `YP_CUSTA_AREA` | `386` | 386 | 规范选择 |
| ↳ `YPV_CUSTA_AREA_CN` | `( YP_CUSTA_AREA*YP_RES_SIZE+1 )` | 38601 | 全国 |
| ↳ `YPV_CUSTA_AREA_GD2020` | `( YP_CUSTA_AREA*YP_RES_SIZE+2 )` | 38602 | 新版广东高规 |
| ↳ `YPV_CUSTA_AREA_SH2023` | `( YP_CUSTA_AREA*YP_RES_SIZE+3 )` | 38603 | 上海抗规 2023 |
| ↳ `YPV_CUSTA_AREA_CN1989` | `( YP_CUSTA_AREA*YP_RES_SIZE+4 )` | 38604 | 全国1989 |
| ↳ `YPV_CUSTA_AREA_CN2001` | `( YP_CUSTA_AREA*YP_RES_SIZE+5 )` | 38605 | 全国2001 |

### 4. 活荷信息

原文节注释行（逐字）：

```c
//////////////////////////////////////////////////////////////////////////
//	活荷信息
```

| 宏名 | 取值 | = 实际值 | 原文注释 |
|---|---|---|---|
| `YP_ZQHHZJ` | `401` | 401 | 柱、墙设计时活荷载是否折减 |
| `YP_HH2JC` | `402` | 402 | 传给基础的活荷载 |
| `YP_MAXHHBL` | `403` | 403 | 活荷载不利布置最高层号 |
| `YP_ZQHHZJXS` | `404` | 404 | 柱、墙设计时活荷载折减系数设置 |
| `YP_LMLHHZJ` | `405` | 405 | 楼面梁活荷载折减 |
| ↳ `YPV_LMLHHZJ_NOT` | `( YP_LMLHHZJ*YP_RES_SIZE+1 )` | 40501 | 不折减 |
| ↳ `YPV_LMLHHZJ_25_9` | `( YP_LMLHHZJ*YP_RES_SIZE+2 )` | 40502 | 从属面积超过 25m时，楼面活荷载折减0.9 |
| ↳ `YPV_LMLHHZJ_50_9` | `( YP_LMLHHZJ*YP_RES_SIZE+3 )` | 40503 | 从属面积超过 50m时，楼面活荷载折减0.9 |
| ↳ `YPV_LMLHHZJ_DXB6` | `( YP_LMLHHZJ*YP_RES_SIZE+4 )` | 40504 | 单向板楼盖楼面活荷载折减0.6 |
| ↳ `YPV_LMLHHZJ_SXB8` | `( YP_LMLHHZJ*YP_RES_SIZE+5 )` | 40505 | 双向板楼盖楼面活荷载折减0.8 |
| `YPE_LMLHHZJ` | `406` | 406 | (欧)梁活荷载折减 |
| `YPE_ZQHHZJ` | `407` | 407 | (欧)柱、墙设计时活荷载是否折减 |
| `YPE_LZJMIN` | `408` | 408 | (欧)梁活荷折减系数最小值 |
| `YP_HHZJBYPM` | `409` | 409 | 按建模菜单“房间属性”计算 |
| `YP_HHBL_QSC` | `410` | 410 | 活荷载不利布置起始层 |
| `YP_HHBL_ZZC` | `411` | 411 | 活荷载不利布置终止层 |
| `YP_HHBL_JSMX` | `412` | 412 | 计算模型(多层) |
| `YP_HHBL_QLKLHHZBLBZ` | `413` | 413 | 全楼考虑活荷载不利布置 |

### 5. 设计相关要求

原文节注释行（逐字）：

```c
//////////////////////////////////////////////////////////////////////////
//	设计相关要求
```

| 宏名 | 取值 | = 实际值 | 原文注释 |
|---|---|---|---|
| `YP_TFXS` | `501` | 501 | 梁端负弯矩调幅系数 |
| `YP_HHNLFD` | `502` | 502 | 活荷载内力放大系数 |
| `YP_NJZJ` | `503` | 503 | 梁扭矩折减系数 |
| `YP_KZZL` | `504` | 504 | 调整与框支柱相连的梁内力 |
| `YP_525` | `505` | 505 | 最小剪重比地震力调整 |
| `YP_482_3` | `506` | 506 | 框支剪力墙结构底部加强区剪力墙抗震等级自动提高一级 |
| `YP_JLQJQ` | `507` | 507 | 剪力墙加强区起算层号 |
| `YP_9ICPXS` | `508` | 508 | 实配钢筋超配系数 |
| `YP_NBRC` | `509` | 509 | 指定薄弱层 |
| `YP_IBRC` | `510` | 510 | 指定薄弱层层号 |
| `YP_ZHC_BRC` | `511` | 511 | 转换层指定为薄弱层 |
| `YP_BRCDZFD` | `512` | 512 | 薄弱层地震内力放大系数 |
| `YP_N02V0` | `514` | 514 | 0.2V0调整 |
| `YP_02V0FLRB` | `515` | 515 | 0.2V0调整起始层号 |
| `YP_02V0FLRE` | `516` | 516 | 0.2V0调整终止层号 |
| `YP_MAX02V0` | `517` | 517 | 0.2V0调整上限 |
| `YP_MAXKZZ` | `518` | 518 | 框支柱调整上限 |
| `YP_GG358` | `519` | 519 | 自动对楼层抗剪承载力形成的薄弱层放大调整 |
| `YP_525RZ` | `520` | 520 | 最小剪重比地震力调整  弱轴方向动位移比例(0~1)  0.5 |
| `YP_525QZ` | `521` | 521 | 最小剪重比地震力调整  强轴方向动位移比例(0~1)  0.5 |
| `YP_BRCGDB` | `522` | 522 | 按层刚度比判断薄弱层的方法 |
| ↳ `YPV_BRCGDB_GGKG` | `( YP_BRCGDB*YP_RES_SIZE+1 )` | 52201 | 高规和抗规从严 |
| ↳ `YPV_BRCGDB_GG` | `( YP_BRCGDB*YP_RES_SIZE+2 )` | 52202 | 按高规 |
| ↳ `YPV_BRCGDB_KG` | `( YP_BRCGDB*YP_RES_SIZE+3 )` | 52203 | 按抗规 |
| ↳ `YPV_BRCGDB_NO` | `( YP_BRCGDB*YP_RES_SIZE+4 )` | 52204 | 不自动判断 |
| ↳ `YPV_BRCGDB_SHKG` | `( YP_BRCGDB*YP_RES_SIZE+5 )` | 52205 | 按上海抗规剪切刚度比 |
| ↳ `YPV_BRCGDB_SHKGJW` | `( YP_BRCGDB*YP_RES_SIZE+6 )` | 52206 | 按上海抗规剪弯刚度比 |
| `YP_525NZXY` | `523` | 523 | (剪重比)扭转效应明显 |
| `YP_DZFD` | `513` | 513 | 全楼地震作用放大系数 |
| `YP_DZFDTYPE` | `524` | 524 | 地震作用放大系数设置类型 |
| ↳ `YPV_DZFDTYPE_ALLSAME` | `( YP_DZFDTYPE*YP_RES_SIZE+1 )` | 52401 | 地震作用放大系数 全楼统一  应用YP_DZFD对应数据 |
| ↳ `YPV_DZFDTYPE_FCFT` | `( YP_DZFDTYPE*YP_RES_SIZE+2 )` | 52402 | 地震作用放大系数 分层分塔  应用YP_DZFDARRAY对应数据 |
| `YP_DZFDARRAY` | `525` | 525 | 地震作用放大系数 各层各塔单设(数组) |
| `YP_KGC_GG3522` | `526` | 526 | 有地下室时嵌固层刚度比执行《高规》3.5.2-2 |
| `YP_02V0NOBEAM` | `527` | 527 | 与柱相连的框架梁端M、V不调整 (0~1) 0 |
| `YP_IS02V0USER` | `528` | 528 | 是否用户指定0.2V0调整系数  (0~1) 0 |
| `YP_02V0USERDATA` | `529` | 529 | 用户定义的0.2V0调整系数 各层各塔单设(数组) |
| `YP_BRACE2COLANG` | `530` | 530 | 支撑临界角(度)  (与竖轴夹角小于此值的支撑将按柱考虑) |
| `YP_IS525USER` | `531` | 531 | 是否用户指定最小剪重比地震力调整系数  (0~1) 0 |
| `YP_525USERDATA` | `532` | 532 | 用户定义的最小剪重比地震力调整系数 各层各塔单设(数组) (无限值) |
| `YP_02V0VRatio` | `533` | 533 | 0.2V0调整时 楼层剪力V最小倍数 (0, ∝)  默认0.2 |
| `YP_02V0VfmaxRatio` | `534` | 534 | 0.2V0调整时 各层剪力最大值的倍数 (0, ∝) 默认 1.5 |
| `YP_GG353` | `535` | 535 | 自动根据层间受剪承载力比值调整配筋《高规》3.5.3 |
| `YP_TUS_DZFD` | `536` | 536 | TUS剪力墙水平地震力放大系数 |
| `YPE_DISPREDU` | `537` | 537 | reduction factor for lateral displacements 层间位移计算时的折减系数v |
| `YP_SUMSEISBYVERMEM` | `538` | 538 | 按竖向构件内力统计层地震剪力 |
| `YP_KJLTFMRATIO` | `539` | 539 | 框架梁调幅后不小于简支梁跨中弯矩的倍数 |
| `YP_NKJLTFMRATIO` | `540` | 540 | 非框架梁调幅后不小于简支梁跨中弯矩的倍数 |
| `YP_WYBXZ` | `541` | 541 | 位移角小于此值时，位移比设置为1 |
| `YP_02V0Type` | `542` | 542 | 0.2V0调整类型，值为0或1。默认为0   0为Min[alpha*Vo, beta*Vfmax], 1为Max[alpha*Vo, beta*Vfmax]  其中alpha即为YP_02V0VRatio， beta即为YP_02V0VfmaxRatio |
| `YP_WALLALLSEIS` | `543` | 543 | 剪力墙承担全部地震剪力0/1  默认0 |
| `YP_AUTOCALC525` | `544` | 544 | 自动计算动位移比例系数，自动计算时，YP_525RZ和YP_525QZ变灰 |
| `YP_TUS_JLQZYB` | `545` | 545 | TUS空心固模剪力墙轴压比限值  0.5 |
| `YP_TUS_CJWYB` | `546` | 546 | TUS层间位移比限值 1/？ （默认 1000） |
| `YPUS_KJRATIO` | `547` | 547 | 框架承担层剪力的最少比例为（之前为“框架至少承担25%层剪力”）		the frames resist at least 25 percent of the story shear |
| `YPUS_JLQRATIO` | `548` | 548 | 剪力墙承担层剪力的最少比例为（之前为“剪力墙至少承担75%层剪力）		the shear walls resist at lease 75 percent of the story shear |
| `YP_0YLQCALC` | `549` | 549 | 零应力区验算时底面尺寸确定方式 |
| ↳ `YPV_0YLQCALC_ZX` | `( YP_0YLQCALC*YP_RES_SIZE+1 )` | 54901 | 零应力区验算时底面尺寸确定方式  质心到最近边距离的2倍 |
| ↳ `YPV_0YLQCALC_SIDE` | `( YP_0YLQCALC*YP_RES_SIZE+2 )` | 54902 | 零应力区验算时底面尺寸确定方式  平面外包矩形边长 |
| `YPUS_TZKJZZL` | `550` | 550 | 调整框架柱轴力 |
| `YPUS_QJRWFDJACLL` | `551` | 551 | 非对角暗撑连梁实行强剪弱弯 |
| `YPUS_QJRWQZ` | `552` | 552 | 墙肢实行强剪弱弯 |
| `YPUS_LLZDSZAC` | `553` | 553 | 连梁自动判断是否设置对角暗撑 |
| `YP_SXDZTZ` | `554` | 554 | 考虑双向地震时内力调整方式 |
| ↳ `YPV_SXDZTZ_DZ` | `( YP_SXDZTZ*YP_RES_SIZE+1 )` | 55401 | 先考虑双向地震再调整 |
| ↳ `YPV_SXDZTZ_TZ` | `( YP_SXDZTZ*YP_RES_SIZE+2 )` | 55402 | 先调整再考虑双向地震 |
| `YP_JLQDZJLTJDKJ` | `555` | 555 | 剪力墙端柱的面外剪力统计到框架部分 |
| `YP_GG353BZ` | `556` | 556 | 《高规》3.5.3 自动根据层间受剪承载力比值调整配筋 配合YP_GG353使用 |
| `YPE_YXQDZTZXSYBWJ` | `557` | 557 | 中高延性墙地震内力调整系数	  一般部位弯矩(Moment outside the critical region)：默认1.2  Enhanced factor of seismic action for DCM or DCH wall |
| `YPE_YXQDZTZXSYBJL` | `558` | 558 | 中高延性墙地震内力调整系数	  一般部位剪力(Shear outside the critical region)：默认1.3  Enhanced factor of seismic action for DCM or DCH wall |
| `YPE_YXQDZTZXSJQJL` | `559` | 559 | 中高延性墙地震内力调整系数	  底部加强区剪力(Shear in the critical region)：默认1.5  Enhanced factor of seismic action for DCM or DCH wall |
| `YPUS_KJRATIOVAL` | `560` | 560 | 框架承担层剪力的最少比例为 与参数YPUS_KJRATIO配合 The minimum proportion of shear on the floor of the frame is |
| `YPUS_JLQRATIOVAL` | `561` | 561 | 剪力墙承担层剪力的最少比例为 与参数YPUS_JLQRATIO配合 The minimum proportion of shear on the floor of the shear wall is |
| `YP_ZHGJDZFDXS` | `562` | 562 | 转换结构构件（三、四级）的水平地震作用效应放大系数 |
| `YP_ShearStiffness` | `563` | 563 | 剪切刚度计算hi取层高 |

### 6. 计算总体信息

原文节注释行（逐字）：

```c
//////////////////////////////////////////////////////////////////////////
//	计算总体信息
```

| 宏名 | 取值 | = 实际值 | 原文注释 |
|---|---|---|---|
| `YP_SGMN` | `601` | 601 | 恒活荷载计算信息 |
| ↳ `YPV_SGMN_0` | `( YP_SGMN*YP_RES_SIZE+1 )` | 60101 | 不计算恒活荷载 |
| ↳ `YPV_SGMN_A` | `( YP_SGMN*YP_RES_SIZE+2 )` | 60102 | 一次性加载 |
| ↳ `YPV_SGMN_1` | `( YP_SGMN*YP_RES_SIZE+3 )` | 60103 | 施工模拟一 |
| ↳ `YPV_SGMN_2` | `( YP_SGMN*YP_RES_SIZE+4 )` | 60104 | 施工模拟二 |
| ↳ `YPV_SGMN_3` | `( YP_SGMN*YP_RES_SIZE+5 )` | 60105 | 施工模拟三 |
| ↳ `YPV_SGMN_FXX` | `( YP_SGMN*YP_RES_SIZE+6 )` | 60106 | 非线性施工模拟 |
| `YP_SGCX` | `602` | 602 | 施工次序 |
| `YP_WTYPE` | `603` | 603 | 风荷载计算信息 |
| ↳ `YPV_NOWIND` | `( YP_WTYPE*YP_RES_SIZE+1 )` | 60301 | 不计算风荷载 |
| ↳ `YPV_HRWIND` | `( YP_WTYPE*YP_RES_SIZE+2 )` | 60302 | 普通方式计算 |
| ↳ `YPV_SPWIND` | `( YP_WTYPE*YP_RES_SIZE+3 )` | 60303 | 精细方式计算 |
| ↳ `YPV_HRSPWIND` | `( YP_WTYPE*YP_RES_SIZE+4 )` | 60304 | 计算水平和特殊风荷载(无用) |
| ↳ `YPV_BYMEMBER` | `( YP_WTYPE*YP_RES_SIZE+5 )` | 60305 | 按构件档风面积计算 |
| `YP_SEISTYPE` | `604` | 604 | 地震作用计算信息 |
| ↳ `YPV_NOSEIS` | `( YP_SEISTYPE*YP_RES_SIZE+1 )` | 60401 | 不计算地震作用 |
| ↳ `YPV_HRSEIS` | `( YP_SEISTYPE*YP_RES_SIZE+2 )` | 60402 | 计算水平地震作用 |
| ↳ `YPV_HRVTSEIS` | `( YP_SEISTYPE*YP_RES_SIZE+3 )` | 60403 | 计算水平和规范简化方法竖向地震作用 |
| ↳ `YPV_HVFYPSEIS` | `( YP_SEISTYPE*YP_RES_SIZE+4 )` | 60404 | 计算水平和反应谱法竖向地震作用(整体求解) |
| ↳ `YPV_HVFYPSEISDIV` | `( YP_SEISTYPE*YP_RES_SIZE+5 )` | 60405 | 计算水平和反应谱法竖向地震作用(独立求解) |
| ↳ `YPV_HVFYPSEISDIVPART` | `( YP_SEISTYPE*YP_RES_SIZE+6 )` | 60406 | 计算水平和反应谱法竖向地震作用（局部模型独立求解） |
| `YP_MESHLEN` | `605` | 605 | 墙元细分最大控制长度（m） |
| `YP_QZGXLB` | `606` | 606 | 对所有楼层强制采用刚性楼板假定 |
| `YP_QGMW` | `607` | 607 | 强制刚性楼板假定时保留弹性板面外刚度 |
| `YP_PDELTA` | `608` | 608 | 考虑P-Delta效应 |
| `YP_LZGY` | `609` | 609 | 梁柱重叠部分简化为刚域	//2013.0420 含义修改 分拆为梁端和柱端。  该宏为考虑梁端刚域 柱端为YP_ZDGY |
| `YP_TQLFD` | `612` | 612 | 托墙梁刚度放大系数 |
| `YP_JS_NCHK` | `613` | 613 | 忽略数检警告信息 |
| `YP_JS_DISP` | `614` | 614 | 结构位移计算 |
| `YP_JS_GJNL` | `616` | 616 | 全楼构件内力计算 |
| `YP_JS_DCHZ` | `617` | 617 | 吊车荷载计算 |
| `YP_JS_JCGD` | `618` | 618 | 生成传给基础的刚度 |
| `YP_JS_PJYS` | `619` | 619 | 构件配筋及验算（包括设置起止配筋层号） |
| `YP_JS_SEIS` | `620` | 620 | 地震作用分析方法（侧刚、总刚） |
| `YP_JS_RESM` | `621` | 621 | 线性方程组求解方法 |
| `YP_HFANG` | `622` | 622 | 水平力与整体坐标夹角 |
| `YP_JS_RFHZ` | `623` | 623 | 计算人防荷载 |
| `YP_JS_WDISP` | `624` | 624 | 输出节点位移 |
| `YP_ASPTOW` | `625` | 625 | 各分塔与整体分别计算，配筋取各分塔与整体结果较大值 |
| `YP_ATOW` | `626` | 626 | 自动分多塔 |
| `YP_B2W` | `627` | 627 | 转换梁/连梁按剪力墙计算 |
| `YP_MESHCO` | `628` | 628 | 网格划分全协调 |
| `YP_LL2WKGB` | `629` | 629 | 连梁按墙元计算控制跨高比 |
| `YP_SQKJ` | `632` | 632 | 少墙框架自动按框架和框架-抗震墙模型计算并取大 |
| `YP_SQKJE` | `633` | 633 | 少墙框架按纯框架计算时墙弹性模量折减系数 |
| `YP_ATOWFLR` | `634` | 634 | 自动分塔控制层号 |
| `YP_SGSTEP` | `635` | 635 | 施工模拟步长 |
| `YP_DXSNATOW` | `636` | 636 | 地下室不自动划分多塔 |
| `YP_MESHLENB` | `637` | 637 | 板元细分最大控制长度（m） |
| `YP_QZGXLBDXS` | `638` | 638 | 地下室强制刚性楼板假定 |
| `YP_QLKZCJD` | `639` | 639 | 墙梁跨中节点作为刚性楼板从节点	//add by cp 2011.10.30 |
| `YP_DQJM` | `640` | 640 | 对短墙肢自动加密	//add by cp 2011.12.07 |
| `YP_LTGD` | `641` | 641 | 结构计算时考虑楼梯刚度 |
| `YP_QLLISKJL` | `642` | 642 | 与剪力墙相连的梁是否按框架梁设计（是） |
| `YP_JSWY_LLBZJ` | `643` | 643 | 计算连梁刚度不折减模型下的地震位移（0~1） （0--不计算） |
| `YP_XJKXB` | `644` | 644 | 现浇空心板计算方法 |
| `YP_JSXJKXB` | `645` | 645 | 计算现浇空心板 （0~1） （0--不计算） |
| `YP_LBBXXT` | `646` | 646 | 梁与弹性板变形协调 （0~1） （0--不协调） |
| `YP_IGNORETRANSZLFD` | `647` | 647 | 特殊构件定义不强制使用从SAT转入的梁刚度系数(处理SAT中勾选矩形梁按T形选项情况) |
| `YP_ZHCGDMOTHED` | `648` | 648 | 转换层上、下结构侧向刚度算法	当转换层所在层号>=3有效 |
| ↳ `YP_ZHCGDMOTHED_GGE03` | `( YP_ZHCGDMOTHED*YP_RES_SIZE+1 )` | 64801 | 高规附录E.0.3 |
| ↳ `YP_ZHCGDMOTHED_GDCMDL` | `( YP_ZHCGDMOTHED*YP_RES_SIZE+2 )` | 64802 | 刚度串模型 |
| `YP_LBXTOFFSET` | `649` | 649 | 弹性板与梁协调时考虑梁向下相对偏移 |
| `YP_ZDGY` | `650` | 650 | 考虑柱端刚域 |
| `YP_LQZZKZD` | `651` | 651 | 梁墙自重扣除柱端 |
| `YP_PDELTAXSD` | `652` | 652 | 考虑P-Delta效应 组合系数恒载 (1.0) |
| `YP_PDELTAXSL` | `653` | 653 | 考虑P-Delta效应 组合系数活载 (0.5) |
| `YP_BUCKLING` | `654` | 654 | 进行屈曲分析 |
| `YP_BUCKMODNUM` | `655` | 655 | 屈曲分析模态数量[0,10)	默认5 |
| `YP_BUCKLOADCOMB` | `656` | 656 | 屈曲分析荷载组合 数组 |
| `YP_MEMTYPE` | `657` | 657 | 膜单元类型： 经典膜元(QA4)  改进膜元(NQ6Star) 默认经典膜元QA4 |
| ↳ `YPV_MEMTYPE_QA4` | `( YP_MEMTYPE*YP_RES_SIZE+1 )` | 65701 | 经典膜元(QA4) |
| ↳ `YPV_MEMTYPE_NQ6STAR` | `( YP_MEMTYPE*YP_RES_SIZE+2 )` | 65702 | 改进膜元(NQ6Star) |
| `YP_BZZKL` | `659` | 659 | 板自重扣梁 |
| `YP_EFORCEBYESLAB6` | `660` | 660 | 地震内力按全楼弹性板6计算 |
| `YP_BUCKDZCS` | `661` | 661 | 屈曲分析迭代次数[0,100]	默认10 |
| `YP_BUCKSLWC` | `662` | 662 | 屈曲分析收敛误差[0.0001, 0.2]	默认0.001 |
| `YP_CSQX` | `664` | 664 | 二阶效应 钢结构按屈曲分析模态考虑整体缺陷(初始缺陷)0/1  //20180809改含义为 是否考虑整体缺陷(初始缺陷) |
| `YP_CSQXMOD` | `665` | 665 | 考虑初始缺陷时对应的屈曲模态量 (1-YP_BUCKMODNUM)  用于按屈曲分析模态考虑 即YPV_CSQXTYPE_QQFX |
| `YP_CSQXMAXDIS` | `666` | 666 | 考虑初始缺陷时 最大缺陷值mm (float) 用于按屈曲分析模态考虑 即YPV_CSQXTYPE_QQFX |
| `YP_CALLENR1` | `667` | 667 | 是否计算长度系数置为1 |
| `YP_CSQXDIR` | `668` | 668 | 初始缺陷的方向  用于按屈曲分析模态考虑 即YPV_CSQXTYPE_QQFX |
| ↳ `YPV_CSQXDIR_X` | `( YP_CSQXDIR*YP_RES_SIZE+1 )` | 66801 | X |
| ↳ `YPV_CSQXDIR_Y` | `( YP_CSQXDIR*YP_RES_SIZE+2 )` | 66802 | Y |
| ↳ `YPV_CSQXDIR_Z` | `( YP_CSQXDIR*YP_RES_SIZE+3 )` | 66803 | Z |
| ↳ `YPV_CSQXDIR_COM` | `( YP_CSQXDIR*YP_RES_SIZE+4 )` | 66804 | COM |
| `YP_MEMSET` | `669` | 669 | 求解器 设定内存(MB, 0为自动) |
| `YPE_ZGDZJXS` | `670` | 670 | (欧)混凝土柱抗弯刚度折减系数 (默认1.0) (0, ∝) |
| `YP_XTBFJNJ` | `671` | 671 | 考虑悬挑板对边梁的附加扭矩 (默认0） |
| `YPE_QGDZJXS` | `672` | 672 | (欧美)墙抗弯刚度折减系数 (默认1.0) (0, ∝)   20171103应刘建永需求 改为 板折减系数 |
| `YPE_MOZJXS` | `673` | 673 | (欧美)膜折减系数 (默认1.0) (0, ∝) |
| `YPE_HLKNZJXS` | `674` | 674 | (欧美)砼梁抗扭刚度折减系数  (默认1.0) (0, ∝) |
| `YPE_ZKNGDZJXS` | `675` | 675 | (欧)混凝土柱抗扭刚度折减系数 (默认1.0) (0, ∝) |
| `YPE_GGJKWGDZJXS` | `676` | 676 | (欧)钢构件抗弯刚度折减系数 (默认1.0) (0, ∝) |
| `YPE_GGJZXGDZJXS` | `677` | 677 | (欧)钢构件轴向刚度折减系数 (默认1.0) (0, ∝) |
| `YPE_HLKWZJXS` | `678` | 678 | (欧美)砼梁抗弯刚度折减系数  (默认1.0) (0, ∝) |
| `YP_CSQXTYPE` | `679` | 679 | 二阶效应 考虑整体缺陷(初始缺陷)的类型 |
| ↳ `YPV_CSQXTYPE_QQFX` | `( YP_CSQXTYPE*YP_RES_SIZE+1 )` | 67901 | 按屈曲分析模态考虑整体缺陷(初始缺陷) |
| ↳ `YPV_CSQXTYPE_JXSPL` | `( YP_CSQXTYPE*YP_RES_SIZE+2 )` | 67902 | 按假想水平力  考虑整体缺陷(初始缺陷) |
| ↳ `YPV_SOLVERTYPE_SGMN_CSFD` | `( YP_CSQXTYPE*YP_RES_SIZE+1 )` | 67901 | CSFD |
| ↳ `YPV_SOLVERTYPE_SGMN_PARDDIRECT` | `( YP_CSQXTYPE*YP_RES_SIZE+2 )` | 67902 | Pardiso Direct |
| ↳ `YPV_SOLVERTYPE_SGMN_PARDINTERAIVE` | `( YP_CSQXTYPE*YP_RES_SIZE+3 )` | 67903 | Pardiso Interaive |
| ↳ `YPV_SOLVERTYPE_SGMN_PARDCOUPLE` | `( YP_CSQXTYPE*YP_RES_SIZE+4 )` | 67904 | Pardiso Couple |
| `YP_KLTCQGD` | `680` | 680 | 考虑填充墙刚度 |
| `YP_PDELTADDCS` | `681` | 681 | P-Delta效应迭代次数[0,100]	默认0 |
| `YP_PDELTASLWC` | `682` | 682 | P-Delta效应收敛误差[0.0001, 0.2]	默认0.001 |
| `YP_FXXDDCS` | `683` | 683 | 非线性分析迭代次数[0,100]	默认30 |
| `YP_FXXSLWC` | `684` | 684 | 非线性分析收敛误差[0.0001, 0.2]	默认0.001   非线性计算 Newton-Raphson方法  收敛条件  荷载控制数值 |
| `YP_MGCALCBYPLAN` | `685` | 685 | 门式刚架按平面框架方式计算 |
| `YP_YXFJDHFS` | `686` | 686 | 异形房间导荷方式  异形房间按梯形/三角形导荷”参数，0/1， 默认值是0 |
| `YP_FXXJSFF` | `687` | 687 | 非线性计算方法 |
| ↳ `YPV_FXXJSFF_Newton_Raphson` | `( YP_FXXJSFF*YP_RES_SIZE+1 )` | 68701 | Newton-Raphson 方法 |
| `YP_FXXJZBZSL` | `688` | 688 | 加载步骤数量 [1, ); |
| `YP_FXXSL_NLKZ` | `689` | 689 | 非线性计算 Newton-Raphson方法  收敛条件  能量控制 [0，1] |
| `YP_FXXSL_NLKZVAL` | `690` | 690 | 非线性计算 Newton-Raphson方法  收敛条件  能量控制数值 (0，)  默认0.001 |
| `YP_FXXSL_WYKZ` | `691` | 691 | 非线性计算 Newton-Raphson方法  收敛条件  位移控制 [0，1]  默认1 |
| `YP_FXXSL_WYKZVAL` | `692` | 692 | 非线性计算 Newton-Raphson方法  收敛条件  位移控制数值 (0，)  默认0.001 |
| `YP_FXXSL_HZKZ` | `693` | 693 | 非线性计算 Newton-Raphson方法  收敛条件  荷载控制 [0，1]  默认1 对应数值参数为 YP_FXXSLWC |
| `YP_ZLFDW` | `695` | 695 | 中梁刚度放大系数(抗风） |
| `YP_PDELTAL` | `697` | 697 | 考虑梁元P-Δ效应	//2021.0831添加 |
| `YP_JJFKJL` | `698` | 698 | 铰接时按非框架梁设计 |
| `YP_BLSJ_DXS` | `699` | 699 | 考虑地下室与不考虑地下室模型分别计算，配筋取两个模型结果较大值 |
| `YP_BLSJ_LT` | `615` | 615 | 考虑楼梯刚度与不考虑楼梯刚度模型分别计算，配筋取两个模型结果较大值 |
| `YP_ZQBZJ` | `2310` | 2310 | 增加计算不考虑周期折减系数下的地震位移 |
| `YP_GXGZDJJ` | `2311` | 2311 | 错层主次梁生成刚性杆自动铰接 |
| `YP_BLSJ_QGDFBJS` | `2312` | 2312 | 多个嵌固端模型分别计算，配筋结果取最大值 |
| `YP_BLSJ_ModelNo` | `2313` | 2313 | 子模型个数 |
| `YP_BLSJ_QGDCH` | `2314` | 2314 | 各子模型嵌固端所在层号 int数组，首位为层号数量 从第二个数开始取 |
| `YP_PECWYJXZZXGF` | `2315` | 2315 | 位移角限制执行规范 |
| ↳ `YPV_PECWYJXZZXGF_CECS2020` | `( YP_PECWYJXZZXGF*YP_RES_SIZE+1 )` | 231501 | CECS-2020 |
| ↳ `YPV_PECWYJXZZXGF_SHANGHAI` | `( YP_PECWYJXZZXGF*YP_RES_SIZE+2 )` | 231502 | 上海地标 |
| ↳ `YPV_PECWYJXZZXGF_ZHEJIANG` | `( YP_PECWYJXZZXGF*YP_RES_SIZE+3 )` | 231503 | 浙江地标 |
| `YP_MGXFX` | `2316` | 2316 | 进行敏感性分析 |
| `YP_GZCHNTKJ` | `2317` | 2317 | 钢支撑-混凝土框架 (包络设计) |
| `YP_ZZSGB` | `3800` | 3800 | 最终施工步结束==0  每个施工步结束==1 |
| `YP_KLJHFXX` | `3801` | 3801 | 考虑几何非线性 |
| `YP_KLCLFXX` | `3802` | 3802 | 考虑材料非线性 |
| `YP_SOLVERTYPE_SGMN` | `3803` | 3803 | 求解器类型 施工模拟用 |
| `YP_JZBZS` | `3804` | 3804 | 加载步骤数 |
| `YP_CHECK_WYKZ` | `3805` | 3805 | 位移控制 |
| `YP_CHECK_HZKZ` | `3806` | 3806 | 荷载控制 |
| `YP_EDIT_WYKZ` | `3807` | 3807 | 位移控制 编辑框 |
| `YP_EDIT_HZKZ` | `3808` | 3808 | 荷载控制 编辑框 |
| `YP_SGMI_DDCS` | `3809` | 3809 | 迭代次数 非线性施工模拟 |
| ↳ `YPV_XJKXB_JCL` | `(YP_SEISTYPE*YP_XJKXB+1)` | (非标准公式) | 交叉梁法 |
| ↳ `YPV_XJKXB_YXY` | `(YP_SEISTYPE*YP_XJKXB+2)` | (非标准公式) | 有限元法 |

### 7. 刚度系数，2021.0827添加

原文节注释行（逐字）：

```c
//////////////////////////////////////////////////////////////////////////
//刚度系数，2021.0827添加
```

| 宏名 | 取值 | = 实际值 | 原文注释 |
|---|---|---|---|
| `YP_ZLFD10` | `630` | 630 | 梁刚度放大系数按10《砼规》5.2.4条取值 |
| `YP_ZLFD10M` | `631` | 631 | 梁刚度放大系数上限 |
| `YP_BLFD` | `663` | 663 | 边梁刚度放大系数上限 |
| `YP_ZLFD` | `611` | 611 | 中梁刚度放大系数 |
| `YP_ZLFDE` | `694` | 694 | 中梁刚度放大系数（地震） |
| `YP_BLFDM_SEIS_GDXS` | `2305` | 2305 | 边梁刚度放大系数（地震） |
| `YP_LLZJ` | `610` | 610 | 连梁刚度折减系数（地震） |
| `YP_ZLFD_WIND_GDXS` | `2306` | 2306 | 中梁刚度放大系数（风） |
| `YP_BLFDM_WIND_GDXS` | `2307` | 2307 | 边梁刚度放大系数（风） |
| `YP_LLZJW` | `658` | 658 | 连梁刚度折减系数（风） |
| `YP_ZLFDEUSE` | `696` | 696 | 控制地震荷载下边、中梁放大系数 |
| `YP_WIND_GDXS` | `2308` | 2308 | 控制风荷载下边、中梁放大系数 |
| `YP_DLQ_ZJ` | `3700` | 3700 | 地连墙刚度折减系数  注意：刚度系数页新加参数占用3700-3799字段 240605wx |

### 8. 设计信息

原文节注释行（逐字）：

```c
//////////////////////////////////////////////////////////////////////////
//	设计信息
```

| 宏名 | 取值 | = 实际值 | 原文注释 |
|---|---|---|---|
| `YP_KJKZDJ` | `701` | 701 | 框架抗震等级 |
| ↳ `YPV_KZDJ_T1` | `( YP_KJKZDJ*YP_RES_SIZE+1 )` | 70101 | 特一级 |
| ↳ `YPV_KZDJ_1` | `( YP_KJKZDJ*YP_RES_SIZE+2 )` | 70102 | 一级 |
| ↳ `YPV_KZDJ_2` | `( YP_KJKZDJ*YP_RES_SIZE+3 )` | 70103 | 二级 |
| ↳ `YPV_KZDJ_3` | `( YP_KJKZDJ*YP_RES_SIZE+4 )` | 70104 | 三级 |
| ↳ `YPV_KZDJ_4` | `( YP_KJKZDJ*YP_RES_SIZE+5 )` | 70105 | 四级 |
| ↳ `YPV_KZDJ_NO` | `( YP_KJKZDJ*YP_RES_SIZE+6 )` | 70106 | 非抗震 |
| `YP_GKJKZDJ` | `702` | 702 | 钢框架抗震等级 |
| `YP_JLQKZDJ` | `703` | 703 | 剪力墙抗震等级 |
| `YP_GZKZDJ` | `704` | 704 | 抗震构造措施的抗震等级提高 |
| `YP_XNSJ` | `705` | 705 | 性能设计（全国）		//2011.1111 修改含义为性能设计（全国），去掉YPV_XNSJ_NO  改YP_ISXNSJ为是否进行性能设计的总参数  //20150227 改含义为正截面性能设计  YP_XNSJXJM为斜截面性能设计 |
| ↳ `YPV_XNSJ_NO` | `( YP_XNSJ*YP_RES_SIZE+1 )` | 70501 | 不考虑	//2011.1111版本后不使用该值 |
| ↳ `YPV_XNSJ_BQF` | `( YP_XNSJ*YP_RES_SIZE+2 )` | 70502 | 不屈服 |
| ↳ `YPV_XNSJ_TX` | `( YP_XNSJ*YP_RES_SIZE+3 )` | 70503 | 弹性 |
| ↳ `YPV_XNSJ_QF` | `( YP_XNSJ*YP_RES_SIZE+4 )` | 70504 | 屈服 |
| ↳ `YPV_XNSJ_JXCZL` | `( YP_XNSJ*YP_RES_SIZE+5 )` | 70505 | 极限承载力(减震性能包络设计与上海抗规用) |
| ↳ `YPV_XNSJ_ZXJM` | `( YP_XNSJ*YP_RES_SIZE+6 )` | 70506 | 最小截面(上海抗规用) |
| `YP_GZCY` | `706` | 706 | 钢柱计算长度系数按有侧移计算X向  YP_GZCYY为Y向 |
| `YP_72164` | `707` | 707 | 剪力墙构造边缘构件的设计执行高规7.2.17-4 |
| `YP_ZPJ` | `708` | 708 | 柱配筋计算方法，单偏压或双偏压 |
| ↳ `YPV_DPY` | `( YP_ZPJ*YP_RES_SIZE+1 )` | 70801 | 单偏压 |
| ↳ `YPV_SPY` | `( YP_ZPJ*YP_RES_SIZE+2 )` | 70802 | 双偏压 |
| `YP_LBHC` | `709` | 709 | 梁保护层厚度 |
| `YP_ZBHC` | `710` | 710 | 柱保护层厚度 |
| `YP_XGHNT` | `711` | 711 | 型钢混凝土构件设计依据 |
| ↳ `YPV_JGJ138` | `( YP_XGHNT*YP_RES_SIZE+1 )` | 71101 | 《型钢混凝土组合结构技术规程》JGJ138-2001 |
| ↳ `YPV_YB9082` | `( YP_XGHNT*YP_RES_SIZE+2 )` | 71102 | 《钢骨混凝土结构技术规程》YB9082-2006 |
| `YP_ZZYBKJ` | `712` | 712 | 框架柱的轴压比限值按框架结构采用 |
| `YP_KJLYAJIN` | `713` | 713 | 框架梁梁端配筋考虑受压钢筋影响 |
| `YP_QZDZ` | `714` | 714 | 墙柱配筋设计考虑端柱  2012.0409 改“翼缘墙（或端柱）”为端柱 |
| `YP_RECT_T` | `715` | 715 | 矩形混凝土梁按T形梁配筋 |
| `YP_LLDCPJ` | `716` | 716 | 连梁按对称配筋设计 |
| `YP_RECT_T_BYJ` | `717` | 717 | 考虑翼缘板中的钢筋为受压钢筋 |
| `YP_RECT_T_BROU` | `718` | 718 | 板中受力钢筋配筋率(%) |
| `YP_BYGJ_SZYJ` | `719` | 719 | 构造边缘构件尺寸设计依据 |
| ↳ `YP_BYGJ_KG645` | `( YP_BYGJ_SZYJ*YP_RES_SIZE+1 )` | 71901 | 《抗规》GB50011 第6.4.5条 |
| ↳ `YP_BYGJ_GG7216` | `( YP_BYGJ_SZYJ*YP_RES_SIZE+2 )` | 71902 | 《高规》JGJ3-2010 第7.2.16条 |
| ↳ `YP_BYGJ_HG11719` | `( YP_BYGJ_SZYJ*YP_RES_SIZE+3 )` | 71903 | 《砼规》GB50010-2010 第11.7.19条 |
| `YP_BYGJ_MINDIS` | `720` | 720 | 边缘构件合并距离(mm)（0~10000）(300) |
| `YP_BYGJ_MOD` | `721` | 721 | 边缘构件尺寸取整模数(mm)(50) |
| `YP_DQBYGJZTPJ` | `722` | 722 | 短肢边缘构件合并距离(mm)（>=0）(600) |
| `YP_QZYYQ` | `723` | 723 | 墙柱配筋设计考虑翼缘墙 (0~1)	//2012.0409增加 |
| `YP_JHJSZJKB` | `724` | 724 | 按简化方法计算柱剪跨比(Hn/2h0) (0~1) (默认1) |
| `YP_DBJQQALLYBZ` | `725` | 725 | 约束边缘构件层全部设为约束边缘构件(0~1) (默认0) 2013.0301由“底部加强区全部设为约束边缘构件”改为当前含义 |
| `YP_BYGJ_LXAZ` | `726` | 726 | 面外梁下生成暗柱边缘构件 0、1、2 分别为	 全都生成、全不生成、铰接梁不生成 |
| `YPV_BYGJ_LXAZ_NONE` | `0` | 0 | 全不生成 |
| `YPV_BYGJ_LXAZ_CREATE` | `1` | 1 | 全都生成 |
| `YPV_BYGJ_LXAZ_NOTHINGE` | `2` | 2 | 铰接梁不生成 |
| `YP_BYGJ_YSYYLENLC` | `727` | 727 | 归入阴影区的λ/2区最大长度[0~∞) 20160315修改  //约束边缘构件阴影区长度取Lc (0~1) (默认0) |
| `YP_AUTOQRZC` | `728` | 728 | 按《钢结构规范》5.3.3-2自动判断强弱支撑 (0~1) (默认0)  YP_GZCY为0时有效 |
| `YP_LZDYWSJ` | `729` | 729 | 梁自动压弯设计 梁有轴压力时自动按压弯设计(0~1) (默认0) |
| `YP_LZLTJ` | `730` | 730 | 梁按压弯设计控制轴压比       (默认0.4) |
| `YP_LDNL2ZZB` | `731` | 731 | 梁端内力取值位置，浮点值(0.0～1.0) (0-节点，1-支座边)  (默认0) |
| `YP_YSKZQSGF` | `732` | 732 | 验算一级抗震墙施工缝(0、1) (默认1) |
| `YP_YSBYGJ_GD` | `733` | 733 | 约束边缘构件尺寸依据《广东高规》设计 (0~1) (默认0) |
| `YP_GZCYY` | `734` | 734 | 钢柱计算长度系数按有侧移计算 Y向  YP_GZCY为X向 |
| `YP_ZYBBYG` | `735` | 735 | 非抗震时按重力荷载代表值计算柱轴压比 |
| `YP_BYGJ_JSPJ` | `736` | 736 | 按边缘构件轮廓计算配筋(0~1) (默认0) |
| `YP_DHZDHB` | `737` | 737 | 按叠合柱设计的叠合比m [0,1) |
| `YPE_STLSYSSTRENGTH` | `738` | 738 | (欧)结构超强系数 >=1 |
| `YPE_STLMATSTRENGTH` | `739` | 739 | (欧)材料超强系数 >=1 |
| `YPE_STLSECTTYPE` | `740` | 740 | (欧)截面分类 |
| ↳ `YPEV_STLSECTTYPE_CLASS1` | `( YPE_STLSECTTYPE*YP_RES_SIZE+1 )` | 74001 | class 1 |
| ↳ `YPEV_STLSECTTYPE_CLASS2` | `( YPE_STLSECTTYPE*YP_RES_SIZE+2 )` | 74002 | class 2 |
| ↳ `YPEV_STLSECTTYPE_CLASS3` | `( YPE_STLSECTTYPE*YP_RES_SIZE+3 )` | 74003 | class 3 |
| `YP_JGJ99_2015` | `741` | 741 | 执行《高钢规》JGJ99-2015 (0~1) (默认1)(6.1版本默认为0) |
| `YP_ZHLSGHZ` | `742` | 742 | 组合梁施工荷载(kN/m2)(>=0) (默认1.5) |
| `YP_MGA08` | `743` | 743 | 执行门规GB51022附录A.0.8 (0~1) (默认0) |
| `YP_MGCOLBYGB51022` | `744` | 744 | 执行门规GB51022附录A (0~1) (默认1) 选中按门规51022执行，否则按CECS102:2012执行 |
| `YP_MAXCORBARD` | `745` | 745 | 双偏压时角筋最大直径 (25~40) (默认32) |
| `YP_GB51022` | `746` | 746 | 门刚规范用GB51022-2015 (0-1) (默认1) |
| `YPUS_JHJSBYGJ` | `747` | 747 | 按简化方法(C&T)计算边缘构件int |
| `YPUS_BYGJZDPJL` | `748` | 748 | 边缘构件纵筋最大配筋率    (默认0.03) |
| `YP_JMKHB` | `749` | 749 | 按宽厚比等级控制局部稳定  Control section width ratio according to steel structure specification |
| `YP_JMKHBDJ` | `750` | 750 | 截面宽厚比等级 (S1-S4)(默认S3)  Section width ratio grade |
| ↳ `YPV_JMKHBDJ_S1` | `( YP_JMKHBDJ*YP_RES_SIZE+1 )` | 75001 | S1 |
| ↳ `YPV_JMKHBDJ_S2` | `( YP_JMKHBDJ*YP_RES_SIZE+2 )` | 75002 | S2 |
| ↳ `YPV_JMKHBDJ_S3` | `( YP_JMKHBDJ*YP_RES_SIZE+3 )` | 75003 | S3 |
| ↳ `YPV_JMKHBDJ_S4` | `( YP_JMKHBDJ*YP_RES_SIZE+4 )` | 75004 | S4 |
| ↳ `YPV_JMKHBDJ_BS1` | `( YP_JMKHBDJ*YP_RES_SIZE+5 )` | 75005 | BS1 |
| ↳ `YPV_JMKHBDJ_BS2` | `( YP_JMKHBDJ*YP_RES_SIZE+6 )` | 75006 | BS2 |
| ↳ `YPV_JMKHBDJ_BS3` | `( YP_JMKHBDJ*YP_RES_SIZE+7 )` | 75007 | BS3 |
| ↳ `YPV_JMKHBDJ_S5` | `( YP_JMKHBDJ*YP_RES_SIZE+8 )` | 75008 | S5 |
| `YP_ZCJMKHBDJ` | `751` | 751 | 支撑杆件截面宽厚比等级(S1-BS3)(默认S3) Width ratio grade of brace member section |
| `YP_GB50017_2017` | `752` | 752 | 执行《钢结构设计标准》(GB50017-2017) |
| `YP_SPYFBQGKB` | `753` | 753 | 双偏压腹板墙最大截面高宽比  默认12 >0   Maximum width ratio of the maximum cross section of double bias web wall |
| `YP_SPYFBQGD` | `754` | 754 | 双偏压腹板墙最大截面高度(mm) 默认2400 >0 Maximum cross section height of double biased web wall |
| `YP_GLZLTJ` | `755` | 755 | 钢梁按压弯设计控制轴压比       (默认0.4) |
| `YP_XYYWD627` | `756` | 756 | 按钢规6.2.7验算梁下翼缘稳定 |
| `YP_ZYGJKLWDZHDEL` | `757` | 757 | 仅轴向受力构件考虑温度组合 |
| `YP_MGJMKHB` | `758` | 758 | 门刚构件按宽厚比等级控制局部稳定 |
| `YP_MGJMKHBDJ` | `759` | 759 | 截面宽厚比等级 (S1-S4)(默认S3) 值取YPV_JMKHBDJ_S1到YPV_JMKHBDJ_S4 Section width ratio grade |
| `YP_ZHLJMKHBDJ` | `760` | 760 | 组合梁截面宽厚比等级 (S1-S4)(默认S2)  Section width ratio grade |
| `YP_LWBJKLLWXY` | `761` | 761 | 冷弯薄壁构件考虑冷弯效应	 《冷弯薄壁型钢钢结构技术规范》4.2.3 |
| `YP_SGZHLB` | `762` | 762 | 组合类别  施工阶段验算 |
| ↳ `YPV_SGZHLB_BASE` | `( YP_SGZHLB*YP_RES_SIZE+1 )` | 76201 | 组合类别  基本组合 |
| ↳ `YPV_SGZHLB_STAND` | `( YP_SGZHLB*YP_RES_SIZE+2 )` | 76202 | 组合类别  标准组合 |
| `YP_YXZZKLGDJ` | `763` | 763 | 异形柱配筋计算只考虑固定钢筋  specially shaped column |
| `YP_KJLKHB_UPF` | `764` | 764 | 框架翼缘宽厚比限值 上翼缘 up flange of fram beam   width-thickness ratio, web depth-thickness ratio   Limit Value of Width-to-Thickness Ratios of Steel Beam |
| `YP_KJLKHB_DWNF` | `765` | 765 | 框架翼缘宽厚比限值 下翼缘 down flange of fram beam |
| `YP_KJLKHB_WEB` | `766` | 766 | 框架翼缘宽厚比限值 腹板   web of fram beam  depth-thickness ratio |
| `YP_NKJLKHB_UPF` | `767` | 767 | 非框架翼缘宽厚比限值 上翼缘 up flange of Non fram beam |
| `YP_NKJLKHB_DWNF` | `768` | 768 | 非框架翼缘宽厚比限值 下翼缘 down flange of Non fram beam |
| `YP_NKJLKHB_WEB` | `769` | 769 | 非框架翼缘宽厚比限值 腹板 web of Non fram beam web |
| `YP_SHEARLINKDIS` | `770` | 770 | 抗剪连接件单侧边距（mm) float   Unilateral margin of shear connector |
| `YP_UBEAMSAFERATIO` | `771` | 771 | 无筋外包U形钢组合截面效应抗力比限值 float   Unilateral margin of shear connector |
| `YP_CLINK_FLAGT` | `772` | 772 | 槽钢连接件翼缘厚（mm) float  槽钢连接件尺寸(mm) Channel Steel Connector Size   Flag thick |
| `YP_CLINK_WEBT` | `773` | 773 | 槽钢连接件腹板厚（mm) float   Channel Steel Connector Size   Web thick |
| `YP_CLINK_HF` | `774` | 774 | 槽钢连接件焊角尺寸（mm) float   Channel Steel Connector Size   Weld hf |
| `YP_CLINK_FLAGW` | `775` | 775 | 槽钢连接件翼缘宽（mm) float  槽钢连接件尺寸(mm) Channel Steel Connector Size   Flag width |
| `YP_DBJQQZYB` | `776` | 776 | 2021.9.24 增加一个关于约束边缘构件判断时使用轴压比取值的控制参数 |
| `YP_CDXSKLQGD` | `778` | 778 | 2021.11.23 增加新的参数钢柱计算长度系数考虑嵌固端 |
| `YP_JXGGHNT` | `779` | 779 | 矩形钢管混凝土构件设计依据 |
| ↳ `YPV_JGJ138_2016` | `( YP_JXGGHNT*YP_RES_SIZE+1 )` | 77901 | 《组合结构设计规范》JGJ 138-2016” |
| ↳ `YPV_CECS159_2004` | `( YP_JXGGHNT*YP_RES_SIZE+2 )` | 77902 | “《矩形钢管混凝土结构技术规程》 CECS 159：2004 ” |
| `YP_ZJKBCYCG` | `780` | 780 | 柱剪跨比采用层高 |
| `YP_GB50017_2017XD` | `781` | 781 | 执行《钢结构设计标准》(GB50017-2017修订稿) |
| `YP_CXFSXS` | `782` | 782 | 成型方式系数 |
| `YP_GFBNZZLTSYYSYCXSW` | `783` | 783 | 光伏板能阻止檩条上翼缘受压侧向失稳 |
| `YP_GLSWKLJLGDYX` | `784` | 784 | 钢梁受弯考虑剪力过大影响 |
| `YP_ZDJSFHBHCHD` | `785` | 785 | 自动计算防火保护层厚度 |
| `YP_GJYDJXCQDB` | `786` | 786 | 箍筋与对角斜筋强度比 |
| `YP_SGJDYSMX` | `787` | 787 | 施工阶段验算模型 |
| `YP_XJHNTTXML` | `788` | 788 | 现浇混凝土弹性模量(×10^4 MPa) |
| `YP_PEC` | `789` | 789 | 包覆钢PEC组合梁 |
| ↳ `YPV_PEC_CLASS1` | `( YP_PEC*YP_RES_SIZE+1 )` | 78901 | class1 |
| ↳ `YPV_PEC_CLASS2` | `( YP_PEC*YP_RES_SIZE+2 )` | 78902 | class2 |
| `YP_MGLYZLSAYWGJSJ` | `790` | 790 | 门刚梁有轴力时按压弯构件设计 |
| `YP_MGLAYWGJYSPMWDX` | `791` | 791 | 门刚梁按压弯构件验算平面内稳定性 |
| `YP_ISQHFKJL` | `792` | 792 | 墙厚≤(350)mm是否按非框架梁设计 |
| `YP_QHFKJL` | `793` | 793 | 墙厚≤(350)mm按非框架梁设计 350为默认值 |
| `YP_GZNBZLTXYYWDX` | `794` | 794 | 构造能保证檩条下翼缘稳定性 |
| `YP_GB50011_2016` | `795` | 795 | 长细比、宽厚比执行《抗规》GB50011-2016 |
| `YP_PECCOLM` | `796` | 796 | 包覆钢PEC组合柱 |
| ↳ `YPV_PECCOLM_CLASS1` | `( YP_PECCOLM*YP_RES_SIZE+1 )` | 79601 | class1 |
| ↳ `YPV_PECCOLM_CLASS2` | `( YP_PECCOLM*YP_RES_SIZE+2 )` | 79602 | class2 |
| `YP_RMFKDXS` | `797` | 797 | 人民防空地下室设计依据 |
| ↳ `YPV_GB50038_2005` | `( YP_RMFKDXS*YP_RES_SIZE+1 )` | 79701 | 《人民防空地下室设计规范》2005 |
| ↳ `YPV_GB50038_2005_2023` | `( YP_RMFKDXS*YP_RES_SIZE+2 )` | 79702 | 《人民防空地下室设计规范》2023 |
| `YP_LTZY` | `798` | 798 | 拉条作用 光伏240425wx |
| ↳ `YPV_YSLTSYY` | `( YP_LTZY*YP_RES_SIZE+1 )` | 79801 | 约束檩条上翼缘 |
| ↳ `YPV_YSLTSXYY` | `( YP_LTZY*YP_RES_SIZE+2 )` | 79802 | 约束檩条上、下翼缘 |
| ↳ `YPV_YSLTXYY` | `( YP_LTZY*YP_RES_SIZE+3 )` | 79803 | 约束檩条下翼缘 |
| `YP_SWGJWDXS_KSI` | `799` | 799 | 受弯构件稳定系数计算用ξ 光伏240604wx |
| ↳ `YPV_SWGJWDXS_KSI_1` | `( YP_SWGJWDXS_KSI*YP_RES_SIZE+1 )` | 79901 | 1 |
| ↳ `YPV_SWGJWDXS_KSI_2` | `( YP_SWGJWDXS_KSI*YP_RES_SIZE+2 )` | 79902 | 2 |

### 9. 材料配筋信息

原文节注释行（逐字）：

```c
//////////////////////////////////////////////////////////////////////////
//	材料配筋信息
```

| 宏名 | 取值 | = 实际值 | 原文注释 |
|---|---|---|---|
| `YP_HNTRZ` | `801` | 801 | 混凝土容重 |
| `YP_GANGH` | `802` | 802 | 钢号 |
| ↳ `YPV_GH_Q235` | `( YP_GANGH*YP_RES_SIZE+1 )` | 80201 | Q235 |
| ↳ `YPV_GH_Q345` | `( YP_GANGH*YP_RES_SIZE+2 )` | 80202 | Q345 |
| ↳ `YPV_GH_Q390` | `( YP_GANGH*YP_RES_SIZE+3 )` | 80203 | Q390 |
| ↳ `YPV_GH_Q420` | `( YP_GANGH*YP_RES_SIZE+4 )` | 80204 | Q420 |
| ↳ `YPV_GH_Q460` | `( YP_GANGH*YP_RES_SIZE+5 )` | 80205 | Q460 |
| ↳ `YPV_GH_Q500` | `( YP_GANGH*YP_RES_SIZE+6 )` | 80206 | Q500 |
| ↳ `YPV_GH_Q560` | `( YP_GANGH*YP_RES_SIZE+7 )` | 80207 | Q560	//之前起名错误，应该用550 但此宏定义使用的地方较多，暂保留，含义同YPV_GH_Q550 |
| ↳ `YPV_GH_Q550` | `( YP_GANGH*YP_RES_SIZE+7 )` | 80207 | Q550 |
| ↳ `YPV_GH_Q620` | `( YP_GANGH*YP_RES_SIZE+8 )` | 80208 | Q620 |
| ↳ `YPV_GH_Q690` | `( YP_GANGH*YP_RES_SIZE+9 )` | 80209 | Q690 |
| ↳ `YPV_GH_Q235GJ` | `( YP_GANGH*YP_RES_SIZE+10 )` | 80210 | Q235GJ |
| ↳ `YPV_GH_Q345GJ` | `( YP_GANGH*YP_RES_SIZE+11 )` | 80211 | Q345GJ |
| ↳ `YPV_GH_Q390GJ` | `( YP_GANGH*YP_RES_SIZE+12 )` | 80212 | Q390GJ |
| ↳ `YPV_GH_Q420GJ` | `( YP_GANGH*YP_RES_SIZE+13 )` | 80213 | Q420GJ |
| ↳ `YPV_GH_Q460GJ` | `( YP_GANGH*YP_RES_SIZE+14 )` | 80214 | Q460GJ |
| ↳ `YPV_GH_Q355` | `( YP_GANGH*YP_RES_SIZE+15 )` | 80215 | Q355 |
| ↳ `YPV_GH_Q355N` | `( YP_GANGH*YP_RES_SIZE+16 )` | 80216 | Q355N |
| ↳ `YPV_GH_Q390N` | `( YP_GANGH*YP_RES_SIZE+17 )` | 80217 | Q390N |
| ↳ `YPV_GH_Q420N` | `( YP_GANGH*YP_RES_SIZE+18 )` | 80218 | Q420N |
| ↳ `YPV_GH_Q460N` | `( YP_GANGH*YP_RES_SIZE+19 )` | 80219 | Q460N |
| ↳ `YPV_GH_Q355M` | `( YP_GANGH*YP_RES_SIZE+20 )` | 80220 | Q355M |
| ↳ `YPV_GH_Q390M` | `( YP_GANGH*YP_RES_SIZE+21 )` | 80221 | Q390M |
| ↳ `YPV_GH_Q420M` | `( YP_GANGH*YP_RES_SIZE+22 )` | 80222 | Q420M |
| ↳ `YPV_GH_Q460M` | `( YP_GANGH*YP_RES_SIZE+23 )` | 80223 | Q460M |
| ↳ `YPV_GH_ES235` | `( YP_GANGH*YP_RES_SIZE+51 )` | 80251 | S235 |
| ↳ `YPV_GH_ES275` | `( YP_GANGH*YP_RES_SIZE+52 )` | 80252 | S275 |
| ↳ `YPV_GH_ES355` | `( YP_GANGH*YP_RES_SIZE+53 )` | 80253 | S355 |
| ↳ `YPV_GH_ES450` | `( YP_GANGH*YP_RES_SIZE+54 )` | 80254 | S450 |
| ↳ `YPV_GH_US36` | `( YP_GANGH*YP_RES_SIZE+71 )` | 80271 | US A36 |
| ↳ `YPV_GH_US53GrB` | `( YP_GANGH*YP_RES_SIZE+72 )` | 80272 | US A53(Gr.B) |
| ↳ `YPV_GH_US500GrB42` | `( YP_GANGH*YP_RES_SIZE+73 )` | 80273 | US A500(Gr.B42) |
| ↳ `YPV_GH_US500GrB46` | `( YP_GANGH*YP_RES_SIZE+74 )` | 80274 | US A500(Gr.B46) |
| ↳ `YPV_GH_US500GrC46` | `( YP_GANGH*YP_RES_SIZE+75 )` | 80275 | US A500(Gr.C46) |
| ↳ `YPV_GH_US500GrC50` | `( YP_GANGH*YP_RES_SIZE+76 )` | 80276 | US A500(Gr.C50) |
| ↳ `YPV_GH_US572Gr50` | `( YP_GANGH*YP_RES_SIZE+77 )` | 80277 | US A572(Gr.50) |
| ↳ `YPV_GH_US992` | `( YP_GANGH*YP_RES_SIZE+78 )` | 80278 | US A992 |
| `YP_GRZ` | `803` | 803 | 钢容重 |
| `YP_QTRZ` | `804` | 804 | 砌体容重 |
| `YP_QGLRZ` | `805` | 805 | 轻骨料混凝土容重 |
| `YP_QGLMD` | `806` | 806 | 轻骨料混凝土密度等级 |
| `YP_GJMB` | `807` | 807 | 钢构件截面净毛面积比 |
| `YP_BEZHUJIN` | `808` | 808 | 梁主筋级别 |
| `YP_CLZHUJIN` | `809` | 809 | 柱主筋级别 |
| `YP_WAZHUJIN` | `810` | 810 | 墙主筋级别 |
| `YP_BEGUJIN` | `811` | 811 | 梁箍筋级别 |
| ↳ `YPV_HPB235` | `( YP_BEGUJIN*YP_RES_SIZE+1 )` | 81101 | HPB235 |
| ↳ `YPV_HPB300` | `( YP_BEGUJIN*YP_RES_SIZE+2 )` | 81102 | HPB300 |
| ↳ `YPV_HRB335` | `( YP_BEGUJIN*YP_RES_SIZE+3 )` | 81103 | HRB335 |
| ↳ `YPV_HRB400` | `( YP_BEGUJIN*YP_RES_SIZE+4 )` | 81104 | HRB400 |
| ↳ `YPV_HRB500` | `( YP_BEGUJIN*YP_RES_SIZE+5 )` | 81105 | HRB500 |
| ↳ `YPV_LZDL550` | `( YP_BEGUJIN*YP_RES_SIZE+6 )` | 81106 | LZDL550 |
| ↳ `YPV_HTRB600` | `( YP_BEGUJIN*YP_RES_SIZE+7 )` | 81107 | HRB600 |
| ↳ `YPV_HTRB630` | `( YP_BEGUJIN*YP_RES_SIZE+8 )` | 81108 | HRB630 |
| ↳ `YPV_CRB600H` | `( YP_BEGUJIN*YP_RES_SIZE+9 )` | 81109 | CRB600H |
| ↳ `YPV_HRB635` | `( YP_BEGUJIN*YP_RES_SIZE+10 )` | 81110 | HG6/C(新) HRB635 名称修改于20240109 |
| ↳ `YPV_HRB600_STD` | `( YP_BEGUJIN*YP_RES_SIZE+11 )` | 81111 | HRB600(盛泰达) |
| ↳ `YPV_HRB650_STD` | `( YP_BEGUJIN*YP_RES_SIZE+12 )` | 81112 | HRB650(盛泰达) |
| ↳ `YPV_HRBF600E_HN` | `( YP_BEGUJIN*YP_RES_SIZE+13 )` | 81113 | HRBF600E(河南) |
| ↳ `YPV_HTRB630E` | `( YP_BEGUJIN*YP_RES_SIZE+14 )` | 81114 | HTRB630E |
| ↳ `YPV_EUB400` | `( YP_BEGUJIN*YP_RES_SIZE+52 )` | 81152 | B400	欧规钢筋 |
| ↳ `YPV_EUB500` | `( YP_BEGUJIN*YP_RES_SIZE+53 )` | 81153 | B500 |
| ↳ `YPV_EUB600` | `( YP_BEGUJIN*YP_RES_SIZE+54 )` | 81154 | B600 |
| ↳ `YPV_USG40` | `( YP_BEGUJIN*YP_RES_SIZE+75 )` | 81175 | USG40	美标钢筋 |
| ↳ `YPV_USG60` | `( YP_BEGUJIN*YP_RES_SIZE+76 )` | 81176 | USG60 |
| ↳ `YPV_USG75` | `( YP_BEGUJIN*YP_RES_SIZE+77 )` | 81177 | USG75 |
| ↳ `YPV_PRESTRESSFPTK_CSJX` | `( YP_BEGUJIN*YP_RES_SIZE+97 )` | 81197 | 钢绞线极限强度标准值  长沙巨星梁预应力筋钢绞线 |
| ↳ `YPV_PRESTRESSFPY_CSJX` | `( YP_BEGUJIN*YP_RES_SIZE+98 )` | 81198 | 钢绞线抗拉强度设计值 |
| ↳ `YPV_PRESTRESSFPY2_CSJX` | `( YP_BEGUJIN*YP_RES_SIZE+99 )` | 81199 | 钢绞线抗压强度设计值 |
| `YP_CLGUJIN` | `812` | 812 | 柱箍筋级别 |
| `YP_WAHRJIN` | `813` | 813 | 墙水平分布筋级别 |
| `YP_WAVTJIN` | `814` | 814 | 墙竖向分布筋级别 |
| `YP_EDGEGUJIN` | `815` | 815 | 边缘构件箍筋级别 |
| `YP_LGJD` | `816` | 816 | 梁箍筋间距（mm） |
| `YP_ZGJD` | `817` | 817 | 柱箍筋间距（mm） |
| `YP_QHRD` | `818` | 818 | 墙水平分布筋间距（mm） |
| `YP_QVTROU` | `819` | 819 | 墙竖向分布筋配筋率（%） |
| `YP_QJROUFL` | `820` | 820 | 结构底部需要单独指定墙竖向分布筋配筋率的层数(旧)，只存一个楼层数 用于20130903以前版本 |
| `YP_QJROU` | `821` | 821 | 结构底部需要单独指定的墙竖向分布筋配筋率 |
| `YP_WAMAT` | `822` | 822 | 墙主要材料(建模?) |
| `YP_QJROUFLRS` | `823` | 823 | 结构底部需要单独指定墙竖向分布筋配筋率的楼层号数组（新），用于20130903及以后版本 |
| `YP_TUS_KXMFY` | `824` | 824 | 空心模水平分布筋强度设计值 float |
| `YP_TUS_KXMDIA` | `825` | 825 | 空心模水平分布筋直径 float |
| `YP_TUS_KXMDIST` | `826` | 826 | 空心模水平分布筋间距 float |
| `YPE_ALPHACC` | `827` | 827 | 欧标 Alpha cc压 [0, 1]  Alpha cc(compression) |
| `YPE_ALPHACT` | `828` | 828 | 欧标 Alpha ct拉 [0, 1]  Alpha ct(tension) |
| `YP_QHORROUMIN` | `829` | 829 | 墙最小水平分布筋配筋率（%） |
| `YP_STRZ` | `830` | 830 | 索体容重 |
| `YP_LHJRZ` | `831` | 831 | 铝合金容重 |
| `YP_HNTFXXS` | `832` | 832 | 混凝土分项系数 |
| `YP_GJFXXS` | `833` | 833 | 钢筋分项系数 |
| `YP_GCFXXS_QD` | `834` | 834 | 钢材分项系数(强度) |
| `YP_GCFXXS_WD` | `835` | 835 | 钢材分项系数(稳定) |
| `YP_GCFXXS_JJMDL` | `836` | 836 | 钢材分项系数(净截面断裂) |

原文本节其余 `#define`（逐字）：

```c
#define YP_FY_HPB235 YPV_HPB235	// HPB235钢筋强度设计值
#define YP_FY_HPB300 YPV_HPB300	// HPB300钢筋强度设计值
#define YP_FY_HRB335 YPV_HRB335	// HRB335钢筋强度设计值
#define YP_FY_HRB400 YPV_HRB400	// HRB400钢筋强度设计值
#define YP_FY_HRB500 YPV_HRB500	// HRB500钢筋强度设计值
#define YP_FY_LZDL550 YPV_LZDL550	// LZDL550钢筋强度设计值
#define YP_FY_HTRB600 YPV_HTRB600	// HRB600钢筋强度设计值
#define YP_FY_HTRB630 YPV_HTRB630	// T63钢筋强度设计值
#define YP_FY_CRB600H YPV_CRB600H	// CRB600H钢筋强度设计值
#define YP_FY_HRB635 YPV_HRB635		// HG6/C钢筋强度设计值(新) HRB635钢筋强度设计值  名称修改于20240109
#define YP_FY_EUB400 YPV_EUB400	// B400钢筋强度设计值 	欧规钢筋
#define YP_FY_EUB500 YPV_EUB500	// B500钢筋强度设计值
#define YP_FY_EUB600 YPV_EUB600	// B600钢筋强度设计值
#define YP_FY_USG40 YPV_USG40	// USG40钢筋强度设计值
#define YP_FY_USG60 YPV_USG60	// USG60钢筋强度设计值
#define YP_FY_USG75 YPV_USG75	// USG75钢筋强度设计值
#define YP_FY_HRB600_STD YPV_HRB600_STD	// HRB600(盛泰达)钢筋强度设计值
#define YP_FY_HRB650_STD YPV_HRB650_STD	// HRB650(盛泰达)钢筋强度设计值
#define YP_FY_HRBF600E_HN	YPV_HRBF600E_HN	 // HRBF600E(河南)钢筋强度设计值
#define YP_FY_HTRB630E	    YPV_HTRB630E	 // HTRB630E	  钢筋强度设计值
#define YP_FY_PRESTRESSFPTK_CSJX YPV_PRESTRESSFPTK_CSJX	 // 钢绞线极限强度标准值  长沙巨星梁预应力筋钢绞线
#define YP_FY_PRESTRESSFPY_CSJX	 YPV_PRESTRESSFPY_CSJX	 // 钢绞线抗拉强度设计值
#define YP_FY_PRESTRESSFPY2_CSJX YPV_PRESTRESSFPY2_CSJX	 // 钢绞线抗压强度设计值
```

### 10. 荷载组合

原文节注释行（逐字）：

```c
//////////////////////////////////////////////////////////////////////////
//	荷载组合
```

| 宏名 | 取值 | = 实际值 | 原文注释 |
|---|---|---|---|
| `YP_ZYXXS` | `901` | 901 | 结构重要性系数 |
| `YP_DLFX` | `902` | 902 | 恒荷载分项系数 |
| `YP_LLFX` | `903` | 903 | 活荷载分项系数 |
| `YP_LLZH` | `904` | 904 | 活荷载组合值系数 |
| `YP_LLTZ` | `905` | 905 | 考虑结构设计使用年限的活荷载调整系数 |
| `YP_WINDFX` | `906` | 906 | 风荷载分项系数 |
| `YP_WINDZH` | `907` | 907 | 风荷载组合值系数 |
| `YP_WINDDZ` | `908` | 908 | 风荷载是否参与地震组合 |
| `YP_HRDZFX` | `909` | 909 | 水平地震分项系数 |
| `YP_VTDZFX` | `910` | 910 | 竖向地震分项系数 |
| `YP_VTDZZH` | `911` | 911 | 是否考虑竖向地震为主的组合 |
| `YP_ZDYZH` | `912` | 912 | 自定义组合 |
| `YP_WINDFD` | `913` | 913 | 承载力设计时风荷载效应放大系数 |
| `YP_DCDBZXS` | `914` | 914 | 吊车荷载重力荷载代表值系数 |
| `YP_LOADCOMB` | `915` | 915 | 是否采用自定义组合 |
| `YP_WDZH` | `916` | 916 | 温度荷载组合值系数 仅考虑恒活荷载参与的组合 默认0.6 |
| `YP_WDZHWIND` | `917` | 917 | 温度荷载组合值系数 风荷载参与的组合 默认0 |
| `YP_WDZHSEIS` | `918` | 918 | 温度荷载组合值系数 地震作用载参与的组合 默认0 |
| `YP_CUSTOMDLNAME` | `919` | 919 | 自定义恒载工况名称  用yjkGetStringVectorSPara取值   也可用LPVARIANT yjkGetSPara(paraID) 取值，然后用Variant2StringArray转为CStringArray |
| `YP_CUSTOMDL` | `920` | 920 | 自定义恒载及组合系数等 数据 |
| `YP_CUSTOMLLNAME` | `921` | 921 | 自定义活载工况名称  用yjkGetStringVectorSPara取值   也可用LPVARIANT yjkGetSPara(paraID) 取值，然后用Variant2StringArray转为CStringArray |
| `YP_CUSTOMLL` | `922` | 922 | 自定义活载组合系数  取值方式同YP_CUSTOMDL |
| `YP_CUSTOMLLZYJ` | `923` | 923 | 自定义活载准永久值系数  取值方式同YP_CUSTOMDL |
| `YP_CUSTOMDLID` | `924` | 924 | 自定义恒载ID数组 与  YP_CUSTOMDLNAME个数相同，一一对位 |
| `YP_CUSTOMLLID` | `925` | 925 | 自定义活载ID数组 与  YP_CUSTOMLLNAME个数相同，一一对位 |
| `YP_CUSTOMLLBZ` | `926` | 926 | 自定义活载标准组合系数  取值方式同YP_CUSTOMDL |
| `YP_CUSTOMLLPY` | `927` | 927 | 自定义活载频遇组合系数  取值方式同YP_CUSTOMDL |
| `YP_LLPY` | `928` | 928 | 活荷载频遇值系数 |
| `YP_LLZYJ` | `929` | 929 | 活荷载准永久值系数 |
| `YP_DCZH` | `930` | 930 | 吊车荷载组合值系数 |
| `YP_DCPY` | `931` | 931 | 吊车荷载频遇值系数 |
| `YP_DCZYJ` | `932` | 932 | 吊车荷载准永久值系数 |
| `YP_WINDPY` | `933` | 933 | 风荷载频遇值系数 |
| `YP_WDPY` | `934` | 934 | 温度荷载频遇值系数 |
| `YP_WDZYJ` | `935` | 935 | 温度荷载准永久值系数 |
| `YP_LOADCASE` | `939` | 939 | 工况组合类型  data[0]数组大小 data[1]当前类型 data[2-16]各类型对应组合方式 |
| `YP_COMBTYPE` | `940` | 940 | 荷载组合生成方式 |
| `YP_CUSTOMWXPID` | `941` | 941 | 自定义风载正x向ID数组 与  YP_CUSTOMWXPNAME个数相同，一一对位 |
| `YP_CUSTOMWXNID` | `942` | 942 | 自定义风载负x向ID数组 与  YP_CUSTOMWXNNAME个数相同，一一对位 |
| `YP_CUSTOMWYPID` | `943` | 943 | 自定义风载正y向ID数组 与  YP_CUSTOMWYPNAME个数相同，一一对位 |
| `YP_CUSTOMWYNID` | `944` | 944 | 自定义风载负y向ID数组 与  YP_CUSTOMWYNNAME个数相同，一一对位 |
| `YP_CUSTOMEXID` | `945` | 945 | 自定义地震荷载x向ID数组 与  YP_CUSTOMEXNAME个数相同，一一对位 |
| `YP_CUSTOMEYID` | `946` | 946 | 自定义地震荷载y向ID数组 与  YP_CUSTOMEYNAME个数相同，一一对位 |
| `YP_CUSTOMRFID` | `947` | 947 | 自定义人防荷载ID数组 与  YP_CUSTOMRFNAME个数相同，一一对位 |
| `YP_CUSTOMEZID` | `948` | 948 | 自定义地震荷载z向ID数组 与  YP_CUSTOMEYNAME个数相同，一一对位 |
| `YP_CUSTOMWXPNAME` | `951` | 951 | 自定义风载正x向工况名称  用yjkGetStringVectorSPara取值   也可用LPVARIANT yjkGetSPara(paraID) 取值，然后用Variant2StringArray转为CStringArray |
| `YP_CUSTOMWXNNAME` | `952` | 952 | 自定义风载负x向工况名称  用yjkGetStringVectorSPara取值   也可用LPVARIANT yjkGetSPara(paraID) 取值，然后用Variant2StringArray转为CStringArray |
| `YP_CUSTOMWYPNAME` | `953` | 953 | 自定义风载正y向工况名称  用yjkGetStringVectorSPara取值   也可用LPVARIANT yjkGetSPara(paraID) 取值，然后用Variant2StringArray转为CStringArray |
| `YP_CUSTOMWYNNAME` | `954` | 954 | 自定义风载负y向工况名称  用yjkGetStringVectorSPara取值   也可用LPVARIANT yjkGetSPara(paraID) 取值，然后用Variant2StringArray转为CStringArray |
| `YP_CUSTOMEXNAME` | `955` | 955 | 自定义地震荷载x向工况名称  用yjkGetStringVectorSPara取值   也可用LPVARIANT yjkGetSPara(paraID) 取值，然后用Variant2StringArray转为CStringArray |
| `YP_CUSTOMEYNAME` | `956` | 956 | 自定义地震荷载y向工况名称  用yjkGetStringVectorSPara取值   也可用LPVARIANT yjkGetSPara(paraID) 取值，然后用Variant2StringArray转为CStringArray |
| `YP_CUSTOMRFNAME` | `957` | 957 | 自定义人防荷载向工况名称  用yjkGetStringVectorSPara取值   也可用LPVARIANT yjkGetSPara(paraID) 取值，然后用Variant2StringArray转为CStringArray |
| `YP_CUSTOMEZNAME` | `958` | 958 | 自定义地震荷载z向工况名称  用yjkGetStringVectorSPara取值   也可用LPVARIANT yjkGetSPara(paraID) 取值，然后用Variant2StringArray转为CStringArray |
| `YP_CUSTOMWXP` | `961` | 961 | 自定义风载正x向组合系数  取值方式同YP_CUSTOMDL |
| `YP_CUSTOMWXN` | `962` | 962 | 自定义风载负x向组合系数  取值方式同YP_CUSTOMDL |
| `YP_CUSTOMWYP` | `963` | 963 | 自定义风载正y向组合系数  取值方式同YP_CUSTOMDL |
| `YP_CUSTOMWYN` | `964` | 964 | 自定义风载负y向组合系数  取值方式同YP_CUSTOMDL |
| `YP_CUSTOMEX` | `965` | 965 | 自定义地震荷载x向组合系数  取值方式同YP_CUSTOMDL |
| `YP_CUSTOMEY` | `966` | 966 | 自定义地震荷载y向组合系数  取值方式同YP_CUSTOMDL |
| `YP_CUSTOMRF` | `967` | 967 | 自定义人防荷载y向组合系数  取值方式同YP_CUSTOMDL |
| `YP_CUSTOMEZ` | `968` | 968 | 自定义地震荷载z向组合系数  取值方式同YP_CUSTOMDL |
| `YP_CUSTOMDLE` | `969` | 969 | 自定义恒载组合系数_地震  数据  取值方式同YP_CUSTOMDL |
| `YP_CUSTOMLLE` | `970` | 970 | 自定义活载组合系数_地震  取值方式同YP_CUSTOMDL |
| `YP_GLFX` | `971` | 971 | 重力荷载分项系数 |
| `YP_USEMDLCOMB` | `972` | 972 | 使用建模荷载组合 |
| `YP_GB50068` | `973` | 973 | 执行《建筑结构可靠性设计统一标准》 |
| `YP_GZBBYGB50068` | `974` | 974 | 刚重比按1.3恒+1.5活计算 |
| `YP_SAFELEVEL` | `975` | 975 | 安全等级  security levels |
| ↳ `YPV_SAFELEVEL_1` | `( YP_SAFELEVEL*YP_RES_SIZE+1 )` | 97501 | 1 |
| ↳ `YPV_SAFELEVEL_2` | `( YP_SAFELEVEL*YP_RES_SIZE+2 )` | 97502 | 2 |
| ↳ `YPV_SAFELEVEL_3` | `( YP_SAFELEVEL*YP_RES_SIZE+3 )` | 97503 | 3 |
| `YP_KLZDYGKJDBLZH` | `976` | 976 | 考虑自定义工况间的不利组合 |
| `YP_MRFGKYZDYFGKHB` | `977` | 977 | 默认风工况与自定义风工况合并 |
| `YP_DLTZ` | `978` | 978 | 考虑结构设计使用年限的恒荷载调整系数 |

### 11. 地下室信息

原文节注释行（逐字）：

```c
//////////////////////////////////////////////////////////////////////////
//	地下室信息
```

| 宏名 | 取值 | = 实际值 | 原文注释 |
|---|---|---|---|
| `YP_DIJIM` | `1001` | 1001 | 土层水平抗力系数的比例系数（M值） |
| `YP_DXWQBHC` | `1002` | 1002 | 外墙分布筋保护层厚度（mm） |
| `YP_NKHTT` | `1003` | 1003 | 扣除地面以下几层的回填土约束（计算） |
| `YP_HTTRZ` | `1004` | 1004 | 回填土容重 |
| `YP_QSWDP` | `1005` | 1005 | 室外地坪标高 |
| `YP_RHTT` | `1006` | 1006 | 回填土侧压力系数 |
| `YP_QWATER` | `1007` | 1007 | 地下水位标高（m） |
| `YP_DMADDLD` | `1008` | 1008 | 室外地面附加荷载（kN/m2） |
| `YP_JCWATERCOMB` | `1009` | 1009 | 基础水工况组合方式 |
| ↳ `YPV_JCWATERCOMB_ADD` | `( YP_JCWATERCOMB*YP_RES_SIZE+1 )` | 100901 | 基础水工况组合方式  叠加 |
| ↳ `YPV_JCWATERCOMB_EVELOP` | `( YP_JCWATERCOMB*YP_RES_SIZE+2 )` | 100902 | 基础水工况组合方式  包络 |
| ↳ `YPV_JCWATERCOMB_ADDEVELOP` | `( YP_JCWATERCOMB*YP_RES_SIZE+3 )` | 100903 | 基础水工况组合方式  叠加+包络 |
| `YP_FYWYJSDZ` | `1010` | 1010 | 按反应位移法计算地下结构的地震作用 (0/1) |
| `YP_JCXS` | `1011` | 1011 | 基床系数K（kN/m^3）(20000) (应大于0) |
| `YP_JCUMAXX` | `1012` | 1012 | 场地设计地震动峰值位移Umax（m） X向(0.1)   (应大于0) |
| `YP_JCUMAXY` | `1013` | 1013 | 场地设计地震动峰值位移Umax（m） Y向(0.1) |
| `YP_SEISG` | `1014` | 1014 | 地震动剪切模量G（MPa）(100)     (应大于0) |
| `YP_JZMSD` | `1015` | 1015 | 设计地震作用基准面的深度H（m）(0)     (应>=0) |
| `YP_SJCTYS` | `1016` | 1016 | 地下室侧土约束施加方式 |
| ↳ `YPV_SJCTYS_DBTH` | `( YP_SJCTYS*YP_RES_SIZE+1 )` | 101601 | 顶板双向弹簧 |
| ↳ `YPV_SJCTYS_WQTH` | `( YP_SJCTYS*YP_RES_SIZE+2 )` | 101602 | 外墙单压弹簧 |
| `YP_GBT51336` | `1017` | 1017 | 按《地下结构抗震设计标准》GBT51336-2018设计 |
| `YP_DXSJGTX` | `1018` | 1018 | 地下室结构形式 |
| ↳ `YPV_DXSJGTX_DANPZKJ` | `( YP_DXSJGTX*YP_RES_SIZE+1 )` | 101801 | 单排柱框架 |
| ↳ `YPV_DXSJGTX_QTKJ` | `( YP_DXSJGTX*YP_RES_SIZE+2 )` | 101802 | 其它框架 |
| ↳ `YPV_DXSJGTX_QTTX` | `( YP_DXSJGTX*YP_RES_SIZE+3 )` | 101803 | 同上部结构类型(其它) |

### 12. 砌体信息

原文节注释行（逐字）：

```c
//////////////////////////////////////////////////////////////////////////
//	砌体信息
```

| 宏名 | 取值 | = 实际值 | 原文注释 |
|---|---|---|---|
| `YP_ERATIO` | `1101` | 1101 | 砼与砌体弹性模量比3 |
| `YP_SGZL` | `1102` | 1102 | 施工质量ABC(B) |
| ↳ `YPV_SGZL_A` | `( YP_SGZL*YP_RES_SIZE+1 )` | 110201 | A |
| ↳ `YPV_SGZL_B` | `( YP_SGZL*YP_RES_SIZE+2 )` | 110202 | B |
| ↳ `YPV_SGZL_C` | `( YP_SGZL*YP_RES_SIZE+3 )` | 110203 | C |
| `YP_HOLERATIO` | `1103` | 1103 | 砌体孔洞率50(%) |
| `YP_BLBYCODE` | `1104` | 1104 | 是否按规范确定墙梁上部荷载，否则按经验(规范) |
| `YP_DKQLZJ` | `1105` | 1105 | 有洞口墙梁荷载折减系数(0.5-1)(1) |
| `YP_NDKQLZJ` | `1106` | 1106 | 无洞口墙梁荷载折减系数1 |
| `YP_SLOPEADD` | `1107` | 1107 | 坡屋面时结构附加高度0 |
| `YP_KZQBKZ` | `1108` | 1108 | 抗震墙侧移刚度考虑边框柱作用1 |
| `YP_RIGTYPE` | `1109` | 1109 | 楼面刚度类型（刚性、刚柔性、柔性） |
| ↳ `YPV_RIGTYPE_R` | `( YP_RIGTYPE*YP_RES_SIZE+1 )` | 110901 | 刚性 |
| ↳ `YPV_RIGTYPE_RF` | `( YP_RIGTYPE*YP_RES_SIZE+2 )` | 110902 | 刚柔性 |
| ↳ `YPV_RIGTYPE_F` | `( YP_RIGTYPE*YP_RES_SIZE+3 )` | 110903 | 柔性 |
| `YP_NDKC` | `1110` | 1110 | 底框层数 |
| `YP_BASEFIX` | `1111` | 1111 | 地下室结构嵌固高度 |
| `YP_QTGDMETHOD` | `1112` | 1112 | 墙体刚度计算方法(常规方法) |
| ↳ `YP_QTGDMETHOD_FINITE` | `( YP_QTGDMETHOD*YP_RES_SIZE+1 )` | 111201 | 有限元方法计算 |
| ↳ `YP_QTGDMETHOD_NOMAL` | `( YP_QTGDMETHOD*YP_RES_SIZE+2 )` | 111202 | 常规方法计算 |
| `YP_SEISZC` | `1113` | 1113 | 抗震计算采用《镇（乡）村建筑抗震技术规程》 |
| `YP_VALIDFLR` | `1114` | 1114 | 考虑基准面积率的有效楼层数 //2016.0115 取消该参数 改用 YP_KLJZMJL |
| `YP_BLBYEXP` | `1115` | 1115 | 是否按经验确定墙梁上部荷载(否) |
| `YP_QTCALCSEISM` | `1116` | 1116 | 是否计算地震作用(T) |
| `YP_QTCALCWIND` | `1117` | 1117 | 是否计算风荷载作用(T) |
| `YP_QTCALCBYTOWER` | `1118` | 1118 | 是否自动分塔计算(T) |
| `YP_QTMATARRY` | `1119` | 1119 | 砌体各层材料强度 |
| `YP_TOPFLRFACTOR` | `1120` | 1120 | 顶层平面小时考虑地震作用放大 |
| `YP_NKJC` | `1121` | 1121 | 内框架层数 |
| `YP_NKJDATA` | `1122` | 1122 | 内框架参数 |
| ↳ `YPV_QTWALLBEM` | `( 1100*YP_RES_SIZE+1 )` | (非标准公式) | 有托墙梁但非底框结构(砌体模块结构体系专用值) |

### 13. 工程信息

原文节注释行（逐字）：

```c
//////////////////////////////////////////////////////////////////////////
//	工程信息
```

| 宏名 | 取值 | = 实际值 | 原文注释 |
|---|---|---|---|
| `YP_COMPNAME` | `1301` | 1301 | 公司名称 |
| `YP_PROJNAME` | `1302` | 1302 | 工程名称 |
| `YP_PROJCODE` | `1303` | 1303 | 工程代号 |
| `YP_DESIGNER` | `1304` | 1304 | 设计人 |
| `YP_CHECKER` | `1305` | 1305 | 校核人 |

### 14. 时程分析信息

原文节注释行（逐字）：

```c
//////////////////////////////////////////////////////////////////////////
//	时程分析信息
```

| 宏名 | 取值 | = 实际值 | 原文注释 |
|---|---|---|---|
| `YP_SCTIMES` | `1401` | 1401 | 输出起始时间(0.f) |
| `YP_SCTIMEE` | `1402` | 1402 | 输出终止时间(25.f)	//2012.0210改默认值为25 |
| `YP_SCTIMESTEP` | `1403` | 1403 | 时间步长(0.1f) |
| `YP_SCDAMPRMETHOD` | `1410` | 1410 | 阻尼比计算方法 |
| ↳ `YP_SCDAMPRSAME` | `( YP_SCDAMPRMETHOD*YP_RES_SIZE+1 )` | 141001 | 所有振型同一阻尼 |
| ↳ `YP_SCDAMPRCOMB` | `( YP_SCDAMPRMETHOD*YP_RES_SIZE+2 )` | 141002 | Rayleigh阻尼组合模态阻尼 |
| `YP_SCCK` | `1412` | 1412 | 刚度因子Ck(0.f) |
| `YP_SCCM` | `1413` | 1413 | 质量因子Cm(0.f) |
| `YP_SCWAVEPARA` | `1414` | 1414 | 地震波参数数组(int)  其数值中高位存储是否计算主/次方向峰值加速度，低位存储地震波ID |
| `YP_SCMODEDI` | `1415` | 1415 | 各振型模态阻尼系数Di(float数组) |
| `YP_SCDZLC` | `1404` | 1404 | 地震烈度 6、7、8、9  默认可取地震信息中烈度，用户可修改为其它值 |
| `YP_SCDZYX` | `1405` | 1405 | 地震影响 |
| ↳ `YP_SCDZYX_DY` | `( YP_SCDZYX*YP_RES_SIZE+1 )` | 140501 | 多遇 |
| ↳ `YP_SCDZYX_HY` | `( YP_SCDZYX*YP_RES_SIZE+2 )` | 140502 | 罕遇 |
| ↳ `YP_SCDZYX_SF` | `( YP_SCDZYX*YP_RES_SIZE+3 )` | 140503 | 设防 内部使用，  不属于YP_SCDZYX参数的值，交互设置不显示 |
| ↳ `YP_SCDZYX_JHY` | `( YP_SCDZYX*YP_RES_SIZE+4 )` | 140504 | 极罕遇 |
| `YP_SCPRIMMAX` | `1406` | 1406 | 主方向峰值加速度(35.f)	//2012.0215改默认值，由35改为默认按烈度及多遇罕遇确定 |
| `YP_SCSECMAX` | `1407` | 1407 | 次方向峰值加速度(默认为YP_SCPRIMMAX*0.85) |
| `YP_SCTIMETOTAL` | `1408` | 1408 | 积分计算时长(35.f)	//2012.0210改默认值为35		//2012.1020改默认值为35 |
| `YP_SCTIMEDELTA` | `1409` | 1409 | 积分步长(0.02f)		//2012.1020改默认值为0.02 |
| `YP_SCDAMPRSAMEVAL` | `1411` | 1411 | 所有振型同一阻尼时的值(0.05f) |
| `YP_SCMODENUM` | `1416` | 1416 | 参与振型数 默认与地震信息中振型数一致，(0-YP_MODENUM) |
| `YP_SCSPECTIMES` | `1417` | 1417 | 反应谱起始周期(0.01s)	(0.0001, 50.) |
| `YP_SCSPECTIMEE` | `1418` | 1418 | 反应谱终止周期(6.s)	(0.0001, 50.) |
| `YP_SCSPECTIMESTEP` | `1419` | 1419 | 反应谱周期步长(0.02)	(0.001, 2)	//2012.0210改默认值为0.02 |
| `YP_SCAMAX` | `1420` | 1420 | 多遇地震影响系数最大值 |
| `YP_SCONLYPRIM` | `1421` | 1421 | 只计算主方向地震效应 |
| `YP_SCWAVEPARANAMES` | `1422` | 1422 | 地震波数组 默认 |
| `YP_SCREADQCLDZ` | `1423` | 1423 | 是否需要读取前处理地震参数 默认为1，读取过一次后改为0 |
| `YP_SCFZJSDTYPE` | `1424` | 1424 | 峰值加速度类型 PGA或EPA  默认PGA  //type of peak acceleration |
| ↳ `YPV_SCFZJSDTYPE_PGA` | `( YP_SCFZJSDTYPE*YP_RES_SIZE+1 )` | 142401 | PGA |
| ↳ `YPV_SCFZJSDTYPE_EPA` | `( YP_SCFZJSDTYPE*YP_RES_SIZE+2 )` | 142402 | EPA |
| `YP_SCTG` | `1425` | 1425 | 特征周期Tg（s） |
| `YP_SCLINESELWAVE` | `1426` | 1426 | 线性时程选波 |
| `YP_SCZNB` | `1427` | 1427 | 弹性时程阻尼比 |
| `YP_SCKLZQZZXS` | `1428` | 1428 | 弹性时程考虑周期折减系数 |
| `YP_SCWAVEPARANAMES_DY` | `1429` | 1429 | 地震波数组 多遇 |
| `YP_SCWAVEPARANAMES_HY` | `1430` | 1430 | 地震波数组 罕遇 |
| `YP_SCWAVEPARANAMES_SF` | `1431` | 1431 | 地震波数组 设防 内部使用， |
| `YP_SCWAVEPARANAMES_JHY` | `1432` | 1432 | 地震波数组 极罕遇 |

原文本节其余 `#define`（逐字）：

```c
#define YP_SCWAVEPARA_ID	0x0FFFFFFF	//用于取地震波参数中的ID (例 id = para & YP_SCWAVEPARA_ID 也可以用下面的宏定义如：id = YPSC_GETWAVEPARA_ID(para);)
#define YP_SCWAVEPARA_PRIM	0x20000000	//用于取地震波参数中的是否计算主方向 (例 bPrim = para & YP_SCWAVEPARA_PRIM 也可以用下面的宏定义如：bPrim = YPSC_GETWAVEPARA_PRIM(para);)
#define YP_SCWAVEPARA_SEC	0x10000000	//用于取地震波参数中的是否计算次方向 (例 bSec = para & YP_SCWAVEPARA_SEC也可以用下面的宏定义如：bSec = YPSC_GETWAVEPARA_SEC(para);)
```

### 15. 包络设计参数

原文节注释行（逐字）：

```c
//////////////////////////////////////////////////////////////////////////
//	包络设计参数
```

| 宏名 | 取值 | = 实际值 | 原文注释 |
|---|---|---|---|
| `YP_BLSJ` | `1501` | 1501 | 是否进行包络设计 (0~1) |
| `YP_BLSJPATH` | `1502` | 1502 | 包络设计路径 var.vt==VT_LPSTR;CSParaData::GetPara(YP_BLSJPATH)->pcVal; |
| `YP_BLSJFLOORS` | `1503` | 1503 | 包络设计层号 （int数组） |
| `YP_BLSJLOCXYZ` | `1504` | 1504 | 包络设计模型相对位置 （float数组） data[0]存数组大小(3)  data[1]存x坐标 data[2]存y坐标 data[3]存z坐标 |
| `YP_BLSJLOCALPHA` | `1505` | 1505 | 包络设计模型相对位置 水平转角α  360度 |
| `YP_BLSJPRJPATH` | `1506` | 1506 | 包络设计各模型的路径 字符串数组，数组个数应与YP_BLSJDATA中行数nPrj一致 |
| `YP_BLSJDATA` | `1507` | 1507 | 包络设计数据，数组 每一行存 x,y,z,α, 正截面、斜截面 |
| `YP_ISXNSJ` | `1607` | 1607 | 是否进行性能设计	//2013.1111 增加 控制是否进行性能设计的总参数 |
| `YP_XNSJGD` | `1601` | 1601 | 性能设计按何种规定考虑 |
| ↳ `YPV_XNSJGD_QG` | `( YP_XNSJGD*YP_RES_SIZE+1 )` | 160101 | 按全国抗规考虑性能设计 |
| ↳ `YPV_XNSJGD_GD` | `( YP_XNSJGD*YP_RES_SIZE+2 )` | 160102 | 按广东规程考虑性能设计 |
| ↳ `YPV_XNSJGD_QGGG` | `( YP_XNSJGD*YP_RES_SIZE+3 )` | 160103 | 按高规考虑性能设计 |
| ↳ `YPV_XNSJGD_SZ` | `( YP_XNSJGD*YP_RES_SIZE+4 )` | 160104 | 按深圳高规考虑性能设计 |
| ↳ `YPV_XNSJGD_SH` | `( YP_XNSJGD*YP_RES_SIZE+5 )` | 160105 | 按上海抗规考虑性能设计 |
| `YP_XNLEVEL` | `1602` | 1602 | 性能设计水准 |
| ↳ `YPV_XNLEVEL_1` | `( YP_XNLEVEL*YP_RES_SIZE+1 )` | 160201 | 性能设计水准1 |
| ↳ `YPV_XNLEVEL_2` | `( YP_XNLEVEL*YP_RES_SIZE+2 )` | 160202 | 性能设计水准2 |
| ↳ `YPV_XNLEVEL_3` | `( YP_XNLEVEL*YP_RES_SIZE+3 )` | 160203 | 性能设计水准3 |
| ↳ `YPV_XNLEVEL_4` | `( YP_XNLEVEL*YP_RES_SIZE+4 )` | 160204 | 性能设计水准4 |
| ↳ `YPV_XNLEVEL_5` | `( YP_XNLEVEL*YP_RES_SIZE+5 )` | 160205 | 性能设计水准5 |
| `YP_SEISLEVEL` | `1603` | 1603 | 地震水准 |
| ↳ `YPV_SEISLEVEL_MDL` | `( YP_SEISLEVEL*YP_RES_SIZE+1 )` | 160301 | 中震 |
| ↳ `YPV_SEISLEVEL_BIG` | `( YP_SEISLEVEL*YP_RES_SIZE+2 )` | 160302 | 大震 |
| `YP_GJGJXS` | `1604` | 1604 | 关键构件系数 |
| `YP_YBSXGJXS` | `1605` | 1605 | 一般竖向构件系数 |
| `YP_SPHNGJXS` | `1606` | 1606 | 水平耗能构件系数 |
| `YP_XNSJXJM` | `1608` | 1608 | 斜截面性能设计  取值与YP_XNSJ相同 |
| `YP_XNSJGB50017` | `1609` | 1609 | 性能设计按《钢结构设计标准》(GB50017-2017) |
| `YP_XNLEVELSTL` | `1610` | 1610 | 《钢结构规范》时 性能设计水准  7级(1-7，默认4) |
| ↳ `YPV_XNLEVELSTL_1` | `( YP_XNLEVELSTL*YP_RES_SIZE+1 )` | 161001 | 性能设计水准1 |
| ↳ `YPV_XNLEVELSTL_2` | `( YP_XNLEVELSTL*YP_RES_SIZE+2 )` | 161002 | 性能设计水准2 |
| ↳ `YPV_XNLEVELSTL_3` | `( YP_XNLEVELSTL*YP_RES_SIZE+3 )` | 161003 | 性能设计水准3 |
| ↳ `YPV_XNLEVELSTL_4` | `( YP_XNLEVELSTL*YP_RES_SIZE+4 )` | 161004 | 性能设计水准4 |
| ↳ `YPV_XNLEVELSTL_5` | `( YP_XNLEVELSTL*YP_RES_SIZE+5 )` | 161005 | 性能设计水准5 |
| ↳ `YPV_XNLEVELSTL_6` | `( YP_XNLEVELSTL*YP_RES_SIZE+6 )` | 161006 | 性能设计水准6 |
| ↳ `YPV_XNLEVELSTL_7` | `( YP_XNLEVELSTL*YP_RES_SIZE+7 )` | 161007 | 性能设计水准7 |
| `YP_XNYXLEVEL` | `1611` | 1611 | 《钢结构规范》时 延性等级  五级:Ⅰ-Ⅴ，默认4 |
| ↳ `YPV_XNYXLEVEL_1` | `( YP_XNYXLEVEL*YP_RES_SIZE+1 )` | 161101 | 延性等级I |
| ↳ `YPV_XNYXLEVEL_2` | `( YP_XNYXLEVEL*YP_RES_SIZE+2 )` | 161102 | 延性等级II |
| ↳ `YPV_XNYXLEVEL_3` | `( YP_XNYXLEVEL*YP_RES_SIZE+3 )` | 161103 | 延性等级III |
| ↳ `YPV_XNYXLEVEL_4` | `( YP_XNYXLEVEL*YP_RES_SIZE+4 )` | 161104 | 延性等级IV |
| ↳ `YPV_XNYXLEVEL_5` | `( YP_XNYXLEVEL*YP_RES_SIZE+5 )` | 161105 | 延性等级V |
| `YP_HNGJEIZJXS` | `1612` | 1612 | 耗能构件抗弯刚度EI折减系数(编辑框，默认值1.0) (0~1) |
| `YP_HNGJEAZJXS` | `1613` | 1613 | 耗能构件轴向刚度EA折减系数(编辑框，默认值1.0)(0~1) |
| `YP_HNGJXNXS` | `1614` | 1614 | 耗能构件性能系数(编辑框，默认值0.55)(>0) |
| `YP_FHNGJTZXS` | `1615` | 1615 | 非耗能构件内力调整系数βe(编辑框，默认值1.32)(0~1) |
| `YP_GJCQXS` | `1616` | 1616 | 考虑钢筋超强系数1.25  默认不勾选 |
| `YP_XNSJGDGGJ` | `1617` | 1617 | 是否按广东高规控制钢构件局部稳定  默认勾选 |
| `YP_SPHNGJXSLL` | `1618` | 1618 | 水平耗能构件系数（连梁）//2021.0819添加代码 |
| `YP_CHECK_XNSJQWGCF` | `1619` | 1619 | 是否勾选轻屋盖厂房按"低延性、高弹性承载力"性能化设计 |
| `YP_XNSJQWGCF` | `1620` | 1620 | 1.5/2倍地震作用 |
| ↳ `YPV_XNSJQWGCF_15` | `( YP_XNSJQWGCF*YP_RES_SIZE+1 )` | 162001 | 1.5倍 |
| ↳ `YPV_XNSJQWGCF_2` | `( YP_XNSJQWGCF*YP_RES_SIZE+2 )` | 162002 | 2倍 |
| `YP_XNSJSHOWTYPE` | `1621` | 1621 | 性能设计显示方式 0文字显示 1数字显示 |

### 16. 弹塑性时程分析信息

原文节注释行（逐字）：

```c
//////////////////////////////////////////////////////////////////////////
//	弹塑性时程分析信息
```

| 宏名 | 取值 | = 实际值 | 原文注释 |
|---|---|---|---|
| `YP_EPSCDZLC` | `1704` | 1704 | 地震烈度 6、7、8、9  默认可取地震信息中烈度，用户可修改为其它值 |
| `YP_EPSCDZYX` | `1705` | 1705 | 地震影响 |
| `YP_EPSCPRIMMAX` | `1706` | 1706 | 主方向峰值加速度(35.f)	//2012.0217改默认值，由35改为默认按烈度及多遇罕遇确定 |
| `YP_EPSCSECMAX` | `1707` | 1707 | 次方向峰值加速度(默认为YP_SCPRIMMAX*0.85) |
| `YP_EPSCTIMETOTAL` | `1708` | 1708 | 积分计算时长(35.f)	//2012.0210改默认值为35		//2012.1020改默认值为35 |
| `YP_EPSCTIMEDELTA` | `1709` | 1709 | 积分步长(0.02f)		//2012.1020改默认值为0.02 |
| `YP_EPSCDAMPRSAMEVAL` | `1711` | 1711 | 所有振型同一阻尼时的值(0.05f) |
| `YP_EPSCMODENUM` | `1716` | 1716 | 参与振型数 默认与地震信息中振型数一致，(0-YP_MODENUM) |
| `YP_EPSCSPECTIMES` | `1717` | 1717 | 反应谱起始周期(0.01s)	(0.0001, 50.) |
| `YP_EPSCSPECTIMEE` | `1718` | 1718 | 反应谱终止周期(6.s)	(0.0001, 50.) |
| `YP_EPSCSPECTIMESTEP` | `1719` | 1719 | 反应谱周期步长(0.02)	(0.001, 2)	//2012.0210改默认值为0.02 |
| `YP_EPSCAMAX` | `1720` | 1720 | 多遇地震影响系数最大值 |
| `YP_EPSCONLYPRIM` | `1721` | 1721 | 只计算主方向地震效应 |
| `YP_EPSCWAVEPARANAMES` | `1722` | 1722 | 地震波数组 |
| `YP_EPSCREADQCLDZ` | `1723` | 1723 | 是否需要读取前处理地震参数 默认为1，读取过一次后改为0 |
| `YP_EPSCFZJSDTYPE` | `1724` | 1724 | 峰值加速度类型 PGA或EPA  默认PGA 值为YPV_SCFZJSDTYPE_PGA 或YPV_SCFZJSDTYPE_EPA |
| `YP_EPSCTG` | `1725` | 1725 | 特征周期Tg（s） |
| `YP_EPSCLINESELWAVE` | `1726` | 1726 | 线性时程选波 |
| `YP_EPSCZNB` | `1727` | 1727 | 弹塑性阻尼比 |
| `YP_EPSCKLZQZZXS` | `1728` | 1728 | 弹塑性考虑周期折减系数 |

### 17. 鉴定加固

原文节注释行（逐字）：

```c
//////////////////////////////////////////////////////////////////////////
//	鉴定加固
```

| 宏名 | 取值 | = 实际值 | 原文注释 |
|---|---|---|---|
| `YP_JDJG` | `1801` | 1801 | 鉴定加固 |
| `YP_JDJGCODE` | `1802` | 1802 | 鉴定加固标准 |
| `YP_GAMAREZJXS` | `1803` | 1803 | 承载力抗震调整系数的折减系数 (float) |
| `YP_JGGJZJXS` | `1804` | 1804 | 震损建筑加固构件承载力折减系数 (float) |
| `YP_REALBARRATIO` | `1805` | 1805 | 实配与计算配筋比值 (float) |
| `YP_JGQPATH` | `1806` | 1806 | 加固前工程所在路径 (CString) |
| `YP_USEJGHXS` | `1807` | 1807 | 计算时采用加固后影响系数 (bool) |
| `YP_JDJGXSARRAY` | `1808` | 1808 | 影响系数 各层各塔单设(数组) |
| `YP_AUTOCALC4BAR` | `1809` | 1809 | 自动计算并生成加固前配筋 |
| `YP_JDJGSTD` | `1810` | 1810 | 砌体结构鉴定加固标准		//2016.0115 取消该参数 改用 YP_JDJGCODE |
| ↳ `YPV_JDJGSTD_A` | `( YP_JDJGSTD*YP_RES_SIZE+1 )` | 181001 | A类鉴定方法 |
| ↳ `YPV_JDJGSTD_B` | `( YP_JDJGSTD*YP_RES_SIZE+2 )` | 181002 | B类鉴定方法 |
| ↳ `YPV_JDJGSTD_C` | `( YP_JDJGSTD*YP_RES_SIZE+3 )` | 181003 | C类鉴定方法 |
| `YP_QTJGMETHOD` | `1811` | 1811 | 砌体结构加固计算方法 |
| ↳ `YPV_QTJGMETHOD_ZDXS` | `( YP_QTJGMETHOD*YP_RES_SIZE+1 )` | 181101 | 增强系数法 |
| ↳ `YPV_QTJGMETHOD_WXGS` | `( YP_QTJGMETHOD*YP_RES_SIZE+2 )` | 181102 | 文献公式法 |
| `YP_KLJZMJL` | `1812` | 1812 | 是否考虑基准面积率有效层数 (0/1) |
| `YP_KLJZMJLNUM` | `1813` | 1813 | 考虑基准面积率有效层数 |
| `YP_JDBZGE` | `1814` | 1814 | 《建筑抗震鉴定标准》附录B中的重力荷载代表值按实际值调整 勾选,则按实际gE计算 (0/1) |
| `YP_JD5216` | `1815` | 1815 | 按《建筑抗震鉴定标准》5.2.16条的二级鉴定计算   勾选后,按此条计算二级鉴定时，应调整地震烈度影响系数λ |
| `YP_VUSENEWWALL` | `1816` | 1816 | 《建筑抗震加固技术规程JGJ116》 楼层剪力全部由新增剪力墙抵抗 |
| `YP_JGJ116_5383` | `1817` | 1817 | 《建筑抗震加固技术规程JGJ116》 按5.3.8 3调整板墙计算方法 |
| `YP_QTJGModel` | `1818` | 1818 | 当前是否为砌体加固模型 |
| `YP_QTCZLBY50702` | `1819` | 1819 | 砌体加固承载力按《砌体结构加固设计规范》GB50702计算 |
| `YP_JDJG_PDXS` | `1820` | 1820 | 砼构件评定形式 |
| `YP_JDJG_FKZZH` | `1821` | 1821 | 非抗震组合 |
| `YP_JDJG_PDBZ` | `1822` | 1822 | 评定标准float数组 首位是有几个参数（肯定就2个） 所以就取1,2号位就行 |
| `YP_JDJG_KZHC` | `1823` | 1823 | 抗震核查的Excel表 yjkGetStringVectorSPara()读取 传入CStringArray 的对象 然后下标读取 【0】是数组大小，【1】是行数【2】列数（不含表头）后面就是每行的数据 |
| `YP_JDJG_FileName` | `1824` | 1824 | 表格名字 |
| `YP_JDJG_HCJL` | `1825` | 1825 | 核查结论 |
| `YP_JDJG_KZSF` | `1826` | 1826 | 抗震设防类别 |
| ↳ `YPV_JDJG_KZSF_A` | `( YP_JDJG_KZSF*YP_RES_SIZE+1 )` | 182601 | 甲类 |
| ↳ `YPV_JDJG_KZSF_B` | `( YP_JDJG_KZSF*YP_RES_SIZE+2 )` | 182602 | 乙类 |
| ↳ `YPV_JDJG_KZSF_C` | `( YP_JDJG_KZSF*YP_RES_SIZE+3 )` | 182603 | 丙类 |
| ↳ `YPV_JDJG_KZSF_D` | `( YP_JDJG_KZSF*YP_RES_SIZE+4 )` | 182604 | 丁类 |
| `YP_JDJG_ConsiderForce` | `1827` | 1827 | 考虑二次受力影响 |
| `YP_JDJG_Standard` | `1828` | 1828 | 抗震鉴定规范系列 |
| ↳ `YPV_JDJG_Standard_CN` | `( YP_JDJG_Standard*YP_RES_SIZE+1 )` | 182801 | 国标 |
| ↳ `YPV_JDJG_Standard_BJ` | `( YP_JDJG_Standard*YP_RES_SIZE+2 )` | 182802 | 北京 |

### 18. 北京地标

原文节注释行（逐字）：

```c
//////////////////////////////////////////////////////////////////////////
// 北京地标
```

| 宏名 | 取值 | = 实际值 | 原文注释 |
|---|---|---|---|
| `YP_StandardBJ_CtrlGrade` | `1829` | 1829 | 抗震宏观控制等级 |
| ↳ `YPV_StandardBJ_CtrlGrade_Ae2` | `( YP_StandardBJ_CtrlGrade*YP_RES_SIZE+1 )` | 182901 | Ae2 |
| ↳ `YPV_StandardBJ_CtrlGrade_Be2` | `( YP_StandardBJ_CtrlGrade*YP_RES_SIZE+2 )` | 182902 | Be2 |
| ↳ `YPV_StandardBJ_CtrlGrade_Ce2` | `( YP_StandardBJ_CtrlGrade*YP_RES_SIZE+3 )` | 182903 | Ce2 |
| ↳ `YPV_StandardBJ_CtrlGrade_De2` | `( YP_StandardBJ_CtrlGrade*YP_RES_SIZE+4 )` | 182904 | De2 |
| `YP_StandardBJ_RatingMethod` | `1830` | 1830 | 抗震承载力评级方法 |
| ↳ `YP_StandardBJ_RatingMethod_ComprehensiveSeis` | `( YP_StandardBJ_RatingMethod*YP_RES_SIZE+1 )` | 183001 | 综合抗震能力 |
| ↳ `YP_StandardBJ_RatingMethod_LateralResistance` | `( YP_StandardBJ_RatingMethod*YP_RES_SIZE+2 )` | 183002 | 抗侧力构件 |
| `YP_StandardBJ_Concrete` | `1831` | 1831 | 民用混凝土构件评级标准 float数组 // 数组第一位是元素个数（8个所以第一位一定是8） |
| `YP_StandardBJ_Steel` | `1832` | 1832 | 民用钢构件评级标准 float数组     // 接着是元素，元素按列的顺序存储，也就是先是ae标准下的 |
| `YP_StandardBJ_Masonry` | `1833` | 1833 | 民用砌体构件评级标准 float数组   // 重要构件、次要构件，再是be标准下的重要构件、次要构件 |
| `YP_JDJG_SPGJJD` | `1834` | 1834 | 不进行实配钢筋鉴定 |
| `YP_JDJG_COMBLOADCOEF1` | `1835` | 1835 | 二次受力计算组合恒载 |
| `YP_JDJG_COMBLOADCOEF2` | `1836` | 1836 | 二次受力计算组合活载 |
| `YP_JDJG_SCWJBZZ` | `1837` | 1837 | 输出所有混凝土梁加固前弯矩标准值M0K |
| `YP_GJGJG` | `1840` | 1840 | 执行钢结构加固规范GB-51367-2019 |
| `YP_GJGJG_MYYLJSPATH` | `1841` | 1841 | 名义应力计算模型路径  字符串 |
| `YP_GJGJG_COMBLOADCOEF1` | `1842` | 1842 | 名义应力计算组合恒载 |
| `YP_GJGJG_COMBLOADCOEF2` | `1843` | 1843 | 名义应力计算组合活载 |
| `YP_GJGJG_MYYLJSDATA` | `1844` | 1844 | 名义应力计算模型参数  其中[0]存数组大小，目前为5 后面依次为相对坐标x,y,z及转角 |
| `YP_GJGJG_SCMYYL` | `1845` | 1845 | 输出所有可加固构件的名义应力 |
| `YP_GJGJG_YYTGBHDLYXS` | `1846` | 1846 | 翼缘贴钢板厚度利用系数 |

### 19. 装配式

原文节注释行（逐字）：

```c
//////////////////////////////////////////////////////////////////////////
//	装配式
```

| 宏名 | 取值 | = 实际值 | 原文注释 |
|---|---|---|---|
| `YP_ZPS` | `1901` | 1901 | 是否装配式结构 |
| `YP_XJQDZFD` | `1902` | 1902 | 现浇墙地震内力放大系数，默认1.1 |
| `YP_YZQGTJBL` | `1903` | 1903 | 预制墙竖向钢筋贯通筋比例[0,1] 默认0.5 |
| `YP_BJYZQJF` | `1904` | 1904 | 按北京市装配式规程验算预制墙接缝 |
| `YP_YZSXGJDZFD` | `1905` | 1905 | 预制竖向构件地震内力放大系数，默认1.0 |
| `YP_XJZDZFD` | `1906` | 1906 | 现浇柱地震内力放大系数，默认1.1 |
| `YP_SGBL_EM` | `1907` | 1907 | 采用竖向无连接墙体系  用于中建八局竖向无连接预制墙, 规程T/CECS 795-2021 |
| ↳ `YPV_SGBL_EM_NONE` | `( YP_SGBL_EM*YP_RES_SIZE+1 )` | 190701 | 关闭 |
| ↳ `YPV_SGBL_EM_FIST` | `( YP_SGBL_EM*YP_RES_SIZE+2 )` | 190702 | 从首层开始使用 |
| ↳ `YPV_SGBL_EM_JQQ` | `( YP_SGBL_EM*YP_RES_SIZE+3 )` | 190703 | 底部加强区以上为竖向不连续墙 |
| `YP_BJYZQJF_DB11` | `1908` | 1908 | 装配式剪力墙结构设计规程 |
| ↳ `YPV_BJYZQJF_DB11_1003_2013` | `( YP_BJYZQJF_DB11*YP_RES_SIZE+1 )` | 190801 | DB11 1003-2013 装配式剪力墙结构设计规程 |
| ↳ `YPV_BJYZQJF_DB11_1003_2022` | `( YP_BJYZQJF_DB11*YP_RES_SIZE+2 )` | 190802 | DB11 1003-2022 装配式剪力墙结构设计规程 |

### 20. 防火设计参数

原文节注释行（逐字）：

```c
//////////////////////////////////////////////////////////////////////////
// 防火设计参数
```

| 宏名 | 取值 | = 实际值 | 原文注释 |
|---|---|---|---|
| `YP_FHYSCZL` | `2001` | 2001 | 进行承载力法防火验算 |
| `YP_FHZYXXS` | `2002` | 2002 | 防火规范结构重要性系数 |
| `YP_MAXTEMPSTL` | `2003` | 2003 | 钢材最高温度 (默认300 >0) |
| `YP_USENHG` | `2004` | 2004 | 使用耐火钢 |
| `YP_WDNLZJXX` | `2005` | 2005 | 温度承载力验算时，温度内力折减系数 默认 |
| `YP_FHBHCL` | `2006` | 2006 | 钢梁抗火设计保护层类型 |
| ↳ `YPV_FHBHC_WBY` | `( YP_FHBHCL*YP_RES_SIZE+1 )` | 200601 | 外边缘型 |
| ↳ `YPV_FHBHC_OTHER` | `( YP_FHBHCL*YP_RES_SIZE+2 )` | 200602 | 非外边缘型 |
| `YP_FHBHCZ` | `2007` | 2007 | 钢柱抗火设计保护层类型 |
| `YP_FHBHCC` | `2008` | 2008 | 钢支撑抗火设计保护层类型 |
| `YP_ZYGJKLWDZH` | `2009` | 2009 | 轴向受力构件考虑温度组合 默认为1  2020.0506修改含义 之前为“仅轴向受力构件考虑温度组合” 不勾选时为全部考虑温度组合 |
| `YP_BURNTYPE` | `2010` | 2010 | 燃烧物类型 |
| ↳ `YPV_BURNTYPE_XW` | `( YP_BURNTYPE*YP_RES_SIZE+1 )` | 201001 | 纤维类 |
| ↳ `YPV_BURNTYPE_TING` | `( YP_BURNTYPE*YP_RES_SIZE+2 )` | 201002 | 烃类 |
| `YP_FZYGJKLWDZH` | `2011` | 2011 | 非轴向受力构件考虑温度组合 默认0 |
| `YP_ICUSTCURVE_FIRE` | `2012` | 2012 | 使用自定义升温曲线 |
| `YP_CUSTCURVE_FIRE` | `2013` | 2013 | 自定义升温曲线 float数组 // 数组第一位是元素个数，接着是元素，按横行的顺序进行存储 |
| `YP_WDQX_DMMJ` | `2014` | 2014 | 地面面积 ==0按选项，==1按输入面积差值 |
| `YP_WDQX_AXX` | `2015` | 2015 | 按选项 |
| `YP_WDQX_ASRMJ` | `2016` | 2016 | 按输入面积差值 |
| `YP_WDQX_JSGD` | `2017` | 2017 | 计算高度 |
| `YP_WDQX_KJGD` | `2018` | 2018 | 空间高度 |
| `YP_WDQX_HZZZLX` | `2019` | 2019 | 火灾增长类型 |
| `YP_WDQX_HYGL` | `2020` | 2020 | 火源功率 |
| `YP_WDQX_QXSJZ` | `2021` | 2021 | 曲线时间轴 |
| `YP_WDQX_ZJ_X_B` | `2022` | 2022 | 直接按x<b |
| `YP_WDQX_HYJL` | `2023` | 2023 | 火源距离 |
| `YP_WDQX_HYBJ` | `2024` | 2024 | 火源半径 |

### 21. 预应力参数

原文节注释行（逐字）：

```c
//////////////////////////////////////////////////////////////////////////
// 预应力参数
```

| 宏名 | 取值 | = 实际值 | 原文注释 |
|---|---|---|---|
| `YP_YYLCALCTYPE` | `2101` | 2101 | 应力损失计算方式  int   0  0-1 |
| `YP_YYLYLSSBL1` | `2102` | 2102 | 第一批预应力损失比例 float  10  0-100 |
| `YP_YYLYLSSBL2` | `2103` | 2103 | 第二批预应力损失比例 float  15  0-100 |
| `YP_YYLKZQDB` | `2104` | 2104 | 控制预应力强度比     float   0.75  0-1 |
| `YP_YYLKLDJ` | `2105` | 2105 | 预应力参数 抗裂等级 |
| ↳ `YPV_YYLKLDJ_1` | `( YP_YYLKLDJ*YP_RES_SIZE+1 )` | 210501 | 抗裂等级一级 |
| ↳ `YPV_YYLKLDJ_2` | `( YP_YYLKLDJ*YP_RES_SIZE+2 )` | 210502 | 抗裂等级二级 |
| ↳ `YPV_YYLKLDJ_3` | `( YP_YYLKLDJ*YP_RES_SIZE+3 )` | 210503 | 抗裂等级三级 |

### 22. zyl 增加ssds的参数

原文节注释行（逐字）：

```c
//////////////////////////////////////////////////////////////////////////
// zyl 增加ssds的参数
```

| 宏名 | 取值 | = 实际值 | 原文注释 |
|---|---|---|---|
| `YP_SSDS_WD` | `2106` | 2106 | float数组 |

### 23. 性能包络设计

原文节注释行（逐字）：

```c
//////////////////////////////////////////////////////////////////////////
//	性能包络设计
```

| 宏名 | 取值 | = 实际值 | 原文注释 |
|---|---|---|---|
| `YP_XNSJBL` | `2221` | 2221 | 按照高规方法进行性能包络设计 |
| `YP_BLZ_BQF` | `2222` | 2222 | 中震计算模型是否不屈服 |
| `YP_BLZ_TX` | `2223` | 2223 | 中震计算模型是否弹性 |
| `YP_BLZ_MAXALPHA` | `2224` | 2224 | 中震地震影响系数最大值 |
| `YP_BLZ_ZQZJ` | `2225` | 2225 | 中震周期折减系数 |
| `YP_BLZBQF_DAMPTYPE` | `2231` | 2231 | 中震不屈服 阻尼比设置类型 值为 YPV_DAMP_TOTAL/YPV_DAMP_BYMAT |
| `YP_BLZBQF_DAMP` | `2232` | 2232 | 中震不屈服 全楼统一 阻尼比数值 |
| `YP_BLZBQF_DAMPMATIDS` | `2234` | 2234 | 中震不屈服 分材料阻尼比时各材料ID(int数组，第一个为数组大小) 暂按yjkidkind.h中标准材料号记录 如钢--IDM_Steel  砼--IDM_Concrete |
| `YP_BLZBQF_DAMPMATDAMPS` | `2235` | 2235 | 中震不屈服 分材料阻尼比时各材料阻尼比值(%)(float数组，第一个为数组大小) |
| `YP_BLZBQF_LLZJ` | `2236` | 2236 | 中震不屈服 连梁刚度折减系数 |
| `YP_BLZBQF_ZLFD` | `2237` | 2237 | 中震不屈服 中梁刚度放大系数 |
| `YP_BLZBQF_SXDZ` | `2238` | 2238 | 中震不屈服 考虑双向地震作用 |
| `YP_BLZTX_DAMPTYPE` | `2241` | 2241 | 中震弹性 阻尼比设置类型 值为 YPV_DAMP_TOTAL/YPV_DAMP_BYMAT |
| `YP_BLZTX_DAMP` | `2242` | 2242 | 中震弹性 全楼统一 阻尼比数值 |
| `YP_BLZTX_DAMPMATIDS` | `2244` | 2244 | 中震弹性 分材料阻尼比时各材料ID(int数组，第一个为数组大小) 暂按yjkidkind.h中标准材料号记录 如钢--IDM_Steel  砼--IDM_Concrete |
| `YP_BLZTX_DAMPMATDAMPS` | `2245` | 2245 | 中震弹性 分材料阻尼比时各材料阻尼比值(%)(float数组，第一个为数组大小) |
| `YP_BLZTX_LLZJ` | `2246` | 2246 | 中震弹性 连梁刚度折减系数 |
| `YP_BLZTX_ZLFD` | `2247` | 2247 | 中震弹性 中梁刚度放大系数 |
| `YP_BLZTX_SXDZ` | `2248` | 2248 | 中震弹性 考虑双向地震作用 |
| `YP_BLD_BQF` | `2252` | 2252 | 大震计算模型是否不屈服 |
| `YP_BLD_TX` | `2253` | 2253 | 大震计算模型是否弹性 |
| `YP_BLD_MAXALPHA` | `2254` | 2254 | 大震地震影响系数最大值 |
| `YP_BLD_TG` | `2255` | 2255 | 大震特征周期 |
| `YP_BLD_ZQZJ` | `2256` | 2256 | 大震周期折减系数 |
| `YP_BLDBQF_DAMPTYPE` | `2261` | 2261 | 大震不屈服 阻尼比设置类型 值为 YPV_DAMP_TOTAL/YPV_DAMP_BYMAT |
| `YP_BLDBQF_DAMP` | `2262` | 2262 | 大震不屈服 全楼统一 阻尼比数值 |
| `YP_BLDBQF_DAMPMATIDS` | `2264` | 2264 | 大震不屈服 分材料阻尼比时各材料ID(int数组，第一个为数组大小) 暂按yjkidkind.h中标准材料号记录 如钢--IDM_Steel  砼--IDM_Concrete |
| `YP_BLDBQF_DAMPMATDAMPS` | `2265` | 2265 | 大震不屈服 分材料阻尼比时各材料阻尼比值(%)(float数组，第一个为数组大小) |
| `YP_BLDBQF_LLZJ` | `2266` | 2266 | 大震不屈服 连梁刚度折减系数 |
| `YP_BLDBQF_ZLFD` | `2267` | 2267 | 大震不屈服 中梁刚度放大系数 |
| `YP_BLDBQF_SXDZ` | `2268` | 2268 | 大震不屈服 考虑双向地震作用 |
| `YP_BLDTX_DAMPTYPE` | `2271` | 2271 | 大震弹性 阻尼比设置类型 值为 YPV_DAMP_TOTAL/YPV_DAMP_BYMAT |
| `YP_BLDTX_DAMP` | `2272` | 2272 | 大震弹性 全楼统一 阻尼比数值 |
| `YP_BLDTX_DAMPMATIDS` | `2274` | 2274 | 大震弹性 分材料阻尼比时各材料ID(int数组，第一个为数组大小) 暂按yjkidkind.h中标准材料号记录 如钢--IDM_Steel  砼--IDM_Concrete |
| `YP_BLDTX_DAMPMATDAMPS` | `2275` | 2275 | 大震弹性 分材料阻尼比时各材料阻尼比值(%)(float数组，第一个为数组大小) |
| `YP_BLDTX_LLZJ` | `2276` | 2276 | 大震弹性 连梁刚度折减系数 |
| `YP_BLDTX_ZLFD` | `2277` | 2277 | 大震弹性 中梁刚度放大系数 |
| `YP_BLDTX_SXDZ` | `2278` | 2278 | 大震弹性 考虑双向地震作用 |
| `YP_BLD_ZJM` | `2279` | 2279 | 大震构件设计正截面 不考虑、不屈服、弹性对应的宏采用705	性能设计（全国）下的宏定义 |
| `YP_BLD_XJM` | `2280` | 2280 | 大震构件设计斜截面 不考虑、不屈服、弹性对应的宏采用705	性能设计（全国）下的宏定义 |
| `YP_BLZ_ZJM` | `2281` | 2281 | 中震构件设计正截面 不考虑、不屈服、弹性对应的宏采用705	性能设计（全国）下的宏定义 |
| `YP_BLZ_XJM` | `2282` | 2282 | 中震构件设计斜截面 不考虑、不屈服、弹性对应的宏采用705	性能设计（全国）下的宏定义 |
| `YP_BLZ_FYWY_X` | `2283` | 2283 | 中震 反应位移法 峰值位移 X向 |
| `YP_BLZ_FYWY_Y` | `2284` | 2284 | 中震 反应位移法 峰值位移 Y向 |
| `YP_BLD_FYWY_X` | `2285` | 2285 | 大震 反应位移法 峰值位移 X向 |
| `YP_BLD_FYWY_Y` | `2286` | 2286 | 大震 反应位移法 峰值位移 Y向 |

### 24. 分析求解参数

原文节注释行（逐字）：

```c
//////////////////////////////////////////////////////////////////////////
//分析求解参数
```

| 宏名 | 取值 | = 实际值 | 原文注释 |
|---|---|---|---|
| `YP_MULTITHREADED` | `2301` | 2301 | 启用并行求解器  默认1 [0-1] |
| `YP_CPUNUM` | `2302` | 2302 | 使用cpu核心数量（0为自动） 默认-2(0,) |
| `YP_CUSTOMSET` | `2303` | 2303 | 自定义控制参数 字符串 |
| `YP_SOLVERTYPE` | `2304` | 2304 | 求解器类型 |
| `YP_HJDY` | `2309` | 2309 | 考虑几何非线性 |
| `YP_CSZTQD` | `2320` | 2320 | 初始状态确定 |
| `YP_ZXFF_RYTXDDPH` | `2321` | 2321 | 任意体系迭代平衡 |
| `YP_ZXFF_KLZZ` | `2322` | 2322 | 考虑自重 |
| `YP_ZJLX` | `2323` | 2323 | 支架类型 |
| `YP_SYKRQJQ` | `2324` | 2324 | 使用扩容求解器 |

### 25. 时域显示随机模拟法

原文节注释行（逐字）：

```c
//////////////////////////////////////////////////////////////////////////////
//时域显示随机模拟法
```

| 宏名 | 取值 | = 实际值 | 原文注释 |
|---|---|---|---|
| `YP_RANDHIS` | `2451` | 2451 | 是否采用时域显式随机模拟法 BOOL |
| `YP_RANDHIS_WAVEAMOUNT` | `2452` | 2452 | 生成地震波数量 int |
| `YP_RANDHIS_TA` | `2453` | 2453 | 均匀调制函数参数  Ta |
| `YP_RANDHIS_TB` | `2454` | 2454 | 均匀调制函数参数  Tb |
| `YP_RANDHIS_C` | `2455` | 2455 | 均匀调制函数参数  C |
| `YP_RANDHIS_UPPERIOD` | `2456` | 2456 | 终止周期 该参数已经删除不用了 |
| `YP_RANDHIS_DURATION` | `2457` | 2457 | 地震波持续时间 float |
| `YP_RANDHIS_STEP` | `2458` | 2458 | 时间步长 float |
| `YP_RANDHIS_FREQUENCY` | `2459` | 2459 | 频率划分段数 int |
| `YP_RANDHIS_MAX_FREQUENCY` | `2460` | 2460 | 截断最大频率 float |
| `YP_RANDHIS_MIN_FREQUENCY` | `2461` | 2461 | 截断最小频率 float |
| `YP_RANDHIS_TOLERANCE` | `2462` | 2462 | 平均反应谱与规范反应谱的相对容差  float |

### 26. 隔震减震

原文节注释行（逐字）：

```c
//////////////////////////////////////////////////////////////////////////
// 隔震减震
```

| 宏名 | 取值 | = 实际值 | 原文注释 |
|---|---|---|---|
| `YP_ISOLATSEIS` | `2501` | 2501 | 是否采用 隔震 Isolation and damping design |
| `YP_FYPTYPE` | `2502` | 2502 | 反应谱计算方法  Response spectrum calculation method |
| ↳ `YPV_FYPTYPE_REALMOD` | `( YP_FYPTYPE*YP_RES_SIZE+1 )` | 250201 | 实振型分解反应谱法  Real mode decomposition response spectrum method |
| ↳ `YPV_FYPTYPE_COMPLEXMOD` | `( YP_FYPTYPE*YP_RES_SIZE+2 )` | 250202 | 复振型分解反应谱法  Complex mode decomposition response spectrum method |
| `YP_ISOLATLINKTYPE` | `2505` | 2505 | 减隔震元件有效刚度和有效阻尼 Effective stiffness and effective damping of vibration reduction and isolation elements |
| ↳ `YPV_ISOLATLINKTYPE_INPUTEQU` | `( YP_ISOLATLINKTYPE*YP_RES_SIZE+1 )` | 250501 | 采用输入的等效线性属性  Equivalent linear attribute of input |
| ↳ `YPV_ISOLATLINKTYPE_ITERATIVE` | `( YP_ISOLATLINKTYPE*YP_RES_SIZE+2 )` | 250502 | 迭代确定  Iterative determination |
| ↳ `YPV_ISOLATLINKTYPE_USETH` | `( YP_ISOLATLINKTYPE*YP_RES_SIZE+3 )` | 250503 | 自动采用弹性里程计算结果 即之前的参数YP_LINKUSETH  Automatically adopt elastic mileage calculation results |
| `YP_ISOLATFLRNUM` | `2506` | 2506 | 隔震层数 Number of isolation floors |
| `YP_ISOLATFLRS` | `2507` | 2507 | 隔震层层号 整数数组 isolation floor No |
| `YP_ISOLATDESIGNTYPE` | `2508` | 2508 | 隔震结构设计方法  Design method of isolated structure |
| ↳ `YP_ISOLATDESIGNTYPE_DIVISION` | `( YP_ISOLATDESIGNTYPE*YP_RES_SIZE+1 )` | 250801 | 分部设计法  Divisional design method |
| ↳ `YP_ISOLATDESIGNTYPE_DIRECT` | `( YP_ISOLATDESIGNTYPE*YP_RES_SIZE+2 )` | 250802 | 直接设计法 Direct design method |
| `YP_ISOLATDBJLFLRS` | `2509` | 2509 | 计算底部剪力比的层号 整数数组 |
| `YP_ISOLATSEIS_DQGD` | `2510` | 2510 | 读取刚度 |
| `YP_ISOLATSEIS_DQZNXS` | `2511` | 2511 | 读取阻尼系数 |
| `YP_ISOLATD_BQF` | `2552` | 2552 | 大震计算模型是否不屈服 |
| `YP_ISOLATD_TX` | `2553` | 2553 | 大震计算模型是否弹性 |
| `YP_ISOLATD_MAXALPHA` | `2554` | 2554 | 大震地震影响系数最大值 |
| `YP_ISOLATD_TG` | `2555` | 2555 | 大震特征周期 |
| `YP_ISOLATD_ZQZJ` | `2556` | 2556 | 大震周期折减系数 |
| `YP_ISOLATDBQF_DAMPTYPE` | `2561` | 2561 | 大震不屈服 阻尼比设置类型 值为 YPV_DAMP_TOTAL/YPV_DAMP_BYMAT |
| `YP_ISOLATDBQF_DAMP` | `2562` | 2562 | 大震不屈服 全楼统一 阻尼比数值 |
| `YP_ISOLATDBQF_DAMPMATIDS` | `2564` | 2564 | 大震不屈服 分材料阻尼比时各材料ID(int数组，第一个为数组大小) 暂按yjkidkind.h中标准材料号记录 如钢--IDM_Steel  砼--IDM_Concrete |
| `YP_ISOLATDBQF_DAMPMATDAMPS` | `2565` | 2565 | 大震不屈服 分材料阻尼比时各材料阻尼比值(%)(float数组，第一个为数组大小) |
| `YP_ISOLATDBQF_LLZJ` | `2566` | 2566 | 大震不屈服 连梁刚度折减系数 |
| `YP_ISOLATDBQF_ZLFD` | `2567` | 2567 | 大震不屈服 中梁刚度放大系数 |
| `YP_ISOLATDBQF_SXDZ` | `2568` | 2568 | 大震不屈服 考虑双向地震作用 |
| `YP_ISOLATDTX_DAMPTYPE` | `2571` | 2571 | 大震弹性 阻尼比设置类型 值为 YPV_DAMP_TOTAL/YPV_DAMP_BYMAT |
| `YP_ISOLATDTX_DAMP` | `2572` | 2572 | 大震弹性 全楼统一 阻尼比数值 |
| `YP_ISOLATDTX_DAMPMATIDS` | `2574` | 2574 | 大震弹性 分材料阻尼比时各材料ID(int数组，第一个为数组大小) 暂按yjkidkind.h中标准材料号记录 如钢--IDM_Steel  砼--IDM_Concrete |
| `YP_ISOLATDTX_DAMPMATDAMPS` | `2575` | 2575 | 大震弹性 分材料阻尼比时各材料阻尼比值(%)(float数组，第一个为数组大小) |
| `YP_ISOLATDTX_LLZJ` | `2576` | 2576 | 大震弹性 连梁刚度折减系数 |
| `YP_ISOLATDTX_ZLFD` | `2577` | 2577 | 大震弹性 中梁刚度放大系数 |
| `YP_ISOLATDTX_SXDZ` | `2578` | 2578 | 大震弹性 考虑双向地震作用 |
| `YP_ISOLATD_GJCQXS` | `2579` | 2579 | 考虑钢筋超强系数 |
| `YP_ISOLATD_YNJZGC` | `2580` | 2580 | 考虑云南减震规程  已经不用了，放在了减震结构设计方法里 |
| `YP_ISOLATD_KZSF` | `2581` | 2581 | 采用第一类抗震设防目标 |
| `YP_ISOLATD_REDUCTIONFACTOR` | `2582` | 2582 | 阻尼比折减系数 |
| `YP_ISOLATD_FGZMX` | `2583` | 2583 | 计算中震非隔震模型 |
| `YP_ISOLATSEIS_JZ` | `2584` | 2584 | 是否采用 减震 |
| `YP_ISOLATDESIGNTYPE_JZ` | `2585` | 2585 | 减震结构设计方法 |
| ↳ `YPV_ISOLATDESIGNTYPE_KG` | `( YP_ISOLATDESIGNTYPE_JZ*YP_RES_SIZE+1 )` | 258501 | 抗规 |
| ↳ `YPV_ISOLATDESIGNTYPE_DZ` | `( YP_ISOLATDESIGNTYPE_JZ*YP_RES_SIZE+2 )` | 258502 | 导则 |
| ↳ `YPV_ISOLATDESIGNTYPE_YN` | `( YP_ISOLATDESIGNTYPE_JZ*YP_RES_SIZE+3 )` | 258503 | 云南 |
| ↳ `YPV_ISOLATDESIGNTYPE_BJ` | `( YP_ISOLATDESIGNTYPE_JZ*YP_RES_SIZE+4 )` | 258504 | 北京 |
| ↳ `YPV_ISOLATDESIGNTYPE_HB` | `( YP_ISOLATDESIGNTYPE_JZ*YP_RES_SIZE+5 )` | 258505 | 河北 |
| ↳ `YPV_ISOLATDESIGNTYPE_SH` | `( YP_ISOLATDESIGNTYPE_JZ*YP_RES_SIZE+6 )` | 258506 | 上海 |
| `YP_ISOLATD_MAXALPHA_XZ` | `2586` | 2586 | 小震地震影响系数最大值 |

### 27. 安全鉴定

原文节注释行（逐字）：

```c
//////////////////////////////////////////////////////////////////////////////
//安全鉴定
```

| 宏名 | 取值 | = 实际值 | 原文注释 |
|---|---|---|---|
| `YP_AQJD` | `2600` | 2600 | 是否进行安全鉴定 |
| `YP_AQJD_JDBZ` | `2601` | 2601 | 采用哪种鉴定标准 |
| ↳ `YPV_AQJD_GB50292_2015` | `( YP_AQJD_JDBZ*YP_RES_SIZE+1 )` | 260101 | 民用建筑 |
| ↳ `YPV_AQJD_GB50144_2019` | `( YP_AQJD_JDBZ*YP_RES_SIZE+2 )` | 260102 | 工业建筑 |
| ↳ `YPV_AQJD_JGJ125_2016` | `( YP_AQJD_JDBZ*YP_RES_SIZE+3 )` | 260103 | 危险房屋 |
| ↳ `YPV_AQJD_DB11637_2015` | `( YP_AQJD_JDBZ*YP_RES_SIZE+4 )` | 260104 | 房屋结构综合安全性鉴定标准 |
| `YP_AQJD_CONCRETECODE` | `2602` | 2602 | 采用哪种混凝土规范 |
| ↳ `YPV_AQJD_89CODE` | `( YP_AQJD_CONCRETECODE*YP_RES_SIZE+1 )` | 260201 | 89系列 |
| ↳ `YPV_AQJD_01CODE` | `( YP_AQJD_CONCRETECODE*YP_RES_SIZE+2 )` | 260202 | 01系列 |
| ↳ `YPV_AQJD_10CODE` | `( YP_AQJD_CONCRETECODE*YP_RES_SIZE+3 )` | 260203 | 10系列 |
| `YP_AQJD_CONSIDERSEIS` | `2603` | 2603 | 是否考虑地震组合 |
| `YP_AQJD_JGHJMJD` | `2604` | 2604 | 按加固后截面鉴定 |
| `YP_AQJD_JBYXXS` | `2605` | 2605 | 考虑承载力折减系数 |
| `YP_AQJD_HNTGJPJBZ_MinYong` | `2606` | 2606 | 民用混凝土构件评级标准 float数组 // 这六个数组第一位是元素个数（8个所以第一位一定是8） |
| `YP_AQJD_GGJPJBZ_MinYong` | `2607` | 2607 | 民用钢构件评级标准 float数组     // 接着是元素，元素按列的顺序存储，也就是先是a标准下的 |
| `YP_AQJD_QTGJPJBZ_MinYong` | `2608` | 2608 | 民用砌体构件评级标准 float数组   // 重要构件、次要构件，再是b标准下的重要构件、次要构件 |
| `YP_AQJD_HNTGJPJBZ_GongYe` | `2609` | 2609 | 工业混凝土构件评级标准 float数组 // 具体采用民用的这三个数组还是工业这三个，需要先获取 |
| `YP_AQJD_GGJPJBZ_GongYe` | `2610` | 2610 | 工业钢构件评级标准 float数组	 	// 采用哪种鉴定标准，再根据这个提取到的宏，选择民用还是 |
| `YP_AQJD_QTGJPJBZ_GongYe` | `2611` | 2611 | 工业砌体构件评级标准 float数组 |
| `YP_AQJD_HNTGJPJBZ_BJ` | `2615` | 2615 | 北京地标混凝土构件评级标准 float数组 |
| `YP_AQJD_GGJPJBZ_BJ` | `2616` | 2616 | 北京地标钢构件评级标准 float数组 |
| `YP_AQJD_QTGJPJBZ_BJ` | `2617` | 2617 | 北京地标砌体构件评级标准 float数组 |
| `YP_AQJD_DCFW` | `2612` | 2612 | 是否采用单层房屋设计 |
| `YP_AQJD_PDXS` | `2613` | 2613 | 砼构件评定形式 |
| ↳ `YPV_KLXY` | `( YP_AQJD_PDXS*YP_RES_SIZE+1 )` | 261301 | 抗力效应比 |
| ↳ `YPV_GJMJ` | `( YP_AQJD_PDXS*YP_RES_SIZE+2 )` | 261302 | 钢筋面积比 |
| `YP_AQJD_FZPJ` | `2614` | 2614 | 构件按分组评级 |

### 28. 危险房屋

原文节注释行（逐字）：

```c
//////////////////////////////////////////////////////////////////////////////
//危险房屋
```

| 宏名 | 取值 | = 实际值 | 原文注释 |
|---|---|---|---|
| `YP_WXFW` | `2700` | 2700 | 是否进行危险房屋鉴定 |
| `YP_WXFW_JDBZ` | `2701` | 2701 | 采用哪种鉴定标准 |
| ↳ `YPV_WXFW_GB50292_2015` | `( YP_WXFW_JDBZ*YP_RES_SIZE+1 )` | 270101 | 危险房屋鉴定标准 |
| `YP_WXFW_TYPE` | `2702` | 2702 | 房屋类型 |
| ↳ `YPV_WXFW_1` | `( YP_WXFW_TYPE*YP_RES_SIZE+1 )` | 270201 | 1类房屋 |
| ↳ `YPV_WXFW_2` | `( YP_WXFW_TYPE*YP_RES_SIZE+2 )` | 270202 | 2类房屋 |
| ↳ `YPV_WXFW_3` | `( YP_WXFW_TYPE*YP_RES_SIZE+3 )` | 270203 | 3类房屋 |
| `YP_WXFW_CONSIDERSEIS` | `2703` | 2703 | 是否考虑地震组合 |
| `YP_WXFW_TZXS` | `2704` | 2704 | 调整系数 float数组       // 存放方式同上面的安全鉴定的数组 |
| `YP_WXFW_KLXYB` | `2705` | 2705 | 抗力效应比 float数组     // 存放方式同上面的安全鉴定的数组 |
| `YP_WXFW_GJSL` | `2706` | 2706 | 危险构件数量 int数组     第一位是数组大小 二是行数，三是列数，后面是数据，按每行存的数据 |
| `YP_WXFW_PDXS` | `2707` | 2707 | 砼构件评定形式 |

### 29. 非线性屈曲参数

原文节注释行（逐字）：

```c
//////////////////////////////////////////////////////////////////////////
//非线性屈曲参数
```

| 宏名 | 取值 | = 实际值 | 原文注释 |
|---|---|---|---|
| `YP_Nonlinear` | `2801` | 2801 | 是否采用非线性屈曲 |
| `YP_NL_Solver` | `2802` | 2802 | 求解器类型 |
| ↳ `YPV_Solver_PARDDIRECT` | `( YP_NL_Solver*YP_RES_SIZE+1 )` | 280201 | Pardiso Direct |
| ↳ `YPV_Solver_PARDITERAIVE` | `( YP_NL_Solver*YP_RES_SIZE+2 )` | 280202 | Pardiso Interaive |
| ↳ `YPV_Solver_PARDCOUPLE` | `( YP_NL_Solver*YP_RES_SIZE+3 )` | 280203 | Pardiso Couple |
| `YP_NL_Type` | `2803` | 2803 | 非线性类型 |
| ↳ `YPV_Type_Geometry` | `( YP_NL_Type*YP_RES_SIZE+1 )` | 280301 | 几何非线性 |
| ↳ `YPV_Type_Material` | `( YP_NL_Type*YP_RES_SIZE+2 )` | 280302 | 材料非线性 |
| ↳ `YPV_Type_Geometry_Material` | `( YP_NL_Type*YP_RES_SIZE+3 )` | 280303 | 几何和材料非线性 |
| `YP_NL_Iteration` | `2804` | 2804 | 迭代方法 |
| ↳ `YPV_Iteration_QMHCZZ` | `( YP_NL_Iteration*YP_RES_SIZE+1 )` | 280401 | 切面弧长 |
| ↳ `YPV_Iteration_CWGZZ` | `( YP_NL_Iteration*YP_RES_SIZE+2 )` | 280402 | 常外功准则 |
| ↳ `YPV_Iteration_GYGDCSZZ` | `( YP_NL_Iteration*YP_RES_SIZE+3 )` | 280403 | 广义刚度参数准则 |
| ↳ `YPV_Iteration_NDLPSDD` | `( YP_NL_Iteration*YP_RES_SIZE+4 )` | 280404 | 牛顿-拉普森迭代 |
| `YP_NL_Error` | `2805` | 2805 | 迭代误差 |
| `YP_NL_Step` | `2806` | 2806 | 步长类型控制 |
| ↳ `YPV_Step_Change` | `( YP_NL_Step*YP_RES_SIZE+1 )` | 280601 | 变步长 |
| ↳ `YPV_Step_Determine` | `( YP_NL_Step*YP_RES_SIZE+2 )` | 280602 | 定步长 |
| `YP_NL_CountSteps` | `2807` | 2807 | 计算步数勾选框 |
| `YP_NL_CountSteps_EDIT` | `2808` | 2808 | 计算步数数值 |
| `YP_NL_MaxFactor` | `2809` | 2809 | 最大荷载系数勾选框 |
| `YP_NL_MaxFactor_EDIT` | `2810` | 2810 | 最大荷载系数数值 |
| `YP_NL_Displacement` | `2811` | 2811 | 节点位移勾选框 |
| `YP_NL_InitialIncrement` | `2812` | 2812 | 初始荷载系数增量 |
| `YP_NL_NodeNo` | `2813` | 2813 | 控制点编号 |
| `YP_NL_MaxDisplacement` | `2814` | 2814 | 位移最大值 |
| `YP_NL_Component` | `2815` | 2815 | 位移分量 |
| ↳ `YPV_Component_X` | `( YP_NL_Component*YP_RES_SIZE+1 )` | 281501 | X |
| ↳ `YPV_Component_Y` | `( YP_NL_Component*YP_RES_SIZE+2 )` | 281502 | Y |
| ↳ `YPV_Component_Z` | `( YP_NL_Component*YP_RES_SIZE+3 )` | 281503 | Z |
| ↳ `YPV_Component_COM` | `( YP_NL_Component*YP_RES_SIZE+4 )` | 281504 | COM |
| `YP_NL_MinIncrement` | `2816` | 2816 | 最小荷载系数增量 |
| `YP_NL_MaxIncrement` | `2817` | 2817 | 最大荷载系数增量 |
| `YP_NL_IterationNo` | `2818` | 2818 | 期望迭代次数 |
| `YP_NL_MaxIteration` | `2819` | 2819 | 最大迭代次数 |
| `YP_NL_Increment_Determine` | `2820` | 2820 | 荷载系统增量——定步长 |
| `YP_NL_MaxIteration_Determine` | `2821` | 2821 | 最大迭代次数——定步长 |
| `YP_NL_Combine` | `2822` | 2822 | 荷载组合 同非线性荷载组合 |

### 30. 整体性等级评定 工业

原文节注释行（逐字）：

```c
//////////////////////////////////////////////////////////////////////////
//整体性等级评定 工业
```

| 宏名 | 取值 | = 实际值 | 原文注释 |
|---|---|---|---|
| `YP_ZTXDJ_DJ_GY` | `2900` | 2900 | 等级 |
| ↳ `YPV_ZTXDJ_Au_GY` | `( YP_ZTXDJ_DJ_GY*YP_RES_SIZE+1 )` | 290001 | Au |
| ↳ `YPV_ZTXDJ_Bu_GY` | `( YP_ZTXDJ_DJ_GY*YP_RES_SIZE+2 )` | 290002 | Bu |
| ↳ `YPV_ZTXDJ_Cu_GY` | `( YP_ZTXDJ_DJ_GY*YP_RES_SIZE+3 )` | 290003 | Cu |
| ↳ `YPV_ZTXDJ_Du_GY` | `( YP_ZTXDJ_DJ_GY*YP_RES_SIZE+4 )` | 290004 | Du |
| `YP_ZTXDJ_JGBZ_GONGYE` | `2901` | 2901 | 结构布置及构造 字符串 char*   yjkGetSPara(YP)->pcVal; |
| `YP_ZTXDJ_DJ_JGBZ_GY` | `2902` | 2902 | 结构布置及构造 的等级 |
| ↳ `YPV_ZTXDJ_Au_JGBZ_GY` | `( YP_ZTXDJ_DJ_JGBZ_GY*YP_RES_SIZE+1 )` | 290201 | Au |
| ↳ `YPV_ZTXDJ_Bu_JGBZ_GY` | `( YP_ZTXDJ_DJ_JGBZ_GY*YP_RES_SIZE+2 )` | 290202 | Bu |
| ↳ `YPV_ZTXDJ_Cu_JGBZ_GY` | `( YP_ZTXDJ_DJ_JGBZ_GY*YP_RES_SIZE+3 )` | 290203 | Cu |
| ↳ `YPV_ZTXDJ_Du_JGBZ_GY` | `( YP_ZTXDJ_DJ_JGBZ_GY*YP_RES_SIZE+4 )` | 290204 | Du |
| `YP_ZTXDJ_ZCXT_GONGYE` | `2903` | 2903 | 支撑系统或其他抗侧力系统的构造 字符串 char*   yjkGetSPara(YP_ZTXDJ_ZCXT_MINYONG)->pcVal; |
| `YP_ZTXDJ_DJ_ZCXT_GY` | `2904` | 2904 | 支撑系统或其他抗侧力系统的构造 的等级 |
| ↳ `YPV_ZTXDJ_Au_ZCXT_GY` | `( YP_ZTXDJ_DJ_ZCXT_GY*YP_RES_SIZE+1 )` | 290401 | Au |
| ↳ `YPV_ZTXDJ_Bu_ZCXT_GY` | `( YP_ZTXDJ_DJ_ZCXT_GY*YP_RES_SIZE+2 )` | 290402 | Bu |
| ↳ `YPV_ZTXDJ_Cu_ZCXT_GY` | `( YP_ZTXDJ_DJ_ZCXT_GY*YP_RES_SIZE+3 )` | 290403 | Cu |
| ↳ `YPV_ZTXDJ_Du_ZCXT_GY` | `( YP_ZTXDJ_DJ_ZCXT_GY*YP_RES_SIZE+4 )` | 290404 | Du |

### 31. 侧向位移评定等级

原文节注释行（逐字）：

```c
//////////////////////////////////////////////////////////////////////////
//侧向位移评定等级
```

| 宏名 | 取值 | = 实际值 | 原文注释 |
|---|---|---|---|
| `YP_CXWY` | `3000` | 3000 | 侧向位移表格 第一位是数组大小 二是行数，三是列数，后面是数据，按每行存的数据 float |
| `YP_CXWY_DJ` | `3001` | 3001 | 等级 |
| ↳ `YPV_CXWY_Au` | `( YP_CXWY_DJ*YP_RES_SIZE+1 )` | 300101 | Au |
| ↳ `YPV_CXWY_Bu` | `( YP_CXWY_DJ*YP_RES_SIZE+2 )` | 300102 | Bu |
| ↳ `YPV_CXWY_Cu` | `( YP_CXWY_DJ*YP_RES_SIZE+3 )` | 300103 | Cu |
| ↳ `YPV_CXWY_Du` | `( YP_CXWY_DJ*YP_RES_SIZE+4 )` | 300104 | Du |
| `YP_CXWY_CD` | `3002` | 3002 | 侧向位移表格测点名称  yjkGetStringVectorSPara()读取 传入CStringArray 的对象 然后下标读取 |

### 32. 整体性等级评定 民用

原文节注释行（逐字）：

```c
//////////////////////////////////////////////////////////////////////////
//整体性等级评定 民用
```

| 宏名 | 取值 | = 实际值 | 原文注释 |
|---|---|---|---|
| `YP_ZTXDJ_DJ` | `3100` | 3100 | 等级 |
| ↳ `YPV_ZTXDJ_Au` | `( YP_ZTXDJ_DJ*YP_RES_SIZE+1 )` | 310001 | Au |
| ↳ `YPV_ZTXDJ_Bu` | `( YP_ZTXDJ_DJ*YP_RES_SIZE+2 )` | 310002 | Bu |
| ↳ `YPV_ZTXDJ_Cu` | `( YP_ZTXDJ_DJ*YP_RES_SIZE+3 )` | 310003 | Cu |
| ↳ `YPV_ZTXDJ_Du` | `( YP_ZTXDJ_DJ*YP_RES_SIZE+4 )` | 310004 | Du |
| `YP_ZTXDJ_JGBZ_MINYONG` | `3101` | 3101 | 结构布置及构造 字符串 char*   yjkGetSPara(YP)->pcVal; |
| `YP_ZTXDJ_DJ_JGBZ` | `3102` | 3102 | 结构布置及构造 的等级 |
| ↳ `YPV_ZTXDJ_Au_JGBZ` | `( YP_ZTXDJ_DJ_JGBZ*YP_RES_SIZE+1 )` | 310201 | Au |
| ↳ `YPV_ZTXDJ_Bu_JGBZ` | `( YP_ZTXDJ_DJ_JGBZ*YP_RES_SIZE+2 )` | 310202 | Bu |
| ↳ `YPV_ZTXDJ_Cu_JGBZ` | `( YP_ZTXDJ_DJ_JGBZ*YP_RES_SIZE+3 )` | 310203 | Cu |
| ↳ `YPV_ZTXDJ_Du_JGBZ` | `( YP_ZTXDJ_DJ_JGBZ*YP_RES_SIZE+4 )` | 310204 | Du |
| `YP_ZTXDJ_ZCXT_MINYONG` | `3103` | 3103 | 支撑系统或其他抗侧力系统的构造 字符串 char*   yjkGetSPara(YP_ZTXDJ_ZCXT_MINYONG)->pcVal; |
| `YP_ZTXDJ_DJ_ZCXT` | `3104` | 3104 | 支撑系统或其他抗侧力系统的构造 的等级 |
| ↳ `YPV_ZTXDJ_Au_ZCXT` | `( YP_ZTXDJ_DJ_ZCXT*YP_RES_SIZE+1 )` | 310401 | Au |
| ↳ `YPV_ZTXDJ_Bu_ZCXT` | `( YP_ZTXDJ_DJ_ZCXT*YP_RES_SIZE+2 )` | 310402 | Bu |
| ↳ `YPV_ZTXDJ_Cu_ZCXT` | `( YP_ZTXDJ_DJ_ZCXT*YP_RES_SIZE+3 )` | 310403 | Cu |
| ↳ `YPV_ZTXDJ_Du_ZCXT` | `( YP_ZTXDJ_DJ_ZCXT*YP_RES_SIZE+4 )` | 310404 | Du |
| `YP_ZTXDJ_GJLX_MINYONG` | `3105` | 3105 | 结构、构件间的联系 字符串 char*   yjkGetSPara(YP_ZTXDJ_ZCXT_MINYONG)->pcVal; |
| `YP_ZTXDJ_DJ_GJLX` | `3106` | 3106 | 结构、构件间的联系 的等级 |
| ↳ `YPV_ZTXDJ_Au_GJLX` | `( YP_ZTXDJ_DJ_GJLX*YP_RES_SIZE+1 )` | 310601 | Au |
| ↳ `YPV_ZTXDJ_Bu_GJLX` | `( YP_ZTXDJ_DJ_GJLX*YP_RES_SIZE+2 )` | 310602 | Bu |
| ↳ `YPV_ZTXDJ_Cu_GJLX` | `( YP_ZTXDJ_DJ_GJLX*YP_RES_SIZE+3 )` | 310603 | Cu |
| ↳ `YPV_ZTXDJ_Du_GJLX` | `( YP_ZTXDJ_DJ_GJLX*YP_RES_SIZE+4 )` | 310604 | Du |
| `YP_ZTXDJ_BZGZ_MINYONG` | `3107` | 3107 | 砌体结构中圈梁及构造柱的布置与构造 字符串 char*   yjkGetSPara(YP_ZTXDJ_ZCXT_MINYONG)->pcVal; |
| `YP_ZTXDJ_DJ_BZGZ` | `3108` | 3108 | 砌体结构中圈梁及构造柱的布置与构造 的等级 |
| ↳ `YPV_ZTXDJ_Au_BZGZ` | `( YP_ZTXDJ_DJ_BZGZ*YP_RES_SIZE+1 )` | 310801 | Au |
| ↳ `YPV_ZTXDJ_Bu_BZGZ` | `( YP_ZTXDJ_DJ_BZGZ*YP_RES_SIZE+2 )` | 310802 | Bu |
| ↳ `YPV_ZTXDJ_Cu_BZGZ` | `( YP_ZTXDJ_DJ_BZGZ*YP_RES_SIZE+3 )` | 310803 | Cu |
| ↳ `YPV_ZTXDJ_Du_BZGZ` | `( YP_ZTXDJ_DJ_BZGZ*YP_RES_SIZE+4 )` | 310804 | Du |

### 33. 围护结构定等级民用

原文节注释行（逐字）：

```c
//////////////////////////////////////////////////////////////////////////
//围护结构定等级民用
```

| 宏名 | 取值 | = 实际值 | 原文注释 |
|---|---|---|---|
| `YP_WHJG_DJ_MY` | `3200` | 3200 | 围护系统等级 |
| ↳ `YPV_WHJG_Au_MY` | `( YP_WHJG_DJ_MY*YP_RES_SIZE+1 )` | 320001 | Au |
| ↳ `YPV_WHJG_Bu_MY` | `( YP_WHJG_DJ_MY*YP_RES_SIZE+2 )` | 320002 | Bu |
| ↳ `YPV_WHJG_Cu_MY` | `( YP_WHJG_DJ_MY*YP_RES_SIZE+3 )` | 320003 | Cu |
| ↳ `YPV_WHJG_Du_MY` | `( YP_WHJG_DJ_MY*YP_RES_SIZE+4 )` | 320004 | Du |
| `YP_WHJG_DJ_CZGN_MY` | `3201` | 3201 | 承载功能等级 |
| ↳ `YPV_WHJG_Au_CZGN_MY` | `( YP_WHJG_DJ_CZGN_MY*YP_RES_SIZE+1 )` | 320101 | Au |
| ↳ `YPV_WHJG_Bu_CZGN_MY` | `( YP_WHJG_DJ_CZGN_MY*YP_RES_SIZE+2 )` | 320102 | Bu |
| ↳ `YPV_WHJG_Cu_CZGN_MY` | `( YP_WHJG_DJ_CZGN_MY*YP_RES_SIZE+3 )` | 320103 | Cu |
| ↳ `YPV_WHJG_Du_CZGN_MY` | `( YP_WHJG_DJ_CZGN_MY*YP_RES_SIZE+4 )` | 320104 | Du |
| `YP_WHJG_DJ_ZTX_MY` | `3202` | 3202 | 结构整体性等级 |
| ↳ `YPV_WHJG_Au_ZTX_MY` | `( YP_WHJG_DJ_ZTX_MY*YP_RES_SIZE+1 )` | 320201 | Au |
| ↳ `YPV_WHJG_Bu_ZTX_MY` | `( YP_WHJG_DJ_ZTX_MY*YP_RES_SIZE+2 )` | 320202 | Bu |
| ↳ `YPV_WHJG_Cu_ZTX_MY` | `( YP_WHJG_DJ_ZTX_MY*YP_RES_SIZE+3 )` | 320203 | Cu |
| ↳ `YPV_WHJG_Du_ZTX_MY` | `( YP_WHJG_DJ_ZTX_MY*YP_RES_SIZE+4 )` | 320204 | Du |

### 34. 围护结构评定等级工业

原文节注释行（逐字）：

```c
//////////////////////////////////////////////////////////////////////////
//围护结构评定等级工业
```

| 宏名 | 取值 | = 实际值 | 原文注释 |
|---|---|---|---|
| `YP_WHJG_DJ_GY` | `3300` | 3300 | 围护系统等级 |
| ↳ `YPV_WHJG_Au_GY` | `( YP_WHJG_DJ_GY*YP_RES_SIZE+1 )` | 330001 | Au |
| ↳ `YPV_WHJG_Bu_GY` | `( YP_WHJG_DJ_GY*YP_RES_SIZE+2 )` | 330002 | Bu |
| ↳ `YPV_WHJG_Cu_GY` | `( YP_WHJG_DJ_GY*YP_RES_SIZE+3 )` | 330003 | Cu |
| ↳ `YPV_WHJG_Du_GY` | `( YP_WHJG_DJ_GY*YP_RES_SIZE+4 )` | 330004 | Du |
| `YP_WHJG_DJ_CZGN_GY` | `3301` | 3301 | 承载功能等级 |
| ↳ `YPV_WHJG_Au_CZGN_GY` | `( YP_WHJG_DJ_CZGN_GY*YP_RES_SIZE+1 )` | 330101 | Au |
| ↳ `YPV_WHJG_Bu_CZGN_GY` | `( YP_WHJG_DJ_CZGN_GY*YP_RES_SIZE+2 )` | 330102 | Bu |
| ↳ `YPV_WHJG_Cu_CZGN_GY` | `( YP_WHJG_DJ_CZGN_GY*YP_RES_SIZE+3 )` | 330103 | Cu |
| ↳ `YPV_WHJG_Du_CZGN_GY` | `( YP_WHJG_DJ_CZGN_GY*YP_RES_SIZE+4 )` | 330104 | Du |
| `YP_WHJG_DJ_GZLJ_GY` | `3302` | 3302 | 构造连接等级 |
| ↳ `YPV_WHJG_Au_GZLJ_GY` | `( YP_WHJG_DJ_GZLJ_GY*YP_RES_SIZE+1 )` | 330201 | Au |
| ↳ `YPV_WHJG_Bu_GZLJ_GY` | `( YP_WHJG_DJ_GZLJ_GY*YP_RES_SIZE+2 )` | 330202 | Bu |
| ↳ `YPV_WHJG_Cu_GZLJ_GY` | `( YP_WHJG_DJ_GZLJ_GY*YP_RES_SIZE+3 )` | 330203 | Cu |
| ↳ `YPV_WHJG_Du_GZLJ_GY` | `( YP_WHJG_DJ_GZLJ_GY*YP_RES_SIZE+4 )` | 330204 | Du |

### 35. 构件承载能力评定验算子项设置

原文节注释行（逐字）：

```c
//////////////////////////////////////////////////////////////////////////
// 构件承载能力评定验算子项设置
```

| 宏名 | 取值 | = 实际值 | 原文注释 |
|---|---|---|---|
| `YP_LoadCapacity_BeamTop_AQJD` | `3400` | 3400 | 安全鉴定页面下的 梁顶弯矩勾选框 |
| `YP_LoadCapacity_BeamBottom_AQJD` | `3401` | 3401 | 安全鉴定页面下的 梁底弯矩勾选框 |
| `YP_LoadCapacity_Shear_AQJD` | `3402` | 3402 | 安全鉴定页面下的 剪力勾选框 |
| `YP_LoadCapacity_BeamTop_WXFW` | `3403` | 3403 | 危险房屋页面下的 梁顶弯矩勾选框 |
| `YP_LoadCapacity_BeamBottom_WXFW` | `3404` | 3404 | 危险房屋页面下的 梁底弯矩勾选框 |
| `YP_LoadCapacity_Shear_WXFW` | `3405` | 3405 | 危险房屋页面下的 剪力勾选框 |

### 36. 减震性能包络设计

原文节注释行（逐字）：

```c
//////////////////////////////////////////////////////////////////////////
// 减震性能包络设计
```

| 宏名 | 取值 | = 实际值 | 原文注释 |
|---|---|---|---|
| `YP_XNSJBLJZ` | `3500` | 3500 | 进行减震性能包络设计 |
| `YP_JZBLZ_BQF` | `3501` | 3501 | 中震计算模型是否不屈服 |
| `YP_JZBLZ_TX` | `3502` | 3502 | 中震计算模型是否弹性 |
| `YP_JZBLZ_JXCZL` | `3503` | 3503 | 中震计算模型是否极限承载力 |
| `YP_JZBLZ_MAXALPHA` | `3504` | 3504 | 中震地震影响系数最大值 |
| `YP_JZBLZ_ZQZJ` | `3505` | 3505 | 中震周期折减系数 |
| `YP_JZBLZBQF_DAMPTYPE` | `3511` | 3511 | 中震不屈服 阻尼比设置类型 值为 YPV_DAMP_TOTAL/YPV_DAMP_BYMAT |
| `YP_JZBLZBQF_DAMP` | `3512` | 3512 | 中震不屈服 全楼统一 阻尼比数值 |
| `YP_JZBLZBQF_DAMPMATIDS` | `3514` | 3514 | 中震不屈服 分材料阻尼比时各材料ID(int数组，第一个为数组大小) 暂按yjkidkind.h中标准材料号记录 如钢--IDM_Steel  砼--IDM_Concrete |
| `YP_JZBLZBQF_DAMPMATDAMPS` | `3515` | 3515 | 中震不屈服 分材料阻尼比时各材料阻尼比值(%)(float数组，第一个为数组大小) |
| `YP_JZBLZBQF_LLZJ` | `3516` | 3516 | 中震不屈服 连梁刚度折减系数 |
| `YP_JZBLZBQF_ZLFD` | `3517` | 3517 | 中震不屈服 中梁刚度放大系数 |
| `YP_JZBLZBQF_SXDZ` | `3518` | 3518 | 中震不屈服 考虑双向地震作用 |
| `YP_JZBLZTX_DAMPTYPE` | `3521` | 3521 | 中震弹性 阻尼比设置类型 值为 YPV_DAMP_TOTAL/YPV_DAMP_BYMAT |
| `YP_JZBLZTX_DAMP` | `3522` | 3522 | 中震弹性 全楼统一 阻尼比数值 |
| `YP_JZBLZTX_DAMPMATIDS` | `3524` | 3524 | 中震弹性 分材料阻尼比时各材料ID(int数组，第一个为数组大小) 暂按yjkidkind.h中标准材料号记录 如钢--IDM_Steel  砼--IDM_Concrete |
| `YP_JZBLZTX_DAMPMATDAMPS` | `3525` | 3525 | 中震弹性 分材料阻尼比时各材料阻尼比值(%)(float数组，第一个为数组大小) |
| `YP_JZBLZTX_LLZJ` | `3526` | 3526 | 中震弹性 连梁刚度折减系数 |
| `YP_JZBLZTX_ZLFD` | `3527` | 3527 | 中震弹性 中梁刚度放大系数 |
| `YP_JZBLZTX_SXDZ` | `3528` | 3528 | 中震弹性 考虑双向地震作用 |
| `YP_JZBLZJXCZL_DAMPTYPE` | `3531` | 3531 | 中震极限承载力 阻尼比设置类型 值为 YPV_DAMP_TOTAL/YPV_DAMP_BYMAT |
| `YP_JZBLZJXCZL_DAMP` | `3532` | 3532 | 中震极限承载力 全楼统一 阻尼比数值 |
| `YP_JZBLZJXCZL_DAMPMATIDS` | `3534` | 3534 | 中震极限承载力 分材料阻尼比时各材料ID(int数组，第一个为数组大小) 暂按yjkidkind.h中标准材料号记录 如钢--IDM_Steel  砼--IDM_Concrete |
| `YP_JZBLZJXCZL_DAMPMATDAMPS` | `3535` | 3535 | 中震极限承载力 分材料阻尼比时各材料阻尼比值(%)(float数组，第一个为数组大小) |
| `YP_JZBLZJXCZL_LLZJ` | `3536` | 3536 | 中震极限承载力 连梁刚度折减系数 |
| `YP_JZBLZJXCZL_ZLFD` | `3537` | 3537 | 中震极限承载力 中梁刚度放大系数 |
| `YP_JZBLZJXCZL_SXDZ` | `3538` | 3538 | 中震极限承载力 考虑双向地震作用 |
| `YP_JZBLD_BQF` | `3542` | 3542 | 大震计算模型是否不屈服 |
| `YP_JZBLD_TX` | `3543` | 3543 | 大震计算模型是否弹性 |
| `YP_JZBLD_JXCZL` | `3544` | 3544 | 大震计算模型是极限承载力 |
| `YP_JZBLD_MAXALPHA` | `3545` | 3545 | 大震地震影响系数最大值 |
| `YP_JZBLD_TG` | `3546` | 3546 | 大震特征周期 |
| `YP_JZBLD_ZQZJ` | `3547` | 3547 | 大震周期折减系数 |
| `YP_JZBLDBQF_DAMPTYPE` | `3551` | 3551 | 大震不屈服 阻尼比设置类型 值为 YPV_DAMP_TOTAL/YPV_DAMP_BYMAT |
| `YP_JZBLDBQF_DAMP` | `3552` | 3552 | 大震不屈服 全楼统一 阻尼比数值 |
| `YP_JZBLDBQF_DAMPMATIDS` | `3554` | 3554 | 大震不屈服 分材料阻尼比时各材料ID(int数组，第一个为数组大小) 暂按yjkidkind.h中标准材料号记录 如钢--IDM_Steel  砼--IDM_Concrete |
| `YP_JZBLDBQF_DAMPMATDAMPS` | `3555` | 3555 | 大震不屈服 分材料阻尼比时各材料阻尼比值(%)(float数组，第一个为数组大小) |
| `YP_JZBLDBQF_LLZJ` | `3556` | 3556 | 大震不屈服 连梁刚度折减系数 |
| `YP_JZBLDBQF_ZLFD` | `3557` | 3557 | 大震不屈服 中梁刚度放大系数 |
| `YP_JZBLDBQF_SXDZ` | `3558` | 3558 | 大震不屈服 考虑双向地震作用 |
| `YP_JZBLDTX_DAMPTYPE` | `3561` | 3561 | 大震弹性 阻尼比设置类型 值为 YPV_DAMP_TOTAL/YPV_DAMP_BYMAT |
| `YP_JZBLDTX_DAMP` | `3562` | 3562 | 大震弹性 全楼统一 阻尼比数值 |
| `YP_JZBLDTX_DAMPMATIDS` | `3564` | 3564 | 大震弹性 分材料阻尼比时各材料ID(int数组，第一个为数组大小) 暂按yjkidkind.h中标准材料号记录 如钢--IDM_Steel  砼--IDM_Concrete |
| `YP_JZBLDTX_DAMPMATDAMPS` | `3565` | 3565 | 大震弹性 分材料阻尼比时各材料阻尼比值(%)(float数组，第一个为数组大小) |
| `YP_JZBLDTX_LLZJ` | `3566` | 3566 | 大震弹性 连梁刚度折减系数 |
| `YP_JZBLDTX_ZLFD` | `3567` | 3567 | 大震弹性 中梁刚度放大系数 |
| `YP_JZBLDTX_SXDZ` | `3568` | 3568 | 大震弹性 考虑双向地震作用 |
| `YP_JZBLDJXCZL_DAMPTYPE` | `3571` | 3571 | 大震极限承载力 阻尼比设置类型 值为 YPV_DAMP_TOTAL/YPV_DAMP_BYMAT |
| `YP_JZBLDJXCZL_DAMP` | `3572` | 3572 | 大震极限承载力 全楼统一 阻尼比数值 |
| `YP_JZBLDJXCZL_DAMPMATIDS` | `3574` | 3574 | 大震极限承载力 分材料阻尼比时各材料ID(int数组，第一个为数组大小) 暂按yjkidkind.h中标准材料号记录 如钢--IDM_Steel  砼--IDM_Concrete |
| `YP_JZBLDJXCZL_DAMPMATDAMPS` | `3575` | 3575 | 大震极限承载力 分材料阻尼比时各材料阻尼比值(%)(float数组，第一个为数组大小) |
| `YP_JZBLDJXCZL_LLZJ` | `3576` | 3576 | 大震极限承载力 连梁刚度折减系数 |
| `YP_JZBLDJXCZL_ZLFD` | `3577` | 3577 | 大震极限承载力 中梁刚度放大系数 |
| `YP_JZBLDJXCZL_SXDZ` | `3578` | 3578 | 大震极限承载力 考虑双向地震作用 |
| `YP_JZBLZJXCZL_YYCQXS` | `3581` | 3581 | 中震对水平构件的不屈服设计用于超强系数 |
| `YP_JZBLDJXCZL_YYCQXS` | `3582` | 3582 | 大震对水平构件的不屈服设计用于超强系数 |
| `YP_JZBL_JZLB` | `3583` | 3583 | 建筑类别 |
| ↳ `YPV_JZBL_JZLB1` | `( YP_JZBL_JZLB*YP_RES_SIZE+1 )` | 358301 | 一类 |
| ↳ `YPV_JZBL_JZLB2` | `( YP_JZBL_JZLB*YP_RES_SIZE+2 )` | 358302 | 二类 |

### 37. 自定义地震影响系数曲线参数（欧美）

原文节注释行（逐字）：

```c
//////////////////////////////////////////////////////////////////////////
//自定义地震影响系数曲线参数（欧美）
```

| 宏名 | 取值 | = 实际值 | 原文注释 |
|---|---|---|---|
| `YPE_CUSTA_S` | `3601` | 3601 | （欧_水平地震） |
| `YPE_CUSTA_TB` | `3602` | 3602 | （欧_水平地震） |
| `YPE_CUSTA_TC` | `3603` | 3603 | （欧_水平地震） |
| `YPE_CUSTA_TD` | `3604` | 3604 | （欧_水平地震） |
| `YPE_CUSTA_AGG` | `3605` | 3605 | （欧_水平地震）水平地震动峰值加速度ag/g |
| `YPE_CUSTA_Q` | `3606` | 3606 | （欧_水平地震）水平地震性能系数qh |
| `YPE_CUSTA_BETA` | `3607` | 3607 | （欧_水平地震）反应谱下限系数beta |
| `YPE_CUSTALPHA` | `3608` | 3608 | （欧_水平地震）自定义地震影响系数曲线 |
| `YPUS_CUSTA_SDS` | `3611` | 3611 | （美）计算系数 SDS = (2/3)*Fa*Ss |
| `YPUS_CUSTA_SD1` | `3612` | 3612 | （美）计算系数 SD1 = (2/3)*Fv*S1 |
| `YPUS_CUSTA_TL` | `3613` | 3613 | （美）过渡周期TL |
| `YPUS_CUSTA_R` | `3614` | 3614 | （美）反应调整系数R |
| `YPUS_CUSTA_I` | `3615` | 3615 | （美）重要性系数I |
| `YPUS_CUSTALPHA` | `3616` | 3616 | （美）自定义地震影响系数曲线 |
| `YP_ICUSTALPHA_V` | `3610` | 3610 | 使用自定义地震影响系数曲线 |
| `YPE_CUSTA_S_V` | `3609` | 3609 | （欧_竖向地震） |
| `YPE_CUSTA_TB_V` | `3617` | 3617 | （欧_竖向地震） |
| `YPE_CUSTA_TC_V` | `3618` | 3618 | （欧_竖向地震） |
| `YPE_CUSTA_TD_V` | `3619` | 3619 | （欧_竖向地震） |
| `YPE_CUSTA_AGG_V` | `3620` | 3620 | （欧_竖向地震）水平地震动峰值加速度ag/g |
| `YPE_CUSTA_Q_V` | `3621` | 3621 | （欧_竖向地震）水平地震性能系数qh |
| `YPE_CUSTA_BETA_V` | `3622` | 3622 | （欧_竖向地震）反应谱下限系数beta |
| `YPE_CUSTALPHA_V` | `3623` | 3623 | （欧_竖向地震）自定义地震影响系数曲线 |
| `YP_CUSTA_STEP_V` | `3624` | 3624 | 自定义地震影响系数曲线数据步长(s) |
| `YP_CUSTA_NSTEP_V` | `3625` | 3625 | 自定义地震影响系数曲线数据步数 |

### 38. 定制项目

原文节注释行（逐字）：

```c
//////////////////////////////////////////////////////////////////////////
// 定制项目
```

| 宏名 | 取值 | = 实际值 | 原文注释 |
|---|---|---|---|
| `YP_RFHZBYHORIZON` | `2401` | 2401 | 自定义人防按水平工况处理 |
| `YP_RFHZBYHORIZONDIR` | `2402` | 2402 | 自定义人防按水平工况处理时统计方向 |
| ↳ `YPV_RFHZBYHORIZONDIR_X` | `( YP_RFHZBYHORIZONDIR*YP_RES_SIZE+1 )` | 240201 | 按X向统计 |
| ↳ `YPV_RFHZBYHORIZONDIR_Y` | `( YP_RFHZBYHORIZONDIR*YP_RES_SIZE+2 )` | 240202 | 按Y向统计 |

### 39. 内置参数

原文节注释行（逐字）：

```c
//////////////////////////////////////////////////////////////////////
//内置参数
```

| 宏名 | 取值 | = 实际值 | 原文注释 |
|---|---|---|---|
| `YP_XNQ` | `2403` | 2403 | 是否启用消能器 |
| `YP_Inhaul_Cable` | `2404` | 2404 | 是否含有拉索 |
| `YP_TextStyle_ShapeFile` | `2405` | 2405 | 是否使用大字体 |
| `YP_TextStyle_Name` | `2406` | 2406 | 字体名   字符串 char*   yjkGetSPara(YP)->pcVal; |
| `YP_TextStyle_FontName` | `2407` | 2407 | 字体样式   字符串 char*   yjkGetSPara(YP)->pcVal; |
| `YP_TextStyle_BigFontName` | `2408` | 2408 | 大字体样式名称  字符串 char*   yjkGetSPara(YP)->pcVal; |
| `YP_TextStyle_Height` | `2409` | 2409 | 图纸文字高度 |
| `YP_TextStyle_WidthFactor` | `2410` | 2410 | 宽度因子 |
| `YP_TextStyle_Oblique` | `2411` | 2411 | 倾斜角度 |

### 40. 内部数据

原文节注释行（逐字）：

```c
//////////////////////////////////////////////////////////////////////////
//	内部数据
```

| 宏名 | 取值 | = 实际值 | 原文注释 |
|---|---|---|---|
| `YP_FLAG` | `10001` | 10001 | 参数状态 |

### 41. 建模参数

原文节注释行（逐字）：

```c
//////////////////////////////////////////////////////////////////////////
//建模参数
```

| 宏名 | 取值 | = 实际值 | 原文注释 |
|---|---|---|---|
| `YP_CADLBZZ` | `100000` | 100000 | 考虑楼板自重 |

### 42. 获取ID值如  int id1 = YPSC_GETWAVEPARA_ID(para)

原文节注释行（逐字）：

```c
//================================================
// 获取ID值如  int id1 = YPSC_GETWAVEPARA_ID(para)
```

| 宏名 | 取值 | = 实际值 | 原文注释 |
|---|---|---|---|

原文本节其余 `#define`（逐字）：

```c
#define YP_SCWAVEPARA_ID	0x0FFFFFFF	//用于取地震波参数中的ID (例 id = para & YP_SCWAVEPARA_ID)
#define YPSC_GETWAVEPARA_ID(para)  	\
#define YPSC_SETWAVEPARA_ID(para, id) \
#define YPSC_GETWAVEPARA_PRIM(para) \
#define YPSC_SETWAVEPARA_PRIM(para, bPrim) \
#define YPSC_GETWAVEPARA_SEC(para) \
#define YPSC_SETWAVEPARA_SEC(para, bSec) \
```

### 43. 用于yjkGetParaBound取参数限值返回值判断

原文节注释行（逐字）：

```c
//================================================
// 用于yjkGetParaBound取参数限值返回值判断
```

| 宏名 | 取值 | = 实际值 | 原文注释 |
|---|---|---|---|
| `YP_PARABOUND_ERROR` | `0` | 0 | 无限制，或不易限制 |

原文本节其余 `#define`（逐字）：

```c
#define YP_PARABOUND_FORCE		0x01	// 强制限制，不允许超出限制
#define YP_PARABOUND_WARNING	0x02	// 不强制，只警示
#define YP_PARABOUND_NOTEDIT	0x10	// 非编辑框限制
```

---

## 四、原文疑似笔误 / 重复值（逐字保留，未修改）

下列现象均为**原文本身**所有。本表只做如实记录，使用时请以实际软件行为为准。

### 4.1 同一枚举序号在同一个参数下重复定义

| 引用参数 | 枚举序号 | 冲突的枚举宏 |
|---|---|---|
| `YP_CSQXTYPE` | +1 | `YPV_CSQXTYPE_QQFX`、`YPV_SOLVERTYPE_SGMN_CSFD` |
| `YP_CSQXTYPE` | +2 | `YPV_CSQXTYPE_JXSPL`、`YPV_SOLVERTYPE_SGMN_PARDDIRECT` |
| `YP_GANGH` | +7 | `YPV_GH_Q560`、`YPV_GH_Q550` |

### 4.2 不同参数ID宏占用了同一个数值

（未检出：`YP_*` / `YPE_*` / `YPU_*` 参数ID宏的数值互不重复）

### 4.3 取值宏命名未带 `V`（写成 `YP_*` 而非 `YPV_*`）

这些宏的**作用**是枚举取值，但名字沿用了参数ID的 `YP_` 前缀。原文如此。

| 所在小节 | 原文引用的参数 | 取值宏 | 原文取值表达式 | 原文注释 |
|---|---|---|---|---|
| 计算总体信息 | `YP_ZHCGDMOTHED` | `YP_ZHCGDMOTHED_GGE03` | `( YP_ZHCGDMOTHED*YP_RES_SIZE+1 )` | 高规附录E.0.3 |
| 计算总体信息 | `YP_ZHCGDMOTHED` | `YP_ZHCGDMOTHED_GDCMDL` | `( YP_ZHCGDMOTHED*YP_RES_SIZE+2 )` | 刚度串模型 |
| 设计信息 | `YP_BYGJ_SZYJ` | `YP_BYGJ_KG645` | `( YP_BYGJ_SZYJ*YP_RES_SIZE+1 )` | 《抗规》GB50011 第6.4.5条 |
| 设计信息 | `YP_BYGJ_SZYJ` | `YP_BYGJ_GG7216` | `( YP_BYGJ_SZYJ*YP_RES_SIZE+2 )` | 《高规》JGJ3-2010 第7.2.16条 |
| 设计信息 | `YP_BYGJ_SZYJ` | `YP_BYGJ_HG11719` | `( YP_BYGJ_SZYJ*YP_RES_SIZE+3 )` | 《砼规》GB50010-2010 第11.7.19条 |
| 砌体信息 | `YP_QTGDMETHOD` | `YP_QTGDMETHOD_FINITE` | `( YP_QTGDMETHOD*YP_RES_SIZE+1 )` | 有限元方法计算 |
| 砌体信息 | `YP_QTGDMETHOD` | `YP_QTGDMETHOD_NOMAL` | `( YP_QTGDMETHOD*YP_RES_SIZE+2 )` | 常规方法计算 |
| 时程分析信息 | `YP_SCDAMPRMETHOD` | `YP_SCDAMPRSAME` | `( YP_SCDAMPRMETHOD*YP_RES_SIZE+1 )` | 所有振型同一阻尼 |
| 时程分析信息 | `YP_SCDAMPRMETHOD` | `YP_SCDAMPRCOMB` | `( YP_SCDAMPRMETHOD*YP_RES_SIZE+2 )` | Rayleigh阻尼组合模态阻尼 |
| 时程分析信息 | `YP_SCDZYX` | `YP_SCDZYX_DY` | `( YP_SCDZYX*YP_RES_SIZE+1 )` | 多遇 |
| 时程分析信息 | `YP_SCDZYX` | `YP_SCDZYX_HY` | `( YP_SCDZYX*YP_RES_SIZE+2 )` | 罕遇 |
| 时程分析信息 | `YP_SCDZYX` | `YP_SCDZYX_SF` | `( YP_SCDZYX*YP_RES_SIZE+3 )` | 设防 内部使用，  不属于YP_SCDZYX参数的值，交互设置不显示 |
| 时程分析信息 | `YP_SCDZYX` | `YP_SCDZYX_JHY` | `( YP_SCDZYX*YP_RES_SIZE+4 )` | 极罕遇 |
| 北京地标 | `YP_StandardBJ_RatingMethod` | `YP_StandardBJ_RatingMethod_ComprehensiveSeis` | `( YP_StandardBJ_RatingMethod*YP_RES_SIZE+1 )` | 综合抗震能力 |
| 北京地标 | `YP_StandardBJ_RatingMethod` | `YP_StandardBJ_RatingMethod_LateralResistance` | `( YP_StandardBJ_RatingMethod*YP_RES_SIZE+2 )` | 抗侧力构件 |
| 隔震减震 | `YP_ISOLATDESIGNTYPE` | `YP_ISOLATDESIGNTYPE_DIVISION` | `( YP_ISOLATDESIGNTYPE*YP_RES_SIZE+1 )` | 分部设计法  Divisional design method |
| 隔震减震 | `YP_ISOLATDESIGNTYPE` | `YP_ISOLATDESIGNTYPE_DIRECT` | `( YP_ISOLATDESIGNTYPE*YP_RES_SIZE+2 )` | 直接设计法 Direct design method |

### 4.4 取值不是 `(<参数ID>*YP_RES_SIZE+n)` 的取值宏

| 所在小节 | 宏名 | 原文取值 | 原文注释 |
|---|---|---|---|
| 计算总体信息 | `YPV_XJKXB_JCL` | `(YP_SEISTYPE*YP_XJKXB+1)` | 交叉梁法 |
| 计算总体信息 | `YPV_XJKXB_YXY` | `(YP_SEISTYPE*YP_XJKXB+2)` | 有限元法 |
| 地震信息 | `YPV_DAMPMATID_STEEL` | `5` | 钢  阻尼比数组中用的材料ID，尽量与梁工的一致 ==IDM_Steel |
| 地震信息 | `YPV_DAMPMATID_CONCRETE` | `6` | 砼  阻尼比数组中用的材料ID，尽量与梁工的一致 ==IDM_Concrete |
| 地震信息 | `YPV_DAMPMATID_GH` | `56` | 型钢砼  阻尼比数组中用的材料ID |
| 设计信息 | `YPV_BYGJ_LXAZ_NONE` | `0` | 全不生成 |
| 设计信息 | `YPV_BYGJ_LXAZ_CREATE` | `1` | 全都生成 |
| 设计信息 | `YPV_BYGJ_LXAZ_NOTHINGE` | `2` | 铰接梁不生成 |

### 4.5 十六进制 / 位运算宏（原文逐字）

```c
#define YP_SCWAVEPARA_ID	0x0FFFFFFF	//用于取地震波参数中的ID (例 id = para & YP_SCWAVEPARA_ID 也可以用下面的宏定义如：id = YPSC_GETWAVEPARA_ID(para);)
#define YP_SCWAVEPARA_PRIM	0x20000000	//用于取地震波参数中的是否计算主方向 (例 bPrim = para & YP_SCWAVEPARA_PRIM 也可以用下面的宏定义如：bPrim = YPSC_GETWAVEPARA_PRIM(para);)
#define YP_SCWAVEPARA_SEC	0x10000000	//用于取地震波参数中的是否计算次方向 (例 bSec = para & YP_SCWAVEPARA_SEC也可以用下面的宏定义如：bSec = YPSC_GETWAVEPARA_SEC(para);)
#define YP_SCWAVEPARA_ID	0x0FFFFFFF	//用于取地震波参数中的ID (例 id = para & YP_SCWAVEPARA_ID)
#define YP_PARABOUND_FORCE		0x01	// 强制限制，不允许超出限制
#define YP_PARABOUND_WARNING	0x02	// 不强制，只警示
#define YP_PARABOUND_NOTEDIT	0x10	// 非编辑框限制
```

---

## 五、统计

- `YP_*` / `YPE_*` / `YPU_*` **参数ID宏**（去重后）：**1034** 个
  - 即参数号本身。除主库 `YP_*` 外，还含欧标 `YPE_*`、美标 `YPU_*` / `YPUS_*` 系列
- 形如 `(<参数ID>*YP_RES_SIZE+n)` 的**取值宏**：去重后 **499** 个宏名，出现 **499** 次
- 其余 `#define`（纯数字取值宏、强度值别名、位运算宏、函数式宏等）：**36** 行
- 原文分节：**44** 个；原文总行数：**1855** 行；`YP_RES_SIZE = 100`

> 本文件为速查索引；**权威原文请始终对照 `前处理计算参数宏定义.md`**（同目录，逐字副本）。
