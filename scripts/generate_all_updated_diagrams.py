# scripts/generate_all_updated_diagrams.py
"""
Script Sinh Toàn Bộ 14 Sơ Đồ Kỹ Thuật Kiến Trúc Cho SmartLogis AI Chuẩn Hóa:
- Tác nhân 1: Quản trị viên (Admin)
- Tác nhân 2: Thủ kho kiêm Kế toán (Storekeeper & Accountant)
- Tác nhân bên ngoài: Trợ lý AI (Google Gemini 1.5 Flash API)
- Cơ sở dữ liệu: MySQL Server 8.0 (InnoDB ACID) & Dual-Database
"""

import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Circle

plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Segoe UI', 'Tahoma']
plt.rcParams['axes.unicode_minus'] = False

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "generated_diagrams")
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ==============================================================================
# 1. HÌNH 2.2.3: SƠ ĐỒ KIẾN TRÚC PHÂN HỆ CHỨC NĂNG (image3.png)
# ==============================================================================
def draw_system_architecture(out_path):
    fig, ax = plt.subplots(figsize=(15, 10), dpi=300)
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 10)
    ax.axis('off')
    fig.patch.set_facecolor('#F8FAFC')
    ax.set_facecolor('#F8FAFC')

    ax.text(7.5, 9.5, "KIẾN TRÚC PHÂN HỆ CHỨC NĂNG HỆ THỐNG QUẢN LÝ KHO TÍCH HỢP AI", 
            ha='center', va='center', fontsize=13, fontweight='bold', color='#0F172A')

    def draw_layer_box(x, y, w, h, title, bg='#FFFFFF', border='#3B82F6'):
        box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1,rounding_size=0.15",
                             facecolor=bg, edgecolor=border, linewidth=1.8)
        ax.add_patch(box)
        ax.text(x + 0.3, y + h - 0.35, title, ha='left', va='center', fontsize=9.5, fontweight='bold', color=border)

    def draw_component(x, y, w, h, title, desc="", fill='#F1F5F9', border='#64748B'):
        box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08,rounding_size=0.1",
                             facecolor=fill, edgecolor=border, linewidth=1.2)
        ax.add_patch(box)
        if desc:
            ax.text(x + w/2, y + h/2 + 0.15, title, ha='center', va='center', fontsize=8.5, fontweight='bold', color='#0F172A')
            ax.text(x + w/2, y + h/2 - 0.18, desc, ha='center', va='center', fontsize=7.0, color='#475569')
        else:
            ax.text(x + w/2, y + h/2, title, ha='center', va='center', fontsize=8.5, fontweight='bold', color='#0F172A')

    # Layer 1: Frontend Presentation
    draw_layer_box(0.5, 6.8, 14.0, 2.3, "1. TẦNG GIAO DIỆN NGƯỜI DÙNG (FRONTEND - JINJA2 SSR & WEBSOCKET REALTIME)", '#F0FDF4', '#16A34A')
    draw_component(0.8, 7.1, 2.8, 1.4, "Phân Hệ Xác Thực RBAC", "Đăng nhập, Phân quyền\nAdmin / Thủ kho kiêm Kế toán", '#DCFCE7', '#16A34A')
    draw_component(3.9, 7.1, 3.2, 1.4, "Quản Lý Danh Mục & Thẻ Kho", "CRUD Hàng hóa, NCC, DVT\nTra cứu biến động sổ thẻ kho", '#DCFCE7', '#16A34A')
    draw_component(7.4, 7.1, 3.2, 1.4, "Nghiệp Vụ Nhập / Xuất Kho", "Lập phiếu nhập & Lập phiếu xuất\nValidation giao diện, Chống tồn âm", '#DCFCE7', '#16A34A')
    draw_component(10.9, 7.1, 3.3, 1.4, "Dashboard & Trợ Lý AI / Báo Cáo", "Giao diện Báo cáo Nhập-Xuất-Tồn\nGợi ý nhập hàng & Xuất Excel/PDF", '#DCFCE7', '#16A34A')

    # Layer 2: Backend Application
    draw_layer_box(0.5, 3.6, 9.8, 2.8, "2. TẦNG XỬ LÝ NGHIỆP VỤ (BACKEND API - FASTAPI PYTHON)", '#EFF6FF', '#2563EB')
    draw_component(0.8, 3.9, 2.8, 2.0, "API Router & Auth", "JWT Authentication\nRBAC Guard: 2 Vai Trò\nSwagger / OpenAPI Docs", '#DBEAFE', '#2563EB')
    draw_component(3.9, 3.9, 3.2, 2.0, "Inventory Service (Core ACID)", "Xử lý Transaction Nhập/Xuất\nAtomic SQL Decrement\nKiểm tra chống tồn kho âm", '#DBEAFE', '#2563EB')
    draw_component(7.4, 3.9, 2.6, 2.0, "AI Aggregator & Sanitizer", "Tổng hợp số liệu xuất nhập tồn\nẨn DonGiaNhap bảo mật giá vốn\nGrounded Prompt Template", '#DBEAFE', '#2563EB')

    # External AI Cloud Layer
    draw_layer_box(10.6, 3.6, 3.9, 2.8, "DỊCH VỤ AI ĐÁM MÂY", '#FAF5FF', '#7C3AED')
    draw_component(10.9, 4.0, 3.3, 1.9, "Google Gemini API", "Mô hình Gemini 1.5 Flash\nSinh báo cáo 3 phần\nGợi ý nhập hàng & Bất thường", '#EDE9FE', '#7C3AED')

    # Layer 3: Database & Storage (MySQL 8.0)
    draw_layer_box(0.5, 0.5, 14.0, 2.7, "3. TẦNG CƠ SỞ DỮ LIỆU & LƯU TRỮ (DATABASE - MYSQL SERVER 8.0 INNODB ACID)", '#FFFBEB', '#D97706')
    draw_component(0.8, 0.8, 3.2, 1.9, "Danh Mục & Người Dùng", "Bảng: NguoiDung (2 vai trò),\nHangHoa, NhomHang, NCC", '#FEF3C7', '#D97706')
    draw_component(4.3, 0.8, 3.4, 1.9, "Tồn Kho & Ràng Buộc ACID", "Bảng: TonKho\nCHECK (SoLuongTon >= 0)\nAtomic SQL Decrement", '#FEF3C7', '#D97706')
    draw_component(8.0, 0.8, 3.1, 1.9, "Giao Dịch Nhập / Xuất", "Bảng: PhieuNhap, ChiTietPN,\nPhieuXuat, ChiTietPX", '#FEF3C7', '#D97706')
    draw_component(11.4, 0.8, 2.8, 1.9, "Nhật Ký Thẻ Kho", "Bảng: TheKho (Append-only)\nTruy vết biến động tồn lũy kế\nPhục vụ đối soát & AI", '#FEF3C7', '#D97706')

    # Connections between layers
    def draw_conn(x1, y1, x2, y2, color='#2563EB', text=""):
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="<->", color=color, lw=1.8))
        if text:
            ax.text((x1+x2)/2 + 0.2, (y1+y2)/2, text, ha='left', va='center', fontsize=7.5, color=color, fontweight='bold')

    draw_conn(5.4, 6.8, 5.4, 6.4, '#16A34A', 'HTTP REST / WebSocket')
    draw_conn(10.0, 4.9, 10.9, 4.9, '#7C3AED', 'Grounded Prompt / HTTPS')
    draw_conn(5.4, 3.6, 5.4, 3.2, '#D97706', 'SQLAlchemy / MySQL Pool')

    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[OK] Saved Hình 2.2.3 to {out_path}")


