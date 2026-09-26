---
name: floor-system-comparison
description: 楼盖（楼板+梁）结构方案的经济比选 —— 不同次梁布置方式（无次梁 / 单向1道 / 单向2道 / 十字梁 / 井字梁 等）在给定柱网与荷载下的混凝土、钢筋、模板用量与造价对比。通过参数化生成 YJK 模型 → 驱动 YJK 实算取配筋 → 按广东省 2018 定额 + 广州信息价计价 → 产出可交付的 Excel 对比报告。当用户要求"不同次梁布置方式比较""楼盖方案经济比选""单向次梁 vs 井字梁哪个省钱""次梁布置对比""楼盖模板和钢筋用量统计""按广东定额算楼盖造价"时使用。
agent_created: true
---

# 楼盖方案经济比选（含 Excel 报告）

同一柱网、同一荷载下，比较若干种次梁布置方式的混凝土用量（m³）、钢筋用量（kg，必须 YJK 实算）、模板用量（m²）与按定额计价的造价。

**与相邻技能的分工**
- `yjk-auto-drive`：纯通路（启动/导入/计算/出量），无比选逻辑；`yjk_quant.py` 在它之上加了两段链（板配筋 + 工程量统计）。
- `column-section-opt`：柱截面/等级优选。
- `column-scheme-comparison`：柱截面形式（RC/CFST）比选。
- 本技能：楼盖体系（次梁布置）比选。四者互不重叠。

## 全流程

```
0) 前提：装了 YJK（7.1 及以上，能跑 IPC），Python 环境已装 pythonnet + openpyxl

1) spec.py           定义柱网/跨数/层高/荷载/各方案的次梁布置与截面      ← 改这里换项目
2) build_floor.py    调 YJK 建模 API（DataFunc）推理几何 → 生成 ydb
3) verify_ydb.py     校验生成的 ydb（表行数、节点、梁段、板块…）
4) yjk_quant.py      逐方案：建工程 → 导入 → 预处理 → 计算 → 板配筋 → 工程量统计
                     → 留档到 results/<S>/（★ 真正花时间的一步，每方案约 3~6 min）
                     运行日志写在 results/quant.log（与产物同目录；`refs/` 只放随包分发的夹具）
5) collect.py        YJK 钢筋 + 解析法算的混凝土/模板 → out/quantities.json
6) build_report.py   计价 + 出 Excel（10 页）
```

```powershell
# 解释器不要写死：优先用 yjk-auto-drive 探测/记录的那个（也可先跑 setup_env.py）
$py = Get-Content "$HOME\.yjk-auto\python.txt" -ErrorAction SilentlyContinue
if (-not $py) { $py = "python" }
cd <工程目录>
& $py -X utf8 -B scripts\spec.py                                  # 先看一眼方案摘要
& $py -X utf8 -B scripts\build_floor.py --layout S0_无次梁 --out models\S0.ydb
& $py -X utf8 -B scripts\verify_ydb.py models\S0.ydb
& $py -X utf8 -B scripts\yjk_quant.py S0 S1 S2 S3 S4              # ★ 前台跑，给足超时
& $py -X utf8 -B scripts\collect.py
& $py -X utf8 -B scripts\build_report.py
```

---

## 必须记住的七条

### 1. 板钢筋：链条缺一步就全 0
`yjk_quant.py` 的 `SLAB_CHAIN` 里，最后一步 **`stdslab_AutoStatstl`** 才让 `全楼楼板钢筋用量.dat` 有数字；少了它，表格只有表头、合计 = 0。
`StdSlab_Quantity` 不够（只写本层文件）；`StdSlab_RESELECTREIN` 单独用是死路。
详见 `yjk-auto-drive/references/commands.md`。

### 2. 模态对话框会把整条链挂死
`StdSlab_batgenstl` 会弹模态框「施工图已经进行过选筋,是否重新选筋?」，模态期间 yjks 主窗口 `Disable`、`RunCmd` 永不返回。
必须由后台线程应答，且只有 `PostMessageW(dlg, WM_COMMAND=0x0111, IDNO=7, btn)` 有效（`BM_CLICK` / 键盘消息 / `WM_CLOSE` 全部无效）。实现在 `scripts/dlgwatch.py`。
问「是否重算/重新选筋」一律答 否（前面步骤已经算好了）。

### 3. 导入校验闸门（防"静默导入空模型"）
`yjk_importydb` 返回 `OK` 不代表真导进去了：传相对路径时 YJK 按自己的工作目录解析，找不到就弹框，放行后导入空模型，直到计算才报「模型中没有单元数据」。
`yjk_quant.py` 在 `yjk_save` 之后跑 `impcheck.py` 逐表核对几何表行数（`tblJoint` / `tblBeamSeg` / `tblColSeg` / `tblSlab` / `tblFloor`），不通过就跳过该方案，不浪费几十分钟计算。
（`tblProperty` / `tblProjectPara` 会因 save 展开，不可作判据。）

