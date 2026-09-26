using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

using CsToYjk;
using APIData;
using DataFuncApplication;

//本代码案例为创建一个钢结构模型，并于指定路径下生成ydb。

namespace ConsoleApp2
{
    class gjgtest
    {
        static void Main(string[] args)
        {
            DataFunc dataFunc = new DataFunc();
            //标准层
            Mdl_StdFlr StdFlr1 = dataFunc.StdFlr_Generate(3600,7,12);
            Mdl_StdFlr StdFlr2 = dataFunc.StdFlr_Generate(8000);
            //截面定义
            Mdl_ColSect defcol = dataFunc.ColSect_Def(5, 2, "20,650,400,28,400,28");
            Mdl_BeamSect defbeam1 = dataFunc.BeamSect_Def(5, 2, "18,900,300,26,300,26");
            Mdl_BeamSect defbeam2 = dataFunc.BeamSect_Def(5, 2, "10,500,300,22,300,22");
            Mdl_BeamSect defbeam3 = dataFunc.BeamSect_Def(5, 8, "152,142");
            Mdl_BraceSect defbrace = dataFunc.BraceSect_Def(5, 3, "150");
            //荷载定义

            //钢框架框架柱及框架梁布置
            var nodelist = new List<List<Mdl_Joint>>();
            var originpos = new List<int> { 0, 0 };
            var xspans = new List<int> { originpos[0], 6400, 6400, 6400, 6400, 6400, 6400 };
            var yspans = new List<int> { originpos[1], 3700, 11100 };
            nodelist = dataFunc.node_generate(xspans, yspans, StdFlr1);
            dataFunc.column_arrange(nodelist, defcol);
            //List<Mdl_Grid> gridlist = new List<Mdl_Grid>();
            var gridlist_beam1 = dataFunc.grid_generate(nodelist, 0, 1);
            var gridlist_beam2 = dataFunc.grid_generate(nodelist, 1, 0);
            dataFunc.beam_arrange(gridlist_beam1, defbeam1);
            dataFunc.beam_arrange(gridlist_beam2, defbeam2);

            //框架结构次梁布置
            xspans = new List<int> { 6400, 6400, 6400, 6400, 6400 };
            yspans = new List<int> { 1850 };
            nodelist = dataFunc.node_generate(xspans, yspans, StdFlr1);
            var gridlist = dataFunc.grid_generate(nodelist, 1, 0);
            dataFunc.beam_arrange(gridlist, defbeam2);
            xspans = new List<int> { 0, 6400, 6400, 6400, 6400, 6400, 6400 };
            yspans = new List<int> { 5550, 1850, 1850, 1850, 1850 };
            nodelist = dataFunc.node_generate(xspans, yspans, StdFlr1);
            gridlist = dataFunc.grid_generate(nodelist, 1, 0);
            dataFunc.beam_arrange(gridlist, defbeam2);

            //第2标准层
            //钢框架框架梁及框架柱布置
            xspans = new List<int> { 0, 6400, 6400, 6400, 6400, 6400, 6400 };
            yspans = new List<int> { 0, 14800 };
            nodelist = dataFunc.node_generate(xspans, yspans, StdFlr2);
            dataFunc.column_arrange(nodelist, defcol);
            gridlist_beam1 = dataFunc.grid_generate(nodelist, 1, 0);
            dataFunc.beam_arrange(gridlist_beam1, defbeam2);
            xspans = new List<int> { 0, 6400, 6400, 6400, 6400, 6400, 6400 };
            yspans = new List<int> { 7400 };
            var nodelist_H750 = dataFunc.node_generate(xspans, yspans, StdFlr2, 750);
            nodelist = dataFunc.merge_nodelist(nodelist, nodelist_H750);
            xspans = new List<int> { 0, 6400, 6400, 6400, 6400, 6400, 6400 };
            yspans = new List<int> { 3700, 7400 };
            var nodelist_H385= dataFunc.node_generate(xspans, yspans, StdFlr2, 385);
            nodelist = dataFunc.merge_nodelist(nodelist, nodelist_H385);
            var nodelist_brace= new List<List<Mdl_Joint>>();

            for(int i=0;i<4;++i)
            {
                var node_combine = new List<Mdl_Joint>();
                node_combine.Add(nodelist[0][i]);
                node_combine.Add(nodelist[1][i+1]);
                nodelist_brace.Add(node_combine);
                node_combine = new List<Mdl_Joint>();
                node_combine.Add(nodelist[0][i+1]);
                node_combine.Add(nodelist[1][i]);
                nodelist_brace.Add(node_combine);
                node_combine = new List<Mdl_Joint>();
                node_combine.Add(nodelist[nodelist.Count - 1][i]);
                node_combine.Add(nodelist[nodelist.Count - 2][i+1]);
                nodelist_brace.Add(node_combine);
                node_combine = new List<Mdl_Joint>();
                node_combine.Add(nodelist[nodelist.Count - 1][i+1]);
                node_combine.Add(nodelist[nodelist.Count - 2][i]);
                nodelist_brace.Add(node_combine);
            }
            gridlist_beam2= dataFunc.grid_generate(nodelist, 0, 1);
            dataFunc.beam_arrange(gridlist_beam2, defbeam1);
            //圆管及斜杆布置
            nodelist = dataFunc.merge_nodelist(nodelist_H385, nodelist_H750);
            var gridlist_beam3= dataFunc.grid_generate(nodelist, 1, 0);
            dataFunc.beam_arrange(gridlist_beam3, defbeam3);
            dataFunc.brace_arrange(nodelist_brace, defbrace);
            //标准层复制
            dataFunc.Floors_Assemb(0, StdFlr1, 1, 6000);
            dataFunc.Floors_Assemb(6000, StdFlr2, 1, 8000);
            //提交建模数据
            dataFunc.DbModel_Assign();
            Hi_DbModelData model = dataFunc.GetDbModelData();
            Hi_AddToAndReadYjk my = new Hi_AddToAndReadYjk(model);
            bool isok = my.CreateYDB(@"..\..\", "gjg.ydb");
            if (isok) Console.WriteLine("运行完成！");
            Console.ReadLine();
        }
    }
}
