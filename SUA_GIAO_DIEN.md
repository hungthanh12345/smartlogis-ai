# BÁO CÁO CẬP NHẬT: SỬA GIAO DIỆN & TỐI ƯU HÓA HỆ THỐNG SMARTLOGIS AI

> **Thời điểm cập nhật:** 09/09/2026  
> **Dự án:** SmartLogis AI - Hệ Thống Quản Lý Kho Thông Minh Tích Hợp AI (Realtime Centralized Web Server)  
> **Tác giả / Nhà sáng lập:** **Nguyễn Thành Hưng** & **Hoàng Tiến Đạt**  

---

## 1. TỔNG QUAN YÊU CẦU & KẾT QUẢ ĐẠT ĐƯỢC

Toàn bộ các cập nhật được thực hiện nghiêm ngặt theo đúng nguyên tắc: **Giữ nguyên toàn bộ kiến trúc lõi backend, schema CSDL, cơ chế giao dịch ACID và bảo vệ chống tồn âm (Zero Negative Stock)**. Trọng tâm là nâng cấp trải nghiệm thị giác, cải tiến giao diện theo phong cách phần mềm kho chuyên nghiệp (KiotViet, Nhanh.vn) và sửa chữa triệt để các lỗi hiển thị định dạng.

| Hạng mục | Yêu cầu | Kết quả thực hiện |
| :--- | :--- | :--- |
| **Bảng màu & Theme** | Chuyển sang gam xanh tươi sáng (Light Blue / KiotViet) và cam-đỏ nổi bật (Orange-Red Alert) | ✅ Đã áp dụng hệ màu tươi sáng hiện đại; các nút thao tác chính mang màu xanh ngọc lục bảo (`btn-kiot-green`), các thẻ cảnh báo tồn kho dùng màu cam-đỏ nổi bật |
| **Tính năng Dark Mode** | Tích hợp chế độ Dark Mode hoạt động mượt mà | ✅ Tích hợp nút chuyển đổi Sáng/Tối (Sun/Moon) trên Topbar; lưu trạng thái vào `localStorage`, chống giật nhấp nháy (Anti-FOUC) |
| **Sửa lỗi định dạng HTML** | Khắc phục chữ `\n` bị in tràn ra ngoài thẻ | ✅ Đã loại bỏ 100% ký tự `\n` thừa ở cuối các file template và static script |
| **Sửa lỗi icon AI** | Khắc phục chuỗi `fa-solid fa-triangle-exclamation text-amber-500` bị in text thô | ✅ Đã sửa cả Jinja2 Template lẫn Javascript dynamic reload thành thẻ icon FontAwesome sắc nét |
| **Đổi tên người dùng** | Cập nhật tên tác giả: Nguyễn Thành Hưng và Hoàng Tiến Đạt | ✅ Cập nhật toàn bộ trong CSDL (`smartlogis.db`), `seed_data.py` và các nút điền nhanh trên trang Login |

---

## 2. CHI TIẾT CÁC THAY ĐỔI GIAO DIỆN & THIẾT KẾ

### 2.1. Phong cách thiết kế KiotViet & Nhanh.vn
* **Thanh điều hướng (Sidebar)**: Thiết kế tông Slate-900 / Navy sang trọng, phân khu rõ ràng giữa:
  * *Nghiệp vụ kho* (Dashboard, Danh mục hàng hóa, Nhà cung cấp).
  * *Chứng từ giao dịch* (Phiếu nhập kho, Phiếu xuất kho).
  * *Báo cáo & Tra cứu* (Thẻ kho, Xuất Excel, Swagger Docs).
  * Trạng thái active sử dụng màu xanh ngọc biển tươi sáng (`#0284c7`), nổi bật rõ vị trí trang người dùng đang thao tác.
* **Thanh công cụ trên cùng (Topbar)**:
  * Nền trắng trang nhã trong chế độ Light Mode, viền phân tách mảnh nhẹ.
  * Tích hợp huy hiệu đồng bộ WebSocket Realtime tự động nhấp nháy.
  * Hiển thị đầy đủ Avatar người dùng, họ tên thật **Nguyễn Thành Hưng** / **Hoàng Tiến Đạt**, huy hiệu vai trò và nút đăng xuất an toàn.
