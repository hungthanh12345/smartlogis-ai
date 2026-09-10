@echo off
chcp 65001 >nul
title SmartLogis AI - Realtime Centralized Web Server
cd /d %~dp0

echo ===============================================================================
echo            SMARTLOGIS AI - HE THONG QUAN LY KHO THONG MINH
echo           REALTIME CENTRALIZED SERVER - MULTI-DEVICE SUPPORT
echo ===============================================================================
echo [1/3] Dang phan tich cau hinh mang va tim dia chi IP LAN...

:: Lay dia chi IPv4 LAN that cua may tinh dang ket noi Wi-Fi
for /f "tokens=*" %%a in ('py -3.12 -c "import socket; s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.connect(('8.8.8.8',80)); print(s.getsockname()[0]); s.close()" 2^>nul') do set LAN_IP=%%a

if "%LAN_IP%"=="" (
    for /f "tokens=*" %%a in ('python -c "import socket; s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.connect(('8.8.8.8',80)); print(s.getsockname()[0]); s.close()" 2^>nul') do set LAN_IP=%%a
)

if "%LAN_IP%"=="" (
    set LAN_IP=172.172.7.99
)

echo.
echo [2/3] KHOI DONG SERVER HO TRO DA THIET BI (PC, LAPTOP, DIEN THOAI DI DONG):
echo -------------------------------------------------------------------------------
echo  * TRUY CAP QUA TEN MIEN (HTTPS SSL) : https://smartlogis-ai.com
echo  * TRUY CAP QUA TEN MIEN (HTTP 8000): http://smartlogis-ai.com:8000
echo  * TRUY CAP TAI MAY CHU (Localhost)  : http://localhost:8000
echo  * TRUY CAP TU DIEN THOAI / LAPTOP   : http://%LAN_IP%:8000
echo  * TAI LIEU API SWAGGER DOCS         : https://smartlogis-ai.com/docs
echo  * REALTIME WEBSOCKET STREAM         : wss://smartlogis-ai.com/ws/inventory
echo  * PGADMIN WEB (Neu dung Docker)     : http://localhost:5050
echo -------------------------------------------------------------------------------
echo  Luu y: Dam bao dien thoai hoac laptop ket noi chung mang Wi-Fi voi may chu nay.
echo -------------------------------------------------------------------------------
echo [3/3] Dang khoi chay Server SmartLogis AI (Port 443 HTTPS & Port 8000 HTTP)...
echo.

:: Tu dong mo trinh duyet sau 3 giay
start "" /b cmd /c "timeout /t 3 >nul & start https://smartlogis-ai.com"

if exist .\venv\Scripts\python.exe (
    .\venv\Scripts\python.exe run_server_dual.py
) else (
    py -3.12 run_server_dual.py 2>nul || python run_server_dual.py
)

pause
