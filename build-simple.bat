@echo off
echo ========================================
echo   SevenX Studio - Build Simples
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

echo Instalando PyInstaller...
pip install pyinstaller

echo Limpando builds anteriores...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo Criando executavel (versao simples)...
pyinstaller --onedir --windowed --name "SevenX Studio" ^
    --add-data "src;src" ^
    --hidden-import=torch ^
    --hidden-import=transformers ^
    --hidden-import=huggingface_hub ^
    --hidden-import=PyQt6.QtCore ^
    --hidden-import=PyQt6.QtWidgets ^
    --hidden-import=PyQt6.QtGui ^
    main.py

if errorlevel 1 (
    echo ERRO: Falha ao criar executavel!
    pause
    exit /b 1
)

echo.
echo ========================================
echo     Build concluido com sucesso!
echo ========================================
echo.
echo Executavel criado em: dist\SevenX Studio\
echo.
pause