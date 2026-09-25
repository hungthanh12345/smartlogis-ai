# app/services/ai_chat_service.py
"""
Phân hệ Trợ Lý AI Chat Box (SmartLogis Conversational AI Assistant)
1. Đồng bộ 100% dữ liệu CSDL thời gian thực: Tồn kho, Cảnh báo tồn min, Burn-rate, Dead stock, Nhà cung cấp.
2. Am hiểu toàn diện thông tin & kiến trúc dự án SmartLogis AI:
   - Cơ chế bảo vệ 2 tầng Zero Negative Stock (Atomic SQL Decrement + Check Constraint).
   - Giao dịch Master-Detail ACID All-or-Nothing.
   - Mô hình phân quyền RBAC 3 vai trò (Admin, Thủ kho kiêm Kế toán, Nhân viên kho).
   - Sổ Thẻ kho bất biến số dư lũy kế.
   - Data Sanitizer khử trùng 100% giá vốn bảo vệ bí mật kinh doanh.
3. Hỗ trợ Google Gemini LLM API (trả lời mọi câu hỏi mở rộng, nghiệp vụ, kiến thức chung kết hợp dữ liệu kho),
   kết hợp Local Grounded Conversational Analytical Engine hoạt động ngoại tuyến 100% bền bỉ, thông minh,
   không bao giờ lặp lại câu trả lời vô nghĩa.
"""

import re
import ast
import json
import logging
import operator
import unicodedata
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.services.ai_data_service import aggregate_warehouse_data_30d, sanitize_inventory_payload
from app.services.inventory_service import get_dashboard_kpis
from app.services.gemini_service import gemini_service, SUPPORTED_GEMINI_MODELS
from app.schemas.inventory_schemas import AIChatMessage
from app.models.inventory_models import NhaCungCap

logger = logging.getLogger("smartlogis.aichat")


OPERATORS_MAP = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def safe_eval_ast(node):
    """Đánh giá cây cú pháp trừu tượng an toàn tuyệt đối cho phép tính số học."""
    if isinstance(node, ast.Expression):
        return safe_eval_ast(node.body)
    elif isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    elif isinstance(node, ast.BinOp) and type(node.op) in OPERATORS_MAP:
        left = safe_eval_ast(node.left)
        right = safe_eval_ast(node.right)
        return OPERATORS_MAP[type(node.op)](left, right)
    elif isinstance(node, ast.UnaryOp) and type(node.op) in OPERATORS_MAP:
        operand = safe_eval_ast(node.operand)
        return OPERATORS_MAP[type(node.op)](operand)
    raise ValueError("Unsupported AST node")


def solve_math_expression(query: str) -> Optional[tuple]:
    """
    Nhận diện và giải chính xác các biểu thức số học (ví dụ: '1 + 1 = ?', '10 * 5', '100 / 4', '10% của 500000').
    Trả về (biểu thức sạch, kết quả số) hoặc None nếu không phải phép tính.
    """
    clean = query.strip()
    clean = re.sub(r'^(tính|tính giúp|kết quả của|cho biết|cho hỏi|kết quả|giải giúp)\s+', '', clean, flags=re.I)
    clean = re.sub(r'[\s=\?]+$', '', clean).strip()

    # Kiểm tra phép tính phần trăm: e.g. 10% của 500000, 15% * 200, 5% cua 1000
    pct_m = re.match(r'^([\d\.]+)\s*%\s*(?:của|cua|\*)\s*([\d\.]+)$', clean, re.I)
    if pct_m:
        try:
            rate = float(pct_m.group(1))
            base = float(pct_m.group(2))
            res = base * (rate / 100.0)
            if res.is_integer():
                res = int(res)
            return (f"{pct_m.group(1)}% của {int(base) if base.is_integer() else base}", res)
        except Exception:
            pass

    clean_eval = clean.replace('^', '**').replace('x', '*').replace('X', '*').replace(':', '/').replace(',', '')
    if not re.search(r'\d', clean_eval):
        return None
    # Chỉ cho phép các ký tự toán học số học an toàn
    if not re.fullmatch(r'[\d\s\+\-\*\/\%\(\)\.]+', clean_eval):
        return None
    # Phải chứa ít nhất 1 toán tử
    if not re.search(r'[\+\-\*\/\%]', clean_eval):
        return None

    try:
        parsed = ast.parse(clean_eval, mode='eval')
        val = safe_eval_ast(parsed)
        if isinstance(val, float) and val.is_integer():
            val = int(val)
        return (clean, val)
    except Exception:
        return None


def remove_accents(input_str: str) -> str:
    """Loại bỏ dấu tiếng Việt để phục vụ tìm kiếm mềm dẻo không dấu."""
    if not input_str:
        return ""
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    res = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
    return res.replace('đ', 'd').replace('Đ', 'D').lower().strip()


SYSTEM_CHAT_PROMPT = """Bạn là Trợ Lý AI Kho Thông Minh SmartLogis AI (SmartLogis Conversational Warehouse Assistant) v2.0 Enterprise.
Bạn có 2 nhiệm vụ chính:
1. ĐỐI VỚI CÂU HỎI VỀ KHO BÃI, TỒN KHO, VẬN HÀNH DỰ ÁN SMARTLOGIS AI:
   - Luôn sử dụng chính xác dữ liệu CSDL thời gian thực được cung cấp trong JSON context.
   - Tuyệt đối không bịa đặt số lượng tồn, mã SKU, tên hàng hay số liệu không có trong hệ thống (Strict Anti-Hallucination).
   - Nắm vững 5 trụ cột kiến trúc SmartLogis AI:
     + Chống tồn âm 2 tầng (Zero Negative Stock): Khóa nguyên tử Atomic SQL Decrement (WHERE SoLuongTon >= total_xuat) + CHECK constraint CSDL (SoLuongTon >= 0).
     + Giao dịch ACID: Phiếu nhập/xuất Master-Detail thực hiện All-or-Nothing, rollback 100% khi có lỗi.
     + Phân quyền RBAC 3 vai trò: Admin (toàn quyền), Thủ kho kiêm Kế toán (nhập/xuất/báo cáo), Nhân viên kho (chỉ tra cứu danh mục).
     + Sổ Thẻ kho: Duy trì số dư lũy kế bất biến Tồn(N) = Tồn(N-1) +/- Lượng biến động.
     + Data Sanitizer: Khử nhạy cảm 100% giá vốn bảo vệ bí mật kinh doanh.

2. ĐỐI VỚI MỌI CÂU HỎI MỞ RỘNG KHÁC (Logistics, Quản trị chuỗi cung ứng, Lập trình, Kỹ thuật, Trò chuyện, Giải đáp thắc mắc tổng quát...):
   - Bạn được tự do sử dụng toàn bộ kiến thức sâu rộng của Google Gemini để trả lời đầy đủ, thông minh, hữu ích và tận tình nhất. Không từ chối những câu hỏi nằm ngoài kho bãi nếu người dùng muốn hỏi hoặc tìm hiểu thêm.

3. PHONG CÁCH GIAO TIẾP:
   - Trả lời bằng tiếng Việt thân thiện, chuyên nghiệp, cấu trúc rõ ràng bằng Markdown (dùng bảng biểu, bullet points, in đậm khi cần).
"""


def build_warehouse_chat_context(db: Session) -> Dict[str, Any]:
    """Tổng hợp dữ liệu CSDL kho thời gian thực để làm ngữ cảnh cho AI Chat."""
    warehouse_data = aggregate_warehouse_data_30d(db)
    kpis = get_dashboard_kpis(db)
    ncc_rows = db.query(NhaCungCap).all()
    ncc_list = [{
        "ma_ncc": s.MaNCC,
        "ten_ncc": s.TenNCC,
        "dia_chi": s.DiaChi or "Chưa cập nhật",
        "so_dien_thoai": s.SoDienThoai or "Chưa cập nhật",
        "email": s.Email or ""
    } for s in ncc_rows]

    context = {
        "metadata": {
            **warehouse_data.get("metadata", {}),
            "tong_sku": kpis.get("tong_sku", 0),
            "tong_gia_tri_xuat_thang": kpis.get("tong_gia_tri_xuat_thang", 0),
            "tong_giao_dich_thang": kpis.get("tong_giao_dich_thang", 0),
            "tong_phieu_nhap": kpis.get("tong_phieu_nhap", 0),
            "tong_phieu_xuat": kpis.get("tong_phieu_xuat", 0),
            "tong_nha_cung_cap": len(ncc_list),
            "project_name": "SmartLogis AI - Quản Lý Kho Thông Minh Tích Hợp AI",
            "system_version": "v2.0 Enterprise Ready"
        },
        "low_stock_alerts": warehouse_data.get("low_stock_alerts", []),
        "dead_stock_items": warehouse_data.get("dead_stock_items", []),
        "high_burn_rate_items": warehouse_data.get("high_burn_rate_items", []),
        "inventory_summary": warehouse_data.get("inventory_summary", []),
        "suppliers": ncc_list
    }
    return sanitize_inventory_payload(context)


