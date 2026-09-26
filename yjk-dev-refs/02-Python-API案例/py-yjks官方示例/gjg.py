import os
import pyYJKSModel                                                          #导入YJK-pyYJKSModel   help(pyYJKSModel)函数可以查看所有类与函数;
import pyYJKCommand
import pyYJKSUI

"""本案例首先进行一个钢结构模型的创建，之后对其进行计算。"""

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
                gridlist.append(grid)
            if ix < len(nodelist)-1 and direct_x:                    # 创建X方向的网格，其余同上
                grid = pyYJKSModel.creatGrid()                       
                grid.setNode1Ptr(nodelist[ix][iy])                   
                grid.setNode2Ptr(nodelist[ix+1][iy])
                bzc.addEntity(grid)
                gridlist.append(grid)
    return gridlist
#构件定义函数
#输入构件类型名及相关定义参数
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
        bzc=member.getBzc()                                 # 获取构件的标准层
        member_load = pyYJKSModel.creatAppLoad()            # 创建荷载
        member_load.setDefID(defload.getID())               # 设置荷载的定义
        member_load.setLoadType(1)                          # 设置荷载工况类型
        member_load.setElementID(member.getID())            # 设置布置荷载的ID
        bzc.addEntity(member_load)                          # 将荷载添加至标准层
#斜杆布置函数
#输入参数包括一个二维节点列表nodelist和斜杆截面定义defbrace
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
#标准层复制函数
#输入参数包括起始高度H_start、标准层bzc、复制次数number、层高height
def bzc_copy(H_start,bzc,number,height):
    for r in range(number):
        zrc = pyYJKSModel.defZrc()                           # 创建自然层
        zrc.setBzcID(bzc.getID())                            # 设置标准层ID
        zrc.setLevel(H_start+height*r)                       # 设置自然层底标高
        zrc.setHeight(height)                                # 设置层高
        ydb.addZrc(zrc)                                      # 将自然层添加至工程文件
#节点排序合并函数，核心排序算法为二路归并
#输入两个二维节点列表nodelist1、nodelist2
#首先按照两个节点列表中节点的X坐标从小到大进行排序
#当节点的X坐标相同时按照节点的Y坐标从小到大进行排序
#输出合并后的二维节点列表nodelist_total
def merge_nodelist(nodelist1,nodelist2):
    len_list1=len(nodelist1)
    len_list2=len(nodelist2)
    r,c=0,0
    nodelist_total=[]
    while(r<len_list1 and c<len_list2):
        x1=int(nodelist1[r][0].getX())
        x2=int(nodelist2[c][0].getX())
        if(x1==x2):                         #当节点的X坐标相同时按照Y坐标从小到大对节点进行排序
            len1=len(nodelist1[r])
            len2=len(nodelist2[c])
            nodelist=[]
            i,j=0,0
            while(i<len1 and j<len2):
                y1=int(nodelist1[r][i].getY())
                y2=int(nodelist2[c][j].getY())
                if(y1<y2):
                    nodelist.append(nodelist1[r][i])
                    i+=1
                else:
                    nodelist.append(nodelist2[c][j])
                    j+=1
            if(i==len1):
                nodelist+=nodelist2[c][j:]
            else:
                nodelist+=nodelist1[r][i:]
            nodelist_total.append(nodelist)
            r+=1
            c+=1
        elif(x1<x2):                        #当x1<x2时,将nodelist1的当前列加入输出列表nodelist_total
            nodelist_total.append(nodelist1[r])
            r+=1
        else:                               #当x1>x2时,将nodelist2的当前列加入输出列表nodelist_total
            nodelist_total.append(nodelist2[c])
            c+=1
    if(r==len_list1 and c==len_list2):
        return nodelist_total
    if(r==len_list1):
        nodelist_total+=nodelist2[c:]
    if(c==len_list2):
        nodelist_total+=nodelist1[r:]
    return nodelist_total        
