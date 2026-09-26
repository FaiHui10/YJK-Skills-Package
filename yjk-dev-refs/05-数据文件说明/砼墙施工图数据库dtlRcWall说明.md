> 来源：YJK 官方二次开发文档包 `数据库文件说明.rar` 内 `砼墙施工图数据库dtlRcWall说明.docx`，由 pandoc 从 .docx 转换为 Markdown（纯文本，图片以标记代替）。

# dtlRcWall.ydb数据结构

### 墙施工图数据中的基本概念

由建模里提供的墙段(WallSeg)穿串形成连续墙，连续墙在节点处或洞口分跨形成墙跨(WallSpan)，墙跨与计算模型中的墙柱(WallColumn)有一一对应的关系，可以看成是一个东西。墙跨间，墙洞上面的部分即为墙梁(WallBeam)，这个墙梁与计算模型中的墙梁是一个概念。墙跨端部、面外墙、梁与墙跨相连处均会生成墙肢(WallLeg)，相交的墙肢及边框柱组合在一起即为边缘构件(EdgeMember)。墙跨中未被墙肢覆盖的部分即为墙身(WallBody)。边缘构件(EdgeMember)、墙梁(WallBeam)、墙身(WallBody)为墙施工图中三种最基本的配筋单位。本数据库中保存的钢筋均为分组归并后的结果。三种基本单位分组归并后分别生成边缘构件配筋组(RcEdgeMember)、墙梁配筋组(RcWallBeam)和墙身配筋组(RcWallBody)。各种配筋组是保存钢筋和构件名称的基本单位。

墙施工图的楼层划分是以钢筋层(ReinFloor)为基本单位的，如果几个自然层构件布置相同，设计结果相近，可以将其归并为同一钢筋层。同一钢筋层的构件只配一次钢筋。

### 工程参数（tblRcWallPara）

| 字段名  | 字段类型 | 允许为空 | 主键 | 字段含义 |
|:-------:|:--------:|:--------:|:----:|:--------:|
|   ID    |   整型   |    否    |  是  |  参数ID  |
| ParaVal |   可变   |    是    |  否  |  参数值  |

目前该表只保存一个版本号（ID为65535,值为整形,目前值为20120706），用于今后数据结构扩展时的版本控制。其他的施工图相关参数保存在工程目录下的DrawSet_Wall.CSV中，该文件为文本格式，每行一个参数，含义自明。

### 自然层（tblFloor）

|  字段名   | 字段类型 | 允许为空 | 主键 |        字段含义        |
|:---------:|:--------:|:--------:|:----:|:----------------------:|
|    ID     |   整型   |    否    |  是  |        自然层ID        |
| StdFlrID  |   整型   |    否    |  否  | 自然层所对应的标准层ID |
| ReinFlrID |   整型   |    否    |  是  | 自然层所对应的钢筋层ID |
|   Name    |   整型   |    是    |  否  |        自然层名        |
|  LevelB   |  浮点型  |    否    |  否  |   自然层层底标高(mm)   |
|  Height   |  浮点型  |    否    |  否  |     自然层层高(mm)     |

该表与模型数据库dtlModel.ydb的tblFloor很相似。只是多了一个ReinFlrID字段。该字段用于自然层与钢筋层的对位。其他字段都是为了检查模型与施工图能否对应而增加的冗余数据。

### 钢筋层（tblReinFloor）

| 字段名  | 字段类型 | 允许为空 | 主键 |    字段含义    |
|:-------:|:--------:|:--------:|:----:|:--------------:|
|   ID    |   整型   |    否    |  是  |    钢筋层ID    |
|  Name   |   整型   |    是    |  否  |    钢筋层名    |
| FloorID |   整型   |    是    |  否  | 代表自然层的ID |

该表中FloorID字段记录了此钢筋层最后一次配筋出图时用的哪个自然层。如果FloorID为空，则该钢筋层从未进行过配筋出图。FloorID如果不为空，必须要保证该自然层属于本条记录所代表的那个钢筋层。

