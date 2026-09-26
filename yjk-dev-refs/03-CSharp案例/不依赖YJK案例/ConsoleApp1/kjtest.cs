using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

using CsToYjk;
using APIData;
using DataFuncApplication;

//本代码案例为创建一个框架结构模型，并于指定路径下生成ydb。

namespace ConsoleApp1
{
    class kjtest
    {
        static void Main(string[] args)
        {
            DataFunc dataFunc = new DataFunc();
            //标准层
            Mdl_StdFlr StdFlr = dataFunc.StdFlr_Generate(3900);
            //截面定义
            Mdl_ColSect defcol = dataFunc.ColSect_Def(6, 1, "400,400");
            Mdl_BeamSect defbeam1 = dataFunc.BeamSect_Def(6, 1, "250,600");
            Mdl_BeamSect defbeam2 = dataFunc.BeamSect_Def(6, 1, "200,400");
            var colCapDefInfo = new ColCapSectCreateInfo();
            colCapDefInfo.SetKind(1)
                         .SetSectPara(1000, 1000, 1000, 2000, 1000, 2000)
                         .SetName("柱帽截面01");
            Mdl_ColCapSect colCapSect = dataFunc.ColCapSect_Def(colCapDefInfo);
            //荷载定义
            Mdl_LoadSect beamload1 = dataFunc.Load_Def(12, "1.00,9.60");
            Mdl_LoadSect beamload2 = dataFunc.Load_Def(12, "1.00,5.50");
            //生成节点
            var nodelist = new List<List<Mdl_Joint>>();
            var originpos = new List<int> { 0, 0 };
            var xpos = new List<int> { originpos[0], 3900, 7800, 11700, 15600, 19500, 23400 };
            var ypos = new List<int> { originpos[1], 6700, 12000 };

            for (int i = 0; i < xpos.Count; ++i)
            {
                List<Mdl_Joint> _nodelist = new List<Mdl_Joint>();
                for (int j = 0; j < ypos.Count; ++j)
                {
                    var node = dataFunc.Joint_Generate(StdFlr.ID, xpos[i], ypos[j]);
                    _nodelist.Add(node);
                }
                nodelist.Add(_nodelist);
            }
            var gridlist = new List<Mdl_Grid>();
            //生成网格
            //竖向
            foreach (var _nodelist in nodelist)
            {
                for (int i = 0; i < _nodelist.Count - 1; ++i)
                {
                    var axis = dataFunc.Axis_Generate(StdFlr.ID, _nodelist[i].ID, _nodelist[i + 1].ID);
                    var grid = dataFunc.Grid_Generate(StdFlr.ID, _nodelist[i].ID, _nodelist[i + 1].ID, axis.ID);
                    gridlist.Add(grid);
                }
            }

            //横向
            for (int i = 0; i < nodelist.Count() - 1; ++i)
            {
                for (int j = 0; j < nodelist[i].Count; ++j)
                {
                    var axis = dataFunc.Axis_Generate(StdFlr.ID, nodelist[i][j].ID, nodelist[i + 1][j].ID);
                    var grid = dataFunc.Grid_Generate(StdFlr.ID, nodelist[i][j].ID, nodelist[i + 1][j].ID, axis.ID);
                    gridlist.Add(grid);
                }
            }

            //布置框架梁柱
            var col_list= dataFunc.column_arrange(nodelist, defcol);
            var beam_list = dataFunc.beam_arrange(gridlist, defbeam1);

            //布置柱帽
            dataFunc.colCap_arrange(col_list[0], colCapSect);


            //布置板
            var slabInfo = new SlabCreateInfo();
            slabInfo.SetCentroid(1950, 9350)
                    .SetThick(300)
                    .SetStdFlr(StdFlr)
                    .SetCc(0)
                    .SetDeadLive(9, 9);

            var slab = dataFunc.slab_arrange(slabInfo);

            //布置梁上荷载
            dataFunc.load_arrange(beam_list, beamload1);

            //标准层复制
            dataFunc.Floors_Assemb(0, StdFlr, 6, 3600);
            //提交建模数据
            dataFunc.DbModel_Assign();
            Hi_DbModelData model = dataFunc.GetDbModelData();
            Hi_AddToAndReadYjk my = new Hi_AddToAndReadYjk(model);
            bool isok = my.CreateYDB(@"..\..\", "kj.ydb");
            if (isok) Console.WriteLine("运行完成！");
            Console.ReadLine();
        }
    }
}
