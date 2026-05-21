# HTTPS Migration - Implementation Details

## Architecture Overview

### Before Migration
```
Client → HTTP:8000 → FastAPI App
         (Unencrypted)
```

### After Migration
```
Client → HTTPS:8000 → FastAPI App (with SSL/TLS)
         (Encrypted)
```

## Components

### 1. SSL Certificate Generation (`main.py`)
The `ensure_ssl_certificates()` function:
- Checks if certificates exist on startup
- Auto-generates self-signed certificates if missing
- Uses 2048-bit RSA encryption
- Certificates are stored in `certs/` directory
- Valid for 365 days

**Key Technologies:**
- `cryptography` library (already in requirements.txt)
- X.509 certificate standard
- SHA-256 hashing

### 2. HTTPS Server Launcher (`run_https.py`)
Starts uvicorn with SSL configuration:
```python
uvicorn.run(
    "main:app",
    host="0.0.0.0",
    port=8000,
    ssl_keyfile="certs/key.pem",
    ssl_certfile="certs/cert.pem",
    reload=True
)
```

**Features:**
- SSL/TLS enabled via uvicorn
- Auto-reload for development
- Pretty startup messages
- Port customizable

### 3. Cross-Platform Launchers
- `run_https.bat` - Windows batch script
- `run_https.sh` - Unix/Linux/macOS shell script
- Both auto-generate certificates before starting server

## Security Considerations

### Self-Signed Certificates
✅ **Pros:**
- Perfect for local development
- Zero cost
- No manual installation needed
- Auto-generated on first run

⚠️ **Cons:**
- Browsers show security warnings
- Cannot be verified by certificate authorities
- Not suitable for production

### Production Deployment
For production, replace certificates with:
1. **Let's Encrypt** (free, automated)
2. **Commercial CAs** (GoDaddy, DigiCert, etc.)
3. **Internal CAs** (for enterprise)

Update `run_https.py` to point to production certificates:
```python
ssl_keyfile="path/to/production/key.pem"
ssl_certfile="path/to/production/cert.pem"
```

## API Compatibility

### ✅ No Breaking Changes
All existing API endpoints work with HTTPS:

| Endpoint | Status |
|----------|--------|
| `POST /auth/login` | ✅ Works |
| `GET /projects` | ✅ Works |
| `GET /users` | ✅ Works |
| `/static/*` | ✅ Works |
| `/health` | ✅ Works |

### ✅ No Frontend Changes Required
Frontend uses relative URLs - automatically compatible:
```javascript
// Works with HTTP and HTTPS
fetch("/auth/login", {...})
fetch("/projects", {...})
```

## Testing HTTPS

### Browser Testing
1. Run: `python run_https.py`
2. Visit: `https://localhost:8000`
3. Click "Advanced" → "Proceed anyway" (or equivalent)

### Command Line Testing
```bash
# Ignore certificate verification
curl -k https://localhost:8000/health

# With certificate verification
curl --cacert certs/cert.pem https://localhost:8000/health

# Python requests
import requests
requests.get("https://localhost:8000/health", verify=False)  # Skip cert check
requests.get("https://localhost:8000/health", verify="certs/cert.pem")  # Use cert
```

### Automated Testing
```python
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Suppress warnings for testing
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

response = requests.get("https://localhost:8000/health", verify=False)
```

## Troubleshooting

### Certificate Issues

**Problem:** `ssl.SSLError: [Errno 1] _ssl.c:1020: error:...`
```bash
# Solution: Delete and regenerate
rm -rf certs
python run_https.py
```

**Problem:** `FileNotFoundError: [Errno 2] No such file or directory: 'certs/cert.pem'`
```bash
# Solution: Run certificate generator
python generate_certs.py
```

### Port Issues

**Problem:** `Address already in use` on port 8000
```bash
# Find process using port (Windows)
netstat -ano | findstr :8000

# Kill process
taskkill /PID <PID> /F

# Or use different port - edit run_https.py
# Change: port=8000 → port=8443
```

### Import Issues

**Problem:** `ModuleNotFoundError: No module named 'cryptography'`
```bash
# Solution: Install dependencies
pip install -r requirements.txt
```

## File Permissions

### Windows
- `.bat` files run directly
- `run_https.py` run with `python run_https.py`

### macOS/Linux
```bash
# Make shell script executable (one-time)
chmod +x run_https.sh

# Then run
./run_https.sh
```

## Docker Deployment

### Dockerfile Example
```dockerfile
FROM python:3.11

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Generate certificates
RUN python generate_certs.py

# Run with HTTPS
CMD ["python", "run_https.py"]
```

### Docker Compose Example
```yaml
version: '3'
services:
  app:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./certs:/app/certs
    environment:
      - PYTHONUNBUFFERED=1
```

## Environment Variables

Optional configuration (can be added to `.env`):

```env
# HTTPS Configuration
HTTPS_PORT=8000
HTTPS_HOST=0.0.0.0
SSL_KEYFILE=certs/key.pem
SSL_CERTFILE=certs/cert.pem
```

Then update `run_https.py` to read from environment:
```python
import os
port = int(os.getenv("HTTPS_PORT", 8000))
```

## Migration Rollback

To revert to HTTP (not recommended for security):

1. **Stop HTTPS server**
2. **Run standard uvicorn:**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

3. **Remove HTTPS files (optional):**
```bash
rm run_https.py run_https.bat run_https.sh generate_certs.py
rm -rf certs
```

## Monitoring & Logging

### Enable Debug Logging
Edit `run_https.py`:
```python
uvicorn.run(..., log_level="debug")
```

### Monitor Certificate Expiration
```bash
# Check certificate expiration (OpenSSL)
openssl x509 -in certs/cert.pem -noout -dates
```

### Automated Renewal (Future)
For production Let's Encrypt setup:
```bash
# Using certbot
certbot certonly --standalone -d yourdomain.com
```

---

## References
- [Uvicorn SSL Configuration](https://www.uvicorn.org/)
- [cryptography.io Documentation](https://cryptography.io/)
- [Let's Encrypt](https://letsencrypt.org/)
- [Mozilla SSL Configuration](https://ssl-config.mozilla.org/)
