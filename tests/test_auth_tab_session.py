# tests/test_auth_tab_session.py - Verification for Unauthenticated Redirects and Tab Session Isolation
import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from fastapi.testclient import TestClient
from main import app
from app.core.security import create_access_token
from app.core.session_manager import session_manager

client = TestClient(app)

def test_1_unauthenticated_web_routes_redirect_to_login_302():
    """Tất cả các trang Quản lý Kho khi chưa đăng nhập phải bắt buộc chuyển hướng 302 về /login và có Anti-Cache."""
    protected_routes = [
        "/dashboard",
        "/hang-hoa",
        "/nha-cung-cap",
        "/inbound",
        "/outbound",
        "/the-kho",
        "/register"
    ]

    for route in protected_routes:
        res = client.get(route, follow_redirects=False)
        assert res.status_code == 302, f"Route {route} expected 302, got {res.status_code}"
        assert res.headers.get("location") == "/login", f"Route {route} expected location /login, got {res.headers.get('location')}"
        assert "no-store" in res.headers.get("Cache-Control", ""), f"Route {route} missing no-store in Cache-Control"

    print("[PASS] 1a. All unauthenticated web routes strictly redirect to /login with 302 and Anti-Cache headers")

    # Trang chủ / khi truy cập lần đầu hiển thị Landing page toàn màn hình (200 OK)
    res_root = client.get("/", follow_redirects=False)
    assert res_root.status_code == 200, f"Expected 200 for landing page, got {res_root.status_code}"
    assert "btnTopRightLogin" in res_root.text
    assert "Log In" in res_root.text
    print("[PASS] 1b. Initial load / displays full-screen landing page with top-right Log In button")


def test_2_authenticated_web_route_succeeds_with_anti_cache():
    """Người dùng có cookie hợp lệ truy cập thành công và vẫn có Anti-Cache headers."""
    sid = session_manager.register_session("admin")
    token = create_access_token({"sub": "admin", "vaitro": "Admin", "hoten": "Quản Trị Viên", "sid": sid})
    
    res = client.get("/dashboard", cookies={"access_token": f"Bearer {token}"}, follow_redirects=False)
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    assert "no-store" in res.headers.get("Cache-Control", "")
    assert "Quản Trị Viên" in res.text
    print("[PASS] 2. Authenticated user accesses dashboard with 200 and anti-cache headers")


def test_3_tab_isolation_cross_account_blocked():
    """
    Fix lỗi 2 tài khoản/2 tab:
    Tab 1 mở tài khoản thukho (header X-Session-User: thukho).
    Nếu cookie bị ghi đè bởi tài khoản Admin (token của admin),
    Server PHẢI chặn đứng với mã 401 Unauthorized, không cho phép mượn quyền Admin!
    """
    admin_sid = session_manager.register_session("admin")
    admin_token = create_access_token({"sub": "admin", "vaitro": "Admin", "hoten": "Quản Trị Viên", "sid": admin_sid})

    # A. Gọi API đúng tài khoản tab: X-Session-User: admin khớp với token admin -> 200 OK
    res_correct = client.get(
        "/api/v1/kho/items",
        cookies={"access_token": f"Bearer {admin_token}"},
        headers={"X-Session-User": "admin"}
    )
    assert res_correct.status_code == 200, f"Expected 200, got {res_correct.status_code}"

    # B. Gọi API từ Tab 1 (vốn thuộc về thukho) nhưng trình duyệt gửi kèm cookie admin:
    # Header X-Session-User: thukho KHÁC sub: admin trong token -> Server chặn ngay lập tức (401)
    res_mismatch = client.get(
        "/api/v1/kho/items",
        cookies={"access_token": f"Bearer {admin_token}"},
        headers={"X-Session-User": "thukho"}
    )
    assert res_mismatch.status_code == 401, f"Expected 401 Unauthorized for mismatched tab user, got {res_mismatch.status_code}"
    data = res_mismatch.json()
    assert "Xung đột phiên làm việc" in data.get("detail", "")
    print("[PASS] 3. Tab isolation strictly blocks cross-account privilege borrowing with 401 Unauthorized")


