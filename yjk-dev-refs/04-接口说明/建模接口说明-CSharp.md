建模接口说明文档
1.标准层
（1）标准层创建
Mdl_StdFlr StdFlr_Generate(int height, double deadload=5.0, double liveload = 2.0)
该方法用于创建标准层，返回创建的标准层对象。

| height (整数型) | 模型中标准层显示的层高。 |
|---|---|
| deadload（双精度浮点型） | 恒载取值，默认为5.0KN/m2。 |
| liveload（双精度浮点型） | 活载取值，默认为2.0KN/m2。 |

（2）空间层创建
Mdl_StdFlr SpcFlr_Generate()
该方法用于创建空间层，参数列表为空，返回创建的空间层对象。
（3）楼层组装
void Floors_Assemb (int H_start, Mdl_StdFlr bzc, int number, int height)
该方法用于楼层组装，返回为空。

| h_start（整数型） | 起始的高度为层底标高，单位为mm。 |
|---|---|
| bzc（自定义标准层类型） | 楼层组装使用的标准层。 |
| number（整数型） | 复制次数。 |
| height（整数型） | 层高，单位为mm。 |

（3.1）楼层组装
void Floor_Assemb (Mdl_StdFlr bzc,int levelB,int height,string Name="")
该方法用于楼层组装，返回为空。

| bzc（自定义标准层类型） | 楼层组装使用的标准层。 |
|---|---|
| levelB（整数型） | 层底标高，单位为mm。 |
| height（整数型） | 层高，单位为mm。 |
| Name（字符串类型） | 楼层名称。 |

（4）标准层复制（已弃用，更为Floors_Assemb）
void bzc_copy(int H_start, Mdl_StdFlr bzc, int number, int height)
该方法用于楼层组装，返回为空。

| h_start（整数型） | 起始的高度为层底标高，单位为mm。 |
|---|---|
| bzc（自定义标准层类型） | 待复制的标准层。 |
| number（整数型） | 复制次数。 |
| height（整数型） | 层高，单位为mm。 |

（5）辅助类型
BzcPara
该类用于生成默认的标准层参数，可按照索引进行成员的修改，并生成字符串参数

| public BzcPara() | 该类的构造函数。 |
|---|---|
| public float getVal(int index) | 获取某一索引的参数。 |
| public void setVal(int index, int val) | 设置某一索引的参数。 |
| public string GetValString() | 获取字符串类型的标准层参数。 |

附参数索引含义

| 0 | 梁钢筋保护层厚度 | 20 | 墙竖向分布筋级别 |
|---|---|---|---|
| 1 | 板厚 | 21 | 其它类别的钢构件钢材，默认为Q235 |
| 2 | 板强度*10 | 22 | 墙保护层厚度,默认取板的 |
| 3 | 板保护层厚度 | 23 | 板主筋级别 |
| 4 | 柱混凝土强度*10 | 24 | 柱钢材 |
| 5 | 梁混凝土强度*10 | 25 | 梁钢材 |
| 6 | 墙混凝土强度*10 | 26 | 墙钢材 |
| 7 | 梁主筋钢筋类别 | 27 | 支撑钢材 |
| 8 | 柱主筋钢筋类别 | 28 | 柱铝合金 |
| 9 | 砌体的砂浆强度等级M*10 | 29 | 梁铝合金 |
| 10 | 砌体的块体强度等级MU*10 | 30 | 墙铝合金 |
| 11 | 灌浆砼等级Cb*10 | 31 | 支撑铝合金 |
| 12 | 墙主筋钢筋类别 | 32 | 其它铝合金 |
| 13 | 混合砂浆(0)或水泥砂浆 | 33 |  |
| 14 | 柱钢筋保护层厚度 | 34 |  |
| 15 | 支撑砼强度等级 | 35 |  |
| 16 | 柱箍筋级别 |  |  |
| 17 | 梁箍筋级别 |  |  |
| 18 | 边缘构件箍筋级别 |  |  |
| 19 | 墙水平分布筋级别 |  |  |

2.节点
（1）节点生成
List<List<Mdl_Joint>> node_generate(List<int> xspans, List<int> yspans, Mdl_StdFlr bzc, int Eon = 0)
该方法用于批量生成节点，返回生成的二维节点列表。

| xspans（一维整数型列表） | X向开间，单位为mm。 |
|---|---|
| yspans（一维整数型列表） | Y向开间，单位为mm。 |
| bzc（自定义标准层类型） | 节点所在的标准层。 |
| Eon（整数型） | 上节点高，默认取0，为标准层顶的位置，单位mm。 |

（2）节点生成
Mdl_Joint Joint_Generate(int StdFlrID, float X, float Y, float Hdiff= 0)
该方法用于单个节点生成，返回生成的节点对象。

| StdFlrID（整数型） | 节点所在的标准层ID，可通过获取内部变量查询。 |
|---|---|
| X（浮点型） | 节点的X坐标。 |
| Y（浮点型） | 节点的Y坐标。 |
| HDiff（整数型） | 上节点高，为标准层顶的位置，默认取0，单位mm。 |

3.网格及轴线
（1）网格生成
List<Mdl_Grid> grid_generate(List<List<Mdl_Joint>> nodelist, int direct_x, int direct_y)
该方法用于批量生成网格，返回生成的二维网格列表。

| nodelist（二维节点类型列表） | 待生成网格的二维节点列表。 |
|---|---|
| direct_x（整数型） | 取1表示在二维节点列表的X向生成网格，取0表示X向不生成网格。 |
| direct_y（整数型） | 取1表示在二维节点列表的Y向生成网格，取0表示Y向不生成网格。 |

（2）网格生成
Mdl_Grid Grid_Generate(int StdFlrID, int Jt1ID, int Jt2ID, int AxisID)
该方法用于单个网格生成，返回生成的网格对象。

| StdFlrID（整数型） | 节点所在的标准层ID，可通过获取内部变量查询。 |
|---|---|
| Jt1ID（整数型） | 节点1的ID，可通过获取内部变量查询。 |
| Jt2ID（整数型） | 节点2的ID，可通过获取内部变量查询。 |
| AxisID（整数型） | 轴线ID，可通过获取内部变量查询。 |

（3）轴线生成
Mdl_Axis Axis_Generate(int StdFlrID, int Jt1ID, int Jt2ID)

| StdFlrID（整数型） | 节点所在的标准层ID，可通过获取内部变量查询。 |
|---|---|
| Jt1ID（整数型） | 节点1的ID，可通过获取内部变量查询； 如果小于0，表示圆弧的圆心。 |
| Jt2ID（整数型） | 节点2的ID，可通过获取内部变量查询； 如是圆弧轴线，则表示圆弧轴线上的一点。 |

4.构件及荷载定义
（1）荷载定义
Mdl_LoadSect Load_Def (int elementkind,string shapeval,string name="")
该方法用于定义荷载，返回生成的荷载定义。

| elementkind（整数型） | 荷载布置的构件类型，详见下表4.1。 |
|---|---|
| shapeval（字符串类型） | 荷载参数构成的字符串，字符串中第一个浮点数表示荷载类型，详见下表4.2，其余浮点数表示该荷载类型下的参数值。 |
| name（字符串类型） | 荷载定义的名称。 |

表4.1

| 1 | 墙 | 41 | 楼梯 | 102 | 柱墩 |
|---|---|---|---|---|---|
| 11 | 柱 | 42 | 钢梯 | 103 | 桩 |
| 12 | 梁 | 62 | 悬挑板 | 104 | 地基梁 |
| 13 | 支撑 | 64 | 预制板 | 105 | 承台 |
| 14 | 次梁 | 65 | 楼板 | 106 | 独基 |
| 15 | 圈梁 | 66 | 空心板 | 107 | 拉梁 |
| 21 | 墙洞 | 67 | 柱帽 |  |  |
| 22 | 板洞 | 101 | 筏板 |  |  |

表4.2

| 1 | 均布荷载 | 10 | 分布三角形 | 75 | 墙面外梯形荷载 |
|---|---|---|---|---|---|
| 2 | 左端均布 | 11 | 分布梯形 | 78 | 移动荷载 |
| 3 | 右端均布 | 21 | 水平均布荷载 | 79 | 斜墙面外梯形荷载(法向) |
| 4 | 集中荷载 | 24 | 水平集中荷载 | 80 | 斜墙面外梯形荷载(沿墙) |
| 5 | 柱垂直集中荷载 | 61 | 均布扭矩 | 81 | 斜梁均布 |
| 6 | 满布梯形 | 64 | 集中扭矩，右手螺旋规则 |  |  |
| 7 | 柱底部均布荷载 | 71 | 楼板上的线荷载 |  |  |
| 8 | 柱水平集中力 | 74 | 楼板上的矩形集中力 |  |  |

