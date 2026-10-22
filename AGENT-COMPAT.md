# 换 agent / 换 IDE 之前请读这一页

本包原先为**某一个特定 agent 平台**而写（技能目录名、托管 Python 环境、"把文件推给用户"
这类专有工具）。这些假设都已改成**与厂商无关**的写法，但**前置条件本身没变** —— YJK 是
Windows 桌面软件，谁也绕不过去。本文列出"另一个 agent 接手这套技能时必须先知道的东西"。

> 相关文档：装到本机看 `INSTALL.md`；一段话上手看 `00-先读我.txt`；每个技能入口是各自的
> `SKILL.md`。

---

## 一、硬前置条件（不满足就别往下走）

| # | 前置条件 | 为什么 | 不满足时的表现 |
|---|---|---|---|
| 1 | **Windows**（真桌面会话） | YJK 是 Windows 桌面程序；本包靠 Win32 窗口消息（`PostMessageW` 应答模态框）+ 命名事件（IPC 通道）驱动它 | Linux/macOS 无法运行。**没有无头/容器方案**：GUI 进程起不来，`yjks.exe` 一启动就死 |
| 2 | **YJK 6.1+（含 7.x / 8.x）已装好，且能手动打开一个工程** | 本包只**驱动**既有安装，不替代 YJK 做结构设计。8.x 由 `initConfig` 建通道并用 `RunYJK` 启动，无需 `yjksipccontrol` | `yjk_probe.py` 报"未找到 YJK 安装"或"实例是死的" |
| 3 | **YJK 许可有效**（能真正算起来） | 无许可时界面能进、命令会应答，但结果是空的 —— "看起来跑通了其实没算" | 计算链 `0.1s` 秒回且不写盘。网络许可的用户可能要连 VPN，这是实测过的现场故障 |
| 4 | **能启动 GUI 进程** | `yjks.exe` 必须无参启动才能开 IPC（带 `.yjk` 路径启动 = 通道坏掉，见 `yjk-auto-drive/SKILL.md`） | 无桌面会话/被策略拦截时启动失败 |
| 5 | **一个带 `pythonnet` 的 Python 解释器** | 官方 DLL 是 .NET 程序集，只能用 pythonnet（`clr`）反射调用。**它决定了"必须用哪个解释器"** | 报 `No module named 'clr'` 或 `No module named 'System'` —— **看着像包坏了，其实是解释器选错了**，见下面专节 |

**一台机器同时只能跑一个 `yjks.exe`**：IPC 事件是**全局**的，两个实例会互抢消息，
表现为"有 Success 应答但命令没执行"。自动化期间**不要并行开两个 YJK 会话**。

### 如果报 `No module named 'clr'` 或 `No module named 'System'`

**这不是包的问题，是解释器选错了**：本包的脚本必须用带 pythonnet 的那个解释器跑。用一个
没装 pythonnet 的解释器去跑，典型报错是：

```
ModuleNotFoundError: No module named 'System'
```

`System` 是 .NET 的命名空间，只有 pythonnet 在场时才存在 —— 所以这条报错**读起来像"包缺
文件"，实际只是"你拿了另一个解释器"**（`clr` 缺失时报 `No module named 'clr'`，好认一点）。
刚接手的 agent 顺手拿默认解释器跑脚本，撞上的就是这个，容易误判成本包有问题。

规则只有两条：

1. **先跑一次** `yjk-auto-drive/scripts/setup_env.py` —— 它建 `~/.yjk-auto/venv`、装好三个依赖，
   并把路径写进 `~/.yjk-auto/python.txt`（详见第二节）。
2. **之后一律用 `column-section-opt/scripts/driver.py python` 打印出来的那个解释器**
   （它内部走 `yjk-auto-drive/scripts/paths.py` 的探测链，是这件事**唯一**的权威来源）。

**不要用 agent 自己的默认解释器，也不要往系统 Python 里 `pip install`** —— 那会污染用户
环境，换台机器又得重来一遍。要强制指定某个解释器时，用环境变量 `YJK_PY`（见第三节）。

---

## 二、一次性环境准备（只做一次，约十分钟）

```powershell
# ① 建隔离环境并装依赖（需要网络；装到 ~/.yjk-auto/venv）
& $py -X utf8 -B "<技能>\yjk-auto-drive\scripts\setup_env.py"

# ② 打开 YJK 的 IPC 开关（改所有 Config.ini，不写死路径）
& $py -X utf8 -B "<技能>\yjk-auto-drive\scripts\yjk_probe.py" --fix-config
```

