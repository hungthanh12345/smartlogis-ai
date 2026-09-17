# tests/test_inventory_ledger_sync.py
import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from main import app
from app.core.database import SessionLocal
from app.core.datetime_utils import utc_now
from app.core.security import create_access_token
from app.models.inventory_models import HangHoa, TonKho, TheKho, NguoiDung, NhaCungCap, NhomHang, DonViTinh
from app.services.inventory_service import (
    recalculate_and_sync_the_kho, get_the_kho_by_item, get_all_hang_hoa
)

client = TestClient(app)

def get_auth_headers(username: str = "admin", role: str = "Admin") -> dict:
    db: Session = SessionLocal()
    user = db.query(NguoiDung).filter(NguoiDung.TenDangNhap == username).first()
    db.close()
    user_id = user.MaND if user else 1
    token = create_access_token(data={"sub": username, "role": role, "user_id": user_id})
    return {"Authorization": f"Bearer {token}"}

def test_1_running_balance_stock_135_export_20_equals_115():
    """
    KIỂM THỬ TRỌNG TÂM 1: Sửa lỗi tính toán số dư chạy trong Sổ Thẻ Kho.
    Tồn 135 - Xuất 20 BẮT BUỘC bằng 115 (khắc phục hoàn toàn lỗi ra 10).
    """
    db: Session = SessionLocal()
    sku = "TEST-RUNNING-BAL-01"

    # Đảm bảo dọn dẹp dữ liệu cũ nếu có
    db.query(TheKho).filter(TheKho.MaHH == sku).delete()
    db.query(TonKho).filter(TonKho.MaHH == sku).delete()
    db.query(HangHoa).filter(HangHoa.MaHH == sku).delete()
    db.commit()

    # Tạo SKU thử nghiệm
    hh = HangHoa(MaHH=sku, TenHH="Hàng Kiểm Thử Running Balance", MaNhom="NH-THEP", MaDVT="Cuộn", TonToiThieu=10)
    db.add(hh)
    tk = TonKho(MaHH=sku, SoLuongTon=135, CapNhatCuoi=utc_now())
    db.add(tk)
    # Tồn ban đầu 135
    init_the_kho = TheKho(
        NgayGiaoDich=utc_now(),
        MaHH=sku,
        MaChungTu="PN-TEST-INIT",
        LoaiGiaoDich="NHAP",
        SoLuongThayDoi=135,
        TonSauGiaoDich=135
    )
    db.add(init_the_kho)
    db.commit()
    db.close()

    headers = get_auth_headers("admin", "Admin")

    # Xuất kho 20 cái
    outbound_payload = {
        "NguoiNhan": "Công Trình Test",
        "LyDoXuat": "Kiểm thử Running Balance",
        "items": [{"MaHH": sku, "SoLuongXuat": 20}]
    }
    res_out = client.post("/api/v1/kho/phieu-xuat", json=outbound_payload, headers=headers)
    assert res_out.status_code == 201, f"Lỗi xuất kho: {res_out.text}"

    # Tra cứu Sổ Thẻ Kho qua API
    res_ledger = client.get(f"/api/v1/reports/the-kho/{sku}", headers=headers)
    assert res_ledger.status_code == 200
    ledger_data = res_ledger.json()
    assert len(ledger_data) == 2

    row_init = ledger_data[0]
    row_export = ledger_data[1]

    assert row_init["TonSauGiaoDich"] == 135
    assert row_export["SoLuongThayDoi"] == -20
    # ĐIỀU KIỆN TIÊN QUYẾT: 135 - 20 = 115, TUYỆT ĐỐI KHÔNG PHẢI 10
    assert row_export["TonSauGiaoDich"] == 115, f"Expected 115 but got {row_export['TonSauGiaoDich']}"

    # Kiểm tra tồn kho hiện thời
    res_items = client.get("/api/v1/kho/items", headers=headers)
    assert res_items.status_code == 200
    item_in_list = next((i for i in res_items.json() if i["MaHH"] == sku), None)
    assert item_in_list is not None
    assert item_in_list["SoLuongTon"] == 115

