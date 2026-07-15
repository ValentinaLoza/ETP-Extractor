@echo off
chcp 65001 > nul
title ETP Session Bridge - IPC PT6A-140 TOC
cd /d "%~dp0"

powershell.exe -NoProfile -ExecutionPolicy Bypass ^
  -File "%~dp0ETP_Session_Bridge.ps1" ^
  -ApiPath "/api/manual/toc?partno=3075744&revision=23&lang=en&media=html"

echo.
echo Presiona una tecla para cerrar.
pause > nul
