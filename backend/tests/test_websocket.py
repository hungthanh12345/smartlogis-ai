# tests/test_websocket.py
"""
Unit & Integration tests for Realtime WebSocket Manager & Event Broadcasting
"""
import uuid
import pytest
from fastapi.testclient import TestClient
from main import app
from app.core.websocket_manager import ws_manager

client = TestClient(app)

def get_auth_token(username: str = "admin", password: str = "admin123") -> str:
    res = client.post("/api/v1/auth/login", json={"TenDangNhap": username, "MatKhau": password})
    assert res.status_code == 200
    return res.json()["access_token"]

def test_websocket_connect_and_ping():
    """Kiểm tra kết nối WebSocket và phản hồi PING / PONG heartbeat."""
    with client.websocket_connect("/ws/inventory") as websocket:
        # 1. Nhận tin nhắn chào mừng
        welcome_data = websocket.receive_json()
        assert welcome_data["type"] == "CONNECTION_ESTABLISHED"
        assert "active_clients" in welcome_data

        # 2. Gửi PING dạng JSON
        websocket.send_json({"type": "PING"})
        pong_data = websocket.receive_json()
        assert pong_data["type"] == "PONG"

        # 3. Gửi ping dạng text
        websocket.send_text("ping")
        pong_text_data = websocket.receive_json()
        assert pong_text_data["type"] == "PONG"

def test_websocket_broadcast_event():
    """Kiểm tra cơ chế phát sóng sự kiện INVENTORY_UPDATED tới các thiết bị đang kết nối."""
    with client.websocket_connect("/ws/inventory") as websocket:
        # Bỏ qua welcome message
        welcome = websocket.receive_json()
        assert welcome["type"] == "CONNECTION_ESTABLISHED"

        # Giả lập phát sự kiện Nhập/Xuất kho từ backend
        test_payload = {
            "type": "INVENTORY_UPDATED",
            "action": "INBOUND",
            "message": "Kiểm thử phát sóng realtime: Đã nhập 50 sản phẩm",
            "details": {"ma_sp": "TEST-SKU", "so_luong": 50}
        }
        
        # Gọi broadcast_sync
        ws_manager.broadcast_sync(test_payload)

        # Client nhận được dữ liệu thời gian thực
        received = websocket.receive_json()
        assert received["type"] == "INVENTORY_UPDATED"
        assert received["action"] == "INBOUND"
        assert "TEST-SKU" in received["details"]["ma_sp"]

def test_inbound_api_triggers_realtime_broadcast():
    """Kiểm tra luồng E2E: Khi thực hiện API Nhập kho, sự kiện INVENTORY_UPDATED được broadcast tức thì."""
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Tạo trước 1 SKU thử nghiệm
    test_sku = f"HH-WS-{uuid.uuid4().hex[:6].upper()}"
    sku_res = client.post(
        "/api/v1/kho/items",
        json={
            "MaHH": test_sku,
            "TenHH": "Mặt hàng kiểm thử WebSocket Realtime",
            "MaNhom": "NH-THEP",
            "MaDVT": "Bao",
            "TonToiThieu": 5,
            "SoLuongBanDau": 10,
            "MoTa": "WebSocket Test"
        },
        headers=headers
    )
    assert sku_res.status_code == 201

    with client.websocket_connect("/ws/inventory") as websocket:
        # Nhận tin chào mừng
        welcome = websocket.receive_json()
        assert welcome["type"] == "CONNECTION_ESTABLISHED"

        # Thực hiện gọi API Nhập kho
        inbound_res = client.post(
            "/api/v1/kho/phieu-nhap",
            json={
                "MaNCC": "NCC-01",
                "GhiChu": "Kiểm thử Realtime Inbound Event",
                "items": [
                    {"MaHH": test_sku, "SoLuongNhap": 25, "DonGiaNhap": 150000}
                ]
            },
            headers=headers
        )
        assert inbound_res.status_code == 201

        # Lắng nghe WebSocket: Phải nhận được tín hiệu INVENTORY_UPDATED với action INBOUND
        event = websocket.receive_json()
        assert event["type"] == "INVENTORY_UPDATED"
        assert event["action"] == "INBOUND"
        assert "ma_chung_tu" in event
        assert event["item_count"] == 1

if __name__ == "__main__":
    pytest.main(["-v", "tests/test_websocket.py"])
