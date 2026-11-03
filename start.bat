@echo off
chcp 65001 > nul
title ระบบขอเบิกพัสดุและคลังพัสดุดิจิทัล มสด. (Stock Order SDU - PostgreSQL 17)
echo ==============================================================================
echo   ระบบขอเบิกพัสดุและคลังพัสดุดิจิทัล มหาวิทยาลัยสวนดุสิต (Stock Order SDU)
echo   PostgreSQL 17 + pgAdmin 4 Edition
echo ==============================================================================
echo.

cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    echo [*] ใช้งาน Python จาก Virtual Environment (.venv)...
    .venv\Scripts\python.exe scripts\launch.py
    goto end
)

where python >nul 2>nul
if %ERRORLEVEL% equ 0 (
    echo [*] ตรวจพบ Python ในระบบ กำลังเปิด Web Server บนพอร์ต 8080...
    python scripts\launch.py
    goto end
)

where py >nul 2>nul
if %ERRORLEVEL% equ 0 (
    echo [*] ตรวจพบ Python Launcher ในระบบ กำลังเปิด Web Server บนพอร์ต 8080...
    py scripts\launch.py
    goto end
)

echo [!] ไม่พบ Python ในเครื่องนี้ กำลังเปิดหน้าระบบผ่านเบราว์เซอร์โดยตรง...
start "" "%~dp0portal.html"

:end
