前处理接口
public class Hi_CToSDesign	// 此类包含楼层信息的相关参数及塔数据定义
{
public:
Hi_CToSDesign();
~Hi_CToSDesign();
// 总层数
int NZRC();
// 总节点数
int NJD();
// 获取节点坐标
void XYZ(int jdID, ref float x, ref float y, ref float z);
// 获取节点X坐标
float X(int jdID);
// 获取节点Y坐标
float Y(int jdID);
// 获取节点Z坐标
float Z(int jdID);
// 节点对应的结构模型编号f
int JDONO(int jdID);
// 节点对应的结构模型楼层号(处理坡屋面和下层节点重合问题)
int JDOFlr(int jdID);
//	节点质量
void JDMass(int jdID, ref float dmass, ref float lmass);
// 节点刚性连接主节点
int JDLinkTo(int jdID);
// 塔高
float HeiTow(int iFlr, int iTow);
// 塔底标高
float EleTow(int iFlr, int iTow);
// 塔附加质量
float TowAddM(int iFlr, int iTow);
// 各塔恒活质量总值
float DLTow(int iFlr, int iTow);
float LLTow(int iFlr, int iTow);
float LLZJTow(int iFlr, int iTow);
//模型塔数
int TowInMdl();
//某层塔数
int TowInflr(int iFlr);
//	性能设计包络模型 iSeis-1/2:中震/大震 iLvl-1/2:弹性/不屈服
//	(0,1)表示隔震设计中震弹性模型
//	(0,2)表示减震设计小震弹性模型
LPCTSTR PDDir(int iSeis, int iLvl);
int ResetToPD(int iSeis, int iLvl);
// 某层某类构件数量
int NGJ(int iKind, int iFlr);
// 构件层号(注意,此ID及以下各ID在未特别说明的情况下均指全楼ID)
int GJFlr(int iKind, int gjID);
// 某层某类构件ID数组
void FlrGJs(int iKind, int iFlr, int Num);
// 构件塔号
List<int> GJTow(int iKind, int gjID);
// 构件在结构模型中的层号O for Original
int GJOFlr(int iKind, int gjID);
// 构件在结构模型中的编号
int GJONO(int iKind, int gjID);
// 构件截面在结构模型中的编号
int GJOLX(int iKind, int gjID);
// 杆件两端节点
void GJJD(int iKind, int gjID, ref int j1, ref int j2);
// 构件材料类型及标号
void GJMat(int iKind, int gjID, ref int matType, ref float matGrade,
ref float matGrade2);
// 构件抗震等级
int GJKZDJ(int iKind, int gjID);
// 构件是否包络设计
int IsEnvelope(int iKind, int gjID);
// 某层梁数
int NBeam(int iFlr);
// 某层梁ID数组
List<int> FlrBeams(int iFlr, int Num);
// 梁层号
int BeamFlr(int BeamID);
// 梁塔号
int BeamTow(int BeamID);
// 裙房梁关联上方塔号
int QFBeamTow(int BeamID);
// 梁的层内编号
int BeamIDInFlr(int BeamID);
// 梁在结构模型中的层号O for Original
int BeamOFlr(int BeamID);
// 梁在结构模型中的编号
int BeamONO(int BeamID);
// 梁在结构模型中的ID(基础梁需求)
int BeamOID(int BeamID);
// 梁截面在结构模型中的编号
int BeamOLX(int BeamID);
// 梁两端节点
void BeamJD(int BeamID, ref int j1, ref int j2);
// 弧梁
int BeamArcCen(int BeamID, ref float xc, ref float yc, ref float zc);
// 梁材料类型及标号
void BeamMat(int BeamID, ref int matType, ref float matGrade,
ref float matGrade2);
// 波纹钢号
int BeamCorStl(int BeamID);
// 梁特殊构件信息
int IsSpecBeam(int BeamID, EBeamSpec);
// 梁系数 EGDXSW:风工况刚度系数 EGDXSS:地震工况刚度系数
float BeamCoef(int BeamID, EBeamCoef);
// 梁抗震等级
virtual int BeamKZDJ(int BeamID);
// 梁端约束(固接,铰接,滑动)
enum EBarRest{ERESTFIX=0,ERESTHINGE=1,ERESTSLIDING=2,ERESTSEMIHINGE=3};
void BeamRest(int BeamID, EBarRest &, EBarRest &);
// 梁保护层厚度
int BeamStlCover(int BeamID);
// 梁主筋等级(返回值见yjkSParaHeader.h中宏定义)
int BeamMainStl(int BeamID);
// 梁箍筋等级
int BeamHoopStl(int BeamID);
// 梁平面外长度(m)
float BeamMianwai(int BeamID);
// 梁刚域
void BeamRigid(int BeamID, ref float rig1, ref float rig2);
// 底框梁轴力
void BeamDKF(int BeamID, ref float fd, ref float fl);
// 梁偏心
void BeamEcc(int BeamID, ref float[] ecc1, ref float[] ecc2);
// 返回1为交叉配筋 2为斜撑配筋 3为对角斜筋
int BeamWallStlType(int BeamID);
// 梁活荷折减系数
float BeamHHZJXS(int BeamID);
// 梁活荷重力荷载代表值组合系数
float BeamHHGEXS(int BeamID);
// 梁自定义工况折减系数
int BeamCustZJXS(int BeamID, int lcID, ref float zjxs);
// 组合梁信息(tb:板托顶宽,bb:板托底宽)
// shearType 0:无抗剪连接件 1:完全抗剪连接 2:不完全抗剪连接
// studType 栓钉型号 M10,M13,M16,M19,M22
// studRows 栓钉排数
// studDist 栓钉间距
// studHeight 栓钉高度
int BeamZHLData(int BeamID, ref int be, ref int hc1, ref int hc2,
ref int tb, ref int bb, ref int shearType, ref int studType,
ref int studRows, ref int studDist, ref int studHeight);
// 组合梁后增信息,主要用于纵向抗剪验算(翼板b1,b2,及栓钉外缘距)
int BeamZHLDataEx(int BeamID, ref int b1, ref int b2, ref int studWidth);
// 组合梁负弯矩区有效翼板宽度等
int BeamZHLDataSup(int BeamID, ref int be, ref int b1, ref int b2, ref int studDist);
// 组合梁混凝土楼板纵筋信息(等级,直径,间距)
int BeamZHLBar(int BeamID, ref int gradeT, ref int diaT, ref int disT,
ref int gradeB, ref int diaB, ref int disB);
// 组合梁混凝土楼板横筋信息(等级,直径,间距)
int BeamZHLHBar(int BeamID, ref int gradeT, ref int diaT, ref int disT,
ref int gradeB, ref int diaB, ref int disB);
// 抗剪连接件为槽钢时的参数,返回值表示抗剪连接件是否为槽钢
// Nvc1为单个槽钢连接件的受剪承载力设计值
int BeamZHLCStl(int BeamID, ref int studDist, ref int stlHeight,
ref int stlWidth, ref float Nvc1);
// 包络设计梁
int IsBeamEnvelope(int gjID);
// 梁重要性系数
float BeamEta(int BeamID);
// 人防构件
int IsBeamAd(int BeamID);
// 按高规进行性能设计时的构件类型 1:关键 2:普通竖向 3:耗能
int BeamPerformType(int BeamID);
// 梁的空间结构属性
// sys: 1.网架 2.双层网壳 3.单层网壳 4.立体桁架 5:一般桁架 6:中心支撑 7:偏心支撑 8:门刚支撑
// type: 1.弦杆及支座腹杆(单层壳面内) 2.腹杆(单层壳面外)
void BeamSpaceType(int BeamID, ref int sys, ref int type);
// 是否按实体单元计算
int IsBeamSolid(int BeamID);
// 梁内钢板宽高
int BeamStlBH(int BeamID, ref int b, ref int h);
// 是否考虑竖向地震
int IsBeamVE(int BeamID);
// 门刚梁横向加劲肋间距与腹板最大高度的比值(a/Hw)(0为不设加劲肋)
float BeamAHw(int BeamID);
// 梁上荷载lc工况(type:1集中力 2集中扭矩 3分布力 4分布扭矩)(cs坐标系:0全局 1局部)
// dir1,2,3轴 seg分段数 load各组荷载(最多分四段,0为定位距离负值表示相对坐标,1荷载值)
// loadsum荷载总值
int BeamLoad(int BeamID, ref int[] lc, ref int[] type, ref int[] cs,
ref int[] dir, ref int[] nseg, ref float[][][] load, ref float[] loadsum);
// 按抗规进行性能设计时的性能水准 (0不考虑 1不屈服 2弹性 3屈服) zz中震 zjm正截面
void BeamPerLvl(int BeamID, ref int zzzjm, ref int zzxjm, ref int dzzjm, ref int dzxjm);
// 是否新钢规性能设计塑性耗能构件
int BeamSTHaoneng(int BeamID);
// 新钢规性能设计宽厚比
int BeamSTKHB(int BeamID);
// 新钢规性能设计延性等级
int BeamSTYanxing(int BeamID);
// 新钢规性能设计非耗能构件系数
float BeamSTBetae(int BeamID);
// 6组刚度系数,轴向,2轴方向剪切,3轴方向剪切,抗扭,绕2轴抗弯,绕3轴抗弯,返回值表示是否为用户指定
int BeamRigCoef(int BeamID, ref float[] rig);
// 获取梁温差 1:升温 2:降温 3:防火升温
void BeamTemp(int BeamID, ref float[] temp);
// iqz-0:膨胀型 1:非膨胀型 th:设计耐火极限 ri:等效热阻/等效热传导系数 dil:保护层厚度 fxz:截面形状系数
int BeamFirePara(int BeamID, ref float th, ref int iqz, ref float ri, ref float dil, ref float fxz);
// 美规梁延性等级
int BeamDuct(int BeamID);
// 结构重要性系数
float BeamGama0(int BeamID);
// 钢梁下翼缘稳定验算
int BeamXYYWD(int BeamID);
// 梁是否大跨屋盖结构关键构件(执行抗规10.2.13)
int IsBeamRoofKey(int BeamID);
// 实配钢筋超配系数
float BeamCPXS(int BeamID);
// 钢梁板件宽厚比限值
int BeamKHBMax(int BeamID, ref float top, ref float web, ref float bottom);
// 按隔规进行性能设计时的构件类型 1:关键 2:普通竖向 3:重要水平 4:普通水平
int BeamIsoType(int BeamID);
// 是否隔震支墩或关联构件
int BeamIsoZd(int BeamID);
// 梁安全性鉴定信息(type=1:主要构件 2:一般构件, coef:局部承载力折减系数 seisCoef:抗震鉴定承载力折减系数)
void BeamSafe(int BeamID, ref int type, ref float coef, ref float seisCoef);
// 某层柱数
int NColumn(int iFlr);
// 某层柱ID数组
List<int> FlrColumns(int iFlr, int Num);
// 柱层号
int ColumnFlr(int ColumnID);
// 柱塔号
int ColumnTow(int ColumnID);
// 裙房柱关联上方塔号
int QFColumnTow(int ColumnID);
// 柱的层内编号
int ColumnIDInFlr(int ColumnID);
// 柱在结构模型中的层号O for Original
int ColumnOFlr(int ColumnID);
// 柱在结构模型中的编号
int ColumnONO(int ColumnID);
// 柱截面在结构模型中的编号
int ColumnOLX(int ColumnID);
// 柱两端节点
void ColumnJD(int ColumnID, ref int j1, ref int j2);
// 柱材料类型及标号(matGrade3为叠合柱内混凝土强度,>0时为叠合柱)
void ColumnMat(int ColumnID, ref int matType, ref float matGrade,
ref float matGrade2, ref float matGrade3);
// 波纹钢号
int ColumnCorStl(int ColumnID);
// 柱抗震等级
int ColumnKZDJ(int ColumnID);
// 柱计算长度系数
void ColumnCL(int ColumnID, ref float mux_cy, ref float muy_cy,
ref float mux_ncy, ref float muy_ncy,
ref float clx, ref float cly);
// 特殊柱
int IsSpecColumn(int ColumnID, EColumnSpec);
// 是否边框柱
int ColumnBK(int ColumnID);
// 柱上方层数
int ColumnUpFlrN(int ColumnID);
// 柱端约束(固接,铰接,滑动)
void ColumnRest(int ColumnID, EBarRest &, EBarRest &);
// 柱保护层厚度
int ColumnStlCover(int ColumnID);
// 柱主筋等级(返回值见yjkSParaHeader.h中宏定义)
int ColumnMainStl(int ColumnID);
// 柱箍筋等级
int ColumnHoopStl(int ColumnID);
// 柱刚域
void ColumnRigid(int ColumnID, ref float rig1, ref float rig2);
// 柱偏心
void ColumnEcc(int ColumnID, ref float ex, ref float ey);
// 柱剪力系数
void ColumnShear(int ColumnID, ref float shearx, ref float sheary);
// 轴压比限值增减量
float ColumnZYBZJ(int ColumnID);
// 与转换梁相连的柱
int ColumnSupBeam(int ColumnID);
// 柱活荷折减系数
float ColumnHHZJXS(int ColumnID);
// 柱活荷重力荷载代表值组合系数
float ColumnHHGEXS(int ColumnID);
// 包络设计柱
int IsColmEnvelope(int gjID);
// 柱重要性系数
float ColumnEta(int ColumnID);
// 人防构件
int IsColumnAd(int ColumnID);
// 按高规进行性能设计时的构件类型 1:关键 2:普通竖向 3:耗能
int ColumnPerformType(int ColumnID);
// 柱的空间结构属性
// sys: 1.网架 2.双层网壳 3.单层网壳 4.立体桁架 5:一般桁架 6:中心支撑 7:偏心支撑 8:门刚支撑 9:温室结构
// type: 1.弦杆及支座腹杆(单层壳面内) 2.腹杆(单层壳面外) 6:温室主要承重构件 7:温室拱杆 8:温室其它构件
void ColumnSpaceType(int ColumnID, ref int sys, ref int type);
// 是否按实体单元计算
int IsColumnSolid(int ColumnID);
// 是否考虑竖向地震
int IsColumnVE(int ColumnID);
// 门刚柱横向加劲肋间距与腹板最大高度的比值(a/Hw)(0为不设加劲肋)
float ColumnAHw(int ColumnID);
// 柱上荷载lc工况(type:1集中力 2集中扭矩 3分布力 4分布扭矩)(cs坐标系:0全局 1局部)
// dir1,2,3轴 seg分段数 load各组荷载(最多分四段,0为定位距离负值表示相对坐标,1荷载值)
// loadsum荷载总值
int ColumnLoad(int ColumnID, ref int[] lc, ref int[] type, ref int[] cs,
ref int[] dir, ref int[] nseg, ref float[][][] load, ref float[] loadsum);
// 按抗规进行性能设计时的性能水准 (0不考虑 1不屈服 2弹性 3屈服) zz中震 zjm正截面
void ColumnPerLvl(int ColumnID, ref int zzzjm, ref int zzxjm, ref int dzzjm, ref int dzxjm);
// 是否新钢规性能设计塑性耗能构件
int ColumnSTHaoneng(int ColumnID);
// 新钢规性能设计宽厚比
int ColumnSTKHB(int ColumnID);
// 新钢规性能设计延性等级
int ColumnSTYanxing(int ColumnID);
// 新钢规性能设计非耗能构件系数
float ColumnSTBetae(int ColumnID);
// 6组刚度系数,轴向,2轴方向剪切,3轴方向剪切,抗扭,绕2轴抗弯,绕3轴抗弯,返回值表示是否为用户指定
int ColumnRigCoef(int ColumnID, ref float[] rig);
// 获取柱温差 1:升温 2:降温 3:防火升温
void ColumnTemp(int ColumnID, ref float[] temp);
// iqz-0:膨胀型 1:非膨胀型 th:设计耐火极限 ri:等效热阻/等效热传导系数 dil:保护层厚度 fxz:截面形状系数
int ColumnFirePara(int ColumnID, ref float th, ref int iqz, ref float ri, ref float dil, ref float fxz);
// 美规柱延性等级
int ColumnDuct(int ColumnID);
// 结构重要性系数
float ColumnGama0(int ColumnID);
// 柱是否大跨屋盖结构关键构件(执行抗规10.2.13)
int IsColumnRoofKey(int ColumnID);
// 实配钢筋超配系数
float ColumnCPXS(int ColumnID);
// 按隔规进行性能设计时的构件类型 1:关键 2:普通竖向 3:重要水平 4:普通水平
int ColumnIsoType(int ColumnID);
// 钢柱板件宽厚比限值(圆柱则khbFlange为径厚比,khbWeb无意义,0表示程序自动计算)
int ColumnKHBMax(int ColumnID, ref float khbFlange, ref float khbWeb);
// 钢柱长细比限值(0表示程序自动计算)
int ColumnCXBMax(int ColumnID, ref float cxb);
// 地震作用放大系数
int ColumnSeisCoef(int ColumnID, ref float xCoef, ref float yCoef);
// 是否隔震支墩或关联构件
int ColumnIsoZd(int ColumnID);
// 柱安全性鉴定信息(type=1:主要构件 2:一般构件, coef:局部承载力折减系数 seisCoef:抗震鉴定承载力折减系数)
void ColumnSafe(int ColumnID, ref int type, ref float coef, ref float seisCoef);
//某层斜杆数
int NBrace(int iFlr);
// 某层斜杆ID数组
List<int> FlrBraces(int iFlr, int Num);
// 斜杆层号
int BraceFlr(int BraceID);
// 斜杆塔号
int BraceTow(int BraceID);
// 裙房斜杆关联上方塔号
int QFBraceTow(int BraceID);
// 斜杆层内编号
int BraceIDInFlr(int BraceID);
// 斜杆在结构模型中的层号O for Original
int BraceOFlr(int BraceID);
// 斜杆在结构模型中的编号
int BraceONO(int BraceID);
// 斜杆截面在结构模型中的编号
int BraceOLX(int BraceID);
// 斜杆两端节点
void BraceJD(int BraceID, ref int j1, ref int j2);
// 斜杆材料类型及标号(matGrade3为叠合柱内混凝土强度,>0时为叠合柱)
void BraceMat(int BraceID, ref int matType, ref float matGrade,
ref float matGrade2, ref float matGrade3);
// 斜杆抗震等级
int BraceKZDJ(int BraceID);
// 斜杆计算长度系数
void BraceCL(int BraceID, ref float mux, ref float muy,
ref float clx, ref float cly);
// 特殊支撑
int IsSpecBrace(int BraceID, EBraceSpec);
// 斜杆上方层数
int BraceUpFlrN(int BraceID);
// 斜杆端约束(固接,铰接,滑动)
void BraceRest(int BraceID, EBarRest &, EBarRest &);
// 斜杆保护层厚度
int BraceStlCover(int BraceID);
// 斜杆主筋等级(返回值见yjkSParaHeader.h中宏定义)
int BraceMainStl(int BraceID);
// 斜杆箍筋等级
int BraceHoopStl(int BraceID);
// 斜杆活荷折减系数
float BraceHHZJXS(int BraceID);
// 斜杆活荷重力荷载代表值组合系数
float BraceHHGEXS(int BraceID);
// 包络设计支撑
int IsBraceEnvelope(int gjID);
// 斜杆是否桁架杆件(0:非桁架 1:桁架腹杆 2:桁架弦杆)
int IsBraceTruss(int gjID);
// 斜杆重要性系数
float BraceEta(int BraceID);
// 人防构件
int IsBraceAd(int BraceID);
// 按高规进行性能设计时的构件类型 1:关键 2:普通竖向 3:耗能
int BracePerformType(int BraceID);
// 斜杆的空间结构属性
// sys: 1.网架 2.双层网壳 3.单层网壳 4.立体桁架 5:一般桁架 6:中心支撑 7:偏心支撑 8:门刚支撑 9:温室结构
// type: 0:非桁架 1:上弦杆(单层壳面内) 2:腹杆(单层壳面外) 3:中层弦杆 4:下弦杆 5:支座腹杆 6:温室主要承重构件 7:温室拱杆 8:温室其它构件
void BraceSpaceType(int BraceID, ref int sys, ref int type);
// 是否按实体单元计算
int IsBraceSolid(int BraceID);
// 是否考虑竖向地震
int IsBraceVE(int BraceID);
// 按抗规进行性能设计时的性能水准 (0不考虑 1不屈服 2弹性 3屈服) zz中震 zjm正截面
void BracePerLvl(int BraceID, ref int zzzjm, ref int zzxjm, ref int dzzjm, ref int dzxjm);
// 是否新钢规性能设计塑性耗能构件
int BraceSTHaoneng(int BraceID);
// 新钢规性能设计宽厚比
int BraceSTKHB(int BraceID);
// 新钢规性能设计延性等级
int BraceSTYanxing(int BraceID);
// 新钢规性能设计非耗能构件系数
float BraceSTBetae(int BraceID);
// 6组刚度系数,轴向,2轴方向剪切,3轴方向剪切,抗扭,绕2轴抗弯,绕3轴抗弯,返回值表示是否为用户指定
int BraceRigCoef(int BraceID, ref float[] rig);
// 获取支撑温差 1:升温 2:降温 3:防火升温
void BraceTemp(int BraceID, ref float[] temp);
// iqz-0:膨胀型 1:非膨胀型 th:设计耐火极限 ri:等效热阻/等效热传导系数 dil:保护层厚度 fxz:截面形状系数
int BraceFirePara(int BraceID, ref float th, ref int iqz, ref float ri, ref float dil, ref float fxz);
// 美规支撑延性等级
int BraceDuct(int BraceID);
// 结构重要性系数
float BraceGama0(int BraceID);
// 斜杆是否大跨屋盖结构关键构件(执行抗规10.2.13)
int IsBraceRoofKey(int BraceID);
// 实配钢筋超配系数
float BraceCPXS(int BraceID);
// 按隔规进行性能设计时的构件类型 1:关键 2:普通竖向 3:重要水平 4:普通水平
int BraceIsoType(int BraceID);
// 钢支撑板件宽厚比限值(圆管则khbFlange为径厚比,khbWeb无意义,0表示程序自动计算)
int BraceKHBMax(int BraceID, ref float khbFlange, ref float khbWeb);
// 钢支撑长细比限值(压/拉,0表示程序自动计算)
int BraceCXBMax(int BraceID, ref float cxbPres, ref float cxPull);
// 是否隔震支墩或关联构件
int BraceIsoZd(int BraceID);
// 斜杆安全性鉴定信息(type=1:主要构件 2:一般构件, coef:局部承载力折减系数 seisCoef:抗震鉴定承载力折减系数)
void BraceSafe(int BraceID, ref int type, ref float coef, ref float seisCoef);
// 某层墙梁数
int NWallBeam(int iFlr);
// 某层墙梁编号
List<int> FlrWallBeam(int iFlr, int Num);
// 墙梁层号
int WallBeamFlr(int WBID);
// 墙梁塔号
int WallBeamTow(int WBID);
// 裙房墙梁关联上方塔号
int QFWallBeamTow(int WBID);
// 墙梁的层内编号
int WallBeamIDInFlr(int WBID);
// 墙梁所属的结构模型墙号
int WallBeamONO(int WBID);
// 弧形墙梁圆心
int WallBeamArcCen(int WBID, ref float xc, ref float yc, ref float zc);
// 墙梁高度
float WallBeamH(int WBID);
float WallBeamUH(int WBID);
float WallBeamDH(int WBID);
// 墙梁宽度
float WallBeamB(int WBID);
// 墙梁材料类型及标号
void WallBeamMat(int WBID, ref int matType, ref float matGrade, ref float matGrade2);
// 墙梁主筋等级
int WallBeamMainStl(int WBID);
// 墙梁箍筋等级
int WallBeamHoopStl(int WBID);
// 墙梁保护层厚度
int WallBeamStlCover(int WBID);
// 墙梁抗震等级
int WallBeamKZDJ(int WBID);
// 墙梁抗震构造措施的抗震等级
int WallBeamGZKZDJ(int WBID);
// 墙梁刚度折减系数
float WallBeamGDZJ(int WBID);
// 墙梁刚度折减系数(风荷载)
float WallBeamGDZJW(int WBID);
// 返回1为交叉配筋 2为斜撑配筋 3为对角斜筋
int WallBeamStlType(int WBID);
// 钢板剪力墙钢板厚度
int WallBeamStlThick(int WBID);
// 墙梁活荷折减系数
float WallBeamHHZJXS(int WBID);
// 墙梁活荷重力荷载代表值组合系数
float WallBeamHHGEXS(int WBID);
// 包络设计墙梁
int IsWBEnvelope(int gjID);
// 墙梁重要性系数
float WallBeamEta(int WBID);
// 人防构件
int IsWBAd(int WBID);
// 按高规进行性能设计时的构件类型 1:关键 2:普通竖向 3:耗能
int WallBeamPerformType(int WBID);
// 是否按实体单元计算
int IsWBSolid(int WBID);
// 梁内钢板宽高
int WallBeamStlBH(int WBID, ref int b, ref int h);
// 是否考虑竖向地震
int IsWBVE(int WBID);
// 某层墙柱数
int NWallColumn(int iFlr);
// 某层墙柱编号
List<int> FlrWallColumn(int iFlr, int Num);
// 墙柱层号
int WallColumnFlr(int WCID);
// 墙柱塔号
int WallColumnTow(int WCID);
// 裙房墙柱关联上方塔号
int QFWallColumnTow(int WCID);
// 墙柱的层内编号
int WallColumnIDInFlr(int WCID);
// 弧形墙柱圆心
int WallColumnArcCen(int WCID, ref float xc, ref float yc, ref float zc);
// 墙柱截面高度
float WallColumnL(int WCID);
// 墙柱厚度
float WallColumnB(int WCID);
// 墙柱底部厚度
float WallColumnBDw(int WCID);
// 墙柱竖向高度
float WallColumnH(int WCID);
// 墙柱材料类型及标号
void WallColumnMat(int WCID, ref int matType, ref float matGrade,
ref float matGrade2);
// 墙柱抗震等级
int WallColumnKZDJ(int WCID);
// 返回墙的角点全楼ID
Tuple<int, int> WallColumnJDUP(int WCID);
// 墙柱主筋等级
int WallColumnMainStl(int WCID);
// 墙柱水平分布筋等级
int WallColumnDsStl(int WCID);
// 墙柱竖向分布筋等级
int WallColumnVDsStl(int WCID);
// 边缘构件箍筋
int WallEdgeHoopStl(int WCID);
// 墙柱竖向分布筋配筋率
float WallColumnRou(int WCID);
// 墙柱水平分布筋配筋率
float WallColumnHRou(int WCID);
// 墙柱钢筋保护层
int WallColumnStlCover(int WCID);
// 墙角点ID(LB, RB, RT, LT)
void WallCorner(int WAID, ref int[] cornerID);
// 实体墙面外内力积分线信息
int SolWaIntLinesNum(int waID);
void SolWaIntLine(IN int waID, IN int lineno, ref int lineid, ref int njd, ref int[] jd);
// 钢板剪力墙钢板厚度
int WallColumnStlThick(int WCID);
// 墙柱活荷折减系数
float WallColumnHHZJXS(int WCID);
// 墙柱活荷重力荷载代表值组合系数
float WallColumnHHGEXS(int WCID);
// 墙柱是否有面外荷载
int WallColumnMWHZ(int WCID);
// 包络设计墙柱
int IsWCEnvelope(int gjID);
// 墙柱重要性系数
float WallColumnEta(int WCID);
// 人防构件
int IsWCAd(int WCID);
// 按高规进行性能设计时的构件类型 1:关键 2:普通竖向 3:耗能
int WallColumnPerformType(int WCID);
// 是否按实体单元计算
int IsWCSolid(int WCID);
// 是否考虑竖向地震
int IsWCVE(int WCID);
// 按抗规进行性能设计时的性能水准 (0不考虑 1不屈服 2弹性 3屈服) zz中震 zjm正截面
void WCPerLvl(int WCID, ref int zzzjm, ref int zzxjm, ref int dzzjm, ref int dzxjm);
// 获取墙梁温差 1:升温 2:降温 3:防火升温
void WCTemp(int WCID, ref float[] temp);
// 美规墙柱延性等级
int WCDuct(int WCID);
// 面外设计墙
int WCMianwai(int WCID);
// 结构重要性系数
float WCGama0(int WCID);
// 实配钢筋超配系数
float WCCPXS(int WCID);
// 交叉斜筋数量,等级,直径,与水平方向夹角
int WCXStl(int WCID, ref int stlNum, ref int stlGrd,
ref int stlDia, ref float stlAng);
// 墙柱安全性鉴定信息(type=1:主要构件 2:一般构件, coef:局部承载力折减系数 seisCoef:抗震鉴定承载力折减系数)
void WCSafe(int WCID, ref int type, ref float coef, ref float seisCoef);
// 某层弹性板数
int NSlab(int iFlr);
// 楼层弹性板编号
List<int> FlrSlab(int iFlr, int Num);
// 弹性板层号
int SlabFlr(int slabID);
// 弹性板塔号
int SlabTow(int slabID);
// 弹性板结构模型编号
int SlabONO(int slabID);
// 弹性板材料类型及标号
void SlabMat(int slabID, ref int matType, ref float matGrade,
ref float matGrade2);
// 是否为蒙皮
int IsSlabSkin(int slabID);
// 人防构件
int IsSlabAd(int slabID);
// 板包含的单元总数
int NSlabPlanar(int slabID);
// 是否按实体单元计算
int IsSlabSolid(int slabID);
// 是否基础板
int IsBaseSlab(int slabID);
// 连接信息
// 楼层连接数
int NLink(int iFlr);
// 楼层弹性板编号
List<int> FlrLink(int iFlr, int Num);
// 连接层号(定义在结构底部的连接属性层号返回0)
int LinkFlr(int linkID);
// 连接塔号
int LinkTow(int linkID);
// 连接结构模型编号
int LinkONO(int linkID);
// 连接对应的斜杆ID(用于判断是否为斜杆定义的连接属性)
int LinkToBrace(int linkID);
// 连接两端节点ID(若其中一端为0则为支座节点)
void LinkNode(int linkID, ref int j1, ref int j2);
// 连接类型
// _LP_LINEAR = 1;			// 线性
// _LP_DAMPER_MAXWELL = 2;	// 阻尼器麦克斯韦模型
// _LP_ISOLATOR1 = 3;		// 隔震支座
// _LP_WEN = 6;				// 塑性单元
// _LP_GAP = 7;				// GAP单元
// _LP_BRB = 8;				// 屈曲约束支撑
// _LP_DAMPER_KELVIN = 9;	// 阻尼器开尔文模型
// _LP_ISOLATOR_FRC = 10;	// 摩擦摆型隔震支座
int LinkType(int linkID);
// dia:有效直径mm
// diaHole:中孔直径mm
// rubThick:橡胶总厚度mm
// hTotal:隔震器+连接板总高度mm
// shp1:一次形状系数
// shp2:二次形状系数
// calcM:计算附加弯矩
int LinkPara(int linkID, ref float dia, ref float diaHole, ref float rubThick,
ref float hTotal, ref float shp1, ref float shp2, ref int calcM);
// 隔震支座屈服力
int IsoYieldForce(int linkID, ref float u2, ref float u3);
// 隔震支座截面积
int IsoArea(int linkID, ref float area);
// 更多的连接属性参数
// [0] u1刚度
// [1] u2刚度
// [2] u3刚度
// [3] u2屈服后刚度比/摩擦摆-快摩擦系数
// [4] u3屈服后刚度比/摩擦摆-快摩擦系数
// [5] u2摩擦摆-慢摩擦系数
// [6] u3摩擦摆-慢摩擦系数
// [7] u2摩擦摆-摩擦系数变化率(s/m)
// [8] u3摩擦摆-摩擦系数变化率(s/m)
// [9] u2摩擦摆-摩擦面曲率半径(m)
// [10]u3摩擦摆-摩擦面曲率半径(m)
void LinkParaEx(int linkID, ref float[] pLinkParaEx);
// 连接名称
string LinkName(int linkID);
// 楼层两点弹性连接数
int NNodeELink(int iFlr);
// 楼层两点弹性连接编号(结构底部节点定义的连接属性归入1层)
List<int> FlrNodeELink(int iFlr, int Num);
// 连接层号(定义在结构底部的连接属性层号返回0)
int ELinkFlr(int linkID);
// 连接塔号
int ELinkTow(int linkID);
// 连接结构模型编号
int ELinkONO(int linkID);
// 连接两端节点ID(若其中一端为0则为支座节点)
void ELinkNode(int linkID, ref int j1, ref int j2);
// 桩ID对应的弹簧ID
int PileSpring(int pileID);
// 获取当前模型类型
//enum {
//	EMODNULL = 0, EMODNORMAL=1/*原始模型*/, EMODTOWER=2/*多塔拆分或门刚分榀*/, EMODPD=3/*性能设计*/,
//	EMODQT3D=4/*性能设计*/, EMODSQKJ=5/*少墙框架*/, EPOOLELAS=6/*水池模块弹性模型*/
//};
int CurModelKind();
private:
CToSDesign* m_CToSDesign;
};
public class Hi_StowExp	// 此类包含楼层信息的相关参数及塔数据定义
{
public:
// 塔参数(负值表示默认值)
float _cCL;	// 柱混凝土强度等级
float _cBE;	// 梁混凝土强度等级
float _cWA;	// 墙混凝土强度等级
float _cSB;	// 板混凝土强度等级
float _cBR;	// 支撑混凝土强度等级
long _stl;	// 钢号
int _h;		// 塔高
float _q;	// 塔底标高
char _JQC;	// 加强层
char _DBJQQ;// 底部加强区
char _GDC;	// 过渡层
char _YBZ;	// 约束边缘构件
char _XTL;	// 顶部小塔楼
char _ROOF;	// 主要屋面层
int _sCLMain;	// 柱主筋
int _sBEMain;	// 梁主筋
int _sWAMain;	// 墙主筋
int _sCLHoop;	// 柱箍筋
int _sBEHoop;	// 梁箍筋
int _sWAHoop;	// 边缘构件箍筋
int _sWAHStl;	// 墙水平筋
int _sWAVStl;	// 墙分布筋
float _rohWAVStl;	// 墙竖向分布筋配筋率
float _rohWAHStl;	// 墙水平分布筋配筋率
int _kzdjCL;		// 柱抗震等级
int _kzdjBEMain;	// 主梁抗震等级
int _kzdjBESub;		// 次梁抗震等级
int _kzdjWA;		// 墙抗震等级
int _kzdjBR;		// 斜杆抗震等级
int _gzkzdjCL;		// 柱抗震构造等级
int _gzkzdjBEMain;	// 主梁抗震构造等级
int _gzkzdjBESub;	// 次梁抗震构造等级
int _gzkzdjWA;		// 墙抗震构造等级
int _gzkzdjBR;		// 斜杆抗震构造等级
int _kzdjSCL;		// 钢柱抗震等级
int _kzdjSBEMain;	// 钢主梁抗震等级
int _kzdjSBESub;	// 钢次梁抗震等级
int _kzdjSBR;		// 钢斜杆抗震等级
int _gzkzdjSCL;		// 钢柱抗震构造等级
int _gzkzdjSBEMain;	// 钢主梁抗震构造等级
int _gzkzdjSBESub;	// 钢次梁抗震构造等级
int _gzkzdjSBR;		// 钢斜杆抗震构造等级
float _cpxsCL;		// 混凝土柱超配系数
float _cpxsBE;		// 混凝土梁超配系数
float _cpxsWC;		// 墙柱超配系数
float _cpxsWB;		// 墙梁超配系数
float _cpxsBR;		// 斜杆超配系数
int _calcIdx;		// 指标统计开关
float _gama;		// 结构重要性系数
int _stlCl;			// 柱钢号
int _stlBe;			// 梁钢号
int _stlWa;			// 墙钢号
int _stlBr;			// 支撑钢号
int _fz; 			// 塔所在自然层号
long _no; 			// 塔号
int _orino; 			// 当有交互输入信息时,临时记录该塔原始塔号,不存盘
List<Tuple<float, float>^>^ _poly; 		// 塔多边形范围
List<Tuple<int, int>^>^ _up;			// 塔关联的上塔
List<Tuple<int, int>^>^ _dw; 			// 塔关联的下塔
};
public class Hi_StrucTowerInfo 	// 此类包含塔信息的对外接口
{
public:
Hi_StrucTowerInfo();
//加载
void Load();
//保存
void Save();
// 新增塔数据(zrc为楼层的编号)
void addTower(Hi_STowExp^ tow，int zrc);
// 获取某一塔某一自然层的塔数据定义
Hi_STowExp^ getTower(int zrc, int tow);
// 构件施工次序
void SetCompOrder(int zrcId, int compId, int order); // zrcId自然层ID、compId构件ID、order施工顺序
int GetCompOrder(int zrcId, int compId); // 0 失败; >0 次序号
//自动生成多塔数据
void AutoGen();
//获取所有存在的塔号
int GetTowNO();
//获得某一自然层的塔编号
List<int>^ GetFzTower(int zrcId);
};
public class Hi_JSCS 	// 此类包含计算参数设置相关的接口
{
public:
// 计算参数表_整数类型参数
void SetSParInt(int paraID, const int val);
// 计算参数表_浮点数类型参数
void SetSParFloat(int paraID, const float val);
// 计算参数表_整型数组类型参数
void SetSParIntArray(int paraID, ref int[] val);
// 计算参数表_浮点数组类型参数
void SetSParFloatArray(int paraID, ref float [] val);
// 保存前处理参数
void SParaSave();
//获取前处理参数(Int型)
string GetSParaInt(int paraID);
//获取前处理参数(Float型)
string GetSParaFlt(int paraID);
//获取前处理参数(浮点数组)
List<float>^ GetSParaFltArray(int paraID);
//获取前处理参数(整型数组)
List<int>^ GetSParaIntArray(int paraID);
//重新读取.par文件
void yjkSParaFileReload();
};
public class Hi_Temperature 	// 此类包含温度设置相关的接口
{
public:
//全楼统一温度荷载
void UniTemp(float fTemp1, float fTemp2);
// 数据存取
void Load();
// 数据存取
void Save();
// 重置所有系数
void Clear();
};
public class Hi_ColumnCalcLengthCoefExp
{
public:
// 重置所有系数
void Clear();
// 数据存取
void Load();
void Save();
// 是否交互指定的长度系数
bool IsManual(int zrcId, int compId);
// 柱有侧移计算长度系数
void SetColMuSway(int zrcId, int clId, List<Mdl_SColCalcLen^>^ mux, List<Mdl_SColCalcLen^>^ muy);
int GetColMuSway(int zrcId, int clId, List<Mdl_SColCalcLen^>^% mux, List<Mdl_SColCalcLen^>^% muy);
// 柱无侧移计算长度系数
void SetColMuNsway(int zrcId, int clId, List<Mdl_SColCalcLen^>^ mux, List<Mdl_SColCalcLen^>^ muy);
int GetColMuNsway(int zrcId, int clId, List<Mdl_SColCalcLen^>^% mux, List<Mdl_SColCalcLen^>^% muy);
// 支撑长度系数
void SetBraceMu(int zrcId, int brId, double mux, double muy);
int GetBraceMu(int zrcId, int brId, double% mux, double% muy);
// 梁面外长度
void SetBeamSideLen(int zrcId, int beId, float beamSideLen);
int GetBeamSideLen(int zrcId, int beId, float% beamSideLen);
// 梁a/Hw
void SetBeClAHw(int zrcId, int beId, float beClAHw);
int GetBeClAHw(int zrcId, int beId, float% beClAHw);
// 墙计算高度
// zrcId:建模的自然层ID
// waId:建模的墙ID
// hl:墙洞左侧（如果没有墙洞则取hl）
// hr:墙洞右侧
void SetWallCalcH(int zrcId, int waId, float hl, float hr);
int GetWallCalcH(int zrcId, int waId, float% hl, float% hr);
};
计算参数ID对应表
结构总体信息

