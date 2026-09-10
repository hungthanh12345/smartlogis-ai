"""
sync_word_report.py
===================
Đồng bộ hóa file Word BAO_CAO_DU_AN_QUAN_LY_KHO (4).docx với:
1. Thay thế 10 hình ảnh sơ đồ trong word/media/
2. Sửa văn bản "3 vai trò / Thủ kho, Kế toán" → "2 vai trò / Thủ kho kiêm Kế toán"
3. Cập nhật Bảng 5 (User Story/Use Case) và Bảng 15 (Test Case)
4. Sync kết quả sang BAO_CAO_DU_AN_QUAN_LY_KHO_AI_V2.docx
"""

import sys
import shutil
import zipfile
import os
import re
import docx
from docx.oxml.ns import qn
from copy import deepcopy
import lxml.etree as etree

sys.stdout.reconfigure(encoding='utf-8')

# ─────────────────────────────────────────────
# PATHS
# ─────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIAGRAMS_DIR = os.path.join(BASE_DIR, "docs", "generated_diagrams")

MAIN_DOC_PATH = r"C:\Users\dat17\OneDrive\Documents\BAO_CAO_DU_AN_QUAN_LY_KHO  (4).docx"
AI_V2_DOC_PATH = os.path.join(BASE_DIR, "docs", "BAO_CAO_DU_AN_QUAN_LY_KHO_AI_V2.docx")
BACKUP_PATH = os.path.join(BASE_DIR, "docs", "backup_BAO_CAO_DU_AN_QUAN_LY_KHO_original.docx")

# Map: tên file ảnh trong word/media/ → file PNG mới từ generated_diagrams/
# Sẽ được xác định tự động bằng cách quét zip
IMAGE_REPLACEMENT_MAP = {
    # Thứ tự xuất hiện trong docs → ảnh tương ứng
    # image3.png: Hình 2.2.3 Kiến trúc phân hệ
    # image4.png: Hình 4.1 Use Case tổng quát
    # image5.png: Hình 4.1.1 Use Case phân hệ nghiệp vụ
    # image6.png: Hình 4.1.2 Use Case AI
    # image7.png: Hình 4.2.1 Trình tự xuất kho
    # image9.png: Hình 4.2.3 Trình tự nhập kho
    # image11.png: Hình 4.2.5 Trình tự xuất Excel
    # image12.png: Hình 4.2.6 Trình tự đăng nhập JWT
    # image13.png: Hình 4.3.2 ERD
    # image16.png: Hình 4.5.1 Class Diagram
    "image3.png": "image3.png",
    "image4.png": "image4.png",
    "image5.png": "image5.png",
    "image6.png": "image6.png",
    "image7.png": "image7.png",
    "image9.png": "image9.png",
    "image11.png": "image11.png",
    "image12.png": "image12.png",
    "image13.png": "image13.png",
    "image16.png": "image16.png",
}

