# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [1.0.0] - 2025-08-07

### Adicionado
- ✨ **Motor de IA próprio (SevenXEngine)** - Independente, baseado em PyTorch
- 💬 **Chat interativo funcionando** - Respostas reais de modelos locais
- 🤖 **Suporte a DialoGPT** - Small, Medium, Large testados e funcionando
- 📊 **Monitor de sistema completo** - CPU, RAM, processos em tempo real
- 🎨 **Interface moderna PyQt6** - Tema escuro, responsiva
- 🔧 **5 abas de configurações** - Geral, Modelos, Chat, Interface, Avançado
- 📦 **Sistema de build robusto** - Criar executável .exe standalone
- 🗂️ **Gerenciamento de modelos** - Download, instalação, mapeamento inteligente
- 🔍 **Sistema de logs detalhado** - Debug e troubleshooting
- 💾 **Configurações persistentes** - Salvar preferências do usuário
- 🚀 **Scripts de instalação** - Setup automatizado para Windows
- 🧪 **Testes automatizados** - Verificar funcionamento de modelos

### Características Técnicas
- Desenvolvido em Python com PyQt6
- Arquitetura modular e extensível
- Suporte a múltiplos modelos simultaneamente
- Threading para operações não-bloqueantes
- Sistema de cache inteligente
- Configurações persistentes

### Modelos Suportados
- Llama 2 (7B, 13B, 70B)
- Mistral 7B
- Code Llama
- Vicuna
- Orca Mini
- Neural Chat
- StarCode
- E todos os modelos compatíveis com Ollama

### Requisitos do Sistema
- Python 3.8+
- 4GB+ RAM (recomendado)
- Windows 10/11, macOS, Linux
- GPU opcional para melhor performance