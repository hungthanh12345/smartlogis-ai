import docx
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

file_path = r"C:\Users\dat17\Downloads\BAO_CAO_DU_AN_QUAN_LY_KHO  (4).docx"
doc = docx.Document(file_path)

print("--- ALL OCCURRENCES OF 'thủ kho' ---")
for i, p in enumerate(doc.paragraphs):
    if "thủ kho" in p.text.lower():
        print(f"P[{i}]: {p.text.strip()}")
