# Guia de Build - SevenX Studio

## 🏗️ Criando Executável (.exe)

### Método 1: Script Automático (Recomendado)
```bash
# Executa todo o processo automaticamente
make_exe.bat
```

### Método 2: Script Avançado
```bash
# Build com mais opções e verificações
python build-advanced.py
```

### Método 3: Manual
```bash
# 1. Ativar ambiente virtual
venv\Scripts\activate.bat

# 2. Instalar PyInstaller
pip install pyinstaller pillow

# 3. Criar ícone
python create_icon.py

# 4. Criar executável
pyinstaller --onefile --windowed --name "SevenX Studio" main.py
```

## 📋 Requisitos para Build

- **Python 3.8+** instalado
- **Ambiente virtual** configurado
- **Dependências** instaladas (PyQt6, torch, transformers, etc.)
- **PyInstaller** para criar executável
- **Pillow** para criar ícone (opcional)

## 🎯 Resultado do Build

Após o build bem-sucedido, você terá:

### Arquivos Criados:
- `dist/SevenX Studio.exe` - Executável principal
- `SevenX_Studio_Portable/` - Pasta portátil completa
- `build/` - Arquivos temporários de build
- `*.spec` - Arquivo de configuração do PyInstaller

### Tamanho Esperado:
- **Executável**: ~200-400MB (inclui PyTorch e modelos)
- **Pasta portátil**: ~400-500MB (com documentação)

## ⚡ Otimizações de Build

### Reduzir Tamanho:
```bash
# Build otimizado (menor tamanho)
pyinstaller --onefile --windowed --optimize=2 --strip main.py
```

### Build com UPX (Compressão):
```bash
# Instalar UPX primeiro: https://upx.github.io/
pyinstaller --onefile --windowed --upx-dir=C:\upx main.py
```

### Build sem Console:
```bash
# Sem janela de console (produção)
pyinstaller --onefile --windowed --noconsole main.py
```

## 🐛 Problemas Comuns

### Erro: "Module not found"
```bash
# Adicionar imports ocultos
pyinstaller --hidden-import=torch --hidden-import=transformers main.py
```

### Erro: "Failed to execute script"
```bash
# Build com console para debug
pyinstaller --onefile --console main.py
```

### Executável muito grande
```bash
# Excluir módulos desnecessários
pyinstaller --exclude-module=matplotlib --exclude-module=scipy main.py
```

### Erro de DLL no Windows
```bash
# Incluir todas as DLLs
pyinstaller --onefile --collect-all=torch main.py
```

## 🔧 Configurações Avançadas

### Arquivo .spec Personalizado:
```python
# sevenx-studio.spec
a = Analysis(['main.py'],
    pathex=[],
    binaries=[],
    datas=[('src', 'src')],
    hiddenimports=['torch', 'transformers'],
    hookspath=[],
    runtime_hooks=[],
    excludes=['matplotlib', 'scipy'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False)

exe = EXE(pyz, a.scripts, a.binaries, a.zipfiles, a.datas, [],
    name='SevenX Studio',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon='assets/icon.ico')
```

### Usar arquivo .spec:
```bash
pyinstaller sevenx-studio.spec
```

## 📦 Distribuição

### Criar Instalador (Opcional):
1. Use **Inno Setup** ou **NSIS**
2. Inclua o executável e documentação
3. Configure auto-update se necessário

### Assinatura Digital (Opcional):
```bash
# Assinar executável (requer certificado)
signtool sign /f certificate.p12 /p password "SevenX Studio.exe"
```

## ✅ Verificação do Build

### Testar Executável:
1. Execute `dist/SevenX Studio.exe`
2. Verifique se a interface abre
3. Teste download de modelo
4. Teste chat básico

### Verificar Dependências:
```bash
# Listar DLLs necessárias
dumpbin /dependents "SevenX Studio.exe"
```

## 🚀 Automação de Build

### GitHub Actions (CI/CD):
```yaml
name: Build SevenX Studio
on: [push, pull_request]
jobs:
  build:
    runs-on: windows-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pyinstaller
    - name: Build executable
      run: make_exe.bat
    - name: Upload artifact
      uses: actions/upload-artifact@v2
      with:
        name: SevenX-Studio-exe
        path: dist/
```

## 💡 Dicas

- **Primeira build**: Pode demorar 10-20 minutos
- **Builds subsequentes**: Mais rápidas (~5 minutos)
- **Teste sempre**: Execute o .exe antes de distribuir
- **Documentação**: Inclua README na pasta portátil
- **Versionamento**: Use tags Git para releases