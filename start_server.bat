@echo off
title SmartLogis AI Server
cd /d %~dp0
echo ===================================================
echo     DANG KHOI DONG HE THONG SMARTLOGIS AI V2.0
echo ===================================================
echo - Localhost:  http://127.0.0.1:8000
echo - LAN IP:     http://172.172.5.168:8000
echo - Swagger:    http://127.0.0.1:8000/docs
echo ===================================================
echo Nhan Ctrl+C de dung may chu.
echo.
.\venv\Scripts\python.exe run.py
pause
