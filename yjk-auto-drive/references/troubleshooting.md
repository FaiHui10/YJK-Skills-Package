# 故障排查：症状 → 根因 → 处置

按「你看到什么」查表。绝大多数问题都落在下面 9 种里。

---

## 快速分诊

```
命令有应答吗？
├─ 没有 / 报异常
│   ├─ ModuleNotFoundError: clr      → §1 pythonnet 缺失
│   ├─ 找不到 DLL / 无 YJKSControl 类型 → §2 客户端 DLL
│   └─ No method matches given arguments → §3 参数个数/重载
└─ 有应答（Success / OK）但没效果
    ├─ 两个 IPC 事件为 False        → §4 Config.ini Flag 未开
    ├─ 事件为 True、但命令秒回 0.1s  → §11 带 .yjk/-open 启动（工程根本没打开）
    ├─ yjks 实例数 > 1              → §5 多实例冲突 最常见
    ├─ 命令秒回 0.0s 且之后全无效    → §6 通道绑在旧上下文（UIOpen 后遗症）
    ├─ TIMEOUT(>Ns)                 → §7 模态框阻塞
    ├─ 导入 OK 但计算报"模型中没有单元数据" → §13 导入了空模型
    └─ 写盘命令无文件变化            → §5 / §8 工程正被打开
```

**永远先跑** `python yjk_probe.py`，它把 §1~§5 全查了。

---

## §1 `ModuleNotFoundError: No module named 'clr'`

**根因**：当前解释器没有 `pythonnet`。

**处置**：
```powershell
& $py -X utf8 -B "<技能>\scripts\setup_env.py"      # 自动建隔离环境并安装
```
然后**用打印出来的那个 python** 跑其他脚本。若是 3.14 等过新版本导致装不上，改用 **3.10~3.13**：
```powershell
& $py -X utf8 -B "<技能>\scripts\setup_env.py" --python "<你机器上 3.10~3.13 的 python.exe>" --force
# 不知道有哪些可选的，先看一遍：python setup_env.py --check
```

---

## §2 找不到客户端 DLL / 类型不存在

**根因**：`YJKAPI.dll` 来源不对。

**对照表**：

| 你用的文件 | 结果 |
|---|---|
| 官方仓库 7.1 分支 `不依赖YJK案例/dll/YJKAPI.dll` | 首选，`YJKIPC.YJKSControl` |
| 安装目录 `STCAD\YJKSControl.dll` | 兜底可用，`YJKSControl`（3 参 `RunCmd`） |
| 安装目录 `STCAD\YJKAPI.dll` | 不含控制类型 |
| 8.x 的原生库 | 与 7.1 互斥 |

