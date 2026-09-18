import io
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status
from app.core.datetime_utils import utc_now
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

from app.models.inventory_models import (
    HangHoa, TonKho, PhieuNhap, PhieuXuat, TheKho, 
    ChiTietPhieuNhap, ChiTietPhieuXuat, NhaCungCap, NhomHang, DonViTinh
)
from app.schemas.inventory_schemas import (
    HangHoaCreate, HangHoaUpdate, NhaCungCapCreate, NhaCungCapUpdate
)

def get_dashboard_kpis(db: Session) -> dict:
    """Tính toán 4 chỉ số KPI chính của Dashboard v2.0."""
    # 1. Tổng danh mục mặt hàng (SKU)
    tong_sku = db.query(func.count(HangHoa.MaHH)).scalar() or 0

    # 2. Số mặt hàng chạm hoặc dưới ngưỡng tồn tối thiểu
    canh_bao_ton_min = db.query(func.count(HangHoa.MaHH)).join(TonKho, HangHoa.MaHH == TonKho.MaHH)\
        .filter(TonKho.SoLuongTon <= HangHoa.TonToiThieu).scalar() or 0

    # 3. Tổng số giao dịch nhập và xuất
    tong_pn = db.query(func.count(PhieuNhap.MaPN)).scalar() or 0
    tong_px = db.query(func.count(PhieuXuat.MaPX)).scalar() or 0
    tong_giao_dich = tong_pn + tong_px

    # 4. Giá trị xuất kho ước tính / thực tế (Tính động theo giá vốn bình quân gia quyền từ ChiTietPhieuNhap)
    # 4.1: Giá bình quân gia quyền từng mặt hàng từ ChiTietPhieuNhap
    subq_item_price = db.query(
        ChiTietPhieuNhap.MaHH,
        (func.sum(ChiTietPhieuNhap.ThanhTien) / func.nullif(func.sum(ChiTietPhieuNhap.SoLuongNhap), 0)).label("item_avg_price")
    ).group_by(ChiTietPhieuNhap.MaHH).subquery()

    # 4.2: Giá bình quân gia quyền theo nhóm hàng (fallback nếu SKU chưa phát sinh phiếu nhập)
    subq_cat_price = db.query(
        HangHoa.MaNhom,
        (func.sum(ChiTietPhieuNhap.ThanhTien) / func.nullif(func.sum(ChiTietPhieuNhap.SoLuongNhap), 0)).label("cat_avg_price")
    ).join(HangHoa, ChiTietPhieuNhap.MaHH == HangHoa.MaHH).group_by(HangHoa.MaNhom).subquery()

    # 4.3: Giá bình quân toàn hệ thống (fallback cấp 3)
    system_avg_price = db.query(
        func.sum(ChiTietPhieuNhap.ThanhTien) / func.nullif(func.sum(ChiTietPhieuNhap.SoLuongNhap), 0)
    ).scalar() or 0.0

    # 4.4: Phân cấp xác định đơn giá xuất: Giá SKU -> Giá Nhóm hàng -> Giá bình quân hệ thống -> 0.0
    effective_price = func.coalesce(
        subq_item_price.c.item_avg_price,
        subq_cat_price.c.cat_avg_price,
        float(system_avg_price),
        0.0
    )

    val_xuat = db.query(
        func.sum(ChiTietPhieuXuat.SoLuongXuat * effective_price)
    ).join(HangHoa, ChiTietPhieuXuat.MaHH == HangHoa.MaHH)\
     .outerjoin(subq_item_price, ChiTietPhieuXuat.MaHH == subq_item_price.c.MaHH)\
     .outerjoin(subq_cat_price, HangHoa.MaNhom == subq_cat_price.c.MaNhom).scalar()

    tong_gia_tri_xuat = round(float(val_xuat or 0.0), 2)

    return {
        "tong_sku": tong_sku,
        "canh_bao_ton_min": canh_bao_ton_min,
        "tong_gia_tri_xuat_thang": tong_gia_tri_xuat,
        "tong_giao_dich_thang": tong_giao_dich,
        "tong_phieu_nhap": tong_pn,
        "tong_phieu_xuat": tong_px
    }

def get_stock_alerts(db: Session) -> list:
    """Lấy danh sách các mặt hàng chạm hoặc dưới ngưỡng tồn tối thiểu (SoLuongTon <= TonToiThieu)."""
    query = db.query(HangHoa, TonKho).join(TonKho, HangHoa.MaHH == TonKho.MaHH)\
        .filter(TonKho.SoLuongTon <= HangHoa.TonToiThieu).all()

    alert_items = []
    for hh, tk in query:
        thieu_hut = max(0, hh.TonToiThieu - tk.SoLuongTon)
        if tk.SoLuongTon <= (hh.TonToiThieu * 0.4) or tk.SoLuongTon == 0:
            muc_do = "danger"
        else:
            muc_do = "warning"

        alert_items.append({
            "MaHH": hh.MaHH,
            "TenHH": hh.TenHH,
            "MaDVT": hh.MaDVT,
            "SoLuongTon": tk.SoLuongTon,
            "TonToiThieu": hh.TonToiThieu,
            "MucDo": muc_do,
            "ThieuHut": thieu_hut
        })

    alert_items.sort(key=lambda x: (0 if x["MucDo"] == "danger" else 1, -x["ThieuHut"]))
    return alert_items

def recalculate_and_sync_the_kho(db: Session, ma_hh: Optional[str] = None) -> dict:
    """
    Chuẩn hóa và đồng bộ số dư Sổ Thẻ Kho & Tồn Kho (ACID Ledger Recalculation):
    1. Bổ sung các bản ghi Thẻ kho còn thiếu từ các Phiếu Nhập / Xuất kho thực tế (Audit Recovery).
    2. Duyệt toàn bộ giao dịch TheKho theo trình tự thời gian (NgayGiaoDich ASC, MaTK ASC).
    3. Đảm bảo tính toán đúng chuẩn:
       Tồn sau giao dịch (N) = Tồn sau giao dịch (N-1) + Số lượng biến động (N).
    4. Khắc phục triệt để các lỗi tính toán sai lệch (ví dụ: Tồn 135 - Xuất 20 = 10 -> sửa thành 115).
    5. Cập nhật TonKho.SoLuongTon đồng bộ tuyệt đối với số dư lũy kế cuối cùng trong Thẻ kho.
    """
    # 1. Bổ sung các chi tiết phiếu nhập còn thiếu vào Thẻ kho (nếu có)
    ct_nhap_query = db.query(ChiTietPhieuNhap, PhieuNhap).join(PhieuNhap, ChiTietPhieuNhap.MaPN == PhieuNhap.MaPN)
    if ma_hh:
        ct_nhap_query = ct_nhap_query.filter(ChiTietPhieuNhap.MaHH == ma_hh)
    
    for ct, pn in ct_nhap_query.all():
        exists = db.query(TheKho).filter(TheKho.MaChungTu == ct.MaPN, TheKho.MaHH == ct.MaHH).first()
        if not exists:
            the_kho_missing = TheKho(
                NgayGiaoDich=pn.NgayNhap,
                MaHH=ct.MaHH,
                MaChungTu=ct.MaPN,
                LoaiGiaoDich="NHAP",
                SoLuongThayDoi=ct.SoLuongNhap,
                TonSauGiaoDich=ct.SoLuongNhap
            )
            db.add(the_kho_missing)

    # Bổ sung các chi tiết phiếu xuất còn thiếu vào Thẻ kho (nếu có)
    ct_xuat_query = db.query(ChiTietPhieuXuat, PhieuXuat).join(PhieuXuat, ChiTietPhieuXuat.MaPX == PhieuXuat.MaPX)
    if ma_hh:
        ct_xuat_query = ct_xuat_query.filter(ChiTietPhieuXuat.MaHH == ma_hh)

    for ct, px in ct_xuat_query.all():
        exists = db.query(TheKho).filter(TheKho.MaChungTu == ct.MaPX, TheKho.MaHH == ct.MaHH).first()
        if not exists:
            the_kho_missing = TheKho(
                NgayGiaoDich=px.NgayXuat,
                MaHH=ct.MaHH,
                MaChungTu=ct.MaPX,
                LoaiGiaoDich="XUAT",
                SoLuongThayDoi=-ct.SoLuongXuat,
                TonSauGiaoDich=0
            )
            db.add(the_kho_missing)

    db.flush()

    # 2. Lấy danh sách hàng hóa cần tính toán
    query = db.query(HangHoa.MaHH)
    if ma_hh:
        query = query.filter(HangHoa.MaHH == ma_hh)
    skus = [s[0] for s in query.all()]

    fixed_ledger_count = 0
    synced_stock_count = 0

    for sku in skus:
        records = db.query(TheKho)\
            .filter(TheKho.MaHH == sku)\
            .order_by(TheKho.NgayGiaoDich.asc(), TheKho.MaTK.asc())\
            .all()

        # Kiểm tra trước tổng biến động để tránh tồn âm do lịch sử dữ liệu cũ
        min_required_initial = 0
        test_balance = 0
        for r in records:
            test_balance += r.SoLuongThayDoi
            if test_balance < 0:
                min_required_initial = max(min_required_initial, abs(test_balance))

        # Nếu có giao dịch khởi tạo ban đầu, nâng số dư ban đầu nếu cần bù âm lịch sử
        if min_required_initial > 0 and records:
            init_row = records[0]
            if "KHOITAO" in init_row.MaChungTu or "BANDAU" in init_row.MaChungTu:
                init_row.SoLuongThayDoi += min_required_initial
                fixed_ledger_count += 1

        running_balance = 0
        for r in records:
            expected = max(0, running_balance + r.SoLuongThayDoi)
            if r.TonSauGiaoDich != expected:
                r.TonSauGiaoDich = expected
                fixed_ledger_count += 1
            running_balance = expected

        tk = db.query(TonKho).filter(TonKho.MaHH == sku).first()
        if records:
            final_balance = records[-1].TonSauGiaoDich
            if not tk:
                tk = TonKho(MaHH=sku, SoLuongTon=final_balance, CapNhatCuoi=utc_now())
                db.add(tk)
                synced_stock_count += 1
            elif tk.SoLuongTon != final_balance:
                tk.SoLuongTon = final_balance
                tk.CapNhatCuoi = utc_now()
                synced_stock_count += 1
        elif tk and tk.SoLuongTon != 0:
            tk.SoLuongTon = 0
            tk.CapNhatCuoi = utc_now()
            synced_stock_count += 1

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    return {
        "processed_skus": len(skus),
        "fixed_ledger_count": fixed_ledger_count,
        "synced_stock_count": synced_stock_count
    }

