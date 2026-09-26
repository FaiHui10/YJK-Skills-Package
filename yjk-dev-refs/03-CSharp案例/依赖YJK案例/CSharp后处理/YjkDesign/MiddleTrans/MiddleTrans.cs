using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Runtime.InteropServices;

namespace MiddleTrans
{
    public class Hi_DesignData
    {
        //----------------------------------------------------------------------
        //获得排序后设计模块的工况信息
        //Option =1       全部计算工况
        //Option =2       构件内力输出用工况，吊车除外，规定水平力除外
        //Option =3       梁吊车荷载工况
        //Option =4       柱吊车荷载工况
        //Option =5       构件内力输出用工况，包含规定水平力，吊车除外
        //Option =6       写基础用工况，基础与上部一起算时的基础工况除外
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetLDCaseBySort")]
        public static extern void dsnGetLDCaseBySort(int Option, ref int nLDCaseNum, int[] LDCase, int[] LDCaseOld, int[] LDKind);
        //----------------------------------------------------------------------
        //获得排序后设计模块的工况信息
        //bBase           是否含有基本工况
        //bBSXDZ          是否含有双向地震工况
        //bApp            是否含有规定水平力工况
        //bBeamCrane      是否含有梁吊车工况
        //bColCrane       是否含有柱吊车工况
        //bPM             是否含有建模自定义工况
        //bJC             是否含有与上部一起算时的基础工况
        //bLDComb         是否含有非线性组合工况
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetLDCaseBySortNew")]
        public static extern void dsnGetLDCaseBySortNew(ref int nLDCaseNum, int[] LDCase, int[] LDCaseOld, int[] LDKind, bool bBase, bool bBSXDZ, bool bApp, bool bBeamCrane, bool bColCrane, bool bPM, bool bJC, bool bLDComb);
        //----------------------------------------------------------------------
        //获得排序后设计模块的工况信息-施工
        //bBase           是否含有基本工况
        //bBSXDZ          是否含有双向地震工况
        //bApp            是否含有规定水平力工况
        //bBeamCrane      是否含有梁吊车工况
        //bColCrane       是否含有柱吊车工况
        //bPM             是否含有建模自定义工况
        //bJC             是否含有与上部一起算时的基础工况
        //bLDComb         是否含有非线性组合工况
        //注意：施工阶段计算时，模型、工况与基本模型是无关的，因此需要单独获取，下面各工况相关接口仅针对基本模型有效
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetLDCaseBySortNew_SG")]
        public static extern void dsnGetLDCaseBySortNew_SG(ref int nLDCaseNum, int[] LDCase, int[] LDCaseOld, int[] LDKind, bool bBase, bool bBSXDZ, bool bApp, bool bBeamCrane, bool bColCrane, bool bPM, bool bJC, bool bLDComb);
        //----------------------------------------------------------------------
        //获得荷载组合用排序后设计模块的工况信息
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetLDCaseBySort_LDComb")]
        public static extern void dsnGetLDCaseBySort_LDComb(ref int nLDCaseNum, int[] LDCase);
        //----------------------------------------------------------------------
        //获得某工况分项系数、组合值系数
        //nLDCase         工况号
        //fLDCaseInf      系数，分别为：分项系数(非地震不利)，分项系数(非地震有利)，分项系数(地震不利)，分项系数(地震有利)
        //                            分项系数(人防不利)，分项系数(人防有利)，组合值系数(非地震)，组合值系数(地震)，组合值系数(人防)
        //                            频遇值系数，准永久值系数
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetLDCaseCoeInf")]
        public static extern bool dsnGetLDCaseCoeInf(int nLDCase, float[] fLDCaseInf);
        //----------------------------------------------------------------------
        //获得某工况类型包含的工况号
        //nLDKind         工况类型，参见宏定义
        //nLDCaseNum      工况数量
        //LDCase          工况号数组
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetLDCaseByLDKind")]
        public static extern bool dsnGetLDCaseByLDKind(int nLDKind, ref int nLDCaseNum, int[] LDCase);
        //----------------------------------------------------------------------
        //根据工况编号获得工况类型
        //nLDCase         工况号
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetLDKind")]
        public static extern int dsnGetLDKind(int nLDCase);
        //----------------------------------------------------------------------
        //根据工况编号获得老工况号
        //nLDCase         工况号
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetLDCaseOldByLDCase")]
        public static extern int dsnGetLDCaseOldByLDCase(int nLDCase);
        //----------------------------------------------------------------------
        //根据老工况号获得工况号
        //nLDCaseOld      老工况号
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetLDCaseByLDCaseOld")]
        public static extern int dsnGetLDCaseByLDCaseOld(int nLDCaseOld);
        //----------------------------------------------------------------------
        //根据工况编号获得空心板用工况号
        //nLDCase         工况号
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetYXYKXBLDCaseByLDCase")]
        public static extern int dsnGetYXYKXBLDCaseByLDCase(int nLDCase);
        //----------------------------------------------------------------------
        //根据工况编号获得计算用工况号
        //nLDCase         工况号
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetAnaLDCaseByLDCase")]
        public static extern int dsnGetAnaLDCaseByLDCase(int nLDCase);
        //----------------------------------------------------------------------
        //根据工况编号获得计算用工况号
        //nAnaLDCase      计算工况号
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetLDCaseByAnaLDCase")]
        public static extern int dsnGetLDCaseByAnaLDCase(int nAnaLDCase);
        //----------------------------------------------------------------------
        //获得工况属性，如水平荷载、竖向荷载等（参见宏定义）
        //nLDCase         工况号
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetLDType")]
        public static extern int dsnGetLDType(int nLDCase);
        //----------------------------------------------------------------------
        //确定该工况是否为恒载工况
        //nLDCase         工况号
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnLDCaseIsDead")]
        public static extern bool dsnLDCaseIsDead(int nLDCase);
        //----------------------------------------------------------------------
        //确定该工况是否为活载工况
        //nLDCase         工况号
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnLDCaseIsLive")]
        public static extern bool dsnLDCaseIsLive(int nLDCase);
        //----------------------------------------------------------------------
        //确定该工况是否为人防工况
        //nLDCase         工况号
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnLDCaseIsAir")]
        public static extern bool dsnLDCaseIsAir(int nLDCase);
        //----------------------------------------------------------------------
        //确定该工况是否为地震工况，规定水平力返回TRUE
        //nLDCase         工况号
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnLDCaseIsSeis")]
        public static extern bool dsnLDCaseIsSeis(int nLDCase);
        //----------------------------------------------------------------------
        //确定该工况是否为竖向地震工况
        //nLDCase         工况号
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnLDCaseIsVerSeis")]
        public static extern bool dsnLDCaseIsVerSeis(int nLDCase);
        //----------------------------------------------------------------------
        //确定该工况是否为规定水平力工况
        //nLDCase         工况号
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnLDCaseIsSeisApp")]
        public static extern bool dsnLDCaseIsSeisApp(int nLDCase);
        //----------------------------------------------------------------------
        //确定该工况是否为风荷载工况
        //nLDCase         工况号
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnLDCaseIsWind")]
        public static extern bool dsnLDCaseIsWind(int nLDCase);
        //----------------------------------------------------------------------
        //确定该工况是否为横向风
        //nLDCase         工况号
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnLDCaseIsWindH")]
        public static extern bool dsnLDCaseIsWindH(int nLDCase);
        //----------------------------------------------------------------------
        //确定该工况是否为扭转风
        //nLDCase         工况号
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnLDCaseIsWindT")]
        public static extern bool dsnLDCaseIsWindT(int nLDCase);
        //----------------------------------------------------------------------
        //确定该工况是否为梁吊车
        //nLDCase         工况号
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnLDCaseIsBeamCrane")]
        public static extern bool dsnLDCaseIsBeamCrane(int nLDCase);
        //----------------------------------------------------------------------
        //确定该工况是否为柱吊车
        //nLDCase         工况号
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnLDCaseIsColCrane")]
        public static extern bool dsnLDCaseIsColCrane(int nLDCase);
        //----------------------------------------------------------------------
        //确定该工况是否为建模自定义工况
        //nLDCase         工况号
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnLDCaseIsPMUser")]
        public static extern bool dsnLDCaseIsPMUser(int nLDCase);
        //----------------------------------------------------------------------
        //确定该工况是否为基础工况
        //nLDCase         工况号
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnLDCaseIsJC")]
        public static extern bool dsnLDCaseIsJC(int nLDCase);
        //----------------------------------------------------------------------
        //确定该工况是否为基础高水工况
        //nLDCase         工况号
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnLDCaseIsJCWaterH")]
        public static extern bool dsnLDCaseIsJCWaterH(int nLDCase);
        //----------------------------------------------------------------------
        //确定该工况是否为预应力工况
        //nLDCase         工况号
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnLDCaseIsPRES")]
        public static extern bool dsnLDCaseIsPRES(int nLDCase);
        //----------------------------------------------------------------------
        //确定该工况是否为反应位移工况
        //nLDCase         工况号
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnLDCaseIsFYWY")]
        public static extern bool dsnLDCaseIsFYWY(int nLDCase);
        //----------------------------------------------------------------------
        //确定该工况是否为空心板工况
        //nLDCase         工况号
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnLDCaseIsKXB")]
        public static extern bool dsnLDCaseIsKXB(int nLDCase);
        //----------------------------------------------------------------------
        //确定该工况是否为非线性组合工况
        //nLDCase         工况号
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnLDCaseIsLDComb")]
        public static extern bool dsnLDCaseIsLDComb(int nLDCase);
        //----------------------------------------------------------------------
        //获得自动生成的荷载组合信息
        //nLDCombNum      组合数量
        //fLDComb         各组合分项系数，第二维为工况
        //fLDComb[][0]    V-D
        //fLDComb[][1]    V-L
        //fLDComb[][2]    +X-W
        //fLDComb[][3]    -X-W
        //fLDComb[][4]    +Y-W
        //fLDComb[][5]    -Y-W
        //fLDComb[][6]    X-E
        //fLDComb[][7]    Y-E
        //fLDComb[][8]    Z-E
        //fLDComb[][9]    R-F
        //fLDComb[][10]   TEM
        //fLDComb[][11]   CRN
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetLDCombInf")]
        public static extern void dsnGetLDCombInf(ref int nLDCombNum, float[,] fLDComb);
        //----------------------------------------------------------------------
        //获得工程使用的的荷载组合信息
        //nLDCombNum      组合数量
        //fLDComb         各组合分项系数，第二维为工况
        //fLDComb[][0]    V-D
        //fLDComb[][1]    V-L
        //fLDComb[][2]    +X-W
        //fLDComb[][3]    -X-W
        //fLDComb[][4]    +Y-W
        //fLDComb[][5]    -Y-W
        //fLDComb[][6]    X-E
        //fLDComb[][7]    Y-E
        //fLDComb[][8]    Z-E
        //fLDComb[][9]    R-F
        //fLDComb[][10]   TEM
        //fLDComb[][11]   CRN
        //nLDCombKind     组合属性，地震、非地震、人防等
        //nNonLineSign    非线性标记，0-线性，1-非线性
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetLDCombInf_Use")]
        public static extern bool dsnGetLDCombInf_Use(ref int nLDCombNum, float[,] fLDComb, int[] nLDCombKind, int[] nNonLineSign);
        //----------------------------------------------------------------------
        //获取总体信息
        //globalInfo[0] 静力工况数目
        //globalInfo[1] 振型数
        //globalInfo[2] 地震工况数
        //globalInfo[3] 反应谱所用振型数
        //globalInfo[4] 节点数
        //globalInfo[5] 框架单元数
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetGlobalInformationByReader")]
        public static extern void dsnGetGlobalInformationByReader(int nModule, int[] globalInfo);
        //----------------------------------------------------------------------
        //获得振型信息
        //Option            选项，1-水平地震，2-竖向地震
        //@param eignNum    振型数量
        //@param maxAngle   最大地震方向
        //@param pieriod[]  各振型周期
        //@param angle[]    各振型转角
        //@param coeff[][6] 各振型质量X/Y/Z平动，RX/RY/RZ扭转系数
        //@param m[][6]     各振型参与质量 ux,uy,uz,rx,ry,rz
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetEignInfo")]
        public static extern void dsnGetEignInfo(int Option, ref int eignNum, ref double maxAngle, double[] pieriod, double[] angle, double[,] coeff, double[,] m);
        //----------------------------------------------------------------------
        //nModule           模型，基本、折减、强刚等，采用dsndatadefine.h中的宏定义
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetEignInfoByReader")]
        public static extern void dsnGetEignInfoByReader(int nModule, ref int eignNum, ref double maxAngle, double[] pieriod, double[] angle, double[] coeff, double[] m);
        //----------------------------------------------------------------------
        //获取局部振动信息
        //int eigenList[]， 局部振动的振型号列表
        //返回值：          局部振动的振型个数
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetLocalVibrationInfo")]
        public static extern int dsnGetLocalVibrationInfo(int[] eigenList);
        //----------------------------------------------------------------------
        //获取局部振动振型的楼层信息
        //int eigenNo，     输入的局部振动的振型号
        //story[],tower[]   本振型发生局部振动的层号塔号列表，层塔一一对应
        //返回值：          本振型局部振动的楼层数
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetLocalVibrationStories")]
        public static extern int dsnGetLocalVibrationStories(int eigenNo,int[] story,int[] tower);
        //----------------------------------------------------------------------
        //获取各振型的阻尼比
        //nModule           模型，基本、折减、强刚等，采用dsndatadefine.h中的宏定义
        //@param ksi[]      预先开好的阻尼比数组，长度为振型数
        //返回振型数
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetDampRatioOfAllModes")]
        public static extern int dsnGetDampRatioOfAllModes(int nModule, double[] ksi);
        //----------------------------------------------------------------------
        //获取反应谱工况下某层的某振型的地震外力
        //nModule           模型，基本、折减、强刚等，采用dsndatadefine.h中的宏定义
        //@param spectrumDir 工况编号
        //@param eigenNum    振型号
        //@param floor,tower 层号，塔号
        //@param f[3]       返回对应工况下的层外力FX,FY,FZ,RX,RY,RZ     
        //@return           true: 成功 false:失败
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetSpectrumLayerForceEigen")]
        public static extern bool dsnGetSpectrumLayerForceEigen(int nModule, int nLDCase, int eigenNum, int floor, int tower, double[] f);
        //----------------------------------------------------------------------
        //获取工况下某层的地震外力
        //@param loadCaseId  工况编号
        //@param eigenNum    振型号
        //@param floor,tower 层号，塔号
        //@param f[3]       返回对应工况下的层外力FX,FY,FZ,RX,RY,RZ    
        //@return           true: 成功 false:失败
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetSpectrumLayerForceCQC")]
        public static extern bool dsnGetSpectrumLayerForceCQC(int nModule, int nLDCase, int floor, int tower, double[] f);
        //----------------------------------------------------------------------
        //获取各地震底部剪力法的各层地震作用标准值
        //@loadcaseId   地震工况号
        //@param floor,tower 层号，塔号，如果 (0层-1塔)，则返回顶层附加地震作用数值
        //@f				返回对应层塔的底部剪力值，如果参数非法，返回0.0
        //@return           成功TRUE，失败FALSE
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetBottomShearingForceOfLoadCase")]
        public static extern bool dsnGetBottomShearingForceOfLoadCase(int nModule,int nLDCase,int nFloor,int nTower,ref double f);
        //----------------------------------------------------------------------
        //获取各地震底部剪力法的各层地震作用标准值
        //@loadcaseId   地震工况号
        //@param floor,tower 层号，塔号，如果 (0层-1塔)，则返回顶层附加地震作用数值
        //@f				返回对应层塔的底部剪力值，如果参数非法，返回0.0
        //@return           成功TRUE，失败FALSE
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetMaxSeismicEffectAngle")]
        public static extern bool dsnGetMaxSeismicEffectAngle(int nModule, ref double dmaxAngle);
        //----------------------------------------------------------------------
        //获取屈曲特征值及Pcr
        //@param eigenValues[] 屈曲特征值
        //@param pcrValues[]   Pcr因子
        //                     两者空间需事先开好，可以传入NULL则不输出
        //@return 返回特征值数目
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetBuckingEigenAndPcrValue")]
        public static extern int dsnGetBuckingEigenAndPcrValue(double[] eigenValues, double[] pcrValues);
        //----------------------------------------------------------------------
        //获取节点的屈曲特征向量
        //@param nodeTag     节点号
        //@param buckingMod    屈曲模态号
        //@param disp[6]    返回对应，模态下节点特征向量，分别为DX,DY,DZ,RX,RY,RZ
        //@return           true: 成功 false:失败
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetNodeBuckingDisp")]
        public static extern bool dsnGetNodeBuckingDisp(int nodeTag, int buckingMod, double[] disp);
        //----------------------------------------------------------------------
        //获取超单元的内部单元数据
        //partCategory: 单元类别，目前只支持（500:超单元）
        //type[] : 单元类型，必须预先开好足够的空间，如果为NULL，则不处理
        //ndCnt[]: 单元节点数
        //nodeIdx[][4]: 单元节点序号
        //guassCnt[]:单元的高斯点数量
        //guassPtIdx[][4]: 高斯点的序号
        //centerPtIdx[]:  中心点序号
        //thickness[]:  单元厚度
        //返回单元数量，如果返回<=0，则表示没有对应单元或者单元类型不支持
        //注意：如果type，ndCnt，nodeIdx任意一个为NULL，则只返回单元数量，不读取具体数据
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetPartElementsEx")]
        public static extern int dsnGetPartElementsEx(int partCategory, int partTag, int[] type,int[] ndCnt,int[] nodeIdx,
								  int[] guassCnt,int[] guassPtIdx,int[] centerPtIdx,double[] thickness);
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetPartElementsExNew")]
        public static extern int dsnGetPartElementsExNew(int nComKind,int partCategory, int partTag, int[] type,int[] ndCnt,int[,] nodeIdx,
									int[] guassCnt,int[] guassPtIdx,int[] centerPtIdx,double[] thickness);
        //----------------------------------------------------------------------
        //获取单元的节点列表坐标(转换到整体坐标系)
        //elemCategory: 单元类别，目前只支持（500:超单元）
        //coord[][3]: 节点坐标 x,y,z，必须预先开好足够的空间，如果为NULL，则不处理
        //flag[]    :  节点标记  <0:外部节点 2:内部节点 3:高斯点，4:中心点 如果为NULL，则不输出这一项
        //返回节点数量，如果返回<=0，则表示没有对应单元或者单元类型不支持
        //注意：如果coord==NULL，则只返回节点数量
        //对于外部节点的flag值小于0，绝对值为外部节点的(Tag)
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetPartNodeCoord")]
        public static extern int dsnGetPartNodeCoord(int elemCategory, int elemTag, double[,] coord,int[] flag);
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetPartNodeCoordNew")]
        public static extern int dsnGetPartNodeCoordNew(int nComKind,int elemCategory, int elemTag, double[] coord,int[] flag);
        //----------------------------------------------------------------------
        //获取单元的各节点应力
        //elemCategory: 单元类别，目前只支持（500:超单元）
        //stress[][12]: 各节点各应力分量，必须预先开好足够的空间。
        //              应力方向为单元局部坐标系，各分量分别为Fxx,Fyy,Fxy,Mxx,Myy,Mxy,Vxx,Vyy,Fmax,Fmin,Mmax,Mmin
        //Fxx：作用在与局部坐标系x轴垂直平面内，单元局部坐标系x轴方向上单位宽度轴力。
        //Fyy：作用在与局部坐标系y轴垂直平面内，单元局部坐标系y轴方向上单位宽度轴力。
        //Fxy：单元局部坐标系的x-y平面内(平面内受剪)单位宽度剪力(Fxy=Fyx)。
        //Fmax：单位宽度最大主轴力。
        //Fmin：单位宽度最小主轴力。
        //Mxx：作用在与局部坐标系x轴垂直平面内，绕y轴旋转的单位宽度弯矩(绕局部坐标系y轴的平面外弯矩)。
        //Myy：作用在与局部坐标系y轴垂直平面内，绕x轴旋转的单位宽度弯矩(绕局部坐标系x轴的平面外弯矩)。
        //Mxy：作用在与局部坐标系x轴垂直平面内，绕x轴旋转的单位宽度扭矩(Mxy=Myx)。
        //Mmax：单位宽度的最大主弯矩。
        //Mmin：单位宽度的最大小弯矩。
        //Vxx：作用在与局部坐标系x轴垂直平面内，沿单元局部坐标系z轴(厚度)方向上单位宽度的剪力。
        //Vyy：作用在与局部坐标系y轴垂直平面内，沿单元局部坐标系z轴(厚度)方向上单位宽度的剪力。
        //返回节点数量，如果返回<=0，则表示没有对应单元或者单元类型不支持
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetPartNodeStress")]
        public static extern int dsnGetPartNodeStress(int elemCategory,int elemTag,int nLDCase,double[] stress);
        //Option:       1-调整前，2-调整后
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetPartNodeStressNew")]
        public static extern int dsnGetPartNodeStressNew(int nFloor, int nComKind, int nTotID,int elemCategory,int elemTag,int nLDCase,int Option,double[,] stress);
        //----------------------------------------------------------------------
        //获取单元（应力积分后）内力
        //@param eleCategory : 单元类型
        //@param eleTag      : 单元编号
        //@param loadCaseId  : 工况编号
        //@param type        ：点类型，FEA_STRESS_NODE,FEA_STRESS_GAUSS,FEA_STRESS_CENT，可以二进制“或”进行组合
        //force[][12]: 单元内各点各应力分量，必须预先开好足够的空间，如果为NULL，则返回点数量（受type控制）。
        //              应力方向为单元局部坐标系，各分量分别为Fxx,Fyy,Fxy,Mxx,Myy,Mxy,Vxx,Vyy,Fmax,Fmin,Mmax,Mmin
        //Fxx：作用在与局部坐标系x轴垂直平面内，单元局部坐标系x轴方向上单位宽度轴力。
        //Fyy：作用在与局部坐标系y轴垂直平面内，单元局部坐标系y轴方向上单位宽度轴力。
        //Fxy：单元局部坐标系的x-y平面内(平面内受剪)单位宽度剪力(Fxy=Fyx)。
        //Fmax：单位宽度最大主轴力。
        //Fmin：单位宽度最小主轴力。
        //Mxx：作用在与局部坐标系x轴垂直平面内，绕y轴旋转的单位宽度弯矩(绕局部坐标系y轴的平面外弯矩)。
        //Myy：作用在与局部坐标系y轴垂直平面内，绕x轴旋转的单位宽度弯矩(绕局部坐标系x轴的平面外弯矩)。
        //Mxy：作用在与局部坐标系x轴垂直平面内，绕x轴旋转的单位宽度扭矩(Mxy=Myx)。
        //Mmax：单位宽度的最大主弯矩。
        //Mmin：单位宽度的最大小弯矩。
        //Vxx：作用在与局部坐标系x轴垂直平面内，沿单元局部坐标系z轴(厚度)方向上单位宽度的剪力。
        //Vyy：作用在与局部坐标系y轴垂直平面内，沿单元局部坐标系z轴(厚度)方向上单位宽度的剪力。
        //对实体单元，每个点前6个分量有效，为FXX   FYY   FZZ   FXY   FYZ   FZX
        //Option:       1-调整前，2-调整后
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetElementStressNew")]
        public static extern int dsnGetElementStressNew(int nFloor, int nComKind, int nTotID, int eleCategory, int eleTag, int nLDCase, int Option, int type, double[] stress);
        //----------------------------------------------------------------------
        //获取单元的各节点应力，已将计算返回的Kp转换成Mp
        //获取单元的各节点应力，不同于#61接口，#74接口为不积分的应力
        //partCategory: 单元类别，目前只支持（500:超单元）
        //partTag     : 超单元tag
        //nLDCase       : 工况编号
        //postion     : 	PLATE_STRESS_TOP	=0,  //板顶应力
        //                  PLATE_STRESS_BOT	=1,  //板底应力
        //              	PLATE_STRESS_TOPBOT	=2   //板顶、板底应力
        //stress[][10]: 各节点各应力分量，必须预先开好足够的空间，如果为NULL，则返回节点数量。
        //              应力方向为单元局部坐标系
        //				各分量分别为Sig-xx,Sig-yy,Sig-zz,Sig-xy,Sig-yz,Sig-xz,Sig-max,Sig-min,Sig-eff,Max-Shear
        //Sig-xx：坐标系X轴方向的轴向应力。
        //Sig-yy：坐标系Y轴方向的轴向应力。
        //Sig-zz：坐标系Z轴方向的轴向应力。
        //Sig-xy：坐标系X-Y平面内的剪应力。
        //Sig-yz：坐标系Y-Z平面内的剪应力。
        //Sig-xz：坐标系X-Z平面内的剪应力。
        //Sig-max：最大主应力。
        //Sig-min：最小主应力。
        //Sig-eff：有效应力(von-Mises 应力)。
        //Max-Shear：。
        //返回节点数量，如果返回<=0，则表示没有对应单元或者单元类型不支持
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetPartNodeStressSigma")]
        public static extern int dsnGetPartNodeStressSigma(int partCategory,int partTag,int nLDCase,int position,double[,] stress);
        //Option:       1-调整前，2-调整后
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetPartNodeStressSigmaNew")]
        public static extern int dsnGetPartNodeStressSigmaNew(int nFloor, int nComKind, int nTotID,int partCategory,int partTag,int nLDCase,int position,int Option,double[,] stress);
        //----------------------------------------------------------------------
        //获得非超单元信息，返回单元数量
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetPlanarEleNum")]
        public static extern int dsnGetPlanarEleNum(int nFloor, int nComKind, int nTotID);
        //获得非超单元信息，返回节点数量，包含单元中心值
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetPlanarNodeNum")]
        public static extern int dsnGetPlanarNodeNum(int nFloor, int nComKind, int nTotID);
        //获得非超单元局部坐标系
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetPlanarAxis")]
        public static extern bool dsnGetPlanarAxis(int nFloor, int nComKind, int nTotID, double[] lx, double[] ly, double[] lz, double[] origin);
        //获得非超单元的单元信息，返回单元数量
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetPlanarEx")]
        public static extern int dsnGetPlanarEx(int nFloor, int nComKind, int nTotID, int[] ndCnt, int[,] nodeIdx, int[] centerPtIdx, double[] thickness);
        //获得非超单元节点坐标
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetPlanarNodeCoord")]
        public static extern bool dsnGetPlanarNodeCoord(int nFloor, int nComKind, int nTotID, double[,] coord, int[] flag);
        //获得非超单元节点位移
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetPlanarNodeDisp")]
        public static extern int dsnGetPlanarNodeDisp(int nFloor, int nComKind, int nTotID,int nLDCase,double[] disp);
        //获得非超单元内力信息，返回节点数量
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetPlanarNodeStress")]
        public static extern int dsnGetPlanarNodeStress(int nFloor, int nComKind, int nTotID,int nLDCase,int Option,double[,] stress);
        //获得非超单元应力信息，返回节点数量
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetPlanarNodeStressSigma")]
        public static extern int dsnGetPlanarNodeStressSigma(int nFloor, int nComKind, int nTotID,int nLDCase,int position,int Option,double[,] stress);
        //----------------------------------------------------------------------
        //获取单元的节点位移(转换到整体坐标系)
        //@param partCategory: 单元类别，目前只支持（:超单元）
        //@param partTag     单元号
        //@param nLDCase     工况编号
        //@param disp[][6]:    各节点位移DX,DY,DZ,RX,RY,RZ，必须预先开好足够的空间，如果为NULL，则不处理
        //返回节点数量，如果返回<=0，则表示没有对应单元或者单元类型不支持
        //注意：如果disp==NULL，则只返回节点数量
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetPartNodeDisp")]
        public static extern int dsnGetPartNodeDisp(int partCategory, int partTag, int nLDCase, double[,] disp);

        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetPartNodeDispNew")]
        public static extern int dsnGetPartNodeDispNew(int nComKind,int partCategory, int partTag, int nLDCase, double[,] disp);
        //----------------------------------------------------------------------
        //根据任工获得弹性板配筋数据增加的接口
        //nFloor          楼层号
        //nPMRoomID       建模房间编号
        //nRoomEleNum     返回单元数量
        //EleNodeNum      单元节点数
        //EleNodeID       单元节点序号
        //EleNodeOut      单元节点是否是出口节点标记，0-内部节点，非0-出口节点且为节点ID
        //dEleNodeCoor    单元节点在整体坐标系下的坐标
        //dEleThick       单元厚度（mm）
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetTXBFordtlslab")]
        public static extern bool dsnGetTXBFordtlslab(int nFloor, int nPMRoomID, ref int nRoomEleNum, int[] EleNodeNum, int[,] EleNodeID, int[,] EleNodeOut, double[,] dEleNodeCoor, double[] dEleThick);
        //----------------------------------------------------------------------
        //根据任工获得空心板配筋数据增加的接口
        //nFloor          楼层号
        //nPMRoomID       建模房间编号
        //nRoomEleNum     返回单元数量
        //EleNodeNum      单元节点数
        //EleNodeID       单元节点序号
        //EleNodeOut      单元节点是否是出口节点标记，0-内部节点，非0-出口节点且为节点ID
        //dEleNodeCoor    单元节点在整体坐标系下的坐标
        //dEleThick       单元厚度（mm）
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetKXBFordtlslab")]
        public static extern bool dsnGetKXBFordtlslab(int nFloor, int nPMRoomID, ref int nRoomEleNum, int[] EleNodeNum, int[,] EleNodeID, int[,] EleNodeOut, double[,] dEleNodeCoor, double[] dEleThick);
        //----------------------------------------------------------------------
        //获得空心板节点某工况内力
        //nFloor          楼层号
        //nRoomID         建模房间编号
        //nLDCase         工况号
        //jdID            节点编号
        //Option:         1-调整前，2-调整后
        //dValue          内力，分别为Mxx、Myy、Mxy、Qxx(Vzx)、Qyy(Vyz)
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetHollowSlabNodeStr")]
        public static extern int dsnGetHollowSlabNodeStr(int nFloor, int nRoomID, int nLDCase, int Option, int jdID, double[] dValue);
        //----------------------------------------------------------------------
        //获得节点单工况位移
        //NodeID          节点编号
        //nLDCase         工况号
        //disp            节点位移
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetNodeDis")]
        public static extern void dsnGetNodeDis(int NodeID, int nLDCase, double[] disp);
        //----------------------------------------------------------------------
        //获得节点预组合位移
        //NodeID          节点编号
        //nLDCombType(in) 组合类别，如基本组合、标准组合等，采用宏定义
        //disp            节点位移
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetNodePrcCombDis")]
        public static extern void dsnGetNodePrcCombDis(int NodeID, int nLDCombType, int nPrcCombType, int nPrcComb, double[] disp);
        //----------------------------------------------------------------------
        //获得单振型节点位移
        //nModule         计算模型标记，如基本、强刚、连梁不折减等，采用宏定义
        //Option          选项，1-水平地震，2-竖向地震
        //NodeID          节点编号
        //EigenNum        振型号
        //disp            节点位移
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetNodeEigenDisp")]
        public static extern void dsnGetNodeEigenDisp(int nModule, int Option, int NodeID, int EigenNum, double[] disp);
        //----------------------------------------------------------------------
        //获得单工况水平位移统计结果
        //nFloor          层号
        //nTower          塔号
        //nLDCase         工况号
        //DisRatio        X、Y方向层位移比
        //DisDRatio       X、Y方向层间位移比
        //DisDAng         X、Y方向层间位移角
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetLDCaseHorDisStat")]
        public static extern bool dsnGetLDCaseHorDisStat(int nFloor, int nTower, int nLDCase, double[] DisRatio, double[] DisDRatio, double[] DisDAng);
        //----------------------------------------------------------------------
        //获得单工况水平位移统计结果
        //nFloor          层号
        //nTower          塔号
        //nLDCase         工况号
        //nOption         1-当前模型，2-连梁刚度不折减模型
        //Dis             分别为层最大位移、平均位移、位移比
        //DisD            分别为层间最大位移、平均位移、位移比
        //DisDAng         分别为层间位移角、层间有害位移角
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetLDCaseHorDisStatNew")]
        public static extern bool dsnGetLDCaseHorDisStatNew(int nFloor, int nTower, int nLDCase, int nOption, double[] Dis, double[] DisD, double[] DisDAng);
        //----------------------------------------------------------------------
        //获得单工况水平位移统计时对应的最大、最小位移对应的全楼节点编号
        //nFloor          层号
        //nTower          塔号
        //nLDCase         工况号
        //nOption         1-当前模型，2-连梁刚度不折减模型
        //nNodeDis        最大、最小绝对位移对应的节点编号
        //nNodeFlrDis     最大、最小层间位移对应的节点编号
        //nNodeFlrAng     层间位移角对应的节点编号
        //nNodeVerDis     竖向力工况为竖向最大位移对应的节点编号
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetHorDisStatNodeTotID")]
        public static extern bool dsnGetHorDisStatNodeTotID(int nFloor, int nTower, int nLDCase, int nOption, int[] nNodeDis, int[] nNodeFlrDis, ref int nNodeFlrAng, ref int nNodeVerDis);
        //----------------------------------------------------------------------
        //获得层刚度
        //nFloor          层号
        //nTower          塔号
        //dSD             X、Y方向层刚度，层间剪力与层间位移之比
        //dSC             X、Y方向层刚度，剪切刚度
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetFlrStiff")]
        public static extern bool dsnGetFlrStiff(int nFloor, int nTower, double[] dSD, double[] dSC);
        //----------------------------------------------------------------------
        //获取转换层上下的剪弯刚度
        //@param tower  塔号
        //@param type   类型  1：转换层以上  -1：转换层以下
        //@param stiff[3] 剪弯刚度，X,Y,RZ
        //@param h  所属部分的高度
        //@param n  所属部分的楼层数
        //@param storys[]  所属部分的楼层号
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetTransFloorStiff")]
        public static extern bool dsnGetTransFloorStiff(int tower, int type, double[] stiff, ref double h, ref int n, int[] storys);
        //----------------------------------------------------------------------
        //获得楼层受剪承载力
        //nFloor          层号
        //nTower          塔号
        //dSC             X、Y方向受剪承载力
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetFlrShearCapacity")]
        public static extern bool dsnGetFlrShearCapacity(int nFloor, int nTower, double[] dSC);
        //----------------------------------------------------------------------
        //获得薄弱层信息
        //nFloor          层号
        //nTower          塔号
        //nBRCSign        薄弱层信息
        //dBRCCoe         X、Y方向薄弱层调整系数
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetBRCSign")]
        public static extern bool dsnGetBRCSign(int nFloor, int nTower, ref int nBRCSign, double[] dBRCCoe);
        //----------------------------------------------------------------------
        //获得分层地震作用放大信息
        //nFloor          层号
        //nTower          塔号
        //dSAmpCoe        X、Y方向地震作用放大系数
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetSeisAmp")]
        public static extern bool dsnGetSeisAmp(int nFloor, int nTower, double[] dSAmpCoe);
        //----------------------------------------------------------------------
        //获得剪重比调整信息
        //nFloor          层号
        //nTower          塔号
        //dJZBCoe         X、Y方向剪重比调整系数
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetJZB")]
        public static extern bool dsnGetJZB(int nFloor, int nTower, double[] dJZBCoe);
        //----------------------------------------------------------------------
        //获得0.2V0调整信息
        //nFloor          层号
        //nTower          塔号
        //dVCoe           X、Y方向0.2V0调整系数
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGet02V0")]
        public static extern bool dsnGet02V0(int nFloor, int nTower, double[] dVCoe);
        //----------------------------------------------------------------------
        //获得墙地震剪力调整系数
        //nFloor          层号
        //nTower          塔号
        //dVCoe           X、Y方向墙调整系数
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetWallCoe_Seis")]
        public static extern bool dsnGetWallCoe_Seis(int nFloor, int nTower, double[] dVCoe);
        //----------------------------------------------------------------------
        //获得墙风剪力调整系数
        //nFloor          层号
        //nTower          塔号
        //dVCoe           +X、-X、+Y、-Y风墙调整系数
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetWallCoe_Wind")]
        public static extern bool dsnGetWallCoe_Wind(int nFloor, int nTower, double[] dVCoe);
        //----------------------------------------------------------------------
        //获得各构件类型CQC下层剪力，先统计单振型内力，再CQC
        //nFloor          层号
        //nTower          塔号
        //dColV           X、Y方向框架柱CQC下剪力，先统计单振型内力，再CQC
        //dColKZZV        X、Y方向框支柱CQC下剪力，先统计单振型内力，再CQC
        //dWallV          X、Y方向剪力墙CQC下剪力，先统计单振型内力，再CQC
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetComFlrV")]
        public static extern bool dsnGetComFlrV(int nFloor, int nTower, double[] dColV, double[] dColKZZV, double[] dWallV);
        //----------------------------------------------------------------------
        //获得规定水平力下层外力
        //nFloor          层号
        //nTower          塔号
        //dFX，dFY        X、Y方向规定水平力外力
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetFlrF_App")]
        public static extern bool dsnGetFlrF_App(int nFloor, int nTower, ref double dFX, ref double dFY);
        //----------------------------------------------------------------------
        //获得各构件类型规定水平力下层剪力
        //nFloor          层号
        //nTower          塔号
        //dColV           X、Y方向框架柱规定水平力下剪力
        //dColKZZV        X、Y方向框支柱规定水平力下剪力
        //dBraceV         X、Y方向支撑规定水平力下剪力
        //dSLegWallV      X、Y方向短肢剪力墙规定水平力下剪力
        //dWallV          X、Y方向一般剪力墙规定水平力下剪力
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetComFlrV_App")]
        public static extern bool dsnGetComFlrV_App(int nFloor, int nTower, double[] dColV, double[] dColKZZV, double[] dBraceV, double[] dSLegWallV, double[] dWallV);
        //----------------------------------------------------------------------
        //获得预制构件规定水平力下层剪力
        //nFloor          层号
        //nTower          塔号
        //dColV           X、Y方向框架柱规定水平力下剪力
        //dColKZZV        X、Y方向框支柱规定水平力下剪力
        //dBraceV         X、Y方向支撑规定水平力下剪力
        //dSLegWallV      X、Y方向短肢剪力墙规定水平力下剪力
        //dWallV          X、Y方向一般剪力墙规定水平力下剪力
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetPrcComFlrV_App")]
        public static extern bool dsnGetPrcComFlrV_App(int nFloor, int nTower, double[] dColV, double[] dBraceV, double[] dWallV);
        //----------------------------------------------------------------------
        //获得各构件类型规定水平力下按轴力方式统计得到的倾覆弯矩
        //nFloor          层号
        //nTower          塔号
        //dColV           X、Y方向框架柱规定水平力下倾覆弯矩
        //dColKZZV        X、Y方向框支柱规定水平力下倾覆弯矩
        //dBraceV         X、Y方向支撑规定水平力下倾覆弯矩
        //dSLegWallV      X、Y方向短肢剪力墙规定水平力下倾覆弯矩
        //dWallV          X、Y方向剪力墙规定水平力下倾覆弯矩
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetComFlrM_AppByAxis")]
        public static extern bool dsnGetComFlrM_AppByAxis(int nFloor, int nTower, double[] dColM, double[] dColKZZM, double[] dBraceM, double[] dSLegWallM, double[] dWallM);
        //----------------------------------------------------------------------
        //获得各构件类型规定水平力下按魏涟改进轴力方式统计得到的倾覆弯矩
        //nFloor          层号
        //nTower          塔号
        //dColV           X、Y方向框架柱规定水平力下倾覆弯矩
        //dColKZZV        X、Y方向框支柱规定水平力下倾覆弯矩
        //dBraceV         X、Y方向支撑规定水平力下倾覆弯矩
        //dSLegWallV      X、Y方向短肢剪力墙规定水平力下倾覆弯矩
        //dWallV          X、Y方向剪力墙规定水平力下倾覆弯矩
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetComFlrM_AppByAxisWL")]
        public static extern bool dsnGetComFlrM_AppByAxisWL(int nFloor, int nTower, double[] dColM, double[] dColKZZM, double[] dBraceM, double[] dSLegWallM, double[] dWallM);
        //----------------------------------------------------------------------
        //获得各构件类型风荷载下层剪力
        //nFloor          层号
        //nTower          塔号
        //dColV           X、Y方向框架柱风荷载下剪力
        //dBraceV         X、Y方向支撑风荷载下剪力
        //dSLegWallV      X、Y方向剪力墙风荷载下剪力
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetComFlrV_Wind")]
        public static extern bool dsnGetComFlrV_Wind(int nFloor, int nTower, double[] dColV, double[] dBraceV, double[] dWallV);
        //----------------------------------------------------------------------
        //获得各种风工况下层外力
        //nFloor          层号
        //nTower          塔号
        //dF              顺风向风外力，数组数量等于4+多方向风，依次为+X、-X、+Y、-Y，多方向风
        //dFH             横风向风外力，数组数量等于4+多方向风，依次为+X、-X、+Y、-Y，多方向风
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetComFlrFH_Wind")]
        public static extern bool dsnGetComFlrFH_Wind(int nFloor, int nTower, double[] dF, double[] dFH);
        //----------------------------------------------------------------------
        //获得各种地震工况下层外力、剪力、倾覆弯矩，考虑分层地震作用放大与剪重比调整
        //nFloor          层号
        //nTower          塔号
        //dFX，dFY        层外力，数组数量等于1+多方向地震+最不利地震，依次为X地震、多方向X地震，最不利X地震
        //dVX，dVY        层剪力，数组数量等于1+多方向地震+最不利地震，依次为X地震、多方向X地震，最不利X地震
        //dMX，dMY        层倾覆弯矩，数组数量等于1+多方向地震+最不利地震，依次为X地震、多方向X地震，最不利X地震
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetComFlrFVM_Seis")]
        public static extern bool dsnGetComFlrFVM_Seis(int nFloor, int nTower, double[] dFX, double[] dFY, double[] dVX, double[] dVY, double[] dMX, double[] dMY);
        //----------------------------------------------------------------------
        //获得按竖向构件内力统计的层地震剪力
        //nFloor          层号
        //nTower          塔号
        //dVX，dVY        层剪力，
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetComFlrVByCom_Seis")]
        public static extern bool dsnGetComFlrVByCom_Seis(int nFloor, int nTower, ref double dVX, ref double dVY);
        //----------------------------------------------------------------------
        //获得整体稳定信息
        //nFloor          层号
        //nTower          塔号
        //dEJd            X、Y方向整体稳定计算数据
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetStability")]
        public static extern bool dsnGetStability(int nFloor, int nTower, double[] dEJd);
        //----------------------------------------------------------------------
        //获得框架结构整体稳定信息
        //nFloor          层号
        //nTower          塔号
        //nOption         1-地震，2-风荷载
        //dStiff          X、Y方向层刚度
        //dCoe            X、Y方向刚重比
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetStability_Frame")]
        public static extern bool dsnGetStability_Frame(int nFloor, int nTower, int nOption, double[] dStiff, double[] dCoe);
        //----------------------------------------------------------------------
        //获得非框架结构整体稳定信息
        //nFloor          层号
        //nTower          塔号
        //nOption         1-地震，2-风荷载
        //dCoe            X、Y方向刚重比
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetStability_NonFrame")]
        public static extern bool dsnGetStability_NonFrame(int nFloor, int nTower, int nOption, double[] dCoe);
        //----------------------------------------------------------------------
        //获得整体抗倾覆验算信息
        //nFloor          层号
        //nTower          塔号
        //dSeisM          X、Y方向地震倾覆弯矩
        //dSeisRM         X、Y方向地震抗倾覆弯矩
        //dWindM          X、Y方向风倾覆弯矩
        //dWindRM         X、Y方向风抗倾覆弯矩
        //dSeisCoe        X、Y方向地震作用下零应力区数值
        //dWindCoe        X、Y方向风作用下零应力区数值
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetOverturn")]
        public static extern bool dsnGetOverturn(int nFloor, int nTower, double[] dSeisM, double[] dSeisRM, double[] dWindM, double[] dWindRM, double[] dSeisCoe, double[] dWindCoe);
        //----------------------------------------------------------------------
        //获得质心、刚心坐标
        //nFloor          层号
        //nTower          塔号
        //mc              质心坐标
        //sc              质心坐标
        //stiff           剪弯刚度，X,Y,RZ
        //ecc             偏心率 ecc_x,ecc_y
        //alpha           刚性主轴的方向(角度)
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetXYZMassandStiff")]
        public static extern void dsnGetXYZMassandStiff(int nFloor, int nTower, double[] mc, double[] sc, double[] stiff, double[] ecc, ref double alpha);
        //----------------------------------------------------------------------
        //获得层风荷载计算指标
        //nFloor          层号
        //nTower          塔号
        //dwx,dwy         分别为外力、层剪力、层倾覆弯矩、层位移、位移角
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetFlrWindInfo")]
        public static extern void dsnGetFlrWindInfo(int nFloor, int nTower, double[] dwx, double[] dwy);
        //----------------------------------------------------------------------
        //获得层地震计算指标，分层地震放大、最小剪重比调整后结果
        //nFloor          层号
        //nTower          塔号
        //nModule         计算模型标记，如基本、强刚、连梁不折减等，采用宏定义
        //dsx,dsy         分别为外力、层剪力、层倾覆弯矩、层位移、位移角
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetFlrSeisInfo")]
        public static extern void dsnGetFlrSeisInfo(int nFloor, int nTower, int nModule, double[] dsx, double[] dsy);
        //----------------------------------------------------------------------
        //获得调整前层地震剪力
        //nFloor          层号
        //nTower          塔号
        //dsx,dsy         分别为X、Y地震层剪力
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetFlrSeisVBeforeAdjust")]
        public static extern bool dsnGetFlrSeisVBeforeAdjust(int nFloor, int nTower, ref double dsx, ref double dsy);
        //----------------------------------------------------------------------
        //获得风振舒适度验算结果
        //nFloor          层号
        //nTower          塔号
        //dwx,dwy         分别为X、Y方向顺风向、横风向风振加速度
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetWindComfortInfo")]
        public static extern bool dsnGetWindComfortInfo(int nFloor, int nTower, double[] dwx, double[] dwy);