### 4. YJK 不出模板量：模板只能手算
按定额计算规则用接触面积算（`takeoff.py`）：
- 梁模板 = 梁两侧 + 梁底；梁与梁、梁与墙、梁与柱交接处净空长度以 m 计，不扣减接合处模板面积。
- 板模板 = 板面积 扣除 柱、梁、墙所占面积。
- 支模高度按楼层高度：层高 4.8m ⇒ 3.6m 子目 + 2 ×「每增加 1m 内」（4.8−3.6=1.2，不足 1m 按 1m 向上取整 ⇒ 2 次）。

### 5. 取「第N层」行，不取「全楼/合计」行
YJK 钢筋用量表里每层一行 + 一行全楼合计。拿合计行当单层值会把面积和用量放大层数倍（例如 3 层会放大 3 倍），而且数量级看起来很"正常"，极难发现。
判据：表的第一列以 `第` 开头。

### 6. 混凝土按有梁板合并计
定额规则：有梁板（包括主、次梁与板）按梁、板体积之和计算；楼板砼体积扣除柱体积；梁长算至柱内侧面，次梁算至主梁内侧面，主梁不扣。
所以「无次梁」方案的板厚必须显著加大，才是有意义的对比。

### 7. 批量循环会被 safe-delete 拦腰打断
`yjk_quant.py` 已内置补丁：
```python
Y.own_clear = lambda *a, **k: None     # own.json 会被下一次 own_claim 覆盖，不需删
```
否则跑到第 2 个方案时钩子抛出非 `Exception` 的错误，`try/except Exception` 抓不住，整批中断 → 表现为"只跑了第 1 个方案"。
另：`yjk_quant.py` 必须前台跑，后台任务会在会话轮转时被杀掉。

---

## 参数化：换项目只改两处

**1) `spec.py`** —— 柱网、跨数、层数层高、荷载、各方案板厚与次梁截面：
```python
BASE = dict(
    几何=dict(跨度X=8400, 跨数X=8, 跨度Y=8400, 跨数Y=4, 层数=3, 层高=4800),
    荷载=dict(附加恒载=5.0, 活载=5.0),
    柱=dict(边长=700, 等级="C40"),
    板=dict(等级="C30"), 主梁=dict(宽=300, 高=800, 等级="C30"),
)
LAYOUTS = { "S0_无次梁": dict(次梁_X向每跨道数=0, 次梁_Y向每跨道数=0, 板厚=180, 次梁=None), ... }
```
命名约定：「X 向梁」= 沿 X 走、位于某个 y 上的梁；「次梁_Y向每跨道数」指在 x 上增加的梁线。搞反会让整张布置旋转 90°。

**2) `collect.py` 顶部的 `SCHEMES` / `INFO`** —— 方案标签、名称、截面、板厚（进报告第 1 页）。

报告文件名在 `build_report.py` 里给定，换项目时改掉。

### 换机器：不用改代码

- 找驱动：`YJK_DRIVER_DIR` / `YJK_AUTO_DRIVE_DIR` / `YJK_SKILLS_DIR` → 同父兄弟目录、当前目录 → 通用扫描各 agent 的技能家目录（枚举 `~` 与 `~/.config` 的一级子目录去找 `<D>/skills/yjk-auto-drive`）→ 中立位置 → `~/.workbuddy-ai/skills/yjk-auto-drive`（历史遗留路径，保留以不破坏现有用户）。不含任何具体厂商名、盘符、用户名或桌面路径；六份副本的这条链由 `selfcheck.py` 的 T31 逐条守着，改一处就得六份一起改。`yjk_api.py` 找 `STCAD` 也复用驱动的跨机器探测，不写死安装位置。换 agent / IDE 的注意事项见根目录 `AGENT-COMPAT.md`。
- 解释器：不写死，用驱动记录的那个（`~/.yjk-auto/python.txt`）或先跑 `setup_env.py`。
- 自检：`python <yjk-auto-drive>/scripts/portability_check.py`（退出码 0 = 通过）。

---

## 方案选择经验（8.4×8.4m 柱网数量级参照）

8.4×8.4m 柱网、10 kN/m²、层高 4.8m、3 层：

| 方案 | 板厚 | 次梁 | 造价指数 |
|---|---|---|---|
| S0 无次梁 | 180 | — | 100.0 |
| S1 单向 1 道 | 120 | 250×550 | 91.9 |
| **S2 单向 2 道** | 100 | 250×500 | **90.4** ★最优 |
| S3 十字梁 | 100 | 250×500 | 92.9 |
| S4 井字梁 | 100 | 250×450 | 94.3 |

规律：设次梁 → 板厚骤降，板钢筋大幅减少（可降到原来的三分之一量级），省下的钢材远大于新增次梁的混凝土+模板；但次梁过多会反弹（井字梁梁模板面积最大、梁筋最多，反而最贵）。最优通常落在"单向 2 道"附近——板厚能做到 100mm、板块 8.4×2.8 仍在合理跨度内。

