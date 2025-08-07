"""
Janela principal da aplicação SevenX Studio
"""

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QTabWidget, QSplitter, QStatusBar, QMenuBar, 
                             QToolBar, QLabel, QPushButton)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QAction, QIcon

# Supondo que os imports relativos estejam corretos para a sua estrutura de pastas
from .chat_widget_simple import ChatWidget
from .models_widget import ModelsWidget
from .settings_widget import SettingsWidget
from .system_monitor import SystemMonitor
from ..core.config import Config
from ..core.logger import setup_logger
from ..core.sevenx_engine import SevenXEngine

class MainWindow(QMainWindow):
    """Janela principal da aplicação"""
    
    def __init__(self, config: Config):
        super().__init__()
        self.config = config
        self.logger = setup_logger(__name__)
        
        # Inicializar motor de IA
        self.ai_engine = SevenXEngine(config.models_directory)
        
        self.setWindowTitle("SevenX Studio - Local AI Platform")
        self.setMinimumSize(1000, 700)
        
        # Restaurar geometria da janela
        self.resize(
            self.config.get("ui_settings.window_width", 1200),
            self.config.get("ui_settings.window_height", 800)
        )
        
        self.setup_ui()
        self.setup_menu()
        self.setup_toolbar()
        self.setup_statusbar()
        self.apply_theme()
        
        # Timer para atualizar informações do sistema (menos frequente para evitar spam)
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_system_info)
        self.update_timer.start(5000)  # Atualizar a cada 5 segundos
    
    def setup_ui(self):
        """Configurar interface do usuário"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(main_splitter)
        
        self.system_monitor = SystemMonitor(self.config)
        main_splitter.addWidget(self.system_monitor)
        
        self.tab_widget = QTabWidget()
        main_splitter.addWidget(self.tab_widget)
        
        # Aba de Chat
        self.chat_widget = ChatWidget(self.config, self.ai_engine)
        self.tab_widget.addTab(self.chat_widget, "💬 Chat")
        
        # Aba de Modelos - CORREÇÃO APLICADA AQUI
        self.models_widget = ModelsWidget(self.ai_engine)
        self.tab_widget.addTab(self.models_widget, "🤖 Modelos")
        
        # Aba de Configurações
        self.settings_widget = SettingsWidget(self.config)
        self.tab_widget.addTab(self.settings_widget, "⚙️ Configurações")
        
        main_splitter.setSizes([250, 950])
        main_splitter.setCollapsible(0, True)
    
    def setup_menu(self):
        """Configurar menu da aplicação"""
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
        refresh_models_action.triggered.connect(self.models_widget.refresh_all_models) # Corrigido para chamar o método correto
        models_menu.addAction(refresh_models_action)
        
        help_menu = menubar.addMenu("&Ajuda")
        about_action = QAction("&Sobre", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_toolbar(self):
        """Configurar barra de ferramentas"""
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        new_chat_btn = QPushButton("Nova Conversa")
        new_chat_btn.clicked.connect(self.chat_widget.new_conversation)
        toolbar.addWidget(new_chat_btn)
        
        toolbar.addSeparator()
        
        refresh_btn = QPushButton("Atualizar Modelos")
        refresh_btn.clicked.connect(self.models_widget.refresh_all_models) # Corrigido para chamar o método correto
        toolbar.addWidget(refresh_btn)
    
    def setup_statusbar(self):
        """Configurar barra de status"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        self.status_label = QLabel("Pronto")
        self.connection_label = QLabel("Desconectado")
        self.models_count_label = QLabel("0 modelos")
        
        self.status_bar.addWidget(self.status_label)
        self.status_bar.addPermanentWidget(self.models_count_label)
        self.status_bar.addPermanentWidget(self.connection_label)
    
    def apply_theme(self):
        """Aplicar tema da aplicação"""
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
    
    def update_system_info(self):
        """Atualizar informações do sistema na barra de status"""
        try:
            if hasattr(self.system_monitor, 'update_info'):
                self.system_monitor.update_info()
            
            if self.ai_engine.is_available():
                self.connection_label.setText("Motor IA: Ativo")
                self.connection_label.setStyleSheet("color: lightgreen;")
            else:
                self.connection_label.setText("Motor IA: Inativo")
                self.connection_label.setStyleSheet("color: red;")
            
            models = self.ai_engine.list_installed_models() # Corrigido para chamar o método correto
            self.models_count_label.setText(f"{len(models)} modelos")
        except Exception as e:
            pass
    
    def show_about(self):
        """Mostrar diálogo sobre a aplicação"""
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.about(self, "Sobre SevenX Studio", 
                          """
                          <h3>SevenX Studio v1.0.0</h3>
                          <p>Uma plataforma moderna para gerenciamento e execução de modelos de IA localmente.</p>
                          <p><b>Desenvolvido com:</b> Python, PyQt6</p>
                          """)
    
    def closeEvent(self, event):
        """Evento de fechamento da janela"""
        self.config.set("ui_settings.window_width", self.width())
        self.config.set("ui_settings.window_height", self.height())
        
        # self.ai_engine.cleanup() # Descomente se tiver um método cleanup no seu engine
        
        self.logger.info("SevenX Studio fechado")
        event.accept()
