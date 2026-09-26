> 来源：YJK 官方二次开发文档包 `数据库文件说明.rar` 内 `砼梁施工图数据库dtlRcBeam说明.docx`，由 pandoc 从 .docx 转换为 Markdown（纯文本，图片以标记代替）。

#  dtlRcBeam.ydb数据结构

### 梁施工图数据中的基本概念

由建模里提供的梁段(BeamSeg)穿串形成连续梁(CntBeam)，连续梁(CntBeam)在节点处分跨形成梁跨(BeamSpan)。连续梁经一定原则归并后形成连续梁组(RcCB)，同时在每一跨上生成梁跨组(RcBeamSpan)。连续梁组(RcCB)是命名的基本单位，一个连续梁组一个名称，且彼此不同名。梁跨组(RcBeamSpan)是保存钢筋的基本单位，基本上梁的各种钢筋均以梁跨组的ID为索引(次梁附加筋除外)。梁施工图的分层是以钢筋层(ReinFloor)为基本单位的，如果几个自然层构件布置相同，设计结果相近，可以将其归并为同一钢筋层。同一钢筋层的构件只配一次钢筋。

### 工程参数（tblRcBeamPara）

| 字段名  | 字段类型 | 允许为空 | 主键 | 字段含义 |
|:-------:|:--------:|:--------:|:----:|:--------:|
|   ID    |   整型   |    否    |  是  |  参数ID  |
| ParaVal |   可变   |    是    |  否  |  参数值  |

目前该表只保存一个版本号（ID为65535,其值为按YYYYMMDD格式表示的日期，型如20120129），用于今后数据结构扩展时的版本控制。每次数据库定义格式发生变化时，版本号都会递增，具体版本历史沿革请参见附录A. 其他的施工图相关参数保存在工程目录下的DrawSet_Beam.CSV中，该文件为文本格式，每行一个参数，含义自明。

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

### 梁段网格信息（tblSegInfo）

|  字段名   | 字段类型 | 允许为空 | 主键 |           字段含义           |
|:---------:|:--------:|:--------:|:----:|:----------------------------:|
|  FloorID  |   整型   |    否    |  是  |   梁段或网格所在的自然层ID   |
|   SegID   |   整型   |    否    |  是  |        梁段或网格的ID        |
| CntBeamID |   整型   |    是    |  否  |   梁段或网格对应的连续梁ID   |
|  NoInCB   |   整型   |    是    |  否  |   在连续梁中的编号(0开始)    |
|  PosInCB  |   整型   |    是    |  否  | 在连续梁中对应的梁跨或支座号 |
| InfoGrid  |   整型   |    是    |  否  |  梁段或网格的一些属性(下详)  |
|  InfoJt1  |   整型   |    是    |  否  |   起节点处的一些属性(下详)   |
|  InfoJt2  |   整型   |    是    |  否  |   终节点处的一些属性(下详)   |

SegID可能为负值。读取后应需先取绝对值在使用。原因是同一网格可能位于两个连续梁的端支座中，这时需为同一网格记录两个记录。为了避免主键重复，其中一条记录的SegID为负值。

SegID就是模型中的梁段或网格ID，根据记录的构件类型的不同，可以在dtlModel.ydb的表tblGrid、 tblBeamSeg或tblSubBeam中找到构件的其他信息。由于同标准层可能划分到不同钢筋层，因此SegID必须与FloorID在一起才能作为主键唯一的确定一条记录。

CntBeamID可能为空，为空表示该梁段不参与穿连续梁（比如虚梁）。此时后面的字段如NoInCB、PosInCB、InfoGrid、InfoJt1、InfoJt2都没有意义。

NoInCB表示网格或梁段在连续梁内的编号。合法的值为从0到连续梁总网格数-1.

