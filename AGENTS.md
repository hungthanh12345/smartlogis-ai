# AGENTS.md - Chỉ Dẫn Vận Hành AI Coding Agent Cho Dự Án SmartLogis AI

Tài liệu này quy định toàn diện các nguyên tắc làm việc, tiêu chuẩn kiến trúc, quy trình bảo mật, giao thức Git và phương pháp kiểm thử dành cho AI Coding Agent khi tham gia phát triển, bảo trì và mở rộng hệ thống **SmartLogis AI** (Hệ Thống Quản Lý Kho Thông Minh Tích Hợp AI V4.0).

Mọi quyết định kỹ thuật phải căn cứ trực tiếp trên yêu cầu của người dùng, cấu trúc mã nguồn thực tế trong repository và các bất biến nghiệp vụ (business invariants) đã được nghiệm thu của hệ thống. Tuyệt đối không tự ý áp đặt công nghệ, quy ước hoặc giả định từ các dự án khác vào repository này.

---

## 1. Tổng Quan Kỹ Thuật & Bối Cảnh Dự Án

### 1.1. Mục Tiêu & Bản Chất Hệ Thống
**SmartLogis AI** là giải pháp quản lý kho vận vật tư công trình xây dựng cấp doanh nghiệp, tích hợp:
- **Giao dịch kho nguyên tử ACID:** Đảm bảo triệt để nguyên tắc **Zero Negative Stock** (Không bao giờ tồn âm) và bảo toàn tính bất biến của sổ Thẻ kho lũy kế.
- **Trợ lý AI Google Gemini LLM & Local Grounded Engine:** Cung cấp báo cáo điều hành kho 3 phần, tư vấn tối ưu chuỗi cung ứng, đồng thời bảo mật tuyệt đối bí mật kinh doanh (100% không để lộ giá vốn).
- **Hạ tầng Realtime Đa Thiết Bị:** Đồng bộ tức thời biến động kho qua WebSocket tới toàn bộ máy tính bàn, laptop, máy tính bảng và điện thoại di động trong mạng nội bộ/tên miền sản xuất.

### 1.2. Tech Stack Thực Tế Của Repository
- **Ngôn ngữ:** Python 3.12+
- **Backend Framework:** FastAPI 0.104+, Uvicorn (ASGI Server), Starlette
- **Data Access & ORM:** SQLAlchemy 2.0 (Core & ORM), Pydantic v2 & Pydantic-Settings
- **Kiến trúc CSDL Kép (Dual-Database Architecture):**
  - **Môi trường Phát triển & Kiểm thử Cục bộ (Dev/Test):** SQLite 3 (Chế độ Write-Ahead Logging `WAL`, `foreign_keys = ON`, `busy_timeout = 30000ms`). File CSDL: `smartlogis.db`.
  - **Môi trường Sản xuất (Production):** PostgreSQL 15+ hoặc MySQL 8.0 (InnoDB Engine, Connection Pooling với `DB_POOL_SIZE=10`, `DB_MAX_OVERFLOW=20`, `pool_pre_ping=True`).
- **Giao diện Người dùng (Frontend SSR & Client UI):** Jinja2 Templates, Tailwind CSS CDN, Vanilla JavaScript (Fetch API + Native WebSocket Client).
- **Bảo mật & Phiên làm việc:** JWT (python-jose), Bcrypt (mã hóa mật khẩu 72 bytes), In-memory Session Manager, Tab Session Isolation qua header `X-Session-User`, Cookie `access_token` (HTTPOnly, SameSite=Lax).
- **Trí tuệ Nhân tạo:** Google Gemini API (`gemini-3.5-flash-lite`, `gemini-3.6-flash`) kết hợp Local Grounded Conversational Engine (Chạy ngoại tuyến 100% dựa trên CSDL nội bộ).
- **Hạ tầng Mạng & Triển khai:** Nginx Reverse Proxy (Port 80/443), OpenSSL Self-Signed / Let's Encrypt CA, Docker & Docker Compose (`docker-compose.yml`), Shell/Batch Scripts (`run_app.bat`, `setup_domain_local.bat`, `open_firewall.bat`).

