# scripts/generate_clean_diagrams.py
"""
Script Thiết Kế & Tạo Lại Toàn Bộ Sơ Đồ Kỹ Thuật Siêu Sạch Sẽ, Thoáng Mắt (Ultra Clean & Academic Theme)
Giải quyết triệt để vấn đề 'rối mắt', đan chéo dây:
- Bố cục lưới thoáng đãng, tuyệt đối không đan chéo dây.
- Nhãn rõ ràng, font chữ to đẹp, chuẩn in ấn luận văn/đồ án CNTT.
- ERD thiết kế theo cấu trúc Manhattan Orthogonal Routing chuẩn database schema.
"""

import os
import sys
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Circle

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Segoe UI', 'Tahoma']
plt.rcParams['axes.unicode_minus'] = False

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "generated_diagrams")
os.makedirs(OUTPUT_DIR, exist_ok=True)

CANVAS_BG = "#F8FAFC"
TEXT_DARK = "#0F172A"
TEXT_MUTED = "#475569"

ADMIN_COLOR = "#1E40AF"     # Deep Blue
KEEPER_COLOR = "#0F766E"    # Deep Teal
AI_COLOR = "#7E22CE"        # Royal Purple
ACID_RED = "#DC2626"        # Alert Red
GOLD_COLOR = "#D97706"      # Warm Amber


# ==============================================================================
# 1. HÌNH 2.2.3: SƠ ĐỒ KIẾN TRÚC PHÂN HỆ CHỨC NĂNG (image3.png)
# ==============================================================================
def draw_clean_architecture(out_path):
    fig, ax = plt.subplots(figsize=(16, 12), dpi=300)
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 12)
    ax.axis('off')
    fig.patch.set_facecolor(CANVAS_BG)
    ax.set_facecolor(CANVAS_BG)

    ax.text(8.0, 11.5, "KIẾN TRÚC PHÂN HỆ HỆ THỐNG QUẢN LÝ KHO TÍCH HỢP AI (SMARTLOGIS AI)", 
            ha='center', va='center', fontsize=14, fontweight='bold', color=TEXT_DARK)

    def draw_layer(x, y, w, h, title, fill, stroke):
        box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1,rounding_size=0.15",
                             facecolor=fill, edgecolor=stroke, linewidth=1.8)
        ax.add_patch(box)
        ax.text(x + 0.4, y + h - 0.32, title, ha='left', va='center', fontsize=9.5, fontweight='bold', color=stroke)

    def draw_comp(x, y, w, h, title, items, fill, stroke):
        box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08,rounding_size=0.1",
                             facecolor=fill, edgecolor=stroke, linewidth=1.2)
        ax.add_patch(box)
        ax.text(x + w/2, y + h - 0.32, title, ha='center', va='center', fontsize=8.8, fontweight='bold', color=TEXT_DARK)
        line_y = y + h - 0.62
        for it in items:
            ax.text(x + 0.18, line_y, f"• {it}", ha='left', va='center', fontsize=7.6, color=TEXT_MUTED)
            line_y -= 0.25

    # Layer 1: Frontend (Y: 7.7, H: 3.3)
    draw_layer(0.6, 7.7, 14.8, 3.3, "1. TẦNG GIAO DIỆN NGƯỜI DÙNG (FRONTEND - JINJA2 SSR & WEBSOCKET REALTIME)", "#F0FDF4", "#16A34A")
    draw_comp(0.9, 8.0, 3.4, 2.4, "Phân Hệ Xác Thực & Phân Quyền", 
              ["Đăng nhập Form bảo mật JWT", "Phân quyền 2 vai trò RBAC", "Quản lý phiên HttpOnly Cookie", "Bảo vệ CSRF / XSS Token"], "#DCFCE7", "#16A34A")
    draw_comp(4.6, 8.0, 3.4, 2.4, "Nghiệp Vụ Kho Vận Hành", 
              ["Lập Phiếu Nhập kho (Inbound)", "Lập Phiếu Xuất kho (Outbound)", "Chống xuất tồn âm Real-time", "Giao diện Master-Detail động"], "#DCFCE7", "#16A34A")
    draw_comp(8.3, 8.0, 3.4, 2.4, "Sổ Thẻ Kho & Danh Mục", 
              ["Tra cứu lịch sử thẻ kho lũy kế", "Quản lý SKU, Nhóm, ĐVT, NCC", "Dashboard cảnh báo Tồn Min", "Bộ lọc tìm kiếm đa tiêu chí"], "#DCFCE7", "#16A34A")
    draw_comp(12.0, 8.0, 3.1, 2.4, "Dashboard AI & Báo Cáo", 
              ["Khuyến nghị nhập hàng tối ưu", "Báo cáo chiến lược kho 3 phần", "Xuất file Excel / PDF 1-click", "Biểu đồ biến động trực quan"], "#DCFCE7", "#16A34A")

    # Layer 2: Backend (Y: 4.1, H: 3.2)
    draw_layer(0.6, 4.1, 10.8, 3.2, "2. TẦNG XỬ LÝ NGHIỆP VỤ (BACKEND APPLICATION - FASTAPI PYTHON)", "#EFF6FF", "#2563EB")
    draw_comp(0.9, 4.4, 3.2, 2.3, "API Router & Security Guard", 
              ["OAuth2 Password Bearer", "RoleGuard: Admin & Thủ kho kiêm KT", "Swagger UI & OpenAPI Docs", "Pydantic Schema Validation"], "#DBEAFE", "#2563EB")
    draw_comp(4.4, 4.4, 3.5, 2.3, "Inventory Service (Core ACID)", 
              ["Database Transaction (ACID)", "Atomic SQL Decrement tồn kho", "Ghi vết thẻ kho tự động", "Cơ chế Rollback an toàn"], "#DBEAFE", "#2563EB")
    draw_comp(8.2, 4.4, 2.9, 2.3, "AI Aggregator & Sanitizer", 
              ["Tổng hợp số liệu xuất nhập tồn", "Ẩn DonGiaNhap bảo mật giá vốn", "Grounded Prompt Engine", "Phân tích tốc độ tiêu thụ (Burn Rate)"], "#DBEAFE", "#2563EB")

    # Dịch vụ AI bên ngoài
    draw_layer(11.8, 4.1, 3.6, 3.2, "DỊCH VỤ AI BÊN NGOÀI", "#FAF5FF", "#7E22CE")
    draw_comp(12.1, 4.4, 3.0, 2.3, "Google Gemini API", 
              ["Model: Gemini 1.5 Flash", "Phân tích tồn & Burn Rate", "Zero-downtime Fallback SQL", "Tốc độ phản hồi < 1.2s", "Tạo khuyến nghị tự động"], "#EDE9FE", "#7E22CE")

    # Layer 3: Database (Y: 0.5, H: 3.2)
    draw_layer(0.6, 0.5, 14.8, 3.2, "3. TẦNG CƠ SỞ DỮ LIỆU & LƯU TRỮ (DATABASE - MYSQL SERVER 8.0 INNODB)", "#FFFBEB", "#D97706")
    draw_comp(0.9, 0.8, 3.4, 2.3, "Danh Mục & Người Dùng", 
              ["NguoiDung (Admin/Thukho_Ketoan)", "HangHoa, NhomHang, DonViTinh", "NhaCungCap (Đối tác cung ứng)", "Toàn vẹn quan hệ 1:N"], "#FEF3C7", "#D97706")
    draw_comp(4.6, 0.8, 3.4, 2.3, "Tồn Kho & Ràng Buộc Khóa", 
              ["TonKho (MaHH PK, FK)", "CHECK (SoLuongTon >= 0)", "Connection Pool (size=10, ping=True)", "Chống tranh chấp ghi Race Condition"], "#FEF3C7", "#D97706")
    draw_comp(8.3, 0.8, 3.4, 2.3, "Giao Dịch Nhập / Xuất Kho", 
              ["PhieuNhap & ChiTietPhieuNhap", "PhieuXuat & ChiTietPhieuXuat", "Toàn vẹn khóa ngoại Foreign Key", "Khóa hàng Master-Detail"], "#FEF3C7", "#D97706")
    draw_comp(12.0, 0.8, 3.1, 2.3, "Sổ Thẻ Kho Biến Động", 
              ["TheKho (Append-Only Audit Log)", "Lưu vết giao dịch NHAP/XUAT", "Truy vết số dư tồn lũy kế", "Hỗ trợ kiểm kê đối soát"], "#FEF3C7", "#D97706")

    def draw_conn(x1, y1, x2, y2, col, label):
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="<->", color=col, lw=1.8))
        ax.text((x1+x2)/2 + 0.15, (y1+y2)/2, label, ha='left', va='center', fontsize=8.2, fontweight='bold', color=col,
                bbox=dict(boxstyle='square,pad=0.08', facecolor='#FFFFFF', edgecolor='none'))

    draw_conn(6.0, 7.7, 6.0, 7.3, "#16A34A", "HTTP / REST API")
    draw_conn(11.4, 5.7, 11.8, 5.7, "#7E22CE", "HTTPS / JSON")
    draw_conn(6.0, 4.1, 6.0, 3.7, "#D97706", "SQLAlchemy ORM")

    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[OK] Đã xuất Hình 2.2.3 tại: {out_path}")


