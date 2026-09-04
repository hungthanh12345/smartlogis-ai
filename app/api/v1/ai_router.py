# app/api/v1/ai_router.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.inventory_schemas import AIAdvisoryResponse
from app.services.ai_service import generate_ai_inventory_advisory, sanitize_inventory_data_for_ai

router = APIRouter(prefix="/ai", tags=["Tr? L? AI Gemini (Advisory & Sanitizer)"])

@router.get("/advisory", response_model=AIAdvisoryResponse)
def api_get_ai_advisory(db: Session = Depends(get_db)):
    """L?y khuy?n ngh? ph?n t?ch kho t? Tr? l? AI (Grounded Prompting)."""
    return generate_ai_inventory_advisory(db)

@router.post("/generate-monthly-report")
def api_generate_monthly_report_stub(db: Session = Depends(get_db)):
    """
    [STUB - S?N S?NG CHO GIAI ?O?N 2 & 3]
    TODO: T?ch h?p Google Gemini API (gemini-1.5-flash / Interactions API)
    Quy tr?nh:
    1. Tr?ch xu?t d? li?u t?ng h?p Nh?p - Xu?t - T?n th?ng t? CSDL.
    2. ?i qua h?m sanitize_inventory_data_for_ai() ?? lo?i b? gi? v?n DonGiaNhap.
    3. ??ng g?i v?o Grounded Prompt Template c? System Instruction ?p AI b?m s?t d? li?u th?t.
    4. G?i Gemini API v? tr? v? k?t qu? t?m t?t ph?n t?ch chi?n l??c.
    """
    advisory = generate_ai_inventory_advisory(db)
    return {
        "status": "success",
        "technique": "Grounded Prompting with Sanitized Input",
        "report_summary": advisory["raw_summary"],
        "insights": advisory["insights"]
    }
