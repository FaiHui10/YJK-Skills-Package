> 来源：YJK 官方二次开发文档包 `数据库文件说明.rar` 内 `dtlCalc说明文档.docx`，由 pandoc 从 .docx 转换为 Markdown（纯文本，图片以标记代替）。

# DtlCalc数据库结构

DtlCalc.ydb数据库处理软件的计算模型、计算模型与建模模型的对应关系及计算结果。所谓计算模型是指程序进行有限元计算时使用的模型。计算模型是根据建模模型自动生成的，这个模型与建模模型的主要区别有：

1.  计算模型的构件只使用节点定位，没有网格、轴线等概念。计算模型中的节点ID全楼唯一，且记录X、Y、Z三维坐标。

2.  计算模型中的构件与建模模型中的构件没有一一对应关系，例如剪力墙计算时会拆成墙梁、墙柱两部分计算。可以根据各构件表中的MdlFlr和MdlNo字段在dtlModel.ydb数据库中找到计算模型构件对应的建模模型构件。其中MdlFlr字段是建模模型中的自然层编号，从1开始。MdlNo字段是构件在建模模型中的层内编号，在dtlModel.ydb数据库中查找对应表的\[No\_\]字段应该可以找到对应的构件。

3.  建模模型没有标准层和楼层组装概念，而是采用整楼模型，全部的节点和构件都是全楼唯一的。各构件都保存了层号\[FlrNo\]和塔号\[TowNo\]，这些层号和塔号是主要为了后期层指标统计准备的，实际应用时并不作为主要索引。通常\[FlrNo\]是与建模模型的自然层编号一致，但也有例外，例如底层底部节点的\[FlrNo\]就是为0的，另外跃层的柱子和斜杆保存的\[FlrNo\]也可能和\[MdlFlr\]不一致。

如无特殊说明，本数据库中的数据采用下列量纲：坐标、长度、尺寸等为mm；力、质量为kN；弯矩为kNm；钢筋面积为mm<sup>2</sup>。

为方便查看和调试，所有数组字段在存储时均格式化成用逗号或分号分割的字符串文本。

## 1、工程总体信息

### 1.1 工程参数表（tblProjectPara）

| 字段名  | 字段类型  | 字段含义 |
|:-------:|:---------:|:--------:|
|   ID    |   整型    |  工程ID  |
| ParaVal | VARIANT型 | 附加信息 |

此表一些工程整体的参数 不同ID代表不同参数，ID的可能数值有以下几个：

kppVersion = 1,//版本号，类型Int

kppNumFlr = 2, //计算模型分的楼层数

kppGenFlr = 3, //是否为广义层建模,类型或NULL

kppMultiTow = 4, //是否为多塔,类型或NULL

kppHasDsnResult = 5, //是否有设计结果,类型为或NULL

### 1.2 塔层表（tblTowFlr）

| 字段名 | 字段类型 | 字段含义 |
|:------:|:--------:|:--------:|
|   Id   |   整型   | 层、塔ID |
| TowNo  |   整型   |   塔号   |
| FlrNo  |   整型   |   层号   |

### 1.3节点表（tblJoint）

| 字段名 |  字段类型  |             字段含义             |
|:------:|:----------:|:--------------------------------:|
|   ID   |    整型    |              节点ID              |
| TowNo  |    整型    |           节点所在塔号           |
| FlrNo  |    整型    |         节点所在计算层号         |
| MdlFlr |   浮点型   |        节点所在的模型层号        |
| MdlNo  |   浮点型   |       节点对应的模型节点号       |
| Coord  | 文本(数组) | 节点坐标,float\[3\]的数组(X,Y,Z) |

## 2、构件信息数据表

### 2.1 梁基本信息表（tblBeamSeg）

| 字段名 | 字段类型 |     字段含义     |
|:------:|:--------:|:----------------:|
|   ID   |   整型   |       梁ID       |
| TowNo  |   整型   |    梁所在塔号    |
| FlrNo  |   整型   |  梁所在的计算层  |
| MdlFlr |   整型   |  梁所在的模型层  |
| MdlNo  |   整型   | 梁对应的模型梁号 |
|  Jt1   |   整型   |   节点1的ID号    |
|  Jt2   |   整型   |   节点2的ID号    |

### 2.2 柱基本信息表（tblColSeg）

| 字段名 | 字段类型 |     字段含义     |
|:------:|:--------:|:----------------:|
|   ID   |   整型   |       柱ID       |
| TowNo  |   整型   |    柱所在塔号    |
| FlrNo  |   整型   |  柱所在的计算层  |
| MdlFlr |   整型   |  柱所在的模型层  |
| MdlNo  |   整型   | 柱对应的模型编号 |
|  Jt1   |   整型   |   节点1的ID号    |
|  Jt2   |   整型   |   节点2的ID号    |

### 2.3 斜杆基本信息表（tblBraceSeg）

| 字段名 | 字段类型 |      字段含义      |
|:------:|:--------:|:------------------:|
|   ID   |   整型   |       斜杆ID       |
| TowNo  |   整型   |    斜杆所在塔号    |
| FlrNo  |   整型   |  斜杆所在的计算层  |
| MdlFlr |   整型   |  斜杆所在的模型层  |
| MdlNo  |   整型   | 斜杆对应的模型编号 |
|  Jt1   |   整型   |    节点1的ID号     |
|  Jt2   |   整型   |    节点2的ID号     |

### 2.4 墙梁基本信息表（tblWallBeam）

