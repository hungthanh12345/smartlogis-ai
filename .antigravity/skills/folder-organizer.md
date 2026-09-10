---
name: folder-organizer
description: Chuyên gia tư vấn, thiết kế, sắp xếp và chuẩn hóa cấu trúc thư mục dự án phần mềm theo các kiến trúc chuẩn (Clean Architecture, Layered/MVC, Feature-based, Monorepo).
version: 1.0.0
---

# Skill: Folder Organizer (Project Structure & Architecture Architect)

## 1. Giới thiệu & Vai trò

`folder-organizer` là kỹ năng chuyên biệt hướng dẫn phân tích, thiết kế, sắp xếp và tái cấu trúc (refactoring) cây thư mục cho các dự án phần mềm. 

Một cấu trúc thư mục chuẩn hóa giúp:
- **Tăng tốc độ Onboarding**: Lập trình viên mới có thể hiểu ngay vị trí của từng thành phần trong 5 phút đầu tiên.
- **Dễ bảo trì & Mở rộng (Maintainability & Scalability)**: Hạn chế tối đa tình trạng phụ thuộc vòng (circular dependencies) và "god-files" (những file chứa hàng nghìn dòng code hỗn tạp).
- **Phân tách trách nhiệm rõ ràng (Separation of Concerns)**: Tách biệt rạch ròi giữa giao diện (Presentation), nghiệp vụ (Business Logic), truy xuất dữ liệu (Data Access), và hạ tầng (Infrastructure).

---

## 2. Các nguyên tắc thiết kế thư mục cốt lõi

1. **Separation of Concerns (SoC - Phân tách mối quan tâm)**:
   - Tầng định tuyến (Routes/Controllers) chỉ tiếp nhận HTTP request, validate schema và gọi Service.
   - Tầng Service chứa 100% logic nghiệp vụ, không trực tiếp viết SQL thuần hoặc phụ thuộc vào framework HTTP.
   - Tầng Repository/DAO chịu trách nhiệm tương tác cơ sở dữ liệu.
2. **Colocation (Gom nhóm theo ngữ cảnh)**:
   - Các file có xu hướng thay đổi cùng nhau thì nên nằm gần nhau (ví dụ: `button.tsx`, `button.test.tsx`, `button.module.css`).
3. **Predictability & Discoverability (Dễ đoán & Dễ tìm)**:
   - Đặt tên thư mục và file rõ nghĩa, nhìn vào đường dẫn là biết ngay trách nhiệm của file.
4. **Single Source of Truth (Nguồn chân lý duy nhất)**:
   - Mọi cấu hình môi trường, hằng số toàn cục, kiểu dữ liệu chung phải được tập trung ở thư mục quy chuẩn (`config/`, `constants/`, `types/`).
5. **No Broken Windows**:
   - Không để các file rác, file nháp thử nghiệm nằm vương vãi ở thư mục gốc (Root directory). Luôn có thư mục `scripts/` hoặc `scratch/` cho tác vụ tạm.

---

## 3. Các mẫu cấu trúc thư mục chuẩn thực chiến

### Pattern A: Modular Layered Architecture (Khuyên dùng cho Backend FastAPI / Node.js / Go)
*Mô hình phân tầng theo module/domain, cực kỳ thích hợp cho các dự án Backend REST API, Microservices vừa và nhỏ.*