**处置**：把正确的 `YJKAPI.dll` 放到 `<技能>\assets\`，或设环境变量 `YJKAPI_DLL=<路径>`，或用 `--dll <路径>`。`yjk_probe.py` 会打印它实际用了哪个、以及为什么跳过了别的。

---

## §3 `No method matches given arguments`

**根因**：`RunCmd` 重载选错。`YJKSControl` 有 `RunCmd(kw, para)` 与 `RunCmd(kw, p1, p2)` 两种，**无参命令也必须补空串**。

**处置**：用本技能的 `Client`（自动挑参数最少且能匹配的重载）；自己写代码时记得 `RunCmd("yjk_save", "")` 而不是 `RunCmd("yjk_save")`。

---

## §4 两个 IPC 事件为 `False`

```
IPC 事件 Global\ShareMemoryEvent = False
IPC 事件 Global\WaitResaultEvent = False
```

**根因**：`Config.ini` 的 `[YJKSControl] Flag` 不是 `True`，通道没建。

**处置**：
```powershell
& $py -X utf8 -B "<技能>\scripts\yjk_probe.py" --fix-config
```
（它会发现所有 Config.ini 并写入；不写死路径）然后重启 yjks。

> 顺带：官方默认值是 `False`，且提示"否则无法进入正常界面下的 yjk"。建议跑自动化时设 `True`、用完改回 `False`。

---

## §5 有应答但不执行（多实例冲突）

**这是最难查的一个。** 表现：

- `RunCmd` 秒回 `OK(0.0s)` 或返回 `Success`
- `shared_memory` 里 `Result` 应答正常
- **但** `yjk_save` 不写盘、计算命令 CPU 不动

**根因**：`Global\ShareMemoryEvent` / `Global\WaitResaultEvent` 是**全局命名对象**，所有 yjks 实例都能收到事件，应答来自**错误的实例**（官方《运行说明》明确警告多实例会引发异常）。
**多实例为什么会积累**：`import YJKAPI` 会自动 `WinExec` 拉起一个**无窗口** yjks。

**处置（"实例隔离"策略）**：先分类，再决定动作 —— **只操作自有实例，绝不关别人的**：

```powershell
& $py -X utf8 -B "<技能>\scripts\yjk_auto.py" status        # 按 自有/你在用/无窗口残留 分类
```

| 类别 | 判定 | 动作 |
|---|---|---|
| 自有 | `~/.yjk-auto/own.json` 里登记的 PID | `host` 收尾 `kill_own()`；`--keep` 可保留 |
| **你在用** | 有 yjks 类主窗口、且不在登记里 | **不碰**。`host` 直接拒绝开工（运行中出现则停手），提示你自行关闭 |
| 无主窗口残留 | 无 yjks 类顶层窗口（`YJKAPI.init`/`WinExec` 拉起） | 默认不碰；要清加 `--clean-orphans`，或用 `yjk_cleanup.py --apply`（默认只预演） |

```powershell
& $py -X utf8 -B "<技能>\scripts\yjk_auto.py" host ... --clean-orphans   # 只清无窗口残留
& $py -X utf8 -B "<技能>\scripts\yjk_auto.py" kill                        # 全清（人工逃生口）
```

**为什么不能"锁定到某个实例去操作"**：两个事件是 `Global\` 命名对象，`RunCmd` 不带 PID，**所有实例都会收到**，应答可能来自错误的那个。所以"多实例共存 + 结果可信"在物理上不成立 —— 只能靠**独占**（发现冲突就停/拒），不能靠路由。

**硬性约束：发命令前全机只能有 1 个 `yjks.exe`（且那个是自有的）。** 判定成功只认文件 mtime / 窗口标题 / CPU 增量 —— `RunCmd` 的返回值和 `Success` 应答在冲突时照样出现，一文不值。

---

## §6 命令秒回 0.0s 且此后全部无效

**根因**：用过 `UIOpen`。它忽略路径、只开出空工程，之后通道像**绑在旧上下文**上，所有命令退化成 0.0s 秒回无效果（纯英文/规范路径都无效）。

**处置**：杀掉实例重来，并且**改用 `UINew` + `yjk_importydb`** 打开模型。

---

## §7 `TIMEOUT(>Ns)`

**根因**：`RunCmd` 阻塞 —— 命令弹了模态框，或计算确实很久。

**处置**：

- 先看屏幕上有没有对话框（更新、未保存提示…）。
- 弹窗应答要在**另一个后台线程**里做，不能"等命令返回再处理"。
- 应答规则：只答 `RULES` 里显式列出的框（「是否重算/重新选筋」「是否删除」「是否退出」→ 否，「文件不存在」→ 取消）；**其余只登记不点击**，授权/许可类框一个按钮都不点。
- 模态框长期不消时主窗口会被置为 `Disable`（用 `IsWindowEnabled(hwnd)` 确认），用 §12 的 `DialogWatch` 后台应答。**别重启 YJK**（§5 的多实例坑等着你）。

---

## §8 写盘/导入后没变化

排查顺序：

1. **工程是否正被 YJK 打开？** 从外部改正在被打开的 `.ymd` 会把 yjks 弄崩。
   ```powershell
   & $py -X utf8 -B "<技能>\scripts\env.py" --proj-dir "<工程目录>"
   # 看最后一行「本工程是否正被打开」应为「否（可安全写盘）」
   ```
2. **是否多实例？** → §5。
3. **导入判据 = 逐表核对**（不是字节数）：`yjk_importydb` + `yjk_save` 之后，用 `scripts/impcheck.py` 比对源 `.ydb` 与 `<工程名>.ymd` 的几何表行数 —— 必判表 `tblJoint/tblColSeg/tblBeamSeg/tblWallSeg/tblFloor/tblStdFlr` 必须逐表相等；`tblSlab/tblAxis/tblProperty/tblProjectPara` 会**合法地变**，不作判据。详见 §13。
   `tblLoadSeg` 是**半放宽**的：导入会把"每层一份的荷载定义"并成一份、重新编号标准层、把条数重排
   （实测塔楼：源 4576 条 / 每层 104 → 工程 10488 条 / 逐层 104~360，一条没丢），
   所以它**不按总条数判**，而是按**自然层号逐层**判：源里有荷载的层，工程里也必须有荷载；
   只有"整批静默丢失"（`Type` 写错时工程里一条都没有）才判不通过。
   （字节数只能作旁证：`save` 会重写模型库，`tblSlab` 的增删也会改它。）
   若导入成功但内容不对（例如柱截面全回退），问题在**模型本身的外键**，不在这条驱动链 —— 见 `column-section-opt` 技能的「模式 B」。
   若命令返回 OK 而 `--dir` 里**一个文件都没变**，先查**目录错配**（会话盯的目录 ≠ YJK 打开的工程目录）—— 见 §13 末尾。
4. **等待方式**：不要固定 `sleep`。用文件 mtime / 窗口标题做条件等待。

---

## §9 jyks 起不来 / 起来就退

| 现象 | 处置 |
|---|---|
| 找不到 `yjks.exe` | 设 `YJK_DIR=<安装目录>`，或先手动开一次 YJK |
| 起来了但 30s 内退出 | Launcher 未就绪 → 先手动启动一次 `YjkLauncher.exe` |
| `PermissionError [WinError 5]` 启动失败 | 父进程在 job 对象里，`CREATE_BREAKAWAY_FROM_JOB` 被拒；`spawn()` 已逐档降级 `0x1000208 → 0x208 → 0x200 → 0` |
| 宿主脚本退出后 yjks 还在 | **正常现象** —— yjks 不受宿主生命周期约束，不会自动回收。`host` 已在 `finally` 里显式 `kill`；自己写脚本时收尾也要 `kill_all()`，否则残留实例下一轮会抢事件（§5） |

---

## §10 无人值守 / 锁屏

- 本链路**不需要** UI 自动化，**锁屏也能跑**（不注入键鼠、不抢焦点）。
- 但**锁屏时任何"往界面键入文字"的方案都失效**（前台是 `LockApp.exe`）—— 所以必须用 `Flag=True` 而不是自动键入 `yjksipccontrol`。
- 需要连续下命令时用 `host --inbox --stay N` 让宿主常驻 —— 理由是**省掉反复重启的开销**（每次 12s + 启动开销），**不是因为**宿主退出会杀掉 yjks（不会，见 §9）。

---

## §11 带 `.yjk` / `-open` 启动：事件有、命令无效

**症状**：`status` 显示两个 IPC 事件都是 `True`，但

- `yjk_save` / `yjk_repair` 等建模命令**秒回 `OK(0.1s)`**（正常流程里是 2~3s）
- **写盘命令完全没有文件变化**（`.ymd` 的 mtime 与大小都不动）
- 窗口标题**只到目录级、不含工程名**（形如 `<盘符>:\...\open_test\ - 盈建科软件`）

**触发方式**：`yjks.exe -product YJKS -open <某工程>.yjk`，或把 `.yjk` 路径当裸参数传给 yjks。

**观测对照**：

| 观测 | 结果 |
|---|---|
| 窗口标题出现命令行里的路径 | t≈25s |
| 两个 IPC 事件为 True | **t≈35s**（无参启动约 12~16s） |
| `SetCurrentLabel IDDSN_DSP` | `OK(4.1s)`（切标签这类 UI 动作仍会执行，具**欺骗性**） |
| `yjk_repair` / `yjk_save` | `OK(0.1s)`，T.ymd mtime 与大小**均未变化** |
| 工程是否真的打开 | **否** —— 标题里没有工程名 |

**根因**：`Flag=True` 只在**无文档启动**时建立可用的控制通道。带文档启动时事件对象会被创建，但通道没绑到已加载的模型上，建模命令全部落空。

**处置**：**不要**试图用 `-open` 驱动真工程。要"打开已有模型"就按硬性约束 1：无参启动（欢迎页）→ `UINew` 建工程 → `yjk_importydb` 导入模型。

> 判据提醒：**"IPC 事件存在"不是通道可用的证据**。永远发一条写盘命令，看文件 mtime。

---

## §12 模态对话框：命令"永久不返回"的唯一正确解法

**症状**：某条命令卡住 >120s 无任何新文件；`RunCmd` 永不返回；YJK 主窗口 `IsWindowEnabled() == False`（被置灰）。看起来像 YJK 死了，其实是在等一个对话框。

**诊断**（枚举本进程的可见 `#32770` 顶层窗口）：

