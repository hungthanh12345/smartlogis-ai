# conftest.py - Pytest Root Configuration
import os
import sys
from pathlib import Path

# Thêm backend và root directory vào sys.path
backend_dir = Path(__file__).resolve().parent.parent
root_dir = backend_dir.parent

for p in [backend_dir, root_dir]:
    p_str = str(p)
    if p_str not in sys.path:
        sys.path.insert(0, p_str)

# Thiết lập encoding UTF-8 cho stdout trên Windows
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

