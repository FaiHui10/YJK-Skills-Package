using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

using CsToYjk;
using APIData;
using DataFuncApplication;

//本代码案例演示设置柱加固定义、梁加固定义、钢结构加固定义及布置相关加固信息。

namespace ConsoleApp08
{
    class JG
    {
        static void Main(string[] args)
        {
            DataFunc dataFunc = new DataFunc();
            Hi_AddToAndReadYjk my = new Hi_AddToAndReadYjk();

            Hi_DbModelData m_modelData = my.ReadYdb(@"..\..\ydb\kj.ydb");

            dataFunc.SetModel(m_modelData);
            //柱加固(以下参数设置得比较随意,仅做示例作用)
            var creatInfo1 = new ColJGCreateInfo_MagnifySect();
            creatInfo1.SetPara(100, 300, 300, 100, 50);
            creatInfo1.SetName("增大截面法");
            var coljg1 = dataFunc.ColJGSect_Def(creatInfo1);

            var creatInfo2 = new ColJGCreateInfo_StickFibre();
            creatInfo2.SetPara(0, 1, 50, 50, 20, 200, 5, 50);
            creatInfo2.SetName("外贴纤维");
            var coljg2 = dataFunc.ColJGSect_Def(creatInfo2);

            var creatInfo3 = new ColJGCreateInfo_WrapSteel();
            creatInfo3.SetPara(235, 100, 50, 200, 0, "L20x4");
            creatInfo3.SetName("外包钢板");
            var coljg3 = dataFunc.ColJGSect_Def(creatInfo3);

            var creatInfo4 = new ColJGCreateInfo_Convert();
            creatInfo4.SetPara(100, 200, 25);
            creatInfo4.SetName("置换混凝土法");
            var coljg4 = dataFunc.ColJGSect_Def(creatInfo4);

            var creatInfo5 = new ColJGCreateInfo_StickPlate();
            creatInfo5.SetPara(1, 100, 200, 25);
            creatInfo5.SetName("外贴钢板");
            var coljg5 = dataFunc.ColJGSect_Def(creatInfo5);

            dataFunc.columnjg_arrange(m_modelData.m_ColSeg[0], coljg1);
            dataFunc.columnjg_arrange(m_modelData.m_ColSeg[1], coljg2);
            dataFunc.columnjg_arrange(m_modelData.m_ColSeg[2], coljg3);
            dataFunc.columnjg_arrange(m_modelData.m_ColSeg[3], coljg4);
            dataFunc.columnjg_arrange(m_modelData.m_ColSeg[4], coljg5);

            //梁加固(以下参数设置得比较随意,仅做示例作用)
            var creatInfo6 = new BeamJGCreateInfo_MagnifySect();
            creatInfo6.SetPara(100, 200, 300, 35);
            creatInfo6.SetName("增大截面法");
            var beamjg1 = dataFunc.BeamJGSect_Def(creatInfo6);

            var creatInfo7 = new BeamJGCreateInfo_WrapSteel();
            creatInfo7.SetPara(100, 200, 300, 0, "L20x4", "L20x4", 100, 200);
            creatInfo7.SetName("外包钢板");
            var beamjg2 = dataFunc.BeamJGSect_Def(creatInfo7);

            var creatInfo8 = new BeamJGCreateInfo_StickPlateAndMagnifySect();
            creatInfo8.SetPara(100, 200, 1, 200, 100, 35);
            creatInfo8.SetName("外粘钢板+底部增大截面");
            var beamjg3 = dataFunc.BeamJGSect_Def(creatInfo8);

            var creatInfo9 = new BeamJGCreateInfo_Convert();
            creatInfo9.SetPara(100, 200, 25);
            creatInfo9.SetName("置换混凝土法");
            var beamjg4 = dataFunc.BeamJGSect_Def(creatInfo9);

            var creatInfo10 = new BeamJGCreateInfo_ReinForceSteelStrand();
            creatInfo10.SetPara(10, 20, 30, 40, 50);
            creatInfo10.SetName("预应力钢绞线");
            var beamjg5 = dataFunc.BeamJGSect_Def(creatInfo10);

            var creatInfo11 = new BeamJGCreateInfo_StickFibre();
            creatInfo11.SetPara(0, 1, 50, 50, 20, 20, 200, 5, 50, 20);
            creatInfo11.SetName("外贴纤维");
            var beamjg6 = dataFunc.BeamJGSect_Def(creatInfo11);

            var creatInfo12 = new BeamJGCreateInfo_StickPlate();
            creatInfo12.SetPara(10, 20, 30, 40, 50, 60, 70, 1);
            creatInfo12.SetName("外贴钢板");
            var beamjg7 = dataFunc.BeamJGSect_Def(creatInfo12);

            dataFunc.beamjg_arrange(m_modelData.m_BeamSeg[0], beamjg1);
            dataFunc.beamjg_arrange(m_modelData.m_BeamSeg[1], beamjg2);
            dataFunc.beamjg_arrange(m_modelData.m_BeamSeg[2], beamjg3);
            dataFunc.beamjg_arrange(m_modelData.m_BeamSeg[3], beamjg4);
            dataFunc.beamjg_arrange(m_modelData.m_BeamSeg[4], beamjg5);
            dataFunc.beamjg_arrange(m_modelData.m_BeamSeg[5], beamjg6);
            dataFunc.beamjg_arrange(m_modelData.m_BeamSeg[6], beamjg7);

            //钢结构加固(以下参数设置得比较随意,仅做示例作用)
            var creatInfo13 = new SteelJGCreateInfo();
            creatInfo13.SetFilletWeldSize(8)
                       .SetWeldInterVal(300)
                       .SetWeldLen(400)
                       .SetSteelLevel(357)
                       .SetKind(1)
                       .SetSteelJGSect(200, 300, 10, 20)
                       .SetIsInter(1)
                       .SetDim(25);
            var steeljg1 = dataFunc.SteelJGSect_Def(creatInfo13);

            var creatInfo14 = new SteelJGCreateInfo();
            creatInfo14.SetFilletWeldSize(8)
                       .SetWeldInterVal(300)
                       .SetWeldLen(400)
                       .SetSteelLevel(358)
                       .SetKind(4)
                       .SetSectionSteelName("L20x4");
            var steeljg2 = dataFunc.SteelJGSect_Def(creatInfo14);

            var creatInfo15 = new SteelJGCreateInfo();
            creatInfo15.SetFilletWeldSize(8)
                       .SetWeldInterVal(300)
                       .SetWeldLen(400)
                       .SetSteelLevel(358)
                       .SetKind(3)
                       .SetSteelJGSect(200, 300, 10, 20)
                       .SetTSecK(1)
                       .SetSectionSteelName("L20x4");
            var steeljg3 = dataFunc.SteelJGSect_Def(creatInfo15);

            dataFunc.steeljg_arrange(m_modelData.m_BeamSeg[7], steeljg1);
            dataFunc.steeljg_arrange(m_modelData.m_BeamSeg[8], steeljg2);
            dataFunc.steeljg_arrange(m_modelData.m_BeamSeg[9], steeljg3);

            var updateInfo = dataFunc.GetUpdateInfo();

            bool isok = my.ReflectAndCreateYDB(updateInfo, @"..\..\", "new.ydb");
            if (isok) Console.WriteLine("运行完成！");
            Console.ReadLine();
        }
    }
}
