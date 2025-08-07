@echo off
echo ========================================
echo    Teste Simples de Carregamento
echo ========================================
echo.

if not exist venv (
    echo Ambiente virtual nao encontrado!
    pause
    exit /b 1
)

echo Ativando ambiente virtual...
call venv\Scripts\activate.bat

echo Testando carregamento de modelo...
python test_load_simple.py

pause