pyYJKSUI.pyd下的方法
//设置脚本状态，仅设置Script状态,设置之后不会有各种弹框出现
def QSetRunScript (bScript: bool)-> bool:
//获取脚本状态
def QGetRunScript (bScript: bool)-> bool:
// 函数功能：运行命令
def QRunCommandEx(lpszCmdString: string, lpCmdParam: string, bFlags: bool)-> bool:
//设置当前标签
def QSetCurrentRibbonLabel(bScript: bool)-> bool:
pyYJKCommand.pyd下的方法
//运行命令，cmdName为命令名称
def RunCommand(cmdName: string)-> bool: