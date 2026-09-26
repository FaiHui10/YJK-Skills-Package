> 来源：YJK 官方二次开发文档包 `数据库文件说明.rar` 内 `dtlModel.docx`，由 pandoc 从 .docx 转换为 Markdown（纯文本，图片以标记代替）。

# dtlModel数据结构

## 1、定位信息数据表

### 1.1 标准层（tblStdFlr）

| 字段名 | 字段类型 | 允许为空 | 主键 |                字段含义                |
|:------:|:--------:|:--------:|:----:|:--------------------------------------:|
|   ID   |   整型   |    否    |  是  |                标准层ID                |
|  No\_  |   整型   |    否    |  是  |                标准层号                |
| Height |   整型   |    否    |  否  |               标准层层高               |
|  Dead  |  浮点型  |    否    |      |                楼面恒载                |
|  Live  |  浮点型  |    否    |      |                楼面活载                |
| DPara  |   整型   |    否    |      |                                        |
|  Para  |   整型   |    否    |      | 标准层参数（见附录4.1 tblStdFlrPara ） |

### 1.2 标准层参数（tblStdFlrPara）

|  字段名  | 字段类型 | 允许为空 | 主键 |        字段含义         |
|:--------:|:--------:|:--------:|:----:|:-----------------------:|
| StdFlrID |   整型   |    否    |  是  |        标准层ID         |
|   Kind   |   整型   |    否    |  是  |        类型编号         |
| ParaVal  | 可变类型 |    否    |      | 标准层参数（见附录4.1） |

### 1.3 自然层（tblFloor）

|  字段名  | 字段类型 | 允许为空 | 主键 |       字段含义       |
|:--------:|:--------:|:--------:|:----:|:--------------------:|
|    ID    |   整型   |    否    |  是  |       自然层ID       |
|   No\_   |   整型   |    否    |  　  |      自然层编号      |
|   Name   |   文本   |    是    |  　  |      自然层名称      |
| StdFlrID |   整型   |    否    |  　  | 自然层对应的标准层ID |
|  LevelB  |  浮点型  |    否    |  　  |    自然层的底标高    |

### 1.4 轴线（tblAxis）

| 字段名 | 字段类型 | 允许为空 | 主键 | 字段含义 |
|:--:|:--:|:--:|:--:|:--:|
| ID | 整型 | 否 | 是 | 轴线ID |
| No\_ | 整型 | 否 | 　 | 轴线编号 |
| StdFlrID | 整型 | 否 | 　 | 轴线所在的标准层ID |
| Jt1ID | 整型 | 否 | 　 | 轴线对应的第一个节点ID 如果小于0，表示圆弧的圆心 |
| Jt2ID | 整型 | 否 | 　 | 轴线对应的第二个节点ID，如是圆弧轴线，则表示圆弧轴线上的一点 |
| Name | 文本 | 是 | 　 | 轴线名 |

### 1.5网格（tblGrid）

|  字段名  | 字段类型 | 允许为空 | 主键 |      字段含义      |
|:--------:|:--------:|:--------:|:----:|:------------------:|
|    ID    |   整型   |    否    |  是  |       网格ID       |
|   No\_   |   整型   |    否    |  　  |      网格编号      |
| StdFlrID |   整型   |    否    |  　  | 网格所在的标准层ID |
|  Jt1ID   |   整型   |    否    |  　  | 网格的第一个节点ID |
|  Jt2ID   |   整型   |    否    |  　  | 网格的第二个节点ID |
|  AxisID  |   整型   |    是    |  　  |  网格所在的轴线ID  |

### 1.6节点（tblJoint）

|  字段名  | 字段类型 | 允许为空 | 主键 |     字段含义     |
|:--------:|:--------:|:--------:|:----:|:----------------:|
|    ID    |   整型   |    否    |  是  |      节点ID      |
|   No\_   |   整型   |    否    |  　  |     节点编号     |
| StdFlrID |   整型   |    否    |  　  | 节点所在标准层ID |
|    X     |  浮点型  |    否    |  　  |   节点的X坐标    |
|    Y     |  浮点型  |    否    |  　  |   节点的Y坐标    |
|  HDiff   |   整型   |    是    |  　  |     上节点高     |

## 2、构件信息数据表

偏心符号：

直线：遵循右手螺旋法则，大拇指向为起点到终点（垂直（x相差小于50）时从上到下，其它从左到右），出屏幕方向为正

圆弧：沿半径方向，远离圆心为正，靠近为负

定位距离（墙洞、悬挑板）： 0居中布置 \>0左边线距离起点的距离 \<0右边线距离终点的距离

柱、板洞的偏心：局部坐标系下的偏心，如下示意

<img src="media/image1.png" style="width:3.25486in;height:2.98125in" alt="010_柱转角2" />

### 2.1 墙类型定义（tblWallSect）

| 字段名 | 字段类型 | 允许为空 | 主键 |             字段含义              |
|:------:|:--------:|:--------:|:----:|:---------------------------------:|
|   ID   |   整型   |    否    |  是  |             墙截面ID              |
|  No\_  |   整型   |    否    |  　  |            墙截面编号             |
|  Mat   |   整型   |    否    |  　  |        墙材质（见附录4.2）        |
|  Kind  |   整型   |    否    |  　  | 墙截面类型（见附录4.3）墙只有矩形 |
|   B    |   整型   |    否    |  　  |               墙厚                |

### 2.2墙布置信息定义（tblWallSeg）

|  字段名  | 字段类型 | 允许为空 | 主键 |           字段含义           |
|:--------:|:--------:|:--------:|:----:|:----------------------------:|
|    ID    |   整型   |    否    |  是  |             墙ID             |
|   No\_   |   整型   |    否    |  　  |            墙编号            |
| StdFlrID |   整型   |    否    |  　  |        墙所在标准层ID        |
|  SectID  |   整型   |    否    |      |           墙类型ID           |
|  GridID  |   整型   |    否    |  　  |         墙所在网格ID         |
|   Ecc    |   整型   |    是    |  　  |      墙的偏轴距离（mm）      |
|  HDiff1  |   整型   |    是    |  　  |        墙顶高1（mm）         |
|  HDiff2  |   整型   |    是    |  　  |        墙顶高2（mm）         |
|  HDiffB  |   整型   |    是    |  　  |         墙底高（mm）         |
|  WallJY  |   文本   |    是    |      | 墙加腋截面尺寸（见附录4.10） |

### 2.3 墙洞类型定义（tblWallHoleDef）

| 字段名  | 字段类型 | 允许为空 | 主键 |         字段含义          |
|:-------:|:--------:|:--------:|:----:|:-------------------------:|
|   ID    |   整型   |    否    |  是  |        墙洞类型ID         |
|  No\_   |   整型   |    否    |  　  |       墙洞类型编号        |
|    B    |   整型   |    否    |  　  |    矩形洞口宽度（mm）     |
|    H    |   整型   |    否    |  　  |     矩形洞口高度(mm)      |
|    K    |   整型   |    否    |      | 墙洞截面类型（见附录4.5） |
| Special |   文本   |    否    |      |   三心圆、半圆截面尺寸    |

### 2.4 墙洞布置信息定义（tblWallHole）

|  字段名  | 字段类型 | 允许为空 | 主键 |            字段含义             |
|:--------:|:--------:|:--------:|:----:|:-------------------------------:|
|    ID    |   整型   |    否    |  是  |             墙洞ID              |
|   No\_   |   整型   |    否    |  　  |            墙洞编号             |
| StdFlrID |   整型   |    否    |  　  |      墙洞所在的标准层编号       |
|  SectID  |   整型   |    否    |  　  |           墙洞类型ID            |
|  GridID  |   整型   |    否    |  　  |        墙洞所在的网格ID         |
|   Ecc    |   整型   |    否    |  　  | 洞口定位距离（mm）（见附录4.4） |
|  HDiff   |   整型   |    否    |  　  |       洞口底部标高（mm）        |

### 2.5 梁类型定义（tblBeamSect）

|  字段名  | 字段类型 | 允许为空 | 主键 |        字段含义         |
|:--------:|:--------:|:--------:|:----:|:-----------------------:|
|    ID    |   整型   |    否    |  是  |        梁类型ID         |
|   No\_   |   整型   |    否    |  　  |       梁类型编号        |
|   Name   |   文本   |    是    |  　  |       梁类型名称        |
|   Mat    |   整型   |    否    |  　  | 梁类型材质（见附录4.2） |
|   Kind   |   整型   |    否    |  　  | 梁截面类型（见附录4.3） |
| ShapeVal |   文本   |    是    |  　  | 梁截面尺寸（见附录4.5） |

### 2.6 梁布置信息定义（tblBeamSeg）

|  字段名  | 字段类型 | 允许为空 | 主键 |    字段含义    |
|:--------:|:--------:|:--------:|:----:|:--------------:|
|    ID    |   整型   |    否    |  是  |      梁ID      |
|   No\_   |   整型   |    否    |  　  |     梁编号     |
| StdFlrID |   整型   |    否    |  　  | 梁所在的标准层 |
|  SectID  |   整型   |    否    |  　  |    梁类型ID    |
|  GridID  |   整型   |    否    |  　  |  梁所在网格ID  |
|   Ecc    |   整型   |    是    |  　  |   梁偏轴距离   |
|  HDiff1  |   整型   |    是    |  　  |   梁顶标高1    |
|  HDiff2  |   整型   |    是    |  　  |   梁顶标高2    |
| Rotation |  浮点数  |    是    |      |      转角      |
|  JYDef   |   文本   |    是    |      | 梁加腋布置位置 |

### 2.7次梁定义（tblSubBeam）

|  字段名  | 字段类型 | 允许为空 | 主键 |       字段含义       |
|:--------:|:--------:|:--------:|:----:|:--------------------:|
|    ID    |   整型   |    否    |  是  |        次梁ID        |
|   No\_   |   整型   |    否    |  　  |       次梁编号       |
| StdFlrID |   整型   |    否    |  　  |   次梁所在的标准层   |
|  SectID  |   整型   |    否    |  　  |    次梁截面类型ID    |
|    X1    |  浮点型  |    否    |  　  |    次梁起点的X值     |
|    Y1    |  浮点型  |    否    |  　  |    次梁起点的Y值     |
|    Z1    |  浮点型  |    是    |  　  |    次梁起点的Z值     |
|    X2    |  浮点型  |    否    |  　  |    次梁终点的X值     |
|    Y2    |  浮点型  |    否    |  　  |    次梁终点的Y值     |
|    Z2    |  浮点型  |    是    |  　  |    次梁终点的Z值     |
| Gird1ID  |   整型   |    是    |  　  | 次梁起点搭接的网格ID |
| Gird2ID  |   整型   |    是    |  　  | 次梁终点搭接的网格ID |

### 2.8板信息定义（tblSlab）

