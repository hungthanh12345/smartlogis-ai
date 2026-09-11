# THIẾT KẾ CƠ SỞ DỮ LIỆU (DATABASE DESIGN SPECIFICATION)
## DỰ ÁN: HỆ THỐNG QUẢN LÝ KHO THÔNG MINH TÍCH HỢP AI (SMARTLOGIS AI V4.0)

---

## 1. TỔNG QUAN KIẾN TRÚC CSDL (DUAL-DATABASE ARCHITECTURE)

* **Hệ quản trị CSDL chính thức (Production):** MySQL Server 8.0 (InnoDB Engine hỗ trợ ACID Transactions, Row-level locking và Check Constraints phần cứng).
* **Hệ quản trị CSDL dự phòng / Kiểm thử (Local/Fallback):** SQLite 3 (Chế độ Write-Ahead Logging WAL mode, Foreign Keys ON, Check Constraints).
* **Tùy chọn mở rộng:** PostgreSQL 15+ (Đã được đóng gói sẵn sàng trong Docker Compose với pgAdmin 4).
* **Tầng truy cập dữ liệu (Data Access Layer):** SQLAlchemy ORM 2.0 kết hợp Pydantic v2 Schemas (`ConfigDict(from_attributes=True)`) đảm bảo tính toàn vẹn và type safety tuyệt đối.
* **Nguyên tắc thiết kế chuẩn mực:**
  * Đạt chuẩn hóa **3NF (Third Normal Form)**, triệt tiêu dư thừa dữ liệu.
  * Tách biệt bảng tổng hợp số dư tức thời (`ton_kho`) và bảng lịch sử lưu vết biến động (`the_kho`).
  * Sử dụng cấu trúc Master - Detail cho các chứng từ Nhập kho (`phieu_nhap` - `chi_tiet_phieu_nhap`) và Xuất kho (`phieu_xuat` - `chi_tiet_phieu_xuat`).
  * Áp dụng cơ chế bảo vệ 2 tầng chống tồn âm: Atomic SQL Decrement tại ứng dụng và Hardware `CHECK (SoLuongTon >= 0)` tại CSDL.

---

## 2. SƠ ĐỒ THỰC THỂ QUAN HỆ (ENTITY RELATIONSHIP DIAGRAM - ERD)

```
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
```

---

## 3. ĐẶC TẢ CHI TIẾT 11 BẢNG CƠ SỞ DỮ LIỆU

### 3.1. Bảng `nguoi_dung` (Tài khoản & Phân quyền RBAC)
| Tên cột | Kiểu dữ liệu | Ràng buộc | Mô tả ý nghĩa |
| :--- | :--- | :--- | :--- |
| `MaND` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Mã định danh người dùng |
| `TenDangNhap` | VARCHAR(50) | UNIQUE, NOT NULL | Tên đăng nhập hệ thống |
| `MatKhau` | VARCHAR(255) | NOT NULL | Chuỗi băm mật khẩu Bcrypt Hash an toàn |
| `HoTen` | VARCHAR(100) | NOT NULL | Họ và tên hiển thị |
| `VaiTro` | VARCHAR(20) | NOT NULL | 3 vai trò: `Admin`, `Thukho` (kiêm Kế toán), `Nhanvien` (Chỉ đọc) |
| `KichHoat` | BOOLEAN | DEFAULT TRUE | Trạng thái hoạt động tài khoản |
| `NgayTao` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Thời điểm khởi tạo tài khoản |

### 3.2. Bảng `nhom_hang` (Phân loại nhóm vật tư)
| Tên cột | Kiểu dữ liệu | Ràng buộc | Mô tả ý nghĩa |
| :--- | :--- | :--- | :--- |
| `MaNhom` | VARCHAR(20) | PRIMARY KEY | Mã nhóm hàng (VD: NH-THEP, NH-XI, NH-SON) |
| `TenNhom` | VARCHAR(100) | NOT NULL | Tên nhóm hàng |
| `MoTa` | TEXT | NULLABLE | Mô tả đặc tính kỹ thuật nhóm vật tư |

### 3.3. Bảng `don_vi_tinh` (Đơn vị tính chuẩn hóa)
| Tên cột | Kiểu dữ liệu | Ràng buộc | Mô tả ý nghĩa |
| :--- | :--- | :--- | :--- |
| `MaDVT` | VARCHAR(20) | PRIMARY KEY | Mã đơn vị tính (Cuon, Cay, Bao, Thung, Kg...) |
| `TenDVT` | VARCHAR(50) | NOT NULL | Tên hiển thị đơn vị đo |

### 3.4. Bảng `nha_cung_cap` (Đối tác nhà cung cấp)
| Tên cột | Kiểu dữ liệu | Ràng buộc | Mô tả ý nghĩa |
| :--- | :--- | :--- | :--- |
| `MaNCC` | VARCHAR(20) | PRIMARY KEY | Mã đối tác nhà cung cấp (VD: NCC-01) |
| `TenNCC` | VARCHAR(150) | NOT NULL | Tên doanh nghiệp cung cấp |
| `DiaChi` | VARCHAR(255) | NULLABLE | Địa chỉ trụ sở/kho bãi |
| `SoDienThoai` | VARCHAR(20) | NULLABLE | Số hotline liên hệ |
| `Email` | VARCHAR(100) | NULLABLE | Thư điện tử giao dịch |

