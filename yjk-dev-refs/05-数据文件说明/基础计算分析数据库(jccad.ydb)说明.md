> 来源：YJK 官方二次开发文档包 `数据库文件说明.rar` 内 `基础计算分析数据库(jccad.ydb)说明.docx`，由 pandoc 从 .docx 转换为 Markdown（纯文本，图片以标记代替）。

# 基础计算分析数据库(jccad.ydb)说明

## 0、概述

基础模型对应的数据库文件为jccad.ydb，存储位置在“工程路径\基础计算及结果输出\jccad.ydb”。jccad.ydb存储的配筋面积为按“承载力要求”和“构造要求”取大的配筋面积，不是施工图中的实际配筋面积。

## 1、计算参数表

### 1.1计算参数（tblCalPara）

| 字段名 | 字段类型 | 允许为空 | 主键 | 字段含义 |
|:--:|:--:|:--:|:--:|:--:|
| ID | 整型 | 否 | 是 | 参数ID |
| ParaValue | ksvtUnknown | 否 | 否 | 参数值（根据ParaName不同代表不同意义，详见附表5.1） |
| ParaName | 文本 | 否 | 否 | 参数名 |

### 1.2节点（tblGeoNode）

| 字段名 | 字段类型 | 允许为空 | 主键 | 字段含义  |
|:------:|:--------:|:--------:|:----:|:---------:|
|   ID   |   整型   |    否    |  是  | 节点编号  |
|   X    |  浮点型  |    否    |  否  | 节点x坐标 |
|   Y    |  浮点型  |    否    |  否  | 节点y坐标 |
|   Z    |  浮点型  |    否    |  否  | 节点z坐标 |

### 1.3网格（tblGeoline）

| 字段名 | 字段类型 | 允许为空 | 主键 |          字段含义           |
|:------:|:--------:|:--------:|:----:|:---------------------------:|
|   ID   |   整型   |    否    |  是  |          网格编号           |
|  nbg   |   整型   |    否    |  否  |         起点网格点          |
|  ned   |   整型   |    否    |  否  |         终点网格点          |
| ngrid  |   整型   |    否    |  否  | 圆弧网格的圆心点,直网格为-1 |
| nAxis  |   整型   |    否    |  否  |     网格线所在的轴线号      |

### 1.4轴线（tblGeoAxis）

| 字段名 | 字段类型 | 允许为空 | 主键 | 字段含义 |
|:--:|:--:|:--:|:--:|:--:|
| ID | 整型 | 否 | 是 | 轴线序号 |
| nbg | 整型 | 否 | 否 | 起点号+1 (从1开始)(若为负数说明是圆弧轴线，圆心结点编号为abs(nbg)-1) |
| ned | 整型 | 否 | 否 | 终点号+1 (从1开始) |
| sName | 文本 | 否 | 否 | 轴线名 |

### 1.5房间（tblGeoRoom）

| 字段名 | 字段类型 | 允许为空 | 主键 | 字段含义 |
|:--:|:--:|:--:|:--:|:--:|
| ID | 整型 | 否 | 是 | 房间编号(从0开始) |
| ang | 浮点型 | 否 | 否 | 主方向(弧度) |
| nodes | 整型数组 | 否 | 否 | 网格点编号，读取顺序为(N1,N2,…,Nn)，N为网格点编号 |
| grids | 整型数组 | 否 | 否 | 网格线编号，读取顺序为(G1,G2,…,Gn)，G为网格线编号 |

## 2、构件信息数据表

### 2.1柱类型定义（tblColumnDef）

<table>
<colgroup>
<col style="width: 19%" />
<col style="width: 16%" />
<col style="width: 13%" />
<col style="width: 8%" />
<col style="width: 42%" />
</colgroup>
<thead>
<tr>
<th style="text-align: center;">字段名</th>
<th style="text-align: center;">字段类型</th>
<th style="text-align: center;">允许为空</th>
<th style="text-align: center;">主键</th>
<th style="text-align: center;">字段含义</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: center;">int m_iID</td>
<td style="text-align: center;">整型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">柱编号</td>
</tr>
<tr>
<td style="text-align: center;">rectB</td>
<td style="text-align: center;">浮点型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">外包矩形宽度(mm)</td>
</tr>
<tr>
<td style="text-align: center;">rectH</td>
<td style="text-align: center;">浮点型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">外包矩形高度(mm)</td>
</tr>
<tr>
<td style="text-align: center;">k</td>
<td style="text-align: center;">整型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">以下参数在m_sPoly（数据描述）为空时有效</td>
</tr>
<tr>
<td style="text-align: center;">b</td>
<td style="text-align: center;">整型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">否</td>
<td rowspan="11" style="text-align: center;">见附录5.2、5.3</td>
</tr>
<tr>
<td style="text-align: center;">h</td>
<td style="text-align: center;">整型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">否</td>
</tr>
<tr>
<td style="text-align: center;">u</td>
<td style="text-align: center;">整型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">否</td>
</tr>
<tr>
<td style="text-align: center;">t</td>
<td style="text-align: center;">整型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">否</td>
</tr>
<tr>
<td style="text-align: center;">d</td>
<td style="text-align: center;">整型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">否</td>
</tr>
<tr>
<td style="text-align: center;">f</td>
<td style="text-align: center;">整型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">否</td>
</tr>
<tr>
<td style="text-align: center;">I</td>
<td style="text-align: center;">整型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">否</td>
</tr>
<tr>
<td style="text-align: center;">m</td>
<td style="text-align: center;">整型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">否</td>
</tr>
<tr>
<td style="text-align: center;">p</td>
<td style="text-align: center;">整型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">否</td>
</tr>
<tr>
<td style="text-align: center;">igzz</td>
<td style="text-align: center;">整型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">否</td>
</tr>
<tr>
<td style="text-align: center;">b1</td>
<td style="text-align: center;">整型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">否</td>
</tr>
<tr>
<td style="text-align: center;">sName</td>
<td style="text-align: center;">文本</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">截面名称</td>
</tr>
<tr>
<td style="text-align: center;">poly</td>
<td style="text-align: center;">文本</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">数据描述</td>
</tr>
</tbody>
</table>

### 2.2柱布置信息定义（tblColumnApp）

| 字段名 | 字段类型 | 允许为空 | 主键 |                字段含义                |
|:------:|:--------:|:--------:|:----:|:--------------------------------------:|
|   ID   |   整型   |    否    |  是  |                 柱编号                 |
|   nj   |   整型   |    否    |  否  |                 网格点                 |
|  kind  |   整型   |    否    |  否  |                 柱定义                 |
|   ex   |  浮点型  |    否    |  否  | 沿轴偏心(mm)(旋转前后相对网格点的偏心) |
|   ey   |  浮点型  |    否    |  否  |              偏轴偏心(mm)              |
|  ang   |  浮点型  |    否    |  否  |              方位角(弧度)              |
|  pier  |   整型   |    否    |  否  |       柱墩定义(柱下无柱墩时为-1)       |
|  hgh   |  浮点型  |    否    |  否  |              探伸距离(mm)              |

### 2.3柱墩类型定义（tblColumnPierDef）

| 字段名 | 字段类型 | 允许为空 | 主键 |                字段含义                 |
|:------:|:--------:|:--------:|:----:|:---------------------------------------:|
|   ID   |   整型   |    否    |  是  |                柱墩序号                 |
|   iX   |   整型   |    否    |  否  |                长度(mm)                 |
|   iY   |   整型   |    否    |  否  |                宽度(mm)                 |
|   iH   |   整型   |    否    |  否  |                高度(mm)                 |
|  iH1   |   整型   |    否    |  否  | 上柱墩为端部高度(mm) 下柱墩为放角的角度 |
| iKind  |   整型   |    否    |  否  |       柱墩类型 0-上柱墩 1-下柱墩        |

### 2.4剪力墙类型定义（tblShearWallDef）

| 字段名 | 字段类型 | 允许为空 | 主键 | 字段含义 |
|:--:|:--:|:--:|:--:|:--:|
| ID | 整型 | 否 | 是 | 剪力墙编号 |
| lW | 整型 | 否 | 否 | 厚度(mm) |
| k | 整型 | 否 | 否 | 类型 1-普通墙 11-钢板混凝土剪力墙 12-双层钢板混凝土墙 31-端柱带肋钢板墙 |
| m | 整型 | 否 | 否 | 材料 1-3:砌体 其他:混凝土 |

### 2.5剪力墙布置信息定义（tblShearWallApp）

|  字段名  | 字段类型 | 允许为空 | 主键 |              字段含义              |
|:--------:|:--------:|:--------:|:----:|:----------------------------------:|
|    ID    |   整型   |    否    |  是  |             剪力墙编号             |
|   nbg    |   整型   |    否    |  否  |            起点网格编号            |
|   ned    |   整型   |    否    |  否  |            终点网格编号            |
|  ngrid   |   整型   |    否    |  否  |             网格线编号             |
|   kind   |   整型   |    否    |  否  |             剪力墙定义             |
|    ec    |   整型   |    否    |  否  |         偏心（偏轴距离mm）         |
|   high   |  浮点型  |    否    |  否  |           剪力墙高（mm）           |
| hole_dis |   整型   |    否    |  否  |     墙洞起点与起始网格点的距离     |
| hole_len |   整型   |    否    |  否  | 墙洞宽度（\<1.0e-6时判别为有洞口） |
|   hgh    |  浮点型  |    否    |  否  |           探伸距离（mm）           |

