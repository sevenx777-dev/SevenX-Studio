🚀 SevenX Studio<div align="center">Uma plataforma de IA desktop, local e privada. Execute, gira e converse com modelos de linguagem open-source com total controlo e performance.📥 Baixar a Última Versão • 🐛 Reportar um Bug • 💬 Iniciar uma Discussão</div>✨ Funcionalidades PrincipaisMulti-Backend Flexível: Escolha como executar os seus modelos:🤖 SevenX Engine (Local): Motor de inferência integrado para modelos Hugging Face, otimizado para rodar localmente em CPU e GPU (NVIDIA).🦙 Integração com Ollama: Conecte-se ao seu servidor Ollama para usar qualquer modelo da sua biblioteca, incluindo os quantizados (GGUF).⚡ Performance Otimizada:Streaming em Tempo Real: Receba respostas do modelo palavra por palavra para uma experiência de chat fluida.Modo Leve: Ative para reduzir o consumo de CPU em computadores com menos recursos.Gestão de Memória Inteligente: Apenas um modelo fica ativo na memória por vez, economizando RAM.🤗 Gestor de Modelos Hugging Face:Pesquise, baixe e gira milhares de modelos diretamente do Hugging Face Hub.Suporte para modelos protegidos através de token de acesso.📊 Monitor de Sistema Completo:Acompanhe o uso de CPU, RAM e Disco.Monitoramento de GPU NVIDIA: Veja o uso de VRAM, a utilização e a temperatura da sua placa de vídeo.🔒 Privacidade Total: Tudo roda na sua máquina. Os seus dados, prompts e conversas nunca saem do seu computador.🎨 Interface Moderna e Configurável:UI responsiva construída com PyQt6.Personalize parâmetros de geração, tema visual, e mais na aba de configurações.🎯 Backends e Modelos SuportadosBackendFormato do ModeloExemplosIdeal ParaSevenX EnginePadrão Transformersmicrosoft/DialoGPT-small, gpt2, google/gemma-2b-itRodar modelos Hugging Face diretamente, com suporte a GPU.OllamaGGUF e outrosllama3, phi3, mistralExecutar modelos quantizados de alta performance no CPU.🛠️ InstalaçãoWindows (Método Rápido)# 1. Instala as dependências num ambiente virtual
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
🎯 Como UsarExecute a Aplicação: Inicie o SevenX Studio.Escolha o Serviço: Na aba "Chat", selecione se quer usar os modelos locais (SevenX (Local)) ou os do Ollama.Selecione um Modelo:Se escolheu Ollama, a lista mostrará os modelos que você já tem no Ollama.Se escolheu SevenX (Local), vá para a aba "Modelos" para pesquisar e baixar modelos do Hugging Face.Converse: Volte para a aba "Chat", digite a sua mensagem e pressione Enter!🏗️ Arquitetura do ProjetoSevenX-Studio/
├── main.py                 # Ponto de entrada da aplicação
├── src/
│   ├── core/               # Módulos principais do backend
│   │   ├── config.py       # Gestão de configurações
│   │   ├── ollama_client.py  # Cliente para a API do Ollama
│   │   └── sevenx_engine.py  # O motor de IA para modelos Transformers
│   └── ui/                 # Módulos da interface gráfica (PyQt6)
│       ├── main_window.py    # A janela principal
│       ├── chat_widget_simple.py # O widget de chat
│       ├── models_widget.py  # O widget de gestão de modelos
│       └── ...               # Outros widgets da UI
├── assets/                 # Ícones, banners e outros recursos visuais
└── requirements.txt        # Dependências do projeto
🤝 ContribuindoContribuições são muito bem-vindas! Se tem uma ideia ou encontrou um bug, por favor, abra uma Issue ou um Pull Request.📄 LicençaEste projeto está licenciado sob a Licença MIT. Veja o ficheiro LICENSE para mais detalhes.<div align="center">⭐ Se gostou do projeto, considere dar uma estrela no GitHub! ⭐