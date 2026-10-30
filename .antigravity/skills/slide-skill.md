Bạn là Technical Presentation Architect & Chuyên gia Thiết kế Slide Báo Cáo Đồ Án Tốt Nghiệp Kỹ Thuật Phần Mềm.

Hãy đọc và phân tích kỹ các tệp sau trong repository:

1. docs/SmartLogis_AI_Presentation_Deck.pptx (File trình chiếu hiện tại trong docs)
2. scripts/generate_presentation.py (Script Python chịu trách nhiệm dựng toàn bộ 15 slide của file pptx trên)
3. docs/HTD_NTH_KTPMK23A.docx và docs/database_design.md (Thuyết minh đồ án và thiết kế kỹ thuật)

Hiện tại, các slide trong presentation đang mắc phải các lỗi lớn:

- Quá nhiều chữ, các thẻ nhồi nhét dày đặc chữ khiến người xem bị ngợp và khó theo dõi khi trình chiếu.
- Sử dụng nhiều từ ngữ mang tính chất "quảng cáo / tiếp thị khởi nghiệp / cam kết bán hàng" không phù hợp với không khí học thuật và hội đồng bảo vệ kỹ thuật phần mềm (như: "cam kết bảo mật", "độc quyền", "triệu đô", "cam kết đầu ra 24/7", "thuyết phục hội đồng", "siêu việt").
- Thiếu sự cô đọng kỹ thuật của một đồ án công nghệ thông tin.

NHIỆM VỤ CỦA BẠN:
Tái cấu trúc và chỉnh sửa mã nguồn script `scripts/generate_presentation.py`, sau đó chạy script này để tạo lại file `docs/SmartLogis_AI_Presentation_Deck.pptx` với phong cách TỐI GIẢN - ÍT CHỮ - GIÀU THÔNG TIN KỸ THUẬT - DỄ THUYẾT TRÌNH THEO CÁC NGUYÊN TẮC SAU:

---

### I. THÔNG TIN CHUẨN XÁC CỦA ĐỒ ÁN & NHÂN SỰ

- Tên đề tài chính thức: HỆ THỐNG QUẢN LÝ KHO THÔNG MINH TÍCH HỢP AI (SMARTLOGIS AI)
- Loại hình: Báo Cáo Đồ Án Chuyên Ngành / Đồ Án Tốt Nghiệp Kỹ Thuật Phần Mềm (Khóa KTPMK23A - Thái Nguyên, 2026)
- Đội ngũ thực hiện (Mô hình Scrum 02 người):
  1. Nguyễn Thành Hưng: Product Owner (PO) kiêm Lead Backend Developer (Phụ trách kiến trúc CSDL, nghiệp vụ ACID, Atomic Decrement, Data Sanitizer và Gemini AI API)
  2. Hoàng Tiến Đạt: Scrum Master kiêm Frontend Developer & Tester (Phụ trách giao diện Jinja2/Tailwind, WebSocket Realtime, kiểm thử tự động Pytest và quy trình Scrum)

---

### II. CÁC NGUYÊN TẮC TINH CHỈNH TỔNG THỂ (CLEAN & MINIMALIST SLIDES)

1. Giảm 40% - 50% lượng chữ: Tuyệt đối không đưa các đoạn văn dài vào slide. Chuyển toàn bộ thành Bullet Points ngắn gọn (mỗi bullet từ 8 - 14 từ, tập trung vào keywords kỹ thuật).
2. Quy tắc "Slide để nhìn, Lời nói để giải thích": Slide chỉ giữ lại các cột mốc, công nghệ, con số định lượng, sơ đồ hoặc thuật toán. Chi tiết diễn giải chuyển toàn bộ vào `Speaker Notes` bên dưới.
3. Loại bỏ 100% từ ngữ quảng cáo / tiếp thị:
   - Xóa bỏ các cụm: "Cam kết an toàn tuyệt đối", "Độc quyền khử sạch", "Lãng phí hàng chục tỷ đồng", "Triệu đô", "Sẵn sàng triển khai thực tế", "Thuyết phục hội đồng".
   - Thay bằng thuật ngữ kỹ thuật khách quan: "Ràng buộc CheckConstraint", "Xử lý Concurrency & Race Condition", "Module Data Sanitizer", "Local Fallback Engine", "Quy trình Agile Scrum".
