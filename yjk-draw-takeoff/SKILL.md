---
name: yjk-draw-takeoff
description: 承接 yjk-auto-drive 的"算完之后"环节：用官方 IPC 通道让 YJK 自动出梁/板/柱/墙施工图（DWG），自动统计工程量（混凝土体积、钢筋用量），最后汇总成一份可交付的 Excel。只做"出图 + 出量"，不做选型与造价（比选见 column-section-opt / column-scheme-comparison / floor-system-comparison）。当用户要求"自动生成施工图""施工图自动出图""梁板柱墙算量""构件工程量统计""钢筋用量统计""混凝土工程量""YJK 出量""算完自动出图和统计""drawings and quantity takeoff"时使用。
agent_created: true
---

# YJK 施工图 + 工程量统计（自动出图 / 自动算量）

`yjk-auto-drive` 负责"把模型算出来"（启动 → 导入 → 预处理 → 计算 → 设计结果）。
本技能负责它之后的全部工作：

```
设计结果/  → 【混凝土工程量】 → 【施工图 DWG】 → 【钢筋工程量】 → 留档 → 汇总 Excel
```

全部命令走同一个 IPC 通道，**全程零人工点击**。

## 与相邻技能的分工

| 技能 | 职责 |
|---|---|
| `yjk-auto-drive` | 纯通路：启动 / 建工程 / 导入 / 预处理 / 计算 / 读设计结果；本技能依赖它 |
| **`yjk-draw-takeoff`（本技能）** | 算完之后：施工图出图 + 混凝土/钢筋工程量统计 + 汇总报告 |
| `column-section-opt` | 柱截面 + 等级优选 |
| `column-scheme-comparison` | 柱截面形式（RC / CFST）比选 |
| `floor-system-comparison` | 楼盖（次梁布置）比选 |

> 本技能是通用出图出量工具，不关心模型是为哪个比选生成的，任何 `.ydb` 都能用。

## 两条命令就够

```bash
# ① 算完 → 出图 → 出量（内部会自己走一遍 导入+预处理+计算，也支持只做后半段）
python <本技能>/scripts/draw_quant.py --ydb 模型.ydb --proj P1

# ② 汇总成可交付 Excel（6 页）
python <本技能>/scripts/summary_xlsx.py results/P1 --name P1
```

`draw_quant.py` 默认把工作目录放在当前目录下：`./YJK_run_dq/<proj>`、留档 `./results/<proj>`。
用 `--root` / `--workdir` / `--out` 改；`--no-conc` / `--no-draw` / `--no-rebar` 可跳过某一段。

两条命令的退出码：

* `draw_quant.py`：`0` 成功 / `1` 失败（导入校验不通过、计算无结果、建工程失败）/
  `2` 找不到 `yjk-auto-drive`。
* `summary_xlsx.py`：`0` 自检无硬问题 / `2` 有硬问题 —— 自检页出现 `★` 即硬问题：缺
  `工程量统计.ini`、一张钢筋用量表都没有、DWG 为 0 字节或不是 DWG、取不到面积或层数导致
  单方指标算不出。明知留档不全仍要返回 0：加 `--allow-incomplete`（问题照旧打印并写进第 6 页）。
  `--help` 始终 rc=0。`--area` 是**每层**楼面面积，不是全楼面积。
* `gcl_ini.py`：`0` 正常 / `1` 文件打不开 / `2` 解析出数据问题（缺 `Cap` 行、字段数≠列数、
  非数值、`Item-Sum` 与明细之和不符等）。

## 执行链

```python
CONC_CHAIN  = [("IDModule_Layer",  "yjkconcreteStat_statCom", "", 300)]
SLAB_CHAIN  = [("IDDTL_DETAIL_SLAB",   "StdSlab_RedrawNceng",  "", 600),
               (None,                  "StdSlab_AUTOCAL",      "", 600),
               (None,                  "StdSlab_batgenstl",    "", 900),
               (None,                  "stdslab_AutoStatstl",  "", 600)]   # ★ 关键
BEAM_CHAIN  = [("IDDTL_DETAIL_BEAM",   "DtlRC_RegenReinsUpdateBeamPlan", "", 900)]
COL_CHAIN   = [("IDDTL_DETAIL_COLUMN", "DtlRC_DrawNewColPlan",  "", 900)]
WALL_CHAIN  = [("IDDTL_DETAIL_WALL",   "DtlRC_WallPlanRegenNew", "", 900)]
REBAR_CHAIN = [("IDQUANTITYLIST_DETAIL", "DtlRC_SSSE",  "", 300),        # 板
               (None, "DtlRC_StatBuildingBeamSteelSpecExcel", "", 300),  # 梁
               (None, "DtlRC_SSCE", "", 300),                            # 柱
               (None, "DtlRC_SSWE", "", 300),                            # 墙
               (None, "dtlrc_ColSumGJ", "", 300)]                        # 柱 txt 补充
```

