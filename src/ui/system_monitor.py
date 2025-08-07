"""
Widget para monitoramento do sistema
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QProgressBar, QGroupBox, QTextEdit, QFrame)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

import psutil
import platform
from datetime import datetime
from typing import Dict, List

class SystemInfoCard(QFrame):
    """Card para exibir informação do sistema"""
    
    def __init__(self, title: str, value: str, unit: str = ""):
        super().__init__()
        self.setup_ui(title, value, unit)
    
    def setup_ui(self, title: str, value: str, unit: str):
        """Configurar interface do card"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        
        # Título
        title_label = QLabel(title)
        title_label.setStyleSheet("font-weight: bold; color: #cccccc; font-size: 10px;")
        layout.addWidget(title_label)
        
        # Valor
        value_layout = QHBoxLayout()
        self.value_label = QLabel(value)
        self.value_label.setStyleSheet("font-size: 16px; font-weight: bold; color: white;")
        value_layout.addWidget(self.value_label)
        
        if unit:
            unit_label = QLabel(unit)
            unit_label.setStyleSheet("font-size: 12px; color: #aaaaaa;")
            value_layout.addWidget(unit_label)
        
        value_layout.addStretch()
        layout.addLayout(value_layout)
        
        # Estilo do card
        self.setStyleSheet("""
            QFrame {
                background-color: #404040;
                border: 1px solid #555555;
                border-radius: 6px;
            }
        """)
        self.setFixedHeight(60)
    
    def update_value(self, value: str):
        """Atualizar valor do card"""
        self.value_label.setText(value)

