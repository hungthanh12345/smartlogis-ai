@echo off
chcp 65001 >nul
title SmartLogis AI - Quickstart Launcher
cd /d %~dp0

echo =====================================================================
echo           SMARTLOGIS AI - HE THONG QUAN LY KHO TICH HOP AI
echo =====================================================================
echo [1] Kiem tra moi truong Python...

set "PYTHON_CMD="
if exist ".\venv\Scripts\python.exe" set "PYTHON_CMD=.\venv\Scripts\python.exe"

if not defined PYTHON_CMD (
    python -c "import sys; sys.exit(0)" >nul 2>&1
    if not errorlevel 1 set "PYTHON_CMD=python"
)

if not defined PYTHON_CMD (
    py -c "import sys; sys.exit(0)" >nul 2>&1
    if not errorlevel 1 set "PYTHON_CMD=py"
)

if not defined PYTHON_CMD (
    echo [LOI] Khong tim thay trinh thong dich Python tren may tinh.
    echo Vui long cai dat Python hoac khoi tao virtualenv.
    pause
    exit /b 1
)

echo [+] Su dung Python: %PYTHON_CMD%
echo.
echo [2] Kiem tra du lieu CSDL kho...
%PYTHON_CMD% -c "from app.core.database import SessionLocal; from app.models.inventory_models import NguoiDung; db=SessionLocal(); has_admin = db.query(NguoiDung).filter_by(TenDangNhap='admin').first() is not None; db.close(); exit(0 if has_admin else 1)" >nul 2>&1
if errorlevel 1 (
    echo [*] Dang tu dong nap du lieu mau [Demo Seeder]...
    %PYTHON_CMD% scripts\seed_data.py
    %PYTHON_CMD% scripts\migrate_v2_constraints_indexes.py
) else (
    echo [+] Co so du lieu da san sang!
)

echo.
echo =====================================================================
echo   MAY CHU DANG CHAY TAI:
echo   - Giao dien Web:     http://127.0.0.1:8000
echo   - Tai lieu API:      http://127.0.0.1:8000/docs
echo.
echo   TAI KHOAN DEMO:
echo   - Admin:                 admin   / admin123
echo   - Thu kho kiem Ke toan:  thukho  / thukho123
echo =====================================================================
echo.

:: Tu dong mo trinh duyet sau 3 giay (cho server khoi dong xong)
start "" /b cmd /c "ping 127.0.0.1 -n 3 >nul & start http://127.0.0.1:8000/login"

:: Khoi chay Uvicorn Server (chi theo doi thu muc app de tranh reload khi ghi CSDL SQLite)
%PYTHON_CMD% -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload --reload-dir app
pause

