# BitMango Windows Installer
# Installs to $HOME\.bitmango

$ErrorActionPreference = "Stop"

$InstallDir = Join-Path $HOME ".bitmango"
$BinDir = Join-Path $HOME "AppData\Local\Microsoft\WindowsApps"
$ConfigDir = Join-Path $HOME ".config\bitmango"

Write-Host "Installing BitMango Trade CLI..." -ForegroundColor Cyan

# 1. Check for uv
if (-not (Get-Command "uv" -ErrorAction SilentlyContinue)) {
    Write-Error "Error: 'uv' is not installed. Please install it first (https://github.com/astral-sh/uv)."
    exit 1
}

# 2. Create directories
if (-not (Test-Path $InstallDir)) { New-Item -ItemType Directory -Path $InstallDir }
if (-not (Test-Path $BinDir)) { New-Item -ItemType Directory -Path $BinDir }
if (-not (Test-Path $ConfigDir)) { New-Item -ItemType Directory -Path $ConfigDir }

# 3. Copy files
Write-Host "Copying files to $InstallDir..." -ForegroundColor Gray
Copy-Item -Path ".*", "*" -Destination $InstallDir -Recurse -Force -Exclude ".git", ".venv", "__pycache__"

# 4. Install Binaries and Create Shims
Write-Host "Installing binaries and shims to $BinDir..." -ForegroundColor Gray

# Detect distribution type
$BinaryRoot = "."
if (Test-Path "binaries") {
    Write-Host "Detected Full-Source distribution (using 'binaries/' directory)." -ForegroundColor Green
    $BinaryRoot = "binaries"
} else {
    Write-Host "Detected Binaries-Only distribution (using root directory)." -ForegroundColor Green
}

function Install-Binary($Name) {
    $BinaryPath = Join-Path $InstallDir (Join-Path $BinaryRoot "$Name.exe")
    $ShimPath = Join-Path $BinDir "$Name.bat"
    
    if (Test-Path $BinaryPath) {
        # Directly create a batch file that calls the executable
        $Content = @"
@echo off
"$BinaryPath" %*
"@
        $Content | Out-File -FilePath $ShimPath -Encoding ascii
    } else {
        # Fallback shim for source execution
        $Content = @"
@echo off
setlocal
cd /d "$InstallDir"
if exist "bitmango-cli" (
    set "PYTHONPATH=$InstallDir;%PYTHONPATH%"
    uv run python -m bitmango_cli.main %*
) else (
    echo Error: Binary not found and no source code found.
)
endlocal
"@
        $Content | Out-File -FilePath $ShimPath -Encoding ascii
    }
}

Install-Binary "bitmango"
Install-Binary "bitmango-help"
Install-Binary "bitmango-vault"

Write-Host "Success! BitMango Trade CLI has been installed." -ForegroundColor Green
Write-Host "You can now run 'bitmango', 'bitmango-help', or 'bitmango-vault'."
Write-Host "Configuration and vault will be stored in $ConfigDir."
