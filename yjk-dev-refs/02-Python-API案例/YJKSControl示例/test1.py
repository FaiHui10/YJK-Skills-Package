import time
import threading
from YJKSControl import RunCmd
from atexit import register
import YJKSControl

"""该例演示通过脚本控制YJK，需要安装configparser模块和atexit模块，
安装完成后在如下代码中修改yjk的路径及模型文件及ydb的路径后即可运行，
运行的说明及命令的说明可参考相关文件"""

# 对单独命令进行调用可取消下面两句，但需要手动修改
# C:\ProgramData\yjkSoft\YJKS5.1\YJKS\Config.ini中YJKSControl下的Flag为True，
# 启动YJK后即可运行脚本，不需要YJKSControl后再将Flag改成False
YJKSControl.init(r"E:\专业软件\YJK5.1\5.1_1018\yjks.exe","6.1")
register(YJKSControl.exit)

RunCmd("UIOpen",r"C:\Users\10497\Desktop\例子\test\1.yjk")
RunCmd("yjk_importydb",r"C:\Users\10497\Desktop\例子\test\pymodel.ydb")
RunCmd("yjk_repair","")
RunCmd("yjk_save","")
RunCmd("yjk_formnode","2")      #根据实际情况是否使用，会合并间距小于50的节点
RunCmd("yjk_formslab_alllayer","")
RunCmd("yjk_setlayersupport","")
RunCmd("yjkspre_genmodrel","")
RunCmd("yjktransload_tlplan","")
RunCmd("yjktransload_tlvert","")
RunCmd("SetCurrentLabel","IDSPRE_ROOT")
RunCmd("yjkdesign_dsncalculating_all","")
RunCmd("SetCurrentLabel","IDDSN_DSP")