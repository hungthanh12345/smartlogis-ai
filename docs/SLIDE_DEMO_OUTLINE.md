# ĐỀ CƯƠNG SLIDE THUYẾT TRÌNH BẢO VỆ ĐỒ ÁN (SMARTLOGIS AI)

**Đề tài:** Hệ Thống Quản Lý Kho Thông Minh Tích Hợp AI & Giao Dịch ACID (SmartLogis AI)  
**Thời lượng trình bày:** 15 - 20 phút  
**Cấu trúc bài thuyết trình:** 12 Slide chuẩn mực theo tiến trình kỹ thuật phần mềm.

---

## SLIDE 1: GIỚI THIỆU ĐỀ TÀI & THÀNH VIÊN
- **Tiêu đề:** SMARTLOGIS AI - GIẢI PHÁP QUẢN LÝ KHO THÔNG MINH TÍCH HỢP AI & BẢO TOÀN GIAO DỊCH ACID
- **Phụ đề:** Ứng dụng Quản lý Kho Vận Vật Tư & Thiết Bị Công Trình Xây Dựng
- **Thành viên thực hiện:** Đội ngũ Kỹ sư Công nghệ Dự án SmartLogis AI
- **Giảng viên hướng dẫn:** Ban Giám khảo / Hội đồng Chấm Đồ án
- **Điểm nhấn cốt lõi:** *"Không chỉ số hóa kho hàng truyền thống, SmartLogis AI mang đến sự an toàn tuyệt đối với ACID Concurrency Control và sức mạnh cố vấn chiến lược từ Google Gemini LLM."*

---

## SLIDE 2: THỰC TRẠNG & NỖI ĐAU TRONG QUẢN LÝ KHO TRUYỀN THỐNG
- **Vấn đề 1 - Lỗi Tồn Kho Âm (Lost Update / Race Condition):** Khi nhiều thủ kho cùng xuất 1 mặt hàng cùng lúc, hệ thống không khóa dòng dẫn đến xuất vượt số lượng có sẵn trong kho.
- **Vấn đề 2 - Đứt gãy chuỗi cung ứng:** Hàng chạm ngưỡng hết sạch mới phát hiện, không kịp đặt hàng nhà cung cấp làm đình trệ công trình.
- **Vấn đề 3 - Đọng vốn (Dead Stock):** Hàng chục SKU vật tư giá trị cao nằm lưu kho trên 60 ngày không luân chuyển mà quản lý không hay biết.
- **Vấn đề 4 - Nguy cơ lộ giá vốn bí mật:** Đưa dữ liệu tài chính nhạy cảm lên AI công cộng gây rủi ro lộ bí mật kinh doanh.

---

## SLIDE 3: MỤC TIÊU & GIẢI PHÁP SMARTLOGIS AI
- **100% Zero Negative Stock:** Loại bỏ hoàn toàn tồn âm bằng cơ chế bảo vệ kép 2 tầng.
- **Trợ lý AI Điều Hành (Google Gemini):**
  - Tự động tính toán tốc độ tiêu thụ hàng ngày (**Burn-rate**).
  - Cảnh báo và đề xuất số lượng nhập hàng khẩn cấp.
  - Tự động phát hiện hàng ứ đọng > 60 ngày.
- **Data Sanitizer Độc Quyền:** Lọc bỏ 100% giá vốn nhạy cảm trước khi nạp cho AI.
- **Sẵn sàng Vận hành (Production-Ready):** Kiến trúc FastAPI hiện đại, đóng gói Docker 1-click.

---

## SLIDE 4: KIẾN TRÚC CÔNG NGHỆ TỔNG THỂ (TECH STACK)
- **Backend Core:** Python 3.12, FastAPI (Asynchronous Framework), Uvicorn ASGI Server.
- **Database Layer:** SQLAlchemy 2.0 ORM, SQLite WAL Mode (Zero-setup) / PostgreSQL 15 (Enterprise).
- **AI & LLM Integration:** Google Gemini API (`gemini-3.5-flash-lite`, `gemini-3.6-flash`), REST Client với Exponential Backoff Retry.
- **Frontend & UI:** Jinja2 Server-Side Rendering, Tailwind CSS, FontAwesome 6, Chart.js.
- **DevOps & Testing:** Docker, Docker Compose, Pytest (12/12 test cases Passed).

