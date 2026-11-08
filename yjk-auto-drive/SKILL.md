---
name: yjk-auto-drive
description: 驱动盈建科（YJK 6.x / 7.x / 8.x）结构设计软件全自动算模型：经官方 YJKSControl IPC 通道零人工点击完成「清场 → 启动 → 新建工程 → 导入模型 → 预处理 → 计算 → 读设计结果」，含单实例隔离、模态框看门狗、总信息（前处理计算参数）按名读写与回读校验，并适配 8.x 的 initConfig/Pid 定向/Invisible 静默/RunYJK/exit。本技能是整套技能的**底座（纯通路，不含业务逻辑）**，其余技能都通过它驱动 YJK。当用户要求"自动跑 YJK""驱动 YJK 计算""批量算模型""导入 ydb 并计算""无人值守跑结构计算""检查 YJK 环境""改总信息/抗震参数"时使用。
agent_created: true
---

# YJK 自动驱动（自动建模 / 迭代计算）

核心是官方 `YJKSControl` IPC 通道：一个 DLL、两个字符串参数，就能让 YJK 执行建模与计算命令。

```
kill 全部 yjks → 确保 YjkLauncher 在跑 → yjks.exe 无参启动
→ IPC 通道自动就绪 → UINew 建工程 → yjk_importydb 导入模型
→ 导入校验（逐表核对 .ydb↔.ymd，不通过就停手）
→ 预处理链 → 计算链 → 读 设计结果\wpj*.out
```

## 版本适配（6.x / 7.x / 8.x）

| 能力 | 6.x | 7.x | 8.x |
|---|---|---|---|
| `RunCmd` IPC 通道 | 是（用 7.1 仓库 DLL） | 是 | 是（安装根 `YJKAPI.dll`） |
| `Config.ini [YJKSControl] Flag=True` | 是 | 是 | 是 |
| `initConfig(ControlConfig)` | — | — | **必须先调** |
| `ControlConfig.Pid` 定向 / `Invisible` 静默 | — | — | 是 |
| `RunYJK(exe)` 由 API 启动 | — | — | 是 |
| `exit()` 优雅退出 | — | — | 是 |
| `SelectYjkProcess` / `IPC_Pipe` / `IPC_ShareMem` | — | — | 是 |
| `yjks_pyload` 依赖脚本 | 是 | 是 | 是（用安装目录 Python） |
| 8.x 新构件 API | — | — | 是 |

`paths.py` 自动按主版本选 DLL：**8.x → 安装根 `YJKAPI.dll` 优先**；7.x → 技能
`assets/` 的 7.1 仓库版；6.x → 同样用 7.1 仓库版（6.1 安装目录没有可用的控制 DLL）。
`status` 打印 DLL 能力矩阵，`probe` 对版本不匹配给出提示。

**8.x 用法差异**

- **启动路径不同（实测 8.1）**：6/7 靠 `Config.ini Flag=True` 自动开通道，再用
  `Global\ShareMemoryEvent` / `Global\WaitResaultEvent` 判就绪；**8.x 没有这两个事件**，
  通道由官方 API 建立。`boot_yjks()` 检测到主版本 ≥8 时自动改走：
  `initConfig(Version, Invisible, Pid=-1)` → `RunYJK(yjks.exe)` → 等进程 →
  `initConfig(..., Pid=真实pid)`。所以 8.x 不需要人工敲 `yjksipccontrol`。
- **先 `initConfig` 再发命令**：`host` 在建工程前自动执行 `Client.configure()`；
  官方 test04 明确要求，跳过时 8.x 命令可能静默不执行。
- **接管已在运行的实例**：`host ... --pid <PID>`（不杀、不启动、不登记自有实例）。
- **静默计算**：`--invisible`（`initConfig(Invisible=True)`），收尾可用 `Client.close()` 发 `exit`。
- **8.x 的 `RunCmd` 返回 void**（没有字符串结果）。成功判据仍只认文件 mtime（铁律 4）。
- **依赖 YJK 运行时的 Python 脚本**：用 `yjks_pyload "<py路径>,<函数名>"`，
  解释器用安装目录内置 Python（`paths.find_yjk_python()` 自动定位）。

8.x 新增建模/设计能力（命令与表结构见 `references/commands.md`）：隔震支座/特殊节点
（`SpNode` + `SpNLProp`）、消能器（`XNQ_arrange` / `XNQSectCreateInfo`）、填充墙
（`FillWall_Def` / `FillWall_arrange`）、加固（柱/梁/钢结构）、楼梯（`Stair_Def` /
`stair_arrange`）、梁加腋（`BeamJYSect_Def` / `beamjy_arrange`）、板加腋
（`SlabJYSect_Def` / `slabjy_arrange`）、蒙皮（`SkinCreateInfo` / `skin_arrange` /
`skinLoad_arrange`）、层间板（`MidSlabCreateInfo`）、柱帽（`ColCapSect_Def`）、
基础建模与设计结果（JCCAD，见下面「基础（JCCAD）模块」一节）、智能辅助设计模型映射（`Hi_ModelMapping`）、联动回写
（`Hi_AddToAndReadYjk` / `ReflecToYJK` / `RefreshToYJK` / `ReflectAndCreateYDB`）、
有限元时程后处理（`Hi_API_YJKDTReport`）。

## 第一步永远是环境自检

```powershell
$py = "<带 pythonnet 的 python.exe>"       # 见下面「用户需要做的基础工作」
& $py -X utf8 -B "<本技能>\scripts\yjk_probe.py"
```

它逐项检查并直接写出怎么修：Python/pythonnet、YJK 安装位置、Config.ini 的 Flag、官方客户端 DLL、yjks 实例数。全绿即可跑，缺项按提示处理后重跑。`--fix-config` 自动补 Config.ini，`--runtime` 真启动一次做活体连接测试。

改代码后先跑离线自检（不需要 YJK，秒级）：

```powershell
& $py -X utf8 -B "<本技能>\scripts\selfcheck.py"
& $py -X utf8 -B "<本技能>\scripts\selfcheck.py" --golden <算过的工程目录> --期望 <基准.json>
#   首次用 --dump 存基准；以后改代码跑一遍即可发现有没有把结果改坏
```

覆盖宏展开 / 窗口标题解析 / 实例分类 / 注册表 / 预检分支 / 收件箱归档与闸门等不依赖 YJK 的判断逻辑。

## 用户需要做的基础工作（新电脑必读）

只做一次，十分钟。详细版见 `references/setup-checklist.md`；
**逐项打勾、含验收标准与失败对照的版本见 `references/deployment-checklist.md`**（新机器照它走）。

