# 故障排查：施工图 + 工程量统计

按「你看到什么」查表。底座问题（启动/导入/计算/通道）见
`yjk-auto-drive/references/troubleshooting.md`，本文只收本环节特有的坑。

---

## 快速分诊

```
跑完 draw_quant.py 了，看什么？
├─ 退出码 2                      → 找不到 yjk-auto-drive（设 YJK_DRIVER_DIR）
├─ 退出码 1，日志说导入校验不通过   → §1 导入了空模型
├─ 退出码 1，日志停在「等待 IPC 通道」→ §8 启动失败 / IPC 未就绪
├─ 退出码 1，设计结果 0 个文件     → 计算失败；看 设计结果/fea.dat-ERR.txt
└─ 退出码 0，但产物不对
    ├─ 一个 Excel 都没有          → §2 顺序错了（混凝土跑在了施工图后面）
    ├─ 板钢筋表只有表头、合计 0    → §3 缺 stdslab_AutoStatstl
    ├─ 命令 TIMEOUT / 挂死        → §4 模态框没人应答
    ├─ Excel 有数字但读出来全 0    → §5 钢筋表读法三个坑
    ├─ openpyxl 直接报错           → §6 styles.xml 颜色值非法
    └─ 墙钢筋全是 0                → §7 先确认本工程有没有墙
```

**永远先看** `<留档目录>/_draw_quant.log`（逐条命令 + 耗时 + 实际产出）和
`run_manifest.json`，再看 `watch.errors`（模态框错误留档）。

---

## §1 退出码 1：导入了空模型

**症状**：日志里 `导入校验：★不通过★`，几何表整表为 0；或（更早的版本）直到计算才报
`fea.dat-ERR.txt: 模型中没有单元数据 / 计算分析失败[-45]`。

**根因**：`yjk_importydb` 收到相对路径。YJK 按它自己的工作目录（工程目录）解析 → 找不到
文件 → 弹「文件不存在」→ 若被放行，「导入」了一个空模型，而命令照样返回 `OK(1.1s)`。

**客观判据（逐表核对几何表行数）**

| table | 源模型 | ✔ 成功 | ✘ 失败 |
|---|---|---|---|
| `tblJoint` | 45 | 45 | **0** |
| `tblBeamSeg` | 76 | 76 | **0** |
| `tblColSeg` | 45 | 45 | **0** |
| `tblSlab` | 32 | 32 | **0** |
| `tblFloor` | 3 | 3 | **0** |

- **不要拿 `tblProperty` / `tblProjectPara` 当判据** —— save 会展开它们
  （`tblProperty` 2 → 473、`tblProjectPara` 1169 → 1172），属正常。
- **字节数相等只能作辅助**，save 会重写库。

**正确顺序**

```python
from impcheck import abs_ydb, check
ydb = abs_ydb("models/S0.ydb")          # ★ 一律转绝对路径
cli.run("yjk_importydb", ydb, 600)
cli.run("yjk_save", "", 300)            # ★ .ymd 是 save 写出的
check(ydb, os.path.join(wd, "S0.ymd"))  # 不通过抛 ImportFailed
```

早于 `yjk_save` 开 `.ymd` → `sqlite3.OperationalError: unable to open database file`。

**看门狗配套**：`RULES` 已把 `("文件不存在", IDCANCEL)` / `("不存在", IDCANCEL)` /
`("读取错误", IDNO)` 当错误处理（不再默认回「是」放行）。

**连带出现的框**（同一根因）：「未正常退出建模模块,是否补充楼层连接关系分析?」→ 回否；
「整体模型计算时出错，是否打开日志文件？」→ 回否（别去开日志）。

---

## §2 一个 Excel 都没有（顺序错了）

**症状**：混凝土 `工程量统计.ini` 有、施工图 DWG 有，但 `施工图/全楼*钢筋用量*.xlsx`
一个都没有；日志里那 5 条 `DtlRC_*` 全是 `OK(0.0s)`、`无产出`。

**根因**：`yjkconcreteStat_statCom` 排在了施工图链之后。它归属**建模模块**
（`IDModule_Layer`），切过去会冲掉施工图上下文，此后所有 `DtlRC_*` 统计命令退化成空操作
且不报错。

**处置**：顺序必须是 **混凝土 → 施工图 → 钢筋**。`draw_quant.py` 的
`main()` 已按此排列（`CONC_CHAIN` → `DRAW_CHAIN` → `REBAR_CHAIN`）。
自己拼链时务必照抄。

> 顺带更正：`yjkconcreteStat_statCom` 不是空操作 —— 之前判它无效，
> 是因为把它挂在了 `IDQUANTITYLIST_DETAIL` 标签下。

---

## §3 板钢筋表只有表头、合计 = 0

**根因**：缺了 `stdslab_AutoStatstl`（全楼楼板钢筋统计）；只跑到 `StdSlab_batgenstl` 不够。

**板钢筋完整链（缺一不可）**

```
SetCurrentLabel IDDTL_DETAIL_SLAB
→ StdSlab_RedrawNceng     绘新图
→ StdSlab_AUTOCAL         计算
→ StdSlab_batgenstl       批量出图 + 选筋   ← 会弹模态框
→ stdslab_AutoStatstl     全楼钢筋统计      ← ★ 就是它让数字非 0
```

判据：写出 `全楼楼板钢筋用量.dat` 与 `SlabStlQuantity1.dat`。

---

## §4 命令 TIMEOUT / 挂死：模态框没人应答

**根因**：`StdSlab_batgenstl` 弹「施工图已经进行过选筋,是否重新选筋?」。模态期间 yjks
主窗口被 `Disable`，IPC 命令从此不返回。

