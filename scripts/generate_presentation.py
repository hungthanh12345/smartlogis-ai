"""
SmartLogis AI - PowerPoint Presentation Deck Generator (v3 - Larger Fonts & High Legibility)
Key Improvements:
- Globally scaled up font sizes across ALL 15 slides:
  * Slide Titles: 26pt - 28pt Bold
  * Section Pills: 12pt - 13pt Bold
  * Card Titles & Headers: 15.5pt - 16.5pt Bold
  * Subheadings / Tech Labels: 13.5pt - 14.5pt Bold
  * Body Text & Bullet Points: 13pt - 14pt (significantly more legible and prominent)
  * Tables & Matrices: 13pt - 13.5pt text with 14pt headers
  * Bottom Banners: 13.5pt - 14.5pt Bold
- Maintained strict left alignment on Slide 4 and balanced margin distributions throughout.
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# -------------------------------------------------------------
# COLOR PALETTE (Primary Blue Scheme)
# -------------------------------------------------------------
COLOR_DEEP_NAVY   = RGBColor(10, 25, 47)      # #0A192F (Dark background, Hero)
COLOR_MID_NAVY    = RGBColor(15, 35, 65)      # #0F2341 (Subtle dark background)
COLOR_ROYAL_BLUE  = RGBColor(30, 58, 138)     # #1E3A8A (Header bars, primary accents)
COLOR_TECH_BLUE   = RGBColor(37, 99, 235)     # #2563EB (Vibrant action items, pills)
COLOR_CYAN_ACCENT = RGBColor(6, 182, 212)     # #06B6D4 (Key highlights, icons, KPIs)
COLOR_ICE_BLUE    = RGBColor(240, 247, 255)   # #F0F7FF (Card background)
COLOR_CARD_BORDER = RGBColor(191, 219, 254)   # #BFDBFE (Card borders)
COLOR_CARD_DARK   = RGBColor(20, 42, 77)      # #142A4D (Card background on dark slides)
COLOR_WHITE       = RGBColor(255, 255, 255)   # #FFFFFF
COLOR_DARK_TEXT   = RGBColor(15, 23, 42)      # #0F172A (Primary text on light)
COLOR_MUTED_TEXT  = RGBColor(51, 65, 85)      # #334155 (Secondary text on light)
COLOR_LIGHT_MUTED = RGBColor(148, 163, 184)   # #94A3B8 (Secondary text on dark)
COLOR_ALERT_RED   = RGBColor(225, 29, 72)     # #E11D48 (Negative highlight)
COLOR_SUCCESS_GRN = RGBColor(16, 185, 129)    # #10B981 (Success highlight)

FONT_HEADING = "Segoe UI"
FONT_BODY    = "Segoe UI"

def set_slide_background(slide, color):
    """Sets a solid color background for the slide."""
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = color

def add_header(slide, title_text, category_badge="SMARTLOGIS AI", is_dark=False):
    """Adds a standard header with category badge and action title."""
    # Category badge pill
    badge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.38), Inches(2.5), Inches(0.38))
    badge.fill.solid()
    badge.fill.fore_color.rgb = COLOR_TECH_BLUE if is_dark else COLOR_ROYAL_BLUE
    badge.line.color.rgb = COLOR_CYAN_ACCENT if is_dark else COLOR_TECH_BLUE
    badge.line.width = Pt(1.5)
    tf_b = badge.text_frame
    tf_b.word_wrap = True
    p_b = tf_b.paragraphs[0]
    p_b.text = category_badge
    p_b.font.name = FONT_HEADING
    p_b.font.size = Pt(12)
    p_b.font.bold = True
    p_b.font.color.rgb = COLOR_WHITE
    p_b.alignment = PP_ALIGN.CENTER

    # Title text
    txBox = slide.shapes.add_textbox(Inches(0.8), Inches(0.78), Inches(11.73), Inches(0.75))
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
    """Embeds formatted speaker notes into the PowerPoint slide."""
    notes_slide = slide.notes_slide
    text_frame = notes_slide.notes_text_frame
    text_frame.text = notes_text

def create_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_slide_layout = prs.slide_layouts[6]

    # =========================================================================
    # SLIDE 1: TITLE / COVER (Hero Dark Navy)
    # =========================================================================
    slide1 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(slide1, COLOR_DEEP_NAVY)

    # Accent decorative top bar
    top_bar = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.14))
    top_bar.fill.solid()
    top_bar.fill.fore_color.rgb = COLOR_CYAN_ACCENT
    top_bar.line.fill.background()

    # Project Tag Badge
    tag = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(0.85), Inches(3.8), Inches(0.44))
    tag.fill.solid()
    tag.fill.fore_color.rgb = COLOR_ROYAL_BLUE
    tag.line.color.rgb = COLOR_CYAN_ACCENT
    tag.line.width = Pt(1.5)
    tf_tag = tag.text_frame
    p_tag = tf_tag.paragraphs[0]
    p_tag.text = "SMARTLOGIS AI • PRODUCTION V4.0"
    p_tag.font.name = FONT_HEADING
    p_tag.font.size = Pt(12.5)
    p_tag.font.bold = True
    p_tag.font.color.rgb = COLOR_CYAN_ACCENT
    p_tag.alignment = PP_ALIGN.CENTER

    # Main Title
    title_box = slide1.shapes.add_textbox(Inches(1.0), Inches(1.45), Inches(11.3), Inches(1.9))
    tf_title = title_box.text_frame
    tf_title.word_wrap = True
    p_t1 = tf_title.paragraphs[0]
    p_t1.text = "HỆ THỐNG QUẢN LÝ KHO THÔNG MINH"
    p_t1.font.name = FONT_HEADING
    p_t1.font.size = Pt(40)
    p_t1.font.bold = True
    p_t1.font.color.rgb = COLOR_WHITE

    p_t2 = tf_title.add_paragraph()
    p_t2.text = "TÍCH HỢP AI & BẢO TOÀN GIAO DỊCH ACID"
    p_t2.font.name = FONT_HEADING
    p_t2.font.size = Pt(36)
    p_t2.font.bold = True
    p_t2.font.color.rgb = COLOR_CYAN_ACCENT
    p_t2.space_before = Pt(4)

    # Subtitle
    sub_box = slide1.shapes.add_textbox(Inches(1.0), Inches(3.55), Inches(11.3), Inches(0.6))
    tf_sub = sub_box.text_frame
    p_sub = tf_sub.paragraphs[0]
    p_sub.text = "Giải Pháp Quản Trị Kho Vận Vật Tư Công Trình: Chống Tồn Âm 2 Tầng & Trợ Lý Google Gemini"
    p_sub.font.name = FONT_BODY
    p_sub.font.size = Pt(18)
    p_sub.font.color.rgb = COLOR_LIGHT_MUTED

    # 3 Key Value Metric Cards
    pillars = [
        ("🛡️ 100% ACID CONCURRENCY", "Loại bỏ hoàn toàn lỗi Tồn âm", "Atomic SQL Decrement & DB CheckConstraints bảo vệ 2 tầng"),
        ("🧠 GOOGLE GEMINI LLM", "Trợ lý Điều hành Tự động", "Data Sanitizer bảo vệ 100% bí mật giá vốn khi phân tích"),
        ("🚀 PRODUCTION DOCKER", "Sẵn sàng Triển khai Thực tế", "Nginx SSL Gateway & Hỗ trợ đa thiết bị Mobile/Tablet mạng LAN")
    ]
    card_w = Inches(3.58)
    card_gap = Inches(0.28)
    start_x = Inches(1.0)
    for i, (head, sub1, sub2) in enumerate(pillars):
        x = start_x + i * (card_w + card_gap)
        card = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(4.35), card_w, Inches(2.05))
        card.fill.solid()
        card.fill.fore_color.rgb = COLOR_CARD_DARK
        card.line.color.rgb = COLOR_TECH_BLUE
        card.line.width = Pt(1.5)
        tf_c = card.text_frame
        tf_c.word_wrap = True
        tf_c.margin_left = tf_c.margin_right = Inches(0.25)
        tf_c.margin_top = Inches(0.2)
        
        p1 = tf_c.paragraphs[0]
        p1.text = head
        p1.font.name = FONT_HEADING
        p1.font.size = Pt(15)
        p1.font.bold = True
        p1.font.color.rgb = COLOR_CYAN_ACCENT

        p2 = tf_c.add_paragraph()
        p2.text = sub1
        p2.font.name = FONT_BODY
        p2.font.size = Pt(14)
        p2.font.bold = True
        p2.font.color.rgb = COLOR_WHITE
        p2.space_before = Pt(6)

        p3 = tf_c.add_paragraph()
        p3.text = f"• {sub2}"
        p3.font.name = FONT_BODY
        p3.font.size = Pt(13)
        p3.font.color.rgb = COLOR_LIGHT_MUTED
        p3.space_before = Pt(5)

    # Footer team info
    foot_box = slide1.shapes.add_textbox(Inches(1.0), Inches(6.65), Inches(11.3), Inches(0.5))
    tf_f = foot_box.text_frame
    p_f = tf_f.paragraphs[0]
    p_f.text = "Đội ngũ Thực hiện: Nguyễn Thành Hưng (Admin) • Hoàng Tiến Đạt (Thủ kho kiêm KT) | Đồ Án Tốt Nghiệp"
    p_f.font.name = FONT_BODY
    p_f.font.size = Pt(13.5)
    p_f.font.color.rgb = COLOR_LIGHT_MUTED

    add_speaker_notes(slide1, 
        "Thời lượng: 60s\n"
        "Lời thoại: Kính thưa Thầy/Cô trong Hội đồng! Trong kỷ nguyên chuỗi cung ứng số hóa, kho vận là trái tim luân chuyển dòng vốn. Hôm nay chúng em xin trân trọng giới thiệu SmartLogis AI - Hệ Thống Quản Lý Kho Thông Minh Tích Hợp AI và Bảo Toàn Giao Dịch ACID. Hệ thống giải quyết triệt để vấn đề mất mát dữ liệu và xung đột tồn kho bằng giải thuật Atomic SQL Decrement, đồng thời tích hợp Trợ lý Trí tuệ Nhân tạo Google Gemini giúp ban điều hành ra quyết định chính xác.\n"
        "Mẹo tương tác: Giọng tự tin, nhấn mạnh 100% ACID và Google Gemini AI."
    )

    # =========================================================================
    # SLIDE 2: PROBLEM STATEMENT (4 Nỗi Đau Quản Lý Kho)
    # =========================================================================
    slide2 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(slide2, COLOR_WHITE)
    add_header(slide2, "Thực Trạng & 4 Nỗi Đau Lớn Trong Quản Trị Kho Vật Tư", "PROBLEM STATEMENT")

    problems = [
        ("⚠️ 1. TỒN KHO ÂM (NEGATIVE STOCK)", 
         "Lỗi Race Condition & Lost Update Khi Xuất Đồng Thời", 
         [
             "Nhiều thủ kho cùng xuất một mặt hàng tại cùng thời điểm",
             "Hệ thống không khóa dòng dẫn đến xuất vượt số lượng có thực",
             "Sai lệch sổ sách nghiêm trọng giữa thủ kho và kế toán công ty"
         ], COLOR_ALERT_RED),
        ("⛓️ 2. ĐỨT GÃY CHUỖI CUNG ỨNG", 
         "Cạn Kiệt Vật Tư Do Thiếu Dự Báo Tốc Độ Tiêu Thụ", 
         [
             "Không theo dõi tốc độ tiêu thụ hàng ngày (Burn-rate tiêu chuẩn)",
             "Hàng chạm ngưỡng cạn kiệt mới phát hiện để đặt nhà cung cấp",
             "Gây chậm tiến độ thi công toàn bộ dây chuyền công trình xây dựng"
         ], COLOR_ROYAL_BLUE),
        ("📦 3. ĐỌNG VỐN (DEAD STOCK)", 
         "Lãng Phí Hàng Chục Tỷ Đồng Lưu Kho Không Luân Chuyển", 
         [
             "Nhiều SKU vật tư giá trị cao nằm kho > 60 ngày không ai hay biết",
             "Chiếm dụng diện tích mặt bằng và phát sinh chi phí lưu bãi lớn",
             "Ban giám đốc thiếu công cụ tự động cảnh báo để giải phóng hàng"
         ], COLOR_ROYAL_BLUE),
        ("🔒 4. RỦI RO LỘ BÍ MẬT GIÁ VỐN", 
         "Rò Rỉ Dữ Liệu Tài Chính Khi Đưa Thẳng Lên Cloud AI", 
         [
             "Đưa trực tiếp đơn giá nhập và thành tiền lên các LLM công cộng",
             "Nguy cơ lộ mức chiết khấu và chính sách giá mua nhà cung cấp",
             "Mối đe dọa an toàn thông tin và uy tín cạnh tranh của doanh nghiệp"
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

        # Top highlight border strip
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
        "Thời lượng: 90s\n"
        "Lời thoại: Khảo sát thực tế tại các kho vật tư xây dựng cho thấy 4 nỗi đau kinh điển: Thứ nhất, lỗi tồn kho âm do Race Condition. Thứ hai, đứt gãy chuỗi cung ứng do không dự báo được Burn-rate. Thứ ba, ứ đọng vốn với hàng chục SKU nằm kho trên 60 ngày. Và thứ tư, rủi ro lộ bí mật giá vốn khi đưa dữ liệu lên Cloud AI. SmartLogis AI ra đời để giải quyết triệt để 4 bài toán này.\n"
        "Mẹo tương tác: Giơ ngón tay đếm từ 1 đến 4, tạo sự đồng cảm với khó khăn thực tế của doanh nghiệp."
    )

    # =========================================================================
    # SLIDE 3: OBJECTIVES & VALUE PROPOSITION
    # =========================================================================
    slide3 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(slide3, COLOR_WHITE)
    add_header(slide3, "Mục Tiêu Chiến Lược: 100% Zero Tồn Âm & AI Cố Vấn Tự Động", "OBJECTIVES & VALUE")

    objs = [
        ("🛡️ 100% ZERO TỒN ÂM", "Bảo Vệ Đồng Thời 2 Lớp", [
            "Atomic SQL Decrement loại bỏ 100% Race Condition",
            "Hardware CheckConstraint (Ton >= 0) cấp CSDL",
            "Tự động Rollback toàn bộ chứng từ nếu hàng thiếu",
            "Cam kết an toàn số liệu kho tuyệt đối 24/7"
        ], COLOR_TECH_BLUE),
        ("🧠 TRỢ LÝ AI ĐIỀU HÀNH", "Google Gemini Cố Vấn 24/7", [
            "Tự động tính toán Burn-rate tiêu thụ thực tế 30 ngày",
            "Cảnh báo & gợi ý khối lượng nhập hàng khẩn cấp",
            "Tự động chỉ điểm các SKU tồn đọng Dead Stock > 60 ngày",
            "Báo cáo điều hành chuẩn hóa 3 phần súc tích"
        ], COLOR_ROYAL_BLUE),
        ("🔐 ZERO FINANCIAL LEAK", "Khử Nhạy Cảm Dữ Liệu 100%", [
            "Module Data Sanitizer độc quyền khử sạch đơn giá nhập",
            "Chỉ gửi context số lượng và phân loại hàng hóa cho LLM",
            "Local Grounded Fallback Engine khi mất mạng/lỗi 429",
            "Thanh tra minh bạch qua API /raw-context bất kỳ lúc nào"
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

        # Header accent band inside card
        band = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(1.6), card_w, Inches(0.88))
        band.fill.solid()
        band.fill.fore_color.rgb = border_col
        band.line.fill.background()
        tf_band = band.text_frame
        tf_band.word_wrap = True
        p_b = tf_band.paragraphs[0]
        p_b.text = head
        p_b.font.name = FONT_HEADING
        p_b.font.size = Pt(15)
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

    # Bottom commitment banner
    banner = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(6.15), Inches(11.73), Inches(0.8))
    banner.fill.solid()
    banner.fill.fore_color.rgb = COLOR_MID_NAVY
    banner.line.color.rgb = COLOR_CYAN_ACCENT
    banner.line.width = Pt(1)
    tf_ban = banner.text_frame
    p_ban = tf_ban.paragraphs[0]
    p_ban.text = "🎯 CAM KẾT ĐẦU RA: Vận hành mượt mà, phân quyền RBAC 3 vai trò, đóng gói Docker 1-click hoàn chỉnh."
    p_ban.font.name = FONT_HEADING
    p_ban.font.size = Pt(14)
    p_ban.font.bold = True
    p_ban.font.color.rgb = COLOR_CYAN_ACCENT
    p_ban.alignment = PP_ALIGN.CENTER

    add_speaker_notes(slide3,
        "Thời lượng: 75s\n"
        "Lời thoại: SmartLogis AI thiết lập 3 mục tiêu chiến lược: Thứ nhất, 100% Zero Negative Stock. Thứ hai, Trợ lý Trí tuệ Nhân tạo Google Gemini tính toán Burn-rate và đưa khuyến nghị nhập hàng tức thời. Thứ ba, nguyên tắc Zero Financial Leakage bảo vệ bí mật kinh doanh với module Data Sanitizer độc quyền.\n"
        "Mẹo tương tác: Nhấn giọng tại cụm từ 'Zero Negative Stock' và 'Zero Financial Leakage'."
    )

    # =========================================================================
    # SLIDE 4: SYSTEM ARCHITECTURE (LARGE, CLEAR & STRICTLY LEFT ALIGNED)
    # =========================================================================
    slide4 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(slide4, COLOR_WHITE)
    add_header(slide4, "Kiến Trúc Phân Tầng Hệ Thống (Modular Clean Architecture)", "SYSTEM ARCHITECTURE")

    layers = [
        ("1. PRESENTATION LAYER (TẦNG GIAO DIỆN NGƯỜI DÙNG)", 
         "Jinja2 Server-Side Rendering • Tailwind CSS • Chart.js • WebSocket Stream", 
         "Giao diện điều hành thời gian thực, hiển thị trực quan 4 thẻ KPIs kho vận, widget AI tương tác trực tiếp và tương thích 100% responsive đa thiết bị (PC, tablet, mobile).", 
         COLOR_TECH_BLUE),
        
        ("2. SECURITY & RBAC LAYER (TẦNG BẢO MẬT & PHÂN QUYỀN)", 
         "FastAPI OAuth2 • JSON Web Token (JWT) • HTTP-Only Cookie • Bcrypt Password Hashing", 
         "Xác thực phiên an toàn chống XSS/CSRF, phân quyền RBAC nghiêm ngặt 3 vai trò: Admin (Toàn quyền), Thủ kho kiêm Kế toán (Vận hành kho & Báo cáo Excel) và Nhân viên kho (Tra cứu chỉ đọc).", 
         COLOR_ROYAL_BLUE),
        
        ("3. BUSINESS & AI ENGINE LAYER (TẦNG NGHIỆP VỤ & TRÍ TUỆ NHÂN TẠO)", 
         "Python 3.12 • Uvicorn ASGI • Google Gemini API Client • Local Grounded Fallback Engine", 
         "Điều phối chu trình giao dịch kho Master-Detail, tính toán tốc độ Burn-rate 30 ngày, module Data Sanitizer khử 100% giá vốn nhạy cảm và cơ chế tự phục hồi 24/7.", 
         COLOR_MID_NAVY),
        
        ("4. DATABASE & STORAGE LAYER (TẦNG DỮ LIỆU & BẢO TOÀN ACID)", 
         "SQLite WAL Mode / MySQL 8.0 InnoDB • SQLAlchemy 2.0 ORM • 8 B-Tree Indexes Chiến Lược", 
         "Kiểm soát toàn vẹn giao dịch chống tồn âm kép (Atomic SQL Decrement + CheckConstraints/Triggers), ghi sổ Thẻ kho tự động và tối ưu hóa truy vấn báo cáo dưới 5ms.", 
         COLOR_DEEP_NAVY)
    ]

    card_y = Inches(1.52)
    card_h = Inches(1.24)
    card_w = Inches(11.73)
    card_gap = Inches(0.16)

    for i, (title, stack, desc, col) in enumerate(layers):
        y = card_y + i * (card_h + card_gap)
        card = slide4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), y, card_w, card_h)
        card.fill.solid()
        card.fill.fore_color.rgb = COLOR_ICE_BLUE
        card.line.color.rgb = COLOR_CARD_BORDER
        card.line.width = Pt(1.5)

        # Left color bar strip
        bar = slide4.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), y, Inches(0.18), card_h)
        bar.fill.solid()
        bar.fill.fore_color.rgb = col
        bar.line.fill.background()

        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.35)
        tf.margin_right = Inches(0.3)
        tf.margin_top = Inches(0.12)

        # Title: strictly left aligned, larger font
        p1 = tf.paragraphs[0]
        p1.text = title
        p1.font.name = FONT_HEADING
        p1.font.size = Pt(15.5)
        p1.font.bold = True
        p1.font.color.rgb = col
        p1.alignment = PP_ALIGN.LEFT

        # Tech Stack: strictly left aligned, larger font
        p2 = tf.add_paragraph()
        p2.text = f"Công nghệ cốt lõi: {stack}"
        p2.font.name = FONT_HEADING
        p2.font.size = Pt(13.5)
        p2.font.bold = True
        p2.font.color.rgb = COLOR_TECH_BLUE
        p2.space_before = Pt(3)
        p2.alignment = PP_ALIGN.LEFT

        # Description: strictly left aligned, larger font
        p3 = tf.add_paragraph()
        p3.text = f"Nhiệm vụ nghiệp vụ: {desc}"
        p3.font.name = FONT_BODY
        p3.font.size = Pt(12.5)
        p3.font.color.rgb = COLOR_DARK_TEXT
        p3.space_before = Pt(3)
        p3.alignment = PP_ALIGN.LEFT

    add_speaker_notes(slide4,
        "Thời lượng: 80s\n"
        "Lời thoại: Về mặt kiến trúc, SmartLogis AI áp dụng mô hình phân tầng Modular Clean Architecture: Tầng Presentation sử dụng kết hợp Jinja2 Server-Side Rendering và Tailwind CSS giúp tối ưu tốc độ phản hồi trang dưới 50 mili-giây. Tầng Security đảm bảo xác thực bằng JSON Web Token với cơ chế bảo vệ HTTP-only Cookie và phân quyền RBAC nghiêm ngặt 3 vai trò: Admin, Thủ kho kiêm Kế toán và Nhân viên kho. Tầng Nghiệp vụ đóng vai trò bộ não điều phối, nơi xử lý các transaction ACID và kết nối với Google Gemini Engine. Và dưới cùng là tầng CSDL với SQLite chế độ WAL hoặc MySQL 8.0 InnoDB tối ưu hóa bằng 8 B-Tree Indexes.\n"
        "Mẹo tương tác: Quét tay theo thứ tự từ tầng trên xuống tầng dưới để người nghe nắm bắt luồng kiến trúc."
    )

    # =========================================================================
    # SLIDE 5: DATABASE DESIGN (BALANCED & PROMINENT)
    # =========================================================================
    slide5 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(slide5, COLOR_WHITE)
    add_header(slide5, "Mô Hình CSDL Chuẩn Hóa 3NF & Tối Ưu Hóa B-Tree Indexes", "DATABASE DESIGN")

    card_w = Inches(5.7)
    card_h = Inches(4.35)
    xs = [Inches(0.8), Inches(6.83)]

    # Left Card: 3NF Relational Model
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
    pl1.text = "📊 10 THỰC THỂ QUAN HỆ CHUẨN HÓA 3NF"
    pl1.font.name = FONT_HEADING
    pl1.font.size = Pt(15.5)
    pl1.font.bold = True
    pl1.font.color.rgb = COLOR_ROYAL_BLUE
    pl1.alignment = PP_ALIGN.LEFT

    entities = [
        ("nguoi_dung:", "Quản trị người dùng, phân quyền RBAC 3 vai trò (Admin, Thủ kho kiêm KT, Nhân viên kho)."),
        ("hang_hoa & ton_kho:", "Quan hệ 1-1 chặt chẽ, kiểm soát số dư khả dụng và ngưỡng tồn tối thiểu."),
        ("phieu_nhap & chi_tiet:", "Chứng từ nhập kho Master-Detail, lưu trữ nhà cung cấp và ngày nhập hàng."),
        ("phieu_xuat & chi_tiet:", "Chứng từ xuất kho Master-Detail, áp dụng Atomic SQL Decrement chống tồn âm."),
        ("the_kho:", "Sổ cái tự động ghi vết biến động xuất/nhập và tính toán số dư lũy kế tức thời."),
        ("Danh mục định chuẩn:", "nhom_hang, don_vi_tinh, nha_cung_cap loại bỏ 100% dữ liệu trùng lặp.")
    ]
    for tag, desc in entities:
        pe = tf_l.add_paragraph()
        pe.text = f"• {tag} {desc}"
        pe.font.name = FONT_BODY
        pe.font.size = Pt(13)
        pe.font.color.rgb = COLOR_DARK_TEXT
        pe.space_before = Pt(7)
        pe.alignment = PP_ALIGN.LEFT

    # Right Card: Indexes & Pragmas
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
    pr1.text = "⚡ TỐI ƯU HÓA HIỆU NĂNG & RÀNG BUỘC TOÀN VẸN"
    pr1.font.name = FONT_HEADING
    pr1.font.size = Pt(15.5)
    pr1.font.bold = True
    pr1.font.color.rgb = COLOR_TECH_BLUE
    pr1.alignment = PP_ALIGN.LEFT

    optimizations = [
        ("Tương thích đa cơ sở dữ liệu:", "Vận hành hoàn hảo trên cả SQLite WAL và MySQL 8.0 InnoDB."),
        ("Kiểm soát khóa ngoại chặt chẽ:", "Ràng buộc Foreign Key cấp engine ngăn chặn triệt để bản ghi mồ côi."),
        ("Hàng đợi Connection Pooling:", "Chờ giải phóng khóa, triệt tiêu lỗi tranh chấp Database Lock."),
        ("8 B-Tree Indexes chiến lược:", "Đánh trên NgayNhap, MaNCC, NgayXuat, MaPN, MaPX, MaHH, MaChungTu."),
        ("Tốc độ truy vấn siêu tốc:", "Báo cáo vận hành 30 ngày & tra cứu Thẻ kho phản hồi tức thời < 5ms."),
        ("Ràng buộc CheckConstraint:", "CHECK (SoLuongTon >= 0) trên SQLite & MySQL ngăn chặn 100% can thiệp số âm.")
    ]
    for tag, desc in optimizations:
        po = tf_r.add_paragraph()
        po.text = f"• {tag} {desc}"
        po.font.name = FONT_BODY
        po.font.size = Pt(13)
        po.font.color.rgb = COLOR_DARK_TEXT
        po.space_before = Pt(7)
        po.alignment = PP_ALIGN.LEFT

    # Bottom hardware banner
    ban5 = slide5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(6.15), Inches(11.73), Inches(0.8))
    ban5.fill.solid()
    ban5.fill.fore_color.rgb = COLOR_MID_NAVY
    ban5.line.color.rgb = COLOR_CYAN_ACCENT
    ban5.line.width = Pt(1)
    tf_b5 = ban5.text_frame
    pb5 = tf_b5.paragraphs[0]
    pb5.text = "🔒 BẢO TOÀN CSDL: Tương thích cả SQLite & MySQL 8.0 InnoDB với Check Constraints & Triggers ngăn chặn 100% mọi giao dịch số âm!"
    pb5.font.name = FONT_HEADING
    pb5.font.size = Pt(13.5)
    pb5.font.bold = True
    pb5.font.color.rgb = COLOR_CYAN_ACCENT
    pb5.alignment = PP_ALIGN.CENTER

    add_speaker_notes(slide5,
        "Thời lượng: 75s\n"
        "Lời thoại: Đi sâu vào tầng dữ liệu, mô hình CSDL của chúng em gồm 10 bảng thực thể được chuẩn hóa nghiêm ngặt theo dạng chuẩn 3NF. Bảng ton_kho gắn chặt quan hệ 1-1 với hang_hoa, và mọi biến động đều tự động ghi sổ vào bảng the_kho. Hệ thống hỗ trợ song song SQLite WAL và MySQL 8.0 InnoDB với 8 chỉ mục B-Tree Index trên các trường khóa ngoại và thời gian giao dịch, giúp giảm độ trễ truy vấn báo cáo 30 ngày xuống dưới 5 mili-giây. Đồng thời, các CheckConstraint cấp CSDL bảo đảm không ai có thể ghi số âm vào hệ thống.\n"
        "Mẹo tương tác: Chỉ vào các dòng hỗ trợ SQLite/MySQL và 8 B-Tree Indexes để chứng minh năng lực tối ưu hệ thống sâu."
    )

    # =========================================================================
    # SLIDE 6: CORE FEATURE 1 - ATOMIC SQL DECREMENT
    # =========================================================================
    slide6 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(slide6, COLOR_WHITE)
    add_header(slide6, "Giải Pháp Kỹ Thuật 1: Atomic SQL Decrement Triệt Tiêu Race Condition", "CORE FEATURE: CONCURRENCY")

    # Left: Bad approach
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
    p_b1.text = "❌ CÁCH LÀM CŨ: TRỪ TRONG BỘ NHỚ PYTHON"
    p_b1.font.name = FONT_HEADING
    p_b1.font.size = Pt(15)
    p_b1.font.bold = True
    p_b1.font.color.rgb = COLOR_ALERT_RED
    p_b1.alignment = PP_ALIGN.LEFT

    bad_points = [
        "1. Đọc số tồn kho vào biến Python: `ton = select()` (Ví dụ số dư là: 10)",
        "2. Hai luồng đồng thời (Luồng A và Luồng B) cùng đọc số dư ban đầu là 10",
        "3. Luồng A trừ 8 còn 2; Luồng B đồng thời trừ 8 cũng tính ra còn 2",
        "4. Cả 2 luồng ghi đè số 2 vào CSDL (Hiện tượng Lost Update kinh điển)",
        "HẬU QUẢ: Kho xuất mất 16 món dù thực tế chỉ có 10! Tồn kho bị âm ngoài đời thực, gây thất thoát tài sản nghiêm trọng."
    ]
    for bp in bad_points:
        p = tf_bad.add_paragraph()
        p.text = bp
        p.font.name = FONT_BODY
        p.font.size = Pt(13)
        p.font.color.rgb = COLOR_DARK_TEXT
        p.space_before = Pt(7)
        p.alignment = PP_ALIGN.LEFT

    # Right: Good approach
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
    p_g1.font.size = Pt(15)
    p_g1.font.bold = True
    p_g1.font.color.rgb = COLOR_SUCCESS_GRN
    p_g1.alignment = PP_ALIGN.LEFT

    good_points = [
        "1. Đẩy câu lệnh trừ nguyên tử có điều kiện trực tiếp xuống SQL Engine",
        "2. Thêm mệnh đề kiểm soát khóa: `WHERE SoLuongTon >= :qty`",
        "3. SQL Engine kiểm tra và trừ tồn trong đúng một thao tác nguyên tử duy nhất",
        "4. Nếu số dư không đủ: `rowcount == 0` -> Kích hoạt Rollback toàn bộ CSDL",
        "KẾT QUẢ: Loại bỏ 100% Race Condition, không bao giờ xuất khống, kiểm soát đồng thời tuyệt đối ngay cả khi stress test đa luồng!"
    ]
    for gp in good_points:
        p = tf_good.add_paragraph()
        p.text = gp
        p.font.name = FONT_BODY
        p.font.size = Pt(13)
        p.font.color.rgb = COLOR_DARK_TEXT
        p.space_before = Pt(7)
        p.alignment = PP_ALIGN.LEFT

    # Bottom SQL box
    sql_box = slide6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(6.15), Inches(11.73), Inches(0.8))
    sql_box.fill.solid()
    sql_box.fill.fore_color.rgb = COLOR_DEEP_NAVY
    sql_box.line.color.rgb = COLOR_CYAN_ACCENT
    sql_box.line.width = Pt(1)
    tf_sql = sql_box.text_frame
    p_sql = tf_sql.paragraphs[0]
    p_sql.text = "SQL NGUYÊN TỬ: UPDATE ton_kho SET SoLuongTon = SoLuongTon - :qty WHERE MaHH = :ma_hh AND SoLuongTon >= :qty;"
    p_sql.font.name = "Consolas"
    p_sql.font.size = Pt(13)
    p_sql.font.bold = True
    p_sql.font.color.rgb = COLOR_CYAN_ACCENT
    p_sql.alignment = PP_ALIGN.CENTER

    add_speaker_notes(slide6,
        "Thời lượng: 90s\n"
        "Lời thoại: Đây là một trong những điểm sáng kỹ thuật quan trọng nhất của đồ án. Thông thường, các lập trình viên hay đọc tồn kho vào biến Python rồi trừ ton.SoLuongTon -= qty. Cách làm này dẫn tới thảm họa Lost Update khi nhiều người cùng thao tác. Để khắc phục, SmartLogis AI áp dụng Atomic SQL Decrement: đẩy toàn bộ điều kiện trừ xuống cấp SQL Engine với mệnh đề WHERE SoLuongTon >= :qty. Nếu tại thời điểm ghi số lượng không đủ, rowcount trả về bằng 0, hệ thống lập tức Rollback toàn bộ chứng từ Master-Detail và trả về lỗi 400 rõ ràng.\n"
        "Mẹo tương tác: Dùng tay miêu tả hai luồng truy cập song song để hội đồng cảm nhận rõ nét hiểm họa của Race Condition và sự ưu việt của Atomic SQL."
    )

    # =========================================================================
    # SLIDE 7: CORE FEATURE 2 - WORKFLOW & RBAC MATRIX
    # =========================================================================
    slide7 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(slide7, COLOR_WHITE)
    add_header(slide7, "Quy Trình Giao Dịch Kho ACID & Ma Trận Phân Quyền RBAC", "CORE FEATURE: WORKFLOW & RBAC")

    # Top ACID Workflow Card
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
    ptw2.text = "[1. Tạo Master Chứng Từ] ➔ [2. Lưu Detail Hàng Hóa] ➔ [3. Atomic SQL Update Tồn Kho] ➔ [4. Ghi Sổ Thẻ Kho]"
    ptw2.font.name = FONT_HEADING
    ptw2.font.size = Pt(13.5)
    ptw2.font.bold = True
    ptw2.font.color.rgb = COLOR_TECH_BLUE
    ptw2.space_before = Pt(4)
    ptw2.alignment = PP_ALIGN.LEFT

    ptw3 = tf_tw.add_paragraph()
    ptw3.text = "Nguyên tắc Toàn Vẹn: Bất kỳ bước nào phát sinh lỗi, toàn bộ giao dịch tự động Rollback về trạng thái ban đầu!"
    ptw3.font.name = FONT_BODY
    ptw3.font.size = Pt(12.5)
    ptw3.font.color.rgb = COLOR_DARK_TEXT
    ptw3.space_before = Pt(3)
    ptw3.alignment = PP_ALIGN.LEFT

    # RBAC Table
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
        ["Quản trị người dùng & Phân quyền", "✅ Toàn Quyền Quản Trị", "❌ Không có quyền", "❌ Không có quyền"],
        ["Quản trị SKU & Nhà cung cấp", "✅ Cho phép thực hiện", "✅ Toàn quyền quản lý", "❌ Chế độ Chỉ Đọc (Staff)"],
        ["Lập Phiếu Nhập / Xuất Kho ACID", "✅ Cho phép thực hiện", "✅ Lập phiếu & ghi sổ", "❌ Bị chặn (HTTP 403)"],
        ["Xuất Báo Cáo Kế Toán Excel", "✅ Cho phép thực hiện", "✅ Xuất báo cáo kế toán", "❌ Bị chặn (HTTP 403)"],
        ["Tra cứu Thẻ kho & Cảnh báo tồn", "✅ Xem toàn bộ dữ liệu", "✅ Tra cứu & cảnh báo", "✅ Tra cứu kiểm đếm kho"]
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
        "Thời lượng: 75s\n"
        "Lời thoại: Bên cạnh giải thuật chống tồn âm, SmartLogis AI đóng gói toàn bộ quy trình Nhập - Xuất kho trong một giao dịch ACID nguyên tử duy nhất gồm 4 bước. Đồng thời, mô hình phân quyền RBAC được tối ưu hóa cho thực tế doanh nghiệp với 3 vai trò rõ ràng: Admin nắm toàn quyền hệ thống; Thủ kho kiêm Kế toán được trao quyền vận hành kho, lập chứng từ và kết xuất báo cáo tài chính kế toán; trong khi Nhân viên kho (Staff) chỉ có quyền tra cứu danh mục để kiểm đếm hiện trường và bị chặn hoàn toàn các thao tác sửa đổi hay lập phiếu (HTTP 403).\n"
        "Mẹo tương tác: Chỉ vào cột 'Nhân viên kho (Staff)' và nhấn mạnh tính phân quyền phân cấp bảo mật chặt chẽ trong doanh nghiệp."
    )

    # =========================================================================
    # SLIDE 8: AI INTEGRATION 1 - DATA SANITIZER
    # =========================================================================
    slide8 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(slide8, COLOR_WHITE)
    add_header(slide8, "Tích Hợp AI 1: Data Sanitizer Khử Nhạy Cảm 100% Giá Vốn", "AI INTEGRATION: PRIVACY")

    # Process flow horizontal boxes
    flow_steps = [
        ("1. CSDL KHO NỘI BỘ", "Chứa đầy đủ đơn giá nhập, giá vốn,\nthành tiền & chiết khấu nhà cung cấp", COLOR_MID_NAVY),
        ("2. DATA SANITIZER FILTER", "Thuật toán khử nhạy cảm đệ quy\nloại bỏ 100% các trường tài chính bí mật", COLOR_TECH_BLUE),
        ("3. CONTEXT GỬI TỚI AI", "Chỉ gồm mã hàng, tên hàng, số tồn,\ntốc độ Burn-rate & số ngày không xuất", COLOR_CYAN_ACCENT)
    ]
    fb_w = Inches(3.68)
    fb_h = Inches(1.25)
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
        tf.margin_top = Inches(0.14)
        p1 = tf.paragraphs[0]
        p1.text = title
        p1.font.name = FONT_HEADING
        p1.font.size = Pt(13.5)
        p1.font.bold = True
        p1.font.color.rgb = col
        p1.alignment = PP_ALIGN.CENTER

        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.name = FONT_BODY
        p2.font.size = Pt(12)
        p2.font.color.rgb = COLOR_DARK_TEXT
        p2.alignment = PP_ALIGN.CENTER
        p2.space_before = Pt(3)

    # 2 Comparison Columns
    card_w = Inches(5.7)
    card_h = Inches(4.0)
    xs = [Inches(0.8), Inches(6.83)]

    # Left: Stripped fields
    c_strip = slide8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, xs[0], Inches(3.05), card_w, card_h)
    c_strip.fill.solid()
    c_strip.fill.fore_color.rgb = COLOR_ICE_BLUE
    c_strip.line.color.rgb = COLOR_ALERT_RED
    c_strip.line.width = Pt(1.5)
    tf_s = c_strip.text_frame
    tf_s.word_wrap = True
    tf_s.margin_left = tf_s.margin_right = Inches(0.3)
    tf_s.margin_top = Inches(0.18)

    ps1 = tf_s.paragraphs[0]
    ps1.text = "❌ DỮ LIỆU TÀI CHÍNH BỊ LOẠI BỎ TRIỆT ĐỂ (100%)"
    ps1.font.name = FONT_HEADING
    ps1.font.size = Pt(15)
    ps1.font.bold = True
    ps1.font.color.rgb = COLOR_ALERT_RED
    ps1.alignment = PP_ALIGN.LEFT

    stripped_items = [
        "Đơn giá nhập (`dongianhap`, `import_price`): Khử sạch 100%",
        "Thành tiền chi tiết (`thanhtien`): Khử sạch 100%",
        "Giá vốn bình quân (`gia_von`): Khử sạch 100%",
        "Tỷ lệ chiết khấu & chính sách giá nhà cung cấp: Xóa bỏ",
        "CAM KẾT: Không một byte dữ liệu tài chính nào rời khỏi máy chủ nội bộ sang bên thứ ba!"
    ]
    for it in stripped_items:
        p = tf_s.add_paragraph()
        p.text = f"• {it}"
        p.font.name = FONT_BODY
        p.font.size = Pt(13)
        p.font.color.rgb = COLOR_DARK_TEXT
        p.space_before = Pt(7)
        p.alignment = PP_ALIGN.LEFT

    # Right: Kept fields
    c_kept = slide8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, xs[1], Inches(3.05), card_w, card_h)
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
    pk1.font.size = Pt(15)
    pk1.font.bold = True
    pk1.font.color.rgb = COLOR_SUCCESS_GRN
    pk1.alignment = PP_ALIGN.LEFT

    kept_items = [
        "Mã hàng (`MaHH`), Tên hàng (`TenHH`), Đơn vị tính (`DVT`)",
        "Số lượng tồn kho thực tế & Ngưỡng tồn an toàn tối thiểu",
        "Tốc độ xuất bình quân 30 ngày (Burn-rate số lượng / ngày)",
        "Số ngày không phát sinh phiếu xuất (Dead stock metric)",
        "MINH BẠCH: Thanh tra trực tiếp payload qua API `/api/v1/ai/raw-context` bất kỳ lúc nào."
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
        "Thời lượng: 80s\n"
        "Lời thoại: Khi đưa trí tuệ nhân tạo vào doanh nghiệp, bài toán hóc búa nhất là: 'Làm thế nào để tận dụng sức mạnh LLM mà không để lộ bí mật giá vốn?'. Câu trả lời của chúng em là module Data Sanitizer. Trước khi bất kỳ dữ liệu nào gửi đi, thuật toán quét đệ quy sẽ loại bỏ hoàn toàn các trường nhạy cảm như đơn giá nhập, thành tiền hay chiết khấu. Ngữ cảnh cung cấp cho Google Gemini chỉ thuần túy là các chỉ số vận hành. Hội đồng có thể kiểm chứng trực tiếp tính minh bạch này qua endpoint /raw-context trong phần demo.\n"
        "Mẹo tương tác: Nhìn thẳng vào hội đồng, khẳng định: 'Dữ liệu tài chính không bao giờ rời khỏi máy chủ doanh nghiệp'."
    )

    # =========================================================================
    # SLIDE 9: AI INTEGRATION 2 - PROMPTS & 3-PART REPORT
    # =========================================================================
    slide9 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(slide9, COLOR_WHITE)
    add_header(slide9, "Tích Hợp AI 2: Prompt Chống Ảo Giác & Báo Cáo Điều Hành 3 Phần", "AI INTEGRATION: PROMPTS")

    card_w = Inches(5.7)
    card_h = Inches(5.3)
    xs = [Inches(0.8), Inches(6.83)]

    # Left: Anti-Hallucination
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
    pp1.font.size = Pt(15)
    pp1.font.bold = True
    pp1.font.color.rgb = COLOR_ROYAL_BLUE
    pp1.alignment = PP_ALIGN.LEFT

    prompt_bullets = [
        "1. System Instruction Ràng Buộc Bất Biến:",
        "   Chỉ phân tích dựa trên dữ liệu JSON thực tế được cung cấp",
        "   Tuyệt đối KHÔNG tự bịa mã SKU, tên hàng hay số liệu kho",
        "2. Cơ Chế Xử Lý Kho Rỗng (Empty Inventory):",
        "   Thông báo rõ: 'Chưa ghi nhận giao dịch hợp lệ trong kỳ'",
        "   Tuyệt đối không phỏng đoán hay tự sinh dữ liệu giả",
        "3. Output Parser Định Chuẩn Cấu Trúc:",
        "   Ép định dạng JSON/Markdown phân tầng tường minh",
        "   Dễ dàng phân rã hiển thị lên Dashboard Widget trực tiếp"
    ]
    for b in prompt_bullets:
        p = tf_p.add_paragraph()
        p.text = b
        p.font.name = FONT_BODY
        p.font.size = Pt(13)
        p.font.color.rgb = COLOR_DARK_TEXT
        p.space_before = Pt(5)
        p.alignment = PP_ALIGN.LEFT

    # Right: 3-Part Operational Report
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
    pr1.font.size = Pt(15)
    pr1.font.bold = True
    pr1.font.color.rgb = COLOR_TECH_BLUE
    pr1.alignment = PP_ALIGN.LEFT

    report_bullets = [
        "PHẦN 1: TÌNH TRẠNG TỒN KHO TỔNG QUAN",
        "• Tổng số SKU quản lý, tổng lượng xuất 30 ngày",
        "• Tỷ lệ SKU an toàn vs SKU chạm ngưỡng tối thiểu",
        "PHẦN 2: CẢNH BÁO & ĐỀ XUẤT NHẬP HÀNG KHẨN CẤP",
        "• Tính toán thiếu hụt dựa trên Burn-rate tiêu thụ ngày",
        "• Gợi ý cụ thể số lượng nhập cho từng mã SKU vật tư",
        "PHẦN 3: TÓM TẮT BIẾN ĐỘNG BẤT THƯỜNG",
        "• Chỉ điểm các mặt hàng có lượng xuất đột biến trong kỳ",
        "• Cảnh báo hàng Dead stock > 60 ngày cần giải phóng mặt bằng"
    ]
    for b in report_bullets:
        p = tf_r.add_paragraph()
        p.text = b
        p.font.name = FONT_BODY
        p.font.size = Pt(13)
        p.font.color.rgb = COLOR_ROYAL_BLUE if ("PHẦN" in b) else COLOR_DARK_TEXT
        p.font.bold = True if ("PHẦN" in b) else False
        p.space_before = Pt(6 if ("PHẦN" in b) else 3)
        p.alignment = PP_ALIGN.LEFT

    add_speaker_notes(slide9,
        "Thời lượng: 75s\n"
        "Lời thoại: Hiện tượng 'ảo giác' là rủi ro lớn nhất của các mô hình LLM. Trong SmartLogis AI, chúng em áp dụng kỹ thuật Prompt Engineering chặt chẽ: System Instruction ràng buộc AI chỉ được phép đóng vai Senior Logistics Assistant, suy luận thuần túy trên tập JSON thực tế và trả lời theo cấu trúc 3 phần bắt buộc: Phần 1 tóm lược sức khỏe kho; Phần 2 đưa ra cảnh báo và đề xuất khối lượng nhập cụ thể; và Phần 3 chỉ điểm các mặt hàng xuất đột biến hoặc hàng chết nằm kho trên 60 ngày.\n"
        "Mẹo tương tác: Chỉ vào 3 phần của báo cáo, giải thích lý do vì sao cấu trúc này tối ưu cho ban giám đốc ra quyết định nhanh."
    )

    # =========================================================================
    # SLIDE 10: AI INTEGRATION 3 - LOCAL GROUNDED FALLBACK ENGINE
    # =========================================================================
    slide10 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(slide10, COLOR_WHITE)
    add_header(slide10, "Tích Hợp AI 3: Local Grounded Fallback Engine Sẵn Sàng 24/7", "AI INTEGRATION: RESILIENCE")

    # Simplified 3-Step Decision Flowchart
    steps = [
        ("YÊU CẦU PHÂN TÍCH KHO", "Người dùng bấm nút trên Web Dashboard hoặc gọi API /generate-report", COLOR_MID_NAVY),
        ("GỌI GOOGLE GEMINI API", "Gửi Sanitized JSON context qua REST API kèm Exponential Backoff 3 lần", COLOR_TECH_BLUE),
        ("ĐIỀU PHỐI TỰ ĐỘNG THÔNG MINH", "Thành công (200 OK) -> Hiển thị kết quả LLM\nThất bại (429/Mất mạng) -> Fallback Engine", COLOR_CYAN_ACCENT)
    ]
    for i, (title, desc, col) in enumerate(steps):
        x = Inches(0.8) + i * (Inches(3.68) + Inches(0.35))
        card = slide10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(1.55), Inches(3.68), Inches(1.3))
        card.fill.solid()
        card.fill.fore_color.rgb = COLOR_ICE_BLUE
        card.line.color.rgb = col
        card.line.width = Pt(1.5)
        tf = card.text_frame
        tf.word_wrap = True
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

    # 2 Comparison Boxes
    c_w = Inches(5.7)
    c_h = Inches(4.0)

    # Left: Cloud Gemini
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
    pc1.font.size = Pt(15)
    pc1.font.bold = True
    pc1.font.color.rgb = COLOR_ROYAL_BLUE
    pc1.alignment = PP_ALIGN.LEFT

    cloud_pts = [
        "Sử dụng mô hình Google Gemini 1.5 / 2.0 (`gemini-3.5-flash-lite`)",
        "Khả năng lập luận phân tích văn phong quản trị điều hành chuyên nghiệp",
        "Cơ chế Exponential Backoff: Tự động retry tối đa 3 lần khi lỗi mạng",
        "Phản hồi mượt mà khi kết nối Internet ổn định và quota API khả dụng",
        "Đem lại trải nghiệm trợ lý số cao cấp cho ban giám đốc doanh nghiệp"
    ]
    for pt in cloud_pts:
        p = tfc.add_paragraph()
        p.text = f"• {pt}"
        p.font.name = FONT_BODY
        p.font.size = Pt(13)
        p.font.color.rgb = COLOR_DARK_TEXT
        p.space_before = Pt(6)
        p.alignment = PP_ALIGN.LEFT

    # Right: Local Fallback
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
    pf1.font.size = Pt(15)
    pf1.font.bold = True
    pf1.font.color.rgb = COLOR_SUCCESS_GRN
    pf1.alignment = PP_ALIGN.LEFT

    fall_pts = [
        "Kích hoạt tự động khi lỗi mạng, sai API Key hoặc gặp lỗi 429 Quota",
        "Thuật toán toán học CSDL nội bộ tự động phân tích tức thời",
        "Đảm bảo sinh báo cáo đủ chuẩn 3 phần với số liệu thật 100%",
        "Hoàn toàn độc lập với Internet và dịch vụ của bên thứ ba",
        "CAM KẾT DOANH NGHIỆP: Ứng dụng không bao giờ sập, vận hành 24/7!"
    ]
    for pt in fall_pts:
        p = tff.add_paragraph()
        p.text = f"• {pt}"
        p.font.name = FONT_BODY
        p.font.size = Pt(13)
        p.font.color.rgb = COLOR_DARK_TEXT
        p.space_before = Pt(6)
        p.alignment = PP_ALIGN.LEFT

    add_speaker_notes(slide10,
        "Thời lượng: 70s\n"
        "Lời thoại: Một hệ thống doanh nghiệp không thể ngừng hoạt động chỉ vì mất kết nối Internet hay nhà cung cấp AI gặp sự cố mã lỗi 429 Quota Exceeded. Do đó, chúng em xây dựng Local Grounded Fallback Engine. Hệ thống được trang bị cơ chế thử lại Exponential Backoff 3 lần. Nếu API bên ngoài vẫn không phản hồi, bộ phân tích toán học nội bộ sẽ tự động kích hoạt ngay lập tức: tự tính toán số dư tồn, tốc độ xuất kho và sinh ra báo cáo 3 phần chuẩn xác 100% dựa trên dữ liệu thật.\n"
        "Mẹo tương tác: Nhấn mạnh thông điệp: 'Tính sẵn sàng cao là tiêu chuẩn bắt buộc của phần mềm cấp doanh nghiệp'."
    )

    # =========================================================================
    # SLIDE 11: SDLC EXECUTION - 4 PHASES
    # =========================================================================
    slide11 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(slide11, COLOR_WHITE)
    add_header(slide11, "Tiến Trình Phát Triển Phần Mềm: 4 Giai Đoạn Hoàn Thiện", "SDLC EXECUTION")

    phases = [
        ("GIAI ĐOẠN 1", "Thiết Kế Nền Tảng", [
            "Khảo sát nghiệp vụ kho vật tư thực tế",
            "Thiết kế ERD chuẩn hóa 3NF 10 bảng",
            "Xây dựng REST APIs CRUD chuẩn",
            "Dựng giao diện Jinja2 ban đầu"
        ], COLOR_MID_NAVY),
        ("GIAI ĐOẠN 2", "Audit & Ràng Buộc", [
            "Phát hiện & sửa lỗi Race Condition",
            "Ứng dụng Atomic SQL Decrement",
            "Cấu hình SQLite WAL & Triggers",
            "Tạo 8 B-Tree Indexes tối ưu"
        ], COLOR_ROYAL_BLUE),
        ("GIAI ĐOẠN 3", "Tích Hợp AI & LLM", [
            "Kết nối Google Gemini Live API",
            "Module Data Sanitizer bảo mật",
            "Prompt Engineering chuẩn 3 phần",
            "Local Grounded Fallback Engine"
        ], COLOR_TECH_BLUE),
        ("GIAI ĐOẠN 4", "DevOps & Đóng Gói", [
            "Đóng gói Docker Compose 4 containers",
            "Cấu hình Nginx Reverse Proxy SSL",
            "Bộ kiểm thử tự động 12 test cases",
            "Triển khai Production Web Server"
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

        # Header band inside card
        band = slide11.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(1.55), card_w, Inches(0.92))
        band.fill.solid()
        band.fill.fore_color.rgb = col
        band.line.fill.background()
        tf_b = band.text_frame
        p_b1 = tf_b.paragraphs[0]
        p_b1.text = p_num
        p_b1.font.name = FONT_HEADING
        p_b1.font.size = Pt(12.5)
        p_b1.font.bold = True
        p_b1.font.color.rgb = COLOR_CYAN_ACCENT if col == COLOR_MID_NAVY else COLOR_WHITE
        p_b1.alignment = PP_ALIGN.CENTER

        p_b2 = tf_b.add_paragraph()
        p_b2.text = p_title
        p_b2.font.name = FONT_HEADING
        p_b2.font.size = Pt(13.5)
        p_b2.font.bold = True
        p_b2.font.color.rgb = COLOR_WHITE
        p_b2.alignment = PP_ALIGN.CENTER

        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = Inches(0.2)
        tf.margin_top = Inches(1.05)

        for b in bullets:
            pb = tf.add_paragraph()
            pb.text = f"• {b}"
            pb.font.name = FONT_BODY
            pb.font.size = Pt(12.5)
            pb.font.color.rgb = COLOR_DARK_TEXT
            pb.space_before = Pt(6)
            pb.alignment = PP_ALIGN.LEFT

    # Bottom status badge
    ban11 = slide11.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(6.15), Inches(11.73), Inches(0.8))
    ban11.fill.solid()
    ban11.fill.fore_color.rgb = COLOR_MID_NAVY
    ban11.line.color.rgb = COLOR_CYAN_ACCENT
    ban11.line.width = Pt(1)
    tf_b11 = ban11.text_frame
    pb11 = tf_b11.paragraphs[0]
    pb11.text = "✅ TRẠNG THÁI TIẾN ĐỘ: Hoàn thành 100% tất cả các mục tiêu kỹ thuật qua cả 4 giai đoạn phát triển!"
    pb11.font.name = FONT_HEADING
    pb11.font.size = Pt(13.5)
    pb11.font.bold = True
    pb11.font.color.rgb = COLOR_CYAN_ACCENT
    pb11.alignment = PP_ALIGN.CENTER

    add_speaker_notes(slide11,
        "Thời lượng: 75s\n"
        "Lời thoại: Quy trình phát triển SmartLogis AI được tổ chức chặt chẽ qua 4 giai đoạn kỹ thuật phần mềm: Giai đoạn 1 thiết kế kiến trúc phân tầng và chuẩn hóa mô hình thực thể 3NF. Giai đoạn 2 kiểm toán sâu, giải quyết lỗi đua lệnh bằng Atomic SQL Decrement và thiết lập 8 chỉ mục B-Tree. Giai đoạn 3 hiện thực hóa mô hình AI với Google Gemini, Data Sanitizer và Fallback Engine. Và Giai đoạn 4 hoàn thiện đóng gói Docker Compose đa container, cấu hình Nginx Gateway và đạt độ phủ kiểm thử tự động tuyệt đối.\n"
        "Mẹo tương tác: Quét tay theo chiều ngang qua 4 giai đoạn, thể hiện sự hoàn thiện trọn vẹn và tính kỷ luật của nhóm dự án."
    )

    # =========================================================================
    # SLIDE 12: QA & AUTOMATED TESTING
    # =========================================================================
    slide12 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(slide12, COLOR_WHITE)
    add_header(slide12, "Chiến Lược Kiểm Thử Tự Động: 16/16 Test Cases Đạt 100%", "QUALITY ASSURANCE")

    # Table of tests
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
        ["MODULE KIỂM THỬ", "SỐ TEST CASES", "KỊCH BẢN KIỂM THỬ TRỌNG YẾU", "KẾT QUẢ"],
        ["test_ai_engine.py", "4 Test Cases", "Kho rỗng không ảo giác, đề xuất tồn min, khử 100% giá vốn, Mocking Fallback 429", "✅ 100% PASSED"],
        ["test_phase2_inventory.py", "6 Test Cases", "ACID Inbound, chống tồn âm, Concurrency Stress Test, RBAC 3 vai trò, CheckConstraint", "✅ 100% PASSED"],
        ["test_websocket.py", "3 Test Cases", "Kết nối song công WebSocket, Broadcast sự kiện tức thời, đồng bộ đa thiết bị", "✅ 100% PASSED"],
        ["test_crud & supplier_crud.py", "2 Test Cases", "Vòng đời CRUD SKU vật tư & Nhà cung cấp, kiểm tra toàn vẹn quan hệ khóa ngoại", "✅ 100% PASSED"],
        ["test_endpoints.py", "1 Test Suite", "Kiểm thử Endpoints Dashboard, Master Data, Sổ Thẻ kho & Xuất báo cáo Excel", "✅ 100% PASSED"]
    ]

    for r_idx, row in enumerate(test_data):
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

    # Bottom summary banner
    ban12 = slide12.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(6.15), Inches(11.73), Inches(0.8))
    ban12.fill.solid()
    ban12.fill.fore_color.rgb = COLOR_MID_NAVY
    ban12.line.color.rgb = COLOR_CYAN_ACCENT
    ban12.line.width = Pt(1)
    tf_b12 = ban12.text_frame
    pb12 = tf_b12.paragraphs[0]
    pb12.text = "🏆 TỔNG NGHIỆM THU: 16/16 TEST CASES PASSED HOÀN TOÀN (100%) TRONG ~40 GIÂY THỰC THI PYTEST!"
    pb12.font.name = FONT_HEADING
    pb12.font.size = Pt(13.5)
    pb12.font.bold = True
    pb12.font.color.rgb = COLOR_CYAN_ACCENT
    pb12.alignment = PP_ALIGN.CENTER

    add_speaker_notes(slide12,
        "Thời lượng: 80s\n"
        "Lời thoại: Để đảm bảo hệ thống đủ tiêu chuẩn vận hành thực tế, chúng em xây dựng bộ kiểm thử tự động toàn diện bằng framework Pytest gồm 16 kịch bản trọng yếu. Đặc biệt, chúng em thực hiện bài kiểm thử Concurrency Stress Test bằng ThreadPoolExecutor: giả lập nhiều thủ kho cùng xuất vét kho đồng thời, kết quả chứng minh tồn kho dừng lại chính xác ở số dư khả dụng và không bao giờ bị âm. Cùng với đó là các kịch bản kiểm thử RBAC chặt chẽ đảm bảo Nhân viên kho bị chặn 403 khi thao tác trái quyền. Toàn bộ 16 test cases từ bảo mật AI, giao dịch ACID, phân quyền RBAC đến xuất báo cáo Excel đều vượt qua với tỷ lệ thành công 100%.\n"
        "Mẹo tương tác: Nhấn mạnh bài test Concurrency và tỷ lệ 16/16 test cases passed để tạo sự thuyết phục cao nhất với hội đồng kỹ thuật."
    )

    # =========================================================================
    # SLIDE 13: PRODUCTION DEPLOYMENT & DOCKER
    # =========================================================================
    slide13 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(slide13, COLOR_WHITE)
    add_header(slide13, "Đóng Gói Triển Khai Docker & Hỗ Trợ Truy Cập Đa Thiết Bị", "PRODUCTION DEPLOYMENT")

    # 4 Architecture containers
    containers = [
        ("GATEWAY (NGINX)", "Reverse Proxy Cổng Vào", "Lắng nghe Port 80 & 443, cân bằng tải, định tuyến Web & WebSocket", COLOR_ROYAL_BLUE),
        ("BACKEND (FASTAPI)", "Máy Chủ Ứng Dụng", "Python 3.12, Uvicorn ASGI, xử lý nghiệp vụ ACID và điều phối AI", COLOR_TECH_BLUE),
        ("DATABASE (POSTGRESQL)", "Cơ Sở Dữ Liệu Tập Trung", "PostgreSQL 15, lưu trữ volume bền bỉ postgres_data, ACID chuẩn", COLOR_MID_NAVY),
        ("ADMIN TOOLS (PGADMIN)", "Quản Trị Trực Quan", "pgAdmin 4 tại cổng 5050 giúp quản trị viên tra cứu DB trực tiếp", COLOR_CYAN_ACCENT)
    ]

    c_w = Inches(2.7)
    c_h = Inches(2.3)
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
        tf.margin_left = tf.margin_right = Inches(0.2)
        tf.margin_top = Inches(0.14)

        p1 = tf.paragraphs[0]
        p1.text = name
        p1.font.name = FONT_HEADING
        p1.font.size = Pt(13)
        p1.font.bold = True
        p1.font.color.rgb = col
        p1.alignment = PP_ALIGN.LEFT

        p2 = tf.add_paragraph()
        p2.text = role
        p2.font.name = FONT_HEADING
        p2.font.size = Pt(12)
        p2.font.bold = True
        p2.font.color.rgb = COLOR_DARK_TEXT
        p2.space_before = Pt(3)
        p2.alignment = PP_ALIGN.LEFT

        p3 = tf.add_paragraph()
        p3.text = desc
        p3.font.name = FONT_BODY
        p3.font.size = Pt(11.5)
        p3.font.color.rgb = COLOR_MUTED_TEXT
        p3.space_before = Pt(4)
        p3.alignment = PP_ALIGN.LEFT

    # Multi-device Access Info Card
    card_net = slide13.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(4.1), Inches(11.73), Inches(2.85))
    card_net.fill.solid()
    card_net.fill.fore_color.rgb = COLOR_DEEP_NAVY
    card_net.line.color.rgb = COLOR_CYAN_ACCENT
    card_net.line.width = Pt(1.5)

    tf_n = card_net.text_frame
    tf_n.word_wrap = True
    tf_n.margin_left = tf_n.margin_right = Inches(0.4)
    tf_n.margin_top = Inches(0.22)

    pn1 = tf_n.paragraphs[0]
    pn1.text = "🌐 HƯỚNG DẪN TRUY CẬP ĐA THIẾT BỊ TRONG MÔI TRƯỜNG DOANH NGHIỆP"
    pn1.font.name = FONT_HEADING
    pn1.font.size = Pt(15)
    pn1.font.bold = True
    pn1.font.color.rgb = COLOR_CYAN_ACCENT
    pn1.alignment = PP_ALIGN.LEFT

    net_points = [
        "1. Truy cập từ Máy chủ (Localhost): http://localhost  |  HTTPS SSL: https://localhost",
        "2. Truy cập qua Tên miền Sản xuất: http://smartlogis-ai.com  |  HTTPS: https://smartlogis-ai.com",
        "3. Truy cập từ Thiết bị Di động (Mobile / Tablet cùng Wi-Fi): http://192.168.x.x (Thủ kho thao tác tại bãi)",
        "4. Công cụ Quản trị CSDL & API Docs: http://localhost:5050 (pgAdmin 4)  |  http://localhost/docs (Swagger UI)",
        "🚀 Khởi chạy tự động 1-Click: Chạy file `run_server.bat` (Windows) hoặc `start.sh` (Linux) tự cấu hình từ A-Z!"
    ]
    for np in net_points:
        p = tf_n.add_paragraph()
        p.text = np
        p.font.name = FONT_BODY
        p.font.size = Pt(13)
        p.font.color.rgb = COLOR_WHITE
        p.space_before = Pt(5)
        p.alignment = PP_ALIGN.LEFT

    add_speaker_notes(slide13,
        "Thời lượng: 75s\n"
        "Lời thoại: Về mặt vận hành triển khai, SmartLogis AI được đóng gói hoàn chỉnh bằng Docker Compose với kiến trúc 4 container độc lập: Nginx đóng vai trò Reverse Proxy làm cổng vào duy nhất, bảo vệ hệ thống với chứng chỉ bảo mật SSL HTTPS; cụm Backend FastAPI xử lý logic; PostgreSQL 15 đảm bảo an toàn dữ liệu; và pgAdmin 4 hỗ trợ quản trị trực quan. Đặc biệt, hệ thống hỗ trợ truy cập đa thiết bị trong mạng LAN: thủ kho có thể dùng máy tính bảng hoặc điện thoại di động kết nối trực tiếp để quét mã và thao tác xuất nhập kho ngay tại hiện trường.\n"
        "Mẹo tương tác: Giơ điện thoại hoặc tablet lên làm động tác minh họa việc thủ kho truy cập qua mạng Wi-Fi tại hiện trường."
    )

    # =========================================================================
    # SLIDE 14: 5-MINUTE LIVE DEMO PLAN
    # =========================================================================
    slide14 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(slide14, COLOR_WHITE)
    add_header(slide14, "Kịch Bản Live Demo Thực Chiến 5 Phút Thuyết Phục Hội Đồng", "LIVE DEMONSTRATION")

    rows, cols = 6, 3
    left = Inches(0.8)
    top = Inches(1.55)
    width = Inches(11.73)
    height = Inches(5.4)

    table_shape = slide14.shapes.add_table(rows, cols, left, top, width, height)
    t = table_shape.table
    t.columns[0].width = Inches(2.0)
    t.columns[1].width = Inches(4.5)
    t.columns[2].width = Inches(5.23)

    demo_data = [
        ["THỜI GIAN", "THAO TÁC THỰC HIỆN TRÊN HỆ THỐNG", "MỤC TIÊU & KẾT QUẢ KỲ VỌNG"],
        ["Phút 1", "Đăng nhập Thủ kho (`thukho`) & Nhân viên (`nhanvien`)", "So sánh giao diện RBAC: Thủ kho có nút Lập phiếu/Báo cáo; Nhân viên chỉ xem tra cứu"],
        ["Phút 2", "Bấm nút 'Báo Cáo 3 Phần' trên AI Widget", "Google Gemini Live API phân tích Burn-rate, đề xuất nhập hàng và cảnh báo Dead stock"],
        ["Phút 3", "Thử nghiệm xuất vượt tồn kho Thép D10", "Giao diện cảnh báo đỏ; Backend từ chối với mã lỗi 400 Bad Request chống tồn âm"],
        ["Phút 4", "Lập phiếu nhập kho & Tra cứu Thẻ kho", "Giao dịch Master-Detail thành công; Sổ Thẻ kho tự động cập nhật số dư lũy kế"],
        ["Phút 5", "Mở Swagger UI gọi API `/raw-context`", "Thanh tra minh bạch: Chứng minh 100% dữ liệu nạp cho AI không chứa giá vốn"]
    ]

    for r_idx, row in enumerate(demo_data):
        for c_idx, val in enumerate(row):
            cell = t.cell(r_idx, c_idx)
            cell.text = val
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            p = cell.text_frame.paragraphs[0]
            p.font.name = FONT_HEADING if r_idx == 0 else FONT_BODY
            p.font.size = Pt(13)
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
        "Thời lượng: 60s\n"
        "Lời thoại: Sau đây, chúng em xin phép được bắt đầu phần Live Demo hệ thống thực tế trong đúng 5 phút theo lộ trình chuẩn: Phút 1: Đăng nhập so sánh 2 vai trò Thủ kho kiêm Kế toán và Nhân viên kho để thấy rõ phân quyền RBAC; Phút 2: Tương tác với AI Widget để nhận báo cáo phân tích chiến lược từ Google Gemini; Phút 3: Trực tiếp 'thử thách' tính toàn vẹn hệ thống bằng cách xuất vượt số lượng tồn kho để quan sát cơ chế chống tồn âm; Phút 4: Lập phiếu nhập và tra cứu sổ Thẻ kho; Và Phút 5: Thanh tra trực tiếp payload gửi tới AI để chứng minh 100% giá vốn đã được khử nhạy cảm.\n"
        "Mẹo tương tác: Chuyển sang màn hình trình chiếu trình duyệt web, bắt đầu thao tác mượt mà theo đúng 5 bước đã nêu."
    )

    # =========================================================================
    # SLIDE 15: CONCLUSION & ROADMAP (Hero Dark Navy)
    # =========================================================================
    slide15 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(slide15, COLOR_DEEP_NAVY)

    # Top accent bar
    top_bar = slide15.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.14))
    top_bar.fill.solid()
    top_bar.fill.fore_color.rgb = COLOR_CYAN_ACCENT
    top_bar.line.fill.background()

    add_header(slide15, "Kết Luận, Giá Trị Doanh Nghiệp & Hướng Phát Triển", "CONCLUSION & ROADMAP", is_dark=True)

    card_w = Inches(5.7)
    card_h = Inches(4.25)
    xs = [Inches(0.8), Inches(6.83)]

    # Left: Achievements
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
    pa1.text = "🏆 THÀNH TỰU NỔI BẬT ĐÃ ĐẠT ĐƯỢC"
    pa1.font.name = FONT_HEADING
    pa1.font.size = Pt(15.5)
    pa1.font.bold = True
    pa1.font.color.rgb = COLOR_CYAN_ACCENT
    pa1.alignment = PP_ALIGN.LEFT

    achs = [
        "100% Zero Negative Stock: Triệt tiêu hoàn toàn rủi ro tồn âm và Lost Update.",
        "Trợ lý AI Gemini Thực Chiến: Cảnh báo Burn-rate & đề xuất nhập kho thông minh.",
        "Bảo Mật Cấp Doanh Nghiệp: Khử 100% giá vốn nhạy cảm, phân quyền RBAC 3 vai trò.",
        "Chất Lượng Xuất Xưởng: 16/16 Test Cases passed, CSDL MySQL 8.0 & SQLite WAL sẵn sàng."
    ]
    for ac in achs:
        p = tfa.add_paragraph()
        p.text = f"• {ac}"
        p.font.name = FONT_BODY
        p.font.size = Pt(13)
        p.font.color.rgb = COLOR_WHITE
        p.space_before = Pt(7)
        p.alignment = PP_ALIGN.LEFT

    # Right: Future Roadmap
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
    pr1.font.size = Pt(15.5)
    pr1.font.bold = True
    pr1.font.color.rgb = COLOR_CYAN_ACCENT
    pr1.alignment = PP_ALIGN.LEFT

    roads = [
        "Dự Báo Nhu Cầu Nâng Cao: Tích hợp mô hình chuỗi thời gian ARIMA / Prophet.",
        "Smart Bin Location: Bản đồ kho 2D/3D tối ưu hóa đường đi lấy hàng cho xe nâng.",
        "Mobile Barcode App: Ứng dụng di động quét mã QR kiểm hàng nhanh ngoài hiện trường.",
        "Tích Hợp ERP Doanh Nghiệp: Kết nối API đồng bộ với SAP, Odoo, Fast Accounting."
    ]
    for rd in roads:
        p = tfr.add_paragraph()
        p.text = f"• {rd}"
        p.font.name = FONT_BODY
        p.font.size = Pt(13)
        p.font.color.rgb = COLOR_WHITE
        p.space_before = Pt(7)
        p.alignment = PP_ALIGN.LEFT

    # Bottom Thank you message
    ban15 = slide15.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(6.05), Inches(11.73), Inches(0.95))
    ban15.fill.solid()
    ban15.fill.fore_color.rgb = COLOR_ROYAL_BLUE
    ban15.line.color.rgb = COLOR_CYAN_ACCENT
    ban15.line.width = Pt(1.5)
    tf_b15 = ban15.text_frame
    pb15_1 = tf_b15.paragraphs[0]
    pb15_1.text = "🌟 TRÂN TRỌNG CẢM ƠN QUÝ THẦY/CÔ TRONG HỘI ĐỒNG ĐÃ CHÚ Ý LẮNG NGHE!"
    pb15_1.font.name = FONT_HEADING
    pb15_1.font.size = Pt(15)
    pb15_1.font.bold = True
    pb15_1.font.color.rgb = COLOR_WHITE
    pb15_1.alignment = PP_ALIGN.CENTER

    pb15_2 = tf_b15.add_paragraph()
    pb15_2.text = "Nhóm nghiên cứu xin sẵn sàng tiếp thu ý kiến và trả lời các câu hỏi phản biện từ Hội đồng."
    pb15_2.font.name = FONT_BODY
    pb15_2.font.size = Pt(13)
    pb15_2.font.color.rgb = COLOR_CYAN_ACCENT
    pb15_2.alignment = PP_ALIGN.CENTER
    pb15_2.space_before = Pt(4)

    add_speaker_notes(slide15,
        "Thời lượng: 60s\n"
        "Lời thoại: Kính thưa Hội đồng, SmartLogis AI đã hoàn thành 100% các mục tiêu đề ra với 16/16 test cases đạt chuẩn, mang lại một giải pháp quản trị kho vận toàn diện: vừa an toàn tuyệt đối với giao dịch ACID chống tồn âm trên cả MySQL 8.0 và SQLite, vừa thông minh vượt bậc với sự trợ lực từ Google Gemini, phân quyền 3 vai trò thực tế và sẵn sàng triển khai ngay vào doanh nghiệp. Trong tương lai, chúng em sẽ tiếp tục mở rộng mô hình học máy chuỗi thời gian để dự báo nhu cầu theo mùa vụ công trình và phát triển ứng dụng di động quét mã vạch tại hiện trường bãi vật tư. Chúng em xin trân trọng cảm ơn sự hướng dẫn tận tình của Thầy/Cô và rất mong nhận được những góp ý quý báu từ Hội đồng để hoàn thiện dự án hơn nữa. Xin trân trọng cảm ơn!\n"
        "Mẹo tương tác: Cúi đầu chào trang trọng, mỉm cười tự tin, chuyển sang trạng thái sẵn sàng lắng nghe câu hỏi phản biện."
    )

    # Save deck
    output_path = os.path.join("docs", "SmartLogis_AI_Presentation_Deck.pptx")
    prs.save(output_path)
    print(f"[OK] Presentation successfully regenerated (v3): {output_path}")

if __name__ == "__main__":
    create_deck()
