from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from routers import auth, projects, users
from database.connection import engine
from database.models import Base
import os
import sys
from pathlib import Path

# Ensure SSL certificates exist
def ensure_ssl_certificates():
    cert_dir = Path("certs")
    cert_file = cert_dir / "cert.pem"
    key_file = cert_dir / "key.pem"
    
    if not cert_file.exists() or not key_file.exists():
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
            
            print("✓ SSL certificates generated successfully!")
            print(f"  - {cert_file}")
            print(f"  - {key_file}")
        except ImportError:
            print("⚠️  Warning: cryptography library not found")
            print("   SSL certificates will not be auto-generated")
            return False
    return True

# Generate certificates on startup
ensure_ssl_certificates()

# Create all tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="DRDO CABS Project Management System",
    description="Secure internal project data management with full audit trail",
    version="1.0.0"
)

@app.middleware("http")
async def add_no_cache_headers(request: Request, call_next):
    response = await call_next(request)
    
    # Prevent caching for all HTML and API responses
    if request.url.path.endswith('.html') or request.url.path.startswith('/static') or request.url.path.startswith('/projects') or request.url.path.startswith('/auth'):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    
    return response

# Routers
app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(users.router)

# Serve frontend
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
def serve_frontend():
    return FileResponse("frontend/index.html")

@app.get("/health")
def health_check():
    return {"status": "ok", "system": "DRDO CABS Project Management"}