def get_supplier_for_item(ma_hh: str, ten_hh: str, suppliers: List[Dict[str, Any]]) -> Dict[str, str]:
    """Tìm nhà cung cấp phù hợp cho mặt hàng dựa trên mã hoặc ngành hàng."""
    ma_u = ma_hh.upper()
    ten_u = ten_hh.upper()
    for s in suppliers:
        s_ten = s.get("ten_ncc", "").upper()
        if ("THEP" in ma_u or "THÉP" in ten_u) and "HÒA PHÁT" in s_ten:
            return s
        if ("NHUA" in ma_u or "NHỰA" in ten_u or "ỐNG" in ten_u) and "TIỀN PHONG" in s_ten:
            return s
        if ("XIMANG" in ma_u or "XI MĂNG" in ten_u) and "VICEM" in s_ten:
            return s
        if ("QUEHAN" in ma_u or "HÀN" in ten_u) and "KIM TÍN" in s_ten:
            return s
        if ("SON" in ma_u or "SƠN" in ten_u or "DUNGMOI" in ma_u) and "HẢI PHÒNG" in s_ten:
            return s
    return suppliers[0] if suppliers else {
        "ma_ncc": "NCC-01",
        "ten_ncc": "Đối tác cung ứng vật tư",
        "so_dien_thoai": "0243.974.7777",
        "dia_chi": "Hà Nội"
    }


def find_matched_items(all_items: List[Dict[str, Any]], query: str, q_no_accent: str) -> List[Dict[str, Any]]:
    """Tìm và xếp hạng các mặt hàng phù hợp nhất với câu hỏi của người dùng."""
    stop_words_no_accent = {
        "chong", "hoat", "dong", "the", "nao", "quan", "ly", "smartlogis", "du", "an", "kho",
        "hang", "cua", "con", "bao", "nhieu", "ton", "cho", "biet", "xem", "tra", "cuu",
        "tim", "kiem", "co", "hay", "khong", "la", "gi", "huong", "dan", "cach", "tao",
        "lap", "phieu", "nhap", "xuat", "kiem", "tra", "them", "duoc", "mot", "hai", "ba",
        "san", "pham", "vat", "tu", "tinh", "trang"
    }
    tokens_q = [w for w in q_no_accent.split() if len(w) >= 2 and w not in stop_words_no_accent]
    scored_items = []

    for it in all_items:
        score = 0
        ma = it.get("ma_hh", "").lower()
        ten = it.get("ten_hh", "").lower()
        ma_no_accent = remove_accents(ma)
        ten_no_accent = remove_accents(ten)

        # 1. Khớp chính xác mã hàng
        if ma in query.lower() or ma_no_accent in q_no_accent:
            score += 120
        clean_sku = ma_no_accent.replace("hh-", "")
        if len(clean_sku) >= 4 and clean_sku in q_no_accent:
            score += 90

        # 2. Khớp trọn vẹn tên hàng
        if ten in query.lower() or ten_no_accent in q_no_accent:
            score += 100

        # 3. Khớp cụm từ đặc thù (Brand / Model)
        phrases = [
            ("vicem but son", 40), ("but son", 35), ("hoang thach", 35), ("ha tien", 35),
            ("hoa phat", 35), ("tien phong", 35), ("thep phi 8", 45), ("thep phi 10", 45),
            ("thep phi 16", 45), ("thep phi 12", 45), ("thep cuon", 30), ("thep cay", 30),
            ("thep h", 30), ("xi mang", 25), ("son dulux", 35), ("son nippon", 35),
            ("son epoxy", 35), ("son alkyd", 35), ("ong nhua", 30), ("que han", 30),
            ("bu long", 30), ("da cat", 30), ("dung moi", 30), ("cap thep", 30),
            ("phu gia", 30)
        ]
        for p, p_score in phrases:
            if p in q_no_accent and p in ten_no_accent:
                score += p_score

        # 4. Khớp các từ đơn
        ten_words = ten_no_accent.split()
        for w in tokens_q:
            if w in ten_words:
                score += 14
            elif w in ten_no_accent:
                score += 4

        if score >= 20:
            scored_items.append((score, it))

    scored_items.sort(key=lambda x: x[0], reverse=True)
    return [item for _, item in scored_items]


