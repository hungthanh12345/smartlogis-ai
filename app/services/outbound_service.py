# app/services/outbound_service.py
import uuid
from datetime import datetime
from sqlalchemy import update
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.models.inventory_models import PhieuXuat, ChiTietPhieuXuat, TonKho, TheKho, HangHoa, NguoiDung
from app.schemas.inventory_schemas import PhieuXuatCreate
from app.core.datetime_utils import utc_now

def execute_outbound_transaction(db: Session, phieu_in: PhieuXuatCreate, user_id: int) -> PhieuXuat:
    """
    Lập phiếu xuất kho Outbound có cơ chế khóa nguyên tử (Atomic SQL Decrement):
    1. Kiểm tra tính hợp lệ của Người dùng và Người nhận.
    2. Với mỗi dòng hàng:
       - Kiểm tra hàng hóa tồn tại trong danh mục (Khóa ngoại).
       - Kiểm tra số dư tồn kho ban đầu.
       - Trừ tồn kho nguyên tử ở cấp CSDL (Atomic SQL Decrement với điều kiện SoLuongTon >= SoLuongXuat).
       - Nếu vi phạm (thiếu hàng / race condition), HỦY GIAO DỊCH (db.rollback) và trả về HTTP 400 Bad Request.
       - Nếu đủ hàng, ghi chi tiết xuất kho và sổ Thẻ kho (TheKho).
    3. Commit toàn vẹn (ACID All-or-Nothing).
    """
    try:
        # 1. Kiểm tra khóa ngoại Người dùng (MaND)
        user = db.query(NguoiDung).filter(NguoiDung.MaND == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tài khoản người dùng (MaND={user_id}) không tồn tại trong hệ thống. Vui lòng đăng nhập lại."
            )

        # 2. Kiểm tra thông tin người nhận
        if not phieu_in.NguoiNhan or not phieu_in.NguoiNhan.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tên người hoặc đơn vị nhận hàng không được để trống."
            )

        # 3. Kiểm tra danh sách mặt hàng
        if not phieu_in.items or len(phieu_in.items) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phiếu xuất kho phải chứa ít nhất 1 mặt hàng."
            )

        ma_px = phieu_in.MaPX.strip().upper() if getattr(phieu_in, 'MaPX', None) and phieu_in.MaPX.strip() and phieu_in.MaPX.strip().upper() != "PX-TỰ-ĐỘNG-TẠO" else f"PX-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        phieu_xuat = PhieuXuat(
            MaPX=ma_px,
            NgayXuat=utc_now(),
            MaND=user_id,
            NguoiNhan=phieu_in.NguoiNhan.strip(),
            LyDoXuat=phieu_in.LyDoXuat.strip() if phieu_in.LyDoXuat else None
        )
        db.add(phieu_xuat)
        db.flush()

        # 4. Thẩm định và gom nhóm tổng số lượng xuất theo từng SKU
        merged_items = {}
        for item in phieu_in.items:
            if not item.MaHH or not item.MaHH.strip():
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Mã hàng hóa trong chi tiết phiếu xuất không được để trống."
                )

            sku = item.MaHH.strip()
            if item.SoLuongXuat is None or item.SoLuongXuat <= 0:
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Số lượng xuất của mặt hàng [{sku}] phải lớn hơn 0 (hiện tại: {item.SoLuongXuat})."
                )

            hh = db.query(HangHoa).filter(HangHoa.MaHH == sku).first()
            if not hh:
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Mặt hàng [{sku}] không tồn tại trong danh mục hàng hóa (vi phạm ràng buộc khóa ngoại)."
                )

            merged_items[sku] = merged_items.get(sku, 0) + item.SoLuongXuat

        if sum(merged_items.values()) <= 0:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tổng số lượng hàng xuất kho phải lớn hơn 0."
            )

        # 2. Xử lý trừ kho nguyên tử và ghi sổ theo từng SKU duy nhất
        for ma_hh, total_xuat in merged_items.items():
            hh = db.query(HangHoa).filter(HangHoa.MaHH == ma_hh).first()
            ton_kho_record = db.query(TonKho).filter(TonKho.MaHH == ma_hh).first()
            if not ton_kho_record:
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Mặt hàng [{hh.TenHH}] chưa từng có số dư trong kho."
                )

            # Lấy số dư lũy kế gần nhất từ Thẻ kho (hoặc Tồn kho hiện có)
            latest_tk = (
                db.query(TheKho)
                .filter(TheKho.MaHH == ma_hh)
                .order_by(TheKho.NgayGiaoDich.desc(), TheKho.MaTK.desc())
                .first()
            )
            if latest_tk is not None:
                current_balance = latest_tk.TonSauGiaoDich
            else:
                current_balance = ton_kho_record.SoLuongTon

            if current_balance < total_xuat:
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Mặt hàng [{hh.TenHH}] (Mã: {ma_hh}) không đủ tồn kho để xuất. "
                        f"Tồn khả dụng trong kho: {current_balance}, "
                        f"Yêu cầu xuất: {total_xuat}. "
                        f"Giao dịch bị hủy hoàn toàn (Rollback) để bảo vệ tính toàn vẹn CSDL."
                    )
                )

            new_ton = current_balance - total_xuat

            # THỰC HIỆN ATOMIC SQL DECREMENT CẤP CSDL CHỐNG RACE CONDITION
            stmt = (
                update(TonKho)
                .where(TonKho.MaHH == ma_hh, TonKho.SoLuongTon >= total_xuat)
                .values(
                    SoLuongTon=new_ton,
                    CapNhatCuoi=utc_now()
                )
            )
            result = db.execute(stmt)

            if result.rowcount == 0:
                if ton_kho_record.SoLuongTon < total_xuat:
                    db.rollback()
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=(
                            f"Mặt hàng [{hh.TenHH}] (Mã: {ma_hh}) không đủ tồn kho để xuất. "
                            f"Tồn khả dụng trong kho: {ton_kho_record.SoLuongTon}, "
                            f"Yêu cầu xuất: {total_xuat}. "
                            f"Giao dịch bị hủy hoàn toàn (Rollback) để bảo vệ tính toàn vẹn CSDL."
                        )
                    )
                ton_kho_record.SoLuongTon = new_ton
                ton_kho_record.CapNhatCuoi = utc_now()
                db.flush()

            # Tạo chi tiết xuất kho
            ct = ChiTietPhieuXuat(
                MaPX=ma_px,
                MaHH=ma_hh,
                SoLuongXuat=total_xuat
            )
            db.add(ct)
            db.flush()

            # Ghi Thẻ kho lưu vết biến động với số dư lũy kế chính xác
            the_kho = TheKho(
                NgayGiaoDich=utc_now(),
                MaHH=ma_hh,
                MaChungTu=ma_px,
                LoaiGiaoDich="XUAT",
                SoLuongThayDoi=-total_xuat,
                TonSauGiaoDich=new_ton
            )
            db.add(the_kho)
            db.flush()

        # Commit toàn bộ giao dịch nguyên tử
        db.commit()
        db.refresh(phieu_xuat)
        return phieu_xuat

    except IntegrityError as ie:
        db.rollback()
        err_orig = str(ie.orig) if hasattr(ie, "orig") else str(ie)
        err_lower = err_orig.lower()
        if "foreign key" in err_lower:
            detail_msg = "Lỗi toàn vẹn CSDL: Vi phạm ràng buộc khóa ngoại (Foreign Key constraint). Vui lòng kiểm tra lại Hàng Hóa hoặc Tài Khoản lập phiếu."
        elif "check" in err_lower or "soluongton" in err_lower:
            detail_msg = "Lỗi toàn vẹn CSDL: Vi phạm ràng buộc số lượng tồn (Check constraint: Số lượng tồn không được âm)."
        else:
            detail_msg = f"Vi phạm ràng buộc cơ sở dữ liệu: {err_orig}"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail_msg
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi hệ thống khi xử lý xuất kho: {str(e)}"
        )