# ==============================================================================
# 2. HÌNH 4.1: BIỂU ĐỒ USE CASE TỔNG QUÁT (image4.png)
# ==============================================================================
def draw_usecase_general(out_path):
    fig, ax = plt.subplots(figsize=(16, 12), dpi=300)
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 12)
    ax.axis('off')
    fig.patch.set_facecolor('#F8FAFC')
    ax.set_facecolor('#F8FAFC')

    sys_box = FancyBboxPatch(
        (3.4, 0.4), 9.2, 11.2,
        boxstyle="round,pad=0.2,rounding_size=0.15",
        facecolor='#FFFFFF', edgecolor='#334155', linewidth=2.0, linestyle='-'
    )
    ax.add_patch(sys_box)

    ax.text(8.0, 11.2, "HỆ THỐNG QUẢN LÝ KHO THÔNG MINH SMARTLOGIS AI", 
            ha='center', va='center', fontsize=14, fontweight='bold', color='#1E293B')

    def draw_actor(x, y, name, role_desc, color='#2563EB'):
        circle = plt.Circle((x, y + 0.35), 0.22, color=color, fill=False, linewidth=2.2)
        ax.add_patch(circle)
        ax.plot([x, x], [y + 0.13, y - 0.35], color=color, linewidth=2.2)
        ax.plot([x - 0.28, x + 0.28], [y - 0.05, y - 0.05], color=color, linewidth=2.2)
        ax.plot([x, x - 0.22], [y - 0.35, y - 0.75], color=color, linewidth=2.2)
        ax.plot([x, x + 0.22], [y - 0.35, y - 0.75], color=color, linewidth=2.2)
        ax.text(x, y - 0.95, name, ha='center', va='top', fontsize=10.5, fontweight='bold', color='#0F172A')
        ax.text(x, y - 1.25, role_desc, ha='center', va='top', fontsize=8.0, color='#64748B', style='italic')

    # Draw 2 Human Actors on Left + 1 AI Actor on Right
    draw_actor(1.6, 9.2, "Quản Trị Viên\n(Admin)", "Toàn quyền hệ thống", '#1E40AF')
    draw_actor(1.6, 4.8, "Thủ Kho Kiêm\nKế Toán", "Vận hành kho & Đối soát", '#0D9488')
    draw_actor(14.4, 6.0, "Trợ Lý AI\n(Gemini 1.5)", "Phân tích & Khuyến nghị", '#7C3AED')

    def draw_usecase(x, y, text, subtext="", fillcolor='#EFF6FF', bordercolor='#3B82F6', width=2.6, height=0.72):
        box = FancyBboxPatch(
            (x - width/2, y - height/2), width, height,
            boxstyle="round,pad=0.1,rounding_size=0.35",
            facecolor=fillcolor, edgecolor=bordercolor, linewidth=1.5
        )
        ax.add_patch(box)
        if subtext:
            ax.text(x, y + 0.09, text, ha='center', va='center', fontsize=9.0, fontweight='bold', color='#1E293B')
            ax.text(x, y - 0.16, subtext, ha='center', va='center', fontsize=7.2, color='#64748B')
        else:
            ax.text(x, y, text, ha='center', va='center', fontsize=9.0, fontweight='bold', color='#1E293B')
        return (x, y)

    uc_nodes = {}
    uc_nodes['login'] = draw_usecase(5.8, 10.3, "Đăng nhập & Xác thực JWT", "US01 (Admin & Thủ kho kiêm KT)", '#F1F5F9', '#64748B', 2.8, 0.65)
    uc_nodes['user_mgmt'] = draw_usecase(10.2, 10.3, "Quản lý Người Dùng & Quyền", "Chỉ Admin quản trị", '#F1F5F9', '#64748B', 2.8, 0.65)
    uc_nodes['catalog'] = draw_usecase(8.0, 9.1, "Quản lý Danh Mục Kho", "Hàng hóa, Nhóm, DVT, NCC (US02)", '#FEF3C7', '#D97706', 3.2, 0.65)
    uc_nodes['inbound'] = draw_usecase(5.8, 7.9, "Lập Phiếu Nhập Kho", "Tăng tồn kho qua ACID (US03)", '#DCFCE7', '#16A34A', 2.8, 0.65)
    uc_nodes['outbound'] = draw_usecase(5.8, 6.6, "Lập Phiếu Xuất Kho", "Trừ tồn kho qua ACID (US04)", '#DCFCE7', '#16A34A', 2.8, 0.65)
    uc_nodes['check_stock'] = draw_usecase(9.8, 6.6, "Kiểm tra & Chống Tồn Âm", "CHECK (Ton >= 0) / Lock ACID", '#FEE2E2', '#DC2626', 2.8, 0.65)
    uc_nodes['card_update'] = draw_usecase(9.8, 7.9, "Ghi Sổ Thẻ Kho Tự Động", "Lưu lịch sử biến động lũy kế", '#F1F5F9', '#475569', 2.8, 0.65)
    uc_nodes['lookup'] = draw_usecase(5.8, 5.1, "Tra cứu Thẻ Kho Lịch Sử", "Truy vết biến động (US05)", '#E0E7FF', '#4F46E5', 2.8, 0.65)
    uc_nodes['alert'] = draw_usecase(10.2, 5.1, "Cảnh báo Tồn tối thiểu", "Cảnh báo TonKho <= TonMin", '#E0E7FF', '#4F46E5', 2.8, 0.65)
    uc_nodes['export'] = draw_usecase(8.0, 3.8, "Xuất Báo Cáo Excel Tồn Kho", "US08 (Biểu mẫu đối soát kho)", '#FEF3C7', '#D97706', 3.2, 0.65)
    uc_nodes['ai_advisory'] = draw_usecase(6.0, 2.5, "AI Khuyến Nghị Nhập Hàng", "Burn rate & Tồn min (US07)", '#EDE9FE', '#7C3AED', 2.8, 0.65)
    uc_nodes['ai_report'] = draw_usecase(6.0, 1.2, "AI Báo Cáo Chiến Lược", "Phân tích biến động 3 phần", '#EDE9FE', '#7C3AED', 2.8, 0.65)
    uc_nodes['ai_sanitize'] = draw_usecase(10.2, 1.8, "Khử Trùng Giá Vốn Nhập", "Data Sanitizer Bảo Mật", '#FEE2E2', '#B91C1C', 2.8, 0.65)

    def draw_assoc(p1, p2, color='#64748B'):
        ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=color, linewidth=1.2, zorder=1)

    def draw_include(from_uc, to_uc):
        ax.annotate('', xy=to_uc, xytext=from_uc,
                    arrowprops=dict(arrowstyle="->", color="#DC2626", lw=1.3, linestyle="--"), zorder=2)
        mid_x = (from_uc[0] + to_uc[0]) / 2
        mid_y = (from_uc[1] + to_uc[1]) / 2 + 0.15
        ax.text(mid_x, mid_y, "<<include>>", ha='center', va='center', fontsize=7.2, fontweight='bold', color='#DC2626',
                bbox=dict(boxstyle='square,pad=0.1', facecolor='#FFFFFF', edgecolor='none', alpha=0.9))

    # Admin connections
    admin_pos = (1.6, 9.2)
    for k in ['login', 'user_mgmt', 'catalog', 'inbound', 'outbound', 'lookup', 'export', 'ai_advisory', 'ai_report']:
        draw_assoc(admin_pos, uc_nodes[k], '#1E40AF')

    # Thukho kiem Ketoan connections
    thukho_pos = (1.6, 4.8)
    for k in ['login', 'catalog', 'inbound', 'outbound', 'lookup', 'export', 'ai_advisory', 'ai_report']:
        draw_assoc(thukho_pos, uc_nodes[k], '#0D9488')

    # AI connections
    ai_pos = (14.4, 6.0)
    for k in ['ai_advisory', 'ai_report', 'alert']:
        draw_assoc(ai_pos, uc_nodes[k], '#7C3AED')

    # Include relationships
    draw_include(uc_nodes['inbound'], uc_nodes['card_update'])
    draw_include(uc_nodes['outbound'], uc_nodes['check_stock'])
    draw_include(uc_nodes['outbound'], uc_nodes['card_update'])
    draw_include(uc_nodes['ai_report'], uc_nodes['ai_sanitize'])

    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[OK] Saved Hình 4.1 to {out_path}")


