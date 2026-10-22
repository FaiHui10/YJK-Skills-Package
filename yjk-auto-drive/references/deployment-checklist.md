# 新环境部署检查清单

适用：**Windows 10/11 x64**；YJK **6.1 / 7.x / 8.x**；任意 agent（Trae / Claude Code / Codex / Cursor…）。
用法：从上到下逐项打勾。每步都写了「期望结果」，不符合就查 §8 对照表。
原理细节见 `setup-checklist.md`，故障排查见 `troubleshooting.md`。

---

## 0. 开工前确认

- [ ] 目标机是 **Windows x64**（YJK 只有 Windows 版）
- [ ] 能**手动**启动 YJK、完成授权签出、打开一个自带算例并算完
- [ ] 知道目标机**是否联网**（首次装 pythonnet 需要联网）
- [ ] 当前账号能写用户目录（`%USERPROFILE%`），必要时有管理员权限

---

## 1. 拷贝技能文件

**目标位置**：当前 agent 的技能目录，常见为

| agent | 技能目录 |
|---|---|
| Trae | `%USERPROFILE%\.trae-cn\skills\` |
| Claude Code | `%USERPROFILE%\.claude\skills\` |
| Codex | `%USERPROFILE%\.codex\skills\` |
| 其它 / 自定义 | 任意目录（需设 `YJK_SKILLS`，见 §7） |

- [ ] 拷贝**整个** `yjk-auto-drive`，且确认带上了：
  - [ ] `scripts\`（8 个 .py）
  - [ ] `assets\YJKAPI.dll`
  - [ ] `assets\YAPIData.dll`
  - [ ] `SKILL.md`、`references\`
- [ ] 拷贝**整个** `yjk-colmodel`（`SKILL.md`、`scripts\yjk.py`、`scripts\yjkio.py`、`references\`）
- [ ] 可选：`column-section-opt`、`column-scheme-comparison`、`beam-layout-oneway`
      （本技能只做可选联动，缺了会自动跳过）
- [ ] **删掉** `__pycache__`、`*.pyc`（不同 Python 版本之间会互相干扰）
- [ ] 目录名保持 `yjk-auto-drive` / `yjk-colmodel` 不变（脚本按 `__file__` 定位，改上级目录无影响）

**期望结果**：`<技能>\yjk-auto-drive\scripts\yjk_probe.py` 与
`<技能>\yjk-colmodel\scripts\yjk.py` 都存在。

---

## 2. Python 环境

- [ ] 找一个 **Python 3.8+**
- [ ] `yjk-colmodel`：**无需第三方包**，直接可用
      ```powershell
      & "<python>" -X utf8 -B "<技能>\yjk-colmodel\scripts\yjk.py" --help
      ```
- [ ] `yjk-auto-drive`：需要 **pythonnet(clr)**，先体检：
      ```powershell
      & "<python>" -X utf8 -B "<技能>\yjk-auto-drive\scripts\setup_env.py" --check
      ```
      - 通过 → 记下该解释器路径
      - 不通过 / 需隔离环境 → 执行：
        ```powershell
        & "<python>" -X utf8 -B "<技能>\yjk-auto-drive\scripts\setup_env.py" --python "<python>" --force
        ```
- [ ] 不想每次写路径：设环境变量 `YJK_PY=<解释器绝对路径>`

**期望结果**：`python -c "import clr;print('CLR-OK')"` 输出 `CLR-OK`；
或 `setup_env.py` 在 `%USERPROFILE%\.yjk-auto\venv` 建好环境并打印其解释器路径。

---

## 3. YJK 与授权

- [ ] 记录 YJK 版本（`6.1.0` / `7.1.0` / `8.1.0`…）
- [ ] 首次启动已**完成授权签出**（`YjkLauncher.exe` 正常，无未授权弹框）
- [ ] **YJKSControl 的 API 授权码已申请**（官方明确该功能需授权，否则命令无效）
- [ ] `Config.ini` 已开通道：
      ```powershell
      & "<python>" -X utf8 -B "<技能>\yjk-auto-drive\scripts\yjk_probe.py" --fix-config
      ```
      - 6.x / 7.x：确认 `[YJKSControl] Flag=True`
      - 8.x：仍建议开着；8.x 真正生效靠 `initConfig`（技能自动做）
- [ ] 目标机没有其它人/agent 正在用 YJK 做别的工程

**期望结果**：`yjk_probe.py` 中「Config.ini 已开 [YJKSControl] Flag=True」为 `[OK]`。

---

## 4. 控制 DLL 选择（按版本）

| 版本 | 用哪个 | 检查项 |
|---|---|---|
| **8.x** | 安装根 `<YJK安装目录>\YJKAPI.dll` | - [ ] 文件存在<br>- [ ] 能力含 `initConfig / RunYJK / exit` |
| **6.x / 7.x** | 技能 `assets\YJKAPI.dll`（+`YAPIData.dll`） | - [ ] 两个文件都在<br>- [ ] 类型为 `YJKIPC.YJKSControl` |

- [ ] **没有把 8.x 的 DLL 拷进 `assets\` 覆盖 7.1 版**（两者互斥，同一进程只能加载一种）
- [ ] 若 8.x 识别错：设 `YJK_DIR=<安装目录>` 后重跑 probe

**期望结果**：probe 打印

```
[OK  ] 控制客户端 DLL
       <安装目录>\YJKAPI.dll
       类型=YJKIPC.YJKSControl  来源=YJK 安装根（8.x 新 API）