（2）柱定义
Mdl_ColSect ColSect_Def(int mat, int kind, string ShapeVal,string name="")
该方法用于定义柱，返回生成的柱定义。

| mat（整数类型） | 柱的材料类型，6为混凝土，5为钢，其余详盈建科软件内的设置。 |
|---|---|
| kind（整数类型） | 柱的截面类型，矩形为1，工字形为2，圆形为3，其余详盈建科软件内的设置。 |
| shapeval（字符串类型） | 柱截面类型参数构成的字符串，尺寸单位为mm。 |
| name（字符串类型） | 柱截面名称，型钢截面填入型钢规格即可布置，不需要填shapeval。 |

（3）梁定义
Mdl_BeamSect BeamSect_Def(int mat, int kind, string ShapeVal,string name="")
该方法用于定义梁，返回生成的梁定义。

| mat（整数类型） | 梁的材料类型，6为混凝土，5为钢，其余详盈建科软件内的设置。 |
|---|---|
| kind（整数类型） | 梁的截面类型，矩形为1，工字形为2，圆形为3，其余详盈建科软件内的设置。 |
| shapeval（字符串类型） | 梁截面类型参数构成的字符串，尺寸单位为mm。 |
| name（字符串类型） | 梁截面名称，型钢截面填入型钢规格即可布置，不需要填shapeval。 |

（4）墙定义
Mdl_WallSect WallSect_Def(int mat, int kind, int b,string name="")
该方法用于定义墙，返回生成的墙定义。

| mat（整数类型） | 墙的材料类型，6为混凝土，5为钢，其余详盈建科软件内的设置。 |
|---|---|
| kind（整数类型） | 墙的截面类型，矩形为1，其余详盈建科软件内的设置。 |
| b（整数类型） | 墙厚，单位为mm。 |
| name（字符串类型） | 墙截面名称。 |

（5）墙洞定义
Mdl_WallHoleDef WallHoleDef(int b,int h,string name="")
该方法用于定义墙洞，返回生成的墙洞定义。

| b（整数类型） | 墙洞的宽度，单位为mm。 |
|---|---|
| h（整数类型） | 墙洞的高度，单位为mm。 |
| name（字符串类型） | 墙洞截面名称。 |

（6）杆件定义
Mdl_BraceSect BraceSect_Def(int mat, int kind, string ShapeVal,string name="")

| mat（整数类型） | 杆件（斜杆）的材料类型，6为混凝土，5为钢，其余详盈建科软件内的设置。 |
|---|---|
| kind（整数类型） | 斜杆的截面类型，矩形为1，工字形为2，圆形为3，其余详盈建科软件内的设置。 |
| shapeval（字符串类型） | 斜杆截面类型参数构成的字符串，尺寸单位为mm。 |
| name（字符串类型） | 杆件截面名称，型钢截面填入型钢规格即可布置，不需要填shapeval。 |

（7）构件关联属性定义
Mdl_Property property_arrange(int id, string name, int type, string value)

| id（整数类型） | 构件的ID。 |
|---|---|
| name（字符串类型） | 属性名称（参考文档特殊构件定义说明）。 |
| type（整数类型） | 属性类型(3整型 4浮点 27数组)。 |
| value（字符串类型） | 属性值。 |

（8）加腋梁定义
Mdl_BeamJY BeamJYSect_Def(int kind, string ShapeVal,string name="")

| kind（整数类型） | 0为竖向加腋，1为水平加腋。 |
|---|---|
| ShapeVal（字符串类型） | 当kind为0时，参数分别为腋长L、腋高H1、腋高H2;当kind为1时，参数分别为左腋长LL、左腋宽LW1、左腋宽LW2、右腋长RL、右腋宽RW1、右腋宽RW2。 |
| name（字符串类型） | 加腋梁定义的名称。 |

（9）加腋板定义
Mdl_SlabJYDef SlabJYSect_Def(int kind, string para, string name="")

| kind（整数类型） | 0为双侧板腋，1为左板腋，2为右板腋。 |
|---|---|
| para（字符串类型） | 当kind为0时，参数分别为左腋长L1、左腋高H1、右腋长L2、右腋高H2;kind为1时，将右腋的参数部分置为0.00;kind为2时，将左腋的参数部分置为0.00。 |
| name（字符串类型） | 加腋板定义的名称。 |

（10）蒙皮荷载定义
Mdl_SkinLoadSect SkinLoadSect_Def(int kind,int style,float val,int dir)
该方法用于定义蒙皮荷载，返回生成的蒙皮荷载定义。

| kind（整数类型） | 工况类型 0恒 1活 2+x风 3-x风 4正y风 5-y风。 |
|---|---|
| style（整数类型） | 0 荷载值 1体形系数 |
| val（浮点数类型） | 荷载值 |
| dir（整数类型） | 0投影面方向 1法线方向 |

（11）自定义工况荷载定义
Mdl_LoadSect GKLoad_Def (GKLoadDefCreateInfo mdl_GKLoad)
该方法用于定义自定义工况荷载，返回生成的自定义工况荷载定义。

| GKLoadDefCreateInfo（自定义类型） | 荷载布置的构件类型，详见9.打包参数类型 。 |
|---|---|

（12）前处理计算参数设置
Mdl_ProjectPara ProjectPara_Set(int id, string ParaVal)
该方法用于设置前处理计算参数

| id（整型） | 前处理计算参数ID,详见前处理接口说明--计算参数ID对应表。 |
|---|---|
| ParaVal（字符串类型） | 前处理计算参数值,详见前处理接口说明--计算参数ID对应表。 |

（13）柱加固定义
public Mdl_ColJGSect ColJGSect_Def(ColJGCreateInfo createInfo)
该方法用于新增柱加固定义，返回生成的柱加固定义。

| createInfo（自定义类型） | 详见9.打包参数类型。 |
|---|---|

（14）梁加固定义
public Mdl_BeamJGSect BeamJGSect_Def(BeamJGCreateInfo createInfo)
该方法用于新增梁加固定义，返回生成的梁加固定义。

| createInfo（自定义类型） | 详见9.打包参数类型。 |
|---|---|

（15）钢结构加固定义
public Mdl_SteelJGSect SteelJGSect_Def(SteelJGCreateInfo createInfo)
该方法用于新增钢结构加固定义，返回生成的钢结构加固定义。

| createInfo（自定义类型） | 详见9.打包参数类型。 |
|---|---|

（16）楼梯定义
public Mdl_StairDef Stair_Def(StairDefCreateInfo stairDefInfo)该方法用于新增梁加固定义，返回生成的梁加固定义。

| StairDefCreateInfo（自定义类型） | 详见9.打包参数类型。 |
|---|---|

（17）柱帽定义
public Mdl_ColCapSect ColCapSect_Def(ColCapSectCreateInfo createInfo)该方法用于定义柱，返回生成的柱定义。

| createInfo（自定义类型） | 详见9.打包参数类型。 |
|---|---|

（18）填充墙定义
public Mdl_FillWallDef FillWall_Def(FillWallSectCreateInfo FillWallDefInfo)

| FillWallDefInfo（自定义类型） | 详见9.打包参数类型。 |
|---|---|

5.构件及荷载布置
（1）荷载布置
void load_arrange<T>(List<T> member_list, Mdl_LoadSect loadsect ,int type=1)
该方法用于布置荷载，返回空。

| member_list（泛型列表） | 待进行荷载布置的构件，目前可传入梁、柱、墙、杆件、节点类型。 |
|---|---|
| loadsect（荷载定义类型） | 已定义好的荷载类型，用于布置于构件上。 |
| type（恒活类型） | 默认为恒载，type为2表示活荷载，自定义工况的type为其kind值，柱X/Y向荷载类型的设置详见表5.1。 |

void load_arrange<T>(T member, Mdl_LoadSect loadsect ,int type=1)
该方法用于布置荷载，返回空。

| member（泛型） | 待进行荷载布置的构件，目前可传入梁、柱、墙、杆件、节点类型。 |
|---|---|
| loadsect（荷载定义类型） | 已定义好的荷载类型，用于布置于构件上。 |
| type（恒活类型） | 默认为恒载，type为2表示活荷载，自定义工况的type为其kind值，柱X/Y向荷载类型的设置详见表5.1。 |