| 字段名 |  字段类型  |      字段含义      |
|:------:|:----------:|:------------------:|
|   ID   |    整型    |       墙梁ID       |
| TowNo  |    整型    |    墙梁所在塔号    |
| FlrNo  |    整型    |  墙梁所在的计算层  |
| MdlFlr |    整型    |  墙梁所在的模型层  |
| MdlNo  |    整型    | 墙梁对应的模型梁号 |
|   B    |   浮点型   |      墙梁宽度      |
|   H    |   浮点型   |      墙梁高度      |
|  Jt1   |    整型    |    节点1的ID号     |
|  Jt2   |    整型    |    节点2的ID号     |
|  Jts   | 文本(数组) | 墙梁经过的全部节点 |

墙梁指剪力墙洞口上下位置形成的梁。

处理起止节点JT1、JT2外，墙梁进行网格剖分时还会产生中间节点与其他构件相连。所有这些墙梁节点(包括JT1和JT2)组合成一个整形数组保存在\[Jts\]数组中，按从节点1到节点2的顺序排列

### 2.5 墙柱基本信息表（tblWallCol）

| 字段名 |  字段类型  |             字段含义             |
|:------:|:----------:|:--------------------------------:|
|   ID   |    整型    |              墙柱ID              |
| TowNo  |    整型    |           墙柱所在塔号           |
| FlrNo  |    整型    |         墙柱所在的计算层         |
| MdlFlr |    整型    |         墙柱所在的模型层         |
| MdlNos | 文本(数组) |    墙柱经过的所有建模模型墙号    |
| MdlPos | 文本(数组) | 墙柱经过的所有建模模型墙段的位置 |
|  JtLB  |    整型    |        墙柱左下角的节点ID        |
|  JtRB  |    整型    |        墙柱右下角的节点ID        |
|  JtRT  |    整型    |        墙柱右上角的节点ID        |
|  JtLT  |    整型    |        墙柱左上角的节点ID        |
|  JtsT  | 文本(数组) |      墙柱上皮经过的全部节点      |
|  JtsB  | 文本(数组) |      墙柱下皮经过的全部节点      |

墙柱指剪力墙中没有开洞的部分。计算模型中的一个墙柱指两个洞口间一片连续的墙身，而建模模型中的墙段是依据网格布置的，由于建模模型中的网格可能被节点打成多段， 因此一个墙柱可能包含多个墙段。

MdlNos是一个整形数的数组，按布置顺序保存此墙柱包含的所有墙段的编号。

MdlPos是一个整形数的数组，数组大小与MdlNos相同，值为墙身在每个建模墙段中的位置(0代表整段墙, 1是有洞口墙起始端墙身,2是有洞口墙终止端墙身)。

JtsT、JtsB字段的类型与含义与墙梁表中Jts字段类似，请参看墙梁表的说明。

## 3、配筋结果

下列表格保存各构件的计算配筋面积及设计内力等信息。

### 3.1 梁配筋表（tblRCBeamDsn）

| 字段名 |  字段类型  |             字段含义             |
|:------:|:----------:|:--------------------------------:|
|   ID   |    整型    |               梁ID               |
| AsTop  | 文本(数组) |           上部纵筋面积           |
| AsBtm  | 文本(数组) |           下部纵筋面积           |
|  Asv   | 文本(数组) |             箍筋面积             |
|  Ast1  | 文本(数组) |          抗扭单肢箍面积          |
|  Astt  | 文本(数组) |  剪扭纵筋面积，计算和构造的大值  |
| Asttc  | 文本(数组) | 计算剪扭纵筋面积，不考虑构造要求 |
| FrcAst | 文本(数组) |   上部纵筋对应的各截面设计内力   |
| FrcAsb | 文本(数组) |   下部纵筋对应的各截面设计内力   |
| FrcAsv | 文本(数组) |     箍筋对应的各截面设计内力     |

梁类构件会沿长度均分为9个截面，给出每个截面配筋面积、设计内力等设计结果。

As开头的字段数据类型均为float\[9\]，保存的每个截面的配筋面积。

Asv是纯剪计算配箍面积和剪扭计算配箍面积的大值，同时考虑箍筋最小配筋率的要求。抗扭单肢箍筋面积；Ast1是按纯扭计算得到的单支箍筋面积；Asv和Ast1给出给出的都是一个箍筋间距范围内的需要的配箍值，梁箍筋间距可由dtlModel.ydb的工程参数表中读到，缺省值为100mm。

FrcAst、FrcAsb、FrcAsv的数据类型均为float\[9\]\[6\],共54个浮点数。每9个数一组，表示9个截面，共有6组，表示6个内力分量，依序为X向弯矩Mx，Y向弯矩My，X向剪力Vx，Y向剪力Vy，轴力N，扭矩T。

### 3.2 次梁配筋表（tblRCSubBeamDsn）

| 字段名 |  字段类型  |           字段含义           |
|:------:|:----------:|:----------------------------:|
| MdlFlr |    整型    |           模型层号           |
| MdlNo  |    整型    |           模型梁号           |
| AsTop  | 文本(数组) |         上部纵筋面积         |
| AsBtm  | 文本(数组) |         下部纵筋面积         |
|  Asv   | 文本(数组) |           箍筋面积           |
|  Ast1  | 文本(数组) |        抗扭单肢箍面积        |
|  Astt  | 文本(数组) |         剪扭纵筋面积         |
| Asttc  | 文本(数组) |       计算剪扭纵筋面积       |
| FrcAst | 文本(数组) | 上部纵筋对应的各截面设计内力 |
| FrcAsb | 文本(数组) | 下部纵筋对应的各截面设计内力 |
| FrcAsv | 文本(数组) |   箍筋对应的各截面设计内力   |

次梁采用简支连续梁交叉梁系模型独立计算，不参与整体计算。计算模型中是没有次梁的，因此次梁采用建模模型中的梁号与序号进行索引。其他字段含义同表tblRCBeamDsn

### 3.3 柱配筋表（tblRCColDsn）