# ==============================================================================
# 3. HÌNH 4.1.1: BIỂU ĐỒ USE CASE PHÂN HỆ NGHIỆP VỤ KHO (image5.png)
# ==============================================================================
def draw_warehouse_usecase(out_path):
    fig, ax = plt.subplots(figsize=(14, 9), dpi=300)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 9)
    ax.axis('off')
    fig.patch.set_facecolor('#F8FAFC')
    ax.set_facecolor('#F8FAFC')

    sys_box = FancyBboxPatch(
        (3.2, 0.4), 8.0, 8.2,
        boxstyle="round,pad=0.2,rounding_size=0.15",
        facecolor='#FFFFFF', edgecolor='#0D9488', linewidth=2.0, linestyle='-'
    )
    ax.add_patch(sys_box)

    ax.text(7.2, 8.2, "PHÂN HỆ NGHIỆP VỤ KHO & CHỐNG TỒN ÂM (ACID)", 
            ha='center', va='center', fontsize=12.5, fontweight='bold', color='#0F766E')

    def draw_actor(x, y, name, role_desc, color='#0D9488'):
        circle = plt.Circle((x, y + 0.35), 0.22, color=color, fill=False, linewidth=2.2)
        ax.add_patch(circle)
        ax.plot([x, x], [y + 0.13, y - 0.35], color=color, linewidth=2.2)
        ax.plot([x - 0.28, x + 0.28], [y - 0.05, y - 0.05], color=color, linewidth=2.2)
        ax.plot([x, x - 0.22], [y - 0.35, y - 0.75], color=color, linewidth=2.2)
        ax.plot([x, x + 0.22], [y - 0.35, y - 0.75], color=color, linewidth=2.2)
        ax.text(x, y - 0.95, name, ha='center', va='top', fontsize=10.0, fontweight='bold', color='#0F172A')
        ax.text(x, y - 1.25, role_desc, ha='center', va='top', fontsize=8.0, color='#64748B', style='italic')

    draw_actor(1.5, 5.8, "Thủ Kho Kiêm\nKế Toán", "Vận hành kho & Đối soát", '#0D9488')
    draw_actor(1.5, 2.3, "Admin\n(Quản trị viên)", "Giám sát & Quản trị", '#1E40AF')

    def draw_usecase(x, y, text, subtext="", fillcolor='#EFF6FF', bordercolor='#3B82F6', width=2.7, height=0.72):
        box = FancyBboxPatch(
            (x - width/2, y - height/2), width, height,
            boxstyle="round,pad=0.1,rounding_size=0.35",
            facecolor=fillcolor, edgecolor=bordercolor, linewidth=1.5
        )
        ax.add_patch(box)
        if subtext:
            ax.text(x, y + 0.08, text, ha='center', va='center', fontsize=9.0, fontweight='bold', color='#1E293B')
            ax.text(x, y - 0.16, subtext, ha='center', va='center', fontsize=7.2, color='#64748B')
        else:
            ax.text(x, y, text, ha='center', va='center', fontsize=9.0, fontweight='bold', color='#1E293B')
        return (x, y)

    uc_nodes = {}
    uc_nodes['inbound'] = draw_usecase(5.2, 7.0, "Lập Phiếu Nhập Kho", "Inbound Transaction", '#DCFCE7', '#16A34A')
    uc_nodes['outbound'] = draw_usecase(5.2, 5.2, "Lập Phiếu Xuất Kho", "Outbound Transaction", '#DCFCE7', '#16A34A')
    uc_nodes['val_stock'] = draw_usecase(9.2, 5.2, "Thẩm Định Tồn Khả Dụng", "Chống âm tại Frontend", '#FEE2E2', '#DC2626')
    uc_nodes['pessimistic'] = draw_usecase(9.2, 3.7, "Khóa Atomic Decrement", "Update SQL chống Race Condition", '#FEE2E2', '#DC2626')
    uc_nodes['card_update'] = draw_usecase(9.2, 7.0, "Ghi Sổ Thẻ Kho Tự Động", "TheKho Append-only", '#F1F5F9', '#475569')
    uc_nodes['export_excel'] = draw_usecase(5.2, 2.2, "Xuất Báo Cáo Excel Tồn", "Tổng hợp Nhập - Xuất - Tồn", '#FEF3C7', '#D97706')

    def draw_assoc(p1, p2, color='#64748B'):
        ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=color, linewidth=1.2)

    def draw_include(from_uc, to_uc):
        ax.annotate('', xy=to_uc, xytext=from_uc,
                    arrowprops=dict(arrowstyle="->", color="#DC2626", lw=1.3, linestyle="--"))
        mid_x = (from_uc[0] + to_uc[0]) / 2
        mid_y = (from_uc[1] + to_uc[1]) / 2 + 0.15
        ax.text(mid_x, mid_y, "<<include>>", ha='center', va='center', fontsize=7.2, fontweight='bold', color='#DC2626',
                bbox=dict(boxstyle='square,pad=0.1', facecolor='#FFFFFF', edgecolor='none', alpha=0.9))

    # Connect Actors
    thukho_pos = (1.5, 5.8)
    for k in ['inbound', 'outbound', 'export_excel']:
        draw_assoc(thukho_pos, uc_nodes[k], '#0D9488')

    admin_pos = (1.5, 2.3)
    for k in ['inbound', 'outbound', 'export_excel']:
        draw_assoc(admin_pos, uc_nodes[k], '#1E40AF')

    # Includes
    draw_include(uc_nodes['inbound'], uc_nodes['card_update'])
    draw_include(uc_nodes['outbound'], uc_nodes['val_stock'])
    draw_include(uc_nodes['outbound'], uc_nodes['pessimistic'])
    draw_include(uc_nodes['outbound'], uc_nodes['card_update'])

    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[OK] Saved Hình 4.1.1 to {out_path}")


