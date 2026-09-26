using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

using CsToYjk;
using APIData;
using DataFuncApplication;

//建议先看reflec_test01案例再看reflec_test02案例,其余说明详见“说明.txt”

namespace ConsoleApp15
{
    class linkYjk
    {
        //测试修改节点,配合test01使用
        static void reflec_test01()
        {
            var model = getDbModelData();
            var node = model.m_Joint[0];
            Hi_UpdateInfo updateInfo = new Hi_UpdateInfo();
            updateInfo.unionID = model.unionID;
            for (int i = 0; i < 10; ++i)
            {
                updateInfo.Clear();
                node.X -= 1000;
                updateInfo.ModifyObj(node);
                transferData(updateInfo);
            }
            for (int i = 0; i < 10; ++i)
            {
                updateInfo.Clear();
                node.X += 1000;
                updateInfo.ModifyObj(node);
                transferData(updateInfo);
            }
        }

        //框架的新增及删除(梁、柱、墙、墙洞、杆件)，配合test02使用
        static void reflec_test02()
        {
            reflec_Def();
            var model = getDbModelData();
            var stdFlrID = model.m_StdFlr[0].ID;
            var defcol = model.m_ColSect[0];
            var defbeam = model.m_BeamSect[0];
            var braceSect = model.m_BraceSect[0];
            var wallSect = model.m_WallSect[0];
            var wallHoleDef = model.m_WallHoleDef[0];

            List<List<Mdl_Joint>> nodelist = new List<List<Mdl_Joint>>();
            List<int> spans = new List<int> { 2, 4, 6, 8, 6, 4, 2, 0 };

            DataFunc dataFunc = new DataFunc();
            var unionID = getUnionID();
            dataFunc.InitForLink(unionID);

            for (int i = 0; i < spans.Count(); ++i)
            {
                int spans_cur = spans[i];
                int span_pre = nodelist.Count();
                if (spans_cur > span_pre)
                {
                    //新增
                    AddMember(span_pre, spans_cur);
                }
                else if (spans_cur < span_pre)
                {
                    //减少
                    DeleteMember(span_pre, spans_cur);
                }
                else
                {
                    //不增加也不减少
                }
            }

            void DeleteMember(int span_pre, int spans_cur)
            {
                Hi_UpdateInfo updateInfo = new Hi_UpdateInfo();
                for (int i = spans_cur; i < span_pre; ++i)
                {
                    updateInfo.DeleteObj(nodelist[i][0]);
                    updateInfo.DeleteObj(nodelist[i][1]);
                }
                transferData(updateInfo);
            }

            void AddMember(int span_pre, int spans_cur)
            {
                List<Mdl_Joint> _nodelist = new List<Mdl_Joint>();
                List<List<Mdl_Joint>> node2grid_X = new List<List<Mdl_Joint>>();
                List<List<Mdl_Joint>> node2grid_Y = new List<List<Mdl_Joint>>();

                //新生成节点、柱
                for (int i = span_pre; i < spans_cur; ++i)
                {
                    var node1 = dataFunc.Joint_Generate(stdFlrID, i * 5000, 0);
                    var node2 = dataFunc.Joint_Generate(stdFlrID, i * 5000, 5000);
                    if (nodelist.Count() > 0)
                    {
                        //X向
                        node2grid_X.Add(new List<Mdl_Joint> { node1, nodelist[nodelist.Count() - 1][0] });
                        node2grid_X.Add(new List<Mdl_Joint> { node2, nodelist[nodelist.Count() - 1][1] });
                    }
                    //Y向
                    node2grid_Y.Add(new List<Mdl_Joint> { node1, node2 });
                    nodelist.Add(new List<Mdl_Joint> { node1, node2 });
                    //布置柱
                    dataFunc.column_arrange(node1, defcol);
                    dataFunc.column_arrange(node2, defcol);
                }

                //新生成网格、梁、杆件、墙、墙洞

                //X向
                for (int i = 0; i < node2grid_X.Count(); ++i)
                {
                    var axis = dataFunc.Axis_Generate(stdFlrID, node2grid_X[i][0].ID, node2grid_X[i][1].ID);
                    var grid = dataFunc.Grid_Generate(stdFlrID, node2grid_X[i][0].ID, node2grid_X[i][1].ID, axis.ID);
                    //布置墙及墙洞
                    dataFunc.wall_arrange(grid, wallSect);
                    dataFunc.wallhole_arrange(grid, wallHoleDef);
                    dataFunc.beam_arrange(grid, defbeam);
                }

                //Y向
                for (int i = 0; i < spans_cur - span_pre; ++i)
                {
                    dataFunc.brace_arrange(node2grid_Y[i][0], node2grid_Y[i][1], braceSect, 0, 0, 0, 0, 0, 1);
                    dataFunc.brace_arrange(node2grid_Y[i][0], node2grid_Y[i][1], braceSect, 0, 0, 1, 0, 0, 0);
                    var axis = dataFunc.Axis_Generate(stdFlrID, node2grid_Y[i][0].ID, node2grid_Y[i][1].ID);
                    var grid = dataFunc.Grid_Generate(stdFlrID, node2grid_Y[i][0].ID, node2grid_Y[i][1].ID, axis.ID);
                    //布置梁
                    dataFunc.beam_arrange(grid, defbeam);
                }
                dataFunc.DbModel_Assign();
                var updateInfo = dataFunc.GetUpdateInfo();
                transferData(updateInfo);
            }
        }

