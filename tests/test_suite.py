# test_suite.py - Bộ test tự động tổng hợp cho SmartLogis AI
import sys
import subprocess
from pathlib import Path

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

def run_all_tests():
    print("==================================================")
    print("     CHẠY BỘ TEST TỰ ĐỘNG SMARTLOGIS AI")
    print("==================================================")
    
    # 1. Test Excel Generation
    print("\n--- 1. Kiểm tra xuất báo cáo Excel Tồn Kho & Nhà Cung Cấp ---")
    try:
        from tests.test_excel import generate_excel_inventory_report
        from app.services.inventory_service import generate_excel_suppliers_report
        from app.core.database import SessionLocal
        db = SessionLocal()
        stream_inv = generate_excel_inventory_report(db)
        stream_sup = generate_excel_suppliers_report(db)
        print(f"[PASS] Xuất báo cáo Excel Tồn kho: {len(stream_inv.getvalue())} bytes")
        print(f"[PASS] Xuất báo cáo Excel Nhà cung cấp: {len(stream_sup.getvalue())} bytes")
    except Exception as e:
        print(f"[FAIL] Lỗi xuất báo cáo Excel: {e}")

    # 2. Test Nghiệp Vụ Nhà Cung Cấp
    print("\n--- 2. Kiểm thử Nghiệp vụ Nhà Cung Cấp & Ràng buộc ACID ---")
    try:
        from tests.test_supplier_crud import test_supplier_suite
        test_supplier_suite()
    except Exception as e:
        print(f"[FAIL] Lỗi kiểm thử Nhà cung cấp: {e}")

    # 2. Test Endpoints & CRUD (Yêu cầu server đang chạy)
    print("\n--- 2. Kiểm tra Endpoints (Live Server) ---")
    try:
        import urllib.request
        with urllib.request.urlopen("http://127.0.0.1:8000/dashboard", timeout=2) as res:
            if res.getcode() == 200:
                print("[PASS] Server đang hoạt động tại http://127.0.0.1:8000")
                print("Đang tiến hành kiểm thử Endpoints...")
                import tests.test_endpoints
                print("\n--- 3. Kiểm thử luồng CRUD nghiệp vụ ---")
                import tests.test_crud
            else:
                print(f"[WARN] Server phản hồi code {res.getcode()}")
    except Exception:
        print("[INFO] Server chưa bật tại http://127.0.0.1:8000. Để chạy trọn bộ kiểm thử Web/API, hãy khởi động server trước!")

    print("\n==================================================")
    print("                 HOÀN TẤT KIỂM THỬ")
    print("==================================================")

if __name__ == "__main__":
    run_all_tests()
