# yjk-dev-refs —— YJK（盈建科）二次开发官方资料离线参考集

> **这是什么**：把盈建科官方发布的**二次开发说明文档**与**官方示例源码**归拢成一套
> 可离线查阅、可被技能引用的参考集。
>
> **不是** SDK 安装包。这里**只有文字与源码**，没有任何动态库、安装包或示例数据文件。
>
> 所有文档内容均为 **YJK（盈建科）官方二次开发文档**，由 gitee 上的官方开源组织
> `yjk-opensource` 公开发布，此处**原样转载用于离线参考**。宏定义、接口签名、
> 中文注释一律逐字保留，未做改写或“纠错”。

---

## 一、目录结构

```
yjk-dev-refs/
├── README.md                      ← 本文件：索引 + 来源 + 许可 + 技能映射
├── 01-总览与运行方式/              ← 三份“怎么跑起来”的整理文档
├── 02-Python-API案例/              ← 官方 .py 案例源码（32 个 .py）
├── 03-CSharp案例/                  ← 官方 C# 案例源码（26 个 .cs + 说明 .txt）
├── 04-接口说明/                    ← 各类接口文档（C# / 6.x / 8.x 三种变体并存）
├── 05-数据文件说明/                ← ydb / 数据库 / 施工图数据表结构说明
└── 06-总信息参数ID表/              ← ⭐ 前处理计算参数宏定义（权威原文）+ 速查表
```

---

## 二、来源仓库一览

三个 gitee 官方仓库，均属 `yjk-opensource` 组织：

| 仓库 | URL | 定位 | 版本坐标 |
|---|---|---|---|
| `csharp-yjks` | <https://gitee.com/yjk-opensource/csharp-yjks> | C# 二次开发 SDK（YJKS C# API） | 覆盖 5.1 → 8.1，文档最全 |
| `py-yjks` | <https://gitee.com/yjk-opensource/py-yjks> | 旧版 Python API（`pyYJKSModel` / `pyYJKSUI` / … 多个 `.pyd`） | **YJK 6.1 + Python 3.8** |
| `yjkapi_-python` | <https://gitee.com/yjk-opensource/yjkapi_-python> | 新版 Python API（统一入口 `from YJKAPI import *`） | **YJK 8.x + Python 3.10** |

