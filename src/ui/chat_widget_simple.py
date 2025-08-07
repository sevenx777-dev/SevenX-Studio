"""
Arquivo: chat_widget_simple.py
Descrição: Widget de chat com correção para o erro de runtime ao limpar a conversa.
"""
import json
from datetime import datetime
from typing import Dict, List, Optional
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
                             QLineEdit, QPushButton, QComboBox, QLabel, 
                             QSplitter, QScrollArea, QFrame,
                             QSpinBox, QDoubleSpinBox, QGroupBox, QMessageBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QMetaObject, Qt
from PyQt6.QtGui import QFont, QTextCursor
from ..core.sevenx_engine import SevenXEngine, ModelInfo
from ..core.ollama_client import OllamaClient
from ..core.config import Config
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatMessage(QFrame):
    def __init__(self, text: str, author_name: str, is_user: bool):
        super().__init__()
        self.is_user = is_user
        self.text_edit = QTextEdit()
        self.setup_ui(text, author_name)
    
    def setup_ui(self, text: str, author_name: str):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        bubble_layout = QVBoxLayout()
        bubble_frame = QFrame()
        bubble_frame.setLayout(bubble_layout)
        header_layout = QHBoxLayout()
        author_icon = "👤" if self.is_user else "🤖"
        header_label = QLabel(f"{author_icon} {author_name}")
        author_color = "#0099ff" if self.is_user else "#00a86b"
        header_label.setStyleSheet(f"font-weight: bold; color: {author_color};")
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        self.text_edit.setPlainText(text)
        self.text_edit.setReadOnly(True)
        self.text_edit.setMinimumHeight(40)
        self.text_edit.setStyleSheet("border: none; background: transparent; color: white;")
        bubble_layout.addLayout(header_layout)
        bubble_layout.addWidget(self.text_edit)
        if self.is_user:
            main_layout.addStretch()
            main_layout.addWidget(bubble_frame)
        else:
            main_layout.addWidget(bubble_frame)
            main_layout.addStretch()
        bubble_bg_color = "#2c3e50" if self.is_user else "#34495e"
        bubble_frame.setStyleSheet(f"QFrame {{ background-color: {bubble_bg_color}; border-radius: 12px; padding: 8px; }}")
        self.layout().setSizeConstraint(QVBoxLayout.SizeConstraint.SetFixedSize)
    
    def update_text(self, new_text: str):
        self.text_edit.setPlainText(new_text)
        doc_height = self.text_edit.document().size().height()
        self.text_edit.setFixedHeight(int(doc_height) + 10)

class ChatWorker(QThread):
    response_chunk = pyqtSignal(str)
    response_completed = pyqtSignal()
    error_occurred = pyqtSignal(str)
    progress_update = pyqtSignal(str)
    
    def __init__(self, service: str, messages: List[Dict], model_id: str, config: Config, ai_engine: SevenXEngine, ollama_client: OllamaClient):
        super().__init__()
        self.service = service
        self.messages = messages
        self.model_id = model_id
        self.config = config
        self.ai_engine = ai_engine
        self.ollama_client = ollama_client
        self.should_stop = False
    
    def run(self):
        try:
            stream_delay = 30 if self.config.get("ui_settings.lite_mode") else 50
            generation_config = self.config.get("chat_settings", {})
            
            # Aplicar configurações específicas para cada serviço
            if self.service == "Ollama":
                # Para Ollama, ajustar parâmetros compatíveis
                ollama_config = generation_config.copy()
                # Mapear parâmetros para Ollama
                if "max_tokens" in ollama_config:
                    ollama_config["num_predict"] = ollama_config.pop("max_tokens", 1024)
                if "temperature" in ollama_config:
                    ollama_config["temperature"] = max(0.0, min(2.0, ollama_config["temperature"]))
                if "top_p" in ollama_config:
                    ollama_config["top_p"] = max(0.0, min(1.0, ollama_config["top_p"]))
                if "top_k" in ollama_config:
                    ollama_config["top_k"] = max(1, ollama_config["top_k"])
                
                stream_generator = self.ollama_client.chat_stream(self.model_id, self.messages, ollama_config)
            else: # Padrão é o SevenX Engine
                # Para SevenX, ajustar parâmetros para Transformers
                transformers_config = generation_config.copy()
                # Mapear parâmetros para Transformers
                if "max_tokens" in transformers_config:
                    transformers_config["max_new_tokens"] = transformers_config.pop("max_tokens", 2048)
                if "temperature" in transformers_config:
                    transformers_config["temperature"] = max(0.0, min(2.0, transformers_config["temperature"]))
                if "top_p" in transformers_config:
                    transformers_config["top_p"] = max(0.0, min(1.0, transformers_config["top_p"]))
                if "top_k" in transformers_config:
                    transformers_config["top_k"] = max(1, transformers_config["top_k"])
                
                stream_generator = self.ai_engine.generate_stream(self.model_id, self.messages, transformers_config)
            
            for chunk in stream_generator:
                if self.should_stop:
                    break
                if "Erro:" in chunk:
                    self.error_occurred.emit(chunk)
                    return
                self.response_chunk.emit(chunk)
                self.msleep(stream_delay)
                
        except Exception as e:
            logger.error(f"Erro no worker: {e}")
            self.error_occurred.emit(f"Erro inesperado no worker: {e}")
        finally:
            self.response_completed.emit()
    
    def stop(self):
        self.should_stop = True