### 3.5. Bảng `hang_hoa` (Danh mục mặt hàng - SKU)
| Tên cột | Kiểu dữ liệu | Ràng buộc | Mô tả ý nghĩa |
| :--- | :--- | :--- | :--- |
| `MaHH` | VARCHAR(20) | PRIMARY KEY | Mã SKU mặt hàng (VD: HH-THEP-D10) |
| `TenHH` | VARCHAR(150) | NOT NULL | Tên chi tiết hàng hóa vật tư |
| `MaNhom` | VARCHAR(20) | FOREIGN KEY (`nhom_hang.MaNhom`) | Nhóm ngành hàng |
| `MaDVT` | VARCHAR(20) | FOREIGN KEY (`don_vi_tinh.MaDVT`) | Đơn vị tính |
| `TonToiThieu` | INTEGER | NOT NULL, DEFAULT 0 | Định mức tồn an toàn (Safety Stock) |
| `MoTa` | TEXT | NULLABLE | Thông số kỹ thuật / quy cách đóng gói |

### 3.6. Bảng `ton_kho` (Số dư tồn kho khả dụng thời gian thực)
| Tên cột | Kiểu dữ liệu | Ràng buộc | Mô tả ý nghĩa |
| :--- | :--- | :--- | :--- |
| `MaTK` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Khóa chính bản ghi tồn |
| `MaHH` | VARCHAR(20) | UNIQUE, FOREIGN KEY (`hang_hoa.MaHH`) | Liên kết 1-1 với Hàng hóa |
| `SoLuongTon` | INTEGER | NOT NULL, **CHECK (SoLuongTon >= 0)** | **Số lượng tồn kho (Khóa cứng chống tồn âm)** |
| `NgayCapNhat`| TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Thời điểm cập nhật biến động gần nhất |

### 3.7. Bảng `phieu_nhap` (Master Phiếu Nhập Kho - Inbound)
| Tên cột | Kiểu dữ liệu | Ràng buộc | Mô tả ý nghĩa |
| :--- | :--- | :--- | :--- |
| `MaPN` | VARCHAR(30) | PRIMARY KEY | Mã chứng từ nhập (VD: PN-YYYYMMDD-XXXXXX) |
| `NgayNhap` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Ngày giờ ghi nhận nhập hàng |
| `MaNCC` | VARCHAR(20) | FOREIGN KEY (`nha_cung_cap.MaNCC`) | Nhà cung cấp xuất hóa đơn |
| `MaND` | INTEGER | FOREIGN KEY (`nguoi_dung.MaND`) | Thủ kho kiêm Kế toán trực tiếp lập phiếu |
| `TongTien` | FLOAT | DEFAULT 0.0 | Tổng giá trị hàng nhập (VNĐ) |
| `GhiChu` | TEXT | NULLABLE | Ghi chú đợt nhập hàng |

### 3.8. Bảng `chi_tiet_phieu_nhap` (Detail Chi Tiết Hàng Nhập)
| Tên cột | Kiểu dữ liệu | Ràng buộc | Mô tả ý nghĩa |
| :--- | :--- | :--- | :--- |
| `MaCTPN` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Mã dòng chi tiết |
| `MaPN` | VARCHAR(30) | FOREIGN KEY (`phieu_nhap.MaPN`) | Khóa ngoại liên kết chứng từ cha |
| `MaHH` | VARCHAR(20) | FOREIGN KEY (`hang_hoa.MaHH`) | Mã hàng nhập |
| `SoLuongNhap`| INTEGER | NOT NULL, CHECK (SoLuongNhap > 0) | Số lượng nhập |
| `DonGiaNhap` | FLOAT | NOT NULL, CHECK (DonGiaNhap >= 0) | Đơn giá mua vào từ NCC |
| `ThanhTien` | FLOAT | NOT NULL | Thành tiền = SoLuongNhap * DonGiaNhap |

### 3.9. Bảng `phieu_xuat` (Master Phiếu Xuất Kho - Outbound)
| Tên cột | Kiểu dữ liệu | Ràng buộc | Mô tả ý nghĩa |
| :--- | :--- | :--- | :--- |
| `MaPX` | VARCHAR(30) | PRIMARY KEY | Mã chứng từ xuất (VD: PX-YYYYMMDD-XXXXXX) |
| `NgayXuat` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Ngày giờ xuất kho vật tư |
| `NguoiNhan` | VARCHAR(100) | NOT NULL | Người / Đội công trình tiếp nhận hàng |
| `LyDoXuat` | VARCHAR(255) | NULLABLE | Mục đích xuất hàng |
| `MaND` | INTEGER | FOREIGN KEY (`nguoi_dung.MaND`) | Thủ kho kiêm Kế toán thực hiện xuất kho |
| `GhiChu` | TEXT | NULLABLE | Ghi chú giao hàng |

