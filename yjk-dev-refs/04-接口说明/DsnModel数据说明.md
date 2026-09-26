dsnModel数据关系
建模PM系列
定义信息
pmSectDef_Beam
[图]

| pmSectDef_Beam |  |  |  |  |  |
|---|---|---|---|---|---|
| 梁截面定义表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | 截面ID |  |  |
| No | INTEGER | False | 建模截面定义编号 |  |  |
| PMComKind | INTEGER | False | 所属构件类型 |  | 建模构件类别枚举YJKDSN::EPMComKind |
| PMSectKind | INTEGER | False | 建模截面类型 |  |  |
| PMMatKind | INTEGER | False | 建模截面材料类型 |  |  |
| Name | TEXT | False | 截面名称 |  |  |
| SectInf | TEXT | False | 建模截面定义数组 |  |  |

pmSectDef_Col
[图]

| pmSectDef_Col |  |  |  |  |  |
|---|---|---|---|---|---|
| 柱截面定义表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | 截面ID |  |  |
| No | INTEGER | False | 建模截面定义编号 |  |  |
| PMComKind | INTEGER | False | 所属构件类型 |  | 建模构件类别枚举YJKDSN::EPMComKind |
| PMSectKind | INTEGER | False | 建模截面类型 |  |  |
| PMMatKind | INTEGER | False | 建模截面材料类型 |  |  |
| Name | TEXT | False | 截面名称 |  |  |
| SectInf | TEXT | False | 建模截面定义数组 |  |  |

pmSectDef_Brace
[图]

| pmSectDef_Brace |  |  |  |  |  |
|---|---|---|---|---|---|
| 支撑截面定义表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | 截面ID |  |  |
| No | INTEGER | False | 建模截面定义编号 |  |  |
| PMComKind | INTEGER | False | 所属构件类型 |  | 建模构件类别枚举YJKDSN::EPMComKind |
| PMSectKind | INTEGER | False | 建模截面类型 |  |  |
| PMMatKind | INTEGER | False | 建模截面材料类型 |  |  |
| Name | TEXT | False | 截面名称 |  |  |
| SectInf | TEXT | False | 建模截面定义数组 |  |  |

pmSectDef_Wall
[图]

| pmSectDef_Wall |  |  |  |  |  |
|---|---|---|---|---|---|
| 墙截面定义表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | 截面ID |  |  |
| No | INTEGER | False | 建模截面定义编号 |  |  |
| PMComKind | INTEGER | False | 所属构件类型 |  | 建模构件类别枚举YJKDSN::EPMComKind |
| PMSectKind | INTEGER | False | 建模截面类型 |  |  |
| PMMatKind | INTEGER | False | 建模截面材料类型 |  |  |
| Name | TEXT | False | 截面名称 |  |  |
| B | REAL | False | 墙厚（mm） |  |  |
| SteelT | REAL | False | 钢板厚（mm） |  | 对于外包为单侧钢板厚 |

pmSectDef_WallHole
[图]

| pmSectDef_WallHole |  |  |  |  |  |
|---|---|---|---|---|---|
| 墙洞截面定义表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | 截面ID |  |  |
| No | INTEGER | False | 建模截面定义编号 |  |  |
| PMComKind | INTEGER | False | 所属构件类型 |  | 建模构件类别枚举YJKDSN::EPMComKind |
| PMSectKind | INTEGER | False | 建模截面类型 |  |  |
| Name | TEXT | False | 截面名称 |  |  |
| B | REAL | False | 墙厚（mm） |  |  |
| H | REAL | False | 钢板厚（对于外包为单侧钢板厚）（mm） |  |  |

pmSectDef_SlabHole
[图]

| pmSectDef_SlabHole |  |  |  |  |  |
|---|---|---|---|---|---|
| 板洞截面定义表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | 截面ID |  |  |
| No | INTEGER | False | 建模截面定义编号 |  |  |
| PMComKind | INTEGER | False | 所属构件类型 |  | 建模构件类别枚举YJKDSN::EPMComKind |
| PMSectKind | INTEGER | False | 建模截面类型 |  |  |
| Name | TEXT | False | 截面名称 |  |  |
| B | REAL | False | 板宽（mm） |  |  |
| H | REAL | False | 板高（mm） |  |  |

pmSectDef_CantiSlab
[图]

| pmSectDef_CantiSlab |  |  |  |  |  |
|---|---|---|---|---|---|
| 悬挑板截面定义表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | 截面ID |  |  |
| No | INTEGER | False | 建模截面定义编号 |  |  |
| PMComKind | INTEGER | False | 所属构件类型 |  | 建模构件类别枚举YJKDSN::EPMComKind |
| PMSubComKind | INTEGER | False | 悬挑板类型 |  | 0-悬挑板 1-阳台板 2-空调板 3-挑沿 YJKDsnData中未记录该参数 |
| PMSectKind | INTEGER | False | 建模截面类型 |  |  |
| PMMatKind | INTEGER | False | 建模截面材料类型 |  |  |
| Name | TEXT | False | 截面名称 |  |  |
| B | REAL | False | 板宽（mm） |  |  |
| H | REAL | False | 板长（mm） |  |  |
| T | REAL | False | 板厚（mm） |  |  |

pmSectDef_HollowSlab
[图]

| pmSectDef_HollowSlab |  |  |  |  |  |
|---|---|---|---|---|---|
| 空心板截面定义表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | 截面ID |  |  |
| No | INTEGER | False | 建模截面定义编号 |  |  |
| PMComKind | INTEGER | False | 所属构件类型 |  | 建模构件类别枚举YJKDSN::EPMComKind |
| PMSectKind | INTEGER | False | 建模截面类型 |  | 1-筒型 2-箱型 |
| PMMatKind | INTEGER | False | 建模截面材料类型 |  |  |
| Name | TEXT | False | 截面名称 |  |  |
| W | REAL | False | 筒型为筒心直径，箱型为顺肋箱宽（mm） |  |  |
| L | REAL | False | 筒长或箱长（mm） |  |  |
| H | REAL | False | 箱高（mm） |  |  |
| Bw | REAL | False | 顺筒肋宽（mm） |  |  |
| Bh | REAL | False | 横筒肋宽（mm） |  |  |
| Htop | REAL | False | 筒顶板厚（mm） |  |  |
| Hbtm | REAL | False | 筒底板厚（mm） |  |  |

pmSectDef_ColCap
[图]

| pmSectDef_ColCap |  |  |  |  |  |
|---|---|---|---|---|---|
| 柱帽截面定义表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | 截面ID |  |  |
| No | INTEGER | False | 建模截面定义编号 |  |  |
| PMComKind | INTEGER | False | 所属构件类型 |  | 建模构件类别枚举YJKDSN::EPMComKind |
| PMSectKind | INTEGER | False | 建模截面类型 |  |  |
| PMMatKind | INTEGER | False | 建模截面材料类型 |  |  |
| Name | TEXT | False | 截面名称 |  |  |
| W | REAL | False | 柱帽宽度（mm） |  |  |
| L | REAL | False | 柱帽长度（mm） |  |  |
| H | REAL | False | 柱帽高度（mm） |  |  |
| SlabW | REAL | False | 托板宽度（mm） |  |  |
| SlabL | REAL | False | 托板长度（mm） |  |  |
| SlabH | REAL | False | 托板高度（mm） |  |  |

pmSectDef_BeamHaunch
[图]

| pmSectDef_BeamHaunch |  |  |  |  |  |
|---|---|---|---|---|---|
| 梁加腋截面定义表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | 截面ID |  |  |
| No | INTEGER | False | 建模截面定义编号 |  |  |
| PMComKind | INTEGER | False | 所属构件类型 |  | 建模构件类别枚举YJKDSN::EPMComKind |
| PMSectKind | INTEGER | False | 建模截面类型 |  |  |
| PMMatKind | INTEGER | False | 建模截面材料类型 |  |  |
| Name | TEXT | False | 截面名称 |  |  |
| SectInf | TEXT | False | 建模截面定义数组 |  |  |

pmSectDef_SlabHaunch
[图]

| pmSectDef_SlabHaunch |  |  |  |  |  |
|---|---|---|---|---|---|
| 板加腋截面定义表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | 截面ID |  |  |
| No | INTEGER | False | 建模截面定义编号 |  |  |
| PMComKind | INTEGER | False | 所属构件类型 |  | 建模构件类别枚举YJKDSN::EPMComKind |
| PMSectKind | INTEGER | False | 建模截面类型 |  |  |
| PMMatKind | INTEGER | False | 建模截面材料类型 |  |  |
| Name | TEXT | False | 截面名称 |  |  |
| BL | REAL | False | 左腋长（mm） |  |  |
| HL | REAL | False | 左腋高（mm） |  |  |
| BR | REAL | False | 右腋长（mm） |  |  |
| HR | REAL | False | 右腋高（mm） |  |  |

pmSectDef_PetroDevice
[图]

| pmSectDef_PetroDevice |  |  |  |  |  |
|---|---|---|---|---|---|
| 石化设备截面定义表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | 截面ID |  |  |
| No | INTEGER | False | 建模截面定义编号 |  |  |
| PMComKind | INTEGER | False | 所属构件类型 |  | 建模构件类别枚举YJKDSN::EPMComKind |
| PMSectKind | INTEGER | False | 建模截面类型 |  |  |
| PMMatKind | INTEGER | False | 建模截面材料类型 |  |  |
| Name | TEXT | False | 截面名称 |  |  |
| LevelNum | INTEGER | False | 立式阶数 |  |  |
| Level1Inf | TEXT | False | 立式一阶数据 |  |  |
| Level2Inf | TEXT | False | 立式二阶数据 |  |  |
| DataInf | TEXT | False | 所有截面参数的double数组 |  |  |

pmLoadDef_Base
[图]

| pmLoadDef_Base |  |  |  |  |  |
|---|---|---|---|---|---|
| 基本荷载定义表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | 建模荷载定义ID |  |  |
| No | INTEGER | False | 建模荷载定义编号 |  |  |
| PMComKind | INTEGER | False | 所属构件类型 |  | 建模构件类别枚举YJKDSN::EPMComKind |
| PMLoadKind | INTEGER | False | 建模荷载类型 |  |  |
| Name | TEXT | False | 荷载名称 |  |  |
| LoadInf | TEXT | False | 建模荷载定义数组 |  |  |

pmLoadDef_Crane
[图]

| pmLoadDef_Crane |  |  |  |  |  |
|---|---|---|---|---|---|
| 吊车荷载定义表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | 建模荷载定义ID |  |  |
| No | INTEGER | False | 建模荷载定义编号 |  |  |
| Name | TEXT | False | 荷载名称 |  |  |
| LoadInf | TEXT | False | 建模荷载定义数组 |  |  |

布置信息
pmNode
[图]

| pmNode |  |  |  |  |  |
|---|---|---|---|---|---|
| 节点信息表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | 节点ID |  |  |
| No | INTEGER | False | 节点顺序号 |  | 每层从1开始统计 |
| StdFlrID | INTEGER | False | 所属标准层ID | pmStdFlr表中ID |  |
| X | REAL | False | 节点X坐标（mm） |  |  |
| Y | REAL | False | 节点Y坐标（mm） |  |  |
| HDiff | REAL | False | 节点高度（mm） |  |  |

pmGrid
[图]

| pmGrid |  |  |  |  |  |
|---|---|---|---|---|---|
| 网格信息表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | 网格ID |  |  |
| No | INTEGER | False | 网格顺序号 |  | 每层从1开始统计 |
| StdFlrID | INTEGER | False | 所属标准层ID | pmStdFlr表中ID |  |
| Node1 | INTEGER | False | 起始节点ID | pmNode表中ID |  |
| Node2 | INTEGER | False | 终止节点ID | pmNode表中ID |  |
| AxisID | INTEGER | False | 所在轴线ID | pmAxis表中ID |  |
| IsArc | INTEGER | False | 是否为圆弧网格 |  | 是取1，否取0 |
| NodeC | INTEGER | False | 圆弧网格中心点ID | pmNode表中ID | 非圆弧取-1 |
| Radius | REAL | False | 圆弧网格半径（mm） |  | 非圆弧时无意义(为起点到原点距离) |
| HaunchID | INTEGER | False | 网格上的板加腋ID | pmSectDef_SlabHaunch表中的ID |  |

pmAxis
[图]

| pmAxis |  |  |  |  |  |
|---|---|---|---|---|---|
| 轴线信息表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | 网格ID |  |  |
| No | INTEGER | False | 网格顺序号 |  | 每层从1开始统计 |
| StdFlrID | INTEGER | False | 所属标准层ID | pmStdFlr表中ID |  |
| Node1 | INTEGER | False | 起始节点ID | pmNode表中ID | 圆弧网格下，起点为圆心且存为负数 |
| Node2 | INTEGER | False | 终止节点ID | pmNode表中ID |  |
| Name | TEXT | False | 轴线名称 |  |  |
| IsArc | INTEGER | False | 是否为圆弧轴线 |  | 是取1，否取0 |
| NodeC | INTEGER | False | 圆弧轴线中心点ID | pmNode表中ID | 非圆弧取0 |

pmBeam
[图]

| pmBeam |  |  |  |  |  |
|---|---|---|---|---|---|
| 梁布置信息表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | 梁ID |  |  |
| No | INTEGER | False | 梁顺序号 |  | 每层从1开始统计 |
| StdFlrID | INTEGER | False | 所属标准层ID | pmStdFlr表中ID |  |
| SectID | INTEGER | False | 梁截面ID | pmSectDef_Beam表中ID |  |
| GridID | INTEGER | False | 所在网格ID | pmGrid表中ID |  |
| EA | REAL | False | 沿轴偏心（mm） |  |  |
| EZ1 | REAL | False | 起点标高（mm） |  |  |
| EZ2 | REAL | False | 终点标高（mm） |  |  |
| Ang | REAL | False | 截面转角（角度） |  |  |
| HaunchInf | TEXT | False | 梁加腋ID | pmSectDef_BeamHaunch表中ID |  |

pmCol
[图]

| pmCol |  |  |  |  |  |
|---|---|---|---|---|---|
| 柱布置信息表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | 柱ID |  |  |
| No | INTEGER | False | 柱顺序号 |  | 每层从1开始统计 |
| StdFlrID | INTEGER | False | 所属标准层ID | pmStdFlr表中ID |  |
| SectID | INTEGER | False | 柱截面ID | pmSectDef_Col表中ID |  |
| CapDefID | INTEGER | False | 柱帽定义ID | pmSectDef_ColCap表中ID |  |
| NodeID | INTEGER | False | 柱所在节点ID | pmNode表中ID |  |
| EX | REAL | False | X方向偏心（mm） |  |  |
| EY | REAL | False | Y方向偏心（mm） |  |  |
| EZ | REAL | False | Z方向偏心（mm） |  |  |
| Ang | REAL | False | 截面转角（角度） |  |  |
| Cut_ColInf | TEXT | False | 柱裁剪点坐标集 |  |  |
| Cut_CapInf | TEXT | False | 柱帽裁剪点坐标集 |  |  |
| Cut_SlabInf | TEXT | False | 托板裁剪点坐标集 |  |  |

pmBrace
[图]

| pmBrace |  |  |  |  |  |
|---|---|---|---|---|---|
| 支撑布置信息表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | 支撑ID |  |  |
| No | INTEGER | False | 支撑顺序号 |  | 每层从1开始统计 |
| StdFlrID | INTEGER | False | 所属标准层ID | pmStdFlr表中ID |  |
| SectID | INTEGER | False | 支撑截面ID | pmSectDef_Brace表中ID |  |
| Node1 | INTEGER | False | 支撑起点ID | pmNode表中ID |  |
| Node2 | INTEGER | False | 支撑终点ID | pmNode表中ID |  |
| EX | REAL | False | X方向偏心（mm） |  |  |
| EY | REAL | False | Y方向偏心（mm） |  |  |
| Ang | REAL | False | 截面转角（角度） |  |  |
| EX1 | REAL | False | 1点X方向偏移（mm） |  |  |
| EY1 | REAL | False | 1点Y方向偏移（mm） |  |  |
| EZ1 | REAL | False | 1点Z方向偏移（mm） |  |  |
| EX2 | REAL | False | 2点X方向偏移（mm） |  |  |
| EY2 | REAL | False | 2点Y方向偏移（mm） |  |  |
| EZ2 | REAL | False | 2点Z方向偏移（mm） |  |  |

pmSubBeam
[图]

| pmSubBeam |  |  |  |  |  |
|---|---|---|---|---|---|
| 次梁布置信息表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | 次梁ID |  |  |
| No | INTEGER | False | 次梁顺序号 |  | 每层从1开始统计 |
| StdFlrID | INTEGER | False | 所属标准层ID | pmStdFlr表中ID |  |
| SectID | INTEGER | False | 次梁截面ID | pmSectDef_Beam表中ID |  |
| Grid1ID | INTEGER | False | 次梁起始网格ID | pmGrid表中ID |  |
| Grid2ID | INTEGER | False | 次梁中止网格ID | pmGrid表中ID |  |
| EA | REAL | False | 偏轴偏心（mm） |  |  |
| EZ1 | REAL | False | 起点高度（mm） |  |  |
| EZ2 | REAL | False | 终点高度（mm） |  |  |
| Ang | REAL | False | 截面转角（角度） |  |  |
| X1 | REAL | False | 起点X坐标（mm） |  |  |
| Y1 | REAL | False | 起点Y坐标（mm） |  |  |
| Z1 | REAL | False | 起点Z坐标（mm） |  |  |
| X2 | REAL | False | 终点X坐标（mm） |  |  |
| Y2 | REAL | False | 终点Y坐标（mm） |  |  |
| Z2 | REAL | False | 终点Z坐标（mm） |  |  |

pmWall
[图]

| pmWall |  |  |  |  |  |
|---|---|---|---|---|---|
| 墙布置信息表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | 墙ID |  |  |
| No | INTEGER | False | 墙顺序号 |  | 每层从1开始统计 |
| StdFlrID | INTEGER | False | 所属标准层ID | pmStdFlr表中ID |  |
| SectID | INTEGER | False | 墙截面ID | pmSectDef_Wall表中ID |  |
| GridID | INTEGER | False | 墙所在网格ID | pmGrid表中ID |  |
| EA | REAL | False | 偏轴偏心（mm） |  |  |
| EA1 | REAL | False | 墙底偏轴偏心（mm） |  |  |
| EZ | REAL | False | 墙底标高（mm） |  |  |
| EZ1 | REAL | False | 墙顶起始点标高（角度） |  |  |
| EZ2 | REAL | False | 墙顶终止点标高（mm） |  |  |
| EX1 | REAL | False | 下端起点外扩距离（mm） |  |  |
| EX2 | REAL | False | 上端终点外扩距离（mm） |  |  |
| IsSlope | INTEGER | False | 是否斜墙 |  | 是-1 否-0 |

pmWallHole
[图]

| pmWallHole |  |  |  |  |  |
|---|---|---|---|---|---|
| 墙洞布置信息表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | 墙洞ID |  |  |
| No | INTEGER | False | 墙洞顺序号 |  | 每层从1开始统计 |
| StdFlrID | INTEGER | False | 所属标准层ID | pmStdFlr表中ID |  |
| HoleID | INTEGER | False | 墙洞截面ID | pmSectDef_WallHole表中ID |  |
| GridID | INTEGER | False | 墙洞所在网格ID | pmGrid表中ID |  |
| EC | REAL | False | 定位距离（mm） |  |  |
| EZ | REAL | False | 底部标高（mm） |  |  |

pmSlab
[图]

| pmSlab |  |  |  |  |  |
|---|---|---|---|---|---|
| 板布置信息表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | 板ID |  |  |
| No | INTEGER | False | 板顺序号 |  | 每层从1开始统计 |
| StdFlrID | INTEGER | False | 所属标准层ID | pmStdFlr表中ID |  |
| GridInf | TEXT | False | 板所在网格ID集 | pmGrid表中ID |  |
| T | REAL | False | 厚度（mm） |  |  |
| IsHole | INTEGER | False | 是否开洞 |  | 是-1 否-0 |
| IsRect | INTEGER | False | 是否矩形 |  | 是-1 否-0 |
| HDiff | REAL | False | 楼板错层（mm） |  |  |
| Xc | REAL | False | 形心X坐标（mm） |  |  |
| Yc | REAL | False | 形心Y坐标（mm） |  |  |
| PolyInf | TEXT | False | 房间周边点集 |  |  |
| TransWay | INTEGER | False | 导荷方式 |  | 0-没设置过 1-单向板 2-梯形三角形 |
| Ang1 | REAL | False | 塑性铰1（角度） |  |  |
| Ang2 | REAL | False | 塑性铰2（角度） |  |  |
| Dead | REAL | False | 楼板恒载 |  |  |
| Live | REAL | False | 楼板活载 |  |  |
| EdgeSupportInf | TEXT | False | 房间非受力边ID集 |  |  |

pmSlabHole
[图]

| pmSlabHole |  |  |  |  |  |
|---|---|---|---|---|---|
| 板洞布置信息表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | 板洞ID |  |  |
| No | INTEGER | False | 板洞顺序号 |  | 每层从1开始统计 |
| StdFlrID | INTEGER | False | 所属标准层ID | pmStdFlr表中ID |  |
| HoleID | INTEGER | False | 板洞截面ID | pmSectDef_SlabHole表中ID |  |
| SlabID | INTEGER | False | 所属楼板ID | pmSlab表中ID |  |
| NodeID | INTEGER | False | 所在节点ID | pmNode表中ID |  |
| EX | REAL | False | X方向偏心（mm） |  |  |
| EY | REAL | False | Y方向偏心（mm） |  |  |
| Ang | REAL | False | 布置方向（角度） |  |  |

pmCantiSlab
[图]

| pmCantiSlab |  |  |  |  |  |
|---|---|---|---|---|---|
| 悬挑板布置信息表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | 悬挑板ID |  |  |
| No | INTEGER | False | 悬挑板顺序号 |  | 每层从1开始统计 |
| StdFlrID | INTEGER | False | 所属标准层ID | pmStdFlr表中ID |  |
| SectID | INTEGER | False | 悬挑板截面ID | pmSectDef_CantiSlab表中ID |  |
| GridID | INTEGER | False | 所在网格ID | pmGrid表中ID |  |
| T | REAL | False | 厚度（mm） |  |  |
| EC | REAL | False | 偏心（mm） |  |  |
| EZ | REAL | False | 高差（mm） |  |  |
| DR | REAL | False | 布置方向 |  | [TODO]貌似应该为int且各数代表什么待确认 |

pmHollowSlab
[图]

| pmHollowSlab |  |  |  |  |  |
|---|---|---|---|---|---|
| 空心板布置信息表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | 空心板ID |  |  |
| No | INTEGER | False | 空心板顺序号 |  | 每层从1开始统计 |
| StdFlrID | INTEGER | False | 所属标准层ID | pmStdFlr表中ID |  |
| SectID | INTEGER | False | 空心板截面ID | pmSectDef_HollowSlab表中ID |  |
| GridIDInf | INTEGER | False | 所在网格ID | pmGrid表中ID |  |
| IsHole | INTEGER | False | 是否开洞 |  | 1-是 0-否 |
| IsRect | INTEGER | False | 是否为矩形 |  | 1-是 0-否 |
| T | REAL | False | 厚度（mm） |  |  |
| HDiff | REAL | False | 楼板错层（mm） |  |  |
| Xc | REAL | False | 形心X坐标（mm） |  |  |
| Yc | REAL | False | 形心X坐标（mm） |  |  |
| PolyInf | TEXT | False | 周边点集 |  |  |
| TransWay | INTEGER | False | 导荷方式 |  | 0-没设置过 1-单向板 2-梯形三角形 |
| Ang1 | REAL | False | 塑性铰1 |  |  |
| Ang2 | REAL | False | 塑性铰2 |  |  |
| Dead | REAL | False | 楼板恒载 |  |  |
| Live | REAL | False | 楼板活载 |  |  |
| SolidX | REAL | False |  |  |  |
| SolidY | REAL | False |  |  |  |
| BoxPosX | INTEGER | False | X方向箱体排布 |  |  |
| BoxPosY | INTEGER | False | Y方向箱体排布 |  |  |
| BegX | REAL | False |  |  |  |
| BegY | REAL | False |  |  |  |
| DisXL | REAL | False | 左边起始边距（mm） |  |  |
| DisXR | REAL | False | 右边起始边距（mm） |  |  |
| DisYT | REAL | False | 上边起始边距（mm） |  |  |
| DisYB | REAL | False | 下边起始边距（mm） |  |  |

pmPetroDevice
[图]

| pmPetroDevice |  |  |  |  |  |
|---|---|---|---|---|---|
| 石化设备布置信息表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | 石化设备ID |  |  |
| No | INTEGER | False | 石化设备顺序号 |  | 每层从1开始统计 |
| StdFlrID | INTEGER | False | 所属标准层ID | pmStdFlr表中ID |  |
| SectID | INTEGER | False | 石化设备截面ID | pmSectDef_PetroDevice表中ID |  |
| SupportIDInf | TEXT | False | 设备作用点ID集 |  |  |
| NodeID | INTEGER | False | 关联节点ID | pmNode表中ID |  |
| SlabID | REAL | False | 关联楼板ID | pmSlab表中ID | 此处应为int类型 |

pmLoadBase
[图]

| pmLoadBase |  |  |  |  |  |
|---|---|---|---|---|---|
| 基本荷载布置信息表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | 荷载ID |  |  |
| No | INTEGER | False | 荷载顺序号 |  | 每层从1开始统计 |
| StdFlrID | INTEGER | False | 所属标准层ID | pmStdFlr表中ID |  |
| LoadID | INTEGER | False | 建模荷载定义ID | pmLoadDef_Base表中ID |  |
| PMComID | INTEGER | False | 所属构件ID |  |  |
| PMComKind | INTEGER | False | 所属构件类型 |  |  |
| PMLoadKind | INTEGER | False | 荷载类型 |  |  |
| LoadInf | TEXT | False | 建模荷载布置数组 |  |  |
| MovingLoadInf | TEXT | False | 建模移动荷载布置数组 |  |  |

pmLoadCrane
[图]

| pmLoadCrane |  |  |  |  |  |
|---|---|---|---|---|---|
| 吊车荷载布置信息表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | 吊车荷载ID |  |  |
| No | INTEGER | False | 吊车荷载顺序号 |  | 每层从1开始统计 |
| StdFlrID | INTEGER | False | 所属标准层ID | pmStdFlr表中ID |  |
| Ch1ID | INTEGER | False |  |  |  |
| Ch2ID | INTEGER | False |  |  |  |
| Ax1ID | INTEGER | False |  |  |  |
| Nd11ID | INTEGER | False |  |  |  |
| Nd12ID | INTEGER | False |  |  |  |
| Ax2ID | INTEGER | False |  |  |  |
| Nd21ID | INTEGER | False |  |  |  |
| Nd22ID | INTEGER | False |  |  |  |
| EX1 | REAL | False |  |  |  |
| EX2 | REAL | False |  |  |  |
| HX | REAL | False |  |  |  |
| F1 | REAL | False |  |  |  |
| F2 | REAL | False |  |  |  |
| Ez | REAL | False |  |  |  |
| IDCHNUM | INTEGER | False |  |  |  |
| IDCH1 | INTEGER | False |  |  |  |
| IDCH2 | INTEGER | False |  |  |  |
| JAN1 | INTEGER | False |  |  |  |
| IDX11 | INTEGER | False |  |  |  |
| IDX12 | INTEGER | False |  |  |  |
| JAN2 | INTEGER | False |  |  |  |
| IDX21 | INTEGER | False |  |  |  |
| IDX22 | INTEGER | False |  |  |  |

pmExtend
[图]

| pmExtend |  |  |  |  |  |
|---|---|---|---|---|---|
| 扩展数据信息表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ComID | INTEGER | False | 构件ID |  |  |
| StdFlrID | INTEGER | False | 所属标准层ID | pmStdFlr表中ID |  |
| PMComKind | INTEGER | False | 所属构件类型 |  |  |
| Name | TEXT | False | 属性名称 |  |  |
| Type | INTEGER | False | 属性类别 |  | 采用VARIANT中的类别定义 |
| intVal | INTEGER | False | int属性 |  |  |
| dblVal | REAL | False | double属性 |  |  |
| strVal | TEXT | False | string属性 |  |  |
| dblValInf | TEXT | False | 建模荷载布置数组 |  |  |

楼层信息
pmStdFlr
[图]
[图]

| pmStdFlr |  |  |  |  |  |
|---|---|---|---|---|---|
| 标准层信息表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | 层ID |  |  |
| No | INTEGER | False | 层号 |  | 从1开始 |
| Name | TEXT | False | 名称 |  |  |
| Height | REAL | False | 层高（mm） |  |  |
| DL | REAL | False | 恒载 |  |  |
| LL | REAL | False | 活载 |  |  |
| LLReduce | INTEGER | False | 楼面活载折减标记 |  | 1-折减 0-不折减 |
| SlabT | REAL | False | 板厚（mm） |  |  |
| Cover_Beam | REAL | False | 梁钢筋保护层厚度（mm） |  |  |
| Cover_Col | REAL | False | 柱钢筋保护层厚度 |  |  |
| Cover_Wall | REAL | False | 墙保护层厚度 |  |  |
| Cover_Slab | REAL | False | 板保护层厚度 |  |  |
| ConGrade_Beam | REAL | False | 梁混凝土强度 |  |  |
| ConGrade_Col | REAL | False | 柱混凝土强度 |  |  |
| ConGrade_Brace | REAL | False | 支撑砼强度等级 |  |  |
| ConGrade_Wall | REAL | False | 墙混凝土强度 |  |  |
| ConGrade_Slab | REAL | False | 板混凝土强度 |  |  |
| MainBar_Beam | INTEGER | False | 梁主筋钢筋类别 |  |  |
| MainBar_Col | INTEGER | False | 柱主筋钢筋类别 |  |  |
| MainBar_Wall | INTEGER | False | 墙主筋钢筋类别 |  |  |
| MainBar_Slab | INTEGER | False | 板主筋级别 |  |  |
| HoopBar_Beam | INTEGER | False | 梁箍筋级别 |  |  |
| HoopBar_Col | INTEGER | False | 柱箍筋级别 |  |  |
| HoopBar_Wall | INTEGER | False | 边缘构件箍筋级别 |  |  |
| HorBar_Wall | INTEGER | False | 墙水平分布筋级别 |  |  |
| VerBar_Wall | INTEGER | False | 墙竖向分布筋级别 |  |  |
| Steel | INTEGER | False | 钢号 |  |  |
| MortarGrade | REAL | False | 砌体的砂浆强度等级M |  |  |
| BlockGrade | REAL | False | 砌体的块体强度等级MU |  |  |
| BlockConGrade | REAL | False | 灌浆砼等级Cb |  |  |
| MortarType | INTEGER | False | 混合砂浆(0)或水泥砂浆 |  |  |

pmFlrAssembly
[图]

| pmFlrAssembly |  |  |  |  |  |
|---|---|---|---|---|---|
| 楼层组装表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | 层ID |  |  |
| No | INTEGER | False | 层号 |  | 从1开始 |
| StdFlrID | INTEGER | False | 所属标准层ID | pmStdFlr表中ID |  |
| Name | TEXT | False | 名称 |  |  |
| Level | REAL | False | 层底标高（mm） |  |  |
| Height | REAL | False | 层高（mm） |  |  |

pmZRCCom
[图]

| pmZRCCom |  |  |  |  |  |
|---|---|---|---|---|---|
| 自然层构件数据表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | 构件编号 |  | 从1开始，不分层 |
| UUID | TEXT | False | UUID |  |  |
| PMComKind | INTEGER | False | 所属构件类型 |  |  |
| StdComID | INTEGER | False | 构件建模ID | pm表中ID |  |
| StdFlrID | INTEGER | False | 所属标准层ID | pmStdFlr表中ID |  |
| FlrID | INTEGER | False | 层号 | pmFlrAssembly表中ID |  |

前处理PRE系列
preBeam
[图]
[图]
[图]
[图]

| preBeam |  |  |  |  |  |
|---|---|---|---|---|---|
| 梁计算与设计参数，对应前处理特殊构件定义 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 梁层号 |  |  |
| TowNo | INTEGER | False | 梁塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| FlrID | INTEGER | False | 梁层内编号 |  |  |
| Shell | INTEGER | False |  |  |  |
| Solid | INTEGER | False | 是否按实体单元计算 |  |  |
| PMNo | INTEGER | False | 梁在结构模型中的编号 |  | 负数为地基梁 |
| PMSectNo | INTEGER | False | 梁截面在结构模型中的编号 |  |  |
| NodeS | INTEGER | False | 梁起始端节点 |  |  |
| NodeE | INTEGER | False | 梁终末端节点 |  |  |
| IsArc | INTEGER | False | 是否是弧梁 |  |  |
| ArcCInf | INTEGER | False | 弧梁圆心 |  |  |
| SpanOut | REAL | False | 梁平面外长度 |  |  |
| EccSInf | TEXT | False | 梁起始端偏心 |  |  |
| EccEInf | TEXT | False | 梁终末端偏心 |  |  |
| SteelT | REAL | False | 梁内钢板宽 |  |  |
| SteelH | REAL | False | 梁内钢板高 |  |  |
| LinkS | INTEGER | False | 梁起始端约束 | EBarRest | 固接,铰接, 滑动，半固接 |
| LinkE | INTEGER | False | 梁终末端约束 | EBarRest | 固接,铰接, 滑动，半固接 |
| RigidS | REAL | False | 梁起始端刚域 |  |  |
| RigidE | REAL | False | 梁终末端刚域 |  |  |
| StiffCoeM | REAL | False | 刚度折减系数 |  |  |
| StiffCoeInf | TEXT | False | 刚度系数 |  | 轴向, 2轴方向剪切, 3轴方向剪切, 抗扭, 绕2轴抗弯, 绕3轴抗弯 |
| StiffReleaseInf | TEXT | False | 刚度释放 |  |  |
| KZDJ | INTEGER | False | 梁抗震等级 |  |  |
| KZDJGZ | INTEGER | False | 梁抗震构造措施的抗震等级 |  |  |
| MainBar | INTEGER | False | 梁主筋等级 |  |  |
| HoopBar | INTEGER | False | 梁箍筋等级 |  |  |
| SeisVCom | INTEGER | False | 是否考虑竖向地震 |  |  |
| ZZZJM | INTEGER | False | 按抗规进行性能设计时的 中震正截面性能水准 |  | 0不考虑 1不屈服 2弹性 3屈服 |
| ZZXJM | INTEGER | False | 按抗规进行性能设计时的 中震斜截面性能水准 |  | 0不考虑 1不屈服 2弹性 3屈服 |
| DZZJM | INTEGER | False | 按抗规进行性能设计时的 大震正截面性能水准 |  | 0不考虑 1不屈服 2弹性 3屈服 |
| DZXJM | INTEGER | False | 按抗规进行性能设计时的 大震斜截面性能水准 |  | 0不考虑 1不屈服 2弹性 3屈服 |
| XNSJEmpSign | INTEGER | False | 按高规进行性能设计时的构件类型 |  | 1:耗能2:普通竖向 3:关键 |
| PMMatType | INTEGER | False | 梁材料类型 |  |  |
| ConGrade | REAL | False | 混凝土等级 |  |  |
| SteelKind | INTEGER | False | 钢号 |  |  |
| Cover | REAL | False | 梁保护层厚度 |  |  |
| Air | INTEGER | False | 是否是人防构件 |  |  |
| YZ | INTEGER | False |  |  |  |
| EnvSign | INTEGER | False | 是否包络设计梁 |  |  |
| DuctLevel | INTEGER | False | 延性等级 |  | 适用欧标、美标 |
| LiveLoadCoe | REAL | False | 梁活荷折减系数 |  |  |
| LiveGraCoe | REAL | False | 梁活荷重力荷载代表值组合系数 |  |  |
| ReduceCoeInf | TEXT | False | 梁自定义工况折减系数 |  |  |
| StruCoe | REAL | False | 结构重要性系数 |  |  |
| EmpCoe | REAL | False | 梁重要性系数 |  |  |
| WJType | INTEGER | False | 梁的空间结构属性 网架类型 |  | 网架 双层网壳 单层网壳 立体桁架 一般桁架杆件 中心支撑 偏心支撑 门刚支撑 温室大棚 |
| TrussSign | INTEGER | False | 梁的空间结构属性 杆件位置 |  | 桁架上弦杆 桁架腹杆 桁架中层弦杆 桁架下弦杆 支座腹杆 温室称重杆件 温室拱杆 温室其他杆件 |
| TrussXID | INTEGER | False | X方向桁架编号 |  |  |
| TrussYID | INTEGER | False | Y方向桁架编号 |  |  |
| TempInf | TEXT | False | 构件温度 |  | 依次记录 0-升温 1-降温 2-防火升温 |
| FHth | REAL | False | 耐火时间 |  |  |
| FHiqz | INTEGER | False | 膨胀型 |  | 1-非膨胀型 2-水泥砂浆 |
| FHri | REAL | False | 等效热阻/等效热传导系数 |  |  |
| FHdil | REAL | False | 保护层厚度 |  |  |
| FHfxz | REAL | False | 截面形状系数 |  |  |
| HN | INTEGER | False | 是否新钢规性能设计塑性耗能构件 |  |  |
| BTRatioGrade | INTEGER | False | 新钢规性能设计宽厚比 |  |  |
| YXGrade | INTEGER | False | 新钢规性能设计延性等级 |  |  |
| BetaE | REAL | False | 新钢规性能设计非耗能构件系数 |  |  |
| TF | INTEGER | False | 是否是调幅梁 |  |  |
| LL | INTEGER | False | 是否是连梁 |  |  |
| Tran | INTEGER | False | 是否是转换梁 |  |  |
| Portal | INTEGER | False | 是否是门刚 |  |  |
| HNL | INTEGER | False | 是否是耗能梁 |  |  |
| ZHL | INTEGER | False | 是否是主梁 |  |  |
| Crane | INTEGER | False | 是否是地梁 |  |  |
| XJKind | INTEGER | False | 斜筋类型 |  | 不设置斜筋 交叉斜筋 对角斜筋 对角暗撑 |
| TorCoe | REAL | False |  |  |  |
| AmpCoe | REAL | False |  |  |  |

preBeam_ZHL
[图]
preBrace
[图]
[图]
[图]
[图]
[图]

| preBrace |  |  |  |  |  |
|---|---|---|---|---|---|
| 支撑计算与设计参数，对应前处理特殊构件定义 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 斜杆层号 |  |  |
| TowNo | INTEGER | False | 斜杆塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| FlrID | INTEGER | False | 斜杆层内编号 |  |  |
| Shell | INTEGER | False |  |  |  |
| Solid | INTEGER | False | 是否按实体单元计算 |  |  |
| PMNo | INTEGER | False | 斜杆在结构模型中的编号 |  | 负数为地基梁 |
| PMSectNo | INTEGER | False | 斜杆截面在结构模型中的编号 |  |  |
| NodeUp | INTEGER | False | 斜杆起始端节点 |  |  |
| NodeDw | INTEGER | False | 斜杆终末端节点 |  |  |
| LinkUp | INTEGER | False | 斜杆起始端约束 | EBarRest | 固接,铰接, 滑动，半固接 |
| LinkDW | INTEGER | False | 斜杆终末端约束 | EBarRest | 固接,铰接, 滑动，半固接 |
| RigidUp | REAL | False | 斜杆起始端刚域 |  |  |
| RigidDw | REAL | False | 斜杆终末端刚域 |  |  |
| StiffCoeInf | TEXT | False | 刚度系数 |  | 轴向, 2轴方向剪切, 3轴方向剪切, 抗扭, 绕2轴抗弯, 绕3轴抗弯 |
| StiffReleaseInf | TEXT | False | 刚度释放 |  |  |
| NonLineSign | INTEGER | False | 非线性标识 |  | 0.无非线性 1.单拉 2.单压 |
| LinkTotID | INTEGER | False | 连接对应的斜杆ID |  | 用于判断是否为斜杆定义的连接属性 |
| KZDJ | INTEGER | False | 斜杆抗震等级 |  |  |
| KZDJGZ | INTEGER | False | 斜杆抗震构造措施的抗震等级 |  |  |
| MainBar | INTEGER | False | 斜杆主筋等级 |  |  |
| HoopBar | INTEGER | False | 斜杆箍筋等级 |  |  |
| SeisVCom | INTEGER | False | 是否考虑竖向地震 |  |  |
| ZZZJM | INTEGER | False | 按抗规进行性能设计时的 中震正截面性能水准 |  | 0不考虑 1不屈服 2弹性 3屈服 |
| ZZXJM | INTEGER | False | 按抗规进行性能设计时的 中震斜截面性能水准 |  | 0不考虑 1不屈服 2弹性 3屈服 |
| DZZJM | INTEGER | False | 按抗规进行性能设计时的 大震正截面性能水准 |  | 0不考虑 1不屈服 2弹性 3屈服 |
| DZXJM | INTEGER | False | 按抗规进行性能设计时的 大震斜截面性能水准 |  | 0不考虑 1不屈服 2弹性 3屈服 |
| XNSJEmpSign | INTEGER | False | 按高规进行性能设计时的构件类型 |  | 1:耗能2:普通竖向 3:关键 |
| PMMatType | INTEGER | False | 斜杆材料类型 |  |  |
| ConGrade | REAL | False | 混凝土等级 |  |  |
| SteelKind | INTEGER | False | 钢号 |  |  |
| Cover | REAL | False | 斜杆保护层厚度 |  |  |
| Air | INTEGER | False | 是否是人防构件 |  |  |
| YZ | INTEGER | False |  |  |  |
| EnvSign | INTEGER | False | 是否包络设计斜杆 |  |  |
| DuctLevel | INTEGER | False | 延性等级 |  | 适用欧标、美标 |
| LiveLoadCoe | REAL | False | 斜杆活荷折减系数 |  |  |
| LiveGraCoe | REAL | False | 斜杆活荷重力荷载代表值组合系数 |  |  |
| ReduceCoeInf | TEXT | False | 斜杆自定义工况折减系数 |  |  |
| StruCoe | REAL | False | 结构重要性系数 |  |  |
| EmpCoe | REAL | False | 斜杆重要性系数 |  |  |
| WJType | INTEGER | False | 斜杆的空间结构属性 网架类型 |  | 网架 双层网壳 单层网壳 立体桁架 一般桁架杆件 中心支撑 偏心支撑 门刚支撑 温室大棚 |
| TrussSign | INTEGER | False | 斜杆的空间结构属性 杆件位置 |  | 桁架上弦杆 桁架腹杆 桁架中层弦杆 桁架下弦杆 支座腹杆 温室称重杆件 温室拱杆 温室其他杆件 |
| TrussXID | INTEGER | False |  |  |  |
| TrussYID | INTEGER | False |  |  |  |
| TempInf | TEXT | False | 构件温度 |  | 依次记录 0-升温 1-降温 2-防火升温 |
| FHth | REAL | False | 耐火时间 |  |  |
| FHiqz | INTEGER | False | 膨胀型 |  | 1-非膨胀型 2-水泥砂浆 |
| FHri | REAL | False | 等效热阻/等效热传导系数 |  |  |
| FHdil | REAL | False | 保护层厚度 |  |  |
| FHfxz | REAL | False | 截面形状系数 |  |  |
| HN | INTEGER | False | 是否新钢规性能设计塑性耗能构件 |  |  |
| BTRatioGrade | INTEGER | False | 新钢规性能设计宽厚比 |  |  |
| YXGrade | INTEGER | False | 新钢规性能设计延性等级 |  |  |
| BetaE | REAL | False | 新钢规性能设计非耗能构件系数 |  |  |
| ConGradeIn | REAL | False | 钢骨内混凝土等级 |  |  |
| LenX | REAL | False | MX向计算长度 |  |  |
| LenY | REAL | False | MY向计算长度 |  |  |
| LenCoeX | REAL | False | MX向计算长度系数 |  |  |
| LenCoeY | REAL | False | MY向计算长度系数 |  |  |
| LenCoeXWCY | REAL | False | MX向计算长度系数(无侧移) |  |  |
| LenCoeYWCY | REAL | False | MY向计算长度系数(无侧移) |  |  |
| UpFlrNum | INTEGER | False | 斜杆上方层数 |  |  |
| LinkToZHL | INTEGER | False |  |  |  |
| BK | INTEGER | False |  |  |  |
| Corner | INTEGER | False |  |  |  |
| Tran | INTEGER | False |  |  |  |
| TranHor | INTEGER | False |  |  |  |
| BraceType | INTEGER | False | 支撑类型 |  | 人字支撑，十字交叉支撑 |

preCol
[图]
[图]
[图]
[图]

| preCol |  |  |  |  |  |
|---|---|---|---|---|---|
| 柱计算与设计参数，对应前处理特殊构件定义 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 柱层号 |  |  |
| TowNo | INTEGER | False | 柱塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| FlrID | INTEGER | False | 柱层内编号 |  |  |
| Shell | INTEGER | False |  |  |  |
| Solid | INTEGER | False | 是否按实体单元计算 |  |  |
| PMNo | INTEGER | False | 柱在结构模型中的编号 |  | 负数为地基梁 |
| PMSectNo | INTEGER | False | 柱截面在结构模型中的编号 |  |  |
| NodeUp | INTEGER | False | 柱上端节点 |  |  |
| NodeDw | INTEGER | False | 柱下端节点 |  |  |
| LinkUp | INTEGER | False | 柱上端约束 | EBarRest | 固接,铰接, 滑动，半固接 |
| LinkDW | INTEGER | False | 柱下端约束 | EBarRest | 固接,铰接, 滑动，半固接 |
| RigidUp | REAL | False | 柱起始端刚域 |  |  |
| RigidDw | REAL | False | 柱终末端刚域 |  |  |
| StiffCoeInf | TEXT | False | 刚度系数 |  | 轴向, 2轴方向剪切, 3轴方向剪切, 抗扭, 绕2轴抗弯, 绕3轴抗弯 |
| StiffReleaseInf | TEXT | False | 刚度释放 |  |  |
| KZDJ | INTEGER | False | 柱抗震等级 |  |  |
| KZDJGZ | INTEGER | False | 柱抗震构造措施的抗震等级 |  |  |
| MainBar | INTEGER | False | 柱主筋等级 |  |  |
| HoopBar | INTEGER | False | 柱箍筋等级 |  |  |
| SeisVCom | INTEGER | False | 是否考虑竖向地震 |  |  |
| ZZZJM | INTEGER | False | 按抗规进行性能设计时的 中震正截面性能水准 |  | 0不考虑 1不屈服 2弹性 3屈服 |
| ZZXJM | INTEGER | False | 按抗规进行性能设计时的 中震斜截面性能水准 |  | 0不考虑 1不屈服 2弹性 3屈服 |
| DZZJM | INTEGER | False | 按抗规进行性能设计时的 大震正截面性能水准 |  | 0不考虑 1不屈服 2弹性 3屈服 |
| DZXJM | INTEGER | False | 按抗规进行性能设计时的 大震斜截面性能水准 |  | 0不考虑 1不屈服 2弹性 3屈服 |
| XNSJEmpSign | INTEGER | False | 按高规进行性能设计时的构件类型 |  | 1:耗能2:普通竖向 3:关键 |
| PMMatType | INTEGER | False | 柱材料类型 |  |  |
| ConGrade | REAL | False | 混凝土等级 |  |  |
| SteelKind | INTEGER | False | 钢号 |  |  |
| Cover | REAL | False | 柱保护层厚度 |  |  |
| Air | INTEGER | False | 是否是人防构件 |  |  |
| YZ | INTEGER | False |  |  |  |
| EnvSign | INTEGER | False | 是否包络设计柱 |  |  |
| DuctLevel | INTEGER | False | 延性等级 |  | 适用欧标、美标 |
| LiveLoadCoe | REAL | False | 柱活荷折减系数 |  |  |
| LiveGraCoe | REAL | False | 柱活荷重力荷载代表值组合系数 |  |  |
| ReduceCoeInf | TEXT | False | 柱自定义工况折减系数 |  |  |
| StruCoe | REAL | False | 结构重要性系数 |  |  |
| EmpCoe | REAL | False | 柱重要性系数 |  |  |
| WJType | INTEGER | False | 柱的空间结构属性 网架类型 |  | 网架 双层网壳 单层网壳 立体桁架 一般桁架杆件 中心支撑 偏心支撑 门刚支撑 温室大棚 |
| TrussSign | INTEGER | False | 柱的空间结构属性 杆件位置 |  | 桁架上弦杆 桁架腹杆 桁架中层弦杆 桁架下弦杆 支座腹杆 温室称重杆件 温室拱杆 温室其他杆件 |
| TrussXID | INTEGER | False |  |  |  |
| TrussYID | INTEGER | False |  |  |  |
| TempInf | TEXT | False | 构件温度 |  | 依次记录 0-升温 1-降温 2-防火升温 |
| FHth | REAL | False | 耐火时间 |  |  |
| FHiqz | INTEGER | False | 膨胀型 |  | 1-非膨胀型 2-水泥砂浆 |
| FHri | REAL | False | 等效热阻/等效热传导系数 |  |  |
| FHdil | REAL | False | 保护层厚度 |  |  |
| FHfxz | REAL | False | 截面形状系数 |  |  |
| HN | INTEGER | False | 是否新钢规性能设计塑性耗能构件 |  |  |
| BTRatioGrade | INTEGER | False | 新钢规性能设计宽厚比 |  |  |
| YXGrade | INTEGER | False | 新钢规性能设计延性等级 |  |  |
| BetaE | REAL | False | 新钢规性能设计非耗能构件系数 |  |  |
| ConGradeIn | REAL | False | 钢骨内混凝土等级 |  |  |
| LenX | REAL | False | MX向计算长度 |  |  |
| LenY | REAL | False | MY向计算长度 |  |  |
| LenCoeX | REAL | False | MX向计算长度系数 |  |  |
| LenCoeY | REAL | False | MY向计算长度系数 |  |  |
| LenCoeXWCY | REAL | False | MX向计算长度系数(无侧移) |  |  |
| LenCoeYWCY | REAL | False | MY向计算长度系数(无侧移) |  |  |
| UpFlrNum | INTEGER | False | 柱上方层数 |  |  |
| LinkToZHL | INTEGER | False | 是否与转换梁相连 |  |  |
| BK | INTEGER | False | 是否是边框柱 |  |  |
| Corner | INTEGER | False | 是否是角柱 |  |  |
| Tran | INTEGER | False | 是否是框支柱 |  |  |
| TranHor | INTEGER | False |  |  |  |
| Portal | INTEGER | False | 是否是门刚柱 |  |  |
| PortalKFZ | INTEGER | False |  |  |  |
| ZCZZ | INTEGER | False |  |  |  |
| SeisVCoeX | REAL | False | 柱X向剪力系数 |  |  |
| SeisVCoeY | REAL | False | 柱Y向剪力系数 |  |  |
| ZYBAdd | REAL | False | 轴压比限值增减量 |  |  |

preFlr
[图]

| preFlr |  |  |  |  |  |
|---|---|---|---|---|---|
| 层内包含塔数表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | TEXT | False | 塔号 |  |  |

preFlrTow
[图]

| preFlrTow |  |  |  |  |  |
|---|---|---|---|---|---|
| 层号、塔号及关联关系表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TowUpInf | TEXT | False | 上层关联层号 |  |  |
| TowDwInf | TEXT | False | 下层关联层号 |  |  |
| FlrLevel | REAL | False | 楼层标高 |  |  |
| FlrHei | REAL | False | 楼层高度 |  |  |

preFlrTowProp
[图]
[图]
[图]
[图]

| preFlrTowProp |  |  |  |  |  |
|---|---|---|---|---|---|
| 层塔参数表，主要对应前处理材料表，及楼层属性、塔高等信息 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| Sign_JQC | INTEGER | False | 是否是加强层 |  |  |
| Sign_JQQ | INTEGER | False | 是否是底部加强区 |  |  |
| Sign_Edge | INTEGER | False | 是否设置约束边缘构件 |  |  |
| Sign_EdgeGD | INTEGER | False | 是否设置约束边缘过渡构件 |  |  |
| ConGrade_Beam | REAL | False | 梁混凝土强度等级 |  |  |
| ConGrade_Col | REAL | False | 柱混凝土强度等级 |  |  |
| ConGrade_Brace | REAL | False | 支撑混凝土强度等级 |  |  |
| ConGrade_Wall | REAL | False | 墙混凝土强度等级 |  |  |
| ConGrade_Slab | REAL | False | 板混凝土强度等级 |  |  |
| Steel | INTEGER | False | 钢号 |  |  |
| KZDJ_Con_Beam | INTEGER | False | 主梁抗震等级 |  |  |
| KZDJGZ_Con_Beam | INTEGER | False | 主梁抗震构造等级 |  |  |
| KZDJ_Con_SubBeam | INTEGER | False | 次梁抗震等级 |  |  |
| KZDJGZ_Con_SubBeam | INTEGER | False | 次梁抗震构造等级 |  |  |
| KZDJ_Con_Col | INTEGER | False | 柱抗震等级 |  |  |
| KZDJGZ_Con_Col | INTEGER | False | 柱抗震构造等级 |  |  |
| KZDJ_Con_Brace | INTEGER | False | 斜杆抗震等级 |  |  |
| KZDJGZ_Con_Brace | INTEGER | False | 斜杆抗震构造措施的抗震等级 |  |  |
| KZDJ_Con_Wall | INTEGER | False | 墙抗震等级 |  |  |
| KZDJGZ_Con_Wall | INTEGER | False | 墙抗震构造等级 |  |  |
| KZDJ_Stl_Beam | INTEGER | False | 钢主梁抗震等级 |  |  |
| KZDJGZ_Stl_Beam | INTEGER | False | 钢主梁抗震构造等级 |  |  |
| KZDJ_Stl_SubBeam | INTEGER | False | 钢次梁抗震等级 |  |  |
| KZDJGZ_Stl_SubBeam | INTEGER | False | 钢次梁抗震构造等级 |  |  |
| KZDJ_Stl_Col | INTEGER | False | 钢柱抗震等级 |  |  |
| KZDJGZ_Stl_Col | INTEGER | False | 钢柱抗震构造等级 |  |  |
| KZDJ_Stl_Brace | INTEGER | False | 钢斜杆抗震等级 |  |  |
| KZDJGZ_Stl_Brace | INTEGER | False | 钢斜杆抗震构造等级 |  |  |
| MainBar_Beam | INTEGER | False | 梁主筋 |  |  |
| HoopBar_Beam | INTEGER | False | 梁箍筋 |  |  |
| MainBar_Col | INTEGER | False | 柱主筋 |  |  |
| HoopBar_Col | INTEGER | False | 柱箍筋 |  |  |
| MainBar_Wall | INTEGER | False | 墙主筋 |  |  |
| HoopBar_Wall | INTEGER | False | 边缘构件箍筋 |  |  |
| HorBar_Wall | INTEGER | False | 墙水平筋 |  |  |
| VerBar_Wall | INTEGER | False | 墙分布筋 |  |  |
| VerBarRatio_Wall | REAL | False | 墙竖向分布筋配筋率 |  |  |
| HorBarRatio_Wall | REAL | False | 墙水平分布筋配筋率 |  |  |
| MassInf | TEXT | False | 恒载质量， 活载质量，附加质量 |  |  |
| VertXInf | TEXT | False | 塔多边形范围X坐标 |  |  |
| VertYInf | TEXT | False | 塔多边形范围Y坐标 |  |  |

preLink
[图]

| preLink |  |  |  |  |  |
|---|---|---|---|---|---|
| 连接，对应单点约束、两点约束及支撑定义的连接 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| ComKind | INTEGER | False | 类型 |  | 连接 |
| LinkType | INTEGER | False | 连接类型 |  | 线性 阻尼器麦克斯韦模型 GAP单元 塑性单元 屈曲约束支撑 隔震支座 |
| NodeS | INTEGER |  | 起始节点号 |  | 其中一端为0则为支座节点 |
| NodeE | INTEGER |  | 终末节点号 |  |  |
| BraceID | INTEGER |  | 连接对应的斜杆ID |  | 是否为斜杆定义的连接属性 |

preNode
[图]

| preNode |  |  |  |  |  |
|---|---|---|---|---|---|
| 节点编号、坐标 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | 节点ID |  |  |
| X | REAL | False | 节点X向坐标 |  |  |
| Y | REAL | False | 节点Y向坐标 |  |  |
| Z | REAL | False | 节点Z向坐标 |  |  |
| MassInf | TEXT | False | 节点恒活质量 |  | 恒载质量， 活载质量 |

prePara
[图]

| prePara |  |  |  |  |  |
|---|---|---|---|---|---|
| 前处理参数表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ParaMacro | INTEGER | False | 参数名称 |  |  |
| ParaVal |  | False | 参数值 |  |  |

preSlab
[图]

| preSlab |  |  |  |  |  |
|---|---|---|---|---|---|
| 弹性板计算与设计参数，对应前处理特殊构件定义 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| PMNo | INTEGER | False | 建模房间对应的塔号 |  |  |
| Shell | INTEGER | False | 是否按壳单元计算 |  |  |
| Solid | INTEGER | False | 是否按实体单元计算 |  |  |
| RoundNodeInf | TEXT | False | 弹性板周边节点号 |  |  |
| PMMatType | INTEGER | False | 弹性板材料 |  |  |
| ConGrade | REAL | False | 弹性板混凝土等级 |  |  |
| SteelKind | INTEGER | False | 弹性板钢号 |  |  |
| IsSkin | INTEGER | False | 是否是蒙皮 |  |  |
| Air | INTEGER | False | 是否是人防构件 |  |  |
| IsPlanar | INTEGER | False | 是否按超单元计算 |  |  |
| Prop | INTEGER | False | 计算假定 |  | 0-无板， 1-刚性板， 2-弹性板3， 3-弹性板6， 4-弹性膜； |
| RigidNo | INTEGER | False | 刚性板号 |  |  |

preParaFlr
preSlabPlanar
[图]

| preSlabPlanar |  |  |  |  |  |
|---|---|---|---|---|---|
| 低级板单元划分信息 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| EleInf | TEXT | False | 单元ID |  |  |
| EleNodeInf | TEXT | False | 单元各角点ID |  |  |
| EleTInf | TEXT | False | 单元厚度 |  |  |
| OriginInf | TEXT | False | 单元原点 |  |  |
| CoorXInf | TEXT | False | 单元各角点局部坐标系X |  |  |
| CoorYInf | TEXT | False | 单元各角点局部坐标系Y |  |  |
| CoorZInf | TEXT | False | 单元各角点局部坐标系Z |  |  |

preTowPara
[图]
[图]

| preTowPara |  |  |  |  |  |
|---|---|---|---|---|---|
| 塔参数表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| TowNo | INTEGER | False | 塔号 |  |  |
| JGTX | INTEGER | False | 结构体系 |  |  |
| FlrTran | INTEGER | False | 结构转换层号 |  |  |
| WindPeriodX | REAL | False | 结构X向基本周期 |  |  |
| WindPeriodY | REAL | False | 结构Y向基本周期 |  |  |
| WindSegFlrInf | TEXT | False | 分段号 |  |  |
| WindSegFrontXInf | TEXT | False | X向迎风 |  |  |
| WindSegFrontYInf | TEXT | False | Y向迎风 |  |  |
| WindSegBackXInf | TEXT | False | X向背风 |  |  |
| WindSegBackYInf | TEXT | False | Y向背风 |  |  |
| WindSegSideXInf | TEXT | False | X向侧风 |  |  |
| WindSegSideYInf | TEXT | False | Y向侧风 |  |  |
| WindSegShelterXInf | TEXT | False | X向挡风 |  |  |
| WindSegShelterYInf | TEXT | False | Y向挡风 |  |  |
| V02SegFlrSInf | TEXT | False | 0.20V0调整起始层数 |  |  |
| V02SegFlrEInf | TEXT | False | 0.20V0调整终止层数 |  |  |
| V02BtmVCoe | REAL | False | 0.2V0调整时楼层剪力最小倍数 |  |  |
| V02VfMaxCoe | REAL | False | 0.2V0调整时各层框架剪力最大值的倍数 |  |  |

preWallBeam
[图]
[图]
[图]
[图]

| preWallBeam |  |  |  |  |  |
|---|---|---|---|---|---|
| 墙梁计算与设计参数，对应前处理特殊构件定义 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 墙梁层号 |  |  |
| TowNo | INTEGER | False | 墙梁塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| FlrID | INTEGER | False | 墙梁层内编号 |  |  |
| Shell | INTEGER | False |  |  |  |
| Solid | INTEGER | False | 是否按实体单元计算 |  |  |
| WallEleIDInf | TEXT | False | 墙梁关联的计算模型墙号 |  | 关联墙数, 关联型墙号 |
| PartIDInf | TEXT | False | 超单元ID |  |  |
| PMWallNo | INTEGER | False | 墙梁所属的结构模型墙号 |  |  |
| NodeInf | TEXT | False | 墙梁节点 |  |  |
| IsArc | INTEGER | False | 是否是弧墙梁 |  |  |
| ArcCInf | INTEGER | False | 弧墙梁圆心 |  |  |
| B | REAL | False | 墙梁宽度 |  |  |
| H | REAL | False | 墙梁高度 |  |  |
| HU | REAL | False |  |  |  |
| HD | REAL | False |  |  |  |
| SteelT | REAL | False | 墙梁内钢板宽 |  |  |
| SteelH | REAL | False | 墙梁内钢板高 |  |  |
| SegInf | TEXT |  | 分缝连梁子连梁编号 |  | 负数表示该连梁为子连梁,负数为主连梁编号 正数为主连梁分缝产生的子连梁数量 0表示为不分缝连梁 |
| StiffCoe | REAL | False | 墙梁刚度折减系数 |  |  |
| KZDJ | INTEGER | False | 墙梁抗震等级 |  |  |
| KZDJGZ | INTEGER | False | 墙梁抗震构造措施的抗震等级 |  |  |
| MainBar | INTEGER | False | 墙梁主筋等级 |  |  |
| HoopBar | INTEGER | False | 墙梁箍筋等级 |  |  |
| SeisVCom | INTEGER | False | 是否考虑竖向地震 |  |  |
| ZZZJM | INTEGER | False | 按抗规进行性能设计时的 中震正截面性能水准 |  | 0不考虑 1不屈服 2弹性 3屈服 |
| ZZXJM | INTEGER | False | 按抗规进行性能设计时的 中震斜截面性能水准 |  | 0不考虑 1不屈服 2弹性 3屈服 |
| DZZJM | INTEGER | False | 按抗规进行性能设计时的 大震正截面性能水准 |  | 0不考虑 1不屈服 2弹性 3屈服 |
| DZXJM | INTEGER | False | 按抗规进行性能设计时的 大震斜截面性能水准 |  | 0不考虑 1不屈服 2弹性 3屈服 |
| XNSJEmpSign | INTEGER | False | 按高规进行性能设计时的构件类型 |  | 1:耗能2:普通竖向 3:关键 |
| PMMatType | INTEGER | False | 墙梁材料类型 |  |  |
| ConGrade | REAL | False | 混凝土等级 |  |  |
| SteelKind | INTEGER | False | 钢号 |  |  |
| Cover | REAL | False | 墙梁保护层厚度 |  |  |
| Air | INTEGER | False | 是否是人防构件 |  |  |
| YZ | INTEGER | False |  |  |  |
| EnvSign | INTEGER | False | 是否包络设计墙梁 |  |  |
| DuctLevel | INTEGER | False | 延性等级 |  | 适用欧标、美标 |
| LiveLoadCoe | REAL | False | 墙梁活荷折减系数 |  |  |
| LiveGraCoe | REAL | False | 墙梁活荷重力荷载代表值组合系数 |  |  |
| ReduceCoeInf | TEXT | False | 墙梁自定义工况折减系数 |  |  |
| StruCoe | REAL | False | 结构重要性系数 |  |  |
| EmpCoe | REAL | False | 墙梁重要性系数 |  |  |
| XJKind | INTEGER | False | 斜筋类型 |  | 不设置斜筋 交叉斜筋 对角斜筋 对角暗撑 |

preWallCol
[图]
[图]
[图]
[图]

| preWallCol |  |  |  |  |  |
|---|---|---|---|---|---|
| 墙柱计算与设计参数，对应前处理特殊构件定义 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 墙柱层号 |  |  |
| TowNo | INTEGER | False | 墙柱塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| FlrID | INTEGER | False | 墙柱层内编号 |  |  |
| Shell | INTEGER | False |  |  |  |
| Solid | INTEGER | False | 是否按实体单元计算 |  |  |
| WallEleIDInf | TEXT | False | 墙柱关联的计算模型墙号 |  | 关联墙数, 关联型墙号 |
| WallElePosInf | TEXT | False |  |  |  |
| PartIDInf | TEXT | False | 超单元ID |  |  |
| PMWallNoInf | TEXT | False | 墙柱关联的结构模型墙号 |  | 关联墙数, 关联型墙号 |
| PMWallPosInf | TEXT | False |  |  |  |
| NodeUpInf | TEXT | False | 墙柱上节点 |  | 节点数，节点 |
| NodeDwInf | TEXT | False | 墙柱下节点 |  | 节点数，节点 |
| IsArc | INTEGER | False | 是否是弧墙柱 |  |  |
| ArcCInf | INTEGER | False | 弧墙柱圆心 |  |  |
| B | REAL | False | 墙柱宽度 |  |  |
| H | REAL | False | 墙柱高度 |  |  |
| L | REAL | False | 墙柱竖向高度 |  |  |
| CalL | REAL | False | 墙柱计算高度 |  |  |
| SteelT | REAL | False | 墙柱内钢板宽 |  |  |
| LKQ | INTEGER | False | 是否是临空墙 |  |  |
| LKQLoad | REAL | False | 临空墙荷载 |  |  |
| CreepCoe | REAL | False |  |  |  |
| StiffCoe | REAL | False | 墙柱刚度折减系数 |  |  |
| StiffCoe_MW | REAL | False |  |  |  |
| KZDJ | INTEGER | False | 墙柱抗震等级 |  |  |
| KZDJGZ | INTEGER | False | 墙柱抗震构造措施的抗震等级 |  |  |
| MainBar | INTEGER | False | 墙柱主筋等级 |  |  |
| HoopBar | INTEGER | False | 墙柱箍筋等级 |  |  |
| SeisVCom | INTEGER | False | 是否考虑竖向地震 |  |  |
| ZZZJM | INTEGER | False | 按抗规进行性能设计时的 中震正截面性能水准 |  | 0不考虑 1不屈服 2弹性 3屈服 |
| ZZXJM | INTEGER | False | 按抗规进行性能设计时的 中震斜截面性能水准 |  | 0不考虑 1不屈服 2弹性 3屈服 |
| DZZJM | INTEGER | False | 按抗规进行性能设计时的 大震正截面性能水准 |  | 0不考虑 1不屈服 2弹性 3屈服 |
| DZXJM | INTEGER | False | 按抗规进行性能设计时的 大震斜截面性能水准 |  | 0不考虑 1不屈服 2弹性 3屈服 |
| XNSJEmpSign | INTEGER | False | 按高规进行性能设计时的构件类型 |  | 1:耗能2:普通竖向 3:关键 |
| PMMatType | INTEGER | False | 墙柱材料类型 |  |  |
| ConGrade | REAL | False | 混凝土等级 |  |  |
| SteelKind | INTEGER | False | 钢号 |  |  |
| Cover | REAL | False | 墙柱保护层厚度 |  |  |
| Air | INTEGER | False | 是否是人防构件 |  |  |
| YZ | INTEGER | False |  |  |  |
| EnvSign | INTEGER | False | 是否包络设计墙柱 |  |  |
| DuctLevel | INTEGER | False | 延性等级 |  | 适用欧标、美标 |
| LiveLoadCoe | REAL | False | 墙柱活荷折减系数 |  |  |
| LiveGraCoe | REAL | False | 墙柱活荷重力荷载代表值组合系数 |  |  |
| ReduceCoeInf | TEXT | False | 墙柱自定义工况折减系数 |  |  |
| StruCoe | REAL | False | 结构重要性系数 |  |  |
| EmpCoe | REAL | False | 墙柱重要性系数 |  |  |
| UpFlrNum | INTEGER | False | 墙柱上方层数 |  |  |
| VerBarKind | INTEGER | False | 墙柱竖向分布筋等级 |  |  |
| BaseWall | INTEGER | False |  |  |  |
| DZ | INTEGER | False |  |  |  |
| SZ | INTEGER | False |  |  |  |
| Buckling | INTEGER | False |  |  |  |
| AsVRatio | REAL | False | 墙柱竖向分布筋配筋率 |  |  |
| AsHMinRatio | REAL | False | 墙柱水平分布筋配筋率 |  |  |
| HasMWHZ | INTEGER | False | 墙柱是否有面外荷载 |  |  |
| DesignMW | INTEGER | False | 是否进行面外设计 |  |  |

计算CAL系列
calBuckling
[图]

| calBuckling |  |  |  |  |  |
|---|---|---|---|---|---|
| 屈曲分析 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ModuleID | INTEGER | False | 计算模型 |  |  |
| BucklingEigenNo | INTEGER | False | 屈曲特征值编号 |  |  |
| Value | REAL | False | 屈曲特征值 |  |  |
| Prc | REAL | False | Pcr因子 |  |  |

calBucklingDisp
[图]

| calBucklingDisp |  |  |  |  |  |
|---|---|---|---|---|---|
| 屈曲分析特征向量 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ModuleID | INTEGER | False | 计算模型 |  |  |
| BucklingEigenNo | INTEGER | False | 屈曲特征值编号 |  |  |
| NodeID | INTEGER | False | 节点号 |  |  |
| DisInf | TEXT | False | 模态下节点特征向量 |  | 分别为DX,DY,DZ,RX,RY,RZ |

calCoord_Frame
[图]

| calCoord_Frame |  |  |  |  |  |
|---|---|---|---|---|---|
| 构件局部坐标系 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ModuleID | INTEGER | False | 计算模型 |  |  |
| ComKind | INTEGER | False | 构件类型 |  |  |
| ComID | INTEGER | False | 构件编号 |  |  |
| CoorXInf | TEXT | False | X方向向量 |  |  |
| CoorYInf | TEXT | False | Y方向向量 |  |  |
| CoorZInf | TEXT | False | Z方向向量 |  |  |

calCoord_WallBeam
[图]

| calCoord_WallBeam |  |  |  |  |  |
|---|---|---|---|---|---|
| 墙梁构件局部坐标系 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ModuleID | INTEGER | False | 计算模型 |  |  |
| ComKind | INTEGER | False | 构件类型 |  |  |
| ComID | INTEGER | False | 构件编号 |  |  |
| CoorXInf | TEXT | False | X方向向量 |  |  |
| CoorYInf | TEXT | False | Y方向向量 |  |  |
| CoorZInf | TEXT | False | Z方向向量 |  |  |

calCoord_WallCol
[图]

| calCoord_WallCol |  |  |  |  |  |
|---|---|---|---|---|---|
| 墙柱构件局部坐标系 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ModuleID | INTEGER | False | 计算模型 |  |  |
| ComKind | INTEGER | False | 构件类型 |  |  |
| ComID | INTEGER | False | 构件编号 |  |  |
| CoorXInf | TEXT | False | X方向向量 |  |  |
| CoorYInf | TEXT | False | Y方向向量 |  |  |
| CoorZInf | TEXT | False | Z方向向量 |  |  |

calEigenInf
[图]

| calEigenInf |  |  |  |  |  |
|---|---|---|---|---|---|
| 振型总体信息 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ModuleID | INTEGER | False | 计算模型 |  |  |
| EigenNo | INTEGER | False | 振型编号 |  |  |
| Period | REAL | False | 振型周期 |  |  |
| Angle | REAL | False | 振型转角 |  |  |
| CoeffInf | TEXT | False | 各振型质量 |  | 分为X/Y/Z平动，RX/RY/RZ扭转系数 |
| mInf | TEXT | False | 各振型参与质量 |  |  |

calFlrInf
[图]

| calFlrInf |  |  |  |  |  |
|---|---|---|---|---|---|
| 各楼层质心/刚心数据 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| ModuleID | INTEGER | False | 计算模型 |  |  |
| McInf | TEXT | False | 质心坐标 |  |  |
| ScInf | TEXT | False | 刚心坐标 |  |  |
| StiffInf | TEXT | False | 剪弯刚度 |  | 分为X/Y/RZ |
| EccInf | TEXT | False | 偏心率 |  | ecc_x,ecc_y |
| Alpha | REAL | False | 刚性主轴的方向(角度) |  |  |

calForce_BtmShear
[图]

| calForce_BtmShear |  |  |  |  |  |
|---|---|---|---|---|---|
| 底部剪力法下各层地震作用标准值 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| ModuleID | INTEGER | False | 计算模型 |  |  |
| LDCaseCalID | INTEGER | False | 地震工况 |  |  |
| ForceInf | TEXT | False | 对应层塔的底部剪力值 |  |  |

calForce_Frame
[图]

| calForce_Frame |  |  |  |  |  |
|---|---|---|---|---|---|
| 框架内力 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ModuleID | INTEGER | False | 计算模型 |  |  |
| LDCaseCalID | INTEGER | False | 工况编号 |  |  |
| ComKind | INTEGER | False | 构件类型 |  |  |
| ComID | INTEGER | False | 构件编号 |  |  |
| Sect | INTEGER | False | 构件计算的断面 |  | 柱（2），梁（2+9） |
| ForceInf | TEXT | False | 对应工况下各断面的内力 |  | 构件局部坐标系下的F1,F2,F3,M1,M2,M3 |

calForce_Link
[图]

| calForce_Link |  |  |  |  |  |
|---|---|---|---|---|---|
| 连接弹簧内力 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ModuleID | INTEGER | False | 计算模型 |  |  |
| LDCaseCalID | INTEGER | False | 工况编号 |  |  |
| ComKind | INTEGER | False | 构件类型 |  |  |
| ComID | INTEGER | False | 构件编号 |  |  |
| Sect | INTEGER | False | 构件计算的断面 |  | 柱（2），梁（2+9） |
| ForceInf | TEXT | False | 对应工况下各断面的内力 |  | 构件局部坐标系下的F1,F2,F3,M1,M2,M3 |

calForce_RibBeam
[图]

| calForce_RibBeam |  |  |  |  |  |
|---|---|---|---|---|---|
| 肋梁内力 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| LDCaseCalID | INTEGER | False | 构件类型 |  |  |
| ComID | INTEGER | False | 构件编号 |  |  |
| Sect | INTEGER | False | 构件计算的断面 |  | 梁（2+9） |
| ForceInf | TEXT | False | 对应工况下各断面的内力 |  | 构件局部坐标系下的F1,F2,F3,M1,M2,M3 |

calForce_SpectrumFrameEigen
[图]

| calForce_SpectrumFrameEigen |  |  |  |  |  |
|---|---|---|---|---|---|
| 框架构件的反应谱工况下某振型下内力 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ModuleID | INTEGER | False | 计算模型 |  |  |
| LDCaseCalID | INTEGER | False | 工况编号 |  |  |
| ComKind | INTEGER | False | 构件类型 |  |  |
| ComID | INTEGER | False | 构件编号 |  |  |
| EigenNo | INTEGER | False | 振型编号 |  |  |
| Sect | INTEGER | False | 构件计算的断面 |  | 柱（2），梁（2+9） |
| ForceInf | TEXT | False | 对应工况下各断面的内力 |  | 构件局部坐标系下的F1,F2,F3,M1,M2,M3 |

calForce_SpectrumLayerCQC
[图]

| calForce_SpectrumLayerCQC |  |  |  |  |  |
|---|---|---|---|---|---|
| 地震工况下层地震外力 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 楼层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| ModuleID | INTEGER | False | 计算模型 |  |  |
| LDCaseCalID | INTEGER | False | 工况编号 |  |  |
| ForceInf | TEXT | False | 对应工况下层地震外力 |  | 分为FX,FY,FZ,RX,RY,RZ |

calForce_SpectrumLayerEigen
[图]

| calForce_SpectrumLayerEigen |  |  |  |  |  |
|---|---|---|---|---|---|
| 反应谱工况下某层的某振型的地震外力 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 楼层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| ModuleID | INTEGER | False | 计算模型 |  |  |
| LDCaseCalID | INTEGER | False | 工况编号 |  |  |
| EigenNo | INTEGER | False | 振型编号 |  |  |
| ForceInf | TEXT | False | 应反应谱工况下的层地震外力 |  | 分为FX,FY,FZ,RX,RY,RZ |

calForce_Spring
[图]

| calForce_Spring |  |  |  |  |  |
|---|---|---|---|---|---|
| 弹簧内力 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ModuleID | INTEGER | False | 计算模型 |  |  |
| LDCaseCalID | INTEGER | False | 工况编号 |  |  |
| ComID | INTEGER | False | 构件编号 |  |  |
| ForceInf | TEXT | False | 对应工况下各断面的内力 |  | 构件局部坐标系下的F1,F2,F3,M1,M2,M3 |

calForce_SubBeam
[图]

| calForce_SubBeam |  |  |  |  |  |
|---|---|---|---|---|---|
| 次梁内力 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| LDCaseCalID | INTEGER | False | 工况编号 |  |  |
| ComID | INTEGER | False | 构件编号 |  |  |
| Sect | INTEGER | False | 构件计算的断面 |  | 梁（2+9） |
| ForceInf | TEXT | False | 对应工况下各断面的内力 |  | 构件局部坐标系下的F1,F2,F3,M1,M2,M3 |

calForce_WallBeam
[图]

| calForce_WallBeam |  |  |  |  |  |
|---|---|---|---|---|---|
| 墙梁内力 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ModuleID | INTEGER | False | 计算模型 |  |  |
| LDCaseCalID | INTEGER | False | 工况编号 |  |  |
| ComKind | INTEGER | False | 构件类型 |  |  |
| ComID | INTEGER | False | 构件编号 |  |  |
| Sect | INTEGER | False | 构件计算的断面 |  |  |
| ForceInf | TEXT | False | 对应工况下各断面的内力 |  | 分为FX,FY,FZ,RX,RY,RZ |

calForce_WallCol
[图]

| calForce_WallCol |  |  |  |  |  |
|---|---|---|---|---|---|
| 墙柱内力 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ModuleID | INTEGER | False | 计算模型 |  |  |
| LDCaseCalID | INTEGER | False | 工况编号 |  |  |
| ComKind | INTEGER | False | 构件类型 |  |  |
| ComID | INTEGER | False | 构件编号 |  |  |
| Sect | INTEGER | False | 构件计算的断面 |  |  |
| ForceInf | TEXT | False | 对应工况下各断面的内力 |  | 分为FX,FY,FZ,RX,RY,RZ |

calGlobalInf
[图]

| calGlobalInf |  |  |  |  |  |
|---|---|---|---|---|---|
| 总体信息 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ModuleID | INTEGER | False | 计算模型 |  |  |
| StaticLDCaseNum | INTEGER | False | 静力工况数目 |  |  |
| EigenNum | INTEGER | False | 振型数 |  |  |
| SeisLDCaseNum | INTEGER | False | 地震工况数 |  |  |
| SpectrumEigenNum | INTEGER | False | 反应谱所用振型数 |  |  |
| NodeNum | INTEGER | False | 节点数 |  |  |
| FrameNum | INTEGER | False | 框架单元数 |  |  |
| MaxAngle | REAL | False | 最大地震方向 |  |  |
| CqcCoeInf | TEXT | False | CQC组合系数 |  | 振型数量 + CQC系数 |

calLDCaseInf
[图]

| calLDCaseInf |  |  |  |  |  |
|---|---|---|---|---|---|
| 工况信息 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ModuleID | INTEGER | False | 计算模型 |  |  |
| LDCaseCalID | INTEGER | False | 荷载工况ID |  |  |
| Type | TEXT | False | 工况类型 |  |  |
| Name | TEXT | False | 工况名称 |  |  |

calLink
[图]
calLocalVibrationInfo
[图]
calModuleIndex
[图]

| calModuleIndex |  |  |  |  |  |
|---|---|---|---|---|---|
| 计算模型信息 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ModuleID | INTEGER | False | 计算模型 |  |  |
| ModuleExplain | TEXT | False | 模型说明 |  |  |

calNodeDisp
[图]

| calNodeDisp |  |  |  |  |  |
|---|---|---|---|---|---|
| 静力工况下的节点位移 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ModuleID | INTEGER | False | 计算模型 |  |  |
| LDCaseCalID | INTEGER | False | 工况编号 |  |  |
| NodeID | INTEGER | False | 节点号 |  |  |
| DisInf | TEXT | False | 节点位移 |  | 分别为DX,DY,DZ,RX,RY,RZ |

calNodeDisp_Eigen
[图]

| calNodeDisp_Eigen |  |  |  |  |  |
|---|---|---|---|---|---|
| 振型的节点特征向量 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ModuleID | INTEGER | False | 计算模型 |  |  |
| EigenNo | INTEGER | False | 振型编号 |  |  |
| NodeID | INTEGER | False | 节点号 |  |  |
| DisInf | TEXT | False | 对应振型下节点特征向量 |  | 分别为DX,DY,DZ,RX,RY,RZ |

calNodeDisp_EigenOfLoadcase
[图]

| calNodeDisp_EigenOfLoadcase |  |  |  |  |  |
|---|---|---|---|---|---|
| 工况下的振型的节点特征向量 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ModuleID | INTEGER | False | 计算模型 |  |  |
| LDCaseCalID | INTEGER | False | 工况编号 |  |  |
| EigenNo | INTEGER | False | 振型编号 |  |  |
| NodeID | INTEGER | False | 节点号 |  |  |
| DisInf | TEXT | False | 对应振型下节点特征向量 |  | 分别为DX,DY,DZ,RX,RY,RZ |

calPart
[图]
[图]

| calPart |  |  |  |  |  |
|---|---|---|---|---|---|
| 面单元数据 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ModuleID | INTEGER | False | 计算模型 |  |  |
| PartCategory | INTEGER | False | 单元类型 |  |  |
| PartID | INTEGER | False | 面单元编号 |  |  |
| EleInf | TEXT | False | 各单元节点数量 |  | 子单元数量+各子单元类型 |
| EleNodeInf | TEXT | False | 各单元节点序号 |  |  |
| EleTypeInf | TEXT | False | 各子单元类型 |  |  |
| NodeNum | INTEGER | False | 单元节点数量 |  |  |
| NodeFlagInf | TEXT | False | 单元节点信息 |  | 超单元节点数量+ 节点标记 <0:外部节点2:内部节点3:高斯点4:中心点 |
| NodeXYZInf | TEXT | False | 单元节点坐标 |  | 节点整体坐标系 |
| GuassEleInf | TEXT | False | 各单元高斯点数量 |  |  |
| GuassEleNodeInf | TEXT | False | 各单元高斯点序号 |  |  |
| NodeCenterInf | TEXT | False | 单元中心节点信息 |  | 中心数量+ 各子单元中心点编号 |
| EleTInf | TEXT | False | 面单元厚度 |  | 子单元数量+ 各子单元厚度 |
| OriginInf | TEXT | False | 局部坐标系原点 |  |  |
| CoorXInf | TEXT | False | 局部坐标系x轴 |  |  |
| CoorYInf | TEXT | False | 局部坐标系y轴 |  |  |
| CoorZInf | TEXT | False | 局部坐标系z轴 |  |  |

calPartDis
[图]

| calPartDis |  |  |  |  |  |
|---|---|---|---|---|---|
| 面单元位移数据 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ModuleID | INTEGER | False | 计算模型 |  |  |
| PartCategory | INTEGER | False | 单元类别 |  |  |
| PartID | INTEGER | False | 超单元编号 |  |  |
| AnalysisID | INTEGER | False | 工况号 |  |  |
| PartNodeID | INTEGER | False | 单元编号 |  |  |
| NodeDisInf | TEXT | False | 各节点位移 |  | 分别为DX,DY,DZ,RX,RY,RZ |

calPartNL
[图]

| calPartNL |  |  |  |  |  |
|---|---|---|---|---|---|
| 面单元应力、内力数据 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ModuleID | INTEGER | False | 计算模型 |  |  |
| PartCategory | INTEGER | False | 单元类别 |  |  |
| PartID | INTEGER | False | 超单元编号 |  |  |
| AnalysisID | INTEGER | False | 工况号 |  |  |
| PartNodeID | INTEGER | False | 节点号 |  |  |
| NodeStressUInf | TEXT | False | 单元的各节点板顶应力 |  | Sig-xx：坐标系X轴方向的轴向应力。 Sig-yy：坐标系Y轴方向的轴向应力。 Sig-zz：坐标系Z轴方向的轴向应力。 Sig-xy：坐标系X-Y平面内的剪应力。 Sig-yz：坐标系Y-Z平面内的剪应力。 Sig-xz：坐标系X-Z平面内的剪应力。 Sig-max：最大主应力。 Sig-min：最小主应力。 Sig-eff：有效应力(von-Mises 应力)。 Max-Shear: 最大剪切应力 |
| NodeStressMInf | TEXT | False | 单元的各节点板顶、板底应力 |  |  |
| NodeStressDInf | TEXT | False | 单元的各节点板底应力 |  |  |
| NodeNLInf | TEXT | False | 单元的各节点内力 |  | Fxx：作用在与局部坐标系x轴垂直平面内，单元局部坐标系x轴方向上单位宽度轴力。 Fyy：作用在与局部坐标系y轴垂直平面内，单元局部坐标系y轴方向上单位宽度轴力。 Fxy：单元局部坐标系的x-y平面内(平面内受剪)单位宽度剪力(Fxy=Fyx)。 Fmax：单位宽度最大主轴力。 Fmin：单位宽度最小主轴力。 Mxx：作用在与局部坐标系x轴垂直平面内，绕y轴旋转的单位宽度弯矩(绕局部坐标系y轴的平面外弯矩)。 Myy：作用在与局部坐标系y轴垂直平面内，绕x轴旋转的单位宽度弯矩(绕局部坐标系x轴的平面外弯矩)。 Mxy：作用在与局部坐标系x轴垂直平面内，绕x轴旋转的单位宽度扭矩(Mxy=Myx)。 Mmax：单位宽度的最大主弯矩。 Mmin：单位宽度的最大小弯矩。 Vxx：作用在与局部坐标系x轴垂直平面内，沿单元局部坐标系z轴(厚度)方向上单位宽度的剪力。 Vyy：作用在与局部坐标系y轴垂直平面内，沿单元局部坐标系z轴(厚度)方向上单位宽度的剪力。 |

calReaction
[图]
calTransFlrStiff
[图]

| calTransFlrStiff |  |  |  |  |  |
|---|---|---|---|---|---|
| 转换层上下的剪弯刚度 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| TowNo | INTEGER | False | 塔号 |  |  |
| ModuleID | INTEGER | False | 计算模型 |  |  |
| Type | INTEGER | False | 层位置 |  | 1：转换层以上  -1：转换层以下 |
| StiffInf | TEXT | False | 弯剪刚度 |  | X,Y,RZ |
| h | REAL | False | 层高 |  |  |
| FlrInf | TEXT | False | 楼层信息 |  | 楼层数 + 楼层号 |

设计DSN系列
通用参数
dsnConfig
[图]

| dsnConfig |  |  |  |  |  |
|---|---|---|---|---|---|
| 数据库信息 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| Name | TEXT | False | 名称 |  |  |
| Value | TEXT | False | 数值 |  |  |

dsnLDCase

| dsnLDCase |  |  |  |  |  |
|---|---|---|---|---|---|
| 工况信息 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | 工况ID |  |  |
| IDOld | INTEGER | False | 工况ID-旧 |  |  |
| LDCaseCalID | INTEGER | False | 工况ID-计算 |  |  |
| LoadKind | INTEGER | False | 工况类型 | YJKDSN::ELDK | 恒载 活载 风载 水平地震 竖向地震 等等 |
| LoadType | INTEGER | False | 工况方向类型 | YJKDSN::ELDType | 水平 水平 竖向 其它 |
| Ang | REAL | False | 水平工况夹角 |  |  |
| Name | TEXT | False | 工况名称 |  |  |
| NameEN | TEXT | False | 工况名称-英文 |  |  |
| NameJH | TEXT | False | 工况名称-简写 |  |  |
| XFC | INTEGER | False | 消防车标记 |  |  |
| Source | INTEGER | False | 工况来源 |  | 1-基本工况 2-建模自定义工况 3-基础工况 4-组合梁施工工况 |
| PMLDType | INTEGER | False | 建模自定义工况类型 |  |  |
| NonLineSign | INTEGER | False | 非线性标记 |  |  |
| MassCoe | REAL | False | 地震计算时的质量折减系数 |  |  |
| ColLiveCoeSign | INTEGER | False | 柱、墙活荷载折减系数标识 |  | 0-同参数设置 1-自定义 |
| ColLiveCoe | REAL | False | 柱、墙活荷载折减系数 |  |  |
| BeamLiveCoeSign | INTEGER | False | 梁活荷载折减系数标识 |  | 0-同参数设置 1-自定义 |
| BeamLiveCoe | REAL | False | 梁活荷载折减系数 |  |  |
| SubBeamLiveCoe | REAL | False | 次梁活荷载折减系数 |  |  |
| SafeCoeMax | REAL | False | 分项系数-非地震不利 |  |  |
| SafeCoeMin | REAL | False | 分项系数-非地震有利 |  |  |
| SafeCoeMax_Seis | REAL | False | 分项系数-地震不利 |  |  |
| SafeCoeMin_Seis | REAL | False | 分项系数-地震有利 |  |  |
| SafeCoeMax_Air | REAL | False | 分项系数-人防不利 |  |  |
| SafeCoeMin_Air | REAL | False | 分项系数-人防有利 |  |  |
| CombCoe | REAL | False | 组合系数-非地震 |  |  |
| CombCoe_Seis | REAL | False | 组合系数-地震 |  |  |
| CombCoe_Air | REAL | False | 组合系数-人防 |  |  |
| FrequentCoe | REAL | False | 组合系数-频域组合 |  |  |
| QuasiCoe | REAL | False | 组合系数-准永久组合 |  |  |

dsnLDCombCom

| dsnLDCombCom |  |  |  |  |  |
|---|---|---|---|---|---|
| 荷载组合表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| ComKind | INTEGER | False | 构件类型 |  |  |
| ComTotID | INTEGER | False | 构件ID |  |  |
| dsnType | INTEGER | False | 设计类型 |  | 正截面设计 斜截面设计 |
| LDCombKind | INTEGER | False | 荷载组合类别 |  | 非地震组合 地震组合 人防组合 |
| LDCombType | INTEGER | False | 荷载组合类别 |  | 基本组合 标准组合 准永久组合 |
| LDCombID | INTEGER | False | 荷载组合ID |  |  |
| LDCombIDDetail | INTEGER | False | 荷载组合详细编号 |  |  |
| Sign | INTEGER | False | 标记 |  | 1-采用基本工况宏定义的组合 2-全工况组合 |
| NonLineSign | INTEGER | False | 非线性标记 |  |  |
| CoeInf | TEXT | False | 荷载分项系数 |  |  |

dsnLDCombJH

| dsnLDCombJH |  |  |  |  |  |
|---|---|---|---|---|---|
| 通用荷载组合表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| dsnType | INTEGER | False | 设计类型 |  | 正截面设计 斜截面设计 |
| LDCombKind | INTEGER | False | 荷载组合类别 |  | 非地震组合 地震组合 人防组合 |
| LDCombType | INTEGER | False | 荷载组合类别 |  | 基本组合 标准组合 准永久组合 |
| LDCombID | INTEGER | False | 荷载组合ID |  |  |
| LDCombIDDetail | INTEGER | False | 荷载组合详细编号 |  |  |
| Sign | INTEGER | False | 标记 |  | 1-采用基本工况宏定义的组合 2-全工况组合 |
| NonLineSign | INTEGER | False | 非线性标记 |  |  |
| CoeInf | TEXT | False | 荷载分项系数 |  |  |

整体指标
dsnStatFlrData
[图]

| dsnStatFlrData |  |  |  |  |  |
|---|---|---|---|---|---|
| 楼层相关基本数据表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| NDead | REAL | False | 恒载轴力 |  |  |
| NLive | REAL | False | 活载轴力 |  |  |
| StiffShearDisXInf | TEXT | False | X向层剪力与位移的比计算出来的层刚度 |  |  |
| StiffShearDisYInf | TEXT | False | Y向层剪力与位移的比计算出来的层刚度 |  |  |
| StiffShearCutXInf | TEXT | False | X向层剪切刚度 |  |  |
| StiffShearCutYInf | TEXT | False | Y向层剪切刚度 |  |  |
| StiffBendXInf | TEXT | False | X向层剪弯刚度，已考虑层高 |  |  |
| StiffBendYInf | TEXT | False | Y向层剪弯刚度，已考虑层高 |  |  |
| CZLXInf | TEXT | False | X向楼层承载力 |  |  |
| CZLYInf | TEXT | False | Y向楼层承载力 |  |  |
| CZLStlColNCZL_WCYX | REAL | False | 钢柱按无侧移计算长度系数计算得到的轴向承载力 |  |  |
| CZLStlColNCZL_WCYY | REAL | False | 钢柱按无侧移计算长度系数计算得到的轴向承载力 |  |  |
| CZLStlColNCZL_YCYX | REAL | False | 钢柱按有侧移计算长度系数计算得到的轴向承载力 |  |  |
| CZLStlColNCZL_YCYY | REAL | False | 钢柱按有侧移计算长度系数计算得到的轴向承载力 |  |  |
| CZLBraceStrenX | INTEGER | False | X向强、弱支撑标志 |  |  |
| CZLBraceStrenY | INTEGER | False | Y向强、弱支撑标志 |  |  |
| FlrFXInf | TEXT | False | X向层地震外力 |  |  |
| FlrFYInf | TEXT | False | Y向层地震外力 |  |  |
| FlrVXInf | TEXT | False | X向层地震剪力 |  |  |
| FlrVYInf | TEXT | False | Y向层地震剪力 |  |  |
| FlrMXInf | TEXT | False | X向层地震倾覆弯矩 |  |  |
| FlrMYInf | TEXT | False | Y向层地震倾覆弯矩 |  |  |
| FlrVXByComInf | TEXT | False | 按内力统计得到的X向层地震剪力 |  |  |
| FlrVYByComInf | TEXT | False | 按内力统计得到的Y向层地震剪力 |  |  |
| FlrWindFInf | TEXT | False | 顺风向外力 |  | 包含基本风和多方向风，数值+4 |
| FlrWindFHInf | TEXT | False | 横风向外力 |  | 包含基本风和多方向风，数值+4 |
| FlrWindVInf | TEXT | False | 顺风向剪力 |  | 包含基本风和多方向风，数值+4 |
| FlrWindVHInf | TEXT | False | 横风向剪力 |  | 包含基本风和多方向风，数值+4 |
| FlrWindMInf | TEXT | False | 顺风向倾覆弯矩 |  | 包含基本风和多方向风，数值+4 |
| FlrWindMHInf | TEXT | False | 横风向倾覆弯矩 |  | 包含基本风和多方向风，数值+4 |
| MRFX_AppInf | TEXT | False | X向MR模型规定水平力时的层地震外力 |  |  |
| MRFY_AppInf | TEXT | False | Y向MR模型规定水平力时的层地震外力 |  |  |
| MRFFX_AppInf | TEXT | False | X向MRF模型规定水平力时的层地震外力 |  |  |
| MRFFY_AppInf | TEXT | False | Y向MRF模型规定水平力时的层地震外力 |  |  |
| SColXInf | TEXT | False | 普通柱X向地震剪力 |  | 按内力统计，不包含框支柱，不一定满足0.2V0调整需求 |
| SColYInf | TEXT | False | 普通柱Y向地震剪力 |  | 按内力统计，不包含框支柱，不一定满足0.2V0调整需求 |
| SColKZZXInf | TEXT | False | 框支柱X向地震剪力 |  | 按内力统计 |
| SColKZZYInf | TEXT | False | 框支柱Y向地震剪力 |  | 按内力统计 |
| SBraceXInf | TEXT | False | 支撑X向地震剪力 |  | 按内力统计 |
| SBraceYInf | TEXT | False | 支撑Y向地震剪力 |  | 按内力统计 |
| SSLegWallXInf | TEXT | False | 短肢墙X向剪力 |  | 按内力统计 |
| SSLegWallYInf | TEXT | False | 短肢墙Y向剪力 |  | 按内力统计 |
| SWallXInf | TEXT | False | 墙X向地震剪力 |  | 按内力统计，不包含短肢墙 |
| SWallYInf | TEXT | False | 墙Y向地震剪力 |  | 按内力统计，不包含短肢墙 |
| SColX_ABSInf | TEXT | False | 普通柱X向地震剪力 |  | 按内力统计并取绝对值叠加，不包含框支柱，不一定满足0.2V0调整需求 |
| SColY_ABSInf | TEXT | False | 普通柱Y向地震剪力 |  | 按内力统计并取绝对值叠加，不包含框支柱，不一定满足0.2V0调整需求 |
| SColKZZX_ABSInf | TEXT | False | 框支柱X向地震剪力 |  | 按内力统计并取绝对值叠加 |
| SColKZZY_ABSInf | TEXT | False | 框支柱Y向地震剪力 |  | 按内力统计并取绝对值叠加 |
| SBraceX_ABSInf | TEXT | False | 支撑X向地震剪力 |  | 按内力统计并取绝对值叠加 |
| SBraceY_ABSInf | TEXT | False | 支撑Y向地震剪力 |  | 按内力统计并取绝对值叠加 |
| SSLegWallX_ABSInf | TEXT | False | 短肢墙X向剪力 |  | 按内力统计并取绝对值叠加 |
| SSLegWallY_ABSInf | TEXT | False | 短肢墙Y向剪力 |  | 按内力统计并取绝对值叠加 |
| SWallX_ABSInf | TEXT | False | 墙X向地震剪力 |  | 按内力统计并取绝对值叠加，不包含短肢墙 |
| SWallY_ABSInf | TEXT | False | 墙Y向地震剪力 |  | 按内力统计并取绝对值叠加，不包含短肢墙 |
| SColX_CQCInf | TEXT | False | 框架柱X向地震剪力 |  | 先统计单振型内力，再CQC，包含非边框柱的框支柱，也与面外是否统计到框架参数相关 |
| SColY_CQCInf | TEXT | False | 框架柱Y向地震剪力 |  | 先统计单振型内力，再CQC，包含非边框柱的框支柱，也与面外是否统计到框架参数相关 |
| SColKZZX_CQCInf | TEXT | False | 框支柱X向地震剪力 |  | 先统计单振型内力，再CQC，所有框支柱，包括边框柱 |
| SColKZZY_CQCInf | TEXT | False | 框支柱Y向地震剪力 |  | 先统计单振型内力，再CQC，所有框支柱，包括边框柱 |
| SWallX_CQCInf | TEXT | False | 墙X向地震剪力 |  | 先统计单振型内力，再CQC |
| SWallY_CQCInf | TEXT | False | 墙Y向地震剪力 |  | 先统计单振型内力，再CQC |
| SColX_AppInf | TEXT | False | 普通柱X向规定水平力时的地震剪力 |  |  |
| SColY_AppInf | TEXT | False | 普通柱Y向规定水平力时的地震剪力 |  |  |
| SColKZZX_AppInf | TEXT | False | 框支柱X向规定水平力时的地震剪力 |  |  |
| SColKZZY_AppInf | TEXT | False | 框支柱Y向规定水平力时的地震剪力 |  |  |
| SBraceX_AppInf | TEXT | False | 支撑X向规定水平力时的地震剪力 |  |  |
| SBraceY_AppInf | TEXT | False | 支撑Y向规定水平力时的地震剪力 |  |  |
| SSLegWallX_AppInf | TEXT | False | 短肢墙X向规定水平力时的地震剪力 |  |  |
| SSLegWallY_AppInf | TEXT | False | 短肢墙Y向规定水平力时的地震剪力 |  |  |
| SWallX_AppInf | TEXT | False | 墙X向规定水平力时的地震剪力 |  |  |
| SWallY_AppInf | TEXT | False | 墙Y向规定水平力时的地震剪力 |  |  |
| SColYZX_AppInf | TEXT | False | 装配式中预制柱X向规定水平力时的地震剪力 |  |  |
| SColYZY_AppInf | TEXT | False | 装配式中预制柱Y向规定水平力时的地震剪力 |  |  |
| SBraceYZX_AppInf | TEXT | False | 装配式中预制支撑X向规定水平力时的地震剪力 |  |  |
| SBraceYZY_AppInf | TEXT | False | 装配式中预制支撑Y向规定水平力时的地震剪力 |  |  |
| SWallYZX_AppInf | TEXT | False | 装配式中预制墙X向规定水平力时的地震剪力 |  |  |
| SWallYZY_AppInf | TEXT | False | 装配式中预制墙Y向规定水平力时的地震剪力 |  |  |
| MColX_AppAxisInf | TEXT | False | 普通柱X向规定水平力时的地震倾覆弯矩（轴力方式） |  |  |
| MColY_AppAxisInf | TEXT | False | 普通柱Y向规定水平力时的地震倾覆弯矩（轴力方式） |  |  |
| MColKZZX_AppAxisInf | TEXT | False | 框支柱X向规定水平力时的地震倾覆弯矩（轴力方式） |  |  |
| MColKZZY_AppAxisInf | TEXT | False | 框支柱Y向规定水平力时的地震倾覆弯矩（轴力方式） |  |  |
| MBraceX_AppAxisInf | TEXT | False | 支撑X向规定水平力时的地震倾覆弯矩（轴力方式） |  |  |
| MBraceY_AppAxisInf | TEXT | False | 支撑Y向规定水平力时的地震倾覆弯矩（轴力方式） |  |  |
| MSLegWallX_AppAxisInf | TEXT | False | 短肢墙X向规定水平力时的地震倾覆弯矩（轴力方式） |  |  |
| MSLegWallY_AppAxisInf | TEXT | False | 短肢墙Y向规定水平力时的地震倾覆弯矩（轴力方式） |  |  |
| MWallX_AppAxisInf | TEXT | False | 墙X向规定水平力时的地震倾覆弯矩（轴力方式） |  |  |
| MWallY_AppAxisInf | TEXT | False | 墙Y向规定水平力时的地震倾覆弯矩（轴力方式） |  |  |
| MColX_AppAxis_WLInf | TEXT | False | 普通柱X向规定水平力时的地震倾覆弯矩（魏涟方式） |  |  |
| MColY_AppAxis_WLInf | TEXT | False | 普通柱Y向规定水平力时的地震倾覆弯矩（魏涟方式） |  |  |
| MColKZZX_AppAxis_WLInf | TEXT | False | 框支柱X向规定水平力时的地震倾覆弯矩（魏涟方式） |  |  |
| MColKZZY_AppAxis_WLInf | TEXT | False | 框支柱Y向规定水平力时的地震倾覆弯矩（魏涟方式） |  |  |
| MBraceX_AppAxis_WLInf | TEXT | False | 支撑X向规定水平力时的地震倾覆弯矩（魏涟方式） |  |  |
| MBraceY_AppAxis_WLInf | TEXT | False | 支撑Y向规定水平力时的地震倾覆弯矩（魏涟方式） |  |  |
| MSLegWallX_AppAxis_WLInf | TEXT | False | 短肢墙X向规定水平力时的地震倾覆弯矩（魏涟方式） |  |  |
| MSLegWallY_AppAxis_WLInf | TEXT | False | 短肢墙Y向规定水平力时的地震倾覆弯矩（魏涟方式） |  |  |
| MWallX_AppAxis_WLInf | TEXT | False | 墙X向规定水平力时的地震倾覆弯矩（魏涟方式） |  |  |
| MWallY_AppAxis_WLInf | TEXT | False | 墙Y向规定水平力时的地震倾覆弯矩（魏涟方式） |  |  |
| SColWXPInf | TEXT | False | 普通柱+X向风剪力 |  |  |
| SColWXNInf | TEXT | False | 普通柱-X向风剪力 |  |  |
| SColWYPInf | TEXT | False | 普通柱+Y向风剪力 |  |  |
| SColWYNInf | TEXT | False | 普通柱-Y向风剪力 |  |  |
| SBraceWXPInf | TEXT | False | 支撑+X向风剪力 |  |  |
| SBraceWXNInf | TEXT | False | 支撑-X向风剪力 |  |  |
| SBraceWYPInf | TEXT | False | 支撑+Y向风剪力 |  |  |
| SBraceWYNInf | TEXT | False | 支撑-Y向风剪力 |  |  |
| SWallWXPInf | TEXT | False | 墙+X向风剪力 |  |  |
| SWallWXNInf | TEXT | False | 墙-X向风剪力 |  |  |
| SWallWYPInf | TEXT | False | 墙+Y向风剪力 |  |  |
| SWallWYNInf | TEXT | False | 墙-Y向风剪力 |  |  |
| SXWallBodyX_CQCInf | TEXT | False | X向墙X向地震剪力 |  | 先统计单振型内力，再CQC |
| SXWallBodyY_CQCInf | TEXT | False | X向墙Y向地震剪力 |  | 先统计单振型内力，再CQC |
| SYWallBodyX_CQCInf | TEXT | False | Y向墙X向地震剪力 |  | 先统计单振型内力，再CQC |
| SYWallBodyY_CQCInf | TEXT | False | Y向墙Y向地震剪力 |  | 先统计单振型内力，再CQC |
| SEdgeX_CQCInf | TEXT | False | 边缘构件X向地震剪力 |  | 先统计单振型内力，再CQC |
| SEdgeY_CQCInf | TEXT | False | 边缘构件Y向地震剪力 |  | 先统计单振型内力，再CQC |
| SXWallBodyX_AppInf | TEXT | False | X向墙X向规定水平力时的剪力 |  |  |
| SXWallBodyY_AppInf | TEXT | False | X向墙Y向规定水平力时的剪力 |  |  |
| SYWallBodyX_AppInf | TEXT | False | Y向墙X向规定水平力时的剪力 |  |  |
| SYWallBodyY_AppInf | TEXT | False | Y向墙Y向规定水平力时的剪力 |  |  |
| SEdgeX_AppInf | TEXT | False | 边缘构件X向规定水平力时的剪力 |  |  |
| SEdgeY_AppInf | TEXT | False | 边缘构件Y向规定水平力时的剪力 |  |  |

dsnStatFlrAdjCoe
[图]

| dsnStatFlrAdjCoe |  |  |  |  |  |
|---|---|---|---|---|---|
| 楼层相关的各调整系数表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| JZBCoeXInf | TEXT | False | X方向调整系数 |  |  |
| JZBCoeYInf | TEXT | False | Y方向调整系数 |  |  |
| JZBCoeZ | REAL | False | Z方向调整系数 |  |  |
| JZBUSDisCoeXInf | TEXT | False | X方向位移调整系数，美国规范用 |  |  |
| JZBUSDisCoeYInf | TEXT | False | Y方向位移调整系数，美国规范用 |  |  |
| BRCSign | INTEGER | False | 薄弱层标志 |  |  |
| BRCCoeXInf | TEXT | False | X向调整系数 |  |  |
| BRCCoeYInf | TEXT | False | Y向调整系数 |  |  |
| KZZCoeXInf | TEXT | False | 框支柱X向调整系数 |  | 取0.2V0和框支柱调整系数的大值 |
| KZZCoeYInf | TEXT | False | 框支柱Y向调整系数 |  | 取0.2V0和框支柱调整系数的大值 |
| V02CoeXInf | REAL | False | X向0.2V0调整系数 |  |  |
| V02CoeYInf | REAL | False | Y向0.2V0调整系数 |  |  |
| V02WallCoeXInf | REAL | False | X向墙在地震作用下的调整系数 |  | 板柱-剪力墙或筒体结构用 |
| V02WallCoeYInf | REAL | False | Y向墙在地震作用下的调整系数 |  | 板柱-剪力墙或筒体结构用 |
| V02WallCoeWXPInf | INTEGER | False | +X向墙在风荷载作用下的调整系数 |  | 板柱-剪力墙或筒体结构用 |
| V02WallCoeWXNInf | INTEGER | False | -X向墙在风荷载作用下的调整系数 |  | 板柱-剪力墙或筒体结构用 |
| V02WallCoeWYPInf | TEXT | False | +Y向墙在风荷载作用下的调整系数 |  | 板柱-剪力墙或筒体结构用 |
| V02WallCoeWYNInf | TEXT | False | -Y向墙在风荷载作用下的调整系数 |  | 板柱-剪力墙或筒体结构用 |
| KTSignXInf | TEXT | False | 是否按框筒结构调整标志 |  |  |
| KTSignYInf | TEXT | False | 是否按框筒结构调整标志 |  |  |

dsnStatDis
[图]

| dsnStatDis |  |  |  |  |  |
|---|---|---|---|---|---|
| 位移统计结果表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| ModuleID | INTEGER | False | 模型号 |  |  |
| LDCase | INTEGER | False | 工况号 |  |  |
| MaxDNode | INTEGER | False | 最大位移对应的节点号 |  |  |
| MaxD | REAL | False | 最大位移 |  |  |
| MinDNode | INTEGER | False | 最小位移对应的节点号 |  |  |
| MinD | REAL | False | 最小位移 |  |  |
| MassAveD | REAL | False | 质量加权绝对平均位移 |  |  |
| MaxFlrDNode | INTEGER | False | 最大层间位移对应的节点号 |  |  |
| MaxFlrD | REAL | False | 最大层间位移 |  |  |
| MinFlrDNode | INTEGER | False | 最小层间位移对应的节点号 |  |  |
| MinFlrD | REAL | False | 最小层间位移 |  |  |
| MassAveFlrD | REAL | False | 质量加权层间平均位移 |  |  |
| MaxFlrAngleNode | INTEGER | False | 最大层间位移角对应的节点号 |  |  |
| MaxFlrAngleDis | REAL | False | 最大层间位移角计算用层间位移 |  |  |
| MinFlrAngleNode | INTEGER | False | 最小层间位移角对应的节点号 |  |  |
| MinFlrAngleDis | REAL | False | 最小层间位移角计算用层间位移 |  |  |
| MaxDZNode | INTEGER | False | 竖向最大位移对应的节点 |  |  |
| MaxDZ | REAL | False | 节点竖向最大位移 |  |  |

dsnStatStab
[图]

| dsnStatStab |  |  |  |  |  |
|---|---|---|---|---|---|
| 刚重比统计结果表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| StifX_SeisInf | TEXT | False | X向地震刚度 |  |  |
| StifY_SeisInf | TEXT | False | Y向地震刚度 |  |  |
| StifX_WindInf | TEXT | False | X向风刚度 |  |  |
| StifY_WindInf | TEXT | False | Y向风刚度 |  |  |
| CoeX_SeisInf | TEXT | False | X向地震整体稳定验算结果 |  |  |
| CoeY_SeisInf | TEXT | False | Y向地震整体稳定验算结果 |  |  |
| CoeX_WindInf | TEXT | False | X向风整体稳定验算结果 |  |  |
| CoeY_WindInf | TEXT | False | Y向风整体稳定验算结果 |  |  |

dsnStatOverturn
[图]

| dsnStatOverturn |  |  |  |  |  |
|---|---|---|---|---|---|
| 零应力区统计结果表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| SeisMXInf | TEXT | False | X向地震倾覆弯矩 |  |  |
| SeisMYInf | TEXT | False | Y向地震倾覆弯矩 |  |  |
| SeisRMXInf | TEXT | False | X向地震抗倾覆弯矩 |  |  |
| SeisRMYInf | TEXT | False | Y向地震抗倾覆弯矩 |  |  |
| WindMXInf | TEXT | False | X向风倾覆弯矩 |  |  |
| WindMYInf | TEXT | False | Y向风倾覆弯矩 |  |  |
| WindRMXInf | TEXT | False | X向风抗倾覆弯矩 |  |  |
| WindRMYInf | TEXT | False | Y向风抗倾覆弯矩 |  |  |
| CoeX_SeisInf | TEXT | False | X向地震零应力区验算结果 |  |  |
| CoeY_SeisInf | TEXT | False | Y向地震零应力区验算结果 |  |  |
| CoeX_WindInf | TEXT | False | X向风零应力区验算结果 |  |  |
| CoeY_WindInf | TEXT | False | Y向风零应力区验算结果 |  |  |

dsnStatWindComfort
[图]

| dsnStatWindComfort |  |  |  |  |  |
|---|---|---|---|---|---|
| 风振舒适度统计结果表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| CoeWindXInf | TEXT | False | 按荷载规范计算的X向风振加速度 |  |  |
| CoeWindXHInf | TEXT | False | 按荷载规范计算的X横向风振加速度 |  |  |
| CoeWindYInf | TEXT | False | 按荷载规范计算的Y向风振加速度 |  |  |
| CoeWindYHInf | TEXT | False | 按荷载规范计算的Y横向风振加速度 |  |  |

构件
调整系数
dsnComAdjCoe_Beam
[图]

| dsnComAdjCoe_Beam |  |  |  |  |  |
|---|---|---|---|---|---|
| 调整参数-梁 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| ComKind | INTEGER | False | 构件类型 |  |  |
| SeisCoe | REAL | False | 水平转换构件地震力放大系数 |  |  |
| SeisVCoe | REAL | False | 竖向地震放大系数 |  |  |
| LiveLoadCoe | REAL | False | 活荷载折减系数 |  |  |
| LiveGraCoe | REAL | False | 活荷载重力荷载代表值系数 |  |  |
| ReduceCoeInf | TEXT | False | 工况对应的折减系数 |  | 目前用于消防车荷载折减系数 |
| StruCoe | REAL | False | 结构重要性系数 |  | 非地震组合用 |
| EmpCoe | REAL | False | 构件重要性系数 |  | 性能设计用 |
| AmpCoe | REAL | False | 调幅系数 |  |  |
| TorCoe | REAL | False | 扭矩折减系数 |  |  |
| VCoe | REAL | False | 设计弯矩调整系数 |  |  |
| MCoe | REAL | False | 设计剪力调整系数 |  |  |

dsnComAdjCoe_Col
[图]
[图]

| dsnComAdjCoe_Col |  |  |  |  |  |
|---|---|---|---|---|---|
| 调整参数-柱 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| ComKind | INTEGER | False | 构件类型 |  |  |
| SeisCoe | REAL | False | 水平转换构件地震力放大系数 |  |  |
| SeisVCoe | REAL | False | 竖向地震放大系数 |  |  |
| LiveLoadCoe | REAL | False | 活荷载折减系数 |  |  |
| LiveGraCoe | REAL | False | 活荷载重力荷载代表值系数 |  |  |
| ReduceCoeInf | TEXT | False | 工况对应的折减系数 |  | 目前用于消防车荷载折减系数 |
| StruCoe | REAL | False | 结构重要性系数 |  | 非地震组合用 |
| EmpCoe | REAL | False | 构件重要性系数 |  | 性能设计用 |
| KZZSeisCoe | REAL | False | 地震力放大系数 |  | 钢转换柱用 |
| AxisCoe | REAL | False | 轴力调整系数 |  | 转换柱用 |
| KZZCoeXInf | TEXT | False | 框支柱X向地震调整系数 |  |  |
| KZZCoeYInf | TEXT | False | 框支柱Y向地震调整系数 |  |  |
| SeisVCoeX | REAL | False | 柱X向剪力系数 |  | 特殊构件定义中输入 |
| SeisVCoeY | REAL | False | 柱Y向剪力系数 |  | 特殊构件定义中输入 |
| ZPSSeisCoe | REAL | False | 装配式结构中现浇构件地震内力放大系数 |  |  |
| UpMCoe | REAL | False | 设计弯矩调整系数-顶 |  |  |
| UpVCoe | REAL | False | 设计剪力调整系数-顶 |  |  |
| DwMCoe | REAL | False | 设计弯矩调整系数-底 |  |  |
| DwVCoe | REAL | False | 设计剪力调整系数-底 |  |  |

dsnComAdjCoe_Brace
[图]
[图]

| dsnComAdjCoe_Brace |  |  |  |  |  |
|---|---|---|---|---|---|
| 调整参数-斜杆 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| ComKind | INTEGER | False | 构件类型 |  |  |
| SeisCoe | REAL | False | 水平转换构件地震力放大系数 |  |  |
| SeisVCoe | REAL | False | 竖向地震放大系数 |  |  |
| LiveLoadCoe | REAL | False | 活荷载折减系数 |  |  |
| LiveGraCoe | REAL | False | 活荷载重力荷载代表值系数 |  |  |
| ReduceCoeInf | TEXT | False | 工况对应的折减系数 |  | 目前用于消防车荷载折减系数 |
| StruCoe | REAL | False | 结构重要性系数 |  | 非地震组合用 |
| EmpCoe | REAL | False | 构件重要性系数 |  | 性能设计用 |
| KZZSeisCoe | REAL | False | 地震力放大系数 |  | 钢转换柱用 |
| AxisCoe | REAL | False | 轴力调整系数 |  | 转换柱用 |
| KZZCoeXInf | TEXT | False | 框支柱X向地震调整系数 |  |  |
| KZZCoeYInf | TEXT | False | 框支柱Y向地震调整系数 |  |  |
| SeisVCoeX | REAL | False | 柱X向剪力系数 |  | 特殊构件定义中输入 |
| SeisVCoeY | REAL | False | 柱Y向剪力系数 |  | 特殊构件定义中输入 |
| ZPSSeisCoe | REAL | False | 装配式结构中现浇构件地震内力放大系数 |  |  |
| UpMCoe | REAL | False | 设计弯矩调整系数-顶 |  |  |
| UpVCoe | REAL | False | 设计剪力调整系数-顶 |  |  |
| DwMCoe | REAL | False | 设计弯矩调整系数-底 |  |  |
| DwVCoe | REAL | False | 设计剪力调整系数-底 |  |  |

dsnComAdjCoe_WallCol
[图]

| dsnComAdjCoe_WallCol |  |  |  |  |  |
|---|---|---|---|---|---|
| 调整参数-墙柱 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| ComKind | INTEGER | False | 构件类型 |  |  |
| SeisCoe | REAL | False | 水平转换构件地震力放大系数 |  |  |
| SeisVCoe | REAL | False | 竖向地震放大系数 |  |  |
| LiveLoadCoe | REAL | False | 活荷载折减系数 |  |  |
| LiveGraCoe | REAL | False | 活荷载重力荷载代表值系数 |  |  |
| ReduceCoeInf | TEXT | False | 工况对应的折减系数 |  | 目前用于消防车荷载折减系数 |
| StruCoe | REAL | False | 结构重要性系数 |  | 非地震组合用 |
| EmpCoe | REAL | False | 构件重要性系数 |  | 性能设计用 |
| ZPSSeisCoe | REAL | False | 装配式结构中现浇构件地震内力放大系数 |  |  |
| UpMCoe | REAL | False | 设计弯矩调整系数-顶 |  |  |
| UpVCoe | REAL | False | 设计剪力调整系数-顶 |  |  |
| DwMCoe | REAL | False | 设计弯矩调整系数-底 |  |  |
| DwVCoe | REAL | False | 设计剪力调整系数-底 |  |  |

dsnComAdjCoe_WallBeam
[图]

| dsnComAdjCoe_WallBeam |  |  |  |  |  |
|---|---|---|---|---|---|
| 调整参数-墙梁 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| ComKind | INTEGER | False | 构件类型 |  |  |
| SeisCoe | REAL | False | 水平转换构件地震力放大系数 |  |  |
| SeisVCoe | REAL | False | 竖向地震放大系数 |  |  |
| LiveLoadCoe | REAL | False | 活荷载折减系数 |  |  |
| LiveGraCoe | REAL | False | 活荷载重力荷载代表值系数 |  |  |
| ReduceCoeInf | TEXT | False | 工况对应的折减系数 |  | 目前用于消防车荷载折减系数 |
| StruCoe | REAL | False | 结构重要性系数 |  | 非地震组合用 |
| EmpCoe | REAL | False | 构件重要性系数 |  | 性能设计用 |
| AmpCoe | REAL | False | 调幅系数 |  |  |
| TorCoe | REAL | False | 扭矩折减系数 |  |  |
| VCoe | REAL | False | 设计剪力调整系数 |  |  |
| MCoe | REAL | False | 设计弯矩调整系数 |  |  |

构件设计结果
梁
构件信息
dsnSectDefBeam
[图]

| dsnSectDefBeam |  |  |  |  |  |
|---|---|---|---|---|---|
| 构件信息-梁截面定义 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | ID |  |  |
| PMTotID | INTEGER | False | 建模构件ID |  |  |
| PMNo | INTEGER | False | 建模构件序号 |  |  |
| PMSectKind | INTEGER | False | 截面类型 |  |  |
| SectComKind | INTEGER | False | 所属构件类型 |  |  |
| Name | TEXT | False | 截面名称 |  |  |
| Source | INTEGER | False | 数据来源 | 枚举 | 1-PM 2-鉴定加固 3-优化设计 |
| SectInf | TEXT | False | 截面定义数据 |  |  |

dsnComBeamInf
[图]
[图]
[图]
[图]
[图]

| dsnComBeamInf |  |  |  |  |  |
|---|---|---|---|---|---|
| 构件信息-梁 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| PMTotID | INTEGER | False | 建模构件ID |  |  |
| FlrID | INTEGER | False | 层内编号 |  |  |
| ComKind | INTEGER | False | 构件类型 |  |  |
| Kind | INTEGER | False | 梁属性 | YJKDSN::EBeamDSN | 普通梁 托墙转换梁 托柱转换梁 门式刚梁 消能梁 组合梁 吊车梁 |
| MatKind | INTEGER | False | 材料类型 | YJKDSN::EMat |  |
| PMMatKind | INTEGER | False | 材料类型-建模分类 |  | 5-钢 6-砼 |
| ConGrade | REAL | False | 砼标号 |  |  |
| ConGradeIn | REAL | False | 砼标号-内部 |  | 钢管砼叠合柱 |
| SteelKind | INTEGER | False | 钢号 |  |  |
| Cover | REAL | False | 保护层厚度 |  |  |
| TranHor | INTEGER | False | 是否为水平转换 |  |  |
| KZDJ | INTEGER | False | 抗震等级 |  |  |
| KZDJGZ | INTEGER | False | 抗震构造等级 |  |  |
| MainBar | INTEGER | False | 纵筋类型 |  |  |
| HoopBar | INTEGER | False | 箍筋类型 |  |  |
| Air | INTEGER | False | 是否按人防设计 |  |  |
| YZ | INTEGER | False | 是否是预制构件 |  |  |
| YYL | INTEGER | False | 是否是预应力构件 |  |  |
| WJType | INTEGER | False | 网架类别 | YJKDSN::EWJType | 网架、单层网壳、双层网壳等 |
| TrussSign | INTEGER | False | 桁架杆件标志 | YJKDSN::ETrussKind | 上弦、下弦、腹杆等 |
| XNSJM | INTEGER | False | 性能设计标志-正截面设计 |  | 弹性、不屈服 |
| XNSJV | INTEGER | False | 性能设计标志-斜截面设计 |  | 弹性、不屈服 |
| XNSJEmpSign | INTEGER | False | 构件重要性类别 |  | 1-耗能构件 2-普通构件 3-关键构件 |
| XNSJBLInf | TEXT | False | 性能设计包络标志 | dsnIModelAComProp_XNSJBL |  |
| Solid | INTEGER | False | 是否为实体元 |  |  |
| SeisVCom | INTEGER | False | 是否是指定竖向地震的构件 |  |  |
| NonLProp | INTEGER | False | 非线性数据 |  |  |
| HN | INTEGER | False | 是否是性能设计耗能构件 |  |  |
| BTRatioGrade | INTEGER | False | 宽厚比等级 |  |  |
| YXGrade | INTEGER | False | 延性等级 |  |  |
| BetaE | REAL | False | 性能系数的调整系数βe |  |  |
| RealXNXS | REAL | False | 实际性能系数 |  |  |
| TempInf | TEXT | False | 构件温度 |  | 依次记录 0-升温 1-降温 2-防火升温 |
| FHth | REAL | False | 耐火时间 |  |  |
| FHiqz | INTEGER | False | 膨胀型 |  | 1-非膨胀型 2-水泥砂浆 |
| FHri | REAL | False | 等效热阻/等效热传导系数 |  |  |
| FHdil | REAL | False | 保护层厚度 |  |  |
| FHfxz | REAL | False | 截面形状系数 |  |  |
| EnvSign | INTEGER | False | 是否包络设计 |  |  |
| DuctLevelEU | INTEGER | False | 延性等级-欧标 |  |  |
| DuctLevelUS | INTEGER | False | 延性等级-美标 |  |  |
| CurveCoe | REAL | False | 曲率系数 |  |  |
| StiffCoeInf | TEXT | False | 杆件的6个自由度对应的刚度系数 |  |  |
| PresInf | TEXT | False |  |  |  |
| TrussXID | INTEGER | False | X方向桁架编号 |  |  |
| TrussYID | INTEGER | False | Y方向桁架编号 |  |  |
| NodeS | INTEGER | False | 节点ID-起始端 |  |  |
| NodeE | INTEGER | False | 节点ID-终止端 |  |  |
| SupKindS | INTEGER | False | 支座类型-起始端 | YJKDSN::EBeamSup |  |
| SupKindE | INTEGER | False | 支座类型-终止端 | YJKDSN::EBeamSup |  |
| SteelT | REAL | False | 钢板厚度 |  |  |
| SteelH | REAL | False | 钢板高度 |  |  |
| StiffCoeM | REAL | False | 刚度放大系数或刚度折减系数 |  |  |
| XJKind | INTEGER | False | 特殊斜筋类型 | YJKDSN::EBeamXJ |  |
| LinkS | INTEGER | False | 支座约束类型 | YJKDSN::ESupLink | 刚接 铰接 滑动 半刚接 |
| LinkE | INTEGER | False | 支座约束类型 | YJKDSN::ESupLink |  |
| Ang | REAL | False | 梁布置角度（rad） |  |  |
| PortalJJLCoe | REAL | False | 门刚梁横向加劲肋间距与腹板最大高度的比值(a/Hw) |  | 0为不设加劲肋 |
| JGID | INTEGER | False |  |  |  |
| FreeSupMoment | TEXT | False | 简支梁内力 |  |  |
| PMSectNo | INTEGER | False | 建模截面索引 |  |  |
| Span | REAL | False | 平面内长度（m） |  |  |
| AmpSign | INTEGER | False | 调幅标志 |  |  |
| SpanOut | REAL | False | 平面外长度（m） |  |  |
| MainBeamID | INTEGER | False | 主梁ID |  |  |
| BeamSegID | INTEGER | False | 梁段ID |  |  |
| FrameSign | INTEGER | False | 梁属性 |  | 框架梁 非框架梁 连梁 |
| InputSign | INTEGER | False | 梁建模类别 |  | 普通梁 按次梁输入的次梁 空心板肋梁 地基梁 |

dsnComBeam_Con
[图]

| dsnComBeam_Con |  |  |  |  |  |
|---|---|---|---|---|---|
| 构件信息-梁-砼 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| ComKind | INTEGER | False | 构件类型 | YJKDSN::ECom |  |
| Sect | INTEGER | False | 截面数量 |  |  |

dsnComBeam_SRC
[图]

| dsnComBeam_SRC |  |  |  |  |  |
|---|---|---|---|---|---|
| 构件信息-梁-钢骨砼 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| ComKind | INTEGER | False | 构件类型 | YJKDSN::ECom |  |
| Sect | INTEGER | False | 截面ID |  |  |
| BTRatio | REAL | False | 翼缘宽厚比 |  |  |
| BTRatioMax | REAL | False | 翼缘宽厚比限值 |  |  |
| HTRatio | REAL | False | 腹板高厚比 |  |  |
| HTRatioMax | REAL | False | 腹板高厚比限值 |  |  |

dsnComBeam_RectTube
[图]

| dsnComBeam_RectTube |  |  |  |  |  |
|---|---|---|---|---|---|
| 构件信息-梁-矩形钢管砼 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| ComKind | INTEGER | False | 构件类型 | YJKDSN::ECom |  |
| Sect | INTEGER | False | 截面数量 |  |  |

dsnComBeam_Steel
[图]

| dsnComBeam_Steel |  |  |  |  |  |
|---|---|---|---|---|---|
| 构件信息-梁-钢 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| ComKind | INTEGER | False | 构件类型 | YJKDSN::ECom |  |
| Sect | INTEGER | False | 截面ID |  |  |
| FAIB | REAL | False | 整体稳定系数 |  |  |
| GMUp | REAL | False | 上翼缘塑性发展系数 |  |  |
| GMDw | REAL | False | 下翼缘塑性发展系数 |  |  |
| BTRatio | REAL | False | 翼缘宽厚比 |  |  |
| BTRatioMax | REAL | False | 翼缘宽厚比限值 |  |  |
| HTRatio | REAL | False | 腹板高厚比 |  |  |
| HTRatioMax | REAL | False | 腹板高厚比限值 |  |  |
| BTRatioReg | REAL | False | 受压翼缘正则化宽厚比 |  |  |
| BTRatioRegMax | REAL | False | 受压翼缘正则化宽厚比限值 |  |  |

dsnComBeam_Comp
[图]

| dsnComBeam_Comp |  |  |  |  |  |
|---|---|---|---|---|---|
| 构件信息-梁-组合梁 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| ComKind | INTEGER | False | 构件类型 | YJKDSN::ECom |  |
| Sect | INTEGER | False | 截面ID |  |  |
| BTRatio | REAL | False | 翼缘宽厚比 |  |  |
| BTRatioMax | REAL | False | 翼缘宽厚比限值 |  |  |
| HTRatio | REAL | False | 腹板高厚比 |  |  |
| HTRatioMax | REAL | False | 腹板高厚比限值 |  |  |
| BTRatioReg | REAL | False | 受压翼缘正则化宽厚比 |  |  |
| BTRatioRegMax | REAL | False | 受压翼缘正则化宽厚比限值 |  |  |
| NutLinkType | INTEGER | False | 组合梁连接类型 |  | 0-无抗剪连接件 1-完全抗剪连接 2-不完全抗剪连接 |

dsnComMainBeamInf
[图]

| dsnComMainBeamInf |  |  |  |  |  |
|---|---|---|---|---|---|
| 主梁基本信息表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| FlrID | INTEGER | False | 构件层内ID |  |  |
| ComInf | TEXT | False | 各梁段全楼ID |  |  |
| ComDirInf | TEXT | False | 各梁段方向是否与主梁方向一致 |  |  |

dsnComSubBeamInf
[图]
[图]
[图]

| dsnComSubBeamInf |  |  |  |  |  |
|---|---|---|---|---|---|
| 次梁基本信息表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| PMTotID | INTEGER | False | 建模构件ID |  |  |
| FlrID | INTEGER | False | 层内编号 |  |  |
| ComKind | INTEGER | False | 构件类型 |  |  |
| Kind | INTEGER | False | 梁属性 | YJKDSN::EBeamDSN | 普通梁 托墙转换梁 托柱转换梁 门式刚梁 消能梁 组合梁 吊车梁 |
| MatKind | INTEGER | False | 材料类型 | YJKDSN::EMat |  |
| PMMatKind | INTEGER | False | 材料类型-建模分类 |  | 5-钢 6-砼 |
| ConGrade | REAL | False | 砼标号 |  |  |
| ConGradeIn | REAL | False | 砼标号-内部 |  | 钢管砼叠合柱 |
| SteelKind | INTEGER | False | 钢号 |  |  |
| Cover | REAL | False | 保护层厚度 |  |  |
| TranHor | INTEGER | False | 是否为水平转换 |  |  |
| KZDJ | INTEGER | False | 抗震等级 |  |  |
| KZDJGZ | INTEGER | False | 抗震构造等级 |  |  |
| MainBar | INTEGER | False | 纵筋类型 |  |  |
| HoopBar | INTEGER | False | 箍筋类型 |  |  |
| Air | INTEGER | False | 是否按人防设计 |  |  |
| YZ | INTEGER | False | 是否是预制构件 |  |  |
| YYL | INTEGER | False | 是否是预应力构件 |  |  |
| WJType | INTEGER | False | 网架类别 | YJKDSN::EWJType | 网架、单层网壳、双层网壳等 |
| TrussSign | INTEGER | False | 桁架杆件标志 | YJKDSN::ETrussKind | 上弦、下弦、腹杆等 |
| XNSJM | INTEGER | False | 性能设计标志-正截面设计 |  | 弹性、不屈服 |
| XNSJV | INTEGER | False | 性能设计标志-斜截面设计 |  | 弹性、不屈服 |
| XNSJEmpSign | INTEGER | False | 构件重要性类别 |  | 1-耗能构件 2-普通构件 3-关键构件 |
| XNSJBLInf | TEXT | False | 性能设计包络标志 | dsnIModelAComProp_XNSJBL |  |
| Solid | INTEGER | False | 是否为实体元 |  |  |
| SeisVCom | INTEGER | False | 是否是指定竖向地震的构件 |  |  |
| NonLProp | INTEGER | False | 非线性数据 |  |  |
| HN | INTEGER | False | 是否是性能设计耗能构件 |  |  |
| BTRatioGrade | INTEGER | False | 宽厚比等级 |  |  |
| YXGrade | INTEGER | False | 延性等级 |  |  |
| BetaE | REAL | False | 性能系数的调整系数βe |  |  |
| RealXNXS | REAL | False | 实际性能系数 |  |  |
| TempInf | TEXT | False | 构件温度 |  | 依次记录 0-升温 1-降温 2-防火升温 |
| FHth | REAL | False | 耐火时间 |  |  |
| FHiqz | INTEGER | False | 膨胀型 |  | 1-非膨胀型 2-水泥砂浆 |
| FHri | REAL | False | 等效热阻/等效热传导系数 |  |  |
| FHdil | REAL | False | 保护层厚度 |  |  |
| FHfxz | REAL | False | 截面形状系数 |  |  |
| EnvSign | INTEGER | False | 是否包络设计 |  |  |
| DuctLevelEU | INTEGER | False | 延性等级-欧标 |  |  |
| DuctLevelUS | INTEGER | False | 延性等级-美标 |  |  |
| CurveCoe | REAL | False | 曲率系数 |  |  |
| StiffCoeInf | TEXT | False | 杆件的6个自由度对应的刚度系数 |  |  |
| PresInf | TEXT | False |  |  |  |
| TrussXID | INTEGER | False | X方向桁架编号 |  |  |
| TrussYID | INTEGER | False | Y方向桁架编号 |  |  |
| PMSectNo | INTEGER | False | 截面ID |  |  |
| Span | REAL | False | 梁平面内长度(m) |  |  |
| AmpSign | INTEGER | False | 调幅梁标志 |  |  |
| SpanOut | REAL | False | 梁平面外长度(m) |  |  |
| MainBeamID | INTEGER | False | 所属主梁ID |  |  |
| BeamSegID | INTEGER | False | 在梁段中的序号 |  |  |
| FrameSign | INTEGER | False | 梁属性 |  | 框架梁 非框架梁 连梁 |
| InputSign | INTEGER | False | 梁建模类别 |  | 普通梁 按次梁输入的次梁 空心板肋梁 地基梁 |

dsnComMainSubBeamInf
[图]

| dsnComMainSubBeamInf |  |  |  |  |  |
|---|---|---|---|---|---|
| 主次梁基本信息表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| FlrID | INTEGER | False | 构件层内ID |  |  |
| ComInf | TEXT | False | 各梁段全楼ID |  |  |
| ComDirInf | TEXT | False | 各梁段方向是否与主梁方向一致 |  |  |

计算结果
dsnComNL_Beam
[图]

| dsnComNL_Beam |  |  |  |  |  |
|---|---|---|---|---|---|
| 构件内力-梁 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| LDCaseID | INTEGER | False | 工况ID |  |  |
| ComKind | INTEGER | False | 构件类型 | YJKDSN::ECom |  |
| Sect | INTEGER | False | 截面ID |  |  |
| NLPreInf | TEXT | False | 内力-调整前 |  |  |
| NLAftInf | TEXT | False | 内力-调整后 |  |  |

dsnComJYB_Beam

| dsnComJYB_Beam |  |  |  |  |  |
|---|---|---|---|---|---|
| 剪压比-梁 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| ComKind | INTEGER | False | 构件类型 | YJKDSN::ECom |  |
| Sect | INTEGER | False | 截面ID |  |  |
| Dir | INTEGER | False | 剪压比方向 |  | 1-X 2-Y |
| JYB | REAL | False | 剪压比 |  |  |
| JYBMax | REAL | False | 剪压比限值 |  |  |
| VCal | REAL | False | 计算剪力 |  |  |
| VMax | REAL | False | 剪力限值 |  |  |
| LDCombID | INTEGER | False | 控制组合号 |  |  |
| VInf | TEXT | False | 控制内力 |  |  |
| AsTow | INTEGER | False | 控制塔号 |  |  |
| VCon | REAL | False | 型钢混凝土中的混凝土X向承担的剪力 |  |  |
| JYBMaxCon | REAL | False | 型钢混凝土中的混凝土X向斜截面验算系数 |  |  |
| VCalCon | REAL | False | 型钢混凝土中的混凝土X向斜截面计算剪应力 |  |  |
| VMaxCon | REAL | False | 型钢混凝土中的混凝土X向斜截面最大承载力 |  |  |

设计结果
dsnComBeamSect_Con

| dsnComBeamSect_Con |  |  |  |  |  |
|---|---|---|---|---|---|
| 梁截面-砼 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| ComKind | INTEGER | False | 构件类型 | YJKDSN::ECom |  |
| Sect | INTEGER | False | 截面ID |  |  |
| UpAs | REAL | False | 上铁-受拉钢筋面积 |  |  |
| UpAsCal | REAL | False | 上铁-计算受拉钢筋面积 |  |  |
| UpAsc | REAL | False | 上铁-受拉时计算得到下部受压钢筋面积 |  |  |
| UpAscCal | REAL | False | 上铁-受拉时计算得到下部计算受压钢筋面积 |  |  |
| UpAsRatio | REAL | False | 上铁-配筋率 |  |  |
| UpMaxAsRatio | REAL | False | 上铁-最大配筋率 |  |  |
| UpMinAsRatio | REAL | False | 上铁-最小配筋率 |  |  |
| UpLDCombIDM | INTEGER | False | 上铁-设计内力组合号 |  |  |
| UpMInf | TEXT | False | 上铁-正截面设计时的控制内力 |  |  |
| UpAsTow | INTEGER | False | 上铁-分塔计算时对应的塔号 |  |  |
| DwAs | REAL | False | 下铁-受拉钢筋面积 |  |  |
| DwAsCal | REAL | False | 下铁-计算受拉钢筋面积 |  |  |
| DwAsc | REAL | False | 下铁-受拉时计算得到下部受压钢筋面积 |  |  |
| DwAscCal | REAL | False | 下铁-受拉时计算得到下部计算受压钢筋面积 |  |  |
| DwAsRatio | REAL | False | 下铁-配筋率 |  |  |
| DwMaxAsRatio | REAL | False | 下铁-最大配筋率 |  |  |
| DwMinAsRatio | REAL | False | 下铁-最小配筋率 |  |  |
| DwLDCombIDM | INTEGER | False | 下铁-设计内力组合号 |  |  |
| DwMInf | TEXT | False | 下铁-正截面设计时的控制内力 |  |  |
| DwAsTow | INTEGER | False | 下铁-分塔计算时对应的塔号 |  |  |
| XI | REAL | False | 混凝土的计算相对受压区高度 |  |  |
| XIB | REAL | False | 混凝土的界限相对受压区高度 |  |  |
| AsVT | REAL | False | 剪扭总箍筋面积(Asv+2Ast1) |  |  |
| AsVTCal | REAL | False | 剪扭总计算箍筋面积(Asv+2Ast1) |  |  |
| AsVTRatio | REAL | False | 箍筋配筋率 |  |  |
| CO | REAL | False | 斜截面验算系数 |  |  |
| VMax | REAL | False | 斜截面最大承载力 |  |  |
| LDCombIDV | INTEGER | False | 斜截面设计内力组合号 |  |  |
| VInf | TEXT | False | 斜截面设计时的控制内力 |  |  |
| AsVTow | INTEGER | False | 分塔计算时对应的塔号 |  |  |
| AsT1 | REAL | False | 受扭沿周边单肢箍筋面积 |  |  |
| AsTLCal | REAL | False | 计算受扭纵筋面积Astl |  |  |
| AsTLMin | REAL | False | 最小受扭纵筋面积 |  |  |
| LDCombIDT | INTEGER | False | 剪扭设计内力组合号 |  |  |
| TInf | TEXT | False | 剪扭设计时的控制内力 |  |  |
| AsTTow | INTEGER | False | 分塔计算时对应的塔号 |  |  |
| AsXJAs | REAL | False | 连梁斜筋面积 |  |  |
| AsXJAsCal | REAL | False | 连梁计算斜筋面积 |  |  |
| XJAng | REAL | False | 连梁斜筋角度 |  |  |
| LDCombIDXJ | INTEGER | False | 连梁斜筋对应的设计内力组合号 |  |  |
| XJInf | TEXT | False | 连梁斜筋对应的控制内力 |  |  |
| AsXJTow | INTEGER | False | 分塔计算时对应的塔号 |  |  |

dsnComBeamSect_SRC

| dsnComBeamSect_SRC |  |  |  |  |  |
|---|---|---|---|---|---|
| 梁截面-钢骨砼 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| ComKind | INTEGER | False | 构件类型 | YJKDSN::ECom |  |
| Sect | INTEGER | False | 截面ID |  |  |
| UpAs | REAL | False | 上铁-受拉钢筋面积 |  |  |
| UpAsCal | REAL | False | 上铁-计算受拉钢筋面积 |  |  |
| UpAsc | REAL | False | 上铁-受拉时计算得到下部受压钢筋面积 |  |  |
| UpAscCal | REAL | False | 上铁-受拉时计算得到下部计算受压钢筋面积 |  |  |
| UpAsRatio | REAL | False | 上铁-配筋率 |  |  |
| UpMaxAsRatio | REAL | False | 上铁-最大配筋率 |  |  |
| UpMinAsRatio | REAL | False | 上铁-最小配筋率 |  |  |
| UpLDCombIDM | INTEGER | False | 上铁-设计内力组合号 |  |  |
| UpMInf | TEXT | False | 上铁-正截面设计时的控制内力 |  |  |
| UpAsTow | INTEGER | False | 上铁-分塔计算时对应的塔号 |  |  |
| DwAs | REAL | False | 下铁-受拉钢筋面积 |  |  |
| DwAsCal | REAL | False | 下铁-计算受拉钢筋面积 |  |  |
| DwAsc | REAL | False | 下铁-受拉时计算得到下部受压钢筋面积 |  |  |
| DwAscCal | REAL | False | 下铁-受拉时计算得到下部计算受压钢筋面积 |  |  |
| DwAsRatio | REAL | False | 下铁-配筋率 |  |  |
| DwMaxAsRatio | REAL | False | 下铁-最大配筋率 |  |  |
| DwMinAsRatio | REAL | False | 下铁-最小配筋率 |  |  |
| DwLDCombIDM | INTEGER | False | 下铁-设计内力组合号 |  |  |
| DwMInf | TEXT | False | 下铁-正截面设计时的控制内力 |  |  |
| DwAsTow | INTEGER | False | 下铁-分塔计算时对应的塔号 |  |  |
| XI | REAL | False | 混凝土的计算相对受压区高度 |  |  |
| XIB | REAL | False | 混凝土的界限相对受压区高度 |  |  |
| AsVT | REAL | False | 剪扭总箍筋面积(Asv+2Ast1) |  |  |
| AsVTCal | REAL | False | 剪扭总计算箍筋面积(Asv+2Ast1) |  |  |
| AsVTRatio | REAL | False | 箍筋配筋率 |  |  |
| CO | REAL | False | 斜截面验算系数 |  |  |
| VMax | REAL | False | 斜截面最大承载力 |  |  |
| LDCombIDV | INTEGER | False | 斜截面设计内力组合号 |  |  |
| VInf | TEXT | False | 斜截面设计时的控制内力 |  |  |
| AsVTow | INTEGER | False | 分塔计算时对应的塔号 |  |  |
| AsT1 | REAL | False | 受扭沿周边单肢箍筋面积 |  |  |
| AsTLCal | REAL | False | 计算受扭纵筋面积Astl |  |  |
| AsTLMin | REAL | False | 最小受扭纵筋面积 |  |  |
| LDCombIDT | INTEGER | False | 剪扭设计内力组合号 |  |  |
| TInf | TEXT | False | 剪扭设计时的控制内力 |  |  |
| AsTTow | INTEGER | False | 分塔计算时对应的塔号 |  |  |
| AsXJAs | REAL | False | 连梁斜筋面积 |  |  |
| AsXJAsCal | REAL | False | 连梁计算斜筋面积 |  |  |
| XJAng | REAL | False | 连梁斜筋角度 |  |  |
| LDCombIDXJ | INTEGER | False | 连梁斜筋对应的设计内力组合号 |  |  |
| XJInf | TEXT | False | 连梁斜筋对应的控制内力 |  |  |
| AsXJTow | INTEGER | False | 分塔计算时对应的塔号 |  |  |
| VCon | REAL | False | 型钢混凝土中的混凝土承担的剪力 |  |  |
| COCon | REAL | False | 型钢混凝土中的混凝土斜截面验算系数 |  |  |
| VMaxCon | REAL | False | 型钢混凝土中的混凝土斜截面最大承载力 |  |  |

dsnComBeamSect_Steel

| dsnComBeamSect_Steel |  |  |  |  |  |
|---|---|---|---|---|---|
| 梁截面-钢 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| ComKind | INTEGER | False | 构件类型 | YJKDSN::ECom |  |
| Sect | INTEGER | False | 截面ID |  |  |
| UpMStrenP | REAL | False | 顶面-受压-计算应力 |  |  |
| UpFMStrenP | REAL | False | 顶面-受压-容许应力 |  |  |
| UpLDCombIDMStrenP | INTEGER | False | 顶面-受压-应力对应组合号 |  |  |
| UpMStrenPInf | TEXT | False | 顶面-受压-最大应力的控制内力 |  |  |
| UpMStrenPTow | INTEGER | False | 顶面-受压-分塔计算时对应的塔号 |  |  |
| UpMStrenT | REAL | False | 顶面-受拉-计算应力 |  |  |
| UpFMStrenT | REAL | False | 顶面-受拉-容许应力 |  |  |
| UpLDCombIDMStrenT | INTEGER | False | 顶面-受拉-应力对应组合号 |  |  |
| UpMStrenTInf | TEXT | False | 顶面-受拉-最大应力的控制内力 |  |  |
| UpMStrenTTow | INTEGER | False | 顶面-受拉-分塔计算时对应的塔号 |  |  |
| DwMStrenP | REAL | False | 底面-受压-计算应力 |  |  |
| DwFMStrenP | REAL | False | 底面-受压-容许应力 |  |  |
| DwLDCombIDMStrenP | INTEGER | False | 底面-受压-应力对应组合号 |  |  |
| DwMStrenPInf | TEXT | False | 底面-受压-最大应力的控制内力 |  |  |
| DwMStrenPTow | INTEGER | False | 底面-受压-分塔计算时对应的塔号 |  |  |
| DwMStrenT | REAL | False | 底面-受拉-计算应力 |  |  |
| DwFMStrenT | REAL | False | 底面-受拉-容许应力 |  |  |
| DwLDCombIDMStrenT | INTEGER | False | 底面-受拉-应力对应组合号 |  |  |
| DwMStrenTInf | TEXT | False | 底面-受拉-最大应力的控制内力 |  |  |
| DwMStrenTTow | INTEGER | False | 底面-受拉-分塔计算时对应的塔号 |  |  |
| UpMSta | REAL | False | 顶面-稳定-计算应力 |  |  |
| UpFMSta | REAL | False | 顶面-稳定-容许应力 |  |  |
| UpLDCombIDMSta | INTEGER | False | 顶面-稳定-应力对应组合号 |  |  |
| UpMStaInf | TEXT | False | 顶面-稳定-最大应力的控制内力 |  |  |
| UpMStaTow | INTEGER | False | 顶面-稳定-分塔计算时对应的塔号 |  |  |
| DwMSta | REAL | False | 底面-稳定-计算应力 |  |  |
| DwFMSta | REAL | False | 底面-稳定-容许应力 |  |  |
| DwLDCombIDMSta | INTEGER | False | 底面-稳定-应力对应组合号 |  |  |
| DwMStaInf | TEXT | False | 底面-稳定-最大应力的控制内力 |  |  |
| DwMStaTow | INTEGER | False | 底面-稳定-分塔计算时对应的塔号 |  |  |
| VStren | REAL | False | 抗剪-计算应力 |  |  |
| FVStren | REAL | False | 抗剪-容许应力 |  |  |
| LDCombIDVStren | INTEGER | False | 抗剪-应力对应组合号 |  |  |
| VStrenInf | TEXT | False | 抗剪-最大应力的控制内力 |  |  |
| VStrenTow | INTEGER | False | 抗剪-分塔计算时对应的塔号 |  |  |
| NStrenXN | REAL | False | 性能设计轴向-计算应力 |  |  |
| FNStrenXN | REAL | False | 性能设计轴向-容许应力 |  |  |
| LDCombIDNStrenXN | INTEGER | False | 性能设计轴向-应力对应组合号 |  |  |
| NStrenXNInf | TEXT | False | 性能设计轴向-最大应力的控制内力 |  |  |
| NStrenXNTow | INTEGER | False | 性能设计轴向-分塔计算时对应的塔号 |  |  |

dsnComBeamSect_Comp

| dsnComBeamSect_Comp |  |  |  |  |  |
|---|---|---|---|---|---|
| 梁截面-组合梁 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| ComKind | INTEGER | False | 构件类型 | YJKDSN::ECom |  |
| Sect | INTEGER | False | 截面ID |  |  |
| UpFMStren | REAL | False | 抗弯验算-上部-容许应力 |  |  |
| UpLDCombIDMStren | INTEGER | False | 抗弯验算-上部-应力对应组合号 |  |  |
| UpMStrenInf | TEXT | False | 抗弯验算-上部-最大应力的控制内力 |  |  |
| UpMStrenTow | INTEGER | False | 抗弯验算-上部-分塔计算时对应的塔号 |  |  |
| DwFMStren | REAL | False | 抗弯验算-下部-容许应力 |  |  |
| DwLDCombIDMStren | INTEGER | False | 抗弯验算-下部-应力对应组合号 |  |  |
| DwMStrenInf | TEXT | False | 抗弯验算-下部-最大应力的控制内力 |  |  |
| DwMStrenTow | INTEGER | False | 抗弯验算-下部-分塔计算时对应的塔号 |  |  |
| VStren | REAL | False | 抗剪验算-计算应力 |  |  |
| FVStren | REAL | False | 抗剪验算-容许应力 |  |  |
| LDCombIDVStren | INTEGER | False | 抗剪验算-应力对应组合号 |  |  |
| VStrenInf | TEXT | False | 抗剪验算-最大应力的控制内力 |  |  |
| VStrenTow | INTEGER | False | 抗剪验算-分塔计算时对应的塔号 |  |  |
| VS | REAL | False | 栓钉验算-容许应力 |  |  |
| CalNutNum | REAL | False | 栓钉验算-需要的最大栓钉数量 |  |  |
| NutNum | INTEGER | False | 栓钉验算-栓钉实际数量 |  |  |
| nvci | REAL | False | 栓钉验算-单个栓钉承载力 |  |  |
| LDCombIDNutStren | INTEGER | False | 栓钉验算-控制组合号 |  |  |
| NutStrenInf | TEXT | False | 栓钉验算-控制内力 |  |  |
| NutStrenTow | INTEGER | False | 栓钉验算-分塔计算时对应的塔号 |  |  |

柱
构件信息
dsnSectDefCol
[图]

| dsnSectDefCol |  |  |  |  |  |
|---|---|---|---|---|---|
| 构件信息-柱截面定义 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | ID |  |  |
| PMTotID | INTEGER | False | 建模构件ID |  |  |
| PMNo | INTEGER | False | 建模构件序号 |  |  |
| PMSectKind | INTEGER | False | 截面类型 |  |  |
| SectComKind | INTEGER | False | 所属构件类型 |  |  |
| Name | TEXT | False | 截面名称 |  |  |
| Source | INTEGER | False | 数据来源 | 枚举 | 1-PM 2-鉴定加固 3-优化设计 |
| SectInf | TEXT | False | 截面定义数据 |  |  |

dsnComColInf

| dsnComColInf |  |  |  |  |  |
|---|---|---|---|---|---|
| 构件信息-柱 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| PMTotID | INTEGER | False | 建模构件ID |  |  |
| FlrID | INTEGER | False | 层内编号 |  |  |
| ComKind | INTEGER | False | 构件类型 |  |  |
| Kind | INTEGER | False | 柱属性 | YJKDSN::EColDSN | 框架柱 框支柱 门式刚柱 构造柱 支撑贮仓的框架柱 抗风柱 |
| MatKind | INTEGER | False | 材料类型 | YJKDSN::EMat |  |
| PMMatKind | INTEGER | False | 材料类型-建模分类 |  | 5-钢 6-砼 |
| ConGrade | REAL | False | 砼标号 |  |  |
| ConGradeIn | REAL | False | 砼标号-内部 |  | 钢管砼叠合柱 |
| SteelKind | INTEGER | False | 钢号 |  |  |
| Cover | REAL | False | 保护层厚度 |  |  |
| TranHor | INTEGER | False | 是否为水平转换 |  |  |
| KZDJ | INTEGER | False | 抗震等级 |  |  |
| KZDJGZ | INTEGER | False | 抗震构造等级 |  |  |
| MainBar | INTEGER | False | 纵筋类型 |  |  |
| HoopBar | INTEGER | False | 箍筋类型 |  |  |
| Air | INTEGER | False | 是否按人防设计 |  |  |
| YZ | INTEGER | False | 是否是预制构件 |  |  |
| YYL | INTEGER | False | 是否是预应力构件 |  |  |
| WJType | INTEGER | False | 网架类别 | YJKDSN::EWJType | 网架、单层网壳、双层网壳等 |
| TrussSign | INTEGER | False | 桁架杆件标志 | YJKDSN::ETrussKind | 上弦、下弦、腹杆等 |
| XNSJM | INTEGER | False | 性能设计标志-正截面设计 |  | 弹性、不屈服 |
| XNSJV | INTEGER | False | 性能设计标志-斜截面设计 |  | 弹性、不屈服 |
| XNSJEmpSign | INTEGER | False | 构件重要性类别 |  | 1-耗能构件 2-普通构件 3-关键构件 |
| XNSJBLInf | TEXT | False | 性能设计包络标志 | dsnIModelAComProp_XNSJBL |  |
| Solid | INTEGER | False | 是否为实体元 |  |  |
| SeisVCom | INTEGER | False | 是否是指定竖向地震的构件 |  |  |
| NonLProp | INTEGER | False | 非线性数据 |  |  |
| HN | INTEGER | False | 是否是性能设计耗能构件 |  |  |
| BTRatioGrade | INTEGER | False | 宽厚比等级 |  |  |
| YXGrade | INTEGER | False | 延性等级 |  |  |
| BetaE | REAL | False | 性能系数的调整系数βe |  |  |
| RealXNXS | REAL | False | 实际性能系数 |  |  |
| TempInf | TEXT | False | 构件温度 |  | 依次记录 0-升温 1-降温 2-防火升温 |
| FHth | REAL | False | 耐火时间 |  |  |
| FHiqz | INTEGER | False | 膨胀型 |  | 1-非膨胀型 2-水泥砂浆 |
| FHri | REAL | False | 等效热阻/等效热传导系数 |  |  |
| FHdil | REAL | False | 保护层厚度 |  |  |
| FHfxz | REAL | False | 截面形状系数 |  |  |
| EnvSign | INTEGER | False | 是否包络设计 |  |  |
| DuctLevelEU | INTEGER | False | 延性等级-欧标 |  |  |
| DuctLevelUS | INTEGER | False | 延性等级-美标 |  |  |
| CurveCoe | REAL | False | 曲率系数 |  |  |
| StiffCoeInf | TEXT | False | 杆件的6个自由度对应的刚度系数 |  |  |
| PresInf | TEXT | False |  |  |  |
| TrussXID | INTEGER | False | X方向桁架编号 |  |  |
| TrussYID | INTEGER | False | Y方向桁架编号 |  |  |
| PMSectNo | INTEGER | False | 建模截面索引 |  |  |
| NodeUp | INTEGER | False | 节点ID-起始端 |  |  |
| NodeDw | INTEGER | False | 节点ID-终止端 |  |  |
| LenX | REAL | False | 局部坐标MX向柱高度(m) |  |  |
| LenY | REAL | False | 局部坐标MY向柱高度(m) |  |  |
| ClearLenX | REAL | False | 局部坐标MX向柱净高(m) |  |  |
| ClearLenY | REAL | False | 局部坐标MY向柱净高(m) |  |  |
| Ang | REAL | False | 柱布置角度（rad） |  |  |
| AngSect | REAL | False | 柱截面惯性主轴与X边夹角（rad） |  |  |
| LenCoeX | REAL | False | MX向计算长度系数 |  |  |
| LenCoeY | REAL | False | MY向计算长度系数 |  |  |
| LenCoeXWCY | REAL | False | MX向计算长度系数(无侧移) |  |  |
| LenCoeYWCY | REAL | False | MY向计算长度系数(无侧移) |  |  |
| LinkUp | INTEGER | False | 上节点连接信息 |  |  |
| LinkDw | INTEGER | False | 下节点连接信息 |  |  |
| WallColInf | TEXT | False | 与柱相连的墙 |  |  |
| DsnWithWallCol | INTEGER | False | 配筋时是否做为墙柱端柱 |  | 1-与单方向墙相连 2-与多个方向墙相连 |
| Pos | INTEGER | False | 柱位置 |  | 中柱 边柱 角柱 |
| BKZ | INTEGER | False | 边框柱标志 |  |  |
| PJZ | INTEGER | False | 排架柱标志 |  |  |
| JLJ | INTEGER | False | 剪力键标志 |  |  |
| ToBrace | INTEGER |  | 是否与支撑相连标志 |  |  |
| BarCalMethod | INTEGER |  | 配筋计算方法 |  | 单偏压 双偏压 |
| BraceKind | INTEGER |  | 支撑标志（仅对支撑有效） |  | 斜柱 斜杆 |
| BraceType | INTEGER |  | 支撑类型（仅对支撑有效） |  | 人字形 V形 十字形 一字形 |
| PortalJJLCoe | REAL |  | 门刚梁横向加劲肋间距与腹板最大高度的比值(a/Hw) |  | 0为不设加劲肋 |
| ZYB | REAL |  | 轴压比 |  |  |
| ZYBLDCombID | INTEGER |  | 轴压比对应的组合号 |  |  |
| ZYBAxis | REAL |  | 轴压比对应的轴力 |  |  |
| ZYBTow | INTEGER |  | 分塔计算时对应的塔号 |  |  |
| ZYB_ZH | REAL |  | 组合轴压比 |  |  |
| ZYBAxis_ZH | REAL |  | 组合轴压比对应的轴力 |  |  |
| ZYB_ZHLDCombID | INTEGER |  | 组合轴压比对应的组合号 |  |  |
| JKB | REAL |  | 剪跨比 |  |  |
| JKBLDCombID | INTEGER |  | 剪跨比对应的组合号 |  |  |
| JKBForce | TEXT |  | 剪跨比控制内力 |  |  |
| JKBTow | INTEGER |  | 分塔计算时对应的塔号 |  |  |
| ShearCapacityX | REAL |  | X向抗剪承载力 |  |  |
| ShearCapacityY | REAL |  | Y向抗剪承载力 |  |  |
| JGID | INTEGER |  |  |  |  |
| ColSegID | INTEGER |  | 柱段ID |  |  |

dsnComMainColInf
[图]

| dsnComMainColInf |  |  |  |  |  |
|---|---|---|---|---|---|
| 主柱基本信息表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| FlrID | INTEGER | False | 构件层内ID |  |  |
| ComInf | TEXT | False | 各柱段全楼ID |  |  |
| ComDirInf | TEXT | False | 各柱段方向是否与主梁方向一致 |  | 目前暂未存该段数据 |

dsnComCol_Con
[图]

| dsnComCol_Con |  |  |  |  |  |
|---|---|---|---|---|---|
| 构件信息-柱-砼 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| ComKind | INTEGER | False | 构件类型 | YJKDSN::ECom |  |
| Sect | INTEGER | False | 截面数量 |  |  |

dsnComCol_SRC
[图]

| dsnComCol_SRC |  |  |  |  |  |
|---|---|---|---|---|---|
| 构件信息-柱-钢骨砼 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| ComKind | INTEGER | False | 构件类型 | YJKDSN::ECom |  |
| Sect | INTEGER | False | 截面数量 |  |  |
| AMDX | REAL | False | 绕X轴长细比 |  |  |
| AMDY | REAL | False | 绕Y轴长细比 |  |  |
| AMDMax | REAL | False | 允许长细比 |  |  |
| BTRatio | REAL | False | 翼缘宽厚比 |  |  |
| BTRatioMax | REAL | False | 翼缘宽厚比限值 |  |  |
| HTRatio | REAL | False | 腹板高厚比 |  |  |
| HTRatioMax | REAL | False | 腹板高厚比限值 |  |  |

dsnComCol_RectTube
[图]

| dsnComCol_RectTube |  |  |  |  |  |
|---|---|---|---|---|---|
| 构件信息-柱-矩形钢管砼 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| ComKind | INTEGER | False | 构件类型 | YJKDSN::ECom |  |
| Sect | INTEGER | False | 截面数量 |  |  |
| AMDX | REAL | False | 绕X轴长细比 |  |  |
| AMDY | REAL | False | 绕Y轴长细比 |  |  |
| AMDMax | REAL | False | 允许长细比 |  |  |
| BTRatio | REAL | False | 管壁宽厚比 |  |  |
| BTRatioMax | REAL | False | 管壁宽厚比限值 |  |  |
| HTRatio | REAL | False | 管壁高厚比 |  |  |
| HTRatioMax | REAL | False | 管壁高厚比限值 |  |  |
| ALFAC | REAL | False | 混凝土工作承担系数 |  |  |
| ALFACMax | REAL | False | 混凝土工作承担系数限值 |  |  |

dsnComCol_CircleTube
[图]

| dsnComCol_CircleTube |  |  |  |  |  |
|---|---|---|---|---|---|
| 构件信息-柱-圆形钢管砼 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| ComKind | INTEGER | False | 构件类型 | YJKDSN::ECom |  |
| Sect | INTEGER | False | 截面数量 |  |  |
| AMDX | REAL | False | 绕X轴长细比 |  |  |
| AMDY | REAL | False | 绕Y轴长细比 |  |  |
| AMDMax | REAL | False | 允许长细比 |  |  |
| SITA | REAL | False | 套箍指标 |  |  |
| SITAMax | REAL | False | 套箍指标下限值 |  |  |
| SITAMin | REAL | False | 套箍指标上限值 |  |  |
| DTRatio | REAL | False | 径厚比 |  |  |
| DTRatioMax | REAL | False | 径厚比上限值 |  |  |

dsnComCol_TubeRein
[图]

| dsnComCol_TubeRein |  |  |  |  |  |
|---|---|---|---|---|---|
| 构件信息-柱-叠合柱 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| ComKind | INTEGER | False | 构件类型 | YJKDSN::ECom |  |
| Sect | INTEGER | False | 截面数量 |  |  |
| AMDX | REAL | False | 绕X轴长细比 |  |  |
| AMDY | REAL | False | 绕Y轴长细比 |  |  |
| AMDMax | REAL | False | 允许长细比 |  |  |
| SITA | REAL | False | 套箍指标 |  |  |
| SITAMax | REAL | False | 套箍指标下限值 |  |  |
| SITAMin | REAL | False | 套箍指标上限值 |  |  |
| DTRatio | REAL | False | 径厚比 |  |  |
| DTRatioMax | REAL | False | 径厚比上限值 |  |  |
| Roa | REAL | False |  |  |  |
| RoaMin | REAL | False |  |  |  |

dsnComCol_Steel
[图]

| dsnComCol_Steel |  |  |  |  |  |
|---|---|---|---|---|---|
| 构件信息-柱-钢 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| ComKind | INTEGER | False | 构件类型 | YJKDSN::ECom |  |
| Sect | INTEGER | False | 截面数量 |  |  |
| AMDX | REAL | False | 绕X轴长细比 |  |  |
| AMDY | REAL | False | 绕Y轴长细比 |  |  |
| AMDMax | REAL | False | 允许长细比 |  |  |
| BTRatio | REAL | False | 外伸受压翼缘宽厚比 |  |  |
| BTRatioMax | REAL | False | 外伸受压翼缘宽厚比限值 |  |  |
| HTRatio | REAL | False | 腹板高厚比 |  |  |
| HTRatioMax | REAL | False | 腹板高厚比限值 |  |  |

dsnComCol_SteelGG
[图]

| dsnComCol_SteelGG |  |  |  |  |  |
|---|---|---|---|---|---|
| 构件信息-柱-格构钢柱 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| ComKind | INTEGER | False | 构件类型 | YJKDSN::ECom |  |
| Sect | INTEGER | False | 截面数量 |  |  |
| AMDX | REAL | False | 绕X轴长细比 |  |  |
| AMDY | REAL | False | 绕Y轴长细比 |  |  |
| AMDMax | REAL | False | 允许长细比 |  |  |
| BTRatio | REAL | False | 外伸受压翼缘宽厚比 |  |  |
| BTRatioMax | REAL | False | 外伸受压翼缘宽厚比限值 |  |  |
| HTRatio | REAL | False | 腹板高厚比 |  |  |
| HTRatioMax | REAL | False | 腹板高厚比限值 |  |  |
| SITA | REAL | False | 套箍指标 |  |  |
| SITAMax | REAL | False | 套箍指标下限值 |  |  |
| SITAMin | REAL | False | 套箍指标上限值 |  |  |

计算结果
dsnComNL_Col
[图]

| dsnComNL_Col |  |  |  |  |  |
|---|---|---|---|---|---|
| 构件内力-柱 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| LDCaseID | INTEGER | False | 工况ID |  |  |
| ComKind | INTEGER | False | 构件类型 | YJKDSN::ECom |  |
| Sect | INTEGER | False | 截面ID |  |  |
| NLPreInf | TEXT | False | 内力-调整前 |  |  |
| NLAftInf | TEXT | False | 内力-调整后 |  |  |

dsnComJYB_Col

| dsnComJYB_Col |  |  |  |  |  |
|---|---|---|---|---|---|
| 剪压比-柱 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| ComKind | INTEGER | False | 构件类型 | YJKDSN::ECom |  |
| Sect | INTEGER | False | 截面ID |  |  |
| Dir | INTEGER | False | 剪压比方向 |  | 1-X 2-Y |
| JYB | REAL | False | 剪压比 |  |  |
| JYBMax | REAL | False | 剪压比限值 |  |  |
| VCal | REAL | False | 计算剪力 |  |  |
| VMax | REAL | False | 剪力限值 |  |  |
| LDCombID | INTEGER | False | 控制组合号 |  |  |
| VInf | TEXT | False | 控制内力 |  |  |
| AsTow | INTEGER | False | 控制塔号 |  |  |
| VCon | REAL | False | 型钢混凝土中的混凝土X向承担的剪力 |  |  |
| JYBMaxCon | REAL | False | 型钢混凝土中的混凝土X向斜截面验算系数 |  |  |
| VCalCon | REAL | False | 型钢混凝土中的混凝土X向斜截面计算剪应力 |  |  |
| VMaxCon | REAL | False | 型钢混凝土中的混凝土X向斜截面最大承载力 |  |  |

设计结果
dsnComColCap
[图]

| dsnComColCap |  |  |  |  |  |
|---|---|---|---|---|---|
| 构件信息-柱帽 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| ComKind | INTEGER | False | 构件类型 | YJKDSN::ECom |  |
| Pos | INTEGER | False | 建模中柱帽编号 |  |  |
| AsV | REAL | False | 抗冲切箍筋配筋面积 |  |  |
| AsVCal | REAL | False | 抗冲切箍筋计算配筋面积 |  |  |
| LDCombIDV | INTEGER | False | 抗冲切箍筋设计内力组合号 |  |  |
| VInf | TEXT | False | 抗冲切箍筋设计内力 |  |  |
| Um | REAL | False | 冲切临界截面周长 |  |  |
| Yita | REAL | False | 系数 |  |  |
| V | REAL | False | 临界截面计算剪应力(MPa) |  |  |
| CO1 | REAL | False | 不需配置箍筋的临界截面最大受剪系数 |  |  |
| CO2 | REAL | False | 配置箍筋的临界截面最大受剪系数 |  |  |
| VMax1 | REAL | False | 不需配置箍筋的临界截面最大剪应力(MPa) |  |  |
| VMax2 | REAL | False | 配置箍筋的临界截面最大剪应力(MPa) |  |  |
| AsVTow | INTEGER | False | 分塔计算时对应的塔号 |  |  |

dsnComColSect_Con

| dsnComColSect_Con |  |  |  |  |  |
|---|---|---|---|---|---|
| 柱截面-砼 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| ComKind | INTEGER | False | 构件类型 | YJKDSN::ECom |  |
| Sect | INTEGER | False | 截面ID |  |  |
| AsX | REAL | False | 纵筋-X向-配筋面积 |  |  |
| AsXCal | REAL | False | 纵筋-X向-计算面积 |  |  |
| LDCombIDMX | INTEGER | False | 纵筋-X向-控制组合号 |  |  |
| MXInf | TEXT | False | 纵筋-X向-控制内力 |  |  |
| AsXTow | INTEGER | False | 纵筋-X向-控制塔号 |  |  |
| AsXAdjSign | INTEGER | False | 纵筋-X向-调整标志 |  | 0-未调整 1-根据楼层受剪承载力调整 |
| AsY | REAL | False | 纵筋-Y向-配筋面积 |  |  |
| AsYCal | REAL | False | 纵筋-Y向-计算面积 |  |  |
| LDCombIDMY | INTEGER | False | 纵筋-Y向-控制组合号 |  |  |
| MYInf | TEXT | False | 纵筋-Y向-控制内力 |  |  |
| AsYTow | INTEGER | False | 纵筋-Y向-控制塔号 |  |  |
| AsYAdjSign | INTEGER | False | 纵筋-Y向-调整标志 |  | 0-未调整 1-根据楼层受剪承载力调整 |
| MaxAsRatio | REAL | False | 纵筋-全截面-最大配筋率 |  |  |
| MinAsRatio | REAL | False | 纵筋-全截面-最小配筋率 |  |  |
| AsCorner | REAL | False | 纵筋-角筋面积 |  |  |
| AsVX | REAL | False | 箍筋-X向-配筋面积 |  |  |
| AsVXCal | REAL | False | 箍筋-X向-计算面积 |  |  |
| LDCombIDVX | INTEGER | False | 箍筋-X向-控制组合号 |  |  |
| VXInf | TEXT | False | 箍筋-X向-控制内力 |  |  |
| JKBX | REAL | False | 箍筋-X向-剪跨比 |  |  |
| COX | REAL | False | 箍筋-X向-斜截面验算系数 |  |  |
| VMaxX | REAL | False | 箍筋-X向-抗剪承载力 |  |  |
| AsVXTow | INTEGER | False | 箍筋-X向-控制塔号 |  |  |
| AsVXAdjSign | INTEGER | False | 箍筋-X向-调整标志 |  | 0-未调整 1-根据楼层受剪承载力调整 |
| AsVY | REAL | False | 箍筋-Y向-配筋面积 |  |  |
| AsVYCal | REAL | False | 箍筋-Y向-计算面积 |  |  |
| LDCombIDVY | INTEGER | False | 箍筋-Y向-控制组合号 |  |  |
| VYInf | TEXT | False | 箍筋-Y向-控制内力 |  |  |
| JKBY | REAL | False | 箍筋-Y向-剪跨比 |  |  |
| COY | REAL | False | 箍筋-Y向-斜截面验算系数 |  |  |
| VMaxY | REAL | False | 箍筋-Y向-抗剪承载力 |  |  |
| AsVYTow | INTEGER | False | 箍筋-Y向-控制塔号 |  |  |
| AsVYAdjSign | INTEGER | False | 箍筋-Y向-调整标志 |  | 0-未调整 1-根据楼层受剪承载力调整 |
| MinAsVRatio | REAL | False | 箍筋最小体积配箍率 |  |  |

dsnComColSect_ConSPY

| dsnComColSect_ConSPY |  |  |  |  |  |
|---|---|---|---|---|---|
| 柱截面-砼-双偏压 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| ComKind | INTEGER | False | 构件类型 | YJKDSN::ECom |  |
| Sect | INTEGER | False | 截面ID |  |  |
| BarDiaCorner | REAL | False | 角筋直径 |  |  |
| BarNumB | INTEGER | False | B边钢筋根数 |  |  |
| BarDiaB | REAL | False | B边钢筋直径 |  |  |
| BarNumH | INTEGER | False | H边钢筋根数 |  |  |
| BarDiaH | REAL | False | H边钢筋直径 |  |  |

dsnComColSect_SRC

| dsnComColSect_SRC |  |  |  |  |  |
|---|---|---|---|---|---|
| 柱截面-钢骨砼 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| ComKind | INTEGER | False | 构件类型 | YJKDSN::ECom |  |
| Sect | INTEGER | False | 截面ID |  |  |
| AsX | REAL | False | 纵筋-X向-配筋面积 |  |  |
| AsXCal | REAL | False | 纵筋-X向-计算面积 |  |  |
| LDCombIDMX | INTEGER | False | 纵筋-X向-控制组合号 |  |  |
| MXInf | TEXT | False | 纵筋-X向-控制内力 |  |  |
| AsXTow | INTEGER | False | 纵筋-X向-控制塔号 |  |  |
| AsXAdjSign | INTEGER | False | 纵筋-X向-调整标志 |  | 0-未调整 1-根据楼层受剪承载力调整 |
| AsY | REAL | False | 纵筋-Y向-配筋面积 |  |  |
| AsYCal | REAL | False | 纵筋-Y向-计算面积 |  |  |
| LDCombIDMY | INTEGER | False | 纵筋-Y向-控制组合号 |  |  |
| MYInf | TEXT | False | 纵筋-Y向-控制内力 |  |  |
| AsYTow | INTEGER | False | 纵筋-Y向-控制塔号 |  |  |
| AsYAdjSign | INTEGER | False | 纵筋-Y向-调整标志 |  | 0-未调整 1-根据楼层受剪承载力调整 |
| MaxAsRatio | REAL | False | 纵筋-全截面-最大配筋率 |  |  |
| MinAsRatio | REAL | False | 纵筋-全截面-最小配筋率 |  |  |
| AsCorner | REAL | False | 纵筋-角筋面积 |  |  |
| AsVX | REAL | False | 箍筋-X向-配筋面积 |  |  |
| AsVXCal | REAL | False | 箍筋-X向-计算面积 |  |  |
| LDCombIDVX | INTEGER | False | 箍筋-X向-控制组合号 |  |  |
| VXInf | TEXT | False | 箍筋-X向-控制内力 |  |  |
| JKBX | REAL | False | 箍筋-X向-剪跨比 |  |  |
| COX | REAL | False | 箍筋-X向-斜截面验算系数 |  |  |
| VMaxX | REAL | False | 箍筋-X向-抗剪承载力 |  |  |
| AsVXTow | INTEGER | False | 箍筋-X向-控制塔号 |  |  |
| AsVXAdjSign | INTEGER | False | 箍筋-X向-调整标志 |  | 0-未调整 1-根据楼层受剪承载力调整 |
| AsVY | REAL | False | 箍筋-Y向-配筋面积 |  |  |
| AsVYCal | REAL | False | 箍筋-Y向-计算面积 |  |  |
| LDCombIDVY | INTEGER | False | 箍筋-Y向-控制组合号 |  |  |
| VYInf | TEXT | False | 箍筋-Y向-控制内力 |  |  |
| JKBY | REAL | False | 箍筋-Y向-剪跨比 |  |  |
| COY | REAL | False | 箍筋-Y向-斜截面验算系数 |  |  |
| VMaxY | REAL | False | 箍筋-Y向-抗剪承载力 |  |  |
| AsVYTow | INTEGER | False | 箍筋-Y向-控制塔号 |  |  |
| AsVYAdjSign | INTEGER | False | 箍筋-Y向-调整标志 |  | 0-未调整 1-根据楼层受剪承载力调整 |
| MinAsVRatio | REAL | False | 箍筋最小体积配箍率 |  |  |
| VXCon | REAL | False | 型钢混凝土中的混凝土X向承担的剪力 |  |  |
| COXCon | REAL | False | 型钢混凝土中的混凝土X向斜截面验算系数 |  |  |
| VMaxXCon | REAL | False | 型钢混凝土中的混凝土X向斜截面最大承载力 |  |  |
| VYCon | REAL | False | 型钢混凝土中的混凝土Y向承担的剪力 |  |  |
| COYCon | REAL | False | 型钢混凝土中的混凝土Y向斜截面验算系数 |  |  |
| VMaxYCon | REAL | False | 型钢混凝土中的混凝土Y向斜截面最大承载力 |  |  |

dsnComColSect_RectTube

| dsnComColSect_RectTube |  |  |  |  |  |
|---|---|---|---|---|---|
| 柱截面-矩形钢管砼 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| ComKind | INTEGER | False | 构件类型 | YJKDSN::ECom |  |
| Sect | INTEGER | False | 截面ID |  |  |
| StrenRatio1 | REAL | False | 强度-计算应力比 |  |  |
| StrenRatio2 | REAL | False | 强度-计算应力比 |  |  |
| FStrenRatio | REAL | False | 强度-容许应力比 |  |  |
| LDCombIDStren | INTEGER | False | 强度-控制组合号 |  |  |
| StrenInf | TEXT | False | 强度-控制内力 |  |  |
| StrenTow | INTEGER | False | 强度-控制塔号 |  |  |
| XStaRatio1 | REAL | False | 稳定-X向-计算应力比 |  |  |
| XStaRatio2 | REAL | False | 稳定-X向-计算应力比 |  |  |
| FXStaRatio | REAL | False | 稳定-X向-容许应力比 |  |  |
| LDCombIDXSta | INTEGER | False | 稳定-X向-控制组合号 |  |  |
| XStaInf | TEXT | False | 稳定-X向-控制内力 |  |  |
| XStaTow | INTEGER | False | 稳定-X向-控制塔号 |  |  |
| YStaRatio1 | REAL | False | 稳定-Y向-计算应力比 |  |  |
| YStaRatio2 | REAL | False | 稳定-Y向-计算应力比 |  |  |
| FYStaRatio | REAL | False | 稳定-Y向-容许应力比 |  |  |
| LDCombIDYSta | INTEGER | False | 稳定-Y向-控制组合号 |  |  |
| YStaInf | TEXT | False | 稳定-Y向-控制内力 |  |  |
| YStaTow | INTEGER | False | 稳定-Y向-控制塔号 |  |  |
| VXStrenRatio | REAL | False | 抗剪-X向-计算应力比 |  |  |
| FVXStrenRatio | REAL | False | 抗剪-X向-容许应力比 |  |  |
| LDCombIDVXStren | INTEGER | False | 抗剪-X向-控制组合号 |  |  |
| VXStrenInf | TEXT | False | 抗剪-X向-控制内力 |  |  |
| VXStrenTow | INTEGER | False | 抗剪-X向-控制塔号 |  |  |
| VYStrenRatio | REAL | False | 抗剪-Y向-计算应力比 |  |  |
| FVYStrenRatio | REAL | False | 抗剪-Y向-容许应力比 |  |  |
| LDCombIDVYStren | INTEGER | False | 抗剪-Y向-控制组合号 |  |  |
| VYStrenInf | TEXT | False | 抗剪-Y向-控制内力 |  |  |
| VYStrenTow | INTEGER | False | 抗剪-Y向-控制塔号 |  |  |

dsnComColSect_CircleTube

| dsnComColSect_CircleTube |  |  |  |  |  |
|---|---|---|---|---|---|
| 柱截面-圆形钢管砼 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| ComKind | INTEGER | False | 构件类型 | YJKDSN::ECom |  |
| Sect | INTEGER | False | 截面ID |  |  |
| NStrenRatio | REAL | False | 轴向-承载力之比 |  |  |
| FNStrenRatio | REAL | False | 轴向-承载力之比限值 |  |  |
| FAIL | REAL | False | 长细比影响折减系数 |  |  |
| FAIE | REAL | False | 偏心率影响折减系数 |  |  |
| LDCombIDNStren | INTEGER | False | 轴向-控制组合号 |  |  |
| NStrenInf | TEXT | False | 轴向-控制内力 |  |  |
| NStrenTow | INTEGER | False | 轴向-控制塔号 |  |  |
| MStrenRatio | REAL | False | 抗弯-承载力之比 |  |  |
| FMStrenRatio | REAL | False | 抗弯-承载力之比限值 |  |  |
| LDCombIDMStren | INTEGER | False | 抗弯-控制组合号 |  |  |
| MStrenInf | TEXT | False | 抗弯-控制内力 |  |  |
| MStrenTow | INTEGER | False | 抗弯-控制塔号 |  |  |
| VStrenRatio | REAL | False | 抗剪-承载力之比 |  |  |
| FVStrenRatio | REAL | False | 抗剪-承载力之比限值 |  |  |
| LDCombIDVStren | INTEGER | False | 抗剪-控制组合号 |  |  |
| VStrenInf | TEXT | False | 抗剪-控制内力 |  |  |
| VStrenTow | INTEGER | False | 抗剪-控制塔号 |  |  |

dsnComColSect_TubeRein

| dsnComColSect_TubeRein |  |  |  |  |  |
|---|---|---|---|---|---|
| 柱截面-叠合柱 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| ComKind | INTEGER | False | 构件类型 | YJKDSN::ECom |  |
| Sect | INTEGER | False | 截面ID |  |  |
| AsX | REAL | False | 纵筋-X向-配筋面积 |  |  |
| AsXCal | REAL | False | 纵筋-X向-计算面积 |  |  |
| LDCombIDMX | INTEGER | False | 纵筋-X向-控制组合号 |  |  |
| MXInf | TEXT | False | 纵筋-X向-控制内力 |  |  |
| AsXTow | INTEGER | False | 纵筋-X向-控制塔号 |  |  |
| AsXAdjSign | INTEGER | False | 纵筋-X向-调整标志 |  | 0-未调整 1-根据楼层受剪承载力调整 |
| AsY | REAL | False | 纵筋-Y向-配筋面积 |  |  |
| AsYCal | REAL | False | 纵筋-Y向-计算面积 |  |  |
| LDCombIDMY | INTEGER | False | 纵筋-Y向-控制组合号 |  |  |
| MYInf | TEXT | False | 纵筋-Y向-控制内力 |  |  |
| AsYTow | INTEGER | False | 纵筋-Y向-控制塔号 |  |  |
| AsYAdjSign | INTEGER | False | 纵筋-Y向-调整标志 |  | 0-未调整 1-根据楼层受剪承载力调整 |
| MaxAsRatio | REAL | False | 纵筋-全截面-最大配筋率 |  |  |
| MinAsRatio | REAL | False | 纵筋-全截面-最小配筋率 |  |  |
| AsCorner | REAL | False | 纵筋-角筋面积 |  |  |
| AsVX | REAL | False | 箍筋-X向-配筋面积 |  |  |
| AsVXCal | REAL | False | 箍筋-X向-计算面积 |  |  |
| LDCombIDVX | INTEGER | False | 箍筋-X向-控制组合号 |  |  |
| VXInf | TEXT | False | 箍筋-X向-控制内力 |  |  |
| JKBX | REAL | False | 箍筋-X向-剪跨比 |  |  |
| COX | REAL | False | 箍筋-X向-斜截面验算系数 |  |  |
| VMaxX | REAL | False | 箍筋-X向-抗剪承载力 |  |  |
| AsVXTow | INTEGER | False | 箍筋-X向-控制塔号 |  |  |
| AsVXAdjSign | INTEGER | False | 箍筋-X向-调整标志 |  |  |
| AsVY | REAL | False | 箍筋-Y向-配筋面积 |  |  |
| AsVYCal | REAL | False | 箍筋-Y向-计算面积 |  |  |
| LDCombIDVY | INTEGER | False | 箍筋-Y向-控制组合号 |  |  |
| VYInf | TEXT | False | 箍筋-Y向-控制内力 |  |  |
| JKBY | REAL | False | 箍筋-Y向-剪跨比 |  |  |
| COY | REAL | False | 箍筋-Y向-斜截面验算系数 |  |  |
| VMaxY | REAL | False | 箍筋-Y向-抗剪承载力 |  |  |
| AsVYTow | INTEGER | False | 箍筋-Y向-控制塔号 |  |  |
| AsVYAdjSign | INTEGER | False | 箍筋-Y向-调整标志 |  |  |
| MinAsVRatio | REAL | False | 箍筋最小体积配箍率 |  |  |
| NStrenRatio | REAL | False | 钢管轴压承载力-计算值 |  |  |
| FNStrenRatio | REAL | False | 钢管轴压承载力-限值 |  |  |
| LDCombIDNStren | INTEGER | False | 钢管轴压承载力-控制组合号 |  |  |
| NStrenInf | TEXT | False | 钢管轴压承载力-控制内力 |  |  |
| NStrenTow | INTEGER | False | 钢管轴压承载力-控制塔号 |  |  |

dsnComColSect_Steel

| dsnComColSect_Steel |  |  |  |  |  |
|---|---|---|---|---|---|
| 柱截面-钢 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| ComKind | INTEGER | False | 构件类型 | YJKDSN::ECom |  |
| Sect | INTEGER | False | 截面ID |  |  |
| Stren | REAL | False | 强度-计算应力比 |  |  |
| FStren | REAL | False | 强度-容许应力比 |  |  |
| LDCombIDStren | INTEGER | False | 强度-控制组合号 |  |  |
| StrenInf | TEXT | False | 强度-控制内力 |  |  |
| StrenTow | INTEGER | False | 强度-控制塔号 |  |  |
| VStren | REAL | False | 抗剪-计算应力比 |  |  |
| FVStren | REAL | False | 抗剪-容许应力比 |  |  |
| LDCombIDVStren | INTEGER | False | 抗剪-控制组合号 |  |  |
| VStrenInf | TEXT | False | 抗剪-控制内力 |  |  |
| VStrenTow | INTEGER | False | 抗剪-控制塔号 |  |  |
| XSta | REAL | False | 稳定-X向-计算应力比 |  |  |
| FXSta | REAL | False | 稳定-X向-容许应力比 |  |  |
| LDCombIDXSta | INTEGER | False | 稳定-X向-控制组合号 |  |  |
| XStaInf | TEXT | False | 稳定-X向-控制内力 |  |  |
| XStaTow | INTEGER | False | 稳定-X向-控制塔号 |  |  |
| YSta | REAL | False | 稳定-Y向-计算应力比 |  |  |
| FYSta | REAL | False | 稳定-Y向-容许应力比 |  |  |
| LDCombIDYSta | INTEGER | False | 稳定-Y向-控制组合号 |  |  |
| YStaInf | TEXT | False | 稳定-Y向-控制内力 |  |  |
| YStaTow | INTEGER | False | 稳定-Y向-控制塔号 |  |  |

节点核心区
dsnComColJoint_Con

| dsnComColJoint_Con |  |  |  |  |  |
|---|---|---|---|---|---|
| 柱节点核心区-砼 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| ComKind | INTEGER | False | 构件类型 | YJKDSN::ECom |  |
| Sect | INTEGER | False | 截面ID |  |  |
| StrongCoe | REAL | False | 节点强度系数 |  |  |
| BeamAffectCoeX | REAL | False | X向正交梁约束影响系数 |  |  |
| BeamAffectCoeY | REAL | False | Y向正交梁约束影响系数 |  |  |
| AsVX | REAL | False | X向-配筋面积 |  |  |
| AsVXCal | REAL | False | X向-计算面积 |  |  |
| LDCombIDVX | INTEGER | False | X向-控制组合号 |  |  |
| VXInf | TEXT | False | X向-控制内力 |  |  |
| COX | REAL | False | X向-斜截面验算系数 |  |  |
| FKX | REAL | False | X向-翼缘影响系数 |  |  |
| HKX | REAL | False | X向-截面高度影响系数ζh |  |  |
| NKX | REAL | False | X向-地震组合轴压比影响系数 |  |  |
| VMaxX | REAL | False | X向-最大承载力 |  |  |
| AsVXTow | INTEGER | False | X向-控制塔号 |  |  |
| AsVY | REAL | False | Y向-配筋面积 |  |  |
| AsVYCal | REAL | False | Y向-计算面积 |  |  |
| LDCombIDVY | INTEGER | False | Y向-控制组合号 |  |  |
| VYInf | TEXT | False | Y向-控制内力 |  |  |
| COY | REAL | False | Y向-斜截面验算系数 |  |  |
| FKY | REAL | False | Y向-翼缘影响系数 |  |  |
| HKY | REAL | False | Y向-截面高度影响系数ζh |  |  |
| NKY | REAL | False | Y向-地震组合轴压比影响系数 |  |  |
| VMaxY | REAL | False | Y向-最大承载力 |  |  |
| AsVYTow | INTEGER | False | Y向-控制塔号 |  |  |

dsnComColJoint_SRC

| dsnComColJoint_SRC |  |  |  |  |  |
|---|---|---|---|---|---|
| 柱节点核心区-钢骨砼 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| ComKind | INTEGER | False | 构件类型 | YJKDSN::ECom |  |
| Sect | INTEGER | False | 截面ID |  |  |
| StrongCoe | REAL | False | 节点强度系数 |  |  |
| BeamAffectCoeX | REAL | False | X向正交梁约束影响系数 |  |  |
| BeamAffectCoeY | REAL | False | Y向正交梁约束影响系数 |  |  |
| AsVX | REAL | False | X向-配筋面积 |  |  |
| AsVXCal | REAL | False | X向-计算面积 |  |  |
| LDCombIDVX | INTEGER | False | X向-控制组合号 |  |  |
| VXInf | TEXT | False | X向-控制内力 |  |  |
| COX | REAL | False | X向-斜截面验算系数 |  |  |
| FKX | REAL | False | X向-翼缘影响系数 |  |  |
| HKX | REAL | False | X向-截面高度影响系数ζh |  |  |
| NKX | REAL | False | X向-地震组合轴压比影响系数 |  |  |
| VMaxX | REAL | False | X向-最大承载力 |  |  |
| AsVXTow | INTEGER | False | X向-控制塔号 |  |  |
| AsVY | REAL | False | Y向-配筋面积 |  |  |
| AsVYCal | REAL | False | Y向-计算面积 |  |  |
| LDCombIDVY | INTEGER | False | Y向-控制组合号 |  |  |
| VYInf | TEXT | False | Y向-控制内力 |  |  |
| COY | REAL | False | Y向-斜截面验算系数 |  |  |
| FKY | REAL | False | Y向-翼缘影响系数 |  |  |
| HKY | REAL | False | Y向-截面高度影响系数ζh |  |  |
| NKY | REAL | False | Y向-地震组合轴压比影响系数 |  |  |
| VMaxY | REAL | False | Y向-最大承载力 |  |  |
| AsVYTow | INTEGER | False | Y向-控制塔号 |  |  |

dsnComColJoint_RectTube

| dsnComColJoint_RectTube |  |  |  |  |  |
|---|---|---|---|---|---|
| 柱节点核心区-矩形钢管砼 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| ComKind | INTEGER | False | 构件类型 | YJKDSN::ECom |  |
| Sect | INTEGER | False | 截面ID |  |  |
| StrongCoe | REAL | False | 节点强度系数 |  |  |
| StrenX | REAL | False | X向-梁柱应力比 |  |  |
| LDCombIDStrenX | INTEGER | False | X向-控制组合号 |  |  |
| StrenXInf | TEXT | False | X向-控制内力 |  |  |
| StrenXTow | INTEGER | False | X向-控制塔号 |  |  |
| StrenY | REAL | False | Y向-梁柱应力比 |  |  |
| LDCombIDStrenY | INTEGER | False | Y向-控制组合号 |  |  |
| StrenYInf | TEXT | False | Y向-控制内力 |  |  |
| StrenYTow | INTEGER | False | Y向-控制塔号 |  |  |

dsnComColJoint_TubeRein

| dsnComColJoint_TubeRein |  |  |  |  |  |
|---|---|---|---|---|---|
| 柱节点核心区-叠合柱 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| ComKind | INTEGER | False | 构件类型 | YJKDSN::ECom |  |
| Sect | INTEGER | False | 截面ID |  |  |
| StrongCoe | REAL | False | 节点强度系数 |  |  |
| BeamAffectCoeX | REAL | False | X向正交梁约束影响系数 |  |  |
| BeamAffectCoeY | REAL | False | Y向正交梁约束影响系数 |  |  |
| AsVX | REAL | False | X向-配筋面积 |  |  |
| AsVXCal | REAL | False | X向-计算面积 |  |  |
| LDCombIDVX | INTEGER | False | X向-控制组合号 |  |  |
| VXInf | TEXT | False | X向-控制内力 |  |  |
| COX | REAL | False | X向-斜截面验算系数 |  |  |
| FKX | REAL | False | X向-翼缘影响系数 |  |  |
| HKX | REAL | False | X向-截面高度影响系数ζh |  |  |
| NKX | REAL | False | X向-地震组合轴压比影响系数 |  |  |
| VMaxX | REAL | False | X向-最大承载力 |  |  |
| AsVXTow | INTEGER | False | X向-控制塔号 |  |  |
| AsVY | REAL | False | Y向-配筋面积 |  |  |
| AsVYCal | REAL | False | Y向-计算面积 |  |  |
| LDCombIDVY | INTEGER | False | Y向-控制组合号 |  |  |
| VYInf | TEXT | False | Y向-控制内力 |  |  |
| COY | REAL | False | Y向-斜截面验算系数 |  |  |
| FKY | REAL | False | Y向-翼缘影响系数 |  |  |
| HKY | REAL | False | Y向-截面高度影响系数ζh |  |  |
| NKY | REAL | False | Y向-地震组合轴压比影响系数 |  |  |
| VMaxY | REAL | False | Y向-最大承载力 |  |  |
| AsVYTow | INTEGER | False | Y向-控制塔号 |  |  |

dsnComColJoint_Steel

| dsnComColJoint_Steel |  |  |  |  |  |
|---|---|---|---|---|---|
| 柱节点核心区-钢 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| ComKind | INTEGER | False | 构件类型 | YJKDSN::ECom |  |
| Sect | INTEGER | False | 截面ID |  |  |
| StrongCoe | REAL | False | 节点强度系数 |  |  |
| StrenX | REAL | False | X向-梁柱应力比 |  |  |
| LDCombIDStrenX | INTEGER | False | X向-控制组合号 |  |  |
| StrenXInf | TEXT | False | X向-控制内力 |  |  |
| StrenXTow | INTEGER | False | X向-控制塔号 |  |  |
| StrenY | REAL | False | Y向-梁柱应力比 |  |  |
| LDCombIDStrenY | INTEGER | False | Y向-控制组合号 |  |  |
| StrenYInf | TEXT | False | Y向-控制内力 |  |  |
| StrenYTow | INTEGER | False | Y向-控制塔号 |  |  |

斜杆
构件信息
dsnSectDefBrace
[图]

| dsnSectDefBrace |  |  |  |  |  |
|---|---|---|---|---|---|
| 构件信息-斜杆截面定义 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | ID |  |  |
| PMTotID | INTEGER | False | 建模构件ID |  |  |
| PMNo | INTEGER | False | 建模构件序号 |  |  |
| PMSectKind | INTEGER | False | 截面类型 |  |  |
| SectComKind | INTEGER | False | 所属构件类型 |  |  |
| Name | TEXT | False | 截面名称 |  |  |
| Source | INTEGER | False | 数据来源 | 枚举 | 1-PM 2-鉴定加固 3-优化设计 |
| SectInf | TEXT | False | 截面定义数据 |  |  |

dsnComBraceInf

| dsnComBraceInf |  |  |  |  |  |
|---|---|---|---|---|---|
| 构件信息-斜杆 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| PMTotID | INTEGER | False | 建模构件ID |  |  |
| FlrID | INTEGER | False | 层内编号 |  |  |
| ComKind | INTEGER | False | 构件类型 |  |  |
| Kind | INTEGER | False | 柱属性 | YJKDSN::EColDSN | 框架柱 框支柱 门式刚柱 构造柱 支撑贮仓的框架柱 抗风柱 |
| MatKind | INTEGER | False | 材料类型 | YJKDSN::EMat |  |
| PMMatKind | INTEGER | False | 材料类型-建模分类 |  | 5-钢 6-砼 |
| ConGrade | REAL | False | 砼标号 |  |  |
| ConGradeIn | REAL | False | 砼标号-内部 |  | 钢管砼叠合柱 |
| SteelKind | INTEGER | False | 钢号 |  |  |
| Cover | REAL | False | 保护层厚度 |  |  |
| TranHor | INTEGER | False | 是否为水平转换 |  |  |
| KZDJ | INTEGER | False | 抗震等级 |  |  |
| KZDJGZ | INTEGER | False | 抗震构造等级 |  |  |
| MainBar | INTEGER | False | 纵筋类型 |  |  |
| HoopBar | INTEGER | False | 箍筋类型 |  |  |
| Air | INTEGER | False | 是否按人防设计 |  |  |
| YZ | INTEGER | False | 是否是预制构件 |  |  |
| YYL | INTEGER | False | 是否是预应力构件 |  |  |
| WJType | INTEGER | False | 网架类别 | YJKDSN::EWJType | 网架、单层网壳、双层网壳等 |
| TrussSign | INTEGER | False | 桁架杆件标志 | YJKDSN::ETrussKind | 上弦、下弦、腹杆等 |
| XNSJM | INTEGER | False | 性能设计标志-正截面设计 |  | 弹性、不屈服 |
| XNSJV | INTEGER | False | 性能设计标志-斜截面设计 |  | 弹性、不屈服 |
| XNSJEmpSign | INTEGER | False | 构件重要性类别 |  | 1-耗能构件 2-普通构件 3-关键构件 |
| XNSJBLInf | TEXT | False | 性能设计包络标志 | dsnIModelAComProp_XNSJBL |  |
| Solid | INTEGER | False | 是否为实体元 |  |  |
| SeisVCom | INTEGER | False | 是否是指定竖向地震的构件 |  |  |
| NonLProp | INTEGER | False | 非线性数据 |  |  |
| HN | INTEGER | False | 是否是性能设计耗能构件 |  |  |
| BTRatioGrade | INTEGER | False | 宽厚比等级 |  |  |
| YXGrade | INTEGER | False | 延性等级 |  |  |
| BetaE | REAL | False | 性能系数的调整系数βe |  |  |
| RealXNXS | REAL | False | 实际性能系数 |  |  |
| TempInf | TEXT | False | 构件温度 |  | 依次记录 0-升温 1-降温 2-防火升温 |
| FHth | REAL | False | 耐火时间 |  |  |
| FHiqz | INTEGER | False | 膨胀型 |  | 1-非膨胀型 2-水泥砂浆 |
| FHri | REAL | False | 等效热阻/等效热传导系数 |  |  |
| FHdil | REAL | False | 保护层厚度 |  |  |
| FHfxz | REAL | False | 截面形状系数 |  |  |
| EnvSign | INTEGER | False | 是否包络设计 |  |  |
| DuctLevelEU | INTEGER | False | 延性等级-欧标 |  |  |
| DuctLevelUS | INTEGER | False | 延性等级-美标 |  |  |
| CurveCoe | REAL | False | 曲率系数 |  |  |
| StiffCoeInf | TEXT | False | 杆件的6个自由度对应的刚度系数 |  |  |
| PresInf | TEXT | False |  |  |  |
| TrussXID | INTEGER | False | X方向桁架编号 |  |  |
| TrussYID | INTEGER | False | Y方向桁架编号 |  |  |
| PMSectNo | INTEGER | False | 建模截面索引 |  |  |
| NodeUp | INTEGER | False | 节点ID-起始端 |  |  |
| NodeDw | INTEGER | False | 节点ID-终止端 |  |  |
| LenX | REAL | False | 局部坐标MX向柱高度(m) |  |  |
| LenY | REAL | False | 局部坐标MY向柱高度(m) |  |  |
| ClearLenX | REAL | False | 局部坐标MX向柱净高(m) |  |  |
| ClearLenY | REAL | False | 局部坐标MY向柱净高(m) |  |  |
| Ang | REAL | False | 柱布置角度（rad） |  |  |
| AngSect | REAL | False | 柱截面惯性主轴与X边夹角（rad） |  |  |
| LenCoeX | REAL | False | MX向计算长度系数 |  |  |
| LenCoeY | REAL | False | MY向计算长度系数 |  |  |
| LenCoeXWCY | REAL | False | MX向计算长度系数(无侧移) |  |  |
| LenCoeYWCY | REAL | False | MY向计算长度系数(无侧移) |  |  |
| LinkUp | INTEGER | False | 上节点连接信息 |  |  |
| LinkDw | INTEGER | False | 下节点连接信息 |  |  |
| WallColInf | TEXT | False | 与柱相连的墙 |  |  |
| DsnWithWallCol | INTEGER | False | 配筋时是否做为墙柱端柱 |  | 1-与单方向墙相连 2-与多个方向墙相连 |
| Pos | INTEGER | False | 柱位置 |  | 中柱 边柱 角柱 |
| BKZ | INTEGER | False | 边框柱标志 |  |  |
| PJZ | INTEGER | False | 排架柱标志 |  |  |
| JLJ | INTEGER | False | 剪力键标志 |  |  |
| ToBrace | INTEGER |  | 是否与支撑相连标志 |  |  |
| BarCalMethod | INTEGER |  | 配筋计算方法 |  | 单偏压 双偏压 |
| BraceKind | INTEGER |  | 支撑标志（仅对支撑有效） |  | 斜柱 斜杆 |
| BraceType | INTEGER |  | 支撑类型（仅对支撑有效） |  | 人字形 V形 十字形 一字形 |
| PortalJJLCoe | REAL |  | 门刚梁横向加劲肋间距与腹板最大高度的比值(a/Hw) |  | 0为不设加劲肋 |
| ZYB | REAL |  | 轴压比 |  |  |
| ZYBLDCombID | INTEGER |  | 轴压比对应的组合号 |  |  |
| ZYBAxis | REAL |  | 轴压比对应的轴力 |  |  |
| ZYBTow | INTEGER |  | 分塔计算时对应的塔号 |  |  |
| ZYB_ZH | REAL |  | 组合轴压比 |  |  |
| ZYBAxis_ZH | REAL |  | 组合轴压比对应的轴力 |  |  |
| ZYB_ZHLDCombID | INTEGER |  | 组合轴压比对应的组合号 |  |  |
| JKB | REAL |  | 剪跨比 |  |  |
| JKBLDCombID | INTEGER |  | 剪跨比对应的组合号 |  |  |
| JKBForce | TEXT |  | 剪跨比控制内力 |  |  |
| JKBTow | INTEGER |  | 分塔计算时对应的塔号 |  |  |
| ShearCapacityX | REAL |  | X向抗剪承载力 |  |  |
| ShearCapacityY | REAL |  | Y向抗剪承载力 |  |  |
| JGID | INTEGER |  |  |  |  |
| AngX | REAL |  | 与X轴夹角（rad） |  |  |
| AngY | REAL |  | 与Y轴夹角（rad） |  |  |
| AngZ | REAL |  | 与Z轴夹角（rad） |  |  |
| LinkTotID | INTEGER |  | 支撑对应的连接编号 |  |  |
| BRBSign | INTEGER |  | 屈曲约束支撑标志 |  |  |
| BraceSegID | INTEGER |  | 斜杆段ID |  |  |

计算结果
dsnComNL_Brace
[图]

| dsnComNL_Brace |  |  |  |  |  |
|---|---|---|---|---|---|
| 构件内力-斜杆 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| LDCaseID | INTEGER | False | 工况ID |  |  |
| ComKind | INTEGER | False | 构件类型 | YJKDSN::ECom |  |
| Sect | INTEGER | False | 截面ID |  |  |
| NLPreInf | TEXT | False | 内力-调整前 |  |  |
| NLAftInf | TEXT | False | 内力-调整后 |  |  |

墙柱
构件信息
dsnSectDefWall
[图]

| dsnSectDefWall |  |  |  |  |  |
|---|---|---|---|---|---|
| 构件信息-墙截面定义 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | ID |  |  |
| PMTotID | INTEGER | False | 建模构件ID |  |  |
| PMNo | INTEGER | False | 建模构件序号 |  |  |
| PMSectKind | INTEGER | False | 截面类型 |  |  |
| SectComKind | INTEGER | False | 所属构件类型 |  |  |
| Name | TEXT | False | 截面名称 |  |  |
| Source | INTEGER | False | 数据来源 | 枚举 | 1-PM 2-鉴定加固 3-优化设计 |
| T | REAL | False | 墙厚m |  |  |
| T1 | REAL | False | 钢板厚m |  | 对于外包为单侧钢板厚 |

dsnComWallColInf

| dsnComWallColInf |  |  |  |  |  |
|---|---|---|---|---|---|
| 构件信息-墙柱 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| PMTotID | INTEGER | False | 建模构件ID |  |  |
| FlrID | INTEGER | False | 层内编号 |  |  |
| ComKind | INTEGER | False | 构件类型 |  |  |
| Kind | INTEGER | False | 墙属性 | YJKDSN::EWallKind | 普通墙 短肢剪力墙 防屈曲钢板墙 |
| MatKind | INTEGER | False | 材料类型 | YJKDSN::EMat |  |
| PMMatKind | INTEGER | False | 材料类型-建模分类 |  | 5-钢 6-砼 |
| ConGrade | REAL | False | 砼标号 |  |  |
| ConGradeIn | REAL | False | 砼标号-内部 |  | 钢管砼叠合柱 |
| SteelKind | INTEGER | False | 钢号 |  |  |
| Cover | REAL | False | 保护层厚度 |  |  |
| TranHor | INTEGER | False | 是否为水平转换 |  |  |
| KZDJ | INTEGER | False | 抗震等级 |  |  |
| KZDJGZ | INTEGER | False | 抗震构造等级 |  |  |
| MainBar | INTEGER | False | 纵筋类型 |  |  |
| HoopBar | INTEGER | False | 箍筋类型 |  |  |
| Air | INTEGER | False | 是否按人防设计 |  |  |
| YZ | INTEGER | False | 是否是预制构件 |  |  |
| YYL | INTEGER | False | 是否是预应力构件 |  |  |
| WJType | INTEGER | False | 网架类别 | YJKDSN::EWJType | 网架、单层网壳、双层网壳等 |
| TrussSign | INTEGER | False | 桁架杆件标志 | YJKDSN::ETrussKind | 上弦、下弦、腹杆等 |
| XNSJM | INTEGER | False | 性能设计标志-正截面设计 |  | 弹性、不屈服 |
| XNSJV | INTEGER | False | 性能设计标志-斜截面设计 |  | 弹性、不屈服 |
| XNSJEmpSign | INTEGER | False | 构件重要性类别 |  | 1-耗能构件 2-普通构件 3-关键构件 |
| XNSJBLInf | TEXT | False | 性能设计包络标志 | dsnIModelAComProp_XNSJBL |  |
| Solid | INTEGER | False | 是否为实体元 |  |  |
| SeisVCom | INTEGER | False | 是否是指定竖向地震的构件 |  |  |
| NonLProp | INTEGER | False | 非线性数据 |  |  |
| HN | INTEGER | False | 是否是性能设计耗能构件 |  |  |
| BTRatioGrade | INTEGER | False | 宽厚比等级 |  |  |
| YXGrade | INTEGER | False | 延性等级 |  |  |
| BetaE | REAL | False | 性能系数的调整系数βe |  |  |
| RealXNXS | REAL | False | 实际性能系数 |  |  |
| TempInf | TEXT | False | 构件温度 |  | 依次记录 0-升温 1-降温 2-防火升温 |
| FHth | REAL | False | 耐火时间 |  |  |
| FHiqz | INTEGER | False | 膨胀型 |  | 1-非膨胀型 2-水泥砂浆 |
| FHri | REAL | False | 等效热阻/等效热传导系数 |  |  |
| FHdil | REAL | False | 保护层厚度 |  |  |
| FHfxz | REAL | False | 截面形状系数 |  |  |
| EnvSign | INTEGER | False | 是否包络设计 |  |  |
| DuctLevelEU | INTEGER | False | 延性等级-欧标 |  |  |
| DuctLevelUS | INTEGER | False | 延性等级-美标 |  |  |
| CurveCoe | REAL | False | 曲率系数 |  |  |
| StiffCoeInf | TEXT | False | 杆件的6个自由度对应的刚度系数 |  |  |
| PresInf | TEXT | False |  |  |  |
| TrussXID | INTEGER | False | X方向桁架编号 |  |  |
| TrussYID | INTEGER | False | Y方向桁架编号 |  |  |
| NodeUpInf | TEXT | False | 节点ID-顶 |  |  |
| NodeDwInf | TEXT | False | 节点ID-底 |  |  |
| NodeLInf | TEXT | False | 竖向节点组-起始端（顶） |  |  |
| NodeRInf | TEXT | False | 竖向节点组-终止端（底） |  |  |
| SteelT | REAL | False | 钢板厚度 |  |  |
| B | REAL | False | 厚度-顶 |  |  |
| BDw | REAL | False | 厚度-底 |  |  |
| H | REAL | False | 截面高度 |  |  |
| Len | REAL | False | 竖向高度 |  |  |
| RealLen | REAL | False | 竖向实际高度 |  |  |
| LenCoeX | REAL | False | 计算长度系数-X向 |  |  |
| LenCoeY | REAL | False | 计算长度系数-Y向 |  |  |
| TUSKind | INTEGER | False |  |  |  |
| SZQ | INTEGER | False | 双肢墙标志 |  |  |
| JQ | INTEGER | False | 加强区标志 |  | 加强区 加强区上一层 非加强区 |
| BarCalMethod | INTEGER | False | 配筋计算方法 |  | 单偏压 双偏压 |
| PJSymmetrical | INTEGER | False | 是否对称配筋 |  |  |
| VerBarKind | INTEGER | False | 竖向分布筋类型 |  |  |
| AsVRatio | REAL | False | 竖向分布筋配筋率 |  |  |
| AsHMinRatio | REAL | False | 水平分布筋最小配筋率 |  |  |
| DesignByCol | INTEGER | False | 是否按柱设计 |  |  |
| ZYB | REAL | False | 轴压比 |  |  |
| ZYBAxis | REAL | False | 轴压比对应的轴力 |  |  |
| ZYBLDCombID | INTEGER | False | 轴压比对应的组合号 |  |  |
| ZYBTow | INTEGER | False | 分塔计算时对应的塔号 |  |  |
| ZYB_ZH | REAL | False | 组合轴压比 |  |  |
| ZYBAxis_ZH | REAL | False | 组合轴压比对应的轴力 |  |  |
| ZYB_ZHLDCombID | INTEGER | False | 组合轴压比对应的组合号 |  |  |
| ZYBSectSign | INTEGER | False |  |  |  |
| JKB | REAL | False | 剪跨比 |  |  |
| JKBLDCombID | INTEGER | False | 剪跨比对应的组合号 |  |  |
| JKBForce | TEXT | False | 剪跨比控制内力 |  |  |
| JKBTow | INTEGER | False | 分塔计算时对应的塔号 |  |  |
| ColSTotID | INTEGER | False |  |  |  |
| ColETotID | INTEGER | False |  |  |  |
| ColInf | TEXT | False | 与墙相连的柱 |  |  |
| BeamInf | TEXT | False | 与墙相连的梁 |  |  |
| BtmWallColTotID | INTEGER | False | 与墙相连的墙 |  |  |
| ShearCapacityX | REAL | False | X向抗剪承载力 |  |  |
| ShearCapacityY | REAL | False | Y向抗剪承载力 |  |  |

dsnComWallAssInf

| dsnComWallAssInf |  |  |  |  |  |
|---|---|---|---|---|---|
| 构件信息-组合墙 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| FlrID | INTEGER | False | 层内编号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| Type | INTEGER | False | 配筋时用到的相交墙形式 |  | 一字形 L形 T形 |
| CrossType | INTEGER | False | 实际的相交墙形式 |  | 一字形 L形 T形 |
| Kind | INTEGER | False | 边缘构件类型 |  | 约束边缘构件 构造边缘构件 |
| SeisLevel_Detail | INTEGER | False | 抗震构造等级 |  |  |
| ConGrade | REAL | False | 砼标号 |  |  |
| MainBar | INTEGER | False | 纵筋类型 |  |  |
| HoopBar | INTEGER | False | 箍筋类型 |  |  |
| NodeHost | INTEGER | False | 主节点ID |  |  |
| NodeAppendNumInf | TEXT | False | 从节点ID |  |  |
| WallColInf | TEXT | False | 边缘构件所连墙的ID |  |  |
| LCInf | TEXT | False | 约束边缘构件Lc |  |  |
| LSInf | TEXT | False | 阴影区长度 |  |  |
| ColTotID | INTEGER | False | 端柱ID |  |  |

dsnComWallColFlangeInf

| dsnComWallColFlangeInf |  |  |  |  |  |
|---|---|---|---|---|---|
| 构件信息-墙柱翼缘 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| dsnType | INTEGER | False | 设计类型 |  | 正截面设计 斜截面设计 |
| WallColLUTotID | INTEGER | False | 左上墙柱-ID |  |  |
| NodeLU | INTEGER | False | 左上墙柱-与腹板墙交点编号 |  |  |
| NodeLUE | INTEGER | False | 左上墙柱-端头节点编号 |  | 非墙柱端点为0 |
| NodeLUEInf | TEXT | False | 左上墙柱-终止端节点坐标 |  |  |
| WallColRUTotID | INTEGER | False | 右上墙柱-ID |  |  |
| NodeRU | INTEGER | False | 右上墙柱-与腹板墙交点编号 |  |  |
| NodeRUE | INTEGER | False | 右上墙柱-端头节点编号 |  | 非墙柱端点为0 |
| NodeRUEInf | TEXT | False | 右上墙柱-终止端节点坐标 |  |  |
| WallColLDTotID | INTEGER | False | 左下墙柱-ID |  |  |
| NodeLD | INTEGER | False | 左下墙柱-与腹板墙交点编号 |  |  |
| NodeLDE | INTEGER | False | 左下墙柱-端头节点编号 |  | 非墙柱端点为0 |
| NodeLDEInf | TEXT | False | 左下墙柱-终止端节点坐标 |  |  |
| WallColRDTotID | INTEGER | False | 右下墙柱-ID |  |  |
| NodeRD | INTEGER | False | 右下墙柱-与腹板墙交点编号 |  |  |
| NodeRDE | INTEGER | False | 右下墙柱-端头节点编号 |  | 非墙柱端点为0 |
| NodeRDEInf | TEXT | False | 右下墙柱-终止端节点坐标 |  |  |
| WallColWebTotID | INTEGER | False | 腹板墙ID |  |  |
| ColSTotID | INTEGER | False | 上端柱ID |  |  |
| ColETotID | INTEGER | False | 下端柱ID |  |  |
| NodeBase | INTEGER | False | 定位点编号 |  |  |
| NodeUp | INTEGER | False | 上端头节点编号 |  |  |
| NodeUpInf | TEXT | False | 上端头节点坐标 |  |  |
| NodeDw | INTEGER | False | 下端头节点编号 |  |  |
| NodeDwInf | TEXT | False | 下端头节点坐标 |  |  |

dsnComWallCol_Con

| dsnComWallCol_Con |  |  |  |  |  |
|---|---|---|---|---|---|
| 构件信息-墙柱-砼 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| ComKind | INTEGER | False | 构件类型 | YJKDSN::ECom |  |
| Sect | INTEGER | False | 截面数量 |  |  |

dsnComWallCol_ConMW

| dsnComWallCol_ConMW |  |  |  |  |  |
|---|---|---|---|---|---|
| 构件信息-墙柱-砼-面外设计 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| SectH | INTEGER | False | 截面数量-竖向从左至右配筋结果 |  |  |
| SectV | INTEGER | False | 截面数量-水平从上至下配筋结果 |  |  |

dsnComWallCol_SRC

| dsnComWallCol_SRC |  |  |  |  |  |
|---|---|---|---|---|---|
| 构件信息-墙柱-钢骨砼 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| ComKind | INTEGER | False | 构件类型 | YJKDSN::ECom |  |
| Sect | INTEGER | False | 截面数量 |  |  |

dsnComWallCol_RectTube

| dsnComWallCol_RectTube |  |  |  |  |  |
|---|---|---|---|---|---|
| 构件信息-墙柱-外包钢板砼 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| ComKind | INTEGER | False | 构件类型 | YJKDSN::ECom |  |
| Sect | INTEGER | False | 截面数量 |  |  |
| THRatio | REAL | False | 钢板与厚度之比 |  |  |
| THRatioMax | REAL | False | 钢板与厚度之比最小值 |  |  |
| THRatioMin | REAL | False | 钢板与厚度之比最大值 |  |  |

dsnComWallCol_Steel

| dsnComWallCol_Steel |  |  |  |  |  |
|---|---|---|---|---|---|
| 构件信息-墙柱-钢板剪力墙 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| ComKind | INTEGER | False | 构件类型 | YJKDSN::ECom |  |
| Sect | INTEGER | False | 截面数量 |  |  |
| AMD | REAL | False | 高厚比 |  |  |
| AMDMax | REAL | False | 允许最大高厚比 |  |  |
| AMDMin | REAL | False | 允许最小高厚比 |  |  |
| KGRatio | REAL | False | 跨高比 |  |  |
| KGRatioMax | REAL | False | 允许最大跨高比 |  |  |
| KGRatioMin | REAL | False | 允许最小跨高比 |  |  |

计算结果
dsnComNL_WallCol
[图]

| dsnComNL_WallCol |  |  |  |  |  |
|---|---|---|---|---|---|
| 构件内力-墙柱 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| LDCaseID | INTEGER | False | 工况ID |  |  |
| ComKind | INTEGER | False | 构件类型 | YJKDSN::ECom |  |
| Sect | INTEGER | False | 截面ID |  |  |
| NLPreInf | TEXT | False | 内力-调整前 |  |  |
| NLAftInf | TEXT | False | 内力-调整后 |  |  |

dsnComJYB_WallCol

| dsnComJYB_WallCol |  |  |  |  |  |
|---|---|---|---|---|---|
| 剪压比-墙柱 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| ComKind | INTEGER | False | 构件类型 | YJKDSN::ECom |  |
| Sect | INTEGER | False | 截面ID |  |  |
| Dir | INTEGER | False | 剪压比方向 |  | 1-X 2-Y |
| JYB | REAL | False | 剪压比 |  |  |
| JYBMax | REAL | False | 剪压比限值 |  |  |
| VCal | REAL | False | 计算剪力 |  |  |
| VMax | REAL | False | 剪力限值 |  |  |
| LDCombID | INTEGER | False | 控制组合号 |  |  |
| VInf | TEXT | False | 控制内力 |  |  |
| AsTow | INTEGER | False | 控制塔号 |  |  |
| VCon | REAL | False | 型钢混凝土中的混凝土X向承担的剪力 |  |  |
| JYBMaxCon | REAL | False | 型钢混凝土中的混凝土X向斜截面验算系数 |  |  |
| VCalCon | REAL | False | 型钢混凝土中的混凝土X向斜截面计算剪应力 |  |  |
| VMaxCon | REAL | False | 型钢混凝土中的混凝土X向斜截面最大承载力 |  |  |

dsnComWallColStab_Con

| dsnComWallColStab_Con |  |  |  |  |  |
|---|---|---|---|---|---|
| 墙柱稳定-砼 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| StaSectKind | INTEGER | False | 稳定验算时的截面类型 |  | 矩形 T形 L形 槽形 工字形 |
| StaPos | INTEGER | False | 验算位置 | YJKDSN::EWallSta | 翼缘 腹板 |
| StaLen | REAL | False | 墙肢长度 |  |  |
| LDCombID | INTEGER | False | 控制组合号 |  |  |
| ForceInf | TEXT | False | 控制内力 |  |  |
| Re | REAL | False | 承载力抗震调整系数 |  |  |
| ZHLDCombID | INTEGER | False | 整体稳定验算-控制组合号 |  |  |
| ZHForceInf | TEXT | False | 整体稳定验算-控制内力 |  |  |
| ZHRe | REAL | False | 整体稳定验算-承载力抗震调整系数 |  |  |
| StaTow | INTEGER | False | 控制塔号 |  |  |
| LimitInf | TEXT | False | 超限标志 |  |  |

设计结果
dsnComWallColSect_Con

| dsnComWallColSect_Con |  |  |  |  |  |
|---|---|---|---|---|---|
| 墙柱截面-砼 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| ComKind | INTEGER | False | 构件类型 | YJKDSN::ECom |  |
| Sect | INTEGER | False | 截面ID |  |  |
| AsS | REAL | False | 下端暗柱-配筋面积 |  |  |
| AsSCal | REAL | False | 下端暗柱-计算面积 |  |  |
| AsSRatio | REAL | False | 下端暗柱-全截面配筋率 |  |  |
| LDCombIDMS | INTEGER | False | 下端暗柱-控制组合号 |  |  |
| MSInf | TEXT | False | 下端暗柱-控制内力 |  |  |
| AsSTow | INTEGER | False | 下端暗柱-控制塔号 |  |  |
| AsE | REAL | False | 上端暗柱-配筋面积 |  |  |
| AsECal | REAL | False | 上端暗柱-计算面积 |  |  |
| AsERatio | REAL | False | 上端暗柱-全截面配筋率 |  |  |
| LDCombIDME | INTEGER | False | 上端暗柱-控制组合号 |  |  |
| MEInf | TEXT | False | 上端暗柱-控制内力 |  |  |
| AsETow | INTEGER | False | 上端暗柱-控制塔号 |  |  |
| MaxAsRatio | REAL | False | 暗柱-最大配筋率 |  |  |
| AsH | REAL | False | 水平分布筋-配筋面积 |  |  |
| AsHCal | REAL | False | 水平分布筋-计算面积 |  |  |
| MinAsHRatio | REAL | False | 水平分布筋-最小配筋率 |  |  |
| LDCombIDV | INTEGER | False | 水平分布筋-控制组合号 |  |  |
| VInf | TEXT | False | 水平分布筋-控制内力 |  |  |
| JKB | REAL | False | 水平分布筋-剪跨比 |  |  |
| CO | REAL | False | 水平分布筋-斜截面验算系数 |  |  |
| VCal | REAL | False | 斜截面-计算剪应力 |  |  |
| VMax | REAL | False | 斜截面-容许剪应力 |  |  |
| AsHTow | INTEGER | False | 水平分布筋-控制塔号 |  |  |
| AsHAdjSign | INTEGER | False | 水平分布筋-调整标志 |  | 0-未调整 1-根据楼层受剪承载力调整 |
| aaS | REAL | False | 下端暗柱长度 |  |  |
| aaE | REAL | False | 上端暗柱长度 |  |  |

dsnComWallColSect_ConMW

| dsnComWallColSect_ConMW |  |  |  |  |  |
|---|---|---|---|---|---|
| 墙柱截面-砼-面外设计 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| Dir | INTEGER | False | 方向ID |  |  |
| Sect | INTEGER | False | 截面ID |  |  |
| UpAs | REAL | False | 上部-受拉钢筋面积 |  |  |
| UpAsCal | REAL | False | 上部-计算受拉钢筋面积 |  |  |
| UpAsc | REAL | False | 上部-受拉时计算得到下部受压钢筋面积 |  |  |
| UpAscCal | REAL | False | 上部-受拉时计算得到下部计算受压钢筋面积 |  |  |
| UpAsRatio | REAL | False | 上部-配筋率 |  |  |
| UpMaxAsRatio | REAL | False | 上部-最大配筋率 |  |  |
| UpMinAsRatio | REAL | False | 上部-最小配筋率 |  |  |
| UpLDCombIDM | INTEGER | False | 上部-控制组合号 |  |  |
| UpMInf | TEXT | False | 上部-控制内力 |  |  |
| UpNode | INTEGER | False | 上部-节点号 |  |  |
| UpAsTow | INTEGER | False | 上部-控制塔号 |  |  |
| DwAs | REAL | False | 下部-受拉钢筋面积 |  |  |
| DwAsCal | REAL | False | 下部-计算受拉钢筋面积 |  |  |
| DwAsc | REAL | False | 下部-受拉时计算得到下部受压钢筋面积 |  |  |
| DwAscCal | REAL | False | 下部-受拉时计算得到下部计算受压钢筋面积 |  |  |
| DwAsRatio | REAL | False | 下部-配筋率 |  |  |
| DwMaxAsRatio | REAL | False | 下部-最大配筋率 |  |  |
| DwMinAsRatio | REAL | False | 下部-最小配筋率 |  |  |
| DwLDCombIDM | INTEGER | False | 下部-控制组合号 |  |  |
| DwMInf | TEXT | False | 下部-控制内力 |  |  |
| DwNode | INTEGER | False | 下部-节点号 |  |  |
| DwAsTow | INTEGER | False | 下部-控制塔号 |  |  |
| XI | REAL | False | 混凝土的计算相对受压区高度 |  |  |
| XIB | REAL | False | 混凝土的界限相对受压区高度 |  |  |
| AsVT | REAL | False | 抗剪-剪扭总箍筋面积(Asv+2Ast1) |  |  |
| AsVTCal | REAL | False | 抗剪-剪扭总计算箍筋面积(Asv+2Ast1) |  |  |
| AsVTRatio | REAL | False | 抗剪-箍筋配筋率 |  |  |
| CO | REAL | False | 抗剪-斜截面验算系数 |  |  |
| VMax | REAL | False | 抗剪-斜截面最大承载力 |  |  |
| LDCombIDV | INTEGER | False | 抗剪-控制组合号 |  |  |
| VInf | TEXT | False | 抗剪-控制内力 |  |  |
| AsVTow | INTEGER | False | 抗剪-控制塔号 |  |  |
| AsT1 | REAL | False | 受扭沿周边单肢箍筋面积 |  |  |
| AsTLCal | REAL | False | 计算受扭纵筋面积Astl |  |  |
| AsTLMin | REAL | False | 最小受扭纵筋面积 |  |  |
| LDCombIDT | INTEGER | False | 剪扭-控制组合号 |  |  |
| TInf | TEXT | False | 剪扭-控制内力 |  |  |
| AsTTow | INTEGER | False | 剪扭-控制塔号 |  |  |

dsnComWallColSect_ConSPY

| dsnComWallColSect_ConSPY |  |  |  |  |  |
|---|---|---|---|---|---|
| 墙柱截面-砼-双偏压 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| ComKind | INTEGER | False | 构件类型 | YJKDSN::ECom |  |
| Sect | INTEGER | False | 截面ID |  |  |
| BarNumS | INTEGER | False | 起始端钢筋根数 |  |  |
| BarDiaS | REAL | False | 起始端钢筋直径 |  |  |
| BarNumE | INTEGER | False | 终止端钢筋根数 |  |  |
| BarDiaE | REAL | False | 终止端钢筋直径 |  |  |
| VerBarNum | INTEGER | False | 分布钢筋根数 |  |  |
| VerBarDia | REAL | False | 分布钢筋直径 |  |  |
| VerBarSpace | REAL | False | 分布钢筋间距 |  |  |
| VerByGZ | INTEGER | False | 分布钢筋是否是构造控制 |  | 0-计算 1-构造 |

dsnComWallColSect_SRC

| dsnComWallColSect_SRC |  |  |  |  |  |
|---|---|---|---|---|---|
| 墙柱截面-钢骨砼 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| ComKind | INTEGER | False | 构件类型 | YJKDSN::ECom |  |
| Sect | INTEGER | False | 截面ID |  |  |
| AsS | REAL | False | 下端暗柱-配筋面积 |  |  |
| AsSCal | REAL | False | 下端暗柱-计算面积 |  |  |
| AsSRatio | REAL | False | 下端暗柱-全截面配筋率 |  |  |
| LDCombIDMS | INTEGER | False | 下端暗柱-控制组合号 |  |  |
| MSInf | TEXT | False | 下端暗柱-控制内力 |  |  |
| AsSTow | INTEGER | False | 下端暗柱-控制塔号 |  |  |
| AsE | REAL | False | 上端暗柱-配筋面积 |  |  |
| AsECal | REAL | False | 上端暗柱-计算面积 |  |  |
| AsERatio | REAL | False | 上端暗柱-全截面配筋率 |  |  |
| LDCombIDME | INTEGER | False | 上端暗柱-控制组合号 |  |  |
| MEInf | TEXT | False | 上端暗柱-控制内力 |  |  |
| AsETow | INTEGER | False | 上端暗柱-控制塔号 |  |  |
| MaxAsRatio | REAL | False | 暗柱-最大配筋率 |  |  |
| AsH | REAL | False | 水平分布筋-配筋面积 |  |  |
| AsHCal | REAL | False | 水平分布筋-计算面积 |  |  |
| MinAsHRatio | REAL | False | 水平分布筋-最小配筋率 |  |  |
| LDCombIDV | INTEGER | False | 水平分布筋-控制组合号 |  |  |
| VInf | TEXT | False | 水平分布筋-控制内力 |  |  |
| JKB | REAL | False | 水平分布筋-剪跨比 |  |  |
| CO | REAL | False | 水平分布筋-斜截面验算系数 |  |  |
| VCal | REAL | False | 斜截面-计算剪应力 |  |  |
| VMax | REAL | False | 斜截面-容许剪应力 |  |  |
| AsHTow | INTEGER | False | 水平分布筋-控制塔号 |  |  |
| AsHAdjSign | INTEGER | False | 水平分布筋-调整标志 |  | 0-未调整 1-根据楼层受剪承载力调整 |
| aaS | REAL | False | 下端暗柱长度 |  |  |
| aaE | REAL | False | 上端暗柱长度 |  |  |
| VCon | REAL | False | 型钢混凝土中的混凝土承担的剪力 |  |  |

dsnComWallColSect_RectTube

| dsnComWallColSect_RectTube |  |  |  |  |  |
|---|---|---|---|---|---|
| 墙柱截面-外包钢板砼 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| ComKind | INTEGER | False | 构件类型 | YJKDSN::ECom |  |
| Sect | INTEGER | False | 截面ID |  |  |
| FMStren | REAL | False | 抗弯-承载力 |  |  |
| LDCombIDMStren | INTEGER | False | 抗弯-控制组合号 |  |  |
| MStrenInf | TEXT | False | 抗弯-控制内力 |  |  |
| MStrenTow | INTEGER | False | 抗弯-控制塔号 |  |  |
| FVStren | REAL | False | 抗剪-承载力 |  |  |
| LDCombIDVStren | INTEGER | False | 抗剪-控制组合号 |  |  |
| VStrenInf | TEXT | False | 抗剪-控制内力 |  |  |
| VStrenTow | INTEGER | False | 抗剪-控制塔号 |  |  |

dsnComWallColSect_Steel

| dsnComWallColSect_Steel |  |  |  |  |  |
|---|---|---|---|---|---|
| 墙柱截面-钢板剪力墙 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| ComKind | INTEGER | False | 构件类型 | YJKDSN::ECom |  |
| Sect | INTEGER | False | 截面ID |  |  |
| VStren | REAL | False | 抗剪-应力 |  |  |
| FVStren | REAL | False | 抗剪-容许应力 |  |  |
| LDCombIDVStren | INTEGER | False | 抗剪-控制组合号 |  |  |
| VStrenInf | TEXT | False | 抗剪-控制内力 |  |  |
| VStrenTow | INTEGER | False | 抗剪-控制塔号 |  |  |

dsnComWallColSeam_Con

| dsnComWallColSeam_Con |  |  |  |  |  |
|---|---|---|---|---|---|
| 施工缝验算-砼 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| LDCombID | INTEGER | False | 控制组合号 |  |  |
| ForceInf | TEXT | False | 控制内力 |  |  |
| Re | REAL | False | 承载力抗震调整系数 |  |  |
| SeamTow | INTEGER | False | 控制塔号 |  |  |
| LimitInf | TEXT | False | 超限标志 |  |  |

墙梁
构件信息
dsnComWallBeamInf

| dsnComWallBeamInf |  |  |  |  |  |
|---|---|---|---|---|---|
| 构件信息-墙梁 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| PMTotID | INTEGER | False | 建模构件ID |  |  |
| FlrID | INTEGER | False | 层内编号 |  |  |
| ComKind | INTEGER | False | 构件类型 |  |  |
| Kind | INTEGER | False | 梁属性 | YJKDSN::EBeamDSN |  |
| MatKind | INTEGER | False | 材料类型 | YJKDSN::EMat |  |
| PMMatKind | INTEGER | False | 材料类型-建模分类 |  | 5-钢 6-砼 |
| ConGrade | REAL | False | 砼标号 |  |  |
| ConGradeIn | REAL | False | 砼标号-内部 |  | 钢管砼叠合柱 |
| SteelKind | INTEGER | False | 钢号 |  |  |
| Cover | REAL | False | 保护层厚度 |  |  |
| TranHor | INTEGER | False | 是否为水平转换 |  |  |
| KZDJ | INTEGER | False | 抗震等级 |  |  |
| KZDJGZ | INTEGER | False | 抗震构造等级 |  |  |
| MainBar | INTEGER | False | 纵筋类型 |  |  |
| HoopBar | INTEGER | False | 箍筋类型 |  |  |
| Air | INTEGER | False | 是否按人防设计 |  |  |
| YZ | INTEGER | False | 是否是预制构件 |  |  |
| YYL | INTEGER | False | 是否是预应力构件 |  |  |
| WJType | INTEGER | False | 网架类别 | YJKDSN::EWJType | 网架、单层网壳、双层网壳等 |
| TrussSign | INTEGER | False | 桁架杆件标志 | YJKDSN::ETrussKind | 上弦、下弦、腹杆等 |
| XNSJM | INTEGER | False | 性能设计标志-正截面设计 |  | 弹性、不屈服 |
| XNSJV | INTEGER | False | 性能设计标志-斜截面设计 |  | 弹性、不屈服 |
| XNSJEmpSign | INTEGER | False | 构件重要性类别 |  | 1-耗能构件 2-普通构件 3-关键构件 |
| XNSJBLInf | TEXT | False | 性能设计包络标志 | dsnIModelAComProp_XNSJBL |  |
| Solid | INTEGER | False | 是否为实体元 |  |  |
| SeisVCom | INTEGER | False | 是否是指定竖向地震的构件 |  |  |
| NonLProp | INTEGER | False | 非线性数据 |  |  |
| HN | INTEGER | False | 是否是性能设计耗能构件 |  |  |
| BTRatioGrade | INTEGER | False | 宽厚比等级 |  |  |
| YXGrade | INTEGER | False | 延性等级 |  |  |
| BetaE | REAL | False | 性能系数的调整系数βe |  |  |
| RealXNXS | REAL | False | 实际性能系数 |  |  |
| TempInf | TEXT | False | 构件温度 |  | 依次记录 0-升温 1-降温 2-防火升温 |
| FHth | REAL | False | 耐火时间 |  |  |
| FHiqz | INTEGER | False | 膨胀型 |  | 1-非膨胀型 2-水泥砂浆 |
| FHri | REAL | False | 等效热阻/等效热传导系数 |  |  |
| FHdil | REAL | False | 保护层厚度 |  |  |
| FHfxz | REAL | False | 截面形状系数 |  |  |
| EnvSign | INTEGER | False | 是否包络设计 |  |  |
| DuctLevelEU | INTEGER | False | 延性等级-欧标 |  |  |
| DuctLevelUS | INTEGER | False | 延性等级-美标 |  |  |
| CurveCoe | REAL | False | 曲率系数 |  |  |
| StiffCoeInf | TEXT | False | 杆件的6个自由度对应的刚度系数 |  |  |
| PresInf | TEXT | False |  |  |  |
| TrussXID | INTEGER | False | X方向桁架编号 |  |  |
| TrussYID | INTEGER | False | Y方向桁架编号 |  |  |
| NodeS | INTEGER | False | 节点ID-起点 |  |  |
| NodeE | INTEGER | False | 节点ID-终点 |  |  |
| SupKindS | INTEGER | False | 支座类型-起始端 | YJKDSN::EBeamSup |  |
| SupKindE | INTEGER | False | 支座类型-终止端 | YJKDSN::EBeamSup |  |
| SteelT | REAL | False | 钢板厚度 |  |  |
| SteelH | REAL | False | 钢板高度 |  |  |
| StiffCoeM | REAL | False | 刚度折减系数 |  |  |
| XJKind | INTEGER | False | 斜筋类型 | YJKDSN::EBeamXJ |  |
| B | REAL | False | 宽度 |  |  |
| H | REAL | False | 高度 |  |  |
| SegTotID | INTEGER | False | 梁段ID |  |  |
| Span | REAL | False | 跨度 |  |  |

dsnComMainWallBeamInf
[图]

| dsnComMainWallBeamInf |  |  |  |  |  |
|---|---|---|---|---|---|
| 主墙梁基本信息表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| FlrID | INTEGER | False | 构件层内ID |  |  |
| ComInf | TEXT | False | 各梁段全楼ID |  |  |
| ComDirInf | TEXT | False | 各梁段方向是否与主梁方向一致 |  |  |

计算结果
dsnComNL_WallBeam
[图]

| dsnComNL_WallBeam |  |  |  |  |  |
|---|---|---|---|---|---|
| 构件内力-墙梁 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| LDCaseID | INTEGER | False | 工况ID |  |  |
| ComKind | INTEGER | False | 构件类型 | YJKDSN::ECom |  |
| Sect | INTEGER | False | 截面ID |  |  |
| NLPreInf | TEXT | False | 内力-调整前 |  |  |
| NLAftInf | TEXT | False | 内力-调整后 |  |  |

墙身
构件信息
dsnComWallBodyInf
[图]

| dsnComWallBodyInf |  |  |  |  |  |
|---|---|---|---|---|---|
| 墙身基本信息表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| FlrID | INTEGER | False | 构件层内ID |  |  |
| TotID | INTEGER | False | 构件全楼ID |  |  |
| B | REAL | False | 墙截面厚度(m) |  |  |
| H | REAL | False | 墙截面高度(m) |  |  |
| WallColInf | TEXT | False | 包含的墙柱ID |  |  |
| ColInf | TEXT | False | 包含的柱ID |  |  |
| SGTID | INTEGER | False | 施工图墙身编号 |  |  |

dsnComWallBodyFlangeInf

| dsnComWallBodyFlangeInf |  |  |  |  |  |
|---|---|---|---|---|---|
| 墙身翼缘信息表（该表目前缺失） |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| WallBodyID | INTEGER | False | 构件ID |  |  |
| Index | INTEGER | False | 构件序号 |  |  |
| dsnType | INTEGER | False | 设计类型 |  | 正截面设计 斜截面设计 |
| WallColLUTotID | INTEGER | False | 左上墙柱-ID |  |  |
| NodeLU | INTEGER | False | 左上墙柱-与腹板墙交点编号 |  |  |
| NodeLUE | INTEGER | False | 左上墙柱-端头节点编号 |  | 非墙柱端点为0 |
| NodeLUEInf | TEXT | False | 左上墙柱-终止端节点坐标 |  |  |
| WallColRUTotID | INTEGER | False | 右上墙柱-ID |  |  |
| NodeRU | INTEGER | False | 右上墙柱-与腹板墙交点编号 |  |  |
| NodeRUE | INTEGER | False | 右上墙柱-端头节点编号 |  | 非墙柱端点为0 |
| NodeRUEInf | TEXT | False | 右上墙柱-终止端节点坐标 |  |  |
| WallColLDTotID | INTEGER | False | 左下墙柱-ID |  |  |
| NodeLD | INTEGER | False | 左下墙柱-与腹板墙交点编号 |  |  |
| NodeLDE | INTEGER | False | 左下墙柱-端头节点编号 |  | 非墙柱端点为0 |
| NodeLDEInf | TEXT | False | 左下墙柱-终止端节点坐标 |  |  |
| WallColRDTotID | INTEGER | False | 右下墙柱-ID |  |  |
| NodeRD | INTEGER | False | 右下墙柱-与腹板墙交点编号 |  |  |
| NodeRDE | INTEGER | False | 右下墙柱-端头节点编号 |  | 非墙柱端点为0 |
| NodeRDEInf | TEXT | False | 右下墙柱-终止端节点坐标 |  |  |
| WallColWebTotID | INTEGER | False | 腹板墙ID |  |  |
| ColSTotID | INTEGER | False | 上端柱ID |  |  |
| ColETotID | INTEGER | False | 下端柱ID |  |  |
| NodeBase | INTEGER | False | 定位点编号 |  |  |
| NodeUp | INTEGER | False | 上端头节点编号 |  |  |
| NodeUpInf | TEXT | False | 上端头节点坐标 |  |  |
| NodeDw | INTEGER | False | 下端头节点编号 |  |  |
| NodeDwInf | TEXT | False | 下端头节点坐标 |  |  |

dsnComWallZHEdgeInf
[图]

| dsnComWallZHEdgeInf |  |  |  |  |  |
|---|---|---|---|---|---|
| 组合墙边缘构件基本信息表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| FlrID | INTEGER | False | 层内ID |  |  |
| TotID | INTEGER | False | 全楼ID |  |  |
| Kind | INTEGER | False | 边缘构件类型，约束边缘构件或构造边缘构件 |  | 目前写该数据库时该处为Type结果 |
| Type | INTEGER | False | 边缘构件类型，一字形、L形、T形等 |  | 目前写该数据库时该处为Kind结果 |
| SeisLevel_Detail | INTEGER | False | 抗震构造措施对应的抗震等级 |  |  |
| ConGrade | REAL | False | 混凝土等级 |  |  |
| MainBar | INTEGER | False | 主筋类别 |  |  |
| HoopBar | INTEGER | False | 箍筋类别 |  |  |
| WallAssInf | TEXT | False | 指向的组合墙ID |  |  |
| ShadeArea | REAL | False | 边缘构件阴影区面积 |  |  |
| MainBarArea | REAL | False | 主筋配筋面积 |  |  |
| HoopRatio | REAL | False | 箍筋体积配箍率 |  |  |
| HoopDia | REAL | False | 箍筋直径，无体积配箍率时用 |  |  |
| HoopSpace | INTEGER | False | 箍筋间距，无体积配箍率时用 |  |  |
| EntStaCheck | INTEGER | False | 是否需要进行整体稳定验算 |  |  |
| SGTID | INTEGER | False | 施工图边缘构件编号 |  |  |

dsnComWallPJEdgeInf
[图]

| dsnComWallPJEdgeInf |  |  |  |  |  |
|---|---|---|---|---|---|
| 配筋边缘构件基本信息表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| FlrID | INTEGER | False | 层内ID |  |  |
| TotID | INTEGER | False | 全楼ID |  |  |
| Kind | INTEGER | False | 边缘构件类型，约束边缘构件或构造边缘构件 |  | 目前写该数据库时该处为Type结果 |
| Type | INTEGER | False | 边缘构件类型，一字形、L形、T形等 |  | 目前写该数据库时该处为Kind结果 |
| SeisLevel_Detail | INTEGER | False | 抗震构造措施对应的抗震等级 |  |  |
| ConGrade | REAL | False | 混凝土等级 |  |  |
| MainBar | INTEGER | False | 主筋类别 |  |  |
| HoopBar | INTEGER | False | 箍筋类别 |  |  |
| WallAssInf | TEXT | False | 指向的组合墙ID |  |  |
| ShadeArea | REAL | False | 边缘构件阴影区面积 |  |  |
| MainBarArea | REAL | False | 主筋配筋面积 |  |  |
| HoopRatio | REAL | False | 箍筋体积配箍率 |  |  |
| HoopDia | REAL | False | 箍筋直径，无体积配箍率时用 |  |  |
| HoopSpace | INTEGER | False | 箍筋间距，无体积配箍率时用 |  |  |
| EntStaCheck | INTEGER | False | 是否需要进行整体稳定验算 |  |  |
| SGTID | INTEGER | False | 施工图边缘构件编号 |  |  |

dsnComWallPJEdgeFlangeInf
[图]
[图]

| dsnComWallPJEdgeFlangeInf |  |  |  |  |  |
|---|---|---|---|---|---|
| 配筋边缘构件翼缘信息表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| PJEdgeID | INTEGER | False | 构件层内ID |  |  |
| dsnType | INTEGER | False | 设计类型 |  | 正截面设计 斜截面设计 |
| WallColLUTotID | INTEGER | False | 左上墙柱-ID |  |  |
| NodeLU | INTEGER | False | 左上墙柱-与腹板墙交点编号 |  |  |
| NodeLUE | INTEGER | False | 左上墙柱-端头节点编号 |  | 非墙柱端点为0 |
| NodeLUEInf | TEXT | False | 左上墙柱-终止端节点坐标 |  |  |
| WallColRUTotID | INTEGER | False | 右上墙柱-ID |  |  |
| NodeRU | INTEGER | False | 右上墙柱-与腹板墙交点编号 |  |  |
| NodeRUE | INTEGER | False | 右上墙柱-端头节点编号 |  | 非墙柱端点为0 |
| NodeRUEInf | TEXT | False | 右上墙柱-终止端节点坐标 |  |  |
| WallColLDTotID | INTEGER | False | 左下墙柱-ID |  |  |
| NodeLD | INTEGER | False | 左下墙柱-与腹板墙交点编号 |  |  |
| NodeLDE | INTEGER | False | 左下墙柱-端头节点编号 |  | 非墙柱端点为0 |
| NodeLDEInf | TEXT | False | 左下墙柱-终止端节点坐标 |  |  |
| WallColRDTotID | INTEGER | False | 右下墙柱-ID |  |  |
| NodeRD | INTEGER | False | 右下墙柱-与腹板墙交点编号 |  |  |
| NodeRDE | INTEGER | False | 右下墙柱-端头节点编号 |  | 非墙柱端点为0 |
| NodeRDEInf | TEXT | False | 右下墙柱-终止端节点坐标 |  |  |
| WallColWebTotID | INTEGER | False | 腹板墙ID |  |  |
| ColSTotID | INTEGER | False | 上端柱ID |  |  |
| ColETotID | INTEGER | False | 下端柱ID |  |  |
| NodeBase | INTEGER | False | 定位点编号 |  |  |
| NodeUp | INTEGER | False | 上端头节点编号 |  |  |
| NodeUpInf | TEXT | False | 上端头节点坐标 |  |  |
| NodeDw | INTEGER | False | 下端头节点编号 |  |  |
| NodeDwInf | TEXT | False | 下端头节点坐标 |  |  |

dsnComWallBody_Con
[图]

| dsnComWallBody_Con |  |  |  |  |  |
|---|---|---|---|---|---|
| 墙身设计结果表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件全楼ID |  |  |
| ComKind | INTEGER | False | 构件类型 |  | 22 墙身 |
| Sect | INTEGER | False | 截面数 |  | 2 |

dsnComWallPJEdge_Con
[图]

| dsnComWallPJEdge_Con |  |  |  |  |  |
|---|---|---|---|---|---|
| 配筋边缘构件设计结果表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件全楼ID |  |  |
| ComKind | INTEGER | False | 构件类型 |  | 9 边缘构件 |
| Sect | INTEGER | False | 截面数 |  | 2 |

设计结果
dsnComWallBodySect_Con
[图]
[图]

| dsnComWallBodySect_Con |  |  |  |  |  |
|---|---|---|---|---|---|
| 墙身截面设计结果表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| ComKind | INTEGER | False | 构件类型 | YJKDSN::ECom |  |
| Sect | INTEGER | False | 截面ID |  |  |
| AsS | REAL | False | 下端暗柱-配筋面积 |  |  |
| AsSCal | REAL | False | 下端暗柱-计算面积 |  |  |
| AsSRatio | REAL | False | 下端暗柱-全截面配筋率 |  |  |
| LDCombIDMS | INTEGER | False | 下端暗柱-控制组合号 |  |  |
| MSInf | TEXT | False | 下端暗柱-控制内力 |  |  |
| AsSTow | INTEGER | False | 下端暗柱-控制塔号 |  |  |
| AsE | REAL | False | 上端暗柱-配筋面积 |  |  |
| AsECal | REAL | False | 上端暗柱-计算面积 |  |  |
| AsERatio | REAL | False | 上端暗柱-全截面配筋率 |  |  |
| LDCombIDME | INTEGER | False | 上端暗柱-控制组合号 |  |  |
| MEInf | TEXT | False | 上端暗柱-控制内力 |  |  |
| AsETow | INTEGER | False | 上端暗柱-控制塔号 |  |  |
| MaxAsRatio | REAL | False | 暗柱-最大配筋率 |  |  |
| AsH | REAL | False | 水平分布筋-配筋面积 |  |  |
| AsHCal | REAL | False | 水平分布筋-计算面积 |  |  |
| MinAsHRatio | REAL | False | 水平分布筋-最小配筋率 |  |  |
| LDCombIDV | INTEGER | False | 水平分布筋-控制组合号 |  |  |
| VInf | TEXT | False | 水平分布筋-控制内力 |  |  |
| JKB | REAL | False | 水平分布筋-剪跨比 |  |  |
| CO | REAL | False | 水平分布筋-斜截面验算系数 |  |  |
| VCal | REAL | False | 斜截面-计算剪应力 |  |  |
| VMax | REAL | False | 斜截面-容许剪应力 |  |  |
| AsHTow | INTEGER | False | 水平分布筋-控制塔号 |  |  |
| AsHAdjSign | INTEGER | False | 水平分布筋-调整标志 |  | 0-未调整 1-根据楼层受剪承载力调整 |
| aaS | REAL | False | 下端暗柱长度 |  |  |
| aaE | REAL | False | 上端暗柱长度 |  |  |

dsnComWallPJEdgeSect_Con
[图]
[图]

| dsnComWallPJEdgeSect_Con |  |  |  |  |  |
|---|---|---|---|---|---|
| 配筋边缘构件截面设计结果表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| ComKind | INTEGER | False | 构件类型 | YJKDSN::ECom | 9 边缘构件 |
| Sect | INTEGER | False | 截面ID |  |  |
| AsX | REAL | False | X向纵筋配筋面积，包含两个角筋面积 |  |  |
| AsXCal | REAL | False | X向纵筋计算配筋面积，包含两个角筋面积 |  |  |
| LDCombIDMX | INTEGER | False | X向纵筋设计内力组合号 |  |  |
| MXInf | TEXT | False | X向纵筋设计内力，可能有多个 |  |  |
| AsXTow | INTEGER | False | X向纵筋分塔计算时对应的塔号 |  |  |
| AsXAdjSign | INTEGER | False | X向纵筋调整标志 |  | 0-未调整，1-根据楼层受剪承载力调整 |
| AsY | REAL | False | Y向纵筋配筋面积，包含两个角筋面积 |  |  |
| AsYCal | REAL | False | Y向纵筋计算配筋面积，包含两个角筋面积 |  |  |
| LDCombIDMY | INTEGER | False | Y向纵筋设计内力组合号 |  |  |
| MYInf | TEXT | False | Y向纵筋设计内力，可能有多个 |  |  |
| AsYTow | INTEGER | False | Y向纵筋分塔计算时对应的塔号 |  |  |
| AsYAdjSign | INTEGER | False | Y向纵筋调整标志 |  | 0-未调整，1-根据楼层受剪承载力调整 |
| MaxAsRatio | REAL | False | 纵筋全截面最大配筋率，从配筋库中获得 |  |  |
| MinAsRatio | REAL | False | 纵筋全截面最小配筋率，从配筋库中获得 |  |  |
| AsCorner | REAL | False | 角筋面积 |  |  |
| AsVX | REAL | False | X向箍筋配筋面积 |  |  |
| AsVXCal | REAL | False | X向箍筋计算配筋面积 |  |  |
| LDCombIDVX | INTEGER | False | X向箍筋设计内力组合号 |  |  |
| VXInf | TEXT | False | X向箍筋设计内力，可能有多个 |  |  |
| JKBX | REAL | False | X向箍筋计算用的剪跨比 |  |  |
| COX | REAL | False | X向箍筋斜截面验算系数 |  |  |
| VMaxX | REAL | False | X向箍筋斜截面最大承载力，用来判断是否超限 |  |  |
| AsVXTow | INTEGER | False | X向箍筋分塔计算时对应的塔号 |  |  |
| AsVXAdjSign | INTEGER | False | X向箍筋调整标志 |  | 0-未调整，1-根据楼层受剪承载力调整 |
| AsVY | REAL | False | Y向箍筋配筋面积 |  |  |
| AsVYCal | REAL | False | Y向箍筋计算配筋面积 |  |  |
| LDCombIDVY | INTEGER | False | Y向箍筋设计内力组合号 |  |  |
| VYInf | TEXT | False | Y向箍筋设计内力，可能有多个 |  |  |
| JKBY | REAL | False | Y向箍筋计算用的剪跨比 |  |  |
| COY | REAL | False | Y向箍筋斜截面验算系数 |  |  |
| VMaxY | REAL | False | Y向箍筋斜截面最大承载力，用来判断是否超限 |  |  |
| AsVYTow | INTEGER | False | Y向箍筋分塔计算时对应的塔号 |  |  |
| AsVYAdjSign | INTEGER | False | Y向箍筋调整标志 |  | 0-未调整，1-根据楼层受剪承载力调整 |
| MinAsVRatio | REAL | False | 箍筋最小体积配筋率，从配筋库中获得 |  |  |

地基梁
dsnComGradeBeamInf

| dsnComGradeBeamInf |  |  |  |  |  |
|---|---|---|---|---|---|
| 构件信息-地基梁 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| PMTotID | INTEGER | False | 建模构件ID |  |  |
| FlrID | INTEGER | False | 层内编号 |  |  |
| ComKind | INTEGER | False | 构件类型 |  |  |
| Kind | INTEGER | False | 梁属性 | YJKDSN::EBeamDSN | 普通梁 托墙转换梁 托柱转换梁 门式刚梁 消能梁 组合梁 吊车梁 |
| MatKind | INTEGER | False | 材料类型 | YJKDSN::EMat |  |
| PMMatKind | INTEGER | False | 材料类型-建模分类 |  | 5-钢 6-砼 |
| ConGrade | REAL | False | 砼标号 |  |  |
| ConGradeIn | REAL | False | 砼标号-内部 |  | 钢管砼叠合柱 |
| SteelKind | INTEGER | False | 钢号 |  |  |
| Cover | REAL | False | 保护层厚度 |  |  |
| TranHor | INTEGER | False | 是否为水平转换 |  |  |
| KZDJ | INTEGER | False | 抗震等级 |  |  |
| KZDJGZ | INTEGER | False | 抗震构造等级 |  |  |
| MainBar | INTEGER | False | 纵筋类型 |  |  |
| HoopBar | INTEGER | False | 箍筋类型 |  |  |
| Air | INTEGER | False | 是否按人防设计 |  |  |
| YZ | INTEGER | False | 是否是预制构件 |  |  |
| YYL | INTEGER | False | 是否是预应力构件 |  |  |
| WJType | INTEGER | False | 网架类别 | YJKDSN::EWJType | 网架、单层网壳、双层网壳等 |
| TrussSign | INTEGER | False | 桁架杆件标志 | YJKDSN::ETrussKind | 上弦、下弦、腹杆等 |
| XNSJM | INTEGER | False | 性能设计标志-正截面设计 |  | 弹性、不屈服 |
| XNSJV | INTEGER | False | 性能设计标志-斜截面设计 |  | 弹性、不屈服 |
| XNSJEmpSign | INTEGER | False | 构件重要性类别 |  | 1-耗能构件 2-普通构件 3-关键构件 |
| XNSJBLInf | TEXT | False | 性能设计包络标志 | dsnIModelAComProp_XNSJBL |  |
| Solid | INTEGER | False | 是否为实体元 |  |  |
| SeisVCom | INTEGER | False | 是否是指定竖向地震的构件 |  |  |
| NonLProp | INTEGER | False | 非线性数据 |  |  |
| HN | INTEGER | False | 是否是性能设计耗能构件 |  |  |
| BTRatioGrade | INTEGER | False | 宽厚比等级 |  |  |
| YXGrade | INTEGER | False | 延性等级 |  |  |
| BetaE | REAL | False | 性能系数的调整系数βe |  |  |
| RealXNXS | REAL | False | 实际性能系数 |  |  |
| TempInf | TEXT | False | 构件温度 |  | 依次记录 0-升温 1-降温 2-防火升温 |
| FHth | REAL | False | 耐火时间 |  |  |
| FHiqz | INTEGER | False | 膨胀型 |  | 1-非膨胀型 2-水泥砂浆 |
| FHri | REAL | False | 等效热阻/等效热传导系数 |  |  |
| FHdil | REAL | False | 保护层厚度 |  |  |
| FHfxz | REAL | False | 截面形状系数 |  |  |
| EnvSign | INTEGER | False | 是否包络设计 |  |  |
| DuctLevelEU | INTEGER | False | 延性等级-欧标 |  |  |
| DuctLevelUS | INTEGER | False | 延性等级-美标 |  |  |
| CurveCoe | REAL | False | 曲率系数 |  |  |
| StiffCoeInf | TEXT | False | 杆件的6个自由度对应的刚度系数 |  |  |
| PresInf | TEXT | False |  |  |  |
| TrussXID | INTEGER | False | X方向桁架编号 |  |  |
| TrussYID | INTEGER | False | Y方向桁架编号 |  |  |
| NodeS | INTEGER | False | 节点ID-起始端 |  |  |
| NodeE | INTEGER | False | 节点ID-终止端 |  |  |
| SupKindS | INTEGER | False | 支座类型-起始端 | YJKDSN::EBeamSup |  |
| SupKindE | INTEGER | False | 支座类型-终止端 | YJKDSN::EBeamSup |  |
| SteelT | REAL | False | 钢板厚度 |  |  |
| SteelH | REAL | False | 钢板高度 |  |  |
| StiffCoeM | REAL | False | 刚度放大系数或刚度折减系数 |  |  |
| XJKind | INTEGER | False | 特殊斜筋类型 | YJKDSN::EBeamXJ |  |
| LinkS | INTEGER | False | 支座约束类型 | YJKDSN::ESupLink | 刚接 铰接 滑动 半刚接 |
| LinkE | INTEGER | False | 支座约束类型 | YJKDSN::ESupLink |  |
| Ang | REAL | False | 梁布置角度（rad） |  |  |
| PortalJJLCoe | REAL | False | 门刚梁横向加劲肋间距与腹板最大高度的比值(a/Hw) |  | 0为不设加劲肋 |
| JGID | INTEGER | False |  |  |  |
| FreeSupMoment | TEXT | False | 简支梁内力 |  |  |
| PMSectNo | INTEGER | False | 建模截面索引 |  |  |
| Span | REAL | False | 平面内长度（m） |  |  |
| AmpSign | INTEGER | False | 调幅标志 |  |  |
| SpanOut | REAL | False | 平面外长度（m） |  |  |
| MainBeamID | INTEGER | False | 主梁ID |  |  |
| BeamSegID | INTEGER | False | 梁段ID |  |  |
| FrameSign | INTEGER | False | 梁属性 |  | 框架梁 非框架梁 连梁 |
| InputSign | INTEGER | False | 梁建模类别 |  | 普通梁 按次梁输入的次梁 空心板肋梁 地基梁 |

dsnComMainGradeBeamInf
[图]

| dsnComMainGradeBeamInf |  |  |  |  |  |
|---|---|---|---|---|---|
| 主地基梁基本信息表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| FlrID | INTEGER | False | 构件层内ID |  |  |
| ComInf | TEXT | False | 各梁段全楼ID |  |  |
| ComDirInf | TEXT | False | 各梁段方向是否与主梁方向一致 |  |  |

肋梁
dsnComRibBeamInf
[图]
[图]
[图]

| dsnComRibBeamInf |  |  |  |  |  |
|---|---|---|---|---|---|
| 肋梁基本信息表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| PMTotID | INTEGER | False | 建模构件ID |  |  |
| FlrID | INTEGER | False | 层内编号 |  |  |
| ComKind | INTEGER | False | 构件类型 |  |  |
| Kind | INTEGER | False | 梁属性 | YJKDSN::EBeamDSN | 普通梁 托墙转换梁 托柱转换梁 门式刚梁 消能梁 组合梁 吊车梁 |
| MatKind | INTEGER | False | 材料类型 | YJKDSN::EMat |  |
| PMMatKind | INTEGER | False | 材料类型-建模分类 |  | 5-钢 6-砼 |
| ConGrade | REAL | False | 砼标号 |  |  |
| ConGradeIn | REAL | False | 砼标号-内部 |  | 钢管砼叠合柱 |
| SteelKind | INTEGER | False | 钢号 |  |  |
| Cover | REAL | False | 保护层厚度 |  |  |
| TranHor | INTEGER | False | 是否为水平转换 |  |  |
| KZDJ | INTEGER | False | 抗震等级 |  |  |
| KZDJGZ | INTEGER | False | 抗震构造等级 |  |  |
| MainBar | INTEGER | False | 纵筋类型 |  |  |
| HoopBar | INTEGER | False | 箍筋类型 |  |  |
| Air | INTEGER | False | 是否按人防设计 |  |  |
| YZ | INTEGER | False | 是否是预制构件 |  |  |
| YYL | INTEGER | False | 是否是预应力构件 |  |  |
| WJType | INTEGER | False | 网架类别 | YJKDSN::EWJType | 网架、单层网壳、双层网壳等 |
| TrussSign | INTEGER | False | 桁架杆件标志 | YJKDSN::ETrussKind | 上弦、下弦、腹杆等 |
| XNSJM | INTEGER | False | 性能设计标志-正截面设计 |  | 弹性、不屈服 |
| XNSJV | INTEGER | False | 性能设计标志-斜截面设计 |  | 弹性、不屈服 |
| XNSJEmpSign | INTEGER | False | 构件重要性类别 |  | 1-耗能构件 2-普通构件 3-关键构件 |
| XNSJBLInf | TEXT | False | 性能设计包络标志 | dsnIModelAComProp_XNSJBL |  |
| Solid | INTEGER | False | 是否为实体元 |  |  |
| SeisVCom | INTEGER | False | 是否是指定竖向地震的构件 |  |  |
| NonLProp | INTEGER | False | 非线性数据 |  |  |
| HN | INTEGER | False | 是否是性能设计耗能构件 |  |  |
| BTRatioGrade | INTEGER | False | 宽厚比等级 |  |  |
| YXGrade | INTEGER | False | 延性等级 |  |  |
| BetaE | REAL | False | 性能系数的调整系数βe |  |  |
| RealXNXS | REAL | False | 实际性能系数 |  |  |
| TempInf | TEXT | False | 构件温度 |  | 依次记录 0-升温 1-降温 2-防火升温 |
| FHth | REAL | False | 耐火时间 |  |  |
| FHiqz | INTEGER | False | 膨胀型 |  | 1-非膨胀型 2-水泥砂浆 |
| FHri | REAL | False | 等效热阻/等效热传导系数 |  |  |
| FHdil | REAL | False | 保护层厚度 |  |  |
| FHfxz | REAL | False | 截面形状系数 |  |  |
| EnvSign | INTEGER | False | 是否包络设计 |  |  |
| DuctLevelEU | INTEGER | False | 延性等级-欧标 |  |  |
| DuctLevelUS | INTEGER | False | 延性等级-美标 |  |  |
| CurveCoe | REAL | False | 曲率系数 |  |  |
| StiffCoeInf | TEXT | False | 杆件的6个自由度对应的刚度系数 |  |  |
| PresInf | TEXT | False |  |  |  |
| TrussXID | INTEGER | False | X方向桁架编号 |  |  |
| TrussYID | INTEGER | False | Y方向桁架编号 |  |  |
| PMSectNo | INTEGER | False | 截面ID |  |  |
| Span | REAL | False | 梁平面内长度(m) |  |  |
| AmpSign | INTEGER | False | 调幅梁标志 |  |  |
| SpanOut | REAL | False | 梁平面外长度(m) |  |  |
| MainBeamID | INTEGER | False | 所属主梁ID |  |  |
| BeamSegID | INTEGER | False | 在梁段中的序号 |  |  |
| FrameSign | INTEGER | False | 梁属性 |  | 框架梁 非框架梁 连梁 |
| InputSign | INTEGER | False | 梁建模类别 |  | 普通梁 按次梁输入的次梁 空心板肋梁 地基梁 |

dsnComMainRibBeamInf
[图]

| dsnComMainRibBeamInf |  |  |  |  |  |
|---|---|---|---|---|---|
| 主肋梁基本信息表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| FlrID | INTEGER | False | 构件层内ID |  |  |
| ComInf | TEXT | False | 各梁段全楼ID |  |  |
| ComDirInf | TEXT | False | 各梁段方向是否与主梁方向一致 |  |  |

鉴定加固
dsnJGDef
[图]

| dsnJGDef |  |  |  |  |  |
|---|---|---|---|---|---|
| 加固做法定义表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | 加固做法编号 |  |  |
| PMTotID | INTEGER | False | 加固做法建模全楼编号 |  |  |
| Kind | INTEGER | False | 加固做法名称 |  |  |
| Name | TEXT | False | 加固做法类别，采用宏定义 |  |  |

dsnJGDefBeam_ZDJM
[图]

| dsnJGDefBeam_ZDJM |  |  |  |  |  |
|---|---|---|---|---|---|
| 梁增大截面法定义表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | 加固做法编号 |  |  |
| PMTotID | INTEGER | False | 加固做法建模全楼编号 |  |  |
| Name | TEXT | False | 加固做法名称 |  |  |
| AddB | REAL | False | B向增加总值(mm) |  |  |
| AddHU | REAL | False | H向上方增加值(mm) |  |  |
| AddHD | REAL | False | H向下方增加值(mm) |  |  |
| ConGrade | REAL | False | 新增的砼等级 |  |  |

dsnJGDefBeam_ZHHNT
[图]

| dsnJGDefBeam_ZHHNT |  |  |  |  |  |
|---|---|---|---|---|---|
| 梁置换混凝土法定义表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | 加固做法编号 |  |  |
| PMTotID | INTEGER | False | 加固做法建模全楼编号 |  |  |
| Name | TEXT | False | 加固做法名称 |  |  |
| ZHHU | REAL | False | H向上方置换值(mm) |  |  |
| ZHHD | REAL | False | H向下方置换值(mm) |  |  |
| ConGrade | REAL | False | 置换的砼等级 |  |  |

dsnJGDefBeam_WBXG
[图]

| dsnJGDefBeam_WBXG |  |  |  |  |  |
|---|---|---|---|---|---|
| 梁外包型钢法定义表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | 加固做法编号 |  |  |
| PMTotID | INTEGER | False | 加固做法建模全楼编号 |  |  |
| Name | TEXT | False | 加固做法名称 |  |  |
| SectUpID | INTEGER | False | 梁顶型钢定义编号 |  |  |
| SectDwID | INTEGER | False | 梁底型钢定义编号 |  |  |
| ZBB | REAL | False | 缀板宽度(mm) |  |  |
| ZBT | REAL | False | 缀板厚度(mm) |  |  |
| ZBSpace | REAL | False | 缀板间距(mm) |  |  |
| SteelKind | INTEGER | False | 钢号，采用宏定义 |  |  |

dsnJGDefBeam_WZGB
[图]

| dsnJGDefBeam_WZGB |  |  |  |  |  |
|---|---|---|---|---|---|
| 梁外粘钢板法定义表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | 加固做法编号 |  |  |
| PMTotID | INTEGER | False | 加固做法建模全楼编号 |  |  |
| Name | TEXT | False | 加固做法名称 |  |  |
| UpB | REAL | False | 梁顶钢板宽度(mm) |  |  |
| UpT | REAL | False | 梁顶钢板厚度(mm) |  |  |
| DwB | REAL | False | 梁底钢板宽度(mm) |  |  |
| DwT | REAL | False | 梁底钢板厚度(mm) |  |  |
| SideB | REAL | False | 梁侧箍板宽度(mm) |  |  |
| SideT | REAL | False | 梁侧箍板厚度(mm) |  |  |
| SideSpace | REAL | False | 梁侧箍板间距(mm) |  |  |
| SteelKind | INTEGER | False | 钢号，采用宏定义 |  |  |

dsnJGDefBeam_WTXWFHCL
[图]

| dsnJGDefBeam_WTXWFHCL |  |  |  |  |  |
|---|---|---|---|---|---|
| 梁外贴纤维复合材料法定义表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | 加固做法编号 |  |  |
| PMTotID | INTEGER | False | 加固做法建模全楼编号 |  |  |
| Name | TEXT | False | 加固做法名称 |  |  |
| PMFHCLKind | INTEGER | False | 建模复合材料类型，采用建模定义 |  | 0-碳纤维单向织物高强度I级 1-碳纤维单向织物高强度II级 2-碳纤维单向织物高强度III级 3-碳纤维条形板高强度I级 4-碳纤维条形板高强度II级 5-芳纶纤维单向织物高强度I级 6-芳纶纤维单向织物高强度II级 7-芳纶纤维条形板高强度I级 8-芳纶纤维条形板高强度II级 9-高强度玻璃纤维S 10-无碱玻璃纤维E |
| ImpSign | INTEGER | False | 重要性 |  | 1：一般构件 0：重要构件 |
| UpLayerNum | INTEGER | False | 梁顶复合材料层数 |  |  |
| UpB | REAL | False | 梁顶复合材料宽度(mm) |  |  |
| DwLayerNum | INTEGER | False | 梁底复合材料层数 |  |  |
| DwB | REAL | False | 梁底复合材料宽度(mm) |  |  |
| SideLayerNum | INTEGER | False | 梁侧复合材料层数 |  |  |
| SideB | REAL | False | 梁侧复合材料宽度(mm) |  |  |
| SideSpace | REAL | False | 梁侧复合材料间距(mm) |  |  |
| LayerT | REAL | False | 复合材料单层厚度(mm) |  |  |

dsnJGDefBeam_GJXW
[图]

| dsnJGDefBeam_GJXW |  |  |  |  |  |
|---|---|---|---|---|---|
| 梁钢绞线网-聚合物砂浆面层加固法定义表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | 加固做法编号 |  |  |
| PMTotID | INTEGER | False | 加固做法建模全楼编号 |  |  |
| Name | TEXT | False | 加固做法名称 |  |  |
| Dia | REAL | False | 钢绞线直径(mm) |  |  |
| LayerNum | INTEGER | False | 钢绞线层数 |  |  |
| SideH | REAL | False | 梁侧面围套高度(mm) |  |  |
| MBarSpace | REAL | False | 钢丝绳纵筋间距(mm) |  |  |
| HBarSpace | REAL | False | 钢丝绳箍筋间距(mm) |  |  |
| Hr | REAL | False | 侧面维套高度(mm) |  |  |

dsnJGDefBeam_ZDJM_WZGB
[图]

| dsnJGDefBeam_ZDJM_WZGB |  |  |  |  |  |
|---|---|---|---|---|---|
| 梁底部增大截面+顶部钢板加固法定义表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | 加固做法编号 |  |  |
| PMTotID | INTEGER | False | 加固做法建模全楼编号 |  |  |
| Name | TEXT | False | 加固做法名称 |  |  |
| AddB | REAL | False | B向增加总值(mm) |  |  |
| AddHD | REAL | False | H向下方增加值(mm) |  |  |
| ConGrade | REAL | False | 新增的砼等级 |  |  |
| UpB | REAL | False | 梁顶钢板宽度(mm) |  |  |
| UpT | REAL | False | 梁顶钢板厚度(mm) |  |  |
| SteelKind | INTEGER | False | 钢号，采用宏定义 |  |  |

dsnJGDefCol_ZDJM
[图]

| dsnJGDefCol_ZDJM |  |  |  |  |  |
|---|---|---|---|---|---|
| 柱增大截面法定义表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | 加固做法编号 |  |  |
| PMTotID | INTEGER | False | 加固做法建模全楼编号 |  |  |
| Name | TEXT | False | 加固做法名称 |  |  |
| AddBL | REAL | False | B向左侧增加值(mm)，水平方向 |  |  |
| AddBR | REAL | False | B向右侧增加值(mm)，水平方向 |  |  |
| AddHU | REAL | False | H向顶部增加总值(mm)，垂直方向 |  |  |
| AddHD | REAL | False | H向底部增加总值(mm)，垂直方向 |  |  |
| ConGrade | REAL | False | 新增的砼等级 |  |  |

dsnJGDefCol_ZHHNT
[图]

| dsnJGDefCol_ZHHNT |  |  |  |  |  |
|---|---|---|---|---|---|
| 柱置换混凝土法定义表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | 加固做法编号 |  |  |
| PMTotID | INTEGER | False | 加固做法建模全楼编号 |  |  |
| Name | TEXT | False | 加固做法名称 |  |  |
| ZHB | REAL | False | B向单侧置换深度(mm)，水平方向 |  |  |
| ZHH | REAL | False | H向单侧置换深度(mm)，垂直方向 |  |  |
| ConGrade | REAL | False | 置换的砼等级 |  |  |

dsnJGDefCol_WBXG
[图]

| dsnJGDefCol_WBXG |  |  |  |  |  |
|---|---|---|---|---|---|
| 柱外包型钢法定义表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | 加固做法编号 |  |  |
| PMTotID | INTEGER | False | 加固做法建模全楼编号 |  |  |
| Name | TEXT | False | 加固做法名称 |  |  |
| SectID | INTEGER | False | 型钢截面定义编号 |  | 目前主要有槽钢和角钢 |
| ZBB | REAL | False | 缀板宽度(mm) |  |  |
| ZBT | REAL | False | 缀板厚度(mm) |  |  |
| ZBSpace | REAL | False | 缀板间距(mm) |  |  |
| SteelKind | INTEGER | False | 钢号，采用宏定义 |  |  |

dsnJGDefCol_WZGB
[图]

| dsnJGDefCol_WZGB |  |  |  |  |  |
|---|---|---|---|---|---|
| 柱外粘钢板法定义表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | 加固做法编号 |  |  |
| PMTotID | INTEGER | False | 加固做法建模全楼编号 |  |  |
| Name | TEXT | False | 加固做法名称 |  |  |
| B | REAL | False | B边单侧钢板宽度(mm) |  |  |
| H | REAL | False | H边单侧钢板宽度(mm) |  |  |
| T | REAL | False | 钢板厚度(mm) |  |  |
| SteelKind | INTEGER | False | 钢号，采用宏定义 |  |  |

dsnJGDefCol_WTXWFHCL
[图]

| dsnJGDefCol_WTXWFHCL |  |  |  |  |  |
|---|---|---|---|---|---|
| 柱外贴纤维复合材料法定义表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | 加固做法编号 |  |  |
| PMTotID | INTEGER | False | 加固做法建模全楼编号 |  |  |
| Name | TEXT | False | 加固做法名称 |  |  |
| PMFHCLKind | INTEGER | False | 建模复合材料类型，采用建模定义 |  | 0-碳纤维单向织物高强度I级 1-碳纤维单向织物高强度II级 2-碳纤维单向织物高强度III级 3-碳纤维条形板高强度I级 4-碳纤维条形板高强度II级 5-芳纶纤维单向织物高强度I级 6-芳纶纤维单向织物高强度II级 7-芳纶纤维条形板高强度I级 8-芳纶纤维条形板高强度II级 9-高强度玻璃纤维S 10-无碱玻璃纤维E |
| ImpSign | INTEGER | False | 重要性 |  | 1：一般构件 0：重要构件 |
| B | REAL | False | B边宽度(mm) |  |  |
| H | REAL | False | H边宽度(mm) |  |  |
| CircleB | REAL | False | 环形箍宽度(mm) |  |  |
| CircleSpace | REAL | False | 环形箍间距(mm) |  |  |
| LayerNum | INTEGER | False | 复合材料层数 |  |  |
| LayerT | REAL | False | 复合材料单层厚度(mm) |  |  |

dsnJGBeam
[图]

| dsnJGBeam |  |  |  |  |  |
|---|---|---|---|---|---|
| 梁加固信息表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| ComKind | INTEGER | False | 构件类型 |  |  |
| SeisDamageCoe | REAL | False | 震损系数 |  |  |
| NewComSign | INTEGER | False | 新增构件标志 |  |  |
| JGDefID | INTEGER | False | 加固做法编号 |  |  |

dsnJGBeamBar
[图]

| dsnJGBeamBar |  |  |  |  |  |
|---|---|---|---|---|---|
| 梁实配钢筋信息表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| ComKind | INTEGER | False | 构件类型 |  |  |
| Sect | INTEGER | False | 截面编号 |  | 从1开始 |
| MBarUpNum | TEXT | False | 上部钢筋根数 |  |  |
| MBarUpGrade | TEXT | False | 上部钢筋级别 |  | 采用计算参数宏定义 |
| MBarUpDia | TEXT | False | 上部钢筋直径(mm) |  |  |
| MBarDwNum | TEXT | False | 下部钢筋根数 |  |  |
| MBarDwGrade | TEXT | False | 下部钢筋级别 |  |  |
| MBarDwDia | TEXT | False | 下部钢筋直径(mm) |  |  |
| HBarNum | INTEGER | False | 箍筋肢数 |  |  |
| HBarGrade | INTEGER | False | 箍筋级别 |  |  |
| HBarDia | REAL | False | 箍筋直径(mm) |  |  |
| HBarSpace | REAL | False | 箍筋间距 |  |  |
| HBarJM | INTEGER | False | 箍筋是否是加密区标记 |  |  |

dsnJGCol
[图]

| dsnJGCol |  |  |  |  |  |
|---|---|---|---|---|---|
| 柱加固信息表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| ComKind | INTEGER | False | 构件类型 |  |  |
| SeisDamageCoe | REAL | False | 震损系数 |  |  |
| NewComSign | INTEGER | False | 新增构件标志 |  |  |
| JGDefID | INTEGER | False | 加固做法编号 |  |  |

dsnJGColBar
[图]

| dsnJGColBar |  |  |  |  |  |
|---|---|---|---|---|---|
| 柱实配钢筋信息表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| ComKind | INTEGER | False | 构件类型 |  |  |
| Sect | INTEGER | False | 截面编号 |  | 从1开始 |
| BarCornerDia | REAL | False | 柱脚筋直径（mm） |  | 目前写数据库时该数据遗漏 |
| MBarBNum | TEXT | False | 柱B边纵筋（异形柱为固定钢筋）根数 |  |  |
| MBarBGrade | TEXT | False | 柱B边纵筋（异形柱为固定钢筋）级别 |  |  |
| MBarBDia | TEXT | False | 柱B边纵筋（异形柱为固定钢筋）直径（mm） |  |  |
| MBarHNum | TEXT | False | 柱H边纵筋（异形柱为分布钢筋）根数 |  |  |
| MBarHGrade | TEXT | False | 柱H边纵筋（异形柱为分布钢筋）级别 |  |  |
| MBarHDia | TEXT | False | 柱H边纵筋（异形柱为分布钢筋）直径（mm） |  |  |
| HBarJMXNum | INTEGER | False | 柱X向加密区箍筋根数 |  |  |
| HBarJMXGrade | INTEGER | False | 柱X向加密区箍筋级别 |  |  |
| HBarJMXDia | REAL | False | 柱X向加密区箍筋直径（mm） |  |  |
| HBarJMXSpace | REAL | False | 柱X向加密区箍筋间距 |  |  |
| HBarJMYNum | INTEGER | False | 柱Y向加密区箍筋根数 |  |  |
| HBarJMYGrade | INTEGER | False | 柱Y向加密区箍筋级别 |  |  |
| HBarJMYDia | REAL | False | 柱Y向加密区箍筋直径（mm） |  |  |
| HBarJMYSpace | REAL | False | 柱Y向加密区箍筋间距间距 |  |  |
| HBarXNum | INTEGER | False | 柱X向非加密区箍筋根数 |  |  |
| HBarXGrade | INTEGER | False | 柱X向非加密区箍筋级别 |  |  |
| HBarXDia | REAL | False | 柱X向非加密区箍筋直径（mm） |  |  |
| HBarXSpace | REAL | False | 柱X向非加密区箍筋间距 |  |  |
| HBarYNum | INTEGER | False | 柱Y向非加密区箍筋根数 |  |  |
| HBarYGrade | INTEGER | False | 柱Y向非加密区箍筋级别 |  |  |
| HBarYDia | REAL | False | 柱Y向非加密区箍筋直径（mm） |  |  |
| HBarYSpace | REAL | False | 柱Y向非加密区箍筋间距 |  |  |

dsnJGBeamSect_ZDJM

| dsnJGBeamSect_ZDJM |  |  |  |  |  |
|---|---|---|---|---|---|
| 梁增大截面法截面计算结果表（暂时缺失） |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
|  |  |  |  |  |  |
|  |  |  |  |  |  |

dsnJGBeamSect_ZHHNT
[图]

| dsnJGBeamSect_ZHHNT |  |  |  |  |  |
|---|---|---|---|---|---|
| 梁置换混凝土法截面计算结果表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| ComKind | INTEGER | False | 构件类型 |  |  |
| Sect | INTEGER | False | 截面编号 |  | 从1开始 |
| ZHHUCal | REAL | False | H向上方计算置换值(mm) |  |  |
| ZHHDCal | REAL | False | H向下方计算置换值(mm) |  |  |

dsnJGBeamSect_WBXG
[图]

| dsnJGBeamSect_WBXG |  |  |  |  |  |
|---|---|---|---|---|---|
| 梁外包型钢法截面计算结果表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| ComKind | INTEGER | False | 构件类型 |  |  |
| Sect | INTEGER | False | 截面编号 |  | 从1开始 |
| StlAreaUpCal | REAL | False | 梁顶计算型钢面积(mm2) |  |  |
| StlAreaUpMin | REAL | False | 梁顶最小型钢面积(mm2) |  |  |
| StlAreaDwCal | REAL | False | 梁底计算型钢面积(mm2) |  |  |
| StlAreaDwMin | REAL | False | 梁底最小型钢面积(mm2) |  |  |
| StlAreaSideCal | REAL | False | 梁侧全部计算型钢面积(mm2) |  |  |
| StlAreaSideMin | REAL | False | 梁侧全部最小型钢面积(mm2) |  |  |

dsnJGBeamSect_WZGB
[图]

| dsnJGBeamSect_WZGB |  |  |  |  |  |
|---|---|---|---|---|---|
| 梁外粘钢板法截面计算结果表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| ComKind | INTEGER | False | 构件类型 |  |  |
| Sect | INTEGER | False | 截面编号 |  | 从1开始 |
| StlAreaUpCal | REAL | False | 梁顶计算型钢面积(mm2) |  |  |
| StlAreaUpMin | REAL | False | 梁顶最小型钢面积(mm2) |  |  |
| StlAreaDwCal | REAL | False | 梁底计算型钢面积(mm2) |  |  |
| StlAreaDwMin | REAL | False | 梁底最小型钢面积(mm2) |  |  |
| StlAreaSideCal | REAL | False | 梁侧全部计算型钢面积(mm2) |  |  |
| StlAreaSideMin | REAL | False | 梁侧全部最小型钢面积(mm2) |  |  |

dsnJGBeamSect_WTXWFHCL
[图]

| dsnJGBeamSect_WTXWFHCL |  |  |  |  |  |
|---|---|---|---|---|---|
| 梁外贴纤维复合材料法截面计算结果表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| ComKind | INTEGER | False | 构件类型 |  |  |
| Sect | INTEGER | False | 截面编号 |  | 从1开始 |
| XWAreaUpCal | REAL | False | 梁顶计算纤维面积(mm2) |  |  |
| XWAreaUpMin | REAL | False | 梁顶最小纤维面积(mm2) |  |  |
| XWAreaDwCal | REAL | False | 梁底计算纤维面积(mm2) |  |  |
| XWAreaDwMin | REAL | False | 梁底最小纤维面积(mm2) |  |  |
| XWAreaSideCal | REAL | False | 梁侧全部计算纤维面积(mm2) |  |  |
| XWAreaSideMin | REAL | False | 梁侧全部最小纤维面积(mm2) |  |  |

dsnJGBeamSect_GJXW
[图]

| dsnJGBeamSect_GJXW |  |  |  |  |  |
|---|---|---|---|---|---|
| 梁钢绞线网-聚合物砂浆面层加固法截面计算结果表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| ComKind | INTEGER | False | 构件类型 |  |  |
| Sect | INTEGER | False | 截面编号 |  | 从1开始 |
| GJXAreaUpCal | REAL | False | 梁顶计算钢绞线面积(mm2) |  |  |
| GJXAreaUpMin | REAL | False | 梁顶最小钢绞线面积(mm2) |  |  |
| GJXAreaDwCal | REAL | False | 梁底计算钢绞线面积(mm2) |  |  |
| GJXAreaDwMin | REAL | False | 梁底最小钢绞线面积(mm2) |  |  |
| GJXAreaSideCal | REAL | False | 梁侧全部计算钢绞线面积(mm2) |  |  |
| GJXAreaSideMin | REAL | False | 梁侧全部最小钢绞线面积(mm2) |  |  |

dsnJGBeamSect_ZDJM_WZGB
[图]

| dsnJGBeamSect_ZDJM_WZGB |  |  |  |  |  |
|---|---|---|---|---|---|
| 梁底部增大截面+顶部钢板加固法截面计算结果表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| ComKind | INTEGER | False | 构件类型 |  |  |
| Sect | INTEGER | False | 截面编号 |  | 从1开始 |
| StlAreaUpCal | REAL | False | 梁顶计算型钢面积(mm2) |  |  |
| StlAreaUpMin | REAL | False | 梁顶最小型钢面积(mm2) |  |  |

dsnJGColSect_ZDJM
[图]

| dsnJGColSect_ZDJM |  |  |  |  |  |
|---|---|---|---|---|---|
| 柱增大截面法截面计算结果表（暂时缺失） |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
|  |  |  |  |  |  |
|  |  |  |  |  |  |

dsnJGColSect_ZHHNT
[图]

| dsnJGColSect_ZHHNT |  |  |  |  |  |
|---|---|---|---|---|---|
| 柱置换混凝土法截面计算结果表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| ComKind | INTEGER | False | 构件类型 |  |  |
| Sect | INTEGER | False | 截面编号 |  | 从1开始 |
| ZHBCal | REAL | False | 计算需要的B向单侧置换深度(mm)，水平方向 |  |  |
| ZHHCal | REAL | False | 计算需要的H向单侧置换深度(mm)，垂直方向 |  |  |

dsnJGColSect_WBXG
[图]

| dsnJGColSect_WBXG |  |  |  |  |  |
|---|---|---|---|---|---|
| 柱外包型钢法截面计算结果表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| ComKind | INTEGER | False | 构件类型 |  |  |
| Sect | INTEGER | False | 截面编号 |  | 从1开始 |
| StlAreaBCal | REAL | False | B边计算需要的单侧型钢面积 |  |  |
| StlAreaBMin | REAL | False | B边单侧型钢最小面积 |  |  |
| StlAreaHCal | REAL | False | H边计算需要的单侧型钢面积 |  |  |
| StlAreaHMin | REAL | False | H边单侧型钢最小面积 |  |  |

dsnJGColSect_WZGB
[图]

| dsnJGColSect_WZGB |  |  |  |  |  |
|---|---|---|---|---|---|
| 柱外粘钢板法截面计算结果表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| ComKind | INTEGER | False | 构件类型 |  |  |
| Sect | INTEGER | False | 截面编号 |  | 从1开始 |
| StlAreaBCal | REAL | False | B边计算需要的单侧型钢面积 |  |  |
| StlAreaBMin | REAL | False | B边单侧型钢最小面积 |  |  |
| StlAreaHCal | REAL | False | H边计算需要的单侧型钢面积 |  |  |
| StlAreaHMin | REAL | False | H边单侧型钢最小面积 |  |  |

dsnJGColSect_WTXWFHCL
[图]

| dsnJGColSect_WTXWFHCL |  |  |  |  |  |
|---|---|---|---|---|---|
| 柱外贴纤维复合材料法截面计算结果表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| TowNo | INTEGER | False | 塔号 |  |  |
| TotID | INTEGER | False | 构件ID |  |  |
| ComKind | INTEGER | False | 构件类型 |  |  |
| Sect | INTEGER | False | 截面编号 |  | 从1开始 |
| XWAreaBCal | REAL | False | B边计算需要的单侧纤维面积 |  |  |
| XWAreaBMin | REAL | False | B边单侧纤维最小面积 |  |  |
| XWAreaHCal | REAL | False | H边计算需要的单侧纤维面积 |  |  |
| XWAreaHMin | REAL | False | H边单侧纤维最小面积 |  |  |
| XWAreaSideCal | REAL | False | 抗剪计算需要的单位间距纤维面积 |  |  |
| XWAreaSideMin | REAL | False | 抗剪单位间距纤维最小面积 |  |  |

关联关系
dsnRelPMNodeToCom
[图]

| dsnRelPMNodeToCom |  |  |  |  |  |
|---|---|---|---|---|---|
| 建模节点编号关联的构件编号表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| PMNodeID | INTEGER | False | 建模节点ID |  |  |
| BeamTotIDInf | TEXT | False | 关联的梁ID |  |  |
| ColTotIDInf | TEXT | False | 关联的柱ID |  |  |

dsnRelNodeToCom
[图]

| dsnRelNodeToCom |  |  |  |  |  |
|---|---|---|---|---|---|
| 计算节点编号关联的构件编号表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| NodeID | INTEGER | False | 计算节点ID |  |  |
| BeamTotIDInf | TEXT | False | 计算节点编号到计算梁全楼编号 |  |  |
| ColTotIDInf | TEXT | False | 计算节点编号到计算柱全楼编号 |  |  |
| BraceTotIDInf | TEXT | False | 计算节点编号到计算斜杆全楼编号 |  |  |
| WallBeamTotIDInf | TEXT | False | 计算节点编号到计算墙梁全楼编号 |  |  |
| WallColTotIDInf | TEXT | False | 计算节点编号到计算墙柱全楼编号 |  |  |

dsnRelComToCom
[图]

| dsnRelComToCom |  |  |  |  |  |
|---|---|---|---|---|---|
| 构件到构件索引表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ComKind | INTEGER | False | 构件类型 |  |  |
| ComTotID | INTEGER | False | 构件ID |  |  |
| UpColTotIDInf | TEXT | False | 柱编号到上柱全楼编号 |  |  |
| DwColTotIDInf | TEXT | False | 柱编号到下柱全楼编号 |  |  |
| UpBraceTotIDInf | TEXT | False | 柱编号到上支撑全楼编号 |  |  |
| DwBraceTotIDInf | TEXT | False | 柱编号到下支撑全楼编号 |  |  |
| UpWallColTotIDInf | TEXT | False | 墙柱编号到上墙柱全楼编号 |  |  |
| DwWallColTotIDInf | TEXT | False | 墙柱编号到下墙柱全楼编号 |  |  |

施工图DTL系列
砼梁
通用参数
dtlConBeam_Para
[图]

| dtlConBeam_Para |  |  |  |  |  |
|---|---|---|---|---|---|
| 梁施工图-数据库信息 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | 枚举值 |  |  |
| ParaVal |  | False | 数值 |  |  |

dtlConBeam_Flr
[图]

| dtlConBeam_Flr |  |  |  |  |  |
|---|---|---|---|---|---|
| 梁施工图-自然层 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | ID |  |  |
| StdFlrID | INTEGER | False | 标准层ID | pmStdFlr的ID |  |
| ReinFlrID | INTEGER | False | 钢筋层ID | dtlConBeam_RcFlr的ID |  |
| Name | TEXT | False | 名称 |  |  |
| LevelB | REAL | False | 底标高 |  |  |
| Height | REAL | False | 层号 |  |  |

dtlConBeam_RcFlr
[图]

| dtlConBeam_RcFlr |  |  |  |  |  |
|---|---|---|---|---|---|
| 梁施工图-钢筋层 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | ID |  |  |
| Name | TEXT | False | 名称 |  |  |
| FloorID | INTEGER | False | 自然层ID | dtlConBeam_Flr的ID |  |

几何信息
dtlConBeam_CntBeam
[图]

| dtlConBeam_CntBeam |  |  |  |  |  |
|---|---|---|---|---|---|
| 梁施工图-连续梁 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | ID |  |  |
| FloorID | INTEGER | False | 层号 |  |  |
| Attrib | INTEGER | False | 连续梁属性 |  | 低8位描述类型 |
| SpanNum | INTEGER | False | 跨数 |  |  |
| RcCBID | INTEGER | False | 配筋连续梁ID | dtlConBeam_RcCntBeam的ID |  |
| MirroredFlag | INTEGER | False |  |  |  |

dtlConBeam_SpanRel
[图]

| dtlConBeam_SpanRel |  |  |  |  |  |
|---|---|---|---|---|---|
| 梁施工图-梁跨信息 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| CBID | INTEGER | False | 连续梁ID | dtlConBeam_CntBeam的ID |  |
| SpanNo | INTEGER | False | 梁跨序号 |  | 从0开始 |
| GridNoS | INTEGER | False | 梁跨包含的梁段起始序号 | dtlConBeam_SegInfo的NoInCB | 从0开始 |
| GridNoE | INTEGER | False | 梁跨包含的梁段终止序号 | dtlConBeam_SegInfo的NoInCB | 从0开始 |

dtlConBeam_SegInfo
[图]

| dtlConBeam_SegInfo |  |  |  |  |  |
|---|---|---|---|---|---|
| 梁施工图-梁段信息 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FloorID | INTEGER | False | 自然层ID | dtlConBeam_Flr的ID |  |
| SegID | INTEGER | False | 梁段ID |  |  |
| CntBeamID | INTEGER | False | 连续梁ID |  |  |
| NoInCB | INTEGER | False | 梁段在连续梁内的序号 |  | 从0开始 |
| PosInCB | INTEGER | False | 在连续梁中对应的梁跨或支座号 |  |  |
| InfoGrid | INTEGER | False | 梁段或网格的一些属性 |  | 位运算 |
| InfoJt1 | INTEGER | False | 起节点处的一些属性 |  | 位运算 |
| InfoJt2 | INTEGER | False | 终节点处的一些属性 |  | 位运算 |

dtlConBeam_SpanPara
[图]

| dtlConBeam_SpanPara |  |  |  |  |  |
|---|---|---|---|---|---|
| 梁施工图-梁段参数 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| SpanID | INTEGER | False | 梁跨ID |  |  |
| Kind | INTEGER | False | 参数枚举 |  |  |
| ParaVal | INTEGER | False | 参数值 |  |  |

dtlConBeam_WallBeam
[图]

| dtlConBeam_WallBeam |  |  |  |  |  |
|---|---|---|---|---|---|
| 梁施工图-连梁 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | ID |  |  |
| FloorID | INTEGER | False | 层号 |  |  |
| B | REAL | False | 梁宽 |  |  |
| H | REAL | False | 梁高 |  |  |
| HDiff | REAL | False | 标高调整值 |  |  |
| Len | REAL | False | 跨度 |  |  |
| X1 | REAL | False | I端坐标 |  |  |
| Y1 | REAL | False | I端坐标 |  |  |
| X2 | REAL | False | J端坐标 |  |  |
| Y2 | REAL | False | J端坐标 |  |  |
| RcBeamID | INTEGER | False | 配筋连续梁ID |  |  |
| XC | REAL | False |  |  |  |
| YC | REAL | False |  |  |  |

配筋信息
dtlConBeam_RcCntBeam
[图]

| dtlConBeam_RcCntBeam |  |  |  |  |  |
|---|---|---|---|---|---|
| 梁施工图-连续梁配筋信息 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | ID |  |  |
| ReinFlrID | INTEGER | False | 钢筋层ID | dtlConBeam_RcFlr的ID |  |
| Name | TEXT | False | 连续梁名称 |  |  |
| SpanNum | INTEGER | False | 跨数 |  |  |

dtlConBeam_RcSpan
[图]

| dtlConBeam_RcSpan |  |  |  |  |  |
|---|---|---|---|---|---|
| 梁施工图-梁跨配筋信息 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | ID |  |  |
| RcCBID | INTEGER | False | 配筋连续梁ID | dtlConBeam_RcCntBeam的ID |  |
| SpanNo | INTEGER | False | 配筋梁跨序号 |  | 从0开始 |

dtlConBeam_RcSpanRein
[图]

| dtlConBeam_RcSpanRein |  |  |  |  |  |
|---|---|---|---|---|---|
| 梁施工图-配筋梁跨钢筋 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| SpanID | INTEGER | False | 配筋梁跨ID | dtlConBeam_RcSpan的ID |  |
| Kind | INTEGER | False | 钢筋枚举 |  |  |
| ReinVal | TEXT | False | 配筋值 |  |  |

dtlConBeam_RcSBRein
[图]

| dtlConBeam_RcSBRein |  |  |  |  |  |
|---|---|---|---|---|---|
| 梁施工图-附加钢筋信息 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | ID |  |  |
| CntBeamID | INTEGER | False | 配筋连续梁ID | dtlConBeam_RcCntBeam的ID |  |
| JointNo | INTEGER | False | 在连续梁的第几个节点上 |  |  |
| Dist | REAL | False | 加筋中点到定位节点的距离 |  | 沿网格线度量 沿连续梁方向为正 |
| AddHoop | INTEGER | False | 次梁梁侧附加箍筋的总套数 |  |  |
| Hanger | TEXT | False | 附加吊筋文字 |  |  |

dtlConBeam_RcReinLen
[图]

| dtlConBeam_RcReinLen |  |  |  |  |  |
|---|---|---|---|---|---|
| 梁施工图-钢筋长度 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | ID |  |  |
| SpanID | INTEGER | False | 配筋梁跨ID |  |  |
| Kind | INTEGER | False |  |  |  |
| ExprIndex | INTEGER | False |  |  |  |
| ExprString | TEXT | False |  |  |  |
| LenValue | REAL | False |  |  |  |

dtlConBeam_RcWallBeam
[图]

| dtlConBeam_RcWallBeam |  |  |  |  |  |
|---|---|---|---|---|---|
| 梁施工图-配筋连梁信息 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | ID |  |  |
| ReinFlrID | INTEGER | False | 钢筋层ID | dtlConBeam_RcFlr的ID |  |
| Name | TEXT | False | 连梁名称 |  |  |
| TopBar | TEXT | False | 上铁 |  |  |
| BottomBar | TEXT | False | 下铁 |  |  |
| HoopBar | TEXT | False | 箍筋 |  |  |
| YaoBar | TEXT | False | 腰筋 |  |  |
| YaoLaBar | TEXT | False | 拉筋 |  |  |
| CrossBar | TEXT | False | 特殊抗剪斜筋-纵筋 |  |  |
| CrossLaBar | TEXT | False | 特殊抗剪斜筋-箍筋 |  |  |
| CrossBarType | INTEGER | False | 特殊抗剪斜筋类型 |  |  |

砼柱
通用信息
dtlConCol_Para
[图]

| dtlConCol_Para |  |  |  |  |  |
|---|---|---|---|---|---|
| 柱施工图-数据库信息 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | 枚举值 |  |  |
| ParaVal |  | False | 数值 |  |  |

dtlConCol_Flr
[图]

| dtlConCol_Flr |  |  |  |  |  |
|---|---|---|---|---|---|
| 柱施工图-自然层 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | ID |  |  |
| StdFlrID | INTEGER | False | 标准层ID | pmStdFlr的ID |  |
| ReinFlrID | INTEGER | False | 钢筋层ID | dtlConBeam_RcFlr的ID |  |
| No_ | INTEGER | False | 序号 |  |  |
| Name | TEXT | False | 名称 |  |  |
| LevelB | REAL | False | 底标高 |  |  |
| Height | REAL | False | 层号 |  |  |

dtlConCol_RcFlr
[图]

| dtlConCol_RcFlr |  |  |  |  |  |
|---|---|---|---|---|---|
| 柱施工图-钢筋层 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | ID |  |  |
| Name | TEXT | False | 名称 |  |  |

几何信息
dtlConCol_CntCol
[图]

| dtlConCol_CntCol |  |  |  |  |  |
|---|---|---|---|---|---|
| 柱施工图-连续柱 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | ID |  |  |
| FloorID | INTEGER | False | 自然层ID | dtlConCol_Flr的ID |  |
| Type | INTEGER | False | 柱类型 |  | 位运算 |
| SpanNum | INTEGER | False | 柱跨数量 |  |  |
| RcCntColID | INTEGER | False | 配筋连续柱ID |  |  |
| JointID | INTEGER | False | 柱底节点ID | pmNode的ID |  |

dtlConCol_Span
[图]

| dtlConCol_Span |  |  |  |  |  |
|---|---|---|---|---|---|
| 柱施工图-柱跨 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | ID |  |  |
| CntColID | INTEGER | False | 连续柱ID | dtlConCol_CntCol的ID |  |
| LevelB | REAL | False | 柱跨底标高 |  |  |
| LevelT | REAL | False | 柱跨顶标高 |  |  |
| LevelBeamB | REAL | False | 柱跨相连梁高度 |  | 柱跨顶标高-梁最底标高 |
| IndexSegStart | INTEGER | False | 柱段在连续柱内的序号起点 |  | 从0开始 |
| IndexSegEnd | INTEGER | False | 柱段在连续柱内的序号终点 |  | 从0开始 |
| RcColID | INTEGER | False | 配筋柱ID | dtlConCol_RcCntCol的ID |  |
| PCColID | INTEGER | False | 预制柱ID |  |  |

dtlConCol_SegInfo
[图]

| dtlConCol_SegInfo |  |  |  |  |  |
|---|---|---|---|---|---|
| 柱施工图-柱段信息 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | ID |  |  |
| FloorID | INTEGER | False | 自然层ID | dtlConCol_Flr的ID |  |
| CntColID | INTEGER | False | 连续柱ID | dtlConCol_CntCol的ID |  |
| NoInCol | INTEGER | False | 柱段在连续柱内的序号 |  | 从0开始 |
| IsBrace | INTEGER | False | 是否为斜杆 |  |  |

配筋信息
dtlConCol_RcCntCol
[图]

| dtlConCol_RcCntCol |  |  |  |  |  |
|---|---|---|---|---|---|
| 柱施工图-配筋连续柱 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | ID |  |  |
| FloorID | INTEGER | False | 自然层ID | dtlConCol_Flr的ID |  |
| CntColID | INTEGER | False | 连续柱ID | dtlConCol_CntCol的ID |  |
| NoInCol | INTEGER | False | 柱段在连续柱内的序号 |  | 从0开始 |
| IsBrace | INTEGER | False | 是否为斜杆 |  |  |

dtlConCol_RcSpan
[图]

| dtlConCol_RcSpan |  |  |  |  |  |
|---|---|---|---|---|---|
| 柱施工图-配筋柱跨 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | ID |  |  |
| RcCntColID | INTEGER | False | 配筋连续柱ID | dtlConCol_RcCntCol的ID |  |
| ColSpanDeID | INTEGER | False | 代表柱跨ID | dtlConCol_Span的ID |  |
| MB_A | TEXT | False | 纵筋-A |  |  |
| MB_B | TEXT | False | 纵筋-B |  |  |
| MB_C | TEXT | False | 纵筋-C |  |  |
| HB_A | TEXT | False | 箍筋-A |  |  |
| HB_B | TEXT | False | 箍筋-B |  |  |
| HB_C | TEXT | False | 箍筋-C |  |  |
| HB_Type | INTEGER | False | 箍筋类型 |  |  |

砼墙
通用信息
dtlConWall_Para
[图]

| dtlConWall_Para |  |  |  |  |  |
|---|---|---|---|---|---|
| 墙施工图-数据库信息 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | 枚举值 |  |  |
| ParaVal |  | False | 数值 |  |  |

dtlConWall_Flr
[图]

| dtlConWall_Flr |  |  |  |  |  |
|---|---|---|---|---|---|
| 墙施工图-自然层 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | ID |  |  |
| StdFlrID | INTEGER | False | 标准层ID | pmStdFlr的ID |  |
| ReinFlrID | INTEGER | False | 钢筋层ID | dtlConWall_RcFlr的ID |  |
| Name | TEXT | False | 名称 |  |  |
| LevelB | REAL | False | 底标高 |  |  |
| Height | REAL | False | 层高 |  |  |

dtlConWall_RcFlr
[图]

| dtlConWall_RcFlr |  |  |  |  |  |
|---|---|---|---|---|---|
| 墙施工图-钢筋层 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | ID |  |  |
| Name | TEXT | False | 名称 |  |  |
| FloorID | INTEGER | False | 自然层ID | dtlConWall_Flr的ID |  |

几何信息
边缘构件
dtlConWall_Edge
[图]

| dtlConWall_Edge |  |  |  |  |  |
|---|---|---|---|---|---|
| 墙施工图-边缘构件 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | ID |  |  |
| FloorID | INTEGER | False | 自然层ID | dtlConWall_Flr的ID |  |
| Type | INTEGER | False | 边缘构件类型 |  |  |
| Attrib | INTEGER | False | 属性 |  | 位运算 |
| Boundary | BLOB | False | 轮廓 |  |  |
| RcEMID | INTEGER | False | 配筋边缘构件ID | dtlConWall_RcEdge的ID |  |
| AsStruct | TEXT | False | 构造所需纵筋配筋面积 |  |  |
| AsDesign | TEXT | False | 设计所需纵筋配筋面积 |  |  |
| AsvDesign | TEXT | False | 箍筋的最小体积配箍率 |  |  |
| PcHjRcEmID | INTEGER | False |  |  |  |

dtlConWall_ColSeg
[图]

| dtlConWall_ColSeg |  |  |  |  |  |
|---|---|---|---|---|---|
| 墙施工图-边框柱 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | ID |  |  |
| FloorID | INTEGER | False | 自然层ID | dtlConWall_Flr的ID |  |
| SectDef | TEXT | False | 截面信息 |  |  |
| JointX | REAL | False | 柱所在节点坐标-X |  |  |
| JointY | REAL | False | 柱所在节点坐标-Y |  |  |
| EccX | REAL | False | 沿轴偏心 |  |  |
| EccY | REAL | False | 偏轴偏心 |  |  |
| Rotation | REAL | False | 转角 |  |  |
| EMID | INTEGER | False | 所属边缘构件ID | dtlConWall_Edge的ID |  |

dtlConWall_WallLeg
[图]

| dtlConWall_WallLeg |  |  |  |  |  |
|---|---|---|---|---|---|
| 墙施工图-墙肢 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | ID |  |  |
| SpanID | INTEGER | False | 墙跨ID | dtlConWall_WallSpan的ID |  |
| B | REAL | False | 墙厚 |  |  |
| Len | REAL | False | 阴影区长度 |  |  |
| X1 | REAL | False | 起点坐标-X |  |  |
| Y1 | REAL | False | 起点坐标-Y |  |  |
| X2 | REAL | False | 终点坐标-X |  |  |
| Y2 | REAL | False | 终点坐标-Y |  |  |
| EMID | INTEGER | False | 所属边缘构件ID | dtlConWall_Edge的ID |  |
| LcVS | TEXT | False | 约束边缘构件 λ/2区域配筋-起点竖向 |  |  |
| LcHS | TEXT | False | 约束边缘构件 λ/2区域配筋-起点水平 |  |  |
| LcVE | TEXT | False | 约束边缘构件 λ/2区域配筋-终点竖向 |  |  |
| LcHE | TEXT | False | 约束边缘构件 λ/2区域配筋-终点水平 |  |  |
| PcID | BLOB | False |  |  |  |
| LcLenS | REAL | False | 起端λ/2 区长度 |  | <0表示相邻墙身整体按λ/2区处理 =0或为空表示无λ/2区 |
| LcLenE | REAL | False | 终端λ/2 区长度 |  | <0表示相邻墙身整体按λ/2区处理 =0或为空表示无λ/2区 |
| Ecc | REAL | False | 偏心 |  |  |
| GridCurve | BLOB | False | 墙肢网格线 |  |  |
| AsvCalc | REAL | False | 箍筋计算面积 |  |  |
| Attribs | INTEGER | False | 属性 |  |  |

墙身
dtlConWall_CntWall
[图]

| dtlConWall_CntWall |  |  |  |  |  |
|---|---|---|---|---|---|
| 墙施工图-连续墙 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | ID |  |  |
| FloorID | INTEGER | False | 层号 |  |  |
| Attrib | INTEGER | False | 属性 |  |  |
| SpanNum | INTEGER | False | 跨数 |  |  |
| RcCWID | INTEGER | False | 配筋连续墙ID |  |  |
| MirroredFlag | INTEGER | False |  |  |  |

dtlConWall_WallSpan
[图]

| dtlConWall_WallSpan |  |  |  |  |  |
|---|---|---|---|---|---|
| 墙施工图-墙跨 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | ID |  |  |
| FloorID | INTEGER | False | 自然层ID | dtlConWall_Flr的ID |  |
| CalcID | INTEGER | False | 计算模型ID |  |  |
| B | REAL | False | 墙厚 |  |  |
| Len | REAL | False | 墙跨长 |  | 网格线长度 |
| X1 | REAL | False | 起点坐标-X |  |  |
| Y1 | REAL | False | 起点坐标-Y |  |  |
| X2 | REAL | False | 终点坐标-X |  |  |
| Y2 | REAL | False | 终点坐标-Y |  |  |
| ZT1 | REAL | False | 起点顶部高差 |  |  |
| ZT2 | REAL | False | 终点顶部高差 |  |  |
| ZB1 | REAL | False | 起点底部高差 |  |  |
| ZB2 | REAL | False | 终点底部高差 |  |  |
| XC | REAL | False | 圆弧中心坐标-X |  |  |
| YC | REAL | False | 圆弧中心坐标-Y |  |  |
| Ecc | REAL | False | 偏心 |  |  |

dtlConWall_WallBody
[图]

| dtlConWall_WallBody |  |  |  |  |  |
|---|---|---|---|---|---|
| 墙施工图-墙身 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | ID |  |  |
| SpanID | INTEGER | False | 墙跨ID | dtlConWall_WallSpan的ID |  |
| B | REAL | False | 墙厚 |  |  |
| Len | REAL | False | 墙身长度 |  |  |
| X1 | REAL | False | 墙身起点坐标-X |  |  |
| Y1 | REAL | False | 墙身起点坐标-Y |  |  |
| X2 | REAL | False | 墙身终点坐标-X |  |  |
| Y2 | REAL | False | 墙身终点坐标-Y |  |  |
| RcBodyID | INTEGER | False | 配筋墙身ID | dtlConWall_RcWallBody的ID |  |
| AllSpanIDs | BLOB | False | 墙身包含的全部墙跨ID | dtlConWall_WallSpan的ID |  |
| PcID | BLOB | False |  |  |  |
| Ecc | REAL | False | 偏心 |  |  |
| GridCurve | BLOB | False | 墙身网格线 |  |  |

连梁
dtlConWall_WallBeam
[图]

| dtlConWall_WallBeam |  |  |  |  |  |
|---|---|---|---|---|---|
| 墙施工图-连梁 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | ID |  |  |
| FloorID | INTEGER | False | 自然层ID | dtlConWall_Flr的ID |  |
| B | REAL | False | 梁宽 |  |  |
| H | REAL | False | 梁高 |  |  |
| HDiff | REAL | False | 标高高差 |  |  |
| Len | REAL | False | 跨度 |  |  |
| X1 | REAL | False | 起点坐标-X |  |  |
| Y1 | REAL | False | 起点坐标-Y |  |  |
| X2 | REAL | False | 终点坐标-X |  |  |
| Y2 | REAL | False | 终点坐标-Y |  |  |
| RcBeamID | INTEGER | False | 配筋连梁ID | dtlConWall_RcWallBeam的ID |  |
| XC | REAL | False | 圆弧中心坐标-X |  |  |
| YC | REAL | False | 圆弧中心坐标-Y |  |  |
| PcID | INTEGER | False |  |  |  |

配筋信息
边缘构件
dtlConWall_RcEdge
[图]

| dtlConWall_RcEdge |  |  |  |  |  |
|---|---|---|---|---|---|
| 墙施工图-配筋边缘构件 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | ID |  |  |
| ReinFlrID | INTEGER | False | 钢筋层ID | dtlConWall_RcFlr的ID |  |
| Name | TEXT | False | 名称 |  |  |
| MainBar | TEXT | False | 纵筋 |  |  |
| HoopBar | TEXT | False | 箍筋 |  |  |
| Flags | INTEGER | False | 箍筋类型 |  |  |

墙身
dtlConWall_RcWallBody
[图]

| dtlConWall_RcWallBody |  |  |  |  |  |
|---|---|---|---|---|---|
| 墙施工图-配筋墙身 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | ID |  |  |
| ReinFlrID | INTEGER | False | 钢筋层ID | dtlConWall_RcFlr的ID |  |
| Name | TEXT | False | 名称 |  |  |
| B | INTEGER | False | 墙宽 |  |  |
| NumRow | INTEGER | False | 钢筋排数 |  |  |
| HoriBar | TEXT | False | 水平分布筋 |  |  |
| VertBar | TEXT | False | 竖向分布筋 |  |  |
| TieBar | TEXT | False | 拉筋 |  |  |
| TieBarType | TEXT | False | 拉筋类型 |  | 0-由工程参数决定 1-双向 2-梅花双向 |

dtlConWall_RcBodySupBar
[图]

| dtlConWall_RcBodySupBar |  |  |  |  |  |
|---|---|---|---|---|---|
| 墙施工图-墙身非贯通筋 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| RcBdID | INTEGER | False | ID |  |  |
| Kind | INTEGER | False | 非贯通筋类型 |  |  |
| BarSpec | TEXT | False | 钢筋贵妃 |  |  |
| LenExpr | TEXT | False | 钢筋长度字符串 |  |  |

连梁
dtlConWall_RcWallBeam
[图]

| dtlConWall_RcWallBeam |  |  |  |  |  |
|---|---|---|---|---|---|
| 墙施工图-配筋连梁 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | ID |  |  |
| ReinFlrID | INTEGER | False | 钢筋层ID | dtlConWall_RcFlr的ID |  |
| Name | TEXT | False | 名称 |  |  |
| TopBar | TEXT | False | 上铁 |  |  |
| BottomBar | TEXT | False | 下铁 |  |  |
| HoopBar | TEXT | False | 箍筋 |  |  |
| YaoBar | TEXT | False | 腰筋 |  |  |
| YaoLaBar | TEXT | False | 侧向筋的拉结筋 |  |  |
| CrossBar | TEXT | False | 斜筋或对角暗撑的单侧纵筋 |  |  |
| CrossLaBar | TEXT | False | 交叉斜筋的末端拉筋或对角暗撑的箍筋 |  |  |
| CrossBarType | INTEGER | False | 斜筋类型 |  | 0-没有 1-交叉斜筋 2-对角暗撑 3-集中对角暗撑 |

砼板
通用信息
dtlConSlab_Para
[图]

| dtlConSlab_Para |  |  |  |  |  |
|---|---|---|---|---|---|
| 板施工图-数据库信息 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | 枚举值 |  |  |
| ParaVal |  | False | 数值 |  |  |

几何信息
dtlConSlab_Base
[图]
[图]
[图]
[图]

| dtlConSlab_Base |  |  |  |  |  |
|---|---|---|---|---|---|
| 板施工图-基本信息 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| BottomJsNum | INTEGER | False | 现浇板块数量 |  |  |
| SupportJsNum | INTEGER | False | 支座数量 |  |  |
| GjbNum | INTEGER | False | 钢筋表数量 |  |  |
| GjbId | INTEGER | False | 钢筋表ID |  |  |
| JzlID | INTEGER | False | 井字梁ID |  |  |
| PtgjNum | INTEGER | False | 普通钢筋数量 |  |  |
| LtgjNum | INTEGER | False | 拉通钢筋数量 |  |  |
| RygjNum | INTEGER | False | 拉通钢筋数量 |  |  |
| SteelIdMax | INTEGER | False | 钢筋ID的最大值 |  |  |
| nmpx | INTEGER | False | 房间归并总数量 |  |  |
| nybj | INTEGER | False | 样板间数量 |  |  |
| vvSupportSpan | BLOB | False | 按平法标注时板跨串 |  |  |
| nXtbYbj | INTEGER | False | 悬挑板(样板间数量) |  |  |
| NBeam_ydb | INTEGER | False | 梁数量 |  |  |
| NWall_ydb | INTEGER | False | 墙数量 |  |  |
| NSubbeam_ydb | INTEGER | False | 次梁数量 |  |  |
| NRoom_ydb | INTEGER | False | 房间数量 |  |  |
| NXtb_ydb | INTEGER | False | 悬挑板数量 |  |  |
| WllgID | INTEGER | False | 无梁楼盖ID |  |  |
| WllgBH | INTEGER | False | 无梁楼盖编号最大号 |  |  |
| ZsKzbdID | INTEGER | False | 柱上，跨板带ID |  |  |
| ZMID | INTEGER | False | 柱帽ID |  |  |
| vWllgNum | INTEGER | False | 柱上无梁楼盖总数量 |  |  |
| vZsKzbdNum | INTEGER | False | 柱上，跨中板带数量 |  |  |
| vZMdataNum | INTEGER | False | 柱帽数量 |  |  |
| NumSlabTopBar | INTEGER | False | 布置了板面钢筋的楼板数量 |  |  |
| KzWllgBH | INTEGER | False | 跨中无梁楼盖最大编号 |  |  |
| stripZsbdNO | INTEGER | False | 柱上板带总数量 |  |  |
| BototmIdVec | INTEGER | False | 本层所有楼板ID（用作模型对比） |  |  |
| SupportIdVec | INTEGER | False | 本层所有支座ID（用作模型对比） |  |  |
| ArcGjBototmIds | INTEGER | False | 暂未使用 |  |  |
| DdlBeamIdsGroup1 | INTEGER | False | 等代梁分组1 |  |  |
| DdlBeamIdsGroup2 | INTEGER | False | 等代梁分组2 |  |  |
| DdlBeamIdsNoGroup | INTEGER | False | 等代梁，未分组 |  |  |
| XTopBarByUserIds | INTEGER | False | 用户指定了X向板顶钢筋的楼板ID数组 |  |  |
| YTopBarByUserIds | INTEGER | False | 用户指定了Y向板顶钢筋的楼板ID数组 |  |  |
| PreSetBotTopRegion | TEXT | False | 预设通长筋信息 |  |  |

dtlConSlab_Btm
[图]
[图]
[图]
[图]
[图]

| dtlConSlab_Btm |  |  |  |  |  |
|---|---|---|---|---|---|
| 板施工图-底筋计算及配筋表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | ID | pmSlab的ID |  |
| FlrNo | INTEGER | False | 层号 |  |  |
| Shape | INTEGER | False | 板形状 |  |  |
| Thick | INTEGER | False | 板厚 |  |  |
| Bhc | INTEGER | False | 板下皮保护层厚度 |  |  |
| CuoC | INTEGER | False | 板错层厚度 |  |  |
| Loc | INTEGER | False | 板区域位置 |  |  |
| DrwMark_1 | INTEGER | False | 钢筋是否绘制标志 |  |  |
| DrwMark_2 | INTEGER | False | 钢筋是否绘制标志 |  |  |
| AdddrwMark_1 | INTEGER | False | 附加钢筋是否绘制标志 |  |  |
| AdddrwMark_2 | INTEGER | False | 附加钢筋是否绘制标志 |  |  |
| Ybj | INTEGER | False | 是否是样板间标志 |  |  |
| RfcControl | INTEGER | False | 是否为人防控制板配筋标志 |  |  |
| VertexX | BLOB | False | 效矩形4个点坐标-X |  |  |
| VertexY | BLOB | False | 效矩形4个点坐标-Y |  |  |
| Aw | REAL | False | 角度，房间定位角，异形房间按最
长边确定 |  |  |
| Rw | REAL | False | 砼等级 |  |  |
| Dead | REAL | False | 恒载 |  |  |
| Live | REAL | False | 活载 |  |  |
| RfLoad | REAL | False | 人防荷载 |  |  |
| BotReduce | REAL | False | 板底弯矩折减 |  |  |
| TopReduce | REAL | False | 支座弯矩折减 |  |  |
| Shear | BLOB | False | 剪力 |  |  |
| Moment_1 | REAL | False | 弯矩 |  |  |
| Moment_2 | REAL | False | 弯矩 |  |  |
| Moment_c_1 | REAL | False | 计算裂缝时的弯矩 |  |  |
| Moment_c_2 | REAL | False | 计算裂缝时的弯矩 |  |  |
| Moment_rf_1 | REAL | False | 计算人防时的弯矩 |  |  |
| Moment_rf_2 | REAL | False | 计算人防时的弯矩 |  |  |
| Moment_ang_1 | REAL | False | 计算弯矩的方向角 |  |  |
| Moment_ang_2 | REAL | False | 计算弯矩的方向角 |  |  |
| Stlas_1 | REAL | False | 板底计算面积1 |  |  |
| Stlas_2 | REAL | False | 板底计算面积2 |  |  |
| Crack_1 | REAL | False | 裂缝1 |  |  |
| Crack_2 | REAL | False | 裂缝2 |  |  |
| Def | REAL | False | 挠度 |  |  |
| Info_1 | TEXT | False | 配筋信息1 |  |  |
| Info_2 | TEXT | False | 配筋信息2 |  |  |
| Info_Top_1 | TEXT | False | 板顶配筋 |  |  |
| Info_Top_2 | TEXT | False | 板顶配筋 |  |  |
| Drwmark_top_1 | INTEGER | False | 板面钢筋绘制标志 |  |  |
| Drwmark_top_2 | INTEGER | False | 板面钢筋绘制标志 |  |  |
| Adddrwmark_top_1 | INTEGER | False | 附加板面钢筋绘制标志 |  |  |
| Adddrwmark_top_2 | INTEGER | False | 附加板面钢筋绘制标志 |  |  |
| Pfdrwmark | INTEGER | False |  |  |  |
| PolyVertexX | TEXT | False | 轮廓坐标-X |  |  |
| PolyVertexY | TEXT | False | 轮廓坐标-Y |  |  |
| PolyVertexZ | TEXT | False | 轮廓坐标-Z |  |  |
| PolyCenterX | REAL | False | 轮廓中心点坐标-X |  |  |
| PolyCenterY | REAL | False | 轮廓中心点坐标-Y |  |  |
| AroundIds | TEXT | False | 单块楼板围区的所有支座ID |  |  |
| nJG | INTEGER | False | 加固方法 |  |  |
| JgMatFa | REAL | False | 加固（钢板或者纤维布）强度值 |  |  |
| JgAs1 | REAL | False | 加固面积，X 向 |  |  |
| JgAs2 | REAL | False | 加固面积，Y 向 |  |  |
| BhcTop | INTEGER | False | 板上皮保护层厚度 |  |  |

dtlConSlab_Sup
[图]
[图]
[图]

| dtlConSlab_Sup |  |  |  |  |  |
|---|---|---|---|---|---|
| 板施工图-顶筋计算及配筋表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | ID |  |  |
| FlrNo | INTEGER | False | 层号 |  |  |
| GouJian | INTEGER | False | 支座关联构件类型 |  |  |
| CuoC | INTEGER | False | 错层信息 |  |  |
| Bound_1 | INTEGER | False | 边界条件-1 |  |  |
| Bound_2 | INTEGER | False | 边界条件-2 |  |  |
| DrwMark_1 | INTEGER | False | 支座钢筋绘制标志 |  |  |
| DrwMark_2 | INTEGER | False | 支座钢筋绘制标志 |  |  |
| AdddrwMark_1 | INTEGER | False | 附加支座钢筋绘制标志 |  |  |
| AdddrwMark_2 | INTEGER | False | 附加支座钢筋绘制标志 |  |  |
| Moment_1 | REAL | False | 弯矩-1 |  |  |
| Moment_2 | REAL | False | 弯矩-2 |  |  |
| Moment_c_1 | REAL | False | 计算裂缝的弯矩-1 |  |  |
| Moment_c_2 | REAL | False | 计算裂缝的弯矩-2 |  |  |
| Moment_rf_1 | REAL | False | 计算人防的弯矩-1 |  |  |
| Moment_rf_2 | REAL | False | 计算人防的弯矩-2 |  |  |
| Stlas_1 | REAL | False | 计算面积-1 |  |  |
| Stlas_2 | REAL | False | 计算面积-2 |  |  |
| Shear_1 | REAL | False | 剪力,非矩形目前不能计算其剪力 |  |  |
| Shear_2 | REAL | False | 剪力,非矩形目前不能计算其剪力 |  |  |
| Crack_1 | REAL | False | 裂缝-1 |  |  |
| Crack_2 | REAL | False | 裂缝-2 |  |  |
| LenFact_1 | REAL | False | 考虑板坡度的长度调整 |  |  |
| LenFact_2 | REAL | False | 考虑板坡度的长度调整 |  |  |
| Room_1 | INTEGER | False | 房间编号 |  |  |
| Room_2 | INTEGER | False | 房间编号 |  |  |
| Length_1 | INTEGER | False | 两侧钢筋长度-1 |  |  |
| Length_2 | INTEGER | False | 两侧钢筋长度-2 |  |  |
| Lwz_1 | INTEGER | False | 两侧钢筋弯折长度-1 |  |  |
| Lwz_2 | INTEGER | False | 两侧钢筋弯折长度-2 |  |  |
| Info_1 | TEXT | False | 配筋信息 |  |  |
| Info_2 | TEXT | False | 配筋信息 |  |  |
| Pxz | INTEGER | False | 无 |  |  |
| nJG | INTEGER | False | 加固方式 |  |  |
| JgMatFa | REAL | False | 加固（钢板或者纤维布）强度值 |  |  |
| JgAs | REAL | False | 加固面积 |  |  |
| ZZLength | INTEGER | False | 模型对比用的支座长度值（无意义） |  |  |

dtlConSlab_RoomMerge
[图]

| dtlConSlab_RoomMerge |  |  |  |  |  |
|---|---|---|---|---|---|
| 板施工图-平法房间归并信息 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| FlrNo | INTEGER | False | 层号 |  |  |
| RoomNum | INTEGER | False | 房间数量 |  |  |
| ID | INTEGER | False | 样板间id号 |  |  |
| YbjNum | INTEGER | False | 样板间号 |  |  |
| Lbtype | INTEGER | False | 板块类型0-2:LB/WB/XB |  |  |

dtlConSlab_WLLG
[图]

| dtlConSlab_WLLG |  |  |  |  |  |
|---|---|---|---|---|---|
| 板施工图-无梁楼盖 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | ID |  |  |
| FlrNo | INTEGER | False | 层号 |  |  |
| Itype | INTEGER | False | 类型:柱上板带或者跨中板带 |  |  |
| Bh | INTEGER | False | 板带编号 |  |  |
| Thick | INTEGER | False | 板带厚度 |  |  |
| Width1 | INTEGER | False | 板带宽度-左侧 |  |  |
| Width2 | INTEGER | False | 板带宽度-右侧 |  |  |
| Nspan | INTEGER | False | 板带跨数 |  |  |
| Xuantiao | INTEGER | False | 板带是否右悬挑 |  |  |
| Info_1 | TEXT | False | 贯通钢筋（底部） |  |  |
| Info_2 | TEXT | False | 贯通钢筋（顶部） |  |  |

dtlConSlab_WLLGColCap
[图]
[图]

| dtlConSlab_WLLGColCap |  |  |  |  |  |
|---|---|---|---|---|---|
| 板施工图-无梁楼盖-柱帽 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | ID |  |  |
| FlrNo | INTEGER | False | 层号 |  |  |
| ColID | INTEGER | False | 柱帽所在位置柱子ID |  |  |
| pt_X | REAL | False | 柱子节点X |  |  |
| pt_Y | REAL | False | 柱子节点Y |  |  |
| Ang[2] | REAL | False | 柱子角度（X和Y） |  |  |
| wid1 | INTEGER | False | 柱帽X向一侧宽度 |  |  |
| wid2 | INTEGER | False | 柱帽X向另一侧宽度 |  |  |
| hei1 | INTEGER | False | 柱帽Y向一侧宽度 |  |  |
| hei2 | INTEGER | False | 柱帽Y向另一侧宽度 |  |  |
| ZsbdID_1 | INTEGER | False | 柱帽X向所在柱上板带ID |  |  |
| ZsbdID_2 | INTEGER | False | 柱帽Y向所在柱上板带ID |  |  |
| thick_1 | INTEGER | False | 柱帽X向厚度 |  |  |
| thick_2 | INTEGER | False | 柱帽Y向厚度 |  |  |
| moment | REAL | False | 柱帽弯矩以及人防弯矩【4】 |  |  |
| stlas_1 | REAL | False | 柱帽计算面积X |  |  |
| stlas_2 | REAL | False | 柱帽计算面积Y |  |  |
| info_1 | TEXT | False | 钢筋信息X |  |  |
| info_2 | TEXT | False | 钢筋信息Y |  |  |
| ang_1 | REAL | False | 无 |  |  |
| SpanNumAsBeam_1 | INTEGER | False | 柱帽X向积分面数量 |  |  |
| SpanNumAsBeam_2 | INTEGER | False | 柱帽Y向积分面数量 |  |  |

dtlConSlab_WLLGSlab
[图]
[图]
[图]

| dtlConSlab_WLLGSlab |  |  |  |  |  |
|---|---|---|---|---|---|
| 板施工图-无梁楼盖板带配筋 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | ID |  |  |
| FlrNo | INTEGER | False | 层号 |  |  |
| wllgid | INTEGER | False | 无量楼盖ID |  |  |
| widexchang | INTEGER | False | 是否需要交换左右宽度值 |  |  |
| AxisIndex | INTEGER | False | 轴线号索引 |  |  |
| vColID | BLOB | False | 柱上板带记录柱子ID数组 |  |  |
| vSupportIndex | BLOB | False | 柱上板带时，记录各段柱之间支座索引号 |  |  |
| moment | BLOB | False | 板带弯矩数组 |  |  |
| stlas_1 | REAL | False | 板带计算面积（下） |  |  |
| stlas_2 | REAL | False | 板带计算面积（上） |  |  |
| info_1 | TEXT | False | 板带适配钢筋（下） |  |  |
| info_2 | TEXT | False | 板带适配钢筋（上） |  |  |
| Xs | REAL | False | 板带起始节点坐标X |  |  |
| Ys | REAL | False | 板带起始节点坐标Y |  |  |
| Xe | REAL | False | 板带终止节点坐标X |  |  |
| Ye | REAL | False | 板带终止节点坐标Y |  |  |
| X1s | REAL | False | 板带第一跨开始处的节点位置 |  |  |
| Y1s | REAL | False | 板带第一跨开始处的节点位置 |  |  |
| X1e | REAL | False | 板带第一跨终止处的节点位置 |  |  |
| Y1e | REAL | False | 板带第一跨终止处的节点位置 |  |  |
| vSpanUpMomentDL | BLOB | False | 板带各跨上部弯矩（恒活） |  |  |
| vSpanUpMomentRF | BLOB | False | 板带各跨上部弯矩（人防） |  |  |
| vSpanDownMomentDL | BLOB | False | 板带各跨下部弯矩（恒活） |  |  |
| vSpanDownMomentRF | BLOB | False | 板带各跨下部弯矩（人防 |  |  |
| vSpanUpStlAs | BLOB | False | 板带各跨上部计算面积 |  |  |
| vSpanDownStlAs | BLOB | False | 板带各跨下部计算面积 |  |  |
| vSpanDownInfo | BLOB | False | 板带各跨下部适配钢筋 |  |  |
| vSpanUpInfo | BLOB | False | 板带各跨上部适配钢筋 |  |  |
| vBeamSpanDownInfo | BLOB | False | 板带各跨下部暗梁适配钢筋 |  |  |
| vBeamSpanUpInfo | BLOB | False | 板带各跨上部暗梁适配钢筋 |  |  |
| Beaminfo_1 | TEXT | False | 暗梁适配（下） |  |  |
| Beaminfo_2 | TEXT | False | 暗梁适配（上） |  |  |
| vSpanNumAsBeam | BLOB | False | 板带各跨积分面数量 |  |  |

配筋信息
dtlConSlab_RcJZL
[图]

| dtlConSlab_RcJZL |  |  |  |  |  |
|---|---|---|---|---|---|
| 板施工图-井字梁信息 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | ID |  |  |
| FlrNo | INTEGER | False | 层号 |  |  |
| GridRoomID | BLOB | False | 组成井字梁的房间ID数组 |  |  |
| GridMemberID | BLOB | False | 组成井字梁的非框架梁ID数组 |  |  |

dtlConSlab_RcStl
[图]

| dtlConSlab_RcStl |  |  |  |  |  |
|---|---|---|---|---|---|
| 板施工图- 钢筋信息表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | ID |  |  |
| FlrNo | INTEGER | False | 层号 |  |  |
| GjbId | INTEGER | False | 钢筋表ID |  |  |
| Itype | INTEGER | False | 钢筋类型：正筋，负筋等 |  |  |
| Detail | INTEGER | False | 是否已有详细标注 |  |  |
| Mebid | INTEGER | False | 钢筋标注构件ID |  |  |
| Kfx | INTEGER | False | 钢筋方向 |  |  |
| Ang | REAL | False | 钢筋布置角度 |  |  |
| Xs | REAL | False | 钢筋线起点X |  |  |
| Ys | REAL | False | 钢筋线起点Y |  |  |
| Xe | REAL | False | 钢筋线终点X |  |  |
| Ye | REAL | False | 钢筋线终点Y |  |  |

dtlConSlab_RcStlAny
[图]

| dtlConSlab_RcStlAny |  |  |  |  |  |
|---|---|---|---|---|---|
| 板施工图- 任意钢筋信息表 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | ID |  |  |
| FlrNo | INTEGER | False | 层号 |  |  |
| Itype | INTEGER | False | 钢筋表ID |  |  |
| Mebid | INTEGER | False | 任意钢筋关联构件，如洞口ID |  |  |
| Bh | INTEGER | False | 编号 |  |  |
| Info | TEXT | False | 钢筋信息 |  |  |
| Len | INTEGER | False | 钢筋长度 |  |  |
| Lwz | INTEGER | False | 左弯折长度 |  |  |
| Rwz | INTEGER | False | 右弯折长度 |  |  |
| Ang | REAL | False | 钢筋布置角度 |  |  |
| Xs | REAL | False | 钢筋线起点X |  |  |
| Ys | REAL | False | 钢筋线起点Y |  |  |
| Xe | REAL | False | 钢筋线终点X |  |  |
| Ye | REAL | False | 钢筋线终点Y |  |  |

dtlConSlab_RcStlLT
[图]

| dtlConSlab_RcStlLT |  |  |  |  |  |
|---|---|---|---|---|---|
| 板施工图- 拉通钢筋信息 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | ID |  |  |
| FlrNo | INTEGER | False | 层号 |  |  |
| Gjbid | INTEGER | False | 钢筋表ID |  |  |
| Itype | INTEGER | False | 钢筋类型：比如普通钢筋还是拉通钢筋 |  |  |
| Detail | INTEGER | False | 是否详细标注 |  |  |
| Num | INTEGER | False | 关联构件个数 |  |  |
| Mebid | BLOB | False | 关联构件ID数组 |  |  |
| DimNum | INTEGER | False | 标注次数 |  |  |
| Ang | REAL | False | 钢筋布置角度 |  |  |
| Xs | REAL | False | 钢筋线起点X |  |  |
| Ys | REAL | False | 钢筋线起点Y |  |  |
| Xe | REAL | False | 钢筋线终点X |  |  |
| Ye | REAL | False | 钢筋线终点Y |  |  |
| StExt | INTEGER | False | 起点外挑长度 |  |  |
| EdExt | INTEGER | False | 终点外挑长度 |  |  |

dtlConSlab_RcStlTable
[图]

| dtlConSlab_RcStlTable |  |  |  |  |  |
|---|---|---|---|---|---|
| 板施工图- 钢筋表信息 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| ID | INTEGER | False | ID |  |  |
| FlrNo | INTEGER | False | 层号 |  |  |
| Bh | INTEGER | False | 钢筋编号 |  |  |
| Itype | INTEGER | False | 钢筋类型 |  |  |
| Llen | INTEGER | False | 钢筋左长度（负筋），正筋时为总长度 |  |  |
| Rlen | INTEGER | False | 钢筋右长度（负筋） |  |  |
| Lwz | INTEGER | False | 左弯折 |  |  |
| Rwz | INTEGER | False | 右弯折 |  |  |
| Detail | INTEGER | False | 是否已有详细标注 |  |  |
| Udefine | INTEGER | False | 当前编号是否由用户指定 |  |  |
| Info | TEXT | False | 配筋信息 |  |  |
| Lmax | INTEGER | False | 最大长度 |  |  |
| Lmin | INTEGER | False | 最小长度 |  |  |
| Ltotal | INTEGER | False | 总长度 |  |  |
| Num | INTEGER | False | 根数 |  |  |
| Weight | INTEGER | False | 重量 |  |  |

dtlConSlab_RcStlTop
[图]

| dtlConSlab_RcStlTop |  |  |  |  |  |
|---|---|---|---|---|---|
| 板施工图- 板顶预设分布钢筋信息 |  |  |  |  |  |
| 变量 | 类型 | 不可空 | 描述 | 数据来源 | 备注 |
| irmID | INTEGER | False | 楼板ID |  |  |
| FlrNo | INTEGER | False | 层号 |  |  |
| infox | TEXT | False | 预设板顶X向钢筋 |  |  |
| infoy | TEXT | False | 预设板顶Y向钢筋 |  |  |
| infoxBot | TEXT | False | 预设板底X向钢筋 |  |  |
| infoyBot | TEXT | False | 预设板底Y向钢筋 |  |  |
