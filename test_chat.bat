@echo off
echo ========================================
echo    Teste de Chat Otimizado
echo ========================================
echo.

if not exist venv (
    echo Ambiente virtual nao encontrado!
    pause
    exit /b 1
)

echo Ativando ambiente virtual...
call venv\Scripts\activate.bat

echo Testando chat com parametros otimizados...
python test_chat_optimized.py

pause