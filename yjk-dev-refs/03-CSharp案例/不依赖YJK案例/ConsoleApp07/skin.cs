using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

using CsToYjk;
using APIData;
using DataFuncApplication;

//本代码案例实现如下功能：
//一、生成蒙皮及蒙皮荷载。

namespace ConsoleApp07
{
    class skin
    {
        static void Main(string[] args)
        {
            DataFunc dataFunc = new DataFunc();

            //截面定义
            Mdl_ColSect defcol = dataFunc.ColSect_Def(6, 1, "400,400");
            Mdl_BeamSect defbeam = dataFunc.BeamSect_Def(6, 1, "250,600");
            Mdl_LoadSect beamload = dataFunc.Load_Def(12, "1.00,9.60");
            var defskin = dataFunc.SkinLoadSect_Def(0, 0, 1.5f, 0);

            //空间层
            Mdl_StdFlr kjc = dataFunc.SpcFlr_Generate();
            Mdl_StdFlr bzc = dataFunc.StdFlr_Generate(3600);

            //生成节点
            var nodelist = new List<List<Mdl_Joint>>();
            var originpos = new List<int> { 0, 0 };

            var xspans = new List<int> { originpos[0], 8000 };
            var yspans = new List<int> { originpos[1], 8000 };

            for (int i = 0; i < xspans.Count; ++i)
            {
                List<Mdl_Joint> _nodelist = new List<Mdl_Joint>();
                for (int j = 0; j < yspans.Count; ++j)
                {
                    var node = dataFunc.Joint_Generate(kjc.ID, xspans[i], yspans[j]);
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
                    var axis = dataFunc.Axis_Generate(kjc.ID, _nodelist[i].ID, _nodelist[i + 1].ID);
                    var grid = dataFunc.Grid_Generate(kjc.ID, _nodelist[i].ID, _nodelist[i + 1].ID, axis.ID);
                    gridlist.Add(grid);
                }
            }
            //生成网格
            //横向
            for (int i = 0; i < nodelist.Count() - 1; ++i)
            {
                for (int j = 0; j < nodelist[i].Count; ++j)
                {
                    var axis = dataFunc.Axis_Generate(kjc.ID, nodelist[i][j].ID, nodelist[i + 1][j].ID);
                    var grid = dataFunc.Grid_Generate(kjc.ID, nodelist[i][j].ID, nodelist[i + 1][j].ID, axis.ID);
                    gridlist.Add(grid);
                }
            }

            //布置框架梁柱及荷载
            dataFunc.column_arrange(nodelist, defcol);
            var beam_list = new List<Mdl_BeamSeg>();
            beam_list = dataFunc.beam_arrange(gridlist, defbeam);
            dataFunc.load_arrange(beam_list, beamload);

            var nodelist_temp = new List<Mdl_Joint>();
            nodelist_temp.Add(nodelist[1][0]);
            nodelist_temp.Add(nodelist[1][1]);
            nodelist_temp.Add(nodelist[0][1]);
            nodelist_temp.Add(nodelist[0][0]);

            //添加蒙皮
            SkinCreateInfo skinInfo = new SkinCreateInfo();
            skinInfo.SetDeadLive(5, 2)
                    .SetMaterialStyle(1)
                    .SetDirection(new Vector(0.0f, 0.0f, 0.0f))
                    .SetSurroundPt(nodelist_temp)
                    .SetNDirection("0,0,0,0,0,1,10");

            var skin = dataFunc.skin_arrange(skinInfo);
            dataFunc.skinLoad_arrange(skin, defskin);


            //提交建模数据
            dataFunc.Floor_Assemb(bzc, 0, 3600);
            dataFunc.DbModel_Assign();
            Hi_DbModelData model = dataFunc.GetDbModelData();
            Hi_AddToAndReadYjk my = new Hi_AddToAndReadYjk(model);
            bool isok = my.CreateYDB(@"..\..\", "skin.ydb");
            if (isok) Console.WriteLine("运行完成！");
            Console.ReadLine();
        }
    }
}
