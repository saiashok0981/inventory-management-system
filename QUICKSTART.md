# 🔒 HTTP to HTTPS Migration - Quick Start

## What's New?
Your application is now running on **HTTPS** with auto-generated SSL certificates for secure local development.

## Quick Start

### Windows Users
**Double-click:** `run_https.bat`

Or from command prompt:
```cmd
python run_https.py
```

### macOS/Linux Users
```bash
chmod +x run_https.sh
./run_https.sh
```

Or directly with Python:
```bash
python run_https.py
```

## First Run
1. Run the startup script above
2. SSL certificates will auto-generate on first startup
3. Server starts at `https://localhost:8000`
4. Open in browser - ignore the SSL warning (self-signed certificate)

## Access Points
- **Web App:** https://localhost:8000
- **API Docs:** https://localhost:8000/docs
- **ReDoc:** https://localhost:8000/redoc

## Important Notes

✅ **Your frontend code needs NO changes**
- All relative URLs (`/auth/login`, etc.) work automatically with HTTPS
- API calls use HTTPS when accessed via HTTPS

⚠️ **SSL Certificate Warning**
- Self-signed certificates trigger browser warnings
- This is **expected and normal** for local development
- In production, use real certificates from Let's Encrypt or similar

🔐 **Certificates Location**
- `certs/cert.pem` - SSL certificate
- `certs/key.pem` - Private key
- Valid for 1 year

## Files Added/Modified

### New Files
- `run_https.py` - Start server with HTTPS
- `run_https.bat` - Windows batch script
- `run_https.sh` - Unix/Linux/macOS script
- `generate_certs.py` - Certificate generator (backup)
- `HTTPS_MIGRATION.md` - Detailed migration guide

### Modified Files
- `main.py` - Added automatic certificate generation

## Regenerate Certificates

If needed, regenerate certificates:

```bash
# Option 1: Auto-regenerate (delete certs folder first)
rm -rf certs
python run_https.py

# Option 2: Use generator script
python generate_certs.py
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Port 8000 already in use | Edit `run_https.py`, change `port=8000` to another port |
| "Certificate not found" error | Run `python generate_certs.py` |
| "Permission denied" on `.sh` | Run `chmod +x run_https.sh` first |
| ModuleNotFoundError: cryptography | Run `pip install -r requirements.txt` |

## Testing with curl

```bash
# Test with self-signed certificate (ignore warnings)
curl -k https://localhost:8000/health

# Test with certificate verification
curl --cacert certs/cert.pem https://localhost:8000/health
```

## More Information
See `HTTPS_MIGRATION.md` for detailed documentation.
