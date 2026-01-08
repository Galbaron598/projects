#!/bin/bash
set -e

echo "=== SundayApp Setup Script ==="
echo "[i] Checking Python..."

if ! command -v python3 &> /dev/null; then
    echo "[✗] Python3 not found. Please install Python 3.9+."
    exit 1
fi

echo "[✓] Python found: $(python3 --version)"

echo "[i] Checking pip..."

if ! command -v pip3 &> /dev/null; then
    echo "[✗] pip not found. Installing pip..."
    python3 -m ensurepip --default-pip
fi

echo "[✓] pip found: $(pip3 --version)"

echo "[i] Installing dependencies: fastapi, uvicorn..."
pip3 install --no-cache-dir fastapi uvicorn

echo "[✓] Dependencies installed!"

echo "=== Setup Complete ==="