def get_the_kho_by_item(db: Session, ma_hh: str, limit: int = 100, from_date: Optional[str] = None, to_date: Optional[str] = None) -> list:
    """
    Tra cứu lịch sử thẻ kho của một mặt hàng cụ thể, đảm bảo số dư lũy kế (Running balance)
    tuân thủ nghiêm ngặt công thức: Tồn(N) = Tồn(N-1) +/- Số lượng biến động.
    Hỗ trợ lọc theo khoảng ngày (from_date, to_date).
    """
    records = db.query(TheKho)\
        .filter(TheKho.MaHH == ma_hh)\
        .order_by(TheKho.NgayGiaoDich.asc(), TheKho.MaTK.asc())\
        .all()

    if not records:
        return []

    # Thẩm tra và chuẩn hóa tính nhất quán của số dư lũy kế
    needs_commit = False
    running_balance = 0
    for r in records:
        expected = running_balance + r.SoLuongThayDoi
        if r.TonSauGiaoDich != expected:
            r.TonSauGiaoDich = expected
            needs_commit = True
        running_balance = expected

    # Đồng bộ số dư vào TonKho
    tk = db.query(TonKho).filter(TonKho.MaHH == ma_hh).first()
    if tk:
        if tk.SoLuongTon != running_balance:
            tk.SoLuongTon = running_balance
            tk.CapNhatCuoi = utc_now()
            needs_commit = True
    else:
        tk = TonKho(MaHH=ma_hh, SoLuongTon=running_balance, CapNhatCuoi=utc_now())
        db.add(tk)
        needs_commit = True

    if needs_commit:
        try:
            db.commit()
        except Exception:
            db.rollback()

    filtered_records = records
    if from_date:
        try:
            from_dt = datetime.strptime(from_date.strip()[:10], "%Y-%m-%d").date()
            filtered_records = [r for r in filtered_records if r.NgayGiaoDich.date() >= from_dt]
        except Exception:
            pass

    if to_date:
        try:
            to_dt = datetime.strptime(to_date.strip()[:10], "%Y-%m-%d").date()
            filtered_records = [r for r in filtered_records if r.NgayGiaoDich.date() <= to_dt]
        except Exception:
            pass

    if limit and len(filtered_records) > limit:
        return filtered_records[-limit:]
    return filtered_records

def get_all_phieu_nhap(db: Session, limit: int = 100, skip: int = 0) -> list:
    """Lấy danh sách phiếu nhập kho sắp xếp theo ngày nhập mới nhất."""
    return db.query(PhieuNhap).order_by(PhieuNhap.NgayNhap.desc()).offset(skip).limit(limit).all()

def get_phieu_nhap_by_id(db: Session, ma_pn: str) -> PhieuNhap:
    """Lấy chi tiết một phiếu nhập kho kèm chi tiết các dòng hàng."""
    pn = db.query(PhieuNhap).filter(PhieuNhap.MaPN == ma_pn).first()
    if not pn:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy phiếu nhập kho [{ma_pn}]."
        )
    return pn

def get_all_phieu_xuat(db: Session, limit: int = 100, skip: int = 0) -> list:
    """Lấy danh sách phiếu xuất kho sắp xếp theo ngày xuất mới nhất."""
    return db.query(PhieuXuat).order_by(PhieuXuat.NgayXuat.desc()).offset(skip).limit(limit).all()

def get_phieu_xuat_by_id(db: Session, ma_px: str) -> PhieuXuat:
    """Lấy chi tiết một phiếu xuất kho kèm chi tiết các dòng hàng."""
    px = db.query(PhieuXuat).filter(PhieuXuat.MaPX == ma_px).first()
    if not px:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy phiếu xuất kho [{ma_px}]."
        )
    return px

# =============================================================================
# CRUD HÀNG HÓA (PRODUCTS / SKUs)
# =============================================================================

def get_all_hang_hoa(db: Session, search: Optional[str] = None, ma_nhom: Optional[str] = None):
    """Lấy danh sách hàng hóa kèm số lượng tồn kho thực tế, hỗ trợ lọc và tìm kiếm."""
    query = db.query(HangHoa)
    if ma_nhom and ma_nhom != "ALL":
        query = query.filter(HangHoa.MaNhom == ma_nhom)
    if search:
        search_fmt = f"%{search}%"
        query = query.filter((HangHoa.MaHH.ilike(search_fmt)) | (HangHoa.TenHH.ilike(search_fmt)))
    
    items = query.all()
    results = []
    for item in items:
        ton = item.ton_kho.SoLuongTon if item.ton_kho else 0
        results.append({
            "MaHH": item.MaHH,
            "TenHH": item.TenHH,
            "MaNhom": item.MaNhom,
            "TenNhom": item.nhom_hang.TenNhom if item.nhom_hang else item.MaNhom,
            "MaDVT": item.MaDVT,
            "TenDVT": item.don_vi_tinh.TenDVT if item.don_vi_tinh else item.MaDVT,
            "TonToiThieu": item.TonToiThieu,
            "SoLuongTon": ton,
            "MoTa": item.MoTa or ""
        })
    return results

