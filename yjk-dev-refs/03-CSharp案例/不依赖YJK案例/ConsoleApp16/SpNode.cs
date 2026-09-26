using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

using CsToYjk;
using APIData;
using DataFuncApplication;

//前处理特殊节点的布置（摩擦摆的设置）

namespace ConsoleApp16
{
    class SpNode
    {
        static void Main(string[] args)
        {
            DataFunc dataFunc = new DataFunc();
            Hi_AddToAndReadYjk my = new Hi_AddToAndReadYjk();

            Hi_DbModelData m_modelData = my.ReadYdb(@"..\..\kj.ydb");
            dataFunc.SetModel(m_modelData);
            SetSpNode_摩擦摆隔震支座(dataFunc, m_modelData);
            SetSpNode_阻尼器麦克斯韦(dataFunc, m_modelData);
            SetSpNode_阻尼器开尔文(dataFunc, m_modelData);

            SetSpNode_塑性单元wen(dataFunc, m_modelData);
            SetSpNode_隔震支座(dataFunc, m_modelData);
            SetSpNode_弹性滑板隔震支座(dataFunc, m_modelData);
            SetSpNode_间隙(dataFunc, m_modelData);
            SetSpNode_钩(dataFunc, m_modelData);
            SetSpNode_TVMD(dataFunc, m_modelData);
            SetSpNode_线性(dataFunc, m_modelData);
            SetSpNode_屈曲支撑(dataFunc, m_modelData);

            var updateInfo = dataFunc.GetUpdateInfo();
            bool isok = my.ReflectAndCreateYDB(updateInfo, @"..\..\", "new.Ydb");
            if (isok) Console.WriteLine("运行完成！");
            Console.ReadLine();
        }
        static void SetSpNode_摩擦摆隔震支座(DataFunc dataFunc, Hi_DbModelData m_modelData)
        {
            var nodes = m_modelData.m_Joint;
            var propers = m_modelData.m_Property;
            var SpNodeProp = new Property("SpNode");
            //支座类型（10为摩擦摆支座）
            SpNodeProp.setVal(27, 10);
            //U1~R3勾选（1为勾选，0为不勾选）
            for (int i = 0; i < 6; ++i)
            {
                SpNodeProp.setVal(28 + i, 1);
            }
            //线性有效刚度
            for (int i = 0; i < 6; ++i)
            {
                SpNodeProp.setVal(40 + i, 100 + i);
            }
            //线性有效阻尼
            for (int i = 0; i < 6; ++i)
            {
                SpNodeProp.setVal(46 + i, 106 + i);
            }
            //非线性U1~U3的勾选
            for (int i = 0; i < 3; ++i)
            {
                SpNodeProp.setVal(52 + i, 1);
            }
            //非线性R1~R3的不勾选
            for (int i = 0; i < 3; ++i)
            {
                SpNodeProp.setVal(55 + i, 0);
            }
            //非线性刚度（58~60）
            for (int i = 0; i < 3; ++i)
            {
                SpNodeProp.setVal(58 + i, i + 112);
            }
            //U2~U3的慢摩擦摆系数
            for (int i = 0; i < 2; ++i)
            {
                SpNodeProp.setVal(65 + i, i + 115);
            }
            //U2~U3的快摩擦摆系数
            for (int i = 0; i < 2; ++i)
            {
                SpNodeProp.setVal(71 + i, i + 117);
            }
            //U2~U3的快摩擦摆系数
            for (int i = 0; i < 2; ++i)
            {
                SpNodeProp.setVal(77 + i, i + 119);
            }

            //曲率半径（94~95）
            for (int i = 0; i < 2; ++i)
            {
                SpNodeProp.setVal(94 + i, i + 121);
            }
            //质量（99）（24）
            for (int i = 0; i < 1; ++i)
            {
                SpNodeProp.setVal(99 + i, 123);
            }
            //有效面积
            SpNodeProp.setVal(70, 124);
            //水平极限位移
            SpNodeProp.setVal(86, 125);
            //支座高度
            SpNodeProp.setVal(89, 126);
            //考虑附加弯矩
            SpNodeProp.setVal(92, 1);

            dataFunc.property_arrange(nodes[0].ID, "SpNode", 27, SpNodeProp.GetValString());
        }
        static void SetSpNode_阻尼器麦克斯韦(DataFunc dataFunc, Hi_DbModelData m_modelData)
        {
            var nodes = m_modelData.m_Joint;
            var propers = m_modelData.m_Property;
            var SpNodeProp = new Property("SpNode");
            //支座类型（2为阻尼器麦克斯韦）
            SpNodeProp.setVal(27, 2);
            //U1~R3勾选（1为勾选，0为不勾选）
            for (int i = 0; i < 6; ++i)
            {
                SpNodeProp.setVal(28 + i, 1);
            }
            //线性有效刚度
            for (int i = 0; i < 6; ++i)
            {
                SpNodeProp.setVal(40 + i, 200 + i);
            }
            //线性有效阻尼
            for (int i = 0; i < 6; ++i)
            {
                SpNodeProp.setVal(46 + i, 206 + i);
            }
            //非线性U1~R3的勾选
            for (int i = 0; i < 6; ++i)
            {
                SpNodeProp.setVal(52 + i, 1);
            }
            //非线性刚度（58~63）
            for (int i = 0; i < 6; ++i)
            {
                SpNodeProp.setVal(58 + i, i + 212);
            }
            //阻尼（64~69）
            for (int i = 0; i < 6; ++i)
            {
                SpNodeProp.setVal(64 + i, i + 218);
            }
            //阻尼指数（70~75）
            for (int i = 0; i < 6; ++i)
            {
                SpNodeProp.setVal(70 + i, i + 224);
            }

            //质量（99）
            SpNodeProp.setVal(99, 233);

            dataFunc.property_arrange(nodes[1].ID, "SpNode", 27, SpNodeProp.GetValString());
        }
        static void SetSpNode_阻尼器开尔文(DataFunc dataFunc, Hi_DbModelData m_modelData)
        {
            var nodes = m_modelData.m_Joint;
            var propers = m_modelData.m_Property;
            var SpNodeProp = new Property("SpNode");
            //支座类型（9为阻尼器开尔文）
            SpNodeProp.setVal(27, 9);
            //U1~R3勾选（1为勾选，0为不勾选）
            for (int i = 0; i < 6; ++i)
            {
                SpNodeProp.setVal(28 + i, 1);
            }
            //线性有效刚度
            for (int i = 0; i < 6; ++i)
            {
                SpNodeProp.setVal(40 + i, 300 + i);
            }
            //线性有效阻尼
            for (int i = 0; i < 6; ++i)
            {
                SpNodeProp.setVal(46 + i, 306 + i);
            }
            //非线性U1~R3的勾选
            for (int i = 0; i < 6; ++i)
            {
                SpNodeProp.setVal(52 + i, 1);
            }
            //非线性刚度（58~63）
            for (int i = 0; i < 6; ++i)
            {
                SpNodeProp.setVal(58 + i, i + 312);
            }
            //阻尼（64~69）
            for (int i = 0; i < 6; ++i)
            {
                SpNodeProp.setVal(64 + i, i + 318);
            }
            //阻尼指数（70~75）
            for (int i = 0; i < 6; ++i)
            {
                SpNodeProp.setVal(70 + i, i + 324);
            }
            //数值刚度（76~81）
            for (int i = 0; i < 6; ++i)
            {
                SpNodeProp.setVal(76 + i, i + 330);
            }

            //质量（99）
            SpNodeProp.setVal(99, 330);
            dataFunc.property_arrange(nodes[2].ID, "SpNode", 27, SpNodeProp.GetValString());
        }
        static void SetSpNode_塑性单元wen(DataFunc dataFunc, Hi_DbModelData m_modelData)
        {
            var nodes = m_modelData.m_Joint;
            var propers = m_modelData.m_Property;
            var SpNodeProp = new Property("SpNode");
            //支座类型（6为塑性单元wen）
            SpNodeProp.setVal(27, 6);
            //U1~R3勾选（1为勾选，0为不勾选）
            for (int i = 0; i < 6; ++i)
            {
                SpNodeProp.setVal(28 + i, 1);
            }
            //线性有效刚度
            for (int i = 0; i < 6; ++i)
            {
                SpNodeProp.setVal(40 + i, 400 + i);
            }
            //线性有效阻尼
            for (int i = 0; i < 6; ++i)
            {
                SpNodeProp.setVal(46 + i, 406 + i);
            }
            //非线性U1~R3的勾选
            for (int i = 0; i < 6; ++i)
            {
                SpNodeProp.setVal(52 + i, 1);
            }
            //非线性刚度（58~63）
            for (int i = 0; i < 6; ++i)
            {
                SpNodeProp.setVal(58 + i, i + 412);
            }
            //屈服力（64~69）
            for (int i = 0; i < 6; ++i)
            {
                SpNodeProp.setVal(64 + i, i + 418);
            }
            //屈服后刚度比（70~75）
            for (int i = 0; i < 6; ++i)
            {
                SpNodeProp.setVal(70 + i, i + 424);
            }
            //屈服指数（76~81）
            for (int i = 0; i < 6; ++i)
            {
                SpNodeProp.setVal(76 + i, i + 430);
            }
            //质量（99）（130）
            SpNodeProp.setVal(99, 436);
            dataFunc.property_arrange(nodes[3].ID, "SpNode", 27, SpNodeProp.GetValString());
        }
        static void SetSpNode_隔震支座(DataFunc dataFunc, Hi_DbModelData m_modelData)
        {
            var nodes = m_modelData.m_Joint;
            var propers = m_modelData.m_Property;
            var SpNodeProp = new Property("SpNode");
            //支座类型（3为隔震支座）
            SpNodeProp.setVal(27, 3);
            //U1~R3勾选（1为勾选，0为不勾选）
            for (int i = 0; i < 6; ++i)
            {
                SpNodeProp.setVal(28 + i, 1);
            }
            //线性有效刚度
            for (int i = 0; i < 6; ++i)
            {
                SpNodeProp.setVal(40 + i, 500 + i);
            }
            //线性有效阻尼
            for (int i = 0; i < 6; ++i)
            {
                SpNodeProp.setVal(46 + i, 506 + i);
            }
            //非线性U1~U3的勾选
            for (int i = 0; i < 3; ++i)
            {
                SpNodeProp.setVal(52 + i, 1);
            }
            //非线性R1~R3的不勾选
            for (int i = 0; i < 3; ++i)
            {
                SpNodeProp.setVal(55 + i, 0);
            }
            //非线性刚度（58~60）
            for (int i = 0; i < 3; ++i)
            {
                SpNodeProp.setVal(58 + i, i + 512);
            }

            //U1抗拉刚度（64）
            SpNodeProp.setVal(64, 515);
            //U2屈服力（65）
            SpNodeProp.setVal(65, 516);
            //U3屈服力（66）
            SpNodeProp.setVal(66, 517);

            //U1截面积（70）
            SpNodeProp.setVal(70, 518);
            //U2屈服后刚度比（71）
            SpNodeProp.setVal(71, 519);
            //U3屈服后刚度比（72）
            SpNodeProp.setVal(72, 520);

            //有效直径
            SpNodeProp.setVal(86, 522);
            //中孔直径
            SpNodeProp.setVal(87, 523);
            //橡胶总厚度
            SpNodeProp.setVal(88, 524);
            //支座+连接板总高
            SpNodeProp.setVal(89, 525);
            //一次形状系数
            SpNodeProp.setVal(90, 526);
            //二次形状系数
            SpNodeProp.setVal(91, 527);

            //考虑附加弯矩
            SpNodeProp.setVal(92, 1);
            //质量（99）
            SpNodeProp.setVal(99, 528);
            dataFunc.property_arrange(nodes[4].ID, "SpNode", 27, SpNodeProp.GetValString());
        }
        static void SetSpNode_弹性滑板隔震支座(DataFunc dataFunc, Hi_DbModelData m_modelData)
        {
            var nodes = m_modelData.m_Joint;
            var propers = m_modelData.m_Property;
            var SpNodeProp = new Property("SpNode");
            //支座类型（3为弹性滑板隔震支座）
            SpNodeProp.setVal(27, 11);
            //U1~R3勾选（1为勾选，0为不勾选）
            for (int i = 0; i < 6; ++i)
            {
                SpNodeProp.setVal(28 + i, 1);
            }
            //线性有效刚度
            for (int i = 0; i < 6; ++i)
            {
                SpNodeProp.setVal(40 + i, 600 + i);
            }
            //线性有效阻尼
            for (int i = 0; i < 6; ++i)
            {
                SpNodeProp.setVal(46 + i, 606 + i);
            }
            //非线性U1~U3的勾选
            for (int i = 0; i < 3; ++i)
            {
                SpNodeProp.setVal(52 + i, 1);
            }
            //非线性R1~R3的勾选
            for (int i = 0; i < 3; ++i)
            {
                SpNodeProp.setVal(55 + i, 0);
            }
            //非线性刚度（58~60）
            for (int i = 0; i < 3; ++i)
            {
                SpNodeProp.setVal(58 + i, i + 612);
            }

            //U2摩擦系数（65）
            SpNodeProp.setVal(65, 615);
            //U3摩擦系数（66）
            SpNodeProp.setVal(66, 616);

            //有效面积（70）
            SpNodeProp.setVal(70, 617);
            //水平极限位移（86）
            SpNodeProp.setVal(86, 618);
            //支座高度（89）
            SpNodeProp.setVal(89, 619);

            //考虑附加弯矩
            SpNodeProp.setVal(92, 1);
            //质量（99）（620）
            for (int i = 0; i < 1; ++i)
            {
                SpNodeProp.setVal(99 + i, 620);
            }
            dataFunc.property_arrange(nodes[5].ID, "SpNode", 27, SpNodeProp.GetValString());
        }
        static void SetSpNode_间隙(DataFunc dataFunc, Hi_DbModelData m_modelData)
        {
            var nodes = m_modelData.m_Joint;
            var propers = m_modelData.m_Property;
            var SpNodeProp = new Property("SpNode");
            //支座类型（7为间隙）
            SpNodeProp.setVal(27, 7);
            //U1~R3勾选（1为勾选，0为不勾选）
            for (int i = 0; i < 6; ++i)
            {
                SpNodeProp.setVal(28 + i, 1);
            }
            //线性有效刚度
            for (int i = 0; i < 6; ++i)
            {
                SpNodeProp.setVal(40 + i, 700 + i);
            }
            //线性有效阻尼
            for (int i = 0; i < 6; ++i)
            {
                SpNodeProp.setVal(46 + i, 706 + i);
            }
            //非线性U1~R3的勾选
            for (int i = 0; i < 6; ++i)
            {
                SpNodeProp.setVal(52 + i, 1);
            }
            //非线性刚度（58~60）
            for (int i = 0; i < 6; ++i)
            {
                SpNodeProp.setVal(58 + i, i + 712);
            }
            //非线性刚度（58~60）
            for (int i = 0; i < 6; ++i)
            {
                SpNodeProp.setVal(64 + i, i + 718);
            }
            //质量（99）
            SpNodeProp.setVal(99, 724);

            dataFunc.property_arrange(nodes[6].ID, "SpNode", 27, SpNodeProp.GetValString());
        }
        static void SetSpNode_钩(DataFunc dataFunc, Hi_DbModelData m_modelData)
        {
            var nodes = m_modelData.m_Joint;
            var propers = m_modelData.m_Property;
            var SpNodeProp = new Property("SpNode");
            //支座类型（12为钩）
            SpNodeProp.setVal(27, 12);
            //U1~R3勾选（1为勾选，0为不勾选）
            for (int i = 0; i < 6; ++i)
            {
                SpNodeProp.setVal(28 + i, 1);
            }
            //线性有效刚度
            for (int i = 0; i < 6; ++i)
            {
                SpNodeProp.setVal(40 + i, 800 + i);
            }
            //线性有效阻尼
            for (int i = 0; i < 6; ++i)
            {
                SpNodeProp.setVal(46 + i, 806 + i);
            }
            //非线性U1~R3的勾选
            for (int i = 0; i < 6; ++i)
            {
                SpNodeProp.setVal(52 + i, 1);
            }
            //非线性刚度（58~60）
            for (int i = 0; i < 6; ++i)
            {
                SpNodeProp.setVal(58 + i, i + 812);
            }
            //非线性刚度（58~60）
            for (int i = 0; i < 6; ++i)
            {
                SpNodeProp.setVal(64 + i, i + 818);
            }
            //质量（99）（620）
            SpNodeProp.setVal(99, 824);

            dataFunc.property_arrange(nodes[7].ID, "SpNode", 27, SpNodeProp.GetValString());
        }
        static void SetSpNode_TVMD(DataFunc dataFunc, Hi_DbModelData m_modelData)
        {
            var nodes = m_modelData.m_Joint;
            var propers = m_modelData.m_Property;
            var SpNodeProp = new Property("SpNode");
            //支座类型（14为TVMD）
            SpNodeProp.setVal(27, 14);
            //U1~R3勾选（1为勾选，0为不勾选）
            for (int i = 0; i < 6; ++i)
            {
                SpNodeProp.setVal(28 + i, 1);
            }
            //线性有效刚度
            for (int i = 0; i < 6; ++i)
            {
                SpNodeProp.setVal(40 + i, 900 + i);
            }
            //线性有效阻尼
            for (int i = 0; i < 6; ++i)
            {
                SpNodeProp.setVal(46 + i, 906 + i);
            }
            //非线性U1~R3的勾选
            for (int i = 0; i < 6; ++i)
            {
                SpNodeProp.setVal(52 + i, 1);
            }
            //非线性刚度（58~63）
            for (int i = 0; i < 6; ++i)
            {
                SpNodeProp.setVal(58 + i, i + 912);
            }
            //阻尼（64~69）
            for (int i = 0; i < 6; ++i)
            {
                SpNodeProp.setVal(64 + i, i + 918);
            }
            //阻尼指数（70~75）
            for (int i = 0; i < 6; ++i)
            {
                SpNodeProp.setVal(70 + i, i + 924);
            }
            //惯性质量（76~81）
            for (int i = 0; i < 6; ++i)
            {
                SpNodeProp.setVal(76 + i, i + 930);
            }

            //质量（99）（620）
            SpNodeProp.setVal(99, 936);

            dataFunc.property_arrange(nodes[8].ID, "SpNode", 27, SpNodeProp.GetValString());
        }
        static void SetSpNode_线性(DataFunc dataFunc, Hi_DbModelData m_modelData)
        {
            var nodes = m_modelData.m_Joint;
            var propers = m_modelData.m_Property;
            var SpNodeProp = new Property("SpNode");
            //支座类型（14为TVMD）
            SpNodeProp.setVal(2, nodes[1].ID);
            //U1~R3勾选（1为勾选，0为不勾选）
            for (int i = 0; i < 6; ++i)
            {
                SpNodeProp.setVal(15 + i, 1001);
            }
            dataFunc.property_arrange(nodes[9].ID, "SpNode", 27, SpNodeProp.GetValString());
        }
        static void SetSpNode_屈曲支撑(DataFunc dataFunc, Hi_DbModelData m_modelData)
        {
            var nodes = m_modelData.m_Joint;
            var propers = m_modelData.m_Property;
            var SpNodeProp = new Property("SpNode");
            //支座类型（8为屈曲约束支撑）
            SpNodeProp.setVal(27, 8);
            //U1~R3勾选（1为勾选，0为不勾选）
            for (int i = 0; i < 6; ++i)
            {
                SpNodeProp.setVal(28 + i, 1);
            }
            //线性有效刚度
            for (int i = 0; i < 6; ++i)
            {
                SpNodeProp.setVal(40 + i, 1100 + i);
            }
            //线性有效阻尼
            for (int i = 0; i < 6; ++i)
            {
                SpNodeProp.setVal(46 + i, 1106 + i);
            }
            //非线性U1~R3的勾选
            for (int i = 0; i < 6; ++i)
            {
                SpNodeProp.setVal(52 + i, 1);
            }
            //非线性刚度（58~60）
            for (int i = 0; i < 6; ++i)
            {
                SpNodeProp.setVal(58 + i, i + 1112);
            }
            //屈服力（64~69）
            for (int i = 0; i < 6; ++i)
            {
                SpNodeProp.setVal(64 + i, i + 1118);
            }
            //屈服后刚度比（70~75）
            for (int i = 0; i < 6; ++i)
            {
                SpNodeProp.setVal(70 + i, i + 1124);
            }
            //屈服指数（76~81）
            for (int i = 0; i < 6; ++i)
            {
                SpNodeProp.setVal(76 + i, i + 1130);
            }

            //芯材面积（87）
            SpNodeProp.setVal(87, 1135);
            //芯材屈服强度标准值（88）
            SpNodeProp.setVal(88, 1136);
            //芯材超强系数（89）
            SpNodeProp.setVal(89, 1137);
            //质量（99）（620）
            SpNodeProp.setVal(99, 1138);

            dataFunc.property_arrange(nodes[10].ID, "SpNode", 27, SpNodeProp.GetValString());
        }
    }
}