---

## SLIDE 5: MÔ HÌNH CSDL & KIỂM SOÁT TOÀN VẸN ACID
- **Thiết kế CSDL Chuẩn Hóa 3NF:** 10 thực thể liên kết chặt chẽ (Người dùng, Hàng hóa, Tồn kho, Nhà cung cấp, Phiếu nhập, Phiếu xuất, Thẻ kho).
- **Tối ưu B-Tree Indexes:** Đánh 8 chỉ mục trên các khóa ngoại và cột lọc ngày tháng giúp truy vấn 30 ngày trong vài mili-giây.
- **Ràng buộc Phần cứng CSDL (Hardware Integrity):**
  - `CHECK (SoLuongTon >= 0)`
  - `CHECK (SoLuongXuat > 0)` & `CHECK (SoLuongNhap > 0)`
  - SQLite Triggers dự phòng chống can thiệp trực tiếp từ bên ngoài.

---

## SLIDE 6: GIẢI PHÁP KỸ THUẬT 1 - CHỐNG TỒN KHO ÂM & RACE CONDITION
- **Phân tích lỗi Race Condition:** Đọc bộ nhớ Python rồi trừ số lượng dẫn đến Lost Update.
- **Giải pháp Atomic SQL Decrement:**
  ```sql
  UPDATE ton_kho 
  SET SoLuongTon = SoLuongTon - :qty, CapNhatCuoi = :now 
  WHERE MaHH = :ma_hh AND SoLuongTon >= :qty;
  ```
- **Cơ chế Rollback nguyên tử:** Nếu `rowcount == 0` (hết hàng tại thời điểm ghi), CSDL lập tức hủy bỏ toàn bộ chứng từ Master-Detail và trả về HTTP 400 rõ ràng.
- **Minh chứng kiểm thử:** Bài test đa luồng `ThreadPoolExecutor` chứng minh tồn kho không bao giờ bị âm.

---

## SLIDE 7: GIẢI PHÁP KỸ THUẬT 2 - AI DATA SANITIZER & BẢO MẬT GIÁ VỐN
- **Nguyên tắc "Zero Financial Leakage":** Bí mật kinh doanh là ưu tiên số 1.
- **Bộ lọc Khử nhạy cảm đệ quy (Data Sanitizer):**
  - Quét sạch các trường `dongianhap`, `thanhtien`, `gia_von`, `import_price`...
- **Dữ liệu Context gửi cho AI chỉ bao gồm:**
  - Mã hàng, Tên hàng, Đơn vị tính, Nhóm hàng.
  - Số lượng tồn hiện tại, Tồn tối thiểu.
  - Tốc độ xuất bình quân 30 ngày (Burn-rate).
  - Số ngày không xuất hàng.
- **Kiểm toán bảo mật:** Endpoint `GET /api/v1/ai/raw-context` chứng minh dữ liệu nạp cho AI an toàn 100%.

---

## SLIDE 8: GIẢI PHÁP KỸ THUẬT 3 - PROMPT CHỐNG ẢO GIÁC & FALLBACK ENGINE
- **System Prompt Chống Ảo Giác (Strict Anti-hallucination):**
  - Ép AI chỉ suy luận dựa trên JSON cung cấp.
  - Thông báo rỗng khi kho chưa có giao dịch.
- **Quy chuẩn Báo cáo Điều hành 3 Phần:**
  - *Phần 1:* Tình trạng tồn kho tổng quan.
  - *Phần 2:* Cảnh báo & Đề xuất nhập hàng khẩn cấp.
  - *Phần 3:* Biến động bất thường (Xuất đột biến & Dead stock > 60 ngày).
- **Local Grounded Fallback Engine:**
  - Khi Gemini API gặp mã 429 Quota hoặc mất mạng, engine nội bộ tự động phân tích số liệu thực tế, đảm bảo ứng dụng không bao giờ bị gián đoạn.

