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
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from huggingface_hub import list_models, model_info, hf_hub_download
    from transformers import AutoTokenizer, AutoModelForCausalLM, TextIteratorStreamer
    # Importa o carregador de modelos GGUF
    from ctransformers import AutoModelForCausalLM as AutoModelForCausalLM_GGUF
    HUGGINGFACE_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Bibliotecas do Hugging Face não disponíveis: {e}")
    HUGGINGFACE_AVAILABLE = False

from .config import Config


@dataclass
class ModelInfo:
    """Classe para representar informações de modelo."""
    name: str
    size: int
    path: str
    modified_at: str
    details: Dict
    status: str = "installed"


class SevenXEngine:
    """Motor de IA com suporte a múltiplos backends: Transformers e CTransformers (GGUF)."""
    
    def __init__(self, config: Config):
        self.config = config
        self.models_dir = Path(config.models_directory)
        self.loaded_models = {}
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_cache = {}  # Cache para modelos já carregados
        logger.info(f"SevenXEngine inicializado. Usando device: {self.device}")
        
        # Garantir que o diretório de modelos exista
        self.models_dir.mkdir(parents=True, exist_ok=True)

    def _find_gguf_file(self, model_dir: Path) -> Optional[Path]:
        """Encontra o primeiro arquivo .gguf em um diretório."""
        try:
            gguf_files = list(model_dir.glob("*.gguf"))
            return gguf_files[0] if gguf_files else None
        except Exception as e:
            logger.error(f"Erro ao procurar arquivos GGUF em {model_dir}: {e}")
            return None

    def _get_model_metadata(self, model_dir: Path) -> Dict:
        """Obtém metadados do modelo de forma otimizada."""
        try:
            info_file = model_dir / "_sevenx_info.json"
            if info_file.exists():
                with open(info_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.warning(f"Erro ao ler metadados do modelo: {e}")
            return {}

    def _estimate_model_size(self, model_dir: Path) -> int:
        """Estima o tamanho do modelo de forma eficiente."""
        try:
            return sum(f.stat().st_size for f in model_dir.rglob('*') if f.is_file())
        except Exception as e:
            logger.warning(f"Erro ao estimar tamanho do modelo: {e}")
            return 0

    def _filter_valid_transformers_params(self, params: Dict) -> Dict:
        """Filtra apenas parâmetros válidos para Transformers."""
        valid_params = {
            "max_new_tokens", "min_new_tokens", "do_sample", "temperature", 
            "top_k", "top_p", "typical_p", "epsilon_cutoff", "eta_cutoff",
            "diversity_penalty", "num_beams", "num_beam_groups", "penalty_alpha",
            "repetition_penalty", "length_penalty", "no_repeat_ngram_size",
            "bad_words_ids", "force_words_ids", "renormalize_logits", 
            "constraints", "prefix_allowed_tokens_fn", "readability_penalties",
            "guidance_scale", "low_memory", "num_return_sequences", 
            "pad_token_id", "bos_token_id", "eos_token_id"
        }
        
        # Filtrar apenas parâmetros válidos
        filtered_params = {k: v for k, v in params.items() if k in valid_params}
        
        # Mapear nomes de parâmetros para os esperados pelo Transformers
        param_mapping = {
            "max_tokens": "max_new_tokens",
            "repeat_penalty": "repetition_penalty"
        }
        
        # Aplicar mapeamento
        mapped_params = {}
        for key, value in filtered_params.items():
            if key in param_mapping:
                mapped_params[param_mapping[key]] = value
            else:
                mapped_params[key] = value
                
        return mapped_params

    def load_model(self, model_id: str, force_reload: bool = False) -> bool:
        """
        Carrega um modelo específico de forma otimizada.
        
        Args:
            model_id (str): ID do modelo a ser carregado
            force_reload (bool): Força o recarregamento mesmo se já estiver carregado
            
        Returns:
            bool: True se o modelo foi carregado com sucesso, False caso contrário
        """
        # Verifica se já está carregado e não precisa ser recarregado
        if model_id in self.loaded_models and not force_reload:
            logger.info(f"Modelo {model_id} já está carregado.")
            return True
            
        # Remove do cache se for forçar reload
        if force_reload and model_id in self.model_cache:
            del self.model_cache[model_id]
            
        model_dir_name = model_id.replace('/', '__')
        model_dir = self.models_dir / model_dir_name
        
        if not model_dir.exists():
            logger.error(f"Diretório do modelo não encontrado: {model_dir}")
            return False
            
        token = self.config.get("hf_token") or None
        logger.info(f"Carregando modelo {model_id} de {model_dir}...")
        
        try:
            # Verifica se é um modelo GGUF
            gguf_file_path = self._find_gguf_file(model_dir)
            if gguf_file_path:
                # --- Carregamento de Modelo GGUF ---
                logger.info(f"Arquivo GGUF detectado: {gguf_file_path.name}. Carregando com CTransformers...")
                
                # Configurações específicas para GGUF
                model_config = {
                    "model_type": 'llama',
                    "context_length": self.config.get("chat_settings.max_tokens", 2048),
                    "gpu_layers": self.config.get("gpu_layers", 0)  # Permite configurar camadas GPU
                }
                
                # Carregamento otimizado com cache
                if model_id in self.model_cache:
                    model = self.model_cache[model_id]
                else:
                    model = AutoModelForCausalLM_GGUF.from_pretrained(
                        str(gguf_file_path),
                        **model_config
                    )
                    self.model_cache[model_id] = model
                
                self.loaded_models[model_id] = {"model": model, "type": "gguf"}
                logger.info(f"Modelo GGUF {model_id} carregado com sucesso.")
                
            else:
                # --- Carregamento de Modelo Transformers Padrão ---
                logger.info("Carregando com a biblioteca Transformers...")
                
                # Carregamento otimizado do tokenizer
                tokenizer = AutoTokenizer.from_pretrained(
                    str(model_dir), 
                    token=token,
                    use_fast=True,  # Usar tokenizer rápido quando disponível
                    trust_remote_code=True  # Para modelos customizados
                )
                
                # Carregamento otimizado do modelo
                model = AutoModelForCausalLM.from_pretrained(
                    str(model_dir), 
                    token=token, 
                    low_cpu_mem_usage=True,
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,  # Otimização de tipo
                    attn_implementation="sdpa" if torch.__version__ >= "2.0" else "eager"  # Otimização de atenção
                )
                
                # Mover modelo para dispositivo correto
                model.to(self.device)
                
                # Configurações do tokenizer
                if tokenizer.pad_token is None: 
                    tokenizer.pad_token = tokenizer.eos_token
                if not getattr(tokenizer, 'chat_template', None): 
                    tokenizer.chat_template = None
                    
                self.loaded_models[model_id] = {
                    "model": model, 
                    "tokenizer": tokenizer, 
                    "type": "transformers"
                }
                logger.info(f"Modelo Transformers {model_id} carregado com sucesso.")
                
            return True
            
        except Exception as e:
            logger.error(f"Erro ao carregar o modelo {model_id}: {e}")
            logger.debug(traceback.format_exc())
            return False

    def generate_stream(self, model_id: str, messages: List[Dict], options: Optional[Dict] = None) -> Generator[str, None, None]:
        """
        Gera uma resposta em streaming a partir de um modelo carregado.
        
        Args:
            model_id (str): ID do modelo a ser usado
            messages (List[Dict]): Lista de mensagens para o modelo
            options (Optional[Dict]): Opções adicionais para geração
            
        Yields:
            str: Partes da resposta gerada
        """
        if model_id not in self.loaded_models:
            if not self.load_model(model_id):
                yield f"Erro: Falha ao carregar o modelo {model_id}."
                return
                
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
                        
                # Otimização de tokenização
                inputs = tokenizer(
                    [prompt_text], 
                    return_tensors="pt", 
                    padding=True, 
                    truncation=True,
                    max_length=self.config.get("chat_settings.max_tokens", 2048)
                ).to(self.device)
                
                # Configurações de geração otimizadas
                generation_kwargs = {
                    "input_ids": inputs.input_ids,
                    "attention_mask": inputs.attention_mask,
                    "streamer": TextIteratorStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True),
                    **opts
                }
                
                # Filtrar parâmetros válidos para Transformers
                filtered_opts = self._filter_valid_transformers_params(opts)
                generation_kwargs.update(filtered_opts)
                
                # Configurações específicas para otimização
                if "max_new_tokens" not in generation_kwargs:
                    generation_kwargs["max_new_tokens"] = self.config.get("chat_settings.max_tokens", 2048)
                
                thread = Thread(target=model.generate, kwargs=generation_kwargs)
                thread.start()
                
                for new_text in generation_kwargs["streamer"]:
                    yield new_text
                    
        except Exception as e:
            logger.error(f"Erro detalhado na geração de stream: {e}")
            logger.debug(traceback.format_exc())
            yield f"Erro durante a geração de texto: {e}"

    def generate_response(self, model_id: str, messages: List[Dict], options: Optional[Dict] = None) -> str:
        """
        Gera uma resposta completa (não streaming) a partir de um modelo carregado.
        
        Args:
            model_id (str): ID do modelo a ser usado
            messages (List[Dict]): Lista de mensagens para o modelo
            options (Optional[Dict]): Opções adicionais para geração
            
        Returns:
            str: Resposta gerada
        """
        if model_id not in self.loaded_models:
            if not self.load_model(model_id):
                return f"Erro: Falha ao carregar o modelo {model_id}."
                
        model_data = self.loaded_models[model_id]
        opts = options or {}
        
        try:
            if model_data["type"] == "gguf":
                # --- Geração com Modelo GGUF ---
                model = model_data["model"]
                # CTransformers espera uma string de prompt simples
                prompt = "\n".join([msg["content"] for msg in messages])
                response = model(prompt, **opts)
                return response
            else:
                # --- Geração com Modelo Transformers ---
                model, tokenizer = model_data["model"], model_data["tokenizer"]
                prompt_text = ""
                
                if tokenizer.chat_template:
                    prompt_text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
                else:
                    for message in messages:
                        prompt_text += message["content"] + tokenizer.eos_token
                        
                # Otimização de tokenização
                inputs = tokenizer(
                    [prompt_text], 
                    return_tensors="pt", 
                    padding=True, 
                    truncation=True,
                    max_length=self.config.get("chat_settings.max_tokens", 2048)
                ).to(self.device)
                
                # Configurações de geração otimizadas
                generation_kwargs = {
                    "input_ids": inputs.input_ids,
                    "attention_mask": inputs.attention_mask,
                    **opts
                }
                
                # Filtrar parâmetros válidos para Transformers
                filtered_opts = self._filter_valid_transformers_params(opts)
                generation_kwargs.update(filtered_opts)
                
                # Configurações específicas para otimização
                if "max_new_tokens" not in generation_kwargs:
                    generation_kwargs["max_new_tokens"] = self.config.get("chat_settings.max_tokens", 2048)
                
                # Gerar resposta completa
                output = model.generate(**generation_kwargs)
                generated_text = tokenizer.decode(output[0], skip_special_tokens=True)
                
                # Extrair apenas a parte gerada (remover o prompt)
                if tokenizer.chat_template:
                    # Para modelos com chat template, temos que lidar com isso diferentemente
                    return generated_text[len(prompt_text):].strip()
                else:
                    # Para modelos tradicionais, podemos usar o prompt como base
                    return generated_text
                
        except Exception as e:
            logger.error(f"Erro detalhado na geração de resposta: {e}")
            logger.debug(traceback.format_exc())
            return f"Erro durante a geração de texto: {e}"

    # --- Outros métodos (sem alterações significativas) ---
    def is_available(self) -> bool:
        """Verifica se o motor de IA está disponível."""
        try:
            torch.tensor([1.0])
            return True
        except Exception as e:
            logger.error(f"Erro no PyTorch, motor indisponível: {e}")
            return False

    def list_installed_models(self) -> List[ModelInfo]:
        """Lista todos os modelos instalados."""
        models = []
        try:
            for info_file in self.models_dir.glob("**/_sevenx_info.json"):
                model_dir = info_file.parent
                with open(info_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    
                size = self._estimate_model_size(model_dir)
                model_id = config.get('model_id', model_dir.name.replace('__', '/'))
                
                models.append(ModelInfo(
                    name=model_id,
                    size=size,
                    path=str(model_dir),
                    modified_at=datetime.fromtimestamp(info_file.stat().st_mtime).isoformat(),
                    details=config
                ))
            return models
        except Exception as e:
            logger.error(f"Erro ao listar modelos instalados: {e}")
            return []

    def search_online_models(self, query: str = "", model_type: str = "text-generation", limit: int = 50) -> List[Dict]:
        """Busca modelos online no Hugging Face."""
        if not HUGGINGFACE_AVAILABLE:
            logger.warning("Bibliotecas do Hugging Face não disponíveis para busca.")
            return []
            
        token = self.config.get("hf_token") or None
        try:
            hf_models = list_models(
                filter=model_type, 
                search=query, 
                limit=limit, 
                sort="downloads", 
                direction=-1, 
                token=token
            )
            return [
                {
                    "id": model.id, 
                    "name": model.id, 
                    "description": getattr(model, 'description', 'Sem descrição'), 
                    "downloads": model.downloads or 0, 
                    "type": model_type
                } 
                for model in hf_models if model.id
            ]
        except Exception as e:
            logger.error(f"Erro ao buscar modelos no Hugging Face: {e}")
            return []

    def download_model(self, model_id: str, progress_callback: Optional[Callable] = None) -> bool:
        """Faz download de um modelo do Hugging Face."""
        if not HUGGINGFACE_AVAILABLE:
            if progress_callback:
                progress_callback(100, "Erro: Bibliotecas do Hugging Face não instaladas.")
            return False
            
        token = self.config.get("hf_token") or None
        try:
            repo_info = model_info(model_id, token=token)
        except Exception as e:
            if "GatedRepo" in str(e):
                if progress_callback:
                    progress_callback(100, f"Acesso negado. Adicione seu token em Configurações > Avançado.")
            else:
                if progress_callback:
                    progress_callback(100, f"Erro: Modelo {model_id} não encontrado.")
            return False
            
        model_dir_name = model_id.replace('/', '__')
        model_dir = self.models_dir / model_dir_name
        model_dir.mkdir(parents=True, exist_ok=True)
        
        if progress_callback:
            progress_callback(0, f"Iniciando download de {model_id}...")
            
        try:
            repo_files = [f for f in repo_info.siblings if f.rfilename]
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
                    local_dir_use_symlinks=False, 
                    token=token
                )
                
            if progress_callback:
                progress_callback(95, "Salvando metadados...")
                
            info_data = {"model_id": model_id, "downloaded_at": datetime.now().isoformat()}
            with open(model_dir / "_sevenx_info.json", 'w', encoding='utf-8') as f:
                json.dump(info_data, f, indent=2)
                
            if progress_callback:
                progress_callback(100, f"Download de {model_id} concluído!")
                
            return True
            
        except Exception as e:
            logger.error(f"Erro durante o download do modelo {model_id}: {e}")
            if progress_callback:
                progress_callback(100, f"Erro ao baixar {model_id}.")
            if model_dir.exists():
                shutil.rmtree(model_dir)
            return False

    def unload_model(self, model_id: str) -> bool:
        """Descarrega um modelo da memória."""
        if model_id in self.loaded_models:
            del self.loaded_models[model_id]
            # Limpar cache do modelo específico
            if model_id in self.model_cache:
                del self.model_cache[model_id]
            if self.device == "cuda":
                torch.cuda.empty_cache()
            logger.info(f"Modelo {model_id} descarregado da memória.")
            return True
        return False

    def delete_model(self, model_id: str) -> bool:
        """Remove completamente um modelo do sistema."""
        self.unload_model(model_id)
        model_dir_name = model_id.replace('/', '__')
        model_dir = self.models_dir / model_dir_name
        
        if model_dir.exists():
            try:
                shutil.rmtree(model_dir)
                logger.info(f"Modelo {model_id} removido.")
                return True
            except Exception as e:
                logger.error(f"Erro ao remover o diretório do modelo {model_id}: {e}")
                return False
        return False

    def cleanup(self):
        """Limpa todos os recursos do motor de IA."""
        logger.info("Limpando recursos do motor de IA...")
        for model_id in list(self.loaded_models.keys()):
            self.unload_model(model_id)
        # Limpar cache completo
        self.model_cache.clear()
        logger.info("Limpeza concluída.")