### 2.6砌体/填充墙类型定义（tblFillWallDef）

| 字段名 | 字段类型 | 允许为空 | 主键 |  字段含义  |
|:------:|:--------:|:--------:|:----:|:----------:|
|   ID   |   整型   |    否    |  是  | 填充墙编号 |
|   lW   |   整型   |    否    |  否  | 厚度（mm） |

### 2.7砌体/填充墙布置信息定义（tblFillWallApp）

| 字段名 | 字段类型 | 允许为空 | 主键 |      字段含义      |
|:------:|:--------:|:--------:|:----:|:------------------:|
|   ID   |   整型   |    否    |  是  |     填充墙编号     |
|  nbg   |   整型   |    否    |  否  |    起点网格编号    |
|  ned   |   整型   |    否    |  否  |    终点网格编号    |
| ngrid  |   整型   |    否    |  否  |     网格线编号     |
|  kind  |   整型   |    否    |  否  |     填充墙定义     |
|   ec   |   整型   |    否    |  否  | 偏心（沿轴距离mm） |
|  high  |  浮点型  |    否    |  否  |     墙高（mm）     |
|  hgh   |  浮点型  |    否    |  否  |    探伸距离(mm)    |

### 2.8筏板类型定义（tblRaft）

| 字段名 | 字段类型 | 允许为空 | 主键 | 字段含义 |
|:--:|:--:|:--:|:--:|:--:|
| ID | 整型 | 否 | 是 | 筏板编号 |
| RaftID | 整型 | 否 | 否 | 筏板ID号(大于0且可以不连续) |
| nMainRaftId | 整型 | 否 | 否 | 主、次筏板 -2:防水板 -1:主筏板 1:是1号主筏板的子筏板或洞口(1为ID号，不是序号) |
| thick | 浮点型 | 否 | 否 | 筏板厚度(mm) |
| BotElevat | 浮点型 | 否 | 否 | 底部标高(m) |
| pts | 浮点型数组 | 否 | 否 | 边界点坐标(mm)，存储序列为(x1,y1,x2,y2,…,xn,yn)，x、y为边界点坐标 |
| nCeng | 整型 | 否 | 否 | 0-无意义 1-加厚区 2-电梯井外圈 3-电梯井里圈 |
| b_h | 浮点型 | 否 | 否 | 外挑放角 b/h |
| lOutB | 整型 | 否 | 否 | 外挑宽度(mm) |
| lBotH | 整型 | 否 | 否 | 底部厚度(mm) |
| dMainAngle | 浮点型 | 否 | 否 | 配筋主方向（弧度） |

### 2.9后浇带类型定义（tblHjd）

| 字段名 | 字段类型 | 允许为空 | 主键 | 字段含义 |
|:--:|:--:|:--:|:--:|:--:|
| ID | 整型 | 否 | 是 | 后浇带序号 |
| iRaft | 整型 | 否 | 否 | 筏板序号 |
| ww | 浮点型 | 否 | 否 | 后浇带宽度(mm) |
| pts | 浮点型数组 | 否 | 否 | 后浇带折线段(mm)，存储序列为(x1,y1,x2,y2,…,xn,yn)，x、y为折线段端点坐标 |

### 2.10承台类型定义（tblDaisDef）

| 字段名 | 字段类型 | 允许为空 | 主键 | 字段含义 |
|:--:|:--:|:--:|:--:|:--:|
| ID | 整型 | 否 | 是 | 承台编号 |
| ns | 整型 | 否 | 否 | 类型0-circle2-rectanglen-polygon(正多边形)-n:polygon(多边形) |
| means | 整型 | 否 | 否 | 做法0-阶形预制1-锥形预制10-阶形现浇11-锥形现浇 |
| nstep | 整型 | 否 | 否 | 阶数(1阶或2阶) |
| npile | 整型 | 否 | 否 | 桩数 |
| ecx | 整型 | 否 | 否 | 上下阶之间的沿轴偏心(mm) |
| ecy | 整型 | 否 | 否 | 上下阶之间的偏轴偏心(mm) |
| pts_step1 | 浮点型数组 | 否 | 否 | 多边形承台下阶定位点坐标(mm)\[下标0到(pt1-1)为1阶定位坐标\]\[下标pt1到(pt1+pt2-1)为2阶定位坐标\]\[坐标以(0,0)为原点\] |
| pts_step2 | 浮点型数组 | 否 | 否 | 多边形承台上阶定位点坐标(mm)\[pt1,pt2:下、上阶定位点数目，若为1阶，pt2=0\] |
| d_step1 | 浮点型 | 否 | 否 | 圆形承台下阶直径(mm) |
| d_step2 | 浮点型 | 否 | 否 | 圆形承台上阶直径(mm) |
| h_step1 | 整型 | 否 | 否 | 下阶高度(mm) |
| h_step2 | 整型 | 否 | 否 | 上阶高度(mm) |

### 2.11承台布置信息定义（tblDaisApp）

| 字段名 | 字段类型 | 允许为空 | 主键 | 字段含义 |
|:--:|:--:|:--:|:--:|:--:|
| ID | 整型 | 否 | 是 | 承台编号 |
| kind | 整型 | 否 | 否 | 承台定义号(与原始x向偏心（mm）,原始y向偏心（mm）,原始转角（弧度）匹配) |
| nj | 整型 | 否 | 否 | 网格点号 |
| ex | 浮点型 | 否 | 否 | 沿轴偏心(mm) |
| ey | 浮点型 | 否 | 否 | 偏轴偏心(mm) |
| ang | 浮点型 | 否 | 否 | 转角(弧度) |
| daispilelen | 浮点型 | 否 | 否 | 承台桩桩长(m) |
| elev | 浮点型 | 否 | 否 | 承台底标高(m) |
| poly | 整型 | 否 | 否 | 仅由复杂独基围成多边形时，记录多边形编号，否则记为-1 |
| fea | 整型 | 否 | 否 | 是否按有限元计算 |

### 2.12地基梁类型定义（tblDiliangDef）

| 字段名 | 字段类型 | 允许为空 | 主键 |    字段含义    |
|:------:|:--------:|:--------:|:----:|:--------------:|
|   DI   |   整型   |    否    |  是  |    承台编号    |
|   b    |   整型   |    否    |  否  |     宽(mm)     |
|   h    |   整型   |    否    |  否  |     高(mm)     |
|   bb   |   整型   |    否    |  否  |   翼缘宽(mm)   |
|   h1   |   整型   |    否    |  否  | 翼缘根部高(mm) |
|   h2   |   整型   |    否    |  否  | 翼缘端部高(mm) |
|   ec   |   整型   |    否    |  否  | 翼缘偏心（mm） |

### 2.13地基梁布置信息定义（tblDiliangApp）

|   字段名   | 字段类型 | 允许为空 | 主键 |         字段含义          |
|:----------:|:--------:|:--------:|:----:|:-------------------------:|
|     ID     |   整型   |    否    |  是  |        地基梁编号         |
|    nbg     |   整型   |    否    |  否  |        起点网格点         |
|    ned     |   整型   |    否    |  否  |        终点网格点         |
|    kind    |   整型   |    否    |  否  |        地基梁定义         |
|     ec     |   整型   |    否    |  否  |       偏轴偏心(mm)        |
|   ngrid    |   整型   |    否    |  否  |          网格线           |
| dBotElevat |  浮点型  |    否    |  否  |        底部标高(m)        |
|   fl_njl   |  浮点型  |    否    |  否  |        左延伸(mm)         |
|   fl_njr   |  浮点型  |    否    |  否  |        右延伸(mm)         |
|   ngrid2   |   整型   |    否    |  否  | 双墙地基梁第2条网格线编号 |

### 2.14归并处理后的地基梁（tblDiliangMacro）

