# tests/test_phase2_inventory.py
"""
Bộ kiểm thử toàn diện Giai đoạn 2 cho SmartLogis AI:
1. Giao dịch Nhập kho Inbound (ACID & Rollback)
2. Giao dịch Xuất kho Outbound & Chống tồn âm
3. Kiểm thử Đua lệnh / Race Condition đa luồng (Concurrency with ThreadPoolExecutor)
4. Phân quyền RBAC (Admin, Thủ kho, Kế toán)
5. Ràng buộc cấp CSDL (Triggers & CheckConstraints chống tồn âm)
"""
import sys
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, OperationalError

root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from main import app
from app.core.database import SessionLocal
from app.models.inventory_models import HangHoa, TonKho, TheKho, PhieuNhap, PhieuXuat, ChiTietPhieuXuat

def get_auth_token(client: TestClient, username: str, password: str) -> str:
    """Helper lấy JWT token cho tài khoản."""
    res = client.post("/api/v1/auth/login", json={"TenDangNhap": username, "MatKhau": password})
    assert res.status_code == 200, f"Đăng nhập thất bại cho user {username}: {res.text}"
    return res.json()["access_token"]


def test_inbound_acid_transaction():
    """Kiểm thử nhập kho: Tồn tăng, ghi nhận thẻ kho, rollback khi NCC không hợp lệ."""
    client = TestClient(app)
    admin_token = get_auth_token(client, "admin", "admin123")
    headers = {"Authorization": f"Bearer {admin_token}"}
    db = SessionLocal()

    # Tạo một SKU thử nghiệm với ĐVT 'Bao' hợp lệ
    test_sku = f"HH-INB-{uuid.uuid4().hex[:6].upper()}"
    create_res = client.post(
        "/api/v1/kho/items",
        json={
            "MaHH": test_sku,
            "TenHH": "Hàng thử nghiệm nhập kho",
            "MaNhom": "NH-THEP",
            "MaDVT": "Bao",
            "TonToiThieu": 10,
            "SoLuongBanDau": 20,
            "MoTa": "Test SKU"
        },
        headers=headers
    )
    assert create_res.status_code == 201, f"Tạo SKU thử nghiệm thất bại: {create_res.text}"

    try:
        # 1. Nhập kho hợp lệ (NCC-01, số lượng 50)
        inbound_payload = {
            "MaNCC": "NCC-01",
            "GhiChu": "Phiếu nhập kiểm thử tự động",
            "items": [
                {
                    "MaHH": test_sku,
                    "SoLuongNhap": 50,
                    "DonGiaNhap": 15000.0
                }
            ]
        }
        res = client.post("/api/v1/kho/phieu-nhap", json=inbound_payload, headers=headers)
        assert res.status_code == 201, f"Lập phiếu nhập thất bại: {res.text}"
        data = res.json()
        assert data["MaPN"].startswith("PN-")
        assert data["TongTien"] == 50 * 15000.0

        # Kiểm tra tồn kho mới = 20 + 50 = 70
        stock_res = client.get(f"/api/v1/kho/check-stock/{test_sku}", headers=headers)
        assert stock_res.json()["TonKhauDung"] == 70

        # Kiểm tra Thẻ kho ghi nhận dòng NHAP
        the_kho_res = client.get(f"/api/v1/kho/the-kho/{test_sku}", headers=headers)
        assert the_kho_res.status_code == 200
        records = the_kho_res.json()
        assert len(records) >= 1
        last_rec = records[-1]
        assert last_rec["LoaiGiaoDich"] == "NHAP"
        assert last_rec["SoLuongThayDoi"] == 50
        assert last_rec["TonSauGiaoDich"] == 70

        # 2. Thử nhập kho với Nhà cung cấp KHÔNG TỒN TẠI -> Phải rollback và báo lỗi 404
        invalid_inbound = {
            "MaNCC": "NCC-NON-EXISTENT",
            "GhiChu": "Thử nhập NCC không hợp lệ",
            "items": [{"MaHH": test_sku, "SoLuongNhap": 30, "DonGiaNhap": 10000.0}]
        }
        invalid_res = client.post("/api/v1/kho/phieu-nhap", json=invalid_inbound, headers=headers)
        assert invalid_res.status_code == 404
        # Tồn kho vẫn phải là 70, không thay đổi
        assert client.get(f"/api/v1/kho/check-stock/{test_sku}", headers=headers).json()["TonKhauDung"] == 70

    finally:
        # Dọn dẹp
        client.delete(f"/api/v1/kho/items/{test_sku}", headers=headers)
        db.close()


