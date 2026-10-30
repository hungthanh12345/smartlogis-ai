# app/services/inbound_service.py
import uuid
from datetime import datetime
from sqlalchemy import update
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.models.inventory_models import PhieuNhap, ChiTietPhieuNhap, TonKho, TheKho, HangHoa, NhaCungCap, NguoiDung
from app.schemas.inventory_schemas import PhieuNhapCreate
from app.core.datetime_utils import utc_now

def execute_inbound_transaction(db: Session, phieu_in: PhieuNhapCreate, user_id: int) -> PhieuNhap:
    """
    Lập phiếu nhập kho Inbound trong 1 Database Transaction nguyên tử (ACID):
    1. Kiểm tra tính hợp lệ của Người dùng và Nhà cung cấp (Foreign Key).
    2. Thẩm định danh sách mặt hàng: Quantity > 0, Unit Price > 0, Tổng tiền > 0.
    3. Tạo Master PhieuNhap (Mã tự sinh dạng PN-YYYYMMDD-UUID).
    4. Cập nhật tăng SoLuongTon và Thẻ kho (TheKho) chuẩn xác lũy kế.
    5. Xử lý an toàn các giá trị null references và lỗi ràng buộc CSDL.
    """
    try:
        # 1. Kiểm tra khóa ngoại Người Dùng (MaND)
        user = db.query(NguoiDung).filter(NguoiDung.MaND == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tài khoản người dùng (MaND={user_id}) không tồn tại trong hệ thống. Vui lòng đăng nhập lại."
            )

        # 2. Kiểm tra khóa ngoại Nhà Cung Cấp (MaNCC)
        if not phieu_in.MaNCC or not phieu_in.MaNCC.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mã Nhà Cung Cấp không được để trống."
            )

        ma_ncc = phieu_in.MaNCC.strip()
        ncc = db.query(NhaCungCap).filter(NhaCungCap.MaNCC == ma_ncc).first()
        if not ncc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Nhà cung cấp mã [{ma_ncc}] không tồn tại trong hệ thống (vi phạm ràng buộc khóa ngoại)."
            )

        # 3. Kiểm tra danh sách mặt hàng không rỗng
        if not phieu_in.items or len(phieu_in.items) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phiếu nhập kho phải chứa ít nhất 1 mặt hàng."
            )

        # 4. Thẩm định từng dòng và gom nhóm các dòng cùng SKU
        merged_items = {}
        for item in phieu_in.items:
            if not item.MaHH or not item.MaHH.strip():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Mã hàng hóa trong chi tiết phiếu nhập không được để trống."
                )

            sku = item.MaHH.strip()

            # Ràng buộc số lượng phải > 0
            qty = item.SoLuongNhap
            if qty is None or qty <= 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Số lượng nhập của mặt hàng [{sku}] phải lớn hơn 0 (hiện tại: {qty})."
                )

            # Ràng buộc đơn giá phải > 0 (Khóa chặn Đơn giá <= 0)
            price = item.DonGiaNhap
            if price is None or price <= 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Đơn giá nhập của mặt hàng [{sku}] phải lớn hơn 0 (hiện tại: {price})."
                )

            # Kiểm tra khóa ngoại Hàng Hóa (MaHH)
            hh = db.query(HangHoa).filter(HangHoa.MaHH == sku).first()
            if not hh:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Mặt hàng mã [{sku}] không tồn tại trong danh mục hàng hóa (vi phạm ràng buộc khóa ngoại)."
                )

            if sku in merged_items:
                prev = merged_items[sku]
                total_qty = prev["SoLuongNhap"] + qty
                total_cost = (prev["SoLuongNhap"] * prev["DonGiaNhap"]) + (qty * price)
                avg_price = round(total_cost / total_qty, 2) if total_qty > 0 else 0.0
                merged_items[sku] = {
                    "MaHH": sku,
                    "SoLuongNhap": total_qty,
                    "DonGiaNhap": avg_price,
                    "ThanhTien": total_cost
                }
            else:
                thanh_tien = round(qty * price, 2)
                merged_items[sku] = {
                    "MaHH": sku,
                    "SoLuongNhap": qty,
                    "DonGiaNhap": price,
                    "ThanhTien": thanh_tien
                }

        # 5. Kiểm tra tổng giá trị phiếu nhập kho bắt buộc > 0
        tong_tien_phieu = sum(it["ThanhTien"] for it in merged_items.values())
        if tong_tien_phieu <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tổng giá trị phiếu nhập kho phải lớn hơn 0 VNĐ."
            )

        # 6. Tạo Master PhieuNhap
        ma_pn = f"PN-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        phieu_nhap = PhieuNhap(
            MaPN=ma_pn,
            NgayNhap=utc_now(),
            MaNCC=ma_ncc,
            MaND=user_id,
            GhiChu=phieu_in.GhiChu or None,
            TongTien=tong_tien_phieu
        )
        db.add(phieu_nhap)
        db.flush()

        # 7. Xử lý Chi Tiết Phiếu Nhập, Cập Nhật Tồn Kho & Thẻ Kho
        for it_data in merged_items.values():
            ma_hh = it_data["MaHH"]
            sl_nhap = it_data["SoLuongNhap"]
            don_gia = it_data["DonGiaNhap"]
            thanh_tien = it_data["ThanhTien"]

            # Tạo chi tiết phiếu nhập
            ct = ChiTietPhieuNhap(
                MaPN=ma_pn,
                MaHH=ma_hh,
                SoLuongNhap=sl_nhap,
                DonGiaNhap=don_gia,
                ThanhTien=thanh_tien
            )
            db.add(ct)

            # Lấy số dư lũy kế gần nhất an toàn (chống null reference)
            latest_tk = (
                db.query(TheKho)
                .filter(TheKho.MaHH == ma_hh)
                .order_by(TheKho.NgayGiaoDich.desc(), TheKho.MaTK.desc())
                .first()
            )
            ton_kho = db.query(TonKho).filter(TonKho.MaHH == ma_hh).first()
            if latest_tk is not None and latest_tk.TonSauGiaoDich is not None:
                prev_ton = latest_tk.TonSauGiaoDich
            elif ton_kho is not None and ton_kho.SoLuongTon is not None:
                prev_ton = ton_kho.SoLuongTon
            else:
                prev_ton = 0

            ton_sau = prev_ton + sl_nhap

            # Cập nhật tồn kho an toàn
            if not ton_kho:
                ton_kho = TonKho(
                    MaHH=ma_hh,
                    SoLuongTon=ton_sau,
                    CapNhatCuoi=utc_now()
                )
                db.add(ton_kho)
                db.flush()
            else:
                stmt = (
                    update(TonKho)
                    .where(TonKho.MaHH == ma_hh)
                    .values(
                        SoLuongTon=ton_sau,
                        CapNhatCuoi=utc_now()
                    )
                )
                db.execute(stmt)
                db.flush()

            # Ghi sổ Thẻ kho lưu vết
            the_kho = TheKho(
                NgayGiaoDich=utc_now(),
                MaHH=ma_hh,
                MaChungTu=ma_pn,
                LoaiGiaoDich="NHAP",
                SoLuongThayDoi=sl_nhap,
                TonSauGiaoDich=ton_sau
            )
            db.add(the_kho)
            db.flush()

        db.commit()
        db.refresh(phieu_nhap)
        return phieu_nhap

    except IntegrityError as ie:
        db.rollback()
        err_orig = str(ie.orig) if hasattr(ie, "orig") else str(ie)
        err_lower = err_orig.lower()
        if "foreign key" in err_lower:
            detail_msg = "Lỗi toàn vẹn CSDL: Vi phạm ràng buộc khóa ngoại (Foreign Key constraint). Vui lòng kiểm tra lại Nhà Cung Cấp, Hàng Hóa hoặc Tài Khoản lập phiếu."
        elif "check" in err_lower:
            detail_msg = "Lỗi toàn vẹn CSDL: Vi phạm ràng buộc kiểm tra (Check constraint - Số lượng và Đơn giá phải lớn hơn 0)."
        elif "unique" in err_lower:
            detail_msg = "Lỗi toàn vẹn CSDL: Trùng lặp mã chứng từ hoặc khóa chính (Unique constraint)."
        else:
            detail_msg = f"Vi phạm ràng buộc toàn vẹn cơ sở dữ liệu: {err_orig}"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail_msg
        )
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi hệ thống khi xử lý giao dịch nhập kho: {str(e)}"
        )

