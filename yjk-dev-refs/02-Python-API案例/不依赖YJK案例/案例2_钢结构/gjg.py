# 本代码案例为创建一个钢结构模型，并于指定路径下生成ydb。
from YJKAPI import *

dataFunc = DataFunc()
# 标准层
StdFlr1 = dataFunc.StdFlr_Generate(3600,7,12)
StdFlr2 = dataFunc.StdFlr_Generate(8000)
# 截面定义
defcol = dataFunc.ColSect_Def(5, 2, "20,650,400,28,400,28")
defbeam1 = dataFunc.BeamSect_Def(5, 2, "18,900,300,26,300,26")
defbeam2 = dataFunc.BeamSect_Def(5, 2, "10,500,300,22,300,22")
defbeam3 = dataFunc.BeamSect_Def(5, 8, "152,142")
defbrace = dataFunc.BraceSect_Def(5, 3, "150")
# 荷载定义

# 钢框架框架柱及框架梁布置
nodelist = []
originpos =  [0,0]
xspans =  [ originpos[0], 6400, 6400, 6400, 6400, 6400, 6400 ]
yspans =  [ originpos[1], 3700, 11100 ]
nodelist = dataFunc.node_generate(xspans, yspans, StdFlr1)
dataFunc.column_arrange(nodelist, defcol)
# List<Mdl_Grid> gridlist =  List<Mdl_Grid>()
gridlist_beam1 = dataFunc.grid_generate(nodelist, 0, 1)
gridlist_beam2 = dataFunc.grid_generate(nodelist, 1, 0)
dataFunc.beam_arrange(gridlist_beam1, defbeam1)
dataFunc.beam_arrange(gridlist_beam2, defbeam2)

# 框架结构次梁布置
xspans =  [ 6400, 6400, 6400, 6400, 6400 ]
yspans =  [ 1850 ]
nodelist = dataFunc.node_generate(xspans, yspans, StdFlr1)
gridlist = dataFunc.grid_generate(nodelist, 1, 0)
dataFunc.beam_arrange(gridlist, defbeam2)
xspans =  [ 0, 6400, 6400, 6400, 6400, 6400, 6400 ]
yspans =  [ 5550, 1850, 1850, 1850, 1850 ]
nodelist = dataFunc.node_generate(xspans, yspans, StdFlr1)
gridlist = dataFunc.grid_generate(nodelist, 1, 0)
dataFunc.beam_arrange(gridlist, defbeam2)

# 第2标准层
# 钢框架框架梁及框架柱布置
xspans =  [ 0, 6400, 6400, 6400, 6400, 6400, 6400 ]
yspans =  [ 0, 14800 ]
nodelist = dataFunc.node_generate(xspans, yspans, StdFlr2)
dataFunc.column_arrange(nodelist, defcol)
gridlist_beam1 = dataFunc.grid_generate(nodelist, 1, 0)
dataFunc.beam_arrange(gridlist_beam1, defbeam2)
xspans =  [ 0, 6400, 6400, 6400, 6400, 6400, 6400 ]
yspans =  [ 7400 ]
nodelist_H750 = dataFunc.node_generate(xspans, yspans, StdFlr2, 750)
nodelist = dataFunc.merge_nodelist(nodelist, nodelist_H750)
xspans =  [ 0, 6400, 6400, 6400, 6400, 6400, 6400 ]
yspans =  [ 3700, 7400 ]
nodelist_H385= dataFunc.node_generate(xspans, yspans, StdFlr2, 385)
nodelist = dataFunc.merge_nodelist(nodelist, nodelist_H385)
nodelist_brace=  []

for i in range(4):
    node_combine =  []
    node_combine.append(nodelist[0][i])
    node_combine.append(nodelist[1][i+1])
    nodelist_brace.append(node_combine)
    node_combine =  []
    node_combine.append(nodelist[0][i+1])
    node_combine.append(nodelist[1][i])
    nodelist_brace.append(node_combine)
    node_combine =  []
    node_combine.append(nodelist[len(nodelist) - 1][i])
    node_combine.append(nodelist[len(nodelist) - 2][i+1])
    nodelist_brace.append(node_combine)
    node_combine =  []
    node_combine.append(nodelist[len(nodelist) - 1][i+1])
    node_combine.append(nodelist[len(nodelist) - 2][i])
    nodelist_brace.append(node_combine)

gridlist_beam2= dataFunc.grid_generate(nodelist, 0, 1)
dataFunc.beam_arrange(gridlist_beam2, defbeam1)
# 圆管及斜杆布置
nodelist = dataFunc.merge_nodelist(nodelist_H385, nodelist_H750)
gridlist_beam3= dataFunc.grid_generate(nodelist, 1, 0)
dataFunc.beam_arrange(gridlist_beam3, defbeam3)
dataFunc.brace_arrange(nodelist_brace, defbrace)
# 标准层复制
dataFunc.Floors_Assemb(0, StdFlr1, 1, 6000)
dataFunc.Floors_Assemb(6000, StdFlr2, 1, 8000)
# 提交建模数据
dataFunc.DbModel_Assign()
model = dataFunc.GetDbModelData()
my =  Hi_AddToAndReadYjk(model)
current_directory=os.getcwd()
my.CreateYDB(current_directory, "gjg.ydb")