```python
import win32gui, win32process, win32api
def find_dialogs(pid):
    out = []
    def cb(h, _):
        if win32gui.GetClassName(h) != "#32770": return True
        if not win32gui.IsWindowVisible(h): return True
        if win32process.GetWindowThreadProcessId(h)[1] != pid: return True
        body = []
        def cc(ch, _):
            if win32gui.GetClassName(ch) == "Static":
                t = win32gui.GetWindowText(ch)
                if t.strip(): body.append(t.strip())
            return True
        win32gui.EnumChildWindows(h, cc, None)
        out.append((h, win32gui.GetWindowText(h), " / ".join(body)))
        return True
    win32gui.EnumWindows(cb, None)
    return out
```

**实例**（`StdSlab_RESELECTREIN`）：弹 `yjks7.1.0` 框，正文 `施工图已经进行过选筋,是否重新选筋?`，子控件 `Button '是(&Y)'`(id 6) / `Button '否(&N)'`(id 7)。此时 IPC 完全堵死，直到对话框被应答。

**唯一有效的应答方式**：

```python
WM_COMMAND = 0x0111
IDYES, IDNO, IDOK, IDCANCEL = 6, 7, 1, 2
btn = win32gui.GetDlgItem(dlg_hwnd, IDNO)          # 标准控件 ID
win32api.PostMessage(dlg_hwnd, WM_COMMAND, IDNO & 0xFFFF, btn or 0)
```