| # | 要做的事                                            | 为什么                           | 怎么确认                           |
| - | ----------------------------------------------- | ----------------------------- | ------------------------------ |
| 1 | **装 YJK（6.1+ / 7.x / 8.x）并能正常打开一个工程**                 | 驱动的前提；首启需能正常进界面               | 手动开一次 YJK 能进界面                 |
|   |                                                 |                               |                                |
| 2 | **两处 `Config.ini` 补 `[YJKSControl] Flag=True`** | 只有这样才能"启动即开 IPC"，**免去人工键入命令** | `yjk_probe.py` 该项显示 OK         |
| 3 | **准备一个带 pythonnet 的 Python 环境**                 | 用 `clr` 反射调用官方 DLL            | `python -c "import clr"` 不报错   |
| 4 | **取得官方客户端 `YJKAPI.dll`**（官方仓库 7.1 分支）           | IPC 调用的入口                     | 放进技能 `assets/`，或设 `YJKAPI_DLL` |
| 5 | **保证全机只有 1 个 yjks.exe**                         | 多实例抢全局事件 → 命令静默失效             | 每次跑前 `yjk_auto.py kill`        |

第 2~4 项都能一键或半自动完成：

```powershell
& $py -X utf8 -B "<本技能>\scripts\setup_env.py"          # 自动建隔离环境并装 pythonnet/openpyxl/psutil
& $py -X utf8 -B "<本技能>\scripts\yjk_probe.py" --fix-config
& $py -X utf8 -B "<本技能>\scripts\yjk_auto.py" probe --fix-config
```

第 4 项的取件方式见 `assets/README.md`：`assets/` 已内置一份可用的 `YJKAPI.dll`（来自 gitee `yjk-opensource/csharp-yjks` 7.1 分支），换机器时把 `assets/` 一起拷过去即可；来源受限就从官方仓库取同名文件放进去。

DLL 来源按版本区分（`paths.py` 会自动挑，通常不用手工指定）：

| YJK 版本 | 首选 DLL | 说明 |
|---|---|---|
| 6.x | 技能 `assets/YJKAPI.dll`（7.1 仓库版） | 6.1 安装目录没有可用的控制 DLL |
| 7.x | 技能 `assets/YJKAPI.dll`（7.1 仓库版） | 安装目录 `STCAD\YJKSControl.dll` 可兜底（3 参 RunCmd） |
| 8.x | **安装根 `YJKAPI.dll`** | 只有它含 `initConfig`/`RunYJK`/`exit` 等 8.x 新 API |

## 命令

```powershell
$D = "<本技能>\scripts"
& $py -X utf8 -B "$D\yjk_probe.py"                     # 环境自检（先跑这个）
& $py -X utf8 -B "$D\yjk_auto.py" status                # 实例分类/命令行/IPC 通道
& $py -X utf8 -B "$D\yjk_auto.py" kill                  # 无差别清全部（人工逃生口，自动化别调用）
& $py -X utf8 -B "$D\yjk_auto.py" host `
      --dir <工作目录> --name <工程名> --import <模型.ydb> --prep --calc `
      [--inbox] [--stay N] [--clean-orphans] [--keep] [--reuse]
```

`host` 是主力：一条命令跑完「隔离预检 → 启动 → 建工程 → 导入 → 导入校验 → 预处理 → 计算 → 列结果 → 只清自有实例」。
**导入校验不通过时 `host` 以非零退出码（2）收尾**，自动化调用方（如 `run_all_yjk.py` 就是拿 rc 当判据的）不会再把"导入空模型 + 白算一轮"当成功。

`--keep` 与 `--reuse` 是两件不同的事，别混：

| 开关 | 管的是什么 | 什么时候用 |
| --- | --- | --- |
| `--keep` | **收尾不杀自有 yjks 实例**（默认收尾清掉）。它管的是"进程留不留" | 想跨会话保留常驻实例（下次 host 会把登记里的它当残留清掉） |
| `--reuse` | **允许在已有 `<工程名>.yjk` 的目录里开工**（默认**拒绝**）。它管的是"目录能不能复用" | 迭代时不想为每轮新建目录；配合 `--keep` 才谈得上"接着上一轮跑" |

`--reuse` 的默认拒绝是老规矩：目录里 `.yjk` 在、新实例并没打开它时直接 `UINew` 会**覆盖**已有模型（且带文档启动建不起 IPC 通道，硬性约束 1）。现场为绕开它连开了五个目录（`YJK_run` / `YJK_base` / `YJK_run2` / `YJK_run3` / `YJK_run4`）。加上 `--reuse` 后行为是诚实的：

```
--reuse：工作目录里已有 Core28.yjk —— 将**打开/覆盖**这个已有工程
   现有文件: ...\Core28.yjk（2026-09-25 21:20:11，917504 字节）
   ★ 这一步之后该工程会被 UINew 重新建/打开，旧模型与旧设计结果可能被覆盖；
     确认没有另一个实例打开它（已查：无）。
```

它同时补上了原规则**真正**要防的那件事：开工前用 `env.py` 的窗口标题探测确认这个工程**没有正被别的实例打开**（两实例同抢一个库 → 界面与库不一致，甚至把 yjks 弄崩）；查到就拒绝，并告诉你去 `status` 看 pid、`close --pid <PID> --yes` 关掉它。

迭代轮之间**不要重跑 host**：工作目录里已有 `<工程名>.yjk` 时 `host` 会**主动中止**（避免覆盖模型、避免误读陈旧结果）；跨会话继续用 `--keep`，确实要同目录重开才加 `--reuse`。

### 实例隔离：只操作自有实例

**命令无法按 PID 定向** —— 两个 IPC 事件是 `Global\` 命名对象，谁先抢谁执行；所以"多实例共存还能安全操作"**不成立**，多实例 = 命令应答不可信。因此本工具是「独占租约 + 只动自有实例」，实例分四类：

| 类别         | 判定                                               | 处置                                                        |
| ---------- | ------------------------------------------------ | --------------------------------------------------------- |
| **自有**     | 登记在 `~/.yjk-auto/own.json` 的 PID（`host` 启动后自动登记） | 只用它、收尾只清它（`--keep` 可跨会话保留）                                |
| **你在用**    | 有 yjks 类主窗口，且不在登记里                               | **一律不碰**。开工会拒绝、运行中会停手；同时**提示关哪个、怎么关**（见下）                 |
| **无主窗口残留** | 无 yjks 类顶层窗口（`YJKAPI.init`/`WinExec` 拉起的）        | 默认也不碰；要清需显式 `--clean-orphans`（或 `yjk_cleanup.py --apply`） |
| **自有已消失**  | 登记中的 PID 不在了                                     | 迭代中止并报告，**不再向任何实例发命令**                                    |

`status` 按「自有 / 你在用 / 无主窗口残留」三类分列，并打印命令行与所打开的工程。**任何时候都不会去关你自己的 YJK**，只会告诉你关哪个、怎么关。

`yjk_cleanup.py` 的判据统一到 `instances()`：只有 orphan 是清理对象，其余一律不动。实例枚举不可用时它报 **rc=2**，而不是打印"没有需要清理" —— 后者会把"看不到"说成"没有"。

### 发现你在用的实例时：提示 + 可选等待 + 精确关闭

```
1) 提示：打印该实例的 PID / 窗口标题 / 正打开的工程 / 完整命令行，
   并给出可直接粘贴的关闭命令：  yjk_auto.py close --pid <PID> --yes