def test_outbound_negative_stock_prevention():
    """Kiểm thử xuất kho: Chặn xuất vượt tồn, kiểm tra tính nguyên tử rollback."""
    client = TestClient(app)
    admin_token = get_auth_token(client, "admin", "admin123")
    headers = {"Authorization": f"Bearer {admin_token}"}
    db = SessionLocal()

    test_sku = f"HH-OUT-{uuid.uuid4().hex[:6].upper()}"
    create_res = client.post(
        "/api/v1/kho/items",
        json={
            "MaHH": test_sku,
            "TenHH": "Hàng thử nghiệm xuất kho",
            "MaNhom": "NH-XIMANG",
            "MaDVT": "Bao",
            "TonToiThieu": 10,
            "SoLuongBanDau": 15,
            "MoTa": "Test SKU"
        },
        headers=headers
    )
    assert create_res.status_code == 201, f"Tạo SKU thử nghiệm thất bại: {create_res.text}"

    try:
        # 1. Thử xuất 20 bao (trong khi tồn chỉ có 15 bao) -> Phải trả về 400 Bad Request
        fail_payload = {
            "NguoiNhan": "Công ty Xây dựng Minh An",
            "LyDoXuat": "Xuất thử nghiệm vượt tồn kho",
            "items": [
                {
                    "MaHH": test_sku,
                    "SoLuongXuat": 20
                }
            ]
        }
        fail_res = client.post("/api/v1/kho/phieu-xuat", json=fail_payload, headers=headers)
        assert fail_res.status_code == 400, f"Đáng lẽ phải bị 400 nhưng trả về: {fail_res.status_code}"
        assert "không đủ tồn kho" in fail_res.json()["detail"].lower()

        # Kiểm tra tồn kho vẫn nguyên vẹn 15
        stock_check = client.get(f"/api/v1/kho/check-stock/{test_sku}", headers=headers).json()
        assert stock_check["TonKhauDung"] == 15

        # 2. Xuất hợp lệ 10 bao -> Thành công, tồn còn 5
        success_payload = {
            "NguoiNhan": "Công ty Xây dựng Minh An",
            "LyDoXuat": "Xuất hợp lệ trong mức tồn",
            "items": [
                {
                    "MaHH": test_sku,
                    "SoLuongXuat": 10
                }
            ]
        }
        succ_res = client.post("/api/v1/kho/phieu-xuat", json=success_payload, headers=headers)
        assert succ_res.status_code == 201
        px_data = succ_res.json()
        assert px_data["MaPX"].startswith("PX-")

        # Kiểm tra tồn sau xuất = 5
        stock_after = client.get(f"/api/v1/kho/check-stock/{test_sku}", headers=headers).json()
        assert stock_after["TonKhauDung"] == 5

        # Kiểm tra thẻ kho ghi nhận -10 và tồn sau = 5
        the_kho = client.get(f"/api/v1/kho/the-kho/{test_sku}", headers=headers).json()
        assert the_kho[-1]["LoaiGiaoDich"] == "XUAT"
        assert the_kho[-1]["SoLuongThayDoi"] == -10
        assert the_kho[-1]["TonSauGiaoDich"] == 5

    finally:
        client.delete(f"/api/v1/kho/items/{test_sku}", headers=headers)
        db.close()


