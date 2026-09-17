# scripts/generate_all_updated_diagrams.py
"""
Script Sinh Toàn Bộ 15 Sơ Đồ Kỹ Thuật Kiến Trúc Cho SmartLogis AI Chuẩn Hóa
Áp dụng tiêu chuẩn Skill 'diagram-architect':
- Kết nối ưu tiên cắm vào MÉP RÌA (Edge Attachment), tuyệt đối không đâm xuyên tâm hay đè chữ.
- Bố cục thoáng đãng, khoảng cách rộng rãi, tách chữ rõ ràng.
- Sơ đồ CSDL ERD MySQL 8.0: Nối đầy đủ 10 quan hệ ngoại khóa (1-1, 1-N) trực giao (orthogonal).
- Biểu đồ Hoạt động Activity Diagram: Khắc phục lỗi khuyết node (y >= 0), đầy đủ các bước kiểm soát.
- Biểu đồ Lớp Class Diagram: Nối đầy đủ các quan hệ Controllers -> Services -> Models.
- Sơ đồ Quy trình Scrum: Vòng lặp cải tiến liên tục chạy vòng phía dưới mép ngoài, không cắt chữ.
"""

import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Circle, Polygon

plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Segoe UI', 'Tahoma']
plt.rcParams['axes.unicode_minus'] = False

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "generated_diagrams")
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ==============================================================================
# HÀM BỔ TRỢ DÙNG CHUNG (EDGE-ATTACHED CONNECTORS & DRAWING UTILITIES)
# ==============================================================================
def draw_card(ax, x, y, w, h, title, subtitle="", header_bg="#1E293B", body_bg="#FFFFFF", border="#334155", rad=0.15):
    """Vẽ hộp thẻ có Header & Body tách biệt."""
    header_h = min(0.55, h * 0.35)
    body_h = h - header_h
    # Body
    body_box = FancyBboxPatch((x, y), w, body_h, boxstyle=f"round,pad=0.02,rounding_size={rad}",
                              facecolor=body_bg, edgecolor=border, linewidth=1.4)
    ax.add_patch(body_box)
    # Header
    head_box = FancyBboxPatch((x, y + body_h), w, header_h, boxstyle=f"round,pad=0.02,rounding_size={rad}",
                              facecolor=header_bg, edgecolor=border, linewidth=1.4)
    ax.add_patch(head_box)
    ax.text(x + w / 2, y + body_h + header_h / 2, title, ha='center', va='center',
            fontsize=8.5, fontweight='bold', color='#FFFFFF')
    if subtitle:
        ax.text(x + w / 2, y + body_h / 2, subtitle, ha='center', va='center',
                fontsize=7.2, color='#475569')


def draw_actor(ax, x, y, name, role_desc, color='#1E40AF'):
    """Vẽ hình biểu trưng Tác nhân (Actor) UML."""
    circle = Circle((x, y + 0.38), 0.22, color=color, fill=False, linewidth=2.0)
    ax.add_patch(circle)
    ax.plot([x, x], [y + 0.16, y - 0.32], color=color, linewidth=2.0)
    ax.plot([x - 0.28, x + 0.28], [y - 0.05, y - 0.05], color=color, linewidth=2.0)
    ax.plot([x, x - 0.22], [y - 0.32, y - 0.72], color=color, linewidth=2.0)
    ax.plot([x, x + 0.22], [y - 0.32, y - 0.72], color=color, linewidth=2.0)
    ax.text(x, y - 0.90, name, ha='center', va='top', fontsize=9.5, fontweight='bold', color='#0F172A')
    if role_desc:
        ax.text(x, y - 1.25, role_desc, ha='center', va='top', fontsize=7.5, color='#64748B', style='italic')
    return (x, y)


# ==============================================================================
# 0. HÌNH 1.5: SƠ ĐỒ QUY TRÌNH SCRUM 3 SPRINT - 6 TUẦN (image2.png)
# ==============================================================================
def draw_scrum_workflow(out_path):
    fig, ax = plt.subplots(figsize=(16, 8.5), dpi=300)
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 8.5)
    ax.axis('off')
    fig.patch.set_facecolor('#F8FAFC')
    ax.set_facecolor('#F8FAFC')

    ax.text(8.0, 8.0, "QUY TRÌNH SCRUM TRONG PHÁT TRIỂN HỆ THỐNG (3 SPRINT - 6 TUẦN)",
            ha='center', va='center', fontsize=13.5, fontweight='bold', color='#0F172A')

    def draw_box(x, y, w, h, title, items, fill='#EFF6FF', border='#3B82F6', title_col='#1E3A8A'):
        box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08,rounding_size=0.15",
                             facecolor=fill, edgecolor=border, linewidth=1.6)
        ax.add_patch(box)
        ax.text(x + w / 2, y + h - 0.35, title, ha='center', va='center',
                fontsize=9.5, fontweight='bold', color=title_col)
        cur_y = y + h - 0.75
        for it in items:
            ax.text(x + w / 2, cur_y, it, ha='center', va='center', fontsize=7.5, color='#334155')
            cur_y -= 0.32

    # 1. Product Backlog
    draw_box(0.5, 3.2, 2.2, 3.8, "PRODUCT\nBACKLOG", [
        "10 User Stories",
        "(US01 - US10)",
        "Ưu tiên nghiệp vụ",
        "kho & Prompt AI",
        "(PO quản lý)"
    ], '#FEF3C7', '#D97706', '#B45309')

    # 2. Sprint Planning
    draw_box(3.2, 3.2, 2.1, 3.8, "SPRINT\nPLANNING", [
        "Lập kế hoạch Sprint",
        "Chọn User Stories",
        "Ước lượng",
        "Story Points",
        "(Định kỳ 2 tuần)"
    ], '#EEF2FF', '#6366F1', '#4338CA')

    # 3. Sprint Backlog
    draw_box(5.8, 3.2, 2.1, 3.8, "SPRINT\nBACKLOG", [
        "Danh sách task",
        "Sprint 2 tuần",
        "Phân công cụ thể:",
        "• Hưng: Backend, PO",
        "• Đạt: Frontend, SM"
    ], '#EEF2FF', '#6366F1', '#4338CA')

    # 4. Sprint Execution (Outer green container)
    sprint_box = FancyBboxPatch((8.4, 2.6), 3.5, 4.6, boxstyle="round,pad=0.08,rounding_size=0.18",
                                facecolor='#F0FDF4', edgecolor='#16A34A', linewidth=2.0)
    ax.add_patch(sprint_box)
    ax.text(10.15, 6.85, "SPRINT (2 TUẦN)", ha='center', va='center',
            fontsize=10.5, fontweight='bold', color='#15803D')

    # Inner: Daily Scrum box
    daily_box = FancyBboxPatch((8.65, 5.0), 3.0, 1.45, boxstyle="round,pad=0.06,rounding_size=0.12",
                               facecolor='#DCFCE7', edgecolor='#16A34A', linewidth=1.4)
    ax.add_patch(daily_box)
    ax.text(10.15, 5.95, "Daily Scrum (Hàng ngày)", ha='center', va='center',
            fontsize=8.5, fontweight='bold', color='#166534')
    ax.text(10.15, 5.45, "Họp 15 phút đồng bộ tiến độ\nGiải quyết trở ngại (Blockers)", ha='center', va='center',
            fontsize=7.2, color='#14532D')

    # Sprint tasks
    tasks = [
        "• Phát triển Backend & Frontend",
        "• Xử lý Transaction ACID CSDL",
        "• Tinh chỉnh Prompt Gemini API",
        "• Viết Unit & Integration Test"
    ]
    ty = 4.4
    for t in tasks:
        ax.text(8.8, ty, t, ha='left', va='center', fontsize=7.5, color='#14532D')
        ty -= 0.38

    # 5. Sprint Review
    draw_box(12.4, 4.8, 3.1, 2.2, "SPRINT REVIEW", [
        "Kiểm thử chấp nhận (UAT)",
        "Đạt Definition of Done (DoD)",
        "Demo tính năng hoàn chỉnh"
    ], '#FAF5FF', '#A855F7', '#7E22CE')

    # 6. Sprint Retrospective
    draw_box(12.4, 2.2, 3.1, 2.1, "SPRINT RETRO", [
        "Họp cải tiến quy trình",
        "Rút kinh nghiệm cho",
        "Sprint tiếp theo"
    ], '#F8FAFC', '#64748B', '#334155')

    # Forward Workflow Arrows (Edge to Edge, clean)
    def draw_fwd_arrow(x1, y1, x2, y2, color='#3B82F6'):
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="->", color=color, lw=2.0))

    draw_fwd_arrow(2.7, 5.1, 3.2, 5.1, '#D97706')
    draw_fwd_arrow(5.3, 5.1, 5.8, 5.1, '#6366F1')
    draw_fwd_arrow(7.9, 5.1, 8.4, 5.1, '#6366F1')
    draw_fwd_arrow(11.9, 5.9, 12.4, 5.9, '#16A34A')
    draw_fwd_arrow(13.95, 4.8, 13.95, 4.3, '#7E22CE')

    # Continuous Improvement Feedback Loop: Goes UNDER all boxes, completely clear of text!
    ax.plot([13.95, 13.95, 4.25, 4.25], [2.2, 1.3, 1.3, 3.15],
            linestyle='--', color='#DC2626', linewidth=2.0)
    ax.annotate('', xy=(4.25, 3.2), xytext=(4.25, 3.0),
                arrowprops=dict(arrowstyle="->", color='#DC2626', lw=2.0))

    # Badge on the loop line
    ax.text(9.1, 1.3, " Cải tiến liên tục cho Sprint tiếp theo (Vòng lặp 2 tuần) ",
            ha='center', va='center', fontsize=8.2, fontweight='bold', color='#DC2626',
            bbox=dict(boxstyle='round,pad=0.25', facecolor='#FFFFFF', edgecolor='#DC2626', linewidth=1.2))

    # Footer note: Personnel allocation
    footer_box = FancyBboxPatch((0.5, 0.25), 15.0, 0.65, boxstyle="round,pad=0.04,rounding_size=0.08",
                                facecolor='#FFFFFF', edgecolor='#CBD5E1', linewidth=1.2)
    ax.add_patch(footer_box)
    ax.text(8.0, 0.58, "Phân công: Product Owner / Backend: Nguyễn Thành Hưng   |   Scrum Master / Frontend & QA: Hoàng Tiến Đạt",
            ha='center', va='center', fontsize=8.2, fontweight='bold', color='#1E293B')

    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[OK] Saved Hình 1.5 to {out_path}")


