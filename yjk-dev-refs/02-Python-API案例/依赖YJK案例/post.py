# 导入命名空间
from YJKAPI import *
# import tkinter as tk
# from tkinter import messagebox

# # 创建隐藏的主窗口
# root = tk.Tk()
# root.withdraw()  # 隐藏主窗口
# root.attributes('-topmost', True)  # 确保消息框置顶

# def show_list_content(values):
#     message = "\n".join(str(val) for val in values)
#     messagebox.showinfo("列表内容为：", message)
# def show_single_content(val):
#     messagebox.showinfo(f"值为{val}",master=root)
# def show_dict(dict):
#     message = "\n".join(str(val) for val in dict)
#     messagebox.showinfo(f"值为{message}")

"""读取当前模型中的第一个组（group），并将其中的构件截面进行修改"""
def test_group_update():
    yjkscmd = YJKSCommandPy()
    yjkscmd.RunCommand("yjk_save")
    my = Hi_AddToAndReadYjk()
    model = my.ReadFromYJK()
    maxID = my.GetUnionID()
    dataFunc = DataFunc()
    dataFunc.SetModel(model)
    dataFunc.SetID(maxID)
    ##新增截面
    defcol = dataFunc.ColSect_Def(6, 1, "501,501")
    defbeam = dataFunc.BeamSect_Def(6, 1, "251,1001")
    defwall = dataFunc.WallSect_Def(6, 1, 1001)
    defbrace = dataFunc.BraceSect_Def(5, 3, "501")
    defwallhole = dataFunc.WallHoleDef(300, 2501)
    ##修改YJK工程中group内构件的截面
    if (model.m_Group.Count() == 0):
        return
    group = dataFunc.GetGroupObjList(model.m_Group[0])
    for col in group.collist:
        col.SectID = defcol.ID
    for beam in group.beamlist:
        beam.SectID = defbeam.ID
    for wall in group.walllist:
        wall.SectID = defwall.ID
    for brace in group.bracelist:
        brace.SectID = defbrace.ID
    for wallhole in group.windowlist:
        wallhole.SectID = defwallhole.ID
    dataFunc.DbModel_Assign()
    updateInfo = dataFunc.GetUpdateInfo()
    ##增加到yjk
    my.ReflecToYJK(updateInfo)

"""不通过ydb，直接在内存中完成新模型的重新生成"""
def test_refresh():
    dataFunc = DataFunc()
    # 标准层
    StdFlr = dataFunc.StdFlr_Generate(3900)
    # 截面定义
    defcol = dataFunc.ColSect_Def(6, 1, "400,400")
    defbeam1 = dataFunc.BeamSect_Def(6, 1, "250,600")
    # 荷载定义
    beamload1 = dataFunc.Load_Def(12, "1.00,9.60")
    # 生成节点
    nodelist = []
    originpos = [0,0]
    xpos = [ originpos[0], 3900, 7800, 11700, 15600, 19500, 23400 ]
    ypos = [ originpos[1], 6700, 12000 ]

    for i in range(len(xpos)):
        _nodelist =[]
        for j in range(len(ypos)):
            node = dataFunc.Joint_Generate(StdFlr.ID, xpos[i], ypos[j])
            _nodelist.append(node)
        nodelist.append(_nodelist)

    gridlist = []
    # 生成网格
    # 竖向
    for _nodelist in nodelist:
        for i in range(len(_nodelist)-1):
            axis = dataFunc.Axis_Generate(StdFlr.ID, _nodelist[i].ID, _nodelist[i + 1].ID)
            grid = dataFunc.Grid_Generate(StdFlr.ID, _nodelist[i].ID, _nodelist[i + 1].ID, axis.ID)
            gridlist.append(grid)

    # 横向
    for i in range(len(nodelist)-1):
        for j in range(len(nodelist[i])):
            axis = dataFunc.Axis_Generate(StdFlr.ID, nodelist[i][j].ID, nodelist[i + 1][j].ID)
            grid = dataFunc.Grid_Generate(StdFlr.ID, nodelist[i][j].ID, nodelist[i + 1][j].ID, axis.ID)
            gridlist.append(grid)

    # 布置框架梁柱
    col_list= dataFunc.column_arrange(nodelist, defcol)
    beam_list = dataFunc.beam_arrange(gridlist, defbeam1)

    # 布置板
    slabInfo = SlabCreateInfo()
    slabInfo.SetCentroid(1950, 9350).SetThick(300).SetStdFlr(StdFlr).SetCc(0).SetDeadLive(9, 9)

    slab = dataFunc.slab_arrange(slabInfo)

    # 布置梁上荷载
    dataFunc.load_arrange(beam_list, beamload1)

    # 标准层复制
    dataFunc.Floors_Assemb(0, StdFlr, 6, 3600)
    #提交建模数据
    dataFunc.DbModel_Assign()
    model = dataFunc.GetDbModelData()
    my = Hi_AddToAndReadYjk(model)
    isok = my.RefreshToYJK()