        //==============================via wjc =======================

        //是否有设计数据，目前仅是检查数据文件是否存在
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnHasDesignData")]
        public static extern bool dsnHasDesignData();

        //----------------------------------------------------------------------
        //初始化全楼楼层索引数据，在调用下述所有接口前调用，调用一次即可

        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnInitData")]
        public static extern bool dsnInitData();

        //----------------------------------------------------------------------
        //是否已经初始化过数据

        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnHasInitData")]
        public static extern bool dsnHasInitData();

        //----------------------------------------------------------------------
        //根据分塔塔号重置工程数据
        //nTower          分塔塔号

        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnResetDataByTower")]
        public static extern bool dsnResetDataByTower(int nTower);

        //----------------------------------------------------------------------
        //根据少墙框架重置工程数据
        //nTower          分塔塔号

        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnResetDataBySQKJ")]
        public static extern bool dsnResetDataBySQKJ(int nTower);

        //----------------------------------------------------------------------
        //根据门刚模型号重置工程数据
        //nPortal         门刚榀号

        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnResetDataByPortalNo")]
        public static extern bool dsnResetDataByPortalNo(int nPortal);

        //----------------------------------------------------------------------
        //根据单榀模型号重置工程数据
        //nFrame          单榀模型号

        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnResetDataByFrameNo")]
        public static extern bool dsnResetDataByFrameNo(int nFrame);

        //----------------------------------------------------------------------
        //根据包络性能设计子模型号重置工程数据
        //nXNSJ           性能设计子模型号

        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnResetDataByXNSJNo")]
        public static extern bool dsnResetDataByXNSJNo(int nXNSJ);

        //----------------------------------------------------------------------
        //根据隔震性能设计子模型号重置工程数据
        //nXNSJGZ         隔震性能设计子模型号 
        //9003[隔震性能设计-大震弹性]  9004[隔震性能设计-大震不屈服]

        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnResetDataByXNSJGZNo")]
        public static extern bool dsnResetDataByXNSJGZNo(int nXNSJGZ);

        //----------------------------------------------------------------------
        //根据砌体中混凝土构件模型重置工程数据
        //nTower          分塔塔号

        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnResetDataByQTCon")]
        public static extern bool dsnResetDataByQTCon();

        //----------------------------------------------------------------------
        //获得当前工程状态
        //返回值          =0 整体模型
        //                >0&&<1000 多塔分塔模型对应的塔号
        //                >5000 门刚多模型对应的模型号
        //                =1000少墙框架模型
        //                =6000砌体中的混凝土构件设计
        //                >=7000性能设计 +1-中震不屈服，+2-中震弹性，+3-大震不屈服，+4-大震弹性
        //                >=8000单榀 +0-非门刚，+1-门刚
        //                >=9000隔震性能设计 +3-大震不屈服，+4-大震弹性

        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetProStatus")]
        public static extern int dsnGetProStatus();

        //----------------------------------------------------------------------
        //退出DLL时的相关操作，如根据用户交互修改结果重新保存配筋文件

        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnExit")]
        public static extern void dsnExit();

