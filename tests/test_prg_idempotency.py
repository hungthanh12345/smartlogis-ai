# tests/test_prg_idempotency.py
import pytest
import time
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from main import app
from app.core.database import SessionLocal
from app.core.datetime_utils import utc_now
from app.core.security import create_access_token
from app.models.inventory_models import (
    HangHoa, TonKho, TheKho, PhieuXuat, PhieuNhap, 
    ChiTietPhieuXuat, ChiTietPhieuNhap, NguoiDung, NhaCungCap
)

client = TestClient(app)

def get_auth_headers(username: str = "admin", role: str = "Admin") -> dict:
    db: Session = SessionLocal()
    user = db.query(NguoiDung).filter(NguoiDung.TenDangNhap == username).first()
    db.close()
    user_id = user.MaND if user else 1
    token = create_access_token(data={"sub": username, "role": role, "user_id": user_id})
    return {"Authorization": f"Bearer {token}"}

def clean_sku(sku: str):
    db: Session = SessionLocal()
    try:
        db.query(TheKho).filter(TheKho.MaHH == sku).delete()
        db.query(ChiTietPhieuXuat).filter(ChiTietPhieuXuat.MaHH == sku).delete()
        db.query(ChiTietPhieuNhap).filter(ChiTietPhieuNhap.MaHH == sku).delete()
        db.query(TonKho).filter(TonKho.MaHH == sku).delete()
        db.query(HangHoa).filter(HangHoa.MaHH == sku).delete()
        db.commit()
    finally:
        db.close()

def init_sku(sku: str, initial_stock: int = 200):
    clean_sku(sku)
    db: Session = SessionLocal()
    try:
        # Ensure supplier exists
        ncc = db.query(NhaCungCap).filter(NhaCungCap.MaNCC == "NCC-IDEM").first()
        if not ncc:
            ncc = NhaCungCap(MaNCC="NCC-IDEM", TenNCC="Nhà Cung Cấp Idempotency Test")
            db.add(ncc)

        hh = HangHoa(MaHH=sku, TenHH=f"Hàng Test {sku}", MaNhom="NH-THEP", MaDVT="Cuộn", TonToiThieu=5)
        db.add(hh)
        tk = TonKho(MaHH=sku, SoLuongTon=initial_stock, CapNhatCuoi=utc_now())
        db.add(tk)

        the_kho = TheKho(
            NgayGiaoDich=utc_now(),
            MaHH=sku,
            MaChungTu=f"PN-INIT-{sku}",
            LoaiGiaoDich="NHAP",
            SoLuongThayDoi=initial_stock,
            TonSauGiaoDich=initial_stock
        )
        db.add(the_kho)
        db.commit()
    finally:
        db.close()

def test_idempotency_key_prevents_duplicate_stock_out():
    """
    Submitting Stock-Out twice with the exact same Idempotency-Key
    must return identical response and NOT create duplicate ledger records.
    """
    sku = "TEST-IDEM-PX-01"
    init_sku(sku, 200)

    try:
        headers = get_auth_headers("admin", "Admin")
        idem_key = f"test-key-px-{int(time.time() * 1000)}"
        headers["Idempotency-Key"] = idem_key

        payload = {
            "NguoiNhan": "Đại lý Thép Miền Trung",
            "LyDoXuat": "Xuất thử nghiệm Idempotency",
            "items": [{"MaHH": sku, "SoLuongXuat": 15}]
        }

        # 1st request
        res1 = client.post("/api/v1/kho/phieu-xuat", json=payload, headers=headers)
        assert res1.status_code == 201
        data1 = res1.json()
        ma_px = data1["MaPX"]

        # 2nd request with same idempotency key (simulating network duplicate / rapid double click)
        res2 = client.post("/api/v1/kho/phieu-xuat", json=payload, headers=headers)
        assert res2.status_code in (200, 201)
        data2 = res2.json()

        # Must return same voucher code
        assert data2["MaPX"] == ma_px

        # Verify Database Integrity: Exactly 1 PhieuXuat created
        db: Session = SessionLocal()
        px_count = db.query(PhieuXuat).filter(PhieuXuat.MaPX == ma_px).count()
        assert px_count == 1

        # Verify TheKho: Only 1 export record created for this voucher
        the_kho_records = db.query(TheKho).filter(
            TheKho.MaHH == sku,
            TheKho.MaChungTu == ma_px
        ).all()
        assert len(the_kho_records) == 1
        assert the_kho_records[0].SoLuongThayDoi == -15
        assert the_kho_records[0].TonSauGiaoDich == 185

        # TonKho must be 185 (200 - 15), NOT reduced twice to 170
        tk = db.query(TonKho).filter(TonKho.MaHH == sku).first()
        assert tk.SoLuongTon == 185
        db.close()
    finally:
        clean_sku(sku)

def test_debounce_deduplication_stock_in():
    """
    Submitting Stock-In twice in rapid succession (debounce within 3s)
    must detect the duplicate payload fingerprint and prevent ledger duplication.
    """
    sku = "TEST-IDEM-PN-01"
    init_sku(sku, 200)

    try:
        headers = get_auth_headers("admin", "Admin")

        payload = {
            "MaNCC": "NCC-IDEM",
            "GhiChu": "Nhập hàng test debounce deduplication",
            "items": [{"MaHH": sku, "SoLuongNhap": 30, "DonGiaNhap": 50000}]
        }

        res1 = client.post("/api/v1/kho/phieu-nhap", json=payload, headers=headers)
        assert res1.status_code == 201
        data1 = res1.json()
        ma_pn = data1["MaPN"]

        # Immediately call again without Idempotency-Key header (rapid double click debounce trigger)
        res2 = client.post("/api/v1/kho/phieu-nhap", json=payload, headers=headers)
        assert res2.status_code in (200, 201)
        data2 = res2.json()
        assert data2["MaPN"] == ma_pn

        # Verify only 1 PhieuNhap was created
        db: Session = SessionLocal()
        pn_count = db.query(PhieuNhap).filter(PhieuNhap.MaPN == ma_pn).count()
        assert pn_count == 1

        # Verify TheKho has only 1 record for this import
        the_kho_entries = db.query(TheKho).filter(
            TheKho.MaHH == sku,
            TheKho.MaChungTu == ma_pn
        ).all()
        assert len(the_kho_entries) == 1
        assert the_kho_entries[0].SoLuongThayDoi == 30
        assert the_kho_entries[0].TonSauGiaoDich == 230

        # TonKho must be 230 (200 + 30), NOT 260
        tk = db.query(TonKho).filter(TonKho.MaHH == sku).first()
        assert tk.SoLuongTon == 230
        db.close()
    finally:
        clean_sku(sku)

def test_prg_redirect_endpoints_render_cleanly():
    """
    Verify GET /outbound?created=... and GET /inbound?created=...
    render correctly as safe idempotent GET requests with no cache headers.
    """
    # Test GET /outbound?created=PX-TEST-001
    res_out = client.get("/outbound?created=PX-TEST-001")
    assert res_out.status_code == 200
    assert "text/html" in res_out.headers.get("content-type", "")
    assert "no-cache" in res_out.headers.get("cache-control", "").lower()

    # Test GET /inbound?created=PN-TEST-001
    res_in = client.get("/inbound?created=PN-TEST-001")
    assert res_in.status_code == 200
    assert "text/html" in res_in.headers.get("content-type", "")
    assert "no-cache" in res_in.headers.get("cache-control", "").lower()
