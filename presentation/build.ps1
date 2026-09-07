# Build script for BiasAperture Presentation (LaTeX Beamer)
$ErrorActionPreference = "Stop"

Write-Host "====================================================" -ForegroundColor Cyan
Write-Host " Building BiasAperture Beamer Presentation" -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan

$CurrentDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $CurrentDir

# Pass 1
Write-Host "[1/2] Running pdflatex (Pass 1)..." -ForegroundColor Yellow
pdflatex -interaction=nonstopmode main.tex | Out-Null

# Pass 2 (resolving labels, counts, and navigation)
Write-Host "[2/2] Running pdflatex (Pass 2)..." -ForegroundColor Yellow
pdflatex -interaction=nonstopmode main.tex | Out-Null

if (Test-Path "main.pdf") {
    $PdfSize = (Get-Item "main.pdf").Length / 1KB
    Write-Host "Successfully compiled main.pdf ($([math]::Round($PdfSize, 1)) KB)" -ForegroundColor Green
    Write-Host "Output: $(Join-Path $CurrentDir 'main.pdf')" -ForegroundColor Green
} else {
    Write-Error "Compilation failed. Check main.log for details."
}
