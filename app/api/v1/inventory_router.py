# app/api/v1/inventory_router.py
from typing import List, Optional
from fastapi import APIRouter, Depends, status, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_active_user, require_role
from app.models.inventory_models import NguoiDung, HangHoa, TonKho, NhaCungCap, NhomHang, DonViTinh, PhieuNhap, PhieuXuat
from app.schemas.inventory_schemas import (
    PhieuNhapCreate, PhieuNhapOut,
    PhieuXuatCreate, PhieuXuatOut,
    KPISummary, StockAlertItem, HangHoaOut, HangHoaCreate, HangHoaUpdate,
    NhaCungCapCreate, NhaCungCapUpdate, NhaCungCapOut, NhaCungCapDetailOut, SupplierKPIs,
    NhomHangOut, DonViTinhOut, TheKhoRecord
)
from app.services.inbound_service import execute_inbound_transaction
from app.services.outbound_service import execute_outbound_transaction
from app.services.inventory_service import (
    get_dashboard_kpis, get_stock_alerts, get_all_hang_hoa,
    create_hang_hoa, update_hang_hoa, delete_hang_hoa,
    get_all_suppliers, get_supplier_kpis, get_supplier_detail,
    create_nha_cung_cap, update_nha_cung_cap, delete_nha_cung_cap,
    get_all_phieu_nhap, get_phieu_nhap_by_id,
    get_all_phieu_xuat, get_phieu_xuat_by_id,
    get_the_kho_by_item
)
from app.core.websocket_manager import ws_manager

router = APIRouter(prefix="/kho", tags=["Nghiệp Vụ Quản Lý Kho (ACID & CRUD)"])

# =============================================================================
# DASHBOARD & KPIS
# =============================================================================

@router.get("/kpis", response_model=KPISummary)
def api_get_kpis(
    db: Session = Depends(get_db),
    current_user: NguoiDung = Depends(get_current_active_user)
):
    """Lấy 4 chỉ số KPI thời gian thực cho Dashboard v2.0."""
    return get_dashboard_kpis(db)

@router.get("/alerts", response_model=List[StockAlertItem])
def api_get_stock_alerts(
    db: Session = Depends(get_db),
    current_user: NguoiDung = Depends(get_current_active_user)
):
    """Lấy danh sách các mặt hàng chạm hoặc dưới ngưỡng tồn tối thiểu (SoLuongTon <= TonToiThieu)."""
    return get_stock_alerts(db)

# =============================================================================
# CRUD HÀNG HÓA (SKU / PRODUCTS)
# =============================================================================

@router.get("/items", response_model=List[HangHoaOut])
def api_get_all_items(
    search: Optional[str] = Query(None, description="Tìm kiếm theo mã SKU hoặc tên hàng"),
    ma_nhom: Optional[str] = Query(None, description="Lọc theo mã nhóm hàng"),
    db: Session = Depends(get_db),
    current_user: NguoiDung = Depends(get_current_active_user)
):
    """Lấy danh sách toàn bộ mặt hàng kèm số lượng tồn khả dụng hiện tại (hỗ trợ tìm kiếm & lọc)."""
    return get_all_hang_hoa(db, search=search, ma_nhom=ma_nhom)

@router.post("/items", response_model=HangHoaOut, status_code=status.HTTP_201_CREATED)
def api_create_item(
    item_in: HangHoaCreate,
    db: Session = Depends(get_db),
    current_user: NguoiDung = Depends(require_role(["Admin", "Thukho"]))
):
    """Thêm mới mặt hàng vào danh mục và tự động khởi tạo tồn kho (Chỉ Admin & Thủ kho)."""
    item = create_hang_hoa(db, item_in)
    ton = item.ton_kho.SoLuongTon if item.ton_kho else 0
    ws_manager.broadcast_sync({
        "type": "INVENTORY_UPDATED",
        "action": "SKU_CREATED",
        "ma_hh": item.MaHH,
        "ten_hh": item.TenHH,
        "message": f"📦 Đã thêm mới mặt hàng [{item.TenHH}] bởi {current_user.HoTen}."
    })
    return {
        "MaHH": item.MaHH,
        "TenHH": item.TenHH,
        "MaNhom": item.MaNhom,
        "TenNhom": item.nhom_hang.TenNhom if item.nhom_hang else item.MaNhom,
        "MaDVT": item.MaDVT,
        "TenDVT": item.don_vi_tinh.TenDVT if item.don_vi_tinh else item.MaDVT,
        "TonToiThieu": item.TonToiThieu,
        "SoLuongTon": ton,
        "MoTa": item.MoTa or ""
    }