| 字段名 | 字段类型 | 字段含义 |
|:--:|:--:|:--:|
| ID | 整型 | 柱ID |
| AsDsnT | 文本(数组) | 顶截面配筋面积结果，计算与构造的大值 |
| AsDsnB | 文本(数组) | 底截面配筋面积结果，计算与构造的大值 |
| AsCalcT | 文本(数组) | 顶截面计算得到的配筋面积结果 |
| AsCalcB | 文本(数组) | 底截面计算得到的配筋面积结果 |
| AsBiAxialT | 文本(数组) | 顶截面双偏压纵筋配筋结果 |
| AsBiAxialB | 文本(数组) | 底截面双偏压纵筋配筋结果 |
| AsRatio | 文本(数组) | 配箍率限值相关 |
| ZYB | 文本(数组) | 轴力及轴压比相关 |
| AsJoint | 文本(数组) | 节点核心区配箍相关 |
| CombinedZYB | 浮点型 | 与周围墙肢进行组合构件设计时得到的重力荷载代表值下的轴压比 |

AsDsnT、AsDsnB、AsCalcT、AsCalcT的类型均为float\[5\]。5个数依序为角筋面积、X向纵筋面积、Y向纵筋面积、X向箍筋面积、Y向箍筋面积。箍筋面积为单位柱箍筋间距内所需要的配箍面积，柱箍筋间距可由dtlModel.ydb的工程参数表中读到，缺省值为100mm。

AsBiAxialT、 AsBiAxialB为设计软件选择的满足双偏压验算的实配纵筋结果。类型为float\[5\],5个数的含义依序为角筋直径、B边纵筋直径、B边纵筋根数、H边纵筋直径、H边纵筋根数。

AsRatio为设计软件依据柱属性和规范相关规定确定的配筋率限值。类型为float\[3\]。3个数的含义依序为纵筋最小全截面配箍率、纵筋最大全截面配箍率、箍筋最小体积配箍率。

ZYB记录与轴压比验算有关的信息，类型为float\[4\]。4个数依序为轴压比、轴压比限值、轴压比对应的轴力,重力荷载代表值下的轴力。重力荷载代表值下的轴力主要用于边框柱参与边缘构件设计时计算边缘构件的轴压比。

AsJoint记录与节点核心区箍筋设计有关的信息，类型为float\[5\]。5个数依序为节点核心区的体积配箍率、X向配箍面积、Y向配箍面积、X向计算配箍面积,Y向计算配箍面积。

### 3.4 斜杆配筋表（tblRCBraceDsn）

|   字段名   |  字段类型  |           字段含义           |
|:----------:|:----------:|:----------------------------:|
|     ID     |    整型    |            斜杆ID            |
|   AsDsnT   | 文本(数组) |      顶截面配筋面积结果      |
|   AsDsnB   | 文本(数组) |      底截面配筋面积结果      |
|  AsCalcT   | 文本(数组) | 顶截面计算得到的配筋面积结果 |
|  AsCalcB   | 文本(数组) | 底截面计算得到的配筋面积结果 |
| AsBiAxialT | 文本(数组) |   顶截面双偏压纵筋配筋结果   |
| AsBiAxialB | 文本(数组) |   底截面双偏压纵筋配筋结果   |
|  AsRatio   | 文本(数组) |        配箍率限值相关        |
|    ZYB     | 文本(数组) |       轴力及轴压比相关       |
|  AsJoint   | 文本(数组) |      节点核心区配箍相关      |

斜杆按柱进行设计，所以此表于柱配筋表tblRCColDsn基本一样。由于斜杆不与墙进行边缘构件组合设计，所以没有CombinedZYB字段。

### 3.4 墙梁配筋表（tblRCWallBeamDsn）

| 字段名  |  字段类型  |           字段含义           |
|:-------:|:----------:|:----------------------------:|
|   ID    |    整型    |            墙梁ID            |
|  AsTop  | 文本(数组) |         上部纵筋面积         |
|  AsBtm  | 文本(数组) |         下部纵筋面积         |
|   Asv   | 文本(数组) |           箍筋面积           |
| AsCross | 文本(数组) |    交叉斜筋或对角斜筋相关    |
| FrcAst  | 文本(数组) | 上部纵筋对应的各截面设计内力 |
| FrcAsb  | 文本(数组) | 下部纵筋对应的各截面设计内力 |
| FrcAsv  | 文本(数组) |   箍筋对应的各截面设计内力   |

墙梁的设计结果与普通梁类似，墙梁不考虑抗扭设计，因此没有与抗扭筋相关的配筋字段。其他字段如AsTop、AsBtm、Asv、FrcAst、FrcAsb、FrcAsv，其数据类型与数值含义均与梁配筋表（tblRCBeamDsn）中的同名字段一致。

墙梁配筋表中多出一个AsCross字段，其类型为float\[3\]。3个数依次为斜筋面积（计算和构造的大值）、斜筋计算面积、斜筋角度。

### 3.6 墙柱配筋表（tblRCWallColDsn）

| 字段名  |  字段类型  |      字段含义      |
|:-------:|:----------:|:------------------:|
|   ID    |    整型    |       墙柱ID       |
| AsTotal | 文本(数组) |    配筋面积结果    |
| AsRatio | 文本(数组) | 墙柱构造配筋率相关 |
|   ZYB   | 文本(数组) |  轴力及轴压比相关  |

AsTotal字段记录配筋面积结果，类型为float\[2\]\[7\]。每7个数一组，共分为2组，分别代表顶底截面。每个截面保存7个数，依次为：左端部的纵筋面积（计算与构造的大值），左端部的计算纵筋面积，右端部的纵筋面积（计算与构造的大值），右端部的计算纵筋面积，由双偏压计算得到的墙身竖向分布筋面积，抗剪水平筋的面积（计算与构造的大值），抗剪水平筋计算面积。