表5.1

| 字段值 | 字段意义 | 字段值 | 字段意义 |
|---|---|---|---|
| 1 | 柱x向恒载 | 3 | 柱y向恒载 |
| 2 | 柱x向活载 | 4 | 柱y向活载 |

（1）楼板荷载布置
void load_arrange(Mdl_Slab slab, Mdl_Joint joint, Mdl_LoadSect loadsect, int x1,int y1,int x2,int y2,int type = 1)

| slab（楼板类型） | 待进行荷载布置的楼板。 |
|---|---|
| joint（节点类型） | 楼板左上角节点。 |
| loadsect（荷载定义类型） | 已定义好的荷载类型，用于布置于构件上。 |
| x1（整数型） | 起始点相对于joint 的X坐标。 |
| y1（整数型） | 起始点相对于joint 的Y坐标。 |
| x2（整数型） | 终止点相对于joint 的X坐标。 |
| y2（整数型） | 终止点相对于joint 的Y坐标。 |
| type(整数型) | 默认为恒载，type为2表示活荷载。 |

（1.1）自定义工况下楼板荷载布置
void load_arrange(Mdl_Slab slab, int gkLoadDefKind, string value)

| slab（楼板类型） | 待布置荷载的楼板。 |
|---|---|
| gkLoadDefKind（整数类型） | 自定义工况的kind。 |
| value（字符串类型） | 荷载值的字符串。 |

（2）柱布置
List<Mdl_ColSeg> column_arrange(List<List<Mdl_Joint>> nodelist, Mdl_ColSect ColSect,
int EccX=0, int EccY = 0, float Rotation=0, int HDiffB=0)
该方法用于布置柱，返回布置好的柱列表。

| nodelist（二维节点列表类型） | 待布置柱的节点列表。 |
|---|---|
| ColSect（柱截面类型） | 柱布置的截面类型。 |
| EccX（整数类型） | 柱的沿轴偏心。 |
| EccY（整数类型） | 柱的偏轴偏心。 |
| Rotation（浮点型） | 柱转角。 |
| HDiffB（整数类型） | 柱底标高。 |

Mdl_ColSeg column_arrange(Mdl_Joint node, Mdl_ColSect ColSect,
int EccX=0, int EccY = 0, float Rotation=0, int HDiffB=0)
该方法用于布置柱，返回布置好的柱。

| node（节点） | 待布置柱的节点。 |
|---|---|
| ColSect（柱截面类型） | 柱布置的截面类型。 |
| EccX（整数类型） | 柱的沿轴偏心。 |
| EccY（整数类型） | 柱的偏轴偏心。 |
| Rotation（浮点型） | 柱转角。 |
| HDiffB（整数类型） | 柱底标高。 |

List<Mdl_ColSeg> column_arrange(List<Mdl_Joint> nodelist, Mdl_ColSect ColSect,
int EccX=0, int EccY = 0, float Rotation=0, int HDiffB=0)
该方法用于布置柱，返回布置好的柱列表。

| nodelist（一维节点列表类型） | 待布置柱的节点列表。 |
|---|---|
| ColSect（柱截面类型） | 柱布置的截面类型。 |
| EccX（整数类型） | 柱的沿轴偏心。 |
| EccY（整数类型） | 柱的偏轴偏心。 |
| Rotation（浮点型） | 柱转角。 |
| HDiffB（整数类型） | 柱底标高。 |

（3）梁布置
Mdl_BeamSeg beam_arrange(Mdl_Grid grid, Mdl_BeamSect BeamSect,
int Ecc=0, int HDiff1=0, int HDiff2 = 0, float Rotation=0)
该方法用于布置梁，返回布置好的梁。

| grid（网格） | 待布置梁的网格。 |
|---|---|
| BeamSect（梁截面类型） | 梁布置的截面类型。 |
| Ecc（整数类型） | 梁偏轴距离。 |
| HDiff1（整数类型） | 梁顶标高1。 |
| HDiff2（整数类型） | 梁顶标高2。 |
| Rotation（浮点型） | 梁的转角。 |

List<Mdl_BeamSeg> beam_arrange(Mdl_Grid grid, Mdl_BeamSect BeamSect,
int Ecc=0, int HDiff1=0, int HDiff2 = 0, float Rotation=0)
该方法用于布置梁，返回布置好的梁列表。

| gridlist（一维网格列表类型） | 待布置梁的网格列表。 |
|---|---|
| BeamSect（梁截面类型） | 梁布置的截面类型。 |
| Ecc（整数类型） | 梁偏轴距离。 |
| HDiff1（整数类型） | 梁顶标高1。 |
| HDiff2（整数类型） | 梁顶标高2。 |
| Rotation（浮点型） | 梁的转角。 |

（4）墙布置
Mdl_WallSeg wall_arrange(Mdl_Grid grid, Mdl_WallSect WallSect, int Ecc=0, int HDiff1=0, int HDiff2=0, int HDiffB=0, int sloping=0,
int EccDown=0, int offset1=0, int offset2=0)
该方法用于布置墙，返回布置好的墙。

| grid（网格） | 待布置墙的网格。 |
|---|---|
| WallSect（梁截面类型） | 墙布置的截面类型。 |
| Ecc（整数类型） | 墙的偏轴距离。 |
| HDiff1（整数类型） | 墙顶高1。 |
| HDiff2（整数类型） | 墙顶高2。 |
| HDiffB（整数类型） | 墙底高。 |
| sloping（整数类型） | 是否为斜墙。 |
| EccDown（整数类型） | 下端偏轴距离。 |
| offset1（整数类型） | 下起点外扩距离。 |
| offset2（整数类型） | 下终点外扩距离。 |

List<Mdl_WallSeg> wall_arrange(List<Mdl_Grid> gridlist, Mdl_WallSect WallSect, int Ecc=0, int HDiff1=0, int HDiff2=0, int HDiffB=0, int sloping=0,
int EccDown=0, int offset1=0, int offset2=0)
该方法用于布置墙，返回布置好的墙列表。

| gridlist（一维网格列表类型） | 待布置墙的网格列表。 |
|---|---|
| WallSect（梁截面类型） | 墙布置的截面类型。 |
| Ecc（整数类型） | 墙的偏轴距离。 |
| HDiff1（整数类型） | 墙顶高1。 |
| HDiff2（整数类型） | 墙顶高2。 |
| HDiffB（整数类型） | 墙底高。 |
| sloping（整数类型） | 是否为斜墙。 |
| EccDown（整数类型） | 下端偏轴距离。 |
| offset1（整数类型） | 下起点外扩距离。 |
| offset2（整数类型） | 下终点外扩距离。 |

（5）杆件布置
Mdl_BraceSeg brace_arrange(Mdl_Joint node1, Mdl_Joint node2, Mdl_BraceSect BraceSect,
int EccX1=0, int EccY1=0, int HDiff1=1, int EccX2=0,
int EccY2=0, int HDiff2=1, float Rotation=0)
该方法用于布置杆件，返回布置好的杆件。

| node（节点类型） | 杆件的起始端。 |
|---|---|
| node（节点类型） | 杆件的终止端。 |
| BraceSect（杆件截面类型） | 杆件布置的截面类型。 |
| EccX1（整数类型） | 斜杆1端的沿轴偏心。 |
| EccY1（整数类型） | 斜杆1端的偏轴偏心。 |
| HDiff1（整数类型） | 斜杆1端的底标高（为1时表示与层同高）。 |
| EccX2（整数类型） | 斜杆2端的沿轴偏心。 |
| EccY2（整数类型） | 斜杆2端的偏轴偏心。 |
| HDiff2（整数类型） | 斜杆2端的底标高（为1时表示与层同高）。 |
| Rotation（浮点型） | 斜杆2端的转角。 |

Mdl_BraceSeg brace_arrange(List<List<Mdl_Joint>> nodelist, Mdl_BraceSect BraceSect,
int EccX1=0, int EccY1=0, int HDiff1=1, int EccX2=0,
int EccY2=0, int HDiff2=1, float Rotation=0)
该方法用于布置杆件，返回布置好的杆件列表。