# ==============================================================================
# 2. HÌNH 4.1: BIỂU ĐỒ USE CASE TỔNG QUÁT SIÊU THOÁNG (image4.png)
# ==============================================================================
def draw_clean_usecase_general(out_path):
    fig, ax = plt.subplots(figsize=(16.5, 11.5), dpi=300)
    ax.set_xlim(0, 16.5)
    ax.set_ylim(0, 11.5)
    ax.axis('off')
    fig.patch.set_facecolor(CANVAS_BG)
    ax.set_facecolor(CANVAS_BG)

    ax.text(8.25, 11.0, "BIỂU ĐỒ USE CASE TỔNG QUÁT HỆ THỐNG SMARTLOGIS AI", 
            ha='center', va='center', fontsize=14, fontweight='bold', color=TEXT_DARK)

    # Khung ranh giới hệ thống (System Boundary)
    boundary = FancyBboxPatch((3.5, 0.6), 9.6, 10.0, boxstyle="round,pad=0.15,rounding_size=0.2",
                              facecolor="#FFFFFF", edgecolor="#334155", linewidth=2.0)
    ax.add_patch(boundary)
    ax.text(8.3, 10.25, "HỆ THỐNG QUẢN LÝ KHO THÔNG MINH (SMARTLOGIS AI)", 
            ha='center', va='center', fontsize=11, fontweight='bold', color="#1E293B")

    # Vẽ Actor hình người UML chuẩn
    def draw_uml_actor(x, y, title, role, color):
        c = plt.Circle((x, y + 0.38), 0.22, color=color, fill=True, alpha=0.15, linewidth=2.0)
        ax.add_patch(c)
        c_border = plt.Circle((x, y + 0.38), 0.22, color=color, fill=False, linewidth=2.0)
        ax.add_patch(c_border)
        ax.plot([x, x], [y + 0.16, y - 0.3], color=color, linewidth=2.2)
        ax.plot([x - 0.28, x + 0.28], [y - 0.05, y - 0.05], color=color, linewidth=2.2)
        ax.plot([x, x - 0.22], [y - 0.3, y - 0.7], color=color, linewidth=2.2)
        ax.plot([x, x + 0.22], [y - 0.3, y - 0.7], color=color, linewidth=2.2)
        ax.text(x, y - 0.92, title, ha='center', va='top', fontsize=9.5, fontweight='bold', color=color)
        ax.text(x, y - 1.25, role, ha='center', va='top', fontsize=7.5, color=TEXT_MUTED, style='italic')

    # Actors: Admin (trên trái), Thủ kho kiêm KT (dưới trái), Gemini AI (phải)
    draw_uml_actor(1.6, 8.4, "Quản Trị Viên\n(Admin)", "Nguyễn Thành Hưng\n(Lead Backend)", ADMIN_COLOR)
    draw_uml_actor(1.6, 3.6, "Thủ Kho Kiêm\nKế Toán", "Hoàng Tiến Đạt\n(Frontend & QA)", KEEPER_COLOR)
    draw_uml_actor(14.8, 6.8, "Trợ Lý AI\n(Gemini 1.5)", "Dịch vụ AI bên ngoài\n(Google Flash API)", AI_COLOR)

    # 4 Subsystems bố trí 2 cột x 2 hàng cực kỳ gọn gàng
    def draw_subsystem_box(x, y, w, h, title, bg, stroke):
        box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08,rounding_size=0.12",
                             facecolor=bg, edgecolor=stroke, linewidth=1.2, linestyle='--')
        ax.add_patch(box)
        ax.text(x + 0.2, y + h - 0.28, title, ha='left', va='center', fontsize=8.5, fontweight='bold', color=stroke)

    # Cột Trái (X: 3.8, W: 4.3):
    # Phân hệ 1 (Trên): Quản trị & Xác thực (Y: 6.8, H: 3.1)
    draw_subsystem_box(3.8, 6.8, 4.3, 3.1, "1. PHÂN HỆ QUẢN TRỊ & XÁC THỰC", "#F8FAFC", "#475569")
    # Phân hệ 2 (Dưới): Nghiệp vụ Kho (Y: 1.0, H: 5.4)
    draw_subsystem_box(3.8, 1.0, 4.3, 5.4, "2. PHÂN HỆ NGHIỆP VỤ KHO (ACID)", "#F0FDFA", KEEPER_COLOR)

    # Cột Phải (X: 8.5, W: 4.3):
    # Phân hệ 4 (Trên): Trợ lý AI (Y: 6.8, H: 3.1)
    draw_subsystem_box(8.5, 6.8, 4.3, 3.1, "4. PHÂN HỆ TRỢ LÝ AI GEMINI", "#FAF5FF", AI_COLOR)
    # Phân hệ 3 (Dưới): Thẻ kho & Báo cáo (Y: 1.0, H: 5.4)
    draw_subsystem_box(8.5, 1.0, 4.3, 5.4, "3. PHÂN HỆ THẺ KHO & ĐỐI SOÁT", "#FFFBEB", GOLD_COLOR)

    def draw_uc(x, y, code, text, fill="#FFFFFF", stroke="#334155", w=3.8, h=0.7):
        box = FancyBboxPatch((x - w/2, y - h/2), w, h, boxstyle="round,pad=0.08,rounding_size=0.35",
                             facecolor=fill, edgecolor=stroke, linewidth=1.3)
        ax.add_patch(box)
        ax.text(x, y, f"{code}: {text}", ha='center', va='center', fontsize=8.2, fontweight='bold', color=TEXT_DARK)
        return (x, y)

    # Use Cases Phân hệ 1
    uc_login = draw_uc(5.95, 8.9, "UC01", "Đăng nhập & Cấp JWT Token", "#F1F5F9", "#475569")
    uc_user = draw_uc(5.95, 7.6, "UC_Admin", "Quản lý Người dùng & Phân quyền", "#F1F5F9", "#475569")

    # Use Cases Phân hệ 2
    uc_cat = draw_uc(5.95, 5.3, "UC02", "Quản lý Danh mục (SKU, NCC, ĐVT)", "#DCFCE7", "#16A34A")
    uc_in = draw_uc(5.95, 3.8, "UC03", "Lập Phiếu Nhập Kho (Inbound ACID)", "#DCFCE7", "#16A34A")
    uc_out = draw_uc(5.95, 2.3, "UC04", "Lập Phiếu Xuất Kho (Chống tồn âm)", "#FEE2E2", ACID_RED)

    # Use Cases Phân hệ 4
    uc_ai_adv = draw_uc(10.65, 8.9, "UC07", "AI Gợi Ý Kế Hoạch Nhập Hàng", "#EDE9FE", AI_COLOR)
    uc_ai_rep = draw_uc(10.65, 7.6, "UC06", "AI Sinh Báo Cáo Chiến Lược Kho", "#EDE9FE", AI_COLOR)

    # Use Cases Phân hệ 3
    uc_card = draw_uc(10.65, 5.3, "UC05", "Tra cứu Sổ Thẻ Kho Lũy Kế", "#FEF3C7", GOLD_COLOR)
    uc_alert = draw_uc(10.65, 3.8, "UC_Alert", "Giám sát & Cảnh báo Tồn Min", "#FEF3C7", GOLD_COLOR)
    uc_exp = draw_uc(10.65, 2.3, "UC08", "Xuất Báo Cáo Excel / PDF", "#FEF3C7", GOLD_COLOR)

    # KẾT NỐI ACTOR (Hoàn toàn trực giao và thẳng hàng, không chéo nhau)
    # Admin kết nối Phân hệ 1 (UC01, UC_Admin)
    ax.annotate('', xy=(4.05, 8.9), xytext=(2.2, 8.6),
                arrowprops=dict(arrowstyle="-", color=ADMIN_COLOR, lw=1.4))
    ax.annotate('', xy=(4.05, 7.6), xytext=(2.2, 8.2),
                arrowprops=dict(arrowstyle="-", color=ADMIN_COLOR, lw=1.4))

    # Thủ kho kiêm Kế toán kết nối Phân hệ 2 (UC02, UC03, UC04)
    ax.annotate('', xy=(4.05, 5.3), xytext=(2.2, 4.2),
                arrowprops=dict(arrowstyle="-", color=KEEPER_COLOR, lw=1.4))
    ax.annotate('', xy=(4.05, 3.8), xytext=(2.2, 3.8),
                arrowprops=dict(arrowstyle="-", color=KEEPER_COLOR, lw=1.4))
    ax.annotate('', xy=(4.05, 2.3), xytext=(2.2, 3.4),
                arrowprops=dict(arrowstyle="-", color=KEEPER_COLOR, lw=1.4))

    # Gemini AI kết nối Phân hệ 4 (UC07, UC06)
    ax.annotate('', xy=(12.55, 8.9), xytext=(14.2, 7.4),
                arrowprops=dict(arrowstyle="->", color=AI_COLOR, lw=1.4))
    ax.annotate('', xy=(12.55, 7.6), xytext=(14.2, 7.0),
                arrowprops=dict(arrowstyle="->", color=AI_COLOR, lw=1.4))

    # Liên kết đối soát dữ liệu giữa Phân hệ 2 sang Phân hệ 3 (Thẳng hàng ngang giữa 2 cột)
    def draw_h_link(y, label):
        ax.annotate('', xy=(8.75, y), xytext=(7.85, y),
                    arrowprops=dict(arrowstyle="->", color=GOLD_COLOR, lw=1.3, linestyle="-"))
        ax.text(8.3, y + 0.16, label, ha='center', va='center', fontsize=7.0, color=GOLD_COLOR, fontweight='bold',
                bbox=dict(boxstyle='square,pad=0.06', facecolor='#FFFFFF', edgecolor='none'))

    draw_h_link(5.3, "Lưu vết")
    draw_h_link(3.8, "Cập nhật")
    draw_h_link(2.3, "Đối soát")

    # Liên kết dữ liệu từ Phân hệ 2/3 lên Phân hệ 4 (AI)
    ax.annotate('', xy=(10.65, 7.25), xytext=(10.65, 5.65),
                arrowprops=dict(arrowstyle="->", color=AI_COLOR, lw=1.3, linestyle="--"))
    ax.text(10.65, 6.45, "Số liệu kho sạch (Sanitized)", ha='center', va='center', fontsize=7.0, color=AI_COLOR, fontweight='bold',
            bbox=dict(boxstyle='square,pad=0.08', facecolor='#FFFFFF', edgecolor='none'))

    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[OK] Đã xuất Hình 4.1 siêu thoáng tại: {out_path}")


