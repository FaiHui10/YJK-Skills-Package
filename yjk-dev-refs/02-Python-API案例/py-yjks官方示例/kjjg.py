#import os
import pyYJKSModel                                                 # 导入YJK-pyYJKSModel   help(pyYJKSModel)函数可以查看所有类与函数;
import pyYJKCommand
import pyYJKSUI

"""本案例首先进行一个空间结构模型的创建，之后对其进行计算。"""

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
#输入参数包括二维节点向量nodelist，相关参数direct_x、direct_y
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
#荷载定义函数（目前仅支持梁柱墙，其余构件类型可自行添加）
#输入荷载类型名及相关定义参数
#输出荷载定义
def def_load(name,*params):
    if(name=="col" or name=="Col"):   
        defload=pyYJKSModel.defLoad()
        defload.setElementKind(11)
        defload.setP(params)
        ydb.addLoad(defload)
        return defload
    if(name=="beam" or name=="Beam"):
        defload=pyYJKSModel.defLoad()
        defload.setElementKind(12)
        defload.setP(params)
        ydb.addLoad(defload)
        return defload
    if(name=="wall" or name=="Wall"):
        defload=pyYJKSModel.defLoad()
        defload.setElementKind(1)
        defload.setP(params)
        ydb.addLoad(defload)
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
#输入参数包括一个一维的构件列表gridlist和荷载定义defload
def load_arrange(member_list,defload):
    for member in member_list:
        bzc=member.getBzc()
        member_load = pyYJKSModel.creatAppLoad()
        member_load.setDefID(defload.getID())
        member_load.setLoadType(1)
        member_load.setElementID(member.getID())
        bzc.addEntity(member_load)
#斜杆布置函数
#输入参数包括一个二维节点列表nodelist和斜杆截面定义defbrace
#输出杆件列表
def brace_arrange(nodelist,defbrace):
    brace_list=[]
    bzc=nodelist[0][0].getBzc()
    for node in nodelist:
        brace = pyYJKSModel.creatBrace()                      # 创建斜杆
        brace.setDefID(defbrace.getID())                      # 设置斜杆定义
        brace.setNode1ID(node[0].getID())                     # 设置斜杆布置的第1个节点
        brace.setNode2ID(node[1].getID())                     # 设置斜杆布置的第2个节点
        brace.setEX1(0)                                       # 设置1节点X向的偏心
        brace.setEX2(0)                                       # 设置2节点X向的偏心
        brace.setEY1(0)                                       # 设置1节点Y向的偏心
        brace.setEY2(0)                                       # 设置2节点Y向的偏心
        brace.setEZ1(1)                                       # 设置1节点Z向的偏心
        brace.setEZ2(1)                                       # 设置2节点Z向的偏心
        brace_list.append(brace)                              # 将brace加入待输出列表
        bzc.addEntity(brace)                                  # 将斜杆添加至标准层
    return brace_list 
#简单的杆件建模函数
#输入参数包括X向开间、Y向开间、上节点高、空间层、斜杆定义、相关参数direct_x、direct_y、Z向杆件长
#可进行X、Y、Z三个方向任意组合的杆件布置
def simple_truss(xspans,yspans,Z,kjc,defbrace,direct_x,direct_y,value_z=0):
    nodelist=node_generate(xspans,yspans,kjc,Z)
    if(direct_x):                                             # X向杆件布置
        for i in range(len(nodelist)-1):
            nodelist_brace=[[nodelist[i][j],nodelist[i+1][j]] for j in range(len(nodelist[i]))]
            brace_arrange(nodelist_brace,defbrace)
    if(direct_y):                                             # Y向杆件布置
        for i in range(len(nodelist)):
            nodelist_brace=[[nodelist[i][j],nodelist[i][j+1]] for j in range(len(nodelist[i])-1)]
            brace_arrange(nodelist_brace,defbrace)
    if(value_z):                                              # Z向杆件布置
        nodelist_Z=node_generate(xspans,yspans,kjc,Z+value_z)
        for i in range(len(nodelist)):
            nodelist_brace=[[nodelist[i][j],nodelist_Z[i][j]] for j in range(len(nodelist[i]))]
            brace_arrange(nodelist_brace,defbrace)