| nodelist（二维节点列表类型） | 待布置杆件的节点列表，其中每一个List<Mdl_Joint>包含两个节点，分别为杆件的起始端和终止端。 |
|---|---|
| BraceSect（杆件截面类型） | 杆件布置的截面类型。 |
| EccX1（整数类型） | 斜杆1端的沿轴偏心。 |
| EccY1（整数类型） | 斜杆1端的偏轴偏心。 |
| HDiff1（整数类型） | 斜杆1端的底标高（为1时表示与层同高）。 |
| EccX2（整数类型） | 斜杆2端的沿轴偏心。 |
| EccY2（整数类型） | 斜杆2端的偏轴偏心。 |
| HDiff2（整数类型） | 斜杆2端的底标高（为1时表示与层同高）。 |
| Rotation（浮点型） | 斜杆2端的转角。 |

（6）楼板布置
Mdl_Slab slab_arrange(int Xc,int Yc,int Thick, Mdl_StdFlr bzc,bool ishole,int cc=0)
该方法用于布置楼板，可以选择将楼板设置成开洞，返回空。

| Xc（整数型） | 楼板的X向形心坐标，单位为mm。 |
|---|---|
| Yc（整数型） | 楼板的Y向形心坐标，单位为mm。 |
| Thick（整数型） | 楼板的厚度，单位为mm |
| bzc（标准层类型） | 楼板所在的标准层。 |
| ishole（布尔型） | 是否将楼板设置成开洞。 |
| cc（整数型） | 楼板的错层，单位为mm，以下为正。 |

（7）构件关联属性
Mdl_Property property_arrange(int id, string name, int type, string value)
该方法用于添加特殊构件

| id（整数型） | 构件的ID。 |
|---|---|
| name（字符串类型） | 特殊构件的名称。 |
| type（整数型） | Value的类型（3为整型/4、5为浮点型/8为字符串型/27为数组型） |
| value（字符串类型） | 参数。 |

（8）添加分组
void add_group(string Name, List<int> nID, List<int> idNewZRC)
该方法用于添加分组

| Name（字符串型） | 组名。 |
|---|---|
| nID（数组型） | 组内的构件ID。 |
| idNewZRC（数组型） | 组内构件ID对应的自然层ID。 |

（9）加腋梁布置
public void beamjy_arrange(Mdl_BeamJY beamjydef, Mdl_BeamSeg beam,bool end1=true,bool end2=true)
该方法用于添加加腋梁

| beamjydef（自定义Mdl_BeamJY类型） | 加腋梁的截面类型。 |
|---|---|
| beam（自定义Mdl_BeamSeg类型） | 待加腋的梁对象。 |
| end1（布尔值） | 1端是否加腋，默认为true。 |
| end2（布尔值） | 2端是否加腋，默认为true。 |

（10）加腋板布置
void slabjy_arrange(Mdl_SlabJYDef slabjydef, Mdl_Grid grid)
该方法用于添加加腋板。

| slabjydef（自定义Mdl_SlabJYDef类型） | 加腋板的截面类型。 |
|---|---|
| grid（自定义Mdl_Grid类型） | 待加腋的板周边网格。 |

（11）楼板布置（用于替代（6）的楼板布置方式）
Mdl_Slab slab_arrange(SlabCreateInfo slabInfo)

| slabInfo（自定义类型，详见9.打包参数类型） | 楼板创建信息。 |
|---|---|

（12）蒙皮布置
Mdl_SkinSeg skin_arrange(SkinCreateInfo skinInfo)

| skinInfo（自定义类型） | 蒙皮创建信息。 |
|---|---|

（13）蒙皮荷载布置
void skinLoad_arrange(Mdl_SkinSeg skinseg, Mdl_SkinLoadSect loadsect)

| skinseg（自定义类型） | 蒙皮。 |
|---|---|
| Loadsect（自定义类型） | 蒙皮荷载定义。 |

（14）加固梁布置
public Mdl_JGSeg beamjg_arrange(Mdl_BeamSeg beam, Mdl_BeamJGSect beamJGSect)

| beam（自定义类型） | 梁。 |
|---|---|
| BeamJGSect（自定义类型） | 梁加固定义。 |

（15）加固梁布置
public Mdl_JGSeg columnjg_arrange(Mdl_ColSeg col, Mdl_ColJGSect colJGSect)

| col（自定义类型） | 柱。 |
|---|---|
| colJGSect（自定义类型） | 柱加固定义。 |

（16）钢结构加固梁布置
public Mdl_JGSeg steeljg_arrange(Mdl_BeamSeg beam, Mdl_SteelJGSect steelJGSect)

| beam（自定义类型） | 钢梁。 |
|---|---|
| SteelJGSect（自定义类型） | 钢结构加固定义。 |

public Mdl_JGSeg steeljg_arrange(Mdl_ColSeg col, Mdl_SteelJGSect steelJGSect)

| col（自定义类型） | 钢柱。 |
|---|---|
| steelJGSect（自定义类型，详见9.打包参数类型） | 钢结构加固定义。 |

（17）层间板布置
public Mdl_MidSlab midslab_arrange(MidSlabCreateInfo midSlabInfo)

| midSlabInfo（自定义类型） | 层间板创建信息。 |
|---|---|

（18）楼梯布置
public Mdl_StairSeg stair_arrange(Mdl_Slab slab,Mdl_StairDef stairdef,int start_node =1,int antiClockwise=1)

| slab（自定义类型） | 楼板。 |
|---|---|
| stairdef（自定义类型） | 楼梯定义。 |
| start_node（整型） | 起始顶点在房间多边形上的序号，从1开始。 |
| antiClockwise（整型） | 楼梯方向是顺时针(0)还是逆时针(1)。 |

（19）柱帽布置
public void colCap_arrange(Mdl_ColSeg col, Mdl_ColCapSect colCapSect);

| col（自定义类型） | 柱。 |
|---|---|
| colCapSect（自定义类型） | 柱帽截面。 |

（20）消能器布置
public Mdl_XNQSeg XNQ_arrange(int StdFlrID, int SectID,int idNode1,int idNode2,int idGrid,int nd1,int nd2,int nTop,int nBottom)

| StdFlrID（整型） | 标准层ID。 |
|---|---|
| SectID（整型） | 消能器截面ID。 |
| idNode1（整型） | 网格的第一个节点ID。 |
| idNode2（整型） | 网格的第二个节点ID。 |
| idGrid（整型） | 网格id。 |
| nd1（整型） | 始端偏移距离。 |
| nd2（整型） | 终端偏移距离。 |
| ntop（整型） | 顶部偏移距离。 |
| nbottom（整型） | 底部偏移距离。 |

（21）填充墙布置
public Mdl_FillWall FillWall_arrange(FillWallSegCreateInfo fillwall)

| fillwall（自定义类型） | 详见9.打包参数类型。 |
|---|---|