# ==============================================================================
# 4. HÌNH 4.1.2: BIỂU ĐỒ USE CASE PHÂN HỆ TRỢ LÝ AI (image6.png)
# ==============================================================================
def draw_ai_usecase(out_path):
    fig, ax = plt.subplots(figsize=(14, 9), dpi=300)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 9)
    ax.axis('off')
    fig.patch.set_facecolor('#F8FAFC')
    ax.set_facecolor('#F8FAFC')

    sys_box = FancyBboxPatch(
        (3.4, 0.4), 7.6, 8.2,
        boxstyle="round,pad=0.2,rounding_size=0.15",
        facecolor='#FFFFFF', edgecolor='#7C3AED', linewidth=2.0, linestyle='-'
    )
    ax.add_patch(sys_box)

    ax.text(7.2, 8.2, "PHÂN HỆ TRỢ LÝ AI (GOOGLE GEMINI 1.5 FLASH API)", 
            ha='center', va='center', fontsize=12.5, fontweight='bold', color='#6D28D9')

    def draw_actor(x, y, name, role_desc, color='#7C3AED'):
        circle = plt.Circle((x, y + 0.35), 0.22, color=color, fill=False, linewidth=2.2)
        ax.add_patch(circle)
        ax.plot([x, x], [y + 0.13, y - 0.35], color=color, linewidth=2.2)
        ax.plot([x - 0.28, x + 0.28], [y - 0.05, y - 0.05], color=color, linewidth=2.2)
        ax.plot([x, x - 0.22], [y - 0.35, y - 0.75], color=color, linewidth=2.2)
        ax.plot([x, x + 0.22], [y - 0.35, y - 0.75], color=color, linewidth=2.2)
        ax.text(x, y - 0.95, name, ha='center', va='top', fontsize=10.0, fontweight='bold', color='#0F172A')
        ax.text(x, y - 1.25, role_desc, ha='center', va='top', fontsize=8.0, color='#64748B', style='italic')

    draw_actor(1.5, 6.0, "Thủ Kho Kiêm\nKế Toán", "Vận hành & Theo dõi kho", '#0D9488')
    draw_actor(1.5, 2.5, "Admin\n(Quản trị viên)", "Giám sát & Quản trị", '#1E40AF')
    draw_actor(12.5, 4.5, "Google Gemini\n1.5 Flash API", "Mô hình LLM Phân tích", '#7C3AED')

    def draw_usecase(x, y, text, subtext="", fillcolor='#EDE9FE', bordercolor='#7C3AED', width=2.8, height=0.72):
        box = FancyBboxPatch(
            (x - width/2, y - height/2), width, height,
            boxstyle="round,pad=0.1,rounding_size=0.35",
            facecolor=fillcolor, edgecolor=bordercolor, linewidth=1.5
        )
        ax.add_patch(box)
        if subtext:
            ax.text(x, y + 0.08, text, ha='center', va='center', fontsize=9.0, fontweight='bold', color='#1E293B')
            ax.text(x, y - 0.16, subtext, ha='center', va='center', fontsize=7.2, color='#64748B')
        else:
            ax.text(x, y, text, ha='center', va='center', fontsize=9.0, fontweight='bold', color='#1E293B')
        return (x, y)

    uc_nodes = {}
    uc_nodes['advisory'] = draw_usecase(5.2, 6.5, "Xem Khuyến Nghị Dashboard", "Widget 3 khuyến nghị nhanh", '#EDE9FE', '#7C3AED')
    uc_nodes['report'] = draw_usecase(5.2, 4.2, "Sinh Báo Cáo Chiến Lược", "Phân tích 3 phần toàn diện", '#EDE9FE', '#7C3AED')
    uc_nodes['sanitizer'] = draw_usecase(9.0, 4.2, "Khử Trùng Giá Vốn Nhập", "Data Sanitizer bảo mật", '#FEE2E2', '#DC2626')
    uc_nodes['grounding'] = draw_usecase(9.0, 6.5, "Grounded Prompting", "Template bám sát số liệu", '#FEF3C7', '#D97706')
    uc_nodes['fallback'] = draw_usecase(5.2, 2.0, "Dự Phòng Offline Engine", "Local Rule-based Analyzer", '#F1F5F9', '#475569')

    def draw_assoc(p1, p2, color='#64748B'):
        ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=color, linewidth=1.2)

    def draw_include(from_uc, to_uc):
        ax.annotate('', xy=to_uc, xytext=from_uc,
                    arrowprops=dict(arrowstyle="->", color="#DC2626", lw=1.3, linestyle="--"))
        mid_x = (from_uc[0] + to_uc[0]) / 2
        mid_y = (from_uc[1] + to_uc[1]) / 2 + 0.15
        ax.text(mid_x, mid_y, "<<include>>", ha='center', va='center', fontsize=7.2, fontweight='bold', color='#DC2626',
                bbox=dict(boxstyle='square,pad=0.1', facecolor='#FFFFFF', edgecolor='none', alpha=0.9))

    def draw_extend(from_uc, to_uc):
        ax.annotate('', xy=to_uc, xytext=from_uc,
                    arrowprops=dict(arrowstyle="->", color="#475569", lw=1.3, linestyle="--"))
        mid_x = (from_uc[0] + to_uc[0]) / 2
        mid_y = (from_uc[1] + to_uc[1]) / 2 + 0.15
        ax.text(mid_x, mid_y, "<<extend>>", ha='center', va='center', fontsize=7.2, fontweight='bold', color='#475569',
                bbox=dict(boxstyle='square,pad=0.1', facecolor='#FFFFFF', edgecolor='none', alpha=0.9))

    # Connect Actors
    thukho_pos = (1.5, 6.0)
    draw_assoc(thukho_pos, uc_nodes['advisory'], '#0D9488')
    draw_assoc(thukho_pos, uc_nodes['report'], '#0D9488')

    admin_pos = (1.5, 2.5)
    draw_assoc(admin_pos, uc_nodes['advisory'], '#1E40AF')
    draw_assoc(admin_pos, uc_nodes['report'], '#1E40AF')

    gemini_pos = (12.5, 4.5)
    draw_assoc(gemini_pos, uc_nodes['grounding'], '#7C3AED')
    draw_assoc(gemini_pos, uc_nodes['report'], '#7C3AED')

    draw_include(uc_nodes['report'], uc_nodes['sanitizer'])
    draw_include(uc_nodes['report'], uc_nodes['grounding'])
    draw_extend(uc_nodes['fallback'], uc_nodes['report'])

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
            ax.plot([x1, x1+0.8, x1+0.8, x1], [y, y, y-0.3, y-0.3], color=col, linewidth=1.4)
            ax.annotate('', xy=(x1, y-0.3), xytext=(x1+0.1, y-0.3),
                        arrowprops=dict(arrowstyle="->", color=col, lw=1.4))
            ax.text(x1 + 0.9, y - 0.15, text, ha='left', va='center', fontsize=8.0, color='#0F172A', fontweight='bold')
        else:
            ax.annotate('', xy=(x2, y), xytext=(x1, y),
                        arrowprops=dict(arrowstyle="->", color=col, lw=1.4, linestyle=style))
            ax.text((x1+x2)/2, y + 0.15, text, ha='center', va='center', fontsize=8.0, color='#0F172A', fontweight='bold')

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
        ax.text((x1+x2)/2, y + 0.14, text, ha='center', va='center', fontsize=7.2, color='#0F172A', fontweight='bold')

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
        ax.text((x1+x2)/2, y + 0.14, text, ha='center', va='center', fontsize=7.5, color='#0F172A', fontweight='bold')

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
        ("Thủ Kho Kiêm Kế Toán (Actor)", 2.0, '#0D9488'),
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
        ax.text((x1+x2)/2, y + 0.14, text, ha='center', va='center', fontsize=7.5, color='#0F172A', fontweight='bold')

    draw_msg(7.8, 2.0, 5.6, "1. Mở Dashboard / Chọn màn hình 'Tra Cứu Thẻ Kho'")
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
        ax.text((x1+x2)/2, y + 0.14, text, ha='center', va='center', fontsize=7.5, color='#0F172A', fontweight='bold')

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
        ("Người Dùng (Admin/Thủ kho kiêm KT)", 2.0, '#1E40AF'),
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
        ax.text((x1+x2)/2, y + 0.14, text, ha='center', va='center', fontsize=7.5, color='#0F172A', fontweight='bold')

    draw_msg(7.8, 2.0, 5.8, "1. Nhập Tên đăng nhập và Mật khẩu (hoặc bấm nút Đăng nhập mẫu)")
    draw_msg(7.0, 5.8, 9.4, "2. POST /api/v1/auth/login (TenDangNhap, MatKhau)")
    draw_msg(6.2, 9.4, 13.2, "3. Query NguoiDung WHERE TenDangNhap = :username AND KichHoat = true")
    draw_msg(5.4, 13.2, 9.4, "4. Trả về thông tin NguoiDung kèm Bcrypt Hash", is_dashed=True)
    draw_msg(4.6, 9.4, 9.4, "5. verify_password(plain, hash) -> Khớp mật khẩu!")
    draw_msg(3.8, 9.4, 9.4, "6. create_access_token(payload: {sub, mand, vaitro, hoten})")
    draw_msg(3.0, 9.4, 5.8, "7. HTTP 200 OK + Set-Cookie: access_token=Bearer ... (HttpOnly, SameSite=Lax)", is_dashed=True)
    draw_msg(2.2, 5.8, 2.0, "8. Chuyển hướng người dùng vào /dashboard theo phân quyền 2 vai trò", is_dashed=True)

    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[OK] Saved Hình 4.2.6 to {out_path}")