2) 默认**拒绝开工且不碰它**（本次不登记、不启动、不杀任何实例）
3) 想省掉"关了还要重跑"：  host ... --wait-others 600
   → 每 15 秒重新提示一次，你关掉它就**自动继续**，不必重跑
4) 确认要关且愿意承担"中断该会话"：  yjk_auto.py close --pid <PID> --yes
   （与 `kill` 不同：必须点名 PID、先打印关的是什么；非自有实例不加 --yes 绝不关）
```

**连续迭代用收件箱**（不重启 YJK）：

```powershell
# 终端 A：常驻托管，开收件箱（自有实例全程存活，迭代期间不杀）
& $py -X utf8 -B "$D\yjk_auto.py" host --dir <工作目录> --name <工程名> --inbox --stay 3600
# 终端 B：一整轮迭代（宏）
& $py -X utf8 -B "$D\yjk_auto.py" send @recalc <新截面.ydb> --dir <工作目录>
```

`--exit-when-idle`（**默认 900 秒**）让收件箱**空闲到点就自动收尾**并清场，不必守着 `--stay` 到期；空闲期间每 60 秒打一行心跳（`[空闲 Ns] 队列 M 条；距自动收尾 Xs`）。要一直守着就 `--exit-when-idle 0`。`exit` / `quit` 指令**优先于隔离闸门**处理 —— 否则有外部实例时会话永远退不出。

收件箱每行格式 `HHMMSS|命令|参数`，回执格式 `序号|命令|返回值|变更=文件列表`。**回执里的"变更"是文件 mtime 差集——这才是真凭据**，不要看返回值。

### 会话目录错配（收件箱每轮命令前自动判定）

收件箱盯的是 `--dir`，但"当前打开哪个工程"是 YJK 自己的状态。有人用 `UINew` 在**别的目录**建了第二个工程，于是 `yjk_importydb` 返回 `OK(6.4s)`（它确实成功了——成功在**另一个目录**），而文件变更闸门盯着 `--dir` 什么都没看到 → 报成"导入很可能没生效"并**跳过本轮剩余 11 条命令**。提示指向导入而不指向目录，很难查。

现在每条命令执行前（**在拿"有没有文件变化"当判据之前**）先从窗口标题读出工程路径，不一致就明确停手并报出两个路径：

```
!! 会话目录与 YJK 打开的工程目录**不一致** —— 本轮命令不可信，已停手
!!   会话监视的目录 (--dir): <会话目录>
!!   YJK 实际打开的工程     : <工程目录>\P2（pid=12345）
!!   工程所在目录            : <工程目录>
!! 处置（二选一，别续用这个会话）：
!!   结束本会话（收件箱发 exit），改到工程自己的目录重开：host --dir "<工程目录>" ...
!!   或让 YJK 回到 --dir：在欢迎页用 UINew 建到 --dir（host 就是这么做的）
```

**读不到工程路径时不猜**（欢迎页标题没有路径、窗口刚创建时标题还读不出来），按"对得上"处理，交给后面的文件变更闸门兜底。

### 迭代闭环

```
@back  回「构件布置（建模调整界面）」   ← 计算链末尾停在「设计结果」标签，
       而 yjk_importydb / yjk_repair 等属建模模块命令，改模型前必须先切回来
