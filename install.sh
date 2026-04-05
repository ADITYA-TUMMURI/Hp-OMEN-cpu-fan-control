#!/bin/bash

# HP OMEN CPU Fan Control - Installer
# https://github.com/ADITYA-TUMMURI/Hp-OMEN-cpu-fan-control

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

USER=$(whoami)
HOME_DIR=$(eval echo ~$USER)

echo -e "${CYAN}"
echo "  ██╗  ██╗██████╗      ██████╗ ███╗   ███╗███████╗███╗   ██╗"
echo "  ██║  ██║██╔══██╗    ██╔═══██╗████╗ ████║██╔════╝████╗  ██║"
echo "  ███████║██████╔╝    ██║   ██║██╔████╔██║█████╗  ██╔██╗ ██║"
echo "  ██╔══██║██╔═══╝     ██║   ██║██║╚██╔╝██║██╔══╝  ██║╚██╗██║"
echo "  ██║  ██║██║         ╚██████╔╝██║ ╚═╝ ██║███████╗██║ ╚████║"
echo "  ╚═╝  ╚═╝╚═╝          ╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═══╝"
echo -e "${NC}"
echo -e "${CYAN}  CPU Fan Control for HP OMEN Laptops on Linux${NC}"
echo -e "${YELLOW}  github.com/ADITYA-TUMMURI/Hp-OMEN-cpu-fan-control${NC}"
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo -e "${RED}Do not run this script as root. Run as your normal user.${NC}"
    exit 1
fi

echo -e "${GREEN}[1/7] Installing dependencies...${NC}"
sudo dnf install -y git cmake autoconf automake libtool libcurl-devel \
    openssl-devel python3-tkinter acpica-tools dkms kernel-devel

echo -e "${GREEN}[2/7] Building nbfc-linux...${NC}"
cd /tmp
rm -rf nbfc-linux
git clone https://github.com/nbfc-linux/nbfc-linux.git
cd nbfc-linux
./autogen.sh
./configure
make -j$(nproc)
sudo make install
cd ~

echo -e "${GREEN}[3/7] Installing acpi_call module...${NC}"
cd /tmp
rm -rf acpi_call
git clone https://github.com/nix-community/acpi_call.git
cd acpi_call
sudo make && sudo make install
sudo modprobe acpi_call
cd ~

echo -e "${GREEN}[4/7] Configuring nbfc for your laptop...${NC}"
echo -e "${YELLOW}Running config rating — this may take a minute...${NC}"
sudo nbfc rate-config -a 2>/dev/null | head -10
echo ""
echo -e "${YELLOW}Applying best matched config...${NC}"
BEST_CONFIG=$(sudo nbfc rate-config -a 2>/dev/null | grep "Config score: 10" -B1 | grep -v "Config score" | head -1 | xargs)
if [ -z "$BEST_CONFIG" ]; then
    BEST_CONFIG="HP 15 Notebook PC"
fi
echo -e "${CYAN}Using config: $BEST_CONFIG${NC}"
sudo nbfc config --apply "$BEST_CONFIG" --yes 2>/dev/null || sudo nbfc config --apply "HP 15 Notebook PC" --yes 2>/dev/null || true
sudo nbfc start || true

echo -e "${GREEN}[5/7] Setting up auto-start on boot...${NC}"
echo 'sudo nbfc start' | sudo tee /etc/rc.d/rc.local > /dev/null
sudo chmod +x /etc/rc.d/rc.local

echo -e "${GREEN}[6/7] Installing the fan control app...${NC}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
mkdir -p "$HOME_DIR/.local/share/icons"
cp "$SCRIPT_DIR/fancontrol.py" "$HOME_DIR/fancontrol.py"
cp "$SCRIPT_DIR/fancontrol.svg" "$HOME_DIR/.local/share/icons/fancontrol.svg"
cp "$SCRIPT_DIR/fancontrol.desktop" "$HOME_DIR/.local/share/applications/fancontrol.desktop"
chmod +x "$HOME_DIR/fancontrol.py"

echo -e "${GREEN}[7/7] Configuring sudo permissions...${NC}"
echo "$USER ALL=(ALL) NOPASSWD: ALL" | sudo tee /etc/sudoers.d/fancontrol > /dev/null

echo ""
echo -e "${GREEN}✓ Installation complete!${NC}"
echo ""
echo -e "  Run the app:     ${CYAN}sudo python3 ~/fancontrol.py${NC}"
echo -e "  Or search:       ${CYAN}'Fan Control' in your app menu${NC}"
echo ""