class SystemMonitor(QWidget):
    """Widget para monitoramento do sistema"""
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        
        self.setup_ui()
        
        # Timer para atualizar informações
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_info)
        self.update_timer.start(2000)  # Atualizar a cada 2 segundos
        
        # Primeira atualização
        self.update_info()
    
    def setup_ui(self):
        """Configurar interface do usuário"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        
        # Título
        title_label = QLabel("Monitor do Sistema")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold; color: white; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # Cards de informações básicas
        self.cpu_card = SystemInfoCard("CPU", "0", "%")
        self.memory_card = SystemInfoCard("Memória", "0", "%")
        self.disk_card = SystemInfoCard("Disco", "0", "%")
        
        layout.addWidget(self.cpu_card)
        layout.addWidget(self.memory_card)
        layout.addWidget(self.disk_card)
        
        # Informações detalhadas do sistema
        system_group = QGroupBox("Informações do Sistema")
        system_layout = QVBoxLayout(system_group)
        
        self.system_info = QTextEdit()
        self.system_info.setReadOnly(True)
        self.system_info.setMaximumHeight(150)
        self.system_info.setStyleSheet("""
            QTextEdit {
                background-color: #2b2b2b;
                border: 1px solid #555555;
                border-radius: 4px;
                color: #cccccc;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 10px;
            }
        """)
        
        system_layout.addWidget(self.system_info)
        layout.addWidget(system_group)
        
        # Processos ativos
        processes_group = QGroupBox("Processos de IA")
        processes_layout = QVBoxLayout(processes_group)
        
        self.processes_info = QTextEdit()
        self.processes_info.setReadOnly(True)
        self.processes_info.setMaximumHeight(120)
        self.processes_info.setStyleSheet("""
            QTextEdit {
                background-color: #2b2b2b;
                border: 1px solid #555555;
                border-radius: 4px;
                color: #cccccc;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 10px;
            }
        """)
        
        processes_layout.addWidget(self.processes_info)
        layout.addWidget(processes_group)
        
        # Status dos modelos
        models_group = QGroupBox("Status dos Modelos")
        models_layout = QVBoxLayout(models_group)
        
        self.models_status = QLabel("🔴 Nenhum modelo carregado")
        self.models_status.setStyleSheet("font-size: 12px; padding: 5px;")
        models_layout.addWidget(self.models_status)
        
        layout.addWidget(models_group)
        
        layout.addStretch()
    
    def update_info(self):
        """Atualizar informações do sistema"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=None)
            self.cpu_card.update_value(f"{cpu_percent:.1f}")
            
            # Memória
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            self.memory_card.update_value(f"{memory_percent:.1f}")
            
            # Disco
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            self.disk_card.update_value(f"{disk_percent:.1f}")
            
            # Informações detalhadas do sistema
            self.update_system_info()
            
            # Processos de IA
            self.update_ai_processes()
            
            # Status dos modelos
            self.update_models_status()
            
        except Exception as e:
            print(f"Erro ao atualizar informações do sistema: {e}")
    
    def update_system_info(self):
        """Atualizar informações detalhadas do sistema"""
        try:
            # Informações básicas
            system_info = []
            system_info.append(f"Sistema: {platform.system()} {platform.release()}")
            system_info.append(f"Arquitetura: {platform.machine()}")
            system_info.append(f"Processador: {platform.processor()}")
            
            # CPU
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            system_info.append(f"CPU Cores: {cpu_count}")
            if cpu_freq:
                system_info.append(f"CPU Freq: {cpu_freq.current:.0f} MHz")
            
            # Memória
            memory = psutil.virtual_memory()
            system_info.append(f"RAM Total: {self.format_bytes(memory.total)}")
            system_info.append(f"RAM Disponível: {self.format_bytes(memory.available)}")
            
            # Uptime
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            system_info.append(f"Uptime: {str(uptime).split('.')[0]}")
            
            self.system_info.setPlainText("\\n".join(system_info))
            
        except Exception as e:
            self.system_info.setPlainText(f"Erro ao obter informações: {e}")
    
    def update_ai_processes(self):
        """Atualizar informações sobre processos de IA"""
        try:
            ai_processes = []
            
            # Procurar por processos relacionados a IA
            ai_keywords = ['ollama', 'python', 'pytorch', 'tensorflow', 'cuda']
            
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    proc_name = proc.info['name'].lower()
                    if any(keyword in proc_name for keyword in ai_keywords):
                        cpu = proc.info['cpu_percent'] or 0
                        memory = proc.info['memory_percent'] or 0
                        
                        if cpu > 0.1 or memory > 0.1:  # Apenas processos com uso significativo
                            ai_processes.append(
                                f"{proc.info['name']} (PID: {proc.info['pid']}) - "
                                f"CPU: {cpu:.1f}% RAM: {memory:.1f}%"
                            )
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if ai_processes:
                self.processes_info.setPlainText("\\n".join(ai_processes[:10]))  # Máximo 10 processos
            else:
                self.processes_info.setPlainText("Nenhum processo de IA detectado")
                
        except Exception as e:
            self.processes_info.setPlainText(f"Erro ao obter processos: {e}")
    
    def update_connection_status(self):
        """Atualizar status da conexão com Ollama"""
        try:
            # Simular verificação de conexão (implementar verificação real)
            import random
            connected = random.choice([True, False])  # Simulação
            
            if connected:
                self.connection_status.setText("🟢 Conectado ao Ollama")
                self.connection_status.setStyleSheet("color: #00ff00; font-size: 12px; padding: 5px;")
            else:
                self.connection_status.setText("🔴 Desconectado")
                self.connection_status.setStyleSheet("color: #ff4444; font-size: 12px; padding: 5px;")
                
        except Exception as e:
            self.connection_status.setText("❓ Status desconhecido")
            self.connection_status.setStyleSheet("color: #ffaa00; font-size: 12px; padding: 5px;")
    
    def format_bytes(self, bytes_value: int) -> str:
        """Formatar bytes em unidades legíveis"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f} PB"
    
    def update_models_status(self):
        """Atualizar status dos modelos (método de compatibilidade)"""
        try:
            # Este método é chamado pelo main_window mas não é necessário
            # Apenas para evitar erros
            pass
        except Exception as e:
            print(f"Erro ao atualizar status dos modelos: {e}")