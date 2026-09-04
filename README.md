# SmartLogis AI v2.0 - Hệ Thống Quản Lý Kho Tích Hợp AI

Dự án hoàn thiện theo đúng tài liệu đặc tả đồ án **Hệ thống Quản lý Kho có Tích hợp AI** (Giai đoạn 1 & Giai đoạn 2).

---

## 1. Điểm Nổi Bật & Kiến Trúc Kỹ Thuật

- **Backend Framework:** FastAPI (Python) hiệu năng cao, tự động sinh tài liệu Swagger UI/OpenAPI.
- **Cơ sở dữ liệu & Toàn vẹn ACID:** 
  - Sử dụng SQLAlchemy 2.0 ORM.
  - Khóa bi quan **Pessimistic Locking (`with_for_update()` / `SELECT ... FOR UPDATE`)** để loại bỏ 100% rủi ro Race Condition khi nhiều thủ kho cùng xuất hàng.
  - Ràng buộc phần cứng CSDL **`CHECK (SoLuongTon >= 0)`** ngăn chặn tồn kho âm tuyệt đối.
- **Xác thực & Phân quyền:** JWT Authentication (Bcrypt Hash) với 3 vai trò: **Admin**, **Thủ kho (Thukho)**, **Kế toán (Ketoan)**.
- **Giao diện Người dùng (UI):** Tái hiện 100% Wireframe trong tài liệu:
  - **Dashboard v2.0:** 4 KPI Cards, Bảng cảnh báo hàng chạm ngưỡng tồn min (đỏ nguy cấp / vàng cận ngưỡng), Khối Widget Gemini AI Advisory.
  - **Màn hình Nhập kho (Inbound):** Bảng chi tiết động, tính thành tiền tự động, kích hoạt Transaction ACID ghi master-detail, tăng tồn kho và ghi sổ thẻ kho.
  - **Màn hình Xuất kho (Outbound):** Thẩm định số dư tồn kho thời gian thực (Real-time Validation), tự động highlight đỏ dòng thiếu hàng và vô hiệu hóa nút submit khi phát hiện vi phạm tồn âm.
  - **Tra cứu Thẻ kho:** Xem lịch sử biến động từng mặt hàng và tồn sau giao dịch.

---

## 2. Cấu Trúc Thư Mục Dự Án

```
smartlogis-ai/
├── app/
│   ├── api/v1/                 # Các REST API Routers
│   │   ├── auth_router.py      # /api/v1/auth (Đăng ký, Đăng nhập, Token JWT, Me)
│   │   ├── inventory_router.py # /api/v1/kho (KPIs, Cảnh báo, CRUD, Nhập/Xuất ACID)
│   │   ├── reports_router.py   # /api/v1/reports (Thẻ kho, Stubs Export Excel/PDF)
│   │   └── ai_router.py        # /api/v1/ai (Gemini Advisory & Data Sanitizer)
│   ├── core/                   # Cấu hình hạt nhân
│   │   ├── config.py           # Cấu hình Settings, JWT, Database URL
│   │   ├── database.py         # SQLAlchemy engine, SessionLocal, Base
│   │   └── security.py         # Bcrypt passlib, JWT create/decode, Role Dependencies
│   ├── models/                 # SQLAlchemy ORM Models
│   │   └── inventory_models.py # NguoiDung, NhomHang, DVT, NhaCungCap, HangHoa, TonKho (CheckConstraint), PhieuNhap, ChiTietNhap, PhieuXuat, ChiTietXuat, TheKho
│   ├── schemas/                # Pydantic Schemas / DTOs
│   │   ├── auth_schemas.py     # UserRegister, UserLogin, Token, UserOut
│   │   └── inventory_schemas.py# PhieuNhapCreate, PhieuXuatCreate, KPISummary, StockAlertItem
│   ├── services/               # Tầng nghiệp vụ xử lý Transaction
│   │   ├── auth_service.py     # Đăng ký & xác thực Bcrypt
│   │   ├── inbound_service.py  # Transaction nhập kho ACID
│   │   ├── outbound_service.py # Transaction xuất kho khóa bi quan with_for_update() chống tồn âm
│   │   ├── inventory_service.py# Tính toán KPIs, lọc cảnh báo tồn min, trích xuất thẻ kho
│   │   └── ai_service.py       # Gemini Grounded Advisory & Data Sanitizer ẩn giá vốn
│   ├── templates/              # Giao diện Jinja2 HTML5 / Tailwind CSS
│   │   ├── base.html           # Master Layout (Sidebar Navy, Topbar, User badge)
│   │   ├── login.html          # Đăng nhập kèm nút bấm demo 1-click
│   │   ├── register.html       # Đăng ký tài khoản
│   │   ├── dashboard.html      # Dashboard tổng quan & cảnh báo tồn min v2.0
│   │   ├── inbound.html        # Lập phiếu nhập kho
│   │   ├── outbound.html       # Lập phiếu xuất kho & kiểm soát tồn âm
│   │   └── the_kho.html        # Tra cứu thẻ kho lũy kế
│   └── static/                 # Static assets (CSS, JS)
├── seed.py                     # Script tạo dữ liệu thử nghiệm ban đầu
├── main.py                     # File ứng dụng FastAPI chính
├── run.py                      # Script chạy server tiện lợi
├── requirements.txt            # Danh sách thư viện cần thiết
└── README.md                   # Tài liệu hướng dẫn
```

