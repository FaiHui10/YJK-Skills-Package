using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

using CsToYjk;
using APIData;
using DataFuncApplication;

//本代码案例为创建一个带加腋梁及加腋板的框架结构模型，并于指定路径下生成ydb（请修改生成ydb的目录）。

namespace ConsoleApp11
{
    class jykj
    {
        static void Main(string[] args)
        {
            DataFunc dataFunc = new DataFunc();
            //标准层
            Mdl_StdFlr StdFlr = dataFunc.StdFlr_Generate(3900);
            BzcPara para = new BzcPara();
            var str = para.GetValString();

            //截面定义
            Mdl_ColSect defcol = dataFunc.ColSect_Def(6, 1, "400,400");
            Mdl_BeamSect defbeam = dataFunc.BeamSect_Def(6, 1, "250,600");
            Mdl_BeamJY defbeamjy = dataFunc.BeamJYSect_Def(0, "1000,500,400", "jy01");
            Mdl_SlabJYDef defslabjy1 = dataFunc.SlabJYSect_Def(1, "1500.00,500.00,0.00,0.00,");
            Mdl_SlabJYDef defslabjy2 = dataFunc.SlabJYSect_Def(2, "0.00,0.00,1500.00,500.00,");

            //生成节点
            List<Mdl_Joint> nodelist = new List<Mdl_Joint>();
            for(int i=0;i<2;++i)
            {
                for(int j=0;j<2;++j)
                {
                   var node= dataFunc.Joint_Generate(StdFlr.ID, i*10000, j*10000);
                    nodelist.Add(node);
                }
            }

            //生成轴线及网格
            List<Mdl_Axis> axislist = new List<Mdl_Axis>();
            axislist.Add(dataFunc.Axis_Generate(StdFlr.ID, nodelist[0].ID, nodelist[1].ID));
            axislist.Add(dataFunc.Axis_Generate(StdFlr.ID, nodelist[2].ID, nodelist[3].ID));
            axislist.Add(dataFunc.Axis_Generate(StdFlr.ID, nodelist[1].ID, nodelist[3].ID));
            axislist.Add(dataFunc.Axis_Generate(StdFlr.ID, nodelist[0].ID, nodelist[2].ID));

            List<Mdl_Grid> gridlist = new List<Mdl_Grid>();
            gridlist.Add(dataFunc.Grid_Generate(StdFlr.ID, nodelist[0].ID, nodelist[1].ID, axislist[0].ID));
            gridlist.Add(dataFunc.Grid_Generate(StdFlr.ID, nodelist[2].ID, nodelist[3].ID, axislist[1].ID));
            gridlist.Add(dataFunc.Grid_Generate(StdFlr.ID, nodelist[1].ID, nodelist[3].ID, axislist[2].ID));
            gridlist.Add(dataFunc.Grid_Generate(StdFlr.ID, nodelist[0].ID, nodelist[2].ID, axislist[3].ID));

            //布置梁
            var beam_list = dataFunc.beam_arrange(gridlist, defbeam);
            //布置柱
            var col_list = dataFunc.column_arrange(nodelist, defcol);
            //加腋梁
            foreach(var beam in beam_list)
            {
                dataFunc.beamjy_arrange(defbeamjy, beam);
            }
            //楼板布置
            var slab = dataFunc.slab_arrange(5000, 5000, 300, StdFlr, false);
            //加腋板
            dataFunc.slabjy_arrange(defslabjy2, gridlist[0]);
            dataFunc.slabjy_arrange(defslabjy1, gridlist[3]);
            dataFunc.slabjy_arrange(defslabjy1, gridlist[1]);
            dataFunc.slabjy_arrange(defslabjy2, gridlist[2]);

            //楼层组装
            dataFunc.Floors_Assemb(0, StdFlr, 1, 3600);
            //提交建模数据
            dataFunc.DbModel_Assign();
            Hi_DbModelData model = dataFunc.GetDbModelData();
            Hi_AddToAndReadYjk my = new Hi_AddToAndReadYjk(model);
            bool isok = my.CreateYDB(@"C:\Users\10497\Desktop\ydb", "jykj.ydb");
            if (isok) Console.WriteLine("运行完成！");
            Console.ReadLine();
        }
    }
}
