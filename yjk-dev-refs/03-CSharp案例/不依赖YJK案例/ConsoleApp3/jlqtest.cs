using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

using CsToYjk;
using APIData;
using DataFuncApplication;

//本代码案例为创建一个剪力墙结构模型，并于指定路径下生成ydb。

namespace ConsoleApp3
{
    class jlqtest
    {
        static void Main(string[] args)
        {
            DataFunc dataFunc = new DataFunc();
            //标准层
            Mdl_StdFlr StdFlr1 = dataFunc.StdFlr_Generate(3000,12,3);
            //墙定义
            Mdl_WallSect defwall = dataFunc.WallSect_Def(6,1,200);
            //墙洞定义
            Mdl_WallHoleDef defwallhole = dataFunc.WallHoleDef(900,2500);
            //剪力墙布置,墙洞布置
            var originpos = new List<List<int>>();
            originpos.Add(new List<int> { 0, 0 });
            originpos.Add(new List<int> { 7000, 8000 });
            originpos.Add(new List<int> { 10500, -8000 });
            originpos.Add(new List<int> { 28000, 0 });
            originpos.Add(new List<int> { 21000, 8000 });
            originpos.Add(new List<int> { 17500, -8000 });
            foreach (var node in originpos)
            {
                var xspans = new List<int> { node[0], 3500, 3500 };
                var yspans = new List<int> { node[1], 3000, 5000 };
                var nodelist = dataFunc.node_generate(xspans, yspans, StdFlr1);
                var gridlist = dataFunc.grid_generate(nodelist,1,1);
                dataFunc.wall_arrange(gridlist, defwall);
                dataFunc.wallhole_arrange(gridlist, defwallhole);
            }
            originpos.Clear();
            originpos.Add(new List<int> { 7000, 0 });
            originpos.Add(new List<int> { 17500, 0 });

            foreach (var node in originpos)
            {
                var xspans = new List<int> { node[0], 3500, 3500, 3500 };
                var yspans = new List<int> { node[1], 8000 };
                var nodelist = dataFunc.node_generate(xspans, yspans, StdFlr1);
                var gridlist = dataFunc.grid_generate(nodelist, 1, 1);
                dataFunc.wall_arrange(gridlist, defwall);
                dataFunc.wallhole_arrange(gridlist, defwallhole);
            }
            //标准层复制
            dataFunc.Floors_Assemb(0, StdFlr1, 18, 3000);
            //提交建模数据
            dataFunc.DbModel_Assign();
            Hi_DbModelData model = dataFunc.GetDbModelData();
            Hi_AddToAndReadYjk my = new Hi_AddToAndReadYjk(model);
            bool isok = my.CreateYDB(@"D:\5.C#二次开发\test\ConsoleApp1\ConsoleApp3", "jlq.ydb");
            if (isok) Console.WriteLine("运行完成！");
            Console.ReadLine();
        }
    }
}