        //----------------------------------------------------------------------
        //设置当前楼层，程序将读取该楼层构件索引，并生成该层构件配筋信息
        //nFloor          楼层号，从1开始


        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnReadFloorPJ")]
        public static extern bool dsnReadFloorPJ(int nFloor);

        //----------------------------------------------------------------------
        //重新进行某楼层构件配筋设计
        //nFloor          楼层号，从1开始

        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnReDesignFloorPJ")]
        public static extern void dsnReDesignFloorPJ(int nFloor);

        //----------------------------------------------------------------------
        //获得版本号

        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetVersion")]
        public static extern int dsnGetVersion();

        //----------------------------------------------------------------------
        //获得配筋数据文件生成时间

        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetPJTime")]
        public static extern int dsnGetPJTime();

        //----------------------------------------------------------------------
        //获得当前楼层

        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetCurFloor")]
        public static extern int dsnGetCurFloor();

        //----------------------------------------------------------------------
        //设置构件设计结果接口中构件指针来源
        //nComPtrFrom     =1 从本层数据中获得
        //nComPtrFrom     =2 从全楼构件索引中获得

        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnSetComPtrResource")]
        public static extern void dsnSetComPtrResource(int nComPtrFrom);

        //----------------------------------------------------------------------
        //设置配筋文件来源
        //nPJFileSource     1-基本配筋文件，2-包络设计用配筋文件，3-钢筋标准层配筋文件，4-工程对比配筋文件
        //bReadFlrPJ  是否重新读取当前层配筋

        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnChangePJFileSource")]
        public static extern bool dsnChangePJFileSource(int nPJFileSource, bool bReadFlrPJ);


        //----------------------------------------------------------------------
        //获得配筋文件来源，1-基本配筋文件，2-包络设计用配筋文件，3-钢筋标准层配筋文件，4-工程对比配筋文件

        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetPJFileSource")]
        public static extern int dsnGetPJFileSource();


        //----------------------------------------------------------------------

        //////////////////////////////////////////////////////////////
        //包络设计用操作函数
        //////////////////////////////////////////////////////////////
        //获得无对应关系构件编号
        //nFloor           楼层号，从1开始
        //nComKind(in)     构件类型
        //nNum(out)        构件数量
        //TotID(out)       构件全楼编号

        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetBLSJComNotFound")]
        public static extern void dsnGetBLSJComNotFound(int nFloor, int nComKind, ref int nNum, int[] TotID);

        //----------------------------------------------------------------------
        //----------------------------------------------------------------------
        //本工程构件对应的对比工程构件全楼编号
        //nFloor           楼层号，从1开始
        //nComKind(in)     构件类型
        //nTotID(in)       构件全楼编号
        //nFloorT(out)     对比工程楼层号，从1开始
        //nTotIDT(out)     对比工程构件全楼编号

        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetRelComID")]
        public static extern bool dsnGetRelComID(int nFloor, int nComKind, int nTotID, ref int nFloorT, ref int nTotIDT);

        //----------------------------------------------------------------------
        //本工程构件对应的对比工程层号，目前的规则仅能支持一对一的关系
        //nFloor           楼层号，从1开始
        //nFloorT(out)     对比工程楼层号，从1开始

        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetRelFloor")]
        public static extern bool dsnGetRelFloor(int nFloor, ref int nFloorT);


        //////////////////////////////////////////////////////////////
        //优化设计用操作函数
        //////////////////////////////////////////////////////////////
        //生成工程对比数据
        //sProPath          工程路径
        //dxyz              原点在本工程中的位置
        //dAng              相对应本工程转角（弧度），逆时针为正

        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnComOptimization")]
        public static extern bool dsnComOptimization();

        //公共操作函数
        //////////////////////////////////////////////////////////////
        //判断构件是否设计结果超限
        //nFloor           楼层号，从1开始
        //nComKind(in)     构件类型
        //nTotID(in)       构件全楼编号

        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnComHasLimitInf")]
        public static extern bool dsnComHasLimitInf(int nFloor, int nComKind, int nTotID);

        //----------------------------------------------------------------------
        //获得构件全部超限信息，包括截面验算与构件验算，不重复
        //nFloor           楼层号，从1开始
        //nComKind(in)     构件类型
        //nTotID(in)       构件全楼编号
        //nNum(out)        超限信息数量
        //LimitInf(out)    超限信息宏定义数据

        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetComTotLimitInf")]
        public static extern void dsnGetComTotLimitInf(int nFloor, int nComKind, int nTotID, ref int nNum, int[] LimitInf);

        //----------------------------------------------------------------------
        //获得构件超限信息
        //nFloor           楼层号，从1开始
        //nComKind(in)     构件类型
        //nTotID(in)       构件全楼编号
        //nNum(out)        超限信息数量
        //LimitInf(out)    超限信息宏定义数据

        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetComLimitInf")]
        public static extern void dsnGetComLimitInf(int nFloor, int nComKind, int nTotID, ref int nNum, int[] LimitInf);

        //----------------------------------------------------------------------
        //获得构件截面超限信息
        //nFloor           楼层号，从1开始
        //nComKind(in)     构件类型
        //nTotID(in)       构件全楼编号
        //nSectPos(in)     截面位置,0开始，对于梁为从左到右；对于柱、支撑、墙为从上到下
        //nNum(out)        超限信息数量
        //LimitInf(out)    超限信息宏定义数据

        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetComSectLimitInf")]
        public static extern void dsnGetComSectLimitInf(int nFloor, int nComKind, int nTotID, int nSectPos, ref int nNum, int[] LimitInf);

        //----------------------------------------------------------------------
        //获得构件对应的建模截面定义编号，1开始
        //nFloor           楼层号，从1开始
        //nComKind(in)     构件类型
        //nTotID(in)       构件全楼编号
        //sComSect(out)    构件截面字符串


        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetComPMSectID")]
        public static extern int dsnGetComPMSectID(int nFloor, int nComKind, int nTotID);

        //----------------------------------------------------------------------
        //获得构件加固做法建模编号
        //nFloor           楼层号，从1开始
        //nComKind(in)     构件类型
        //nTotID(in)       构件全楼编号
        //nJGKind(out)     加固做法，采用宏定义
        //nJGPMID(out)     加固做法建模编号

        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetComJDJGMethod")]
        public static extern bool dsnGetComJDJGMethod(int nFloor, int nComKind, int nTotID, ref int nJGKind, ref int nJGPMID);

        //----------------------------------------------------------------------
        //----------------------------------------------------------------------
        //输出构件信息
        //nFloor           楼层号，从1开始
        //nComKind(in)     构件类型
        //nTotID(in)       构件全楼编号

        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnOutputComInf")]
        public static extern void dsnOutputComInf(int nFloor, int nComKind, int nTotID);

        //输出构件信息-WORD
        //nFloor           楼层号，从1开始
        //nComKind(in)     构件类型
        //nTotID(in)       构件全楼编号

        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnOutputComInf_Word")]
        public static extern bool dsnOutputComInf_Word(int nFloor, int nComKind, int nTotID);

        //----------------------------------------------------------------------
        //调用截面验算工具
        //nFloor           楼层号，从1开始
        //nComKind(in)     构件类型
        //nTotID(in)       构件全楼编号

        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnShowDSNToolsDlg")]
        public static extern void dsnShowDSNToolsDlg(int nFloor, int nComKind, int nTotID);

        //----------------------------------------------------------------------
        //获得底层柱、墙底预组合内力
        //nFloor           楼层号
        //nComKind(in)     构件类型
        //nTotID(in)       构件全楼编号
        //nPrcCombKind(in) 预组合工况号
        //nSect(out)       截面数量
        //fnl(out)         返回设计内力，第一维为截面数量，第二维分别为X弯矩，Y弯矩，X剪力，Y剪力，轴力，扭矩
        //nLDCombID        组合号

        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetComPrcNL")]
        public static extern void dsnGetComPrcNL(int nFloor, int nComKind, int nTotID, int nPrcCombKind, ref int nSect, float[,] fnl, ref int nLDCombID);

        //----------------------------------------------------------------------
        //将构件局部坐标系下内力换算成整体坐标系
        //nFloor           楼层号
        //nComKind(in)     构件类型
        //nTotID(in)       构件全楼编号
        //nSect(in)        截面位置
        //dnl(in)          输入内力，分别为X弯矩，Y弯矩，X剪力，Y剪力，轴力，扭矩
        //dnlret(out)      返回内力，分别为X弯矩，Y弯矩，X剪力，Y剪力，轴力，扭矩

        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnTranComNLToMainCoor")]
        public static extern void dsnTranComNLToMainCoor(int nFloor, int nComKind, int nTotID, int nSect, double[] dnl, double[] dnlret);

        //----------------------------------------------------------------------
        //将构件整体坐标系下内力换算成局部坐标系
        //nFloor           楼层号
        //nComKind(in)     构件类型
        //nTotID(in)       构件全楼编号
        //nSect(in)        截面位置
        //dnl(in)          输入内力，分别为X弯矩，Y弯矩，X剪力，Y剪力，轴力，扭矩
        //dnlret(out)      返回内力，分别为X弯矩，Y弯矩，X剪力，Y剪力，轴力，扭矩

        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnTranComNLToLocalCoor")]
        public static extern void dsnTranComNLToLocalCoor(int nFloor, int nComKind, int nTotID, int nSect, double[] dnl, double[] dnlret);

        //----------------------------------------------------------------------
        //判断某构件是否需要输出标准内力
        //nFloor           楼层号
        //nComKind(in)     构件类型
        //nTotID(in)       构件全楼编号

        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnShowDSNToolsDlg")]
        public static extern bool dsnComNeedWriteStlNL(int nFloor, int nComKind, int nTotID);

        //----------------------------------------------------------------------
        //判断某构件是否需要设计
        //nFloor           楼层号
        //nComKind(in)     构件类型
        //nTotID(in)       构件全楼编号

        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnComNeedDesign")]
        public static extern bool dsnComNeedDesign(int nFloor, int nComKind, int nTotID);

        //----------------------------------------------------------------------
        //获得某构件单工况内力
        //nFloor           楼层号
        //nComKind(in)     构件类型
        //nTotID(in)       构件全楼编号
        //nLDCase(in)      工况号
        //Option(in)       1-调整前，2-调整后
        //nSect(out)       返回截面数量
        //dnl(out)         返回单工况内力，分别为X弯矩，Y弯矩，X剪力，Y剪力，轴力，扭矩

        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetComStdNL")]
        public static extern bool dsnGetComStdNL(int nFloor, int nComKind, int nTotID, int nLDCase, int Option, ref int nSect, float[,] fnl);

        //----------------------------------------------------------------------
        //判断该组合类型下的正、斜截面组合是否一致
        //nFloor           楼层号
        //nComKind(in)     构件类型
        //nTotID(in)       构件全楼编号
        //nLDCombType      组合类别，如基本组合、标准组合等，采用宏定义


        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetComLDCombIsSame")]
        public static extern bool dsnGetComLDCombIsSame(int nFloor, int nComKind, int nTotID, int nLDCombType);

        //获得某构件基本组合内力
        //nFloor           楼层号
        //nComKind(in)     构件类型
        //nTotID(in)       构件全楼编号
        //nSectDSNType(in) 截面设计类别，如正截面、斜截面，采用宏定义
        //nSect(in)        截面位置
        //nLDCombNum(out)  返回组合数量
        //dnlpre(out)      返回强柱弱梁、强剪弱弯调整前设计内力，分别为X弯矩，Y弯矩，X剪力，Y剪力，轴力，扭矩
        //dnlaft(out)      返回强柱弱梁、强剪弱弯调整后设计内力，分别为X弯矩，Y弯矩，X剪力，Y剪力，轴力，扭矩
        //nSign(out)       组合号

        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetComLDCombNL")]
        public static extern bool dsnGetComLDCombNL(int nFloor, int nComKind, int nTotID, int nSectDSNType, int nSect, ref int nLDCombNum, double[,] dnlpre, double[,] dnlaft, int[,] nSign);

        //----------------------------------------------------------------------
        //获得某构件基本组合内力
        //nFloor           楼层号
        //nComKind(in)     构件类型
        //nTotID(in)       构件全楼编号
        //nSectDSNType(in) 截面设计类别，如正截面、斜截面，采用宏定义
        //nWallSign(in)    数据来源，仅对墙有效，1-受弯截面，2-受剪截面，3-只腹板自身，4-组合轴压比内力
        //nSect(in)        截面位置
        //nLDCombNum(out)  返回组合数量
        //dnlpre(out)      返回强柱弱梁、强剪弱弯调整前设计内力，分别为X弯矩，Y弯矩，X剪力，Y剪力，轴力，扭矩
        //dnlaft(out)      返回强柱弱梁、强剪弱弯调整后设计内力，分别为X弯矩，Y弯矩，X剪力，Y剪力，轴力，扭矩
        //nSign(out)       组合号

        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetComLDCombNLNew")]
        public static extern bool dsnGetComLDCombNLNew(int nFloor, int nComKind, int nTotID, int nSectDSNType, int nWallSign, int nSect, ref int nLDCombNum, double[,] dnlpre, double[,] dnlaft, int[,] nSign);

        //----------------------------------------------------------------------
        //获得某构件标准组合内力
        //nFloor           楼层号
        //nComKind(in)     构件类型
        //nTotID(in)       构件全楼编号
        //nSect(in)        截面位置
        //nLDCombNum(out)  返回组合数量
        //dnl(out)         返回设计内力，分别为X弯矩，Y弯矩，X剪力，Y剪力，轴力，扭矩
        //nSign(out)       组合号

        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetComSTDCombNL")]
        public static extern bool dsnGetComSTDCombNL(int nFloor, int nComKind, int nTotID, int nSect, ref int nLDCombNum, double[,] dnl, int[,] nSign);

        //----------------------------------------------------------------------
        //获得某构件标准组合内力
        //nFloor           楼层号
        //nComKind(in)     构件类型
        //nTotID(in)       构件全楼编号
        //nWallSign(in)    数据来源，仅对墙有效，1-受弯截面，2-受剪截面，3-只腹板自身，4-组合轴压比内力
        //nSect(in)        截面位置
        //nLDCombNum(out)  返回组合数量
        //dnl(out)         返回设计内力，分别为X弯矩，Y弯矩，X剪力，Y剪力，轴力，扭矩
        //nSign(out)       组合号

        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetComSTDCombNLNew")]
        public static extern bool dsnGetComSTDCombNLNew(int nFloor, int nComKind, int nTotID, int nSect, ref int nLDCombNum, double[,] dnl, int[,] nSign);

        //----------------------------------------------------------------------
        //获得某构件频遇组合内力
        //nFloor           楼层号
        //nComKind(in)     构件类型
        //nTotID(in)       构件全楼编号
        //nSect(in)        截面位置
        //nLDCombNum(out)  返回组合数量
        //dnl(out)         返回设计内力，分别为X弯矩，Y弯矩，X剪力，Y剪力，轴力，扭矩
        //nSign(out)       组合号

        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetComFrequentCombNL")]
        public static extern bool dsnGetComFrequentCombNL(int nFloor, int nComKind, int nTotID, int nSect, ref int nLDCombNum, double[,] dnl, int[] nSign);

        //----------------------------------------------------------------------
        //获得某构件准永久组合内力
        //nFloor           楼层号
        //nComKind(in)     构件类型
        //nTotID(in)       构件全楼编号
        //nSect(in)        截面位置
        //nLDCombNum(out)  返回组合数量
        //dnl(out)         返回设计内力，分别为X弯矩，Y弯矩，X剪力，Y剪力，轴力，扭矩
        //nSign(out)       组合号

        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetComQuasiCombNL")]
        public static extern bool dsnGetComQuasiCombNL(int nFloor, int nComKind, int nTotID, int nSect, ref int nLDCombNum, double[,] dnl, int[] nSign);

        //----------------------------------------------------------------------
        //获得某构件某预组合下内力
        //nFloor           楼层号
        //nComKind(in)     构件类型
        //nTotID(in)       构件全楼编号
        //nLDCombType(in)  组合类别，如基本组合、标准组合等，采用宏定义
        //nPrcCombType(in) 预组合类别，采用宏定义
        //nPrcComb (in)    预组合目标，采用宏定义
        //nSect(out)       截面数量
        //dnl(out)         第一维分别为截面位置，第二维分别为X弯矩，Y弯矩，X剪力，Y剪力，轴力，扭矩


        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetComPrcCombNL")]
        public static extern bool dsnGetComPrcCombNL(int nFloor, int nComKind, int nTotID, int nLDCombType, int nPrcCombType, int nPrcComb, ref int nSect, double[,] dnl);

        //----------------------------------------------------------------------
        //获得某构件抗震等级
        //nFloor           楼层号
        //nComKind(in)     构件类型
        //nTotID(in)       构件全楼编号
        //nSect(in)        截面位置
        //nKZDJ(out)       返回抗震等级
        //nKZDJGZ(out)     返回构造措施抗震等级

        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetComKZDJ")]
        public static extern bool dsnGetComKZDJ(int nFloor, int nComKind, int nTotID, ref int nKZDJ, ref int nKZDJGZ);

        //----------------------------------------------------------------------
        //获得某构件多塔分塔设计时，设计结果对应的塔号，有一种设计结果采用了单塔，就返回单塔塔号
        //nFloor           楼层号
        //nComKind(in)     构件类型
        //nTotID(in)       构件全楼编号
        //nSect(in)        截面位置
        //nTow(out)        返回单塔塔号，0为整体


        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetComDSNTow")]
        public static extern bool dsnGetComDSNTow(int nFloor, int nComKind, int nTotID, ref int nTow);

        //----------------------------------------------------------------------
        //获得某构件布置时的转角，目前主要是柱、支撑
        //nFloor           楼层号
        //nComKind(in)     构件类型
        //nTotID(in)       构件全楼编号
        //fAng(out)        返回转角（弧度）


        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetComAng")]
        public static extern bool dsnGetComAng(int nFloor, int nComKind, int nTotID, ref float fAng);

        //----------------------------------------------------------------------
        //判断某组合类别，参见dsndatadefine.h
        //nFloor           楼层号
        //nComKind(in)     构件类型
        //nTotID(in)       构件全楼编号
        //nLDCombID(in)    组合号

        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetLDCombKind")]
        public static extern int dsnGetLDCombKind(int nFloor, int nComKind, int nTotID, int nLDCombID);

        //----------------------------------------------------------------------
        //判断某组合类别，参见dsndatadefine.h
        //nFloor           楼层号
        //nComKind(in)     构件类型
        //nTotID(in)       构件全楼编号
        //nLDCombType(in)  组合类别，如基本、标准等，采用宏定义
        //nSectDSNType(in) 截面设计类别，如正截面、斜截面，采用宏定义
        //nLDCombID(in)    组合号

        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetLDCombKindByCombType")]
        public static extern int dsnGetLDCombKindByCombType(int nFloor, int nComKind, int nTotID, int nLDCombType, int nSectDSNType, int nLDCombID);

        //----------------------------------------------------------------------
        //判断某组合类别是否是风荷载参与组合，参见dsndatadefine.h
        //nFloor           楼层号
        //nComKind(in)     构件类型
        //nTotID(in)       构件全楼编号
        //nLDCombType(in)  组合类别，如基本、标准等，采用宏定义
        //nSectDSNType(in) 截面设计类别，如正截面、斜截面，采用宏定义
        //nLDCombID(in)    组合号

        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnLDCombHasWind")]
        public static extern bool dsnLDCombHasWind(int nFloor, int nComKind, int nTotID, int nLDCombType, int nSectDSNType, int nLDCombID);

        //----------------------------------------------------------------------
        //判断某组合类别，参见dsndatadefine.h
        //nFloor           楼层号
        //nComKind(in)     构件类型
        //nTotID(in)       构件全楼编号
        //nPMSectNO(out)   建模截面编号
        //nPMSectKind(out) 建模截面类型

        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetComSectID")]
        public static extern void dsnGetComSectID(int nFloor, int nComKind, int nTotID, ref int nPMSectNO, ref int nPMSectKind);

        //----------------------------------------------------------------------
        //获得构件轴向承载力
        //nFloor           楼层号
        //nComKind(in)     构件类型
        //nTotID(in)       构件全楼编号
        //nCalSign         数据来源，仅对墙有效，1-受弯截面，2-受剪截面，3-只腹板自身，4-组合轴压比内力
        //bStlCZLByCon     钢材强度值按照钢材与砼弹膜比值换算
        //fNCZLY(out)      轴压承载力
        //fNCZLYK(out)     按标准值计算的轴压承载力
        //fNCZLYU(out)     按极限值计算的轴压承载力
        //fNCZLL(out)      轴拉承载力
        //fNCZLLK(out)     按标准值计算的轴拉承载力
        //fNCZLLU(out)     按极限值计算的轴拉承载力

        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetComNCZL")]
        public static extern void dsnGetComNCZL(int nFloor, int nComKind, int nTotID, int nCalSign, bool bStlCZLByCon, ref float fNCZLY, ref float fNCZLYK, ref float fNCZLYU, ref float fNCZLL, ref float fNCZLLK, ref float fNCZLLU);

        //----------------------------------------------------------------------
        //获得构件N-M曲线数据
        //nFloor           楼层号
        //nComKind(in)     构件类型
        //nTotID(in)       构件全楼编号
        //nLDCombKind(in)  组合类别，目前采用荷载组合类别宏定义
        //nNumX(out)       返回数组容量
        //fDataX(out)      返回数据，第一维为数量，第二维分别为弯矩、轴力
        //nNumY(out)       返回数组容量
        //fDataY(out)      返回数据，第一维为数量，第二维分别为弯矩、轴力

        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetComNMGraphData")]
        public static extern bool dsnGetComNMGraphData(int nFloor, int nComKind, int nTotID, int nLDCombKind, ref int nNumX, float[,] fDataX, ref int nNumY, float[,] fDataY);

        //----------------------------------------------------------------------
        //输出构件N-M曲线数据到文本
        //nFloor           楼层号
        //nComKind(in)     构件类型
        //nTotID(in)       构件全楼编号
        //nLDCombKind(in)  组合类别，目前采用荷载组合类别宏定义

        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnOutputComNMGraphData")]
        public static extern bool dsnOutputComNMGraphData(int nFloor, int nComKind, int nTotID, int nLDCombKind);

        //----------------------------------------------------------------------
        //获得梁设计内力
        //nFloor           楼层号，从1开始
        //nComKind(in)     构件类型
        //nTotID(in)       梁全楼编号
        //nSect(out)       截面数量
        //fnl(out)         返回设计内力，第一维为截面位置，第二维分别为上截面纵筋、下截面纵筋、箍筋，第三维分别为X弯矩，Y弯矩，X剪力，Y剪力，轴力，扭矩

        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetBeamNLBL")]
        public static extern bool dsnGetBeamNLBL(int nFloor, int nComKind, int nTotID, ref int nSect, float[,] fnl);

        //----------------------------------------------------------------------
        //获得构件局部坐标系
        //nFloor           楼层号，从1开始
        //nComKind(in)     构件类型
        //nTotID(in)       构件全楼编号
        //v(out)           返回局部坐标系

        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetComLocalCoor")]
        public static extern bool dsnGetComLocalCoor(int nFloor, int nComKind, int nTotID, double[,] v);

        //----------------------------------------------------------------------
        //获得构件剪压比计算结果
        //nFloor           楼层号
        //nComKind(in)     构件类型
        //nTotID(in)       构件全楼编号
        //nSect(in)        截面位置
        //fJYB(out)        返回剪压比数值，考虑承载力抗震调整系数
        //fJYBMax(out)     返回剪压比限值
        //dnlret(out)      返回内力，分别为X弯矩，Y弯矩，X剪力，Y剪力，轴力，扭矩

        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetComJYB")]
        public static extern bool dsnGetComJYB(int nFloor, int nComKind, int nTotID, int nSect, ref float fJYB, ref float fJYBMax, float[] fnl);

        //----------------------------------------------------------------------
        //获得构件节点核芯区剪压比计算结果
        //nFloor           楼层号
        //nComKind(in)     构件类型
        //nTotID(in)       构件全楼编号
        //nDir(in)         方向，1-局部坐标系X方向，2-局部坐标系Y方向
        //fJYB(out)        返回剪压比数值，考虑承载力抗震调整系数
        //fJYBMax(out)     返回剪压比限值
        //dnlret(out)      返回内力，分别为X弯矩，Y弯矩，X剪力，Y剪力，轴力，扭矩

        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetComJointJYB")]
        public static extern bool dsnGetComJointJYB(int nFloor, int nComKind, int nTotID, int nDir, ref float fJYB, ref float fJYBMax, float[] fnl);

