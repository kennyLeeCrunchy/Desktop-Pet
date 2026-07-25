$ErrorActionPreference = "Stop"

$Workspace = Split-Path -Parent $PSScriptRoot
$Python = (Get-Command python.exe -ErrorAction Stop).Source
$Source = Join-Path $PSScriptRoot "main.py"
$AssetDir = Join-Path $PSScriptRoot "assets"
$PublishDir = Join-Path $Workspace "publish\KIMACHI-App"
$WorkDir = Join-Path $Workspace ".build\pyinstaller-work"
$SpecDir = Join-Path $Workspace ".build\pyinstaller-spec"
$PetSpritesheet = Join-Path $Workspace "publish\kimachi\spritesheet.webp"

New-Item -ItemType Directory -Path $PublishDir -Force | Out-Null
New-Item -ItemType Directory -Path $WorkDir -Force | Out-Null
New-Item -ItemType Directory -Path $SpecDir -Force | Out-Null

& $Python (Join-Path $PSScriptRoot "prepare_assets.py") $PetSpritesheet $AssetDir

& $Python -m PyInstaller `
    --noconfirm `
    --clean `
    --onefile `
    --windowed `
    --name "KIMACHI" `
    --icon (Join-Path $AssetDir "kimachi.ico") `
    --add-data "$AssetDir;assets" `
    --exclude-module "numpy" `
    --exclude-module "pygame" `
    --exclude-module "psutil" `
    --distpath $PublishDir `
    --workpath $WorkDir `
    --specpath $SpecDir `
    $Source

if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller failed with exit code $LASTEXITCODE"
}

Copy-Item -LiteralPath (Join-Path $PSScriptRoot "FRIEND-README.txt") `
    -Destination (Join-Path $PublishDir "README.txt") -Force

Write-Host "Published to $PublishDir"
