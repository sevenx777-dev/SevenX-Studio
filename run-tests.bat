@echo off
echo ========================================
echo      SevenX Studio - Executar Testes
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

echo Instalando dependencias de teste...
pip install pytest pytest-cov

echo.
echo Executando testes...
echo.

REM Configurar display para PyQt
set QT_QPA_PLATFORM=offscreen

REM Executar testes
pytest tests/ -v --cov=src --cov-report=term-missing

if errorlevel 1 (
    echo.
    echo Alguns testes falharam!
    echo Verifique os erros acima.
) else (
    echo.
    echo ========================================
    echo        Todos os testes passaram!
    echo ========================================
)

echo.
pause