using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

using CsToYjk;
using APIData;
using DataFuncApplication;

namespace ConsoleApp19
{
    class subBeam
    {
        static void Main(string[] args)
        {
            DataFunc dataFunc = new DataFunc();
            Hi_AddToAndReadYjk my = new Hi_AddToAndReadYjk();

            Hi_DbModelData m_modelData = my.ReadYdb(@"..\..\subbeam_pre.ydb");

            dataFunc.SetModel(m_modelData);
            var creatInfo1 = new SubBeamCreateInfo();
            creatInfo1.SetStartPoint(0, 3000, 0)
                      .SetEndPoint(3900, 300, 0)
                      .SetGridIDs(1032, 1036)
                      .SetStdFlrID(m_modelData.m_StdFlr[0].ID)
                      .SetSectID(m_modelData.m_BeamSect[0].ID);

            dataFunc.subbeam_arrange(creatInfo1.GetSubBeamSeg());

            var updateInfo = dataFunc.GetUpdateInfo();

            bool isok = my.ReflectAndCreateYDB(updateInfo, @"..\..\", "subbeam.ydb");
            if (isok) Console.WriteLine("运行完成！");
            Console.ReadLine();
        }
    }
}