# ==============================================================================
# 11. HÌNH 4.3.3: SƠ ĐỒ QUAN HỆ CƠ SỞ DỮ LIỆU CỤ THỂ (ERD - image13.png)
# ==============================================================================
def draw_database_erd(out_path):
    fig, ax = plt.subplots(figsize=(16, 12), dpi=300)
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 12)
    ax.axis('off')
    fig.patch.set_facecolor('#F8FAFC')
    ax.set_facecolor('#F8FAFC')

    ax.text(8.0, 11.4, "SƠ ĐỒ QUAN HỆ CƠ SỞ DỮ LIỆU MYSQL 8.0 (PHYSICAL ERD SCHEMA)", 
            ha='center', va='center', fontsize=13, fontweight='bold', color='#0F172A')

    def draw_table(x, y, w, h, name, fields, header_bg='#1E293B', body_bg='#FFFFFF'):
        header_h = 0.55
        h_box = FancyBboxPatch((x, y + h - header_h), w, header_h, boxstyle="round,pad=0.04,rounding_size=0.08",
                               facecolor=header_bg, edgecolor='#334155', linewidth=1.5)
        ax.add_patch(h_box)
        ax.text(x + w/2, y + h - header_h/2, name, ha='center', va='center', fontsize=9.0, fontweight='bold', color='#FFFFFF')

        b_box = FancyBboxPatch((x, y), w, h - header_h, boxstyle="round,pad=0.04,rounding_size=0.08",
                               facecolor=body_bg, edgecolor='#334155', linewidth=1.5)
        ax.add_patch(b_box)
        
        line_y = y + h - header_h - 0.28
        for f in fields:
            is_pk = "(PK)" in f
            is_fk = "(FK)" in f
            is_chk = "CHECK" in f
            col = '#B91C1C' if is_pk else ('#2563EB' if is_fk else ('#D97706' if is_chk else '#1E293B'))
            ax.text(x + 0.15, line_y, f, ha='left', va='center', fontsize=7.5, color=col, fontweight='bold' if (is_pk or is_chk) else 'normal')
            line_y -= 0.26

    # 1. NguoiDung (Updated to reflect 2 unified roles)
    draw_table(0.6, 8.5, 3.2, 2.2, "NguoiDung (Người dùng)", [
        "MaND (PK): INT AUTO_INCREMENT",
        "TenDangNhap: VARCHAR(50)",
        "MatKhau: VARCHAR(255)",
        "HoTen: VARCHAR(100)",
        "VaiTro: VARCHAR(20) [Admin/Thukho]",
        "NgayTao: TIMESTAMP"
    ], '#1E40AF', '#EFF6FF')

    # 2. NhomHang
    draw_table(0.6, 5.5, 3.0, 1.8, "NhomHang (Nhóm hàng)", [
        "MaNhom (PK): VARCHAR(20)",
        "TenNhom: VARCHAR(100)",
        "MoTa: TEXT"
    ], '#059669', '#F0FDF4')

    # 3. DonViTinh
    draw_table(0.6, 3.0, 3.0, 1.8, "DonViTinh (Đơn vị tính)", [
        "MaDVT (PK): VARCHAR(20)",
        "TenDVT: VARCHAR(50)",
        "MoTa: TEXT"
    ], '#059669', '#F0FDF4')

    # 4. NhaCungCap
    draw_table(0.6, 0.5, 3.2, 2.1, "NhaCungCap (Nhà cung cấp)", [
        "MaNCC (PK): VARCHAR(20)",
        "TenNCC: VARCHAR(255)",
        "DiaChi: VARCHAR(255)",
        "SoDienThoai: VARCHAR(20)",
        "Email: VARCHAR(100)"
    ], '#D97706', '#FFFBEB')

    # 5. HangHoa
    draw_table(4.6, 6.0, 3.2, 2.6, "HangHoa (Hàng hóa)", [
        "MaHH (PK): VARCHAR(20)",
        "TenHH: VARCHAR(255)",
        "MaNhom (FK): VARCHAR(20)",
        "MaDVT (FK): VARCHAR(20)",
        "TonToiThieu: INT DEFAULT 0",
        "MoTa: TEXT"
    ], '#059669', '#F0FDF4')

    # 6. TonKho
    draw_table(4.6, 2.8, 3.2, 2.1, "TonKho (Tồn kho thực tế)", [
        "MaHH (PK, FK): VARCHAR(20)",
        "SoLuongTon: INT CHECK (>= 0)",
        "CapNhatCuoi: TIMESTAMP"
    ], '#DC2626', '#FEF2F2')

    # 7. PhieuNhap
    draw_table(8.8, 8.5, 3.2, 2.2, "PhieuNhap (Phiếu nhập)", [
        "MaPN (PK): VARCHAR(30)",
        "NgayNhap: TIMESTAMP",
        "MaNCC (FK): VARCHAR(20)",
        "MaND (FK): INT",
        "TongTien: FLOAT DEFAULT 0",
        "GhiChu: TEXT"
    ], '#2563EB', '#EFF6FF')

    # 8. ChiTietPhieuNhap
    draw_table(8.8, 5.5, 3.2, 2.2, "ChiTietPhieuNhap (CT Nhập)", [
        "MaCTPN (PK): INT AUTO_INCREMENT",
        "MaPN (FK): VARCHAR(30)",
        "MaHH (FK): VARCHAR(20)",
        "SoLuongNhap: INT CHECK (> 0)",
        "DonGiaNhap: FLOAT CHECK (>= 0)",
        "ThanhTien: FLOAT"
    ], '#2563EB', '#EFF6FF')

    # 9. PhieuXuat
    draw_table(12.4, 8.5, 3.2, 2.2, "PhieuXuat (Phiếu xuất)", [
        "MaPX (PK): VARCHAR(30)",
        "NgayXuat: TIMESTAMP",
        "MaND (FK): INT",
        "NguoiNhan: VARCHAR(100)",
        "LyDoXuat: TEXT"
    ], '#7C3AED', '#FAF5FF')

    # 10. ChiTietPhieuXuat
    draw_table(12.4, 5.5, 3.2, 2.0, "ChiTietPhieuXuat (CT Xuất)", [
        "MaCTPX (PK): INT AUTO_INCREMENT",
        "MaPX (FK): VARCHAR(30)",
        "MaHH (FK): VARCHAR(20)",
        "SoLuongXuat: INT CHECK (> 0)"
    ], '#7C3AED', '#FAF5FF')

    # 11. TheKho
    draw_table(8.8, 1.2, 5.0, 2.7, "TheKho (Sổ thẻ kho lưu vết biến động)", [
        "MaGD (PK): INT AUTO_INCREMENT",
        "NgayGiaoDich: TIMESTAMP",
        "MaHH (FK): VARCHAR(20)",
        "MaChungTu: VARCHAR(30) [PN/PX]",
        "LoaiGiaoDich: VARCHAR(10) ['NHAP' / 'XUAT']",
        "SoLuongThayDoi: INT",
        "TonSauGiaoDich: INT CHECK (>= 0)"
    ], '#0D9488', '#F0FDFA')

    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[OK] Saved Hình 4.3.3 to {out_path}")


