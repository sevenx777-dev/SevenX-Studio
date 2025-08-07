"""
Widget para monitoramento do sistema, com suporte a GPU NVIDIA.
"""

import psutil
import platform
import os
from datetime import datetime
from typing import Dict, List

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QProgressBar, QGroupBox, QTextEdit, QFrame)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

# Importa as classes do projeto
from ..core.config import Config
from ..core.sevenx_engine import SevenXEngine

# Tenta importar a biblioteca da NVIDIA; se não existir, a funcionalidade da GPU é desativada
try:
    import pynvml
    PYNVML_AVAILABLE = True
except ImportError:
    PYNVML_AVAILABLE = False

class ResourceBar(QFrame):
    """Widget customizado para exibir uma barra de progresso de recurso."""
    def __init__(self, title: str):
        super().__init__()
        self.title_label = QLabel(title)
        self.progress_bar = QProgressBar()
        self.value_label = QLabel("0.0 %")
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(3)
        
        top_layout = QHBoxLayout()
        top_layout.addWidget(self.title_label)
        top_layout.addStretch()
        top_layout.addWidget(self.value_label)
        
        layout.addLayout(top_layout)
        layout.addWidget(self.progress_bar)
        
        self.setStyleSheet("QLabel { font-size: 11px; }")

    def set_value(self, value: float):
        self.progress_bar.setValue(int(value))
        self.value_label.setText(f"{value:.1f} %")
        
        # Muda a cor da barra com base no uso
        if value > 85:
            stylesheet = "QProgressBar::chunk { background-color: #d32f2f; }" # Vermelho
        elif value > 60:
            stylesheet = "QProgressBar::chunk { background-color: #f57c00; }" # Laranja
        else:
            stylesheet = "QProgressBar::chunk { background-color: #0078d4; }" # Azul
        self.progress_bar.setStyleSheet(stylesheet)

class SystemMonitor(QWidget):
    """Widget para monitoramento de CPU, RAM, Disco e GPU."""
    
    def __init__(self, config: Config, ai_engine: SevenXEngine):
        super().__init__()
        self.config = config
        self.ai_engine = ai_engine
        self.nvml_handle = None
        self.current_process = psutil.Process(os.getpid())
        
        if PYNVML_AVAILABLE:
            self._init_nvml()
        
        self.setup_ui()
        
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_info)
        self.update_timer.start(2000) # Atualiza a cada 2 segundos
        self.update_info()

    def _init_nvml(self):
        """Inicializa a biblioteca pynvml para monitoramento da GPU."""
        try:
            pynvml.nvmlInit()
            # Pega o handle da primeira GPU
            self.nvml_handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            print("Monitoramento de GPU NVIDIA ativado.")
        except Exception as e:
            print(f"Não foi possível inicializar o monitoramento de GPU: {e}")
            self.nvml_handle = None
    
    def setup_ui(self):
        """Configura a interface gráfica do widget."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        title_label = QLabel("Monitor do Sistema")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 5px;")
        layout.addWidget(title_label)
        
        # Barras de Recursos
        self.cpu_bar = ResourceBar("CPU")
        self.memory_bar = ResourceBar("Memória (RAM)")
        self.disk_bar = ResourceBar("Disco (Principal)")
        layout.addWidget(self.cpu_bar)
        layout.addWidget(self.memory_bar)
        layout.addWidget(self.disk_bar)

        # Grupo da GPU (só aparece se houver uma GPU NVIDIA)
        if self.nvml_handle:
            gpu_group = QGroupBox("GPU NVIDIA")
            gpu_layout = QVBoxLayout(gpu_group)
            self.gpu_util_bar = ResourceBar("Uso da GPU")
            self.gpu_mem_bar = ResourceBar("Memória da GPU (VRAM)")
            self.gpu_temp_label = QLabel("Temperatura: -- °C")
            gpu_layout.addWidget(self.gpu_util_bar)
            gpu_layout.addWidget(self.gpu_mem_bar)
            gpu_layout.addWidget(self.gpu_temp_label)
            layout.addWidget(gpu_group)
        
        # Grupo de Status do App
        app_status_group = QGroupBox("Status da Aplicação")
        app_status_layout = QVBoxLayout(app_status_group)
        self.app_process_label = QLabel("Uso do App: --")
        self.model_status_label = QLabel("Modelo Carregado: Nenhum")
        app_status_layout.addWidget(self.app_process_label)
        app_status_layout.addWidget(self.model_status_label)
        layout.addWidget(app_status_group)

        layout.addStretch()

    def update_info(self):
        """Atualiza todas as informações de monitoramento."""
        try:
            # CPU, RAM e Disco
            self.cpu_bar.set_value(psutil.cpu_percent(interval=None))
            self.memory_bar.set_value(psutil.virtual_memory().percent)
            self.disk_bar.set_value(psutil.disk_usage('/').percent)

            # GPU (se disponível)
            if self.nvml_handle:
                gpu_util = pynvml.nvmlDeviceGetUtilizationRates(self.nvml_handle)
                self.gpu_util_bar.set_value(gpu_util.gpu)
                
                gpu_mem = pynvml.nvmlDeviceGetMemoryInfo(self.nvml_handle)
                self.gpu_mem_bar.set_value((gpu_mem.used / gpu_mem.total) * 100)
                
                gpu_temp = pynvml.nvmlDeviceGetTemperature(self.nvml_handle, pynvml.NVML_TEMPERATURE_GPU)
                self.gpu_temp_label.setText(f"Temperatura: {gpu_temp} °C")

            # Status da Aplicação
            app_cpu = self.current_process.cpu_percent() / psutil.cpu_count()
            app_mem = self.current_process.memory_info().rss
            self.app_process_label.setText(f"Uso do App: {app_cpu:.1f}% CPU, {self.format_bytes(app_mem)} RAM")

            loaded_models = list(self.ai_engine.loaded_models.keys())
            if loaded_models:
                self.model_status_label.setText(f"Modelo Carregado: {loaded_models[0]}")
            else:
                self.model_status_label.setText("Modelo Carregado: Nenhum")

        except Exception as e:
            # Desativa o timer em caso de erro para não sobrecarregar
            self.update_timer.stop()
            print(f"Erro no monitor do sistema, desativando: {e}")

    def format_bytes(self, bytes_value: int) -> str:
        """Formata bytes em unidades legíveis (KB, MB, GB)."""
        if bytes_value < 1024: return f"{bytes_value} B"
        kb = bytes_value / 1024
        if kb < 1024: return f"{kb:.1f} KB"
        mb = kb / 1024
        if mb < 1024: return f"{mb:.1f} MB"
        gb = mb / 1024
        return f"{gb:.1f} GB"
        
    def closeEvent(self, event):
        """Garante que os recursos sejam liberados ao fechar."""
        if PYNVML_AVAILABLE and self.nvml_handle:
            pynvml.nvmlShutdown()
        super().closeEvent(event)
