# app/services/inbound_service.py
import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.inventory_models import PhieuNhap, ChiTietPhieuNhap, TonKho, TheKho, HangHoa
from app.schemas.inventory_schemas import PhieuNhapCreate

def execute_inbound_transaction(db: Session, phieu_in: PhieuNhapCreate, user_id: int) -> PhieuNhap:
    """
    L?p phi?u nh?p kho Inbound trong 1 Database Transaction nguy?n t? (ACID):
    1. T?o Master PhieuNhap (M? t? sinh d?ng PN-YYYYMMDD-UUID).
    2. Duy?t t?ng ChiTietNhap, t?nh th?nh ti?n.
    3. Kh?a d?ng TonKho (SELECT FOR UPDATE) ?? t?ng SoLuongTon.
    4. Ghi v?t bi?n ??ng v?o TheKho (LoaiGiaoDich='NHAP', SoLuongThayDoi=+SL).
    5. Commit to?n v?n ho?c Rollback n?u c? l?i.
    """
    try:
        ma_pn = f"PN-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        phieu_nhap = PhieuNhap(
            MaPN=ma_pn,
            NgayNhap=datetime.utcnow(),
            MaNCC=phieu_in.MaNCC,
            MaND=user_id,
            GhiChu=phieu_in.GhiChu,
            TongTien=0.0
        )
        db.add(phieu_nhap)
        db.flush()  # T?o kh?a ch?nh tr??c ?? chi ti?t li?n k?t

        tong_tien_phieu = 0.0

        for item in phieu_in.items:
            # Ki?m tra h?ng h?a c? t?n t?i trong danh m?c kh?ng
            hh = db.query(HangHoa).filter(HangHoa.MaHH == item.MaHH).first()
            if not hh:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"M?t h?ng m? [{item.MaHH}] kh?ng t?n t?i trong danh m?c."
                )

            thanh_tien = item.SoLuongNhap * item.DonGiaNhap
            tong_tien_phieu += thanh_tien

            # T?o chi ti?t phi?u nh?p
            ct = ChiTietPhieuNhap(
                MaPN=ma_pn,
                MaHH=item.MaHH,
                SoLuongNhap=item.SoLuongNhap,
                DonGiaNhap=item.DonGiaNhap,
                ThanhTien=thanh_tien
            )
            db.add(ct)

            # Kh?a d?ng c?p nh?t t?n kho b?ng with_for_update()
            ton_kho = db.query(TonKho).filter(TonKho.MaHH == item.MaHH).with_for_update().first()
            if not ton_kho:
                ton_kho = TonKho(MaHH=item.MaHH, SoLuongTon=item.SoLuongNhap)
                db.add(ton_kho)
            else:
                ton_kho.SoLuongTon += item.SoLuongNhap

            db.flush()

            # Ghi s? Th? kho l?u v?t
            the_kho = TheKho(
                NgayGiaoDich=datetime.utcnow(),
                MaHH=item.MaHH,
                MaChungTu=ma_pn,
                LoaiGiaoDich="NHAP",
                SoLuongThayDoi=item.SoLuongNhap,
                TonSauGiaoDich=ton_kho.SoLuongTon
            )
            db.add(the_kho)

        phieu_nhap.TongTien = tong_tien_phieu
        db.commit()
        db.refresh(phieu_nhap)
        return phieu_nhap

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"L?i h? th?ng khi x? l? giao d?ch nh?p kho: {str(e)}"
        )
