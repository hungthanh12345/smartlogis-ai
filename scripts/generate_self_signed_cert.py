# scripts/generate_self_signed_cert.py
"""
Script sinh chứng chỉ SSL tự ký (Self-Signed Certificate) cho tên miền smartlogis-ai.com
Phục vụ chạy thử nghiệm Nginx Reverse Proxy trên môi trường Local / Staging
khi chưa trỏ DNS Internet hoặc trước khi Certbot cấp phát chứng chỉ Let's Encrypt thật.
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta, timezone

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

def generate_self_signed_cert(domain: str = "smartlogis-ai.com"):
    out_dir = Path(__file__).resolve().parent.parent / "certbot" / "conf" / "live" / domain
    out_dir.mkdir(parents=True, exist_ok=True)

    privkey_path = out_dir / "privkey.pem"
    fullchain_path = out_dir / "fullchain.pem"

    if privkey_path.exists() and fullchain_path.exists():
        print(f"[INFO] Cặp chứng chỉ SSL đã tồn tại tại: {out_dir}")
        return

    print(f"[INFO] Đang tạo chứng chỉ SSL tự ký cho domain: {domain}...")

    # 1. Tạo Private Key RSA 2048-bit
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    # 2. Xây dựng X.509 Certificate
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "VN"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Hanoi"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "SmartLogis AI"),
        x509.NameAttribute(NameOID.COMMON_NAME, domain),
    ])

    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.now(timezone.utc))
        .not_valid_after(datetime.now(timezone.utc) + timedelta(days=365))
        .add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName(domain),
                x509.DNSName(f"www.{domain}"),
                x509.DNSName("localhost")
            ]),
            critical=False,
        )
        .sign(key, hashes.SHA256())
    )

    # 3. Ghi ra file pem
    with open(privkey_path, "wb") as f:
        f.write(
            key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )

    with open(fullchain_path, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

    print(f"[SUCCESS] Đã sinh thành công cặp chứng chỉ SSL:")
    print(f" - Private Key: {privkey_path}")
    print(f" - Fullchain  : {fullchain_path}")

if __name__ == "__main__":
    generate_self_signed_cert()