def test_outbound_concurrency_race_condition():
    """
    Kiểm thử Đua lệnh (Race Condition) Đa luồng:
    Khởi tạo tồn kho = 10.
    2 luồng đồng thời gửi yêu cầu xuất mỗi luồng 8 sản phẩm (Tổng cầu = 16 > 10).
    Với Atomic SQL Decrement, CHỈ ĐÚNG 1 luồng được duyệt (201), luồng còn lại bị từ chối (400).
    Tồn kho cuối cùng phải là 2, tuyệt đối KHÔNG bao giờ bị âm (-6).
    """
    client = TestClient(app)
    admin_token = get_auth_token(client, "admin", "admin123")
    headers = {"Authorization": f"Bearer {admin_token}"}

    test_sku = f"HH-RACE-{uuid.uuid4().hex[:6].upper()}"
    create_res = client.post(
        "/api/v1/kho/items",
        json={
            "MaHH": test_sku,
            "TenHH": "Hàng thử nghiệm Race Condition",
            "MaNhom": "NH-THEP",
            "MaDVT": "Bao",
            "TonToiThieu": 5,
            "SoLuongBanDau": 10,
            "MoTa": "Concurrency SKU"
        },
        headers=headers
    )
    assert create_res.status_code == 201, f"Tạo SKU thử nghiệm thất bại: {create_res.text}"

    try:
        def request_export(req_id: int):
            th_client = TestClient(app)
            payload = {
                "NguoiNhan": f"Khách hàng Luồng {req_id}",
                "LyDoXuat": f"Đua lệnh xuất kho đồng thời {req_id}",
                "items": [{"MaHH": test_sku, "SoLuongXuat": 8}]
            }
            res = th_client.post("/api/v1/kho/phieu-xuat", json=payload, headers=headers)
            return res.status_code, res.json()

        # Thực thi 2 luồng đồng thời
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(request_export, i) for i in [1, 2]]
            results = [f.result() for f in futures]

        status_codes = [r[0] for r in results]
        print(f"\n[Race Condition Test Results] Status Codes: {status_codes}")

        # Kiểm tra: Phải có đúng 1 lệnh thành công (201) và 1 lệnh bị từ chối (400)
        assert 201 in status_codes, f"Phải có 1 giao dịch thành công. Nhận: {status_codes}"
        assert 400 in status_codes, f"Phải có 1 giao dịch bị chặn vì thiếu hàng. Nhận: {status_codes}"
        assert status_codes.count(201) == 1, "Chỉ duy nhất 1 giao dịch được thành công"
        assert status_codes.count(400) == 1, "Giao dịch vượt hạn mức phải bị từ chối"

        # Kiểm tra tồn kho cuối cùng phải là 10 - 8 = 2 (tuyệt đối không âm)
        final_stock = client.get(f"/api/v1/kho/check-stock/{test_sku}", headers=headers).json()
        assert final_stock["TonKhauDung"] == 2, f"Tồn kho bị sai lệch: {final_stock['TonKhauDung']}"

    finally:
        client.delete(f"/api/v1/kho/items/{test_sku}", headers=headers)


def test_rbac_matrix():
    """
    Kiểm thử Ma trận phân quyền (Role-Based Access Control):
    - Kế toán (Ketoan):
      + Được xem danh mục, kho, lập phiếu nhập, lập phiếu xuất, xem thẻ kho.
      + BỊ CẤM (HTTP 403) khi cố Tạo/Sửa/Xóa Hàng hóa (SKU).
      + BỊ CẤM (HTTP 403) khi cố Tạo/Sửa/Xóa Nhà cung cấp.
    - Thủ kho (Thukho):
      + Được toàn quyền thực hiện các nghiệp vụ quản lý kho, SKU, NCC.
    """
    client = TestClient(app)
    admin_token = get_auth_token(client, "admin", "admin123")
    ketoan_token = get_auth_token(client, "ketoan", "ketoan123")
    thukho_token = get_auth_token(client, "thukho", "thukho123")

    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    ketoan_headers = {"Authorization": f"Bearer {ketoan_token}"}
    thukho_headers = {"Authorization": f"Bearer {thukho_token}"}

    # 1. Kế toán ĐƯỢC PHÉP xem danh mục hàng và nhà cung cấp
    res = client.get("/api/v1/kho/items", headers=ketoan_headers)
    assert res.status_code == 200

    res = client.get("/api/v1/kho/suppliers", headers=ketoan_headers)
    assert res.status_code == 200

    # 2. Kế toán BỊ CẤM (403) khi cố TẠO HÀNG HÓA
    res = client.post(
        "/api/v1/kho/items",
        json={
            "MaHH": "HH-FORBIDDEN",
            "TenHH": "Hàng hóa cấm",
            "MaNhom": "NH-THEP",
            "MaDVT": "Bao",
            "TonToiThieu": 5,
            "SoLuongBanDau": 10
        },
        headers=ketoan_headers
    )
    assert res.status_code == 403, f"Kế toán không được phép tạo hàng hóa, nhưng nhận: {res.status_code}"

    # 3. Kế toán BỊ CẤM (403) khi cố TẠO NHÀ CUNG CẤP
    res = client.post(
        "/api/v1/kho/suppliers",
        json={
            "MaNCC": "NCC-FORBIDDEN",
            "TenNCC": "Đối tác cấm",
            "DiaChi": "HN",
            "SoDienThoai": "0123456789"
        },
        headers=ketoan_headers
    )
    assert res.status_code == 403, f"Kế toán không được phép tạo nhà cung cấp, nhưng nhận: {res.status_code}"

    # 4. Kế toán ĐƯỢC PHÉP lập phiếu nhập kho
    # Tạo trước 1 SKU bằng quyền Admin
    test_sku = f"HH-RBAC-{uuid.uuid4().hex[:6].upper()}"
    create_res = client.post(
        "/api/v1/kho/items",
        json={
            "MaHH": test_sku,
            "TenHH": "Hàng kiểm tra RBAC",
            "MaNhom": "NH-THEP",
            "MaDVT": "Bao",
            "TonToiThieu": 5,
            "SoLuongBanDau": 10
        },
        headers=admin_headers
    )
    assert create_res.status_code == 201, f"Tạo SKU thử nghiệm thất bại: {create_res.text}"

    try:
        # Kế toán lập phiếu nhập thành công
        inbound_payload = {
            "MaNCC": "NCC-01",
            "GhiChu": "Phiếu do Kế toán lập",
            "items": [{"MaHH": test_sku, "SoLuongNhap": 15, "DonGiaNhap": 20000.0}]
        }
        res_inb = client.post("/api/v1/kho/phieu-nhap", json=inbound_payload, headers=ketoan_headers)
        assert res_inb.status_code == 201, f"Kế toán phải được phép lập phiếu nhập: {res_inb.text}"

        # Kế toán lập phiếu xuất thành công
        outbound_payload = {
            "NguoiNhan": "Công ty Bê tông Việt",
            "LyDoXuat": "Xuất do Kế toán duyệt",
            "items": [{"MaHH": test_sku, "SoLuongXuat": 5}]
        }
        res_out = client.post("/api/v1/kho/phieu-xuat", json=outbound_payload, headers=ketoan_headers)
        assert res_out.status_code == 201, f"Kế toán phải được phép lập phiếu xuất: {res_out.text}"

        # Kế toán xem được thẻ kho
        res_tk = client.get(f"/api/v1/kho/the-kho/{test_sku}", headers=ketoan_headers)
        assert res_tk.status_code == 200

        # Kế toán xem được danh sách phiếu nhập và xuất
        res_list_pn = client.get("/api/v1/kho/phieu-nhap", headers=ketoan_headers)
        assert res_list_pn.status_code == 200

        res_list_px = client.get("/api/v1/kho/phieu-xuat", headers=ketoan_headers)
        assert res_list_px.status_code == 200

    finally:
        client.delete(f"/api/v1/kho/items/{test_sku}", headers=admin_headers)