|  字段名  | 字段类型 | 允许为空 | 主键 |             字段含义              |
|:--------:|:--------:|:--------:|:----:|:---------------------------------:|
|    ID    |   整型   |    否    |  是  |               编号                |
|   nbg    |   整型   |    否    |  否  |            起始点编号             |
|   ned    |   整型   |    否    |  否  |            终止点编号             |
|    dL    |  浮点型  |    否    |  否  |    第1个地基梁的取值范围(0到1)    |
|    dR    |  浮点型  |    否    |  否  | 第n个地基梁的取值范围(n可以等于1) |
| iDLArray | 整型数组 |    否    |  否  | 地基梁编号(从0号地基梁开始存储）  |
|    XT    |   整型   |    否    |  否  |    是否是悬挑梁（0-否，1-是）     |

### 2.15拉梁类型定义（tblLaliangDef）

| 字段名 | 字段类型 | 允许为空 | 主键 | 字段含义 |
|:------:|:--------:|:--------:|:----:|:--------:|
|   ID   |   整型   |    否    |  是  | 拉梁编号 |
|   b    |   整型   |    否    |  否  | 宽度(mm) |
|   h    |   整型   |    否    |  否  | 高度(mm) |

### 2.16拉梁布置信息定义（tblLaliangApp）

|   字段名   | 字段类型 | 允许为空 | 主键 |   字段含义   |
|:----------:|:--------:|:--------:|:----:|:------------:|
|     ID     |   整型   |    否    |  是  |   拉梁编号   |
|    nbg     |   整型   |    否    |  否  |  起点网格点  |
|    ned     |   整型   |    否    |  否  |  终点网格点  |
|    kind    |   整型   |    否    |  否  |   拉梁定义   |
|     ec     |   整型   |    否    |  否  | 偏轴偏心(mm) |
| dBotElevat |  浮点型  |    否    |  否  | 底部标高(m)  |
|   ngrid    |   整型   |    否    |  否  |    网格线    |

### 2.17拉梁（tblLaliangNL）

| 字段名 | 字段类型 | 允许为空 | 主键 | 字段含义 |
|:--:|:--:|:--:|:--:|:--:|
| ID | 整型 | 否 | 是 | 编号 |
| LaliangID | 整型 | 否 | 否 | 拉梁编号 |
| CombID | 整型 | 否 | 否 | 拉梁内力组合号 |
| CombType | 整型 | 否 | 否 | 拉梁内力组合类型 1-基本组合 2-标准组合 3-准永久组合 |
| M | 浮点型数组 | 否 | 否 | 弯矩 |
| N | 浮点型数组 | 否 | 否 | 轴力 |
| V | 浮点型数组 | 否 | 否 | 剪力 |

### 2.18条基类型定义（tblTiaojiDef）

| 字段名 | 字段类型 | 允许为空 | 主键 | 字段含义 |
|:--:|:--:|:--:|:--:|:--:|
| ID | 整型 | 否 | 是 | 条基编号 |
| kind | 整型 | 否 | 否 | 做法 0-灰土基础 1-素混凝土基础 2-钢筋混凝土基础 3-带卧梁钢筋混凝土基础 4-毛石、片石基础 5-砖基础 6-钢混毛石基础 7-任意截面 |
| b | 整型 | 否 | 否 | 宽度(mm) |
| h | 整型 | 否 | 否 | 高度(mm) |
| area | 整型 | 否 | 否 | 断面面积(mm\*mm) |
| length | 整型 | 否 | 否 | 任意截面宽度(暂无用) |
| b1 | 整型 | 否 | 否 | 砖、毛石放脚宽(mm)(毛石台阶宽 kind =4 或kind = 7) |
| h1 | 整型 | 否 | 否 | 砖、毛石放脚宽(mm)(毛石台阶高 kind =4 或 kind = 7) |
| WLb | 整型 | 否 | 否 | 卧梁宽(mm) |
| WLh | 整型 | 否 | 否 | 卧梁高(mm) |
| ec | 整型 | 否 | 否 | 基础相对墙体移心(模板计算高度 kind ==7) |
| zj | 整型 | 否 | 否 | 底板受力筋 1位级别后2位是直径后3位是间距 |
| BTop4 | 整型 | 否 | 否 | 毛石阶顶部宽(kind==4) |
| tana01 | 整型 | 否 | 否 | 条基刚度 |
| gj | 整型 | 否 | 否 | 底板分布钢筋 1-HPB235 2-HPB300 3-HRB335 4-HRB400 5-HRB500 6-RRB400 |
| zj_l | 整型 | 否 | 否 | 卧梁主筋 1-HPB235 2-HPB300 3-HRB335 4-HRB400 5-HRB500 6-RRB400 |
| gj_l | 整型 | 否 | 否 | 卧梁箍筋 1-HPB235 2-HPB300 3-HRB335 4-HRB400 5-HRB500 6-RRB400 |
| Hall | 整型 | 否 | 否 | 基础总高（mm） |
| BTop6 | 整型 | 否 | 否 | 毛石阶顶部宽(mm) |
| HEndL | 整型 | 否 | 否 | 混凝土条基端部高 左端高(mm)(kind=2时有效) |
| HEndR | 整型 | 否 | 否 | 混凝土条基端部高 右端高(mm)(kind=2时有效) |
| bw1 | 整型 | 否 | 否 | 墙宽1(mm) |
| bw2 | 整型 | 否 | 否 | 墙宽2(mm)(双墙条基有效，否则为0) |
| wSpace | 整型 | 否 | 否 | 双墙条基的墙间距(mm) |
| lNewFlag | 整型 | 否 | 否 | 无用字段 |
| lIsUsed | 整型 | 否 | 否 | 无用字段 |
| lArea_b | 整型 | 否 | 否 | 基础底面挑出宽度(mm)0灰土1素砼起做用 |

### 2.19条基布置信息定义（tblTiaojiApp）

| 字段名 | 字段类型 | 允许为空 | 主键 | 字段含义 |
|:--:|:--:|:--:|:--:|:--:|
| ID | 整型 | 否 | 是 | 编号 |
| nbg | 整型 | 否 | 否 | 起始网格点号 |
| ned | 整型 | 否 | 否 | 终止网格点号 |
| kind | 整型 | 否 | 否 | 条基定义编号 |
| ec | 浮点型 | 否 | 否 | 偏轴偏心(mm) |
| ngrid | 整型 | 否 | 否 | 网格线号 |
| dBotElevat | 浮点型 | 否 | 否 | 底部标高(m) |
| gridlist | 整型数组 | 否 | 否 | 双墙条基对应的网格编号（多柱独基的节点）读取顺序为(G1,G2,…,Gn)，G为网格线编号 |

### 2.20独基类型定义（tblDujiDef）

| 字段名 | 字段类型 | 允许为空 | 主键 | 字段含义 |
|:--:|:--:|:--:|:--:|:--:|
| ID | 整型 | 否 | 是 | 独基编号 |
| kind | 整型 | 否 | 否 | 做法：0-锥形现浇1-锥形杯口2-阶形现浇3-阶形杯口4-锥形短柱5-锥形高杯6-阶形短柱7-阶形高杯8-双柱单梁独基9-四柱双梁独基 |
| n | 整型 | 否 | 否 | 阶数 |
| ak | 整型 | 否 | 否 | 杯口深度 |
| ecx | 整型 | 否 | 否 | 第1阶与第2阶的S方向偏心 |
| ecy | 整型 | 否 | 否 | 第1阶与第2阶的B方向偏心 |
| s | 浮点型 | 否 | 否 | 各阶长度，最多5阶 |
| b | 浮点型 | 否 | 否 | 各阶宽度，最多5阶 |
| h | 浮点型 | 否 | 否 | 各阶高度，最多5阶 |
| lBeamB1 | 整型 | 否 | 否 | 1梁宽(mm) |
| lBeamB2 | 整型 | 否 | 否 | 2梁宽(mm) |
| lBeamH1 | 整型 | 否 | 否 | 1梁高(mm) |
| lBeamH2 | 整型 | 否 | 否 | 2梁高(mm) |
| lDis1 | 整型 | 否 | 否 | 1梁距上(左)距离(mm) |
| lDis2 | 整型 | 否 | 否 | 2梁距下(右)距离(mm) |
| lBeamBearing | 整型 | 否 | 否 | 梁方向0-水平(X)1-竖直(Y) |

### 2.21独基布置信息定义（tblDujiApp）

| 字段名 | 字段类型 | 允许为空 | 主键 | 字段含义 |
|:--:|:--:|:--:|:--:|:--:|
| ID | 整型 | 否 | 是 | 独基编号 |
| nj | 整型 | 否 | 否 | 网格点 |
| kind | 整型 | 否 | 否 | 独基定义 |
| ex | 浮点型 | 否 | 否 | 沿轴偏心(mm) |
| ey | 浮点型 | 否 | 否 | 偏轴偏心(mm) |
| ang | 浮点型 | 否 | 否 | 转角(弧度)，库里是角度，读库时转换过 |
| dBotElevat | 浮点型 | 否 | 否 | 底部标高(m) |
| nodelist | 整型数组 | 否 | 否 | 多柱独基对应的网格点（读取顺序为(N1,N2,…,Nn)，N为网格点编号） |

### 2.22桩类型定义（tblPileDef）

| 字段名 | 字段类型 | 允许为空 | 主键 | 字段含义 |
|:--:|:--:|:--:|:--:|:--:|
| ID | 整型 | 否 | 是 | 桩序号 |
| B | 整型 | 否 | 否 | 圆桩为直径，方桩为边长（mm） |
| H | 整型 | 否 | 否 | 双圆桩有效，对应左半圆直径(mm)，当m_H为0时，m_w起效 |
| F1 | 浮点型 | 否 | 否 | 桩竖向承载力标准值(kN) |
| means | 整型 | 否 | 否 | 1-预制方桩 2-水下冲(钻)孔桩 3-沉管灌注桩 4-干作业钻(挖)孔桩 5-预制砼管桩 6-钢管桩 7-双圆桩 8 - 锚杆（此时F0含义是预拉力） |
| topd | 整型 | 否 | 否 | 顶部扩大头直径（mm） |
| w | 整型 | 否 | 否 | 管桩为壁厚(mm)，双圆桩为圆心距(mm) |
| r2 | 整型 | 否 | 否 | 干作业钻(挖)孔桩扩大头直径（mm） |
| toph_u | 整型 | 否 | 否 | 扩大头上部直径(mm) |
| toph_m | 整型 | 否 | 否 | 扩大头中间直径(mm) |
| toph_b | 整型 | 否 | 否 | 扩大头下部直径(mm) |
| F0 | 浮点型 | 否 | 否 | 桩水平承载力标准值 8 - 锚杆（此时F0含义是预拉力） |
| F2 | 浮点型 | 否 | 否 | 桩抗拔承载力标准值（kN） |

### 2.23桩布置信息定义（tblPileApp）

| 字段名 | 字段类型 | 允许为空 | 主键 | 字段含义 |
|:--:|:--:|:--:|:--:|:--:|
| ID | 整型 | 否 | 是 | 编号 |
| nRaft_CT | 整型 | 否 | 否 | 与桩相连构件的ID 筏板0-9999 承台10000-19999 地基梁20000以上 |
| xx | 浮点型 | 否 | 否 | 中心点x坐标(mm) |
| yy | 浮点型 | 否 | 否 | 中心点y坐标(mm) |
| kind | 整型 | 否 | 否 | 桩定义 |
| ang | 浮点型 | 否 | 否 | 方位角(弧度) |
| len | 浮点型 | 否 | 否 | 桩长(m) |

### 2.24电梯井布置信息定义（tblElevatorApp）

| 字段名  | 字段类型 | 允许为空 | 主键 |      字段含义       |
|:-------:|:--------:|:--------:|:----:|:-------------------:|
|   ID    |   整型   |    否    |  是  |        编号         |
|  kind   |   整型   |    否    |  否  |   电梯井定义编号    |
| nRaftID |   整型   |    否    |  否  |      筏板序号       |
|   ang   |  浮点型  |    否    |  否  |  布置角度（弧度）   |
|  cenx   |  浮点型  |    否    |  否  | 中心点x向坐标（mm） |
|  ceny   |  浮点型  |    否    |  否  | 中心点y向坐标（mm） |
|   npt   |   整型   |    否    |  否  |     多边形点数      |
|   ptx   |   文本   |    否    |  否  | 多边形顶点x坐标(mm) |
|   pty   |   文本   |    否    |  否  | 多边形顶点y坐标(mm) |

### 2.25电梯井类型定义（tblElevatorDef）

| 字段名 | 字段类型 | 允许为空 | 主键 | 字段含义 |
|:--:|:--:|:--:|:--:|:--:|
| ID | 整型 | 否 | 是 | 序号 |
| shape | 整型 | 否 | 否 | 形状 0-矩形，1-多边形 |
| rectL | 整型 | 否 | 否 | 电梯井长（mm）,只用于shape =0的情况 |
| rectB | 整型 | 否 | 否 | 电梯井宽（mm）,只用于shape =0的情况 |
| depth | 整型 | 否 | 否 | 电梯井深（mm） |
| botThick | 整型 | 否 | 否 | 坑底板厚（mm） |
| nEdge | 整型 | 否 | 否 | 边数，用于各方向水平起坡距、垂直起坡距、放坡角度不等的情况，各方向尺寸相等时为1 |
| horzDist_vec | 文本 | 否 | 否 | 水平起坡距(mm)，要求数组长度\>=nEdge，下标从0开始 |
| vertDist_vec | 文本 | 否 | 否 | 垂直起坡距(mm)，要求数组长度\>=nEdge |
| slope_vec | 文本 | 否 | 否 | 放坡角度(度)，要求数组长度\>=nEdge |
| equalSize | 整型 | 否 | 否 | 各方向尺寸相同与否，1-相同，0不同 |

### 2.26加腋类型定义（tblJiaYe）

| 字段名 | 字段类型 | 允许为空 | 主键 |           字段含义           |
|:------:|:--------:|:--------:|:----:|:----------------------------:|
|   ID   |   整型   |    否    |  是  |          加腋的序号          |
|   x1   |  浮点型  |    否    |  否  |      腋角起点x坐标(mm)       |
|   y1   |  浮点型  |    否    |  否  |     腋角起点y坐标（mm）      |
|   z1   |  浮点型  |    否    |  否  |     腋角起点z坐标（mm）      |
|   x2   |  浮点型  |    否    |  否  |     腋角终点x坐标（mm）      |
|   y2   |  浮点型  |    否    |  否  |     腋角终点y坐标（mm）      |
|   z2   |  浮点型  |    否    |  否  |     腋角终点z坐标（mm）      |
|   b    |  浮点型  |    否    |  否  |          腋宽（mm）          |
|   h    |  浮点型  |    否    |  否  |          腋高（mm）          |
|  dir   |   整型   |    否    |  否  | 方向，1-右(下)，-1表示左(上) |
| offset |  浮点型  |    否    |  否  |       到网格线距离(mm)       |

### 2.27水管布置信息定义（tblWaterPipeApp）

| 字段名 | 字段类型 | 允许为空 | 主键 | 字段含义 |
|:--:|:--:|:--:|:--:|:--:|
| ID | 整型 | 否 | 是 | 序号 |
| kind | 整型 | 否 | 否 | 水管定义 |
| nRaftID | 整型 | 否 | 否 | 筏板编号 |
| npt | 整型 | 否 | 否 | 多段线点数 |
| ptx | 文本 | 否 | 否 | 多段线顶点x坐标(mm)，数组长度\>=npt，下标从0开始 |
| pty | 文本 | 否 | 否 | 多段线顶点y坐标(mm)，数组长度\>=npt，下标从0开始 |

### 2.28水管类型定义（tblWaterPipeDef）

| 字段名 | 字段类型 | 允许为空 | 主键 |        字段含义         |
|:------:|:--------:|:--------:|:----:|:-----------------------:|
|   ID   |   整型   |    否    |  是  |          序号           |
| shape  |   整型   |    否    |  否  | 形状 0-矩形 1-矩形+圆弧 |
| rectB  |   整型   |    否    |  否  |      矩形宽（mm）       |
| rectH  |   整型   |    否    |  否  |      矩形高（mm）       |
|  arcH  |  浮点型  |    否    |  否  |     圆弧拱高（mm）      |
|        |          |          |      |                         |

### 2.29水坑布置信息定义（tblWaterPitApp）

| 字段名 | 字段类型 | 允许为空 | 主键 | 字段含义 |
|:--:|:--:|:--:|:--:|:--:|
| ID | 整型 | 否 | 是 | 序号 |
| kind | 整型 | 否 | 否 | 水坑定义 |
| nRaftID | 整型 | 否 | 否 | 筏板编号 |
| ang | 浮点型 | 否 | 否 | 布置角度(弧度) |
| cenx | 浮点型 | 否 | 否 | 中心点x坐标(mm) |
| ceny | 浮点型 | 否 | 否 | 中心点y坐标(mm) |
| npt | 整型 | 否 | 否 | 多边形点数 |
| ptx | 文本 | 否 | 否 | 多边形顶点x坐标(mm)，数组长度\>=npt，下标从0开始 |
| pty | 文本 | 否 | 否 | 多边形顶点y坐标(mm)，数组长度\>=npt，下标从0开始 |

### 2.30水坑类型定义（tblWaterPitDef）

| 字段名 | 字段类型 | 允许为空 | 主键 | 字段含义 |
|:--:|:--:|:--:|:--:|:--:|
| ID | 整型 | 否 | 是 | 序号 |
| shape | 整型 | 否 | 否 | 形状 0-矩形，1-多边形 |
| rectL | 整型 | 否 | 否 | 电梯井长（mm）,只用于shape =0的情况 |
| rectB | 整型 | 否 | 否 | 电梯井宽（mm）,只用于shape =0的情况 |
| depth | 整型 | 否 | 否 | 电梯井深（mm） |
| botThick | 整型 | 否 | 否 | 坑底板厚（mm） |
| nEdge | 整型 | 否 | 否 | 边数，用于各方向水平起坡距、垂直起坡距、放坡角度不等的情况，各方向尺寸相等时为1 |
| horzDist_vec | 文本 | 否 | 否 | 水平起坡距(mm)，要求数组长度\>=nEdge，下标从0开始 |
| vertDist_vec | 文本 | 否 | 否 | 垂直起坡距(mm)，要求数组长度\>=nEdge |
| slope_vec | 文本 | 否 | 否 | 放坡角度(度)，要求数组长度\>=nEdge |
| equalSize | 整型 | 否 | 否 | 各方向尺寸相同与否，1-相同，0不同 |

## 3、配筋信息表

### 3.1筏板配筋表（房间）（tblSlabPJ_Room）

| 字段名 | 字段类型 | 允许为空 | 主键 | 字段含义 |
|:--:|:--:|:--:|:--:|:--:|
| RoomID | 整型 | 否 | 否 | 房间编号 |
| MainRaftID | 整型 | 否 | 否 | 母板编号(从0开始) |
| SubRaftID | 整型 | 否 | 否 | 子板编号(默认-1) |
| Thick | 浮点型 | 否 | 否 | 厚度(mm) |
| Asux | 浮点型 | 否 | 否 | X向板带（全部区域）筏板上部受拉钢筋面积 取：max（计算值，规范最小值）（mm<sup>2</sup>） |
| Asdx | 浮点型 | 否 | 否 | X向板带（全部区域）筏板下部受拉钢筋面积 取：max（计算值，规范最小值）（mm<sup>2</sup>） |
| Asuy | 浮点型 | 否 | 否 | Y向板带（全部区域）筏板上部受拉钢筋面积 取：max（计算值，规范最小值）（mm<sup>2</sup>） |
| Asdy | 浮点型 | 否 | 否 | Y向板带（全部区域）筏板下部受拉钢筋面积 取：max（计算值，规范最小值）（mm<sup>2</sup>） |
| Mxu | 浮点型 | 否 | 否 | X向板带（全部区域）上部正截面设计时的控制内力 计算板带上部配筋用 |
| Mxd | 浮点型 | 否 | 否 | X向板带（全部区域）上部正截面设计时的控制内力 计算板带下部配筋用 |
| Myu | 浮点型 | 否 | 否 | Y向板带（全部区域）上部正截面设计时的控制内力 计算板带上部配筋用 |
| Myd | 浮点型 | 否 | 否 | Y向板带（全部区域）上部正截面设计时的控制内力 计算板带下部配筋用 |
| AsuxMid | 浮点型 | 否 | 否 | X向板带（跨中区域）筏板上部受拉钢筋面积 取：max（计算值，规范最小值）（mm<sup>2</sup>） |
| AsdxMid | 浮点型 | 否 | 否 | X向板带（跨中区域）筏板下部受拉钢筋面积 取：max（计算值，规范最小值）（mm<sup>2</sup>） |
| AsuyMid | 浮点型 | 否 | 否 | Y向板带（跨中区域）筏板上部受拉钢筋面积 取：max（计算值，规范最小值）（mm<sup>2</sup>） |
| AsdyMid | 浮点型 | 否 | 否 | Y向板带（跨中区域）筏板下部受拉钢筋面积 取：max（计算值，规范最小值）（mm<sup>2</sup>） |

### 3.2筏板配筋表（柱间）（tblSlabPJ_Grid）

| 字段名 | 字段类型 | 允许为空 | 主键 | 字段含义 |
|:--:|:--:|:--:|:--:|:--:|
| GridID | 整型 | 否 | 否 | 网格线号 |
| MainRaftID | 整型 | 否 | 否 | 母板编号(从0开始) |
| SubRaftID | 整型 | 否 | 否 | 子板编号(默认-1) |
| thick | 浮点型 | 否 | 否 | 厚度(mm) |
| Asux | 浮点型 | 否 | 否 | 平行方向 筏板上部受拉钢筋面积 取：max（计算值，规范最小值）（mm<sup>2</sup>） |
| Asdx | 浮点型 | 否 | 否 | 平行方向 筏板下部受拉钢筋面积 取：max（计算值，规范最小值）（mm<sup>2</sup>） |
| Asuy | 浮点型 | 否 | 否 | 垂直方向 筏板上部受拉钢筋面积 取：max（计算值，规范最小值）（mm<sup>2</sup>） |
| Asdy | 浮点型 | 否 | 否 | 垂直方向 筏板下部受拉钢筋面积 取：max（计算值，规范最小值）（mm<sup>2</sup>） |
| Mxu | 浮点型 | 否 | 否 | 平行方向 上部正截面设计时的控制内力 用于计算上部受拉钢筋面积 |
| Mxd | 浮点型 | 否 | 否 | 平行方向 上部正截面设计时的控制内力 用于计算下部受拉钢筋面积 |
| Myu | 浮点型 | 否 | 否 | 垂直方向 上部正截面设计时的控制内力 用于计算上部受拉钢筋面积 |
| Myd | 浮点型 | 否 | 否 | 垂直方向 上部正截面设计时的控制内力 用于计算下部受拉钢筋面积 |

### 3.3筏板配筋表（柱下）（tblSlabPJ_Column）

| 字段名 | 字段类型 | 允许为空 | 主键 | 字段含义 |
|:--:|:--:|:--:|:--:|:--:|
| ColumnID | 整型 | 否 | 否 | 柱编号 |
| MainRaftID | 整型 | 否 | 否 | 主板编号(从0开始) |
| SubRaftID | 整型 | 否 | 否 | 子板编号(默认-1) |
| thick | 浮点型 | 否 | 否 | 厚度(mm) |
| Asdx | 浮点型 | 否 | 否 | tblSlabPJ_Wall柱下X向 筏板下部受拉钢筋面积 取：max（计算值，规范最小值）（mm<sup>2</sup>） |
| Asdy | 浮点型 | 否 | 否 | 柱下Y向 板带下部受拉钢筋面积 取：max（计算值，规范最小值）（mm<sup>2</sup>） |
| Mxd | 浮点型 | 否 | 否 | 柱下X向 上部正截面设计时的控制内力 |
| Myd | 浮点型 | 否 | 否 | 柱下Y向 上部正截面设计时的控制内力 |

### 3.4筏板配筋表（墙下）（tblSlabPJ_Wall）

| 字段名 | 字段类型 | 允许为空 | 主键 | 字段含义 |
|:--:|:--:|:--:|:--:|:--:|
| WallID | 整型 | 否 | 否 | 墙编号 |
| MainRaftID | 整型 | 否 | 否 | 母板编号 |
| SubRaftID | 整型 | 否 | 否 | 子板编号(默认-1) |
| thick | 浮点型 | 否 | 否 | 厚度(mm) |
| Asd | 浮点型 | 否 | 否 | 墙下板带配筋 取：max（计算值，规范最小值）（mm<sup>2</sup>） |
| Md | 浮点型 | 否 | 否 | 计算墙下板带配筋时上部正截面设计时的控制内力 |

### 3.5筏板配筋表（垂直地基梁方向）（tblSlabPJ_Diliang）

| 字段名 | 字段类型 | 允许为空 | 主键 | 字段含义 |
|:--:|:--:|:--:|:--:|:--:|
| DiliangID | 整型 | 否 | 否 | 地基梁编号 |
| MainRaftID | 整型 | 否 | 否 | 筏板编号（从0开始） |
| SubRaftID | 整型 | 否 | 否 | 子板编号（默认-1） |
| thick | 浮点型 | 否 | 否 | 厚度（mm） |
| Asd | 浮点型 | 否 | 否 | 垂直于地基梁的板带受拉钢筋面积 取：max（计算值，规范最小值）（mm<sup>2</sup>） |
| Md | 浮点型 | 否 | 否 | 计算垂直于地基梁的板带配筋时的上部正截面设计的控制内力 |

### 3.6承台配筋表（tblDaisPJ）

| 字段名 | 字段类型 | 允许为空 | 主键 | 字段含义 |
|:--:|:--:|:--:|:--:|:--:|
| DaisID | 整型 | 否 | 是 | 承台编号 |
| Asx_bot | 浮点型 | 否 | 否 | 承台x向底筋每延米配筋面积(mm<sup>2</sup>) |
| Asy_bot | 浮点型 | 否 | 否 | 承台y向底筋每延米配筋面积(mm<sup>2</sup>) |
| Asx_top | 浮点型 | 否 | 否 | 承台x向顶筋面积(按1m板带计算)，负数表示不用配顶筋 |
| Asy_top | 浮点型 | 否 | 否 | 承台y向顶筋面积(按1m板带计算)，负数表示不用配顶筋 |

### 3.7承台配筋表v2019（tblDaisPJ_v2019）

<table>
<colgroup>
<col style="width: 18%" />
<col style="width: 16%" />
<col style="width: 13%" />
<col style="width: 8%" />
<col style="width: 42%" />
</colgroup>
<thead>
<tr>
<th style="text-align: center;">字段名</th>
<th style="text-align: center;">字段类型</th>
<th style="text-align: center;">允许为空</th>
<th style="text-align: center;">主键</th>
<th style="text-align: center;">字段含义</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: center;">DaisID</td>
<td style="text-align: center;">整型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">承台编号</td>
</tr>
<tr>
<td style="text-align: center;">Style</td>
<td style="text-align: center;">整型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;"><p>配筋类型</p>
<p>0:异常</p>
<p>1:正交配筋，只配底筋(mm*mm/m)</p>
<p>2:正交配筋，双层双向(mm*mm/m)</p>
<p>3:梁式配筋，纵筋(mm*mm)+水平分布筋(mm*mm/m)+竖向分布筋(mm*mm/m)</p>
<p>4:梁式配筋，纵筋(mm*mm)+箍筋(mm*mm/m)</p>
<p>5:三向均匀配筋，As(mm*mm/m)，As0(mm*mm)</p>
<p>6:三向配筋，两腰+1底，Asdi/Asyao(mm*mm/m)，Asdi0/Asyao0(mm*mm)</p></td>
</tr>
<tr>
<td style="text-align: center;">Asx_bot</td>
<td style="text-align: center;">浮点型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">承台x向底筋每延米配筋面积(mm<sup>2</sup>)</td>
</tr>
<tr>
<td style="text-align: center;">Asy_bot</td>
<td style="text-align: center;">浮点型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">承台y向底筋每延米配筋面积(mm<sup>2</sup>)</td>
</tr>
<tr>
<td style="text-align: center;">Asx_top</td>
<td style="text-align: center;">浮点型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">承台x向顶筋面积(按1m板带计算)，负数表示不用配顶筋</td>
</tr>
<tr>
<td style="text-align: center;">Asy_top</td>
<td style="text-align: center;">浮点型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">承台y向顶筋面积(按1m板带计算)，负数表示不用配顶筋</td>
</tr>
<tr>
<td style="text-align: center;">bb_x</td>
<td style="text-align: center;">浮点型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">所取板带x方向长度(mm)</td>
</tr>
<tr>
<td style="text-align: center;">bb_y</td>
<td style="text-align: center;">浮点型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">所取板带y方向长度（mm）</td>
</tr>
</tbody>
</table>

### 3.8地基梁配筋表（tblDiliangPJ）

| 字段名 | 字段类型 | 允许为空 | 主键 | 字段含义 |
|:--:|:--:|:--:|:--:|:--:|
| DiliangID | 整型 | 否 | 是 | 地基梁编号 |
| Asu | 浮点型数组 | 否 | 否 | 地基梁设计截面(0-8)上部钢筋面积（mm<sup>2</sup>) |
| Asd | 浮点型数组 | 否 | 否 | 地基梁设计截面(0-8)下部钢筋面积（mm<sup>2</sup>) |
| Asv | 浮点型数组 | 否 | 否 | 地基梁设计截面(0-8)箍筋面积(mm<sup>2</sup>)，箍筋间距按"tblCalPara"定义值(100/150/200mm)计算 |
| Ast | 浮点型数组 | 否 | 否 | 地基梁设计截面(0-8)受扭纵筋面积(mm<sup>2</sup>),应沿截面周边均匀布置 |
| Ast1 | 浮点型数组 | 否 | 否 | 地基梁设计截面(0-8)受扭沿周边单肢计算箍筋面积（mm<sup>2</sup>) |
| Ash | 浮点型数组 | 否 | 否 | 地基梁设计截面(0-8)横向钢筋面积（mm<sup>2</sup>） |
| Rsumin | 浮点型数组 | 否 | 否 | 地基梁设计截面(0-8)上部最小配筋率 |
| Rsdmin | 浮点型数组 | 否 | 否 | 地基梁设计截面(0-8)下部最小配筋率 |
| Rshmin | 浮点型数组 | 否 | 否 | 地基梁设计截面(0-8)横向最小配筋率 |
| AsuCal | 浮点型数组 | 否 | 否 | 地基梁设计截面(0-8)上部计算受拉钢筋面积 |
| AsdCal | 浮点型数组 | 否 | 否 | 地基梁设计截面(0-8)下部计算受拉钢筋面积 |
| MfCtrl | 浮点型数组 | 否 | 否 | 地基梁设计截面(0-8)负弯矩设计值 |
| MzCtrl | 浮点型数组 | 否 | 否 | 地基梁设计截面(0-8)正弯矩设计值 |