def test_4_multi_tab_concurrent_sessions_for_same_account():
    """
    Khi cùng một tài khoản mở nhiều tab (phiên làm việc) khác nhau:
    Cả 2 phiên (sid1 và sid2) đều hoạt động đồng thời bình thường, không bị đá ra.
    """
    sid1 = session_manager.register_session("thukho")
    token1 = create_access_token({"sub": "thukho", "vaitro": "Thukho", "sid": sid1})

    # Thao tác với tab 1 -> Thành công
    res1 = client.get("/api/v1/kho/items", cookies={"access_token": f"Bearer {token1}"})
    assert res1.status_code == 200

    # Tab 2 mở phiên mới -> sid2
    sid2 = session_manager.register_session("thukho")
    token2 = create_access_token({"sub": "thukho", "vaitro": "Thukho", "sid": sid2})

    # Thao tác với tab 1 -> Vẫn tiếp tục hoạt động thành công (200 OK)
    res_tab1 = client.get("/api/v1/kho/items", cookies={"access_token": f"Bearer {token1}"})
    assert res_tab1.status_code == 200, f"Expected 200 for tab 1, got {res_tab1.status_code}"

    # Thao tác với tab 2 -> Thành công (200 OK)
    res_tab2 = client.get("/api/v1/kho/items", cookies={"access_token": f"Bearer {token2}"})
    assert res_tab2.status_code == 200, f"Expected 200 for tab 2, got {res_tab2.status_code}"
    print("[PASS] 4. Multi-tab concurrent sessions work: both tabs active simultaneously")


def test_5_logout_invalidates_session_and_clears_cookies():
    """Đăng xuất vô hiệu hóa session trong SessionManager và xóa cookie."""
    sid = session_manager.register_session("admin")
    token = create_access_token({"sub": "admin", "vaitro": "Admin", "sid": sid})

    res_logout = client.get("/logout", cookies={"access_token": f"Bearer {token}"}, follow_redirects=False)
    assert res_logout.status_code == 302
    assert res_logout.headers.get("location") == "/login"

    # Kiểm tra session_manager đã vô hiệu hóa session
    assert not session_manager.is_session_valid("admin", sid)

    # Request tiếp theo với token cũ sẽ bị từ chối
    res_after = client.get("/dashboard", cookies={"access_token": f"Bearer {token}"}, follow_redirects=False)
    assert res_after.status_code == 302
    assert res_after.headers.get("location") == "/login"
    print("[PASS] 5. Logout properly invalidates session and clears credentials")


def test_6_admin_broadcast_channel_rendered_only_for_admin():
    """Kiểm tra đoạn mã BroadcastChannel API khóa 2 tab Admin được render chuẩn xác cho vai trò Admin."""
    sid_admin = session_manager.register_session("admin")
    admin_token = create_access_token({"sub": "admin", "vaitro": "Admin", "hoten": "Quản Trị Viên", "sid": sid_admin})

    res_admin = client.get("/dashboard", cookies={"access_token": f"Bearer {admin_token}"})
    assert res_admin.status_code == 200
    assert "smartlogis_admin_tab_channel" in res_admin.text
    assert "NEW_ADMIN_TAB_ACTIVE" in res_admin.text
    assert "BroadcastChannel" in res_admin.text

    # Thủ kho không bị chặn mở nhiều tab -> Không chèn BroadcastChannel lock
    sid_thukho = session_manager.register_session("thukho")
    thukho_token = create_access_token({"sub": "thukho", "vaitro": "Thukho", "hoten": "Thủ Kho", "sid": sid_thukho})

    res_thukho = client.get("/dashboard", cookies={"access_token": f"Bearer {thukho_token}"})
    assert res_thukho.status_code == 200
    assert "smartlogis_admin_tab_channel" not in res_thukho.text
    print("[PASS] 6. BroadcastChannel single-tab lock rendered specifically for Admin role")


def test_7_admin_strict_single_active_session():
    """Kiểm tra tài khoản Admin bị giới hạn nghiêm ngặt 1 session: Phiên cũ bị hủy khi mở phiên mới."""
    # Phiên 1 của Admin
    sid1 = session_manager.register_session("admin")
    token1 = create_access_token({"sub": "admin", "vaitro": "Admin", "sid": sid1})

    res1 = client.get("/api/v1/kho/items", cookies={"access_token": f"Bearer {token1}"})
    assert res1.status_code == 200

    # Phiên 2 của Admin đăng nhập/mở mới -> sid1 của Admin lập tức bị vô hiệu hóa
    sid2 = session_manager.register_session("admin")
    token2 = create_access_token({"sub": "admin", "vaitro": "Admin", "sid": sid2})

    # Request mang sid cũ của Admin bị từ chối 401
    res_old = client.get("/api/v1/kho/items", cookies={"access_token": f"Bearer {token1}"})
    assert res_old.status_code == 401, f"Expected 401 for invalidated older admin session, got {res_old.status_code}"

    # Request mang sid mới của Admin thành công 200
    res_new = client.get("/api/v1/kho/items", cookies={"access_token": f"Bearer {token2}"})
    assert res_new.status_code == 200
    print("[PASS] 7. Strict single active session for Admin strictly enforced: older session rejected with 401")
