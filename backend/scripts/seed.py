# scripts/seed.py
"""
Script seed dữ liệu ban đầu cho SmartLogis AI (Entrypoint tương thích ngược).
Gọi trực tiếp logic chuẩn từ scripts/seed_data.py.
"""

import sys
from pathlib import Path

root_dir = str(Path(__file__).resolve().parent.parent)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from scripts.seed_data import reset_and_seed_database


def seed_database():
    """Hàm seed mặc định được gọi tự động khi khởi động main.py."""
    reset_and_seed_database(force_reset=False)


if __name__ == "__main__":
    force = "--reset" in sys.argv
    reset_and_seed_database(force_reset=force)
