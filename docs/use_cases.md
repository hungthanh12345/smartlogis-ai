# ĐẶC TẢ USE CASE CHI TIẾT (USE CASE SPECIFICATIONS)
## DỰ ÁN: HỆ THỐNG QUẢN LÝ KHO TÍCH HỢP AI (SMARTLOGIS AI V2.0)

---

## 1. DANH SÁCH CÁC TÁC NHÂN (ACTORS)

| Tác nhân (Actor) | Mô tả vai trò | Trách nhiệm chính trong hệ thống |
| :--- | :--- | :--- |
| **Admin (Quản trị viên)** | Người quản lý toàn quyền hệ thống | Quản trị tài khoản người dùng, cấu hình tham số kho, theo dõi toàn diện Dashboard và khuyến nghị AI. |
| **Thủ kho (Warehouse Staff)** | Người trực tiếp vận hành tại kho vật lý | Tiếp nhận hàng nhập, tạo phiếu nhập kho, kiểm tra tồn và lập phiếu xuất kho vật tư. |
| **Kế toán (Accountant)** | Người kiểm soát số liệu và luân chuyển tài chính | Tra cứu sổ thẻ kho, đối soát tính toàn vẹn chứng từ, kiểm tra cảnh báo tồn tối thiểu và xuất báo cáo. |
| **Trợ lý AI (Gemini AI)** | Hệ thống dịch vụ thông minh bên ngoài | Tiếp nhận dữ liệu tồn kho đã làm sạch, xử lý Grounded Prompting và sinh khuyến nghị phân tích chiến lược. |

---

## 2. MA TRẬN PHÂN QUYỀN USE CASE (USE CASE MATRIX)

| Mã UC | Tên Use Case | Admin | Thủ kho | Kế toán | Trợ lý AI |
| :---: | :--- | :---: | :---: | :---: | :---: |
| **UC01** | Đăng nhập & Quản lý phiên làm việc (JWT) | ✔ | ✔ | ✔ | |
| **UC02** | Quản trị Danh mục hàng hóa & Nhà cung cấp | ✔ | ✔ | | |
| **UC03** | Lập Phiếu Nhập Kho & Cập nhật tồn kho (Inbound) | ✔ | ✔ | | |
| **UC04** | Lập Phiếu Xuất Kho & Phòng tỏa tồn âm (Outbound) | ✔ | ✔ | | |
| **UC05** | Tra cứu Sổ Thẻ Kho lũy kế chi tiết | ✔ | ✔ | ✔ | |
| **UC06** | Giám sát Dashboard KPI & Cảnh báo tồn kho min | ✔ | ✔ | ✔ | |
| **UC07** | Tham vấn Trợ lý AI phân tích & Lập kế hoạch bổ sung | ✔ | ✔ | ✔ | ✔ *(Xử lý)* |
| **UC08** | Xuất Báo cáo Nhập - Xuất - Tồn (Excel / PDF) | ✔ | | ✔ | |

---

## 3. ĐẶC TẢ CHI TIẾT CÁC USE CASE TIÊU BIỂU

### 3.1. UC01: Đăng nhập & Xác thực Hệ thống
* **Tác nhân:** Toàn bộ người dùng (Admin, Thủ kho, Kế toán).
* **Mục tiêu:** Cấp quyền truy cập hệ thống phù hợp với vai trò của người dùng.
* **Tiền điều kiện:** Người dùng đã có tài khoản đang kích hoạt (KichHoat = True).
* **Luồng chính (Basic Flow):**
  1. Người dùng mở trang /login và nhập Tên đăng nhập cùng Mật khẩu.
  2. Frontend gửi request POST /api/v1/auth/login.
  3. Backend truy vấn CSDL tìm người dùng theo TenDangNhap.
  4. Backend kiểm tra mật khẩu bằng hàm băm crypt.checkpw().
  5. Nếu khớp, Backend sinh chuỗi JWT Access Token chứa sub (tên đăng nhập) và aitro (vai trò).
  6. Backend ghi Cookie ccess_token có gắn cờ HttpOnly: True và trả về thông tin người dùng.
  7. Trình duyệt chuyển hướng vào trang /dashboard.
* **Luồng ngoại lệ (Alternative Flow):**
  * *4a. Sai tên đăng nhập hoặc mật khẩu:* Hệ thống trả về HTTP 401 Unauthorized, hiển thị cảnh báo đỏ trên form đăng nhập.

