# scripts 契约

六个脚本：2 个是要跑的命令，4 个是被调用的库。

```
draw_quant.py ──┬─ impcheck.py     （导入校验闸门）
（命令 ①）      ├─ gcl_ini.py      （解析混凝土 ini）
                └─ dlgwatch.py     （模态框看门狗）+ yjk-auto-drive/scripts/yjk_auto.py

summary_xlsx.py ─┬─ gcl_ini.py     （混凝土）
（命令 ②）        └─ read_yjk_xlsx.py → 解析钢筋 xlsx
```

---

## ① `draw_quant.py` —— 算完 → 出图 → 出量

```bash
python draw_quant.py --ydb <模型.ydb> --proj <工程名> [选项]
```

| 选项 | 默认 | 说明 |
|---|---|---|
| `--ydb` | 必填 | 源模型 `.ydb`。**会自动转绝对路径** |
| `--proj` | 必填 | 工程名。用**英文/数字**，别用中文 |
| `--root` | 当前目录 | 工作根目录 |
| `--workdir` | `<root>/YJK_run_dq/<proj>` | YJK 工程目录 |
| `--out` | `<root>/results/<proj>` | 留档目录 |
| `--no-conc` | — | 跳过混凝土统计 |
| `--no-draw` | — | 跳过施工图 |
| `--no-rebar` | — | 跳过钢筋统计 |
| `--timeout` | 1800 | 单条计算命令超时秒 |

**退出码**：`0` 成功 / `1` 失败（导入校验不通过、计算无结果、建工程失败）/
`2` 找不到 `yjk-auto-drive`。

**产出**（`--out` 下）：`混凝土工程量汇总.txt` / `.json`、`run_manifest.json`、
`施工图/`（全部 DWG + 钢筋 Excel）、`_draw_quant.log`（日志在 `--workdir` 下）。

**内部流程**：清场 → Launcher → 拉看门狗 → `yjks.exe`(无参) → `UINew`
→ `yjk_importydb` → `yjk_save` → 导入校验 → `PREP_CHAIN` → `CALC_CHAIN`
→ 混凝土 → 施工图 → 钢筋 → 留档 → 汇总 → 清场。

**前置**：全机不能有别的 `yjks.exe`（脚本会先清场）。看门狗在启动 yjks **之前**拉起，
那时只能 `pid=None`（pid 还不知道）：这一阶段**只登记不动手**，一个按钮都不点；
`own_claim` 之后 `narrow(pid)` 收窄到自有实例，才按 `RULES` 应答 —— 未命中 `RULES` 的框
默认不应答（`DEFAULT = None`），授权/许可类框永不自动应答。

---

## ② `summary_xlsx.py` —— 汇总成 6 页 Excel

```bash
python summary_xlsx.py <留档目录> [--name 工程名] [--area 每层楼面面积m2] [--floors 层数]
```

输出 `<留档目录>/<工程名>_施工图与工程量汇总.xlsx`：

| 页 | 内容 |
|---|---|
| 1. 汇总 | 混凝土 / 钢筋 分构件小计 + 单位面积指标 |
| 2. 混凝土工程量 | 逐层 × 构件，体积 m³ |
| 3. 钢筋工程量 | 逐构件 × 直径，kg（含全楼合计） |
| 4. 施工图清单 | 每个 DWG 的大小与状态（正常 / ★不可用 / 疑似截断） |
| 5. 计算口径 | 口径说明与校核依据 |
| 6. 自检 | 交叉校核（逐层之和 vs 合计、柱体积手算对照、非零直径档数…） |

`--area` 是**每层**楼面面积，不是全楼面积（全楼 = 每层 × 层数）；不填就把钢筋表的逐层楼面
面积求和当全楼面积。层数默认从 `工程量统计.ini` 的 `Gcl-Hnt-ZrcNum` / 逐层段数推断，也可用
`--floors` 直接给。只会读，不改任何 YJK 产物。

**退出码**：`0` 自检无硬问题 / `2` 有硬问题。第 6 页（自检页）结论以 `★` 开头即为硬问题，
退出码必为 2；硬问题指缺 `工程量统计.ini`、一张钢筋用量表都没有、DWG 为 0 字节或不是 DWG、
取不到面积或层数导致单方指标算不出。`!` 开头是提示（各层构件不同、DWG 疑似截断这类正常
差异），不影响退出码。`--help` 始终 rc=0。明知留档不全仍要返回 0：加 `--allow-incomplete`
（问题照旧打印并写进第 6 页）。

---

## `impcheck.py` —— 导入校验闸门（别跳过）

```python
from impcheck import abs_ydb, check, ImportFailed
ydb = abs_ydb(path)                      # 转绝对路径 + 存在性检查
...
ok, rep = check(src_ydb, ymd, strict=False)   # 逐表比对几何表行数
```

