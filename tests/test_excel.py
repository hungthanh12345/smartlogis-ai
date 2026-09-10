import time
import sys
from pathlib import Path

root_dir = str(Path(__file__).resolve().parent.parent)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app.core.database import SessionLocal
from app.services.inventory_service import generate_excel_inventory_report

db = SessionLocal()
t0 = time.time()
stream = generate_excel_inventory_report(db)
print(f"[EXCEL TEST OK] Generated in {time.time() - t0:.3f}s | Bytes: {len(stream.getvalue())}")