def create_hang_hoa(db: Session, item_in: HangHoaCreate) -> HangHoa:
    """Thêm mới một mặt hàng và khởi tạo bản ghi tồn kho ban đầu."""
    existing = db.query(HangHoa).filter(HangHoa.MaHH == item_in.MaHH).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mã hàng hóa [{item_in.MaHH}] đã tồn tại trong hệ thống."
        )

    # Đảm bảo Nhóm hàng và ĐVT hợp lệ (hỗ trợ không phân biệt hoa thường)
    nhom = db.query(NhomHang).filter(func.lower(NhomHang.MaNhom) == func.lower(item_in.MaNhom.strip())).first()
    if not nhom:
        raise HTTPException(status_code=400, detail=f"Mã nhóm hàng [{item_in.MaNhom}] không tồn tại.")
    
    dvt = db.query(DonViTinh).filter(func.lower(DonViTinh.MaDVT) == func.lower(item_in.MaDVT.strip())).first()
    if not dvt:
        raise HTTPException(status_code=400, detail=f"Mã đơn vị tính [{item_in.MaDVT}] không tồn tại.")

    new_item = HangHoa(
        MaHH=item_in.MaHH.strip().upper(),
        TenHH=item_in.TenHH.strip(),
        MaNhom=nhom.MaNhom,
        MaDVT=dvt.MaDVT,
        TonToiThieu=item_in.TonToiThieu,
        MoTa=item_in.MoTa
    )
    db.add(new_item)
    db.flush()

    # Khởi tạo bản ghi Tồn kho với ràng buộc CheckConstraint >= 0
    ton_kho = TonKho(
        MaHH=new_item.MaHH,
        SoLuongTon=item_in.SoLuongBanDau,
        CapNhatCuoi=utc_now()
    )
    db.add(ton_kho)

    # Nếu có tồn ban đầu, ghi nhận giao dịch vào Thẻ kho
    if item_in.SoLuongBanDau > 0:
        the_kho = TheKho(
            NgayGiaoDich=utc_now(),
            MaHH=new_item.MaHH,
            MaChungTu="SODU-BANDAU",
            LoaiGiaoDich="NHAP",
            SoLuongThayDoi=item_in.SoLuongBanDau,
            TonSauGiaoDich=item_in.SoLuongBanDau
        )
        db.add(the_kho)

    db.commit()
    db.refresh(new_item)
    return new_item

def update_hang_hoa(db: Session, ma_hh: str, item_in: HangHoaUpdate) -> HangHoa:
    """Cập nhật thông tin hàng hóa."""
    item = db.query(HangHoa).filter(HangHoa.MaHH == ma_hh).first()
    if not item:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy mặt hàng [{ma_hh}].")

    if item_in.MaNhom:
        nhom = db.query(NhomHang).filter(func.lower(NhomHang.MaNhom) == func.lower(item_in.MaNhom.strip())).first()
        if not nhom:
            raise HTTPException(status_code=400, detail=f"Mã nhóm hàng [{item_in.MaNhom}] không tồn tại.")
        item.MaNhom = nhom.MaNhom

    if item_in.MaDVT:
        dvt = db.query(DonViTinh).filter(func.lower(DonViTinh.MaDVT) == func.lower(item_in.MaDVT.strip())).first()
        if not dvt:
            raise HTTPException(status_code=400, detail=f"Mã đơn vị tính [{item_in.MaDVT}] không tồn tại.")
        item.MaDVT = dvt.MaDVT

    item.TenHH = item_in.TenHH.strip()
    item.TonToiThieu = item_in.TonToiThieu
    item.MoTa = item_in.MoTa

    db.commit()
    db.refresh(item)
    return item

def delete_hang_hoa(db: Session, ma_hh: str) -> bool:
    """Xóa mặt hàng nếu chưa phát sinh phiếu nhập/xuất kho."""
    item = db.query(HangHoa).filter(HangHoa.MaHH == ma_hh).first()
    if not item:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy mặt hàng [{ma_hh}].")

    # Kiểm tra ràng buộc toàn vẹn: Không cho xóa nếu đã có chứng từ
    has_pn = db.query(ChiTietPhieuNhap).filter(ChiTietPhieuNhap.MaHH == ma_hh).first()
    has_px = db.query(ChiTietPhieuXuat).filter(ChiTietPhieuXuat.MaHH == ma_hh).first()
    if has_pn or has_px:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mặt hàng [{item.TenHH}] đã phát sinh chứng từ nhập/xuất kho. Không thể xóa để bảo toàn lịch sử sổ sách kế toán."
        )

    # Xóa bản ghi thẻ kho ban đầu và tồn kho nếu có
    db.query(TheKho).filter(TheKho.MaHH == ma_hh).delete()
    db.query(TonKho).filter(TonKho.MaHH == ma_hh).delete()
    db.delete(item)
    db.commit()
    return True

# =============================================================================
# CRUD NHÀ CUNG CẤP (SUPPLIERS)
# =============================================================================

