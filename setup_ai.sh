#!/bin/bash
# Astrologico AI Setup Script
# Installs AI features and configures the environment

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔════════════════════════════════════════╗"
echo "║   Astrologico AI Features Setup        ║"
echo "║   Version 2.0.0                        ║"
echo "╚════════════════════════════════════════╝"
echo -e "${NC}"

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${BLUE}Detected Python: ${python_version}${NC}"

# Check if venv exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating Python virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate venv
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Upgrade pip
echo -e "${YELLOW}Upgrading pip...${NC}"
pip install --upgrade pip setuptools wheel

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install -r requirements.txt

# Check for .env file
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo -e "${YELLOW}Creating .env file from template...${NC}"
        cp .env.example .env
        echo -e "${GREEN}✓ .env file created${NC}"
        echo -e "${YELLOW}Please edit .env and add your API keys:${NC}"
        echo -e "${BLUE}  - OPENAI_API_KEY (for GPT-4)${NC}"
        echo -e "${BLUE}  - ANTHROPIC_API_KEY (for Claude)${NC}"
    fi
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi

# Check installation
echo -e "${BLUE}Verifying installation...${NC}"

# Test imports
python3 -c "import fastapi; print(f'  FastAPI: OK')" 2>/dev/null && echo -e "${GREEN}✓ FastAPI installed${NC}" || echo -e "${RED}✗ FastAPI not found${NC}"
python3 -c "import astrologico; print('  Astrologico: OK')" 2>/dev/null && echo -e "${GREEN}✓ Astrologico module OK${NC}" || echo -e "${RED}✗ Astrologico module not found${NC}"

# Create necessary directories
mkdir -p ./data ./logs ./cache

# Display next steps
echo -e "\n${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   Installation Complete!               ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}\n"

echo -e "${BLUE}Next Steps:${NC}"
echo ""
echo "1. ${YELLOW}Configure API keys:${NC}"
echo "   ${BLUE}nano .env${NC}"
echo ""
echo "2. ${YELLOW}Start the API server:${NC}"
echo "   ${BLUE}python3 api_server.py${NC}"
echo ""
echo "3. ${YELLOW}Access the API:${NC}"
echo "   ${BLUE}http://localhost:8000/docs${NC}"
echo ""
echo "4. ${YELLOW}Use the CLI client:${NC}"
echo "   ${BLUE}python3 api_client.py status${NC}"
echo ""
echo "5. ${YELLOW}Test a chart generation:${NC}"
echo "   ${BLUE}python3 api_client.py chart --date \"2000-01-15 09:30:00\" --lat 40.7128 --lon -74.0060${NC}"
echo ""

echo -e "${BLUE}Documentation:${NC}"
echo "  - AI Features: ${BLUE}cat AI_FEATURES.md${NC}"
echo "  - Main README: ${BLUE}cat README.md${NC}"
echo "  - Configuration: ${BLUE}cat .env.example${NC}"
echo ""

echo -e "${GREEN}Happy Astrological Computing! 🌟${NC}\n"