# ==============================================================================
# 3. SƠ ĐỒ CÂY PHÂN RÃ CHỨC NĂNG HỆ THỐNG (functional_decomposition.png)
# ==============================================================================
def draw_functional_decomposition(out_path):
    fig, ax = plt.subplots(figsize=(16, 11), dpi=300)
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 11)
    ax.axis('off')
    fig.patch.set_facecolor(CANVAS_BG)
    ax.set_facecolor(CANVAS_BG)

    ax.text(8.0, 10.4, "SƠ ĐỒ PHÂN RÃ CHỨC NĂNG HỆ THỐNG (FUNCTIONAL DECOMPOSITION DIAGRAM)", 
            ha='center', va='center', fontsize=14, fontweight='bold', color=TEXT_DARK)

    # ROOT
    root_box = FancyBboxPatch((4.5, 9.2), 7.0, 0.85, boxstyle="round,pad=0.1,rounding_size=0.15",
                              facecolor="#1E293B", edgecolor="#0F172A", linewidth=2.0)
    ax.add_patch(root_box)
    ax.text(8.0, 9.62, "HỆ THỐNG QUẢN LÝ KHO THÔNG MINH (SMARTLOGIS AI)", 
            ha='center', va='center', fontsize=11, fontweight='bold', color="#FFFFFF")

    # 4 Subsystems
    subsystems = [
        ("1. PHÂN HỆ QUẢN TRỊ & XÁC THỰC", 2.0, "#F8FAFC", "#475569", [
            ("Đăng nhập & Cấp JWT", "Bcrypt + HttpOnly Cookie"),
            ("Quản trị Người Dùng", "CRUD tài khoản & Phân quyền"),
            ("Kiểm soát Nhật ký", "Theo dõi truy cập hệ thống")
        ]),
        ("2. PHÂN HỆ NGHIỆP VỤ KHO (ACID)", 5.9, "#F0FDFA", KEEPER_COLOR, [
            ("Quản lý Danh Mục Kho", "SKU, Nhóm hàng, ĐVT, NCC"),
            ("Lập Phiếu Nhập Kho", "Inbound + Tăng tồn kho"),
            ("Lập Phiếu Xuất Kho", "Outbound + Check tồn âm")
        ]),
        ("3. PHÂN HỆ THẺ KHO & BÁO CÁO", 9.8, "#FFFBEB", GOLD_COLOR, [
            ("Tra cứu Sổ Thẻ Kho", "Truy vết biến động lũy kế"),
            ("Cảnh báo Tồn Min", "Dashboard SoLuongTon <= Min"),
            ("Xuất Báo Cáo Kho", "File Excel / PDF đối soát")
        ]),
        ("4. PHÂN HỆ TRỢ LÝ AI GEMINI", 13.7, "#FAF5FF", AI_COLOR, [
            ("AI Khuyến Nghị Nhập Hàng", "Phân tích Burn Rate tối ưu"),
            ("AI Sinh Báo Cáo Chiến Lược", "Tổng quan, Biến động, Đề xuất"),
            ("Data Sanitizer Bảo Mật", "Khử trùng & Ẩn đơn giá nhập")
        ])
    ]

    for title, center_x, bg_col, stroke_col, funcs in subsystems:
        box_w = 3.6
        box = FancyBboxPatch((center_x - box_w/2, 7.6), box_w, 0.75, boxstyle="round,pad=0.08,rounding_size=0.12",
                             facecolor=stroke_col, edgecolor=stroke_col, linewidth=1.5)
        ax.add_patch(box)
        ax.text(center_x, 7.97, title, ha='center', va='center', fontsize=8.2, fontweight='bold', color="#FFFFFF")

        ax.annotate('', xy=(center_x, 8.35), xytext=(8.0, 9.2),
                    arrowprops=dict(arrowstyle="-", color="#64748B", lw=1.4))

        curr_y = 6.4
        for f_title, f_desc in funcs:
            f_box = FancyBboxPatch((center_x - box_w/2, curr_y - 0.4), box_w, 0.85, boxstyle="round,pad=0.06,rounding_size=0.1",
                                   facecolor=bg_col, edgecolor=stroke_col, linewidth=1.2)
            ax.add_patch(f_box)
            ax.text(center_x, curr_y + 0.15, f_title, ha='center', va='center', fontsize=8.2, fontweight='bold', color=TEXT_DARK)
            ax.text(center_x, curr_y - 0.15, f_desc, ha='center', va='center', fontsize=7.0, color=TEXT_MUTED)

            ax.plot([center_x, center_x], [curr_y + 0.45, curr_y + 0.7], color=stroke_col, linewidth=1.2)
            curr_y -= 1.35

    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[OK] Đã xuất Sơ đồ Cây Phân Rã Chức Năng tại: {out_path}")


