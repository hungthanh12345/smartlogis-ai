# THIẾT KẾ CƠ SỞ DỮ LIỆU (DATABASE DESIGN SPECIFICATION)
## DỰ ÁN: HỆ THỐNG QUẢN LÝ KHO TÍCH HỢP AI (SMARTLOGIS AI V2.0)

---

## 1. TỔNG QUAN KIẾN TRÚC CSDL

* **Hệ quản trị CSDL mục tiêu:** PostgreSQL 15+ (Hỗ trợ đầy đủ Row-level locking SELECT ... FOR UPDATE và Check Constraints).
* **Môi trường phát triển cục bộ:** SQLite 3 (Tích hợp cơ chế Check Constraint và WAL mode).
* **Tầng truy cập dữ liệu (Data Access Layer):** SQLAlchemy ORM 2.0 kết hợp Pydantic Schemas v2 nhằm chuẩn hóa kiểu dữ liệu đầu vào/ra.
* **Nguyên tắc thiết kế:**
  * Chuẩn hóa CSDL đạt mức **3NF (Third Normal Form)** nhằm loại bỏ dư thừa dữ liệu.
  * Tách biệt bảng tổng hợp số dư tức thời (	on_kho) và bảng lịch sử biến động (	he_kho).
  * Sử dụng cấu trúc Master - Detail cho các chứng từ Nhập kho và Xuất kho.

---

## 2. SƠ ĐỒ THỰC THỂ QUAN HỆ (ENTITY RELATIONSHIP DIAGRAM - ERD)

`
+----------------+          +----------------+          +----------------+
|   nhom_hang    | 1      * |    hang_hoa    | 1      1 |    ton_kho     |
+----------------+----------+----------------+----------+----------------+
| PK MaNhom      |          | PK MaHH        |          | PK MaTK        |
|    TenNhom     |          |    TenHH       |          | FK MaHH (UQ)   |
|    MoTa        |          | FK MaNhom      |          |    SoLuongTon  |
+----------------+          | FK MaDVT       |          |    NgayCapNhat |
                            |    TonToiThieu |          +----------------+
+----------------+ 1      * |    MoTa        |                  |
|  don_vi_tinh   |----------+----------------+                  |
+----------------+                  | 1                         | 1
| PK MaDVT       |                  |                           |
|    TenDVT      |                  | *                         | *
+----------------+          +----------------+          +----------------+
                            |     the_kho    |          |   nguoi_dung   |
+----------------+ 1      * +----------------+          +----------------+
|  nha_cung_cap  |----+     | PK MaTK        |          | PK MaND        |
+----------------+    |     |    NgayGiaoDich|          |    TenDangNhap |
| PK MaNCC       |    |     | FK MaHH        |          |    MatKhau     |
|    TenNCC      |    |     |    MaChungTu   |          |    HoTen       |
|    DiaChi      |    |     |    LoaiGiaoDich|          |    VaiTro      |
|    SoDienThoai |    |     |    SoLuong     |          |    KichHoat    |
+----------------+    |     |    TonSauGD    |          +----------------+
                      |     +----------------+             | 1      | 1
                      |                                    |        |
                      | 1                                  | *      | *
+---------------------+----+                        +------+--------+----+
|        phieu_nhap        |                        |     phieu_xuat     |
+--------------------------+                        +--------------------+
| PK MaPN                  |                        | PK MaPX            |
|    NgayNhap              |                        |    NgayXuat        |
| FK MaNCC                 |                        |    NguoiNhan       |
| FK MaND                  |                        |    LyDoXuat        |
|    TongTien              |                        | FK MaND            |
|    GhiChu                |                        |    GhiChu          |
+--------------------------+                        +--------------------+
             | 1                                               | 1
             |                                                 |
             | *                                               | *
+--------------------------+                        +--------------------+
|   chi_tiet_phieu_nhap    |                        | chi_tiet_phieu_xuat|
+--------------------------+                        +--------------------+
| PK MaCTPN                |                        | PK MaCTPX          |
| FK MaPN                  |                        | FK MaPX            |
| FK MaHH                  |                        | FK MaHH            |
|    SoLuongNhap           |                        |    SoLuongXuat     |
|    DonGiaNhap            |                        +--------------------+
|    ThanhTien             |
+--------------------------+
`

---

## 3. ĐẶC TẢ CHI TIẾT CÁC BẢNG CƠ SỞ DỮ LIỆU

### 3.1. Bảng 
guoi_dung (Tài khoản & Phân quyền)
| Tên cột | Kiểu dữ liệu | Ràng buộc | Mô tả ý nghĩa |
| :--- | :--- | :--- | :--- |
| MaND | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Mã định danh người dùng |
| TenDangNhap | VARCHAR(50) | UNIQUE, NOT NULL | Tên đăng nhập hệ thống |
| MatKhau | VARCHAR(255) | NOT NULL | Chuỗi băm mật khẩu Bcrypt Hash |
| HoTen | VARCHAR(100) | NOT NULL | Họ và tên hiển thị |
| VaiTro | VARCHAR(20) | NOT NULL, DEFAULT 'Thukho' | Vai trò: Admin, Thukho, Ketoan |
| KichHoat | BOOLEAN | DEFAULT TRUE | Trạng thái hoạt động của tài khoản |
| NgayTao | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Thời điểm khởi tạo tài khoản |