* **Cụm nút chức năng KiotViet**:
  * Nút **+ Thêm Mới**, **Xuất Excel Danh Bạ**, **Lưu Mặt Hàng**: Sử dụng gam màu xanh lá tươi chuẩn mực (`bg-emerald-600 hover:bg-emerald-700`).
  * Nút **+ Nhập hàng** tại bảng Dashboard: Sử dụng xanh dương Cerulean (`btn-kiot-blue`).
  * Nút **Khóa xuất kho / Vi phạm tồn âm**: Tự động chuyển đỏ rực rỡ kèm cảnh báo vi phạm `SELECT ... FOR UPDATE`.

---

### 2.2. Tính năng Dark Mode (Giao diện ban đêm)
* **Cơ chế hoạt động**:
  * Người dùng bấm vào nút chuyển đổi hình **Mặt trăng / Mặt trời** tại góc phải Topbar (hoặc góc trên trang Đăng nhập).
  * Trình duyệt ngay lập tức đảo lớp `dark` trên thẻ `<html>` và ghi nhớ lựa chọn vào `localStorage.getItem('smartlogis_theme')`.
  * Trong `<head>` có script thực thi ngay lập tức trước khi render, đảm bảo **không bao giờ bị chớp sáng (Zero FOUC)** khi người dùng chuyển trang hoặc F5.
* **Thẩm mỹ Dark Mode**:
  * Tông nền tối dịu mắt (`#0f172a` và `#1e293b`), giảm mỏi mắt tối đa khi làm việc ban đêm trong kho.
  * Bảng dữ liệu, hộp thoại Modal, khung nhập liệu có viền tối mảnh (`#334155`), chữ trắng sáng rõ ràng (`#f8fafc`).
  * Các huy hiệu tồn kho tự động chuyển sang chế độ nền trong mờ phát sáng nhẹ (glow badge).

---

### 2.3. Sửa triệt để các lỗi hiển thị & Typo

