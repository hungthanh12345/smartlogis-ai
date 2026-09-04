# app/api/v1/inventory_router.py
from typing import List
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_active_user, require_role
from app.models.inventory_models import NguoiDung, HangHoa, TonKho, NhaCungCap
from app.schemas.inventory_schemas import (
    PhieuNhapCreate, PhieuNhapOut,
    PhieuXuatCreate, PhieuXuatOut,
    KPISummary, StockAlertItem, HangHoaOut
)
from app.services.inbound_service import execute_inbound_transaction
from app.services.outbound_service import execute_outbound_transaction
from app.services.inventory_service import get_dashboard_kpis, get_stock_alerts

router = APIRouter(prefix="/kho", tags=["Nghi?p V? Qu?n L? Kho (ACID)"])

@router.get("/kpis", response_model=KPISummary)
def api_get_kpis(db: Session = Depends(get_db)):
    """L?y 4 ch? s? KPI th?i gian th?c cho Dashboard v2.0."""
    return get_dashboard_kpis(db)

@router.get("/alerts", response_model=List[StockAlertItem])
def api_get_stock_alerts(db: Session = Depends(get_db)):
    """L?y danh s?ch c?c m?t h?ng ch?m ho?c d??i ng??ng t?n t?i thi?u (SoLuongTon <= TonToiThieu)."""
    return get_stock_alerts(db)

@router.get("/items", response_model=List[HangHoaOut])
def api_get_all_items(db: Session = Depends(get_db)):
    """L?y danh s?ch to?n b? m?t h?ng k?m s? l??ng t?n kh? d?ng hi?n t?i."""
    items = db.query(HangHoa).all()
    results = []
    for item in items:
        ton = item.ton_kho.SoLuongTon if item.ton_kho else 0
        results.append({
            "MaHH": item.MaHH,
            "TenHH": item.TenHH,
            "MaNhom": item.MaNhom,
            "MaDVT": item.MaDVT,
            "TonToiThieu": item.TonToiThieu,
            "MoTa": item.MoTa,
            "SoLuongTon": ton,
            "TenDVT": item.don_vi_tinh.TenDVT if item.don_vi_tinh else item.MaDVT
        })
    return results

@router.get("/suppliers")
def api_get_suppliers(db: Session = Depends(get_db)):
    """L?y danh s?ch nh? cung c?p."""
    return db.query(NhaCungCap).all()

@router.get("/check-stock/{ma_hh}")
def api_check_single_stock(ma_hh: str, db: Session = Depends(get_db)):
    """API th?m ??nh t?n kho t?c th?i ph?c v? Real-time validation tr?n giao di?n xu?t kho."""
    hh = db.query(HangHoa).filter(HangHoa.MaHH == ma_hh).first()
    if not hh:
        raise HTTPException(status_code=404, detail="Kh?ng t?m th?y m?t h?ng.")
    ton = hh.ton_kho.SoLuongTon if hh.ton_kho else 0
    return {
        "MaHH": hh.MaHH,
        "TenHH": hh.TenHH,
        "MaDVT": hh.MaDVT,
        "TonKhauDung": ton,
        "TonToiThieu": hh.TonToiThieu
    }

@router.post("/phieu-nhap", response_model=PhieuNhapOut, status_code=status.HTTP_201_CREATED)
def api_tao_phieu_nhap(
    phieu_in: PhieuNhapCreate,
    db: Session = Depends(get_db),
    current_user: NguoiDung = Depends(get_current_active_user)
):
    """API L?p Phi?u Nh?p Kho Inbound & C?p nh?t t?ng t?n kho trong 1 Transaction ACID."""
    phieu = execute_inbound_transaction(db, phieu_in, user_id=current_user.MaND)
    return phieu

@router.post("/phieu-xuat", response_model=PhieuXuatOut, status_code=status.HTTP_201_CREATED)
def api_tao_phieu_xuat(
    phieu_in: PhieuXuatCreate,
    db: Session = Depends(get_db),
    current_user: NguoiDung = Depends(get_current_active_user)
):
    """API L?p Phi?u Xu?t Kho Outbound c? Kh?a Bi Quan (SELECT FOR UPDATE) ch?ng t?n ?m."""
    phieu = execute_outbound_transaction(db, phieu_in, user_id=current_user.MaND)
    return phieu