# ==============================================================================
# 1. HÌNH 2.2.3: SƠ ĐỒ KIẾN TRÚC PHÂN HỆ CHỨC NĂNG (image3.png)
# ==============================================================================
def draw_system_architecture(out_path):
    fig, ax = plt.subplots(figsize=(16, 10.5), dpi=300)
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 10.5)
    ax.axis('off')
    fig.patch.set_facecolor('#F8FAFC')
    ax.set_facecolor('#F8FAFC')

    ax.text(8.0, 10.0, "KIẾN TRÚC PHÂN HỆ CHỨC NĂNG HỆ THỐNG QUẢN LÝ KHO TÍCH HỢP AI",
            ha='center', va='center', fontsize=13.5, fontweight='bold', color='#0F172A')

    def draw_layer_box(x, y, w, h, title, bg='#FFFFFF', border='#3B82F6'):
        box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1,rounding_size=0.15",
                             facecolor=bg, edgecolor=border, linewidth=1.8)
        ax.add_patch(box)
        ax.text(x + 0.35, y + h - 0.35, title, ha='left', va='center', fontsize=9.5, fontweight='bold', color=border)

    def draw_component(x, y, w, h, title, desc="", fill='#F1F5F9', border='#64748B'):
        box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08,rounding_size=0.1",
                             facecolor=fill, edgecolor=border, linewidth=1.2)
        ax.add_patch(box)
        if desc:
            ax.text(x + w / 2, y + h / 2 + 0.16, title, ha='center', va='center', fontsize=8.5, fontweight='bold', color='#0F172A')
            ax.text(x + w / 2, y + h / 2 - 0.20, desc, ha='center', va='center', fontsize=7.2, color='#475569')
        else:
            ax.text(x + w / 2, y + h / 2, title, ha='center', va='center', fontsize=8.5, fontweight='bold', color='#0F172A')

    # Layer 1: Frontend Presentation
    draw_layer_box(0.6, 7.1, 14.8, 2.4, "1. TẦNG GIAO DIỆN NGƯỜI DÙNG (FRONTEND - JINJA2 SSR & WEBSOCKET REALTIME)", '#F0FDF4', '#16A34A')
    draw_component(1.0, 7.4, 3.2, 1.5, "Phân Hệ Xác Thực RBAC", "Đăng nhập, Phân quyền\nAdmin / Thủ kho / Nhân viên", '#DCFCE7', '#16A34A')
    draw_component(4.6, 7.4, 3.4, 1.5, "Quản Lý Danh Mục & Thẻ Kho", "CRUD Hàng hóa, NCC, DVT\nTra cứu biến động sổ thẻ kho", '#DCFCE7', '#16A34A')
    draw_component(8.4, 7.4, 3.4, 1.5, "Nghiệp Vụ Nhập / Xuất Kho", "Lập phiếu nhập & Lập phiếu xuất\nValidation giao diện, Chống tồn âm", '#DCFCE7', '#16A34A')
    draw_component(12.2, 7.4, 3.0, 1.5, "Dashboard & Trợ Lý AI", "Báo cáo Nhập-Xuất-Tồn\nGợi ý nhập & Xuất Excel/PDF", '#DCFCE7', '#16A34A')

    # Layer 2: Backend Application
    draw_layer_box(0.6, 3.7, 10.4, 2.9, "2. TẦNG XỬ LÝ NGHIỆP VỤ (BACKEND API - FASTAPI PYTHON)", '#EFF6FF', '#2563EB')
    draw_component(1.0, 4.0, 3.1, 2.1, "API Router & Auth", "JWT Authentication\nRBAC Guard: 3 Vai Trò\nSwagger / OpenAPI Docs", '#DBEAFE', '#2563EB')
    draw_component(4.5, 4.0, 3.4, 2.1, "Inventory Service (Core ACID)", "Xử lý Transaction Nhập/Xuất\nAtomic SQL Decrement\nKiểm tra chống tồn kho âm", '#DBEAFE', '#2563EB')
    draw_component(8.3, 4.0, 2.5, 2.1, "AI Sanitizer Module", "Tổng hợp số liệu xuất nhập tồn\nKhử trùng DonGiaNhap bảo mật\nGrounded Prompt Template", '#DBEAFE', '#2563EB')

    # External AI Cloud Layer
    draw_layer_box(11.4, 3.7, 4.0, 2.9, "DỊCH VỤ AI ĐÁM MÂY", '#FAF5FF', '#7C3AED')
    draw_component(11.8, 4.1, 3.2, 2.0, "Google Gemini API", "Mô hình Gemini 1.5 Flash\nSinh báo cáo 3 phần\nGợi ý nhập hàng & Bất thường", '#EDE9FE', '#7C3AED')

    # Layer 3: Database & Storage (MySQL 8.0)
    draw_layer_box(0.6, 0.5, 14.8, 2.7, "3. TẦNG CƠ SỞ DỮ LIỆU & LƯU TRỮ (DATABASE - MYSQL SERVER 8.0 INNODB ACID)", '#FFFBEB', '#D97706')
    draw_component(1.0, 0.8, 3.3, 1.9, "Danh Mục & Người Dùng", "Bảng: NguoiDung (3 vai trò),\nHangHoa, NhomHang, NCC", '#FEF3C7', '#D97706')
    draw_component(4.7, 0.8, 3.4, 1.9, "Tồn Kho & Ràng Buộc ACID", "Bảng: TonKho\nCHECK (SoLuongTon >= 0)\nAtomic SQL Decrement", '#FEF3C7', '#D97706')
    draw_component(8.5, 0.8, 3.2, 1.9, "Giao Dịch Nhập / Xuất", "Bảng: PhieuNhap, ChiTietPN,\nPhieuXuat, ChiTietPX", '#FEF3C7', '#D97706')
    draw_component(12.1, 0.8, 3.1, 1.9, "Nhật Ký Thẻ Kho", "Bảng: TheKho (Append-only)\nTruy vết biến động tồn lũy kế\nPhục vụ đối soát & AI", '#FEF3C7', '#D97706')

    # Inter-layer connectors
    def draw_conn(x1, y1, x2, y2, color='#2563EB', text=""):
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="<->", color=color, lw=1.8))
        if text:
            ax.text((x1 + x2) / 2 + 0.25, (y1 + y2) / 2, text, ha='left', va='center',
                    fontsize=8.0, color=color, fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.15', facecolor='#FFFFFF', edgecolor=color, alpha=0.9))

    draw_conn(5.8, 7.1, 5.8, 6.6, '#16A34A', 'HTTP REST / WebSocket')
    draw_conn(10.8, 5.0, 11.8, 5.0, '#7C3AED', 'Grounded Prompt / HTTPS')
    draw_conn(5.8, 3.7, 5.8, 3.2, '#D97706', 'SQLAlchemy / MySQL Pool')

    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[OK] Saved Hình 2.2.3 to {out_path}")


# ==============================================================================
# 2. HÌNH 4.1: BIỂU ĐỒ USE CASE TỔNG QUÁT (image4.png) - EDGE ATTACHMENT
# ==============================================================================
def draw_usecase_general(out_path):
    fig, ax = plt.subplots(figsize=(17, 12.5), dpi=300)
    ax.set_xlim(0, 17)
    ax.set_ylim(0, 12.5)
    ax.axis('off')
    fig.patch.set_facecolor('#F8FAFC')
    ax.set_facecolor('#F8FAFC')

    # System boundary box
    sys_box = FancyBboxPatch(
        (3.6, 0.4), 10.2, 11.6,
        boxstyle="round,pad=0.2,rounding_size=0.15",
        facecolor='#FFFFFF', edgecolor='#334155', linewidth=2.0
    )
    ax.add_patch(sys_box)

    ax.text(8.7, 11.65, "HỆ THỐNG QUẢN LÝ KHO THÔNG MINH SMARTLOGIS AI",
            ha='center', va='center', fontsize=13.5, fontweight='bold', color='#1E293B')

    # Actors: 3 on left, 1 on right
    draw_actor(ax, 1.6, 10.0, "Quản Trị Viên\n(Admin)", "Toàn quyền hệ thống", '#1E40AF')
    draw_actor(ax, 1.6, 5.8, "Thủ Kho Kiêm\nKế Toán", "Vận hành & Đối soát", '#0D9488')
    draw_actor(ax, 1.6, 2.0, "Nhân Viên Kho\n(Staff)", "Tra cứu & Xem cảnh báo", '#9333EA')
    draw_actor(ax, 15.4, 1.7, "Trợ Lý AI\n(Gemini 1.5)", "Dịch vụ LLM ngoài", '#7C3AED')

    # Helper to draw use cases and record edge anchors
    nodes = {}

    def add_uc(key, x, y, text, subtext="", fill='#EFF6FF', border='#3B82F6', w=3.4, h=0.72):
        box = FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                             boxstyle="round,pad=0.08,rounding_size=0.35",
                             facecolor=fill, edgecolor=border, linewidth=1.4)
        ax.add_patch(box)
        if subtext:
            ax.text(x, y + 0.10, text, ha='center', va='center', fontsize=8.6, fontweight='bold', color='#0F172A')
            ax.text(x, y - 0.16, subtext, ha='center', va='center', fontsize=6.8, color='#64748B')
        else:
            ax.text(x, y, text, ha='center', va='center', fontsize=8.6, fontweight='bold', color='#0F172A')
        nodes[key] = {
            'center': (x, y),
            'left': (x - w / 2, y),
            'right': (x + w / 2, y),
            'top': (x, y + h / 2),
            'bottom': (x, y - h / 2),
            'w': w, 'h': h
        }

    # Column 1 (Left Column, x = 6.1): Primary Actions
    add_uc('login', 6.1, 10.8, "Đăng nhập & Phân quyền", "US01 (3 Vai trò: Admin, Thủ kho, Staff)", '#F1F5F9', '#64748B')
    add_uc('user_mgmt', 6.1, 9.5, "Quản lý Người Dùng", "US02 (Admin quản trị tài khoản & quyền)", '#F1F5F9', '#64748B')
    add_uc('catalog', 6.1, 8.2, "Quản lý Danh Mục Kho", "Hàng hóa, Nhóm, ĐVT, Nhà CC (US02)", '#FEF3C7', '#D97706')
    add_uc('inbound', 6.1, 6.9, "Lập Phiếu Nhập Kho", "Inbound ACID Transaction (US03)", '#DCFCE7', '#16A34A')
    add_uc('outbound', 6.1, 5.6, "Lập Phiếu Xuất Kho", "Outbound ACID Transaction (US04)", '#DCFCE7', '#16A34A')
    add_uc('lookup', 6.1, 4.3, "Tra Cứu Sổ Thẻ Kho", "Truy vết biến động lũy kế (US05)", '#E0E7FF', '#4F46E5')
    add_uc('export', 6.1, 3.0, "Xuất Báo Cáo Excel Tồn", "Tổng hợp đối soát kho (US08)", '#FEF3C7', '#D97706')
    add_uc('ai_report', 6.1, 1.7, "Phân Tích & Báo Cáo AI", "Burn-rate & Dự báo tồn an toàn (US07/09)", '#EDE9FE', '#7C3AED')

    # Column 2 (Right Column, x = 11.4): Included ACID Safeguards & Security
    add_uc('card_update', 11.4, 6.9, "Ghi Sổ Thẻ Kho Tự Động", "TheKho Append-only Audit Log", '#F1F5F9', '#475569')
    add_uc('check_stock', 11.4, 5.6, "Kiểm Tra & Chống Tồn Âm", "CHECK (Ton >= 0) / Atomic Lock", '#FEE2E2', '#DC2626')
    add_uc('alert', 11.4, 4.3, "Cảnh Báo Tồn Tối Thiểu", "Cảnh báo khi TonKho <= TonMin", '#E0E7FF', '#4F46E5')
    add_uc('ai_sanitize', 11.4, 2.3, "Khử Trùng Giá Vốn Nhập", "Data Sanitizer Bảo Mật Tuyệt Đối", '#FEE2E2', '#DC2626')
    add_uc('gemini_prompt', 11.4, 1.1, "Grounded Prompting", "Template bám sát số liệu kho thật", '#EDE9FE', '#7C3AED')

    # Connect Actors to Column 1 LEFT edges
    def connect_actor_left(actor_x, actor_y, node_key, col):
        p_start = (actor_x + 0.35, actor_y)
        p_end = nodes[node_key]['left']
        ax.plot([p_start[0], p_end[0]], [p_start[1], p_end[1]], color=col, linewidth=1.3, zorder=1)

    def connect_actor_right(actor_x, actor_y, node_key, col):
        p_start = (actor_x - 0.35, actor_y)
        p_end = nodes[node_key]['right']
        ax.plot([p_start[0], p_end[0]], [p_start[1], p_end[1]], color=col, linewidth=1.3, zorder=1)

    # Admin: Connects to left edges
    for k in ['login', 'user_mgmt', 'catalog', 'lookup']:
        connect_actor_left(1.6, 10.0, k, '#1E40AF')

    # Thủ kho kiêm Kế toán: Connects to left edges
    for k in ['login', 'catalog', 'inbound', 'outbound', 'lookup', 'export', 'ai_report']:
        connect_actor_left(1.6, 5.8, k, '#0D9488')

    # Staff: Connects to left edges
    for k in ['login', 'lookup']:
        connect_actor_left(1.6, 2.0, k, '#9333EA')

    # Gemini AI: Connects to Column 2 right edges
    connect_actor_right(15.4, 1.7, 'ai_sanitize', '#7C3AED')
    connect_actor_right(15.4, 1.7, 'gemini_prompt', '#7C3AED')

    # Relationships between Column 1 and Column 2 (in empty corridor)
    def draw_include_edge(k_from, k_to):
        p1 = nodes[k_from]['right']
        p2 = nodes[k_to]['left']
        ax.annotate('', xy=p2, xytext=p1,
                    arrowprops=dict(arrowstyle="->", color="#DC2626", lw=1.4, linestyle="--"), zorder=2)
        mid_x = (p1[0] + p2[0]) / 2
        mid_y = (p1[1] + p2[1]) / 2 + 0.16
        ax.text(mid_x, mid_y, "<<include>>", ha='center', va='center', fontsize=7.2, fontweight='bold', color='#DC2626',
                bbox=dict(boxstyle='round,pad=0.15', facecolor='#FFFFFF', edgecolor='#DC2626', linewidth=0.8, alpha=0.95))

    draw_include_edge('inbound', 'card_update')
    draw_include_edge('outbound', 'check_stock')
    draw_include_edge('lookup', 'alert')
    draw_include_edge('ai_report', 'ai_sanitize')
    draw_include_edge('ai_report', 'gemini_prompt')

    # Outbound to card_update (clean diagonal between columns)
    p_out = nodes['outbound']['right']
    p_card = nodes['card_update']['left']
    ax.annotate('', xy=p_card, xytext=p_out,
                arrowprops=dict(arrowstyle="->", color="#DC2626", lw=1.4, linestyle="--"), zorder=2)
    ax.text((p_out[0] + p_card[0]) / 2 - 0.1, (p_out[1] + p_card[1]) / 2 + 0.12, "<<include>>",
            ha='center', va='center', fontsize=7.0, fontweight='bold', color='#DC2626',
            bbox=dict(boxstyle='round,pad=0.15', facecolor='#FFFFFF', edgecolor='#DC2626', linewidth=0.8, alpha=0.95))

    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[OK] Saved Hình 4.1 to {out_path}")


