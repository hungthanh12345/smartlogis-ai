#!/usr/bin/env bash
# start_server.sh - Khoi chay SmartLogis AI Realtime Centralized Server tren Linux/macOS
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd "$DIR"

echo "==============================================================================="
echo "           SMARTLOGIS AI - HE THONG QUAN LY KHO THONG MINH"
echo "          REALTIME CENTRALIZED SERVER - MULTI-DEVICE SUPPORT"
echo "==============================================================================="
echo "[1/3] Dang phan tich cau hinh mang va tim dia chi IP LAN..."

# Tim dia chi IPv4 LAN
LAN_IP=$(hostname -I 2>/dev/null | awk '{print $1}')
if [ -z "$LAN_IP" ]; then
    LAN_IP=$(ip route get 1.1.1.1 2>/dev/null | awk -F"src " 'NR==1{split($2,a," ");print a[1]}')
fi
if [ -z "$LAN_IP" ]; then
    LAN_IP="127.0.0.1"
fi

echo ""
echo "[2/3] KHOI DONG SERVER HO TRO DA THIET BI (PC, LAPTOP, DIEN THOAI DI DONG):"
echo "-------------------------------------------------------------------------------"
echo " * TRUY CAP TAI MAY CHU (Localhost) : http://localhost:8000"
echo " * TRUY CAP TU DIEN THOAI / LAPTOP  : http://${LAN_IP}:8000"
echo " * TAI LIEU API SWAGGER DOCS        : http://${LAN_IP}:8000/docs"
echo " * REALTIME WEBSOCKET STREAM        : ws://${LAN_IP}:8000/ws/inventory"
echo " * PGADMIN WEB (Neu dung Docker)    : http://localhost:5050"
echo "-------------------------------------------------------------------------------"
echo " Luu y: Dam bao thiet bi di dong va may chu ket noi chung mang Wi-Fi/LAN."
echo " Neu bi chan boi UFW Firewall, chay lenh: sudo ufw allow 8000/tcp"
echo "-------------------------------------------------------------------------------"
echo "[3/3] Dang khoi chay FastAPI Uvicorn Server tren 0.0.0.0:8000 (Ctrl+C de dung)..."
echo ""

if [ -f "./venv/bin/python" ]; then
    ./venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
elif command -v python3 >/dev/null 2>&1; then
    python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
else
    python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
fi
