---
name: diagram-architect
description: Chuyên gia thiết kế, tạo và chuẩn hóa các loại sơ đồ kỹ thuật kiến trúc phần mềm (Use Case, Sequence, ERD, Flowchart, Class, State) chuẩn cú pháp Mermaid.js cho tài liệu và thiết kế hệ thống.
version: 1.0.0
---

# Skill: Diagram Architect (Mermaid.js Specialist)

## 1. Giới thiệu & Vai trò

`diagram-architect` là một kỹ năng chuyên biệt giúp thiết kế, biểu diễn và chuẩn hóa các mô hình kiến trúc phần mềm, quy trình nghiệp vụ và cấu trúc dữ liệu dưới dạng sơ đồ trực quan bằng **Mermaid.js**.

### Mục tiêu cốt lõi:
- Chuyển đổi mô tả nghiệp vụ thành sơ đồ trực quan, dễ hiểu cho cả kỹ sư và các bên liên quan (stakeholders).
- Đảm bảo 100% cú pháp Mermaid.js hợp lệ, không gây lỗi render trên GitHub, GitLab, Notion, Antigravity và Markdown viewers.
- Tạo cấu trúc sơ đồ sạch sẽ, có phân tầng, chú thích rõ ràng, hỗ trợ tài liệu hóa hệ thống theo tiêu chuẩn kỹ thuật chuyên nghiệp.

---

## 2. Các nguyên tắc vàng khi viết Mermaid.js

1. **Bọc nhãn chứa ký tự đặc biệt**:
   - Nếu nhãn node chứa dấu ngoặc `()`, `[]`, `{}` hoặc ký tự đặc biệt, toán tử, khoảng trắng đặc thù, **bắt buộc** phải bọc trong dấu ngoặc kép:
     ```mermaid
     id1["Người dùng (Khách vãng lai)"]
     id2["Hàm calculateTotal(items)"]
     ```
2. **Không dùng thẻ HTML không an toàn**:
   - Tránh dùng `<br>`, `<b>` nếu không thực sự cần thiết. Dùng chuỗi ký tự chuẩn hoặc dấu ngắt dòng `\n` khi cú pháp hỗ trợ.
3. **Định danh Node ngắn gọn, ngữ nghĩa**:
   - Tách biệt `Node ID` và `Node Label`:
     - Tốt: `auth_service["Dịch vụ Xác thực"]`
     - Không tốt: `Dịch vụ Xác thực["Dịch vụ Xác thực"]`
4. **Lựa chọn hướng hiển thị (Orientation)**:
   - `TB` (Top to Bottom) / `TD` (Top Down): Phù hợp cho sơ đồ phân cấp, kiến trúc tầng, sơ đồ quyết định.
   - `LR` (Left to Right): Phù hợp cho luồng xử lý theo thời gian, pipeline dữ liệu, User Journey.

---

## 3. Thiết kế Sơ đồ Use Case (Use Case Diagram)

Trong Mermaid.js, sơ đồ Use Case thường được biểu diễn tối ưu nhất bằng cú pháp `flowchart LR` kết hợp các hình khối (shapes) và nhóm hệ thống (`subgraph`) để mô phỏng ranh giới hệ thống (System Boundary).

### Quy ước biểu diễn:
- **Actor**: Thường ký hiệu bằng hình lục giác `{{...}}`, hình tròn `((...))` hoặc gắn icon `fa:fa-user`.
- **System Boundary**: Đóng gói trong `subgraph "Tên Hệ Thống" ... end`.
- **Use Case**: Biểu diễn bằng hình Oval `([Tên Use Case])`.
- **Quan hệ**:
  - Tương tác trực tiếp: `-->`
  - Quan hệ phụ thuộc `<<include>>`: `-.->|<<include>>|`
  - Quan hệ mở rộng `<<extend>>`: `-.->|<<extend>>|`
  - Quan hệ kế thừa Actor: `==>|Generalizes|`

### Mẫu sơ đồ Use Case chuẩn:

