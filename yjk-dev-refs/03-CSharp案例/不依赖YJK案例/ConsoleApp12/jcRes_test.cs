using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

using APIData;
using DataFuncApplication;
using JcResultData;
using System.IO;

/*本案例为对Jccad_Result_New.ydb(基础设计结果)进行读取的案例
注意事项如下：
    1.本案例目前只支持YJK5.2.1版本，并且需要将ConsoleApp12/YJK替换文件中的内容复制到YJK工程路径下
    2.进行基础计算后，即可读取生成的Jccad_Result_New.ydb文件，存储位置在“工程路径\基础计算及结果输出\Jccad_Result_New.ydb”
    3.用户可以根据需要获取内部对象列表，对象类型可查阅“基础计算结果数据库(Jccad_Result_New.ydb)说明”
*/
namespace ConsoleApp10
{
    class jcRes_test
    {
        static void Main(string[] args)
        {
            JcResultDataFunc jcResDataFunc = new JcResultDataFunc();
            //读取ydb
            jcResDataFunc.ReadJcYdb(@"D:\1.pyYJKS\yjk_test5.2\独基\基础计算及结果输出\", @"Jccad_Result_New.ydb");
            //获取板元节点列表
            var FeaPoint = jcResDataFunc.GetGeoFeaPointList();
            foreach(var Point in FeaPoint)
            {
                string str = String.Format("ID:{0},ptx:{1},pty:{2},ptz:{3}", Point.ID, Point.ptx, Point.pty, Point.ptz);
                console(str);
            }
        }
        public static void console(string info)
        {
            File.AppendAllText("D:\\Jccad_Result_New_Info.txt", "\r\n" + info);
        }

    }
}
