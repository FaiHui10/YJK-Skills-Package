using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

using CsToYjk;
using APIData;
using DataFuncApplication;

//设置前处理计算参数

namespace ConsoleApp14
{
    class projPara
    {
        //设置工程参数
        static void setSpara(DataFunc dataFunc)
        {
            //风荷载信息_基本参数
            dataFunc.ProjectPara_Set(212, "3");
            //体型分段数&&迎风面系数&&背风面系数
            dataFunc.ProjectPara_Set(213, "2,3,4,6");
            //风荷载体型系数_X向
            dataFunc.ProjectPara_Set(214, "13,0.9,0.85,-0.55,0.1,0.9,0.85,-0.55,0.1,0.9,0.85,-0.55,0.1");
            //风荷载体型系数_Y向
            dataFunc.ProjectPara_Set(214, "13,0.9,0.85,-0.55,0.1,0.9,0.85,-0.55,0.1,0.9,0.85,-0.55,0.1");
            //考虑横风向风振
            dataFunc.ProjectPara_Set(207, "1");
            //截面形状
            dataFunc.ProjectPara_Set(228, "22804");
            //圆形截面_结构二阶平动周期
            dataFunc.ProjectPara_Set(231, "0.4");
        }

        static void Main(string[] args)
        {
            DataFunc dataFunc = new DataFunc();
            setSpara(dataFunc);
            //标准层
            Mdl_StdFlr StdFlr = dataFunc.StdFlr_Generate(3900);
            //截面定义
            Mdl_ColSect defcol = dataFunc.ColSect_Def(6, 1, "400,400");
            Mdl_BeamSect defbeam1 = dataFunc.BeamSect_Def(6, 1, "250,600");

            //荷载定义
            Mdl_LoadSect beamload1 = dataFunc.Load_Def(12, "1.00,9.60");
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
            var col_list = dataFunc.column_arrange(nodelist, defcol);
            var beam_list = dataFunc.beam_arrange(gridlist, defbeam1);

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
