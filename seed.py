# seed.py - Khởi tạo dữ liệu mẫu ban đầu cho SmartLogis AI
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.core.security import get_password_hash
from app.models.inventory_models import (
    NguoiDung, NhomHang, DonViTinh, NhaCungCap, 
    HangHoa, TonKho, PhieuNhap, ChiTietPhieuNhap, 
    PhieuXuat, ChiTietPhieuXuat, TheKho
)

def seed_database():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    try:
        # 1. Kiểm tra nếu đã có tài khoản admin thì bỏ qua
        if db.query(NguoiDung).filter_by(TenDangNhap="admin").first():
            print("[OK] Co so du lieu da co du lieu. Bo qua seed.")
            return

        print("[*] Dang khoi tao du lieu mau (Seed Data)...")

        # 2. Khởi tạo Người dùng (Admin, Thủ kho, Kế toán)
        users = [
            NguoiDung(
                TenDangNhap="admin",
                MatKhau=get_password_hash("admin123"),
                HoTen="Nguyễn Thành Hưng (Admin)",
                VaiTro="Admin",
                KichHoat=True
            ),
            NguoiDung(
                TenDangNhap="thukho",
                MatKhau=get_password_hash("thukho123"),
                HoTen="Hoàng Tiến Đạt (Thủ kho)",
                VaiTro="Thukho",
                KichHoat=True
            ),
            NguoiDung(
                TenDangNhap="ketoan",
                MatKhau=get_password_hash("ketoan123"),
                HoTen="Hoàng Tiến Đạt (Kế toán)",
                VaiTro="Ketoan",
                KichHoat=True
            ),

        ]
        db.add_all(users)
        db.flush()

        # 3. Khởi tạo Nhóm Hàng
        categories = [
            NhomHang(MaNhom="NH-THEP", TenNhom="Thép & Kim loại xây dựng", MoTa="Các loại thép cuộn, thép cây, kết cấu"),
            NhomHang(MaNhom="NH-NHUA", TenNhom="Ống & Phụ kiện nhựa", MoTa="Ống cấp thoát nước PVC, HDPE, PPR"),
            NhomHang(MaNhom="NH-XIMANG", TenNhom="Xi măng & Bê tông", MoTa="Xi măng bao, phụ gia bê tông"),
            NhomHang(MaNhom="NH-SON", TenNhom="Sơn & Hóa chất bảo vệ", MoTa="Sơn chống rỉ, sơn epoxy, dung môi"),
            NhomHang(MaNhom="NH-CODIEN", TenNhom="Vật tư cơ điện & Phụ kiện", MoTa="Que hàn, bu lông, ốc vít, cáp điện")
        ]
        db.add_all(categories)

        # 4. Khởi tạo Đơn Vị Tính
        units = [
            DonViTinh(MaDVT="Cuộn", TenDVT="Cuộn"),
            DonViTinh(MaDVT="Cây", TenDVT="Cây"),
            DonViTinh(MaDVT="Bao", TenDVT="Bao (50kg)"),
            DonViTinh(MaDVT="Thùng", TenDVT="Thùng"),
            DonViTinh(MaDVT="Hộp", TenDVT="Hộp"),
            DonViTinh(MaDVT="Bộ", TenDVT="Bộ"),
        ]
        db.add_all(units)

        # 5. Khởi tạo Nhà Cung Cấp
        suppliers = [
            NhaCungCap(MaNCC="NCC-01", TenNCC="Công ty CP Thép Việt Đức", DiaChi="KCN Bình Xuyên, Vĩnh Phúc", SoDienThoai="0211.3888.999", Email="sales@vietducthep.vn"),
            NhaCungCap(MaNCC="NCC-02", TenNCC="Công ty TNHH Nhựa Tiền Phong", DiaChi="2 An Đà, Ngô Quyền, Hải Phòng", SoDienThoai="0225.3813.979", Email="contact@nhuatienphong.vn"),
            NhaCungCap(MaNCC="NCC-03", TenNCC="Tập đoàn Xi măng Vicem", DiaChi="228 Lê Duẩn, Đống Đa, Hà Nội", SoDienThoai="0243.8512.441", Email="info@vicem.vn"),
            NhaCungCap(MaNCC="NCC-04", TenNCC="Công ty CP Kim Tín", DiaChi="KCN Tiên Sơn, Bắc Ninh", SoDienThoai="0222.3714.888", Email="kinhdoanh@kimtingroup.com"),
            NhaCungCap(MaNCC="NCC-05", TenNCC="Công ty Sơn Hải Phòng", DiaChi="12 Lạch Tray, Ngô Quyền, Hải Phòng", SoDienThoai="0225.3847.003", Email="haiphongpaint@hp.vn")
        ]
        db.add_all(suppliers)
        db.flush()

        # 6. Khởi tạo Danh mục Mặt Hàng & Tồn Kho Ban Đầu
        items_data = [
            ("HH-001", "Thép cuộn phi 8 Việt Đức", "NH-THEP", "Cuộn", 20, 85, 1250000.0),
            ("HH-002", "Thép cuộn phi 10 Việt Đức", "NH-THEP", "Cuộn", 20, 60, 1380000.0),
            ("HH-003", "Thép cây phi 16 Hòa Phát", "NH-THEP", "Cây", 50, 45, 245000.0),      # Cận ngưỡng min
            ("HH-004", "Ống nhựa PVC D90 Tiền Phong", "NH-NHUA", "Cây", 30, 120, 85000.0),
            ("HH-005", "Ống nhựa PVC D110 Tiền Phong", "NH-NHUA", "Cây", 25, 90, 115000.0),
            ("HH-008", "Sơn chống rỉ Alkyd 5L Hải Phòng", "NH-SON", "Thùng", 30, 10, 380000.0), # NGUY CẤP (Thiếu 20)
            ("HH-009", "Sơn lót Epoxy 2 thành phần 20L", "NH-SON", "Thùng", 15, 6, 1200000.0),  # NGUY CẤP (Thiếu 9)
            ("HH-014", "Xi măng Holcim PCB40", "NH-XIMANG", "Bao", 100, 25, 88000.0),          # NGUY CẤP (Thiếu 75)
            ("HH-015", "Bu lông M16x80 mạ kẽm", "NH-CODIEN", "Bộ", 50, 400, 12000.0),
            ("HH-016", "Bu lông neo móng M24x600", "NH-CODIEN", "Bộ", 30, 150, 45000.0),
            ("HH-029", "Ống nhựa Bình Minh D60", "NH-NHUA", "Cây", 20, 18, 52000.0),          # Cận ngưỡng min
            ("HH-035", "Que hàn điện Kim Tín 3.2mm", "NH-CODIEN", "Hộp", 40, 8, 110000.0),      # NGUY CẤP (Thiếu 32)
            ("HH-040", "Sơn phủ màu ghi sáng 5L", "NH-SON", "Thùng", 25, 12, 420000.0),        # NGUY CẤP (Thiếu 13)
            ("HH-045", "Dây cáp thép mạ kẽm phi 12", "NH-THEP", "Cuộn", 10, 7, 2150000.0),     # Cận ngưỡng min
            ("HH-050", "Đá cắt sắt Hải Dương 355mm", "NH-CODIEN", "Hộp", 30, 14, 280000.0),    # NGUY CẤP (Thiếu 16)
        ]

        now = datetime.utcnow()
        admin_user = users[0]

        for ma_hh, ten_hh, ma_nhom, ma_dvt, ton_min, ton_hientai, gia_nhap in items_data:
            hh = HangHoa(
                MaHH=ma_hh,
                TenHH=ten_hh,
                MaNhom=ma_nhom,
                MaDVT=ma_dvt,
                TonToiThieu=ton_min,
                MoTa=f"Vật tư chất lượng cao phục vụ thi công công trình ({ten_hh})"
            )
            db.add(hh)

            tk = TonKho(
                MaHH=ma_hh,
                SoLuongTon=ton_hientai,
                CapNhatCuoi=now
            )
            db.add(tk)

            # Giao dịch khởi tạo thẻ kho
            the_kho = TheKho(
                NgayGiaoDich=now - timedelta(days=10),
                MaHH=ma_hh,
                MaChungTu="PN-KHOITAO-001",
                LoaiGiaoDich="NHAP",
                SoLuongThayDoi=ton_hientai + 20,
                TonSauGiaoDich=ton_hientai + 20
            )
            db.add(the_kho)

            # Giao dịch xuất gần đây
            the_kho_xuat = TheKho(
                NgayGiaoDich=now - timedelta(days=2),
                MaHH=ma_hh,
                MaChungTu="PX-20260902-001",
                LoaiGiaoDich="XUAT",
                SoLuongThayDoi=-20,
                TonSauGiaoDich=ton_hientai
            )
            db.add(the_kho_xuat)

        # 7. Phiếu nhập & xuất mẫu
        pn_sample = PhieuNhap(
            MaPN="PN-20260901-001",
            NgayNhap=now - timedelta(days=3),
            MaNCC="NCC-01",
            MaND=admin_user.MaND,
            TongTien=76000000.0,
            GhiChu="Nhập bổ sung nguyên vật liệu dự án xây dựng Quý 3"
        )
        db.add(pn_sample)
        db.flush()

        ct_pn = ChiTietPhieuNhap(
            MaPN=pn_sample.MaPN,
            MaHH="HH-001",
            SoLuongNhap=50,
            DonGiaNhap=1250000.0,
            ThanhTien=62500000.0
        )
        db.add(ct_pn)

        px_sample = PhieuXuat(
            MaPX="PX-20260902-001",
            NgayXuat=now - timedelta(days=1),
            MaND=admin_user.MaND,
            NguoiNhan="Đội thi công Xây dựng Tân Thịnh",
            LyDoXuat="Xuất vật tư kết cấu dầm cầu giai đoạn 1"
        )
        db.add(px_sample)

        db.commit()
        print("[SUCCESS] Khoi tao du lieu mau hoan tat 100%!")

    except Exception as e:
        db.rollback()
        print(f"[ERROR] Loi khi seed du lieu: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
