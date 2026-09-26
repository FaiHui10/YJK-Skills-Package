import pyYJKSPre

"""该例展示如何获取模型的塔楼数及某楼层包含的塔数，将信息生成于D:\Pydsn.txt路径下。"""
def pyyjks():  
    CToSDesign=pyYJKSPre.FP()
    #获取某楼层包含的塔楼数
    a=CToSDesign.TowInflr(1)
    str1=str(a)
    console('Pydsn',str1)
    #获取模型的塔楼数
    b=CToSDesign.TowInMdl()
    str2=str(b)
    console('Pydsn',str2)

def console(filename,infor):                                               # 日志文件生成
    path = 'D:\\'
    file_path = path + filename + '.txt'
    file = open(file_path, 'a')
    file.writelines([infor+ '\n'])
    file.close()

