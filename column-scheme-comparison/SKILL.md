---
name: column-scheme-comparison
description: 结构柱型方案比选全流程。从种子模型读取柱位和内力信息，按 JGJ3 与 CECS188 的轴压比/含钢率/套箍指标等限值自动选配普通RC、加芯RC、型钢SRC、钢管叠合柱、圆钢管混凝土柱截面，导出可人工微调的 Excel 设计表，回写 YJK 模型，进行模型计算，然后用户也可以继续要求回读计算结果，要求进一步回填，用户满意后统计用量、造价与投入产出比；另含一条轻量经济比选链路（RC vs 矩形/圆形 CFST，按 GB 50936-2014 与广州定额，直接产出 Excel 经济对比报告）。当用户要求柱型比选、按轴压比调整柱截面、统计柱构件用量与造价、为各柱型建立独立计算目录、比较 RC 与钢管混凝土柱哪个便宜时使用。不适用于梁、板、墙或基础。
---

# 柱型方案比选

把"设计轴力 → 按规范选截面 → 写进模型 → 重算 → 统计比选"这条链路固化成可复用的流程。
**程序负责算得快、算得一致；判断与确认留给人**。本文件是流程总纲。

---

## 一、全流程一览

```
   【人】分组与楼层 ─┐
                    ▼
  ┌──────────────────────────────────────────────────────────────────┐
  │ ① 定柱位与楼层      cli.py init  →  scope                        │──► 00_输入/scheme.json
  └───────────────────────────────┬──────────────────────────────────┘
                                  ▼
  ┌──────────────────────────────────────────────────────────────────┐
  │ ② 建计算目录        cli.py scaffold                              │──► 01_RC/ 02_RC_Core/
  │                     每种柱型一个目录 + 一份种子模型副本            │     03_SRC/ 04_Diehe/
  └───────────────────────────────┬──────────────────────────────────┘     05_CFST/ 99_汇总/
                                  ▼
  ┌──────────────────────────────────────────────────────────────────┐
  │ ③ 取设计轴力与材料  yjk.py res / wmass / export                  │──► 00_输入/forces.json
  │ 【人】叠合柱管内砼 ──► 必须回 YJK 设置（程序读不到）                 │
  └───────────────────────────────┬──────────────────────────────────┘
                                  ▼
        ┌───────────────────────── 迭代环（每个柱型各走一遍） ─────────────────────────┐
        │                                                                             │
        │  ④ 选截面     cli.py design ──► scheme_design.json + 截面设计表.xlsx          │
        │  【人】限值取值 / 型钢规格 / 单价与假定                                        │
        │        │                                                                    │
        │        ▼                                                                    │
        │  ⑤ 人工微调   cli.py excel → 【人】改 Excel → cli.py import-excel            │
        │        │                                                                    │
        │        ▼                                                                    │
        │  ⑥ 回写模型   yjk.py apply 【人】确认后加 --apply（自动备份）                  │
        │        │                                                                    │
        │        ▼                                                                    │
        │  ⑦ 重算复核   【人】回 YJK 重算 → yjk.py res / verify                        │
        │        │                                                                    │
        │        └──── 不满足限值或目标利用率 ──► 回到 ④ ──────────────────────────────┘
        └─────────────────────────────────┬───────────────────────────────────────────┘
                                          ▼
  ┌──────────────────────────────────────────────────────────────────┐
  │ ⑧ 统计与报告        cli.py quantity / io                         │──► 99_汇总/柱型对比.xlsx
  │ 【人】单价与配筋假定 ──► 换地区换年份必须替换                        │    汇报 PPT
  └──────────────────────────────────────────────────────────────────┘
```

图例：**【人】** = 必须人工判断或操作；**不加【人】的步骤 = 程序可自动完成**。

---

## 二、需要用户干预的工作（重点）

程序会在这些地方**停下来等人**，不要指望它自动拍板。