|    字段名    | 字段类型 | 允许为空 | 主键 |            字段含义             |
|:------------:|:--------:|:--------:|:----:|:-------------------------------:|
|      ID      |   整型   |    否    |  是  |             楼板ID              |
|     No\_     |   整型   |    否    |  　  |            楼板编号             |
|   StdFlrID   |   整型   |    否    |  　  |        楼板所在的标准层         |
|   GridsID    |   文本   |    否    |  　  |       楼板轮廓线的网格ID        |
|   VertexX    |   文本   |    否    |  　  |        楼板轮廓点的X坐标        |
|   VertexY    |   文本   |    否    |  　  |        楼板轮廓点的Y坐标        |
|   VertexZ    |   文本   |    否    |  　  |        楼板轮廓点的Z坐标        |
|  RoomIsHole  |   整型   |    是    |  　  | 是否为全房间洞（空为否，1为是） |
|  Thickness   |   整型   |    是    |  　  |  楼板厚度,9999表示同标准层参数  |
|      cc      |   整型   |    是    |  　  |              错层               |
|     dead     |  浮点型  |    是    |  　  |   恒载，9999表示同工程默认值    |
|     live     |  浮点型  |    是    |  　  |   活载，9999表示同工程默认值    |
|   TransWay   |   整型   |    是    |      |            导荷方式             |
|     Ang1     |  浮点型  |    是    |      |             塑性角1             |
|     Ang2     |  浮点型  |    是    |      |             塑性角2             |
| nEdgeSupport |   整型   |    是    |      |        房间非受力边边数         |
| EdgeSupport  |   文本   |    是    |      |           非受力边id            |
|    Shape     |   整型   |    是    |      |  房间形状 1为矩形，其他形状为0  |
|      xc      |  浮点型  |    是    |      |            房间形心x            |
|      Yc      |  浮点型  |    是    |      |            房间形心y            |

### 2.9板洞类型定义（tblSlabHoleDef）

|  字段名  | 字段类型 | 允许为空 | 主键 |          字段含义           |
|:--------:|:--------:|:--------:|:----:|:---------------------------:|
|    ID    |   整型   |    否    |  是  |         板洞类型ID          |
|   No\_   |   整型   |    否    |  　  |        板洞类型编号         |
|   Kind   |   整型   |    否    |  　  |    板洞形状（见附录4.3）    |
| ShapeVal |   文本   |    否    |  　  | 板洞轮廓线尺寸（见附录4.5） |

### 2.10板洞布置信息定义（tblSlabHole）

|  字段名  | 字段类型 | 允许为空 | 主键 |       字段含义       |
|:--------:|:--------:|:--------:|:----:|:--------------------:|
|    ID    |   整型   |    否    |  是  |        板洞ID        |
|   No\_   |   整型   |    否    |  　  |       板洞编号       |
| StdFlrID |   整型   |    否    |  　  |    板洞所在标准层    |
|  SectID  |   整型   |    否    |  　  |     板洞的类型ID     |
|   JtID   |   整型   |    否    |  　  |   板洞的形心节点ID   |
|  SlabID  |   整型   |    否    |  　  |    板洞的宿主板ID    |
|   EccX   |   整型   |    否    |  　  | 板洞的沿轴偏心（mm） |
|   EccY   |   整型   |    否    |  　  | 板洞的偏轴偏心（mm） |
| Rotation |  浮点型  |    否    |  　  |  板洞的轴转角（度）  |

### 2.11悬挑板类型定义（tblCantiSlabDef）

| 字段名 | 字段类型 | 允许为空 | 主键 |              字段含义               |
|:------:|:--------:|:--------:|:----:|:-----------------------------------:|
|   ID   |   整型   |    否    |  是  |            悬挑板类型ID             |
|  No\_  |   整型   |    否    |  　  |           悬挑板类型编号            |
|  Kind  |   整型   |    否    |  　  | 悬挑板的截面类型（目前只支持矩形1） |
| Length |   整型   |    否    |  　  |   悬挑板宽度（0为同网格长）（mm）   |
| Width  |   整型   |    否    |  　  |        悬挑板外挑长度（mm）         |
| Thick  |   整型   |    否    |  　  |    板厚（0为与相邻板厚相同）(mm)    |

### 2.12悬挑板布置信息定义（tblCantiSlab）

|  字段名  | 字段类型 | 允许为空 | 主键 |      字段含义      |
|:--------:|:--------:|:--------:|:----:|:------------------:|
|    ID    |   整型   |    否    |  是  |      悬挑板ID      |
|   No\_   |   整型   |    否    |  　  |     悬挑板编号     |
| StdFlrID |   整型   |    否    |  　  | 悬挑板所在的标准层 |
|  SectID  |   整型   |    否    |  　  |   悬挑板的类型ID   |
|  GridID  |   整型   |    否    |  　  |  挑板所在的网格ID  |
|    ez    |   整型   |    否    |  　  |   距楼板的距离　   |
|    ec    |   整型   |    否    |  　  |      水平偏移      |
|    dr    |   整型   |    否    |  　  |      布置方向      |

### 2.13柱类型定义（tblColSect）

|  字段名  | 字段类型 | 允许为空 | 主键 |        字段含义         |
|:--------:|:--------:|:--------:|:----:|:-----------------------:|
|    ID    |   整型   |    否    |  是  |        柱类型ID         |
|   No\_   |   整型   |    否    |  　  |       柱类型编号        |
|   Name   |   文本   |    是    |  　  |       柱类型名称        |
|   Mat    |   整型   |    否    |  　  | 柱类型材质（见附录4.2） |
|   Kind   |   整型   |    否    |  　  | 柱截面类型（见附录4.3） |
| ShapeVal |   文本   |    否    |  　  | 柱截面尺寸（见附录4.5） |

### 2.14柱布置信息定义（tblColSeg）

|  字段名  | 字段类型 | 允许为空 | 主键 |    字段含义    |
|:--------:|:--------:|:--------:|:----:|:--------------:|
|    ID    |   整型   |    否    |  是  |      柱ID      |
|   No\_   |   整型   |    否    |  　  |     柱编号     |
| StdFlrID |   整型   |    否    |  　  | 柱所在标准层ID |
|  SectID  |   整型   |    否    |  　  |    柱类型ID    |
|   JtID   |   整型   |    否    |  　  |  柱定位节点ID  |
|   EccX   |   整型   |    是    |  　  |  柱的沿轴偏心  |
|   EccY   |   整型   |    是    |  　  |  柱的偏轴偏心  |
| Rotation |  浮点数  |    是    |  　  |     柱转角     |
|  HDiffB  |   整型   |    是    |  　  |    柱底标高    |
| ColcapId |   整型   |    否    |      |     柱帽ID     |

### 2.15斜杆类型定义（tblBraceSect）

|  字段名  | 字段类型 | 允许为空 | 主键 |         字段含义          |
|:--------:|:--------:|:--------:|:----:|:-------------------------:|
|    ID    |   整型   |    否    |  是  |        斜杆类型ID         |
|   No\_   |   整型   |    否    |  　  |       斜杆类型编号        |
|   Name   |   文本   |    是    |  　  |       斜杆类型名称        |
|   Mat    |   整型   |    否    |  　  | 斜杆类型材质（见附录4.2） |
|   Kind   |   整型   |    否    |  　  | 斜杆截面类型（见附录4.3） |
| ShapeVal |   文本   |    否    |  　  | 斜杆截面尺寸（见附录4.5） |

### 2.16斜杆布置信息定义（tblBraceSeg）

|  字段名  | 字段类型 | 允许为空 | 主键 |               字段含义               |
|:--------:|:--------:|:--------:|:----:|:------------------------------------:|
|    ID    |   整型   |    否    |  是  |                斜杆ID                |
|   No\_   |   整型   |    否    |  　  |               斜杆编号               |
| StdFlrID |   整型   |    否    |  　  |           斜杆所在标准层ID           |
|  SectID  |   整型   |    否    |  　  |              斜杆类型ID              |
|  Jt1ID   |   整型   |    否    |  　  |           斜杆1端的节点ID            |
|  Jt2ID   |   整型   |    否    |  　  |           斜杆2端的节点ID            |
|  EccX1   |   整型   |    是    |  　  |          斜杆1端的沿轴偏心           |
|  EccY1   |   整型   |    是    |  　  |          斜杆1端的偏轴偏心           |
|  HDiff1  |   整型   |    是    |  　  | 斜杆1端的底标高（为1时表示与层同高） |
|  EccX2   |   整型   |    是    |  　  |          斜杆2端的沿轴偏心           |
|  EccY2   |   整型   |    是    |  　  |          斜杆2端的偏轴偏心           |
|  HDiff2  |   整型   |    是    |  　  | 斜杆2端的底标高（为1时表示与层同高） |
| Rotation |  浮点数  |    是    |  　  |            斜杆2端的转角             |

### 2.17荷载类型定义（tblLoadSect）

|   字段名    | 字段类型 | 允许为空 | 主键 |          字段含义           |
|:-----------:|:--------:|:--------:|:----:|:---------------------------:|
|     ID      |   整型   |    否    |  是  |           类型ID            |
|    No\_     |   整型   |    否    |  　  |          类型编号           |
| ElementKind |   整型   |    否    |  　  |     荷载对应的构件类型      |
|  ShapeVal   |   文本   |    否    |  　  | 荷载定义（6个连续的浮点数） |

### 2.18荷载布置信息定义（tblLoadSeg）

|   字段名    | 字段类型 | 允许为空 | 主键 |       字段含义        |
|:-----------:|:--------:|:--------:|:----:|:---------------------:|
|     ID      |   整型   |    否    |  是  |        荷载ID         |
|    No\_     |   整型   |    否    |  　  |       荷载编号        |
|   SectID    |   整型   |    否    |  　  |      荷载类型ID       |
|   Type\_    |   整型   |    否    |  　  | 荷载工况（见附录4.7） |
| ElementID\_ |   整型   |    否    |  　  |     对应构件的id      |

### 2.19构件关联的属性信息（tblProperty）

| 字段名  | 字段类型 | 允许为空 | 主键 |           字段含义           |
|:-------:|:--------:|:--------:|:----:|:----------------------------:|
|   ID    |   整型   |    否    |      |            构件ID            |
|  Name   |   文本   |    否    |  　  |           属性名称           |
|  Type   |   整型   |    否    |  　  | 属性类型(3整型 4浮点 27数组) |
| Value\_ |   文本   |    否    |  　  |            属性值            |

**注：**

1、同层之间的构件编号按构件顺序排列，且唯一。不同层之间的构件编号可以重复。构件的ID号为全局编号，模型中的构件的ID号具有唯一性。

2、构件的偏轴距离按照局部坐标系下正向为正值，负向为负值。

3、构件的HDiff1为构件定位线的起点，HDiff2为定位线的终点。起点和终点的确定规则为：水平构件左为起点，右为终点。垂直构件下为起点，上为终点。

4、次梁截面同主梁截面。

5、板洞的类型只有矩形、圆形、正多边形三种。

### 2.20楼梯定义表（tblStairDef）