---

## SLIDE 9: GIAO DIỆN NGƯỜI DÙNG & LUỒNG NGHIỆP VỤ CỐT LÕI
- **Dashboard v2.0:**
  - 4 Thẻ KPIs tổng quan.
  - Bảng cảnh báo tồn min phân màu (Đỏ nguy cấp / Vàng cận ngưỡng).
  - Khối Gemini AI Widget hiển thị khuyến nghị trực tiếp.
- **Màn hình Xuất kho Thời gian thực (Outbound):**
  - Real-time client validation: Tự động highlight đỏ dòng thiếu hàng, hiển thị badge âm tồn và khóa nút xác nhận.
- **Màn hình Nhập kho (Inbound):**
  - Bảng động thêm dòng, tính thành tiền và lưu master-detail.
- **Tra cứu Thẻ kho (Stock Card):**
  - Xem dòng tiền và lịch sử xuất nhập theo từng mặt hàng.

---

## SLIDE 10: CHIẾN LƯỢC KIỂM THỬ TỰ ĐỘNG (AUTOMATED TESTING)
- **Phương pháp tiếp cận:** TDD & Regression Testing với `pytest`.
- **Tổng số 12 Test Cases bao phủ toàn diện:**
  - *Kiểm thử AI:* Kho rỗng, Đề xuất nhập tồn min, Khử giá nhập, Mocking Gemini & Fallback 429.
  - *Kiểm thử Giao dịch:* Nhập kho ACID, Chặn tồn âm, Concurrency Race condition đa luồng.
  - *Kiểm thử Phân quyền:* Ma trận RBAC cho Admin, Thủ kho, Kế toán.
  - *Kiểm thử Tích hợp:* CRUD SKU, APIs danh mục, Xuất báo cáo Excel.
- **Kết quả nghiệm thu:** **12/12 Test Cases PASSED (100%)** trong thời gian 40 giây.

---

## SLIDE 11: KỊCH BẢN LIVE DEMO 5 PHÚT (BẢO VỆ ĐỒ ÁN)
1. **Phút 1:** Đăng nhập 1-click Thủ kho -> Trình diễn Dashboard & KPIs.
2. **Phút 2:** Bấm nút **"Báo cáo 3 phần"** trên AI Widget -> Trình diễn phân tích từ Google Gemini Live API.
3. **Phút 3:** Thử nghiệm xuất vượt tồn kho Thép D10 -> Giao diện chặn xuất, Backend ném 400 Bad Request chống tồn âm.
4. **Phút 4:** Lập phiếu nhập kho thành công -> Kiểm tra Thẻ kho cập nhật số dư tức thời.
5. **Phút 5:** Mở Swagger `/docs` -> Gọi `/api/v1/ai/raw-context` chứng minh dữ liệu sạch 100% không lộ giá vốn.

---

## SLIDE 12: ĐÁNH GIÁ KẾT QUẢ & HƯỚNG PHÁT TRIỂN
- **Kết quả đạt được:**
  - Đạt 100% mục tiêu của 4 giai đoạn đồ án.
  - Hệ thống vận hành mượt mà, sẵn sàng demo thực tế.
  - Đóng gói Docker và scripts khởi chạy 1-click trên mọi hệ điều hành.
- **Hướng phát triển tiếp theo:**
  - Tích hợp mô hình chuỗi thời gian (ARIMA/Prophet) dự báo nhu cầu theo mùa vụ.
  - Xây dựng bản đồ định vị vị trí kho thông minh (Smart Bin Location).
  - Ứng dụng di động quét mã vạch (Barcode Scanner) cho thủ kho tại hiện trường.
- **Lời cảm ơn:** Trân trọng cảm ơn Thầy/Cô và Hội đồng đã lắng nghe bài thuyết trình!

---

<div align="center">
  <b>HẾT BÀI THUYẾT TRÌNH - SẴN SÀNG TRẢ LỜI CÂU HỎI PHẢN BIỆN TỪ HỘI ĐỒNG!</b>
</div>