PosInCB表示网格或梁段在连续梁中对应的梁跨或支座号。大于0表示该梁段在连续梁的第PosInCB个梁跨中，小于0表示该网格或梁段在连续梁的第-PosInCB支座中。不论梁跨还是支座，均从1开始查。梁跨的端部叫做支座，所以一个连续梁的支座数始终为梁跨数加1.

InfoGrid是一个由各种二进制标记位构成的组合数。目前这个数中使用的标记位如下：

SegIsBeam = 0x0001, //记录的是梁段还是网格

InvertGrid = 0x0002, //网格方向与连续梁方向不一致

IsInSup = 0x0004, //此网格或梁段在某个支座内部

HasDownWall = 0x0010, //有梁下墙

HasUpWall = 0x0020, //有梁上墙

UpDownWallEqual = 0x0040, //梁从墙中间通过,上下墙是一个墙

OverlappedUpSeg = 0x0080, //梁段所在网格上方是否完全被墙或被柱覆盖

HasDownCol = 0x0100, //有梁下柱

HasUpCol = 0x0200, //有梁上柱

UpDownColEqual = 0x0400, //梁从柱中间通过,上下柱是一个柱

DownWallIgnored = 0x1000 //虽然有梁下墙,但该梁下墙在进行支座判断时被忽略

InfoGrid的最低位表示该记录的SegID是梁段还是网格。InfoGrid为偶数时，SegID代表一个网格ID，InfoGrid为奇数时，SegID代表一个梁段ID。至于是主梁(BeamSeg)还是次梁(SubBeam)，需要参考连续梁表(tblCntBeam)中的相关属性。

InfoJt1、InfoJt2同样是一个二进制标记位构成的组合数。各标记位含义如下：

HasDownCol = 0x00010000, //有梁下柱(斜杆也算)

HasUpCol = 0x00020000, //有梁上柱(斜杆也算)

UpDownColEqual = 0x00040000, //梁下柱和梁上柱是一个构件，就是说本连续梁从一个柱子中间穿过

DownColIsBrace = 0x00800000, //梁下柱是斜杆

UpColIsBrace = 0x08000000, //梁上柱是斜杆

HasPerpBeam = 0x00080000, //有面外梁

HasPerpDownWall = 0x00100000, //梁下有面外墙

HasPerpUpWall = 0x00200000, //梁上有面外墙

UpDownPerpWallEqual = 0x00400000, //梁下和梁上的面外墙是一个构件

HasPrevDownWall = 0x01000000, //梁下在连续梁的反向上有面内墙

HasPrevUpWall = 0x02000000, //梁上在连续梁的反向上有面内墙

UpDownPrevWallEqual = 0x04000000,

HasNextDownWall = 0x10000000, //梁下在连续梁的反向上有面内墙

HasNextUpWall = 0x20000000, //梁上在连续梁的反向上有面内墙

UpDownNextWallEqual = 0x40000000,

### 连续梁（tblCntBeam）

| 字段名  | 字段类型 | 允许为空 | 主键 |         字段含义         |
|:-------:|:--------:|:--------:|:----:|:------------------------:|
|   ID    |   整型   |    否    |  是  |         连续梁ID         |
| FloorID |   整型   |    否    |  否  |      所在自然层的ID      |
| Attrib  |   整型   |    否    |  否  | 连续梁属性类型，含义下详 |
| SpanNum |   整型   |    否    |  否  |         梁跨数量         |
| RcCBID  |   整型   |    否    |  否  |    连续梁所属梁组的ID    |

Attrib是一个由各种二进制标记位构成的组合数。标志位0x4000表示该连续梁全由建模时建的次梁组成。标志位0x2000表示该连续梁全由建模时生成的空心板肋梁组成。Attrib的低八位表示连续梁的类型，具体含义如下:

kbtFKL = 0x11, //kbtJZL 非框(架)梁.全部支座为梁

kbtFKZHL = 0x12, //kbtFL 非框(架)转换梁，托墙或托柱的非框架梁

kbtRibL = 0x14, //kbtRibL 密肋楼盖肋梁

