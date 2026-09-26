using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.Drawing;
using MiddleTrans;
using System.IO;

using APIData;
using CsToYjk;
using DataFuncApplication;

using System.Data;
using System.Data.Common;
using System.Data.SQLite;

//这是一个向YJK平台注册命令的案例，用户可通过一个dll向YJK平台完成多个命令的注册（更新于5.1版本）
//一、将更新的dll替换到YJK对应安装路径后，执行yjks_csload,加载写好的dll文件。
//二、命令行弹出加载成功后，即可调用写好的命令。
//三、对于用户开发阶段，更新dll之后，只需执行yjks_csreload即可完成dll的更新。

namespace UserCode
{
    public class testClass
    {
        public void help()
        {
            string sqlCommand = "select * from" + "struct_base_table";
            SQLiteConnection sql = new SQLiteConnection();
            MessageBox.Show("调用了其它类里的方法");
        }
    }
    public class MyClass
    {
        //注册一个名称为Test_Func1的命令。
        //调用后弹出一个窗口，显示"this is fun1"
        [CommandMethod("test_func1")]
        public void Func1()
        {
            MessageBox.Show("this is func");
            testClass test = new testClass();
            test.help();
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
        //更改了数组维数，引出弹窗bug
        [CommandMethod("yjk_post")]
        public void Func5()
        {
            string xing = new String('*', 50);
            string title = xing + "楼层刚度信息统计" + xing;
            console(title);//输出title内容到指定位置的txt文件
            for (int i = 0; i < 10; ++i)
            {
                double[] dSD = new double[1];
                double[] dSC = new double[1];
                try
                {
                    Hi_DesignData.dsnGetFlrStiff(i + 1, 1, dSD, dSC);
                    string str = String.Format("层号：{0}， 塔号：{1}， X、Y方向层间剪力与层间位移之比:{2}，{3}，" +
                    " X、Y方向层剪切刚度:{4}，{5}", i + 1, 1, dSD[0], dSD[1], dSC[0], dSC[1]);
                    console(str);//输出str内容到指定位置的txt文件
                }
                catch (Exception ex)
                {
                    MessageBox.Show(ex.ToString());
                }
            }
            console("");

            void console(string info)
            {
                File.AppendAllText("D:\\Cslog.txt", "\r\n" + info);
            }
        }

        [CommandMethod("yjk_post1")]
        public void Func6()
        {
            try
            {
                //打印第一层的全楼编号
                Hi_CToSDesign test1 = new Hi_CToSDesign();
                int iFlr = 5;
                int res = test1.NBeam(iFlr);
                console("某层梁数" + res.ToString());
                int[] idFlrBeams = new int[res];
                test1.FlrBeams(iFlr, idFlrBeams);
                for (int i = 0; i < res; ++i)
                {
                    console("编号" + idFlrBeams[i].ToString());
                }
                //由梁的全楼编号获取梁建模ID
                DataFunc dataFunc = new DataFunc();
                Hi_DbModelData m_modelData = dataFunc.DbModelRead(@"D:\5.C#二次开发\MyExample\ydb\kj.ydb");
                dataFunc.SetModel(m_modelData);
                for (int i = 0; i < res; ++i)
                {
                    int Beam_No = test1.BeamONO(idFlrBeams[i]);
                    int BeamFlr = test1.BeamOFlr(idFlrBeams[i]);
                    string str = String.Format("全楼编号:{0}, 建模ID:{1}", idFlrBeams[i], dataFunc.GetGjId(12, BeamFlr, Beam_No));
                    console(str);
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.ToString());
            }

            void console(string info)
            {
                File.AppendAllText("D:\\ydbinfo.txt", "\r\n" + info);
            }

        }
        //测试生成ydb
        [CommandMethod("yjk_scydb")]
        public void Func7()
        {
            try
            {
                DataFunc dataFunc = new DataFunc();
                //标准层
                Mdl_StdFlr StdFlr = dataFunc.StdFlr_Generate(3900);
                //工程参数
                Mdl_ProjectPara ProjectPara = dataFunc.ProjectPara_Set("10101");
                //截面定义
                Mdl_ColSect defcol = dataFunc.ColSect_Def(6, 1, "400,400");
                Mdl_BeamSect defbeam1 = dataFunc.BeamSect_Def(6, 1, "250,600");
                Mdl_BeamSect defbeam2 = dataFunc.BeamSect_Def(6, 1, "200,400");
                //荷载定义
                Mdl_LoadSect beamload1 = dataFunc.def_load(12, "1.00,9.60");
                Mdl_LoadSect beamload2 = dataFunc.def_load(12, "1.00,5.50");
                //生成节点
                var nodelist = new List<List<Mdl_Joint>>();
                var originpos = new List<int> { 0, 0 };
                var xspans = new List<int> { originpos[0], 3900, 3900, 3900, 3900, 3900, 3900 };
                var yspans = new List<int> { originpos[1], 6700, 5300 };
                nodelist = dataFunc.node_generate(xspans, yspans, StdFlr);
                //生成网格
                var gridlist = new List<Mdl_Grid>();
                gridlist = dataFunc.grid_generate(nodelist, 0, 1);
                //布置框架梁柱及荷载
                dataFunc.column_arrange(nodelist, defcol);
                var beam_list = new List<Mdl_BeamSeg>();
                beam_list = dataFunc.beam_arrange(gridlist, defbeam1);
                dataFunc.load_arrange(beam_list, beamload1);
                gridlist = dataFunc.grid_generate(nodelist, 1, 0);
                beam_list = dataFunc.beam_arrange(gridlist, defbeam2);
                dataFunc.load_arrange(beam_list, beamload2);
                //布置次梁
                xspans = new List<int> { originpos[0], 3900, 3900, 3900, 3900, 3900, 3900 };
                yspans = new List<int> { 5200 };
                nodelist = dataFunc.node_generate(xspans, yspans, StdFlr);
                gridlist = dataFunc.grid_generate(nodelist, 1, 0);
                beam_list = dataFunc.beam_arrange(gridlist, defbeam2);
                dataFunc.load_arrange(beam_list, beamload2);
                //标准层复制
                dataFunc.bzc_copy(0, StdFlr, 6, 3600);
                //提交建模数据
                dataFunc.DbModel_Assign();
                Hi_DbModelData model = dataFunc.GetDbModelData();
                Hi_AddProjectToYjk my = new Hi_AddProjectToYjk(model);
                my.CreateYDB(@"D:\5.C#二次开发\MyExample\ydb", "kj.ydb");
            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.ToString());
            }
        }
        //测试标准层参数
        [CommandMethod("yjk_bzcpara")]
        public void Func8()
        {
            try
            {
                DataFunc dataFunc = new DataFunc();
                Hi_DbModelData m_modelData = dataFunc.DbModelRead(@"D:\5.C#二次开发\MyExample\ydb\kj.ydb");
                dataFunc.SetModel(m_modelData);

                //截面定义
                Mdl_ColSect defcol = dataFunc.ColSect_Def(6, 1, "600,600");

                //修改柱截面尺寸
                var colseg = dataFunc.GetColSegList();
                colseg[0].SectID = defcol.ID;


                Hi_DbModelData model = dataFunc.GetDbModelData();

                Hi_AddProjectToYjk my = new Hi_AddProjectToYjk(model);
                my.CreateYDB(@"D:\5.C#二次开发\MyExample\ydb\", "new.ydb");
            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.ToString());
            }

        }
        //测试前处理
        [CommandMethod("yjk_pre111")]
        public void Func9()
        {
            Hi_JSCS test2 = new Hi_JSCS();
            string res1 = test2.GetSParaInt(106);
            string res2 = test2.GetSParaFlt(694);
            
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

            //风荷载体型系数_X向
            float[] TXXS_Y = new float[13];

            //第一段X挡风&&Y迎风面&&Y背风面&&Y侧风面
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
            //设防烈度
            test2.SetSParInt(302, 30206);
        }
        //导出ydb
        [CommandMethod("Test_exportydb")]
        public void Func10()
        {
            ClrYJKSUI yjksui = new ClrYJKSUI();
            //ClrYJKSCommand yjkscmd = new ClrYJKSCommand();
            //yjkscmd.CsRunCommand("yjk_save");
            yjksui.CsQRunCommandEx("yjk_Exportydb", @"D:\5.C#二次开发\MyExample\ydb\kj0518.ydb", @"D:\1.pyYJKS\yjk_test5.1\test03\1");
        }
        //脚本模式不弹窗
        [CommandMethod("Test_script")]
        public void Func11()
        {
            ClrYJKSUI YJKSUI = new ClrYJKSUI();
            ClrYJKSCommand YJKSCommand = new ClrYJKSCommand();
            //切换标签栏至轴线网格
            YJKSUI.CsQSetCurrentRibbonLabel("IDModule_Axis");
            YJKSUI.CsQRunCommandEx("yjk_importydb", "D:/5.C#二次开发/MyExample/ydb/kj.ydb", 0);
            //
            YJKSUI.CsQSetRunScript(1);
            //工程修复、保存
            YJKSCommand.CsRunCommand("yjk_repairex");
            YJKSCommand.CsRunCommand("yjk_save");
            YJKSCommand.CsRunCommand("yjk_setlayersupport");
            YJKSCommand.CsRunCommand("yjkspre_genmodrel");
            YJKSCommand.CsRunCommand("yjktransload_tlplan");
            YJKSCommand.CsRunCommand("yjktransload_tlvert");
            //切换标签栏至前处理
            YJKSUI.CsQSetCurrentRibbonLabel("IDSPRE_ROOT");
            //设计计算
            YJKSCommand.CsRunCommand("yjkdesign_dsncalculating_all");
            //切换标签栏至设计结果
            YJKSUI.CsQSetCurrentRibbonLabel("IDDSN_DSP");
        }
        //Nbeam失效
        [CommandMethod("Test_dsnydb")]
        public void Func12()
        {
            ClrYJKSUI yjksui = new ClrYJKSUI();
            yjksui.CsQRunCommandEx("yjkdesign_dsnexportdb", "", "true");
        }
        //测试获取newdata的内容
        [CommandMethod("Test_newdata")]
        public void Func13()
        {

            ClrYJKSCommand yjkscmd = new ClrYJKSCommand();
            yjkscmd.CsRunCommand("yjk_save");
            Hi_AddProjectToYjk my = new Hi_AddProjectToYjk();
            my.ReadAll();
            int maxID = my.GetMaxID();
            var model= my.GetDbmodel();
            DataFunc dataFunc = new DataFunc();
            dataFunc.SetModel(model);
            dataFunc.SetID(maxID);
            //新增截面
            Mdl_ColSect defcol = dataFunc.ColSect_Def(6, 1, "500,500");
            Mdl_BeamSect defbeam = dataFunc.BeamSect_Def(6, 1, "250,1000");
            Mdl_WallSect defwall = dataFunc.WallSect_Def(6, 1, 1000);
            Mdl_BraceSect defbrace = dataFunc.BraceSect_Def(5, 3, "500");
            Mdl_WallHoleDef defwallhole = dataFunc.WallHoleDef(300, 2500);
            //修改YJK工程中group内构件的截面
            var group = dataFunc.GetGroupObjList(model.m_Group[0]);
            foreach(var col in group.collist)
            {
                col.SectID = defcol.ID;
            }
            foreach (var beam in group.beamlist)
            {
                beam.SectID = defbeam.ID;
            }
            foreach (var wall in group.walllist)
            {
                wall.SectID = defwall.ID;
            }
            foreach (var brace in group.bracelist)
            {
                brace.SectID = defbrace.ID;
            }
            foreach (var wallhole in group.windowlist)
            {
                wallhole.SectID = defwallhole.ID;
            }
            dataFunc.DbModel_Assign();
            my.SetDbmodel(dataFunc.GetDbModelData());
            //增加到yjk
            my.ReflecToYJK();
        }
        //测试修改楼层信息
        [CommandMethod("test_flrInfo")]
        public void Func14()
        {
            Hi_StrucTowerInfo info = new Hi_StrucTowerInfo();
            info.Load();
            var res= info.GetTower(1,1);
            res._cCL = 60;
            info.AddTower(res);
            info.Save();
        }

