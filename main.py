# main.py - Điểm khởi chạy ứng dụng SmartLogis AI
import os
import json
from fastapi import FastAPI, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import Base, engine, get_db
from app.core.security import get_current_user_optional
from app.models.inventory_models import HangHoa, NhomHang, DonViTinh, NhaCungCap
from app.services.inventory_service import (
    get_dashboard_kpis, get_stock_alerts, get_all_hang_hoa, get_all_suppliers, get_supplier_kpis
)
from app.services.ai_service import generate_ai_inventory_advisory
from app.api.v1 import auth_router, inventory_router, reports_router, ai_router
from scripts.seed import seed_database

# Khởi tạo bảng CSDL và seed data nếu chưa có
Base.metadata.create_all(bind=engine)
try:
    from sqlalchemy import text
    with engine.connect() as _conn:
        _cols = [c[1] for c in _conn.execute(text("PRAGMA table_info(nha_cung_cap)")).fetchall()]
        if "TongTien" not in _cols:
            _conn.execute(text("ALTER TABLE nha_cung_cap ADD COLUMN TongTien FLOAT DEFAULT 0.0"))
            _conn.commit()
except Exception as _e:
    pass

seed_database()

# Chuẩn hóa và đồng bộ số dư Sổ Thẻ Kho & Tồn Kho khi khởi động máy chủ
try:
    from app.core.database import SessionLocal
    from app.services.inventory_service import recalculate_and_sync_the_kho
    _init_db = SessionLocal()
    recalculate_and_sync_the_kho(_init_db)
    _init_db.close()
except Exception as _e:
    print(f"[!] Warning on initial ledger sync: {_e}")

from fastapi.middleware.cors import CORSMiddleware
from fastapi import WebSocket, WebSocketDisconnect
from app.core.websocket_manager import ws_manager

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "Hệ thống Quản lý Kho Thông minh Tích hợp AI (Realtime Centralized Web Server) - "
        "FastAPI, WebSocket Multi-Device Sync, SQLite WAL / PostgreSQL ACID Transactions, "
        "Atomic SQL Decrement Chống Tồn Âm, Google Gemini LLM Advisory."
    ),
    docs_url="/docs",
    redoc_url="/redoc"
)

# Cấu hình CORS cho phép mọi thiết bị trong mạng LAN, Wi-Fi, Localhost và Domain kết nối
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^https?://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_anti_cache_headers(request: Request, call_next):
    """Bảo đảm trình duyệt luôn nhận số liệu tồn kho mới nhất, chống mất trạng thái hoặc hiển thị số dư cũ khi refresh."""
    response = await call_next(request)
    path = request.url.path
    if path.startswith("/api/v1/") or path in ["/outbound", "/inbound", "/the-kho", "/hang-hoa", "/dashboard"]:
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

# Gắn thư mục static và templates
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "app", "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "app", "templates"))

# Gắn các API Router v1
app.include_router(auth_router.router, prefix=settings.API_V1_STR)
app.include_router(inventory_router.router, prefix=settings.API_V1_STR)
app.include_router(reports_router.router, prefix=settings.API_V1_STR)
app.include_router(ai_router.router, prefix=settings.API_V1_STR)

# =============================================================================
# REALTIME WEBSOCKET ENDPOINTS (ĐỒNG BỘ ĐA THIẾT BỊ)
# =============================================================================

@app.websocket("/ws/inventory")
@app.websocket("/ws")
async def websocket_inventory_endpoint(websocket: WebSocket):
    """
    WebSocket Endpoint lắng nghe và duy trì kết nối Realtime từ các thiết bị:
    - Máy tính để bàn / Laptop của Thủ kho, Kế toán, Quản lý
    - Điện thoại di động / Máy tính bảng truy cập qua mạng WiFi/LAN
    """
    await ws_manager.connect(websocket)
    try:
        while True:
            raw_data = await websocket.receive_text()
            try:
                msg = json.loads(raw_data)
                msg_type = msg.get("type", "").upper() if isinstance(msg, dict) else ""
                if msg_type == "PING":
                    await websocket.send_json({"type": "PONG", "active_clients": len(ws_manager.active_connections)})
            except Exception:
                if raw_data.strip().lower() == "ping":
                    await websocket.send_json({"type": "PONG", "active_clients": len(ws_manager.active_connections)})
    except (WebSocketDisconnect, Exception):
        await ws_manager.disconnect(websocket)


# Middleware kiểm soát truy cập và chống Cache cho SSR Web UI
@app.middleware("http")
async def auth_enforce_middleware(request: Request, call_next):
    """
    Bắt buộc người dùng vào web chưa đăng nhập phải chuyển hướng về /login (HTTP 302).
    Đồng thời áp dụng Anti-Cache headers chống lưu bfcache trình duyệt.
    """
    path = request.url.path
    public_paths = [
        "/",
        "/login",
        "/logout",
        "/register",
        "/landing",
        "/about",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/favicon.ico"
    ]
    is_public = (
        path.startswith("/static")
        or path.startswith("/api")
        or path.startswith("/ws")
        or path in public_paths
    )

    if not is_public:
        token = request.cookies.get("access_token")
        if token and token.startswith("Bearer "):
            token = token[7:]

        valid_user = False
        if token:
            from app.core.security import decode_access_token
            from app.core.session_manager import session_manager
            payload = decode_access_token(token)
            if payload and payload.get("sub"):
                username = payload.get("sub")
                sid = payload.get("sid")
                if session_manager.is_session_valid(username, sid):
                    valid_user = True

        if not valid_user:
            redirect_res = RedirectResponse(url="/login", status_code=302)
            redirect_res.delete_cookie(key="access_token", path="/", httponly=True, samesite="lax")
            redirect_res.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            redirect_res.headers["Pragma"] = "no-cache"
            redirect_res.headers["Expires"] = "0"
            return redirect_res

    response = await call_next(request)

    # Áp dụng anti-cache cho mọi trang HTML Web UI SSR
    if not path.startswith("/static") and not path.startswith("/api"):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"

    return response

