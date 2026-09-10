#!/usr/bin/env bash
# start.sh - Quickstart script for Linux & macOS

set -e
cd "$(dirname "$0")"

echo "====================================================================="
echo "          SMARTLOGIS AI - HỆ THỐNG QUẢN LÝ KHO TÍCH HỢP AI"
echo "====================================================================="

# 1. Kiểm tra Python 3
if command -v python3 &>/dev/null; then
    PYTHON_CMD=python3
elif command -v python &>/dev/null; then
    PYTHON_CMD=python
else
    echo "[LỖI] Không tìm thấy Python. Vui lòng cài đặt Python 3.10+."
    exit 1
fi

echo "[+] Sử dụng: $($PYTHON_CMD --version)"

# 2. Tạo virtual environment nếu chưa có
if [ ! -d "venv" ]; then
    echo "[*] Khởi tạo môi trường ảo venv..."
    $PYTHON_CMD -m venv venv
fi

source venv/bin/activate

# 3. Cài đặt thư viện nếu cần
if ! python -c "import fastapi" &>/dev/null; then
    echo "[*] Cài đặt dependencies từ requirements.txt..."
    pip install --upgrade pip
    pip install -r requirements.txt
fi

# 4. Kiểm tra CSDL và Seed data nếu chưa có
python -c "from app.core.database import SessionLocal; from app.models.inventory_models import NguoiDung; db=SessionLocal(); has_admin = db.query(NguoiDung).filter_by(TenDangNhap='admin').first() is not None; db.close(); exit(0 if has_admin else 1)" 2>/dev/null || {
    echo "[*] Đang nạp dữ liệu demo ban đầu..."
    python scripts/seed_data.py
    python scripts/migrate_v2_constraints_indexes.py
}

echo ""
echo "====================================================================="
echo "  MÁY CHỦ ĐANG CHẠY TẠI:"
echo "  - Giao diện Web:     http://127.0.0.1:8000"
echo "  - Tài liệu Swagger:  http://127.0.0.1:8000/docs"
echo ""
echo "  TÀI KHOẢN DEMO:"
echo "  - Admin:    admin   / admin123"
echo "  - Thủ kho:  thukho  / thukho123"
echo "  - Kế toán:  ketoan  / ketoan123"
echo "====================================================================="
echo ""

# 5. Khởi chạy Uvicorn Server
exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload
