using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using MiddleTrans;
using System.IO;
using System.Windows.Forms;

//这是捕获代码异常的案例，可防止因为接口调用导致的程序崩溃，并提示错误信息。（适用于5.1及之后的版本）
namespace UserCode
{
    public class MyClass
    {
        [CommandMethod("yjk_post")]
        public void Func5()
        {
            string xing = new String('*', 50);
            string title = xing + "楼层刚度信息统计" + xing;
            console(title);//输出title内容到指定位置的txt文件
            for (int i = 0; i < 10; ++i)
            {
                //这里数组的大小为2是正常情况，为1是错误情况
                double[] dSD = new double[1];
                double[] dSC = new double[1];
                //捕获异常，以窗口形式弹出异常信息。
                try
                {
                    Hi_DesignData.dsnGetFlrStiff(i + 1, 1, dSD, dSC);
                    string str = String.Format("层号：{0}， 塔号：{1}， X、Y方向层间剪力与层间位移之比:{2}，{3}，" +
                    " X、Y方向层剪切刚度:{4}，{5}", i + 1, 1, dSD[0], dSD[1], dSC[0], dSC[1]);
                    console(str);//输出str内容到指定位置的txt文件
                }
                catch (Exception ex)
                {
                    MessageBox.Show(ex.ToString(),"Error!");
                }
            }
            console("");

            void console(string info)
            {
                File.AppendAllText("D:\\Cslog.txt", "\r\n" + info);
            }
        }
    }
}
