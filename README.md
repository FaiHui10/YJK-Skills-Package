# YJK 自动化技能包

用脚本驱动盈建科（YJK），不用手点界面：

```
自动建工程 → 自动导入模型 → 自动预处理/计算 → 读设计结果
→ 出施工图 / 算工程量 / 做方案比选 / 出造价报告        （全程零人工点击）
```

换 agent / IDE 前先读 [`AGENT-COMPAT.md`](AGENT-COMPAT.md)：硬前置条件、一次性环境准备、
环境变量、首次自检步骤、编码约定。

**YJK 版本**：6.x / 7.x / 8.x 都支持。8.x 用安装根 `YJKAPI.dll`，启动走官方
`initConfig → RunYJK → initConfig(Pid)`（不再依赖 6/7 的命名事件，也不用敲
`yjksipccontrol`）；差异与实测记录见 `yjk-auto-drive/SKILL.md` 的「版本适配」。

---

## 一、包含哪些技能

| 技能 | 职责 | 角色 |
|---|---|---|
| **`yjk-auto-drive`** | 纯通路：启动 YJK / 新建工程 / 导入模型 / 预处理 / 计算 / 读设计结果 | **底座** |
| `column-section-opt` | 柱**截面 + 混凝土等级**优选，并产出分析报告 | 业务 |
| `floor-system-comparison` | **楼盖**（次梁布置方式）经济比选 | 业务 |
| `column-scheme-comparison` | 柱**截面形式**（钢筋混凝土 vs 钢管混凝土）经济比选 | 业务 |
| `yjk-draw-takeoff` | **算完之后**：施工图出图 + 混凝土/钢筋工程量 + 汇总 Excel | 业务 |
| `yjk-dev-refs/` | （**不是技能**）YJK 官方**二次开发资料**的离线参考集 | 资料 |

`yjk-dev-refs/` 由 gitee 上 YJK 官方开源组织 `yjk-opensource` 的 `csharp-yjks` / `py-yjks` /
`yjkapi_-python` 三个仓库的文档与官方案例转换而来：建模/前处理/设计结果三套接口说明、
前处理计算参数宏定义（`tblProjectPara` 的 ID 与枚举码权威表）、数据库文件说明，
以及 18 个不依赖 YJK 运行的官方 Python 案例。索引见 `yjk-dev-refs/README.md`；
底层源码与 SDK 压缩包未随包分发。

---

## 二、结构：一个底座 + 四个业务技能

```
                    ┌──────────────────────────────┐
                    │        yjk-auto-drive        │
                    │  （唯一碰 YJK 的地方：IPC 通道） │
                    └──────────────┬───────────────┘
              find_driver() ──────┼────── find_driver()
        ┌───────────────┬─────────┴────────┬────────────────┐
        ▼               ▼                  ▼                ▼
 column-section-opt  floor-system-   yjk-draw-takeoff   （独立）
                     comparison                          column-scheme-
                                                         comparison
```

* **单向依赖**：业务技能用 `find_driver()` 定位 `yjk-auto-drive/scripts/yjk_auto.py`；
  底座不引用任何业务技能，所以底座可单独用、业务技能可按需增删。
* **`column-scheme-comparison` 不驱动 YJK**：读 `设计结果\wpj*.out` + 模型库，
  做 GB 50936-2014 承载力计算与广州定额计价，属纯解析/计算。
* 所有技能共用同一套跨机器定位约定（第四节）：不含盘符、用户名、桌面路径，
  也不把任何具体厂商目录当前提。

---

## 三、典型串联方式

**① 简单框架全自动（从零到报告）**

```
column-section-opt  build   → 生成 .ydb
        ↓
yjk-auto-drive      host    → 启动/建工程/导入/预处理/计算
        ↓
column-section-opt  opt     → 按实算轴力重新选型
        ↓
yjk-auto-drive      send @recalc <新截面.ydb>   → 不重启 YJK，重算一轮
        ↓
column-section-opt  report  → Excel 报告
```

**② 算完之后出图 + 出量**

```
yjk-draw-takeoff  draw_quant.py --ydb 模型.ydb --proj P1
                  summary_xlsx.py results/P1 --name P1
```