### 墙跨信息（tblWallSpan）

<table>
<colgroup>
<col style="width: 15%" />
<col style="width: 14%" />
<col style="width: 13%" />
<col style="width: 8%" />
<col style="width: 47%" />
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
<td style="text-align: center;">ID</td>
<td style="text-align: center;">整型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">墙跨ID</td>
</tr>
<tr>
<td style="text-align: center;">FloorID</td>
<td style="text-align: center;">整型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">墙跨所在的自然层ID</td>
</tr>
<tr>
<td style="text-align: center;">CalcID</td>
<td style="text-align: center;">整型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">墙跨在计算模型中对应的墙柱ID</td>
</tr>
<tr>
<td style="text-align: center;">B</td>
<td style="text-align: center;">浮点型</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">墙厚</td>
</tr>
<tr>
<td style="text-align: center;">Len</td>
<td style="text-align: center;">浮点型</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">墙跨长，按网格度量</td>
</tr>
<tr>
<td style="text-align: center;">X1</td>
<td style="text-align: center;">浮点型</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
<td rowspan="4" style="text-align: center;"><p>墙跨起止点的坐标，</p>
<p>按定位网格线衡量</p></td>
</tr>
<tr>
<td style="text-align: center;">Y1</td>
<td style="text-align: center;">浮点型</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
</tr>
<tr>
<td style="text-align: center;">X2</td>
<td style="text-align: center;">浮点型</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
</tr>
<tr>
<td style="text-align: center;">Y2</td>
<td style="text-align: center;">浮点型</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
</tr>
<tr>
<td style="text-align: center;">ZT1</td>
<td style="text-align: center;">浮点型</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
<td rowspan="2" style="text-align: center;">墙跨起止点的顶高差,层顶标高处为0</td>
</tr>
<tr>
<td style="text-align: center;">ZT2</td>
<td style="text-align: center;">浮点型</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
</tr>
<tr>
<td style="text-align: center;">ZB1</td>
<td style="text-align: center;">浮点型</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
<td rowspan="2" style="text-align: center;">墙跨起止点的底高差,层底标高处为0</td>
</tr>
<tr>
<td style="text-align: center;">ZB2</td>
<td style="text-align: center;">浮点型</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
</tr>
<tr>
<td style="text-align: center;">XC</td>
<td style="text-align: center;">浮点型</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
<td rowspan="2" style="text-align: center;">弧墙跨圆心点坐标,非弧墙跨为空</td>
</tr>
<tr>
<td style="text-align: center;">YC</td>
<td style="text-align: center;">浮点型</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
</tr>
<tr>
<td style="text-align: center;">Ecc</td>
<td style="text-align: center;">浮点型</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">墙跨中心线与网格线的偏心</td>
</tr>
</tbody>
</table>

### 边框柱段信息（tblColSeg）

<table>
<colgroup>
<col style="width: 15%" />
<col style="width: 14%" />
<col style="width: 13%" />
<col style="width: 8%" />
<col style="width: 47%" />
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
<td style="text-align: center;">ID</td>
<td style="text-align: center;">整型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">柱段ID</td>
</tr>
<tr>
<td style="text-align: center;">FloorID</td>
<td style="text-align: center;">整型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">所在自然层的ID</td>
</tr>
<tr>
<td style="text-align: center;">SectDef</td>
<td style="text-align: center;">文本</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">柱截面信息</td>
</tr>
<tr>
<td style="text-align: center;">JointX</td>
<td style="text-align: center;">浮点型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">否</td>
<td rowspan="2" style="text-align: center;">柱所在节点的坐标</td>
</tr>
<tr>
<td style="text-align: center;">JointY</td>
<td style="text-align: center;">浮点型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">否</td>
</tr>
<tr>
<td style="text-align: center;">EccX</td>
<td style="text-align: center;">浮点型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">沿轴偏心</td>
</tr>
<tr>
<td style="text-align: center;">EccY</td>
<td style="text-align: center;">浮点型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">偏轴偏心</td>
</tr>
<tr>
<td style="text-align: center;">Rotation</td>
<td style="text-align: center;">浮点型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">转角</td>
</tr>
<tr>
<td style="text-align: center;">EMID</td>
<td style="text-align: center;">整型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">所属边缘构件的ID</td>
</tr>
</tbody>
</table>

