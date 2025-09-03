#!/usr/bin/env bash

set -e

# 1. Detect OS
detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        echo "$ID"
    else
        echo "unknown"
    fi
}

OS_ID=$(detect_os)
echo "Detected OS: $OS_ID"

# 2. Confirm Python 3 install
read -rp "Do you want to install Python 3? (y/n): " INSTALL_PYTHON
INSTALL_PYTHON=${INSTALL_PYTHON,,} # to lowercase

if [[ "$INSTALL_PYTHON" == "y" ]]; then
    echo "Installing Python 3..."

    case "$OS_ID" in
        arch|manjaro|arcolinux|endeavouros|garuda)
            sudo pacman -Sy --noconfirm python
            ;;
        void)
            sudo xbps-install -Sy python3
            ;;
        debian|ubuntu|linuxmint|pop|elementary|kali|zorin|neon|parrot|trisquel)
            sudo apt update
            sudo apt install -y python3
            ;;
        fedora|rhel|centos|almalinux|rocky|ol|oracle)
            sudo dnf install -y python3
            ;;
        opensuse|suse|opensuse-leap|opensuse-tumbleweed|sles)
            sudo zypper install -y python3
            ;;
        *)
            echo "Unsupported OS: $OS_ID"
            exit 1
            ;;
    esac

    echo "Python 3 installed."
else
    echo "Skipping Python 3 installation."
fi

# 3. Create 'installer' alias
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOOL_ENTRY="$SCRIPT_DIR/main.py"

if [ ! -f "$TOOL_ENTRY" ]; then
    echo " Could not find main.py in: $SCRIPT_DIR"
    exit 1
fi

ALIAS_CMD="alias installer='python3 \"$TOOL_ENTRY\"'"

if ! grep -Fxq "$ALIAS_CMD" "$HOME/.bashrc"; then
    echo "$ALIAS_CMD" >> "$HOME/.bashrc"
    echo "Alias 'installer' added to ~/.bashrc"
else
    echo "Alias 'installer' already exists in ~/.bashrc"
fi

# 4. Final Instructions
echo
echo " Setup complete!"
echo "Run this to activate the alias in your current terminal:"
echo "   source ~/.bashrc"
echo "Then run your tool with:"
echo "   installer"