6.获取内部变量函数
public ref Hi_DbModelData GetDbModelData()
该方法获取类内模型数据，返回模型数据的引用。
public ref List<Mdl_StdFlr> GetStdFlrList()
该方法返回标准层列表，返回标准层列表的引用。
public ref List<Mdl_ProjectPara> GetProjectParaList()
该方法获取工程参数的列表，返回工程参数列表的引用。
public ref List<Mdl_LoadSeg> GetLoadSegList()
该方法获取荷载列表，返回荷载列表的引用。
public ref List<Mdl_LoadSect> GetLoadSectList()
该方法获取荷载定义的列表，返回荷载定义列表的引用。
public ref List<Mdl_BraceSeg> GetBraceSegList()
该方法获取杆件列表，返回杆件列表的引用。
public ref List<Mdl_BraceSect> GetBraceSectList()
该方法获取杆件定义的列表，返回杆件定义列表的引用。
public ref List<Mdl_ColSeg> GetColSegList()
该方法获取柱列表，返回柱列表的引用。
public ref List<Mdl_ColSect> GetColSectList()
该方法获取柱定义的列表，返回柱定义列表的引用。
public ref List<Mdl_Property> GetPropertyList ()
该方法获取特殊构件列表，返回特殊构件列表的引用。
public ref List<Mdl_BeamSeg> GetBeamSegList()
该方法获取梁列表，返回梁列表的引用。
public ref List<Mdl_BeamSect> GetBeamSectList()
该方法获取梁定义的列表，返回梁定义列表的引用。
public ref List<Mdl_WallHole> GetWallHoleList()
该方法获取墙洞列表，返回墙洞列表的引用。
public ref List<Mdl_WallHoleDef> GetWallHoleDefList()
该方法获取墙洞定义的列表，返回墙洞定义列表的引用。
public ref List<Mdl_WallSeg> GetWallSegList()
该方法获取墙列表，返回墙列表的引用。
public ref List<Mdl_WallSect> GetWallSectList()
该方法获取墙定义的列表，返回墙定义列表的引用。
public ref List<Mdl_Joint> GetJointList()
该方法获取节点列表，返回节点列表的引用。
public ref List<Mdl_Grid> GetGridList()
该方法获取网格列表，返回网格列表的引用。
public ref List<Mdl_Axis> GetAxisList()
该方法获取轴线列表，返回轴线列表的引用。
public ref List<Mdl_Floor> GetFloorList()
该方法获取楼层列表，返回楼层列表的引用。
public ref int GetID()
该方法获取当前已用ID的最大值，返回ID的引用。
public ref int GetStdFlrNo()
该方法获取当前标准层编号的最大值，返回引用类型。
public ref int GetProjectParaNo()
该方法获取当前工程参数编号的最大值，返回引用类型。
public ref int GetLoadSegNo()
该方法获取当前荷载编号的最大值，返回引用类型。
public ref int GetLoadSectNo()
该方法获取当前荷载定义编号的最大值，返回引用类型。
public ref int GetBraceSegNo()
该方法获取当前杆件编号的最大值，返回引用类型。
public ref int GetBraceSectNo()
该方法获取当前杆件定义编号的最大值，返回引用类型。
public ref int GetColSegNo()
该方法获取当前柱编号的最大值，返回引用类型。
public ref int GetColSectNo()
该方法获取当前柱定义编号的最大值，返回引用类型。
public ref int GetSlabNo()
该方法获取当前楼板编号的最大值，返回引用类型。
public ref int GetBeamSegNo()
该方法获取当前梁编号的最大值，返回引用类型。
public ref int GetBeamSectNo()
该方法获取当前梁定义编号的最大值，返回引用类型。
public ref int GetWallHoleNo()
该方法获取当前墙洞编号的最大值，返回引用类型。
public ref int GetWallHoleDefNo()
该方法获取当前墙洞定义编号的最大值，返回引用类型。
public ref int GetWallSegNo()
该方法获取当前墙编号的最大值，返回引用类型。
public ref int GetWallSectNo()
该方法获取当前墙定义编号的最大值，返回引用类型。
public ref int GetJointNo()
该方法获取当前节点编号的最大值，返回引用类型。
public ref int GetGridNo()
该方法获取当前网格编号的最大值，返回引用类型。
public ref int GetAxisNo()
该方法获取当前轴线编号的最大值，返回引用类型。
public ref int GetFloorNo()
该方法获取当前楼层编号的最大值，返回引用类型。
int GetGjId(int kind, int flr,int No)

| kind（整数型） | 构件类型，详表4.1。 |
|---|---|
| flr（整数型） | 楼层号。 |
| No（整数型） | 标准层内的建模序号。 |

该方法获取当前dataFunc对象种已使用的最大ID
ProperList GetGroupObjList(Mdl_Group group)

| group（Mdl_Group） | Group类型的对象。 |
|---|---|

该方法返回group中各类构件的对象。
7.与YJK联动
（1）从用户传输到YJK（CsToYjk.dll中的方法）
bool IPC_ToYJK()
该方法用于将用户生成的模型传输到yjk
（2）从YJK传输到用户（CsToYjk.dll中的方法）
bool IPC_YJKToUs()
该方法用于将YJK当前的模型传输到用户（目前只支持分组数据和板数据）
（3）在依赖YJK环境下的模型局部更新
bool ReflecToYJK()
（4）依赖YJK环境下重新生成模型
bool RefreshToYJK()
（5）数据跨进程传输的模板函数
Link2YJK.LinkPrepare<T>(T model);
将数据准备传输到YJK进程。

| model（模板类型参数） | 可以是任意的参数类型。 |
|---|---|

Link2YJK.GetIPCdata<T>();
获取之前准备的数据。

| model（模板类型） | 之前传输的数据类型。 |
|---|---|

8.其它功能函数
（1）节点排序合并
merge_nodelist(List<List<Mdl_Joint>> nodelist1, List<List<Mdl_Joint>> nodelist2)
该方法用于将两个节点列表进行排序，首先按照两个节点列表中节点的X坐标从小到大进行排序，当节点的X坐标相同时按照节点的Y坐标从小到大进行排序，输出合并后的二维节点列表。

| nodelist1（二维节点列表类型） | 待合并的二维节点列表nodelist1。 |
|---|---|
| nodelist2（二维节点列表类型） | 待合并的二维节点列表nodelist2。 |

（2）简单杆件布置
void simple_truss(List<int> xspans,List<int> yspans,int Z, Mdl_StdFlr kjc, Mdl_BraceSect defbrace, int direct_x,int direct_y,int value_z=0)
该方法用于生成X、Y、Z三个方向任意组合的杆件布置，返回为空。

| xspans（整数型一维列表） | X向开间，单位为mm。 |
|---|---|
| yspans（整数型一维列表） | Y向开间，单位为mm。 |
| Z（整数型） | 表示上节点高度，单位为mm。 |
| kjc（自定义空间层类型） | 提前定义好的空间层。 |
| defbrace（自定义杆件截面类型） | 杆件布置的截面类型。 |
| direct_x（整数型） | 取1表示在X向布置杆件，取0表示X向不布置杆件。 |
| direct_y（整数型） | 取1表示在Y向布置杆件，取0表示Y向不布置杆件。 |
| value_z（整数型） | Z向的杆件长度，单位为mm。 |

（3）建模数据提交
void DbModel_Assign()
该方法用于提交设置好的建模数据，参数为空，返回为空，仅需在代码最后执行一次即可。
（4）设置建模数据
void SetModel(Hi_DbModelData mdl)

| mdl（建模数据类型） | 建模数据类型的对象。 |
|---|---|

（5）生成ydb（CsToYjk.dll中的方法）
bool CreateYDB(string path,string name)

| Path（字符串类型） | 生成ydb的路径。 |
|---|---|
| Name（字符串类型） | ydb的名称。 |

（6）获取选择集内的构件ID的接口（位于Hi_AddToAndReadYjk类中）
Dictionary<int,List<int>> GetSelectSetIDs()
（7）获取选择集内的构件ID及其所在自然层的接口（位于Hi_AddToAndReadYjk类中）
Dictionary<int, List<Tuple<int, int>>> GetSelectSetIDsWithZrc()

| Result.key（返回字典的key） | 构件类别。 |
|---|---|
| Result.value（返回字典的value） | 选择集中当前类别的所有构件，Tuple的first为构件ID，second为其所在的自然层。 |

9.打包参数类型
（1）Property
该类用于生成默认的特殊构件参数，可按照索引进行成员的修改，并生成字符串参数

| public Property(string type) | 该类的构造函数。 |
|---|---|
| public float getVal(int index) | 获取某一索引的参数。 |
| public void setVal(int index, int val) | 设置某一索引的参数。 |
| public string GetValString() | 获取字符串类型的标准层参数。 |

（2）SlabCreateInfo
该类用于设置楼板的相关参数

| public SlabCreateInfo (void) | 该类的构造函数。 |
|---|---|
| Public SlabCreateInfo SetCentroid (int index) | 设置楼板的形心。 |
| public SlabCreateInfo SetThick (int thick) | 设置楼板的厚度。 |
| public SlabCreateInfo SetStdFlr (Mdl_StdFlr bzc) | 设置标准层。 |
| public SlabCreateInfo SetCc(int cc) | 设置错层。 |
| public SlabCreateInfo SetDeadLive(float dead,float live) | 设置楼板恒活。 |
| public Mdl_Slab GetSlab() | 获取楼板对象。 |

（3）GKLoadDefCreateInfo
该类用于设置自定义工况的相关参数

| public GKLoadDefCreateInfo (void) | 该类的构造函数。 |
|---|---|
| Public GKLoadDefCreateInfo SetDeadFacotr (float dDead) | 设置重力荷载代表值系数。 |
| public GKLoadDefCreateInfo SetLiveFacotr (int nLive, float dLive1, float dLive2, float dLive3) | nLive: 0恒载,1活载,2消防车, 3 +x风,4 -x风,5 +y风 ,6 -y风,7 x地震 ,8 y地震, 9人防 , 10地震; fLive1活荷载折减值 0(不考虑) 1(自动考虑) （0~1自己输入）;fLive2主梁活荷载折减值 0(不考虑) 1(自动考虑) （0~1自己输入）;fLive3次梁活荷载折减值 0(不考虑) 1(自动考虑) （0~1自己输入） |
| public GKLoadDefCreateInfo SetName (string strName) | 设置自定义工况名称。 |
| public GKLoadDefCreateInfo SetData (string Data) | 设置相关系数。 |
| public Mdl_GKLoadDef GetGKLoad () | 获取自定义工况荷载定义。 |