# ─────────────────────────────────────────────
# TEXT REPLACEMENTS (paragraph level)
# ─────────────────────────────────────────────
TEXT_REPLACEMENTS = [
    # Thay "3 vai trò: Admin, Thủ kho, Kế toán" → "2 vai trò: Admin, Thủ kho kiêm Kế toán"
    (
        "phân quyền theo 3 vai trò: Admin, Thủ kho, Kế toán",
        "phân quyền theo 2 vai trò: Admin, Thủ kho kiêm Kế toán"
    ),
    # P[158] Stakeholders
    (
        "Stakeholders: Admin (Quản lý), Thủ kho (Vận hành), Kế toán (Đối soát), Dev Team (Nguyễn Thành Hưng, Hoàng Tiến Đạt).",
        "Stakeholders: Admin (Quản lý), Thủ kho kiêm Kế toán (Vận hành & Đối soát), Dev Team (Nguyễn Thành Hưng, Hoàng Tiến Đạt)."
    ),
    # P[171] Actor kế toán
    (
        "Actor: Admin, Kế toán.",
        "Actor: Admin, Thủ kho kiêm Kế toán."
    ),
    # P[180] Biểu đồ use case tổng quát 3 Actors
    (
        "3 Actors (Admin, Thủ kho, Kế toán)",
        "2 Actors (Admin, Thủ kho kiêm Kế toán)"
    ),
    # P[183] Biểu đồ phân hệ nghiệp vụ kho
    (
        "sự tương tác của Thủ kho và Quản trị viên",
        "sự tương tác của Thủ kho kiêm Kế toán và Quản trị viên"
    ),
    # P[187] Biểu đồ AI 3 vai trò
    (
        "người dùng (Admin, Kế toán, Thủ kho)",
        "người dùng (Admin, Thủ kho kiêm Kế toán)"
    ),
    # P[212] JWT chứa vai trò
    (
        "vai trò người dùng (Admin, Thủ kho, Kế toán)",
        "vai trò người dùng (Admin, Thủ kho kiêm Kế toán)"
    ),
    # P[217] NguoiDung VaiTro field
    (
        "VaiTro (Admin, Thukho, Ketoan)",
        "VaiTro (Admin, Thukho [= Thủ kho kiêm Kế toán])"
    ),
    # Bất kỳ đề cập chung nào
    (
        "Admin, Thủ kho, Kế toán",
        "Admin, Thủ kho kiêm Kế toán"
    ),
    (
        "Admin, Kế toán",
        "Admin, Thủ kho kiêm Kế toán"
    ),
]

# ─────────────────────────────────────────────
# TABLE CELL REPLACEMENTS
# ─────────────────────────────────────────────
# Bảng 5: User Story / Actor
TABLE5_ACTOR_MAP = {
    "Admin, Thủ kho, Kế toán": "Admin, Thủ kho kiêm Kế toán",
    "Admin, Kế toán":           "Admin, Thủ kho kiêm Kế toán",
    "Thủ kho":                  "Thủ kho kiêm Kế toán",
    "Admin, Thủ kho":           "Admin, Thủ kho kiêm Kế toán",
}

# Bảng 15: Test Case descriptions
TABLE15_TEXT_MAP = {
    "Admin, Thủ kho, Kế toán": "Admin, Thủ kho kiêm Kế toán",
    "Admin, Kế toán":           "Admin, Thủ kho kiêm Kế toán",
}