| # | 干预点 | 为什么必须人工 | 程序提供什么辅助 | 不做的后果 |
|---|---|---|---|---|
| 1 | **柱位分组 `groups`** | 分组是设计意图，不是模型属性 | `init --groups` 解析你的分组；`scope` 报出"柱号写错"和"漏柱" | 写错柱号 → 硬错误拒写；漏柱 → 静默少算 |
| 2 | **参与对比的标准层 `--std`** | 取全楼还是只取受力最大几层，是设计判断 | `init` 打印各标准层的定义层高、自然层、柱数供选 | 取错层 → 比选结论偏 |
| 3 | **轴压比限值取值** | 结构类型、抗震等级、短柱、加密箍措施**是否可叠加**（规范注5 原文是"措施之一"）须与抗震审查一致 | `limits` 打印全部限值与展开表 | 限值取宽 → 柱偏小；取严 → 偏保守浪费造价 |
| 4 | **叠合柱管内（核心）混凝土等级** | 该等级存在模型 `.yjk` 二进制里，**程序既读不到也写不进去** | 一律打印提醒；设计表「设计参数」留可编辑列；`config.diehe.fc_in` 可显式指定 | 按错误等级算套箍指标 θ，叠合柱截面不可信 |
| 5 | **型钢规格（十字型钢）** | 自动比例只是经验值，正式项目要用设计确认的规格 | `config.src.steel="f,tw,d"` 或 `src.family=[...]` 传入实际规格 | 含钢率、型钢用量与造价失真 |
| 6 | **单价与配筋假定** | 随地区/年份/项目口径变化 | 设计表「单价」「截面参数」的纵筋率/配箍率列可直接改；报告里写明口径 | 造价与投入产出比失去可比性 |
| 7 | **截面人工微调** | 可施工性、建筑配合、规格归并 | `excel` 导出可编辑设计表 → `import-excel` 读回并打印逐条差异 | 程序方案可能不合施工/建筑要求 |
| 8 | **确认是否改模型** | 改模型不可逆 | `apply` **默认只预演**；`--apply` 才写；写前自动备份；写后校验不通过则非 0 退出 | 未经确认改坏模型 |
| 9 | **回 YJK 重算** | 程序只改几何，不触发计算；**YJK 必须人工用 `YjkLauncher.exe` 打开并敲一次 `yjksIPCControl`**，启动这一步无法自动化 | 通道开好后，`YJKSControl` 可自动跑完全部命令（见第三节"YJK 自动化前置条件"） | 拿不到新结果，复核无从谈起 |
| 10 | **逐结构层材料设置** | 材料在 `.yjk` 二进制里，脚本写不进 | `wmass` 能**读**出各层等级，供你照着设 | 按wmass.out文件设置 |

> 程序的安全约定：**所有写操作默认预演**（`init` / `design` / `import-excel` / `apply` 都要显式 `--apply`），
> 且每次落盘前自动备份 `*.bak_时间戳`。任何"程序自己改模型"的用法都是错的。

---

## 三、环境与前置

```powershell
$py = 'E:\ProgramData\anaconda3\python.exe'                                     # 唯一装了依赖的解释器
$sk = 'c:\Users\Administrator\.trae-cn\skills\column-scheme-comparison\scripts'  # 本技能
$yk = 'c:\Users\Administrator\.trae-cn\skills\yjk-colmodel\scripts'              # 配套技能
$M  = '<种子模型目录>'                                                            # 含 g-of.ymd
```

- Windows + 已安装 YJK；解释器必须用上面这个（msys64 的 python 无 pip）
- 运行加 `-B`；stderr 的 `No module named '_distutils_hack'` **无害**，用 `2>$null` 屏蔽
- Excel **写出**只用标准库；**读回**改过的 Excel 需要 `openpyxl`（anaconda 自带）
- 读 `wmass.out` 需要同机装有 yjk-colmodel 技能；读不到时会提示改用 `--model-json`
- 要在 ⑦ 自动触发重算，需要 `YJKAPI`（`pip install yjkapi`）；**但启动 YJK 这一步必须人工做**，见下

### YJK 自动化前置条件（⑦ 之前必读）

重算环节可以交给 `YJKSControl` 自动跑，但**启动 YJK 无法自动化**，必须先人工做两件事：

1. **用正常入口打开 YJK**：双击 `YjkLauncher.exe`（桌面/开始菜单快捷方式的目标就是它），由它完成授权签出。
   直接运行 `yjks.exe`（`YJKSControl.init` 就是这么干的）会**绕过启动器**，软件弹"**要添加授权**"且主程序起不来，通道自然不通。