### 3.9拉梁配筋表（tblLaliangPJ）

| 字段名 | 字段类型 | 允许为空 | 主键 | 字段含义 |
|:--:|:--:|:--:|:--:|:--:|
| LaliangID | 整型 | 否 | 是 | 拉梁编号 |
| Asu | 浮点型数组 | 否 | 否 | 拉梁设计截面(0-8)上部钢筋面积(mm<sup>2</sup>) |
| Asd | 浮点型数组 | 否 | 否 | 拉梁设计截面(0-8)下部钢筋面积(mm<sup>2</sup>) |
| Asv | 浮点型数组 | 否 | 否 | 拉梁设计截面(0-8)箍筋面积（mm<sup>2</sup>)，箍筋间距按"tblCalPara"定义值(100/150/200mm)计算 |
| Ast | 浮点型数组 | 否 | 否 | 拉梁设计截面(0-8)受扭纵筋面积（mm<sup>2</sup>),应沿截面周边均匀布置 |
| Ast1 | 浮点型数组 | 否 | 否 | 拉梁设计截面(0-8)受扭沿周边单肢计算箍筋面积（mm<sup>2</sup>) |

### 3.10条基配筋表（tblTiaojiPJ）

|  字段名  | 字段类型 | 允许为空 | 主键 |              字段含义              |
|:--------:|:--------:|:--------:|:----:|:----------------------------------:|
| TiaojiID |   整型   |    否    |  是  |              条基编号              |
|   Asd    |  浮点型  |    否    |  否  | 底筋每延米配筋面积(mm<sup>2</sup>) |

