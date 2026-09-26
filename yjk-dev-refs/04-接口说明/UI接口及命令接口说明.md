public class ClrYJKSUI
{
public:
ClrYJKSUI(void);
~ClrYJKSUI(void);
// 函数功能：运行命令
BOOL CsQRunCommandEx(String lpszCmdString, String lpCmdParam, BOOL bFlags);
// 函数功能：运行命令(目前仅针对于导出ydb的功能，ydbPath为输出ydb的路径，如: @"D:\5.C#二次开发\MyExample\ydb\kj0518.ydb"，projPath为工程文件目录（不带.yjk后缀），如@"D:\1.pyYJKS\yjk_test5.1\test03\1")
BOOL CsQRunCommandEx(String lpszCmdString ,String ydbPath, String projPath);
//设置当前标签
BOOL CsQSetCurrentRibbonLabel(String lpszCurLabelIDString);
//在视图区设定鼠标位置
BOOL CsQViewSetCursorPos(int x, int y);
//设置脚本状态，为true则为脚本状态，调用命令之后不弹出窗口，false为非脚本状态，调用命令之后弹出窗口，调用位置需要在导入ydb之后执行。
BOOL CsQSetRunScript(BOOL bScript);
//获取命令的参数
String CsGetScriptParam();
// 函数功能：获取程序路径
String CsQGetAppPath();
//工程量统计
//bJsgz,计算规则，下标各位分别代表：0，板扣梁墙，1，板扣柱，2，梁扣柱，3，梁扣墙，4，墙扣柱
//SteelDensity 钢材容重
// iOutKind 输出形式选择，0,文本，1，word，2，excel
// iResKind 输出内容选择，0,所有工程量，1，型材截面统计
// bOpenFile 是否打开生成的文件
void yjkConcretStat(ref int[] bJsgz,float SteelDensity, int iOutKind, int iResKind, int bOpenFile);
// 插入衬图
// vRefs 插入衬图数据的列表
// Mdl_RefInfo 衬图数据，nBzcNo 标准层编号，ptBaseX 基点X，ptBaseY 基点Y，ptBaseZ // 基点Z，ptInsertX 插入点X，ptInsertY 插入点Y，ptInsertZ 插入点Z，bVisible 是否可// 见，strFilePath 衬图路径。
// bClearOld是否清掉标准层的原有衬图，1为是，0为否。
void yjkAddReference(List<Mdl_RefInfo> vRefs, bool bClearOld);
//获取版本信息
String CsQGetYJKSVersion();
};
public class ClrYJKSCommand
{
public:
ClrYJKSCommand(void);
~ClrYJKSCommand(void);
//运行命令，cmdName为命令名称,
int CsRunCommand(String cmdName);
//获取当前项目的路径
String CsGetCurrentPath();
};