# ─────────────────────────────────────────────
# STEP 1: Replace images in zip
# ─────────────────────────────────────────────
def replace_images_in_docx(docx_path: str, replacement_map: dict) -> str:
    """
    Mở file .docx dưới dạng zip, thay thế từng file ảnh trong word/media/,
    lưu ra file mới (thêm hậu tố _synced).
    Trả về đường dẫn file đã được cập nhật ảnh.
    """
    out_path = docx_path.replace(".docx", "_synced.docx")
    
    with zipfile.ZipFile(docx_path, 'r') as zin:
        with zipfile.ZipFile(out_path, 'w', compression=zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                # Xác định tên file media (vd: word/media/image3.png)
                basename = os.path.basename(item.filename)
                if item.filename.startswith("word/media/") and basename in replacement_map:
                    new_img_filename = replacement_map[basename]
                    new_img_path = os.path.join(DIAGRAMS_DIR, new_img_filename)
                    if os.path.exists(new_img_path):
                        print(f"  ✅ Replacing {item.filename} ← {new_img_filename}")
                        with open(new_img_path, 'rb') as f:
                            zout.writestr(item, f.read())
                    else:
                        print(f"  ⚠️  Source image not found: {new_img_path}, keeping original")
                        zout.writestr(item, zin.read(item.filename))
                else:
                    zout.writestr(item, zin.read(item.filename))
    
    print(f"  → Image-replaced docx saved: {out_path}")
    return out_path


# ─────────────────────────────────────────────
# STEP 2: Replace text in paragraphs
# ─────────────────────────────────────────────
def replace_text_in_paragraph(paragraph, old_text: str, new_text: str) -> bool:
    """
    Thay thế text trong paragraph, giữ nguyên formatting.
    Trả về True nếu có thay đổi.
    """
    full_text = paragraph.text
    if old_text not in full_text:
        return False
    
    # Ghép tất cả runs lại, thay text, rồi ghi vào run đầu tiên
    for i, run in enumerate(paragraph.runs):
        if i == 0:
            combined = full_text.replace(old_text, new_text)
            run.text = combined
        else:
            run.text = ""
    return True


def apply_text_replacements(doc: docx.Document) -> int:
    """Áp dụng tất cả text replacement vào paragraphs. Trả về số lần thay thế."""
    count = 0
    for i, para in enumerate(doc.paragraphs):
        for old, new in TEXT_REPLACEMENTS:
            if old in para.text:
                if replace_text_in_paragraph(para, old, new):
                    print(f"  ✅ P[{i}]: '{old[:50]}...' → '{new[:50]}...'")
                    count += 1
    return count


# ─────────────────────────────────────────────
# STEP 3: Update tables
# ─────────────────────────────────────────────
def update_table_cells(doc: docx.Document, table_idx: int, cell_map: dict) -> int:
    """Cập nhật nội dung các cell trong bảng theo cell_map."""
    count = 0
    tbl = doc.tables[table_idx]
    for r_idx, row in enumerate(tbl.rows):
        for c_idx, cell in enumerate(row.cells):
            cell_text = cell.text.strip()
            for old, new in cell_map.items():
                if old in cell_text:
                    # Thay text trực tiếp trong các paragraphs của cell
                    for para in cell.paragraphs:
                        if old in para.text:
                            for run in para.runs:
                                if old in run.text:
                                    run.text = run.text.replace(old, new)
                    print(f"  ✅ Table[{table_idx}][R{r_idx}][C{c_idx}]: '{old}' → '{new}'")
                    count += 1
    return count


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main():
    print("=" * 60)
    print("SYNC WORD REPORT - SmartLogis AI v2.0")
    print("=" * 60)

    # Kiểm tra file gốc
    if not os.path.exists(MAIN_DOC_PATH):
        print(f"❌ Main document not found: {MAIN_DOC_PATH}")
        return

    print(f"\n[1/5] Replacing images in docx...")
    synced_path = replace_images_in_docx(MAIN_DOC_PATH, IMAGE_REPLACEMENT_MAP)

    print(f"\n[2/5] Loading synced docx for text editing...")
    doc = docx.Document(synced_path)

    print(f"\n[3/5] Replacing text in paragraphs...")
    para_count = apply_text_replacements(doc)
    print(f"  → {para_count} paragraph replacements made")

    print(f"\n[4/5] Updating tables...")
    # Table 5: User Story (index 5)
    t5_count = update_table_cells(doc, 5, TABLE5_ACTOR_MAP)
    # Table 15: Test Case (index 15)
    t15_count = update_table_cells(doc, 15, TABLE15_TEXT_MAP)
    print(f"  → Table 5: {t5_count} cells updated | Table 15: {t15_count} cells updated")

    print(f"\n[5/5] Saving final documents...")
    # Lưu đè lên main doc
    doc.save(MAIN_DOC_PATH)
    print(f"  ✅ Main doc updated: {MAIN_DOC_PATH}")

    # Đồng bộ sang AI_V2
    doc.save(AI_V2_DOC_PATH)
    print(f"  ✅ AI_V2 doc updated: {AI_V2_DOC_PATH}")

    # Xóa file tạm
    if os.path.exists(synced_path):
        os.remove(synced_path)
        print(f"  🗑️  Temp file removed: {synced_path}")

    print("\n" + "=" * 60)
    print("✅ SYNC COMPLETE!")
    print(f"   - Paragraph replacements : {para_count}")
    print(f"   - Table 5 cells updated  : {t5_count}")
    print(f"   - Table 15 cells updated : {t15_count}")
    print(f"   - Images replaced        : {len(IMAGE_REPLACEMENT_MAP)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
