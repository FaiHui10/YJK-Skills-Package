# 填充墙布置的案例
from YJKAPI import *

dataFunc = DataFunc()
my = Hi_AddToAndReadYjk()
current_directory=os.getcwd()
_m_modelData = my.ReadYdb(current_directory+"\\fillwall_pre.ydb")
m_modelData=_m_modelData.ToPyList()
dataFunc.SetModel(_m_modelData)
# 填充墙定义
fillWallSectCreateInfo01 = FillWallSectCreateInfo()
fillWallSectCreateInfo01.SetE(4000).SetRongZhong(10).SetM(0).SetThick(200).SetFuncType(0).SetKZJ(1).SetU(0.15)

fillWallSectCreateInfo02 = FillWallSectCreateInfo()
fillWallSectCreateInfo02.SetE(4000).SetRongZhong(15).SetM(1).SetThick(200).SetFuncType(1).SetKZJ(1).SetU(0.15)

fillWallSectCreateInfo03 = FillWallSectCreateInfo()
fillWallSectCreateInfo03.SetE(4000).SetRongZhong(10).SetM(0).SetThick(200).SetFuncType(0).SetKZJ(0).SetU(0.15)

fillWallDef01 = dataFunc.FillWall_Def(fillWallSectCreateInfo01)
fillWallDef02 = dataFunc.FillWall_Def(fillWallSectCreateInfo02)
fillWallDef03 = dataFunc.FillWall_Def(fillWallSectCreateInfo03)
# 按照网格的方式布置填充墙
for grid in m_modelData.m_Grid:
    fillWallSegCreateInfo = FillWallSegCreateInfo()
    fillWallSegCreateInfo.SetGridID(grid.ID).SetStdFlrID(m_modelData.m_StdFlr[0].ID).SetDefID(fillWallDef01.ID)
    dataFunc.FillWall_arrange(fillWallSegCreateInfo)

# 按照两点的方式布置填充墙
fillWallSegCreateInfo_ByPt = FillWallSegCreateInfo()
fillWallSegCreateInfo_ByPt.SetPtBeg(0, 0).SetPtEnd(2400, 2400).SetGridID(0).SetStdFlrID(m_modelData.m_StdFlr[0].ID).SetDefID(fillWallDef03.ID)

dataFunc.FillWall_arrange(fillWallSegCreateInfo_ByPt)

# 弧形填充墙
fillWallSegCreateInfo_Cir = FillWallSegCreateInfo()
fillWallSegCreateInfo_Cir.SetPtCen(5000, 2500).SetR(2000).SetAgS(0).SetGridID(0).SetAgE(270).SetStdFlrID(m_modelData.m_StdFlr[0].ID).SetDefID(fillWallDef03.ID)

dataFunc.FillWall_arrange(fillWallSegCreateInfo_Cir)

updateInfo = dataFunc.GetUpdateInfo()
my.ReflectAndCreateYDB(updateInfo, current_directory, "fillwall_post.ydb")