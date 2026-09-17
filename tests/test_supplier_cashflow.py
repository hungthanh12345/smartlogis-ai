# tests/test_supplier_cashflow.py
# Kiểm thử chức năng quản lý dòng tiền và nguồn dữ liệu Nhà Cung Cấp
import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from fastapi.testclient import TestClient
from main import app
from app.core.database import SessionLocal
from app.models.inventory_models import NhaCungCap
from app.schemas.inventory_schemas import NhaCungCapCreate, NhaCungCapUpdate, SupplierCashflowUpdate
from app.services.inventory_service import (
    create_nha_cung_cap, update_nha_cung_cap, update_supplier_cashflow,
    get_supplier_detail, delete_nha_cung_cap, get_supplier_kpis
)
from app.core.security import create_access_token

client = TestClient(app)

def get_auth_headers(role: str = "Admin", username: str = "admin"):
    token = create_access_token(data={"sub": username, "role": role})
    return {"Authorization": f"Bearer {token}"}

def test_supplier_cashflow_service_and_endpoints():
    db = SessionLocal()
    test_ma_ncc = "NCC-CASHFLOW-TEST"

    try:
        # Cleanup neu co
        try:
            delete_nha_cung_cap(db, test_ma_ncc)
        except Exception:
            pass

        # 1. Tao NCC co so tien ban dau (TongTien = 50,000,000)
        new_ncc = NhaCungCapCreate(
            MaNCC=test_ma_ncc,
            TenNCC="Cong ty Co phan Thep Dong Tien Thu Nghiem",
            DiaChi="Ha Noi",
            SoDienThoai="0901234567",
            Email="dongtien@test.com",
            TongTien=50000000.0
        )
        created = create_nha_cung_cap(db, new_ncc)
        assert created.MaNCC == test_ma_ncc
        assert created.TongTien == 50000000.0

        # 2. Lay chi tiet NCC -> TongGiaTriNhap phai bang 50,000,000
        detail = get_supplier_detail(db, test_ma_ncc)
        assert detail["TongGiaTriNhap"] == 50000000.0

        # 3. Dieu chinh dong tien truc tiep qua service: 75,000,000
        cf_updated = update_supplier_cashflow(db, test_ma_ncc, 75000000.0, "Dieu chinh quy 3")
        assert cf_updated.TongTien == 75000000.0

        detail2 = get_supplier_detail(db, test_ma_ncc)
        assert detail2["TongGiaTriNhap"] == 75000000.0

        # 4. Cap nhat qua update_nha_cung_cap voi TongTien = 120,000,000
        up_data = NhaCungCapUpdate(
            TenNCC="Cong ty Co phan Thep Dong Tien Thu Nghiem (Da Sua)",
            TongTien=120000000.0
        )
        updated = update_nha_cung_cap(db, test_ma_ncc, up_data)
        assert updated.TongTien == 120000000.0
        assert updated.TenNCC == "Cong ty Co phan Thep Dong Tien Thu Nghiem (Da Sua)"

        # 5. Test API Endpoint PUT /api/v1/kho/suppliers/{ma_ncc}/cashflow
        headers = get_auth_headers(role="Admin", username="admin")
        res = client.put(
            f"/api/v1/kho/suppliers/{test_ma_ncc}/cashflow",
            json={"TongTien": 88888000.0, "GhiChu": "Thanh toan bu tru tu dong"},
            headers=headers
        )
        assert res.status_code == 200, f"Response: {res.text}"
        data = res.json()
        assert data["TongTien"] == 88888000.0

        # 6. Test API GET /api/v1/kho/suppliers/{ma_ncc}
        res_detail = client.get(f"/api/v1/kho/suppliers/{test_ma_ncc}", headers=headers)
        assert res_detail.status_code == 200
        assert res_detail.json()["TongGiaTriNhap"] == 88888000.0

        # 7. Test API GET /api/v1/kho/suppliers/summary/kpis
        res_kpi = client.get("/api/v1/kho/suppliers/summary/kpis", headers=headers)
        assert res_kpi.status_code == 200
        kpi_data = res_kpi.json()
        assert kpi_data["TongNCC"] > 0
        assert kpi_data["TongChiTieu"] >= 88888000.0

        # 8. Test Route Alias /suppliers va /nha-cung-cap
        token = create_access_token(data={"sub": "admin", "role": "Admin"})
        cookies = {"access_token": token, "session_id": "test_tab_sess_01"}

        res_alias = client.get("/suppliers", cookies=cookies)
        assert res_alias.status_code == 200
        assert "Qu\u1ea3n L\u00fd Nh\u00e0 Cung C\u1ea5p" in res_alias.text or "\u0110\u1ed1i T\u00e1c Cung \u1ee8ng" in res_alias.text

        res_orig = client.get("/nha-cung-cap", cookies=cookies)
        assert res_orig.status_code == 200

        # 9. Cleanup
        delete_nha_cung_cap(db, test_ma_ncc)

    finally:
        db.close()


