# scripts/cleanup_and_keep_single_word.py
"""
Script Xóa Sạch Các File Word Cũ Và Giữ Lại Duy Nhất 1 File Hoàn Chỉnh:
Tên file duy nhất: HTD_NTH_KTPMK23A.docx
(Hoàng Tiến Đạt - Nguyễn Thành Hưng - KTPMK23A)
"""

import os
import sys
import shutil
import zipfile
import docx

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

MASTER_SOURCE = r"d:\antigravity_file\smartlogis-ai\docs\BAO_CAO_DU_AN_QUAN_LY_KHO  (4).docx"
TARGET_DOCX_NAME = "HTD_NTH_KTPMK23A.docx"

TARGET_DOWNLOADS = os.path.join(r"C:\Users\dat17\Downloads", TARGET_DOCX_NAME)
TARGET_WORKSPACE = os.path.join(r"d:\antigravity_file\smartlogis-ai\docs", TARGET_DOCX_NAME)

print("=" * 80)
print(f"   TIẾN HÀNH SAO LƯU THÀNH FILE DUY NHẤT: {TARGET_DOCX_NAME}")
print("=" * 80)

# 1. Kiểm tra tính toàn vẹn của Master file trước khi thực hiện
if not os.path.exists(MASTER_SOURCE):
    print(f"[ERROR] Không tìm thấy file nguồn hoàn chỉnh: {MASTER_SOURCE}")
    sys.exit(1)

src_size = os.path.getsize(MASTER_SOURCE)
print(f"[+] File nguồn hoàn chỉnh: {MASTER_SOURCE} ({src_size} bytes)")

doc_test = docx.Document(MASTER_SOURCE)
print(f"[+] Kiểm tra tính toàn vẹn: {len(doc_test.paragraphs)} đoạn văn, {len(doc_test.tables)} bảng.")

with zipfile.ZipFile(MASTER_SOURCE, 'r') as z:
    media_count = len([f for f in z.namelist() if f.startswith('word/media/')])
print(f"[+] Số lượng ảnh media nhúng trong file: {media_count} ảnh.")

# 2. Tạo file duy nhất HTD_NTH_KTPMK23A.docx ở cả 2 vị trí (Downloads và Workspace docs)
shutil.copy2(MASTER_SOURCE, TARGET_DOWNLOADS)
shutil.copy2(MASTER_SOURCE, TARGET_WORKSPACE)
print(f"\n[OK] Đã tạo file nguyên vẹn hoàn chỉnh tại Downloads: {TARGET_DOWNLOADS}")
print(f"[OK] Đã tạo file nguyên vẹn hoàn chỉnh tại Workspace: {TARGET_WORKSPACE}")

# Xác minh 2 file đích
assert os.path.exists(TARGET_DOWNLOADS) and os.path.getsize(TARGET_DOWNLOADS) == src_size
assert os.path.exists(TARGET_WORKSPACE) and os.path.getsize(TARGET_WORKSPACE) == src_size
print("[OK] Xác minh 2 file đích hoàn toàn khớp 100% về kích thước và dữ liệu.")

# 3. Danh sách các file Word cũ cần xóa bỏ
files_to_delete = [
    # Thư mục Downloads
    r"C:\Users\dat17\Downloads\BAO_CAO_DU_AN_QUAN_LY_KHO  (4).docx",
    r"C:\Users\dat17\Downloads\BAO_CAO_DU_AN_QUAN_LY_KHO  (4)_backup_original.docx",
    r"C:\Users\dat17\Downloads\BAO_CAO_DU_AN_QUAN_LY_KHO  (4)_BACKUP_PRE_MERGE.docx",
    
    # Thư mục OneDrive Documents
    r"C:\Users\dat17\OneDrive\Documents\BAO_CAO_DU_AN_QUAN_LY_KHO  (4).docx",
    
    # Thư mục docs của dự án
    r"d:\antigravity_file\smartlogis-ai\docs\BAO_CAO_DU_AN_QUAN_LY_KHO  (4).docx",
    r"d:\antigravity_file\smartlogis-ai\docs\BAO_CAO_DU_AN_QUAN_LY_KHO_AI_V2.docx",
    r"d:\antigravity_file\smartlogis-ai\docs\backup_BAO_CAO_DU_AN_QUAN_LY_KHO_original.docx",
    r"d:\antigravity_file\smartlogis-ai\docs\ai_log.docx",
    r"d:\antigravity_file\smartlogis-ai\docs\database_design.docx",
    r"d:\antigravity_file\smartlogis-ai\docs\README.docx",
    r"d:\antigravity_file\smartlogis-ai\docs\requirements.docx",
    r"d:\antigravity_file\smartlogis-ai\docs\TONG_HOP_TOAN_BO_TAI_LIEU_DU_AN.docx",
    r"d:\antigravity_file\smartlogis-ai\docs\use_cases.docx",
]

print("\n" + "=" * 80)
print("   BẮT ĐẦU XÓA TẤT CẢ CÁC FILE WORD DỰ ÁN CŨ")
print("=" * 80)

deleted_count = 0
for fpath in files_to_delete:
    if os.path.exists(fpath):
        try:
            os.remove(fpath)
            deleted_count += 1
            print(f"  [DELETED] {fpath}")
        except Exception as e:
            print(f"  [ERROR] Không thể xóa {fpath}: {e}")
    else:
        print(f"  [SKIP - NOT FOUND] {fpath}")

print(f"\n-> Đã xóa thành công {deleted_count} file Word cũ.")

# 4. Kiểm tra lại thư mục
print("\n" + "=" * 80)
print("   KIỂM TRA CÁC FILE WORD CÒN LẠI SAU KHI DỌN DẸP")
print("=" * 80)

print("\n--- THƯ MỤC docs/: ---")
for f in os.listdir(r"d:\antigravity_file\smartlogis-ai\docs"):
    if f.endswith(".docx"):
        p = os.path.join(r"d:\antigravity_file\smartlogis-ai\docs", f)
        print(f"  * {f} ({os.path.getsize(p)} bytes)")

print("\n--- THƯ MỤC Downloads (liên quan đến đồ án): ---")
for f in os.listdir(r"C:\Users\dat17\Downloads"):
    if ("HTD" in f or "BAO_CAO" in f) and f.endswith(".docx"):
        p = os.path.join(r"C:\Users\dat17\Downloads", f)
        print(f"  * {f} ({os.path.getsize(p)} bytes)")

print("\n" + "=" * 80)
print(f"   HOÀN TẤT: DUY NHẤT 1 FILE WORD NGUYÊN VẸN LÀ '{TARGET_DOCX_NAME}'!")
print("=" * 80)
