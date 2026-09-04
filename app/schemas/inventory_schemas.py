# app/schemas/inventory_schemas.py
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

# --- Schema cho Danh m?c ---
class HangHoaOut(BaseModel):
    MaHH: str
    TenHH: str
    MaNhom: str
    MaDVT: str
    TonToiThieu: int
    MoTa: Optional[str] = None
    SoLuongTon: int = 0
    TenDVT: Optional[str] = None

    class Config:
        from_attributes = True

# --- Schema cho Phi?u Nh?p ---
class ChiTietNhapCreate(BaseModel):
    MaHH: str
    SoLuongNhap: int = Field(gt=0, description="S? l??ng nh?p ph?i > 0")
    DonGiaNhap: float = Field(ge=0, description="??n gi? nh?p kh?ng ???c ?m")

class PhieuNhapCreate(BaseModel):
    MaNCC: str
    GhiChu: Optional[str] = None
    items: List[ChiTietNhapCreate] = Field(min_length=1, description="Phi?u ph?i c? ?t nh?t 1 d?ng h?ng")

class ChiTietNhapOut(BaseModel):
    MaCTPN: int
    MaHH: str
    TenHH: Optional[str] = None
    SoLuongNhap: int
    DonGiaNhap: float
    ThanhTien: float

    class Config:
        from_attributes = True

class PhieuNhapOut(BaseModel):
    MaPN: str
    NgayNhap: datetime
    MaNCC: str
    MaND: int
    TongTien: float
    GhiChu: Optional[str] = None
    items: List[ChiTietNhapOut] = []

    class Config:
        from_attributes = True

# --- Schema cho Phi?u Xu?t ---
class ChiTietXuatCreate(BaseModel):
    MaHH: str
    SoLuongXuat: int = Field(gt=0, description="S? l??ng xu?t ph?i > 0")

class PhieuXuatCreate(BaseModel):
    NguoiNhan: str = Field(min_length=2, description="T?n ng??i ho?c ??n v? nh?n h?ng")
    LyDoXuat: Optional[str] = None
    items: List[ChiTietXuatCreate] = Field(min_length=1, description="Phi?u ph?i c? ?t nh?t 1 d?ng h?ng")

class ChiTietXuatOut(BaseModel):
    MaCTPX: int
    MaHH: str
    TenHH: Optional[str] = None
    SoLuongXuat: int

    class Config:
        from_attributes = True

class PhieuXuatOut(BaseModel):
    MaPX: str
    NgayXuat: datetime
    MaND: int
    NguoiNhan: str
    LyDoXuat: Optional[str] = None
    items: List[ChiTietXuatOut] = []

    class Config:
        from_attributes = True

# --- Schema cho Dashboard & C?nh b?o T?n min ---
class StockAlertItem(BaseModel):
    MaHH: str
    TenHH: str
    MaDVT: str
    SoLuongTon: int
    TonToiThieu: int
    MucDo: str  # 'danger' (nguy c?p) ho?c 'warning' (c?n ng??ng)
    ThieuHut: int
    TenNCCGoiY: Optional[str] = None

class KPISummary(BaseModel):
    tong_sku: int
    canh_bao_ton_min: int
    tong_gia_tri_xuat_thang: float
    tong_giao_dich_thang: int
    tong_phieu_nhap: int
    tong_phieu_xuat: int

# --- Schema cho Th? Kho ---
class TheKhoRecord(BaseModel):
    MaTK: int
    NgayGiaoDich: datetime
    MaHH: str
    MaChungTu: str
    LoaiGiaoDich: str
    SoLuongThayDoi: int
    TonSauGiaoDich: int

    class Config:
        from_attributes = True

# --- Schema cho AI Advisory ---
class AIAdvisoryResponse(BaseModel):
    model_name: str
    prompt_technique: str
    insights: List[dict]
    raw_summary: Optional[str] = None
    csdl_integrity: Optional[str] = "100% ACID Compliant. 0 Negative Stock."
    recommendations: Optional[List[dict]] = None
