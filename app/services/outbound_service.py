# app/services/outbound_service.py
import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.models.inventory_models import PhieuXuat, ChiTietPhieuXuat, TonKho, TheKho, HangHoa
from app.schemas.inventory_schemas import PhieuXuatCreate

def execute_outbound_transaction(db: Session, phieu_in: PhieuXuatCreate, user_id: int) -> PhieuXuat:
    """
    L?p phi?u xu?t kho Outbound c? c? ch? kh?a bi quan (SELECT FOR UPDATE) ch?ng t?n kho ?m:
    1. T?o Master PhieuXuat (M? t? sinh d?ng PX-YYYYMMDD-UUID).
    2. V?i m?i d?ng h?ng:
       - Kh?a d?ng b?ng with_for_update() ?? ch?ng Race Condition khi nhi?u ng??i xu?t ??ng th?i.
       - Ki?m tra nghi?m ng?t: SoLuongTon >= SoLuongXuat.
       - N?u vi ph?m (thi?u h?ng), H?Y GIAO D?CH (db.rollback) v? tr? v? l?i HTTP 400 Bad Request.
       - N?u ?? h?ng, tr? t?n kho v? ghi s? Th? kho.
    3. Commit to?n v?n (ACID All-or-Nothing).
    """
    try:
        ma_px = f"PX-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        phieu_xuat = PhieuXuat(
            MaPX=ma_px,
            NgayXuat=datetime.utcnow(),
            MaND=user_id,
            NguoiNhan=phieu_in.NguoiNhan,
            LyDoXuat=phieu_in.LyDoXuat
        )
        db.add(phieu_xuat)
        db.flush()

        for item in phieu_in.items:
            # Ki?m tra h?ng h?a trong danh m?c
            hh = db.query(HangHoa).filter(HangHoa.MaHH == item.MaHH).first()
            if not hh:
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"M?t h?ng [{item.MaHH}] kh?ng t?n t?i trong danh m?c."
                )

            # KH?A BI QUAN C?P D?NG: with_for_update() -> SELECT ... FOR UPDATE tr?n PostgreSQL
            ton_kho = db.query(TonKho).filter(TonKho.MaHH == item.MaHH).with_for_update().first()

            if not ton_kho:
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"M?t h?ng [{hh.TenHH}] ch?a t?ng c? s? d? trong kho."
                )

            # KI?M TRA CH?NG T?N ?M NGHI?M NG?T
            if ton_kho.SoLuongTon < item.SoLuongXuat:
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"M?t h?ng [{hh.TenHH}] (M?: {item.MaHH}) kh?ng ?? t?n kho ?? xu?t. "
                        f"T?n kh? d?ng trong kho: {ton_kho.SoLuongTon}, "
                        f"Y?u c?u xu?t: {item.SoLuongXuat}. "
                        f"Giao d?ch b? h?y ho?n to?n (Rollback) ?? b?o v? t?nh to?n v?n CSDL."
                    )
                )

            # Tr? s? l??ng t?n kho
            ton_kho.SoLuongTon -= item.SoLuongXuat

            # T?o chi ti?t xu?t kho
            ct = ChiTietPhieuXuat(
                MaPX=ma_px,
                MaHH=item.MaHH,
                SoLuongXuat=item.SoLuongXuat
            )
            db.add(ct)
            db.flush()

            # Ghi Th? kho l?u v?t bi?n ??ng
            the_kho = TheKho(
                NgayGiaoDich=datetime.utcnow(),
                MaHH=item.MaHH,
                MaChungTu=ma_px,
                LoaiGiaoDich="XUAT",
                SoLuongThayDoi=-item.SoLuongXuat,
                TonSauGiaoDich=ton_kho.SoLuongTon
            )
            db.add(the_kho)

        # Commit to?n b?
        db.commit()
        db.refresh(phieu_xuat)
        return phieu_xuat

    except IntegrityError as ie:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Vi ph?m r?ng bu?c c? s? d? li?u (SoLuongTon >= 0): {str(ie.orig)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"L?i h? th?ng khi x? l? xu?t kho: {str(e)}"
        )
