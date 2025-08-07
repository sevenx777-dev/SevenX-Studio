"""
Arquivo: config.py
Descrição: Classe robusta para gerenciar as configurações da aplicação.
"""

import json
from pathlib import Path
from typing import Dict, Any

class Config:
    """Classe robusta para gerenciar as configurações da aplicação."""
    
    def __init__(self):
        self.config_dir = Path.home() / ".sevenx_studio"
        self.config_file = self.config_dir / "config.json"
        self.default_models_path = self.config_dir / "models"
        self.logs_dir = self.config_dir / "logs"
        self.conversations_dir = self.config_dir / "conversations"
        
        self._create_directories()
        self.settings = self._load_from_file()

    def _get_default_config(self) -> Dict[str, Any]:
        """Retorna um dicionário com todas as configurações padrão da aplicação."""
        return {
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
                "lite_mode": False
            }
        }

    def _load_from_file(self) -> Dict[str, Any]:
        """Carrega as configurações do arquivo, mesclando com os padrões."""
        defaults = self._get_default_config()
        if not self.config_file.exists():
            print("Arquivo de configuração não encontrado. Usando padrões.")
            return defaults

        try:
            print(f"Carregando configurações de: {self.config_file}")
            with open(self.config_file, 'r', encoding='utf-8') as f:
                loaded_config = json.load(f)
            
            # Mescla os valores salvos sobre os padrões para garantir que novas chaves sejam adicionadas
            for key, value in loaded_config.items():
                if isinstance(value, dict) and key in defaults:
                    defaults[key].update(value)
                else:
                    defaults[key] = value
        except Exception as e:
            print(f"Erro ao carregar config.json, usando padrões: {e}")
            return self._get_default_config()
        
        print("Configurações carregadas com sucesso.")
        return defaults

    def save_config(self) -> bool:
        """Salva o estado atual das configurações no arquivo JSON e retorna True em caso de sucesso."""
        try:
            print(f"Salvando configurações em: {self.config_file}")
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            print("Configurações salvas com sucesso!")
            return True
        except Exception as e:
            print(f"ERRO AO SALVAR CONFIGURAÇÕES: {e}")
            return False

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
        """Define um valor de configuração na memória (não salva no arquivo)."""
        keys = key.split('.')
        config = self.settings
        for k in keys[:-1]:
            config = config.setdefault(k, {})
        config[keys[-1]] = value

    def reset_to_defaults(self):
        """Restaura as configurações para os valores padrão e salva no arquivo."""
        self.settings = self._get_default_config()
        self.save_config()

    @property
    def models_directory(self) -> Path:
        return Path(self.get("models_directory"))

    def _create_directories(self):
        for directory in [self.config_dir, self.default_models_path, self.logs_dir, self.conversations_dir]:
            directory.mkdir(parents=True, exist_ok=True)