#### Lỗi 1: Ký tự `\n` in ra ngoài màn hình Đăng nhập (ảnh tham chiếu 4)
* **Nguyên nhân kỹ thuật**: Ở cuối các file HTML (như [login.html](file:///d:/antigravity_file/smartlogis-ai/app/templates/login.html), [base.html](file:///d:/antigravity_file/smartlogis-ai/app/templates/base.html)), ký tự chuỗi thô `\n` nằm sau thẻ đóng `</html>`. Theo chuẩn HTML5 Tree Construction, các nút văn bản sau `</html>` sẽ bị đẩy ngược vào `<body>`. Do thẻ `<body>` có class `flex items-center justify-center`, ký tự `\n` bị hiển thị như một phần tử flex nằm lơ lửng bên phải khung đăng nhập.
* **Khắc phục**: Đã dọn dẹp và cắt bỏ hoàn toàn các ký tự `\n` thừa ở tất cả các file template và static script.

#### Lỗi 2: Text thô FontAwesome trên khối AI Insight Dashboard (ảnh tham chiếu 5)
* **Nguyên nhân kỹ thuật**: Tại [dashboard.html](file:///d:/antigravity_file/smartlogis-ai/app/templates/dashboard.html), đoạn render dùng thẻ `<span>{{ insight.icon }}</span>` và trong script Javascript dùng `<span>${ins.icon}</span>`. Do đó chuỗi class `fa-solid fa-triangle-exclamation text-amber-500` bị in trực tiếp dưới dạng chữ thay vì tạo thẻ `<i>`.
* **Khắc phục**: Đã sửa thành:
  ```html
  <span class="w-5 h-5 flex items-center justify-center rounded-md bg-slate-100 dark:bg-slate-800 text-xs">
    <i class="{{ insight.icon }}"></i>
  </span>
  ```
  Biểu tượng tam giác cảnh báo màu vàng, ngọn lửa xuất đột biến màu đỏ và hộp lưu trữ tồn kho màu xanh lá giờ đây hiển thị icon trực quan, sắc nét 100%.

#### Lỗi 3: Nút "Thao Tác" (+ Nhập hàng) trên bảng Cảnh Báo Tồn Min bị ẩn/mất màu (ảnh người dùng phản hồi)
* **Nguyên nhân kỹ thuật**: Cột "THAO TÁC" trước đây sử dụng class `.btn-kiot-blue text-white`. Do trình duyệt người dùng lưu cache CSS cũ hoặc độ trễ tải lớp custom, thuộc tính background không được áp dụng trong khi class `text-white` có hiệu lực, dẫn đến chữ trắng hiển thị trên nền bảng trắng (trở nên vô hình). Đồng thời, việc tải song song cả `all.min.css` và `all.min.js` của FontAwesome gây xung đột biến đổi thẻ DOM `<i>` thành `<svg>`.
* **Khắc phục triệt để**:
  1. Thêm style nội tuyến cứng trực tiếp: `style="background-color: #0284c7; color: #ffffff;"` kết hợp các lớp Tailwind `bg-sky-600 hover:bg-sky-500 active:bg-sky-700 text-white font-bold rounded-lg text-xs transition shadow-xs hover:shadow-md cursor-pointer whitespace-nowrap`. Đảm bảo nút **"+ Nhập hàng"** luôn luôn hiển thị nền xanh biển đậm, chữ trắng in đậm nổi bật trong mọi điều kiện (ngay cả khi CSS chưa tải xong).
  2. Nút **"Xuất Excel"** cũng được bổ sung style nội tuyến `style="background-color: #059669; color: #ffffff;"` cùng lớp xanh ngọc lục bảo KiotViet `bg-emerald-600`.
  3. Canh giữa đồng bộ cột tiêu đề `THAO TÁC` (`text-center`) và ô dữ liệu nút bấm để bố cục bảng cân đối, đẹp mắt.
  4. Cập nhật đồng bộ cả trong mã nguồn HTML tĩnh (SSR) lẫn hàm JavaScript làm mới dữ liệu thời gian thực `window.refreshStockAlertsTable()`.
  5. Loại bỏ script `all.min.js` gây xung đột DOM, giữ lại thư viện FontAwesome 6 WebFonts CSS (`all.min.css`) chuẩn mực, ổn định cao.
  6. Tăng tham số chống cache (Cache-buster) lên `?v=20260909_5` trên toàn hệ thống để trình duyệt tự động nạp phiên bản mới nhất ngay lập tức.

---

## 3. CẬP NHẬT TÊN NGƯỜI DÙNG & TÁC GIẢ SÁNG LẬP

Toàn bộ thông tin định danh mẫu đã được cập nhật sang tên hai tác giả sáng lập dự án:

| Tên Đăng Nhập | Mật Khẩu | Họ Tên Hiển Thị | Vai Trò | Phân Quyền |
| :--- | :--- | :--- | :--- | :--- |
| `admin` | `admin123` | **Nguyễn Thành Hưng** | Quản Trị Viên (Admin) | Toàn quyền quản trị kho, cấu hình CSDL, xem AI Advisory, phân quyền |
| `thukho` | `thukho123` | **Hoàng Tiến Đạt** | Thủ Kho Trưởng (Thukho) | Lập phiếu nhập kho, phiếu xuất kho, tra cứu thẻ kho, điều chuyển |
| `ketoan` | `ketoan123` | **Hoàng Tiến Đạt** | Kế Toán Kho (Ketoan) | Đối soát công nợ, đối soát nhà cung cấp, xuất báo cáo Excel |

> **Lưu ý:** Theo đúng yêu cầu người dùng, tài khoản **Kế toán kho** được đặt duy nhất tên tác giả **Hoàng Tiến Đạt**.

### 2.5. Nâng Cấp Giao Diện Đăng Nhập & Chế Độ Dark Mode Sáng Rõ Hơn

1. **Thiết kế màn hình Đăng nhập dạng Split-Screen (Chia đôi hiện đại)**:
   - **Bên trái (Chiếm 60% màn hình)**: Hình ảnh minh họa kho thông minh độ phân giải cao (`/static/images/warehouse_login_banner.jpg`) kèm lớp phủ thương hiệu SmartLogis AI, 3 khối giới thiệu công nghệ cốt lõi (*Zero Negative Stock ACID, Gemini AI Advisory 2.0, Realtime WebSocket Sync*).
   - **Bên phải (Chiếm 40% màn hình)**: Khung đăng nhập dời sang hẳn bên phải theo đúng yêu cầu, canh chỉnh trung tâm tinh tế, các ô nhập liệu tương phản cao, 3 nút điền nhanh tài khoản 1-click.
2. **Hoàn thiện 100% nút Dark Mode**:
   - Tích hợp hàm `initTheme()` và `toggleDarkMode()` từ `app.js` cho cả trang Đăng nhập và Đăng ký.
   - Nút chuyển đổi giao diện hiển thị biểu tượng Mặt trời (Sáng) / Mặt trăng (Tối) kèm nhãn chữ rõ ràng, chuyển đổi tức thì không cần tải lại trang.
3. **Làm sáng tông màu tối (Brighter Dark Palette)**:
   - Thay thế toàn bộ mã màu đen kịt (`slate-950` / `#020617`) bằng tông Slate-Navy thanh lịch (`slate-900` / `#0f172a` và `slate-850` / `#1e293b`).
   - Tăng độ tương phản của chữ (`slate-100` / `slate-200`) và viền thẻ (`slate-700` / `#334155`), giúp người dùng quan sát số liệu kho ban đêm rõ ràng, êm mắt, không bị tối mờ khó nhìn.

### 2.6. Khóa Đăng Ký Tự Do & Tinh Giản Sidebar Trái (Clean Minimal Navigation)

1. **Loại bỏ tính năng Đăng ký tài khoản ngoài**:
   - Hệ thống kho là tài sản nội bộ quan trọng, không mở cho người dùng bên ngoài tự do đăng ký.
   - Loại bỏ liên kết đăng ký tại màn hình Đăng nhập [login.html](file:///d:/antigravity_file/smartlogis-ai/app/templates/login.html), thay bằng thông điệp bảo mật: *"Cổng kho nội bộ — Tài khoản do Quản Trị Viên cấp phát"*.
   - Khóa route `/register` trong [main.py](file:///d:/antigravity_file/smartlogis-ai/main.py), tự động chuyển hướng HTTP 307 Redirect về `/login`.
2. **Tinh giản thanh Sidebar bên trái**:
   - Loại bỏ các tiêu đề phân nhóm rườm rà ("Nghiệp vụ kho", "Chứng từ giao dịch", "Báo cáo & Tra cứu").
   - Loại bỏ liên kết ngoài không thuộc luồng kho (Swagger API Docs).
   - Chỉ giữ lại đúng 6 danh mục nghiệp vụ kho trọng yếu với icon trực quan, căn lề chuẩn mực:
     * *Dashboard Tồn Kho*
     * *Danh Mục Hàng Hóa*
     * *Nhà Cung Cấp*
     * *Phiếu Nhập Kho*
     * *Phiếu Xuất Kho*
     * *Tra Cứu Thẻ Kho*

### 2.7. Tài Liệu Báo Cáo Chuyên Sâu: So Sánh Phân Quyền & Tích Hợp AI
- Đã xuất bản tài liệu độc lập phục vụ công tác thẩm định và nghiệm thu kiến trúc tại:  
  **[docs/BAO_CAO_PHAN_QUYEN_VA_TICH_HOP_AI.md](file:///d:/antigravity_file/smartlogis-ai/docs/BAO_CAO_PHAN_QUYEN_VA_TICH_HOP_AI.md)**  
  Gồm 2 phần trọng tâm:
  1. *Role Difference Report*: Ma trận RBAC, so sánh chi tiết UI/Permissions giữa Admin (**Nguyễn Thành Hưng**), Thủ kho (**Hoàng Tiến Đạt**), Kế toán (**Hoàng Tiến Đạt**) và nguyên lý phân tách trách nhiệm (Separation of Duties).
  2. *AI Integration Analysis*: Kiến trúc Grounded Prompting, lớp bảo mật Data Sanitizer khử 100% giá vốn nhạy cảm, 3 phân hệ phụ thuộc AI nhiều nhất và cơ chế dự phòng Zero-downtime Fallback.

---

## 4. DANH SÁCH CÁC TẬP TIN ĐÃ THAY ĐỔI

1. **[app/templates/base.html](file:///d:/antigravity_file/smartlogis-ai/app/templates/base.html)**:
   - Cấu hình Tailwind `darkMode: 'class'`, mở rộng bảng màu `brand` (Light Blue) và `accent` (Orange-Red).
   - Tích hợp script chống FOUC và nút chuyển đổi Dark Mode trên Topbar.
   - Hiển thị tên tác giả đăng nhập và avatar chuẩn hóa.
   - Loại bỏ ký tự `\n` sau thẻ `</html>`.

2. **[app/templates/login.html](file:///d:/antigravity_file/smartlogis-ai/app/templates/login.html)**:
   - Xóa bỏ ký tự `\n` hiển thị mép phải khung đăng nhập.
   - Tích hợp nút chuyển theme nổi (Floating Theme Switcher).
   - Cập nhật 3 nút điền nhanh tài khoản theo tên Nguyễn Thành Hưng & Hoàng Tiến Đạt.

3. **[app/templates/register.html](file:///d:/antigravity_file/smartlogis-ai/app/templates/register.html)**:
   - Đồng bộ giao diện hiện đại, Dark Mode, hỗ trợ FontAwesome và xóa bỏ ký tự `\n`.

4. **[app/templates/dashboard.html](file:///d:/antigravity_file/smartlogis-ai/app/templates/dashboard.html)**:
   - Sửa lỗi in text thô FontAwesome thành icon chuẩn cho khối AI Advisory và hàm gọi API Realtime.
   - Nâng cấp 4 thẻ KPI với màu cam-đỏ nổi bật cho cảnh báo tồn min.
   - Bảng cảnh báo tồn kho phong cách KiotViet hỗ trợ Dark Mode hoàn chỉnh.
   - Xóa bỏ ký tự `\n` thừa.

5. **[app/templates/items.html](file:///d:/antigravity_file/smartlogis-ai/app/templates/items.html)**:
   - Nút `+ Thêm Mới` và `Xuất Excel` chuẩn phong cách KiotViet (`btn-kiot-green`).
   - Hỗ trợ Dark Mode cho toàn bộ bảng hàng hóa và 2 Modal thêm mới / sửa SKU.

6. **[app/templates/suppliers.html](file:///d:/antigravity_file/smartlogis-ai/app/templates/suppliers.html)**:
   - Nút thêm mới nhà cung cấp xanh lá KiotViet, đồng bộ giao diện và Dark Mode.

7. **[app/templates/inbound.html](file:///d:/antigravity_file/smartlogis-ai/app/templates/inbound.html)**:
   - Tự động lấy ngày hiện tại bằng Javascript.
   - Nâng cấp bảng nhập kho, hỗ trợ Dark Mode và xóa bỏ `\n` thừa.

8. **[app/templates/outbound.html](file:///d:/antigravity_file/smartlogis-ai/app/templates/outbound.html)**:
   - Tự động lấy ngày hiện tại.
   - Giữ vững thuật toán thẩm định chống tồn âm, nâng cấp bảng xuất kho và Dark Mode.

9. **[app/templates/the_kho.html](file:///d:/antigravity_file/smartlogis-ai/app/templates/the_kho.html)**:
   - Sổ thẻ kho lũy kế thời gian thực, định dạng ngày tiếng Việt, Dark Mode và xóa bỏ `\n` thừa.

10. **[app/static/css/style.css](file:///d:/antigravity_file/smartlogis-ai/app/static/css/style.css)**:
    - Bổ sung hệ thống biến CSS, lớp nút KiotViet (`.btn-kiot-green`, `.btn-kiot-blue`, `.btn-kiot-orange`), thanh cuộn hiện đại và Dark Mode transition.

11. **[app/static/js/app.js](file:///d:/antigravity_file/smartlogis-ai/app/static/js/app.js)**:
    - Bộ điều khiển `initTheme()`, `toggleDarkMode()`, cập nhật icon Sun/Moon và đồng bộ `localStorage`.

12. **[scripts/seed_data.py](file:///d:/antigravity_file/smartlogis-ai/scripts/seed_data.py)** & **[smartlogis.db](file:///d:/antigravity_file/smartlogis-ai/smartlogis.db)**:
    - Cập nhật người dùng mặc định mang tên Nguyễn Thành Hưng và Hoàng Tiến Đạt.

---

## 5. KẾT QUẢ KIỂM THỬ HỆ THỐNG

### 5.1. Automated Test Suite (Pytest)
Toàn bộ 15 kịch bản kiểm thử tự động đều đã vượt qua 100%:
* `tests/test_ai_engine.py` (4/4 passed): Kiểm tra khử dữ liệu nhạy cảm Data Sanitizer, chống ảo giác Zero Hallucination.
* `tests/test_crud.py` (1/1 passed): Kiểm tra toàn vẹn CRUD danh mục hàng hóa.
* `tests/test_endpoints.py` (1/1 passed): Kiểm tra định tuyến API v1.
* `tests/test_phase2_inventory.py` (5/5 passed): Kiểm tra giao dịch ACID nhập kho, khóa `with_for_update()`, chống tồn kho âm, kiểm tra chạy đồng thời nhiều thiết bị (Race condition).
* `tests/test_supplier_crud.py` (1/1 passed): Kiểm tra ràng buộc đối tác và phiếu nhập.
* `tests/test_websocket.py` (3/3 passed): Kiểm tra đồng bộ đa thiết bị Realtime WebSocket.

```
====================== 15 passed in 38.30s =======================
```

### 5.2. Kiểm tra phản hồi Web SSR Endpoints
* `/login` -> **HTTP 200 OK** (Không có ký tự `\n` thừa)
* `/register` -> **HTTP 200 OK** (Không có ký tự `\n` thừa)
* `/dashboard` -> **HTTP 200 OK** (Hiển thị người dùng Nguyễn Thành Hưng, icon AI sắc nét)
* `/hang-hoa` -> **HTTP 200 OK** (Nút KiotViet xanh tươi, bộ lọc tức thì)
* `/nha-cung-cap` -> **HTTP 200 OK**
* `/inbound` -> **HTTP 200 OK**
* `/outbound` -> **HTTP 200 OK**
* `/the-kho` -> **HTTP 200 OK**

---

## 6. HƯỚNG DẪN TRẢI NGHIỆM

1. Mở trình duyệt truy cập: **[http://127.0.0.1:8000/login](http://127.0.0.1:8000/login)**
2. Quan sát khung đăng nhập:
   * Không còn bất kỳ chữ `\n` nào ở nền bên phải.
   * Bấm nút tài khoản demo **Nguyễn Thành Hưng** hoặc **Hoàng Tiến Đạt** để điền nhanh thông tin và đăng nhập.
3. Trên trang Dashboard:
   * Quan sát biểu tượng **Mặt trăng / Mặt trời** trên thanh Topbar: Bấm vào để trải nghiệm chuyển đổi mượt mà giữa chế độ Sáng (KiotViet) và Tối (Dark Mode).
   * Khối Trợ lý AI ở cột bên phải hiển thị đầy đủ icon tam giác vàng, ngọn lửa đỏ và hộp lưu trữ.
   * Thử bấm nút **"Phân tích lại"** để quan sát icon tự động làm mới theo dữ liệu realtime.
4. Truy cập trang **Danh Mục Hàng Hóa**:
   * Kiểm tra cụm nút **+ Thêm Mới** màu xanh ngọc lục bảo chuẩn KiotViet.
   * Thử nghiệm bộ lọc tìm kiếm tức thì và các trạng thái tồn kho an toàn / cảnh báo min.

---

## 7. CẬP NHẬT GIAO DIỆN ĐĂNG NHẬP & XÁC THỰC 3 TÍNH NĂNG AI CỐT LÕI (MỤC 3.2)

### 7.1. Tinh chỉnh Giao diện Đăng nhập (Login Page Clean-up)
- **Xóa bỏ nút/icon thừa phía trên tiêu đề**: Đã gỡ bỏ hoàn toàn khối icon vuông nằm ngay trên dòng chữ *"Đăng Nhập Hệ Thống"*, giúp bố cục form đăng nhập thoáng đãng, cân đối và chuyên nghiệp.
- **Xóa bỏ dòng chữ "Mặc định: 123"**: Đã xóa triệt để dòng chữ gợi ý `Mặc định: 123` ở nhãn mật khẩu và các placeholder, nâng cao tính bảo mật cho giao diện cổng nội bộ.
- **Chuẩn hóa thẻ tài khoản Demo 1-Click**:
  - `Nguyễn Thành Hưng` - Quản Trị Viên
  - `Hoàng Tiến Đạt` - Thủ Kho Trưởng
  - `Hoàng Tiến Đạt` - Kế Toán Kho
  *(Xóa sạch các chuỗi `(admin123)`, `(thukho123)`, `(ketoan123)` hiển thị thô, tích hợp hàm điền ngầm mượt mà).*

### 7.2. Kết quả Xác thực 3 Tính Năng AI Cốt Lõi (Mục 3.2)
Hệ thống đã kiểm thử thực tế và đối soát trực tiếp qua API `POST /api/v1/ai/generate-report` và `GET /api/v1/ai/advisory` kết nối mô hình trực tuyến **Google Gemini 3.5 Flash Lite** (hoạt động đồng thời với Local Grounded Engine):

1. **Báo cáo Nhập - Xuất - Tồn theo tháng (Monthly Inventory Report Generation)**:
   - Tự động trích xuất lịch sử kho 30 ngày gần nhất qua `aggregate_warehouse_data_30d()`.
   - Phân tích toàn diện 75 SKU, phát hiện 29 SKU chạm hoặc dưới ngưỡng tồn min và 31 SKU không phát sinh xuất trên 60 ngày.
   - Trợ lý AI đưa ra đánh giá điều hành tổng quan sắc bén, phản ánh khách quan rủi ro đứt gãy hàng hóa và chi phí ứ đọng vốn lưu kho.

2. **Gợi ý Nhập hàng Thông minh (Smart Restock Suggestions)**:
   - Tính toán tự động theo công thức: `Đề xuất nhập = Thiếu hụt tồn min + (Tốc độ tiêu thụ ngày × 15 ngày đệm)`.
   - Đánh giá mức độ ưu tiên: Phân cấp `KHAN_CAP` (khi tồn &le; 30% min) và `CANH_BAO`.
   - Ví dụ thực nghiệm: Mặt hàng *Xi măng Vicem Bút Sơn PCB40* (tồn 15, min 80, tốc độ xuất 2.5 bao/ngày) &rarr; AI khuyến nghị nhập khẩn cấp **+102 bao**.

3. **Tóm tắt & Cảnh báo Biến động Bất thường (Anomaly Summarization & Alerts)**:
   - **Xuất tăng đột biến (High Burn Rate)**: Tự động phát hiện các mặt hàng có vận tốc tiêu thụ vượt ngưỡng (ví dụ: *Bu lông kết cấu M16x80* đạt 3.33 đơn vị/ngày).
   - **Hàng tồn kho ứ đọng lâu (> 60 ngày)**: Phát hiện và liệt kê danh sách Dead Stock (ví dụ: *Bu lông neo móng M24x800* ứ đọng 120 chiếc) kèm khuyến nghị giải phóng mặt bằng, thanh lý thu hồi dòng tiền.

4. **Bảo mật Dữ liệu Kinh doanh (Data Sanitizer)**:
   - Đã kiểm tra và đảm bảo 100% giá vốn nhạy cảm (`DonGiaNhap`, `ThanhTien`, `GiaVon`) bị loại bỏ triệt để trước khi truyền vào AI context.
   - Bảng điều khiển Dashboard và Modal Báo Cáo 3 Phần đã được nâng cấp JavaScript để đồng bộ cập nhật dữ liệu Phần 3 ngay khi người dùng nhấn *"Phân tích lại"*.
