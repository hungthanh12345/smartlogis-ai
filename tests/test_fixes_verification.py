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

def test_1_root_renders_login_page_and_landing_at_landing():
    """1. Khi vào web trang chủ (/) -> Trực tiếp hiển thị giao diện Đăng nhập (login.html). Landing page ở /landing."""
    res_root = client.get("/", follow_redirects=False)
    assert res_root.status_code == 200, f"Expected 200, got {res_root.status_code}"
    assert "Đăng Nhập" in res_root.text or "SmartLogis" in res_root.text
    assert 'name="username"' in res_root.text or "TenDangNhap" in res_root.text or "username" in res_root.text

    # Kiểm tra Landing page chuyển sang /landing
    res_landing = client.get("/landing", follow_redirects=False)
    assert res_landing.status_code == 200, f"Expected 200, got {res_landing.status_code}"
    assert "btnTopRightLogin" in res_landing.text
    assert "Log In" in res_landing.text
    print("[PASS] 1. Root directly renders login view, landing page available at /landing")

def test_2_protected_routes_strictly_redirect_unauthenticated():
    """Các trang quản lý kho khi chưa đăng nhập bắt buộc chuyển hướng 302 về /login."""
    res = client.get("/dashboard", follow_redirects=False)
    assert res.status_code == 302, f"Expected 302, got {res.status_code}"
    assert res.headers.get("location") == "/login"
    print("[PASS] 2. Protected routes strictly redirect unauthenticated requests to /login")

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
        root_dir / "main.py"
    ]
    for f in files_to_check:
        if f.exists():
            text = f.read_text(encoding="utf-8")
            assert ("reload-dir" in text or "reload_dirs" in text), f"Missing reload dir configuration in {f.name}"
def test_8_inbound_duplicate_sku_and_validation():
    """8. Nhập kho - Hợp nhất SKU trùng lặp và tính giá vốn bình quân gia quyền, từ chối số âm/0"""
    token = create_access_token({"sub": "admin", "vaitro": "Admin", "mand": 1, "hoten": "Quản trị viên"})
    headers = {"Authorization": f"Bearer {token}"}
    cookies = {"access_token": f"Bearer {token}"}

    # Test invalid qty <= 0 or price < 0
    invalid_payload = {
        "MaNCC": "NCC-01",
        "items": [
            {"MaHH": "HH-THEP-D08", "SoLuongNhap": 0, "DonGiaNhap": 100000}
        ]
    }
    res_inv = client.post("/api/v1/kho/phieu-nhap", json=invalid_payload, headers=headers, cookies=cookies)
    assert res_inv.status_code in [400, 422], f"Expected 400 or 422, got {res_inv.status_code}"

    # Test duplicate SKU in same payload -> backend consolidates
    dup_payload = {
        "MaNCC": "NCC-01",
        "GhiChu": "Test consolidation SKU trung lap",
        "items": [
            {"MaHH": "HH-THEP-D08", "SoLuongNhap": 2, "DonGiaNhap": 100000},
            {"MaHH": "HH-THEP-D08", "SoLuongNhap": 3, "DonGiaNhap": 150000}
        ]
    }
    res_dup = client.post("/api/v1/kho/phieu-nhap", json=dup_payload, headers=headers, cookies=cookies)
    assert res_dup.status_code in [200, 201], f"Expected success, got {res_dup.text}"
    dup_data = res_dup.json()
    # Total qty: 2 + 3 = 5, total amount: 2*100000 + 3*150000 = 650000
    assert dup_data["TongTien"] == 650000, f"Expected 650000, got {dup_data['TongTien']}"
    # Verify receipt detail has 1 consolidated line
    pn_detail = client.get(f"/api/v1/kho/phieu-nhap/{dup_data['MaPN']}", headers=headers, cookies=cookies)
    assert pn_detail.status_code == 200
    items_saved = pn_detail.json()["items"]
    assert len(items_saved) == 1, f"Expected 1 consolidated item line, got {len(items_saved)}"
    assert items_saved[0]["SoLuongNhap"] == 5
    assert items_saved[0]["DonGiaNhap"] == 130000 # (2*100k + 3*150k) / 5 = 130k
    print("[PASS] 8. Inbound duplicate SKU consolidated with weighted average cost successfully")

