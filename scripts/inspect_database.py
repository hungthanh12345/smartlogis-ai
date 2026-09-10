# scripts/inspect_database.py
"""
Script Xem Tổng Thể CSDL MySQL - SmartLogis AI
Hiển thị:
1. Thông tin kết nối & trạng thái CSDL.
2. Thống kê số lượng bản ghi của toàn bộ 11 bảng.
3. Tổng quan số liệu kho (Tổng SKU, Tổng tồn, Phiếu nhập, Phiếu xuất).
4. Top 5 mặt hàng chạm ngưỡng tồn tối thiểu (Cảnh báo).
5. Top 5 phiếu nhập/xuất gần nhất.
"""

import sys
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

root_dir = str(Path(__file__).resolve().parent.parent)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app.core.config import settings
from app.models.inventory_models import (
    HangHoa, TonKho, NhomHang, DonViTinh, NhaCungCap,
    PhieuNhap, ChiTietPhieuNhap, PhieuXuat, ChiTietPhieuXuat, TheKho, NguoiDung
)

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def inspect_db():
    engine = create_engine(settings.DATABASE_URL)
    Session = sessionmaker(bind=engine)
    db = Session()

    print("=" * 78)
    print("           SMARTLOGIS AI - BẢNG ĐIỀU KHIỂN & BÁO CÁO TỔNG THỂ CSDL")
    print("=" * 78)
    print(f"[*] Máy chủ CSDL : MySQL 8.0 (localhost:3306)")
    print(f"[*] Database      : smartlogis_db")
    print(f"[*] Người dùng    : root")
    print("-" * 78)

    tables = [
        ("nguoi_dung", "Tài khoản người dùng (RBAC)", db.query(NguoiDung).count()),
        ("nhom_hang", "Nhóm hàng hóa vật tư", db.query(NhomHang).count()),
        ("don_vi_tinh", "Đơn vị tính chuẩn hóa", db.query(DonViTinh).count()),
        ("nha_cung_cap", "Đối tác nhà cung cấp", db.query(NhaCungCap).count()),
        ("hang_hoa", "Danh mục mặt hàng (SKU)", db.query(HangHoa).count()),
        ("ton_kho", "Số dư tồn kho khả dụng", db.query(TonKho).count()),
        ("phieu_nhap", "Phiếu nhập kho (Inbound)", db.query(PhieuNhap).count()),
        ("chi_tiet_phieu_nhap", "Chi tiết mặt hàng nhập kho", db.query(ChiTietPhieuNhap).count()),
        ("phieu_xuat", "Phiếu xuất kho (Outbound)", db.query(PhieuXuat).count()),
        ("chi_tiet_phieu_xuat", "Chi tiết mặt hàng xuất kho", db.query(ChiTietPhieuXuat).count()),
        ("the_kho", "Sổ thẻ kho lưu vết giao dịch", db.query(TheKho).count()),
    ]

    print(f"{'STT':<4} | {'TÊN BẢNG (TABLE)':<22} | {'MÔ TẢ NGHIỆP VỤ':<32} | {'SỐ DÒNG':>8}")
    print("-" * 78)
    total_rows = 0
    for idx, (tbl, desc, count) in enumerate(tables, 1):
        print(f"{idx:<4} | {tbl:<22} | {desc:<32} | {count:>8,}")
        total_rows += count
    print("-" * 78)
    print(f"TỔNG CỘNG TẤT CẢ CÁC BẢNG: {total_rows:,} BẢN GHI TRONG CSDL")
    print("=" * 78)

    # 1. Thống kê tồn kho
    total_qty = db.execute(text("SELECT COALESCE(SUM(SoLuongTon), 0) FROM ton_kho")).scalar()
    print(f"\n[+] TỔNG SỐ LƯỢNG HÀNG HÓA ĐANG NẰM TRONG KHO: {int(total_qty):,} đơn vị.")

    # 2. Cảnh báo tồn min
    low_stock = db.query(HangHoa, TonKho).join(TonKho, HangHoa.MaHH == TonKho.MaHH).filter(
        TonKho.SoLuongTon <= HangHoa.TonToiThieu
    ).limit(5).all()

    print("\n[!] TOP 5 MẶT HÀNG ĐANG CHẠM / DƯỚI NGƯỠNG TỒN TỐI THIỂU (CẦN NHẬP THÊM):")
    print(f"    {'MÃ SKU':<18} | {'TÊN MẶT HÀNG':<32} | {'TỒN HIỆN TẠI':>12} | {'TỒN MIN':>8}")
    print("    " + "-" * 74)
    for hh, tk in low_stock:
        print(f"    {hh.MaHH:<18} | {hh.TenHH[:30]:<32} | {tk.SoLuongTon:>12} | {hh.TonToiThieu:>8}")

    # 3. Phiếu nhập gần nhất
    recent_pn = db.query(PhieuNhap).order_by(PhieuNhap.NgayNhap.desc()).limit(3).all()
    print("\n[*] 3 PHIẾU NHẬP KHO GẦN ĐÂY NHẤT:")
    for pn in recent_pn:
        print(f"    - [{pn.MaPN}] Ngày: {pn.NgayNhap.strftime('%d/%m/%Y %H:%M')} | NCC: {pn.MaNCC} | Tổng tiền: {pn.TongTien:,.0f} VNĐ | Ghi chú: {pn.GhiChu or '---'}")

    # 4. Phiếu xuất gần nhất
    recent_px = db.query(PhieuXuat).order_by(PhieuXuat.NgayXuat.desc()).limit(3).all()
    print("\n[*] 3 PHIẾU XUẤT KHO GẦN ĐÂY NHẤT:")
    for px in recent_px:
        print(f"    - [{px.MaPX}] Ngày: {px.NgayXuat.strftime('%d/%m/%Y %H:%M')} | Người nhận: {px.NguoiNhan} | Lý do: {px.LyDoXuat or '---'}")

    print("\n" + "=" * 78 + "\n")
    db.close()
    engine.dispose()


if __name__ == "__main__":
    inspect_db()