# ==============================================================================
# 4. HÌNH 4.1.1: USE CASE PHÂN HỆ NGHIỆP VỤ KHO (image5.png)
# ==============================================================================
def draw_clean_usecase_kho(out_path):
    fig, ax = plt.subplots(figsize=(16, 9.5), dpi=300)
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 9.5)
    ax.axis('off')
    fig.patch.set_facecolor(CANVAS_BG)
    ax.set_facecolor(CANVAS_BG)

    ax.text(8.0, 9.0, "PHÂN HỆ NGHIỆP VỤ KHO & CHỐNG TỒN ÂM (ACID TRANSACTION)", 
            ha='center', va='center', fontsize=13, fontweight='bold', color=TEXT_DARK)

    box = FancyBboxPatch((3.4, 0.5), 12.0, 8.1, boxstyle="round,pad=0.1,rounding_size=0.15",
                         facecolor="#FFFFFF", edgecolor=KEEPER_COLOR, linewidth=1.8)
    ax.add_patch(box)

    def draw_uml_actor(x, y, title, col):
        c = plt.Circle((x, y + 0.35), 0.22, color=col, fill=True, alpha=0.15, linewidth=2.0)
        ax.add_patch(c)
        c_border = plt.Circle((x, y + 0.35), 0.22, color=col, fill=False, linewidth=2.0)
        ax.add_patch(c_border)
        ax.plot([x, x], [y + 0.13, y - 0.3], color=col, linewidth=2.2)
        ax.plot([x - 0.25, x + 0.25], [y - 0.05, y - 0.05], color=col, linewidth=2.2)
        ax.plot([x, x - 0.2], [y - 0.3, y - 0.7], color=col, linewidth=2.2)
        ax.plot([x, x + 0.2], [y - 0.3, y - 0.7], color=col, linewidth=2.2)
        ax.text(x, y - 0.95, title, ha='center', va='top', fontsize=9.2, fontweight='bold', color=col)

    draw_uml_actor(1.6, 6.0, "Thủ Kho Kiêm\nKế Toán", KEEPER_COLOR)
    draw_uml_actor(1.6, 2.2, "Quản Trị Viên\n(Admin)", ADMIN_COLOR)

    def draw_uc(x, y, text, fill="#F0FDFA", stroke=KEEPER_COLOR, w=3.8, h=0.75):
        b = FancyBboxPatch((x - w/2, y - h/2), w, h, boxstyle="round,pad=0.08,rounding_size=0.32",
                           facecolor=fill, edgecolor=stroke, linewidth=1.3)
        ax.add_patch(b)
        ax.text(x, y, text, ha='center', va='center', fontsize=8.2, fontweight='bold', color=TEXT_DARK)
        return (x, y)

    # Cột 1: Nghiệp vụ chính (X: 5.8)
    uc_in = draw_uc(5.8, 7.3, "Lập Phiếu Nhập Kho\n(Inbound Master-Detail)", "#DCFCE7", "#16A34A")
    uc_out = draw_uc(5.8, 4.4, "Lập Phiếu Xuất Kho\n(Outbound Master-Detail)", "#DCFCE7", "#16A34A")
    uc_card = draw_uc(5.8, 1.6, "Tra Cứu Sổ Thẻ Kho\n& Cảnh Báo Tồn Min", "#FEF3C7", GOLD_COLOR)

    # Cột 2: Các bước kiểm soát kỹ thuật ACID (X: 12.0)
    uc_thekho_in = draw_uc(12.0, 7.3, "Ghi Sổ Thẻ Kho Khi Nhập\n(Tự động tăng tồn lũy kế)", "#FEF3C7", GOLD_COLOR, 4.6, 0.75)
    uc_check = draw_uc(12.0, 5.5, "Kiểm Tra Tồn & Khóa ACID\n(Atomic SQL Decrement)", "#FEE2E2", ACID_RED, 4.6, 0.75)
    uc_rollback = draw_uc(12.0, 4.2, "Rollback & Cảnh Báo Thiếu Hàng\n(Hủy giao dịch khi tồn < xuất)", "#FEE2E2", ACID_RED, 4.6, 0.75)
    uc_thekho_out = draw_uc(12.0, 2.9, "Ghi Sổ Thẻ Kho Khi Xuất\n(Tự động trừ tồn lũy kế)", "#FEF3C7", GOLD_COLOR, 4.6, 0.75)

    # Nối Actor sang Cột 1
    for uc in [uc_in, uc_out, uc_card]:
        ax.annotate('', xy=(uc[0] - 1.9, uc[1]), xytext=(2.3, 6.0),
                    arrowprops=dict(arrowstyle="-", color=KEEPER_COLOR, lw=1.4))
        ax.annotate('', xy=(uc[0] - 1.9, uc[1]), xytext=(2.3, 2.2),
                    arrowprops=dict(arrowstyle="-", color=ADMIN_COLOR, lw=1.2, linestyle=":"))

    # Include Lập Phiếu Nhập -> Ghi Thẻ Kho Khi Nhập (Thẳng hàng ngang hoàn toàn)
    ax.annotate('', xy=(9.7, 7.3), xytext=(7.7, 7.3),
                arrowprops=dict(arrowstyle="->", color=GOLD_COLOR, lw=1.3, linestyle="--"))
    ax.text(8.7, 7.55, "<<include>>", ha='center', va='center', fontsize=7.2, color=GOLD_COLOR, fontweight='bold',
            bbox=dict(boxstyle='square,pad=0.06', facecolor='#FFFFFF', edgecolor='none'))

    # Include Lập Phiếu Xuất -> Kiểm Tra Tồn & Khóa ACID
    ax.annotate('', xy=(9.7, 5.5), xytext=(7.7, 4.6),
                arrowprops=dict(arrowstyle="->", color=ACID_RED, lw=1.3, linestyle="--"))
    ax.text(8.7, 5.25, "<<include>>", ha='center', va='center', fontsize=7.2, color=ACID_RED, fontweight='bold',
            bbox=dict(boxstyle='square,pad=0.06', facecolor='#FFFFFF', edgecolor='none'))

    # Extend Lập Phiếu Xuất -> Rollback & Cảnh Báo Thiếu Hàng (Thẳng hàng ngang)
    ax.annotate('', xy=(9.7, 4.2), xytext=(7.7, 4.3),
                arrowprops=dict(arrowstyle="->", color=ACID_RED, lw=1.3, linestyle="--"))
    ax.text(8.7, 4.45, "<<extend>>", ha='center', va='center', fontsize=7.2, color=ACID_RED, fontweight='bold',
            bbox=dict(boxstyle='square,pad=0.06', facecolor='#FFFFFF', edgecolor='none'))

    # Include Lập Phiếu Xuất -> Ghi Thẻ Kho Khi Xuất
    ax.annotate('', xy=(9.7, 2.9), xytext=(7.7, 4.1),
                arrowprops=dict(arrowstyle="->", color=GOLD_COLOR, lw=1.3, linestyle="--"))
    ax.text(8.7, 3.35, "<<include>>", ha='center', va='center', fontsize=7.2, color=GOLD_COLOR, fontweight='bold',
            bbox=dict(boxstyle='square,pad=0.06', facecolor='#FFFFFF', edgecolor='none'))

    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[OK] Đã xuất Hình 4.1.1 tại: {out_path}")


