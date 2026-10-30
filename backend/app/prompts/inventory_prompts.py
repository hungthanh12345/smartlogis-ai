# app/prompts/inventory_prompts.py
"""
Hệ Thống Quản Lý Prompt Templates Cho SmartLogis AI
Tối ưu hóa kỹ thuật Prompt Engineering với:
1. Chỉ thị hệ thống chống ảo giác nghiêm ngặt (Strict Anti-Hallucination).
2. Quy chuẩn cấu trúc đầu ra 3 phần (Tổng quan, Đề xuất nhập hàng, Biến động bất thường).
3. Hỗ trợ định dạng JSON có cấu trúc chuẩn cho Widget và Markdown cho báo cáo chuyên sâu.
"""

import json
from typing import Dict, Any

# System Prompt cốt lõi - Chống ảo giác tuyệt đối
SYSTEM_PROMPT_ANTI_HALLUCINATION = (
    "Bạn là Trợ lý Quản lý Kho Chuyên nghiệp (Senior Warehouse Logistics AI Assistant) thuộc hệ thống SmartLogis AI.\n"
    "BẮT BỘC TUÂN THỦ NGHIÊM NGẶT CÁC NGUYÊN TẮC SAU:\n"
    "1. CHỈ phân tích dựa trên dữ liệu JSON được cung cấp bên dưới. Tuyệt đối KHÔNG tự bịa số liệu, KHÔNG phỏng đoán các mã hàng (MaHH), tên hàng hay các số liệu không có trong dữ liệu (Anti-hallucination / Zero Hallucination).\n"
    "2. Nếu dữ liệu đầu vào rỗng (không có SKU nào hoặc is_empty = true), BẮT BUỘC thông báo rõ: 'Hệ thống chưa ghi nhận dữ liệu giao dịch hợp lệ trong kỳ phân tích' và không suy diễn thêm.\n"
    "3. Báo cáo phân tích BẮT BUỘC có cấu trúc chuẩn gồm 3 phần:\n"
    "   - PHẦN 1: TÌNH TRẠNG TỒN KHO TỔNG QUAN (Tổng số SKU, tổng lượng xuất 30 ngày, số SKU an toàn, số SKU chạm/dưới ngưỡng tồn tối thiểu).\n"
    "   - PHẦN 2: CẢNH BÁO & GỢI Ý NHẬP HÀNG KHẨN CẤP (Nêu rõ MaHH, TenHH, tồn hiện tại, tồn tối thiểu, lượng thiếu hụt, tốc độ xuất và số lượng đề xuất nhập thêm cụ thể).\n"
    "   - PHẦN 3: TÓM TẮT BIẾN ĐỘNG BẤT THƯỜNG (Các mặt hàng xuất tăng đột biến hoặc hàng tồn kho lâu > 60 ngày không phát sinh xuất hàng cần thanh lý/giải phóng mặt bằng).\n"
    "4. Phản hồi hoàn toàn bằng tiếng Việt chuẩn mực, rõ ràng, phong cách điều hành kho chuyên nghiệp."
)


