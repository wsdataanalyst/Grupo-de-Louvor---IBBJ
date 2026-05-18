# Inicia o Grupo de Louvor IBBJ (PWA + push prontos após setup_onesignal.py)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "Instalando dependencias..." -ForegroundColor Cyan
pip install -r requirements.txt

if (-not (Test-Path "static\icon-192.png")) {
    Write-Host "Gerando icones PWA..." -ForegroundColor Cyan
    python scripts\generate_pwa_icons.py
}

if (-not (Test-Path ".streamlit\secrets.toml")) {
    Write-Host ""
    Write-Host "AVISO: secrets.toml nao encontrado." -ForegroundColor Yellow
    Write-Host "Configure o OneSignal: python setup_onesignal.py" -ForegroundColor Yellow
    Write-Host "Guia: CONFIGURAR_ONESIGNAL.md" -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "Abrindo app..." -ForegroundColor Green
streamlit run app.py
