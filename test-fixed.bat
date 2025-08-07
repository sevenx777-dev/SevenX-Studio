@echo off
echo ========================================
echo   SevenX Studio - Teste Corrigido
echo ========================================
echo.

if not exist venv (
    echo Ambiente virtual nao encontrado!
    pause
    exit /b 1
)

echo Ativando ambiente virtual...
call venv\Scripts\activate.bat

echo Testando aplicacao corrigida...
python main.py

pause