kbtJZL = 0x15, //kbtJZL井字梁,

kbtXTL = 0x18, //kbtXTL 悬挑梁，一般用于单跨或双跨的悬挑连续梁

kbtZTL = 0x18, //kbtZTL,左挑梁，一般用于首跨挑出的梁跨

kbtYTL = 0x19, //kbtYTL,右挑梁，一般用于末跨跨挑出的梁跨

kbtKL = 0x20, //kbtKL，框梁，普通楼层框架梁

kbtWKL = 0x21, //kbtWKL，屋框梁，屋面层框架梁，

kbtKZL = 0x22, //框支梁. 转换层中托墙或托柱的梁

kbtTQL = 0x40, //kbtTQL,砼墙梁，特指混凝土剪力墙连梁.

kbtWTQL = 0x41, //kbtWTQL,屋面砼墙梁，屋面层的剪力墙连梁.

kbtTQFKL = 0x51, //kbtTFKL 砼(墙)非框梁，剪力墙连梁作为非框架梁对待

kbtTQJZL = 0x55, //kbtTJZL 砼(墙)井字梁, 剪力墙连梁作为井字梁对待

kbtTQKL = 0x60, //kbtTQKL,砼(墙)框梁，剪力墙连梁作为框架梁对待

kbtTQWKL = 0x61, //kbtTQKL,砼(墙)框梁，剪力墙连梁作为屋面框架梁对待

kbtZQL = 0x80, //kbtZQL,砖(墙)圈梁，程序中暂未使用

kbtZGL = 0x90, //kbtZGL,砖(墙)过梁，程序中暂未使用

kbtDKL = 0xA2, //kbtDKL底层框架梁，底框-砌体结构中的托砌体墙的梁或托柱的梁，该标志暂未使用，底框梁目前也按框支梁算，使用类型标记kbtKZL = 0x22

kbtTypeMask = 0xFF //梁跨类型的掩码

### 梁跨关系表(tblSpanRel)

| 字段名  | 字段类型 | 允许为空 | 主键 |           字段含义           |
|:-------:|:--------:|:--------:|:----:|:----------------------------:|
|  CBID   |   整型   |    否    |  是  |      梁跨所在的连续梁ID      |
| SpanNo  |   整型   |    否    |  是  |    梁跨在连续梁中是第几跨    |
| GridNoS |   整型   |    否    |  否  | 梁跨起始网格在连续梁中的编号 |
| GridNoE |   整型   |    否    |  否  | 梁跨终止网格在连续梁中的编号 |

该表于20140612 加入，方便第三方软件通过数据库直接查询梁跨与连续梁关系

### 连续梁组（tblRcCB）

|  字段名   | 字段类型 | 允许为空 | 主键 |      字段含义      |
|:---------:|:--------:|:--------:|:----:|:------------------:|
|    ID     |   整型   |    否    |  是  |     连续梁组ID     |
| ReinFlrID |   整型   |    否    |  否  | 梁组所在钢筋层的ID |
|   Name    |   文本   |    否    |  否  |   连续梁组的名称   |
|  SpanNum  |   整型   |    否    |  否  |      梁跨数量      |

### 梁跨组（tblRcSpan）

| 字段名 | 字段类型 | 允许为空 | 主键 |          字段含义           |
|:------:|:--------:|:--------:|:----:|:---------------------------:|
|   ID   |   整型   |    否    |  是  |          梁跨组ID           |
| RcCBID |   整型   |    否    |  否  |      所属连续梁组的ID       |
| SpanNo |   文本   |    否    |  否  | 是连续梁组的第几跨(从0开始) |

### 梁钢筋信息（tblSpanRein）

| 字段名  | 字段类型 | 允许为空 | 主键 |          字段含义          |
|:-------:|:--------:|:--------:|:----:|:--------------------------:|
| SpanID  |   整型   |    否    |  是  | 梁跨组ID,索引到表tblRcSpan |
|  Kind   |   整型   |    否    |  是  |     钢筋类型，含义下详     |
| ReinVal |   文本   |    否    |  否  |        钢筋的具体值        |

