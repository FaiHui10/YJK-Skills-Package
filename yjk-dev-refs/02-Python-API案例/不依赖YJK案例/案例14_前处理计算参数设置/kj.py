# 本代码案例为创建一个框架结构模型，并于指定路径下生成ydb。
from YJKAPI import *

def setSpara():
    # 风荷载信息_基本参数
    dataFunc.ProjectPara_Set(212, "3")
    # 体型分段数&&迎风面系数&&背风面系数
    dataFunc.ProjectPara_Set(213, "2,3,4,6")
    # 风荷载体型系数_X向
    dataFunc.ProjectPara_Set(214, "13,0.9,0.85,-0.55,0.1,0.9,0.85,-0.55,0.1,0.9,0.85,-0.55,0.1")
    # 风荷载体型系数_Y向
    dataFunc.ProjectPara_Set(214, "13,0.9,0.85,-0.55,0.1,0.9,0.85,-0.55,0.1,0.9,0.85,-0.55,0.1")
    # 考虑横风向风振
    dataFunc.ProjectPara_Set(207, "1")
    # 截面形状
    dataFunc.ProjectPara_Set(228, "22804")
    # 圆形截面_结构二阶平动周期
    dataFunc.ProjectPara_Set(231, "0.4")

dataFunc = DataFunc()
setSpara()
# 标准层
StdFlr = dataFunc.StdFlr_Generate(3900)
# 截面定义
defcol = dataFunc.ColSect_Def(6, 1, "400,400")
defbeam1 = dataFunc.BeamSect_Def(6, 1, "250,600")
defbeam2 = dataFunc.BeamSect_Def(6, 1, "200,400")

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

# 布置梁上荷载
dataFunc.load_arrange(beam_list, beamload1)

# 标准层复制
dataFunc.Floors_Assemb(0, StdFlr, 6, 3600)
# 提交建模数据
dataFunc.DbModel_Assign()
model = dataFunc.GetDbModelData()
my = Hi_AddToAndReadYjk(model)
current_directory=os.getcwd()
isok = my.CreateYDB(current_directory, "kj.ydb")