def test_database_level_negative_stock_constraints():
    """
    Kiểm thử Ràng buộc CSDL (Database Engine Level):
    Khi có can thiệp SQL trực tiếp (bỏ qua application layer), CSDL phải tự động:
    - Chặn cập nhật tồn kho âm trên bảng `ton_kho` (Trigger trg_prevent_negative_stock_update).
    - Chặn chèn bản ghi âm trên bảng `the_kho` (Trigger trg_prevent_negative_thekho_insert).
    """
    db = SessionLocal()
    try:
        # 1. Lấy SKU thực tế đầu tiên đang có trong DB
        target_item = db.query(TonKho).first()
        assert target_item is not None, "CSDL phai co it nhat 1 SKU ton kho de test"
        target_ma_hh = target_item.MaHH

        # 1. Thử can thiệp trực tiếp UPDATE SoLuongTon = -999 vào target_ma_hh
        blocked_stock = False
        try:
            db.execute(text(f"UPDATE ton_kho SET SoLuongTon = -999 WHERE MaHH = '{target_ma_hh}'"))
            db.commit()
        except (IntegrityError, OperationalError) as e:
            db.rollback()
            blocked_stock = True
            print(f"\n[PASS] CSDL đã chặn thành công UPDATE tồn âm: {e}")
        
        assert blocked_stock, "CSDL cho phép tồn kho âm! Ràng buộc / Trigger chưa hoạt động."

        # 2. Thử can thiệp trực tiếp INSERT vào the_kho với TonSauGiaoDich = -50
        blocked_thekho = False
        try:
            db.execute(text(f"""
                INSERT INTO the_kho (NgayGiaoDich, MaHH, MaChungTu, LoaiGiaoDich, SoLuongThayDoi, TonSauGiaoDich)
                VALUES (CURRENT_TIMESTAMP, '{target_ma_hh}', 'PX-TEST-HACK', 'XUAT', -100, -50)
            """))
            db.commit()
        except (IntegrityError, OperationalError) as e:
            db.rollback()
            blocked_thekho = True
            print(f"[PASS] CSDL đã chặn thành công INSERT thẻ kho âm: {e}")

        assert blocked_thekho, "CSDL cho phép chèn bản ghi Thẻ kho có số tồn sau giao dịch âm!"

    finally:
        db.close()
