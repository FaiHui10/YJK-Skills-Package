# 本代码案例包含型钢截面定义、自定义工况荷载定义及布置、层间板布置、弧形网格创建、前处理计算参数设置、特殊构件定义、分组设置等，并于指定路径下生成ydb。
from YJKAPI import *

# 创建弧形网格
def hxgrid(StdFlrID, dataFunc):
    center = dataFunc.Joint_Generate(StdFlrID, -2000, -2000)
    pt1 = dataFunc.Joint_Generate(StdFlrID, -1000, -2000)
    pt2 = dataFunc.Joint_Generate(StdFlrID, -2000, -3000)
    axis = dataFunc.Axis_Generate(StdFlrID, -center.ID, pt1.ID)
    dataFunc.Grid_Generate(StdFlrID, pt1.ID, pt2.ID, axis.ID)

# 本代码案例包含型钢截面定义、自定义工况荷载定义及布置、层间板布置、弧形网格创建、前处理计算参数设置、特殊构件定义、分组设置等，并于指定路径下生成ydb。
dataFunc = DataFunc()
# 标准层
StdFlr = dataFunc.StdFlr_Generate(3900)
para = BzcPara()
str = para.GetValString()
StdFlr.Para = str
# 前处理计算参数设置，参数含义请查阅前处理接口说明--计算参数ID对应表
ProjectPara = dataFunc.ProjectPara_Set(101,"10102")

# 截面定义
defcol = dataFunc.ColSect_Def(6, 1, "400,400")
dataFunc.ColSect_Def(5, 303, "", "L40X2.0")# 型钢截面
# dataFunc.ColSect_Def(5, 26, "", "HW350X350")# 型钢截面
defbeam = dataFunc.BeamSect_Def(6, 1, "250,600")
# 荷载定义
beamload = dataFunc.Load_Def(12, "1.00,9.60")
jointload = dataFunc.Load_Def(-1, "1001,1002,1003,1004,1005,1006")

# 自定义工况荷载定义（活载）
gkloadInfo = GKLoadDefCreateInfo()
gkloadInfo.SetDeadFacotr(0.5).SetLiveFacotr(1, 1.1, 1.1, 1.1).SetName("test_live").SetData("0.50,1.50,1.50,1.30,1.00,0.70,0.50,0.60,0.50,")

GKLoad = dataFunc.GKLoad_Def(gkloadInfo)

# 生成节点
nodelist = []
originpos = [0, 0]

xspans = [originpos[0], 8000]
yspans = [originpos[1], 8000]

for i in range(len(xspans)):
    _nodelist = []
    for j in range(len(yspans)):
        node = dataFunc.Joint_Generate(StdFlr.ID, xspans[i], yspans[j])
        _nodelist.append(node)
    nodelist.append(_nodelist)

gridlist = []
# 生成网格
# 竖向
for _nodelist in nodelist:
    for i in range(len(_nodelist)-1):
        axis = dataFunc.Axis_Generate(StdFlr.ID, _nodelist[i].ID, _nodelist[i + 1].ID)
        grid = dataFunc.Grid_Generate(StdFlr.ID, _nodelist[i].ID, _nodelist[i + 1].ID, axis.ID)
        gridlist.append(grid)

# 生成网格
# 横向
for i in range(len(nodelist)-1):
    for j in range(len(nodelist[i])):
        axis = dataFunc.Axis_Generate(StdFlr.ID, nodelist[i][j].ID, nodelist[i + 1][j].ID)
        grid = dataFunc.Grid_Generate(StdFlr.ID, nodelist[i][j].ID, nodelist[i + 1][j].ID, axis.ID)
        gridlist.append(grid)

# 布置框架梁柱及荷载
dataFunc.column_arrange(nodelist, defcol)
beam_list1 = dataFunc.beam_arrange(gridlist, defbeam)
beam_list2 = dataFunc.beam_arrange(gridlist, defbeam,0,-2000,-2000)
dataFunc.load_arrange(beam_list1, beamload, GKLoad.kind)

# 层间板(节点按照逆时针方向排序)
midSlabNode = []
midSlabNode.append(nodelist[0][0])
midSlabNode.append(nodelist[0][1])
midSlabNode.append(nodelist[1][1])
midSlabNode.append(nodelist[1][0])

midslabCreateInfo = MidSlabCreateInfo()
midslabCreateInfo.SetThick(200).SetStdFlr(StdFlr).SetCentroid(4000, 4000).SetSurroundNodes(midSlabNode, -5900).SetDeadLive(5,2).SetSurroundGrids(gridlist)
dataFunc.midslab_arrange(midslabCreateInfo)

# 自定义工况板荷载
slabInfo = SlabCreateInfo()
slabInfo.SetCentroid(4000, 4000).SetThick(300).SetStdFlr(StdFlr).SetCc(0).SetDeadLive(9, 9)

slab = dataFunc.slab_arrange(slabInfo)
dataFunc.load_arrange(slab, GKLoad.kind, "10")


# 特殊梁
proper = Property("SpBeam")
proper.setVal(3,1)# 连梁

proper.setVal(0, 1)# 左端铰接
proper.setVal(1, 0)# 右端固定

res = proper.GetValString()
for beam in beam_list1:
    dataFunc.property_arrange(beam.ID, "SpBeam", 27, res)

node_list = [ nodelist[0][0] ]
# 节点荷载
dataFunc.load_arrange(node_list, jointload)

# 弧形网格
hxgrid(StdFlr.ID, dataFunc)

# 楼层组装
dataFunc.Floors_Assemb(0, StdFlr, 1, 3600)

# 设置组
idlist = []
zrcidnewlist = []
for beam in beam_list1:
    idlist.append(beam.ID)
    zrcidnewlist.append(1037)
dataFunc.add_group("group01", idlist, zrcidnewlist)

# 提交建模数据
dataFunc.DbModel_Assign()
model = dataFunc.GetDbModelData()
my =Hi_AddToAndReadYjk(model)
current_directory=os.getcwd()
my.CreateYDB(current_directory, "elseSetting.ydb")