# ==============================================================================
# 3. HÌNH 4.1.1: BIỂU ĐỒ USE CASE PHÂN HỆ NGHIỆP VỤ KHO (image5.png) - EDGE ATTACH
# ==============================================================================
def draw_warehouse_usecase(out_path):
    fig, ax = plt.subplots(figsize=(15, 9.5), dpi=300)
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 9.5)
    ax.axis('off')
    fig.patch.set_facecolor('#F8FAFC')
    ax.set_facecolor('#F8FAFC')

    sys_box = FancyBboxPatch(
        (3.6, 0.4), 9.6, 8.7,
        boxstyle="round,pad=0.2,rounding_size=0.15",
        facecolor='#FFFFFF', edgecolor='#0D9488', linewidth=2.0
    )
    ax.add_patch(sys_box)

    ax.text(8.4, 8.75, "PHÂN HỆ NGHIỆP VỤ KHO & CHỐNG TỒN ÂM (ACID)",
            ha='center', va='center', fontsize=13.0, fontweight='bold', color='#0F766E')

    draw_actor(ax, 1.6, 7.2, "Admin\n(Quản trị viên)", "Giám sát & Quản trị", '#1E40AF')
    draw_actor(ax, 1.6, 4.4, "Thủ Kho Kiêm\nKế Toán", "Vận hành kho & Đối soát", '#0D9488')
    draw_actor(ax, 1.6, 1.6, "Nhân Viên Kho\n(Staff)", "Tra cứu thẻ kho & Cảnh báo", '#9333EA')

    nodes = {}

    def add_uc(key, x, y, text, subtext="", fill='#EFF6FF', border='#3B82F6', w=3.4, h=0.74):
        box = FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                             boxstyle="round,pad=0.08,rounding_size=0.35",
                             facecolor=fill, edgecolor=border, linewidth=1.4)
        ax.add_patch(box)
        if subtext:
            ax.text(x, y + 0.10, text, ha='center', va='center', fontsize=8.8, fontweight='bold', color='#0F172A')
            ax.text(x, y - 0.16, subtext, ha='center', va='center', fontsize=7.0, color='#64748B')
        else:
            ax.text(x, y, text, ha='center', va='center', fontsize=8.8, fontweight='bold', color='#0F172A')
        nodes[key] = {
            'left': (x - w / 2, y),
            'right': (x + w / 2, y),
            'top': (x, y + h / 2),
            'bottom': (x, y - h / 2)
        }

    # Left Column (Core Actions, x = 6.0)
    add_uc('inbound', 6.0, 7.4, "Lập Phiếu Nhập Kho", "Inbound Transaction (US03)", '#DCFCE7', '#16A34A')
    add_uc('outbound', 6.0, 5.4, "Lập Phiếu Xuất Kho", "Outbound Transaction (US04)", '#DCFCE7', '#16A34A')
    add_uc('lookup', 6.0, 3.4, "Tra Cứu Thẻ Kho & Báo Cáo", "Xem sổ thẻ kho & Cảnh báo min (US05)", '#E0E7FF', '#4F46E5')
    add_uc('export_excel', 6.0, 1.4, "Xuất Báo Cáo Excel Tồn", "Tổng hợp Nhập - Xuất - Tồn (US08)", '#FEF3C7', '#D97706')

    # Right Column (Included ACID Safeguards, x = 11.2)
    add_uc('card_update', 11.2, 7.4, "Ghi Sổ Thẻ Kho Tự Động", "TheKho Append-only Audit Log", '#F1F5F9', '#475569')
    add_uc('val_stock', 11.2, 5.4, "Thẩm Định Tồn Khả Dụng", "Chống âm tại Frontend", '#FEE2E2', '#DC2626')
    add_uc('pessimistic', 11.2, 3.4, "Khóa Atomic Decrement", "Update SQL chống Race Condition", '#FEE2E2', '#DC2626')

    # Connect Actors to LEFT edges
    def conn_left(ax_x, ax_y, node_key, col):
        p1 = (ax_x + 0.35, ax_y)
        p2 = nodes[node_key]['left']
        ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=col, linewidth=1.3)

    for k in ['inbound', 'outbound', 'lookup', 'export_excel']:
        conn_left(1.6, 7.2, k, '#1E40AF')
        conn_left(1.6, 4.4, k, '#0D9488')

    conn_left(1.6, 1.6, 'lookup', '#9333EA')

    # Include edge-to-edge
    def draw_inc(k1, k2):
        p1 = nodes[k1]['right']
        p2 = nodes[k2]['left']
        ax.annotate('', xy=p2, xytext=p1,
                    arrowprops=dict(arrowstyle="->", color="#DC2626", lw=1.4, linestyle="--"))
        mid_x = (p1[0] + p2[0]) / 2
        mid_y = (p1[1] + p2[1]) / 2 + 0.15
        ax.text(mid_x, mid_y, "<<include>>", ha='center', va='center', fontsize=7.2, fontweight='bold', color='#DC2626',
                bbox=dict(boxstyle='round,pad=0.15', facecolor='#FFFFFF', edgecolor='#DC2626', linewidth=0.8, alpha=0.95))

    draw_inc('inbound', 'card_update')
    draw_inc('outbound', 'val_stock')
    draw_inc('outbound', 'pessimistic')

    # Outbound to card_update diagonal
    p_out = nodes['outbound']['right']
    p_card = nodes['card_update']['left']
    ax.annotate('', xy=p_card, xytext=p_out,
                arrowprops=dict(arrowstyle="->", color="#DC2626", lw=1.4, linestyle="--"))
    ax.text((p_out[0] + p_card[0]) / 2 - 0.1, (p_out[1] + p_card[1]) / 2 + 0.12, "<<include>>",
            ha='center', va='center', fontsize=7.0, fontweight='bold', color='#DC2626',
            bbox=dict(boxstyle='round,pad=0.15', facecolor='#FFFFFF', edgecolor='#DC2626', linewidth=0.8, alpha=0.95))

    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[OK] Saved Hình 4.1.1 to {out_path}")


# ==============================================================================
# 4. HÌNH 4.1.2: BIỂU ĐỒ USE CASE PHÂN HỆ TRỢ LÝ AI (image6.png) - EDGE ATTACH
# ==============================================================================
def draw_ai_usecase(out_path):
    fig, ax = plt.subplots(figsize=(15, 9.5), dpi=300)
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 9.5)
    ax.axis('off')
    fig.patch.set_facecolor('#F8FAFC')
    ax.set_facecolor('#F8FAFC')

    sys_box = FancyBboxPatch(
        (3.6, 0.4), 9.2, 8.7,
        boxstyle="round,pad=0.2,rounding_size=0.15",
        facecolor='#FFFFFF', edgecolor='#7C3AED', linewidth=2.0
    )
    ax.add_patch(sys_box)

    ax.text(8.2, 8.75, "PHÂN HỆ TRỢ LÝ AI (GOOGLE GEMINI 1.5 FLASH API)",
            ha='center', va='center', fontsize=13.0, fontweight='bold', color='#6D28D9')

    draw_actor(ax, 1.6, 7.0, "Thủ Kho Kiêm\nKế Toán", "Vận hành & Theo dõi kho", '#0D9488')
    draw_actor(ax, 1.6, 4.4, "Admin\n(Quản trị viên)", "Giám sát & Chiến lược", '#1E40AF')
    draw_actor(ax, 1.6, 1.8, "Nhân Viên Kho\n(Staff)", "Xem khuyến nghị Dashboard", '#9333EA')
    draw_actor(ax, 13.8, 5.0, "Google Gemini\n1.5 Flash API", "Mô hình LLM Phân tích", '#7C3AED')

    nodes = {}

    def add_uc(key, x, y, text, subtext="", fill='#EDE9FE', border='#7C3AED', w=3.4, h=0.74):
        box = FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                             boxstyle="round,pad=0.08,rounding_size=0.35",
                             facecolor=fill, edgecolor=border, linewidth=1.4)
        ax.add_patch(box)
        if subtext:
            ax.text(x, y + 0.10, text, ha='center', va='center', fontsize=8.8, fontweight='bold', color='#0F172A')
            ax.text(x, y - 0.16, subtext, ha='center', va='center', fontsize=7.0, color='#64748B')
        else:
            ax.text(x, y, text, ha='center', va='center', fontsize=8.8, fontweight='bold', color='#0F172A')
        nodes[key] = {
            'left': (x - w / 2, y),
            'right': (x + w / 2, y),
            'top': (x, y + h / 2),
            'bottom': (x, y - h / 2)
        }

    # Left Column: Primary AI Use Cases (x = 5.8)
    add_uc('advisory', 5.8, 7.0, "Xem Khuyến Nghị Dashboard", "Widget 3 khuyến nghị nhanh (US07)", '#EDE9FE', '#7C3AED')
    add_uc('report', 5.8, 4.4, "Sinh Báo Cáo Chiến Lược", "Phân tích 3 phần toàn diện (US09)", '#EDE9FE', '#7C3AED')
    add_uc('fallback', 5.8, 1.8, "Dự Phòng Offline Engine", "Local Rule-based Analyzer", '#F1F5F9', '#475569')

    # Right Column: AI Supporting / Security (x = 10.8)
    add_uc('grounding', 10.8, 6.0, "Grounded Prompting", "Template bám sát số liệu thật", '#FEF3C7', '#D97706')
    add_uc('sanitizer', 10.8, 3.8, "Khử Trùng Giá Vốn Nhập", "Data Sanitizer Bảo Mật Tuyệt Đối", '#FEE2E2', '#DC2626')

    # Connect Human Actors to LEFT edges
    def conn_left(ax_x, ax_y, node_key, col):
        p1 = (ax_x + 0.35, ax_y)
        p2 = nodes[node_key]['left']
        ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=col, linewidth=1.3)

    conn_left(1.6, 7.0, 'advisory', '#0D9488')
    conn_left(1.6, 7.0, 'report', '#0D9488')
    conn_left(1.6, 4.4, 'advisory', '#1E40AF')
    conn_left(1.6, 4.4, 'report', '#1E40AF')
    conn_left(1.6, 1.8, 'advisory', '#9333EA')

    # Connect AI Actor to RIGHT edges
    def conn_right(ax_x, ax_y, node_key, col):
        p1 = (ax_x - 0.35, ax_y)
        p2 = nodes[node_key]['right']
        ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=col, linewidth=1.3)

    conn_right(13.8, 5.0, 'grounding', '#7C3AED')
    conn_right(13.8, 5.0, 'sanitizer', '#7C3AED')

    # Relationships between use cases
    def draw_inc(k1, k2):
        p1 = nodes[k1]['right']
        p2 = nodes[k2]['left']
        ax.annotate('', xy=p2, xytext=p1,
                    arrowprops=dict(arrowstyle="->", color="#DC2626", lw=1.4, linestyle="--"))
        mid_x = (p1[0] + p2[0]) / 2
        mid_y = (p1[1] + p2[1]) / 2 + 0.15
        ax.text(mid_x, mid_y, "<<include>>", ha='center', va='center', fontsize=7.2, fontweight='bold', color='#DC2626',
                bbox=dict(boxstyle='round,pad=0.15', facecolor='#FFFFFF', edgecolor='#DC2626', linewidth=0.8, alpha=0.95))

    draw_inc('report', 'sanitizer')
    draw_inc('report', 'grounding')

    # Fallback to report <<extend>> (Strictly Vertical)
    p_fall = nodes['fallback']['top']
    p_rep_bot = nodes['report']['bottom']
    ax.annotate('', xy=p_rep_bot, xytext=p_fall,
                arrowprops=dict(arrowstyle="->", color="#475569", lw=1.4, linestyle="--"))
    ax.text(p_fall[0] + 0.38, (p_fall[1] + p_rep_bot[1]) / 2, "<<extend>>",
            ha='left', va='center', fontsize=7.2, fontweight='bold', color='#475569',
            bbox=dict(boxstyle='round,pad=0.15', facecolor='#FFFFFF', edgecolor='#475569', linewidth=0.8, alpha=0.95))

    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[OK] Saved Hình 4.1.2 to {out_path}")


