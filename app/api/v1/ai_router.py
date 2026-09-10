# app/api/v1/ai_router.py
"""
AI Router - Cung cấp các API Endpoints cho Trợ Lý Trí Tuệ Nhân Tạo (SmartLogis AI)
1. GET /api/v1/ai/advisory: Trả về khuyến nghị nhanh cho Dashboard Widget.
2. POST /api/v1/ai/generate-report: Sinh báo cáo phân tích vận hành kho toàn diện 3 phần từ Gemini LLM.
3. GET /api/v1/ai/raw-context: Trích xuất context dữ liệu 30 ngày đã lọc bỏ giá nhập phục vụ kiểm toán bảo mật.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.schemas.inventory_schemas import AIAdvisoryResponse, AIReportResponse
from app.services.ai_service import (
    generate_ai_inventory_advisory,
    generate_full_ai_report,
    aggregate_warehouse_data_30d
)

router = APIRouter(prefix="/ai", tags=["Trợ Lý AI Gemini (Advisory & Reports)"])


@router.get("/advisory", response_model=AIAdvisoryResponse)
def api_get_ai_advisory(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Lấy khuyến nghị phân tích kho thời gian thực từ Trợ lý AI (Grounded Prompting / Gemini LLM).
    Hiển thị trực tiếp lên Widget Dashboard.
    """
    return generate_ai_inventory_advisory(db)


@router.post("/generate-report", response_model=AIReportResponse)
def api_generate_ai_report(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    [GIAI ĐOẠN 3] Sinh Báo Cáo Phân Tích Điều Hành Kho Toàn Diện từ Google Gemini LLM:
    Quy trình:
    1. Trích xuất số liệu vận hành kho 30 ngày (Tồn thực tế vs Min, Tốc độ xuất Burn-rate, Tồn lâu > 60 ngày).
    2. Đi qua bộ lọc Data Sanitizer khử bỏ 100% thông tin giá vốn (DonGiaNhap, ThanhTien).
    3. Nạp vào Grounded Prompt Template có System Instruction chống ảo giác nghiêm ngặt.
    4. Gửi tới Gemini API (kèm cơ chế Retry, Rate Limit Handling & Fallback tự động).
    5. Trả về cấu trúc chuẩn 3 phần (Tổng quan, Đề xuất nhập khẩn cấp, Biến động bất thường).
    """
    try:
        report = generate_full_ai_report(db)
        return report
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi khởi tạo báo cáo phân tích AI: {str(e)}"
        )


@router.get("/raw-context")
def api_get_ai_raw_context(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    [AUDIT & KIỂM TOÁN DỮ LIỆU]
    Xem toàn bộ dữ liệu Context được nạp cho AI trước khi gửi qua API.
    Minh chứng bảo mật: Không có bất kỳ trường DonGiaNhap hoặc giá vốn nào xuất hiện trong payload.
    """
    sanitized_data = aggregate_warehouse_data_30d(db)
    return {
        "status": "success",
        "security_audit": "100% Sanitized (No financial cost fields included)",
        "context": sanitized_data
    }


# Giữ route cũ để tương thích ngược
@router.post("/generate-monthly-report")
def api_generate_monthly_report_legacy(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Endpoint tương thích ngược chuyển hướng sang generate-report."""
    return generate_full_ai_report(db)