        //测试加腋
        [CommandMethod("test_jy")]
        public void Func15()
        {
            ClrYJKSCommand yjkscmd = new ClrYJKSCommand();
            yjkscmd.CsRunCommand("yjk_save");
            Hi_AddProjectToYjk my = new Hi_AddProjectToYjk();
            my.ReadAll();
            int maxID = my.GetMaxID();
            var model = my.GetDbmodel();
            DataFunc dataFunc = new DataFunc();
            dataFunc.SetModel(model);
            dataFunc.SetID(maxID);
            //新增截面
            Mdl_SlabJYDef defslabjy = dataFunc.SlbaJYSect_Def(1, "1500.00,500.00,0.00,0.00,");
            Mdl_ColSect defcol = dataFunc.ColSect_Def(6, 1, "501,501");
            Mdl_BeamSect defbeam = dataFunc.BeamSect_Def(6, 1, "251,1001");
            Mdl_WallSect defwall = dataFunc.WallSect_Def(6, 1, 1001);
            Mdl_BraceSect defbrace = dataFunc.BraceSect_Def(5, 3, "501");
            Mdl_WallHoleDef defwallhole = dataFunc.WallHoleDef(300, 2501);
            Mdl_BeamJY defbeamjy = dataFunc.BeamJYSect_Def(1, "1000,500,400,1000,500,400", "jy01");

            //修改YJK工程中group内构件的截面
            var group = dataFunc.GetGroupObjList(model.m_Group[0]);
            foreach (var col in group.collist)
            {
                col.SectID = defcol.ID;
            }
            foreach (var beam in group.beamlist)
            {
                //beam.SectID = defbeam.ID;
                dataFunc.beamjy_arrange(defbeamjy, beam);
            }
            foreach (var wall in group.walllist)
            {
                wall.SectID = defwall.ID;
            }
            foreach (var brace in group.bracelist)
            {
                brace.SectID = defbrace.ID;
            }
            foreach (var wallhole in group.windowlist)
            {
                wallhole.SectID = defwallhole.ID;
            }
            foreach (var grid in group.gridlist)
            {
                dataFunc.slabjy_arrange(defslabjy, grid);
            }
            dataFunc.DbModel_Assign();
            my.SetDbmodel(dataFunc.GetDbModelData());
            //增加到yjk
            my.ReflecToYJK();
        }

