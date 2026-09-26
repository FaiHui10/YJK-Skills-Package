> 来源：YJK 官方二次开发文档包 `数据库文件说明.rar` 内 `砼柱施工图数据库dtlRcCol说明.docx`，由 pandoc 从 .docx 转换为 Markdown（纯文本，图片以标记代替）。

# dtlRcCol.ydb数据结构

### 连续柱（tblRCCntCol）

<table>
<colgroup>
<col style="width: 21%" />
<col style="width: 14%" />
<col style="width: 13%" />
<col style="width: 9%" />
<col style="width: 40%" />
</colgroup>
<thead>
<tr>
<th>字段名</th>
<th>字段类型</th>
<th>允许为空</th>
<th>主键</th>
<th>字段含义</th>
</tr>
</thead>
<tbody>
<tr>
<td>ID</td>
<td>整型</td>
<td>否</td>
<td>是</td>
<td>连续柱id　</td>
</tr>
<tr>
<td>FloorID</td>
<td>整型</td>
<td>否</td>
<td>否</td>
<td>柱底柱段所属自然层ID</td>
</tr>
<tr>
<td>Type</td>
<td>整型</td>
<td>否</td>
<td>否</td>
<td><p>柱类型，可能属于多种类型</p>
<p>0x01 框架柱</p>
<p>0x02 框支柱</p>
<p>0x04 梁上柱</p>
<p>0x08 墙上柱</p>
<p>0x10 角柱</p>
<p>0x20 边框柱</p></td>
</tr>
<tr>
<td>SpanNum</td>
<td>整型</td>
<td>否</td>
<td>否</td>
<td>柱包含跨数</td>
</tr>
<tr>
<td>RcCntColID</td>
<td>整型</td>
<td>否</td>
<td>否</td>
<td>所属配筋连续柱的ID</td>
</tr>
<tr>
<td>JointID</td>
<td>整型</td>
<td>否</td>
<td>否</td>
<td>柱底布置节点的ID</td>
</tr>
</tbody>
</table>

### 自然层信息（tblRCFloor）

|  字段名   | 字段类型 | 允许为空 | 主键 |     字段含义     |
|:---------:|:--------:|:--------:|:----:|:----------------:|
|    ID     |   整型   |    否    |  是  |    　自然层ID    |
| StdFlrID  |   整型   |    否    |  否  |     标准层ID     |
| ReinFlrID |   整型   |    否    |  否  | 　　钢筋标准层ID |
|   No\_    |   整型   |    否    |  否  |    自然层序号    |
|   Name    |  文本型  |    否    |  否  |    自然层名称    |
|  LevelB   |  浮点型  |    否    |  否  |     层底标高     |
|  Height   |  浮点型  |    否    |  否  |       层高       |

### 配筋连续柱组（tblRCRcCntCol）

| 字段名     | 字段类型 | 允许为空 | 主键 | 字段含义             |
|------------|----------|----------|------|----------------------|
| ID         | 整型     | 否       | 是   | 配筋连续柱id　       |
| FloorID    | 整型     | 否       | 否   | 柱底柱段所属自然层ID |
| Name       | 文本型   | 否       | 否   | 配筋连续柱名称       |
| SpanNum    | 整型     | 否       | 否   | 柱包含跨数           |
| CntColDeID | 整型     | 否       | 否   | 代表连续柱ID         |

### 

### 柱跨表（tblRCSpan）

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
<td style="text-align: center;">　ID(只在同一连续柱中不重复)</td>
</tr>
<tr>
<td style="text-align: center;">CntColID</td>
<td style="text-align: center;">整型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">　所属连续柱ID</td>
</tr>
<tr>
<td style="text-align: center;">LevelB</td>
<td style="text-align: center;">浮点型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">柱跨底标高</td>
</tr>
<tr>
<td style="text-align: center;">LevelT</td>
<td style="text-align: center;">浮点型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">柱跨顶标高</td>
</tr>
<tr>
<td style="text-align: center;">LevelBeamB</td>
<td style="text-align: center;">浮点型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;"><p>柱跨相连梁高度</p>
<p>（取柱跨顶标高-梁最底标高）</p></td>
</tr>
<tr>
<td style="text-align: center;">IndexSegStart</td>
<td style="text-align: center;">整型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">柱跨底所属柱段在连续柱中的序数</td>
</tr>
<tr>
<td style="text-align: center;">IndexSegEnd</td>
<td style="text-align: center;">整型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">柱跨顶所属柱段在连续柱中的序数</td>
</tr>
</tbody>
</table>

### 配筋柱跨组表（tblRCRcSpan）

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
<td style="text-align: center;">　ID(只在同一配筋连续柱中不重复)</td>
</tr>
<tr>
<td style="text-align: center;">RcCntColID</td>
<td style="text-align: center;">整型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">　所属配筋连续柱ID</td>
</tr>
<tr>
<td style="text-align: center;">ColSpanDeID</td>
<td style="text-align: center;">整型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">代表柱跨ID</td>
</tr>
<tr>
<td style="text-align: center;"><p>MB_A</p>
<p>MB_B</p>
<p>MB_C</p></td>
<td style="text-align: center;">文本型</td>
<td style="text-align: center;">是</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;"><p>配筋数据：</p>
<p>当矩形截面时，MB_A为角筋、MB_B为B边配筋、MB_C为H边配筋</p>
<p>当为圆形截面时，MB_A为配筋，MB_B和MB_C为空</p>
<p>当为异形柱截面时，MB_A为固定筋、MB_B为分布筋，MB_C为空</p></td>
</tr>
<tr>
<td style="text-align: center;">HB_A</td>
<td style="text-align: center;">文本型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">B边箍筋(异型柱箍筋肢数无意义)</td>
</tr>
<tr>
<td style="text-align: center;">HB_B</td>
<td style="text-align: center;">文本型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">H边箍筋(异型柱箍筋肢数无意义)</td>
</tr>
<tr>
<td style="text-align: center;">HB_C</td>
<td style="text-align: center;">文本型</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">否</td>
<td style="text-align: center;">节点核心区箍筋，保存的肢数无意义，B边、H边肢数与HB_A、HB_B一致</td>
</tr>
</tbody>
</table>

### 柱段信息（tblRcSegInfo）

|  字段名  | 字段类型 | 允许为空 | 主键 |     字段含义     |
|:--------:|:--------:|:--------:|:----:|:----------------:|
|    ID    |   整型   |    否    |  是  |  　建模模型中ID  |
| FloorID  |   整型   |    否    |  否  |  　所属自然层ID  |
| CntColID |   整型   |    否    |  否  |   所属连续柱ID   |
| NoInCol  |   整型   |    否    |  否  | 在连续柱中的序号 |

### 钢筋层（tblRcReiFlr）

| 字段名 | 字段类型 | 允许为空 | 主键 |  字段含义  |
|:------:|:--------:|:--------:|:----:|:----------:|
|   ID   |   整型   |    否    |  是  | 　钢筋层ID |
|  Name  |  文本型  |    否    |  否  | 钢筋层名称 |