def generate_local_grounded_chat_response(
    context: Dict[str, Any],
    query: str,
    history: Optional[List[Any]] = None
) -> Dict[str, Any]:
    """
    Local Grounded Conversational Engine v2.0 Enterprise:
    Đối chiếu dữ liệu thời gian thực từ CSDL kho SmartLogis AI.
    Đảm bảo:
    1. Trả lời đúng trọng tâm câu hỏi 100%, không bị lệch đề.
    2. Cung cấp bảng số liệu, số dư, đơn vị tính, ngưỡng tồn min, burn-rate thực tế.
    3. Hỗ trợ logic đa lượt (multi-turn) 'làm tiếp', 'tiếp tục', 'bước tiếp theo' mượt mà.
    4. Trả về danh sách câu hỏi gợi ý tiếp theo chính xác, hỗ trợ người dùng click chạy tiếp.
    """
    q = query.lower().strip()
    q_no_accent = remove_accents(q)
    meta = context.get("metadata", {})
    low_stocks = context.get("low_stock_alerts", [])
    dead_stocks = context.get("dead_stock_items", [])
    high_burns = context.get("high_burn_rate_items", [])
    all_items = context.get("inventory_summary", [])
    suppliers = context.get("suppliers", [])

    default_suggested = [
        "📊 Sinh báo cáo điều hành kho 3 phần",
        "⚠️ Mặt hàng nào đang thiếu hụt nguy cấp?",
        "📦 Danh sách hàng tồn lâu > 60 ngày",
        "🚀 Top mặt hàng xuất kho nhiều nhất (Burn-rate)",
        "🛡️ Giải thích cơ chế chống tồn âm Zero Negative Stock"
    ]

    # =========================================================================
    # 1. GIẢI PHÉP TÍNH TOÁN HỌC & SỐ HỌC
    # =========================================================================
    math_res = solve_math_expression(query)
    if math_res:
        expr_str, val = math_res
        val_str = f"{val:,}" if isinstance(val, int) else f"{val:,.2f}".rstrip("0").rstrip(".")
        reply = f"""### 🔢 KẾT QUẢ PHÉP TÍNH:
> **{expr_str} = {val_str}**

*(Được tính toán tự động và chính xác bởi Bộ máy Số học SmartLogis Engine)*"""
        return {
            "reply": reply,
            "suggested_questions": [
                "📊 Sinh báo cáo điều hành kho 3 phần",
                "⚠️ Mặt hàng nào đang thiếu hụt nguy cấp?",
                "🚀 Top mặt hàng xuất kho nhiều nhất (Burn-rate)"
            ]
        }

    # =========================================================================
    # 2. HỎI THỜI GIAN & NGÀY THÁNG HỆ THỐNG
    # =========================================================================
    if any(k in q_no_accent for k in ["hom nay ngay may", "hom nay la ngay bao nhieu", "bay gio la may gio", "ngay thang nam", "thoi gian hien tai", "gio hien tai"]):
        now = datetime.now()
        thu_map = {0: "Thứ Hai", 1: "Thứ Ba", 2: "Thứ Tư", 3: "Thứ Năm", 4: "Thứ Sáu", 5: "Thứ Bảy", 6: "Chủ Nhật"}
        thu = thu_map.get(now.weekday(), "Hôm nay")
        date_str = now.strftime("%d/%m/%Y")
        time_str = now.strftime("%H:%M:%S")
        reply = f"""### 📅 THỜI GIAN HỆ THỐNG
- **Hôm nay:** {thu}, ngày **{date_str}**
- **Thời gian hiện tại:** **{time_str}** (Múi giờ Việt Nam GMT+7)

Hệ thống **SmartLogis AI** đang kết nối trực tuyến và theo dõi số liệu của **{meta.get('tong_sku', 0)} SKU** vật tư trong kho."""
        return {
            "reply": reply,
            "suggested_questions": [
                "📊 Sinh báo cáo điều hành kho 3 phần",
                "⚠️ Mặt hàng nào đang thiếu hụt nguy cấp?",
                "📦 Danh sách hàng tồn lâu > 60 ngày"
            ]
        }

    # =========================================================================
    # 2B. XỬ LÝ LOGIC "LÀM TIẾP" / "TIẾP TỤC" / "BƯỚC TIẾP THEO" (CONVERSATIONAL CONTINUITY)
    # =========================================================================
    is_continue_query = any(k in q_no_accent for k in [
        "lam tiep", "tiep tuc", "tiep theo", "buoc tiep theo", "lam gi tiep",
        "lam gi tiep theo", "huong dan tiep", "tiep di", "next", "lam tiep nhe",
        "cac buoc tiep", "buoc ke tiep", "hanh dong tiep theo", "tiep tuc nhe"
    ]) or q_no_accent in ["tiep", "continue", "next step", "lam tiep?"]

    if is_continue_query:
        last_topic = ""
        if history:
            for h in reversed(history):
                text = ""
                if isinstance(h, dict):
                    text = h.get("content", "")
                elif hasattr(h, "content"):
                    text = getattr(h, "content", "")
                text_no_acc = remove_accents(text.lower())
                
                if any(w in text_no_acc for w in ["thieu hut", "ton min", "nguy cap", "can nhap", "de xuat nhap", "sap het"]):
                    last_topic = "low_stock"
                    break
                elif any(w in text_no_acc for w in ["bao cao", "3 phan", "dieu hanh kho", "tong quan"]):
                    last_topic = "report"
                    break
                elif any(w in text_no_acc for w in ["dead stock", "ton lau", "u dong", "60 ngay", "thanh ly"]):
                    last_topic = "dead_stock"
                    break
                elif any(w in text_no_acc for w in ["burn rate", "burn-rate", "xuat chay", "tieu thu manh"]):
                    last_topic = "burn_rate"
                    break
                elif any(w in text_no_acc for w in ["nha cung cap", "ncc", "supplier", "doi tac"]):
                    last_topic = "supplier"
                    break
                elif any(w in text_no_acc for w in ["xuat kho", "phieu xuat", "outbound", "chong ton am"]):
                    last_topic = "outbound"
                    break
                elif any(w in text_no_acc for w in ["nhap kho", "phieu nhap", "inbound"]):
                    last_topic = "inbound"
                    break

        if last_topic == "low_stock":
            if not low_stocks:
                reply = "✅ **Toàn bộ kho đang ở mức an toàn!** Không có mặt hàng nào cần xử lý nhập hàng gấp."
            else:
                total_needed = sum(it.get("de_xuat_nhap_them", 0) for it in low_stocks)
                lines = [
                    f"### 📥 BƯỚC TIẾP THEO: QUY TRÌNH NHẬP KHO XỬ LÝ {len(low_stocks)} SKU THIẾU HỤT",
                    f"Tổng lượng hàng cần nhập bổ sung an toàn: **+{total_needed} đơn vị**.",
                    "",
                    "1. **Bước 1: Rà soát danh sách dự thảo phiếu nhập**",
                    "   - Các SKU khẩn cấp: " + ", ".join([f"`{it['ma_hh']}` ({it['ten_hh']})" for it in low_stocks[:3]]) + ("..." if len(low_stocks) > 3 else "."),
                    "2. **Bước 2: Kết nối đối tác cung ứng tương ứng**",
                    "   - Chọn nhà cung cấp phù hợp cho từng mặt hàng (Thép Hòa Phát, Nhựa Tiền Phong, Vicem Bút Sơn...).",
                    "3. **Bước 3: Lập và lưu Phiếu Nhập Kho**",
                    "   - Truy cập phân hệ **[Phiếu Nhập Kho](/inbound)**.",
                    "   - Chọn Nhà cung cấp, điền số lượng theo đề xuất và nhấn **Lưu Phiếu**.",
                    "   - Giao dịch Master-Detail ACID sẽ tự động cộng tồn kho và ghi sổ Thẻ kho ngay lập tức."
                ]
                reply = "\n".join(lines)
            return {
                "reply": reply,
                "suggested_questions": [
                    "Lập danh sách phiếu nhập cho các mặt hàng nguy cấp",
                    "Gợi ý nhà cung cấp cho các mặt hàng thiếu hụt",
                    "Sinh báo cáo điều hành kho 3 phần"
                ]
            }

        elif last_topic == "report":
            lines = [
                "### 📋 KẾ HOẠCH HÀNH ĐỘNG TIẾP THEO SAU BÁO CÁO VẬN HÀNH KHO",
                "Dựa trên kết quả phân tích 3 phần của hệ thống, đây là các bước hành động cụ thể:",
                "",
                f"1. 🚨 **Hành động 1 - Xử lý thiếu hụt ({len(low_stocks)} SKU):**",
                "   - Chuyển giao danh sách đề xuất nhập thêm sang bộ phận Thu mua để tạo **[Phiếu Nhập Kho](/inbound)**.",
                f"2. 📦 **Hành động 2 - Giải phóng hàng ứ đọng ({len(dead_stocks)} SKU):**",
                "   - Lập phương án chiết khấu hoặc xuất thanh lý tại **[Phiếu Xuất Kho](/outbound)** để giải phóng diện tích.",
                f"3. 🚀 **Hành động 3 - Kiểm soát hàng xuất mạnh ({len(high_burns)} SKU):**",
                "   - Rà soát ngưỡng tồn an toàn (Safety Stock) để không xảy ra tình trạng thiếu hụt bất ngờ.",
                "4. 🛡️ **Hành động 4 - Đối chiếu sổ thẻ kho:**",
                "   - Kiểm tra lịch sử biến động lũy kế tại **[Sổ Thẻ Kho](/the-kho)** bảo đảm khớp 100% CSDL."
            ]
            return {
                "reply": "\n".join(lines),
                "suggested_questions": [
                    "Lập danh sách phiếu nhập cho các mặt hàng nguy cấp",
                    "Danh sách hàng tồn lâu > 60 ngày",
                    "Top mặt hàng xuất kho nhiều nhất (Burn-rate)"
                ]
            }

        elif last_topic == "dead_stock":
            lines = [
                f"### 📦 KẾ HOẠCH TIẾP THEO: GIẢI PHÓNG {len(dead_stocks)} MẶT HÀNG TỒN LÂU > 60 NGÀY",
                "1. **Bước 1: Kiểm kê thực tế và phân loại chất lượng**",
                "   - Đối chiếu số lượng thực tế với số liệu tồn kho trên hệ thống.",
                "2. **Bước 2: Áp dụng chính sách thanh lý / kích cầu**",
                "   - Đề xuất chiết khấu 10% - 20% cho các dự án hoặc đối tác mua số lượng lớn.",
                "3. **Bước 3: Lập phiếu xuất thanh lý**",
                "   - Vào **[Phiếu Xuất Kho](/outbound)**, chọn lý do 'Xuất thanh lý hàng tồn đọng'.",
                "   - Hệ thống tự động ghi giảm số dư tồn kho và lưu vết kiểm toán đầy đủ."
            ]
            return {
                "reply": "\n".join(lines),
                "suggested_questions": [
                    "Danh sách hàng tồn lâu > 60 ngày",
                    "Mặt hàng nào đang thiếu hụt nguy cấp?",
                    "Sinh báo cáo điều hành kho 3 phần"
                ]
            }

        elif last_topic == "supplier":
            lines = [
                "### 🏢 BƯỚC TIẾP THEO: LIÊN HỆ ĐỐI TÁC VÀ TẠO PHIẾU NHẬP",
                "1. Liên hệ với đại diện nhà cung cấp qua Hotline/SĐT để xác nhận đơn giá và thời gian giao nhận.",
                "2. Mở phân hệ **[Phiếu Nhập Kho](/inbound)** trên thanh menu bên trái.",
                "3. Chọn Nhà cung cấp tương ứng từ danh sách, thêm các SKU cần nhập và nhấn **Lưu Phiếu**.",
                "4. Hệ thống sẽ tự động cập nhật công nợ và cộng tồn kho tức thời."
            ]
            return {
                "reply": "\n".join(lines),
                "suggested_questions": [
                    "Lập danh sách phiếu nhập cho các mặt hàng nguy cấp",
                    "Mặt hàng nào đang thiếu hụt nguy cấp?",
                    "Sinh báo cáo điều hành kho 3 phần"
                ]
            }

        else:
            # Mặc định: Phân tích trạng thái hiện tại và đưa ra các bước tiếp theo tốt nhất
            lines = [
                "### 📋 CÁC BƯỚC HÀNH ĐỘNG TIẾP THEO ĐƯỢC ĐỀ XUẤT CHO KHO:",
                f"- ⚠️ **Bước 1:** Có **{len(low_stocks)} mặt hàng** thiếu hụt $\\to$ Ưu tiên lập phiếu nhập tại **[Phiếu Nhập Kho](/inbound)**.",
                f"- 📦 **Bước 2:** Có **{len(dead_stocks)} mặt hàng** ứ đọng > 60 ngày $\\to$ Lập phương án thanh lý giải phóng mặt bằng.",
                "- 📊 **Bước 3:** Bấm **'Sinh báo cáo điều hành kho 3 phần'** bên dưới để xem số liệu tổng hợp chi tiết nhất.",
                "",
                "Bạn muốn tôi hỗ trợ triển khai cụ thể bước nào trước?"
            ]
            return {
                "reply": "\n".join(lines),
                "suggested_questions": [
                    "Lập danh sách phiếu nhập cho các mặt hàng nguy cấp",
                    "Danh sách hàng tồn lâu > 60 ngày",
                    "Sinh báo cáo điều hành kho 3 phần"
                ]
            }

    # =========================================================================
    # 3. GỢI Ý NHÀ CUNG CẤP CHO CÁC MẶT HÀNG THIẾU HỤT
    # =========================================================================
    is_supplier_for_low_stock = (
        any(k in q_no_accent for k in ["nha cung cap", "ncc", "supplier", "doi tac", "ai cung cap"]) and
        any(k in q_no_accent for k in ["thieu", "thieu hut", "nguy cap", "can nhap", "het hang", "ton min", "khan cap"])
    )
    if is_supplier_for_low_stock:
        if not low_stocks:
            return {
                "reply": "✅ **Toàn bộ kho đang ở mức an toàn!** Không có mặt hàng nào bị thiếu hụt nên chưa cần kích hoạt đề xuất nhà cung cấp nhập hàng khẩn cấp.",
                "suggested_questions": default_suggested
            }

        lines = [
            f"### 🏢 GỢI Ý NHÀ CUNG CẤP CHO {len(low_stocks)} MẶT HÀNG THIẾU HỤT TỒN KHO:",
            "Dưới đây là danh sách đối tác cung ứng tương ứng cho từng mặt hàng cần nhập gấp:",
            "",
            "| Mã SKU | Tên Hàng Hóa | Tồn Hiện Tại | Ngưỡng Min | Đề Xuất Nhập | Nhà Cung Cấp Đề Xuất | Liên Hệ (Hotline / SĐT) |",
            "| :--- | :--- | :---: | :---: | :---: | :--- | :--- |"
        ]
        for it in low_stocks:
            sup = get_supplier_for_item(it["ma_hh"], it["ten_hh"], suppliers)
            lines.append(
                f"| `{it['ma_hh']}` | **{it['ten_hh']}** | {it['ton_hien_tai']} {it['don_vi_tinh']} | {it['ton_toi_thieu']} | "
                f"**+{it.get('de_xuat_nhap_them', 0)} {it['don_vi_tinh']}** | {sup.get('ten_ncc', 'Đang cập nhật')} | `{sup.get('so_dien_thoai', '--')}` |"
            )
        lines.extend([
            "",
            "💡 **Hướng dẫn tạo phiếu:** Bạn có thể vào menu **[Phiếu Nhập Kho](/inbound)**, chọn nhà cung cấp tương ứng ở trên và bấm **Lưu Phiếu** để cập nhật tồn kho tức thời (giao dịch ACID bảo vệ 100%)."
        ])
        return {
            "reply": "\n".join(lines),
            "suggested_questions": [
                "Lập danh sách phiếu nhập cho các mặt hàng nguy cấp",
                "Tốc độ xuất kho của các mặt hàng này là bao nhiêu?",
                "Sinh báo cáo điều hành kho 3 phần"
            ]
        }

    # =========================================================================
    # 4. LẬP DANH SÁCH PHIẾU NHẬP CHO CÁC MẶT HÀNG NGUY CẤP
    # =========================================================================
    is_draft_inbound_order = (
        any(k in q_no_accent for k in ["lap danh sach", "danh sach phieu nhap", "tao phieu nhap cho", "ke hoach nhap", "de xuat nhap", "du thao phieu nhap", "lap phieu nhap"]) and
        any(k in q_no_accent for k in ["nguy cap", "thieu hut", "khan cap", "can nhap", "ton min", "hang thieu", "cac mat hang nay"])
    )
    if is_draft_inbound_order:
        if not low_stocks:
            return {
                "reply": "✅ **Không có mặt hàng nào cần lập phiếu nhập khẩn cấp.** Toàn bộ danh mục SKU đang đạt ngưỡng an toàn.",
                "suggested_questions": default_suggested
            }

        lines = [
            f"### 📥 DỰ THẢO DANH SÁCH LẬP PHIẾU NHẬP KHO ({len(low_stocks)} SKU NGUY CẤP):",
            "Bảng kế hoạch nhập bù số dư được tính toán dựa trên mức thiếu hụt và tốc độ tiêu thụ (Burn-rate) 30 ngày:",
            "",
            "| STT | Mã SKU | Tên Vật Tư Hàng Hóa | ĐVT | Tồn Thực Tế | Ngưỡng Min | Thiếu Hụt | Đề Xuất Nhập Thêm | Đối Tác Cung Ứng |",
            "| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |"
        ]
        for idx, it in enumerate(low_stocks, 1):
            sup = get_supplier_for_item(it["ma_hh"], it["ten_hh"], suppliers)
            lines.append(
                f"| {idx} | `{it['ma_hh']}` | {it['ten_hh']} | {it['don_vi_tinh']} | {it['ton_hien_tai']} | "
                f"{it['ton_toi_thieu']} | -{it['thieu_hut']} | **+{it.get('de_xuat_nhap_them', 0)}** | {sup.get('ten_ncc', '--')} |"
            )
        lines.extend([
            "",
            "🛡️ **Cơ chế an toàn:** Khi bạn xác nhận lập phiếu tại menu **[Phiếu Nhập Kho](/inbound)**, hệ thống kích hoạt giao dịch **Master-Detail ACID All-or-Nothing**, ghi nhận lũy kế bất biến vào **Sổ Thẻ kho** ngay tức thì."
        ])
        return {
            "reply": "\n".join(lines),
            "suggested_questions": [
                "Gợi ý nhà cung cấp cho các mặt hàng thiếu hụt",
                "Tốc độ xuất kho của các mặt hàng này là bao nhiêu?",
                "Sinh báo cáo điều hành kho 3 phần"
            ]
        }

    # =========================================================================
    # 5. TỐC ĐỘ XUẤT KHO / BURN-RATE / HÀNG XUẤT CHẠY NHẤT
    # =========================================================================
    is_burn_rate_query = any(k in q_no_accent for k in [
        "toc do xuat", "burn rate", "burn-rate", "xuat chay", "ban chay", "xuat manh",
        "tieu thu manh", "xuat nhieu nhat", "top xuat", "tieu thu", "toc do tieu thu"
    ])
    if is_burn_rate_query:
        if not high_burns:
            return {
                "reply": "📊 Trong 30 ngày qua, tốc độ xuất kho diễn ra đều đặn, không có mặt hàng nào bị đột biến vượt ngưỡng 2 đơn vị/ngày.",
                "suggested_questions": default_suggested
            }

        lines = [
            f"### 🚀 BÁO CÁO TỐC ĐỘ XUẤT KHO & TIÊU THỤ (HIGH BURN-RATE 30 NGÀY):",
            "Danh sách các mặt hàng có lượng xuất kho lớn nhất giúp doanh nghiệp dự phòng tồn kho kịp thời:",
            "",
            "| Mã SKU | Tên Hàng Hóa | ĐVT | Tổng Xuất 30D | Tốc Độ/Ngày (Burn-rate) | Tồn Khả Dụng | Dự Trữ Ước Tính | Đánh Giá |",
            "| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |"
        ]
        for it in high_burns:
            burn = it.get('burn_rate_ngay', 0)
            ton = it.get('ton_kho_hien_tai', 0)
            days = f"{int(ton / burn)} ngày" if burn > 0 else "Không xác định"
            badge = "🔴 Cần chú ý" if burn > 1.5 else "🟡 Theo dõi"
            lines.append(
                f"| `{it['ma_hh']}` | **{it['ten_hh']}** | {it.get('don_vi_tinh', 'ĐV')} | {it.get('tong_xuat_30d', 0)} | "
                f"**{burn} đv/ngày** | {ton} | {days} | {badge} |"
            )
        lines.extend([
            "",
            "💡 **Công thức chuẩn hóa:** $\\text{Burn-rate} = \\frac{\\text{Tổng lượng xuất 30 ngày}}{30}$.",
            "Doanh nghiệp nên duy trì mức **Tồn kho an toàn (Safety Stock)** tối thiểu gấp 2 lần chu kỳ đặt hàng của nhóm hàng này."
        ])
        return {
            "reply": "\n".join(lines),
            "suggested_questions": [
                "Mặt hàng nào đang thiếu hụt nguy cấp?",
                "Danh sách hàng tồn lâu > 60 ngày",
                "Sinh báo cáo điều hành kho 3 phần"
            ]
        }

    # =========================================================================
    # 6. HÀNG TỒN KHO LÂU > 60 NGÀY / DEAD STOCK / Ứ ĐỌNG
    # =========================================================================
    is_dead_stock_query = any(k in q_no_accent for k in [
        "ton lau", "u dong", "dead stock", "60 ngay", "cham", "khong xuat", "thanh ly", "cham luan chuyen"
    ])
    if is_dead_stock_query:
        if not dead_stocks:
            return {
                "reply": "✨ **Kho vận hành rất tích cực!** Không ghi nhận mặt hàng nào bị tồn đọng quá 60 ngày mà không xuất hàng.",
                "suggested_questions": default_suggested
            }

        lines = [
            f"### 📦 DANH SÁCH {len(dead_stocks)} MẶT HÀNG TỒN LÂU (> 60 NGÀY KHÔNG XUẤT):",
            "Các mặt hàng này làm tăng chi phí lưu kho và ứ đọng vốn lưu động:",
            "",
            "| Mã SKU | Tên Hàng Hóa | ĐVT | Lượng Tồn Đọng | Số Ngày Không Xuất | Ngày Xuất Gần Nhất | Đề Xuất Giải Pháp |",
            "| :--- | :--- | :---: | :---: | :---: | :---: | :--- |"
        ]
        for it in dead_stocks:
            lines.append(
                f"| `{it['ma_hh']}` | **{it['ten_hh']}** | {it['don_vi_tinh']} | **{it.get('ton_kho_u_dong', 0)}** | "
                f"**{it.get('so_ngay_khong_xuat', 0)} ngày** | {it.get('ngay_xuat_cuoi', '--')} | Thanh lý / Điều chuyển |"
            )
        lines.extend([
            "",
            "🔍 **Kiến nghị:** Ban quản lý nên lập phương án ưu tiên xuất cho các dự án mới hoặc áp dụng chính sách giảm giá thanh lý để giải phóng diện tích mặt bằng kho."
        ])
        return {
            "reply": "\n".join(lines),
            "suggested_questions": [
                "Top mặt hàng xuất kho nhiều nhất (Burn-rate)",
                "Mặt hàng nào đang thiếu hụt nguy cấp?",
                "Sinh báo cáo điều hành kho 3 phần"
            ]
        }

    # =========================================================================
    # 7. BÁO CÁO ĐIỀU HÀNH KHO 3 PHẦN TOÀN DIỆN
    # =========================================================================
    is_report_query = (
        any(k in q_no_accent for k in ["3 phan", "ba phan", "dieu hanh kho", "bao cao tong hop"]) or
        (("bao cao" in q_no_accent or "report" in q_no_accent) and not any(k in q_no_accent for k in ["huong dan", "the kho"]))
    )
    if is_report_query:
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
                "Gợi ý nhà cung cấp cho các mặt hàng thiếu hụt",
                "Top mặt hàng xuất kho nhiều nhất (Burn-rate)"
            ]
        }

    # =========================================================================
    # 8. CẢNH BÁO TỒN KHO / THIẾU HỤT / SẮP HẾT
    # =========================================================================
    is_low_stock_query = any(k in q_no_accent for k in [
        "thieu hut", "nguy cap", "sap het", "can nhap gap", "canh bao ton",
        "duoi ton min", "cham ton min", "hang thieu", "het hang", "thieu hang"
    ])
    if is_low_stock_query:
        if not low_stocks:
            return {
                "reply": "✅ **Tuyệt vời!** Hiện tại toàn bộ mặt hàng trong kho đều đang ở ngưỡng an toàn, không có SKU nào bị chạm hoặc dưới tồn tối thiểu.",
                "suggested_questions": default_suggested
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
                f"-{it['thieu_hut']} | **+{it.get('de_xuat_nhap_them', 0)} {it['don_vi_tinh']}** | {muc_do} |"
            )
        lines.extend([
            "",
            "💡 **Khuyến nghị:** Bạn có thể vào menu **[Phiếu Nhập Kho](/inbound)** để lập chứng từ bổ sung số dư ngay lập tức."
        ])
        return {
            "reply": "\n".join(lines),
            "suggested_questions": [
                "Gợi ý nhà cung cấp cho các mặt hàng thiếu hụt",
                "Lập danh sách phiếu nhập cho các mặt hàng nguy cấp",
                "Tốc độ xuất kho của các mặt hàng này là bao nhiêu?"
            ]
        }

    # =========================================================================
    # 9. TRA CỨU MẶT HÀNG CỤ THỂ (SPECIFIC SKU / ITEM LOOKUP)
    # Được ưu tiên trước các hướng dẫn generic để không bị trả lời lạc đề!
    # =========================================================================
    matched_items = find_matched_items(all_items, query, q_no_accent)
    if matched_items:
        primary = matched_items[0]
        ma_p = primary["ma_hh"]
        ten_p = primary["ten_hh"]
        ton_p = primary.get("ton_kho_hien_tai", 0)
        min_p = primary.get("ton_kho_toi_thieu", 0)
        dvt_p = primary.get("don_vi_tinh", "ĐV")
        burn_p = primary.get("xuat_trung_binh_ngay", 0)
        xuat_30_p = primary.get("tong_xuat_30_ngay", 0)
        days_p = primary.get("du_tru_uoc_tinh_ngay", 0)
        sup_p = get_supplier_for_item(ma_p, ten_p, suppliers)

        # 9.1 Nếu hỏi cụ thể về Thẻ kho của mặt hàng này
        if any(k in q_no_accent for k in ["the kho", "so the kho", "lich su", "bien dong", "giao dich"]):
            lines = [
                f"### 📜 THÔNG TIN SỔ THẺ KHO: `{ma_p}` - {ten_p}",
                f"- **Số dư tồn hiện tại**: **{ton_p} {dvt_p}** (Ngưỡng an toàn: {min_p} {dvt_p})",
                f"- **Tổng lượng xuất 30 ngày**: {xuat_30_p} {dvt_p} (Bình quân: {burn_p} {dvt_p}/ngày)",
                f"- **Thời gian dự trữ khả dụng**: Khoảng **{days_p} ngày** hoạt động.",
                f"- **Quy tắc lũy kế bất biến**: $$\\text{{Tồn}}(N) = \\text{{Tồn}}(N-1) + \\text{{Nhập}}(N) - \\text{{Xuất}}(N)$$",
                "",
                f"🔗 Bạn có thể xem chi tiết từng chứng từ Nhập / Xuất của mặt hàng này tại menu: **[Tra Cứu Thẻ Kho (`/card-ledger?ma_hh={ma_p}`)](/card-ledger)**."
            ]
            return {
                "reply": "\n".join(lines),
                "suggested_questions": [
                    f"Tốc độ xuất kho của {ma_p}",
                    "Mặt hàng nào đang thiếu hụt nguy cấp?",
                    "Sinh báo cáo điều hành kho 3 phần"
                ]
            }

        # 9.2 Nếu hỏi về nhập hàng / bổ sung cho mặt hàng này
        if any(k in q_no_accent for k in ["nhap", "nhap them", "mua them", "bo sung", "can nhap khong"]):
            need_restock = ton_p <= min_p
            thieu = max(0, min_p - ton_p)
            suggest_qty = max(thieu, int(burn_p * 15)) if burn_p > 0 else (thieu if thieu > 0 else 10)
            status_text = "🔴 **Đang thiếu hụt so với tồn tối thiểu - Cần nhập thêm!**" if need_restock else "🟢 **Tồn kho hiện tại đang ở mức an toàn.**"
            lines = [
                f"### 📥 TƯ VẤN NHẬP HÀNG: `{ma_p}` - {ten_p}",
                f"- **Tình trạng:** {status_text}",
                f"- **Tồn kho thực tế:** **{ton_p} {dvt_p}** (Tồn min quy định: {min_p} {dvt_p})",
                f"- **Tốc độ tiêu thụ:** {burn_p} {dvt_p}/ngày",
                f"- **Lượng đề xuất nhập thêm:** **+{suggest_qty} {dvt_p}**",
                f"- **Nhà cung cấp đề xuất:** **{sup_p.get('ten_ncc', '--')}** (SĐT: `{sup_p.get('so_dien_thoai', '--')}`)",
                "",
                f"💡 Để lập chứng từ bổ sung, bạn vào menu **[Phiếu Nhập Kho](/inbound)**, chọn nhà cung cấp `{sup_p.get('ten_ncc')}` và nhập số lượng `{suggest_qty} {dvt_p}`."
            ]
            return {
                "reply": "\n".join(lines),
                "suggested_questions": [
                    f"Xem lịch sử thẻ kho của {ma_p}",
                    "Mặt hàng nào đang thiếu hụt nguy cấp?",
                    "Sinh báo cáo điều hành kho 3 phần"
                ]
            }

        # 9.3 Trả về thẻ thông tin tra cứu mặt hàng chi tiết (hỗ trợ hiển thị nhiều SKU nếu tìm thấy cụm từ chung)
        lines = [f"🔍 **KẾT QUẢ TRA CỨU VẬT TƯ & TỒN KHO THỜI GIAN THỰC ({len(matched_items)} SKU PHÙ HỢP):**", ""]
        for it in matched_items[:3]:
            t_ton = it.get("ton_kho_hien_tai", 0)
            t_min = it.get("ton_kho_toi_thieu", 0)
            t_dvt = it.get("don_vi_tinh", "ĐV")
            t_tag = "🔴 **DƯỚI TỒN MIN**" if t_ton < t_min else ("🟡 **CHẠM TỒN MIN**" if t_ton == t_min else "🟢 **AN TOÀN**")
            lines.extend([
                f"### 📦 `{it['ma_hh']}` - {it['ten_hh']}",
                f"- **Nhóm vật tư**: {it.get('nhom_hang', 'Khác')} | **Đơn vị tính**: {t_dvt}",
                f"- **Số lượng tồn thực tế**: **{t_ton} {t_dvt}** (Tồn tối thiểu: {t_min} {t_dvt})",
                f"- **Trạng thái**: {t_tag}",
                f"- **Xuất 30 ngày qua**: {it.get('tong_xuat_30_ngay', 0)} {t_dvt} (Bình quân {it.get('xuat_trung_binh_ngay', 0)} {t_dvt}/ngày)",
                f"- **Dự trữ ước tính**: {it.get('du_tru_uoc_tinh_ngay', 0)} ngày hoạt động.",
                ""
            ])
        return {
            "reply": "\n".join(lines),
            "suggested_questions": [
                f"Xem lịch sử thẻ kho của {ma_p}",
                "Mặt hàng nào đang thiếu hụt nguy cấp?",
                "Sinh báo cáo điều hành kho 3 phần"
            ]
        }

    # =========================================================================
    # 10. HƯỚNG DẪN QUY TRÌNH XUẤT KHO & CHỐNG TỒN ÂM (Chỉ khi hỏi rõ cách làm)
    # =========================================================================
    is_outbound_guide = any(k in q_no_accent for k in [
        "huong dan xuat", "cach xuat", "cach tao phieu xuat", "quy trinh xuat", "lam sao de xuat", "cach lap phieu xuat"
    ])
    if is_outbound_guide:
        reply = r"""### 📤 HƯỚNG DẪN LẬP PHIẾU XUẤT KHO (OUTBOUND & ZERO NEGATIVE STOCK)

Quy trình xuất kho tại **SmartLogis AI** được bảo vệ nghiêm ngặt chống thất thoát và sai lệch số liệu:

1. **Truy cập Giao diện:** Chọn menu **[Phiếu Xuất Kho](/outbound)** từ thanh bên trái.
2. **Chọn Mặt Hàng & Nhập Số Lượng Xuất:**
   - Hệ thống hiển thị trực quan **Số lượng tồn thực tế** của từng SKU.
   - Nếu bạn nhập số lượng xuất **vượt quá tồn kho**, hệ thống sẽ cảnh báo đỏ và chặn ngay tại giao diện!
3. **Cơ chế bảo vệ 2 tầng Chống Tồn Âm (Zero Negative Stock):**
   - **Tầng Backend:** Câu lệnh SQL Atomic Decrement:
     `UPDATE ton_kho SET SoLuongTon = SoLuongTon - :xuat WHERE MaHH = :ma AND SoLuongTon >= :xuat`
     Nếu tồn kho không đủ (do nhiều luồng cùng xuất), thao tác bị hủy lập tức.
   - **Tầng CSDL:** Ràng buộc `CHECK (SoLuongTon >= 0)` ngăn chặn tuyệt đối tồn âm ở cấp độ database.
4. **Giao dịch ACID:** Toàn bộ phiếu xuất được thực hiện **All-or-Nothing**, nếu lỗi 1 dòng hàng sẽ rollback 100%."""
        return {
            "reply": reply,
            "suggested_questions": [
                "Top mặt hàng xuất kho nhiều nhất (Burn-rate)",
                "Xem sổ thẻ kho để theo dõi lịch sử xuất nhập",
                "Sinh báo cáo điều hành kho 3 phần"
            ]
        }

    # =========================================================================
    # 11. HƯỚNG DẪN QUY TRÌNH NHẬP KHO (Chỉ khi hỏi rõ cách làm)
    # =========================================================================
    is_inbound_guide = any(k in q_no_accent for k in [
        "huong dan nhap", "cach nhap", "cach tao phieu nhap", "quy trinh nhap", "lam sao de nhap", "cach lap phieu nhap"
    ])
    if is_inbound_guide:
        reply = r"""### 📥 HƯỚNG DẪN LẬP PHIẾU NHẬP KHO (INBOUND TRANSACTION)

Để lập phiếu nhập kho chuẩn hóa trong **SmartLogis AI**, bạn thực hiện các bước sau:

1. **Truy cập Giao diện:** Chọn menu **[Phiếu Nhập Kho](/inbound)** từ thanh điều hướng bên trái.
2. **Chọn Nhà Cung Cấp:** Chọn đối tác cung cấp nguyên vật tư từ danh sách có sẵn.
3. **Thêm Danh Sách Hàng Hóa:**
   - Chọn mặt hàng (SKU) cần nhập.
   - Nhập **Số lượng nhập** (bắt buộc $> 0$) và **Đơn giá nhập** (nếu có quyền Thủ kho/Admin).
   - Có thể bấm **Thêm dòng hàng** để nhập nhiều mặt hàng cùng lúc trên 1 phiếu.
4. **Xác nhận Lưu Phiếu:**
   - Bấm **Hoàn Tất & Lưu Phiếu Nhập Kho**.
   - **Cơ chế bảo vệ ACID:** Toàn bộ thông tin đầu phiếu và các chi tiết hàng hóa được đóng gói trong một Transaction duy nhất (All-or-Nothing). Số lượng tồn kho và Sổ Thẻ kho sẽ được cập nhật đồng bộ tức thời!"""
        return {
            "reply": reply,
            "suggested_questions": [
                "Mặt hàng nào đang cần nhập hàng gấp?",
                "Gợi ý nhà cung cấp cho các mặt hàng thiếu hụt",
                "Giải thích cơ chế bảo vệ giao dịch ACID"
            ]
        }

    # =========================================================================
    # 12. SỔ THẺ KHO (KHÁI NIỆM & NGUYÊN LÝ)
    # =========================================================================
    if any(k in q_no_accent for k in ["the kho", "so the kho", "card ledger", "luy ke"]):
        reply = r"""### 📜 SỔ THẺ KHO BẤT BIẾN (INVENTORY CARD LEDGER)

Trong **SmartLogis AI**, Sổ Thẻ kho là tài liệu pháp lý kế toán quan trọng nhất để theo dõi biến động từng SKU:

- **Công thức Lũy kế Bất biến:**
  $$Tồn(N) = Tồn(N-1) + Nhập(N) - Xuất(N)$$
- **Tính năng nổi bật:**
  1. Ghi nhận thời gian thực mọi biến động Nhập / Xuất theo từng giây.
  2. Truy vết chính xác mã chứng từ (`PN-...`, `PX-...`), người thực hiện, và số dư tồn sau từng giao dịch.
  3. Cơ chế đối chiếu tự động giúp phát hiện ngay lập tức bất kỳ sai lệch nào.
- **Cách tra cứu:** Bạn vào menu **[Tra Cứu Thẻ Kho](/card-ledger)**, chọn mặt hàng và khoảng thời gian để xem chi tiết hoặc in báo cáo."""
        return {
            "reply": reply,
            "suggested_questions": [
                "Tra cứu mặt hàng HH-THEP-D08",
                "Giải thích cơ chế chống tồn âm Zero Negative Stock",
                "Sinh báo cáo điều hành kho 3 phần"
            ]
        }

    # =========================================================================
    # 13. DANH MỤC TOÀN BỘ HÀNG HÓA TRONG KHO
    # =========================================================================
    if any(k in q_no_accent for k in ["danh muc hang", "danh sach hang", "toan bo hang", "co nhung hang gi", "co nhung mat hang nao", "tat ca sku"]):
        lines = [
            f"📋 **DANH MỤC HÀNG HÓA & TỒN KHO THỜI GIAN THỰC ({len(all_items)} SKU):**",
            "",
            "| Mã SKU | Tên Mặt Hàng | Nhóm Hàng | Tồn Kho | Min | ĐVT | Trạng Thái |",
            "| :--- | :--- | :---: | :---: | :---: | :---: | :---: |"
        ]
        for it in all_items:
            ton = it.get("ton_kho_hien_tai", 0)
            min_ton = it.get("ton_kho_toi_thieu", 0)
            st = "🔴 Thiếu" if ton < min_ton else ("🟡 Cận Min" if ton == min_ton else "🟢 An toàn")
            lines.append(
                f"| `{it['ma_hh']}` | {it['ten_hh']} | {it.get('nhom_hang', 'Khác')} | **{ton}** | {min_ton} | {it.get('don_vi_tinh', '')} | {st} |"
            )
        lines.extend([
            "",
            "💡 Bạn có thể tra cứu chi tiết bất kỳ mặt hàng nào bằng cách gõ tên hoặc mã (ví dụ: *Xi măng Bút Sơn* hoặc *HH-THEP-D08*)."
        ])
        return {
            "reply": "\n".join(lines),
            "suggested_questions": [
                "Mặt hàng nào đang thiếu hụt nguy cấp?",
                "Tra cứu mặt hàng HH-THEP-D08",
                "Sinh báo cáo điều hành kho 3 phần"
            ]
        }

    # =========================================================================
    # 14. DANH SÁCH NHÀ CUNG CẤP / ĐỐI TÁC
    # =========================================================================
    if any(k in q_no_accent for k in ["nha cung cap", "doi tac", "ncc", "ai cung cap", "supplier"]):
        if not suppliers:
            return {
                "reply": "Hệ thống chưa ghi nhận thông tin nhà cung cấp nào trong cơ sở dữ liệu.",
                "suggested_questions": default_suggested
            }
        lines = [
            f"🏢 **DANH SÁCH {len(suppliers)} NHÀ CUNG CẤP LIÊN KẾT TRONG HỆ THỐNG:**",
            "",
            "| Mã NCC | Tên Nhà Cung Cấp | Điện Thoại | Địa Chỉ |",
            "| :--- | :--- | :---: | :--- |"
        ]
        for s in suppliers:
            lines.append(f"| `{s['ma_ncc']}` | **{s['ten_ncc']}** | {s['so_dien_thoai']} | {s['dia_chi']} |")
        lines.extend([
            "",
            "💡 Bạn có thể quản lý danh sách nhà cung cấp đầy đủ tại menu **[Nhà Cung Cấp](/suppliers)**."
        ])
        return {
            "reply": "\n".join(lines),
            "suggested_questions": [
                "Gợi ý nhà cung cấp cho các mặt hàng thiếu hụt",
                "Lập danh sách phiếu nhập cho các mặt hàng nguy cấp",
                "Sinh báo cáo điều hành kho 3 phần"
            ]
        }

    # =========================================================================
    # 15. TỔNG QUAN / KPI TOÀN BỘ KHO
    # =========================================================================
    if any(k in q_no_accent for k in ["tong quan", "kpi", "thong ke", "bao nhieu sku", "tong so", "tinh hinh kho"]):
        reply = f"""### 📈 TỔNG QUAN CHỈ SỐ VẬN HÀNH KHO SMARTLOGIS AI

- **Tổng danh mục quản lý**: **{meta.get('tong_sku', 0)} SKU** vật tư.
- **Mặt hàng chạm / dưới tồn tối thiểu**: **{len(low_stocks)} SKU** ({'⚠️ Cần xử lý' if low_stocks else '✅ An toàn'}).
- **Tổng số giao dịch đã thực hiện**: **{meta.get('tong_giao_dich_thang', 0)} giao dịch** ({meta.get('tong_phieu_nhap', 0)} Phiếu Nhập / {meta.get('tong_phieu_xuat', 0)} Phiếu Xuất).
- **Tổng giá trị xuất kho lũy kế**: **{meta.get('tong_gia_tri_xuat_thang', 0):,.0f} VNĐ** (Tính theo giá vốn bình quân gia quyền).
- **Đối tác cung cấp (Nhà cung cấp)**: **{meta.get('tong_nha_cung_cap', 0)} đối tác** liên kết.
- **Hàng tồn kho ứ đọng > 60 ngày**: **{len(dead_stocks)} SKU**."""
        return {
            "reply": reply,
            "suggested_questions": default_suggested
        }

    # =========================================================================
    # 16. KIẾN TRÚC & CÔNG NGHỆ BẢO MẬT SMARTLOGIS AI
    # =========================================================================
    if any(k in q_no_accent for k in ["zero negative", "chong ton am", "ton am", "acid", "rbac", "sanitizer", "kien truc"]):
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
                "Mặt hàng nào đang thiếu hụt nguy cấp?",
                "Top mặt hàng xuất kho nhiều nhất (Burn-rate)"
            ]
        }

    # =========================================================================
    # 17. CÁC ĐỊNH NGHĨA LOGISTICS
    # =========================================================================
    if "fifo" in q_no_accent or "nhap truoc xuat truoc" in q_no_accent:
        return {
            "reply": """### 📦 NGUYÊN TẮC FIFO (FIRST IN, FIRST OUT - NHẬP TRƯỚC, XUẤT TRƯỚC)
- **Định nghĩa:** Hàng hóa nào nhập vào kho trước sẽ được ưu tiên xuất kho trước.
- **Mục đích:** Tránh hết hạn sử dụng hoặc suy giảm chất lượng vật tư lưu kho (đặc biệt với xi măng, sơn, keo dán...).
- **Tại SmartLogis AI:** Hệ thống lưu vết chi tiết từng lô nhập vào **Sổ Thẻ kho** để thủ kho dễ dàng tra cứu và xuất kho chuẩn xác.""",
            "suggested_questions": ["LIFO là gì?", "Sinh báo cáo điều hành kho 3 phần", "Danh sách hàng tồn lâu > 60 ngày"]
        }

    if "lifo" in q_no_accent or "nhap sau xuat truoc" in q_no_accent:
        return {
            "reply": """### 📦 NGUYÊN TẮC LIFO (LAST IN, FIRST OUT - NHẬP SAU, XUẤT TRƯỚC)
- **Định nghĩa:** Hàng hóa nhập vào kho sau cùng sẽ được xuất ra trước tiên.
- **Ứng dụng:** Thường áp dụng cho vật tư đổ đống không suy giảm phẩm chất (cát, đá, than...).
- **Lưu ý:** Chuẩn mực kế toán VAS/IFRS hiện nay ưu tiên phương pháp **Bình quân gia quyền** hoặc **FIFO** hơn LIFO.""",
            "suggested_questions": ["FIFO là gì?", "Sinh báo cáo điều hành kho 3 phần", "Top mặt hàng xuất kho nhiều nhất (Burn-rate)"]
        }

    if any(k in q_no_accent for k in ["safety stock", "ton an toan"]):
        return {
            "reply": f"""### 🛡️ TỒN KHO AN TOÀN (SAFETY STOCK / TỒN TỐI THIỂU)
- **Định nghĩa:** Lượng hàng dự phòng tối thiểu duy trì trong kho để tránh nguy cơ đứt gãy cung ứng khi phát sinh nhu cầu đột xuất.
- **Số liệu SmartLogis AI hiện tại:**
  - Có **{len(low_stocks)} mặt hàng** đang chạm hoặc dưới ngưỡng tồn an toàn cần nhập bổ sung khẩn cấp.""",
            "suggested_questions": ["⚠️ Mặt hàng nào đang thiếu hụt nguy cấp?", "Gợi ý nhà cung cấp cho các mặt hàng thiếu hụt", "Sinh báo cáo điều hành kho 3 phần"]
        }

    # =========================================================================
    # 18. LỜI CẢM ƠN
    # =========================================================================
    if any(k in q_no_accent for k in ["cam on", "thank you", "thanks", "tot lam", "tuyet voi", "hay lam"]):
        return {
            "reply": """Rất vui được hỗ trợ bạn! Chúc bạn có một ngày làm việc hiệu quả và quản lý kho hàng luôn thông suốt, chính xác.

Nếu bạn cần kiểm tra tồn kho, rà soát cảnh báo hay số dư thẻ kho, đừng ngần ngại hỏi tôi nhé!""",
            "suggested_questions": default_suggested
        }

    # =========================================================================
    # 19. TẠM BIỆT
    # =========================================================================
    if any(k in q_no_accent for k in ["tam biet", "bye", "goodbye", "hen gap lai"]):
        return {
            "reply": """Tạm biệt bạn! Chúc bạn công việc thuận lợi. Hẹn gặp lại bạn trong các phiên làm việc tiếp theo cùng **SmartLogis AI**!""",
            "suggested_questions": default_suggested
        }

    # =========================================================================
    # 20. BẠN LÀ AI / GIỚI THIỆU
    # =========================================================================
    if any(k in q_no_accent for k in ["ban la ai", "ten gi", "gioi thieu ban than", "ai tao ra ban"]):
        return {
            "reply": f"""Tôi là **Trợ Lý AI Vận Hành Kho SmartLogis AI**.

Tôi được thiết kế chuyên biệt để đồng hành cùng thủ kho, kế toán và ban quản lý:
1. 🛡️ **Kiểm soát an toàn dữ liệu:** Nắm vững cơ chế chống tồn âm 2 tầng (Zero Negative Stock) và giao dịch ACID All-or-Nothing.
2. ⚡ **Đồng bộ thời gian thực:** Kết nối trực tiếp CSDL {meta.get('tong_sku', 0)} SKU và {meta.get('tong_nha_cung_cap', 0)} đối tác cung ứng.
3. 🔢 **Tính toán số học tức thời:** Tự động giải các phép tính, tỷ lệ phần trăm và công thức vận hành.
4. 🔒 **Bảo mật tuyệt đối:** Tự động khử nhạy cảm 100% dữ liệu giá vốn bằng module Data Sanitizer trước khi xử lý.""",
            "suggested_questions": default_suggested
        }

    # =========================================================================
    # 21. CHÀO HỎI (ÁP DỤNG QUY TẮC KHỚP TỪ ĐỘC LẬP - TRÁNH LỖI PHIẾU/KHI/CHI)
    # =========================================================================
    is_pure_greeting = (
        bool(re.search(r'\b(xin chao|chao ban|chao bot|chao ai|chao em)\b', q_no_accent)) or
        bool(re.fullmatch(r'[\s!?.~]*(hi|hello|alo|chao)[\s!?.~]*', q_no_accent))
    )
    if is_pure_greeting:
        return {
            "reply": f"""Xin chào bạn! Tôi là **Trợ Lý AI Vận Hành Kho SmartLogis AI**. Rất sẵn sàng hỗ trợ bạn hôm nay!

Tôi có thể hỗ trợ bạn nhanh các nội dung:
- 📊 **Báo cáo 3 phần:** Tổng quan kho, cảnh báo thiếu hụt và biến động bất thường.
- ⚠️ **Hàng thiếu hụt:** Rà soát ngay {len(low_stocks)} SKU chạm hoặc dưới tồn tối thiểu.
- 🏢 **Gợi ý nhà cung cấp:** Tìm đối tác cung ứng nhanh cho các mặt hàng thiếu.
- 📦 **Hàng tồn lâu:** Danh sách các mặt hàng ứ đọng > 60 ngày cần giải phóng.
- 🔍 **Tra cứu chi tiết:** Nhập mã SKU hoặc tên hàng hóa (ví dụ: *Thép phi 8*, *Xi măng Bút Sơn*...).
- 🔢 **Tính toán nhanh:** Nhập trực tiếp phép tính bất kỳ (ví dụ: `1 + 1 = ?`, `10 * 5`...).""",
            "suggested_questions": default_suggested
        }

    # =========================================================================
    # 22. PHẢN HỒI KHI CÂU HỎI MỞ RỘNG (CSDL NỘI BỘ VẪN HỖ TRỢ TỐI ĐA)
    # =========================================================================
    return {
        "reply": f"""Tôi đã tiếp nhận câu hỏi của bạn: *"**{query}**"*.

Hiện tại hệ thống đang chạy ở chế độ **Local Grounded Conversational Engine (CSDL Nội Bộ)**:
- 📊 Đang kết nối trực tiếp số liệu của **{meta.get('tong_sku', 0)} SKU** vật tư và **{meta.get('tong_nha_cung_cap', 0)} nhà cung cấp**.
- ⚠️ Ghi nhận **{len(low_stocks)} mặt hàng** chạm/dưới tồn min và **{len(dead_stocks)} mặt hàng** tồn lâu > 60 ngày.
- 🛡️ Sẵn sàng trả lời các câu hỏi về: Tra cứu hàng hóa, tính toán số học, báo cáo 3 phần, quy trình xuất nhập kho và cơ chế chống tồn âm Zero Negative Stock.

💡 **Mẹo:** Bạn có thể bấm vào các câu hỏi gợi ý bên dưới hoặc bấm biểu tượng 🔑 **(Cấu hình Gemini API Key)** ở góc trên để mở khóa khả năng trả lời tự do mọi câu hỏi mở rộng!""",
        "suggested_questions": default_suggested
    }


