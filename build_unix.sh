#!/bin/bash
# Build Bongo Cat for Linux/macOS

echo "================================================"
echo "Bongo Cat Unix Build Script"
echo "================================================"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 not found!"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

# Make build.py executable
chmod +x build.py

# Run build script
python3 build.py

echo ""
echo "Build complete! Check the dist folder."