# =============================================================================
# WEB UI SSR ROUTES (GIAO DIỆN NGƯỜI DÙNG)
# =============================================================================

@app.get("/")
@app.get("/landing")
@app.get("/about")
def route_root_landing(request: Request, user = Depends(get_current_user_optional)):
    """Trang chủ root URL (/) cùng /landing, /about hiển thị giao diện Giới thiệu (landing.html)."""
    response = templates.TemplateResponse(
        request=request,
        name="landing.html",
        context={"request": request, "user": user}
    )
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return response

@app.post("/logout")
@app.get("/logout")
def route_logout(user = Depends(get_current_user_optional)):
    """Đăng xuất người dùng: Vô hiệu hóa session, xóa cookie và chuyển hướng về trang Đăng nhập."""
    if user:
        from app.core.session_manager import session_manager
        session_manager.invalidate_session(user.TenDangNhap)
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie(key="access_token", path="/", httponly=True, samesite="lax")
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return response

@app.get("/login")
def route_login(request: Request):
    """Màn hình Đăng nhập: Luôn hiển thị form đăng nhập, không tự động chuyển hướng để cho phép chọn/đổi tài khoản."""
    response = templates.TemplateResponse(request=request, name="login.html")
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return response

@app.get("/register")
def route_register():
    """Khóa đăng ký tự do — Hệ thống kho nội bộ chuyển hướng trực tiếp về trang đăng nhập."""
    return RedirectResponse(url="/login", status_code=302)

@app.get("/dashboard")
def route_dashboard(request: Request, db: Session = Depends(get_db), user = Depends(get_current_user_optional)):
    """Màn hình Dashboard Tổng quan v2.0 (Hình 4.6.1 Wireframe)."""
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    kpis = get_dashboard_kpis(db)
    alerts = get_stock_alerts(db)
    ai_advisory = generate_ai_inventory_advisory(db)

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "request": request,
            "active_page": "dashboard",
            "user": user,
            "kpis": kpis,
            "alerts": alerts,
            "ai_advisory": ai_advisory
        }
    )

@app.get("/hang-hoa")
def route_hang_hoa(request: Request, db: Session = Depends(get_db), user = Depends(get_current_user_optional)):
    """Màn hình Quản lý Danh mục Hàng hóa (CRUD SKU)."""
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    items = get_all_hang_hoa(db)
    categories = db.query(NhomHang).all()
    units = db.query(DonViTinh).all()

    return templates.TemplateResponse(
        request=request,
        name="items.html",
        context={
            "request": request,
            "active_page": "hang_hoa",
            "user": user,
            "items": items,
            "categories": categories,
            "units": units
        }
    )

@app.get("/nha-cung-cap")
@app.get("/suppliers")
def route_nha_cung_cap(request: Request, db: Session = Depends(get_db), user = Depends(get_current_user_optional)):
    """Màn hình Quản lý Nhà cung cấp (CRUD NCC & KPI, hỗ trợ cả /nha-cung-cap và /suppliers)."""
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    suppliers = get_all_suppliers(db)
    kpis = get_supplier_kpis(db)

    return templates.TemplateResponse(
        request=request,
        name="suppliers.html",
        context={
            "request": request,
            "active_page": "nha_cung_cap",
            "user": user,
            "suppliers": suppliers,
            "kpis": kpis
        }
    )

@app.get("/inbound")
def route_inbound(request: Request, db: Session = Depends(get_db), user = Depends(get_current_user_optional)):
    """Màn hình Lập Phiếu Nhập Kho (Hình 4.6.2 Wireframe)."""
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    if user.VaiTro not in ["Admin", "Thukho"]:
        return RedirectResponse(url="/dashboard?error=access_denied", status_code=302)

    suppliers = get_all_suppliers(db)

    return templates.TemplateResponse(
        request=request,
        name="inbound.html",
        context={
            "request": request,
            "active_page": "inbound",
            "user": user,
            "suppliers": suppliers
        }
    )

@app.get("/outbound")
def route_outbound(request: Request, db: Session = Depends(get_db), user = Depends(get_current_user_optional)):
    """Màn hình Lập Phiếu Xuất Kho & Chống Tồn Âm (Hình 4.6.3 Wireframe)."""
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    if user.VaiTro not in ["Admin", "Thukho"]:
        return RedirectResponse(url="/dashboard?error=access_denied", status_code=302)

    return templates.TemplateResponse(
        request=request,
        name="outbound.html",
        context={
            "request": request,
            "active_page": "outbound",
            "user": user
        }
    )

@app.get("/the-kho")
def route_the_kho(request: Request, db: Session = Depends(get_db), user = Depends(get_current_user_optional)):
    """Màn hình Tra Cứu Thẻ Kho Lũy Kế."""
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    items = db.query(HangHoa).all()
    item_list = []
    for it in items:
        item_list.append({
            "MaHH": it.MaHH,
            "TenHH": it.TenHH,
            "MaDVT": it.MaDVT,
            "SoLuongTon": it.ton_kho.SoLuongTon if it.ton_kho else 0
        })

    return templates.TemplateResponse(
        request=request,
        name="the_kho.html",
        context={
            "request": request,
            "active_page": "the-kho",
            "user": user,
            "items": item_list
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, reload_dirs=["app"])
