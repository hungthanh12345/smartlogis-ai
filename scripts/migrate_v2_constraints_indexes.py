# scripts/migrate_v2_constraints_indexes.py
import os
import sys
import sqlite3
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from app.core.config import settings

def run_migration():
    """Áp dụng các Indexes và SQLite Triggers bảo vệ toàn vẹn dữ liệu cho SmartLogis."""
    db_path = settings.DATABASE_URL.replace("sqlite:///", "")
    if not os.path.isabs(db_path):
        db_path = os.path.join(root_dir, db_path)

    print(f"[*] Connecting to database: {db_path}")
    if not os.path.exists(db_path):
        print(f"[!] Warning: Database file does not exist at {db_path}. It will be initialized.")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. Bật WAL mode & foreign keys
    cursor.execute("PRAGMA foreign_keys = ON;")
    cursor.execute("PRAGMA journal_mode = WAL;")
    cursor.execute("PRAGMA busy_timeout = 30000;")
    print("[+] SQLite PRAGMAs configured: foreign_keys=ON, journal_mode=WAL, busy_timeout=30000ms")

    # 2. Tạo Indexes tối ưu hóa truy vấn
    indexes = [
        ("idx_phieu_nhap_ngay", "CREATE INDEX IF NOT EXISTS idx_phieu_nhap_ngay ON phieu_nhap(NgayNhap);"),
        ("idx_phieu_nhap_ncc", "CREATE INDEX IF NOT EXISTS idx_phieu_nhap_ncc ON phieu_nhap(MaNCC);"),
        ("idx_phieu_xuat_ngay", "CREATE INDEX IF NOT EXISTS idx_phieu_xuat_ngay ON phieu_xuat(NgayXuat);"),
        ("idx_ctpn_mapn", "CREATE INDEX IF NOT EXISTS idx_ctpn_mapn ON chi_tiet_phieu_nhap(MaPN);"),
        ("idx_ctpn_mahh", "CREATE INDEX IF NOT EXISTS idx_ctpn_mahh ON chi_tiet_phieu_nhap(MaHH);"),
        ("idx_ctpx_mapx", "CREATE INDEX IF NOT EXISTS idx_ctpx_mapx ON chi_tiet_phieu_xuat(MaPX);"),
        ("idx_ctpx_mahh", "CREATE INDEX IF NOT EXISTS idx_ctpx_mahh ON chi_tiet_phieu_xuat(MaHH);"),
        ("idx_thekho_machungtu", "CREATE INDEX IF NOT EXISTS idx_thekho_machungtu ON the_kho(MaChungTu);")
    ]

    for name, sql in indexes:
        try:
            cursor.execute(sql)
            print(f"[+] Applied index: {name}")
        except sqlite3.OperationalError as e:
            print(f"[-] Skip index {name}: {e}")

    # 3. Tạo Triggers bảo vệ chống số lượng âm ở cấp DB engine
    triggers = [
        ("trg_prevent_negative_stock_update", """
        CREATE TRIGGER IF NOT EXISTS trg_prevent_negative_stock_update
        BEFORE UPDATE OF SoLuongTon ON ton_kho
        FOR EACH ROW
        WHEN NEW.SoLuongTon < 0
        BEGIN
            SELECT RAISE(ABORT, 'Lỗi ràng buộc: Số lượng tồn kho không được âm (SoLuongTon >= 0).');
        END;
        """),
        ("trg_prevent_negative_stock_insert", """
        CREATE TRIGGER IF NOT EXISTS trg_prevent_negative_stock_insert
        BEFORE INSERT ON ton_kho
        FOR EACH ROW
        WHEN NEW.SoLuongTon < 0
        BEGIN
            SELECT RAISE(ABORT, 'Lỗi ràng buộc: Số lượng tồn kho không được âm (SoLuongTon >= 0).');
        END;
        """),
        ("trg_prevent_negative_thekho_insert", """
        CREATE TRIGGER IF NOT EXISTS trg_prevent_negative_thekho_insert
        BEFORE INSERT ON the_kho
        FOR EACH ROW
        WHEN NEW.TonSauGiaoDich < 0
        BEGIN
            SELECT RAISE(ABORT, 'Lỗi ràng buộc: Tồn sau giao dịch trong sổ thẻ kho không được âm.');
        END;
        """),
        ("trg_prevent_negative_thekho_update", """
        CREATE TRIGGER IF NOT EXISTS trg_prevent_negative_thekho_update
        BEFORE UPDATE OF TonSauGiaoDich ON the_kho
        FOR EACH ROW
        WHEN NEW.TonSauGiaoDich < 0
        BEGIN
            SELECT RAISE(ABORT, 'Lỗi ràng buộc: Tồn sau giao dịch trong sổ thẻ kho không được âm.');
        END;
        """)
    ]

    for name, sql in triggers:
        try:
            cursor.execute(sql)
            print(f"[+] Applied trigger: {name}")
        except sqlite3.OperationalError as e:
            print(f"[-] Skip trigger {name}: {e}")

    conn.commit()
    conn.close()
    print("[SUCCESS] Migration v2 completed successfully!")

if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    run_migration()
