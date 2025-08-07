# 🤝 Contribuindo para o SevenX Studio

Obrigado por considerar contribuir para o SevenX Studio! Este documento fornece diretrizes para contribuições.

## 📋 Código de Conduta

Este projeto adere ao [Código de Conduta](CODE_OF_CONDUCT.md). Ao participar, você deve seguir este código.

## 🚀 Como Contribuir

### 🐛 Reportar Bugs

1. **Verifique** se o bug já foi reportado nas [Issues](https://github.com/sevenx-team/sevenx-studio/issues)
2. **Crie** uma nova issue com:
   - Título claro e descritivo
   - Passos para reproduzir
   - Comportamento esperado vs atual
   - Screenshots (se aplicável)
   - Informações do sistema (OS, Python version, etc.)

### 💡 Sugerir Melhorias

1. **Abra** uma issue com label `enhancement`
2. **Descreva** a melhoria proposta
3. **Explique** por que seria útil
4. **Forneça** exemplos de uso

### 🔧 Contribuir com Código

#### Configuração do Ambiente

```bash
# 1. Fork e clone o repositório
git clone https://github.com/SEU_USERNAME/sevenx-studio.git
cd sevenx-studio

# 2. Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/macOS
# ou
venv\Scripts\activate.bat  # Windows

# 3. Instalar dependências de desenvolvimento
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 4. Instalar pre-commit hooks
pre-commit install
```

#### Processo de Desenvolvimento

1. **Crie** uma branch para sua feature:
   ```bash
   git checkout -b feature/nome-da-feature
   ```

2. **Faça** suas alterações seguindo os padrões:
   - Use docstrings em português
   - Siga PEP 8
   - Adicione testes quando necessário
   - Mantenha compatibilidade com Python 3.8+

3. **Teste** suas alterações:
   ```bash
   # Executar testes
   python -m pytest tests/
   
   # Verificar estilo de código
   flake8 src/
   
   # Verificar tipos
   mypy src/
   ```

4. **Commit** suas mudanças:
   ```bash
   git add .
   git commit -m "feat: adicionar nova funcionalidade X"
   ```

5. **Push** para sua branch:
   ```bash
   git push origin feature/nome-da-feature
   ```

6. **Abra** um Pull Request

#### Padrões de Commit

Use [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` - Nova funcionalidade
- `fix:` - Correção de bug
- `docs:` - Mudanças na documentação
- `style:` - Formatação, sem mudança de código
- `refactor:` - Refatoração de código
- `test:` - Adicionar ou corrigir testes
- `chore:` - Tarefas de manutenção

Exemplos:
```
feat: adicionar suporte a modelo Llama
fix: corrigir erro de carregamento de modelo
docs: atualizar guia de instalação
```

## 🏗️ Estrutura do Projeto

```
SevenX Studio/
├── src/
│   ├── core/              # Lógica principal
│   │   ├── config.py      # Configurações
│   │   ├── logger.py      # Sistema de logging
│   │   └── ollama_client.py # Motor de IA
│   └── ui/                # Interface do usuário
│       ├── main_window.py # Janela principal
│       ├── chat_widget.py # Widget de chat
│       └── ...
├── tests/                 # Testes automatizados
├── docs/                  # Documentação
├── assets/                # Recursos (ícones, etc.)
└── scripts/              # Scripts de build
```

## 🧪 Testes

### Executar Testes

```bash
# Todos os testes
python -m pytest

# Testes específicos
python -m pytest tests/test_core/

# Com cobertura
python -m pytest --cov=src tests/
```

### Escrever Testes

- Use `pytest` para testes
- Coloque testes em `tests/`
- Nomeie arquivos como `test_*.py`
- Use fixtures para setup comum

Exemplo:
```python
import pytest
from src.core.config import Config

def test_config_creation():
    config = Config()
    assert config is not None
    assert config.theme == "dark"
```

## 📝 Documentação

### Docstrings

Use docstrings em português seguindo o padrão Google:

```python
def load_model(self, model_name: str) -> bool:
    """Carregar modelo na memória.
    
    Args:
        model_name: Nome do modelo a ser carregado.
        
    Returns:
        True se o modelo foi carregado com sucesso, False caso contrário.
        
    Raises:
        ModelNotFoundError: Se o modelo não for encontrado.
    """
```

### Comentários

- Use comentários em português
- Explique o "porquê", não o "o quê"
- Mantenha comentários atualizados

## 🎨 Padrões de Interface

### PyQt6

- Use layouts responsivos
- Implemente temas escuro/claro
- Mantenha consistência visual
- Teste em diferentes resoluções

### Estilo de Código

```python
# Bom
class ChatWidget(QWidget):
    """Widget para interface de chat."""
    
    def __init__(self, config: Config):
        super().__init__()
        self.config = config
        self.setup_ui()
    
    def setup_ui(self) -> None:
        """Configurar interface do usuário."""
        layout = QVBoxLayout(self)
        # ...
```

## 🔍 Code Review

### Checklist para Pull Requests

- [ ] Código segue padrões do projeto
- [ ] Testes passam
- [ ] Documentação atualizada
- [ ] Sem conflitos de merge
- [ ] Commit messages seguem padrão
- [ ] Funcionalidade testada manualmente

### O que Procuramos

- **Funcionalidade**: Código faz o que deveria fazer?
- **Legibilidade**: Código é fácil de entender?
- **Performance**: Não introduz lentidão desnecessária?
- **Segurança**: Não introduz vulnerabilidades?
- **Compatibilidade**: Funciona em diferentes sistemas?

## 🏷️ Versionamento

Seguimos [Semantic Versioning](https://semver.org/):

- **MAJOR**: Mudanças incompatíveis na API
- **MINOR**: Funcionalidades compatíveis
- **PATCH**: Correções de bugs compatíveis

## 📞 Precisa de Ajuda?

- 💬 **Discord**: [SevenX Community](https://discord.gg/sevenx)
- 📧 **Email**: dev@sevenx.dev
- 🐛 **Issues**: [GitHub Issues](https://github.com/sevenx-team/sevenx-studio/issues)

## 🙏 Reconhecimento

Todos os contribuidores são listados no [CONTRIBUTORS.md](CONTRIBUTORS.md) e no README principal.

---

**Obrigado por contribuir para o SevenX Studio! 🚀**