假定墙柱是两端对称配筋的单向偏心受压构件，计算得到的单侧配筋面积为AsTotal字段中记录的纵筋面积。

AsTotal字段记录的箍筋面积为一个水平筋间距范围内需要的箍筋面积。墙水平筋间距可以从dtlModel.ydb的工程参数表中读到。

AsRatio为设计软件依据墙柱属性和规范相关规定确定的配筋率限值。类型为float\[3\]。3个数的含义依序为纵筋全截面最小、最大配筋率以及水平分布筋最小配箍率。

ZYB记录与轴压比验算有关的信息，类型为float\[4\]。4个数依序为重力荷载代表值下的轴压比、轴压比限值、轴压比对应的轴力、组合轴压比。

## 4、相关参数信息

下列表保存各种实体的相关参数，表格的结构都是三个字段: \[ID\]记录实体ID，\[Kind\]为参数类型的枚举值，每张表中可能出现的枚举值所代表的含义参见各表说明。材料类型、材料等级、钢筋等级、抗震等级等参数值有统一的定义，说明如下：

材料类型是整形数，可能值有1(砌体),5(钢),6(钢筋混凝土),101(钢骨混凝土)。

材料等级是浮点型数，参数值的含义依据构件材料类型而定。钢构件为钢号，如Q235记录235；混凝土或砌体记录材料标号。例如C25混凝土记录25。

钢筋等级是整形数，可能值有81101（HPB235），81102（HPB300），81103（HRB335），

81104（HRB400），81105（HRB500），81106（CRB550），81107（HTRB600），81108（HTRB630），81109（CRB600H）; 81152（B400），81153（B500），81154（B600）; 81175（G40），81176（G60），81177（G75）。

抗震等级是整形数，可能值有70101（特一级抗震），70102（一级抗震），70103（二级抗震），70104（三级抗震），70105（四级抗震），70106（不抗震）

### 4.1 层塔相关参数表（tblTowFlrPara）

| 字段名  | 字段类型 |            字段含义            |
|:-------:|:--------:|:------------------------------:|
|   ID    |   整型   | 层塔ID,在tblTowFlr中应有对应值 |
|  Kind   |   整型   |            参数类型            |
| ParaVal | VARIANT  |             参数值             |

不同Kind代表不同参数，可能数值有以下几个：

kptfHeight = 1, //层塔高度,

kptfLevelB = 2, //层塔底部标高,

kptfJQC = 3, //是否为加强层

kptfGDC = 4, //是否为过渡层

kptfDBJQQ = 5, //是否为底部加强区

kptfAddM = 6, //层塔附加质量

kptfDeadM = 7, //层塔恒载质量总值

kptfLiveM = 8, //层塔活载质量总值

kptfWindLoad = 9, //层塔风荷载,float\[4\],分别为xWindx,xWindy,yWindx,yWindy

kptfUpTowFlr = 10, //与某个层塔顶部相连的所有其他层塔ID,32位整形数的数组

kptfDwTowFlr = 11, //与某个层塔底部相连的所有其他层塔ID, 32位整形数的数组

### 4.2 节点相关参数表（tblJointPara）

| 字段名  | 字段类型 |            字段含义            |
|:-------:|:--------:|:------------------------------:|
|   ID    |   整型   | 节点ID，在tblJoint中应有对应值 |
|  Kind   |   整型   |            参数类型            |
| ParaVal | VARIANT  |             参数值             |

不同Kind代表不同参数，可能数值有以下几个：

kpjFixed = 1, //是否为嵌固节点,值为1,非嵌固节点不记录

kpjDeadMass = 2, //恒载质量，类型double

kpjLiveMass = 3, //活载质量，类型double

### 4.3 梁相关参数表（tblBeamSegPara）

| 字段名  | 字段类型 | 字段含义 |
|:-------:|:--------:|:--------:|
|   ID    |   整型   |    ID    |
|  Kind   |   整型   | 参数类型 |
| ParaVal | VARIANT  |  参数值  |

不同Kind代表不同参数，可能数值有以下几个：

kpbmMatKind = 0, //材料类型

kpbmMatGrade = 1, //材料等级

kpbmMatGrade2 = 2,//钢骨混凝土时有效，记录钢骨的钢号

kpbmKZDJ = 3, //抗震等级

kpbmCover = 4, //保护层厚度

kpbmMBGrade = 5, //主筋等级，

kpbmHBGrade = 6, //箍筋等级,

kpbmRigidBar = 7, //是否为刚性杆,值为1或无记录

kpbmRest1 = 8, //1端约束类型,可能值为1(铰接)、2(滑动) 、3(半铰接) ,固接时不记录

kpbmRest2 = 9, //2端约束类型,可能值为1(铰接)、2(滑动) 、3(半铰接) ,固接时不记录

kpbmCenter = 10,//弧梁圆心点坐标类型float\[3\](X,Y,Z),直梁无此记录

kpbmCoefStiff = 11,//刚度调整系数,浮点数

kpbmCoefTiaoFu = 12,//调幅系数，浮点数

kpbmCoefTorsion = 13,//扭矩折减系数，浮点数

kpbmTiaoFu = 14,//是否为调幅梁,值为1或无记录

kpbmLianLiang = 15,//是否为连梁,值为1或无记录

kpbmZhuanHuan = 16,//是否为转换梁,值为1或无记录

kpbmMenGang = 17,//是否为门式钢架梁,值为1或无记录

kpbmHaoNeng = 18,//是否为耗能梁,值为1或无记录

kpbmCrossBar = 19,//墙梁(以梁段方式建模) 斜向交叉钢筋配筋方式, = 1交叉斜筋,= 2对角暗撑,=3为对角斜筋

