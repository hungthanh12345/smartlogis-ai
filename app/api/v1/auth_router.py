# app/api/v1/auth_router.py
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.schemas.auth_schemas import UserRegister, UserLogin, UserOut, Token
from app.services.auth_service import register_user, authenticate_user
from app.models.inventory_models import NguoiDung

router = APIRouter(prefix="/auth", tags=["X?c th?c & T?i kho?n (Auth)"])

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def api_register(user_in: UserRegister, db: Session = Depends(get_db)):
    """??ng k? t?i kho?n ng??i d?ng m?i (M?c ??nh vai tr? Th? kho)."""
    return register_user(db, user_in)

@router.post("/login", response_model=Token)
def api_login(user_in: UserLogin, response: Response, db: Session = Depends(get_db)):
    """??ng nh?p h? th?ng b?ng JSON body, c?p m? JWT Token v? ??t Cookie x?c th?c."""
    auth_result = authenticate_user(db, user_in)
    # Ghi Cookie access_token ?? tr?nh duy?t Web UI t? ??ng nh?n di?n phi?n ??ng nh?p
    response.set_cookie(
        key="access_token",
        value=f"Bearer {auth_result['access_token']}",
        httponly=True,
        max_age=60 * 60 * 24,
        samesite="lax"
    )
    return auth_result

@router.post("/token")
def api_token_oauth2(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Endpoint chu?n OAuth2 Password Flow ph?c v? Swagger UI Documentation."""
    user_login = UserLogin(TenDangNhap=form_data.username, MatKhau=form_data.password)
    auth_result = authenticate_user(db, user_login)
    return {
        "access_token": auth_result["access_token"],
        "token_type": "bearer"
    }

@router.get("/me", response_model=UserOut)
def api_get_me(current_user: NguoiDung = Depends(get_current_active_user)):
    """L?y th?ng tin ng??i d?ng ?ang ??ng nh?p t? JWT Token."""
    return current_user

@router.get("/logout")
@router.post("/logout")
def api_logout(response: Response):
    """Đăng xuất và xóa Cookie xác thực."""
    response.delete_cookie(key="access_token", path="/", httponly=True, samesite="lax")
    return {"message": "Đăng xuất thành công."}

