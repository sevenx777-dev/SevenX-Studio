@echo off
echo ========================================
echo       SevenX Studio - Executando
echo ========================================
echo.

if not exist venv (
    echo Ambiente virtual nao encontrado!
    echo Execute install.bat primeiro.
    pause
    exit /b 1
)

echo Ativando ambiente virtual...
call venv\Scripts\activate.bat

echo Iniciando SevenX Studio...
python main.py

pause