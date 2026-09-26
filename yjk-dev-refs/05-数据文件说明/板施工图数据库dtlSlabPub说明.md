> 来源：YJK 官方二次开发文档包 `数据库文件说明.rar` 内 `板施工图数据库dtlSlabPub说明.docx`，由 pandoc 从 .docx 转换为 Markdown（纯文本，图片以标记代替）。

# dtlSlabPub数据结构

说明：字段中带(\_数字)的字段即为一个数组分成多个字段进行存储。如：DrwMark\[2\]在数据库中存储为DrwMark_1和DrwMark_2。二进制存储的数组的具体描述见表下解释。

### 工程参数（tblProjectPara）

|  字段名   | 字段类型 | 允许为空 | 主键 |     字段含义      |
|:---------:|:--------:|:--------:|:----:|:-----------------:|
|    ID     |   整型   |    否    |  是  | 参数ID（见附录1） |
| PareValue |   可变   |    否    |  否  |      参数值       |

### 板底计算（tblBottomCal）

| 字段名 | 字段类型 | 允许为空 | 主键 | 字段含义 |
|----|----|----|----|----|
| ID | 整型 | 否 | 是 | 板id　 |
| FlrNo | 整型 | 否 | 是 | 　自然层号 |
| Shape | 整型 | 否 | 否 | 　0/1/2:矩形/异形/异形但可按矩形计算 |
| Thick | 整型 | 否 | 否 | 　板厚 |
| Bhc | 整型 | 否 | 否 | 保护层 |
| CuoC | 整型 | 否 | 否 | 　错层值 |
| Loc | 整型 | 否 | 否 | 房间位置　/1/2/3:中间区域/边区域/角区域/独立房间 |
| DrwMark_1 | 整型 | 否 | 否 | 钢筋绘制标志 |
| DrwMark_2 | 整型 | 否 | 否 | 钢筋绘制标志 |
| AdddrwMark_1 | 整型 | 否 | 否 | 附加钢筋绘制标志 |
| AdddrwMark_2 | 整型 | 否 | 否 | 附加钢筋绘制标志 |
| Ybj | 整型 | 否 | 否 | 是否为样板间标志 |
| RfcControl | 整型 | 否 | 否 | 是否为人防控制板配筋标志 |
| VertexX | 二进制（double） | 否 | 否 | 　近似计算时房间四个顶点坐标 |
| VertexY | 二进制（double） | 否 | 否 | 　近似计算时房间四个顶点坐标 |
| Aw | 浮点型 | 否 | 否 | 　度，房间定位角，异形房间按最长边确定 |
| Rw | 浮点型 | 否 | 否 | 　砼等级 |
| Dead | 浮点型 | 否 | 否 | 　恒载 |
| Live | 浮点型 | 否 | 否 | 　活载 |
| RfLoad | 浮点型 | 否 | 否 | 　人防荷载 |
| BotReduce | 浮点型 | 否 | 否 | 　板底弯矩折减系数 |
| TopReduce | 浮点型 | 否 | 否 | 　支座弯矩折减系数 |
| Shear | 二进制（double） | 否 | 否 | 剪力 |
| Moment_1 | 浮点型 | 否 | 否 | 　弯矩 |
| Moment_2 | 浮点型 | 否 | 否 | 　弯矩 |
| Moment_c_1 | 浮点型 | 否 | 否 | 　计算裂缝时的弯矩 |
| Moment_c_2 | 浮点型 | 否 | 否 | 　计算裂缝时的弯矩 |
| Moment_rf_1 | 浮点型 | 否 | 否 | 　人防计算时的弯矩 |
| Moment_rf_2 | 浮点型 | 否 | 否 | 　人防计算时的弯矩 |
| Moment_ang_1 | 浮点型 | 否 | 否 | 　计算弯矩的方向角 |
| Moment_ang_2 | 浮点型 | 否 | 否 | 　计算弯矩的方向角 |
| Stlas_1 | 浮点型 | 否 | 否 | 计算面积 |
| Stlas_2 | 浮点型 | 否 | 否 | 　计算面积 |
| Crack_1 | 浮点型 | 否 | 否 | 裂缝 |
| Crack_2 | 浮点型 | 否 | 否 | 　裂缝 |
| Def | 浮点型 | 否 | 否 | 挠度 |
| Info_1 | 文本型 | 否 | 否 | 　板底配筋 |
| Info_2 | 文本型 | 否 | 否 | 　板底配筋 |
| Info_Top_1 | 文本型 | 否 | 否 | 　板顶配筋 |
| Info_Top_2 | 文本型 | 否 | 否 | 　板顶配筋 |
| Drwmark_top_1 | 整型 | 否 | 否 | 　板面钢筋绘制标志 |
| Drwmark_top_2 | 整型 | 否 | 否 | 板面钢筋绘制标志　 |
| Adddrwmark_top_1 | 整型 | 否 | 否 | 附加板面钢筋绘制标志 |
| Adddrwmark_top_2 | 整型 | 否 | 否 | 附加板面钢筋绘制标志　 |