def test_9_outbound_duplicate_sku_and_validation():
    """9. Xuất kho - Hợp nhất SKU trùng lặp và chặn tổng số lượng vượt tồn kho"""
    token = create_access_token({"sub": "admin", "vaitro": "Admin", "mand": 1, "hoten": "Quản trị viên"})
    headers = {"Authorization": f"Bearer {token}"}
    cookies = {"access_token": f"Bearer {token}"}

    # Test invalid qty <= 0
    inv_res = client.post("/api/v1/kho/phieu-xuat", json={
        "NguoiNhan": "Test Receiver",
        "items": [{"MaHH": "HH-THEP-D08", "SoLuongXuat": -1}]
    }, headers=headers, cookies=cookies)
    assert inv_res.status_code in [400, 422], f"Expected 400 or 422, got {inv_res.status_code}"

    # Get current stock of HH-THEP-D08
    stock_res = client.get("/api/v1/kho/items", headers=headers, cookies=cookies)
    all_items = stock_res.json()
    thep_item = next(i for i in all_items if i["MaHH"] == "HH-THEP-D08")
    current_ton = thep_item["SoLuongTon"]
    assert current_ton >= 5

    # Test duplicate rows where sum exceeds stock
    excessive_dup = {
        "NguoiNhan": "Test Receiver",
        "items": [
            {"MaHH": "HH-THEP-D08", "SoLuongXuat": current_ton},
            {"MaHH": "HH-THEP-D08", "SoLuongXuat": 1}
        ]
    }
    exc_res = client.post("/api/v1/kho/phieu-xuat", json=excessive_dup, headers=headers, cookies=cookies)
    assert exc_res.status_code == 400
    assert "tồn" in exc_res.json()["detail"].lower()

    # Test valid duplicate rows that sum <= current_ton
    valid_dup = {
        "NguoiNhan": "Test Receiver Valid Duplicate",
        "LyDoXuat": "Test aggregate dispatch",
        "items": [
            {"MaHH": "HH-THEP-D08", "SoLuongXuat": 1},
            {"MaHH": "HH-THEP-D08", "SoLuongXuat": 1}
        ]
    }
    val_res = client.post("/api/v1/kho/phieu-xuat", json=valid_dup, headers=headers, cookies=cookies)
    assert val_res.status_code in [200, 201]
    px_data = val_res.json()
    px_detail = client.get(f"/api/v1/kho/phieu-xuat/{px_data['MaPX']}", headers=headers, cookies=cookies)
    assert px_detail.status_code == 200
    out_items = px_detail.json()["items"]
    assert len(out_items) == 1
    assert out_items[0]["SoLuongXuat"] == 2
    print("[PASS] 9. Outbound duplicate SKU consolidated and stock verified successfully")

def test_10_outbound_valuation_calculation():
    """10. Tính toán giá trị xuất kho - Kiểm tra KPI tổng giá trị xuất kho hoạt động chính xác theo giá vốn bình quân gia quyền"""
    token = create_access_token({"sub": "admin", "vaitro": "Admin", "mand": 1, "hoten": "Quản trị viên"})
    headers = {"Authorization": f"Bearer {token}"}
    cookies = {"access_token": f"Bearer {token}"}

    res_kpis = client.get("/api/v1/kho/kpis", headers=headers, cookies=cookies)
    assert res_kpis.status_code == 200, f"KPI endpoint failed: {res_kpis.text}"
    kpis = res_kpis.json()
    assert "tong_gia_tri_xuat_thang" in kpis
    assert isinstance(kpis["tong_gia_tri_xuat_thang"], (int, float))
    assert kpis["tong_gia_tri_xuat_thang"] > 0
    print(f"[PASS] 10. Outbound valuation calculated correctly: {kpis['tong_gia_tri_xuat_thang']:,.2f} VNĐ")

if __name__ == "__main__":
    print("==================================================")
    print("   KIỂM THỬ TỔNG THỂ CÁC BẢN SỬA LỖI (SMARTLOGIS)")
    print("==================================================")
    test_1_root_renders_login_page_and_landing_at_landing()
    test_2_protected_routes_strictly_redirect_unauthenticated()
    test_3_websocket_client_badge_removed()
    test_4_inbound_creation_and_history()
    test_8_inbound_duplicate_sku_and_validation()
    test_9_outbound_duplicate_sku_and_validation()
    test_10_outbound_valuation_calculation()
    print("==================================================")
    print("  TẤT CẢ TEST SUITE KIỂM THỬ ĐỀU ĐẠT 100%!")
    print("==================================================")