（4）ProjectPara
该类用于处理读取的Mdl_ProjectPara列表，可按照索引进行成员的访问及修改

| public ProjectPara(List<Mdl_ProjectPara> paraList) | 该类的构造函数。 |
|---|---|
| public Mdl_ProjectPara findParaById(int id) | 获取某一ID的Mdl_ProjectPara成员。 |

（5）SkinCreateInfo
该类用于设置蒙皮的相关参数

| public SkinCreateInfo (void) | 该类的构造函数。 |
|---|---|
| Public SlabCreateInfo SetDeadLive (float dead,float live) | 设置蒙皮的恒活。 |
| public SlabCreateInfo SetTotalStress (float totalStress) | 设置蒙皮的总压力。 |
| public SlabCreateInfo SetMaterialStyle (int mat) | 设置蒙皮的材料类型（ -1没有布置，0混凝土强度等级 1钢 2自定义材料）。 |
| public SlabCreateInfo SetConcreteLevel (int concreteLevel) | 设置蒙皮的混凝土强度等级。 |
| public SlabCreateInfo SetCustomMaterialID (Vector dir) | 设置蒙皮的自定义材料ID。 |
| public SlabCreateInfo SetNDirection (string nDirection) | [图] 按照+X、+Y、+Z、-X、-Y、-Z、角度的顺序组成的字符串。 |
| public SkinCreateInfo SetSurroundPt(List<Mdl_Joint> joints) | 按照顺时针或者逆时针输入节点列表。 |
| public SkinCreateInfo SetThick(int thick) | 设置蒙皮厚度。 |
| Mdl_SkinSeg GetSkinSeg() | 获取蒙皮对象。 |

（6）ColJGCreateInfo_MagnifySect
该类用于设置柱加固（增大截面法）的相关参数

| public ColJGCreateInfo_MagnifySect() | 该类的构造函数。 |
|---|---|
| Public ColJGCreateInfo_MagnifySect SetPara (int b_l,int b_r, int h_t,int h_b,int hnt) | 设置参数。 b_l: b左向增加值 b_r: b右向增加值 h_t: h向顶部增加总值 h_b: h向顶部增加总值 hnt: 新增截面的混凝土强度等级 |
| public Mdl_ColJGSect GetColJG() | 获取柱加固定义。 |

（6）ColJGCreateInfo_Convert
该类用于设置柱加固（置换混凝土法）的相关参数

| public ColJGCreateInfo_Convert () | 该类的构造函数。 |
|---|---|
| public ColJGCreateInfo_Convert SetPara (int b, int h, int hnt) | 设置参数。 b: b方向砼置换深度 h: h方向砼置换深度 hnt: 新置换砼强度等级 |
| public Mdl_ColJGSect GetColJG() | 获取柱加固定义。 |

（7）ColJGCreateInfo_WrapSteel
该类用于设置柱加固（外包钢法）的相关参数

| public ColJGCreateInfo_WrapSteel () | 该类的构造函数。 |
|---|---|
| public ColJGCreateInfo_WrapSteel SetPara (int gangh,int b, float h, int s, int pos,string secSteelName) | 设置参数。 Gangh:钢号(0为Q235，1为Q345) b: b方向砼置换深度 h: h方向砼置换深度 hnt: 新置换砼强度等级 |
| public Mdl_ColJGSect GetColJG() | 获取柱加固定义。 |

（8）ColJGCreateInfo_StickPlate
该类用于设置柱加固（外粘钢板）的相关参数

| public ColJGCreateInfo_ StickPlate () | 该类的构造函数。 |
|---|---|
| public ColJGCreateInfo_StickPlate SetPara (int gangh, int b, int h, float t) | 设置参数。 Gangh:钢号(0为Q235，1为Q345) b: b方向钢板宽度 h: h方向钢板宽度 t: 钢板厚度 |
| public Mdl_ColJGSect GetColJG() | 获取柱加固定义。 |

（8）ColJGCreateInfo_StickFibre
该类用于设置柱加固（外贴纤维复合材料法）的相关参数

| public ColJGCreateInfo_StickFibre () | 该类的构造函数。 |
|---|---|
| public ColJGCreateInfo_StickFibre SetPara (int _k, int kk, int bw, int hw, int cw, int cs, int n,float t) | 设置参数。 _k: 复合材类型 0:单向织物I级 1:单向织物II级 2:条形I级 3:条形II级 4:S玻璃纤维 5:E玻璃纤维 kk: 重要性 1：一般构件 0：重要构件 bw: b方向宽度 hw: h方向宽度 cw: 环形箍宽度 cs: 环形箍中心间距 n: 复合材层数 t: 复合材每层的厚度 |
| public Mdl_ColJGSect GetColJG() | 获取柱加固定义。 |

（9）BeamJGCreateInfo_MagnifySect
该类用于设置梁加固（增大截面法）的相关参数

| public BeamJGCreateInfo_MagnifySect() | 该类的构造函数。 |
|---|---|
| Public BeamJGCreateInfo_MagnifySect SetPara (int b, int hb, int ht, int hnt) | 设置参数。 b: b向增加值 hb: h向底部增加值 ht: h向顶部增加值 hnt: 新增截面的混凝土强度等级 |
| public Mdl_BeamJGSect GetBeamJG() | 获取梁加固定义。 |

（10）BeamJGCreateInfo_Convert
该类用于设置梁加固（置换混凝土法）的相关参数

| public BeamJGCreateInfo_Convert () | 该类的构造函数。 |
|---|---|
| public BeamJGCreateInfo_Convert SetPara(int hb, int ht, int hnt) | 设置参数。 hb: h方向砼底部置换深度 ht: h方向砼顶部置换深度 hnt: 新增截面的混凝土强度等级 |
| public Mdl_BeamJGSect GetBeamJG() | 获取梁加固定义。 |

（11）BeamJGCreateInfo_WrapSteel
该类用于设置梁加固（外包钢加固法）的相关参数

| public BeamJGCreateInfo_WrapSteel () | 该类的构造函数。 |
|---|---|
| public BeamJGCreateInfo_WrapSteel SetPara (int cw, float ct, int cs,int gangh,string SecSteelName_b, string SecSteelName_t,int bw,int bt) | 设置参数。 cw: 梁侧粘贴篐板宽度 ct: 梁侧粘贴篐板厚度 cs: 梁侧粘贴箍板间距mm gangh: 钢号			1:hpb235 2:HRB335 3:HRB400 4:RRB400 SecSteelName_b: 梁底两角粘贴角钢型名称 SecSteelName_t: 梁顶两角粘贴角钢型名称 |
| public Mdl_BeamJGSect GetBeamJG() | 获取梁加固定义。 |

（12）BeamJGCreateInfo_StickPlate
该类用于设置梁加固（外粘钢板法）的相关参数

| public BeamJGCreateInfo_StickPlate () | 该类的构造函数。 |
|---|---|
| public BeamJGCreateInfo_StickPlate SetPara (int bw, float bt, int tw, float tt, int cw, float ct, int cs, int gangh) | 设置参数。 bw: 梁底粘贴钢板面积宽度 bt: 梁底粘贴钢板面积厚度 tw: 梁顶粘贴钢板面积宽度 tt: 梁顶粘贴钢板面积厚度 cw: 梁侧箍板宽度 ct: 梁侧箍板厚度 cs: 梁侧箍板间距 gangh: 钢材类型 0:q235 1:q345 |
| public Mdl_BeamJGSect GetBeamJG() | 获取梁加固定义。 |

（12）BeamJGCreateInfo_StickPlate
该类用于设置梁加固（外粘钢板法）的相关参数

| public BeamJGCreateInfo_StickFibre () | 该类的构造函数。 |
|---|---|
| public BeamJGCreateInfo_StickFibre SetPara (int _k, int kk, int bn, int bw, int tn, int tw, int cn, int cs, int cw, float t) | 设置参数。 _k: 复合材类型 0:单向织物I级 1:单向织物II级 2:条形I级 3:条形II级 4:S玻璃纤维 5:E玻璃纤维 kk: 重要性 1：一般构件 0：重要构件 bn: 梁底粘贴复合材的层数 bw: 梁底粘贴复合材的宽度 tn: 梁顶粘贴复合材的层数 tw: 梁顶粘贴复合材的宽度 cn: 梁侧粘贴复合材的层数 cs: 梁侧粘贴复合材间距 cw: 梁侧粘贴复合材宽度(bf) t: 复合材的每层厚度 |
| public Mdl_BeamJGSect GetBeamJG() | 获取梁加固定义。 |

