# app/schemas/auth_schemas.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class UserRegister(BaseModel):
    TenDangNhap: str = Field(min_length=3, max_length=50, description="T?n ??ng nh?p")
    MatKhau: str = Field(min_length=6, description="M?t kh?u t?i thi?u 6 k? t?")
    HoTen: str = Field(min_length=2, max_length=100, description="H? v? t?n ng??i d?ng")
    VaiTro: Optional[str] = Field(default="Thukho", description="Vai tr?: Admin, Thukho, ho?c Ketoan")

class UserLogin(BaseModel):
    TenDangNhap: str
    MatKhau: str

class UserOut(BaseModel):
    MaND: int
    TenDangNhap: str
    HoTen: str
    VaiTro: str
    KichHoat: bool
    NgayTao: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserOut

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None
    user_id: Optional[int] = None