```mermaid
flowchart LR
    %% Actors
    ActorCustomer(("fa:fa-user Khách hàng"))
    ActorAdmin(("fa:fa-user-shield Quản trị viên"))
    ActorWarehouse(("fa:fa-warehouse Quản lý kho"))

    %% System Boundary
    subgraph SystemBoundary ["Hệ Thống Quản Lý Đơn Hàng & Logistics"]
        UC1(["Đăng nhập / Đăng ký"])
        UC2(["Tìm kiếm & Xem sản phẩm"])
        UC3(["Tạo đơn hàng"])
        UC4(["Thanh toán đơn hàng"])
        UC5(["Xác thực thẻ tín dụng / Ví"])
        UC6(["Hủy đơn hàng"])
        UC7(["Cập nhật trạng thái tồn kho"])
        UC8(["Điều phối vận chuyển"])
        UC9(["Báo cáo & Thống kê doanh thu"])
    end

    %% Mối quan hệ của Khách hàng
    ActorCustomer --> UC1
    ActorCustomer --> UC2
    ActorCustomer --> UC3
    ActorCustomer --> UC6

    %% Quan hệ Include / Extend
    UC3 -.->|<<include>>| UC4
    UC4 -.->|<<include>>| UC5
    UC6 -.->|<<extend>>| UC3

    %% Quan hệ của Quản lý kho & Admin
    UC3 -.->|<<include>>| UC7
    ActorWarehouse --> UC7
    ActorWarehouse --> UC8
    ActorAdmin --> UC9
    ActorAdmin --> UC1

    %% Styling
    classDef actorStyle fill:#e1f5fe,stroke:#0288d1,stroke-width:2px,color:#01579b;
    classDef ucStyle fill:#f3e5f5,stroke:#7b1fa2,stroke-width:1.5px,color:#4a148c;
    class ActorCustomer,ActorAdmin,ActorWarehouse actorStyle;
    class UC1,UC2,UC3,UC4,UC5,UC6,UC7,UC8,UC9 ucStyle;
```

---

## 4. Thiết kế Sơ đồ Tuần tự (Sequence Diagram)

Sơ đồ tuần tự mô tả sự tương tác giữa các đối tượng theo thứ tự thời gian. Rất quan trọng khi thiết kế API, vi dịch vụ (microservices), và các luồng xử lý giao dịch.

### Cú pháp & Kỹ thuật trọng tâm:
- `autonumber`: Tự động đánh số bước gọi (khuyên dùng cho tài liệu kỹ thuật).
- `actor` vs `participant`: Khai báo rõ vai trò người dùng và thành phần hệ thống.
- Các loại mũi tên:
  - `->>`: Lời gọi đồng bộ (Sync Request).
  - `-->>`: Phản hồi kết quả (Sync Response).
  - `-)`: Lời gọi bất đồng bộ / Message Queue (Async Request).
  - `-->>)`: Phản hồi bất đồng bộ.
- `activate` / `deactivate`: Thể hiện vòng đời xử lý của thành phần.
- Khối điều khiển:
  - `alt / else`: Điều kiện rẽ nhánh (if/else).
  - `opt`: Tùy chọn có hoặc không (optional).
  - `loop`: Vòng lặp.
  - `par`: Xử lý song song đồng thời.
  - `critical`: Giao dịch cần đảm bảo tính toàn vẹn (atomic transaction).

### Mẫu sơ đồ Sequence chuẩn:

```mermaid
sequenceDiagram
    autonumber
    actor Driver as Tài xế (Mobile App)
    participant API as API Gateway (FastAPI)
    participant RouteService as Service Tối Ưu Lộ Trình
    participant Cache as Redis Cache
    participant DB as Database (PostgreSQL)
    participant Notification as Notification Hub

    Driver ->> API: POST /api/v1/routes/optimize (VehicleID, Locations)
    activate API

    API ->> Cache: GET route_cache:{VehicleID}
    activate Cache
    Cache -->> API: Cache Miss (null)
    deactivate Cache

    API ->> RouteService: calculateOptimalPath(Locations, VehicleCapacity)
    activate RouteService
    
    RouteService ->> RouteService: Áp dụng thuật toán OR-Tools / Dijkstra
    RouteService -->> API: OptimalPathResult (Khoảng cách, Lộ trình, Thời gian)
    deactivate RouteService

    alt Kết quả tìm thấy hợp lệ
        API ->> DB: INSERT INTO shipments_routes (...)
        activate DB
        DB -->> API: RouteID: 10452, Status: ASSIGNED
        deactivate DB

        API ->> Cache: SETEX route_cache:{VehicleID} (TTL=3600s)
        
        API -) Notification: PushNotification (Gán lộ trình mới cho tài xế)
        
        API -->> Driver: 201 Created { route_id: 10452, eta: "45 mins", waypoints: [...] }
    else Không tìm được đường đi hoặc vượt tải trọng
        API -->> Driver: 400 Bad Request { error_code: "ROUTE_OVERLOAD", message: "Vượt tải trọng cho phép" }
    end

    deactivate API
```