```

---

## 5. 四项验证（全绿才算部署完成）

### 5.1 环境自检
```powershell
& "<python>" -X utf8 -B "<技能>\yjk-auto-drive\scripts\yjk_probe.py"
```
- [ ] Python 有 pythonnet
- [ ] YJK 安装位置命中，版本正确
- [ ] Config.ini 通道已开
- [ ] 控制客户端 DLL 与版本匹配
- [ ] yjks 实例分类正常

### 5.2 离线逻辑自检
```powershell
& "<python>" -X utf8 -B "<技能>\yjk-auto-drive\scripts\selfcheck.py"
```
- [ ] 末尾输出 `逻辑断言：通过 106，失败 0`
      （`T12 real_opt` / golden 若提示 `[--] 未找到…跳过`，属于可选技能缺失，不算失败）

### 5.3 模型只读自检
```powershell
& "<python>" -X utf8 -B "<技能>\yjk-colmodel\scripts\yjk.py" doctor <模型目录>
```
- [ ] 找到 `g-of.ymd`
- [ ] `tblColSect / tblColSeg / tblFloor / tblStdFlr / tblGroup / tblProperty` 全部「有」
- [ ] 打印「模型代际」（6.x/旧版 / 7.x / 8.x）
- [ ] 完整性校验通过（无悬空 SectID、ID 无重复）

### 5.4 活体连接（可选，但新机器建议做一次）
```powershell
& "<python>" -X utf8 -B "<技能>\yjk-auto-drive\scripts\yjk_probe.py" --runtime --proj-dir "<工程目录>"
```
- [ ] 能启动/接管实例并收到命令应答
- [ ] 8.x 收尾正常 `exit`，无幽灵进程

---

## 6. 烟测：真跑一轮计算

用一个小模型（1～3 层即可）：

```powershell
& "<python>" -X utf8 -B "<技能>\yjk-auto-drive\scripts\yjk_auto.py" host `
    --dir "<工作目录>" --name smoke --import "<小模型.ydb>" --prep --calc
```

- [ ] 实例启动成功、工程创建成功
- [ ] `.ydb` 导入成功
- [ ] 「生成数据 + 全部计算」跑完
- [ ] `设计结果\` 下有结果文件，`wmass.out` 有内容
- [ ] 收尾后没有残留的自有 yjks（`status` 复核）

> 8.x 附加确认：`host` 自动 `initConfig(Version/Pid)`；若用 `--pid N` 接管已在运行的实例，
> 不会杀、不会重启。

---

## 7. 环境变量一览（按需，不是全要设）

| 变量 | 作用 | 何时设 |
|---|---|---|
| `YJK_DIR` / `YJK_ROOT` | 指定 YJK 安装目录 | 自动探测失败时 |
| `YJK_PY` / `YJK_PYTHON` | 指定带 pythonnet 的解释器 | 机器上有多个 Python 时 |
| `YJKAPI_DLL` | 指定控制 DLL | DLL 不在默认候选链时 |
| `YJK_CONFIG` | 指定 `Config.ini` | 配置在非标准位置时 |
| `YJK_SKILLS` | 技能根目录（供跨技能自检/golden 查找） | 技能不在 agent 默认目录时 |

---

## 8. 部署登记表（填完存档）

| 项 | 值 |
|---|---|
| 机器名 / 使用人 | |
| 操作系统 | |
| YJK 版本 / 安装目录 | |
| 控制 DLL 路径 / 能力 | |
| Python 解释器 | |
| pythonnet 是否可用 | |
| 技能根目录 | |
| 验证日期 / 验证人 | |

---

## 9. 失败对照（快速定位）

| 现象 | 原因 | 处理 |
|---|---|---|
| `ModuleNotFoundError: clr` | 解释器没有 pythonnet | §2 跑 `setup_env.py`，或设 `YJK_PY` |
| `找不到可用的控制 DLL` | 8.x 只找到 assets 的 7.1 版 | 设 `YJK_DIR` 指向安装目录，重跑 probe |
| `ReflectionTypeLoadException` | 用 `LoadFile` 加载 8.x 安装根 DLL | 技能已用 `chdir + LoadFrom`，勿自行改回 |
| 命令返回 OK 但 YJK 无反应（8.x） | 没调 `initConfig` | 用 `host`（自动调）或 `host --pid N` |
| `Config.ini … Flag=False` | 通道未开 | `probe --fix-config`，或手工改 `Flag=True` |
| 命令一直阻塞 / 弹窗卡住 | `RunCmd` 阻塞，弹窗没人应答 | 见 `troubleshooting.md` §5 |
| `RunCmd` 返回 `None`（8.x） | 8.x 重载返回 `void`，不是失败 | 以文件 mtime / 窗口状态判成功 |
| `doctor` 报 `no such column` | 模型不是本技能预期的 schema | 先看「模型代际」；6.x 旧库用 9 列回退 |
| 技能目录写不进去 | 沙箱保护 | 运行加 `-B`；编辑用编辑器工具 |

---

## 10. 回滚与清理（可选）

- 关闭自有实例：`yjk_auto.py close --pid <PID> --yes`；全杀：`yjk_auto.py kill`
- 删除用户缓存：`%USERPROFILE%\.yjk-auto`（会丢掉 venv 与实例登记，不影响系统 Python）
- 卸载技能：删除技能目录即可，脚本不写注册表、不装系统级包

---

## 验收标准（一句话）

**§5 四项全绿 + §6 烟测通过 + §8 登记表填完**，即视为新环境部署完成。
