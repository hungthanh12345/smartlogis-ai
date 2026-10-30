@echo off
chcp 65001 >nul
title SmartLogis AI - Quickstart Launcher
cd /d %~dp0

echo =====================================================================
echo           SMARTLOGIS AI - HE THONG QUAN LY KHO TICH HOP AI
echo                   [KHOI DONG HE THONG TONG THE]
echo =====================================================================
echo [*] Chuyen huong vao thu muc backend/ de khoi chay may chu...
echo.

:: Cau hinh uvicorn voi --reload-dir app de tranh reload khi ghi CSDL SQLite
if exist "%~dp0backend\run_app.bat" (
    cd /d "%~dp0backend"
    call run_app.bat
) else (
    echo [LOI] Khong tim thay backend\run_app.bat!
    pause
    exit /b 1
)