### 3.2. Bảng 
hom_hang (Phân loại mặt hàng)
| Tên cột | Kiểu dữ liệu | Ràng buộc | Mô tả ý nghĩa |
| :--- | :--- | :--- | :--- |
| MaNhom | VARCHAR(20) | PRIMARY KEY | Mã nhóm hàng (VD: NH-THEP, NH-SON) |
| TenNhom | VARCHAR(100) | NOT NULL | Tên loại nhóm hàng |
| MoTa | TEXT | NULLABLE | Mô tả đặc tính kỹ thuật của nhóm |

### 3.3. Bảng don_vi_tinh (Đơn vị đo lường)
| Tên cột | Kiểu dữ liệu | Ràng buộc | Mô tả ý nghĩa |
| :--- | :--- | :--- | :--- |
| MaDVT | VARCHAR(20) | PRIMARY KEY | Mã đơn vị tính (Cuon, Cay, Bao, Thung...) |
| TenDVT | VARCHAR(50) | NOT NULL | Tên hiển thị đơn vị đo |

### 3.4. Bảng 
ha_cung_cap (Đối tác cung ứng vật tư)
| Tên cột | Kiểu dữ liệu | Ràng buộc | Mô tả ý nghĩa |
| :--- | :--- | :--- | :--- |
| MaNCC | VARCHAR(20) | PRIMARY KEY | Mã đối tác nhà cung cấp |
| TenNCC | VARCHAR(150) | NOT NULL | Tên doanh nghiệp cung cấp |
| DiaChi | VARCHAR(255) | NULLABLE | Địa chỉ trụ sở/kho bãi |
| SoDienThoai | VARCHAR(20) | NULLABLE | Số hotline liên hệ |
| Email | VARCHAR(100) | NULLABLE | Thư điện tử giao dịch |

### 3.5. Bảng hang_hoa (Danh mục vật tư hàng hóa)
| Tên cột | Kiểu dữ liệu | Ràng buộc | Mô tả ý nghĩa |
| :--- | :--- | :--- | :--- |
| MaHH | VARCHAR(20) | PRIMARY KEY | Mã SKU mặt hàng (VD: HH-001) |
| TenHH | VARCHAR(150) | NOT NULL | Tên chi tiết hàng hóa vật tư |
| MaNhom | VARCHAR(20) | FOREIGN KEY (
hom_hang.MaNhom) | Nhóm ngành hàng |
| MaDVT | VARCHAR(20) | FOREIGN KEY (don_vi_tinh.MaDVT) | Đơn vị tính |
| TonToiThieu | INTEGER | NOT NULL, DEFAULT 0 | Định mức tồn an toàn (Safety Stock) |
| MoTa | TEXT | NULLABLE | Thông số kỹ thuật/quy cách đóng gói |

### 3.6. Bảng 	on_kho (Số dư khả dụng thời gian thực)
| Tên cột | Kiểu dữ liệu | Ràng buộc | Mô tả ý nghĩa |
| :--- | :--- | :--- | :--- |
| MaTK | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Khóa chính bản ghi tồn |
| MaHH | VARCHAR(20) | UNIQUE, FOREIGN KEY (hang_hoa.MaHH) | Liên kết 1-1 với Hàng hóa |
| SoLuongTon | INTEGER | NOT NULL, **CHECK (SoLuongTon >= 0)** | **Số lượng tồn kho (Không bao giờ âm)** |
| NgayCapNhat| TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Thời điểm cập nhật biến động gần nhất |

### 3.7. Bảng phieu_nhap (Master Phiếu Nhập)
| Tên cột | Kiểu dữ liệu | Ràng buộc | Mô tả ý nghĩa |
| :--- | :--- | :--- | :--- |
| MaPN | VARCHAR(30) | PRIMARY KEY | Mã chứng từ nhập (VD: PN-20260904-XXXX) |
| NgayNhap | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Ngày giờ ghi nhận nhập hàng |
| MaNCC | VARCHAR(20) | FOREIGN KEY (
ha_cung_cap.MaNCC) | Nhà cung cấp xuất hóa đơn |
| MaND | INTEGER | FOREIGN KEY (
guoi_dung.MaND) | Thủ kho trực tiếp lập phiếu |
| TongTien | FLOAT | DEFAULT 0.0 | Tổng giá trị hàng nhập |
| GhiChu | TEXT | NULLABLE | Ghi chú đợt nhập |