## 顺序约束（必读）

混凝土统计 → 施工图 → 钢筋统计，三者顺序不能换。

- `yjkconcreteStat_statCom` 归属**建模模块**（`HelpRef = 楼层组装\18工程量统计`）。切到
  `IDModule_Layer` 会冲掉施工图上下文：它若排在出图链之后，后续所有 `DtlRC_*` 钢筋统计命令
  会退化成 `OK(0.0s)` 且不产出任何文件，但不报错。症状是"命令全部成功，Excel 一个没有"。

## 导入校验闸门（防"静默导入空模型"）

`yjk_importydb` 必须收到**绝对路径**：

```python
ydb = impcheck.abs_ydb("models/S0.ydb")   # ★ 一律先转绝对路径
cli.run("yjk_importydb", ydb, 600)
cli.run("yjk_save", "", 300)              # ★ .ymd 是 save 才写出的
impcheck.check(ydb, os.path.join(wd, "S0.ymd"))
```

* 传相对路径时 YJK 按它自己的工作目录解析 → 弹「文件不存在」→ 若被放行，导入的是空模型，
  命令照样返回 `OK(1.1s)`。直到计算阶段才以 `模型中没有单元数据`（`fea.dat-ERR.txt`）暴露，
  此时现场已被污染，难以回溯。
* 判据：逐表核对几何表行数（与源模型逐表一致即为通过）：

  | table | 作用 | 通过判据 |
  |---|---|---|
  | `tblJoint` | 节点 | 与源模型一致 |
  | `tblBeamSeg` | 梁段 | 与源模型一致 |
  | `tblColSeg` | 柱段 | 与源模型一致 |
  | `tblSlab` | 板块 | 与源模型一致 |
  | `tblFloor` | 自然层 | 与源模型一致 |
  | `tblLoadSeg` | 梁上荷载 | **逐层**都有荷载（不按总条数判） |

  导入失败（空模型）时这些表全部为 0，所以「是否与源一致」足以判定。
  `tblLoadSeg` 例外：导入会把"每层一份的荷载定义"并成一份、重编号标准层、把条数
  重排/展开（实测源 4576 条 / 每层 104 → 工程 10488 条 / 逐层 104~360，一条没丢），
  要求总条数相等会把正常模型判成"没进来"；只有"源有荷载、工程一条都没有"才算失败。
  `tblProperty`、`tblProjectPara` 在 `yjk_save` 时会展开，属正常，绝不要拿它们做判据。
* 校验必须排在 `yjk_save` 之后 —— `.ymd` 由 save 写出，早于 save 会得到
  `unable to open database file`。

## 模态框看门狗

`StdSlab_batgenstl` 会弹「施工图已经进行过选筋,是否重新选筋?」。模态期间主窗口被
`Disable`，**IPC 命令从此不返回**。

* `BM_CLICK(0x00F5)` / 键盘消息 / `WM_CLOSE` **全部无效**。
* 唯一有效：`PostMessageW(dlg, WM_COMMAND=0x0111, IDNO=7, GetDlgItem(dlg, 7))`。

落地在 `scripts/dlgwatch.py` 的 `DialogWatch` 后台线程。

它必须在启动 `yjks.exe` 之前拉起来 —— `draw_quant.py` 先 `DialogWatch(None)` 再 `start()`，
然后才 `boot_yjks()`。`pid=None` 阶段（pid 还未知）**只登记不动手**，一个按钮都不点；
`own_claim` 拿到自有实例后 `narrow(pid)` 收窄到本实例，此后才按 `RULES` 应答；未命中 `RULES`
的框默认不应答（`DEFAULT = None`），授权/许可类框永不自动应答。顺序反了就没人应答启动阶段
弹出的框，会一直等到超时才报「IPC 未就绪」（见 `references/troubleshooting.md` §8）。

它同时把正文命中「文件不存在 / 不存在 / 读取错误 / 非法数据 / 出错 / 失败」的框收进
`watch.errors` —— 收工后必须看这个列表，别只看 `RunCmd` 返回值。

## 产出物

