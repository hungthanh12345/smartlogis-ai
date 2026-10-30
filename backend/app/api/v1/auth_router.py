# app/api/v1/auth_router.py
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_active_user, get_current_user_optional
from app.schemas.auth_schemas import UserRegister, UserLogin, UserOut, Token
from app.services.auth_service import register_user, authenticate_user
from app.models.inventory_models import NguoiDung
from app.core.session_manager import session_manager

router = APIRouter(prefix="/auth", tags=["Xác thực & Tài khoản (Auth)"])

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def api_register(user_in: UserRegister, db: Session = Depends(get_db)):
    """Đăng ký tài khoản người dùng mới (Mặc định vai trò Thủ kho)."""
    return register_user(db, user_in)

@router.post("/login", response_model=Token)
def api_login(user_in: UserLogin, response: Response, db: Session = Depends(get_db)):
    """Đăng nhập hệ thống bằng JSON body, cấp mã JWT Token và đặt Cookie xác thực."""
    auth_result = authenticate_user(db, user_in)

    # Ghi Cookie access_token để trình duyệt Web UI tự động nhận diện phiên đăng nhập
    response.set_cookie(
        key="access_token",
        value=f"Bearer {auth_result['access_token']}",
        httponly=False,
        max_age=60 * 60 * 24,
        samesite="lax"
    )
    return auth_result

@router.post("/token")
def api_token_oauth2(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Endpoint chuẩn OAuth2 Password Flow phục vụ Swagger UI Documentation."""
    user_login = UserLogin(TenDangNhap=form_data.username, MatKhau=form_data.password)
    auth_result = authenticate_user(db, user_login)
    return {
        "access_token": auth_result["access_token"],
        "token_type": "bearer"
    }

@router.get("/me", response_model=UserOut)
def api_get_me(current_user: NguoiDung = Depends(get_current_active_user)):
    """Lấy thông tin người dùng đang đăng nhập từ JWT Token."""
    return current_user

@router.get("/logout")
@router.post("/logout")
def api_logout(response: Response, current_user = Depends(get_current_user_optional)):
    """Đăng xuất và xóa Cookie xác thực, vô hiệu hóa session."""
    if current_user:
        session_manager.invalidate_session(current_user.TenDangNhap)
    response.delete_cookie(key="access_token", path="/", httponly=True, samesite="lax")
    return {"message": "Đăng xuất thành công."}

