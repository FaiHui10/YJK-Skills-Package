# 新电脑前置准备清单（用户基础工作）

目标：让"脚本全自动驱动 YJK"在某台电脑上跑通。只做一次，约十分钟。
每项给出「做什么 / 为什么 / 怎么验证 / 没做的故障表现」。

> 一句话：装好 YJK + 改两处 Config.ini + 一个带 pythonnet 的 Python + 一份官方 DLL。这些都能用脚本一键或半自动完成。

---

## 0. 总览与自检入口

准备完成后，用一条命令验收：

```powershell
& $py -X utf8 -B "<技能目录>\scripts\yjk_probe.py"
```

输出 `[2] 结论` 显示「环境齐备」即完成。加 `--runtime` 会真启动一次并连一下，
用 `yjk_save` 的**文件 mtime** 作为通过判据（这是唯一可信的证据）。

---

## 1. 安装 YJK 并能正常打开工程

- **做什么**：装 YJK **6.1 或更高**（7.x 更好，本文按 7.1 说明）；手动打开一个自带算例，确认能进界面、能算。
- **为什么**：全自动链路依赖 `yjks.exe` 与 `YjkLauncher.exe`。
- **怎么验证**：双击 `yjks.exe` 能到欢迎页；打开一个工程标题形如 `<工程全路径> - 盈建科软件`。
- **故障表现**：`yjk_probe.py` 报「未找到 yjks.exe」→ 设环境变量 `YJK_DIR=<安装目录>` 后重跑；或先手动开一次 YJK（运行中的进程是最好的线索，脚本会读到它的路径）。

## 2. 两处 `Config.ini` 补 `[YJKSControl] Flag = True`

- **做什么**：在两处 Config.ini 里补上（这是"启动即自动开 IPC"的关键）：
  ```ini
  [YJKSControl]
  Flag = True
  ```
  - YJK 安装目录：`<YJK安装目录>\Config.ini`（如 `C:\YJKS\YJKS_7_1_0\Config.ini`）
  - 用户配置目录：`%ProgramData%\yjkSoft\<版本目录>\Config.ini`
    （如 `C:\ProgramData\yjkSoft\YJKS7.1.0\Config.ini`，有的版本还有 `\YJKS\Config.ini`）

- **一键完成**：
  ```powershell
  & $py -X utf8 -B "<技能目录>\scripts\yjk_probe.py" --fix-config
  ```
  它会自动**发现所有** Config.ini 并写入（没有该段就补整段），不写死路径。

- **为什么**：官方《运行说明》第 5 条 —— 要在自动启动 YJK 时就开启 yjkscontrol，必须用这个方式在 Config.ini 里配置。6.1+ 也可以启动后键入 `yjksIPCControl` 开启，但那需要人工键入，而自动化键入做不到（见下）。
- **怎么验证**：`yjk_probe.py` 该项显示 `[OK]` 且列出命中的 Config.ini。
- **故障表现**：yjks 起来了、CPU 也在跑，但 `yjk_probe.py` 报「Config.ini 的 Flag 不是 True」；`yjk_auto.py status` 显示两个 IPC 事件为 `False`。

### 为什么不能"自动键入 yjksipccontrol"

命令行 `Edit` 控件能找到（主窗口下 `(11,989)-(639,1001)`），`WM_CHAR` 也能把文字写进去（回读 `'命令:yjksipccontrol'`），**但回车无法被接受** —— `PostMessage`/`SendMessage` 送 `VK_RETURN` 均无效，物理按键又需要前台焦点；**锁屏时（前台是 `LockApp.exe`）根本抢不到焦点**。这条路不通，必须靠 `Flag=True`。

> 官方文档里写的是 `Flag = False`（默认关闭）。改成 `True` 后，正常界面下的手工使用会受影响（官方提示"否则无法进入正常界面下的 yjk"），所以**不建议长期开着**：跑自动化时设 True，用完改回 False。本技能的 `--fix-config` 只负责设 True。

## 3. 准备一个带 pythonnet 的 Python 环境

- **做什么**：
  ```powershell
  & $py -X utf8 -B "<技能目录>\scripts\setup_env.py"
  ```
  它会在 `~/.yjk-auto/venv` 建隔离环境，安装 `pythonnet`（`clr`）、`openpyxl`、`psutil`，
  并把可用解释器路径记到 `~/.yjk-auto/python.txt`（后续脚本自动复用）。
