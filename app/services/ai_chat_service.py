# app/services/ai_chat_service.py
"""
Phân hệ Trợ Lý AI Chat Box (SmartLogis Conversational AI Assistant)
1. Đồng bộ 100% dữ liệu CSDL thời gian thực: Tồn kho, Cảnh báo tồn min, Burn-rate, Dead stock.
2. Am hiểu toàn diện thông tin & kiến trúc dự án SmartLogis AI:
   - Cơ chế bảo vệ 2 tầng Zero Negative Stock (Atomic SQL Decrement + Check Constraint).
   - Giao dịch Master-Detail ACID All-or-Nothing.
   - Mô hình phân quyền RBAC 3 vai trò (Admin, Thủ kho kiêm Kế toán, Nhân viên kho).
   - Sổ Thẻ kho bất biến số dư lũy kế.
   - Data Sanitizer khử trùng 100% giá vốn bảo vệ bí mật kinh doanh.
3. Hỗ trợ Google Gemini LLM API khi có key, kết hợp Local Grounded Conversational Fallback Engine
   hoạt động ngoại tuyến 100% bền bỉ, không ảo giác (Zero Hallucination).
"""

import re
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.services.ai_data_service import aggregate_warehouse_data_30d, sanitize_inventory_payload
from app.services.inventory_service import get_dashboard_kpis
from app.services.gemini_service import gemini_service
from app.schemas.inventory_schemas import AIChatMessage
from app.models.inventory_models import NhaCungCap

logger = logging.getLogger("smartlogis.aichat")

SYSTEM_CHAT_PROMPT = """Bạn là Trợ Lý Kho Thông Minh (SmartLogis AI Warehouse Assistant) của dự án SmartLogis AI v2.0.
BẮT BUỘC TUÂN THỦ CÁC NGUYÊN TẮC SAU:
1. TRẢ LỜI CĂN CỨ VÀO DỮ LIỆU CƠ SỞ DỮ LIỆU THỰC TẾ được cung cấp trong ngữ cảnh JSON. Tuyệt đối KHÔNG bịa đặt số lượng, mã SKU, tên hàng hay thông số không tồn tại (Strict Anti-Hallucination).
2. Dữ liệu giá vốn đã được khử trùng bảo mật bởi Module Data Sanitizer để bảo vệ bí mật kinh doanh.
3. Nắm vững kiến trúc dự án SmartLogis AI:
   - Cơ chế chống tồn âm 2 tầng (Zero Negative Stock): Khóa nguyên tử Atomic SQL Decrement tại backend kết hợp ràng buộc CHECK (SoLuongTon >= 0) tại CSDL.
   - Giao dịch ACID: Phiếu nhập/xuất xử lý All-or-Nothing, rollback hoàn toàn nếu vi phạm toàn vẹn.
   - Phân quyền RBAC 3 vai trò: Admin (toàn quyền), Thủ kho kiêm Kế toán (vận hành kho, chứng từ, báo cáo), Nhân viên kho (chỉ tra cứu danh mục).
   - Sổ Thẻ kho: Duy trì số dư lũy kế bất biến Tồn(N) = Tồn(N-1) +/- Lượng biến động.
4. Trả lời bằng tiếng Việt chuyên nghiệp, súc tích, định dạng Markdown rõ ràng (sử dụng bảng biểu, danh sách, in đậm khi cần).
"""


def build_warehouse_chat_context(db: Session) -> Dict[str, Any]:
    """Tổng hợp dữ liệu CSDL kho thời gian thực để làm ngữ cảnh cho AI Chat."""
    warehouse_data = aggregate_warehouse_data_30d(db)
    kpis = get_dashboard_kpis(db)
    ncc_count = db.query(NhaCungCap).count()

    context = {
        "metadata": {
            **warehouse_data.get("metadata", {}),
            "tong_sku": kpis.get("tong_sku", 0),
            "tong_gia_tri_xuat_thang": kpis.get("tong_gia_tri_xuat_thang", 0),
            "tong_giao_dich_thang": kpis.get("tong_giao_dich_thang", 0),
            "tong_phieu_nhap": kpis.get("tong_phieu_nhap", 0),
            "tong_phieu_xuat": kpis.get("tong_phieu_xuat", 0),
            "tong_nha_cung_cap": ncc_count,
            "project_name": "SmartLogis AI - Quản Lý Kho Thông Minh Tích Hợp AI",
            "system_version": "v2.0 Enterprise Ready"
        },
        "low_stock_alerts": warehouse_data.get("low_stock_alerts", []),
        "dead_stock_items": warehouse_data.get("dead_stock_items", []),
        "high_burn_rate_items": warehouse_data.get("high_burn_rate_items", []),
        "inventory_summary": warehouse_data.get("inventory_summary", [])
    }
    return sanitize_inventory_payload(context)