**无效的方式**：`BM_CLICK (0x00F5)` 打在按钮上、`WM_KEYDOWN/WM_KEYUP` 空格打在按钮/对话框上、`WM_CHAR 'N'`、`WM_CLOSE` —— 全部无效，对话框纹丝不动。

**无人值守要点**：必须在**后台线程**里轮询应答（不能等命令返回再处理）。未命中 `RULES` 的框**默认不应答**（`DEFAULT = None`），只登记 + 打一行日志 —— 旧版是 `DEFAULT = IDYES          # 没匹配上时默认「是」，但会留档告警`，已改掉：看不懂的框留给人工，比盲答安全。

```python
class DialogWatch(threading.Thread):
    RULES = [("重新选筋", IDNO), ("是否删除", IDNO), ("是否退出", IDNO)]
    DEFAULT = None           # 未命中规则不应答（只登记、只打日志）
    interval = 1.2           # 秒
```

每轮 `find_dialogs(pid)` → 匹配标题/正文关键词决定点「是」还是「否」→ `WM_COMMAND` 应答。
**匹配不上的一律留档不点**，收工后回看 `.seen`。`WM_COMMAND` 应答后主窗口自动恢复 `Enable`，命令随即正常返回。

> 写 `RULES` 时的原则：**问「是否重算/重新选筋」→ 否**（前面步骤已经算好了）；
> 问「是否中止/退出」→ 否。没把握的框一律不写进 `RULES`，让它挂着、由超时报出来。