@router.put("/items/{ma_hh}", response_model=HangHoaOut)
def api_update_item(
    ma_hh: str,
    item_in: HangHoaUpdate,
    db: Session = Depends(get_db),
    current_user: NguoiDung = Depends(require_role(["Admin", "Thukho"]))
):
    """Cập nhật thông tin mặt hàng (Chỉ Admin & Thủ kho)."""
    item = update_hang_hoa(db, ma_hh, item_in)
    ton = item.ton_kho.SoLuongTon if item.ton_kho else 0
    ws_manager.broadcast_sync({
        "type": "INVENTORY_UPDATED",
        "action": "SKU_UPDATED",
        "ma_hh": item.MaHH,
        "ten_hh": item.TenHH,
        "message": f"📦 Mặt hàng [{item.TenHH}] vừa được cập nhật bởi {current_user.HoTen}."
    })
    return {
        "MaHH": item.MaHH,
        "TenHH": item.TenHH,
        "MaNhom": item.MaNhom,
        "TenNhom": item.nhom_hang.TenNhom if item.nhom_hang else item.MaNhom,
        "MaDVT": item.MaDVT,
        "TenDVT": item.don_vi_tinh.TenDVT if item.don_vi_tinh else item.MaDVT,
        "TonToiThieu": item.TonToiThieu,
        "SoLuongTon": ton,
        "MoTa": item.MoTa or ""
    }

@router.delete("/items/{ma_hh}")
def api_delete_item(
    ma_hh: str,
    db: Session = Depends(get_db),
    current_user: NguoiDung = Depends(require_role(["Admin", "Thukho"]))
):
    """Xóa mặt hàng (Chỉ Admin & Thủ kho, chỉ cho phép khi chưa phát sinh phiếu nhập/xuất kho)."""
    delete_hang_hoa(db, ma_hh)
    ws_manager.broadcast_sync({
        "type": "INVENTORY_UPDATED",
        "action": "SKU_DELETED",
        "ma_hh": ma_hh,
        "message": f"🗑️ Mặt hàng mã [{ma_hh}] đã bị xóa bởi {current_user.HoTen}."
    })
    return {"status": "success", "message": f"Đã xóa thành công mặt hàng [{ma_hh}]."}

# =============================================================================
# DANH MỤC NHÓM HÀNG & ĐƠN VỊ TÍNH
# =============================================================================

@router.get("/categories", response_model=List[NhomHangOut])
def api_get_categories(
    db: Session = Depends(get_db),
    current_user: NguoiDung = Depends(get_current_active_user)
):
    """Lấy danh sách các nhóm hàng hóa."""
    return db.query(NhomHang).all()

@router.get("/units", response_model=List[DonViTinhOut])
def api_get_units(
    db: Session = Depends(get_db),
    current_user: NguoiDung = Depends(get_current_active_user)
):
    """Lấy danh sách đơn vị tính."""
    return db.query(DonViTinh).all()

# =============================================================================
# CRUD NHÀ CUNG CẤP (SUPPLIERS)
# =============================================================================

@router.get("/suppliers/summary/kpis", response_model=SupplierKPIs)
def api_get_supplier_kpis(
    db: Session = Depends(get_db),
    current_user: NguoiDung = Depends(get_current_active_user)
):
    """Lấy chỉ số KPI tổng hợp phân hệ Nhà Cung Cấp."""
    return get_supplier_kpis(db)