kpbmPerformType = 20,// 按高规进行性能设计时的构件类型 1:关键 2:普通竖向 3:耗能

kpbmGZKZDJ =21, //抗震构造措施的抗震等级,其值参见SParaHeader.h中的抗震等级枚举

### 4.4 柱相关参数表（tblColSegPara）

| 字段名  | 字段类型 | 字段含义 |
|:-------:|:--------:|:--------:|
|   ID    |   整型   |    ID    |
|  Kind   |   整型   | 参数类型 |
| ParaVal | VARIANT  |  参数值  |

不同Kind代表不同参数，可能数值有以下几个：

kpclMatKind = 0, //材料类型

kpclMatGrade = 1, //材料等级

kpclMatGrade2 = 2,//钢骨混凝土时有效，记录钢骨的钢号,等于默认值时不记录

kpclKZDJ = 3, //抗震等级

kpclCover = 4, //保护层厚度,材料非混凝土或等于默认值时不记录

kpclMBGrade = 5, //主筋等级,非混凝土构件或等于默认值时不记录

kpclHBGrade = 6, //箍筋等级,非混凝土构件或等于默认值时不记录

kpclRigidBar = 7, //是否为刚性杆,值为1或无记录

kpclRest1 = 8, //1端约束类型, 1(铰接) ,固接时不记录

kpclRest2 = 9, //2端约束类型, 1(铰接) ,固接时不记录

kpclCalcLen =10, //计算长度相关,类型float\[4\],依次为x向长度系数,y向长度系数,x向实际长度,y向实际长度，长度系数乘以实际长度即为计算长度

kpclJiaoZhu =11, //是否为角柱

kpclKuangZhi =12, //是否为框支柱

kpclMenGang =13, //是否为门式钢架柱

kpclSPZH =14, //是否为水平转换桁架的竖杆

kpclBianKuang =15, //是否为边框柱

kpclSupBeam =16, //是否为梁上起柱

kpclZYBZJ =17, //轴压比限值增减量, 浮点数

kpclWithWall =18,//是否与周边墙一起进行组合构件配筋设计

kpclMatGrade3 =19,//叠合柱钢管内混凝土强度

kpclPerformType =20,// 按高规进行性能设计时的构件类型 1:关键 2:普通竖向 3:耗能

kpclGZKZDJ =21,//抗震构造措施的抗震等级,其值参见SParaHeader.h中的抗震等级枚举

### 4.5 斜杆相关参数表（tblBraceSegPara）

| 字段名  | 字段类型 | 字段含义 |
|:-------:|:--------:|:--------:|
|   ID    |   整型   |    ID    |
|  Kind   |   整型   | 参数类型 |
| ParaVal | VARIANT  |  参数值  |

不同Kind代表不同参数，可能数值有以下几个：

kpbrMatKind = 0 ,//材料类型

kpbrMatGrade = 1 ,//材料等级

kpbrMatGrade2 = 2 ,//钢骨混凝土时有效

kpbrKZDJ = 3 ,//抗震等级

kpbrCover = 4 ,//保护层厚度,材料非混凝土或等于默认值时不记录

kpbrMBGrade = 5 ,//主筋等级,非混凝土构件或等于默认值时不记录

kpbrHBGrade = 6 ,//箍筋等级,非混凝土构件或等于默认值时不记录

kpbrRigidBar = 7 ,//是否为刚性杆,值为或无记录

kpbrRest1 = 8 ,//1端约束类型,可能值为(铰接)、(滑动) =0(固接)时不记录

kpbrRest2 = 9 ,//1端约束类型,可能值为(铰接)、(滑动) =0(固接)时不记录

kpbrCalcLen =10 ,// 计算长度相关,类型float\[4\],依次为x向长度系数,y向长度系数,x向实际长度,y向实际长度，长度系数乘以实际长度即为计算长度

kpbrNormalType =11 ,//是否为单向斜撑(早期版本数据，已无效)

kpbrXType =12 ,//是否为交叉斜撑(早期版本数据，已无效)

kpbrYType =13 ,//是否为人字形斜撑(早期版本数据，已无效)

kpbrSPZH =14 ,//是否为水平转换桁架的斜杆

kpbrEJIAOZC =15 ,//特殊支撑,是否为角柱的斜杆

kpbrMatGrade3 =16 ,//叠合柱钢管内混凝土强度

kpbrPerformType =17 ,//按高规进行性能设计时的构件类型 1:关键 2:普通竖向 3:耗能

kpbrGZKZDJ =18 ,//抗震构造措施的抗震等级,其值参见SParaHeader.h中的抗震等级枚举

kpbrKuangZhi =19 ,//是否为转换柱

kpbrTENSE =20 ,//是否为单拉杆

kpbrCOMP =21 ,//是否为单压杆

### 4.6 墙梁相关参数表（tblWallBeamPara）

| 字段名  | 字段类型 | 字段含义 |
|:-------:|:--------:|:--------:|
|   ID    |   整型   |    ID    |
|  Kind   |   整型   | 参数类型 |
| ParaVal | VARIANT  |  参数值  |

不同Kind代表不同参数，可能数值有以下几个：

kpwbMatKind = 0 ,//材料类型

kpwbMatGrade = 1 ,//材料等级

kpwbMatGrade2 = 2 ,//钢骨混凝土时有效

kpwbKZDJ = 3 ,//抗震等级

kpwbCover = 4 ,//保护层厚度,材料非混凝土或等于默认值时不记录

kpwbMBGrade = 5 ,//主筋等级,非混凝土构件或等于默认值时不记录

kpwbHBGrade = 6 ,//箍筋等级,非混凝土构件或等于默认值时不记录

kpwbCenter =10 ,//弧形墙梁圆心点坐标类型float\[3\](X,Y,Z),直梁无记录