"""修改楼层属性中的楼层信息"""
def test_flrInfo():
    info = YJKSPrePy_Tower()
    info.Init()
    info.Load()
    res = info.GetTower(1, 1)
    res.cCL = 60
    info.AddTower(res, 1)
    info.Save()
    num = info.GetTowNO()
    list = info.GetFzTower(1)

"""设置前处理的计算参数"""
def test_pre():
    test2 = YJKSPrePy_JSCS()
    #风荷载信息_基本参数
    test2.SetSParInt(212, 3)

    #体型分段数&&迎风面系数&&背风面系数
    TXFD = [0]*4
    #体型分段数
    TXFD[0] = 3
    #第一段最高层号
    TXFD[1] = 2
    #第二段最高层号
    TXFD[2] = 4
    #第三段最高层号
    TXFD[3] = 6
    test2.SetSParIntArray(213, TXFD)

    #风荷载体型系数_X向
    TXXS_X = [0]*13
    #第一段X挡风&&X迎风面&&X背风面&&X侧风面
    TXXS_X[0] = 13.0
    TXXS_X[1] = 0.9
    TXXS_X[2] = 0.85
    TXXS_X[3] = -0.55
    TXXS_X[4] = 0.1
    #第二段
    TXXS_X[5] = 0.9
    TXXS_X[6] = 0.85
    TXXS_X[7] = -0.55
    TXXS_X[8] = 0.1
    #第三段
    TXXS_X[9] = 0.9
    TXXS_X[10] = 0.85
    TXXS_X[11] = -0.55
    TXXS_X[12] = 0.1

    test2.SetSParFloatArray(214, TXXS_X)

    #风荷载体型系数_X向
    TXXS_Y = [0]*13

    #第一段X挡风&&Y迎风面&&Y背风面&&Y侧风面
    TXXS_Y[0] = 13.0
    TXXS_Y[1] = 0.9
    TXXS_Y[2] = 0.85
    TXXS_Y[3] = -0.55
    TXXS_Y[4] = 0.1
    #第二段
    TXXS_Y[5] = 0.9
    TXXS_Y[6] = 0.85
    TXXS_Y[7] = -0.55
    TXXS_Y[8] = 0.1
    #第三段
    TXXS_Y[9] = 0.9
    TXXS_Y[10] = 0.85
    TXXS_Y[11] = -0.55
    TXXS_Y[12] = 0.1

    test2.SetSParFloatArray(252, TXXS_Y)
    #横风向风振

    #考虑横风向风振
    test2.SetSParInt(207, 1)
    #截面形状
    test2.SetSParInt(228, 22804)
    #圆形截面_结构二阶平动周期
    test2.SetSParFloat(231, 0.4)
    #保存前处理参数
    test2.SParaSave()

"""多塔划分_案例使用的模型参见ydb文件夹中的dt.ydb"""
def test_dthf():
    info = YJKSPrePy_Tower()
    info.Load()
    info.AutoGen()
    res = info.GetTower(2, 1)
    #修改1塔2层
    res.cCL = 60
    poly = res._poly
    poly[0] = (115.0, 2840.0)
    poly[1] = (115, 8840)
    poly[2] = (6115, 8840)
    poly[3] = (6115, 2840)

    info.AddTower(res,2)
    #新增2塔2层
    res.no = 2
    poly[0] = (12115, 2840)
    poly[1] = (12115, 8840)
    poly[2] = (18115, 8840)
    poly[3] = (18115, 2840)
    info.AddTower(res,2)
    info.Save()

"""根据超限信息获取构件的全楼ID并转换为建模模块对应的ID,在设计结果模块使用，搭配yjk文件夹里的超限项目使用"""
def test_LimitInf():
    # 获取所有梁的全楼编号
    test1 = YJKSPrePy()
    # 总层数
    NZRC = test1.NZRC()

    LimitIdList =[]
    LimitInfoList = {}
    for i in range(1,NZRC+1):
        iFlr = i
        beamNum = test1.NBeam(iFlr)
        idFlrBeams =test1.FlrBeams(iFlr,beamNum)

        # 查询超限构件
        YJKSDsnDataPy.dsnInitData()
        YJKSDsnDataPy.dsnReadFloorPJ(i)    # 设置当前楼层，程序将读取该楼层构件索引，并生成该层构件配筋信息
        for j in range(beamNum):
            是否超限 = YJKSDsnDataPy.dsnComHasLimitInf(i, PostGjKind.COM_BEAM, idFlrBeams[j])
            if (是否超限):
                LimitIdList.append(idFlrBeams[j])
                nNum, LimitInf=YJKSDsnDataPy.dsnGetComTotLimitInf(i, PostGjKind.COM_BEAM, idFlrBeams[j])
                # LimitInf中1代表LIMIT_BEAM_V（梁截面抗剪超限）、4代表LIMIT_BEAM_ASMAXUP（梁上截面最大配筋率超限），详见设计结果宏定义说明文档
                LimitInfoList[idFlrBeams[j]]=LimitInf

    # 全楼ID转建模ID
    my = Hi_AddToAndReadYjk()
    ids = set()
    for i in range(len(LimitIdList)):
        No = test1.BeamONO(LimitIdList[i])
        flrNo = test1.BeamOFlr(LimitIdList[i])
        ID_Model = my.ReadIdByNO(GjKind.IDK_BEAM, No, flrNo)
        ids.add(ID_Model)
    #show_dict(ids)