yjk_importydb <新截面.ydb>            ← 其它技能产出的新模型库（同结构、只换截面/等级）
@prep  修复 → 保存 → 形成节点 → 形成楼板
@calc  建模→前处理过渡 → 生成数据+全部计算 → 切到设计结果
```

`@recalc [新模型.ydb]` = 上面四条合成一轮；不给 ydb 参数就只重算当前模型。可用宏：`@back` / `@prep` / `@calc` / `@recalc` / `@takeoff`。

**算量链只走 `@takeoff`（顺序是硬性的）**：

```
& $py -X utf8 -B "$D\yjk_auto.py" send @takeoff --dir <工作目录>
混凝土工程量   SetCurrentLabel IDModule_Layer → yjkconcreteStat_statCom
施工图         IDDTL_DETAIL_SLAB/BEAM/COLUMN/WALL → 板/梁/柱/墙 绘新图
钢筋工程量     SetCurrentLabel IDQUANTITYLIST_DETAIL → DtlRC_SSSE / …BeamSteelSpecExcel / SSCE / SSWE
```

**顺序不能换**：`yjkconcreteStat_statCom`（混凝土统计）归属**建模模块**（`HelpRef` 就是「楼层组装\18工程量统计」），切过去会**冲掉施工图上下文**。若它排在出图之后，钢筋统计里所有 `DtlRC_*` 会退化成 `OK(0.0s)`——**不产出任何文件，也不报任何错**，只能靠"零产出"反推。宏把它固定成「混凝土统计 → 出图 → 钢筋统计」，理由记在 `TAKEOFF_CHAIN` 的注释里。`DtlRC_*` 前必须先 `SetCurrentLabel IDQUANTITYLIST_DETAIL`；`@takeoff` 之前要先 `@recalc`（施工图与钢筋统计都吃设计结果）。

**三条使用纪律**：

- **先启动会话，再 send**。启动前预置在收件箱里的命令会被**归档**（见下），不会执行。
- **收件箱启动时会归档历史内容**（`_yjk_inbox.txt.<时间>.bak`）：`send` 是追加写，不归档的话上一轮留下的命令会被逐条重放。
- 隔离闸门/前置校验触发时是**跳过本轮、会话继续**（不是结束会话），修正后可再发新命令；闸门结果会写进 outbox（`序号|命令|原因|变更=-`），便于事后核对。

**重导入到已打开的工程是可行的**：`yjk_importydb` 只改动指定截面的柱段，其它标准层不动；混凝土等级跟随新 `.ydb` 的 `tblStdFlr.Para`（idx 4 柱 / idx 6 墙）。

### 耗时量级参考（用来判断命令是否真的执行了）

下面左列是**一次示例测量**（AMD Ryzen AI 7 H 350 / 16 核，28 层框架-核心筒：672 节点 / 448 柱段 / 784 梁段 / 224 墙段 / 336 板），右列是旧文档给的经验值。两者差约 5 倍 —— **量级强依赖机器与模型规模，这里只给一个可对照的样本，不是通用常数**：

| 步骤 | 示例测量（28 层） | 旧文档 | 备注 |
| --- | --- | --- | --- |
| 切到建模标签 `SetCurrentLabel(IDModule_Element)` | 1~7 s | — | 每轮固定开销 |
| 重导入 `yjk_importydb` | 5~12 s | 5~10 s | 随模型大小 |
| 修复 + 保存 | 1~2 s | 约 3 s | |
| 形成节点/楼板 + 前处理过渡 | 1~2 s | 5~6 s | |
| 切到前处理 `SetCurrentLabel(IDSPRE_ROOT)` | 3~5 s | 约 7 s | 每轮固定开销 |
| **算（`yjkdesign_dsncalculating_all`）** | **约 38 s** | 4~5 min | 是单轮的大头（约 60%） |
| **单轮 `@recalc` 合计** | **64~72 s** | 约 5 min | |

> **别按旧文档把超时设成 10 分钟**：一轮就一分多钟，超时给太大只会让"弹了模态框/卡住"晚 10 分钟才发现。**按「你自己的实测 × 2~3」设** —— 上面这个样本一轮给 **150 s** 就够。判断是否真算完，优先看 `_yjk_outbox.txt` 的回执（命令级、带时间戳），比用 `设计结果\wmass.out` 的 mtime 轮询更准：mtime 轮询每轮都要过冲几秒，还分不清"算完了"和"算失败了"（失败也会写文件）。量级随机器与模型规模变化，**以你的实测为准**。

## 基础（JCCAD）模块：`jc.py` / `jc_react.py`

基础（筏板/承台/桩）**不能**走 `host` 那条链 —— `UINew` 建空工程 + 导入 ydb 建不出基础模型。
基础库 `Jccad_0.ydb` 跟着工程一起打开，所以必须**带着 `.yjk` 启动**，再 `initConfig(Pid)` 把 IPC 定向过去：

```powershell
& $py -X utf8 -B "$D\jc.py" --dir "<工程目录>"             # 生成数据 + 基础计算 + 判结果
& $py -X utf8 -B "$D\jc.py" --dir "<工程目录>" --gen-only   # 改了桩/筏板后只生成数据
& $py -X utf8 -B "$D\jc.py" --dir "<工程目录>" --pid <PID>  # 接管已打开该工程的实例（不启动、不杀）
& $py -X utf8 -B "$D\jc_react.py" --dir "<工程目录>" --kp <单桩竖向刚度>
```

- 链条：`SetCurrentLabel JCCAD_RESULT` → `BaseDraw_GenData_script` → `BaseDraw_BaseAnalysis`（8.1 实测：切标签 11.5~31 s，生成数据 4~11 s，计算 4~6 s）。
- **装哪个版本要自己点**：`paths.find_yjk_install()` 可能命中 `YJK_DIR` 指的 7.x（本机就是 7.1），
  而基础链只在 8.1 上验过 → 用 `--root "<8.x 安装目录>"`；版本 <8 时脚本**直接拒绝**（要试加 `--force`）。
- 判据三条齐看：`计算分析.log` 末行「计算正常，未发现问题」（**GBK**）+ `jccad.result`/`CAL_MID.DIS` 的 mtime 晚于本轮开始 + `CAL_MID.DIS` 字节结构对得上。
- **8.1 实测：带文档启动后 IPC 可用**（`SetCurrentLabel` 真执行 11.5 s）。硬性约束 1 说的"带文档启动失效"针对**建模命令**，不要据此推断基础命令也失效；判据永远是"耗时 + 文件 mtime"。
- 逐桩反力：`Jccad_1.ydb` 的 `PileForce` 是**空表**，`Jccad_Result_New.ydb` 不一定生成，所以从 `CAL_MID.INP/.DIS` 反算：`R = −Kp × Σ(四节点形函数×UZ)`。`Kp` 是单桩竖向刚度，**只能从基础计算书取**——用"Σ弹簧反力 = Σ桩反力"反推会偏大（弹簧里同时含筏板底土弹簧）。
- 改 `Jccad_0.ydb` 的 `app_Pile`（`DaisFlag=-1` = 板下桩）之前**先关掉打开该工程的 YJK**，否则写入会被内存副本覆盖。
- **基础模块的备份/图形文件会把旧模型恢复回来（已验证，最坑）**：`基础备份\`、`<工程名>_F.yjc`、`.tmp`、`.yg`、`.ygt`、`.ygjcbak`、`Jccad_0_ydb.dat` 都是它的模型与恢复源。
  只改 `app_Pile` 后，用户一进基础模块并保存，就会把 `Jccad_0.ydb` 写回旧桩，**并把桩顶 `z` 写成 0**（实测两次：54 桩被写回 279/56、z 全 0）。
  可靠做法是把这些文件**整体移出工程目录**（不是改名留在原地），再重开工程：实测移出后界面显示与 ydb 一致。现成脚本 `pile-layout-opt\scripts\prep_model.py --dir <工程目录>`。
- 移出后若用户又打开并保存了基础模块，`z` 会被 GUI 统一重算（实测 54 桩全部变 −13700）；要保留原桩顶标高就在保存后重算复核。
- `.yjc` 可以缺席：工程没有 `_F.yjc` 时照样能打开，`--gen-only` / `--output` 也照常跑通，且**不会重建它** → 它是 GUI 侧数据，不是驱动链的输入。
- `--gen-only` 结束时会重写 `Jccad_0.ydb`：桩数/桩位应保持不变；若变了，就是上一条那几个 GUI 文件把旧模型带回来了。
- **不清旧结果会直接复用**：改桩后必须删 `基础计算及结果输出\jccad.result`、`jccad.ydb` 与旧 `*.out`，否则"改了没反应"。
- 逐桩反力更省事的来源是 `基础计算及结果输出\YJK-F桩承载力验算.out`：按 `ZH-n` 分块解析 `组合号 Nk Ra`，`ZH-n` 与 `app_Pile order by ID` 一一对应。
  解析要在章节标题（`一、`/`二、`/`三、`）处截断，否则后续表格的数字会串进来，峰值判错。
- 布桩优化（变距/减桩/复核）交给 `pile-layout-opt` 技能，本技能只负责驱动通道。

### 基础模块 8.1 二次开发 API（`JcDataFunc`）

- **8.1 SDK 不在 PyPI 包里**：PyPI 的 `YJKAPI` 包可能对应旧版 DLL，写出的 ydb 在 8.1 里导入后可能空跑；要用 Gitee `yjk-opensource/yjkapi_-python` 对应版本分支的 `SDK` 包（解压出 `python310` + `YJKAPI`）。运行时把 `<YJK安装目录>` 加入 `PATH`，工作目录用纯 ASCII 路径。
- **`JcDais_App` 只加不删**：在同一柱位新增承台时，`app_dais.Remove(old)` 可能不生效，导致同一柱位出现两座承台。改承台优先只改原承台的 `kind`/`dBotElevat`/`idaispilelen`；改完必须核对 `app_dais` 总数与 `group by nj having count(*)>1`。
- **`jccad_read_by_ydb` 只导模型、不保组合**：导入后 `LoadZhuHe` 会减少、恒载可能被清零；如发现组合缺失，先从 API ydb 回填 `Loads`/`LoadZhuHe`/`CalPara`，再跑 `jc.py`（不要再 import）。
- **标高体系要统一核对**：筏板顶/底、承台顶/底（底 = 顶 - 台阶高之和）、承台桩长（按统一桩端反算）、板下桩顶/桩长要能对上；不要把不同基准的 `z` 混用。
- 细节、SQL、脚本与验收顺序见 `references/foundation-jccad-8.1-api.md`。

命令全表、耗时、`YJK.CUI` 反查法与 `CAL_MID.DIS` 格式见 `references\commands.md` §6。

## 总信息（前处理计算参数）—— 最容易静默失真的一环

**YJK 新建空工程的默认总信息是**：

```
结构体系 = 框架结构     设防烈度 = 6 度 (0.05g)   场地类别 = Ⅰ1
地面粗糙度 = A         修正后基本风压 = 0.10 kN/m²  剪力墙抗震等级 = 三级
```

拿这套默认值去算一栋百米级框架-核心筒，等于**基本不算抗震、不算风**，但结果文件齐全、数值也"看着正常" —— 属于最危险的一类静默错误。

`scripts/projpara.py` 把官方宏定义（`前处理计算参数宏定义.h`，已随技能包放在 `yjk-dev-refs/06-总信息参数ID表/`）固化成"名字 → ID → 枚举码"，不用再靠"改一行 `tblProjectPara` → 跑一轮 → 回读 `wmass.out`"逐条猜 ID。

```powershell
# 看默认值 / 看某个模型当前的值
& $py -X utf8 -B "$D\projpara.py" read  --db 模型.ydb
# 按名改（枚举可以写中文名）
& $py -X utf8 -B "$D\projpara.py" set   --db 模型.ydb `
      --set 结构体系=框筒结构 --set 设防烈度="7 (0.1g)" --set 场地类别=III `
      --set 地面粗糙度=B --set 基本风压=0.60 --set 周期折减系数=0.90 `
      --set 特征周期=0.45 --set 多遇地震影响系数最大值=0.08 `
      --set 框架抗震等级=二级 --set 剪力墙抗震等级=二级