@router.get("/suppliers", response_model=List[NhaCungCapOut])
def api_get_suppliers(
    db: Session = Depends(get_db),
    current_user: NguoiDung = Depends(get_current_active_user)
):
    """Lấy danh sách toàn bộ nhà cung cấp."""
    return get_all_suppliers(db)

@router.get("/suppliers/{ma_ncc}", response_model=NhaCungCapDetailOut)
def api_get_supplier_detail(
    ma_ncc: str,
    db: Session = Depends(get_db),
    current_user: NguoiDung = Depends(get_current_active_user)
):
    """Lấy thông tin chi tiết nhà cung cấp và lịch sử phiếu nhập liên kết."""
    return get_supplier_detail(db, ma_ncc)

@router.post("/suppliers", response_model=NhaCungCapOut, status_code=status.HTTP_201_CREATED)
def api_create_supplier(
    ncc_in: NhaCungCapCreate,
    db: Session = Depends(get_db),
    current_user: NguoiDung = Depends(require_role(["Admin", "Thukho"]))
):
    """Thêm mới đối tác nhà cung cấp (Chỉ Admin & Thủ kho)."""
    return create_nha_cung_cap(db, ncc_in)

@router.put("/suppliers/{ma_ncc}", response_model=NhaCungCapOut)
def api_update_supplier(
    ma_ncc: str,
    ncc_in: NhaCungCapUpdate,
    db: Session = Depends(get_db),
    current_user: NguoiDung = Depends(require_role(["Admin", "Thukho"]))
):
    """Cập nhật thông tin nhà cung cấp (Chỉ Admin & Thủ kho)."""
    return update_nha_cung_cap(db, ma_ncc, ncc_in)

@router.delete("/suppliers/{ma_ncc}")
def api_delete_supplier(
    ma_ncc: str,
    db: Session = Depends(get_db),
    current_user: NguoiDung = Depends(require_role(["Admin", "Thukho"]))
):
    """Xóa nhà cung cấp (Chỉ Admin & Thủ kho, chỉ khi chưa có phiếu nhập liên kết)."""
    delete_nha_cung_cap(db, ma_ncc)
    return {"status": "success", "message": f"Đã xóa thành công nhà cung cấp [{ma_ncc}]."}

# =============================================================================
# KIỂM TRA TỒN KHO & GIAO DỊCH NHẬP / XUẤT (ACID & RBAC)
# =============================================================================

@router.get("/check-stock/{ma_hh}")
def api_check_single_stock(
    ma_hh: str,
    db: Session = Depends(get_db),
    current_user: NguoiDung = Depends(get_current_active_user)
):
    """API thẩm định tồn kho tức thời phục vụ Real-time validation trên giao diện xuất kho."""
    hh = db.query(HangHoa).filter(HangHoa.MaHH == ma_hh).first()
    if not hh:
        raise HTTPException(status_code=404, detail="Không tìm thấy mặt hàng.")
    ton = hh.ton_kho.SoLuongTon if hh.ton_kho else 0
    return {
        "MaHH": hh.MaHH,
        "TenHH": hh.TenHH,
        "MaDVT": hh.MaDVT,
        "TonKhauDung": ton,
        "TonToiThieu": hh.TonToiThieu
    }

@router.post("/phieu-nhap", response_model=PhieuNhapOut, status_code=status.HTTP_201_CREATED)
def api_tao_phieu_nhap(
    phieu_in: PhieuNhapCreate,
    db: Session = Depends(get_db),
    current_user: NguoiDung = Depends(require_role(["Admin", "Thukho", "Ketoan"]))
):
    """API Lập Phiếu Nhập Kho Inbound trong 1 Transaction ACID (Admin, Thủ kho, Kế toán)."""
    phieu = execute_inbound_transaction(db, phieu_in, user_id=current_user.MaND)
    ws_manager.broadcast_sync({
        "type": "INVENTORY_UPDATED",
        "action": "INBOUND",
        "ma_chung_tu": phieu.MaPN,
        "user_name": current_user.HoTen,
        "vai_tro": current_user.VaiTro,
        "item_count": len(phieu.items),
        "message": f"📥 [{current_user.VaiTro}] {current_user.HoTen} vừa lập Phiếu Nhập [{phieu.MaPN}] ({len(phieu.items)} mặt hàng)."
    })
    return phieu

