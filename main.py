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
seed_database()

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


# =============================================================================
# WEB UI SSR ROUTES (GIAO DIỆN NGƯỜI DÙNG)
# =============================================================================

@app.get("/")
def route_root():
    """Chuyển hướng trang chủ về Dashboard."""
    return RedirectResponse(url="/dashboard")

@app.get("/logout")
@app.post("/logout")
def route_logout():
    """Đăng xuất người dùng: Xóa cookie xác thực và chuyển hướng về trang Đăng nhập."""
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie(key="access_token", path="/", httponly=True, samesite="lax")
    return response

@app.get("/login")
def route_login(request: Request, user = Depends(get_current_user_optional)):
    """Màn hình Đăng nhập."""
    if user:
        return RedirectResponse(url="/dashboard")
    return templates.TemplateResponse(request=request, name="login.html")

@app.get("/register")
def route_register():
    """Khóa đăng ký tự do — Hệ thống kho nội bộ chuyển hướng trực tiếp về trang đăng nhập."""
    return RedirectResponse(url="/login")

@app.get("/dashboard")
def route_dashboard(request: Request, db: Session = Depends(get_db), user = Depends(get_current_user_optional)):
    """Màn hình Dashboard Tổng quan v2.0 (Hình 4.6.1 Wireframe)."""
    if not user:
        return RedirectResponse(url="/login")

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
        return RedirectResponse(url="/login")

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
def route_nha_cung_cap(request: Request, db: Session = Depends(get_db), user = Depends(get_current_user_optional)):
    """Màn hình Quản lý Nhà cung cấp (CRUD NCC & KPI)."""
    if not user:
        return RedirectResponse(url="/login")

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
        return RedirectResponse(url="/login")
    if user.VaiTro not in ["Admin", "Thukho", "Ketoan"]:
        return RedirectResponse(url="/dashboard?error=access_denied")

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
        return RedirectResponse(url="/login")
    if user.VaiTro not in ["Admin", "Thukho", "Ketoan"]:
        return RedirectResponse(url="/dashboard?error=access_denied")

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
        return RedirectResponse(url="/login")

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
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
