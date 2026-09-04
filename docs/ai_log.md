# NHẬT KÝ ỨNG DỤNG TRÍ TUỆ NHÂN TẠO (AI INTEGRATION & DEVELOPMENT LOG)
## DỰ ÁN: HỆ THỐNG QUẢN LÝ KHO TÍCH HỢP AI (SMARTLOGIS AI V2.0)

---

## 1. MỤC TIÊU & ĐỊNH HƯỚNG ỨNG DỤNG AI

Trong đề tài **SmartLogis AI**, Trí tuệ Nhân tạo không chỉ được ứng dụng ở giai đoạn phát triển mã nguồn (AI-assisted Coding) mà còn được tích hợp trực tiếp như một **phân hệ nghiệp vụ cốt lõi (Core Business Module)**.

### 1.1. Bài toán thực tế giải quyết
1. **Quá tải dữ liệu báo cáo:** Hàng ngày kho phát sinh hàng chục giao dịch xuất/nhập, thủ kho và kế toán không đủ thời gian để rà soát thủ công từng mã hàng có nguy cơ thiếu hụt.
2. **Nguy cơ đứt gãy chuỗi cung ứng:** Khi các mặt hàng chiến lược (thép, xi măng, sơn...) chạm ngưỡng tồn tối thiểu, nếu không đặt hàng kịp thời sẽ gây đình trệ toàn bộ dự án xây dựng.
3. **Bảo mật dữ liệu kinh doanh:** Cần tận dụng sức mạnh phân tích của mô hình ngôn ngữ lớn (LLM) nhưng tuyệt đối không được để lộ giá vốn mua hàng nhạy cảm của doanh nghiệp ra dịch vụ Cloud công cộng.

---

## 2. LỰA CHỌN MÔ HÌNH & KIẾN TRÚC TÍCH HỢP

### 2.1. Mô hình lựa chọn: Google Gemini 1.5 Flash
* **Lý do lựa chọn:**
  * Cửa sổ ngữ cảnh (Context Window) lớn, tốc độ phản hồi cực nhanh (< 1.5 giây), chi phí tối ưu.
  * Hỗ trợ Structured Outputs (JSON Schema) và khả năng tuân thủ System Instruction xuất sắc.
  * Tích hợp native thông qua thư viện chính thức google-genai / SDK Python.

### 2.2. Kiến trúc 3 tầng tích hợp AI (AI Pipeline Architecture)

`
[ CƠ SỞ DỮ LIỆU KHO (PostgreSQL) ]
                |
                v  (Bước 1: Trích xuất số liệu thô)
[ 1. DATA AGGREGATOR SERVICE ]
  - Tổng hợp tồn kho hiện tại
  - Định mức tồn tối thiểu
  - Tần suất xuất hàng trong kỳ
                |
                v  (Bước 2: Lọc bỏ giá vốn nhạy cảm)
[ 2. DATA SANITIZER (BẢO MẬT) ]
  - XÓA BỎ: DonGiaNhap, GiaVon, ThongTinThuongLuong
  - GIỮ LẠI: MaHH, TenHH, SoLuongTon, TonToiThieu, MaDVT
                |
                v  (Bước 3: Neo dữ liệu & Chống ảo giác)
[ 3. GROUNDED PROMPTING ENGINE ]
  - System Instruction ép tuân thủ số liệu thật
  - Cung cấp Context cụ thể của kỳ báo cáo
                |
                v  (Gửi HTTPS Request)
[ GOOGLE GEMINI 1.5 FLASH API ]
                |
                v  (Trả về JSON phân tích)
[ GIAO DIỆN DASHBOARD ADVISORY & BÁO CÁO ĐIỀU HÀNH ]
`

---

## 3. THIẾT KẾ KỸ THUẬT PROMPT (GROUNDED PROMPTING)

