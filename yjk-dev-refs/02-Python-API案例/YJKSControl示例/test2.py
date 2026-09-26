import YJKSControl
from YJKSControl import RunCmd

"""该案例为对模型梁板柱墙钢筋的统计"""

RunCmd("SetCurrentLabel","IDDTL_DETAIL_SLAB")#切换至板模块
RunCmd("stdslab_redrawnceng","")#绘新图
RunCmd("stdslab_opendrawplan","")#打开旧图
RunCmd("stdslab_autocal","")#计算
RunCmd("stdslab_dispcal","")#计算结果
RunCmd("stdslab_quantity","")#本层楼板钢筋统计
RunCmd("stdslab_autostatstl","")#全楼楼板钢筋统计

RunCmd("SetCurrentLabel","IDDTL_DETAIL_BEAM")#切换至梁模块
RunCmd("dtlrc_newbeamplanload","")#由现有配筋结果绘新图
RunCmd("dtlrc_beamtext","")#单跨计算书
RunCmd("dtlrc_statbeam","")#本层梁钢筋统计
RunCmd("dtlrc_statbuildingbeamsteelspecexcel","")#全楼梁钢筋统计（按钢筋规格和类别）

RunCmd("SetCurrentLabel","IDDTL_DETAIL_COLUMN")#切换至柱模块
RunCmd("dtlrc_colmerge","")#由现有配筋结果绘新图
RunCmd("dtlrc_colsumgj","")#全楼柱钢筋统计
RunCmd("dtlrc_ssce","")#全楼柱钢筋统计excel

RunCmd("SetCurrentLabel","IDDTL_DETAIL_WALL")#切换至墙模块
RunCmd("dtlrc_wallplanregennew","")#重新归并选筋并绘新图
RunCmd("dtlrc_stwbarj","")#本层墙钢筋统计
RunCmd("dtlrc_ssw","")#全楼墙钢筋统计文本
RunCmd("dtlrc_sswe","")#全楼墙钢筋统计excel

