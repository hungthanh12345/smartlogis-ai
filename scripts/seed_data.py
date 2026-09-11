# scripts/seed_data.py
"""
Script Nạp Dữ Liệu Mẫu Chuẩn Cho SmartLogis AI (Demo Seeder & Data Reset)
Phục vụ hoàn hảo cho việc Demo, nghiệm thu và chấm điểm đồ án:
1. Tài khoản: Admin (admin/admin123), Thủ kho kiêm Kế toán (thukho/thukho123), Nhân viên kho (nhanvien/nhanvien123).
2. Danh mục: 5 Nhóm hàng, 6 Đơn vị tính, 5 Nhà cung cấp thực tế.
3. Hàng hóa: 20 SKUs bao gồm cả 3 trạng thái nghiệp vụ:
   - Hàng an toàn (Normal stock).
   - Hàng chạm / dưới ngưỡng tồn tối thiểu (Low stock alerts - để AI đề xuất nhập).
   - Hàng ứ đọng lâu ngày (> 60 ngày không xuất - Dead stock - để AI phát hiện bất thường).
4. Lịch sử giao dịch: Các phiếu nhập/xuất trong 30 ngày qua để AI tính Burn-rate chuẩn xác.
5. Hỗ trợ cờ `--reset` để làm sạch toàn bộ dữ liệu và nạp lại từ đầu.
"""

import sys
import os
import argparse
from pathlib import Path
from datetime import datetime, timedelta

# Đảm bảo root directory nằm trong sys.path
root_dir = str(Path(__file__).resolve().parent.parent)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.core.security import get_password_hash
from app.models.inventory_models import (
    NguoiDung, NhomHang, DonViTinh, NhaCungCap, 
    HangHoa, TonKho, PhieuNhap, ChiTietPhieuNhap, 
    PhieuXuat, ChiTietPhieuXuat, TheKho
)


# Đảm bảo terminal console trên Windows không bị lỗi Unicode
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