### 3.1. Cơ chế Data Sanitizer (Khử trùng dữ liệu giá vốn)
Hàm sanitize_inventory_data_for_ai() trong pp/services/ai_service.py đảm bảo chỉ truyền thông tin định lượng, không truyền thông tin tài chính nhạy cảm:
`python
def sanitize_inventory_data_for_ai(items_data: list) -> list:
    clean_data = []
    for item in items_data:
        clean_data.append({
             sku: item[MaHH],
            name: item[TenHH],
            unit: item[TenDVT],
            current_stock: item[SoLuongTon],
            safety_stock: item[TonToiThieu],
            is_critical: item[SoLuongTon] <= item[TonToiThieu]
        })
    return clean_data
`

### 3.2. Mẫu System Instruction & Grounded Prompt Template
`
[SYSTEM INSTRUCTION]
Bạn là Chuyên gia Cố vấn Quản trị Chuỗi cung ứng và Tồn kho (Chief Supply Chain Officer AI).
Nhiệm vụ của bạn là phân tích dữ liệu tồn kho thực tế được cung cấp bên dưới và đưa ra khuyến nghị bổ sung hàng hóa.

NGUYÊN TẮC BẮT BUỘC (GROUNDING RULES):
1. CHỈ sử dụng dữ liệu được cung cấp trong CONTEXT. Tuyệt đối KHÔNG tự ý suy diễn hoặc bịa đặt số liệu tồn kho.
2. KHÔNG đề cập đến giá mua hoặc ước tính giá vốn (đã bị loại bỏ vì lý do bảo mật).
3. Đưa ra khuyến nghị cụ thể: Mặt hàng nào cần nhập ngay, số lượng khuyến nghị bổ sung (đưa tồn về mức an toàn gấp 1.5 - 2 lần tồn tối thiểu).
4. Phản hồi bằng tiếng Việt chuyên nghiệp, cấu trúc rõ ràng gồm: Tóm tắt rủi ro, Danh sách mặt hàng báo động đỏ, và Kế hoạch hành động cụ thể.
`

---

## 4. NHẬT KÝ THỬ NGHIỆM & ĐÁNH GIÁ (EVALUATION LOG)

### 4.1. Thử nghiệm 1: Khả năng bảo mật giá vốn (Sanitizer Verification)
* **Mục tiêu:** Đảm bảo không có trường DonGia hay TongTien nào bị rò rỉ vào payload gửi tới API.
* **Phương pháp kiểm thử:** Phân tích payload bằng Unit Test tự động trước khi gửi request.
* **Kết quả:** **ĐẠT (PASS 100%)**. Toàn bộ thuộc tính tài chính nhạy cảm được gỡ bỏ hoàn toàn ở tầng Memory trước khi đóng gói Prompt.

### 4.2. Thử nghiệm 2: Chống hiện tượng ảo giác số liệu (Anti-Hallucination)
* **Tình huống thử nghiệm:** Cung cấp danh sách 15 mặt hàng, trong đó có 9 mặt hàng có số tồn $\le$ định mức an toàn.
* **Kết quả từ Gemini:**
  * AI nhận diện chính xác /9$ mặt hàng cần cảnh báo (đúng mã SKU và tên mặt hàng).
  * Số lượng khuyến nghị bổ sung dựa trên công thức toán học logic: \ nghị = (Tồn\ tối\ thiểu \times 2) - Tồn\ hiện\ tại$.
  * Không xuất hiện bất kỳ mặt hàng nào ngoài danh mục được cung cấp.

---

## 5. LỘ TRÌNH PHÁT TRIỂN AI TIẾP THEO (ROADMAP)

| Giai đoạn | Tính năng AI mục tiêu | Công nghệ dự kiến | Trạng thái |
| :---: | :--- | :--- | :---: |
| **Sprint 1 & 2** | Phân tích cảnh báo tồn min, Grounded Prompting & Data Sanitizer | Google Gemini 1.5 Flash API, FastAPI |  **Đã hoàn thành 100%** |
| **Sprint 3** | Dự báo nhu cầu vật tư theo mùa vụ (Demand Forecasting) | Time-Series (ARIMA / Prophet) + Gemini Summarizer |  Sẵn sàng triển khai |
| **Sprint 4** | Trợ lý hỏi đáp kho bằng ngôn ngữ tự nhiên (Chatbot NL2SQL) | LangChain / Gemini Function Calling |  Kế hoạch tương lai |
