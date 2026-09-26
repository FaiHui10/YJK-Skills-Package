# CSharp YJKS（C# 二次开发 SDK）运行方式

> **来源**：gitee 仓库 [`yjk-opensource/csharp-yjks`](https://gitee.com/yjk-opensource/csharp-yjks)
> —— 盈建科官方 YJKS C# 二次开发 SDK 说明文档。
> 本文是仓库内 `README.md`、`说明文档\运行说明.md`、`说明文档\CSharpYJKS运行说明.md`
> 三份原文的**合并整理**：正文凡引用原文之处均逐字保留，仅做编排。
> 原文中的截图以 `【原文此处为截图】` 标出。

---

## 一、CSharpYJKS 是什么

### 介绍（原文）

> CSharpYJKS是盈建科结构设计软件基于Csharp语言提供的二次开发接口，用户可以使用CSharpYJKS对盈建科建筑结构计算软件进行二次开发,目前支持模型创建及荷载施加功能。

### 软件架构（原文）

> 目前支持不依赖YJK进程的情况下实现YDB文件的创建及读取修改，和依赖YJK进程情况下的建模、特殊构件定义及设计结果获取，搭配YJKSControl还可以实现循环计算、命令流形式的实时命令调用等功能。

因此 C# SDK 有两种使用形态，本包内的案例按此分为两个目录：

| 形态 | 案例目录 | 说明 |
|---|---|---|
| **不依赖 YJK 进程** | `03-CSharp案例\不依赖YJK案例\` | 仅用 DLL 生成 / 读写 `.ydb`，不需要启动 YJK |
| **依赖 YJK 进程** | `03-CSharp案例\依赖YJK案例\` | 作为插件在 YJK 内运行（`yjks_csload` 加载），可读设计结果、注册命令 |

---

## 二、安装与编译运行

### CSharpYJKS_V1.0 文档说明 — 一、安装运行说明（原文）

> 以Visual Studio 2017为例，勾选.NET桌面开发选项并进行安装。
>
> 【原文此处为截图】
>
> 将文件夹dll中的动态库文件复制到相应的Debug文件夹或Release文件夹下。
>
> 【原文此处为截图】
>
> 设置好VS中的解决方案配置、解决方案平台、启动项目及引用文件。
>
> 【原文此处为截图】
>
> 在代码中修改生成ydb文件的目标地址，启动项目（F5），出现“运行完成！”提示，表示程序运行成功，生成ydb。
>
> 【原文此处为截图】
>
> 在YJK中导入生成的ydb文件。

### 仓库 README 的等价步骤（原文）

> 1. 以Visual Studio 2017为例，勾选.NET桌面开发选项并进行安装。
> 2. 将文件夹dll中的动态库文件复制到相应的Debug文件夹或Release文件夹下。
> 3. 设置好VS中的解决方案配置、解决方案平台、启动项目及引用文件。
> 4. 在代码中修改生成ydb文件的目标地址，启动项目（F5），出现“运行完成！”提示，表示程序运行成功，生成ydb。

### 常见问题（原文）

> **Q1：程序集“RevitYjkND.dll”或它的某一个依赖向，找不到指定的模块**
>
> 【原文此处为截图】
>
> 解决方式：需要把dll中的内容复制到debug或release目录下

> ⚠️ **本参考集不包含任何 DLL / 动态库**。仓库中的 `dll\` 目录、
> `YJK替换文件\`、`不依赖YJK案例\dll\` 等二进制内容**未被复制**，
> 请从原始仓库或 YJK 安装目录获取（见 `README.md` 的“未复制的二进制”一节）。

---

## 三、不依赖 YJK 进程的用法（核心套路）

本包内 19 个 C# 案例几乎都遵循同一个骨架（下面逐字摘自
`03-CSharp案例\不依赖YJK案例\ConsoleApp1\kjtest.cs`，省略处标 `// ...`）：

```csharp
using CsToYjk;
using APIData;
using DataFuncApplication;

//本代码案例为创建一个框架结构模型，并于指定路径下生成ydb。
namespace ConsoleApp1
{
    class kjtest
    {
        static void Main(string[] args)
        {
            DataFunc dataFunc = new DataFunc();
            //标准层
            Mdl_StdFlr StdFlr = dataFunc.StdFlr_Generate(3900);
            //截面定义
            Mdl_ColSect defcol = dataFunc.ColSect_Def(6, 1, "400,400");
            // ... 节点 / 网格 / 构件 / 柱帽 / 板 / 荷载 ...
            //标准层复制
            dataFunc.Floors_Assemb(0, StdFlr, 6, 3600);
            //提交建模数据
            dataFunc.DbModel_Assign();
            Hi_DbModelData model = dataFunc.GetDbModelData();
            Hi_AddToAndReadYjk my = new Hi_AddToAndReadYjk(model);
            bool isok = my.CreateYDB(@"..\..\", "kj.ydb");
            if (isok) Console.WriteLine("运行完成！");
            Console.ReadLine();
        }
    }
}
```

要点：

- `DataFunc` 是“内存模型”工厂：定义标准层、截面、节点、网格、构件、荷载。
- `dataFunc.GetDbModelData()` 取出 `Hi_DbModelData`，再交给 `Hi_AddToAndReadYjk`。
- `CreateYDB(目录, 文件名)` 落盘为 `.ydb`；之后的建模、特殊构件、设计结果接口都建立在它之上。
- **不需要启动 YJK 界面**，这是本包 `yjk-auto-drive` / `column-section-opt` /
  `floor-system-comparison` 等技能可以做批量试算的基础。
- 需引用的程序集为 `CsToYjk` / `APIData` / `DataFuncApplication`（来自仓库 `dll\`，本包未收录）。

对应的 Python 版本见 `01-总览与运行方式\Python-API-运行方式.md`（API 名称不同，思路与函数名几乎一一对应）。

---

## 四、依赖 YJK 进程 + 外部控制（YJKSControl）

以下为 `说明文档\运行说明.md` **逐字**内容（仅将截图替换为标记）：

> 需要在C:\ProgramData\yjkSoft\YJKS5.1\YJKS\Config.ini文件中补充如下内容：
>
> 【原文此处为截图】
>
> ```ini
> [YJKSControl]
> Flag = False
> ```
>
> 在案例文件中更改YJKSControl.init函数中对应的yjks.exed的路径、YJK的版本以及yjk_opennew命令中对应的模型文件地址，然后运行案例文件。
>
> 【原文此处为截图】
>
> 【原文此处为截图】
>
> 对命令进行单独测试需要手动修改C:\ProgramData\yjkSoft\YJKS5.1\YJKS\Config.ini文件中的Flag为True，成功启动YJK之后再运行脚本，完成后需要手动将Flag再切换回False（否则无法进入正常界面下的yjk）。
>
> ```ini
> [YJKSControl]
> Flag = True
> ```
>
> **注意事项:**
>
> - 不要启动多个支持外部控制的yjks.exe，否则执行外部控制会引发异常。
> - 可通过YJKSControl调用二次开发插件（yjks_csload、yjks_pyload）的命令，更细致的内容可在插件中完成。
> - 可通过YJKSControl调用二次开发插件的命令，更细致的内容可在插件中完成。
> - 目前YJKSControl的功能需要授权，授权仅为方便管理，可向当地技术支持的同事申请API授权码。

### 6.1 及之后版本（原文）

> 1. 可不用在Config.ini文件中补充内容，启动YJK软件后输入命令 **yjksIPCControl** 即可开启yjkscontrol，在代码中仅保留运行命令的语句。
> 2. yjkscontrol开启的界面状态和常规状态同步，不再有区分。
> 3. 新增工程选择界面（有欢迎使用盈建科软件!的界面）的项目新建和项目打开的命令控制（UINew/ UIOpen）。
> 4. 解决在开启yjkscontrol状态下用YjkLauncher.exe启动时会出现两个显示窗口的问题。
> 5. 若需要在自动启动yjk时就开启yjkscontrol，请按照之前的方式在Config.ini文件中补充内容。

### 8.0 及之后版本（原文）

> 1. 可选择控制当前启动的某个YJK进程。

### 相关案例与接口

- 案例：`03-CSharp案例\不依赖YJK案例\ConsoleApp10\yjkipc.cs`（`YJKIPC` / `YJKSControl` / `YJKS_All_8`）
- 案例：`03-CSharp案例\不依赖YJK案例\ConsoleApp15\linkYjk.cs`（`Hi_UpdateInfo` 联动）
- 案例：`03-CSharp案例\依赖YJK案例\ConsoleApp5\`（从导入 ydb 至计算完成的全流程控制）
- 接口：`04-接口说明\UI接口及命令接口说明.md`（`ClrYJKSUI` / `ClrYJKSCommand`）
- 命令表：`04-接口说明\命令说明文档.md`

> 📌 `yjk-auto-drive` 技能驱动的正是这一层：`ClrYJKSCommand.CsRunCommand` / `CsQRunCommandEx`
> 加上 `yjksIPCControl` 打开的外部控制通道，即可把 YJK 当作可编排的进程来跑命令流。

---

## 五、命令注册（插件形态）

`依赖YJK案例\ConsoleApp8` 演示“用户可通过一个 dll 向 YJK 平台完成多个命令的注册”；
`ConsoleApp8\dll\dtlPlugList.txt` 是命令注册清单样例。
相关接口见 `04-接口说明\UI接口及命令接口说明.md`。

---

## 六、源码位置

| 内容 | 本包位置 |
|---|---|
| 不依赖进程的 19 个案例 | `03-CSharp案例\不依赖YJK案例\ConsoleApp1 … ConsoleApp19\` |
| 依赖进程的案例 | `03-CSharp案例\依赖YJK案例\ConsoleApp5 / ConsoleApp8 / ConsoleApp9 / ConsoleApp14 / CSharp后处理 / 自定义按钮演示\` |
| 官方案例说明原文 | `03-CSharp案例\...` 各目录内的 `操作说明.txt` / `说明.txt`，以及 `04-接口说明` 内的接口文档 |
