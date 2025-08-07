"""
Widget de configurações da aplicação
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QComboBox, QSpinBox,
                            QDoubleSpinBox, QCheckBox, QGroupBox, QTabWidget,
                            QFileDialog, QTextEdit, QSlider, QFormLayout,
                            QMessageBox, QScrollArea)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

import os
from pathlib import Path

class SettingsWidget(QWidget):
    """Widget de configurações da aplicação"""
    
    settings_changed = pyqtSignal()
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        """Configurar interface do usuário"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Scroll area para as configurações
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Widget principal das configurações
        settings_widget = QWidget()
        settings_layout = QVBoxLayout(settings_widget)
        
        # Abas de configurações
        tab_widget = QTabWidget()
        
        # Aba Geral
        general_tab = self.create_general_tab()
        tab_widget.addTab(general_tab, "Geral")
        
        # Aba Modelos
        models_tab = self.create_models_tab()
        tab_widget.addTab(models_tab, "Modelos")
        
        # Aba Chat
        chat_tab = self.create_chat_tab()
        tab_widget.addTab(chat_tab, "Chat")
        
        # Aba Interface
        interface_tab = self.create_interface_tab()
        tab_widget.addTab(interface_tab, "Interface")
        
        # Aba Avançado
        advanced_tab = self.create_advanced_tab()
        tab_widget.addTab(advanced_tab, "Avançado")
        
        settings_layout.addWidget(tab_widget)
        
        # Botões de ação
        buttons_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("Salvar Configurações")
        self.save_btn.clicked.connect(self.save_settings)
        
        self.reset_btn = QPushButton("Restaurar Padrões")
        self.reset_btn.clicked.connect(self.reset_settings)
        
        self.apply_btn = QPushButton("Aplicar")
        self.apply_btn.clicked.connect(self.apply_settings)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.reset_btn)
        buttons_layout.addWidget(self.apply_btn)
        buttons_layout.addWidget(self.save_btn)
        
        settings_layout.addLayout(buttons_layout)
        
        scroll.setWidget(settings_widget)
        layout.addWidget(scroll)
    
    def create_general_tab(self) -> QWidget:
        """Criar aba de configurações gerais"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Configurações de idioma e tema
        appearance_group = QGroupBox("Aparência")
        appearance_layout = QFormLayout(appearance_group)
        
        # Tema
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["dark", "light"])
        appearance_layout.addRow("Tema:", self.theme_combo)
        
        # Idioma
        self.language_combo = QComboBox()
        self.language_combo.addItems(["pt-BR", "en-US", "es-ES"])
        appearance_layout.addRow("Idioma:", self.language_combo)
        
        layout.addWidget(appearance_group)
        
        # Configurações de diretórios
        directories_group = QGroupBox("Diretórios")
        directories_layout = QFormLayout(directories_group)
        
        # Diretório de modelos
        models_dir_layout = QHBoxLayout()
        self.models_dir_input = QLineEdit()
        models_dir_btn = QPushButton("Procurar")
        models_dir_btn.clicked.connect(self.select_models_directory)
        models_dir_layout.addWidget(self.models_dir_input)
        models_dir_layout.addWidget(models_dir_btn)
        directories_layout.addRow("Modelos:", models_dir_layout)
        
        layout.addWidget(directories_group)
        
        # Configurações de conexão
        connection_group = QGroupBox("Conexão")
        connection_layout = QFormLayout(connection_group)
        
        # Host do Ollama
        self.ollama_host_input = QLineEdit()
        connection_layout.addRow("Host Ollama:", self.ollama_host_input)
        
        # Porta da API
        self.api_port_spin = QSpinBox()
        self.api_port_spin.setRange(1000, 65535)
        connection_layout.addRow("Porta API:", self.api_port_spin)
        
        layout.addWidget(connection_group)
        
        layout.addStretch()
        return widget
    
    def create_models_tab(self) -> QWidget:
        """Criar aba de configurações de modelos"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Configurações de download
        download_group = QGroupBox("Download de Modelos")
        download_layout = QFormLayout(download_group)
        
        # Threads simultâneas
        self.download_threads_spin = QSpinBox()
        self.download_threads_spin.setRange(1, 8)
        download_layout.addRow("Threads simultâneas:", self.download_threads_spin)
        
        # Auto-verificar atualizações
        self.auto_check_updates = QCheckBox("Verificar atualizações automaticamente")
        download_layout.addRow(self.auto_check_updates)
        
        layout.addWidget(download_group)
        
        # Configurações de cache
        cache_group = QGroupBox("Cache")
        cache_layout = QFormLayout(cache_group)
        
        # Tamanho máximo do cache
        self.cache_size_spin = QSpinBox()
        self.cache_size_spin.setRange(1, 100)
        self.cache_size_spin.setSuffix(" GB")
        cache_layout.addRow("Tamanho máximo:", self.cache_size_spin)
        
        # Limpar cache automaticamente
        self.auto_clear_cache = QCheckBox("Limpar cache automaticamente")
        cache_layout.addRow(self.auto_clear_cache)
        
        layout.addWidget(cache_group)
        
        layout.addStretch()
        return widget
    
    def create_chat_tab(self) -> QWidget:
        """Criar aba de configurações de chat"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Parâmetros padrão do modelo
        model_params_group = QGroupBox("Parâmetros Padrão do Modelo")
        model_params_layout = QFormLayout(model_params_group)
        
        # Temperature
        self.temperature_spin = QDoubleSpinBox()
        self.temperature_spin.setRange(0.0, 2.0)
        self.temperature_spin.setSingleStep(0.1)
        self.temperature_spin.setDecimals(2)
        model_params_layout.addRow("Temperature:", self.temperature_spin)
        
        # Max Tokens
        self.max_tokens_spin = QSpinBox()
        self.max_tokens_spin.setRange(1, 8192)
        model_params_layout.addRow("Max Tokens:", self.max_tokens_spin)
        
        # Top P
        self.top_p_spin = QDoubleSpinBox()
        self.top_p_spin.setRange(0.0, 1.0)
        self.top_p_spin.setSingleStep(0.1)
        self.top_p_spin.setDecimals(2)
        model_params_layout.addRow("Top P:", self.top_p_spin)
        
        # Top K
        self.top_k_spin = QSpinBox()
        self.top_k_spin.setRange(1, 100)
        model_params_layout.addRow("Top K:", self.top_k_spin)
        
        # Repeat Penalty
        self.repeat_penalty_spin = QDoubleSpinBox()
        self.repeat_penalty_spin.setRange(0.0, 2.0)
        self.repeat_penalty_spin.setSingleStep(0.1)
        self.repeat_penalty_spin.setDecimals(2)
        model_params_layout.addRow("Repeat Penalty:", self.repeat_penalty_spin)
        
        layout.addWidget(model_params_group)
        
        # Configurações de conversa
        conversation_group = QGroupBox("Conversas")
        conversation_layout = QFormLayout(conversation_group)
        
        # Máximo de conversas
        self.max_conversations_spin = QSpinBox()
        self.max_conversations_spin.setRange(10, 1000)
        conversation_layout.addRow("Máximo de conversas:", self.max_conversations_spin)
        
        # Auto-salvar
        self.auto_save_check = QCheckBox("Salvar conversas automaticamente")
        conversation_layout.addRow(self.auto_save_check)
        
        layout.addWidget(conversation_group)
        
        layout.addStretch()
        return widget
    
    def create_interface_tab(self) -> QWidget:
        """Criar aba de configurações de interface"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Configurações da janela
        window_group = QGroupBox("Janela")
        window_layout = QFormLayout(window_group)
        
        # Tamanho da fonte
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 24)
        window_layout.addRow("Tamanho da fonte:", self.font_size_spin)
        
        # Largura da sidebar
        self.sidebar_width_spin = QSpinBox()
        self.sidebar_width_spin.setRange(200, 400)
        window_layout.addRow("Largura da sidebar:", self.sidebar_width_spin)
        
        # Mostrar informações do sistema
        self.show_system_info_check = QCheckBox("Mostrar informações do sistema")
        window_layout.addRow(self.show_system_info_check)
        
        layout.addWidget(window_group)
        
        # Configurações do chat
        chat_ui_group = QGroupBox("Interface do Chat")
        chat_ui_layout = QFormLayout(chat_ui_group)
        
        # Mostrar timestamps
        self.show_timestamps_check = QCheckBox("Mostrar timestamps nas mensagens")
        chat_ui_layout.addRow(self.show_timestamps_check)
        
        # Syntax highlighting
        self.syntax_highlighting_check = QCheckBox("Destacar sintaxe de código")
        chat_ui_layout.addRow(self.syntax_highlighting_check)
        
        layout.addWidget(chat_ui_group)
        
        layout.addStretch()
        return widget
    
    def create_advanced_tab(self) -> QWidget:
        """Criar aba de configurações avançadas"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Configurações de logging
        logging_group = QGroupBox("Logging")
        logging_layout = QFormLayout(logging_group)
        
        # Nível de log
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        logging_layout.addRow("Nível de log:", self.log_level_combo)
        
        # Tamanho máximo do arquivo de log
        self.log_file_size_spin = QSpinBox()
        self.log_file_size_spin.setRange(1, 100)
        self.log_file_size_spin.setSuffix(" MB")
        logging_layout.addRow("Tamanho máximo do log:", self.log_file_size_spin)
        
        layout.addWidget(logging_group)
        
        # Configurações de performance
        performance_group = QGroupBox("Performance")
        performance_layout = QFormLayout(performance_group)
        
        # Usar GPU se disponível
        self.use_gpu_check = QCheckBox("Usar GPU se disponível")
        performance_layout.addRow(self.use_gpu_check)
        
        # Threads de processamento
        self.processing_threads_spin = QSpinBox()
        self.processing_threads_spin.setRange(1, 16)
        performance_layout.addRow("Threads de processamento:", self.processing_threads_spin)
        
        layout.addWidget(performance_group)
        
        # Configurações experimentais
        experimental_group = QGroupBox("Experimental")
        experimental_layout = QFormLayout(experimental_group)
        
        # Recursos experimentais
        self.experimental_features_check = QCheckBox("Habilitar recursos experimentais")
        experimental_layout.addRow(self.experimental_features_check)
        
        layout.addWidget(experimental_group)
        
        layout.addStretch()
        return widget
    
    def load_settings(self):
        """Carregar configurações atuais"""
        # Geral
        self.theme_combo.setCurrentText(self.config.get("theme", "dark"))
        self.language_combo.setCurrentText(self.config.get("language", "pt-BR"))
        self.models_dir_input.setText(str(self.config.models_directory))
        self.ollama_host_input.setText(self.config.get("ollama_host", "http://localhost:11434"))
        self.api_port_spin.setValue(self.config.get("api_port", 8080))
        
        # Chat
        self.temperature_spin.setValue(self.config.get("chat_settings.temperature", 0.7))
        self.max_tokens_spin.setValue(self.config.get("chat_settings.max_tokens", 2048))
        self.top_p_spin.setValue(self.config.get("chat_settings.top_p", 0.9))
        self.top_k_spin.setValue(self.config.get("chat_settings.top_k", 40))
        self.repeat_penalty_spin.setValue(self.config.get("chat_settings.repeat_penalty", 1.1))
        self.max_conversations_spin.setValue(self.config.get("max_conversations", 100))
        self.auto_save_check.setChecked(self.config.get("auto_save", True))
        
        # Interface
        self.font_size_spin.setValue(self.config.get("ui_settings.font_size", 12))
        self.sidebar_width_spin.setValue(self.config.get("ui_settings.sidebar_width", 250))
        self.show_system_info_check.setChecked(self.config.get("ui_settings.show_system_info", True))
    
    def save_settings(self):
        """Salvar todas as configurações"""
        # Geral
        self.config.set("theme", self.theme_combo.currentText())
        self.config.set("language", self.language_combo.currentText())
        self.config.set("models_directory", self.models_dir_input.text())
        self.config.set("ollama_host", self.ollama_host_input.text())
        self.config.set("api_port", self.api_port_spin.value())
        
        # Chat
        self.config.set("chat_settings.temperature", self.temperature_spin.value())
        self.config.set("chat_settings.max_tokens", self.max_tokens_spin.value())
        self.config.set("chat_settings.top_p", self.top_p_spin.value())
        self.config.set("chat_settings.top_k", self.top_k_spin.value())
        self.config.set("chat_settings.repeat_penalty", self.repeat_penalty_spin.value())
        self.config.set("max_conversations", self.max_conversations_spin.value())
        self.config.set("auto_save", self.auto_save_check.isChecked())
        
        # Interface
        self.config.set("ui_settings.font_size", self.font_size_spin.value())
        self.config.set("ui_settings.sidebar_width", self.sidebar_width_spin.value())
        self.config.set("ui_settings.show_system_info", self.show_system_info_check.isChecked())
        
        # Emitir sinal de mudança
        self.settings_changed.emit()
        
        QMessageBox.information(self, "Configurações Salvas", 
                              "As configurações foram salvas com sucesso!")
    
    def apply_settings(self):
        """Aplicar configurações sem salvar"""
        self.save_settings()
    
    def reset_settings(self):
        """Restaurar configurações padrão"""
        reply = QMessageBox.question(self, "Restaurar Padrões", 
                                   "Deseja restaurar todas as configurações para os valores padrão?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            # Resetar para valores padrão
            self.theme_combo.setCurrentText("dark")
            self.language_combo.setCurrentText("pt-BR")
            self.models_dir_input.setText(str(self.config.models_dir))
            self.ollama_host_input.setText("http://localhost:11434")
            self.api_port_spin.setValue(8080)
            
            self.temperature_spin.setValue(0.7)
            self.max_tokens_spin.setValue(2048)
            self.top_p_spin.setValue(0.9)
            self.top_k_spin.setValue(40)
            self.repeat_penalty_spin.setValue(1.1)
            self.max_conversations_spin.setValue(100)
            self.auto_save_check.setChecked(True)
            
            self.font_size_spin.setValue(12)
            self.sidebar_width_spin.setValue(250)
            self.show_system_info_check.setChecked(True)
    
    def select_models_directory(self):
        """Selecionar diretório de modelos"""
        directory = QFileDialog.getExistingDirectory(
            self, 
            "Selecionar Diretório de Modelos",
            str(self.config.models_directory)
        )
        
        if directory:
            self.models_dir_input.setText(directory)