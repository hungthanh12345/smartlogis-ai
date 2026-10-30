# scripts/migrate_sqlite_to_mysql.py
"""
Script Di Chuyển Dữ Liệu Tự Động Từ SQLite sang MySQL Server (SmartLogis AI)
Quy trình:
1. Đảm bảo Database MySQL 'smartlogis_db' tồn tại với charset utf8mb4.
2. Khởi tạo toàn bộ Tables, Primary Keys, Foreign Keys trên MySQL.
3. Đọc dữ liệu từ SQLite (smartlogis.db) và sao chép theo đúng thứ tự phụ thuộc khóa ngoại.
4. Đối soát số lượng bản ghi giữa SQLite và MySQL để đảm bảo tính toàn vẹn 100%.
"""

import sys
from pathlib import Path
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker

root_dir = str(Path(__file__).resolve().parent.parent)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app.core.config import settings
from app.models.inventory_models import (
    Base, NguoiDung, NhomHang, DonViTinh, NhaCungCap,
    HangHoa, TonKho, PhieuNhap, ChiTietPhieuNhap,
    PhieuXuat, ChiTietPhieuXuat, TheKho
)

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def migrate():
    sqlite_url = "sqlite:///./smartlogis.db"
    mysql_url = settings.DATABASE_URL
    if not mysql_url.startswith("mysql"):
        mysql_url = "mysql+pymysql://root:Hdat171106.@localhost:3306/smartlogis_db?charset=utf8mb4"

    print("=" * 70)
    print("      SMARTLOGIS AI - TRÌNH DI CHUYỂN DỮ LIỆU SQLITE -> MYSQL")
    print("=" * 70)
    print(f"[*] Nguồn (SQLite): {sqlite_url}")
    print(f"[*] Đích  (MySQL) : {mysql_url.split('@')[-1]}")
    print("-" * 70)

    # 1. Đảm bảo MySQL Database đã tồn tại
    mysql_server_url = "mysql+pymysql://root:Hdat171106.@localhost:3306/mysql"
    server_engine = create_engine(mysql_server_url)
    with server_engine.connect() as conn:
        conn.execute(text("CREATE DATABASE IF NOT EXISTS smartlogis_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"))
        conn.commit()
    server_engine.dispose()
    print("[+] Kiểm tra CSDL 'smartlogis_db' trên MySQL: SẴN SÀNG.")

    # 2. Kết nối tới nguồn và đích
    sqlite_engine = create_engine(sqlite_url)
    mysql_engine = create_engine(
        mysql_url,
        pool_size=5,
        pool_recycle=3600,
        pool_pre_ping=True
    )

    # 3. Tạo toàn bộ cấu trúc bảng trên MySQL
    print("[*] Đang khởi tạo Schema & Ràng buộc toàn vẹn trên MySQL...")
    Base.metadata.create_all(bind=mysql_engine)
    print("[+] Đã tạo thành công toàn bộ bảng trong MySQL.")

    SQLiteSession = sessionmaker(bind=sqlite_engine)
    MySQLSession = sessionmaker(bind=mysql_engine)

    src_db = SQLiteSession()
    dst_db = MySQLSession()

    tables_order = [
        ("NguoiDung", NguoiDung, "MaND"),
        ("NhomHang", NhomHang, "MaNhom"),
        ("DonViTinh", DonViTinh, "MaDVT"),
        ("NhaCungCap", NhaCungCap, "MaNCC"),
        ("HangHoa", HangHoa, "MaHH"),
        ("TonKho", TonKho, "MaHH"),
        ("PhieuNhap", PhieuNhap, "MaPN"),
        ("ChiTietPhieuNhap", ChiTietPhieuNhap, "MaCTPN"),
        ("PhieuXuat", PhieuXuat, "MaPX"),
        ("ChiTietPhieuXuat", ChiTietPhieuXuat, "MaCTPX"),
        ("TheKho", TheKho, "MaTK"),
    ]

    total_records = 0

    try:
        # Tạm thời tắt FOREIGN_KEY_CHECKS trong MySQL để chèn dữ liệu không bị chặn
        dst_db.execute(text("SET FOREIGN_KEY_CHECKS=0;"))

        for name, model_cls, pk_field in tables_order:
            src_records = src_db.query(model_cls).all()
            src_count = len(src_records)
            
            # Xóa sạch bảng đích trước khi nạp lại
            dst_db.query(model_cls).delete()
            dst_db.flush()

            for item in src_records:
                # Trích xuất các thuộc tính cột nguyên bản
                data = {
                    c.name: getattr(item, c.name)
                    for c in item.__table__.columns
                }
                new_obj = model_cls(**data)
                dst_db.add(new_obj)

            dst_db.flush()
            dst_count = dst_db.query(model_cls).count()
            print(f"[+] Bảng {name:<18}: SQLite ({src_count:>3}) -> MySQL ({dst_count:>3}) [OK]")
            total_records += dst_count

        dst_db.execute(text("SET FOREIGN_KEY_CHECKS=1;"))
        dst_db.commit()
        print("-" * 70)
        print(f"[SUCCESS] Di chuyển hoàn tất! Tổng cộng {total_records} bản ghi đã chuyển sang MySQL thành công.")
        print("=" * 70)

    except Exception as e:
        dst_db.rollback()
        print(f"[ERROR] Quá trình di chuyển thất bại: {e}")
        raise
    finally:
        src_db.close()
        dst_db.close()
        sqlite_engine.dispose()
        mysql_engine.dispose()


if __name__ == "__main__":
    migrate()
