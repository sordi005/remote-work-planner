# Builds a Windows .exe using PyInstaller, bundling QSS and icons.
# Usage (PowerShell):
#   pwsh -NoProfile -File scripts/build.ps1

$ErrorActionPreference = "Stop"

Write-Host "[build] Cleaning previous dist/build..." -ForegroundColor Cyan
if (Test-Path dist) { Remove-Item dist -Recurse -Force }
if (Test-Path build) { Remove-Item build -Recurse -Force }

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path | Split-Path -Parent
$resourcesDir = Join-Path $projectRoot "ui/resources"

$iconIco = Join-Path $resourcesDir "app.ico"
$iconPng = Join-Path $resourcesDir "app.png"
$iconPath = $null
if (Test-Path $iconIco) { $iconPath = $iconIco }
elseif (Test-Path $iconPng) { $iconPath = $iconPng }

Write-Host "[build] Running PyInstaller..." -ForegroundColor Cyan
if ($null -ne $iconPath) {
  pyinstaller --noconfirm --windowed --onefile --clean --noupx `
    --name TrabajoRemoto `
    --icon "$iconPath" `
    --add-data "$resourcesDir;ui/resources" `
    --collect-all PyQt6 `
    "$projectRoot/main.py"
} else {
  Write-Host "[build] app icon not found (ui/resources/app.ico|app.png). Building without --icon..." -ForegroundColor Yellow
  pyinstaller --noconfirm --windowed --onefile --clean --noupx `
    --name TrabajoRemoto `
    --add-data "$resourcesDir;ui/resources" `
    --collect-all PyQt6 `
    "$projectRoot/main.py"
}

$exePath = Join-Path $PWD "dist/TrabajoRemoto.exe"
if (Test-Path $exePath -PathType Leaf) {
  $pfx = $env:SIGN_PFX_PATH
  $ppw = $env:SIGN_PFX_PASS
  $ts  = $env:SIGN_TIMESTAMP_URL
  if ([string]::IsNullOrWhiteSpace($ts)) { $ts = "http://timestamp.digicert.com" }
  if (-not [string]::IsNullOrWhiteSpace($pfx) -and -not [string]::IsNullOrWhiteSpace($ppw)) {
    if (Get-Command signtool -ErrorAction SilentlyContinue) {
      Write-Host "[build] Signing EXE with signtool..." -ForegroundColor Cyan
      & signtool sign /fd SHA256 /tr $ts /td SHA256 /f $pfx /p $ppw $exePath
      if ($LASTEXITCODE -ne 0) { throw "signtool failed signing $exePath" }
    } else {
      Write-Host "[build] signtool not found. Skipping code signing." -ForegroundColor Yellow
    }
  } else {
    Write-Host "[build] SIGN_PFX_PATH/PASS not set. Skipping code signing." -ForegroundColor Yellow
  }
}

Write-Host "[build] Done. Output in dist/TrabajoRemoto.exe" -ForegroundColor Green

