#!/bin/bash
set -e

echo "🔧 Upgrading pip, setuptools, wheel, and build tools..."
pip install --upgrade pip setuptools wheel

echo "📦 Installing dependencies..."
# Install without build isolation to avoid maturin issues
pip install --no-build-isolation --no-cache-dir -r requirements.txt

echo "✅ Build complete!"