        //----------------------------------------------------------------------
        //获得构件是否是装配式预制构件标记
        //nFloor           楼层号
        //nComKind(in)     构件类型
        //nTotID(in)       构件全楼编号

        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnComIsPC")]
        public static extern bool dsnComIsPC(int nFloor, int nComKind, int nTotID);

        //----------------------------------------------------------------------
        //获得构件性能系数
        //nFloor           楼层号
        //nComKind(in)     构件类型
        //nTotID(in)       构件全楼编号
        //fRealXNXS(out)   构件实际性能系数
        //fXNXS(in)        构件输入性能系数，已考虑beta

        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetComXNXS")]
        public static extern bool dsnGetComXNXS(int nFloor, int nComKind, int nTotID, ref float fRealXNXS, ref float fXNXS);



        //////////////////////////////////////////////////////////////
        //框架梁设计结果输出
        //////////////////////////////////////////////////////////////
        //获得梁属性
        //nFloor           楼层号，从1开始
        //nTotID(in)       梁全楼编号

        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetComXNXS")]
        public static extern int dsnGetBeamKind(int nFloor, int nTotID);

        //----------------------------------------------------------------------
        //获得梁材料属性
        //nFloor           楼层号，从1开始
        //nTotID(in)       梁全楼编号

        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetBeamMatKind")]
        public static extern int dsnGetBeamMatKind(int nFloor, int nTotID);

        //----------------------------------------------------------------------
        //获得梁支座信息
        //nFloor           楼层号，从1开始
        //nTotID(in)       梁全楼编号

        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetBeamSupKind")]
        public static extern bool dsnGetBeamSupKind(int nFloor, int nTotID, ref int nSupS, ref int nSupE);

        //----------------------------------------------------------------------
        //获得挑梁信息
        //nFloor           楼层号，从1开始
        //nTotID(in)       梁全楼编号

        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetBeamCanti")]
        public static extern int dsnGetBeamCanti(int nFloor, int nTotID);

        //----------------------------------------------------------------------
        //获得梁标准内力
        //nFloor           楼层号，从1开始
        //nTotID(in)       梁全楼编号
        //nLDCase(in)      工况号
        //Option(in)       1-调整前，2-调整后
        //nSect(out)       截面数量
        //force(out)       返回内力，第一维为截面数量，第二维分别为：X弯矩，Y弯矩，X剪力，Y剪力，轴力，扭矩

        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetBeamStdForce")]
        public static extern bool dsnGetBeamStdForce(int nFloor, int nTotID, int nLDCase, int Option, ref int nSect, float[,] Force);

        //----------------------------------------------------------------------
        //获得梁施工阶段验算标准内力
        //nFloor           楼层号，从1开始
        //nTotID(in)       梁全楼编号
        //nLDCase(in)      工况号
        //Option(in)       1-调整前，2-调整后
        //nSect(out)       截面数量
        //force(out)       返回内力，第一维为截面数量，第二维分别为：X弯矩，Y弯矩，X剪力，Y剪力，轴力，扭矩


        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetBeamStdForceSG")]
        public static extern bool dsnGetBeamStdForceSG(int nFloor, int nTotID, int nLDCase, int Option, ref int nSect, float[,] Force);

        //----------------------------------------------------------------------
        //获得混凝土、型钢混凝土梁某截面配筋
        //nFloor           楼层号，从1开始
        //nTotID(in)       梁全楼编号
        //nSect(out)       截面数量
        //fpj(out)         返回配筋面积，第一维为截面编号，第二维分别为上截面纵筋、下截面纵筋、箍筋，第三维分别为配筋面积、配筋率，组合号
        //fnl(out)         返回设计内力，第一维为截面位置，第二维分别为上截面纵筋、下截面纵筋、箍筋，第三维分别为X弯矩，Y弯矩，X剪力，Y剪力，轴力，扭矩

        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetBeamAs")]
        public static extern void dsnGetBeamAs(int nFloor, int nTotID, ref int nSect, float[,,] fpj, float[,,] fnl);

        //----------------------------------------------------------------------
        //获得混凝土、型钢混凝土梁某截面配筋
        //nFloor           楼层号，从1开始
        //nTotID(in)       梁全楼编号
        //nSect(out)       截面数量
        //fpj(out)         返回配筋面积，第一维为截面编号，第二维分别为上截面纵筋、下截面纵筋、箍筋，第三维分别为配筋面积、计算配筋面积、配筋率，组合号
        //fnl(out)         返回设计内力，第一维为截面位置，第二维分别为上截面纵筋、下截面纵筋、箍筋，第三维分别为X弯矩，Y弯矩，X剪力，Y剪力，轴力，扭矩

        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetBeamAsWithCal")]
        public static extern bool dsnGetBeamAsWithCal(int nFloor, int nTotID, ref int nSect, float[,,] fpj, float[,,] fnl);

        //=====================================================================================

        //----------------------------------------------------------------------
        //获得混凝土、型钢混凝土梁某截面配筋率
        //nFloor           楼层号，从1开始
        //nTotID(in)       梁全楼编号
        //nSect(out)       截面数量
        //fpj(out)         返回配筋面积，第一维为截面编号，第二维分别为上截面纵筋、下截面纵筋、箍筋，第三维分别为配筋率，最小配筋率，最大配筋率
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetBeamPJRatio")]
        public static extern bool dsnGetBeamPJRatio(int nFloor, int nTotID, ref int nSect, float[,,] fpjr);
        //----------------------------------------------------------------------
        //获得混凝土梁加密区、非加密区箍筋面积
        //nFloor           楼层号，从1开始
        //nTotID(in)       梁全楼编号
        //fHoopBarJM(out)  返回加密区箍筋面积
        //fHoopBar(out)    返回非加密区箍筋面积
        //fHoopBarJMRatio(out)  返回加密区箍筋面积
        //fHoopBarRatio(out)    返回非加密区箍筋面积
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetBeamAsVJM")]
        public static extern void dsnGetBeamAsVJM(int nFloor, int nTotID, ref float fHoopBarJM, ref float fHoopBar, ref float fHoopBarJMRatio, ref float fHoopBarRatio);
        //----------------------------------------------------------------------
        //获得混凝土梁剪扭配筋
        //nFloor           楼层号，从1开始
        //nTotID(in)       梁全楼编号
        //nSect(out)       截面数量
        //fpj(out)         返回配筋面积，第一维为截面编号，第二维分别为受扭沿周边单肢箍筋面积、受扭纵筋面积、计算受扭纵筋面积
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetBeamAsTL")]
        public static extern void dsnGetBeamAsTL(int nFloor, int nTotID, ref int nSect, float[,] fpj);
        //----------------------------------------------------------------------
        //获得混凝土连梁斜筋配筋
        //nFloor           楼层号，从1开始
        //nTotID(in)       梁全楼编号
        //nSect(out)       截面数量
        //fpj(out)         返回配筋面积，第一维为截面编号，第二维分别为斜筋面积、计算斜筋面积、斜筋角度、组合号
        //fnl(out)         返回设计内力，第一维为截面位置，第二维分别为X弯矩，Y弯矩，X剪力，Y剪力，轴力，扭矩
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetBeamAsXJ")]
        public static extern void dsnGetBeamAsXJ(int nFloor, int nTotID, ref int nSect, float[,,] fpj, float[,,] fnl);
        //----------------------------------------------------------------------
        //获得混凝土梁受压区高度
        //nFloor           楼层号，从1开始
        //nTotID(in)       梁全楼编号
        //nSect(out)       截面数量
        //fxi(out)         返回受压区高度，第一维为截面编号，第二维分别为受压区高度、界限受压区高度
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetBeamConPressHei")]
        public static extern bool dsnGetBeamConPressHei(int nFloor, int nTotID, ref int nSect, float[,] fxi);
        //----------------------------------------------------------------------
        //获得钢梁应力验算结果，包含组合梁
        //nFloor           楼层号，从1开始
        //nTotID(in)       梁全楼编号
        //nSect(out)       截面数量
        //fpj(out)         返回验算结果，第一维为截面编号，第二维分别为上截面强度、下截面强度、上截面稳定、下截面稳定、抗剪强度，第三维分别为计算应力、允许应力，组合号
        //fnl(out)         返回设计内力，第一维为截面位置，第二维分别为上截面强度、下截面强度、上截面稳定、下截面稳定、抗剪强度，第三维分别为X弯矩，Y弯矩，X剪力，Y剪力，轴力，扭矩
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetSteelBeamCheck")]
        public static extern void dsnGetSteelBeamCheck(int nFloor, int nTotID, ref int nSect, float[,,] fpj, float[,,] fnl);
        //----------------------------------------------------------------------
        //获得钢梁应力验算结果，包含组合梁
        //nFloor           楼层号，从1开始
        //nTotID(in)       梁全楼编号
        //nSect(out)       截面数量
        //fpj(out)         返回验算结果，第一维为截面编号，第二维分别为上截面强度、下截面强度、上截面稳定、下截面稳定、抗剪强度、下翼缘畸变失稳，第三维分别为计算应力、允许应力，组合号
        //fnl(out)         返回设计内力，第一维为截面位置，第二维分别为上截面强度、下截面强度、上截面稳定、下截面稳定、抗剪强度、下翼缘畸变失稳，第三维分别为X弯矩，Y弯矩，X剪力，Y剪力，轴力，扭矩
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetSteelBeamCheckNew")]
        public static extern void dsnGetSteelBeamCheckNew(int nFloor, int nTotID, ref int nSect, float[,,] fpj, float[,,] fnl);
        //----------------------------------------------------------------------
        //获得钢梁截面验算结果，包含组合梁
        //nFloor           楼层号，从1开始
        //nTotID(in)       梁全楼编号
        //BTRatio(out)     宽厚比
        //BTRatioMax(out)  宽厚比限值
        //HTRatio(out)     高厚比
        //HTRatioMax(out)  高厚比限值
        //fBTRatioReg(out)     外伸受压翼缘正则化宽厚比
        //fBTRatioRegMax(out)  外伸受压翼缘正则化宽厚比限值
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetSteelBeamSectCheck")]
        public static extern bool dsnGetSteelBeamSectCheck(int nFloor, int nTotID, ref float BTRatio, ref float BTRatioMax, ref float HTRatio, ref float HTRatioMax, ref float fBTRatioReg, ref float fBTRatioRegMax);
        //----------------------------------------------------------------------
        //获得型钢砼梁截面验算结果
        //nFloor           楼层号，从1开始
        //nTotID(in)       梁全楼编号
        //BTRatio(out)     宽厚比
        //BTRatioMax(out)  宽厚比限值
        //HTRatio(out)     高厚比
        //HTRatioMax(out)  高厚比限值
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetSRCBeamSectCheck")]
        public static extern bool dsnGetSRCBeamSectCheck(int nFloor, int nTotID, ref float BTRatio, ref float BTRatioMax, ref float HTRatio, ref float HTRatioMax);
        //----------------------------------------------------------------------
        //获得钢梁防火应力验算结果，包含组合梁
        //nFloor           楼层号，从1开始
        //nTotID(in)       梁全楼编号
        //nSect(out)       截面数量
        //fpj(out)         返回验算结果，第一维为截面编号，第二维分别为上截面强度、下截面强度、上截面稳定、下截面稳定、抗剪强度，第三维分别为计算应力、允许应力，组合号
        //fnl(out)         返回设计内力，第一维为截面位置，第二维分别为上截面强度、下截面强度、上截面稳定、下截面稳定、抗剪强度，第三维分别为X弯矩，Y弯矩，X剪力，Y剪力，轴力，扭矩
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetSteelBeamCheck_FH")]
        public static extern void dsnGetSteelBeamCheck_FH(int nFloor, int nTotID, ref int nSect, float[,,] fpj, float[,,] fnl);
        //----------------------------------------------------------------------
        //获得门式刚梁坡度改变率
        //nFloor           楼层号，从1开始
        //nTotID(in)       梁全楼编号
        //fSlope(out)      初始坡度
        //fSlopeLast(out)  考虑位移后坡度
        //fSlopeRatio(out) 坡度改变率
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetPortalBeamSlope")]
        public static extern bool dsnGetPortalBeamSlope(int nFloor, int nTotID, ref float fSlope, ref float fSlopeLast, ref float fSlopeRatio);
        //----------------------------------------------------------------------
        //获得梁跨高比
        //nFloor           楼层号，从1开始
        //nTotID(in)       梁全楼编号
        //fRatio(out)      跨高比
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetBeamSpanHRatio")]
        public static extern bool dsnGetBeamSpanHRatio(int nFloor, int nTotID, ref float fRatio);
        //----------------------------------------------------------------------
        //获得梁基本组合设计内力，适应预应力需求
        //nFloor           楼层号
        //nTotID(in)       构件全楼编号
        //nSectDSNType(in) 截面设计类别，如正截面、斜截面，采用宏定义
        //nCurSect(in)     截面位置
        //dnladd(in)       传入的预应力内力
        //nLDCombNum(out)  返回组合数量
        //dnlpre(out)      返回强柱弱梁、强剪弱弯调整前设计内力，分别为X弯矩，Y弯矩，X剪力，Y剪力，轴力，扭矩
        //dnlaft(out)      返回强柱弱梁、强剪弱弯调整后设计内力，分别为X弯矩，Y弯矩，X剪力，Y剪力，轴力，扭矩
        //nSign(out)       组合号
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetBeamLDCombNL")]
        public static extern bool dsnGetBeamLDCombNL(int nFloor, int nTotID, int nSectDSNType, int nCurSect, double[] dnladd, ref int nLDCombNum, double[] dnlpre, double[,] dnlaft, int[] nSign);
        //----------------------------------------------------------------------
        //是否按偏拉设计，仅针对砼构件有效
        //nFloor           楼层号
        //nTotID(in)       构件全楼编号
        //返回值            0-非偏拉，1-大偏拉，2-小偏拉
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnIsBeamDesignByPL")]
        public static extern int dsnIsBeamDesignByPL(int nFloor, int nTotID);
        //----------------------------------------------------------------------
        //获得鉴定加固用已有钢筋数据
        //nFloor           楼层号
        //nTotID(in)       构件全楼编号
        //nCurSect(in)     截面位置
        //nMBarKindNumUp(out)        返回梁顶纵筋种类数
        //MBarNumUp(out)             返回梁顶纵筋每一种类钢筋数量
        //fMBarDiaUp(out)            返回梁顶纵筋每一种类钢筋直径(mm)
        //nMBarKindNumDw(out)        返回梁底纵筋种类数
        //MBarNumDw(out)             返回梁底纵筋每一种类钢筋数量
        //fMBarDiaDw(out)            返回梁底纵筋每一种类钢筋直径(mm)
        //nHBarNum(out)              返回箍筋根数
        //fHBarDia(out)              返回箍筋直径(mm)
        //fSpace(out)                返回箍筋间距(mm)
        //bJM(out)                   是否是加密区
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetBeamJDJGExistGJ")]
        public static extern bool dsnGetBeamJDJGExistGJ(int nFloor, int nTotID, int nCurSect, ref int nMBarKindNumUp, int[] MBarNumUp, float[] fMBarDiaUp,
        ref int nMBarKindNumDw, int[] MBarNumDw, float[] fMBarDiaDw,
        ref int nHBarNum, ref float fHBarDia, ref float fHBarSpace, ref bool bJM);
        //----------------------------------------------------------------------
        //获得混凝土、型钢混凝土梁某截面配筋
        //nFloor           楼层号，从1开始
        //nTotID(in)       梁全楼编号
        //nSect(out)       截面数量
        //fpj(out)         返回配筋面积，第一维为截面编号，第二维分别为上截面纵筋、下截面纵筋、箍筋，第三维分别为配筋面积、计算配筋面积、配筋率，组合号（对于有加固做法的情况，分别为计算与构造面积大值、计算面积、定义面积、组合号）
        //fnl(out)         返回设计内力，第一维为截面位置，第二维分别为上截面纵筋、下截面纵筋、箍筋，第三维分别为X弯矩，Y弯矩，X剪力，Y剪力，轴力，扭矩
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetBeamJDJGArea")]
        public static extern bool dsnGetBeamJDJGArea(int nFloor, int nTotID, ref int nSect, float[,,] fpj, float[,,] fnl);
        //----------------------------------------------------------------------
        //获得装配式中预制梁抗剪验算所需钢筋面积
        //nFloor           楼层号，从1开始
        //nTotID(in)       梁全楼编号
        //nCurSect(in)     截面位置，0开始
        //fAc1(in)         叠合梁端后浇砼叠合层面积(mm2)
        //fAk(in)          叠合梁端键槽面积(mm2)（取大后）
        //fAs(out)         返回所需钢筋面积(mm2)
        //nLDCombID(out)   返回对应组合号
        //fnl(out)         返回的设计内力，分别为 X弯矩、 Y弯矩、 X剪力、 Y剪力、 轴力、 扭矩
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetPcBeamShearCheck")]
        public static extern bool dsnGetPcBeamShearCheck(int nFloor, int nTotID, int nCurSect, float fAc1, float fAk, ref float fAs, ref int nLDCombID, float[] fnl);
        //----------------------------------------------------------------------
        //获得根据竖向支座划分的主梁信息，临时生成
        //nFloor           楼层号，从1开始
        //nNodeTotID(in)   节点计算编号
        //nBeamTotIDS(in)  前段梁全楼编号
        //nBeamTotIDE(in)  后段梁全楼编号
        //fAddAs(out)      分别为组合号、设计内力、附加钢筋面积（按箍筋计算）
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetSubBeamAddPJ")]
        public static extern bool dsnGetSubBeamAddPJ(int nFloor, int nNodeTotID, int nBeamTotIDS, int nBeamTotIDE, float[] fAddAs);
        //----------------------------------------------------------------------

        //////////////////////////////////////////////////////////////
        //主梁设计结果输出
        //////////////////////////////////////////////////////////////
        //获得主梁数量
        //nFloor             楼层号，从1开始
        //nMainBeamNum(out)  梁段数量
        //nMainBeamID(out)   梁段编号数组
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetMainBeamNum")]
        public static extern void dsnGetMainBeamNum(int nFloor, ref int nMainBeamNum, int[] nMainBeamID);
        //----------------------------------------------------------------------
        //获得某主梁包含的梁段编号
        //nFloor           楼层号，从1开始
        //ID(in)           主梁编号
        //BeamSegNum(out)  梁段数量
        //BeamSegID(out)   梁段全楼编号数组
        //BeamSegDir(out)  梁段方向与主梁方向
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetBeamSegIDbyMainBeam")]
        public static extern void dsnGetBeamSegIDbyMainBeam(int nFloor, int ID, ref int BeamSegNum, int[] BeamSegID, int[] BeamSegDir);
        //----------------------------------------------------------------------
        //获得主梁跨度
        //nFloor           楼层号，从1开始
        //ID(in)           主梁编号
        //fSpan(out)       主梁跨度（m)
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetMainBeamSpan")]
        public static extern bool dsnGetMainBeamSpan(int nFloor, int ID, ref float fSpan);
        //----------------------------------------------------------------------
        //获得根据竖向支座划分的主梁信息，临时生成
        //nFloor           楼层号，从1开始
        //nMainBeamNum(out)梁段数量
        //nMainBeamID(out) 梁段编号数组
        //BeamSegNum(out)  梁段数量
        //BeamSegID(out)   梁段全楼编号数组，按一维数组记录
        //BeamSegDir(out)  梁段方向与主梁方向，按一维数组记录
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetVerSupMainBeam")]
        public static extern void dsnGetVerSupMainBeam(int nFloor, ref int nMainBeamNum, int[] nMainBeamID, int[] BeamSegNum, int[] BeamSegID, int[] BeamSegDir);
        //----------------------------------------------------------------------

        //////////////////////////////////////////////////////////////
        //次梁设计结果输出
        //////////////////////////////////////////////////////////////
        //获得次梁材料属性
        //nFloor           楼层号，从1开始
        //nTotID(in)       梁全楼编号
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetSubBeamMatKind")]
        public static extern int dsnGetSubBeamMatKind(int nFloor, int nTotID);
        //----------------------------------------------------------------------
        //获得次梁所属塔号
        //nFloor           楼层号，从1开始
        //nTotID(in)       梁全楼编号
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetSubBeamTow")]
        public static extern int dsnGetSubBeamTow(int nFloor, int nTotID);
        //----------------------------------------------------------------------
        //获得次梁标准内力
        //nFloor           楼层号，从1开始
        //nTotID(in)       梁全楼编号
        //nLDCase(in)      工况号
        //Option(in)       1-调整前，2-调整后
        //nSect(out)       截面数量
        //force(out)       返回内力，第一维为截面数量，第二维分别为：X弯矩，Y弯矩，X剪力，Y剪力，轴力，扭矩
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetSubBeamStdForce")]
        public static extern bool dsnGetSubBeamStdForce(int nFloor, int nTotID, int nLDCase, int Option, ref int nSect, float[,] Force);
        //----------------------------------------------------------------------
        //获得混凝土、型钢混凝土次梁某截面配筋
        //nFloor           楼层号，从1开始
        //nTotID(in)       梁全楼编号
        //nSect(out)       截面数量
        //fpj(out)         返回配筋面积，第一维为截面编号，第二维分别为上截面纵筋、下截面纵筋、箍筋，第三维分别为配筋面积、配筋率，组合号
        //fnl(out)         返回设计内力，第一维为截面位置，第二维分别为上截面纵筋、下截面纵筋、箍筋，第三维分别为X弯矩，Y弯矩，X剪力，Y剪力，轴力，扭矩
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetSubBeamAs")]
        public static extern void dsnGetSubBeamAs(int nFloor, int nTotID, ref int nSect, float[,,] fpj, float[,,] fnl);
        //----------------------------------------------------------------------
        //获得混凝土、型钢混凝土次梁某截面配筋
        //nFloor           楼层号，从1开始
        //nTotID(in)       梁全楼编号
        //nSect(out)       截面数量
        //fpj(out)         返回配筋面积，第一维为截面编号，第二维分别为上截面纵筋、下截面纵筋、箍筋，第三维分别为配筋面积、计算配筋面积、配筋率，组合号
        //fnl(out)         返回设计内力，第一维为截面位置，第二维分别为上截面纵筋、下截面纵筋、箍筋，第三维分别为X弯矩，Y弯矩，X剪力，Y剪力，轴力，扭矩
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetSubBeamAsWithCal")]
        public static extern bool dsnGetSubBeamAsWithCal(int nFloor, int nTotID, ref int nSect, float[,,] fpj, float[,,] fnl);
        //----------------------------------------------------------------------
        //获得混凝土、型钢混凝土次梁某截面配筋率
        //nFloor           楼层号，从1开始
        //nTotID(in)       梁全楼编号
        //nSect(out)       截面数量
        //fpj(out)         返回配筋面积，第一维为截面编号，第二维分别为上截面纵筋、下截面纵筋、箍筋，第三维分别为配筋率，最小配筋率，最大配筋率
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetSubBeamPJRatio")]
        public static extern bool dsnGetSubBeamPJRatio(int nFloor, int nTotID, ref int nSect, float[,,] fpjr);
        //----------------------------------------------------------------------
        //获得混凝土次梁加密区、非加密区箍筋面积
        //nFloor           楼层号，从1开始
        //nTotID(in)       梁全楼编号
        //fHoopBarJM(out)  返回加密区箍筋面积
        //fHoopBar(out)    返回非加密区箍筋面积
        //fHoopBarJMRatio(out)  返回加密区箍筋面积
        //fHoopBarRatio(out)    返回非加密区箍筋面积
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetSubBeamAsVJM")]
        public static extern void dsnGetSubBeamAsVJM(int nFloor, int nTotID, ref float fHoopBarJM, ref float fHoopBar, ref float fHoopBarJMRatio, ref float fHoopBarRatio);
        //----------------------------------------------------------------------
        //获得混凝土次梁剪扭配筋
        //nFloor           楼层号，从1开始
        //nTotID(in)       梁全楼编号
        //nSect(out)       截面数量
        //fpj(out)         返回配筋面积，第一维为截面编号，第二维分别为受扭沿周边单肢箍筋面积、受扭纵筋面积、计算受扭纵筋面积
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetSubBeamAsTL")]
        public static extern void dsnGetSubBeamAsTL(int nFloor, int nTotID, ref int nSect, float[,] fpj);
        //----------------------------------------------------------------------
        //获得钢次梁应力验算结果
        //nFloor           楼层号，从1开始
        //nTotID(in)       梁全楼编号
        //nSect(out)       截面数量
        //fpj(out)         返回验算结果，第一维为截面编号，第二维分别为上截面强度、下截面强度、上截面稳定、下截面稳定、抗剪强度，第三维分别为计算应力、允许应力，组合号
        //fnl(out)         返回设计内力，第一维为截面位置，第二维分别为上截面强度、下截面强度、上截面稳定、下截面稳定、抗剪强度，第三维分别为X弯矩，Y弯矩，X剪力，Y剪力，轴力，扭矩
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetSteelSubBeamCheck")]
        public static extern void dsnGetSteelSubBeamCheck(int nFloor, int nTotID, ref int nSect, float[,,] fpj, float[,,] fnl);
        //----------------------------------------------------------------------
        //获得钢次梁截面验算结果
        //nFloor           楼层号，从1开始
        //nTotID(in)       梁全楼编号
        //BTRatio(out)     宽厚比
        //BTRatioMax(out)  宽厚比限值
        //HTRatio(out)     高厚比
        //HTRatioMax(out)  高厚比限值
        //fBTRatioReg(out)     外伸受压翼缘正则化宽厚比
        //fBTRatioRegMax(out)  外伸受压翼缘正则化宽厚比限值
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetSteelSubBeamSectCheck")]
        public static extern bool dsnGetSteelSubBeamSectCheck(int nFloor, int nTotID, ref float BTRatio, ref float BTRatioMax, ref float HTRatio, ref float HTRatioMax, ref float BTRatioReg, ref float BTRatioRegMax);
        //----------------------------------------------------------------------
        //获得型钢砼次梁截面验算结果
        //nFloor           楼层号，从1开始
        //nTotID(in)       梁全楼编号
        //BTRatio(out)     宽厚比
        //BTRatioMax(out)  宽厚比限值
        //HTRatio(out)     高厚比
        //HTRatioMax(out)  高厚比限值
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetSRCSubBeamSectCheck")]
        public static extern bool dsnGetSRCSubBeamSectCheck(int nFloor, int nTotID, ref float BTRatio, ref float BTRatioMax, ref float HTRatio, ref float HTRatioMax);
        //----------------------------------------------------------------------
        //是否按偏拉设计，仅针对砼构件有效
        //nFloor           楼层号
        //nTotID(in)       构件全楼编号
        //返回值            0-非偏拉，1-大偏拉，2-小偏拉
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnIsSubBeamDesignByPL")]
        public static extern int dsnIsSubBeamDesignByPL(int nFloor, int nTotID);
        //----------------------------------------------------------------------

