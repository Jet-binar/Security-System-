#!/bin/bash
# Installation script for Security System dependencies on Raspberry Pi

echo "Installing system dependencies..."
sudo apt update
sudo apt install -y \
    python3-pip \
    python3-venv \
    python3-picamera2 \
    cmake \
    build-essential \
    libopenblas-dev \
    liblapack-dev \
    python3-dev \
    python3-setuptools \
    libcap-dev \
    libjpeg-dev \
    zlib1g-dev

echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "Upgrading pip..."
pip install --upgrade pip

echo "Installing Python packages..."
echo "Note: This may take 10-30 minutes, especially for dlib..."

pip install -r requirements.txt

echo ""
echo "Installation complete!"
echo "To activate the virtual environment, run:"
echo "  source venv/bin/activate"

