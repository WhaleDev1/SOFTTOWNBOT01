@echo off
title Discord Bot Auto Runner

:: รัน bot.py ในหน้าต่างใหม่
start "" cmd /c "python bot.py"

:: รัน server.py ในหน้าต่างใหม่
start "" cmd /c "python server.py"

:: ปิดไฟล์ .bat ทันทีหลังสั่งรัน
exit
