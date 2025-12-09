@echo off
title Installing Requirements...

echo ===================================================
echo     Discord Verification Bot - Installer
echo ===================================================
echo.
echo [1/5] Installing discord.py...
pip install discord.py

echo.
echo [2/5] Installing Flask...
pip install flask

echo.
echo [3/5] Installing Requests...
pip install requests

echo.
echo [4/5] Installing Python-Dateutil...
pip install python-dateutil

echo.
echo [5/5] Installing python-dotenv (for .env support)...
pip install python-dotenv

echo.
echo ===================================================
echo     Installation Complete! (เสร็จสิ้น)
echo ===================================================
echo.
pause