本表中只保存按柱子进行配筋的边缘构件所在的柱段。真正有意义的字段只有构成主键的ID、FloorID,以及EMID。其他字段都是为了检查模型是否发生变化的冗余字段。其含义同dtlModel.ydb数据库中表dtlColSeg的同名字段。SectDef的含义同dtlModel.ydb数据库中表dtlColSect中的ShapeVal字段。

### 墙肢信息（tblWallLeg）

<table>
<colgroup>
<col style="width: 15%" />
<col style="width: 14%" />
<col style="width: 13%" />
<col style="width: 8%" />
<col style="width: 47%" />
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
<td style="text-align: center;">ID</td>
<td style="text-align: center;">整型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">墙肢ID</td>
</tr>
<tr>
<td style="text-align: center;">SpanID</td>
<td style="text-align: center;">整型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">所属墙跨ID</td>
</tr>
<tr>
<td style="text-align: center;">B</td>
<td style="text-align: center;">浮点型</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">墙厚</td>
</tr>
<tr>
<td style="text-align: center;">Len</td>
<td style="text-align: center;">浮点型</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">墙肢阴影区的长度</td>
</tr>
<tr>
<td style="text-align: center;">X1</td>
<td style="text-align: center;">浮点型</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
<td rowspan="4" style="text-align: center;">墙肢起止点的坐标(不含λ/2区)</td>
</tr>
<tr>
<td style="text-align: center;">Y1</td>
<td style="text-align: center;">浮点型</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
</tr>
<tr>
<td style="text-align: center;">X2</td>
<td style="text-align: center;">浮点型</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
</tr>
<tr>
<td style="text-align: center;">Y2</td>
<td style="text-align: center;">浮点型</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
</tr>
<tr>
<td style="text-align: center;">EMID</td>
<td style="text-align: center;">整型</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">所属边缘构件的ID</td>
</tr>
<tr>
<td style="text-align: center;">LcHS</td>
<td style="text-align: center;">文本</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
<td rowspan="4" style="text-align: center;">拟用于保存约束边缘构件λ/2区的配筋，目前暂时没有存这个字段的数据</td>
</tr>
<tr>
<td style="text-align: center;">LcVS</td>
<td style="text-align: center;">文本</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
</tr>
<tr>
<td style="text-align: center;">LcHS</td>
<td style="text-align: center;">文本</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
</tr>
<tr>
<td style="text-align: center;">LcVS</td>
<td style="text-align: center;">文本</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
</tr>
<tr>
<td style="text-align: center;">PcID</td>
<td style="text-align: center;">浮点型</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">所属预制墙的ID</td>
</tr>
<tr>
<td style="text-align: center;">LcLenS</td>
<td style="text-align: center;">浮点型</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
<td rowspan="2" style="text-align: center;">起端终端λ/2区长度，&lt; 0表示相邻墙身整体按λ/2区处理, = 0或为空表示无λ/2区</td>
</tr>
<tr>
<td style="text-align: center;">LcLenE</td>
<td style="text-align: center;">浮点型</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
</tr>
<tr>
<td style="text-align: center;">Ecc</td>
<td style="text-align: center;">浮点型</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">墙肢中心线与网格线的偏心</td>
</tr>
<tr>
<td style="text-align: center;">GridCurve</td>
<td style="text-align: center;">二进制</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">墙肢网格线具体坐标<sup>注1</sup></td>
</tr>
<tr>
<td style="text-align: center;">Asv</td>
<td style="text-align: center;">浮点型</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">抗剪所需箍筋面积<sup>注2</sup></td>
</tr>
</tbody>
</table>