（13）BeamJGCreateInfo_ReinForceSteelStrand
该类用于设置梁加固（钢纹线加固法）的相关参数

| Public BeamJGCreateInfo_ReinForceSteelStrand () | 该类的构造函数。 |
|---|---|
| public BeamJGCreateInfo_ReinForceSteelStrand  SetPara(float r, int cs, int Hrl, int Srw, int Szj) | 设置参数。 r: 钢绞线直径mm cs: 钢绞线层数 Hrl: 梁侧面围套高度 Srw: 钢绞线箍筋间距 Szj: 钢绞线纵筋间距 |
| public Mdl_BeamJGSect GetBeamJG() | 获取梁加固定义。 |

（14）BeamJGCreateInfo_StickPlateAndMagnifySect
该类用于设置梁加固（外粘钢板法+底部増大截面法）的相关参数

| Public BeamJGCreateInfo_ReinForceSteelStrand () | 该类的构造函数。 |
|---|---|
| public BeamJGCreateInfo_StickPlateAndMagnifySect SetPara(int tw, float tt, int gangh, int b, int hb, int hnt) | 设置参数。 tw: 梁顶粘贴钢板面积宽度 tt: 梁顶粘贴钢板面积厚度 gangh: 钢材类型 0:q235 1:q345 b: b向增加值 hb: h向底部增加值 hnt:新增截面的混凝土强度等级 |
| public Mdl_BeamJGSect GetBeamJG() | 获取梁加固定义。 |

（15）SteelJGCreateInfo
该类用于设置钢结构加固定义的相关参数

| public SteelJGCreateInfo() | 该类的构造函数。 |
|---|---|
| public SteelJGCreateInfo SetKind(int k) | 设置类型 |
| public SteelJGCreateInfo SetName(string name) | 设置做法名称 |
| public SteelJGCreateInfo SetWeldLen(double HDCD) | 设置焊段长度。 |
| public SteelJGCreateInfo SetFilletWeldSize (double HJCC) | 设置焊脚尺寸。 |
| public SteelJGCreateInfo SetWeldInterVal (double HDJG) | 设置焊段间隔。 |
| public SteelJGCreateInfo SetWeldMethod (double SHFS) | 设置加固施焊方法。 （0为间断焊，1为连续焊） |
| public SteelJGCreateInfo SetSteelLevel(int SteelLevel) | 设置加固部分钢号。 （带GJ后缀为原钢号值+1，带N后缀为原钢号值+2，带GJ后缀为原钢号值+3） |
| public SteelJGCreateInfo SetDim(int Dmid) | 设置加强板定位距离。 |
| public SteelJGCreateInfo isXY(int IsXY) | 是否为双侧加固。 （0：单侧，1：双侧） |
| public SteelJGCreateInfo SetSectionSteelName(string SectionSteelName) | 设置型钢截面的名称。 |
| public SteelJGCreateInfo SetSteelJGSect (double B1,double B2,double T1,double T2) | 设置钢结构加固截面尺寸。 （B1:加强板B1、B2:加强板B2、T1:加强板T1、T2:加强板T2） |
| public SteelJGCreateInfo SetTSecK(int TSecK) | 设置T型钢截面类型。 （0:焊接T型钢截面、1:国标部分T型钢） |
| public SteelJGCreateInfo SetIsInter(int IsInter) | 设置上翼缘加强板。 （0:外侧、1:内侧） |
| public Mdl_SteelJGSect GetSteelJG() | 获取梁加固定义。 |

（16）MidSlabCreateInfo
该类用于设置层间板的相关参数

| public SlabCreateInfo (void) | 该类的构造函数。 |
|---|---|
| Public MidSlabCreateInfo SetCentroid (int index) | 设置楼板的形心。 |
| public MidSlabCreateInfo SetThick (int thick) | 设置楼板的厚度。 |
| public MidSlabCreateInfo SetStdFlr (Mdl_StdFlr bzc) | 设置标准层。 |
| public MidSlabCreateInfo SetCc(int cc) | 设置错层。 |
| public MidSlabCreateInfo SetDeadLive(float dead,float live) | 设置楼板恒活。 |
| public MidSlabCreateInfo SetSurroundNodes(List<Mdl_Joint> nodes, int relativeH) | 设置层间板的围区的节点坐标（按照逆时针方向） relativeH=-标准层高度-层间板平面下降高度（不计错层） |
| public MidSlabCreateInfo SetSurroundGrids(List<Mdl_Grid> grids) | 设置层间板围区的网格（顺序不做要求）。 |
| public MidSlabCreateInfo GetSlab() | 获取层间板对象。 |

（17）StairDefCreateInfo
该类用于设置楼梯的相关参数

| public StairDefCreateInfo (void) | 该类的构造函数。 |
|---|---|
| public StairDefCreateInfo SetKind(int kind) | 设置楼梯类型。 楼梯类型：单跑楼梯（10）、双跑楼梯（20）、双分中起楼梯（21）、交叉楼梯（22）、剪刀楼梯（23）、双分边起楼梯（24）、三跑楼梯（30）、四跑楼梯（40） |
| public StairDefCreateInfo SetStartPos(int dis) | 设置起点位置（和房间起始边距离） |
| public StairDefCreateInfo SetEndPos(int dis) | 设置终点位置（和房间终止边距离） |
| public StairDefCreateInfo SetLevel(int H) | 设置第一跑相对地面的高度。 |
| public StairDefCreateInfo IsPrefabricated(int flag) | 设置是否为预制楼梯。 （1为预制楼梯，0为非预制楼梯） |
| public StairDefCreateInfo SetStepW(int width) | 设置踏步宽。 |
| public StairDefCreateInfo SetCrossStair(int H1,int W1,int H2,int W2) | 设置交叉楼梯的参数 H1:梁式交叉楼梯斜梁截面高度。 W1:梁式交叉楼梯斜梁截面宽度。 H2:梁式交叉楼梯水平梁截面高度。 W2:梁式交叉楼梯水平梁截面宽度。 |
| public StairDefCreateInfo SetAllLevel(int allLevel) | 设置楼梯整体抬升值。 |
| public StairDefCreateInfo IsGenPtFarBeam(int flag) | 是否生成休息平台远端梯梁。 （1为生成，0为不生成） |
| public StairDefCreateInfo IsGenColumn(int flag) | 是否生成梯柱。 （1为生成，0为不生成） |
| public StairDefCreateInfo SetTZSect(int W,int H) | 设置梯柱截面尺寸。 （w为梯柱截面宽，H为梯柱截面高） |
| public StairDefCreateInfo Set1stPlatForm(int platFormH,int platFormW,int slabThick,int TbeamPos,int platBeamW,int platBeamH) | 设置休息平台1的相关参数。 platFormH:平台高，platFormW:平台宽，slabThick:平台板厚，TbeamPos:梯梁位置，platBeamW:平台梁宽，platBeamH:平台梁高 |
| public StairDefCreateInfo Set2ndPlatForm(int platFormH, int platFormW, int slabThick, int TbeamPos, int platBeamW, int platBeamH) | 设置休息平台2的相关参数。 （参数同上） |
| public StairDefCreateInfo Set3rdPlatForm(int platFormH, int platFormW, int slabThick, int TbeamPos, int platBeamW, int platBeamH) | 设置休息平台3的相关参数。 （参数同上） |
| public StairDefCreateInfo Set1stStair(int kind, int width, int thickness, int lowPlatLen, int midPlatLen, int highPlatLen, int lowStepNum, int highStepNum) | 设置楼梯的第一跑参数。 梯跑类型 0:AT 1:BT 2:CT 3:DT 4:ET 5:FT 6:HT 7:JT; width:梯板宽度,thickness:梯板厚度, lowPlatLen:低端平板长度, midPlatLen:中端平板长度, highPlatLen:高端平板长度, lowStepNum:低端踏步数, highStepNum:高度踏步数。 |
| public StairDefCreateInfo Set2ndStair(int kind, int width, int thickness, int lowPlatLen, int midPlatLen, int highPlatLen, int lowStepNum, int highStepNum) | 设置楼梯的第二跑参数。 （参数同上） |
| public StairDefCreateInfo Set3rdStair(int kind, int width, int thickness, int lowPlatLen, int midPlatLen, int highPlatLen, int lowStepNum, int highStepNum) | 设置楼梯的第三跑参数。 （参数同上） |
| public StairDefCreateInfo Set4thStair(int kind, int width, int thickness, int lowPlatLen, int midPlatLen, int highPlatLen, int lowStepNum, int highStepNum) | 设置楼梯的第四跑参数。 （参数同上） |
| public StairDefCreateInfo SetGangH(int gangh) | 设置钢号。 |
| public StairDefCreateInfo GetStairDef() | 获取楼梯定义。 |

