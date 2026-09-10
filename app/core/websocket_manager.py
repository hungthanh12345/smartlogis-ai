# app/core/websocket_manager.py
"""
WebSocket Connection & Realtime Broadcast Manager (SmartLogis AI)
Chịu trách nhiệm:
1. Duy trì danh sách kết nối WebSocket đồng thời từ nhiều thiết bị (PC, Laptop, Mobile).
2. Phát tín hiệu thời gian thực (Broadcast) ngay khi phát sinh giao dịch Nhập/Xuất kho hoặc thay đổi SKU.
3. Cung cấp cả giao thức async và helper sync cho tầng nghiệp vụ.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import List, Dict, Any
from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger("smartlogis.websocket")


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket):
        """Chấp nhận kết nối từ Client mới và lưu vết."""
        await websocket.accept()
        async with self._lock:
            self.active_connections.append(websocket)
        
        client_count = len(self.active_connections)
        logger.info(f"[WebSocket] Thiết bị mới kết nối thành công. Tổng số thiết bị online: {client_count}")
        
        # Gửi thông điệp chào mừng và thông số ban đầu cho thiết bị vừa kết nối
        await websocket.send_json({
            "type": "CONNECTION_ESTABLISHED",
            "message": "Kết nối máy chủ thời gian thực SmartLogis AI thành công.",
            "active_clients": client_count,
            "timestamp": datetime.now().isoformat()
        })

    async def disconnect(self, websocket: WebSocket):
        """Gỡ bỏ kết nối khi client đóng trình duyệt hoặc mất mạng."""
        async with self._lock:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)
        logger.info(f"[WebSocket] Một thiết bị đã ngắt kết nối. Còn lại: {len(self.active_connections)}")

    async def broadcast(self, message: Dict[str, Any]):
        """
        Phát sóng thông điệp Realtime tới TOÀN BỘ các thiết bị đang mở hệ thống.
        Tự động dọn dẹp các kết nối bị lỗi hoặc ngắt đột ngột.
        """
        if not message.get("timestamp"):
            message["timestamp"] = datetime.now().strftime("%H:%M:%S")

        disconnected_clients = []
        
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning(f"[WebSocket] Lỗi khi gửi tin nhắn tới client: {e}")
                disconnected_clients.append(connection)

        # Dọn dẹp các kết nối chết
        if disconnected_clients:
            async with self._lock:
                for dead_conn in disconnected_clients:
                    if dead_conn in self.active_connections:
                        self.active_connections.remove(dead_conn)

    def broadcast_sync(self, message: Dict[str, Any]):
        """
        Helper cho phép phát sóng an toàn từ các hàm đồng bộ (Synchronous Service Functions).
        """
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self.broadcast(message))
        except RuntimeError:
            try:
                asyncio.run(self.broadcast(message))
            except Exception as e:
                logger.error(f"[WebSocket] Lỗi broadcast_sync: {e}")


# Singleton instance toàn hệ thống
ws_manager = ConnectionManager()
