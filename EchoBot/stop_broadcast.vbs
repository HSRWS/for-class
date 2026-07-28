Set objShell = CreateObject("WScript.Shell")
objShell.Run "taskkill /f /im python.exe", 0, False
MsgBox "广播机器人已停止", 64, "提示"