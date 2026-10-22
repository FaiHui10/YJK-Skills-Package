# 安装与验收

把技能放到一台装了 YJK 的 Windows 机器上并跑通。前置准备只做一次，约十分钟。

> 换 agent / IDE 前先读 [`AGENT-COMPAT.md`](AGENT-COMPAT.md)（硬前置条件、环境变量、
> 首次自检步骤）。本文只讲怎么装到本机。

> 仓库里已内置官方客户端 DLL 与离线参考集，克隆下来即可用。若 DLL 缺失或与你的
> YJK 版本不匹配（只拷了部分文件、换了版本），跑一次体检与补齐：
>
> ```powershell
> python fetch_vendor_refs.py --check      # 看缺什么、本机 YJK 装在哪
> python fetch_vendor_refs.py              # 从本机 YJK 安装目录 / 官方公开仓库补齐
> ```
>
> 第三方内容与许可见 [`NOTICE.md`](NOTICE.md)；见 README 的「本仓库带了什么、许可是怎么分的」。

---

## 一、系统与软件前提

| 项 | 要求 | 说明 |
|---|---|---|
| 操作系统 | Windows | 依赖 Win32 窗口消息与命名事件 |
| YJK | **6.1 或更高**（6.x / 7.x / 8.x 均可） | 需要有 `yjks.exe` 与 `YjkLauncher.exe`；6/7 用技能内置 `assets/YJKAPI.dll`，8.x 用安装根 `YJKAPI.dll`（走 `initConfig`/`RunYJK`/`exit`）。本文按 7.1 说明，8.x 差异见 `yjk-auto-drive/SKILL.md` |
| Python | **3.10 ~ 3.13** | 需要 `pythonnet`（`clr`）、`openpyxl`、`psutil` |
| 磁盘 | 无特殊要求 | 技能本身很轻（DLL 约 300 KB） |

Python 版本别太新：pythonnet 对 3.14 的支持常滞后，3.10~3.13 最稳。

---

## 二、把技能放到哪

### 2.1 放进本 agent / IDE 的用户级技能目录（推荐）

不需要知道那个目录叫什么，把五个目录**平级**放进去：

```
<本 agent 的用户级技能目录>/
├── yjk-auto-drive/          ← 底座（必装，其余四个都依赖它）
├── column-section-opt/
├── floor-system-comparison/
├── column-scheme-comparison/
└── yjk-draw-takeoff/
```

`column-section-opt/scripts/driver.py` 会枚举家目录一级子目录去找
`<家>/.<任意名>/skills/yjk-auto-drive`，也试 `~/.config/<任意名>/skills/…`、
`~/.agent-skills/`、`~/.skills/`、`<cwd>/.skills/` —— 任何 agent 的技能家目录都能命中，
不需要改代码（只列一级、不递归，家目录很大也不拖慢启动）。

**五个技能必须是同级目录**：业务技能优先靠兄弟目录找到 `yjk-auto-drive`，
兄弟目录找不到才扫各 agent 技能目录，最后才靠 `YJK_DRIVER_DIR` / `YJK_SKILLS_DIR` 指路。

### 2.2 历史位置的兼容

老用户放在厂商约定的技能目录里（如 `~/.workbuddy-ai/skills/`）不用搬家，
那条路径仍在候选链里；新装走 2.1。

### 2.3 完全自定义位置

任意位置都行，满足其一即可：五个目录仍同级；或设
`YJK_DRIVER_DIR=<...>\yjk-auto-drive\scripts`；或设 `YJK_SKILLS_DIR=<...>`（其下是五个技能目录）。

### 2.4 不要打包的文件

`_user_meta.json` 是宿主平台生成的安装元数据（记录安装时间/来源），换平台会重新生成 ——
分享打包时不必带上，带上也无害。

---

## 三、前置准备（新机器只做一次）

逐条版（含"怎么验证"与"没做的故障表现"）见 `yjk-auto-drive/references/setup-checklist.md`。

### 3.1 装 YJK 并能正常打开工程

手动启动一次 YJK，打开一个自带算例，确认能进界面、能算。

### 3.2 两处 `Config.ini` 补 `[YJKSControl] Flag = True`

这是"启动即自动开 IPC"的关键：否则必须人工在 YJK 里键入 `yjksIPCControl`，
而自动化键入做不到（回车提交不了、锁屏抢不到焦点）。

```ini
[YJKSControl]
Flag = True
```

* 安装目录：`<YJK安装目录>\Config.ini`
* 用户配置目录：`%ProgramData%\yjkSoft\<版本目录>\Config.ini`

一键完成（会自动发现所有 `Config.ini`，不写死路径）：

```powershell
& $py -X utf8 -B "<技能>\yjk-auto-drive\scripts\yjk_probe.py" --fix-config
```

跑自动化时设 `True`，用完可改回 `False`（官方默认值）。

### 3.3 准备带 pythonnet 的 Python 环境