二进制说明：VertexX：一维数组，总共4个数。

VertexY：一维数组，总共4个数。

Shear：一维数组，总共4个数。

### 支座计算（tblSupportCal）

| 字段名 | 字段类型 | 允许为空 | 主键 | 字段含义 |
|:--:|:--:|:--:|:--:|:--:|
| ID | 整型 | 否 | 是 | 　id |
| FlrNo | 整型 | 否 | 是 | 楼层编号 |
| GouJian | 整型 | 否 | 否 | 　　梁（＞）、圈梁（+20000）、次梁（+40000）或墙（＜0）的编号 |
| CuoC | 整型 | 否 | 否 | 错层信息 |
| Bound_1 | 整型 | 否 | 否 | 　边界条件:简支1:固定2:自由 |
| Bound_2 | 整型 | 否 | 否 | 　　边界条件:简支1:固定2:自由 |
| DrwMark_1 | 整型 | 否 | 否 | 支座钢筋绘制标志 |
| DrwMark_2 | 整型 | 否 | 否 | 　支座钢筋绘制标志 |
| AdddrwMark_1 | 整型 | 否 | 否 | 附加支座钢筋绘制标志 |
| AdddrwMark_2 | 整型 | 否 | 否 | 　附加支座钢筋绘制标志 |
| Moment_1 | 浮点型 | 否 | 否 | 　弯矩 |
| Moment_2 | 浮点型 | 否 | 否 | 　弯矩 |
| Moment_c_1 | 浮点型 | 否 | 否 | 　计算裂缝时的弯矩 |
| Moment_c_2 | 浮点型 | 否 | 否 | 　计算裂缝时的弯矩 |
| Moment_rf_1 | 浮点型 | 否 | 否 | 　人防计算时的弯矩 |
| Moment_rf_2 | 浮点型 | 否 | 否 | 　人防计算时的弯矩 |
| Stlas_1 | 浮点型 | 否 | 否 | 　计算面积 |
| Stlas_2 | 浮点型 | 否 | 否 | 　计算面积 |
| Shear_1 | 浮点型 | 否 | 否 | 　剪力,非矩形目前不能计算其剪力 |
| Shear_2 | 浮点型 | 否 | 否 | 　剪力,非矩形目前不能计算其剪力 |
| Crack_1 | 浮点型 | 否 | 否 | 　裂缝 |
| Crack_2 | 浮点型 | 否 | 否 | 　裂缝 |
| LenFact_1 | 浮点型 | 否 | 否 | 　考虑板坡度的长度调整 |
| LenFact_2 | 浮点型 | 否 | 否 | 　考虑板坡度的长度调整 |
| Room_1 | 整型 | 否 | 否 | 　两侧房间编号 次梁时两侧相同\<0时为悬挑板编号 |
| Room_2 | 整型 | 否 | 否 | 　两侧房间编号 次梁时两侧相同\<0时为悬挑板编号 |
| Length_1 | 整型 | 否 | 否 | 　两侧钢筋的长度 |
| Length_2 | 整型 | 否 | 否 | 　两侧钢筋的长度 |
| Lwz_1 | 整型 | 否 | 否 | 两侧钢筋的弯折长度　 |
| Lwz_2 | 整型 | 否 | 否 | 两侧钢筋的弯折长度　 |
| Info_1 | 文本型 | 否 | 否 | 配筋信息 |
| Info_2 | 文本型 | 否 | 否 | 配筋信息　 |

