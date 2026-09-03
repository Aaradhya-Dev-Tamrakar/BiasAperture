# Download FairFace Data for BiasAperture P1 Inference
# This script downloads the FairFace validation label CSV and prepares directory structure
# Data hosted on Google Drive per: https://github.com/dchen236/FairFace#data

param(
    [string]$FairFaceRoot = "..\FairFace",
    [switch]$SkipLabels = $false,
    [switch]$Help = $false
)

# Function to download from Google Drive given a file ID
function Invoke-GoogleDriveFileDownload {
    param(
        [string]$FileId,
        [string]$OutputPath,
        [string]$FileName
    )
    
    try {
        # Try direct link first
        $Url = "https://drive.google.com/uc?export=download&id=$FileId"
        Write-Host "  → Downloading from Google Drive: $FileName" -ForegroundColor Gray
        
        Invoke-WebRequest -Uri $Url -OutFile $OutputPath -ErrorAction Stop | Out-Null
        Write-Host "  ✓ Downloaded: $FileName"
        return $true
    }
    catch {
        Write-Host "  ⚠ Direct download failed, trying alternative method..." -ForegroundColor Yellow
        try {
            # Alternative: use Invoke-WebRequest with session
            $session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
            $session.UserAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/90.0.4430.93"
            
            Invoke-WebRequest -Uri $Url -WebSession $session -OutFile $OutputPath -ErrorAction Stop
            Write-Host "  ✓ Downloaded: $FileName"
            return $true
        }
        catch {
            Write-Host "  ✗ Download failed: $_" -ForegroundColor Red
            return $false
        }
    }
}

if ($Help) {
    @"
USAGE: .\download_fairface_data.ps1 [OPTIONS]

OPTIONS:
  -FairFaceRoot <path>    Path to FairFace repo (default: ../FairFace)
  -SkipLabels             Skip label CSV download (only create directories)
  -Help                   Show this help message

DOWNLOADS:
  1. fairface_label_val.csv   (~100 KB) - Validation set labels
  2. Creates directory structure for BiasAperture integration

EXAMPLE:
  # Standard usage
  .\download_fairface_data.ps1

  # Custom FairFace location
  .\download_fairface_data.ps1 -FairFaceRoot "D:\FairFace"

NOTES:
  - Images must be downloaded manually (2 GB) or via GitHub LFS
  - After download, place validation images in: FairFace/faces/val/
  - Repository: https://github.com/dchen236/FairFace
"@
    exit 0
}

# Resolve paths
$FairFaceRoot = Resolve-Path $FairFaceRoot -ErrorAction Stop
$DataDir = Join-Path $FairFaceRoot "data"
$FacesDir = Join-Path $FairFaceRoot "faces"
$ValDir = Join-Path $FacesDir "val"

Write-Host "=== FairFace Data Download Script ===" -ForegroundColor Cyan
Write-Host "FairFace Root: $FairFaceRoot" -ForegroundColor Gray
Write-Host ""

# Create directory structure
Write-Host "[1/3] Creating directory structure..." -ForegroundColor Yellow
if (-not (Test-Path $DataDir)) {
    New-Item -ItemType Directory -Path $DataDir -Force | Out-Null
    Write-Host "  ✓ Created: $DataDir"
}
if (-not (Test-Path $FacesDir)) {
    New-Item -ItemType Directory -Path $FacesDir -Force | Out-Null
    Write-Host "  ✓ Created: $FacesDir"
}
if (-not (Test-Path $ValDir)) {
    New-Item -ItemType Directory -Path $ValDir -Force | Out-Null
    Write-Host "  ✓ Created: $ValDir (awaiting images)"
}

# Download label CSV
if (-not $SkipLabels) {
    Write-Host ""
    Write-Host "[2/3] Downloading fairface_label_val.csv..." -ForegroundColor Yellow
    
    # Google Drive file ID for validation labels
    $ValLabelFileId = "1wOdja-ezstMEp81tX1a-EYkFebev4h7D"
    $LabelPath = Join-Path $DataDir "fairface_label_val.csv"
    
    if (Test-Path $LabelPath) {
        Write-Host "  ⚠ File exists: $LabelPath" -ForegroundColor Gray
        $response = Read-Host "  Overwrite? (y/n) [default: n]"
        if ($response -ne "y" -and $response -ne "Y") {
            Write-Host "  ⊘ Skipped (keeping existing file)"
        }
        else {
            Remove-Item $LabelPath -Force
            if (Invoke-GoogleDriveFileDownload -FileId $ValLabelFileId -OutputPath $LabelPath -FileName "fairface_label_val.csv") {
                # Verify download
                $sampleCount = Get-Content $LabelPath | Measure-Object -Line | Select-Object -ExpandProperty Lines
                Write-Host "  ℹ File contains $sampleCount lines (10,954 validation images + header)"
            }
        }
    }
    else {
        if (Invoke-GoogleDriveFileDownload -FileId $ValLabelFileId -OutputPath $LabelPath -FileName "fairface_label_val.csv") {
            # Verify download
            $sampleCount = Get-Content $LabelPath | Measure-Object -Line | Select-Object -ExpandProperty Lines
            Write-Host "  ℹ File contains $sampleCount lines (10,954 validation images + header)"
        }
        else {
            exit 1
        }
    }
}

# Download training label CSV (optional, for reference)
Write-Host ""
Write-Host "[3/3] Downloading fairface_label_train.csv (reference)..." -ForegroundColor Yellow

# Google Drive file ID for training labels
$TrainLabelFileId = "1i1L3Yqwaio7YSOCj7ftgk8ZZchPG7dmH"
$TrainLabelPath = Join-Path $DataDir "fairface_label_train.csv"

if (Test-Path $TrainLabelPath) {
    Write-Host "  ⊘ Already exists: $(Split-Path $TrainLabelPath -Leaf)"
}
else {
    Invoke-GoogleDriveFileDownload -FileId $TrainLabelFileId -OutputPath $TrainLabelPath -FileName "fairface_label_train.csv" | Out-Null
}

# Summary
Write-Host ""
Write-Host "=== SETUP COMPLETE ===" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Download validation images to:"
Write-Host "     $ValDir"
Write-Host ""
Write-Host "     GitHub options:"
Write-Host "       - Use git-lfs: cd $FairFaceRoot && git lfs pull --include 'data/face_images/val'"
Write-Host "       - Manual download: See https://github.com/dchen236/FairFace#data"
Write-Host ""
Write-Host "  2. Verify image count:"
Write-Host "     (Get-ChildItem '$ValDir' -Recurse -File | Measure-Object).Count"
Write-Host ""
Write-Host "  3. Create BiasAperture symbolic link (optional):"
Write-Host "     New-Item -ItemType SymbolicLink -Path '..\BiasAperture\data\raw\fairface' -Target '$FairFaceRoot' -Force"
Write-Host ""
Write-Host "  4. Run inference:"
Write-Host "     uv run --extra dev python scripts/run_fairface_inference.py"
Write-Host ""