def get_all_suppliers(db: Session):
    """Lấy danh sách toàn bộ nhà cung cấp kèm thống kê số phiếu nhập và tổng tiền."""
    suppliers = db.query(NhaCungCap).order_by(NhaCungCap.TenNCC.asc()).all()
    results = []
    for s in suppliers:
        pns = s.phieu_nhap or []
        so_pn = len(pns)
        # Tính tổng tiền chi tiết phiếu nhập (tự động fallback nếu TongTien trên master chưa cập nhật)
        tien_pns = sum((pn.TongTien if pn.TongTien and pn.TongTien > 0 else sum(ct.ThanhTien for ct in pn.chi_tiet)) for pn in pns)
        # Nếu s.TongTien được người dùng thiết lập / điều chỉnh trực tiếp (> 0) thì ưu tiên hiển thị s.TongTien
        tong_tien = s.TongTien if (s.TongTien is not None and s.TongTien > 0) else tien_pns
        latest_date = None
        if pns:
            latest_pn = max(pns, key=lambda p: p.NgayNhap)
            latest_date = latest_pn.NgayNhap.strftime("%d/%m/%Y")
        
        results.append({
            "MaNCC": s.MaNCC,
            "TenNCC": s.TenNCC,
            "DiaChi": s.DiaChi or "",
            "SoDienThoai": s.SoDienThoai or "",
            "Email": s.Email or "",
            "SoPhieuNhap": so_pn,
            "TongGiaTriNhap": tong_tien,
            "TongTien": s.TongTien if s.TongTien is not None else tong_tien,
            "NgayNhapGanNhat": latest_date
        })
    return results

def get_supplier_kpis(db: Session) -> dict:
    """Thống kê chỉ số KPI toàn diện phân hệ Nhà Cung Cấp."""
    suppliers = db.query(NhaCungCap).all()
    tong_ncc = len(suppliers)
    ncc_active = 0
    tong_chi_tieu = 0.0
    top_ncc = "Chưa có"
    top_ncc_tien = 0.0

    for s in suppliers:
        pns = s.phieu_nhap or []
        tien_pns = sum((pn.TongTien if pn.TongTien and pn.TongTien > 0 else sum(ct.ThanhTien for ct in pn.chi_tiet)) for pn in pns)
        tien_s = s.TongTien if (s.TongTien is not None and s.TongTien > 0) else tien_pns
        if pns or (s.TongTien and s.TongTien > 0):
            ncc_active += 1
        tong_chi_tieu += tien_s
        if tien_s > top_ncc_tien:
            top_ncc_tien = tien_s
            top_ncc = s.TenNCC

    return {
        "TongNCC": tong_ncc,
        "NCCActive": ncc_active,
        "TongChiTieu": tong_chi_tieu,
        "TopNCC": top_ncc,
        "TopNCCTien": top_ncc_tien
    }

def get_supplier_detail(db: Session, ma_ncc: str) -> dict:
    """Lấy chi tiết hồ sơ nhà cung cấp và toàn bộ lịch sử phiếu nhập liên kết."""
    ncc = db.query(NhaCungCap).filter(NhaCungCap.MaNCC == ma_ncc).first()
    if not ncc:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy nhà cung cấp [{ma_ncc}].")

    pns = sorted(ncc.phieu_nhap, key=lambda p: p.NgayNhap, reverse=True)
    so_pn = len(pns)
    tien_pns = sum((pn.TongTien if pn.TongTien and pn.TongTien > 0 else sum(ct.ThanhTien for ct in pn.chi_tiet)) for pn in pns)
    tong_tien = ncc.TongTien if (ncc.TongTien is not None and ncc.TongTien > 0) else tien_pns
    latest_date = pns[0].NgayNhap.strftime("%d/%m/%Y") if pns else None

    history = []
    for pn in pns:
        ct_items = []
        for ct in pn.chi_tiet:
            ten_hh = ct.hang_hoa.TenHH if ct.hang_hoa else ct.MaHH
            ct_items.append({
                "MaHH": ct.MaHH,
                "TenHH": ten_hh,
                "SoLuongNhap": ct.SoLuongNhap,
                "DonGiaNhap": ct.DonGiaNhap,
                "ThanhTien": ct.ThanhTien
            })
        
        history.append({
            "MaPN": pn.MaPN,
            "NgayNhap": pn.NgayNhap,
            "NguoiLap": pn.nguoi_dung.HoTen if pn.nguoi_dung else "Thủ kho",
            "TongTien": pn.TongTien if pn.TongTien and pn.TongTien > 0 else sum(ct.ThanhTien for ct in pn.chi_tiet),
            "GhiChu": pn.GhiChu or "",
            "SoMatHang": len(pn.chi_tiet),
            "ChiTiet": ct_items
        })

    return {
        "MaNCC": ncc.MaNCC,
        "TenNCC": ncc.TenNCC,
        "DiaChi": ncc.DiaChi or "",
        "SoDienThoai": ncc.SoDienThoai or "",
        "Email": ncc.Email or "",
        "SoPhieuNhap": so_pn,
        "TongGiaTriNhap": tong_tien,
        "TongTien": ncc.TongTien if ncc.TongTien is not None else tong_tien,
        "NgayNhapGanNhat": latest_date,
        "LichSuNhap": history
    }

