"""
Arquivo: main_ui.py
Descrição: Widget para gerenciamento de modelos de IA e ponto de entrada da aplicação.
"""
import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QTableWidget, QTableWidgetItem, QPushButton, QLineEdit, QLabel,
                             QProgressBar, QSplitter, QGroupBox, QHeaderView, QMessageBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

# Importa as classes dos outros arquivos
from ..core.sevenx_engine import SevenXEngine
from ..core.huggingface_client import Config
class ModelDownloadWorker(QThread):
    """Worker em uma thread separada para não bloquear a UI durante o download."""
    progress_updated = pyqtSignal(int)
    status_updated = pyqtSignal(str)
    download_completed = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, model_id: str, ai_engine: SevenXEngine):
        super().__init__()
        self.model_id = model_id
        self.ai_engine = ai_engine
    
    def run(self):
        """Executa o download do modelo."""
        try:
            def progress_callback(progress, status):
                if self.isInterruptionRequested(): return
                self.progress_updated.emit(progress)
                self.status_updated.emit(status)
            
            success = self.ai_engine.download_model(self.model_id, progress_callback)
            
            if self.isInterruptionRequested():
                self.status_updated.emit("Download cancelado.")
                return

            if success:
                self.download_completed.emit(self.model_id)
            else:
                self.error_occurred.emit("Falha no download. Verifique o console para detalhes.")
        except Exception as e:
            self.error_occurred.emit(str(e))