注1：GridCurve 列表示墙肢网格线具体坐标。此列有数的话，将由N\*3个float数构成，N为网格线顶点个数。第i顶点坐标为( Cv\[i\*3\], Cv\[i\*3+1\]),第i段拱高为Cv\[i\*3+2\]。此列为空表示网格线为两点直线，用(X1,Y1,X2,Y2)即可确定网格线，不需额外附加具体坐标。

注2：通常情况，墙的水平剪力由墙身水平筋承担。但是对于两侧均无相邻墙身的独立墙肢，此剪力只能由墙肢箍筋承担。因此只有两侧均无相邻墙身的独立墙肢才Asv才有数，数值得具体含义为竖向间距Sv范围内所需箍筋面积。其中Sv为前处理计算参数中填写的墙水平分布筋间距。

### 边缘构件信息（tblEdgeMember）

|  字段名   | 字段类型 | 允许为空 | 主键 |         字段含义          |
|:---------:|:--------:|:--------:|:----:|:-------------------------:|
|    ID     |   整型   |    否    |  是  |        边缘构件ID         |
|  FloorID  |   整型   |    否    |  否  |       所属自然层ID        |
|   Type    |   整形   |    是    |  否  |   边缘构件类型,含义下详   |
|  Attrib   |   整形   |    是    |  否  |       边缘构件属性        |
| Boundary  | 二进制值 |    是    |  否  |   边缘构件外轮廓的坐标    |
|  RcEMID   |   整型   |    是    |  否  |  所属边缘构件配筋组的ID   |
| AsStruct  |  浮点型  |    是    |  否  | 构造所需纵筋配筋面积(mm2) |
| AsDesign  |  浮点型  |    是    |  否  | 设计所需纵筋配筋面积(mm2) |
| AsvDesign |  浮点型  |    是    |  否  |  箍筋的最小体积配箍率(%)  |

Type值的含义：构造边缘构件为0，约束边缘构件为1，按柱配筋的边框柱为10(矩形柱)、11(圆形柱)或12(异型柱)。

Boundary字段保存了一个float数组。数组大小为边界多边形顶点数乘以3。每三个数一组，分别代表顶点的X坐标、顶点的Y坐标、弧边的拱高(直边第三个数为0.0)。

### 墙身信息（tblWallBody）

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 14%" />
<col style="width: 13%" />
<col style="width: 8%" />
<col style="width: 47%" />
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
<td style="text-align: center;">ID</td>
<td style="text-align: center;">整型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">墙肢ID</td>
</tr>
<tr>
<td style="text-align: center;">SpanID</td>
<td style="text-align: center;">整型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">所属墙跨ID</td>
</tr>
<tr>
<td style="text-align: center;">B</td>
<td style="text-align: center;">浮点型</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">墙厚</td>
</tr>
<tr>
<td style="text-align: center;">Len</td>
<td style="text-align: center;">浮点型</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">墙身的长度，按网格线度量</td>
</tr>
<tr>
<td style="text-align: center;">X1</td>
<td style="text-align: center;">浮点型</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
<td rowspan="4" style="text-align: center;">墙身起止点的坐标，按网格线度量</td>
</tr>
<tr>
<td style="text-align: center;">Y1</td>
<td style="text-align: center;">浮点型</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
</tr>
<tr>
<td style="text-align: center;">X2</td>
<td style="text-align: center;">浮点型</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
</tr>
<tr>
<td style="text-align: center;">Y2</td>
<td style="text-align: center;">浮点型</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
</tr>
<tr>
<td style="text-align: center;">RcBodyID</td>
<td style="text-align: center;">整型</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">所属墙身配筋组的ID</td>
</tr>
<tr>
<td style="text-align: center;">AllSpanIDs</td>
<td style="text-align: center;">二进制</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">Int形数组，跨越多跨时记录全部墙跨</td>
</tr>
<tr>
<td style="text-align: center;">PcID</td>
<td style="text-align: center;">整型</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">所属预制墙的ID</td>
</tr>
<tr>
<td style="text-align: center;">Ecc</td>
<td style="text-align: center;">浮点型</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">墙身中心线与网格线的偏心</td>
</tr>
<tr>
<td style="text-align: center;">GridCurve</td>
<td style="text-align: center;">二进制</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">墙身网格线具体坐标<sup>注1</sup></td>
</tr>
</tbody>
</table>