def create_nha_cung_cap(db: Session, ncc_in: NhaCungCapCreate) -> NhaCungCap:
    """Thêm mới nhà cung cấp với hỗ trợ khởi tạo dòng tiền / số tiền ban đầu."""
    existing = db.query(NhaCungCap).filter(func.lower(NhaCungCap.MaNCC) == func.lower(ncc_in.MaNCC.strip())).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Mã NCC [{ncc_in.MaNCC}] đã tồn tại.")

    ncc = NhaCungCap(
        MaNCC=ncc_in.MaNCC.strip().upper(),
        TenNCC=ncc_in.TenNCC.strip(),
        DiaChi=ncc_in.DiaChi.strip() if ncc_in.DiaChi and ncc_in.DiaChi.strip() else None,
        SoDienThoai=ncc_in.SoDienThoai.strip() if ncc_in.SoDienThoai and ncc_in.SoDienThoai.strip() else None,
        Email=ncc_in.Email.strip() if ncc_in.Email and ncc_in.Email.strip() else None,
        TongTien=max(0.0, float(ncc_in.TongTien)) if ncc_in.TongTien is not None else 0.0
    )
    db.add(ncc)
    db.commit()
    db.refresh(ncc)
    return ncc

def update_nha_cung_cap(db: Session, ma_ncc: str, ncc_in: NhaCungCapUpdate) -> NhaCungCap:
    """Cập nhật thông tin nhà cung cấp và cho phép điều chỉnh dòng tiền / số tiền."""
    ncc = db.query(NhaCungCap).filter(NhaCungCap.MaNCC == ma_ncc).first()
    if not ncc:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy nhà cung cấp [{ma_ncc}].")

    ncc.TenNCC = ncc_in.TenNCC.strip()
    ncc.DiaChi = ncc_in.DiaChi.strip() if ncc_in.DiaChi and ncc_in.DiaChi.strip() else None
    ncc.SoDienThoai = ncc_in.SoDienThoai.strip() if ncc_in.SoDienThoai and ncc_in.SoDienThoai.strip() else None
    ncc.Email = ncc_in.Email.strip() if ncc_in.Email and ncc_in.Email.strip() else None
    if ncc_in.TongTien is not None:
        ncc.TongTien = max(0.0, float(ncc_in.TongTien))

    db.commit()
    db.refresh(ncc)
    return ncc

def update_supplier_cashflow(db: Session, ma_ncc: str, tong_tien: float, ghi_chu: Optional[str] = None) -> NhaCungCap:
    """Điều chỉnh trực tiếp số tiền / dòng tiền cho nhà cung cấp."""
    ncc = db.query(NhaCungCap).filter(NhaCungCap.MaNCC == ma_ncc).first()
    if not ncc:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy nhà cung cấp [{ma_ncc}].")
    ncc.TongTien = max(0.0, float(tong_tien))
    db.commit()
    db.refresh(ncc)
    return ncc

def delete_nha_cung_cap(db: Session, ma_ncc: str) -> bool:
    """Xóa nhà cung cấp nếu chưa có phiếu nhập."""
    ncc = db.query(NhaCungCap).filter(NhaCungCap.MaNCC == ma_ncc).first()
    if not ncc:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy nhà cung cấp [{ma_ncc}].")

    has_pn = db.query(PhieuNhap).filter(PhieuNhap.MaNCC == ma_ncc).first()
    if has_pn:
        raise HTTPException(
            status_code=400,
            detail=f"Nhà cung cấp [{ncc.TenNCC}] ({ma_ncc}) đã có phiếu nhập kho liên kết trong hệ thống. Để đảm bảo toàn vẹn dữ liệu kế toán, không thể xóa."
        )

    db.delete(ncc)
    db.commit()
    return True

