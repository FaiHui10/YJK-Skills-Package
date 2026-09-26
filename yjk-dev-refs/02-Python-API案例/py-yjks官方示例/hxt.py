import os
import pyYJKSModel                                                        # 导入YJK-pyYJKSModel   help(pyYJKSModel)函数可以查看所有类与函数;
import pyYJKCommand
import pyYJKSUI
import pyYJKSPre                                                          # 前处理模块

"""本案例首先进行一个核心筒的创建，之后对其进行进行两端铰接梁的定义及连梁的定义，最后进行计算。"""

#节点生成的函数
#输入参数包括关于x向布点的参数xspans、x向布点的参数xspans、标准层bzc以及上节点高Eon
#最终输出一个二维节点向量nodelist[index_x][index_y]
def node_generate(xspans,yspans,bzc,Eon=0,is3d=False):
    xp = 0                                                          
    nodelist = []  
    for nodex in range(len(xspans)):
        yp = 0
        xp += xspans[nodex]
        node_combine=[]
        for nodey in range(len(yspans)):
            node = pyYJKSModel.creatNode()                          # 创建节点
            node.setX(xp)                                           # 设置节点X坐标
            yp += yspans[nodey]
            node.setY(yp)                                           # 设置节点Y坐标
            node.setEon(Eon)                                        # 设置节点的上节点高
            bzc.addEntity(node)                                     # 将节点添加至标准层
            node_combine.append(node)
        nodelist.append(node_combine) 
    return nodelist
#网格生成函数
#输入参数包括二维节点向量nodelist、相关参数direct_x、direct_y
#输出一个一维的网格列表gridlist
def grid_generate(nodelist,direct_x,direct_y):
    gridlist = []
    bzc=nodelist[0][0].getBzc()
    for ix in range(len(nodelist)):                                   
        for iy in range(len(nodelist[ix])):
            if iy< len(nodelist[0])-1 and direct_y:                  # 创建Y方向的网格
                grid = pyYJKSModel.creatGrid()                       # 创建网格
                grid.setNode1Ptr(nodelist[ix][iy])                   # 设置网格线的第一个点
                grid.setNode2Ptr(nodelist[ix][iy+1])                 # 设置网格线的第二个点
                bzc.addEntity(grid)                                  # 将生成的网格线添加至标准层
                gridlist.append(grid)                                # 将grid加入待输出列表
            if ix < len(nodelist)-1 and direct_x:                    # 创建X方向的网格，其余同上
                grid = pyYJKSModel.creatGrid()                       
                grid.setNode1Ptr(nodelist[ix][iy])                   
                grid.setNode2Ptr(nodelist[ix+1][iy])
                bzc.addEntity(grid)
                gridlist.append(grid)
    return gridlist
#构件定义函数（目前仅支持梁柱墙，其余构件类型可自行添加）
#输入构件类型名及相关定义参数
#输出构件定义
def def_member(name,*params):
    if(name=="col" or name=="Col"):                         # 定义柱
        defcol = pyYJKSModel.defCol()                             
        defcol.set(*params)              
        ydb.addCol(defcol)
        return defcol
    if(name=="beam" or name=="Beam"):                       # 定义梁
        defbeam = pyYJKSModel.defBeam()                         
        defbeam.set(*params)         
        ydb.addBeam(defbeam)
        return defbeam 
    if(name=="brace" or name=="Brace"):                     # 定义斜杆
        defbrace = pyYJKSModel.defBrace()
        defbrace.set(*params)
        ydb.addBrace(defbrace)
        return defbrace
    raise Exception('未定义的构件类型名称')
#楼板布置函数，可设置为洞口
#输入参数包括楼板的
def slab_arrange(Xc,Yc,Thick,bzc,ishole):
    slab = pyYJKSModel.creatSlab()                           # 创建楼板
    slab.setXc(Xc)                                           # 设置楼板形心X
    slab.setYc(Yc)                                           # 设置楼板形心Y
    slab.setThick(Thick)                                     # 设置楼板厚度
    bzc.addEntity(slab)                                      # 将楼板添加至标准层
    if(ishole):                                              # 将楼板设置为开洞
        hole = pyYJKSModel.creatHole()                       # 创建板洞
        hole.setSlabID(slab.getID())                         # 获取楼板ID
        bzc.addEntity(hole)     
#梁布置函数
#输入参数包括一个一维的网格列表gridlist和梁定义defbeam
#输出梁列表
def beam_arrange(gridlist,defbeam):
    beam_list=[]
    bzc=gridlist[0].getBzc()
    for grid in gridlist:
        beam = pyYJKSModel.creatBeam()                      # 创建梁
        beam.setGridID(grid.getID())                        # 设置网格ID
        beam.setDefID(defbeam.getID())                      # 设置梁定义
        beam_list.append(beam)                              # 将beam加入待输出列表
        bzc.addEntity(beam)                                 # 将梁添加至标准层
    return beam_list
#墙布置函数
#输入参数包括一维的网格列表gridlist和墙定义defwall
#输出墙列表
def wall_arrange(gridlist,defwall):
    wall_list=[]
    bzc=gridlist[0].getBzc()
    for grid in gridlist:
        wall = pyYJKSModel.creatWall()                      # 创建墙
        wall.setGridID(grid.getID())                        # 设置网格ID
        wall.setDefID(defwall.getID())                      # 设置墙定义
        wall_list.append(wall)                              # 将wall加入待输出列表
        bzc.addEntity(wall)  