### 钢筋表（tblSteelTable）

<table>
<colgroup>
<col style="width: 22%" />
<col style="width: 12%" />
<col style="width: 13%" />
<col style="width: 10%" />
<col style="width: 41%" />
</colgroup>
<thead>
<tr>
<th style="text-align: center;">字段名</th>
<th style="text-align: center;">字段类型</th>
<th style="text-align: center;">允许为空</th>
<th style="text-align: center;">主键</th>
<th style="text-align: center;">字段含义</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: center;">ID</td>
<td style="text-align: center;">整型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">　钢筋表中id编号</td>
</tr>
<tr>
<td style="text-align: center;">FlrNo</td>
<td style="text-align: center;">整型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">　楼层</td>
</tr>
<tr>
<td style="text-align: center;">Bh</td>
<td style="text-align: center;">整型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">　钢筋编号</td>
</tr>
<tr>
<td style="text-align: center;">Itype</td>
<td style="text-align: center;">整型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">　正筋:1、板底正筋，温度钢筋，中间层筋;2：板顶面筋,负筋:10</td>
</tr>
<tr>
<td style="text-align: center;">Llen</td>
<td style="text-align: center;">整型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;"><p>　左侧长度 负筋(面筋)使用</p>
<p>正筋使用时为总长度</p></td>
</tr>
<tr>
<td style="text-align: center;">Rlen</td>
<td style="text-align: center;">整型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">　右侧长度 负筋(面筋)使用</td>
</tr>
<tr>
<td style="text-align: center;">Lwz</td>
<td style="text-align: center;">整型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">　左弯折</td>
</tr>
<tr>
<td style="text-align: center;">Rwz</td>
<td style="text-align: center;">整型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">　右弯折</td>
</tr>
<tr>
<td style="text-align: center;">Detail</td>
<td style="text-align: center;">整型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">　是否已有详细标注</td>
</tr>
<tr>
<td style="text-align: center;">Udefine</td>
<td style="text-align: center;">整型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">　当前编号是否由用户指定</td>
</tr>
<tr>
<td style="text-align: center;">Info</td>
<td style="text-align: center;">文本型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">　钢筋信息a8@200</td>
</tr>
<tr>
<td style="text-align: center;">Lmax</td>
<td style="text-align: center;">整型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">　最短长度</td>
</tr>
<tr>
<td style="text-align: center;">Lmin</td>
<td style="text-align: center;">整型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">　最长长度</td>
</tr>
<tr>
<td style="text-align: center;">Ltotal</td>
<td style="text-align: center;">整型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">　总长度</td>
</tr>
<tr>
<td style="text-align: center;">Num</td>
<td style="text-align: center;">整型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">　根数</td>
</tr>
<tr>
<td style="text-align: center;">Weight</td>
<td style="text-align: center;">整型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">　重量</td>
</tr>
</tbody>
</table>

### 普通钢筋（tblGeneralSteel）

| 字段名 | 字段类型 | 允许为空 | 主键 | 字段含义 |
|:--:|:--:|:--:|:--:|:--:|
| ID | 整型 | 否 | 是 | 　钢筋id编号 |
| FlrNo | 整型 | 否 | 是 | 　楼层编号 |
| GjbId | 整型 | 否 | 否 | 钢筋表中的id编号 |
| Itype | 整型 | 否 | 否 | 　1：普通筋2:补强筋 |
| Detail | 整型 | 否 | 否 | 　是否是详细标注 |
| Mebid | 整型 | 否 | 否 | 　支座id号/房间id编号 |
| Kfx | 整型 | 否 | 否 | 　0/1房间时代表xy方向，/1/2支座时代表左右侧,2为没有错层，无错层时不区分左右侧 |
| Ang | 浮点型 | 否 | 否 | 　钢筋布置角度 |
| Xs | 浮点型 | 否 | 否 | 　钢筋所画位置的起点坐标 |
| Ys | 浮点型 | 否 | 否 | 　钢筋所画位置的起点坐标 |
| Xe | 浮点型 | 否 | 否 | 　钢筋所画位置的终点坐标 |
| Ye | 浮点型 | 否 | 否 | 　钢筋所画位置的终点坐标 |