---

## 2. Các Bất Biến Nghiệp Vụ Cốt Lõi (Core Business Invariants)

Bất kỳ thay đổi mã nguồn nào cũng **PHẢI** tuân thủ và bảo toàn các bất biến nghiệp vụ sau đây:

### 2.1. Bất Biến Kiểm Soát Tồn Kho Chống Âm (Zero Negative Stock Invariant)
1. **Kiểm soát 2 tầng (Hardware & Software):**
   - **Tầng Backend (Application Level):** Nghi thức **Atomic SQL Decrement** được thực thi trực tiếp tại `app/services/outbound_service.py`:
     ```sql
     UPDATE ton_kho 
     SET SoLuongTon = SoLuongTon - :so_luong_xuat, CapNhatCuoi = :now 
     WHERE MaHH = :ma_hh AND SoLuongTon >= :so_luong_xuat;
     ```
     Nếu số bản ghi cập nhật `rowcount == 0` (do thiếu hàng hoặc có tiến trình khác tranh chấp trước), giao dịch **BẮT BUỘC** phải được rollback (`db.rollback()`) và trả về HTTP 400 Bad Request kèm thông báo minh bạch.
   - **Tầng CSDL (Database Level):** Ràng buộc phần cứng `CheckConstraint("SoLuongTon >= 0", name="check_soluongton_khong_am")` trên bảng `ton_kho` và `CheckConstraint("TonSauGiaoDich >= 0")` trên bảng `the_kho`.
2. **Giao dịch All-or-Nothing:** Không bao giờ cho phép một phiếu xuất/nhập ghi nhận dở dang một phần mặt hàng. Tất cả các SKU trong phiếu phải hợp lệ và thỏa mãn số dư thì mới được commit.

### 2.2. Bất Biến Sổ Thẻ Kho Bất Biến (Immutable Ledger & Running Balance Invariant)
1. Bảng `the_kho` là sổ cái kế toán phản ánh toàn bộ lịch sử biến động. Mỗi thao tác nhập kho (`NHAP`) hoặc xuất kho (`XUAT`) **bắt buộc** phải ghi thêm một bản ghi vào `the_kho` trong **cùng một Database Transaction** với cập nhật `ton_kho`.
2. Số dư lũy kế `TonSauGiaoDich` của bản ghi Thẻ kho mới nhất cho một SKU **luôn luôn phải bằng chính xác** giá trị `SoLuongTon` hiện thời trong bảng `ton_kho`.
3. Khi khởi động hoặc khi có nghi vấn sai lệch, sử dụng hàm chuẩn hóa `recalculate_and_sync_the_kho(db)` trong `app/services/inventory_service.py` để đồng bộ lại sổ cái.

### 2.3. Bất Biến Khử Nhạy Cảm Dữ Liệu AI (Data Sanitizer & Confidentiality Invariant)
1. **Tuyệt đối không gửi giá vốn sang AI bên ngoài:** Mọi truy vấn trích xuất dữ liệu kho để nạp cho Google Gemini API (qua `app/services/ai_data_service.py` hoặc `app/services/gemini_service.py`) **bắt buộc** phải đi qua bộ lọc đệ quy `sanitize_inventory_payload()`.
2. Danh sách đen các trường cấm gửi: `DonGiaNhap`, `don_gia_nhap`, `ThanhTien`, `thanh_tien`, `GiaVon`, `gia_von`, `cost_price`, `import_price`, `purchase_price`.
3. Kiểm toán dữ liệu qua endpoint `GET /api/v1/ai/raw-context` phải luôn trả về context sạch 100% không chứa bất kỳ trường giá nhập nào.