@router.get("/phieu-nhap", response_model=List[PhieuNhapOut])
def api_get_phieu_nhap_list(
    limit: int = Query(100, ge=1, le=500),
    skip: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: NguoiDung = Depends(require_role(["Admin", "Thukho", "Ketoan"]))
):
    """Xem danh sách các phiếu nhập kho (Admin, Thủ kho, Kế toán)."""
    return get_all_phieu_nhap(db, limit=limit, skip=skip)

@router.get("/phieu-nhap/{ma_pn}", response_model=PhieuNhapOut)
def api_get_phieu_nhap_detail(
    ma_pn: str,
    db: Session = Depends(get_db),
    current_user: NguoiDung = Depends(require_role(["Admin", "Thukho", "Ketoan"]))
):
    """Xem chi tiết một phiếu nhập kho kèm các dòng hàng (Admin, Thủ kho, Kế toán)."""
    return get_phieu_nhap_by_id(db, ma_pn)

@router.post("/phieu-xuat", response_model=PhieuXuatOut, status_code=status.HTTP_201_CREATED)
def api_tao_phieu_xuat(
    phieu_in: PhieuXuatCreate,
    db: Session = Depends(get_db),
    current_user: NguoiDung = Depends(require_role(["Admin", "Thukho", "Ketoan"]))
):
    """API Lập Phiếu Xuất Kho Outbound có Atomic SQL Decrement chống race condition (Admin, Thủ kho, Kế toán)."""
    phieu = execute_outbound_transaction(db, phieu_in, user_id=current_user.MaND)
    ws_manager.broadcast_sync({
        "type": "INVENTORY_UPDATED",
        "action": "OUTBOUND",
        "ma_chung_tu": phieu.MaPX,
        "user_name": current_user.HoTen,
        "vai_tro": current_user.VaiTro,
        "item_count": len(phieu.items),
        "message": f"📤 [{current_user.VaiTro}] {current_user.HoTen} vừa xuất kho thành công theo Phiếu [{phieu.MaPX}]."
    })
    return phieu

@router.get("/phieu-xuat", response_model=List[PhieuXuatOut])
def api_get_phieu_xuat_list(
    limit: int = Query(100, ge=1, le=500),
    skip: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: NguoiDung = Depends(require_role(["Admin", "Thukho", "Ketoan"]))
):
    """Xem danh sách các phiếu xuất kho (Admin, Thủ kho, Kế toán)."""
    return get_all_phieu_xuat(db, limit=limit, skip=skip)

@router.get("/phieu-xuat/{ma_px}", response_model=PhieuXuatOut)
def api_get_phieu_xuat_detail(
    ma_px: str,
    db: Session = Depends(get_db),
    current_user: NguoiDung = Depends(require_role(["Admin", "Thukho", "Ketoan"]))
):
    """Xem chi tiết một phiếu xuất kho kèm các dòng hàng (Admin, Thủ kho, Kế toán)."""
    return get_phieu_xuat_by_id(db, ma_px)

@router.get("/the-kho/{ma_hh}", response_model=List[TheKhoRecord])
def api_get_the_kho(
    ma_hh: str,
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: NguoiDung = Depends(require_role(["Admin", "Thukho", "Ketoan"]))
):
    """Tra cứu lịch sử sổ thẻ kho của một mặt hàng (Admin, Thủ kho, Kế toán)."""
    return get_the_kho_by_item(db, ma_hh, limit=limit)
