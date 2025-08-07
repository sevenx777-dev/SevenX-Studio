@echo off
echo ========================================
echo     SevenX Studio - Criar EXE
echo ========================================
echo.

REM Verificar se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python nao encontrado!
    echo Instale Python 3.8+ antes de continuar.
    pause
    exit /b 1
)

REM Verificar ambiente virtual
if not exist venv (
    echo Criando ambiente virtual...
    python -m venv venv
    if errorlevel 1 (
        echo ERRO: Falha ao criar ambiente virtual!
        pause
        exit /b 1
    )
)

echo Ativando ambiente virtual...
call venv\Scripts\activate.bat

echo Instalando dependencias para build...
pip install --upgrade pip
pip install pyinstaller pillow

echo Instalando dependencias da aplicacao...
pip install PyQt6 torch transformers huggingface-hub requests psutil numpy

echo Criando icone...
python create_icon.py

echo Limpando builds anteriores...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.spec del *.spec

echo.
echo Criando executavel... (isso pode demorar alguns minutos)
echo.

pyinstaller ^
    --onefile ^
    --windowed ^
    --name "SevenX Studio" ^
    --icon=assets/icon.ico ^
    --add-data "src;src" ^
    --hidden-import=torch ^
    --hidden-import=transformers ^
    --hidden-import=huggingface_hub ^
    --hidden-import=tokenizers ^
    --hidden-import=PyQt6.QtCore ^
    --hidden-import=PyQt6.QtWidgets ^
    --hidden-import=PyQt6.QtGui ^
    --hidden-import=requests ^
    --hidden-import=psutil ^
    --hidden-import=numpy ^
    --collect-all=transformers ^
    --collect-all=tokenizers ^
    --distpath=dist ^
    --workpath=build ^
    --specpath=. ^
    main.py

if errorlevel 1 (
    echo.
    echo ERRO: Falha ao criar executavel!
    echo Verifique os erros acima.
    pause
    exit /b 1
)

REM Verificar se o executável foi criado
if not exist "dist\SevenX Studio.exe" (
    echo ERRO: Executavel nao foi criado!
    pause
    exit /b 1
)

REM Obter tamanho do arquivo
for %%A in ("dist\SevenX Studio.exe") do set size=%%~zA
set /a size_mb=%size% / 1048576

echo.
echo ========================================
echo        BUILD CONCLUIDO!
echo ========================================
echo.
echo Executavel criado: dist\SevenX Studio.exe
echo Tamanho: %size_mb% MB
echo.

REM Criar pasta portátil
echo Criando versao portatil...
if exist SevenX_Studio_Portable rmdir /s /q SevenX_Studio_Portable
mkdir SevenX_Studio_Portable

copy "dist\SevenX Studio.exe" "SevenX_Studio_Portable\"
if exist README.md copy README.md SevenX_Studio_Portable\
if exist LICENSE copy LICENSE SevenX_Studio_Portable\
if exist INSTALL.md copy INSTALL.md SevenX_Studio_Portable\

echo.
echo Versao portatil criada em: SevenX_Studio_Portable\
echo.
echo Para testar, execute: "dist\SevenX Studio.exe"
echo.
pause