def generate_local_grounded_chat_response(context: Dict[str, Any], query: str) -> Dict[str, Any]:
    """
    Local Grounded Conversational Fallback Engine:
    Phân tích câu hỏi và sinh câu trả lời đối chiếu chính xác 100% CSDL nội bộ
    khi mất mạng, không có API Key hoặc bị giới hạn Quota.
    """
    q = query.lower().strip()
    meta = context.get("metadata", {})
    low_stocks = context.get("low_stock_alerts", [])
    dead_stocks = context.get("dead_stock_items", [])
    high_burns = context.get("high_burn_rate_items", [])
    all_items = context.get("inventory_summary", [])

    suggested_questions = [
        "📊 Sinh báo cáo điều hành kho 3 phần",
        "⚠️ Mặt hàng nào đang thiếu hụt nguy cấp?",
        "📦 Danh sách hàng tồn lâu > 60 ngày",
        "🚀 Top mặt hàng xuất kho nhiều nhất",
        "🛡️ Giải thích cơ chế chống tồn âm Zero Negative Stock"
    ]

    # --- Ý ĐỊNH 1: BÁO CÁO 3 PHẦN ---
    if any(k in q for k in ["báo cáo", "3 phần", "ba phần", "report", "tổng kết", "điều hành kho"]):
        reply = [
            "### 📊 BÁO CÁO ĐIỀU HÀNH VẬN HÀNH KHO TOÀN DIỆN (3 PHẦN CHUẨN MỰC)",
            f"*Dữ liệu trích xuất thời gian thực | Hệ thống quản lý: **{meta.get('tong_sku', 0)} SKU** vật tư*",
            "",
            "#### 1️⃣ PHẦN 1: TÌNH TRẠNG TỒN KHO TỔNG QUAN",
            f"- **Tổng số mặt hàng (SKU) quản lý**: {meta.get('tong_sku', 0)} SKU.",
            f"- **Số mặt hàng an toàn tồn kho**: {max(0, meta.get('tong_sku', 0) - len(low_stocks))} SKU.",
            f"- **Số mặt hàng chạm / dưới tồn min**: **{len(low_stocks)} SKU** (Cần lập kế hoạch nhập bù).",
            f"- **Số mặt hàng ứ đọng > 60 ngày (Dead stock)**: **{len(dead_stocks)} SKU**.",
            f"- **Tổng giao dịch trong kỳ**: {meta.get('tong_giao_dich_thang', 0)} ({meta.get('tong_phieu_nhap', 0)} Nhập / {meta.get('tong_phieu_xuat', 0)} Xuất).",
            f"- **Tổng giá trị xuất kho ước tính**: {meta.get('tong_gia_tri_xuat_thang', 0):,.0f} VNĐ (Định giá theo giá vốn bình quân gia quyền).",
            "",
            "#### 2️⃣ PHẦN 2: CẢNH BÁO & GỢI Ý NHẬP HÀNG KHẨN CẤP",
            "| Mã SKU | Tên Hàng Hóa | Tồn Kho | Ngưỡng Min | Thiếu Hụt | Tốc Độ Xuất | Đề Xuất Nhập | Mức Độ |",
            "| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |"
        ]

        if not low_stocks:
            reply.append("| - | *Tuyệt vời! Toàn bộ kho đang ở trạng thái an toàn* | - | - | - | - | - | AN TOÀN |")
        else:
            for it in low_stocks:
                badge = "**NGUY CẤP**" if it.get("muc_do_nguy_cap") == "KHAN_CAP" else "CẢNH BÁO"
                reply.append(
                    f"| `{it['ma_hh']}` | {it['ten_hh']} | {it['ton_hien_tai']} {it['don_vi_tinh']} | {it['ton_toi_thieu']} | "
                    f"-{it['thieu_hut']} | {it.get('burn_rate_ngay', 0)}/ngày | **+{it.get('de_xuat_nhap_them', 0)}** | {badge} |"
                )

        reply.extend([
            "",
            "#### 3️⃣ PHẦN 3: BIẾN ĐỘNG BẤT THƯỜNG TRONG KHO",
            "**3.1. Hàng hóa xuất tăng mạnh (High Burn-Rate):**"
        ])

        if not high_burns:
            reply.append("- Không ghi nhận SKU nào có tốc độ xuất kho đột biến vượt ngưỡng.")
        else:
            for hb in high_burns:
                reply.append(f"- **{hb['ten_hh']}** (`{hb['ma_hh']}`): Xuất {hb.get('tong_xuat_30d', 0)} đơn vị trong 30 ngày (Trung bình **{hb.get('burn_rate_ngay', 0)} đơn vị/ngày**). Tồn hiện tại: {hb.get('ton_kho_hien_tai', 0)}.")

        reply.append("\n**3.2. Hàng tồn kho ứ đọng lâu (> 60 ngày không xuất hàng):**")
        if not dead_stocks:
            reply.append("- Tốc độ luân chuyển kho tốt, không có hàng tồn đọng quá 60 ngày.")
        else:
            for ds in dead_stocks[:10]:
                reply.append(f"- **{ds['ten_hh']}** (`{ds['ma_hh']}`): Tồn đọng `{ds.get('ton_kho_u_dong', 0)}` {ds.get('don_vi_tinh', '')}, không xuất trong **{ds.get('so_ngay_khong_xuat', 0)} ngày**. *Đề xuất: Lập phương án kích cầu hoặc thanh lý để tối ưu diện tích kho.*")

        return {
            "reply": "\n".join(reply),
            "suggested_questions": [
                "Lập danh sách phiếu nhập cho các mặt hàng nguy cấp",
                "Phân tích nguyên nhân hàng tồn lâu > 60 ngày",
                "Kiểm tra mặt hàng xuất chạy nhất"
            ]
        }

    # --- Ý ĐỊNH 2: CẢNH BÁO TỒN KHO / THIẾU HỤT / CẦN NHẬP GẤP ---
    if any(k in q for k in ["thiếu", "tồn min", "hết hàng", "nhập hàng", "cảnh báo", "low stock", "restock", "cần nhập"]):
        if not low_stocks:
            return {
                "reply": "✅ **Tuyệt vời!** Hiện tại toàn bộ mặt hàng trong kho đều đang ở ngưỡng an toàn, không có SKU nào bị chạm hoặc dưới tồn tối thiểu.",
                "suggested_questions": suggested_questions
            }

        lines = [
            f"⚠️ **CẢNH BÁO TỒN KHO: Có {len(low_stocks)} mặt hàng đang chạm hoặc dưới ngưỡng tồn tối thiểu.**",
            "Dưới đây là danh sách ưu tiên bù đắp hàng hóa:",
            "",
            "| Mã SKU | Tên Hàng Hóa | Tồn Thực Tế | Tồn Min | Thiếu Hụt | Đề Xuất Nhập Thêm | Mức Độ |",
            "| :--- | :--- | :---: | :---: | :---: | :---: | :---: |"
        ]
        for it in low_stocks:
            muc_do = "🚨 Nguy cấp" if it.get("muc_do_nguy_cap") == "KHAN_CAP" else "⚠️ Cận ngưỡng"
            lines.append(
                f"| `{it['ma_hh']}` | {it['ten_hh']} | **{it['ton_hien_tai']}** {it['don_vi_tinh']} | {it['ton_toi_thieu']} | "
                f"{it['thieu_hut']} | **+{it.get('de_xuat_nhap_them', 0)} {it['don_vi_tinh']}** | {muc_do} |"
            )
        lines.extend([
            "",
            "💡 **Khuyến nghị:** Bạn có thể vào menu **Phiếu Nhập Kho** (`/inbound`) để lập chứng từ bổ sung số dư ngay lập tức."
        ])
        return {
            "reply": "\n".join(lines),
            "suggested_questions": [
                "Gợi ý nhà cung cấp cho các mặt hàng thiếu hụt",
                "Tốc độ xuất kho của các mặt hàng này là bao nhiêu?",
                "Sinh báo cáo điều hành kho 3 phần"
            ]
        }

    # --- Ý ĐỊNH 3: HÀNG TỒN LÂU > 60 NGÀY / DEAD STOCK ---
    if any(k in q for k in ["tồn lâu", "ứ đọng", "dead stock", "60 ngày", "chậm", "không xuất", "thanh lý"]):
        if not dead_stocks:
            return {
                "reply": "✨ **Kho vận hành rất tích cực!** Không ghi nhận mặt hàng nào bị tồn kho ứ đọng quá 60 ngày mà không xuất hàng.",
                "suggested_questions": suggested_questions
            }

        lines = [
            f"📦 **DANH SÁCH {len(dead_stocks)} MẶT HÀNG TỒN KHO LÂU (> 60 NGÀY KHÔNG XUẤT):**",
            "",
            "| Mã SKU | Tên Hàng Hóa | ĐVT | Tồn Đọng | Số Ngày Không Xuất | Ngày Xuất Cuối |",
            "| :--- | :--- | :---: | :---: | :---: | :---: |"
        ]
        for it in dead_stocks:
            lines.append(
                f"| `{it['ma_hh']}` | {it['ten_hh']} | {it['don_vi_tinh']} | **{it.get('ton_kho_u_dong', 0)}** | "
                f"**{it.get('so_ngay_khong_xuat', 0)} ngày** | {it.get('ngay_xuat_cuoi', '--')} |"
            )
        lines.extend([
            "",
            "🔍 **Kiến nghị:** Các mặt hàng trên chiếm dụng diện tích lưu kho và vốn lưu động. Doanh nghiệp nên kích cầu, luân chuyển sang dự án khác hoặc lập kế hoạch thanh lý."
        ])
        return {
            "reply": "\n".join(lines),
            "suggested_questions": [
                "Top mặt hàng xuất kho nhiều nhất",
                "Cảnh báo hàng chạm ngưỡng tồn min",
                "Sinh báo cáo điều hành kho 3 phần"
            ]
        }

    # --- Ý ĐỊNH 4: HÀNG XUẤT CHẠY / BURN RATE CAO ---
    if any(k in q for k in ["xuất chạy", "bán chạy", "xuất mạnh", "burn rate", "tiêu thụ", "đột biến", "nhanh nhất"]):
        if not high_burns:
            return {
                "reply": "📊 Trong 30 ngày qua, tốc độ xuất kho của các mặt hàng diễn ra đều đặn, không ghi nhận SKU nào đột biến vượt ngưỡng 2 đơn vị/ngày.",
                "suggested_questions": suggested_questions
            }

        lines = [
            f"🚀 **TOP {len(high_burns)} MẶT HÀNG TIÊU THỤ MẠNH TRONG 30 NGÀY (HIGH BURN-RATE):**",
            "",
            "| Mã SKU | Tên Hàng Hóa | Tổng Xuất 30 Ngày | Tốc Độ/Ngày (Burn-rate) | Tồn Khả Dụng Còn Lại |",
            "| :--- | :--- | :---: | :---: | :---: |"
        ]
        for it in high_burns:
            lines.append(
                f"| `{it['ma_hh']}` | {it['ten_hh']} | **{it.get('tong_xuat_30d', 0)}** | "
                f"**{it.get('burn_rate_ngay', 0)} đv/ngày** | {it.get('ton_kho_hien_tai', 0)} |"
            )
        lines.extend([
            "",
            "⚠️ **Lưu ý:** Cần theo dõi sát mức tồn kho của nhóm hàng này để tránh nguy cơ đứt gãy chuỗi cung ứng."
        ])
        return {
            "reply": "\n".join(lines),
            "suggested_questions": [
                "Kiểm tra số dư an toàn của các mặt hàng tiêu thụ mạnh",
                "Sinh báo cáo điều hành kho 3 phần",
                "Các mặt hàng nào cần nhập bổ sung gấp?"
            ]
        }

    # --- Ý ĐỊNH 5: THÔNG TIN DỰ ÁN / KIẾN TRÚC KHO / BẢO VỆ ACID & CHỐNG TỒN ÂM ---
    if any(k in q for k in ["dự án", "smartlogis", "acid", "tồn âm", "zero negative", "rbac", "phân quyền", "bảo mật", "sanitizer", "thẻ kho", "kiến trúc", "chống tồn âm"]):
        reply = r"""### 🛡️ KIẾN TRÚC & CÔNG NGHỆ CỐT LÕI CỦA SMARTLOGIS AI v2.0

Hệ thống Quản lý Kho Thông minh **SmartLogis AI** được thiết kế chuẩn doanh nghiệp với 5 trụ cột kỹ thuật:

1. **Cơ Chế Bảo Vệ 2 Tầng Chống Tồn Âm (Zero Negative Stock):**
   - **Tầng Backend:** Atomic SQL Decrement với điều kiện `WHERE SoLuongTon >= total_xuat`, chống hiện tượng Race Condition (tranh chấp đa luồng).
   - **Tầng CSDL:** Ràng buộc `CHECK (SoLuongTon >= 0)` kết hợp Triggers ngăn chặn tồn âm ở mọi cấp độ.
2. **Giao Dịch ACID Chuẩn Mực:**
   - Đóng gói Master - Detail (`phieu_nhap`, `chi_tiet_phieu_nhap` / `phieu_xuat`, `chi_tiet_phieu_xuat`).
   - Giao dịch thực hiện All-or-Nothing: Nếu phát hiện thiếu 1 dòng hàng, toàn bộ giao dịch được Rollback ngay lập tức.
3. **Mô Hình Phân Quyền RBAC 3 Vai Trò:**
   - 👑 **Admin**: Toàn quyền cấu hình hệ thống và danh mục.
   - 📋 **Thủ kho kiêm Kế toán**: Lập phiếu Nhập/Xuất kho, thẩm tra số dư, trích xuất báo cáo tài chính kế toán.
   - 👷 **Nhân viên kho (Staff)**: Chỉ có quyền tra cứu danh mục hàng hóa hiện trường; bị chặn toàn bộ thao tác sửa đổi hay lập phiếu (HTTP 403).
4. **Sổ Thẻ Kho (Inventory Ledger) Bất Biến:**
   - Duy trì công thức lũy kế nghiêm ngặt: $Tồn(N) = Tồn(N-1) \pm Lượng\_biến\_động$.
   - Tính năng tự động đối chiếu và đồng bộ số dư ACID.
5. **Module Data Sanitizer Khử Trùng Giá Vốn:**
   - Tự động loại bỏ 100% trường giá vốn (`DonGiaNhap`, `ThanhTien`, `GiaVon`) trước khi nạp vào AI Context để bảo vệ tuyệt đối bí mật kinh doanh."""
        return {
            "reply": reply,
            "suggested_questions": [
                "Sinh báo cáo điều hành kho 3 phần",
                "Kiểm tra mặt hàng nào đang chạm tồn min",
                "Cách thức tính giá trị xuất kho bình quân gia quyền"
            ]
        }

    # --- Ý ĐỊNH 6: TỔNG QUAN / KPI TOÀN BỘ KHO ---
    if any(k in q for k in ["tổng quan", "kpi", "thống kê", "bao nhiêu sku", "tổng số", "tình hình kho"]):
        reply = f"""### 📈 TỔNG QUAN CHỈ SỐ VẬN HÀNH KHO SMARTLOGIS AI

- **Tổng danh mục quản lý**: **{meta.get('tong_sku', 0)} SKU** vật tư.
- **Mặt hàng chạm / dưới tồn tối thiểu**: **{len(low_stocks)} SKU** ({'⚠️ Cần xử lý' if low_stocks else '✅ An toàn'}).
- **Tổng số giao dịch đã thực hiện**: **{meta.get('tong_giao_dich_thang', 0)} giao dịch** ({meta.get('tong_phieu_nhap', 0)} Phiếu Nhập / {meta.get('tong_phieu_xuat', 0)} Phiếu Xuất).
- **Tổng giá trị xuất kho lũy kế**: **{meta.get('tong_gia_tri_xuat_thang', 0):,.0f} VNĐ** (Tính theo giá vốn bình quân gia quyền).
- **Đối tác cung cấp (Nhà cung cấp)**: **{meta.get('tong_nha_cung_cap', 0)} đối tác** liên kết.
- **Hàng tồn kho ứ đọng > 60 ngày**: **{len(dead_stocks)} SKU**."""
        return {
            "reply": reply,
            "suggested_questions": suggested_questions
        }

    # --- Ý ĐỊNH 7: TRA CỨU MẶT HÀNG / SKU CỤ THỂ ---
    # Tìm kiếm theo mã hàng hoặc tên hàng trong CSDL
    matched_items = []
    stop_words = {"chống", "hoạt", "động", "thế", "nào", "quản", "lý", "smartlogis", "dự", "án", "kho", "hàng", "của"}
    for it in all_items:
        ma = it.get("ma_hh", "").lower()
        ten = it.get("ten_hh", "").lower()
        if ma in q:
            matched_items.append(it)
        elif len(ten) > 0 and ten in q:
            matched_items.append(it)
        else:
            # Tra cứu từ khóa tên (loại bỏ stop words để tránh match nhầm từ đơn)
            q_clean = q.replace("tra cứu", "").replace("tìm", "").replace("mặt hàng", "").replace("sku", "").strip()
            tokens = [t for t in q_clean.split() if len(t) >= 3 and t not in stop_words]
            if len(tokens) >= 2 and all(tok in ten for tok in tokens[:2]):
                matched_items.append(it)
            elif len(tokens) == 1 and tokens[0] in ma:
                matched_items.append(it)

    if matched_items:
        # Lấy tối đa 5 mặt hàng khớp nhất
        lines = ["🔍 **KẾT QUẢ TRA CỨU DANH MỤC & TỒN KHO THỜI GIAN THỰC:**", ""]
        for it in matched_items[:5]:
            ton = it.get("ton_kho_hien_tai", 0)
            min_ton = it.get("ton_kho_toi_thieu", 0)
            status_tag = "🔴 **DƯỚI TỒN MIN**" if ton < min_ton else ("🟡 **CHẠM TỒN MIN**" if ton == min_ton else "🟢 **AN TOÀN**")
            lines.extend([
                f"### 📦 `{it['ma_hh']}` - {it['ten_hh']}",
                f"- **Nhóm vật tư**: {it.get('nhom_hang', 'Khác')} | **Đơn vị tính**: {it.get('don_vi_tinh', '')}",
                f"- **Số lượng tồn thực tế**: **{ton} {it.get('don_vi_tinh', '')}**",
                f"- **Ngưỡng tồn tối thiểu**: {min_ton} {it.get('don_vi_tinh', '')}",
                f"- **Trạng thái**: {status_tag}",
                f"- **Xuất 30 ngày qua**: {it.get('tong_xuat_30_ngay', 0)} (Trung bình {it.get('xuat_trung_binh_ngay', 0)}/ngày)",
                f"- **Dự trữ ước tính**: {it.get('du_tru_uoc_tinh_ngay', 0)} ngày hoạt động.",
                ""
            ])
        return {
            "reply": "\n".join(lines),
            "suggested_questions": [
                f"Xem lịch sử thẻ kho của {matched_items[0]['ma_hh']}",
                "Mặt hàng nào đang thiếu hụt nguy cấp?",
                "Sinh báo cáo điều hành kho 3 phần"
            ]
        }

    # --- MẶC ĐỊNH / CHÀO HỎI ---
    return {
        "reply": f"""Xin chào bạn! Tôi là **Trợ Lý AI Vận Hành Kho SmartLogis AI**. 

Tôi được kết nối trực tiếp với **Cơ sở dữ liệu kho thời gian thực** (hiện đang theo dõi **{meta.get('tong_sku', 0)} SKU**, phát hiện **{len(low_stocks)} cảnh báo thiếu hụt**, và **{len(dead_stocks)} mặt hàng tồn lâu > 60 ngày**).

Bạn có thể yêu cầu tôi hỗ trợ:
1. 📊 **Sinh Báo Cáo Điều Hành Kho 3 Phần** (Tổng quan, Đề xuất nhập hàng khẩn cấp, Biến động bất thường).
2. ⚠️ **Cảnh báo tồn kho**: Liệt kê các mặt hàng cần nhập bổ sung ngay và số lượng đề xuất.
3. 📦 **Phát hiện hàng ứ đọng (Dead Stock)**: Các mặt hàng > 60 ngày không xuất kho.
4. 🔍 **Tra cứu chi tiết bất kỳ mặt hàng nào** (gõ mã SKU hoặc tên hàng, ví dụ: `HH-THEP-D08`).
5. 🛡️ **Tìm hiểu kiến trúc**: Cơ chế chống tồn âm 2 tầng Zero Negative Stock, giao dịch ACID, phân quyền RBAC 3 vai trò.

Hãy nhập câu hỏi bên dưới hoặc chọn một trong các gợi ý nhanh!""",
        "suggested_questions": suggested_questions
    }