`setup_env.py` 把解释器路径写进 `~/.yjk-auto/python.txt`，后续脚本自动复用。

三个第三方依赖，各管一件事：

| 包 | 干什么 | 缺了会怎样 |
|---|---|---|
| `pythonnet`（`import clr`） | 反射调用 YJK 的 **.NET 程序集**（官方客户端 DLL、建模/序列化接口） | `driver.py` / 建模路径全部不可用。**三个里唯一"难装对"的那个** —— 见下 |
| `openpyxl` | 写 **Excel 报告**（各业务的 `*_xlsx.py` / `report*.py`） | 报告阶段崩，前面算的部分不受影响 |
| `psutil` | **找进程 / 验活**（`yjks.exe` 实例分类、清场、等待消失） | 实例判定退化，容易出现"多实例互抢"的静默故障 |

**`pythonnet` 是三个里唯一需要当心的**：另两个装进哪个解释器都行，它一旦装好就**钉死了
"这一整套脚本必须用哪个解释器"** —— 换个没有它的解释器跑同一个脚本，报出来的错还像是包
坏了（见第一节末的专节）。它对 Python 3.14+ 的支持常滞后，所以 `setup_env.py` 优先挑
3.10~3.13 的基础解释器。

**依赖面本身是干净且封闭的**：对全部 53 个脚本做过一遍 AST 扫描，第三方 pip 模块**只有
三个** —— `openpyxl`（15 处导入）、`clr`（7 处）、`psutil`（5 处），恰好就是
`setup_env.py` 里 `PKGS` 那三项。其余"不像标准库"的名字（`System`、`DataFuncApplication`、
`CsToYjk`、`APIData`）**不是 pip 包，而是 .NET 命名空间**，靠 pythonnet 桥过去；引用它们的
6 个文件**都先导入 `clr`**，没有导入顺序问题。所以 **`setup_env.py` 跑成功，依赖就不会
缺**；真报"模块找不到"，八成是你用了另一个解释器（见第一节末专节），不是包缺了什么。

**pip 需要网络。** 离线机器：先在有网机器上下好 wheel；或由脚本自己打印的镜像命令安装：

```powershell
"<~/.yjk-auto/venv/Scripts/python.exe>" -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple pythonnet openpyxl psutil
```

`--fix-config` 写入的是：

```ini
[YJKSControl]
Flag = True
```

没有它就必须人工在 YJK 里键入 `yjksIPCControl` —— 自动化键入做不到（回车提交不了、锁屏
抢不到焦点）。用完可以改回 `False`（官方默认值）。

---

## 三、三个环境变量（全部可选，但"技能没放在预期位置"时必须设）

| 变量 | 指向 | 什么时候需要 |
|---|---|---|
| `YJK_SKILLS_DIR` | **整套技能的根**（其下应有 5 个技能目录） | 技能被拆散、不在同级时 |
| `YJK_DRIVER_DIR` | 直接指向 `yjk-auto-drive/scripts` | 只保留了底座和某个业务技能时 |
| `YJK_PY` | 带 `pythonnet` 的解释器 | 隔离环境没用上、或想用自己已有的环境时 |

**底座 `yjk-auto-drive` 必须与业务技能平级。** 业务技能找底座的顺序是（六个业务脚本各带
一份**完全相同**的候选链，由 `selfcheck.py` 的 T31 逐条守着）：

```
YJK_DRIVER_DIR / YJK_AUTO_DRIVE_DIR / YJK_SKILLS_DIR   ← 环境变量最优先（三个都认）
→ 同父兄弟目录、当前目录                                 ← 装机默认形态，最可靠
→ 通用扫描：枚举 ~ 与 ~/.config 的一级子目录 D，
   逐个探 D/skills/yjk-auto-drive、D/yjk-auto-drive      ← 不认任何具体厂商名
→ 中立约定位置：~/.agent-skills、~/.skills、<cwd>/.skills
→ ~/.workbuddy-ai/skills/yjk-auto-drive                 ← 历史遗留路径，保留以不破坏现有用户
```

那档"各 agent 的技能家目录"是**通用扫描**出来的 —— **不认任何具体厂商名**：本包列出
`~` 与 `~/.config` 的**一级子目录** `D`，逐个探 `D/skills/yjk-auto-drive`、
`D/yjk-auto-drive`、`D/skills/<任意名>/yjk-auto-drive`，再探 `~/.agent-skills/`、
`~/.skills/`、`<cwd>/.skills/`。只列一级、不递归（家目录很大也不拖慢启动），读不了的目录
直接跳过。**不含任何盘符、用户名或桌面路径**（桌面探测早已删除）。唯一带厂商名的是最后一档
**历史遗留兼容项**，去掉它其余各档照样工作，所以它**不是前提**。

