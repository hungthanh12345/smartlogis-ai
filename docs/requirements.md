# ĐẶC TẢ YÊU CẦU HỆ THỐNG (SYSTEM REQUIREMENTS SPECIFICATION)
## DỰ ÁN: HỆ THỐNG QUẢN LÝ KHO TÍCH HỢP AI (SMARTLOGIS AI V2.0)

---

### THÔNG TIN DỰ ÁN
* **Đơn vị đào tạo:** Trường Đại học Công nghệ Thông tin & Truyền thông (ICTU) - Khoa Công nghệ Thông tin
* **Học phần:** Ứng dụng Trí tuệ Nhân tạo trong Phát triển Phần mềm
* **Nhóm thực hiện:** Nhóm 07
  * **Hoàng Tiến Đạt (# Nhóm trưởng):** Scrum Master / Frontend & QA Engineer
  * **Nguyễn Thành Hưng:** Product Owner / Lead Backend Developer
* **Giảng viên hướng dẫn:** TS. Nguyễn Thị Tuyển
* **Công nghệ cốt lõi:** Python, FastAPI, SQLAlchemy ORM, PostgreSQL, Tailwind CSS, Google Gemini 1.5 Flash

---

## 1. TỔNG QUAN & MỤC TIÊU DỰ ÁN

### 1.1. Đặt vấn đề
Các hệ thống quản lý kho truyền thống thường gặp các thách thức nghiêm trọng:
1. **Lỗi tồn kho âm (Negative Stock):** Do thiếu cơ chế Transaction locking, khi có nhiều yêu cầu xuất hàng đồng thời, hệ thống ghi nhận xuất vượt quá số lượng thực tế trong kho, làm sai lệch báo cáo kế toán.
2. **Thiếu cảnh báo chủ động:** Không kịp thời phát hiện các mặt hàng sắp hết hoặc chạm ngưỡng tồn kho tối thiểu (*Safety Stock*), dẫn đến đình trệ sản xuất / kinh doanh.
3. **Phân tích thủ công:** Việc phân tích xu hướng nhập - xuất và lập kế hoạch đặt hàng tốn nhiều giờ làm việc của thủ kho và kế toán, dễ xảy ra sai sót chủ quan.

### 1.2. Mục tiêu hệ thống
* Xây dựng hệ thống quản lý kho hoàn chỉnh, bảo đảm **tính toàn vẹn dữ liệu tuyệt đối (100% ACID)**, triệt tiêu hoàn toàn lỗi tồn kho âm.
* Tích hợp **Trợ lý AI Gemini** phân tích thông minh dựa trên kỹ thuật **Grounded Prompting**, tự động đưa ra khuyến nghị bổ sung hàng hóa chính xác mà không làm lộ dữ liệu tài chính nhạy cảm.
* Cung cấp giao diện trực quan, tốc độ xử lý tức thời (< 100ms), chuẩn hóa biểu mẫu thẻ kho và hỗ trợ xuất báo cáo.

---

## 2. YÊU CẦU CHỨC NĂNG (FUNCTIONAL REQUIREMENTS - FR)

### FR1: Phân hệ Xác thực & Phân quyền người dùng (Auth Module)
* **FR1.1:** Đăng nhập hệ thống bằng Tên đăng nhập và Mật khẩu. Mật khẩu được mã hóa một chiều bằng thuật toán **Bcrypt Hash**.
* **FR1.2:** Cấp mã định danh **JWT (JSON Web Token)** với hạn sử dụng và lưu trữ an toàn qua HttpOnly Cookie.
* **FR1.3:** Phân quyền truy cập dựa trên 3 vai trò (RBAC):
  * **Admin (Quản trị viên):** Toàn quyền cấu hình, quản lý người dùng, xem toàn bộ báo cáo và cấu hình AI.
  * **Thủ kho:** Quản lý danh mục hàng hóa, lập phiếu nhập kho, phiếu xuất kho, theo dõi thẻ kho.
  * **Kế toán:** Tra cứu lịch sử thẻ kho lũy kế, đối soát số liệu, xem cảnh báo tồn và xuất báo cáo.
* **FR1.4:** Cho phép đăng ký tài khoản mới và đăng xuất an toàn (thu hồi phiên làm việc tức thì).

### FR2: Phân hệ Quản lý Danh mục Kho (Master Data)
* **FR2.1:** Quản lý nhóm hàng hóa, đơn vị tính chuẩn (Cuộn, Cây, Bao, Thùng, Hộp...).
* **FR2.2:** Quản lý đối tác Nhà cung cấp (Tên công ty, địa chỉ, số điện thoại liên hệ, email).
* **FR2.3:** Quản lý thông tin chi tiết từng mặt hàng: Mã hàng (SKU), Tên hàng hóa, Định mức tồn tối thiểu (*TonToiThieu*).

### FR3: Phân hệ Quản lý Nhập Kho (Inbound Management)
* **FR3.1:** Khởi tạo Phiếu nhập kho (*Inbound Voucher*) liên kết với Nhà cung cấp và người lập phiếu.
* **FR3.2:** Thêm nhiều mặt hàng trong cùng một phiếu nhập (quan hệ Master - Detail).
* **FR3.3:** Xử lý giao dịch nhập kho trong một **Database Transaction** nguyên tử:
  * Tự động cộng tăng số lượng tồn kho khả dụng (TonKho.SoLuongTon).
  * Tự động ghi nhận một bản ghi giao dịch mới vào Sổ Thẻ kho (TheKho) với loại giao dịch NHAP.

### FR4: Phân hệ Quản lý Xuất Kho & Phòng Tỏa Tồn Âm (Outbound & Anti-Negative Stock)
* **FR4.1:** Lập Phiếu xuất kho (*Outbound Voucher*) ghi rõ người nhận, bộ phận và lý do xuất kho.
* **FR4.2:** Tích hợp kiểm tra thời gian thực (*Real-time Validation*) trên giao diện: Cảnh báo đỏ và vô hiệu hóa nút xuất nếu số lượng nhập vượt tồn kho khả dụng.
* **FR4.3:** **Bảo vệ 2 lớp tại tầng Backend:**
  * **Lớp 1 - Khóa bi quan (Pessimistic Locking):** Sử dụng câu lệnh SELECT ... FOR UPDATE khóa bản ghi tồn kho trong suốt thời gian xử lý giao dịch xuất.
  * **Lớp 2 - Ràng buộc CSDL (Check Constraint):** Thiết lập CHECK (SoLuongTon >= 0). Nếu số lượng xuất vượt tồn, giao dịch lập tức bị ROLLBACK và ném lỗi HTTP 400 Bad Request.
* **FR4.4:** Khi xuất thành công, tự động trừ số lượng tồn và ghi nhận vào Sổ Thẻ kho loại giao dịch XUAT.

### FR5: Phân hệ Sổ Thẻ Kho & Cảnh Báo Tồn Min
* **FR5.1:** Tra cứu dòng lịch sử biến động kho theo từng mặt hàng theo thứ tự thời gian.
* **FR5.2:** Thể hiện rõ ràng: Ngày giao dịch, Mã chứng từ đối soát, Loại giao dịch (Nhập/Xuất), Số lượng thay đổi và **Tồn kho lũy kế sau giao dịch**.
* **FR5.3:** Cảnh báo các mặt hàng có số lượng tồn hiện tại $\le$ định mức tồn tối thiểu trên Dashboard.

### FR6: Phân hệ Trợ lý AI Phân tích & Tư vấn (Gemini Advisory)
* **FR6.1:** Tự động tổng hợp dữ liệu kho (*Data Aggregator*) và làm sạch dữ liệu (*Data Sanitizer*) loại bỏ đơn giá vốn mua hàng nhạy cảm.
* **FR6.2:** Đóng gói dữ liệu vào mẫu câu lệnh chuẩn (*Grounded Prompting*) gửi đến Google Gemini API.
* **FR6.3:** Trả về bảng phân tích xu hướng nhập - xuất, phát hiện biến động bất thường và khuyến nghị kế hoạch đặt hàng dự phòng.

---

## 3. YÊU CẦU PHI CHỨC NĂNG (NON-FUNCTIONAL REQUIREMENTS - NFR)

### NFR1: Tính toàn vẹn dữ liệu & Tính nhất quán (Data Integrity)
* Tuân thủ 100% nguyên lý **ACID (Atomicity, Consistency, Isolation, Durability)**. Không để xảy ra hiện tượng dữ liệu rác (*dirty data*) khi hệ thống gặp sự cố mạng hoặc lỗi runtime.

### NFR2: Bảo mật & Quyền riêng tư (Security & Privacy)
* Dữ liệu mật khẩu người dùng không bao giờ được lưu trữ dưới dạng văn bản rõ (*plain text*).
* Token xác thực được lưu dưới cờ HttpOnly và SameSite=Lax để ngăn chặn triệt để tấn công XSS và CSRF.
* **Bảo mật giá vốn với AI:** Dữ liệu đơn giá mua vào của Nhà cung cấp được khử trùng (*Sanitized*) trước khi gửi tới API bên ngoài.

### NFR3: Hiệu năng & Khả năng mở rộng (Performance & Scalability)
* Thời gian phản hồi API trung bình dưới **50ms**, giao dịch nhập/xuất kho dưới **150ms**.
* Kiến trúc tách biệt tầng Controller (Router), Service (Business Logic) và Repository (ORM Model).

### NFR4: Giao diện & Trải nghiệm người dùng (UI/UX)
* Giao diện Responsive thiết kế theo Wireframe v2.0 chuẩn Bootstrap/Tailwind.
* Tối ưu hiển thị phông chữ tiếng Việt với typography Be Vietnam Pro.

---

## 4. PHẠM VI DỰ ÁN (PROJECT SCOPE)

### 4.1. Trong phạm vi (In-Scope)
* Quản trị kho đơn cơ sở (Single Warehouse).
* Quản lý Master Data: Hàng hóa, Nhóm hàng, Đối tác Nhà cung cấp.
* Giao dịch Nhập kho, Xuất kho có kiểm soát tồn âm bằng Transaction ACID.
* Tra cứu Sổ Thẻ kho lũy kế.
* Tích hợp Trợ lý AI Gemini phân tích cảnh báo tồn tối thiểu.
* Xác thực JWT đa vai trò: Admin, Thủ kho, Kế toán.

### 4.2. Ngoài phạm vi (Out-of-Scope)
* Quản lý luân chuyển đa kho (Multi-warehouse transfer) - *Dành cho giai đoạn phát triển mở rộng*.
* Tích hợp phần cứng quét mã vạch RFID/Barcode trực tiếp qua máy quét công nghiệp.
* Hạch toán kế toán chuyên sâu (LIFO/FIFO chi tiết giá vốn bình quân gia quyền theo lô).
