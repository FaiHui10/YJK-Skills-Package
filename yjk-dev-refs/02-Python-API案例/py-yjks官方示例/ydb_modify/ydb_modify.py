import os
import pyYJKSModel                                          # 导入YJK-pyYJKSModel   help(pyYJKSModel)函数可以查看所有类与函数;

"""本案例不需要依赖yjk软件，但需要在依赖项文件夹内运行，
    首先读取一个ydb，之后对其进行修改，然后保存。"""

def LoadTest():
    ydb = pyYJKSModel.LoadYDB("123")
    defbeam2 = pyYJKSModel.defBeam()                        # 梁定义
    defbeam2.set(1, 600, 350, 0, 0, 0, 0, 0, 6, 0)          # 梁参数定义
    defbeam2.getM()  # 梁参数获取
    print("defbeam_isSteelSec?", defbeam2.isSteelSec())     # 查询属性   #梁参数查看
    ydb.addBeam(defbeam2)
    bzclist = pyYJKSModel.getList(-4,ydb)                   # 得到模型中的所有标准层 返回列表[]
    for v in range(len(bzclist)):
        bzc = pyYJKSModel.yjkBzc.cast(bzclist[v])           # 遍历所有列表，对每个标准层进行操作
        print("第",v+1,"个标准层")
        bzcbeam = bzc.getGjVec(12)                          # 得到标准层中的构件(例为梁)
        print(len(bzcbeam),"个标准层梁bzcbeam")
        for b in range(len(bzcbeam)):
            beam2 = ydb.getBeamFromID(bzcbeam[b].getID())
            beam2.setDefID(defbeam2.getID())
            grid1 = beam2.getGridPtr()                      # 梁得到网格
            getwall_by_grid = grid1.getGridConnectedEnt(1)  # 得到网格上的指定构件
            for w in range(len(getwall_by_grid)):
                pwall = pyYJKSModel.yjkWall.cast(getwall_by_grid[w])
        bzc.setHeight(5000)                                 # 修改标准层高，注意！标准层高修改后自然层底标高和层高需对应修改，否则标准层修改无效
    zrclist = pyYJKSModel.getList(-5, ydb)                  # 获取所有自然层列表
    if len(zrclist) == 0:
        return
    for z in range(len(zrclist)):                           # 使用循环对自然层进行操作
        zrc = pyYJKSModel.yjkZrc.cast(zrclist[z])
        # print(zrc.getHeight(),zrc.getLevel())             # 查询自然层信息
        zrc.setLevel(z*5000)                                # 修改底标高
        zrc.setHeight(5000)                                 # 修改层高
    lever = 10                                              # 再次加10层
    flheight = 3800
    for r in range(lever):  # 添加自然层
        print("第", r + 1, "个自然层")
        zrc = pyYJKSModel.defZrc()
        zrc.setBzcID(bzc.getID())
        zrc.setLevel(flheight * r+5000*10)
        zrc.setHeight(flheight)
        ydb.addZrc(zrc)
    save = pyYJKSModel.SaveYDB("ok", ydb)                   # 保存修改
    print(save)

LoadTest()