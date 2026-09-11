# app/services/auth_service.py
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.inventory_models import NguoiDung
from app.schemas.auth_schemas import UserRegister, UserLogin
from app.core.security import verify_password, get_password_hash, create_access_token

def register_user(db: Session, user_in: UserRegister) -> NguoiDung:
    """??ng k? t?i kho?n ng??i d?ng m?i v?i m?t kh?u Bcrypt Hash."""
    # Ki?m tra tr?ng t?n ??ng nh?p
    existing = db.query(NguoiDung).filter(NguoiDung.TenDangNhap == user_in.TenDangNhap).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"T?n ??ng nh?p '{user_in.TenDangNhap}' ?? t?n t?i trong h? th?ng."
        )

    # Chuẩn hóa vai trò (Admin, Thukho, Nhanvien)
    role = user_in.VaiTro if user_in.VaiTro in ["Admin", "Thukho", "Nhanvien"] else "Nhanvien"

    hashed_pw = get_password_hash(user_in.MatKhau)
    new_user = NguoiDung(
        TenDangNhap=user_in.TenDangNhap,
        MatKhau=hashed_pw,
        HoTen=user_in.HoTen,
        VaiTro=role,
        KichHoat=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def authenticate_user(db: Session, credentials: UserLogin) -> dict:
    """X?c th?c ??ng nh?p v? c?p m? JWT Access Token."""
    user = db.query(NguoiDung).filter(NguoiDung.TenDangNhap == credentials.TenDangNhap).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="T?n ??ng nh?p ho?c m?t kh?u kh?ng ch?nh x?c."
        )
    if not verify_password(credentials.MatKhau, user.MatKhau):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="T?n ??ng nh?p ho?c m?t kh?u kh?ng ch?nh x?c."
        )
    if not user.KichHoat:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="T?i kho?n n?y ?? b? t?m kh?a b?i Qu?n tr? vi?n."
        )

    # T?o JWT token
    token_payload = {
        "sub": user.TenDangNhap,
        "mand": user.MaND,
        "vaitro": user.VaiTro,
        "hoten": user.HoTen
    }
    access_token = create_access_token(token_payload)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }
