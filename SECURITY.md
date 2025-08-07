# Política de Segurança

## Versões Suportadas

Atualmente, oferecemos suporte de segurança para as seguintes versões do SevenX Studio:

| Versão | Suportada          |
| ------ | ------------------ |
| 1.0.x  | :white_check_mark: |
| < 1.0  | :x:                |

## Reportar uma Vulnerabilidade

A segurança do SevenX Studio é uma prioridade. Se você descobrir uma vulnerabilidade de segurança, por favor, nos ajude a resolvê-la de forma responsável.

### Como Reportar

**NÃO** abra uma issue pública para vulnerabilidades de segurança.

Em vez disso, envie um email para: **security@sevenx.dev**

### Informações a Incluir

Por favor, inclua as seguintes informações em seu relatório:

- **Descrição** da vulnerabilidade
- **Passos para reproduzir** o problema
- **Impacto potencial** da vulnerabilidade
- **Versão afetada** do SevenX Studio
- **Ambiente** (OS, Python version, etc.)
- **Possível solução** (se você tiver uma)

### O que Esperar

1. **Confirmação**: Confirmaremos o recebimento do seu relatório em até 48 horas
2. **Avaliação**: Avaliaremos a vulnerabilidade e determinaremos sua gravidade
3. **Correção**: Trabalharemos em uma correção e a testaremos
4. **Divulgação**: Coordenaremos a divulgação pública após a correção

### Cronograma de Resposta

- **Crítica**: 24-48 horas
- **Alta**: 3-7 dias
- **Média**: 1-2 semanas
- **Baixa**: 2-4 semanas

### Divulgação Responsável

Pedimos que você:

- **Não divulgue** a vulnerabilidade publicamente até que tenhamos uma correção
- **Não acesse** dados que não são seus
- **Não modifique** ou delete dados
- **Não execute** ataques de negação de serviço

### Reconhecimento

Reconhecemos publicamente pesquisadores de segurança responsáveis que nos ajudam a melhorar a segurança do SevenX Studio (a menos que prefiram permanecer anônimos).

## Práticas de Segurança

### Para Usuários

- **Mantenha** o SevenX Studio atualizado
- **Use** apenas modelos de fontes confiáveis
- **Não execute** código não confiável
- **Configure** adequadamente as permissões de arquivo

### Para Desenvolvedores

- **Valide** todas as entradas do usuário
- **Use** bibliotecas atualizadas
- **Implemente** logging de segurança
- **Teste** regularmente para vulnerabilidades

## Recursos de Segurança

### Isolamento de Modelos

- Modelos são executados em ambiente isolado
- Acesso limitado ao sistema de arquivos
- Monitoramento de uso de recursos

### Proteção de Dados

- Dados do usuário permanecem locais
- Conversas são criptografadas em repouso
- Logs não contêm informações sensíveis

### Atualizações de Segurança

- Verificação automática de atualizações
- Assinatura digital de releases
- Canal seguro para downloads

## Contato

Para questões de segurança:
- **Email**: security@sevenx.dev
- **PGP Key**: [Chave Pública](https://sevenx.dev/pgp-key.asc)

Para outras questões:
- **Issues**: [GitHub Issues](https://github.com/sevenx-team/sevenx-studio/issues)
- **Email**: support@sevenx.dev

---

**Obrigado por ajudar a manter o SevenX Studio seguro!**