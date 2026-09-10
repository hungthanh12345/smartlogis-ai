# scripts/migrate_postgres.py
"""
Script Đồng Bộ Schema, Indexes & Triggers Cho Cơ Sở Dữ Liệu PostgreSQL (SmartLogis AI)
Tự động áp dụng:
1. 8 B-Tree Indexes tối ưu truy vấn nghiệp vụ kho 30 ngày.
2. PL/pgSQL Triggers bảo vệ chống tồn kho âm ở cấp CSDL.
"""

import sys
from pathlib import Path

root_dir = str(Path(__file__).resolve().parent.parent)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from sqlalchemy import text
from app.core.database import engine, Base
from app.core.config import settings

def migrate_postgresql():
    print("=" * 65)
    print("   SMARTLOGIS AI - MIGRATION DỮ LIỆU POSTGRESQL (PRODUCTION)")
    print("=" * 65)
    print(f"[*] Database URL: {settings.DATABASE_URL}")

    # Tạo tất cả các bảng nếu chưa có
    print("[*] Khoi tao toan bo Tables tren CSDL...")
    Base.metadata.create_all(bind=engine)

    # Nếu đang dùng SQLite thì thông báo chuyển hướng sang migrate_v2
    if settings.DATABASE_URL.startswith("sqlite"):
        print("[INFO] He thong dang ket noi SQLite. De migrate SQLite, chay: scripts/migrate_v2_constraints_indexes.py")
        return

    print("[*] Dang ap dung Indexes va PL/pgSQL Triggers tren PostgreSQL...")
    with engine.connect() as conn:
        trans = conn.begin()
        try:
            # 1. B-Tree Indexes
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_phieu_nhap_ngay ON phieu_nhap (NgayNhap);",
                "CREATE INDEX IF NOT EXISTS idx_phieu_nhap_ncc ON phieu_nhap (MaNCC);",
                "CREATE INDEX IF NOT EXISTS idx_phieu_xuat_ngay ON phieu_xuat (NgayXuat);",
                "CREATE INDEX IF NOT EXISTS idx_ctpn_mapn ON chi_tiet_phieu_nhap (MaPN);",
                "CREATE INDEX IF NOT EXISTS idx_ctpn_mahh ON chi_tiet_phieu_nhap (MaHH);",
                "CREATE INDEX IF NOT EXISTS idx_ctpx_mapx ON chi_tiet_phieu_xuat (MaPX);",
                "CREATE INDEX IF NOT EXISTS idx_ctpx_mahh ON chi_tiet_phieu_xuat (MaHH);",
                "CREATE INDEX IF NOT EXISTS idx_thekho_machungtu ON the_kho (MaChungTu);"
            ]
            for idx in indexes:
                conn.execute(text(idx))
                print(f"  [+] Applied index: {idx.split()[5]}")

            # 2. PL/pgSQL Functions & Triggers chống tồn âm
            plpgsql_func = """
            CREATE OR REPLACE FUNCTION trg_fn_check_negative_stock()
            RETURNS TRIGGER AS $$
            BEGIN
                IF NEW.SoLuongTon < 0 THEN
                    RAISE EXCEPTION 'VI PHAM TOAN VEN CSDL: So luong ton kho khong duoc am! (MaHH: %, Ton: %)', NEW.MaHH, NEW.SoLuongTon;
                END IF;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
            """
            conn.execute(text(plpgsql_func))

            # Drop trigger nếu đã tồn tại để tránh trùng lặp
            conn.execute(text("DROP TRIGGER IF EXISTS trg_check_ton_kho_negative ON ton_kho;"))
            conn.execute(text("""
                CREATE TRIGGER trg_check_ton_kho_negative
                BEFORE INSERT OR UPDATE ON ton_kho
                FOR EACH ROW
                EXECUTE FUNCTION trg_fn_check_negative_stock();
            """))
            print("  [+] Applied PostgreSQL Trigger: trg_check_ton_kho_negative")

            trans.commit()
            print("[SUCCESS] Da hoan tat Migration PostgreSQL 100%!")
        except Exception as e:
            trans.rollback()
            print(f"[ERROR] Loi khi migrate PostgreSQL: {e}")
            raise e

if __name__ == "__main__":
    migrate_postgresql()
