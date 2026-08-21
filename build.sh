#!/bin/bash

# MAB Share - APK Build Script
# ====================================

echo "🔨 MAB Share APK Build Script"
echo "===================================="

# Check if buildozer is installed
if ! command -v buildozer &> /dev/null; then
    echo "❌ buildozer is not installed"
    echo "Install with: pip install buildozer cython"
    exit 1
fi

# Check if Java SDK is installed
if [ -z "$JAVA_HOME" ]; then
    echo "⚠️  JAVA_HOME is not set"
    echo "Please install Java SDK and set JAVA_HOME"
    exit 1
fi

# Clean previous builds
echo "🧹 Cleaning previous builds..."
buildozer android clean

# Build the APK
echo "🏗️  Building APK (this may take 5-10 minutes)..."
buildozer android debug

# Check build result
if [ -f "bin/mabshare-1.0.0-debug.apk" ]; then
    echo ""
    echo "✅ APK Build Successful!"
    echo "📱 APK Location: bin/mabshare-1.0.0-debug.apk"
    echo ""
    echo "📋 Installation Instructions:"
    echo "1. Transfer APK to your Android phone"
    echo "2. Go to Settings > Security > Enable Unknown Sources"
    echo "3. Open the APK file and tap Install"
    echo ""
    echo "🚀 After installation:"
    echo "- Open MAB Share app"
    echo "- Use QR code or URL to connect from browser"
    echo "- Share files between devices on same network"
else
    echo ""
    echo "❌ APK Build Failed"
    echo "Check the build logs above for errors"
    exit 1
fi
