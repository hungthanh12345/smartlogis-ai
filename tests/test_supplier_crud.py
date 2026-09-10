# tests/test_supplier_crud.py - Kiểm thử tự động nghiệp vụ Nhà Cung Cấp
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

from fastapi import HTTPException
from app.core.database import SessionLocal
from app.schemas.inventory_schemas import NhaCungCapCreate, NhaCungCapUpdate
from app.services.inventory_service import (
    get_all_suppliers, get_supplier_kpis, get_supplier_detail,
    create_nha_cung_cap, update_nha_cung_cap, delete_nha_cung_cap,
    generate_excel_suppliers_report
)

def test_supplier_suite():
    print("==================================================")
    print("     KIỂM THỬ TỰ ĐỘNG PHÂN HỆ NHÀ CUNG CẤP")
    print("==================================================")
    
    db = SessionLocal()
    test_ma_ncc = "NCC-TEST-AUTO"

    try:
        # Dọn dẹp bản ghi cũ nếu còn sót lại từ lần test trước
        try:
            delete_nha_cung_cap(db, test_ma_ncc)
        except Exception:
            pass

        # 1. Kiểm tra truy vấn danh sách & KPI
        print("\n--- 1. Kiểm tra truy vấn danh sách & KPI ---")
        suppliers = get_all_suppliers(db)
        print(f"[PASS] Lấy danh sách thành công: {len(suppliers)} đối tác")
        assert len(suppliers) > 0, "Danh sách NCC không được rỗng"

        kpis = get_supplier_kpis(db)
        print(f"[PASS] Tính toán KPI thành công:")
        print(f"       - Tổng NCC: {kpis['TongNCC']}")
        print(f"       - Đang giao dịch: {kpis['NCCActive']}")
        print(f"       - Tổng chi tiêu: {kpis['TongChiTieu']:,.0f} VNĐ")
        print(f"       - Top NCC: {kpis['TopNCC']} ({kpis['TopNCCTien']:,.0f} VNĐ)")

        # 2. Kiểm tra truy vấn chi tiết NCC đã có chứng từ (NCC-01)
        print("\n--- 2. Kiểm tra truy vấn chi tiết & lịch sử đơn hàng ---")
        detail = get_supplier_detail(db, "NCC-01")
        print(f"[PASS] Truy vấn chi tiết NCC-01: {detail['TenNCC']}")
        print(f"       - Số phiếu nhập liên kết: {detail['SoPhieuNhap']}")
        print(f"       - Lịch sử phiếu: {len(detail['LichSuNhap'])} chứng từ")
        assert detail["MaNCC"] == "NCC-01"

        # 3. Kiểm tra TẠO MỚI Nhà Cung Cấp
        print("\n--- 3. Kiểm tra Thêm mới Nhà Cung Cấp ---")
        new_ncc = NhaCungCapCreate(
            MaNCC=test_ma_ncc,
            TenNCC="Công ty Cổ phần Thép Thử Nghiệm Tự Động",
            DiaChi="KCN Quang Minh, Mê Linh, Hà Nội",
            SoDienThoai="0243.999.888",
            Email="contact@theptudong.vn"
        )
        created = create_nha_cung_cap(db, new_ncc)
        print(f"[PASS] Tạo thành công NCC: [{created.MaNCC}] - {created.TenNCC}")
        assert created.MaNCC == test_ma_ncc

        # 4. Kiểm tra chặn tạo trùng mã (Duplicate key constraint)
        print("\n--- 4. Kiểm tra kiểm soát trùng lặp mã đối tác ---")
        try:
            create_nha_cung_cap(db, new_ncc)
            print("[FAIL] Cho phép tạo trùng mã NCC (Sai nghiệp vụ)")
            assert False, "Phải ném ra ngoại lệ khi tạo trùng mã"
        except HTTPException as e:
            print(f"[PASS] Đã chặn tạo trùng mã chính xác (HTTP {e.status_code}: {e.detail})")

        # 5. Kiểm tra CẬP NHẬT Nhà Cung Cấp
        print("\n--- 5. Kiểm tra Cập nhật thông tin Đối tác ---")
        update_data = NhaCungCapUpdate(
            TenNCC="Tập đoàn Thép Thử Nghiệm Tự Động (Đã Cập Nhật)",
            DiaChi="KCN Thăng Long II, Hưng Yên",
            SoDienThoai="0221.888.777",
            Email="info@theptudong-updated.vn"
        )
        updated = update_nha_cung_cap(db, test_ma_ncc, update_data)
        print(f"[PASS] Cập nhật thành công: {updated.TenNCC} | SĐT: {updated.SoDienThoai}")
        assert updated.TenNCC == update_data.TenNCC

        # 6. Kiểm tra ràng buộc toàn vẹn khi XÓA (ACID Integrity)
        print("\n--- 6. Kiểm tra ràng buộc toàn vẹn khi Xóa (Foreign Key Protection) ---")
        try:
            # Thử xóa NCC-01 (đã có phiếu nhập mẫu)
            delete_nha_cung_cap(db, "NCC-01")
            print("[FAIL] Cho phép xóa NCC đang có liên kết phiếu nhập kho!")
            assert False, "Không được phép xóa NCC đã có chứng từ"
        except HTTPException as e:
            print(f"[PASS] Đã bảo vệ toàn vẹn dữ liệu thành công (HTTP {e.status_code}: {e.detail})")

        # 7. Kiểm tra XÓA NCC hợp lệ (chưa phát sinh giao dịch)
        print("\n--- 7. Kiểm tra Xóa NCC chưa có giao dịch ---")
        del_res = delete_nha_cung_cap(db, test_ma_ncc)
        print(f"[PASS] Xóa thành công đối tác thử nghiệm [{test_ma_ncc}]")
        assert del_res is True

        # 8. Kiểm tra Xuất Excel Danh bạ NCC
        print("\n--- 8. Kiểm tra Xuất Báo Cáo Excel Danh Bạ NCC ---")
        excel_stream = generate_excel_suppliers_report(db)
        excel_bytes = len(excel_stream.getvalue())
        print(f"[PASS] Xuất file Excel danh bạ thành công ({excel_bytes} bytes)")
        assert excel_bytes > 1000

        print("\n==================================================")
        print("  TẤT CẢ TEST NGHIỆP VỤ NHÀ CUNG CẤP: 100% THÀNH CÔNG")
        print("==================================================")

    finally:
        db.close()

if __name__ == "__main__":
    test_supplier_suite()
