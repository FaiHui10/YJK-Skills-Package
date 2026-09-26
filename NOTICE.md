# 第三方内容与许可声明（NOTICE）

本仓库主体（五个技能的代码与文档、根文档、`fetch_vendor_refs.py`）是本项目的原创内容。
下面列出**随仓库一起分发**的第三方内容及其来源与许可。转载均**原样保留**，未做改写。

---

## 一、厂商二进制（`yjk-auto-drive/assets/`）

| 文件 | 大小 | SHA256（前 16 位） | 来源 |
|---|---|---|---|
| `YJKAPI.dll` | 220,672 B | `0e260eb39a17b06c` | 盈建科官方公开仓库 `gitee.com/yjk-opensource/csharp-yjks`（7.1 分支），路径 `不依赖YJK案例/dll/YJKAPI.dll` |
| `YAPIData.dll` | 76,800 B | `6f900a124fc5d71f` | 同上目录，`YJKAPI.dll` 的依赖数据 DLL |

这两个文件是**盈建科（YJK）官方客户端控制 DLL**，用于通过官方 IPC 通道驱动 YJK，
版权归**北京盈建科软件股份有限公司**所有。放在这里只为让克隆下来的人开箱可用；
不使用它们也能运行（`scripts/paths.py` 的候选链会继续往 YJK 安装目录、用户缓存等处找）。

---

## 二、官方二次开发资料转载（`yjk-dev-refs/`）

`yjk-dev-refs/README.md` 里有逐文件的来源清单；下面是许可概览。

| 来源仓库 | 仓库内 LICENSE | 本仓库对应的转载内容 |
|---|---|---|
| `gitee.com/yjk-opensource/csharp-yjks` | **木兰宽松许可证，第 2 版**（Mulan PSL v2，<http://license.coscl.org.cn/MulanPSL2>）—— 允许复制、使用、修改、分发 | `04-接口说明/*-CSharp.md`、`04-接口说明/*-6x.md`、`03-CSharp案例/`、`05-数据文件说明/`、`06-总信息参数ID表/`、`01-总览与运行方式/` 等 |
| `gitee.com/yjk-opensource/py-yjks` | **Apache License 2.0** —— 允许复制、使用、修改、分发 | `02-Python-API案例/py-yjks官方示例/`、`02-Python-API案例/YJKSControl示例/` |
| `gitee.com/yjk-opensource/yjkapi_-python` | **仓库内没有 LICENSE 文件** | `04-接口说明/*-8x.md`、`02-Python-API案例/不依赖YJK案例/`、`02-Python-API案例/依赖YJK案例/post.py` |

关于第三行（**无许可声明**的那一批）：这批材料的版权同样归**北京盈建科软件股份有限公司**，
本仓库按其公开发布状态**转载以作离线技术参考**，未对其主张任何权利、也未做实质性修改。
本仓库作者已确认按此方式收录；**如需再分发到别处，请自行确认授权**。

---

## 三、名称与商标

YJK、盈建科 是北京盈建科软件股份有限公司的商标。
本仓库是**第三方自动化工具**，与盈建科公司无隶属关系，也未获得其背书；
文中出现这些名称仅为技术引用与互操作说明。

---

## 四、本仓库原创部分的许可

见根目录 [`LICENSE`](LICENSE)。
