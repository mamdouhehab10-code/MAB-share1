#!/bin/bash

# MAB Share - Automated APK Build & Download
# ==========================================

set -e  # Exit on error

echo "════════════════════════════════════════"
echo "  🚀 MAB Share APK Builder"
echo "════════════════════════════════════════"
echo ""

# Check system requirements
echo "✓ Checking system requirements..."

if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Install from https://www.python.org/"
    exit 1
fi

if ! command -v java &> /dev/null; then
    echo "❌ Java not found. Install JDK 11+ from https://www.oracle.com/java/technologies/javase-downloads.html"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "  Python: $PYTHON_VERSION ✓"

JAVA_VERSION=$(java -version 2>&1 | head -n 1)
echo "  Java: $JAVA_VERSION ✓"

# Install/Update buildozer
echo ""
echo "✓ Installing buildozer and dependencies..."
pip install --upgrade buildozer cython

# Verify buildozer
if ! command -v buildozer &> /dev/null; then
    echo "❌ Buildozer installation failed"
    exit 1
fi

echo "  Buildozer: $(buildozer --version) ✓"

# Clean previous builds
echo ""
echo "✓ Cleaning previous builds..."
buildozer android clean || true

# Download/Update Android SDK if needed
echo ""
echo "✓ Preparing Android build environment..."
export BUILDOZER_LOG_LEVEL=2

# Build APK
echo ""
echo "✓ Building APK (this may take 5-15 minutes)..."
echo "  This includes downloading SDK, NDK, and dependencies..."
echo ""

buildozer android debug 2>&1 | tee build.log

# Check if build was successful
echo ""
if [ -f "bin/mabshare-1.0.0-debug.apk" ]; then
    echo "════════════════════════════════════════"
    echo "  ✅ APK BUILD SUCCESSFUL!"
    echo "════════════════════════════════════════"
    echo ""
    echo "📱 APK Location:"
    echo "   $(pwd)/bin/mabshare-1.0.0-debug.apk"
    echo ""
    echo "📊 APK Size:"
    ls -lh bin/mabshare-1.0.0-debug.apk | awk '{print "   " $5}'
    echo ""
    echo "📋 Next Steps:"
    echo "   1. Transfer APK to Android phone (USB or cloud)"
    echo "   2. Enable Settings > Security > Unknown Sources"
    echo "   3. Open APK file and tap Install"
    echo "   4. Launch MAB Share from app drawer"
    echo ""
    echo "🔗 Connection:"
    echo "   App will show URL and QR code"
    echo "   Open in browser: http://[phone-ip]:2010"
    echo ""
    
    # Optional: Try to open file manager
    if command -v xdg-open &> /dev/null; then
        xdg-open bin/ 2>/dev/null || true
    fi
else
    echo "════════════════════════════════════════"
    echo "  ❌ APK BUILD FAILED"
    echo "════════════════════════════════════════"
    echo ""
    echo "📋 Troubleshooting:"
    echo "   1. Check build.log for errors"
    echo "   2. Ensure Java/Android SDK is installed"
    echo "   3. Set JAVA_HOME if not set"
    echo "   4. Try: buildozer android debug -v"
    echo ""
    echo "📝 Build log saved to: build.log"
    exit 1
fi