钢筋类型Kind可能出现的值列表如下：

kbmbTong = 0 , //通长负筋

kbmbLT = 1 , //左支座负筋,包含通长钢筋

kbmbRT = 2 , //右支座负筋,包含通长钢筋

kbmbJiaLi = 3 , //架立筋

kbmbB1 = 4 , //入支座梁下筋

kbmbB2 = 5 , //不入支座梁下筋

kbmbYao = 6 , //腰筋

kbmbFlange = 7 , //挑耳同通筋

kbmbHoop = 8 , //箍筋

kbmbYaoLa= 9 , //腰拉筋

kbmbFlangeLa = 10, //挑耳拉筋

kbmbSurfNet = 11 , //表层钢筋网片

kbmbLHV = 12 , //左腋筋

kbmbRHV = 13 , //右腋筋

ReinVal字段的文本格式符合平法图集的相关规定。只是钢筋等级改用英文字母A~F表示。钢筋等级具体对应关系为：

A: HPB300 新一级钢

B: HRB335 二级钢

C: HRB400 三级钢

D: HRB500 四级钢

E: CRB550 (冷轧带肋)

F: HPB235 (老一级钢)

G: CRB600H (冷轧带肋)

H: HTRB600

I: HTRB630

J: EUB400 欧标钢筋

K: EUB500 欧标钢筋

L: EUB600 欧标钢筋

P: USG40 美标钢筋, 参见ASTM-A615

Q: USG60 美标钢筋, 参见ASTM-A615

R: USG75 美标钢筋, 参见ASTM-A615

### 梁跨组的参数（tblSpanPara）

| 字段名  | 字段类型 | 允许为空 | 主键 |          字段含义          |
|:-------:|:--------:|:--------:|:----:|:--------------------------:|
| SpanID  |   整型   |    否    |  是  | 梁跨组ID,索引到表tblRcSpan |
|  Kind   |   整型   |    否    |  是  |          参数类型          |
| ParaVal |   可变   |    否    |  否  |        钢筋的具体值        |

本表用于存储配筋时一些杂项类型的参数，做接口程序时可以不管这个表。

### 次梁附加钢筋（tblSBRein）

| 字段名 | 字段类型 | 允许为空 | 主键 | 字段含义 |
|:--:|:--:|:--:|:--:|:--:|
| ID | 整型 | 否 | 是 | 附加筋ID,全楼唯一 |
| CntBeamID | 整型 | 否 | 是 | 附加筋所在连续梁,索引到表tblCntBeam |
| JointNo | 整形 | 否 | 否 | 定位节点在连续梁上的编号(从0始) |
| Dist | 浮点形 | 否 | 否 | 加筋中点与定位节点的距离，沿网格线度量，沿连续梁方向为正。 |
| AddHoop | 整形 | 是 | 否 | 次梁两侧附加箍筋的总套数，为空表示采用缺省值(目前为6)。附加箍筋的规格与梁箍筋同，间距固定为50. |
| Hanger | 文本 | 否 | 否 | 附加吊筋，空值表示没有吊筋 |

### 预制梁截面定义（tblPcSect）

| 字段名 | 字段类型 | 允许为空 | 主键 |             字段含义             |
|:------:|:--------:|:--------:|:----:|:--------------------------------:|
|   ID   |   整型   |    否    |  是  |         预制ID,全楼唯一          |
|   H    |  浮点型  |    是    |  否  | 预制梁预制部分的高度(含顶部键槽) |
|  TopH  |  浮点型  |    是    |  否  |       预制梁顶部键槽的深度       |
|  TopB  |  浮点型  |    是    |  否  | 定位节点在连续梁上的编号(从0始)  |

