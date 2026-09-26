import YJKSControl
from YJKSControl import RunCmd

"""该例为通过外部调用直观地创建节点、轴线、圆弧、圆及矩形等几何的案例，让用户能在外部
   实现复杂几何形体的绘制，省去繁重的手动绘制调整修改"""


RunCmd("yjk_opennew",r"C:\Users\10497\Desktop\例子\test\1")
#创建节点
RunCmd("yjk_node","p!(0, -3900, 0),p!(3900, -3900, 0),p!(3900, -7800, 0),p!(0, -7800, 0),k(VK_RBUTTON)")
RunCmd("yjk_node","p!(9500, -3700, 0), p!(12000, -7500, 0), p!(13000, -7600, 0),k(VK_RBUTTON)")
RunCmd("yjk_node","p!(18000, -6000, 0.000000),k(VK_RBUTTON)")
RunCmd("yjk_node","p!(23000, -3500, 0), p!(27000, -8000, 0),k(VK_RBUTTON)")
#创建直线
RunCmd("yjk_line2ps","p!(0, -3900, 0), p!(3900, -3900, 0), p!(3900, -7800, 0), p!(0, -7800, 0), p!(0, -3900, 0),k(VK_RBUTTON)")
#创建圆弧
RunCmd("yjk_arc3p","p!(9500, -3700, 0), p!(12000, -7500, 0), p!(13000, -7600, 0),k(VK_RBUTTON)")
#创建圆
RunCmd("yjk_circle","p!(18000, -6000, 0.000000), d(2000),k(VK_RBUTTON)")
#创建矩形
RunCmd("yjk_rectangle","p!(23000, -3500, 0), p!(27000, -8000, 0),k(VK_RBUTTON)")
