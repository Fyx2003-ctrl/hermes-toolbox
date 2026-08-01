@echo off
title Hermes 技能实时更新
echo ==============================================
echo   Hermes 技能与本体更新
echo ==============================================
echo.

echo [1/2] 更新技能库...
wsl -d Ubuntu-24.04 -e bash -lc "export PATH=$HOME/.local/bin:$PATH; hermes skills update 2>&1 | tail -5"
echo.

echo [2/2] 更新 Hermes 本体...
wsl -d Ubuntu-24.04 -e bash -lc "export PATH=$HOME/.local/bin:$PATH; hermes update 2>&1 | tail -5"
echo.

echo ==============================================
echo   更新完成! 新技能下次对话自动生效
echo ==============================================
pause
