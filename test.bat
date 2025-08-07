@echo off
echo ========================================
echo      SevenX Studio - Teste Rapido
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

echo Testando versao simplificada...
python main-simple.py

pause