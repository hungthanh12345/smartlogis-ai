@echo off
chcp 65001 >nul
title SmartLogis AI - 1-Click Production Web Server
cd /d %~dp0

echo ===============================================================================
echo            SMARTLOGIS AI - HE THONG QUAN LY KHO THONG MINH
echo          PRODUCTION WEB SERVER & MULTI-DEVICE GATEWAY RUNNER
echo ===============================================================================
echo [1/4] Dang kiem tra va lay dia chi IPv4 LAN cua may chu...

:: Uu tien lay dia chi IP LAN bang Python
for /f "tokens=*" %%a in ('python -c "import socket; s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.connect(('8.8.8.8',80)); print(s.getsockname()[0]); s.close()" 2^>nul') do set LAN_IP=%%a

if "%LAN_IP%"=="" (
    for /f "tokens=*" %%a in ('py -3.12 -c "import socket; s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.connect(('8.8.8.8',80)); print(s.getsockname()[0]); s.close()" 2^>nul') do set LAN_IP=%%a
)

:: Phuong an du phong bang route print Windows
if "%LAN_IP%"=="" (
    for /f "tokens=4" %%a in ('route print ^| findstr 0.0.0.0 ^| findstr /v "0.0.0.0.*0.0.0.0.*On-link" 2^>nul') do (
        if not defined LAN_IP if not "%%a"=="0.0.0.0" set LAN_IP=%%a
    )
)

if "%LAN_IP%"=="" set LAN_IP=127.0.0.1

echo [OK] Dia chi IP LAN may chu: %LAN_IP%
echo.

echo [2/4] Kiem tra moi truong Docker & Docker Compose...
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] May tinh chua cai dat Docker! Vui long cai dat Docker Desktop: https://www.docker.com/products/docker-desktop
    echo Chuyen sang che do chay du phong bang Python Server cuc bo...
    pause
    if exist .\venv\Scripts\python.exe (
        .\venv\Scripts\python.exe run_server_dual.py
    ) else (
        python run_server_dual.py
    )
    exit /b
)

:: Kiem tra Docker Daemon dang chay
docker info >nul 2>&1
if errorlevel 1 (
    echo [CANH BAO] Docker Daemon chua duoc bat!
    echo Vui long mo Docker Desktop len, cho ung dung hien 'Engine running', roi nhan phim bat ky de thu lai...
    echo * Hoac nhan Ctrl+C de thoat va chay ban Local: python run_server_dual.py
    pause
)

echo.
echo [3/4] Khoi chay he thong SmartLogis AI Containers qua Docker Compose...
echo -------------------------------------------------------------------------------
docker compose up -d --remove-orphans
if errorlevel 1 (
    echo [ERROR] Khoi dong Docker Compose that bai! Vui long kiem tra log.
    pause
    exit /b
)

echo.
echo [4/4] HE THONG SMARTLOGIS AI DA SAN SANG PHUC VU DA THIET BI!
echo ===============================================================================
echo                      BANG HUONG DAN TRUY CAP HE THONG
echo ===============================================================================
echo  1. TRUY CAP TU MAY CHU (Localhost):
echo     * Web App:          http://localhost
echo     * Web App (Secure): https://localhost
echo.
echo  2. TRUY CAP TU DIEN THOAI / TABLET / LAPTOP KHAC (CUNG MANG WI-FI / LAN):
echo     * Dia chi Web:      http://%LAN_IP%
echo     * WebSocket Stream: ws://%LAN_IP%/ws/inventory
echo     (Dam bao dien thoai bat Wi-Fi chung mang voi may chu nay)
echo.
echo  3. TRUY CAP BANG TEN MIEN (Ten mien ao san xuat):
echo     * HTTP (Port 80):   http://smartlogis-ai.com
echo     * HTTPS (Port 443): https://smartlogis-ai.com
echo     (Can cau hinh file hosts: %LAN_IP% smartlogis-ai.com)
echo.
echo  4. CONG CU QUAN TRI & TAI LIEU KY THUAT:
echo     * Quan tri CSDL:    http://localhost:5050 (pgAdmin 4: admin@smartlogis.vn / adminpassword)
echo     * Tai lieu API:     http://localhost/docs  hoac  http://%LAN_IP%/docs
echo -------------------------------------------------------------------------------
echo  * Tai khoan dang nhap san co:
echo    - Quan tri vien:          admin  /  admin123
echo    - Thu kho kiem Ke toan:   thukho /  thukho123
echo ===============================================================================
echo.
echo He thong dang chay ngam (Background Containers).
echo - De kiem tra trang thai:   docker compose ps
echo - De xem log hoat dong:     docker compose logs -f
echo - De dung he thong:         docker compose down
echo.

:: Tu dong mo trinh duyet sau 3 giay
start "" http://localhost/login

echo Nhan phim bat ky de thoat man hinh nay (Server van tiep tuc chay ngam)...
pause >nul