> 所以"把整套技能丢进我这个 agent 的技能目录"这种最自然的装法，现在直接可用，不需要为本包
> 改代码，也不需要知道那个目录叫什么。解释器同理：`paths.py` 也会扫各 agent 的
> `venv/Scripts/python.exe` 与 `binaries/python/<ver>/Scripts/python.exe`，你已经在自己的
> agent 环境里装好的 `pythonnet` 会被认出来，不用重装。

找不到底座时，业务技能以**退出码 2** 收尾，并把**所有真正查过的位置**逐条列出来 —— 照着
那份列表逐个看即可，不用猜。

---

## 四、技能发现（agent 靠这个找到技能）

* 五个技能都带 YAML frontmatter（`name` / `description`），可直接被按 frontmatter 发现的
  agent 收录。`yjk-auto-drive` 曾漏掉 frontmatter —— 它是其余四个的前置依赖，漏了就整套
  都用不起来，已补上。
* `description` 一律先说做什么、末尾给触发短语，且不含任何平台专有的工具名。
* 底座 `yjk-auto-drive` 是其余四个的前置依赖（`column-section-opt`、
  `floor-system-comparison`、`column-scheme-comparison`、`yjk-draw-takeoff`）。
  只装业务技能不装底座 = 必然报"找不到驱动技能"。
* `yjk-dev-refs/` 是参考资料，不是技能（没有 `SKILL.md`，扫技能的 agent 请忽略它）。它是
  YJK 官方随盘案例与接口文档（第三方素材），里面必然带着厂商自己机器的盘符 —— 这正是
  `portability_check.py` 把它排除在扫描之外的原因：扫它只会让退出码永远为 1，把真正的回归
  信号淹掉。

---

## 五、平台与编码假设（照抄即可，别"顺手现代化"）

* **Windows only**：`ctypes.windll` / `PostMessageW` / 命名事件 / `winreg` 都不可替代。
* **YJK 的文本输出是 GBK**（`设计结果\wpj*.out` 等）：`decode("gbk", "ignore")` 是**对的**，
  改成 UTF-8 会全变乱码。
* **少数设计文件是 UTF-16LE**（如 `设计结果\check.out`，带 BOM）：当 GBK 读会全是乱码。
  所以读这类文件要按编码逐个试，不能一刀切。
* **`.ydb` / `.ymd` 是 SQLite 库**：直接 `sqlite3` 打开。**只读时用 `mode=ro`**。
* **全机只假定一个 `yjks.exe`**：IPC 事件是全局的（见第一节第 4 条）。
* **本包不往技能目录里写任何东西**：全部脚本都扫过一遍，没有一处
  `open(os.path.join(HERE, …), "w")` 之类的写入。所以宿主 agent 把技能目录挂成只读也照跑
  不误，不需要为它开写权限。运行期真正写盘的地方只有两处：`~/.yjk-auto/`（隔离环境、
  DLL 缓存、自有实例登记）和工作目录（YJK 的工程与设计结果）。*（唯一例外是随包发布的
  二进制资源 `floor-system-comparison/refs/scaffold.ydb` —— 它只被**读**，不会被改写。）*
* 别把 `%TEMP%` 当成"一定可写、一定够快"的临时盘 —— 大模型的工作目录放在项目盘上更稳。

### 输出的编码：脚本必须能在默认 GBK 控制台下跑完

上面那条「YJK 的输出是 GBK」是**读**的一面；**写**的一面同样会咬人（实测踩过）：

本包会在控制台打印 `✅ ❌ ⚠ −`(U+2212) `² ³ ⇒ ✓` 等**非 cp936** 字符。
Windows 默认控制台（`chcp`=936、未设 `PYTHONIOENCODING`）下 `print` 会抛

```
UnicodeEncodeError: 'gbk' codec can't encode character '\u2705' ...
```

并**以退出码 1 中断进程**。危害不是"少打一行字"，而是：

* `ydb_lint.py`、`compat_check.py` 这类**检查脚本**，结论其实是「通过」，却**恒定返回 1** ——
  上层编排按退出码判定，会把「通过」当成「不通过」；