def extract_smart_suggestions(reply_text: str, query: str, context: Dict[str, Any]) -> List[str]:
    """Trích xuất hoặc tự động sinh các câu hỏi gợi ý tiếp theo thông minh, gắn liền với mạch hội thoại."""
    suggestions = []
    
    # 1. Thử trích xuất từ phần 'GỢI Ý TIẾP THEO:' hoặc 'Gợi ý:' nếu LLM sinh ra
    lines = reply_text.split("\n")
    collecting = False
    for line in lines:
        l = line.strip()
        if re.search(r'(gợi ý tiếp theo|câu hỏi gợi ý|hành động tiếp theo):', l, re.I):
            collecting = True
            continue
        if collecting:
            m = re.match(r'^(?:[-*•]|\d+\.)\s*\[?([^\]\n]+)\]?', l)
            if m:
                sug = m.group(1).strip()
                if 5 < len(sug) < 80 and not sug.lower().startswith("câu hỏi"):
                    suggestions.append(sug)
            elif not l:
                continue
            else:
                break
    
    if len(suggestions) >= 2:
        return suggestions[:4]

    # 2. Sinh câu hỏi linh hoạt dựa trên nội dung câu hỏi hiện tại và tình trạng kho
    q_no_acc = remove_accents(query.lower())
    low_stocks = context.get("low_stock_alerts", [])
    dead_stocks = context.get("dead_stock_items", [])
    
    if any(k in q_no_acc for k in ["lam tiep", "tiep tuc", "tiep theo", "buoc tiep"]):
        return [
            "📥 Xem hướng dẫn tạo phiếu tại /inbound",
            "📋 Đối chiếu số dư lũy kế tại /the-kho",
            "📊 Sinh báo cáo điều hành kho 3 phần",
            "🏢 Gợi ý nhà cung cấp cho các mặt hàng thiếu hụt"
        ]
    elif any(k in q_no_acc for k in ["thieu hut", "ton min", "nguy cap", "can nhap"]):
        return [
            "Làm tiếp: Lập dự thảo phiếu nhập kho",
            "🏢 Gợi ý nhà cung cấp cho các mặt hàng thiếu hụt",
            "🚀 Top mặt hàng xuất kho nhiều nhất (Burn-rate)",
            "📊 Sinh báo cáo điều hành kho 3 phần"
        ]
    elif any(k in q_no_acc for k in ["bao cao", "3 phan"]):
        return [
            "Làm tiếp: Lập kế hoạch nhập hàng cho SKU nguy cấp",
            "Làm tiếp: Phương án giải phóng hàng tồn lâu > 60 ngày",
            "🏢 Gợi ý nhà cung cấp tương ứng",
            "🛡️ Giải thích cơ chế chống tồn âm Zero Negative Stock"
        ]
    elif any(k in q_no_acc for k in ["nha cung cap", "ncc", "supplier"]):
        return [
            "Làm tiếp: Hướng dẫn tạo phiếu nhập từ NCC này",
            "⚠️ Mặt hàng nào đang thiếu hụt nguy cấp?",
            "📊 Sinh báo cáo điều hành kho 3 phần"
        ]
    elif any(k in q_no_acc for k in ["dead stock", "ton lau", "60 ngay"]):
        return [
            "Làm tiếp: Kế hoạch thanh lý chiết khấu hàng tồn",
            "⚠️ Mặt hàng nào đang thiếu hụt nguy cấp?",
            "🚀 Top mặt hàng xuất kho nhiều nhất (Burn-rate)"
        ]
    else:
        return [
            "📊 Sinh báo cáo điều hành kho 3 phần",
            "⚠️ Mặt hàng nào đang thiếu hụt nguy cấp?",
            "🏢 Gợi ý nhà cung cấp cho các mặt hàng thiếu hụt",
            "🛡️ Giải thích cơ chế chống tồn âm Zero Negative Stock"
        ]


