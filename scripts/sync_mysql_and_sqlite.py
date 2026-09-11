# scripts/sync_mysql_and_sqlite.py
import sys
from pathlib import Path
from sqlalchemy import create_engine, text

root_dir = str(Path(__file__).resolve().parent.parent)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app.core.config import settings
from app.core.security import get_password_hash

def sync():
    sqlite_url = "sqlite:///./smartlogis.db"
    mysql_url = settings.DATABASE_URL

    print("=== SYNCHRONIZING SQLITE & MYSQL DATABASES ===")
    sqlite_engine = create_engine(sqlite_url)
    mysql_engine = create_engine(mysql_url)

    pwd_hash = get_password_hash("nhanvien123")

    for name, eng in [("SQLite", sqlite_engine), ("MySQL", mysql_engine)]:
        print(f"\n--- Checking {name} ---")
        with eng.begin() as conn:
            # Reassign any slips owned by ketoan (MaND=3) to thukho (MaND=2)
            conn.execute(text("UPDATE phieu_nhap SET MaND = 2 WHERE MaND = (SELECT MaND FROM nguoi_dung WHERE TenDangNhap = 'ketoan')"))
            conn.execute(text("UPDATE phieu_xuat SET MaND = 2 WHERE MaND = (SELECT MaND FROM nguoi_dung WHERE TenDangNhap = 'ketoan')"))
            # 1. Delete ketoan if present
            res = conn.execute(text("DELETE FROM nguoi_dung WHERE TenDangNhap = 'ketoan'"))
            print(f"[{name}] Removed 'ketoan': {res.rowcount} rows")

            # 2. Check nhanvien
            from datetime import datetime
            user = conn.execute(text("SELECT MaND, TenDangNhap, VaiTro FROM nguoi_dung WHERE TenDangNhap = 'nhanvien'")).fetchone()
            if not user:
                conn.execute(
                    text("INSERT INTO nguoi_dung (TenDangNhap, MatKhau, HoTen, VaiTro, KichHoat, NgayTao) VALUES (:u, :p, :h, :v, 1, :t)"),
                    {"u": "nhanvien", "p": pwd_hash, "h": "Nhân Viên Kho", "v": "Nhanvien", "t": datetime.utcnow()}
                )
                print(f"[{name}] Inserted 'nhanvien'")
            else:
                print(f"[{name}] 'nhanvien' exists (ID: {user[0]}, Role: {user[2]})")

            # 3. List users
            users = conn.execute(text("SELECT MaND, TenDangNhap, HoTen, VaiTro FROM nguoi_dung ORDER BY MaND")).fetchall()
            print(f"[{name}] Current Users ({len(users)}):")
            for u in users:
                print(f"   ID: {u[0]} | User: {u[1]} | Name: {u[2]} | Role: {u[3]}")

if __name__ == "__main__":
    sync()