def test_supplier_phone_validation():
    """Xac minh SoDienThoai bi tu choi khi chua dau cham, chu hoac qua ngan."""
    headers = get_auth_headers()

    # So dien thoai dinh dang dau cham -> 422
    res = client.post(
        "/api/v1/kho/suppliers",
        json={
            "MaNCC": "NCC-PHONE-INVALID-01",
            "TenNCC": "Test Phone Dot Format",
            "SoDienThoai": "024.3974.7777",
        },
        headers=headers,
    )
    assert res.status_code == 422, f"Expected 422, got {res.status_code}: {res.text}"

    # So dien thoai chua chu -> 422
    res2 = client.post(
        "/api/v1/kho/suppliers",
        json={
            "MaNCC": "NCC-PHONE-INVALID-02",
            "TenNCC": "Test Phone Letters",
            "SoDienThoai": "0901abc567",
        },
        headers=headers,
    )
    assert res2.status_code == 422, f"Expected 422, got {res2.status_code}: {res2.text}"

    # So dien thoai qua ngan (< 8 ky tu) -> 422
    res3 = client.post(
        "/api/v1/kho/suppliers",
        json={
            "MaNCC": "NCC-PHONE-INVALID-03",
            "TenNCC": "Test Phone Too Short",
            "SoDienThoai": "0901234",
        },
        headers=headers,
    )
    assert res3.status_code == 422, f"Expected 422, got {res3.status_code}: {res3.text}"

    # So hop le (10 chu so) -> schema khong raise
    valid = NhaCungCapCreate(
        MaNCC="NCC-PHONE-VALID",
        TenNCC="Test Valid Phone",
        SoDienThoai="0901234567",
    )
    assert valid.SoDienThoai == "0901234567"


def test_supplier_email_validation():
    """Xac minh Email bi tu choi khi sai dinh dang chuan."""
    headers = get_auth_headers()

    # Email khong co @ -> 422
    res = client.post(
        "/api/v1/kho/suppliers",
        json={
            "MaNCC": "NCC-EMAIL-INVALID-01",
            "TenNCC": "Test Invalid Email No At",
            "Email": "contacthoaphat.com",
        },
        headers=headers,
    )
    assert res.status_code == 422, f"Expected 422, got {res.status_code}: {res.text}"

    # Email khong co domain extension -> 422
    res2 = client.post(
        "/api/v1/kho/suppliers",
        json={
            "MaNCC": "NCC-EMAIL-INVALID-02",
            "TenNCC": "Test Invalid Email No Ext",
            "Email": "contact@hoaphat",
        },
        headers=headers,
    )
    assert res2.status_code == 422, f"Expected 422, got {res2.status_code}: {res2.text}"

    # Email hop le -> schema khong raise
    valid = NhaCungCapCreate(
        MaNCC="NCC-EMAIL-VALID",
        TenNCC="Test Valid Email",
        Email="sales@hoaphat.com.vn",
    )
    assert valid.Email == "sales@hoaphat.com.vn"


def test_supplier_address_field_persisted():
    """Xac minh DiaChi duoc luu vao DB va tra ve dung qua API."""
    db = SessionLocal()
    test_ma_ncc = "NCC-ADDR-TEST"
    test_diachi = "Lo 12, KCN Pho Noi A, Hung Yen"
    headers = get_auth_headers()

    try:
        # Cleanup
        try:
            delete_nha_cung_cap(db, test_ma_ncc)
        except Exception:
            pass

        # Tao qua API
        res = client.post(
            "/api/v1/kho/suppliers",
            json={
                "MaNCC": test_ma_ncc,
                "TenNCC": "Test Address Supplier",
                "DiaChi": test_diachi,
                "SoDienThoai": "02439747777",
                "Email": "addr@test.vn",
                "TongTien": 0,
            },
            headers=headers,
        )
        assert res.status_code == 201, f"Expected 201, got {res.status_code}: {res.text}"

        # Kiem tra GET detail tra ve DiaChi dung
        res_d = client.get(f"/api/v1/kho/suppliers/{test_ma_ncc}", headers=headers)
        assert res_d.status_code == 200
        assert res_d.json()["DiaChi"] == test_diachi

        # Kiem tra GET list cung co DiaChi
        res_list = client.get("/api/v1/kho/suppliers", headers=headers)
        assert res_list.status_code == 200
        found = next((s for s in res_list.json() if s["MaNCC"] == test_ma_ncc), None)
        assert found is not None
        assert found["DiaChi"] == test_diachi

    finally:
        try:
            delete_nha_cung_cap(db, test_ma_ncc)
        except Exception:
            pass
        db.close()
