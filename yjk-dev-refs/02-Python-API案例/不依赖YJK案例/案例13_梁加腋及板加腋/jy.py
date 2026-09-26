# 本代码案例为创建一个带加腋梁及加腋板的框架结构模型，并于指定路径下生成ydb（请修改生成ydb的目录）。
from YJKAPI import *

dataFunc = DataFunc()
# 标准层
StdFlr = dataFunc.StdFlr_Generate(3900)
para = BzcPara()
str = para.GetValString()

# 截面定义
defcol = dataFunc.ColSect_Def(6, 1, "400,400")
defbeam = dataFunc.BeamSect_Def(6, 1, "250,600")
defbeamjy = dataFunc.BeamJYSect_Def(0, "1000,500,400", "jy01")
defslabjy1 = dataFunc.SlabJYSect_Def(1, "1500.00,500.00,0.00,0.00,")
defslabjy2 = dataFunc.SlabJYSect_Def(2, "0.00,0.00,1500.00,500.00,")

# 生成节点
nodelist = []
for i in range(2):
    for j in range(2):
        node= dataFunc.Joint_Generate(StdFlr.ID, i*10000, j*10000)
        nodelist.append(node)

# 生成轴线及网格
axislist = []
axislist.append(dataFunc.Axis_Generate(StdFlr.ID, nodelist[0].ID, nodelist[1].ID))
axislist.append(dataFunc.Axis_Generate(StdFlr.ID, nodelist[2].ID, nodelist[3].ID))
axislist.append(dataFunc.Axis_Generate(StdFlr.ID, nodelist[1].ID, nodelist[3].ID))
axislist.append(dataFunc.Axis_Generate(StdFlr.ID, nodelist[0].ID, nodelist[2].ID))

gridlist = []
gridlist.append(dataFunc.Grid_Generate(StdFlr.ID, nodelist[0].ID, nodelist[1].ID, axislist[0].ID))
gridlist.append(dataFunc.Grid_Generate(StdFlr.ID, nodelist[2].ID, nodelist[3].ID, axislist[1].ID))
gridlist.append(dataFunc.Grid_Generate(StdFlr.ID, nodelist[1].ID, nodelist[3].ID, axislist[2].ID))
gridlist.append(dataFunc.Grid_Generate(StdFlr.ID, nodelist[0].ID, nodelist[2].ID, axislist[3].ID))

# 布置梁
beam_list = dataFunc.beam_arrange(gridlist, defbeam)
# 布置柱
for node in nodelist:
    dataFunc.column_arrange(node, defcol)
# 加腋梁
for beam in beam_list:
    dataFunc.beamjy_arrange(defbeamjy, beam)
# 楼板布置
slab = dataFunc.slab_arrange(5000, 5000, 300, StdFlr, False)

# 加腋板
dataFunc.slabjy_arrange(defslabjy2, gridlist[0])
dataFunc.slabjy_arrange(defslabjy1, gridlist[3])
dataFunc.slabjy_arrange(defslabjy1, gridlist[1])
dataFunc.slabjy_arrange(defslabjy2, gridlist[2])

# 楼层组装
dataFunc.Floors_Assemb(0, StdFlr, 1, 3600)
# 提交建模数据
dataFunc.DbModel_Assign()
model = dataFunc.GetDbModelData()
my = Hi_AddToAndReadYjk(model)
current_directory=os.getcwd()
my.CreateYDB(current_directory, "jykj.ydb")