### 3.10. Bảng `chi_tiet_phieu_xuat` (Detail Chi Tiết Hàng Xuất)
| Tên cột | Kiểu dữ liệu | Ràng buộc | Mô tả ý nghĩa |
| :--- | :--- | :--- | :--- |
| `MaCTPX` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Mã dòng chi tiết |
| `MaPX` | VARCHAR(30) | FOREIGN KEY (`phieu_xuat.MaPX`) | Khóa ngoại liên kết chứng từ cha |
| `MaHH` | VARCHAR(20) | FOREIGN KEY (`hang_hoa.MaHH`) | Mặt hàng xuất |
| `SoLuongXuat`| INTEGER | NOT NULL, CHECK (SoLuongXuat > 0) | Số lượng xuất khỏi kho |

### 3.11. Bảng `the_kho` (Sổ Thẻ Kho Lưu Vết Lịch Sử Giao Dịch)
| Tên cột | Kiểu dữ liệu | Ràng buộc | Mô tả ý nghĩa |
| :--- | :--- | :--- | :--- |
| `MaTK` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Mã bản ghi thẻ kho |
| `NgayGiaoDich`| TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Thời điểm diễn ra giao dịch |
| `MaHH` | VARCHAR(20) | FOREIGN KEY (`hang_hoa.MaHH`) | Mã hàng hóa liên quan |
| `MaChungTu` | VARCHAR(30) | NOT NULL | Số hiệu chứng từ gốc (Mã PN hoặc Mã PX) |
| `LoaiGiaoDich`| VARCHAR(10) | NOT NULL | `NHAP` (Nhập kho) hoặc `XUAT` (Xuất kho) |
| `SoLuongThayDoi`| INTEGER | NOT NULL | Biến động (+ khi nhập, - khi xuất) |
| `TonSauGiaoDich`| INTEGER | NOT NULL | **Số lượng tồn kho lũy kế ngay sau giao dịch** |

---

## 4. CHIẾN LƯỢC TOÀN VẸN DỮ LIỆU & PHÒNG CHỐNG TỒN ÂM 2 TẦNG

### 4.1. Tầng 1: Atomic SQL Decrement (Mức Ứng Dụng)
Trong môi trường có nhiều người dùng cùng thao tác xuất cùng một mặt hàng đồng thời (Race Condition), hệ thống thực thi câu lệnh trừ số lượng nguyên tử trong Transaction:
```python
# Atomic SQL Decrement kiểm tra điều kiện tồn kho ngay trong câu UPDATE
affected = db.query(TonKho).filter(
    TonKho.MaHH == item.MaHH,
    TonKho.SoLuongTon >= item.SoLuongXuat
).update(
    {TonKho.SoLuongTon: TonKho.SoLuongTon - item.SoLuongXuat},
    synchronize_session=False
)

if affected == 0:
    db.rollback()
    raise HTTPException(status_code=400, detail=f"Hàng '{item.MaHH}' không đủ tồn kho khả dụng để xuất.")
```

### 4.2. Tầng 2: Hardware Check Constraint & Trigger (Mức CSDL)
Tất cả bảng chứa số lượng được bảo vệ bởi mệnh đề ràng buộc cứng mức CSDL:
```sql
-- MySQL 8.0 & SQLite Check Constraint:
ALTER TABLE ton_kho ADD CONSTRAINT chk_ton_khong_am CHECK (SoLuongTon >= 0);
ALTER TABLE chi_tiet_phieu_nhap ADD CONSTRAINT chk_nhap_duong CHECK (SoLuongNhap > 0 AND DonGiaNhap >= 0);
ALTER TABLE chi_tiet_phieu_xuat ADD CONSTRAINT chk_xuat_duong CHECK (SoLuongXuat > 0);
```
Nếu bất kỳ luồng nào cố tình ghi đè làm `SoLuongTon < 0`, CSDL lập tức từ chối và văng `IntegrityError`, kích hoạt Rollback toàn phần.

---

## 5. TỐI ƯU HÓA TRUY VẤN VỚI 8 CHỈ MỤC B-TREE (INDEXING STRATEGY)

Để đảm bảo hiệu năng cao với thời gian truy vấn dưới 5ms trên tập dữ liệu lớn:
1. `idx_tonkho_mahh`: Tìm kiếm số dư tức thời theo mã SKU `MaHH`.
2. `idx_thekho_mahh_ngay`: Truy vấn lịch sử sổ thẻ kho theo `MaHH` và khoảng thời gian `NgayGiaoDich`.
3. `idx_thekho_machungtu`: Tra cứu thẻ kho theo mã chứng từ `MaChungTu`.
4. `idx_phieunhap_ngay`: Báo cáo nhập kho theo ngày `NgayNhap`.
5. `idx_phieunhap_mancc`: Lọc phiếu nhập theo nhà cung cấp `MaNCC`.
6. `idx_phieuxuat_ngay`: Báo cáo xuất kho theo ngày `NgayXuat`.
7. `idx_hanghoa_manhom`: Lọc danh mục hàng hóa theo nhóm ngành `MaNhom`.
8. `idx_nguoidung_tendangnhap`: Tăng tốc xác thực người dùng `TenDangNhap`.
