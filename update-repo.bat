@echo off
echo ========================================
echo   SevenX Studio - Atualizar Repositorio
echo ========================================
echo.

echo Verificando status do Git...
git status

echo.
echo Adicionando arquivos modificados...
git add .

echo.
echo Fazendo commit das atualizacoes...
git commit -m "feat: SevenX Studio v1.0.0 - Release Candidate

🎉 APLICAÇÃO COMPLETA E FUNCIONAL:

✨ Funcionalidades Principais:
- 🤖 Motor de IA próprio (SevenXEngine) independente
- 💬 Chat interativo com modelos Hugging Face
- 📊 Monitor de sistema em tempo real
- 🎨 Interface moderna PyQt6 com tema escuro
- 🔧 5 abas de configurações avançadas
- 📦 Sistema de build automático para .exe

🔥 Modelos Suportados:
- ✅ DialoGPT Small/Medium (chat conversacional)
- ✅ GPT-2 (geração de texto)
- ❌ CodeBERT removido (não compatível com chat)

🛠️ Correções de Bugs:
- ✅ Carregamento robusto de modelos
- ✅ Mapeamento correto de nomes
- ✅ Tratamento de erros de token
- ✅ Parâmetros otimizados para chat
- ✅ Filtros para modelos incompatíveis

📁 Estrutura Completa:
- 📝 Documentação profissional (README, CONTRIBUTING, etc.)
- 🧪 Testes automatizados
- 🔄 CI/CD com GitHub Actions
- 📦 Build automático de executável
- 🎨 Templates para Issues/PRs

🚀 PRONTO PARA PRODUÇÃO!"

echo.
echo Enviando para GitHub...
git push origin main

if errorlevel 1 (
    echo.
    echo Configurando repositorio remoto...
    git remote add origin https://github.com/sevenx777-dev/SevenX-Studio.git
    git branch -M main
    git push -u origin main
)

echo.
echo ========================================
echo     Repositorio atualizado!
echo ========================================
echo.
echo Acesse: https://github.com/sevenx777-dev/SevenX-Studio
echo.
pause