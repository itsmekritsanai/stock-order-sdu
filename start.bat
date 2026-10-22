@echo off
chcp 65001 > nul
title สวนดุสิต - ระบบคลังพัสดุดิจิทัล (Stock Order SDU)

echo ======================================================================
echo   ระบบขอเบิกพัสดุและคลังพัสดุดิจิทัล มหาวิทยาลัยสวนดุสิต
echo   Suan Dusit University - Digital Stock & Requisition System
echo ======================================================================
echo.

:: ตรวจสอบการทำงานของ Local Server บนพอร์ต 8080
netstat -ano | findstr :8080 > nul
if %errorlevel% equ 0 (
    echo [*] เว็บเซิร์ฟเวอร์กำลังทำงานอยู่ที่พอร์ต 8080 (Active)
) else (
    echo [*] กำลังเริ่มทำงาน Local Web Server บนพอร์ต 8080...
    start /B python -m http.server 8080 > nul 2>&1
    timeout /t 2 /nobreak > nul
    echo [*] เซิร์ฟเวอร์พร้อมใช้งานแล้วที่ http://localhost:8080
)

echo.
echo เลือกระบบที่ต้องการเปิดใช้งาน:
echo   [1] เปิดศูนย์กลางเชื่อมต่อพอร์ทัล (portal.html) - [ค่าเริ่มต้น แนะนำ]
echo   [2] เปิดระบบขอเบิกพัสดุ (index.html) - สำหรับอาจารย์/บุคลากร
echo   [3] เปิดระบบบริหารคลังพัสดุ (staff.html) - สำหรับเจ้าหน้าที่
echo   [4] เปิดทั้ง 2 ระบบพร้อมกัน 2 แท็บ (ทดสอบ Real-time Sync)
echo.

set /p choice="กรุณาเลือกหมายเลข [1-4] (กด Enter เพื่อเลือก 1): "

if "%choice%"=="2" (
    echo กำลังเปิดหน้าผู้ขอเบิกพัสดุ...
    start http://localhost:8080/index.html
) else if "%choice%"=="3" (
    echo กำลังเปิดหน้าระบบเจ้าหน้าที่พัสดุ...
    start http://localhost:8080/staff.html
) else if "%choice%"=="4" (
    echo กำลังเปิดทั้ง 2 หน้าต่างพร้อมกันเพื่อทดสอบ Real-time Sync...
    start http://localhost:8080/index.html
    start http://localhost:8080/staff.html
) else (
    echo กำลังเปิดศูนย์กลางเชื่อมต่อพอร์ทัล...
    start http://localhost:8080/portal.html
)

echo.
echo ระบบเปิดทำงานเรียบร้อยแล้ว ท่านสามารถปิดหน้าต่างนี้ได้ทันทีครับ
timeout /t 3 > nul
