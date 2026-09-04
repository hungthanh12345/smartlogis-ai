# app/models/inventory_models.py
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, 
    ForeignKey, CheckConstraint, Text, Boolean
)
from sqlalchemy.orm import relationship
from app.core.database import Base

class NguoiDung(Base):
    """B?ng ng??i d?ng h? th?ng v?i ph?n quy?n 3 vai tr?: Admin, Thukho, Ketoan."""
    __tablename__ = "nguoi_dung"

    MaND = Column(Integer, primary_key=True, autoincrement=True)
    TenDangNhap = Column(String(50), unique=True, index=True, nullable=False)
    MatKhau = Column(String(255), nullable=False)
    HoTen = Column(String(100), nullable=False)
    VaiTro = Column(String(20), nullable=False, default="Thukho")  # 'Admin', 'Thukho', 'Ketoan'
    KichHoat = Column(Boolean, default=True, nullable=False)
    NgayTao = Column(DateTime, default=datetime.utcnow, nullable=False)

    phieu_nhap = relationship("PhieuNhap", back_populates="nguoi_dung")
    phieu_xuat = relationship("PhieuXuat", back_populates="nguoi_dung")

class NhomHang(Base):
    """Ph?n lo?i danh m?c h?ng h?a (V?t li?u, Ph? ki?n, H?a ch?t...)."""
    __tablename__ = "nhom_hang"

    MaNhom = Column(String(50), primary_key=True)
    TenNhom = Column(String(255), nullable=False)
    MoTa = Column(Text, nullable=True)

    hang_hoa = relationship("HangHoa", back_populates="nhom_hang")

class DonViTinh(Base):
    """??n v? t?nh chu?n h?a (C?y, Cu?n, Th?ng, H?p, Bao...)."""
    __tablename__ = "don_vi_tinh"

    MaDVT = Column(String(20), primary_key=True)
    TenDVT = Column(String(100), nullable=False)

    hang_hoa = relationship("HangHoa", back_populates="don_vi_tinh")

class NhaCungCap(Base):
    """Th?ng tin c?c ??i t?c cung c?p nguy?n v?t t?, h?ng h?a."""
    __tablename__ = "nha_cung_cap"

    MaNCC = Column(String(50), primary_key=True)
    TenNCC = Column(String(255), nullable=False, index=True)
    DiaChi = Column(String(255), nullable=True)
    SoDienThoai = Column(String(50), nullable=True)
    Email = Column(String(100), nullable=True)

    phieu_nhap = relationship("PhieuNhap", back_populates="nha_cung_cap")

class HangHoa(Base):
    """Th?c th? h?ng h?a trong kho (SKU)."""
    __tablename__ = "hang_hoa"

    MaHH = Column(String(50), primary_key=True, index=True)
    TenHH = Column(String(255), nullable=False, index=True)
    MaNhom = Column(String(50), ForeignKey("nhom_hang.MaNhom"), nullable=False)
    MaDVT = Column(String(20), ForeignKey("don_vi_tinh.MaDVT"), nullable=False)
    TonToiThieu = Column(Integer, default=10, nullable=False)
    MoTa = Column(Text, nullable=True)

    nhom_hang = relationship("NhomHang", back_populates="hang_hoa")
    don_vi_tinh = relationship("DonViTinh", back_populates="hang_hoa")
    ton_kho = relationship("TonKho", back_populates="hang_hoa", uselist=False, cascade="all, delete-orphan")
    the_kho = relationship("TheKho", back_populates="hang_hoa")
    chi_tiet_nhap = relationship("ChiTietPhieuNhap", back_populates="hang_hoa")
    chi_tiet_xuat = relationship("ChiTietPhieuXuat", back_populates="hang_hoa")

class TonKho(Base):
    """Th?c th? l?u tr? s? l??ng t?n kho kh? d?ng hi?n th?i v?i r?ng bu?c CheckConstraint."""
    __tablename__ = "ton_kho"
    __table_args__ = (
        CheckConstraint("SoLuongTon >= 0", name="check_soluongton_khong_am"),
    )

    MaHH = Column(String(50), ForeignKey("hang_hoa.MaHH", ondelete="CASCADE"), primary_key=True)
    SoLuongTon = Column(Integer, nullable=False, default=0)
    CapNhatCuoi = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    hang_hoa = relationship("HangHoa", back_populates="ton_kho")