* `split_stdflr.py`、`frame_build.py` 崩在**收尾那一行**上：文件（或模型）其实已经写好，
  甚至已经 `integrity_check: ok`，退出码却是 1。

**处置（已在本包落地）**：每个 CLI 入口都调用一次

```python
def _utf8_console():
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass
```

UTF-8 控制台下原样输出，GBK 下退化成 `?`，**两种情况都不崩**。它**只在 `__main__` /
`main()` 里调用**，不在 import 时改 stdout —— 这些模块会被别的脚本当库 import，污染
import 方的 stdout 是不对的。

> **`-X utf8` 会把这类缺陷全部掩盖掉**：本文件下面「首次自检」的命令原先一律带 `-X utf8`，
> 于是 ✅ 一直显示正常、退出码一直是 0 —— 缺陷只在**上层编排按默认编码管道/重定向调用**时
> 才现形，而那恰恰是编排的常规做法。所以：**加 `-X utf8` 跑一遍、再不加跑一遍，两次都要
> 绿。** 下面第 ②③④ 步已按此写明。

---

## 五之二、退出码与「授权暂停」（编排器必读）

### `yjk_auto.py host` 的退出码

以前 **preflight 拒绝也返回 0**（日志写着「本次未做任何操作」，退出码却是 0），任何按退出码
判定的编排都会把「一个动作都没做」当成成功。现已区分：

| 退出码 | 含义 | 编排该怎么办 |
|---|---|---|
| **0** | 干完了，且没有登记到失败 | 继续 |
| **2** | **本轮确认为失败**（导入校验不通过 / 通道没起来 / 工程没就位 / 客户端初始化失败…） | 停下来看日志里那个「失败台账」 |
| **3** | **预检拒绝**：一个动作都没做（有你在用的实例 / 有残留 / 另一 host 在跑） | 先解决占用，**别当成功** |
| **5** | **无法判定**：看门狗的对话框监视起不来 → "没弹框"与"没人看着"不可区分，相关命令结果不可信 | **别当成功**；人工看一眼 |
| **6** | **授权/许可问题**（见下） | 提示用户处理；处理完重跑即可 |

> `driver.py host` / `run_all_yjk.py` 这类调用方现在都能正确分辨这五种。

### 碰到授权问题：**暂停，等用户处理**（绝不替你点「是」）

网络许可不可达时，YJK 会每隔约 2 秒弹一次「授权」框。**千万不要盲答** —— 实测：看门狗按
默认规则回「是」，YJK 就被引导去走「单机码激活」，紧接着弹「序列号输入不正确」，再一次次
回「是」……**对话框无限循环、IPC 通道永远起不来**，现场只看到一串「回是」，看不出真因是
许可没连上。

现在的行为：

* 看门狗**对授权类对话框不点任何按钮**（只登记）；判定关键字见
  `dlgwatch.LICENSE_KW`（授权／许可／网络版服务器／单机码／序列号／激活／加密锁…）。
* `host` 检测到它之后：打印醒目提示、在工作目录写
  **`_yjk_license.need_user`** 标志，然后**继续等**（默认最多 30 分钟，
  `--license-timeout` 可调）。你把许可修好（例如连上 VPN）之后，通道一通就**自动继续**，
  不需要重跑、不需要改任何东西。
* 无人值守的编排可以用 **`--on-license fail`** 换成「立刻以退出码 6 结束」。
* 相关开关：`host --wait-ipc <秒>`（默认 150）、
  `--on-license {pause,fail}`、`--license-timeout <秒>`。

排查授权按这个清单走（提示里也会打印）：
公司 VPN 是否连着 · `lic.yjk.cn:8081` 是否可达 · 许可是否被占满（残留会话会占名额）·
本机 YJK 的网络版服务器/授权码配置有没有被改过。

#### 怎么看出「它正卡在授权上」（标志的读口）

`_yjk_license.need_user` 是**跨进程唯一**的信道：宿主进程内存里的 `_LICENSE_BLOCKED`
只存在于那个进程，别的 agent/会话读不到。所以有两个读口，**别去猜**：

```powershell
# 人看：查这个工作目录（不给 --dir 就查 own.json 里登记的目录）
yjk_auto.py status --dir "<工作目录>"
#   有标志时打印：标志路径 + 写入时间 + 当时对话框内容 + 「不代答授权框」
#   另外它会提示：许可恢复后**不用改脚本**，重跑 host 即可（就绪时自动清标志）

# 编排看：未就绪时 send 会**先判授权**，命中就点名原因并给人工处理清单，退出码仍是 2
yjk_auto.py send --dir "<工作目录>" "@calc"
#   ★★ 该目录上次是**因授权/许可问题暂停**的（标志 _yjk_license.need_user，N 秒前写入）：
#      当时对话框内容：授权失败：网络版服务器 lic.yjk.cn:8081 无响应
#      请**用户**先处理许可（VPN / lic.yjk.cn:8081 可达 / 许可名额 / 网络版服务器配置）
```

