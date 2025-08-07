@echo off
echo ========================================
echo    Teste de Carregamento de Modelos
echo ========================================
echo.

if not exist venv (
    echo Ambiente virtual nao encontrado!
    pause
    exit /b 1
)

echo Ativando ambiente virtual...
call venv\Scripts\activate.bat

echo Testando carregamento de modelos...
python test_model.py

pause