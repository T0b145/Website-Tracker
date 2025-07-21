#!/bin/bash

set -e

echo "[Website Tracker] Creating virtual environment..."
python3 -m venv venv

echo "[Website Tracker] Activating virtual environment..."
source venv/bin/activate

echo "[Website Tracker] Upgrading pip..."
pip install --upgrade pip

echo "[Website Tracker] Installing requirements..."
pip install -r requirements.txt

echo "[Website Tracker] Installing Playwright browser binaries..."
python -m playwright install

echo "[Website Tracker] Setup complete!"
echo "To activate the environment in the future, run:"
echo "source venv/bin/activate" 