标志内容是**给人看的**：用 `utf-8-sig` 读，用户拿记事本改过（带 BOM）也不会打出乱码方块。
这套读口由 `selfcheck.py` 的 **T31e** 守着（含「未就绪时**不写收件箱**」那条）。

> 顺带说明：看门狗在启动阶段只能 `pid=None`（那时还不知道 pid），也就是**枚举全机所有
> yjks.exe，但只登记不动手**；拿到自有 pid 之后会立刻 `narrow()` 收窄到本实例，此后才按
> `RULES` 应答 —— 不会再对**别人正在用的** YJK 的对话框乱点。未命中 `RULES` 的框默认
> 不应答（`DEFAULT = None`），授权/许可类框永不自动应答。

### 收件箱「就绪」判据（别再只看文件在不在）

`send` 以前只做 `os.path.exists(_yjk_inbox.ready)`。这个文件**会残留**：host 被硬杀
（taskkill／断电）时收尾不执行，文件留在盘上，于是 `send` 返回 **0** 并把命令写进收件箱，
**却没有任何进程在读它** —— 命令静默石沉大海。

现在 `send` 会逐条校验（**任一失败都判「未就绪」并 rc=2**，fail-closed）：内容首字段是不是
PID · 那个 PID 是不是**活着的本包宿主** · 心跳（mtime）是否在 `READY_STALE`（120s）内。
心跳由收件箱轮询循环每 2 秒续写，它还能覆盖 PID 校验查不出的一类：**宿主还活着、但收件箱
循环已经卡死/退出**。

### 命令执行中实例消失：**立刻**返回，不再阻塞到超时

`yjks` 被硬杀/自己崩时结果事件永远不来。老版一直阻塞到 `timeout`（收件箱路径 **900s**），
而循环正卡在那条命令里 → `exit` 读不到 → 现场表现为「不响应 exit，只能强制收尾」
（50 案例 F01/F02：各 **180.1s**）。现在 `Client.run()` 每 2 秒查一次实例存活，实例一没就
立刻返回 `实例已退出(N.Ns…)`、记入失败台账（`host` 收尾 **rc=2**）、outbox 留结果行，循环
随即回去处理 `exit`。自检 **T33** 守着这条。

### 导入校验闸门**自触发**（不依赖链条里有没有 `yjk_save`）

老版把待校验 `.ydb` 记下、**等 `yjk_save` 才核**；`CALC_CHAIN` 里没有 `yjk_save`，所以
`yjk_importydb` 紧接 `@calc` 时校验**静默地从未运行**（审计 **S11**）。现在只要下一条命令
不是 `yjk_save`，会自动补一步保存再核，不通过就跳过本轮剩余命令（outbox 多条
`<序号>|yjk_save(自动补)|…`）。自检 **T32** 守着这条。

### 写回类脚本的退出码（`column-section-opt`）

这两个脚本会**把改好的 `.ydb` 写到 `--dst`**，然后跑自检。自检不过时**文件已经落盘**，
但退出码不是 0 —— 编排必须按退出码判定，不能因为「文件在、屏幕没 traceback」就当成功：

| 退出码 | 谁返回 | 含义 | 编排该怎么办 |
|---|---|---|---|
| 0 | `write_sections.py` / `split_stdflr.py` | 自检全过，`--dst` 可用 | 继续导入/计算 |
| 1 | 同上 | **文件已写出，但没全部成功**（逐条 `!!` 清单） | **停止**，修正输入后重跑；不要导入计算 |
| 2 | 同上 | 脚本没跑起来（参数/输入文件/技能目录不对） | 修参数，`--dst` 不会被写 |

* `write_sections.py` rc=1：等级表里的标准层不存在 · `tblStdFlr.Para` 放不下四个下标 ·
  截面清单的层不存在或一条 UPDATE 都没命中 · 柱段改写 0 个 · 写入后逐格反查不一致 ·
  全局 `idNew` 撞号（YJK 按 `idNew` 去重会**静默丢构件**）。
