@echo off
chcp 65001 >nul
title Cau Hinh Ten Mien smartlogis-ai.com Local

:: Kiem tra va yeu cau quyen Administrator (UAC Prompt)
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [THONG BAO] Dang yeu cau quyen Administrator de chinh sua file hosts...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

set HOSTS_FILE=%SystemRoot%\System32\drivers\etc\hosts
echo ===============================================================================
echo        CAU HINH TEN MIEN LOCAL: smartlogis-ai.com -> 127.0.0.1
echo ===============================================================================

findstr /i "smartlogis-ai.com" "%HOSTS_FILE%" >nul
if %errorLevel% equ 0 (
    echo [INFO] Ten mien smartlogis-ai.com DA TON TAI trong file hosts cua may!
) else (
    echo. >> "%HOSTS_FILE%"
    echo # SmartLogis AI Local Domain Mapping >> "%HOSTS_FILE%"
    echo 127.0.0.1       smartlogis-ai.com >> "%HOSTS_FILE%"
    echo 127.0.0.1       www.smartlogis-ai.com >> "%HOSTS_FILE%"
    echo [THANH CONG] Da them thanh cong smartlogis-ai.com vao file hosts!
)

ipconfig /flushdns >nul
echo [INFO] Da lam moi bo nho dem DNS (ipconfig /flushdns thanh cong).

:: Cai dat chung chi Root CA vao Windows de trinh duyet Chrome/Edge nhan dien Bao mat an toan
set CA_FILE=%~dp0certbot\conf\smartlogis_root_ca.crt
if exist "%CA_FILE%" (
    powershell -NoProfile -Command "Import-Certificate -FilePath '%CA_FILE%' -CertStoreLocation 'Cert:\LocalMachine\Root' | Out-Null" 2>nul
    echo [THANH CONG] Da cai dat chung chi bao mat vao Windows Trusted Store!
)
echo -------------------------------------------------------------------------------
echo Bay gio ban co the truy cap bang:
echo  1. https://smartlogis-ai.com        (Truc tiep qua Port 443 SSL)
echo  2. http://smartlogis-ai.com:8000   (Qua Port 8000)
echo ===============================================================================
echo.
echo Nhấn phím bất kỳ để TỰ ĐỘNG KHỞI ĐỘNG SERVER và mở trang web ngay...
pause >nul

cd /d "%~dp0"
start "SmartLogis AI Server" cmd /c "%~dp0start_server.bat"
exit
