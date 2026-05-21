#!/bin/bash
# Run HTTPS Server - Unix/Linux/macOS Script

echo ""
echo "============================================================"
echo "Checking Python installation..."
echo "============================================================"

if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "Error: Python is not installed"
    exit 1
fi

PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

echo ""
echo "============================================================"
echo "Starting HTTPS Server..."
echo "============================================================"
echo ""
echo "Server URL: https://localhost:8000"
echo "Docs:       https://localhost:8000/docs"
echo "ReDoc:      https://localhost:8000/redoc"
echo ""
echo "Note: You may see SSL certificate warnings - this is normal"
echo "      for self-signed certificates in local development."
echo ""

$PYTHON_CMD run_https.py