| 字段名 | 字段类型 | 允许为空 | 主键 | 字段含义 |
|:--:|:--:|:--:|:--:|:--:|
| ID | 整型 | 否 | 是 | 楼梯定义的ID |
| No\_ | 整形 | 否 | 　 | 楼梯定义序号 |
| Col2 | 整形 | 是 |  | 楼梯类型：单跑楼梯（10）、双跑楼梯（20）、双分中起楼梯（21）、交叉楼梯（22）、剪刀楼梯（23）、双分边起楼梯（24）、三跑楼梯（30）、四跑楼梯（40） |
| Col3 | 整形 | 是 |  | 起点位置（和房间起始边距离） |
| Col4 | 整形 | 是 |  | 生成梯柱标记 |
| Col5 | 整形 | 是 |  | 第一个平台高 |
| Col6 | 整形 | 是 |  | 第一个平台宽 |
| Col7 | 整形 | 是 |  | 第一个平台板厚 |
| Col8 | 整形 | 是 |  | 第一个平台梁宽 |
| Col9 | 整形 | 是 |  | 第一个平台梁高 |
| Col10 | 整形 | 是 |  | 第二个平台高 |
| Col11 | 整形 | 是 |  | 第二个平台宽 |
| Col12 | 整形 | 是 |  | 第二个平台板厚 |
| Col13 | 整形 | 是 |  | 第二个平台梁宽 |
| Col14 | 整形 | 是 |  | 第二个平台梁高 |
| Col15 | 整形 | 是 |  | 第三个平台高 |
| Col16 | 整形 | 是 |  | 第三个平台宽 |
| Col17 | 整形 | 是 |  | 第三个平台板厚 |
| Col18 | 整形 | 是 |  | 第三个平台梁宽 |
| Col19 | 整形 | 是 |  | 第三个平台梁高 |
| Col20 | 整形 | 是 |  | 第一梯跑类型0:AT 1:BT 2:CT 3:DT 4:ET 5:FT 6:HT 7:JT |
| Col21 | 整形 | 是 |  | 第一梯跑梯板宽度 |
| Col22 | 整形 | 是 |  | 第一梯跑梯板厚度 |
| Col23 | 整形 | 是 |  | 第一梯跑低端平板长度 |
| Col24 | 整形 | 是 |  | 第一梯跑中端平板长度 |
| Col25 | 整形 | 是 |  | 第一梯跑高端平板长度 |
| Col26 | 整形 | 是 |  | 第一梯跑低端踏步数 |
| Col27 | 整形 | 是 |  | 第一梯跑高端踏步数 |
| Col28 | 整形 | 是 |  | 第二梯跑类型0:AT 1:BT 2:CT 3:DT 4:ET 5:FT 6:HT 7:JT |
| Col29 | 整形 | 是 |  | 第二梯跑梯板宽度 |
| Col30 | 整形 | 是 |  | 第二梯跑梯板厚度 |
| Col31 | 整形 | 是 |  | 第二梯跑低端平板长度 |
| Col32 | 整形 | 是 |  | 第二梯跑中端平板长度 |
| Col33 | 整形 | 是 |  | 第二梯跑高端平板长度 |
| Col34 | 整形 | 是 |  | 第二梯跑低端踏步数 |
| Col35 | 整形 | 是 |  | 第二梯跑高端踏步数 |
| Col36 | 整形 | 是 |  | 第三梯跑类型0:AT 1:BT 2:CT 3:DT 4:ET 5:FT 6:HT 7:JT |
| Col37 | 整形 | 是 |  | 第三梯跑梯板宽度 |
| Col38 | 整形 | 是 |  | 第三梯跑梯板厚度 |
| Col39 | 整形 | 是 |  | 第三梯跑低端平板长度 |
| Col40 | 整形 | 是 |  | 第三梯跑中端平板长度 |
| Col41 | 整形 | 是 |  | 第三梯跑高端平板长度 |
| Col42 | 整形 | 是 |  | 第三梯跑低端踏步数 |
| Col43 | 整形 | 是 |  | 第三梯跑高端踏步数 |
| Col44 | 整形 | 是 |  | 第四梯跑类型0:AT 1:BT 2:CT 3:DT 4:ET 5:FT 6:HT 7:JT |
| Col45 | 整形 | 是 |  | 第四梯跑梯板宽度 |
| Col46 | 整形 | 是 |  | 第四梯跑梯板厚度 |
| Col47 | 整形 | 是 |  | 第四梯跑低端平板长度 |
| Col48 | 整形 | 是 |  | 第四梯跑中端平板长度 |
| Col49 | 整形 | 是 |  | 第四梯跑高端平板长度 |
| Col50 | 整形 | 是 |  | 第四梯跑低端踏步数 |
| Col51 | 整形 | 是 |  | 第四梯跑高端踏步数 |
| Col52 | 整形 | 是 |  | 第一跑相对地面的高度 |
| Col53 | 整形 | 是 |  | 第一个梯梁位置 |
| Col54 | 整形 | 是 |  | 第二个梯梁位置 |
| Col55 | 整形 | 是 |  | 第三个梯梁位置 |
| Col56 | 整形 | 是 |  | 终止位置 |
| Col57 | 整形 | 是 |  | 55缺省值 |
| Col58 | 整形 | 是 |  | 56缺省值 |
| Col59 | 整形 | 是 |  | 57缺省值 |
| Col60 | 整形 | 是 |  | 宽高比 X 10 |
| Col61 | 整形 | 是 |  | 是否预制楼梯 |
| Col62 | 整形 | 是 |  | 踏步长度 |
| Col63 | 整形 | 是 |  | 梁式交叉楼梯斜梁截面高度 |
| Col64 | 整形 | 是 |  | 梁式交叉楼梯斜梁截面宽度 |
| Col65 | 整形 | 是 |  | 梁式交叉楼梯水平梁截面高度 |
| Col66 | 整形 | 是 |  | 梁式交叉楼梯水平梁截面宽度 |
| Col67 | 整形 | 是 |  | 整体抬升值 |
| Col68 | 整形 | 是 |  | 生成休息平台远端梯梁标志 |
| Col69 | 整形 | 是 |  | 钢楼梯梯柱宽 |
| Col70 | 整形 | 是 |  | 钢楼梯梯柱高 |
| Col71 | 整形 | 是 |  | 69缺省值 |
| idNew |  |  |  |  |
| StateFlag |  |  |  |  |
| TZdef | 文本 | 是 |  | 钢楼梯梯柱定义 |
| TLdef | 文本 | 是 |  | 钢楼梯梯梁定义 |
| LCLdef | 文本 | 是 |  | 钢楼梯楼层平台梁定义 |

### 2.21 楼梯布置信息表（tblStairSeg）

<table>
<colgroup>
<col style="width: 18%" />
<col style="width: 12%" />
<col style="width: 12%" />
<col style="width: 7%" />
<col style="width: 50%" />
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
<td style="text-align: center;">楼梯ID</td>
</tr>
<tr>
<td style="text-align: center;">No_</td>
<td style="text-align: center;">整型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">楼梯编号</td>
</tr>
<tr>
<td style="text-align: center;">StdFlrID</td>
<td style="text-align: center;">整型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">楼梯所在的标准层</td>
</tr>
<tr>
<td style="text-align: center;">SectionID</td>
<td style="text-align: center;">整型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">楼梯类型ID</td>
</tr>
<tr>
<td style="text-align: center;">SlabID</td>
<td style="text-align: center;">整型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">楼梯所在房间ID</td>
</tr>
<tr>
<td style="text-align: center;">StartNode</td>
<td style="text-align: center;">整型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;"><p>起始顶点在房间多边形上的序号，从1开始</p>
<p>此多边形应是房间网格多边形去掉共线点和重复点后形成的多边形</p></td>
</tr>
<tr>
<td style="text-align: center;">AntiClockwise</td>
<td style="text-align: center;">整型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">楼梯方向是顺时针(0)还是逆时针(1)</td>
</tr>
</tbody>
</table>

**  **
nData\[0\] //楼梯类型：单跑楼梯（）、双跑楼梯（）、双分中起楼梯（）、交叉楼梯（）、剪刀楼梯（）、双分边起楼梯（）、跑楼梯（）、四跑楼梯（）

nData\[1\] //起点位置（和房间起始边距离）

nData\[2\] //生成梯柱标记

//平台数据：平台高、平台宽、平台板厚、平台梁宽、平台两个

nData\[3\] //第一个平台高

nData\[4\] //第一个平台宽

nData\[5\] //第一个平台板厚

nData\[6\] //第一个平台梁宽

nData\[7\] //第一个平台梁高

nData\[8\] //第二个平台高

nData\[9\] //第二个平台宽

nData\[10\] //第二个平台板厚

nData\[11\] //第二个平台梁宽

nData\[12\] //第二个平台梁高

nData\[13\] //第三个平台高

nData\[14\] //第三个平台宽

nData\[15\] //第三个平台板厚

nData\[16\] //第三个平台梁宽

nData\[17\] //第三个平台梁高

//每跑的数据(目前最多为四跑)

nData\[18\] //梯跑类型0:AT 1:BT 2:CT 3:DT 4:ET 5:FT 6:HT 7:JT

nData\[19\] //梯板宽度

nData\[20\] //梯板厚度

nData\[21\] //低端平板长度

nData\[22\] //中端平板长度

nData\[23\] //高端平板长度

nData\[24\] //低端踏步数

nData\[25\] //高度踏步数

nData\[26\] //梯跑类型0:AT 1:BT 2:CT 3:DT 4:ET 5:FT 6:HT 7:JT

nData\[27\] //梯板宽度

nData\[28\] //梯板厚度

nData\[29\] //低端平板长度

nData\[30\] //中端平板长度

nData\[31\] //高端平板长度

nData\[32\] //低端踏步数

nData\[33\] //高度踏步数

nData\[34\] //梯跑类型0:AT 1:BT 2:CT 3:DT 4:ET 5:FT 6:HT 7:JT

nData\[35\] //梯板宽度

nData\[36\] //梯板厚度

nData\[37\] //低端平板长度

nData\[38\] //中端平板长度

nData\[39\] //高端平板长度

nData\[40\] //低端踏步数

nData\[41\] //高度踏步数

nData\[42\] //梯跑类型0:AT 1:BT 2:CT 3:DT 4:ET 5:FT 6:HT 7:JT

nData\[43\] //梯板宽度

nData\[44\] //梯板厚度

nData\[45\] //低端平板长度

nData\[46\] //中端平板长度

nData\[47\] //高端平板长度

nData\[48\] //低端踏步数

nData\[49\] //高度踏步数

nData\[50\] //第一跑相对地面的高度

### 2.22 梁加腋定义（tblBeamJYDef）

