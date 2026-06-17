#!/bin/bash

# BitMango macOS Installer (.command format for double-clickability)
# Installs to ~/.bitmango and symlinks to /usr/local/bin

set -e

# Change to the directory where the script is located
cd "$(dirname "$0")"

INSTALL_DIR="$HOME/.bitmango"
BIN_DIR="/usr/local/bin"
CONFIG_DIR="$HOME/.config/bitmango"

echo "Installing BitMango Trade CLI for macOS..."

# 1. Check for uv
if ! command -v uv &> /dev/null; then
    echo "Error: 'uv' is not installed. Please install it first (https://github.com/astral-sh/uv)."
    exit 1
fi

# 2. Create directories
mkdir -p "$INSTALL_DIR"
mkdir -p "$CONFIG_DIR"

# Ensure /usr/local/bin exists and is writable
if [ ! -d "$BIN_DIR" ]; then
    echo "Creating $BIN_DIR (may require password)..."
    sudo mkdir -p "$BIN_DIR"
    sudo chown -R $(whoami) "$BIN_DIR"
fi

# 3. Copy files
echo "Copying files to $INSTALL_DIR..."
# Use rsync if available, otherwise cp
if command -v rsync &> /dev/null; then
    rsync -av --exclude '.git' --exclude '.venv' --exclude '__pycache__' ./ "$INSTALL_DIR/"
else
    cp -R . "$INSTALL_DIR/"
    find "$INSTALL_DIR" -name ".git" -type d -exec rm -rf {} +
    find "$INSTALL_DIR" -name ".venv" -type d -exec rm -rf {} +
    find "$INSTALL_DIR" -name "__pycache__" -type d -exec rm -rf {} +
fi

# 4. Create robust shims
echo "Creating shims in $BIN_DIR..."

# Detect distribution type
if [ -d "binaries" ]; then
    echo "Detected Full-Source distribution (using 'binaries/' directory)."
    BINARY_ROOT="binaries"
else
    echo "Detected Binaries-Only distribution (using root directory)."
    BINARY_ROOT="."
fi

create_shim() {
    local name=$1
    local shim="$BIN_DIR/$name"
    
    # Remove existing shim to avoid following symlinks if it was one
    rm -f "$shim"
    
    cat > "$shim" <<EOF
#!/bin/bash
# BitMango Shim
cd "$INSTALL_DIR"
if [ -f "$BINARY_ROOT/$name" ]; then
    "$INSTALL_DIR/$BINARY_ROOT/$name" "\$@"
elif [ -d "bitmango-cli" ]; then
    export PYTHONPATH="\$INSTALL_DIR:\$PYTHONPATH"
    uv run python -m bitmango_cli.main "\$@"
else
    echo "Error: Binary not found and no source code found."
    exit 1
fi
EOF
    chmod +x "$shim"
}

create_shim "bitmango"
create_shim "bitmango-help"
create_shim "bitmango-vault"

# 5. Handle PATH (just in case)
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo "Warning: $BIN_DIR is not in your PATH."
    echo "Please add the following to your .bashrc, .zshrc, or .profile:"
    echo "  export PATH=\"/usr/local/bin:\$PATH\""
fi

echo "Success! BitMango Trade CLI has been installed."
echo "You can now run 'bitmango', 'bitmango-help', or 'bitmango-vault'."
echo "Configuration and vault will be stored in $CONFIG_DIR."
