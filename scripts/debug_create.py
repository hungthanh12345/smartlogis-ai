import urllib.request
import urllib.error
import json
import sys
from pathlib import Path

root_dir = str(Path(__file__).resolve().parent.parent)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

sys.stdout.reconfigure(encoding='utf-8')

try:
    login_url = "http://127.0.0.1:8000/api/v1/auth/login"
    login_payload = json.dumps({"TenDangNhap": "admin", "MatKhau": "admin123"}).encode('utf-8')
    req = urllib.request.Request(login_url, data=login_payload, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as res:
        auth_data = json.loads(res.read().decode('utf-8'))
        token = auth_data["access_token"]

    item_payload = json.dumps({
        "MaHH": "HH-TEST-01",
        "TenHH": "Xi Măng Nghi Sơn PCB40 Thử Nghiệm",
        "MaNhom": "NH-XIMANG",
        "MaDVT": "BAO",
        "TonToiThieu": 25,
        "SoLuongBanDau": 50,
        "MoTa": "Sản phẩm thử nghiệm kiểm thử tự động CRUD"
    }).encode('utf-8')

    req = urllib.request.Request(
        "http://127.0.0.1:8000/api/v1/kho/items", 
        data=item_payload, 
        headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {token}"},
        method='POST'
    )
    with urllib.request.urlopen(req) as res:
        print("Response:", res.read().decode('utf-8'))

except urllib.error.HTTPError as he:
    print("HTTP Error:", he.code, he.read().decode('utf-8'))