class ModelsWidget(QWidget):
    """Widget principal para gerenciar os modelos de IA."""
    
    def __init__(self, ai_engine: SevenXEngine):
        super().__init__()
        self.ai_engine = ai_engine
        self.download_worker = None
        
        self.setup_ui()
        self.refresh_all_models()
    
    def setup_ui(self):
        """Configura a interface gráfica do widget."""
        layout = QVBoxLayout(self)
        splitter = QSplitter(Qt.Orientation.Vertical)
        layout.addWidget(splitter)
        
        splitter.addWidget(self.create_available_models_section())
        splitter.addWidget(self.create_installed_models_section())
        layout.addWidget(self.create_download_section())
        
        splitter.setSizes([300, 200])
    
    def create_available_models_section(self) -> QGroupBox:
        group = QGroupBox("Buscar Modelos Online (Hugging Face)")
        layout = QVBoxLayout(group)
        
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Pesquisar:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Digite para buscar modelos e pressione Enter...")
        self.search_input.returnPressed.connect(self.search_online_models)
        search_layout.addWidget(self.search_input)
        
        search_btn = QPushButton("Buscar")
        search_btn.clicked.connect(self.search_online_models)
        search_layout.addWidget(search_btn)
        layout.addLayout(search_layout)
        
        self.available_table = QTableWidget()
        self.available_table.setColumnCount(4)
        self.available_table.setHorizontalHeaderLabels(["ID do Modelo", "Downloads", "Descrição", "Ação"])
        self.available_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.available_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.available_table)
        
        return group
    
    def create_installed_models_section(self) -> QGroupBox:
        group = QGroupBox("Modelos Instalados Localmente")
        layout = QVBoxLayout(group)
        
        self.installed_table = QTableWidget()
        self.installed_table.setColumnCount(5)
        self.installed_table.setHorizontalHeaderLabels(["Nome", "Tamanho", "Status", "Ação", "Remover"])
        self.installed_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.installed_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.installed_table)
        
        return group
    
    def create_download_section(self) -> QGroupBox:
        group = QGroupBox("Status do Download")
        layout = QVBoxLayout(group)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Pronto.")
        layout.addWidget(self.status_label)
        
        self.cancel_btn = QPushButton("Cancelar Download")
        self.cancel_btn.setVisible(False)
        self.cancel_btn.clicked.connect(self.cancel_download)
        layout.addWidget(self.cancel_btn, 0, Qt.AlignmentFlag.AlignRight)
        
        return group

    def search_online_models(self):
        """Busca modelos online e atualiza a tabela."""
        query = self.search_input.text()
        self.status_label.setText(f"Buscando por '{query}'...")
        QApplication.processEvents() # Atualiza a UI
        
        models = self.ai_engine.search_online_models(query=query)
        self.available_table.setRowCount(len(models))
        
        for row, model in enumerate(models):
            self.available_table.setItem(row, 0, QTableWidgetItem(model["id"]))
            self.available_table.setItem(row, 1, QTableWidgetItem(str(model["downloads"])))
            self.available_table.setItem(row, 2, QTableWidgetItem(model["description"]))
            
            btn = QPushButton("Baixar")
            btn.clicked.connect(lambda checked, m=model["id"]: self.start_download(m))
            self.available_table.setCellWidget(row, 3, btn)
            
        self.status_label.setText(f"{len(models)} modelos encontrados.")

    def update_installed_models_table(self):
        """Atualiza a tabela de modelos instalados."""
        models = self.ai_engine.list_installed_models()
        self.installed_table.setRowCount(len(models))
        
        for row, model in enumerate(models):
            size_gb = model.size / (1024**3)
            status = "Carregado" if self.ai_engine.loaded_models.get(model.name) else "Disponível"
            
            self.installed_table.setItem(row, 0, QTableWidgetItem(model.name))
            self.installed_table.setItem(row, 1, QTableWidgetItem(f"{size_gb:.2f} GB"))
            self.installed_table.setItem(row, 2, QTableWidgetItem(status))
            
            action_btn = QPushButton("Carregar" if status == "Disponível" else "Descarregar")
            action_btn.clicked.connect(lambda checked, m=model.name: self.toggle_load_model(m))
            self.installed_table.setCellWidget(row, 3, action_btn)

            remove_btn = QPushButton("Remover")
            remove_btn.clicked.connect(lambda checked, m=model.name: self.remove_model(m))
            self.installed_table.setCellWidget(row, 4, remove_btn)

    def start_download(self, model_id: str):
        if self.download_worker and self.download_worker.isRunning():
            QMessageBox.warning(self, "Aviso", "Um download já está em andamento.")
            return
        
        reply = QMessageBox.question(self, "Confirmar Download", f"Deseja baixar o modelo '{model_id}'?")
        if reply != QMessageBox.StandardButton.Yes: return
        
        self.progress_bar.setVisible(True)
        self.cancel_btn.setVisible(True)
        
        self.download_worker = ModelDownloadWorker(model_id, self.ai_engine)
        self.download_worker.progress_updated.connect(self.progress_bar.setValue)
        self.download_worker.status_updated.connect(self.status_label.setText)
        self.download_worker.download_completed.connect(self.on_download_completed)
        self.download_worker.error_occurred.connect(self.on_download_error)
        self.download_worker.start()

    def cancel_download(self):
        if self.download_worker and self.download_worker.isRunning():
            self.download_worker.requestInterruption()
            self.download_worker.wait()
            self.reset_download_ui()

    def on_download_completed(self, model_id: str):
        QMessageBox.information(self, "Sucesso", f"Modelo '{model_id}' baixado com sucesso.")
        self.reset_download_ui()
        self.refresh_all_models()

    def on_download_error(self, error: str):
        QMessageBox.critical(self, "Erro no Download", error)
        self.reset_download_ui()

    def reset_download_ui(self):
        self.progress_bar.setVisible(False)
        self.cancel_btn.setVisible(False)
        self.status_label.setText("Pronto.")

    def remove_model(self, model_id: str):
        reply = QMessageBox.question(self, "Confirmar Remoção", f"Tem certeza que deseja remover o modelo '{model_id}'?")
        if reply == QMessageBox.StandardButton.Yes:
            if self.ai_engine.delete_model(model_id):
                QMessageBox.information(self, "Sucesso", f"Modelo '{model_id}' removido.")
                self.refresh_all_models()
            else:
                QMessageBox.critical(self, "Erro", f"Falha ao remover o modelo '{model_id}'.")

    def toggle_load_model(self, model_id: str):
        if self.ai_engine.loaded_models.get(model_id): # Se está carregado, descarrega
            if self.ai_engine.unload_model(model_id):
                self.status_label.setText(f"Modelo '{model_id}' descarregado.")
            else:
                self.status_label.setText(f"Falha ao descarregar '{model_id}'.")
        else: # Se não está carregado, carrega
            self.status_label.setText(f"Carregando '{model_id}'...")
            QApplication.processEvents()
            if self.ai_engine.load_model(model_id):
                self.status_label.setText(f"Modelo '{model_id}' carregado.")
            else:
                self.status_label.setText(f"Falha ao carregar '{model_id}'.")
        self.update_installed_models_table()

    def refresh_all_models(self):
        """Atualiza todas as tabelas e informações."""
        self.update_installed_models_table()
        self.status_label.setText("Pronto.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # 1. Inicializa a configuração
    config = Config()
    
    # 2. Inicializa o motor de IA com o diretório de modelos da configuração
    engine = SevenXEngine(models_dir=config.models_directory)
    
    # 3. Cria a janela principal e o widget
    window = QMainWindow()
    models_widget = ModelsWidget(ai_engine=engine)
    window.setCentralWidget(models_widget)
    window.setWindowTitle("Gerenciador de Modelos de IA - SevenX Studio")
    window.resize(800, 600)
    
    window.show()
    sys.exit(app.exec())