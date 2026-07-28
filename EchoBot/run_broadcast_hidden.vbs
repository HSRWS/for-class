Set objShell = CreateObject("WScript.Shell")
objShell.CurrentDirectory = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
cmd = "python\python.exe -c ""import sys; sys.path.insert(0, r'python\Lib\site-packages'); exec(open(r'broadcast-new.py', encoding='utf-8').read())"""
objShell.Run cmd, 0, False