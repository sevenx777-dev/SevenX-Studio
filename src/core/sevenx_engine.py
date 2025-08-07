"""
Arquivo: sevenx_engine.py
Descrição: Motor de IA com suporte a modelos Transformers e GGUF (via ctransformers).
"""

import torch
import json
import shutil
import traceback
from pathlib import Path
from threading import Thread
from typing import Dict, List, Optional, Callable, Generator
from dataclasses import dataclass
from datetime import datetime

try:
    from huggingface_hub import list_models, model_info, hf_hub_download
    from transformers import AutoTokenizer, AutoModelForCausalLM, TextIteratorStreamer
    # Importa o carregador de modelos GGUF
    from ctransformers import AutoModelForCausalLM as AutoModelForCausalLM_GGUF
    HUGGINGFACE_AVAILABLE = True
except ImportError:
    HUGGINGFACE_AVAILABLE = False

from .config import Config

@dataclass
class ModelInfo:
    name: str; size: int; path: str; modified_at: str; details: Dict; status: str = "installed"

class SevenXEngine:
    """Motor de IA com suporte a múltiplos backends: Transformers e CTransformers (GGUF)."""
    
    def __init__(self, config: Config):
        self.config = config
        self.models_dir = config.models_directory
        self.loaded_models = {}
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"SevenXEngine inicializado. Usando device: {self.device}")

    def _find_gguf_file(self, model_dir: Path) -> Optional[Path]:
        """Encontra o primeiro arquivo .gguf em um diretório."""
        gguf_files = list(model_dir.glob("*.gguf"))
        return gguf_files[0] if gguf_files else None

    def load_model(self, model_id: str) -> bool:
        if model_id in self.loaded_models: return True
        
        model_dir_name = model_id.replace('/', '__')
        model_dir = self.models_dir / model_dir_name
        if not model_dir.exists(): return False
        
        token = self.config.get("hf_token") or None
        print(f"Carregando modelo {model_id} de {model_dir}...")

        try:
            gguf_file_path = self._find_gguf_file(model_dir)
            
            if gguf_file_path:
                # --- Carregamento de Modelo GGUF ---
                print(f"Arquivo GGUF detectado: {gguf_file_path.name}. Carregando com CTransformers...")
                model = AutoModelForCausalLM_GGUF.from_pretrained(
                    str(gguf_file_path),
                    model_type='llama', # Tipo genérico, funciona para a maioria
                    context_length=self.config.get("chat_settings.max_tokens", 2048)
                )
                self.loaded_models[model_id] = {"model": model, "type": "gguf"}
                print(f"Modelo GGUF {model_id} carregado com sucesso no CPU.")
            else:
                # --- Carregamento de Modelo Transformers Padrão ---
                print("Carregando com a biblioteca Transformers...")
                tokenizer = AutoTokenizer.from_pretrained(str(model_dir), token=token)
                model = AutoModelForCausalLM.from_pretrained(
                    str(model_dir), 
                    token=token, 
                    low_cpu_mem_usage=True
                )
                model.to(self.device)
                if tokenizer.pad_token is None: tokenizer.pad_token = tokenizer.eos_token
                if not getattr(tokenizer, 'chat_template', None): tokenizer.chat_template = None
                self.loaded_models[model_id] = {"model": model, "tokenizer": tokenizer, "type": "transformers"}
                print(f"Modelo Transformers {model_id} carregado com sucesso.")

            return True
        except Exception as e:
            print(f"Erro ao carregar o modelo {model_id}: {e}")
            traceback.print_exc()
            return False

    def generate_stream(self, model_id: str, messages: List[Dict], options: Optional[Dict] = None) -> Generator[str, None, None]:
        if model_id not in self.loaded_models:
            if not self.load_model(model_id):
                yield f"Erro: Falha ao carregar o modelo {model_id}."; return
        
        model_data = self.loaded_models[model_id]
        opts = options or {}

        try:
            if model_data["type"] == "gguf":
                # --- Geração com Modelo GGUF ---
                model = model_data["model"]
                # CTransformers espera uma string de prompt simples
                prompt = "\n".join([msg["content"] for msg in messages])
                stream_generator = model(prompt, stream=True, **opts)
                for chunk in stream_generator:
                    yield chunk
            else:
                # --- Geração com Modelo Transformers ---
                model, tokenizer = model_data["model"], model_data["tokenizer"]
                prompt_text = ""
                if tokenizer.chat_template:
                    prompt_text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
                else:
                    for message in messages:
                        prompt_text += message["content"] + tokenizer.eos_token
                
                inputs = tokenizer([prompt_text], return_tensors="pt").to(self.device)
                streamer = TextIteratorStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)
                generation_kwargs = {"input_ids": inputs.input_ids, "attention_mask": inputs.attention_mask, "streamer": streamer, **opts}
                thread = Thread(target=model.generate, kwargs=generation_kwargs)
                thread.start()
                for new_text in streamer:
                    yield new_text
        except Exception as e:
            print(f"Erro detalhado na geração de stream: {e}"); traceback.print_exc()
            yield f"Erro durante a geração de texto: {e}"

    # --- Outros métodos (sem alterações significativas) ---
    def is_available(self) -> bool:
        try:
            torch.tensor([1.0]); return True
        except Exception as e:
            print(f"Erro no PyTorch, motor indisponível: {e}"); return False
    
    def list_installed_models(self) -> List[ModelInfo]:
        models = []
        try:
            for info_file in self.models_dir.glob("**/_sevenx_info.json"):
                model_dir = info_file.parent
                with open(info_file, 'r', encoding='utf-8') as f: config = json.load(f)
                size = sum(f.stat().st_size for f in model_dir.rglob('*') if f.is_file())
                model_id = config.get('model_id', model_dir.name.replace('__', '/'))
                models.append(ModelInfo(name=model_id, size=size, path=str(model_dir), modified_at=datetime.fromtimestamp(info_file.stat().st_mtime).isoformat(), details=config))
            return models
        except Exception as e:
            print(f"Erro ao listar modelos instalados: {e}"); return []
    
    def search_online_models(self, query: str = "", model_type: str = "text-generation", limit: int = 50) -> List[Dict]:
        if not HUGGINGFACE_AVAILABLE: return []
        token = self.config.get("hf_token") or None
        try:
            hf_models = list_models(filter=model_type, search=query, limit=limit, sort="downloads", direction=-1, token=token)
            return [{"id": model.id, "name": model.id, "description": getattr(model, 'description', 'Sem descrição'), "downloads": model.downloads or 0, "type": model_type} for model in hf_models if model.id]
        except Exception as e:
            print(f"Erro ao buscar modelos no Hugging Face: {e}"); return []

    def download_model(self, model_id: str, progress_callback: Optional[Callable] = None) -> bool:
        if not HUGGINGFACE_AVAILABLE:
            if progress_callback: progress_callback(100, "Erro: Bibliotecas do Hugging Face não instaladas."); return False
        
        token = self.config.get("hf_token") or None
        
        try:
            repo_info = model_info(model_id, token=token)
        except Exception as e:
            if "GatedRepo" in str(e):
                if progress_callback: progress_callback(100, f"Acesso negado. Adicione seu token em Configurações > Avançado.")
            else:
                if progress_callback: progress_callback(100, f"Erro: Modelo {model_id} não encontrado.")
            return False
            
        model_dir_name = model_id.replace('/', '__')
        model_dir = self.models_dir / model_dir_name
        model_dir.mkdir(parents=True, exist_ok=True)
        
        if progress_callback: progress_callback(0, f"Iniciando download de {model_id}...")
        
        try:
            repo_files = [f for f in repo_info.siblings if f.rfilename]
            total_files = len(repo_files)
            for i, sibling in enumerate(repo_files):
                filename = sibling.rfilename
                if progress_callback:
                    progress = int(((i + 1) / total_files) * 95)
                    progress_callback(progress, f"Baixando {filename}...")
                hf_hub_download(repo_id=model_id, filename=filename, local_dir=str(model_dir), local_dir_use_symlinks=False, token=token)

            if progress_callback: progress_callback(95, "Salvando metadados...")
            info_data = {"model_id": model_id, "downloaded_at": datetime.now().isoformat()}
            with open(model_dir / "_sevenx_info.json", 'w', encoding='utf-8') as f: json.dump(info_data, f, indent=2)
            if progress_callback: progress_callback(100, f"Download de {model_id} concluído!")
            return True
            
        except Exception as e:
            print(f"Erro durante o download do modelo {model_id}: {e}")
            if progress_callback: progress_callback(100, f"Erro ao baixar {model_id}.")
            if model_dir.exists(): shutil.rmtree(model_dir)
            return False

    def unload_model(self, model_id: str) -> bool:
        if model_id in self.loaded_models:
            del self.loaded_models[model_id]
            if self.device == "cuda": torch.cuda.empty_cache()
            print(f"Modelo {model_id} descarregado da memória."); return True
        return False

    def delete_model(self, model_id: str) -> bool:
        self.unload_model(model_id)
        model_dir_name = model_id.replace('/', '__')
        model_dir = self.models_dir / model_dir_name
        if model_dir.exists():
            try:
                shutil.rmtree(model_dir); print(f"Modelo {model_id} removido."); return True
            except Exception as e:
                print(f"Erro ao remover o diretório do modelo {model_id}: {e}"); return False
        return False

    def cleanup(self):
        print("Limpando recursos do motor de IA...")
        for model_id in list(self.loaded_models.keys()):
            self.unload_model(model_id)
        print("Limpeza concluída.")