---

## 附：四条"看起来像成功"的假象（务必记住）

1. `RunCmd` 返回 `OK(0.0s)` —— 多实例下照样出现，**不代表执行了**。
2. `shared_memory` 里出现 `Result` / `Success` —— 同样不保证执行。
3. 命令耗时很短 —— 可能是被错误实例"秒回"了。
4. **两个 IPC 事件都是 `True`** —— 带文档启动的实例也会建事件，命令却全不执行（§11）。

**唯一可信的判据**：文件 mtime 变化、窗口标题变化、CPU 时间增量。

---

## 附 2：批量无人值守时被 safe-delete 拦截

`yjk_auto.py kill_own()` 会调 `own_clear()`，而 `own_clear()` 是 `os.remove(~/.yjk-auto/own.json)`。批量循环跑多方案时，这条删除会被 safe-delete 钩子拦下，抛出的**不是 `Exception` 子类**，所以 `try/except Exception` 抓不到，整个批次直接中断（表现为"只跑了第 1 个方案"）。

**处置**：在自己脚本里直接打补丁 —— `own.json` 反正会被下一次 `own_claim()` 覆盖，根本不需要删：

```python
import yjk_auto as Y
Y.own_clear = lambda *a, **k: None
```

同时把清场那一步的 `kill_own()` 包进 `try/except`。注意返回 `BaseException` 的钩子用 `except BaseException` 更稳。

---

## §13 导入了空模型：`模型中没有单元数据` / `计算分析失败[-45]`

**症状**

```
计算阶段失败，<工作目录>\设计结果\fea.dat-ERR.txt 里：
    模型中没有单元数据.
    存在非法数据，计算中止.
    模型文件读取错误.
    计算分析失败[-45].
    任务处理失败(-45)
```

但 `yjk_importydb` **当时返回的是 `OK(1.1s)`**，一路无异常。

**根因（两个现场都验过）**

1. `yjk_importydb` 收到了**相对路径**（如 `models/S0.ydb`）。YJK 按**它自己的工作目录**（工程目录）解析这个相对路径 → 找不到 → 弹「文件不存在」框 → 该框一旦被放行，**就会导入一个空模型**，而命令**照样返回 OK**。
2. 源 `.ydb` 本身是**半写状态**（序列化器清完表之后中途抛异常，库能打开、表结构完整，但几何表是空的）。导入"成功"，其实什么都没进来。

两种情况的共同点：**错误直到计算阶段才暴露，现场已被污染，一整轮计算白跑。**

**客观判据（唯一可信）**：导入 + `yjk_save` 之后**逐表核对几何表行数**：

| 级别 | table | 作用 | 成功导入 | 失败导入 |
|---|---|---|---|---|
| **必判** | `tblJoint` | 节点 | 与源一致 | **0** |
| **必判** | `tblColSeg` | 柱段 | 与源一致 | **0** |
| **必判** | `tblBeamSeg` | 梁段 | 与源一致 | **0** |
| **必判** | `tblWallSeg` | 墙段 | 与源一致 | **0** |
| **必判** | `tblFloor` | 自然层 | 与源一致 | **0** |
| **必判** | `tblStdFlr` | 标准层 | 与源一致 | **1**（骨架自带那一行） |
| **必判** | `tblLoadSeg` | 梁上荷载 | **逐层**都有荷载 | 一条都没有 |
| 参考 | `tblAxis` | 轴网 | —— | **合法地变**：1008 → 280（合并共线轴） |
| 参考 | `tblSlab` | 板块 | —— | **合法地变**：336 → 364（拆分/补板） |

