#!/usr/bin/env python3
"""
SevenX Studio - Local AI Model Management Platform
Aplicação desktop moderna para gerenciar e executar modelos de IA localmente
"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QFont

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.ui.main_window import MainWindow
from src.core.config import Config
from src.core.logger import setup_logger

def main():
    """Função principal da aplicação"""
    
    # Configurar logging
    logger = setup_logger()
    logger.info("Iniciando SevenX Studio...")
    
    # Criar aplicação Qt
    app = QApplication(sys.argv)
    app.setApplicationName("SevenX Studio")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("SevenX")
    
    # Configurar fonte padrão
    font = QFont("Segoe UI", 9)
    app.setFont(font)
    
    # Configurar tema escuro
    app.setStyle('Fusion')
    
    # Carregar configurações
    config = Config()
    
    # Criar janela principal
    window = MainWindow(config)
    window.show()
    
    logger.info("SevenX Studio iniciado com sucesso!")
    
    # Executar aplicação
    sys.exit(app.exec())

if __name__ == "__main__":
    main()