# ==============================================================================
# 12. HÌNH 4.4.1: BIỂU ĐỒ HOẠT ĐỘNG XUẤT KHO CHỐNG TỒN ÂM (image14.png)
# ==============================================================================
def draw_activity_outbound(out_path):
    fig, ax = plt.subplots(figsize=(15, 11), dpi=300)
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 11)
    ax.axis('off')
    fig.patch.set_facecolor('#F8FAFC')
    ax.set_facecolor('#F8FAFC')

    ax.text(7.5, 10.5, "BIỂU ĐỒ HOẠT ĐỘNG (ACTIVITY DIAGRAM): NGHIỆP VỤ XUẤT KHO CHỐNG TỒN ÂM", 
            ha='center', va='center', fontsize=12.5, fontweight='bold', color='#0F172A')

    # Start Node
    circle_start = plt.Circle((7.5, 9.7), 0.2, color='#0F172A', fill=True)
    ax.add_patch(circle_start)

    def draw_activity_box(x, y, w, h, text, bg='#EFF6FF', border='#2563EB', text_col='#0F172A'):
        box = FancyBboxPatch((x - w/2, y - h/2), w, h, boxstyle="round,pad=0.1,rounding_size=0.15",
                             facecolor=bg, edgecolor=border, linewidth=1.5)
        ax.add_patch(box)
        ax.text(x, y, text, ha='center', va='center', fontsize=8.5, fontweight='bold', color=text_col)

    def draw_arrow(x1, y1, x2, y2, col='#2563EB'):
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="->", color=col, lw=1.5))

    # Box 1
    draw_arrow(7.5, 9.5, 7.5, 8.9)
    draw_activity_box(7.5, 8.4, 6.0, 0.8, "1. Thủ kho kiêm Kế toán chọn Hàng hóa & Số lượng xuất", '#EFF6FF', '#2563EB')

    # Box 2
    draw_arrow(7.5, 8.0, 7.5, 7.4)
    draw_activity_box(7.5, 6.9, 6.4, 0.8, "2. Mở Transaction CSDL MySQL 8.0 & Khóa Atomic SQL Decrement", '#EFF6FF', '#2563EB')

    # Diamond Decision
    draw_arrow(7.5, 6.5, 7.5, 5.9)
    # Diamond patch
    diamond = patches.Polygon([[7.5, 5.9], [9.5, 5.1], [7.5, 4.3], [5.5, 5.1]], 
                              closed=True, facecolor='#FEF3C7', edgecolor='#D97706', linewidth=1.8)
    ax.add_patch(diamond)
    ax.text(7.5, 5.1, "Số lượng tồn >=\nSố lượng xuất?", ha='center', va='center', fontsize=8.5, fontweight='bold', color='#92400e')

    # Branch Left: Không đủ hàng (Error)
    ax.text(4.2, 5.3, "[KHÔNG ĐỦ HÀNG]", fontsize=8.0, fontweight='bold', color='#DC2626')
    draw_arrow(5.5, 5.1, 3.5, 3.9, '#DC2626')
    draw_activity_box(3.5, 3.4, 4.5, 0.8, "3B. Kích hoạt ROLLBACK TRANSACTION\n(Hủy bỏ mọi thay đổi)", '#FEE2E2', '#DC2626', '#991B1B')

    draw_arrow(3.5, 3.0, 3.5, 2.4, '#DC2626')
    draw_activity_box(3.5, 1.9, 4.5, 0.8, "4B. Báo lỗi: 'Chỉ còn tồn X, không đủ xuất Y'\n(Giữ nguyên tồn kho)", '#FEE2E2', '#DC2626', '#991B1B')

    # Branch Right: Đủ hàng (Success)
    ax.text(10.8, 5.3, "[ĐỦ HÀNG]", fontsize=8.0, fontweight='bold', color='#16A34A')
    draw_arrow(9.5, 5.1, 11.5, 4.0, '#16A34A')
    draw_activity_box(11.5, 3.5, 4.5, 0.8, "3A. Trừ tồn kho qua Transaction\n(SoLuongTon = SoLuongTon - Xuat)", '#DCFCE7', '#16A34A', '#14532D')

    draw_arrow(11.5, 3.1, 11.5, 2.5, '#16A34A')
    draw_activity_box(11.5, 2.0, 4.5, 0.8, "4A. Lưu PhieuXuat, ChiTietPX & Ghi TheKho", '#DCFCE7', '#16A34A', '#14532D')

    draw_arrow(11.5, 1.6, 11.5, 1.0, '#16A34A')
    draw_activity_box(11.5, 0.5, 4.5, 0.7, "5A. COMMIT TRANSACTION & Báo thành công", '#DCFCE7', '#16A34A', '#14532D')

    # End Node
    circle_out = plt.Circle((7.5, 0.5), 0.26, color='#0F172A', fill=False, linewidth=2.0)
    circle_in = plt.Circle((7.5, 0.5), 0.16, color='#0F172A', fill=True)
    ax.add_patch(circle_out)
    ax.add_patch(circle_in)
    ax.text(7.5, 0.1, "Kết thúc nghiệp vụ xuất kho", ha='center', va='center', fontsize=7.5, style='italic', color='#64748B')

    draw_arrow(3.5, 1.5, 7.2, 0.5, '#DC2626')
    draw_arrow(9.2, 0.5, 7.8, 0.5, '#16A34A')

    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[OK] Saved Hình 4.4.1 to {out_path}")