# 回读校验：库里写的值，实算时真的生效了吗？
& $py -X utf8 -B "$D\projpara.py" check --db 模型.ydb --res <工程目录>
```

**两条必须记住的编码规则**（都是实测出来的，想当然会写错）：

1. **枚举型参数值 = 参数ID × 100 + 枚举序号**，数值型直接写数值；但**布尔/组号类参数是直写**（`考虑偶然偏心` 写 `1`，`设计地震分组` 写 `1`）。
2. **枚举基 ID 未必等于参数 ID**：抗震等级族里 `701 框架 / 702 钢框架 / 703 剪力墙` **共用 `701` 作枚举基**（70101 特一 … 70104 三级），所以"剪力墙二级"要写成 `703 = 70103`，按"ID×100+序号"会写错。

**`check` 不是可选项。** 实测教训：某一项在 `tblProjectPara` 里写对了、YJK 也照常出结果，但那一项**根本没被采用**（当时把"结构体系"写到了 ID=201，`wmass.out` 里仍然是"框架结构"，直到逐条回读才发现）。`check` 按 `wmass.out` 的「设计参数输出」逐项与库里的值比对，把这类"写了没生效"直接列出来。

## 模态框看门狗（内建）

**`host` 会自动拉起看门狗**（`dlgwatch.py`，`start_dlgwatch()`，在启动 `yjks.exe` **之前**拉起）。

- YJK **出错时**会弹模态确认框（如「计算分析失败」）。模态期间 yjks 主窗口被 `Disable`，**IPC 命令从此不返回** —— 表现为"命令挂死"，且没有任何输出。框不处理掉，命令就一直挂到超时。
- 唯一有效应答：向对话框发 `WM_COMMAND`，`wParam=控件ID`、`lParam=按钮 hwnd`。`BM_CLICK` / 键盘消息 / `WM_CLOSE` 全部无效。
- **作用范围只有自有实例**：`pid=None`（还没拿到自有实例）阶段**只登记不动手**，一个按钮都不点；`own_claim` 之后 `narrow(pid)` 收窄到自有实例，此时才按 `RULES` 应答。看门狗不会去盯全机所有 yjks.exe 并应答 —— 那会把别人正在用的 YJK 的框也答掉。
- **未命中 `RULES` 的对话框默认不应答**（`DEFAULT = None`）：只登记 + 打一行日志，框留在那里由人处理。盲答一个看不懂的框，等于替本包没理解过的事替用户确认。
- 授权/许可类框**永不**自动应答（见下）。
- `_answer()` 只在 `PostMessageW` 真的返回非 0 时才把答复记进 `seen`；发送失败进 `failed` 并打一行日志 —— 框可能还挂着，不能当"已处理"。
- 看门狗会把拦下的**错误弹框**留档；`host` 收尾时会打印 `!! 本轮共拦下 N 个错误弹框`。**看到这一行就说明有步骤真的失败了，别只看 `RunCmd` 的 `OK` 应答。**
- **启动阶段弹出的框会一直挂着，命令会等到超时** —— 这是有意的 fail-loud，不是"自动应答"：启动期的框没有任何依据替用户作答。
- 手动用（不经 `host`）时：`python dlgwatch.py [pid]`。

### 授权/许可类对话框：不自动应答，暂停等用户处理

**看门狗对授权类对话框一个按钮都不点**（只登记），由 `host` 驱动「暂停 + 提示」。

不能盲答的原因（实测）：网络许可不可达时 YJK 每 ~2 秒弹一次「授权」框，看门狗回「是」→ YJK 被引导去走**「单机码激活」**→ 再弹「序列号输入不正确」→ 再回「是」……**对话框无限循环、IPC 通道永远起不来**，日志里只看到一串「回是」，看不出真因是**许可没连上**。

`host` 一看到授权框就

1. 打印醒目提示 + 排查清单（VPN / `lic.yjk.cn:8081` / 许可被占满 / 授权配置）；
2. 在工作目录写标志 **`_yjk_license.need_user`**（供人/编排发现）；
3. **继续等**（默认上限 30 分钟），你修好许可后通道一通就**自动继续** —— 不用重跑、不用改任何东西。

开关：`--on-license {pause,fail}`（默认 `pause`；`fail` = 立刻以**退出码 6** 结束）、`--license-timeout <秒>`、`--wait-ipc <秒>`。

**怎么看出来「它正卡在授权上」**（标志是**跨进程唯一**的信道 —— 宿主内存里的 `_LICENSE_BLOCKED` 别的会话读不到，所以别去猜）：

```powershell
yjk_auto.py status --dir "<工作目录>"      # 人看：标志路径 + 写入时间 + 当时对话框内容
yjk_auto.py send   --dir "<工作目录>" "@calc"   # 编排看：未就绪时会**先判授权**并点名原因
```

`status` 不给 `--dir` 时查 `own.json` 里登记的工作目录；`send` 命中授权时退出码仍是 **2**（fail-closed）、**不写收件箱**，并提示「许可恢复后不用改脚本，重跑 host 即可（就绪时会自动清掉标志）」。标志用 `utf-8-sig` 读：用户拿记事本改过（带 BOM）也不会打出乱码方块。

### 退出码（编排器按这个判成败）

| 码 | 含义 |
|---|---|
| 0 | 干完了且没登记到失败 |
| 2 | **本轮确认为失败**（导入校验不过 / 通道没起来 / 工程没就位…） |
| 3 | **预检拒绝**：一个动作都没做（有你在用的实例 / 有残留 / 另一 host 在跑） |
| 5 | **无法判定**：证据缺失。目前只有一种 —— 看门狗的对话框监视起不来，于是"没弹框"与"没人看着"不可区分，相关命令的结果不可信 |
| 6 | **授权/许可问题** |

> 以前 preflight 拒绝也返回 **0**，日志写着「本次未做任何操作」—— 按退出码判定的编排会把「什么都没做」当成成功。现已区分。

### 收件箱「就绪」判据（别只看文件在不在）

`_yjk_inbox.ready` **会残留**（host 被硬杀时收尾不执行）。只判存在的话，`send` 会返回 0 并把命令写进收件箱，**却没有任何进程在读它** —— 静默丢弃。现在 `send` 逐条校验：内容首字段是不是 PID · 该 PID 是不是**活着的本包宿主** · **心跳**（mtime，由收件箱循环每 2 秒续写）是否新鲜；任一不过就 **rc=2 拒绝且不写入**。

## 硬性约束

| # | 约束                             | 原因                                                                                                                                                                                                       |
| - | ------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1 | **yjks 必须无参启动**（**基础 JCCAD 是例外**：必须 `-open <工程>.yjk` 带文档启动，见「基础（JCCAD）模块」） | 建模：带 `.yjk` 或 `-open <路径>` 启动时，**工程其实并没打开**（窗口标题只到目录级、不含工程名），所有建模命令退化成 `0.1s` 秒回且不写盘；但 **IPC 事件照样会建立**（约 35s，比无参启动的 12~16s 慢）——所以"事件在不在"不能当判据。`Flag=True` 只在无文档启动时生效。详见 `references/troubleshooting.md` §11 |
| 2 | **yjks 不会随宿主退出而回收，必须显式清**      | `host` 进程退出后 yjks 仍存活（`DETACHED` + `CREATE_BREAKAWAY` 也留得住）。故 `host` 开工先清、收尾在 `finally` 里再清。需要连续下命令时用常驻 `host --inbox`（免得反复重启，每次 12s + 启动开销）                                                               |
| 3 | **全机只能有 1 个 yjks.exe；且只动自有那个** | 多实例抢 `Global\ShareMemoryEvent` / `Global\WaitResaultEvent` → 症状是"有 Success 应答但命令不执行"。命令**不能按 PID 定向**，所以只能靠"独占"：见上面「实例隔离」——只清 `own.json` 里那个，发现你在用的实例就拒绝/停手，**绝不去关你的**                                   |
| 4 | **成功判据只认客观证据**                 | 文件 mtime / 窗口标题 / CPU 增量。`RunCmd` 正常返回 + Success 应答在多实例下照样出现，不能作依据。**"两个 IPC 事件存在"同样不算证据**——带文档启动的实例也会建事件（约束 1），却根本不执行命令                                                                                 |

## 原生 DLL 搜索路径（已修复，别改回去）

**症状**：建模时弹出 YJK 自己的模态框

```
未能加载到yjkTransYDB.dll或其依赖项
```

然后**进程永久挂住** —— 不是 Python 异常，`try/except` 拦不住，超时也杀不干净。

**真因**：`column-section-opt/scripts/driver.py` 里曾经这样写：

```python
try:
    os.add_dll_directory(sdir)      # ← 返回值没有保存
