#!/bin/bash
# Install script for Astrologico on Debian/Linux systems

set -e

echo "======================================================================"
echo "Astrologico Installation Script for Debian/Linux"
echo "======================================================================"
echo ""

# Check if running on Linux
if [[ ! "$OSTYPE" =~ ^linux ]]; then
    echo "Error: This script requires Linux. Your OS is: $OSTYPE"
    exit 1
fi

# Check Python 3.8+ available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python3 not found. Install with: sudo apt-get install python3"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
echo "✓ Python $PYTHON_VERSION detected"

# Install system dependencies
echo ""
echo "Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y python3-pip python3-dev build-essential python3-venv git 2>/dev/null || true

# Create installation directory
INSTALL_DIR="${INSTALL_DIR:=$HOME/astrologico}"
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

echo "✓ Installation directory: $INSTALL_DIR"

# Create virtual environment
echo ""
echo "Creating Python virtual environment..."
python3 -m venv venv 2>/dev/null || true
source venv/bin/activate

# Install Python packages
echo "Installing Python packages..."
pip install --upgrade pip setuptools wheel > /dev/null 2>&1
pip install skyfield PyMeeus ephem astropy numpy scipy > /dev/null 2>&1

echo "✓ Python packages installed"

# Create symbolic link for CLI access
echo ""
echo "Setting up command-line access..."
sudo ln -sf "$INSTALL_DIR/venv/bin/python3" /usr/local/bin/astrologico 2>/dev/null || true

# Create shell wrapper
sudo bash -c "cat > /usr/local/bin/astrologico << 'WRAPPER'
#!/bin/bash
cd $INSTALL_DIR
source venv/bin/activate
exec python3 cli.py \"\$@\"
WRAPPER
chmod +x /usr/local/bin/astrologico" 2>/dev/null || true

echo "✓ Installed: astrologico command"

# Summary
echo ""
echo "======================================================================"
echo "Installation Complete!"
echo "======================================================================"
echo ""
echo "Quick Start:"
echo "  astrologico chart --now"
echo "  astrologico planets --now --lat 51.5074 --lon -0.1278"
echo "  astrologico moon --now --json"
echo ""
echo "Documentation: $INSTALL_DIR/README.md"
echo "Virtual Environment: $INSTALL_DIR/venv"
echo ""
echo "For help: astrologico --help"
echo ""