### 2.4. Bất Biến Phân Quyền RBAC 3 Vai Trò
Hệ thống chuẩn hóa 3 vai trò người dùng trong bảng `nguoi_dung`:
- **`Admin` (Quản trị viên):** Toàn quyền cấu hình hệ thống, quản lý tài khoản, danh mục hàng hóa, nhà cung cấp, lập chứng từ nhập/xuất, xuất file Excel và xem báo cáo AI.
- **`Thukho` (Thủ kho kiêm Kế toán):** Vận hành kho toàn diện và đối soát tài chính: Quản lý SKU, quản lý NCC, lập phiếu nhập/xuất ACID, tra cứu thẻ kho, xuất báo cáo kế toán Excel.
- **`Nhanvien` (Nhân viên kho - Staff):** Quyền **CHỈ ĐỌC (Read-only)**: Xem Dashboard, tra cứu SKU, tra cứu NCC, xem sổ thẻ kho phục vụ kiểm đếm/bốc dỡ. **BỊ CẤM:** Không được lập phiếu nhập kho, không được lập phiếu xuất kho (HTTP 403 / Redirect), không xuất file Excel, không sửa/xóa Master Data.

### 2.5. Bất Biến Chống Treo Trạng Thái & Đồng Bộ Đa Thiết Bị
- Mọi route Web SSR (`/dashboard`, `/inbound`, `/outbound`, `/the-kho`, `/hang-hoa`, `/nha-cung-cap`) và API kho phải luôn đính kèm header chống lưu bộ đệm trình duyệt: `Cache-Control: no-store, no-cache, must-revalidate, max-age=0` để loại bỏ rủi ro hiển thị số dư tồn kho cũ khi người dùng nhấn nút Back/Forward (bfcache).
- Sau khi transaction nhập kho hoặc xuất kho thành công, backend **phải gọi** `ws_manager.broadcast_sync({"type": "INVENTORY_UPDATED", ...})` để đồng bộ realtime tới tất cả client đang kết nối.

---

## 3. Quy Trình Làm Việc Của AI Agent Trước Khi Thay Đổi

1. **Khảo sát Hiện trạng & Tài liệu:**
   - Đọc kỹ `AGENTS.md`, `README.md`, `docs/database_design.md` và `docs/DEPLOY_DOMAIN_GUIDE.md`.
   - Kiểm tra các model tại `app/models/inventory_models.py`, schemas tại `app/schemas/inventory_schemas.py`, và services tại `app/services/`.
2. **Kiểm tra Trạng thái Git Trước Khi Sửa:**
   - Chạy `git status` trước khi thực hiện bất kỳ sửa đổi nào.
   - **Giữ nguyên các tệp đang uncommitted:** Không xóa, không revert, không ghi đè các thay đổi đang có của người dùng (bao gồm `.antigravity/`, các tệp tài liệu binary `docs/*.docx`, `docs/*.pptx`, hoặc các file service đang được chỉnh sửa).
   - Bảo vệ tệp cơ sở dữ liệu cục bộ `smartlogis.db` và tệp cấu hình `.env`. Tuyệt đối không xóa hoặc drop database.
3. **Phân tích Luồng Dữ Liệu & Điểm Gọi:**
   - Xác định rõ luồng: `Frontend (Template/JS)` -> `API Router (app/api/v1/)` -> `Service (app/services/)` -> `ORM Model (app/models/)` -> `Database Engine`.
   - Kiểm tra xem API có liên quan đến WebSocket broadcast, Idempotency token hoặc Anti-cache headers hay không.
4. **Làm rõ Yêu Cầu & Nêu Giả Định:**
   - Nếu yêu cầu có nhiều cách hiểu ảnh hưởng tới schema CSDL, nghiệp vụ tài chính hoặc phân quyền, dừng lại và hỏi người dùng.
   - Với các tối ưu nhỏ, an toàn và dễ đảo ngược, chọn giải pháp tối giản nhất bám sát kiến trúc hiện tại.

---

## 4. Nguyên Tắc Triển Khai & Phát Triển Mã Nguồn

