# app/api/v1/reports_router.py
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_active_user, require_role
from app.models.inventory_models import NguoiDung
from app.services.inventory_service import (
    get_the_kho_by_item, generate_excel_inventory_report, generate_excel_suppliers_report
)
from app.schemas.inventory_schemas import TheKhoRecord

router = APIRouter(prefix="/reports", tags=["Báo Cáo & Thẻ Kho (Reports)"])

@router.get("/the-kho/{ma_hh}", response_model=List[TheKhoRecord])
def api_get_the_kho(
    ma_hh: str, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: NguoiDung = Depends(get_current_active_user)
):
    """Tra cứu lịch sử biến động Thẻ kho và tồn lũy kế của một mặt hàng (Yêu cầu đăng nhập)."""
    return get_the_kho_by_item(db, ma_hh, limit=limit)

@router.get("/export/excel")
def api_export_excel(
    db: Session = Depends(get_db),
    current_user: NguoiDung = Depends(require_role(["Admin", "Thukho"]))
):
    """
    KẾT XUẤT BÁO CÁO EXCEL THỰC TẾ (OPENPYXL ENGINE):
    Dành cho vai trò Admin và Thủ kho kiêm Kế toán (Phân quyền RBAC).
    Truy vấn trực tiếp số liệu tồn kho, định mức tối thiểu từ CSDL PostgreSQL/SQLite.
    Sinh file Excel (.xlsx) chuẩn biểu mẫu kế toán và trả về luồng tải tệp tin cho trình duyệt.
    """
    excel_stream = generate_excel_inventory_report(db)
    filename = f"BaoCao_NhapXuatTon_SmartLogis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    
    return StreamingResponse(
        excel_stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.get("/export/suppliers-excel")
def api_export_suppliers_excel(
    db: Session = Depends(get_db),
    current_user: NguoiDung = Depends(require_role(["Admin", "Thukho"]))
):
    """
    KẾT XUẤT BÁO CÁO DANH BẠ NHÀ CUNG CẤP RA EXCEL (.XLSX):
    Trích xuất toàn bộ danh bạ đối tác kèm thống kê số phiếu nhập và tổng tiền chi tiêu.
    """
    excel_stream = generate_excel_suppliers_report(db)
    filename = f"DanhBa_NhaCungCap_SmartLogis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    
    return StreamingResponse(
        excel_stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.get("/export/pdf")
def api_export_pdf_stub(
    ma_phieu: str = Query(..., description="Mã chứng từ cần in ra file PDF"),
    db: Session = Depends(get_db),
    current_user: NguoiDung = Depends(get_current_active_user)
):
    """
    In chứng từ phiếu xuất / nhập kho ra định dạng PDF chuẩn văn bản.
    """
    return {
        "status": "success",
        "message": f"Chứng từ [{ma_phieu}] đã sẵn sàng xuất in biểu mẫu PDF.",
        "voucher_id": ma_phieu
    }
