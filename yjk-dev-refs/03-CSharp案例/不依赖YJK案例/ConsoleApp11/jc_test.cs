using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

using CsToYjk;
using APIData;
using DataFuncApplication;
using JcModelData;
using System.IO;

/*本案例为一对基础YDB进行节点网格创建、构件类型定义、构件布置的案例
注意事项如下：
    1.需要先导入一个在进入基础模块后，点击重新读取按钮生成的Jccad_0.ydb，其生成于YJK项目路径
    2.在完成好基础构件定义、布置等操作之后需要先删除YJK项目路径下的Jccad_0.ydb文件，然后再生成Jccad_0.ydb文件
    3.之后在YJK的命令行中输入 jccad_read_by_ydb命令，不要点击导入ydb的按钮，此按钮会产生累加的效应，此问题将于最新版本修复
    4.循环读写YDB时需要注意当前读取的YDB是上一循环生成的YDB
    5.基础数据依赖上部建模的数据，所以需要在最开始时需要调用一次重新读取获取,之后不要轻易调用，如果上部结构发生变化需要调用时要先删除Jccad_0.ydb之后再点击重新读取
*/
namespace ConsoleApp11
{
    class jc_test
    {
        static void Main(string[] args)
        {
            //基础建模
            JcDataFunc jcdataFunc = new JcDataFunc();
            jcdataFunc.ReadJcYdb(@"E:\gitee\csharp-yjks\不依赖YJK案例\ConsoleApp11\", @"Jccad_0.ydb");

            //获取节点和网格
            var nodelist = jcdataFunc.GetJcNodeList();
            var iwaglist = jcdataFunc.GetJcIwagList();
            ////新增节点和轴线
            //var node1 = jcdataFunc.JcNode_Generate(-500, -500);
            //var node2 = jcdataFunc.JcNode_Generate(-1000, -500);
            //var node3 = jcdataFunc.JcNode_Generate(-1000, -1000);
            //var node4 = jcdataFunc.JcNode_Generate(-500, -1000);
            //jcdataFunc.JcGrid_Generate(node1, node2);
            //jcdataFunc.JcGrid_Generate(node2, node3);
            //jcdataFunc.JcGrid_Generate(node3, node4);
            //jcdataFunc.JcGrid_Generate(node4, node1);
            //定义独基
            jcdataFunc.JcDj_Def(0, "0,0,0,2,3300,3300,300,600,600,3000,0,0,0");
            //布置独基
            jcdataFunc.JcDJ_App(nodelist[0].ID, 1, 500, 500, 60, -1.5, 1);
            //定义地基梁
            var FbeamDef = jcdataFunc.JcFbeam_Def(401, 1001, 1501, 501, 301, 0);
            //布置地基梁
            jcdataFunc.JcFbeam_App(FbeamDef.lID, iwaglist[0], 500, -1.5, 1);
            //定义桩
            var PileDef = jcdataFunc.JcPile_Def(2, "800,200,300,500,25.0,1");
            //定义桩基承台(方形承台)
            var DaisDef = jcdataFunc.JcDais_Def(10, 2, 1, 4, 100, 100);
            jcdataFunc.JcDais_Cir(DaisDef.DaisFlag, 0, 1500, 1500);
            jcdataFunc.JcDais_Cir(DaisDef.DaisFlag, 0, -1500, 1500);
            jcdataFunc.JcDais_Cir(DaisDef.DaisFlag, 0, -1500, -1500);
            jcdataFunc.JcDais_Cir(DaisDef.DaisFlag, 0, 1500, -1500);
            jcdataFunc.JcDais_StepH(0, 0, 301);
            //定义桩基承台(圆形承台)
            var DaisDef1 = jcdataFunc.JcDais_Def(10, 0, 1, 4, 100, 100);
            jcdataFunc.JcDais_Cir(DaisDef1.DaisFlag, 3001);
            jcdataFunc.JcDais_StepH(DaisDef1.DaisFlag, 0, 301);
            //布置桩基承台
            jcdataFunc.JcDais_App(nodelist[0].ID, DaisDef.lID, 100, 100, 60, 10, -1.5, 1);
            jcdataFunc.JcDais_App(nodelist[10].ID, DaisDef1.lID, 100, 100, 60, 10, -1.5, 1);
            //布置桩
            jcdataFunc.JcPile_App(PileDef.lID, nodelist[0], -1, 0.0, 10);
            jcdataFunc.JcPile_App(PileDef.lID, 750, 750, 0, DaisDef.DaisFlag, 0.0, 10, -1.5, 1);
            jcdataFunc.JcPile_App(PileDef.lID, 750, -750, 0, DaisDef.DaisFlag, 0.0, 10, -1.5, 1);
            jcdataFunc.JcPile_App(PileDef.lID, -750, 750, 0, DaisDef.DaisFlag, 0.0, 10, -1.5, 1);
            jcdataFunc.JcPile_App(PileDef.lID, -750, -750, 0, DaisDef.DaisFlag, 0.0, 10, -1.5, 1);
            jcdataFunc.JcPile_App(PileDef.lID, 750, 750, 0, DaisDef1.DaisFlag, 0.0, 10, -1.5, 1);
            jcdataFunc.JcPile_App(PileDef.lID, 750, -750, 0, DaisDef1.DaisFlag, 0.0, 10, -1.5, 1);
            jcdataFunc.JcPile_App(PileDef.lID, -750, 750, 0, DaisDef1.DaisFlag, 0.0, 10, -1.5, 1);
            jcdataFunc.JcPile_App(PileDef.lID, -750, -750, 0, DaisDef1.DaisFlag, 0.0, 10, -1.5, 1);
            //拉梁定义
            var LLDef = jcdataFunc.JcLL_Def(400, 600);
            //拉梁布置
            jcdataFunc.JcLL_App(LLDef.lID, iwaglist[1], 100, 10, 10, -1.5, 1);
            //定义条基
            var TJDef = jcdataFunc.JcTJ_Def(0, "2000,200,133,100,250,100,100,60,60");
            //条基布置
            jcdataFunc.JcTJ_App(TJDef.lID, iwaglist[3], 100, -1.5, 1);
            //定义筏板
            var SlabDef = jcdataFunc.JcRaftSlab_Def(-1, "200,10,2,3,0,-0.5,1,10,10,10");
            //筏板布置
            jcdataFunc.JcRaftSlab_App(SlabDef.lID, 16200, 12600);
            jcdataFunc.JcRaftSlab_App(SlabDef.lID, 11100, 12600);
            jcdataFunc.JcRaftSlab_App(SlabDef.lID, 11100, -600);
            jcdataFunc.JcRaftSlab_App(SlabDef.lID, 16200, -600);
            //定义柱墩
            var ZDDef = jcdataFunc.JcZD_Def(1, 5000, 4000, 1000, 45);
            //布置柱墩
            var ColumnList = jcdataFunc.GetJcAppColumnList();
            ColumnList[12].lZDKind = ZDDef.kind;

            DeleteFile(@"C:\Users\10497\Desktop\例子\dev\2.基础\test04\");
            jcdataFunc.CreateYDB(@"C:\Users\10497\Desktop\例子\dev\2.基础\test04\", @"Jccad_0.ydb");

        }

        static public void DeleteFile(string path)
        {
            string[] filenameList1 = Directory.GetFiles(path, "Jccad_0*");
            string[] filenameList2 = Directory.GetFiles(path, "*_F.*");
            foreach(var f in filenameList1)
            {
                File.Delete(f);
            }
            foreach (var f in filenameList2)
            {
                File.Delete(f);
            }
        }
    }
}