def generate_excel_suppliers_report(db: Session) -> io.BytesIO:
    """
    Sinh file Excel (.xlsx) Báo cáo Danh bạ Đối tác & Nhà Cung Cấp từ CSDL.
    Định dạng chuẩn kế toán với border, header màu thương hiệu SmartLogis, và tính tổng chi tiêu.
    """
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "DanhBa_NhaCungCap"

    # Font và Styles
    font_title = Font(name="Times New Roman", size=16, bold=True, color="0F172A")
    font_sub = Font(name="Times New Roman", size=11, italic=True, color="475569")
    font_header = Font(name="Times New Roman", size=11, bold=True, color="FFFFFF")
    font_data = Font(name="Times New Roman", size=11)
    font_total = Font(name="Times New Roman", size=11, bold=True, color="0F172A")

    fill_header = PatternFill(start_color="0369A1", end_color="0369A1", fill_type="solid")
    fill_zebra = PatternFill(start_color="F0F9FF", end_color="F0F9FF", fill_type="solid")

    thin_border = Border(
        left=Side(style='thin', color='CBD5E1'),
        right=Side(style='thin', color='CBD5E1'),
        top=Side(style='thin', color='CBD5E1'),
        bottom=Side(style='thin', color='CBD5E1')
    )

    # 1. Tiêu đề Báo Cáo
    ws.merge_cells("A1:H1")
    ws["A1"] = "HỆ THỐNG QUẢN LÝ KHO THÔNG MINH SMARTLOGIS AI"
    ws["A1"].font = Font(name="Times New Roman", size=12, bold=True, color="0284C7")
    ws["A1"].alignment = Alignment(horizontal="center")

    ws.merge_cells("A2:H2")
    ws["A2"] = "DANH BẠ ĐỐI TÁC & THỐNG KÊ CUNG ỨNG VẬT TƯ NHÀ CUNG CẤP"
    ws["A2"].font = font_title
    ws["A2"].alignment = Alignment(horizontal="center")

    ws.merge_cells("A3:H3")
    ws["A3"] = f"Thời điểm trích xuất: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} - Toàn bộ dữ liệu trích xuất từ PostgreSQL/SQLite CSDL"
    ws["A3"].font = font_sub
    ws["A3"].alignment = Alignment(horizontal="center")

    # 2. Header bảng dữ liệu
    headers = [
        "STT", "Mã Đối Tác", "Tên Công Ty / Nhà Cung Cấp", "Số Điện Thoại",
        "Hòm Thư Email", "Địa Chỉ Trụ Sở", "Số Phiếu Nhập", "Tổng Tiền Nhập (VNĐ)"
    ]
    row_idx = 5
    for col_idx, h in enumerate(headers, 1):
        cell = ws.cell(row=row_idx, column=col_idx, value=h)
        cell.font = font_header
        cell.fill = fill_header
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = thin_border
    ws.row_dimensions[row_idx].height = 28

    # 3. Lấy dữ liệu
    suppliers = get_all_suppliers(db)
    total_pos = 0
    grand_total_spent = 0.0

    for idx, s in enumerate(suppliers, 1):
        row_idx += 1
        so_pn = s.get("SoPhieuNhap", 0)
        tong_tien = s.get("TongGiaTriNhap", 0.0)
        total_pos += so_pn
        grand_total_spent += tong_tien

        row_data = [
            idx,
            s["MaNCC"],
            s["TenNCC"],
            s["SoDienThoai"] or "--",
            s["Email"] or "--",
            s["DiaChi"] or "--",
            so_pn,
            f"{tong_tien:,.0f}"
        ]

        for col_idx, val in enumerate(row_data, 1):
            cell = ws.cell(row=row_idx, column=col_idx, value=val)
            cell.font = font_data
            cell.border = thin_border
            if idx % 2 == 0:
                cell.fill = fill_zebra

            if col_idx in [1, 2]:
                cell.alignment = Alignment(horizontal="center")
            elif col_idx in [7, 8]:
                cell.alignment = Alignment(horizontal="right")
            else:
                cell.alignment = Alignment(horizontal="left")

    # 4. Dòng tổng cộng
    row_idx += 1
    ws.cell(row=row_idx, column=1, value="TỔNG CỘNG").font = font_total
    ws.merge_cells(start_row=row_idx, start_column=1, end_row=row_idx, end_column=6)
    cell_tot_lbl = ws.cell(row=row_idx, column=1)
    cell_tot_lbl.alignment = Alignment(horizontal="center", vertical="center")
    cell_tot_lbl.border = thin_border
    cell_tot_lbl.fill = PatternFill(start_color="E2E8F0", end_color="E2E8F0", fill_type="solid")

    for c in range(2, 7):
        ws.cell(row=row_idx, column=c).border = thin_border
        ws.cell(row=row_idx, column=c).fill = PatternFill(start_color="E2E8F0", end_color="E2E8F0", fill_type="solid")

    cell_tot_po = ws.cell(row=row_idx, column=7, value=total_pos)
    cell_tot_po.font = font_total
    cell_tot_po.alignment = Alignment(horizontal="right")
    cell_tot_po.border = thin_border
    cell_tot_po.fill = PatternFill(start_color="E2E8F0", end_color="E2E8F0", fill_type="solid")

    cell_tot_tien = ws.cell(row=row_idx, column=8, value=f"{grand_total_spent:,.0f}")
    cell_tot_tien.font = font_total
    cell_tot_tien.alignment = Alignment(horizontal="right")
    cell_tot_tien.border = thin_border
    cell_tot_tien.fill = PatternFill(start_color="E2E8F0", end_color="E2E8F0", fill_type="solid")

    # 5. Tự động điều chỉnh độ rộng cột
    for col in ws.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws.column_dimensions[col_letter].width = max(max_len + 4, 12)
    ws.column_dimensions["C"].width = 36
    ws.column_dimensions["F"].width = 35

    stream = io.BytesIO()
    wb.save(stream)
    stream.seek(0)
    return stream


# =============================================================================
# XUẤT BÁO CÁO EXCEL CHUẨN KẾ TOÁN (OPENPYXL REAL ENGINE)
# =============================================================================

