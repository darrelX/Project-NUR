# Script de lancement de l'interface Streamlit
# Double-cliquez pour lancer l'application

Write-Host "🚀 Lancement de l'interface Streamlit..." -ForegroundColor Cyan
Write-Host ""

# Se déplacer dans le dossier backend
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# Vérifier si streamlit est installé
try {
    $streamlitVersion = streamlit --version 2>&1
    Write-Host "✅ Streamlit détecté : $streamlitVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Streamlit n'est pas installé!" -ForegroundColor Red
    Write-Host "Installation de Streamlit..." -ForegroundColor Yellow
    pip install streamlit
}

Write-Host ""
Write-Host "📊 Ouverture de l'interface dans votre navigateur..." -ForegroundColor Cyan
Write-Host "🔗 URL : http://localhost:8501" -ForegroundColor Yellow
Write-Host ""
Write-Host "⚠️  Pour arrêter l'application, fermez cette fenêtre ou appuyez sur Ctrl+C" -ForegroundColor Yellow
Write-Host ""

# Lancer streamlit
streamlit run stream.py

# Pause en cas d'erreur
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ Une erreur s'est produite lors du lancement" -ForegroundColor Red
    Read-Host "Appuyez sur Entrée pour fermer cette fenêtre"
}
