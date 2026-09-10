@echo off
chcp 65001 >nul
title Mo Tuong Lua Windows Cho Cac Thiet Bi Khac - SmartLogis AI
cd /d "%~dp0"

:: Goi truc tiep file open_firewall.bat da duoc toi uu co che UAC va chong lap
call "%~dp0open_firewall.bat" %*
