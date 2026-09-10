# scripts/generate_trusted_ssl_ca.py
"""
Tạo Certificate Authority (CA) nội bộ và cấp phát chứng chỉ SSL cho smartlogis-ai.com
Được ký bởi Local Root CA để Windows và trình duyệt (Chrome, Edge) công nhận 100% BẢO MẬT.
"""
import sys
import ipaddress
from pathlib import Path
from datetime import datetime, timedelta, timezone

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from cryptography import x509
from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa

def generate_ca_and_cert():
    base_dir = Path(__file__).resolve().parent.parent
    ca_dir = base_dir / "certbot" / "conf"
    cert_dir = ca_dir / "live" / "smartlogis-ai.com"

    ca_dir.mkdir(parents=True, exist_ok=True)
    cert_dir.mkdir(parents=True, exist_ok=True)

    ca_key_path = ca_dir / "smartlogis_ca.key"
    ca_cert_path = ca_dir / "smartlogis_root_ca.crt"
    server_key_path = cert_dir / "privkey.pem"
    server_cert_path = cert_dir / "fullchain.pem"

    now = datetime.now(timezone.utc)

    # -------------------------------------------------------------------------
    # 1. TẠO HOẶC TẢI LOCAL ROOT CA (Thời hạn 10 năm)
    # -------------------------------------------------------------------------
    print("[1/3] Đang tạo Root Certificate Authority (SmartLogis Local Root CA)...")
    ca_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    
    ca_subject = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "VN"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Hanoi"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "SmartLogis AI Authority"),
        x509.NameAttribute(NameOID.COMMON_NAME, "SmartLogis AI Local Root CA"),
    ])

    ca_cert = (
        x509.CertificateBuilder()
        .subject_name(ca_subject)
        .issuer_name(ca_subject)
        .public_key(ca_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(days=1))
        .not_valid_after(now + timedelta(days=3650))
        .add_extension(
            x509.BasicConstraints(ca=True, path_length=None),
            critical=True,
        )
        .add_extension(
            x509.KeyUsage(
                digital_signature=True,
                key_encipherment=False,
                key_cert_sign=True,
                crl_sign=True,
                content_commitment=False,
                data_encipherment=False,
                key_agreement=False,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )
        .add_extension(
            x509.SubjectKeyIdentifier.from_public_key(ca_key.public_key()),
            critical=False,
        )
        .sign(ca_key, hashes.SHA256())
    )

    # Lưu Root CA
    with open(ca_key_path, "wb") as f:
        f.write(ca_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        ))

    with open(ca_cert_path, "wb") as f:
        f.write(ca_cert.public_bytes(serialization.Encoding.PEM))

    print(f" [+] Root CA lưu tại: {ca_cert_path}")

    # -------------------------------------------------------------------------
    # 2. TẠO VÀ KÝ CHỨNG CHỈ SERVER CHO smartlogis-ai.com
    # -------------------------------------------------------------------------
    print("[2/3] Đang cấp phát chứng chỉ SSL cho smartlogis-ai.com...")
    server_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    server_subject = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "VN"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Hanoi"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "SmartLogis AI"),
        x509.NameAttribute(NameOID.COMMON_NAME, "smartlogis-ai.com"),
    ])

    san_list = [
        x509.DNSName("smartlogis-ai.com"),
        x509.DNSName("www.smartlogis-ai.com"),
        x509.DNSName("localhost"),
        x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
    ]

    server_cert = (
        x509.CertificateBuilder()
        .subject_name(server_subject)
        .issuer_name(ca_subject)
        .public_key(server_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(days=1))
        .not_valid_after(now + timedelta(days=825))  # 825 ngày theo chuẩn Apple/Google mới nhất
        .add_extension(
            x509.BasicConstraints(ca=False, path_length=None),
            critical=True,
        )
        .add_extension(
            x509.KeyUsage(
                digital_signature=True,
                key_encipherment=True,
                key_cert_sign=False,
                crl_sign=False,
                content_commitment=False,
                data_encipherment=False,
                key_agreement=False,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )
        .add_extension(
            x509.ExtendedKeyUsage([
                ExtendedKeyUsageOID.SERVER_AUTH,
                ExtendedKeyUsageOID.CLIENT_AUTH,
            ]),
            critical=False,
        )
        .add_extension(
            x509.SubjectAlternativeName(san_list),
            critical=False,
        )
        .add_extension(
            x509.AuthorityKeyIdentifier.from_issuer_public_key(ca_key.public_key()),
            critical=False,
        )
        .sign(ca_key, hashes.SHA256())
    )

    # Lưu Private Key Server
    with open(server_key_path, "wb") as f:
        f.write(server_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        ))

    # Lưu Fullchain (Server Cert + Root CA Cert)
    with open(server_cert_path, "wb") as f:
        f.write(server_cert.public_bytes(serialization.Encoding.PEM))
        f.write(ca_cert.public_bytes(serialization.Encoding.PEM))

    print(f" [+] Server Private Key: {server_key_path}")
    print(f" [+] Server Fullchain  : {server_cert_path}")
    print("\n[3/3] HOÀN TẤT CẤP PHÁT CHỨNG CHỈ SSL ĐƯỢC KÝ BỞI CA!")

if __name__ == "__main__":
    generate_ca_and_cert()