"""设置全楼温差"""
def test_Temperature():
    temperature = YJKSPrePy_Temperature()
    t1= 10.1
    t2 = 20.2
    temperature.UniTemp(t1, t2)
    temperature.Save()

"""脚本模式不弹窗完成计算"""
def test_DsnCal():
    YJKSUI = YJKSUIPy()
    YJKSCommand = YJKSCommandPy()
    #切换标签栏至轴线网格
    YJKSUI.QSetCurrentRibbonLabel("IDModule_Axis")
    YJKSUI.QSetRunScript(1)
    #工程修复、保存
    YJKSCommand.RunCommand("yjk_repairex")
    YJKSCommand.RunCommand("yjk_save")
    #从建模模块切换到前处理模块需要执行的命令
    YJKSCommand.RunCommand("yjk_setlayersupport")
    YJKSCommand.RunCommand("yjkspre_genmodrel")
    YJKSCommand.RunCommand("yjktransload_tlplan")
    YJKSCommand.RunCommand("yjktransload_tlvert")
    #切换标签栏至前处理
    YJKSUI.QSetCurrentRibbonLabel("IDSPRE_ROOT")
    #设计计算
    YJKSCommand.RunCommand("yjkdesign_dsncalculating_all")
    #切换标签栏至设计结果
    YJKSUI.QSetCurrentRibbonLabel("IDDSN_DSP")

"""统计设计结果内容"""
def test_dsnInfo():
    def console(infor):# 日志文件生成
        script_path = os.path.abspath(__file__)  # 获取当前脚本的绝对路径
        script_dir = os.path.dirname(script_path)  # 获取当前脚本所在的目录
        file_path = script_dir +'\\'+filename + '.txt'
        file = open(file_path, 'a')
        file.writelines([infor+ '\n'])
        file.close()
    # 由CToSDesign获取构件全楼编号
    filename="dsnInfo"
    CToSDesign = YJKSPrePy()
    # 标准层编号
    iFlr = 1
    ColumnNum = CToSDesign.NColumn(iFlr)
    str='第一层柱数：%d'%(ColumnNum)
    console(str)
    # 第一层柱的全楼编号
    idFlrColumns= CToSDesign.FlrColumns(iFlr,ColumnNum)
    # 统计总节点
    NodeNum = CToSDesign.NJD()
    str='模型总节点数：%d'%(NodeNum)
    console(str)
    # 统计总层数
    FlrNum = CToSDesign.NZRC()
    str='模型总层数：%d'%(FlrNum)
    console(str)

    xing = '*'*50
    title = xing + "层刚度信息统计" + xing
    console(title)         # 输出title内容到指定txt文件
    for i in range(FlrNum):
        dSD, dSC=YJKSDsnDataPy.dsnGetFlrStiff(i + 1, 1)
        str='层号：%d,  塔号:%d,  X、Y方向层间剪力与层间位移之比:%f,%f,  X、Y方向层剪切刚度:%f,%f'%(i+1,1,dSD[0], dSD[1], dSC[0], dSC[1])
        console(str)
    console("")

    title = xing + "楼层受剪承载力信息统计" + xing
    console(title)
    for i in range(FlrNum):
        dSC=YJKSDsnDataPy.dsnGetFlrShearCapacity(i + 1, 1)
        str = '层号：%d,  塔号:%d,  X、Y方向受剪承载力:%f,%f'%(i+1,1,dSC[0], dSC[1])
        console(str)
    console("")

    title = xing + "调整前首层柱标准内力" + xing
    console(title)
    for i in range(ColumnNum):
        nSect, Force=YJKSDsnDataPy.dsnGetColumnStdForce(iFlr, idFlrColumns[i], 1, 1)
        str='层号:%d,  柱全楼编号:%d,  截面数量:%d, 工况号：%d 内力: X弯矩:%f， Y弯矩:%f， X剪力:%f， Y剪力:%f， 轴力:%f， 扭矩:%f'%(iFlr,idFlrColumns[i],nSect, 1, Force[1][0], Force[1][1], Force[1][2], Force[1][3], Force[1][4], Force[1][5])
        console(str)

def pyyjks():
    test_refresh()
    # test_flrInfo()
    # test_pre()
    # test_dthf()
    # test_LimitInf()
    # test_Temperature()
    # test_DsnCal()
    # test_dsnInfo()
    #show_single_content("OK")