---

## 5. Thiết kế Sơ đồ Thực thể Quan hệ (ERD - Entity Relationship Diagram)

ERD biểu diễn cơ sở dữ liệu quan hệ, các bảng (tables/entities), khóa chính (PK), khóa ngoại (FK), các trường dữ liệu và ràng buộc liên kết.

### Bảng Cardinality (Bậc quan hệ):
| Ký hiệu | Ý nghĩa | Ví dụ |
| :--- | :--- | :--- |
| `\|\|--\|\|` | Một - Một bắt buộc (Exactly one) | Người dùng - Hồ sơ CCCD |
| `\|\|--o\|` | Một - Không hoặc Một (Zero or one) | Đơn hàng - Mã giảm giá |
| `\|\|--\|{` | Một - Nhiều bắt buộc (One or more) | Hóa đơn - Dòng chi tiết hóa đơn |
| `\|\|--o{` | Một - Nhiều tùy chọn (Zero or more) | Danh mục - Sản phẩm |
| `}o--o{` | Nhiều - Nhiều (Many to many) | Sinh viên - Môn học |

### Mẫu sơ đồ ERD chuẩn cho Hệ thống Logistics:

```mermaid
erDiagram
    USERS ||--o{ ORDERS : "places"
    USERS ||--o{ VEHICLES : "operates"
    ORDERS ||--|{ ORDER_ITEMS : "contains"
    PRODUCTS ||--o{ ORDER_ITEMS : "included_in"
    ORDERS ||--o| SHIPMENTS : "delivered_by"
    VEHICLES ||--o{ SHIPMENTS : "assigned_to"
    ROUTES ||--|{ SHIPMENTS : "defines_path_for"

    USERS {
        int id PK "Khóa chính tự tăng"
        string email UK "Email duy nhất"
        string hashed_password "Mật khẩu mã hóa"
        string full_name "Họ và tên"
        string role "ADMIN | DRIVER | CUSTOMER"
        datetime created_at "Thời gian tạo"
    }

    VEHICLES {
        int id PK "Mã xe"
        int driver_id FK "Tài xế phụ trách"
        string plate_number UK "Biển số xe"
        float max_weight_kg "Tải trọng tối đa"
        float max_volume_m3 "Thể tích tối đa"
        string status "ACTIVE | MAINTENANCE | IN_TRANSIT"
    }

    ORDERS {
        int id PK "Mã đơn hàng"
        int user_id FK "Người tạo đơn"
        string tracking_code UK "Mã tra cứu vận đơn"
        decimal total_amount "Tổng tiền"
        string payment_status "PENDING | PAID | FAILED"
        string order_status "CREATED | PROCESSING | SHIPPING | DELIVERED"
        datetime created_at "Ngày tạo đơn"
    }

    ORDER_ITEMS {
        int id PK "Mã dòng chi tiết"
        int order_id FK "Thuộc đơn hàng nào"
        int product_id FK "Sản phẩm liên kết"
        int quantity "Số lượng"
        decimal unit_price "Đơn giá tại thời điểm mua"
    }

    PRODUCTS {
        int id PK "Mã sản phẩm"
        string sku UK "Mã kho hàng SKU"
        string name "Tên sản phẩm"
        float weight_kg "Khối lượng đơn vị"
        decimal price "Giá niêm yết"
        int stock_quantity "Tồn kho khả dụng"
    }

    SHIPMENTS {
        int id PK "Mã chuyến giao hàng"
        int order_id FK "Đơn hàng cần giao"
        int vehicle_id FK "Xe phụ trách"
        int route_id FK "Lộ trình di chuyển"
        datetime start_time "Giờ xuất phát"
        datetime estimated_arrival "Dự kiến đến"
        string current_status "PREPARING | ON_ROAD | COMPLETED"
    }

    ROUTES {
        int id PK "Mã lộ trình"
        string origin_hub "Kho xuất phát"
        string destination "Điểm đến"
        float total_distance_km "Tổng quãng đường km"
        json waypoints "Danh sách tọa độ GPS trung gian"
    }
```