<table>
<colgroup>
<col style="width: 15%" />
<col style="width: 12%" />
<col style="width: 12%" />
<col style="width: 7%" />
<col style="width: 51%" />
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
<td style="text-align: center;">梁加腋ID</td>
</tr>
<tr>
<td style="text-align: center;">No_</td>
<td style="text-align: center;">整型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">梁加腋编号</td>
</tr>
<tr>
<td style="text-align: center;">Name</td>
<td style="text-align: center;">文本</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">梁加腋名称</td>
</tr>
<tr>
<td rowspan="2" style="text-align: center;">Para</td>
<td rowspan="2" style="text-align: center;">整型</td>
<td rowspan="2" style="text-align: center;">否</td>
<td rowspan="2" style="text-align: center;">　</td>
<td style="text-align: center;">腋长 腋高H1 腋高H2</td>
</tr>
<tr>
<td style="text-align: center;"><p>左腋长LL 左腋宽LW1 左腋宽LW2</p>
<p>右腋长RL 右腋宽RW1 右腋宽RW2</p></td>
</tr>
<tr>
<td style="text-align: center;">Kind</td>
<td style="text-align: center;">整型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">梁加腋类型（0竖向梁腋 1水平梁腋）</td>
</tr>
<tr>
<td style="text-align: center;">idNew</td>
<td style="text-align: center;"></td>
<td style="text-align: center;"></td>
<td style="text-align: center;">　</td>
<td style="text-align: center;"></td>
</tr>
<tr>
<td style="text-align: center;">StateFlag</td>
<td style="text-align: center;"></td>
<td style="text-align: center;"></td>
<td style="text-align: center;"></td>
<td style="text-align: center;"></td>
</tr>
</tbody>
</table>

### 2.23 板加腋定义（tblSlabJYDef）

|  字段名   | 字段类型 | 允许为空 | 主键 |                字段含义                 |
|:---------:|:--------:|:--------:|:----:|:---------------------------------------:|
|    ID     |   整型   |    否    |  是  |                板加腋ID                 |
|   No\_    |   整型   |    否    |  　  |               板加腋编号                |
|   Name    |   文本   |    是    |  　  |               板加腋名称                |
|   Para    |   整型   |    否    |  　  |   左腋长L1 左腋高H1 右腋长L2 右腋高H2   |
|   Kind    |   整型   |    否    |  　  | 板加腋类型（0双侧板腋 1左板腋 2右板腋） |
|   idNew   |          |          |  　  |                                         |
| StateFlag |          |          |      |                                         |

### 2.24 柱帽类型定义（tblColcapSect）

|  字段名   | 字段类型 | 允许为空 | 主键 |        字段含义        |
|:---------:|:--------:|:--------:|:----:|:----------------------:|
|    ID     |   整型   |    否    |  是  |         柱帽ID         |
|   No\_    |   整型   |    否    |  　  |        柱帽编号        |
|   Name    |   文本   |    是    |  　  |        柱帽名称        |
|   Kind    |   整型   |    否    |  　  | 柱帽类型（见附录4.10） |
|     W     |   整型   |    否    |      |        柱帽宽度        |
|     L     |   整型   |    否    |      |        柱帽长度        |
|     H     |   整型   |    否    |      |        柱帽高度        |
|    SW     |   整型   |    否    |      |        托板宽度        |
|    SL     |   整型   |    否    |      |        托板长度        |
|    SH     |   整型   |    否    |      |        托板高度        |
|   idNew   |          |          |  　  |                        |
| StateFlag |          |          |      |                        |

## 3、参数、属性与荷载

### 3.1 工程参数信息表（tblProjectPara）

该表记录应用于整个工程的各种参数，每个参数的具体类型请参见附录4.6

| 字段名  | 字段类型 | 允许为空 | 主键 |      字段含义       |
|:-------:|:--------:|:--------:|:----:|:-------------------:|
|   ID    |   整型   |    否    |  是  | 参数ID（见附录4.6） |
| ParaVal | 可变类型 |    否    |  　  | 参数值（见附录4.6） |

### 3.2荷载类型定义（tblLoadSect）

| 字段名 | 字段类型 | 允许为空 | 主键 | 字段含义 |
|:--:|:--:|:--:|:--:|:--:|
| ID | 整型 | 否 | 是 | 类型ID |
| No\_ | 整型 | 否 | 　 | 类型编号 |
| ElementKind | 整型 | 否 | 　 | 荷载对应的构件类型（见附录4.7） |
| ShapeVal | 文本 | 否 | 　 | 荷载定义（6个连续的浮点数），与荷载定义对话框中显示的荷载信息一致。 |

### 3.3荷载布置信息（tblLoadSeg）

|   字段名    | 字段类型 | 允许为空 | 主键 |       字段含义        |
|:-----------:|:--------:|:--------:|:----:|:---------------------:|
|     ID      |   整型   |    否    |  是  |        荷载ID         |
|    No\_     |   整型   |    否    |  　  |       荷载编号        |
|   SectID    |   整型   |    否    |  　  |      荷载类型ID       |
|   Type\_    |   整型   |    否    |  　  | 荷载工况（见附录4.8） |
| ElementID\_ |   整型   |    否    |  　  |     对应构件的id      |

### 3.4构件关联的属性信息（tblProperty）

建筑模型和计算模型互相转换时，盈建科软件内部记录了一些构件的特殊属性。该表记录了这些特殊属性。Name字段表示该条记录的具体含义，目前可能出现的各种属性请参考附录4.9

| 字段名  | 字段类型 | 允许为空 | 主键 |           字段含义           |
|:-------:|:--------:|:--------:|:----:|:----------------------------:|
|   ID    |   整型   |    否    |      |    构件ID，构件类型不固定    |
|  Name   |   文本   |    否    |  　  |           属性名称           |
|  Type   |   整型   |    否    |  　  | 属性类型(3整型 4浮点 27数组) |
| Value\_ |   文本   |    否    |  　  |            属性值            |

### 3.5 标准层参数（tblStdFlrPara）

此表格记录各标准层相关的属性信息

|  字段名  | 字段类型 | 允许为空 | 主键 |           字段含义           |
|:--------:|:--------:|:--------:|:----:|:----------------------------:|
| StdFlrID |   整型   |    否    |      |           标准层ID           |
|   Kind   |   整型   |    否    |  　  | 参数类型,各数值意义见附录4.1 |
| ParaVal  |  浮点型  |    否    |  　  |            属性值            |

## 4、附录

### 4.1标准层参数意义

| 字段值 |         字段意义         |
|:------:|:------------------------:|
|   0    |     梁钢筋保护层厚度     |
|   1    |           板厚           |
|   2    |       板砼等级\*10       |
|   3    |       板保护层厚度       |
|   4    |     柱混凝土等级\*10     |
|   5    |     梁混凝土强度\*10     |
|   6    |     墙混凝土强度\*10     |
|   7    |      梁主筋钢筋类别      |
|   8    |      柱主筋钢筋类别      |
|   9    | 砌体的砂浆强度等级M\*10  |
|   10   | 砌体的块体强度等级MU\*10 |
|   11   |     灌浆砼等级Cb\*10     |
|   12   |      墙主筋钢筋类别      |
|   13   |  混合砂浆(0)或水泥砂浆   |
|   14   |     柱钢筋保护层厚度     |
|   15   |    支撑砼强度等级\*10    |
|   16   |        柱箍筋级别        |
|   17   |        梁箍筋级别        |
|   18   |     边缘构件箍筋级别     |
|   19   |     墙水平分布筋级别     |
|   20   |     墙竖向分布筋级别     |
|   21   |      其它钢构件钢材      |
|   22   |         楼面恒载         |
|   23   |         楼面活载         |

### 4.1.1 钢筋类别

| 值  |      意义      |
|:---:|:--------------:|
|  1  |     HPB300     |
|  2  |     HRB335     |
|  3  |     HRB400     |
|  4  |     HRB500     |
|  5  |     CRB550     |
|  6  |     HPB235     |
|  7  |    HTRB600     |
|  8  |    T63/E/G     |
|  9  |    CRB600H     |
| 10  |     HG6/C      |
| 11  |  HRB600(STD)   |
| 12  |  HRB650(STD)   |
| 13  | HRBF600E(河南) |
| 14  | HTRB(HRBF)630E |

### 4.1.2 钢材类别

| 值  | 意义 |
|:---:|:----:|
| 235 | Q235 |
| 345 | Q345 |
| 390 | Q390 |
| 420 | Q420 |

### 4.2材质

| 字段值 |    字段意义    |
|:------:|:--------------:|
|   1    |     烧结砖     |
|   2    |     蒸压砖     |
|   3    |    空心砌块    |
|   5    |       钢       |
|   6    |     混凝土     |
|   10   |     刚性杆     |
|   16   | 轻骨料混凝土级 |

### 4.3截面类型

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

### 4.4洞口定位距离

| 字段值 |      字段意义      |
|:------:|:------------------:|
|   1    |        靠左        |
|   0    |        居中        |
|   -1   |        靠右        |
| 大于0  | 距墙左边角点的距离 |
| 小于0  | 距墙右边角点的距离 |

### 4.5截面尺寸

序列化int值存储，第一位为截面类型（参看附录4.3），后面的为截面尺寸，即为B、H、U、T、D、F…(以逗号分隔)同YJK截面类型中的截面尺寸值。

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
<td style="text-align: center;">1（矩形）</td>
<td style="text-align: left;"><p>洞口宽</p>
<p>洞口高</p>
<p>材料</p>
<p>唯一ID</p></td>
</tr>
<tr>
<td style="text-align: center;"></td>
<td style="text-align: center;">3（圆形）</td>
<td style="text-align: left;"><p>圆形直径</p>
<p>材料</p>
<p>唯一ID</p></td>
</tr>
<tr>
<td style="text-align: center;"></td>
<td style="text-align: center;">11（半圆拱）</td>
<td style="text-align: left;"><p>沟口净宽</p>
<p>沟口净高</p>
<p>上矢高</p>
<p>材料</p>
<p>唯一ID</p></td>
</tr>
<tr>
<td style="text-align: center;"></td>
<td style="text-align: center;">13（三心圆）</td>
<td style="text-align: left;"><p>沟口净宽</p>
<p>沟口净高</p>
<p>上矢高</p>
<p>第二弧半径</p>
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

### 4.6 计算参数