**唯一有效的应答方式**（其余全无效）

```python
_u.PostMessageW(dlg, 0x0111, IDNO & 0xFFFF, _u.GetDlgItem(dlg, 7))
```

无效清单：`BM_CLICK(0x00F5)`、给按钮发键盘消息、`WM_CLOSE`、`SendMessage` 模拟点击。
原理与 `find_dialogs()` 枚举代码见 `yjk-auto-drive/references/troubleshooting.md` §12。

**检查项**：`DialogWatch` 是否真的起来了（`draw_quant.py` 在 `Client()` 就绪后
`watch.start()`）；`watch.seen` / `watch.errors` 是否为空。

---

## §5 Excel 有数字，但我读出来全 0（最隐蔽）

**三个要点（按易错程度排序）**

1. **不能用「包含」匹配找合计行**。板的标题行是 `['', '全楼楼板钢筋用量', …]`，含「全楼」
   二字，会被当成合计行 —— 那一行直径列全空 → 读成 0，表现得像"统计没生效"，会让人跑去
   重跑 YJK（白跑）。**必须让楼层列（索引 1）精确等于** `全楼` / `合计` / `总计`。

   ```python
   TOTAL_WORDS = {"全楼", "合计", "总计"}
   key = str(r[1]).strip() if len(r) > 1 and r[1] is not None else ""
   if key not in TOTAL_WORDS:
       continue
   ```

2. **直径行在表头行的下一行**。表头行只有合并的 `'HRB400'` 标题，没有数字，在表头行上找
   直径一无所获。做法：在前 10 行里找出现 ≥2 个 4~50 数值的那一行。

3. **表尾有一行只重复总计数字**（板 r8 / 梁 r20 / 柱 r12），第一列是空的 —— 不能用"第一个
   数字行"当合计。

**另一个方向的易错点**：取「第N层」行当单层值，不要取「全楼/合计」行 —— 拿合计行当单层会把
面积和用量放大 3 倍（层数倍），且看起来"很合理"。

---

## §6 openpyxl 打不开 YJK 的 xlsx

**症状**：`ValueError: Colors must be aRGB hex values`。

**根因**：YJK 写出的 `xl/styles.xml` 里有非 aRGB 的 `rgb` 值（如 `rgb="auto"`、6 位色值），
并可能带越界的 `theme=` / `indexed=`。

**处置**：把 xlsx 当 zip 读出来，在内存里修好 `styles.xml` 再交给 openpyxl，不动原文件
（`read_yjk_xlsx.py`）：

```python
txt = re.sub(r'rgb="([^"]*)"', rep, txt)          # 6 位补成 "FF"+6 位；非法置黑
txt = re.sub(r'\s(?:theme|indexed)="[^"]*"', "", txt)
```

---

## §7 墙钢筋全是 0

**先别急着当故障**：本工程可能没有剪力墙。`全楼墙钢筋用量.xlsx` 为 6×6 布局、只有
「合计(kg)」列，无直径列 —— 无墙时全 0 是合法结果。

判据：`parse_rebar()` 返回 `({}, None)` = 无直径列 = 该构件没有钢筋（正常）；返回
`({}, "未找到全楼合计行")` = 真的没读到（异常）。`summary_xlsx.py` 的自检页按此区分，
先判 `rebar_zero` 再判内容。

---

## §8 启动失败 / IPC 未就绪（退出码 1，日志停在「等待 IPC 通道」）

**症状**：日志里 `!! 启动失败 / IPC 未就绪`，之后什么都没做。

**按顺序排查**

1. **有没有弹框没人应答。** 这是最常见的。看日志里的 `[对话框]` 记录 —— 看门狗若是在
   启动之后才拉起来的，启动阶段弹的框就没人应答，会白等满 150s。现在的做法是
   `DialogWatch(None)` 在 `boot_yjks()` 之前 `start()`：`pid=None` 阶段（pid 还不知道）
   只登记不动手，等收窄到自有实例后才按 `RULES` 应答，所以启动阶段的框也会被登记下来。
2. **有没有残留的 `yjks.exe`。** 开工前必须全机只有 1 个（见 `yjk-auto-drive` 硬性约束 3）。
   清场：`python yjk-auto-drive/scripts/yjk_auto.py kill`
3. **两处 `Config.ini` 的 `[YJKSControl] Flag` 是否都是 `True`。**
   一键修：`python yjk-auto-drive/scripts/yjk_probe.py --fix-config`
4. **冷启动慢。** 干净环境下通道就绪约需 23~36s。若每次都逼近 150s 超时，先用
   `yjk_probe.py` 看环境。
5. **收工确认 `yjks` 已退出。** 脚本的 `finally` 会清掉自己登记的实例；但若被 `head` /
   `Ctrl-C` 之类打断管道，进程会被信号杀掉、`finally` 来不及跑，留下残留实例 —— 下次
   开工的第 1 步会把它清掉，知道这点能省一次困惑。

---

## 附：本环节"看起来像成功"的假象

1. `yjk_importydb` 返回 `OK(1.1s)` → **可能导入了空模型**（§1）。
2. `DtlRC_*` 返回 `OK(0.0s)` → **可能什么都没做**（§2）。
3. `工程量统计.ini` 存在 → 内容可能只有 `[INFO]`，没有 `Gcl-Hnt-Zrc*` 段。
4. DWG 文件存在 → 可能是上一次运行的遗留（看 mtime）。
5. 钢筋表有数字 → 可能读到的是合计行而不是单层行，或反之（§5）。

**唯一可信**：`impcheck` 的逐表行数比对、文件 mtime、`run_manifest.json` 的
`产物` 列表、`watch.errors`。
