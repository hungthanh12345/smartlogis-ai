# tests/test_endpoints.py
import sys
from pathlib import Path
from fastapi.testclient import TestClient

root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from main import app

def test_endpoints_suite():
    client = TestClient(app)

    # 1. Login lấy token
    login_res = client.post("/api/v1/auth/login", json={"TenDangNhap": "admin", "MatKhau": "admin123"})
    assert login_res.status_code == 200, f"Login failed: {login_res.text}"
    token = login_res.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    client.cookies.set("access_token", token)

    endpoints = [
        ("Dashboard", "/dashboard", 200),
        ("Hang Hoa Page", "/hang-hoa", 200),
        ("Nha Cung Cap Page", "/nha-cung-cap", 200),
        ("Inbound Page", "/inbound", 200),
        ("API Items", "/api/v1/kho/items", 200),
        ("API Suppliers", "/api/v1/kho/suppliers", 200),
        ("API Supplier KPIs", "/api/v1/kho/suppliers/summary/kpis", 200),
        ("API Supplier Detail", "/api/v1/kho/suppliers/NCC-01", 200),
        ("API Excel Inventory Export", "/api/v1/reports/export/excel", 200),
        ("API Excel Suppliers Export", "/api/v1/reports/export/suppliers-excel", 200)
    ]

    for name, path, expected_status in endpoints:
        res = client.get(path, headers=headers)
        assert res.status_code == expected_status, f"Endpoint {name} ({path}) failed with status {res.status_code}: {res.text}"
        print(f"[SUCCESS] {name} -> Status: {res.status_code} | Bytes: {len(res.content)}")

if __name__ == "__main__":
    test_endpoints_suite()
