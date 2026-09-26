# 导入命名空间
from YJKAPI import *

#测试修改节点,配合test01使用
def reflec_test01():
    model = getDbModelData()
    node = model.m_Joint[0]
    updateInfo = Hi_UpdateInfo()
    updateInfo.unionID = model.unionID
    for i in range(10):
        updateInfo.Clear()
        node.X -= 1000
        updateInfo.ModifyObj(node)
        transUpdateInfo(updateInfo)
    for i in range(10):
        updateInfo.Clear()
        node.X += 1000
        updateInfo.ModifyObj(node)
        transUpdateInfo(updateInfo)

#框架的新增及删除(梁、柱、墙、墙洞、杆件)，配合test02使用
def reflec_test02():
    def DeleteMember(span_pre, spans_cur):
        updateInfo = Hi_UpdateInfo()
        for i in range(spans_cur,span_pre):
            updateInfo.DeleteObj(nodelist[i][0])
            updateInfo.DeleteObj(nodelist[i][1])
        transUpdateInfo(updateInfo)

    def AddMember(span_pre, spans_cur):
        node2grid_X = []
        node2grid_Y = []

        #新生成节点、柱
        for i in range(span_pre,spans_cur):
            node1 = dataFunc.Joint_Generate(stdFlrID, i * 5000, 0)
            node2 = dataFunc.Joint_Generate(stdFlrID, i * 5000, 5000)
            if (len(nodelist) > 0):
                #X向
                node2grid_X.append([node1, nodelist[len(nodelist) - 1][0]])
                node2grid_X.append([node2, nodelist[len(nodelist) - 1][1]])
            #Y向
            node2grid_Y.append([node1, node2])
            nodelist.append([node1, node2])
            #布置柱
            dataFunc.column_arrange(node1, defcol)
            dataFunc.column_arrange(node2, defcol)

        #新生成网格、梁、杆件、墙、墙洞
        #X向
        for i in range(len(node2grid_X)):
            axis = dataFunc.Axis_Generate(stdFlrID, node2grid_X[i][0].ID, node2grid_X[i][1].ID)
            grid = dataFunc.Grid_Generate(stdFlrID, node2grid_X[i][0].ID, node2grid_X[i][1].ID, axis.ID)
            #布置墙及墙洞
            dataFunc.wall_arrange(grid, wallSect)
            dataFunc.wallhole_arrange(grid, wallHoleDef)
            dataFunc.beam_arrange(grid, defbeam)

        #Y向
        for i in range(spans_cur - span_pre):
            dataFunc.brace_arrange(node2grid_Y[i][0], node2grid_Y[i][1], braceSect, 0, 0, 0, 0, 0, 1)
            dataFunc.brace_arrange(node2grid_Y[i][0], node2grid_Y[i][1], braceSect, 0, 0, 1, 0, 0, 0)
            axis = dataFunc.Axis_Generate(stdFlrID, node2grid_Y[i][0].ID, node2grid_Y[i][1].ID)
            grid = dataFunc.Grid_Generate(stdFlrID, node2grid_Y[i][0].ID, node2grid_Y[i][1].ID, axis.ID)
            #布置梁
            dataFunc.beam_arrange(grid, defbeam)

        dataFunc.DbModel_Assign()
        updateInfo = dataFunc.GetUpdateInfo()
        transUpdateInfo(updateInfo)

    reflec_Def()
    model = getDbModelData()
    stdFlrID = model.m_StdFlr[0].ID
    defcol = model.m_ColSect[0]
    defbeam = model.m_BeamSect[0]
    braceSect = model.m_BraceSect[0]
    wallSect = model.m_WallSect[0]
    wallHoleDef = model.m_WallHoleDef[0]

    nodelist = []

    spans = [ 2, 4, 6, 8, 6, 4, 2, 0 ]
    dataFunc = DataFunc()
    unionID = getUnionID()
    dataFunc.InitForLink(unionID)

    for i in range(len(spans)):
        spans_cur = spans[i]
        span_pre = len(nodelist)
        if (spans_cur > span_pre):
            #新增
            AddMember(span_pre, spans_cur)
        elif (spans_cur < span_pre):
            #减少
            DeleteMember(span_pre, spans_cur)
        else:
            pass
            #不增加也不减少

