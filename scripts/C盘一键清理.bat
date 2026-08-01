@echo off
title C 盘一键清理 (安全项)
echo ==============================================
echo   C 盘安全清理 - 只删缓存, 不动个人文件
echo ==============================================
echo.

set USER=C:\Users\冯翼信

echo [1/9] 用户临时文件...
del /f /q "%USER%\AppData\Local\Temp\*" >nul 2>&1

echo [2/9] 系统临时文件...
del /f /q "C:\Windows\Temp\*" >nul 2>&1

echo [3/9] Windows 更新缓存...
del /f /q "C:\Windows\SoftwareDistribution\Download\*" >nul 2>&1

echo [4/9] Edge 浏览器缓存...
del /f /q "%USER%\AppData\Local\Microsoft\Edge\User Data\Default\Cache\*" >nul 2>&1
del /f /q "%USER%\AppData\Local\Microsoft\Edge\User Data\Default\Code Cache\*" >nul 2>&1

echo [5/9] WPS 组件缓存...
del /f /q "%USER%\AppData\Roaming\Kingsoft\wps\addons\pool\*" >nul 2>&1

echo [6/9] 微信插件缓存...
del /f /q "%USER%\AppData\Roaming\Tencent\WeChat\XPlugin\*" >nul 2>&1
del /f /q "%USER%\AppData\Roaming\Tencent\WeChat\log\*" >nul 2>&1

echo [7/9] 剪映缓存...
del /f /q "%USER%\AppData\Local\JianyingPro\User Data\Cache\*" >nul 2>&1

echo [8/9] 回收站...
powershell -NoProfile -Command "Clear-RecycleBin -Force -ErrorAction SilentlyContinue" >nul 2>&1

echo [9/9] 检查结果...
powershell -NoProfile -Command "$d = Get-PSDrive C; Write-Host ('C 盘可用: ' + [math]::Round($d.Free/1GB,1) + ' GB')"
echo.
echo ==============================================
echo   清理完成! 可配合"存储感知"自动清理
echo ==============================================
pause