<table>
<colgroup>
<col style="width: 11%" />
<col style="width: 34%" />
<col style="width: 18%" />
<col style="width: 34%" />
</colgroup>
<thead>
<tr>
<th style="text-align: center;">字段ID</th>
<th style="text-align: center;">字段意义</th>
<th style="text-align: center;">字段值</th>
<th style="text-align: center;">值的意义</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: center;">1</td>
<td style="text-align: center;">版本号</td>
<td style="text-align: center;">20111019</td>
<td style="text-align: center;">当前数据库的版本</td>
</tr>
<tr>
<td style="text-align: center;">2</td>
<td style="text-align: center;">工程名</td>
<td style="text-align: center;"></td>
<td style="text-align: center;"></td>
</tr>
<tr>
<td style="text-align: center;">3</td>
<td style="text-align: center;">归并距离</td>
<td style="text-align: center;"></td>
<td style="text-align: center;"></td>
</tr>
<tr>
<td style="text-align: center;">4</td>
<td style="text-align: center;">当前工程已用的最大id号</td>
<td style="text-align: center;"></td>
<td style="text-align: center;"></td>
</tr>
<tr>
<td rowspan="16" style="text-align: center;">101</td>
<td rowspan="16" style="text-align: center;">结构体系</td>
<td style="text-align: center;">10101</td>
<td style="text-align: center;">框架结构</td>
</tr>
<tr>
<td style="text-align: center;">10102</td>
<td style="text-align: center;">框剪结构</td>
</tr>
<tr>
<td style="text-align: center;">10103</td>
<td style="text-align: center;">框筒结构</td>
</tr>
<tr>
<td style="text-align: center;">10104</td>
<td style="text-align: center;">筒中筒结构</td>
</tr>
<tr>
<td style="text-align: center;">10105</td>
<td style="text-align: center;">剪力墙结构</td>
</tr>
<tr>
<td style="text-align: center;">10106</td>
<td style="text-align: center;">框支剪力墙结构</td>
</tr>
<tr>
<td style="text-align: center;">10107</td>
<td style="text-align: center;">板柱-剪力墙结构</td>
</tr>
<tr>
<td style="text-align: center;">10108</td>
<td style="text-align: center;">异形柱框架结构</td>
</tr>
<tr>
<td style="text-align: center;">10109</td>
<td style="text-align: center;">异形柱框剪结构</td>
</tr>
<tr>
<td style="text-align: center;">10110</td>
<td style="text-align: center;">配筋砌块砌体结构</td>
</tr>
<tr>
<td style="text-align: center;">10111</td>
<td style="text-align: center;">砌体结构</td>
</tr>
<tr>
<td style="text-align: center;">10112</td>
<td style="text-align: center;">底框结构</td>
</tr>
<tr>
<td style="text-align: center;">10113</td>
<td style="text-align: center;">钢框架-中心支撑结构</td>
</tr>
<tr>
<td style="text-align: center;">10114</td>
<td style="text-align: center;">钢框架-偏心支撑结构</td>
</tr>
<tr>
<td style="text-align: center;">10115</td>
<td style="text-align: center;">单层工业厂房</td>
</tr>
<tr>
<td style="text-align: center;">10116</td>
<td style="text-align: center;">多层工业厂房</td>
</tr>
<tr>
<td rowspan="6" style="text-align: center;">102</td>
<td rowspan="6" style="text-align: center;">结构所在地区</td>
<td style="text-align: center;">10201</td>
<td style="text-align: center;">全国</td>
</tr>
<tr>
<td style="text-align: center;">10202</td>
<td style="text-align: center;">广东</td>
</tr>
<tr>
<td style="text-align: center;">10203</td>
<td style="text-align: center;">上海</td>
</tr>
<tr>
<td style="text-align: center;">10204</td>
<td style="text-align: center;">B类建筑（89规范全国）</td>
</tr>
<tr>
<td style="text-align: center;">10205</td>
<td style="text-align: center;">B类建筑（89规范上海）</td>
</tr>
<tr>
<td style="text-align: center;">10206</td>
<td style="text-align: center;">A类建筑</td>
</tr>
<tr>
<td rowspan="4" style="text-align: center;">103</td>
<td rowspan="4" style="text-align: center;">结构材料</td>
<td style="text-align: center;">10301</td>
<td style="text-align: center;">钢筋混凝土</td>
</tr>
<tr>
<td style="text-align: center;">10302</td>
<td style="text-align: center;">钢与混凝土混合结构</td>
</tr>
<tr>
<td style="text-align: center;">10303</td>
<td style="text-align: center;">钢结构</td>
</tr>
<tr>
<td style="text-align: center;">10304</td>
<td style="text-align: center;">砌体结构</td>
</tr>
<tr>
<td style="text-align: center;">104</td>
<td style="text-align: center;">裙房层数</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">105</td>
<td style="text-align: center;">转换层号</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">106</td>
<td style="text-align: center;">地下室层数</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">107</td>
<td style="text-align: center;">加强层所在层号</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">108</td>
<td style="text-align: center;">嵌固端所在层号</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">109</td>
<td style="text-align: center;">与基础相连最大构件底标高</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">110</td>
<td style="text-align: center;">加强层所在层号数</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">111</td>
<td style="text-align: center;">加强层所在层号(数组)</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">112</td>
<td style="text-align: center;">是否弹性时程分析</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td rowspan="4" style="text-align: center;">201</td>
<td rowspan="4" style="text-align: center;">地面粗糙度类别</td>
<td style="text-align: center;">20101</td>
<td style="text-align: center;">A</td>
</tr>
<tr>
<td style="text-align: center;">20102</td>
<td style="text-align: center;">B</td>
</tr>
<tr>
<td style="text-align: center;">20103</td>
<td style="text-align: center;">C</td>
</tr>
<tr>
<td style="text-align: center;">20104</td>
<td style="text-align: center;">D</td>
</tr>
<tr>
<td style="text-align: center;">202</td>
<td style="text-align: center;">修正后的基本风压（kN/m2）</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">203</td>
<td style="text-align: center;">结构X向基本周期（s）</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">204</td>
<td style="text-align: center;">结构Y向基本周期（s）</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">205</td>
<td style="text-align: center;">风荷载计算用阻尼比</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">206</td>
<td style="text-align: center;">是否考虑风振系数</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">207</td>
<td style="text-align: center;">是否考虑横风向风振</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">208</td>
<td style="text-align: center;">对风荷载敏感的高层建筑(承载力计算时的风荷载内力放大)</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">209</td>
<td style="text-align: center;">水平风体型系数分段数(无用)</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">210</td>
<td style="text-align: center;">水平风体型系数分段层号(无用)</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">211</td>
<td style="text-align: center;">水平风体型系数(无用)</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">212</td>
<td style="text-align: center;">风荷载体型系数分段数</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">213</td>
<td style="text-align: center;">风荷载体型系数分段层号</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">214</td>
<td style="text-align: center;">风荷载体型系数</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">215</td>
<td style="text-align: center;">设缝多塔背风面体型系数</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">216</td>
<td style="text-align: center;">多方向风方向数</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">217</td>
<td style="text-align: center;">多方向风各方向角度</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">218</td>
<td style="text-align: center;">有填充墙钢结构</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">301</td>
<td style="text-align: center;">设计地震分组</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td rowspan="6" style="text-align: center;">302</td>
<td rowspan="6" style="text-align: center;">设防烈度</td>
<td style="text-align: center;">30201</td>
<td style="text-align: center;">6(0.05g)</td>
</tr>
<tr>
<td style="text-align: center;">30202</td>
<td style="text-align: center;">7(0.1g)</td>
</tr>
<tr>
<td style="text-align: center;">30203</td>
<td style="text-align: center;">7(0.15g)</td>
</tr>
<tr>
<td style="text-align: center;">30204</td>
<td style="text-align: center;">8(0.2g)</td>
</tr>
<tr>
<td style="text-align: center;">30205</td>
<td style="text-align: center;">8(0.3g)</td>
</tr>
<tr>
<td style="text-align: center;">30206</td>
<td style="text-align: center;">9(0.4g)</td>
</tr>
<tr>
<td rowspan="6" style="text-align: center;">303</td>
<td rowspan="6" style="text-align: center;">场地类别</td>
<td style="text-align: center;">30301</td>
<td style="text-align: center;">I0</td>
</tr>
<tr>
<td style="text-align: center;">30302</td>
<td style="text-align: center;">I1</td>
</tr>
<tr>
<td style="text-align: center;">30303</td>
<td style="text-align: center;">II</td>
</tr>
<tr>
<td style="text-align: center;">30304</td>
<td style="text-align: center;">III</td>
</tr>
<tr>
<td style="text-align: center;">30305</td>
<td style="text-align: center;">VI</td>
</tr>
<tr>
<td style="text-align: center;">30306</td>
<td style="text-align: center;">上海(建模用)</td>
</tr>
<tr>
<td style="text-align: center;">304</td>
<td style="text-align: center;">考虑偶然偏心</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">305</td>
<td style="text-align: center;">X向偶然偏心</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">306</td>
<td style="text-align: center;">Y向偶然偏心</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">307</td>
<td style="text-align: center;">考虑双向地震作用</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">308</td>
<td style="text-align: center;">计算振型个数</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">309</td>
<td style="text-align: center;">活荷载重力荷载代表值组合系数</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">310</td>
<td style="text-align: center;">周期折减系数</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">311</td>
<td style="text-align: center;">结构阻尼比（%）</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">312</td>
<td style="text-align: center;">特征周期Tg（s）</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">313</td>
<td style="text-align: center;">多遇地震影响系数最大值</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">314</td>
<td style="text-align: center;">罕遇地震影响系数最大值</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">315</td>
<td style="text-align: center;">斜交抗侧力构件方向数</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">316</td>
<td style="text-align: center;">斜交抗侧力构件方向角度</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">317</td>
<td style="text-align: center;">自动计算最不利地震方向的地震作用</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td rowspan="2" style="text-align: center;">318</td>
<td rowspan="2" style="text-align: center;">偶然偏心算法</td>
<td style="text-align: center;">31801</td>
<td style="text-align: center;">等效扭矩法</td>
</tr>
<tr>
<td style="text-align: center;">31802</td>
<td style="text-align: center;">瑞利-里兹投影反射谱法</td>
</tr>
<tr>
<td style="text-align: center;">319</td>
<td style="text-align: center;">是否自动设定振型个数</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">320</td>
<td style="text-align: center;">竖向地震作用系数底线值</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">321</td>
<td style="text-align: center;">质量参与系数</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">322</td>
<td style="text-align: center;">自动设定振型个数时<br />
是否指定最大振型个数</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">323</td>
<td style="text-align: center;">自动设定振型个数时<br />
最大振型个数(150)</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">401</td>
<td style="text-align: center;">柱、墙设计时活荷载是否折减</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">402</td>
<td style="text-align: center;">传给基础的活荷载</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">403</td>
<td style="text-align: center;">活荷载不利布置最高层号</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">404</td>
<td style="text-align: center;">柱、墙设计时活荷载折减系数设置</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">501</td>
<td style="text-align: center;">梁端负弯矩调幅系数</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">502</td>
<td style="text-align: center;">活荷载内力放大系数</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">503</td>
<td style="text-align: center;">梁扭矩折减系数</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">504</td>
<td style="text-align: center;">调整与框支柱相连的梁内力</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">505</td>
<td style="text-align: center;">最小剪重比地震力调整</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">506</td>
<td style="text-align: center;">框支剪力墙结构底部加强区剪力墙抗震等级自动提高一级</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">507</td>
<td style="text-align: center;">剪力墙加强区起算层号</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">508</td>
<td style="text-align: center;">实配钢筋超配系数</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">509</td>
<td style="text-align: center;">指定薄弱层</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">510</td>
<td style="text-align: center;">指定薄弱层层号</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">511</td>
<td style="text-align: center;">转换层指定为薄弱层</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">512</td>
<td style="text-align: center;">薄弱层地震内力放大系数</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">513</td>
<td style="text-align: center;">全楼地震作用放大系数</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">514</td>
<td style="text-align: center;">0.2V0调整</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">515</td>
<td style="text-align: center;">0.2V0调整起始层号</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">516</td>
<td style="text-align: center;">0.2V0调整终止层号</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">517</td>
<td style="text-align: center;">0.2V0调整上限</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">518</td>
<td style="text-align: center;">框支柱调整上限</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">519</td>
<td style="text-align: center;">自动对楼层抗剪承载力形成的薄弱层放大调整</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">520</td>
<td style="text-align: center;">最小剪重比地震力调整弱轴方向动位移比例(0~1)0.5</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">521</td>
<td style="text-align: center;">最小剪重比地震力调整强轴方向动位移比例(0~1)0.5</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td rowspan="5" style="text-align: center;">601</td>
<td rowspan="5" style="text-align: center;">恒活荷载计算信息</td>
<td style="text-align: center;">60101</td>
<td style="text-align: center;">不计算恒活荷载</td>
</tr>
<tr>
<td style="text-align: center;">60102</td>
<td style="text-align: center;">一次性加载</td>
</tr>
<tr>
<td style="text-align: center;">60103</td>
<td style="text-align: center;">施工模拟一</td>
</tr>
<tr>
<td style="text-align: center;">60104</td>
<td style="text-align: center;">施工模拟二</td>
</tr>
<tr>
<td style="text-align: center;">60105</td>
<td style="text-align: center;">施工模拟三</td>
</tr>
<tr>
<td style="text-align: center;">602</td>
<td style="text-align: center;">施工次序</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td rowspan="4" style="text-align: center;">603</td>
<td rowspan="4" style="text-align: center;">风荷载计算信息</td>
<td style="text-align: center;">60301</td>
<td style="text-align: center;">不计算风荷载</td>
</tr>
<tr>
<td style="text-align: center;">60302</td>
<td style="text-align: center;">普通方式计算</td>
</tr>
<tr>
<td style="text-align: center;">60303</td>
<td style="text-align: center;">精细方式计算</td>
</tr>
<tr>
<td style="text-align: center;">60304</td>
<td style="text-align: center;">计算水平和特殊风荷载(无用)</td>
</tr>
<tr>
<td rowspan="4" style="text-align: center;">604</td>
<td rowspan="4" style="text-align: center;">地震作用计算信息</td>
<td style="text-align: center;">60401</td>
<td style="text-align: center;">不计算地震作用</td>
</tr>
<tr>
<td style="text-align: center;">60402</td>
<td style="text-align: center;">计算水平地震作用</td>
</tr>
<tr>
<td style="text-align: center;">60403</td>
<td style="text-align: center;">计算水平和规范简化方法竖向地震作用</td>
</tr>
<tr>
<td style="text-align: center;">60404</td>
<td style="text-align: center;">计算水平和反应谱法竖向地震作用</td>
</tr>
<tr>
<td style="text-align: center;">605</td>
<td style="text-align: center;">墙元细分最大控制长度（m）</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">606</td>
<td style="text-align: center;">对所有楼层强制采用刚性楼板假定</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">607</td>
<td style="text-align: center;">强制刚性楼板假定时保留弹性板面外刚度</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">608</td>
<td style="text-align: center;">考虑P-Delta效应</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">609</td>
<td style="text-align: center;">梁柱重叠部分简化为刚域</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">610</td>
<td style="text-align: center;">连梁刚度折减系数</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">611</td>
<td style="text-align: center;">中梁刚度放大系数</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">612</td>
<td style="text-align: center;">托墙梁刚度放大系数</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">613</td>
<td style="text-align: center;">忽略数检警告信息</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">614</td>
<td style="text-align: center;">结构位移计算</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">616</td>
<td style="text-align: center;">全楼构件内力计算</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">617</td>
<td style="text-align: center;">吊车荷载计算</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">618</td>
<td style="text-align: center;">生成传给基础的刚度</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">619</td>
<td style="text-align: center;">构件配筋及验算（包括设置起止配筋层号）</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">620</td>
<td style="text-align: center;">地震作用分析方法（侧刚、总刚）</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">621</td>
<td style="text-align: center;">线性方程组求解方法</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">622</td>
<td style="text-align: center;">水平力与整体坐标夹角</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">623</td>
<td style="text-align: center;">计算人防荷载</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">624</td>
<td style="text-align: center;">输出节点位移</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">625</td>
<td style="text-align: center;">各分塔与整体分别计算</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">626</td>
<td style="text-align: center;">自动分多塔</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">627</td>
<td style="text-align: center;">转换梁/连梁按剪力墙计算</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">628</td>
<td style="text-align: center;">网格划分全协调</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">629</td>
<td style="text-align: center;">连梁按墙元计算控制跨高比</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">630</td>
<td style="text-align: center;">梁刚度放大系数按2010《混凝土规范》取值</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">631</td>
<td style="text-align: center;">梁刚度放大系数上限</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">632</td>
<td style="text-align: center;">少墙框架自动按框架和框架-抗震墙模型计算并取大</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">633</td>
<td style="text-align: center;">少墙框架按纯框架计算时墙弹性模量折减系数</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">634</td>
<td style="text-align: center;">自动分塔控制层号</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">635</td>
<td style="text-align: center;">施工模拟步长</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">636</td>
<td style="text-align: center;">地下室不自动划分多塔</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">637</td>
<td style="text-align: center;">板元细分最大控制长度（m）</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">638</td>
<td style="text-align: center;">地下室强制刚性楼板假定</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">639</td>
<td style="text-align: center;">墙梁跨中节点作为刚性楼板从节点</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">640</td>
<td style="text-align: center;">对短墙肢自动加密</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td rowspan="6" style="text-align: center;">701</td>
<td rowspan="6" style="text-align: center;">框架抗震等级</td>
<td style="text-align: center;">70101</td>
<td style="text-align: center;">特一级</td>
</tr>
<tr>
<td style="text-align: center;">70102</td>
<td style="text-align: center;">一级</td>
</tr>
<tr>
<td style="text-align: center;">70103</td>
<td style="text-align: center;">二级</td>
</tr>
<tr>
<td style="text-align: center;">70104</td>
<td style="text-align: center;">三级</td>
</tr>
<tr>
<td style="text-align: center;">70105</td>
<td style="text-align: center;">四级</td>
</tr>
<tr>
<td style="text-align: center;">70106</td>
<td style="text-align: center;">非抗震</td>
</tr>
<tr>
<td style="text-align: center;">702</td>
<td style="text-align: center;">钢框架抗震等级</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">703</td>
<td style="text-align: center;">剪力墙抗震等级</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">704</td>
<td style="text-align: center;">抗震构造措施的抗震等级提高</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td rowspan="3" style="text-align: center;">705</td>
<td rowspan="3" style="text-align: center;">性能设计</td>
<td style="text-align: center;">70501</td>
<td style="text-align: center;">不考虑</td>
</tr>
<tr>
<td style="text-align: center;">70502</td>
<td style="text-align: center;">不屈服</td>
</tr>
<tr>
<td style="text-align: center;">70503</td>
<td style="text-align: center;">弹性</td>
</tr>
<tr>
<td style="text-align: center;">706</td>
<td style="text-align: center;">钢柱计算长度系数按有侧移计算</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">707</td>
<td style="text-align: center;">剪力墙构造边缘构件的设计执行高规7.2.17-4</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td rowspan="2" style="text-align: center;">708</td>
<td rowspan="2" style="text-align: center;">柱配筋计算方法，单偏压或双偏压</td>
<td style="text-align: center;">70801</td>
<td style="text-align: center;">单偏压</td>
</tr>
<tr>
<td style="text-align: center;">70802</td>
<td style="text-align: center;">双偏压</td>
</tr>
<tr>
<td style="text-align: center;">709</td>
<td style="text-align: center;">梁保护层厚度</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">710</td>
<td style="text-align: center;">柱保护层厚度</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td rowspan="2" style="text-align: center;">711</td>
<td rowspan="2" style="text-align: center;">型钢混凝土构件设计依据</td>
<td style="text-align: center;">71101</td>
<td style="text-align: center;">《型钢混凝土组合结构技术规程》JGJ138-2001</td>
</tr>
<tr>
<td style="text-align: center;">71102</td>
<td style="text-align: center;">《钢骨混凝土结构技术规程》YB9082-2006</td>
</tr>
<tr>
<td style="text-align: center;">712</td>
<td style="text-align: center;">框架柱的轴压比限值按框架结构采用</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">713</td>
<td style="text-align: center;">框架梁梁端配筋考虑受压钢筋影响</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">714</td>
<td style="text-align: center;">墙柱配筋设计考虑端柱</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">715</td>
<td style="text-align: center;">矩形混凝土梁按T形梁配筋</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">716</td>
<td style="text-align: center;">连梁按对称配筋设计</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">717</td>
<td style="text-align: center;">考虑翼缘板中的钢筋为受压钢筋</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">718</td>
<td style="text-align: center;">板中受力钢筋配筋率(%)</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td rowspan="3" style="text-align: center;">719</td>
<td rowspan="3" style="text-align: center;">构造边缘构件尺寸设计依据</td>
<td style="text-align: center;">71901</td>
<td style="text-align: center;">《抗规》GB50011第6.4.5条</td>
</tr>
<tr>
<td style="text-align: center;">71902</td>
<td style="text-align: center;">《高规》JGJ3-2010第7.2.16条</td>
</tr>
<tr>
<td style="text-align: center;">71903</td>
<td style="text-align: center;">《砼规》GB50010-2010第11.7.19条</td>
</tr>
<tr>
<td style="text-align: center;">720</td>
<td style="text-align: center;">边缘构件合并距离(mm)(300)</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">721</td>
<td style="text-align: center;">边缘构件尺寸取整模数(mm)(50)</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">801</td>
<td style="text-align: center;">混凝土容重</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td rowspan="4" style="text-align: center;">802</td>
<td rowspan="4" style="text-align: center;">钢号</td>
<td style="text-align: center;">80201</td>
<td style="text-align: center;">Q235</td>
</tr>
<tr>
<td style="text-align: center;">80202</td>
<td style="text-align: center;">Q345</td>
</tr>
<tr>
<td style="text-align: center;">80203</td>
<td style="text-align: center;">Q390</td>
</tr>
<tr>
<td style="text-align: center;">80204</td>
<td style="text-align: center;">Q420</td>
</tr>
<tr>
<td style="text-align: center;">803</td>
<td style="text-align: center;">钢容重</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">804</td>
<td style="text-align: center;">砌体容重</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">805</td>
<td style="text-align: center;">轻骨料混凝土容重</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">806</td>
<td style="text-align: center;">轻骨料混凝土密度等级</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">807</td>
<td style="text-align: center;">钢构件截面净毛面积比</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">808</td>
<td style="text-align: center;">梁主筋级别</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">809</td>
<td style="text-align: center;">柱主筋级别</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">810</td>
<td style="text-align: center;">墙主筋级别</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td rowspan="6" style="text-align: center;">811</td>
<td rowspan="6" style="text-align: center;">梁箍筋级别</td>
<td style="text-align: center;">81101</td>
<td style="text-align: center;">HPB235</td>
</tr>
<tr>
<td style="text-align: center;">81102</td>
<td style="text-align: center;">HPB300</td>
</tr>
<tr>
<td style="text-align: center;">81103</td>
<td style="text-align: center;">HRB335</td>
</tr>
<tr>
<td style="text-align: center;">81104</td>
<td style="text-align: center;">HRB400</td>
</tr>
<tr>
<td style="text-align: center;">81105</td>
<td style="text-align: center;">HRB500</td>
</tr>
<tr>
<td style="text-align: center;">81106</td>
<td style="text-align: center;">LZDL550</td>
</tr>
<tr>
<td style="text-align: center;">812</td>
<td style="text-align: center;">柱箍筋级别</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">813</td>
<td style="text-align: center;">墙水平分布筋级别</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">814</td>
<td style="text-align: center;">墙竖向分布筋级别</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">815</td>
<td style="text-align: center;">边缘构件箍筋级别</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">816</td>
<td style="text-align: center;">梁箍筋间距（mm）</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">817</td>
<td style="text-align: center;">柱箍筋间距（mm）</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">818</td>
<td style="text-align: center;">墙水平分布筋间距（mm）</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">819</td>
<td style="text-align: center;">墙竖向分布筋配筋率（%）</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">820</td>
<td style="text-align: center;">结构底部需要单独指定墙竖向分布筋配筋率的层数</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">821</td>
<td style="text-align: center;">结构底部需要单独指定的墙竖向分布筋配筋率</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">822</td>
<td style="text-align: center;">墙主要材料</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">901</td>
<td style="text-align: center;">结构重要性系数</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">902</td>
<td style="text-align: center;">恒荷载分项系数</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">903</td>
<td style="text-align: center;">活荷载分项系数</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">904</td>
<td style="text-align: center;">活荷载组合值系数</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">905</td>
<td style="text-align: center;">考虑结构设计使用年限的活荷载调整系数</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">906</td>
<td style="text-align: center;">风荷载分项系数</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">907</td>
<td style="text-align: center;">风荷载组合值系数</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">908</td>
<td style="text-align: center;">风荷载是否参与地震组合</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">909</td>
<td style="text-align: center;">水平地震分项系数</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">910</td>
<td style="text-align: center;">竖向地震分项系数</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">911</td>
<td style="text-align: center;">是否考虑竖向地震为主的组合</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">912</td>
<td style="text-align: center;">自定义组合</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">913</td>
<td style="text-align: center;">承载力设计时风荷载效应放大系数</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">914</td>
<td style="text-align: center;">吊车荷载重力荷载代表值系数</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">915</td>
<td style="text-align: center;">是否采用自定义组合</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">1001</td>
<td style="text-align: center;">土层水平抗力系数的比例系数（M值）</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">1002</td>
<td style="text-align: center;">外墙分布筋保护层厚度（mm）</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">1003</td>
<td style="text-align: center;">扣除地面以下几层的回填土约束（计算）</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">1004</td>
<td style="text-align: center;">回填土容重</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">1005</td>
<td style="text-align: center;">室外地坪标高</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">1006</td>
<td style="text-align: center;">回填土侧压力系数</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">1007</td>
<td style="text-align: center;">地下水位标高（m）</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">1008</td>
<td style="text-align: center;">室外地面附加荷载（kN/m2）</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">1100101</td>
<td style="text-align: center;">有托墙梁但非底框结构(砌体模块结构体系专用值)</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">1101</td>
<td style="text-align: center;">砼与砌体弹性模量比3</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td rowspan="3" style="text-align: center;">1102</td>
<td rowspan="3" style="text-align: center;">施工质量ABC(B)</td>
<td style="text-align: center;">110201</td>
<td style="text-align: center;">A</td>
</tr>
<tr>
<td style="text-align: center;">110202</td>
<td style="text-align: center;">B</td>
</tr>
<tr>
<td style="text-align: center;">110203</td>
<td style="text-align: center;">C</td>
</tr>
<tr>
<td style="text-align: center;">1103</td>
<td style="text-align: center;">砌体孔洞率50(%)</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">1104</td>
<td style="text-align: center;">是否按规范确定墙梁上部荷载，否则按经验(规范)</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">1105</td>
<td style="text-align: center;">有洞口墙梁荷载折减系数(0.5-1)(1)</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">1106</td>
<td style="text-align: center;">无洞口墙梁荷载折减系数1</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">1107</td>
<td style="text-align: center;">坡屋面时结构附加高度0</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">1108</td>
<td style="text-align: center;">抗震墙侧移刚度考虑边框柱作用1</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td rowspan="3" style="text-align: center;">1109</td>
<td rowspan="3" style="text-align: center;">楼面刚度类型（刚性、刚柔性、柔性）</td>
<td style="text-align: center;">110901</td>
<td style="text-align: center;">刚性</td>
</tr>
<tr>
<td style="text-align: center;">110902</td>
<td style="text-align: center;">刚柔性</td>
</tr>
<tr>
<td style="text-align: center;">110903</td>
<td style="text-align: center;">柔性</td>
</tr>
<tr>
<td style="text-align: center;">1110</td>
<td style="text-align: center;">底框层数</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">1111</td>
<td style="text-align: center;">地下室结构嵌固高度</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td rowspan="2" style="text-align: center;">1112</td>
<td rowspan="2" style="text-align: center;">墙体刚度计算方法(常规方法)</td>
<td style="text-align: center;">11201</td>
<td style="text-align: center;">有限元方法计算</td>
</tr>
<tr>
<td style="text-align: center;">11202</td>
<td style="text-align: center;">常规方法计算</td>
</tr>
<tr>
<td style="text-align: center;">1113</td>
<td style="text-align: center;">抗震计算采用《镇（乡）村建筑抗震技术规程》</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">1114</td>
<td style="text-align: center;">考虑基准面积率的有效楼层数</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">1115</td>
<td style="text-align: center;">是否按经验确定墙梁上部荷载(否)</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">1116</td>
<td style="text-align: center;">是否计算地震作用(T)</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">1117</td>
<td style="text-align: center;">是否计算风荷载作用(T)</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">1118</td>
<td style="text-align: center;">是否自动分塔计算(T)</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">1301</td>
<td style="text-align: center;">公司名称</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">1302</td>
<td style="text-align: center;">工程名称</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">1303</td>
<td style="text-align: center;">工程代号</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">1304</td>
<td style="text-align: center;">设计人</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">1305</td>
<td style="text-align: center;">校核人</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">1401</td>
<td style="text-align: center;">输出起始时间(0.f)</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">1402</td>
<td style="text-align: center;">输出终止时间(10.f)</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">1403</td>
<td style="text-align: center;">时间步长(0.1f)</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">1404</td>
<td style="text-align: center;">地震烈度6、7、8、9默认可取地震信息中烈度，用户可修改为其它值</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td rowspan="2" style="text-align: center;">1405</td>
<td rowspan="2" style="text-align: center;">地震影响</td>
<td style="text-align: center;">140501</td>
<td style="text-align: center;">多遇</td>
</tr>
<tr>
<td style="text-align: center;">140502</td>
<td style="text-align: center;">罕遇</td>
</tr>
<tr>
<td style="text-align: center;">1406</td>
<td style="text-align: center;">主方向峰值加速度(35.f)</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">1407</td>
<td style="text-align: center;">次方向峰值加速度(默认为YP_SCPRIMMAX*0.85)</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">1408</td>
<td style="text-align: center;">积分计算时长(10.f)</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">1409</td>
<td style="text-align: center;">积分步长(0.1f)</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td rowspan="2" style="text-align: center;">1410</td>
<td rowspan="2" style="text-align: center;">阻尼比计算方法</td>
<td style="text-align: center;">141001</td>
<td style="text-align: center;">所有振型同一阻尼</td>
</tr>
<tr>
<td style="text-align: center;">141002</td>
<td style="text-align: center;">Rayleigh阻尼组合模态阻尼</td>
</tr>
<tr>
<td style="text-align: center;">1411</td>
<td style="text-align: center;">所有振型同一阻尼时的值(0.05f)</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">1412</td>
<td style="text-align: center;">刚度因子Ck(0.f)</td>
<td style="text-align: center;">0x0FFFFFFF</td>
<td style="text-align: center;">用于取地震波参数中的ID</td>
</tr>
<tr>
<td style="text-align: center;">1413</td>
<td style="text-align: center;">质量因子Cm(0.f)</td>
<td style="text-align: center;">0x20000000</td>
<td style="text-align: center;">用于取地震波参数中的是否计算主方向</td>
</tr>
<tr>
<td style="text-align: center;">1414</td>
<td style="text-align: center;">地震波参数数组(int)其数值中高位存储是否计算主/次方向峰值加速度，低位存储地震波ID</td>
<td style="text-align: center;">0x10000000</td>
<td style="text-align: center;">用于取地震波参数中的是否计算次方向</td>
</tr>
<tr>
<td style="text-align: center;">1415</td>
<td style="text-align: center;">各振型模态阻尼系数Di(float数组)</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">1416</td>
<td style="text-align: center;">参与振型数 默认与地震信息中振型数一致，(0-YP_MODENUM)</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">1417</td>
<td style="text-align: center;">反应谱起始周期</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">1418</td>
<td style="text-align: center;">反应谱终止周期</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
<tr>
<td style="text-align: center;">1419</td>
<td style="text-align: center;">反应谱周期步长</td>
<td style="text-align: center;">　</td>
<td style="text-align: center;">　</td>
</tr>
</tbody>
</table>