（18）XNQSectCreateInfo
该类用于设置消能器的相关参数

| public XNQSectCreateInfo() | 该类的构造函数。 |
|---|---|
| public XNQSectCreateInfo SetName(string name) | 设置消能器名称。 |
| public XNQSectCreateInfo SetMat(int mat) |  |
| public XNQSectCreateInfo SetKind(int kind) | 设置截面类型。（1：墙板式，2：梁式，3：隔震阻尼器1型、4：隔震阻尼器2型、5：正人字1型、6：倒人字1型、7：正人字2型、8：倒人字2型、9：正人字3型、10：倒人字3型、11：正人字4型、12：倒人字4型） |
| public XNQSectCreateInfo SetL1(int nL1) | 设置连接板宽度。 |
| public XNQSectCreateInfo SetH1(int nH1) | 设置连接板高度。 |
| public XNQSectCreateInfo SetH(int nH) | 设置阻尼器高度。 |
| public XNQSectCreateInfo SetT(int nThick) |  |
| public XNQSectCreateInfo SetBrcLevel(int nBrcLevel) | 设置斜撑砼等级。 |
| public XNQSectCreateInfo SetBrcMaterial(int nBrcMaterial) | 设置斜撑材料类别。 |
| public XNQSectCreateInfo SetWallLevel(int nWallLevel) | 设置墙砼等级。 |
| public XNQSectCreateInfo SetWallMaterial(int nWallMaterial) | 设置墙材料类别。 |
| public XNQSectCreateInfo SetShuBrcIdDef(int nShuBrcIdDef) | 设置竖杆截面、阻尼柱墩截面。 |
| public XNQSectCreateInfo SetBraceidDef(int braceid) | 设置斜撑截面定义。 |
| public XNQSectCreateInfo SetQuality(float dQ) | 设置质量。 |
| public XNQSectCreateInfo SetXNQPara(string CalPara) | 设置消能器参数。 |
| public Mdl_XNQSect GetXNQDef() | 获取消能器定义。 |

（19）FillWallSectCreateInfo
该类用于设置填充墙定义的相关参数。

| public FillWallSectCreateInfo() | 该类的构造函数。 |
|---|---|
| public FillWallSectCreateInfo SetRongZhong(int RongZhong) | 设置容重。 |
| public FillWallSectCreateInfo SetM(int FillMainMat) | 设置填充材料（填充墙=0、隔墙=1、玻璃幕墙=2）。 |
| public FillWallSectCreateInfo SetThick(int Thick) | 设置填充墙墙厚度。 |
| public FillWallSectCreateInfo SetFuncType(int FuncType) | 设置墙体功能（内墙=0、外墙=1）。 |
| public FillWallSectCreateInfo SetKZJ(int KZJ) | 是否考虑刚度折减（考虑为1，不考虑为0，布置在网格上的隔墙考虑刚度折减，其它不考虑）。 |
| public FillWallSectCreateInfo SetE(int E) | 设置弹性模量。 |
| public FillWallSectCreateInfo SetU(float U) | 设置泊松比。 |

（20）FillWallSegCreateInfo
该类用于设置填充墙布置的相关参数。

| public FillWallSegCreateInfo() | 该类的构造函数。 |
|---|---|
| public FillWallSegCreateInfo SetDefID(int SectID) | 设置填充墙定义的ID。 |
| public FillWallSegCreateInfo SetStdFlrID(int StdFlrID) | 设置标准层ID。 |
| public FillWallSegCreateInfo SetPtBeg(float x1, float y1) | 设置隔墙起始点（用于按照两点的方式布置隔墙）。 |
| public FillWallSegCreateInfo SetPtEnd(float x2, float y2) | 设置隔墙的终点（用于按照两点的方式布置隔墙）。 |
| public FillWallSegCreateInfo SetPtCen(float x1, float y1) | 设置弧形隔墙的圆心。 |
| public FillWallSegCreateInfo SetR(float dR) | 设置弧形隔墙的半径。 |
| public FillWallSegCreateInfo SetAgS(float x2) | 设置弧形隔墙的起始角度（和X轴正方向的角度）。 |
| public FillWallSegCreateInfo SetAgE(float y2) | 设置弧形隔墙的终止角度（和X轴正方向的角度）。 |
| public FillWallSegCreateInfo SetEA(int Ea) | 设置隔墙的偏轴距离。 |
| public FillWallSegCreateInfo SetEZ(int Ez) | 设置墙底高1（同软件中对话框的参数）。 |
| public FillWallSegCreateInfo SetEZ1(int Ez1) | 设置墙顶高1（同软件中对话框的参数）。 |
| public FillWallSegCreateInfo SetEZ2(int Ez2) | 设置墙顶高2（同软件中对话框的参数）。 |
| public FillWallSegCreateInfo SetEZ3(int ez3) | 设置墙底高2（同软件中对话框的参数）。 |
| public FillWallSegCreateInfo SetGridID(int GridId) | 设置网格ID（按照网格的方式布置隔墙）。 |

（21）CantiSlabDefCreateInfo
该类用于设置悬挑板定义的相关参数。

| public CantiSlabDefCreateInfo () | 该类的构造函数。 |
|---|---|
| public CantiSlabDefCreateInfo SetKind(int kind) | 设置悬挑板的截面类型（1：矩形）。 |
| Public CantiSlabDefCreateInfo SetLength(int length) | 设置悬挑板宽度（0为同网格长）。 |
| public CantiSlabDefCreateInfo SetWidth(int width) | 设置悬挑板外挑长度。 |
| public CantiSlabDefCreateInfo SetThick(int thick) | 设置板厚（0为与相邻板厚相同）。 |
| public CantiSlabDefCreateInfo SetSubKind(int nSubKind) | 设置悬挑板的类型（0：悬挑板；1：预制阳台；2：预制空调板；3：挑檐）。 |
| public CantiSlabDefCreateInfo SetPara(string para) | 设置预制阳台和挑檐的参数（详见软件设置）。 |
| public CantiSlabDefCreateInfo SetName(string name) | 设置名称。 |

（22）CantiSlabSegCreateInfo
该类用于设置悬挑板布置的相关参数。

| public CantiSlabSegCreateInfo() | 该类的构造函数。 |
|---|---|
| public CantiSlabSegCreateInfo SetStdFlrID(int stdflrid) | 设置悬挑板的标准层。 |
| public CantiSlabSegCreateInfo SetSectID(int sectid) | 设置悬挑板的定义。 |
| public CantiSlabSegCreateInfo SetGridID(int gridid) | 设置悬挑板所在的网格。 |
| public CantiSlabSegCreateInfo SetEZ(int ez) | 设置距楼板的距离。 |
| public CantiSlabSegCreateInfo SetEC(int ec) | 设置水平偏移。 |
| public CantiSlabSegCreateInfo SetDR(int dr) | 设置布置方向。 |
| public CantiSlabSegCreateInfo SetDeadLive(float dead,float live) | 设置悬挑板恒活荷载。 |

（22）SubBeamCreateInfo
该类用于设置次梁的相关参数。

| public SubBeamCreateInfo () | 该类的构造函数。 |
|---|---|
| public SubBeamCreateInfo SetStdFlrID (int stdflrid) | 设置次梁的标准层。 |
| public SubBeamCreateInfo SetSectID(int sectid) | 设置次梁的定义。 |
| public SubBeamCreateInfo SetStartPoint (float x1, float y1, float z1) | 设置次梁的起始点。 |
| public SubBeamCreateInfo SetEndPoint (float x2, float y2, float z2) | 设置次梁的终止点。 |
| public SubBeamCreateInfo SetGridIDs (int gridID1, int gridID2) | 设置次梁起始的搭接网格gridID1、终止的搭接网格gridID2。 |