        //////////////////////////////////////////////////////////////
        //空心板肋梁设计结果输出
        //////////////////////////////////////////////////////////////
        //获得空心板肋梁材料属性
        //nFloor           楼层号，从1开始
        //nTotID(in)       梁全楼编号
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetRibBeamMatKind")]
        public static extern int dsnGetRibBeamMatKind(int nFloor, int nTotID);
        //----------------------------------------------------------------------
        //获得空心板肋梁所属塔号
        //nFloor           楼层号，从1开始
        //nTotID(in)       梁全楼编号
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetRibBeamTow")]
        public static extern int dsnGetRibBeamTow(int nFloor, int nTotID);
        //----------------------------------------------------------------------
        //获得空心板肋梁标准内力
        //nFloor           楼层号，从1开始
        //nTotID(in)       梁全楼编号
        //nLDCase(in)      工况号
        //Option(in)       1-调整前，2-调整后
        //nSect(out)       截面数量
        //force(out)       返回内力，第一维为截面数量，第二维分别为：X弯矩，Y弯矩，X剪力，Y剪力，轴力，扭矩
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetRibBeamStdForce")]
        public static extern bool dsnGetRibBeamStdForce(int nFloor, int nTotID, int nLDCase, int Option, ref int nSect, float[,] Force);
        //----------------------------------------------------------------------
        //获得混凝土、型钢混凝土空心板肋梁某截面配筋
        //nFloor           楼层号，从1开始
        //nTotID(in)       梁全楼编号
        //nSect(out)       截面数量
        //fpj(out)         返回配筋面积，第一维为截面编号，第二维分别为上截面纵筋、下截面纵筋、箍筋，第三维分别为配筋面积、配筋率，组合号
        //fnl(out)         返回设计内力，第一维为截面位置，第二维分别为上截面纵筋、下截面纵筋、箍筋，第三维分别为X弯矩，Y弯矩，X剪力，Y剪力，轴力，扭矩
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetRibBeamAs")]
        public static extern void dsnGetRibBeamAs(int nFloor, int nTotID, ref int nSect, float[,,] fpj, float[,,] fnl);
        //----------------------------------------------------------------------
        //获得混凝土、型钢混凝土空心板肋梁某截面配筋
        //nFloor           楼层号，从1开始
        //nTotID(in)       梁全楼编号
        //nSect(out)       截面数量
        //fpj(out)         返回配筋面积，第一维为截面编号，第二维分别为上截面纵筋、下截面纵筋、箍筋，第三维分别为配筋面积、计算配筋面积、配筋率，组合号
        //fnl(out)         返回设计内力，第一维为截面位置，第二维分别为上截面纵筋、下截面纵筋、箍筋，第三维分别为X弯矩，Y弯矩，X剪力，Y剪力，轴力，扭矩
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetRibBeamAsWithCal")]
        public static extern bool dsnGetRibBeamAsWithCal(int nFloor, int nTotID, ref int nSect, float[,,] fpj, float[,,] fnl);
        //----------------------------------------------------------------------
        //获得混凝土、型钢混凝土空心板肋梁某截面配筋率
        //nFloor           楼层号，从1开始
        //nTotID(in)       梁全楼编号
        //nSect(out)       截面数量
        //fpj(out)         返回配筋面积，第一维为截面编号，第二维分别为上截面纵筋、下截面纵筋、箍筋，第三维分别为配筋率，最小配筋率，最大配筋率
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetRibBeamPJRatio")]
        public static extern bool dsnGetRibBeamPJRatio(int nFloor, int nTotID, ref int nSect, float[,,] fpjr);
        //----------------------------------------------------------------------
        //获得混凝土次梁加密区、非加密区箍筋面积
        //nFloor           楼层号，从1开始
        //nTotID(in)       梁全楼编号
        //fHoopBarJM(out)  返回加密区箍筋面积
        //fHoopBar(out)    返回非加密区箍筋面积
        //fHoopBarJMRatio(out)  返回加密区箍筋面积
        //fHoopBarRatio(out)    返回非加密区箍筋面积
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetRibBeamAsVJM")]
        public static extern void dsnGetRibBeamAsVJM(int nFloor, int nTotID, ref float fHoopBarJM, ref float fHoopBar, ref float fHoopBarJMRatio, ref float fHoopBarRatio);
        //----------------------------------------------------------------------
        //获得混凝土空心板肋梁剪扭配筋
        //nFloor           楼层号，从1开始
        //nTotID(in)       梁全楼编号
        //nSect(out)       截面数量
        //fpj(out)         返回配筋面积，第一维为截面编号，第二维分别为受扭沿周边单肢箍筋面积、受扭纵筋面积、计算受扭纵筋面积
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetRibBeamAsTL")]
        public static extern void dsnGetRibBeamAsTL(int nFloor, int nTotID, ref int nSect, float[,] fpj);
        //----------------------------------------------------------------------
        //是否按偏拉设计，仅针对砼构件有效
        //nFloor           楼层号
        //nTotID(in)       构件全楼编号
        //返回值            0-非偏拉，1-大偏拉，2-小偏拉
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnIsRibBeamDesignByPL")]
        public static extern int dsnIsRibBeamDesignByPL(int nFloor, int nTotID);
        //----------------------------------------------------------------------

        //////////////////////////////////////////////////////////////
        //地基梁设计结果输出
        //////////////////////////////////////////////////////////////
        //获得地基梁材料属性
        //nFloor           楼层号，从1开始
        //nTotID(in)       梁全楼编号
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetGradeBeamMatKind")]
        public static extern int dsnGetGradeBeamMatKind(int nFloor, int nTotID);
        //----------------------------------------------------------------------
        //获得地基梁所属塔号
        //nFloor           楼层号，从1开始
        //nTotID(in)       梁全楼编号
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetGradeBeamTow")]
        public static extern int dsnGetGradeBeamTow(int nFloor, int nTotID);
        //----------------------------------------------------------------------
        //获得地基梁标准内力
        //nFloor           楼层号，从1开始
        //nTotID(in)       梁全楼编号
        //nLDCase(in)      工况号
        //Option(in)       1-调整前，2-调整后
        //nSect(out)       截面数量
        //force(out)       返回内力，第一维为截面数量，第二维分别为：X弯矩，Y弯矩，X剪力，Y剪力，轴力，扭矩
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetGradeBeamStdForce")]
        public static extern bool dsnGetGradeBeamStdForce(int nFloor, int nTotID, int nLDCase, int Option, ref int nSect, float[,] Force);
        //----------------------------------------------------------------------
        //获得混凝土、型钢混凝土地基梁某截面配筋
        //nFloor           楼层号，从1开始
        //nTotID(in)       梁全楼编号
        //nSect(out)       截面数量
        //fpj(out)         返回配筋面积，第一维为截面编号，第二维分别为上截面纵筋、下截面纵筋、箍筋，第三维分别为配筋面积、配筋率，组合号
        //fnl(out)         返回设计内力，第一维为截面位置，第二维分别为上截面纵筋、下截面纵筋、箍筋，第三维分别为X弯矩，Y弯矩，X剪力，Y剪力，轴力，扭矩
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetGradeBeamAs")]
        public static extern void dsnGetGradeBeamAs(int nFloor, int nTotID, ref int nSect, float[,,] fpj, float[,,] fnl);
        //----------------------------------------------------------------------
        //获得混凝土、型钢混凝土地基梁某截面配筋率
        //nFloor           楼层号，从1开始
        //nTotID(in)       梁全楼编号
        //nSect(out)       截面数量
        //fpj(out)         返回配筋面积，第一维为截面编号，第二维分别为上截面纵筋、下截面纵筋、箍筋，第三维分别为配筋率，最小配筋率，最大配筋率
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetGradeBeamPJRatio")]
        public static extern bool dsnGetGradeBeamPJRatio(int nFloor, int nTotID, ref int nSect, float[,,] fpjr);
        //----------------------------------------------------------------------
        //获得地基梁加密区、非加密区箍筋面积
        //nFloor           楼层号，从1开始
        //nTotID(in)       梁全楼编号
        //fHoopBarJM(out)  返回加密区箍筋面积
        //fHoopBar(out)    返回非加密区箍筋面积
        //fHoopBarJMRatio(out)  返回加密区箍筋面积
        //fHoopBarRatio(out)    返回非加密区箍筋面积
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetGradeBeamAsVJM")]
        public static extern void dsnGetGradeBeamAsVJM(int nFloor, int nTotID, ref float fHoopBarJM, ref float fHoopBar, ref float fHoopBarJMRatio, ref float fHoopBarRatio);
        //----------------------------------------------------------------------
        //获得地基梁剪扭配筋
        //nFloor           楼层号，从1开始
        //nTotID(in)       梁全楼编号
        //nSect(out)       截面数量
        //fpj(out)         返回配筋面积，第一维为截面编号，第二维分别为受扭沿周边单肢箍筋面积、受扭纵筋面积、计算受扭纵筋面积
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetGradeBeamAsTL")]
        public static extern void dsnGetGradeBeamAsTL(int nFloor, int nTotID, ref int nSect, float[,] fpj);
        //----------------------------------------------------------------------
        //是否按偏拉设计，仅针对砼构件有效
        //nFloor           楼层号
        //nTotID(in)       构件全楼编号
        //返回值            0-非偏拉，1-大偏拉，2-小偏拉
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnIsGradeBeamDesignByPL")]
        public static extern int dsnIsGradeBeamDesignByPL(int nFloor, int nTotID);
        //----------------------------------------------------------------------
        //获得地基梁实际对应的楼层号，目前地基梁记录在第一层，因此第一层返回值为0
        //nFloor           楼层号，从1开始
        //nTotID(in)       梁全楼编号
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetGradeBeamPJFloor")]
        public static extern int dsnGetGradeBeamPJFloor(int nFloor);
        //----------------------------------------------------------------------

        //////////////////////////////////////////////////////////////
        //框架柱设计结果输出
        //////////////////////////////////////////////////////////////
        //获得柱属性
        //nFloor           楼层号，从1开始
        //nTotID(in)       柱全楼编号
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetColumnKind")]
        public static extern int dsnGetColumnKind(int nFloor, int nTotID);
        //----------------------------------------------------------------------
        //获得柱材料属性
        //nFloor           楼层号，从1开始
        //nTotID(in)       柱全楼编号
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetColumnMatKind")]
        public static extern int dsnGetColumnMatKind(int nFloor, int nTotID);
        //----------------------------------------------------------------------
        //获得柱标准内力
        //nFloor           楼层号，从1开始
        //nTotID(in)       柱全楼编号
        //nLDCase(in)      工况号
        //Option(in)       1-调整前，2-调整后
        //nSect(out)       截面数量
        //force(out)       返回内力，第一维为截面数量，第二维分别为：X弯矩，Y弯矩，X剪力，Y剪力，轴力，扭矩
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetColumnStdForce")]
        public static extern  bool dsnGetColumnStdForce(int nFloor, int nTotID, int nLDCase, int Option, ref int nSect, float[,] Force);


        //----------------------------------------------------------------------
        //获得混凝土柱配筋计算方法，采用dy的宏定义
        //nFloor           楼层号
        //nTotID(in)       柱全楼编号
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetColumnDesignMethod")]
        public static extern int dsnGetColumnDesignMethod(int nFloor, int nTotID);
        //----------------------------------------------------------------------
        //获得混凝土、型钢混凝土柱某截面配筋
        //nFloor           楼层号，从1开始
        //nTotID(in)       柱全楼编号
        //nSect(out)       截面数量
        //Asc(out)         返回角筋面积，对纵筋有效
        //fpj(out)         返回设计内力，第一维为截面位置（上、下），
        //                 第二维分别为X纵筋（包含角筋，对于双偏压配筋时为固定钢筋面积）、Y纵筋（包含角筋，对于双偏压配筋时为分布钢筋面积）、X箍筋、Y箍筋，
        //                 第三维分别为配筋面积、计算配筋面积、组合号
        //fnl(out)         返回设计内力，第一维为截面位置（上、下），第二维分别为X纵筋、Y纵筋、X箍筋、Y箍筋，第三维分别为X弯矩，Y弯矩，X剪力，Y剪力，轴力，扭矩
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetColumnAs")]
        public static extern void dsnGetColumnAs(int nFloor, int nTotID, ref int nSect, ref float Asc, float[,,] fpj, float[,,] fnl);
        //----------------------------------------------------------------------
        //获得混凝土柱双偏压配筋结果
        //nFloor           楼层号，从1开始
        //nTotID(in)       柱全楼编号
        //nPos(in)         截面位置，1-上，2-下
        //DiaAsc(out)      返回角筋直径
        //DiaAsB(out)      返回B边钢筋直径
        //nBarB(out)       返回B边钢筋根数（不包含角筋）
        //DiaAsH(out)      返回H边钢筋直径
        //nBarH(out)       返回H边钢筋根数（不包含角筋）
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetColumnBiAxisAs")]
        public static extern void dsnGetColumnBiAxisAs(int nFloor, int nTotID, int nPos, ref float DiaAsc, ref float DiaAsB, ref int nBarB, ref float DiaAsH, ref int nBarH);
        //----------------------------------------------------------------------
        //获得混凝土、型钢混凝土柱某截面配筋率
        //nFloor           楼层号，从1开始
        //nTotID(in)       柱全楼编号
        //nBarKind(in)     配筋种类，1-全截面纵筋，2-箍筋
        //AsRatio(out)     返回配筋率，箍筋为体积配箍率
        //AsRatioMin(out)  返回最小配筋率，箍筋为最小体积配箍率
        //AsRatioMax(out)  返回最大配筋率，箍筋为最小体积配箍率
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetColumnAsRatio")]
        public static extern void dsnGetColumnAsRatio(int nFloor, int nTotID, int nBarKind, ref float AsRatio, ref float AsRatioMin, ref float AsRatioMax);
        //----------------------------------------------------------------------
        //获得混凝土、型钢混凝土柱某纵筋单边配筋率
        //nFloor           楼层号，从1开始
        //nTotID(in)       柱全楼编号
        //SideAsRatioB(out)返回B边单边配筋率
        //SideAsRatioH(out)返回H边单边配筋率
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetColumnSideAsRatio")]
        public static extern bool dsnGetColumnSideAsRatio(int nFloor, int nTotID, ref float SideAsRatioB, ref float SideAsRatioH);
        //----------------------------------------------------------------------
        //获得混凝土、型钢混凝土柱轴压比
        //nFloor           楼层号，从1开始
        //nTotID(in)       柱全楼编号
        //fZYB(out)        返回轴压比
        //fZYBMax(out)     返回轴压比限值
        //fZYBAxis(out)    返回轴压比对应的轴力设计值
        //nZYBLDCombID(out)返回轴压比对应的组合号
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetColumnZYB")]
        public static extern void dsnGetColumnZYB(int nFloor, int nTotID, ref float fZYB, ref float fZYBMax, ref float fZYBAxis, ref int nZYBLDCombID);

        //=====================================liu=============================
        //----------------------------------------------------------------------
        //获得混凝土、型钢混凝土柱组合轴压比
        //nFloor           楼层号，从1开始
        //nTotID(in)       柱全楼编号
        //fZYB_ZH(out)     返回组合轴压比
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetColumnZYB_ZH")]
        public static extern bool dsnGetColumnZYB_ZH(int nFloor, int nTotID, ref float fZYB_ZH);


        //----------------------------------------------------------------------
        //获得混凝土、型钢混凝土柱剪跨比
        //nFloor           楼层号，从1开始
        //nTotID(in)       柱全楼编号
        //fJKB(out)        返回剪跨比
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetColumnJKB")]
        public static extern bool dsnGetColumnJKB(int nFloor, int nTotID, ref float fJKB);

        //----------------------------------------------------------------------
        //获得混凝土、型钢混凝土柱在重力荷载代表值下的轴力
        //nFloor           楼层号，从1开始
        //nTotID(in)       柱全楼编号
        //fZYBAxis(out)    返回轴压比对应的轴力设计值
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetColumnAxis_Gravity")]
        public static extern float dsnGetColumnAxis_Gravity(int nFloor, int nTotID);

        //----------------------------------------------------------------------
        //获得混凝土、型钢混凝土柱节点核芯区配筋面积
        //nFloor           楼层号，从1开始
        //nTotID(in)       柱全楼编号
        //fAsRatio(out)    返回体积配箍率
        //fpj(out)         返回设计内力，第一维为X、Y方向，第二维为配筋面积、计算配筋面积、组合号
        //fnl(out)         返回设计内力，第一维为X、Y方向，第二维分别为X弯矩，Y弯矩，X剪力，Y剪力，轴力，扭矩
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetColumnJointAs")]
        public static extern void dsnGetColumnJointAs(int nFloor, int nTotID, ref float fAsRatio, float[,] fpj, float[,] fnl);

        //----------------------------------------------------------------------
        //获得混凝土、型钢混凝土柱柱帽配筋面积
        //nFloor           楼层号，从1开始
        //nTotID(in)       柱全楼编号
        //fpj(out)         返回设计内力，第一维为柱根、柱帽、托板，第二维为配筋面积、计算配筋面积、组合号
        //fnl(out)         返回设计内力，第一维为柱根、柱帽、托板，第二维分别为X弯矩，Y弯矩，X剪力，Y剪力，轴力，扭矩
        //fRatio(out)      返回承载力之比，第一维为柱根、柱帽、托板
        //bNeedPunchAs(out)  返回是否需配筋抗冲切钢筋
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetColumnCapAs")]
        public static extern bool dsnGetColumnCapAs(int nFloor, int nTotID, float[,] fpj, float[,] fnl, float[] fRatio, ref bool bDoCheckJYBWithAs);

        //----------------------------------------------------------------------
        //nHasAs           是否需要配筋，1-需要，0-不需要
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetColumnCapAsBase")]
        public static extern bool dsnGetColumnCapAsBase(int nFloor, int nTotID, float[,] fpj, float[,] fnl, float[] fRatio, int[] nHasAs);

        //----------------------------------------------------------------------
        //获得钢柱应力验算结果
        //nFloor           楼层号
        //nTotID(in)       柱全楼编号
        //nSect(out)       截面数量
        //fpj(out)         返回验算结果，第一维为截面编号，第二维分别为强度、X向稳定、Y向稳定，第三维分别为计算应力、允许应力，组合号
        //fnl(out)         返回设计内力，第一维为截面位置，第二维分别为强度、X向稳定、Y向稳定，第三维分别为X弯矩，Y弯矩，X剪力，Y剪力，轴力，扭矩
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetSteelColumnCheck")]
        public static extern void dsnGetSteelColumnCheck(int nFloor, int nTotID, ref int nSect, float[,,] fpj, float[,,] fnl);

        //fpj(out)         返回验算结果，第一维为截面编号，第二维分别为强度、X向稳定、Y向稳定、X向抗剪、Y向抗剪，第三维分别为计算应力、允许应力，组合号
        //fnl(out)         返回设计内力，第一维为截面位置，第二维分别为强度、X向稳定、Y向稳定、X向抗剪、Y向抗剪，第三维分别为X弯矩，Y弯矩，X剪力，Y剪力，轴力，扭矩
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetSteelColumnCheckNew")]
        public static extern void dsnGetSteelColumnCheckNew(int nFloor, int nTotID, ref int nSect, float[,,] fpj, float[,,] fnl);

        //----------------------------------------------------------------------
        //获得钢柱截面验算结果
        //nFloor           楼层号，从1开始
        //nTotID(in)       柱全楼编号
        //RmdX(out)        X向长细比
        //RmdY(out)        Y向长细比
        //RmdMax(out)      允许长细比
        //BTRatio(out)     宽厚比
        //BTRatioMax(out)  宽厚比限值
        //HTRatio(out)     高厚比
        //HTRatioMax(out)  高厚比限值
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetSteelColumnSectCheck")]
        public static extern bool dsnGetSteelColumnSectCheck(int nFloor, int nTotID, ref float RmdX, ref float RmdY, ref float RmdMax, ref float BTRatio, ref float BTRatioMax, ref float HTRatio, ref float HTRatioMax);
        //----------------------------------------------------------------------
        //获得钢柱防火应力验算结果
        //nFloor           楼层号
        //nTotID(in)       柱全楼编号
        //nSect(out)       截面数量
        //fpj(out)         返回验算结果，第一维为截面编号，第二维分别为强度、X向稳定、Y向稳定，第三维分别为计算应力、允许应力，组合号
        //fnl(out)         返回设计内力，第一维为截面位置，第二维分别为强度、X向稳定、Y向稳定，第三维分别为X弯矩，Y弯矩，X剪力，Y剪力，轴力，扭矩
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetSteelColumnCheck_FH")]
        public static extern void dsnGetSteelColumnCheck_FH(int nFloor, int nTotID, ref int nSect, float[,,] fpj, float[,,] fnl);

        //----------------------------------------------------------------------//获得型钢砼柱截面验算结果
        //nFloor           楼层号，从1开始
        //nTotID(in)       柱全楼编号
        //RmdX(out)        X向长细比
        //RmdY(out)        Y向长细比
        //RmdMax(out)      允许长细比
        //BTRatio(out)     宽厚比
        //BTRatioMax(out)  宽厚比限值
        //HTRatio(out)     高厚比
        //HTRatioMax(out)  高厚比限值
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetSRCColumnSectCheck")]
        public static extern bool dsnGetSRCColumnSectCheck(int nFloor, int nTotID, ref float RmdX, ref float RmdY, ref float RmdMax, ref float BTRatio, ref float BTRatioMax, ref float HTRatio, ref float HTRatioMax);
        //----------------------------------------------------------------------
        //获得方钢管混凝土柱应力验算结果
        //nFloor           楼层号
        //nTotID(in)       柱全楼编号
        //nSect(out)       截面数量
        //fpj(out)         返回验算结果，第一维为截面编号，第二维分别为强度、X向稳定、Y向稳定、X向抗剪、Y向抗剪，第三维分别为计算应力、允许应力，组合号
        //fnl(out)         返回设计内力，第一维为截面位置，第二维分别为强度、X向稳定、Y向稳定、X向抗剪、Y向抗剪，第三维分别为X弯矩，Y弯矩，X剪力，Y剪力，轴力，扭矩
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetRectTubeColumnCheck")]
        public static extern void dsnGetRectTubeColumnCheck(int nFloor, int nTotID, ref int nSect, float[,,] fpj, float[,,] fnl);