class PhieuNhap(Base):
    """Ch?ng t? nh?p kho (Master)."""
    __tablename__ = "phieu_nhap"

    MaPN = Column(String(50), primary_key=True, index=True)
    NgayNhap = Column(DateTime, default=datetime.utcnow, nullable=False)
    MaNCC = Column(String(50), ForeignKey("nha_cung_cap.MaNCC"), nullable=False)
    MaND = Column(Integer, ForeignKey("nguoi_dung.MaND"), nullable=False)
    TongTien = Column(Float, default=0.0, nullable=False)
    GhiChu = Column(String(500), nullable=True)

    nha_cung_cap = relationship("NhaCungCap", back_populates="phieu_nhap")
    nguoi_dung = relationship("NguoiDung", back_populates="phieu_nhap")
    chi_tiet = relationship("ChiTietPhieuNhap", back_populates="phieu_nhap", cascade="all, delete-orphan")

    @property
    def items(self):
        return self.chi_tiet

class ChiTietPhieuNhap(Base):
    """Chi tiết các mặt hàng trong phiếu nhập (Detail)."""
    __tablename__ = "chi_tiet_phieu_nhap"

    MaCTPN = Column(Integer, primary_key=True, autoincrement=True)
    MaPN = Column(String(50), ForeignKey("phieu_nhap.MaPN", ondelete="CASCADE"), nullable=False)
    MaHH = Column(String(50), ForeignKey("hang_hoa.MaHH"), nullable=False)
    SoLuongNhap = Column(Integer, nullable=False)
    DonGiaNhap = Column(Float, nullable=False)
    ThanhTien = Column(Float, nullable=False)

    phieu_nhap = relationship("PhieuNhap", back_populates="chi_tiet")
    hang_hoa = relationship("HangHoa", back_populates="chi_tiet_nhap")

class PhieuXuat(Base):
    """Chứng từ xuất kho (Master)."""
    __tablename__ = "phieu_xuat"

    MaPX = Column(String(50), primary_key=True, index=True)
    NgayXuat = Column(DateTime, default=datetime.utcnow, nullable=False)
    MaND = Column(Integer, ForeignKey("nguoi_dung.MaND"), nullable=False)
    NguoiNhan = Column(String(255), nullable=False)
    LyDoXuat = Column(String(500), nullable=True)

    nguoi_dung = relationship("NguoiDung", back_populates="phieu_xuat")
    chi_tiet = relationship("ChiTietPhieuXuat", back_populates="phieu_xuat", cascade="all, delete-orphan")

    @property
    def items(self):
        return self.chi_tiet

class ChiTietPhieuXuat(Base):
    """Chi ti?t c?c m?t h?ng trong phi?u xu?t (Detail)."""
    __tablename__ = "chi_tiet_phieu_xuat"

    MaCTPX = Column(Integer, primary_key=True, autoincrement=True)
    MaPX = Column(String(50), ForeignKey("phieu_xuat.MaPX", ondelete="CASCADE"), nullable=False)
    MaHH = Column(String(50), ForeignKey("hang_hoa.MaHH"), nullable=False)
    SoLuongXuat = Column(Integer, nullable=False)

    phieu_xuat = relationship("PhieuXuat", back_populates="chi_tiet")
    hang_hoa = relationship("HangHoa", back_populates="chi_tiet_xuat")

class TheKho(Base):
    """S? th? kho l?u v?t to?n b? bi?n ??ng giao d?ch nh?p xu?t v? t?n l?y k? theo th?i gian."""
    __tablename__ = "the_kho"

    MaTK = Column(Integer, primary_key=True, autoincrement=True)
    NgayGiaoDich = Column(DateTime, default=datetime.utcnow, index=True)
    MaHH = Column(String(50), ForeignKey("hang_hoa.MaHH"), nullable=False, index=True)
    MaChungTu = Column(String(50), nullable=False)
    LoaiGiaoDich = Column(String(10), nullable=False)  # 'NHAP' ho?c 'XUAT'
    SoLuongThayDoi = Column(Integer, nullable=False)
    TonSauGiaoDich = Column(Integer, nullable=False)

    hang_hoa = relationship("HangHoa", back_populates="the_kho")
