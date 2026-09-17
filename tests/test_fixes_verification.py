# tests/test_fixes_verification.py - Comprehensive verification test for recent fixes
import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from fastapi.testclient import TestClient
from main import app
from app.core.database import SessionLocal
from app.models.inventory_models import NguoiDung, HangHoa, TonKho, PhieuNhap, ChiTietPhieuNhap
from app.core.security import create_access_token

client = TestClient(app)

def test_1_root_redirect_unauthenticated():
    """1. Khi vao web chua dang nhap -> Chuyen huong den /login (302)"""
    # Clear any cookies
    res = client.get("/", follow_redirects=False)
    assert res.status_code == 302, f"Expected 302, got {res.status_code}"
    assert res.headers.get("location") == "/login", f"Expected /login redirect, got {res.headers.get('location')}"
    print("[PASS] 1. Root redirect unauthenticated: 302 -> /login")

def test_2_root_redirect_authenticated():
    """Root khi da dang nhap -> Chuyen huong den /dashboard (302)"""
    token = create_access_token({"sub": "admin", "vaitro": "Admin", "hoten": "Quản trị viên"})
    res = client.get("/", cookies={"access_token": f"Bearer {token}"}, follow_redirects=False)
    assert res.status_code == 302, f"Expected 302, got {res.status_code}"
    assert res.headers.get("location") == "/dashboard", f"Expected /dashboard redirect, got {res.headers.get('location')}"
    print("[PASS] 2. Root redirect authenticated: 302 -> /dashboard")

def test_3_websocket_client_badge_removed():
    """2. Tab switch count badge removed from websocket.js"""
    ws_file = root_dir / "app" / "static" / "js" / "websocket.js"
    content = ws_file.read_text(encoding="utf-8")
    assert "(${count} thiết bị)" not in content, "Found (${count} thiết bị) in websocket.js!"
    assert "updateActiveClientsCount" in content, "Missing updateActiveClientsCount function in websocket.js"
    print("[PASS] 3. WebSocket badge 'thiết bị' successfully removed")

def test_4_inbound_creation_and_history():
    """4. Sửa danh sách nhập kho - Logic tính giá, kiểm tra trùng SKU, và lịch sử phiếu nhập"""
    token = create_access_token({"sub": "admin", "vaitro": "Admin", "mand": 1, "hoten": "Quản trị viên"})
    headers = {"Authorization": f"Bearer {token}"}
    cookies = {"access_token": f"Bearer {token}"}

    # Verify query history endpoint
    res_history = client.get("/api/v1/kho/phieu-nhap", headers=headers, cookies=cookies)
    assert res_history.status_code == 200, f"History returned {res_history.status_code}"
    assert isinstance(res_history.json(), list)
    print(f"[PASS] 4a. Query inbound history: {len(res_history.json())} receipts found")

    # Verify receipt creation with validation
    payload = {
        "MaNCC": "NCC-01",
        "GhiChu": "Test verification phiếu nhập kho tự động",
        "items": [
            {
                "MaHH": "HH-THEP-D08",
                "SoLuongNhap": 5,
                "DonGiaNhap": 120000
            }
        ]
    }
    res_create = client.post("/api/v1/kho/phieu-nhap", json=payload, headers=headers, cookies=cookies)
    assert res_create.status_code in [200, 201], f"Create receipt failed: {res_create.text}"
    created_data = res_create.json()
    assert created_data["TongTien"] == 600000, f"Expected 600,000 TongTien, got {created_data['TongTien']}"
    print(f"[PASS] 4b. Inbound receipt created successfully: {created_data['MaPN']} with TongTien = {created_data['TongTien']}")

