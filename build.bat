@echo off
chcp 65001 >nul
title 粒子周报... 不, 粒子角色系统 - 一键打包EXE
echo ============================================
echo   二次元角色粒子系统 - 一键打包 EXE
echo ============================================
echo.

cd /d %~dp0

REM ---- 检查 Python ----
where python >nul 2>nul
if errorlevel 1 (
    echo [错误] 未检测到 Python!
    echo 请先安装 Python 3.9+: https://www.python.org/downloads/
    echo 安装时务必勾选 "Add Python to PATH"
    pause
    exit /b 1
)

REM ---- 创建虚拟环境 ----
if not exist .venv-win (
    echo [1/3] 创建虚拟环境...
    python -m venv .venv-win
)

echo [2/3] 安装依赖 (首次需要几分钟)...
".venv-win\Scripts\python.exe" -m pip install -q --upgrade pip
".venv-win\Scripts\python.exe" -m pip install -q -r requirements.txt
if errorlevel 1 (
    echo [错误] 依赖安装失败, 请检查网络
    pause
    exit /b 1
)

echo [3/3] 打包 EXE...
cd src
"..\.venv-win\Scripts\python.exe" -m PyInstaller --noconfirm --onefile --windowed ^
    --name "AnimeParticles" ^
    --add-data "character_gen.py;." ^
    main.py
cd ..

echo.
echo ============================================
echo   打包完成!
echo   生成的 EXE 在: dist\AnimeParticles.exe
echo.
echo   使用方法:
echo     AnimeParticles.exe                 默认角色 (初音未来)
echo     AnimeParticles.exe --character kurumi
echo     AnimeParticles.exe --image 图片.png
echo     AnimeParticles.exe --fullscreen
echo ============================================
pause