- **`tblSlab` 不能当判据**：YJK 在导入/save 时会拆分与补板，行数本来就会变（实测 336 → 364）。**把它要求成"与源一致"，会把一对完全正确的导入判成失败** —— 这个坑真踩过（拿 336→364 的好样本反复校验通不过，白白怀疑导入路径）。
- **`tblLoadSeg` 只按"逐层有没有"判，不按总条数判**：导入会把"每层一份的荷载定义"并成一份、重新编号标准层、把条数重排/展开（实测 200 m 塔楼：源 4576 条 / 每层 104 → 工程 10488 条 / 逐层 104~360，**一条没丢**）。要求"总条数相等"会把正常重排判成"模型没进来"、把一整轮打断 —— 这个坑也真踩过。要拦的是 `Type` 写错导致的**整批静默丢弃**（那种情况工程里一条都没有，仍然判不通过）。改判据的实现在 `impcheck.py::_loadseg_by_floor`。
- **不要拿 `tblProperty` / `tblProjectPara` 当判据** —— `yjk_save` 会把它们展开（2 → 5518、1169 → 1172），这是**正常**行为。
- **字节数相等只能作辅助** —— save 会重写库，且 `tblSlab` 的增删也会改字节数。

**正确顺序（`.ymd` 是 `yjk_save` 写出的，不是导入写出的）**

```python
from impcheck import abs_ydb, check
ydb = abs_ydb("models/S0.ydb")          # 一律转绝对路径
cli.run("yjk_importydb", ydb, 600)
cli.run("yjk_save", "", 300)            # 校验必须排在这后面
ok, rep = check(ydb, os.path.join(wd, "S0.ymd"), strict=False)   # 不通过就别往下跑
```

早于 `yjk_save` 去开 `.ymd` 会得到 `sqlite3.OperationalError: unable to open database file`。

底座已把这一关做成自动闸门（`yjk-auto-drive/scripts/impcheck.py`，判据就是上面这张表，只依赖 sqlite3）：`host` 的导入步与收件箱 `@recalc` 的导入步都会自动跑；不通过时打印逐表对照 + 失败块并**中止**，`host` 还会**以退出码 2 收尾**。`yjk-draw-takeoff/scripts/impcheck.py`、`floor-system-comparison/scripts/impcheck.py` 是**同源副本**（出图/方案对比前也做这一关），底座改了要**一起同步**（三份 MD5 应相同）。

**同类但不同的症状：导入 OK、`--dir` 里却"没有文件变化"**

命令返回 OK 而工作目录**一个文件都没变**时，先别怀疑导入 —— 先看**目录**：用 `UINew` 在别的目录开过第二个工程时，命令成功在**那个**工程里，而文件变更闸门盯的是 `--dir`。底座现在每条收件箱命令前都会比对"会话目录 vs 窗口标题里的工程目录"，错配就明确报出两个路径并停手（见 SKILL.md「会话目录错配」）。**不要**静默当成"导入没生效"。

**看门狗配套**：`dlgwatch.py` 的 `RULES` 里已把 `("文件不存在", IDCANCEL)` / `("不存在", IDCANCEL)` / `("读取错误", IDNO)` 当**错误**处理（应答为取消/否，不放行），并单列进 `DialogWatch.errors`。授权/许可类框与其它未命中规则的框一律不应答，只登记 + 打日志。

**附带症状**（同一根因，会一起出现）：「未正常退出建模模块,是否补充楼层连接关系分析?」→ 必须回**否**；「整体模型计算时出错，是否打开日志文件？」→ 回否（别去开日志）。