* `split_stdflr.py` rc=1：跨标准层引用自检不过 · **`idNewBzc` 与所属标准层 `idNew` 不一致**
  （后果是导入丢弃自然层 `tblFloor=0`、几何全丢）· 有标准层没有自然层。
* `--grades` 的层号范围要和模型里真实的标准层对得上：拿 `expand_plan.py` 打印的
  `--grades` 串（按模型现算），别写死 `"1-40:50"`。

> 这一族缺陷（**屏幕上报了问题、退出码却是 0**）在本包出现过两次，现在由 `compat_check.py`
> 的 **[4] 退出码纪律**静态守着：凡是有 `problems.append(` 的脚本，必须存在非零退出路径
> （`sys.exit(非0)` 或 `sys.exit(main())`；`sys.exit(0)` **不算**）。往包里加新的自检脚本时，
> 这条不变量要一起满足。

### 规范复核的退出码（`verify_results.py --strict`）

| 退出码 | 含义 | 编排该怎么办 |
|---|---|---|
| 0 | 全部复核项取到值且满足 | 通过 |
| 3 | 有项**没核**（位移角未解析到 / wdisp.out 缺失）| 别当通过；补结果或查格式 |
| 4 | 规范指标**不满足**（wpj/配筋率/Uc/位移角/刚度比） | 打回，看 `不满足项` |
| 1 | **本工具不适用或对不上**：模型没有柱（纯剪力墙）· wpj 柱号与模型对不上 | 看 `!!` 那行说明；这是**拒绝**不是通过 |

**4 优先于 3**。JSON 里可机械读：`判定` / `不满足项` / `未取到` / `位移角来源` /
`位移角全部哨兵` / `位移角哨兵交叉印证`。位移角全 `1/9999` 是**满足**（YJK 的上限哨兵，
实测位移 0.2mm/3600mm），但脚本会用同文件的 `h`/`Max-D` 列**现算交叉印证**；印证矛盾或
做不成都会写在 `位移角哨兵交叉印证` 里 —— 别自己把 `位移角: {}` 读成"没核"。

---

## 五之三、编码约定


### 规则表（可用 `encoding_check.py` 静态检查，0 = 合规）

| 规则 | 要求 | 不遵守会怎样 |
|---|---|---|
| R1 | 源码与文本产物 **UTF-8、无 BOM** | BOM 被当成正文：按字节读首字段的解析失败（收件箱就绪标志的首字段本该是 PID） |
| R2 | 所有 `open()` 显式 `encoding=`（文本 `utf-8`；人改过的配置/标志文件 `utf-8-sig`） | 按系统 locale（cp936）打开：读 UTF-8 抛 `UnicodeDecodeError`，写中文落成 GBK |
| R3 | `print` 含非 GBK 字符（`✅❌⚠²³−`）时必须能兜底 | GBK 控制台抛 `UnicodeEncodeError` → 命令以**退出码 1** 中断（文件其实已经写好） |
| R4 | 读 YJK 自己的输出（`*.out`、`设计结果\*.txt`、`中间数据\*`、`dsnctrl.ini`）用 **`gbk`** | 乱码，且通常**不报错**，只是解析出 0 条记录 |
| R5 | CLI 入口有控制台兜底 | 同 R3 |
| R6 | `subprocess` 抓文本输出指定 `encoding=` | 按 locale 解码：中文变乱码，错误信息失去价值 |
| R7 | `json.dump(..., ensure_ascii=False)` + `encoding="utf-8"` | 中文被写成 `\uXXXX`，人不可读 |
| R8 | 兜底要在 **`main()`** 里调用；没有 `main()` 的库模块放在对外入口函数里 | 只在 `__main__` 分支里兜底时，被 import 当库用仍会崩 |
| R9 | `.py` 首两行声明 `# -*- coding: utf-8 -*-` | 被别的编辑器另存成别的编码后，问题推迟到运行时才暴露 |

### 调用本包脚本的固定写法

```powershell
& $py -X utf8 -B <脚本.py> ...          # -X utf8：让解释器用 UTF-8 做 stdio
$env:PYTHONIOENCODING = "utf-8"          # 兜底（子进程/管道场景）
```

### 实测口径（抽查 1500 余个产物）

包自己写的文本产物（`.json` / `.txt` / `.md`）全部是**无 BOM 的 UTF-8**；
同一批目录里那些"不是 UTF-8"的文件（`dsnctrl.ini`、`中间数据\Yjkcombine\*`、
`yjkwindforce.txt`、`工程名称_M--建模版本号.txt`、`计算书\工程量统计\工程量统计.ini`）
都是 **YJK 自己写的 GBK 文件**——所以读它们必须按 GBK（R4）。
"包产物合规 / YJK 产物按 GBK 读"这两件事可以分别复验，验证脚本见工作区
`verify_products_encoding.py`。

