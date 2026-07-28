@echo off
chcp 65001 >nul
cd /d "%~dp0"
"%~dp0python\python.exe" -c "import sys; sys.path.insert(0, r'%~dp0python\Lib\site-packages'); exec(open(r'%~dp0broadcast-new.py', encoding='utf-8').read())"
pause