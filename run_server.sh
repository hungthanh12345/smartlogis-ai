#!/usr/bin/env bash
# run_server.sh - 1-Click Production Web Server Launcher cho SmartLogis AI (Linux / macOS)
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd "$DIR"

# Màu sắc ANSI
GREEN="\033[1;32m"
BLUE="\033[1;34m"
CYAN="\033[1;36m"
YELLOW="\033[1;33m"
RED="\033[1;31m"
BOLD="\033[1m"
RESET="\033[0m"

echo -e "${BLUE}===============================================================================${RESET}"
echo -e "${BOLD}           SMARTLOGIS AI - HE THONG QUAN LY KHO THONG MINH${RESET}"
echo -e "${BOLD}         PRODUCTION WEB SERVER & MULTI-DEVICE GATEWAY RUNNER${RESET}"
echo -e "${BLUE}===============================================================================${RESET}"
echo -e "${YELLOW}[1/4] Dang kiem tra va lay dia chi IPv4 LAN cua may chu...${RESET}"

# Tim dia chi IPv4 LAN
LAN_IP=$(hostname -I 2>/dev/null | awk '{print $1}')
if [ -z "$LAN_IP" ]; then
    LAN_IP=$(ip route get 1.1.1.1 2>/dev/null | awk -F"src " 'NR==1{split($2,a," ");print a[1]}')
fi
if [ -z "$LAN_IP" ]; then
    LAN_IP=$(python3 -c "import socket; s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.connect(('8.8.8.8',80)); print(s.getsockname()[0]); s.close()" 2>/dev/null || echo "127.0.0.1")
fi

echo -e "${GREEN}[OK] Dia chi IP LAN may chu: ${BOLD}${LAN_IP}${RESET}"
echo ""

echo -e "${YELLOW}[2/4] Kiem tra Docker va Docker Compose...${RESET}"
if ! command -v docker &>/dev/null; then
    echo -e "${RED}[ERROR] Docker chua duoc cai dat tren may tinh!${RESET}"
    echo "Vui long cai dat Docker Engine hoac Docker Desktop: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! docker info &>/dev/null; then
    echo -e "${RED}[ERROR] Docker daemon chua duoc khoi dong hoac quyen bi han che (can sudo)!${RESET}"
    echo "Hay chay: sudo systemctl start docker (Linux) hoac mo Docker Desktop (macOS)."
    exit 1
fi

echo -e "${YELLOW}[3/4] Khoi chay he thong SmartLogis AI Containers qua Docker Compose...${RESET}"
docker compose up -d --remove-orphans

echo ""
echo -e "${GREEN}[4/4] HE THONG SMARTLOGIS AI DA SAN SANG PHUC VU DA THIET BI!${RESET}"
echo -e "${BLUE}===============================================================================${RESET}"
echo -e "${BOLD}                     BANG HUONG DAN TRUY CAP HE THONG${RESET}"
echo -e "${BLUE}===============================================================================${RESET}"
echo -e " ${BOLD}1. TRUY CAP TU MAY CHU (Localhost):${RESET}"
echo -e "    * Web App:          ${CYAN}http://localhost${RESET}"
echo -e "    * Web App (Secure): ${CYAN}https://localhost${RESET}"
echo ""
echo -e " ${BOLD}2. TRUY CAP TU DIEN THOAI / TABLET / LAPTOP KHAC (CUNG WI-FI / LAN):${RESET}"
echo -e "    * Dia chi Web:      ${GREEN}http://${LAN_IP}${RESET}"
echo -e "    * WebSocket Stream: ${GREEN}ws://${LAN_IP}/ws/inventory${RESET}"
echo -e "    (Luu y: Dam bao thiet bi di dong ket noi chung mang Wi-Fi voi may chu)"
echo ""
echo -e " ${BOLD}3. TRUY CAP BANG TEN MIEN (Ten mien ao san xuat):${RESET}"
echo -e "    * HTTP (Port 80):   ${CYAN}http://smartlogis-ai.com${RESET}"
echo -e "    * HTTPS (Port 443): ${CYAN}https://smartlogis-ai.com${RESET}"
echo -e "    (Them vao file /etc/hosts: ${LAN_IP} smartlogis-ai.com)"
echo ""
echo -e " ${BOLD}4. CONG CU QUAN TRI & TAI LIEU KY THUAT:${RESET}"
echo -e "    * Quan tri CSDL:    ${CYAN}http://localhost:5050${RESET} (pgAdmin: admin@smartlogis.vn / adminpassword)"
echo -e "    * Tai lieu API:     ${CYAN}http://localhost/docs${RESET} hoac ${CYAN}http://${LAN_IP}/docs${RESET}"
echo -e "${BLUE}-------------------------------------------------------------------------------${RESET}"
echo -e " * Tai khoan dang nhap san co:"
echo -e "   - Quan tri vien: ${BOLD}admin${RESET}  /  ${BOLD}admin123${RESET}"
echo -e "   - Thu kho:       ${BOLD}thukho${RESET} /  ${BOLD}thukho123${RESET}"
echo -e "   - Ke toan kho:   ${BOLD}ketoan${RESET} /  ${BOLD}ketoan123${RESET}"
echo -e "${BLUE}===============================================================================${RESET}"
echo ""
echo "He thong dang van hanh duoi dang Container ngam."
echo " - Kiem tra trang thai: docker compose ps"
echo " - Xem log he thong:    docker compose logs -f"
echo " - Dung he thong:       docker compose down"
echo ""