注1：GridCurve 列表示墙肢网格线具体坐标。此列有数的话，将由N\*3个float数构成，N为网格线顶点个数。第i顶点坐标为( Cv\[i\*3\], Cv\[i\*3+1\]),第i段拱高为Cv\[i\*3+2\]。此列为空表示网格线为两点直线，用(X1,Y1,X2,Y2)即可确定网格线，不需额外附加具体坐标。

### 墙梁信息（tblWallBeam）

<table>
<colgroup>
<col style="width: 15%" />
<col style="width: 14%" />
<col style="width: 13%" />
<col style="width: 8%" />
<col style="width: 47%" />
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
<td style="text-align: center;">ID</td>
<td style="text-align: center;">整型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">墙梁ID</td>
</tr>
<tr>
<td style="text-align: center;">FloorID</td>
<td style="text-align: center;">整型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">所属自然层ID</td>
</tr>
<tr>
<td style="text-align: center;">B</td>
<td style="text-align: center;">浮点型</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">墙梁宽</td>
</tr>
<tr>
<td style="text-align: center;">H</td>
<td style="text-align: center;">浮点型</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">墙梁高</td>
</tr>
<tr>
<td style="text-align: center;">HDiff</td>
<td style="text-align: center;">浮点型</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">墙梁上皮与层顶标高的高差</td>
</tr>
<tr>
<td style="text-align: center;">Len</td>
<td style="text-align: center;">浮点型</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">墙梁的长度</td>
</tr>
<tr>
<td style="text-align: center;">X1</td>
<td style="text-align: center;">浮点型</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
<td rowspan="4" style="text-align: center;">墙梁起止点的坐标，按墙梁中心线</td>
</tr>
<tr>
<td style="text-align: center;">Y1</td>
<td style="text-align: center;">浮点型</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
</tr>
<tr>
<td style="text-align: center;">X2</td>
<td style="text-align: center;">浮点型</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
</tr>
<tr>
<td style="text-align: center;">Y2</td>
<td style="text-align: center;">浮点型</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
</tr>
<tr>
<td style="text-align: center;">RcBeamID</td>
<td style="text-align: center;">整型</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">所属墙梁配筋组的ID</td>
</tr>
<tr>
<td style="text-align: center;">XC</td>
<td style="text-align: center;">浮点型</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
<td rowspan="2" style="text-align: center;">弧墙跨圆心点坐标,非弧墙跨为空</td>
</tr>
<tr>
<td style="text-align: center;">YC</td>
<td style="text-align: center;">浮点型</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
</tr>
<tr>
<td style="text-align: center;">PcID</td>
<td style="text-align: center;">整型</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">所属预制墙的ID</td>
</tr>
</tbody>
</table>

### 边缘构件配筋组（tblRcEdgeMember）

|  字段名   | 字段类型 | 允许为空 | 主键 |     字段含义     |
|:---------:|:--------:|:--------:|:----:|:----------------:|
|    ID     |   整型   |    否    |  是  |      墙梁ID      |
| ReinFlrID |   整型   |    否    |  否  |   所属钢筋层ID   |
|   Name    |   文本   |    否    |  否  |   边缘构件名称   |
|  MainBar  |   文本   |    是    |  否  |       主筋       |
|  HoopBar  |   文本   |    是    |  否  |       箍筋       |
|   Flags   |   整形   |    是    |  否  | 边缘构件箍筋形式 |

MainBar为边缘构件中全部的纵筋根数。HoopBar为边缘构件箍筋。Flags为边缘构件箍筋形式，可能有以下值：

kRcEmHoopisDefault = 0x0001,//采用工程默认参数

kRcEmHoopisClosed = 0x0002, //内部拉筋采用封闭箍---（对应拉筋）