### 4.1. Kiến Trúc Phân Lớp (Layered Service-Oriented Architecture)
- **Tầng API (`app/api/v1/`):** Chỉ thực hiện xác thực người dùng (`get_current_active_user`), kiểm tra vai trò (`require_role`), validate schema Pydantic đầu vào, gọi hàm Service tương ứng và trả response DTO. Không viết trực tiếp logic nghiệp vụ trừu tượng hoặc transaction phức tạp trong Router.
- **Tầng Dịch Vụ Nghiệp Vụ (`app/services/`):** Nơi duy trì transaction ACID, kiểm tra khóa ngoại logic, gom nhóm SKU, thực thi Atomic Decrement, ghi nhận sổ Thẻ kho, tính toán Burn-rate và kích hoạt WebSocket.
- **Tầng Truy Cập Dữ Liệu (`app/models/`):** Định nghĩa bảng SQLAlchemy với đầy đủ kiểu dữ liệu, index, ràng buộc khóa ngoại (`ForeignKey`) và `CheckConstraint`.
- **Tầng Xác Thực & Tiện Ích Hạt Nhân (`app/core/`):** Cung cấp cấu hình Pydantic (`config.py`), kết nối database (`database.py`), thuật toán Bcrypt/JWT (`security.py`), chống spam submit (`idempotency.py`), cô lập phiên làm việc (`session_manager.py`), và quản lý WebSocket kết nối (`websocket_manager.py`).

### 4.2. Quy Tắc Lập Trình & Naming Convention
- **Bảo toàn Quy ước Đặt tên Tiếng Việt Chuẩn Hóa trong CSDL & DTO:**
  - Bảng và cột CSDL sử dụng PascalCase/snake_case theo chuẩn nghiệp vụ kho Việt Nam: `MaHH`, `TenHH`, `SoLuongTon`, `TonSauGiaoDich`, `MaPN`, `MaPX`, `MaNCC`, `NguoiNhan`, `TonToiThieu`.
  - **TUYỆT ĐỐI KHÔNG** tự ý đổi tên các trường này sang tiếng Anh (như `product_id`, `quantity`, `inventory`) vì sẽ phá vỡ toàn bộ các liên kết trong giao diện Jinja2, các truy vấn SQL, báo cáo kế toán Excel và tài liệu bảo vệ đồ án.
- **Tái sử dụng Mã Nguồn Hiện Hữu:**
  - Lấy thời gian UTC chuẩn hóa qua tiện ích `app.core.datetime_utils.utc_now`.
  - Sử dụng `ws_manager.broadcast_sync(...)` để gửi thông báo realtime.
  - Sử dụng `idempotency_store` để bảo vệ các thao tác submit form tránh double click.
- **Không Thêm Dependency Hay Lớp Trừu Tượng Tùy Tiện:**
  - Không cài đặt thêm thư viện bên ngoài trừ khi người dùng yêu cầu hoặc bài toán thực sự đòi hỏi.
  - Không tạo thêm các abstract class, repository pattern phức tạp khi SQLAlchemy Session và Service functions đã đáp ứng đủ.

---

## 5. Quy Chuẩn Cơ Sở Dữ Liệu & ACID Transactions

### 5.1. Cấu Trúc Bảng & Quan Hệ Thực Thể (11 Bảng Chuẩn)
1. `nguoi_dung`: Quản lý tài khoản, mật khẩu Bcrypt hash, vai trò RBAC (`Admin`, `Thukho`, `Nhanvien`).
2. `nhom_hang`: Danh mục nhóm vật tư (Thép, Xi măng, Sơn, Bulong...).
3. `don_vi_tinh`: Đơn vị đo lường chuẩn hóa (Cây, Cuộn, Bao, Thùng, Hộp...).
4. `nha_cung_cap`: Thông tin đối tác, số điện thoại, địa chỉ, tổng tiền công nợ nhập hàng.
5. `hang_hoa`: Danh mục SKU, định mức tồn tối thiểu (`TonToiThieu`).
6. `ton_kho`: Số lượng tồn kho khả dụng tức thời (`SoLuongTon >= 0`). Quan hệ 1-1 với `hang_hoa`.
7. `phieu_nhap`: Chứng từ nhập Master, liên kết `nha_cung_cap` và `nguoi_dung`.
8. `chi_tiet_phieu_nhap`: Chi tiết SKU nhập, số lượng (`> 0`), đơn giá (`>= 0`), thành tiền.
9. `phieu_xuat`: Chứng từ xuất Master, thông tin người nhận, lý do xuất.
10. `chi_tiet_phieu_xuat`: Chi tiết SKU xuất, số lượng (`> 0`).
11. `the_kho`: Sổ cái ghi vết giao dịch (`NHAP`/`XUAT`), số lượng thay đổi, tồn sau giao dịch (`>= 0`).