def test_2_sequential_inbound_outbound_running_balance_invariant():
    """
    KIỂM THỬ TRỌNG TÂM 2: Mọi giao dịch thứ N trong Sổ Thẻ Kho luôn tuân thủ bất biến:
    TồnSauGD(N) = TồnSauGD(N-1) +/- Số Lượng Biến Động(N).
    """
    db: Session = SessionLocal()
    sku = "TEST-INVARIANT-02"

    db.query(TheKho).filter(TheKho.MaHH == sku).delete()
    db.query(TonKho).filter(TonKho.MaHH == sku).delete()
    db.query(HangHoa).filter(HangHoa.MaHH == sku).delete()
    db.commit()

    hh = HangHoa(MaHH=sku, TenHH="Hàng Kiểm Thử Bất Biến Lũy Kế", MaNhom="NH-THEP", MaDVT="Cuộn", TonToiThieu=5)
    db.add(hh)
    tk = TonKho(MaHH=sku, SoLuongTon=50, CapNhatCuoi=utc_now())
    db.add(tk)
    init_the_kho = TheKho(
        NgayGiaoDich=utc_now(),
        MaHH=sku,
        MaChungTu="PN-INIT-50",
        LoaiGiaoDich="NHAP",
        SoLuongThayDoi=50,
        TonSauGiaoDich=50
    )
    db.add(init_the_kho)
    db.commit()
    db.close()

    headers = get_auth_headers("admin", "Admin")

    # Chuỗi giao dịch:
    # 1. Nhập thêm 30 -> Tồn 80
    # 2. Xuất 15 -> Tồn 65
    # 3. Xuất 25 -> Tồn 40
    # 4. Nhập 10 -> Tồn 50
    client.post("/api/v1/kho/phieu-nhap", json={
        "MaNCC": "NCC-01", "GhiChu": "Đợt 1", "items": [{"MaHH": sku, "SoLuongNhap": 30, "DonGiaNhap": 1000}]
    }, headers=headers)

    client.post("/api/v1/kho/phieu-xuat", json={
        "NguoiNhan": "Đội 1", "LyDoXuat": "Đợt 2", "items": [{"MaHH": sku, "SoLuongXuat": 15}]
    }, headers=headers)

    client.post("/api/v1/kho/phieu-xuat", json={
        "NguoiNhan": "Đội 2", "LyDoXuat": "Đợt 3", "items": [{"MaHH": sku, "SoLuongXuat": 25}]
    }, headers=headers)

    client.post("/api/v1/kho/phieu-nhap", json={
        "MaNCC": "NCC-01", "GhiChu": "Đợt 4", "items": [{"MaHH": sku, "SoLuongNhap": 10, "DonGiaNhap": 1000}]
    }, headers=headers)

    # Thẩm tra Sổ Thẻ Kho
    res_ledger = client.get(f"/api/v1/reports/the-kho/{sku}", headers=headers)
    assert res_ledger.status_code == 200
    rows = res_ledger.json()
    assert len(rows) == 5

    running = 0
    for idx, r in enumerate(rows):
        if idx == 0:
            expected = r["SoLuongThayDoi"]
        else:
            expected = running + r["SoLuongThayDoi"]
        assert r["TonSauGiaoDich"] == expected, f"Lệch số dư tại dòng {idx}: {r['TonSauGiaoDich']} != {expected}"
        running = expected

    assert running == 50

    # Thẩm tra đồng bộ TonKho
    db = SessionLocal()
    final_tk = db.query(TonKho).filter(TonKho.MaHH == sku).first()
    assert final_tk.SoLuongTon == 50
    db.close()

