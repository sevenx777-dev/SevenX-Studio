@echo off
echo ========================================
echo    SevenX Studio - Inicializar Git
echo ========================================
echo.

echo Inicializando repositorio Git...
git init

echo Adicionando arquivos...
git add .

echo Fazendo commit inicial...
git commit -m "feat: initial commit - SevenX Studio v1.0.0

- ✨ Interface completa com PyQt6
- 🤖 Motor de IA próprio (SevenXEngine)
- 💬 Chat interativo com modelos locais
- 📊 Monitor de sistema em tempo real
- 🔧 Configurações avançadas
- 📦 Sistema de build para executáveis
- 🤗 Integração com Hugging Face Hub
- 📝 Documentação completa
- 🧪 Testes automatizados
- 🔒 Suporte a modelos DialoGPT, GPT-2, CodeBERT"

echo.
echo ========================================
echo     Repositorio Git inicializado!
echo ========================================
echo.
echo Proximos passos:
echo 1. Crie um repositorio no GitHub
echo 2. Execute: git remote add origin [URL_DO_REPOSITORIO]
echo 3. Execute: git push -u origin main
echo.
pause