# ==============================================================================
# 5. HÌNH 4.2.1: BIỂU ĐỒ TRÌNH TỰ XUẤT KHO CHỐNG TỒN ÂM (image7.png)
# ==============================================================================
def draw_sequence_outbound(out_path):
    fig, ax = plt.subplots(figsize=(15, 11), dpi=300)
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 11)
    ax.axis('off')
    fig.patch.set_facecolor('#F8FAFC')
    ax.set_facecolor('#F8FAFC')

    ax.text(7.5, 10.5, "BIỂU ĐỒ TRÌNH TỰ: LẬP PHIẾU XUẤT KHO VÀ KHÓA GIAO DỊCH CHỐNG TỒN ÂM",
            ha='center', va='center', fontsize=12.5, fontweight='bold', color='#0F172A')

    lifelines = [
        ("Thủ Kho Kiêm Kế Toán (Actor)", 2.0, '#0D9488'),
        ("Web UI (SSR/JS)", 5.6, '#16A34A'),
        ("FastAPI Backend", 9.4, '#2563EB'),
        ("MySQL 8.0 Database (InnoDB)", 13.2, '#D97706')
    ]

    for name, x, col in lifelines:
        box = FancyBboxPatch((x - 1.3, 9.4), 2.6, 0.7, boxstyle="round,pad=0.08,rounding_size=0.1",
                             facecolor='#FFFFFF', edgecolor=col, linewidth=1.8)
        ax.add_patch(box)
        ax.text(x, 9.75, name, ha='center', va='center', fontsize=8.2, fontweight='bold', color=col)
        ax.plot([x, x], [9.4, 0.6], linestyle='--', color='#94A3B8', linewidth=1.2)

    def draw_msg(y, x1, x2, text, is_dashed=False, is_error=False, self_call=False):
        col = '#DC2626' if is_error else ('#2563EB' if not is_dashed else '#059669')
        style = '--' if is_dashed else '-'
        if self_call:
            ax.plot([x1, x1 + 0.8, x1 + 0.8, x1], [y, y, y - 0.3, y - 0.3], color=col, linewidth=1.4)
            ax.annotate('', xy=(x1, y - 0.3), xytext=(x1 + 0.1, y - 0.3),
                        arrowprops=dict(arrowstyle="->", color=col, lw=1.4))
            ax.text(x1 + 0.9, y - 0.15, text, ha='left', va='center', fontsize=8.0, color='#0F172A', fontweight='bold')
        else:
            ax.annotate('', xy=(x2, y), xytext=(x1, y),
                        arrowprops=dict(arrowstyle="->", color=col, lw=1.4, linestyle=style))
            ax.text((x1 + x2) / 2, y + 0.15, text, ha='center', va='center', fontsize=8.0, color='#0F172A', fontweight='bold')

    draw_msg(8.8, 2.0, 5.6, "1. Chọn hàng (MaHH), nhập SoLuongXuat -> Bấm 'Xác nhận'")
    draw_msg(8.2, 5.6, 9.4, "2. POST /api/v1/kho/phieu-xuat {MaHH, SoLuongXuat}")
    draw_msg(7.6, 9.4, 13.2, "3. BEGIN TRANSACTION (ACID)")
    draw_msg(7.0, 9.4, 13.2, "4. UPDATE ton_kho SET SoLuongTon = SoLuongTon - :qty WHERE SoLuongTon >= :qty")
    draw_msg(6.4, 13.2, 9.4, "5. rowcount = 1 (Trừ tồn kho thành công)", is_dashed=True)
    draw_msg(5.8, 9.4, 13.2, "6. INSERT INTO phieu_xuat & chi_tiet_phieu_xuat")
    draw_msg(5.2, 9.4, 13.2, "7. INSERT INTO the_kho (Loai='XUAT', SoLuongThayDoi=-qty, TonSauGD)")
    draw_msg(4.6, 9.4, 13.2, "8. COMMIT TRANSACTION")
    draw_msg(4.0, 13.2, 9.4, "9. Transaction thành công", is_dashed=True)
    draw_msg(3.4, 9.4, 5.6, "10. HTTP 201 Created (Chi tiết phiếu xuất & thẻ kho)", is_dashed=True)
    draw_msg(2.8, 5.6, 2.0, "11. Cập nhật tồn kho Realtime & Thông báo thành công", is_dashed=True)

    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[OK] Saved Hình 4.2.1 to {out_path}")


# ==============================================================================
# 6. HÌNH 4.2.2: BIỂU ĐỒ TRÌNH TỰ AI SINH BÁO CÁO (image8.png)
# ==============================================================================
def draw_seq_ai_report(out_path):
    fig, ax = plt.subplots(figsize=(15, 10), dpi=300)
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 10)
    ax.axis('off')
    fig.patch.set_facecolor('#F8FAFC')
    ax.set_facecolor('#F8FAFC')

    ax.text(7.5, 9.5, "BIỂU ĐỒ TRÌNH TỰ: CHỨC NĂNG AI SINH BÁO CÁO NHẬP - XUẤT - TỒN",
            ha='center', va='center', fontsize=12.5, fontweight='bold', color='#0F172A')

    lifelines = [
        ("Thủ Kho Kiêm Kế Toán / Admin", 1.8, '#0D9488'),
        ("Web UI (AI Modal)", 4.5, '#16A34A'),
        ("FastAPI Backend", 7.2, '#2563EB'),
        ("Data Sanitizer", 9.6, '#DC2626'),
        ("MySQL 8.0 CSDL", 12.0, '#D97706'),
        ("Gemini API", 14.2, '#7C3AED')
    ]

    for name, x, col in lifelines:
        box = FancyBboxPatch((x - 1.15, 8.5), 2.3, 0.65, boxstyle="round,pad=0.08,rounding_size=0.1",
                             facecolor='#FFFFFF', edgecolor=col, linewidth=1.8)
        ax.add_patch(box)
        ax.text(x, 8.82, name, ha='center', va='center', fontsize=7.5, fontweight='bold', color=col)
        ax.plot([x, x], [8.5, 0.5], linestyle='--', color='#94A3B8', linewidth=1.2)

    def draw_msg(y, x1, x2, text, is_dashed=False):
        col = '#059669' if is_dashed else '#2563EB'
        style = '--' if is_dashed else '-'
        ax.annotate('', xy=(x2, y), xytext=(x1, y),
                    arrowprops=dict(arrowstyle="->", color=col, lw=1.3, linestyle=style))
        ax.text((x1 + x2) / 2, y + 0.14, text, ha='center', va='center', fontsize=7.2, color='#0F172A', fontweight='bold')

    draw_msg(7.8, 1.8, 4.5, "1. Chọn Tháng/Kỳ & Bấm 'Sinh Báo Cáo AI'")
    draw_msg(7.0, 4.5, 7.2, "2. POST /api/v1/ai/generate-report {month, year}")
    draw_msg(6.2, 7.2, 12.0, "3. Query dữ liệu Nhập-Xuất-Tồn & Thẻ Kho 30 ngày")
    draw_msg(5.4, 12.0, 7.2, "4. Trả về raw dataset (kèm DonGiaNhap)", is_dashed=True)
    draw_msg(4.6, 7.2, 9.6, "5. Chuyển raw dataset qua Data Sanitizer")
    draw_msg(3.8, 9.6, 7.2, "6. Loại bỏ DonGiaNhap & Giá vốn (Bảo mật nội bộ)", is_dashed=True)
    draw_msg(3.0, 7.2, 14.2, "7. Gửi Grounded Prompt + Clean Data tới Gemini API")
    draw_msg(2.2, 14.2, 7.2, "8. Trả về kết quả phân tích chuẩn JSON 3 phần", is_dashed=True)
    draw_msg(1.4, 7.2, 4.5, "9. Trả về Markdown Báo cáo hoàn chỉnh", is_dashed=True)
    draw_msg(0.7, 4.5, 1.8, "10. Hiển thị Báo cáo AI, cho phép Xuất PDF/Excel đối soát", is_dashed=True)

    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[OK] Saved Hình 4.2.2 to {out_path}")


# ==============================================================================
# 7. HÌNH 4.2.3: BIỂU ĐỒ TRÌNH TỰ NHẬP KHO (image9.png)
# ==============================================================================
def draw_seq_inbound(out_path):
    fig, ax = plt.subplots(figsize=(15, 10), dpi=300)
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 10)
    ax.axis('off')
    fig.patch.set_facecolor('#F8FAFC')
    ax.set_facecolor('#F8FAFC')

    ax.text(7.5, 9.5, "BIỂU ĐỒ TRÌNH TỰ: LẬP PHIẾU NHẬP KHO VÀ CẬP NHẬT TĂNG TỒN KHO (ACID)",
            ha='center', va='center', fontsize=12.5, fontweight='bold', color='#0F172A')

    lifelines = [
        ("Thủ Kho Kiêm Kế Toán (Actor)", 1.8, '#0D9488'),
        ("Web UI (Form Nhập)", 5.4, '#16A34A'),
        ("FastAPI Backend", 9.2, '#2563EB'),
        ("MySQL 8.0 Database (InnoDB)", 13.2, '#D97706')
    ]

    for name, x, col in lifelines:
        box = FancyBboxPatch((x - 1.2, 8.5), 2.4, 0.65, boxstyle="round,pad=0.08,rounding_size=0.1",
                             facecolor='#FFFFFF', edgecolor=col, linewidth=1.8)
        ax.add_patch(box)
        ax.text(x, 8.82, name, ha='center', va='center', fontsize=8.2, fontweight='bold', color=col)
        ax.plot([x, x], [8.5, 0.5], linestyle='--', color='#94A3B8', linewidth=1.2)

    def draw_msg(y, x1, x2, text, is_dashed=False):
        col = '#059669' if is_dashed else '#2563EB'
        style = '--' if is_dashed else '-'
        ax.annotate('', xy=(x2, y), xytext=(x1, y),
                    arrowprops=dict(arrowstyle="->", color=col, lw=1.3, linestyle=style))
        ax.text((x1 + x2) / 2, y + 0.14, text, ha='center', va='center', fontsize=7.5, color='#0F172A', fontweight='bold')

    draw_msg(7.8, 1.8, 5.4, "1. Chọn Nhà cung cấp, nhập danh sách hàng, số lượng và đơn giá nhập")
    draw_msg(7.0, 5.4, 9.2, "2. POST /api/v1/kho/phieu-nhap (PhieuNhapCreate payload)")
    draw_msg(6.2, 9.2, 13.2, "3. BEGIN TRANSACTION (Atomic ACID)")
    draw_msg(5.4, 9.2, 13.2, "4. INSERT INTO phieu_nhap (Master) & chi_tiet_phieu_nhap (Detail)")
    draw_msg(4.6, 9.2, 13.2, "5. UPDATE ton_kho SET SoLuongTon = SoLuongTon + :qty")
    draw_msg(3.8, 9.2, 13.2, "6. INSERT INTO the_kho (Loai='NHAP', SoLuongThayDoi=+qty, TonSauGD)")
    draw_msg(3.0, 9.2, 13.2, "7. COMMIT TRANSACTION")
    draw_msg(2.2, 13.2, 9.2, "8. Xác nhận Commit thành công", is_dashed=True)
    draw_msg(1.4, 9.2, 5.4, "9. HTTP 201 Created & WebSocket Broadcast INVENTORY_UPDATED", is_dashed=True)
    draw_msg(0.7, 5.4, 1.8, "10. Hiển thị thông báo thành công & Cập nhật tồn kho tức thời", is_dashed=True)

    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[OK] Saved Hình 4.2.3 to {out_path}")


