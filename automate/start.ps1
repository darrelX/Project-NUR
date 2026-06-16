# Script de démarrage pour l'application Streamlit
# Plateforme de traitement Excel - CellDown, Ticket, OCM RAN

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Plateforme de Traitement Excel" -ForegroundColor Cyan
Write-Host "  CellDown | Ticket | OCM RAN" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier si Python est installé
Write-Host "Vérification de Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ $pythonVersion détecté" -ForegroundColor Green
} catch {
    Write-Host "✗ Python n'est pas installé ou n'est pas dans le PATH" -ForegroundColor Red
    Write-Host "  Téléchargez Python depuis : https://www.python.org/downloads/" -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host ""

# Vérifier si l'environnement virtuel existe
$venvPath = "venv"
if (-not (Test-Path $venvPath)) {
    Write-Host "Environnement virtuel non trouvé. Création en cours..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "✓ Environnement virtuel créé" -ForegroundColor Green
} else {
    Write-Host "✓ Environnement virtuel trouvé" -ForegroundColor Green
}

Write-Host ""

# Activer l'environnement virtuel
Write-Host "Activation de l'environnement virtuel..." -ForegroundColor Yellow
& "$venvPath\Scripts\Activate.ps1"

Write-Host ""

# Vérifier si les dépendances sont installées
Write-Host "Vérification des dépendances..." -ForegroundColor Yellow
try {
    $streamlitCheck = pip show streamlit 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Streamlit non installé"
    }
    Write-Host "✓ Dépendances installées" -ForegroundColor Green
} catch {
    Write-Host "Installation des dépendances..." -ForegroundColor Yellow
    pip install -r requirements.txt
    Write-Host "✓ Dépendances installées" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Démarrage de l'application..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "L'application va s'ouvrir dans votre navigateur" -ForegroundColor Yellow
Write-Host "URL : http://localhost:8501" -ForegroundColor Cyan
Write-Host ""
Write-Host "Pour arrêter l'application, appuyez sur Ctrl+C" -ForegroundColor Yellow
Write-Host ""

# Lancer Streamlit
streamlit run app.py

# Si Streamlit s'arrête
Write-Host ""
Write-Host "Application arrêtée." -ForegroundColor Yellow
pause