# ==============================================================================
# 13. HÌNH 4.4.2: BIỂU ĐỒ HOẠT ĐỘNG TRỢ LÝ AI & DATA SANITIZER (image15.png)
# ==============================================================================
def draw_activity_ai_sanitizer(out_path):
    fig, ax = plt.subplots(figsize=(15, 11), dpi=300)
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 11)
    ax.axis('off')
    fig.patch.set_facecolor('#F8FAFC')
    ax.set_facecolor('#F8FAFC')

    ax.text(7.5, 10.5, "BIỂU ĐỒ HOẠT ĐỘNG (ACTIVITY DIAGRAM): TRỢ LÝ AI & DATA SANITIZER", 
            ha='center', va='center', fontsize=12.5, fontweight='bold', color='#0F172A')

    # Start Node
    circle_start = plt.Circle((7.5, 9.7), 0.2, color='#0F172A', fill=True)
    ax.add_patch(circle_start)

    def draw_activity_box(x, y, w, h, text, bg='#FAF5FF', border='#7C3AED', text_col='#0F172A'):
        box = FancyBboxPatch((x - w/2, y - h/2), w, h, boxstyle="round,pad=0.1,rounding_size=0.15",
                             facecolor=bg, edgecolor=border, linewidth=1.5)
        ax.add_patch(box)
        ax.text(x, y, text, ha='center', va='center', fontsize=8.5, fontweight='bold', color=text_col)

    def draw_arrow(x1, y1, x2, y2, col='#7C3AED'):
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="->", color=col, lw=1.5))

    # Box 1
    draw_arrow(7.5, 9.5, 7.5, 9.0)
    draw_activity_box(7.5, 8.5, 6.2, 0.8, "1. Thủ kho kiêm Kế toán / Admin yêu cầu Sinh Báo cáo", '#FAF5FF', '#7C3AED')

    # Box 2
    draw_arrow(7.5, 8.1, 7.5, 7.6)
    draw_activity_box(7.5, 7.1, 6.2, 0.8, "2. Backend truy vấn DataSet kho 30 ngày từ MySQL 8.0", '#EFF6FF', '#2563EB')

    # Box 3
    draw_arrow(7.5, 6.7, 7.5, 6.2)
    draw_activity_box(7.5, 5.7, 6.2, 0.8, "3. Data Sanitizer loại bỏ DonGiaNhap (Bảo mật giá vốn)", '#FEE2E2', '#DC2626', '#991B1B')

    # Box 4
    draw_arrow(7.5, 5.3, 7.5, 4.8)
    draw_activity_box(7.5, 4.3, 6.2, 0.8, "4. Đóng gói Grounded Prompt Template + System Instruction", '#FAF5FF', '#7C3AED')

    # Box 5
    draw_arrow(7.5, 3.9, 7.5, 3.4)
    draw_activity_box(7.5, 2.9, 6.2, 0.8, "5. Gửi Request tới Google Gemini API (LLM Cloud)", '#FAF5FF', '#7C3AED')

    # Diamond Decision
    draw_arrow(7.5, 2.5, 7.5, 2.0)
    diamond = patches.Polygon([[7.5, 2.0], [9.5, 1.3], [7.5, 0.6], [5.5, 1.3]], 
                              closed=True, facecolor='#FEF3C7', edgecolor='#D97706', linewidth=1.8)
    ax.add_patch(diamond)
    ax.text(7.5, 1.3, "Kết nối Gemini API\nthành công?", ha='center', va='center', fontsize=8.0, fontweight='bold', color='#92400e')

    # Branch Left: Lỗi / Timeout
    ax.text(3.5, 1.5, "[MẤT KẾT NỐI / TIMEOUT]", fontsize=7.5, fontweight='bold', color='#DC2626')
    draw_arrow(5.5, 1.3, 3.8, 0.6, '#DC2626')
    draw_activity_box(2.8, -0.1, 4.4, 0.8, "6B. Kích hoạt Fallback SQL Engine\n(Sinh báo cáo thống kê thuần)", '#FEE2E2', '#DC2626', '#991B1B')

    # Branch Right: Thành công
    ax.text(11.2, 1.5, "[THÀNH CÔNG]", fontsize=7.5, fontweight='bold', color='#16A34A')
    draw_arrow(9.5, 1.3, 11.2, 0.6, '#16A34A')
    draw_activity_box(12.2, -0.1, 4.4, 0.8, "6A. Nhận Markdown Báo cáo AI\n& Render lên giao diện React", '#DCFCE7', '#16A34A', '#14532D')

    # End Node
    circle_out = plt.Circle((7.5, -0.1), 0.26, color='#0F172A', fill=False, linewidth=2.0)
    circle_in = plt.Circle((7.5, -0.1), 0.16, color='#0F172A', fill=True)
    ax.add_patch(circle_out)
    ax.add_patch(circle_in)

    draw_arrow(5.0, -0.1, 7.2, -0.1, '#DC2626')
    draw_arrow(10.0, -0.1, 7.8, -0.1, '#16A34A')

    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[OK] Saved Hình 4.4.2 to {out_path}")


