# app/api/v1/reports_router.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.inventory_service import get_the_kho_by_item
from app.schemas.inventory_schemas import TheKhoRecord

router = APIRouter(prefix="/reports", tags=["B?o C?o & Th? Kho (Reports)"])

@router.get("/the-kho/{ma_hh}", response_model=List[TheKhoRecord])
def api_get_the_kho(ma_hh: str, limit: int = 50, db: Session = Depends(get_db)):
    """Tra c?u l?ch s? bi?n ??ng Th? kho v? t?n l?y k? c?a m?t m?t h?ng."""
    return get_the_kho_by_item(db, ma_hh, limit=limit)

@router.get("/export/excel")
def api_export_excel_stub(
    loai_bao_cao: str = Query("nhap_xuat_ton", description="Lo?i b?o c?o c?n xu?t"),
    db: Session = Depends(get_db)
):
    """
    [STUB - S?N S?NG CHO GIAI ?O?N 3]
    TODO: T?ch h?p th? vi?n openpyxl ?? k?t xu?t file Excel chu?n bi?u m?u k? to?n kho.
    Quy tr?nh: Truy v?n CSDL -> Ghi d? li?u v?o Workbook -> ??nh d?ng cell borders, s? ti?n -> Tr? v? StreamingResponse.
    """
    return {
        "status": "ready_for_sprint_3",
        "message": "Ch?c n?ng xu?t b?o c?o Excel ?ang ???c k?t n?i v?i module openpyxl.",
        "report_type": loai_bao_cao
    }

@router.get("/export/pdf")
def api_export_pdf_stub(
    ma_phieu: str = Query(..., description="M? ch?ng t? c?n in ra file PDF"),
    db: Session = Depends(get_db)
):
    """
    [STUB - S?N S?NG CHO GIAI ?O?N 3]
    TODO: T?ch h?p ReportLab / WeasyPrint ?? sinh b?n in phi?u nh?p/xu?t kho PDF.
    """
    return {
        "status": "ready_for_sprint_3",
        "message": "Ch?c n?ng in phi?u xu?t/nh?p kho PDF ?ang ???c c?u h?nh bi?u m?u ReportLab.",
        "voucher_id": ma_phieu
    }