---

## 3. Hướng Dẫn Cài Đặt & Khởi Chạy

### Cách 1: Sử dụng Môi trường Ảo (Virtual Environment) đã tạo sẵn

1. Mở Terminal / PowerShell tại thư mục dự án:
   ```bash
   cd "C:\Users\NGUYEN THANH HUNG\.gemini\antigravity\scratch\smartlogis-ai"
   ```

2. Kích hoạt môi trường ảo:
   ```powershell
   .\venv\Scripts\activate
   ```

3. Khởi chạy máy chủ:
   ```powershell
   python run.py
   # hoặc:
   uvicorn main:app --reload --port 8000
   ```

4. Truy cập hệ thống trên trình duyệt:
   - **Giao diện Web:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
   - **Tài liệu Swagger API:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 4. Tài Khoản Demo Mẫu Đã Tạo Sẵn

Hệ thống đã tự động chạy script `seed.py` khởi tạo sẵn các tài khoản sau (bạn có thể bấm trực tiếp các nút demo trên màn hình đăng nhập):

| Tên Đăng Nhập | Mật Khẩu | Vai Trò | Quyền Hạn |
| :--- | :--- | :--- | :--- |
| `admin` | `admin123` | **Admin** | Toàn quyền quản trị hệ thống, danh mục và báo cáo |
| `thukho` | `thukho123` | **Thủ kho** | Lập phiếu nhập kho, xuất kho, kiểm soát tồn |
| `ketoan` | `ketoan123` | **Kế toán** | Tra cứu thẻ kho, xem báo cáo thống kê |

---

## 5. Thử Nghiệm Tính Năng Chống Tồn Âm (ACID Locking)

1. Đăng nhập với tài khoản `thukho` / `thukho123`.
2. Vào màn hình **Lập Phiếu Xuất Kho** (`/outbound`).
3. Nhập mặt hàng `[HH-008] Sơn chống rỉ Alkyd 5L` (Tồn khả dụng trong kho là `10`).
4. Nhập số lượng xuất là `25` (Vượt tồn kho 15 thùng):
   - **Tầng giao diện:** Ô nhập chuyển sang viền đỏ rực, hiển thị badge `LỖI: TỒN ÂM (-15)`, xuất hiện Banner cảnh báo vi phạm tồn âm và nút **Xác nhận Xuất Kho bị khóa chặt (Disabled)**.
   - **Tầng Backend:** Nếu cố tình gửi request trực tiếp qua API, hàm `execute_outbound_transaction` sử dụng `with_for_update()` phát hiện vi phạm, lập tức gọi `db.rollback()` và ném lỗi `HTTP 400 Bad Request`, đảm bảo không bao giờ bị tồn âm.\n