### 5.2. Nguyên Tắc Quản Trị Dual-Database
- **Khi làm việc với SQLite:**
  - Luôn đảm bảo `PRAGMA foreign_keys = ON;` được kích hoạt ở mỗi kết nối.
  - Luôn bật chế độ `WAL` (Write-Ahead Logging) để cho phép đọc song song không bị khóa khi có thao tác ghi.
  - Thiết lập `PRAGMA busy_timeout = 30000;` để tránh lỗi `database is locked` khi có nhiều luồng truy cập đồng thời.
- **Khi làm việc với PostgreSQL / MySQL:**
  - Sử dụng Connection Pool đã cấu hình sẵn trong `app/core/database.py`.
  - Không hardcode dialect SQL riêng của SQLite (như syntax PRAGMA) vào logic chung; nếu cần, phải có khối kiểm tra `if is_sqlite:`.
- **An toàn Dữ liệu:** Tuyệt đối không chạy lệnh `DROP TABLE`, `TRUNCATE` hoặc xóa file `smartlogis.db`. Mọi migration điều chỉnh cấu trúc phải tương thích ngược và kiểm tra cột tồn tại trước khi chạy `ALTER TABLE`.

---

## 6. Tiêu Chuẩn Bảo Mật, Xác Thực & Trí Tuệ Nhân Tạo

### 6.1. Xác Thực & Cô Lập Phiên Làm Việc (Tab Session Isolation)
- Hệ thống hỗ trợ đăng nhập qua Web UI (Lưu JWT vào HTTPOnly Cookie `access_token`) và API Mobile/Postman (Header `Authorization: Bearer <token>`).
- Khi người dùng mở nhiều tab với các tài khoản khác nhau trên cùng một trình duyệt, Frontend sẽ gửi kèm header `X-Session-User: <username>`.
- Hàm `get_current_user_optional` trong `app/core/security.py` phải kiểm tra: nếu header `X-Session-User` không khớp với `sub` trong JWT token, phiên làm việc lập tức bị từ chối (trả về `None` hoặc HTTP 401) để ngăn chặn hành vi thao tác chéo quyền giữa các tab.
- Khi người dùng đăng xuất (`/logout`), session ID của người dùng phải bị vô hiệu hóa trong `session_manager` và cookie phải được xóa sạch.

### 6.2. Bảo Mật & Dự Phòng Cho Trợ Lý AI Google Gemini
- **Data Sanitizer là bắt buộc:** Bất kỳ hàm nào nạp context dữ liệu cho AI đều phải chạy qua `sanitize_inventory_payload()`.
- **System Instruction Anti-Hallucination:** System prompt luôn phải có điều khoản nghiêm cấm bịa đặt số liệu không có trong context JSON.
- **Cơ chế Fallback Grounded Engine Ngoại Tuyến:**
  - Nếu `GEMINI_API_KEY` chưa cấu hình, mạng gián đoạn, API trả HTTP 429 (Rate Limit Quota Exceeded), hoặc quá thời gian `AI_TIMEOUT_SECONDS`:
  - Hệ thống **KHÔNG ĐƯỢC PHÉP CRASH** hoặc trả lỗi 500 ra giao diện.
  - Hệ thống phải tự động chuyển sang `_generate_grounded_fallback()` để dùng giải thuật nội bộ phân tích số liệu trực tiếp từ CSDL và trả về báo cáo 3 phần hoàn chỉnh.
- **Bảo mật Secret:** Tuyệt đối không commit tệp `.env` chứa API Key thật lên remote repository. Không in API Key ra log hay response.

---

## 7. Quy Trình Git & Phối Hợp Thay Đổi

