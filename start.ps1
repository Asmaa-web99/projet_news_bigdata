#!/usr/bin/env pwsh
# Script de démarrage simplifié pour le projet Big Data

Write-Host "
╔══════════════════════════════════════════════════════════════╗
║   Plateforme Big Data - Analyse de Médias                   ║
║   Démarrage automatique                                      ║
╚══════════════════════════════════════════════════════════════╝
" -ForegroundColor Cyan

# Vérifier Docker
Write-Host "`n[1/4] Vérification de Docker..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version
    Write-Host "✅ Docker trouvé: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker n'est pas installé ou pas en cours d'exécution" -ForegroundColor Red
    Write-Host "   Installez Docker Desktop et relancez ce script" -ForegroundColor Red
    exit 1
}

# Démarrer les services
Write-Host "`n[2/4] Démarrage des services Docker..." -ForegroundColor Yellow
docker-compose up -d

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erreur lors du démarrage des services" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Services lancés en arrière-plan" -ForegroundColor Green

# Attendre le démarrage
Write-Host "`n[3/4] Attente du démarrage des services (30 secondes)..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Vérifier l'état
Write-Host "`n[4/4] Vérification de l'état des services..." -ForegroundColor Yellow
$status = docker-compose ps --format json | ConvertFrom-Json

$allRunning = $true
foreach ($service in $status) {
    if ($service.State -like "Up*") {
        Write-Host "   ✅ $($service.Service)" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  $($service.Service): $($service.State)" -ForegroundColor Yellow
        $allRunning = $false
    }
}

# Afficher les URLs
Write-Host "`n╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                    SERVICES DISPONIBLES                     ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

Write-Host "`n📊 Dashboard Streamlit (RECOMMANDÉ)" -ForegroundColor Green
Write-Host "   👉 http://localhost:8501`n" -ForegroundColor Cyan

Write-Host "🔄 Airflow (Orchestration)" -ForegroundColor Green
Write-Host "   👉 http://localhost:8080" -ForegroundColor Cyan
Write-Host "   Login: airflow / airflow`n" -ForegroundColor White

Write-Host "💾 MinIO Console (Data Lake)" -ForegroundColor Green
Write-Host "   👉 http://localhost:9001" -ForegroundColor Cyan
Write-Host "   Login: minioadmin / minioadmin`n" -ForegroundColor White

Write-Host "📈 Metabase (BI)" -ForegroundColor Green
Write-Host "   👉 http://localhost:3000`n" -ForegroundColor Cyan

Write-Host "🗄️  PostgreSQL DWH" -ForegroundColor Green
Write-Host "   👉 localhost:5433" -ForegroundColor Cyan
Write-Host "   User: dwh_admin / dwh_password`n" -ForegroundColor White

Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
if ($allRunning) {
    Write-Host "✅ Tous les services sont OPÉRATIONNELS" -ForegroundColor Green
} else {
    Write-Host "⚠️  Quelques services sont encore en démarrage..." -ForegroundColor Yellow
    Write-Host "   Attendez 1-2 minutes supplémentaires" -ForegroundColor Yellow
}
Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

Write-Host "`nPour arrêter tous les services:" -ForegroundColor White
Write-Host "   docker-compose down`n" -ForegroundColor Gray

Write-Host "Pour voir les logs:" -ForegroundColor White
Write-Host "   docker-compose logs -f`n" -ForegroundColor Gray

Write-Host "Pour plus d'infos, voir QUICK_START.md`n" -ForegroundColor Gray