2. **在 YJK 命令行敲一次 `yjksIPCControl`** 回车，开启外部控制通道。

之后所有命令都能自动发：

```powershell
# 通道是否已开：开了秒回；没开 RunCmd 会一直阻塞（无超时，不要傻等）
& $py -X utf8 -u -B -c "from YJKAPI import *; YJKSControl.RunCmd('SetCurrentLabel','IDModule_Axis')" 2>$null
```

单个柱型目录的完整重算命令序列（每个目录各走一遍）：

```
yjk_opennew <该柱型目录>\<工程名>          # 打开已有模型，不带 .yjk
yjk_save
yjk_setlayersupport  →  yjkspre_genmodrel
yjktransload_tlplan  →  yjktransload_tlvert
SetCurrentLabel IDSPRE_ROOT
yjkdesign_dsncalculating_all               # 生成数据 + 全部计算
SetCurrentLabel IDDSN_DSP
yjk_save
```

要点与坑：

- **只允许一个开启 IPC 的实例**。命令打到"当前开着 IPC 的那个 YJK"上，若该实例里正开着真实工程，
  `UINew` 会把工程顶掉（未保存改动会丢）——发 `UINew`/导入 ydb 前必须先确认。
- `Config.ini` 里的 `[YJKSControl] Flag = True`（`C:\ProgramData\yjkSoft\YJKS{版本}\YJKS\Config.ini`）
  在 6.1 / 7.1 上**不生效**，别指望它开通道；且该文件会被 YJK 启动/退出整份重写，
  要在 YJK **全关**状态下改才留得住。
- `YJKSControl` 功能本身需要**盈建科 API 授权码**，可向当地技术支持申请；没授权码就只能走上面的人工两步。
- **`RunCmd` 是阻塞的**：要等 YJK 把命令执行完才返回（不是 fire-and-forget）。
  所以命令里弹出模态框时，`RunCmd` 会**永久阻塞**——弹窗必须在**后台线程**里应答，见下。

### 必须自动应答「是否保存当前工程?」

`UINew` 顶掉当前打开的工程时，YJK 会弹模态框（标题「提示」，正文「是否保存当前工程?」，
按钮 `是(&Y)` / `否(&N)` / `取消`）。不处理就整条流程卡死。
YJKSControl **没有**对外可用的关弹窗命令（`QSetRunScript` 只存在于 yjks.exe 的进程内导出），
只能用窗口消息：

```python
# 后台线程每秒执行：只碰 yjks 自己的问答型对话框
# 1) EnumWindows 找 class=#32770 且进程可执行文件含 "yjks" 的窗口
# 2) 取其 Button 子窗口，文字含「是/确定/OK」的
# 3) SendMessageW(btn, BM_CLICK=0x00F5, 0, 0)   ← 实测最可靠
# 注意：keybd_event/SetForegroundWindow 会被 UIPI、焦点限制挡掉，不要指望它
```

三条要点：

1. **必须后台线程全程盯着**，不能"等 RunCmd 返回后再处理"——那时已经卡死了。
2. **只处理有问答按钮的窗口**：计算进度条一类没有 Button 子窗口，别对它按回车/点按钮。
3. 用按钮的 `BM_CLICK`，并严格限定"窗口属于 yjks.exe"，避免干扰用户其它程序。

已试过、**确认无效**的两条规避路径，不要再走：

| 规避思路 | 实测结果 |
|---|---|
| `UINew` 前先 `yjk_save` 保存当前工程 | 无效，YJK 仍会询问 |
| 复用同一工程，每轮只 `yjk_importydb` 覆盖模型 | 无效，对已有工程的导入**静默不生效**（模型文件毫无变化） |

### 等待策略：信号驱动 + 只缩不放

不要用固定 sleep 硬等（一轮会白等 3~4 分钟）。做法：

- 能观测完成信号的步骤就轮询信号，取**实测耗时**：
  新建工程 → 看 **YJK 主窗口标题**（`class=yjks` 的窗口，标题即工程路径）；
  保存 → 看 `<工程名>.ymd` 的 mtime（工程文件**保存时**才落盘，不要拿它判断新建完成）；
  计算 → 看 `设计结果\wmass.out` 的 mtime。
