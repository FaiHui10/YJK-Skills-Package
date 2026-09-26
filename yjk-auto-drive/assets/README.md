# assets/ 官方客户端 DLL 存放处

## 这里应该有什么

| 文件 | 必需 | 说明 |
|---|---|---|
| `YJKAPI.dll` | 必需 | 官方控制客户端，类型 `YJKIPC.YJKSControl` |
| `YAPIData.dll` | 视版本 | `YJKAPI.dll` 的依赖数据 DLL，与它同目录即可 |

本技能已内置一份可用的 `YJKAPI.dll`（约 216 KB，SHA256 前缀 `0e260eb39a17b06c…`）。
换电脑时连整个 `assets/` 一起拷即可，不用重新取件。

## 如果要从官方仓库重新取件

来源：`gitee.com/yjk-opensource/csharp-yjks` 的 7.1 分支（参考提交 `a0c739e`），路径：

```
不依赖YJK案例/dll/YJKAPI.dll
```

取到后覆盖本目录的同名文件。

## 放在这里 vs 放在别处

脚本按下面顺序找 `YJKAPI.dll`（命中即止）：

1. `--dll <路径>` 命令参数
2. 环境变量 `YJKAPI_DLL`
3. **本目录（`assets/YJKAPI.dll`）** ← 推荐
4. 用户缓存 `~/.yjk-auto/YJKAPI.dll`
5. YJK 安装目录 `STCAD\YJKSControl.dll`（兜底，签名不同）
6. YJK 安装目录 `STCAD\YJKAPI.dll`（无控制类型，会被跳过）
7. 用户目录里 `csharp-yjks` 的检出副本

命中了哪个、跳过了哪些，`scripts/yjk_probe.py` 都会打印。

## 不要用这些

| 文件 | 原因 |
|---|---|
| YJK 安装目录 `STCAD\YJKAPI.dll` | **不含** `YJKSControl` 类型 |
| YJK 8.x SDK 的原生库 | 与 7.1 的原生库**互斥**，混用会崩 |
| 任何 `import YJKAPI` 的写法 | 会 `WinExec` 再拉起一个无窗口 yjks，造成多实例抢事件 |