### 3.8. Bảng chi_tiet_phieu_nhap (Detail Phiếu Nhập)
| Tên cột | Kiểu dữ liệu | Ràng buộc | Mô tả ý nghĩa |
| :--- | :--- | :--- | :--- |
| MaCTPN | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Mã dòng chi tiết |
| MaPN | VARCHAR(30) | FOREIGN KEY (phieu_nhap.MaPN) | Khóa ngoại liên kết chứng từ cha |
| MaHH | VARCHAR(20) | FOREIGN KEY (hang_hoa.MaHH) | Mã hàng nhập |
| SoLuongNhap| INTEGER | NOT NULL, CHECK (SoLuongNhap > 0) | Số lượng nhập |
| DonGiaNhap | FLOAT | NOT NULL, CHECK (DonGiaNhap >= 0) | Đơn giá mua vào từ NCC |
| ThanhTien | FLOAT | NOT NULL | Thành tiền = SoLuongNhap * DonGiaNhap |

### 3.9. Bảng phieu_xuat (Master Phiếu Xuất)
| Tên cột | Kiểu dữ liệu | Ràng buộc | Mô tả ý nghĩa |
| :--- | :--- | :--- | :--- |
| MaPX | VARCHAR(30) | PRIMARY KEY | Mã chứng từ xuất (VD: PX-20260904-XXXX) |
| NgayXuat | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Ngày giờ xuất kho vật tư |
| NguoiNhan | VARCHAR(100) | NOT NULL | Người/Đội công trình tiếp nhận hàng |
| LyDoXuat | VARCHAR(255) | NULLABLE | Mục đích xuất hàng |
| MaND | INTEGER | FOREIGN KEY (
guoi_dung.MaND) | Thủ kho thực hiện xuất kho |
| GhiChu | TEXT | NULLABLE | Ghi chú giao hàng |

### 3.10. Bảng chi_tiet_phieu_xuat (Detail Phiếu Xuất)
| Tên cột | Kiểu dữ liệu | Ràng buộc | Mô tả ý nghĩa |
| :--- | :--- | :--- | :--- |
| MaCTPX | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Mã dòng chi tiết |
| MaPX | VARCHAR(30) | FOREIGN KEY (phieu_xuat.MaPX) | Khóa ngoại liên kết chứng từ cha |
| MaHH | VARCHAR(20) | FOREIGN KEY (hang_hoa.MaHH) | Mặt hàng xuất |
| SoLuongXuat| INTEGER | NOT NULL, CHECK (SoLuongXuat > 0) | Số lượng xuất khỏi kho |

### 3.11. Bảng 	he_kho (Sổ Thẻ Kho Lũy Kế Lịch Sử)
| Tên cột | Kiểu dữ liệu | Ràng buộc | Mô tả ý nghĩa |
| :--- | :--- | :--- | :--- |
| MaTK | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Mã bản ghi thẻ kho |
| NgayGiaoDich| TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Thời điểm diễn ra giao dịch |
| MaHH | VARCHAR(20) | FOREIGN KEY (hang_hoa.MaHH) | Mã hàng hóa liên quan |
| MaChungTu | VARCHAR(30) | NOT NULL | Số hiệu chứng từ gốc (Mã PN hoặc Mã PX) |
| LoaiGiaoDich| VARCHAR(10) | NOT NULL | NHAP (Nhập hàng) hoặc XUAT (Xuất hàng) |
| SoLuongThayDoi| INTEGER | NOT NULL | Số lượng biến động dương (khi nhập) hoặc âm |
| TonSauGiaoDich| INTEGER | NOT NULL | **Số lượng tồn kho lũy kế ngay sau giao dịch** |

---

## 4. CHIẾN LƯỢC TOÀN VẸN DỮ LIỆU & PHÒNG CHỐNG TỒN ÂM

### 4.1. Check Constraint mức CSDL
Tất cả bảng chứa số lượng được bảo vệ bởi mệnh đề ràng buộc cứng:
`sql
ALTER TABLE ton_kho ADD CONSTRAINT chk_ton_khong_am CHECK (SoLuongTon >= 0);
ALTER TABLE chi_tiet_phieu_nhap ADD CONSTRAINT chk_nhap_duong CHECK (SoLuongNhap > 0 AND DonGiaNhap >= 0);
ALTER TABLE chi_tiet_phieu_xuat ADD CONSTRAINT chk_xuat_duong CHECK (SoLuongXuat > 0);
`

### 4.2. Khóa Bi Quan (Pessimistic Locking SELECT ... FOR UPDATE)
Trong môi trường có nhiều thủ kho cùng thao tác xuất cùng một mặt hàng đồng thời (Concurrency), hệ thống áp dụng kỹ thuật khóa bi quan:
`python
# SQLAlchemy Implementation
ton_record = db.query(TonKho).filter(TonKho.MaHH == item.MaHH).with_for_update().first()
if ton_record.SoLuongTon < item.SoLuongXuat:
    db.rollback()
    raise HTTPException(status_code=400, detail= Không đủ tồn kho để xuất.)
ton_record.SoLuongTon -= item.SoLuongXuat
db.commit()
`
Cơ chế này ép các transaction khác phải chờ đợi, đảm bảo số dư được kiểm tra và trừ tuần tự, triệt tiêu race condition.