另外，`05-数据文件说明` 中 **14 份**文档来自官方文档包
**`数据库文件说明.rar`**（`csharp-yjks\说明文档\` 与 `py-yjks\说明文档及案例\说明文档\`
各存一份，内容相同），该 rar 内的 `.docx` / `.doc` 已转为 Markdown 收入本包；
另有 1 份（`基础计算结果数据库(Jccad_Result_New.ydb)说明.md`）来自
`csharp-yjks\说明文档\` 目录，不在 rar 内。

---

## 三、⭐ 版本分野：6.1 与 8.x 不是同一套 API

这是用本参考集时**最容易踩的坑**，务必先分清：

| | **py-yjks（旧）** | **yjkapi_-python（新）** |
|---|---|---|
| 目标 YJK | **6.1** | **8.x**（README 正文写作 8.0，SDK 包实际是 `8.1.rar`） |
| Python | **3.8**（原文明确“推荐 3.8.4”，否则会闪退） | **3.10**（用**软件安装目录自带**的解释器） |
| 导入方式 | 若干独立 `.pyd` 模块 | 单一 `from YJKAPI import *` |
| SDK 获取 | 仓库内“替换文件”复制到 YJK 安装目录 | **API 已集成进软件安装环境，不再单独发包** |
| 接口文档 | `04-接口说明\*-6x.md` | `04-接口说明\*-8x.md` |
| 案例 | `02-Python-API案例\py-yjks官方示例\`、`YJKSControl示例\` | `02-Python-API案例\不依赖YJK案例\`、`依赖YJK案例\` |

`yjkapi_-python` 的仓库 README 原文（要点）：

> ❕ 为了方便与主软件的兼容和支持Agent智能建模自定义工具函数，**YJKAPI将被集成在软件安装环境中，不再提供单独的安装包。**
>
> 1. **配置python环境**：安装8.0版本软件 → 将SDK目录下的 `8.0.rar` 压缩包解压并复制到安装目录下，替换文件 →
>    打开 vscode，选择**安装目录下的 python3.10 解释器**，环境中已经安装好了 YJKAPI。
> 2. **运行YJKAPI案例**：不依赖软件运行时的脚本 `from YJKAPI import *`；依赖软件运行时的脚本需要打开软件，
>    通过 `yjks_pyload` 命令执行。

> ⚠️ README 里写的是 `SDK\8.0.rar`，**仓库里实际的文件名是 `yjkapi_-python\SDK\8.1.rar`（约 23.8 MB）**。
> 该压缩包**未被复制到本包**（见第五节）。操作步骤不变：**解压到 YJK 安装目录 → 用安装目录自带的
> Python 解释器 → `from YJKAPI import *`**。

两套 API 的**参数ID 编码体系（`YP_*` / `YPV_*`）与命令体系是一致的**，所以
`06-总信息参数ID表\参数ID速查.md` 对两套都适用。
详细的运行步骤见 `01-总览与运行方式\Python-API-运行方式.md`。

---

## 四、文档来源清单（本包文件 ← 原文 ← 仓库）

### 4.1 `06-总信息参数ID表\`（最常用）

| 本包文件 | 原文文件 | 来源仓库 |
|---|---|---|
| `前处理计算参数宏定义.md` | `说明文档\前处理计算参数宏定义.docx`（75892 B） | `csharp-yjks` |
| `参数ID速查.md` | **本包新编**，内容逐字转录自上表文件 | — |

`前处理计算参数宏定义.md`（145 KB / 1855 行）是**前处理计算参数（总信息）的权威 `#define` 表**：
1034 个参数ID宏 + 499 个取值宏，含 44 个原文分节。
`参数ID速查.md` 是它的**派生速查索引**（含编码规则、高频 21 项、按原文分节的全量表格、
原文笔误清单），两者请配套使用。

### 4.2 `04-接口说明\`

| 本包文件 | 原文文件 | 来源仓库 | 大小 |
|---|---|---|---|
| `建模接口说明-8x.md` | `案例\二次开发\说明文档\建模接口说明.docx` | `yjkapi_-python` | 50 KB |
| `建模接口说明-6x.md` | `说明文档及案例\说明文档\建模接口说明.docx` | `py-yjks` | 24 KB |
| `建模接口说明-CSharp.md` | `说明文档\建模接口说明.docx` | `csharp-yjks` | 58 KB |
| `建模模块宏定义.md` | `说明文档及案例\说明文档\建模模块宏定义.docx` | `py-yjks` | 7.5 KB |
| `前处理接口说明-8x.md` | `案例\二次开发\说明文档\前处理接口说明.docx` | `yjkapi_-python` | 67 KB |
| `前处理接口说明-6x.md` | `说明文档及案例\说明文档\前处理接口说明.docx`（1.9 KB，以文字为主） | `py-yjks` | 1.9 KB |
| `前处理接口说明-CSharp.md` | `说明文档\前处理接口说明.docx` | `csharp-yjks` | 69 KB |
| `设计结果接口说明-新.md` | `说明文档\设计结果接口说明_新.docx` | `csharp-yjks` | 249 KB |
| `设计结果接口说明-CSharp.md` | `说明文档\设计结果接口说明.docx` | `csharp-yjks` | 190 KB |
| `设计结果接口说明-8x.md` | `案例\二次开发\说明文档\设计结果接口说明.docx` | `yjkapi_-python` | 235 KB |
| `设计结果接口说明-6x.md` | `说明文档及案例\说明文档\设计结果接口说明.docx` | `py-yjks` | 166 KB |
| `设计结果宏定义.md` | `说明文档\设计结果宏定义.docx` | `csharp-yjks`（与 `py-yjks` 同名文件 **MD5 完全相同**，只收一份） | 52 KB |
| `特殊构件定义说明.md` | `说明文档\特殊构件定义说明.docx` | `csharp-yjks` | 24 KB |
| `特殊构件定义说明-6x.md` | `说明文档及案例\说明文档\特殊构件定义说明.docx`（含 Python 签名，与上条**有实质差异**） | `py-yjks` | 24 KB |
| `有限元接口说明.md` | `说明文档\有限元接口说明.docx` | `csharp-yjks` | 8 KB |
| `基础建模接口说明.md` | `说明文档\基础建模接口说明.docx` | `csharp-yjks` | 21 KB |
| `基础设计结果接口说明.md` | `说明文档\基础设计结果接口说明.docx` | `csharp-yjks` | 4.2 KB |
| `命令说明文档.md` | `说明文档\YJKSControl\命令说明文档.docx` | `csharp-yjks` | 6.4 KB |
| `UI接口及命令接口说明.md` | `说明文档\UI接口及命令接口说明.docx` | `csharp-yjks` | 2.2 KB |
| `UI接口及命令接口说明-6x.md` | `说明文档及案例\说明文档\UI接口及命令接口说明.docx` | `py-yjks` | **519 B（原文以截图／短签名为主）** |
| `其他接口说明.md` | 三份小文档的**逐字合并**：`说明文档\智能辅助设计相关接口说明.docx`、`转图相关接口说明.docx`、`Dtl相关接口说明.docx` | `csharp-yjks` | 3.4 KB |
| `DsnModel数据说明.md` | `说明文档\DsnModel数据说明.docx` | `csharp-yjks` | **302 KB（体量过大，单独成文；`其他接口说明.md` 内有指针）** |

