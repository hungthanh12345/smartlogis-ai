# app/schemas/inventory_schemas.py
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

# --- Schema cho Danh mục & Nhóm Hàng & ĐVT ---
class NhomHangOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    MaNhom: str
    TenNhom: str
    MoTa: Optional[str] = None

class DonViTinhOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    MaDVT: str
    TenDVT: str

class HangHoaCreate(BaseModel):
    MaHH: str = Field(min_length=2, max_length=50, description="Mã hàng hóa duy nhất")
    TenHH: str = Field(min_length=2, max_length=255, description="Tên hàng hóa")
    MaNhom: str = Field(description="Mã nhóm hàng")
    MaDVT: str = Field(description="Mã đơn vị tính")
    TonToiThieu: int = Field(default=10, ge=0, description="Ngưỡng tồn kho tối thiểu cảnh báo")
    MoTa: Optional[str] = None
    SoLuongBanDau: int = Field(default=0, ge=0, description="Số lượng tồn kho ban đầu khi khai báo")

class HangHoaUpdate(BaseModel):
    TenHH: str = Field(min_length=2, max_length=255)
    MaNhom: str
    MaDVT: str
    TonToiThieu: int = Field(ge=0)
    MoTa: Optional[str] = None

class HangHoaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    MaHH: str
    TenHH: str
    MaNhom: str
    MaDVT: str
    TonToiThieu: int
    MoTa: Optional[str] = None
    SoLuongTon: int = 0
    TenDVT: Optional[str] = None
    TenNhom: Optional[str] = None

# --- Schema cho Nhà Cung Cấp ---
class NhaCungCapCreate(BaseModel):
    MaNCC: str = Field(min_length=2, max_length=50, description="Mã nhà cung cấp duy nhất")
    TenNCC: str = Field(min_length=2, max_length=255, description="Tên nhà cung cấp")
    DiaChi: Optional[str] = None
    SoDienThoai: Optional[str] = None
    Email: Optional[str] = None

class NhaCungCapUpdate(BaseModel):
    TenNCC: str = Field(min_length=2, max_length=255)
    DiaChi: Optional[str] = None
    SoDienThoai: Optional[str] = None
    Email: Optional[str] = None

class NhaCungCapOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    MaNCC: str
    TenNCC: str
    DiaChi: Optional[str] = None
    SoDienThoai: Optional[str] = None
    Email: Optional[str] = None
    SoPhieuNhap: int = 0
    TongGiaTriNhap: float = 0.0
    NgayNhapGanNhat: Optional[str] = None

class LichSuPhieuNhapItem(BaseModel):
    MaHH: str
    TenHH: Optional[str] = None
    SoLuongNhap: int
    DonGiaNhap: float
    ThanhTien: float

class LichSuPhieuNhap(BaseModel):
    MaPN: str
    NgayNhap: datetime
    NguoiLap: Optional[str] = None
    TongTien: float
    GhiChu: Optional[str] = None
    SoMatHang: int = 0
    ChiTiet: List[LichSuPhieuNhapItem] = []

class NhaCungCapDetailOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    MaNCC: str
    TenNCC: str
    DiaChi: Optional[str] = None
    SoDienThoai: Optional[str] = None
    Email: Optional[str] = None
    SoPhieuNhap: int = 0
    TongGiaTriNhap: float = 0.0
    NgayNhapGanNhat: Optional[str] = None
    LichSuNhap: List[LichSuPhieuNhap] = []

class SupplierKPIs(BaseModel):
    TongNCC: int = 0
    NCCActive: int = 0
    TongChiTieu: float = 0.0
    TopNCC: Optional[str] = None
    TopNCCTien: float = 0.0


# --- Schema cho Phiếu Nhập ---
class ChiTietNhapCreate(BaseModel):
    MaHH: str
    SoLuongNhap: int = Field(gt=0, description="Số lượng nhập phải > 0")
    DonGiaNhap: float = Field(ge=0, description="Đơn giá nhập không được âm")

class PhieuNhapCreate(BaseModel):
    MaNCC: str
    GhiChu: Optional[str] = None
    items: List[ChiTietNhapCreate] = Field(min_length=1, description="Phiếu phải có ít nhất 1 dòng hàng")

class ChiTietNhapOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    MaCTPN: int
    MaHH: str
    TenHH: Optional[str] = None
    SoLuongNhap: int
    DonGiaNhap: float
    ThanhTien: float

class PhieuNhapOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    MaPN: str
    NgayNhap: datetime
    MaNCC: str
    MaND: int
    TongTien: float
    GhiChu: Optional[str] = None
    items: List[ChiTietNhapOut] = []

# --- Schema cho Phiếu Xuất ---
class ChiTietXuatCreate(BaseModel):
    MaHH: str
    SoLuongXuat: int = Field(gt=0, description="Số lượng xuất phải > 0")

class PhieuXuatCreate(BaseModel):
    NguoiNhan: str = Field(min_length=2, description="Tên người hoặc đơn vị nhận hàng")
    LyDoXuat: Optional[str] = None
    items: List[ChiTietXuatCreate] = Field(min_length=1, description="Phiếu phải có ít nhất 1 dòng hàng")

class ChiTietXuatOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    MaCTPX: int
    MaHH: str
    TenHH: Optional[str] = None
    SoLuongXuat: int

class PhieuXuatOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    MaPX: str
    NgayXuat: datetime
    MaND: int
    NguoiNhan: str
    LyDoXuat: Optional[str] = None
    items: List[ChiTietXuatOut] = []

# --- Schema cho Dashboard & Cảnh báo Tồn min ---
class StockAlertItem(BaseModel):
    MaHH: str
    TenHH: str
    MaDVT: str
    SoLuongTon: int
    TonToiThieu: int
    MucDo: str  # 'danger' (nguy cấp) hoặc 'warning' (cận ngưỡng)
    ThieuHut: int
    TenNCCGoiY: Optional[str] = None

class KPISummary(BaseModel):
    tong_sku: int
    canh_bao_ton_min: int
    tong_gia_tri_xuat_thang: float
    tong_giao_dich_thang: int
    tong_phieu_nhap: int
    tong_phieu_xuat: int

# --- Schema cho Thẻ Kho ---
class TheKhoRecord(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    MaTK: int
    NgayGiaoDich: datetime
    MaHH: str
    TenHH: Optional[str] = None
    MaChungTu: str
    LoaiGiaoDich: str  # 'NHAP' hoặc 'XUAT'
    SoLuongThayDoi: int
    TonSauGiaoDich: int

# --- Schema cho Trợ Lý AI ---
class AIInsightItem(BaseModel):
    icon: str
    title: str
    content: str

class AIAdvisoryResponse(BaseModel):
    model_name: str
    prompt_technique: str
    insights: List[AIInsightItem]
    raw_summary: str
    is_fallback: Optional[bool] = False
    markdown_report: Optional[str] = None

class AIRestockRecommendationItem(BaseModel):
    ma_hh: str
    ten_hh: str
    ton_hien_tai: int
    ton_toi_thieu: int
    thieu_hut: Optional[int] = 0
    burn_rate_ngay: Optional[float] = 0.0
    so_luong_de_xuat_nhap: int
    muc_do: Optional[str] = "CANH_BAO"
    ly_do: Optional[str] = None

class AIReportOverview(BaseModel):
    tong_so_sku: int
    so_sku_canh_bao_ton_min: int
    so_sku_u_dong_60_ngay: int
    danh_gia_chung: str

class AIAbnormalFluctuation(BaseModel):
    xuat_dot_bien: List[Dict[str, Any]] = []
    hang_ton_lau_60_ngay: List[Dict[str, Any]] = []

class AIReportResponse(BaseModel):
    status: str = "success"
    model_used: str
    is_fallback: bool = False
    fallback_reason: Optional[str] = None
    data_context_summary: Dict[str, Any]
    phan_1_tong_quan: Dict[str, Any]
    phan_2_canh_bao_va_de_xuat_nhap: List[Dict[str, Any]]
    phan_3_bien_dong_bat_thuong: Dict[str, Any]
    insights_widget: List[AIInsightItem]
    markdown_report: str
