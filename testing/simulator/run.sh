#!/bin/bash
# Run the simulated exchange API
# It will be available at http://127.0.0.1:8000

# Ensure we are in the simulator directory
cd "$(dirname "$0")"

# Use the project's venv or a local one if preferred
# For now, using the main project venv
../../.venv/bin/uvicorn app:app --host 127.0.0.1 --port 8080 --reload
