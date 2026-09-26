using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.Drawing;
using System.IO;

using APIData;
using CsToYjk;
using DataFuncApplication;
using MiddleTrans;


//这是一个向YJK平台注册命令的案例，用户可通过一个dll向YJK平台完成多个命令的注册（适用于6.0版本）
//一、将更新的dll替换到YJK对应安装路径后，执行yjks_csload,加载写好的dll文件。
//二、命令行弹出加载成功后，即可调用写好的命令。
//三、对于用户开发阶段，更新dll之后，只需执行yjks_csreload即可完成dll的更新。

namespace UserCode
{
    public class MyClass
    {
        //读取当前模型中的第一个组（group），并将其中的构件截面进行修改
        [CommandMethod("test_grp")]
        public void Func1()
        {
            ClrYJKSCommand yjkscmd = new ClrYJKSCommand();
            yjkscmd.CsRunCommand("yjk_save");
            Hi_AddToAndReadYjk my = new Hi_AddToAndReadYjk();
            var model = my.ReadFromYJK();
            int maxID = my.GetUnionID();
            DataFunc dataFunc = new DataFunc();
            dataFunc.SetModel(model);
            dataFunc.SetID(maxID);
            //新增截面
            Mdl_ColSect defcol = dataFunc.ColSect_Def(6, 1, "501,501");
            Mdl_BeamSect defbeam = dataFunc.BeamSect_Def(6, 1, "251,1001");
            Mdl_WallSect defwall = dataFunc.WallSect_Def(6, 1, 1001);
            Mdl_BraceSect defbrace = dataFunc.BraceSect_Def(5, 3, "501");
            Mdl_WallHoleDef defwallhole = dataFunc.WallHoleDef(300, 2501);
            //修改YJK工程中group内构件的截面
            if (model.m_Group.Count() == 0) return;
            var group = dataFunc.GetGroupObjList(model.m_Group[0]);
            foreach (var col in group.collist)
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
            var updateInfo = dataFunc.GetUpdateInfo();
            //增加到yjk
            my.ReflecToYJK(updateInfo);
        }
        //不通过ydb，直接在内存中完成新模型的重新生成
        [CommandMethod("test_refresh")]
        public void Func2()
        {
            DataFunc dataFunc = new DataFunc();
            //标准层
            Mdl_StdFlr StdFlr = dataFunc.StdFlr_Generate(3900);
            BzcPara para = new BzcPara();
            var str = para.GetValString();
            //截面定义
            Mdl_ColSect defcol = dataFunc.ColSect_Def(6, 1, "400,400");
            Mdl_BeamSect defbeam1 = dataFunc.BeamSect_Def(6, 1, "250,600");
            Mdl_BeamSect defbeam2 = dataFunc.BeamSect_Def(6, 1, "200,400");
            //Mdl_BeamJY defbeamjy = dataFunc.BeamJYSect_Def(0,"1000,500,400","jy01");
            //Mdl_SlabJYDef defslabjy = dataFunc.SlbaJYSect_Def(1, "1500.00,500.00,0.00,0.00,");
            //荷载定义
            Mdl_LoadSect beamload1 = dataFunc.Load_Def(12, "1.00,9.60");
            Mdl_LoadSect beamload2 = dataFunc.Load_Def(12, "1.00,5.50");
            Mdl_LoadSect jointload1 = dataFunc.Load_Def(-1, "1001.000,1002.000,1003.000,1004.000,1005.000,1006.000,0.000");
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
            //布置节点荷载
            foreach (var _nodelist in nodelist)
            {
                dataFunc.load_arrange(_nodelist, jointload1);
            }
            //布置次梁
            xspans = new List<int> { originpos[0], 3900, 3900, 3900, 3900, 3900, 3900 };
            yspans = new List<int> { 5200 };
            nodelist = dataFunc.node_generate(xspans, yspans, StdFlr);
            gridlist = dataFunc.grid_generate(nodelist, 1, 0);
            beam_list = dataFunc.beam_arrange(gridlist, defbeam2);
            dataFunc.load_arrange(beam_list, beamload2);

            //标准层复制
            dataFunc.Floors_Assemb(0, StdFlr, 6, 3600);
            //提交建模数据
            dataFunc.DbModel_Assign();
            Hi_DbModelData model = dataFunc.GetDbModelData();
            Hi_AddToAndReadYjk my = new Hi_AddToAndReadYjk(model);
            bool isok = my.RefreshToYJK();
        }
        //修改楼层属性中的楼层信息
        [CommandMethod("Test_FlrInfo")]
        public void Func14()
        {
            ClrYJKSUI yjksui = new ClrYJKSUI();
            //获取命令参数
            var para = yjksui.CsGetScriptParam();

            Hi_StrucTowerInfo info = new Hi_StrucTowerInfo();
            info.Init();
            info.Load();
            var res = info.GetTower(1, 1);
            res.cCL = 60;
            info.AddTower(res, 1);
            info.Save();
            var num = info.GetTowNO();
            var list = info.GetFzTower(1);
        }
        //多塔划分_案例使用的模型参见ydb文件夹中的dt.ydb
        [CommandMethod("test_dthf")]
        public void Func19()
        {
            Hi_StrucTowerInfo info = new Hi_StrucTowerInfo();
            info.Load();
            var res = info.GetTower(2, 1);
            //修改1塔2层
            res.cCL = 60;
            var poly = res.poly;
            poly[0] = Tuple.Create(115f, 2840f);
            poly[1] = Tuple.Create(115f, 8840f);
            poly[2] = Tuple.Create(6115f, 8840f);
            poly[3] = Tuple.Create(6115f, 2840f);

            info.AddTower(res, 2);
            //新增2塔2层
            res.no = 2;
            poly[0] = Tuple.Create(12115f, 2840f);
            poly[1] = Tuple.Create(12115f, 8840f);
            poly[2] = Tuple.Create(18115f, 8840f);
            poly[3] = Tuple.Create(18115f, 2840f);
            info.AddTower(res, 2);
            info.Save();
        }