kpwbCoefStiff =11 , //墙梁刚度折减系数，等于默认值时不记录

kpwbGapSub =12 ,//分缝连梁主连梁会有此条记录,类型32位整形数的数组,数组大小为子连梁数,值为子连梁ID

kpwbGapMain =13 ,//分缝连梁子连梁会有此条记录,类型是整形数，值为主连梁ID

kpwbCrossBar =14 ,//斜向交叉钢筋配筋方式, = 1交叉斜筋,= 2对角暗撑,=3为对角斜筋

kpwbPerformType =15 ,//按高规进行性能设计时的构件类型 1:关键 2:普通竖向 3:耗能

kpwbGZKZDJ =16 ,//抗震构造措施的抗震等级,其值参见SParaHeader.h中的抗震等级枚举

kpwbStlBH =17, //连梁钢板厚度和高度(mm)，指定了连梁钢板的连梁会有此条记录,类型int数组,数组大小为2,值为钢板厚和高(mm)

### 4.7 墙柱相关参数表（tblWallColPara）

| 字段名  | 字段类型 | 允许为空 | 主键 | 字段含义 |
|:-------:|:--------:|:--------:|:----:|:--------:|
|   ID    |   整型   |    否    |  是  |    ID    |
|  Kind   |   整型   |    是    |  　  | 参数类型 |
| ParaVal | VARIANT  |    是    |  　  |  参数值  |

kpwcMatKind =0 ,//材料类型

kpwcMatGrade =1 ,//材料等级,

kpwcMatGrade2 =2 ,//钢骨混凝土时有效，记录钢骨的钢号,

kpwcKZDJ =3 ,//抗震等级

kpwcCover =4 ,//保护层厚度

kpwcMBGrade =5 ,//边缘构件纵筋等级,非混凝土构件或等于默认值时不记录

kpwcHBGrade =6 ,//水平分布筋等级,非混凝土构件或等于默认值时不记录

kpwcVBGrade =7 ,//竖向分布筋等级,非混凝土构件或等于默认值时不记录

kpwcWidth =8 ,//墙柱按长度加权的平均厚度,浮点数

kpwcLength =9 ,//墙柱长度,浮点数,计算时都是按这个取墙长的

kpwcCenter =10 ,//弧形墙柱圆心点坐标类型float\[3\](X,Y,Z),直梁无记录、

kpwcVertRou =11 ,//墙身竖向分布筋配筋率, 非混凝土墙或不等于默认值时不记录

kpwcBaseOut =12 ,//是否为地下室外墙

kpwcLinKong =13 ,//是否为临空墙

kpwcLinKongLoad =14 ,//临空墙荷载,单位是kN/m<sup>2</sup>

kpwcShortLeg =15 ,//是否为短肢墙

kpwcDesignAsCol =16 ,//是否按柱设计

kpwcEdgeHBGrade =17 ,//边缘构件箍筋等级, 非混凝土构件不记录

kpwcPerformType =18 ,//按高规进行性能设计时的构件类型 1:关键 2:普通竖向 3:耗能

kpwcGZKZDJ =19 ,//抗震构造措施的抗震等级,其值参见SParaHeader.h中的抗震等级枚举

kpwcHoriRou =20 ,//墙身水平分布筋配筋率, 等于默认值时不记录

## 5、标准工况内力

标准工况内力表共6张，每种构件均有一张表保存在标准工况下的内力。6张表与构件对应关系包括：tblBeamForce保存梁的标准内力，tblSubBeamForce保存次梁的标准内力，tblColForce保存柱的标准内力，tblBraceForce保存支撑(斜杆)的标准内力，tblWallBeamForce保存墙梁的标准内力，tblWallColForce保存墙的标准内力。

6张表的结构基本相同，都包含构件ID，工况号，内力值等字段。

tblSubBeamForce的构件ID由MdlFlr和MdlNo两个字段构成，表示次梁在建模模型中所在楼层及层内序号，其他表的ID字段即是构件在计算模型中的ID。

内力值字段Val是此构件在特定工况下的内力值。梁类构件（包括tblBeamForce、tblSubBeamForce、tblWallBeamForce）包含54个数，每9个数一组，表示9个截面，共有6组，表示6个内力分量，依序为X向弯矩Mx，Y向弯矩My，X向剪力Vx，Y向剪力Vy，轴力N，扭矩T。柱类构件（包括tblColForce、tblBraceForce、tblWallColForce）的内力包含12个数，分成两组，表示顶、底两个截面，每组6个数，表示截面上的6个内力分量，依序为X向弯矩Mx，Y向弯矩My，X向剪力Vx，Y向剪力Vy，轴力N，扭矩T。

工况号字段LoadCase表示此内力采用哪种工况，对应tblLoadCaseDef中的ID字段。表tblLoadCaseDef共包含4个字段，ID为工况的唯一标示号，Kind为工况的具体类型，Category为工况的分类，Name为工况的名称。各字段的说明详见下文。

表tblLoadCaseDef的Kind字段可能为下列值之一，各值的详细含义说明如下：

0 //未知类型或自定义工况

<span class="mark">1 //X水平地震</span>

<span class="mark">2 //X规定水平力</span>

<span class="mark">3 //X水平地震正偏5%</span>

<span class="mark">4 //X规定水平力正偏5%</span>

<span class="mark">5 //X水平地震负偏5%</span>

<span class="mark">6 //X规定水平力负偏5%</span>

<span class="mark">7 //X双向地震</span>

<span class="mark">8 //X最不利地震</span>

<span class="mark">9 //X水平地震反应位移正向</span>

<span class="mark">10 //X水平地震反应位移负向</span>

<span class="mark">11 //X水平地震多方向起始工况号，之后的为该数值加1</span>

