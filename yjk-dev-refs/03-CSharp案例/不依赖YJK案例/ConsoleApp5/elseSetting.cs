using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

using CsToYjk;
using APIData;
using DataFuncApplication;

//本代码案例包含型钢截面定义、自定义工况荷载定义及布置、层间板布置、悬挑板布置、弧形网格创建、前处理计算参数设置、特殊构件定义、分组设置等，并于指定路径下生成ydb。

namespace ConsoleApp5
{
    class elseSetting
    {
        static void Main(string[] args)
        {
            DataFunc dataFunc = new DataFunc();
            //标准层
            Mdl_StdFlr StdFlr = dataFunc.StdFlr_Generate(3900);
            BzcPara para = new BzcPara();
            var str = para.GetValString();
            StdFlr.Para = str;

            //前处理计算参数设置，参数含义请查阅前处理接口说明--计算参数ID对应表
            Mdl_ProjectPara ProjectPara = dataFunc.ProjectPara_Set(101,"10102");

            //截面定义
            Mdl_ColSect defcol = dataFunc.ColSect_Def(6, 1, "400,400");

            Mdl_BeamSect defbeam = dataFunc.BeamSect_Def(6, 1, "250,600");
            //荷载定义
            Mdl_LoadSect beamload = dataFunc.Load_Def(12, "1.00,9.60");
            Mdl_LoadSect jointload = dataFunc.Load_Def(-1, "1001,1002,1003,1004,1005,1006");

            //自定义工况荷载定义（活载）
            var gkloadInfo = new GKLoadDefCreateInfo();
            gkloadInfo.SetDeadFacotr(0.5f)
                     .SetLiveFacotr(1, 1.1f, 1.1f, 1.1f)
                     .SetName("test_live")
                     .SetData("0.50,1.50,1.50,1.30,1.00,0.70,0.50,0.60,0.50,");

            Mdl_GKLoadDef GKLoad = dataFunc.GKLoad_Def(gkloadInfo);

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
                    var node = dataFunc.Joint_Generate(StdFlr.ID, xspans[i], yspans[j]);
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
            //生成网格
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

            //布置框架梁柱及荷载
            dataFunc.column_arrange(nodelist, defcol);
            var beam_list1 = dataFunc.beam_arrange(gridlist, defbeam);
            var beam_list2 = dataFunc.beam_arrange(gridlist, defbeam,0,-2000,-2000);
            dataFunc.load_arrange(beam_list1, beamload, GKLoad.kind);

            //层间板(节点按照逆时针方向排序)
            var midSlabNode = new List<Mdl_Joint>();
            midSlabNode.Add(nodelist[0][0]);
            midSlabNode.Add(nodelist[0][1]);
            midSlabNode.Add(nodelist[1][1]);
            midSlabNode.Add(nodelist[1][0]);

            var midslabCreateInfo = new MidSlabCreateInfo();
            midslabCreateInfo.SetThick(200)
                             .SetStdFlr(StdFlr)
                             .SetCentroid(4000, 4000)
                             .SetSurroundNodes(midSlabNode, -5900)
                             .SetDeadLive(5,2)
                             .SetSurroundGrids(gridlist);
            dataFunc.midslab_arrange(midslabCreateInfo);

            //悬挑板
            CantiSlabDefCreateInfo cantiSlabDefCreateInfo1 = new CantiSlabDefCreateInfo();
            cantiSlabDefCreateInfo1.SetKind(1).SetLength(0).SetWidth(600).SetThick(100);
            var CantiSlabDef1 = dataFunc.CantiSlab_Def(cantiSlabDefCreateInfo1);

            CantiSlabSegCreateInfo cantiSlabSegCreateInfo1 = new CantiSlabSegCreateInfo();
            cantiSlabSegCreateInfo1.SetStdFlrID(StdFlr.ID).SetEZ(0).SetEC(0).SetDR(1).SetGridID(gridlist[0].ID).SetSectID(CantiSlabDef1.ID).SetDeadLive(5, 2);
            dataFunc.CantiSlab_arrange(cantiSlabSegCreateInfo1);

            //自定义工况板荷载
            var slabInfo = new SlabCreateInfo();
            slabInfo.SetCentroid(4000, 4000)
                    .SetThick(300)
                    .SetStdFlr(StdFlr)
                    .SetCc(0)
                    .SetDeadLive(9, 9);

            var slab = dataFunc.slab_arrange(slabInfo);
            dataFunc.load_arrange(slab, GKLoad.kind, "10");


            //特殊梁
            var proper = new Property("SpBeam");
            proper.setVal(3,1);//连梁

            proper.setVal(0, 1);//左端铰接
            proper.setVal(1, 0);//右端固定

            var res = proper.GetValString();
            foreach(var beam in beam_list1)
            {
                dataFunc.property_arrange(beam.ID, "SpBeam", 27, res);
            }

            var node_list = new List<Mdl_Joint> { nodelist[0][0] };
            //节点荷载
            dataFunc.load_arrange(node_list, jointload);

            //弧形网格
            hxgrid(StdFlr.ID, dataFunc);

            //楼层组装
            dataFunc.Floors_Assemb(0, StdFlr, 1, 3600);

            //设置组
            var idlist = new List<int>();
            var zrcidnewlist = new List<int>();
            foreach (var beam in beam_list1)
            {
                idlist.Add(beam.ID);
                zrcidnewlist.Add(1037);
            }
            dataFunc.add_group("group01", idlist, zrcidnewlist);

            //提交建模数据
            dataFunc.DbModel_Assign();
            Hi_DbModelData model = dataFunc.GetDbModelData();
            Hi_AddToAndReadYjk my = new Hi_AddToAndReadYjk(model);
            bool isok = my.CreateYDB(@"..\..\", "elseSetting.ydb");
            if (isok) Console.WriteLine("运行完成！");
            Console.ReadLine();
        }
        //创建弧形网格
        static public void hxgrid(int StdFlrID, DataFunc dataFunc)
        {
            var center = dataFunc.Joint_Generate(StdFlrID, -2000, -2000);
            var pt1 = dataFunc.Joint_Generate(StdFlrID, -1000, -2000);
            var pt2 = dataFunc.Joint_Generate(StdFlrID, -2000, -3000);
            var axis = dataFunc.Axis_Generate(StdFlrID, -center.ID, pt1.ID);
            dataFunc.Grid_Generate(StdFlrID, pt1.ID, pt2.ID, axis.ID);
        }
    }
}