# ==============================================================================
# 14. HÌNH 4.5.1: BIỂU ĐỒ LỚP BACKEND (image16.png)
# ==============================================================================
def draw_class_diagram_backend(out_path):
    fig, ax = plt.subplots(figsize=(16, 12), dpi=300)
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 12)
    ax.axis('off')
    fig.patch.set_facecolor('#F8FAFC')
    ax.set_facecolor('#F8FAFC')

    ax.text(8.0, 11.4, "BIỂU ĐỒ LỚP (CLASS DIAGRAM): KIẾN TRÚC BACKEND FASTAPI & DOMAIN SERVICES", 
            ha='center', va='center', fontsize=13, fontweight='bold', color='#0F172A')

    def draw_class_box(x, y, w, h, class_name, stereotype="", attrs=None, methods=None, header_bg='#1E293B'):
        attrs = attrs or []
        methods = methods or []
        header_h = 0.6
        h_box = FancyBboxPatch((x, y + h - header_h), w, header_h, boxstyle="round,pad=0.04,rounding_size=0.08",
                               facecolor=header_bg, edgecolor='#334155', linewidth=1.5)
        ax.add_patch(h_box)
        if stereotype:
            ax.text(x + w/2, y + h - 0.2, f"<<{stereotype}>>", ha='center', va='center', fontsize=7.0, color='#94A3B8', style='italic')
            ax.text(x + w/2, y + h - 0.42, class_name, ha='center', va='center', fontsize=8.5, fontweight='bold', color='#FFFFFF')
        else:
            ax.text(x + w/2, y + h - header_h/2, class_name, ha='center', va='center', fontsize=8.5, fontweight='bold', color='#FFFFFF')

        b_box = FancyBboxPatch((x, y), w, h - header_h, boxstyle="round,pad=0.04,rounding_size=0.08",
                               facecolor='#FFFFFF', edgecolor='#334155', linewidth=1.5)
        ax.add_patch(b_box)

        cur_y = y + h - header_h - 0.25
        for a in attrs:
            ax.text(x + 0.12, cur_y, a, fontsize=7.2, color='#1E293B')
            cur_y -= 0.22

        if attrs and methods:
            ax.plot([x, x + w], [cur_y + 0.1, cur_y + 0.1], color='#CBD5E1', linewidth=1.0)
            cur_y -= 0.15

        for m in methods:
            ax.text(x + 0.12, cur_y, m, fontsize=7.2, color='#2563EB')
            cur_y -= 0.22

    # Controllers
    draw_class_box(0.5, 7.8, 3.4, 3.0, "InventoryRouter", "Controller / API", [
        "- prefix: str = '/api/v1/kho'",
        "- auth_service: AuthService"
    ], [
        "+ api_create_item(item_in)",
        "+ api_tao_phieu_nhap(phieu_in)",
        "+ api_tao_phieu_xuat(phieu_in)",
        "+ api_get_the_kho(ma_hh)"
    ], '#1E40AF')

    draw_class_box(4.2, 7.8, 3.4, 3.0, "AIRouter", "Controller / API", [
        "- prefix: str = '/api/v1/ai'",
        "- ai_service: AIService"
    ], [
        "+ api_get_ai_advisory()",
        "+ api_generate_ai_report()",
        "+ api_get_raw_context()"
    ], '#7C3AED')

    draw_class_box(7.9, 7.8, 3.4, 3.0, "ReportsRouter", "Controller / API", [
        "- prefix: str = '/api/v1/reports'",
        "- report_service: InventoryService"
    ], [
        "+ api_export_excel(db, user)",
        "+ api_export_suppliers_excel()",
        "+ api_export_pdf_stub()"
    ], '#0D9488')

    draw_class_box(11.6, 7.8, 3.8, 3.0, "AuthRouter", "Controller / API", [
        "- prefix: str = '/api/v1/auth'",
        "- sec_service: Security"
    ], [
        "+ api_login(credentials)",
        "+ api_register(user_in)",
        "+ api_get_me()",
        "+ api_logout()"
    ], '#D97706')

    # Core Domain Services
    draw_class_box(0.5, 3.8, 4.2, 3.2, "InboundService", "Domain Service (ACID)", [
        "- db: Session"
    ], [
        "+ execute_inbound_transaction(phieu_in, user_id)",
        "+ update_stock_increase(ma_hh, qty)",
        "+ append_the_kho(ma_hh, 'NHAP', qty)",
        "+ notify_websocket(event_type)"
    ], '#16A34A')

    draw_class_box(5.0, 3.8, 4.4, 3.2, "OutboundService", "Domain Service (ACID)", [
        "- db: Session"
    ], [
        "+ execute_outbound_transaction(phieu_in, user_id)",
        "+ atomic_sql_decrement(ma_hh, qty)",
        "+ validate_zero_negative_stock(ma_hh, qty)",
        "+ append_the_kho(ma_hh, 'XUAT', -qty)"
    ], '#16A34A')

    draw_class_box(9.7, 3.8, 5.7, 3.2, "AIService", "Domain Service (Gemini API)", [
        "- api_key: str",
        "- sanitizer: DataSanitizer"
    ], [
        "+ aggregate_warehouse_data_30d(db)",
        "+ sanitize_warehouse_data(data)",
        "+ generate_ai_inventory_advisory(db)",
        "+ generate_full_ai_report(db)"
    ], '#7C3AED')

    # Security & Models
    draw_class_box(2.0, 0.5, 5.5, 2.7, "SecurityService", "Core Security & RBAC", [
        "- SECRET_KEY: str",
        "- ALGORITHM: str = 'HS256'"
    ], [
        "+ get_password_hash(password: str) -> str",
        "+ verify_password(plain, hashed) -> bool",
        "+ create_access_token(payload: dict) -> str",
        "+ require_role(roles: List[str]) -> Callable"
    ], '#1E293B')

    draw_class_box(8.2, 0.5, 5.8, 2.7, "NguoiDungModel", "SQLAlchemy ORM Model", [
        "+ MaND: Column(Integer, PK)",
        "+ TenDangNhap: Column(String)",
        "+ MatKhau: Column(String)",
        "+ HoTen: Column(String)",
        "+ VaiTro: Column(String) ['Admin', 'Thukho']",
        "+ KichHoat: Column(Boolean)"
    ], [], '#1E293B')

    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[OK] Saved Hình 4.5.1 to {out_path}")


def generate_all():
    print("=== Generating All 14 High-Res Diagrams for SmartLogis AI (Unified Storekeeper & Accountant) ===")
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
    print("=== All 14 Diagrams Generated Successfully ===")


if __name__ == "__main__":
    generate_all()
