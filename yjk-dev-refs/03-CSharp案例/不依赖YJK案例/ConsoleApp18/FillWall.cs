using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

using CsToYjk;
using APIData;
using DataFuncApplication;

namespace ConsoleApp18
{
    class FillWall
    {
        static void Main(string[] args)
        {
            DataFunc dataFunc = new DataFunc();
            Hi_AddToAndReadYjk my = new Hi_AddToAndReadYjk();

            Hi_DbModelData m_modelData = my.ReadYdb(@"..\..\fillwall_pre.ydb");
            dataFunc.SetModel(m_modelData);
            //填充墙定义
            FillWallSectCreateInfo fillWallSectCreateInfo01 = new FillWallSectCreateInfo();
            fillWallSectCreateInfo01.SetE(4000)
                                  .SetRongZhong(10)
                                  .SetM(0)
                                  .SetThick(200)
                                  .SetFuncType(0)
                                  .SetKZJ(1)
                                  .SetU(0.15f);

            FillWallSectCreateInfo fillWallSectCreateInfo02 = new FillWallSectCreateInfo();
            fillWallSectCreateInfo02.SetE(4000)
                                  .SetRongZhong(15)
                                  .SetM(1)
                                  .SetThick(200)
                                  .SetFuncType(1)
                                  .SetKZJ(1)
                                  .SetU(0.15f);

            FillWallSectCreateInfo fillWallSectCreateInfo03 = new FillWallSectCreateInfo();
            fillWallSectCreateInfo03.SetE(4000)
                                  .SetRongZhong(10)
                                  .SetM(0)
                                  .SetThick(200)
                                  .SetFuncType(0)
                                  .SetKZJ(0)
                                  .SetU(0.15f);

            var fillWallDef01 = dataFunc.FillWall_Def(fillWallSectCreateInfo01);
            var fillWallDef02 = dataFunc.FillWall_Def(fillWallSectCreateInfo02);
            var fillWallDef03 = dataFunc.FillWall_Def(fillWallSectCreateInfo03);
            //按照网格的方式布置填充墙
            foreach (var grid in m_modelData.m_Grid)
            {
                FillWallSegCreateInfo fillWallSegCreateInfo = new FillWallSegCreateInfo();
                fillWallSegCreateInfo.SetGridID(grid.ID)
                                     .SetStdFlrID(m_modelData.m_StdFlr[0].ID)
                                     .SetDefID(fillWallDef01.ID);

                dataFunc.FillWall_arrange(fillWallSegCreateInfo);
            }
            //按照两点的方式布置填充墙
            FillWallSegCreateInfo fillWallSegCreateInfo_ByPt = new FillWallSegCreateInfo();
            fillWallSegCreateInfo_ByPt.SetPtBeg(0, 0)
                                 .SetPtEnd(2400, 2400)
                                 .SetGridID(0)
                                 .SetStdFlrID(m_modelData.m_StdFlr[0].ID)
                                 .SetDefID(fillWallDef03.ID);

            dataFunc.FillWall_arrange(fillWallSegCreateInfo_ByPt);

            //弧形填充墙
            FillWallSegCreateInfo fillWallSegCreateInfo_Cir = new FillWallSegCreateInfo();
            fillWallSegCreateInfo_Cir.SetPtCen(5000, 2500)
                                 .SetR(2000)
                                 .SetAgS(0)
                                 .SetGridID(0)
                                 .SetAgE(270)
                                 .SetStdFlrID(m_modelData.m_StdFlr[0].ID)
                                 .SetDefID(fillWallDef03.ID);

            dataFunc.FillWall_arrange(fillWallSegCreateInfo_Cir);

            var updateInfo = dataFunc.GetUpdateInfo();
            bool isok = my.ReflectAndCreateYDB(updateInfo, @"..\..\", "fillwall_post.ydb");
            Console.WriteLine("运行完成！");
            Console.ReadLine();
        }
    }
}
