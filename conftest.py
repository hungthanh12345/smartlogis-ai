# conftest.py - Pytest Root Configuration
import os
import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent
backend_dir = root_dir / "backend"

for p in [backend_dir, root_dir]:
    p_str = str(p)
    if p_str not in sys.path:
        sys.path.insert(0, p_str)

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

