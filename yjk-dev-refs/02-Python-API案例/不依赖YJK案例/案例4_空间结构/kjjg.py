# 本代码案例为创建一个空间结构模型，并于指定路径下生成ydb。
from YJKAPI import *

dataFunc =  DataFunc()
# 标准层
bzc = dataFunc.StdFlr_Generate(3600)
# 空间层
kjc = dataFunc.SpcFlr_Generate()
# 定义柱
defcol2 = dataFunc.ColSect_Def(5, 2, "9,250,250,14,250,14")    # 钢柱
# 定义梁
defbeam1 = dataFunc.BeamSect_Def(5, 2, "6,194,150,9,150,9")   # 钢梁
# 定义斜杆
defbrace1 = dataFunc.BraceSect_Def(5, 8, "102,92")  # 钢斜杆
xpos =  [0, 2000, 4000]
ypos =  [0, 2000]
zpos =  [0, 4000, 6000]

nodelists = []
gridlist =  []
# 新建节点和网格，2层
for k in range(2):
    nodelist =  []
    for i in range(len(xpos)):
        _nodelist =  []
        for j in range(len(ypos)):
            node = dataFunc.Joint_Generate(kjc.ID, xpos[i], ypos[j], zpos[k + 1])
            _nodelist.append(node)
        nodelist.append(_nodelist)
    # 生成网格
    # 竖向
    for _nodelist in nodelist:
        for i in range(len(_nodelist) - 1):
            axis = dataFunc.Axis_Generate(kjc.ID, _nodelist[i].ID, _nodelist[i + 1].ID)
            grid = dataFunc.Grid_Generate(kjc.ID, _nodelist[i].ID, _nodelist[i + 1].ID, axis.ID)
            gridlist.append(grid)

    # 横向
    for i in range(len(nodelist) - 1):
        for j in range(len(nodelist[i])):
            axis = dataFunc.Axis_Generate(kjc.ID, nodelist[i][j].ID, nodelist[i + 1][j].ID)
            grid = dataFunc.Grid_Generate(kjc.ID, nodelist[i][j].ID, nodelist[i + 1][j].ID, axis.ID)
            gridlist.append(grid)
    nodelists.append(nodelist)

# 布置梁
beam_list = dataFunc.beam_arrange(gridlist, defbeam1)
# 布置水平斜杆
dataFunc.brace_arrange(nodelists[0][0][0], nodelists[0][1][1], defbrace1)
dataFunc.brace_arrange(nodelists[0][1][1], nodelists[0][2][0], defbrace1)
dataFunc.brace_arrange(nodelists[1][0][0], nodelists[1][1][1], defbrace1)
dataFunc.brace_arrange(nodelists[1][1][1], nodelists[1][2][0], defbrace1)
# 布置竖直斜杆
dataFunc.brace_arrange(nodelists[1][0][0], nodelists[0][1][0], defbrace1)
dataFunc.brace_arrange(nodelists[0][1][0], nodelists[1][2][0], defbrace1)
dataFunc.brace_arrange(nodelists[1][0][1], nodelists[0][1][1], defbrace1)
dataFunc.brace_arrange(nodelists[0][1][1], nodelists[1][2][1], defbrace1)

dataFunc.brace_arrange(nodelists[0][1][0], nodelists[1][1][0], defbrace1)
dataFunc.brace_arrange(nodelists[0][1][1], nodelists[1][1][1], defbrace1)

# 布置柱
dataFunc.column_arrange(nodelists[1][0][0], defcol2)
dataFunc.column_arrange(nodelists[1][0][1], defcol2)
dataFunc.column_arrange(nodelists[1][2][0], defcol2)
dataFunc.column_arrange(nodelists[1][2][1], defcol2)

# 提交建模数据
dataFunc.DbModel_Assign()
model = dataFunc.GetDbModelData()
my =  Hi_AddToAndReadYjk(model)
current_directory=os.getcwd()
my.CreateYDB(current_directory, "kjjg.ydb")