### 3.11独基配筋表（tblDujiPJ）

| 字段名 | 字段类型 | 允许为空 | 主键 | 字段含义 |
|:--:|:--:|:--:|:--:|:--:|
| DujiID | 整型 | 否 | 是 | 独基编号 |
| Asx_bot | 浮点型 | 否 | 否 | 独基x向底筋每延米配筋面积(mm<sup>2</sup>) |
| Asy_bot | 浮点型 | 否 | 否 | 独基y向底筋每延米配筋面积(mm<sup>2</sup>) |
| Asx_top | 浮点型 | 否 | 否 | 独基x向顶筋面积(按1m板带计算)，负数表示不用配顶筋 |
| Asy_top | 浮点型 | 否 | 否 | 独基y向顶筋面积(按1m板带计算)，负数表示不用配顶筋 |

### 3.12独基梁配筋表（tblDujiliangPJ）

| 字段名 | 字段类型 | 否 | 主键 | 字段含义 |
|:--:|:--:|:--:|:--:|:--:|
| DujiID | 整型 | 否 | 是 | 独基梁编号 |
| Asu1 | 浮点型数组 | 否 | 否 | （1顶筋）1号梁设计截面(0-8)上部钢筋面积(mm<sup>2</sup>) |
| Asd1 | 浮点型数组 | 否 | 否 | （1底筋）1号梁设计截面(0-8)下部钢筋面积(mm<sup>2</sup>) |
| Asv1 | 浮点型数组 | 否 | 否 | （1箍筋）1号梁设计截面(0-8)箍筋面积（mm<sup>2</sup>)，箍筋间距按"tblCalPara"定义值(100/150/200mm)计算 |
| Asu2 | 浮点型数组 | 否 | 否 | （2顶筋）2号梁设计截面(0-8)上部钢筋面积(mm<sup>2</sup>) |
| Asd2 | 浮点型数组 | 否 | 否 | （2底筋）2号梁设计截面(0-8)下部钢筋面积(mm<sup>2</sup>) |
| Asv2 | 浮点型数组 | 否 | 否 | （2箍筋）2号梁设计截面(0-8)箍筋面积（mm<sup>2</sup>)，箍筋间距按"tblCalPara"定义值(100/150/200mm)计算 |