**③ 楼盖方案比选**

```
floor-system-comparison  spec.py → build_floor.py → verify_ydb.py
                         → yjk_quant.py（逐方案实算）→ collect.py → build_report.py
```

**④ 柱形式比选**（不驱动 YJK）

```
column-scheme-comparison  col_data.py → cost_model.py → report_xlsx.py
```

---

## 四、跨机器契约（改代码时不要破坏）

**① 业务技能找驱动：六份副本共用同一套查找链**（`selfcheck.py` 的 T31 逐条守着）

```
YJK_DRIVER_DIR / YJK_AUTO_DRIVE_DIR / YJK_SKILLS_DIR   ← 环境变量最优先（三个都认）
→ 同父兄弟目录、当前目录（../.. 、.. 、. 、..）           ← 装机默认形态，最可靠
→ 通用扫描：枚举 ~ 与 ~/.config 的一级子目录 D，
   逐个探 D/skills/yjk-auto-drive、D/yjk-auto-drive      ← 不认任何具体厂商名
→ 中立约定位置：~/.agent-skills、~/.skills、<cwd>/.skills
→ 历史遗留路径（保留以不破坏现有用户；唯一带厂商名的一档，见 AGENT-COMPAT.md）
```

通用扫描只列家目录一级子目录、不递归，所以"把整套技能丢进本 agent 的技能目录"直接可用；
带厂商名的只有最后一档历史兼容项，去掉它其余各档照样工作。
找不到以**退出码 2** 报错，并逐条列出所有真正查过的位置。

**② 环境变量（全部可选）**

| 变量 | 作用 |
|---|---|
| `YJK_SKILLS_DIR` | 整套技能的安装根目录（其下应有 `yjk-auto-drive/`、`column-section-opt/` …） |
| `YJK_DRIVER_DIR` | 直接指向 `yjk-auto-drive/scripts` |
| `YJK_AUTO_DRIVE_DIR` | 直接指向 `yjk-auto-drive` 技能目录 |
| `YJK_DIR` / `YJK_ROOT` / `YJK_INSTALL` | YJK 安装位置（不设则自动探测） |
| `YJK_PY` / `YJK_PYTHON` | 指定带 pythonnet 的解释器 |
| `YJK_STCAD_DIR` | 直接指向 YJK 安装目录下的 `STCAD` |
| `YJKAPI_DLL` | 指定官方客户端 DLL |
| `YJK_COL_RES` / `YJK_COL_YDB` | 柱形式比选的默认数据源 |

**③ 解释器不写死**：`yjk-auto-drive/scripts/paths.py` 的 `find_python()` /
`python_candidates()` 是唯一探测处（环境变量 → `~/.yjk-auto/venv` → 各 agent 托管环境 →
`sys.executable` → 全量枚举 → 常见安装路径），其它脚本一律复用它。

**④ YJK 安装位置不写死**：同文件的 `all_install_roots()`（环境变量 → 运行中的 yjks 进程路径
→ 注册表 → 枚举各盘符下的常见安装位置，限深剪枝）；`STCAD` 由此推导。

**⑤ 回归护栏 `portability_check.py`**

```powershell
& $py -X utf8 -B "yjk-auto-drive\scripts\portability_check.py"
```

扫 `*.py` 真实代码行与 `*.md` 死引用，覆盖写死盘符 / POSIX 用户目录 / 桌面依赖 /
Anaconda 假设 / 具体工程名 / 写死的等级表·柱号分组表；配显式白名单（每条写明例外理由），
允许现状、不允许新增。**退出码 0 = 通过。**

**⑥ 编码约定**：源码与文本产物一律 UTF-8、无 BOM；`open()` 显式 `encoding=`；
读 YJK 自己的输出用 **GBK**；非 GBK 字符的输出要有控制台兜底；子进程抓文本指定 `encoding=`。
完整规则与静态检查见 [`AGENT-COMPAT.md`](AGENT-COMPAT.md) 的「编码约定」一节与
`yjk-auto-drive/scripts/encoding_check.py`。

---

## 五、分发建议