def generate_excel_inventory_report(db: Session) -> io.BytesIO:
    """
    Sinh file Excel (.xlsx) Báo cáo Nhập - Xuất - Tồn kho thực tế từ CSDL.
    Định dạng chuẩn kế toán doanh nghiệp với header màu, borders, tự động căn chỉnh độ rộng cột.
    """
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "BaoCao_NhapXuatTon"

    # Font và Styles
    font_title = Font(name="Times New Roman", size=16, bold=True, color="0F172A")
    font_sub = Font(name="Times New Roman", size=11, italic=True, color="475569")
    font_header = Font(name="Times New Roman", size=11, bold=True, color="FFFFFF")
    font_data = Font(name="Times New Roman", size=11)
    font_total = Font(name="Times New Roman", size=11, bold=True, color="0F172A")

    fill_header = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
    fill_zebra = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
    fill_alert = PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid")

    thin_border = Border(
        left=Side(style='thin', color='CBD5E1'),
        right=Side(style='thin', color='CBD5E1'),
        top=Side(style='thin', color='CBD5E1'),
        bottom=Side(style='thin', color='CBD5E1')
    )

    # 1. Tiêu đề Báo Cáo
    ws.merge_cells("A1:I1")
    ws["A1"] = "HỆ THỐNG QUẢN LÝ KHO THÔNG MINH SMARTLOGIS AI"
    ws["A1"].font = Font(name="Times New Roman", size=12, bold=True, color="2563EB")
    ws["A1"].alignment = Alignment(horizontal="center")

    ws.merge_cells("A2:I2")
    ws["A2"] = "BÁO CÁO TỔNG HỢP NHẬP - XUẤT - TỒN KHO HÀNG HÓA"
    ws["A2"].font = font_title
    ws["A2"].alignment = Alignment(horizontal="center")

    ws.merge_cells("A3:I3")
    ws["A3"] = f"Thời điểm kết xuất: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} - Toàn bộ dữ liệu trích xuất từ PostgreSQL CSDL"
    ws["A3"].font = font_sub
    ws["A3"].alignment = Alignment(horizontal="center")

    # 2. Header bảng dữ liệu
    headers = [
        "STT", "Mã SKU", "Tên Hàng Hóa", "Nhóm Hàng", "ĐVT", 
        "Tồn Hiện Tại", "Tồn Tối Thiểu", "Thiếu Hụt", "Trạng Thái Cảnh Báo"
    ]
    row_idx = 5
    for col_idx, h in enumerate(headers, 1):
        cell = ws.cell(row=row_idx, column=col_idx, value=h)
        cell.font = font_header
        cell.fill = fill_header
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = thin_border
    ws.row_dimensions[row_idx].height = 28

    # 3. Lấy dữ liệu thật từ CSDL
    items = db.query(HangHoa).order_by(HangHoa.MaHH.asc()).all()
    
    total_ton = 0
    total_min = 0
    total_thieu = 0

    for idx, item in enumerate(items, 1):
        row_idx += 1
        ton = item.ton_kho.SoLuongTon if item.ton_kho else 0
        min_ton = item.TonToiThieu
        thieu = max(0, min_ton - ton)
        
        total_ton += ton
        total_min += min_ton
        total_thieu += thieu

        if ton <= 0:
            status_text = "HẾT HÀNG (Nguy cấp)"
        elif ton <= min_ton:
            status_text = f"CẢNH BÁO (Thiếu {thieu})"
        else:
            status_text = "An toàn"

        row_data = [
            idx,
            item.MaHH,
            item.TenHH,
            item.nhom_hang.TenNhom if item.nhom_hang else item.MaNhom,
            item.don_vi_tinh.TenDVT if item.don_vi_tinh else item.MaDVT,
            ton,
            min_ton,
            thieu,
            status_text
        ]

        for col_idx, val in enumerate(row_data, 1):
            c = ws.cell(row=row_idx, column=col_idx, value=val)
            c.font = font_data
            c.border = thin_border
            
            # Căn lề
            if col_idx in [1, 2, 5]:
                c.alignment = Alignment(horizontal="center", vertical="center")
            elif col_idx in [6, 7, 8]:
                c.alignment = Alignment(horizontal="right", vertical="center")
                c.number_format = "#,##0"
            elif col_idx == 9:
                c.alignment = Alignment(horizontal="center", vertical="center")
                if ton <= min_ton:
                    c.fill = fill_alert
                    c.font = Font(name="Times New Roman", size=11, bold=True, color="B91C1C")
            else:
                c.alignment = Alignment(horizontal="left", vertical="center")

        ws.row_dimensions[row_idx].height = 20

    # 4. Hàng Tổng Cộng
    row_idx += 1
    ws.merge_cells(start_row=row_idx, start_column=1, end_row=row_idx, end_column=5)
    total_label = ws.cell(row=row_idx, column=1, value="TỔNG CỘNG HỆ THỐNG")
    total_label.font = font_total
    total_label.alignment = Alignment(horizontal="center", vertical="center")
    
    for c_i in range(1, 10):
        ws.cell(row=row_idx, column=c_i).border = thin_border
        ws.cell(row=row_idx, column=c_i).fill = fill_zebra

    c_ton = ws.cell(row=row_idx, column=6, value=total_ton)
    c_ton.font = font_total
    c_ton.alignment = Alignment(horizontal="right", vertical="center")
    c_ton.number_format = "#,##0"

    c_min = ws.cell(row=row_idx, column=7, value=total_min)
    c_min.font = font_total
    c_min.alignment = Alignment(horizontal="right", vertical="center")
    c_min.number_format = "#,##0"

    c_thieu = ws.cell(row=row_idx, column=8, value=total_thieu)
    c_thieu.font = font_total
    c_thieu.alignment = Alignment(horizontal="right", vertical="center")
    c_thieu.number_format = "#,##0"

    ws.row_dimensions[row_idx].height = 24

    # 5. Tự động căn chỉnh độ rộng cột
    for col in ws.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            val_str = str(cell.value or "")
            if cell.row > 3:
                max_len = max(max_len, len(val_str))
        ws.column_dimensions[col_letter].width = max(max_len + 4, 12)
    ws.column_dimensions["A"].width = 8
    ws.column_dimensions["C"].width = 32

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output
