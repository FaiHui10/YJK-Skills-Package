# 减震器的布置
from YJKAPI import *

dataFunc = DataFunc()
my = Hi_AddToAndReadYjk()
current_directory=os.getcwd()
m_modelData = my.ReadYdb(current_directory+"\\kj.ydb")
dataFunc.SetModel(m_modelData)

# 消能器(墙式)
xnqPara = XNQPara(1)
# 连接单元类型（0：屈曲约束支撑、1：阻尼器麦克斯韦、2：塑性单元wen）
xnqPara.setVal(0, 0)
# 有效刚度
xnqPara.setVal(1, 104167)
# 有效阻尼
xnqPara.setVal(2, 0)
# 非线性
xnqPara.setVal(3, 1)
# 刚度
xnqPara.setVal(4, 104167)
# 屈服力
xnqPara.setVal(5, 500)
# 屈服后刚度比
xnqPara.setVal(6, 0.035)
# 屈服指数
xnqPara.setVal(7, 10)
# 设置面外转动刚度
xnqPara.setVal(9, 1)
# 设置面外平动刚度
xnqPara.setVal(10, 0)
# 施工次序
xnqPara.setVal(11, 1)

xNQSectCreateInfo = XNQSectCreateInfo()
xNQSectCreateInfo.SetKind(1).SetBrcLevel(30).SetWallLevel(30).SetWallMaterial(6).SetBrcMaterial(6).SetL1(1500)
xNQSectCreateInfo.SetH1(1000).SetH(300).SetT(200).SetXNQPara(xnqPara.GetValString())
XNQSect01 = dataFunc.XNQ_Def(xNQSectCreateInfo)
dataFunc.XNQ_arrange(m_modelData.m_Joint[0].StdFlrID, XNQSect01.ID, 1013, 1014, 0, 0, 0, 0, 0)

# 消能器(梁式)
xnqPara1 = XNQPara(2)
# 连接单元类型（0：屈曲约束支撑、1：阻尼器麦克斯韦、2：塑性单元wen）
xnqPara1.setVal(0, 0)
# 有效刚度
xnqPara1.setVal(1, 89285.7031)
# 有效阻尼
xnqPara1.setVal(2, 0)
# 非线性
xnqPara1.setVal(3, 1)
# 刚度
xnqPara1.setVal(4, 89285.7031)
# 屈服力
xnqPara1.setVal(5, 500)
# 屈服后刚度比
xnqPara1.setVal(6, 0.035)
# 屈服指数
xnqPara1.setVal(7, 10)
# 施工次序
xnqPara1.setVal(9, 1)

xNQSectCreateInfo1 = XNQSectCreateInfo()
xNQSectCreateInfo1.SetKind(2).SetH(300).SetT(200).SetXNQPara(xnqPara1.GetValString())
XNQSect02 = dataFunc.XNQ_Def(xNQSectCreateInfo1)
dataFunc.XNQ_arrange(m_modelData.m_Joint[0].StdFlrID, XNQSect02.ID, 0, 0, 1052, 0, 0, 0, 0)

updateInfo = dataFunc.GetUpdateInfo()
my.ReflectAndCreateYDB(updateInfo, current_directory, "AddXNQ.ydb")