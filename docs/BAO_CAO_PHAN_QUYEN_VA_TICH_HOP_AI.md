# BÁO CÁO TOÀN DIỆN: SO SÁNH PHÂN QUYỀN VAI TRÒ & PHÂN TÍCH TÍCH HỢP AI TRONG HỆ THỐNG SMARTLOGIS AI

> **Dự án:** SmartLogis AI - Hệ Thống Quản Lý Kho Thông Minh Vận Hành Thời Gian Thực  
> **Phiên bản:** v2.0 Enterprise  
> **Tác giả / Nhà sáng lập:** **Nguyễn Thành Hưng** & **Hoàng Tiến Đạt**  
> **Thời điểm lập báo cáo:** 09/09/2026  

---

## MỤC LỤC

1. [PHẦN 1: BÁO CÁO KHÁC BIỆT VAI TRÒ & PHÂN QUYỀN (ROLE DIFFERENCE REPORT)](#phan-1)
   - 1.1. Ma trận phân quyền 3 vai trò (RBAC Matrix)
   - 1.2. Khác biệt về Bố cục Giao diện (UI Layout & Components per Role)
   - 1.3. Chi tiết chức năng từng vai trò & Bảng quyền thao tác (CRUD & Endpoints)
   - 1.4. Nguyên lý phân tách trách nhiệm (Separation of Duties & SOX Compliance)
2. [PHẦN 2: PHÂN TÍCH TÍCH HỢP TRÍ TUỆ NHÂN TẠO (AI INTEGRATION ANALYSIS)](#phan-2)
   - 2.1. Kiến trúc tích hợp AI tổng thể trong hệ thống
   - 2.2. Lớp bảo mật khử dữ liệu nhạy cảm (Data Sanitizer Layer)
   - 2.3. Các phân hệ và quy trình phụ thuộc nhiều nhất vào AI
   - 2.4. Tác động của AI đối với luồng vận hành kho thực tế
   - 2.5. Cơ chế dự phòng đảm bảo tính sẵn sàng 24/7 (Local Grounded Fallback Engine)
3. [TỔNG KẾT & KẾ HOẠCH BÀN GIAO](#tong-ket)

---

<a name="phan-1"></a>
## PHẦN 1: BÁO CÁO KHÁC BIỆT VAI TRÒ & PHÂN QUYỀN (ROLE DIFFERENCE REPORT)

Hệ thống SmartLogis AI được thiết kế theo mô hình kiểm soát truy cập dựa trên vai trò (**Role-Based Access Control - RBAC**) nghiêm ngặt. Ba vai trò cốt lõi trong doanh nghiệp được định hình rõ ràng nhằm đảm bảo an toàn kho vận, ngăn ngừa gian lận và tối ưu hiệu suất làm việc.

### 1.1. Ma Trận Phân Quyền Tổng Quan (RBAC Matrix)

| Vai Trò Hệ Thống | Tài Khoản Mẫu | Nhân Sự Đại Diện | Trách Nhiệm Cốt Lõi |
| :--- | :--- | :--- | :--- |
| **Quản Trị Viên (Admin)** | `admin` / `admin123` | **Nguyễn Thành Hưng** | Toàn quyền kiểm soát hệ thống, quản trị danh mục gốc, cấu hình CSDL, xóa mặt hàng/đối tác, kích hoạt phân tích AI cấp cao. |
| **Thủ Kho Trưởng (Thukho)** | `thukho` / `thukho123` | **Hoàng Tiến Đạt** | Điều hành nhập - xuất kho thực tế, kiểm soát tồn kho tại chỗ, theo dõi cảnh báo tồn min, tra cứu thẻ kho, lập chứng từ giao dịch. |
| **Kế Toán Kho (Ketoan)** | `ketoan` / `ketoan123` | **Hoàng Tiến Đạt** | Giám sát tài chính kho, đối soát công nợ đối tác, xuất báo cáo tài chính Excel, tra cứu lịch sử luân chuyển hàng hóa mà không can thiệp vào kho thực. |

---

### 1.2. Khác Biệt Về Bố Cục Giao Diện (UI Layout & Components per Role)

Bố cục giao diện tự động thích ứng theo vai trò của người dùng đã đăng nhập:

```
+-----------------------------------------------------------------------------------+
| Topbar: Logo SmartLogis AI | [Theme Toggle] | [WebSocket Sync] | [User Info]      |
+-----------------------------------------------------------------------------------+
| SIDEBAR (Thanh Điều Hướng)     | KHÔNG GIAN LÀM VIỆC CHÍNH (Workspace)            |
|                                |                                                  |
| * Dashboard Tồn Kho            | - Admin: Xem full KPI, Cảnh báo tồn, AI Widget   |
| * Danh Mục Hàng Hóa            |   + Nút Thao Tác: [+ Nhập Hàng], [Xuất Excel]    |
| * Nhà Cung Cấp                 |                                                  |
|                                | - Thủ Kho: Xem KPI số lượng, Thẻ kho, Bảng alert |
| (Chứng từ giao dịch)           |   + Nút Thao Tác: [+ Nhập Hàng]                  |
| * Phiếu Nhập Kho (Ẩn với KT)   |                                                  |
| * Phiếu Xuất Kho (Ẩn với KT)   | - Kế Toán: Xem KPI giá trị, Doanh số xuất        |
|                                |   + Nút Thao Tác: [Xuất Excel], [Xem Thẻ Kho]    |
| * Tra Cứu Thẻ Kho              |   (Bị ẩn nút Tạo Phiếu Nhập / Xuất Kho)          |
+-----------------------------------------------------------------------------------+
```

#### A. Thanh Điều Hướng Bên Trái (Left Sidebar)
1. **Quản Trị Viên (Admin) & Thủ Kho (Thukho)**:
   - Hiển thị đầy đủ 6 danh mục cốt lõi: *Dashboard Tồn Kho, Danh Mục Hàng Hóa, Nhà Cung Cấp, Phiếu Nhập Kho, Phiếu Xuất Kho, Tra Cứu Thẻ Kho*.
2. **Kế Toán Kho (Ketoan)**:
   - **Tự động ẩn 2 mục chứng từ giao dịch:** *Phiếu Nhập Kho* và *Phiếu Xuất Kho*. 
   - Kế toán chỉ tập trung vào việc tra cứu, kiểm tra thẻ kho và xuất báo cáo đối soát.

#### B. Màn Hình Danh Mục Hàng Hóa (`/hang-hoa`)
* **Admin**: Có nút **"+ Thêm Mới Hàng Hóa"**, nút **"Sửa"** (icon bút chì) và nút **"Xóa"** (icon thùng rác màu đỏ). Admin là vai trò duy nhất có thể xóa hoàn toàn một SKU khỏi hệ thống nếu chưa phát sinh giao dịch.
* **Thủ Kho**: Có nút **"+ Thêm Mới Hàng Hóa"** và nút **"Sửa"** thông tin định danh/ngưỡng min; **không có nút Xóa** (ngăn chặn việc làm mất dấu dữ liệu lịch sử).
* **Kế Toán**: Giao diện hoàn toàn ở chế độ **Chỉ Đọc (Read-Only)**. Không xuất hiện nút thêm, sửa hay xóa hàng hóa.

#### C. Màn Hình Đối Tác Nhà Cung Cấp (`/nha-cung-cap`)
* **Admin & Thủ Kho**: Có nút **"+ Thêm Nhà Cung Cấp"**, nút cập nhật thông tin đối tác (SĐT, Email, Địa chỉ) và nút xem chi tiết lịch sử giao dịch.
* **Kế Toán**: Xem danh bạ nhà cung cấp, tổng giá trị đã nhập lũy kế, nút xem chi tiết công nợ và nút **"Xuất Excel Danh Bạ"**; cột thao tác hiển thị badge *Chỉ đọc*.

#### D. Màn Hình Báo Cáo Xuất Excel (`/api/v1/reports/export/excel`)
* Nút xuất file Excel chuyên sâu (kèm công thức tài chính và giá trị tồn kho) được ưu tiên hiển thị cho **Kế Toán** và **Admin**.

---

### 1.3. Bảng Quyền Thao Tác Chi Tiết (CRUD & API Endpoints)

Hệ thống bảo vệ phân quyền ở cả 2 tầng: **Giao diện (Frontend SSR)** và **Bộ lọc API Backend (FastAPI Dependency `require_role`)**:

| Nghiệp Vụ / Endpoint API | Admin | Thủ Kho (Thukho) | Kế Toán (Ketoan) | Cơ Chế Bảo Vệ Backend |
| :--- | :---: | :---: | :---: | :--- |
| **Đăng nhập hệ thống** (`/api/v1/auth/login`) | ✅ | ✅ | ✅ | OAuth2 Password Bearer + JWT Token |
| **Xem Dashboard & Cảnh báo** (`/dashboard`) | ✅ | ✅ | ✅ | Quyền truy cập mở cho nhân sự nội bộ |
| **Thêm mới Hàng hóa** (`POST /api/v1/kho/items`) | ✅ | ✅ | ❌ | `require_role(["Admin", "Thukho"])` (KT: 403) |
| **Chỉnh sửa Hàng hóa** (`PUT /api/v1/kho/items/{id}`) | ✅ | ✅ | ❌ | `require_role(["Admin", "Thukho"])` (KT: 403) |
| **Xóa Hàng hóa khỏi CSDL** (`DELETE /api/v1/kho/items/{id}`) | ✅ | ❌ | ❌ | `require_role(["Admin"])` (Chỉ Admin) |
| **Thêm Nhà cung cấp** (`POST /api/v1/kho/suppliers`) | ✅ | ✅ | ❌ | `require_role(["Admin", "Thukho"])` (KT: 403) |
| **Sửa Nhà cung cấp** (`PUT /api/v1/kho/suppliers/{id}`) | ✅ | ✅ | ❌ | `require_role(["Admin", "Thukho"])` (KT: 403) |
| **Xóa Nhà cung cấp** (`DELETE /api/v1/kho/suppliers/{id}`) | ✅ | ❌ | ❌ | `require_role(["Admin"])` (Chỉ Admin) |
| **Lập Phiếu Nhập Kho** (`POST /api/v1/kho/phieu-nhap`) | ✅ | ✅ | ❌ | `require_role(["Admin", "Thukho"])` (ACID Lock) |
| **Lập Phiếu Xuất Kho** (`POST /api/v1/kho/phieu-xuat`) | ✅ | ✅ | ❌ | `require_role(["Admin", "Thukho"])` (Zero Neg) |
| **Tra cứu Thẻ Kho** (`GET /api/v1/kho/the-kho`) | ✅ | ✅ | ✅ | Toàn quyền tra cứu kiểm toán |
| **Xuất Excel Tồn & Giá Trị** (`GET /api/v1/reports/export/excel`) | ✅ | ❌ | ✅ | `require_role(["Admin", "Ketoan"])` (Bảo mật giá) |
| **Xuất Excel Danh Bạ NCC** (`GET /api/v1/reports/export/suppliers-excel`)| ✅ | ✅ | ✅ | Toàn quyền xuất danh bạ liên hệ |
| **Yêu cầu AI Phân Tích Live** (`POST /api/v1/ai/generate-report`) | ✅ | ✅ | ✅ | Hỗ trợ phân tích hỗ trợ ra quyết định |

---

### 1.4. Nguyên Lý Phân Tách Trách Nhiệm (Separation of Duties & SOX Compliance)

Việc phân quyền của SmartLogis AI không chỉ dừng lại ở mặt kỹ thuật mà tuân thủ chuẩn mực kiểm soát nội bộ quốc tế:

1. **Phân lập giữa "Người giữ hàng" và "Người ghi sổ" (Keeper vs. Accountant)**:
   - Thủ kho là người trực tiếp cầm chìa khóa kho, kiểm đếm hàng thực tế nên có quyền tạo phiếu Nhập và phiếu Xuất.
   - Kế toán kho là người đối soát độc lập. Kế toán **tuyệt đối không được phép tự tạo phiếu nhập xuất hay sửa số lượng tồn kho**. Nếu kế toán vừa có quyền xuất kho vừa có quyền sửa số liệu, nguy cơ thất thoát tài sản và gian lận sổ sách là rất lớn.
2. **Nguyên tắc bất biến của sổ Thẻ Kho (Append-Only Ledger)**:
   - Cả Admin, Thủ kho và Kế toán đều không thể trực tiếp "sửa số tồn" bằng câu lệnh UPDATE tùy tiện. Mọi biến động tăng giảm bắt buộc phải thông qua Phiếu Nhập hoặc Phiếu Xuất được ký nhận bởi Thủ kho hoặc Admin với giao dịch ACID bảo vệ.
3. **Bảo vệ giá vốn bí mật kinh doanh**:
   - Nhân viên kho thông thường chỉ cần quan tâm đến số lượng vật lý và vị trí lưu trữ. Giá nhập và chi phí mua hàng được dành riêng cho Kế toán và Admin.

---

<a name="phan-2"></a>
## PHẦN 2: PHÂN TÍCH TÍCH HỢP TRÍ TUỆ NHÂN TẠO (AI INTEGRATION ANALYSIS)

SmartLogis AI không sử dụng AI theo kiểu chatbot chung chung, mà triển khai theo mô hình **Grounded Analytical Engine** (AI bám sát dữ liệu vận hành thực tế), giải quyết các bài toán tối ưu chuỗi cung ứng cụ thể.

### 2.1. Kiến Trúc Tích Hợp AI Tổng Thể

```
+-----------------------------------------------------------------------------------------+
|                                    TẦNG GIAO DIỆN (UI)                                  |
|   - Widget SmartLogis AI Dashboard: 3 thẻ khuyến nghị vận hành (Tam giác, Lửa, Hộp lưu) |
|   - Modal Báo Cáo AI Toàn Diện: 3 phần (Tổng quan, Đề xuất nhập, Biến động bất thường) |
+-----------------------------------------------------------------------------------------+
                                           │ (Gọi API Fetch JSON)
                                           ▼
+-----------------------------------------------------------------------------------------+
|                                TẦNG ĐIỀU HƯỚNG (ai_router.py)                           |
|   - GET  /api/v1/ai/advisory        -> Trả về Widget khuyến nghị tức thì               |
|   - POST /api/v1/ai/generate-report -> Sinh báo cáo toàn diện 3 phần                  |
+-----------------------------------------------------------------------------------------+
                                           │
                                           ▼
+-----------------------------------------------------------------------------------------+
|                              TẦNG DỊCH VỤ (ai_service.py Facade)                         |
|                                                                                         |
|  1. [ai_data_service.py]               2. [inventory_prompts.py]                        |
|     * Truy vấn số liệu kho 30 ngày        * System Instruction nghiêm ngặt              |
|     * Tính Burn-Rate & Dead Stock         * Kỹ thuật Grounded Few-Shot                   |
|     * BỘ LỌC DATA SANITIZER (100%)       * Khống chế ảo giác (Anti-Hallucination)       |
|                                                                                         |
|                                           │                                             |
|                                           ▼                                             |
|  3. [gemini_service.py - Connector & Fallback Engine]                                   |
|     * Kết nối Google Gemini API (gemini-3.5-flash-lite, gemini-3.6-flash)               |
|     * Cơ chế Exponential Backoff Retry (Max 3 lần)                                      |
|     * Bắt lỗi Rate Limit (429), Timeout, Quota Exhausted                                |
|     * TỰ ĐỘNG CHUYỂN SANG: Local Grounded Fallback Engine (Zero Downtime)               |
+-----------------------------------------------------------------------------------------+
```

---

### 2.2. Lớp Bảo Mật Khử Dữ Liệu Nhạy Cảm (Data Sanitizer Layer)

Một trong những rủi ro lớn nhất của doanh nghiệp khi ứng dụng Cloud LLM (Gemini/OpenAI) là nguy cơ **lộ bí mật kinh doanh và giá vốn nhập hàng**. SmartLogis AI giải quyết triệt để vấn đề này thông qua module `Data Sanitizer` tại `app/services/ai_data_service.py`:

```python
SENSITIVE_FINANCIAL_KEYS = {
    "dongianhap", "don_gia_nhap", "import_price", "cost_price",
    "thanhtien", "thanh_tien", "total_cost", "giavon", "gia_von",
    "gianhap", "gia_nhap", "purchase_price"
}
```

* **Cơ chế hoạt động**:
  1. Trước khi bất kỳ dữ liệu nào được chuyển thành câu lệnh Prompt, hàm `sanitize_inventory_payload()` sẽ quét đệ quy qua toàn bộ cây dữ liệu JSON.
  2. Bất kỳ trường nào liên quan đến giá mua, đơn giá vốn, tổng tiền nhập hàng đều bị **cắt bỏ hoàn toàn 100%**.
  3. Mô hình AI chỉ nhận được các thông số kỹ thuật thuần túy: *Mã SKU, Tên hàng, Đơn vị tính, Số lượng tồn thực tế, Ngưỡng min, Tốc độ xuất 30 ngày (Burn-Rate), Số ngày không phát sinh xuất*.
* **Lợi ích**: Doanh nghiệp được bảo vệ tuyệt đối. Nhà cung cấp dịch vụ AI không thể nắm được giá vốn hoặc biên lợi nhuận của doanh nghiệp.

---

### 2.3. Các Phân Hệ Phụ Thuộc Nhiều Nhất Vào AI

AI trong SmartLogis AI tập trung giải quyết **3 bài toán sống còn** của kho vận hiện đại:

#### 1. Module Đề Xuất Bổ Sung Hàng Tồn Min (Auto-Restock Recommendation)
* **Vị trí phụ thuộc:** Bảng điều khiển chính và Phần 2 của Báo cáo AI.
* **Cách thức AI xử lý:**
  - AI không chỉ nhìn vào số lượng thiếu hụt tức thời (`ThieuHut = TonToiThieu - SoLuongTon`), mà phân tích kết hợp với **Tốc độ xuất bình quân ngày (Burn Rate)** trong 30 ngày qua.
  - *Ví dụ:* Cùng thiếu 10 đơn vị, nhưng mặt hàng A xuất 5 cái/ngày sẽ được AI gắn nhãn **"KHẨN CẤP"** và đề xuất nhập thêm 50 cái (đủ dùng 10 ngày); trong khi mặt hàng B xuất 0.1 cái/ngày chỉ được AI đề xuất nhập mức tối thiểu để tránh tồn ứ vốn.

#### 2. Module Nhận Diện Bất Thường Tốc Độ Xuất (Outbound Velocity Spikes)
* **Vị trí phụ thuộc:** Thẻ chỉ số màu đỏ trên AI Widget và Phần 3 của Báo cáo AI.
* **Cách thức AI xử lý:**
  - So sánh tốc độ tiêu thụ hiện tại với ngưỡng chuẩn 30 ngày.
  - Phát hiện các mặt hàng có nhu cầu tăng vọt bất thường (Outbound Outliers) để kịp thời cảnh báo thủ kho điều phối phương tiện vận chuyển và thông báo cho phòng mua hàng.

#### 3. Module Thanh Lý Hàng Ứ Đọng Lâu (> 60 Ngày - Dead Stock)
* **Vị trí phụ thuộc:** Thẻ chỉ số màu xanh trên AI Widget và Phần 3 của Báo cáo AI.
* **Cách thức AI xử lý:**
  - Quét toàn bộ CSDL và tìm các mặt hàng có tồn kho > 0 nhưng không hề phát sinh bất kỳ Phiếu Xuất nào trong 60 ngày gần nhất.
  - AI tổng hợp danh sách mặt hàng chiếm dụng diện tích, đưa ra khuyến nghị thanh lý, giảm giá hoặc gom hàng để giải phóng diện tích sàn kho.

---

### 2.4. Tác Động Của AI Đối Với Luồng Vận Hành Kho Thực Tế

| Giai Đoạn Luồng | Vận Hành Kho Truyền Thống | Vận Hành Với SmartLogis AI |
| :--- | :--- | :--- |
| **Theo dõi kho** | Thủ kho phải dùng mắt rà soát từng dòng trong bảng Excel hàng trăm SKU để tìm mặt hàng thiếu. | **Tự động 100%:** AI Widget tổng hợp ngay 3 nhóm trọng tâm khi vừa mở màn hình: Cần nhập gấp, Đang bán chạy, Đang ứ đọng. |
| **Quyết định nhập**| Thủ kho đặt hàng theo cảm tính, dễ dẫn đến thiếu hàng bán chạy hoặc thừa hàng ế ẩm. | **Đề xuất dựa trên dữ liệu:** AI tính toán số lượng đặt hàng tối ưu (Reorder Quantity) dựa trên Burn-Rate thực tế. |
| **Thao tác lập phiếu**| Phải nhớ mã hàng, gõ tay từng SKU sang form nhập. | **Thao tác 1-Click:** Nút **"+ Nhập hàng"** ngay cạnh cảnh báo AI tự động mở form Nhập kho với mã hàng đã được chọn sẵn. |
| **Báo cáo định kỳ** | Mất từ 1 đến 2 ngày để kế toán/thủ kho làm slide và biểu đồ phân tích cho Ban Giám Đốc. | **Sinh báo cáo tức thì:** Bấm nút **"Phân tích lại"**, Gemini LLM xuất báo cáo điều hành toàn diện 3 phần chuẩn format trong 3 giây. |

---

### 2.5. Cơ Chế Dự Phòng Zero-Downtime Fallback (Local Grounded Engine)

Một trong những ưu điểm kỹ thuật vượt trội của SmartLogis AI là khả năng **tự chữa lành và dự phòng không điểm nghẽn**:

* Khi hệ thống gặp các sự cố ngoại cảnh:
  1. Mất kết nối Internet hoặc rớt mạng ra quốc tế.
  2. Google Gemini API bị lỗi hoặc quá hạn mức Quota (HTTP 429 Too Many Requests).
  3. Quên chưa điền hoặc điền sai Gemini API Key.
* **Cơ chế chuyển mạch tự động:**
  - `gemini_service.py` ngay lập tức bắt ngoại lệ và kích hoạt **Local Grounded Fallback Engine**.
  - Động cơ nội bộ sử dụng thuật toán Heuristic tính toán toán học trực tiếp trên SQLite WAL, tạo ra bảng đề xuất 3 phần và 3 thẻ widget với số liệu chính xác 100%.
  - Giao diện người dùng vẫn hiển thị huy hiệu `Local Grounded` màu vàng, **tuyệt đối không bao giờ hiển thị lỗi 500 hay làm gián đoạn công việc của thủ kho**.

---

<a name="tong-ket"></a>
## TỔNG KẾT & KẾ HOẠCH BÀN GIAO

1. **Về Giao Diện & Bố Cục**:
   - Đã đóng hoàn toàn chức năng Đăng ký tài khoản tự do (`/register`), bảo đảm kho vận là hệ sinh thái nội bộ khép kín, an toàn thông tin.
   - Thanh điều hướng Sidebar bên trái đã được tinh giản, loại bỏ các chữ thừa rườm rà, chỉ giữ lại đúng 6 danh mục nghiệp vụ kho trọng yếu.
   - Màn hình Đăng nhập dạng Split-Screen kết hợp ảnh minh họa kho thông minh AI tạo ấn tượng thị giác chuyên nghiệp, đẳng cấp.
   - Chế độ Dark Mode hoạt động mượt mà với bảng màu Slate-Navy tươi sáng, bảo vệ mắt người dùng khi làm ca đêm.
2. **Về Vai Trò & Trách Nhiệm**:
   - Xác lập phân định quyền hạn minh bạch giữa Admin (**Nguyễn Thành Hưng**), Thủ kho (**Hoàng Tiến Đạt**) và Kế toán (**Hoàng Tiến Đạt**).
3. **Về Trí Tuệ Nhân Tạo (AI)**:
   - Module Data Sanitizer khử 100% giá vốn nhạy cảm.
   - AI đóng vai trò như một "Cố vấn kho vận tự động", giúp chuyển đổi phương thức quản lý từ bị động đối phó sang chủ động dự báo.

*Tài liệu này được lưu trữ chính thức tại kho lưu trữ mã nguồn dự án SmartLogis AI phục vụ công tác bàn giao, thẩm định kiến trúc và nghiệm thu.*