        //测试refresh
        [CommandMethod("test_refresh")]
        public void Func16()
        {
            DataFunc dataFunc = new DataFunc();
            //标准层
            Mdl_StdFlr StdFlr = dataFunc.StdFlr_Generate(3900);
            BzcPara para = new BzcPara();
            var str = para.GetValString();
            //工程参数
            Mdl_ProjectPara ProjectPara = dataFunc.ProjectPara_Set("10101");
            //截面定义
            Mdl_ColSect defcol = dataFunc.ColSect_Def(6, 1, "400,400");
            Mdl_BeamSect defbeam1 = dataFunc.BeamSect_Def(6, 1, "250,600");
            Mdl_BeamSect defbeam2 = dataFunc.BeamSect_Def(6, 1, "200,400");
            //Mdl_BeamJY defbeamjy = dataFunc.BeamJYSect_Def(0,"1000,500,400","jy01");
            //Mdl_SlabJYDef defslabjy = dataFunc.SlbaJYSect_Def(1, "1500.00,500.00,0.00,0.00,");
            //荷载定义
            Mdl_LoadSect beamload1 = dataFunc.def_load(12, "1.00,9.60");
            Mdl_LoadSect beamload2 = dataFunc.def_load(12, "1.00,5.50");
            //生成节点
            var nodelist = new List<List<Mdl_Joint>>();
            var originpos = new List<int> { 0, 0 };
            var xspans = new List<int> { originpos[0], 3900, 3900, 3900, 3900, 3900, 3900 };
            var yspans = new List<int> { originpos[1], 6700, 5300 };
            nodelist = dataFunc.node_generate(xspans, yspans, StdFlr);
            //生成网格
            var gridlist = new List<Mdl_Grid>();
            gridlist = dataFunc.grid_generate(nodelist, 0, 1);
            //布置框架梁柱及荷载
            dataFunc.column_arrange(nodelist, defcol);
            var beam_list = new List<Mdl_BeamSeg>();
            beam_list = dataFunc.beam_arrange(gridlist, defbeam1);
            dataFunc.load_arrange(beam_list, beamload1);
            gridlist = dataFunc.grid_generate(nodelist, 1, 0);
            beam_list = dataFunc.beam_arrange(gridlist, defbeam2);
            dataFunc.load_arrange(beam_list, beamload2);
            //布置次梁
            xspans = new List<int> { originpos[0], 3900, 3900, 3900, 3900, 3900, 3900 };
            yspans = new List<int> { 5200 };
            nodelist = dataFunc.node_generate(xspans, yspans, StdFlr);
            gridlist = dataFunc.grid_generate(nodelist, 1, 0);
            beam_list = dataFunc.beam_arrange(gridlist, defbeam2);
            dataFunc.load_arrange(beam_list, beamload2);

            //标准层复制
            dataFunc.bzc_copy(0, StdFlr, 6, 3600);
            //提交建模数据
            dataFunc.DbModel_Assign();
            Hi_DbModelData model = dataFunc.GetDbModelData();
            Hi_AddProjectToYjk my = new Hi_AddProjectToYjk(model);
            bool isok = my.RefreshToYJK();
        }
    }

}
