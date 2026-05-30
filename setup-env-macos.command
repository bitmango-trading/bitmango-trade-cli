#!/bin/bash

# BitMango macOS Setup Environment (.command for double-clickability)
# Installs uv, creates a virtual environment, and installs dependencies

set -e

# Change to the directory where the script is located
cd "$(dirname "$0")"

echo "--- Setting up uv Python environment for macOS ---"

# 1. Install uv (if not already installed)
if ! command -v uv &> /dev/null
then
    echo "uv not found, installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source "$HOME/.local/bin/env"
else
    echo "uv is already installed."
    # Ensure it's in path
    [ -f "$HOME/.local/bin/env" ] && source "$HOME/.local/bin/env"
fi

VENV_DIR=".venv"

# Use system python3 if available
SYSTEM_PYTHON_EXE="/usr/bin/python3"
if [ ! -f "$SYSTEM_PYTHON_EXE" ]; then
    SYSTEM_PYTHON_EXE="python3"
fi

# 2. Create virtual environment
if [ -d "$VENV_DIR" ]; then
    echo "Removing existing virtual environment $VENV_DIR..."
    rm -rf "$VENV_DIR"
fi

echo "Creating uv virtual environment in $VENV_DIR..."
uv venv "$VENV_DIR" --python "$SYSTEM_PYTHON_EXE"

# 3. Install dependencies
echo "Installing dependencies from requirements.txt..."
uv pip install -r requirements.txt

echo "--- Environment setup complete ---"
echo "To activate the virtual environment, run: source $VENV_DIR/bin/activate"
