@echo off
echo ========================================
echo    Corrigindo CI/CD do GitHub Actions
echo ========================================
echo.

echo Adicionando arquivos corrigidos...
git add .github/workflows/

echo Fazendo commit das correcoes...
git commit -m "fix: corrigir GitHub Actions workflow

🔧 Correções aplicadas:
- Atualizado actions/upload-artifact para v4
- Simplificado workflow de build
- Removido release automático (será manual)
- Adicionado workflow dedicado para build
- Melhorado tratamento de erros

📦 Resultado esperado:
- Build automático do executável
- Artifacts disponíveis para download
- Processo mais estável e confiável"

echo Enviando para GitHub...
git push origin main

echo.
echo ========================================
echo     Correções enviadas!
echo ========================================
echo.
echo Agora o GitHub Actions deve funcionar corretamente.
echo Verifique em: https://github.com/sevenx777-dev/SevenX-Studio/actions
echo.
pause