def process_ai_chat_message(
    db: Session,
    message: str,
    history: Optional[List[AIChatMessage]] = None,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Hàm điều phối xử lý tin nhắn Chat Box:
    1. Trích xuất Context CSDL kho 30 ngày (đã làm sạch 100% giá vốn nhạy cảm).
    2. Nếu có Gemini API Key hợp lệ: Gọi Google Gemini LLM API kèm context CSDL thực tế.
    3. Nếu không có Key hoặc mạng gián đoạn: Kích hoạt Local Grounded Conversational Engine v2.0
       đối chiếu chính xác 100% CSDL nội bộ, hỗ trợ multi-turn 'làm tiếp' chuẩn xác.
    """
    context = build_warehouse_chat_context(db)
    key_to_use = (api_key or "").strip() or gemini_service.api_key
    has_gemini = bool(key_to_use and len(key_to_use) > 10)

    if has_gemini:
        try:
            meta = context.get("metadata", {})
            summary_context = {
                "metadata": meta,
                "low_stock_count": len(context.get("low_stock_alerts", [])),
                "dead_stock_count": len(context.get("dead_stock_items", [])),
                "high_burn_count": len(context.get("high_burn_rate_items", [])),
                "top_low_stocks": context.get("low_stock_alerts", [])[:10],
                "top_dead_stocks": context.get("dead_stock_items", [])[:10],
                "top_high_burns": context.get("high_burn_rate_items", [])[:10],
                "inventory_sample": context.get("inventory_summary", [])[:20],
                "suppliers_sample": context.get("suppliers", [])[:10]
            }

            hist_str = ""
            if history:
                for h in history[-8:]:
                    role_lbl = "Người dùng" if getattr(h, 'role', '') == "user" or (isinstance(h, dict) and h.get('role') == 'user') else "Trợ lý AI"
                    c_text = getattr(h, 'content', '') if hasattr(h, 'content') else (h.get('content', '') if isinstance(h, dict) else '')
                    if c_text:
                        hist_str += f"{role_lbl}: {c_text}\n"

            user_query_prompt = f"""Dữ liệu CSDL kho thời gian thực của hệ thống SmartLogis AI:
```json
{json.dumps(summary_context, ensure_ascii=False, indent=2)}
```

Lịch sử trò chuyện gần nhất:
{hist_str or "(Chưa có lịch sử trước đó)"}

Câu hỏi hiện tại của người dùng:
"{message}"

YÊU CẦU TRẢ LỜI:
1. Trả lời trực tiếp, chính xác, ĐÚNG TRỌNG TÂM câu hỏi của người dùng. Không trả lời lạc đề, không tự ý chuyển sang chủ đề khác nếu người dùng không yêu cầu.
2. Nếu câu hỏi liên quan đến dữ liệu kho (tồn kho, cảnh báo, xuất nhập, báo cáo, nhà cung cấp, thẻ kho): Phải dựa vào đúng số liệu CSDL thực tế ở trên để trả lời trung thực.
3. Nếu người dùng hỏi về gợi ý nhà cung cấp: Trả về bảng đối tác cung cấp tương ứng.
4. Nếu người dùng hỏi về lập danh sách nhập kho: Trả về bảng dự thảo phiếu nhập với số lượng đề xuất.
5. Nếu câu hỏi là câu hỏi mở rộng, kiến thức logistics, kỹ thuật hoặc trò chuyện: Hãy trả lời thông minh, nhiệt tình, hữu ích.
6. ĐẶC BIỆT KHI NGƯỜI DÙNG NÓI 'LÀM TIẾP', 'TIẾP TỤC', 'TIẾP THEO', 'BƯỚC TIẾP LÀ GÌ':
   Hãy đọc kỹ lịch sử trò chuyện phía trên để hiểu người dùng đang ở bước nào (ví dụ: vừa xem danh sách thiếu hụt, vừa xem báo cáo, vừa xem nhà cung cấp, vừa tra cứu SKU...), và hướng dẫn/thực hiện cụ thể bước tiếp theo một cách liền mạch, chi tiết và có thể hành động ngay (actionable).
7. Luôn trình bày đẹp mắt bằng Markdown (bảng biểu, bullet points, in đậm). Cuối câu trả lời, hãy gợi ý 3-4 câu hỏi/hành động tiếp theo có ý nghĩa nhất theo cú pháp:
GỢI Ý TIẾP THEO:
- [Câu hỏi 1]
- [Câu hỏi 2]
- [Câu hỏi 3]"""

            for model_name in SUPPORTED_GEMINI_MODELS:
                gemini_reply = gemini_service._call_gemini_with_retry(
                    model_name=model_name,
                    user_prompt=user_query_prompt,
                    system_prompt=SYSTEM_CHAT_PROMPT,
                    api_key=key_to_use
                )
                if gemini_reply and len(gemini_reply.strip()) > 10:
                    suggested_list = extract_smart_suggestions(gemini_reply.strip(), message, context)
                    return {
                        "status": "success",
                        "reply": gemini_reply.strip(),
                        "model_used": f"Google Gemini ({model_name})",
                        "is_fallback": False,
                        "context_summary": meta,
                        "suggested_questions": suggested_list
                    }
        except Exception as e:
            logger.warning(f"[AIChat] Lỗi khi gọi Google Gemini API: {e}. Chuyển sang Local Grounded Fallback Engine.")

    # Kích hoạt Local Grounded Fallback Engine v2.0 kèm history
    fallback_res = generate_local_grounded_chat_response(context, message, history=history)
    return {
        "status": "success",
        "reply": fallback_res.get("reply", ""),
        "model_used": "SmartLogis Grounded Analytical Engine (Local DB Grounded)",
        "is_fallback": True,
        "context_summary": context.get("metadata", {}),
        "suggested_questions": fallback_res.get("suggested_questions", [])
    }