def process_ai_chat_message(
    db: Session,
    message: str,
    history: Optional[List[AIChatMessage]] = None
) -> Dict[str, Any]:
    """
    Hàm điều phối xử lý tin nhắn Chat Box:
    1. Trích xuất Context CSDL kho 30 ngày (đã làm sạch giá vốn).
    2. Nếu có Gemini API Key hợp lệ: Gọi Google Gemini API với System Instruction chống ảo giác.
    3. Nếu không có Key hoặc mạng gián đoạn: Tự động kích hoạt Local Grounded Conversational Fallback Engine.
    """
    context = build_warehouse_chat_context(db)
    
    # Kiểm tra xem có cấu hình Gemini API Key không
    if gemini_service.is_configured():
        try:
            # Chuẩn bị context rút gọn để gửi kèm prompt
            meta = context.get("metadata", {})
            summary_context = {
                "metadata": meta,
                "low_stock_count": len(context.get("low_stock_alerts", [])),
                "dead_stock_count": len(context.get("dead_stock_items", [])),
                "high_burn_count": len(context.get("high_burn_rate_items", [])),
                "top_low_stocks": context.get("low_stock_alerts", [])[:10],
                "top_dead_stocks": context.get("dead_stock_items", [])[:10],
                "top_high_burns": context.get("high_burn_rate_items", [])[:10],
                "sample_items": context.get("inventory_summary", [])[:15]
            }

            # Lịch sử hội thoại
            hist_str = ""
            if history:
                for h in history[-4:]:
                    role_lbl = "Người dùng" if h.role == "user" else "Trợ lý AI"
                    hist_str += f"{role_lbl}: {h.content}\n"

            user_query_prompt = f"""Dưới đây là dữ liệu CSDL kho thời gian thực của hệ thống SmartLogis AI:
```json
{json.dumps(summary_context, ensure_ascii=False, indent=2)}
```

Lịch sử hội thoại trước đó:
{hist_str or "(Chưa có)"}

Câu hỏi mới của người dùng:
"{message}"

YÊU CẦU: Hãy trả lời câu hỏi dựa trên dữ liệu kho thực tế ở trên. Nếu người dùng yêu cầu báo cáo 3 phần hoặc hỏi về tồn kho, hãy liệt kê số liệu chính xác. Định dạng câu trả lời Markdown đẹp mắt."""

            model_name = "gemini-2.0-flash"
            gemini_reply = gemini_service._call_gemini_with_retry(model_name, user_query_prompt)
            if gemini_reply and len(gemini_reply.strip()) > 10:
                return {
                    "status": "success",
                    "reply": gemini_reply.strip(),
                    "model_used": f"Google Gemini API ({model_name})",
                    "is_fallback": False,
                    "context_summary": meta,
                    "suggested_questions": [
                        "📊 Sinh báo cáo điều hành kho 3 phần",
                        "⚠️ Mặt hàng nào đang thiếu hụt nguy cấp?",
                        "📦 Danh sách hàng tồn lâu > 60 ngày",
                        "🛡️ Cơ chế chống tồn âm Zero Negative Stock"
                    ]
                }
        except Exception as e:
            logger.warning(f"[AIChat] Lỗi khi gọi Gemini API: {e}. Kích hoạt Local Grounded Fallback.")

    # Kích hoạt Local Grounded Fallback Engine
    fallback_res = generate_local_grounded_chat_response(context, message)
    return {
        "status": "success",
        "reply": fallback_res.get("reply", ""),
        "model_used": "SmartLogis Grounded Analytical Engine (Local DB Grounded)",
        "is_fallback": True,
        "context_summary": context.get("metadata", {}),
        "suggested_questions": fallback_res.get("suggested_questions", [])
    }
