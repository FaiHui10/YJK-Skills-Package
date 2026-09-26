# 本案例为对Jccad_Result_New.ydb(基础设计结果)进行读取的案例
# 注意事项如下：
#     1.在软件中进行基础计算后，即可读取生成的Jccad_Result_New.ydb文件，存储位置在“工程路径\基础计算及结果输出\Jccad_Result_New.ydb”
#     2.用户可以根据需要获取内部对象列表，对象类型可查阅“基础计算结果数据库(Jccad_Result_New.ydb)说明”

from YJKAPI import *

def console(content_to_append):
    file_path = "ydbinfo.txt"  # 替换为你的文件路径
    with open(file_path, "a", encoding="utf-8") as file:
        file.write(content_to_append)

jcResDataFunc = JcResultDataFunc()
# 读取ydb
jcResDataFunc.ReadJcYdb(r"C:\Users\10497\Desktop", "Jccad_Result_New.ydb")
# 获取板元节点列表
_m_JcModelData=jcResDataFunc.GetJcResultModel()
m_JcModelData=_m_JcModelData.ToPyList()

FeaPoint = m_JcModelData.m_jcResultGeoFeaPoint
for Point in FeaPoint:
    str = f"ID:{Point.ID},ptx:{Point.ptx},pty:{Point.pty},ptz:{Point.ptz}"
    console(str)