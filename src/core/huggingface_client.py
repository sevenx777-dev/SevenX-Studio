"""
Arquivo: huggingface_client.py
Descrição: Cliente de compatibilidade e classe de configuração para o SevenXEngine.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional

# Importa a classe principal do nosso motor de IA
from .sevenx_engine import SevenXEngine

class Config:
    """Classe para gerenciar as configurações da aplicação."""
    
    def __init__(self):
        self.config_dir = Path.home() / ".sevenx_studio"
        self.config_file = self.config_dir / "config.json"
        self.default_models_path = self.config_dir / "models"
        self.logs_dir = self.config_dir / "logs"
        self.conversations_dir = self.config_dir / "conversations"
        
        self._create_directories()
        self.settings = self._load_config()
    
    def _create_directories(self):
        """Cria os diretórios necessários para a aplicação se não existirem."""
        for directory in [self.config_dir, self.default_models_path, self.logs_dir, self.conversations_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _load_config(self) -> Dict[str, Any]:
        """Carrega as configurações do arquivo JSON, usando padrões se o arquivo não existir."""
        default_config = {
            "theme": "dark",
            "language": "pt-BR",
            "models_directory": str(self.default_models_path),
            "hf_token": "", # Campo para o token de acesso do Hugging Face
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
                "show_system_info": True
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
        """Salva as configurações atuais no arquivo JSON."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar as configurações: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Obtém um valor de configuração usando notação de ponto."""
        keys = key.split('.')
        value = self.settings
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def set(self, key: str, value: Any):
        """Define um valor de configuração e salva o arquivo."""
        keys = key.split('.')
        config = self.settings
        for k in keys[:-1]:
            config = config.setdefault(k, {})
        config[keys[-1]] = value
        self.save_config()
    
    @property
    def models_directory(self) -> Path:
        """Retorna o caminho para o diretório de modelos como um objeto Path."""
        return Path(self.get("models_directory"))

class HuggingFaceClient:
    """Cliente de compatibilidade que utiliza o SevenXEngine."""
    def __init__(self, engine: SevenXEngine):
        self.engine = engine
    
    def get_popular_models(self, query: str = "") -> List[Dict]:
        return self.engine.search_online_models(query=query)
    
    def is_model_downloaded(self, model_id: str) -> bool:
        return any(model.name == model_id for model in self.engine.list_installed_models())
    
    def is_model_loaded(self, model_id: str) -> bool:
        return model_id in self.engine.loaded_models
    
    def load_model(self, model_id: str) -> bool:
        return self.engine.load_model(model_id)
    
    def get_loaded_model(self) -> Optional[str]:
        return next(iter(self.engine.loaded_models), None)
    
    def download_model(self, model_id: str, progress_callback=None) -> bool:
        return self.engine.download_model(model_id, progress_callback)
    
    def generate_response(self, prompt: str, **kwargs) -> str:
        loaded_model_id = self.get_loaded_model()
        if not loaded_model_id:
            return "Nenhum modelo carregado."
        return self.engine.generate_response(loaded_model_id, prompt, options=kwargs)