**施工图**（DWG，落在 `<工程目录>\施工图\`）

| 文件 | 内容 |
|---|---|
| `BeamPlan1.dwg` | 梁平法施工图 |
| `ColPlan1.dwg` | 柱平法施工图 |
| `WallT1.dwg` | 墙施工图 |
| `SlabPm1/2/3.dwg` | 板平面配筋图（逐层） |
| `SlabJt1/3.dwg` | 板节点图 |
| `楼板弯矩/挠度/裂缝/计算面积简图1-3.dwg` | 板计算简图 |
| `SlabCalData*.txt` / `SlabCalPara*.txt` | 板计算数据 |

**工程量**

| 文件 | 内容 |
|---|---|
| `计算书/工程量统计/工程量统计.ini` | **混凝土**体积（GBK）。`Gcl-Hnt-Zrc<层>` 逐层，`Cap=` 给列名 |
| `施工图/全楼楼板钢筋用量.xlsx` | 板钢筋（9×11 布局） |
| `施工图/全楼梁钢筋用量(钢筋规格与类别).xlsx` | 梁钢筋（21×15） |
| `施工图/全楼柱钢筋用量(钢筋规格与类别).xlsx` | 柱钢筋（13×9） |
| `施工图/全楼墙钢筋用量(钢筋规格与类别).xlsx` | 墙钢筋（6×6，无墙时合法为空） |
| `施工图/柱钢筋统计.txt` | 柱钢筋 txt 补充 |

**留档 + 汇总**：`results/<proj>/` 下 `混凝土工程量汇总.txt/.json`、`run_manifest.json`、
`_draw_quant.log`（逐条命令日志）；最后 `summary_xlsx.py` 出 6 页 Excel
（汇总 / 混凝土 / 钢筋 / 施工图清单 / 计算口径 / 自检）。

## 读 YJK 钢筋表的三个要点

1. **直径行在表头行的下一行**。表头行只有合并的 `'HRB400'` 标题，没有数字，在表头行上找直径
   一无所获。
2. **表尾有一行只重复总计数字**（板 r8 / 梁 r20 / 柱 r12），第一列是空的 —— 不能拿"第一个
   数字行"当合计，必须认 `全楼` / `合计` / `总计` 文字。
3. **不能用「包含」匹配** —— 板的标题行是 `['', '全楼楼板钢筋用量', …]`，含「全楼」二字，会被
   误当合计行（该行直径列全空 → 结果读成 0，伪装成"统计未生效"）。必须让**楼层列（第 2 列）
   精确等于** 合计关键字。

另外 openpyxl 直接开 YJK 的 xlsx 会报 `Colors must be aRGB hex values` ——
YJK 写出的 `styles.xml` 里有非 aRGB 的 `rgb` 值。见 `read_yjk_xlsx.py`：把 xlsx 当 zip
读出来修 `xl/styles.xml`（6 位补成 `FF` + 6 位、非法置黑、去掉 `theme=`/`indexed=`），
再 `load_workbook(BytesIO)`，不动原文件。

## 已知边界

* YJK 不出模板（formwork）工程量 —— 必须按定额接触面积手算。
  （`floor-system-comparison` 技能里的 `takeoff.py` 实现了这件事，可复用其口径。）
* `DtlRC_AutoStatExcel` / `DtlRC_MpcAutoStatSteel` / `DtlRC_SS` / `DtlRC_SSBE` /
  `DtlRC_SSB` / `DtlRC_SSW` 在 `IDQUANTITYLIST_DETAIL` 下都是 `OK(0.0s)` 空操作，
  不要用；用上面 `REBAR_CHAIN` 里那 5 条。
* `yjkdesignexport_dsnQuantityStatisticsReport`（`IDDSN_DSP`）只产出 `SPara.par`，无用。

## 批量跑时的两个注意点

1. **safe-delete 钩子**：`Y.kill_own() → own_clear() → os.remove(own.json)` 抛的
   不是 `Exception`，`try/except Exception` 抓不住，会让批量循环只跑完第 1 个。
   `draw_quant.py` 里已处置：`Y.own_clear = lambda *a, **k: None`。
   自己写批量脚本时照做即可。
2. **必须前台跑**（或让宿主进程常驻）。`yjks` 由宿主进程托管
   （见 `yjk-auto-drive` 硬性约束 2），宿主一退出 `yjks` 立即被回收；后台任务在会话轮转时
   也会被杀掉。

## 参考文件

* `references/commands.md` —— 命令登记表（含哪些是空操作）+ 环境依赖
* `references/troubleshooting.md` —— 导入空模型 / 模态框 / 钢筋表读法 的完整排查
* `scripts/README.md` —— 每个脚本的输入输出契约与退出码

## 依赖

* 本技能必须能找到 `yjk-auto-drive`（用它启动/导入/计算，以及 `Y.diff()` 快照）。查找顺序
  （全部是环境变量/相对路径/家目录一级子目录，无写死盘符与桌面依赖）：环境变量
  `YJK_DRIVER_DIR` → `YJK_SKILLS_DIR/yjk-auto-drive/scripts` → 同父兄弟目录 → 当前目录
  → 各 agent 的技能家目录（枚举 `~` 与 `~/.config` 的一级子目录去找 `<D>/skills/yjk-auto-drive`，
  不写死任何厂商名）→ 历史遗留路径（唯一带厂商名的一档，保留以不破坏现有用户：去掉它其余
  各档照样工作；具体路径见 AGENT-COMPAT.md）。找不到会以退出码 2 报错，并列出所有查过的位置。
  换 agent / IDE 的注意事项见根目录 `AGENT-COMPAT.md`。
* Python：不要写死解释器路径，用 `yjk-auto-drive` 的探测结果 ——
  `python paths.py --doctor` 或代码里 `driver.python_exe()`（需 `openpyxl`、`pythonnet`）。
  首次在新机器上可先跑 `python setup_env.py` 一键建隔离环境。
* 改完脚本跑一遍可移植性自检：`python <yjk-auto-drive>\scripts\portability_check.py`
  （扫描整套技能，退出码 0 = 通过）。

## YJK 官方二次开发资料（离线参考集）

本技能做的事全在"命令 + 设计结果 + 数据文件"三块，官方最对口的几篇已随包转到
`yjk-dev-refs/`（来源与版本见该目录 README）：

| 文档 | 用途 |
|---|---|
| `04-接口说明/命令说明文档.md`、`UI接口及命令接口说明.md` | 命令全表与标签归属——`CONC_CHAIN`/`REBAR_CHAIN` 的口径依据 |
| `04-接口说明/设计结果接口说明-新.md`、`设计结果宏定义.md` | 设计结果字段定义（解析 `wpj*.out`、核对钢筋量口径时对照） |
| `04-接口说明/基础设计结果接口说明.md` | 基础部分的设计结果 |
| `05-数据文件说明/` | **施工图数据库**：`dtlRcCol`（砼柱）、`dtlRcBeam`（砼梁）、`dtlRcWall`（砼墙）、`dtlSlabPub`（板）的字段说明，以及《楼板钢筋文件记录说明》——读"全楼\*钢筋用量.xlsx"读不懂时先查原表定义 |
| `06-总信息参数ID表/` | 总信息各项含义（判断抗震等级/轴压比限值口径时用） |

## 编码约定（生成代码与文件时必须遵守）

本包在简体中文 Windows 上运行，控制台与部分工具默认用 GBK。下面的约定是硬的：
这里出问题时**多数不报错**，只是静默给错结果，或把成功判成失败。

1. 源码与文本产物一律 **UTF-8、无 BOM**；`.py` 首行写 `# -*- coding: utf-8 -*-`。
2. 所有 `open()` 显式 `encoding=`：普通文本 `utf-8`；人可能用记事本改过的配置/标志文件用
   `utf-8-sig`（BOM 会被当成正文）。二进制模式除外。