该表于20150508第一次加入。用于定义预制梁截面预制部分的信息。梁截面的宽度及整体高度由梁段的截面确定，无法独立修改，所以此处不保存。截面中保存的信息无法适应所布置的梁段时，盈建科软件可能调整相关尺寸以保证布置，自动调整尺寸失败的情况下，软件会取消预制梁的布置。预制梁截面定义（tblPcSect）

### 预制梁布置信息（tblPcBeam）

<table>
<colgroup>
<col style="width: 19%" />
<col style="width: 14%" />
<col style="width: 13%" />
<col style="width: 6%" />
<col style="width: 45%" />
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
<td style="text-align: center;">FloorID</td>
<td style="text-align: center;">整型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">预制梁所在的自然层ID</td>
</tr>
<tr>
<td style="text-align: center;">ID</td>
<td style="text-align: center;">整型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">预制梁ID,自然层内唯一</td>
</tr>
<tr>
<td style="text-align: center;">SectID</td>
<td style="text-align: center;">整型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">预制梁预制部分的截面ID,索引到表tblPcSect</td>
</tr>
<tr>
<td style="text-align: center;">CntBeamID</td>
<td style="text-align: center;">整型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">预制梁所在连续梁的ID, tblPcSect</td>
</tr>
<tr>
<td style="text-align: center;">PcBeamNo</td>
<td style="text-align: center;">整型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">预制梁在连续梁上的编号(从0始)</td>
</tr>
<tr>
<td style="text-align: center;">GridNoS</td>
<td style="text-align: center;">整型</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
<td rowspan="4" style="text-align: center;">GridNoS与GridNoE记录预制梁在连续梁上的起终网格序号，PosS和PosE记录起终位置</td>
</tr>
<tr>
<td style="text-align: center;">PosS</td>
<td style="text-align: center;">浮点型</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
</tr>
<tr>
<td style="text-align: center;">GridNoE</td>
<td style="text-align: center;">整型</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
</tr>
<tr>
<td style="text-align: center;">PosE</td>
<td style="text-align: center;">浮点型</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
</tr>
<tr>
<td style="text-align: center;">SGS</td>
<td style="text-align: center;">二进制</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
<td rowspan="2" style="text-align: center;">预制梁起止截面的抗剪键槽，参见下面的说明</td>
</tr>
<tr>
<td style="text-align: center;">SGE</td>
<td style="text-align: center;">二进制</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
</tr>
<tr>
<td style="text-align: center;">RcPcID</td>
<td style="text-align: center;">整形</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">预制梁配筋组的ID,索引到表tblRcPcBeam</td>
</tr>
<tr>
<td style="text-align: center;">Overlap2Sup</td>
<td style="text-align: center;">整形</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">预制梁与支座之间的距离</td>
</tr>
</tbody>
</table>

该表于20150508第一次加入, 20190327新增列Overlap2Sup。

SGS和SGE代表抗剪键槽，为8个short(16位整形数) 构成的结构体, 具体说明如下：

Struct mpcShearGroove {

short m_depth; //凹槽深度, 必须 \>= 0; = 0 下面的数都没意义了

short m_side; //槽口距布置区域侧边的距离, 横向贯通的槽口取为0;

short m_width; //槽口沿高度方向的宽度,必须 \>= 0；

short m_bottom; //第一个槽口底边与布置区域的距离

short m_top; //最后一个槽口底边与布置区域顶部的距离

short m_shrink; //槽底内缩尺寸, atan(m_shrink/m_depth) 为槽壁倾角

short m_count; //槽口数量,

short m_gap; //槽口数量\>1时表示槽口与槽口之间的距离 槽口数量 == 1 时等于槽口上沿到预制部上沿的距离

};

###  预制梁组信息（tblRcPcBeam）

