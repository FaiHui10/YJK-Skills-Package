using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

using CsToYjk;
using APIData;
using DataFuncApplication;

//本代码案例为创建一个空间结构模型，并于指定路径下生成ydb。

namespace ConsoleApp4
{
    class kjjgtest
    {
        //一个简单的空间结构案例
        static void simpleDemo()
        {
            DataFunc dataFunc = new DataFunc();
            //标准层
            Mdl_StdFlr bzc = dataFunc.StdFlr_Generate(3600);
            //空间层
            Mdl_StdFlr kjc = dataFunc.SpcFlr_Generate();
            //定义柱
            Mdl_ColSect defcol2 = dataFunc.ColSect_Def(5, 2, "9,250,250,14,250,14");    //钢柱
            //定义梁
            Mdl_BeamSect defbeam1 = dataFunc.BeamSect_Def(5, 2, "6,194,150,9,150,9");   //钢梁
            //定义斜杆
            Mdl_BraceSect defbrace1 = dataFunc.BraceSect_Def(5, 8, "102,92");  //钢斜杆
            var xpos = new List<int> { 0, 2000, 4000 };
            var ypos = new List<int> { 0, 2000 };
            var zpos = new List<int> { 0, 4000, 6000 };

            var nodelists = new List<List<List<Mdl_Joint>>>();
            var gridlist = new List<Mdl_Grid>();
            //新建节点和网格，2层
            for (int k = 0; k < 2; k++)
            {
                var nodelist = new List<List<Mdl_Joint>>();
                for (int i = 0; i < xpos.Count; ++i)
                {
                    List<Mdl_Joint> _nodelist = new List<Mdl_Joint>();
                    for (int j = 0; j < ypos.Count; ++j)
                    {
                        var node = dataFunc.Joint_Generate(kjc.ID, xpos[i], ypos[j], zpos[k + 1]);
                        _nodelist.Add(node);
                    }
                    nodelist.Add(_nodelist);
                }

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

                nodelists.Add(nodelist);
            }

            //布置梁
            var beam_list = dataFunc.beam_arrange(gridlist, defbeam1);
            //布置水平斜杆
            dataFunc.brace_arrange(nodelists[0][0][0], nodelists[0][1][1], defbrace1);
            dataFunc.brace_arrange(nodelists[0][1][1], nodelists[0][2][0], defbrace1);
            dataFunc.brace_arrange(nodelists[1][0][0], nodelists[1][1][1], defbrace1);
            dataFunc.brace_arrange(nodelists[1][1][1], nodelists[1][2][0], defbrace1);
            //布置竖直斜杆
            dataFunc.brace_arrange(nodelists[1][0][0], nodelists[0][1][0], defbrace1);
            dataFunc.brace_arrange(nodelists[0][1][0], nodelists[1][2][0], defbrace1);
            dataFunc.brace_arrange(nodelists[1][0][1], nodelists[0][1][1], defbrace1);
            dataFunc.brace_arrange(nodelists[0][1][1], nodelists[1][2][1], defbrace1);

            dataFunc.brace_arrange(nodelists[0][1][0], nodelists[1][1][0], defbrace1);
            dataFunc.brace_arrange(nodelists[0][1][1], nodelists[1][1][1], defbrace1);

            //布置柱
            dataFunc.column_arrange(nodelists[1][0][0], defcol2);
            dataFunc.column_arrange(nodelists[1][0][1], defcol2);
            dataFunc.column_arrange(nodelists[1][2][0], defcol2);
            dataFunc.column_arrange(nodelists[1][2][1], defcol2);

            //提交建模数据
            dataFunc.DbModel_Assign();
            Hi_DbModelData model = dataFunc.GetDbModelData();
            Hi_AddToAndReadYjk my = new Hi_AddToAndReadYjk(model);
            bool isok = my.CreateYDB(@"..\..\", "kjjg.ydb");
            if (isok) Console.WriteLine("运行完成！");
            Console.ReadLine();

        }

        static void originDemo()
        {
            DataFunc dataFunc = new DataFunc();
            //标准层
            Mdl_StdFlr bzc = dataFunc.StdFlr_Generate(3600);
            //空间层
            Mdl_StdFlr kjc = dataFunc.SpcFlr_Generate();
            //定义柱
            Mdl_ColSect defcol1 = dataFunc.ColSect_Def(6, 1, "600,600");
            Mdl_ColSect defcol2 = dataFunc.ColSect_Def(6, 1, "800,1100");
            //定义梁
            Mdl_BeamSect defbeam1 = dataFunc.BeamSect_Def(6, 1, "350,800");
            Mdl_BeamSect defbeam2 = dataFunc.BeamSect_Def(6, 1, "600,900");
            //定义斜杆
            Mdl_BraceSect defbrace1 = dataFunc.BraceSect_Def(5, 8, "180,166");
            Mdl_BraceSect defbrace2 = dataFunc.BraceSect_Def(5, 8, "102,92");
            Mdl_BraceSect defbrace3 = dataFunc.BraceSect_Def(5, 8, "219,199");
            //定义荷载
            Mdl_LoadSect beamload1 = dataFunc.Load_Def(12, "1.00,8.00,0.00,0.00,0.00,0.00,0.00");
            Mdl_LoadSect beamload2 = dataFunc.Load_Def(12, "1.00,8.50,0.00,0.00,0.00,0.00,0.00");
            //布置框架结构
            var originpos = new List<List<int>>();
            originpos.Add(new List<int> { 0, 0 });
            originpos.Add(new List<int> { 0, 27900 });
            originpos.Add(new List<int> { 64800, 0 });
            originpos.Add(new List<int> { 64800, 27900 });

            var xspans = new List<int>();
            var yspans = new List<int>();
            foreach (var node in originpos)
            {
                xspans = new List<int> { node[0], 3600, 3600, 3600, 3600 };
                yspans = new List<int> { node[1], 8400 };
                var nodelist = dataFunc.node_generate(xspans, yspans, bzc);
                dataFunc.column_arrange(nodelist, defcol1);
                var gridlist_beam1 = dataFunc.grid_generate(nodelist, 1, 1);
                var beam_list = dataFunc.beam_arrange(gridlist_beam1, defbeam1);
                dataFunc.load_arrange(beam_list, beamload1);
            }
            originpos.Clear();
            originpos.Add(new List<int> { 0, 8400 });
            originpos.Add(new List<int> { 64800, 8400 });
            foreach (var node in originpos)
            {
                xspans = new List<int> { node[0], 3600, 3600, 3600, 3600 };
                yspans = new List<int> { node[1], 6500, 6500, 6500 };
                var nodelist = dataFunc.node_generate(xspans, yspans, bzc);
                dataFunc.column_arrange(nodelist, defcol1);
                var gridlist_beam2 = dataFunc.grid_generate(nodelist, 1, 1);
                var beam_list = dataFunc.beam_arrange(gridlist_beam2, defbeam1);
                dataFunc.load_arrange(beam_list, beamload1);
                xspans = new List<int> { node[0], 14400 };
                yspans = new List<int> { 11650, 6500, 6500 };
                nodelist = dataFunc.node_generate(xspans, yspans, bzc);
                var gridlist_beam3 = dataFunc.grid_generate(nodelist, 1, 0);
                beam_list = dataFunc.beam_arrange(gridlist_beam3, defbeam1);
                dataFunc.load_arrange(beam_list, beamload2);
            }
            xspans = new List<int> { 14400, 7200, 7200, 7200, 7200, 7200, 7200, 7200 };
            yspans = new List<int> { 0, 36300 };
            {
                var nodelist = dataFunc.node_generate(xspans, yspans, bzc);
                dataFunc.column_arrange(nodelist, defcol2);
                var gridlist_beam3 = dataFunc.grid_generate(nodelist, 1, 0);
                var beam_list = dataFunc.beam_arrange(gridlist_beam3, defbeam2);
                dataFunc.load_arrange(beam_list, beamload1);
                dataFunc.slab_arrange(39600, 18150, 0, bzc, true);
            }
            originpos.Clear();
            originpos.Add(new List<int> { 20400, 0 });
            //布置主桁架
            for (int i = 0; i < 6; ++i)
            {
                xspans = new List<int> { originpos[0][0] + i * 7200, 2400 };
                yspans = new List<int> { };
                for (int j = 0; j < 15; ++j)
                {
                    yspans.Add(2420);
                }
                yspans.Insert(0, originpos[0][1]);
                var node_down_y = new List<int>();
                for (int j = 0; j < 14; ++j)
                {
                    node_down_y.Add(2420);
                }
                node_down_y.Insert(0, originpos[0][1] + 2420 / 2);

                var node_down = dataFunc.node_generate(new List<int>() { xspans[0] + xspans[1] / 2 }, node_down_y, kjc, 10707);
                var nodelist = dataFunc.node_generate(xspans, yspans, kjc, 13100);
                var nodelist_brace1 = new List<List<Mdl_Joint>>();
                var nodelist_brace2 = new List<List<Mdl_Joint>>();
                var nodelist_brace3 = new List<List<Mdl_Joint>>();
                for (int j = 0; j < 15; ++j)
                {
                    nodelist_brace1.Add(new List<Mdl_Joint>() { nodelist[0][j], nodelist[0][j + 1] });
                }
                for (int j = 0; j < 15; ++j)
                {
                    nodelist_brace1.Add(new List<Mdl_Joint>() { nodelist[1][j], nodelist[1][j + 1] });
                }
                for (int j = 0; j < 15; ++j)
                {
                    nodelist_brace2.Add(new List<Mdl_Joint>() { node_down[0][j], nodelist[0][j] });
                    nodelist_brace2.Add(new List<Mdl_Joint>() { node_down[0][j], nodelist[1][j] });
                    nodelist_brace2.Add(new List<Mdl_Joint>() { node_down[0][j], nodelist[0][j + 1] });
                    nodelist_brace2.Add(new List<Mdl_Joint>() { node_down[0][j], nodelist[1][j + 1] });
                    nodelist_brace2.Add(new List<Mdl_Joint>() { nodelist[0][j + 1], nodelist[1][j + 1] });
                    if ((j + 1) % 2 == 1)
                    {
                        nodelist_brace2.Add(new List<Mdl_Joint>() { nodelist[0][j + 1], nodelist[1][j] });
                    }
                    else
                    {
                        nodelist_brace2.Add(new List<Mdl_Joint>() { nodelist[1][j + 1], nodelist[0][j] });
                    }
                }
                dataFunc.brace_arrange(nodelist_brace2, defbrace2);
                for (int j = 0; j < node_down[0].Count - 1; ++j)
                {
                    nodelist_brace3.Add(new List<Mdl_Joint>() { node_down[0][j], node_down[0][j + 1] });
                }
                dataFunc.brace_arrange(nodelist_brace1, defbrace1);
                dataFunc.brace_arrange(nodelist_brace3, defbrace3);
            }
            //布置次桁架
            var SecTruss_infos_left = new List<List<int>>();
            var SecTruss_infos_right = new List<List<int>>();
            var SecTruss_infos_mid = new List<List<int>>();
            SecTruss_infos_left.Add(new List<int> { 14400, 7260, 2000, 3 });
            SecTruss_infos_left.Add(new List<int> { 14400, 14520, 2000, 3 });
            SecTruss_infos_left.Add(new List<int> { 14400, 19360, 2000, 3 });
            SecTruss_infos_left.Add(new List<int> { 14400, 26620, 2000, 3 });
            SecTruss_infos_right.Add(new List<int> { 58800, 7260, 2000, 3 });
            SecTruss_infos_right.Add(new List<int> { 58800, 14520, 2000, 3 });
            SecTruss_infos_right.Add(new List<int> { 58800, 19360, 2000, 3 });
            SecTruss_infos_right.Add(new List<int> { 58800, 26620, 2000, 3 });
            for (int r = 0; r < 2; ++r)
            {
                for (int c = 0; c < 5; ++c)
                {
                    var tmp = new List<int>() { 22800 + c * 7200, 14520 + r * 4840, 1600, 3 };
                    SecTruss_infos_mid.Add(tmp);
                }
            }
            var SecTruss_infos = new List<List<int>>();
            SecTruss_infos.AddRange(SecTruss_infos_left);
            SecTruss_infos.AddRange(SecTruss_infos_right);
            SecTruss_infos.AddRange(SecTruss_infos_mid);
            foreach (var SecTruss_info in SecTruss_infos)
            {
                var nodelist_brace1 = new List<List<Mdl_Joint>>();
                var nodelist_brace2 = new List<List<Mdl_Joint>>();
                var nodelist_brace3 = new List<List<Mdl_Joint>>();
                yspans = new List<int>() { SecTruss_info[1], 2420 };
                xspans.Clear();
                for (int j = 0; j < SecTruss_info[3]; ++j)
                {
                    xspans.Add(SecTruss_info[2]);
                }
                xspans.Insert(0, SecTruss_info[0]);
                var node_down_x = new List<int>() { SecTruss_info[2], SecTruss_info[2] };
                node_down_x.Insert(0, SecTruss_info[0] + SecTruss_info[2] / 2);
                var node_down = dataFunc.node_generate(node_down_x, new List<int>() { yspans[0] + yspans[1] / 2 }, kjc, 10707);
                var nodelist = dataFunc.node_generate(xspans, yspans, kjc, 13100);
                for (int j = 0; j < SecTruss_info[3]; ++j)
                {
                    nodelist_brace1.Add(new List<Mdl_Joint>() { nodelist[j][0], nodelist[j + 1][0] });
                }
                for (int j = 0; j < SecTruss_info[3]; ++j)
                {
                    nodelist_brace1.Add(new List<Mdl_Joint>() { nodelist[j][1], nodelist[j + 1][1] });
                }
                for (int j = 0; j < SecTruss_info[3]; ++j)
                {
                    nodelist_brace2.Add(new List<Mdl_Joint>() { node_down[j][0], nodelist[j][0] });
                    nodelist_brace2.Add(new List<Mdl_Joint>() { node_down[j][0], nodelist[j][1] });
                    nodelist_brace2.Add(new List<Mdl_Joint>() { node_down[j][0], nodelist[j + 1][0] });
                    nodelist_brace2.Add(new List<Mdl_Joint>() { node_down[j][0], nodelist[j + 1][1] });
                    nodelist_brace2.Add(new List<Mdl_Joint>() { nodelist[j + 1][0], nodelist[j + 1][1] });
                    if ((j + 1) % 2 == 1)
                    {
                        nodelist_brace2.Add(new List<Mdl_Joint>() { nodelist[j + 1][0], nodelist[j][1] });
                    }
                    else
                    {
                        nodelist_brace2.Add(new List<Mdl_Joint>() { nodelist[j + 1][1], nodelist[j][0] });
                    }
                }
                dataFunc.brace_arrange(nodelist_brace2, defbrace2);
                for (int j = 0; j < node_down[0].Count - 1; ++j)
                {
                    nodelist_brace3.Add(new List<Mdl_Joint>() { node_down[0][j], node_down[0][j + 1] });
                }
                dataFunc.brace_arrange(nodelist_brace2, defbrace2);
                dataFunc.brace_arrange(nodelist_brace1, defbrace2);
            }

            //布置此桁架的下弦杆
            xspans = new List<int> { 15400, 2000, 2000, 2200 };
            yspans = new List<int> { 8470, 7260, 4840, 7260 };
            dataFunc.simple_truss(xspans, yspans, 10707, kjc, defbrace2, 1, 0);
            xspans = new List<int> { 57600, 2200, 2000, 2000 };
            yspans = new List<int> { 8470, 7260, 4840, 7260 };
            dataFunc.simple_truss(xspans, yspans, 10707, kjc, defbrace2, 1, 0);
            originpos.Clear();
            originpos.Add(new List<int> { 21600, 15730 });
            originpos.Add(new List<int> { 28800, 15730 });
            originpos.Add(new List<int> { 36000, 15730 });
            originpos.Add(new List<int> { 43200, 15730 });
            originpos.Add(new List<int> { 50400, 15730 });
            foreach (var p in originpos)
            {
                xspans = new List<int> { p[0], 2000, 1600, 1600, 2000 };
                yspans = new List<int> { p[1], 4840 };
                dataFunc.simple_truss(xspans, yspans, 10707, kjc, defbrace2, 1, 0);
            }
            //布置桁架上弦杆与周边框架搭接的部分
            xspans = new List<int> { 14400, 6000, 2400, 4800, 2400, 4800, 2400, 4800, 2400, 4800, 2400, 4800, 2400, 6000 };
            yspans = new List<int> { 0, 36300 };
            dataFunc.simple_truss(xspans, yspans, 13100, kjc, defbrace2, 1, 0, -500);
            xspans = new List<int> { 14400, 50400 };
            yspans = new List<int> { 0, 7260, 2420, 4840, 2420, 2420, 2420, 4840, 2420, 7260 };
            dataFunc.simple_truss(xspans, yspans, 13100, kjc, defbrace2, 0, 1, -500);
            //标准层复制
            dataFunc.Floors_Assemb(0, bzc, 3, 4200);
            dataFunc.Floors_Assemb(0, kjc, 1, 0);
            //提交建模数据
            dataFunc.DbModel_Assign();
            Hi_DbModelData model = dataFunc.GetDbModelData();
            Hi_AddToAndReadYjk my = new Hi_AddToAndReadYjk(model);
            bool isok = my.CreateYDB(@"..\..\", "kjjg.ydb");
            if (isok) Console.WriteLine("运行完成！");
            Console.ReadLine();
        }
        static void Main(string[] args)
        {
            simpleDemo();
        }
    }
}
