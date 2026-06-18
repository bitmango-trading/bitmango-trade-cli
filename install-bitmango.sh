#!/bin/bash

# BitMango Local Installer (Linux/macOS)
# Installs to ~/.bitmango and symlinks to ~/.local/bin

set -e

INSTALL_DIR="$HOME/.bitmango"
BIN_DIR="$HOME/.local/bin"
CONFIG_DIR="$HOME/.config/bitmango"

echo "Installing BitMango Trade CLI..."

# 1. Check for uv
if ! command -v uv &> /dev/null; then
    echo "Error: 'uv' is not installed. Please install it first (https://github.com/astral-sh/uv)."
    exit 1
fi

# 2. Create directories
mkdir -p "$INSTALL_DIR"
mkdir -p "$BIN_DIR"
mkdir -p "$CONFIG_DIR"

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

# Ensure bitmango/ directory is present in INSTALL_DIR
# (It will be copied by the rsync/cp above)

# 4. Install Binaries and Create Shims
echo "Installing binaries and shims to $BIN_DIR..."

# Detect distribution type
if [ -d "bin" ]; then
    echo "Detected Full-Source distribution (using 'bin/' directory)."
fi

install_binary() {
    local name=$1
    local binary_path=""
    
    if [ -d "bin" ]; then
        binary_path="$INSTALL_DIR/bin/$name"
    else
        binary_path="$INSTALL_DIR/$name"
    fi
    
    local shim="$BIN_DIR/$name"
    
    if [ -f "$binary_path" ]; then
        # Create a symbolic link to the script
        ln -sf "$binary_path" "$shim"
        chmod +x "$binary_path"
    else
        # Fallback shim for source execution
        cat > "$shim" <<EOF
#!/bin/bash
cd "$INSTALL_DIR"
# If we have source code available, run via uv
if [ -d "bitmango-cli" ]; then
    export PYTHONPATH="\$INSTALL_DIR"
    exec uv run python "\$INSTALL_DIR/bin/\$name" "\$@"
else
    echo "Error: Binary not found at $binary_path and no source code found."
    exit 1
fi
EOF
        chmod +x "$shim"
    fi
}

install_binary "bitmango"
install_binary "bitmango-help"
install_binary "bitmango-vault"

# 5. Handle PATH
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo "Warning: $BIN_DIR is not in your PATH."
    echo "Please add the following to your .bashrc, .zshrc, or .profile:"
    echo "  export PATH="\$HOME/.local/bin:\$PATH""
fi

echo "Success! BitMango Trade CLI has been installed."
echo "You can now run 'bitmango', 'bitmango-help', or 'bitmango-vault'."
echo "Configuration and vault will be stored in $CONFIG_DIR."
