from YJKAPI import *
        
def test_readModel():
    yjkscmd = YJKSCommandPy()
    yjkscmd.RunCommand("yjk_save")
    my = Hi_AddToAndReadYjk()
    model = my.ReadFromYJK()
    link = Link2YJK.Instance
    link.LinkPrepare(model)

def test_ipcreflect():
    my = Hi_AddToAndReadYjk()
    my.RestCadInfo()
    my.ReadBzcAndProj()
    link = Link2YJK.Instance
    model = link.GetIPCdataWrapper(Hi_UpdateInfo)
    # model = link.GetIPCdata<Hi_UpdateInfo>()
    #增加到yjk
    my.ReflecToYJK(model)

def test_ipcrefresh():
    link = Link2YJK.Instance
    # model = link.GetIPCdata<Hi_DbModelData>()
    model = link.GetIPCdataWrapper(Hi_DbModelData)
    my = Hi_AddToAndReadYjk(model)
    #增加到yjk
    my.RefreshToYJK()

def test_updateUnionID():
    my = Hi_AddToAndReadYjk()
    my.RestCadInfo()
    unionID = my.GetUnionID()
    link = Link2YJK.Instance
    link.LinkPrepare(unionID)