#构件id获取函数
#输入构件列表
#输出构件id列表
def get_id(member_list):
    id_list=[]
    for member in member_list:
        id_list.append(member.getID())
    return id_list
#标准层复制函数
#输入参数包括起始高度H_start、标准层bzc、复制次数number、层高height
def bzc_copy(H_start,bzc,number,height):
    for r in range(number):
        zrc = pyYJKSModel.defZrc()                           # 创建自然层
        zrc.setBzcID(bzc.getID())                            # 设置标准层ID
        zrc.setLevel(H_start+height*r)                       # 设置自然层底标高
        zrc.setHeight(height)                                # 设置层高
        ydb.addZrc(zrc)   

#主体建模函数
def TestBuild():
    print("OK")
    global ydb                                                # 设置全局变量ydb
    ydb = pyYJKSModel.creatProjEx()                           # 创建工程
    pyYJKSModel.yjkProj.init(ydb)                             # 初始化工程文件
    bzc = pyYJKSModel.defBzc()                                # 定义标准层
    bzc.setHeight(3600)                                       # 设置标准层高
    bzc.setDataVect([20,150])                                 # 设置标准层梁钢筋保护层厚度为20，板厚为150
    ydb.addBzc(bzc)                                           # 将定义的标准层加入ydb
    #梁定义
    defbeam1=def_member("beam",1,200,800,0,0,0,0,0,6,0)       # 添加梁定义                        
    defbeam2=def_member("beam",1,600,800,0,0,0,0,0,6,0)            
    #墙定义
    defwall = pyYJKSModel.defWall()                           # 添加墙定义
    defwall.setK(1)                                           # 设置墙类型
    defwall.setT(600)                                         # 设置墙厚
    defwall.setM(6)                                           # 设置墙材料
    ydb.addWall(defwall)                                      # 将墙定义添加至ydb   
    #框架结构框架柱及框架梁布置
    xspans = [0,10500]                                          # X向开间
    yspans = [0,9600]                                           # Y向开间
    nodelist=node_generate(xspans,yspans,bzc)                   # 生成节点列表nodelist
    gridlist=grid_generate(nodelist,0,1)                        # 由nodelist生成Y向的网格
    wall_arrange(gridlist,defwall)
    beam_list1=[]
    beam_list2=[]
    originpos=[[0,0],[7000,0]]
    for node in originpos:
        xspans = [node[0],3500]                                # X向开间
        yspans = [node[1],9600]                                # Y向开间
        nodelist=node_generate(xspans,yspans,bzc)              # 生成节点列表nodelist
        gridlist=grid_generate(nodelist,1,0)                   # 由nodelist生成Y向的网格
        wall_arrange(gridlist,defwall)
        xspans = [node[0],3500]                                # X向开间
        yspans = [node[1]+3200,3200]                           # Y向开间
        nodelist=node_generate(xspans,yspans,bzc)              # 生成节点列表nodelist
        gridlist=grid_generate(nodelist,1,0)                   # 由nodelist生成Y向的网格
        beam_list1+=beam_arrange(gridlist,defbeam1)
    xspans = [3500,3500]                                
    yspans = [node[1],9600]
    nodelist=node_generate(xspans,yspans,bzc)
    gridlist=grid_generate(nodelist,0,1)
    beam_arrange(gridlist,defbeam1)
    gridlist=grid_generate(nodelist,1,0)
    beam_list2+=beam_arrange(gridlist,defbeam2)
    beam_list1=get_id(beam_list1)
    beam_list2=get_id(beam_list2)
    #标准层复制
    bzc_copy(0,bzc,3,3600)                                                  # 复制标准层
    save = pyYJKSModel.SaveYDB("pymodel", ydb)                              # 保存ydb文件，自定义文件名
    return beam_list1, beam_list2

def yjksetLabel(IDString):                                                  # 切换YJK模块Ribbob菜单
    pyYJKSUI.QSetCurrentRibbonLabel(IDString, 1)
    return 1   

def pyyjks():                                                            # 入口函数
    Module_Axis = yjksetLabel("IDModule_Axis")                              # 将标签栏切换至轴线网格
    if Module_Axis:
        pyYJKSUI.QViewSetCursorPos(0,0)                                     # 控制鼠标停留在绘图点（0，0）
        beam_list1,beam_list2=TestBuild()
    importmodel = pyYJKSUI.QRunCommandEx("yjk_importydb", "pymodel.ydb", 0) # 导入已经生成的ydb模型pymodel
    pyYJKCommand.RunCommand("yjk_setlayersupport")                          # 前处理
    pyYJKCommand.RunCommand("yjk_repairex")                                 # 修复
    pyYJKCommand.RunCommand("yjk_save")                                     # 保存到项目
    if importmodel:
        pyYJKSUI.QViewSetCursorPos(0, 0)                                    # 控制鼠标停留在绘图（0，0）
    Module_Pre = yjksetLabel("IDSPRE_ROOT")                                 # 进入前处理模块
    for id in beam_list1:
        pyYJKSPre.yjkAddPropertyVec(id,"SpBeam",[1,1,1,0],False)
    for id in beam_list2:
        pyYJKSPre.yjkAddPropertyVec(id,"SpBeam",[0,0,1,1,0,0,-70102,0,0,0,2,0,1],False)
    pyYJKCommand.RunCommand("yjkdesign_dsncalculating_all")                 # 生成数据+全部计算
    yjksetLabel("IDDSN_DSP")                                            # 将标签栏切换至轴线网格