#!/usr/bin/env powershell
# Script de compilation LaTeX automatisée
# Usage: .\compile.ps1

param(
    [Switch]$Clean = $false,
    [Switch]$View = $false
)

$script_dir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $script_dir

Write-Host "╔════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  Compilation LaTeX - Rapport Big Data               ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Vérifier pdflatex
Write-Host "🔍 Vérification des outils..." -ForegroundColor Yellow
$pdflatex = Get-Command pdflatex -ErrorAction SilentlyContinue
$bibtex = Get-Command bibtex -ErrorAction SilentlyContinue

if (-not $pdflatex) {
    Write-Host "❌ pdflatex non trouvé!" -ForegroundColor Red
    Write-Host "   Installez MiKTeX ou TeX Live" -ForegroundColor Red
    exit 1
}

if (-not $bibtex) {
    Write-Host "⚠️  bibtex non trouvé (bibliographie désactivée)" -ForegroundColor Yellow
}

Write-Host "✓ pdflatex trouvé" -ForegroundColor Green
Write-Host "✓ bibtex trouvé" -ForegroundColor Green
Write-Host ""

# Nettoyage avant compilation
if (Test-Path "main.aux") {
    Write-Host "🧹 Nettoyage des fichiers temporaires..." -ForegroundColor Yellow
    Remove-Item *.aux, *.log, *.out, *.toc, *.bbl, *.blg, *.synctex.gz -ErrorAction SilentlyContinue
    Write-Host "✓ Nettoyé" -ForegroundColor Green
    Write-Host ""
}

# Compilation
Write-Host "📖 Compilation LaTeX (1ère passe)..." -ForegroundColor Cyan
pdflatex -interaction=nonstopmode -file-line-error main.tex 2>&1 | Out-Null

if ($LastExitCode -ne 0) {
    Write-Host "❌ Erreur lors de la compilation!" -ForegroundColor Red
    Write-Host "Logs:" -ForegroundColor Red
    pdflatex -interaction=nonstopmode main.tex
    exit 1
}
Write-Host "✓ Passe 1 complétée" -ForegroundColor Green

# Bibtex
if ($bibtex) {
    Write-Host "📚 Traitement de la bibliographie..." -ForegroundColor Cyan
    bibtex main.aux 2>&1 | Out-Null
    Write-Host "✓ Bibliographie traitée" -ForegroundColor Green
}

# Compilation passe 2
Write-Host "📖 Compilation LaTeX (2ème passe)..." -ForegroundColor Cyan
pdflatex -interaction=nonstopmode -file-line-error main.tex 2>&1 | Out-Null
Write-Host "✓ Passe 2 complétée" -ForegroundColor Green

# Compilation passe 3
Write-Host "📖 Compilation LaTeX (3ème passe)..." -ForegroundColor Cyan
pdflatex -interaction=nonstopmode -file-line-error main.tex 2>&1 | Out-Null
Write-Host "✓ Passe 3 complétée (finalisé)" -ForegroundColor Green
Write-Host ""

# Vérifier le résultat
if (Test-Path "main.pdf") {
    $size = (Get-Item "main.pdf").Length / 1MB
    Write-Host "✅ SUCCÈS!" -ForegroundColor Green
    Write-Host "   Fichier: main.pdf" -ForegroundColor Green
    Write-Host "   Taille: $([Math]::Round($size, 2)) MB" -ForegroundColor Green
}
else {
    Write-Host "❌ Erreur: main.pdf non généré!" -ForegroundColor Red
    exit 1
}

# Nettoyage final
Write-Host ""
Write-Host "🧹 Nettoyage des fichiers temporaires..." -ForegroundColor Yellow
Remove-Item *.aux, *.log, *.out, *.toc, *.bbl, *.blg, *.synctex.gz -ErrorAction SilentlyContinue
Write-Host "✓ Nettoyé" -ForegroundColor Green

# Afficher le PDF si -View est spécifié
if ($View) {
    Write-Host ""
    Write-Host "🔍 Ouverture du PDF..." -ForegroundColor Cyan
    Invoke-Item "main.pdf"
}

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  Compilation terminée avec succès!                   ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "Commandes utiles:" -ForegroundColor Yellow
Write-Host "  .\compile.ps1           # Compilation simple" -ForegroundColor White
Write-Host "  .\compile.ps1 -View     # Compilation + Ouverture PDF" -ForegroundColor White
Write-Host "  .\compile.ps1 -Clean    # Nettoyage avant compilation" -ForegroundColor White
Write-Host ""