### 4.7 构件类型

| 值  |    意义    |
|:----|:----------:|
| -1  |    节点    |
| 1   |     墙     |
| 11  |     柱     |
| 12  |     梁     |
| 13  |    支撑    |
| 14  |    次梁    |
| 21  | 门窗，墙洞 |
| 22  |    板洞    |

### 4.8 荷载工况

| 字段值 | 字段意义  |
|:-------|:---------:|
| 1      |   恒载    |
| 2      |   活载    |
| 1      | 柱x向恒载 |
| 2      | 柱x向活载 |
| 3      | 柱y向恒载 |
| 4      | 柱y向活载 |

### 4.9 构件上的各种扩展数据

本节给出了在表tblProperty可能出现的各种扩展数据。如无特殊说明，负数代表该数据是通过工程参数或楼层参数由软件自动判断得到的属性，正数则是由用户手工指定过的属性。本节说明的数据含义均指绝对值的含义。

| 字段名 | HNTDJ                     |
|--------|---------------------------|
| 类型   | VT_R4(5)                  |
| 说明   | 记录混凝土标号，钢构件为0 |

1混凝土等级，ID对应的构件可能为梁、次梁、柱、支撑、墙、板

| 字段名 | GANGH                                               |
|--------|-----------------------------------------------------|
| 类型   | VT_R4(5)                                            |
| 说明   | 记录钢号，只对钢构件和型钢砼构件有效，混凝土构件为0 |

