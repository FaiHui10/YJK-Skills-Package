# IPC 通道原理与原生兜底协议

官方文档缺失、或官方 DLL 不可用时，靠这层自救。

---

## 一、通道是怎么建立的

```
yjks.exe 无参启动
   → 读 Config.ini 的 [YJKSControl] Flag
      Flag=True  → 自动创建两个全局命名事件 + 一块共享内存 → 通道就绪（约 10~18s）
      Flag=False → 通道不建；须在 YJK 里键入 yjksIPCControl 手动开启
```

**通道就绪的可观测特征**（`yjk_auto.py status` 直接显示）：

| 对象 | 类型 | 说明 |
|---|---|---|
| `Global\ShareMemoryEvent` | Event | 命令投递信号 |
| `Global\WaitResaultEvent` | Event | 结果就绪信号 |
| `shared_memory` | 共享内存 1024 B | 命令与结果的双向缓冲区 |

官方《运行说明》要点：
- 6.1+ 可不用改 Config.ini，**启动后键入 `yjksIPCControl`** 即可；
- **要在自动启动 YJK 时就开启，必须用 Config.ini 的 Flag 方式**；
- **不要启动多个支持外部控制的 `yjks.exe`，否则执行外部控制会引发异常**。

---

## 二、官方客户端（推荐路径）

```python
import clr
from System import Array, Object
from System.Reflection import Assembly

asm = Assembly.LoadFile(r"...\YJKAPI.dll")
T   = asm.GetType("YJKIPC.YJKSControl")
run2 = [m for m in T.GetMethods()
        if m.Name == "RunCmd" and len(m.GetParameters()) == 2][0]
arr  = Array[Object](("yjk_save", ""))     # 无参命令也要补一个空串
run2.Invoke(None, arr)
```

**为什么用反射、不直接 `import`**：`import YJKAPI` 会触发模块初始化并 `WinExec` 再拉起一个 `yjks.exe`（绕过 `YjkLauncher` 的启动流程）→ 每跑一次脚本多一个无窗口实例 → 多实例抢事件、主窗口被顶崩。反射方式 + **绝不调 `init()`** 可以完全避免。

### 两种 DLL 的签名差异（本技能的 `Client` 自动适配）

| 来源 | 类型名 | `RunCmd` 参数 |
|---|---|---|
| 官方仓库 `csharp-yjks` 7.1 分支 `不依赖YJK案例/dll/YJKAPI.dll` | `YJKIPC.YJKSControl` | `(string keyword, string param) → string` |
| YJK 安装目录 `STCAD\YJKSControl.dll` | `YJKSControl` | `(string keyword, string param, out string result)` |
| YJK 安装目录 `STCAD\YJKAPI.dll` | — | 不含控制类型，别用 |

`Client` 按 `RunCmd` 的参数个数自动选择：`<=2` 直接传两个，`==3` 补一个空串收 `out`。
安装目录版本还有 `init(String,String)` 与 `waitEventCreate()`，**都不要调**。

### 为什么必须后台线程调用

`RunCmd` 阻塞。命令触发模态对话框时它**一直不返回**，所以 `Client.run()` 把调用丢到后台线程并 `join(timeout)`；超时后返回 `TIMEOUT(>Ns)`，不假装失败，也不杀进程。

配套的弹窗处理（另起后台线程反复 `EnumWindows` 找 `#32770` 对话框）：

- **只应答写进 `RULES` 的框**（「重新选筋」「是否删除」→ 否；「文件不存在」→ 取消）。未命中规则的框**默认不应答**（`DEFAULT = None`），只登记、只打日志，留给人工 —— 盲答一个看不懂的框，等于替用户确认了一件本包没理解过的事。
- 授权/许可类框一个按钮都不点，交上层暂停等用户。
- 还没拿到自有实例 pid 时（`pid=None`）只登记不动手，`narrow(pid)` 之后才应答。
- 不要"含「保存」就点「是」"：计算进度窗上就有「中止计算」，见"确定"就点会把计算掐断。

---

## 三、原生兜底协议（无官方 DLL 时）

协议已按 IL 逆向核实。**共享内存布局**（1024 B，UTF-8）：

| 偏移 | 长度 | 内容 |
|---|---|---|
| `[0..15]` | 16 | `IPC_Cmd`（结果标志，如 `Result`/`Success`） |
| `[16..63]` | 48 | 命令名 |
| `[64..]` | 960 | 参数（结果也在这一段回写） |

**握手顺序**（关键，不能错）：

```
1. 映射共享内存 "shared_memory" (1024B, FILE_MAP_ALL_ACCESS)
2. 打开事件 Global\ShareMemoryEvent / Global\WaitResaultEvent
3. memset(共享内存, 0)
4. 写入命令到 [16..]，参数到 [64..]
5. ResetEvent(WaitResaultEvent)      ← 先清结果信号
6. SetEvent(ShareMemoryEvent)        ← 再投递命令
7. WaitForSingleObject(WaitResaultEvent, timeout)
8. 读 [0..15] / [64..] 取结果
```

ctypes 关键调用：

```python
h = k32.OpenFileMappingW(0x000F001F, False, "shared_memory")
p = k32.MapViewOfFile(h, 0x000F001F, 0, 0, 1024)
ev_s = k32.OpenEventW(0x00100002, False, r"Global\ShareMemoryEvent")
ev_w = k32.OpenEventW(0x00100002, False, r"Global\WaitResaultEvent")
```

**原生通道的应答不可轻信**：多实例冲突时，`Result/Success` 会照常出现在共享内存里，但命令根本没执行。判据永远只能是文件 mtime / 窗口标题 / CPU 增量。

---

## 四、多实例冲突为什么这么难查

两个（或更多）`yjks.exe` 同时活着时：

```
脚本 SetEvent(ShareMemoryEvent)
  → 事件是 Global\ 命名对象，**所有实例都收到**
  → 某个实例处理并 SetEvent(WaitResaultEvent) → 脚本以为成功
  → 但"真正持有工程"的那个实例可能压根没收到/没执行
```

症状清单：

| 症状 | 说明 |
|---|---|
| `RunCmd` 秒回、返回 `Success` | 应答来自**错误实例** |
| `yjk_save` 不写盘 | 文件 mtime 无变化 |
| 计算命令 CPU 不动 | 计算没真的开始 |
| 命令"有时灵有时不灵" | 取决于哪个实例先抢到 |
| YJK 主窗口"莫名其妙被关掉" | 无窗口实例抢事件把主窗口顶崩 |

**处置**：开工前 `yjk_auto.py kill`；只清无窗口残留用 `yjk_cleanup.py --apply`（它按"有没有 `yjks` 类主窗口"区分，不碰你在用的界面）。

---

## 五、窗口标题作为状态探针

yjks 的主窗口类名固定是 `yjks`，标题格式：

```
<工程全路径> - 盈建科软件        （有工程）
 - 盈建科软件                    （欢迎页/空工程）
```

「工程是否已建立」「当前打开的是哪个工程」都能从标题读出来，比等文件落盘更快（新建的工程要保存才落盘）。`env.py` 与 `yjk_auto.py` 都用这个。

---

## 六、锁屏 / 无人值守

- 本链路**不依赖** UI 自动化（不注入键鼠、不抢焦点），**锁屏也能跑**。
- 反过来，任何"往界面里键入文字"的方案（如自动键入 `yjksipccontrol`）在锁屏时彻底不可用：前台是 `LockApp.exe`，`SetForegroundWindow` 无效，`PostMessage(VK_RETURN)` 也不被接受。
- 结论：**用 Config.ini 的 `Flag=True`，不要依赖键入。**