---

## 6. Các Sơ đồ Hỗ trợ Phổ biến khác

### A. State Diagram (Vòng đời trạng thái đơn hàng):
```mermaid
stateDiagram-v2
    [*] --> NhapDon: Khởi tạo đơn hàng
    NhapDon --> ChoXacNhan: Khách gửi đơn
    ChoXacNhan --> DaHuy: Khách hủy / Hết hàng
    ChoXacNhan --> DangDongGoi: Xác nhận đơn & Tồn kho
    DangDongGoi --> DangGiaoHang: Bàn giao tài xế
    DangGiaoHang --> GiaoThanhCong: Người nhận đã ký nhận
    DangGiaoHang --> GiaoThatBai: Không liên lạc được
    GiaoThatBai --> DangGiaoHang: Giao lại (Tối đa 3 lần)
    GiaoThatBai --> HoanDonVeKho: Quá số lần cho phép
    HoanDonVeKho --> [*]
    GiaoThanhCong --> [*]
    DaHuy --> [*]
```

### B. Kiến trúc Hệ thống Phân tầng (Architecture Diagram):
```mermaid
flowchart TD
    Client["Client Web / Mobile (React / Flutter)"]
    
    subgraph Gateway ["Cổng Giao Tiếp (Reverse Proxy)"]
        Nginx["Nginx / Traefik (Rate Limit, SSL, Routing)"]
    end
    
    subgraph CoreBackend ["Hệ Thống Backend (FastAPI / NestJS)"]
        API["API Layer (Controller / Router)"]
        AuthMiddleware["JWT Authentication Middleware"]
        BusinessLogic["Business Logic (Service Layer)"]
        DataLayer["Data Access (Repository / ORM)"]
    end
    
    subgraph DataPersistence ["Tầng Lưu Trữ & Message"]
        Postgres[(PostgreSQL - Primary Data)]
        RedisCache[(Redis - Cache & Session)]
        RabbitMQ([RabbitMQ - Background Task Queue])
        Worker[Celery / Background Worker]
    end

    Client -->|HTTPS / REST / WS| Nginx
    Nginx --> API
    API --> AuthMiddleware
    AuthMiddleware --> BusinessLogic
    BusinessLogic --> DataLayer
    DataLayer --> Postgres
    BusinessLogic --> RedisCache
    BusinessLogic --> RabbitMQ
    RabbitMQ --> Worker
    Worker --> Postgres
```

---

## 7. Quy trình làm việc đề xuất khi vẽ sơ đồ

Khi người dùng yêu cầu vẽ sơ đồ kiến trúc hoặc thiết kế hệ thống, hãy thực hiện theo 4 bước chuẩn:
1. **Làm rõ yêu cầu & Phạm vi (Scope Clarification)**: Xác định rõ đối tượng mục tiêu, các luồng tương tác và mức độ chi tiết cần hiển thị.
2. **Chọn loại sơ đồ phù hợp**:
   - Nghiệp vụ tổng quan, phân quyền -> **Use Case Diagram**
   - Luồng tương tác giữa các API/Services -> **Sequence Diagram**
   - Thiết kế Database, Bảng, Khóa -> **ERD**
   - Vòng đời dữ liệu (Đơn hàng, Vé, Task) -> **State Diagram**
   - Kiến trúc tổng thể hạ tầng, vi dịch vụ -> **Architecture Flowchart**
3. **Viết mã Mermaid.js chuẩn chỉnh**: Đảm bảo node id sạch sẽ, các nhãn có ngoặc kép, định dạng rõ ràng.
4. **Cung cấp phần giải thích tóm tắt**: Chỉ rõ các điểm nổi bật của sơ đồ (Entity chính, điểm rẽ nhánh rủi ro, cơ chế fallback, transaction).