def test_3_synchronize_current_stock_across_all_skus():
    """
    KIỂM THỬ TRỌNG TÂM 3: Kiểm tra tính đồng bộ toàn diện giữa TonKho.SoLuongTon
    và số dư lũy kế cuối cùng trong TheKho trên toàn bộ CSDL.
    """
    db: Session = SessionLocal()
    # Chạy hàm chuẩn hóa
    res_repair = recalculate_and_sync_the_kho(db)
    assert res_repair["processed_skus"] > 0

    # Thẩm tra: Không còn bất kỳ SKU nào bị lệch số dư giữa TonKho và TheKho
    skus = db.query(HangHoa.MaHH).all()
    discrepancies = []
    for (sku,) in skus:
        tk = db.query(TonKho).filter(TonKho.MaHH == sku).first()
        records = db.query(TheKho).filter(TheKho.MaHH == sku).order_by(TheKho.NgayGiaoDich.asc(), TheKho.MaTK.asc()).all()
        if records:
            last_the_kho = records[-1]
            if tk and tk.SoLuongTon != last_the_kho.TonSauGiaoDich:
                discrepancies.append((sku, tk.SoLuongTon, last_the_kho.TonSauGiaoDich))
    db.close()

    assert len(discrepancies) == 0, f"Phát hiện lệch tồn kho: {discrepancies}"

def test_4_anti_cache_headers_prevent_stale_stock_on_refresh():
    """
    KIỂM THỬ TRỌNG TÂM 4: Kiểm tra HTTP Anti-cache Headers trên các route kho
    để ngăn ngừa trình duyệt lưu cache hiển thị số dư cũ khi refresh trang.
    """
    headers = get_auth_headers("admin", "Admin")

    routes_to_test = [
        "/api/v1/kho/items",
        "/the-kho",
        "/outbound",
        "/inbound",
        "/hang-hoa"
    ]

    for path in routes_to_test:
        client.cookies.set("access_token", headers["Authorization"].split(" ")[1])
        res = client.get(path, headers=headers)
        assert res.status_code in [200, 302], f"Route {path} failed with {res.status_code}"
        assert "Cache-Control" in res.headers, f"Missing Cache-Control on {path}"
        assert "no-store" in res.headers["Cache-Control"]
        assert "no-cache" in res.headers["Cache-Control"]

def test_5_seeder_produces_zero_discrepancies():
    """
    KIỂM THỬ TRỌNG TÂM 5: Kiểm tra seeder chuẩn hóa tự động tính toán đúng
    running balance và không bao giờ tạo lại lỗi Stock 135 - Export 20 = 10.
    """
    from scripts.seed_data import reset_and_seed_database
    reset_and_seed_database(force_reset=True)

    db = SessionLocal()
    # Kiểm tra riêng mặt hàng Thép D08 (HH-THEP-D08)
    the_khos_d08 = db.query(TheKho).filter(TheKho.MaHH == "HH-THEP-D08").order_by(TheKho.NgayGiaoDich.asc(), TheKho.MaTK.asc()).all()
    assert len(the_khos_d08) >= 3

    # Dòng 1: Khởi tạo 135 -> Tồn 135
    assert the_khos_d08[0].SoLuongThayDoi == 135
    assert the_khos_d08[0].TonSauGiaoDich == 135

    # Dòng 2: Nhập 40 -> Tồn 175
    assert the_khos_d08[1].SoLuongThayDoi == 40
    assert the_khos_d08[1].TonSauGiaoDich == 175

    # Dòng 3: Xuất 20 -> Tồn 155 (175 - 20 = 155)
    assert the_khos_d08[2].SoLuongThayDoi == -20
    assert the_khos_d08[2].TonSauGiaoDich == 155

    # Kiểm tra toàn bộ 20 SKUs không có bất kỳ dòng nào bị lệch công thức
    skus = db.query(HangHoa.MaHH).all()
    formula_errors = []
    for (sku,) in skus:
        records = db.query(TheKho).filter(TheKho.MaHH == sku).order_by(TheKho.NgayGiaoDich.asc(), TheKho.MaTK.asc()).all()
        bal = 0
        for r in records:
            bal += r.SoLuongThayDoi
            if r.TonSauGiaoDich != bal:
                formula_errors.append((sku, r.MaChungTu, r.SoLuongThayDoi, r.TonSauGiaoDich, bal))
    db.close()

    assert len(formula_errors) == 0, f"Found formula errors after seeding: {formula_errors}"
