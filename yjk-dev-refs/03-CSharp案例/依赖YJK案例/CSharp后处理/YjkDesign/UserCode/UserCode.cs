using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.IO;

using MiddleTrans;

namespace UserCode
{
    public class MyClass
    {
        public void run()
        {
            string xing = new String('*', 50);
            string title = xing + "楼层受剪承载力信息统计" + xing;
            console(title);
            for (int i = 0; i < 10; ++i)
            {
                double[] dSD = new double[2];
                double[] dSC = new double[2];
                Hi_DesignData.dsnGetFlrStiff(i + 1, 1, dSD, dSC);
                string str = String.Format("层号：{0}， 塔号：{1}， X、Y方向层间剪力与层间位移之比:{2}，{3}， X、Y方向层剪切刚度:{4}，{5}", i + 1, 1, dSD[0], dSD[1], dSC[0], dSC[1]);
                console(str);
            }
            console("");

            title = xing + "楼层受剪承载力信息统计" + xing;
            console(title);
            for (int i = 0; i < 10; ++i)
            {
                double[] dSC = new double[2];
                Hi_DesignData.dsnGetFlrShearCapacity(i + 1, 1, dSC);
                string str = String.Format("层号：{0}， 塔号：{1}， X、X、Y方向受剪承载力:{2}，{3}", i + 1, 1, dSC[0], dSC[1]);
                console(str);
            }
            console("");

            title = xing + "调整前柱标准内力" + xing;
            console(title);
            for (int i = 0; i < 10; ++i)
            {
                for (int j = 0; j < 20; ++j)
                {
                    int nSect = 0;
                    float[,] Force = { { 0, 0, 0, 0, 0, 0 }, { 0, 0, 0, 0, 0, 0 } };
                    Hi_DesignData.dsnGetColumnStdForce(i + 1, (i + 1) * 1000000 + 46 + j, 1, 1, ref nSect, Force);
                    string str = String.Format("层号：{0}， 柱全楼编号：{1}，截面数量：{2}，工况号：{3}， 内力: X弯矩:{4}， Y弯矩:{5}， X剪力:{6}， Y剪力:{7}， 轴力:{8}， 扭矩:{9}", i + 1, (i + 1) * 1000000 + 46 + j, nSect,1, Force[1,0], Force[1, 1], Force[1, 2], Force[1, 3],Force[1, 4], Force[1, 5]);
                    console(str);
                }
            }
        }

        public void console(string info)
        {
            File.AppendAllText("D:\\Cslog.txt", "\r\n" + info);
        }

    }

}
