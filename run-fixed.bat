@echo off
echo ========================================
echo    SevenX Studio - Versao Corrigida
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

echo Iniciando SevenX Studio (versao corrigida)...
python main.py

pause