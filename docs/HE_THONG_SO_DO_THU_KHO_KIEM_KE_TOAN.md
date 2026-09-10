# HỆ THỐNG SƠ ĐỒ KỸ THUẬT KIẾN TRÚC SMARTLOGIS AI V2.0
## CHUẨN HÓA MÔ HÌNH VAI TRÒ "THỦ KHO KIÊM KẾ TOÁN" (MERMAID.JS ARCHITECT)
**Dự án:** SmartLogis AI - Hệ Thống Quản Lý Kho Tích Hợp AI  
**Tiêu chuẩn thiết kế:** Cú pháp Mermaid.js chuẩn hóa theo Skill `diagram-architect`  
**Cơ cấu nhân sự dự án (02 Thành viên Scrum):**
- **Nguyễn Thành Hưng:** Product Owner / Lead Backend Developer $\rightarrow$ Vai trò hệ thống: **Admin (Quản trị viên)**
- **Hoàng Tiến Đạt:** Scrum Master / Frontend Developer & Tester $\rightarrow$ Vai trò hệ thống: **Thủ kho kiêm Kế toán (Storekeeper & Accountant)**
- **Dịch vụ tích hợp bên ngoài:** **Trợ lý AI (Google Gemini 1.5 Flash API)**

---

## MỤC LỤC HỆ THỐNG SƠ ĐỒ
1. [Sơ đồ Use Case Tổng Quát (Hình 4.1)](#1-sơ-đồ-use-case-tổng-quát-hình-41)
2. [Sơ đồ Use Case Phân Hệ Nghiệp Vụ Kho & Chống Tồn Âm (Hình 4.1.1)](#2-sơ-đồ-use-case-phân-hệ-nghiệp-vụ-kho--chống-tồn-âm-hình-411)
3. [Sơ đồ Use Case Phân Hệ Trợ Lý AI Gemini (Hình 4.1.2)](#3-sơ-đồ-use-case-phân-hệ-trợ-lý-ai-gemini-hình-412)
4. [Sơ đồ Trình Tự Lập Phiếu Xuất Kho & Khóa Chống Tồn Âm (Hình 4.2.1)](#4-sơ-đồ-trình-tự-lập-phiếu-xuất-kho--khóa-chống-tồn-âm-hình-421)
5. [Sơ đồ Trình Tự AI Sinh Báo Cáo Nhập - Xuất - Tồn (Hình 4.2.2)](#5-sơ-đồ-trình-tự-ai-sinh-báo-cáo-nhập---xuất---tồn-hình-422)
6. [Sơ đồ Trình Tự Lập Phiếu Nhập Kho (Inbound Transaction) (Hình 4.2.3)](#6-sơ-đồ-trình-tự-lập-phiếu-nhập-kho-inbound-transaction-hình-423)
7. [Sơ đồ Trình Tự Tra Cứu Thẻ Kho & Cảnh Báo Tồn Min (Hình 4.2.4)](#7-sơ-đồ-trình-tự-tra-cứu-thẻ-kho--cảnh-báo-tồn-min-hình-424)
8. [Sơ đồ Trình Tự Xuất Báo Cáo Excel / PDF (Hình 4.2.5)](#8-sơ-đồ-trình-tự-xuất-báo-cáo-excel--pdf-hình-425)
9. [Sơ đồ Trình Tự Đăng Nhập & Phân Quyền JWT (Hình 4.2.6)](#9-sơ-đồ-trình-tự-đăng-nhập--phân-quyền-jwt-hình-426)
10. [Sơ đồ Thực Thể Quan Hệ Cơ Sở Dữ Liệu MySQL 8.0 (Hình 4.3.3)](#10-sơ-đồ-thực-thể-quan-hệ-cơ-sở-dữ-liệu-mysql-80-hình-433)
11. [Sơ đồ Hoạt Động (Activity) Xuất Kho Chống Tồn Âm (Hình 4.4.1)](#11-sơ-đồ-hoạt-động-activity-xuất-kho-chống-tồn-âm-hình-441)
12. [Sơ đồ Hoạt Động (Activity) Trợ Lý AI & Data Sanitizer (Hình 4.4.2)](#12-sơ-đồ-hoạt-động-activity-trợ-lý-ai--data-sanitizer-hình-442)
13. [Sơ đồ Lớp (Class Diagram) Backend FastAPI & Domain Services (Hình 4.5.1)](#13-sơ-đồ-lớp-class-diagram-backend-fastapi--domain-services-hình-451)
14. [Sơ đồ Kiến Trúc Phân Hệ Chức Năng (Hình 2.2.3)](#14-sơ-đồ-kiến-trúc-phân-hệ-chức-năng-hình-223)

---

## 1. Sơ đồ Use Case Tổng Quát (Hình 4.1)

```mermaid
flowchart LR
    %% Actors Definition
    Admin(["fa:fa-user-shield Quản trị viên\n(Admin)"]):::adminStyle
    Keeper(["fa:fa-user-gear Thủ kho kiêm\nKế toán"]):::keeperStyle
    Gemini(["fa:fa-brain Trợ lý AI\n(Google Gemini)"]):::aiStyle

    %% Subsystems Definition
    subgraph S1 ["1. QUẢN TRỊ & XÁC THỰC"]
        UC01(["Đăng nhập & Phân quyền JWT"]):::coreUC
        UC02(["Quản lý Danh mục & Người dùng"]):::coreUC
    end

    subgraph S2 ["2. NGHIỆP VỤ KHO & ACID"]
        UC03(["Lập Phiếu Nhập Kho"]):::acidUC
        UC04(["Lập Phiếu Xuất Kho"]):::acidUC
        UC_ACID(["Khóa ACID Chống Tồn Âm"]):::acidUC
    end

    subgraph S3 ["3. THẺ KHO & BÁO CÁO"]
        UC05(["Ghi Sổ & Tra Cứu Thẻ Kho"]):::coreUC
        UC_Alert(["Cảnh Báo Tồn Min & Dashboard"]):::coreUC
        UC08(["Xuất Báo Cáo Excel / PDF"]):::reportUC
    end

    subgraph S4 ["4. TRỢ LÝ AI GEMINI"]
        UC07(["AI Khuyến Nghị Đặt Hàng"]):::reportUC
        UC06(["AI Sinh Báo Cáo Chiến Lược"]):::reportUC
        UC_Sanitize(["Khử Trùng Dữ Liệu Giá Vốn"]):::reportUC
    end

    %% Direct, Uncrossed Actor Connections
    Admin --> S1
    Admin --> S3
    
    Keeper --> S1
    Keeper --> S2
    Keeper --> S3
    Keeper --> S4

    Gemini --> S4

    %% Internal Subsystem Relationships
    UC04 -.->|"<<include>>"| UC_ACID
    UC03 -.->|"<<include>>"| UC05
    UC04 -.->|"<<include>>"| UC05
    UC06 -.->|"<<include>>"| UC_Sanitize
    UC07 -.->|"<<include>>"| UC_Sanitize

    %% Styling
    classDef adminStyle fill:#e0f2fe,stroke:#0284c7,stroke-width:2px,color:#0369a1;
    classDef keeperStyle fill:#ecfdf5,stroke:#059669,stroke-width:2px,color:#047857;
    classDef aiStyle fill:#f5f3ff,stroke:#7c3aed,stroke-width:2px,color:#6d28d9;
    classDef coreUC fill:#ffffff,stroke:#475569,stroke-width:1.5px,color:#0f172a;
    classDef acidUC fill:#fef2f2,stroke:#dc2626,stroke-width:1.5px,color:#991b1b;
    classDef reportUC fill:#fffbeb,stroke:#d97706,stroke-width:1.5px,color:#92400e;
```

---

## 1.1. Sơ đồ Cây Phân Rã Chức Năng Hệ Thống (Hình 4.1a)

```mermaid
graph TD
    Root["<b>HỆ THỐNG QUẢN LÝ KHO SMARTLOGIS AI</b>"]:::rootStyle

    Root --> S1["<b>1. Phân hệ Quản trị & Xác thực</b>"]:::s1Style
    Root --> S2["<b>2. Phân hệ Nghiệp vụ Kho & ACID</b>"]:::s2Style
    Root --> S3["<b>3. Phân hệ Thẻ kho & Báo cáo</b>"]:::s3Style
    Root --> S4["<b>4. Phân hệ Trợ lý AI Gemini</b>"]:::s4Style

    S1 --> F1_1["1.1. Đăng nhập JWT & Phân quyền"]:::leafStyle
    S1 --> F1_2["1.2. Quản lý Tài khoản Người dùng"]:::leafStyle
    S1 --> F1_3["1.3. Quản lý Danh mục Hàng & NCC"]:::leafStyle

    S2 --> F2_1["2.1. Lập Phiếu Nhập Kho"]:::leafStyle
    S2 --> F2_2["2.2. Lập Phiếu Xuất Kho"]:::leafStyle
    S2 --> F2_3["2.3. Khóa Atomic SQL Chống Tồn Âm"]:::leafStyle

    S3 --> F3_1["3.1. Ghi Sổ & Tra Cứu Thẻ Kho"]:::leafStyle
    S3 --> F3_2["3.2. Giám Sát Định Mức Tồn Min"]:::leafStyle
    S3 --> F3_3["3.3. Xuất Báo Cáo Excel / PDF"]:::leafStyle

    S4 --> F4_1["4.1. Khuyến Nghị Đặt Hàng Tối Ưu"]:::leafStyle
    S4 --> F4_2["4.2. AI Sinh Báo Cáo Chiến Lược"]:::leafStyle
    S4 --> F4_3["4.3. Khử Trùng & Bảo Mật Giá Vốn"]:::leafStyle

    classDef rootStyle fill:#0284c7,stroke:#0369a1,stroke-width:2px,color:#ffffff;
    classDef s1Style fill:#e0f2fe,stroke:#0284c7,stroke-width:2px,color:#0369a1;
    classDef s2Style fill:#ecfdf5,stroke:#059669,stroke-width:2px,color:#047857;
    classDef s3Style fill:#fef3c7,stroke:#d97706,stroke-width:2px,color:#92400e;
    classDef s4Style fill:#f5f3ff,stroke:#7c3aed,stroke-width:2px,color:#6d28d9;
    classDef leafStyle fill:#ffffff,stroke:#64748b,stroke-width:1.5px,color:#0f172a;
```

---

## 2. Sơ đồ Use Case Phân Hệ Nghiệp Vụ Kho & Chống Tồn Âm (Hình 4.1.1)

```mermaid
flowchart LR
    Keeper(["fa:fa-user-gear Thủ kho kiêm\nKế toán"]):::keeperStyle
    Admin(["fa:fa-user-shield Quản trị viên\n(Admin)"]):::adminStyle

    subgraph Col1 ["1. NGHIỆP VỤ NHẬP / XUẤT / TRA CỨU"]
        UC_Inbound(["Lập Phiếu Nhập Kho"]):::normalUC
        UC_Outbound(["Lập Phiếu Xuất Kho"]):::criticalUC
        UC_Lookup(["Tra Cứu Thẻ Kho & Báo Cáo"]):::reportUC
    end

    subgraph Col2 ["2. KIỂM SOÁT ACID & SỔ SÁCH"]
        UC_TheKho(["Ghi Sổ Thẻ Kho Lũy Kế"]):::normalUC
        UC_LockStock(["Khóa Atomic SQL Chống Tồn Âm"]):::criticalUC
        UC_Rollback(["Hủy Giao Dịch Khi Thiếu Hàng"]):::criticalUC
    end

    Keeper --> Col1
    Admin --> Col1

    UC_Inbound -.->|"<<include>>"| UC_TheKho
    UC_Outbound -.->|"<<include>>"| UC_LockStock
    UC_Outbound -.->|"<<include>>"| UC_TheKho
    UC_Rollback -.->|"<<extend>>"| UC_Outbound

    classDef keeperStyle fill:#ecfdf5,stroke:#059669,stroke-width:2px,color:#047857;
    classDef adminStyle fill:#e0f2fe,stroke:#0284c7,stroke-width:2px,color:#0369a1;
    classDef normalUC fill:#ffffff,stroke:#475569,stroke-width:1.5px,color:#0f172a;
    classDef criticalUC fill:#fef2f2,stroke:#dc2626,stroke-width:1.5px,color:#991b1b;
    classDef reportUC fill:#fffbeb,stroke:#d97706,stroke-width:1.5px,color:#92400e;
```

---

## 3. Sơ đồ Use Case Phân Hệ Trợ Lý AI Gemini (Hình 4.1.2)

```mermaid
flowchart LR
    User(["fa:fa-user-check Thủ kho kiêm Kế toán\n& Quản trị viên"]):::userStyle
    GeminiAPI(["fa:fa-cloud Google Gemini\n1.5 Flash API"]):::aiStyle

    subgraph Col1 ["1. PHÂN TÍCH & KHUYẾN NGHỊ"]
        UC_Advisory(["Xem Khuyến Nghị Dashboard"]):::ucStyle
        UC_GenReport(["Sinh Báo Cáo Chiến Lược Kho"]):::ucStyle
    end

    subgraph Col2 ["2. BẢO MẬT & DỰ PHÒNG"]
        UC_Sanitizer(["Khử Trùng & Lọc Giá Vốn (Sanitizer)"]):::securityUC
        UC_Grounded(["Grounded Prompting Chống Ảo Giác"]):::ucStyle
        UC_Fallback(["Dự Phòng Cục Bộ (Fallback SQL Engine)"]):::fallbackUC
    end

    User --> Col1
    GeminiAPI --> Col2

    UC_GenReport -.->|"<<include>>"| UC_Sanitizer
    UC_GenReport -.->|"<<include>>"| UC_Grounded
    UC_Advisory -.->|"<<include>>"| UC_Sanitizer
    UC_Fallback -.->|"<<extend>>"| UC_GenReport

    classDef userStyle fill:#e0f2fe,stroke:#0284c7,stroke-width:2px,color:#0369a1;
    classDef aiStyle fill:#f5f3ff,stroke:#7c3aed,stroke-width:2px,color:#6d28d9;
    classDef ucStyle fill:#ffffff,stroke:#6d28d9,stroke-width:1.5px,color:#4c1d95;
    classDef securityUC fill:#fef2f2,stroke:#dc2626,stroke-width:1.5px,color:#991b1b;
    classDef fallbackUC fill:#f8fafc,stroke:#64748b,stroke-width:1.5px,color:#334155;
```

---

## 4. Sơ đồ Trình Tự Lập Phiếu Xuất Kho & Khóa Chống Tồn Âm (Hình 4.2.1)

```mermaid
sequenceDiagram
    autonumber
    actor Staff as "Thủ kho kiêm Kế toán"
    participant UI as "Web UI (Frontend)"
    participant Router as "FastAPI Outbound Router"
    participant Service as "Outbound Service (ACID)"
    participant DB as "MySQL 8.0 CSDL (InnoDB)"

    Staff ->> UI: 1. Chọn Mã SKU, nhập Số lượng xuất -> Bấm "Xác nhận Xuất"
    activate UI
    UI ->> UI: 2. Validate phía Client: SoLuongXuat <= TonKhaDung?
    UI ->> Router: 3. POST /api/v1/kho/phieu-xuat {MaHH, SoLuongXuat, NguoiNhan, LyDo}
    activate Router

    Router ->> Service: 4. execute_outbound_transaction(payload, user_id)
    activate Service

    Service ->> DB: 5. BEGIN TRANSACTION (ACID)
    activate DB

    Service ->> DB: 6. UPDATE ton_kho SET SoLuongTon = SoLuongTon - :qty, CapNhatCuoi = NOW()<br/>WHERE MaHH = :id AND SoLuongTon >= :qty
    DB -->> Service: 7. rowcount (Số dòng cập nhật thành công)

    alt rowcount == 0 (Nguy cơ TỒN ÂM / Xung đột đồng thời)
        Note over Service, DB: PHÁT HIỆN THIẾU TỒN KHO - BẢO VỆ AN TOÀN ACID
        Service ->> DB: 8. ROLLBACK TRANSACTION
        DB -->> Service: Rollback Completed
        Service -->> Router: 9. HTTP 400 Bad Request ("Số lượng xuất vượt quá tồn kho khả dụng")
        Router -->> UI: 10. HTTP 400 Bad Request
        UI -->> Staff: 11. Bật cảnh báo đỏ rực rỡ, từ chối giao dịch
    else rowcount == 1 (Cập nhật nguyên tử hợp lệ)
        Service ->> DB: 12. INSERT INTO phieu_xuat (MaPX, NgayXuat, MaND, NguoiNhan, LyDoXuat)
        Service ->> DB: 13. INSERT INTO chi_tiet_phieu_xuat (MaPX, MaHH, SoLuongXuat)
        Service ->> DB: 14. INSERT INTO the_kho (NgayGiaoDich, MaHH, MaChungTu, LoaiGD='XUAT', SoLuongThayDoi=-qty, TonSauGiaoDich)
        Service ->> DB: 15. COMMIT TRANSACTION
        deactivate DB
        Service -->> Router: 16. HTTP 201 Created (Chi tiết phiếu xuất & Thẻ kho)
        deactivate Service
        Router -->> UI: 17. HTTP 201 Created
        deactivate Router
        UI -->> Staff: 18. Cập nhật tồn kho Real-time & Hiển thị thông báo thành công
    end
    deactivate UI
```

---

## 5. Sơ đồ Trình Tự AI Sinh Báo Cáo Nhập - Xuất - Tồn (Hình 4.2.2)

```mermaid
sequenceDiagram
    autonumber
    actor User as "Thủ kho kiêm Kế toán / Admin"
    participant UI as "Web UI (Dashboard / AI Modal)"
    participant Router as "FastAPI AI Router"
    participant Service as "AIService & Aggregator"
    participant Sanitizer as "Data Sanitizer"
    participant DB as "MySQL 8.0 CSDL"
    participant Gemini as "Google Gemini API"

    User ->> UI: 1. Bấm nút "Sinh Báo Cáo Phân Tích AI"
    activate UI
    UI ->> Router: 2. POST /api/v1/ai/generate-report
    activate Router

    Router ->> Service: 3. generate_full_ai_report(db)
    activate Service

    Service ->> DB: 4. Query dữ liệu biến động 30 ngày (Nhập, Xuất, Tồn, Dead Stock)
    activate DB
    DB -->> Service: 5. Raw Warehouse Dataset (Chứa DonGiaNhap)
    deactivate DB

    Service ->> Sanitizer: 6. sanitize_warehouse_data(raw_data)
    activate Sanitizer
    Note over Sanitizer: LOẠI BỎ 100% ĐƠN GIÁ NHẬP & BẢO MẬT GIÁ VỐN
    Sanitizer -->> Service: 7. Sanitized Clean Context JSON
    deactivate Sanitizer

    Service ->> Service: 8. Đóng gói Grounded Prompt Template (Strict Anti-Hallucination)

    alt Kết nối Google Gemini API thành công
        Service ->> Gemini: 9. POST /v1beta/models/gemini-1.5-flash:generateContent (Prompt)
        activate Gemini
        Gemini -->> Service: 10. 200 OK (Cấu trúc JSON 3 phần: Tổng quan, Cảnh báo min, Bất thường)
        deactivate Gemini
    else Lỗi kết nối / Quota 429 / Timeout > 6s
        Note over Service: TỰ ĐỘNG CHUYỂN HƯỚNG SANG CƠ CHẾ FAST FALLBACK
        Service ->> Service: 11. Kích hoạt Local Grounded Fallback Engine (< 0.2s)
        Service ->> DB: 12. Query SQL phân tích định mức tồn min trực tiếp
        DB -->> Service: 13. Fallback Dataset
        Service ->> Service: 14. Tổng hợp báo cáo chuẩn hóa nội bộ
    end

    Service -->> Router: 15. Báo cáo phân tích hoàn chỉnh (JSON + Markdown)
    deactivate Service
    Router -->> UI: 16. HTTP 200 OK (Render Modal Báo cáo)
    deactivate Router
    UI -->> User: 17. Hiển thị Báo cáo điều hành & Cho phép Tải / In / Đối soát
    deactivate UI
```

---

## 6. Sơ đồ Trình Tự Lập Phiếu Nhập Kho (Inbound Transaction) (Hình 4.2.3)

```mermaid
sequenceDiagram
    autonumber
    actor Staff as "Thủ kho kiêm Kế toán"
    participant UI as "Web UI (Form Lập Phiếu Nhập)"
    participant Router as "FastAPI Inventory Router"
    participant Service as "Inbound Service (ACID)"
    participant DB as "MySQL 8.0 CSDL (InnoDB)"

    Staff ->> UI: 1. Chọn NCC, thêm danh sách SKU, số lượng nhập (>0) & đơn giá
    activate UI
    UI ->> Router: 2. POST /api/v1/kho/phieu-nhap (PhieuNhapCreate payload)
    activate Router

    Router ->> Service: 3. execute_inbound_transaction(payload, user_id)
    activate Service

    Service ->> DB: 4. BEGIN TRANSACTION (Atomic ACID)
    activate DB
    Service ->> DB: 5. INSERT INTO phieu_nhap (MaPN, NgayNhap, MaNCC, MaND, TongTien, GhiChu)
    Service ->> DB: 6. INSERT INTO chi_tiet_phieu_nhap (MaPN, MaHH, SoLuongNhap, DonGiaNhap, ThanhTien)
    Service ->> DB: 7. UPDATE ton_kho SET SoLuongTon = SoLuongTon + :qty, CapNhatCuoi = NOW()<br/>WHERE MaHH = :id
    Service ->> DB: 8. INSERT INTO the_kho (NgayGiaoDich, MaHH, MaChungTu, LoaiGD='NHAP', SoLuongThayDoi=+qty, TonSauGiaoDich)
    Service ->> DB: 9. COMMIT TRANSACTION
    DB -->> Service: 10. Commit Confirmed (Success)
    deactivate DB

    Service -->> Router: 11. HTTP 201 Created (Chi tiết phiếu nhập đã lưu)
    deactivate Service
    Router -->> UI: 12. HTTP 201 Created & WebSocket Broadcast INVENTORY_UPDATED
    deactivate Router
    UI -->> Staff: 13. Thông báo nhập kho thành công & Cập nhật số dư kho tức thời
    deactivate UI
```

---

## 7. Sơ đồ Trình Tự Tra Cứu Thẻ Kho & Cảnh Báo Tồn Min (Hình 4.2.4)

```mermaid
sequenceDiagram
    autonumber
    actor Staff as "Thủ kho kiêm Kế toán"
    participant UI as "Web UI (Dashboard / Thẻ Kho)"
    participant Router as "FastAPI Inventory Router"
    participant DB as "MySQL 8.0 Database"

    Staff ->> UI: 1. Truy cập màn hình Thẻ kho & Chọn Mã SKU cần đối soát
    activate UI
    UI ->> Router: 2. GET /api/v1/kho/the-kho/{ma_hh}
    activate Router

    Router ->> DB: 3. SELECT * FROM the_kho WHERE MaHH = :id ORDER BY NgayGiaoDich ASC
    activate DB
    DB -->> Router: 4. Danh sách bản ghi biến động thẻ kho lũy kế
    deactivate DB
    Router -->> UI: 5. HTTP 200 OK (Danh sách dòng thẻ kho chi tiết)
    deactivate Router

    par Quá trình tự động giám sát cảnh báo tồn
        UI ->> Router: 6. GET /api/v1/kho/canh-bao-ton-kho
        activate Router
        Router ->> DB: 7. SELECT h.MaHH, h.TenHH, t.SoLuongTon, h.TonToiThieu<br/>FROM ton_kho t JOIN hang_hoa h ON t.MaHH = h.MaHH<br/>WHERE t.SoLuongTon <= h.TonToiThieu
        activate DB
        DB -->> Router: 8. Danh sách mặt hàng chạm/dưới ngưỡng an toàn
        deactivate DB
        Router -->> UI: 9. HTTP 200 OK (Danh sách cảnh báo tồn min)
        deactivate Router
    end

    UI -->> Staff: 10. Hiển thị bảng biến động lũy kế và Bật Badge cảnh báo đỏ trên Dashboard
    deactivate UI
```

---

## 8. Sơ đồ Trình Tự Xuất Báo Cáo Excel / PDF (Hình 4.2.5)

```mermaid
sequenceDiagram
    autonumber
    actor Staff as "Thủ kho kiêm Kế toán / Admin"
    participant UI as "Web UI (Reports / Dashboard)"
    participant Router as "FastAPI Reports Router"
    participant ExportGen as "OpenPyXL Export Generator"
    participant DB as "MySQL 8.0 CSDL"

    Staff ->> UI: 1. Bấm nút "Xuất Báo Cáo Excel" (Tồn kho / Nhập - Xuất - Tồn)
    activate UI
    UI ->> Router: 2. GET /api/v1/reports/export/excel (Bearer Token JWT)
    activate Router

    Router ->> Router: 3. require_role(['Admin', 'Thukho']) -> Xác thực quyền hợp lệ!
    Router ->> DB: 4. Query toàn bộ danh mục hàng hóa, số dư tồn kho & định mức an toàn
    activate DB
    DB -->> Router: 5. Tập dữ liệu báo cáo đối soát thực tế
    deactivate DB

    Router ->> ExportGen: 6. build_inventory_excel_workbook(data)
    activate ExportGen
    ExportGen ->> ExportGen: 7. Định dạng tiêu đề doanh nghiệp, Header màu sắc, highlight tồn min, tính tổng lũy kế
    ExportGen -->> Router: 8. BytesIO Binary Stream hoàn chỉnh
    deactivate ExportGen

    Router -->> UI: 9. StreamingResponse (application/vnd.openxmlformats..., Content-Disposition: attachment)
    deactivate Router
    UI -->> Staff: 10. Trình duyệt tự động tải tệp BaoCao_NhapXuatTon_SmartLogis_*.xlsx
    deactivate UI
```

---

## 9. Sơ đồ Trình Tự Đăng Nhập & Phân Quyền JWT (Hình 4.2.6)

```mermaid
sequenceDiagram
    autonumber
    actor User as "Người Dùng (Admin / Thủ kho kiêm KT)"
    participant UI as "Web UI (Form /login)"
    participant Router as "FastAPI Auth Router"
    participant Security as "Security Service (Bcrypt/JWT)"
    participant DB as "MySQL 8.0 CSDL"

    User ->> UI: 1. Nhập Tên đăng nhập và Mật khẩu
    activate UI
    UI ->> Router: 2. POST /api/v1/auth/login (TenDangNhap, MatKhau)
    activate Router

    Router ->> DB: 3. SELECT * FROM nguoi_dung WHERE TenDangNhap = :u AND KichHoat = true
    activate DB
    DB -->> Router: 4. Bản ghi NguoiDung (Bcrypt Hash, VaiTro: 'Admin' hoặc 'Thukho')
    deactivate DB

    Router ->> Security: 5. verify_password(plain, hash)
    activate Security
    Security -->> Router: 6. Mật khẩu chính xác (True)
    deactivate Security

    Router ->> Security: 7. create_access_token(payload: {sub, mand, vaitro, hoten})
    activate Security
    Security -->> Router: 8. Chuỗi mã hóa JWT Access Token (HS256)
    deactivate Security

    Router -->> UI: 9. HTTP 200 OK + Set-Cookie: access_token=Bearer ... (HttpOnly, SameSite=Lax)
    deactivate Router
    UI -->> User: 10. Chuyển hướng vào Dashboard theo quyền hạn (Admin: Toàn quyền; Thukho: Vận hành kho & Báo cáo)
    deactivate UI
```

---

## 10. Sơ đồ Thực Thể Quan Hệ Cơ Sở Dữ Liệu MySQL 8.0 (Hình 4.3.3)

```mermaid
erDiagram
    NGUOI_DUNG ||--o{ PHIEU_NHAP : "lap_phieu_nhap"
    NGUOI_DUNG ||--o{ PHIEU_XUAT : "lap_phieu_xuat"
    NHA_CUNG_CAP ||--o{ PHIEU_NHAP : "cung_cap"
    NHOM_HANG ||--o{ HANG_HOA : "phan_loai"
    DON_VI_TINH ||--o{ HANG_HOA : "dinh_luong"
    HANG_HOA ||--|| TON_KHO : "so_du_kha_dung"
    HANG_HOA ||--o{ THE_KHO : "luu_vet_bien_dong"
    PHIEU_NHAP ||--|{ CHI_TIET_PHIEU_NHAP : "chua_dong_hang"
    HANG_HOA ||--o{ CHI_TIET_PHIEU_NHAP : "duoc_nhap"
    PHIEU_XUAT ||--|{ CHI_TIET_PHIEU_XUAT : "chua_dong_hang"
    HANG_HOA ||--o{ CHI_TIET_PHIEU_XUAT : "duoc_xuat"

    NGUOI_DUNG {
        int MaND PK "Khóa chính tự tăng"
        string TenDangNhap UK "Tên đăng nhập duy nhất"
        string MatKhau "Bcrypt Hash an toàn"
        string HoTen "Họ và tên hiển thị"
        string VaiTro "Admin | Thukho (Thủ kho kiêm Kế toán)"
        boolean KichHoat "Trạng thái kích hoạt"
        datetime NgayTao "Thời điểm tạo"
    }

    NHOM_HANG {
        string MaNhom PK "Mã nhóm hàng (NH-THEP...)"
        string TenNhom "Tên nhóm hàng hóa"
        text MoTa "Mô tả phân loại"
    }

    DON_VI_TINH {
        string MaDVT PK "Mã đơn vị tính"
        string TenDVT "Tên đơn vị (Cuộn, Cây, Thùng...)"
    }

    NHA_CUNG_CAP {
        string MaNCC PK "Mã đối tác cung ứng"
        string TenNCC "Tên nhà cung cấp"
        string DiaChi "Địa chỉ đối tác"
        string SoDienThoai "Số điện thoại liên hệ"
        string Email "Email giao dịch"
    }

    HANG_HOA {
        string MaHH PK "Mã SKU vật tư"
        string TenHH "Tên hàng hóa"
        string MaNhom FK "Thuộc nhóm hàng"
        string MaDVT FK "Đơn vị tính"
        int TonToiThieu "Định mức tồn an toàn"
        text MoTa "Thông số quy cách"
    }

    TON_KHO {
        string MaHH PK, FK "Khóa chính kiêm khóa ngoại 1-1"
        int SoLuongTon "CHECK (SoLuongTon >= 0)"
        datetime CapNhatCuoi "Thời điểm cập nhật"
    }

    PHIEU_NHAP {
        string MaPN PK "Số hiệu chứng từ PN-YYYYMMDD-XXXX"
        datetime NgayNhap "Thời điểm nhập kho"
        string MaNCC FK "Nhà cung cấp"
        int MaND FK "Thủ kho lập phiếu"
        float TongTien "Tổng giá trị nhập"
        string GhiChu "Ghi chú phiếu"
    }

    CHI_TIET_PHIEU_NHAP {
        int MaCTPN PK "Khóa chính tự tăng"
        string MaPN FK "Thuộc phiếu nhập"
        string MaHH FK "Hàng hóa nhập"
        int SoLuongNhap "CHECK (SoLuongNhap > 0)"
        float DonGiaNhap "CHECK (DonGiaNhap >= 0)"
        float ThanhTien "Thành tiền dòng nhập"
    }

    PHIEU_XUAT {
        string MaPX PK "Số hiệu chứng từ PX-YYYYMMDD-XXXX"
        datetime NgayXuat "Thời điểm xuất kho"
        int MaND FK "Thủ kho lập phiếu"
        string NguoiNhan "Đơn vị / Người nhận"
        string LyDoXuat "Mục đích xuất kho"
    }

    CHI_TIET_PHIEU_XUAT {
        int MaCTPX PK "Khóa chính tự tăng"
        string MaPX FK "Thuộc phiếu xuất"
        string MaHH FK "Hàng hóa xuất"
        int SoLuongXuat "CHECK (SoLuongXuat > 0)"
    }

    THE_KHO {
        int MaTK PK "Khóa chính tự tăng"
        datetime NgayGiaoDich "Thời điểm giao dịch"
        string MaHH FK "Mặt hàng biến động"
        string MaChungTu "Số hiệu chứng từ gốc (PN/PX)"
        string LoaiGiaoDich "NHAP hoặc XUAT"
        int SoLuongThayDoi "+N khi nhập, -N khi xuất"
        int TonSauGiaoDich "CHECK (TonSauGiaoDich >= 0)"
    }
```

---

## 11. Sơ đồ Hoạt Động (Activity) Xuất Kho Chống Tồn Âm (Hình 4.4.1)

```mermaid
flowchart TD
    StartNode([Khởi đầu]) --> Action1["Thủ kho kiêm Kế toán chọn Hàng hóa & Nhập số lượng xuất"]
    Action1 --> Action2["Giao diện Frontend tiền kiểm định:\nSoLuongXuat <= TonKhaDung"]
    Action2 --> Action3["Gửi yêu cầu POST /api/v1/kho/phieu-xuat tới FastAPI Backend"]
    Action3 --> Action4["FastAPI mở Database Transaction (ACID) trên MySQL 8.0"]
    Action4 --> Action5["Thực thi câu lệnh cập nhật nguyên tử có điều kiện:\nUPDATE ton_kho SET SoLuongTon = SoLuongTon - :qty\nWHERE MaHH = :id AND SoLuongTon >= :qty"]
    Action5 --> Decision1{"Số dòng bị tác động\n(rowcount == 1)?"}

    Decision1 -- "KHÔNG ĐỦ TỒN (rowcount = 0)" --> ErrorBranch["Phát hiện vi phạm điều kiện tồn kho"]
    ErrorBranch --> Rollback["Thực thi ROLLBACK TRANSACTION toàn phần"]
    Rollback --> ErrorMsg["Trả về mã lỗi HTTP 400 Bad Request:\n'Số lượng yêu cầu vượt quá tồn khả dụng'"]
    ErrorMsg --> AlertUI["Giao diện đổi màu viền đỏ cảnh báo & Giữ nguyên số dư tồn"]
    AlertUI --> EndNode([Kết thúc])

    Decision1 -- "ĐỦ TỒN HÀNG (rowcount = 1)" --> SuccessBranch["Ghi bản ghi Master PhieuXuat và Detail ChiTietPhieuXuat"]
    SuccessBranch --> WriteTheKho["Ghi nhận Sổ Thẻ Kho:\nLoaiGD = 'XUAT', SoLuongThayDoi = -qty, TonSauGiaoDich"]
    WriteTheKho --> Commit["Thực thi COMMIT TRANSACTION ghi nhận vĩnh viễn"]
    Commit --> SuccessMsg["Trả về HTTP 201 Created kèm thông tin chứng từ"]
    SuccessMsg --> UpdateUI["Giao diện cập nhật số dư tồn kho thời gian thực"]
    UpdateUI --> EndNode

    classDef startEnd fill:#0f172a,stroke:#0f172a,color:#ffffff,font-weight:bold;
    classDef action fill:#f8fafc,stroke:#334155,stroke-width:1.5px,color:#0f172a;
    classDef condition fill:#fef3c7,stroke:#d97706,stroke-width:2px,color:#92400e;
    classDef success fill:#dcfce7,stroke:#16a34a,stroke-width:1.5px,color:#14532d;
    classDef error fill:#fee2e2,stroke:#dc2626,stroke-width:1.5px,color:#7f1d1d;

    class StartNode,EndNode startEnd;
    class Action1,Action2,Action3,Action4,Action5 action;
    class Decision1 condition;
    class SuccessBranch,WriteTheKho,Commit,SuccessMsg,UpdateUI success;
    class ErrorBranch,Rollback,ErrorMsg,AlertUI error;
```

---

## 12. Sơ đồ Hoạt Động (Activity) Trợ Lý AI & Data Sanitizer (Hình 4.4.2)

```mermaid
flowchart TD
    StartAI([Bắt đầu yêu cầu AI]) --> Req["Thủ kho kiêm Kế toán / Admin yêu cầu\nSinh Báo Cáo Phân Tích Chiến Lược"]
    Req --> Aggregate["Data Aggregator truy vấn dữ liệu kho 30 ngày từ MySQL 8.0\n(Số lượng nhập, xuất, tồn, định mức tồn min, dead stock)"]
    Aggregate --> Sanitize["Data Sanitizer xử lý khử nhạy cảm:\nLỌC BỎ 100% ĐƠN GIÁ NHẬP & BẢO MẬT GIÁ VỐN"]
    Sanitize --> Ground["Đóng gói dữ liệu sạch vào Grounded Prompt Template\n(Kèm System Prompt chống ảo giác)"]
    Ground --> CallAPI["Gửi Request HTTPS tới Google Gemini 1.5 Flash API"]
    CallAPI --> CheckAPI{"Kết nối Gemini API\nthành công?"}

    CheckAPI -- "THÀNH CÔNG (200 OK)" --> ParseJSON["Output Parser phân tích cú pháp JSON có cấu trúc 3 phần"]
    ParseJSON --> RenderReport["Hiển thị Báo cáo điều hành & Gợi ý bổ sung hàng trên Dashboard"]
    RenderReport --> EndAI([Hoàn thành])

    CheckAPI -- "MẤT KẾT NỐI / TIMEOUT / 429" --> TriggerFallback["Kích hoạt Local Grounded Fallback Engine (< 0.2s)"]
    TriggerFallback --> LocalSQL["Truy vấn CSDL MySQL 8.0 tính toán trực tiếp mức độ thiếu hụt"]
    LocalSQL --> RenderFallback["Hiển thị báo cáo thống kê cục bộ kèm thông báo chế độ Fallback"]
    RenderFallback --> EndAI

    classDef startEnd fill:#0f172a,stroke:#0f172a,color:#ffffff,font-weight:bold;
    classDef step fill:#f3e8ff,stroke:#7e22ce,stroke-width:1.5px,color:#581c87;
    classDef check fill:#fef3c7,stroke:#d97706,stroke-width:2px,color:#92400e;
    classDef success fill:#dcfce7,stroke:#16a34a,stroke-width:1.5px,color:#14532d;
    classDef fallback fill:#fee2e2,stroke:#dc2626,stroke-width:1.5px,color:#7f1d1d;

    class StartAI,EndAI startEnd;
    class Req,Aggregate,Sanitize,Ground,CallAPI step;
    class CheckAPI check;
    class ParseJSON,RenderReport success;
    class TriggerFallback,LocalSQL,RenderFallback fallback;
```

---

## 13. Sơ đồ Lớp (Class Diagram) Backend FastAPI & Domain Services (Hình 4.5.1)

```mermaid
classDiagram
    class InventoryRouter {
        -prefix: str = "/api/v1/kho"
        -auth_service: AuthService
        +api_create_item(item_in: HangHoaCreate)
        +api_tao_phieu_nhap(phieu_in: PhieuNhapCreate)
        +api_tao_phieu_xuat(phieu_in: PhieuXuatCreate)
        +api_get_the_kho(ma_hh: str)
        +api_get_canh_bao_ton()
    }

    class AIRouter {
        -prefix: str = "/api/v1/ai"
        -ai_service: AIService
        +api_get_ai_advisory()
        +api_generate_ai_report()
        +api_get_raw_context()
    }

    class ReportsRouter {
        -prefix: str = "/api/v1/reports"
        -report_service: InventoryService
        +api_export_excel(db: Session, current_user: NguoiDung)
        +api_export_suppliers_excel(db: Session)
    }

    class AuthRouter {
        -prefix: str = "/api/v1/auth"
        -sec_service: SecurityService
        +api_login(credentials: OAuth2PasswordRequestForm)
        +api_get_me(current_user: NguoiDung)
        +api_logout()
    }

    class InboundService {
        -db: Session
        +execute_inbound_transaction(phieu_in: PhieuNhapCreate, user_id: int)
        +update_stock_increase(ma_hh: str, qty: int)
        +append_the_kho(ma_hh: str, loai: str, qty: int)
    }

    class OutboundService {
        -db: Session
        +execute_outbound_transaction(phieu_in: PhieuXuatCreate, user_id: int)
        +atomic_sql_decrement(ma_hh: str, qty: int)
        +validate_zero_negative_stock(ma_hh: str, qty: int)
        +append_the_kho(ma_hh: str, loai: str, qty: int)
    }

    class AIService {
        -api_key: str
        -sanitizer: DataSanitizer
        +aggregate_warehouse_data_30d(db: Session)
        +sanitize_warehouse_data(data: dict)
        +generate_full_ai_report(db: Session)
        +local_fallback_analysis(db: Session)
    }

    class SecurityService {
        -SECRET_KEY: str
        -ALGORITHM: str = "HS256"
        +get_password_hash(password: str) str
        +verify_password(plain: str, hashed: str) bool
        +create_access_token(payload: dict) str
        +require_role(roles: list) Callable
    }

    class NguoiDungModel {
        +MaND: int PK
        +TenDangNhap: str UK
        +MatKhau: str
        +HoTen: str
        +VaiTro: str (Admin | Thukho)
        +KichHoat: bool
    }

    InventoryRouter --> InboundService
    InventoryRouter --> OutboundService
    AIRouter --> AIService
    ReportsRouter --> InboundService
    AuthRouter --> SecurityService
    InboundService --> NguoiDungModel
    OutboundService --> NguoiDungModel
```

---

## 14. Sơ đồ Kiến Trúc Phân Hệ Chức Năng (Hình 2.2.3)

```mermaid
flowchart TD
    subgraph PresentationLayer ["1. TẦNG GIAO DIỆN NGƯỜI DÙNG (FRONTEND - JINJA2 SSR & WEBSOCKET REAL-TIME)"]
        UI_Auth["Phân Hệ Xác Thực RBAC\n(Đăng nhập / Phân quyền 2 vai trò:\nAdmin & Thủ kho kiêm Kế toán)"]
        UI_Catalog["Quản Lý Danh Mục & Thẻ Kho\n(CRUD SKU, Đối tác NCC, ĐVT,\nTra cứu sổ thẻ kho biến động)"]
        UI_Ops["Nghiệp Vụ Nhập / Xuất Kho\n(Lập phiếu nhập & Phiếu xuất,\nClient-side Validation chống tồn âm)"]
        UI_Report["Dashboard KPI & Trợ Lý AI / Báo Cáo\n(Cảnh báo tồn min, Widget AI,\nXuất Báo cáo Excel / PDF)"]
    end

    subgraph SecurityLayer ["2. TẦNG XÁC THỰC & BẢO VỆ PHÂN QUYỀN (FASTAPI SECURITY)"]
        JWT_Auth["JWT Middleware & HttpOnly Cookie Handler"]
        RBAC_Guard["RBAC Guard: 2 Vai Trò\n['Admin', 'Thukho']"]
    end

    subgraph BusinessLayer ["3. TẦNG XỬ LÝ NGHIỆP VỤ LÕI (BACKEND DOMAIN SERVICES)"]
        InboundSvc["Inbound Service\n(Atomic ACID Master-Detail)"]
        OutboundSvc["Outbound Service\n(Atomic SQL Decrement,\nChống tồn kho âm tuyệt đối)"]
        AISvc["AI Engine & Data Sanitizer\n(Khử giá vốn, Grounded Prompting,\nFast Fallback Engine < 0.2s)"]
        ReportSvc["Report Service (OpenPyXL)\n(Kết xuất bảng kê Nhập-Xuất-Tồn)"]
    end

    subgraph ExternalAI ["DỊCH VỤ AI ĐÁM MÂY"]
        GeminiCloud["Google Gemini 1.5 Flash API\n(LLM Cloud Service)"]
    end

    subgraph DatabaseLayer ["4. TẦNG CƠ SỞ DỮ LIỆU & LƯU TRỮ (MYSQL 8.0 INNODB / DUAL-DATABASE)"]
        DB_Users["NguoiDung (2 vai trò: Admin / Thukho),\nNhomHang, DonViTinh, NhaCungCap"]
        DB_Stock["TonKho\nCHECK (SoLuongTon >= 0)"]
        DB_Vouchers["PhieuNhap, ChiTietPhieuNhap,\nPhieuXuat, ChiTietPhieuXuat"]
        DB_Ledger["TheKho (Append-only Ledger,\nLưu vết lịch sử và tồn lũy kế)"]
    end

    PresentationLayer -->|RESTful HTTPS / WebSocket| SecurityLayer
    SecurityLayer --> BusinessLayer
    AISvc -->|HTTPS Grounded Prompt| GeminiCloud
    BusinessLayer -->|SQLAlchemy 2.0 Connection Pool| DatabaseLayer

    classDef presStyle fill:#f0fdf4,stroke:#16a34a,stroke-width:1.8px,color:#14532d;
    classDef secStyle fill:#eff6ff,stroke:#2563eb,stroke-width:1.8px,color:#1e3a8a;
    classDef bizStyle fill:#faf5ff,stroke:#7c3aed,stroke-width:1.8px,color:#581c87;
    classDef dbStyle fill:#fffbeb,stroke:#d97706,stroke-width:1.8px,color:#78350f;
    classDef cloudStyle fill:#fdf2f8,stroke:#db2777,stroke-width:1.8px,color:#831843;

    class UI_Auth,UI_Catalog,UI_Ops,UI_Report presStyle;
    class JWT_Auth,RBAC_Guard secStyle;
    class InboundSvc,OutboundSvc,AISvc,ReportSvc bizStyle;
    class DB_Users,DB_Stock,DB_Vouchers,DB_Ledger dbStyle;
    class GeminiCloud cloudStyle;
```
