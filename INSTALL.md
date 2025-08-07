# Guia de Instalação - SevenX Studio

## 🚀 Instalação Rápida (Windows)

### Método 1: Script Automático
```bash
# Execute o instalador
install.bat
```

### Método 2: Manual
```bash
# 1. Criar ambiente virtual
python -m venv venv
venv\Scripts\activate.bat

# 2. Atualizar pip
python -m pip install --upgrade pip

# 3. Instalar PyQt6
pip install PyQt6

# 4. Instalar PyTorch (CPU)
pip install torch --index-url https://download.pytorch.org/whl/cpu

# 5. Instalar Transformers
pip install transformers huggingface-hub tokenizers

# 6. Instalar outras dependências
pip install requests psutil numpy scipy sentencepiece python-dotenv
```

## 🐧 Linux/macOS

```bash
# 1. Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# 2. Instalar dependências
pip install --upgrade pip
pip install PyQt6 torch transformers huggingface-hub
pip install requests psutil numpy scipy sentencepiece

# 3. Executar
python main.py
```

## 🔧 Instalação com GPU (CUDA)

Se você tem uma GPU NVIDIA compatível:

```bash
# Instalar PyTorch com CUDA
pip install torch --index-url https://download.pytorch.org/whl/cu118

# Instalar aceleração (opcional)
pip install accelerate bitsandbytes
```

## 📋 Verificação da Instalação

```bash
# Testar imports
python -c "import torch; print('PyTorch:', torch.__version__)"
python -c "import transformers; print('Transformers:', transformers.__version__)"
python -c "from PyQt6.QtWidgets import QApplication; print('PyQt6: OK')"
```

## 🚨 Problemas Comuns

### Erro: "No module named 'PyQt6'"
```bash
pip install PyQt6
```

### Erro: "No module named 'torch'"
```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

### Erro: "Microsoft Visual C++ 14.0 is required"
- Instale o Visual Studio Build Tools
- Ou use: `pip install --only-binary=all torch`

### Erro de memória ao carregar modelos
- Use modelos menores (DialoGPT-small)
- Feche outros programas
- Considere usar quantização

## 💡 Dicas

- **Primeira execução**: Pode demorar para baixar modelos
- **Modelos recomendados**: DialoGPT-small (120MB) para começar
- **GPU**: Detectada automaticamente se disponível
- **Memória**: Mínimo 4GB RAM, recomendado 8GB+

## 🆘 Suporte

Se encontrar problemas:
1. Verifique se Python 3.8+ está instalado
2. Use ambiente virtual sempre
3. Atualize pip: `pip install --upgrade pip`
4. Reinstale dependências se necessário