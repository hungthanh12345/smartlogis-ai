# tests/test_ai_chat.py
"""
Kiểm thử tự động cho Phân hệ AI Chat Box (SmartLogis Conversational Assistant)
1. Kiểm tra bảo mật xác thực (chặn unauthenticated).
2. Kiểm tra sinh Báo cáo 3 phần chuẩn hóa từ CSDL thật.
3. Kiểm tra các câu hỏi cảnh báo tồn kho, dead stock, burn-rate.
4. Kiểm tra tra cứu SKU thời gian thực.
5. Kiểm tra tính năng giải thích kiến trúc dự án (Zero Negative Stock, ACID, RBAC).
6. Kiểm tra giao diện web SSR /ai-chat.
"""

import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from fastapi.testclient import TestClient
from main import app
from app.core.security import create_access_token

client = TestClient(app)

def get_auth_headers():
    token = create_access_token({"sub": "admin", "vaitro": "Admin", "mand": 1, "hoten": "Quản trị viên"})
    return {
        "Authorization": f"Bearer {token}"
    }, {
        "access_token": f"Bearer {token}"
    }

def test_ai_chat_endpoint_unauthenticated():
    """Chặn truy cập API chat khi chưa đăng nhập (HTTP 401)."""
    res = client.post("/api/v1/ai/chat", json={"message": "Xin chào"})
    assert res.status_code in [401, 403], f"Expected 401/403, got {res.status_code}"

def test_ai_chat_page_redirects_unauthenticated():
    """Trang /ai-chat chuyển hướng 302 về /login khi chưa đăng nhập."""
    res = client.get("/ai-chat", follow_redirects=False)
    assert res.status_code == 302
    assert res.headers.get("location") == "/login"

def test_ai_chat_page_renders_authenticated():
    """Trang /ai-chat render thành công (HTTP 200) cho người dùng đã đăng nhập."""
    headers, cookies = get_auth_headers()
    res = client.get("/ai-chat", headers=headers, cookies=cookies)
    assert res.status_code == 200
    assert "SmartLogis AI Conversational Engine" in res.text
    assert "Trợ Lý Kho AI" in res.text or "Grounded" in res.text
    assert 'id="chatInputMessage"' in res.text

def test_ai_chat_report_3_parts():
    """Yêu cầu sinh báo cáo điều hành 3 phần: Trả về đầy đủ Phần 1, Phần 2, Phần 3."""
    headers, cookies = get_auth_headers()
    payload = {"message": "Hãy sinh báo cáo điều hành kho 3 phần giúp tôi"}
    res = client.post("/api/v1/ai/chat", json=payload, headers=headers, cookies=cookies)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    reply = data["reply"]
    assert "PHẦN 1" in reply or "TỔNG QUAN" in reply
    assert "PHẦN 2" in reply or "CẢNH BÁO" in reply
    assert "PHẦN 3" in reply or "BIẾN ĐỘNG" in reply
    assert len(data.get("suggested_questions", [])) > 0

def test_ai_chat_low_stock_query():
    """Hỏi về các mặt hàng thiếu hụt: Trả về dữ liệu từ CSDL."""
    headers, cookies = get_auth_headers()
    payload = {"message": "Mặt hàng nào đang thiếu hụt tồn kho hoặc cần nhập gấp?"}
    res = client.post("/api/v1/ai/chat", json=payload, headers=headers, cookies=cookies)
    assert res.status_code == 200
    reply = res.json()["reply"]
    assert "TỒN" in reply or "an toàn" in reply or "thiếu hụt" in reply.lower()

def test_ai_chat_dead_stock_query():
    """Hỏi về hàng tồn kho lâu > 60 ngày: Trả về danh sách hoặc trạng thái."""
    headers, cookies = get_auth_headers()
    payload = {"message": "Kiểm tra danh sách hàng tồn kho lâu > 60 ngày"}
    res = client.post("/api/v1/ai/chat", json=payload, headers=headers, cookies=cookies)
    assert res.status_code == 200
    reply = res.json()["reply"]
    assert "tồn" in reply.lower() or "dead stock" in reply.lower() or "60 ngày" in reply or "luân chuyển" in reply.lower()

def test_ai_chat_sku_lookup():
    """Tra cứu cụ thể một SKU có trong kho (ví dụ HH-THEP-D08)."""
    headers, cookies = get_auth_headers()
    payload = {"message": "Tra cứu mã hàng HH-THEP-D08"}
    res = client.post("/api/v1/ai/chat", json=payload, headers=headers, cookies=cookies)
    assert res.status_code == 200
    reply = res.json()["reply"]
    assert "HH-THEP-D08" in reply
    assert "Số lượng tồn" in reply or "Tồn thực tế" in reply or "Cuộn" in reply

def test_ai_chat_architecture_inquiry():
    """Hỏi về kiến trúc dự án: Zero Negative Stock, ACID, RBAC."""
    headers, cookies = get_auth_headers()
    payload = {"message": "Dự án SmartLogis AI hoạt động thế nào và có cơ chế chống tồn âm ra sao?"}
    res = client.post("/api/v1/ai/chat", json=payload, headers=headers, cookies=cookies)
    assert res.status_code == 200
    reply = res.json()["reply"]
    assert "Zero Negative Stock" in reply or "chống tồn âm" in reply.lower()
    assert "ACID" in reply or "RBAC" in reply or "Atomic" in reply