### 拉通钢筋（tblRatonSteel）

| 字段名 | 字段类型 | 允许为空 | 主键 | 字段含义 |
|:--:|:--:|:--:|:--:|:--:|
| ID | 整型 | 否 | 是 | 　钢筋id编号 |
| FlrNo | 整型 | 否 | 是 | 　楼层编号 |
| Gjbid | 整型 | 否 | 否 | 　钢筋表中的id编号 |
| Itype | 整型 | 否 | 否 | 　1平行直线、圆弧线、放射线;31:普通拉通（以房间或支座为单位）41：区域拉通（以房间为单位） |
| Detail | 整型 | 否 | 否 | 　是否是详细标注 |
| Num | 整型 | 否 | 否 | 　拉通房间或支座的个数 |
| MebId | 二进制（int） | 否 | 否 | 每个拉通房间或支座的ID号 |
| DimNum | 整型 | 否 | 否 | 　标注次数\[允许一个区域多次标注\] |
| Ang | 浮点型 | 否 | 否 | 　钢筋布置角度 |
| Xs | 浮点型 | 否 | 否 | 　钢筋所画位置的起点坐标 |
| Ys | 浮点型 | 否 | 否 | 　钢筋所画位置的起点坐标 |
| Xe | 浮点型 | 否 | 否 | 　钢筋所画位置的终点坐标 |
| Ye | 浮点型 | 否 | 否 | 　钢筋所画位置的终点坐标 |

MebId：std::vector \<int\>，具体个数见Num。

### 任意钢筋(tblConnectSteel)

| 字段名 | 字段类型 | 允许为空 | 主键 |                 字段含义                 |
|:------:|:--------:|:--------:|:----:|:----------------------------------------:|
|   ID   |   整型   |    否    |  是  |               　钢筋id编号               |
| FlrNo  |   整型   |    否    |  是  |                　楼层编号                |
| Itype  |   整型   |    否    |  否  | 　1:洞口直线、:洞口圆弧、圆弧线、放射线; |
| MebId  |   整型   |    否    |  否  |       　id号（洞口id号，其它时为）       |
|   Bh   |   整型   |    否    |  否  |                　钢筋编号                |
|  Info  |  文本型  |    否    |  否  |                　钢筋信息                |
|  Len   |   整型   |    否    |  否  |                　钢筋长度                |
|  Lwz   |   整型   |    否    |  否  |        　左弯折长度 =-10时有弯钩         |
|  Rwz   |   整型   |    否    |  否  |               　右弯折长度               |
|  Ang   |  浮点型  |    否    |  否  |              　钢筋布置角度              |
|   Xs   |  浮点型  |    否    |  否  |           　钢筋起点位置的坐标           |
|   Ys   |  浮点型  |    否    |  否  |           　钢筋起点位置的坐标           |
|   Xe   |  浮点型  |    否    |  否  |           　钢筋终点位置的坐标           |
|   Ye   |  浮点型  |    否    |  否  |           　钢筋终点位置的坐标           |

### 房间合并（tblRoomMerge）

| 字段名  | 字段类型 | 允许为空 | 主键 |        字段含义        |
|:-------:|:--------:|:--------:|:----:|:----------------------:|
|  FlrNo  |   整型   |    否    |  是  |       　楼层编号       |
| RoomNum |   整型   |    否    |  是  |        　房间号        |
|   ID    |   整型   |    否    |  否  |      　样板间id号      |
| YbjNum  |   整型   |    否    |  否  |       　样板间号       |
| Lbtype  |   整型   |    否    |  否  | 　板块类型0-2:LB/WB/XB |

### 井字梁（tblJzBeam）

|    字段名    | 字段类型 | 允许为空 | 主键 |                字段含义                |
|:------------:|:--------:|:--------:|:----:|:--------------------------------------:|
|      ID      |   整型   |    否    |  是  |             　井字梁范围id             |
|    FlrNo     |   整型   |    否    |  是  |               　楼层编号               |
|  GridRoomID  |  二进制  |    否    |  否  |         　组成井字梁的各房间ID         |
| GridMemberID |  二进制  |    否    |  否  | 　组成井字梁的非框架梁ID，为底图画法用 |