```text
my-backend-project/
├── .env.example             # Template biến môi trường
├── .gitignore               # Loại trừ file rác, virtualenv, caches
├── Dockerfile               # Cấu hình containerization
├── docker-compose.yml       # Điều phối dịch vụ (App, DB, Redis)
├── README.md                # Tài liệu tổng quan, hướng dẫn setup
├── requirements.txt         # Dependencies (Python) hoặc package.json
│
├── app/                     # Mã nguồn chính của ứng dụng
│   ├── __init__.py
│   ├── main.py              # Khởi tạo App (FastAPI/Express instance), gắn middleware
│   │
│   ├── api/                 # Tầng giao tiếp mạng (Controllers / Routers)
│   │   ├── __init__.py
│   │   ├── deps.py          # Dependency Injection (Auth, DB session, Permissions)
│   │   └── v1/              # Versioning API
│   │       ├── __init__.py
│   │       ├── router.py    # Tổng hợp các endpoint v1
│   │       └── endpoints/
│   │           ├── auth.py
│   │           ├── users.py
│   │           ├── orders.py
│   │           └── shipments.py
│   │
│   ├── core/                # Các cấu hình nòng cốt, bảo mật
│   │   ├── __init__.py
│   │   ├── config.py        # Đọc biến môi trường (.env) bằng Pydantic Settings
│   │   ├── security.py      # Băm mật khẩu (bcrypt), tạo & giải mã JWT token
│   │   └── logging.py       # Cấu hình Structured Logger
│   │
│   ├── db/                  # Quản lý kết nối cơ sở dữ liệu & Migrations
│   │   ├── __init__.py
│   │   ├── session.py       # Khởi tạo Engine, SessionMaker
│   │   ├── base.py          # Khai báo Base class của ORM
│   │   └── migrations/      # Thư mục Alembic migrations
│   │
│   ├── models/              # Định nghĩa bảng CSDL (ORM Entities: SQLAlchemy, Prisma)
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── order.py
│   │   └── vehicle.py
│   │
│   ├── schemas/             # DTO (Data Transfer Objects) / Pydantic Models (Validation)
│   │   ├── __init__.py
│   │   ├── user.py          # UserCreate, UserUpdate, UserResponse
│   │   └── order.py         # OrderCreate, OrderFilter, OrderOut
│   │
│   ├── services/            # Logic nghiệp vụ trung tâm (Business Logic Layer)
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── order_service.py
│   │   └── routing_optimizer.py
│   │
│   ├── repositories/        # (Tùy chọn) Thao tác truy vấn DB nâng cao (DAO)
│   │   ├── __init__.py
│   │   ├── user_repository.py
│   │   └── order_repository.py
│   │
│   └── utils/               # Tiện ích bổ trợ dùng chung
│       ├── __init__.py
│       ├── datetime_helper.py
│       └── geo_calculator.py
│
├── tests/                   # Kiểm thử tự động (Unit & Integration Tests)
│   ├── conftest.py          # Fixtures, test database mock
│   ├── test_api/            # Kiểm thử các API Endpoints
│   └── test_services/       # Kiểm thử logic nghiệp vụ
│
├── docs/                    # Tài liệu kiến trúc, sơ đồ, hướng dẫn API
└── scripts/                 # Script bảo trì, seed data ban đầu
    ├── seed_db.py
    └── run_migrations.sh
```

---

### Pattern B: Clean Architecture / Hexagonal Architecture (Enterprise & DDD)
*Dành cho các hệ thống quy mô lớn cần độc lập hoàn toàn với Framework, Database và UI.*

```text
src/
├── domain/                  # Lõi hệ thống: Độc lập 100% với bên ngoài
│   ├── entities/            # Doanh nghiệp cốt lõi (User, Order)
│   ├── value_objects/       # Money, Email, Coordinate
│   ├── exceptions/          # Domain errors
│   └── repositories/        # Interfaces/Protocols (Cổng giao tiếp dữ liệu)
│
├── application/             # Use Cases nghiệp vụ cụ thể
│   ├── use_cases/           # CreateOrderUseCase, CancelOrderUseCase
│   ├── dtos/                # Request & Response Data Transfer Objects
│   └── interfaces/          # Cổng dịch vụ ngoài (IEmailService, IPaymentGateway)
│
├── infrastructure/          # Chi tiết cài đặt công nghệ bên ngoài
│   ├── database/            # SQLAlchemy / TypeORM implementations
│   ├── external_apis/       # StripeGateway, GoogleMapsService
│   ├── cache/               # RedisCacheAdapter
│   └── message_broker/      # RabbitMQPublisher
│
└── presentation/            # Đầu vào giao diện người dùng
    ├── http/                # REST Controllers, Middlewares
    ├── cli/                 # Console commands
    └── workers/             # Background consumer jobs
```

---

### Pattern C: Feature-based Architecture (Khuyên dùng cho Frontend Hiện Đại: React / Next.js)
*Gom nhóm code theo tính năng (Feature-first) thay vì loại file (Type-first).*