- **为什么**：驱动走 `clr` 反射调用官方 DLL。pythonnet 是驱动 7.1 的关键依赖。另外 **Python 版本别太新**：pythonnet 对 3.14 的支持常滞后，建议 **3.10~3.13**。
- **怎么验证**：
  ```powershell
  & "<~/.yjk-auto/venv/Scripts/python.exe>" -c "import clr;print('CLR-OK')"
  ```
- **离线机器**：先在有网机器上下好 wheel，或换国内镜像 `-i https://pypi.tuna.tsinghua.edu.cn/simple`。
- **故障表现**：`ModuleNotFoundError: No module named 'clr'`。

## 4. 取得官方客户端 `YJKAPI.dll`

- **做什么**：从官方开源仓库 **`gitee.com/yjk-opensource/csharp-yjks`** 的 **7.1 分支**取 `不依赖YJK案例/dll/YJKAPI.dll`，放进技能目录的 `assets/`：
  ```
  <技能目录>\assets\YJKAPI.dll
  ```
  或者放到任意位置并设环境变量 `YJKAPI_DLL` / 用 `--dll` 参数指定。
- **为什么**：这是 IPC 调用的入口类型 `YJKIPC.YJKSControl`。
- **本技能已内置一份可用的**：直接把 `assets/` 连同 `YJKAPI.dll`、`YAPIData.dll` 拷到新电脑即可（约 290 KB）。
- **怎么验证**：`yjk_probe.py` 显示「控制客户端 DLL ... 类型=YJKIPC.YJKSControl」。
- **不要用错**：
  | 文件 | 结果 |
  |---|---|
  | 官方仓库 `不依赖YJK案例/dll/YJKAPI.dll` | 类型 `YJKIPC.YJKSControl`，`RunCmd` 2 参 |
  | 安装目录 `STCAD\YJKSControl.dll` | 类型 `YJKSControl`，`RunCmd` 3 参（含 `out`），可用兜底 |
  | 安装目录 `STCAD\YJKAPI.dll` | **不含控制类型**（本技能会自动跳过并说明） |
  | 8.x SDK 的原生库 | 与 7.1 原生库互斥，别混用 |

## 5. 保证全机只有一个 `yjks.exe`

- **做什么**：每次开工前先清场：
  ```powershell
  & $py -X utf8 -B "<技能目录>\scripts\yjk_auto.py" kill
  & $py -X utf8 -B "<技能目录>\scripts\yjk_cleanup.py"        # 只清无主窗口的残留（预演）
  ```
- **为什么**：官方《运行说明》明确警告「不要启动多个支持外部控制的 yjks.exe，否则执行外部控制会引发异常」。多实例互抢 `Global\ShareMemoryEvent` / `Global\WaitResaultEvent`，症状极具迷惑性 —— **有 `Success` 应答、`RunCmd` 秒回，但命令根本不执行**。
- **怎么验证**：`yjk_auto.py status` 的「yjks 实例数=1」。
- **故障表现**：`yjk_save` 不写盘、计算命令 CPU 不动。

---

## 附：跑通后的最小验收脚本

```powershell
$py = "<~/.yjk-auto/venv/Scripts/python.exe>"
$D  = "<技能目录>\scripts"

# 1) 自检（含 Config.ini 修正）
& $py -X utf8 -B "$D\yjk_probe.py" --fix-config

# 2) 清场
& $py -X utf8 -B "$D\yjk_auto.py" kill

# 3) 全自动：建工程 → 导入 → 预处理 → 计算
& $py -X utf8 -B "$D\yjk_auto.py" host `
    --dir "<工作目录>" --name Auto1 `
    --import "<模型.ydb>" --prep --calc

# 4) 看结果文件个数（30 层工程一次约 70 个文件）
Get-ChildItem "<工作目录>\设计结果" | Measure-Object
```

（`<工作目录>` / `<模型.ydb>` 换成你自己的路径。文档里一律不写具体盘符 —— 照抄别人的路径是换机器后最常见的"看起来跑通了其实没算"来源。）

**判据**：第 3 步日志里 `设计结果/ 共 N 个`，且 `设计结果\wmass.out` 的 mtime 是刚刚。不要看 `RunCmd` 的返回值。
