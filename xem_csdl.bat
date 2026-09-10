@echo off
chcp 65001 >nul
title SmartLogis AI - Báo Cáo Tổng Thể CSDL MySQL
cd /d %~dp0

echo ===============================================================================
echo            SMARTLOGIS AI - TRÌNH XEM TỔNG THỂ CƠ SỞ DỮ LIỆU MYSQL
echo ===============================================================================
echo.
python scripts\inspect_database.py

echo Nhấn phím bất kỳ để đóng cửa sổ này...
pause >nul
