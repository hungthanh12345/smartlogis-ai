# HỆ THỐNG TÀI LIỆU SƠ ĐỒ THIẾT KẾ KIẾN TRÚC & QUY TRÌNH NGHIỆP VỤ SMARTLOGIS AI
> **Phiên bản:** 2.0 (Chuẩn hóa Kiến trúc phần mềm & Cú pháp Mermaid.js theo Skill `diagram-architect`)  
> **Hệ thống:** Phần mềm Quản lý Kho Thông minh SmartLogis AI  
> **Nhóm thực hiện:** Nguyễn Thành Hưng (Product Owner / Backend) & Hoàng Tiến Đạt (Scrum Master / Frontend & QA)  
> **Cơ sở dữ liệu:** MySQL 8.0 (ACID Engine, InnoDb, Check Constraints)  
> **Trợ lý AI:** Google Gemini 1.5 Flash API (Data Sanitizer & Fallback Rule-based Engine)

---

## MỤC LỤC TỔNG HỢP CÁC SƠ ĐỒ HỆ THỐNG

1. [Sơ đồ 1: Quy trình Scrum trong Phát triển Hệ thống (3 Sprint - 6 Tuần)](#1-sơ-đồ-quy-trình-scrum-trong-phát-triển-hệ-thống) *(Hình 1.5 - `image2.png`)*
2. [Sơ đồ 2: Sơ đồ Cây Phân Rã Chức Năng Hệ Thống (Functional Decomposition)](#2-sơ-đồ-cây-phân-rã-chức-năng-hệ-thống) *(Hình 4.1a - `image20.png`)*
3. [Sơ đồ 3: Sơ đồ Kiến Trúc Phân Hệ Chức Năng Toàn Diện](#3-sơ-đồ-kiến-trúc-phân-hệ-chức-năng-toàn-diện) *(Hình 2.2.3 - `image3.png`)*
4. [Sơ đồ 4: Biểu đồ Use Case Tổng Quát Hệ Thống Quản Lý Kho SmartLogis AI](#4-biểu-đồ-use-case-tổng-quát) *(Hình 4.1 - `image4.png`)*
5. [Sơ đồ 5: Biểu đồ Use Case Phân Hệ Nghiệp Vụ Kho & Chống Tồn Âm (ACID)](#5-biểu-đồ-use-case-phân-hệ-nghiệp-vụ-kho) *(Hình 4.1.1 - `image5.png`)*
6. [Sơ đồ 6: Biểu đồ Use Case Phân Hệ Trợ Lý AI & Khử Trùng Giá Vốn](#6-biểu-đồ-use-case-phân-hệ-trợ-lý-ai) *(Hình 4.1.2 - `image6.png`)*
7. [Sơ đồ 7: Biểu đồ Tuần Tự (Sequence Diagram) - Lập Phiếu Xuất Kho & Khóa ACID](#7-sequence-diagram---lập-phiếu-xuất-kho--khóa-acid) *(Hình 4.2.1 - `image7.png`)*
8. [Sơ đồ 8: Biểu đồ Tuần Tự (Sequence Diagram) - AI Sinh Báo Cáo Nhập - Xuất - Tồn](#8-sequence-diagram---ai-sinh-báo-cáo-nhập---xuất---tồn) *(Hình 4.2.2 - `image8.png`)*
9. [Sơ đồ 9: Biểu đồ Tuần Tự (Sequence Diagram) - Lập Phiếu Nhập Kho & Ghi Sổ Thẻ Kho](#9-sequence-diagram---lập-phiếu-nhập-kho--ghi-sổ-thẻ-kho) *(Hình 4.2.3 - `image9.png`)*
10. [Sơ đồ 10: Biểu đồ Tuần Tự (Sequence Diagram) - Tra Cứu Thẻ Kho & Cảnh Báo Tồn Tối Thiểu](#10-sequence-diagram---tra-cứu-thẻ-kho--cảnh-báo-tồn-tối-thiểu) *(Hình 4.2.4 - `image10.png`)*
11. [Sơ đồ 11: Biểu đồ Tuần Tự (Sequence Diagram) - Xuất Báo Cáo Dữ Liệu Ra File Excel](#11-sequence-diagram---xuất-báo-cáo-dữ-liệu-ra-file-excel) *(Hình 4.2.5 - `image11.png`)*
12. [Sơ đồ 12: Biểu đồ Tuần Tự (Sequence Diagram) - Đăng Nhập & Phân Quyền Truy Cập JWT](#12-sequence-diagram---đăng-nhập--phân-quyền-truy-cập-jwt) *(Hình 4.2.6 - `image12.png`)*
13. [Sơ đồ 13: Sơ đồ Thực Thể Quan Hệ Cơ Sở Dữ Liệu Cụ Thể (Physical Database ERD Schema MySQL 8.0)](#13-sơ-đồ-thực-thể-quan-hệ-cơ-sở-dữ-liệu-cụ-thể-erd) *(Hình 4.3.3 - `image13.png`)*
14. [Sơ đồ 14: Biểu đồ Hoạt Động (Activity Diagram) - Nghiệp Vụ Xuất Kho Chống Tồn Âm Đa Tầng](#14-activity-diagram---nghiệp-vụ-xuất-kho-chống-tồn-âm) *(Hình 4.4.1 - `image14.png`)*
15. [Sơ đồ 15: Biểu đồ Hoạt Động (Activity Diagram) - Trợ Lý AI & Quy Trình Khử Trùng Giá Vốn](#15-activity-diagram---trợ-lý-ai--data-sanitizer) *(Hình 4.4.2 - `image15.png`)*
16. [Sơ đồ 16: Biểu đồ Lớp (Class Diagram) - Kiến Trúc Backend FastAPI & Domain Services](#16-class-diagram---kiến-trúc-backend-fastapi--domain-services) *(Hình 4.5.1 - `image16.png`)*

---

## 1. Sơ đồ Quy trình Scrum trong Phát triển Hệ thống
- **Mã ảnh báo cáo Word:** `word/media/image2.png` *(Hình 1.5)*
- **Ý nghĩa kỹ thuật:** Mô tả vòng đời lặp phát triển 3 Sprint (mỗi Sprint 2 tuần, tổng cộng 6 tuần) từ Product Backlog (10 User Stories) qua Sprint Planning, Sprint Backlog, Sprint Execution (Daily Scrum 15 phút), Sprint Review và Sprint Retrospective. Vòng lặp cải tiến liên tục nối tuần hoàn cho Sprint kế tiếp.

```mermaid
flowchart LR
    PB["Product Backlog\n• 10 User Stories (US01-US10)\n• Ưu tiên nghiệp vụ kho & Prompt AI\n(PO quản lý)"]
    SP["Sprint Planning\n• Lập kế hoạch Sprint\n• Chọn User Stories\n• Ước lượng Story Points\n(Định kỳ 2 tuần)"]
    SB["Sprint Backlog\n• Danh sách task\n• Phân công: Hưng (BE), Đạt (FE)"]

    subgraph SprintExec ["Sprint (2 Tuần)"]
        DS["Daily Scrum (Hằng ngày)\n• Họp 15 phút đồng bộ\n• Tháo gỡ Blockers"]
        Dev["Thực thi Phát triển:\n• Backend & Frontend\n• Xử lý Transaction ACID CSDL\n• Tinh chỉnh Prompt Gemini API\n• Viết Unit & Integration Test"]
        DS --> Dev
    end

    SR["Sprint Review\n• Kiểm thử chấp nhận (UAT)\n• Đạt Definition of Done (DoD)\n• Demo tính năng hoàn chỉnh"]
    Ret["Sprint Retrospective\n• Họp cải tiến quy trình\n• Rút kinh nghiệm cho Sprint tiếp"]

    PB --> SP
    SP --> SB
    SB --> SprintExec
    SprintExec --> SR
    SR --> Ret
    Ret -.->|"Cải tiến liên tục cho Sprint tiếp theo (Vòng lặp 2 tuần)"| SP

    classDef pbStyle fill:#FEF3C7,stroke:#D97706,stroke-width:2px,color:#92400E;
    classDef spStyle fill:#EEF2FF,stroke:#4F46E5,stroke-width:2px,color:#3730A3;
    classDef execStyle fill:#ECFDF5,stroke:#059669,stroke-width:2px,color:#065F46;
    classDef revStyle fill:#F5F3FF,stroke:#7C3AED,stroke-width:2px,color:#5B21B6;
    classDef retStyle fill:#F3F4F6,stroke:#4B5563,stroke-width:2px,color:#1F2937;

    class PB pbStyle;
    class SP,SB spStyle;
    class SprintExec,DS,Dev execStyle;
    class SR revStyle;
    class Ret retStyle;
```

---

## 2. Sơ đồ Cây Phân Rã Chức Năng Hệ Thống
- **Mã ảnh báo cáo Word:** `word/media/image20.png` *(Hình 4.1a)*
- **Ý nghĩa kỹ thuật:** Phân tách phân cấp toàn bộ chức năng SmartLogis AI thành 4 phân hệ chính: Quản trị & Xác thực, Nghiệp vụ Kho & Kiểm soát ACID, Báo cáo & Thống kê Tồn kho, Trợ lý AI & Phân tích Tự động.

```mermaid
flowchart TD
    Root["HỆ THỐNG QUẢN LÝ KHO THÔNG MINH SMARTLOGIS AI"]

    subgraph F1 ["1. Phân hệ Quản trị & Xác thực"]
        F1_1["1.1 Đăng nhập & Xác thực JWT"]
        F1_2["1.2 Phân quyền 3 vai trò (Admin / Thủ kho / Staff)"]
        F1_3["1.3 Quản lý Tài khoản & Trạng thái hoạt động"]
    end

    subgraph F2 ["2. Phân hệ Nghiệp vụ Kho & ACID"]
        F2_1["2.1 Lập phiếu Nhập kho & Ghi sổ thẻ kho tự động"]
        F2_2["2.2 Lập phiếu Xuất kho & Kiểm soát Tồn âm"]
        F2_3["2.3 Khóa Atomic Decrement tại CSDL MySQL 8.0"]
        F2_4["2.4 Quản lý Danh mục (Hàng hóa, ĐVT, Nhóm, NCC)"]
    end

    subgraph F3 ["3. Phân hệ Báo cáo & Đối soát"]
        F3_1["3.1 Tra cứu Sổ thẻ kho lịch sử biến động"]
        F3_2["3.2 Cảnh báo Tồn tối thiểu (TonKho <= TonToiThieu)"]
        F3_3["3.3 Xuất Báo cáo Đối soát kho ra Excel (.xlsx)"]
    end

    subgraph F4 ["4. Phân hệ Trợ lý AI Thông minh"]
        F4_1["4.1 Sinh Báo cáo Nhập-Xuất-Tồn Chiến lược 30 ngày"]
        F4_2["4.2 Data Sanitizer (Khử trùng & Ẩn giá vốn tuyệt đối)"]
        F4_3["4.3 Khuyến nghị nhập hàng Dashboard (Burn-rate)"]
        F4_4["4.4 Động cơ Dự phòng Fallback Offline (Rule-based)"]
    end

    Root --> F1
    Root --> F2
    Root --> F3
    Root --> F4

    classDef rootStyle fill:#1E293B,stroke:#0F172A,stroke-width:2px,color:#FFFFFF;
    classDef f1Style fill:#EFF6FF,stroke:#2563EB,stroke-width:1.5px,color:#1E3A8A;
    classDef f2Style fill:#ECFDF5,stroke:#059669,stroke-width:1.5px,color:#065F46;
    classDef f3Style fill:#FEF3C7,stroke:#D97706,stroke-width:1.5px,color:#92400E;
    classDef f4Style fill:#FAF5FF,stroke:#9333EA,stroke-width:1.5px,color:#581C87;

    class Root rootStyle;
    class F1,F1_1,F1_2,F1_3 f1Style;
    class F2,F2_1,F2_2,F2_3,F2_4 f2Style;
    class F3,F3_1,F3_2,F3_3 f3Style;
    class F4,F4_1,F4_2,F4_3,F4_4 f4Style;
```

---

## 3. Sơ đồ Kiến Trúc Phân Hệ Chức Năng Toàn Diện
- **Mã ảnh báo cáo Word:** `word/media/image3.png` *(Hình 2.2.3)*
- **Ý nghĩa kỹ thuật:** Mô tả luồng tương tác giữa Client Frontend (HTML5/Vanilla CSS/Modern JS), Tầng API Reverse Proxy & Gateway, Backend FastAPI xử lý nghiệp vụ ACID, CSDL MySQL 8.0 InnoDb, và Dịch vụ ngoài Google Gemini 1.5 Flash API.

```mermaid
flowchart TB
    subgraph ClientLayer ["1. TẦNG TRÌNH DIỄN (FRONTEND CLIENT)"]
        UI_Admin["Giao diện Admin (Quản trị hệ thống)"]
        UI_Kho["Giao diện Thủ kho (Nhập / Xuất / Thẻ kho)"]
        UI_Staff["Giao diện Nhân viên (Xem tồn / Cảnh báo / Dashboard)"]
    end

    subgraph GatewayLayer ["2. TẦNG CỔNG DỊCH VỤ & BẢO MẬT"]
        Nginx["Cổng Reverse Proxy / Nginx"]
        AuthMiddleware["JWT Bearer Authentication & RBAC Authorization"]
    end

    subgraph BackendLayer ["3. TẦNG NGHIỆP VỤ LÕI FASTAPI"]
        RouterLayer["API Routers: Auth / Kho / AI / Reports"]
        InventoryService["Inventory Domain Service (ACID Transaction Manager)"]
        AIService["AI Advisory Service (Prompt Engineering & Data Sanitizer)"]
        ReportService["Excel Reporting Engine (OpenPyXL)"]
    end

    subgraph StorageLayer ["4. TẦNG LƯU TRỮ CƠ SỞ DỮ LIỆU"]
        MySQL[("MySQL 8.0 InnoDB Engine\n• Bảng Transaction: PhieuNhap, PhieuXuat, TheKho\n• Bảng Trạng thái: TonKho (CHECK Ton >= 0)\n• Khóa Record Lock / Row-level Lock")]
    end

    subgraph ExternalLayer ["5. TẦNG DỊCH VỤ NGOÀI (EXTERNAL AI)"]
        GeminiAPI["Google Gemini 1.5 Flash API\n• Grounded Prompting\n• Phân tích xu hướng tiêu thụ 30 ngày"]
        FallbackEngine["Local Rule-based Analyzer\n(Động cơ dự phòng khi API ngoại tuyến)"]
    end

    UI_Admin & UI_Kho & UI_Staff -->|HTTP/REST API| Nginx
    Nginx --> AuthMiddleware
    AuthMiddleware --> RouterLayer
    RouterLayer --> InventoryService & AIService & ReportService

    InventoryService -->|SQLAlchemy Atomic Commit/Rollback| MySQL
    ReportService -->|Query Read-only| MySQL
    AIService -->|Query Aggregated DataSet| MySQL
    AIService -->|Data Sanitizer -> HTTPS Prompt| GeminiAPI
    AIService -.->|Khi Timeout > 8s / Lỗi mạng| FallbackEngine

    classDef clientStyle fill:#EFF6FF,stroke:#3B82F6,stroke-width:1.5px,color:#1E40AF;
    classDef gwStyle fill:#F1F5F9,stroke:#64748B,stroke-width:1.5px,color:#334155;
    classDef beStyle fill:#ECFDF5,stroke:#10B981,stroke-width:2px,color:#065F46;
    classDef dbStyle fill:#FEF3C7,stroke:#F59E0B,stroke-width:2px,color:#92400E;
    classDef extStyle fill:#FAF5FF,stroke:#A855F7,stroke-width:2px,color:#6B21A8;

    class UI_Admin,UI_Kho,UI_Staff clientStyle;
    class Nginx,AuthMiddleware gwStyle;
    class RouterLayer,InventoryService,AIService,ReportService beStyle;
    class MySQL dbStyle;
    class GeminiAPI,FallbackEngine extStyle;
```

---

## 4. Biểu đồ Use Case Tổng Quát
- **Mã ảnh báo cáo Word:** `word/media/image4.png` *(Hình 4.1)*
- **Ý nghĩa kỹ thuật:** Toàn bộ 13 ca sử dụng của hệ thống phân bố theo kiến trúc 2 cột. Các Actor người dùng (Admin, Thủ kho kiêm Kế toán, Nhân viên kho) kết nối vào mép trái các Use Case Cột 1; các quan hệ `<<include>>` đi qua hành lang giữa sang Cột 2; Trợ lý AI (Google Gemini 1.5) kết nối vào mép phải.

```mermaid
flowchart LR
    %% Actors bên trái
    Admin(("fa:fa-user-shield Quản Trị Viên\n(Admin)"))
    ThuKho(("fa:fa-warehouse Thủ Kho Kiêm\nKế Toán"))
    NhanVien(("fa:fa-user Nhân Viên Kho\n(Staff)"))

    %% Actor bên phải
    Gemini(("fa:fa-robot Trợ Lý AI\n(Gemini 1.5)"))

    subgraph SystemBoundary ["HỆ THỐNG QUẢN LÝ KHO THÔNG MINH SMARTLOGIS AI"]
        subgraph Col1 ["Phân hệ Use Case Người Dùng Tương Tác"]
            UC_Auth(["Đăng nhập & Phân quyền\n(US01)"])
            UC_UserMgr(["Quản lý Người Dùng\n(US02)"])
            UC_CatMgr(["Quản lý Danh Mục Kho\n(US02)"])
            UC_Inbound(["Lập Phiếu Nhập Kho\n(US03)"])
            UC_Outbound(["Lập Phiếu Xuất Kho\n(US04)"])
            UC_CardQuery(["Tra Cứu Sổ Thẻ Kho\n(US05)"])
            UC_ExportExcel(["Xuất Báo Cáo Excel Tồn\n(US08)"])
            UC_AIReport(["Phân Tích & Báo Cáo AI\n(US07/US09)"])
        end

        subgraph Col2 ["Phân hệ Use Case Hệ Thống & Bảo Mật"]
            UC_AutoCard(["Ghi Sổ Thẻ Kho Tự Động\n(Audit Trail)"])
            UC_AntiNegative(["Kiểm Tra & Chống Tồn Âm\n(CHECK >= 0 & Atomic Lock)"])
            UC_MinAlert(["Cảnh Báo Tồn Tối Thiểu\n(TonKho <= TonMin)"])
            UC_Sanitizer(["Khử Trùng Giá Vốn Nhập\n(Data Sanitizer Bảo mật)"])
            UC_Prompting(["Grounded Prompting\n(Bám sát số liệu thật)"])
        end
    end

    %% Tương tác Actor Admin
    Admin --> UC_Auth
    Admin --> UC_UserMgr
    Admin --> UC_CatMgr
    Admin --> UC_Inbound
    Admin --> UC_Outbound
    Admin --> UC_CardQuery
    Admin --> UC_ExportExcel
    Admin --> UC_AIReport

    %% Tương tác Actor Thủ kho
    ThuKho --> UC_Auth
    ThuKho --> UC_CatMgr
    ThuKho --> UC_Inbound
    ThuKho --> UC_Outbound
    ThuKho --> UC_CardQuery
    ThuKho --> UC_ExportExcel
    ThuKho --> UC_AIReport

    %% Tương tác Actor Nhân viên
    NhanVien --> UC_Auth
    NhanVien --> UC_CardQuery
    NhanVien --> UC_AIReport

    %% Quan hệ Include giữa 2 cột
    UC_Inbound -.->|<<include>>| UC_AutoCard
    UC_Outbound -.->|<<include>>| UC_AutoCard
    UC_Outbound -.->|<<include>>| UC_AntiNegative
    UC_CardQuery -.->|<<include>>| UC_MinAlert
    UC_AIReport -.->|<<include>>| UC_Sanitizer
    UC_AIReport -.->|<<include>>| UC_Prompting

    %% Tương tác Actor Gemini AI bên phải
    UC_Prompting --- Gemini
    UC_Sanitizer --- Gemini

    classDef actorStyle fill:#E0E7FF,stroke:#4338CA,stroke-width:2px,color:#1E1B4B;
    classDef ucStyle fill:#FFFFFF,stroke:#2563EB,stroke-width:1.5px,color:#0F172A;
    classDef incStyle fill:#FEF2F2,stroke:#DC2626,stroke-width:1.5px,color:#991B1B;
    classDef aiStyle fill:#FAF5FF,stroke:#9333EA,stroke-width:2px,color:#581C87;

    class Admin,ThuKho,NhanVien actorStyle;
    class Gemini aiStyle;
    class UC_Auth,UC_UserMgr,UC_CatMgr,UC_Inbound,UC_Outbound,UC_CardQuery,UC_ExportExcel,UC_AIReport ucStyle;
    class UC_AutoCard,UC_AntiNegative,UC_MinAlert,UC_Sanitizer,UC_Prompting incStyle;
```

---

## 5. Biểu đồ Use Case Phân Hệ Nghiệp Vụ Kho
- **Mã ảnh báo cáo Word:** `word/media/image5.png` *(Hình 4.1.1)*
- **Ý nghĩa kỹ thuật:** Tập trung chuyên sâu vào quy trình nghiệp vụ xuất nhập tồn và cơ chế bảo vệ toàn vẹn dữ liệu ACID chống bán khống, chống âm kho.

```mermaid
flowchart LR
    Admin(("fa:fa-user-shield Admin\n(Quản trị viên)"))
    ThuKho(("fa:fa-warehouse Thủ Kho Kiêm\nKế Toán"))
    Staff(("fa:fa-user Nhân Viên Kho\n(Staff)"))

    subgraph KhoBoundary ["PHÂN HỆ NGHIỆP VỤ KHO & CHỐNG TỒN ÂM (ACID)"]
        UC_Nhap(["Lập Phiếu Nhập Kho\n(Inbound Transaction)"])
        UC_Xuat(["Lập Phiếu Xuất Kho\n(Outbound Transaction)"])
        UC_TheKho(["Tra Cứu Thẻ Kho & Báo Cáo\n(Xem biến động & Cảnh báo)"])
        UC_Excel(["Xuất Báo Cáo Excel Tồn\n(Tổng hợp Nhập - Xuất - Tồn)"])

        UC_GhiTheKho(["Ghi Sổ Thẻ Kho Tự Động\n(TheKho Append-only)"])
        UC_KiemTraFrontend(["Thẩm Định Tồn Khả Dụng\n(Chống âm tại Frontend)"])
        UC_LockBackend(["Khóa Atomic Decrement\n(UPDATE SQL chống Race Condition)"])
    end

    Admin --> UC_Nhap
    Admin --> UC_Xuat
    Admin --> UC_TheKho
    Admin --> UC_Excel

    ThuKho --> UC_Nhap
    ThuKho --> UC_Xuat
    ThuKho --> UC_TheKho
    ThuKho --> UC_Excel

    Staff --> UC_TheKho

    UC_Nhap -.->|<<include>>| UC_GhiTheKho
    UC_Xuat -.->|<<include>>| UC_GhiTheKho
    UC_Xuat -.->|<<include>>| UC_KiemTraFrontend
    UC_Xuat -.->|<<include>>| UC_LockBackend

    classDef actorStyle fill:#E0E7FF,stroke:#4338CA,stroke-width:2px,color:#1E1B4B;
    classDef mainUC fill:#ECFDF5,stroke:#059669,stroke-width:2px,color:#065F46;
    classDef subUC fill:#FEF2F2,stroke:#DC2626,stroke-width:1.5px,color:#991B1B;

    class Admin,ThuKho,Staff actorStyle;
    class UC_Nhap,UC_Xuat,UC_TheKho,UC_Excel mainUC;
    class UC_GhiTheKho,UC_KiemTraFrontend,UC_LockBackend subUC;
```

---

## 6. Biểu đồ Use Case Phân Hệ Trợ Lý AI
- **Mã ảnh báo cáo Word:** `word/media/image6.png` *(Hình 4.1.2)*
- **Ý nghĩa kỹ thuật:** Làm rõ cơ chế tương tác với Google Gemini 1.5 Flash API, quy trình Data Sanitizer loại bỏ giá vốn nhập trước khi gửi prompt ra ngoài, và cơ chế mở rộng Fallback sang Động cơ Offline khi mất mạng.

```mermaid
flowchart LR
    ThuKho(("fa:fa-warehouse Thủ Kho Kiêm\nKế Toán"))
    Admin(("fa:fa-user-shield Admin\n(Giám sát & Quản trị)"))
    Staff(("fa:fa-user Nhân Viên Kho\n(Staff)"))
    Gemini(("fa:fa-robot Google Gemini\n1.5 Flash API"))

    subgraph AIBoundary ["PHÂN HỆ TRỢ LÝ AI (GOOGLE GEMINI 1.5 FLASH API)"]
        UC_Widget(["Xem Khuyến Nghị Dashboard\n(Widget 3 khuyến nghị nhanh)"])
        UC_ReportAI(["Sinh Báo Cáo Chiến Lược\n(Phân tích toàn diện 3 phần)"])
        UC_OfflineFallback(["Dự Phòng Offline Engine\n(Local Rule-based Analyzer)"])

        UC_Grounded(["Grounded Prompting\n(Template bám sát số liệu thật)"])
        UC_DataSanitizer(["Khử Trùng Giá Vốn Nhập\n(Data Sanitizer Bảo mật Tuyệt đối)"])
    end

    ThuKho --> UC_Widget
    ThuKho --> UC_ReportAI
    Admin --> UC_ReportAI
    Staff --> UC_Widget

    UC_ReportAI -.->|<<include>>| UC_Grounded
    UC_ReportAI -.->|<<include>>| UC_DataSanitizer
    UC_OfflineFallback -.->|<<extend>>| UC_ReportAI

    UC_Grounded --- Gemini
    UC_DataSanitizer --- Gemini

    classDef actorStyle fill:#E0E7FF,stroke:#4338CA,stroke-width:2px,color:#1E1B4B;
    classDef mainUC fill:#FAF5FF,stroke:#9333EA,stroke-width:2px,color:#581C87;
    classDef secUC fill:#FEF2F2,stroke:#DC2626,stroke-width:1.5px,color:#991B1B;
    classDef fallbackUC fill:#F3F4F6,stroke:#4B5563,stroke-width:1.5px,color:#1F2937;

    class ThuKho,Admin,Staff actorStyle;
    class Gemini actorStyle;
    class UC_Widget,UC_ReportAI mainUC;
    class UC_Grounded,UC_DataSanitizer secUC;
    class UC_OfflineFallback fallbackUC;
```

---

## 7. Sequence Diagram - Lập Phiếu Xuất Kho & Khóa ACID
- **Mã ảnh báo cáo Word:** `word/media/image7.png` *(Hình 4.2.1)*
- **Ý nghĩa kỹ thuật:** Mô tả giao dịch ACID chống tồn âm với câu lệnh khóa dòng nguyên tử: `UPDATE ton_kho SET so_luong = so_luong - :qty WHERE ma_hh = :id AND so_luong >= :qty`.

```mermaid
sequenceDiagram
    autonumber
    actor ThuKho as Thủ kho kiêm Kế toán
    participant Web as Giao diện Web (FastAPI Jinja/JS)
    participant API as Inventory API Router
    participant Service as Outbound Domain Service
    participant DB as MySQL 8.0 (InnoDB)

    ThuKho ->> Web: Nhập thông tin phiếu xuất & Chọn mặt hàng, số lượng
    Web ->> Web: Thẩm định sơ bộ (Client-side validation)
    Web ->> API: POST /api/v1/kho/phieu-xuat (Payload JSON)
    activate API

    API ->> Service: execute_outbound_transaction(data)
    activate Service

    Service ->> DB: BEGIN TRANSACTION (ISOLATION LEVEL READ COMMITTED)
    activate DB

    Service ->> DB: UPDATE ton_kho SET so_luong = so_luong - :qty WHERE ma_hh = :id AND so_luong >= :qty
    alt rowcount == 1 (Đủ hàng tồn kho)
        DB -->> Service: Rowcount = 1 (Trừ kho thành công)
        Service ->> DB: INSERT INTO phieu_xuat (MaPX, NgayXuat, NguoiNhan, LyDo)
        Service ->> DB: INSERT INTO chi_tiet_phieu_xuat (MaPX, MaHH, SoLuongXuat)
        Service ->> DB: INSERT INTO the_kho (MaHH, LoaiGD='XUAT', SoLuongThayDoi, TonSauGD)
        Service ->> DB: COMMIT TRANSACTION
        DB -->> Service: Transaction Committed
        Service -->> API: XuatKhoSuccessResponse (HTTP 200)
        API -->> Web: 200 OK { message: "Xuất kho thành công", phieu_id: "PX001" }
        Web -->> ThuKho: Hiển thị thông báo thành công & In phiếu xuất
    else rowcount == 0 (Tồn kho không đủ / Âm kho)
        DB -->> Service: Rowcount = 0 (Điều kiện >= :qty thất bại)
        Service ->> DB: ROLLBACK TRANSACTION
        DB -->> Service: Transaction Rolled Back
        Service -->> API: OutOfStockError (HTTP 400 Bad Request)
        API -->> Web: 400 Bad Request { error: "Số lượng xuất vượt tồn khả dụng" }
        Web -->> ThuKho: Cảnh báo đỏ: "Không đủ tồn kho để xuất!"
    end

    deactivate DB
    deactivate Service
    deactivate API
```

---

## 8. Sequence Diagram - AI Sinh Báo Cáo Nhập - Xuất - Tồn
- **Mã ảnh báo cáo Word:** `word/media/image8.png` *(Hình 4.2.2)*
- **Ý nghĩa kỹ thuật:** Quy trình Data Sanitizer bảo mật giá vốn và cơ chế Fallback sang Local Rule-based Analyzer khi kết nối Google Gemini API bị timeout hoặc mất mạng.

```mermaid
sequenceDiagram
    autonumber
    actor Admin as Quản trị viên / Thủ kho
    participant Web as Giao diện Web Dashboard
    participant AIService as AI Domain Service
    participant Sanitizer as Data Sanitizer (Security)
    participant DB as MySQL 8.0 Database
    participant Gemini as Google Gemini 1.5 Flash API
    participant Fallback as Local Rule-based Analyzer

    Admin ->> Web: Nhấn "Sinh Báo Cáo Đánh Giá Chiến Lược Kho AI"
    Web ->> AIService: POST /api/v1/ai/generate-report (Token, Range=30d)
    activate AIService

    AIService ->> DB: SELECT aggregate_30d_movement(MaHH, Nhap, Xuat, Ton)
    activate DB
    DB -->> AIService: RawData (Bao gồm DonGiaNhap, GiaVon, SoLuong)
    deactivate DB

    AIService ->> Sanitizer: sanitize_inventory_data(RawData)
    activate Sanitizer
    Note over Sanitizer: Loại bỏ 100% cột DonGiaNhap, TongTienNhap, ThongTinGiaVon
    Sanitizer -->> AIService: SanitizedData (Chỉ chứa SKU, Tên, Số lượng, Tốc độ xuất)
    deactivate Sanitizer

    AIService ->> AIService: Đóng gói Grounded Prompt Template + SanitizedData

    alt Kết nối Gemini API thành công (Timeout < 8s)
        AIService ->> Gemini: HTTPS POST /v1beta/models/gemini-1.5-flash:generateContent
        activate Gemini
        Gemini -->> AIService: 200 OK (Nội dung Markdown 3 phần: Đánh giá, Rủi ro, Khuyến nghị)
        deactivate Gemini
    else Lỗi mạng / Timeout > 8s
        AIService ->> Fallback: compute_local_warehouse_heuristics(SanitizedData)
        activate Fallback
        Fallback -->> AIService: Fallback Markdown Report (Phân tích toán học thuần túy)
        deactivate Fallback
    end

    AIService -->> Web: 200 OK { report_markdown: "...", engine: "Gemini 1.5 / Fallback" }
    deactivate AIService
    Web -->> Admin: Hiển thị báo cáo chiến lược dạng Markdown & Nút Xuất PDF/Excel
```

---

## 9. Sequence Diagram - Lập Phiếu Nhập Kho & Ghi Sổ Thẻ Kho
- **Mã ảnh báo cáo Word:** `word/media/image9.png` *(Hình 4.2.3)*
- **Ý nghĩa kỹ thuật:** Ghi nhận phiếu nhập hàng hóa, tăng số lượng tồn kho tức thì và append-only vào bảng sổ thẻ kho `the_kho` để làm căn cứ đối soát kế toán.

```mermaid
sequenceDiagram
    autonumber
    actor ThuKho as Thủ kho kiêm Kế toán
    participant Web as Web Interface
    participant API as Inventory API Router
    participant Service as Inbound Domain Service
    participant DB as MySQL 8.0 (InnoDB)

    ThuKho ->> Web: Điền thông tin phiếu nhập, Nhà cung cấp & Danh sách hàng hóa
    Web ->> API: POST /api/v1/kho/phieu-nhap (Payload)
    activate API

    API ->> Service: execute_inbound_transaction(data)
    activate Service

    Service ->> DB: BEGIN TRANSACTION
    activate DB
    Service ->> DB: INSERT INTO phieu_nhap (MaPN, NgayNhap, MaNCC, MaND, TongTien)
    Service ->> DB: INSERT INTO chi_tiet_phieu_nhap (MaPN, MaHH, SoLuongNhap, DonGiaNhap)
    Service ->> DB: UPDATE ton_kho SET so_luong = so_luong + :qty WHERE ma_hh = :id
    Service ->> DB: INSERT INTO the_kho (MaHH, LoaiGD='NHAP', SoLuongThayDoi, TonSauGD)
    Service ->> DB: COMMIT TRANSACTION
    DB -->> Service: Transaction Committed
    deactivate DB

    Service -->> API: InboundSuccessResponse (HTTP 201 Created)
    deactivate Service
    API -->> Web: 201 Created { message: "Nhập kho thành công", phieu_id: "PN001" }
    deactivate API
    Web -->> ThuKho: Cập nhật tồn mới trên màn hình & Thông báo thành công
```

---

## 10. Sequence Diagram - Tra Cứu Thẻ Kho & Cảnh Báo Tồn Tối Thiểu
- **Mã ảnh báo cáo Word:** `word/media/image10.png` *(Hình 4.2.4)*
- **Ý nghĩa kỹ thuật:** Truy vấn lịch sử biến động thẻ kho lũy kế và đối soát với ngưỡng `TonToiThieu` để kích hoạt cảnh báo trực quan cho nhân viên và thủ kho.

```mermaid
sequenceDiagram
    autonumber
    actor User as Thủ kho / Nhân viên kho
    participant Web as Web Interface (Báo cáo Thẻ kho)
    participant API as Inventory Query API
    participant DB as MySQL 8.0 Database

    User ->> Web: Chọn Mặt hàng (SKU) & Khoảng thời gian tra cứu
    Web ->> API: GET /api/v1/kho/the-kho?ma_hh=HH01&from_date=...&to_date=...
    activate API

    API ->> DB: SELECT * FROM the_kho WHERE ma_hh = :id ORDER BY ngay_gd ASC
    activate DB
    DB -->> API: Danh sách bản ghi biến động (Ngày, Loại GD, Biến động, Tồn lũy kế)

    API ->> DB: SELECT so_luong FROM ton_kho WHERE ma_hh = :id
    DB -->> API: TonKhoHienTai
    API ->> DB: SELECT ton_toi_thieu FROM hang_hoa WHERE ma_hh = :id
    DB -->> API: TonToiThieu
    deactivate DB

    API ->> API: Kiểm tra: IsLowStock = (TonKhoHienTai <= TonToiThieu)
    API -->> Web: 200 OK { history: [...], current_stock: X, min_stock: Y, is_low: true/false }
    deactivate API

    Web -->> User: Hiển thị bảng biến động lũy kế & Cảnh báo Huy hiệu Đỏ nếu tồn thấp
```

---

## 11. Sequence Diagram - Xuất Báo Cáo Dữ Liệu Ra File Excel
- **Mã ảnh báo cáo Word:** `word/media/image11.png` *(Hình 4.2.5)*
- **Ý nghĩa kỹ thuật:** Trích xuất toàn bộ bảng cân đối nhập - xuất - tồn, đóng gói định dạng file Excel `.xlsx` tương thích các phần mềm kế toán.

```mermaid
sequenceDiagram
    autonumber
    actor User as Thủ kho kiêm Kế toán / Admin
    participant Web as Web Interface
    participant ReportAPI as Report API Router
    participant ExcelEngine as OpenPyXL Excel Generator
    participant DB as MySQL 8.0 Database

    User ->> Web: Nhấn "Xuất Báo Cáo Tồn Kho Excel (.xlsx)"
    Web ->> ReportAPI: GET /api/v1/reports/export-inventory-excel
    activate ReportAPI

    ReportAPI ->> DB: Truy vấn tổng hợp: HangHoa, TonKho, Tổng Nhập, Tổng Xuất
    activate DB
    DB -->> ReportAPI: Tập dữ liệu đối soát tồn kho
    deactivate DB

    ReportAPI ->> ExcelEngine: generate_inventory_workbook(data)
    activate ExcelEngine
    ExcelEngine ->> ExcelEngine: Format Header, Font, Cột Tiền Tệ, Border, Cảnh báo màu
    ExcelEngine -->> ReportAPI: File Stream Binary (application/vnd.openxmlformats...)
    deactivate ExcelEngine

    ReportAPI -->> Web: HTTP 200 OK (Content-Disposition: attachment; filename="BaoCaoTonKho.xlsx")
    deactivate ReportAPI
    Web -->> User: Trình duyệt tải file Excel về máy tính thành công
```

---

## 12. Sequence Diagram - Đăng Nhập & Phân Quyền Truy Cập JWT
- **Mã ảnh báo cáo Word:** `word/media/image12.png` *(Hình 4.2.6)*
- **Ý nghĩa kỹ thuật:** Xác thực người dùng bằng mật khẩu băm Bcrypt, cấp phát JSON Web Token (JWT) có chữ ký số bí mật và kiểm tra quyền hạn (RBAC) theo từng vai trò.

```mermaid
sequenceDiagram
    autonumber
    actor User as Người dùng (Admin / Thủ kho / Staff)
    participant Web as Trang Đăng Nhập (Login View)
    participant AuthAPI as Auth Router (/api/v1/auth)
    participant SecService as Security & Token Service
    participant DB as MySQL 8.0 (NguoiDung)

    User ->> Web: Nhập Tên đăng nhập & Mật khẩu
    Web ->> AuthAPI: POST /api/v1/auth/login (username, password)
    activate AuthAPI

    AuthAPI ->> DB: SELECT * FROM nguoi_dung WHERE ten_dang_nhap = :user
    activate DB
    DB -->> AuthAPI: UserRecord (mat_khau_hash, vai_tro, kich_hoat)
    deactivate DB

    AuthAPI ->> SecService: verify_password(plain_password, mat_khau_hash)
    activate SecService

    alt Mật khẩu chính xác & Tài khoản hoạt động
        SecService -->> AuthAPI: True (Hợp lệ)
        AuthAPI ->> SecService: create_access_token(user_id, role, expiry)
        SecService -->> AuthAPI: Encoded JWT Token String
        deactivate SecService
        AuthAPI -->> Web: 200 OK { access_token: "...", token_type: "bearer", role: "Thukho" }
        Web ->> Web: Lưu JWT vào Cookie / LocalStorage & Điều hướng Dashboard
        Web -->> User: Vào giao diện chính với quyền hạn tương ứng
    else Sai mật khẩu hoặc Tài khoản bị vô hiệu hóa
        SecService -->> AuthAPI: False (Không hợp lệ)
        AuthAPI -->> Web: 401 Unauthorized { detail: "Sai tài khoản hoặc mật khẩu" }
        Web -->> User: Hiển thị thông báo lỗi đăng nhập màu đỏ
    end
    deactivate AuthAPI
```

---

## 13. Sơ đồ Thực Thể Quan Hệ Cơ Sở Dữ Liệu Cụ Thể (ERD)
- **Mã ảnh báo cáo Word:** `word/media/image13.png` *(Hình 4.3.3)*
- **Ý nghĩa kỹ thuật:** Toàn bộ 11 bảng cơ sở dữ liệu MySQL 8.0 với đầy đủ các mối quan hệ khóa ngoại (Foreign Keys), ràng buộc kiểm tra toàn vẹn `CHECK (SoLuongTon >= 0)` và chỉ mục tối ưu hóa hiệu năng.

```mermaid
erDiagram
    NguoiDung ||--o{ PhieuNhap : "tao_phieu_nhap (MaND)"
    NguoiDung ||--o{ PhieuXuat : "tao_phieu_xuat (MaND)"
    NhaCungCap ||--o{ PhieuNhap : "cung_cap_hang (MaNCC)"
    
    PhieuNhap ||--|{ ChiTietPhieuNhap : "chi_tiet_nhap (MaPN)"
    PhieuXuat ||--|{ ChiTietPhieuXuat : "chi_tiet_xuat (MaPX)"
    
    HangHoa ||--|{ ChiTietPhieuNhap : "nhap_mat_hang (MaHH)"
    HangHoa ||--|{ ChiTietPhieuXuat : "xuat_mat_hang (MaHH)"
    
    NhomHang ||--o{ HangHoa : "phan_loai (MaNhom)"
    DonViTinh ||--o{ HangHoa : "don_vi_tinh (MaDVT)"
    
    HangHoa ||--|| TonKho : "luu_tru_ton_thuc (MaHH)"
    HangHoa ||--o{ TheKho : "lich_su_bien_dong (MaHH)"

    NguoiDung {
        int MaND PK "Khóa chính tự tăng"
        varchar TenDangNhap UK "Tài khoản đăng nhập"
        varchar MatKhau "Băm mật khẩu Bcrypt"
        varchar HoTen "Họ và tên người dùng"
        varchar VaiTro "Admin | Thukho | Nhanvien"
        timestamp NgayTao "Thời gian tạo tài khoản"
    }

    NhaCungCap {
        varchar MaNCC PK "Mã nhà cung cấp"
        varchar TenNCC "Tên nhà cung cấp"
        varchar DiaChi "Địa chỉ liên hệ"
        varchar SoDienThoai "Số điện thoại liên lạc"
        varchar Email "Địa chỉ thư điện tử"
    }

    NhomHang {
        varchar MaNhom PK "Mã nhóm hàng"
        varchar TenNhom "Tên nhóm sản phẩm"
        text MoTa "Mô tả nhóm hàng hóa"
    }

    DonViTinh {
        varchar MaDVT PK "Mã đơn vị tính"
        varchar TenDVT "Tên đơn vị (Thùng, Hộp, Chai, Chiếc)"
        text MoTa "Ghi chú đơn vị tính"
    }

    HangHoa {
        varchar MaHH PK "Mã hàng hóa SKU"
        varchar TenHH "Tên hàng hóa"
        varchar MaNhom FK "Khóa ngoại Nhóm hàng"
        varchar MaDVT FK "Khóa ngoại Đơn vị tính"
        int TonToiThieu "Ngưỡng cảnh báo tồn tối thiểu"
        text MoTa "Mô tả quy cách đóng gói"
    }

    TonKho {
        varchar MaHH PK,FK "Mã hàng hóa (1-1 với HangHoa)"
        int SoLuongTon "CHECK (SoLuongTon >= 0)"
        timestamp CapNhatCuoi "Thời điểm biến động gần nhất"
    }

    PhieuNhap {
        varchar MaPN PK "Mã phiếu nhập kho"
        timestamp NgayNhap "Ngày giờ nhập hàng"
        varchar MaNCC FK "Khóa ngoại Nhà cung cấp"
        int MaND FK "Khóa ngoại Người lập phiếu"
        float TongTien "Tổng giá trị phiếu nhập"
        text GhiChu "Ghi chú chứng từ"
    }

    ChiTietPhieuNhap {
        int MaCTPN PK "Khóa chính tự tăng"
        varchar MaPN FK "Khóa ngoại Phiếu nhập"
        varchar MaHH FK "Khóa ngoại Hàng hóa"
        int SoLuongNhap "CHECK (SoLuongNhap > 0)"
        float DonGiaNhap "CHECK (DonGiaNhap >= 0)"
        float ThanhTien "Thành tiền dòng nhập"
    }

    PhieuXuat {
        varchar MaPX PK "Mã phiếu xuất kho"
        timestamp NgayXuat "Ngày giờ xuất hàng"
        int MaND FK "Khóa ngoại Người lập phiếu"
        varchar NguoiNhan "Họ tên người nhận hàng"
        text LyDoXuat "Mục đích xuất kho"
    }

    ChiTietPhieuXuat {
        int MaCTPX PK "Khóa chính tự tăng"
        varchar MaPX FK "Khóa ngoại Phiếu xuất"
        varchar MaHH FK "Khóa ngoại Hàng hóa"
        int SoLuongXuat "CHECK (SoLuongXuat > 0)"
    }

    TheKho {
        int MaGD PK "Khóa chính tự tăng"
        timestamp NgayGiaoDich "Thời điểm phát sinh giao dịch"
        varchar MaHH FK "Khóa ngoại Hàng hóa liên quan"
        varchar MaChungTu "Số hiệu phiếu (MaPN hoặc MaPX)"
        varchar LoaiGiaoDich "NHAP hoặc XUAT"
        int SoLuongThayDoi "Số lượng biến động (+ / -)"
        int TonSauGiaoDich "CHECK (TonSauGiaoDich >= 0)"
    }
```

---

## 14. Activity Diagram - Nghiệp Vụ Xuất Kho Chống Tồn Âm
- **Mã ảnh báo cáo Word:** `word/media/image14.png` *(Hình 4.4.1)*
- **Ý nghĩa kỹ thuật:** Quy trình luồng nghiệp vụ xuất kho chuẩn hóa: Kiểm tra số lượng tồn bằng Atomic Decrement tại Database, nếu không đủ hàng sẽ Rollback và trả HTTP 400; nếu đủ hàng sẽ ghi ChiTietPhieuXuat, lưu vết TheKho và Commit Transaction.

```mermaid
flowchart TD
    StartNode(( )) --> Step1["1. Thủ kho chọn SKU & Nhập số lượng xuất trên Web Form"]
    Step1 --> Step2["2. Gửi POST /api/v1/kho/phieu-xuat & Bắt đầu Database Transaction (ACID)"]
    Step2 --> Step3["3. Khóa dòng & Thực thi Atomic Decrement:\nUPDATE ton_kho ... WHERE SoLuongTon >= :qty"]
    Step3 --> Decision{"Số lượng tồn >=\nSố lượng xuất?\n(rowcount == 1)"}

    Decision -->|ĐỦ HÀNG / HỢP LỆ| Step4A["4A. Ghi nhận PhieuXuat, ChiTietPhieuXuat\n& Cập nhật trừ tồn kho thành công"]
    Step4A --> Step5A["5A. INSERT TheKho (Loai='XUAT', TonSauGD)\n& COMMIT TRANSACTION (ACID)"]
    Step5A --> Step6["6. Cập nhật giao diện & Kết thúc"]

    Decision -->|KHÔNG ĐỦ HÀNG| Step4B["4B. Kích hoạt ROLLBACK TRANSACTION\n(Hủy bỏ mọi biến động dữ liệu)"]
    Step4B --> Step5B["5B. Báo lỗi HTTP 400 Bad Request:\n'Chỉ còn tồn X, không đủ xuất Y'"]
    Step5B --> Step6

    Step6 --> EndNode((( )))

    classDef startClass fill:#1E293B,stroke:#0F172A,stroke-width:2px,color:#FFFFFF;
    classDef stepClass fill:#EFF6FF,stroke:#3B82F6,stroke-width:1.5px,color:#1E3A8A;
    classDef okClass fill:#ECFDF5,stroke:#059669,stroke-width:1.5px,color:#065F46;
    classDef failClass fill:#FEF2F2,stroke:#DC2626,stroke-width:1.5px,color:#991B1B;
    classDef decisionClass fill:#FFFBEB,stroke:#D97706,stroke-width:2px,color:#92400E;

    class StartNode,EndNode startClass;
    class Step1,Step2,Step3,Step6 stepClass;
    class Step4A,Step5A okClass;
    class Step4B,Step5B failClass;
    class Decision decisionClass;
```

---

## 15. Activity Diagram - Trợ Lý AI & Data Sanitizer
- **Mã ảnh báo cáo Word:** `word/media/image15.png` *(Hình 4.4.2)*
- **Ý nghĩa kỹ thuật:** Toàn bộ 7 bước của quy trình Trợ lý AI: Truy vấn 30 ngày, Khử trùng giá vốn bí mật bằng Data Sanitizer, Đóng gói Grounded Prompt, Gọi Gemini 1.5 Flash API có kiểm soát Timeout 8 giây, Rẽ nhánh Fallback SQL Engine nội bộ nếu mạng lỗi, và Kết xuất báo cáo 3 phần.

```mermaid
flowchart TD
    StartNode(( )) --> Step1["1. Người dùng yêu cầu Sinh Báo cáo Nhập-Xuất-Tồn / Khuyến nghị kho"]
    Step1 --> Step2["2. Backend truy vấn DataSet kho 30 ngày từ MySQL 8.0 (Xuất, Nhập, Tồn)"]
    Step2 --> Step3["3. Data Sanitizer loại bỏ triệt để DonGiaNhap & Giá vốn (Bảo mật tuyệt đối)"]
    Step3 --> Step4["4. Đóng gói Grounded Prompt Template + Dữ liệu sạch + Chỉ dẫn phân tích"]
    Step4 --> Step5["5. Gửi HTTPS Request tới Google Gemini API (Model: Gemini 1.5 Flash)"]
    Step5 --> Decision{"Kết nối Gemini API\nthành công?\n(Timeout < 8s)"}

    Decision -->|THÀNH CÔNG| Step6A["6A. Nhận Markdown Báo cáo AI 3 phần\n& Render lên giao diện Dashboard"]
    Step6A --> Step7["7. Hiển thị kết quả & Hỗ trợ Xuất Excel/PDF"]

    Decision -->|MẤT MẠNG / TIMEOUT| Step6B["6B. Kích hoạt Fallback SQL Engine\n(Sinh báo cáo thống kê thuần túy)"]
    Step6B --> Step7

    Step7 --> EndNode((( )))

    classDef startClass fill:#1E293B,stroke:#0F172A,stroke-width:2px,color:#FFFFFF;
    classDef stepClass fill:#F5F3FF,stroke:#7C3AED,stroke-width:1.5px,color:#4C1D95;
    classDef cleanClass fill:#FEF2F2,stroke:#DC2626,stroke-width:2px,color:#991B1B;
    classDef okClass fill:#ECFDF5,stroke:#059669,stroke-width:1.5px,color:#065F46;
    classDef failClass fill:#FEF2F2,stroke:#DC2626,stroke-width:1.5px,color:#991B1B;
    classDef decisionClass fill:#FFFBEB,stroke:#D97706,stroke-width:2px,color:#92400E;

    class StartNode,EndNode startClass;
    class Step1,Step2,Step4,Step5,Step7 stepClass;
    class Step3 cleanClass;
    class Step6A okClass;
    class Step6B failClass;
    class Decision decisionClass;
```

---

## 16. Class Diagram - Kiến Trúc Backend FastAPI & Domain Services
- **Mã ảnh báo cáo Word:** `word/media/image16.png` *(Hình 4.5.1)*
- **Ý nghĩa kỹ thuật:** Phân tầng phần mềm kiến trúc 3 lớp chuẩn mực: API Controllers/Routers -> Domain Services (Nghiệp vụ ACID & AI) -> SQLAlchemy ORM Persistence Models, cùng các đường nối quan hệ ngữ nghĩa chuẩn UML.

```mermaid
classDiagram
    %% Tầng 1: API Controllers / Routers
    class InventoryRouter {
        <<API Controller>>
        - prefix: str = '/api/v1/kho'
        - auth_service: AuthService
        + api_tao_phieu_nhap(payload)
        + api_tao_phieu_xuat(payload)
        + api_get_the_kho(ma_hh)
    }

    class AIRouter {
        <<API Controller>>
        - prefix: str = '/api/v1/ai'
        - ai_service: AIService
        + api_get_ai_advisory()
        + api_generate_ai_report()
        + api_get_raw_context()
    }

    class ReportsRouter {
        <<API Controller>>
        - prefix: str = '/api/v1/reports'
        - inv_service: InventoryService
        + api_export_excel(db, user)
        + api_export_suppliers()
        + api_export_pdf_stub()
    }

    class AuthRouter {
        <<API Controller>>
        - prefix: str = '/api/v1/auth'
        - sec_service: Security
        + api_login(credentials)
        + api_register(user_in)
        + api_get_me()
    }

    %% Tầng 2: Domain Services
    class InboundService {
        <<Domain Service (ACID)>>
        - db: Session
        + execute_inbound_tx(phieu_in)
        + update_stock_increase(ma_hh, qty)
        + append_the_kho(ma_hh, 'NHAP')
        + notify_websocket(event)
    }

    class OutboundService {
        <<Domain Service (ACID)>>
        - db: Session
        + execute_outbound_tx(phieu_in)
        + atomic_sql_decrement(ma_hh, qty)
        + validate_zero_stock(ma_hh, qty)
        + append_the_kho(ma_hh, 'XUAT')
    }

    class AIService {
        <<Domain Service (Gemini)>>
        - api_key: str
        - sanitizer: DataSanitizer
        + aggregate_warehouse_data_30d()
        + sanitize_warehouse_data(data)
        + generate_inventory_advisory()
        + generate_full_ai_report()
    }

    class SecurityService {
        <<Core Security>>
        - SECRET_KEY: str
        - ALGORITHM: str
        + hash_password(plain)
        + verify_password(plain, hash)
        + create_access_token(data)
        + require_role(roles)
    }

    %% Tầng 3: SQLAlchemy ORM Models
    class HangHoaModel {
        <<SQLAlchemy ORM>>
        + MaHH: Column(String, PK)
        + TenHH: Column(String)
        + MaNhom: Column(String, FK)
        + MaDVT: Column(String, FK)
        + TonToiThieu: Column(Integer)
    }

    class TonKhoModel {
        <<SQLAlchemy ORM>>
        + MaHH: Column(String, PK, FK)
        + SoLuongTon: Column(Integer)
        + CheckConstraint('SoLuongTon >= 0')
        + CapNhatCuoi: Column(DateTime)
    }

    class TheKhoModel {
        <<SQLAlchemy ORM>>
        + MaGD: Column(Integer, PK)
        + MaHH: Column(String, FK)
        + MaChungTu: Column(String)
        + LoaiGiaoDich: Column(String)
        + SoLuongThayDoi: Column(Integer)
        + TonSauGiaoDich: Column(Integer)
    }

    class NguoiDungModel {
        <<SQLAlchemy ORM>>
        + MaND: Column(Integer, PK)
        + TenDangNhap: Column(String)
        + MatKhau: Column(String)
        + VaiTro: Column(String)
        + KichHoat: Column(Boolean)
    }

    %% Relationships giữa các tầng
    InventoryRouter ..> InboundService : "<<calls>>"
    InventoryRouter ..> OutboundService : "<<calls>>"
    AIRouter ..> AIService : "<<calls>>"
    ReportsRouter ..> OutboundService : "<<queries>>"
    AuthRouter ..> SecurityService : "<<authenticates>>"

    InboundService --> HangHoaModel : "<<queries>>"
    InboundService --> TonKhoModel : "<<updates>>"
    OutboundService --> TonKhoModel : "<<decrements>>"
    OutboundService --> TheKhoModel : "<<appends>>"
    AIService --> TheKhoModel : "<<analyzes>>"
    SecurityService --> NguoiDungModel : "<<validates>>"
```

---
*Tài liệu được sinh tự động và chuẩn hóa bởi Antigravity Skill `diagram-architect`.*