---

## 六、首次自检六步（照抄，逐级加深）

```powershell
$py = "<带 pythonnet 的 python.exe>"          # 或 ~/.yjk-auto/venv/Scripts/python.exe
$S  = "<整套技能的根>"

# ① 环境自检：不需要真的算，秒级
& $py -X utf8 -B "$S\yjk-auto-drive\scripts\yjk_probe.py"
#   期望：输出里出现「[2] 结论 …… 环境齐备」；退出码 0
#   退出码 1 = 还有阻断项，按它逐条 -> 提示处理

# ② 离线逻辑自检：不需要 YJK，秒级
& $py -X utf8 -B "$S\yjk-auto-drive\scripts\selfcheck.py"
& $py -B "$S\yjk-auto-drive\scripts\selfcheck.py"          # ★ 不加 -X utf8 再跑一遍
#   期望：两次都「逻辑断言：通过 244，失败 0」+ 退出码 0
#   其中 T31 专门守「六份找驱动的副本不许漂移」（块内容 / 候选顺序 / 不许写死桌面）：
#   你把整套技能换地方装、或改了其中一份的查找链，它都会立刻变红并点名是哪一份。

# ③ 可移植性自检：秒级
& $py -X utf8 -B "$S\yjk-auto-drive\scripts\portability_check.py"
& $py -B "$S\yjk-auto-drive\scripts\portability_check.py"   # ★ 不加 -X utf8 再跑一遍
#   期望：两次都「结论：通过」+ 退出码 0（= 没有未列入白名单的设备/工程耦合写法）

# ④ ★ 跨 agent 兼容性守卫：秒级，**换 agent / 换机器时最该先跑这个**
& $py -X utf8 -B "$S\yjk-auto-drive\scripts\compat_check.py"
& $py -B "$S\yjk-auto-drive\scripts\compat_check.py"        # ★ 不加 -X utf8 再跑一遍
#   期望：两次都退出码 0。六份「查找实现」能力矩阵全 OK + 4 组技能间重复副本逐字节一致
#        + 4 个 reporter 脚本的「退出码纪律」合规 + 5 个 SKILL.md 的 frontmatter 齐全。
#        -X utf8 下结论行是「结论：✅ 通过」；默认 GBK 下是「结论：? 通过」—— **都是通过**，
#        退出码必须都是 0。（加不加 -X utf8 都跑，正是为了守住第五节的编码问题：
#        这两个自检脚本曾经在默认 GBK 下**恒定返回 1**，而结论其实是对的。）
#   为什么要它：「找驱动技能 / 找技能根」这段逻辑在本包里被复制了六份
#   （各技能要能独立安装，在找到驱动目录之前没法 import 它的 paths.py）。
#   复制可以接受，但**它们会漂移** —— 真实发生过：厂商路径只在部分副本里、
#   通用扫描只在另一部分副本里，于是"能不能找到"取决于你恰好跑了哪个脚本；
#   而且本机一直"看着能用"，只是因家目录里正好有一份旧副本。
#   这个守卫把六份副本必须共有的最低能力（三个环境变量、同级相对路径、
#   与厂商无关的通用扫描、找不到时明确报错、不写死桌面）变成硬断言，
#   并顺带守住 `draw_quant.py` / `read_yjk_xlsx.py` / `dlgwatch.py` / `impcheck.py`
#   这四组「两个技能各存一份、必须逐字节相同」的副本（只改一份就会静默行为分叉）。

# ⑤ 官方建模接口能不能写盘（历史上踩过会挂死的坑）
& $py -X utf8 -B "$S\column-section-opt\scripts\driver.py" where
& $py -X utf8 -B "$S\column-section-opt\scripts\driver.py" createydb
#   where     -> 打印「驱动技能目录：<...>\yjk-auto-drive」
#   createydb -> 打印「CreateYDB 探测：**OK**（写出了 N 字节的 probe.ydb）」+「结论：OK」；退出码 0
#   非 0 时不代表环境坏：官方建模接口在本机写不了盘，建模改走
#   「骨架 ydb + 序列化」路径（见 column-section-opt/scripts/frame_build.py）

# ⑥ 编码守卫：秒级，不需要 YJK
& $py -X utf8 -B "$S\yjk-auto-drive\scripts\encoding_check.py"
#   期望：输出「结论：通过 —— 编码约定全部满足」+ 退出码 0
#   它查的编码约定：文本文件 UTF-8 无 BOM · open() 显式给 encoding= · 读 YJK 输出用 GBK ·
#   非 GBK 输出有控制台兜底、且只在 main() 里调用 · subprocess 抓文本指定 encoding ·
#   json.dump 用 ensure_ascii=False
#   退出码 1 = 有违规，逐条给出文件:行号
```

