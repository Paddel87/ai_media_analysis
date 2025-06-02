# AI Media Analysis - Automatischer Formatierungs-Check (PowerShell)
# Verwendung: .\scripts\format-check.ps1 [-Fix]

param(
    [switch]$Fix
)

Write-Host "🎨 AI Media Analysis - Code-Formatierungs-Check" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

$ErrorCount = 0
$PythonDirs = "services", "tests"

# Funktion für farbigen Output
function Write-Status {
    param($Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Success {
    param($Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Error {
    param($Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Write-Warning {
    param($Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

if ($Fix) {
    Write-Status "Formatierungs-Fix-Modus aktiviert"
}

Write-Status "Prüfe Python-Verzeichnisse: $($PythonDirs -join ', ')"

# Black-Formatierung prüfen/fixieren
Write-Status "🖤 Black-Formatierung..."
try {
    if ($Fix) {
        $result = & python -m black @PythonDirs 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Black-Formatierung angewendet"
        } else {
            Write-Error "Black-Formatierung fehlgeschlagen: $result"
            $ErrorCount++
        }
    } else {
        $result = & python -m black --check --diff @PythonDirs 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Black-Formatierung OK"
        } else {
            Write-Error "Black-Formatierung erforderlich - führe '.\scripts\format-check.ps1 -Fix' aus"
            $ErrorCount++
        }
    }
} catch {
    Write-Error "Black-Fehler: $_"
    $ErrorCount++
}

# isort-Import-Sortierung prüfen/fixieren
Write-Status "🔧 isort-Import-Sortierung..."
try {
    if ($Fix) {
        $result = & python -m isort @PythonDirs 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "isort-Sortierung angewendet"
        } else {
            Write-Error "isort-Sortierung fehlgeschlagen: $result"
            $ErrorCount++
        }
    } else {
        $result = & python -m isort --check-only --diff @PythonDirs 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "isort-Sortierung OK"
        } else {
            Write-Error "isort-Sortierung erforderlich - führe '.\scripts\format-check.ps1 -Fix' aus"
            $ErrorCount++
        }
    }
} catch {
    Write-Error "isort-Fehler: $_"
    $ErrorCount++
}

# flake8-Linting (nur Check, keine Fixes)
Write-Status "🔍 flake8-Linting..."
try {
    $result = & python -m flake8 @PythonDirs --max-line-length=88 --extend-ignore=E203,W503 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Success "flake8-Linting OK"
    } else {
        Write-Error "flake8-Linting Fehler gefunden: $result"
        $ErrorCount++
    }
} catch {
    Write-Error "flake8-Fehler: $_"
    $ErrorCount++
}

# Trailing Whitespace prüfen/fixieren
Write-Status "🧹 Trailing Whitespace..."
$filesWithTrailingWhitespace = @()
foreach ($dir in $PythonDirs) {
    $pythonFiles = Get-ChildItem -Path $dir -Recurse -Filter "*.py" -ErrorAction SilentlyContinue
    foreach ($file in $pythonFiles) {
        $content = Get-Content -Path $file.FullName -Raw
        if ($content -match '\s+$') {
            $filesWithTrailingWhitespace += $file.FullName
        }
    }
}

if ($filesWithTrailingWhitespace.Count -gt 0) {
    if ($Fix) {
        foreach ($file in $filesWithTrailingWhitespace) {
            $content = Get-Content -Path $file -Raw
            $content = $content -replace '\s+$', ''
            Set-Content -Path $file -Value $content -NoNewline
        }
        Write-Success "Trailing Whitespace entfernt ($($filesWithTrailingWhitespace.Count) Dateien)"
    } else {
        Write-Error "Trailing Whitespace gefunden in $($filesWithTrailingWhitespace.Count) Dateien - führe '.\scripts\format-check.ps1 -Fix' aus"
        $ErrorCount++
    }
} else {
    Write-Success "Trailing Whitespace OK"
}

# End-of-File-Newline prüfen/fixieren
Write-Status "📄 End-of-File Newlines..."
$filesWithoutEOF = @()
foreach ($dir in $PythonDirs) {
    $pythonFiles = Get-ChildItem -Path $dir -Recurse -Filter "*.py" -ErrorAction SilentlyContinue
    foreach ($file in $pythonFiles) {
        $content = Get-Content -Path $file.FullName -Raw
        if ($content -and -not $content.EndsWith("`n")) {
            $filesWithoutEOF += $file.FullName
        }
    }
}

if ($filesWithoutEOF.Count -gt 0) {
    if ($Fix) {
        foreach ($file in $filesWithoutEOF) {
            Add-Content -Path $file -Value ""
        }
        Write-Success "End-of-File Newlines korrigiert ($($filesWithoutEOF.Count) Dateien)"
    } else {
        Write-Error "Dateien ohne End-of-File Newline gefunden ($($filesWithoutEOF.Count) Dateien) - führe '.\scripts\format-check.ps1 -Fix' aus"
        $ErrorCount++
    }
} else {
    Write-Success "End-of-File Newlines OK"
}

# Zusammenfassung
Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
if ($ErrorCount -eq 0) {
    Write-Success "🎉 Alle Formatierungs-Checks erfolgreich!"
    if ($Fix) {
        Write-Status "Code wurde automatisch formatiert"
    }
    exit 0
} else {
    Write-Error "❌ $ErrorCount Formatierungs-Fehler gefunden!"
    if (-not $Fix) {
        Write-Warning "Führe '.\scripts\format-check.ps1 -Fix' aus um automatisch zu korrigieren"
    }
    exit 1
} 