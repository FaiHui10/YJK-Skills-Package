import os
import pyYJKSModel                                                    # 导入YJK-pyYJKSModel   help(pyYJKSModel)函数可以查看所有类与函数;
import pyYJKCommand
import pyYJKSUI

"""本案例首先进行一个框架结构模型的创建，之后对其进行计算。"""

#节点生成的函数
#输入参数包括关于x向布点的参数xspans、y向布点的参数yspans、标准层bzc以及上节点高Eon
#最终输出一个二维节点向量nodelist[index_x][index_y]
def node_generate(xspans,yspans,bzc,Eon=0):
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
        ydb1.addCol(defcol)
        return defcol
    if(name=="beam" or name=="Beam"):                       # 定义梁
        defbeam = pyYJKSModel.defBeam()                         
        defbeam.set(*params)         
        ydb1.addBeam(defbeam)
        return defbeam 
    if(name=="brace" or name=="Brace"):                     # 定义斜杆
        defbrace = pyYJKSModel.defBrace()
        defbrace.set(*params)
        ydb1.addBrace(defbrace)
        return defbrace
    raise Exception('未定义的构件类型名称')
#荷载定义函数（目前仅支持梁柱墙，其余构件类型可自行添加）
#输入荷载类型名及相关定义参数
#输出荷载定义
def def_load(name,*params):
    if(name=="col" or name=="Col"):                         # 定义柱荷载
        defload=pyYJKSModel.defLoad()
        defload.setElementKind(11)
        defload.setP(params)
        ydb1.addLoad(defload)
        return defload
    if(name=="beam" or name=="Beam"):                       # 定义梁荷载
        defload=pyYJKSModel.defLoad()
        defload.setElementKind(12)
        defload.setP(params)
        ydb1.addLoad(defload)
        return defload
    if(name=="wall" or name=="Wall"):                       # 定义墙荷载
        defload=pyYJKSModel.defLoad()
        defload.setElementKind(1)
        defload.setP(params)
        ydb1.addLoad(defload)
        return defload
    raise Exception('未定义的构件类型名称')
#柱布置函数
#输入参数包括一个二维节点列表nodelist和柱定义defcol
#输出柱列表
def column_arrange(nodelist,defcol):
    column_list=[]
    bzc=nodelist[0][0].getBzc()
    for node_column in nodelist:
        for node in node_column:
            col = pyYJKSModel.creatColumn()                            # 创建柱子
            col.setNodeID(node.getID())                                # 设置节点ID
            col.setDefID(defcol.getID())                               # 设置柱定义ID
            column_list.append(col)                                    # 将col加入待输出列表
            bzc.addEntity(col)                                         # 将生成的柱添加至标准层
    return column_list
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
#荷载布置函数
#输入参数包括一个一维的构件列表gridlist、荷载定义defload
def load_arrange(member_list,defload):
    for member in member_list:
        bzc=member.getBzc()                                 # 获取构件的标准层
        member_load = pyYJKSModel.creatAppLoad()            # 创建荷载
        member_load.setDefID(defload.getID())               # 设置荷载的定义
        member_load.setLoadType(1)                          # 设置荷载工况类型
        member_load.setElementID(member.getID())            # 设置布置荷载的ID
        bzc.addEntity(member_load)                          # 将荷载添加至标准层
#标准层复制函数
#输入参数包括起始高度H_start、标准层bzc、复制次数number、层高height
def bzc_copy(H_start,bzc,number,height):
    for r in range(number):
        zrc = pyYJKSModel.defZrc()                           # 创建自然层
        zrc.setBzcID(bzc.getID())                            # 设置标准层ID
        zrc.setLevel(H_start+height*r)                       # 设置自然层底标高
        zrc.setHeight(height)                                # 设置层高
        ydb1.addZrc(zrc)                                      # 将自然层添加至工程文件