# ==============================================================================
# 5. HÌNH 4.1.2: USE CASE PHÂN HỆ TRỢ LÝ AI (image6.png)
# ==============================================================================
def draw_clean_usecase_ai(out_path):
    fig, ax = plt.subplots(figsize=(16.5, 9.5), dpi=300)
    ax.set_xlim(0, 16.5)
    ax.set_ylim(0, 9.5)
    ax.axis('off')
    fig.patch.set_facecolor(CANVAS_BG)
    ax.set_facecolor(CANVAS_BG)

    ax.text(8.25, 9.0, "PHÂN HỆ TRỢ LÝ AI GEMINI & BẢO MẬT DỮ LIỆU KHO", 
            ha='center', va='center', fontsize=13, fontweight='bold', color=TEXT_DARK)

    box = FancyBboxPatch((3.4, 0.8), 10.0, 7.8, boxstyle="round,pad=0.1,rounding_size=0.15",
                         facecolor="#FFFFFF", edgecolor=AI_COLOR, linewidth=1.8)
    ax.add_patch(box)

    def draw_actor(x, y, title, col):
        c = plt.Circle((x, y + 0.35), 0.22, color=col, fill=True, alpha=0.15, linewidth=2.0)
        ax.add_patch(c)
        c_border = plt.Circle((x, y + 0.35), 0.22, color=col, fill=False, linewidth=2.0)
        ax.add_patch(c_border)
        ax.plot([x, x], [y + 0.13, y - 0.3], color=col, linewidth=2.2)
        ax.plot([x - 0.25, x + 0.25], [y - 0.05, y - 0.05], color=col, linewidth=2.2)
        ax.plot([x, x - 0.2], [y - 0.3, y - 0.7], color=col, linewidth=2.2)
        ax.plot([x, x + 0.2], [y - 0.3, y - 0.7], color=col, linewidth=2.2)
        ax.text(x, y - 0.95, title, ha='center', va='top', fontsize=9.2, fontweight='bold', color=col)

    draw_actor(1.6, 5.4, "Người Dùng\n(Admin / Thủ kho kiêm KT)", KEEPER_COLOR)
    draw_actor(15.0, 5.4, "Trợ Lý AI\n(Google Gemini)", AI_COLOR)

    def draw_uc(x, y, text, fill="#EDE9FE", stroke=AI_COLOR, w=4.2, h=0.85):
        b = FancyBboxPatch((x - w/2, y - h/2), w, h, boxstyle="round,pad=0.08,rounding_size=0.32",
                           facecolor=fill, edgecolor=stroke, linewidth=1.3)
        ax.add_patch(b)
        ax.text(x, y, text, ha='center', va='center', fontsize=8.0, fontweight='bold', color=TEXT_DARK)
        return (x, y)

    # Cột 1 (Trái): Use Cases người dùng tương tác (X: 5.8)
    uc_adv = draw_uc(5.8, 6.4, "UC07: AI Khuyến Nghị Nhập Hàng\n(Dựa trên Burn Rate tiêu thụ)", "#EDE9FE", AI_COLOR, 4.3, 0.9)
    uc_rep = draw_uc(5.8, 3.4, "UC06: AI Sinh Báo Cáo Chiến Lược\n(Tổng quan, Biến động, Kiến nghị)", "#EDE9FE", AI_COLOR, 4.3, 0.9)

    # Cột 2 (Phải): Các bước tiền xử lý & kiểm soát AI (X: 11.0)
    uc_san = draw_uc(11.0, 6.4, "<<include>> Data Sanitizer\n(Khử trùng & Ẩn đơn giá nhập DonGiaNhap)", "#FEE2E2", ACID_RED, 4.4, 0.9)
    uc_grd = draw_uc(11.0, 3.4, "<<include>> Grounded Prompting\n(Gắn chặt số liệu thực tế MySQL, chống ảo giác)", "#FEF3C7", GOLD_COLOR, 4.4, 0.9)

    # Người dùng kết nối Cột 1
    ax.annotate('', xy=(3.65, 6.4), xytext=(2.3, 5.7), arrowprops=dict(arrowstyle="-", color=KEEPER_COLOR, lw=1.4))
    ax.annotate('', xy=(3.65, 3.4), xytext=(2.3, 5.1), arrowprops=dict(arrowstyle="-", color=KEEPER_COLOR, lw=1.4))

    # UC07 include Data Sanitizer (Ngang trực tiếp)
    ax.annotate('', xy=(8.8, 6.4), xytext=(7.95, 6.4), arrowprops=dict(arrowstyle="->", color=ACID_RED, lw=1.3, linestyle="--"))
    ax.text(8.37, 6.65, "<<include>>", ha='center', va='center', fontsize=7.2, color=ACID_RED, fontweight='bold',
            bbox=dict(boxstyle='square,pad=0.06', facecolor='#FFFFFF', edgecolor='none'))

    # UC06 include Grounded Prompting (Ngang trực tiếp)
    ax.annotate('', xy=(8.8, 3.4), xytext=(7.95, 3.4), arrowprops=dict(arrowstyle="->", color=GOLD_COLOR, lw=1.3, linestyle="--"))
    ax.text(8.37, 3.65, "<<include>>", ha='center', va='center', fontsize=7.2, color=GOLD_COLOR, fontweight='bold',
            bbox=dict(boxstyle='square,pad=0.06', facecolor='#FFFFFF', edgecolor='none'))

    # Data Sanitizer chuyển dữ liệu sạch xuống Grounded Prompting
    ax.annotate('', xy=(11.0, 3.85), xytext=(11.0, 5.95), arrowprops=dict(arrowstyle="->", color=AI_COLOR, lw=1.3, linestyle="--"))
    ax.text(11.0, 4.9, "<<include>> Dữ liệu sạch", ha='center', va='center', fontsize=7.2, color=AI_COLOR, fontweight='bold',
            bbox=dict(boxstyle='square,pad=0.06', facecolor='#FFFFFF', edgecolor='none'))

    # Gemini API nhận Prompt từ Cột 2
    ax.annotate('', xy=(14.2, 5.6), xytext=(13.2, 6.4), arrowprops=dict(arrowstyle="->", color=AI_COLOR, lw=1.4))
    ax.annotate('', xy=(14.2, 5.2), xytext=(13.2, 3.4), arrowprops=dict(arrowstyle="->", color=AI_COLOR, lw=1.4))

    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[OK] Đã xuất Hình 4.1.2 tại: {out_path}")


