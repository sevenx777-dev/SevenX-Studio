"""
Widget de chat para interação com modelos de IA
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
                            QLineEdit, QPushButton, QComboBox, QLabel, 
                            QSplitter, QScrollArea, QFrame, QSlider,
                            QSpinBox, QDoubleSpinBox, QGroupBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QTextCursor, QPixmap

import json
from datetime import datetime
from typing import Dict, List, Optional

class ChatMessage(QFrame):
    """Widget para exibir uma mensagem do chat"""
    
    def __init__(self, message: str, is_user: bool = True, timestamp: str = None):
        super().__init__()
        self.setup_ui(message, is_user, timestamp)
    
    def setup_ui(self, message: str, is_user: bool, timestamp: str):
        """Configurar interface da mensagem"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Header com autor e timestamp
        header_layout = QHBoxLayout()
        
        author_label = QLabel("Você" if is_user else "Assistente")
        author_label.setStyleSheet(f"""
            font-weight: bold;
            color: {'#0078d4' if is_user else '#00a86b'};
        """)
        
        if timestamp:
            time_label = QLabel(timestamp)
            time_label.setStyleSheet("color: #888888; font-size: 10px;")
            header_layout.addWidget(time_label)
        
        header_layout.addWidget(author_label)
        header_layout.addStretch()
        
        # Mensagem
        message_text = QTextEdit()
        message_text.setPlainText(message)
        message_text.setReadOnly(True)
        message_text.setMaximumHeight(200)
        message_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {'#404040' if is_user else '#2d5a2d'};
                border: 1px solid #555555;
                border-radius: 8px;
                padding: 8px;
                color: white;
            }}
        """)
        
        layout.addLayout(header_layout)
        layout.addWidget(message_text)
        
        # Estilo do frame
        self.setStyleSheet("""
            QFrame {
                background-color: #3c3c3c;
                border-radius: 8px;
                margin: 2px;
            }
        """)

class ChatWorker(QThread):
    """Worker thread para comunicação com modelos de IA"""
    
    response_chunk = pyqtSignal(str)
    response_completed = pyqtSignal()
    error_occurred = pyqtSignal(str)
    
    def __init__(self, message: str, model: str, config: Dict, ai_engine):
        super().__init__()
        self.message = message
        self.model = model
        self.config = config
        self.ai_engine = ai_engine
        self.should_stop = False
    
    def run(self):
        """Executar requisição para o modelo"""
        try:
            # Verificar se o modelo está disponível
            if self.model not in [m.name for m in self.ai_engine.list_models()]:
                self.error_occurred.emit(f"Modelo {self.model} não encontrado")
                return
            
            self.response_chunk.emit(f"Processando com {self.model}...")
            
            # Gerar resposta usando o SevenX Engine
            messages = [{"role": "user", "content": self.message}]
            result = self.ai_engine.chat(self.model, messages, self.config)
            
            if "error" in result:
                self.error_occurred.emit(result["error"])
                return
            
            # Simular streaming dividindo a resposta
            response = result.get("message", {}).get("content", "Sem resposta")
            words = response.split()
            
            for word in words:
                if self.should_stop:
                    break
                self.response_chunk.emit(word + " ")
                self.msleep(50)  # Pequena pausa para simular streaming
            
            self.response_completed.emit()
            
        except Exception as e:
            self.error_occurred.emit(str(e))
    
    def stop(self):
        """Parar geração"""
        self.should_stop = True

class ChatWidget(QWidget):
    """Widget principal do chat"""
    
    def __init__(self, config, ai_engine):
        super().__init__()
        self.config = config
        self.ai_engine = ai_engine
        self.conversation_history = []
        self.current_worker = None
        self.current_response = ""
        
        # Importar e inicializar cliente Hugging Face
        from ..core.huggingface_client import HuggingFaceClient
        self.hf_client = HuggingFaceClient(str(config.models_directory))
        
        self.setup_ui()
        self.load_models()
    
    def setup_ui(self):
        """Configurar interface do usuário"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Splitter principal
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)
        
        # Área de chat
        chat_area = self.create_chat_area()
        splitter.addWidget(chat_area)
        
        # Painel de configurações
        settings_panel = self.create_settings_panel()
        splitter.addWidget(settings_panel)
        
        # Configurar proporções
        splitter.setSizes([800, 300])
    
    def create_chat_area(self) -> QWidget:
        """Criar área de chat"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Área de mensagens
        self.messages_scroll = QScrollArea()
        self.messages_scroll.setWidgetResizable(True)
        self.messages_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        self.messages_widget = QWidget()
        self.messages_layout = QVBoxLayout(self.messages_widget)
        self.messages_layout.addStretch()
        
        self.messages_scroll.setWidget(self.messages_widget)
        layout.addWidget(self.messages_scroll)
        
        # Área de entrada
        input_layout = QHBoxLayout()
        
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Digite sua mensagem...")
        self.message_input.returnPressed.connect(self.send_message)
        
        self.send_button = QPushButton("Enviar")
        self.send_button.clicked.connect(self.send_message)
        
        input_layout.addWidget(self.message_input)
        input_layout.addWidget(self.send_button)
        
        layout.addLayout(input_layout)
        
        return widget
    
    def create_settings_panel(self) -> QWidget:
        """Criar painel de configurações"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Seleção de modelo
        model_group = QGroupBox("Modelo")
        model_layout = QVBoxLayout(model_group)
        
        self.model_combo = QComboBox()
        model_layout.addWidget(self.model_combo)
        
        layout.addWidget(model_group)
        
        # Parâmetros do modelo
        params_group = QGroupBox("Parâmetros")
        params_layout = QVBoxLayout(params_group)
        
        # Temperature
        temp_layout = QHBoxLayout()
        temp_layout.addWidget(QLabel("Temperature:"))
        self.temperature_spin = QDoubleSpinBox()
        self.temperature_spin.setRange(0.0, 2.0)
        self.temperature_spin.setSingleStep(0.1)
        self.temperature_spin.setValue(self.config.get("chat_settings.temperature", 0.7))
        temp_layout.addWidget(self.temperature_spin)
        params_layout.addLayout(temp_layout)
        
        # Max Tokens
        tokens_layout = QHBoxLayout()
        tokens_layout.addWidget(QLabel("Max Tokens:"))
        self.max_tokens_spin = QSpinBox()
        self.max_tokens_spin.setRange(1, 8192)
        self.max_tokens_spin.setValue(self.config.get("chat_settings.max_tokens", 2048))
        tokens_layout.addWidget(self.max_tokens_spin)
        params_layout.addLayout(tokens_layout)
        
        # Top P
        top_p_layout = QHBoxLayout()
        top_p_layout.addWidget(QLabel("Top P:"))
        self.top_p_spin = QDoubleSpinBox()
        self.top_p_spin.setRange(0.0, 1.0)
        self.top_p_spin.setSingleStep(0.1)
        self.top_p_spin.setValue(self.config.get("chat_settings.top_p", 0.9))
        top_p_layout.addWidget(self.top_p_spin)
        params_layout.addLayout(top_p_layout)
        
        layout.addWidget(params_group)
        
        # Botões de ação
        actions_group = QGroupBox("Ações")
        actions_layout = QVBoxLayout(actions_group)
        
        self.new_chat_btn = QPushButton("Nova Conversa")
        self.new_chat_btn.clicked.connect(self.new_conversation)
        actions_layout.addWidget(self.new_chat_btn)
        
        self.save_chat_btn = QPushButton("Salvar Conversa")
        self.save_chat_btn.clicked.connect(self.save_conversation)
        actions_layout.addWidget(self.save_chat_btn)
        
        self.clear_chat_btn = QPushButton("Limpar Chat")
        self.clear_chat_btn.clicked.connect(self.clear_chat)
        actions_layout.addWidget(self.clear_chat_btn)
        
        layout.addWidget(actions_group)
        
        layout.addStretch()
        
        return widget
    
    def load_models(self):
        """Carregar lista de modelos disponíveis"""
        try:
            # Obter modelos instalados do SevenX Engine
            installed_models = self.ai_engine.list_models()
            
            self.model_combo.clear()
            
            if not installed_models:
                self.model_combo.addItem("Nenhum modelo instalado", "")
                return
            
            for model in installed_models:
                display_name = f"{model.name}"
                if model.status == "installed":
                    display_name += " ✓"
                
                self.model_combo.addItem(display_name, model.name)
            
            # Selecionar primeiro modelo
            if self.model_combo.count() > 0:
                self.model_combo.setCurrentIndex(0)
                    
        except Exception as e:
            print(f"Erro ao carregar modelos: {e}")
            self.model_combo.clear()
            self.model_combo.addItem("Erro ao carregar modelos", "")
            # Fallback para lista básica
            self.model_combo.clear()
            self.model_combo.addItem("Nenhum modelo disponível", "")
    
    def send_message(self):
        """Enviar mensagem para o modelo"""
        message = self.message_input.text().strip()
        if not message:
            return
        
        # Adicionar mensagem do usuário
        self.add_message(message, is_user=True)
        self.message_input.clear()
        
        # Desabilitar entrada durante processamento
        self.message_input.setEnabled(False)
        self.send_button.setEnabled(False)
        self.send_button.setText("Enviando...")
        
        # Criar worker para processar mensagem
        model_id = self.model_combo.currentData()
        if not model_id:
            self.add_message("Erro: Nenhum modelo selecionado", is_user=False)
            self.message_input.setEnabled(True)
            self.send_button.setEnabled(True)
            self.send_button.setText("Enviar")
            return
        
        config = {
            "temperature": self.temperature_spin.value(),
            "max_tokens": self.max_tokens_spin.value(),
            "top_p": self.top_p_spin.value()
        }
        
        self.current_response = ""
        self.current_worker = ChatWorker(message, model_id, config, self.ai_engine)
        self.current_worker.response_chunk.connect(self.on_response_chunk)
        self.current_worker.response_completed.connect(self.on_response_completed)
        self.current_worker.error_occurred.connect(self.on_error_occurred)
        self.current_worker.start()
    
    def add_message(self, message: str, is_user: bool = True):
        """Adicionar mensagem ao chat"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        message_widget = ChatMessage(message, is_user, timestamp)
        
        # Inserir antes do stretch
        self.messages_layout.insertWidget(self.messages_layout.count() - 1, message_widget)
        
        # Scroll para o final
        QTimer.singleShot(100, self.scroll_to_bottom)
        
        # Adicionar ao histórico
        self.conversation_history.append({
            "message": message,
            "is_user": is_user,
            "timestamp": timestamp
        })
    
    def scroll_to_bottom(self):
        """Fazer scroll para o final da conversa"""
        scrollbar = self.messages_scroll.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def on_response_chunk(self, chunk: str):
        """Callback quando chunk de resposta é recebido"""
        self.current_response += chunk
        
        # Atualizar a última mensagem ou criar nova se necessário
        if hasattr(self, 'current_response_widget'):
            # Atualizar widget existente - buscar o QTextEdit dentro do widget
            try:
                text_widget = self.current_response_widget.findChild(QTextEdit)
                if text_widget:
                    text_widget.setPlainText(self.current_response)
            except:
                pass
        else:
            # Criar nova mensagem
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.current_response_widget = ChatMessage(self.current_response, is_user=False, timestamp=timestamp)
            self.messages_layout.insertWidget(self.messages_layout.count() - 1, self.current_response_widget)
        
        # Scroll para o final
        QTimer.singleShot(10, self.scroll_to_bottom)
    
    def on_response_completed(self):
        """Callback quando resposta é completada"""
        # Adicionar ao histórico
        if self.current_response:
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.conversation_history.append({
                "message": self.current_response,
                "is_user": False,
                "timestamp": timestamp
            })
        
        # Limpar referência
        if hasattr(self, 'current_response_widget'):
            delattr(self, 'current_response_widget')
        
        self.current_response = ""
        
        # Reabilitar entrada
        self.message_input.setEnabled(True)
        self.send_button.setEnabled(True)
        self.send_button.setText("Enviar")
        
        # Focar na entrada
        self.message_input.setFocus()
    
    def on_error_occurred(self, error: str):
        """Callback quando erro ocorre"""
        self.add_message(f"Erro: {error}", is_user=False)
        
        # Limpar resposta atual se houver
        if hasattr(self, 'current_response_widget'):
            delattr(self, 'current_response_widget')
        self.current_response = ""
        
        # Reabilitar entrada
        self.message_input.setEnabled(True)
        self.send_button.setEnabled(True)
        self.send_button.setText("Enviar")
    
    def new_conversation(self):
        """Iniciar nova conversa"""
        self.clear_chat()
        self.add_message("Nova conversa iniciada! Como posso ajudar?", is_user=False)
    
    def clear_chat(self):
        """Limpar chat"""
        # Remover todas as mensagens exceto o stretch
        for i in reversed(range(self.messages_layout.count() - 1)):
            child = self.messages_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        self.conversation_history.clear()
    
    def save_conversation(self):
        """Salvar conversa atual"""
        if not self.conversation_history:
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"conversa_{timestamp}.json"
        filepath = self.config.conversations_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.conversation_history, f, indent=2, ensure_ascii=False)
            
            self.add_message(f"Conversa salva em: {filename}", is_user=False)
        except Exception as e:
            self.add_message(f"Erro ao salvar conversa: {e}", is_user=False)