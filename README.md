# 🚀 SevenX Studio

<div align="center">

![SevenX Studio Logo](assets/banner.png)

**Uma aplicação desktop moderna para gerenciamento e execução de modelos de IA localmente**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![PyQt6](https://img.shields.io/badge/PyQt6-6.5+-green.svg)](https://pypi.org/project/PyQt6/)
[![GitHub release](https://img.shields.io/github/release/sevenx777-dev/SevenX-Studio.svg)](https://github.com/sevenx777-dev/SevenX-Studio/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub stars](https://img.shields.io/github/stars/sevenx777-dev/SevenX-Studio.svg)](https://github.com/sevenx777-dev/SevenX-Studio/stargazers)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)]()

[📥 Download](#-instalação) • [📖 Documentação](#-como-usar) • [🐛 Issues](https://github.com/sevenx-team/sevenx-studio/issues) • [💬 Discussões](https://github.com/sevenx-team/sevenx-studio/discussions)

</div>

## ✨ Características

- 🤖 **Motor de IA Próprio** - Engine independente baseado em PyTorch e Transformers
- 💬 **Chat Interativo** - Interface de chat moderna com streaming em tempo real
- 📊 **Monitor de Sistema** - Acompanhe uso de CPU, RAM e GPU em tempo real
- 🎨 **Interface Moderna** - UI responsiva com tema escuro/claro
- 🔧 **Configurações Avançadas** - Parâmetros personalizáveis (temperature, top-p, etc.)
- 🔒 **Privacidade Total** - Tudo roda localmente, seus dados ficam seguros
- 📁 **Histórico de Conversas** - Salve e organize suas conversas
- 🤗 **Hugging Face Hub** - Integração direta com modelos do Hugging Face
- ⚡ **GPU Acceleration** - Suporte automático para CUDA quando disponível
- 📦 **Executável Standalone** - Crie arquivos .exe para distribuição

## 🎯 Modelos Suportados

- **DialoGPT** (Small, Medium, Large) - Conversação
- **GPT-2** (Base, Medium) - Geração de texto
- **CodeBERT** - Especializado em código
- **DistilBERT** - Embeddings eficientes
- **E todos os modelos compatíveis com Transformers**

## 📋 Requisitos

- **Python 3.8+** (recomendado 3.9+)
- **4GB+ RAM** (recomendado 8GB+)
- **2GB espaço livre** para modelos
- **GPU NVIDIA** (opcional, para melhor performance)
- **Windows 10/11**, Linux ou macOS

## 🛠️ Instalação

### Windows (Recomendado)
```bash
# Método rápido
install.bat

# Executar aplicação
run.bat
```

### Manual (Todos os sistemas)
```bash
# 1. Clonar repositório
git clone https://github.com/sevenx-team/sevenx-studio.git
cd sevenx-studio

# 2. Criar ambiente virtual
python -m venv venv

# 3. Ativar ambiente (Windows)
venv\Scripts\activate.bat
# Ou Linux/macOS:
# source venv/bin/activate

# 4. Instalar dependências
pip install -r requirements.txt

# 5. Executar aplicação
python main.py
```

📖 **Guia completo**: Veja [INSTALL.md](INSTALL.md) para instruções detalhadas

## 🎯 Como Usar

### 1️⃣ **Primeira Execução**
- Execute a aplicação
- Configure o diretório de modelos (opcional)

### 2️⃣ **Baixar Modelos**
- Vá para aba **"Modelos"**
- Clique em **"Atualizar Modelos"**
- Baixe um modelo (recomendamos DialoGPT-small para começar)

### 3️⃣ **Chat**
- Volte para aba **"Chat"**
- Selecione o modelo baixado
- Digite uma mensagem e clique **"Enviar"**

### 4️⃣ **Configurações**
- Ajuste parâmetros como temperature, max tokens, etc.
- Configure temas e preferências

## 📦 Criar Executável

```bash
# Criar arquivo .exe standalone
make_exe_simple.bat

# Ou versão avançada
make_exe.bat
```

O executável será criado em `dist/SevenX Studio.exe`

## 🏗️ Arquitetura

```
SevenX Studio/
├── main.py                 # Ponto de entrada
├── src/
│   ├── core/              # Módulos principais
│   │   ├── config.py      # Gerenciamento de configurações
│   │   ├── logger.py      # Sistema de logging
│   │   └── ollama_client.py # Motor de IA (SevenXEngine)
│   └── ui/                # Interface do usuário
│       ├── main_window.py # Janela principal
│       ├── chat_widget.py # Widget de chat
│       ├── models_widget.py # Gerenciamento de modelos
│       ├── system_monitor.py # Monitor do sistema
│       └── settings_widget.py # Configurações
├── assets/                # Recursos (ícones, imagens)
├── requirements.txt       # Dependências Python
└── scripts/              # Scripts de build e instalação
```

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. **Fork** o repositório
2. **Crie** uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. **Commit** suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. **Push** para a branch (`git push origin feature/AmazingFeature`)
5. **Abra** um Pull Request

Veja [CONTRIBUTING.md](CONTRIBUTING.md) para mais detalhes.

## 📸 Screenshots

<div align="center">

### Interface Principal
![Interface Principal](assets/screenshots/main-interface.png)

### Chat em Ação
![Chat](assets/screenshots/chat-demo.png)

### Gerenciamento de Modelos
![Modelos](assets/screenshots/models-management.png)

</div>

## 🐛 Problemas Conhecidos

- **Primeira execução lenta**: Normal, modelos precisam ser carregados
- **Alto uso de RAM**: Modelos grandes consomem mais memória
- **GPU não detectada**: Verifique drivers CUDA

Veja [Issues](https://github.com/sevenx-team/sevenx-studio/issues) para problemas conhecidos e soluções.

## 📈 Roadmap

- [ ] **v1.1**: Suporte a mais modelos (Llama, Mistral)
- [ ] **v1.2**: Plugin system
- [ ] **v1.3**: API REST externa
- [ ] **v1.4**: Modo servidor
- [ ] **v2.0**: Suporte a modelos multimodais

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🙏 Agradecimentos

- [Hugging Face](https://huggingface.co/) - Pelos modelos e bibliotecas
- [PyQt](https://www.riverbankcomputing.com/software/pyqt/) - Pela interface gráfica
- [PyTorch](https://pytorch.org/) - Pelo framework de IA
- [Transformers](https://github.com/huggingface/transformers) - Pela biblioteca de modelos

## 📞 Suporte

- 🐛 **Bugs**: [GitHub Issues](https://github.com/sevenx-team/sevenx-studio/issues)
- 💬 **Discussões**: [GitHub Discussions](https://github.com/sevenx-team/sevenx-studio/discussions)
- 📧 **Email**: support@sevenx.dev
- 💬 **Discord**: [SevenX Community](https://discord.gg/sevenx)

---

<div align="center">

**⭐ Se você gostou do projeto, dê uma estrela! ⭐**

Feito com ❤️ pela equipe SevenX

</div>