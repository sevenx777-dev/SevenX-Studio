@echo off
echo ========================================
echo    SevenX Studio - Build Executavel
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
if exist *.spec del *.spec

echo Criando icone...
python create_icon.py

echo Criando executavel...
pyinstaller --onefile --windowed --name "SevenX Studio" ^
    --icon=assets/icon.ico ^
    --add-data "src;src" ^
    --hidden-import=torch ^
    --hidden-import=transformers ^
    --hidden-import=huggingface_hub ^
    --hidden-import=tokenizers ^
    --hidden-import=PyQt6 ^
    --hidden-import=PyQt6.QtCore ^
    --hidden-import=PyQt6.QtWidgets ^
    --hidden-import=PyQt6.QtGui ^
    --hidden-import=requests ^
    --hidden-import=psutil ^
    --hidden-import=numpy ^
    --collect-all=transformers ^
    --collect-all=tokenizers ^
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
echo Executavel criado em: dist\SevenX Studio.exe
echo.
pause