# ==============================================================================
# 6. HÌNH 4.3.3: SƠ ĐỒ THỰC THỂ QUAN HỆ ERD MYSQL 8.0 (image13.png)
# ==============================================================================
def draw_clean_database_erd(out_path):
    fig, ax = plt.subplots(figsize=(17, 12), dpi=300)
    ax.set_xlim(0, 17)
    ax.set_ylim(0, 12)
    ax.axis('off')
    fig.patch.set_facecolor(CANVAS_BG)
    ax.set_facecolor(CANVAS_BG)

    ax.text(8.5, 11.5, "SƠ ĐỒ THỰC THỂ QUAN HỆ CƠ SỞ DỮ LIỆU MYSQL 8.0 (PHYSICAL ERD SCHEMA)", 
            ha='center', va='center', fontsize=14, fontweight='bold', color=TEXT_DARK)

    def draw_table_card(x, y, w, h, title, fields, header_bg, body_bg):
        header_h = 0.52
        h_box = FancyBboxPatch((x, y + h - header_h), w, header_h, boxstyle="round,pad=0.03,rounding_size=0.08",
                               facecolor=header_bg, edgecolor="#334155", linewidth=1.4)
        ax.add_patch(h_box)
        ax.text(x + w/2, y + h - header_h/2, title, ha='center', va='center', fontsize=8.6, fontweight='bold', color="#FFFFFF")

        b_box = FancyBboxPatch((x, y), w, h - header_h, boxstyle="round,pad=0.03,rounding_size=0.08",
                               facecolor=body_bg, edgecolor="#334155", linewidth=1.4)
        ax.add_patch(b_box)

        line_y = y + h - header_h - 0.26
        for f in fields:
            is_pk = "(PK)" in f
            is_fk = "(FK)" in f
            is_chk = "CHECK" in f
            col = "#B91C1C" if is_pk else ("#1D4ED8" if is_fk else ("#B45309" if is_chk else TEXT_DARK))
            weight = "bold" if (is_pk or is_chk) else "normal"
            ax.text(x + 0.12, line_y, f, ha='left', va='center', fontsize=7.4, color=col, fontweight=weight)
            line_y -= 0.24

    # CỘT 1: Master Data (X: 0.6)
    draw_table_card(0.6, 8.8, 3.2, 2.2, "NguoiDung (Người Dùng)", [
        "MaND (PK): INT AUTO_INCREMENT",
        "TenDangNhap: VARCHAR(50) UNIQUE",
        "MatKhau: VARCHAR(255) [Bcrypt]",
        "HoTen: VARCHAR(100)",
        "VaiTro: VARCHAR(20) [Admin/Thukho_KT]",
        "NgayTao: TIMESTAMP"
    ], "#1E40AF", "#EFF6FF")

    draw_table_card(0.6, 6.1, 3.2, 2.1, "NhaCungCap (Nhà Cung Cấp)", [
        "MaNCC (PK): VARCHAR(20)",
        "TenNCC: VARCHAR(255)",
        "DiaChi: VARCHAR(255)",
        "SoDienThoai: VARCHAR(20)",
        "Email: VARCHAR(100)"
    ], "#D97706", "#FFFBEB")

    draw_table_card(0.6, 3.6, 3.2, 1.9, "NhomHang (Nhóm Hàng)", [
        "MaNhom (PK): VARCHAR(20)",
        "TenNhom: VARCHAR(100)",
        "MoTa: TEXT"
    ], "#059669", "#F0FDF4")

    draw_table_card(0.6, 1.1, 3.2, 1.9, "DonViTinh (Đơn Vị Tính)", [
        "MaDVT (PK): VARCHAR(20)",
        "TenDVT: VARCHAR(50)",
        "MoTa: TEXT"
    ], "#059669", "#F0FDF4")

    # CỘT 2: Hàng Hóa & Tồn Kho (X: 4.6)
    draw_table_card(4.6, 6.1, 3.4, 2.6, "HangHoa (Danh Mục Vật Tư)", [
        "MaHH (PK): VARCHAR(20)",
        "TenHH: VARCHAR(255)",
        "MaNhom (FK): VARCHAR(20)",
        "MaDVT (FK): VARCHAR(20)",
        "TonToiThieu: INT DEFAULT 0",
        "MoTa: TEXT"
    ], "#059669", "#F0FDF4")

    draw_table_card(4.6, 2.6, 3.4, 2.2, "TonKho (Tồn Kho Thực Tế)", [
        "MaHH (PK, FK): VARCHAR(20)",
        "SoLuongTon: INT CHECK (>= 0)",
        "CapNhatCuoi: TIMESTAMP"
    ], "#DC2626", "#FEF2F2")

    # CỘT 3: Giao Dịch Nhập & Xuất (X: 8.8)
    draw_table_card(8.8, 8.8, 3.4, 2.2, "PhieuNhap (Phiếu Nhập Kho)", [
        "MaPN (PK): VARCHAR(30)",
        "NgayNhap: TIMESTAMP",
        "MaNCC (FK): VARCHAR(20)",
        "MaND (FK): INT",
        "TongTien: FLOAT DEFAULT 0",
        "GhiChu: TEXT"
    ], "#2563EB", "#EFF6FF")

    draw_table_card(8.8, 6.0, 3.4, 2.3, "ChiTietPhieuNhap (CT Nhập)", [
        "MaCTPN (PK): INT AUTO_INCREMENT",
        "MaPN (FK): VARCHAR(30)",
        "MaHH (FK): VARCHAR(20)",
        "SoLuongNhap: INT CHECK (> 0)",
        "DonGiaNhap: FLOAT CHECK (>= 0)",
        "ThanhTien: FLOAT"
    ], "#2563EB", "#EFF6FF")

    draw_table_card(8.8, 3.3, 3.4, 2.1, "PhieuXuat (Phiếu Xuất Kho)", [
        "MaPX (PK): VARCHAR(30)",
        "NgayXuat: TIMESTAMP",
        "MaND (FK): INT",
        "NguoiNhan: VARCHAR(100)",
        "LyDoXuat: TEXT"
    ], "#7C3AED", "#FAF5FF")

    draw_table_card(8.8, 0.7, 3.4, 2.1, "ChiTietPhieuXuat (CT Xuất)", [
        "MaCTPX (PK): INT AUTO_INCREMENT",
        "MaPX (FK): VARCHAR(30)",
        "MaHH (FK): VARCHAR(20)",
        "SoLuongXuat: INT CHECK (> 0)"
    ], "#7C3AED", "#FAF5FF")

    # CỘT 4: Sổ Thẻ Kho Audit Log (X: 13.0)
    draw_table_card(13.0, 3.8, 3.4, 2.8, "TheKho (Sổ Thẻ Kho Biến Động)", [
        "MaGD (PK): INT AUTO_INCREMENT",
        "NgayGiaoDich: TIMESTAMP",
        "MaHH (FK): VARCHAR(20)",
        "MaChungTu: VARCHAR(30) [PN/PX]",
        "LoaiGD: VARCHAR(10) [NHAP/XUAT]",
        "SoLuongThayDoi: INT",
        "TonSauGiaoDich: INT CHECK (>= 0)"
    ], "#0F766E", "#F0FDFA")

    # ĐƯỜNG KẾT NỐI FOREIGN KEY TRỰC GIAO (KHÔNG CHÉO QUA BẢNG KHÁC)
    def draw_ortho_line(points, label="", col="#64748B"):
        for i in range(len(points) - 1):
            is_last = (i == len(points) - 2)
            arrow = "->" if is_last else "-"
            ax.annotate('', xy=points[i+1], xytext=points[i],
                        arrowprops=dict(arrowstyle=arrow, color=col, lw=1.3, linestyle="-"))
        if label:
            mid = points[len(points)//2]
            ax.text(mid[0], mid[1] + 0.12, label, ha='center', va='center', fontsize=7.0, color=col, fontweight='bold',
                    bbox=dict(boxstyle='square,pad=0.08', facecolor='#FFFFFF', edgecolor='none'))

    # 1. NhomHang & DVT -> HangHoa (Đi ngang sang Cột 2)
    draw_ortho_line([(3.8, 4.5), (4.2, 4.5), (4.2, 6.8), (4.6, 6.8)], "N:1", "#059669")
    draw_ortho_line([(3.8, 2.0), (4.2, 2.0), (4.2, 6.4), (4.6, 6.4)], "N:1", "#059669")

    # 2. HangHoa -> TonKho (1:1 Thẳng đứng)
    draw_ortho_line([(6.3, 6.1), (6.3, 4.8)], "1:1", "#DC2626")

    # 3. PhieuNhap -> ChiTietPhieuNhap (1:N Thẳng đứng)
    draw_ortho_line([(10.5, 8.8), (10.5, 8.3)], "1:N", "#2563EB")

    # 4. PhieuXuat -> ChiTietPhieuXuat (1:N Thẳng đứng)
    draw_ortho_line([(10.5, 3.3), (10.5, 2.8)], "1:N", "#7C3AED")

    # 5. HangHoa -> ChiTietPhieuNhap (Ngang trực tiếp từ Cột 2 sang Cột 3)
    draw_ortho_line([(8.0, 7.2), (8.8, 7.2)], "1:N", "#2563EB")

    # 6. HangHoa -> ChiTietPhieuXuat (Đi qua khoảng trống giữa PhieuNhap và PhieuXuat)
    draw_ortho_line([(8.0, 6.2), (8.4, 6.2), (8.4, 1.8), (8.8, 1.8)], "1:N", "#7C3AED")

    # 7. ChiTietPhieuNhap & ChiTietPhieuXuat -> TheKho (Ngang sang Cột 4)
    draw_ortho_line([(12.2, 7.0), (12.6, 7.0), (12.6, 5.5), (13.0, 5.5)], "1:1", "#0F766E")
    draw_ortho_line([(12.2, 1.8), (12.6, 1.8), (12.6, 4.5), (13.0, 4.5)], "1:1", "#0F766E")

    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[OK] Đã xuất Hình 4.3.3 siêu sạch tại: {out_path}")


def main():
    print("=" * 80)
    print("   BẮT ĐẦU VẼ LẠI TOÀN BỘ SƠ ĐỒ CỐT LÕI THEO CHUẨN SIÊU THOÁNG MẮT")
    print("=" * 80)

    draw_clean_architecture(os.path.join(OUTPUT_DIR, "image3.png"))
    draw_clean_usecase_general(os.path.join(OUTPUT_DIR, "image4.png"))
    draw_functional_decomposition(os.path.join(OUTPUT_DIR, "functional_decomposition.png"))
    draw_clean_usecase_kho(os.path.join(OUTPUT_DIR, "image5.png"))
    draw_clean_usecase_ai(os.path.join(OUTPUT_DIR, "image6.png"))
    draw_clean_database_erd(os.path.join(OUTPUT_DIR, "image13.png"))

    print("=" * 80)
    print("   HOÀN THÀNH VẼ LẠI CÁC SƠ ĐỒ USE CASE, ERD VÀ PHÂN RÃ!")
    print("=" * 80)


if __name__ == "__main__":
    main()
