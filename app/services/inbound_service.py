# app/services/inbound_service.py
import uuid
from datetime import datetime
from sqlalchemy import update
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.models.inventory_models import PhieuNhap, ChiTietPhieuNhap, TonKho, TheKho, HangHoa, NhaCungCap
from app.schemas.inventory_schemas import PhieuNhapCreate

def execute_inbound_transaction(db: Session, phieu_in: PhieuNhapCreate, user_id: int) -> PhieuNhap:
    """
    Lập phiếu nhập kho Inbound trong 1 Database Transaction nguyên tử (ACID):
    1. Kiểm tra nhà cung cấp tồn tại trong hệ thống.
    2. Tạo Master PhieuNhap (Mã tự sinh dạng PN-YYYYMMDD-UUID).
    3. Duyệt từng ChiTietNhap, tính thành tiền.
    4. Cập nhật tăng SoLuongTon một cách an toàn (khởi tạo hoặc cộng dồn).
    5. Ghi vết biến động vào TheKho (LoaiGiaoDich='NHAP', SoLuongThayDoi=+SL).
    6. Commit toàn vẹn hoặc Rollback nếu có bất kỳ lỗi nào.
    """
    try:
        # Kiểm tra nhà cung cấp
        ncc = db.query(NhaCungCap).filter(NhaCungCap.MaNCC == phieu_in.MaNCC).first()
        if not ncc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Nhà cung cấp [{phieu_in.MaNCC}] không tồn tại trong hệ thống."
            )

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
        db.flush()  # Tạo khóa chính trước để chi tiết liên kết

        tong_tien_phieu = 0.0

        for item in phieu_in.items:
            # Kiểm tra hàng hóa có tồn tại trong danh mục không
            hh = db.query(HangHoa).filter(HangHoa.MaHH == item.MaHH).first()
            if not hh:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Mặt hàng mã [{item.MaHH}] không tồn tại trong danh mục."
                )

            thanh_tien = item.SoLuongNhap * item.DonGiaNhap
            tong_tien_phieu += thanh_tien

            # Tạo chi tiết phiếu nhập
            ct = ChiTietPhieuNhap(
                MaPN=ma_pn,
                MaHH=item.MaHH,
                SoLuongNhap=item.SoLuongNhap,
                DonGiaNhap=item.DonGiaNhap,
                ThanhTien=thanh_tien
            )
            db.add(ct)

            # Cập nhật tồn kho an toàn
            ton_kho = db.query(TonKho).filter(TonKho.MaHH == item.MaHH).first()
            if not ton_kho:
                ton_kho = TonKho(
                    MaHH=item.MaHH,
                    SoLuongTon=item.SoLuongNhap,
                    CapNhatCuoi=datetime.utcnow()
                )
                db.add(ton_kho)
                db.flush()
                ton_sau = item.SoLuongNhap
            else:
                stmt = (
                    update(TonKho)
                    .where(TonKho.MaHH == item.MaHH)
                    .values(
                        SoLuongTon=TonKho.SoLuongTon + item.SoLuongNhap,
                        CapNhatCuoi=datetime.utcnow()
                    )
                )
                db.execute(stmt)
                db.flush()
                ton_sau = db.query(TonKho.SoLuongTon).filter(TonKho.MaHH == item.MaHH).scalar()

            # Ghi sổ Thẻ kho lưu vết
            the_kho = TheKho(
                NgayGiaoDich=datetime.utcnow(),
                MaHH=item.MaHH,
                MaChungTu=ma_pn,
                LoaiGiaoDich="NHAP",
                SoLuongThayDoi=item.SoLuongNhap,
                TonSauGiaoDich=ton_sau
            )
            db.add(the_kho)

        phieu_nhap.TongTien = tong_tien_phieu
        db.commit()
        db.refresh(phieu_nhap)
        return phieu_nhap

    except IntegrityError as ie:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Vi phạm ràng buộc toàn vẹn cơ sở dữ liệu: {str(ie.orig)}"
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