<span class="mark">21 //Y水平地震</span>

<span class="mark">22 //Y规定水平力</span>

<span class="mark">23 //Y水平地震正偏5%</span>

<span class="mark">24 //Y规定水平力正偏5%</span>

<span class="mark">25 //Y水平地震负偏5%</span>

<span class="mark">26 //Y规定水平力负偏5%</span>

<span class="mark">27 //Y双向地震</span>

<span class="mark">28 //Y最不利地震</span>

<span class="mark">29 //Y水平地震反应位移正向</span>

<span class="mark">30 //Y水平地震反应位移负向</span>

<span class="mark">31 //Y水平地震多方向起始工况号，之后的为该数值加1</span>

<span class="mark">41 //X风载正吹</span>

<span class="mark">42 //X风载正吹横向</span>

<span class="mark">43 //X风载正吹扭转</span>

<span class="mark">44 //X风载反吹</span>

<span class="mark">45 //X风载反吹横向</span>

<span class="mark">46 //X风载反吹扭转</span>

<span class="mark">47 //X风载正吹正偏，美国规范用</span>

<span class="mark">48 //X风载正吹负偏，美国规范用</span>

<span class="mark">49 //X风载反吹正偏，美国规范用</span>

<span class="mark">50 //X风载反吹负偏，美国规范用</span>

<span class="mark">51 //Y风载正吹</span>

<span class="mark">52 //Y风载正吹横向</span>

<span class="mark">53 //Y风载正吹扭转</span>

<span class="mark">54 //Y风载反吹</span>

<span class="mark">55 //Y风载反吹横向</span>

<span class="mark">56 //Y风载反吹扭转</span>

<span class="mark">57 //Y风载正吹正偏，美国规范用</span>

<span class="mark">58 //Y风载正吹负偏，美国规范用</span>

<span class="mark">59 //Y风载反吹正偏，美国规范用</span>

<span class="mark">60 //Y风载反吹负偏，美国规范用</span>

<span class="mark">61 //X风载正吹双向，美国规范用</span>

<span class="mark">62 //X风载正吹双向正偏，美国规范用</span>

<span class="mark">63 //X风载正吹双向负偏，美国规范用</span>

<span class="mark">64 //X风载反吹双向，美国规范用，暂时没用，通过在正吹上加负号处理</span>

<span class="mark">65 //X风载反吹双向正偏，美国规范用，暂时没用，通过在正吹上加负号处理</span>

<span class="mark">66 //X风载反吹双向负偏，美国规范用，暂时没用，通过在正吹上加负号处理</span>

<span class="mark">67 //Y风载正吹双向，美国规范用</span>

<span class="mark">68 //Y风载正吹双向正偏，美国规范用</span>

<span class="mark">69 //Y风载正吹双向负偏，美国规范用</span>

<span class="mark">70 //Y风载反吹双向，美国规范用，暂时没用，通过在正吹上加负号处理</span>

<span class="mark">71 //Y风载反吹双向正偏，美国规范用，暂时没用，通过在正吹上加负号处理</span>

<span class="mark">72 //Y风载反吹双向负偏，美国规范用，暂时没用，通过在正吹上加负号处理</span>

<span class="mark">100 //恒载</span>

<span class="mark">101 //活载</span>

<span class="mark">102 //活荷载不利布置负弯矩包络</span>

<span class="mark">103 //活荷载不利布置正弯矩包络</span>

<span class="mark">104 //竖向地震</span>

<span class="mark">105 //人防</span>

<span class="mark">106 //温度</span>

<span class="mark">107 //温度，升温</span>

<span class="mark">108 //温度，降温</span>

<span class="mark">109 //土压力</span>

<span class="mark">110 //水压力</span>

<span class="mark">111 //预应力</span>

<span class="mark">120 //吊车</span>

<span class="mark">121 //吊车+刹车，梁-M、N</span>

<span class="mark">122 //吊车+刹车，梁-V、T</span>

<span class="mark">123 //吊车+刹车，梁+M、N</span>

<span class="mark">124 //吊车+刹车，梁+V、T</span>

<span class="mark">125 //吊车+刹车，柱Vxmax</span>

<span class="mark">126 //吊车+刹车，柱Vymax</span>

<span class="mark">127 //吊车+刹车，柱+Mxmax</span>

<span class="mark">128 //吊车+刹车，柱-Mxmax</span>

<span class="mark">129 //吊车+刹车，柱+Mymax</span>

<span class="mark">130 //吊车+刹车，柱-Mymax</span>

<span class="mark">131 //吊车+刹车，柱Nmax、+Mxmax</span>

<span class="mark">132 //吊车+刹车，柱Nmax、-Mxmax</span>

<span class="mark">133 //吊车+刹车，柱Nmax、+Mymax</span>

<span class="mark">134 //吊车+刹车，柱Nmax、-Mymax</span>

<span class="mark">135 //吊车+刹车，柱Nmin、+Mxmax</span>

<span class="mark">136 //吊车+刹车，柱Nmin、-Mxmax</span>

<span class="mark">137 //吊车+刹车，柱Nmin、+Mymax</span>

<span class="mark">138 //吊车+刹车，柱Nmin、-Mymax</span>

<span class="mark">141 //吊车，梁-M、N</span>

<span class="mark">142 //吊车，梁-V、T</span>

<span class="mark">143 //吊车，梁+M、N</span>

<span class="mark">144 //吊车，梁+V、T</span>

<span class="mark">145 //吊车，柱Vxmax</span>

<span class="mark">146 //吊车，柱Vymax</span>

<span class="mark">147 //吊车，柱+Mxmax</span>

<span class="mark">148 //吊车，柱-Mxmax</span>

<span class="mark">149 //吊车，柱+Mymax</span>