#主体建模函数
def TestBuild():
    global ydb1                                                # 设置全局变量ydb
    ydb1 = pyYJKSModel.creatProjEx()                           # 创建工程
    pyYJKSModel.yjkProj.init(ydb1)                             # 初始化工程文件
    bzc = pyYJKSModel.defBzc()                                # 定义标准层
    bzc.setHeight(3600)                                       # 设置标准层高
    bzc.setDataVect([20,150])                                 # 设置标准层梁钢筋保护层厚度为20，板厚为150
    ydb1.addBzc(bzc)                                           # 将定义的标准层加入ydb
    #柱定义
    defcol=def_member("col",1,400,400,0,0,0,0,0,6,0)          # 添加柱定义
    #梁定义
    defbeam1=def_member("beam",1,250,600,0,0,0,0,0,6,0)       # 添加梁定义                        
    defbeam2=def_member("beam",1,200,400,0,0,0,0,0,6,0)
    #荷载定义
    beamload1=def_load("beam",1,9.6) 
    beamload2=def_load("beam",1,5.5)              
    #框架结构框架柱及框架梁布置
    originpos = [0,0]                                               # 网格坐标原点
    xspans = [originpos[0],3900,3900,3900,3900,3900,3900]           # X向开间
    yspans = [originpos[1],6700,5300]                               # Y向开间
    nodelist=node_generate(xspans,yspans,bzc)                       # 生成节点列表nodelist
    column_arrange(nodelist,defcol)                             # 布置柱子
    gridlist_beam1=grid_generate(nodelist,0,1)                  # 由nodelist生成Y向的网格
    gridlist_beam2=grid_generate(nodelist,1,0)                  # 由nodelist生成X向的网格
    beam_list=beam_arrange(gridlist_beam1,defbeam1)                       # 布置梁
    load_arrange(beam_list,beamload2)
    beam_list=beam_arrange(gridlist_beam2,defbeam2)
    load_arrange(beam_list,beamload1)
    #框架结构次梁布置
    xspans = [originpos[0],3900,3900,3900,3900,3900,3900]            
    yspans = [5200]
    nodelist=node_generate(xspans,yspans,bzc)
    gridlist=grid_generate(nodelist,1,0)
    beam_list=beam_arrange(gridlist,defbeam2)
    load_arrange(beam_list,beamload2)
    #标准层复制
    bzc_copy(0,bzc,5,3600)                                                  # 复制标准层
    print("OK")
    print(ydb1)
    save = pyYJKSModel.SaveYDB("pymodel1", ydb1)                              # 保存ydb文件，自定义文件名
    print(save)
    return 0 

def yjksetLabel(IDString):                                                  # 切换YJK模块Ribbon菜单
    pyYJKSUI.QSetCurrentRibbonLabel(IDString, 1)
    return 1   

def pyyjks():                                                            # 入口函数
    Module_Axis = yjksetLabel("IDModule_Axis")                              # 将标签栏切换至轴线网格
    if Module_Axis:
        pyYJKSUI.QViewSetCursorPos(0,0)                                     # 控制鼠标停留在绘图点（0，0）
        TestBuild() 
    importmodel = pyYJKSUI.QRunCommandEx("yjk_importydb", "pymodel1.ydb", 0) # 导入已经生成的ydb模型pymodel
    pyYJKCommand.RunCommand("yjk_setlayersupport")                          # 前处理
    pyYJKCommand.RunCommand("yjk_repairex")                                 # 修复
    pyYJKCommand.RunCommand("yjk_save")                                     # 保存到项目
    if importmodel:
        pyYJKSUI.QViewSetCursorPos(0, 0)                                    # 控制鼠标停留在绘图点（0，0）
    Module_Pre = yjksetLabel("IDSPRE_ROOT")                                 # 进入前处理模块
    pyYJKCommand.RunCommand("yjkdesign_dsncalculating_all")                 # 生成数据+全部计算
    yjksetLabel("IDDSN_DSP")    