- 观测不到信号的快命令（导入/修复/形成节点等），按"上轮实测总时长 × 余量 − 已观测部分"按比例调整。
- **只缩不放**：上限永远是配置里的默认值（默认值即余量），下限 1.5s；实测取**历史最小值**，
  偶发卡顿（弹窗、杀进程）不污染后续计时。
- 实测值落盘（如 `timing.json`），可查看/手改/删除（删了恢复默认）。

参考量级（4 层 3×3 跨框架，本机实测）：整段 282s → **73s**，其中新建 3.2s、建模段 21s、计算段 32s。

可直接复用的代码（弹窗应答 / 信号等待 / 命令序列）见 `yjk-colmodel/references/yjkcontrol.md`。

---

## 四、工作流详解

### ① 定柱位与楼层

**目的**：把"比哪几层、比哪几根柱"变成机器可读的 `scheme.json`。

```powershell
& $py -X utf8 -B "$sk\cli.py" init --model $M `
      --groups "Z1=15,16;Z2=14;Z3=13;Z4=1,7;Z5=2,3,4,9,10" `
      --std 3,4,5 --sec-type 圆钢管混凝土柱 --project "项目名" `
      --out 00_输入\scheme.json --apply 2>$null

& $py -X utf8 -B "$sk\cli.py" scope --scheme 00_输入\scheme.json --model $M 2>$null
```

- `--groups`：**【人】干预点 1**，形如 `名称=柱号,柱号;名称2=…`
- `--std`：**【人】干预点 2**，不给则取模型里所有有柱的标准层
- `--sec-type`：把模型**现有**截面当作哪个柱型的初始截面（默认第一个柱型）
- `init` 输出：`std_floors`（定义层高 / 各自然层实际层高 / 首个自然层号）+ `sections`（现有截面）

**判据**：`scope` 报 `0 个错误`；漏柱提醒要逐条确认是否"有意为之"。

### ② 建计算目录

**目的**：一个 YJK 模型目录只能有一套柱截面，五种柱型要分五份算。

```powershell
& $py -X utf8 -B "$sk\cli.py" scaffold --root "D:\项目\柱型比选" `
      --scheme 00_输入\scheme.json --seed $M `
      --forces 00_输入\forces.json --config 00_输入\config.json `
      --mode slim --dry-run 2>$null      # 确认后去掉 --dry-run
```

```
<root>/  00_输入/  01_RC/  02_RC_Core/  03_SRC/  04_Diehe/  05_CFST/  99_汇总/  README.txt
```

- `--mode slim`（默认）跳过大目录（`中间数据`/`基础计算及结果输出`/`基础备份`/`backup`/`设计结果`）；
  `full` 全量；`none` 只建目录不复制
- 目录名可用 `SLOT` 映射调整；`README.txt` 会写明目录对应关系与流程

### ③ 取设计轴力与材料

**目的**：拿到每根柱的设计轴力，和**逐结构层**的混凝土强度/钢号。

```powershell
& $py -X utf8 -B "$yk\yjk.py" doctor $M 2>$null                                  # 先自检
& $py -X utf8 -B "$yk\yjk.py" res    $M --std 3,4,5 --json 00_输入\forces.json 2>$null
& $py -X utf8 -B "$yk\yjk.py" wmass  $M --floors 3,4,5,8,11,14 2>$null            # 看材料
& $py -X utf8 -B "$yk\yjk.py" export $M --json 00_输入\model.json 2>$null         # 一次拿全
```

- `res` 给出 `截面 / λc / 材料 / Nu / Uc / R_F1 / Rs / Rsv / θ / D/t / 超限标记`
- `wmass` 给出各**自然层**的柱混凝土等级与钢号（**型钢混凝土构件**表最可靠）
- **【人】干预点 4**：叠合柱管内混凝土等级读不到 → 现在就去 YJK 里确认并设置

**判据**：`res` 能解析出柱记录（条数 = 层数 × 目标柱数）；`wmass` 的等级与设计文件一致。

### ④ 选截面