* **只放底座**：`yjk-auto-drive` 能单独用（自带的 `yjk_probe.py` / `selfcheck.py` /
  `portability_check.py` 足以自证可用）。
* **完整链条**：五个一起放，**保持同级目录**（业务技能的兄弟目录查找依赖这一点）。
* **只要出图出量**：`yjk-auto-drive` + `yjk-draw-takeoff`。
* **只要柱/楼盖比选**：`yjk-auto-drive` + 对应业务技能。

放置与依赖见 `INSTALL.md`；换 agent / IDE 前必读 `AGENT-COMPAT.md`；一段话上手见 `00-先读我.txt`。

---

## 五之二、本仓库带了什么、许可是怎么分的

**开箱即用**：克隆下来就能跑（含官方客户端 DLL 与离线参考集）。第三方内容与许可见
[`NOTICE.md`](NOTICE.md) —— 厂商 DLL 与 `yjk-dev-refs/` 的转载**不适用**本仓库的
[`LICENSE`](LICENSE)，各自版权归权利人，若要再分发到别处请自行确认授权。

万一 DLL 缺失或不匹配（换了 YJK 版本、只拷了部分文件），跑一次体检与补齐：

```powershell
python fetch_vendor_refs.py --check      # 看缺什么、本机 YJK 装在哪
python fetch_vendor_refs.py              # 能取到就补齐（从本机 YJK 安装目录 / 官方公开仓库）
```

| 内容 | 本仓库 | 说明 |
| --- | --- | --- |
| 五个技能的代码与文档、根文档 | 带 | 本仓库原创部分（MIT，见 `LICENSE`） |
| `yjk-auto-drive/assets/`（`YJKAPI.dll`、`YAPIData.dll`） | 带 | 盈建科官方客户端 DLL，来自官方公开仓库 `csharp-yjks` 7.1 分支 |
| `yjk-dev-refs/`（官方二次开发资料转载，117 个文件） | 带 | 来源与许可逐项列在 `NOTICE.md`：`csharp-yjks`（木兰宽松许可证 v2）、`py-yjks`（Apache-2.0）、`yjkapi_-python`（仓库内无 LICENSE，按其公开发布状态转载） |

即使这两个 DLL 都没有，技能也能运行：找 DLL 的候选链会继续往下找
（环境变量 `YJKAPI_DLL` → 技能 `assets/` → 用户缓存 `~/.yjk-auto/` → YJK 安装目录），
`yjk_probe.py` 会打印命中了哪一个。

---

## 六、目录内容

```
yjk-skills-package/
├── README.md                     # 本文件
├── INSTALL.md                    # 安装与验收
├── AGENT-COMPAT.md               # 换 agent / IDE 前必读（前置条件 / 环境变量 / 自检六步）
├── NOTICE.md                     # 第三方内容与许可声明（厂商 DLL / 官方资料转载）
├── LICENSE                       # MIT（只覆盖本仓库原创部分）
├── 00-先读我.txt                 # 一段话上手
├── fetch_vendor_refs.py          # 体检/补齐厂商 DLL 与官方参考集
├── yjk-auto-drive/               # 底座
│   ├── SKILL.md
│   ├── assets/                   # 官方客户端 DLL（已内置可用的一份）
│   ├── references/               # 装机清单 / 命令全表 / IPC 协议 / 排查
│   └── scripts/
├── column-section-opt/
├── floor-system-comparison/
├── column-scheme-comparison/
├── yjk-draw-takeoff/
└── yjk-dev-refs/                 # YJK 官方二次开发资料（索引 + 来源 + 许可说明）
    ├── README.md                 # 索引：来源仓库、版本、怎么用、许可与再分发说明
    ├── 04-接口说明/               # 建模 / 前处理 / 设计结果 三套接口说明
    ├── 05-数据文件说明/            # ydb 及各施工图数据库
    └── 06-总信息参数ID表/          # tblProjectPara 的 ID 与枚举码权威表
```

> 每个技能的 `SKILL.md` 是入口文档；细节在其 `references/` 下；脚本的输入输出契约在各
> `scripts/README.md`。
