# AI Media Analysis - Service-Strukturierung PowerShell Script
# Entfernt Root-Level-Duplikate und erstellt einheitliche services/ Struktur

Write-Host "=== AI Media Analysis - Service Strukturierung ===" -ForegroundColor Blue
Write-Host ""

# Redundante Root-Level-Verzeichnisse
$rootDuplicates = @(
    "control",
    "embedding_server", 
    "llm_interface",
    "object_review",
    "ocr_logo_title",
    "preprocess",
    "qdrant",
    "streamlit_ui",
    "vector_db",
    "whisper",
    "vision_pipeline"
)

Write-Host "🔍 Gefundene Root-Level-Duplikate:" -ForegroundColor Yellow
foreach ($dir in $rootDuplicates) {
    if (Test-Path $dir) {
        Write-Host "   ❌ $dir/ (redundant zu services/$dir/)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "⚠️  Diese Verzeichnisse sind redundant, da docker-compose.yml nur services/ verwendet!" -ForegroundColor Yellow
Write-Host ""

$response = Read-Host "Möchten Sie die Root-Level-Duplikate entfernen? (y/N)"
if ($response -eq "y" -or $response -eq "Y") {
    
    # Backup erstellen
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupDir = "backup_$timestamp"
    New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
    
    Write-Host "📦 Erstelle Backup in $backupDir..." -ForegroundColor Blue
    
    foreach ($dir in $rootDuplicates) {
        if (Test-Path $dir) {
            Copy-Item -Recurse $dir $backupDir\
            Write-Host "   ✅ Backup erstellt: $dir" -ForegroundColor Green
        }
    }
    
    Write-Host ""
    Write-Host "🗑️  Entferne Root-Level-Duplikate..." -ForegroundColor Blue
    
    foreach ($dir in $rootDuplicates) {
        if (Test-Path $dir) {
            Remove-Item -Recurse -Force $dir
            Write-Host "   ✅ Entfernt: $dir/" -ForegroundColor Green
        }
    }
    
    Write-Host ""
    Write-Host "🎉 Strukturierung abgeschlossen!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Nächste Schritte:" -ForegroundColor Yellow
    Write-Host "   1. Tests ausführen: make test" 
    Write-Host "   2. Services starten: make run-core-services"
    Write-Host "   3. Health-Check: make health-check"
    Write-Host "   4. Bei Problemen: Backup in $backupDir verwenden"
    
} else {
    Write-Host "❌ Abgebrochen. Strukturierung nicht durchgeführt." -ForegroundColor Red
}

Write-Host ""
Write-Host "📊 Aktuelle services/ Struktur:" -ForegroundColor Blue
Get-ChildItem services\ -Directory | Select-Object Name | Sort-Object Name | Format-Table -AutoSize 