import sys
import os
from pathlib import Path
import uvicorn

# Đảm bảo root directory luôn nằm trong sys.path và là working directory
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))
os.chdir(root_dir)

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

if __name__ == "__main__":
    print("Khoi chay may chu SmartLogis AI...")
    print(" - Local:   http://127.0.0.1:8000")
    print(" - LAN IP:  http://172.172.5.168:8000")
    print(" - Swagger: http://127.0.0.1:8000/docs")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
