"""
Arquivo: config.py
Descrição: Classe para gerenciar as configurações da aplicação.
"""

import json
from pathlib import Path
from typing import Dict, Any

class Config:
    def __init__(self):
        self.config_dir = Path.home() / ".sevenx_studio"
        self.config_file = self.config_dir / "config.json"
        self.default_models_path = self.config_dir / "models"
        self.logs_dir = self.config_dir / "logs"
        self.conversations_dir = self.config_dir / "conversations"
        
        self._create_directories()
        self.settings = self._load_config()
    
    def _create_directories(self):
        for directory in [self.config_dir, self.default_models_path, self.logs_dir, self.conversations_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _load_config(self) -> Dict[str, Any]:
        default_config = {
            "theme": "dark",
            "language": "pt-BR",
            "models_directory": str(self.default_models_path),
            "hf_token": "",
            "ollama_host": "http://localhost:11434",
            "api_port": 8080,
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
                "show_system_info": True,
                "lite_mode": False # OTIMIZAÇÃO: Modo Leve para PCs com menos recursos
            }
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    for key, value in loaded_config.items():
                        if isinstance(value, dict) and key in default_config:
                            default_config[key].update(value)
                        else:
                            default_config[key] = value
            except Exception as e:
                print(f"Erro ao carregar o arquivo de configuração: {e}")
        
        return default_config
    
    def save_config(self):
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar as configurações: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        keys = key.split('.')
        value = self.settings
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def set(self, key: str, value: Any):
        keys = key.split('.')
        config = self.settings
        for k in keys[:-1]:
            config = config.setdefault(k, {})
        config[keys[-1]] = value
        self.save_config()
    
    @property
    def models_directory(self) -> Path:
        return Path(self.get("models_directory"))
