@echo off
title 数据保存路径迁移到 D 盘 (源头解决)
echo ==============================================
echo   数据路径迁移 - 从源头解决 C 盘膨胀
echo   下载/文档/图片等默认保存到 D 盘
echo ==============================================
echo.

set USER=C:\Users\冯翼信

echo [1/5] 创建 D 盘数据目录...
mkdir D:\UserData 2>nul
mkdir D:\UserData\Downloads 2>nul
mkdir D:\UserData\Documents 2>nul
mkdir D:\UserData\Pictures 2>nul
mkdir D:\UserData\Videos 2>nul
mkdir D:\UserData\Music 2>nul
echo       D:\UserData 已创建

echo [2/5] 迁移现有下载文件...
robocopy "%USER%\Downloads" "D:\UserData\Downloads" /E /MOVE /R:1 /W:1 /NFL /NDL >nul 2>&1
echo       下载文件已迁移

echo [3/5] 设置系统默认保存位置到 D 盘...
powershell -NoProfile -Command "
$sh = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders'
Set-ItemProperty -Path $sh -Name '{374DE290-123F-4565-9164-39C4925E467B}' -Value 'D:\UserData\Downloads' -Type ExpandString
Set-ItemProperty -Path $sh -Name '{FDD39AD0-238F-46AF-ADB4-6C85480369C7}' -Value 'D:\UserData\Documents' -Type ExpandString
Set-ItemProperty -Path $sh -Name '{33E28130-4E1E-4676-835A-98395C3BC3BB}' -Value 'D:\UserData\Pictures' -Type ExpandString
Set-ItemProperty -Path $sh -Name '{18989B1D-99B5-455B-841C-AB7C74E4DDFC}' -Value 'D:\UserData\Videos' -Type ExpandString
Set-ItemProperty -Path $sh -Name '{A0C69A99-21C8-4671-8703-7934162FCF1D}' -Value 'D:\UserData\Music' -Type ExpandString
Write-Host '系统默认位置已设置'
"

echo [4/5] 重启资源管理器使设置生效...
taskkill /f /im explorer.exe >nul 2>&1
start explorer.exe

echo [5/5] 完成!
echo.
echo ==============================================
echo   ? 数据路径已迁移到 D 盘!
echo   - 以后浏览器下载/保存文件默认进 D:\UserData
echo   - 桌面/文档在 OneDrive 不受影响
echo.
echo   ? 额外建议:
echo   - 安装新软件时手动选择 D 盘
echo   - 游戏安装时选择 D 盘
echo   - 各软件内"设置-存储位置"也改到 D 盘
echo ==============================================
pause
