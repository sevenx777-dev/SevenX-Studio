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
                             QSpinBox, QDoubleSpinBox, QGroupBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QTextCursor

from ..core.sevenx_engine import SevenXEngine, ModelInfo
from ..core.ollama_client import OllamaClient
from ..core.config import Config

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
            generation_config = self.config.get("chat_settings")
            
            stream_generator = None
            if self.service == "Ollama":
                stream_generator = self.ollama_client.chat_stream(self.model_id, self.messages, generation_config)
            else: # Padrão é o SevenX Engine
                stream_generator = self.ai_engine.generate_stream(self.model_id, self.messages, generation_config)

            for chunk in stream_generator:
                if self.should_stop: break
                if "Erro:" in chunk:
                    self.error_occurred.emit(chunk)
                    return
                self.response_chunk.emit(chunk)
                self.msleep(stream_delay)
        except Exception as e:
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
        self.setup_ui()
        self.on_service_changed()

    def create_settings_panel(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        service_group = QGroupBox("Serviço de IA")
        service_layout = QVBoxLayout(service_group)
        self.service_combo = QComboBox()
        self.service_combo.addItems(["SevenX (Local)", "Ollama"])
        self.service_combo.currentTextChanged.connect(self.on_service_changed)
        service_layout.addWidget(self.service_combo)
        layout.addWidget(service_group)

        model_group = QGroupBox("Modelo")
        model_layout = QVBoxLayout(model_group)
        self.model_combo = QComboBox()
        model_layout.addWidget(self.model_combo)
        layout.addWidget(model_group)
        
        params_group = QGroupBox("Parâmetros de Geração")
        params_layout = QVBoxLayout(params_group)
        self.temperature_spin = self.create_parameter_spinbox(params_layout, "Temperatura:", 0.0, 2.0, 0.1, "chat_settings.temperature", 0.7)
        self.max_tokens_spin = self.create_parameter_spinbox(params_layout, "Max. Tokens:", 1, 8192, 10, "chat_settings.max_tokens", 2048, is_double=False)
        self.top_p_spin = self.create_parameter_spinbox(params_layout, "Top P:", 0.0, 1.0, 0.05, "chat_settings.top_p", 0.9)
        layout.addWidget(params_group)
        
        actions_group = QGroupBox("Ações")
        actions_layout = QVBoxLayout(actions_group)
        self.new_chat_btn = QPushButton("Nova Conversa")
        self.new_chat_btn.clicked.connect(self.new_conversation)
        actions_layout.addWidget(self.new_chat_btn)
        layout.addWidget(actions_group)
        
        layout.addStretch()
        return widget

    def on_service_changed(self):
        service = self.service_combo.currentText()
        self.model_combo.clear()
        
        models = []
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
                name = model.name; model_id = model.name
            else:
                name = model.get('name'); model_id = model.get('id')
            
            if name and model_id:
                self.model_combo.addItem(name, model_id)

    def send_message(self):
        message_text = self.message_input.text().strip()
        if not message_text or (self.current_worker and self.current_worker.isRunning()): return
        
        self.add_message_to_ui(message_text, is_user=True)
        self.add_message_to_history(message_text, is_user=True)
        self.message_input.clear()
        
        model_id = self.model_combo.currentData()
        service = self.service_combo.currentText()

        if not model_id or "Nenhum" in self.model_combo.currentText():
            self.add_message_to_ui("Erro: Nenhum modelo válido selecionado.", is_user=False)
            return
        
        self.toggle_input_enabled(False)
        self.current_response_widget = self.add_message_to_ui("", is_user=False)
        
        self.current_worker = ChatWorker(service, self.conversation_history, model_id, self.config, self.ai_engine, self.ollama_client)
        self.current_worker.response_chunk.connect(self.update_response)
        self.current_worker.response_completed.connect(self.finalize_response)
        self.current_worker.error_occurred.connect(self.handle_error)
        self.current_worker.start()

    def setup_ui(self):
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
        layout = QHBoxLayout()
        layout.addWidget(QLabel(label))
        spinbox = QDoubleSpinBox() if is_double else QSpinBox()
        spinbox.setRange(min_val, max_val)
        if is_double: spinbox.setSingleStep(step)
        spinbox.setValue(self.config.get(config_key, default_val))
        layout.addWidget(spinbox)
        parent_layout.addLayout(layout)
        return spinbox

    def add_message_to_ui(self, text: str, is_user: bool) -> Optional[ChatMessage]:
        author_name = "Você" if is_user else (self.model_combo.currentData() or "Assistente")
        message_widget = ChatMessage(text, author_name, is_user)
        self.messages_layout.insertWidget(self.messages_layout.count() - 1, message_widget)
        QTimer.singleShot(10, lambda: self.messages_scroll.verticalScrollBar().setValue(self.messages_scroll.verticalScrollBar().maximum()))
        if not text and not is_user: return message_widget
        return None

    def add_message_to_history(self, text: str, is_user: bool):
        role = "user" if is_user else "assistant"
        self.conversation_history.append({"role": role, "content": text})

    def update_response(self, chunk: str):
        if self.current_response_widget:
            current_text = self.current_response_widget.text_edit.toPlainText()
            self.current_response_widget.update_text(current_text + chunk)

    def finalize_response(self):
        # **CORREÇÃO AQUI**: Verifica se o widget ainda existe antes de o aceder.
        if self.current_response_widget:
            final_text = self.current_response_widget.text_edit.toPlainText()
            if final_text.strip():
                self.add_message_to_history(final_text, is_user=False)
        
        self.current_worker = None
        self.current_response_widget = None
        self.toggle_input_enabled(True)

    def handle_error(self, error_msg: str):
        if self.current_response_widget:
            self.current_response_widget.update_text(f"Erro: {error_msg}")
        else:
            self.add_message_to_ui(f"Erro: {error_msg}", is_user=False)
        self.finalize_response()

    def toggle_input_enabled(self, enabled: bool):
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
        if self.current_worker:
            self.current_worker.stop()

    def new_conversation(self):
        if self.current_worker and self.current_worker.isRunning():
            self.current_worker.stop()
        for i in reversed(range(self.messages_layout.count() - 1)):
            widget = self.messages_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        self.conversation_history.clear()
        self.add_message_to_ui("Olá! Como posso te ajudar hoje?", is_user=False)
        self.add_message_to_history("Olá! Como posso te ajudar hoje?", is_user=False)