> **为什么三个变体都留着**：C# / 6.x / 8.x 的 `建模接口说明`、`前处理接口说明`、
> `设计结果接口说明` **确实不一样**（C# 用 `ClrYJKS*` / `Hi_*` 类声明，Python 用
> `def xxx(...) -> type` 签名，6.x 与 8.x 的模块划分与函数集也不同），
> 因此不做去重。**`设计结果宏定义` 是唯一完全相同的文件**（C# 与 py 两份 MD5 一致），只收一份。

### 4.3 `05-数据文件说明\`

来自官方文档包 `数据库文件说明.rar`（`.docx` 用 pandoc 转 Markdown，`.doc` 先经
Word 转 `.docx` 再转 Markdown；**图片以 `【原文此处为图片／截图】` 标记代替，未收录二进制**）。
`.rar` 内的重复文件（如 `基础\` 与 `施工图\` 各存一份 `基础施工图数据库(JCPlan.ydb)说明.docx`）
按**文件名去重**，只保留一份。**14 份来自 rar，1 份来自 `csharp-yjks\说明文档\`**，共 15 份。

| 本包文件（= 原文 basename） | 原文 | 说明 |
|---|---|---|
| `dtlModel.md` | `dtlModel.docx` | dtlModel 数据表结构（本组最大，115 KB） |
| `dtlModel补.md` | `dtlModel补.docx` | dtlModel 补充 |
| `dtlCalc说明文档.md` | `dtlCalc说明文档.doc` | 施工图计算数据（旧 `.doc`，已转换） |
| `前处理特殊构件定义属性含义.md` | `前处理特殊构件定义属性含义.docx` | 特殊构件属性取值含义 |
| `楼板钢筋文件记录说明.md` | `楼板钢筋文件记录说明.docx` | 楼板钢筋记录 |
| `钢结构施工图数据.md` | `钢结构施工图数据.docx` | 钢结构施工图数据表（308 KB） |
| `基础建模数据库(jccad_0.ydb)说明.md` | 同名 `.docx` | 基础建模库（ydb 版） |
| `基础建模数据库(jccad_0.mdb)说明.md` | 同名 `.docx` | 基础建模库（mdb 版） |
| `基础计算分析数据库(jccad.ydb)说明.md` | 同名 `.docx` | 基础计算分析库 |
| `基础施工图数据库(JCPlan.ydb)说明.md` | 同名 `.docx` | 基础施工图库 |
| `板施工图数据库dtlSlabPub说明.md` | `板施工图数据库dtlSlabPub说明.doc` | 板施工图库（旧 `.doc`） |
| `砼墙施工图数据库dtlRcWall说明.md` | `砼墙施工图数据库dtlRcWall说明.doc` | 砼墙施工图库（旧 `.doc`） |
| `砼柱施工图数据库dtlRcCol说明.md` | `砼柱施工图数据库dtlRcCol说明.doc` | 砼柱施工图库（旧 `.doc`） |
| `砼梁施工图数据库dtlRcBeam说明.md` | `砼梁施工图数据库dtlRcBeam说明.doc` | 砼梁施工图库（旧 `.doc`） |
| `基础计算结果数据库(Jccad_Result_New.ydb)说明.md` | `说明文档\基础计算结果数据库(Jccad_Result_New.ydb)说明.docx` | 非 rar 内文件；来自 `csharp-yjks` 说明文档目录 |

### 4.4 `01-总览与运行方式\`

| 本包文件 | 内容来源 |
|---|---|
| `CSharp-SDK运行方式.md` | **本包整理**，合并 `csharp-yjks\README.md`、`说明文档\YJKSControl\运行说明.docx`、`说明文档\CSharpYJKS运行说明.docx`，引用处逐字 |
| `Python-API-运行方式.md` | **本包整理**，合并 `py-yjks\README.md`、`说明文档\Python二次开发Api运行说明.docx`、`YJKSControl\说明文档\运行说明.docx`、`yjkapi_-python\README.md`，引用处逐字 |
| `案例总览.md` | **本包整理**，案例说明取自各案例源码头注释、`py-yjks\……\example\案例说明.docx`、`csharp-yjks\说明文档\案例说明` 原文 |
| `命令执行修改说明.txt` | 逐字复制自 `py-yjks\说明文档及案例\命令执行修改说明.txt`（114 B） |

### 4.5 `02-Python-API案例\`（32 个 `.py`）

| 本包目录 | 来源 |
|---|---|
| `不依赖YJK案例\案例1…案例18\` | `yjkapi_-python\案例\二次开发\不依赖YJK案例\`（**只复制 `.py`**，`.ydb` 数据文件未复制） |
| `依赖YJK案例\post.py` | `yjkapi_-python\案例\二次开发\依赖YJK案例\post.py` |
| `py-yjks官方示例\` | `py-yjks\说明文档及案例\example\`（9 个 `.py`，含子目录 `ydb_modify\`） |
| `YJKSControl示例\` | `py-yjks\YJKSControl\example\`（`test1.py` / `test2.py` / `test3.py`） |

每个案例一行说明见 `01-总览与运行方式\案例总览.md`。

### 4.6 `03-CSharp案例\`

| 本包目录 | 来源 |
|---|---|
| `不依赖YJK案例\ConsoleApp1…ConsoleApp19\` | `csharp-yjks\不依赖YJK案例\`（`.cs` 源码 + 说明 `.txt`；`ConsoleApp15` 含 `YJK项目\test01/test02` 的小 `.txt`） |
| `依赖YJK案例\ConsoleApp5 / ConsoleApp8 / ConsoleApp9 / ConsoleApp14\` | `csharp-yjks\依赖YJK案例\`（插件形态案例，含 `操作说明.txt`、`dll\dtlPlugList.txt`、`dll\example.txt`） |
| `依赖YJK案例\CSharp后处理\` | `csharp-yjks\依赖YJK案例\CSharp后处理\`（含 258 KB 的 `MiddleTrans.cs`） |
| `依赖YJK案例\自定义按钮演示\补充说明.txt` | 同名原文 |
| `依赖YJK案例\YJK替换文件\8.1YJK\readme(我不是替换文件).txt` | 同名原文 |

---

## 五、**未复制**的二进制（有意为之）

以下内容**故意没有复制进本参考集**，需要时请从原仓库或 YJK 安装目录获取：

| 未复制内容 | 原始位置 | 大小 | 为什么排除 |
|---|---|---|---|
| **新版 Python SDK 包** | `yjkapi_-python\SDK\8.1.rar` | **≈ 23.8 MB** | 官方 API 二进制包，属安装物，非文档 |
| 旧版 Python 替换文件 | `py-yjks\6.1YJK&3.8py_V1.0\替换文件\`、`py-yjks\YJKSControl\example\*.pyd` | 数 MB | `.dll` / `.pyd` 二进制 |
| 数据库说明压缩包 | `csharp-yjks\说明文档\数据库文件说明.rar`、`py-yjks\说明文档及案例\说明文档\数据库文件说明.rar` | 1.07 MB ×2 | **内容已解包为 `05-数据文件说明\` 的 Markdown**，故不再收 rar |
| 示例模型数据 | 各案例目录下的 `*.ydb`、`*.yjk`（如 `123.ydb`、`pymodel.ydb`、`Jccad_0.ydb`） | 数百 KB ～ 数 MB | 二进制模型数据 |
| 依赖库 | `py-yjks\说明文档及案例\example\ydb_modify\依赖项\*.dll`（含 10 MB 的 `BCGCBPRO2410u120.dll`） | > 30 MB | 第三方 / 官方二进制 |
| 演示视频与截图 | `说明文档\YJKSControl\yjkscontrol.mp4`（21 MB）、各仓库的 `*.png`、案例视频 `.wmv` | — | 二进制媒体 |
| C# DLL | `csharp-yjks\不依赖YJK案例\dll\`、`依赖YJK案例\*\dll\` | — | 二进制程序集 |
| 原始 Office 文档 | 各 `*.docx` / `*.doc` / `*.xlsx` / `*.CUI` | — | 已转成 Markdown 正文收纳；`.xlsx` / `.CUI` 未转换（见第八节第 2 条） |
| 样板文件 | `Properties\AssemblyInfo.cs` × 26 | 各 1.3 KB | 纯 Visual Studio 样板，无技术内容 |
| 空文件 | `依赖YJK案例\YJK替换文件\8.1YJK\apiPlugList.txt` | 0 B | 空 |

---

## 六、许可与再分发说明

| 仓库 | 仓库内 LICENSE | 说明 |
|---|---|---|
| `csharp-yjks` | **木兰宽松许可证，第 2 版**（Mulan PSL v2，<http://license.coscl.org.cn/MulanPSL2>） | 允许复制、使用、修改、分发 |
| `py-yjks` | **Apache License 2.0** | 允许复制、使用、修改、分发 |
| `yjkapi_-python` | **仓库内没有 LICENSE 文件** | 该仓库仅有 `README.md` / `.gitignore` / `images` / `SDK` / `案例` |

因此：

- `csharp-yjks` 与 `py-yjks` 的材料按其各自开源许可转载，**保留原版权与许可**。
- `yjkapi_-python` 的材料（`04-接口说明\*-8x.md`、`02-Python-API案例\不依赖YJK案例\`、
  `依赖YJK案例\post.py`）**未见随附许可声明**，此处仅作为**离线技术参考**收录，
  版权归**北京盈建科软件股份有限公司**所有；若需对外分发请自行确认授权。
- 全部材料均为 **YJK 官方二次开发文档（YJK's official secondary-development documentation）**，
  在此**转载以作离线参考**，本参考集未对其主张任何权利、也未做实质性修改。
- 名称与商标：YJK、盈建科 为北京盈建科软件股份有限公司的商标；本文档仅为技术引用。

---

## 七、本技能包哪里会用到

本参考集服务于 `yjk-skills-package` 下的 5 个技能，映射如下：

| 技能 | 主要参考文档 | 用来解决什么 |
|---|---|---|
| **`yjk-auto-drive`**（底座：驱动 / 命令 / 前处理） | `01-总览与运行方式\CSharp-SDK运行方式.md`、`Python-API-运行方式.md`<br>`04-接口说明\命令说明文档.md`、`UI接口及命令接口说明.md`、`UI接口及命令接口说明-6x.md`<br>`02-Python-API案例\YJKSControl示例\test1.py`（完整命令流）<br>`06-总信息参数ID表\参数ID速查.md`（`scripts\projpara.py` 的参数ID依据） | 启动/接管 YJK 进程、下发命令流、设前处理参数、判断哪套 API 对应哪个 YJK 版本 |
| **`column-section-opt`**（柱截面 + 混凝土等级优选） | `04-接口说明\建模接口说明-CSharp.md` / `-6x.md` / `-8x.md`（柱截面定义、截面修改）<br>`06-总信息参数ID表\前处理计算参数宏定义.md` + `参数ID速查.md`（**改变结构体系/抗震等级/材料等总信息以重算**）<br>`04-接口说明\设计结果接口说明-新.md`（`.wpj` / 设计结果解析）<br>`05-数据文件说明\dtlModel.md`（模型库表结构，配合 `scripts\ydb_serialize.py`、`scripts\verify_results.py`） | 建/改模型→重算→读结果→选型闭环；总信息参数按 `ID×100+序号` 设置 |
| **`floor-system-comparison`**（楼盖次梁布置经济比选） | `04-接口说明\建模接口说明-8x.md` / `-6x.md`（次梁、板、房间与荷载布置）<br>`05-数据文件说明\基础建模数据库(jccad_0.ydb)说明.md` 等 ydb 说明（ydb 序列化口径）<br>`02-Python-API案例\不依赖YJK案例\案例1_框架结构\kj.py`（板/梁布置骨架，`scripts\make_ydb.py`）<br>`06-总信息参数ID表\参数ID速查.md`（试算参数） | 批量生成不同楼盖方案的 ydb、跑通算量对比 |
| **`yjk-draw-takeoff`**（出施工图 + 工程量） | `04-接口说明\命令说明文档.md`（命令名与参数表）<br>`02-Python-API案例\YJKSControl示例\test2.py`（**楼板/梁/柱/墙钢筋统计命令流**）、`test3.py`（几何绘制命令）<br>`04-接口说明\设计结果接口说明-新.md`、`设计结果宏定义.md`<br>`05-数据文件说明\砼梁施工图数据库dtlRcBeam说明.md`、`砼柱施工图数据库dtlRcCol说明.md`、`砼墙施工图数据库dtlRcWall说明.md`、`板施工图数据库dtlSlabPub说明.md`、`dtlCalc说明文档.md`、`楼板钢筋文件记录说明.md`、`钢结构施工图数据.md`、`基础施工图数据库(JCPlan.ydb)说明.md` | 出图、钢筋/混凝土统计、直接读施工图库校验算量 |
| **`column-scheme-comparison`**（钢筋混凝土柱 vs 钢管混凝土柱比选，**不驱动 YJK**） | `04-接口说明\设计结果接口说明-新.md` / `-CSharp.md`（柱设计结果字段、轴力/配筋读取）<br>`04-接口说明\设计结果宏定义.md`（结果枚举取值）<br>`04-接口说明\特殊构件定义说明.md`（构件属性口径）<br>`05-数据文件说明\dtlModel.md`（模型库柱截面与材料） | 纯解析 `设计结果\wpj*.out` + 模型库，做 GB 50936 承载力复核与计价 |

---

## 八、已知限制与未完成项

1. **图片未收录**：所有文档中的插图、截图均以 `【原文此处为图片／截图】` 标记代替
   （部分原文本身就是“以截图为主”的小文档，见下表）。需要图请查原仓库。
2. **`.xlsx` 与 `.CUI` 未转换**：`数据库文件说明.rar` 内还有
   `基础\JC_计算参数.xlsx`、`基础\JC_选择规范.xlsx`、`基础\JC_高级参数.xlsx`、
   `水池\POOL_参数说明.xlsx`（基础／水池模块的参数表）以及
   `基础\基础设计-地质资料.CUI`、`基础设计-地质资料转图.CUI`。
   这些是电子表格与界面配置文件，**未转为 Markdown**，也未复制二进制。
   如需要，请从原 rar 中取。
3. **“原文以截图为主”的小文档清单**（均已保留原文，只是内容短）：

   | 文档 | 大小 | 本包位置 |
   |---|---|---|
   | `py-yjks\Python二次开发Api运行说明.md` | 633 B | 合并进 `01-总览与运行方式\Python-API-运行方式.md` |
   | `py-yjks\UI接口及命令接口说明.md` | 519 B | `04-接口说明\UI接口及命令接口说明-6x.md` |
   | `py-yjks\前处理接口说明.md` | 1.9 KB | `04-接口说明\前处理接口说明-6x.md` |
   | `py-yjks\案例说明.md` | 1.3 KB | 合并进 `01-总览与运行方式\案例总览.md` |
   | `csharp-yjks\CSharpYJKS运行说明.md` | 719 B | 合并进 `01-总览与运行方式\CSharp-SDK运行方式.md` |
   | `csharp-yjks\Dtl相关接口说明.md` | 650 B | 合并进 `04-接口说明\其他接口说明.md` |
   | `csharp-yjks\转图相关接口说明.md` | 781 B | 合并进 `04-接口说明\其他接口说明.md` |
   | `csharp-yjks\智能辅助设计相关接口说明.md` | 870 B | 合并进 `04-接口说明\其他接口说明.md` |

4. **`其他接口说明.md` 不内联 DsnModel**：302 KB 的 `DsnModel数据说明.md` 单独成文，
   `其他接口说明.md` 内以链接指向它。
5. **`06-总信息参数ID表\参数ID速查.md` 是派生文档**：其中的“取值表达式 / 注释”逐字来自
   `前处理计算参数宏定义.md`，但“展开后的整数值”与“原文笔误清单”是本包的计算结果。
   **有疑问时以同目录的宏定义原文为准。**
6. **`.rar` 内重复文件已按 basename 去重**：例如
   `基础施工图数据库(JCPlan.ydb)说明.docx` 与 `施工图\基础施工图数据库(JCPlan.ydb)说明.docx`、
   两份 `楼板钢筋文件记录说明.docx`，内容相同，各只保留一份。
7. **`03-CSharp案例` 不含工程文件**：`.csproj` / `.sln` / `.vs` / `dll` / `Properties\AssemblyInfo.cs`
   未复制，源码需自行建工程并引用 `CsToYjk` / `APIData` / `DataFuncApplication`。

---

## 九、怎么开始用

- **要设总信息参数（改结构体系、抗震等级、设防烈度、场地类别…）** →
  先看 `06-总信息参数ID表\参数ID速查.md` 第一节的编码规则
  （**参数值 = 参数ID × 100 + 枚举序号**），再查第二／第三节的表，
  最后对照 `06-总信息参数ID表\前处理计算参数宏定义.md` 与
  `02-Python-API案例\不依赖YJK案例\案例14_前处理计算参数设置\kj.py`。
- **要跑命令流（建模/预处理/计算/出图/算量）** →
  `04-接口说明\命令说明文档.md` 查命令名，`02-Python-API案例\YJKSControl示例\test1.py`
  看完整命令流，`test2.py` 看钢筋统计命令。
- **要读设计结果** → `04-接口说明\设计结果接口说明-新.md` + `设计结果宏定义.md`。
- **要直接读数据库文件** → `05-数据文件说明\` 找对应的 `.ydb` / `dtl*` 说明。
- **不知道案例是干什么的** → `01-总览与运行方式\案例总览.md`（一个案例一行）。