3. 读 YJK 自己的输出（`*.out`、`设计结果\*.txt`、`中间数据\*`、`dsnctrl.ini`）用 **`gbk`**
   （`errors="replace"`）。用 UTF-8 读会乱码，而且通常不报错，只是解析出 0 条。
4. `print` 里含非 GBK 字符（`✅❌⚠²³−` 等）时，本文件必须调用 `_utf8_console()`，并且要在
   `main()` 里调用一次；只在 `if __name__ == "__main__"` 分支里调用时，被别的脚本 import
   当库用仍会在 GBK 控制台崩（退出码 1，明明成功却判成失败）。没有 `main()` 的库模块，
   放在对外入口函数里。新增输出优先用 ASCII 标记（`[OK]` / `!!`）。
5. 子进程抓文本：`text=True, encoding="utf-8", errors="replace"`；调用本包脚本加 `-X utf8`
   并传 `PYTHONIOENCODING=utf-8`。
6. 写 JSON 用 `ensure_ascii=False` + `encoding="utf-8"`，中文才可读。
7. 生成 `.bat` / `.ps1` 若含中文，先 `chcp 65001 >nul`，否则只用 ASCII。

静态检查：`python yjk-auto-drive\scripts\encoding_check.py`（0 = 合规）。
完整规则与"不遵守会怎样"的对照见 `AGENT-COMPAT.md` 的「编码约定」一节。