**目的**：按规范限值与目标利用率，为每个 (柱型, 标准层, 组) 选出截面。

```powershell
& $py -X utf8 -B "$sk\cli.py" limits --seismic 2 2>$null                          # 【人】干预点 3
& $py -X utf8 -B "$sk\cli.py" check  --scheme s.json --forces res.json --model $M 2>$null

& $py -X utf8 -B "$sk\cli.py" design --scheme s.json --forces res.json --model $M `
      --config cfg.json --types 钢管叠合柱 --out <该柱型目录>\scheme.json `
      --excel <该柱型目录>\截面设计表.xlsx 2>$null
#   确认后再加 --apply 写 scheme；--types 保证一个目录只算一个柱型
```

- 材料等级由 `--model` / `--wmass` / `--model-json` 提供，逐标准层取值（**不全楼一个等级**）
- **【人】干预点 3**：`limits` 的取值与抗震审查意见不符时，用 `--config` 覆盖
- **【人】干预点 5**：SRC 的十字型钢规格用 `config.src.steel` / `src.family` 传入
- `--std` / `--cols` 只用于**范围核对**（会裁减组内成员、改变控制轴力），**不要用它定案**

**判据**：`未能求解 0 处`；复核列里的 `Uc / R_F1 / Roa / θ / Dt / 净距 / cover` 都在限值内。

### ⑤ 人工微调截面

**目的**：程序方案落到可施工、合建筑、规格可归并的截面。

```powershell
& $py -X utf8 -B "$sk\cli.py" import-excel --xlsx 截面设计表.xlsx `
      --scheme scheme_design.json --out scheme_edited.json 2>$null   # 确认后加 --apply
```

设计表 5 张：**说明 / 设计参数（可改）/ 单价（可改）/ 截面参数（可改）/ 用量造价（公式）**。

- 「截面参数」A~N 列可直接改（Kind、b/h/u/t/d/f、混凝土等级、钢材牌号），O 列以后全公式自动重算
- 「设计参数」可改各标准层材料等级与**管内混凝土等级**
- `import-excel` 会打印**逐条差异**（柱型/标准层/组/原截面 → 新截面）供确认

### ⑥ 生成改动清单并回写模型

**目的**：把 ⑤ 定稿的截面转成 YJK 的改动清单，再写进该柱型目录里的模型（计算模型 + 施工图模型同步）。

> **待补**：`scheme.json → changes.json` 的转换命令目前还没有（`cli.py changes`）。
> 现阶段这一步要手工按下面的格式写，或写一次性脚本从 `scheme.json` 生成。

```powershell
# 目标形态（待补命令后可直接用）：
& $py -X utf8 -B "$sk\cli.py" changes --scheme scheme_edited.json --types 钢管叠合柱 `
      --std 3,4,5 --out <该柱型目录>\changes.json 2>$null

& $py -X utf8 -B "$yk\yjk.py" apply <该柱型目录> --changes ch.json 2>$null          # 预演
& $py -X utf8 -B "$yk\yjk.py" apply <该柱型目录> --changes ch.json --apply 2>$null  # 【人】干预点 8
& $py -X utf8 -B "$yk\yjk.py" verify <该柱型目录> 2>$null
& $py -X utf8 -B "$yk\yjk.py" diff    <原模型> <该柱型目录> 2>$null                  # 核对改了哪些
```

改动清单格式（键是**标准层号**；`cols` 是柱号列表；`kind` 可省，按字段自动判定）：

```json
{ "3": [ {"cols": [15,16], "kind": 1,  "b": 1650},
         {"cols": [14],    "kind": 12, "D": 1300, "tw": 20},
         {"cols": [13],    "kind": 15, "b": 1450, "f": 350, "tw": 26, "d": 950},
         {"cols": [1,7],   "kind": 102,"b": 1400, "D": 700,  "tw": 28} ] }
```

**判据**：`integrity=ok`、悬空 SectID=0、`idNewDef` 不匹配=0、ID 重复=0。

### ⑦ 重算复核

**目的**：拿到真实结果，检查是否满足限值与目标利用率。

