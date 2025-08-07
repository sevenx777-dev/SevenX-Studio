"""
Janela principal da aplicação SevenX Studio
"""

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QTabWidget, QSplitter, QStatusBar, QMenuBar, 
                             QToolBar, QLabel, QPushButton, QMessageBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction

from .chat_widget_simple import ChatWidget
from .models_widget import ModelsWidget
from .settings_widget import SettingsWidget
from .system_monitor import SystemMonitor
from ..core.config import Config
from ..core.logger import setup_logger
from ..core.sevenx_engine import SevenXEngine
from ..core.ollama_client import OllamaClient

class MainWindow(QMainWindow):
    """Janela principal da aplicação"""
    
    def __init__(self, config: Config):
        super().__init__()
        self.config = config
        self.logger = setup_logger(__name__)
        
        self.ai_engine = SevenXEngine(config)
        self.ollama_client = OllamaClient(config)
        
        self.setWindowTitle("SevenX Studio - Local AI Platform")
        self.setMinimumSize(1000, 700)
        
        self.resize(
            self.config.get("ui_settings.window_width", 1200),
            self.config.get("ui_settings.window_height", 800)
        )
        
        self.setup_ui()
        self.setup_menu()
        self.setup_toolbar()
        self.setup_statusbar()
        self.apply_theme()
        
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_statusbar_info)
        self.update_timer.start(5000)
    
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal) # Tornar acessível
        main_layout.addWidget(self.main_splitter)
        
        self.system_monitor = SystemMonitor(self.config, self.ai_engine, self.ollama_client)
        self.main_splitter.addWidget(self.system_monitor)
        
        self.tab_widget = QTabWidget()
        self.main_splitter.addWidget(self.tab_widget)
        
        self.chat_widget = ChatWidget(self.config, self.ai_engine, self.ollama_client)
        self.tab_widget.addTab(self.chat_widget, "💬 Chat")
        
        self.models_widget = ModelsWidget(self.ai_engine)
        self.tab_widget.addTab(self.models_widget, "🤖 Modelos")
        
        self.settings_widget = SettingsWidget(self.config)
        self.settings_widget.settings_changed.connect(self.on_settings_changed)
        self.tab_widget.addTab(self.settings_widget, "⚙️ Configurações")
        
        self.main_splitter.setSizes([self.config.get("ui_settings.sidebar_width"), 920])
        self.main_splitter.setCollapsible(0, True)

    def on_settings_changed(self):
        """Aplica as configurações que podem ser mudadas em tempo real."""
        print("Aplicando configurações alteradas na janela principal...")
        
        sidebar_width = self.config.get("ui_settings.sidebar_width")
        current_sizes = self.main_splitter.sizes()
        self.main_splitter.setSizes([sidebar_width, current_sizes[1]])

        show_monitor = self.config.get("ui_settings.show_system_info")
        self.system_monitor.setVisible(show_monitor)
        
        QMessageBox.information(self, "Configurações Aplicadas",
                                "Algumas alterações, como o tema e o tamanho da fonte, "
                                "podem exigir que a aplicação seja reiniciada para terem efeito completo.")

    def setup_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("&Arquivo")
        new_chat_action = QAction("&Nova Conversa", self)
        new_chat_action.setShortcut("Ctrl+N")
        new_chat_action.triggered.connect(self.chat_widget.new_conversation)
        file_menu.addAction(new_chat_action)
        file_menu.addSeparator()
        exit_action = QAction("&Sair", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        models_menu = menubar.addMenu("&Modelos")
        refresh_models_action = QAction("&Atualizar Lista", self)
        refresh_models_action.setShortcut("F5")
        refresh_models_action.triggered.connect(self.models_widget.refresh_all_models)
        models_menu.addAction(refresh_models_action)
        help_menu = menubar.addMenu("&Ajuda")
        about_action = QAction("&Sobre", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def setup_toolbar(self):
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        new_chat_btn = QPushButton("Nova Conversa")
        new_chat_btn.clicked.connect(self.chat_widget.new_conversation)
        toolbar.addWidget(new_chat_btn)
        toolbar.addSeparator()
        refresh_btn = QPushButton("Atualizar Modelos")
        refresh_btn.clicked.connect(self.models_widget.refresh_all_models)
        toolbar.addWidget(refresh_btn)

    def setup_statusbar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_label = QLabel("Pronto")
        self.connection_label = QLabel("Motor IA: --")
        self.models_count_label = QLabel("0 modelos locais")
        self.status_bar.addWidget(self.status_label)
        self.status_bar.addPermanentWidget(self.models_count_label)
        self.status_bar.addPermanentWidget(self.connection_label)

    def apply_theme(self):
        if self.config.get("theme") == "dark":
            self.setStyleSheet("""
                QMainWindow { background-color: #2b2b2b; color: #ffffff; }
                QTabWidget::pane { border: 1px solid #555555; background-color: #3c3c3c; }
                QTabBar::tab { background-color: #404040; color: #ffffff; padding: 8px 16px; margin-right: 2px; border-top-left-radius: 4px; border-top-right-radius: 4px; }
                QTabBar::tab:selected { background-color: #3c3c3c; border-bottom: 2px solid #0078d4; }
                QTabBar::tab:hover { background-color: #4a4a4a; }
                QStatusBar { background-color: #404040; color: #ffffff; border-top: 1px solid #555555; }
                QMenuBar { background-color: #404040; color: #ffffff; border-bottom: 1px solid #555555; }
                QMenuBar::item:selected { background-color: #0078d4; }
                QToolBar { background-color: #404040; border-bottom: 1px solid #555555; spacing: 5px; }
                QPushButton { background-color: #0078d4; color: white; border: none; padding: 6px 12px; border-radius: 3px; }
                QPushButton:hover { background-color: #106ebe; }
                QPushButton:pressed { background-color: #005a9e; }
            """)

    def update_statusbar_info(self):
        try:
            if self.ai_engine.is_available():
                self.connection_label.setText("Motor IA: Ativo")
                self.connection_label.setStyleSheet("color: lightgreen;")
            else:
                self.connection_label.setText("Motor IA: Inativo")
                self.connection_label.setStyleSheet("color: red;")
            models = self.ai_engine.list_installed_models()
            self.models_count_label.setText(f"{len(models)} modelos locais")
        except Exception:
            pass

    def show_about(self):
        QMessageBox.about(self, "Sobre SevenX Studio", "<h3>SevenX Studio v1.0.0</h3><p>Uma plataforma moderna para IA local.</p>")

    def closeEvent(self, event):
        self.config.set("ui_settings.window_width", self.width())
        self.config.set("ui_settings.window_height", self.height())
        self.ai_engine.cleanup()
        self.logger.info("SevenX Studio fechado")
        event.accept()