---

### 3.2. UC03: Lập Phiếu Nhập Kho (Inbound Transaction)
* **Tác nhân:** Thủ kho, Admin.
* **Mục tiêu:** Nhập hàng hóa từ Nhà cung cấp vào kho, tự động tăng tồn kho và ghi thẻ kho.
* **Tiền điều kiện:** Người dùng đã đăng nhập với quyền Thủ kho hoặc Admin.
* **Luồng chính (Basic Flow):**
  1. Thủ kho chọn chức năng **Lập Phiếu Nhập Kho** trên thanh Menu.
  2. Chọn Nhà cung cấp từ danh sách đối tác và nhập ghi chú.
  3. Chọn các mặt hàng cần nhập, điền Số lượng nhập ($>0$) và Đơn giá mua.
  4. Hệ thống tự động tính Thành tiền từng dòng và Tổng giá trị phiếu nhập.
  5. Bấm nút **Xác nhận Nhập Kho**.
  6. Backend mở một **Database Transaction (ACID)**:
     * Tạo bản ghi PhieuNhap (Master) và các bản ghi ChiTietPhieuNhap (Detail).
     * Khóa bản ghi TonKho tương ứng và thực hiện phép cộng SoLuongTon = SoLuongTon + SoLuongNhap.
     * Tạo bản ghi TheKho với LoaiGiaoDich = 'NHAP', lưu lại số lượng tăng và tồn lũy kế sau giao dịch.
     * Thực thi lệnh db.commit().
  7. Hệ thống thông báo nhập kho thành công và cập nhật lại giao diện.

---

### 3.3. UC04: Lập Phiếu Xuất Kho & Kiểm Soát Chống Tồn Âm (Outbound Transaction)
* **Tác nhân:** Thủ kho, Admin.
* **Mục tiêu:** Xuất vật tư phục vụ công trình / khách hàng và đảm bảo tuyệt đối không bị tồn âm.
* **Tiền điều kiện:** Người dùng đã đăng nhập.
* **Luồng chính (Basic Flow):**
  1. Người dùng mở màn hình **Lập Phiếu Xuất Kho**.
  2. Nhập Người nhận / Đơn vị tiếp nhận và Lý do xuất kho.
  3. Chọn mặt hàng cần xuất: Hệ thống tải số lượng tồn khả dụng thời gian thực.
  4. Nhập số lượng xuất:
     * *Tầng Frontend Validation:* Nếu \ lượng\ xuất \le Tồn\ khả\ dụng$, nút xuất sáng và hợp lệ.
  5. Bấm nút **Xác nhận Xuất Kho**.
  6. Backend tiếp nhận request và bắt đầu một **Database Transaction**:
     * Áp dụng khóa bi quan with_for_update() trên dòng tồn kho của mặt hàng.
     * Kiểm tra điều kiện: Nếu TonKho.SoLuongTon < SoLuongXuat, lập tức thực hiện db.rollback() và trả về HTTP 400 Bad Request.
     * Nếu đủ tồn: Giảm tồn kho TonKho.SoLuongTon = TonKho.SoLuongTon - SoLuongXuat.
     * Tạo bản ghi PhieuXuat và ChiTietPhieuXuat.
     * Ghi Sổ Thẻ kho TheKho với LoaiGiaoDich = 'XUAT' và ghi nhận TonSauGiaoDich.
     * Thực hiện db.commit().
  7. Hệ thống thông báo thành công và trừ tồn kho ngay trên màn hình.
* **Luồng ngoại lệ (Alternative Flow - Vi phạm tồn âm):**
  * *4a. Người dùng nhập số lượng xuất vượt tồn khả dụng trên UI:* Ô nhập chuyển sang viền đỏ rực, badge LỖI TỒN ÂM xuất hiện và nút Xác nhận Xuất bị vô hiệu hóa (Disabled).
  * *6a. Yêu cầu gian lận hoặc xung đột đồng thời vượt tồn tại Backend:* Backend kích hoạt cơ chế Rollback, hủy toàn bộ giao dịch và trả về thông báo vi phạm toàn vẹn dữ liệu.

---

