using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

using System.Runtime.InteropServices;
using YJKIPC;
namespace ConsoleApp10
{
    class yjkipc
    {
        //从启动yjk进程到自动化计算的流程控制
        static void test01()
        {
            ControlConfig config = new ControlConfig();
            config.Version = "8.0.0";
            config.Invisible = false;   //如果启动静默计算需要调用exit命令，不然yjk进程会一直存在。

            YJKSControl.initConfig(config);
            string str = YJKSControl.RunYJK(@"E:\专业软件\YJK8.0\1128\Setup_YJKS_All_8.0.0X64\YJKS_8_0_0\yjks.exe");
            Console.WriteLine(str);
            //YJKSControl.RunCmd("UINew", @"C:\Users\10497\Desktop\用户问题\99.UINew\1.yjk");
            YJKSControl.RunCmd("UIOpen", @"E:\MyProject\16.智能辅助设计\YJK案例\测试模型\04自测验证模型\框剪-截面\1.yjk");
            //YJKSControl.RunCmd("yjk_importydb", @"C:\Users\10497\Desktop\例子\test\pymodel1.ydb");
            YJKSControl.RunCmd("yjk_repair", "");
            YJKSControl.RunCmd("yjk_save", "");
            YJKSControl.RunCmd("yjk_formnode", "2");  //根据实际情况是否使用，会合并间距小于50的节点
            YJKSControl.RunCmd("yjk_formslab_alllayer", "");
            YJKSControl.RunCmd("yjk_setlayersupport", "");
            YJKSControl.RunCmd("yjkspre_genmodrel", "");
            YJKSControl.RunCmd("yjktransload_tlplan", "");
            YJKSControl.RunCmd("yjktransload_tlvert", "");
            YJKSControl.RunCmd("SetCurrentLabel", "IDSPRE_ROOT");
            YJKSControl.RunCmd("yjkdesign_dsncalculating_all", "");
            YJKSControl.RunCmd("SetCurrentLabel", "IDDSN_DSP");
            //YJKSControl.RunCmd("exit", "");
            Console.WriteLine("运行完成！");
            Console.ReadLine();
        }

        // 在已启动8.0版本YJK的情况下在软件中输入命令yjksipccontrol，之后运行test04即可（如果开启了多个yjks需要手动选择匹配的yjk进程）
        static void test04()
        {
            ControlConfig config = new ControlConfig();
            config.Version = "8.0.0";
            config.Invisible = false;
            config.Pid = -1; //根据用户自身的需求看是否设置Pid，若没有设置之后会弹一次窗口让用户指定
            var configRes = YJKSControl.initConfig(config);
            Console.WriteLine(configRes);

            YJKSControl.RunCmd("yjk_repair", "");
            YJKSControl.RunCmd("yjk_save", "");
            YJKSControl.RunCmd("yjk_formnode", "2");  //根据实际情况是否使用，会合并间距小于50的节点
            YJKSControl.RunCmd("yjk_formslab_alllayer", "");
            YJKSControl.RunCmd("yjk_setlayersupport", "");
            YJKSControl.RunCmd("yjkspre_genmodrel", "");
            YJKSControl.RunCmd("yjktransload_tlplan", "");
            YJKSControl.RunCmd("yjktransload_tlvert", "");
            YJKSControl.RunCmd("SetCurrentLabel", "IDSPRE_ROOT");
            YJKSControl.RunCmd("yjkdesign_dsncalculating_all", "");
            YJKSControl.RunCmd("SetCurrentLabel", "IDDSN_DSP");
            //YJKSControl.RunCmd("exit", "");
            Console.WriteLine("运行完成！");
            Console.ReadLine();
        }