        //----------------------------------------------------------------------
        //获得方钢管柱截面验算结果
        //nFloor           楼层号，从1开始
        //nTotID(in)       柱全楼编号
        //RmdX(out)        X向长细比
        //RmdY(out)        Y向长细比
        //RmdMax(out)      允许长细比
        //BTRatio(out)     宽厚比
        //BTRatioMax(out)  宽厚比限值
        //HTRatio(out)     高厚比
        //HTRatioMax(out)  高厚比限值
        //ALFAC(out)       混凝土工作承担系数
        //ALFACMax(out)    混凝土工作承担系数限值
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetRectTubeColumnSectCheck")]
        public static extern bool dsnGetRectTubeColumnSectCheck(int nFloor, int nTotID, ref float RmdX, ref float RmdY, ref float RmdMax, ref float BTRatio, ref float BTRatioMax, ref float HTRatio, ref float HTRatioMax, ref float ALFAC, ref float ALFACMax);
        //----------------------------------------------------------------------
        //获得中建科工异形柱应力验算结果
        //nFloor           楼层号
        //nTotID(in)       柱全楼编号
        //nSect(out)       截面数量
        //fpj(out)         返回验算结果，第一维为截面编号，第二维分别为强度、X向稳定、Y向稳定、X向抗剪、Y向抗剪，第三维分别为计算应力、允许应力，组合号
        //fnl(out)         返回设计内力，第一维为截面位置，第二维分别为强度、X向稳定、Y向稳定、X向抗剪、Y向抗剪，第三维分别为X弯矩，Y弯矩，X剪力，Y剪力，轴力，扭矩
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetAMCSColumnCheck")]
        public static extern void dsnGetAMCSColumnCheck(int nFloor, int nTotID, ref int nSect, float[,,] fpj, float[,,] fnl);


        //----------------------------------------------------------------------
        //获得中建科工异形柱截面验算结果
        //nFloor           楼层号，从1开始
        //nTotID(in)       柱全楼编号
        //RmdX(out)        X向长细比
        //RmdY(out)        Y向长细比
        //RmdMax(out)      允许长细比
        //BTRatio(out)     宽厚比
        //BTRatioMax(out)  宽厚比限值
        //HTRatio(out)     高厚比
        //HTRatioMax(out)  高厚比限值
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetAMCSColumnSectCheck")]
        public static extern bool dsnGetAMCSColumnSectCheck(int nFloor, int nTotID, ref float RmdX, ref float RmdY, ref float RmdMax, ref float BTRatio, ref float BTRatioMax, ref float HTRatio, ref float HTRatioMax);
        //----------------------------------------------------------------------
        //获得甲壳柱应力验算结果
        //nFloor           楼层号
        //nTotID(in)       柱全楼编号
        //nSect(out)       截面数量
        //fpj(out)         返回验算结果，第一维为截面编号，第二维分别为强度、X向稳定、Y向稳定、X向抗剪、Y向抗剪，第三维分别为计算应力、允许应力，组合号
        //fnl(out)         返回设计内力，第一维为截面位置，第二维分别为强度、X向稳定、Y向稳定、X向抗剪、Y向抗剪，第三维分别为X弯矩，Y弯矩，X剪力，Y剪力，轴力，扭矩
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetURCBColumnCheck")]
        public static extern void dsnGetURCBColumnCheck(int nFloor, int nTotID, ref int nSect, float[,,] fpj, float[,,] fnl);
        //----------------------------------------------------------------------
        //获得方钢管混凝土柱应力验算结果
        //nFloor           楼层号
        //nTotID(in)       柱全楼编号
        //nSect(out)       截面数量
        //fpj(out)         返回验算结果，第一维为截面编号，第二维分别为荷载比、承载力系数、所需保护层厚度、已有保护层厚度、组合号
        //fnl(out)         返回设计内力，第一维为截面位置，第二维分别为X弯矩，Y弯矩，X剪力，Y剪力，轴力，扭矩
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetRectTubeColumnCheck_FH")]
        public static extern void dsnGetRectTubeColumnCheck_FH(int nFloor, int nTotID, ref int nSect, float[,] fpj, float[,] fnl);
        //----------------------------------------------------------------------
        //获得圆钢管混凝土柱应力验算结果
        //nFloor           楼层号
        //nTotID(in)       柱全楼编号
        //nSect(out)       截面数量
        //fpj(out)         返回验算结果，第一维为截面编号，第二维分别为轴压强度、拉弯强度、抗剪强度，第三维分别为计算应力、允许应力，组合号
        //fnl(out)         返回设计内力，第一维为截面位置，第二维分别为轴压强度、拉弯强度、抗剪强度，第三维分别为X弯矩，Y弯矩，X剪力，Y剪力，轴力，扭矩
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetCircleTubeColumnCheck")]
        public static extern void dsnGetCircleTubeColumnCheck(int nFloor, int nTotID, ref int nSect, float[,,] fpj, float[,] fnl);
        //----------------------------------------------------------------------
        //获得圆钢管柱截面验算结果
        //nFloor           楼层号，从1开始
        //nTotID(in)       柱全楼编号
        //RmdX(out)        X向长细比
        //RmdY(out)        Y向长细比
        //RmdMax(out)      允许长细比
        //SITA(out)        套箍指标
        //SITAMin(out)     套箍指标下限值
        //SITAMax(out)     套箍指标上限值
        //DTRatio(out)     径厚比
        //DTRatioMax(out)  径厚比限值
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetCircleTubeColumnSectCheck")]
        public static extern bool dsnGetCircleTubeColumnSectCheck(int nFloor, int nTotID, ref float RmdX, ref float RmdY, ref float RmdMax, ref float SITA, ref float SITAMin, ref float SITAMax, ref float DTRatio, ref float DTRatioMax);
        //----------------------------------------------------------------------
        //获得圆钢管混凝土柱应力验算结果
        //nFloor           楼层号
        //nTotID(in)       柱全楼编号
        //nSect(out)       截面数量
        //fpj(out)         返回验算结果，第一维为截面编号，第二维分别为荷载比、承载力系数、所需保护层厚度、已有保护层厚度、组合号
        //fnl(out)         返回设计内力，第一维为截面位置，第二维分别为X弯矩，Y弯矩，X剪力，Y剪力，轴力，扭矩
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetCircleTubeColumnCheck_FH")]
        public static extern void dsnGetCircleTubeColumnCheck_FH(int nFloor, int nTotID, ref int nSect, float[,] fpj, float[,] fnl);
        //----------------------------------------------------------------------
        //获得叠合柱截面验算结果
        //nFloor           楼层号，从1开始
        //nTotID(in)       柱全楼编号
        //RmdX(out)        X向长细比
        //RmdY(out)        Y向长细比
        //RmdMax(out)      允许长细比
        //SITA(out)        套箍指标
        //SITAMin(out)     套箍指标下限值
        //SITAMax(out)     套箍指标上限值
        //DTRatio(out)     径厚比
        //DTRatioMax(out)  径厚比限值
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetTubeReinColumnSectCheck")]
        public static extern bool dsnGetTubeReinColumnSectCheck(int nFloor, int nTotID, ref float RmdX, ref float RmdY, ref float RmdMax, ref float SITA, ref float SITAMin, ref float SITAMax, ref float DTRatio, ref float DTRatioMax);
        //----------------------------------------------------------------------
        //获得钢柱、矩形钢管砼柱节点核芯区验算结果
        //nFloor           楼层号，从1开始
        //nTotID(in)       柱全楼编号
        //fJointStrongCoe(out) 强节点系数
        //fpj(out)         返回设计内力，第一维为X、Y方向，第二维为比值、组合号
        //fnl(out)         返回设计内力，第一维为X、Y方向，第二维分别为X弯矩，Y弯矩，X剪力，Y剪力，轴力，扭矩
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetColumnJointCheck")]
        public static extern bool dsnGetColumnJointCheck(int nFloor, int nTotID, ref float fJointStrongCoe, float[,] fpj, float[,] fnl);
        //----------------------------------------------------------------------
        //判断该柱设计时是否做为墙翼缘，0-不作为翼缘，1-只与单方向墙，2-与多方向墙相连
        //nFloor           楼层号，从1开始
        //nTotID(in)       柱全楼编号
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetColumnDesignWithWallColSign")]
        public static extern int dsnGetColumnDesignWithWallColSign(int nFloor, int nTotID);
        //----------------------------------------------------------------------
        //判断该柱是否是异形柱
        //nFloor           楼层号，从1开始
        //nTotID(in)       柱全楼编号
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnColIsYXZ")]
        public static extern bool dsnColIsYXZ(int nFloor, int nTotID);
        //----------------------------------------------------------------------
        //判断该柱是否是短柱
        //nFloor           楼层号，从1开始
        //nTotID(in)       柱全楼编号
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnColIsShort")]
        public static extern bool dsnColIsShort(int nFloor, int nTotID);
        //----------------------------------------------------------------------
        //获得该柱长度、长度系数
        //nFloor           楼层号，从1开始
        //nTotID(in)       柱全楼编号
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetColLenCoe")]
        public static extern void dsnGetColLenCoe(int nFloor, int nTotID, ref float fLenX, ref float fLenY, ref float fLenXCoe, ref float fLenYCoe);
        //----------------------------------------------------------------------
        //获得柱受剪承载力
        //nFloor           楼层号，从1开始
        //nTotID(in)       柱全楼编号
        //fSCX(out)        返回整体坐标系下X向受剪承载力
        //fSCY(out)        返回整体坐标系下Y向受剪承载力
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetColumnShearCapacity")]
        public static extern bool dsnGetColumnShearCapacity(int nFloor, int nTotID, ref float fSCX, ref float fSCY);
        //----------------------------------------------------------------------
        //获得鉴定加固用已有钢筋数据
        //nFloor           楼层号
        //nTotID(in)       构件全楼编号
        //nCurSect(in)     截面位置
        //nMBarKindNumB(out)    返回B边钢筋种类
        //MBarNumB(out)         返回B边钢筋每种钢筋数量
        //fMBarDiaB(out)        返回B边钢筋每种钢筋直径(mm)
        //nMBarKindNumH(out)    返回H边钢筋种类
        //MBarNumH(out)         返回H边钢筋每种钢筋数量
        //fMBarDiaH(out)        返回H边钢筋每种钢筋直径(mm)
        //fMBarDiaC(out)        返回角筋直径(mm)
        //nHBarJMNumX(out)      返回X向加密区箍筋根数
        //fHBarJMDiaX(out)      返回X向加密区箍筋直径(mm)
        //nHBarJMNumY(out)      返回Y向加密区箍筋根数
        //fHBarJMDiaY(out)      返回Y向加密区箍筋直径(mm)
        //fHBarJMSpace(out)     返回加密区箍筋间距(mm)
        //nHBarNumX(out)        返回X向非加密区箍筋根数
        //fHBarDiaX(out)        返回X向非加密区箍筋直径(mm)
        //nHBarNumY(out)        返回Y向非加密区箍筋根数
        //fHBarDiaY(out)        返回Y向非加密区箍筋直径(mm)
        //fHBarSpace(out)       返回非加密区箍筋间距(mm)
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetColJDJGExistGJ")]
        public static extern bool dsnGetColJDJGExistGJ(int nFloor, int nTotID, int nCurSect, ref int nMBarKindNumB, int[] MBarNumB, float[] fMBarDiaB,
                                              ref int nMBarKindNumH, int[] MBarNumH, float[] fMBarDiaH, ref float fMBarDiaC,
                                              ref int nHBarJMNumX, ref float fHBarJMDiaX, ref int nHBarJMNumY, ref float fHBarJMDiaY, ref float fHBarJMSpace,
                                              ref int nHBarNumX, ref float fHBarDiaX, ref int nHBarNumY, ref float fHBarDiaY, ref float fHBarSpace);
        //----------------------------------------------------------------------
        //获得混凝土、型钢混凝土柱某截面配筋
        //nFloor           楼层号，从1开始
        //nTotID(in)       柱全楼编号
        //nSect(out)       截面数量
        //Asc(out)         返回角筋面积，对纵筋有效
        //fpj(out)         返回设计内力，第一维为截面位置（上、下），
        //                 第二维分别为X纵筋、Y纵筋、X箍筋、Y箍筋，
        //                 第三维分别为计算与构造面积大值、计算面积、定义面积、组合号
        //fnl(out)         返回设计内力，第一维为截面位置（上、下），第二维分别为X纵筋、Y纵筋、X箍筋、Y箍筋，第三维分别为X弯矩，Y弯矩，X剪力，Y剪力，轴力，扭矩
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetColumnJDJGArea")]
        public static extern bool dsnGetColumnJDJGArea(int nFloor, int nTotID, ref int nSect, ref float Asc, float[,,] fpj, float[,,] fnl);
        //----------------------------------------------------------------------
        //获得装配式中预制柱抗剪验算所需钢筋面积
        //nFloor           楼层号，从1开始
        //nTotID(in)       柱全楼编号
        //fAs(out)         返回所需钢筋面积(mm2)
        //nLDCombID(out)   返回对应组合号
        //fnl(out)         返回的设计内力，分别为 X弯矩、 Y弯矩、 X剪力、 Y剪力、 轴力、 扭矩
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetPcColShearCheck")]
        public static extern bool dsnGetPcColShearCheck(int nFloor, int nTotID, ref float fAs, ref int nLDCombID, float[] fnl);
        ////----------------------------------------------------------------------
        ////获得柱建模编号对应计算模型编号索引map
        ////nFloor           楼层号，从1开始
        ////pPMIDToTotIDMap(out)  柱建模序号对应计算模型全楼编号
        ////pTotIDToPMIDMap(out)  柱计算模型全楼编号对应建模序号
        //[DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetColumnPMIDToTotIDMap")]
        //public static extern void dsnGetColumnPMIDToTotIDMap(int nFloor, CIntIntMap* pPMIDToTotIDMap, CIntIntMap* pTotIDToPMIDMap);
        //----------------------------------------------------------------------

        //////////////////////////////////////////////////////////////
        //主柱设计结果输出
        //////////////////////////////////////////////////////////////
        //获得主柱数量
        //nFloor           楼层号，从1开始
        //nMainColNum(out) 柱段数量
        //nMainColID(out)  柱段编号数组
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetMainColNum")]
        public static extern void dsnGetMainColNum(int nFloor, ref int nMainColNum, int[] nMainColID);
        //----------------------------------------------------------------------
        //获得某主柱包含的柱段编号，从下到上
        //nFloor           楼层号，从1开始
        //ID(in)           主柱编号
        //ColSegNum(out)   柱段数量
        //ColSegID(out)    柱段全楼编号数组
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetColSegIDbyMainCol")]
        public static extern void dsnGetColSegIDbyMainCol(int nFloor, int ID, ref int ColSegNum, int[] ColSegID);
        //----------------------------------------------------------------------

        //////////////////////////////////////////////////////////////
        //支撑设计结果输出
        //////////////////////////////////////////////////////////////
        //获得支撑属性
        //nFloor           楼层号，从1开始
        //nTotID(in)       支撑全楼编号
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetBraceColKind")]
        public static extern int dsnGetBraceColKind(int nFloor, int nTotID);
        //----------------------------------------------------------------------
        //获得支撑类别
        //nFloor           楼层号，从1开始
        //nTotID(in)       支撑全楼编号
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetBraceKind")]
        public static extern int dsnGetBraceKind(int nFloor, int nTotID);
        //----------------------------------------------------------------------
        //获得支撑材料属性
        //nFloor           楼层号，从1开始
        //nTotID(in)       支撑全楼编号
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetBraceMatKind")]
        public static extern int dsnGetBraceMatKind(int nFloor, int nTotID);
        //----------------------------------------------------------------------
        //获得支撑标准内力
        //nFloor           楼层号，从1开始
        //nTotID(in)       支撑全楼编号
        //nLDCase(in)      工况号
        //Option(in)       1-调整前，2-调整后
        //nSect(out)       截面数量
        //force(out)       返回内力，第一维为截面数量，第二维分别为：X弯矩，Y弯矩，X剪力，Y剪力，轴力，扭矩
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetBraceStdForce")]
        public static extern bool dsnGetBraceStdForce(int nFloor, int nTotID, int nLDCase, int Option, ref int nSect, float[,] Force);
        //----------------------------------------------------------------------
        //获得混凝土支撑配筋计算方法，采用dy的宏定义
        //nFloor           楼层号，从1开始
        //nTotID(in)       支撑全楼编号
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetBraceDesignMethod")]
        public static extern int dsnGetBraceDesignMethod(int nFloor, int nTotID);
        //----------------------------------------------------------------------
        //获得混凝土、型钢混凝土支撑某截面配筋
        //nFloor           楼层号，从1开始
        //nTotID(in)       支撑全楼编号
        //nSect(out)       截面数量
        //Asc(out)         返回角筋面积，对纵筋有效
        //fpj(out)         返回设计内力，第一维为截面位置（上、下），
        //                 第二维分别为X纵筋（包含角筋，对于双偏压配筋时为固定钢筋面积）、Y纵筋（包含角筋，对于双偏压配筋时为分布钢筋面积）、X箍筋、Y箍筋，
        //                 第三维分别为配筋面积、计算配筋面积、组合号
        //fnl(out)         返回设计内力，第一维为截面位置（上、下），第二维分别为X纵筋、Y纵筋、X箍筋、Y箍筋，第三维分别为X弯矩，Y弯矩，X剪力，Y剪力，轴力，扭矩
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetBraceAs")]
        public static extern void dsnGetBraceAs(int nFloor, int nTotID, ref int nSect, ref float Asc, float[,,] fpj, float[,,] fnl);
        //----------------------------------------------------------------------
        //获得混凝土支撑双偏压配筋结果
        //nFloor           楼层号，从1开始
        //nTotID(in)       支撑全楼编号
        //nPos(in)         截面位置，1-上，2-下
        //DiaAsc(out)      返回角筋直径
        //DiaAsB(out)      返回B边钢筋直径
        //nBarB(out)       返回B边钢筋根数（不包含角筋）
        //DiaAsH(out)      返回H边钢筋直径
        //nBarH(out)       返回H边钢筋根数（不包含角筋）
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetBraceBiAxisAs")]
        public static extern void dsnGetBraceBiAxisAs(int nFloor, int nTotID, int nPos, ref float DiaAsc, ref float DiaAsB, ref int nBarB, ref float DiaAsH, ref int nBarH);
        //----------------------------------------------------------------------
        //获得混凝土、型钢混凝土支撑某截面配筋率
        //nFloor           楼层号，从1开始
        //nTotID(in)       支撑全楼编号
        //nBarKind(in)     配筋种类，1-全截面纵筋，2-箍筋
        //AsRatio(out)     返回配筋率，箍筋为体积配箍率
        //AsRatioMin(out)  返回最小配筋率，箍筋为最小体积配箍率
        //AsRatioMax(out)  返回最大配筋率，箍筋为最小体积配箍率
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetBraceAsRatio")]
        public static extern void dsnGetBraceAsRatio(int nFloor, int nTotID, int nBarKind, ref float AsRatio, ref float AsRatioMin, ref float AsRatioMax);
        //----------------------------------------------------------------------
        //获得混凝土、型钢混凝土支撑轴压比
        //nFloor           楼层号，从1开始
        //nTotID(in)       支撑全楼编号
        //fZYB(out)        返回轴压比
        //fZYBMax(out)     返回轴压比限值
        //fZYBAxis(out)    返回轴压比对应的轴力设计值
        //nZYBLDCombID(out)返回最大配筋率，箍筋为最小体积配箍率
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetBraceZYB")]
        public static extern void dsnGetBraceZYB(int nFloor, int nTotID, ref float fZYB, ref float fZYBMax, ref float fZYBAxis, ref int nZYBLDCombID);
        //----------------------------------------------------------------------
        //获得混凝土、型钢混凝土支撑组合轴压比
        //nFloor           楼层号，从1开始
        //nTotID(in)       支撑全楼编号
        //fZYB_ZH(out)     返回组合轴压比
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetBraceZYB_ZH")]
        public static extern bool dsnGetBraceZYB_ZH(int nFloor, int nTotID, ref float fZYB_ZH);
        //----------------------------------------------------------------------
        //获得混凝土、型钢混凝土支撑剪跨比
        //nFloor           楼层号，从1开始
        //nTotID(in)       柱全楼编号
        //fJKB(out)        返回剪跨比
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetBraceJKB")]
        public static extern bool dsnGetBraceJKB(int nFloor, int nTotID, ref float fJKB);
        //----------------------------------------------------------------------
        //获得混凝土、型钢混凝土支撑节点核芯区配筋面积
        //nFloor           楼层号，从1开始
        //nTotID(in)       支撑全楼编号
        //fAsRatio(out)    返回体积配箍率
        //fpj(out)         返回设计内力，第一维为X、Y方向，第二维为配筋面积、计算配筋面积、组合号
        //fnl(out)         返回设计内力，第一维为X、Y方向，第二维分别为X弯矩，Y弯矩，X剪力，Y剪力，轴力，扭矩
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetBraceJointAs")]
        public static extern void dsnGetBraceJointAs(int nFloor, int nTotID, ref float fAsRatio, float[,] fpj, float[,] fnl);
        //----------------------------------------------------------------------
        //获得钢支撑应力验算结果
        //nFloor           楼层号，从1开始
        //nTotID(in)       支撑全楼编号
        //nSect(out)       截面数量
        //fpj(out)         返回验算结果，第一维为截面编号，第二维分别为强度、X向稳定、Y向稳定，第三维分别为计算应力、允许应力，组合号
        //fnl(out)         返回设计内力，第一维为截面位置，第二维分别为强度、X向稳定、Y向稳定，第三维分别为X弯矩，Y弯矩，X剪力，Y剪力，轴力，扭矩
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetSteelBraceCheck")]
        public static extern void dsnGetSteelBraceCheck(int nFloor, int nTotID, ref int nSect, float[,,] fpj, float[,,] fnl);
        //----------------------------------------------------------------------
        //fpj(out)         返回验算结果，第一维为截面编号，第二维分别为强度、X向稳定、Y向稳定、X向抗剪、Y向抗剪，第三维分别为计算应力、允许应力，组合号
        //fnl(out)         返回设计内力，第一维为截面位置，第二维分别为强度、X向稳定、Y向稳定、X向抗剪、Y向抗剪，第三维分别为X弯矩，Y弯矩，X剪力，Y剪力，轴力，扭矩
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetSteelBraceCheckNew")]
        public static extern void dsnGetSteelBraceCheckNew(int nFloor, int nTotID, ref int nSect, float[,,] fpj, float[,,] fnl);
        //----------------------------------------------------------------------
        //获得钢支撑截面验算结果
        //nFloor           楼层号，从1开始
        //nTotID(in)       支撑全楼编号
        //RmdX(out)        X向长细比
        //RmdY(out)        Y向长细比
        //RmdMax(out)      允许长细比
        //BTRatio(out)     宽厚比
        //BTRatioMax(out)  宽厚比限值
        //HTRatio(out)     高厚比
        //HTRatioMax(out)  高厚比限值
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetSteelBraceSectCheck")]
        public static extern bool dsnGetSteelBraceSectCheck(int nFloor, int nTotID, ref float RmdX, ref float RmdY, ref float RmdMax, ref float BTRatio, ref float BTRatioMax, ref float HTRatio, ref float HTRatioMax);
        //----------------------------------------------------------------------
        //获得钢支撑防火应力验算结果
        //nFloor           楼层号，从1开始
        //nTotID(in)       支撑全楼编号
        //nSect(out)       截面数量
        //fpj(out)         返回验算结果，第一维为截面编号，第二维分别为强度、X向稳定、Y向稳定，第三维分别为计算应力、允许应力，组合号
        //fnl(out)         返回设计内力，第一维为截面位置，第二维分别为强度、X向稳定、Y向稳定，第三维分别为X弯矩，Y弯矩，X剪力，Y剪力，轴力，扭矩
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetSteelBraceCheck_FH")]
        public static extern void dsnGetSteelBraceCheck_FH(int nFloor, int nTotID, ref int nSect, float[,,] fpj, float[,,] fnl);
        //----------------------------------------------------------------------//获得型钢砼支撑截面验算结果
        //nFloor           楼层号，从1开始
        //nTotID(in)       支撑全楼编号
        //RmdX(out)        X向长细比
        //RmdY(out)        Y向长细比
        //RmdMax(out)      允许长细比
        //BTRatio(out)     宽厚比
        //BTRatioMax(out)  宽厚比限值
        //HTRatio(out)     高厚比
        //HTRatioMax(out)  高厚比限值
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetSRCBraceSectCheck")]
        public static extern bool dsnGetSRCBraceSectCheck(int nFloor, int nTotID, ref float RmdX, ref float RmdY, ref float RmdMax, ref float BTRatio, ref float BTRatioMax, ref float HTRatio, ref float HTRatioMax);
        //----------------------------------------------------------------------
        //获得方钢管混凝土支撑应力验算结果
        //nFloor           楼层号
        //nTotID(in)       支撑全楼编号
        //nSect(out)       截面数量
        //fpj(out)         返回验算结果，第一维为截面编号，第二维分别为强度、X向稳定、Y向稳定、X向抗剪、Y向抗剪，第三维分别为计算应力、允许应力，组合号
        //fnl(out)         返回设计内力，第一维为截面位置，第二维分别为强度、X向稳定、Y向稳定、X向抗剪、Y向抗剪，第三维分别为X弯矩，Y弯矩，X剪力，Y剪力，轴力，扭矩
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetRectTubeBraceCheck")]
        public static extern void dsnGetRectTubeBraceCheck(int nFloor, int nTotID, ref int nSect, float[,,] fpj, float[,,] fnl);
        //----------------------------------------------------------------------
        //获得方钢管支撑截面验算结果
        //nFloor           楼层号，从1开始
        //nTotID(in)       支撑全楼编号
        //RmdX(out)        X向长细比
        //RmdY(out)        Y向长细比
        //RmdMax(out)      允许长细比
        //BTRatio(out)     宽厚比
        //BTRatioMax(out)  宽厚比限值
        //HTRatio(out)     高厚比
        //HTRatioMax(out)  高厚比限值
        //ALFAC(out)       混凝土工作承担系数
        //ALFACMax(out)    混凝土工作承担系数限值
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetRectTubeBraceSectCheck")]
        public static extern bool dsnGetRectTubeBraceSectCheck(int nFloor, int nTotID, ref float RmdX, ref float RmdY, ref float RmdMax, ref float BTRatio, ref float BTRatioMax, ref float HTRatio, ref float HTRatioMax, ref float ALFAC, ref float ALFACMax);
        //----------------------------------------------------------------------
        //获得方钢管混凝土支撑防火验算结果
        //nFloor           楼层号
        //nTotID(in)       柱全楼编号
        //nSect(out)       截面数量
        //fpj(out)         返回验算结果，第一维为截面编号，第二维分别为荷载比、承载力系数、所需保护层厚度、已有保护层厚度、组合号
        //fnl(out)         返回设计内力，第一维为截面位置，第二维分别为X弯矩，Y弯矩，X剪力，Y剪力，轴力，扭矩
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetRectTubeBraceCheck_FH")]
        public static extern void dsnGetRectTubeBraceCheck_FH(int nFloor, int nTotID, ref int nSect, float[,] fpj, float[,] fnl);
        //----------------------------------------------------------------------
        //获得圆钢管混凝土支撑应力验算结果
        //nFloor           楼层号
        //nTotID(in)       支撑全楼编号
        //nSect(out)       截面数量
        //fpj(out)         返回验算结果，第一维为截面编号，第二维分别为轴压强度、拉弯强度、抗剪强度，第三维分别为计算应力、允许应力，组合号
        //fnl(out)         返回设计内力，第一维为截面位置，第二维分别为轴压强度、拉弯强度、抗剪强度，第三维分别为X弯矩，Y弯矩，X剪力，Y剪力，轴力，扭矩
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetCircleTubeBraceCheck")]
        public static extern void dsnGetCircleTubeBraceCheck(int nFloor, int nTotID, ref int nSect, float[,,] fpj, float[,,] fnl);
        //----------------------------------------------------------------------
        //获得圆钢管支撑截面验算结果
        //nFloor           楼层号，从1开始
        //nTotID(in)       支撑全楼编号
        //RmdX(out)        X向长细比
        //RmdY(out)        Y向长细比
        //RmdMax(out)      允许长细比
        //SITA(out)        套箍指标
        //SITAMin(out)     套箍指标下限值
        //SITAMax(out)     套箍指标上限值
        //DTRatio(out)     径厚比
        //DTRatioMax(out)  径厚比限值
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetCircleTubeBraceSectCheck")]
        public static extern bool dsnGetCircleTubeBraceSectCheck(int nFloor, int nTotID, ref float RmdX, ref float RmdY, ref float RmdMax, ref float SITA, ref float SITAMin, ref float SITAMax, ref float DTRatio, ref float DTRatioMax);
        //----------------------------------------------------------------------
        //获得圆钢管混凝土支撑防火验算结果
        //nFloor           楼层号
        //nTotID(in)       柱全楼编号
        //nSect(out)       截面数量
        //fpj(out)         返回验算结果，第一维为截面编号，第二维分别为荷载比、承载力系数、所需保护层厚度、已有保护层厚度、组合号
        //fnl(out)         返回设计内力，第一维为截面位置，第二维分别为X弯矩，Y弯矩，X剪力，Y剪力，轴力，扭矩
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetCircleTubeBraceCheck_FH")]
        public static extern void dsnGetCircleTubeBraceCheck_FH(int nFloor, int nTotID, ref int nSect, float[,] fpj, float[,] fnl);
        //----------------------------------------------------------------------
        //获得叠合支撑截面验算结果
        //nFloor           楼层号，从1开始
        //nTotID(in)       支撑全楼编号
        //RmdX(out)        X向长细比
        //RmdY(out)        Y向长细比
        //RmdMax(out)      允许长细比
        //SITA(out)        套箍指标
        //SITAMin(out)     套箍指标下限值
        //SITAMax(out)     套箍指标上限值
        //DTRatio(out)     径厚比
        //DTRatioMax(out)  径厚比限值
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetTubeReinBraceSectCheck")]
        public static extern bool dsnGetTubeReinBraceSectCheck(int nFloor, int nTotID, ref float RmdX, ref float RmdY, ref float RmdMax, ref float SITA, ref float SITAMin, ref float SITAMax, ref float DTRatio, ref float DTRatioMax);
        //----------------------------------------------------------------------
        //判断该支撑设计时是否做为墙翼缘，0-不作为翼缘，1-只与单方向墙，2-与多方向墙相连
        //nFloor           楼层号，从1开始
        //nTotID(in)       柱全楼编号
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetBraceDesignWithWallColSign")]
        public static extern int dsnGetBraceDesignWithWallColSign(int nFloor, int nTotID);
        //----------------------------------------------------------------------
        //判断该支撑是否是异形柱
        //nFloor           楼层号，从1开始
        //nTotID(in)       柱全楼编号
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnBraceIsYXZ")]
        public static extern bool dsnBraceIsYXZ(int nFloor, int nTotID);
        //----------------------------------------------------------------------
        //判断该支撑是否是短柱
        //nFloor           楼层号，从1开始
        //nTotID(in)       柱全楼编号
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnBraceIsShort")]
        public static extern bool dsnBraceIsShort(int nFloor, int nTotID);
        //----------------------------------------------------------------------
        //获得该支撑长度、长度系数
        //nFloor           楼层号，从1开始
        //nTotID(in)       柱全楼编号
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetBraceLenCoe")]
        public static extern void dsnGetBraceLenCoe(int nFloor, int nTotID, ref float fLenX, ref float fLenY, ref float fLenXCoe, ref float fLenYCoe);
        //----------------------------------------------------------------------
        //获得支撑受剪承载力
        //nFloor           楼层号，从1开始
        //nTotID(in)       柱全楼编号
        //fSCX(out)        返回整体坐标系下X向受剪承载力
        //fSCY(out)        返回整体坐标系下Y向受剪承载力
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetBraceShearCapacity")]
        public static extern bool dsnGetBraceShearCapacity(int nFloor, int nTotID, ref float fSCX, ref float fSCY);
        //----------------------------------------------------------------------