# ==============================================================================
# 8. HÌNH 4.2.4: BIỂU ĐỒ TRÌNH TỰ TRA CỨU THẺ KHO & CẢNH BÁO TỒN MIN (image10.png)
# ==============================================================================
def draw_seq_the_kho_alert(out_path):
    fig, ax = plt.subplots(figsize=(15, 10), dpi=300)
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 10)
    ax.axis('off')
    fig.patch.set_facecolor('#F8FAFC')
    ax.set_facecolor('#F8FAFC')

    ax.text(7.5, 9.5, "BIỂU ĐỒ TRÌNH TỰ: TRA CỨU THẺ KHO VÀ TỰ ĐỘNG CẢNH BÁO TỒN TỐI THIỂU",
            ha='center', va='center', fontsize=12.5, fontweight='bold', color='#0F172A')

    lifelines = [
        ("Người Dùng (Staff/Thủ kho/Admin)", 2.0, '#9333EA'),
        ("Web UI (Dashboard / Thẻ Kho)", 5.6, '#16A34A'),
        ("FastAPI Backend", 9.4, '#2563EB'),
        ("MySQL 8.0 Database", 13.2, '#D97706')
    ]

    for name, x, col in lifelines:
        box = FancyBboxPatch((x - 1.3, 8.5), 2.6, 0.65, boxstyle="round,pad=0.08,rounding_size=0.1",
                             facecolor='#FFFFFF', edgecolor=col, linewidth=1.8)
        ax.add_patch(box)
        ax.text(x, 8.82, name, ha='center', va='center', fontsize=8.0, fontweight='bold', color=col)
        ax.plot([x, x], [8.5, 0.5], linestyle='--', color='#94A3B8', linewidth=1.2)

    def draw_msg(y, x1, x2, text, is_dashed=False):
        col = '#059669' if is_dashed else '#2563EB'
        style = '--' if is_dashed else '-'
        ax.annotate('', xy=(x2, y), xytext=(x1, y),
                    arrowprops=dict(arrowstyle="->", color=col, lw=1.3, linestyle=style))
        ax.text((x1 + x2) / 2, y + 0.14, text, ha='center', va='center', fontsize=7.5, color='#0F172A', fontweight='bold')

    draw_msg(7.8, 2.0, 5.6, "1. Mở Dashboard / Chọn 'Tra Cứu Thẻ Kho' (Hỗ trợ cả Nhân viên kho)")
    draw_msg(7.0, 5.6, 9.4, "2. GET /api/v1/kho/the-kho?ma_hh=HH-001&from_date=...&to_date=...")
    draw_msg(6.2, 9.4, 13.2, "3. SELECT * FROM the_kho WHERE MaHH = :id ORDER BY NgayGiaoDich ASC")
    draw_msg(5.4, 13.2, 9.4, "4. Trả về lịch sử giao dịch (Nhập, Xuất, Tồn sau giao dịch)", is_dashed=True)
    draw_msg(4.6, 5.6, 9.4, "5. Song song gọi GET /api/v1/kho/canh-bao-ton-kho (Kiểm tra cảnh báo tồn)")
    draw_msg(3.8, 9.4, 13.2, "6. SELECT * FROM ton_kho t JOIN hang_hoa h ON t.MaHH=h.MaHH WHERE SoLuongTon <= TonToiThieu")
    draw_msg(3.0, 13.2, 9.4, "7. Danh sách các mặt hàng chạm/dưới mức tồn min", is_dashed=True)
    draw_msg(2.2, 9.4, 5.6, "8. Response {the_kho_records: [...], min_stock_alerts: [...]}", is_dashed=True)
    draw_msg(1.4, 5.6, 2.0, "9. Hiển thị bảng biểu biến động thẻ kho & Bật Badge/Cảnh báo đỏ trên Dashboard", is_dashed=True)

    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[OK] Saved Hình 4.2.4 to {out_path}")


# ==============================================================================
# 9. HÌNH 4.2.5: BIỂU ĐỒ TRÌNH TỰ XUẤT BÁO CÁO EXCEL (image11.png)
# ==============================================================================
def draw_seq_export_report(out_path):
    fig, ax = plt.subplots(figsize=(15, 10), dpi=300)
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 10)
    ax.axis('off')
    fig.patch.set_facecolor('#F8FAFC')
    ax.set_facecolor('#F8FAFC')

    ax.text(7.5, 9.5, "BIỂU ĐỒ TRÌNH TỰ: XUẤT BÁO CÁO DỮ LIỆU KHO RA FILE EXCEL / PDF",
            ha='center', va='center', fontsize=12.5, fontweight='bold', color='#0F172A')

    lifelines = [
        ("Thủ Kho Kiêm Kế Toán / Admin", 2.0, '#7C3AED'),
        ("Web UI (Dashboard / Items)", 5.6, '#16A34A'),
        ("FastAPI Backend", 8.8, '#2563EB'),
        ("OpenPyXL Generator", 11.6, '#0D9488'),
        ("MySQL 8.0 Database", 14.0, '#D97706')
    ]

    for name, x, col in lifelines:
        box = FancyBboxPatch((x - 1.2, 8.5), 2.4, 0.65, boxstyle="round,pad=0.08,rounding_size=0.1",
                             facecolor='#FFFFFF', edgecolor=col, linewidth=1.8)
        ax.add_patch(box)
        ax.text(x, 8.82, name, ha='center', va='center', fontsize=8.0, fontweight='bold', color=col)
        ax.plot([x, x], [8.5, 0.5], linestyle='--', color='#94A3B8', linewidth=1.2)

    def draw_msg(y, x1, x2, text, is_dashed=False):
        col = '#059669' if is_dashed else '#2563EB'
        style = '--' if is_dashed else '-'
        ax.annotate('', xy=(x2, y), xytext=(x1, y),
                    arrowprops=dict(arrowstyle="->", color=col, lw=1.3, linestyle=style))
        ax.text((x1 + x2) / 2, y + 0.14, text, ha='center', va='center', fontsize=7.5, color='#0F172A', fontweight='bold')

    draw_msg(7.8, 2.0, 5.6, "1. Bấm nút 'Xuất Excel' trên Dashboard hoặc Danh mục hàng hóa")
    draw_msg(7.0, 5.6, 8.8, "2. GET /api/v1/reports/export/excel (Bearer Token / Cookie)")
    draw_msg(6.2, 8.8, 8.8, "3. require_role(['Admin', 'Thukho']) -> Xác thực quyền hợp lệ!", is_dashed=True)
    draw_msg(5.4, 8.8, 14.0, "4. Query danh sách SKU, Tồn khả dụng, Định mức tồn min từ CSDL")
    draw_msg(4.6, 14.0, 8.8, "5. Trả về DataSet danh mục tồn kho thực tế", is_dashed=True)
    draw_msg(3.8, 8.8, 11.6, "6. Sinh tệp Excel .xlsx chuẩn biểu mẫu kế toán (Styles, Header, Cảnh báo)")
    draw_msg(3.0, 11.6, 8.8, "7. Trả về BytesIO Stream hoàn chỉnh", is_dashed=True)
    draw_msg(2.2, 8.8, 5.6, "8. StreamingResponse (application/vnd.openxmlformats..., Content-Disposition)", is_dashed=True)
    draw_msg(1.4, 5.6, 2.0, "9. Trình duyệt tự động tải tệp tin BaoCao_NhapXuatTon_SmartLogis_*.xlsx", is_dashed=True)

    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[OK] Saved Hình 4.2.5 to {out_path}")


# ==============================================================================
# 10. HÌNH 4.2.6: BIỂU ĐỒ TRÌNH TỰ ĐĂNG NHẬP JWT (image12.png)
# ==============================================================================
def draw_seq_jwt_auth(out_path):
    fig, ax = plt.subplots(figsize=(15, 10), dpi=300)
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 10)
    ax.axis('off')
    fig.patch.set_facecolor('#F8FAFC')
    ax.set_facecolor('#F8FAFC')

    ax.text(7.5, 9.5, "BIỂU ĐỒ TRÌNH TỰ: ĐĂNG NHẬP VÀ PHÂN QUYỀN TRUY CẬP JWT (US01)",
            ha='center', va='center', fontsize=12.5, fontweight='bold', color='#0F172A')

    lifelines = [
        ("Người Dùng (Admin/Thủ kho/Nhân viên)", 2.0, '#1E40AF'),
        ("Web UI (Auth Form /login)", 5.8, '#16A34A'),
        ("FastAPI Auth Router", 9.4, '#2563EB'),
        ("MySQL 8.0 Database", 13.2, '#D97706')
    ]

    for name, x, col in lifelines:
        box = FancyBboxPatch((x - 1.3, 8.5), 2.6, 0.65, boxstyle="round,pad=0.08,rounding_size=0.1",
                             facecolor='#FFFFFF', edgecolor=col, linewidth=1.8)
        ax.add_patch(box)
        ax.text(x, 8.82, name, ha='center', va='center', fontsize=8.0, fontweight='bold', color=col)
        ax.plot([x, x], [8.5, 0.5], linestyle='--', color='#94A3B8', linewidth=1.2)

    def draw_msg(y, x1, x2, text, is_dashed=False):
        col = '#059669' if is_dashed else '#2563EB'
        style = '--' if is_dashed else '-'
        ax.annotate('', xy=(x2, y), xytext=(x1, y),
                    arrowprops=dict(arrowstyle="->", color=col, lw=1.3, linestyle=style))
        ax.text((x1 + x2) / 2, y + 0.14, text, ha='center', va='center', fontsize=7.5, color='#0F172A', fontweight='bold')

    draw_msg(7.8, 2.0, 5.8, "1. Nhập Tên đăng nhập và Mật khẩu (hoặc bấm nút Đăng nhập mẫu)")
    draw_msg(7.0, 5.8, 9.4, "2. POST /api/v1/auth/login (TenDangNhap, MatKhau)")
    draw_msg(6.2, 9.4, 13.2, "3. Query NguoiDung WHERE TenDangNhap = :username AND KichHoat = true")
    draw_msg(5.4, 13.2, 9.4, "4. Trả về NguoiDung (Bcrypt Hash, VaiTro: Admin | Thukho | Nhanvien)", is_dashed=True)
    draw_msg(4.6, 9.4, 9.4, "5. verify_password(plain, hash) -> Khớp mật khẩu!")
    draw_msg(3.8, 9.4, 9.4, "6. create_access_token(payload: {sub, mand, vaitro, hoten})")
    draw_msg(3.0, 9.4, 5.8, "7. HTTP 200 OK + Set-Cookie: access_token=Bearer ... (HttpOnly, SameSite=Lax)", is_dashed=True)
    draw_msg(2.2, 5.8, 2.0, "8. Chuyển hướng /dashboard theo phân quyền 3 vai trò (RBAC Guard)", is_dashed=True)

    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[OK] Saved Hình 4.2.6 to {out_path}")