#楼板布置函数，可设置为洞口
#输入参数包括楼板的形心坐标Xc、Yc、楼板厚度Thick、标准层bzc、是否开洞ishole
def slab_arrange(Xc,Yc,Thick,bzc,ishole):
    slab = pyYJKSModel.creatSlab()                           # 创建楼板
    slab.setXc(Xc)                                           # 设置楼板形心X
    slab.setYc(Yc)                                           # 设置楼板形心Y
    slab.setThick(Thick)                                     # 设置楼板厚度
    bzc.addEntity(slab)                                      # 将楼板添加至标准层
    if(ishole):                                              # 将楼板设置为开洞
        hole = pyYJKSModel.creatHole()                       # 创建板洞
        hole.setSlabID(slab.getID())                         # 获取楼板ID
        bzc.addEntity(hole)                                  # 将板洞加入标准层
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
    global ydb                                                # 设置全局变量ydb
    ydb = pyYJKSModel.creatProjEx()                           # 创建工程
    pyYJKSModel.yjkProj.init(ydb)                             # 初始化工程文件
    bzc = pyYJKSModel.defBzc()                                # 定义标准层
    bzc.setHeight(3600)                                       # 设置标准层高
    ydb.addBzc(bzc)                                           # 将定义的标准层加入ydb
    kjc = pyYJKSModel.creatSpaceBzc()                         # 创建空间层
    kjc.setHeight(0)                                          # 设置空间层高                      
    ydb.addBzc(kjc)                                           # 将定义的空间层加入ydb
    #定义柱
    defcol1 = def_member("col",1, 600, 600, 0, 0, 0, 0, 0, 6, 0)             # 添加柱定义
    defcol2 = def_member("col",1, 800, 1100, 0, 0, 0, 0, 0, 6, 0)           
    #梁定义
    defbeam1= def_member("beam",1, 350, 800, 0, 0, 0, 0, 0, 6, 0)            # 添加梁定义                        
    defbeam2= def_member("beam",1, 600, 900, 0, 0, 0, 0, 0, 6, 0)               
    #定义斜杆                                                             
    defbrace1= def_member("brace",8, 180, 166, 0, 0, 0, 0, 0, 5, 0)          # 添加杆件定义  
    defbrace2= def_member("brace",8, 102, 92, 0, 0, 0, 0, 0, 5, 0)
    defbrace3= def_member("brace",8, 219, 199, 0, 0, 0, 0, 0, 5, 0)
    #定义荷载
    beamload1=def_load("beam",1,8) 
    beamload2=def_load("beam",1,8.5)
    #布置框架结构
    originpos=[[0,0],[0,27900],[64800,0],[64800,27900]]                      # 网格坐标原点
    for node in originpos:
        xspans = [node[0],3600,3600,3600,3600]                               # X向开间
        yspans = [node[1],8400]                                              # Y向开间
        nodelist=node_generate(xspans,yspans,bzc)                                # 生成节点列表nodelist
        column_arrange(nodelist,defcol1)                                     # 布置柱
        gridlist_beam1=grid_generate(nodelist,1,1)                           # 由nodelist生成X向及Y向网格
        beam_list=beam_arrange(gridlist_beam1,defbeam1)                      # 布置梁 
        load_arrange(beam_list,beamload1)
    originpos=[[0,8400],[64800,8400]]
    for node in originpos:    
        xspans = [node[0],3600,3600,3600,3600]
        yspans = [node[1],6500,6500,6500]
        nodelist=node_generate(xspans,yspans,bzc)
        column_arrange(nodelist,defcol1)
        gridlist_beam2=grid_generate(nodelist,1,1)
        beam_list=beam_arrange(gridlist_beam2,defbeam1)
        load_arrange(beam_list,beamload1)
        xspans = [node[0],14400]
        yspans = [11650,6500,6500]
        nodelist=node_generate(xspans,yspans,bzc)
        gridlist_beam3=grid_generate(nodelist,1,0)
        beam_list=beam_arrange(gridlist_beam3,defbeam1)
        load_arrange(beam_list,beamload2)
    xspans = [14400,7200,7200,7200,7200,7200,7200,7200]
    yspans = [0,36300]
    nodelist=node_generate(xspans,yspans,bzc)
    column_arrange(nodelist,defcol2)
    gridlist_beam3=grid_generate(nodelist,1,0)
    beam_list=beam_arrange(gridlist_beam3,defbeam2)
    load_arrange(beam_list,beamload1)
    slab_arrange(39600,18150,0,bzc,True)                                      # 先布置楼板，然后布置洞口

    xspans = [0,13200]
    #布置主桁架
    originpos = [20400,0]
    for c in range(6):
        nodelist_brace1=[]                                                     # 上弦杆节点列表
        nodelist_brace2=[]                                                     # 腹杆节点列表
        nodelist_brace3=[]                                                     # 下弦杆节点列表
        xspans = [originpos[0]+c*7200,2400]                                    # X向开间
        yspans = [2420 for x in range(15)]                                     # Y向开间
        yspans.insert(0,originpos[1])
        node_down_y=[2420 for x in range(14)]                                  # 下弦杆节点Y坐标
        node_down_y.insert(0,originpos[1]+2420/2) 
        node_down=node_generate([xspans[0]+xspans[1]/2],node_down_y,kjc,10707) # 生成下弦杆节点
        nodelist=node_generate(xspans,yspans,kjc,13100)                        # 上弦杆节点
        nodelist_brace1+=[[nodelist[0][i],nodelist[0][i+1]] for i in range(15)]# 组合上弦杆节点 
        nodelist_brace1+=[[nodelist[1][i],nodelist[1][i+1]] for i in range(15)]
        for i in range(15):                                                    # 组合腹杆节点
            nodelist_brace2.append([node_down[0][i],nodelist[0][i]])
            nodelist_brace2.append([node_down[0][i],nodelist[1][i]])
            nodelist_brace2.append([node_down[0][i],nodelist[0][i+1]])
            nodelist_brace2.append([node_down[0][i],nodelist[1][i+1]]) 
            nodelist_brace2.append([nodelist[0][i+1],nodelist[1][i+1]])        # 水平X向杆件        
            if((i+1)%2):                                                                                       
                nodelist_brace2.append([nodelist[0][i+1],nodelist[1][i]])      # 水平斜向杆件
            else:
                nodelist_brace2.append([nodelist[1][i+1],nodelist[0][i]])
        brace_arrange(nodelist_brace2,defbrace2)
        for i in range(len(node_down[0])-1):
            nodelist_brace3.append([node_down[0][i],node_down[0][i+1]])         # 组合下弦杆节点
        brace_arrange(nodelist_brace1,defbrace1)                                # 进行杆件布置
        brace_arrange(nodelist_brace3,defbrace3)
    #布置次桁架
    SecTruss_infos_left=[[14400,7260,2000,3],[14400,14520,2000,3],[14400,19360,2000,3],[14400,26620,2000,3]]    # 左侧次桁架段的坐标原点
    SecTruss_infos_right=[[58800,7260,2000,3],[58800,14520,2000,3],[58800,19360,2000,3],[58800,26620,2000,3]]   # 右侧次桁架段的坐标原点
    SecTruss_infos_mid=[]                                                                                       # 中部次桁架段的坐标原点   
    for r in range(2):
        for c in range(5):
            tmp=[22800+c*7200,14520+r*4840,1600,3]
            SecTruss_infos_mid.append(tmp)
    SecTruss_infos=SecTruss_infos_left+SecTruss_infos_right+SecTruss_infos_mid
    for SecTruss_info in SecTruss_infos:
        nodelist_brace1=[]
        nodelist_brace2=[]
        nodelist_brace3=[]
        yspans = [SecTruss_info[1],2420]
        xspans = [SecTruss_info[2] for x in range(SecTruss_info[3])]
        xspans.insert(0,SecTruss_info[0])
        node_down_x=[SecTruss_info[2] for x in range(2)]
        node_down_x.insert(0,SecTruss_info[0]+SecTruss_info[2]/2) 
        node_down=node_generate(node_down_x,[yspans[0]+yspans[1]/2],kjc,10707)
        nodelist=node_generate(xspans,yspans,kjc,13100)
        nodelist_brace1+=[[nodelist[i][0],nodelist[i+1][0]] for i in range(SecTruss_info[3])]
        nodelist_brace1+=[[nodelist[i][1],nodelist[i+1][1]] for i in range(SecTruss_info[3])]
        for i in range(SecTruss_info[3]):
            nodelist_brace2.append([node_down[i][0],nodelist[i][0]])
            nodelist_brace2.append([node_down[i][0],nodelist[i][1]])
            nodelist_brace2.append([node_down[i][0],nodelist[i+1][0]])
            nodelist_brace2.append([node_down[i][0],nodelist[i+1][1]]) 
            nodelist_brace2.append([nodelist[i+1][0],nodelist[i+1][1]])
            if((i+1)%2):
                nodelist_brace2.append([nodelist[i+1][0],nodelist[i][1]])
            else:
                nodelist_brace2.append([nodelist[i+1][1],nodelist[i][0]])
        brace_arrange(nodelist_brace2,defbrace2)
        for i in range(len(node_down[0])-1):
            nodelist_brace3.append([node_down[0][i],node_down[0][i+1]])
        brace_arrange(nodelist_brace1,defbrace2)
    #布置次桁架的下弦杆
    xspans=[15400,2000,2000,2200]
    yspans=[8470,7260,4840,7260]
    simple_truss(xspans,yspans,10707,kjc,defbrace2,1,0)                     # 布置X向杆件
    xspans=[57600,2200,2000,2000]
    yspans=[8470,7260,4840,7260]
    simple_truss(xspans,yspans,10707,kjc,defbrace2,1,0)                     # 布置Y向杆件
    originpos=[[21600,15730],[28800,15730],[36000,15730],[43200,15730],[50400,15730]]
    for p in originpos:
        xspans=[p[0],2000,1600,1600,2000]
        yspans=[p[1],4840]
        simple_truss(xspans,yspans,10707,kjc,defbrace2,1,0)
    #布置桁架上弦杆与周边框架搭接的部分
    xspans=[14400,6000,2400,4800,2400,4800,2400,4800,2400,4800,2400,4800,2400,6000]
    yspans=[0,36300]
    simple_truss(xspans,yspans,13100,kjc,defbrace2,1,0,-500)                # 布置X向杆件及Z向杆件
    xspans=[14400,50400]
    yspans=[0,7260,2420,4840,2420,2420,2420,4840,2420,7260]
    simple_truss(xspans,yspans,13100,kjc,defbrace2,0,1,-500)                # 布置Y向杆件及Z向杆件
    bzc_copy(0,bzc,3,4200)                                                  # 复制标准层
    save = pyYJKSModel.SaveYDB("pymodel", ydb)                              # ydb文件保存，自定义文件名
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
    importmodel = pyYJKSUI.QRunCommandEx("yjk_importydb", "pymodel.ydb", 0) # 导入已经生成的ydb模型pymodel
    
    pyYJKCommand.RunCommand("yjk_repairex")                                 # 修复
    pyYJKCommand.RunCommand("yjk_save")                                     # 保存到项目
    #pyYJKCommand.RunCommand("yjk_setlayersupport")                          # 前处理
    if importmodel:
        pyYJKSUI.QViewSetCursorPos(0, 0)                                    # 控制鼠标停留在绘图点（0，0）
    Module_Pre = yjksetLabel("IDSPRE_ROOT")                                 # 进入前处理模块
    pyYJKCommand.RunCommand("yjkdesign_dsncalculating_all")                 # 生成数据+全部计算
    yjksetLabel("IDDSN_DSP")                                                # 将标签栏切换至设计结果
    return 