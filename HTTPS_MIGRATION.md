# HTTPS Migration Guide

## Overview
Your FastAPI application has been migrated from HTTP to HTTPS for local development with self-signed SSL certificates.

## What Changed

### 1. **Auto-Generated SSL Certificates**
   - On first startup, the app automatically generates self-signed certificates
   - Certificates are stored in: `certs/cert.pem` and `certs/key.pem`
   - Certificates are valid for 1 year

### 2. **New Startup Script**
   - **Use this to run the app with HTTPS:**
     ```bash
     python run_https.py
     ```
   - The server will start on `https://localhost:8000`

### 3. **Updated main.py**
   - Added automatic SSL certificate generation on startup
   - No code changes needed in routers or middleware

## Running the Application

### Development (with HTTPS)
```bash
python run_https.py
```

### With Custom Port
Edit `run_https.py` and change the port number:
```python
uvicorn.run(..., port=8443, ...)
```

## Frontend Updates

### ✓ No Changes Required!
Your frontend code uses **relative URLs** (`/auth/login`, `/projects`, etc.), so:
- Frontend assets load correctly via HTTPS
- API calls automatically use HTTPS when accessed via HTTPS
- No hardcoded `http://` URLs need changing

### Example (Already Works)
```javascript
// This works with HTTPS automatically
const response = await fetch("/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password })
});
```

## Browser Security Warnings

When you first visit `https://localhost:8000`, you'll see a security warning:
- This is **normal** for self-signed certificates
- Click "Advanced" → "Proceed anyway" (or equivalent)
- The browser remembers your choice

## API Endpoints

All endpoints now use HTTPS:

| Endpoint | Example |
|----------|---------|
| Health Check | `https://localhost:8000/health` |
| API Docs | `https://localhost:8000/docs` |
| ReDoc | `https://localhost:8000/redoc` |
| Authentication | `https://localhost:8000/auth/login` |
| Projects | `https://localhost:8000/projects` |
| Users | `https://localhost:8000/users` |

## SSL Certificate Files

If you want to manually regenerate certificates:
```bash
python generate_certs.py
```

Or delete `certs/` folder and restart the app (it will regenerate automatically).

## Production Deployment

For production, replace the self-signed certificates with real SSL certificates from a certificate authority (Let's Encrypt, etc.) and update the SSL paths accordingly.

## Troubleshooting

### "Certificate verify failed" errors in tests
- Add `verify=False` to requests (not recommended for production)
- Or use the certificate file: `verify='certs/cert.pem'`

### Port 8000 already in use
- Edit `run_https.py` and change the port
- Or kill the process: `taskkill /IM python.exe` (Windows) or `lsof -ti:8000 | xargs kill` (Unix)

### Module 'cryptography' not found
- Install missing packages: `pip install -r requirements.txt`
- The cryptography library is already in requirements.txt
