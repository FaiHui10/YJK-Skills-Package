# 本代码案例为创建一个剪力墙结构模型，并于指定路径下生成ydb。
from YJKAPI import *

dataFunc =  DataFunc()
StdFlr1 = dataFunc.StdFlr_Generate(3000,12,3)
# 墙定义
defwall = dataFunc.WallSect_Def(6,1,200)
# 墙洞定义
defwallhole = dataFunc.WallHoleDef(900,2500)
# 剪力墙布置,墙洞布置
originpos =  []
originpos.append([0, 0])
originpos.append([7000, 8000])
originpos.append([10500, -8000])
originpos.append([28000, 0])
originpos.append([21000, 8000])
originpos.append([17500, -8000])
for node in originpos:
    xspans = [node[0], 3500, 3500 ]
    yspans = [node[1], 3000, 5000 ]
    nodelist = dataFunc.node_generate(xspans, yspans, StdFlr1)
    gridlist = dataFunc.grid_generate(nodelist,1,1)
    dataFunc.wall_arrange(gridlist, defwall)
    dataFunc.wallhole_arrange(gridlist, defwallhole)

originpos=[]
originpos.append([7000, 0 ])
originpos.append([17500, 0 ])

for node in originpos:
    xspans = [node[0], 3500, 3500, 3500]
    yspans = [node[1], 8000]
    nodelist = dataFunc.node_generate(xspans, yspans, StdFlr1)
    gridlist = dataFunc.grid_generate(nodelist, 1, 1)
    dataFunc.wall_arrange(gridlist, defwall)
    dataFunc.wallhole_arrange(gridlist, defwallhole)
# 标准层复制
dataFunc.Floors_Assemb(0, StdFlr1, 18, 3000)
# 提交建模数据
dataFunc.DbModel_Assign()
model = dataFunc.GetDbModelData()
my =  Hi_AddToAndReadYjk(model)
current_directory=os.getcwd()
my.CreateYDB(current_directory, "jlq.ydb")