| 项名称 | 宏定义（id号） | 输入参数类型 | 额外说明 |
|---|---|---|---|
| 结构体系 | YP_JGTX（101） | Int | 框架结构（10101） 框剪结构（10102） 框筒结构（10103） 筒中筒结构（10104） 剪力墙结构（10105） 框支剪力墙结构（10106） 板柱-剪力墙结构（10107） 异形柱框架结构（10108） 异形柱框剪结构（10109） 配筋砌块砌体结构（10110） 砌体结构（10111） 底框结构（10112） 钢框架-中心支撑结构（10113） 钢框架-偏心支撑结构（10114） 单层工业厂房（10115） 多层钢结构厂房（10116） 竖向框排架（10117） TUS剪力墙结构（10118） 变电构架结构（10119） 温室结构（10120） 低层冷弯薄壁房屋（10121） 波纹钢板组合框架（10122） 波纹钢板组合框架-支撑（10123） 全框支剪力墙结构（10124） 矩形柱组合框架结构(渝建) （10125） 矩形柱组合框架结构_支撑(渝建) （10126） 门式刚架结构（10127） |
| 结构材料 | YP_JGCL（103） | Int | 钢筋混凝土（10301） 钢与混凝土混合结构（10302） 钢结构（10303） 砌体结构（10304） |
| 结构所在地区 | YP_AREA（102） | Int |  |
| 地下室层数 | YP_DXS（106） | Int |  |
| 嵌固端所在层号 （层顶嵌固） | YP_KGC（108） | Int | 对应白色框填入的数值（其余白色数值框相同） |
| 与基础相连构件最大底标高（m） | YP_FIXELE（109） | Float |  |
| 裙房层数 | YP_QFCS（104） | Int |  |
| 转换层所在层号 | YP_ZHC（105） | Int |  |
| 加强层所在层号 | YP_JQC（107） | Int |  |
| 底框层数 | YP_NDKC（1110） | Int |  |
| 施工模拟加载层步长 | YP_SGSTEP（635） | Int |  |
| 恒活荷载计算信息 | YP_SGMN（601） | Int | 不计算恒活荷载（60101） 一次性加载（60102） 施工模拟一（60103） 施工模拟二（60104） 施工模拟三（60105） |
| 风荷载计算信息 | YP_WTYPE（603） | Int | 不计算风荷载（60301） 普通方式计算（60302） 精细方式计算（60303） 计算水平和特殊风荷载(无用)（60304） 按构件档风面积计算（60305） |
| 地震作用计算信息 | YP_SEISTYPE（604） | Int | 不计算地震作用（60401） 计算水平地震作用（60402） 计算水平和规范简化方法竖向地震作用（60403） 计算水平和反应谱法竖向地震作用(整体求解)（60404） 计算水平和反应谱法竖向地震作用(独立求解)（60405） 计算水平和反应谱法竖向地震作用（局部模型独立求解）（60406） |
| 计算吊车荷载 | YP_JS_DCHZ（617） | Int | 填入0指不打勾，填入1指打勾（其余打勾框相同） |
| 计算人防荷载 | YP_JS_RFHZ（623） | Int |  |
| 考虑预应力等效荷载工况 | YP_JSKLYYL（125） | Int |  |
| 生成传给基础的刚度 | YP_JS_JCGD（618） | Int |  |
| 凝聚局部楼层刚度时考虑的底部层数（0表示全部楼层） | YP_JS_JCGDFLR（116） | Int |  |
| 上部结构计算考虑基础结构 | YP_JSKLJC（124） | Int |  |
| 生成绘等值线用数据 | YP_JS_DZX（114） | Int |  |
| 计算温度荷载 | YP_JS_WDHZ（113） | Int |  |
| 考虑收缩徐变的砼构件温度效应折减系数 | YP_WDZJXS（115） | Int |  |
| 竖向荷载下砼墙轴向刚度考虑徐变收缩影响墙刚度折减系数 | YP_QGDZJXS（123） | Float |  |
| 考虑填充墙刚度 | YP_KLTCQGD（680） | Int |  |
| 采用通用规范 | YP_TYGF（126） | Int |  |

