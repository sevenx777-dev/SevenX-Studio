"""
Widget de chat simplificado para evitar erros
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

class SimpleChatWidget(QWidget):
    """Widget de chat simplificado"""
    
    def __init__(self, config, ai_engine):
        super().__init__()
        self.config = config
        self.ai_engine = ai_engine
        self.conversation_history = []
        
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
        
        # Área de mensagens (texto simples)
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background-color: #2b2b2b;
                color: white;
                border: 1px solid #555555;
                border-radius: 8px;
                padding: 10px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
            }
        """)
        layout.addWidget(self.chat_display)
        
        # Área de entrada
        input_layout = QHBoxLayout()
        
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Digite sua mensagem...")
        self.message_input.returnPressed.connect(self.send_message)
        self.message_input.setStyleSheet("""
            QLineEdit {
                background-color: #404040;
                color: white;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 8px;
                font-size: 12px;
            }
        """)
        
        self.send_button = QPushButton("Enviar")
        self.send_button.clicked.connect(self.send_message)
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
        """)
        
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
        self.model_combo.setStyleSheet("""
            QComboBox {
                background-color: #404040;
                color: white;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 5px;
            }
        """)
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
        self.temperature_spin.setValue(0.7)
        temp_layout.addWidget(self.temperature_spin)
        params_layout.addLayout(temp_layout)
        
        # Max Tokens
        tokens_layout = QHBoxLayout()
        tokens_layout.addWidget(QLabel("Max Tokens:"))
        self.max_tokens_spin = QSpinBox()
        self.max_tokens_spin.setRange(1, 2048)
        self.max_tokens_spin.setValue(512)
        tokens_layout.addWidget(self.max_tokens_spin)
        params_layout.addLayout(tokens_layout)
        
        layout.addWidget(params_group)
        
        # Botões de ação
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
    
    def load_models(self):
        """Carregar lista de modelos disponíveis"""
        try:
            # Obter modelos instalados
            installed_models = self.ai_engine.list_models()
            
            self.model_combo.clear()
            
            if not installed_models:
                self.model_combo.addItem("Nenhum modelo instalado", "")
                return
            
            for model in installed_models:
                self.model_combo.addItem(model.name, model.name)
            
            # Selecionar primeiro modelo
            if self.model_combo.count() > 0:
                self.model_combo.setCurrentIndex(0)
                    
        except Exception as e:
            print(f"Erro ao carregar modelos: {e}")
            self.model_combo.clear()
            self.model_combo.addItem("Erro ao carregar modelos", "")
    
    def send_message(self):
        """Enviar mensagem para o modelo"""
        message = self.message_input.text().strip()
        if not message:
            return
        
        # Adicionar mensagem do usuário ao display
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.add_to_display(f"[{timestamp}] Você: {message}")
        self.message_input.clear()
        
        # Verificar se há modelo selecionado
        model_name = self.model_combo.currentData()
        if not model_name:
            self.add_to_display("[ERRO] Nenhum modelo selecionado")
            return
        
        # Desabilitar entrada durante processamento
        self.message_input.setEnabled(False)
        self.send_button.setEnabled(False)
        self.send_button.setText("Processando...")
        
        # Processar mensagem
        try:
            self.add_to_display(f"[{timestamp}] Assistente: Processando...")
            
            # Usar o motor de IA
            messages = [{"role": "user", "content": message}]
            config = {
                "temperature": self.temperature_spin.value(),
                "max_tokens": self.max_tokens_spin.value()
            }
            
            # Verificar se há modelos instalados
            installed_models = self.ai_engine.list_models()
            
            if not installed_models:
                # Resposta simulada se não há modelos
                response = f"Olá! Esta é uma resposta simulada para '{message}'. Para usar modelos reais, vá para a aba 'Modelos' e baixe um modelo como DialoGPT-small."
            else:
                # Usar modelo real
                result = self.ai_engine.chat(model_name, messages, config)
                
                if "error" in result:
                    response = f"Erro: {result['error']} - Vá para aba 'Modelos' para baixar modelos."
                else:
                    response = result.get("message", {}).get("content", "Sem resposta")
            
            # Atualizar display
            self.update_last_message(f"[{timestamp}] Assistente: {response}")
            
        except Exception as e:
            self.update_last_message(f"[{timestamp}] Assistente: Erro - {str(e)}")
        
        finally:
            # Reabilitar entrada
            self.message_input.setEnabled(True)
            self.send_button.setEnabled(True)
            self.send_button.setText("Enviar")
            self.message_input.setFocus()
    
    def add_to_display(self, text: str):
        """Adicionar texto ao display"""
        self.chat_display.append(text)
        self.chat_display.append("")  # Linha em branco
        
        # Scroll para o final
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.chat_display.setTextCursor(cursor)
    
    def update_last_message(self, text: str):
        """Atualizar última mensagem"""
        # Remover as duas últimas linhas (mensagem anterior + linha em branco)
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.movePosition(QTextCursor.MoveOperation.Up, QTextCursor.MoveMode.KeepAnchor, 2)
        cursor.removeSelectedText()
        
        # Adicionar nova mensagem
        self.chat_display.append(text)
        self.chat_display.append("")
        
        # Scroll para o final
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.chat_display.setTextCursor(cursor)
    
    def new_conversation(self):
        """Iniciar nova conversa"""
        self.clear_chat()
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.add_to_display(f"[{timestamp}] Sistema: Nova conversa iniciada!")
    
    def clear_chat(self):
        """Limpar chat"""
        self.chat_display.clear()
        self.conversation_history.clear()

# Alias para compatibilidade
ChatWidget = SimpleChatWidget