        //////////////////////////////////////////////////////////////
        //墙梁设计结果输出
        //////////////////////////////////////////////////////////////
        //获得墙梁属性
        //nFloor           楼层号，从1开始
        //nTotID(in)       墙梁全楼编号
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetWallBeamKind")]
        public static extern int dsnGetWallBeamKind(int nFloor, int nTotID);
        //----------------------------------------------------------------------
        //获得墙梁材料属性
        //nFloor           楼层号，从1开始
        //nTotID(in)       墙梁全楼编号
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetWallBeamMatKind")]
        public static extern int dsnGetWallBeamMatKind(int nFloor, int nTotID);
        //----------------------------------------------------------------------
        //获得墙梁标准内力
        //nFloor           楼层号，从1开始
        //nTotID(in)       墙梁全楼编号
        //nLDCase(in)      工况号
        //Option(in)       1-调整前，2-调整后
        //nSect(out)       截面数量
        //force(out)       返回内力，第一维为截面数量，第二维分别为：X弯矩，Y弯矩，X剪力，Y剪力，轴力，扭矩
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetWallBeamStdForce")]
        public static extern bool dsnGetWallBeamStdForce(int nFloor, int nTotID, int nLDCase, int Option, ref int nSect, float[,] Force);
        //----------------------------------------------------------------------
        //获得墙梁某截面配筋
        //nFloor           楼层号，从1开始
        //nTotID(in)       墙梁全楼编号
        //nSect(out)       截面数量
        //fpj(out)         返回配筋面积，第一维为截面编号，第二维分别为上截面纵筋、下截面纵筋、箍筋，第三维分别为配筋面积、配筋率，组合号
        //fnl(out)         返回设计内力，第一维为截面位置，第二维分别为上截面纵筋、下截面纵筋、箍筋，第三维分别为X弯矩，Y弯矩，X剪力，Y剪力，轴力，扭矩
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetWallBeamAs")]
        public static extern void dsnGetWallBeamAs(int nFloor, int nTotID, ref int nSect, float[,,] fpj, float[,,] fnl);
        //----------------------------------------------------------------------
        //获得墙梁某截面配筋
        //nFloor           楼层号，从1开始
        //nTotID(in)       梁全楼编号
        //nSect(out)       截面数量
        //fpj(out)         返回配筋面积，第一维为截面编号，第二维分别为上截面纵筋、下截面纵筋、箍筋，第三维分别为配筋面积、计算配筋面积、配筋率，组合号
        //fnl(out)         返回设计内力，第一维为截面位置，第二维分别为上截面纵筋、下截面纵筋、箍筋，第三维分别为X弯矩，Y弯矩，X剪力，Y剪力，轴力，扭矩
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetWallBeamAsWithCal")]
        public static extern bool dsnGetWallBeamAsWithCal(int nFloor, int nTotID, ref int nSect, float[,,] fpj, float[,,] fnl);
        //----------------------------------------------------------------------
        //获得混凝土、型钢混凝土墙梁某截面配筋率
        //nFloor           楼层号，从1开始
        //nTotID(in)       梁全楼编号
        //nSect(out)       截面数量
        //fpj(out)         返回配筋面积，第一维为截面编号，第二维分别为上截面纵筋、下截面纵筋、箍筋，第三维分别为配筋率，最小配筋率，最大配筋率
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetWallBeamPJRatio")]
        public static extern bool dsnGetWallBeamPJRatio(int nFloor, int nTotID, ref int nSect, float[,,] fpjr);
        //----------------------------------------------------------------------
        //获得混凝土墙梁加密区、非加密区箍筋面积
        //nFloor           楼层号，从1开始
        //nTotID(in)       梁全楼编号
        //fHoopBarJM(out)  返回加密区箍筋面积
        //fHoopBar(out)    返回非加密区箍筋面积
        //fHoopBarJMRatio(out)  返回加密区箍筋面积
        //fHoopBarRatio(out)    返回非加密区箍筋面积
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetWallBeamAsVJM")]
        public static extern void dsnGetWallBeamAsVJM(int nFloor, int nTotID, ref float fHoopBarJM, ref float fHoopBar, ref float fHoopBarJMRatio, ref float fHoopBarRatio);
        //----------------------------------------------------------------------
        //获得混凝土墙梁剪扭配筋
        //nFloor           楼层号，从1开始
        //nTotID(in)       梁全楼编号
        //nSect(out)       截面数量
        //fpj(out)         返回配筋面积，第一维为截面编号，第二维分别为受扭沿周边单肢箍筋面积、受扭纵筋面积、计算受扭纵筋面积
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetWallBeamAsTL")]
        public static extern void dsnGetWallBeamAsTL(int nFloor, int nTotID, ref int nSect, float[,] fpj);
        //----------------------------------------------------------------------
        //获得混凝土墙梁斜筋配筋
        //nFloor           楼层号，从1开始
        //nTotID(in)       墙梁全楼编号
        //nSect(out)       截面数量
        //fpj(out)         返回配筋面积，第一维为截面编号，第二维分别为斜筋面积、计算斜筋面积、斜筋角度、组合号
        //fnl(out)         返回设计内力，第一维为截面位置，第二维分别为X弯矩，Y弯矩，X剪力，Y剪力，轴力，扭矩
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetWallBeamAsXJ")]
        public static extern void dsnGetWallBeamAsXJ(int nFloor, int nTotID, ref int nSect, float[,] fpj, float[,] fnl);
        //----------------------------------------------------------------------
        //获得墙梁跨高比
        //nFloor           楼层号，从1开始
        //nTotID(in)       墙梁全楼编号
        //fRatio(out)      跨高比
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetWallBeamSpanHRatio")]
        public static extern bool dsnGetWallBeamSpanHRatio(int nFloor, int nTotID, ref float fRatio);
        //----------------------------------------------------------------------

        //////////////////////////////////////////////////////////////
        //墙梁主梁设计结果输出
        //////////////////////////////////////////////////////////////
        //获得墙梁主梁数量
        //nFloor             楼层号，从1开始
        //nMainBeamNum(out)  梁段数量
        //nMainBeamID(out)   梁段编号数组
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetMainWallBeamNum")]
        public static extern void dsnGetMainWallBeamNum(int nFloor, ref int nMainBeamNum, int[] nMainBeamID);
        //----------------------------------------------------------------------
        //获得墙梁主梁包含的梁段编号
        //nFloor           楼层号，从1开始
        //ID(in)           主梁编号
        //BeamSegNum(out)  梁段数量
        //BeamSegID(out)   梁段全楼编号数组
        //BeamSegDir(out)  梁段方向与主梁方向
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetBeamSegIDbyMainWallBeam")]
        public static extern void dsnGetBeamSegIDbyMainWallBeam(int nFloor, int ID, ref int BeamSegNum, int[] BeamSegID, int[] BeamSegDir);
        //----------------------------------------------------------------------


