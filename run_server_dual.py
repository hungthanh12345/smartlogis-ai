# run_server_dual.py
"""
SmartLogis AI - Dual Port Server Runner (Port 8000 HTTP & Port 443 HTTPS)
Cho phép truy cập đồng thời:
1. https://smartlogis-ai.com (Trực tiếp không cần gõ cổng, bảo mật SSL)
2. http://smartlogis-ai.com:8000 & http://localhost:8000
3. http://<LAN_IP>:8000 (Cho điện thoại, máy tính bảng trong mạng WiFi)
"""
import sys
import socket
import asyncio
from pathlib import Path
import uvicorn

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from main import app

def get_lan_ip() -> str:
    """Lấy địa chỉ IPv4 LAN đang hoạt động."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

async def run_servers():
    base_dir = Path(__file__).resolve().parent
    cert_dir = base_dir / "certbot" / "conf" / "live" / "smartlogis-ai.com"
    privkey = cert_dir / "privkey.pem"
    fullchain = cert_dir / "fullchain.pem"

    lan_ip = get_lan_ip()

    print("=" * 79)
    print("           SMARTLOGIS AI - HE THONG QUAN LY KHO THONG MINH")
    print("      REALTIME CENTRALIZED SERVER & DUAL-PORT DOMAIN RUNNER")
    print("=" * 79)
    print(" [1] TRUY CAP QUA TEN MIEN (HTTPS SSL) : https://smartlogis-ai.com")
    print(" [2] TRUY CAP QUA TEN MIEN (HTTP 8000) : http://smartlogis-ai.com:8000")
    print(" [3] TRUY CAP TAI MAY CHU (Localhost)  : http://localhost:8000")
    print(f" [4] TRUY CAP TU DIEN THOAI / LAPTOP   : http://{lan_ip}:8000")
    print(" [5] TAI LIEU API SWAGGER DOCS         : https://smartlogis-ai.com/docs")
    print(" [6] WEBSOCKET REALTIME STREAM         : wss://smartlogis-ai.com/ws/inventory")
    print("-" * 79)
    print(" * Tai khoan Demo: admin / admin123  |  thukho / thukho123  |  ketoan / ketoan123")
    print(" * Nhan Ctrl + C de dung may chu.")
    print("=" * 79 + "\n")

    # 1. Cấu hình HTTP Server trên Port 8000 (chuẩn cho LAN & Local)
    config_8000 = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        access_log=False
    )
    server_8000 = uvicorn.Server(config_8000)
    tasks = [server_8000.serve()]

    # 2. Cấu hình HTTPS SSL Server trên Port 443 (chuẩn cho Domain smartlogis-ai.com)
    if privkey.exists() and fullchain.exists():
        try:
            config_443 = uvicorn.Config(
                app,
                host="0.0.0.0",
                port=443,
                ssl_keyfile=str(privkey),
                ssl_certfile=str(fullchain),
                log_level="info",
                access_log=False
            )
            server_443 = uvicorn.Server(config_443)
            tasks.append(server_443.serve())
            print("[INFO] Da kich hoat thanh cong SSL HTTPS tren Port 443!")
        except Exception as e:
            print(f"[WARN] Khong the khoi chay Port 443: {e}")

    await asyncio.gather(*tasks)

if __name__ == "__main__":
    try:
        asyncio.run(run_servers())
    except (KeyboardInterrupt, SystemExit):
        print("\n[INFO] May chu da dung.")