def build_inventory_user_prompt(data: Dict[str, Any], output_format: str = "json") -> str:
    """
    Xây dựng User Prompt kèm JSON Context đã được khử nhạy cảm giá vốn.
    Hỗ trợ output_format = 'json' (cho Widget/API) hoặc 'markdown' (cho Báo cáo xuất bản).
    """
    is_empty = data.get("metadata", {}).get("is_empty", False)
    total_skus = data.get("metadata", {}).get("total_skus", 0)

    if is_empty or total_skus == 0:
        return (
            "DỮ LIỆU KHO CUNG CẤP: Hiện tại hệ thống không có bản ghi SKU hoặc giao dịch kho nào (Dữ liệu rỗng).\n"
            "Yêu cầu: Hãy đưa ra thông báo phù hợp rằng chưa có dữ liệu giao dịch hợp lệ theo đúng quy tắc chống ảo giác."
        )

    # Đóng gói ngữ cảnh tóm tắt để AI dễ dàng xử lý mà không bị quá tải token
    context_payload = {
        "metadata": data.get("metadata", {}),
        "low_stock_alerts": data.get("low_stock_alerts", [])[:15],  # Top 15 SKU thiếu hụt nhất
        "dead_stock_items": data.get("dead_stock_items", [])[:15],  # Top 15 SKU ứ đọng nhất
        "high_burn_rate_items": data.get("high_burn_rate_items", [])[:10],
        # Tóm tắt một số mặt hàng tiêu biểu
        "sample_inventory": data.get("inventory_summary", [])[:20]
    }

    json_context = json.dumps(context_payload, ensure_ascii=False, indent=2)

    if output_format == "json":
        return f"""Dưới đây là dữ liệu vận hành kho 30 ngày gần nhất (đã lọc bỏ giá vốn nhạy cảm):
```json
{json_context}
```

YÊU CẦU: Hãy phân tích số liệu trên và trả về kết quả theo ĐÚNG định dạng JSON sau (không kèm markdown râu ria ngoài JSON):
{{
  "phan_1_tong_quan": {{
    "tong_so_sku": {total_skus},
    "so_sku_canh_bao_ton_min": {len(data.get("low_stock_alerts", []))},
    "so_sku_u_dong_60_ngay": {len(data.get("dead_stock_items", []))},
    "danh_gia_chung": "Nhận xét tổng quát về mức độ an toàn tồn kho dựa trên số liệu"
  }},
  "phan_2_canh_bao_va_de_xuat_nhap": [
    {{
      "ma_hh": "Mã hàng",
      "ten_hh": "Tên hàng",
      "ton_hien_tai": 0,
      "ton_toi_thieu": 10,
      "thieu_hut": 10,
      "burn_rate_ngay": 1.5,
      "so_luong_de_xuat_nhap": 25,
      "muc_do": "KHAN_CAP | CANH_BAO",
      "ly_do": "Giải thích ngắn gọn căn cứ đề xuất"
    }}
  ],
  "phan_3_bien_dong_bat_thuong": {{
    "xuat_dot_bien": [
      {{
        "ma_hh": "Mã hàng",
        "ten_hh": "Tên hàng",
        "burn_rate_ngay": 3.0,
        "nhan_xet": "Xuất mạnh trong kỳ"
      }}
    ],
    "hang_ton_lau_60_ngay": [
      {{
        "ma_hh": "Mã hàng",
        "ten_hh": "Tên hàng",
        "ton_kho_u_dong": 50,
        "so_ngay_khong_xuat": 999,
        "kien_nghi": "Đề xuất thanh lý hoặc kích cầu"
      }}
    ]
  }},
  "insights_widget": [
    {{
      "icon": "fa-solid fa-triangle-exclamation text-amber-500",
      "title": "Tiêu đề ngắn 1",
      "content": "Nội dung ngắn gọn hiển thị trên dashboard widget"
    }},
    {{
      "icon": "fa-solid fa-cart-arrow-down text-sky-500",
      "title": "Tiêu đề ngắn 2",
      "content": "Nội dung ngắn gọn"
    }},
    {{
      "icon": "fa-solid fa-boxes-stacked text-emerald-500",
      "title": "Tiêu đề ngắn 3",
      "content": "Nội dung ngắn gọn"
    }}
  ],
  "markdown_report": "Nội dung báo cáo điều hành hoàn chỉnh gồm 3 phần dạng Markdown chuẩn"
}}
"""
    else:
        return f"""Dưới đây là dữ liệu kho 30 ngày gần nhất (đã khử nhạy cảm giá vốn):
```json
{json_context}
```

YÊU CẦU: Soạn thảo Báo Cáo Điều Hành Quản Lý Kho chuẩn mực dạng Markdown gồm đúng 3 phần:
# BÁO CÁO PHÂN TÍCH VẬN HÀNH KHO THỜI GIAN THỰC (SMARTLOGIS AI)
## Phần 1: Tình Trạng Tồn Kho Tổng Quan
## Phần 2: Cảnh Báo & Gợi Ý Nhập Hàng Khẩn Cấp
## Phần 3: Tóm Tắt Biến Động Bất Thường
"""
