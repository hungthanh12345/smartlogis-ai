"""
SmartLogis AI - PowerPoint Presentation Deck Generator
Phong cách: TỐI GIẢN - ÍT CHỮ - GIÀU THÔNG TIN KỸ THUẬT - DỄ THUYẾT TRÌNH (CLEAN & MINIMALIST)
Tiêu chuẩn: Báo Cáo Đồ Án Chuyên Ngành / Đồ Án Tốt Nghiệp Kỹ Thuật Phần Mềm (K23A - Thái Nguyên, 2026)
Đội ngũ: Nguyễn Thành Hưng (PO - Fullstack Dev) • Hoàng Tiến Đạt (Scrum Master - Database Architect, AI & QA)
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# -------------------------------------------------------------
# PALETTE MÀU CHUYÊN NGHIỆP (Deep Navy & Technical Blue Scheme)
# -------------------------------------------------------------
COLOR_DEEP_NAVY   = RGBColor(10, 25, 47)      # #0A192F (Nền tối Hero Cover / Conclusion)
COLOR_MID_NAVY    = RGBColor(15, 35, 65)      # #0F2341 (Nền phụ, container tối)
COLOR_ROYAL_BLUE  = RGBColor(30, 58, 138)     # #1E3A8A (Header chính, border card trọng yếu)
COLOR_TECH_BLUE   = RGBColor(37, 99, 235)     # #2563EB (Nhấn mạnh hành động, pills, icon)
COLOR_CYAN_ACCENT = RGBColor(6, 182, 212)     # #06B6D4 (Accent highlight, KPI, line decor)
COLOR_ICE_BLUE    = RGBColor(240, 247, 255)   # #F0F7FF (Nền card sáng)
COLOR_CARD_BORDER = RGBColor(191, 219, 254)   # #BFDBFE (Viền card tinh tế)
COLOR_CARD_DARK   = RGBColor(20, 42, 77)      # #142A4D (Card nền tối trên Hero slide)
COLOR_WHITE       = RGBColor(255, 255, 255)   # #FFFFFF
COLOR_DARK_TEXT   = RGBColor(15, 23, 42)      # #0F172A (Chữ chính trên nền sáng)
COLOR_MUTED_TEXT  = RGBColor(51, 65, 85)      # #334155 (Chữ phụ, bullet points)
COLOR_LIGHT_MUTED = RGBColor(148, 163, 184)   # #94A3B8 (Chữ phụ trên nền tối)
COLOR_ALERT_RED   = RGBColor(225, 29, 72)     # #E11D48 (Cảnh báo, nhược điểm)
COLOR_SUCCESS_GRN = RGBColor(16, 185, 129)    # #10B981 (Thành công, giải pháp đạt chuẩn)

FONT_HEADING = "Segoe UI"
FONT_BODY    = "Segoe UI"
FONT_CODE    = "Consolas"

def set_slide_background(slide, color):
    """Thiết lập màu nền đơn sắc cho slide."""
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = color

def add_header(slide, title_text, category_badge="SMARTLOGIS AI", is_dark=False):
    """Tạo header chuẩn hóa gồm Section Badge và Tiêu đề hành động kỹ thuật."""
    # Badge Pill trên cùng
    badge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.38), Inches(2.7), Inches(0.36))
    badge.fill.solid()
    badge.fill.fore_color.rgb = COLOR_TECH_BLUE if is_dark else COLOR_ROYAL_BLUE
    badge.line.color.rgb = COLOR_CYAN_ACCENT if is_dark else COLOR_TECH_BLUE
    badge.line.width = Pt(1.5)
    tf_b = badge.text_frame
    tf_b.word_wrap = True
    p_b = tf_b.paragraphs[0]
    p_b.text = category_badge
    p_b.font.name = FONT_HEADING
    p_b.font.size = Pt(11.5)
    p_b.font.bold = True
    p_b.font.color.rgb = COLOR_WHITE
    p_b.alignment = PP_ALIGN.CENTER

    # Tiêu đề lớn
    txBox = slide.shapes.add_textbox(Inches(0.8), Inches(0.78), Inches(11.73), Inches(0.68))
    tf = txBox.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.text = title_text
    p.font.name = FONT_HEADING
    p.font.size = Pt(26)
    p.font.bold = True
    p.font.color.rgb = COLOR_WHITE if is_dark else COLOR_ROYAL_BLUE
    p.alignment = PP_ALIGN.LEFT

def add_speaker_notes(slide, notes_text):
    """Ghi chú diễn giả (Speaker Notes) chi tiết phục vụ thuyết trình."""
    notes_slide = slide.notes_slide
    text_frame = notes_slide.notes_text_frame
    text_frame.text = notes_text

def create_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # =========================================================================
    # SLIDE 1: TRANG BÌA (Hero Dark Navy)
    # =========================================================================
    slide1 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide1, COLOR_DEEP_NAVY)

    # Dải viền trang trí Cyan trên đỉnh
    top_bar = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.14))
    top_bar.fill.solid()
    top_bar.fill.fore_color.rgb = COLOR_CYAN_ACCENT
    top_bar.line.fill.background()

    # Badge học thuật
    tag = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(0.7), Inches(4.3), Inches(0.42))
    tag.fill.solid()
    tag.fill.fore_color.rgb = COLOR_ROYAL_BLUE
    tag.line.color.rgb = COLOR_CYAN_ACCENT
    tag.line.width = Pt(1.5)
    tf_tag = tag.text_frame
    p_tag = tf_tag.paragraphs[0]
    p_tag.text = "ĐỒ ÁN TỐT NGHIỆP • KỸ THUẬT PHẦN MỀM K23A"
    p_tag.font.name = FONT_HEADING
    p_tag.font.size = Pt(12)
    p_tag.font.bold = True
    p_tag.font.color.rgb = COLOR_CYAN_ACCENT
    p_tag.alignment = PP_ALIGN.CENTER

    # Tiêu đề chính đề tài
    title_box = slide1.shapes.add_textbox(Inches(1.0), Inches(1.28), Inches(11.333), Inches(1.85))
    tf_title = title_box.text_frame
    tf_title.word_wrap = True
    
    p_t1 = tf_title.paragraphs[0]
    p_t1.text = "HỆ THỐNG QUẢN LÝ KHO THÔNG MINH"
    p_t1.font.name = FONT_HEADING
    p_t1.font.size = Pt(38)
    p_t1.font.bold = True
    p_t1.font.color.rgb = COLOR_WHITE

    p_t2 = tf_title.add_paragraph()
    p_t2.text = "TÍCH HỢP TRÍ TUỆ NHÂN TẠO & BẢO TOÀN GIAO DỊCH ACID"
    p_t2.font.name = FONT_HEADING
    p_t2.font.size = Pt(32)
    p_t2.font.bold = True
    p_t2.font.color.rgb = COLOR_CYAN_ACCENT
    p_t2.space_before = Pt(4)

    # Subtitle học thuật
    sub_box = slide1.shapes.add_textbox(Inches(1.0), Inches(3.25), Inches(11.333), Inches(0.5))
    tf_sub = sub_box.text_frame
    p_sub = tf_sub.paragraphs[0]
    p_sub.text = "Kiến trúc Giao dịch Kho Nguyên tử ACID • Tối ưu Chuỗi Cung ứng với Google Gemini LLM"
    p_sub.font.name = FONT_BODY
    p_sub.font.size = Pt(16)
    p_sub.font.color.rgb = COLOR_LIGHT_MUTED

    # 3 Card chân trang tóm lược 3 trụ cột kỹ thuật
    pillars = [
        ("🛡️ GIAO DỊCH ACID NGUYÊN TỬ", 
         "Chống Tồn Âm 2 Tầng Kỹ Thuật", 
         "Atomic SQL Decrement kết hợp Database CheckConstraint"),
        ("🧠 TRÍ TUỆ NHÂN TẠO GEMINI", 
         "Cố Vấn Điều Hành Kho Thông Minh", 
         "Data Sanitizer khử 100% giá vốn & Local Grounded Fallback"),
        ("🚀 HẠ TẦNG THỰC TẾ & REALTIME", 
         "FastAPI • PostgreSQL • WebSocket", 
         "Nginx SSL Gateway & Đồng bộ tức thời biến động đa thiết bị")
    ]
    card_w = Inches(3.64)
    card_gap = Inches(0.20)
    start_x = Inches(1.0)
    for i, (head, sub1, sub2) in enumerate(pillars):
        x = start_x + i * (card_w + card_gap)
        card = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(3.85), card_w, Inches(1.95))
        card.fill.solid()
        card.fill.fore_color.rgb = COLOR_CARD_DARK
        card.line.color.rgb = COLOR_TECH_BLUE
        card.line.width = Pt(1.5)
        tf_c = card.text_frame
        tf_c.word_wrap = True
        tf_c.margin_left = tf_c.margin_right = Inches(0.25)
        tf_c.margin_top = Inches(0.18)
        
        p1 = tf_c.paragraphs[0]
        p1.text = head
        p1.font.name = FONT_HEADING
        p1.font.size = Pt(14)
        p1.font.bold = True
        p1.font.color.rgb = COLOR_CYAN_ACCENT

        p2 = tf_c.add_paragraph()
        p2.text = sub1
        p2.font.name = FONT_BODY
        p2.font.size = Pt(13)
        p2.font.bold = True
        p2.font.color.rgb = COLOR_WHITE
        p2.space_before = Pt(5)

        p3 = tf_c.add_paragraph()
        p3.text = f"• {sub2}"
        p3.font.name = FONT_BODY
        p3.font.size = Pt(12)
        p3.font.color.rgb = COLOR_LIGHT_MUTED
        p3.space_before = Pt(4)

    # Khung thông tin nhân sự thực hiện (Mô hình Scrum 02 người)
    team_box = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(5.98), Inches(11.333), Inches(1.15))
    team_box.fill.solid()
    team_box.fill.fore_color.rgb = COLOR_MID_NAVY
    team_box.line.color.rgb = COLOR_TECH_BLUE
    team_box.line.width = Pt(1.2)
    tf_team = team_box.text_frame
    tf_team.word_wrap = True
    tf_team.margin_left = tf_team.margin_right = Inches(0.3)
    tf_team.margin_top = Inches(0.12)

    p_tm0 = tf_team.paragraphs[0]
    p_tm0.text = "NHÓM SINH VIÊN THỰC HIỆN (MÔ HÌNH AGILE SCRUM 02 THÀNH VIÊN):"
    p_tm0.font.name = FONT_HEADING
    p_tm0.font.size = Pt(12)
    p_tm0.font.bold = True
    p_tm0.font.color.rgb = COLOR_CYAN_ACCENT

    p_tm1 = tf_team.add_paragraph()
    p_tm1.text = "1. Nguyễn Thành Hưng: Product Owner (PO) kiêm Lead Fullstack Developer (Backend FastAPI, Giao diện Jinja2/Tailwind, Nghiệp vụ kho & Báo cáo Excel)"
    p_tm1.font.name = FONT_BODY
    p_tm1.font.size = Pt(12)
    p_tm1.font.color.rgb = COLOR_WHITE
    p_tm1.space_before = Pt(3)

    p_tm2 = tf_team.add_paragraph()
    p_tm2.text = "2. Hoàng Tiến Đạt: Scrum Master kiêm Database Architect & AI/QA Engineer (CSDL 3NF, Gemini AI, Data Sanitizer, Pytest 110 Cases & Docker)"
    p_tm2.font.name = FONT_BODY
    p_tm2.font.size = Pt(12)
    p_tm2.font.color.rgb = COLOR_WHITE
    p_tm2.space_before = Pt(2)

    add_speaker_notes(slide1,
        "Thời lượng: 60 giây\n"
        "Kính thưa Quý Thầy/Cô trong Hội đồng Đánh giá Đồ án Tốt nghiệp Kỹ thuật Phần mềm Khóa K23A!\n"
        "Hôm nay, nhóm chúng em gồm 02 thành viên: Nguyễn Thành Hưng đảm nhiệm vai trò Product Owner kiêm Lead Fullstack Developer và Hoàng Tiến Đạt đảm nhiệm vai trò Scrum Master kiêm Database Architect & AI/QA Engineer, xin trân trọng báo cáo đề tài: 'Hệ Thống Quản Lý Kho Thông Minh Tích Hợp Trí Tuệ Nhân Tạo & Bảo Toàn Giao Dịch ACID (SmartLogis AI)'.\n"
        "Đề tài tập trung giải quyết hai bài toán kỹ thuật cốt lõi: Bảo toàn tính nhất quán tuyệt đối của dữ liệu kho với giải thuật Atomic SQL Decrement, và ứng dụng Trí tuệ nhân tạo Google Gemini nhằm tự động hóa công tác cảnh báo, điều phối chuỗi cung ứng nhưng vẫn bảo vệ tuyệt đối bí mật kinh doanh."
    )

    # =========================================================================
    # SLIDE 2: ĐẶT VẤN ĐỀ - BỐI CẢNH THỰC TẾ
    # =========================================================================
    slide2 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide2, COLOR_WHITE)
    add_header(slide2, "Bối Cảnh Thực Tế & 4 Thách Thức Kỹ Thuật Quản Trị Kho", "PROBLEM STATEMENT")

    problems = [
        ("⚠️ 1. LỖI TỒN ÂM (NEGATIVE STOCK)", 
         "Xung Đột Đồng Thời (Concurrency Race Condition)", 
         [
             "Nhiều thủ kho cùng xuất một mặt hàng tại cùng thời điểm",
             "Hiện tượng Lost Update do trừ tồn kho trong bộ nhớ ứng dụng",
             "Sai lệch nghiêm trọng giữa số liệu kế toán và kho thực tế"
         ], COLOR_ALERT_RED),
        ("⛓️ 2. ĐỨT GÃY NGUỒN CUNG VẬT TƯ", 
         "Thiếu Cơ Chế Dự Báo Tốc Độ Tiêu Thụ (Burn-Rate)", 
         [
             "Không theo dõi định lượng tốc độ tiêu thụ bình quân hàng ngày",
             "Chậm trễ phát hiện khi vật tư chạm ngưỡng tồn tối thiểu",
             "Gây đình trệ dây chuyền cung ứng và tiến độ thi công công trình"
         ], COLOR_ROYAL_BLUE),
        ("📦 3. HÀNG Ứ ĐỌNG (DEAD STOCK)", 
         "Khó Khăn Kiểm Soát Thủ Công Vật Tư Lưu Kho Lâu Ngày", 
         [
             "Nhiều SKU giá trị cao nằm kho vượt 60 ngày không phát sinh xuất",
             "Chiếm dụng diện tích mặt bằng kho bãi và phát sinh chi phí lưu kho",
             "Thiếu thuật toán tự động nhận diện và cảnh báo sớm cho quản lý"
         ], COLOR_ROYAL_BLUE),
        ("🔒 4. NGUY CƠ LỘ GIÁ VỐN KHI DÙNG AI", 
         "Rủi Ro Bảo Mật Dữ Liệu Khi Gửi Lên Public Cloud LLM", 
         [
             "Gửi trực tiếp bảng dữ liệu thô chứa đơn giá và thành tiền sang AI",
             "Nguy cơ rò rỉ chính sách chiết khấu và giá mua từ nhà cung cấp",
             "Yêu cầu bắt buộc phải có cơ chế khử nhạy cảm trước khi gửi context"
         ], COLOR_ALERT_RED)
    ]

    card_w = Inches(5.7)
    card_h = Inches(2.62)
    xs = [Inches(0.8), Inches(6.83)]
    ys = [Inches(1.6), Inches(4.45)]

    for idx, (title, sub, bullets, accent_col) in enumerate(problems):
        x = xs[idx % 2]
        y = ys[idx // 2]
        card = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, card_w, card_h)
        card.fill.solid()
        card.fill.fore_color.rgb = COLOR_ICE_BLUE
        card.line.color.rgb = COLOR_CARD_BORDER
        card.line.width = Pt(1.5)

        # Thanh trang trí màu trên đầu card
        strip = slide2.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, card_w, Inches(0.08))
        strip.fill.solid()
        strip.fill.fore_color.rgb = accent_col
        strip.line.fill.background()

        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = Inches(0.3)
        tf.margin_top = Inches(0.16)

        p1 = tf.paragraphs[0]
        p1.text = title
        p1.font.name = FONT_HEADING
        p1.font.size = Pt(15)
        p1.font.bold = True
        p1.font.color.rgb = accent_col
        p1.alignment = PP_ALIGN.LEFT

        p2 = tf.add_paragraph()
        p2.text = sub
        p2.font.name = FONT_HEADING
        p2.font.size = Pt(13.5)
        p2.font.bold = True
        p2.font.color.rgb = COLOR_DARK_TEXT
        p2.space_before = Pt(4)
        p2.alignment = PP_ALIGN.LEFT

        for b in bullets:
            pb = tf.add_paragraph()
            pb.text = f"• {b}"
            pb.font.name = FONT_BODY
            pb.font.size = Pt(13)
            pb.font.color.rgb = COLOR_MUTED_TEXT
            pb.space_before = Pt(4)
            pb.alignment = PP_ALIGN.LEFT

    add_speaker_notes(slide2,
        "Thời lượng: 75 giây\n"
        "Kính thưa Thầy/Cô, qua khảo sát thực tế tại các kho vật tư xây dựng, nhóm nghiên cứu đã tổng hợp được 4 thách thức kỹ thuật lớn nhất:\n"
        "1. Lỗi tồn kho âm: Xảy ra khi nhiều thủ kho thao tác đồng thời. Do ứng dụng đọc tồn kho lên bộ nhớ Python rồi mới trừ, dẫn đến hiện tượng Lost Update kinh điển trong hệ quản trị CSDL.\n"
        "2. Đứt gãy nguồn cung: Doanh nghiệp không có công cụ tính toán tốc độ tiêu thụ hàng ngày (Burn-rate), chỉ khi hàng hết kiệt mới đặt mua, gây chậm tiến độ thi công.\n"
        "3. Hàng ứ đọng (Dead Stock): Thiếu cơ chế theo dõi tự động các SKU nằm kho trên 60 ngày không luân chuyển, gây đọng vốn.\n"
        "4. Nguy cơ lộ giá vốn: Khi ứng dụng Trí tuệ Nhân tạo đám mây, nếu nạp toàn bộ dữ liệu kế toán thô gồm đơn giá mua và chiết khấu sang LLM của bên thứ ba, bí mật thương mại sẽ bị đe dọa."
    )

    # =========================================================================
    # SLIDE 3: MỤC TIÊU & GIẢI PHÁP ĐỀ XUẤT
    # =========================================================================
    slide3 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide3, COLOR_WHITE)
    add_header(slide3, "Mục Tiêu Đề Tài & 3 Trụ Cột Giải Pháp Kỹ Thuật", "OBJECTIVES & VALUE")

    objs = [
        ("🛡️ 1. BẢO TOÀN GIAO DỊCH ACID", "Kiểm Soát Tồn Kho Chống Âm 2 Tầng", [
            "Atomic SQL Decrement triệt tiêu hoàn toàn Race Condition",
            "Hardware CheckConstraint (SoLuongTon >= 0) cấp CSDL",
            "Cơ chế Rollback tự động toàn bộ khi hàng không đủ số lượng",
            "Bảo toàn tính bất biến của sổ Thẻ kho lũy kế (the_kho)"
        ], COLOR_TECH_BLUE),
        ("🧠 2. HỖ TRỢ ĐIỀU HÀNH THÔNG MINH", "Trợ Lý AI Phân Tích Chuyên Sâu", [
            "Tích hợp Google Gemini LLM với System Prompt Logistics",
            "Tự động tính toán tốc độ tiêu thụ Burn-rate 30 ngày gần nhất",
            "Báo cáo điều hành chuẩn hóa 3 phần phục vụ ra quyết định",
            "Tự động chỉ điểm danh mục Dead Stock cần ưu tiên giải phóng"
        ], COLOR_ROYAL_BLUE),
        ("🔐 3. BẢO MẬT & ĐỘ SẴN SÀNG CAO", "Khử Trùng Dữ Liệu & Fallback Ngoại Tuyến", [
            "Module Data Sanitizer lọc sạch 100% trường giá vốn nhạy cảm",
            "Endpoint audit dữ liệu minh bạch: GET /api/v1/ai/raw-context",
            "Local Grounded Fallback Engine chạy khi mất mạng hoặc lỗi 429",
            "Phân quyền RBAC 3 vai trò và cô lập phiên Tab Session"
        ], COLOR_TECH_BLUE)
    ]

    card_w = Inches(3.68)
    card_h = Inches(4.35)
    start_x = Inches(0.8)
    card_gap = Inches(0.35)

    for i, (head, sub, bullets, border_col) in enumerate(objs):
        x = start_x + i * (card_w + card_gap)
        card = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(1.6), card_w, card_h)
        card.fill.solid()
        card.fill.fore_color.rgb = COLOR_ICE_BLUE
        card.line.color.rgb = border_col
        card.line.width = Pt(1.5)

        band = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(1.6), card_w, Inches(0.88))
        band.fill.solid()
        band.fill.fore_color.rgb = border_col
        band.line.fill.background()
        tf_band = band.text_frame
        tf_band.word_wrap = True
        p_b = tf_band.paragraphs[0]
        p_b.text = head
        p_b.font.name = FONT_HEADING
        p_b.font.size = Pt(14.5)
        p_b.font.bold = True
        p_b.font.color.rgb = COLOR_WHITE
        p_b.alignment = PP_ALIGN.CENTER

        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = Inches(0.25)
        tf.margin_top = Inches(1.02)

        p1 = tf.paragraphs[0]
        p1.text = sub
        p1.font.name = FONT_HEADING
        p1.font.size = Pt(14)
        p1.font.bold = True
        p1.font.color.rgb = COLOR_ROYAL_BLUE
        p1.alignment = PP_ALIGN.LEFT

        for b in bullets:
            pb = tf.add_paragraph()
            pb.text = f"• {b}"
            pb.font.name = FONT_BODY
            pb.font.size = Pt(13)
            pb.font.color.rgb = COLOR_DARK_TEXT
            pb.space_before = Pt(7)
            pb.alignment = PP_ALIGN.LEFT

    # Banner kỹ thuật dưới chân trang
    banner = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(6.15), Inches(11.73), Inches(0.8))
    banner.fill.solid()
    banner.fill.fore_color.rgb = COLOR_MID_NAVY
    banner.line.color.rgb = COLOR_CYAN_ACCENT
    banner.line.width = Pt(1)
    tf_ban = banner.text_frame
    p_ban = tf_ban.paragraphs[0]
    p_ban.text = "🎯 KẾT QUẢ ĐẦU RA: Hệ thống hoàn chỉnh đáp ứng ACID, bảo mật dữ liệu AI, phân quyền 3 vai trò và vận hành đa thiết bị."
    p_ban.font.name = FONT_HEADING
    p_ban.font.size = Pt(13.5)
    p_ban.font.bold = True
    p_ban.font.color.rgb = COLOR_CYAN_ACCENT
    p_ban.alignment = PP_ALIGN.CENTER

    add_speaker_notes(slide3,
        "Thời lượng: 70 giây\n"
        "Từ 4 bài toán thực tế, nhóm nghiên cứu xác lập 3 trụ cột kỹ thuật trọng tâm:\n"
        "Thứ nhất: Triệt tiêu hoàn toàn rủi ro tồn âm bằng cơ chế kiểm soát 2 tầng: Tầng ứng dụng thực thi Atomic SQL Decrement kết hợp Tầng CSDL ràng buộc CheckConstraint phần cứng.\n"
        "Thứ hai: Xây dựng Trợ lý AI trên nền tảng Google Gemini để tự động tính toán Burn-rate tiêu thụ và xuất báo cáo 3 phần, hỗ trợ ban lãnh đạo ra quyết định nhập hàng kịp thời.\n"
        "Thứ ba: Thiết lập cơ chế bảo mật kép với Data Sanitizer lọc sạch 100% giá vốn nhạy cảm trước khi nạp context, và dự phòng Local Grounded Fallback Engine giúp hệ thống vận hành liên tục ngay cả khi mất mạng."
    )

    # =========================================================================
    # SLIDE 4: KIẾN TRÚC PHÂN TẦNG HỆ THỐNG
    # =========================================================================
    slide4 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide4, COLOR_WHITE)
    add_header(slide4, "Kiến Trúc Hệ Thống Phân Tầng (Layered Architecture)", "SYSTEM ARCHITECTURE")

    layers = [
        ("1. PRESENTATION LAYER (TẦNG GIAO DIỆN & TƯƠNG TÁC)", 
         "Jinja2 Server-Side Rendering • Tailwind CSS • Chart.js • Native WebSocket Client", 
         "Hiển thị Dashboard điều hành thời gian thực, trực quan hóa KPI kho, tương tác trợ lý AI và hỗ trợ responsive trên PC, tablet, mobile.", 
         COLOR_TECH_BLUE),
        
        ("2. SECURITY & AUTH LAYER (TẦNG BẢO MẬT & PHIÊN LÀM VIỆC)", 
         "FastAPI OAuth2 • JWT HTTPOnly Cookie • Bcrypt Hash (72 bytes) • Header X-Session-User", 
         "Xác thực phiên an toàn chống XSS/CSRF, cô lập phiên làm việc đa tab (Tab Session Isolation) và thực thi phân quyền RBAC 3 vai trò chặt chẽ.", 
         COLOR_ROYAL_BLUE),
        
        ("3. BUSINESS & AI LAYER (TẦNG NGHIỆP VỤ & TRÍ TUỆ NHÂN TẠO)", 
         "FastAPI Services • ACID Transactions • Google Gemini API Client • Local Fallback Engine", 
         "Thực thi nghiệp vụ xuất nhập Master-Detail, tính toán Burn-rate, lọc sạch giá vốn qua Data Sanitizer và tự động kích hoạt Fallback khi lỗi mạng.", 
         COLOR_MID_NAVY),
        
        ("4. DATABASE LAYER (TẦNG CƠ SỞ DỮ LIỆU & BẢO TOÀN DỮ LIỆU)", 
         "Dual DB: SQLite WAL (Dev/Test) / PostgreSQL 15 (Prod) • SQLAlchemy 2.0 ORM • 8 B-Tree Indexes", 
         "Thực thi Atomic SQL Decrement, kiểm soát CheckConstraints cấp CSDL, ghi vết sổ Thẻ kho bất biến và tối ưu truy vấn dưới 5ms.", 
         COLOR_DEEP_NAVY)
    ]

    card_y = Inches(1.55)
    card_h = Inches(1.22)
    card_w = Inches(11.73)
    card_gap = Inches(0.16)

    for i, (title, stack, desc, col) in enumerate(layers):
        y = card_y + i * (card_h + card_gap)
        card = slide4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), y, card_w, card_h)
        card.fill.solid()
        card.fill.fore_color.rgb = COLOR_ICE_BLUE
        card.line.color.rgb = COLOR_CARD_BORDER
        card.line.width = Pt(1.5)

        bar = slide4.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), y, Inches(0.18), card_h)
        bar.fill.solid()
        bar.fill.fore_color.rgb = col
        bar.line.fill.background()

        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.35)
        tf.margin_right = Inches(0.3)
        tf.margin_top = Inches(0.12)

        p1 = tf.paragraphs[0]
        p1.text = title
        p1.font.name = FONT_HEADING
        p1.font.size = Pt(15)
        p1.font.bold = True
        p1.font.color.rgb = col
        p1.alignment = PP_ALIGN.LEFT

        p2 = tf.add_paragraph()
        p2.text = f"Công nghệ cốt lõi: {stack}"
        p2.font.name = FONT_HEADING
        p2.font.size = Pt(13)
        p2.font.bold = True
        p2.font.color.rgb = COLOR_TECH_BLUE
        p2.space_before = Pt(3)
        p2.alignment = PP_ALIGN.LEFT

        p3 = tf.add_paragraph()
        p3.text = f"Nhiệm vụ kiến trúc: {desc}"
        p3.font.name = FONT_BODY
        p3.font.size = Pt(12.5)
        p3.font.color.rgb = COLOR_DARK_TEXT
        p3.space_before = Pt(3)
        p3.alignment = PP_ALIGN.LEFT

    add_speaker_notes(slide4,
        "Thời lượng: 75 giây\n"
        "Về mặt kiến trúc, SmartLogis AI được thiết kế theo mô hình phân tầng chặt chẽ (Separation of Concerns):\n"
        "- Tầng Presentation: Kết hợp Jinja2 Server-Side Rendering tối ưu thời gian tải trang ban đầu và WebSocket Client cập nhật thời gian thực không cần reload trang.\n"
        "- Tầng Security: Sử dụng JWT lưu trong Cookie HTTPOnly chống tấn công XSS. Điểm đặc biệt là cơ chế Tab Session Isolation qua header X-Session-User, ngăn chặn lỗi nhầm lẫn tài khoản khi mở nhiều tab.\n"
        "- Tầng Nghiệp vụ: Chứa đựng các Service điều phối giao dịch ACID và phân hệ AI độc lập.\n"
        "- Tầng CSDL: Sử dụng kiến trúc Dual-Database linh hoạt: SQLite WAL cho môi trường kiểm thử cục bộ và PostgreSQL 15 cho môi trường sản xuất, được tối ưu với 8 B-Tree Indexes."
    )

    # =========================================================================
    # SLIDE 5: THIẾT KẾ CSDL - 11 BẢNG CHUẨN HÓA
    # =========================================================================
    slide5 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide5, COLOR_WHITE)
    add_header(slide5, "Thiết Kế CSDL: Mô Hình 11 Bảng Chuẩn Hóa 3NF & Tối Ưu Truy Vấn", "DATABASE DESIGN")

    card_w = Inches(5.7)
    card_h = Inches(4.35)
    xs = [Inches(0.8), Inches(6.83)]

    # Card Trái: Chuẩn hóa 3NF & Thực thể
    card_left = slide5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, xs[0], Inches(1.6), card_w, card_h)
    card_left.fill.solid()
    card_left.fill.fore_color.rgb = COLOR_ICE_BLUE
    card_left.line.color.rgb = COLOR_ROYAL_BLUE
    card_left.line.width = Pt(1.5)

    tf_l = card_left.text_frame
    tf_l.word_wrap = True
    tf_l.margin_left = tf_l.margin_right = Inches(0.3)
    tf_l.margin_top = Inches(0.18)

    pl1 = tf_l.paragraphs[0]
    pl1.text = "📊 11 THỰC THỂ QUAN HỆ CHUẨN HÓA 3NF"
    pl1.font.name = FONT_HEADING
    pl1.font.size = Pt(15)
    pl1.font.bold = True
    pl1.font.color.rgb = COLOR_ROYAL_BLUE
    pl1.alignment = PP_ALIGN.LEFT

    entities = [
        ("nguoi_dung:", "Quản trị tài khoản, mã hóa Bcrypt, phân quyền RBAC 3 vai trò"),
        ("hang_hoa & ton_kho:", "Quan hệ 1-1, kiểm soát số dư khả dụng và tồn an toàn"),
        ("phieu_nhap & chi_tiet:", "Chứng từ nhập kho Master-Detail, lưu trữ nhà cung cấp"),
        ("phieu_xuat & chi_tiet:", "Chứng từ xuất kho Master-Detail, liên kết người nhận"),
        ("the_kho:", "Sổ cái ghi vết toàn bộ lịch sử xuất nhập và số dư lũy kế"),
        ("Danh mục định chuẩn:", "nhom_hang, don_vi_tinh, nha_cung_cap loại bỏ trùng lặp")
    ]
    for tag, desc in entities:
        pe = tf_l.add_paragraph()
        pe.text = f"• {tag} {desc}"
        pe.font.name = FONT_BODY
        pe.font.size = Pt(13)
        pe.font.color.rgb = COLOR_DARK_TEXT
        pe.space_before = Pt(7)
        pe.alignment = PP_ALIGN.LEFT

    # Card Phải: Tối ưu hiệu năng & Ràng buộc
    card_right = slide5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, xs[1], Inches(1.6), card_w, card_h)
    card_right.fill.solid()
    card_right.fill.fore_color.rgb = COLOR_ICE_BLUE
    card_right.line.color.rgb = COLOR_TECH_BLUE
    card_right.line.width = Pt(1.5)

    tf_r = card_right.text_frame
    tf_r.word_wrap = True
    tf_r.margin_left = tf_r.margin_right = Inches(0.3)
    tf_r.margin_top = Inches(0.18)

    pr1 = tf_r.paragraphs[0]
    pr1.text = "⚡ TỐI ƯU HIỆU NĂNG & RÀNG BUỘC TOÀN VẸN"
    pr1.font.name = FONT_HEADING
    pr1.font.size = Pt(15)
    pr1.font.bold = True
    pr1.font.color.rgb = COLOR_TECH_BLUE
    pr1.alignment = PP_ALIGN.LEFT

    optimizations = [
        ("Kiến trúc CSDL kép:", "Hỗ trợ SQLite WAL (Dev/Test) và PostgreSQL 15 (Production)"),
        ("Hardware CheckConstraints:", "SoLuongTon >= 0 và TonSauGiaoDich >= 0"),
        ("Ràng buộc Foreign Key:", "Kích hoạt Foreign Keys ON, loại bỏ hoàn toàn dữ liệu mồ côi"),
        ("8 B-Tree Indexes:", "Đánh trên NgayNhap, NgayXuat, MaNCC, MaPN, MaPX, MaHH"),
        ("Hiệu năng tối ưu:", "Tốc độ phản hồi báo cáo 30 ngày và tra cứu Thẻ kho dưới 5ms")
    ]
    for tag, desc in optimizations:
        po = tf_r.add_paragraph()
        po.text = f"• {tag} {desc}"
        po.font.name = FONT_BODY
        po.font.size = Pt(13)
        po.font.color.rgb = COLOR_DARK_TEXT
        po.space_before = Pt(8)
        po.alignment = PP_ALIGN.LEFT

    # Banner CSDL dưới chân trang
    ban5 = slide5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(6.15), Inches(11.73), Inches(0.8))
    ban5.fill.solid()
    ban5.fill.fore_color.rgb = COLOR_MID_NAVY
    ban5.line.color.rgb = COLOR_CYAN_ACCENT
    ban5.line.width = Pt(1)
    tf_b5 = ban5.text_frame
    pb5 = tf_b5.paragraphs[0]
    pb5.text = "🔒 BẢO TOÀN CSDL: Dual-Database (SQLite WAL / PostgreSQL 15) kết hợp CheckConstraints bảo vệ toàn vẹn dữ liệu."
    pb5.font.name = FONT_HEADING
    pb5.font.size = Pt(13.5)
    pb5.font.bold = True
    pb5.font.color.rgb = COLOR_CYAN_ACCENT
    pb5.alignment = PP_ALIGN.CENTER

    add_speaker_notes(slide5,
        "Thời lượng: 75 giây\n"
        "Cơ sở dữ liệu của SmartLogis AI gồm 11 bảng thực thể đạt chuẩn 3NF:\n"
        "1. Tách biệt rõ ràng: Bảng 'ton_kho' quản lý số dư khả dụng tức thời có quan hệ 1-1 với 'hang_hoa', trong khi 'the_kho' đóng vai trò sổ cái kế toán bất biến ghi nhận mọi biến động xuất nhập.\n"
        "2. Ràng buộc phần cứng: Bên cạnh kiểm tra ở tầng code, chúng em áp dụng CheckConstraint phần cứng cấp CSDL (SoLuongTon >= 0 và TonSauGiaoDich >= 0). Dù có ai can thiệp trực tiếp vào database thì cũng không thể ghi nhận số dư âm.\n"
        "3. Tối ưu hóa truy vấn: Thiết lập 8 B-Tree Indexes chiến lược trên các trường khóa ngoại và mốc thời gian, giúp truy vấn báo cáo luân chuyển 30 ngày đạt tốc độ phản hồi dưới 5ms."
    )

    # =========================================================================
    # SLIDE 6: KỸ THUẬT CỐT LÕI 1 - ATOMIC SQL DECREMENT
    # =========================================================================
    slide6 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide6, COLOR_WHITE)
    add_header(slide6, "Kỹ Thuật Cốt Lõi 1: Atomic SQL Decrement Triệt Tiêu Race Condition", "CORE FEATURE: CONCURRENCY")

    # Card Trái: Nhược điểm cách cũ
    card_bad = slide6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.6), Inches(5.7), Inches(4.35))
    card_bad.fill.solid()
    card_bad.fill.fore_color.rgb = COLOR_ICE_BLUE
    card_bad.line.color.rgb = COLOR_ALERT_RED
    card_bad.line.width = Pt(1.5)
    tf_bad = card_bad.text_frame
    tf_bad.word_wrap = True
    tf_bad.margin_left = tf_bad.margin_right = Inches(0.3)
    tf_bad.margin_top = Inches(0.18)

    p_b1 = tf_bad.paragraphs[0]
    p_b1.text = "❌ CÁCH TIẾP CẬN CŨ: TRỪ TỒN KHO TRONG ỨNG DỤNG"
    p_b1.font.name = FONT_HEADING
    p_b1.font.size = Pt(14.5)
    p_b1.font.bold = True
    p_b1.font.color.rgb = COLOR_ALERT_RED
    p_b1.alignment = PP_ALIGN.LEFT

    bad_points = [
        "Bước 1: Ứng dụng đọc số tồn vào bộ nhớ Python (ton = select())",
        "Bước 2: Hai luồng đọc cùng số dư khả dụng (ví dụ tồn hiện thời = 10)",
        "Bước 3: Cả hai luồng cùng trừ trong bộ nhớ và ghi đè vào CSDL (Lost Update)",
        "HẬU QUẢ: Xuất vượt số lượng thực tế, gây tồn âm và sai lệch sổ sách kế toán"
    ]
    for bp in bad_points:
        p = tf_bad.add_paragraph()
        p.text = f"• {bp}"
        p.font.name = FONT_BODY
        p.font.size = Pt(13)
        p.font.color.rgb = COLOR_DARK_TEXT
        p.space_before = Pt(8)
        p.alignment = PP_ALIGN.LEFT

    # Card Phải: Giải pháp Atomic SQL Decrement
    card_good = slide6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.83), Inches(1.6), Inches(5.7), Inches(4.35))
    card_good.fill.solid()
    card_good.fill.fore_color.rgb = COLOR_ICE_BLUE
    card_good.line.color.rgb = COLOR_SUCCESS_GRN
    card_good.line.width = Pt(1.5)
    tf_good = card_good.text_frame
    tf_good.word_wrap = True
    tf_good.margin_left = tf_good.margin_right = Inches(0.3)
    tf_good.margin_top = Inches(0.18)

    p_g1 = tf_good.paragraphs[0]
    p_g1.text = "✅ GIẢI PHÁP SMARTLOGIS AI: ATOMIC SQL DECREMENT"
    p_g1.font.name = FONT_HEADING
    p_g1.font.size = Pt(14.5)
    p_g1.font.bold = True
    p_g1.font.color.rgb = COLOR_SUCCESS_GRN
    p_g1.alignment = PP_ALIGN.LEFT

    good_points = [
        "Đẩy câu lệnh UPDATE có điều kiện trực tiếp xuống Database Engine",
        "Mệnh đề bảo vệ nguyên tử: WHERE SoLuongTon >= :so_luong_xuat",
        "Database Engine thực thi kiểm tra và cập nhật trong 1 thao tác duy nhất",
        "Nếu hàng không đủ: rowcount == 0 -> Kích hoạt Rollback toàn bộ và trả HTTP 400",
        "KẾT QUẢ: Triệt tiêu 100% Race Condition, bảo đảm nguyên tắc Zero Negative Stock"
    ]
    for gp in good_points:
        p = tf_good.add_paragraph()
        p.text = f"• {gp}"
        p.font.name = FONT_BODY
        p.font.size = Pt(13)
        p.font.color.rgb = COLOR_DARK_TEXT
        p.space_before = Pt(7)
        p.alignment = PP_ALIGN.LEFT

    # Bottom SQL Code Box
    sql_box = slide6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(6.15), Inches(11.73), Inches(0.8))
    sql_box.fill.solid()
    sql_box.fill.fore_color.rgb = COLOR_DEEP_NAVY
    sql_box.line.color.rgb = COLOR_CYAN_ACCENT
    sql_box.line.width = Pt(1)
    tf_sql = sql_box.text_frame
    p_sql = tf_sql.paragraphs[0]
    p_sql.text = "UPDATE ton_kho SET SoLuongTon = SoLuongTon - :so_luong_xuat, CapNhatCuoi = :now WHERE MaHH = :ma_hh AND SoLuongTon >= :so_luong_xuat;"
    p_sql.font.name = FONT_CODE
    p_sql.font.size = Pt(12)
    p_sql.font.bold = True
    p_sql.font.color.rgb = COLOR_CYAN_ACCENT
    p_sql.alignment = PP_ALIGN.CENTER

    add_speaker_notes(slide6,
        "Thời lượng: 80 giây\n"
        "Đây là điểm sáng kỹ thuật quan trọng nhất về mặt toàn vẹn dữ liệu của đồ án:\n"
        "- Ở cách làm thông thường, lập trình viên hay select tồn kho ra một biến Python, kiểm tra 'if ton >= xuat', rồi mới trừ và lưu lại. Khi có hai giao dịch đồng thời cùng đọc tồn kho là 10 và mỗi bên yêu cầu xuất 8, cả hai bên đều thấy đủ hàng và cùng thực thi, dẫn đến tổng xuất là 16 trong khi kho chỉ có 10!\n"
        "- SmartLogis AI giải quyết triệt để vấn đề này bằng Atomic SQL Decrement: Chúng em đưa điều kiện 'WHERE SoLuongTon >= :so_luong_xuat' vào trực tiếp câu lệnh UPDATE. CSDL sẽ khóa dòng và thực thi kiểm tra - trừ tồn trong đúng một thao tác nguyên tử.\n"
        "- Nếu một bên tranh chấp trước làm số lượng còn lại không đủ, CSDL trả về 'rowcount == 0'. Backend bắt được tín hiệu này sẽ lập tức gọi db.rollback() và trả về HTTP 400 báo lỗi rõ ràng."
    )

    # =========================================================================
    # SLIDE 7: KỸ THUẬT CỐT LÕI 2 - QUY TRÌNH NGHIỆP VỤ & PHÂN QUYỀN RBAC
    # =========================================================================
    slide7 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide7, COLOR_WHITE)
    add_header(slide7, "Kỹ Thuật Cốt Lõi 2: Quy Trình Giao Dịch ACID & Phân Quyền RBAC", "CORE FEATURE: WORKFLOW & RBAC")

    # Card chu trình giao dịch ACID Master-Detail trên cùng
    top_w = slide7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.55), Inches(11.73), Inches(1.35))
    top_w.fill.solid()
    top_w.fill.fore_color.rgb = COLOR_ICE_BLUE
    top_w.line.color.rgb = COLOR_ROYAL_BLUE
    top_w.line.width = Pt(1.5)
    tf_tw = top_w.text_frame
    tf_tw.word_wrap = True
    tf_tw.margin_left = tf_tw.margin_right = Inches(0.3)
    tf_tw.margin_top = Inches(0.14)

    ptw1 = tf_tw.paragraphs[0]
    ptw1.text = "🔄 CHU TRÌNH GIAO DỊCH MASTER-DETAIL (100% ACID TRANSACTION)"
    ptw1.font.name = FONT_HEADING
    ptw1.font.size = Pt(14)
    ptw1.font.bold = True
    ptw1.font.color.rgb = COLOR_ROYAL_BLUE
    ptw1.alignment = PP_ALIGN.LEFT

    ptw2 = tf_tw.add_paragraph()
    ptw2.text = "[1. Khởi tạo Master Chứng từ] ➔ [2. Ghi nhận Detail SKU] ➔ [3. Atomic Decrement Tồn kho] ➔ [4. Ghi Sổ Thẻ kho lũy kế]"
    ptw2.font.name = FONT_HEADING
    ptw2.font.size = Pt(13)
    ptw2.font.bold = True
    ptw2.font.color.rgb = COLOR_TECH_BLUE
    ptw2.space_before = Pt(4)
    ptw2.alignment = PP_ALIGN.LEFT

    ptw3 = tf_tw.add_paragraph()
    ptw3.text = "Nguyên tắc All-or-Nothing: Bất kỳ bước nào không hợp lệ, toàn bộ giao dịch được Rollback ngay lập tức."
    ptw3.font.name = FONT_BODY
    ptw3.font.size = Pt(12.5)
    ptw3.font.color.rgb = COLOR_DARK_TEXT
    ptw3.space_before = Pt(3)
    ptw3.alignment = PP_ALIGN.LEFT

    # Bảng ma trận phân quyền RBAC
    rows, cols = 6, 4
    left = Inches(0.8)
    top = Inches(3.05)
    width = Inches(11.73)
    height = Inches(3.9)

    table_shape = slide7.shapes.add_table(rows, cols, left, top, width, height)
    table = table_shape.table
    table.columns[0].width = Inches(3.93)
    table.columns[1].width = Inches(2.6)
    table.columns[2].width = Inches(2.6)
    table.columns[3].width = Inches(2.6)

    table_data = [
        ["NGHIỆP VỤ & TÀI NGUYÊN", "ADMIN HỆ THỐNG", "THỦ KHO KIÊM KẾ TOÁN", "NHÂN VIÊN KHO (STAFF)"],
        ["Quản trị tài khoản & Cấu hình hệ thống", "✅ Toàn quyền quản trị", "❌ Không có quyền", "❌ Không có quyền"],
        ["Quản lý danh mục SKU & Nhà cung cấp", "✅ Toàn quyền quản lý", "✅ Toàn quyền quản lý", "❌ Chế độ chỉ đọc (Read-only)"],
        ["Lập phiếu Nhập / Xuất kho ACID", "✅ Cho phép thực hiện", "✅ Lập phiếu & ghi sổ", "❌ Bị chặn (HTTP 403 / Redirect)"],
        ["Xuất báo cáo tài chính kế toán Excel", "✅ Cho phép thực hiện", "✅ Xuất báo cáo Excel", "❌ Bị chặn (HTTP 403)"],
        ["Tra cứu Tồn kho & Sổ Thẻ kho lũy kế", "✅ Xem toàn bộ dữ liệu", "✅ Tra cứu & cảnh báo", "✅ Tra cứu kiểm đếm hiện trường"]
    ]

    for r_idx, row in enumerate(table_data):
        for c_idx, val in enumerate(row):
            cell = table.cell(r_idx, c_idx)
            cell.text = val
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            p = cell.text_frame.paragraphs[0]
            p.font.name = FONT_HEADING if r_idx == 0 else FONT_BODY
            p.font.size = Pt(12)
            if r_idx == 0:
                p.font.bold = True
                p.font.color.rgb = COLOR_WHITE
                cell.fill.solid()
                cell.fill.fore_color.rgb = COLOR_ROYAL_BLUE
                p.alignment = PP_ALIGN.CENTER if c_idx > 0 else PP_ALIGN.LEFT
            else:
                cell.fill.solid()
                cell.fill.fore_color.rgb = COLOR_ICE_BLUE if r_idx % 2 == 1 else COLOR_WHITE
                p.font.color.rgb = COLOR_DARK_TEXT
                if c_idx > 0:
                    p.alignment = PP_ALIGN.CENTER
                    if "✅" in val:
                        p.font.bold = True
                        p.font.color.rgb = COLOR_SUCCESS_GRN
                    elif "❌" in val:
                        p.font.color.rgb = COLOR_ALERT_RED

    add_speaker_notes(slide7,
        "Thời lượng: 70 giây\n"
        "Về quy trình vận hành và kiểm soát truy cập:\n"
        "1. Chu trình giao dịch ACID 4 bước: Từ tạo Header chứng từ, lưu Detail các SKU, thực thi Atomic Decrement tồn kho, đến ghi nhận biến động Thẻ kho. Tất cả gói gọn trong một Database Transaction. Nếu một SKU bị thiếu hàng, toàn bộ phiếu xuất bị rollback về trạng thái ban đầu, không bao giờ có chuyện xuất dở dang một phần.\n"
        "2. Phân quyền RBAC 3 vai trò: Admin nắm toàn quyền; Thủ kho kiêm Kế toán có đầy đủ thẩm quyền vận hành chứng từ và trích xuất báo cáo kế toán; còn Nhân viên kho chỉ có quyền tra cứu (Read-only) để phục vụ kiểm đếm hiện trường và bị chặn hoàn toàn các thao tác ghi dữ liệu từ tầng Backend."
    )

    # =========================================================================
    # SLIDE 8: TÍCH HỢP AI 1 - DATA SANITIZER KHỬ NHẠY CẢM
    # =========================================================================
    slide8 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide8, COLOR_WHITE)
    add_header(slide8, "Tích Hợp AI 1: Module Data Sanitizer Khử Nhạy Cảm Dữ Liệu", "AI INTEGRATION: PRIVACY")

    # Flow 3 bước lọc ngang trên đầu
    flow_steps = [
        ("1. CSDL KHO NỘI BỘ", "Chứa đơn giá nhập, giá vốn,\nthành tiền và chiết khấu nhà cung cấp", COLOR_MID_NAVY),
        ("2. DATA SANITIZER FILTER", "Thuật toán lọc đệ quy loại bỏ 100%\ncác trường tài chính nhạy cảm", COLOR_TECH_BLUE),
        ("3. SANITIZED CONTEXT CHO AI", "Chỉ gồm mã hàng, tên hàng, số tồn,\ntốc độ Burn-rate & số ngày lưu kho", COLOR_CYAN_ACCENT)
    ]
    fb_w = Inches(3.68)
    fb_h = Inches(1.22)
    start_x = Inches(0.8)
    gap = Inches(0.35)

    for i, (title, desc, col) in enumerate(flow_steps):
        x = start_x + i * (fb_w + gap)
        box = slide8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(1.55), fb_w, fb_h)
        box.fill.solid()
        box.fill.fore_color.rgb = COLOR_ICE_BLUE
        box.line.color.rgb = col
        box.line.width = Pt(1.5)

        tf = box.text_frame
        tf.word_wrap = True
        tf.margin_top = Inches(0.12)
        p1 = tf.paragraphs[0]
        p1.text = title
        p1.font.name = FONT_HEADING
        p1.font.size = Pt(13)
        p1.font.bold = True
        p1.font.color.rgb = col
        p1.alignment = PP_ALIGN.CENTER

        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.name = FONT_BODY
        p2.font.size = Pt(11.5)
        p2.font.color.rgb = COLOR_DARK_TEXT
        p2.alignment = PP_ALIGN.CENTER
        p2.space_before = Pt(3)

    # 2 Cột so sánh chi tiết
    card_w = Inches(5.7)
    card_h = Inches(4.1)
    xs = [Inches(0.8), Inches(6.83)]

    # Card Trái: Trường bị loại bỏ
    c_strip = slide8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, xs[0], Inches(3.0), card_w, card_h)
    c_strip.fill.solid()
    c_strip.fill.fore_color.rgb = COLOR_ICE_BLUE
    c_strip.line.color.rgb = COLOR_ALERT_RED
    c_strip.line.width = Pt(1.5)
    tf_s = c_strip.text_frame
    tf_s.word_wrap = True
    tf_s.margin_left = tf_s.margin_right = Inches(0.3)
    tf_s.margin_top = Inches(0.18)

    ps1 = tf_s.paragraphs[0]
    ps1.text = "❌ DỮ LIỆU TÀI CHÍNH BỊ LOẠI BỎ TRIỆT ĐỂ"
    ps1.font.name = FONT_HEADING
    ps1.font.size = Pt(14.5)
    ps1.font.bold = True
    ps1.font.color.rgb = COLOR_ALERT_RED
    ps1.alignment = PP_ALIGN.LEFT

    stripped_items = [
        "Đơn giá nhập (DonGiaNhap, dongianhap, import_price): Khử sạch 100%",
        "Thành tiền chi tiết (ThanhTien, thanhtien, total_amount): Khử sạch 100%",
        "Giá vốn bình quân (GiaVon, gia_von, cost_price): Khử sạch 100%",
        "Tỷ lệ chiết khấu và chính sách giá mua từ nhà cung cấp: Loại bỏ hoàn toàn",
        "Bảo đảm tuyệt đối bí mật kinh doanh khi sử dụng Public Cloud LLM"
    ]
    for it in stripped_items:
        p = tf_s.add_paragraph()
        p.text = f"• {it}"
        p.font.name = FONT_BODY
        p.font.size = Pt(13)
        p.font.color.rgb = COLOR_DARK_TEXT
        p.space_before = Pt(7)
        p.alignment = PP_ALIGN.LEFT

    # Card Phải: Dữ liệu an toàn được giữ lại
    c_kept = slide8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, xs[1], Inches(3.0), card_w, card_h)
    c_kept.fill.solid()
    c_kept.fill.fore_color.rgb = COLOR_ICE_BLUE
    c_kept.line.color.rgb = COLOR_SUCCESS_GRN
    c_kept.line.width = Pt(1.5)
    tf_k = c_kept.text_frame
    tf_k.word_wrap = True
    tf_k.margin_left = tf_k.margin_right = Inches(0.3)
    tf_k.margin_top = Inches(0.18)

    pk1 = tf_k.paragraphs[0]
    pk1.text = "✅ DỮ LIỆU ĐƯỢC GIỮ LẠI PHỤC VỤ AI PHÂN TÍCH"
    pk1.font.name = FONT_HEADING
    pk1.font.size = Pt(14.5)
    pk1.font.bold = True
    pk1.font.color.rgb = COLOR_SUCCESS_GRN
    pk1.alignment = PP_ALIGN.LEFT

    kept_items = [
        "Mã hàng (MaHH), Tên hàng (TenHH), Đơn vị tính (DVT)",
        "Số lượng tồn kho thực tế và Định mức tồn an toàn tối thiểu (TonToiThieu)",
        "Tốc độ xuất kho bình quân ngày (Burn-rate số lượng / ngày trong 30 ngày)",
        "Số ngày không phát sinh phiếu xuất (Dead Stock metric)",
        "Endpoint kiểm toán minh bạch: GET /api/v1/ai/raw-context"
    ]
    for it in kept_items:
        p = tf_k.add_paragraph()
        p.text = f"• {it}"
        p.font.name = FONT_BODY
        p.font.size = Pt(13)
        p.font.color.rgb = COLOR_DARK_TEXT
        p.space_before = Pt(7)
        p.alignment = PP_ALIGN.LEFT

    add_speaker_notes(slide8,
        "Thời lượng: 75 giây\n"
        "Khi đưa Trí tuệ Nhân tạo đám mây vào doanh nghiệp, thách thức bảo mật lớn nhất là bảo vệ bí mật kinh doanh:\n"
        "- Module Data Sanitizer đóng vai trò một màng lọc bảo mật trung gian. Trước khi bất kỳ tập context nào được gửi sang Google Gemini API, thuật toán quét đệ quy sẽ rà soát và loại bỏ toàn bộ các trường tài chính: đơn giá nhập, thành tiền, giá vốn và chiết khấu.\n"
        "- Tập dữ liệu cung cấp cho AI thuần túy là các chỉ số vận hành vật lý: số lượng tồn, ngưỡng tồn tối thiểu, tốc độ xuất bình quân ngày (Burn-rate) và số ngày nằm kho.\n"
        "- Tính minh bạch này có thể được kiểm chứng tức thời thông qua API GET /api/v1/ai/raw-context trong phần demo."
    )

    # =========================================================================
    # SLIDE 9: TÍCH HỢP AI 2 - PROMPT ENGINEERING & BÁO CÁO 3 PHẦN
    # =========================================================================
    slide9 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide9, COLOR_WHITE)
    add_header(slide9, "Tích Hợp AI 2: Kỹ Thuật Prompt Chống Ảo Giác & Báo Cáo 3 Phần", "AI INTEGRATION: PROMPTS")

    card_w = Inches(5.7)
    card_h = Inches(5.35)
    xs = [Inches(0.8), Inches(6.83)]

    # Card Trái: Anti-Hallucination Prompt
    card_prompt = slide9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, xs[0], Inches(1.55), card_w, card_h)
    card_prompt.fill.solid()
    card_prompt.fill.fore_color.rgb = COLOR_ICE_BLUE
    card_prompt.line.color.rgb = COLOR_ROYAL_BLUE
    card_prompt.line.width = Pt(1.5)
    tf_p = card_prompt.text_frame
    tf_p.word_wrap = True
    tf_p.margin_left = tf_p.margin_right = Inches(0.3)
    tf_p.margin_top = Inches(0.18)

    pp1 = tf_p.paragraphs[0]
    pp1.text = "🤖 KỸ THUẬT ANTI-HALLUCINATION PROMPT"
    pp1.font.name = FONT_HEADING
    pp1.font.size = Pt(14.5)
    pp1.font.bold = True
    pp1.font.color.rgb = COLOR_ROYAL_BLUE
    pp1.alignment = PP_ALIGN.LEFT

    prompt_bullets = [
        "1. System Instruction Đóng Khung Chuyên Môn:",
        "   Định hình AI đóng vai trò Chuyên gia Điều phối Kho vận",
        "   Ràng buộc bất biến: Chỉ lập luận trên dữ liệu JSON thực tế được cấp",
        "2. Nguyên Tắc Trung Thực Số Liệu:",
        "   Nghiêm cấm tự sinh mã SKU, tên hàng hoặc số liệu không có trong context",
        "   Xử lý biên trường hợp kho rỗng: 'Chưa ghi nhận giao dịch trong kỳ'",
        "3. Output Parser Định Chuẩn Cấu Trúc:",
        "   Ép chuẩn định dạng Markdown/JSON phân tầng tường minh",
        "   Phân tích cú pháp tự động để hiển thị trực tiếp lên Dashboard Widget"
    ]
    for b in prompt_bullets:
        p = tf_p.add_paragraph()
        p.text = b
        p.font.name = FONT_BODY
        p.font.size = Pt(12.5)
        p.font.color.rgb = COLOR_DARK_TEXT
        p.space_before = Pt(5)
        p.alignment = PP_ALIGN.LEFT

    # Card Phải: Báo cáo điều hành 3 phần
    card_rep = slide9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, xs[1], Inches(1.55), card_w, card_h)
    card_rep.fill.solid()
    card_rep.fill.fore_color.rgb = COLOR_ICE_BLUE
    card_rep.line.color.rgb = COLOR_TECH_BLUE
    card_rep.line.width = Pt(1.5)
    tf_r = card_rep.text_frame
    tf_r.word_wrap = True
    tf_r.margin_left = tf_r.margin_right = Inches(0.3)
    tf_r.margin_top = Inches(0.18)

    pr1 = tf_r.paragraphs[0]
    pr1.text = "📑 QUY CHUẨN BÁO CÁO ĐIỀU HÀNH 3 PHẦN"
    pr1.font.name = FONT_HEADING
    pr1.font.size = Pt(14.5)
    pr1.font.bold = True
    pr1.font.color.rgb = COLOR_TECH_BLUE
    pr1.alignment = PP_ALIGN.LEFT

    report_bullets = [
        "PHẦN 1: TÌNH TRẠNG TỒN KHO TỔNG QUAN",
        "• Thống kê tổng số SKU, tổng sản lượng xuất kho trong 30 ngày",
        "• Đánh giá tỷ lệ SKU an toàn so với SKU chạm ngưỡng tồn tối thiểu",
        "PHẦN 2: CẢNH BÁO & ĐỀ XUẤT NHẬP HÀNG KHẨN CẤP",
        "• Tính toán thiếu hụt dựa trên tốc độ tiêu thụ hàng ngày (Burn-rate)",
        "• Đề xuất định lượng cụ thể số lượng cần nhập cho từng mã SKU",
        "PHẦN 3: TÓM TẮT BIẾN ĐỘNG BẤT THƯỜNG & DEAD STOCK",
        "• Nhận diện các mặt hàng có lượng xuất đột biến trong kỳ",
        "• Cảnh báo hàng ứ đọng > 60 ngày cần ưu tiên luân chuyển mặt bằng"
    ]
    for b in report_bullets:
        p = tf_r.add_paragraph()
        p.text = b
        p.font.name = FONT_BODY
        p.font.size = Pt(12.5)
        p.font.color.rgb = COLOR_ROYAL_BLUE if ("PHẦN" in b) else COLOR_DARK_TEXT
        p.font.bold = True if ("PHẦN" in b) else False
        p.space_before = Pt(6 if ("PHẦN" in b) else 3)
        p.alignment = PP_ALIGN.LEFT

    add_speaker_notes(slide9,
        "Thời lượng: 75 giây\n"
        "Hiện tượng ảo giác (hallucination) là rủi ro lớn nhất của các mô hình LLM. Nhóm chúng em kiểm soát việc này qua hai kỹ thuật chính:\n"
        "1. Anti-hallucination Prompt: Sử dụng System Instruction đóng khung vai trò chuyên môn của AI, kèm điều khoản cấm tự suy đoán ngoài dữ liệu JSON. Khi kho chưa có dữ liệu, AI phải thông báo trung thực là kho rỗng chứ không được tự sinh ra số liệu giả.\n"
        "2. Báo cáo chuẩn 3 phần: Kết quả trả về được định dạng cấu trúc 3 phần bắt buộc: Phần 1 tổng quan sức khỏe kho; Phần 2 đề xuất nhập hàng dựa trên Burn-rate; và Phần 3 chỉ điểm các SKU bất thường hoặc Dead Stock nằm kho trên 60 ngày. Cấu trúc này giúp người quản lý nắm bắt toàn diện bức tranh kho vận trong chưa đầy 1 phút."
    )

    # =========================================================================
    # SLIDE 10: TÍCH HỢP AI 3 - LOCAL GROUNDED FALLBACK ENGINE
    # =========================================================================
    slide10 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide10, COLOR_WHITE)
    add_header(slide10, "Tích Hợp AI 3: Local Grounded Fallback Engine Sẵn Sàng 24/7", "AI INTEGRATION: RESILIENCE")

    # Flow 3 bước ngang
    steps = [
        ("1. YÊU CẦU BÁO CÁO KHO", "Kích hoạt từ Dashboard điều hành\nhoặc gọi qua API endpoint", COLOR_MID_NAVY),
        ("2. GỌI GOOGLE GEMINI API", "Gửi context JSON sạch, áp dụng\nExponential Backoff tối đa 3 lần", COLOR_TECH_BLUE),
        ("3. ĐIỀU PHỐI DỰ PHÒNG TỰ ĐỘNG", "Thành công (200 OK) -> Hiển thị kết quả LLM\nLỗi mạng / Quota 429 -> Kích hoạt Fallback", COLOR_CYAN_ACCENT)
    ]
    for i, (title, desc, col) in enumerate(steps):
        x = Inches(0.8) + i * (Inches(3.68) + Inches(0.35))
        card = slide10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(1.55), Inches(3.68), Inches(1.25))
        card.fill.solid()
        card.fill.fore_color.rgb = COLOR_ICE_BLUE
        card.line.color.rgb = col
        card.line.width = Pt(1.5)
        tf = card.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        p1.text = title
        p1.font.name = FONT_HEADING
        p1.font.size = Pt(12.5)
        p1.font.bold = True
        p1.font.color.rgb = col
        p1.alignment = PP_ALIGN.CENTER
        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.name = FONT_BODY
        p2.font.size = Pt(11.5)
        p2.font.color.rgb = COLOR_DARK_TEXT
        p2.alignment = PP_ALIGN.CENTER
        p2.space_before = Pt(3)

    # 2 Card so sánh
    c_w = Inches(5.7)
    c_h = Inches(4.0)

    # Trái: Cloud Gemini
    c_cloud = slide10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(3.05), c_w, c_h)
    c_cloud.fill.solid()
    c_cloud.fill.fore_color.rgb = COLOR_ICE_BLUE
    c_cloud.line.color.rgb = COLOR_ROYAL_BLUE
    c_cloud.line.width = Pt(1.5)
    tfc = c_cloud.text_frame
    tfc.word_wrap = True
    tfc.margin_left = tfc.margin_right = Inches(0.3)
    tfc.margin_top = Inches(0.18)
    pc1 = tfc.paragraphs[0]
    pc1.text = "☁️ CHẾ ĐỘ 1: GOOGLE GEMINI CLOUD LLM"
    pc1.font.name = FONT_HEADING
    pc1.font.size = Pt(14.5)
    pc1.font.bold = True
    pc1.font.color.rgb = COLOR_ROYAL_BLUE
    pc1.alignment = PP_ALIGN.LEFT

    cloud_pts = [
        "Ứng dụng mô hình Google Gemini 1.5 / 2.0 (gemini-3.5-flash-lite)",
        "Khả năng phân tích ngôn ngữ tự nhiên và lập luận logic quản trị chuyên sâu",
        "Cơ chế Exponential Backoff tự động retry 3 lần khi gián đoạn mạng",
        "Mang lại báo cáo điều hành chuyên nghiệp với văn phong linh hoạt"
    ]
    for pt in cloud_pts:
        p = tfc.add_paragraph()
        p.text = f"• {pt}"
        p.font.name = FONT_BODY
        p.font.size = Pt(13)
        p.font.color.rgb = COLOR_DARK_TEXT
        p.space_before = Pt(8)
        p.alignment = PP_ALIGN.LEFT

    # Phải: Local Fallback Engine
    c_fall = slide10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.83), Inches(3.05), c_w, c_h)
    c_fall.fill.solid()
    c_fall.fill.fore_color.rgb = COLOR_ICE_BLUE
    c_fall.line.color.rgb = COLOR_SUCCESS_GRN
    c_fall.line.width = Pt(1.5)
    tff = c_fall.text_frame
    tff.word_wrap = True
    tff.margin_left = tff.margin_right = Inches(0.3)
    tff.margin_top = Inches(0.18)
    pf1 = tff.paragraphs[0]
    pf1.text = "🛡️ CHẾ ĐỘ 2: LOCAL GROUNDED FALLBACK ENGINE"
    pf1.font.name = FONT_HEADING
    pf1.font.size = Pt(14.5)
    pf1.font.bold = True
    pf1.font.color.rgb = COLOR_SUCCESS_GRN
    pf1.alignment = PP_ALIGN.LEFT

    fall_pts = [
        "Tự động kích hoạt khi mất kết nối Internet, chưa có API Key hoặc lỗi 429",
        "Giải thuật nội bộ phân tích và tính toán toán học trực tiếp từ CSDL",
        "Đảm bảo sinh báo cáo đủ chuẩn 3 phần với số liệu thực tế 100%",
        "Hoàn toàn độc lập với dịch vụ bên thứ ba, bảo đảm hệ thống không bị crash"
    ]
    for pt in fall_pts:
        p = tff.add_paragraph()
        p.text = f"• {pt}"
        p.font.name = FONT_BODY
        p.font.size = Pt(13)
        p.font.color.rgb = COLOR_DARK_TEXT
        p.space_before = Pt(8)
        p.alignment = PP_ALIGN.LEFT

    add_speaker_notes(slide10,
        "Thời lượng: 70 giây\n"
        "Trong kỹ thuật phần mềm, tính sẵn sàng cao (High Availability) là tiêu chí sống còn:\n"
        "- Một hệ thống quản lý kho không thể ngừng hoạt động chỉ vì nhà cung cấp AI bên ngoài bị nghẽn mạng hoặc hết hạn ngạch truy vấn (HTTP 429 Rate Limit).\n"
        "- Để giải quyết, chúng em xây dựng Local Grounded Fallback Engine: Khi gọi Gemini API gặp lỗi sau 3 lần thử lại Exponential Backoff, hệ thống sẽ âm thầm chuyển sang thuật toán toán học nội bộ.\n"
        "- Thuật toán này truy vấn trực tiếp từ bảng 'ton_kho' và 'the_kho', tính toán Burn-rate và tự sinh báo cáo 3 phần chuẩn xác 100% dựa trên dữ liệu thật. Người dùng vẫn nhận được báo cáo điều hành đầy đủ mà hệ thống không bao giờ bị lỗi sập."
    )

    # =========================================================================
    # SLIDE 11: QUY TRÌNH PHÁT TRIỂN PHẦN MỀM - AGILE SCRUM
    # =========================================================================
    slide11 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide11, COLOR_WHITE)
    add_header(slide11, "Quy Trình Phát Triển Phần Mềm: Mô Hình Agile Scrum 4 Sprints", "SDLC: AGILE SCRUM")

    phases = [
        ("SPRINT 1", "Nền Tảng & ACID", [
            "Khảo sát nghiệp vụ kho và thiết kế ERD 11 bảng chuẩn 3NF",
            "Hiện thực hóa Atomic SQL Decrement chống tồn âm 2 tầng",
            "Xây dựng REST APIs Inbound/Outbound và cấu hình SQLite WAL",
            "Dựng khung giao diện Jinja2 Server-Side Rendering"
        ], COLOR_MID_NAVY),
        ("SPRINT 2", "AI & Data Sanitizer", [
            "Tích hợp Google Gemini Live API với System Instruction",
            "Xây dựng module Data Sanitizer lọc bỏ 100% giá vốn",
            "Hiện thực hóa Local Grounded Fallback Engine ngoại tuyến",
            "Thiết lập endpoint kiểm toán minh bạch /raw-context"
        ], COLOR_ROYAL_BLUE),
        ("SPRINT 3", "Realtime & RBAC", [
            "Tích hợp WebSocket Realtime broadcast biến động kho",
            "Thiết lập phân quyền RBAC 3 vai trò và Tab Session Isolation",
            "Hoàn thiện giao diện Tailwind CSS responsive đa thiết bị",
            "Tích hợp bộ lọc chống cache trình duyệt (Anti-cache Headers)"
        ], COLOR_TECH_BLUE),
        ("SPRINT 4", "Kiểm Thử & Docker", [
            "Xây dựng bộ kiểm thử tự động 65+ Test Cases Pytest",
            "Kiểm thử Concurrency Stress Test và Ledger Sync",
            "Đóng gói Docker Compose (Nginx, FastAPI, PostgreSQL, pgAdmin)",
            "Hoàn thiện tài liệu nghiệm thu và bảo vệ đồ án"
        ], COLOR_CYAN_ACCENT)
    ]

    card_w = Inches(2.7)
    card_h = Inches(4.35)
    start_x = Inches(0.8)
    gap = Inches(0.31)

    for i, (p_num, p_title, bullets, col) in enumerate(phases):
        x = start_x + i * (card_w + gap)
        card = slide11.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(1.55), card_w, card_h)
        card.fill.solid()
        card.fill.fore_color.rgb = COLOR_ICE_BLUE
        card.line.color.rgb = col
        card.line.width = Pt(1.5)

        band = slide11.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(1.55), card_w, Inches(0.92))
        band.fill.solid()
        band.fill.fore_color.rgb = col
        band.line.fill.background()
        tf_b = band.text_frame
        p_b1 = tf_b.paragraphs[0]
        p_b1.text = p_num
        p_b1.font.name = FONT_HEADING
        p_b1.font.size = Pt(12)
        p_b1.font.bold = True
        p_b1.font.color.rgb = COLOR_CYAN_ACCENT if col == COLOR_MID_NAVY else COLOR_WHITE
        p_b1.alignment = PP_ALIGN.CENTER

        p_b2 = tf_b.add_paragraph()
        p_b2.text = p_title
        p_b2.font.name = FONT_HEADING
        p_b2.font.size = Pt(13)
        p_b2.font.bold = True
        p_b2.font.color.rgb = COLOR_WHITE
        p_b2.alignment = PP_ALIGN.CENTER

        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = Inches(0.18)
        tf.margin_top = Inches(1.02)

        for b in bullets:
            pb = tf.add_paragraph()
            pb.text = f"• {b}"
            pb.font.name = FONT_BODY
            pb.font.size = Pt(12)
            pb.font.color.rgb = COLOR_DARK_TEXT
            pb.space_before = Pt(6)
            pb.alignment = PP_ALIGN.LEFT

    # Banner Agile dưới chân trang
    ban11 = slide11.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(6.15), Inches(11.73), Inches(0.8))
    ban11.fill.solid()
    ban11.fill.fore_color.rgb = COLOR_MID_NAVY
    ban11.line.color.rgb = COLOR_CYAN_ACCENT
    ban11.line.width = Pt(1)
    tf_b11 = ban11.text_frame
    pb11 = tf_b11.paragraphs[0]
    pb11.text = "✅ QUY TRÌNH AGILE: 4 Sprint phát triển liên tục, phân công rõ ràng giữa PO và Scrum Master, hoàn thành 100% mục tiêu."
    pb11.font.name = FONT_HEADING
    pb11.font.size = Pt(13)
    pb11.font.bold = True
    pb11.font.color.rgb = COLOR_CYAN_ACCENT
    pb11.alignment = PP_ALIGN.CENTER

    add_speaker_notes(slide11,
        "Thời lượng: 75 giây\n"
        "Đồ án được triển khai theo mô hình Agile Scrum gồm 02 thành viên qua 4 Sprint phát triển rõ ràng:\n"
        "- Sprint 1: Thiết kế ERD 11 bảng chuẩn 3NF, giải quyết bài toán chống tồn âm bằng Atomic SQL Decrement và cấu hình SQLite WAL.\n"
        "- Sprint 2: Hiện thực hóa phân hệ AI với Gemini API, module Data Sanitizer và Local Grounded Fallback Engine.\n"
        "- Sprint 3: Hoàn thiện đồng bộ thời gian thực qua WebSocket, bảo mật phân quyền RBAC 3 vai trò và Tab Session Isolation.\n"
        "- Sprint 4: Viết bộ kiểm thử tự động toàn diện với Pytest, đóng gói Docker Compose và hoàn thiện tài liệu thuyết minh đồ án.\n"
        "Sự phân công rõ ràng giữa PO và Scrum Master giúp dự án duy trì tiến độ ổn định và đạt chất lượng cao."
    )

    # =========================================================================
    # SLIDE 12: ĐẢM BẢO CHẤT LƯỢNG - KIỂM THỬ TỰ ĐỘNG
    # =========================================================================
    slide12 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide12, COLOR_WHITE)
    add_header(slide12, "Chiến Lược Đảm Bảo Chất Lượng: 65+ Test Cases Tự Động (Pytest)", "QUALITY ASSURANCE")

    rows, cols = 6, 4
    left = Inches(0.8)
    top = Inches(1.55)
    width = Inches(11.73)
    height = Inches(4.35)

    table_shape = slide12.shapes.add_table(rows, cols, left, top, width, height)
    t = table_shape.table
    t.columns[0].width = Inches(3.2)
    t.columns[1].width = Inches(1.8)
    t.columns[2].width = Inches(4.73)
    t.columns[3].width = Inches(2.0)

    test_data = [
        ["PHÂN HỆ KIỂM THỬ", "SỐ TEST CASES", "KỊCH BẢN KIỂM THỬ TRỌNG YẾU", "KẾT QUẢ"],
        ["test_phase2_inventory.py", "6 Test Cases", "ACID Inbound/Outbound, Concurrency Stress Test, CheckConstraints cấp CSDL", "✅ 100% PASSED"],
        ["test_inventory_ledger_sync.py", "5 Test Cases", "Bất biến sổ cái Thẻ kho lũy kế (Running Balance Invariant), Anti-cache headers", "✅ 100% PASSED"],
        ["test_ai_engine.py & test_ai_chat.py", "17 Test Cases", "Khử 100% giá vốn, Mocking lỗi 429 Fallback, Chatbot đa chủ đề, Anti-hallucination", "✅ 100% PASSED"],
        ["test_auth_tab_session.py & rbac", "7 Test Cases", "JWT Cookie HTTPOnly, Header X-Session-User cô lập phiên đa tab, chặn RBAC 403", "✅ 100% PASSED"],
        ["test_websocket, exceptions, crud", "31+ Test Cases", "WebSocket Broadcast tức thời, Idempotency Token, Xử lý ngoại lệ, CRUD Master Data", "✅ 100% PASSED"]
    ]

    for r_idx, row in enumerate(test_data):
        for c_idx, val in enumerate(row):
            cell = t.cell(r_idx, c_idx)
            cell.text = val
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            p = cell.text_frame.paragraphs[0]
            p.font.name = FONT_HEADING if r_idx == 0 else FONT_BODY
            p.font.size = Pt(12)
            if r_idx == 0:
                p.font.bold = True
                p.font.color.rgb = COLOR_WHITE
                cell.fill.solid()
                cell.fill.fore_color.rgb = COLOR_ROYAL_BLUE
                p.alignment = PP_ALIGN.CENTER if c_idx != 0 else PP_ALIGN.LEFT
            else:
                cell.fill.solid()
                cell.fill.fore_color.rgb = COLOR_ICE_BLUE if r_idx % 2 == 1 else COLOR_WHITE
                p.font.color.rgb = COLOR_DARK_TEXT
                if c_idx in [1, 3]:
                    p.alignment = PP_ALIGN.CENTER
                if c_idx == 3:
                    p.font.bold = True
                    p.font.color.rgb = COLOR_SUCCESS_GRN

    # Banner tổng nghiệm thu
    ban12 = slide12.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(6.15), Inches(11.73), Inches(0.8))
    ban12.fill.solid()
    ban12.fill.fore_color.rgb = COLOR_MID_NAVY
    ban12.line.color.rgb = COLOR_CYAN_ACCENT
    ban12.line.width = Pt(1)
    tf_b12 = ban12.text_frame
    pb12 = tf_b12.paragraphs[0]
    pb12.text = "🏆 TỔNG KẾT KIỂM THỬ: 66/66 TEST CASES TỰ ĐỘNG (100% PASSED) TRONG ~40 GIÂY THỰC THI PYTEST!"
    pb12.font.name = FONT_HEADING
    pb12.font.size = Pt(13)
    pb12.font.bold = True
    pb12.font.color.rgb = COLOR_CYAN_ACCENT
    pb12.alignment = PP_ALIGN.CENTER

    add_speaker_notes(slide12,
        "Thời lượng: 80 giây\n"
        "Để đảm bảo chất lượng phần mềm theo chuẩn kỹ thuật, nhóm nghiên cứu đã xây dựng bộ kiểm thử tự động toàn diện với 66 Test Cases sử dụng Pytest:\n"
        "- Bài kiểm thử Concurrency Stress Test: Sử dụng ThreadPoolExecutor giả lập nhiều luồng thủ kho cùng gửi yêu cầu xuất kho tại cùng một mili-giây. Kết quả khẳng định số tồn kho dừng lại chính xác tại 0, không bao giờ bị âm.\n"
        "- Bài kiểm thử Ledger Sync: Kiểm chứng tính bất biến giữa số dư lũy kế trên Thẻ kho và số tồn thực tế trong bảng ton_kho qua chuỗi nhiều giao dịch liên tiếp.\n"
        "- Bài kiểm thử AI Security: Kiểm tra tự động 100% payload nạp cho Gemini, xác nhận không có bất kỳ trường giá nhập hay thành tiền nào lọt qua.\n"
        "Toàn bộ 66 test cases đều vượt qua 100% trong khoảng 40 giây thực thi."
    )

    # =========================================================================
    # SLIDE 13: ĐÓNG GÓI TRIỂN KHAI & ĐỒNG BỘ ĐA THIẾT BỊ
    # =========================================================================
    slide13 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide13, COLOR_WHITE)
    add_header(slide13, "Đóng Gói Triển Khai Docker & Đồng Bộ Thời Gian Thực Đa Thiết Bị", "DEPLOYMENT & REALTIME")

    containers = [
        ("GATEWAY (NGINX)", "Reverse Proxy Cổng Vào", "Lắng nghe Port 80 & 443 SSL, cân bằng tải, định tuyến Web & WebSocket", COLOR_ROYAL_BLUE),
        ("BACKEND (FASTAPI)", "Máy Chủ Ứng Dụng", "Python 3.12, Uvicorn ASGI, xử lý nghiệp vụ ACID và điều phối AI", COLOR_TECH_BLUE),
        ("DATABASE (POSTGRESQL)", "CSDL Quan Hệ Tập Trung", "PostgreSQL 15, volume lưu trữ dữ liệu bền bỉ postgres_data", COLOR_MID_NAVY),
        ("ADMIN TOOLS (PGADMIN)", "Quản Trị Trực Quan", "pgAdmin 4 tại cổng 5050 hỗ trợ quản trị viên giám sát CSDL", COLOR_CYAN_ACCENT)
    ]

    c_w = Inches(2.7)
    c_h = Inches(2.25)
    start_x = Inches(0.8)
    gap = Inches(0.31)

    for i, (name, role, desc, col) in enumerate(containers):
        x = start_x + i * (c_w + gap)
        card = slide13.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(1.55), c_w, c_h)
        card.fill.solid()
        card.fill.fore_color.rgb = COLOR_ICE_BLUE
        card.line.color.rgb = col
        card.line.width = Pt(1.5)

        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = Inches(0.18)
        tf.margin_top = Inches(0.14)

        p1 = tf.paragraphs[0]
        p1.text = name
        p1.font.name = FONT_HEADING
        p1.font.size = Pt(12.5)
        p1.font.bold = True
        p1.font.color.rgb = col
        p1.alignment = PP_ALIGN.LEFT

        p2 = tf.add_paragraph()
        p2.text = role
        p2.font.name = FONT_HEADING
        p2.font.size = Pt(11.5)
        p2.font.bold = True
        p2.font.color.rgb = COLOR_DARK_TEXT
        p2.space_before = Pt(3)
        p2.alignment = PP_ALIGN.LEFT

        p3 = tf.add_paragraph()
        p3.text = desc
        p3.font.name = FONT_BODY
        p3.font.size = Pt(11)
        p3.font.color.rgb = COLOR_MUTED_TEXT
        p3.space_before = Pt(3)
        p3.alignment = PP_ALIGN.LEFT

    # Card mạng LAN & Đồng bộ Realtime đa thiết bị
    card_net = slide13.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(4.05), Inches(11.73), Inches(2.9))
    card_net.fill.solid()
    card_net.fill.fore_color.rgb = COLOR_DEEP_NAVY
    card_net.line.color.rgb = COLOR_CYAN_ACCENT
    card_net.line.width = Pt(1.5)

    tf_n = card_net.text_frame
    tf_n.word_wrap = True
    tf_n.margin_left = tf_n.margin_right = Inches(0.35)
    tf_n.margin_top = Inches(0.2)

    pn1 = tf_n.paragraphs[0]
    pn1.text = "🌐 KHẢ NĂNG TRUY CẬP ĐA THIẾT BỊ & ĐỒNG BỘ REALTIME TRONG MẠNG LAN DOANH NGHIỆP"
    pn1.font.name = FONT_HEADING
    pn1.font.size = Pt(14)
    pn1.font.bold = True
    pn1.font.color.rgb = COLOR_CYAN_ACCENT
    pn1.alignment = PP_ALIGN.LEFT

    net_points = [
        "1. Truy cập Máy chủ Cục bộ (Localhost): http://localhost  |  HTTPS SSL: https://localhost",
        "2. Truy cập Tên miền Nội bộ: http://smartlogis-ai.com qua DNS / file hosts nội bộ",
        "3. Truy cập Thiết bị Di động (Mobile / Tablet cùng Wi-Fi): http://192.168.x.x (Thủ kho kiểm đếm tại bãi)",
        "4. Đồng bộ Thời gian thực (Realtime WebSocket): Biến động kho broadcast tức thời tới mọi thiết bị kết nối",
        "5. Khởi chạy 1-Click tự động: Tệp script run_app.bat (Windows) hoặc Docker Compose sẵn sàng vận hành"
    ]
    for np in net_points:
        p = tf_n.add_paragraph()
        p.text = np
        p.font.name = FONT_BODY
        p.font.size = Pt(12.5)
        p.font.color.rgb = COLOR_WHITE
        p.space_before = Pt(5)
        p.alignment = PP_ALIGN.LEFT

    add_speaker_notes(slide13,
        "Thời lượng: 75 giây\n"
        "Về mô hình triển khai và khả năng kết nối đa thiết bị:\n"
        "- Hệ thống được đóng gói hoàn chỉnh bằng Docker Compose với 4 container độc lập: Nginx Reverse Proxy làm cổng vào bảo mật HTTPS; FastAPI Backend xử lý ứng dụng; PostgreSQL 15 quản trị dữ liệu; và pgAdmin 4 phục vụ quản trị.\n"
        "- Điểm mạnh thực tiễn là khả năng hỗ trợ truy cập đa thiết bị trong mạng LAN: Thủ kho có thể cầm điện thoại di động hoặc máy tính bảng kết nối qua Wi-Fi nội bộ để thao tác kiểm đếm trực tiếp tại kho bãi.\n"
        "- Khi một phiếu xuất hoặc nhập được lập thành công, WebSocket Manager sẽ broadcast ngay lập tức một gói tin sự kiện tới tất cả các thiết bị đang mở màn hình, giúp số dư tồn kho đồng bộ tức thì dưới 100 mili-giây mà không cần tải lại trang."
    )

    # =========================================================================
    # SLIDE 14: KỊCH BẢN THỰC NGHIỆM DEMO
    # =========================================================================
    slide14 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide14, COLOR_WHITE)
    add_header(slide14, "Kịch Bản Thực Nghiệm Demo Hệ Thống (Lộ Trình 5 Phút Mạch Lạc)", "LIVE DEMONSTRATION")

    rows, cols = 6, 3
    left = Inches(0.8)
    top = Inches(1.55)
    width = Inches(11.73)
    height = Inches(5.4)

    table_shape = slide14.shapes.add_table(rows, cols, left, top, width, height)
    t = table_shape.table
    t.columns[0].width = Inches(1.8)
    t.columns[1].width = Inches(4.6)
    t.columns[2].width = Inches(5.33)

    demo_data = [
        ["THỜI GIAN", "THAO TÁC THỰC HIỆN TRÊN HỆ THỐNG", "MỤC TIÊU & KẾT QUẢ KỲ VỌNG"],
        ["Phút 1", "Đăng nhập Thủ kho (thukho) và Nhân viên (nhanvien)", "Kiểm chứng phân quyền RBAC: Thủ kho có nút Lập phiếu; Nhân viên ở chế độ chỉ đọc"],
        ["Phút 2", "Bấm 'Báo Cáo 3 Phần' trên AI Widget", "Google Gemini tính toán Burn-rate, đề xuất nhập hàng và cảnh báo Dead Stock"],
        ["Phút 3", "Thử nghiệm xuất vượt số lượng tồn kho khả dụng", "Giao diện cảnh báo; Backend từ chối ngay lập tức với mã lỗi HTTP 400 Bad Request"],
        ["Phút 4", "Lập phiếu nhập kho & Tra cứu sổ Thẻ kho", "Giao dịch Master-Detail thành công; Sổ Thẻ kho tự động cập nhật số dư lũy kế"],
        ["Phút 5", "Mở Swagger UI kiểm tra API /raw-context", "Kiểm toán minh bạch: Chứng minh 100% dữ liệu nạp cho AI không chứa giá vốn"]
    ]

    for r_idx, row in enumerate(demo_data):
        for c_idx, val in enumerate(row):
            cell = t.cell(r_idx, c_idx)
            cell.text = val
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            p = cell.text_frame.paragraphs[0]
            p.font.name = FONT_HEADING if r_idx == 0 else FONT_BODY
            p.font.size = Pt(12.5)
            if r_idx == 0:
                p.font.bold = True
                p.font.color.rgb = COLOR_WHITE
                cell.fill.solid()
                cell.fill.fore_color.rgb = COLOR_ROYAL_BLUE
                p.alignment = PP_ALIGN.CENTER if c_idx == 0 else PP_ALIGN.LEFT
            else:
                cell.fill.solid()
                cell.fill.fore_color.rgb = COLOR_ICE_BLUE if r_idx % 2 == 1 else COLOR_WHITE
                p.font.color.rgb = COLOR_DARK_TEXT
                if c_idx == 0:
                    p.alignment = PP_ALIGN.CENTER
                    p.font.bold = True
                    p.font.color.rgb = COLOR_TECH_BLUE

    add_speaker_notes(slide14,
        "Thời lượng: 60 giây\n"
        "Kính thưa Hội đồng, để kiểm chứng các tính năng kỹ thuật đã trình bày, nhóm chúng em xin phép được thực hiện phần Live Demo trực tiếp trong 5 phút:\n"
        "- Phút 1: Trình diễn ma trận phân quyền RBAC qua 2 tài khoản 'thukho' và 'nhanvien' trên 2 tab trình duyệt riêng biệt.\n"
        "- Phút 2: Tương tác với Trợ lý AI để xuất Báo cáo 3 phần phân tích sức khỏe kho và đề xuất nhập hàng dựa trên Burn-rate.\n"
        "- Phút 3: Trực tiếp gửi yêu cầu xuất vượt tồn kho để quan sát cơ chế Atomic SQL Decrement chặn lỗi 400 và bảo toàn số dư.\n"
        "- Phút 4: Lập phiếu nhập và kiểm tra sự đồng bộ tức thì của sổ cái Thẻ kho lũy kế.\n"
        "- Phút 5: Mở API /raw-context để Hội đồng kiểm toán tính năng khử sạch 100% giá vốn của Data Sanitizer."
    )

    # =========================================================================
    # SLIDE 15: TỔNG KẾT & ĐỊNH HƯỚNG PHÁT TRIỂN (Hero Dark Navy)
    # =========================================================================
    slide15 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide15, COLOR_DEEP_NAVY)

    # Dải viền Cyan trên đỉnh
    top_bar = slide15.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.14))
    top_bar.fill.solid()
    top_bar.fill.fore_color.rgb = COLOR_CYAN_ACCENT
    top_bar.line.fill.background()

    add_header(slide15, "Tổng Kết Đề Tài & Định Hướng Phát Triển Tương Lai", "CONCLUSION & ROADMAP", is_dark=True)

    card_w = Inches(5.7)
    card_h = Inches(4.25)
    xs = [Inches(0.8), Inches(6.83)]

    # Card Trái: Thành tựu kỹ thuật
    card_ach = slide15.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, xs[0], Inches(1.55), card_w, card_h)
    card_ach.fill.solid()
    card_ach.fill.fore_color.rgb = COLOR_CARD_DARK
    card_ach.line.color.rgb = COLOR_TECH_BLUE
    card_ach.line.width = Pt(1.5)
    tfa = card_ach.text_frame
    tfa.word_wrap = True
    tfa.margin_left = tfa.margin_right = Inches(0.3)
    tfa.margin_top = Inches(0.18)

    pa1 = tfa.paragraphs[0]
    pa1.text = "🏆 KẾT QUẢ & THÀNH TỰU ĐẠT ĐƯỢC"
    pa1.font.name = FONT_HEADING
    pa1.font.size = Pt(15)
    pa1.font.bold = True
    pa1.font.color.rgb = COLOR_CYAN_ACCENT
    pa1.alignment = PP_ALIGN.LEFT

    achs = [
        "Bảo toàn giao dịch ACID: Triệt tiêu hoàn toàn rủi ro tồn âm và Lost Update",
        "Trợ lý AI thực tiễn: Khử sạch 100% giá vốn nhạy cảm, cung cấp báo cáo 3 phần",
        "Kiến trúc mở & tin cậy: Đồng bộ WebSocket đa thiết bị, phân quyền RBAC 3 vai trò",
        "Đảm bảo chất lượng: 66/66 Test Cases Pytest bao phủ toàn diện các phân hệ cốt lõi"
    ]
    for ac in achs:
        p = tfa.add_paragraph()
        p.text = f"• {ac}"
        p.font.name = FONT_BODY
        p.font.size = Pt(13)
        p.font.color.rgb = COLOR_WHITE
        p.space_before = Pt(8)
        p.alignment = PP_ALIGN.LEFT

    # Card Phải: Hướng phát triển
    card_road = slide15.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, xs[1], Inches(1.55), card_w, card_h)
    card_road.fill.solid()
    card_road.fill.fore_color.rgb = COLOR_CARD_DARK
    card_road.line.color.rgb = COLOR_CYAN_ACCENT
    card_road.line.width = Pt(1.5)
    tfr = card_road.text_frame
    tfr.word_wrap = True
    tfr.margin_left = tfr.margin_right = Inches(0.3)
    tfr.margin_top = Inches(0.18)

    pr1 = tfr.paragraphs[0]
    pr1.text = "🚀 ĐỊNH HƯỚNG MỞ RỘNG TƯƠNG LAI"
    pr1.font.name = FONT_HEADING
    pr1.font.size = Pt(15)
    pr1.font.bold = True
    pr1.font.color.rgb = COLOR_CYAN_ACCENT
    pr1.alignment = PP_ALIGN.LEFT

    roads = [
        "Dự báo nhu cầu nâng cao: Tích hợp mô hình chuỗi thời gian (ARIMA / ML)",
        "Ứng dụng di động Native: Xây dựng App Flutter / React Native quét mã QR/RFID",
        "Bản đồ kho thông minh (Smart Bin Location): Tối ưu sơ đồ vị trí và đường đi lấy hàng",
        "Tích hợp chuẩn ERP: Kết nối API trao đổi dữ liệu với Odoo, SAP, Fast Accounting"
    ]
    for rd in roads:
        p = tfr.add_paragraph()
        p.text = f"• {rd}"
        p.font.name = FONT_BODY
        p.font.size = Pt(13)
        p.font.color.rgb = COLOR_WHITE
        p.space_before = Pt(8)
        p.alignment = PP_ALIGN.LEFT

    # Card Cảm ơn trang trọng dưới cùng
    ban15 = slide15.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(6.05), Inches(11.73), Inches(0.95))
    ban15.fill.solid()
    ban15.fill.fore_color.rgb = COLOR_ROYAL_BLUE
    ban15.line.color.rgb = COLOR_CYAN_ACCENT
    ban15.line.width = Pt(1.5)
    tf_b15 = ban15.text_frame
    pb15_1 = tf_b15.paragraphs[0]
    pb15_1.text = "🌟 TRÂN TRỌNG CẢM ƠN QUÝ THẦY/CÔ TRONG HỘI ĐỒNG ĐÃ CHÚ Ý LẮNG NGHE!"
    pb15_1.font.name = FONT_HEADING
    pb15_1.font.size = Pt(14.5)
    pb15_1.font.bold = True
    pb15_1.font.color.rgb = COLOR_WHITE
    pb15_1.alignment = PP_ALIGN.CENTER

    pb15_2 = tf_b15.add_paragraph()
    pb15_2.text = "Nhóm sinh viên thực hiện xin sẵn sàng tiếp thu ý kiến đóng góp và trả lời các câu hỏi phản biện."
    pb15_2.font.name = FONT_BODY
    pb15_2.font.size = Pt(12.5)
    pb15_2.font.color.rgb = COLOR_CYAN_ACCENT
    pb15_2.alignment = PP_ALIGN.CENTER
    pb15_2.space_before = Pt(4)

    add_speaker_notes(slide15,
        "Thời lượng: 60 giây\n"
        "Kính thưa Quý Thầy/Cô trong Hội đồng!\n"
        "Đề tài SmartLogis AI đã hoàn thành 100% mục tiêu đề ra: xây dựng thành công một giải pháp quản lý kho bảo toàn giao dịch ACID chống tồn âm, tích hợp trợ lý Trí tuệ Nhân tạo hỗ trợ điều hành nhưng vẫn bảo mật tuyệt đối bí mật kinh doanh, và đạt độ phủ kiểm thử tự động 66/66 test cases.\n"
        "Trong giai đoạn tiếp theo, nhóm nghiên cứu dự kiến sẽ phát triển ứng dụng di động quét mã QR/RFID tại kho bãi và mở rộng thuật toán học máy chuỗi thời gian để nâng cao độ chính xác dự báo theo mùa vụ.\n"
        "Nhóm chúng em xin trân trọng cảm ơn sự hướng dẫn tận tình của Quý Thầy/Cô. Chúng em xin sẵn sàng lắng nghe các ý kiến nhận xét và trả lời câu hỏi phản biện từ Hội đồng!"
    )

    # Lưu file kết quả
    output_path = os.path.join("docs", "SmartLogis_AI_Presentation_Deck.pptx")
    prs.save(output_path)
    print(f"[OK] Presentation successfully regenerated: {output_path}")

if __name__ == "__main__":
    create_deck()