except Exception:
    pass
```

`os.add_dll_directory()` 返回的 `DllDirectory` 对象**被回收时就会 RemoveDllDirectory**：返回值没人接，语句一结束目录就被移出搜索路径 → YJK 原生代码 `LoadLibrary("yjkTransYDB.dll")` 找不到文件 → 它用自己的 MessageBox 报错，于是挂死。

**修法**（已在 `driver.py` 的 `pin_native_dll_dir()` 里落地，三重保险）：

1. **把句柄存到模块级列表**（`_DLL_HANDLES.append(...)`）—— 这是关键；
2. `SetDllDirectoryW(dir)` 加进程级默认目录（老式 `LoadLibrary` 也认）；
3. 用 ctypes 把 `ypGeo / yjkSPara / YJK_SQL / yjkCadNewData / yjkTransYDB` 按**绝对路径**预加载一遍。

> 同一份知识早已存在于 `floor-system-comparison/scripts/yjk_api.py` 的 `_DLL_HANDLES` 注释里（"保持 os.add_dll_directory 句柄存活，不能回收"），只是没传播到 `driver.py`。**改这类共享基础设施时，请两个技能一起看。**

**怎么确认它现在是好的**（在底座技能里就能验，不需要起 YJK 会话）：

```powershell
& $py -X utf8 -B "<column-section-opt>\scripts\driver.py" createydb
# 期望：CreateYDB 探测：**OK**（写出了 N 字节的 probe.ydb）
```

**底座实测**：

```
CreateYDB 探测：**OK**（写出了 925696 字节的 probe.ydb）
结论：OK（写出 925696 字节）                      # 退出码 0
```

即 `pin_native_dll_dir()` 之后原生 DLL 能正常加载并真的写出库。字节数随骨架模型而变，**看的是 `OK` 不是这个数**。

探测**故意跑在子进程里**：`CreateYDB` 除了挂死，还出现过进程级 access violation（同样拦不住），只有开子进程才能安全地试。

## 命令语义易错点

- `UINew` / `UIOpen`：参数**带 `.yjk`**。**`UINew` 认路径**（能在指定目录建工程）；**`UIOpen` 忽略路径**（只在欢迎页开出空工程，且此后命令全部退化 0.0s 秒回无效）。→ 「打开已有模型」的正确做法是 `UINew` 建工程 + `yjk_importydb` 导入模型。
- `yjk_opennew` / `yjk_new`：参数**不带 `.yjk`**（建模模块命令）；`yjk_importydb` 带 `.ydb`。
- `yjk_opennew` 返回假的 `OK(0.0s)` 且不打开工程，**别用**。
- 导入成功的判据：**`yjk_importydb` + `yjk_save` 之后，逐表核对源 `.ydb` 与写出的 `.ymd`**（`scripts/impcheck.py`，`host` 与收件箱的导入步都会自动跑）。见下面「导入校验闸门」。字节数只能当辅助参考：`save` 会重写模型库（通常多 1 个 sqlite 页 4096 B），`tblSlab` 的合法增删也会改变文件大小 —— 所以"字节数相等"既不是充分也不是必要条件。`host` 仍会打印 save 前的字节数对照（±4096 B 内视为一致），那是给排查用的旁证。
- 参数里**不能有前后空格**；中文字符串要 UTF-8（脚本已处理）。
- `yjkw.py wait` 等文件 mtime 变化时，**等到返回 0、超时返回非零**。别把"超时没等到"当成成功串下去（`wait && 下一步` 会照跑）。

## 导入校验闸门（别只看 `yjk_importydb` 的返回值）

**症状**：一个**半写完**的 `.ydb`（序列化器清完表之后中途抛异常）拿去导入，`yjk_importydb` **照样返回成功**；失败要等到两步之后才现形：

```
设计结果\fea.dat-ERR.txt = 「模型中没有单元数据」   +   分析失败[-45]
```

—— 一整轮计算白跑。同类现场：给 `yjk_importydb` 传**相对路径**时 YJK 按自己的工作目录解析 → 找不到文件 → 弹「文件不存在」框，若被应答放行，导入的是**空模型**，命令同样返回 `OK`。

**判据是逐表行数**（`scripts/impcheck.py`，只依赖 sqlite3）：

| 级别 | 表 | 判法 |
| --- | --- | --- |
| **必判** | `tblJoint` `tblColSeg` `tblBeamSeg` `tblWallSeg` `tblFloor` `tblStdFlr` | 必须**逐表相等**，差一行就不通过 |
| **半判** | `tblLoadSeg` | 源里有荷载的**层**，工程里也必须**逐层**有荷载；条数不定死 |
| 参考 | `tblAxis` `tblGrid` `tblSlab` `tblBeamSect` `tblColSect` `tblProperty` `tblProjectPara` | 只打印，**不判死** |

**`tblLoadSeg` 为什么只判"逐层有没有"**：导入会把"每层一份的荷载定义"并成一份、
重新编号标准层、把条数重排/展开（实测 200 m 塔楼：源 4576 条 / 每层 104 →
工程 10488 条 / 逐层 104~360，一条没丢）。按总条数判会把这种**正常**重排判成
"模型没进来"并中止一轮；要拦的是 `Type` 写错导致的**整批静默丢弃**
（那种情况工程里一条都没有，仍然判不通过）。

**参考表为什么不能判死**（实测值，源 → 导入后）：

```
tblAxis        1008 → 280      YJK 合并共线轴网
tblSlab         336 → 364      YJK 拆分/补板
tblProperty       2 → 5518     save 展开参数表
tblProjectPara 1169 → 1172     save 展开总信息表
```

把 `tblSlab`/`tblAxis` 也要求相等，会把**一对完全正确的导入判成失败**（底座上真踩过：拿 336→364 的好样本死活不通过）。

**顺序要点**：`<工程>.ymd` 是 `yjk_save` 写出来的，导入刚返回时它**还不存在** —— 所以校验必须排在 `yjk_save` **之后**（早于 save 会得到"打不开数据库文件"/找不到 `.ymd`）。

**闸门自触发：不依赖调用方链条里有没有 `yjk_save`**

老版只把待校验的 `.ydb` 记下来，**等 `yjk_save` 才核**；而 `CALC_CHAIN` 里根本没有 `yjk_save` —— 调用方若发 `yjk_importydb x.ydb` 紧接 `@calc`，校验**静默地从未运行**，与"导入后自动跑，不通过就别往下算"的承诺不符（审计 **S11**）。

现在：只要**下一条命令不是 `yjk_save`**，`host` 就会**自动补一步 `yjk_save` 再核**，不通过照样跳过本轮剩余命令（不拿空模型跑一整轮计算）。outbox 里会多一条 `<序号>|yjk_save(自动补)|…` 的回执，便于事后核对。自检 **T32** 守着这条。

**不通过时的行为**（`host`）：打印逐表对照 + 失败块，**中止**（不进预处理/计算链），并**以退出码 2 收尾**——免得自动化调用方把这次当成成功。收件箱里则是"跳过本轮剩余命令、会话继续"，并在 outbox 留一条 `导入校验不通过|变更=-` 的回执。

## 命令执行中实例消失：立刻放弃，别阻塞到超时

`yjks` 被硬杀（或自己崩）时，那条命令的结果事件**永远不会来**。老版会一直阻塞到 `timeout`（收件箱执行路径传的是 **900s**）才返回 —— 而**收件箱循环正卡在这条命令里**，后面写进收件箱的 `exit` 也读不到，于是"收尾"被推迟到超时之后。50 案例 F01/F02 的实测现场：

```
session_close | rc=1 | 180.1s | 未响应 exit，已强制收尾（实例其实早已不存在）
```

现在 `Client.run()` 在等待期间**每 2 秒查一次目标实例存活**（`yjks_pids()`，psapi，几毫秒）：实例一没就立刻返回 `实例已退出(N.Ns，放弃等结果)`，收件箱循环随即回到循环体去处理 `exit`。同时这条会被记进**失败台账**（本轮确实失败了，`host` 收尾给退出码 **2**），outbox 也会留一条结果行 —— 不再是"沉默了 900 秒然后被外力强杀"。这条决定"收尾卡不卡"。

> 已知边界：**0 线程的残壳**（`threads==0`、PID 还在）在 psapi 里仍看得见，会被当成"活着"，那一种情况仍退回到 `timeout` 兜底。自检 **T33** 守着"实例消失 → 立刻返回"这条。

## 绝对不要做

- **不要调 `YJKSControl.init()`**。它会 `WinExec` 再拉起一个无窗口 yjks，正是多实例的元凶。6.1+ 只需 `RunCmd`（通道靠 `Flag=True` 开启）。
- **不要在 YJK 正打开某工程时从外部改它的 `.ymd`** —— 会导致 yjks 崩溃。写盘前先用 `env.py` 看"本工程是否正被打开"。
- **不要指望"自动往命令行键入 `yjksipccontrol`"**：控件找得到、`WM_CHAR` 写得进，但**回车提交不了**；锁屏时（前台 `LockApp.exe`）更抢不到焦点。这条路不通，用 `Flag=True`。

## 跨机器自适应怎么实现的

`scripts/paths.py` 是唯一的"找东西"的地方，**不含任何盘符与用户名**：

| 要找的东西      | 候选链（命中即止）                                                                                       |
| ---------- | ----------------------------------------------------------------------------------------------- |
| YJK 安装目录   | 环境变量 `YJK_DIR/YJK_ROOT/…` → **运行中的 yjks 进程路径** → 注册表 `yjkSoft\*` + 卸载信息 → 各盘按目录名特征扫盘（限深 3 层、剪枝） |
| Config.ini | 环境变量 `YJK_CONFIG` → 安装目录 → `%ProgramData%\yjkSoft\*\Config.ini` 及 `\*\YJKS\Config.ini`          |
| 官方客户端 DLL  | `--dll` 参数 → 环境变量 `YJKAPI_DLL` → 技能 `assets/` → `~/.yjk-auto/` → 安装目录 `STCAD/` → 用户目录里的仓库检出     |
| 解释器        | 环境变量 `YJK_PY` → `~/.yjk-auto/venv` → **通用扫描到的各 agent 托管环境**（枚举家目录一级子目录，认 `~/.<任意名>/venv/Scripts/python.exe` 与 `~/.<任意名>/binaries/python/<ver>/Scripts/python.exe`，不写死厂商名） → `sys.executable` → `py -0p` 全量 → 常见安装路径   |

**客户端签名也自适应**：`YJKIPC.YJKSControl`（官方仓库版，`RunCmd(kw,param)`）与安装目录的 `STCAD\YJKSControl.dll`（`RunCmd(kw,param,out string)`）都能用，`Client` 自动挑重载。安装目录的 `STCAD\YJKAPI.dll` **没有控制类型**，会被跳过并给出说明。

**启动 flags 也自适应**：`CREATE_BREAKAWAY_FROM_JOB` 可能被拒（`WinError 5`，父进程在 job 里），故 `spawn()` 逐档降级 `0x1000208 → 0x208 → 0x200 → 0`。

## 可移植性契约（不依赖特定设备）

整套技能（本技能 + 4 个业务技能）的目标是**放到任何机器、任何目录都能跑**。改代码时请勿破坏：

**① 环境变量（全部可选，只用于"我就要放这儿"的场景）**

| 变量                                       | 作用                                                         |
| ---------------------------------------- | ---------------------------------------------------------- |
| `YJK_SKILLS_DIR`                         | 整套技能的安装根目录（其下应有 `yjk-auto-drive/`、`column-section-opt/` …） |
| `YJK_DRIVER_DIR`                         | 直接指向 `yjk-auto-drive/scripts`                              |
| `YJK_AUTO_DRIVE_DIR`                     | 直接指向 `yjk-auto-drive` 技能目录                                 |
| `YJK_DIR` / `YJK_ROOT` / `YJK_INSTALL` … | YJK 安装位置（不设则自动探测）                                          |
| `YJK_PY` / `YJK_PYTHON`                  | 指定带 pythonnet 的解释器                                         |
| `YJK_STCAD_DIR`                          | 直接指向 YJK 安装目录下的 `STCAD`                                    |

**② 业务技能找驱动，只用「环境变量 → 相对路径 → 家目录一级子目录」**

`YJK_DRIVER_DIR` → `YJK_SKILLS_DIR/yjk-auto-drive/scripts` → 同父兄弟目录 → 当前目录 → **各 agent 的技能家目录**（枚举 `~` 与 `~/.config` 的一级子目录 `D`，逐个探 `D/skills/yjk-auto-drive`、`D/yjk-auto-drive`，再探 `~/.agent-skills`、`~/.skills`、`<cwd>/.skills`；**不写死任何厂商名**，只列一级不递归）→ 历史遗留路径（**保留以不破坏现有用户**：唯一带厂商名的一档，去掉它其余各档照样工作；具体路径见 AGENT-COMPAT.md）。
**不含任何盘符、用户名、桌面路径**。找不到就以退出码 2 明确报错，并把**所有查过的位置**列出来。换 agent / 换 IDE 的完整注意事项见根目录 **`AGENT-COMPAT.md`**。

**③ 自检脚本 `scripts/portability_check.py`（回归护栏）**

```powershell
& $py -X utf8 -B "<本技能>\scripts\portability_check.py"       # 扫整套技能
& $py -X utf8 -B "<本技能>\scripts\portability_check.py" --list-allow
```

扫 `*.py` 的**真实代码行**与 `*.md` 的**死引用**，规则：写死盘符 / POSIX 用户目录 / 桌面依赖 / Anaconda 假设 / 具体工程名 / 写死的等级表·柱号分组表 / **SQL 列名是猜的（P7）**。配套**显式白名单**（每条都写明"为什么这处可以例外"）——允许现状，不允许新增。退出码 0 = 通过。改完技能请跑一遍。

两条补充说明：

- **`yjk-dev-refs/` 不扫**：那是 YJK 官方随盘的案例与接口文档（第三方素材），带着厂商自己机器的盘符（实测 17 处：用户名下的 Documents 目录、某个数据盘下的 `MyProject` 之类）。扫它只会让退出码永远为 1，把真正的回归信号淹掉。
- **P7（警告级）** 管的是另一类"静默失真"：手写的 `INSERT INTO <表> (...)` / `UPDATE <表> SET <列>` 里，列名没有按表定义核对过。

  ```
  真实教训：某序列化器把 tblLoadSeg 的序号列 `No` 写成 `No_`。
  一句都不报错 —— INSERT 里少了那一列只当"没给"，被填成默认值 0，
  结果 784 条梁上均布线荷载在 yjk_importydb 时整批被丢弃。
  ```

  这类写法静态判不出对错（列名到底是不是实列要看库），所以它**只提示、不阻断退出码**；核对无误的**逐条**加进白名单（写理由，别整文件豁免）。新代码的正确做法是**从 `PRAGMA table_info` 派生列名**，或在插入前校验"给的键都在实列里"—— `column-section-opt/scripts/ydb_serialize.py` 的 `add()` 就是这个范式（键不在表里直接抛 `YdbSchemaError`，并对 `No_`/`No` 这种易混列名给出专门提示）。

## 目录结构

```
yjk-auto-drive/
├── SKILL.md
├── assets/
│   ├── README.md          # YJKAPI.dll 从哪来、放哪
│   ├── YJKAPI.dll         # 官方客户端（内置一份可用的）
│   └── YAPIData.dll
├── references/
│   ├── setup-checklist.md # 用户前置准备（逐条含"验证方法"与"故障表现"）
│   ├── commands.md        # 官方命令全表（界面/建模/计算/结果）
│   ├── ipc-protocol.md    # 通道原理、事件、共享内存、原生兜底协议
│   └── troubleshooting.md # 症状 → 根因 → 处置
└── scripts/
    ├── paths.py              # 跨机器自适应定位（唯一"找东西"的地方）
    ├── yjk_probe.py          # 环境自检 / 一键修 Config.ini / 活体测试
    ├── setup_env.py          # 建隔离 venv 并装 pythonnet/openpyxl/psutil
    ├── yjk_auto.py           # 主驱动：status/kill/probe/host/send（含 @takeoff 算量宏）
    ├── impcheck.py           # 导入校验闸门：逐表核对 .ydb→.ymd（只依赖 sqlite3）
    ├── projpara.py           # 总信息（前处理计算参数）按名读写 + 回读校验
    ├── jc.py                 # 基础（JCCAD）重算：带工程启动 → 切标签 → 生成数据 → 基础计算
    ├── jc_react.py           # 由 CAL_MID.INP/.DIS 反算逐桩反力与利用率（不依赖 YJK 结果库）
    ├── portability_check.py  # 可移植性回归护栏（扫整套技能）
    ├── dlgwatch.py           # 模态框看门狗（host 内线程，自动应答出错弹框）
    ├── env.py                # 工程目录级探测（模型文件名/版本/是否正被打开）
    ├── yjkw.py               # 纯 Win32：找 yjks 窗口 / 应答对话框
    ├── selfcheck.py          # 离线自检（不需要 YJK）
    └── yjk_cleanup.py        # 清理"无主窗口"的残留 yjks 实例
```

`dlgwatch.py` 只答 `RULES` 命中的框：未命中的、授权/许可类的框一个按钮都不点。

`paths.py` 另有两个对外接口供其它技能复用：`all_install_roots()`（所有候选安装根，用于遍历多个版本找 `STCAD`）与 `python_candidates()`（解释器候选链，`setup_env.py` 也用它）。

## 与 column-section-opt 的分工

- **本技能**：只负责"把 YJK 驱动起来 → 算出结果 → 拿到 `设计结果\`"。
- **`column-section-opt`**：负责"读现状 → 按轴压比/造价选型 → 把截面与等级写回模型 → 调本技能算 → 复核 → 出 Excel 报告"。它的 `scripts/driver.py` 会自动找到本技能目录。

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