## 4、恒活弯矩表

### 4.1筏板恒活弯矩表（房间）（tblSlabCrackM_Room）

| 字段名 | 字段类型 | 允许为空 | 主键 | 字段含义 |
|:--:|:--:|:--:|:--:|:--:|
| SlabID | 整型 | 否 | 是 | 板带编号 |
| D | 浮点型数组 | 否 | 否 | 房间板带（仅跨中区域）恒载弯矩(0-X向正弯矩 1-X向负弯矩 2-Y向正弯矩 3-Y向负弯矩) |
| L | 浮点型数组 | 否 | 否 | 房间板带（仅跨中区域）活载弯矩(0-X向正弯矩 1-X向负弯矩 2-Y向正弯矩 3-Y向负弯矩) |

### 4.2筏板恒活弯矩表（柱间）（tblSlabCrackM_Grid）

| 字段名 | 字段类型 | 允许为空 | 主键 | 字段含义 |
|:--:|:--:|:--:|:--:|:--:|
| SlabID | 整型 | 否 | 是 | 板带编号 |
| D | 浮点型数组 | 否 | 否 | 网格板带恒载弯矩(0-X向正弯矩 1-X向负弯矩 2-Y向正弯矩 3-Y向负弯矩) |
| L | 浮点型数组 | 否 | 否 | 网格板带活载弯矩(0-X向正弯矩 1-X向负弯矩 2-Y向正弯矩 3-Y向负弯矩) |

### 4.3筏板恒活弯矩表（柱下）（tblSlabCrackM_Column）

| 字段名 | 字段类型 | 允许为空 | 主键 | 字段含义 |
|:--:|:--:|:--:|:--:|:--:|
| SlabID | 整型 | 否 | 是 | 板带编号 |
| D | 浮点型数组 | 否 | 否 | 柱下板带恒载弯矩(0-X向正弯矩 1-X向负弯矩 2-Y向正弯矩 3-Y向负弯矩) |
| L | 浮点型数组 | 否 | 否 | 柱下板带活载弯矩(0-X向正弯矩 1-X向负弯矩 2-Y向正弯矩 3-Y向负弯矩) |

### 4.4筏板恒活弯矩表（墙下）（tblSlabCrackM_Wall）

