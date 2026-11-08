# 基础（JCCAD）模块二次开发 API 与承台更新

记录 YJK 8.x 基础模块 `JcDataFunc` 通路、承台更新、组合保留、标高核对与结果解析。
配合 `yjk-auto-drive`（IPC 驱动）与 `pile-layout-opt`（布桩优化）使用。
文中 `<YJK安装目录>`、`<SDK目录>`、`<工程目录>`、`<工作目录>` 按本机实际路径替换；
`<工作目录>` 建议用纯 ASCII 路径。

## 1. SDK 选择与安装

PyPI 的 `YJKAPI` 包可能对应旧版 DLL；用它写出的 ydb 在 8.1 里可能“能导入、但
GenData/BaseAnalysis 空跑”。应使用 Gitee `yjk-opensource/yjkapi_-python`
**与 YJK 版本对应的分支**里的 `SDK` 包。

典型结构（解压后）：

```
<SDK目录>\python310\python.exe
<SDK目录>\python310\site-packages\YJKAPI
```

运行前：

```powershell
$env:PATH = "<YJK安装目录>;<SDK目录>;" + $env:PATH
& "<SDK目录>\python310\python.exe" -c "from YJKAPI import JcDataFunc; JcDataFunc(); print('OK')"
```

- `<YJK安装目录>` 必须在 `PATH` 里（原生 DLL 依赖）；否则 `JcDataFunc()` 可能报
  “未能加载由 ClrYJKAPI.dll 导入的过程”。
- 工作目录用纯 ASCII 路径；中文路径下 `ReadJcYdb` 可能读到 0 节点/0 承台。
- YJK 安装根目录的 `ClrYJKAPI.dll`/`YAPIData.dll` 是 C++/CLI 混合模式，
  **不能**在 pythonnet/.NET 控制台里独立 `LoadFrom`；走 SDK 的 `YJKAPI` 包装。

## 2. JcDataFunc 最小可用流程

```python
import os
os.environ['PATH'] = r'<YJK安装目录>;<SDK目录>;' + os.environ['PATH']
from YJKAPI import JcDataFunc

jc = JcDataFunc()
jc.ReadJcYdb(WORK, '\\Jccad_0.ydb')          # WORK 为 ASCII 目录

D = jc.JcDais_Def(10, 2, 1, req, 0, 0)       # 10=梯形现浇, ns=2 矩形, nstep=1, npile=req
for (x, y) in [(-W/2,-H/2),(W/2,-H/2),(W/2,H/2),(-W/2,H/2)]:
    jc.JcDais_Cir(D.DaisFlag, 0, x, y)       # 局部坐标轮廓
jc.JcDais_StepH(D.DaisFlag, 0, H)            # 阶高 mm
jc.JcDais_App(nj, D.lID, ex, ey, ang, pilelen, dBotElevat, 1)
for (x, y) in pile_pts:
    jc.JcPile_App(1, x, y, 0, D.DaisFlag, 0.0, pilelen, dBotElevat, 1)

jc.CreateYDB(WORK, 'Jccad_0.ydb')
```

读模型列表的坑：

- `GetJcModelDBdata().ToPyList()` 可能报 `PythonEngine is not initialized`；
  可直接用反射取字段：
  ```python
  m = jc.GetJcModelDBdata()
  nodes    = m.GetType().GetField('m_jcNodeList').GetValue(m)
  app_dais = m.GetType().GetField('m_jcAppDaisList').GetValue(m)
  stepH    = m.GetType().GetField('m_jcDaisStepHList').GetValue(m)
  ```
- .NET `List` 不支持负索引：`nodes[-1]` 报错，用 `nodes[len(nodes)-1]`。

## 3. 承台更新：`JcDais_App` 会“加”不会“删”

`JcDais_App` 在节点上**新增**一座承台；`app_dais.Remove(old)` 在 pythonnet 下不可靠。
结果可能是同一柱位出现两座承台，YJK 里表现为“同一柱位不同承台”，并出现大量
1.8D 桩距报警。

可靠做法：

1. 从干净备份重建，不要在已重复的模型上继续加；
2. 只改**原承台**的 `kind`/`dBotElevat`/`idaispilelen`，不要新增承台；
3. 重建后必查：
   ```sql
   select count(*) from app_dais;
   select nj from app_dais group by nj having count(*)>1;   -- 应为空
   ```