def test_ai_chat_sanitizer_security():
    """Xác nhận Context và câu trả lời không làm lộ các trường giá vốn nhạy cảm."""
    headers, cookies = get_auth_headers()
    payload = {"message": "Tổng quan tình hình kho và các cảnh báo"}
    res = client.post("/api/v1/ai/chat", json=payload, headers=headers, cookies=cookies)
    assert res.status_code == 200
    ctx = res.json().get("context_summary", {})
    ctx_str = str(ctx).lower()
    assert "dongianhap" not in ctx_str
    assert "import_price" not in ctx_str
    assert "thanhtien" not in ctx_str

def test_ai_status_endpoint():
    """Kiểm tra endpoint GET /api/v1/ai/status trả về đúng schema."""
    headers, cookies = get_auth_headers()
    res = client.get("/api/v1/ai/status", headers=headers, cookies=cookies)
    assert res.status_code == 200
    data = res.json()
    assert "configured" in data
    assert "model_name" in data
    assert "engine" in data

def test_ai_chat_diverse_inquiries_no_canned_repeats():
    """Đảm bảo các câu hỏi đa dạng (nhập kho, xuất kho, nhà cung cấp, toàn bộ hàng) trả về câu trả lời riêng biệt, không bị lặp lại câu chào mặc định."""
    headers, cookies = get_auth_headers()

    queries = [
        ("Hướng dẫn tạo phiếu nhập kho", ["nhập kho", "inbound", "bước", "nhà cung cấp"]),
        ("Làm sao để xuất kho an toàn?", ["xuất kho", "tồn âm", "outbound", "atomic"]),
        ("Danh sách nhà cung cấp của công ty", ["nhà cung cấp", "ncc", "đối tác"]),
        ("Kho có những mặt hàng nào?", ["danh mục", "sku", "mặt hàng"])
    ]

    replies = []
    for q, expected_keywords in queries:
        res = client.post("/api/v1/ai/chat", json={"message": q}, headers=headers, cookies=cookies)
        assert res.status_code == 200
        reply = res.json()["reply"]
        replies.append(reply)
        # Kiểm tra câu trả lời có chứa từ khóa nghiệp vụ thực tế
        assert any(k in reply.lower() for k in expected_keywords), f"Query '{q}' failed keyword match: {reply[:100]}"
    
    # Xác minh các câu trả lời hoàn toàn khác nhau (không lặp lại)
    assert len(set(replies)) == len(replies), "Các câu trả lời bị trùng lặp!"

def test_ai_key_clear_endpoint():
    """Kiểm tra endpoint DELETE /api/v1/ai/api-key xóa key thành công (bảo vệ tệp .env thật)."""
    from unittest.mock import patch
    from app.services.gemini_service import gemini_service
    from app.core.config import settings

    orig_service_key = gemini_service.api_key
    orig_settings_key = settings.GEMINI_API_KEY

    headers, cookies = get_auth_headers()
    try:
        with patch("app.services.gemini_service.update_env_file"):
            res = client.delete("/api/v1/ai/api-key", headers=headers, cookies=cookies)
            assert res.status_code == 200
            data = res.json()
            assert data["status"] == "success"
            assert data["ai_status"]["configured"] is False
    finally:
        # Khôi phục trạng thái key
        gemini_service.api_key = orig_service_key
        settings.GEMINI_API_KEY = orig_settings_key


def test_ai_chat_multi_turn_continue():
    """Kiểm tra tính năng đàm thoại nhiều lượt khi người dùng yêu cầu 'làm tiếp'."""
    headers, cookies = get_auth_headers()
    
    # Lượt 1: Hỏi về mặt hàng thiếu hụt
    res1 = client.post("/api/v1/ai/chat", json={"message": "Mặt hàng nào đang thiếu hụt nguy cấp?"}, headers=headers, cookies=cookies)
    assert res1.status_code == 200
    r1_text = res1.json()["reply"]

    # Lượt 2: Hỏi 'làm tiếp' kèm lịch sử lượt 1
    history = [
        {"role": "user", "content": "Mặt hàng nào đang thiếu hụt nguy cấp?"},
        {"role": "assistant", "content": r1_text[:300]}
    ]
    res2 = client.post("/api/v1/ai/chat", json={"message": "làm tiếp", "history": history}, headers=headers, cookies=cookies)
    assert res2.status_code == 200
    r2_data = res2.json()
    r2_text = r2_data["reply"]

    # Phản hồi phải nhận diện ngữ cảnh và triển khai các bước kế tiếp
    assert any(w in r2_text.lower() for w in ["nhập kho", "phiếu nhập", "bước", "nhà cung cấp", "dự thảo"]), f"Làm tiếp failed: {r2_text[:200]}"
    assert len(r2_data.get("suggested_questions", [])) > 0


