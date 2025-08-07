@echo off
setlocal

echo ========================================
echo   SevenX Studio - Atualizador de Repositorio
echo ========================================
echo.

REM --- Verifica se o git esta instalado ---
git --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Git nao encontrado. Por favor, instale o Git e adicione ao PATH.
    pause
    exit /b 1
)

REM --- Mostra o status atual do repositorio ---
echo --- Status Atual do Repositorio ---
git status
echo ---------------------------------
echo.

REM --- Pergunta ao usuario se deseja continuar ---
choice /c SN /m "Deseja adicionar todos os arquivos e fazer um novo commit?"
if errorlevel 2 (
    echo Operacao cancelada pelo usuario.
    pause
    exit /b 0
)

echo.
echo Adicionando todos os arquivos ao stage...
git add .
echo Arquivos adicionados.
echo.

REM --- Pede ao usuario para inserir a mensagem do commit ---
set /p commit_message="Digite a mensagem do commit (ex: 'feat: Adiciona nova funcionalidade'): "

if not defined commit_message (
    echo [AVISO] Mensagem de commit vazia. Usando mensagem padrao.
    set commit_message="chore: Atualizacoes de rotina"
)

echo.
echo Fazendo commit com a mensagem: "%commit_message%"
git commit -m "%commit_message%"
echo.

REM --- **CORRECAO AQUI**: Puxa as alteracoes do repositorio remoto primeiro ---
echo Puxando as ultimas alteracoes do GitHub (git pull)...
git pull origin main --no-edit
echo.

echo Enviando atualizacoes para o repositorio remoto (origin main)...
git push origin main

REM --- Fallback para configurar o repositorio remoto se o primeiro push falhar ---
if errorlevel 1 (
    echo.
    echo [INFO] Falha no push. Pode ser a primeira vez ou o remote nao esta configurado.
    echo Tentando configurar o repositorio remoto 'origin'...
    git remote add origin https://github.com/sevenx777-dev/SevenX-Studio.git
    git branch -M main
    echo.
    echo Tentando enviar novamente com a nova configuracao...
    git push -u origin main
)

echo.
echo ========================================
echo      Repositorio atualizado!
echo ========================================
echo.
echo Acesse: https://github.com/sevenx777-dev/SevenX-Studio
echo.
pause