4. Giữ nguyên thẩm mỹ & Font chữ lớn:
   - Kích thước chữ to, dễ đọc trên máy chiếu phòng bảo vệ (Tiêu đề 26-28pt, thẻ 15-16pt, nội dung 13-14pt).
   - Tông màu chuyên nghiệp: Deep Navy (#0A192F), Royal Blue (#1E3A8A), Ice Blue (#F0F7FF) và Cyan Accent (#06B6D4).

---

### III. HƯỚNG DẪN CHI TIẾT TỪNG SLIDE (15 SLIDES)

- SLIDE 1 (Trang bìa - Hero Dark):
  - Badge trên cùng: "ĐỒ ÁN TỐT NGHIỆP • KỸ THUẬT PHẦN MỀM K23A" (Bỏ "PRODUCTION V4.0").
  - Tiêu đề lớn: HỆ THỐNG QUẢN LÝ KHO THÔNG MINH
  - Tiêu đề phụ: TÍCH HỢP TRÍ TUỆ NHÂN TẠO & BẢO TOÀN GIAO DỊCH ACID
  - Thông tin sinh viên rõ ràng: Nguyễn Thành Hưng (PO - Lead Backend) • Hoàng Tiến Đạt (Scrum Master - Frontend/Tester).
  - 3 Card chân trang ngắn gọn: (1) Giao Dịch ACID (Chống tồn âm 2 tầng), (2) Trí Tuệ Nhân Tạo (Google Gemini & Local Fallback), (3) Kiến Trúc Thực Tế (FastAPI, PostgreSQL & WebSocket).

- SLIDE 2 (Đặt Vấn Đề - Bối Cảnh Thực Tế):
  - Bỏ các câu chữ thổi phồng "Lãng phí hàng chục tỷ", "Nguy hiểm rò rỉ".
  - Chia 4 bài toán kỹ thuật cốt lõi:
    1. Lỗi tồn âm (Negative Stock) do Race Condition khi nhiều thủ kho thao tác đồng thời.
    2. Đứt gãy nguồn cung do thiếu cơ chế dự báo tốc độ xuất hàng ngày (Burn-rate).
    3. Ứ đọng hàng hóa (Dead Stock) do khó theo dõi thủ công các SKU nằm kho > 60 ngày.
    4. Nguy cơ lộ giá vốn khi gửi dữ liệu thô sang các dịch vụ Public Cloud LLM.

- SLIDE 3 (Mục Tiêu & Giải Pháp Đề Xuất):
  - Bỏ banner "CAM KẾT ĐẦU RA".
  - 3 Trụ cột giải pháp trọng tâm:
    1. Bảo toàn giao dịch: Loại bỏ tồn âm bằng Atomic SQL Decrement kết hợp DB Constraints.
    2. Hỗ trợ điều hành: Ứng dụng Gemini AI phân tích 3 phần (Tổng quan, Tồn cạn kiệt, Hàng ứ đọng).
    3. Bảo mật dữ liệu: Lọc sạch 100% trường giá nhập trước khi nạp context cho AI Model.

- SLIDE 4 (Kiến Trúc Hệ Thống - Phân Tầng):
  - 4 Tầng kiến trúc Clean & Rõ ràng:
    1. Presentation: Jinja2 SSR, Tailwind CSS, Native WebSocket Client.
    2. Security & Auth: JWT Cookie HTTPOnly, Bcrypt 72-byte, Header X-Session-User (Tab Isolation).
    3. Core Business & AI: FastAPI Services, Atomic Transactions, Google Gemini Client & Grounded Fallback.
    4. Database: Dual DB (SQLite WAL / PostgreSQL 15), SQLAlchemy 2.0 ORM, 8 B-Tree Indexes.

- SLIDE 5 (Thiết Kế CSDL - 11 Bảng Chuẩn Hóa):
  - Tinh giản text, chia 2 khối:
    - Khối 1: Chuẩn hóa 3NF, phân tách Master-Detail (phieu_nhap / phieu_xuat), bảo toàn sổ cái Thẻ kho lũy kế (the_kho).
    - Khối 2: Tối ưu hóa truy vấn với 8 B-Tree Indexes và Hardware CheckConstraints (SoLuongTon >= 0, TonSauGiaoDich >= 0).

- SLIDE 6 (Kỹ Thuật Cốt Lõi 1 - Atomic SQL Decrement):
  - Trình bày rõ nguyên lý: Backend thực thi UPDATE với điều kiện `SoLuongTon >= :so_luong_xuat`.
  - Nếu `rowcount == 0` -> Rollback ngay lập tức và trả về HTTP 400.
  - Trưng bày đoạn mã SQL cốt lõi và kết quả kiểm thử Concurrency Test đồng thời không phát sinh sai lệch.

- SLIDE 7 (Kỹ Thuật Cốt Lõi 2 - Quy Trình Nghiệp Vụ & Phân Quyền RBAC):
  - Bảng ma trận 3 vai trò súc tích:
    - Admin: Toàn quyền cấu hình, tài khoản, danh mục, chứng từ, báo cáo AI.
    - Thủ kho (kiêm Kế toán): Lập phiếu xuất/nhập ACID, tra cứu thẻ kho, xuất file Excel.
    - Nhân viên kho (Staff): Quyền chỉ đọc (Read-only) tra cứu tồn và sổ thẻ kho; chặn lập chứng từ và sửa dữ liệu.

- SLIDE 8 (Tích Hợp AI 1 - Data Sanitizer Khử Nhạy Cảm):
  - Bỏ các từ "độc quyền", "cam kết an toàn".
  - Giải thích cơ chế lọc đệ quy `sanitize_inventory_payload()`: Quét và loại bỏ triệt để danh sách đen (`DonGiaNhap`, `ThanhTien`, `GiaVon`, `cost_price`).
  - Cung cấp endpoint audit minh bạch: `GET /api/v1/ai/raw-context`.

- SLIDE 9 (Tích Hợp AI 2 - Prompt Engineering & Báo Cáo 3 Phần):
  - Cấu trúc báo cáo điều hành chuẩn hóa 3 phần:
    - Phần 1: Tình trạng tồn kho tổng quan.
    - Phần 2: Đề xuất nhập hàng khẩn cấp dựa trên tốc độ tiêu thụ (Burn-rate).
    - Phần 3: Cảnh báo hàng bất thường & Dead Stock (> 60 ngày không xuất).
  - System Instruction chống ảo giác (Anti-hallucination) nghiêm ngặt chỉ dựa trên dữ liệu JSON thực tế.

- SLIDE 10 (Tích Hợp AI 3 - Local Grounded Fallback Engine):
  - Giải thuật dự phòng ngoại tuyến: Khi mất mạng, chưa có API Key hoặc gặp lỗi 429 (Rate Limit Quota).
  - Tự động kích hoạt Fallback Engine phân tích trực tiếp từ CSDL, đảm bảo hệ thống không bị crash (Zero Crash).

- SLIDE 11 (Quy Trình Phát Triển Phần Mềm - Agile Scrum):
  - Phản ánh trung thực quy trình của nhóm 2 người qua 4 Sprint:
    - Sprint 1: Phân hệ Quản trị Kho & Giao dịch ACID Chống Tồn Âm.
    - Sprint 2: Phân hệ Trợ lý AI Gemini, Data Sanitizer & Báo cáo 3 phần.
    - Sprint 3: Đồng bộ WebSocket Realtime Đa Thiết Bị, Phân quyền RBAC & Giao diện.
    - Sprint 4: Kiểm thử tự động Pytest, Đóng gói Docker & Hoàn thiện tài liệu nghiệm thu.

- SLIDE 12 (Đảm Bảo Chất Lượng - Kiểm Thử Tự Động):
  - Cập nhật con số thực tế trong repository: Bộ kiểm thử tự động với 65+ Test Cases (Pytest) bao phủ 100% các phân hệ (ACID, Concurrency Race Condition, Ledger Sync, RBAC, Data Sanitizer, WebSocket).

- SLIDE 13 (Đóng Gói Triển Khai & Khả Năng Đồng Bộ Đa Thiết Bị):
  - Mô hình Nginx Reverse Proxy (Port 80/443 SSL) định tuyến tới FastAPI và PostgreSQL.
  - Hỗ trợ truy cập mạng LAN/Wi-Fi đa thiết bị (Máy tính bàn, Laptop, Điện thoại di động, Máy tính bảng) kết nối thời gian thực qua WebSocket.

- SLIDE 14 (Kịch Bản Thực Nghiệm Demo):
  - Tinh giản kịch bản 5 bước demo trong 5 phút mạch lạc:
    1. Đăng nhập & Bảng điều khiển KPI thời gian thực.
    2. Trợ lý AI tư vấn Burn-rate và Báo cáo 3 phần.
    3. Thử nghiệm xuất vượt tồn kho (Kiểm chứng rào chắn Chống Tồn Âm).
    4. Lập phiếu nhập kho & Kiểm tra sổ Thẻ kho tự động đồng bộ.
    5. Kiểm toán dữ liệu sạch qua API /raw-context.

- SLIDE 15 (Tổng Kết & Định Hướng Phát Triển - Hero Dark):
  - Kết quả đạt được: Hoàn thành 100% mục tiêu đề tài, hệ thống hoạt động ổn định, bảo toàn dữ liệu ACID và tích hợp AI an toàn.
  - Hướng phát triển tương lai: Xây dựng ứng dụng di động Native (Flutter/React Native), tích hợp quét mã QR/RFID kiểm kê kho tự động.
  - Lời cảm ơn chân thành tới Quý Thầy/Cô trong Hội đồng đánh giá.

---

### IV. THỰC HIỆN VÀ BÀN GIAO:

1. Sửa đổi trực tiếp tệp `scripts/generate_presentation.py` bằng mã nguồn Python `python-pptx` chuẩn xác, tối ưu hóa text frames và speaker notes.
2. Chạy lệnh: `python scripts/generate_presentation.py` để biên dịch ra file PowerPoint hoàn chỉnh mới: `docs/SmartLogis_AI_Presentation_Deck.pptx`.
3. Kiểm tra thông báo hoàn thành và báo cáo tóm tắt các điểm đã được tinh gọn.