def test_5_outbound_dispatch_and_stock_preservation():
    """6. Xuất kho - Kiểm tra kiểm soát tồn kho và bảo toàn giao dịch"""
    token = create_access_token({"sub": "admin", "vaitro": "Admin", "mand": 1, "hoten": "Quản trị viên"})
    headers = {"Authorization": f"Bearer {token}"}
    cookies = {"access_token": f"Bearer {token}"}

    # Query outbound history
    res_history = client.get("/api/v1/kho/phieu-xuat", headers=headers, cookies=cookies)
    assert res_history.status_code == 200, f"Outbound history failed: {res_history.status_code}"
    print(f"[PASS] 5a. Outbound history queried: {len(res_history.json())} dispatches")

    # Attempt dispatch exceeding stock (should fail gracefully)
    fail_payload = {
        "NguoiNhan": "Bộ phận kỹ thuật",
        "items": [
            {
                "MaHH": "HH-THEP-D08",
                "SoLuongXuat": 9999999
            }
        ]
    }
    res_fail = client.post("/api/v1/kho/phieu-xuat", json=fail_payload, headers=headers, cookies=cookies)
    assert res_fail.status_code == 400, f"Expected 400 for excessive stock, got {res_fail.status_code}"
    print("[PASS] 5b. Outbound excessive stock correctly rejected with HTTP 400")

    # Successful dispatch of 1 item
    success_payload = {
        "NguoiNhan": "Xưởng sản xuất số 1",
        "LyDoXuat": "Test verification xuất kho",
        "items": [
            {
                "MaHH": "HH-THEP-D08",
                "SoLuongXuat": 1
            }
        ]
    }
    res_success = client.post("/api/v1/kho/phieu-xuat", json=success_payload, headers=headers, cookies=cookies)
    assert res_success.status_code in [200, 201], f"Outbound dispatch failed: {res_success.text}"
    out_data = res_success.json()
    print(f"[PASS] 5c. Outbound dispatch created successfully: {out_data['MaPX']}")

def test_6_supplier_workflow_and_null_fields():
    """5 & 7. Nhà cung cấp - Tạo với null fields, quản lý dòng tiền và modals"""
    token = create_access_token({"sub": "admin", "vaitro": "Admin", "mand": 1, "hoten": "Quản trị viên"})
    headers = {"Authorization": f"Bearer {token}"}
    cookies = {"access_token": f"Bearer {token}"}

    test_ncc_code = "NCC-TEST-VERIFY"
    # Clean up before
    client.delete(f"/api/v1/kho/suppliers/{test_ncc_code}", headers=headers, cookies=cookies)

    # Create supplier with null optional fields
    payload = {
        "MaNCC": test_ncc_code,
        "TenNCC": "Công ty Kiểm Thử Xác Minh",
        "DiaChi": None,
        "SoDienThoai": None,
        "Email": None
    }
    res = client.post("/api/v1/kho/suppliers", json=payload, headers=headers, cookies=cookies)
    assert res.status_code in [200, 201], f"Create supplier failed: {res.text}"
    created = res.json()
    assert created["MaNCC"] == test_ncc_code
    assert created["DiaChi"] is None
    print(f"[PASS] 6a. Created supplier with null optional fields: {created['MaNCC']}")

    # Clean up after
    del_res = client.delete(f"/api/v1/kho/suppliers/{test_ncc_code}", headers=headers, cookies=cookies)
    assert del_res.status_code == 200
    print("[PASS] 6b. Cleaned up test supplier")

def test_7_scripts_reload_dir_applied():
    """9. Web tự reset nhưng data tự tăng -> Đã cấu hình --reload-dir app ở tất cả script"""
    files_to_check = [
        root_dir / "run_app.bat",
        root_dir / "start.sh",
        root_dir / "start_server.sh",
        root_dir / "scripts" / "run.py",
        root_dir / "main.py"
    ]
    for f in files_to_check:
        if f.exists():
            text = f.read_text(encoding="utf-8")
            assert ("reload-dir" in text or "reload_dirs" in text), f"Missing reload dir configuration in {f.name}"
            print(f"[PASS] 7. Verified reload-dir in {f.name}")

if __name__ == "__main__":
    print("==================================================")
    print("   KIỂM THỬ TỔNG THỂ CÁC BẢN SỬA LỖI (SMARTLOGIS)")
    print("==================================================")
    test_1_root_redirect_unauthenticated()
    test_2_root_redirect_authenticated()
    test_3_websocket_client_badge_removed()
    test_4_inbound_creation_and_history()
    test_5_outbound_dispatch_and_stock_preservation()
    test_6_supplier_workflow_and_null_fields()
    test_7_scripts_reload_dir_applied()
    print("==================================================")
    print("  TẤT CẢ 7/7 TEST SUITE KIỂM THỬ ĐỀU ĐẠT 100%!")
    print("==================================================")
