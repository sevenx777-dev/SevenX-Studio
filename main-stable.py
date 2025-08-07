#!/usr/bin/env python3
"""
SevenX Studio - Versão Estável (sem timer de atualização)
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

class StableMainWindow(MainWindow):
    """Versão estável da janela principal sem timer automático"""
    
    def __init__(self, config):
        super().__init__(config)
        
        # Parar o timer automático para evitar spam de erros
        if hasattr(self, 'update_timer'):
            self.update_timer.stop()
        
        # Fazer uma atualização inicial única
        try:
            self.update_system_info()
        except:
            pass

def main():
    """Função principal da aplicação"""
    
    # Configurar logging
    logger = setup_logger()
    logger.info("Iniciando SevenX Studio (versão estável)...")
    
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
    
    # Criar janela principal (versão estável)
    window = StableMainWindow(config)
    window.show()
    
    logger.info("SevenX Studio iniciado com sucesso!")
    
    # Executar aplicação
    sys.exit(app.exec())

if __name__ == "__main__":
    main()