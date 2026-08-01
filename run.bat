@echo off
chcp 65001 >nul
cd /d %~dp0
echo 正在启动二次元粒子系统...
".venv-win\Scripts\python.exe" src\main.py %*
pause