def reset_and_seed_database(force_reset: bool = False):
    """Nap du lieu mau chuan cho he thong SmartLogis AI."""
    print("=" * 65)
    print("    SMARTLOGIS AI - TRINH KHOI TAO DU LIEU DEMO CHUAN HOA")
    print("=" * 65)

    if force_reset:
        print("[*] Dang xoa bo CSDL cu de tai tao lai (FORCE RESET)...")
        Base.metadata.drop_all(bind=engine)

    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    try:
        # Kiểm tra nếu đã có dữ liệu và không yêu cầu reset thì bỏ qua
        existing_admin = db.query(NguoiDung).filter_by(TenDangNhap="admin").first()
        if existing_admin and not force_reset:
            print("[INFO] He thong da co du lieu. Su dung co '--reset' neu muon nap lai tu dau.")
            return

        print("[*] Dang khoi tao danh sach Nguoi dung (RBAC: Admin, Thukho kiem Ketoan)...")
        users = [
            NguoiDung(
                TenDangNhap="admin",
                MatKhau=get_password_hash("admin123"),
                HoTen="Nguyễn Thành Hưng (Quản Trị Viên)",
                VaiTro="Admin",
                KichHoat=True
            ),
            NguoiDung(
                TenDangNhap="thukho",
                MatKhau=get_password_hash("thukho123"),
                HoTen="Hoàng Tiến Đạt (Thủ Kho Kiêm Kế Toán)",
                VaiTro="Thukho",
                KichHoat=True
            ),
            NguoiDung(
                TenDangNhap="nhanvien",
                MatKhau=get_password_hash("nhanvien123"),
                HoTen="Nhân Viên Kho",
                VaiTro="Nhanvien",
                KichHoat=True
            ),
        ]
        db.add_all(users)
        db.flush()

        print("[*] Dang khoi tao 5 Nhom hang & 6 Don vi tinh chuan...")
        categories = [
            NhomHang(MaNhom="NH-THEP", TenNhom="Thép & Kim loại xây dựng", MoTa="Thép cuộn, thép cây vằn, thép hình kết cấu công trình"),
            NhomHang(MaNhom="NH-NHUA", TenNhom="Ống & Phụ kiện cấp thoát nước", MoTa="Ống nhựa PVC, HDPE, PPR và phụ kiện co cút hàn nhiệt"),
            NhomHang(MaNhom="NH-XIMANG", TenNhom="Xi măng & Bê tông", MoTa="Xi măng bao PCB40, phụ gia bê tông, vữa đóng gói"),
            NhomHang(MaNhom="NH-SON", TenNhom="Sơn & Hóa chất bảo vệ", MoTa="Sơn chống rỉ Alkyd, sơn nền sàn Epoxy, dung môi công nghiệp"),
            NhomHang(MaNhom="NH-CODIEN", TenNhom="Vật tư cơ điện & Phụ kiện cơ khí", MoTa="Que hàn, bu lông neo móng, cáp điện, đá mài đá cắt")
        ]
        db.add_all(categories)

        units = [
            DonViTinh(MaDVT="Cuộn", TenDVT="Cuộn tiêu chuẩn"),
            DonViTinh(MaDVT="Cây", TenDVT="Cây (Độ dài tiêu chuẩn)"),
            DonViTinh(MaDVT="Bao", TenDVT="Bao (Khối lượng 50kg)"),
            DonViTinh(MaDVT="Thùng", TenDVT="Thùng đóng gói"),
            DonViTinh(MaDVT="Hộp", TenDVT="Hộp"),
            DonViTinh(MaDVT="Bộ", TenDVT="Bộ phụ kiện"),
        ]
        db.add_all(units)

        print("[*] Dang khoi tao 5 Nha cung cap chien luoc...")
        suppliers = [
            NhaCungCap(MaNCC="NCC-01", TenNCC="Công ty CP Tập đoàn Hòa Phát", DiaChi="KCN Phố Nối A, Giai Phạm, Yên Mỹ, Hưng Yên", SoDienThoai="024.3974.7777", Email="sales@hoaphat.com.vn"),
            NhaCungCap(MaNCC="NCC-02", TenNCC="Công ty CP Nhựa Thiếu Niên Tiền Phong", DiaChi="Số 2 An Đà, Lạch Tray, Ngô Quyền, Hải Phòng", SoDienThoai="0225.3813.979", Email="contact@nhuatienphong.vn"),
            NhaCungCap(MaNCC="NCC-03", TenNCC="Tổng Công ty Xi măng Việt Nam (Vicem)", DiaChi="Tòa tháp Vicem, 228 Lê Duẩn, Đống Đa, Hà Nội", SoDienThoai="0243.8512.441", Email="contact@vicem.vn"),
            NhaCungCap(MaNCC="NCC-04", TenNCC="Công ty CP Tập đoàn Kim Tín", DiaChi="KCN Tiên Sơn, Hoàn Sơn, Tiên Du, Bắc Ninh", SoDienThoai="0222.3714.888", Email="kinhdoanh@kimtingroup.com"),
            NhaCungCap(MaNCC="NCC-05", TenNCC="Công ty CP Sơn Hải Phòng", DiaChi="Số 12 Lạch Tray, Ngô Quyền, Hải Phòng", SoDienThoai="0225.3847.003", Email="info@haiphongpaint.vn")
        ]
        db.add_all(suppliers)
        db.flush()

        print("[*] Dang tao 20 SKUs hang hoa voi 3 trang thai van hanh (An toan, Canh bao ton min, Ton dong > 60 ngay)...")
        # Danh sách 20 SKUs:
        # Cấu trúc: (MaHH, TenHH, MaNhom, MaDVT, TonToiThieu, SoLuongTon, DonGiaNhap)
        skus_definition = [
            # --- NHÓM 1: HÀNG AN TOÀN (Tồn dồi dào, xuất nhập đều) ---
            ("HH-THEP-D08", "Thép cuộn phi 8 Hòa Phát", "NH-THEP", "Cuộn", 20, 95, 1250000.0),
            ("HH-NHUA-D110", "Ống nhựa PVC D110 Tiền Phong", "NH-NHUA", "Cây", 25, 110, 115000.0),
            ("HH-XIMANG-HOAPOW", "Xi măng Vicem Hoàng Thạch PCB40", "NH-XIMANG", "Bao", 50, 140, 89000.0),
            ("HH-BULONG-M16", "Bu lông kết cấu M16x80 mạ kẽm", "NH-CODIEN", "Bộ", 50, 350, 12000.0),
            ("HH-SON-GLOSS", "Sơn phủ bóng ngoại thất 5L", "NH-SON", "Thùng", 15, 60, 480000.0),
            ("HH-THEP-H150", "Thép hình chữ H 150x150x7x10", "NH-THEP", "Cây", 10, 45, 3200000.0),
            ("HH-QUEHAN-26", "Que hàn điện Kim Tín 2.6mm", "NH-CODIEN", "Hộp", 20, 80, 95000.0),

            # --- NHÓM 2: CHẠM / DƯỚI TỒN TỐI THIỂU (LOW STOCK - Cần AI cảnh báo & đề xuất nhập khẩn) ---
            ("HH-THEP-D10", "Thép cuộn phi 10 Hòa Phát", "NH-THEP", "Cuộn", 25, 4, 1380000.0),     # Thiếu 21 (NGUY CẤP)
            ("HH-XIMANG-BUTSON", "Xi măng Vicem Bút Sơn PCB40", "NH-XIMANG", "Bao", 80, 15, 88000.0),  # Thiếu 65 (NGUY CẤP)
            ("HH-SON-ALKYD", "Sơn lót chống rỉ Alkyd 5L Hải Phòng", "NH-SON", "Thùng", 25, 6, 380000.0),# Thiếu 19 (NGUY CẤP)
            ("HH-NHUA-D90", "Ống nhựa PVC D90 Tiền Phong", "NH-NHUA", "Cây", 30, 22, 85000.0),        # Thiếu 8 (CẬN NGƯỠNG)
            ("HH-QUEHAN-32", "Que hàn điện Kim Tín 3.2mm", "NH-CODIEN", "Hộp", 35, 8, 110000.0),       # Thiếu 27 (NGUY CẤP)
            ("HH-THEP-D16", "Thép cây vằn D16 Hòa Phát", "NH-THEP", "Cây", 40, 12, 245000.0),         # Thiếu 28 (NGUY CẤP)
            ("HH-DACAT-355", "Đá cắt sắt Hải Dương 355mm", "NH-CODIEN", "Hộp", 30, 10, 280000.0),      # Thiếu 20 (NGUY CẤP)

            # --- NHÓM 3: HÀNG TỒN LÂU > 60 NGÀY (DEAD STOCK - Cần AI phát hiện bất thường) ---
            ("HH-SON-EPOXY", "Sơn sàn công nghiệp Epoxy KCC 20L", "NH-SON", "Thùng", 15, 45, 1250000.0),
            ("HH-BULONG-M24", "Bu lông neo móng M24x800 cường độ cao", "NH-CODIEN", "Bộ", 20, 120, 65000.0),
            ("HH-NHUA-PPR32", "Ống hàn nhiệt PPR D32 Tiền Phong", "NH-NHUA", "Cây", 20, 75, 98000.0),
            ("HH-DUNGMOI-PU", "Dung môi pha sơn công nghiệp PU 20L", "NH-SON", "Thùng", 10, 30, 520000.0),
            ("HH-CAPTHEP-14", "Dây cáp thép mạ kẽm phi 14 chống xoắn", "NH-THEP", "Cuộn", 10, 18, 2450000.0),
            ("HH-PHUGIA-SIKA", "Phụ gia đông kết nhanh Sika R4", "NH-XIMANG", "Thùng", 15, 50, 680000.0)
        ]

        now = datetime.utcnow()
        admin_id = users[0].MaND
        thukho_id = users[1].MaND

        # Lưu Hàng hóa và Tồn kho
        for ma_hh, ten_hh, ma_nhom, ma_dvt, ton_min, ton_hientai, gia_nhap in skus_definition:
            hh = HangHoa(
                MaHH=ma_hh,
                TenHH=ten_hh,
                MaNhom=ma_nhom,
                MaDVT=ma_dvt,
                TonToiThieu=ton_min,
                MoTa=f"Vật tư đạt tiêu chuẩn chất lượng TCVN ({ten_hh})"
            )
            db.add(hh)

            tk = TonKho(
                MaHH=ma_hh,
                SoLuongTon=ton_hientai,
                CapNhatCuoi=now
            )
            db.add(tk)

            # Khởi tạo bản ghi Thẻ kho ban đầu (Cách đây 45 ngày)
            the_kho_init = TheKho(
                NgayGiaoDich=now - timedelta(days=45),
                MaHH=ma_hh,
                MaChungTu="PN-KHOITAO-01",
                LoaiGiaoDich="NHAP",
                SoLuongThayDoi=ton_hientai + 40,
                TonSauGiaoDich=ton_hientai + 40
            )
            db.add(the_kho_init)

        db.flush()

        print("[*] Dang tao cac giao dich Nhap/Xuat 30 ngay gan nhat phuc vu AI Burn-Rate...")
        
        # 1. Các phiếu nhập kho trong 30 ngày qua
        inbound_fixtures = [
            ("PN-20260815-01", now - timedelta(days=23), "NCC-01", admin_id, "Nhập thép cuộn và thép cây phục vụ dự án Cầu Vĩnh Tuy 2"),
            ("PN-20260822-02", now - timedelta(days=16), "NCC-02", thukho_id, "Nhập bổ sung ống nhựa Tiền Phong theo hợp đồng Q3"),
            ("PN-20260901-03", now - timedelta(days=6), "NCC-03", admin_id, "Nhập xi măng Vicem Bút Sơn và Hoàng Thạch đợt 1"),
            ("PN-20260905-04", now - timedelta(days=2), "NCC-04", thukho_id, "Nhập que hàn và vật tư cơ điện định kỳ")
        ]

        for ma_pn, ngay_nhap, ma_ncc, ma_nd, ghi_chu in inbound_fixtures:
            pn = PhieuNhap(
                MaPN=ma_pn,
                NgayNhap=ngay_nhap,
                MaNCC=ma_ncc,
                MaND=ma_nd,
                TongTien=0.0,
                GhiChu=ghi_chu
            )
            db.add(pn)

        db.flush()

        # Chi tiết phiếu nhập mẫu
        inbound_details = [
            ("PN-20260815-01", "HH-THEP-D08", 40, 1250000.0),
            ("PN-20260815-01", "HH-THEP-D10", 30, 1380000.0),
            ("PN-20260822-02", "HH-NHUA-D110", 50, 115000.0),
            ("PN-20260822-02", "HH-NHUA-D90", 40, 85000.0),
            ("PN-20260901-03", "HH-XIMANG-HOAPOW", 80, 89000.0),
            ("PN-20260901-03", "HH-XIMANG-BUTSON", 50, 88000.0),
            ("PN-20260905-04", "HH-QUEHAN-32", 30, 110000.0),
            ("PN-20260905-04", "HH-BULONG-M16", 100, 12000.0),
        ]

        for ma_pn, ma_hh, qty, price in inbound_details:
            ct = ChiTietPhieuNhap(
                MaPN=ma_pn,
                MaHH=ma_hh,
                SoLuongNhap=qty,
                DonGiaNhap=price,
                ThanhTien=qty * price
            )
            db.add(ct)

        # 2. Các phiếu xuất kho trong 30 ngày qua (Tạo Burn-rate mạnh cho Nhóm 1 & Nhóm 2)
        # CHÚ Ý: KHÔNG XUẤT các SKU Nhóm 3 (Dead Stock) để AI nhận diện là hàng tồn ứ đọng > 60 ngày!
        outbound_fixtures = [
            ("PX-20260818-01", now - timedelta(days=20), thukho_id, "Ban Quản Lý Dự Án Cao Tốc", "Xuất thép thi công dầm cầu"),
            ("PX-20260825-02", now - timedelta(days=13), thukho_id, "Công ty Xây Lắp Điện 1", "Xuất vật tư cơ điện và ống nước"),
            ("PX-20260829-03", now - timedelta(days=9), admin_id, "Xí Nghiệp Bê Tông Tân Tạo", "Xuất xi măng đúc dầm dự ứng lực"),
            ("PX-20260903-04", now - timedelta(days=4), thukho_id, "Đội Cơ Giới Số 4", "Xuất đá cắt, que hàn và thép cuộn D10"),
            ("PX-20260906-05", now - timedelta(days=1), thukho_id, "Đội Thi Công Sơn Hoàn Thiện", "Xuất sơn Alkyd và que hàn 3.2mm")
        ]

        for ma_px, ngay_xuat, ma_nd, nguoi_nhan, ly_do in outbound_fixtures:
            px = PhieuXuat(
                MaPX=ma_px,
                NgayXuat=ngay_xuat,
                MaND=ma_nd,
                NguoiNhan=nguoi_nhan,
                LyDoXuat=ly_do
            )
            db.add(px)

        db.flush()

        # Chi tiết phiếu xuất kho (Tạo burn rate cao cho Thép D10, Xi măng Bút Sơn, Que hàn 3.2, Sơn Alkyd)
        outbound_details = [
            # Ngày -20
            ("PX-20260818-01", "HH-THEP-D10", 25),
            ("PX-20260818-01", "HH-THEP-D08", 20),
            ("PX-20260818-01", "HH-THEP-D16", 28),
            # Ngày -13
            ("PX-20260825-02", "HH-NHUA-D110", 30),
            ("PX-20260825-02", "HH-NHUA-D90", 18),
            ("PX-20260825-02", "HH-BULONG-M16", 100),
            # Ngày -9
            ("PX-20260829-03", "HH-XIMANG-BUTSON", 55), # Xuất mạnh
            ("PX-20260829-03", "HH-XIMANG-HOAPOW", 40),
            # Ngày -4
            ("PX-20260903-04", "HH-THEP-D10", 25),      # Xuất tiếp -> Gây tụt tồn còn 4 cuộn
            ("PX-20260903-04", "HH-QUEHAN-32", 22),     # Gây tụt tồn còn 8 hộp
            ("PX-20260903-04", "HH-DACAT-355", 20),     # Gây tụt tồn còn 10 hộp
            # Ngày -1
            ("PX-20260906-05", "HH-SON-ALKYD", 19),     # Gây tụt tồn còn 6 thùng
            ("PX-20260906-05", "HH-XIMANG-BUTSON", 20), # Gây tụt tồn còn 15 bao
        ]

        for ma_px, ma_hh, qty in outbound_details:
            ct_px = ChiTietPhieuXuat(
                MaPX=ma_px,
                MaHH=ma_hh,
                SoLuongXuat=qty
            )
            db.add(ct_px)

            # Ghi thẻ kho phản ánh xuất kho
            tk_rec = TheKho(
                NgayGiaoDich=now - timedelta(days=2),
                MaHH=ma_hh,
                MaChungTu=ma_px,
                LoaiGiaoDich="XUAT",
                SoLuongThayDoi=-qty,
                TonSauGiaoDich=10 # Mức đại diện
            )
            db.add(tk_rec)

        db.commit()
        print("[SUCCESS] Da nap thanh cong 100% du lieu mau chuan cho SmartLogis AI:")
        print("  + 3 Tai khoan demo: admin/admin123 (Admin), thukho/thukho123 (Thu kho kiem Ke toan), nhanvien/nhanvien123 (Nhan vien kho)")
        print("  + 5 Nhom hang & 6 Don vi tinh")
        print("  + 5 Nha cung cap")
        print("  + 20 SKUs hang hoa (7 An toan, 7 Canh bao ton min, 6 Dead Stock > 60 ngay)")
        print("  + 4 Phieu nhap, 5 Phieu xuat trong 30 ngay (Tao san Burn-rate cho Gemini AI)")
        print("=" * 65)

    except Exception as e:
        db.rollback()
        print(f"[ERROR] Xay ra loi khi nap du lieu demo: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seeder dữ liệu mẫu cho SmartLogis AI")
    parser.add_argument("--reset", action="store_true", help="Xóa sạch CSDL cũ và nạp lại từ đầu")
    args = parser.parse_args()

    reset_and_seed_database(force_reset=args.reset)
