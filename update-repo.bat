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
git commit -m "feat: SevenX Studio totalmente funcional

✅ Funcionalidades Implementadas:
- Motor de IA próprio (SevenXEngine) funcionando
- Modelo DialoGPT Small carregado e testado
- Chat com respostas reais de IA
- Interface completa com PyQt6
- Monitor de sistema em tempo real
- Sistema de build para executável (.exe)
- Mapeamento correto de modelos
- Scripts de instalação e teste

🔧 Correções Aplicadas:
- Corrigido carregamento de modelos
- Mapeamento de nomes de modelos
- Tratamento robusto de erros
- Compatibilidade com diferentes sistemas
- Logs detalhados para debug

📦 Arquivos Principais:
- main.py - Aplicação principal
- src/core/ollama_client.py - Motor de IA
- src/ui/ - Interface gráfica
- make_exe_simple.bat - Criar executável
- test_model.py - Teste de modelos
- Documentação completa

🚀 Status: PRONTO PARA USO!"

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