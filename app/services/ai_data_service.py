# app/services/ai_data_service.py
"""
Module Tổng Hợp và Tiền Xử Lý Dữ Liệu Kho (Inventory Data Aggregator & Sanitizer)
Chịu trách nhiệm:
1. Trích xuất số liệu kho 30 ngày: Tồn kho hiện tại vs Tồn tối thiểu, Tốc độ xuất (Burn Rate).
2. Phát hiện hàng tồn kho lâu (> 60 ngày không phát sinh phiếu xuất - Dead Stock).
3. BẢO MẬT TUYỆT ĐỐI: Loại bỏ 100% đơn giá nhập (DonGiaNhap, ThanhTien, GiaVon) khỏi Context.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.inventory_models import HangHoa, TonKho, PhieuXuat, ChiTietPhieuXuat, NhomHang

# Danh sách đen các trường nhạy cảm về giá vốn & tài chính cần loại bỏ tuyệt đối
SENSITIVE_FINANCIAL_KEYS = {
    "dongianhap", "don_gia_nhap", "import_price", "cost_price",
    "thanhtien", "thanh_tien", "total_cost", "giavon", "gia_von",
    "gianhap", "gia_nhap", "purchase_price"
}


def sanitize_inventory_payload(data: Any) -> Any:
    """
    Hàm khử nhạy cảm đệ quy (Recursive Data Sanitizer):
    Quét qua toàn bộ từ điển/danh sách để loại bỏ hoàn toàn các trường chứa thông tin giá nhập
    trước khi chuyển thành JSON context gửi cho AI Model.
    """
    if isinstance(data, dict):
        cleaned = {}
        for k, v in data.items():
            if str(k).lower() in SENSITIVE_FINANCIAL_KEYS:
                continue
            cleaned[k] = sanitize_inventory_payload(v)
        return cleaned
    elif isinstance(data, list):
        return [sanitize_inventory_payload(item) for item in data]
    return data


def aggregate_warehouse_data_30d(
    db: Session,
    reference_date: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Truy vấn CSDL và tổng hợp dữ liệu vận hành kho trong 30 ngày gần nhất:
    - Bảng tổng hợp tồn kho hiện tại vs tồn tối thiểu (min_quantity).
    - Tốc độ xuất hàng 30 ngày (Tổng xuất, Trung bình/ngày - Burn rate).
    - Danh sách sản phẩm tồn kho lâu (> 60 ngày không xuất hàng - Dead Stock).
    - Trả về cấu trúc dữ liệu đã được làm sạch 100% không còn giá nhập nhạy cảm.
    """
    now = reference_date or datetime.now()
    start_30d = now - timedelta(days=30)
    start_60d = now - timedelta(days=60)

    # 1. Truy vấn tất cả SKU hàng hóa và tồn kho
    sku_query = db.query(
        HangHoa.MaHH,
        HangHoa.TenHH,
        HangHoa.MaDVT,
        HangHoa.TonToiThieu,
        NhomHang.TenNhom,
        TonKho.SoLuongTon
    ).join(TonKho, HangHoa.MaHH == TonKho.MaHH)\
     .outerjoin(NhomHang, HangHoa.MaNhom == NhomHang.MaNhom)\
     .all()

    total_skus = len(sku_query)

    # Xử lý kịch bản dữ liệu rỗng (Kho chưa có SKU nào)
    if total_skus == 0:
        return {
            "metadata": {
                "extracted_at": now.isoformat(),
                "period_days": 30,
                "is_empty": True,
                "total_skus": 0,
                "total_outbound_30d": 0
            },
            "inventory_summary": [],
            "low_stock_alerts": [],
            "dead_stock_items": [],
            "high_burn_rate_items": []
        }

    # 2. Truy vấn tổng lượng xuất trong 30 ngày gần nhất theo từng SKU
    outbound_30d_query = db.query(
        ChiTietPhieuXuat.MaHH,
        func.sum(ChiTietPhieuXuat.SoLuongXuat).label("tong_xuat_30d")
    ).join(PhieuXuat, ChiTietPhieuXuat.MaPX == PhieuXuat.MaPX)\
     .filter(PhieuXuat.NgayXuat >= start_30d)\
     .group_by(ChiTietPhieuXuat.MaHH)\
     .all()

    outbound_30d_map = {row.MaHH: int(row.tong_xuat_30d or 0) for row in outbound_30d_query}

    # 3. Truy vấn ngày xuất kho gần nhất của từng SKU để phát hiện Dead Stock (> 60 ngày không xuất)
    last_outbound_query = db.query(
        ChiTietPhieuXuat.MaHH,
        func.max(PhieuXuat.NgayXuat).label("ngay_xuat_cuoi")
    ).join(PhieuXuat, ChiTietPhieuXuat.MaPX == PhieuXuat.MaPX)\
     .group_by(ChiTietPhieuXuat.MaHH)\
     .all()

    last_outbound_map = {row.MaHH: row.ngay_xuat_cuoi for row in last_outbound_query}

    # 4. Phân loại và tính toán chỉ số cho từng mặt hàng
    inventory_summary = []
    low_stock_alerts = []
    dead_stock_items = []
    high_burn_rate_items = []

    total_outbound_volume = sum(outbound_30d_map.values())

    for row in sku_query:
        ma_hh = row.MaHH
        ten_hh = row.TenHH
        dvt = row.MaDVT or ""
        ten_nhom = row.TenNhom or "Khác"
        ton_kho = row.SoLuongTon
        ton_min = row.TonToiThieu
        tong_xuat = outbound_30d_map.get(ma_hh, 0)
        burn_rate_daily = round(tong_xuat / 30.0, 2)
        
        # Số ngày dự trữ còn lại dựa trên tốc độ xuất hiện tại
        if burn_rate_daily > 0:
            days_of_stock = round(ton_kho / burn_rate_daily, 1)
        else:
            days_of_stock = 999.0  # Không có xuất trong kỳ

        item_info = {
            "ma_hh": ma_hh,
            "ten_hh": ten_hh,
            "nhom_hang": ten_nhom,
            "don_vi_tinh": dvt,
            "ton_kho_hien_tai": ton_kho,
            "ton_kho_toi_thieu": ton_min,
            "tong_xuat_30_ngay": tong_xuat,
            "xuat_trung_binh_ngay": burn_rate_daily,
            "du_tru_uoc_tinh_ngay": days_of_stock
        }

        inventory_summary.append(item_info)

        # Cảnh báo chạm hoặc dưới ngưỡng tồn min
        if ton_kho <= ton_min:
            thieu_hut = max(0, ton_min - ton_kho)
            # Số lượng đề xuất nhập = Thiếu hụt để đạt tồn min + nhu cầu sử dụng trong 15 ngày tới
            de_xuat_nhap = thieu_hut + int(burn_rate_daily * 15)
            if de_xuat_nhap == 0 and ton_kho <= ton_min:
                de_xuat_nhap = max(10, ton_min)

            low_stock_alerts.append({
                "ma_hh": ma_hh,
                "ten_hh": ten_hh,
                "don_vi_tinh": dvt,
                "ton_hien_tai": ton_kho,
                "ton_toi_thieu": ton_min,
                "thieu_hut": thieu_hut,
                "burn_rate_ngay": burn_rate_daily,
                "de_xuat_nhap_them": de_xuat_nhap,
                "muc_do_nguy_cap": "KHAN_CAP" if ton_kho <= (ton_min * 0.3) else "CANH_BAO"
            })

        # Phát hiện Dead Stock: Có tồn kho > 0 nhưng > 60 ngày không phát sinh xuất hàng (hoặc chưa từng xuất)
        last_out_date = last_outbound_map.get(ma_hh)
        is_dead_stock = False
        days_inactive = 0

        if ton_kho > 0:
            if last_out_date is None:
                # Chưa từng có phiếu xuất nào
                is_dead_stock = True
                days_inactive = 999
            elif last_out_date < start_60d:
                # Phiếu xuất cuối cùng cách đây hơn 60 ngày
                is_dead_stock = True
                days_inactive = (now - last_out_date).days

        if is_dead_stock:
            dead_stock_items.append({
                "ma_hh": ma_hh,
                "ten_hh": ten_hh,
                "don_vi_tinh": dvt,
                "ton_kho_u_dong": ton_kho,
                "so_ngay_khong_xuat": days_inactive,
                "ngay_xuat_cuoi": last_out_date.strftime("%Y-%m-%d") if last_out_date else "Chưa từng xuất"
            })

        # Phát hiện xuất tăng mạnh (Burn rate cao)
        if burn_rate_daily >= 2.0:
            high_burn_rate_items.append({
                "ma_hh": ma_hh,
                "ten_hh": ten_hh,
                "tong_xuat_30d": tong_xuat,
                "burn_rate_ngay": burn_rate_daily,
                "ton_kho_hien_tai": ton_kho
            })

    # Sắp xếp danh sách cảnh báo theo độ ưu tiên
    low_stock_alerts.sort(key=lambda x: (x["muc_do_nguy_cap"] == "KHAN_CAP", x["thieu_hut"]), reverse=True)
    dead_stock_items.sort(key=lambda x: x["ton_kho_u_dong"], reverse=True)
    high_burn_rate_items.sort(key=lambda x: x["burn_rate_ngay"], reverse=True)

    raw_payload = {
        "metadata": {
            "extracted_at": now.strftime("%Y-%m-%d %H:%M:%S"),
            "period_days": 30,
            "is_empty": False,
            "total_skus": total_skus,
            "total_outbound_30d": total_outbound_volume,
            "low_stock_sku_count": len(low_stock_alerts),
            "dead_stock_sku_count": len(dead_stock_items),
            "high_burn_rate_count": len(high_burn_rate_items)
        },
        "inventory_summary": inventory_summary,
        "low_stock_alerts": low_stock_alerts,
        "dead_stock_items": dead_stock_items,
        "high_burn_rate_items": high_burn_rate_items
    }

    # BẮT BỘC: Làm sạch thông tin nhạy cảm trước khi trả về
    return sanitize_inventory_payload(raw_payload)
