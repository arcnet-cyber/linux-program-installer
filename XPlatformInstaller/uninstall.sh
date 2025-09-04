#!/usr/bin/env bash

set -e

ALIAS_NAME="installer"
BASHRC="$HOME/.bashrc"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)/linux-program-installer"

# 1. Remove alias from .bashrc
if grep -q "alias $ALIAS_NAME=" "$BASHRC"; then
    echo "Removing alias '$ALIAS_NAME' from $BASHRC..."
    sed -i "/alias $ALIAS_NAME=/d" "$BASHRC"
    echo "Alias removed."
else
    echo "No alias '$ALIAS_NAME' found in $BASHRC."
fi

# 2. Ask if they want to delete the project folder
read -rp "Do you want to delete the project directory at $TARGET_DIR? (y/n): " DELETE_PROJECT
DELETE_PROJECT=${DELETE_PROJECT,,} # to lowercase

if [[ "$DELETE_PROJECT" == "y" ]]; then
    read -rp "Are you sure? This will permanently delete: $TARGET_DIR (y/n): " CONFIRM_DELETE
    CONFIRM_DELETE=${CONFIRM_DELETE,,}

    if [[ "$CONFIRM_DELETE" == "y" ]]; then
        rm -rf "$TARGET_DIR"
        echo "Project directory deleted."
    else
        echo "Project deletion cancelled."
    fi
else
    echo "Project files retained."
fi

# 3. Final note
echo
echo "Uninstall complete!"
echo "Run this to update your shell:"
echo "   source ~/.bashrc"
