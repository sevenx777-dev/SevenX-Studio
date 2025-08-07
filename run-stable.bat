@echo off
echo ========================================
echo    SevenX Studio - Versao Estavel
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

echo Iniciando SevenX Studio (sem timer automatico)...
python main-stable.py

pause