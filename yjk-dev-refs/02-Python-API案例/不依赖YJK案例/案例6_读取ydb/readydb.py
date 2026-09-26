# 本代码案例为打开一个指定路径的ydb文件，实现如下功能：
# 一、读取ydb信息并将内容输出到 ydbinfo.txt。
# 二、修改ydb中的楼层高度及柱截面尺寸，并生成一个新的ydb。

from YJKAPI import *

def console(content_to_append):
    file_path = "ydbinfo.txt"  # 替换为你的文件路径
    with open(file_path, "a", encoding="utf-8") as file:
        file.write(content_to_append)

dataFunc = DataFunc()
my = Hi_AddToAndReadYjk()
current_directory=os.getcwd()
_m_modelData = my.ReadYdb(current_directory+"\\kj.ydb")
m_modelData=_m_modelData.ToPyList()
dataFunc.SetModel(_m_modelData)

xing = '*'*50
title = xing + "标准层信息" + xing
console(title)
StdFlrList = m_modelData.m_StdFlr
for i in range(len(StdFlrList)):
    str = f"ID:{StdFlrList[i].ID},No:{StdFlrList[i].No},Height:{StdFlrList[i].Height}"
    console(str)

title = xing + "楼层信息" + xing
console(title)
FloorList = m_modelData.m_Floor
for i in range(len(FloorList)):
    str = f"ID:{FloorList[i].ID}, 层底标高:{FloorList[i].LevelB}, 层高:{FloorList[i].Height}"
    console(str)
    # 修改层高
    m_modelData.m_Floor[i].Height = 4800
    if (i > 0):
        # 修改层底标高
        m_modelData.m_Floor[i].LevelB = m_modelData.m_Floor[i - 1].LevelB + m_modelData.m_Floor[i].Height

title = xing + "节点信息" + xing
console(title)
JointList = m_modelData.m_Joint
for i in range(len(JointList)):
    str = f"ID:{JointList[i].ID}, X坐标:{JointList[i].X}, Y坐标:{JointList[i].Y}"
    console(str)

# 修改柱截面尺寸
tmp = m_modelData.m_ColSect[0].ShapeVal
console(tmp)
tmp = tmp.replace("400", "600")
console(tmp)
m_modelData.m_ColSect[0].ShapeVal = tmp
m_modelData.m_BeamSect[0].Name = "梁1_修改"
dataFunc.property_arrange(m_modelData.m_BeamSect[0].ID, "CustomName", 8, m_modelData.m_BeamSect[0].Name)
m_modelData.m_BeamSect[1].Name = "梁2_修改"
dataFunc.property_arrange(m_modelData.m_BeamSect[1].ID, "CustomName", 8, m_modelData.m_BeamSect[1].Name)
dataFunc.ColSect_Def(6, 26, "", "H98X99X5X7")
updateInfo = dataFunc.GetUpdateInfo()

my.ReflectAndCreateYDB(updateInfo,current_directory, "kj_modified.ydb")