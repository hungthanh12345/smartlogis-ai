@echo off
chcp 65001 >nul
title SmartLogis AI - Mo Tuong Lua Windows
cd /d "%~dp0"

:: 1. Neu da chay voi co --elevated thi vao thang phan cau hinh tuong lua (Chong lap 100%)
if "%1"=="--elevated" goto :RUN_FIREWALL

:: 2. Kiem tra quyen Administrator
powershell -NoProfile -Command "if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) { exit 1 }" >nul 2>&1
if %errorlevel% equ 0 goto :RUN_FIREWALL

:: 3. Neu chua co quyen, yeu cau UAC dung 1 lan duy nhat
echo [THONG BAO] Dang yeu cau quyen Administrator de mo Tuong lua Windows...
echo Vui long nhan 'Yes' o cua so xac nhan UAC neu co...
powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process cmd.exe -ArgumentList '/k \"\"%~f0\" --elevated\"' -Verb RunAs" 2>nul
if %errorlevel% neq 0 (
    echo.
    echo [!] Khong the lay quyen Administrator hoac ban da chon 'No'.
    echo     De mo thu cong: Nhap chuot phai vao file ^> Chon 'Run as administrator'.
    echo.
    pause
)
exit /b

:RUN_FIREWALL
cls
echo ===============================================================================
echo            SMARTLOGIS AI - CAU HINH TUONG LUA WINDOWS DEFENDER
echo ===============================================================================
echo.
echo [1/2] Dang mo cac cong Port 80, Port 443 va Port 8000 tren Windows Firewall...

:: Xoa cac luat cu neu co de tranh xung dot
netsh advfirewall firewall delete rule name="SmartLogis AI Server" >nul 2>&1

:: Them luat Inbound cho phep Port 80, 443, 8000
netsh advfirewall firewall add rule name="SmartLogis AI Server" dir=in action=allow protocol=TCP localport=80,443,8000 profile=any >nul

if %errorlevel% equ 0 (
    echo [OK] Da mo thanh cong cac cong: Port 80, Port 443 va Port 8000!
) else (
    echo [!] Dang ap dung luat bo sung qua PowerShell...
    powershell -NoProfile -Command "New-NetFirewallRule -DisplayName 'SmartLogis AI Server' -Direction Inbound -LocalPort 80,443,8000 -Protocol TCP -Action Allow -ErrorAction SilentlyContinue" >nul 2>&1
    echo [OK] Da ap dung luat tuong lua thanh cong!
)

:: Lay dia chi IP LAN de huong dan ket noi
set LAN_IP=
for /f "tokens=*" %%a in ('python -c "import socket; s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.connect(('8.8.8.8',80)); print(s.getsockname()[0]); s.close()" 2^>nul') do set LAN_IP=%%a
if "%LAN_IP%"=="" set LAN_IP=127.0.0.1

echo.
echo ===============================================================================
echo                 HUONG DAN KET NOI CHO DIEN THOAI / TABLET
echo ===============================================================================
echo  1. Ket noi dien thoai vao CUNG MANG Wi-Fi voi may tinh nay.
echo  2. Mo trinh duyet tren dien thoai (Safari tren iPhone hoac Chrome tren Android).
echo  3. Nhap dia chi sau de truy cap Web:
echo.
echo     * Qua Nginx Gateway (Port 80):     http://%LAN_IP%
echo     * Truc tiep Backend (Port 8000):   http://%LAN_IP%:8000
echo.
echo  [OK] Tuong lua da duoc mo, dien thoai se truy cap duoc ngay ma khong bi chan.
echo ===============================================================================
echo.
echo Hoan tat! Nhan phim bat ky de dong cua so nay...
pause >nul
