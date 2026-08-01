@echo off
title WSL 迁移到 D 盘 (自动备份, 可回滚)
echo ==============================================
echo   WSL 迁移到 D 盘 - 一键脚本
echo   含自动备份, 迁移失败可回滚, 数据零风险
echo ==============================================
echo.
echo [警告] 迁移过程中 WSL 会关闭约 5-10 分钟,
echo        期间微信远程助手会暂时断联, 属正常现象
echo.
pause

cd /d %~dp0

echo.
echo [1/6] 确认 WSL 发行版...
set DISTRO=Ubuntu-24.04
echo      发行版: %DISTRO%
wsl -d "%DISTRO%" -e echo "发行版访问正常" >nul 2>&1
if errorlevel 1 (
    echo [错误] 无法访问 %DISTRO% ! 请修改脚本中的发行版名称
    pause
    exit /b 1
)

echo.
echo [2/6] 创建目标目录 D:\WSL ...
mkdir D:\WSL 2>nul

echo.
echo [3/6] 备份当前系统到 D:\WSL\backup-%DISTRO%.tar ...
wsl --shutdown
wsl --export "%DISTRO%" "D:\WSL\backup-%DISTRO%.tar"
if errorlevel 1 (
    echo [错误] 备份失败! 系统未做任何更改
    pause
    exit /b 1
)

echo.
echo [4/6] 迁移到 D:\WSL\%DISTRO% ...
wsl --unregister "%DISTRO%"
if errorlevel 1 (
    echo [错误] 注销失败! 可用备份恢复:
    echo       wsl --import "%DISTRO%" "%LOCALAPPDATA%\wsl" "D:\WSL\backup-%DISTRO%.tar"
    pause
    exit /b 1
)
wsl --import "%DISTRO%" "D:\WSL\%DISTRO%" "D:\WSL\backup-%DISTRO%.tar" --version 2
if errorlevel 1 (
    echo [错误] 导入失败! 正在自动回滚...
    wsl --import "%DISTRO%" "%LOCALAPPDATA%\wsl" "D:\WSL\backup-%DISTRO%.tar" --version 2
    echo 回滚完成
    pause
    exit /b 1
)

echo.
echo [5/6] 设置默认用户...
wsl -d "%DISTRO%" -u root -e sh -c "echo '[user]' > /etc/wsl.conf && echo 'default=fyxacxg1379' >> /etc/wsl.conf"
wsl --shutdown
timeout /t 3

echo.
echo [6/6] 清理临时备份...
del "D:\WSL\backup-%DISTRO%.tar"
echo.
echo ==============================================
echo   OK! WSL 已迁移到: D:\WSL\%DISTRO%
echo   C 盘释放约 6.6GB
echo ==============================================
pause
