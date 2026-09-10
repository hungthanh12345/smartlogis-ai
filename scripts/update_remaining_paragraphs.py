import docx
import shutil
import sys
import os

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

DOC_PATH = r"C:\Users\dat17\Downloads\BAO_CAO_DU_AN_QUAN_LY_KHO  (4).docx"
WORKSPACE_DOC = r"d:\antigravity_file\smartlogis-ai\docs\BAO_CAO_DU_AN_QUAN_LY_KHO  (4).docx"
WORKSPACE_V2_DOC = r"d:\antigravity_file\smartlogis-ai\docs\BAO_CAO_DU_AN_QUAN_LY_KHO_AI_V2.docx"

doc = docx.Document(DOC_PATH)

def replace_in_paragraph(p, old_text, new_text):
    if old_text not in p.text:
        return False
    for r in p.runs:
        if old_text in r.text:
            r.text = r.text.replace(old_text, new_text)
            return True
    full_text = p.text.replace(old_text, new_text)
    if p.runs:
        p.runs[0].text = full_text
        for r in p.runs[1:]:
            r.text = ""
    else:
        p.text = full_text
    return True

additional_replacements = [
    ("P[165]", "Actor: Thủ kho.", "Actor: Thủ kho kiêm Kế toán."),
    ("P[167]", "Thủ kho chọn \"Lập Phiếu Xuất Kho\", chọn danh sách hàng và số lượng xuất.", "Thủ kho kiêm Kế toán chọn \"Lập Phiếu Xuất Kho\", chọn danh sách hàng và số lượng xuất."),
    ("P[181]", "Biểu đồ Use Case tổng quát thể hiện sự tương tác giữa 3 Actors (Admin, Thủ kho, Kế toán) với các phân hệ chức năng kho và AI.", "Biểu đồ Use Case tổng quát thể hiện sự tương tác giữa 2 Actors chính (Admin, Thủ kho kiêm Kế toán) với các phân hệ chức năng kho và Trợ lý AI (Google Gemini 1.5 Flash API)."),
    ("P[245]", "tối ưu hóa không gian làm việc của thủ kho", "tối ưu hóa không gian làm việc của Thủ kho kiêm Kế toán"),
    ("P[250]", "thao tác bàn phím của thủ kho", "thao tác bàn phím của Thủ kho kiêm Kế toán"),
    ("P[266]", "thông tin thủ kho đăng nhập", "thông tin Thủ kho kiêm Kế toán đăng nhập"),
    ("P[267]", "ngay khi thủ kho rời con trỏ chuột", "ngay khi Thủ kho kiêm Kế toán rời con trỏ chuột"),
    ("P[277]", "ngăn cản thủ kho gửi request", "ngăn cản người dùng (Thủ kho kiêm Kế toán) gửi request"),
    ("P[311]", "nhiều thủ kho cùng xuất hàng", "nhiều người dùng (Thủ kho kiêm Kế toán) cùng xuất hàng"),
]

count = 0
for p in doc.paragraphs:
    for tag, old_t, new_t in additional_replacements:
        if replace_in_paragraph(p, old_t, new_t):
            count += 1
            print(f"[{tag}] Successfully replaced: '{old_t}' -> '{new_t}'")

doc.save(DOC_PATH)
shutil.copy2(DOC_PATH, WORKSPACE_DOC)
shutil.copy2(DOC_PATH, WORKSPACE_V2_DOC)
print(f"Updated {count} remaining paragraphs and synced files successfully!")
