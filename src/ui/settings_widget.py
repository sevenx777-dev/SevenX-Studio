"""
Widget de configurações da aplicação, com lógica refatorada e UX aprimorada.
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

    def create_general_tab(self) -> QWidget:
        widget = QWidget(); layout = QFormLayout(widget)
        layout.setSpacing(15)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["dark", "light"])
        self.theme_combo.setToolTip("Define o tema visual da aplicação (requer reinicialização).")
        layout.addRow("Tema Visual:", self.theme_combo)

        self.models_dir_input = QLineEdit()
        self.models_dir_input.setToolTip("Pasta onde os modelos de IA serão armazenados.")
        models_dir_btn = QPushButton("Procurar...")
        models_dir_btn.clicked.connect(self.select_models_directory)
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(self.models_dir_input)
        dir_layout.addWidget(models_dir_btn)
        layout.addRow("Diretório de Modelos:", dir_layout)
        
        return widget

    def create_chat_tab(self) -> QWidget:
        widget = QWidget(); layout = QFormLayout(widget)
        layout.setSpacing(15)

        self.temperature_spin = QDoubleSpinBox()
        self.temperature_spin.setRange(0.0, 2.0); self.temperature_spin.setSingleStep(0.1)
        self.temperature_spin.setToolTip("Controla a criatividade da resposta. Valores mais altos = mais criativo.")
        layout.addRow("Temperatura:", self.temperature_spin)
        
        self.max_tokens_spin = QSpinBox()
        self.max_tokens_spin.setRange(1, 8192); self.max_tokens_spin.setSingleStep(128)
        self.max_tokens_spin.setToolTip("Número máximo de tokens (palavras/partes de palavras) na resposta.")
        layout.addRow("Máximo de Tokens:", self.max_tokens_spin)

        self.top_p_spin = QDoubleSpinBox()
        self.top_p_spin.setRange(0.0, 1.0); self.top_p_spin.setSingleStep(0.05)
        self.top_p_spin.setToolTip("Amostragem de núcleo. Considera apenas os tokens mais prováveis com uma probabilidade cumulativa de 'top_p'.")
        layout.addRow("Top P:", self.top_p_spin)

        self.top_k_spin = QSpinBox()
        self.top_k_spin.setRange(0, 100)
        self.top_k_spin.setToolTip("Considera apenas os 'k' tokens mais prováveis para a resposta. 0 para desativar.")
        layout.addRow("Top K:", self.top_k_spin)

        self.repeat_penalty_spin = QDoubleSpinBox()
        self.repeat_penalty_spin.setRange(1.0, 2.0); self.repeat_penalty_spin.setSingleStep(0.1)
        self.repeat_penalty_spin.setToolTip("Penaliza tokens que já apareceram, reduzindo a repetição. 1.0 = sem penalidade.")
        layout.addRow("Penalidade de Repetição:", self.repeat_penalty_spin)

        self.auto_save_check = QCheckBox("Salvar conversas automaticamente ao fechar")
        layout.addRow(self.auto_save_check)

        return widget

    def create_interface_tab(self) -> QWidget:
        widget = QWidget(); layout = QFormLayout(widget)
        layout.setSpacing(15)

        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 20)
        self.font_size_spin.setToolTip("Tamanho da fonte principal da aplicação (requer reinicialização).")
        layout.addRow("Tamanho da Fonte:", self.font_size_spin)

        self.sidebar_width_spin = QSpinBox()
        self.sidebar_width_spin.setRange(200, 500)
        self.sidebar_width_spin.setToolTip("Largura do painel lateral do monitor de sistema.")
        layout.addRow("Largura do Painel Lateral:", self.sidebar_width_spin)

        self.show_system_info_check = QCheckBox("Exibir painel de monitoramento do sistema")
        layout.addRow(self.show_system_info_check)
        
        return widget

    def create_advanced_tab(self) -> QWidget:
        widget = QWidget()
        layout = QFormLayout(widget)
        layout.setSpacing(15)

        self.hf_token_input = QLineEdit()
        self.hf_token_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.hf_token_input.setToolTip("Cole aqui o seu token de acesso do Hugging Face para baixar modelos protegidos.")
        layout.addRow("Token Hugging Face:", self.hf_token_input)

        self.ollama_host_input = QLineEdit()
        self.ollama_host_input.setToolTip("Endereço do servidor Ollama (se utilizado). Deixe em branco se não usar.")
        layout.addRow("Host Ollama:", self.ollama_host_input)

        self.api_port_spin = QSpinBox()
        self.api_port_spin.setRange(1024, 65535)
        self.api_port_spin.setToolTip("Porta para a API interna (se implementada).")
        layout.addRow("Porta da API:", self.api_port_spin)

        return widget

    def map_widgets_to_config(self):
        self.widget_map = {
            self.theme_combo: "theme",
            self.models_dir_input: "models_directory",
            self.temperature_spin: "chat_settings.temperature",
            self.max_tokens_spin: "chat_settings.max_tokens",
            self.top_p_spin: "chat_settings.top_p",
            self.top_k_spin: "chat_settings.top_k",
            self.repeat_penalty_spin: "chat_settings.repeat_penalty",
            self.auto_save_check: "auto_save",
            self.font_size_spin: "ui_settings.font_size",
            self.sidebar_width_spin: "ui_settings.sidebar_width",
            self.show_system_info_check: "ui_settings.show_system_info",
            self.hf_token_input: "hf_token",
            self.ollama_host_input: "ollama_host",
            self.api_port_spin: "api_port",
        }

    def load_settings(self):
        for widget, key in self.widget_map.items():
            value = self.config.get(key)
            if isinstance(widget, (QSpinBox, QDoubleSpinBox)): widget.setValue(value)
            elif isinstance(widget, QLineEdit): widget.setText(str(value))
            elif isinstance(widget, QComboBox): widget.setCurrentText(str(value))
            elif isinstance(widget, QCheckBox): widget.setChecked(bool(value))

    def save_settings(self):
        for widget, key in self.widget_map.items():
            value = None
            if isinstance(widget, (QSpinBox, QDoubleSpinBox)): value = widget.value()
            elif isinstance(widget, QLineEdit): value = widget.text()
            elif isinstance(widget, QComboBox): value = widget.currentText()
            elif isinstance(widget, QCheckBox): value = widget.isChecked()
            if value is not None: self.config.set(key, value)
        self.settings_changed.emit()
        QMessageBox.information(self, "Sucesso", "Configurações salvas e aplicadas!")

    def reset_settings(self):
        reply = QMessageBox.question(self, "Restaurar Padrões", "Tem certeza que deseja restaurar todas as configurações?")
        if reply == QMessageBox.StandardButton.Yes:
            default_config = Config(); default_config.settings = default_config._load_config()
            for widget, key in self.widget_map.items():
                self.config.set(key, default_config.get(key))
            self.load_settings()
            QMessageBox.information(self, "Sucesso", "Configurações restauradas para o padrão.")

    def select_models_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Selecionar Pasta de Modelos", self.models_dir_input.text())
        if directory:
            self.models_dir_input.setText(directory)