4. GUI 里仍显示重复承台：用 `prep_model.py` 移出 `CK_F.*`/`Jccad_0_ydb.dat`，再 GenData。

## 4. `jccad_read_by_ydb` 会丢组合 → 导入后回填

API 写出的 ydb 带有完整组合；`jccad_read_by_ydb` 只导入模型，导入后
`LoadZhuHe` 会减少（常见只剩 8 个）、恒载可能被清零，目标组合可能不存在。

已验证的补救顺序：

1. 先只做 `SetCurrentLabel` + `jccad_read_by_ydb`（`jc.py --gen-only` 的导入段），
   把模型导入 GUI；
2. 用 SQL 从 API ydb 回填三张表（列名一致时 `select *`）：
   ```sql
   ATTACH '<API工作目录>\Jccad_0.ydb' AS api;
   DELETE FROM Loads;    INSERT INTO Loads    SELECT * FROM api.Loads;
   DELETE FROM LoadZhuHe;INSERT INTO LoadZhuHe SELECT * FROM api.LoadZhuHe;
   DELETE FROM CalPara;  INSERT INTO CalPara  SELECT * FROM api.CalPara;
   DETACH DATABASE api;
   ```
3. 再跑 `jc.py`（**不要再 import**）：GenData 用导入后的 GUI 模型，组合用回填后的；
4. 判据：`tblPileNL` 行数 ≈ 桩数 × 组合数；`jccad.result`/`CAL_MID.DIS` mtime 刷新；
   日志“计算正常”。

## 5. 标高体系（示例，按工程实际替换）

| 对象 | 标高/长度 | 说明 |
|---|---|---|
| 筏板 | 顶 = 底 + 厚 | `RaftSlab.BotElevat` 为底、`thick` 为厚 |
| 节点 | 柱底/建筑面 | 与筏板顶可能差一个建筑面层 |
| 承台顶 | 与筏板顶齐平（或按设计） | 由 `dBotElevat + Σdais_stepH` 反算 |
| 承台底 | 顶 - Σdais_stepH | 每个类型单独算 |
| 承台桩长 | 统一桩端 - 承台底 | 先定统一桩端，再反算每类桩长 |
| 板下桩 | 桩顶 = 筏板底，桩长 = 统一桩端 - 桩顶 | `app_Pile.z` 用绝对标高（mm） |

核对步骤：

1. 统计所有承台的 `dBotElevat + Σdais_stepH`，应等于承台顶设计标高；
2. 统计承台桩端、板下桩端，应统一（或按持力层分区统一）；
3. 对不上的承台（底标高明显高于/低于筏板）单独列出并修正；
4. 修完再 `prep_model.py` + `jc.py` 重算。

## 6. 结果解析

结果表：`基础计算及结果输出\jccad.ydb`

- `tblPileApp`：逐桩（`ID,nRaft_CT,xx,yy,kind`）；
- `tblPileNL`：按 `CombType/CombID` 取组合，`N` blob 前 9 个 float 的第 1 个即轴力；
- `tblDaisApp` / `tblDaisDef`：承台。

```python
n = {pid: struct.unpack('<9f', b)[0] for pid, b in
     c.execute('select PileID,N from tblPileNL where CombType=1 and CombID=51')}
over = [r for r in piles if r['kind']==1 and n[r['ID']] < -400]
```

若后处理失败（`jccad.result` 缺失、`jccad.ydb` 明显偏小、`tblPileNL` 行数不足），
按“减少组合 / 放粗网格 / 分块或 GUI 直接跑”排查；这是计算链路问题，不是规范限制。

## 7. 一次干净的“重建 + 改标高 + 重算”顺序

```
1) 关 YJK（或确认无 yjks.exe）
2) copy <干净备份>  →  Jccad_0.ydb
3) apply_layout.py <工程目录> <layout.csv>          # 板下桩
4) SQL：DEF_Pile F2、app_Pile fKn/fKm
5) SQL：承台 dBotElevat/桩长；板下 z/桩长（按统一桩端）
6) prep_model.py --dir <工程目录>                   # 移出 CK_F/基础备份/Jccad_0_ydb.dat
7) jc.py --dir <工程目录> --root <YJK安装目录>
8) 验收：承台数/重复数；tblPileApp 总数；目标组合超限数；日志“计算正常”
```