### 7.1. Cấu Trúc Nhánh & Phân Phối Công Việc
- Repository này sử dụng nhánh chính thức là **`main`**.
- Tất cả các công việc phát triển, tính năng mới hoặc sửa lỗi **PHẢI** được thực hiện trên nhánh riêng biệt xuất phát từ nhánh chính mới nhất:
  - Tính năng mới: `feature/<ten-tinh-nang>` (Ví dụ: `feature/export-pdf-report`)
  - Sửa lỗi: `fix/<ten-loi>` (Ví dụ: `fix/websocket-reconnect-lag`)
  - Tối ưu / Dọn dẹp: `chore/<nhiem-vu>` (Ví dụ: `chore/update-readme-diagrams`)
- **Nguyên tắc bảo vệ nhánh `main`:**
  - Không code, commit hoặc push trực tiếp mã nguồn chưa kiểm thử lên `main`.
  - Chỉ tích hợp vào `main` sau khi toàn bộ bài kiểm thử tự động đã hoàn thành và có sự phê duyệt của chủ sở hữu dự án.
- Không sử dụng `git push --force` trên bất kỳ nhánh chia sẻ nào.
- Không tự ý rebase hoặc rewrite Git history đã công bố.

### 7.2. Kiểm Tra Diff & Quy Chuẩn Commit
- Trước khi tạo commit, chạy `git diff` và `git status` để rà soát từng dòng thay đổi.
- Chỉ stage các file nằm trong phạm vi yêu cầu (`git add <file>`). Tuyệt đối không sử dụng `git add .` bừa bãi làm dính các file tạm, file log (`*.log`), file cache (`.pytest_cache`, `__pycache__`) hoặc database.
- Quy chuẩn thông điệp Commit (Conventional Commits):
  - `feat(<module>): <mô tả ngắn ngọn>`
  - `fix(<module>): <mô tả lỗi đã sửa>`
  - `docs(<module>): <cập nhật tài liệu>`
  - `test(<module>): <bổ sung hoặc cập nhật test cases>`
  - `chore(<module>): <dọn dẹp mã nguồn>`

---

## 8. Quy Chuẩn Kiểm Thử & Xác Minh (Testing & Verification)

Mọi thay đổi mã nguồn phải có bằng chứng kiểm thử trước khi bàn giao. Dự án tích hợp bộ kiểm thử tự động toàn diện trong thư mục `tests/`.

### 8.1. Các Lệnh Kiểm Thử Tiêu Chuẩn
- **Chạy toàn bộ bộ kiểm thử tự động:**
  ```powershell
  pytest tests/ -v
  ```
  *(Hoặc chỉ định rõ phiên bản Python: `py -3.12 -m pytest tests/ -v`)*

- **Chạy kiểm thử theo từng phân hệ trọng tâm:**
  - *Kiểm thử ACID, Chống tồn âm & Concurrency Race Condition:*
    ```powershell
    pytest tests/test_phase2_inventory.py -v
    ```
  - *Kiểm thử Đồng bộ Sổ Thẻ kho & Tồn kho Lũy kế:*
    ```powershell
    pytest tests/test_inventory_ledger_sync.py -v
    ```
  - *Kiểm thử Phân hệ Trí tuệ Nhân tạo & Khử Nhạy Cảm Giá Vốn:*
    ```powershell
    pytest tests/test_ai_engine.py -v
    ```
  - *Kiểm thử Chatbot AI Đàm Thoại & Trích Xuất Dữ Liệu:*
    ```powershell
    pytest tests/test_ai_chat.py -v
    ```
  - *Kiểm thử WebSocket Realtime Multi-Device:*
    ```powershell
    pytest tests/test_websocket.py -v
    ```
  - *Kiểm thử Xác thực, Đa Tab Session & Anti-Cache:*
    ```powershell
    pytest tests/test_auth_tab_session.py -v
    ```
  - *Kiểm thử Xử lý Ngoại lệ Inbound/Outbound & Idempotency:*
    ```powershell
    pytest tests/test_inbound_outbound_exceptions.py tests/test_prg_idempotency.py -v
    ```