        //////////////////////////////////////////////////////////////
        //墙柱设计结果输出
        //////////////////////////////////////////////////////////////
        //获得墙柱属性
        //nFloor           楼层号，从1开始
        //nTotID(in)       墙柱全楼编号
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetWallColumnKind")]
        public static extern int dsnGetWallColumnKind(int nFloor, int nTotID);
        //----------------------------------------------------------------------
        //获得墙柱材料属性
        //nFloor           楼层号，从1开始
        //nTotID(in)       墙柱全楼编号
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetWallColumnMatKind")]
        public static extern int dsnGetWallColumnMatKind(int nFloor, int nTotID);
        //----------------------------------------------------------------------
        //获得墙柱标准内力
        //nFloor           楼层号，从1开始
        //nTotID(in)       墙柱全楼编号
        //nLDCase(in)      工况号
        //Option(in)       1-调整前，2-调整后
        //nSect(out)       截面数量
        //force(out)       返回内力，第一维为截面数量，第二维分别为：X弯矩，Y弯矩，X剪力，Y剪力，轴力，扭矩
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetWallColumnStdForce")]
        public static extern bool dsnGetWallColumnStdForce(int nFloor, int nTotID, int nLDCase, int Option, ref int nSect, float[,] Force);
        //----------------------------------------------------------------------
        //获得墙柱面外标准内力
        //nFloor           楼层号，从1开始
        //nTotID(in)       墙柱全楼编号
        //nLDCase(in)      工况号
        //Option(in)       1-调整前，2-调整后
        //bOnlydsnNode(in) 是否只输出配筋节点对应的内力。如果是，则force第一维分别为：左侧：水平左、水平中、水平右，右侧：水平左、水平中、水平右；对于竖向为上、中、下
        //nNodeNum(out)    节点数量
        //force(out)       返回内力，第一维为节点序号，第二维分别为水平、竖向，第三维分别为：X弯矩，Y弯矩，X剪力，Y剪力，轴力，扭矩
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetWallColumnOutPlanStdForce")]
        public static extern bool dsnGetWallColumnOutPlanStdForce(int nFloor, int nTotID, int nLDCase, int Option, bool bOnlydsnNode, ref int nNodeNum, float[,,] Force);
        //----------------------------------------------------------------------
        //获得墙柱某截面配筋
        //nFloor           楼层号，从1开始
        //nTotID(in)       墙柱全楼编号
        //nSect(out)       截面数量
        //fpj(out)         返回配筋面积，第一维为截面位置（上、下），第二维分别为正截面起始端纵筋、正截面终止端纵筋、斜截面水平分布筋，第三维分别为配筋面积、计算配筋面积、组合号
        //fnl(out)         返回设计内力，第一维为截面位置（上、下），第二维分别为正截面起始端纵筋、正截面终止端纵筋、斜截面水平分布筋，第三维分别为X弯矩，Y弯矩，X剪力，Y剪力，轴力，扭矩
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetWallColumnAs")]
        public static extern void dsnGetWallColumnAs(int nFloor, int nTotID, ref int nSect, float[,,] fpj, float[,,] fnl);
        //----------------------------------------------------------------------
        //获得墙柱某截面配筋率
        //nFloor           楼层号，从1开始
        //nTotID(in)       墙柱全楼编号
        //nBarKind(in)     配筋种类，1-全截面纵筋，2-水平分布筋
        //AsSRatio(out)    返回截面下端配筋率
        //AsERatio(out)    返回截面上端配筋率
        //AsVRatio(out)    返回竖向分布筋配筋率
        //AsRatioMin(out)  返回最小配筋率
        //AsRatioMax(out)  返回最大配筋率
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetWallColumnBarRatio")]
        public static extern void dsnGetWallColumnBarRatio(int nFloor, int nTotID, int nBarKind, ref float AsSRatio, ref float AsERatio, ref float AsVRatio, ref float AsRatioMin, ref float AsRatioMax);
        //----------------------------------------------------------------------
        //获得墙柱双偏压配筋结果
        //nFloor           楼层号，从1开始
        //nTotID(in)       柱全楼编号
        //Dia(out)         返回钢筋直径，第一维为截面位置（上、下），第二维分别为起始端、终止端、分布筋
        //nBar(out)        返回钢筋根数，第一维为截面位置（上、下），第二维分别为起始端、终止端、分布筋
        //Space(out)       返回分布钢筋间距（mm），第一维为截面位置（上、下）
        //VerBarIsGZ(out)  返回分布钢筋是否为构造控制标记，0-计算，1-构造，第一维为截面位置（上、下）
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetWallColumnBiAxisAs")]
        public static extern bool dsnGetWallColumnBiAxisAs(int nFloor, int nTotID, float[,] fDia, int[,] nBar, float[] Space, int[] VerBarIsGZ);
        //----------------------------------------------------------------------
        //获得墙柱轴压比
        //nFloor           楼层号，从1开始
        //nTotID(in)       墙柱全楼编号
        //fZYB(out)        返回轴压比
        //fZYBMax(out)     返回轴压比限值
        //fZYBAxis(out)    返回轴压比对应的轴力设计值
        //fZYB_ZH(out)     返回组合轴压比
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetWallColumnZYB")]
        public static extern void dsnGetWallColumnZYB(int nFloor, int nTotID, ref float fZYB, ref float fZYBMax, ref float fZYBAxis, ref float fZYB_ZH);
        //----------------------------------------------------------------------
        //获得墙柱剪跨比
        //nFloor           楼层号，从1开始
        //nTotID(in)       墙柱全楼编号
        //fJKB(out)        返回剪跨比
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetWallColumnJKB")]
        public static extern void dsnGetWallColumnJKB(int nFloor, int nTotID, ref float fJKB);
        //----------------------------------------------------------------------
        //获得地下室外墙墙柱配筋
        //nFloor           楼层号，从1开始
        //nTotID(in)       墙柱全楼编号
        //fpj(out)         返回每延米双侧配筋面积
        //fnl(out)         返回设计内力，分别为X弯矩，Y弯矩，X剪力，Y剪力，轴力，扭矩
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetBaseWallColumnAs")]
        public static extern void dsnGetBaseWallColumnAs(int nFloor, int nTotID, ref float fpj, float[] fnl);
        //----------------------------------------------------------------------
        //获得墙柱面外配筋结果
        //nFloor           楼层号，从1开始
        //nTotID(in)       墙柱全楼编号
        //fpj(out)         返回配筋面积，第一维分别为竖向上、竖向中、竖向下、水平左、水平中、水平右，第二维分别为左侧、右侧（沿起点向终点看），第三维分别为配筋面积、计算配筋面积、组合号
        //fnl(out)         返回设计内力，第一维分别为竖向上、竖向中、竖向下、水平左、水平中、水平右，第二维分别为左侧、右侧（沿起点向终点看），第三维分别为X弯矩，Y弯矩，X剪力，Y剪力，轴力，扭矩
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetWallColumnOutPlanAs")]
        public static extern bool dsnGetWallColumnOutPlanAs(int nFloor, int nTotID, float[,,] fpj, float[,,] fnl);
        //----------------------------------------------------------------------
        //获得墙柱施工缝验算结果
        //nFloor           楼层号，从1开始
        //nTotID(in)       墙柱全楼编号
        //nSLWallColNum(out) 按全长验算时包含的同直线墙柱数量
        //nSLWallColTotID(out)  按全长验算时包含的同直线墙柱编号
        //nLDCombID(out)   组合号
        //fnl(out)         返回设计内力，分别为X弯矩，Y弯矩，X剪力，Y剪力，轴力，扭矩
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetWallColumnSeam")]
        public static extern bool dsnGetWallColumnSeam(int nFloor, int nTotID, ref int nSLWallColNum, int[] nSLWallColTotID, ref int nLDCombID, float[] fnl);
        //----------------------------------------------------------------------
        //获得墙柱施工缝验算不足时的补强钢筋面积，按竖向分布筋强度计算
        //nFloor           楼层号，从1开始
        //nTotID(in)       墙柱全楼编号
        //fAsNeed(out)     补强钢筋面积
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetWallColumnSeamAsNeed")]
        public static extern bool dsnGetWallColumnSeamAsNeed(int nFloor, int nTotID, ref float fAsNeed);
        //----------------------------------------------------------------------
        //该墙柱是否是短肢墙
        //nFloor           楼层号，从1开始
        //nTotID(in)       墙柱全楼编号
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnWallColumnIsShortLeg")]
        public static extern bool dsnWallColumnIsShortLeg(int nFloor, int nTotID);
        //----------------------------------------------------------------------
        //该墙柱是否按组合墙配筋，带端柱也算
        //nFloor           楼层号，从1开始
        //nTotID(in)       墙柱全楼编号
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnWallColumnIsDesignWithFlange")]
        public static extern bool dsnWallColumnIsDesignWithFlange(int nFloor, int nTotID);
        //----------------------------------------------------------------------
        //该墙柱是否按型钢砼墙配筋
        //nFloor           楼层号，从1开始
        //nTotID(in)       墙柱全楼编号
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnWallColumnIsDesignBySRC")]
        public static extern bool dsnWallColumnIsDesignBySRC(int nFloor, int nTotID);
        //----------------------------------------------------------------------
        //获得墙柱设计时上下翼缘柱信息
        //nFloor           楼层号，从1开始
        //nTotID(in)       墙柱全楼编号
        //nColTotID(out)   返回两端柱全楼编号
        //nColMatKind(out) 返回柱作为翼缘设计时采用的柱材料
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetWallColumnFlangeCol")]
        public static extern bool dsnGetWallColumnFlangeCol(int nFloor, int nTotID, int[] nColTotID, ref int nColMatKind);
        //----------------------------------------------------------------------
        //获得带翼缘墙柱的外轮廓多边形(mm)
        //nFloor           楼层号，从1开始
        //nTotID(in)       墙柱全楼编号
        //nNodeNum(out)    返回外轮廓多边形顶点数
        //dx、dy(out)      返回外轮廓多边形顶点坐标
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetFlangeWallColumnPoly")]
        public static extern bool dsnGetFlangeWallColumnPoly(int nFloor, int nTotID, ref int nNodeNum, double[] dx, double[] dy);
        //----------------------------------------------------------------------
        //获得计算组合轴压比时的墙柱真实外轮廓(mm)
        //nFloor           楼层号，从1开始
        //nTotID(in)       墙柱全楼编号
        //nNodeNum(out)    返回外轮廓多边形顶点数
        //dx、dy(out)      返回外轮廓多边形顶点坐标
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetZHZYBWallColumnPoly")]
        public static extern bool dsnGetZHZYBWallColumnPoly(int nFloor, int nTotID, ref int nNodeNum, double[] dx, double[] dy);
        //----------------------------------------------------------------------
        //获得墙柱所在的组合墙真实外轮廓(mm)
        //nFloor           楼层号，从1开始
        //nTotID(in)       墙柱全楼编号
        //nNodeNum(out)    返回外轮廓多边形顶点数
        //dx、dy(out)      返回外轮廓多边形顶点坐标
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetZHEdgePolyByWallColumn")]
        public static extern bool dsnGetZHEdgePolyByWallColumn(int nFloor, int nTotID, ref int nNodeNum, double[] dx, double[] dy);
        //----------------------------------------------------------------------
        //该墙柱是否是对称配筋
        //nFloor           楼层号，从1开始
        //nTotID(in)       墙柱全楼编号
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnWallColumnIsPJSymmetrical")]
        public static extern bool dsnWallColumnIsPJSymmetrical(int nFloor, int nTotID);
        //----------------------------------------------------------------------
        //该墙柱是否是按柱配筋
        //nFloor           楼层号，从1开始
        //nTotID(in)       墙柱全楼编号
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnWallColumnIsPJByCol")]
        public static extern bool dsnWallColumnIsPJByCol(int nFloor, int nTotID);
        //----------------------------------------------------------------------
        //判断墙柱所在的组合墙是否包含地下室外墙
        //nFloor           楼层号，从1开始
        //nTotID(in)       墙柱全楼编号
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnZHEdgePolyHasBaseWall")]
        public static extern bool dsnZHEdgePolyHasBaseWall(int nFloor, int nTotID);
        //----------------------------------------------------------------------
        //获得墙柱稳定验算结果
        //nFloor           楼层号，从1开始
        //nTotID(in)       墙柱全楼编号
        //fN(out)          返回设计轴力(kN)
        //fNMax(out)       返回允许轴力(kN)
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetWallColumnStability")]
        public static extern bool dsnGetWallColumnStability(int nFloor, int nTotID, ref float fN, ref float fNMax);
        //----------------------------------------------------------------------
        //输出墙柱稳定验算文本文件
        //nFloor           楼层号，从1开始
        //nTotID(in)       墙柱全楼编号
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnOutputWallColumnStabilityInf")]
        public static extern bool dsnOutputWallColumnStabilityInf(int nFloor, int nTotID);
        //----------------------------------------------------------------------
        //获得墙柱受剪承载力
        //nFloor           楼层号，从1开始
        //nTotID(in)       柱全楼编号
        //fSCX(out)        返回整体坐标系下X向受剪承载力
        //fSCY(out)        返回整体坐标系下Y向受剪承载力
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetWallColumnShearCapacity")]
        public static extern bool dsnGetWallColumnShearCapacity(int nFloor, int nTotID, ref float fSCX, ref float fSCY);
        //----------------------------------------------------------------------
        //获得墙柱aa
        //nFloor           楼层号，从1开始
        //nTotID(in)       柱全楼编号
        //faa(out)         返回钢筋合力点到截面边缘的距离(mm)
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetWallColumnaa")]
        public static extern bool dsnGetWallColumnaa(int nFloor, int nTotID, ref float faa);
        //----------------------------------------------------------------------
        //获得装配式中预制墙抗剪验算所需钢筋面积
        //nFloor           楼层号，从1开始
        //nTotID(in)       墙柱全楼编号
        //bIsDC(in)        是否是多层
        //fAs(out)         返回所需钢筋面积(mm2)
        //nLDCombID(out)   返回对应组合号
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetPcWallColumnShearCheck")]
        public static extern bool dsnGetPcWallColumnShearCheck(int nFloor, int nTotID, bool bIsDC, ref float fAs, ref int nLDCombID);
        //----------------------------------------------------------------------
        //获得外包钢板砼墙验算结果
        //nFloor           楼层号
        //nTotID(in)       墙柱全楼编号
        //nSect(out)       截面数量
        //fpj(out)         返回验算结果，第一维为截面编号，第二维分别为受弯承载力、受剪承载力，第三维分别为内力比，组合号
        //fnl(out)         返回设计内力，第一维为截面位置，第二维分别为受弯承载力、受剪承载力，第三维分别为X弯矩，Y弯矩，X剪力，Y剪力，轴力，扭矩
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetRectTubeWallColumnCheck")]
        public static extern bool dsnGetRectTubeWallColumnCheck(int nFloor, int nTotID, ref int nSect, float[,,] fpj, float[,,] fnl);
        //----------------------------------------------------------------------
        //获得外包钢板砼墙截面验算结果
        //nFloor           楼层号，从1开始
        //nTotID(in)       墙柱全楼编号
        //fTHRatio(out)    墙厚与钢板厚度之比
        //fTHRatioMin(out) 墙厚与钢板厚度之比下限值
        //fTHRatioMax(out) 墙厚与钢板厚度之比上限值
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetRectTubeWallColumnSectCheck")]
        public static extern bool dsnGetRectTubeWallColumnSectCheck(int nFloor, int nTotID, ref float fTHRatio, ref float fTHRatioMin, ref float fTHRatioMax);
        //----------------------------------------------------------------------
        //获得外包钢板+端柱砼墙验算结果
        //nFloor           楼层号
        //nTotID(in)       墙柱全楼编号
        //nSect(out)       截面数量
        //fpj(out)         返回验算结果，第一维为截面编号，第二维分别为受弯承载力、受剪承载力，第三维分别为内力比，组合号
        //fnl(out)         返回设计内力，第一维为截面位置，第二维分别为受弯承载力、受剪承载力，第三维分别为X弯矩，Y弯矩，X剪力，Y剪力，轴力，扭矩
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetRectTube_DBLSTEELWallColumnCheck")]
        public static extern bool dsnGetRectTube_DBLSTEELWallColumnCheck(int nFloor, int nTotID, ref int nSect, float[,,] fpj, float[,,] fnl);
        //----------------------------------------------------------------------
        //获得外包钢板+端柱砼墙截面验算结果
        //nFloor           楼层号，从1开始
        //nTotID(in)       墙柱全楼编号
        //fTHRatio(out)    墙厚与钢板厚度之比
        //fTHRatioMin(out) 墙厚与钢板厚度之比下限值
        //fTHRatioMax(out) 墙厚与钢板厚度之比上限值
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetRectTube_DBLSTEELWallColumnSectCheck")]
        public static extern bool dsnGetRectTube_DBLSTEELWallColumnSectCheck(int nFloor, int nTotID, ref float fTHRatio, ref float fTHRatioMin, ref float fTHRatioMax);
        //----------------------------------------------------------------------
        //获得钢板墙应力验算结果
        //nFloor           楼层号，从1开始
        //nTotID(in)       支撑全楼编号
        //nSect(out)       截面数量
        //fpj(out)         返回验算结果，第一维为截面编号，第二维分别为抗剪强度，第三维分别为计算应力、允许应力，组合号
        //fnl(out)         返回设计内力，第一维为截面位置，第二维分别为抗剪强度，第三维分别为X弯矩，Y弯矩，X剪力，Y剪力，轴力，扭矩
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetSteelWallColumnCheck")]
        public static extern void dsnGetSteelWallColumnCheck(int nFloor, int nTotID, ref int nSect, float[,,] fpj, float[,,] fnl);
        //----------------------------------------------------------------------
        //获得钢板墙截面验算结果
        //nFloor           楼层号，从1开始
        //nTotID(in)       支撑全楼编号
        //Rmd(out)         高厚比
        //RmdMax(out)      允许最大高厚比
        //RmdMin(out)      允许最小高厚比
        //KGRatio(out)     跨高比
        //KGRatioMax(out)  允许最大跨高比
        //KGRatioMin(out)  允许最小跨高比
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetSteelWallColumnSectCheck")]
        public static extern bool dsnGetSteelWallColumnSectCheck(int nFloor, int nTotID, ref float Rmd, ref float RmdMax, ref float RmdMin, ref float KGRatio, ref float KGRatioMax, ref float KGRatioMin);
        //----------------------------------------------------------------------
        //获得美国规范用地震组合下最大压应力(Mpa)，拉为正
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetWallColumnMaxfc_US")]
        public static extern bool dsnGetWallColumnMaxfc_US(int nFloor, int nTotID, ref float fcs, ref float fce);
        //----------------------------------------------------------------------
        //获得墙柱配筋用截面尺寸
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetWallColumnSect")]
        public static extern bool dsnGetWallColumnSect(int nFloor, int nTotID, int nCurSect, int nSectDSNType, ref float fB, ref float fH, ref float fBUp, ref float fTUp, ref float fBDw, ref float fTDw);
        //----------------------------------------------------------------------
        //获得美国规范简化算法墙柱配筋、aa
        //nFloor           楼层号，从1开始
        //nTotID(in)       柱全楼编号
        //faaS,faaE(out)   分别为截面下端、上端暗柱长度(mm)
        //fAsS,fAsE(out)   分别为截面下端、上端暗柱配筋面积(mm)
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetWallColumnSimplePJ_US")]
        public static extern bool dsnGetWallColumnSimplePJ_US(int nFloor, int nTotID, ref float faaS, ref float fAsS, ref float faaE, ref float fAsE);
        //----------------------------------------------------------------------
        //获得欧洲规范简化算法墙柱配筋、aa
        //nFloor           楼层号，从1开始
        //nTotID(in)       柱全楼编号
        //faaS,faaE(out)   分别为截面下端、上端暗柱长度(mm)
        //fAsS,fAsE(out)   分别为截面下端、上端暗柱配筋面积(mm)
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetWallColumnSimplePJ_EU")]
        public static extern bool dsnGetWallColumnSimplePJ_EU(int nFloor, int nTotID, ref float faaS, ref float fAsS, ref float faaE, ref float fAsE);
        //----------------------------------------------------------------------
        //获得弹性板PartID
        //nFloor           楼层号，从1开始
        //nRoomID(in)      板建模编号
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetTXBPartIDByRoomID")]
        public static extern int dsnGetTXBPartIDByRoomID(int nFloor, int nRoomID);
        //----------------------------------------------------------------------
        //////////////////////////////////////////////////////////////
        //获得空心板某预组合下的组合位移，采用节点值，不限制基本组合、标准组合
        //nFloor           楼层号，从1开始
        //nRoomID(in)      板建模编号
        //nLDCombType(in)  组合类别，如基本组合、标准组合等，采用宏定义
        //mapLDCombCoe(in) 每个工况对应的系数，采用设计模块的工况号
        //nRoomEleNum(out) 单元数量
        //dDis(out)        返回组合位移，分别为X、Y、Z
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetKXBElePrcCombDis")]
        public static extern bool dsnGetKXBElePrcCombDis(int nFloor, int nRoomID, int nLDCombType, int nPrcCombType, int nPrcComb, ref int nRoomEleNum, double[,,] dDis);
        //----------------------------------------------------------------------
        //获得弹性板某预组合下的组合位移，采用节点值，不限制基本组合、标准组合
        //nFloor           楼层号，从1开始
        //nRoomID(in)      板建模编号
        //nLDCombType(in)  组合类别，如基本组合、标准组合等，采用宏定义
        //mapLDCombCoe(in) 每个工况对应的系数，采用设计模块的工况号
        //nRoomNodeNum(out)节点数量
        //dDis(out)        返回组合位移，分别为X、Y、Z
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetTXBElePrcCombDis")]
        public static extern bool dsnGetTXBElePrcCombDis(int nFloor, int nRoomID, int nLDCombType, int nPrcCombType, int nPrcComb, ref int nRoomNodeNum, double[,] dDis);
        //----------------------------------------------------------------------
        //获得单片墙元某预组合下的组合位移，采用节点值，不限制基本组合、标准组合，该墙元可能是墙柱、墙梁、转壳连梁、框支梁
        //nFloor           楼层号，从1开始
        //nComKind(in)     构件类型
        //nTotID(in)       构件全楼编号
        //nPartID(in)      墙元计算编号
        //nLDCombType(in)  组合类别，如基本组合、标准组合等，采用宏定义
        //mapLDCombCoe(in) 每个工况对应的系数，采用设计模块的工况号
        //nPartNodeNum(out)节点数量
        //dDis(out)        返回组合位移，分别为X、Y、Z
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetPartElePrcCombDis")]
        public static extern bool dsnGetPartElePrcCombDis(int nFloor, int nComKind, int nTotID, int nPartID, int nLDCombType, int nPrcCombType, int nPrcComb, ref int nPartNodeNum, double[,] dDis);
        //----------------------------------------------------------------------
        //////////////////////////////////////////////////////////////
        //边缘构件设计结果输出
        //////////////////////////////////////////////////////////////
        //进行新边缘构件配筋，该函数目前不存数据
        //nFloor           楼层号，从1开始
        //pArrPJEdgeID(out) 编号数组
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnFormPJEdge")]
        public static extern bool dsnFormPJEdge(int nFloor);
        //----------------------------------------------------------------------
        //获得施工图边缘构件编号
        //nFloor           楼层号，从1开始
        //nID(in)          边缘构件编号
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetPJEdgeSGTID")]
        public static extern int dsnGetPJEdgeSGTID(int nFloor, int nID);
        //----------------------------------------------------------------------
        //根据施工图边缘构件编号获得新配筋边缘构件编号
        //nFloor           楼层号，从1开始
        //nSGTEdgeID(in)   施工图边缘构件编号
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetPJEdgeIDBySGTID")]
        public static extern int dsnGetPJEdgeIDBySGTID(int nFloor, int nSGTEdgeID);
        //----------------------------------------------------------------------
        //获得新配筋边缘构件配筋结果
        //nFloor           楼层号，从1开始
        //nID(in)          边缘构件编号
        //fpj(out)         返回配筋面积，第一维为截面位置（上、下），第二维分别为固定钢筋、分布钢筋，第三维分别为配筋面积、计算配筋面积、组合号
        //fnl(out)         返回设计内力，第一维为截面位置（上、下），第二维分别为固定钢筋、分布钢筋，第三维分别为X弯矩，Y弯矩，X剪力，Y剪力，轴力，扭矩
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetPJEdgePJ")]
        public static extern bool dsnGetPJEdgePJ(int nFloor, int nID, ref int nSect, float[,,] fpj, float[,,] fnl);
        //----------------------------------------------------------------------
        //获得新配筋边缘构件配筋用外轮廓
        //nFloor           楼层号，从1开始
        //nID(in)          边缘构件编号
        //nNodeNum(out)    返回外轮廓多边形顶点数
        //dx、dy(out)      返回外轮廓多边形顶点坐标
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetPJEdgePoly")]
        public static extern bool dsnGetPJEdgePoly(int nFloor, int nID, ref int nNodeNum, double[] dx, double[] dy);
        //----------------------------------------------------------------------


        //////////////////////////////////////////////////////////////
        //墙身设计结果输出
        //////////////////////////////////////////////////////////////
        //进行墙身配筋，该函数目前不存数据
        //nFloor           楼层号，从1开始
        //pArrPJEdgeID(out) 编号数组
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnFormPJWallBody")]
        public static extern bool dsnFormPJWallBody(int nFloor);
        //----------------------------------------------------------------------
        //获得施工图墙身编号
        //nFloor           楼层号，从1开始
        //nID(in)          墙身编号
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetPJWallBodySGTID")]
        public static extern int dsnGetPJWallBodySGTID(int nFloor, int nID);
        //----------------------------------------------------------------------
        //根据施工图墙身编号获得墙身编号
        //nFloor           楼层号，从1开始
        //nSGTWallBodyID(in)   施工图墙身编号
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetPJWallBodyIDBySGTID")]
        public static extern int dsnGetPJWallBodyIDBySGTID(int nFloor, int nSGTWallBodyID);
        //----------------------------------------------------------------------
        //获得墙身配筋结果
        //nFloor           楼层号，从1开始
        //nID(in)          墙身编号
        //fpj(out)         返回配筋面积，第一维为截面位置（上、下），第二维分别为X向钢筋、Y向钢筋，第三维分别为配筋面积、计算配筋面积、组合号
        //fnl(out)         返回设计内力，第一维为截面位置（上、下），第二维分别为X向钢筋、Y向钢筋，第三维分别为X弯矩，Y弯矩，X剪力，Y剪力，轴力，扭矩
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetPJWallBodyPJ")]
        public static extern bool dsnGetPJWallBodyPJ(int nFloor, int nID, ref int nSect, float[,,] fpj, float[,,] fnl);
        //----------------------------------------------------------------------
        //获得墙身配筋用外轮廓
        //nFloor           楼层号，从1开始
        //nID(in)          墙身编号
        //nNodeNum(out)    返回外轮廓多边形顶点数
        //dx、dy(out)      返回外轮廓多边形顶点坐标
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetPJWallBodyPoly")]
        public static extern bool dsnGetPJWallBodyPoly(int nFloor, int nID, ref int nNodeNum, double[] dx, double[] dy);
        //----------------------------------------------------------------------


        //////////////////////////////////////////////////////////////
        //弹塑性用函数
        //////////////////////////////////////////////////////////////
        //----------------------------------------------------------------------
        //获得楼层规定水平力(外力)
        //nFloor           楼层号，从1开始
        //nTower(in)       塔号
        //fFX,fFY(out)     X、Y方向楼层规定水平力
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnEPGetSeisAppF")]
        public static extern bool dsnEPGetSeisAppF(int nFloor, int nTower, ref double dFX, ref double dFY);
        //----------------------------------------------------------------------
        //获得单振型外力
        //nFloor           楼层号，从1开始
        //nTower(in)       塔号
        //nCurEigen(in)    振型号，从1开始
        //fFX,fFY(out)     X、Y方向楼层外力
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnEPGetEigenSeisF")]
        public static extern bool dsnEPGetEigenSeisF(int nFloor, int nTower, int nCurEigen, ref double dFX, ref double dFY);
        //----------------------------------------------------------------------

        //////////////////////////////////////////////////////////////
        //隔震设计结果
        //////////////////////////////////////////////////////////////
        //----------------------------------------------------------------------
        //获取工程中隔震层的层号和塔号
        //floor(in)              楼层号
        //tower(in)              塔号
        //ReturnValue            返回值标识着有多少个隔震层
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetIsolationFloorTowerData")]
        public static extern int dsnGetIsolationFloorTowerData(int[] floor, int[] tower);

        //----------------------------------------------------------------------
        //获取某隔震层的隔震支座的id
        //floor(in)                             楼层号
        //tower(in)                             塔号
        //isolationSupportIDArray(out)          隔震支座id数组
        //ReturnValue                           返回值表示有多少个隔震支座
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetIsolationSupportData")]
        public static extern int dsnGetIsolationSupportData(int nFloor, int nTower, int[] isolationSupportIDArray);

        //----------------------------------------------------------------------
        //获取隔震层支座的长期应力
        //floor(in)                             楼层号
        //tower(in)                             塔号
        //nIsolationSupportID(in)               隔震支座id
        //secondShpaeCo(out)                    隔震支座的第二形状系数
        //ReturnValue(out)                      返回值是隔震支座的长期应力
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetIsolationSupportLongtimeStress")]
        public static extern float dsnGetIsolationSupportLongtimeStress(int nFloor, int nTower, int nIsolationSupportID, ref float secondShpaeCo);

        //----------------------------------------------------------------------
        //获取隔震层支座的长期应力
        //floor(in)                             楼层号
        //tower(in)                             塔号
        //nIsolationSupportID(in)               隔震支座id
        //isolatorType(out)                     隔震支座的类别，目前均为0[橡胶支座]
        //activeDia(out)                        支座有效直径
        //activeArea(out)                       支座有效面积
        //horInitialStiffness(out)              水平初始刚度
        //verInitialStiffness(out)              竖向初始刚度
        //xHorYieldForce(out)                   水平X屈服力
        //yHorYieldForce(out)                   水平y屈服力
        //horStiffnessAfterYield(out)           屈服后的水平刚度
        //xStiffnessAfterIteration(out)         迭代后的X向等效刚度
        //yStiffnessAfterIteration(out)         迭代后的Y向等效刚度
        //xDampingAfterIteration(out)           迭代后的X向等效阻尼比
        //yDampingAfterIteration(out)           迭代后的Y向等效阻尼比
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetIsolatorData")]
        public static extern void dsnGetIsolatorData(int nFloor, int nTower, int nIsolationSupportID, ref int isolatorType, ref float activeDia, ref float activeArea,
           ref float horInitialStiffness, ref float verInitialStiffness, ref float xHorYieldForce, ref float yHorYieldForce,
           ref float horStiffnessAfterYield, ref float xStiffnessAfterIteration, ref float yStiffnessAfterIteration, ref float xDampingAfterIteration, ref float yDampingAfterIteration);

        //----------------------------------------------------------------------
        //获取支座最大拉应力和最大压应力
        //floor(in)                             楼层号
        //tower(in)                             塔号
        //nIsolationSupportID(in)               隔震支座id
        //maxTensiles(out)                      最大拉应力
        //maxCompresiveStress(out)              最大压应力
        //fMaxDisp(out)                         最大位移
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetIsolatorMaxTensileStressAndMaxCompressiveStress")]
        public static extern void dsnGetIsolatorMaxTensileStressAndMaxCompressiveStress(int nFloor, int nTower, int nIsolationSupportID, ref float maxTensiles, ref float maxCompresiveStress, ref float fMaxDisp);

        //----------------------------------------------------------------------
        //获取支座在各个工况下的位移
        //floor(in)                             楼层号
        //tower(in)                             塔号
        //nIsolationSupportID(in)               隔震支座id
        //nLDCase(out)                          工况号
        //disp[6]                               x,y,z,rx,ry,rz
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetIsolatorDisplacement")]
        public static extern void dsnGetIsolatorDisplacement(int nFloor, int nTower, int nIsolationSupportID, int nLDCase, float[] disp);

        //-----------------------------------------------------------------------
        //获取支座在各工况下的内力
        //floor(in)                             楼层号
        //tower(in)                             塔号
        //nIsolationSupportID(in)               隔震支座id
        //nLDCase(out)                          工况号
        //fNL[6]                                MX,MY,VX,VY,N,T
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetIsolatorNL")]
        public static extern void dsnGetIsolatorNL(int nFloor, int nTower, int nIsolationSupportID, int nLDCase, float[] fNL);
        //----------------------------------------------------------------------
        //获取隔震层的偏心率
        //floor(in)                          楼层号
        //tower(in)                          塔号
        //xResult(out)                       X方向的重心-刚心-偏心距-弹力半径-偏心率
        //yResult(out)                       Y方向的重心-刚心-偏心距-弹力半径-偏心率
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnGetIsolationFloorEccentricityRatio")]
        public static extern void dsnGetIsolationFloorEccentricityRatio(int nFloor, int nTower, double[] xResult, double[] yResult);

        //----------------------------------------------------------------------
        //隔震层的总水平力验算 : 风荷载及其他非地震作用的水平荷载标准值产生的总水平力不宜超过结构总重力的10%
        //floor(in)                          楼层号
        //tower(in)                          塔号
        //ratio[2](out)                      表示X、Y方向风和其他非地震作用的水平荷载标准值产生的总水平力与结构总重力的比值 [不宜超过10%]
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnCheckIsolationFloorTotalHorizontalForce")]
        public static extern void dsnCheckIsolationFloorTotalHorizontalForce(int nFloor, int nTower, ref float xFv, ref float yFv, ref float fG);

        //----------------------------------------------------------------------
        //隔震层的抗风承载力  1.4 * fVw <= fVs
        //floor(in)                          楼层号
        //tower(in)                          塔号
        //fVs[2](out)                        X、Y方向隔震层抗风承载力设计值(由抗风装置和各镇支座的屈服力构成)
        //fVw[2](out)                        X、Y方向风荷载下隔震层的水平剪力标准值
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnCheckIsolationFloorWindResistance")]
        public static extern void dsnCheckIsolationFloorWindResistance(int nFloor, int nTower, float[] fVs, float[] fVw);

        //----------------------------------------------------------------------
        //隔震层的屈重比[注意：目前给了接口，但是由于规范并没有强制给定这个依据]
        //隔震层X方向的屈服力与隔震层以上重力荷载代表值的比值[下限值2%]
        //floor(in)                          楼层号
        //tower(in)                          塔号
        //fXIsoYieldForce(out)               隔震层X方向的屈服力
        //fYIsoYieldForce(out)               隔震层Y方向的屈服力e
        //fG(out)                            隔震层以上重力荷载代表值
        [DllImport("YJKDesign.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.Cdecl, EntryPoint = "dsnCheckTheRatioOfYieldForceAndGravity")]
        public static extern void dsnCheckTheRatioOfYieldForceAndGravity(int nFloor, int nTower, ref float fXIsoYieldForce, ref float fYIsoYieldForce, ref float fG);

    }
}
