"""
Cliente para Hugging Face Hub (compatibilidade)
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from pathlib import Path

@dataclass
class HFModel:
    """Modelo do Hugging Face"""
    name: str
    model_id: str
    description: str
    size_gb: float
    parameters: str
    is_downloaded: bool = False

class HuggingFaceClient:
    """Cliente para compatibilidade com código antigo"""
    
    def __init__(self, models_dir: str):
        self.models_dir = Path(models_dir)
        self.loaded_model = None
    
    def get_popular_models(self) -> List[HFModel]:
        """Obter modelos populares (lista vazia - sem modelos predefinidos)"""
        return []  # Retorna lista vazia - agora busca dinamicamente
    
    def is_model_downloaded(self, model_id: str) -> bool:
        """Verificar se modelo está baixado"""
        model_dir = self.models_dir / model_id.replace('/', '_')
        return model_dir.exists()
    
    def is_model_loaded(self, model_id: str) -> bool:
        """Verificar se modelo está carregado"""
        return self.loaded_model == model_id
    
    def load_model(self, model_id: str) -> bool:
        """Carregar modelo"""
        if self.is_model_downloaded(model_id):
            self.loaded_model = model_id
            return True
        return False
    
    def get_loaded_model(self) -> Optional[str]:
        """Obter modelo carregado"""
        return self.loaded_model
    
    def download_model(self, model_id: str, progress_callback=None) -> bool:
        """Download de modelo (simulado)"""
        if progress_callback:
            for i in range(0, 101, 10):
                progress_callback(i, f"Baixando {model_id}...")
        return True
    
    def generate_response(self, prompt: str, max_length: int = 100, 
                         temperature: float = 0.7, top_p: float = 0.9):
        """Gerar resposta (simulado)"""
        words = f"Esta é uma resposta simulada para: {prompt}".split()
        for word in words:
            yield word + " "