        //脚本模式不弹窗
        [CommandMethod("Test_script")]
        public void Func20()
        {
            ClrYJKSUI YJKSUI = new ClrYJKSUI();
            ClrYJKSCommand YJKSCommand = new ClrYJKSCommand();
            //切换标签栏至轴线网格
            YJKSUI.CsQSetCurrentRibbonLabel("IDModule_Axis");
            //YJKSUI.CsQRunCommandEx("yjk_importydb", "D:/5.C#二次开发/MyExample/ydb/kj.ydb", 0);
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

        [CommandMethod("test_order")]
        public void Func23()
        {
            Hi_StrucTowerInfo info = new Hi_StrucTowerInfo();
            info.Init();
            info.Load();
            int order = info.GetCompOrder(1182, 1117);
            info.SetCompOrder(1182, 1117, 2);
            info.Save();
        }
        [CommandMethod("test_post")]
        public void Func24()
        {
            //由CToSDesign获取构件全楼编号
            Hi_CToSDesign CToSDesign = new Hi_CToSDesign();
            //标准层编号
            int iFlr = 1;
            int ColumnNum = CToSDesign.NColumn(iFlr);
            console("第一层柱数：" + ColumnNum.ToString());
            //第一层柱的全楼编号
            var idFlrColumns = CToSDesign.FlrColumns(iFlr, ColumnNum);
            //统计总节点
            int NodeNum = CToSDesign.NJD();
            console("模型总节点数：" + NodeNum.ToString());
            //统计总层数
            int FlrNum = CToSDesign.NZRC();
            console("模型总层数：" + FlrNum.ToString());

            string xing = new String('*', 50);
            string title = xing + "层刚度信息统计" + xing;
            console(title);         //输出title内容到指定txt文件
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


        [CommandMethod("test_ipcreflect")]
        public void Func25()
        {
            Hi_AddToAndReadYjk my = new Hi_AddToAndReadYjk();
            my.RestCadInfo();
            my.ReadBzcAndProj();
            var link = Link2YJK.Instance;
            var model = link.GetIPCdata<Hi_UpdateInfo>();
            //增加到yjk
            my.ReflecToYJK(model);
        }

        [CommandMethod("test_ipcrefresh")]
        public void Func26()
        {
            var link = Link2YJK.Instance;
            var model = link.GetIPCdata<Hi_DbModelData>();
            Hi_AddToAndReadYjk my = new Hi_AddToAndReadYjk(model);

            //增加到yjk
            my.RefreshToYJK();
        }

        [CommandMethod("test_updateUnionID")]
        public void Func27()
        {
            //ClrYJKSCommand yjkscmd = new ClrYJKSCommand();
            //yjkscmd.CsRunCommand("yjk_save");
            Hi_AddToAndReadYjk my = new Hi_AddToAndReadYjk();
            my.RestCadInfo();
            var unionID = my.GetUnionID();
            var link = Link2YJK.Instance;
            link.LinkPrepare(unionID);
        }

        [CommandMethod("test_readModel")]
        public void Func28()
        {
            ClrYJKSCommand yjkscmd = new ClrYJKSCommand();
            yjkscmd.CsRunCommand("yjk_save");
            Hi_AddToAndReadYjk my = new Hi_AddToAndReadYjk();
            var model = my.ReadFromYJK();
            var link = Link2YJK.Instance;
            link.LinkPrepare(model);
        }

        //在设计结果模块使用，搭配yjk文件夹里的超限项目使用
        [CommandMethod("test_LimitInf")]
        public void Func29()
        {
            //获取所有梁的全楼编号
            Hi_CToSDesign test1 = new Hi_CToSDesign();
            //总层数
            int NZRC = test1.NZRC();
            var LimitIdList = new List<int>();
            var LimitInfoList = new Dictionary<int, int[]>();
            for (int i = 1; i < NZRC + 1; ++i)
            {
                int iFlr = i;
                int beamNum = test1.NBeam(iFlr);
                var idFlrBeams = test1.FlrBeams(iFlr, beamNum);

                //查询超限构件
                Hi_DesignData.dsnInitData();
                Hi_DesignData.dsnReadFloorPJ(i);    //设置当前楼层，程序将读取该楼层构件索引，并生成该层构件配筋信息
                for (int j = 0; j < beamNum; ++j)
                {
                    var 是否超限 = Hi_DesignData.dsnComHasLimitInf(i, (int)PostGjKind.COM_BEAM, idFlrBeams[j]);
                    if (是否超限)
                    {
                        LimitIdList.Add(idFlrBeams[j]);
                        int nNum = 0;
                        //两次调用，第一次调用获取超限信息数量，第二次调用获取超限信息内容
                        int[] tmp = new int[1];
                        Hi_DesignData.dsnGetComTotLimitInf(i, (int)PostGjKind.COM_BEAM, idFlrBeams[j], ref nNum, tmp);
                        int[] LimitInf = new int[nNum];
                        Hi_DesignData.dsnGetComTotLimitInf(i, (int)PostGjKind.COM_BEAM, idFlrBeams[j], ref nNum, LimitInf);
                        //LimitInf中1代表LIMIT_BEAM_V（梁截面抗剪超限）、4代表LIMIT_BEAM_ASMAXUP（梁上截面最大配筋率超限），详见设计结果宏定义说明文档
                        LimitInfoList.Add(idFlrBeams[j], LimitInf);
                    }
                }
            }


            //全楼ID转建模ID
            Hi_AddToAndReadYjk my = new Hi_AddToAndReadYjk();
            HashSet<int> ids = new HashSet<int>();
            for (int i = 0; i < LimitIdList.Count; ++i)
            {
                int No = test1.BeamONO(LimitIdList[i]);
                int flrNo = test1.BeamOFlr(LimitIdList[i]);
                int ID_Model = my.ReadIdByNO(GjKind.IDK_BEAM, No, flrNo);
                ids.Add(ID_Model);
            }

            //把ID传给用户进程（可选，看是否需要联动）
            //var link = Link2YJK.Instance;
            //link.LinkPrepare(ids);
        }
        //在设计结果模块使用，搭配yjk文件夹里的test_dtl项目使用，用于获取某梁端所属的梁跨的所有梁段ID号、整根连续梁上所有的梁段ID号、当前梁跨梁端的支座信息
        [CommandMethod("test_dtl")]
        public void Func30()
        {
            var res = ClrYJKDTL.LoadProjectInfo();
            var IDs1 = ClrYJKDTL.GetBeamSpanIds(0, 1135);
            var IDs2 = ClrYJKDTL.GetCntBeamIds(0, 1135);
            var subInfo = ClrYJKDTL.GetBeamSupSegIds(0, 1135);
        }

        //在弹性时程分析模块使用，接口含义参照有限元接口说明
        [CommandMethod("test_API_YJKDTReport")]
        public void Func45()
        {
            Hi_API_YJKDTReport hi_YJKDTReport = new Hi_API_YJKDTReport();
            List<string> vLoadCaseComb = new List<string>();
            List<string> vLoadCase = new List<string>();
            List<string> vLoadComb = new List<string>();
            hi_YJKDTReport.getVLoadComb(vLoadCaseComb, vLoadCase, vLoadComb);

            Dictionary<string, List<double>> vLoadTimeTable = new Dictionary<string, List<double>>();
            hi_YJKDTReport.getVLTimeTbale(vLoadTimeTable);
        }

        [CommandMethod("test_Sensi_naodu")]
        public void Func46()
        {
            //灵敏度相关
            Mdl_SensiParaData para=new Mdl_SensiParaData();
            para.m_bSpecialFlr = true;
            var res = Hi_DesignDataPro.GetElemSensiVal(para);
            var beam = res.m_mapBeam;
            //挠度相关
            Hi_DesignDataPro.InitialFlrData(1);
            var StrList = Hi_DesignDataPro.GetLDCombStr((int)PostLDCombType.LDCOMBTYPE_LDCASE, 2, (int)PostGjKind.COM_BEAM);
            var id = ClrYJKDTL.FindBeamSegMainByID(0, 1130);
            var naodu = Hi_DesignDataPro.getMainBeamDefByStr(1, id, (int)PostLDCombType.LDCOMBTYPE_LDCASE,StrList[8]);

        }

        [CommandMethod("test_waveinfo")]
        public void Func47()
        {
            List<double> vWaveP = new List<double>();
            List<double> vWaveS = new List<double>();
            List<double> vWaveV = new List<double>();
            var wallinfo1 = Hi_YJKFEA.GetAllWaveInfoDataByName("ArtWave-RH1TG025,Tg(0.25)", vWaveP, vWaveS, vWaveV);
        }

    }
}
