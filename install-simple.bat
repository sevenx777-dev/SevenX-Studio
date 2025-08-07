@echo off
echo ========================================
echo   SevenX Studio - Instalacao Simples
echo ========================================
echo.

echo Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python nao encontrado!
    pause
    exit /b 1
)

echo Criando ambiente virtual...
if exist venv rmdir /s /q venv
python -m venv venv

echo Ativando ambiente virtual...
call venv\Scripts\activate.bat

echo Atualizando pip...
python -m pip install --upgrade pip

echo Instalando dependencias basicas (sem accelerate)...
pip install PyQt6
pip install requests psutil numpy

echo Instalando PyTorch (CPU apenas)...
pip install torch --index-url https://download.pytorch.org/whl/cpu

echo Instalando Transformers...
pip install transformers huggingface-hub tokenizers

echo.
echo ========================================
echo    Instalacao concluida!
echo ========================================
echo.
echo Para executar: python main.py
echo.
pause