计算控制信息_控制信息

| 项名称 | 宏定义（id号） | 输入参数类型 | 额外说明 |
|---|---|---|---|
| 水平力与整体坐标夹角 | YP_HFANG（622） | Float |  |
| 连梁按墙元计算控制跨高比 | YP_LL2WKGB（629） | Float |  |
| 普通梁连梁砼等级默认同墙 | YP_LLWAC（119） | Int |  |
| 墙元细分最大控制长度（m） | YP_MESHLEN（605） | Float |  |
| 板元细分最大控制长度（m） | YP_MESHLENB（637） | Float |  |
| 短墙肢自动加密 | YP_DQJM（640） | Int |  |
| 弹性板荷载计算方式 | YP_ESLABLOAD（118） | Int | 平面导荷(11801) 有限元计算（11802） |
| 膜单元类型 | YP_MEMTYPE（657） | Int | 经典膜元(QA4)（65701） 改进膜元(NQ6Star)（65702） |
| 考虑梁端刚域 | YP_LZGY（609） | Int |  |
| 考虑柱端刚域 | YP_ZDGY（650） | Int |  |
| 墙梁跨中节点作为刚性楼板从节点 | YP_QLKZCJD（639） | Int |  |
| 梁与弹性板变形协调 | YP_LBBXXT（646） | Int |  |
| 弹性板与梁协调时考虑梁向下相对偏移 | YP_LBXTOFFSET（649） | Int |  |
| 刚性楼板假定 | YP_QZGXLB（606） | Int | 一、二、三个选项分别对应0，1，2的输入值（其余分选项处相同） |
| 地下室楼板强制采用刚性楼板假定 | YP_QZGXLBDXS（638） | Int |  |
| 自动划分多塔 | YP_ATOW（626） | Int |  |
| 自动划分不考虑地下室 | YP_DXSNATOW（636） | Int |  |
| 可确定最多塔的参考层号 | YP_ATOWFLR（634） | Int |  |
| 各分塔与整体分别计算，配筋取各芬塔与整体结果较大值 | YP_ASPTOW（625） | Int |  |
| 计算现浇空心板 | YP_JSXJKXB（645） | Int |  |
| 现浇空心板计算方法 | YP_XJKXB（644） | Int |  |
| 增加计算连梁刚度不折减模型下的地震位移 | YP_JSWY_LLBZJ（643） | Int |  |
| 梁墙自重扣除与柱重叠部分 | YP_LQZZKZD（651） | Int |  |
| 楼板自重扣除与梁墙重叠部分 | YP_BZZKL（659） | Int |  |
| 输出节点位移 | YP_JS_WDISP（624） | Int |  |
| 地震内力按全楼弹性板6计算 | YP_EFORCEBYESLAB6（660） | Int |  |
| 结构计算时考虑楼梯刚度 | YP_LTGD（641） | Int |  |
| 门式刚架按平面结构方式计算 | YP_MGCALCBYPLAN（685） | Int |  |