第 ①~④ 与 ⑥ 步全绿 = 这套技能在这台机器上"逻辑上可用"；要证明"真能算"，再加
`yjk_probe.py --runtime`（真启动一次、真建工程、真写盘，判据是**文件 mtime**）。

> 第 ① 步就报 `No module named 'clr'` / `No module named 'System'` 的话，别去查包的代码 ——
> 先用 `driver.py python` 换成带 pythonnet 的解释器（见第一节末尾那个专节）。

---

## 七、换 agent 时的注意事项

1. **不要假设某个"把文件推给用户"的专有工具存在。** 报告/结果一律把文件路径回报给用户，
   提示可直接打开即可。（本包原先在某处写了这种专有工具名，已改成中性说法。）
2. **长时任务不要用超长超时阻塞等待。** 实测一轮 `@recalc` 约 **64~72 s**（28 层框架-核心筒、
   16 核机器；旧文档写的"约 5 分钟"是**过时的**）。按"你自己的实测 × 2~3"设超时 —— 上面这个
   样本给 **150 s** 就够。超时太大只会让"弹了模态框/卡住"这类故障晚十分钟才被发现；超时应
   当被当作"该去查日志"的信号，不是"再多等等"。耗时表见 `yjk-auto-drive/SKILL.md`
   的「耗时量级参考」。
3. **不要并行跑两个 YJK 会话**（IPC 事件是全局的，见第一节第 4 条）。
4. **判断成功不要看命令的返回值**，只看文件是否真的变了（mtime / 大小）。命令秒回成功却
   什么都没做，是本包踩过最多的坑。
5. **改了代码先跑第 ②③ 步自检**（秒级、不需要 YJK），再动真机。改动任何一份「找驱动技能」
   的查找链时，T31 会要求你六份一起改 —— 这是故意的：这六份过去就漂移过（厂商路径只在部分
   副本里、通用扫描只在另一部分里），结果是"能不能找到驱动"取决于用户恰好跑了哪个脚本。

---

## 八、已知的、故意保留的"不通用"之处

这些不是遗漏，是**已评估后决定保留**的（换机器/换 agent 不需要改）：

| 现象 | 为什么保留 |
|---|---|
| `selfcheck.py` 里约 30 处绝对路径 | 合成测试向量（虚构盘符下的假工程/假 exe 路径），测的就是**路径与命令行解析**，不依赖真实设备 |
| `paths.py` 里的 `python.exe` / 盘符字符串 | 那个文件**就是**解释器与安装位置的探测器，它必须枚举这些候选 |
| `portability_check.py` 里的正则 | 它**就是**在"搜这些模式"，模式串本身不是耦合 |
| `dlgwatch.py` / `yjkw.py` 的 `windll` / `PostMessageW` | 本包天生 Windows-only（YJK 是 Windows 应用），没有替代品 |
| `decode("gbk")` / `utf-16` | YJK 就写 GBK 和 UTF-16LE 文件（见第五节） |
| `openpyxl` / `psutil` / `clr` | 真实依赖（见第二节），不是可选项 |
| `~/.workbuddy-ai/...` 的候选路径 | **历史遗留路径，保留以不破坏现有用户**：那条路径仍然可达，但已**不是前提**（去掉它其余各档照样工作），任何 agent 的技能目录都能被通用扫描到 |
| 六份「找驱动技能」的候选链是**重复代码** | **故意的、有界的**：业务技能在找到驱动目录之前没法 import 它的 paths.py（鸡生蛋），所以每份必须自带最小回退。回退只保留三样（环境变量 + 同级目录 + 通用扫描 + 中立位置），其余一律委托给 `paths.py`（本包契约里"唯一找东西的地方"）。`selfcheck.py` 的 T31 把七处逐条比对，**漂移会立刻变红** |
| 文档里少数 YJK 安装目录举例 | 只出现在"如 / 例"形式的出处说明里（`YJK.CUI` 是命令名的权威来源），不是运行时依赖 |
