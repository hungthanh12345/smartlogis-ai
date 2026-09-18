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
    assert "TỒN" in reply or "60 ngày" in reply or "luân chuyển" in reply

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
