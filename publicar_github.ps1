# Envia o projeto para o GitHub (passo 1 para publicar no Streamlit Cloud)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host ""
Write-Host "=== Publicar no GitHub (para depois usar Streamlit Cloud) ===" -ForegroundColor Cyan
Write-Host ""

if (Test-Path ".streamlit\secrets.toml") {
    Write-Host "OK: secrets.toml local existe (NAO sera enviado ao GitHub)." -ForegroundColor Green
} else {
    Write-Host "Dica: depois rode python setup_onesignal.py para criar secrets.toml local." -ForegroundColor Yellow
}

$repoName = Read-Host "Nome do repositorio no GitHub (ex: grupo-louvor-ibbj)"
if (-not $repoName) { $repoName = "grupo-louvor-ibbj" }

$gitUser = Read-Host "Seu usuario do GitHub (ex: willsousaa7x)"
if (-not $gitUser) {
    Write-Host "Usuario GitHub obrigatorio." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Preparando commit..." -ForegroundColor Cyan

git add .gitignore README.md PUBLICAR.md CONFIGURAR_ONESIGNAL.md MOBILE.md
git add app.py push_notifications.py requirements.txt setup_onesignal.py iniciar.ps1 publicar_github.ps1
git add build_louvores_db.py scripts static assets .streamlit/config.toml .streamlit/secrets.toml.example
git add components 2>$null

if (Test-Path "data\louvores.csv") {
    git add data/louvores.csv
    Write-Host "Incluido: data/louvores.csv" -ForegroundColor Green
}

git status --short

$msg = "App Grupo de Louvor IBBJ - escalas, chat, PWA e push"
$hasChanges = git diff --cached --quiet 2>$null; if ($LASTEXITCODE -ne 0) {
    git commit -m $msg
    Write-Host "Commit criado." -ForegroundColor Green
} else {
    Write-Host "Nada novo para commitar (ja esta commitado?)." -ForegroundColor Yellow
}

git branch -M main 2>$null

$remoteUrl = "https://github.com/$gitUser/$repoName.git"
$existing = git remote get-url origin 2>$null
if ($LASTEXITCODE -ne 0) {
    git remote add origin $remoteUrl
    Write-Host "Remote adicionado: $remoteUrl" -ForegroundColor Green
} else {
    Write-Host "Remote atual: $existing" -ForegroundColor Yellow
    $trocar = Read-Host "Trocar remote para $remoteUrl ? (s/n)"
    if ($trocar -eq "s") {
        git remote set-url origin $remoteUrl
    }
}

Write-Host ""
Write-Host "=== ANTES DO PUSH ===" -ForegroundColor Yellow
Write-Host "1. Crie o repositorio vazio no GitHub:" -ForegroundColor White
Write-Host "   https://github.com/new?name=$repoName" -ForegroundColor Cyan
Write-Host "   (NAO marque README, .gitignore ou license — deixe vazio)" -ForegroundColor White
Write-Host ""
$continuar = Read-Host "Ja criou o repositorio vazio no GitHub? (s/n)"
if ($continuar -ne "s") {
    Write-Host "Crie o repo e execute de novo: .\publicar_github.ps1" -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "Enviando para GitHub..." -ForegroundColor Cyan
git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "=== SUCESSO no GitHub! ===" -ForegroundColor Green
    Write-Host ""
    Write-Host "Proximo passo — Streamlit Cloud (1 clique):" -ForegroundColor Cyan
    Write-Host "  https://share.streamlit.io/deploy" -ForegroundColor White
    Write-Host ""
    Write-Host "  - Repository: $gitUser/$repoName" -ForegroundColor White
    Write-Host "  - Main file: app.py" -ForegroundColor White
    Write-Host "  - Deploy" -ForegroundColor White
    Write-Host ""
    Write-Host "Depois: Manage app -> Settings -> Secrets (cole secrets.toml)" -ForegroundColor Yellow
    Write-Host "public_url = URL que o Streamlit mostrar (https://....streamlit.app)" -ForegroundColor Yellow
    Start-Process "https://share.streamlit.io/deploy"
} else {
    Write-Host ""
    Write-Host "Push falhou. Causas comuns:" -ForegroundColor Red
    Write-Host "  - Repositorio ainda nao criado no GitHub" -ForegroundColor White
    Write-Host "  - Login: git config credential ou use GitHub Desktop" -ForegroundColor White
    Write-Host "  - URL errada do remote" -ForegroundColor White
}