# ==============================================================================
# 11. HÌNH 4.3.3: SƠ ĐỒ QUAN HỆ CƠ SỞ DỮ LIỆU CỤ THỂ (ERD - image13.png)
# ĐÃ BỔ SUNG TOÀN BỘ 10 ĐƯỜNG NỐI NGOẠI KHÓA TRỰC GIAO (ORTHOGONAL LINES)
# ==============================================================================
def draw_database_erd(out_path):
    fig, ax = plt.subplots(figsize=(18, 13.5), dpi=300)
    ax.set_xlim(0, 18)
    ax.set_ylim(0, 13.5)
    ax.axis('off')
    fig.patch.set_facecolor('#F8FAFC')
    ax.set_facecolor('#F8FAFC')

    ax.text(9.0, 13.0, "SƠ ĐỒ QUAN HỆ CƠ SỞ DỮ LIỆU MYSQL 8.0 (PHYSICAL ERD SCHEMA)",
            ha='center', va='center', fontsize=14.0, fontweight='bold', color='#0F172A')

    tables = {}

    def draw_table(key, x, y, w, h, name, fields, header_bg='#1E293B', body_bg='#FFFFFF'):
        header_h = 0.52
        h_box = FancyBboxPatch((x, y + h - header_h), w, header_h, boxstyle="round,pad=0.04,rounding_size=0.08",
                               facecolor=header_bg, edgecolor='#334155', linewidth=1.5)
        ax.add_patch(h_box)
        ax.text(x + w / 2, y + h - header_h / 2, name, ha='center', va='center', fontsize=8.8, fontweight='bold', color='#FFFFFF')

        b_box = FancyBboxPatch((x, y), w, h - header_h, boxstyle="round,pad=0.04,rounding_size=0.08",
                               facecolor=body_bg, edgecolor='#334155', linewidth=1.5)
        ax.add_patch(b_box)

        line_y = y + h - header_h - 0.26
        field_positions = {}
        for f in fields:
            is_pk = "(PK)" in f
            is_fk = "(FK)" in f
            is_chk = "CHECK" in f
            col = '#B91C1C' if is_pk else ('#2563EB' if is_fk else ('#D97706' if is_chk else '#1E293B'))
            ax.text(x + 0.15, line_y, f, ha='left', va='center', fontsize=7.2, color=col,
                    fontweight='bold' if (is_pk or is_chk) else 'normal')
            field_name = f.split(':')[0].strip()
            field_positions[field_name] = line_y
            line_y -= 0.25

        tables[key] = {
            'x': x, 'y': y, 'w': w, 'h': h,
            'left': (x, y + h / 2),
            'right': (x + w, y + h / 2),
            'top': (x + w / 2, y + h),
            'bottom': (x + w / 2, y),
            'fields': field_positions
        }

    # Bố cục 11 bảng chuẩn hóa
    # Column 1 (Master / Catalog data)
    draw_table('nguoi_dung', 0.6, 9.8, 3.4, 2.3, "NguoiDung (Người dùng)", [
        "MaND (PK): INT AUTO_INCREMENT",
        "TenDangNhap: VARCHAR(50)",
        "MatKhau: VARCHAR(255)",
        "HoTen: VARCHAR(100)",
        "VaiTro: VARCHAR(20) [Admin/Thukho/Nhanvien]",
        "NgayTao: TIMESTAMP"
    ], '#1E40AF', '#EFF6FF')

    draw_table('nhom_hang', 0.6, 6.7, 3.2, 1.8, "NhomHang (Nhóm hàng)", [
        "MaNhom (PK): VARCHAR(20)",
        "TenNhom: VARCHAR(100)",
        "MoTa: TEXT"
    ], '#059669', '#F0FDF4')

    draw_table('don_vi_tinh', 0.6, 3.9, 3.2, 1.8, "DonViTinh (Đơn vị tính)", [
        "MaDVT (PK): VARCHAR(20)",
        "TenDVT: VARCHAR(50)",
        "MoTa: TEXT"
    ], '#059669', '#F0FDF4')

    draw_table('nha_cung_cap', 0.6, 0.7, 3.2, 2.2, "NhaCungCap (Nhà cung cấp)", [
        "MaNCC (PK): VARCHAR(20)",
        "TenNCC: VARCHAR(255)",
        "DiaChi: VARCHAR(255)",
        "SoDienThoai: VARCHAR(20)",
        "Email: VARCHAR(100)"
    ], '#D97706', '#FFFBEB')

    # Column 2 (Core Item & Stock)
    draw_table('hang_hoa', 5.2, 6.2, 3.3, 2.7, "HangHoa (Hàng hóa)", [
        "MaHH (PK): VARCHAR(20)",
        "TenHH: VARCHAR(255)",
        "MaNhom (FK): VARCHAR(20)",
        "MaDVT (FK): VARCHAR(20)",
        "TonToiThieu: INT DEFAULT 0",
        "MoTa: TEXT"
    ], '#059669', '#F0FDF4')

    draw_table('ton_kho', 5.2, 2.5, 3.3, 2.2, "TonKho (Tồn kho thực tế)", [
        "MaHH (PK, FK): VARCHAR(20)",
        "SoLuongTon: INT CHECK (>= 0)",
        "CapNhatCuoi: TIMESTAMP"
    ], '#DC2626', '#FEF2F2')

    # Column 3 (Transactions Master & Detail)
    draw_table('phieu_nhap', 9.6, 9.8, 3.4, 2.3, "PhieuNhap (Phiếu nhập)", [
        "MaPN (PK): VARCHAR(30)",
        "NgayNhap: TIMESTAMP",
        "MaNCC (FK): VARCHAR(20)",
        "MaND (FK): INT",
        "TongTien: FLOAT DEFAULT 0",
        "GhiChu: TEXT"
    ], '#2563EB', '#EFF6FF')

    draw_table('ct_phieu_nhap', 9.6, 6.2, 3.4, 2.4, "ChiTietPhieuNhap (CT Nhập)", [
        "MaCTPN (PK): INT AUTO_INCREMENT",
        "MaPN (FK): VARCHAR(30)",
        "MaHH (FK): VARCHAR(20)",
        "SoLuongNhap: INT CHECK (> 0)",
        "DonGiaNhap: FLOAT CHECK (>= 0)",
        "ThanhTien: FLOAT"
    ], '#2563EB', '#EFF6FF')

    # Column 4 (Outbound Transactions & Log)
    draw_table('phieu_xuat', 14.0, 9.8, 3.4, 2.3, "PhieuXuat (Phiếu xuất)", [
        "MaPX (PK): VARCHAR(30)",
        "NgayXuat: TIMESTAMP",
        "MaND (FK): INT",
        "NguoiNhan: VARCHAR(100)",
        "LyDoXuat: TEXT"
    ], '#7C3AED', '#FAF5FF')

    draw_table('ct_phieu_xuat', 14.0, 6.2, 3.4, 2.2, "ChiTietPhieuXuat (CT Xuất)", [
        "MaCTPX (PK): INT AUTO_INCREMENT",
        "MaPX (FK): VARCHAR(30)",
        "MaHH (FK): VARCHAR(20)",
        "SoLuongXuat: INT CHECK (> 0)"
    ], '#7C3AED', '#FAF5FF')

    # Audit Trail: TheKho
    draw_table('the_kho', 9.6, 0.7, 7.8, 2.8, "TheKho (Sổ thẻ kho lưu vết biến động ACID)", [
        "MaGD (PK): INT AUTO_INCREMENT",
        "NgayGiaoDich: TIMESTAMP",
        "MaHH (FK): VARCHAR(20)",
        "MaChungTu: VARCHAR(30) [PN/PX]",
        "LoaiGiaoDich: VARCHAR(10) ['NHAP' / 'XUAT']",
        "SoLuongThayDoi: INT",
        "TonSauGiaoDich: INT CHECK (>= 0)"
    ], '#0D9488', '#F0FDFA')

    # ==========================================================================
    # VẼ CÁC ĐƯỜNG NỐI QUAN HỆ TRỰC GIAO (ORTHOGONAL FK LINES)
    # ==========================================================================
    def draw_fk_ortho(points, label="", col="#475569", lw=1.4):
        """Vẽ đường gấp khúc trực giao có mũi tên ở đích và nhãn."""
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        ax.plot(xs, ys, color=col, linewidth=lw, zorder=1)
        # Arrow at end
        ax.annotate('', xy=points[-1], xytext=points[-2],
                    arrowprops=dict(arrowstyle="->", color=col, lw=lw))
        if label:
            if len(points) == 2:
                mid_x = (points[0][0] + points[1][0]) / 2
                mid_y = (points[0][1] + points[1][1]) / 2
            else:
                idx = len(points) // 2
                p_a = points[idx - 1]
                p_b = points[idx]
                mid_x = (p_a[0] + p_b[0]) / 2
                mid_y = (p_a[1] + p_b[1]) / 2
            ax.text(mid_x, mid_y + 0.14, label, ha='center', va='center',
                    fontsize=7.0, fontweight='bold', color=col,
                    bbox=dict(boxstyle='round,pad=0.2', facecolor='#FFFFFF', edgecolor=col, linewidth=0.8, alpha=0.98))

    # 1. NhomHang -> HangHoa (1 - N)
    draw_fk_ortho([(3.8, 7.6), (4.5, 7.6), (4.5, 7.6), (5.2, 7.6)], "1..N (MaNhom)", "#059669")

    # 2. DonViTinh -> HangHoa (1 - N)
    draw_fk_ortho([(3.8, 4.8), (4.5, 4.8), (4.5, 6.9), (5.2, 6.9)], "1..N (MaDVT)", "#059669")

    # 3. HangHoa -> TonKho (1 - 1)
    draw_fk_ortho([(6.85, 6.2), (6.85, 4.7)], "1..1 (MaHH)", "#DC2626", lw=1.8)

    # 4. NhaCungCap -> PhieuNhap (1 - N)
    draw_fk_ortho([(3.8, 1.8), (4.2, 1.8), (4.2, 0.4), (9.2, 0.4), (9.2, 10.9), (9.6, 10.9)], "1..N (MaNCC)", "#D97706")

    # 5. NguoiDung -> PhieuNhap (1 - N)
    draw_fk_ortho([(4.0, 11.2), (9.6, 11.2)], "1..N (MaND)", "#1E40AF")

    # 6. NguoiDung -> PhieuXuat (1 - N)
    draw_fk_ortho([(2.3, 12.1), (2.3, 12.5), (15.7, 12.5), (15.7, 12.1)], "1..N (MaND)", "#1E40AF")

    # 7. PhieuNhap -> ChiTietPhieuNhap (1 - N)
    draw_fk_ortho([(11.3, 9.8), (11.3, 8.6)], "1..N (MaPN)", "#2563EB", lw=1.6)

    # 8. HangHoa -> ChiTietPhieuNhap (1 - N)
    draw_fk_ortho([(8.5, 7.5), (9.6, 7.5)], "1..N (MaHH)", "#059669")

    # 9. PhieuXuat -> ChiTietPhieuXuat (1 - N)
    draw_fk_ortho([(15.7, 9.8), (15.7, 8.4)], "1..N (MaPX)", "#7C3AED", lw=1.6)

    # 10. HangHoa -> ChiTietPhieuXuat (1 - N)
    draw_fk_ortho([(8.5, 6.6), (9.0, 6.6), (9.0, 5.8), (13.5, 5.8), (13.5, 7.2), (14.0, 7.2)], "1..N (MaHH)", "#059669")

    # 11. HangHoa -> TheKho (1 - N)
    draw_fk_ortho([(5.2, 8.2), (4.8, 8.2), (4.8, 0.3), (11.0, 0.3), (11.0, 0.7)], "1..N (MaHH)", "#0D9488")

    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[OK] Saved Hình 4.3.3 to {out_path}")


