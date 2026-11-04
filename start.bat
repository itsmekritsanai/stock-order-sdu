@echo off
cd /d "%~dp0"
title SDU Stock Order Server (Port 8080)

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" scripts\launch.py
    goto end
)

where python >nul 2>nul
if %ERRORLEVEL% equ 0 (
    python scripts\launch.py
    goto end
)

where py >nul 2>nul
if %ERRORLEVEL% equ 0 (
    py scripts\launch.py
    goto end
)

start "" "%~dp0portal.html"

:end
pause
