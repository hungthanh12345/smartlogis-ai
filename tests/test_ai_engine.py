# tests/test_ai_engine.py
"""
Bộ Kiểm Thử Tự Động AI Engine & Prompt Engineering (Giai đoạn 3 - SmartLogis AI)
Bao gồm:
- Test 1: Tổng hợp dữ liệu kho trống (Zero Data) -> AI trả về thông báo chưa có dữ liệu giao dịch.
- Test 2: Mặt hàng dưới tồn tối thiểu -> AI đề xuất chính xác mã hàng, số lượng và BẢO ĐẢM KHÔNG LỘ GIÁ NHẬP.
- Test 3: Mocking Gemini API Call -> Kiểm tra tốc độ, định dạng JSON/Markdown và cơ chế Fallback khi gặp lỗi (429/Timeout).
- Test 4: Integration Test các API Endpoints (/api/v1/ai/generate-report, /api/v1/ai/advisory, /api/v1/ai/raw-context).
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from main import app
from app.core.database import Base
from app.models.inventory_models import (
    HangHoa, TonKho, NhomHang, DonViTinh, PhieuXuat, ChiTietPhieuXuat, NguoiDung
)
from app.services.ai_data_service import (
    aggregate_warehouse_data_30d,
    sanitize_inventory_payload
)
from app.services.gemini_service import GeminiService
from app.prompts.inventory_prompts import (
    SYSTEM_PROMPT_ANTI_HALLUCINATION,
    build_inventory_user_prompt
)


@pytest.fixture(scope="function")
def in_memory_db():
    """Tạo CSDL SQLite in-memory biệt lập cho từng bài test."""
    engine = create_engine("sqlite:///:memory:")
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    session = TestingSession()
    
    # Tạo danh mục cơ sở
    nhom = NhomHang(MaNhom="NH-TEST", TenNhom="Nhóm Thử Nghiệm", MoTa="Test category")
    dvt = DonViTinh(MaDVT="CAI", TenDVT="Cái")
    session.add_all([nhom, dvt])
    session.commit()
    
    yield session
    
    session.close()
    Base.metadata.drop_all(bind=engine)


# =============================================================================
# TEST 1: DỮ LIỆU KHO RỖNG (ZERO DATA RULE)
# =============================================================================
def test_ai_data_empty_inventory(in_memory_db):
    """
    Test 1: Truy vấn tổng hợp dữ liệu kho trống -> AI trả về thông báo chưa có dữ liệu giao dịch hợp lệ,
    chống ảo giác tuyệt đối (không bịa đặt số liệu).
    """
    # CSDL in-memory vừa tạo hoàn toàn chưa có SKU hàng hóa nào
    data = aggregate_warehouse_data_30d(in_memory_db)
    
    assert data["metadata"]["is_empty"] is True
    assert data["metadata"]["total_skus"] == 0
    assert len(data["inventory_summary"]) == 0
    assert len(data["low_stock_alerts"]) == 0

    # Kiểm tra User Prompt xây dựng cho kho rỗng
    user_prompt = build_inventory_user_prompt(data)
    assert "chưa có dữ liệu giao dịch hợp lệ" in user_prompt.lower() or "rỗng" in user_prompt.lower()

    # Kiểm tra GeminiService phản hồi đúng quy chuẩn khi nhận kho rỗng
    service = GeminiService(api_key="mock-key-1234567890")
    report = service.generate_inventory_report(data)

    assert report["is_fallback"] is True
    assert "chưa ghi nhận dữ liệu giao dịch hợp lệ" in report["phan_1_tong_quan"]["danh_gia_chung"].lower()
    assert len(report["phan_2_canh_bao_va_de_xuat_nhap"]) == 0
    assert "chưa có dữ liệu" in report["insights_widget"][0]["title"].lower()


# =============================================================================
# TEST 2: ĐỀ XUẤT NHẬP HÀNG KHI DƯỚI TỒN MIN & KHỬ GIÁ NHẬP BẢO MẬT
# =============================================================================
def test_ai_under_min_stock_recommendation(in_memory_db):
    """
    Test 2: Dữ liệu có sản phẩm dưới tồn tối thiểu -> AI đề xuất chính xác mã hàng, số lượng
    và BẮT BUỘC loại bỏ hoàn toàn thông tin giá nhập (DonGiaNhap, import_price).
    """
    now = datetime.now()
    
    # Tạo SKU 1: Thiếu hụt nghiêm trọng (Tồn 10, Tồn min 50)
    hh1 = HangHoa(MaHH="SKU-AI-LOW-01", TenHH="Thép Vằn D20 Hòa Phát", MaNhom="NH-TEST", MaDVT="CAI", TonToiThieu=50)
    tk1 = TonKho(MaHH="SKU-AI-LOW-01", SoLuongTon=10)
    
    # Tạo SKU 2: Tồn đọng không xuất (Dead Stock: Tồn 80, Tồn min 20)
    hh2 = HangHoa(MaHH="SKU-AI-DEAD-02", TenHH="Sơn Chống Gỉ Alkyd Cũ", MaNhom="NH-TEST", MaDVT="CAI", TonToiThieu=20)
    tk2 = TonKho(MaHH="SKU-AI-DEAD-02", SoLuongTon=80)

    # Tạo User để tạo phiếu xuất
    user = NguoiDung(TenDangNhap="test_user", MatKhau="secret", HoTen="Tester", VaiTro="Thukho")
    in_memory_db.add_all([hh1, tk1, hh2, tk2, user])
    in_memory_db.commit()

    # Giả lập phiếu xuất cho SKU 1 trong 30 ngày qua (Tổng xuất 60 cái -> Burn rate = 2.0 cái/ngày)
    px = PhieuXuat(
        MaPX="PX-AI-TEST-01",
        NgayXuat=now - timedelta(days=5),
        MaND=user.MaND,
        NguoiNhan="Đội Thi Công Công Trình",
        LyDoXuat="Xuất vật tư sản xuất"
    )
    in_memory_db.add(px)
    in_memory_db.commit()
    
    ctpx = ChiTietPhieuXuat(MaPX="PX-AI-TEST-01", MaHH="SKU-AI-LOW-01", SoLuongXuat=60)
    in_memory_db.add(ctpx)
    in_memory_db.commit()

    # Tổng hợp dữ liệu kho 30 ngày
    data = aggregate_warehouse_data_30d(in_memory_db, reference_date=now)

    # 1. Kiểm định tính toán nghiệp vụ
    assert data["metadata"]["total_skus"] == 2
    assert len(data["low_stock_alerts"]) == 1
    
    alert = data["low_stock_alerts"][0]
    assert alert["ma_hh"] == "SKU-AI-LOW-01"
    assert alert["ton_hien_tai"] == 10
    assert alert["ton_toi_thieu"] == 50
    assert alert["thieu_hut"] == 40
    assert alert["burn_rate_ngay"] == 2.0
    # Đề xuất nhập = 40 (thiếu) + (2.0 * 15 ngày) = 70 đơn vị
    assert alert["de_xuat_nhap_them"] == 70
    assert alert["muc_do_nguy_cap"] == "KHAN_CAP"

    # SKU 2 phải rơi vào danh sách dead stock (> 60 ngày không xuất hoặc chưa từng xuất)
    assert len(data["dead_stock_items"]) == 1
    assert data["dead_stock_items"][0]["ma_hh"] == "SKU-AI-DEAD-02"

    # 2. KIỂM ĐỊNH BẢO MẬT: Khử hoàn toàn giá nhập
    json_str = json.dumps(data)
    assert "DonGiaNhap" not in json_str
    assert "don_gia_nhap" not in json_str
    assert "import_price" not in json_str
    assert "ThanhTien" not in json_str
    assert "GiaVon" not in json_str
    assert "gia_von" not in json_str

    # 3. Kiểm định Fallback Engine sinh đề xuất nhập chính xác
    service = GeminiService(api_key="")  # Không có key -> Chạy Fallback Engine
    report = service.generate_inventory_report(data)
    
    recommendations = report["phan_2_canh_bao_va_de_xuat_nhap"]
    assert len(recommendations) == 1
    assert recommendations[0]["ma_hh"] == "SKU-AI-LOW-01"
    assert recommendations[0]["so_luong_de_xuat_nhap"] == 70
    assert "SKU-AI-DEAD-02" in str(report["phan_3_bien_dong_bat_thuong"])


# =============================================================================
# TEST 3: TEST MOCKING GEMINI API CALL (TỐC ĐỘ, FORMAT, RETRY & FALLBACK)
# =============================================================================
def test_mocking_gemini_api_call():
    """
    Test 3: Mocking Gemini API call:
    - Kịch bản 3a: Gemini phản hồi thành công JSON 3 phần -> parser bóc tách chính xác.
    - Kịch bản 3b: Gemini API gặp mã 429 Quota Exceeded / Timeout -> Tự động Fallback sang Local Engine an toàn.
    """
    mock_warehouse_data = {
        "metadata": {"total_skus": 10, "is_empty": False},
        "low_stock_alerts": [
            {
                "ma_hh": "SKU-MOCK-01",
                "ten_hh": "Dây Cáp Điện Cadivi",
                "don_vi_tinh": "CUON",
                "ton_hien_tai": 5,
                "ton_toi_thieu": 20,
                "thieu_hut": 15,
                "burn_rate_ngay": 1.0,
                "de_xuat_nhap_them": 30,
                "muc_do_nguy_cap": "KHAN_CAP"
            }
        ],
        "dead_stock_items": [
            {
                "ma_hh": "SKU-MOCK-02",
                "ten_hh": "Bulong Inox Cũ",
                "ton_kho_u_dong": 100,
                "so_ngay_khong_xuat": 75
            }
        ],
        "high_burn_rate_items": []
    }

    # 3a. Mock Response Gemini thành công
    gemini_json_response = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": json.dumps({
                                "phan_1_tong_quan": {
                                    "tong_so_sku": 10,
                                    "so_sku_canh_bao_ton_min": 1,
                                    "so_sku_u_dong_60_ngay": 1,
                                    "danh_gia_chung": "Kho vận hành tương đối ổn định, cần bổ sung SKU thiếu hụt."
                                },
                                "phan_2_canh_bao_va_de_xuat_nhap": [
                                    {
                                        "ma_hh": "SKU-MOCK-01",
                                        "ten_hh": "Dây Cáp Điện Cadivi",
                                        "ton_hien_tai": 5,
                                        "ton_toi_thieu": 20,
                                        "thieu_hut": 15,
                                        "burn_rate_ngay": 1.0,
                                        "so_luong_de_xuat_nhap": 30,
                                        "muc_do": "KHAN_CAP",
                                        "ly_do": "Tồn kho chỉ còn 5 cuộn, tiêu thụ 1 cuộn/ngày."
                                    }
                                ],
                                "phan_3_bien_dong_bat_thuong": {
                                    "xuat_dot_bien": [],
                                    "hang_ton_lau_60_ngay": [
                                        {
                                            "ma_hh": "SKU-MOCK-02",
                                            "ten_hh": "Bulong Inox Cũ",
                                            "ton_kho_u_dong": 100,
                                            "kien_nghi": "Thanh lý giải phóng diện tích"
                                        }
                                    ]
                                },
                                "insights_widget": [
                                    {"icon": "fa-solid fa-triangle-exclamation", "title": "Cảnh báo", "content": "SKU-MOCK-01 thiếu"}
                                ],
                                "markdown_report": "## Báo Cáo Gemini Live\n\nNội dung Markdown 3 phần hoàn chỉnh."
                            })
                        }
                    ]
                }
            }
        ]
    }

    service = GeminiService(api_key="valid-mock-api-key-123456789")

    # Giả lập httpx.Client.post trả về 200 OK
    mock_post_success = MagicMock()
    mock_post_success.status_code = 200
    mock_post_success.json.return_value = gemini_json_response

    with patch("httpx.Client.post", return_value=mock_post_success):
        report = service.generate_inventory_report(mock_warehouse_data)
        assert report["is_fallback"] is False
        assert "Google Gemini API" in report["model_used"]
        assert report["phan_1_tong_quan"]["tong_so_sku"] == 10
        assert len(report["phan_2_canh_bao_va_de_xuat_nhap"]) == 1
        assert report["phan_2_canh_bao_va_de_xuat_nhap"][0]["ma_hh"] == "SKU-MOCK-01"

    # 3b. Giả lập Gemini API gặp lỗi 429 Rate Limit hoặc Network Timeout
    mock_post_error = MagicMock()
    mock_post_error.status_code = 429
    mock_post_error.text = "RESOURCE_EXHAUSTED: Rate limit exceeded"

    service_fallback = GeminiService(api_key="valid-mock-api-key-123456789")
    service_fallback.max_retries = 1

    with patch("httpx.Client.post", return_value=mock_post_error), patch("time.sleep", return_value=None):
        # Service phải tự động kích hoạt fallback an toàn mà không văng Exception
        report_fallback = service_fallback.generate_inventory_report(mock_warehouse_data)
        assert report_fallback["is_fallback"] is True
        assert "Fallback" in report_fallback["model_used"]
        assert len(report_fallback["phan_2_canh_bao_va_de_xuat_nhap"]) == 1
        assert report_fallback["phan_2_canh_bao_va_de_xuat_nhap"][0]["ma_hh"] == "SKU-MOCK-01"


# =============================================================================
# TEST 4: FASTAPI API ENDPOINTS INTEGRATION
# =============================================================================
def test_ai_api_endpoints_integration():
    """
    Test 4: Gọi các Endpoints qua FastAPI TestClient:
    - POST /api/v1/ai/generate-report
    - GET /api/v1/ai/advisory
    - GET /api/v1/ai/raw-context
    """
    client = TestClient(app)

    # Đăng nhập lấy access_token
    login_res = client.post("/api/v1/auth/login", json={"TenDangNhap": "admin", "MatKhau": "admin123"})
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Test POST /api/v1/ai/generate-report
    res_report = client.post("/api/v1/ai/generate-report", headers=headers)
    assert res_report.status_code == 200, f"Generate report failed: {res_report.text}"
    report_data = res_report.json()
    assert report_data["status"] == "success"
    assert "phan_1_tong_quan" in report_data
    assert "phan_2_canh_bao_va_de_xuat_nhap" in report_data
    assert "phan_3_bien_dong_bat_thuong" in report_data
    assert len(report_data["markdown_report"]) > 50

    # 2. Test GET /api/v1/ai/advisory
    res_adv = client.get("/api/v1/ai/advisory", headers=headers)
    assert res_adv.status_code == 200
    adv_data = res_adv.json()
    assert "insights" in adv_data
    assert len(adv_data["insights"]) > 0

    # 3. Test GET /api/v1/ai/raw-context (Kiểm toán bảo mật không lộ giá nhập)
    res_ctx = client.get("/api/v1/ai/raw-context", headers=headers)
    assert res_ctx.status_code == 200
    raw_ctx_str = json.dumps(res_ctx.json())
    assert "DonGiaNhap" not in raw_ctx_str
    assert "import_price" not in raw_ctx_str
    assert "ThanhTien" not in raw_ctx_str
