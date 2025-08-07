@echo off
echo Teste rapido de modelo...

if not exist venv (
    echo Ambiente virtual nao encontrado!
    pause
    exit /b 1
)

call venv\Scripts\activate.bat
python test_model.py

pause