def refresh_test01():
    dataFunc = DataFunc()
    #标准层
    StdFlr = dataFunc.StdFlr_Generate(3900)
    para = BzcPara()
    str = para.GetValString()
    #截面定义
    defcol = dataFunc.ColSect_Def(6, 1, "400,400")
    defbeam1 = dataFunc.BeamSect_Def(6, 1, "250,600")
    defbeam2 = dataFunc.BeamSect_Def(6, 1, "200,400")
    #荷载定义
    beamload1 = dataFunc.Load_Def(12, "1.00,9.60")
    beamload2 = dataFunc.Load_Def(12, "1.00,5.50")
    #生成节点
    nodelist = []
    originpos = [0, 0]
    xspans = [originpos[0], 3900, 3900, 3900, 3900, 3900, 3900 ]
    yspans = [originpos[1], 6700, 5300]
    nodelist = dataFunc.node_generate(xspans, yspans, StdFlr)
    #生成网格
    gridlist = []
    gridlist = dataFunc.grid_generate(nodelist, 0, 1)
    #布置框架梁柱及荷载
    dataFunc.column_arrange(nodelist, defcol)
    beam_list = []
    beam_list = dataFunc.beam_arrange(gridlist, defbeam1)
    dataFunc.load_arrange(beam_list, beamload1)
    gridlist = dataFunc.grid_generate(nodelist, 1, 0)
    beam_list = dataFunc.beam_arrange(gridlist, defbeam2)
    dataFunc.load_arrange(beam_list, beamload2)
    #布置次梁
    xspans = [originpos[0], 3900, 3900, 3900, 3900, 3900, 3900]
    yspans = [5200]
    nodelist = dataFunc.node_generate(xspans, yspans, StdFlr)
    gridlist = dataFunc.grid_generate(nodelist, 1, 0)
    beam_list = dataFunc.beam_arrange(gridlist, defbeam2)
    dataFunc.load_arrange(beam_list, beamload2)

    #标准层复制
    dataFunc.Floors_Assemb(0, StdFlr, 6, 3600)
    #提交建模数据
    dataFunc.DbModel_Assign()
    model = dataFunc.GetDbModelData()
    transModel(model)

def getDbModelData():
    YJKSControl.RunCmd("yjks_pyload", r"E:\MyProject\9.python_api_new中文\example\案例15_联动\MyHelper.py","test_readModel")
    link = Link2YJK.Instance
    result = link.GetIPCdataWrapper(Hi_DbModelData)
    return result

def transUpdateInfo(updateInfo):
    link = Link2YJK.Instance
    link.LinkPrepareWrapper(updateInfo, Hi_UpdateInfo)
    YJKSControl.RunCmd("yjks_pyload", r"E:\MyProject\9.python_api_new中文\example\案例15_联动\MyHelper.py","test_ipcreflect")
    # YJKSControl.RunCmd("test_ipcreflect", "")

def transModel(model):
    link = Link2YJK.Instance
    link.LinkPrepareWrapper(model, Hi_DbModelData)
    YJKSControl.RunCmd("yjks_pyload", r"E:\MyProject\9.python_api_new中文\example\案例15_联动\MyHelper.py","test_ipcrefresh")
    # YJKSControl.RunCmd("test_ipcreflect", "")

def getUnionID():
    YJKSControl.RunCmd("yjks_pyload", r"E:\MyProject\9.python_api_new中文\example\案例15_联动\MyHelper.py","test_updateUnionID")
    link = Link2YJK.Instance
    return link.GetIPCUnionID()

def reflec_Def():
    unionID = getUnionID()
    dataFunc = DataFunc()
    dataFunc.InitForLink(unionID)
    #截面定义
    defbeam1 = dataFunc.BeamSect_Def(6, 26, "", "H98X99X5X7")
    defcol = dataFunc.ColSect_Def(6, 1, "401,401", "col_400*400")
    defbrace = dataFunc.BraceSect_Def(5, 1, "351,501", "brace_350*500")
    defWall = dataFunc.WallSect_Def(6, 1, 201, "wall_201")
    defWallHole = dataFunc.WallHoleDef(1500, 2000)
    dataFunc.ColSect_Def(5, 303, "", "L40X2.0") #型钢截面
    dataFunc.DbModel_Assign()
    updateInfo = dataFunc.GetUpdateInfo()
    transUpdateInfo(updateInfo)

def main():
    # reflec_test01()
    # reflec_test02()
    refresh_test01()

if __name__ == "__main__":
    main()