GridRoomID：vector\<int\>

GridMemberID：vector\<int\>

### 附加表（tblAdditionalTable）

|    字段名     |   字段类型    | 允许为空 | 主键 |        字段含义        |
|:-------------:|:-------------:|:--------:|:----:|:----------------------:|
|     FlrNo     |     整型      |    否    |  是  |       　楼层编号       |
|  BottomJsNum  |     整型      |    否    |  否  |     　现浇板块数量     |
| SupportJsNum  |     整型      |    否    |  否  |       　支座数量       |
|    GjbNum     |     整型      |    否    |  否  |      　钢筋表数量      |
|     GjbId     |     整型      |    否    |  否  |       　钢筋表ID       |
|     JzlID     |     整型      |    否    |  否  |       　井字梁ID       |
|    PtgjNum    |     整型      |    否    |  否  |     　普通钢筋数量     |
|    LtgjNum    |     整型      |    否    |  否  |     　拉通钢筋数量     |
|    RygjNum    |     整型      |    否    |  否  |     　拉通钢筋数量     |
|  SteelIdMax   |     整型      |    否    |  否  |    　钢筋ID的最大值    |
|     nmpx      |     整型      |    否    |  否  |    房间归并总数量　    |
|     nybj      |     整型      |    否    |  否  |      　样板间数量      |
| vvSupportSpan | 二进制（int） |    否    |  否  |  　按平法标注时板跨串  |
|    nXtbYbj    |     整型      |    否    |  否  | 　悬挑板（样板间数量） |

vvSupportSpan：std::vector\<std::vector\<int\>\>

### 附录1