计算控制信息_刚度系数

| 项名称 | 宏定义（id号） | 输入参数类型 | 额外说明 |
|---|---|---|---|
| 竖向荷载梁刚度放大系数按10《砼规》5.2.4条取值 | YP_ZLFD10（630） | Int |  |
| 竖向荷载梁刚度放大系数上限 | YP_ZLFD10M（631） | Float |  |
| 竖向荷载中梁刚度放大系数 | YP_ZLFD（611） | Float |  |
| 竖向荷载边梁刚度放大系数上限 | YP_BLFD（663） | Float |  |
| 控制地震荷载下边、中梁放大系数 | YP_ZLFDEUSE（696） | Int |  |
| 地震作用中梁刚度放大系数 | YP_ZLFDE（694） | Float |  |
| 地震作用边梁刚度放大系数 | YP_BLFDM_SEIS_GDXS（2305） | Float |  |
| 地震作用连梁刚度折减系数 | YP_LLZJ（610） | Float |  |
| 控制风荷载下边、中梁放大系数 | YP_WIND_GDXS（2308） | Int |  |
| 风荷载中梁刚度放大系数 | YP_ZLFD_WIND_GDXS（2306） | Float |  |
| 风荷载边梁刚度放大系数 | YP_BLFDM_WIND_GDXS（2307） | Float |  |
| 风荷载连梁刚度折减系数 | YP_LLZJW（658） | Float |  |