class ChatWidget(QWidget):
    def __init__(self, config: Config, ai_engine: SevenXEngine, ollama_client: OllamaClient):
        super().__init__()
        self.config = config
        self.ai_engine = ai_engine
        self.ollama_client = ollama_client
        self.conversation_history = []
        self.current_worker = None
        self.current_response_widget = None
        self.is_generating = False
        self.setup_ui()
        self.on_service_changed()
    
    def create_settings_panel(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Grupo de Serviço
        service_group = QGroupBox("Serviço de IA")
        service_layout = QVBoxLayout(service_group)
        self.service_combo = QComboBox()
        self.service_combo.addItems(["SevenX (Local)", "Ollama"])
        self.service_combo.currentTextChanged.connect(self.on_service_changed)
        service_layout.addWidget(self.service_combo)
        layout.addWidget(service_group)
        
        # Grupo de Modelo
        model_group = QGroupBox("Modelo")
        model_layout = QVBoxLayout(model_group)
        self.model_combo = QComboBox()
        self.model_combo.currentTextChanged.connect(self.on_model_selected)
        model_layout.addWidget(self.model_combo)
        layout.addWidget(model_group)
        
        # Grupo de Parâmetros
        params_group = QGroupBox("Parâmetros de Geração")
        params_layout = QVBoxLayout(params_group)
        
        # Temperature
        self.temperature_spin = self.create_parameter_spinbox(
            params_layout, "Temperatura:", 0.0, 2.0, 0.1, "chat_settings.temperature", 0.7
        )
        
        # Max Tokens
        self.max_tokens_spin = self.create_parameter_spinbox(
            params_layout, "Max. Tokens:", 1, 8192, 10, "chat_settings.max_tokens", 2048, is_double=False
        )
        
        # Top P
        self.top_p_spin = self.create_parameter_spinbox(
            params_layout, "Top P:", 0.0, 1.0, 0.05, "chat_settings.top_p", 0.9
        )
        
        # Top K
        self.top_k_spin = self.create_parameter_spinbox(
            params_layout, "Top K:", 1, 100, 1, "chat_settings.top_k", 40, is_double=False
        )
        
        layout.addWidget(params_group)
        
        # Grupo de Ações
        actions_group = QGroupBox("Ações")
        actions_layout = QVBoxLayout(actions_group)
        
        self.new_chat_btn = QPushButton("Nova Conversa")
        self.new_chat_btn.clicked.connect(self.new_conversation)
        actions_layout.addWidget(self.new_chat_btn)
        
        self.clear_chat_btn = QPushButton("Limpar Chat")
        self.clear_chat_btn.clicked.connect(self.clear_chat)
        actions_layout.addWidget(self.clear_chat_btn)
        
        layout.addWidget(actions_group)
        layout.addStretch()
        return widget
    
    def on_service_changed(self):
        """Atualiza a lista de modelos quando o serviço muda."""
        service = self.service_combo.currentText()
        self.model_combo.clear()
        models = []
        
        try:
            if service == "Ollama":
                models = self.ollama_client.list_models()
            else: # SevenX (Local)
                models = self.ai_engine.list_installed_models()
                
            if not models:
                self.model_combo.addItem(f"Nenhum modelo encontrado para {service}")
                self.model_combo.setEnabled(False)
                return
                
            self.model_combo.setEnabled(True)
            for model in models:
                if isinstance(model, ModelInfo):
                    name = model.name
                    model_id = model.name
                else:
                    name = model.get('name', '')
                    model_id = model.get('id', '')
                    
                if name and model_id:
                    self.model_combo.addItem(name, model_id)
                    
        except Exception as e:
            logger.error(f"Erro ao carregar modelos: {e}")
            self.model_combo.addItem("Erro ao carregar modelos")
            self.model_combo.setEnabled(False)
    
    def on_model_selected(self, model_name: str):
        """Lida com a seleção de um modelo."""
        if model_name and not self.model_combo.currentData():
            logger.warning("Modelo selecionado sem ID válido")
    
    def send_message(self):
        """Envia a mensagem do usuário para o modelo de IA."""
        message_text = self.message_input.text().strip()
        if not message_text or self.is_generating:
            return
            
        # Verifica se há modelo selecionado
        model_id = self.model_combo.currentData()
        if not model_id or "Nenhum" in self.model_combo.currentText():
            self.show_error_message("Selecione um modelo válido antes de enviar uma mensagem.")
            return
            
        self.add_message_to_ui(message_text, is_user=True)
        self.add_message_to_history(message_text, is_user=True)
        self.message_input.clear()
        
        service = self.service_combo.currentText()
        self.toggle_input_enabled(False)
        self.is_generating = True
        
        # Prepara o widget de resposta vazio
        self.current_response_widget = self.add_message_to_ui("", is_user=False)
        
        # Cria e inicia o worker
        self.current_worker = ChatWorker(
            service, 
            self.conversation_history, 
            model_id, 
            self.config, 
            self.ai_engine, 
            self.ollama_client
        )
        self.current_worker.response_chunk.connect(self.update_response)
        self.current_worker.response_completed.connect(self.finalize_response)
        self.current_worker.error_occurred.connect(self.handle_error)
        self.current_worker.start()
    
    def setup_ui(self):
        """Configura a interface gráfica do chat."""
        layout = QHBoxLayout(self)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)
        splitter.addWidget(self.create_chat_area())
        splitter.addWidget(self.create_settings_panel())
        splitter.setSizes([800, 300])
    
    def create_chat_area(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        self.messages_scroll = QScrollArea()
        self.messages_scroll.setWidgetResizable(True)
        self.messages_scroll.setStyleSheet("background-color: #2b2b2b; border: none;")
        messages_container = QWidget()
        self.messages_layout = QVBoxLayout(messages_container)
        self.messages_layout.addStretch()
        self.messages_scroll.setWidget(messages_container)
        layout.addWidget(self.messages_scroll)
        
        # Área de entrada de mensagem
        input_layout = QHBoxLayout()
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Digite sua mensagem...")
        self.message_input.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.message_input)
        
        self.send_button = QPushButton("Enviar")
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)
        
        layout.addLayout(input_layout)
        return widget
    
    def create_parameter_spinbox(self, parent_layout, label, min_val, max_val, step, config_key, default_val, is_double=True):
        """Cria um QSpinBox ou QDoubleSpinBox para um parâmetro."""
        layout = QHBoxLayout()
        layout.addWidget(QLabel(label))
        spinbox = QDoubleSpinBox() if is_double else QSpinBox()
        spinbox.setRange(min_val, max_val)
        if is_double:
            spinbox.setSingleStep(step)
        else:
            spinbox.setSingleStep(step)
        spinbox.setValue(self.config.get(config_key, default_val))
        layout.addWidget(spinbox)
        parent_layout.addLayout(layout)
        return spinbox
    
    def add_message_to_ui(self, text: str, is_user: bool) -> Optional[ChatMessage]:
        """Adiciona um widget de mensagem à área de chat."""
        author_name = "Você" if is_user else (self.model_combo.currentData() or "Assistente")
        message_widget = ChatMessage(text, author_name, is_user)
        self.messages_layout.insertWidget(self.messages_layout.count() - 1, message_widget)
        
        # Scroll automático para o final
        QTimer.singleShot(10, lambda: self.messages_scroll.verticalScrollBar().setValue(
            self.messages_scroll.verticalScrollBar().maximum()
        ))
        
        if not text and not is_user:  # Se for uma mensagem de assistente vazia, retorna o widget
            return message_widget
        return None
    
    def add_message_to_history(self, text: str, is_user: bool):
        """Adiciona mensagem ao histórico da conversa."""
        role = "user" if is_user else "assistant"
        self.conversation_history.append({"role": role, "content": text})
    
    def update_response(self, chunk: str):
        """Atualiza o balão de resposta do assistente com um novo pedaço de texto."""
        if self.current_response_widget:
            current_text = self.current_response_widget.text_edit.toPlainText()
            self.current_response_widget.update_text(current_text + chunk)
    
    def finalize_response(self):
        """Finaliza a geração da resposta."""
        # Verifica se o widget ainda existe antes de acessá-lo
        if self.current_response_widget:
            final_text = self.current_response_widget.text_edit.toPlainText()
            if final_text.strip():
                self.add_message_to_history(final_text, is_user=False)
        
        self.current_worker = None
        self.current_response_widget = None
        self.is_generating = False
        self.toggle_input_enabled(True)
    
    def handle_error(self, error_msg: str):
        """Lida com erros ocorridos durante a geração."""
        if self.current_response_widget:
            self.current_response_widget.update_text(f"Erro: {error_msg}")
        else:
            self.add_message_to_ui(f"Erro: {error_msg}", is_user=False)
        self.finalize_response()
    
    def toggle_input_enabled(self, enabled: bool):
        """Habilita ou desabilita os campos de entrada e o botão."""
        self.message_input.setEnabled(enabled)
        self.send_button.setEnabled(enabled)
        
        if not enabled:
            self.send_button.setText("Parar")
            self.send_button.clicked.disconnect()
            self.send_button.clicked.connect(self.stop_generation)
        else:
            self.send_button.setText("Enviar")
            self.send_button.clicked.disconnect()
            self.send_button.clicked.connect(self.send_message)
            self.message_input.setFocus()
    
    def stop_generation(self):
        """Para a geração de resposta atual."""
        if self.current_worker and self.current_worker.isRunning():
            self.current_worker.stop()
            self.current_worker.wait()  # Aguarda a thread terminar
    
    def clear_chat(self):
        """Limpa o chat sem reiniciar a aplicação."""
        if self.current_worker and self.current_worker.isRunning():
            self.current_worker.stop()
            self.current_worker.wait()
        
        # Remove todos os widgets de mensagem exceto o espaçador
        while self.messages_layout.count() > 1:  # Mantém o espaço em branco
            item = self.messages_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        self.conversation_history.clear()
        self.current_response_widget = None
        self.is_generating = False
        self.toggle_input_enabled(True)
    
    def new_conversation(self):
        """Limpa o histórico e a UI para uma nova conversa."""
        self.clear_chat()
        self.add_message_to_ui("Olá! Como posso te ajudar hoje?", is_user=False)
        self.add_message_to_history("Olá! Como posso te ajudar hoje?", is_user=False)
    
    def show_error_message(self, message: str):
        """Exibe uma mensagem de erro ao usuário."""
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setWindowTitle("Erro")
        msg_box.setText(message)
        msg_box.exec()
    
    def closeEvent(self, event):
        """Lida com o fechamento do widget."""
        if self.current_worker and self.current_worker.isRunning():
            self.current_worker.stop()
            self.current_worker.wait()
        event.accept()