截面合理性（"构件截面要合理"的落点）：板厚按跨度控制（双向板 ≈ 短跨/40~45，单向板 ≈ 短跨/30~35 且 ≥ 80~100mm），次梁高 ≈ 跨度/12~18、宽 ≈ 高/2~2.5，主梁高 ≈ 跨度/8~12。

---

## 交付物

`out/<项目>楼盖方案经济对比报告.xlsx`，10 页：
1. 方案概况 2. 工程量对比 3. 综合单价分析 4. 造价对比 5. 造价明细
6. 计算书-梁 7. 材料用量指标 8. 定额依据 9. 自检与校核 10. 结论与建议

报告内置自检（第 9 页）：分项之和 = 合计、手算交叉校核、YJK 验收证据。交付前务必翻一遍第 9 页；有任一「未核对」即非零退出（见文末「缺数据一律失败」）。

## 参考

- `references/quota-guangdong.md` —— 广东省 2018 定额子目 + 广州信息价 + 取费规则（含更新清单）
- `yjk-auto-drive/references/commands.md` —— 全部 IPC 命令与链条
- `yjk-auto-drive/references/troubleshooting.md` —— 模态框应答、safe-delete 处置

## YJK 官方二次开发资料（离线参考集）

本技能要自己造模型，容易踩的坑官方文档里都有权威答案，已随包转换到 `yjk-dev-refs/`（来源见该目录 README）：

| 文档 | 为什么本技能要看 |
|---|---|
| `04-接口说明/建模接口说明-*.md` | 节点/轴线/网格/柱/梁/板/**墙**的建模 API 与参数含义（`WallSect_Def`+`wall_arrange` 就在这里） |
| `06-总信息参数ID表/参数ID速查.md` + `前处理计算参数宏定义.md` | `tblProjectPara` 的 ID 与枚举码权威表（新工程默认总信息是不能用的，见 `yjk-auto-drive/scripts/projpara.py`） |
| `05-数据文件说明/` | `.ydb` 与各施工图/基础数据库的表结构 |
| `02-Python-API案例/案例3_剪力墙结构/jlq.py` | 官方的**剪力墙**建模写法 |
| `02-Python-API案例/案例14_前处理计算参数设置/kj.py` | 官方的**计算参数**设置写法（`ProjectPara_Set`） |
| `02-Python-API案例/案例1_框架结构/kj.py` | 官方框架建模写法（含梁上荷载 `Load_Def` + `load_arrange`） |

> 序列化落盘时必写荷载表：`tblLoadSect` / `tblLoadSeg` 的序号列叫 `No`，而其它几何表都叫 `No_`。写错列名不会报错，只会被填成默认值 0，于是整批梁上荷载在 `yjk_importydb` 时被静默丢弃 —— 模型照样算得出来，但柱轴力少一整块（实测一个 8 kN/m × 201.6 m 的例子少约 20%）。

## 缺数据一律失败（本轮口径）

这些脚本以前在缺数据时会静默给出一份看起来正常的结论，现在一律显式失败。

1. `collect.py`：拿不到 YJK 实测数据（如缺面积表）时返回非零，并在 JSON 里加 `sources` / `flags` 说明来源；报告第 1 页按来源出文，不再谎称"模型实测值"。
2. `build_report.py`：新增真读盘取证（`check.out`、`.ydb` vs `.ymd` 逐表行数、wpj 个数 vs 层数、钢筋来源）。拿不到证据时第 9 页写「未核对」并非零退出；分项造价改成从工程量×单价独立重算后再比对合计；第 2/5/7/10 页缺钢筋数据时显示「未取得」并在第 4 页注明"合计不含钢筋"；第 10 页的区间/板厚/板钢筋含量/最优方案改成现算。
3. `yjk_quant.py`：留档产物缺项（`KEEP` 列表里任一项）就列清单并非零退出。
4. `parse_wpj.py`：解析覆盖率不满即非零退出（有 `N-C` / `N-B` 行却一条都留不下就直接失败；拿错文件则明确报错）。已用 115 个真实 wpj 校准，正常文件零误报。
5. `make_ydb.py`：写盘改成 `<out>.ydb.part` + 全部写完才 `os.replace`，失败时最终路径上不出现半成品；另加硬守卫「配置 q>0 但 `tblLoadSeg == 0`」直接失败。
6. `spec.py`：给了 `--config` 就必须读到，否则退出，不再静默回退默认值；读文件用 `utf-8-sig`。
7. `build_floor.py`：`ok` 为假、产物不存在或 0 字节、内存模型为空都算失败；`--help` 不再预加载官方 DLL。
8. `yjk_cleanup.py`（全包只有一份，在 `yjk-auto-drive\scripts\`）：判据统一到 `yjk_auto.instances()`，只有 orphan 是清理对象；枚举不可用 rc=2；`--apply` 没清干净 rc=1。

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