```powershell
& $py -X utf8 -B "<技能>\yjk-auto-drive\scripts\setup_env.py"
```

它会在 `~/.yjk-auto/venv` 建隔离环境、装好 `pythonnet` / `openpyxl` / `psutil`，
并把可用解释器路径记到 `~/.yjk-auto/python.txt`（后续脚本自动复用）。验证：

```powershell
& "<~/.yjk-auto/venv/Scripts/python.exe>" -c "import clr;print('CLR-OK')"
```

离线机器：先在有网机器下好 wheel，或换国内镜像
`-i https://pypi.tuna.tsinghua.edu.cn/simple`。

### 3.4 官方客户端 `YJKAPI.dll`

本包在 `yjk-auto-drive/assets/` 已内置一份可用的 `YJKAPI.dll` + `YAPIData.dll`，
换机器拷整个 `assets/` 即可，不需要重新取件。要自己取：官方开源仓库
**`gitee.com/yjk-opensource/csharp-yjks`** 的 **7.1 分支**，路径
`不依赖YJK案例/dll/YJKAPI.dll`，放进 `assets/`。细节见 `yjk-auto-drive/assets/README.md`。

### 3.5 保证全机只有一个 `yjks.exe`

```powershell
& $py -X utf8 -B "<技能>\yjk-auto-drive\scripts\yjk_auto.py" kill
& $py -X utf8 -B "<技能>\yjk-auto-drive\scripts\yjk_cleanup.py"   # 只清无主窗口残留（预演）
```

多实例会互抢全局事件，表现为**有 Success 应答但命令不执行**。

---

## 四、验收（逐级加深）

### 第 1 步：环境自检（秒级，不需要真的算）

```powershell
& $py -X utf8 -B "<技能>\yjk-auto-drive\scripts\yjk_probe.py"
```

输出 `[2] 结论` 显示「环境齐备」即通过。加 `--runtime` 会真启动一次并做活体连接测试
（判据是 `yjk_save` 的**文件 mtime**）。

### 第 2 步：离线逻辑自检（秒级，不需要 YJK）

```powershell
& $py -X utf8 -B "<技能>\yjk-auto-drive\scripts\selfcheck.py"
```

覆盖宏展开、窗口标题解析、实例分类、注册表、预检分支、收件箱归档与闸门等不依赖 YJK 的逻辑；
末尾打印 `逻辑断言：通过 N，失败 0`。

### 第 3 步：可移植性自检（秒级）

```powershell
& $py -X utf8 -B "<技能>\yjk-auto-drive\scripts\portability_check.py"
```

**退出码 0 = 通过**（未发现未列入白名单的设备/工程耦合写法）。

### 第 4 步：编码约定自检（秒级）

```powershell
& $py -X utf8 -B "<技能>\yjk-auto-drive\scripts\encoding_check.py"
```

**退出码 0 = 通过**（UTF-8 无 BOM、`open()` 显式编码、读 YJK 输出用 GBK、非 GBK 输出有兜底等）。

### 第 5 步（可选）：真机跑一轮

```powershell
& $py -X utf8 -B "<技能>\yjk-auto-drive\scripts\yjk_auto.py" host `
    --dir "<工作目录>" --name Auto1 `
    --import "<模型.ydb>" --prep --calc

Get-ChildItem "<工作目录>\设计结果" | Measure-Object
```

尖括号里换成你自己的路径（文档一律不写具体盘符：照抄别人的路径是换机器后最常见的
"看起来跑通了其实没算"来源）。判据：日志里 `设计结果/ 共 N 个`，且
`设计结果\wmass.out` 的 mtime 是刚刚。**不要看 `RunCmd` 的返回值。**

---

## 五、常见问题

| 现象 | 先看哪 |
|---|---|
| `ModuleNotFoundError: No module named 'clr'` | 用 `setup_env.py` 建的环境；或 `YJK_PY` 指定解释器 |
| 找不到 DLL / 无 `YJKSControl` 类型 | `assets/` 里的 DLL 是否在；`yjk_probe.py` 会打印它实际用了哪个 |
| 命令有应答但没效果 | 是否多实例；是否带 `.yjk` 启动了（见 `references/troubleshooting.md`） |
| 命令永不返回 | 模态框没人应答 → 看门狗；见 `references/troubleshooting.md` §12 |
| 计算报 `模型中没有单元数据` | 导入了空模型 → 见 `references/troubleshooting.md` §13 |
| 业务技能报"找不到驱动技能"（退出码 2） | 五个技能是否同级；或设 `YJK_DRIVER_DIR`；报错会列出**所有**查找过的位置 |
| 输出中文变问号 / 乱码 | 见 `AGENT-COMPAT.md` 的「编码约定」；跑 `encoding_check.py` |

各技能的 `references/troubleshooting.md`（`yjk-draw-takeoff` 也有）按"你看到什么"分节给出
症状 → 根因 → 处置。