kRcEmHoopisAllLacing = 0x0004, //内部拉筋采用全部拉筋---（对应隔一拉一）

如果配筋组中保存的是按柱配筋的边框柱边缘构件，数据格式可能有些变化：矩形柱的MainBar字段变为用逗号隔开的三组配筋，形如“4B18,3B18,2B18”，三组配筋分别代表角筋、B边钢筋、H边钢筋。异形柱的MainBar字段变为用逗号隔开的两组配筋，分别代表固定筋、分布筋。矩形柱的箍筋字段增加肢数表示，形如“A10@100/150{4x4}”，其中用花括号{}括起来的两个数分别为B边、H边箍筋肢数。按柱配筋的边缘构件Flag字段没有意义，其值始终为空。

### 墙身配筋组（tblRcEdgeMember）

| 字段名 | 字段类型 | 允许为空 | 主键 | 字段含义 |
|:--:|:--:|:--:|:--:|:--:|
| ID | 整型 | 否 | 是 | 墙梁ID |
| ReinFlrID | 整型 | 否 | 否 | 所属钢筋层ID |
| Name | 文本 | 否 | 否 | 边缘构件名称 |
| B | 整形 | 否 | 否 | 墙身厚度，取整到5mm |
| NumRow | 整形 | 是 | 否 | 分布筋排数 |
| HoriBar | 文本 | 是 | 否 | 水平分布筋 |
| VertBar | 文本 | 是 | 否 | 竖直分布筋 |
| TieBar | 文本 | 是 | 否 | 拉筋 |
| TieBarType | 整形 | 是 | 否 | 拉筋形式 0，由工程参数确定，1,双向2 梅花双向 |

###  墙梁配筋组（tblRcWallBeam）

<table>
<colgroup>
<col style="width: 20%" />
<col style="width: 11%" />
<col style="width: 13%" />
<col style="width: 7%" />
<col style="width: 46%" />
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
<td style="text-align: center;">ID</td>
<td style="text-align: center;">整型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">墙梁ID</td>
</tr>
<tr>
<td style="text-align: center;">ReinFlrID</td>
<td style="text-align: center;">整型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">所属钢筋层ID</td>
</tr>
<tr>
<td style="text-align: center;">Name</td>
<td style="text-align: center;">文本</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">边缘构件名称</td>
</tr>
<tr>
<td style="text-align: center;">B</td>
<td style="text-align: center;">整形</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">墙身厚度，取整到5mm</td>
</tr>
<tr>
<td style="text-align: center;">TopBar</td>
<td style="text-align: center;">文本</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">顶筋</td>
</tr>
<tr>
<td style="text-align: center;">BottomBar</td>
<td style="text-align: center;">文本</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">底筋</td>
</tr>
<tr>
<td style="text-align: center;">HoopBar</td>
<td style="text-align: center;">文本</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">箍筋</td>
</tr>
<tr>
<td style="text-align: center;">YaoBar</td>
<td style="text-align: center;">文本</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">侧面筋,为空时表示使用相邻墙身的水平分布筋</td>
</tr>
<tr>
<td style="text-align: center;">YaoLaBar</td>
<td style="text-align: center;">文本</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">侧向筋的拉结筋，暂未记录</td>
</tr>
<tr>
<td style="text-align: center;">CrossBar</td>
<td style="text-align: center;">文本</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">斜筋或对角暗撑的单侧纵筋</td>
</tr>
<tr>
<td style="text-align: center;">CrossLaBar</td>
<td style="text-align: center;">文本</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;"><p>交叉斜筋的末端拉筋或</p>
<p>对角暗撑的箍筋</p></td>
</tr>
<tr>
<td style="text-align: center;">CrossBarType</td>
<td style="text-align: center;">整形</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">斜筋类型： 0 没有 1交叉斜筋 2对角暗撑 3 集中对角斜筋</td>
</tr>
</tbody>
</table>

### 预制墙信息（tblPcWall）

