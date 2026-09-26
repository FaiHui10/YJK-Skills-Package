# 本案例为一对基础YDB进行节点网格创建、构件类型定义、构件布置的案例
# 注意事项如下：
#     1.需要先导入一个在进入基础模块后，点击重新读取按钮生成的Jccad_0.ydb，其生成于YJK项目路径
#     2.在完成好基础构件定义、布置等操作之后需要先删除YJK项目路径下的Jccad_0.ydb文件，然后再生成Jccad_0.ydb文件
#     3.之后在YJK的命令行中输入 jccad_read_by_ydb命令，不要点击导入ydb的按钮，此按钮会产生累加的效应，此问题将于最新版本修复
#     4.循环读写YDB时需要注意当前读取的YDB是上一循环生成的YDB
#     5.基础数据依赖上部建模的数据，所以需要在最开始时需要调用一次重新读取获取,之后不要轻易调用，如果上部结构发生变化需要调用时要先删除Jccad_0.ydb之后再点击重新读取

from YJKAPI import *

import os
import glob

def delete_files(path):
    # 获取匹配 "Jccad_0*" 的文件列表
    filename_list1 = glob.glob(os.path.join(path, "Jccad_0*"))
    # 获取匹配 "*_F.*" 的文件列表
    filename_list2 = glob.glob(os.path.join(path, "*_F.*"))
    
    # 删除文件
    for file in filename_list1:
        os.remove(file)
    for file in filename_list2:
        os.remove(file)

current_directory=os.getcwd()
# 基础建模
jcdataFunc = JcDataFunc()
jcdataFunc.ReadJcYdb(current_directory, "\\Jccad_0.ydb")
_m_JcModelData=jcdataFunc.GetJcModelDBdata()
m_JcModelData=_m_JcModelData.ToPyList()
# 获取节点和网格
nodelist = m_JcModelData.m_jcNode
iwaglist = m_JcModelData.m_jcIwag
# 定义独基
jcdataFunc.JcDj_Def(0, "0,0,0,2,3300,3300,300,600,600,3000,0,0,0")
# 布置独基
jcdataFunc.JcDJ_App(nodelist[0].ID, 1, 500, 500, 60, -1.5, 1)
# 定义地基梁
FbeamDef = jcdataFunc.JcFbeam_Def(401, 1001, 1501, 501, 301, 0)
# 布置地基梁
jcdataFunc.JcFbeam_App(FbeamDef.lID, iwaglist[0], 500, -1.5, 1)
# 定义桩
PileDef = jcdataFunc.JcPile_Def(2, "800,200,300,500,25.0,1")
# 定义桩基承台(方形承台)
DaisDef = jcdataFunc.JcDais_Def(10, 2, 1, 4, 100, 100)
jcdataFunc.JcDais_Cir(DaisDef.DaisFlag, 0, 1500, 1500)
jcdataFunc.JcDais_Cir(DaisDef.DaisFlag, 0, -1500, 1500)
jcdataFunc.JcDais_Cir(DaisDef.DaisFlag, 0, -1500, -1500)
jcdataFunc.JcDais_Cir(DaisDef.DaisFlag, 0, 1500, -1500)
jcdataFunc.JcDais_StepH(0, 0, 301)
# 定义桩基承台(圆形承台)
DaisDef1 = jcdataFunc.JcDais_Def(10, 0, 1, 4, 100, 100)
jcdataFunc.JcDais_Cir(DaisDef1.DaisFlag, 3001)
jcdataFunc.JcDais_StepH(DaisDef1.DaisFlag, 0, 301)
# 布置桩基承台
jcdataFunc.JcDais_App(nodelist[0].ID, DaisDef.lID, 100, 100, 60, 10, -1.5, 1)
jcdataFunc.JcDais_App(nodelist[10].ID, DaisDef1.lID, 100, 100, 60, 10, -1.5, 1)
# 布置桩
jcdataFunc.JcPile_App(PileDef.lID, nodelist[0], -1, 0.0, 10)
jcdataFunc.JcPile_App(PileDef.lID, 750, 750, 0, DaisDef.DaisFlag, 0.0, 10, -1.5, 1)
jcdataFunc.JcPile_App(PileDef.lID, 750, -750, 0, DaisDef.DaisFlag, 0.0, 10, -1.5, 1)
jcdataFunc.JcPile_App(PileDef.lID, -750, 750, 0, DaisDef.DaisFlag, 0.0, 10, -1.5, 1)
jcdataFunc.JcPile_App(PileDef.lID, -750, -750, 0, DaisDef.DaisFlag, 0.0, 10, -1.5, 1)
jcdataFunc.JcPile_App(PileDef.lID, 750, 750, 0, DaisDef1.DaisFlag, 0.0, 10, -1.5, 1)
jcdataFunc.JcPile_App(PileDef.lID, 750, -750, 0, DaisDef1.DaisFlag, 0.0, 10, -1.5, 1)
jcdataFunc.JcPile_App(PileDef.lID, -750, 750, 0, DaisDef1.DaisFlag, 0.0, 10, -1.5, 1)
jcdataFunc.JcPile_App(PileDef.lID, -750, -750, 0, DaisDef1.DaisFlag, 0.0, 10, -1.5, 1)
# 拉梁定义
LLDef = jcdataFunc.JcLL_Def(400, 600)
# 拉梁布置
jcdataFunc.JcLL_App(LLDef.lID, iwaglist[1], 100, 10, 10, -1.5, 1)
# 定义条基
TJDef = jcdataFunc.JcTJ_Def(0, "2000,200,133,100,250,100,100,60,60")
# 条基布置
jcdataFunc.JcTJ_App(TJDef.lID, iwaglist[3], 100, -1.5, 1)
# 定义筏板
SlabDef = jcdataFunc.JcRaftSlab_Def(-1, "200,10,2,3,0,-0.5,1,10,10,10")
# 筏板布置
jcdataFunc.JcRaftSlab_App(SlabDef.lID, 16200, 12600)
jcdataFunc.JcRaftSlab_App(SlabDef.lID, 11100, 12600)
jcdataFunc.JcRaftSlab_App(SlabDef.lID, 11100, -600)
jcdataFunc.JcRaftSlab_App(SlabDef.lID, 16200, -600)
# 定义柱墩
ZDDef = jcdataFunc.JcZD_Def(1, 5000, 4000, 1000, 45)
# 布置柱墩
ColumnList = m_JcModelData.m_jcAppColumn
ColumnList[12].lZDKind = ZDDef.kind

delete_files(r"C:\Users\10497\Desktop\用户问题\115.基础测试\yjk")
jcdataFunc.CreateYDB(r"C:\Users\10497\Desktop\用户问题\115.基础测试\yjk", "Jccad_0.ydb")