计算控制信息_二阶效应

| 项名称 | 宏定义（id号） | 输入参数类型 | 额外说明 |
|---|---|---|---|
| 考虑P-Delta效应 | YP_PDELTA（608） | Int |  |
| 组合系数：恒载 | YP_PDELTAXSD（652） | Float |  |
| 组合系数：活载 | YP_PDELTAXSL（653） | Float |  |
| 迭代次数[0，100] | YP_PDELTADDCS（681） | Int |  |
| 收敛误差[0.0001，0.2] | YP_PDELTASLWC（682） | Float |  |
| 考虑整体缺陷 | YP_CSQXTYPE（679） | Int |  |
| 对应的屈曲模态号 | YP_CSQXMOD（665） | Int |  |
| 最大缺陷值（mm） | YP_CSQXMAXDIS（666） | Int |  |
| 方向 | YP_CSQXDIR（668） | Int |  |
| 计算长度系数置为1 | YP_CALLENR1（667） | Int |  |
| 考虑梁元P-Delta效应 | YP_PDELTAL（697） | Int |  |
| 进行屈曲分析 | YP_BUCKLING（654） | Int |  |
| 迭代次数[0，100] | YP_BUCKDZCS（661） | Int |  |
| 收敛误差[0.0001，0.2] | YP_BUCKSLWC（662） | Float |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |

计算控制信息_分析求解参数

| 项名称 | 宏定义（id号） | 输入参数类型 | 额外说明 |
|---|---|---|---|
| 启用并行求解器 | YP_MULTITHREADED(2301) | Int |  |
| 使用cpu核心数量（0为自动） | YP_CPUNUM(2302) | Int |  |
| 设定内存（0MB，0为自动） | YP_MEMSET(669) | Int |  |
| 自定义控制参数 | YP_CUSTOMSET(2303) | Int |  |
| 求解器类型 | YP_SOLVERTYPE(2304) | Int | CSFD（230401） Pardiso Direct（230402） Pardiso Interaive（230403） Pardiso Couple（230404） |
| 加载步骤数量 | YP_FXXJZBZSL(688) | Int |  |
| 迭代次数[0，100] | YP_FXXDDCS(683) | Int |  |
| 位移控制开关 | YP_FXXSL_WYKZ(691) | Int |  |
| 位移控制数值 | YP_FXXSL_WYKZVAL(692) | Float |  |
| 荷载控制开关 | YP_FXXSL_HZKZ(693) | Int |  |
| 荷载控制数值 | YP_FXXSLWC(684) | Float |  |

风荷载信息

| 项名称 | 宏定义（id号） | 输入参数类型 | 额外说明 |
|---|---|---|---|
| 执行规范 | YP_WINDCODE | Int |  |
| 地面粗糙度类别 | YP_DMCCD(201) | Int |  |
| 修正后的基本风压 | YP_JBFY(202) | Float |  |
| 风荷载计算用阻尼比 | YP_WINDZNB(205) | Float |  |
| 结构X向基本周期 | YP_JBZQX(203) | Float |  |
| 结构Y向基本周期 | YP_JBZQY(204) | Float |  |
| 承载力设计时风荷载效应放大系数 | YP_WINDFD(913) | Float |  |
| 舒适度验算参数_风压 | YP_SSDFY(219) | Float |  |
| 舒适度验算参数_结构阻尼比 | YP_SSDWDZNB(220) | Float |  |
| 体型分段数 | YP_NTSFTX(212) | Int |  |
| 体型分段层号 | YP_NTSFTX(213) | Int[] | [0]分段数量 [1]第一段最高层号（0为未设置） [2]第二段最高层号（0为未设置） [3]第三段最高层号（0为未设置） |
| 风荷载体型系数_X向 | YP_TSFTX(214) | Float [] | [0]数组长度 [1]第一段X挡风 [2]第一段X迎风面 [3]第一段X背风面 [4]第一段X侧风面 (有二三段则往后补充) |
| 风荷载体型系数_Y向 | YP_TSFTXY(252) | Float [] | [0]数组长度 [1]第一段Y挡风 [2]第一段Y迎风面 [3]第一段Y背风面 [4]第一段Y侧风面 (有二三段则往后补充) |
| 精细计算方式下对柱按柱间均布风荷加载 | YP_COLLDEQ(251) | Int |  |
| 考虑顺风向风振 | YP_FZXS(206) | Int |  |
| 其它风向角度 | YP_DFXF(217) | Int |  |
| 程序自动计算 | YP_WINDDB(225) | Int |  |
| BX（m） | YP_WINDBX(226) | Float |  |
| BY（m） | YP_WINDBY(227) | Float |  |
| 考虑横向风振 | YP_HXFZ (207) | Int |  |
| 截面形状 | YP_WINDSECT(228) | Int | 矩形（22801） 凹角矩形（22802） 削角矩形（22803） 圆形（22804） |
| 凹角矩形_bX | YP_WINDJYX(229) | Float |  |
| 凹角矩形_bY | YP_WINDJYY(230) | Float |  |
| 圆形截面_结构二阶平动周期 | YP_WINDT2(231) | Float |  |
| 考虑扭转风振 | YP_NZFZ(222) | Int |  |
| 结构一阶扭 转周期 | YP_WINDTT(232) | Float |  |

计算控制信息_指定风荷载
地震信息