| 编号 | 类型 | 含义 |
|:--:|:--:|:--:|
| 1 | 整型 | 当前层是否计算过的标志 |
| 2 | 浮点型 | 当前砼等级 |
| 3 | 整型 | 当前是否为人防计算 |
| 4 | 浮点型 | 负筋最小直径\[包括构造筋\] |
| 5 | 浮点型 | 正筋最小直径\[包括构造筋\] |
| 6 | 整型 | 最大钢筋间距 |
| 7 | 整型 | 双向板计算方法　0：弹性　1：塑性 |
| 8 | 浮点型 | 塑性计算时的支座与跨中弯矩比值 |
| 9 | 浮点型 | 有限元划分楼板的尺寸，单位米 |
| 10 | 整型 | 边缘梁墙边界 0/1:简支/固定 |
| 11 | 整型 | 错层边界取法 0/1:简支/固定 |
| 12 | 整型 | 1/2/-2/3/11钢筋级别　11：冷轧 |
| 13 | 整型 | 直径大于该值时为二级钢 |
| 14 | 浮点型 | 板底钢筋调整系数 |
| 15 | 浮点型 | 板顶钢筋调整系数 |
| 16 | 整型 | 自定义钢筋强度设计值开关　0/1:默认/用户指定 |
| 17 | 浮点型 | 钢筋强度设计值　此处不必要设多个，一个即可 |
| 18 | 整型 | 考虑活载不利布置标志 |
| 19 | 整型 | 按允许裂缝宽度调整标志 |
| 20 | 浮点型 | 允许裂缝宽度 |
| 21 | 浮点型 | 人防计算时跨中弯矩折减系数，此系数应与正弯矩调整一致 |
| 22 | 整型 | 人防等级 |
| 23 | 整型 | 负筋长度取大值 |
| 24 | 整型 | 负筋长度 0/1/2:四分/三分/与活载有关 |
| 25 | 整型 | 负筋长度的模数 |
| 26 | 整型 | 0/1:负筋长度的模数的取整方法（两边分别取整，总长取整） |
| 27 | 整型 | 0/1:负筋净距小于设定值时自动拉通 |
| 28 | 浮点型 | 双向板长宽比 |
| 29 | 浮点型 | 准永久值系数 |
| 30 | 整型 | 用户指定配筋率 |
| 31 | 浮点型 | 最小配筋率 |
| 32 | 浮点型 | 最大配筋率　超过此值提示超筋信息 |
| 33 | 浮点型 | 近似计算时板底弯矩系数 |
| 34 | 浮点型 | 近似计算时支座弯矩系数 |
| 35 | 浮点型 | 近似计算时缺口相对尺寸 |
| 36 | 浮点型 | 中间跨板底弯矩调整系数 |
| 37 | 浮点型 | 中间跨支座弯矩调整系数 |
| 38 | 浮点型 | 边跨板底弯矩调整系数 |
| 39 | 浮点型 | 边跨支座弯矩调整系数 |
| 40 | 浮点型 | 边支座钢筋伸入支座的最大长度 |
| 41 | 整型 | 挠度限值 小于7米 |
| 42 | 整型 | 挠度限值 小于9米 |
| 43 | 整型 | 挠度限值 大于9米 |
| 44 | 整型 | 级配库中钢筋总数 |
| 45 | 二进制（浮点） | 级配库 直径 |
| 46 | 二进制（浮点） | 级配库 间距 |
| 47 | 二进制（浮点） | 级配库 面积 |
| 48 | 整型 | 最小直径范围 |
| 49 | 整型 | 最大直径范围 |
| 50 | 文本型 | 最优直径 |
| 51 | 文本型 | 钢筋间距 |
| 52 | 浮点型 | 连续板串计算时调幅系数 |
| 53 | 整型 | 左端边界条件 |
| 54 | 整型 | 右端边界条件 |
| 55 | 整型 | 跨中弯矩不小于简支弯矩的一半 |
| 56 | 整型 | 次梁形成支座 |
| 57 | 整型 | 荷载考虑双向板作用 |
| 58 | 整型 | 图纸号 |
| 59 | 浮点型 | 图纸加宽比例 |
| 60 | 整型 | 绘图比例 |
| 61 | 整型 | 0/1/2=全编号/仅负筋/全不 钢筋是否编号 |
| 62 | 整型 | 钢筋是否简化标注 |
| 63 | 整型 | 标注预制板板缝尺寸 |
| 64 | 整型 | 画钢筋表 |
| 65 | 整型 | 负筋标注位置　梁中心/梁边 |
| 66 | 整型 | 负筋标注尺寸位置　上边/下边　　 |
| 67 | 整型 | 负筋尺寸标注方式　文字标注/尺寸标注 |
| 68 | 整型 | 负筋标注方式　　平法/传统方法 |
| 69 | 整型 | 间距标注符号　＠/－ |
| 70 | 整型 | 二级钢弯钩形式　无弯钩/斜钩 |
| 71 | 整型 | 按平法标注支座钢筋时，支座两侧板配置有板顶面筋时，不自动布置支座钢筋标志 |
| 72 | 整型 | 按平法标注支座钢筋时，支座两侧板配置有板顶面筋时，不自动布置支座钢筋标志 |
| 73 | 整型 | 简化标注的个数 |
| 74 | 二进制（文本） | 简化标注的内容(未开放) |
| 75 | 二进制（文本） | 简化标注的内容(未开放) |
| 76 | 预留位 | 预留位 |
| 77 | 预留位 | 预留位 |
| 78 | 预留位 | 预留位 |
| 79 | 预留位 | 预留位 |
| 80 | 预留位 | 预留位 |
| 81 | 预留位 | 预留位 |
| 82 | 整型 | 显示钢筋标注 |
| 83 | 二进制（整型） | 洞口钢筋可供选择的直径库 |
| 84 | 整型 | 洞口钢筋可供选择的直径数量 |
| 85 | 预留位 | 预留位 |
| 86 | 整型 | 当前房间洞口编号 |
| 87 | 二进制（整型） | 每层对应的id号 |
| 88 | 整型 | 版本号 |
| 89 | 二进制（整型） | 每层对应的id号 |
| 90 | 二进制（整型） | 每层是否有计算数据的标志 |
| 91 | 整型 | 钢筋文件中记录的总层数 |
| 92 | 文本型 | 工程名称 |
| 93 | 整型 | 当前程序的数据库版本 |
| 94 | 整型 | 按平法标注支座钢筋时，是否仅标注在第1跨标志 |
| 95 | 浮点型 | 板底钢筋直斜钩长 |
| 96 | 浮点型 | 板底钢筋圆钩长 |
| 97 | 浮点型 | 板底钢筋圆钩半径 |
| 98 | 浮点型 | 板顶钢筋直弯钩长度 |