# ==============================================================================
# 12. HÌNH 4.4.1: BIỂU ĐỒ HOẠT ĐỘNG XUẤT KHO CHỐNG TỒN ÂM (image14.png)
# ĐÃ KHẮC PHỤC TRIỆT ĐỂ KHUYẾT NODE, TOÀN BỘ TRONG VÙNG NHÌN THẤY
# ==============================================================================
def draw_activity_outbound(out_path):
    fig, ax = plt.subplots(figsize=(16, 12), dpi=300)
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 12)
    ax.axis('off')
    fig.patch.set_facecolor('#F8FAFC')
    ax.set_facecolor('#F8FAFC')

    ax.text(8.0, 11.5, "BIỂU ĐỒ HOẠT ĐỘNG (ACTIVITY DIAGRAM): NGHIỆP VỤ XUẤT KHO CHỐNG TỒN ÂM",
            ha='center', va='center', fontsize=13.0, fontweight='bold', color='#0F172A')

    # Start Node
    circle_start = Circle((8.0, 10.8), 0.22, color='#0F172A', fill=True)
    ax.add_patch(circle_start)

    def draw_activity_box(x, y, w, h, text, bg='#EFF6FF', border='#2563EB', text_col='#0F172A'):
        box = FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.08,rounding_size=0.15",
                             facecolor=bg, edgecolor=border, linewidth=1.5)
        ax.add_patch(box)
        ax.text(x, y, text, ha='center', va='center', fontsize=8.2, fontweight='bold', color=text_col)
        return {
            'top': (x, y + h / 2),
            'bottom': (x, y - h / 2),
            'left': (x - w / 2, y),
            'right': (x + w / 2, y)
        }

    def draw_arrow(p1, p2, col='#2563EB'):
        ax.annotate('', xy=p2, xytext=p1,
                    arrowprops=dict(arrowstyle="->", color=col, lw=1.5))

    # Steps
    b1 = draw_activity_box(8.0, 9.8, 7.0, 0.75, "1. Thủ kho kiêm Kế toán chọn SKU & nhập Số lượng xuất trên Web Form", '#EFF6FF', '#2563EB')
    draw_arrow((8.0, 10.58), b1['top'])

    b2 = draw_activity_box(8.0, 8.6, 7.4, 0.75, "2. Gửi POST /api/v1/kho/phieu-xuat & Bắt đầu Database Transaction (ACID)", '#EFF6FF', '#2563EB')
    draw_arrow(b1['bottom'], b2['top'])

    b3 = draw_activity_box(8.0, 7.4, 7.8, 0.75, "3. Khóa dòng & Thực thi Atomic Decrement: UPDATE ton_kho ... WHERE SoLuongTon >= :qty", '#DBEAFE', '#1D4ED8')
    draw_arrow(b2['bottom'], b3['top'])

    # Decision Diamond
    diamond = Polygon([[8.0, 6.4], [10.2, 5.6], [8.0, 4.8], [5.8, 5.6]],
                      closed=True, facecolor='#FEF3C7', edgecolor='#D97706', linewidth=1.8)
    ax.add_patch(diamond)
    ax.text(8.0, 5.6, "Số lượng tồn >=\nSố lượng xuất?\n(rowcount == 1)", ha='center', va='center',
            fontsize=8.0, fontweight='bold', color='#92400E')
    draw_arrow(b3['bottom'], (8.0, 6.4))

    # Branch Left: Không đủ hàng (Rollback & Error) - Orthogonal routing
    ax.text(4.4, 5.85, "[KHÔNG ĐỦ HÀNG]", fontsize=8.0, fontweight='bold', color='#DC2626')
    b_err1 = draw_activity_box(3.6, 4.2, 4.8, 0.8, "4B. Kích hoạt ROLLBACK TRANSACTION\n(Hủy bỏ mọi biến động dữ liệu)", '#FEE2E2', '#DC2626', '#991B1B')
    # From diamond left (5.8, 5.6) -> (3.6, 5.6) -> down to b_err1 top (3.6, 4.6)
    ax.plot([5.8, 3.6, 3.6], [5.6, 5.6, 4.6], color='#DC2626', linewidth=1.5)
    ax.annotate('', xy=(3.6, 4.6), xytext=(3.6, 4.7), arrowprops=dict(arrowstyle="->", color='#DC2626', lw=1.5))

    b_err2 = draw_activity_box(3.6, 2.7, 4.8, 0.8, "5B. Báo lỗi HTTP 400 Bad Request:\n'Chỉ còn tồn X, không đủ xuất Y'", '#FEE2E2', '#DC2626', '#991B1B')
    draw_arrow(b_err1['bottom'], b_err2['top'], '#DC2626')

    # Branch Right: Đủ hàng (Commit & Success) - Orthogonal routing
    ax.text(11.2, 5.85, "[ĐỦ HÀNG / HỢP LỆ]", fontsize=8.0, fontweight='bold', color='#16A34A')
    b_ok1 = draw_activity_box(12.4, 4.2, 5.0, 0.8, "4A. Ghi nhận PhieuXuat, ChiTietPhieuXuat\n& Cập nhật trừ tồn kho thành công", '#DCFCE7', '#16A34A', '#14532D')
    # From diamond right (10.2, 5.6) -> (12.4, 5.6) -> down to b_ok1 top (12.4, 4.6)
    ax.plot([10.2, 12.4, 12.4], [5.6, 5.6, 4.6], color='#16A34A', linewidth=1.5)
    ax.annotate('', xy=(12.4, 4.6), xytext=(12.4, 4.7), arrowprops=dict(arrowstyle="->", color='#16A34A', lw=1.5))

    b_ok2 = draw_activity_box(12.4, 2.7, 5.0, 0.8, "5A. INSERT TheKho (Loai='XUAT', TonSauGD)\n& COMMIT TRANSACTION (ACID)", '#DCFCE7', '#16A34A', '#14532D')
    draw_arrow(b_ok1['bottom'], b_ok2['top'], '#16A34A')

    # End Node (Clear and fully within view at y = 1.3)
    end_box = draw_activity_box(8.0, 1.3, 3.6, 0.65, "6. Cập nhật giao diện & Kết thúc", '#F1F5F9', '#475569')

    # Orthogonal connect into End Box
    ax.plot([3.6, 3.6, 6.2], [2.3, 1.3, 1.3], color='#DC2626', linewidth=1.5)
    ax.annotate('', xy=(6.2, 1.3), xytext=(6.1, 1.3), arrowprops=dict(arrowstyle="->", color='#DC2626', lw=1.5))

    ax.plot([12.4, 12.4, 9.8], [2.3, 1.3, 1.3], color='#16A34A', linewidth=1.5)
    ax.annotate('', xy=(9.8, 1.3), xytext=(9.9, 1.3), arrowprops=dict(arrowstyle="->", color='#16A34A', lw=1.5))

    # Bullseye End symbol inside/beside
    circle_out = Circle((8.0, 0.45), 0.24, color='#0F172A', fill=False, linewidth=2.0)
    circle_in = Circle((8.0, 0.45), 0.15, color='#0F172A', fill=True)
    ax.add_patch(circle_out)
    ax.add_patch(circle_in)
    draw_arrow(end_box['bottom'], (8.0, 0.7))
    ax.text(8.0, 0.12, "Kết thúc nghiệp vụ xuất kho", ha='center', va='center', fontsize=7.5, style='italic', color='#64748B')

    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[OK] Saved Hình 4.4.1 to {out_path}")


# ==============================================================================
# 13. HÌNH 4.4.2: BIỂU ĐỒ HOẠT ĐỘNG TRỢ LÝ AI & DATA SANITIZER (image15.png)
# ĐÃ SỬA LỖI TỌA ĐỘ ÂM (Y < 0), ĐẦY ĐỦ 100% NODE KHÔNG BỊ CẮT
# ==============================================================================
def draw_activity_ai_sanitizer(out_path):
    fig, ax = plt.subplots(figsize=(16, 12), dpi=300)
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 12)
    ax.axis('off')
    fig.patch.set_facecolor('#F8FAFC')
    ax.set_facecolor('#F8FAFC')

    ax.text(8.0, 11.5, "BIỂU ĐỒ HOẠT ĐỘNG (ACTIVITY DIAGRAM): TRỢ LÝ AI & DATA SANITIZER",
            ha='center', va='center', fontsize=13.0, fontweight='bold', color='#0F172A')

    # Start Node
    circle_start = Circle((8.0, 10.8), 0.22, color='#0F172A', fill=True)
    ax.add_patch(circle_start)

    def draw_activity_box(x, y, w, h, text, bg='#FAF5FF', border='#7C3AED', text_col='#0F172A'):
        box = FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.08,rounding_size=0.15",
                             facecolor=bg, edgecolor=border, linewidth=1.5)
        ax.add_patch(box)
        ax.text(x, y, text, ha='center', va='center', fontsize=8.2, fontweight='bold', color=text_col)
        return {
            'top': (x, y + h / 2),
            'bottom': (x, y - h / 2),
            'left': (x - w / 2, y),
            'right': (x + w / 2, y)
        }

    def draw_arrow(p1, p2, col='#7C3AED'):
        ax.annotate('', xy=p2, xytext=p1,
                    arrowprops=dict(arrowstyle="->", color=col, lw=1.5))

    # Sequential steps
    b1 = draw_activity_box(8.0, 9.8, 7.2, 0.75, "1. Người dùng yêu cầu Sinh Báo cáo Nhập-Xuất-Tồn / Khuyến nghị kho", '#FAF5FF', '#7C3AED')
    draw_arrow((8.0, 10.58), b1['top'])

    b2 = draw_activity_box(8.0, 8.6, 7.2, 0.75, "2. Backend truy vấn DataSet kho 30 ngày từ MySQL 8.0 (Xuất, Nhập, Tồn)", '#EFF6FF', '#2563EB')
    draw_arrow(b1['bottom'], b2['top'])

    b3 = draw_activity_box(8.0, 7.4, 7.2, 0.75, "3. Data Sanitizer loại bỏ triệt để DonGiaNhap & Giá vốn (Bảo mật tuyệt đối)", '#FEE2E2', '#DC2626', '#991B1B')
    draw_arrow(b2['bottom'], b3['top'])

    b4 = draw_activity_box(8.0, 6.2, 7.2, 0.75, "4. Đóng gói Grounded Prompt Template + Dữ liệu sạch + Chỉ dẫn phân tích", '#FAF5FF', '#7C3AED')
    draw_arrow(b3['bottom'], b4['top'])

    b5 = draw_activity_box(8.0, 5.0, 7.2, 0.75, "5. Gửi HTTPS Request tới Google Gemini API (Model: Gemini 1.5 Flash)", '#FAF5FF', '#7C3AED')
    draw_arrow(b4['bottom'], b5['top'])

    # Decision Diamond
    diamond = Polygon([[8.0, 4.1], [10.2, 3.4], [8.0, 2.7], [5.8, 3.4]],
                      closed=True, facecolor='#FEF3C7', edgecolor='#D97706', linewidth=1.8)
    ax.add_patch(diamond)
    ax.text(8.0, 3.4, "Kết nối Gemini API\nthành công?\n(Timeout < 8s)", ha='center', va='center',
            fontsize=8.0, fontweight='bold', color='#92400E')
    draw_arrow(b5['bottom'], (8.0, 4.1))

    # Branch Left: Lỗi / Timeout -> Fallback (Orthogonal)
    ax.text(4.1, 3.65, "[MẤT MẠNG / TIMEOUT]", fontsize=7.8, fontweight='bold', color='#DC2626')
    b_err = draw_activity_box(3.6, 2.0, 4.8, 0.8, "6B. Kích hoạt Fallback SQL Engine\n(Sinh báo cáo thống kê thuần túy)", '#FEE2E2', '#DC2626', '#991B1B')
    ax.plot([5.8, 3.6, 3.6], [3.4, 3.4, 2.4], color='#DC2626', linewidth=1.5)
    ax.annotate('', xy=(3.6, 2.4), xytext=(3.6, 2.5), arrowprops=dict(arrowstyle="->", color='#DC2626', lw=1.5))

    # Branch Right: Thành công -> AI Report (Orthogonal)
    ax.text(11.4, 3.65, "[THÀNH CÔNG]", fontsize=7.8, fontweight='bold', color='#16A34A')
    b_ok = draw_activity_box(12.4, 2.0, 4.8, 0.8, "6A. Nhận Markdown Báo cáo AI 3 phần\n& Render lên giao diện Dashboard", '#DCFCE7', '#16A34A', '#14532D')
    ax.plot([10.2, 12.4, 12.4], [3.4, 3.4, 2.4], color='#16A34A', linewidth=1.5)
    ax.annotate('', xy=(12.4, 2.4), xytext=(12.4, 2.5), arrowprops=dict(arrowstyle="->", color='#16A34A', lw=1.5))

    # End Node (At positive coordinate y = 1.0, fully visible!)
    end_box = draw_activity_box(8.0, 1.0, 4.0, 0.65, "7. Hiển thị kết quả & Hỗ trợ Xuất Excel/PDF", '#F1F5F9', '#475569')

    # Orthogonal connect into End Box
    ax.plot([3.6, 3.6, 6.0], [1.6, 1.0, 1.0], color='#DC2626', linewidth=1.5)
    ax.annotate('', xy=(6.0, 1.0), xytext=(5.9, 1.0), arrowprops=dict(arrowstyle="->", color='#DC2626', lw=1.5))

    ax.plot([12.4, 12.4, 10.0], [1.6, 1.0, 1.0], color='#16A34A', linewidth=1.5)
    ax.annotate('', xy=(10.0, 1.0), xytext=(10.1, 1.0), arrowprops=dict(arrowstyle="->", color='#16A34A', lw=1.5))

    circle_out = Circle((8.0, 0.35), 0.24, color='#0F172A', fill=False, linewidth=2.0)
    circle_in = Circle((8.0, 0.35), 0.15, color='#0F172A', fill=True)
    ax.add_patch(circle_out)
    ax.add_patch(circle_in)
    draw_arrow(end_box['bottom'], (8.0, 0.6))
    ax.text(8.0, 0.05, "Hoàn tất quy trình phân tích AI", ha='center', va='center', fontsize=7.5, style='italic', color='#64748B')

    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[OK] Saved Hình 4.4.2 to {out_path}")


