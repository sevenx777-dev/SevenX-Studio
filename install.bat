@echo off
echo ========================================
echo    SevenX Studio - Instalador Windows
echo ========================================
echo.

echo Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python nao encontrado!
    echo Por favor, instale Python 3.8+ antes de continuar.
    echo Download: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Python encontrado!
echo.

echo Criando ambiente virtual...
python -m venv venv
if errorlevel 1 (
    echo ERRO: Falha ao criar ambiente virtual!
    pause
    exit /b 1
)

echo Ativando ambiente virtual...
call venv\Scripts\activate.bat

echo Atualizando pip...
python -m pip install --upgrade pip

echo Instalando dependencias basicas...
pip install --upgrade pip
pip install PyQt6 requests psutil

echo Instalando PyTorch (pode demorar)...
pip install torch --index-url https://download.pytorch.org/whl/cpu

echo Instalando Transformers e Hugging Face...
pip install transformers huggingface-hub tokenizers

echo Instalando dependencias adicionais...
pip install numpy scipy sentencepiece

echo Instalando dependencias opcionais...
pip install python-dotenv aiohttp httpx websockets
if errorlevel 1 (
    echo ERRO: Falha ao instalar dependencias!
    pause
    exit /b 1
)

echo.
echo ========================================
echo    Instalacao concluida com sucesso!
echo ========================================
echo.
echo Para executar o SevenX Studio:
echo 1. Execute: venv\Scripts\activate.bat
echo 2. Execute: python main.py
echo.
echo Ou simplesmente execute: run.bat
echo.
pause