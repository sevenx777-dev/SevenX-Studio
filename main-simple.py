#!/usr/bin/env python3
"""
SevenX Studio - Versão Simplificada para Teste
"""

import sys
import os
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton
    from PyQt6.QtCore import Qt
    
    class SimpleWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("SevenX Studio - Teste")
            self.setGeometry(100, 100, 400, 300)
            
            # Widget central
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            
            # Layout
            layout = QVBoxLayout(central_widget)
            
            # Labels
            title = QLabel("SevenX Studio")
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px;")
            
            status = QLabel("✅ Interface funcionando!")
            status.setAlignment(Qt.AlignmentFlag.AlignCenter)
            status.setStyleSheet("font-size: 16px; color: green; margin: 10px;")
            
            # Verificar dependências
            deps_status = self.check_dependencies()
            deps_label = QLabel(deps_status)
            deps_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            deps_label.setStyleSheet("font-size: 12px; margin: 10px;")
            
            # Botão
            test_btn = QPushButton("Testar Motor de IA")
            test_btn.clicked.connect(self.test_ai_engine)
            
            # Adicionar ao layout
            layout.addWidget(title)
            layout.addWidget(status)
            layout.addWidget(deps_label)
            layout.addWidget(test_btn)
            layout.addStretch()
        
        def check_dependencies(self):
            """Verificar dependências"""
            deps = []
            
            try:
                import torch
                deps.append(f"✅ PyTorch {torch.__version__}")
            except ImportError:
                deps.append("❌ PyTorch não encontrado")
            
            try:
                import transformers
                deps.append(f"✅ Transformers {transformers.__version__}")
            except ImportError:
                deps.append("❌ Transformers não encontrado")
            
            try:
                import huggingface_hub
                deps.append("✅ Hugging Face Hub")
            except ImportError:
                deps.append("❌ Hugging Face Hub não encontrado")
            
            return "\n".join(deps)
        
        def test_ai_engine(self):
            """Testar motor de IA"""
            try:
                from core.ollama_client import SevenXEngine
                
                # Criar diretório de modelos
                models_dir = Path.home() / ".sevenx_studio" / "models"
                models_dir.mkdir(parents=True, exist_ok=True)
                
                # Inicializar engine
                engine = SevenXEngine(models_dir)
                
                if engine.is_available():
                    self.show_message("✅ Motor de IA funcionando!")
                else:
                    self.show_message("❌ Motor de IA com problemas")
                    
            except Exception as e:
                self.show_message(f"❌ Erro: {str(e)}")
        
        def show_message(self, message):
            """Mostrar mensagem"""
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(self, "Teste", message)
    
    def main():
        app = QApplication(sys.argv)
        app.setStyle('Fusion')
        
        window = SimpleWindow()
        window.show()
        
        sys.exit(app.exec())
    
    if __name__ == "__main__":
        main()

except ImportError as e:
    print(f"Erro de importação: {e}")
    print("\nExecute install-simple.bat primeiro!")
    input("Pressione Enter para continuar...")
except Exception as e:
    print(f"Erro: {e}")
    input("Pressione Enter para continuar...")