@echo off
echo ========================================
echo   SevenX Studio - Build Simples
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

echo Instalando PyInstaller...
pip install pyinstaller

echo Criando icone...
python create_icon.py

echo Limpando builds anteriores...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.spec del *.spec

echo.
echo Criando executavel (versao simples)...
echo Isso pode demorar alguns minutos...
echo.

pyinstaller ^
    --onefile ^
    --windowed ^
    --name "SevenX Studio" ^
    --icon=assets/icon.ico ^
    --add-data "src;src" ^
    --hidden-import=PyQt6.QtCore ^
    --hidden-import=PyQt6.QtWidgets ^
    --hidden-import=PyQt6.QtGui ^
    --hidden-import=torch ^
    --hidden-import=transformers ^
    --hidden-import=huggingface_hub ^
    --exclude-module=matplotlib ^
    --exclude-module=scipy ^
    --exclude-module=pandas ^
    --exclude-module=jupyter ^
    --exclude-module=notebook ^
    main.py

if errorlevel 1 (
    echo.
    echo ERRO: Falha ao criar executavel!
    echo Tentando versao ainda mais simples...
    echo.
    
    pyinstaller --onefile --windowed --name "SevenX Studio" main.py
    
    if errorlevel 1 (
        echo ERRO: Build falhou completamente!
        pause
        exit /b 1
    )
)

REM Verificar se o executável foi criado
if not exist "dist\SevenX Studio.exe" (
    echo ERRO: Executavel nao foi criado!
    pause
    exit /b 1
)

echo.
echo ========================================
echo        BUILD CONCLUIDO!
echo ========================================
echo.
echo Executavel criado: dist\SevenX Studio.exe
echo.

REM Testar o executável
echo Testando executavel...
"dist\SevenX Studio.exe" &

echo.
echo Para distribuir, copie o arquivo:
echo dist\SevenX Studio.exe
echo.
pause