* `GEOM_TABLES`：`tblJoint / tblGrid / tblBeamSeg / tblColSeg / tblSlab /
  tblWallSeg / tblBeamSect / tblColSect / tblFloor`
* **必判表**（`MUST_MATCH`）逐表行数须相等；`tblLoadSeg` **只看逐层有没有**：
  导入会合并"每层一份的荷载定义"、重编号标准层、把条数重排/展开
  （实测源 4576 条 / 每层 104 → 工程 10488 条 / 逐层 104~360，一条没丢），
  按总数比会把正常模型判成"没进来"。只有"源有荷载、工程一条都没有"才算失败。
* **不比** `tblProperty` / `tblProjectPara`（save 会展开，属正常）
* `wait=20.0` 秒内轮询等 `.ymd` 出现（它由 `yjk_save` 写出）
* CLI：`python impcheck.py <源.ydb> <工程.ymd>`
* 本文件与底座 `yjk-auto-drive/scripts/impcheck.py`、`floor-system-comparison/scripts/impcheck.py`
  是**同源副本**，底座改了要一起同步（三份 MD5 应相同）。

---

## `gcl_ini.py` —— 解析混凝土 `工程量统计.ini`（GBK）

```python
import gcl_ini
d = gcl_ini.parse(ini_path)      # {info, 层, problems}
print(gcl_ini.dump_text(d))      # 表格式文本报告
s = gcl_ini.summarize(d)         # {按构件种类, 合计, 逐层, 层数, 声明层数, problems}
```

`problems` 是解析中"读不到 / 被丢弃 / 对不上"的清单：缺 `Cap` 行导致整层明细被丢、字段数
≠列数、数值不是数字（含千分位 `620,861` 被逗号拆开）、`Item-Sum` 与明细之和对不上、一层
明细为空。清单非空就说明数值不可信，`dump_text()` 会把它打印出来。

CLI：`python gcl_ini.py <ini> [out.json]`

**退出码**：`0` 无数据问题 / `1` 找不到文件 / `2` 有数据问题。
`2` 指解析出的数据问题：缺 `Cap` 行、字段数≠列数、非数值、`Item-Sum` 与明细之和不符等；
`1` 即文件打不开。

---

## `read_yjk_xlsx.py` —— 修好 styles 再开 YJK 的 xlsx

```python
import read_yjk_xlsx as R
wb = R.load(path)     # 内存里修 xl/styles.xml，不动原文件
```

CLI：`python read_yjk_xlsx.py <xlsx>...`（打印前 40 行，排查用）

---

## `dlgwatch.py` —— 模态对话框看门狗

```python
from dlgwatch import DialogWatch, yjks_pids
w = DialogWatch(log=print)     # pid=None：只登记不动手（收窄到自有实例后才应答）
w.start()                      # ★ 要在启动 yjks 之前就 start()
...
w.stop()
w.seen      # [(标题, 正文, 答复)]  全部留档
w.errors    # 正文命中「文件不存在/读取错误/非法数据/出错/失败」的
```

* 唯一有效的答复方式：`PostMessageW(dlg, WM_COMMAND=0x0111, IDNO, GetDlgItem(dlg, IDNO))`
* `RULES` 按关键字决定答「是」还是「否」；命中 `ERROR_KW` 的另存一份供上层判失败
* 作用范围只有自有实例：`pid=None`（pid 未知）阶段扫到的是全机 yjks.exe，**只登记不动手**；
  `own_claim` 之后 `narrow(pid)` 收窄到自有实例才按 `RULES` 应答。未命中 `RULES` 的框默认
  不应答（`DEFAULT = None`）；授权/许可类框（`LICENSE_KW`）永不自动应答。
* 只处理 `#32770` 可见顶层窗口，不会误点系统对话框
* `yjks_pids()` 用 `tasklist` 列 `yjks.exe`，不依赖 `psutil`
* CLI：`python dlgwatch.py [pid]` —— 不带 pid 就列出所有 yjks 实例及其对话框

---

## 环境

* Python：不要写死解释器路径 —— 用 `yjk-auto-drive/scripts/paths.py` 的探测结果（它把
  `~/.yjk-auto/venv` 与各 agent 托管环境都当候选，不写死厂商名）
* 需要：`openpyxl`、`pythonnet`（后者由 `yjk-auto-drive/scripts/setup_env.py` 装）
* 依赖 `yjk-auto-drive` 的 `scripts/yjk_auto.py`。查找顺序：
  `YJK_DRIVER_DIR` → `YJK_SKILLS_DIR/yjk-auto-drive/scripts` → 同父兄弟目录 → 当前目录
  → 各 agent 的技能家目录（枚举 `~` 与 `~/.config` 的一级子目录去找
  `<D>/skills/yjk-auto-drive`，不写死任何厂商名）→ 历史遗留路径（唯一带厂商名的一档，
  保留以不破坏现有用户：去掉它其余各档照样工作；具体路径见 AGENT-COMPAT.md）。
  找不到 → 退出码 2。
