from datetime import datetime, timedelta
from typing import Optional, List
import bcrypt
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/token", auto_error=False)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Kiểm tra mật khẩu văn bản thường với chuỗi Bcrypt Hash."""
    try:
        pwd_bytes = plain_password.encode('utf-8')[:72]
        hash_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(pwd_bytes, hash_bytes)
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    """Băm mật khẩu bằng thuật toán Bcrypt trực tiếp."""
    pwd_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Khởi tạo mã JWT Access Token mã hóa thông tin người dùng."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_access_token(token: str) -> Optional[dict]:
    """Giải mã JWT Access Token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None

def get_current_user_optional(request: Request, token: Optional[str] = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Lấy thông tin người dùng hiện tại từ Header Bearer hoặc Cookie (dành cho Web UI)."""
    from app.models.inventory_models import NguoiDung
    
    jwt_token = token
    if not jwt_token:
        jwt_token = request.cookies.get("access_token")
        if jwt_token and jwt_token.startswith("Bearer "):
            jwt_token = jwt_token[7:]

    if not jwt_token:
        return None

    payload = decode_access_token(jwt_token)
    if not payload:
        return None

    username: str = payload.get("sub")
    if not username:
        return None

    user = db.query(NguoiDung).filter(NguoiDung.TenDangNhap == username).first()
    return user

def get_current_active_user(user = Depends(get_current_user_optional)):
    """Bắt buộc người dùng đã xác thực, nếu không ném lỗi HTTP 401."""
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Phiên làm việc hết hạn hoặc chưa đăng nhập.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

def require_role(allowed_roles: List[str]):
    """Dependency phân quyền truy cập theo vai trò (Admin, Thukho, Ketoan)."""
    def role_checker(current_user = Depends(get_current_active_user)):
        if current_user.VaiTro not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Tài khoản vai trò '{current_user.VaiTro}' không có quyền thực hiện chức năng này."
            )
        return current_user
    return role_checker