| 项名称 | 宏定义（id号） | 输入参数类型 | 额外说明 |
|---|---|---|---|
| 设计地震分组 | YP_SEISGP（301） | Int |  |
| 按新区划图计算 | YP_USENEWQHT（374） | Int |  |
| 设防烈度 | YP_SFLD（302） | Int |  |
| 场地类别 | YP_CDLB（303） | Int |  |
| 特征周期 | YP_TG（312） | Float |  |
| 周期折减系数 | YP_ZQZJ（310） | Float |  |
| 特征值分析参数 _分析类型 | YP_TZZTYPE（324） | Int |  |
| 用户定义/程序自动确定振型数 | YP_AUTOMODENUM(319) | Int |  |
| 用户定义振型数个数 | YP_CUSTOM_MAXMODENUM(322) | Int |  |
| 质量参与系数之和 | YP_ZLCYXS(321) | Int |  |
| 最多振型数量 | YP_MAXMODENUM(323) | Int |  |
| 按主振型确定地震内力符号 | YP_DZNLFH(335) | Int |  |
| 砼框架抗震等级 | YP_KJKZDJ(701) | Int |  |
| 剪力墙抗震等级 | YP_JLQKZDJ(703) | Int |  |
| 钢框架抗震等级 | YP_GKJKZDJ(702) | Int |  |
| 抗震构造措施的抗震等级 | YP_GZKZDJ (704) | Int |  |
| 框支剪力墙结构底部加强区剪力墙抗震等级自动提高一级 | YP_482_3(506) | Int |  |
| 地下一层以下抗震构造措施的抗震等级逐层降低及抗震措施四级 | YP_DXSKZDJ(345) | Int |  |
| 局部模型反应谱法计算竖向地震时 考熊求平质量 | YP_JBMXFYPKLSPZL(373) | Int |  |
| 结构阻尼比设置方法 | YP_DAMPTYPE(325) | Int | 全楼统一 32501 按材料区分 32502 |
| 结构阻尼比_全楼统一填入值 | YP_DAMP(311) | Float |  |
| 结构阻尼比_按材料区分 | YP_DAMPMATNUM(328) YP_DAMPMATIDS(329) | Float[] |  |
| 考虑偶然偏心 | YP_ORPX(304) | Int |  |
| X向偶然偏心 | YP_ORPXX(305) | Float |  |
| Y向偶然偏心 | YP_ORPXY(306) | Float |  |
| 偶然偏心计算方法 | YP_ORPXM(318) | Int | 等效扭矩法(传统法) 31801 瑞利-里兹投影反射谱法(新算法) 31802 |
| 考虑双向地震作用 | YP_SXDZ(307) | Int |  |
| 自动计算最不利地震方向的地震作用 | YP_IZBLDZFX(317) | Int |  |
| 斜交抗侧力构件方向角度 | YP_XJKCL(316) | Float[] |  |
| 活荷载重力荷载代表值组合系数 | YP_HHDBZXS(309) | Float |  |
| 地震影响系数最大值 | YP_AMAX(313) | Float |  |
| 用于12层以下规则砼框架结构薄层 验算的地震影响系数最大值 | YP_AMAXHY(314) | Float |  |
| 竖向地震作用系数底线值 | YP_SXDZDXZ(320) | Float |  |
| 地震计算时不考虑地下室的结构质量 | YP_ZZBKLDXZL(346) | Int |  |

地震信息_地震作用放大系数

| 项名称 | 宏定义（id号） | 输入参数类型 | 额外说明 |
|---|---|---|---|
| 全楼统一地震作用放大系数 | YP_DZFD(513) | Float |  |

地震信息_性能设计

| 项名称 | 宏定义（id号） | 输入参数类型 | 额外说明 |
|---|---|---|---|
| 考虑性能设计 | YP_ISXNSJ(1607) | Int |  |
| 地震水准 | YP_SEISLEVEL(1603) | Int |  |
| 性能设计按何种规定考虑 | YP_XNSJGD(1601) | Int | 按全国抗规考虑性能设计(160101) 按广东规程考虑性能设计(160102) 按高规考虑性能设计 (160103) 按深圳高规考虑性能设计(160104) |
| 性能设计（抗规）_正截面 | YP_XNSJ(705) | Int | 不屈服(70502) 弹性(70503) |
| 性能设计（抗规）_斜截面 | YP_XNSJXJM(1608) | Int | 不屈服(70502) 弹性(70503) |
| 性能水准 | YP_XNLEVEL(1602) | Int | 1(160201) 2(160202) 3(160203) 4(160204) 5(160205) |
| 关键构件系数 | YP_GJGJXS(1604) | Float |  |
| 一般竖向构件系数 | YP_YBSXGJXS(1605) | Float |  |
| 水平耗能构件系数（框架梁） | YP_SPHNGJXS(1606) | Float |  |
| 水平耗能构件系数（连染） | YP_SPHNGJXSLL(1618) | Float |  |
| 考虑钢筋超强系数1.25 | YP_GJCQXS(1616) | Int |  |
| 按广东高规进行钢构件性能设计 | YP_XNSJGDGGJ(1617) | Int |  |
| 性能设计（《钢结构设计标准》（GB50017-2017）） | YP_GB50017_2017(752) | Int |  |
| 性能等级 | YP_XNLEVELSTL(1610) | Int | 1(161001) 2(161002) 3(161003) 4(161004) 5(161005) 6(161006) 7(161007) |
| 延性等级 | YP_XNYXLEVEL(1611) | Int | I(161101) II(161102) III(161103) IV(161104) V(161105) |
| 耗能构件抗弯刚度EI折减系数 | YP_HNGJEIZJXS(1612) | Float |  |
| 耗能构件轴向刚度EA折减系数 | YP_HNGJEAZJXS(1613) | Float |  |
| 耗能构件性能系数 | YP_HNGJXNXS(1614) | Float |  |
| 非耗能构件内力调整系数βe | YP_FHNGJTZXS(1615) | Float |  |

地震信息_性能包络设计

| 项名称 | 宏定义（id号） | 输入参数类型 | 额外说明 |
|---|---|---|---|
| 按照抗规方法进行性能包络设计 | YP_XNSJBL(2221) | Int | 0 按照高规方法进行性能包络设计。 1 按照抗规方法进行性能包络设计。 |
| 中震计算模型不屈服 | YP_BLZ_BQF(2222) | Int |  |
| 中震计算模型弹性 | YP_BLZ_TX(2223) | Int |  |
| 中震地震影响系数最大值 | YP_BLZ_MAXALPHA(2224) | Float |  |
| 周期折减系数 | YP_BLZ_ZQZJ(2225) | Float |  |
| 中震_不屈服_结构阻尼比_全楼统一 | YP_BLZBQF_DAMP(2232) | Float |  |
| 中震_不屈服_结构阻尼比_按材料区分 | YP_BLZBQF_DAMPMATIDS(2234) YP_BLZBQF_DAMPMATDAMPS(2235) | Float[] | 混凝土(6) 钢(5) 型钢砼(56) |
| 中震_不屈服_连梁刚度折减系数 | YP_BLZBQF_LLZJ(2236) | Float |  |
| 中震_不屈服_中梁刚度放大系数 | YP_BLZBQF_ZLFD(2237) | Float |  |
| 中震_不屈服_考虑双向地震作用 | YP_BLZBQF_SXDZ(2238) | Int |  |
| 中震_弹性_结构阻尼比设置类型 | YP_BLZTX_DAMPTYPE(2241) | Int | 全楼统一(32501) 按材料设置阻尼比(32502) |
| 中震_弹性_结构阻尼比_全楼统一 | YP_BLZTX_DAMP(2242) | Int |  |
| 中震_弹性_结构阻尼比_按材料区分 | YP_BLZTX_DAMPMATIDS(2244) YP_BLZTX_DAMPMATDAMPS(2245) | Float[] | 混凝土(6) 钢(5) 型钢砼(56) |
| 中震_弹性_连梁刚度折减系数 | YP_BLZTX_LLZJ(2246) | Float |  |
| 中震_弹性_中梁刚度放大系数 | YP_BLZTX_ZLFD(2247) | Float |  |
| 中震_弹性_考虑双向地震作用 | YP_BLZTX_SXDZ(2248) | Int |  |
| 大震计算模型不屈服 | YP_ISOLATD_BQF(2552) | Int |  |
| 大震计算模型弹性 | YP_ISOLATD_TX(2553) | Int |  |
| 大震地震影响系数最大值 | YP_ISOLATD_MAXALPHA(2554) | Float |  |
| 周期折减系数 | YP_ISOLATD_ZQZJ(2556) | Float |  |
| 特征周期 | YP_ISOLATD_TG(2555) | Float |  |
| 大震_不屈服_结构阻尼比设置类型 | YP_ISOLATDBQF_DAMPTYPE(2561) | Int | 全楼统一(32501) 按材料设置阻尼比(32502) |
| 大震_不屈服_结构阻尼比_全楼统一 | YP_ISOLATDBQF_DAMP(2562) | Float |  |
| 大震_不屈服_结构阻尼比_按材料区分 | YP_ISOLATDBQF_DAMPMATIDS(2564) YP_ISOLATDBQF_DAMPMATDAMPS (2565) | Int |  |
| 大震_不屈服_连梁刚度折减系数 | YP_ISOLATDBQF_LLZJ(2566) | Float |  |
| 大震_不屈服_中梁刚度放大系数 | YP_ISOLATDBQF_ZLFD(2567) | Float |  |
| 大震_不屈服_考虑双向地震作用 | YP_ISOLATDBQF_SXDZ(2568) | Int |  |
| 大震_弹性_结构阻尼比设置类型 | YP_ISOLATDTX_DAMPTYPE(2571) | Int | 全楼统一(32501) 按材料设置阻尼比(32502) |
| 大震_弹性_结构阻尼比_全楼统一 | YP_ISOLATDTX_DAMP(2572) | Float |  |
| 大震_弹性_结构阻尼比_按材料区分 | YP_ISOLATDTX_DAMPMATIDS(2574) YP_ISOLATDTX_DAMPMATDAMPS(2575) | Float[] |  |
| 大震_弹性_连梁刚度折减系数 | YP_ISOLATDTX_LLZJ(2576) | Float |  |
| 大震_弹性_中梁刚度放大系数 | YP_ISOLATDTX_ZLFD(2577) | Float |  |
| 大震_弹性_考虑双向地震作用 | YP_ISOLATDTX_SXDZ(2578) | Int |  |

地震信息_隔震减震

| 项名称 | 宏定义（id号） | 输入参数类型 | 额外说明 |
|---|---|---|---|
| 隔震 | YP_ISOLATSEIS(2501) | Int |  |
| 减震 | YP_ISOLATSEIS_JZ(2584) | Int |  |
| 隔震层数 | YP_ISOLATFLRNUM(2506) | Int |  |
| 隔震层层号 | YP_ISOLATFLRS(2507) | Int |  |
| 隔震结构设计方法 | YP_ISOLATDESIGNTYPE(2508) | Int |  |
| 调整后水平向减震系数 | YP_SPJZXS(350) | Float |  |
| 计算中震非隔震模型 | YP_ISOLATD_FGZMX(2583) | Int |  |
| 减震结构设计方法 | YP_ISOLATDESIGNTYPE_JZ(2585) | Int |  |
| 最大附加阻尼比 | YP_MAXADDDMPRATIO(337) | Float |  |
| 附加阻尼比折减系数 |  | Float |  |
| 考虑钢筋超强系数 | YP_GJCQXS(1616) | Int |  |
| 反应谱计算方法 | YP_FYPTYPE(2502) | Int |  |
| 减震隔震附加阻尼比算法 | YP_ADDDMPMETHOD(336) | Int | 强制解耦(33601) 能量法(33602) |
| 减隔震元件有效刚度和有效阻尼 | YP_ISOLATLINKTYPE(2505) | Int | 采用输入的等效线性属性(250501) 迭代确定(250502) 自动采用弹性里程计算结果(250503) |
| 大震计算模型是否不屈服 | YP_BLD_BQF(2252) | Int |  |
| 大震计算模型是否弹性 | YP_BLD_TX(2253) | Int |  |
| 大震地震影响系数最大值 | YP_BLD_MAXALPHA(2254) | Float |  |
| 周期折减系数 | YP_BLD_TG(2256) | Float |  |
| 特征周期 | YP_BLD_TG(2255) | Float |  |
| 不屈服_结构阻尼比设置类型 | YP_BLDBQF_DAMPTYPE | Int | 全楼统一(32501) 按材料区分(32502) |
| 不屈服_结构阻尼比_全楼统一 | YP_BLDBQF_DAMP(2262) | Float |  |
| 不屈服_结构阻尼比_按材料区分 | YP_BLDBQF_DAMPMATIDS(2264) YP_BLDBQF_DAMPMATDAMPS(2265) | Float[] |  |
| 连梁刚度折减系数 | YP_BLDBQF_LLZJ(2266) | Float |  |
| 中梁刚度放大系数 | YP_BLDBQF_ZLFD(2267) | Float |  |
| 考虑双向地震作用 | YP_BLDBQF_SXDZ(2268) | Int |  |
| 弹性_结构阻尼比设置类型 | YP_BLDTX_DAMPTYPE(2271) | Int | 全楼统一(32501) 按材料区分(32502) |
| 弹性_结构阻尼比_全楼统一 | YP_BLDTX_DAMP(2272) | Float |  |
| 弹性_结构阻尼比_按材料区分 | YP_BLDTX_DAMPMATIDS(2274) YP_BLDTX_DAMPMATDAMPS(2275) | Float[] |  |
| 连梁刚度折减系数 | YP_BLDTX_LLZJ(2276) | Float |  |
| 中梁刚度放大系数 | YP_BLDTX_ZLFD(2277) | Float |  |
| 考虑双向地震作用 | YP_BLDTX_SXDZ(2278) | Int |  |

设计信息

| 项名称 | 宏定义（id号） | 输入参数类型 | 额外说明 |
|---|---|---|---|
| 按规范调整地震内力 | YP_525(505) | Int |  |
| 扭转效应明显 | YP_525NZXY(523) | Int |  |
| 最小剪重比_自定义调整系数 | YP_IS525USER(531) | Float |  |
| 最小剪重比_设置调整系数 | YP_525USERDATA(532) | Float |  |
| 自动计算动位移比例 | YP_AUTOCALC525(544) | Float |  |
| 第一平动周期方向动位移比例 | YP_525RZ(520) | Float |  |
| 第二平动周期方向动位移比例 | YP_525QZ(521) | Float |  |
| 与柱相连的框架梁端M、V不调整 | YP_02V0NOBEAM(527) | Int |  |
| 调整方式 | YP_02V0Type(542) | Int | Min[alpha*Vo, beta*Vfmax](0) Max[alpha*Vo, beta*Vfmax](1) |
| α__楼层剪力V | YP_02V0Vratio(533) | Float |  |
| β__Vfmax | YP_02V0VfmaxRatio(534) | Float |  |
| 分段数 | YP_N02V0(514) | Int |  |
| 起始层号 | YP_02V0FLRB(515) | Int[] |  |
| 上限 | YP_MAX02V0(517) | Int |  |
| 终止层号 | YP_02V0FLRE(516) | Int[] |  |
| 考虑双向地震时内力调整方式 | YP_SXDZTZ(554) | Int | 先考虑双向地震再调整(55401) 先调整再考虑双向地震(55402) |
| 剪力墙端柱的面外剪力统计到框架部分 | YP_JLQDZJLTJDKJ(555) | Int |  |
| 实配钢筋超配系数 | YP_9ICPXS(508) | Float |  |
| 框支柱调整上限 | YP_MAXKZZ(518) | Float |  |
| 零应力区验算时底面尺寸确定方式 | YP_0YLQCALC(549) | Int | 零应力区验算时底面尺寸确定方式  质心到最近边距离的2倍(54901) 零应力区验算时底面尺寸确定方式  平面外包矩形边长(54902) |
| 按层刚度比判断薄弱层方法 | YP_BRCGDB(522) | Int | 高规和抗规从严(52201) 按高规(52202) 按抗规(52203) 不自动判断(52204) 按上海抗规剪切刚度比(52205) 按上海抗规剪弯刚度比(52206) |
| 底部嵌固楼层刚度比执行《高规》3.5.2-2 | YP_KGC_GG3522(526) | Int |  |
| 自动对层间受剪承载力突变形成的薄弱层放大调整 | YP_GG358(519) | Int |  |
| 自动根据层间受剪承载力比值调整配筋至非薄弱层 | YP_GG353(535) | Int |  |
| 层间受剪承载力比值 | YP_GG353BZ(556) | Float |  |
| 指定薄弱层层号 | YP_IBRC(510) | Int |  |
| 薄弱层地震内力放大系数 | YP_BRCDZFD(512) | Float |  |
| 梁端负弯矩调幅系数 | YP_TFXS(501) | Float |  |
| 框架梁调幅后不小于简支梁跨中弯矩__倍 | YP_KJLTFMRATIO(539) | Float |  |
| 非框架梁调幅后不小于简支梁跨中弯矩__倍 | YP_NKJLTFMRATIO (540) | Float |  |
| 梁扭矩折减系数 | YP_NJZJ(503) | Float |  |
| 转换结构构件、（三、四级）的水平地震作用效应放大系数 | YP_ZHGJDZFDXS(562) | Float |  |
| 支撑临界角度 | YP_BRACE2COLANG(530) | Int |  |
| 按竖向构件内力统计层水平荷载剪力位移角小于____时，位移比置1 | YP_WYBXZ(541) | Float |  |
| 剪力墙承担全部地震剪力 | YP_WALLALLSEIS(543) | Int |  |

活荷载信息

| 项名称 | 宏定义（id号） | 输入参数类型 | 额外说明 |
|---|---|---|---|
| 按建模菜单“房间属性”计算 | YP_HHZJBYPM(409) | Int |  |
| 设计时折减柱、墙活荷载 | YPE_ZQHHZJ (407) | Int |  |
| 计算截面以上层数的折减系数 | YP_ZQHHZJXS(404) | float[] |  |
| 楼面梁活荷载折减设置 | YP_LMLHHZJ(405) | Int | 不折减(40501) 从属面积超过25m2时，楼面活荷载折减0.9(40502) 从属面积超过50m2时，楼面活荷载折减0.9(40503) 单向板楼盖楼面活荷载折减0.6 (40504) 双向板楼盖楼面活荷载折减0.8 (40505) |
| 活荷不利布置最高层号 | YP_MAXHHBL(403) | Int |  |
| 梁活荷载内力放大系数 | YP_HHNLFD(502) | Float |  |

构件设计信息

| 项名称 | 宏定义（id号） | 输入参数类型 | 额外说明 |
|---|---|---|---|
| 柱配筋计算方法 | YP_ZPJ(708) | Int | 单偏压(70801) 双偏压(70802) |
| 双偏压时角筋最大直径 | YP_MAXCORBARD(745) | Int |  |
| 柱剪跨比计算方法 | YP_JHJSZJKB(724) | Int | 通用方法（0） 简化方法（1） |
| 连梁按对称配筋设计 | YP_LLDCPJ(716) | Int |  |
| 框架梁梁端配筋考虑受压钢筋影响 | YP_KJLYAJIN(713) | Int |  |
| 矩形混凝土梁按考虑楼板翼缘的T形梁配筋 | YP_RECT_T(715) | Int |  |
| 墙柱配筋设计考虑端柱 | YP_QZDZ(714) | Int |  |
| 墙柱配筋设计考虑翼缘墙 | YP_QZYYQ(723) | Int |  |
| 腹板墙最大截面高宽比 | YP_SPYFBQGKB(753) | Float |  |
| 腹板墙最大截面高度 | YP_SPYFBQGD(754) | Int |  |
| 与剪力墙面外相连的梁按框架梁设计 | YP_QLLISKJL(642) | Int |  |
| 验算一级抗震墙施工缝 | YP_YSKZQSGF(732) | Int |  |
| 受弯构件按压弯设计控制轴压比 | YP_LZLTJ(730) | Float |  |
| 梁端配筋内力取值位置（0~1） （0节点，1-支座边） | YP_LDNL2ZZB(731) | Int |  |
| 框架柱的轴压比限值按框架结构采用 | YP_ZZYBKJ(712) | Int |  |
| 不计算地震作用时，按重方荷载代表值计算柱轴压比 | YP_ZYBBYG(735) | Int |  |
| 保护层厚度（mm）梁 | YP_LBHC(709) | Int |  |
| 保护层厚度（mm）柱 | YP_ZBHC(710) | Int |  |
| 构造边缘构件设计执行高规7.2.16-4 | YP_72164(707) | Int |  |
| 约束边缘构件层全部设为约束边缘构件 | YP_DBJQQALLYBZ(725) | Int |  |
| 约束边缘构件判定采用底部加强区底层轴压比归入阴影区的入/2区最大长度 | YP_BYGJ_YSYYLENLC(727) | Int |  |
| 面外梁下生成暗柱边缘构件 | YP_BYGJ_LXAZ(726) | Int | 全不生成(0) 全都生成(1) 铰接梁不生成(2) |
| 边缘构件合并距离（mm） | YP_BYGJ_MINDIS(720) | Int |  |
| 短肢边缘构件合并距离（mm） | YP_DQBYGJZTPJ(722) | Int |  |
| 边缘构件尺寸取整模数（mm） | YP_BYGJ_MOD(721) | Int |  |
| 构造边缘构件尺寸设计依据 | YP_BYGJ_SZYJ(719) | Int | 《抗规》GB50011 第6.4.5条(71901) 《高规》JGJ3-2010 第7.2.16条(71902) 《砼规》GB50010-2010 第11.7.19条(71903) |
| 边缘构件尺寸依据《广东高规》设计 | YP_YSBYGJ_GD(733) | Int |  |
| 型钢混凝土构件设计 | YP_XGHNT(711) | Int | 《型钢混凝土组合结构技术规程》JGJ138-2001(71101) 《钢骨混凝土结构技术规程》YB9082-2006(71102) |
| 按边缘构件轮廓计算配筋 | YP_BYGJ_JSPJ(736) | Int |  |
| 异形柱配筋计算只考虑固定钢筋 | YP_YXZZKLGDJ(763) | Int |  |
| 按叠合柱设计的叠合比m | YP_DHZDHB(737) | Float |  |

构件设计信息_边缘构件设计信息
构件设计信息_钢构件设计信息