        static void test02()
        {
            YJKSControl.RunCmd("SetCurrentLabel", "IDDTL_DETAIL_SLAB");//切换至板模块
            YJKSControl.RunCmd("stdslab_redrawnceng", "");//绘新图
            YJKSControl.RunCmd("stdslab_opendrawplan", "");//打开旧图
            YJKSControl.RunCmd("stdslab_autocal", "");//计算
            YJKSControl.RunCmd("stdslab_dispcal", "");//计算结果
            YJKSControl.RunCmd("stdslab_quantity", "");//本层楼板钢筋统计
            YJKSControl.RunCmd("stdslab_autostatstl", "");//全楼楼板钢筋统计

            YJKSControl.RunCmd("SetCurrentLabel", "IDDTL_DETAIL_BEAM");//切换至梁模块
            YJKSControl.RunCmd("dtlrc_newbeamplanload", "");//由现有配筋结果绘新图
            YJKSControl.RunCmd("dtlrc_beamtext", "");//单跨计算书
            YJKSControl.RunCmd("dtlrc_statbeam", "");//本层梁钢筋统计
            YJKSControl.RunCmd("dtlrc_statbuildingbeamsteelspecexcel", "");//全楼梁钢筋统计（按钢筋规格和类别）

            YJKSControl.RunCmd("SetCurrentLabel", "IDDTL_DETAIL_COLUMN");//切换至柱模块
            YJKSControl.RunCmd("dtlrc_colmerge", "");//由现有配筋结果绘新图
            YJKSControl.RunCmd("dtlrc_colsumgj", "");//全楼柱钢筋统计
            YJKSControl.RunCmd("dtlrc_ssce", "");//全楼柱钢筋统计excel

            YJKSControl.RunCmd("SetCurrentLabel", "IDDTL_DETAIL_WALL");//切换至墙模块
            YJKSControl.RunCmd("dtlrc_wallplanregennew", "");//重新归并选筋并绘新图
            YJKSControl.RunCmd("dtlrc_stwbarj", "");//本层墙钢筋统计
            YJKSControl.RunCmd("dtlrc_ssw", "");//全楼墙钢筋统计文本
            YJKSControl.RunCmd("dtlrc_sswe", "");//全楼墙钢筋统计excel


            Console.WriteLine("运行完成！");
            Console.ReadLine();
        }

        static void test03()
        {
            YJKSControl.RunCmd("yjk_opennew", @"C:\Users\10497\Desktop\例子\test\1");
            // 创建节点
            YJKSControl.RunCmd("yjk_node", "p!(0, -3900, 0),p!(3900, -3900, 0),p!(3900, -7800, 0),p!(0, -7800, 0),k(VK_RBUTTON)");
            YJKSControl.RunCmd("yjk_node", "p!(9500, -3700, 0), p!(12000, -7500, 0), p!(13000, -7600, 0),k(VK_RBUTTON)");
            YJKSControl.RunCmd("yjk_node", "p!(18000, -6000, 0.000000),k(VK_RBUTTON)");
            YJKSControl.RunCmd("yjk_node", "p!(23000, -3500, 0), p!(27000, -8000, 0),k(VK_RBUTTON)");
            // 创建直线
            YJKSControl.RunCmd("yjk_line2ps", "p!(0, -3900, 0), p!(3900, -3900, 0), p!(3900, -7800, 0), p!(0, -7800, 0), p!(0, -3900, 0),k(VK_RBUTTON)");
            // 创建圆弧
            YJKSControl.RunCmd("yjk_arc3p", "p!(9500, -3700, 0), p!(12000, -7500, 0), p!(13000, -7600, 0),k(VK_RBUTTON)");
            // 创建圆
            YJKSControl.RunCmd("yjk_circle", "p!(18000, -6000, 0.000000), d(2000),k(VK_RBUTTON)");
            // 创建矩形
            YJKSControl.RunCmd("yjk_rectangle", "p!(23000, -3500, 0), p!(27000, -8000, 0),k(VK_RBUTTON)");

            Console.WriteLine("运行完成！");
            Console.ReadLine();
        }

        static void Main(string[] args)
        {
            test04();
        }
    }
}
