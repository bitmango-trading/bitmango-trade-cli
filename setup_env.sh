#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

echo "--- Setting up uv Python environment ---"

UV_INSTALL_DIR="$HOME/.local/bin"

# 1. Install uv (if not already installed)
if ! command -v uv &> /dev/null
then
    echo "uv not found, installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    echo "uv installed."
    # Source the uv environment file if it exists
    [ -f "$HOME/.local/bin/env" ] && source "$HOME/.local/bin/env"
else
    echo "uv is already installed."
    # Source the uv environment file if it exists
    [ -f "$HOME/.local/bin/env" ] && source "$HOME/.local/bin/env"
fi

# Verify uv is now in PATH
if ! command -v uv &> /dev/null
then
    echo "Error: uv is not in PATH after installation. Please check your installation."
    exit 1
fi

VENV_DIR=".venv"

# Explicitly use the system Python 3 interpreter
SYSTEM_PYTHON_EXE="/usr/bin/python3"
if [ ! -f "$SYSTEM_PYTHON_EXE" ]; then
    echo "Error: System Python 3 not found at $SYSTEM_PYTHON_EXE. Please ensure it's installed."
    exit 1
fi

# Remove existing .venv if it exists to ensure a clean slate
if [ -d "$VENV_DIR" ]; then
    echo "Removing existing virtual environment $VENV_DIR..."
    rm -rf "$VENV_DIR"
fi

# 2. Create a uv virtual environment
echo "Creating uv virtual environment in $VENV_DIR using $SYSTEM_PYTHON_EXE..."
uv venv "$VENV_DIR" --python "$SYSTEM_PYTHON_EXE" # Explicitly use system python

# 3. Install dependencies from requirements.txt
echo "Installing dependencies from requirements.txt into $VENV_DIR..."
uv pip install -r requirements.txt # uv should be in PATH and detect .venv

echo "--- Environment setup complete ---"
echo "To activate the virtual environment, run: source $VENV_DIR/bin/activate"
echo "To deactivate, run: deactivate"
