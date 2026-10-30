# tests/test_inbound_outbound_exceptions.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from main import app
from app.core.database import SessionLocal
from app.core.datetime_utils import utc_now
from app.core.security import create_access_token
from app.models.inventory_models import (
    HangHoa, TonKho, TheKho, PhieuNhap, PhieuXuat, 
    ChiTietPhieuNhap, ChiTietPhieuXuat, NguoiDung, NhaCungCap
)

client = TestClient(app)

def get_auth_headers(username: str = "admin", role: str = "Admin") -> dict:
    db: Session = SessionLocal()
    user = db.query(NguoiDung).filter(NguoiDung.TenDangNhap == username).first()
    db.close()
    user_id = user.MaND if user else 1
    token = create_access_token(data={"sub": username, "role": role, "user_id": user_id})
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def test_setup():
    db: Session = SessionLocal()
    sku = "TEST-EXC-SKU-01"

    # Cleanup
    db.query(TheKho).filter(TheKho.MaHH == sku).delete()
    db.query(ChiTietPhieuXuat).filter(ChiTietPhieuXuat.MaHH == sku).delete()
    db.query(ChiTietPhieuNhap).filter(ChiTietPhieuNhap.MaHH == sku).delete()
    db.query(TonKho).filter(TonKho.MaHH == sku).delete()
    db.query(HangHoa).filter(HangHoa.MaHH == sku).delete()

    ncc = db.query(NhaCungCap).filter(NhaCungCap.MaNCC == "NCC-EXC-VALID").first()
    if not ncc:
        ncc = NhaCungCap(MaNCC="NCC-EXC-VALID", TenNCC="NCC Hợp Lệ Test Exceptions")
        db.add(ncc)

    hh = HangHoa(MaHH=sku, TenHH="Hàng Test Exceptions", MaNhom="NH-THEP", MaDVT="Cuộn", TonToiThieu=5)
    db.add(hh)
    tk = TonKho(MaHH=sku, SoLuongTon=50, CapNhatCuoi=utc_now())
    db.add(tk)
    db.commit()
    db.close()

    yield sku

    db_clean: Session = SessionLocal()
    db_clean.query(TheKho).filter(TheKho.MaHH == sku).delete()
    db_clean.query(ChiTietPhieuXuat).filter(ChiTietPhieuXuat.MaHH == sku).delete()
    db_clean.query(ChiTietPhieuNhap).filter(ChiTietPhieuNhap.MaHH == sku).delete()
    db_clean.query(TonKho).filter(TonKho.MaHH == sku).delete()
    db_clean.query(HangHoa).filter(HangHoa.MaHH == sku).delete()
    db_clean.commit()
    db_clean.close()

def test_inbound_rejects_nonexistent_supplier_foreign_key(test_setup):
    """
    Submitting an import with a non-existent MaNCC must be rejected with 404/400
    protecting the foreign key constraint.
    """
    sku = test_setup
    headers = get_auth_headers("admin", "Admin")

    payload = {
        "MaNCC": "NCC-DOES-NOT-EXIST-9999",
        "GhiChu": "Test invalid supplier foreign key",
        "items": [{"MaHH": sku, "SoLuongNhap": 10, "DonGiaNhap": 25000}]
    }

    res = client.post("/api/v1/kho/phieu-nhap", json=payload, headers=headers)
    assert res.status_code in (400, 404)
    data = res.json()
    assert "NCC-DOES-NOT-EXIST-9999" in data["detail"] or "khóa ngoại" in data["detail"].lower()

def test_inbound_rejects_nonexistent_item_foreign_key():
    """
    Submitting an import with a non-existent MaHH must be rejected with 404/400
    protecting the item foreign key constraint.
    """
    headers = get_auth_headers("admin", "Admin")

    payload = {
        "MaNCC": "NCC-EXC-VALID",
        "GhiChu": "Test invalid SKU foreign key",
        "items": [{"MaHH": "SKU-GHOST-NOT-EXIST", "SoLuongNhap": 10, "DonGiaNhap": 25000}]
    }

    res = client.post("/api/v1/kho/phieu-nhap", json=payload, headers=headers)
    assert res.status_code in (400, 404)
    data = res.json()
    assert "SKU-GHOST-NOT-EXIST" in data["detail"] or "khóa ngoại" in data["detail"].lower()

