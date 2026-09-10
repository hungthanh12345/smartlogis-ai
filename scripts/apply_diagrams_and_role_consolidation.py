# scripts/apply_diagrams_and_role_consolidation.py
"""
Script Đồng Bộ Hóa Toàn Diện File Báo Cáo Word (BAO_CAO_DU_AN_QUAN_LY_KHO  (4).docx)
Nhiệm vụ:
1. Sao lưu file gốc trước khi thực hiện.
2. Thay thế toàn bộ 14 sơ đồ kiến trúc cũ (image3.png -> image16.png) bằng 14 sơ đồ mới
   được tạo từ skill 'diagram-architect' chuẩn hóa mô hình "Thủ kho kiêm Kế toán" & "MySQL 8.0".
3. Cập nhật các đoạn văn bản (Paragraphs) và các bảng (Tables 5 & 15) xóa bỏ hoàn toàn
   khái niệm 3 vai trò rời rạc, chuẩn hóa thành 2 vai trò: Admin và Thủ kho kiêm Kế toán.
4. Đồng bộ kết quả sang bản sao trong thư mục docs/ của dự án.
"""

import os
import sys
import shutil
import zipfile
import docx

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIAGRAMS_DIR = os.path.join(BASE_DIR, "docs", "generated_diagrams")
DOWNLOADS_DOC = r"C:\Users\dat17\Downloads\BAO_CAO_DU_AN_QUAN_LY_KHO  (4).docx"
WORKSPACE_DOC = os.path.join(BASE_DIR, "docs", "BAO_CAO_DU_AN_QUAN_LY_KHO  (4).docx")
WORKSPACE_V2_DOC = os.path.join(BASE_DIR, "docs", "BAO_CAO_DU_AN_QUAN_LY_KHO_AI_V2.docx")
BACKUP_DOC = r"C:\Users\dat17\Downloads\BAO_CAO_DU_AN_QUAN_LY_KHO  (4)_BACKUP_PRE_MERGE.docx"

print("=" * 80)
print("   BẮT ĐẦU ĐỒNG BỘ SƠ ĐỒ & CHUẨN HÓA VAI TRÒ 'THỦ KHO KIÊM KẾ TOÁN'")
print("=" * 80)

if not os.path.exists(DOWNLOADS_DOC):
    print(f"[ERROR] Không tìm thấy file nguồn: {DOWNLOADS_DOC}")
    sys.exit(1)

# 1. Sao lưu file
shutil.copy2(DOWNLOADS_DOC, BACKUP_DOC)
print(f"[1/4] Đã sao lưu file gốc sang: {BACKUP_DOC}")

# 2. Thay thế 14 file ảnh trong word/media/
# Danh sách 14 ảnh sơ đồ kỹ thuật
image_names = [f"image{i}.png" for i in range(3, 17)]
print(f"[2/4] Đang thay thế 14 sơ đồ trong word/media/ ({image_names[0]} -> {image_names[-1]})...")

temp_zip_path = DOWNLOADS_DOC + ".temp.zip"

