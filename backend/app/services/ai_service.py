# app/services/ai_service.py
"""
AI Service Facade - Giao diện thống nhất cho các nghiệp vụ Trí tuệ Nhân tạo trong SmartLogis AI
Kết hợp:
1. Data Sanitizer & Aggregator (ai_data_service)
2. Prompt Engineering (inventory_prompts)
3. Gemini LLM Connector & Local Grounded Fallback Engine (gemini_service)
"""

from typing import List, Dict, Any
from sqlalchemy.orm import Session

from app.services.ai_data_service import aggregate_warehouse_data_30d, sanitize_inventory_payload
from app.services.gemini_service import gemini_service


def sanitize_inventory_data_for_ai(raw_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Module Data Sanitizer (Tương thích ngược):
    Loại bỏ 100% thông tin đơn giá nhập nhạy cảm (DonGiaNhap, ThanhTien, GiaVon)
    trước khi dữ liệu được gửi đến mô hình Gemini LLM để bảo vệ bí mật kinh doanh.
    """
    return sanitize_inventory_payload(raw_records)


def generate_ai_inventory_advisory(db: Session) -> dict:
    """
    Trợ lý AI Gemini Advisory (Phục vụ Widget Dashboard):
    1. Tổng hợp số liệu kho 30 ngày và loại bỏ giá nhập.
    2. Gửi dữ liệu tới GeminiService (kèm cơ chế Retry & Fallback).
    3. Định dạng kết quả tương thích hoàn hảo với giao diện Dashboard.
    """
    # 1. Trích xuất và làm sạch dữ liệu kho 30 ngày
    warehouse_data = aggregate_warehouse_data_30d(db)

    # 2. Sinh báo cáo phân tích
    report = gemini_service.generate_inventory_report(warehouse_data, output_format="json")

    insights = report.get("insights_widget", [])
    model_name = report.get("model_used", "SmartLogis Grounded Analytical Engine")
    is_fallback = report.get("is_fallback", False)
    meta = warehouse_data.get("metadata", {})

    summary_text = (
        f"Phân tích từ {meta.get('total_skus', 0)} SKU, "
        f"phát hiện {meta.get('low_stock_sku_count', 0)} mặt hàng chạm tồn min "
        f"và {meta.get('dead_stock_sku_count', 0)} mặt hàng đọng > 60 ngày."
    )

    return {
        "model_name": model_name,
        "prompt_technique": "Grounded Prompting with Strict Anti-Hallucination",
        "insights": insights,
        "raw_summary": summary_text,
        "is_fallback": is_fallback,
        "markdown_report": report.get("markdown_report", ""),
        "structured_report": {
            "phan_1_tong_quan": report.get("phan_1_tong_quan", {}),
            "phan_2_canh_bao_va_de_xuat_nhap": report.get("phan_2_canh_bao_va_de_xuat_nhap", []),
            "phan_3_bien_dong_bat_thuong": report.get("phan_3_bien_dong_bat_thuong", {})
        }
    }


def generate_full_ai_report(db: Session) -> dict:
    """
    Sinh báo cáo phân tích kho toàn diện phục vụ API POST /api/v1/ai/generate-report.
    Đầu ra tuân thủ chuẩn 3 phần theo yêu cầu Giai đoạn 3:
    - Phần 1: Tình trạng tồn kho tổng quan.
    - Phần 2: Cảnh báo & Gợi ý nhập hàng khẩn cấp.
    - Phần 3: Tóm tắt biến động bất thường (xuất tăng đột biến hoặc hàng tồn lâu > 60 ngày).
    """
    warehouse_data = aggregate_warehouse_data_30d(db)
    report = gemini_service.generate_inventory_report(warehouse_data, output_format="json")

    return {
        "status": "success",
        "model_used": report.get("model_used", "SmartLogis AI"),
        "is_fallback": report.get("is_fallback", False),
        "fallback_reason": report.get("fallback_reason"),
        "data_context_summary": warehouse_data.get("metadata", {}),
        "phan_1_tong_quan": report.get("phan_1_tong_quan", {}),
        "phan_2_canh_bao_va_de_xuat_nhap": report.get("phan_2_canh_bao_va_de_xuat_nhap", []),
        "phan_3_bien_dong_bat_thuong": report.get("phan_3_bien_dong_bat_thuong", {}),
        "insights_widget": report.get("insights_widget", []),
        "markdown_report": report.get("markdown_report", "")
    }