| 字段名 | 字段类型 | 允许为空 | 主键 | 字段含义 |
|:--:|:--:|:--:|:--:|:--:|
| SlabID | 整型 | 否 | 是 | 板带编号 |
| D | 浮点型数组 | 否 | 否 | 墙下板带恒载弯矩(0-X向正弯矩 1-X向负弯矩 2-Y向正弯矩 3-Y向负弯矩) |
| L | 浮点型数组 | 否 | 否 | 墙下板带活载弯矩(0-X向正弯矩 1-X向负弯矩 2-Y向正弯矩 3-Y向负弯矩) |

### 4.5筏板恒活弯矩表（垂直地基梁方向）（tblSlabCrackM_Diliang）

| 字段名 | 字段类型 | 允许为空 | 主键 | 字段含义 |
|:--:|:--:|:--:|:--:|:--:|
| SlabID | 整型 | 否 | 是 | 板带编号 |
| D | 浮点型数组 | 否 | 否 | 墙下板带恒载弯矩(0-X向正弯矩 1-X向负弯矩 2-Y向正弯矩 3-Y向负弯矩) |
| L | 浮点型数组 | 否 | 否 | 墙下板带活载弯矩(0-X向正弯矩 1-X向负弯矩 2-Y向正弯矩 3-Y向负弯矩) |

### 4.6承台恒活弯矩表（tblDaisCrackM）

| 字段名 | 字段类型 | 允许为空 | 主键 | 字段含义 |
|:--:|:--:|:--:|:--:|:--:|
| DaisID | 整型 | 否 | 是 | 承台编号 |
| D | 浮点型数组 | 否 | 否 | 承台恒载弯矩(0-X向正弯矩 1-X向负弯矩 2-Y向正弯矩 3-Y向负弯矩) |
| L | 浮点型数组 | 否 | 否 | 承台板带活载弯矩(0-X向正弯矩 1-X向负弯矩 2-Y向正弯矩 3-Y向负弯矩) |

### 4.7地基梁恒活弯矩表（tblDiliangCrackM）

|  字段名   |  字段类型  | 允许为空 | 主键 |          字段含义           |
|:---------:|:----------:|:--------:|:----:|:---------------------------:|
| DiliangID |    整型    |    否    |  是  |         地基梁编号          |
|     D     | 浮点型数组 |    否    |  否  | 地基梁设计截面(0-8)恒载弯矩 |
|     L     | 浮点型数组 |    否    |  否  | 地基梁设计截面(0-8)活载弯矩 |

### 4.8拉梁恒活弯矩表（tblLaliangCrackM）

|  字段名   |  字段类型  | 允许为空 | 主键 |         字段含义          |
|:---------:|:----------:|:--------:|:----:|:-------------------------:|
| LaliangID |    整型    |    否    |  是  |         拉梁编号          |
|     D     | 浮点型数组 |    否    |  否  | 拉梁设计截面(0-8)恒载弯矩 |
|     L     | 浮点型数组 |    否    |  否  | 拉梁设计截面(0-8)活载弯矩 |

### 4.9条基恒活弯矩表（tblTiaojiCrackM）

|  字段名  | 字段类型 | 允许为空 | 主键 |   字段含义   |
|:--------:|:--------:|:--------:|:----:|:------------:|
| TiaojiID |   整型   |    否    |  是  |   条基编号   |
|    D     |  浮点型  |    否    |  否  | 条基恒载弯矩 |
|    L     |  浮点型  |    否    |  否  | 条基活载弯矩 |

### 4.10独基恒活弯矩表（tblDujiCrackM）

| 字段名 | 字段类型 | 允许为空 | 主键 | 字段含义 |
|:--:|:--:|:--:|:--:|:--:|
| DujiID | 整型 | 否 | 是 | 独基编号 |
| D | 浮点型数组 | 否 | 否 | 独基恒载弯矩(0-X向正弯矩 1-X向负弯矩 2-Y向正弯矩 3-Y向负弯矩) |
| L | 浮点型数组 | 否 | 否 | 独基活载弯矩(0-X向正弯矩 1-X向负弯矩 2-Y向正弯矩 3-Y向负弯矩) |

## 5、附录

### 5.1计算参数说明

| ID | ParaValue | ParaName | 含义 |
|:--:|:--:|:--:|:--:|
| 1 | 20171220 | sqlversion | 版本编号，ParaValue为整型，20171220表示当前版本为“2017年12月20日” |
| 2 | 30 | duji_rc | 独立基础混凝土强度等级，ParaValue为整型，30表示C30混凝土（下同） |
| 3 | 4 | duji_rs | 独基主筋级别 1-HPB235 2-HPB300 3-HRB335 4-HRB400 5-HRB500 6-RRB400（下同） |
| 4 | 1 | duji_gj | 独基箍筋级别 1-HPB235 2-HPB300 3-HRB335 4-HRB400 5-HRB500 6-RRB400（下同） |
| 5 | 40 | duji_cover | 独基保护层厚度（mm） |
| 6 | 30 | dais_rc | 承台混凝土级别 |
| 7 | 4 | dais_rs | 承台主筋级别 |
| 8 | 4 | dais_gj | 承台箍筋级别 |
| 9 | 40 | dais_cover | 承台保护层厚度（mm） |
| 10 | 30 | diliang_rc | 地基梁混凝土级别，ParaValue为整型，30表示C30混凝土 |
| 11 | 4 | diliang_rs | 地基梁主筋级别 |
| 12 | 4 | diliang_gj | 地基梁箍筋级别 |
| 13 | 40 | diliang_cover | 地基梁保护层厚度（mm） |
| 14 | 30 | laliang_rc | 拉梁混凝土级别 |
| 15 | 4 | laliang_rs | 拉梁主筋级别 |
| 16 | 4 | laliang_gj | 拉梁箍筋级别 |
| 17 | 40 | laliang_cover | 拉梁保护层厚度（mm） |
| 18 | 30 | raft_rc | 筏板混凝土级别 |
| 19 | 4 | raft_rs | 筏板主筋级别 |
| 20 | 1 | raft_gj | 筏板箍筋级别 |
| 21 | 40 | raft_cover | 筏板底部保护层厚度（mm） |
| 22 | 40 | raft_upcover | 筏板顶部保护层厚度（mm） |
| 23 | 30 | tiaoji_rc | 条基混凝土级别 |
| 24 | 4 | tiaoji_rs | 条基主筋级别 |
| 25 | 4 | tiaoji_gj | 条基箍筋级别 |
| 26 | 40 | tiaoji_cover | 条基保护层厚度（mm） |
| 27 | 200 | dilianggj_space | 地基梁箍筋间距（mm） |
| 28 | 5 | diliang_seismicgrade | 地基梁抗震等级 0:特一级 1:一级抗震 2:二级抗震 3:三级抗震 4:四级抗震 5:非抗震 |

### 5.2柱截面类型

| 字段值 |    字段意义    |
|:------:|:--------------:|
|   1    |      矩形      |
|   2    |     工字形     |
|   3    |      圆型      |
|   4    |    正多边形    |
|   5    |      槽形      |
|   6    |     十字形     |
|   7    |      箱形      |
|   8    |      圆管      |
|   9    |      双槽      |
|   10   |     十字工     |
|   11   |      梯形      |
|   12   |   钢管混凝土   |
|   13   |     工形劲     |
|   14   |     箱形劲     |
|   15   |     十字劲     |
|   21   |   矩形变截面   |
|   22   |   梯形变截面   |
|   23   |   箱形变截面   |
|   26   |      型钢      |
|   28   |      L形       |
|   29   |      T形       |
|   99   |  自定义多边形  |
|  101   |  不对称十字劲  |
|  102   |     圆形劲     |
|  103   |  外圆内工形劲  |
|  104   |  外圆内圆形劲  |
|  105   |  外圆内十字劲  |
|  301   | 实腹式组合截面 |
|  302   | 格构式组合截面 |
|  303   |    薄壁型钢    |
|  304   |  薄壁型钢组合  |
|  305   |   自定义截面   |

### 5.3柱截面尺寸

