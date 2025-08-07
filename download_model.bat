@echo off
echo ========================================
echo    Download DialoGPT Small
echo ========================================
echo.

if not exist venv (
    echo Ambiente virtual nao encontrado!
    echo Execute install-simple.bat primeiro.
    pause
    exit /b 1
)

echo Ativando ambiente virtual...
call venv\Scripts\activate.bat

echo Baixando DialoGPT Small...
python download_dialogpt.py

pause