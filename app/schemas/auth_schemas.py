# app/schemas/auth_schemas.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class UserRegister(BaseModel):
    TenDangNhap: str = Field(min_length=3, max_length=50, description="Tên đăng nhập")
    MatKhau: str = Field(min_length=6, description="Mật khẩu tối thiểu 6 ký tự")
    HoTen: str = Field(min_length=2, max_length=100, description="Họ và tên người dùng")
    VaiTro: Optional[str] = Field(default="Nhanvien", description="Vai trò: Admin, Thukho, hoặc Nhanvien")

class UserLogin(BaseModel):
    TenDangNhap: str
    MatKhau: str

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    MaND: int
    TenDangNhap: str
    HoTen: str
    VaiTro: str
    KichHoat: bool
    NgayTao: datetime

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserOut

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None
    user_id: Optional[int] = None