序列化int值存储，第一位为截面类型（参看附录5.2），后面的为截面尺寸，即为B、H、U、T、D、F…(以逗号分隔)同YJK截面类型中的截面尺寸值。

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 40%" />
<col style="width: 42%" />
</colgroup>
<thead>
<tr>
<th style="text-align: center;">构件类型</th>
<th style="text-align: center;">截面类型</th>
<th style="text-align: center;">值的意义</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: center;">1（墙）</td>
<td style="text-align: center;">1</td>
<td style="text-align: left;"><p>墙厚</p>
<p>墙高（目前版本为0）</p>
<p>材料</p>
<p>唯一Id</p></td>
</tr>
<tr>
<td style="text-align: center;">21（墙洞）</td>
<td style="text-align: center;">1</td>
<td style="text-align: left;"><p>洞口宽</p>
<p>洞口高</p>
<p>材料</p>
<p>唯一ID</p></td>
</tr>
<tr>
<td style="text-align: center;"><p>11（柱）</p>
<p>12（梁）</p>
<p>13（支撑）</p>
<p>15（圈梁）</p></td>
<td style="text-align: center;">1（矩形）</td>
<td style="text-align: left;"><p>矩形宽</p>
<p>矩形高</p>
<p>材料</p>
<p>唯一ID</p></td>
</tr>
<tr>
<td style="text-align: center;"></td>
<td style="text-align: center;">2（工字形）</td>
<td style="text-align: left;"><p>腹板厚度</p>
<p>截面总高</p>
<p>上翼宽度</p>
<p>上翼厚度</p>
<p>下翼宽度</p>
<p>下翼厚度</p>
<p>材料</p>
<p>唯一ID</p></td>
</tr>
<tr>
<td style="text-align: center;"></td>
<td style="text-align: center;">3（圆形）</td>
<td style="text-align: left;"><p>直径</p>
<p>材料</p>
<p>唯一ID</p></td>
</tr>
<tr>
<td style="text-align: center;"></td>
<td style="text-align: center;">4（正多边形）</td>
<td style="text-align: left;"><p>外圆直径</p>
<p>边数</p>
<p>材料</p>
<p>唯一ID</p></td>
</tr>
<tr>
<td style="text-align: center;"></td>
<td style="text-align: center;">5（正多边形）</td>
<td style="text-align: left;"><p>外圆直径</p>
<p>边数</p>
<p>材料</p>
<p>唯一ID</p></td>
</tr>
<tr>
<td style="text-align: center;"></td>
<td style="text-align: center;">6（十字形）</td>
<td style="text-align: left;"><p>腹板厚度</p>
<p>截面总高</p>
<p>上边距离</p>
<p>翼缘厚度</p>
<p>左翼宽度</p>
<p>右翼宽度</p>
<p>材料</p>
<p>唯一ID</p></td>
</tr>
<tr>
<td style="text-align: center;"></td>
<td style="text-align: center;">7（箱形）</td>
<td style="text-align: left;"><p>截面总宽</p>
<p>截面总高</p>
<p>上边厚度</p>
<p>左边厚度</p>
<p>下边厚度</p>
<p>右边厚度</p>
<p>材料</p>
<p>唯一ID</p></td>
</tr>
<tr>
<td style="text-align: center;"></td>
<td style="text-align: center;">8（圆管）</td>
<td style="text-align: left;"><p>外圆直径</p>
<p>内圆直径</p>
<p>材料</p>
<p>唯一ID</p></td>
</tr>
<tr>
<td style="text-align: center;"></td>
<td style="text-align: center;">9（双槽）</td>
<td style="text-align: left;"><p>腹板厚度</p>
<p>截面总高</p>
<p>上翼宽度</p>
<p>翼缘厚度</p>
<p>下翼宽度</p>
<p>最小间距</p>
<p>材料</p>
<p>唯一ID</p></td>
</tr>
<tr>
<td style="text-align: center;"></td>
<td style="text-align: center;">10（十字工）</td>
<td style="text-align: left;"><p>竖向腹板厚度</p>
<p>竖向截面总高</p>
<p>竖向翼缘厚度</p>
<p>竖向翼缘宽度</p>
<p>横向腹板厚度</p>
<p>横向截面总高</p>
<p>横向翼缘厚度</p>
<p>横向翼缘宽度</p>
<p>材料</p>
<p>唯一ID</p></td>
</tr>
<tr>
<td style="text-align: center;"></td>
<td style="text-align: center;">11（梯形）</td>
<td style="text-align: left;"><p>底边宽度</p>
<p>截面总高</p>
<p>左上伸长</p>
<p>右上伸长</p>
<p>材料</p>
<p>唯一ID</p></td>
</tr>
<tr>
<td style="text-align: center;"></td>
<td style="text-align: center;">12（钢管混凝土）</td>
<td style="text-align: left;"><p>外圆直径</p>
<p>内圆直径</p>
<p>材料</p>
<p>唯一ID</p></td>
</tr>
<tr>
<td style="text-align: center;"></td>
<td style="text-align: center;">13（工形劲）</td>
<td style="text-align: left;"><p>截面总宽</p>
<p>截面总高</p>
<p>腹板厚度</p>
<p>形钢总高</p>
<p>翼缘宽度</p>
<p>翼缘厚度</p>
<p>材料</p>
<p>唯一ID</p></td>
</tr>
<tr>
<td style="text-align: center;"></td>
<td style="text-align: center;">14（箱形劲）</td>
<td style="text-align: left;"><p>截面总宽</p>
<p>截面总高</p>
<p>形钢总宽</p>
<p>形钢总高</p>
<p>上下厚度</p>
<p>左右厚度</p>
<p>材料</p>
<p>唯一ID</p></td>
</tr>
<tr>
<td style="text-align: center;"></td>
<td style="text-align: center;">15（十字劲）</td>
<td style="text-align: left;"><p>截面总宽</p>
<p>截面总高</p>
<p>腹板厚度</p>
<p>翼缘厚度</p>
<p>形钢总高</p>
<p>翼缘宽度</p>
<p>材料</p>
<p>唯一ID</p></td>
</tr>
<tr>
<td style="text-align: center;"></td>
<td style="text-align: center;">21（矩形变截面）</td>
<td style="text-align: left;"><p>截面总宽</p>
<p>截面总高</p>
<p>腹板厚度</p>
<p>材料</p>
<p>唯一ID</p></td>
</tr>
<tr>
<td style="text-align: center;"></td>
<td style="text-align: center;">22（H形变截面）</td>
<td style="text-align: left;"><p>Ｈ形下翼缘宽度</p>
<p>Ｈ形上翼缘宽度</p>
<p>Ｈ形截面左端高度</p>
<p>Ｈ形截面右端高度</p>
<p>Ｈ形腹板厚度</p>
<p>Ｈ形下翼缘厚度</p>
<p>Ｈ形上翼缘厚度</p>
<p>材料</p>
<p>唯一ID</p></td>
</tr>
<tr>
<td style="text-align: center;"></td>
<td style="text-align: center;">23（箱形变截面）</td>
<td style="text-align: left;"><p>箱形截面宽度</p>
<p>箱形截面左端高度</p>
<p>箱形截面右端高度</p>
<p>箱形截面腹板壁厚</p>
<p>箱形截面翼缘壁厚</p>
<p>材料</p>
<p>唯一ID</p></td>
</tr>
<tr>
<td style="text-align: center;"></td>
<td style="text-align: center;">28（L形）</td>
<td style="text-align: left;"><p>腹板厚度</p>
<p>截面总高</p>
<p>翼缘宽度</p>
<p>翼缘厚度</p>
<p>材料</p>
<p>唯一ID</p></td>
</tr>
<tr>
<td style="text-align: center;"></td>
<td style="text-align: center;">29（T形）</td>
<td style="text-align: left;"><p>腹板厚度</p>
<p>截面总高</p>
<p>翼缘宽度</p>
<p>翼缘厚度</p>
<p>材料</p>
<p>唯一ID</p></td>
</tr>
<tr>
<td style="text-align: center;"></td>
<td style="text-align: center;">101（不对称十字劲）</td>
<td style="text-align: left;"><p>截面总宽度</p>
<p>截面总高度</p>
<p>纵向工形腹板厚度</p>
<p>纵向工形翼缘厚度</p>
<p>纵向工形截面总高</p>
<p>纵向工形翼缘宽度</p>
<p>横向工形腹板厚度</p>
<p>横向工形翼缘厚度</p>
<p>横向工形截面总高</p>
<p>横向工形翼缘宽度</p>
<p>材料</p>
<p>唯一ID</p></td>
</tr>
<tr>
<td style="text-align: center;"></td>
<td style="text-align: center;">102（圆形劲）</td>
<td style="text-align: left;"><p>截面总宽度</p>
<p>截面总高度</p>
<p>钢管外径(</p>
<p>钢管内径(</p>
<p>材料</p>
<p>唯一ID</p></td>
</tr>
<tr>
<td style="text-align: center;"></td>
<td style="text-align: center;">103（外圆内工形劲）</td>
<td style="text-align: left;"><p>圆形直径</p>
<p>工形腹板厚度</p>
<p>工形总高度</p>
<p>工形翼缘宽度</p>
<p>工形翼缘厚度</p>
<p>材料</p>
<p>唯一ID</p></td>
</tr>
<tr>
<td style="text-align: center;"></td>
<td style="text-align: center;">104（外圆内圆形劲）</td>
<td style="text-align: left;"><p>截面直径</p>
<p>钢管外径</p>
<p>钢管内径</p>
<p>材料</p>
<p>唯一ID</p></td>
</tr>
<tr>
<td style="text-align: center;"></td>
<td style="text-align: center;">105（外圆内十字劲）</td>
<td style="text-align: left;"><p>圆形直径</p>
<p>纵向工形腹板厚度</p>
<p>纵向工形翼缘厚度</p>
<p>纵向工形截面总高</p>
<p>纵向工形翼缘宽度</p>
<p>横向工形腹板厚度</p>
<p>横向工形翼缘厚度</p>
<p>横向工形截面总高</p>
<p>横向工形翼缘宽度</p>
<p>材料</p>
<p>唯一ID</p></td>
</tr>
</tbody>
</table>