### 8.2. Quy Tắc Kiểm Thử Nghiêm Ngặt
1. **Không sửa test để che giấu lỗi:** Tuyệt đối không xóa assert, không làm yếu điều kiện kiểm tra hoặc skip test chỉ để báo cáo kết quả PASS.
2. **Cách ly Môi trường Kiểm Thử:** Test suite phải chạy trên SQLite in-memory hoặc database kiểm thử riêng biệt, tuyệt đối không được ghi dữ liệu rác làm sai lệch file `smartlogis.db` chính thức.
3. **Độc lập với Kết nối Internet:** Các bài kiểm thử AI (`test_ai_engine.py`, `test_ai_chat.py`) phải sử dụng cơ chế Mocking hoặc Fallback Grounded Engine nội bộ, không phụ thuộc vào trạng thái mạng hay hạn ngạch của Google Gemini API.
4. **Xác minh Thực Tế:**
   - Kết quả kiểm thử thành công ở tầng code không thay thế được việc kiểm tra hành vi UI. Khi sửa giao diện, phải xác nhận tính thẩm mỹ, responsive và thông báo lỗi hiển thị đúng trên trình duyệt.
   - Báo cáo rõ ràng: Tên test đã chạy, số lượng PASSED/FAILED, và đính kèm output cụ thể.

---

## 9. Khởi Chạy Ứng Dụng & Vận Hành Cục Bộ

Khi cần khởi chạy ứng dụng để xác minh trực quan:
- **Khởi chạy chính thức (Windows):** Chạy tệp batch tự động:
  ```cmd
  run_app.bat
  ```
  *(Tự động phát hiện môi trường Python, kiểm tra CSDL, nạp seed ban đầu và mở trình duyệt tại `http://127.0.0.1:8000/`)*
- **Khởi chạy thủ công qua dòng lệnh:**
  ```powershell
  python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload --reload-dir app
  ```
- **Tài khoản Kiểm thử & Demo Mặc định:**
  - `Admin`: `admin` / `admin123` (Toàn quyền quản trị)
  - `Thủ kho kiêm Kế toán`: `thukho` / `thukho123` (Vận hành xuất/nhập, thẻ kho, Excel)
  - `Nhân viên kho (Staff)`: `nhanvien` / `nhanvien123` (Chỉ đọc Dashboard, SKU, NCC)

---

## 10. Tiêu Chí Hoàn Tất Công Việc (Definition of Done)

Một tác vụ chỉ được coi là hoàn tất khi AI Agent đáp ứng đầy đủ các tiêu chí:
1. **Mã nguồn sạch & đúng phạm vi:** Chỉ thay đổi các tệp thuộc yêu cầu; không để lại file tạm, debug logs, hay sửa đổi ngoài phạm vi.
2. **Bảo toàn Bất biến:** Đảm bảo Zero Negative Stock, đồng bộ Thẻ kho, Data Sanitizer và phân quyền RBAC 3 vai trò hoạt động chính xác 100%.
3. **Kiểm thử tự động PASS:** Các bài kiểm thử liên quan trong thư mục `tests/` chạy thành công không có lỗi hồi quy.
4. **Bảo vệ Dữ liệu & Git:** Không làm thất thoát dữ liệu trong `smartlogis.db`, không ghi đè uncommitted changes của người dùng, git diff phản ánh đúng mục tiêu.
5. **Báo cáo Trung Thực & Minh Bạch:** Trình bày rõ ràng những gì đã thực hiện, tệp đã sửa, kết quả test thực tế và hướng dẫn người dùng tự kiểm chứng.

---

> **Nguyên tắc cốt lõi dành cho SmartLogis AI:**
> Đọc hiểu trước khi sửa • Bảo vệ dữ liệu và bất biến kho • Không bao giờ để tồn âm • Khử trùng giá vốn 100% trước khi gửi AI • Bảo mật đa tab và phân quyền từ backend • Giữ nguyên quy ước PascalCase Tiếng Việt trong CSDL • Kiểm thử tự động trước khi báo cáo • Tôn trọng quy trình nhánh Git.