**【人】干预点 9**：先确认 YJK 已由 `YjkLauncher.exe` 正常打开、且已在命令行敲过 `yjksIPCControl`（见第三节），
然后二选一——手动点"生成数据 + 全部计算"，或由 `YJKSControl` 自动跑那串命令。

```powershell
# 【人】干预点 9：打开 YJK 并敲 yjksIPCControl 之后，下列命令可全自动发
# yjk_setlayersupport → yjkspre_genmodrel → yjktransload_tlplan/tlvert
# SetCurrentLabel IDSPRE_ROOT → yjkdesign_dsncalculating_all → SetCurrentLabel IDDSN_DSP → yjk_save
& $py -X utf8 -B "$yk\yjk.py" res    <该柱型目录> --std 3,4,5 --json r2.json 2>$null
& $py -X utf8 -B "$sk\cli.py" check  --scheme scheme_edited.json --forces r2.json `
      --model <该柱型目录> --config cfg.json 2>$null
```

**判据**：`Uc ≤ 限值`、CFT 的 `R_F1 ∈ 目标区间`、叠合柱 `θ ≤ 上限`、`Roa ≥ 3%`、SRC `ρa ∈ [4%,5%]`。
**不满足就回到 ④ 重选**——这是本流程的正常迭代，不是异常。

### ⑧ 统计与报告

```powershell
& $py -X utf8 -B "$sk\cli.py" quantity --scheme scheme_final.json --out 99_汇总\柱型对比.xlsx 2>$null
& $py -X utf8 -B "$sk\cli.py" io       --scheme scheme_final.json 2>$null
```

- **【人】干预点 6**：单价与配筋假定换地区/年份必须替换，并在报告里写明口径
- 统计表是公式驱动，改「单价与假定」或「截面参数」即自动重算
- 汇报 PPT 的生成与同步见 struct-report-pptx 技能

---

## 五、输入文件规格

**scheme.json**

```json
{
  "project": "项目名",
  "std_floors": {
    "3": {"height_mm": 6000, "nat_heights": [6000, 5500], "first_nat": 3},
    "4": {"height_mm": 7500, "nat_heights": [7500, 4500, 4500], "first_nat": 5},
    "5": {"height_mm": 4500, "nat_heights": [4500, 4500, 4500, 4500, 4500, 4500, 4500]}
  },
  "groups": {"Z1": [15, 16], "Z2": [14], "Z3": [13], "Z4": [1, 7], "Z5": [2, 3, 4, 9, 10]},
  "types": ["普通RC", "加芯RC", "型钢SRC", "钢管叠合柱", "圆钢管混凝土柱"],
  "sections": { "普通RC": { "3": { "Z1": {"kind": 1, "b": 1650} } } }
}
```

- `height_mm` = 标准层定义层高；`nat_heights` = 覆盖的各自然层**实际**层高（可不等）；`first_nat` = 第一个自然层的结构层号
- `groups` 是**设计单位**：同组同截面
- 几何：`kind 1` 用 `b`；`kind 12` 用 `D`+`tw`；`kind 15` 用 `b`+`f`+`tw`+`d`；`kind 102` 用 `b`+`D`+`tw`

**config.json**（都可省，用默认值）

```json
{
  "concrete": "C60", "steel_grade": "Q355",
  "rc":    {"seismic": 2, "densify_hoop": true},
  "core":  {"core_ratio": 0.25},
  "src":   {"seismic": 2, "densify_hoop": true, "roa": 0.045, "steel": [350, 26, 950]},
  "diehe": {"gap": 650, "gap_min": 600, "fc_in": "C60"},
  "cft":   {"D": [900,1000,1100,1200,1300,1400], "lo": 0.80, "hi": 0.88},
  "prices": {"C60混凝土": 530, "HRB400钢筋": 4050},
  "rebar": {"普通RC": 0.008, "加芯RC": 0.016},
  "tie":   {"普通RC": 1.2, "加芯RC": 2.2}
}
```

---

## 六、铁律

1. **先 `scope` 再干活**。柱号写错会被拦，漏柱不会——漏柱要自己看。
2. **材料等级逐层取，不要一个 C60 通吃**。结构层 3~10 是 C60、11~14 是 C55 时，写错一级结论就偏。
3. **叠合柱管内混凝土必须人工确认**（干预点 4）。这是全流程唯一"程序算不了的输入"。
4. **写操作一律默认预演**，确认后才 `--apply`；落盘自动备份。
5. **`--std` / `--cols` 只作范围核对**，会改变控制轴力，不要用它定案。
6. **同组同截面、竖向不出现下小上大**：按组逐层设计，约束每组独立，不跨组抬高。
7. **用钢量乘密度 7.85**；**结构占用面积是"每层"量**（代表楼层口径乘自然层数）。这两处都出过错。
8. **造价口径必须在报告里写明**（哪年、哪地区、含什么、不含什么）。
9. **不满足限值就回 ④ 迭代**，不要靠改结论凑数。
10. **要自动重算，先人工开 YJK**：`YjkLauncher.exe` 打开 + 命令行敲一次 `yjksIPCControl`。直接起 `yjks.exe` 会弹"要添加授权"，通道永远不通（见第三节）。

---

## 七、口径速查

| 项 | 口径 |
|---|---|
| 混凝土量 | 矩形/型钢/叠合柱 = 全截面×层高；圆钢管混凝土柱 = **管内净面积**×层高 |
| 钢筋量 | (纵筋率 + 体积配箍率)×**结构占用面积**×层高×7.85 |
| 型钢/钢管量 | 钢材截面积×层高×7.85（十字型钢 `4ft+2dt−t²`；钢管 `π/4(D²−Din²)`） |
| 模板量 | 柱周长×层高；圆钢管混凝土柱钢管兼作模板，不另计 |
| 防腐防火 | 圆钢管混凝土柱按含 30mm 涂层的钢管外表面 `π(D+2a)×层高`，其余不另计 |
| 结构占用面积 | 圆钢管混凝土柱 `π/4×(D+2a)²`（钢管+涂料）；其余 = 柱外轮廓面积。**每层量** |
| 投入产出比 | 相对基准柱型的**造价增量 ÷ 换回的楼面面积**（占用面积减少量），元/m² |

---

## 八、出错怎么办

| 症状 | 原因 | 处理 |
|---|---|---|
| `scope` 报"柱号模型里不存在" | `--groups` 写错 | 按提示的"该层实际柱号"改正后重跑 |
| `design` 报"取不到设计轴力" | `forces.json` 里没有该柱号/该标准层 | 确认 `res` 的 `--std` 覆盖到，或 `groups` 柱号写错 |
| `design` 报"无可行截面" | 约束太紧（θ 上下限、含钢率区间、保护层） | 先试 `src.family` / `src.steel` 换型钢族、`diehe.gap`/`gap_min` 放宽净距、放大 `cft.D` 候选；θ 上下限与 `th_max` 目前未开放到 config（见第十节） |
| 某组 `R_F1` 明显低于目标 | 该组轴力偏小，θ 已到下限 | 正常结果，说明该组不是控制组；程序会标注"偏低" |
| Excel 里数值不刷新 | 未开自动重算 | 已设 `fullCalcOnLoad`；仍不刷就 Ctrl+Alt+F9 强制重算 |
| `import-excel` 读不到表 | 改动了「截面参数」表头行 | 表头必须留在第 2 行、数据从第 3 行起 |
| `apply` 后校验非 0 | 写入异常 | 直接用同目录的 `*.bak_时间戳` 回滚 |
| YJK 打开模型报错 | 只改了 `SectID` 没改 `idNewDef` 等 | 用 `yjk.py verify` 定位；本技能已成对更新 |
| `YJKSControl.RunCmd` 发出去**几十秒不返回** | IPC 通道没开（`RunCmd` 无超时，会一直阻塞） | 在已打开的 YJK 命令行敲 `yjksIPCControl`；再确认没有第二个 YJK 实例 |
| 自动启动的 YJK 弹"**要添加授权**" | 直接起了 `yjks.exe`，绕过 `YjkLauncher.exe` 的授权签出 | 改人工用 `YjkLauncher.exe` 启动；想彻底自动就去申请 YJKSControl 的 API 授权码 |
| 命令跑完但结果目录没更新 | 命令是异步的，没等够就查了产物 | 轮询 `设计结果\wmass.out` 等产物文件，别用固定 sleep 判断 |

---

## 九、当前代码与本文档的差距（待补）

改代码时对着这张表逐项处理。

| # | 本文档描述 | 现状 | 建议 |
|---|---|---|---|
| G1 | ⑥ `cli.py changes`：`scheme.json` → YJK 改动清单 `changes.json` | **没有**，目前手工写 | 新增子命令：按 `--types`/`--std` 取定稿截面，按标准层号+柱号输出 `{"3":[{"cols":[…],"kind":…,…}]}` |
| G2 | 排错表"放宽 θ 上下限" | `design_cft` 的 `theta_min` / `theta_max`、`design_diehe` 的 `uc_lim` / `th_max` / `t_cap`、`design_src` 的 `cover` / `step` **未从 config 透传** | 在 `design_one` 里把这些参数从 `cfg` 读出来传给 `codes.*` |
| G3 | ② "目录名可用 `SLOT` 映射调整" | `scaffold.SLOT` 是常量，无 CLI 覆盖 | 加 `--slots "普通RC=01_RC;…"`，或明确写"改 `scaffold.py` 里的 SLOT" |
| G4 | ⑧ "改「单价与假定」或「截面参数」即自动重算" | `quantity` 出的表叫「单价与假定」；设计表里那张叫「单价」 | 统一命名，或文档分别写清是哪张表 |
| G5 | ④ `check --model $M` 在 ⑦ 里换成"该柱型目录" | 无问题，仅提示：`check` 的 `--model` 决定读哪套材料等级 | 文档已说明 |
| G6 | 干预点 5 "`src.family=[...]`" | 已实现（`design_src(family=…)`），但 config 里没给示例 | 在 `references/codes.md` 补一个 family 写法示例 |

> 表中 **G1 是流程断点**，优先级最高：没有它，⑤ 到 ⑥ 之间要人工搬数。

---

## 十、进一步阅读

- `references/codes.md` —— 各限值的规范出处、公式、单位约定、材料强度来源
- `references/pricing.md` —— 单价口径、默认配筋假定的来源与替换方法
- `references/gb50936.md` —— 钢管混凝土按 GB 50936-2014 的承载力与稳定系数
- `references/quota-guangzhou.md` —— 广州地区现行定额与信息价口径
- yjk-colmodel 技能 —— `doctor / sect / floors / groups / wmass / res / export / apply / verify / diff`
- struct-report-pptx 技能 —— 汇报 PPT 的表格与图表数据同步

---

## 十一、经济比选工具链（可选）

除上面的「按柱型建目录 → 回写 → 重算」全流程外，本技能还带一条**轻量经济比选**链路：
同一套内力与工程量口径下，直接比较**钢筋混凝土柱（RC）**与**矩形/圆形钢管混凝土柱（CFST）**的造价，
产出可交付的 Excel 对比报告。适合"已经有实算结果、只想快速出经济比较"的场合。

```
设计结果\wpj*.out + <模型>.ydb
  └─ col_data.py    → 柱设计数据.json      # 逐柱段内力 + 层高 + 现状工程量
     cost_model.py  → 造价对比.json        # 选型 + 计价 + 敏感性（GB 50936 控制利用率）
     report_xlsx.py → <项目>_柱形式比选经济对比报告.xlsx
```

```powershell
& $py -X utf8 -B scripts\col_data.py --res <设计结果目录> --ydb <模型.ydb>
& $py -X utf8 -B scripts\cost_model.py
& $py -X utf8 -B scripts\report_xlsx.py --project "<工程名>" --system "框筒" --seismic "二级"
```

- `col_data.py` 也可以从环境变量 `YJK_COL_RES` / `YJK_COL_YDB` 取数据源；分组按柱**平面坐标**现算，不依赖写死的柱号表。
- **缺数据不算成功**：关键字段缺失、某自然层没有 `wpj<自然层>.out`、或整层解析不出柱段时，打印缺项明细并**非零退出**，不写半成品 JSON。
- `cfst_design.py` 是 GB 50936-2014 承载力库，可单独运行做自检；`gz_quota.py` 是广州定额单价表。
- 三份产物（`柱设计数据.json` / `造价对比.json` / xlsx）放在当前目录，便于随工程归档。