# ==============================================================================
# 14. HÌNH 4.5.1: BIỂU ĐỒ LỚP BACKEND (image16.png)
# ĐÃ BỔ SUNG TOÀN BỘ CÁC ĐƯỜNG NỐI QUAN HỆ UML GIỮA CONTROLLERS - SERVICES - MODELS
# ==============================================================================
def draw_class_diagram_backend(out_path):
    fig, ax = plt.subplots(figsize=(18, 13.5), dpi=300)
    ax.set_xlim(0, 18)
    ax.set_ylim(0, 13.5)
    ax.axis('off')
    fig.patch.set_facecolor('#F8FAFC')
    ax.set_facecolor('#F8FAFC')

    ax.text(9.0, 13.0, "BIỂU ĐỒ LỚP (CLASS DIAGRAM): KIẾN TRÚC BACKEND FASTAPI & DOMAIN SERVICES",
            ha='center', va='center', fontsize=14.0, fontweight='bold', color='#0F172A')

    classes = {}

    def draw_class_box(key, x, y, w, h, class_name, stereotype="", attrs=None, methods=None, header_bg='#1E293B'):
        attrs = attrs or []
        methods = methods or []
        header_h = 0.58
        h_box = FancyBboxPatch((x, y + h - header_h), w, header_h, boxstyle="round,pad=0.04,rounding_size=0.08",
                               facecolor=header_bg, edgecolor='#334155', linewidth=1.5)
        ax.add_patch(h_box)
        if stereotype:
            ax.text(x + w / 2, y + h - 0.20, f"<<{stereotype}>>", ha='center', va='center',
                    fontsize=7.0, color='#CBD5E1', style='italic')
            ax.text(x + w / 2, y + h - 0.42, class_name, ha='center', va='center',
                    fontsize=8.5, fontweight='bold', color='#FFFFFF')
        else:
            ax.text(x + w / 2, y + h - header_h / 2, class_name, ha='center', va='center',
                    fontsize=8.5, fontweight='bold', color='#FFFFFF')

        b_box = FancyBboxPatch((x, y), w, h - header_h, boxstyle="round,pad=0.04,rounding_size=0.08",
                               facecolor='#FFFFFF', edgecolor='#334155', linewidth=1.5)
        ax.add_patch(b_box)

        cur_y = y + h - header_h - 0.24
        for a in attrs:
            ax.text(x + 0.12, cur_y, a, fontsize=7.0, color='#1E293B')
            cur_y -= 0.22

        if attrs and methods:
            ax.plot([x, x + w], [cur_y + 0.1, cur_y + 0.1], color='#CBD5E1', linewidth=1.0)
            cur_y -= 0.14

        for m in methods:
            ax.text(x + 0.12, cur_y, m, fontsize=7.0, color='#2563EB')
            cur_y -= 0.22

        classes[key] = {
            'x': x, 'y': y, 'w': w, 'h': h,
            'top': (x + w / 2, y + h),
            'bottom': (x + w / 2, y),
            'left': (x, y + h / 2),
            'right': (x + w, y + h / 2)
        }

    # ==========================================
    # TẦNG 1: API CONTROLLERS / ROUTERS (y: 9.6 - 12.4)
    # ==========================================
    draw_class_box('inv_router', 0.6, 9.6, 3.8, 2.7, "InventoryRouter", "API Controller", [
        "- prefix: str = '/api/v1/kho'",
        "- auth_service: AuthService"
    ], [
        "+ api_tao_phieu_nhap(payload)",
        "+ api_tao_phieu_xuat(payload)",
        "+ api_get_the_kho(ma_hh)"
    ], '#1E40AF')

    draw_class_box('ai_router', 5.0, 9.6, 3.8, 2.7, "AIRouter", "API Controller", [
        "- prefix: str = '/api/v1/ai'",
        "- ai_service: AIService"
    ], [
        "+ api_get_ai_advisory()",
        "+ api_generate_ai_report()",
        "+ api_get_raw_context()"
    ], '#7C3AED')

    draw_class_box('rep_router', 9.4, 9.6, 3.8, 2.7, "ReportsRouter", "API Controller", [
        "- prefix: str = '/api/v1/reports'",
        "- inv_service: InventoryService"
    ], [
        "+ api_export_excel(db, user)",
        "+ api_export_suppliers()",
        "+ api_export_pdf_stub()"
    ], '#0D9488')

    draw_class_box('auth_router', 13.8, 9.6, 3.6, 2.7, "AuthRouter", "API Controller", [
        "- prefix: str = '/api/v1/auth'",
        "- sec_service: Security"
    ], [
        "+ api_login(credentials)",
        "+ api_register(user_in)",
        "+ api_get_me()"
    ], '#D97706')

    # ==========================================
    # TẦNG 2: DOMAIN SERVICES (y: 5.2 - 8.4)
    # ==========================================
    draw_class_box('inbound_svc', 0.6, 5.2, 4.0, 3.1, "InboundService", "Domain Service (ACID)", [
        "- db: Session"
    ], [
        "+ execute_inbound_tx(phieu_in)",
        "+ update_stock_increase(ma_hh, qty)",
        "+ append_the_kho(ma_hh, 'NHAP')",
        "+ notify_websocket(event)"
    ], '#16A34A')

    draw_class_box('outbound_svc', 5.0, 5.2, 4.2, 3.1, "OutboundService", "Domain Service (ACID)", [
        "- db: Session"
    ], [
        "+ execute_outbound_tx(phieu_in)",
        "+ atomic_sql_decrement(ma_hh, qty)",
        "+ validate_zero_stock(ma_hh, qty)",
        "+ append_the_kho(ma_hh, 'XUAT')"
    ], '#16A34A')

    draw_class_box('ai_svc', 9.6, 5.2, 4.2, 3.1, "AIService", "Domain Service (Gemini)", [
        "- api_key: str",
        "- sanitizer: DataSanitizer"
    ], [
        "+ aggregate_warehouse_data_30d()",
        "+ sanitize_warehouse_data(data)",
        "+ generate_inventory_advisory()",
        "+ generate_full_ai_report()"
    ], '#7C3AED')

    draw_class_box('sec_svc', 14.2, 5.2, 3.2, 3.1, "SecurityService", "Core Security", [
        "- SECRET_KEY: str",
        "- ALGORITHM: str"
    ], [
        "+ hash_password(plain)",
        "+ verify_password(plain, hash)",
        "+ create_access_token(data)",
        "+ require_role(roles)"
    ], '#334155')

    # ==========================================
    # TẦNG 3: ORM MODELS & ENTITIES (y: 0.8 - 3.7)
    # ==========================================
    draw_class_box('item_model', 0.6, 0.8, 3.8, 2.9, "HangHoaModel", "SQLAlchemy ORM", [
        "+ MaHH: Column(String, PK)",
        "+ TenHH: Column(String)",
        "+ MaNhom: Column(String, FK)",
        "+ MaDVT: Column(String, FK)",
        "+ TonToiThieu: Column(Integer)"
    ], [], '#1E293B')

    draw_class_box('stock_model', 4.8, 0.8, 4.0, 2.9, "TonKhoModel", "SQLAlchemy ORM", [
        "+ MaHH: Column(String, PK, FK)",
        "+ SoLuongTon: Column(Integer)",
        "+ CheckConstraint('SoLuongTon >= 0')",
        "+ CapNhatCuoi: Column(DateTime)"
    ], [], '#1E293B')

    draw_class_box('card_model', 9.2, 0.8, 4.4, 2.9, "TheKhoModel", "SQLAlchemy ORM", [
        "+ MaGD: Column(Integer, PK)",
        "+ MaHH: Column(String, FK)",
        "+ MaChungTu: Column(String)",
        "+ LoaiGiaoDich: Column(String)",
        "+ SoLuongThayDoi: Column(Integer)",
        "+ TonSauGiaoDich: Column(Integer)"
    ], [], '#1E293B')

    draw_class_box('user_model', 14.0, 0.8, 3.4, 2.9, "NguoiDungModel", "SQLAlchemy ORM", [
        "+ MaND: Column(Integer, PK)",
        "+ TenDangNhap: Column(String)",
        "+ MatKhau: Column(String)",
        "+ VaiTro: Column(String)",
        "+ KichHoat: Column(Boolean)"
    ], [], '#1E293B')

    # ==========================================================================
    # VẼ CÁC ĐƯỜNG NỐI QUAN HỆ UML ĐẦY ĐỦ (DEPENDENCY & ASSOCIATION)
    # ==========================================================================
    def draw_uml_dependency(k1, k2, label="<<uses>>", col="#2563EB"):
        """Vẽ mũi tên phụ thuộc nét đứt ..> từ mép dưới k1 đến mép trên k2."""
        p1 = classes[k1]['bottom']
        p2 = classes[k2]['top']
        ax.annotate('', xy=p2, xytext=p1,
                    arrowprops=dict(arrowstyle="->", color=col, lw=1.5, linestyle="--"))
        mid_x = (p1[0] + p2[0]) / 2
        mid_y = (p1[1] + p2[1]) / 2
        ax.text(mid_x, mid_y, label, ha='center', va='center', fontsize=7.2, fontweight='bold', color=col,
                bbox=dict(boxstyle='round,pad=0.15', facecolor='#FFFFFF', edgecolor=col, linewidth=0.8, alpha=0.95))

    def draw_uml_assoc(k1, k2, label="<<manages>>", col="#16A34A"):
        """Vẽ mũi tên liên kết nét liền --> từ mép dưới k1 đến mép trên k2."""
        p1 = classes[k1]['bottom']
        p2 = classes[k2]['top']
        ax.annotate('', xy=p2, xytext=p1,
                    arrowprops=dict(arrowstyle="->", color=col, lw=1.5))
        mid_x = (p1[0] + p2[0]) / 2
        mid_y = (p1[1] + p2[1]) / 2
        ax.text(mid_x, mid_y, label, ha='center', va='center', fontsize=7.2, fontweight='bold', color=col,
                bbox=dict(boxstyle='round,pad=0.15', facecolor='#FFFFFF', edgecolor=col, linewidth=0.8, alpha=0.95))

    # 1. Routers -> Services
    draw_uml_dependency('inv_router', 'inbound_svc', "<<calls>>", "#1E40AF")
    draw_uml_dependency('inv_router', 'outbound_svc', "<<calls>>", "#1E40AF")
    draw_uml_dependency('ai_router', 'ai_svc', "<<calls>>", "#7C3AED")
    draw_uml_dependency('rep_router', 'outbound_svc', "<<queries>>", "#0D9488")
    draw_uml_dependency('auth_router', 'sec_svc', "<<authenticates>>", "#D97706")

    # 2. Services -> Models
    draw_uml_assoc('inbound_svc', 'item_model', "<<queries>>", "#16A34A")
    draw_uml_assoc('inbound_svc', 'stock_model', "<<updates>>", "#16A34A")
    draw_uml_assoc('outbound_svc', 'stock_model', "<<decrements>>", "#16A34A")
    draw_uml_assoc('outbound_svc', 'card_model', "<<appends>>", "#16A34A")
    draw_uml_assoc('ai_svc', 'card_model', "<<analyzes>>", "#7C3AED")
    draw_uml_assoc('sec_svc', 'user_model', "<<validates>>", "#334155")

    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[OK] Saved Hình 4.5.1 to {out_path}")


# ==============================================================================
# HÀM CHÍNH: SINH TOÀN BỘ 15 SƠ ĐỒ CHUẨN HÓA
# ==============================================================================
def generate_all():
    print("=== Đang sinh lại toàn bộ 15 sơ đồ kiến trúc SmartLogis AI chuẩn hóa (diagram-architect) ===")
    draw_scrum_workflow(os.path.join(OUTPUT_DIR, "image2.png"))
    draw_system_architecture(os.path.join(OUTPUT_DIR, "image3.png"))
    draw_usecase_general(os.path.join(OUTPUT_DIR, "image4.png"))
    draw_warehouse_usecase(os.path.join(OUTPUT_DIR, "image5.png"))
    draw_ai_usecase(os.path.join(OUTPUT_DIR, "image6.png"))
    draw_sequence_outbound(os.path.join(OUTPUT_DIR, "image7.png"))
    draw_seq_ai_report(os.path.join(OUTPUT_DIR, "image8.png"))
    draw_seq_inbound(os.path.join(OUTPUT_DIR, "image9.png"))
    draw_seq_the_kho_alert(os.path.join(OUTPUT_DIR, "image10.png"))
    draw_seq_export_report(os.path.join(OUTPUT_DIR, "image11.png"))
    draw_seq_jwt_auth(os.path.join(OUTPUT_DIR, "image12.png"))
    draw_database_erd(os.path.join(OUTPUT_DIR, "image13.png"))
    draw_activity_outbound(os.path.join(OUTPUT_DIR, "image14.png"))
    draw_activity_ai_sanitizer(os.path.join(OUTPUT_DIR, "image15.png"))
    draw_class_diagram_backend(os.path.join(OUTPUT_DIR, "image16.png"))
    print("=== Hoàn tất sinh toàn bộ 15 sơ đồ thành công! ===")


if __name__ == "__main__":
    generate_all()
