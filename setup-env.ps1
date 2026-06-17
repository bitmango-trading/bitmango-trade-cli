# BitMango Windows Setup Environment
# Installs uv, creates a virtual environment, and installs dependencies

$ErrorActionPreference = "Stop"

Write-Host "--- Setting up uv Python environment ---" -ForegroundColor Cyan

# 1. Install uv (if not already installed)
if (-not (Get-Command "uv" -ErrorAction SilentlyContinue)) {
    Write-Host "uv not found, installing uv..." -ForegroundColor Gray
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    $env:Path += ";$HOME\.local\bin"
} else {
    Write-Host "uv is already installed." -ForegroundColor Gray
}

# 2. Create virtual environment
$VenvDir = ".venv"
if (Test-Path $VenvDir) {
    Write-Host "Removing existing virtual environment $VenvDir..." -ForegroundColor Gray
    Remove-Item -Path $VenvDir -Recurse -Force
}

Write-Host "Creating uv virtual environment in $VenvDir..." -ForegroundColor Gray
uv venv $VenvDir

# 3. Install dependencies
Write-Host "Installing dependencies from requirements.txt..." -ForegroundColor Gray
uv pip install -r requirements.txt

Write-Host "--- Environment setup complete ---" -ForegroundColor Green
Write-Host "To activate the virtual environment, run: .\.venv\Scripts\Activate.ps1"