```text
src/
├── app/                     # Next.js App Router (Layouts & Route pages)
│   ├── layout.tsx
│   ├── page.tsx
│   ├── (auth)/login/page.tsx
│   └── dashboard/
│
├── features/                # Từng tính năng độc lập, khép kín
│   ├── authentication/
│   │   ├── components/      # LoginForm.tsx, OAuthButton.tsx
│   │   ├── hooks/           # useAuth.ts, useCurrentUser.ts
│   │   ├── api/             # authApi.ts
│   │   └── types/           # auth.types.ts
│   │
│   └── order-tracking/
│       ├── components/      # OrderMap.tsx, StatusBadge.tsx
│       ├── hooks/           # useLiveLocation.ts
│       ├── services/        # trackingSocket.ts
│       └── types/           # order.types.ts
│
├── shared/                  # Tài nguyên dùng chung cho toàn bộ ứng dụng
│   ├── components/          # Button, Modal, Input, Table
│   ├── hooks/               # useDebounce, useLocalStorage
│   ├── utils/               # formatCurrency, formatDate
│   └── constants/           # routes.ts, config.ts
│
└── assets/                  # Hình ảnh, icons, fonts tĩnh
```

---

## 4. Quy chuẩn đặt tên (Naming Conventions)

| Thành phần | Quy ước | Ví dụ |
| :--- | :--- | :--- |
| **Thư mục (Directories)** | `kebab-case` hoặc `snake_case` (thống nhất trong dự án) | `order-tracking/`, `api_v1/` |
| **File Python** | `snake_case` | `order_service.py`, `auth_middleware.py` |
| **File TypeScript/JS** | `camelCase` (logic/utils) hoặc `kebab-case` | `formatDate.ts`, `api-client.ts` |
| **React Components** | `PascalCase` | `UserProfileCard.tsx`, `NavigationBar.tsx` |
| **Data Models / Entities** | Danh từ số ít, `snake_case` hoặc `PascalCase` | `user.py` (`class User`), `order_item.py` |
| **Unit Tests** | Tiền tố `test_` hoặc hậu tố `.test.` / `.spec.` | `test_order_service.py`, `Button.test.tsx` |

---

## 5. Quy trình 5 bước tái cấu trúc thư mục (Refactoring Workflow)

Khi tiếp nhận một dự án có cấu trúc thư mục lộn xộn hoặc cần chuẩn hóa, hãy thực hiện tuần tự:

1. **Khảo sát hiện trạng (Audit Current Structure)**:
   - Liệt kê toàn bộ cây thư mục gốc.
   - Xác định Tech Stack chính (FastAPI, NestJS, Next.js, Django, v.v.).
   - Nhận diện các file "rác" hoặc các file lớn kiêm nhiệm quá nhiều nhiệm vụ.
2. **Thiết kế Cây thư mục Đích (Target Architecture Plan)**:
   - Lựa chọn Pattern phù hợp (Layered, Clean, hoặc Feature-based).
   - Vẽ cây thư mục dự kiến và nêu rõ lý do di chuyển từng nhóm file.
3. **Thực thi di chuyển theo từng giai đoạn an toàn (Incremental Migration)**:
   - Di chuyển các file dùng chung và cấu hình trước (`config`, `constants`, `utils`).
   - Di chuyển tầng dữ liệu (`models`, `schemas`, `db`).
   - Di chuyển tầng nghiệp vụ (`services`).
   - Di chuyển tầng định tuyến (`api`, `controllers`).
4. **Cập nhật Import Statements**:
   - Cập nhật toàn bộ đường dẫn import tương ứng ở các file đã di chuyển.
   - Ưu tiên sử dụng Absolute Imports (hoặc Path Aliases như `@/components`, `app.services`) thay vì relative imports phức tạp (`../../../../utils`).
5. **Kiểm tra & Dọn dẹp (Verify & Clean Up)**:
   - Chạy lệnh test, linter hoặc khởi động máy chủ để kiểm tra syntax errors / import errors.
   - Xóa các thư mục rỗng và file tạm không còn sử dụng.

---

## 6. Checklist đánh giá cấu trúc thư mục đạt chuẩn

- [ ] **Gốc dự án sạch sẽ**: Chỉ chứa các file cấu hình tiêu chuẩn (`.gitignore`, `.env.example`, `README.md`, config files). Không có file code test tạm.
- [ ] **Ranh giới module rõ ràng**: Không có logic truy vấn database trực tiếp trong controller/router.
- [ ] **Quản lý Secrets chuẩn mực**: Tuyệt đối không commit file `.env` chứa credentials thật; luôn có `.env.example`.
- [ ] **Cấu trúc kiểm thử song hành**: Thư mục `tests/` phản ánh tương ứng cấu trúc module của `app/` hoặc `src/`.
- [ ] **Không có Circular Dependency**: Các module cấp thấp không import ngược lại các module cấp cao hơn.
