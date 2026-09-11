# app/services/outbound_service.py
import uuid
from datetime import datetime
from sqlalchemy import update
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.models.inventory_models import PhieuXuat, ChiTietPhieuXuat, TonKho, TheKho, HangHoa
from app.schemas.inventory_schemas import PhieuXuatCreate
from app.core.datetime_utils import utc_now

def execute_outbound_transaction(db: Session, phieu_in: PhieuXuatCreate, user_id: int) -> PhieuXuat:
    """
    Lập phiếu xuất kho Outbound có cơ chế khóa nguyên tử (Atomic SQL Decrement):
    1. Tạo Master PhieuXuat (Mã tự sinh dạng PX-YYYYMMDD-UUID).
    2. Với mỗi dòng hàng:
       - Kiểm tra hàng hóa tồn tại trong danh mục.
       - Kiểm tra số dư tồn kho ban đầu.
       - Trừ tồn kho nguyên tử ở cấp CSDL (Atomic SQL Decrement với điều kiện SoLuongTon >= SoLuongXuat).
       - Nếu vi phạm (thiếu hàng / race condition), HỦY GIAO DỊCH (db.rollback) và trả về HTTP 400 Bad Request.
       - Nếu đủ hàng, ghi chi tiết xuất kho và sổ Thẻ kho (TheKho).
    3. Commit toàn vẹn (ACID All-or-Nothing).
    """
    try:
        ma_px = f"PX-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        phieu_xuat = PhieuXuat(
            MaPX=ma_px,
            NgayXuat=utc_now(),
            MaND=user_id,
            NguoiNhan=phieu_in.NguoiNhan,
            LyDoXuat=phieu_in.LyDoXuat
        )
        db.add(phieu_xuat)
        db.flush()

        for item in phieu_in.items:
            # Kiểm tra hàng hóa trong danh mục
            hh = db.query(HangHoa).filter(HangHoa.MaHH == item.MaHH).first()
            if not hh:
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Mặt hàng [{item.MaHH}] không tồn tại trong danh mục."
                )

            # Kiểm tra tồn kho có tồn tại không
            ton_kho_record = db.query(TonKho).filter(TonKho.MaHH == item.MaHH).first()
            if not ton_kho_record:
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Mặt hàng [{hh.TenHH}] chưa từng có số dư trong kho."
                )

            # THỰC HIỆN ATOMIC SQL DECREMENT CẤP CSDL CHỐNG RACE CONDITION
            # Câu lệnh UPDATE chỉ thành công khi SoLuongTon >= SoLuongXuat
            stmt = (
                update(TonKho)
                .where(TonKho.MaHH == item.MaHH, TonKho.SoLuongTon >= item.SoLuongXuat)
                .values(
                    SoLuongTon=TonKho.SoLuongTon - item.SoLuongXuat,
                    CapNhatCuoi=utc_now()
                )
            )
            result = db.execute(stmt)

            if result.rowcount == 0:
                db.rollback()
                # Truy vấn lại số tồn hiện thực tại thời điểm lỗi
                current_ton = db.query(TonKho.SoLuongTon).filter(TonKho.MaHH == item.MaHH).scalar()
                current_ton_val = current_ton if current_ton is not None else 0
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Mặt hàng [{hh.TenHH}] (Mã: {item.MaHH}) không đủ tồn kho để xuất. "
                        f"Tồn khả dụng trong kho: {current_ton_val}, "
                        f"Yêu cầu xuất: {item.SoLuongXuat}. "
                        f"Giao dịch bị hủy hoàn toàn (Rollback) để bảo vệ tính toàn vẹn CSDL."
                    )
                )

            # Lấy số tồn mới sau khi trừ để ghi sổ Thẻ kho
            new_ton = db.query(TonKho.SoLuongTon).filter(TonKho.MaHH == item.MaHH).scalar()

            # Tạo chi tiết xuất kho
            ct = ChiTietPhieuXuat(
                MaPX=ma_px,
                MaHH=item.MaHH,
                SoLuongXuat=item.SoLuongXuat
            )
            db.add(ct)
            db.flush()

            # Ghi Thẻ kho lưu vết biến động
            the_kho = TheKho(
                NgayGiaoDich=utc_now(),
                MaHH=item.MaHH,
                MaChungTu=ma_px,
                LoaiGiaoDich="XUAT",
                SoLuongThayDoi=-item.SoLuongXuat,
                TonSauGiaoDich=new_ton
            )
            db.add(the_kho)

        # Commit toàn bộ giao dịch nguyên tử
        db.commit()
        db.refresh(phieu_xuat)
        return phieu_xuat

    except IntegrityError as ie:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Vi phạm ràng buộc cơ sở dữ liệu (SoLuongTon >= 0): {str(ie.orig)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi hệ thống khi xử lý xuất kho: {str(e)}"
        )

