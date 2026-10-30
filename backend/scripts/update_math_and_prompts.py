import re

filepath = "backend/app/services/ai_chat_service.py"
with open(filepath, "r", encoding="utf-8") as f:
    text = f.read()

# 1. Update SYSTEM_CHAT_PROMPT
old_sys_prompt_pattern = r'SYSTEM_CHAT_PROMPT = """[\s\S]*?"""'
new_sys_prompt = '''SYSTEM_CHAT_PROMPT = """Bạn là Trợ lý AI Thông minh của Hệ thống Quản trị Kho SmartLogis AI (SmartLogis Conversational Assistant) v2.0 Enterprise.

Nguyên tắc phản hồi:
1. Giao tiếp tự nhiên, linh hoạt và chuẩn xác:
   - Nếu người dùng chào hỏi, trò chuyện thông thường hoặc hỏi các câu đố/toán học (ví dụ: "1+1 bằng mấy"), hãy trả lời ngắn gọn, chính xác và tự nhiên (ví dụ: "1 + 1 = 2"). Tuyệt đối không gán ghép các quy tắc kho vào những câu hỏi không liên quan.
2. Khi được hỏi về dữ liệu kho, vật tư, số dư, nhà cung cấp, hoặc quy trình vận hành dự án:
   - Hãy dựa vào Context Dữ Liệu Kho (JSON) được cung cấp kèm theo để trả lời chi tiết, chính xác từng số liệu thực tế (SKU, số lượng tồn, ngưỡng tối thiểu, cảnh báo tồn lâu).
   - Nắm vững 3 vai trò RBAC: Admin (toàn quyền), Thủ kho (nhập/xuất kho ACID, Thẻ kho, đối soát NCC), Nhân viên kho (chỉ đọc, bị chặn lập phiếu HTTP 403).
   - Hướng dẫn rõ ràng các menu giao diện Web SSR (/inbound, /outbound, /the-kho, /hang-hoa, /nha-cung-cap) và cơ chế bảo vệ giao dịch ACID, Zero Negative Stock 2 tầng.
3. Tuân thủ bảo mật & chống ảo giác:
   - Tuyệt đối không suy đoán hoặc bịa đặt số liệu không có trong context.
   - Tuyệt đối không tiết lộ các trường giá vốn nhạy cảm (DonGiaNhap, ThanhTien, GiaVon).
4. Phong cách:
   - Trình bày bằng tiếng Việt thân thiện, cấu trúc rõ ràng bằng Markdown (bảng biểu, bullet points, in đậm khi cần).
"""'''

text = re.sub(old_sys_prompt_pattern, lambda m: new_sys_prompt, text, count=1)

# 2. Update solve_math_expression
old_math_pattern = r'def solve_math_expression\(query: str\) -> Optional\[tuple\]:[\s\S]*?def remove_accents'
new_math = '''def solve_math_expression(query: str) -> Optional[tuple]:
    """
    Nhận diện và giải chính xác các biểu thức số học:
    '1+1', '1+1 bằng mấy', '1 cộng 1 bằng mấy', '1 + 1 = ?', '10 * 5', '100 / 4', '10% của 500000'.
    """
    clean = query.strip()
    # Loại bỏ tiền tố hỏi phép tính
    clean = re.sub(r'^(?:tính|tính giúp|kết quả của|cho biết|cho hỏi|kết quả|giải giúp|hỏi|cho mình hỏi|bạn tính|tính hộ|bao nhiêu là)\\s+', '', clean, flags=re.I).strip()
    
    # Loại bỏ hậu tố hỏi kết quả: "bằng mấy", "bằng bao nhiêu", "la may", "la bao nhieu", "=?", "= ?", "?"
    clean = re.sub(r'\\s*(?:bằng|bang|là|la|ra)\\s*(?:mấy|may|bao nhiêu|bao nhieu|\\?)+$', '', clean, flags=re.I).strip()
    clean = re.sub(r'[\\s=\\?]+$', '', clean).strip()

    # Thay thế từ ngữ toán học tiếng Việt thành toán tử chuẩn
    clean = re.sub(r'\\b(?:cộng|cong)\\b', '+', clean, flags=re.I)
    clean = re.sub(r'\\b(?:trừ|tru)\\b', '-', clean, flags=re.I)
    clean = re.sub(r'\\b(?:nhân|nhan)\\b', '*', clean, flags=re.I)
    clean = re.sub(r'\\b(?:chia cho|chia)\\b', '/', clean, flags=re.I)

    # Kiểm tra phép tính phần trăm: e.g. 10% của 500000, 15% * 200, 5% cua 1000
    pct_m = re.match(r'^([\\d\\.]+)\\s*%\\s*(?:của|cua|\\*)\\s*([\\d\\.]+)$', clean, re.I)
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

    clean_eval = clean.replace('^', '**').replace('x', '*').replace('X', '*').replace(':', '/').replace(',', '').strip()
    if not re.search(r'\\d', clean_eval):
        return None
    # Chỉ cho phép các ký tự toán học số học an toàn
    if not re.fullmatch(r'[\\d\\s\\+\\-\\*/\\%\\(\\)\\.]+', clean_eval):
        return None
    # Phải chứa ít nhất 1 toán tử
    if not re.search(r'[\\+\\-\\*/\\%]', clean_eval):
        return None

    try:
        parsed = ast.parse(clean_eval, mode='eval')
        val = safe_eval_ast(parsed)
        if isinstance(val, float) and val.is_integer():
            val = int(val)
        return (clean, val)
    except Exception:
        return None


def remove_accents'''

