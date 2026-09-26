# Python API 运行方式（6.x 与 8.x 两套并存）

> **来源**：两个 gitee 仓库的运行说明合并
>
> - [`yjk-opensource/py-yjks`](https://gitee.com/yjk-opensource/py-yjks) —— 说明文档及案例
>   内的 `运行说明.md`、`Python二次开发Api运行说明.md`、`README.md`
> - [`yjk-opensource/yjkapi_-python`](https://gitee.com/yjk-opensource/yjkapi_-python) —— 仓库 `README.md`
>
> 两套 API **不是同一个东西**，环境与运行方式都不同，务必按下表对号入座。
> 原文内容逐字保留，截图以 `【原文此处为截图】` 标出。

---

## 0. 先看版本分野（最容易踩的坑）

| | **py-yjks（旧）** | **yjkapi_-python（新）** |
|---|---|---|
| 目标 YJK 版本 | **YJK 6.1** | **YJK 8.x（README 写作 8.0，SDK 包为 8.1）** |
| Python 版本 | **Python 3.8**（原文明确“推荐 3.8.4”） | **Python 3.10**（用**软件安装目录自带**的解释器） |
| 包名 / 导入 | `pyYJKSModel` / `pyYJKSUI` / `pyYJKSPre` / `pyYJKSParam` / `pyYJKSPCommand` / `pyYJKSDesign` 等若干 `.pyd` | 单一入口 `from YJKAPI import *` |
| SDK 获取方式 | 仓库内“替换文件”复制进 YJK 安装目录 | **已集成进软件安装环境**，解压 `SDK\8.1.rar` 到安装目录，用安装目录的 Python 解释器 |
| 接口文档 | `04-接口说明\*-6x.md` | `04-接口说明\*-8x.md` |
| 参考案例 | `02-Python-API案例\py-yjks官方示例\`、`02-Python-API案例\YJKSControl示例\` | `02-Python-API案例\不依赖YJK案例\`、`02-Python-API案例\依赖YJK案例\` |

> `py-yjks` 的坐标是 **YJK 6.1 + Python 3.8**；
> `yjkapi_-python` 的坐标是 **YJK 8.x + Python 3.10**。
> 两者的 `#define` 参数ID体系（`YP_*` / `YPV_*`）与命令体系是一致的，
> 所以 `06-总信息参数ID表\参数ID速查.md` 对两套都适用。

---

## 一、py-yjks（YJK 6.1 + Python 3.8）

### 介绍（原文，`py-yjks\README.md`）

> pyYJKS是盈建科结构设计软件基于Python语言提供的二次开发接口，用户可以使用pyYJKS对盈建科建筑结构计算软件进行二次开发，实现模型、项目、构件参数化批量创建、批量修改、自定义荷载施加、前处理、自动计算、提取设计结果、模型迭代优化、参数化出图、智能设计、个性化定制等；pyYJKS结合Python强大且丰富的第三方扩展库可以为结构设计赋予无限发展空间。

### 模块与API（原文）

> pyYJKS是建立在盈建科结构设计软件基础之上的，其模块需要在YJK-A运行时才能够工作， pyYJKS提供一整套机制来扩展和展示YJK-A的功能。pyYJKS程序包含了读写YJK-A中DB级别的**pyYJKSModel**模块、YJK-A的所有界面操作和定制YJK-A UI的**pyYJKSUI**模块、对模型进行前处理的**pyYJKSPre**模块、对构件添加特殊构件属性定义的**pyYJKSParam**模块、执行和自定义YJK-A命令的**pyYJKSCommand**模块以及整体数据输出和构件设计结果输出的设计结果**pyYJKSDesign**模块。

### 安装教程（原文）

> 注意：为了避免因python版本导致的奔溃无法运行的问题，请安装**3.8.4**版本python。
>
> 1. 安装python3.8.4
>    【原文此处为截图】
> 2. 将替换文件中的内容复制并替换到YJK安装目录下（可参考视频）
> 3. 将python安装文件下的 **python38.dll** 复制替换到YJK安装目录下（可参考视频）
> 4. 安装Numpy库

### 运行说明 — `Python二次开发Api运行说明.md`（原文，截图已标出）

> Python二次开发Api运行说明
>
> **运行说明**
>
> （1）安装python，推荐3.8.4版本的python（其它版本可能会出问题）。
> 【原文此处为截图】
>
> （2）安装python的numpy库
> 可通过输入 `pip list` 命令查看是否成功安装
> 【原文此处为截图】
>
> （3）选择对应YJK版本和Python版本的替换文件，替换到YJK安装路径下
> 【原文此处为截图】
>
> （4）运行YJK，在命令行输入 **`yjks_pyload`** 命令加载写好的py文件
> 【原文此处为截图】
>
> **常见问题**
>
> Q1: “No module named ‘numpy’ ”
> 【原文此处为截图】
> 解决方法：安装python的numpy库
>
> Q2: 输入命令之后YJK直接闪退
> 解决方法：python版本不正确，请安装3.8.4版本的python。

### 使用说明（原文，`py-yjks\README.md`）

> 1. 安装包内包含操作流程视频与API文档，使用前请阅读使用说明。
> 2. 在YJK中运行命令 `yjks_pyload` 加载py文件（可重复执行）
> 3. 导入py文件并生成模型
> 4. 运行结果及错误信息

> ⚠️ 本参考集**不含** `py-yjks` 的“替换文件”、`.pyd`、视频与安装包，
> 只收录了说明文档与官方 `.py` 案例源码。

---

## 二、yjkapi_-python（YJK 8.x + Python 3.10）

### 介绍（原文，`yjkapi_-python\README.md`）

> # YJKAPI 8.0 👋
>
> #### 介绍 📚
> 盈建科新版python API 8.0

### 使用方式（原文）

> ❕ 为了方便与主软件的兼容和支持Agent智能建模自定义工具函数，**YJKAPI将被集成在软件安装环境中，不再提供单独的安装包。**
>
> **1. 配置python环境**:
> - 安装8.0版本软件
> - 将SDK目录下的 **8.0.rar** 压缩包解压并复制到安装目录下，替换文件
> - 打开vscode，选择安装目录的python解释器（Ctrl+Shift+P，输入 select interpreter，选择python解释器），环境中已经安装好了YJKAPI
>   选择安装目录下的 **python3.10** 解释器
>
> **2. 运行YJKAPI案例**:
> - **不依赖软件运行时的脚本**，依旧通过YJKAPI编写脚本
>   ```python
>   from YJKAPI import *
>   ```
> - **依赖软件运行时的脚本**，需要打开软件，通过 `yjks_pyload` 命令执行
>
> **3. 安装其他python库(windows)**
> - powershell
>   ```powershell
>   # 浏览python环境
>   & "C:\YJKS\YJKS_8_0_0\Python310\python.exe" -m pip list
>
>   # 安装其他python库
>   & "C:\YJKS\YJKS_8_0_0\Python310\python.exe" -m pip install -r requirements.txt
>   ```
> - cmd
>   ```cmd
>   # 方法1：直接使用引号
>   "C:\YJKS\YJKS_8_0_0\Python310\python.exe" -m pip list
>
>   # 方法2：先切换到目录
>   cd /d "C:\YJKS\YJKS_8_0_0\Python310"
>   python.exe -m pip list
>
>   # 方法3：使用pip.exe
>   "C:\YJKS\YJKS_8_0_0\Python310\Scripts\pip.exe" list
>   ```

> 📌 **关于压缩包名字**：仓库 README 正文写的是 `SDK目录下的 8.0.rar`，
> 而仓库里实际存在的文件是 **`yjkapi_-python\SDK\8.1.rar`（约 23.8 MB）**。
> 该二进制 **未被复制到本参考集**，需要时请从原仓库下载。
> 操作步骤不变：**解压到 YJK 安装目录 → 用安装目录自带的 Python 解释器 → `from YJKAPI import *`**。

### 后续开发计划（原文）

> - [ ] 在软件安装包中集成python310环境和相关文件
> - [ ] Agent智能建模自定义工具函数
>   - 通过YJKAPI编写自定义工具函数，agent解析工具函数并执行

---

## 三、两种运行姿态（8.x 案例均适用）

| 姿态 | 是否需要开 YJK | 写法 | 本包案例 |
|---|---|---|---|
| **不依赖软件运行时** | 否 | `from YJKAPI import *`，直接 `Hi_AddToAndReadYjk(model)` + `CreateYDB(...)` | `02-Python-API案例\不依赖YJK案例\案例1…案例18` |
| **依赖软件运行时** | 是 | 打开软件 → 命令行 `yjks_pyload` 执行脚本 | `02-Python-API案例\依赖YJK案例\post.py`、`案例10_远程控制`、`案例15_联动` |

不依赖姿态的最小骨架（摘自 `案例1_框架结构\kj.py`）：

```python
# 本代码案例为创建一个框架结构模型，并于指定路径下生成ydb。
from YJKAPI import *

dataFunc = DataFunc()
# 标准层
StdFlr = dataFunc.StdFlr_Generate(3900)
# 截面定义
defcol = dataFunc.ColSect_Def(6, 1, "400,400")
defbeam1 = dataFunc.BeamSect_Def(6, 1, "250,600")
# ... 节点 / 网格 / 构件 / 荷载 ...
# 标准层复制
dataFunc.Floors_Assemb(0, StdFlr, 6, 3600)
# 提交建模数据
dataFunc.DbModel_Assign()
model = dataFunc.GetDbModelData()
my = Hi_AddToAndReadYjk(model)
# current_directory=r"E:\MyProject\9.python_api_new中文"
current_directory=os.getcwd()
isok = my.CreateYDB(current_directory, "kj.ydb")
```

> 上面除注释标注 `# ...` 的一行为省略外，其余各行**逐字取自**
> `02-Python-API案例\不依赖YJK案例\案例1_框架结构\kj.py`。
> 注意函数名是 `Floors_Assemb`（不是 Assemble），以源码为准。

前处理计算参数的设置方式见 `06-总信息参数ID表\参数ID速查.md` 第一节
（`dataFunc.ProjectPara_Set(228, "22804")`，即 **参数ID × 100 + 枚举序号**）。

---

## 四、外部控制（YJKSControl）在 Python 侧

`py-yjks` 的 `运行说明.md` 与 C# 版内容同源，Python 侧额外给出调用样例：

> 在案例文件中更改YJKSControl.init函数中对应的yjks.exe的路径、YJK的版本以及yjk_opennew命令中对应的模型文件地址，然后运行案例文件。
>
> ```python
> YJKSControl.init(r"E:\YJK5.1\5.1_1027\yjks.exe","5.1")
> RunCmd("yjk_opennew", r"C:\Users\10497\Desktop\例子\test\1")
> ```
>
> 对命令进行单独测试需要手动修改 `C:\ProgramData\yjkSoft\YJKS5.1\YJKS\Config.ini` 文件中的Flag为True，成功启动YJK之后再运行脚本，完成后需要手动将Flag再切换回False（否则无法进入正常界面下的yjk）。
>
> **注意事项:**
>
> - 不要启动多个支持外部控制的yjks.exe，否则执行外部控制会引发异常。
> - **目前对带参数的命令只支持传输路径的情况。**
> - 可通过YJKSControl调用二次开发插件的命令，更细致的内容可在插件中完成。
> - **上传的YJKSControl仅针对于python3.8版本。**
> - 目前YJKSControl的功能需要授权，授权仅为方便管理，可向当地技术支持的同事申请API授权码。
>
> 6.1版本：不用在Config.ini文件中补充内容，直接启动YJK软件后输入命令 **`yjksIPCcontrol`** 即可开启yjkscontrol。

案例：`02-Python-API案例\YJKSControl示例\test1.py / test2.py / test3.py`。

---

## 五、被引用为“原文以截图为主”的小文档

以下原文体量极小、以截图为主，但**均已在 `01-总览与运行方式\` 或 `04-接口说明\` 中保留原文**：

| 原文 | 大小 | 本包位置 | 说明 |
|---|---|---|---|
| `py-yjks\Python二次开发Api运行说明.md` | 633 B | 本文第一节 | 4 步安装 + 2 个常见问题，正文为文字，附图 6 张未收录 |
| `py-yjks\UI接口及命令接口说明.md` | 519 B | `04-接口说明\UI接口及命令接口说明-6x.md` | pyYJKSUI / pyYJKCommand 方法签名，纯文字 |
| `py-yjks\前处理接口说明.md` | 1.9 KB | `04-接口说明\前处理接口说明-6x.md` | CtoSDesign 的 Python 签名，纯文字 |
| `py-yjks\案例说明.md` | 1.3 KB | `01-总览与运行方式\案例总览.md` | 官方示例一句话说明表 |
| `csharp-yjks\CSharpYJKS运行说明.md` | 719 B | `01-总览与运行方式\CSharp-SDK运行方式.md` | 安装 4 步，附图未收录 |
