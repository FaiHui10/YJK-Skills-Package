# 导入命名空间
from YJKAPI import *

dataFunc = DataFunc()
my = Hi_AddToAndReadYjk()
current_directory=os.getcwd()
_m_modelData = my.ReadYdb(current_directory+"\\kj.ydb")
m_modelData=_m_modelData.ToPyList()
dataFunc.SetModel(_m_modelData)

# 双跑楼梯
stairDefCreateInfo1 = StairDefCreateInfo()
stairDefCreateInfo1.SetKind(20).Set1stPlatForm(1800, 1720, 80, 1720, 200, 400).Set1stStair(0, 1720, 100, 0, 0, 0, 12, 0).Set2ndStair(2, 1720, 100, 0, 0, 30, 12, 0)
stairDefCreateInfo1.SetStepW(300).IsGenPtFarBeam(1).IsGenColumn(1).SetTZSect(200, 200).SetAllLevel(0).SetEndPos(0).SetLevel(0).SetStartPos(30)

# 四跑楼梯
stairDefCreateInfo2 = StairDefCreateInfo()
stairDefCreateInfo2.SetKind(40).Set1stPlatForm(900, 1720, 80, 1720, 200, 400).Set2ndPlatForm(1800, 3230, 80, 3230, 200, 400).Set3rdPlatForm(2700, 1720, 80, 1720, 200, 400).Set1stStair(0, 1720, 100, 0, 0, 0, 6, 0)
stairDefCreateInfo2.Set2ndStair(0, 1720, 100, 0, 0, 0, 6, 0).Set3rdStair(0, 1720, 100, 0, 0, 0, 6, 0).Set4thStair(2, 1720, 100, 0, 0, 3230, 6, 0).SetAllLevel(0).SetEndPos(0).SetLevel(0).SetStartPos(3230).SetStepW(300)
stairDefCreateInfo2.IsGenPtFarBeam(1).IsGenColumn(1).SetTZSect(200, 200)

# 钢楼梯
stairDefCreateInfo3 = StairDefCreateInfo()
stairDefCreateInfo3.SetKind(30).Set1stPlatForm(1200, 2630, 0, 2630, 0, 0).Set2ndPlatForm(2400, 1720, 0, 1720, 0, 0).Set1stStair(0, 1720, 6, 0, 0, 0, 8, 0).Set2ndStair(0, 1720, 6, 0, 0, 0, 8, 0)
stairDefCreateInfo3.Set3rdStair(2, 1720, 6, 0, 0, 2630, 8, 0).SetAllLevel(0).SetEndPos(0).SetLevel(0).SetGangH(235).SetStartPos(1720).SetTZSect(200, 200).IsGenColumn(1).SetStepW(300)

# 转角楼梯
stairDefCreateInfo4 = StairDefCreateInfo()
stairDefCreateInfo4.SetKind(25).Set1stPlatForm(1800, 50, 80, 50, 200, 400).Set1stStair(0, 50, 100, 0, 0, 0, 12, 0).Set2ndStair(2, 50, 100, 0, 0, 300, 12, 0)
stairDefCreateInfo4.SetAllLevel(0).SetEndPos(0).SetLevel(0).SetStartPos(1700).SetStepW(300).IsGenColumn(1).SetTZSect(200, 200)


starDef1 = dataFunc.Stair_Def(stairDefCreateInfo1)
starDef2 = dataFunc.Stair_Def(stairDefCreateInfo2)
starDef3 = dataFunc.Stair_Def(stairDefCreateInfo3)
starDef4 = dataFunc.Stair_Def(stairDefCreateInfo4)

dataFunc.stair_arrange(m_modelData.m_Slab[0], starDef1)
dataFunc.stair_arrange(m_modelData.m_Slab[1], starDef2)
dataFunc.stair_arrange(m_modelData.m_Slab[2], starDef3)
dataFunc.stair_arrange(m_modelData.m_Slab[3], starDef4)

updateInfo = dataFunc.GetUpdateInfo()
current_directory=os.getcwd()
my.ReflectAndCreateYDB(updateInfo, current_directory, "new.ydb")