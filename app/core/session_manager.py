# app/core/session_manager.py
"""
Quản lý phiên đăng nhập tập trung (Multi-Tab Concurrent Session & Tab Isolation)
- Hỗ trợ người dùng mở nhiều tab trên cùng một tài khoản mà không bị xung đột.
- Cho phép xác thực và vô hiệu hóa phiên theo từng session_id hoặc toàn bộ tài khoản khi đăng xuất.
"""
import uuid
from typing import Dict, Optional, Set
from fastapi import WebSocket

class SessionManager:
    def __init__(self):
        # username -> Set[session_id]
        self._user_sessions: Dict[str, Set[str]] = {}
        # username -> Set[WebSocket]
        self._user_websockets: Dict[str, Set[WebSocket]] = {}

    def register_session(self, username: str) -> str:
        """Đăng ký phiên đăng nhập mới cho user và trả về session_id (sid) duy nhất."""
        sid = uuid.uuid4().hex
        if username == "admin":
            # SIẾT CHẶT SINGLE ACTIVE SESSION CHO ADMIN:
            # Khi Admin đăng nhập/mở phiên mới, chỉ cho phép đúng 1 session duy nhất
            self._user_sessions[username] = {sid}
        else:
            if username not in self._user_sessions:
                self._user_sessions[username] = set()
            self._user_sessions[username].add(sid)
        return sid

    def get_active_sessions(self, username: str) -> Set[str]:
        return self._user_sessions.get(username, set())

    def is_session_valid(self, username: str, sid: Optional[str]) -> bool:
        """Kiểm tra session_id của request có hợp lệ không."""
        if not sid:
            # Token không có sid thì vẫn chấp nhận
            return True
        if username not in self._user_sessions:
            # Nếu chưa lưu trong cache thì khởi tạo và chấp nhận sid này
            self._user_sessions[username] = {sid}
            return True
        return sid in self._user_sessions[username]

    def invalidate_session(self, username: str, sid: Optional[str] = None):
        """Hủy phiên đăng nhập khi đăng xuất."""
        if sid and username in self._user_sessions:
            self._user_sessions[username].discard(sid)
        else:
            self._user_sessions[username] = set()

    def register_websocket(self, username: str, ws: WebSocket):
        if username not in self._user_websockets:
            self._user_websockets[username] = set()
        self._user_websockets[username].add(ws)

    def unregister_websocket(self, username: str, ws: WebSocket):
        if username in self._user_websockets:
            self._user_websockets[username].discard(ws)
            if not self._user_websockets[username]:
                del self._user_websockets[username]

    async def notify_force_logout(self, username: str, new_sid: str):
        """Không tự ý broadcast đá phiên các tab cùng tài khoản."""
        pass

    def notify_force_logout_sync(self, username: str, new_sid: str):
        """Không tự ý broadcast đá phiên các tab cùng tài khoản."""
        pass

session_manager = SessionManager()

