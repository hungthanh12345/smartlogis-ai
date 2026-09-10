# tests/test_crud.py
import sys
from pathlib import Path
from fastapi.testclient import TestClient

root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from main import app

def test_crud_suite():
    client = TestClient(app)

    # 1. Login lấy token
    login_res = client.post("/api/v1/auth/login", json={"TenDangNhap": "admin", "MatKhau": "admin123"})
    assert login_res.status_code == 200, f"Login failed: {login_res.text}"
    token = login_res.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    base_url = "/api/v1/kho"

    # Dọn dẹp trước nếu item/supplier cũ còn tồn tại
    client.delete(f"{base_url}/items/HH-TEST-02", headers=headers)
    client.delete(f"{base_url}/suppliers/NCC-CRUD-TEST", headers=headers)

    # 2. CREATE Item
    item_payload = {
        "MaHH": "HH-TEST-02",
        "TenHH": "Xi Măng Nghi Sơn PCB40 Thử Nghiệm",
        "MaNhom": "NH-XIMANG",
        "MaDVT": "BAO",
        "TonToiThieu": 25,
        "SoLuongBanDau": 50,
        "MoTa": "Sản phẩm thử nghiệm kiểm thử tự động CRUD"
    }
    create_res = client.post(f"{base_url}/items", json=item_payload, headers=headers)
    assert create_res.status_code == 201, f"Create item failed: {create_res.text}"
    created = create_res.json()
    assert created["MaHH"] == "HH-TEST-02"
    assert created["SoLuongTon"] == 50
    print(f"[CREATE OK] Created item: {created['MaHH']} | Stock: {created['SoLuongTon']}")

    # 3. UPDATE Item
    update_payload = {
        "TenHH": "Xi Măng Nghi Sơn PCB40 Cập Nhật",
        "MaNhom": "NH-XIMANG",
        "MaDVT": "BAO",
        "TonToiThieu": 30,
        "MoTa": "Đã cập nhật mô tả thành công"
    }
    update_res = client.put(f"{base_url}/items/HH-TEST-02", json=update_payload, headers=headers)
    assert update_res.status_code == 200, f"Update item failed: {update_res.text}"
    updated = update_res.json()
    assert updated["TenHH"] == "Xi Măng Nghi Sơn PCB40 Cập Nhật"
    assert updated["TonToiThieu"] == 30
    print(f"[UPDATE OK] Updated item: {updated['TenHH']} | Min: {updated['TonToiThieu']}")

    # 4. DELETE Item
    del_res = client.delete(f"{base_url}/items/HH-TEST-02", headers=headers)
    assert del_res.status_code == 200, f"Delete item failed: {del_res.text}"
    print(f"[DELETE OK] Deleted item: {del_res.json()['message']}")

    # 5. CREATE Supplier
    supplier_payload = {
        "MaNCC": "NCC-CRUD-TEST",
        "TenNCC": "Công ty TNHH Thử Nghiệm API",
        "DiaChi": "123 Đường Thử Nghiệm, Hà Nội",
        "SoDienThoai": "0987654321",
        "Email": "test@supplier-api.vn"
    }
    create_sup_res = client.post(f"{base_url}/suppliers", json=supplier_payload, headers=headers)
    assert create_sup_res.status_code == 201, f"Create supplier failed: {create_sup_res.text}"
    created_sup = create_sup_res.json()
    assert created_sup["MaNCC"] == "NCC-CRUD-TEST"
    print(f"[CREATE OK] Created supplier: {created_sup['MaNCC']} - {created_sup['TenNCC']}")

    # 6. GET Supplier Detail
    detail_res = client.get(f"{base_url}/suppliers/NCC-CRUD-TEST", headers=headers)
    assert detail_res.status_code == 200, f"Get supplier detail failed: {detail_res.text}"
    sup_detail = detail_res.json()
    assert sup_detail["TenNCC"] == "Công ty TNHH Thử Nghiệm API"
    print(f"[DETAIL OK] Supplier detail: {sup_detail['TenNCC']} | PO count: {sup_detail['SoPhieuNhap']}")

    # 7. UPDATE Supplier
    sup_update_payload = {
        "TenNCC": "Công ty TNHH Thử Nghiệm API (Đã Cập Nhật)",
        "DiaChi": "456 Đường Cập Nhật, Hà Nội",
        "SoDienThoai": "0912345678",
        "Email": "updated@supplier-api.vn"
    }
    update_sup_res = client.put(f"{base_url}/suppliers/NCC-CRUD-TEST", json=sup_update_payload, headers=headers)
    assert update_sup_res.status_code == 200, f"Update supplier failed: {update_sup_res.text}"
    updated_sup = update_sup_res.json()
    assert updated_sup["TenNCC"] == "Công ty TNHH Thử Nghiệm API (Đã Cập Nhật)"
    print(f"[UPDATE OK] Updated supplier: {updated_sup['TenNCC']}")

    # 8. DELETE Supplier
    del_sup_res = client.delete(f"{base_url}/suppliers/NCC-CRUD-TEST", headers=headers)
    assert del_sup_res.status_code == 200, f"Delete supplier failed: {del_sup_res.text}"
    print(f"[DELETE OK] Deleted supplier: {del_sup_res.json()['message']}")

    # 9. GET Supplier KPIs
    kpis_res = client.get(f"{base_url}/suppliers/summary/kpis", headers=headers)
    assert kpis_res.status_code == 200, f"Get supplier KPIs failed: {kpis_res.text}"
    kpis = kpis_res.json()
    assert kpis["TongNCC"] >= 0
    print(f"[KPIS OK] Supplier KPIs: Total {kpis['TongNCC']} | Active {kpis['NCCActive']} | Spent {kpis['TongChiTieu']:,.0f} VND")

if __name__ == "__main__":
    test_crud_suite()
