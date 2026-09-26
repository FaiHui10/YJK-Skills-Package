# 柱截面优选（column-section-opt）

框架柱**截面 + 混凝土强度等级**的成本优选，并产出可交付的 Excel 报告。
完整流程、判据、边界与坑 → 见 **[SKILL.md](SKILL.md)**。

> **分工**：本技能做「读现状 → 选型 → 写回模型 → 复核 → 出报告」。
> 「把 YJK 驱动起来算」由 **[yjk-auto-drive](../yjk-auto-drive/SKILL.md)** 技能负责，
> 本技能通过 `scripts/driver.py` 自动找到并调用它。

## 两种模式

| 模式 | 适用 | 模型来源 | 写入模型 | 状态 |
|---|---|---|---|---|
| **A 简单框架（全自动）** | 规则柱网、自建模型 | `frame_build.py` 生成 `.ydb` | 生成即完整，直接导入 | 全自动 |
| **B 真实工程（半自动）** | 已有 YJK 工程 | 现有 `.ydb/.ymd` + `wpj*.out` | `write_sections.py` 改库 | 半自动（写回 + 复核） |

## 文件

```
SKILL.md                      流程总纲（先读它）
references/method.md          方法：闭式求解 + 小枚举 + 不动点验证
references/real-project.md    真实工程：写入路径、两个决定性发现、迭代记录
references/report-spec.md     Excel 报告的页签结构与内容要求
config.example.json           配置示例（3跨×3跨×10层）
sections.base.json            保守基线截面（第一轮拿真实轴力用）

scripts/
  driver.py         找到 yjk-auto-drive 技能 / 准备官方 API / 调它驱动 / 环境自检
  write_sections.py 把「等级 + 优化截面」写回 ydb，自带三项自检
  make_spec.py      生成"某组不折减"的截面清单（--keep G3）
  verify_results.py 一把梭复核 设计结果\（轴压比/位移角/刚度比/配筋率）
  colopt.py         主入口：build / drive / opt / cost / iterate / report
  frame_build.py    模式A：按 config + sections 生成模型 ydb（简单框架 / 框架-核心筒）
  ydb_serialize.py  按表结构把内存模型序列化进骨架 ydb（--scaffold 这条可选写盘路径）
  section_opt.py    按轴压比限值选截面（短柱/非短柱分别取值）
  cost.py           造价统计（混凝土+模板+钢筋，可改单价）
  report.py         多轮对比 Excel 汇报
  common.py         公共工具
  ydb_lint.py       模型库自检：实体 ID >100000、引用悬空、楼层与截面结构摘要
  split_stdflr.py   按自然层拆标准层（DB 层自洽，但 YJK 导入不接受结构改动）
```

## 上手

### 模式 B（真实工程，推荐闭环）

```powershell
$py = "<带 pythonnet 的 python.exe>"        # 没装过就先跑 driver.py probe
$S  = "<本技能>\scripts"

& $py -X utf8 -B "$S\driver.py" where       # 1) 确认能找到驱动技能
& $py -X utf8 -B "$S\driver.py" probe       # 2) 驱动环境自检（缺什么会告诉你）

# 3) 写回模型（等级 + 截面），看自检是否全过
& $py -X utf8 -B "$S\write_sections.py" 源.ydb 目标.ydb --grade `
      --grades "1-3:60,4-5:50,6:45,7:40" --sections 优化截面清单.json

# 4) 驱动实算（导入 + 预处理 + 计算）
& $py -X utf8 -B "$S\colopt.py" drive --ydb 目标.ydb --proj "<工程目录>" --name R1

# 5) 复核
& $py -X utf8 -B "$S\verify_results.py" "<工程目录>\设计结果" --json verify_R1.json
```

自检输出应为：

```
柱段改写 112 个（7 个标准层）
自检 idNew 重复组数 = 0
截面自检：符合 112 / 不符 0
```

### 模式 A（简单框架）

```powershell
& $py -X utf8 -B "$S\colopt.py" iterate --config config.json --sections sections.base.json --tag 00 --work .
& $py -X utf8 -B "$S\colopt.py" opt     --config config.json --res .\工程_00 --out s1.json --compare sections.base.json
& $py -X utf8 -B "$S\colopt.py" iterate --config config.json --sections s1.json --tag 01 --work .
& $py -X utf8 -B "$S\colopt.py" report  --config config.json --out 汇报.xlsx iter_*.json
```

## 先读这三条，能省几小时

1. **截面写回要同时写 `tblColSeg.SectID` 与 `idNewDef`**（YJK 认的是后者）。
   只写 `SectID` → 导入后柱段**全部静默回退**。
2. **等级要写 `tblStdFlr.Para` 下标 2/4/5/6**（板/柱/梁/墙 强度×10）。
   只改 `tblProperty.HNTDJ` → YJK 仍按 C30 算（Uc 差 1.92 倍）。
3. **判定成功只认实算结果**：`wdisp.out` 的 `1/9999` 是"≈0"哨兵（**上限**：比值优于 1/9999），
   取最小值时要剔除；**全都是哨兵 = 满足**（不是"没核"），但 `verify_results.py` 会用同文件的
   `h`/`Max-D` 列**现算交叉印证**，结果写在 JSON 的 `位移角哨兵交叉印证` 里（见 `SKILL.md`）；
   `Ratx1/Raty1` 判据是 **≥1.0 满足**。