### 3.4. UC05: Tra Cứu Sổ Thẻ Kho Lũy Kế
* **Tác nhân:** Thủ kho, Kế toán, Admin.
* **Mục tiêu:** Kiểm tra lịch sử vào - ra của từng SKU để đối soát số lượng thực tế với sổ sách.
* **Luồng chính:**
  1. Người dùng chọn chức năng **Tra Cứu Thẻ Kho**.
  2. Chọn mặt hàng cần đối soát từ danh sách thả xuống.
  3. Bảng dữ liệu hiển thị toàn bộ lịch sử biến động theo trình tự thời gian tăng dần:
     * Ngày giờ giao dịch.
     * Mã chứng từ (Phiếu nhập PN-... hoặc Phiếu xuất PX-...).
     * Loại nghiệp vụ (Nhập kho màu xanh / Xuất kho màu tím).
     * Số lượng thay đổi ($+N$ hoặc $-N$).
     * **Số lượng tồn kho sau giao dịch.**

---

### 3.5. UC07: Tham Vấn Trợ Lý AI Gemini (Grounded Advisory)
* **Tác nhân:** Admin, Kế toán, Thủ kho.
* **Mục tiêu:** Nhận báo cáo phân tích rủi ro kho và gợi ý kế hoạch nhập hàng tự động.
* **Luồng chính:**
  1. Người dùng truy cập Dashboard hoặc gửi yêu cầu phân tích kho.
  2. Hệ thống thực hiện bước **Data Aggregator**: Tổng hợp số lượng tồn hiện tại, định mức tồn min, tốc độ xuất hàng trong kỳ.
  3. Hệ thống thực hiện bước **Data Sanitizer**: Lọc bỏ toàn bộ thông tin giá vốn, đơn giá nhập khẩu để bảo mật nội bộ.
  4. Đưa dữ liệu sạch vào mẫu **Grounded Prompting Template** có System Instruction nghiêm ngặt.
  5. Gửi request tới **Google Gemini 1.5 Flash API**.
  6. AI phân tích và trả về cấu trúc JSON gồm: Danh sách SKU chạm ngưỡng nguy hiểm, xu hướng xuất hàng và khuyến nghị bổ sung số lượng tối ưu.
  7. Hiển thị thông tin trực quan lên thẻ tư vấn AI trên Dashboard.

---

## 4. BIỂU ĐỒ TRÌNH TỰ (SEQUENCE DIAGRAMS)

### 4.1. Quy trình Xác thực Người dùng (UC01)
`
User (Browser)               FastAPI Backend             PostgreSQL Database
     |                              |                             |
     |---- 1. POST /auth/login ---->|                             |
     |   {username, password}       |---- 2. Query user --------->|
     |                              |<--- 3. User & Hash Pwd -----|
     |                              |                             |
     |                              |-- 4. bcrypt.checkpw()       |
     |                              |-- 5. create_access_token()  |
     |                              |                             |
     |<--- 6. 200 OK + Set-Cookie --|                             |
     |    (HttpOnly JWT Token)      |                             |
     |                              |                             |
     |---- 7. GET /dashboard ------>|                             |
     |<--- 8. Render Dashboard -----|                             |
`

### 4.2. Giao dịch Xuất kho Chống Tồn Âm ACID (UC04)
`
Thủ Kho (UI)                 FastAPI Service             Database (Transaction)
     |                              |                             |
     |---- 1. POST /phieu-xuat ---->|                             |
     |   {MaHH, SoLuongXuat}        |---- 2. BEGIN TRANSACTION -->|
     |                              |---- 3. SELECT FOR UPDATE -->|
     |                              |<--- 4. Current Stock (Ton) -|
     |                              |                             |
     |                              |-- 5. Check: Ton < Xuat?     |
     |                              |      [Nếu THIẾU TỒN]        |
     |                              |---- 6. ROLLBACK ----------->|
     |<--- 7. 400 Bad Request ------|                             |
     |    (Bảo vệ chống tồn âm)     |                             |
     |                              |      [Nếu ĐỦ TỒN]           |
     |                              |---- 8. UPDATE TonKho ------>|
     |                              |---- 9. INSERT PhieuXuat --->|
     |                              |---- 10. INSERT TheKho ----->|
     |                              |---- 11. COMMIT ------------>|
     |<--- 12. 201 Created ---------|                             |
     |    (Xuất kho thành công)     |                             |
`