text = re.sub(old_math_pattern, lambda m: new_math, text, count=1)

# 3. Update Section 1 math result formatting
old_sec_1 = '''    math_res = solve_math_expression(query)
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
        }'''

new_sec_1 = '''    math_res = solve_math_expression(query)
    if math_res:
        expr_str, val = math_res
        val_str = f"{val:,}" if isinstance(val, int) else f"{val:,.2f}".rstrip("0").rstrip(".")
        reply = f"**{expr_str} = {val_str}**"
        return {
            "reply": reply,
            "suggested_questions": [
                "📊 Sinh báo cáo điều hành kho 3 phần",
                "⚠️ Mặt hàng nào đang thiếu hụt nguy cấp?",
                "🚀 Top mặt hàng xuất kho nhiều nhất (Burn-rate)"
            ]
        }'''

text = text.replace(old_sec_1, new_sec_1)

# 4. Update Section 22 (intelligent warehouse check vs general conversation)
old_sec_22_pattern = r"# =========================================================================\s*# 22\. PHẢN HỒI THÔNG MINH CHO CÂU HỎI MỞ RỘNG[\s\S]*?def extract_smart_suggestions"

new_sec_22 = '''# =========================================================================
    # 22. PHẢN HỒI THÔNG MINH CHO CÂU HỎI MỞ RỘNG (KNOWLEDGE ENGINE NỘI BỘ)
    # =========================================================================
    is_warehouse_topic = any(k in q_no_accent for k in [
        "kho", "ton", "sku", "vat tu", "hang hoa", "nhap", "xuat", "the kho", "ncc",
        "nha cung cap", "bao cao", "sanitizer", "acid", "burn", "dead stock", "dieu hanh",
        "smartlogis", "kiem ke", "dinh muc", "luu kho", "cong no", "giao dich", "du an"
    ])

    if is_warehouse_topic:
        reply_lines = [
            "### 💡 TƯ VẤN QUẢN TRỊ KHO & VẬN HÀNH DỰ ÁN SMARTLOGIS AI",
            f'Đối với câu hỏi của bạn: **"{query}"**',
            "",
            "Trong công tác quản trị kho vận vật tư công trình của **SmartLogis AI**, hệ thống khuyến nghị các nguyên tắc cốt lõi sau:",
            "",
            "1. **Định lượng & Kiểm soát số dư:** Mọi biến động vật tư cần được phản ánh vào chứng từ chuẩn hóa (Phiếu Nhập tại **[/inbound](/inbound)** hoặc Phiếu Xuất tại **[/outbound](/outbound)**).",
            "2. **Minh bạch hóa sổ cái Thẻ kho:** Số dư lũy kế phải được cập nhật tức thì vào **[Sổ Thẻ Kho](/the-kho)** để đảm bảo tính bất biến kế toán.",
            "3. **Kiểm soát Tồn an toàn (Safety Stock):** Luôn theo dõi sát các mặt hàng có tốc độ xuất cao (High Burn-rate) để kịp thời kích hoạt chu kỳ đặt hàng bổ sung.",
            "",
            f"📊 **Hiện trạng kho thời gian thực:**",
            f"- Tổng danh mục quản lý: **{meta.get('tong_sku', 0)} SKU** vật tư.",
            f"- Trạng thái an toàn: **{max(0, meta.get('tong_sku', 0) - len(low_stocks))} SKU** đạt ngưỡng chuẩn.",
            f"- Cần chú ý nhập bù: **{len(low_stocks)} SKU** đang chạm hoặc dưới tồn tối thiểu.",
            "",
            "💡 *Bạn có thể chọn một trong các thao tác nhanh bên dưới để xem số liệu phân tích chi tiết:*"
        ]
        return {
            "reply": "\\n".join(reply_lines),
            "suggested_questions": [
                "📊 Sinh báo cáo điều hành kho 3 phần",
                "⚠️ Mặt hàng nào đang thiếu hụt nguy cấp?",
                "📥 Hướng dẫn tạo phiếu nhập kho",
                "🛡️ Giải thích cơ chế chống tồn âm Zero Negative Stock"
            ]
        }
    else:
        # Câu hỏi trò chuyện / đàm thoại đời sống bình thường: Trả lời tự nhiên, thân thiện
        reply = f"""Tôi là **Trợ Lý AI SmartLogis AI**. Rất vui được hỗ trợ bạn!

Hệ thống được thiết kế chuyên biệt để hỗ trợ quản trị kho vận vật tư công trình, tính toán số liệu và kiểm soát thẻ kho. Bạn có thể hỏi tôi bất kỳ câu hỏi nào về tình trạng tồn kho, tra cứu SKU, cảnh báo hàng sắp hết hoặc hướng dẫn lập phiếu nhập/xuất kho!"""
        return {
            "reply": reply,
            "suggested_questions": default_suggested
        }


def extract_smart_suggestions'''

text = re.sub(old_sec_22_pattern, lambda m: new_sec_22, text, count=1)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(text)

print("Updated math and prompts in ai_chat_service.py successfully!")
