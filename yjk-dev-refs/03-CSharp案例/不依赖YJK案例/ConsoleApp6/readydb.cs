using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.IO;

using CsToYjk;
using APIData;
using DataFuncApplication;

//本代码案例为打开一个指定路径的ydb文件，实现如下功能：
//一、读取ydb信息并将内容输出到 D:\\ydbinfo.txt。
//二、修改ydb中的楼层高度及柱截面尺寸，并生成一个新的ydb。

namespace ConsoleApp6
{
    class readydb
    {
        static void Main(string[] args)
        {
            DataFunc dataFunc = new DataFunc();
            Hi_AddToAndReadYjk my = new Hi_AddToAndReadYjk();
            Hi_DbModelData m_modelData = my.ReadYdb(@"..\..\new.ydb");
            dataFunc.SetModel(m_modelData);

            //获取型钢截面特性
            var property= dataFunc.GetSteelSectProperty(1230);

            string xing = new String('*', 50);
            string title = xing + "标准层信息" + xing;
            console(title);
            var StdFlrList = m_modelData.m_StdFlr;
            for (int i = 0; i < StdFlrList.Count(); ++i)
            {
                string str = String.Format("ID:{0},No:{1},Height:{2}", StdFlrList[i].ID, StdFlrList[i].No, StdFlrList[i].Height);
                console(str);
            }

            title = xing + "楼层信息" + xing;
            console(title);
            var FloorList = m_modelData.m_Floor;
            for (int i = 0; i < FloorList.Count(); ++i)
            {
                string str = String.Format("ID:{0}, 层底标高:{1}, 层高:{2}", FloorList[i].ID, FloorList[i].LevelB, FloorList[i].Height);
                console(str);
                //修改层高
                m_modelData.m_Floor[i].Height = 4800;
                if (i > 0)
                {
                    //修改层底标高
                    m_modelData.m_Floor[i].LevelB = m_modelData.m_Floor[i - 1].LevelB + m_modelData.m_Floor[i].Height;
                }
            }

            title = xing + "节点信息" + xing;
            console(title);
            var JointList = m_modelData.m_Joint;
            for (int i = 0; i < JointList.Count(); ++i)
            {
                string str = String.Format("ID:{0}, X坐标:{1}, Y坐标:{2}", JointList[i].ID, JointList[i].X, JointList[i].Y);
                console(str);
            }

            //修改柱截面尺寸
            string tmp = m_modelData.m_ColSect[0].ShapeVal;
            console(tmp);
            tmp = tmp.Replace("400", "600");
            console(tmp);
            m_modelData.m_ColSect[0].ShapeVal = tmp;
            m_modelData.m_BeamSect[0].Name = "梁1_修改";
            dataFunc.property_arrange(m_modelData.m_BeamSect[0].ID, "CustomName", 8, m_modelData.m_BeamSect[0].Name);
            m_modelData.m_BeamSect[1].Name = "梁2_修改";
            dataFunc.property_arrange(m_modelData.m_BeamSect[1].ID, "CustomName", 8, m_modelData.m_BeamSect[1].Name);

            //301实腹式组合截面
            var sscs_create_info = new SSCSCompCreateInfo();
            sscs_create_info.SetMat(5).SetKind(301);
            sscs_create_info.SetCompType(型钢组合形式.钢板_焊接工字钢)
                .SetFirstSteelPara(new List<double>() { 501, 401, 19, 21 }) // h\b\tw\tf
                .SetPlatePara(new List<double>() { 801, 17, 301, 11 });     // 组合截面的高度\组合截面腹板的厚度\边上钢板的宽度\边上钢板的厚度
            dataFunc.ColSect_Def(sscs_create_info);

            //26型钢截面
            var sscs_create_info2 = new SSCSCreateInfo();
            sscs_create_info2.SetMat(5).SetKind(26).SetSteelType(型钢形式.热轧普通工字钢).SetSpecification(热轧普通工字钢.I10);
            dataFunc.ColSect_Def(sscs_create_info2);

            var updateInfo = dataFunc.GetUpdateInfo();

            bool isok = my.ReflectAndCreateYDB(updateInfo,@"..\..\", "new.ydb");
            if (isok) Console.WriteLine("运行完成！");
            Console.ReadLine();
        }

        public static void console(string info)
        {
            File.AppendAllText(@"..\..\ydbinfo.txt", "\r\n" + info);
        }
    }
}
