"""
Widget de configurações da aplicação, com lógica de salvamento e restauração corrigida.
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QComboBox, QSpinBox,
                             QDoubleSpinBox, QCheckBox, QGroupBox, QTabWidget,
                             QFileDialog, QFormLayout, QMessageBox, QScrollArea)
from PyQt6.QtCore import Qt, pyqtSignal

from ..core.config import Config

class SettingsWidget(QWidget):
    """Widget aprimorado para gerenciamento de todas as configurações da aplicação."""
    
    settings_changed = pyqtSignal()
    
    def __init__(self, config: Config):
        super().__init__()
        self.config = config
        self.widget_map = {}
        
        self.setup_ui()
        self.map_widgets_to_config()
        self.load_settings()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        scroll = QScrollArea(); scroll.setWidgetResizable(True); layout.addWidget(scroll)
        container = QWidget(); layout_container = QVBoxLayout(container); scroll.setWidget(container)
        tabs = QTabWidget()
        tabs.addTab(self.create_general_tab(), " GERAL")
        tabs.addTab(self.create_chat_tab(), "💬 CHAT")
        tabs.addTab(self.create_interface_tab(), "🎨 INTERFACE")
        tabs.addTab(self.create_advanced_tab(), "⚙️ AVANÇADO")
        layout_container.addWidget(tabs)
        buttons = QHBoxLayout(); buttons.addStretch()
        self.reset_btn = QPushButton("Restaurar Padrões"); self.reset_btn.clicked.connect(self.reset_settings); buttons.addWidget(self.reset_btn)
        self.save_btn = QPushButton("Salvar e Aplicar"); self.save_btn.clicked.connect(self.save_settings); self.save_btn.setStyleSheet("background-color: #0078d4;"); buttons.addWidget(self.save_btn)
        layout_container.addLayout(buttons)

    def create_interface_tab(self) -> QWidget:
        widget = QWidget(); layout = QFormLayout(widget); layout.setSpacing(15)
        self.font_size_spin = QSpinBox(); self.font_size_spin.setRange(8, 20); layout.addRow("Tamanho da Fonte:", self.font_size_spin)
        self.sidebar_width_spin = QSpinBox(); self.sidebar_width_spin.setRange(200, 500); layout.addRow("Largura do Painel Lateral:", self.sidebar_width_spin)
        self.show_system_info_check = QCheckBox("Exibir painel de monitoramento"); layout.addRow(self.show_system_info_check)
        self.lite_mode_check = QCheckBox("Ativar Modo Leve (melhor performance)"); self.lite_mode_check.setToolTip("Reduz a frequência de atualizações da UI para economizar CPU."); layout.addRow(self.lite_mode_check)
        return widget

    def map_widgets_to_config(self):
        self.widget_map = {
            self.theme_combo: "theme", self.models_dir_input: "models_directory",
            self.temperature_spin: "chat_settings.temperature", self.max_tokens_spin: "chat_settings.max_tokens",
            self.top_p_spin: "chat_settings.top_p", self.top_k_spin: "chat_settings.top_k",
            self.repeat_penalty_spin: "chat_settings.repeat_penalty", self.auto_save_check: "auto_save",
            self.font_size_spin: "ui_settings.font_size", self.sidebar_width_spin: "ui_settings.sidebar_width",
            self.show_system_info_check: "ui_settings.show_system_info", self.lite_mode_check: "ui_settings.lite_mode",
            self.hf_token_input: "hf_token", self.ollama_host_input: "ollama_host", self.api_port_spin: "api_port",
        }

    def load_settings(self):
        print("Carregando configurações nos widgets...")
        for widget, key in self.widget_map.items():
            value = self.config.get(key)
            if isinstance(widget, (QSpinBox, QDoubleSpinBox)): widget.setValue(value)
            elif isinstance(widget, QLineEdit): widget.setText(str(value))
            elif isinstance(widget, QComboBox): widget.setCurrentText(str(value))
            elif isinstance(widget, QCheckBox): widget.setChecked(bool(value))

    def save_settings(self):
        """Coleta os valores dos widgets, atualiza o config e salva no arquivo."""
        print("Coletando valores dos widgets para salvar...")
        for widget, key in self.widget_map.items():
            value = None
            if isinstance(widget, (QSpinBox, QDoubleSpinBox)): value = widget.value()
            elif isinstance(widget, QLineEdit): value = widget.text()
            elif isinstance(widget, QComboBox): value = widget.currentText()
            elif isinstance(widget, QCheckBox): value = widget.isChecked()
            if value is not None: self.config.set(key, value)
        
        if self.config.save_config():
            self.settings_changed.emit()
            QMessageBox.information(self, "Sucesso", "Configurações salvas e aplicadas!")
        else:
            QMessageBox.critical(self, "Erro ao Salvar", 
                                 f"Não foi possível salvar as configurações no arquivo:\n"
                                 f"{self.config.config_file}\n\n"
                                 f"Por favor, verifique as permissões da pasta.")

    def reset_settings(self):
        reply = QMessageBox.question(self, "Restaurar Padrões", "Tem certeza que deseja restaurar todas as configurações?")
        if reply == QMessageBox.StandardButton.Yes:
            self.config.reset_to_defaults()
            self.load_settings()
            QMessageBox.information(self, "Sucesso", "Configurações restauradas para o padrão.")

    def select_models_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Selecionar Pasta de Modelos", self.models_dir_input.text())
        if directory:
            self.models_dir_input.setText(directory)
            
    # --- Métodos de UI (sem alterações) ---
    def create_general_tab(self) -> QWidget:
        widget = QWidget(); layout = QFormLayout(widget); self.theme_combo = QComboBox(); self.theme_combo.addItems(["dark", "light"]); layout.addRow("Tema Visual:", self.theme_combo); self.models_dir_input = QLineEdit(); btn = QPushButton("Procurar..."); btn.clicked.connect(self.select_models_directory); hlayout = QHBoxLayout(); hlayout.addWidget(self.models_dir_input); hlayout.addWidget(btn); layout.addRow("Diretório de Modelos:", hlayout); return widget
    def create_chat_tab(self) -> QWidget:
        widget = QWidget(); layout = QFormLayout(widget); layout.setSpacing(15); self.temperature_spin = QDoubleSpinBox(); self.temperature_spin.setRange(0.0, 2.0); self.temperature_spin.setSingleStep(0.1); layout.addRow("Temperatura:", self.temperature_spin); self.max_tokens_spin = QSpinBox(); self.max_tokens_spin.setRange(1, 8192); self.max_tokens_spin.setSingleStep(128); layout.addRow("Máximo de Tokens:", self.max_tokens_spin); self.top_p_spin = QDoubleSpinBox(); self.top_p_spin.setRange(0.0, 1.0); self.top_p_spin.setSingleStep(0.05); layout.addRow("Top P:", self.top_p_spin); self.top_k_spin = QSpinBox(); self.top_k_spin.setRange(0, 100); layout.addRow("Top K:", self.top_k_spin); self.repeat_penalty_spin = QDoubleSpinBox(); self.repeat_penalty_spin.setRange(1.0, 2.0); self.repeat_penalty_spin.setSingleStep(0.1); layout.addRow("Penalidade de Repetição:", self.repeat_penalty_spin); self.auto_save_check = QCheckBox("Salvar conversas automaticamente ao fechar"); layout.addRow(self.auto_save_check); return widget
    def create_advanced_tab(self) -> QWidget:
        widget = QWidget(); layout = QFormLayout(widget); layout.setSpacing(15); self.hf_token_input = QLineEdit(); self.hf_token_input.setEchoMode(QLineEdit.EchoMode.Password); self.hf_token_input.setToolTip("Cole aqui o seu token de acesso do Hugging Face para baixar modelos protegidos."); layout.addRow("Token Hugging Face:", self.hf_token_input); self.ollama_host_input = QLineEdit(); self.ollama_host_input.setToolTip("Endereço do servidor Ollama (se utilizado). Deixe em branco se não usar."); layout.addRow("Host Ollama:", self.ollama_host_input); self.api_port_spin = QSpinBox(); self.api_port_spin.setRange(1024, 65535); self.api_port_spin.setToolTip("Porta para a API interna (se implementada)."); layout.addRow("Porta da API:", self.api_port_spin); return widget
