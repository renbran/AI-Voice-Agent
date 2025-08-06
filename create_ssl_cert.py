"""
Generate self-signed SSL certificates for HTTPS mobile access
"""

from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import datetime
import ipaddress

def create_self_signed_cert():
    # Generate private key
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    
    # Create certificate
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "State"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "City"), 
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "James AI"),
        x509.NameAttribute(NameOID.COMMON_NAME, "192.168.0.161"),
    ])
    
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.datetime.utcnow()
    ).not_valid_after(
        datetime.datetime.utcnow() + datetime.timedelta(days=365)
    ).add_extension(
        x509.SubjectAlternativeName([
            x509.DNSName("localhost"),
            x509.IPAddress(ipaddress.IPv4Address("192.168.0.161")),
            x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
        ]),
        critical=False,
    ).sign(key, hashes.SHA256())
    
    # Write private key
    with open("key.pem", "wb") as f:
        f.write(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))
    
    # Write certificate
    with open("cert.pem", "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))
    
    print("✅ SSL certificates created: cert.pem and key.pem")

if __name__ == "__main__":
    create_self_signed_cert()