def test_inbound_blocks_zero_or_negative_quantity(test_setup):
    """
    Submitting an import with Quantity <= 0 must be rejected.
    """
    sku = test_setup
    headers = get_auth_headers("admin", "Admin")

    # Zero quantity
    res_zero = client.post("/api/v1/kho/phieu-nhap", json={
        "MaNCC": "NCC-EXC-VALID",
        "items": [{"MaHH": sku, "SoLuongNhap": 0, "DonGiaNhap": 25000}]
    }, headers=headers)
    assert res_zero.status_code in (400, 422)

    # Negative quantity
    res_neg = client.post("/api/v1/kho/phieu-nhap", json={
        "MaNCC": "NCC-EXC-VALID",
        "items": [{"MaHH": sku, "SoLuongNhap": -5, "DonGiaNhap": 25000}]
    }, headers=headers)
    assert res_neg.status_code in (400, 422)

def test_inbound_blocks_zero_or_negative_unit_price(test_setup):
    """
    Submitting an import with Unit Price <= 0 must be rejected.
    """
    sku = test_setup
    headers = get_auth_headers("admin", "Admin")

    # Zero unit price
    res_zero = client.post("/api/v1/kho/phieu-nhap", json={
        "MaNCC": "NCC-EXC-VALID",
        "items": [{"MaHH": sku, "SoLuongNhap": 10, "DonGiaNhap": 0}]
    }, headers=headers)
    assert res_zero.status_code in (400, 422)

    # Negative unit price
    res_neg = client.post("/api/v1/kho/phieu-nhap", json={
        "MaNCC": "NCC-EXC-VALID",
        "items": [{"MaHH": sku, "SoLuongNhap": 10, "DonGiaNhap": -1000}]
    }, headers=headers)
    assert res_neg.status_code in (400, 422)

def test_inbound_handles_null_references_gracefully(test_setup):
    """
    Submitting with null GhiChu and valid parameters must succeed gracefully.
    """
    sku = test_setup
    headers = get_auth_headers("admin", "Admin")

    payload = {
        "MaNCC": "NCC-EXC-VALID",
        "GhiChu": None,
        "items": [{"MaHH": sku, "SoLuongNhap": 20, "DonGiaNhap": 30000}]
    }

    res = client.post("/api/v1/kho/phieu-nhap", json=payload, headers=headers)
    assert res.status_code == 201
    data = res.json()
    assert data["TongTien"] == 600000
    assert data["MaPN"].startswith("PN-")

    # Verify TonKho increased by 20 (50 + 20 = 70)
    db: Session = SessionLocal()
    tk = db.query(TonKho).filter(TonKho.MaHH == sku).first()
    assert tk.SoLuongTon == 70

    # Verify TheKho record has correct running balance
    the_kho = db.query(TheKho).filter(TheKho.MaHH == sku, TheKho.MaChungTu == data["MaPN"]).first()
    assert the_kho is not None
    assert the_kho.SoLuongThayDoi == 20
    assert the_kho.TonSauGiaoDich == 70
    db.close()

def test_outbound_blocks_zero_or_negative_quantity(test_setup):
    """
    Submitting an export with Quantity <= 0 must be rejected.
    """
    sku = test_setup
    headers = get_auth_headers("admin", "Admin")

    # Zero quantity
    res_zero = client.post("/api/v1/kho/phieu-xuat", json={
        "NguoiNhan": "Đại lý A",
        "items": [{"MaHH": sku, "SoLuongXuat": 0}]
    }, headers=headers)
    assert res_zero.status_code in (400, 422)

    # Negative quantity
    res_neg = client.post("/api/v1/kho/phieu-xuat", json={
        "NguoiNhan": "Đại lý A",
        "items": [{"MaHH": sku, "SoLuongXuat": -10}]
    }, headers=headers)
    assert res_neg.status_code in (400, 422)
