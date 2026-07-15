@echo off
chcp 65001 > nul
title ETP Session Bridge v0.3
cd /d "%~dp0"

powershell.exe -NoProfile -ExecutionPolicy Bypass ^
  -File "%~dp0ETP_Session_Bridge.ps1"

echo.
echo Presiona una tecla para cerrar.
pause > nul
