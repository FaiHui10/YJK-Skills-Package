# 本代码案例实现如下功能：
# 一、生成蒙皮及蒙皮荷载。
from YJKAPI import *

dataFunc = DataFunc()

# 截面定义
defcol = dataFunc.ColSect_Def(6, 1, "400,400")
defbeam = dataFunc.BeamSect_Def(6, 1, "250,600")
beamload = dataFunc.Load_Def(12, "1.00,9.60")
defskin = dataFunc.SkinLoadSect_Def(0, 0, 1.5, 0)

# 空间层
kjc = dataFunc.SpcFlr_Generate()
bzc = dataFunc.StdFlr_Generate(3600)

# 生成节点
nodelist = []
originpos = [0, 0]

xspans = [ originpos[0], 8000 ]
yspans = [ originpos[1], 8000 ]

for i in range(len(xspans)):
    _nodelist = []
    for j in range(len(yspans)):
        node = dataFunc.Joint_Generate(kjc.ID, xspans[i], yspans[j])
        _nodelist.append(node)
    nodelist.append(_nodelist)

gridlist = []
# 生成网格
# 竖向
for _nodelist in nodelist:
    for i in range(len(_nodelist)-1):
        axis = dataFunc.Axis_Generate(kjc.ID, _nodelist[i].ID, _nodelist[i + 1].ID)
        grid = dataFunc.Grid_Generate(kjc.ID, _nodelist[i].ID, _nodelist[i + 1].ID, axis.ID)
        gridlist.append(grid)

# 生成网格
# 横向
for i in range(len(nodelist)-1):
    for j in range(len(nodelist[i])):
        axis = dataFunc.Axis_Generate(kjc.ID, nodelist[i][j].ID, nodelist[i + 1][j].ID)
        grid = dataFunc.Grid_Generate(kjc.ID, nodelist[i][j].ID, nodelist[i + 1][j].ID, axis.ID)
        gridlist.append(grid)

# 布置框架梁柱及荷载
dataFunc.column_arrange(nodelist, defcol)
beam_list = []
beam_list = dataFunc.beam_arrange(gridlist, defbeam)
dataFunc.load_arrange(beam_list, beamload)

nodelist_temp = []
nodelist_temp.append(nodelist[1][0])
nodelist_temp.append(nodelist[1][1])
nodelist_temp.append(nodelist[0][1])
nodelist_temp.append(nodelist[0][0])

# 添加蒙皮
skinInfo = SkinCreateInfo()
skinInfo.SetDeadLive(5, 2).SetMaterialStyle(1).SetDirection([0.0, 0.0, 0.0]).SetSurroundPt(nodelist_temp).SetNDirection("0,0,0,0,0,1,10")

skin = dataFunc.skin_arrange(skinInfo)
dataFunc.skinLoad_arrange(skin, defskin)


# 提交建模数据
dataFunc.Floor_Assemb(bzc, 0, 3600)
dataFunc.DbModel_Assign()
model = dataFunc.GetDbModelData()
my = Hi_AddToAndReadYjk(model)
current_directory=os.getcwd()
my.CreateYDB(current_directory, "skin.ydb")