|  字段名   | 字段类型 | 允许为空 | 主键 |          字段含义          |
|:---------:|:--------:|:--------:|:----:|:--------------------------:|
|    ID     |   整型   |    否    |  是  |         预制梁组ID         |
| ReinFlrID |   整型   |    否    |  否  |     梁组所在钢筋层的ID     |
|   Name    |   文本   |    否    |  否  |       预制梁组的名称       |
|  BarEdit  |  二进制  |    否    |  否  | 记录三维钢筋编辑及避让信息 |

该表于20150508第一次加入, 20180827新增列BarEdit。

###  钢筋长度信息（tblReinLen）

| 字段名 | 字段类型 | 允许为空 | 主键 | 字段含义 |
|:--:|:--:|:--:|:--:|:--:|
| ID | 整型 | 否 | 是 | 此条记录的ID全楼唯一 |
| SpanID | 整型 | 否 | 否 | 此条记录处理哪个梁跨组，关联到表tblRcSpan的ID |
| Kind | 整型 | 否 | 否 | 此条记录处理的是哪种长度 |
| ExprIndex | 整型 | 是 | 否 | 预定义表达式的编号,常用值-1表示与邻跨拉通 |
| ExprString | 字符串 | 否 | 否 | 用于计算钢筋长度的表达式 |
| LenValue | 浮点型 | 是 | 否 | 计算得到的长度具体数值 |

出于执行效率考虑，YJK软件通常只保存用户修改过的钢筋长度。优先保存表达式编号和表达式字符串。读取的时候处理优先级为首先根据表达式编号ExprIndex处理特殊情况，编号为空的解析表达式字符串ExprString求值，ExprString为空则读取LenValue中的具体值。

Kind值的含义如下

kbleEmpty = 0, //占位用, 无意义

kbleDefaultLa = 1, //直锚缺省长度

kbleDefaultBS = 2,//弯锚直段缺省长度

kbleDefaultBB = 3,//弯锚弯段缺省长度

kbleDefaultLap = 4,//搭接缺省长度

kbleKLTrunc1 = 5,//负筋截断位置

kbleKLTrunc2 = 6,//负筋截断位置（多于一排）

kbleKLLapJiaLi = 7,//架立筋搭接长度

kbleKLTruncBtm = 8,//不入支座底筋截断长度

kbleKLHoopLen = 9,//箍筋加密区长度

kbleLeftTopA = 10,//直锚长度(左支座负筋)

kbleLeftTopBS = 11,//弯锚直段长度(左支座负筋)

kbleLeftTopBB = 12,//弯锚弯段长度(左支座负筋)

kbleLeftBtmA = 13,//直锚长度(底筋左端)

kbleLeftBtmBS = 14,//弯锚直段长度(底筋左端)

kbleLeftBtmBB = 15,//弯锚弯段长度(底筋左端)

kbleLeftYaoA = 16,//直锚长度(腰筋)

kbleLeftYaoBS = 17,//弯锚直段长度(腰筋)

kbleLeftYaoBB = 18,//弯锚弯段长度(腰筋)

kbleRightTopA = 20,//直锚长度(右支座负筋)

kbleRightTopBS = 21,//弯锚直段长度(右支座负筋)

kbleRightTopBB = 22,//弯锚弯段长度(右支座负筋)

kbleRightBtmA = 23,//直锚长度(底筋右端)

kbleRightBtmBS = 24,//弯锚直段长度(底筋右端)

kbleRightBtmBB = 25,//弯锚弯段长度(底筋右端)

kbleRightYaoA = 26,//直锚长度(腰筋右端)

kbleRightYaoBS = 27,//弯锚直段长度(腰筋右端)

kbleRightYaoBB = 28,//弯锚弯段长度(腰筋右端)

### 附录A. dtlRcBeam.ydb数据库定义的版本沿革

**20190411**

新增表格tblReinLen，方便造价及建造方向的应用

**20190327**

表格tblReinLen，方便造价及建造方向的应用

**20140612**

新增表格tblSpanRel，方便第三方软件通过数据库直接查询梁跨与连续梁关系