with zipfile.ZipFile(DOWNLOADS_DOC, 'r') as zin:
    with zipfile.ZipFile(temp_zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            filename = item.filename
            # Kiểm tra xem có phải ảnh cần thay không
            base_img = os.path.basename(filename)
            if filename.startswith("word/media/") and base_img in image_names:
                new_img_path = os.path.join(DIAGRAMS_DIR, base_img)
                if os.path.exists(new_img_path):
                    with open(new_img_path, 'rb') as f_new:
                        new_data = f_new.read()
                    zout.writestr(item, new_data)
                    print(f"  [REPLACED] {filename} <- {base_img} ({len(new_data)} bytes)")
                else:
                    print(f"  [WARNING] Không tìm thấy file ảnh mới: {new_img_path}")
                    zout.writestr(item, zin.read(filename))
            else:
                zout.writestr(item, zin.read(filename))

# Ghi đè file zip tạm vào file chính
shutil.move(temp_zip_path, DOWNLOADS_DOC)
print("  -> Đã cập nhật thành công 14 sơ đồ kiến trúc vào file Word!")

# 3. Mở file Word bằng python-docx để cập nhật nội dung văn bản và bảng biểu
print("[3/4] Đang nạp tài liệu để cập nhật văn bản & bảng biểu...")
doc = docx.Document(DOWNLOADS_DOC)

def replace_in_paragraph(p, old_text, new_text):
    if old_text not in p.text:
        return False
    # Kiểm tra từng run
    for r in p.runs:
        if old_text in r.text:
            r.text = r.text.replace(old_text, new_text)
            return True
    # Nếu text trải dài qua nhiều runs
    full_text = p.text.replace(old_text, new_text)
    if p.runs:
        p.runs[0].text = full_text
        for r in p.runs[1:]:
            r.text = ""
    else:
        p.text = full_text
    return True

# Danh mục thay thế đoạn văn bản (Paragraphs)
paragraph_replacements = [
    (
        "phân quyền theo 3 vai trò: Admin, Thủ kho, Kế toán.",
        "phân quyền theo 2 vai trò: Admin, Thủ kho kiêm Kế toán."
    ),
    (
        "Stakeholders: Admin (Quản lý), Thủ kho (Vận hành), Kế toán (Đối soát), Dev Team (Nguyễn Thành Hưng, Hoàng Tiến Đạt).",
        "Stakeholders: Admin (Quản lý), Thủ kho kiêm Kế toán (Vận hành & Đối soát), Dev Team (Nguyễn Thành Hưng, Hoàng Tiến Đạt)."
    ),
    (
        "Actor: Admin, Kế toán.",
        "Actor: Admin, Thủ kho kiêm Kế toán."
    ),
    (
        "Biểu đồ Use Case tổng quát thể hiện sự tương tác giữa 3 Actors (Admin, Thủ kho, Kế toán) với các phân hệ chức năng kho và trợ lý AI.",
        "Biểu đồ Use Case tổng quát thể hiện sự tương tác giữa 2 Actors chính (Admin, Thủ kho kiêm Kế toán) với các phân hệ chức năng kho và Trợ lý AI (Google Gemini 1.5 Flash API)."
    ),
    (
        "sự tương tác của Thủ kho và Quản trị viên đối với các chức năng",
        "sự tương tác của Thủ kho kiêm Kế toán và Quản trị viên đối với các chức năng"
    ),
    (
        "Biểu đồ mô tả sự phối hợp giữa người dùng (Admin, Kế toán, Thủ kho) với các Use Case AI: Sinh báo cáo tháng, gợi ý kế hoạch nhập hàng và phát hiện biến động bất thường.",
        "Biểu đồ mô tả sự phối hợp giữa người dùng (Admin, Thủ kho kiêm Kế toán) với các Use Case AI: Sinh báo cáo chiến lược kho, gợi ý kế hoạch nhập hàng tối ưu và phát hiện biến động bất thường."
    ),
    (
        "Khi Thủ kho nhập thông tin lô hàng từ Nhà cung cấp",
        "Khi Thủ kho kiêm Kế toán nhập thông tin lô hàng từ Nhà cung cấp"
    ),
    (
        "chứa vai trò người dùng (Admin, Thủ kho, Kế toán) để Frontend phân quyền màn hình tương ứng.",
        "chứa vai trò người dùng (Admin, Thủ kho kiêm Kế toán) để Frontend phân quyền màn hình tương ứng."
    ),
    (
        "VaiTro (Admin, Thukho, Ketoan).",
        "VaiTro (Admin, Thukho_Ketoan)."
    ),
    (
        "phân quyền người dùng (Thủ kho, Quản lý)",
        "phân quyền người dùng (Thủ kho kiêm Kế toán, Quản trị viên)"
    ),
    (
        "Ngay khi thủ kho nhập mã mặt hàng và số lượng xuất",
        "Ngay khi Thủ kho kiêm Kế toán nhập mã mặt hàng và số lượng xuất"
    ),
    (
        "ngăn cản thủ kho bấm nút gửi dữ liệu",
        "ngăn cản người dùng bấm nút gửi dữ liệu"
    ),
    (
        "Đối với nghiệp vụ kế toán kho, việc tính toán Báo cáo Nhập-Xuất-Tồn lũy kế",
        "Đối với nghiệp vụ kho và kế toán đối soát, việc tính toán Báo cáo Nhập-Xuất-Tồn lũy kế"
    ),
    (
        "nhiều thủ kho cùng xuất hàng đồng thời",
        "nhiều người dùng (Thủ kho kiêm Kế toán) cùng thao tác xuất hàng đồng thời"
    ),
]

p_count = 0
for p in doc.paragraphs:
    for old_t, new_t in paragraph_replacements:
        if replace_in_paragraph(p, old_t, new_t):
            p_count += 1
            print(f"  [P_UPDATE] Thay thế: '{old_t[:45]}...' -> '{new_t[:45]}...'")

# Cập nhật Bảng (Tables)
t_count = 0
for t_idx, tbl in enumerate(doc.tables):
    for r_idx, row in enumerate(tbl.rows):
        for c_idx, cell in enumerate(row.cells):
            # Bảng 5: User Stories
            if "Admin, Thủ kho, Kế toán" in cell.text:
                for p in cell.paragraphs:
                    replace_in_paragraph(p, "Admin, Thủ kho, Kế toán", "Admin, Thủ kho kiêm Kế toán")
                t_count += 1
                print(f"  [T_UPDATE] Bảng {t_idx} R{r_idx} C{c_idx}: Thay 'Admin, Thủ kho, Kế toán' -> 'Admin, Thủ kho kiêm Kế toán'")
            elif "Admin, Kế toán" in cell.text:
                for p in cell.paragraphs:
                    replace_in_paragraph(p, "Admin, Kế toán", "Admin, Thủ kho kiêm Kế toán")
                t_count += 1
                print(f"  [T_UPDATE] Bảng {t_idx} R{r_idx} C{c_idx}: Thay 'Admin, Kế toán' -> 'Admin, Thủ kho kiêm Kế toán'")
            elif cell.text.strip() == "Thủ kho":
                for p in cell.paragraphs:
                    replace_in_paragraph(p, "Thủ kho", "Thủ kho kiêm Kế toán")
                t_count += 1
                print(f"  [T_UPDATE] Bảng {t_idx} R{r_idx} C{c_idx}: Thay 'Thủ kho' -> 'Thủ kho kiêm Kế toán'")
            elif cell.text.strip() == "Admin, Thủ kho":
                for p in cell.paragraphs:
                    replace_in_paragraph(p, "Admin, Thủ kho", "Admin, Thủ kho kiêm Kế toán")
                t_count += 1
                print(f"  [T_UPDATE] Bảng {t_idx} R{r_idx} C{c_idx}: Thay 'Admin, Thủ kho' -> 'Admin, Thủ kho kiêm Kế toán'")

# Lưu lại file Word
doc.save(DOWNLOADS_DOC)
print(f"  -> Đã lưu {p_count} chỉnh sửa văn bản và {t_count} ô bảng vào {DOWNLOADS_DOC}")

# 4. Sao chép đồng bộ sang thư mục docs của workspace
print(f"[4/4] Đang đồng bộ tài liệu sang workspace docs/...")
shutil.copy2(DOWNLOADS_DOC, WORKSPACE_DOC)
shutil.copy2(DOWNLOADS_DOC, WORKSPACE_V2_DOC)
print(f"  -> Đã copy sang: {WORKSPACE_DOC}")
print(f"  -> Đã copy sang: {WORKSPACE_V2_DOC}")

print("=" * 80)
print("   HOÀN THÀNH ĐỒNG BỘ 100% FILE BÁO CÁO VỚI SƠ ĐỒ VÀ VAI TRÒ MỚI!")
print("=" * 80)