#主体建模函数
def TestBuild():
    global ydb                                                            # 设置全局变量ydb
    ydb = pyYJKSModel.creatProjEx()                                       # 创建工程
    pyYJKSModel.yjkProj.init(ydb)                                         # 初始化工程文件
    bzc1 = pyYJKSModel.defBzc()                                           # 定义标准层
    bzc1.setHeight(3600)                                                  # 设置标准层高
    bzc1.setDead(7.0)                                                     # 设置标准层1的恒载
    bzc1.setLive(12.0)                                                    # 设置标准层1的活载
    bzc2 = pyYJKSModel.defBzc()
    bzc2.setHeight(8000)
    ydb.addBzc(bzc1)                                                      # 将定义的标准层加入ydb
    ydb.addBzc(bzc2)
    #柱截面定义
    defcol=def_member("col",2,20,650,400,28,400,28,0,5,0)                 # 柱定义的参数设置
    #梁截面定义
    defbeam1=def_member("beam",2,18,900,300,26,300,26,0,5,0)              # 梁定义的参数设置
    defbeam2=def_member("beam",2,10,500,300,22,300,22,0,5,0)
    defbeam3=def_member("beam",8,152,142,0,0,0,0,0,5,0)
    #定义斜杆
    defbrace=def_member("brace",3,150,0,0,0,0,0,0,6,0)                    # 斜杆定义的参数设置
    #第1标准层
    #钢框架框架柱及框架梁布置
    xspans = [0,6400,6400,6400,6400,6400,6400]                            # X向开间
    yspans = [0,3700,11100]                                               # Y向开间
    nodelist=node_generate(xspans,yspans,bzc1)                            # 生成节点列表nodelist
    column_arrange(nodelist,defcol)                                       # 布置柱子
    gridlist_beam1=grid_generate(nodelist,0,1)                            # 由nodelist生成Y向的网格
    gridlist_beam2=grid_generate(nodelist,1,0)                            # 由nodelist生成X向的网格
    beam_arrange(gridlist_beam1,defbeam1)                                 # 布置梁
    beam_arrange(gridlist_beam2,defbeam2)
    #框架结构次梁布置
    xspans = [6400,6400,6400,6400,6400]
    yspans = [1850]
    nodelist=node_generate(xspans,yspans,bzc1)
    gridlist=grid_generate(nodelist,1,0)
    beam_arrange(gridlist,defbeam2)
    xspans = [0,6400,6400,6400,6400,6400,6400]
    yspans = [5550,1850,1850,1850,1850]
    nodelist=node_generate(xspans,yspans,bzc1)
    gridlist=grid_generate(nodelist,1,0)
    beam_arrange(gridlist,defbeam2)
    #第2标准层
    #钢框架框架梁及框架柱布置
    xspans = [0,6400,6400,6400,6400,6400,6400]
    yspans = [0,14800]
    nodelist=node_generate(xspans,yspans,bzc2)
    column_arrange(nodelist,defcol)
    gridlist_beam1=grid_generate(nodelist,1,0)
    beam_arrange(gridlist_beam1,defbeam2)
    xspans = [0,6400,6400,6400,6400,6400,6400]
    yspans = [7400]
    nodelist_H750=node_generate(xspans,yspans,bzc2,750)                   # 生成上节点高为750的节点列表nodelist_H750
    nodelist=merge_nodelist(nodelist,nodelist_H750)                       # 按先X后Y的顺序合并节点列表nodelist和nodelist_H750
    xspans = [0,6400,6400,6400,6400,6400,6400]
    yspans = [3700,7400]
    nodelist_H385=node_generate(xspans,yspans,bzc2,385)                   # 生成上节点高为385的节点列表nodelist_H385
    nodelist=merge_nodelist(nodelist,nodelist_H385)                       # 按先X后Y的顺序合并节点列表nodelist和nodelist_H385
    nodelist_brace=[]                                                     # 设置斜杆布置的列表，列表中的每个元素为一包含两个节点的列表
    for i in range(4):
        node_combine=[]
        node_combine.append(nodelist[0][i])
        node_combine.append(nodelist[1][i+1])
        nodelist_brace.append(node_combine)
        node_combine=[]
        node_combine.append(nodelist[0][i+1])
        node_combine.append(nodelist[1][i])
        nodelist_brace.append(node_combine)
        node_combine=[]
        node_combine.append(nodelist[-1][i])
        node_combine.append(nodelist[-2][i+1])
        nodelist_brace.append(node_combine)
        node_combine=[]
        node_combine.append(nodelist[-1][i+1])
        node_combine.append(nodelist[-2][i])
        nodelist_brace.append(node_combine)
    gridlist_beam2=grid_generate(nodelist,0,1)
    beam_arrange(gridlist_beam2,defbeam1)
    #圆管及斜杆布置
    nodelist=merge_nodelist(nodelist_H385,nodelist_H750)                   # 按先X后Y的顺序合并节点列表nodelist_H750和nodelist_H385                    
    gridlist_beam3=grid_generate(nodelist,1,0)
    beam_arrange(gridlist_beam3,defbeam3)
    brace_arrange(nodelist_brace,defbrace)                                 # 布置斜杆
    #标准层复制
    bzc_copy(0,bzc1,1,6000)
    bzc_copy(6000,bzc2,1,8000)
    print(ydb)
    save = pyYJKSModel.SaveYDB("pymodel2", ydb)                          # ydb文件保存，自定义文件名
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
    importmodel = pyYJKSUI.QRunCommandEx("yjk_importydb", "pymodel2.ydb", 0) # 导入已经生成的ydb模型pymodel
    pyYJKCommand.RunCommand("yjk_setlayersupport")                          # 前处理
    pyYJKCommand.RunCommand("yjk_repairex")                                 # 修复
    pyYJKCommand.RunCommand("yjk_save")                                     # 保存到项目
    if importmodel:
        pyYJKSUI.QViewSetCursorPos(0, 0)                                    # 控制鼠标停留在绘图点（0，0）
    Module_Pre = yjksetLabel("IDSPRE_ROOT")                                 # 进入前处理模块
    pyYJKCommand.RunCommand("yjkdesign_dsncalculating_all")                 # 生成数据+全部计算
    yjksetLabel("IDDSN_DSP")                                                # 将标签栏切换至设计结果