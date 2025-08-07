"""
Widget para gerenciamento de modelos de IA
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                            QTableWidgetItem, QPushButton, QLineEdit, QLabel,
                            QProgressBar, QComboBox, QTextEdit, QSplitter,
                            QGroupBox, QHeaderView, QMessageBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont

import json
import os
from datetime import datetime
from typing import List, Dict, Optional

class ModelDownloadWorker(QThread):
    """Worker thread para download de modelos"""
    
    progress_updated = pyqtSignal(int)
    status_updated = pyqtSignal(str)
    download_completed = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, model_id: str, ai_engine):
        super().__init__()
        self.model_id = model_id
        self.ai_engine = ai_engine
    
    def run(self):
        """Executar download do modelo"""
        try:
            def progress_callback(progress, status):
                if self.isInterruptionRequested():
                    return
                self.progress_updated.emit(progress)
                self.status_updated.emit(status)
            
            success = self.ai_engine.download_model(self.model_id, progress_callback)
            
            if success:
                self.download_completed.emit(self.model_id)
            else:
                self.error_occurred.emit("Falha no download")
            
        except Exception as e:
            self.error_occurred.emit(str(e))

class ModelsWidget(QWidget):
    """Widget para gerenciamento de modelos"""
    
    def __init__(self, config, ai_engine):
        super().__init__()
        self.config = config
        self.ai_engine = ai_engine
        self.download_worker = None
        
        self.setup_ui()
        self.load_available_models()
        self.load_installed_models()
    
    def setup_ui(self):
        """Configurar interface do usuário"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Splitter principal
        splitter = QSplitter(Qt.Orientation.Vertical)
        layout.addWidget(splitter)
        
        # Seção de modelos disponíveis
        available_section = self.create_available_models_section()
        splitter.addWidget(available_section)
        
        # Seção de modelos instalados
        installed_section = self.create_installed_models_section()
        splitter.addWidget(installed_section)
        
        # Seção de download
        download_section = self.create_download_section()
        layout.addWidget(download_section)
        
        # Configurar proporções
        splitter.setSizes([300, 300])
    
    def create_available_models_section(self) -> QWidget:
        """Criar seção de modelos disponíveis"""
        group = QGroupBox("Modelos Disponíveis")
        layout = QVBoxLayout(group)
        
        # Barra de pesquisa
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Pesquisar:"))
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Digite o nome do modelo...")
        self.search_input.textChanged.connect(self.filter_available_models)
        search_layout.addWidget(self.search_input)
        
        refresh_btn = QPushButton("Atualizar")
        refresh_btn.clicked.connect(self.load_available_models)
        search_layout.addWidget(refresh_btn)
        
        layout.addLayout(search_layout)
        
        # Tabela de modelos disponíveis
        self.available_table = QTableWidget()
        self.available_table.setColumnCount(4)
        self.available_table.setHorizontalHeaderLabels(["Nome", "Tamanho", "Descrição", "Ação"])
        
        header = self.available_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        
        layout.addWidget(self.available_table)
        
        return group
    
    def create_installed_models_section(self) -> QWidget:
        """Criar seção de modelos instalados"""
        group = QGroupBox("Modelos Instalados")
        layout = QVBoxLayout(group)
        
        # Tabela de modelos instalados
        self.installed_table = QTableWidget()
        self.installed_table.setColumnCount(5)
        self.installed_table.setHorizontalHeaderLabels(["Nome", "Tamanho", "Modificado", "Status", "Ação"])
        
        header = self.installed_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        
        layout.addWidget(self.installed_table)
        
        return group
    
    def create_download_section(self) -> QWidget:
        """Criar seção de download"""
        group = QGroupBox("Download")
        layout = QVBoxLayout(group)
        
        # Barra de progresso
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Status do download
        self.status_label = QLabel("Pronto para download")
        layout.addWidget(self.status_label)
        
        # Botões de controle
        buttons_layout = QHBoxLayout()
        
        self.cancel_btn = QPushButton("Cancelar")
        self.cancel_btn.setVisible(False)
        self.cancel_btn.clicked.connect(self.cancel_download)
        buttons_layout.addWidget(self.cancel_btn)
        
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
        
        return group
    
    def load_available_models(self):
        """Carregar lista de modelos disponíveis"""
        try:
            # Obter modelos disponíveis do SevenX Engine
            available_models = self.ai_engine.get_available_models()
            
            self.available_models = []
            for model in available_models:
                self.available_models.append({
                    "name": model["name"],
                    "model_id": model["id"],
                    "size": model["size"],
                    "description": model["description"],
                    "type": model["type"],
                    "is_downloaded": False  # Será verificado depois
                })
            
            self.update_available_table()
            
        except Exception as e:
            print(f"Erro ao carregar modelos: {e}")
            self.available_models = []
            self.update_available_table()
    
    def update_available_table(self):
        """Atualizar tabela de modelos disponíveis"""
        self.available_table.setRowCount(len(self.available_models))
        
        for row, model in enumerate(self.available_models):
            # Nome
            name_item = QTableWidgetItem(model["name"])
            if model.get("is_downloaded", False):
                name_item.setText(f"{model['name']} ✓")
                name_item.setBackground(Qt.GlobalColor.darkGreen)
            self.available_table.setItem(row, 0, name_item)
            
            # Tamanho
            size_text = f"{model['size']} ({model.get('parameters', 'N/A')})"
            self.available_table.setItem(row, 1, QTableWidgetItem(size_text))
            
            # Descrição
            self.available_table.setItem(row, 2, QTableWidgetItem(model["description"]))
            
            # Botão de download/carregar
            if model.get("is_downloaded", False):
                action_btn = QPushButton("Carregar")
                action_btn.clicked.connect(lambda checked, model_id=model["model_id"]: self.load_model(model_id))
            else:
                action_btn = QPushButton("Download")
                action_btn.clicked.connect(lambda checked, model_id=model["model_id"]: self.download_model(model_id))
            
            self.available_table.setCellWidget(row, 3, action_btn)
    
    def filter_available_models(self):
        """Filtrar modelos disponíveis por pesquisa"""
        search_text = self.search_input.text().lower()
        
        if not search_text:
            self.load_available_models()
            return
        
        filtered_models = [
            model for model in self.available_models
            if search_text in model["name"].lower() or search_text in model["description"].lower()
        ]
        
        self.available_models = filtered_models
        self.update_available_table()
    
    def load_installed_models(self):
        """Carregar lista de modelos instalados"""
        try:
            # Obter modelos instalados do SevenX Engine
            installed_models = self.ai_engine.list_models()
            
            self.installed_table.setRowCount(len(installed_models))
            
            for row, model in enumerate(installed_models):
                # Nome
                self.installed_table.setItem(row, 0, QTableWidgetItem(model.name))
                
                # Tamanho
                size_mb = model.size / (1024 * 1024)
                size_text = f"{size_mb:.1f}MB" if size_mb < 1024 else f"{size_mb/1024:.1f}GB"
                self.installed_table.setItem(row, 1, QTableWidgetItem(size_text))
                
                # Modificado
                self.installed_table.setItem(row, 2, QTableWidgetItem(model.modified_at[:16]))
                
                # Status
                status = "Carregado" if model.name in self.ai_engine.loaded_models else "Disponível"
                status_item = QTableWidgetItem(status)
                if status == "Carregado":
                    status_item.setBackground(Qt.GlobalColor.darkGreen)
                self.installed_table.setItem(row, 3, status_item)
                
                # Botão de remoção
                remove_btn = QPushButton("Remover")
                remove_btn.clicked.connect(lambda checked, model_name=model.name: self.remove_model(model_name))
                self.installed_table.setCellWidget(row, 4, remove_btn)
                
        except Exception as e:
            print(f"Erro ao carregar modelos instalados: {e}")
            self.installed_table.setRowCount(0)
    
    def download_model(self, model_id: str):
        """Iniciar download de modelo"""
        if self.download_worker and self.download_worker.isRunning():
            QMessageBox.warning(self, "Download em Andamento", 
                              "Já existe um download em andamento. Aguarde ou cancele o download atual.")
            return
        
        # Confirmar download
        reply = QMessageBox.question(self, "Confirmar Download", 
                                   f"Deseja baixar o modelo '{model_id}'?\n\nEste processo pode demorar alguns minutos.",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # Iniciar download
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.cancel_btn.setVisible(True)
        
        self.download_worker = ModelDownloadWorker(model_id, self.ai_engine)
        self.download_worker.progress_updated.connect(self.progress_bar.setValue)
        self.download_worker.status_updated.connect(self.status_label.setText)
        self.download_worker.download_completed.connect(self.on_download_completed)
        self.download_worker.error_occurred.connect(self.on_download_error)
        self.download_worker.start()
    
    def cancel_download(self):
        """Cancelar download atual"""
        if self.download_worker and self.download_worker.isRunning():
            self.download_worker.requestInterruption()
            self.download_worker.wait()
            
            self.progress_bar.setVisible(False)
            self.cancel_btn.setVisible(False)
            self.status_label.setText("Download cancelado")
    
    def on_download_completed(self, model_id: str):
        """Callback quando download é concluído"""
        self.progress_bar.setVisible(False)
        self.cancel_btn.setVisible(False)
        self.status_label.setText(f"Download de '{model_id}' concluído com sucesso!")
        
        # Atualizar listas de modelos
        self.load_available_models()
        self.load_installed_models()
        
        QMessageBox.information(self, "Download Concluído", 
                              f"O modelo '{model_id}' foi baixado com sucesso!\n\nVocê pode agora usá-lo no chat.")
    
    def on_download_error(self, error: str):
        """Callback quando erro ocorre no download"""
        self.progress_bar.setVisible(False)
        self.cancel_btn.setVisible(False)
        self.status_label.setText(f"Erro no download: {error}")
        
        QMessageBox.critical(self, "Erro no Download", f"Erro ao baixar modelo:\n{error}")
    
    def remove_model(self, model_id: str):
        """Remover modelo instalado"""
        reply = QMessageBox.question(self, "Confirmar Remoção", 
                                   f"Deseja remover o modelo '{model_id}'?\n\nEsta ação não pode ser desfeita.",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                success = self.hf_client.delete_model(model_id)
                
                if success:
                    self.status_label.setText(f"Modelo '{model_id}' removido com sucesso!")
                    # Atualizar listas
                    self.load_available_models()
                    self.load_installed_models()
                    
                    QMessageBox.information(self, "Modelo Removido", 
                                          f"O modelo '{model_id}' foi removido com sucesso!")
                else:
                    QMessageBox.warning(self, "Erro na Remoção", 
                                      f"Não foi possível remover o modelo '{model_id}'.")
                    
            except Exception as e:
                QMessageBox.critical(self, "Erro na Remoção", 
                                   f"Erro ao remover modelo:\n{str(e)}")
    
    def load_model(self, model_id: str):
        """Carregar modelo na memória"""
        try:
            self.status_label.setText(f"Carregando modelo '{model_id}'...")
            
            # Carregar modelo em thread separada para não bloquear UI
            from PyQt6.QtCore import QTimer
            
            def load_in_background():
                success = self.hf_client.load_model(model_id)
                if success:
                    self.status_label.setText(f"Modelo '{model_id}' carregado com sucesso!")
                    self.load_installed_models()  # Atualizar status
                    QMessageBox.information(self, "Modelo Carregado", 
                                          f"O modelo '{model_id}' está pronto para uso!")
                else:
                    self.status_label.setText(f"Falha ao carregar modelo '{model_id}'")
                    QMessageBox.warning(self, "Erro no Carregamento", 
                                      f"Não foi possível carregar o modelo '{model_id}'.")
            
            # Executar após um pequeno delay para permitir atualização da UI
            QTimer.singleShot(100, load_in_background)
            
        except Exception as e:
            QMessageBox.critical(self, "Erro no Carregamento", 
                               f"Erro ao carregar modelo:\n{str(e)}")
    
    def refresh_models(self):
        """Atualizar listas de modelos"""
        self.load_available_models()
        self.load_installed_models()
        self.status_label.setText("Listas de modelos atualizadas")