@echo off
chcp 65001 >nul
title Cai Dat Chung Chi SSL Bao Mat - SmartLogis AI
cd /d "%~dp0"

echo [THONG BAO] Dang yeu cau quyen Administrator de cai dat chung chi vao Windows...
powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process powershell -Verb RunAs -ArgumentList '-NoProfile -ExecutionPolicy Bypass -File \""%~dp0install_ca.ps1\""'"
exit
