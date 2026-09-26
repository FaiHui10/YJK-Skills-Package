using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.IO;

using APIData;
using CsToYjk;
using DataFuncApplication;
using MiddleTrans;


//这是一个向YJK平台注册命令的案例，用户可通过一个dll向YJK平台完成多个命令的注册（适用于5.1及之后版本）
//一、将更新的dll替换到YJK对应安装路径后，执行yjks_csload,加载写好的dll文件。
//二、命令行弹出加载成功后，即可调用写好的命令。
//三、对于用户开发阶段，更新dll之后，只需执行yjks_csreload即可完成dll的更新。

namespace UserCode
{
    public class MyClass
    {
        //注册一个名称为Test_Func1的命令。
        //调用后弹出一个窗口，显示"this is fun1"
        [CommandMethod("Test_Func1")]
        public void Func1()
        {
            MessageBox.Show("this is func1");
        }
        //注册一个名称为Test_Func2的命令。
        //弹出一个窗口，显示"this is fun2"
        [CommandMethod("Test_Func2")]
        public void Func2()
        {
            MessageBox.Show("this is func2");

        }
        //注册一个名称为Test_Func3的命令。
        //在yjk命令行弹出信息内容
        [CommandMethod("Test_Func3")]
        public void Func3()
        {
            ClrYJKSCommand YJKSCommand = new ClrYJKSCommand();
            string str = "this is func3";
            YJKSCommand.RefPrint(str);
        }
        //注册一个名称为Test_Func4的命令。
        //运行yjk自带修复命令
        [CommandMethod("Test_Func4")]
        public void Func4()
        {
            ClrYJKSCommand YJKSCommand = new ClrYJKSCommand();
            YJKSCommand.CsRunCommand("yjk_repairex");
        }

        //注册一个名称为Test_Pre的命令。
        //设置前处理的计算参数
        [CommandMethod("Test_Pre")]
        public void Func5()
        {
            Hi_JSCS test2 = new Hi_JSCS();

            //风荷载信息_基本参数
            test2.SetSParInt(212, 3);

            //体型分段数&&迎风面系数&&背风面系数
            int[] TXFD = new int[4];
            //体型分段数
            TXFD[0] = 3;
            //第一段最高层号
            TXFD[1] = 2;
            //第二段最高层号
            TXFD[2] = 4;
            //第三段最高层号
            TXFD[3] = 6;
            test2.SetSParIntArray(213, TXFD);


            //风荷载体型系数_X向
            float[] TXXS_X = new float[13];
            //第一段X挡风&&X迎风面&&X背风面&&X侧风面
            TXXS_X[0] = 13f;
            TXXS_X[1] = 0.9f;
            TXXS_X[2] = 0.85f;
            TXXS_X[3] = -0.55f;
            TXXS_X[4] = 0.1f;
            //第二段
            TXXS_X[5] = 0.9f;
            TXXS_X[6] = 0.85f;
            TXXS_X[7] = -0.55f;
            TXXS_X[8] = 0.1f;
            //第三段
            TXXS_X[9] = 0.9f;
            TXXS_X[10] = 0.85f;
            TXXS_X[11] = -0.55f;
            TXXS_X[12] = 0.1f;

            test2.SetSParFloatArray(214, TXXS_X);

            //风荷载体型系数_Y向
            float[] TXXS_Y = new float[13];

            //第一段Y挡风&&Y迎风面&&Y背风面&&Y侧风面
            TXXS_Y[0] = 13;
            TXXS_Y[1] = 0.9f;
            TXXS_Y[2] = 0.85f;
            TXXS_Y[3] = -0.55f;
            TXXS_Y[4] = 0.1f;
            //第二段
            TXXS_Y[5] = 0.9f;
            TXXS_Y[6] = 0.85f;
            TXXS_Y[7] = -0.55f;
            TXXS_Y[8] = 0.1f;
            //第三段
            TXXS_Y[9] = 0.9f;
            TXXS_Y[10] = 0.85f;
            TXXS_Y[11] = -0.55f;
            TXXS_Y[12] = 0.1f;

            test2.SetSParFloatArray(252, TXXS_Y);

            //横风向风振

            //考虑横风向风振
            test2.SetSParInt(207, 1);
            //截面形状
            test2.SetSParInt(228, 22804);
            //圆形截面_结构二阶平动周期
            test2.SetSParFloat(231, 0.4f);
            //保存前处理参数
            test2.SParaSave();
        }

        //注册一个名称为Test_DsnCal的命令。
        //完成从导入ydb到计算完成到设计结果信息统计的功能
        [CommandMethod("Test_DsnCal")]
        public void Func6()
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

            void DesignData()
            {
                //由CToSDesign获取构件全楼编号
                Hi_CToSDesign CToSDesign = new Hi_CToSDesign();
                //标准层编号
                int iFlr = 1;
                int ColumnNum = CToSDesign.NColumn(iFlr);
                console("第一层柱数：" + ColumnNum.ToString());
                //第一层柱的全楼编号
                var idFlrColumns= CToSDesign.FlrColumns(iFlr);
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

            void console(string info)
            {
                File.AppendAllText("D:\\DesignInfo.txt", "\r\n" + info);
            }
        }
        //设置全楼温差
        [CommandMethod("Test_Temperature")]
        public void Func15()
        {
            Hi_Temperature temperature = new Hi_Temperature();
            float t1= 10.1F;
            float t2 = 20.2F;
            temperature.UniTemp(t1, t2);
            temperature.Save();
        }

    }

}