<table>
<colgroup>
<col style="width: 15%" />
<col style="width: 14%" />
<col style="width: 13%" />
<col style="width: 8%" />
<col style="width: 47%" />
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
<td style="text-align: center;">ID</td>
<td style="text-align: center;">整型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">预制墙ID</td>
</tr>
<tr>
<td style="text-align: center;">FlrID</td>
<td style="text-align: center;">整型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">所在自然层ID</td>
</tr>
<tr>
<td style="text-align: center;">Name</td>
<td style="text-align: center;">文本</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">预制墙名称</td>
</tr>
<tr>
<td style="text-align: center;">X1</td>
<td style="text-align: center;">浮点型</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
<td rowspan="4" style="text-align: center;">预制墙起止点的坐标，按网格线度量</td>
</tr>
<tr>
<td style="text-align: center;">Y1</td>
<td style="text-align: center;">浮点型</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
</tr>
<tr>
<td style="text-align: center;">X2</td>
<td style="text-align: center;">浮点型</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
</tr>
<tr>
<td style="text-align: center;">Y2</td>
<td style="text-align: center;">浮点型</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
</tr>
<tr>
<td style="text-align: center;">RcID</td>
<td style="text-align: center;">整型</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">所属墙身配筋组的ID</td>
</tr>
<tr>
<td style="text-align: center;">PcID</td>
<td style="text-align: center;">浮点型</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">所属预制墙的ID</td>
</tr>
<tr>
<td style="text-align: center;">B</td>
<td style="text-align: center;">浮点型</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">墙厚</td>
</tr>
<tr>
<td style="text-align: center;">Len</td>
<td style="text-align: center;">浮点型</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">预制墙的长度，按网格线度量</td>
</tr>
<tr>
<td style="text-align: center;">Ecc</td>
<td style="text-align: center;">浮点型</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">预制墙中心线与网格线的偏心</td>
</tr>
<tr>
<td style="text-align: center;">GridCurve</td>
<td style="text-align: center;">二进制</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">预制墙网格线具体坐标<sup>注1</sup></td>
</tr>
</tbody>
</table>

注1：GridCurve 列表示预制墙网格线具体坐标。此列有数的话，将由N\*3个float数构成，N为网格线顶点个数。第i顶点坐标为( Cv\[i\*3\], Cv\[i\*3+1\]),第i段拱高为Cv\[i\*3+2\]。此列为空表示网格线为两点直线，用(X1,Y1,X2,Y2)即可确定网格线，不需额外附加具体坐标。

NOTE: 从 v4.x 版本开始, 所有预制构件均写入 dtlPcXXX.ydb 了， dtlRcWall.ydb 中的 装配式墙相关数据不再维护。

### 预制墙配筋组（tblRcPcWall）

|  字段名   | 字段类型 | 允许为空 | 主键 |    字段含义    |
|:---------:|:--------:|:--------:|:----:|:--------------:|
|    ID     |   整型   |    否    |  是  | 预制墙配筋组ID |
| ReinFlrID |   整型   |    否    |  否  |  所属钢筋层ID  |
|   Name    |   文本   |    否    |  否  |  预制墙组名称  |

NOTE: 从 v4.x 版本开始, 所有预制构件均写入 dtlPcXXX.ydb 了， dtlRcWall.ydb 中的 装配式墙相关数据不再维护。

### 墙身非贯通筋信息（tblRcBdSupBar）

记录墙身非贯通筋信息, 墙身非贯通筋分布在墙身上下边缘及竖向支座处, 主要用于有面外荷载的墙身, 如地下室外墙, 水池池壁等。

| 字段名  | 字段类型 | 允许为空 | 主键 |          字段含义           |
|:-------:|:--------:|:--------:|:----:|:---------------------------:|
|  Kind   |   整型   |    否    |  是  | 墙身非贯通筋的位置类型(注1) |
| BarSpec |   文本   |    是    |  否  |          钢筋规格           |
| LenExpr |   文本   |    是    |  否  |        预制墙组名称         |
