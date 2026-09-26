# 本代码案例为创建一个框架结构模型，并于指定路径下生成ydb。
from YJKAPI import *

dataFunc = DataFunc()
# 标准层
StdFlr = dataFunc.StdFlr_Generate(3900)
# 截面定义
defcol = dataFunc.ColSect_Def(6, 1, "400,400")
defbeam1 = dataFunc.BeamSect_Def(6, 1, "250,600")
defbeam2 = dataFunc.BeamSect_Def(6, 1, "200,400")
colCapDefInfo = ColCapSectCreateInfo()
colCapDefInfo.SetKind(1).SetSectPara(1000, 1000, 1000, 2000, 1000, 2000).SetName("柱帽截面01")
colCapSect = dataFunc.ColCapSect_Def(colCapDefInfo)
# 荷载定义
beamload1 = dataFunc.Load_Def(12, "1.00,9.60")
beamload2 = dataFunc.Load_Def(12, "1.00,5.50")
# 生成节点
nodelist = []
originpos = [0,0]
xpos = [ originpos[0], 3900, 7800, 11700, 15600, 19500, 23400 ]
ypos = [ originpos[1], 6700, 12000 ]

for i in range(len(xpos)):
    _nodelist =[]
    for j in range(len(ypos)):
        node = dataFunc.Joint_Generate(StdFlr.ID, xpos[i], ypos[j])
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

# 横向
for i in range(len(nodelist)-1):
    for j in range(len(nodelist[i])):
        axis = dataFunc.Axis_Generate(StdFlr.ID, nodelist[i][j].ID, nodelist[i + 1][j].ID)
        grid = dataFunc.Grid_Generate(StdFlr.ID, nodelist[i][j].ID, nodelist[i + 1][j].ID, axis.ID)
        gridlist.append(grid)

# 布置框架梁柱
col_list= dataFunc.column_arrange(nodelist, defcol)
beam_list = dataFunc.beam_arrange(gridlist, defbeam1)
# 布置柱帽
dataFunc.colCap_arrange(col_list[0], colCapSect)

# 布置板
slabInfo = SlabCreateInfo()
slabInfo.SetCentroid(1950, 9350).SetThick(300).SetStdFlr(StdFlr).SetCc(0).SetDeadLive(9, 9)

slab = dataFunc.slab_arrange(slabInfo)

# 布置梁上荷载
dataFunc.load_arrange(beam_list, beamload1)

# 标准层复制
dataFunc.Floors_Assemb(0, StdFlr, 6, 3600)
# 提交建模数据
dataFunc.DbModel_Assign()
model = dataFunc.GetDbModelData()
my = Hi_AddToAndReadYjk(model)
# current_directory=r"E:\MyProject\9.python_api_new中文"
current_directory=os.getcwd()
isok = my.CreateYDB(current_directory, "kj.ydb")