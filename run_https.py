#!/usr/bin/env python3
"""Run FastAPI application with HTTPS"""

import uvicorn
import sys
from pathlib import Path

def generate_ssl_certificates():
    """Generate self-signed SSL certificates if they don't exist"""
    cert_dir = Path("certs")
    cert_file = cert_dir / "cert.pem"
    key_file = cert_dir / "key.pem"
    
    if cert_file.exists() and key_file.exists():
        return True
    
    print("📝 Generating SSL certificates for HTTPS...")
    try:
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.backends import default_backend
        from cryptography.hazmat.primitives.asymmetric import rsa
        import datetime
        
        # Generate private key
        key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        
        # Create certificate
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, u'localhost'),
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
                x509.DNSName(u'localhost'),
                x509.DNSName(u'127.0.0.1'),
            ]),
            critical=False,
        ).sign(key, hashes.SHA256(), default_backend())
        
        # Create certs directory
        cert_dir.mkdir(exist_ok=True)
        
        # Write certificate
        with open(cert_file, 'wb') as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        
        # Write private key
        with open(key_file, 'wb') as f:
            f.write(key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        print("✅ SSL certificates generated successfully!")
        print(f"   - {cert_file}")
        print(f"   - {key_file}\n")
        return True
        
    except ImportError as e:
        print(f"❌ Error: cryptography library not found")
        print(f"   Please run: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Error generating certificates: {e}")
        return False

def main():
    cert_file = Path("certs/cert.pem")
    key_file = Path("certs/key.pem")
    
    # Generate certificates BEFORE starting uvicorn
    if not generate_ssl_certificates():
        print("❌ Failed to generate SSL certificates. Exiting.")
        sys.exit(1)
    
    # Start uvicorn with HTTPS
    print("\n" + "="*60)
    print("🔒 Starting HTTPS Server")
    print("="*60)
    print(f"📍 Server: https://localhost:8000")
    print(f"📍 Docs:   https://localhost:8000/docs")
    print(f"📍 ReDoc:  https://localhost:8000/redoc")
    print("\n⚠️  Note: Self-signed certificate will trigger browser warnings")
    print("   This is normal for local development.")
    print("="*60 + "\n")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        ssl_keyfile=str(key_file),
        ssl_certfile=str(cert_file),
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()
