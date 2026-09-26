using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.IO;

using MiddleTrans;

//这是一个向YJK平台注册命令的案例，用户可通过一个dll向YJK平台完成多个命令的注册（适用于5.1及之后版本）
//一、将更新的dll替换到YJK对应安装路径后，执行yjks_csload,加载写好的dll文件。
//二、命令行弹出加载成功后，即可调用写好的命令。
//三、对于用户开发阶段，更新dll之后，只需执行yjks_csreload即可完成dll的更新。

namespace UserCode
{
    public class MyClass
    {
        [CommandMethod("Test_Func1")]
        public void Func1()
        {
            run();
        }
        public void run()
        {
            ClrYJKSUI YJKSUI = new ClrYJKSUI();
            ClrYJKSCommand YJKSCommand = new ClrYJKSCommand();
            //切换标签栏至轴线网格
            YJKSUI.CsQSetCurrentRibbonLabel("IDModule_Axis");
            YJKSUI.CsQRunCommandEx("yjk_importydb", "D:/5.C#二次开发/MyExample/ydb/kj.ydb", 0);
            //工程修复、保存
            YJKSCommand.CsRunCommand("yjk_setlayersupport");
            YJKSCommand.CsRunCommand("yjk_repairex");
            YJKSCommand.CsRunCommand("yjk_save");
            //切换标签栏至前处理
            YJKSUI.CsQSetCurrentRibbonLabel("IDSPRE_ROOT");
            //设计计算
            YJKSCommand.CsRunCommand("yjkdesign_dsncalculating_all");
            //切换标签栏至设计结果
            YJKSUI.CsQSetCurrentRibbonLabel("IDDSN_DSP");
            //设计结果信息统计
            DesignData();
        }

        public void DesignData()
        {
            //由CToSDesign获取构件全楼编号
            Hi_CToSDesign CToSDesign = new Hi_CToSDesign();
            //标准层编号
            int iFlr = 1;
            int ColumnNum = CToSDesign.NColumn(iFlr);
            console("第一层柱数：" + ColumnNum.ToString());
            //第一层柱的全楼编号
            int[] idFlrColumns = new int[ColumnNum];
            CToSDesign.FlrColumns(iFlr, idFlrColumns);
            //统计总节点
            int NodeNum = CToSDesign.NJD();
            console("模型总节点数：" + NodeNum.ToString());
            //统计总层数
            int FlrNum = CToSDesign.NZRC();
            console("模型总层数：" + FlrNum.ToString());

            string xing = new String('*', 50);
            string title = xing + "层刚度信息统计" + xing;
            console(title);
            for (int i = 0; i < FlrNum; ++i)
            {
                double[] dSD = new double[2];
                double[] dSC = new double[2];
                Hi_DesignData.dsnGetFlrStiff(i + 1, 1, dSD, dSC);
                string str = String.Format("层号：{0}， 塔号：{1}， X、Y方向层间剪力与层间位移之比:{2}，{3}， X、Y方向层剪切刚度:{4}，{5}", i + 1, 1, dSD[0], dSD[1], dSC[0], dSC[1]);
                console(str);
            }
            console("");

            title = xing + "楼层受剪承载力信息统计" + xing;
            console(title);
            for (int i = 0; i < FlrNum; ++i)
            {
                double[] dSC = new double[2];
                Hi_DesignData.dsnGetFlrShearCapacity(i + 1, 1, dSC);
                string str = String.Format("层号：{0}， 塔号：{1}， X、X、Y方向受剪承载力:{2}，{3}", i + 1, 1, dSC[0], dSC[1]);
                console(str);
            }
            console("");

            title = xing + "调整前首层柱标准内力" + xing;
            console(title);
            for (int j = 0; j < ColumnNum; ++j)
            {
                int nSect = 0;
                float[,] Force = new float[2, 6];
                Hi_DesignData.dsnGetColumnStdForce(iFlr, idFlrColumns[j], 1, 1, ref nSect, Force);
                string str = String.Format("层号：{0}， 柱全楼编号：{1}，截面数量：{2}，工况号：{3}， 内力: X弯矩:{4}， Y弯矩:{5}， X剪力:{6}， Y剪力:{7}， 轴力:{8}， 扭矩:{9}", iFlr, idFlrColumns[j], nSect, 1, Force[1, 0], Force[1, 1], Force[1, 2], Force[1, 3], Force[1, 4], Force[1, 5]);
                console(str);
            }

        }

        public void console(string info)
        {
            File.AppendAllText("D:\\DesignInfo.txt", "\r\n" + info);
        }
        
    }
}