        //模型重新生成案例（非增量式）
        static void refresh_test01()
        {
            DataFunc dataFunc = new DataFunc();
            //标准层
            Mdl_StdFlr StdFlr = dataFunc.StdFlr_Generate(3900);
            BzcPara para = new BzcPara();
            var str = para.GetValString();
            //截面定义
            Mdl_ColSect defcol = dataFunc.ColSect_Def(6, 1, "400,400");
            Mdl_BeamSect defbeam1 = dataFunc.BeamSect_Def(6, 1, "250,600");
            Mdl_BeamSect defbeam2 = dataFunc.BeamSect_Def(6, 1, "200,400");
            //Mdl_BeamJY defbeamjy = dataFunc.BeamJYSect_Def(0,"1000,500,400","jy01");
            //Mdl_SlabJYDef defslabjy = dataFunc.SlbaJYSect_Def(1, "1500.00,500.00,0.00,0.00,");
            //荷载定义
            Mdl_LoadSect beamload1 = dataFunc.Load_Def(12, "1.00,9.60");
            Mdl_LoadSect beamload2 = dataFunc.Load_Def(12, "1.00,5.50");
            //生成节点
            var nodelist = new List<List<Mdl_Joint>>();
            var originpos = new List<int> { 0, 0 };
            var xspans = new List<int> { originpos[0], 3900, 3900, 3900, 3900, 3900, 3900 };
            var yspans = new List<int> { originpos[1], 6700, 5300 };
            nodelist = dataFunc.node_generate(xspans, yspans, StdFlr);
            //生成网格
            var gridlist = new List<Mdl_Grid>();
            gridlist = dataFunc.grid_generate(nodelist, 0, 1);
            //布置框架梁柱及荷载
            dataFunc.column_arrange(nodelist, defcol);
            var beam_list = new List<Mdl_BeamSeg>();
            beam_list = dataFunc.beam_arrange(gridlist, defbeam1);
            dataFunc.load_arrange(beam_list, beamload1);
            gridlist = dataFunc.grid_generate(nodelist, 1, 0);
            beam_list = dataFunc.beam_arrange(gridlist, defbeam2);
            dataFunc.load_arrange(beam_list, beamload2);
            //布置次梁
            xspans = new List<int> { originpos[0], 3900, 3900, 3900, 3900, 3900, 3900 };
            yspans = new List<int> { 5200 };
            nodelist = dataFunc.node_generate(xspans, yspans, StdFlr);
            gridlist = dataFunc.grid_generate(nodelist, 1, 0);
            beam_list = dataFunc.beam_arrange(gridlist, defbeam2);
            dataFunc.load_arrange(beam_list, beamload2);

            //标准层复制
            dataFunc.Floors_Assemb(0, StdFlr, 6, 3600);
            //提交建模数据
            dataFunc.DbModel_Assign();
            Hi_DbModelData model = dataFunc.GetDbModelData();
            transferData(model);
        }

        static Hi_DbModelData getDbModelData()
        {
            YJKSControl.RunCmd("test_readModel", "");
            Link2YJK link = Link2YJK.Instance;
            return link.GetIPCdata<Hi_DbModelData>();
        }

        static void reflec_Def()
        {
            var unionID = getUnionID();
            DataFunc dataFunc = new DataFunc();
            dataFunc.InitForLink(unionID);
            //截面定义
            Mdl_BeamSect defbeam1 = dataFunc.BeamSect_Def(6, 26, "", "H98X99X5X7");
            Mdl_ColSect defcol = dataFunc.ColSect_Def(6, 1, "401,401", "col_400*400");
            Mdl_BraceSect defbrace = dataFunc.BraceSect_Def(5, 1, "351,501", "brace_350*500");
            Mdl_WallSect defWall = dataFunc.WallSect_Def(6, 1, 201, "wall_201");
            Mdl_WallHoleDef defWallHole = dataFunc.WallHoleDef(1500, 2000);
            dataFunc.ColSect_Def(5, 303, "", "L40X2.0");//型钢截面
            dataFunc.DbModel_Assign();
            var updateInfo = dataFunc.GetUpdateInfo();
            transferData(updateInfo);
        }

        static void transferData(Hi_UpdateInfo updateInfo)
        {
            Link2YJK link = Link2YJK.Instance;
            link.LinkPrepare(updateInfo);
            YJKSControl.RunCmd("test_ipcreflect", "");
        }

        static void transferData(Hi_DbModelData model)
        {
            Link2YJK link = Link2YJK.Instance;
            link.LinkPrepare(model);
            YJKSControl.RunCmd("test_ipcrefresh", "");
        }

        static int getUnionID()
        {
            YJKSControl.RunCmd("test_updateUnionID", "");
            Link2YJK link = Link2YJK.Instance;
            return link.GetIPCUnionID();
        }


        static void Main(string[] args)
        {
            //reflec_test01();
            reflec_test02();
            //refresh_test01();
        }
    }
}