2钢号，ID对应的构件可能为梁、次梁、柱、支撑、墙、板

<table>
<caption><p>3特殊梁，ID对应的构件可能为梁或次梁</p></caption>
<colgroup>
<col style="width: 19%" />
<col style="width: 21%" />
<col style="width: 58%" />
</colgroup>
<thead>
<tr>
<th>字段名</th>
<th colspan="2">SpBeam</th>
</tr>
</thead>
<tbody>
<tr>
<td>类型</td>
<td colspan="2">VT_SAFEARRAY</td>
</tr>
<tr>
<td>数组长度</td>
<td colspan="2">13</td>
</tr>
<tr>
<td>[0]</td>
<td>左端约束</td>
<td>0-固接 1-铰接 2-滑动</td>
</tr>
<tr>
<td>[1]</td>
<td>右端约束</td>
<td>0-固接 1-铰接 2-滑动</td>
</tr>
<tr>
<td>[2]</td>
<td>不调幅梁</td>
<td>1-不调幅梁0/2-调幅梁</td>
</tr>
<tr>
<td>[3]</td>
<td>连梁</td>
<td>1-连梁 0/2-非连梁</td>
</tr>
<tr>
<td>[4]</td>
<td>转换梁</td>
<td>1-托墙转换梁 2-非托墙转换梁 其他-非转换梁</td>
</tr>
<tr>
<td>[5]</td>
<td><p>个位-耗能梁</p>
<p>十位-门式刚梁</p></td>
<td><p>0-否 1-是</p>
<p>0-否 1-是</p></td>
</tr>
<tr>
<td>[6]</td>
<td>抗震等级</td>
<td><p>70101-特一级</p>
<p>70102-一级</p>
<p>70103-二级</p>
<p>70104-三级</p>
<p>70105-四级</p>
<p>70106-非抗震</p></td>
</tr>
<tr>
<td>[7]</td>
<td>刚度系数</td>
<td>浮点值</td>
</tr>
<tr>
<td>[8]</td>
<td>扭矩折减</td>
<td>浮点值</td>
</tr>
<tr>
<td>[9]</td>
<td>调幅系数</td>
<td>浮点值</td>
</tr>
<tr>
<td>[11]</td>
<td>连梁分缝</td>
<td>整型值：0-3</td>
</tr>
<tr>
<td>[12]</td>
<td>连梁钢筋</td>
<td>0-普通配筋 1-交叉配筋 2-斜撑配筋 3-集中对角</td>
</tr>
</tbody>
</table>

