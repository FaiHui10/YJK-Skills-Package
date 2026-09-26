using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

using CsToYjk;
using APIData;
using DataFuncApplication;

//本代码案例实现如下功能：
//一、读取一个相对路径下的ydb。
//二、添加楼梯定义及布置并生成ydb。

namespace ConsoleApp09
{
    class stair
    {
        static void Main(string[] args)
        {
            DataFunc dataFunc = new DataFunc();
            Hi_AddToAndReadYjk my = new Hi_AddToAndReadYjk();

            Hi_DbModelData m_modelData = my.ReadYdb(@"..\..\kj.ydb");

            dataFunc.SetModel(m_modelData);

            //双跑楼梯
            var stairDefCreateInfo1 = new StairDefCreateInfo();
            stairDefCreateInfo1.SetKind(20)
                              .Set1stPlatForm(1800, 1720, 80, 1720, 200, 400)
                              .Set1stStair(0, 1720, 100, 0, 0, 0, 12, 0)
                              .Set2ndStair(2, 1720, 100, 0, 0, 30, 12, 0)
                              .SetAllLevel(0)
                              .SetEndPos(0)
                              .SetLevel(0)
                              .SetStartPos(30)
                              .SetStepW(300)
                              .IsGenPtFarBeam(1)
                              .IsGenColumn(1)
                              .SetTZSect(200, 200);

            //四跑楼梯
            var stairDefCreateInfo2 = new StairDefCreateInfo();
            stairDefCreateInfo2.SetKind(40)
                              .Set1stPlatForm(900, 1720, 80, 1720, 200, 400)
                              .Set2ndPlatForm(1800, 3230, 80, 3230, 200, 400)
                              .Set3rdPlatForm(2700, 1720, 80, 1720, 200, 400)
                              .Set1stStair(0, 1720, 100, 0, 0, 0, 6, 0)
                              .Set2ndStair(0, 1720, 100, 0, 0, 0, 6, 0)
                              .Set3rdStair(0, 1720, 100, 0, 0, 0, 6, 0)
                              .Set4thStair(2, 1720, 100, 0, 0, 3230, 6, 0)
                              .SetAllLevel(0)
                              .SetEndPos(0)
                              .SetLevel(0)
                              .SetStartPos(3230)
                              .SetStepW(300)
                              .IsGenPtFarBeam(1)
                              .IsGenColumn(1)
                              .SetTZSect(200, 200);

            //钢楼梯
            var stairDefCreateInfo3 = new StairDefCreateInfo();
            stairDefCreateInfo3.SetKind(30)
                              .Set1stPlatForm(1200, 2630, 0, 2630, 0, 0)
                              .Set2ndPlatForm(2400, 1720, 0, 1720, 0, 0)
                              .Set1stStair(0, 1720, 6, 0, 0, 0, 8, 0)
                              .Set2ndStair(0, 1720, 6, 0, 0, 0, 8, 0)
                              .Set3rdStair(2, 1720, 6, 0, 0, 2630, 8, 0)
                              .SetAllLevel(0)
                              .SetEndPos(0)
                              .SetLevel(0)
                              .SetGangH(235)
                              .SetStartPos(1720)
                              .SetTZSect(200, 200)
                              .IsGenColumn(1)
                              .SetStepW(300);

            //转角楼梯
            var stairDefCreateInfo4 = new StairDefCreateInfo();
            stairDefCreateInfo4.SetKind(25)
                              .Set1stPlatForm(1800, 50, 80, 50, 200, 400)
                              .Set1stStair(0, 50, 100, 0, 0, 0, 12, 0)
                              .Set2ndStair(2, 50, 100, 0, 0, 300, 12, 0)
                              .SetAllLevel(0)
                              .SetEndPos(0)
                              .SetLevel(0)
                              .SetStartPos(1700)
                              .SetStepW(300)
                              .IsGenColumn(1)
                              .SetTZSect(200, 200);


            var starDef1 = dataFunc.Stair_Def(stairDefCreateInfo1);
            var starDef2 = dataFunc.Stair_Def(stairDefCreateInfo2);
            var starDef3 = dataFunc.Stair_Def(stairDefCreateInfo3);
            var starDef4 = dataFunc.Stair_Def(stairDefCreateInfo4);

            dataFunc.stair_arrange(m_modelData.m_Slab[0], starDef1);
            dataFunc.stair_arrange(m_modelData.m_Slab[1], starDef2);
            dataFunc.stair_arrange(m_modelData.m_Slab[2], starDef3);
            dataFunc.stair_arrange(m_modelData.m_Slab[3], starDef4);

            var updateInfo = dataFunc.GetUpdateInfo();

            bool isok = my.ReflectAndCreateYDB(updateInfo, @"..\..\", "new.ydb");
            if (isok) Console.WriteLine("运行完成！");
            Console.ReadLine();
        }
    }
}
