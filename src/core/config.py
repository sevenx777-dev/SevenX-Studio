"""
Gerenciamento de configurações da aplicação
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional

class Config:
    """Classe para gerenciar configurações da aplicação"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".sevenx_studio"
        self.config_file = self.config_dir / "config.json"
        self.models_dir = self.config_dir / "models"
        self.logs_dir = self.config_dir / "logs"
        self.conversations_dir = self.config_dir / "conversations"
        
        # Criar diretórios se não existirem
        self._create_directories()
        
        # Carregar configurações
        self.settings = self._load_config()
    
    def _create_directories(self):
        """Criar diretórios necessários"""
        for directory in [self.config_dir, self.models_dir, self.logs_dir, self.conversations_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _load_config(self) -> Dict[str, Any]:
        """Carregar configurações do arquivo"""
        default_config = {
            "theme": "dark",
            "language": "pt-BR",
            "models_directory": str(self.models_dir),
            "ollama_host": "http://localhost:11434",
            "api_port": 8080,
            "max_conversations": 100,
            "auto_save": True,
            "chat_settings": {
                "temperature": 0.7,
                "max_tokens": 2048,
                "top_p": 0.9,
                "top_k": 40,
                "repeat_penalty": 1.1
            },
            "ui_settings": {
                "window_width": 1200,
                "window_height": 800,
                "sidebar_width": 250,
                "font_size": 12,
                "show_system_info": True
            }
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # Merge com configurações padrão
                    default_config.update(loaded_config)
            except Exception as e:
                print(f"Erro ao carregar configurações: {e}")
        
        return default_config
    
    def save_config(self):
        """Salvar configurações no arquivo"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar configurações: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Obter valor de configuração"""
        keys = key.split('.')
        value = self.settings
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """Definir valor de configuração"""
        keys = key.split('.')
        config = self.settings
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        self.save_config()
    
    @property
    def models_directory(self) -> Path:
        """Diretório de modelos"""
        return Path(self.get("models_directory", self.models_dir))
    
    @property
    def ollama_host(self) -> str:
        """Host do Ollama"""
        return self.get("ollama_host", "http://localhost:11434")
    
    @property
    def theme(self) -> str:
        """Tema da aplicação"""
        return self.get("theme", "dark")