<table>
<caption><p>4特殊柱，ID对应的构件为柱</p></caption>
<colgroup>
<col style="width: 19%" />
<col style="width: 23%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th>字段名</th>
<th colspan="2">SpColm</th>
</tr>
</thead>
<tbody>
<tr>
<td>类型</td>
<td colspan="2">VT_SAFEARRAY</td>
</tr>
<tr>
<td>数组长度</td>
<td colspan="2">8</td>
</tr>
<tr>
<td>[0]</td>
<td>上端约束</td>
<td>0-固接 1-铰接</td>
</tr>
<tr>
<td>[1]</td>
<td>下端约束</td>
<td>0-固接 1-铰接</td>
</tr>
<tr>
<td>[2]</td>
<td style="text-align: left;"><p>个位-角柱</p>
<p>十位-转换柱</p>
<p>百位-门式刚柱</p></td>
<td>0-否 1-是</td>
</tr>
<tr>
<td>[3]</td>
<td>抗震等级</td>
<td>同梁（&gt;0）</td>
</tr>
<tr>
<td>[4]</td>
<td>x向剪力系数</td>
<td>浮点值</td>
</tr>
<tr>
<td>[5]</td>
<td>y向剪力系数</td>
<td>浮点值</td>
</tr>
<tr>
<td>[6]</td>
<td>轴压比限值增减量</td>
<td>浮点值</td>
</tr>
<tr>
<td>[7]</td>
<td>水平转换构件</td>
<td>0-否 1-是</td>
</tr>
</tbody>
</table>

<table>
<caption><p>5特殊支撑，ID对应的构件为支撑（斜杆）</p></caption>
<colgroup>
<col style="width: 19%" />
<col style="width: 23%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th>字段名</th>
<th colspan="2">SpBrac</th>
</tr>
</thead>
<tbody>
<tr>
<td>类型</td>
<td colspan="2">VT_SAFEARRAY</td>
</tr>
<tr>
<td>数组长度</td>
<td colspan="2">8</td>
</tr>
<tr>
<td>[0]</td>
<td>上端约束</td>
<td>0-固接 1-铰接</td>
</tr>
<tr>
<td>[1]</td>
<td>下端约束</td>
<td>0-固接 1-铰接</td>
</tr>
<tr>
<td>[3]</td>
<td>抗震等级</td>
<td>同梁</td>
</tr>
<tr>
<td>[4]</td>
<td>水平转换构件</td>
<td>0-否 1-是</td>
</tr>
</tbody>
</table>

<table>
<caption><p>6特殊墙，ID对应的构件为墙</p></caption>
<colgroup>
<col style="width: 19%" />
<col style="width: 33%" />
<col style="width: 47%" />
</colgroup>
<thead>
<tr>
<th>字段名</th>
<th colspan="2">SpWall</th>
</tr>
</thead>
<tbody>
<tr>
<td>类型</td>
<td colspan="2">VT_SAFEARRAY</td>
</tr>
<tr>
<td>数组长度</td>
<td colspan="2">11</td>
</tr>
<tr>
<td>[0]</td>
<td>地下室外墙</td>
<td>1-地下室外墙 2-临空墙 0/3-一般墙</td>
</tr>
<tr>
<td>[1]</td>
<td>抗震等级</td>
<td>同梁</td>
</tr>
<tr>
<td>[2]</td>
<td style="text-align: left;">水平分布筋最小配筋率</td>
<td>浮点值</td>
</tr>
<tr>
<td>[3]</td>
<td>竖向分布筋最小配筋率</td>
<td>浮点值</td>
</tr>
<tr>
<td>[4]</td>
<td>临空墙荷载</td>
<td>浮点值</td>
</tr>
<tr>
<td>[5]</td>
<td>连梁刚度折减系数</td>
<td>浮点值</td>
</tr>
<tr>
<td>[6]</td>
<td>连梁分缝</td>
<td>整型值：0-3</td>
</tr>
<tr>
<td>[7]</td>
<td>连梁钢筋</td>
<td>0-普通配筋 1-交叉配筋 2-斜撑配筋</td>
</tr>
<tr>
<td>[9]</td>
<td>左墙柱是否短肢剪力墙</td>
<td>0-否 1-是</td>
</tr>
<tr>
<td>[10]</td>
<td>右墙柱是否短肢剪力墙</td>
<td>0-否 1-是</td>
</tr>
</tbody>
</table>

<table>
<caption><p>7板属性，ID对应的构件为板</p></caption>
<colgroup>
<col style="width: 19%" />
<col style="width: 23%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th>字段名</th>
<th colspan="2">SpSlab</th>
</tr>
</thead>
<tbody>
<tr>
<td>类型</td>
<td colspan="2">VT_SAFEARRAY</td>
</tr>
<tr>
<td>数组长度</td>
<td colspan="2">1</td>
</tr>
<tr>
<td rowspan="2">[0]</td>
<td>个位-板类型</td>
<td>0-无板 1-刚性板 2-弹性板3 3-弹性板6 4-弹性膜</td>
</tr>
<tr>
<td>十位-刚性板号</td>
<td></td>
</tr>
</tbody>
</table>

<table>
<caption><p>8节点属性，ID对应的构件为节点</p></caption>
<colgroup>
<col style="width: 19%" />
<col style="width: 23%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th>字段名</th>
<th colspan="2">SpNode</th>
</tr>
</thead>
<tbody>
<tr>
<td>类型</td>
<td colspan="2">VT_SAFEARRAY</td>
</tr>
<tr>
<td>数组长度</td>
<td colspan="2">27</td>
</tr>
<tr>
<td>[0]</td>
<td>附加质量</td>
<td>浮点值，单位kg</td>
</tr>
<tr>
<td>[1]</td>
<td>局部坐标系标志</td>
<td>= 1表示是否定义了局部坐标系</td>
</tr>
<tr>
<td>[2]</td>
<td>节点约束</td>
<td><p>= 0，普通节点，与其他节点无关</p>
<p>&gt;0，本节点是从节点，记录所属主节点的ID</p>
<p>&lt;0，本节点是主节点，绝对值是对应从节点的ID</p></td>
</tr>
<tr>
<td>[3]~[8]</td>
<td>局部坐标系的值</td>
<td>局部坐标系的1轴向量和2轴向量</td>
</tr>
<tr>
<td>[9]~[14]</td>
<td>自由度约束</td>
<td>=1表示该方向自由度被约束</td>
</tr>
<tr>
<td>[15]~[20]</td>
<td>弹簧刚度</td>
<td>6个自由度方向设置的弹簧刚度</td>
</tr>
<tr>
<td>[21]~[26]</td>
<td>强制位移</td>
<td>6个自由度方向的强制位移，-9999表示没有</td>
</tr>
</tbody>
</table>

| 字段名 | support                             |
|--------|-------------------------------------|
| 类型   | VT_I4 (3)                           |
| 说明   | 接基础的节点有此属性，属性值固定为1 |

9支座属性，ID对应的构件为节点

<table>
<caption><p>6人防设计等级，ID对应的对象为标准层</p></caption>
<colgroup>
<col style="width: 19%" />
<col style="width: 80%" />
</colgroup>
<thead>
<tr>
<th>字段名</th>
<th>rfsjdj</th>
</tr>
</thead>
<tbody>
<tr>
<td>类型</td>
<td>VT_I4 (3)</td>
</tr>
<tr>
<td>可能值</td>
<td><ol type="1">
<li><p>不考虑人防</p></li>
</ol>
<p>40-4级（核）</p>
<p>45-4B级（核）</p>
<ol start="50" type="1">
<li><p>5级（核）</p></li>
<li><p>5级（常规）</p></li>
</ol>
<p>60-6级（核）</p>
<p>61-6级（常规）</p>
<p>65-6B级（核）</p></td>
</tr>
</tbody>
</table>

| 字段名 | dbrfdxhz              |
|--------|-----------------------|
| 类型   | VT_R4 (5) ，单位kN/m2 |

7顶板人防等效荷载，ID对应的对象为标准层

| 字段名 | wqrfdxhz              |
|--------|-----------------------|
| 类型   | VT_R4 (5) ，单位kN/m2 |

8外墙人防等效荷载，ID对应的对象为标准层

### 4.10 墙加腋参数

举例： 1，1000.00，500.00，-2

1：此墙上的墙洞数；

1000.00：墙加腋长度；

500.00：墙加腋宽度；

-2：墙加腋位置

位置 = 起始点 \* 方向

起始点：1为起点，2为终点，3为两端都设置

方向：-1为下方或右方，1为上方或左方

### 4.11 柱帽类型

| 值  |                    意义                    |
|:---:|:------------------------------------------:|
| -1  |  （↑）锥形柱帽+矩形托板（勾选楼板上柱帽）  |
| -2  |      （↑）锥形柱帽（勾选楼板上柱帽）       |
| -3  |      （↑）矩形托板（勾选楼板上柱帽）       |
|  1  | （↓）锥形柱帽+矩形托板（未勾选楼板上柱帽） |
|  2  |     （↓）锥形柱帽（未勾选楼板上柱帽）      |
|  3  |     （↓）矩形托板（未勾选楼板上柱帽）      |
|  4  |           （↓）锥形柱帽+锥形托板           |
|  5  |           （↓）矩形柱帽+矩形托板           |
