"""
Arquivo: sevenx_engine.py
Descrição: Motor de IA próprio do SevenX Studio para gerenciar modelos do Hugging Face.
"""

import torch
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime

try:
    from huggingface_hub import list_models, model_info, hf_hub_download
    from transformers import AutoTokenizer, AutoModelForCausalLM
    HUGGINGFACE_AVAILABLE = True
except ImportError:
    HUGGINGFACE_AVAILABLE = False

@dataclass
class ModelInfo:
    """Estrutura de dados para armazenar informações sobre um modelo instalado."""
    name: str
    size: int
    path: str
    modified_at: str
    details: Dict
    status: str = "installed"

class SevenXEngine:
    """
    Motor de IA com capacidade de buscar, baixar, gerenciar e executar
    modelos de linguagem do Hugging Face.
    """
    
    def __init__(self, models_dir: Path):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.loaded_models = {}
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        if not HUGGINGFACE_AVAILABLE:
            print("AVISO: As bibliotecas 'transformers' e 'huggingface_hub' não estão instaladas.")
        
        print(f"SevenXEngine inicializado. Usando device: {self.device}")

    def is_available(self) -> bool:
        try:
            torch.tensor([1.0])
            return True
        except Exception as e:
            print(f"Erro no PyTorch, motor indisponível: {e}")
            return False
    
    def list_installed_models(self) -> List[ModelInfo]:
        """Lista todos os modelos que foram baixados e estão disponíveis localmente."""
        models = []
        try:
            for info_file in self.models_dir.glob("**/_sevenx_info.json"):
                model_dir = info_file.parent
                with open(info_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                size = sum(f.stat().st_size for f in model_dir.rglob('*') if f.is_file())
                model_id = config.get('model_id', model_dir.name.replace('__', '/'))
                
                model = ModelInfo(
                    name=model_id,
                    size=size,
                    path=str(model_dir),
                    modified_at=datetime.fromtimestamp(info_file.stat().st_mtime).isoformat(),
                    details=config,
                    status="installed"
                )
                models.append(model)
            return models
        except Exception as e:
            print(f"Erro ao listar modelos instalados: {e}")
            return []
    
    def search_online_models(self, query: str = "", model_type: str = "text-generation", limit: int = 50) -> List[Dict]:
        if not HUGGINGFACE_AVAILABLE: return []
        print(f"Buscando modelos online com query='{query}', tipo='{model_type}'")
        try:
            hf_models = list_models(filter=model_type, search=query, limit=limit, sort="downloads", direction=-1)
            return [{"id": model.id, "name": model.id, "description": getattr(model, 'description', 'Sem descrição'), "downloads": model.downloads or 0, "type": model_type} for model in hf_models if model.id]
        except Exception as e:
            print(f"Erro ao buscar modelos no Hugging Face: {e}")
            return []

    def download_model(self, model_id: str, progress_callback: Optional[Callable] = None) -> bool:
        """Faz o download de um modelo, salvando os arquivos diretamente no diretório local."""
        if not HUGGINGFACE_AVAILABLE:
            if progress_callback: progress_callback(100, "Erro: Bibliotecas do Hugging Face não instaladas.")
            return False
        try:
            repo_info = model_info(model_id)
        except Exception:
            if progress_callback: progress_callback(100, f"Erro: Modelo {model_id} não encontrado.")
            return False
            
        model_dir_name = model_id.replace('/', '__')
        model_dir = self.models_dir / model_dir_name
        model_dir.mkdir(parents=True, exist_ok=True)
        
        if progress_callback: progress_callback(0, f"Iniciando download de {model_id}...")
        
        try:
            # **CORREÇÃO**: Baixar cada arquivo individualmente para o diretório local correto.
            # Isso evita o problema do cache da biblioteca transformers.
            repo_files = list(repo_info.siblings)
            total_files = len(repo_files)

            for i, sibling in enumerate(repo_files):
                filename = sibling.rfilename
                if progress_callback:
                    progress = int(((i + 1) / total_files) * 95)
                    progress_callback(progress, f"Baixando {filename}...")

                hf_hub_download(
                    repo_id=model_id,
                    filename=filename,
                    local_dir=str(model_dir),
                    local_dir_use_symlinks=False # Garante que os arquivos sejam copiados
                )

            if progress_callback: progress_callback(95, "Salvando metadados...")
            info_data = {"model_id": model_id, "downloaded_at": datetime.now().isoformat()}
            with open(model_dir / "_sevenx_info.json", 'w', encoding='utf-8') as f:
                json.dump(info_data, f, indent=2)

            if progress_callback: progress_callback(100, f"Download de {model_id} concluído!")
            return True
            
        except Exception as e:
            print(f"Erro durante o download do modelo {model_id}: {e}")
            if progress_callback: progress_callback(100, f"Erro ao baixar {model_id}.")
            if model_dir.exists(): shutil.rmtree(model_dir)
            return False

    def load_model(self, model_id: str) -> bool:
        """Carrega um modelo instalado na memória."""
        if model_id in self.loaded_models: return True
        
        model_dir_name = model_id.replace('/', '__')
        model_dir = self.models_dir / model_dir_name
        
        if not model_dir.exists(): 
            print(f"Erro: diretório do modelo {model_id} não encontrado.")
            return False
            
        print(f"Carregando modelo {model_id} de {model_dir}...")
        try:
            # Agora ele vai ler o config.json que foi baixado diretamente para o diretório
            tokenizer = AutoTokenizer.from_pretrained(str(model_dir))
            model = AutoModelForCausalLM.from_pretrained(str(model_dir))
            model.to(self.device)
            
            if tokenizer.pad_token is None: tokenizer.pad_token = tokenizer.eos_token
            
            self.loaded_models[model_id] = {"model": model, "tokenizer": tokenizer}
            print(f"Modelo {model_id} carregado com sucesso no device '{self.device}'.")
            return True
        except Exception as e:
            print(f"Erro ao carregar o modelo {model_id}: {e}")
            return False

    def unload_model(self, model_id: str) -> bool:
        """Descarrega um modelo da memória para liberar recursos."""
        if model_id in self.loaded_models:
            del self.loaded_models[model_id]
            if self.device == "cuda":
                torch.cuda.empty_cache()
            print(f"Modelo {model_id} descarregado da memória.")
            return True
        return False

    def delete_model(self, model_id: str) -> bool:
        """Remove um modelo do disco."""
        self.unload_model(model_id)
        model_dir_name = model_id.replace('/', '__')
        model_dir = self.models_dir / model_dir_name
        if model_dir.exists():
            try:
                shutil.rmtree(model_dir)
                print(f"Modelo {model_id} removido de {model_dir}.")
                return True
            except Exception as e:
                print(f"Erro ao remover o diretório do modelo {model_id}: {e}")
                return False
        return False

    def generate_response(self, model_id: str, prompt: str, options: Optional[Dict] = None) -> str:
        """Gera uma resposta a partir de um modelo carregado."""
        if model_id not in self.loaded_models:
            if not self.load_model(model_id): return f"Erro: Falha ao carregar o modelo {model_id}."
        
        model_data = self.loaded_models[model_id]
        model, tokenizer = model_data["model"], model_data["tokenizer"]
        opts = options or {}
        max_new_tokens = opts.get("max_new_tokens", 150)
        temperature = opts.get("temperature", 0.7)
        
        try:
            inputs = tokenizer(prompt, return_tensors="pt").to(self.device)
            with torch.no_grad():
                outputs = model.generate(**inputs, max_new_tokens=max_new_tokens, temperature=temperature, pad_token_id=tokenizer.eos_token_id, do_sample=True)
            response_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
            return response_text[len(prompt):].strip()
        except Exception as e:
            return f"Erro durante a geração de texto: {e}"
