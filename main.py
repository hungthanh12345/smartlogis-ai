# main.py - Điểm khởi chạy ứng dụng SmartLogis AI
import os
from fastapi import FastAPI, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import Base, engine, get_db
from app.core.security import get_current_user_optional
from app.models.inventory_models import HangHoa
from app.services.inventory_service import get_dashboard_kpis, get_stock_alerts
from app.services.ai_service import generate_ai_inventory_advisory
from app.api.v1 import auth_router, inventory_router, reports_router, ai_router
from seed import seed_database

# Khởi tạo bảng CSDL và seed data nếu chưa có
Base.metadata.create_all(bind=engine)
seed_database()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Hệ thống Quản lý Kho Tích hợp AI (Giai đoạn 1 & 2) - FastAPI, PostgreSQL Transaction ACID, CheckConstraint, Gemini Advisory"
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
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register")
def route_register(request: Request, user = Depends(get_current_user_optional)):
    """Màn hình Đăng ký."""
    if user:
        return RedirectResponse(url="/dashboard")
    return templates.TemplateResponse("register.html", {"request": request})


@app.get("/dashboard")
def route_dashboard(request: Request, db: Session = Depends(get_db), user = Depends(get_current_user_optional)):
    """Màn hình Dashboard Tổng quan v2.0 (Hình 4.6.1 Wireframe)."""
    if not user:
        return RedirectResponse(url="/login")

    kpis = get_dashboard_kpis(db)
    alerts = get_stock_alerts(db)
    ai_advisory = generate_ai_inventory_advisory(db)

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "active_page": "dashboard",
        "user": user,
        "kpis": kpis,
        "alerts": alerts,
        "ai_advisory": ai_advisory
    })

@app.get("/inbound")
def route_inbound(request: Request, db: Session = Depends(get_db), user = Depends(get_current_user_optional)):
    """Màn hình Lập Phiếu Nhập Kho (Hình 4.6.2 Wireframe)."""
    if not user:
        return RedirectResponse(url="/login")

    return templates.TemplateResponse("inbound.html", {
        "request": request,
        "active_page": "inbound",
        "user": user
    })

@app.get("/outbound")
def route_outbound(request: Request, db: Session = Depends(get_db), user = Depends(get_current_user_optional)):
    """Màn hình Lập Phiếu Xuất Kho & Chống Tồn Âm (Hình 4.6.3 Wireframe)."""
    if not user:
        return RedirectResponse(url="/login")

    return templates.TemplateResponse("outbound.html", {
        "request": request,
        "active_page": "outbound",
        "user": user
    })

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

    return templates.TemplateResponse("the_kho.html", {
        "request": request,
        "active_page": "the-kho",
        "user": user,
        "items": item_list
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