<span class="mark">150 //吊车，柱-Mymax</span>

<span class="mark">151 //吊车，柱Nmax、+Mxmax</span>

<span class="mark">152 //吊车，柱Nmax、-Mxmax</span>

<span class="mark">153 //吊车，柱Nmax、+Mymax</span>

<span class="mark">154 //吊车，柱Nmax、-Mymax</span>

<span class="mark">155 //吊车，柱Nmin、+Mxmax</span>

<span class="mark">156 //吊车，柱Nmin、-Mxmax</span>

<span class="mark">157 //吊车，柱Nmin、+Mymax</span>

<span class="mark">158 //吊车，柱Nmin、-Mymax</span>

<span class="mark">161 //多方向风起始工况号，顺风向，之后的为该数值加1</span>

<span class="mark">211 //多方向风起始工况号，横风向，之后的为该数值加1</span>

<span class="mark">261 //多方向风起始工况号，扭转风，之后的为该数值加1</span>

<span class="mark">311 //+X风载门刚-i</span>

<span class="mark">312 //+X风载门刚不平衡</span>

<span class="mark">313 //-X风载门刚-i</span>

<span class="mark">314 //-X风载门刚不平衡</span>

<span class="mark">315 //+Y风载门刚-i</span>

<span class="mark">316 //+Y风载门刚不平衡</span>

<span class="mark">317 //-Y风载门刚-i</span>

<span class="mark">318 //-Y风载门刚不平衡</span>

表tblLoadCaseDef的Category字段可能为下列值之一，各值的详细含义说明如下：

0 //未知的工况分类

<span class="mark">1 //恒载</span>

<span class="mark">2 //活载</span>

<span class="mark">3 //风载</span>

<span class="mark">4 //水平地震</span>

<span class="mark">5 //竖向地震</span>

<span class="mark">6 //人防</span>

<span class="mark">7 //吊车</span>

<span class="mark">8 //温度</span>

<span class="mark">9 //土</span>

<span class="mark">10 //水</span>

<span class="mark">21 //非线性组合-基本组合-非地震</span>

<span class="mark">22 //非线性组合-基本组合-水平地震</span>

<span class="mark">23 //非线性组合-基本组合-竖向地震</span>

<span class="mark">24 //非线性组合-基本组合-仅竖向地震</span>

<span class="mark">25 //非线性组合-基本组合-人防</span>

### 5.1 梁的标准内力表（tblBeamForce）

|  字段名  | 字段类型 | 字段含义 |
|:--------:|:--------:|:--------:|
|    ID    |   整型   |   梁ID   |
| LoadCase |   整型   |  工况号  |
|   Val    | VARIANT  |  参数值  |

### 5.2次梁的标准内力表（tblSubBeamForce）

|  字段名  | 字段类型 | 字段含义 |
|:--------:|:--------:|:--------:|
|  MdlFlr  |   整型   | 模型层号 |
|  MdlNo   |   整型   | 次梁编号 |
| LoadCase |   整型   |  工况号  |
|   Val    | VARIANT  |  参数值  |

### 5.3 柱的标准内力表（tblColForce）

|  字段名  | 字段类型 | 字段含义 |
|:--------:|:--------:|:--------:|
|    ID    |   整型   |   柱ID   |
| LoadCase |   整型   |  工况号  |
|   Val    | VARIANT  |  参数值  |

### 5.4支撑(斜杆)的标准内力表（tblBraceForce）

|  字段名  | 字段类型 |   字段含义   |
|:--------:|:--------:|:------------:|
|    ID    |   整型   | 支撑(斜杆)ID |
| LoadCase |   整型   |    工况号    |
|   Val    | VARIANT  |    参数值    |

### 5.5 墙梁的标准内力表（tblWallBeamForce）

|  字段名  | 字段类型 | 字段含义 |
|:--------:|:--------:|:--------:|
|    ID    |   整型   |  墙梁ID  |
| LoadCase |   整型   |  工况号  |
|   Val    | VARIANT  |  参数值  |

### 5.6 墙柱的标准内力表（tblWallColForce）

|  字段名  | 字段类型 | 字段含义 |
|:--------:|:--------:|:--------:|
|    ID    |   整型   |  墙柱ID  |
| LoadCase |   整型   |  工况号  |
|   Val    | VARIANT  |  参数值  |

### 5.7 工况信息表（tblLoadCaseDef）

|  字段名  | 字段类型 |   字段含义   |
|:--------:|:--------:|:------------:|
|    ID    |   整型   |    工况ID    |
|   Kind   |   整型   | 工况具体类型 |
| Category |   整型   |  工况的分类  |
|   Name   |  文本型  |  工况的名称  |

### 5.8 基本内力组合系数表（tblLoadCombine）

|  字段名  | 字段类型 |         字段含义          |
|:--------:|:--------:|:-------------------------:|
|    ID    |   整型   |          组合号           |
| CombKind |   整型   |        工组合类别         |
|    D     |  浮点型  |       恒载分项系数        |
|    L     |  浮点型  |       活载分项系数        |
|   WXP    |  浮点型  | X正方向水平风荷载分项系数 |
|   WXN    |  浮点型  | X负方向水平风荷载分项系数 |
|   WYP    |  浮点型  | Y正方向水平风荷载分项系数 |
|   WYN    |  浮点型  | Y负方向水平风荷载分项系数 |
|    EX    |  浮点型  |  X向水平地震荷载分项系数  |
|    EY    |  浮点型  |  Y向水平地震荷载分项系数  |
|    EZ    |  浮点型  |   竖向地震荷载分项系数    |
|    RF    |  浮点型  |     人防荷载分项系数      |
|   TEM    |  浮点型  |     温度荷载分项系数      |
|   CRN    |  浮点型  |     吊车荷载分项系数      |
