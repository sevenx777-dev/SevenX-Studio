🚀 SevenX Studio<div align="center">Uma aplicação desktop moderna para gerenciamento e execução de modelos de IA localmente, com total privacidade e performance.📥 Download da Última Versão • 🐛 Reportar um Bug • 💬 Iniciar uma Discussão</div>✨ Características Principais🤖 Motor de IA Próprio - Engine de inferência local (SevenXEngine) baseado em PyTorch e Transformers.⚡ Streaming em Tempo Real - Receba respostas do modelo palavra por palavra, proporcionando uma experiência de chat fluida e instantânea.🤗 Integração com Hugging Face - Pesquise, baixe e gerencie milhares de modelos diretamente do Hugging Face Hub.💬 Chat Interativo - Interface de chat moderna e intuitiva para conversar com seus modelos de IA.📊 Monitor de Sistema - Acompanhe o uso de CPU, RAM e Disco em tempo real.🎨 Interface Moderna - UI responsiva construída com PyQt6, incluindo um elegante tema escuro.🔧 Configurações Avançadas - Personalize parâmetros de geração como temperature, top_p, max_tokens, e mais.🔒 Privacidade Total - Tudo roda na sua máquina. Seus dados e conversas nunca saem do seu computador.📦 Executável Standalone - Scripts inclusos para criar um arquivo .exe para fácil distribuição no Windows.🎯 Modelos SuportadosO SevenX Studio é compatível com uma vasta gama de modelos da biblioteca transformers, incluindo:Conversação: microsoft/DialoGPT (small, medium, large)Geração de Texto: gpt2, distilgpt2, EleutherAI/gpt-neo-125ME milhares de outros modelos focados em geração de texto disponíveis no Hugging Face Hub.📋 RequisitosPython 3.8+ (recomendado 3.9 ou superior)4GB+ RAM (8GB ou mais é recomendado para modelos maiores)2GB de espaço livre em disco para instalar modelosGPU NVIDIA com CUDA (opcional, mas altamente recomendado para melhor performance)Sistema Operacional: Windows 10/11, Linux ou macOS🛠️ InstalaçãoWindows (Método Rápido)# 1. Instala as dependências em um ambiente virtual
install.bat

# 2. Executa a aplicação
run.bat
Manual (Para todos os sistemas)# 1. Clone o repositório
git clone [https://github.com/sevenx777-dev/SevenX-Studio.git](https://github.com/sevenx777-dev/SevenX-Studio.git)
cd SevenX-Studio

# 2. Crie e ative um ambiente virtual
python -m venv venv
# No Windows:
venv\Scripts\activate
# No Linux/macOS:
# source venv/bin/activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Execute a aplicação
python main.py
🎯 Como UsarExecute a Aplicação: Inicie o SevenX Studio usando run.bat ou python main.py.Encontre um Modelo: Vá para a aba "Modelos". Use a barra de pesquisa para encontrar um modelo no Hugging Face Hub (ex: microsoft/DialoGPT-small).Baixe o Modelo: Clique no botão "Baixar" ao lado do modelo desejado e aguarde a conclusão.Inicie o Chat: Vá para a aba "Chat". O modelo que você baixou aparecerá na lista de seleção. Ele será carregado automaticamente na primeira vez que for selecionado.Converse: Digite sua mensagem e pressione Enter para começar a interagir com a IA!📦 Criar Executável (Windows)Para empacotar a aplicação em um único arquivo .exe, use os scripts fornecidos:# Cria um executável simples (mais rápido)
build-simple.bat

# Cria um executável avançado com mais opções
build-advanced.bat
O arquivo final estará localizado na pasta dist/.🏗️ Arquitetura do ProjetoSevenX-Studio/
├── main.py                 # Ponto de entrada da aplicação
├── src/
│   ├── core/               # Módulos principais do backend
│   │   ├── config.py       # Gerenciamento de configurações
│   │   ├── huggingface_client.py # Camada de compatibilidade (cliente)
│   │   └── sevenx_engine.py  # O motor de IA principal
│   └── ui/                 # Módulos da interface gráfica (PyQt6)
│       ├── main_window.py    # A janela principal
│       ├── chat_widget_simple.py # O widget de chat
│       ├── models_widget.py  # O widget de gerenciamento de modelos
│       ├── system_monitor.py # O widget do monitor de sistema
│       └── settings_widget.py # O widget de configurações
├── assets/                 # Ícones, banners e outros recursos visuais
├── requirements.txt        # Dependências do projeto
└── scripts/                # Scripts de build e instalação (.bat)
🤝 ContribuindoContribuições são muito bem-vindas! Se você tem uma ideia ou encontrou um bug, por favor:Faça um Fork do repositório.Crie uma nova Branch (git checkout -b feature/MinhaFeature).Faça o Commit das suas alterações (git commit -m 'feat: Adiciona MinhaFeature').Faça o Push para a sua branch (git push origin feature/MinhaFeature).Abra um Pull Request.Para mais detalhes, veja nosso guia de contribuição CONTRIBUTING.md.📸 Screenshots<div align="center">Interface PrincipalChat em Ação|