| 项名称 | 宏定义（id号） | 输入参数类型 | 额外说明 |
|---|---|---|---|
| 执行《高钢规》JGJ99-2015 | YP_JGJ99_2015(741) | Int |  |
| 钢结构防火验算钢构件截面净毛面积比 | YP_GJMB(807) | Float |  |
| 梁按压弯设计控制轴压比 | YP_LZLTJ(730) | Float |  |
| 钢柱计算长度系数按有侧移计算_X向 | YP_GZCY(706) | Int |  |
| 钢柱计算长度系数按有侧移计算_Y向 | YP_GZCYY(734) | Int |  |
| 按《钢规》自动判断强弱支撑 | YP_AUTOQRZC(728) | Int |  |
| 执行门规GB51022-2015 | YP_GB51022(746) | Int |  |
| 执行门规GB51022附录A | YP_MGCOLBYGB51022(744) | Int |  |
| 执行门规GB51022附录A.0.8 | YP_MGA08(743) | Int |  |
| 门刚构件按宽厚比等级控制局部稳定 | YP_JMKHB(749) | Int |  |
| 截面宽厚比等级 | YP_MGJMKHBDJ (759) | Int | S1 (75001) S2 (75002) S3 (75003) S4 (75004) |
| 执行《钢结构设计标准》（GB50017-2017） | YP_GB50017_2017(752) | Int |  |
| 按宽厚比等级控制局部稳定 | YP_MGJMKHB(758) | Int |  |
| 截面宽厚比等级 | YP_JMKHBDJ(750) | Int | S1 (75001) S2 (75002) S3 (75003) S4 (75004) BS1 (75005) BS2 (75006) BS3 (75007) S5  (75008) |
| 中心支撑截面宽厚比等级 | YP_ZCJMKHBDJ(751) | Int | S1 (75001) S2 (75002) S3 (75003) S4 (75004) BS1 (75005) BS2 (75006) BS3 (75007) |
| 组合梁截面宽厚比等级 | YP_ZHLJMKHBDJ(760) | Int | S1 (75001) S2 (75002) S3 (75003) S4 (75004) |
| 按钢规6.2.7验算梁下翼缘稳定 | YP_XYYWD627(756) | Int |  |
| 冷弯薄壁构件考虑冷弯效应 | YP_LWBJKLLWXY(761) | Int |  |
| 进行承载力法防火验算 | YP_FHYSCZL(2001) | Int |  |
| 防火规范结构重要性系数 | YP_FHZYXXS(2002) | Float |  |
| 承载力验算时温度内力折减系数 | YP_WDNLZJXX(2005) | Float |  |
| 燃烧物类型 | YP_BURNTYPE(2010) | Int | 纤维类 (201001) 烃类 (201002) |
| 保护层类型_梁 | YP_FHBHCL(2006) | Int | 外边缘型 (200601) 非外边缘型(200602) |
| 保护层类型_柱 | YP_FHBHCZ(2007) | Int | 外边缘型 (200601) 非外边缘型(200602) |
| 保护层类型_支撑 | YP_FHBHCC(2008) | Int | 外边缘型 (200601) 非外边缘型(200602) |
| 使用耐火钢 | YP_USENHG(2004) | Int |  |
| 轴向受力构件考虑温度组合 | YP_ZYGJKLWDZH(2009) | Int |  |
| 非轴向受力构件考虑温度组合 | YP_FZYGJKLWDZH(2011) | Int |  |
| 组合梁施工荷载 | YP_ZHLSGHZ(742) | Float |  |
| 组合类别 | YP_SGZHLB(762) | Int | 基本组合(76201) 标准组合(76202) |
| 抗剪连接件单侧边距 | YP_SHEARLINKDIS(770) | Int |  |

包络设计

| 项名称 | 宏定义（id号） | 输入参数类型 | 额外说明 |
|---|---|---|---|
| 自动取框架和框架-抗震墙模型计算大值 | YP_SQKJ(632) | Int |  |
| 按纯框架计算时墙弹模折减系数 | YP_SQKJE(633) | Float |  |

材料参数

| 项名称 | 宏定义（id号） | 输入参数类型 | 额外说明 |
|---|---|---|---|
| 混凝土容重 | YP_HNTRZ(801) | Float |  |
| 砌体容重 | YP_QTRZ(804) | Float |  |
| 钢材容重 | YP_GRZ(803) | Float |  |
| 轻骨料混凝土容重 | YP_QGLRZ(805) | Float |  |
| 轻骨料混凝土密度等级 | YP_QGLMD(806) | Int |  |
| 梁箍筋间距 | YP_LGJD(816) | Int |  |
| 墙竖向分布筋配筋率 | YP_QVTROU(819) | Float |  |
| 墙最小水平分布筋配筋率（%） | YP_QHORROUMIN(829) | Float |  |
| 柱箍筋间距（mm） | YP_ZGJD(817) | Int |  |
| 墙水平分布筋间距（mm） | YP_QHRD(818) | Int |  |
| 结构底部需要单独指定墙竖向分布筋配筋率的层号 | YP_QJROUFLRS(823) | Int[] |  |
| 结构底部需要单独指定的墙竖向分布筋配筋率（%） | YP_QVTROU(819) | Float |  |

钢筋强度

| 项名称 | 宏定义（id号） | 输入参数类型 | 额外说明 |
|---|---|---|---|
| HPB235钢筋强度设计值 | YP_FY_HPB235(811001) | Int |  |
| HPB300钢筋强度设计值 | YP_FY_HPB300(811002) | Int |  |
| HRB335钢筋强度设计值 | YP_FY_HRB335(811003) | Int |  |
| HRB400钢筋强度设计值 | YP_FY_HRB400(811004) | Int |  |
| HRB500钢筋虽度设计值 | YP_FY_HRB500(811005) | Int |  |
| HTRB600钢筋强度设计值 | YP_FY_HTRB600(811007) | Int |  |
| T63/E/G钢筋强度设计值 | YP_FY_HTRB630(811008) | Int |  |
| 冷轧带肋550钢筋强度设计值 | YP_FY_LZDL550(811006) | Int |  |
| CRB600H钢筋强度设计值 | YP_FY_CRB600H(811009) | Int |  |
| 项E6S5钢筋强度设计值 | YP_FY_HRB635(811010) | Int |  |

地下室信息

| 项名称 | 宏定义（id号） | 输入参数类型 | 额外说明 |
|---|---|---|---|
| 土层水平抗力系数的比例系数（m值） | YP_DIJIM(1001) | Float |  |
| 扣除地面以下几层的回填土约束 | YP_NKHTT(1003) | Int |  |
| 外墙分布筋保护层厚度 | YP_DXWQBHC(1002) | Int |  |
| 回填土容重 | YP_HTTRZ(1004) | Float |  |
| 室外地坪标高 | YP_QSWDP(1005) | Float |  |
| 回填土侧压力系数 | YP_RHTT(1006) | Float |  |
| 地下水位标高 | YP_QWATER(1007) | Float |  |
| 室外地面附加荷载 | YP_DMADDLD(1008) | Float |  |
| 基础水工况组合方式 | YP_JCWATERCOMB(1009) | Int |  |
| 地下室侧土约束施加方式 | YP_SJCTYS(1016) | Int | 顶板双向弹簧(101601) 外墙单压弹簧(101602) |
| 按反应位移法计算地下结构的地震作用 | YP_FYWYJSDZ(1010) | Int |  |
| 基床系数K | YP_JCXS(1011) | Int |  |
| 地震动剪切模量G | YP_SEISG(1014) | Int |  |
| 场地设计地震动峰值位移Umax_X向 | YP_JCUMAXX(1012) | Float |  |
| 场地设计地震动峰值位移Umax_Y向 | YP_JCUMAXY(1013) | Float |  |
| 设计地震作用基准面的深度H | YP_JZMSD(1015) | Float |  |
| 按《地下结构抗震设计标准》2018设计 | YP_GBT51336(1017) | Int |  |
| 地下室结构形式 | YP_DXSJGTX(1018) | Int | 单排柱框架(101801) 其它框架(101802) 同上部结构类型(其它)(101803) |

荷载组合

| 项名称 | 宏定义（id号） | 输入参数类型 | 额外说明 |
|---|---|---|---|
| 结构重要性系数 | YP_ZYXXS(901) | Float |  |
| 恒荷载分项系数 | YP_DLFX(902) | Float |  |
| 活荷载分项系数 | YP_LLFX(903) | Float |  |
| 活荷载组合值系数 | YP_LLZH(904) | Float |  |
| 活荷载频遇值系数 | YP_LLPY (928) | Float |  |
| 活荷载准永久值系数 | YP_LLZYJ(929) | Float |  |
| 考虑结构设计使用年限的活荷载调整系数 | YP_LLTZ(905) | Float |  |
| 吊车荷载重力荷载代表值系数 | YP_DCDBZXS(914) | Float |  |
| 吊车荷载组合值系数 | YP_DCZH(930) | Float |  |
| 吊车荷载频遇值系数 | YP_DCPY(931) | Float |  |
| 吊车荷载准永久值系数 | YP_DCZYJ(932) | Float |  |
| 风荷载分项系数 | YP_WINDFX(906) | Float |  |
| 风荷载组合值系数 | YP_WINDZH(907) | Float |  |
| 风荷载频遇值系数 | YP_WINDPY(933) | Float |  |
| 风荷载参与地震组合 | YP_WINDDZ(908) | Int |  |
| 执行《建筑结构可靠性设计统一标准》 | YP_GB50068(973) | Int |  |
| 刚重比按1.3恒+1.5活计算 | YP_GZBBYGB50068(974) | Int |  |
| 重力荷载分项系数 | YP_GLFX(971) | Float |  |
| 水平地震作用分项系数 | YP_HRDZFX(909) | Float |  |
| 竖向地震作用分项系数 | YP_VTDZFX(910) | Float |  |
| 考虑竖向地震作用为主的组合 | YP_VTDZZH(911) | Int |  |
| 仅考虑恒活荷载参与的组合 | YP_WDZH(916) | Float |  |
| 风荷载参与的组合 | YP_WDZHWIND(917) | Float |  |
| 地震作用参与的组合 | YP_WDZHSEIS(918) | Float |  |
| 温度荷载频遇值系数 | YP_WDPY(934) | Float |  |
| 温度荷载准永久值系数 | YP_WDZYJ(935) | Float |  |

鉴定加固

| 项名称 | 宏定义（id号） | 输入参数类型 | 额外说明 |
|---|---|---|---|
| 鉴定加固 | YP_JDJG(1801) | Int |  |
| 鉴定加固标准 | YP_JDJGCODE(1802) | Int | 建筑抗震鉴定标准(GB50023-95) 对应B类(180201) 1989系列规范 对应A类(180202) 2001系列规范 对应C类(180203) 2010系列规范 对应C类(180204) |
| 计算时采用加固后影响系数（用于上部设计） | YP_USEJGHXS(1807) | Int |  |
| 承载力抗震调整系数的折减系数 | YP_GAMAREZJXS(1803) | Float |  |

装配式

| 项名称 | 宏定义（id号） | 输入参数类型 | 额外说明 |
|---|---|---|---|
| 装配式结构 | YP_ZPS(1901) | Int |  |
| 现浇墙地震内力放大系数 | YP_XJQDZFD(1902) | Float |  |
| 现浇柱地震内力放大系数 | YP_XJZDZFD(1906) | Float |  |
| 预制竖向构件地震内力放大系数 | YP_YZSXGJDZFD(1905) | Float |  |
| 按北京市装配式规程验算预制墙接缝 | YP_BJYZQJF(1904) | Int |  |
