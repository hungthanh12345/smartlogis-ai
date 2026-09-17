# app/services/auth_service.py
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.inventory_models import NguoiDung
from app.schemas.auth_schemas import UserRegister, UserLogin
from app.core.security import verify_password, get_password_hash, create_access_token

def register_user(db: Session, user_in: UserRegister) -> NguoiDung:
    """Đăng ký tài khoản người dùng mới với mật khẩu Bcrypt Hash."""
    # Kiểm tra trùng tên đăng nhập
    existing = db.query(NguoiDung).filter(NguoiDung.TenDangNhap == user_in.TenDangNhap).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tên đăng nhập '{user_in.TenDangNhap}' đã tồn tại trong hệ thống."
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
    """Xác thực đăng nhập và cấp mã JWT Access Token."""
    user = db.query(NguoiDung).filter(NguoiDung.TenDangNhap == credentials.TenDangNhap).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tên đăng nhập hoặc mật khẩu không chính xác."
        )
    if not verify_password(credentials.MatKhau, user.MatKhau):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tên đăng nhập hoặc mật khẩu không chính xác."
        )
    if not user.KichHoat:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản này đã bị tạm khóa bởi Quản trị viên."
        )

    # Tạo JWT token
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
