"""
Motor de IA próprio do SevenX Studio
"""

import torch
import json
import asyncio
import threading
from pathlib import Path
from typing import Dict, List, Optional, AsyncGenerator, Callable
from dataclasses import dataclass
from datetime import datetime
import requests
from huggingface_hub import hf_hub_download, list_repo_files
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

# Imports opcionais
try:
    from accelerate import init_empty_weights, load_checkpoint_and_dispatch
    ACCELERATE_AVAILABLE = True
except ImportError:
    ACCELERATE_AVAILABLE = False

@dataclass
class ModelInfo:
    """Informações sobre um modelo"""
    name: str
    size: int
    path: str
    modified_at: str
    details: Dict
    status: str = "available"

class SevenXEngine:
    """Motor de IA próprio do SevenX Studio"""
    
    def __init__(self, models_dir: Path):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.loaded_models = {}
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.session = None
        
        # Modelos disponíveis para download (apenas modelos de geração)
        self.available_models = {
            "microsoft/DialoGPT-small": {
                "name": "DialoGPT Small", 
                "description": "Modelo conversacional compacto - RECOMENDADO",
                "size": "120MB",
                "type": "chat"
            },
            "microsoft/DialoGPT-medium": {
                "name": "DialoGPT Medium",
                "description": "Modelo conversacional da Microsoft",
                "size": "350MB",
                "type": "chat"
            },
            "gpt2": {
                "name": "GPT-2",
                "description": "Modelo de linguagem OpenAI",
                "size": "500MB",
                "type": "generation"
            },
            "gpt2-medium": {
                "name": "GPT-2 Medium",
                "description": "GPT-2 versão média",
                "size": "1.5GB",
                "type": "generation"
            }
        }
    
    def is_available(self) -> bool:
        """Verificar se o motor está disponível"""
        try:
            # Verificar se PyTorch está funcionando
            torch.tensor([1.0])
            return True
        except:
            return False
    
    def list_models(self) -> List[ModelInfo]:
        """Listar modelos instalados"""
        models = []
        
        try:
            for model_dir in self.models_dir.iterdir():
                if model_dir.is_dir():
                    config_file = model_dir / "config.json"
                    if config_file.exists():
                        with open(config_file, 'r') as f:
                            config = json.load(f)
                        
                        # Calcular tamanho do modelo
                        size = sum(f.stat().st_size for f in model_dir.rglob('*') if f.is_file())
                        
                        # Usar nome do config ou mapear do nome do diretório
                        display_name = config.get('name', self._get_display_name_from_directory(model_dir.name))
                        
                        model = ModelInfo(
                            name=display_name,
                            size=size,
                            path=str(model_dir),
                            modified_at=datetime.fromtimestamp(model_dir.stat().st_mtime).isoformat(),
                            details=config,
                            status="installed"
                        )
                        models.append(model)
            
            return models
            
        except Exception as e:
            print(f"Erro ao listar modelos: {e}")
            return []
    
    def get_available_models(self) -> List[Dict]:
        """Obter lista de modelos disponíveis para download"""
        return [
            {
                "id": model_id,
                "name": info["name"],
                "description": info["description"],
                "size": info["size"],
                "type": info["type"]
            }
            for model_id, info in self.available_models.items()
        ]
    
    def download_model(self, model_id: str, progress_callback: Callable = None) -> bool:
        """Fazer download de um modelo do Hugging Face"""
        try:
            if model_id not in self.available_models:
                return False
            
            model_info = self.available_models[model_id]
            model_dir = self.models_dir / model_id.replace('/', '_')
            model_dir.mkdir(parents=True, exist_ok=True)
            
            if progress_callback:
                progress_callback(10, f"Iniciando download de {model_info['name']}...")
            
            # Listar arquivos do repositório
            try:
                files = list_repo_files(model_id)
                total_files = len(files)
                
                for i, filename in enumerate(files):
                    if progress_callback:
                        progress = int(10 + (i / total_files) * 80)
                        progress_callback(progress, f"Baixando {filename}...")
                    
                    # Download do arquivo
                    try:
                        file_path = hf_hub_download(
                            repo_id=model_id,
                            filename=filename,
                            cache_dir=str(model_dir),
                            local_dir=str(model_dir),
                            local_dir_use_symlinks=False
                        )
                    except Exception as e:
                        print(f"Erro ao baixar {filename}: {e}")
                        continue
                
            except Exception as e:
                print(f"Erro ao listar arquivos: {e}")
                # Fallback: baixar arquivos essenciais
                essential_files = ["config.json", "pytorch_model.bin", "tokenizer.json", "vocab.txt"]
                for filename in essential_files:
                    try:
                        hf_hub_download(
                            repo_id=model_id,
                            filename=filename,
                            cache_dir=str(model_dir),
                            local_dir=str(model_dir),
                            local_dir_use_symlinks=False
                        )
                    except:
                        continue
            
            # Criar arquivo de configuração local
            config = {
                "name": model_info["name"],
                "description": model_info["description"],
                "type": model_info["type"],
                "model_id": model_id,
                "downloaded_at": datetime.now().isoformat(),
                "device": self.device
            }
            
            with open(model_dir / "config.json", 'w') as f:
                json.dump(config, f, indent=2)
            
            if progress_callback:
                progress_callback(100, f"Download de {model_info['name']} concluído!")
            
            return True
            
        except Exception as e:
            print(f"Erro ao baixar modelo {model_id}: {e}")
            return False
    
    def delete_model(self, model_name: str) -> bool:
        """Remover um modelo"""
        try:
            # Descarregar modelo da memória se estiver carregado
            if model_name in self.loaded_models:
                del self.loaded_models[model_name]
                torch.cuda.empty_cache() if torch.cuda.is_available() else None
            
            # Remover diretório do modelo
            model_dir = self.models_dir / model_name.replace('/', '_')
            if model_dir.exists():
                import shutil
                shutil.rmtree(model_dir)
                return True
            
            return False
            
        except Exception as e:
            print(f"Erro ao remover modelo {model_name}: {e}")
            return False
    
    def load_model(self, model_name: str) -> bool:
        """Carregar modelo na memória"""
        try:
            print(f"Tentando carregar modelo: {model_name}")
            
            # Verificar se é um modelo compatível
            if "CodeBERT" in model_name or "BERT" in model_name or "DistilBERT" in model_name:
                print(f"❌ {model_name} não é compatível com geração de texto!")
                print("💡 Use DialoGPT Small ou GPT-2 para chat")
                return False
            
            if model_name in self.loaded_models:
                print(f"Modelo {model_name} já está carregado")
                return True
            
            # Mapear nomes de modelos para diretórios
            model_dir_name = self._get_model_directory_name(model_name)
            model_dir = self.models_dir / model_dir_name
            print(f"Procurando modelo em: {model_dir}")
            
            if not model_dir.exists():
                print(f"Diretório do modelo não existe: {model_dir}")
                # Tentar encontrar diretório similar
                similar_dir = self._find_similar_model_directory(model_name)
                if similar_dir:
                    model_dir = similar_dir
                    print(f"Encontrado diretório similar: {model_dir}")
                else:
                    return False
            
            # Carregar configuração
            config_file = model_dir / "config.json"
            config = {}
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = json.load(f)
                model_id = config.get('model_id', model_name)
                print(f"Configuração carregada: {model_id}")
            else:
                model_id = model_name
                print(f"Usando model_id padrão: {model_id}")
            
            print("Carregando tokenizer...")
            
            # Tentar diferentes abordagens para carregar
            try:
                # Primeira tentativa: carregar do diretório local
                tokenizer = AutoTokenizer.from_pretrained(str(model_dir), use_fast=False)
                print("Tokenizer carregado do diretório local")
            except Exception as e1:
                print(f"Erro ao carregar tokenizer local: {e1}")
                try:
                    # Segunda tentativa: carregar do Hugging Face
                    tokenizer = AutoTokenizer.from_pretrained(model_id, use_fast=False)
                    print("Tokenizer carregado do Hugging Face")
                except Exception as e2:
                    print(f"Erro ao carregar tokenizer do HF: {e2}")
                    return False
            
            # Configurar tokens especiais se não existirem
            if not hasattr(tokenizer, 'pad_token') or tokenizer.pad_token is None:
                if hasattr(tokenizer, 'eos_token') and tokenizer.eos_token:
                    tokenizer.pad_token = tokenizer.eos_token
                    print("Configurado pad_token = eos_token")
                else:
                    tokenizer.add_special_tokens({'pad_token': '[PAD]'})
                    print("Adicionado pad_token especial")
            
            if not hasattr(tokenizer, 'eos_token') or tokenizer.eos_token is None:
                tokenizer.add_special_tokens({'eos_token': '</s>'})
                print("Adicionado eos_token especial")
            
            print("Carregando modelo...")
            
            # Configurar parâmetros de carregamento mais conservadores
            load_params = {
                "torch_dtype": torch.float32,  # Usar float32 para compatibilidade
                "low_cpu_mem_usage": True,
            }
            
            try:
                # Primeira tentativa: carregar do diretório local
                model = AutoModelForCausalLM.from_pretrained(str(model_dir), **load_params)
                print("Modelo carregado do diretório local")
            except Exception as e1:
                print(f"Erro ao carregar modelo local: {e1}")
                try:
                    # Segunda tentativa: carregar do Hugging Face
                    model = AutoModelForCausalLM.from_pretrained(model_id, **load_params)
                    print("Modelo carregado do Hugging Face")
                except Exception as e2:
                    print(f"Erro ao carregar modelo do HF: {e2}")
                    return False
            
            # Mover para device
            model = model.to(self.device)
            print(f"Modelo movido para device: {self.device}")
            
            # Criar pipeline
            try:
                pipe = pipeline(
                    "text-generation",
                    model=model,
                    tokenizer=tokenizer,
                    device=-1  # Usar CPU para compatibilidade
                )
                print("Pipeline criado com sucesso")
            except Exception as e:
                print(f"Erro ao criar pipeline: {e}")
                # Fallback: criar estrutura simples
                pipe = {
                    "model": model,
                    "tokenizer": tokenizer
                }
                print("Usando estrutura simples em vez de pipeline")
            
            self.loaded_models[model_name] = {
                "pipeline": pipe,
                "tokenizer": tokenizer,
                "model": model,
                "config": config
            }
            
            print(f"Modelo {model_name} carregado com sucesso!")
            return True
            
        except Exception as e:
            print(f"Erro geral ao carregar modelo {model_name}: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def generate_response(self, model_name: str, prompt: str, options: Dict = None) -> str:
        """Gerar resposta do modelo"""
        try:
            print(f"Gerando resposta para modelo: {model_name}")
            
            # Carregar modelo se necessário
            if not self.load_model(model_name):
                return "Erro: Não foi possível carregar o modelo"
            
            model_data = self.loaded_models[model_name]
            pipeline = model_data["pipeline"]
            tokenizer = model_data["tokenizer"]
            model = model_data["model"]
            
            # Configurar parâmetros otimizados para conversação
            max_length = options.get("max_tokens", 150) if options else 150  # Aumentado
            temperature = options.get("temperature", 0.8) if options else 0.8  # Mais criativo
            top_p = options.get("top_p", 0.95) if options else 0.95  # Mais diversidade
            
            print(f"Parâmetros: max_length={max_length}, temperature={temperature}")
            
            # Melhorar o prompt para conversação
            conversation_prompt = f"""Você é um assistente útil e amigável. Responda de forma natural e conversacional.

Humano: {prompt.replace('Usuário:', '').replace('Assistente:', '').strip()}

Assistente:"""

            # Verificar se é pipeline real ou estrutura simples
            if hasattr(pipeline, '__call__'):
                # Pipeline real
                print("Usando pipeline real")
                # Configurar parâmetros de geração seguros
                generation_params = {
                    "max_length": len(conversation_prompt.split()) + max_length,
                    "temperature": temperature,
                    "top_p": top_p,
                    "do_sample": True,
                    "repetition_penalty": 1.2,
                }
                
                # Adicionar pad_token_id se disponível
                if hasattr(tokenizer, 'pad_token_id') and tokenizer.pad_token_id is not None:
                    generation_params["pad_token_id"] = tokenizer.pad_token_id
                elif hasattr(tokenizer, 'eos_token_id') and tokenizer.eos_token_id is not None:
                    generation_params["pad_token_id"] = tokenizer.eos_token_id
                
                response = pipeline(conversation_prompt, **generation_params)
                
                # Extrair resposta
                generated_text = response[0]["generated_text"]
                new_text = generated_text[len(conversation_prompt):].strip()
                
            else:
                # Estrutura simples - usar modelo diretamente
                print("Usando estrutura simples")
                
                # Tokenizar entrada
                inputs = tokenizer.encode(conversation_prompt, return_tensors="pt").to(self.device)
                
                # Configurar parâmetros de geração seguros
                generation_params = {
                    "max_length": inputs.shape[1] + max_length,
                    "temperature": temperature,
                    "top_p": top_p,
                    "do_sample": True,
                    "repetition_penalty": 1.2,
                    "no_repeat_ngram_size": 3,
                }
                
                # Adicionar pad_token_id se disponível
                if hasattr(tokenizer, 'pad_token_id') and tokenizer.pad_token_id is not None:
                    generation_params["pad_token_id"] = tokenizer.pad_token_id
                elif hasattr(tokenizer, 'eos_token_id') and tokenizer.eos_token_id is not None:
                    generation_params["pad_token_id"] = tokenizer.eos_token_id
                else:
                    # Fallback: usar 0 como pad_token_id
                    generation_params["pad_token_id"] = 0
                
                # Gerar resposta com parâmetros otimizados
                with torch.no_grad():
                    outputs = model.generate(inputs, **generation_params)
                
                # Decodificar resposta
                generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
                new_text = generated_text[len(conversation_prompt):].strip()
            
            result = new_text if new_text else "Desculpe, não consegui gerar uma resposta adequada."
            print(f"Resposta gerada: {result[:100]}...")
            return result
            
        except Exception as e:
            error_msg = f"Erro na geração: {str(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            return error_msg
    
    def chat(self, model_name: str, messages: List[Dict], options: Dict = None) -> Dict:
        """Enviar mensagens em formato de chat"""
        try:
            # Construir prompt a partir das mensagens
            prompt = ""
            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                
                if role == "system":
                    prompt += f"Sistema: {content}\n"
                elif role == "user":
                    prompt += f"Usuário: {content}\n"
                elif role == "assistant":
                    prompt += f"Assistente: {content}\n"
            
            prompt += "Assistente: "
            
            # Gerar resposta
            response = self.generate_response(model_name, prompt, options)
            
            return {
                "message": {
                    "role": "assistant",
                    "content": response
                },
                "done": True
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_model_info(self, model_name: str) -> Optional[Dict]:
        """Obter informações detalhadas de um modelo"""
        try:
            model_dir = self.models_dir / model_name.replace('/', '_')
            config_file = model_dir / "config.json"
            
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = json.load(f)
                
                # Calcular tamanho
                size = sum(f.stat().st_size for f in model_dir.rglob('*') if f.is_file())
                
                return {
                    "name": config.get("name", model_name),
                    "description": config.get("description", ""),
                    "type": config.get("type", "unknown"),
                    "size": size,
                    "path": str(model_dir),
                    "device": config.get("device", self.device),
                    "loaded": model_name in self.loaded_models
                }
            
            return None
            
        except Exception as e:
            print(f"Erro ao obter informações do modelo {model_name}: {e}")
            return None
    
    def unload_model(self, model_name: str) -> bool:
        """Descarregar modelo da memória"""
        try:
            if model_name in self.loaded_models:
                del self.loaded_models[model_name]
                
                # Limpar cache da GPU se disponível
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                
                return True
            return False
            
        except Exception as e:
            print(f"Erro ao descarregar modelo {model_name}: {e}")
            return False
    
    def get_system_info(self) -> Dict:
        """Obter informações do sistema"""
        return {
            "device": self.device,
            "cuda_available": torch.cuda.is_available(),
            "cuda_device_count": torch.cuda.device_count() if torch.cuda.is_available() else 0,
            "loaded_models": list(self.loaded_models.keys()),
            "models_directory": str(self.models_dir)
        }
    
    def optimize_model(self, model_name: str) -> bool:
        """Otimizar modelo para melhor performance"""
        try:
            if model_name not in self.loaded_models:
                if not self.load_model(model_name):
                    return False
            
            model_data = self.loaded_models[model_name]
            model = model_data["model"]
            
            # Aplicar otimizações
            if hasattr(model, 'half') and self.device == "cuda":
                model = model.half()  # Usar FP16 para economizar memória
            
            if hasattr(torch, 'compile'):
                model = torch.compile(model)  # PyTorch 2.0+ optimization
            
            # Atualizar modelo otimizado
            self.loaded_models[model_name]["model"] = model
            
            return True
            
        except Exception as e:
            print(f"Erro ao otimizar modelo {model_name}: {e}")
            return False
    
    def get_model_memory_usage(self, model_name: str) -> Dict:
        """Obter uso de memória do modelo"""
        try:
            if model_name not in self.loaded_models:
                return {"loaded": False, "memory_usage": 0}
            
            model = self.loaded_models[model_name]["model"]
            
            # Calcular uso de memória
            param_size = sum(p.numel() * p.element_size() for p in model.parameters())
            buffer_size = sum(b.numel() * b.element_size() for b in model.buffers())
            total_size = param_size + buffer_size
            
            return {
                "loaded": True,
                "memory_usage": total_size,
                "memory_usage_mb": total_size / (1024 * 1024),
                "parameters": sum(p.numel() for p in model.parameters()),
                "device": str(next(model.parameters()).device)
            }
            
        except Exception as e:
            print(f"Erro ao obter uso de memória do modelo {model_name}: {e}")
            return {"loaded": False, "memory_usage": 0, "error": str(e)}
    
    def validate_model(self, model_name: str) -> Dict:
        """Validar integridade do modelo"""
        try:
            model_dir = self.models_dir / model_name.replace('/', '_')
            
            if not model_dir.exists():
                return {"valid": False, "error": "Diretório do modelo não encontrado"}
            
            # Verificar arquivos essenciais
            config_file = model_dir / "config.json"
            if not config_file.exists():
                return {"valid": False, "error": "Arquivo config.json não encontrado"}
            
            # Tentar carregar configuração
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
            except Exception as e:
                return {"valid": False, "error": f"Erro ao ler config.json: {str(e)}"}
            
            # Verificar se pode carregar o modelo
            try:
                if self.load_model(model_name):
                    return {"valid": True, "message": "Modelo válido e carregado com sucesso"}
                else:
                    return {"valid": False, "error": "Falha ao carregar o modelo"}
            except Exception as e:
                return {"valid": False, "error": f"Erro ao validar: {str(e)}"}
            
        except Exception as e:
            return {"valid": False, "error": f"Erro na validação: {str(e)}"}
    
    def generate_streaming_response(self, model_name: str, prompt: str, options: Dict = None):
        """Gerar resposta em streaming (simulado)"""
        try:
            # Gerar resposta completa primeiro
            full_response = self.generate_response(model_name, prompt, options)
            
            # Simular streaming dividindo a resposta em palavras
            words = full_response.split()
            
            for i, word in enumerate(words):
                yield {
                    "response": word + " ",
                    "done": i == len(words) - 1
                }
                
        except Exception as e:
            yield {"error": str(e), "done": True}
    
    def list_available_models_online(self) -> List[Dict]:
        """Listar modelos disponíveis online (Hugging Face)"""
        # Lista expandida de modelos populares
        online_models = {
            "microsoft/DialoGPT-large": {
                "name": "DialoGPT Large",
                "description": "Modelo conversacional grande da Microsoft",
                "size": "800MB",
                "type": "chat",
                "downloads": "1M+"
            },
            "facebook/blenderbot-400M-distill": {
                "name": "BlenderBot 400M",
                "description": "Chatbot da Meta/Facebook",
                "size": "400MB", 
                "type": "chat",
                "downloads": "500K+"
            },
            "microsoft/CodeBERT-base-mlm": {
                "name": "CodeBERT MLM",
                "description": "Modelo para compreensão de código",
                "size": "500MB",
                "type": "code",
                "downloads": "100K+"
            },
            "huggingface/CodeBERTa-small-v1": {
                "name": "CodeBERTa Small",
                "description": "Modelo compacto para código",
                "size": "200MB",
                "type": "code", 
                "downloads": "50K+"
            },
            "sentence-transformers/all-MiniLM-L6-v2": {
                "name": "MiniLM Sentence Transformer",
                "description": "Modelo para embeddings de sentenças",
                "size": "90MB",
                "type": "embedding",
                "downloads": "2M+"
            }
        }
        
        # Combinar com modelos já definidos
        all_models = {**self.available_models, **online_models}
        
        return [
            {
                "id": model_id,
                "name": info["name"],
                "description": info["description"],
                "size": info["size"],
                "type": info["type"],
                "downloads": info.get("downloads", "N/A")
            }
            for model_id, info in all_models.items()
        ]
    
    def cleanup(self):
        """Limpar recursos e descarregar todos os modelos"""
        try:
            # Descarregar todos os modelos
            for model_name in list(self.loaded_models.keys()):
                self.unload_model(model_name)
            
            # Limpar cache
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            print("Limpeza de recursos concluída")
            
        except Exception as e:
            print(f"Erro na limpeza: {e}")
    
    def export_model_config(self, model_name: str) -> Optional[Dict]:
        """Exportar configuração do modelo"""
        try:
            model_info = self.get_model_info(model_name)
            if not model_info:
                return None
            
            config = {
                "model_name": model_name,
                "export_date": datetime.now().isoformat(),
                "model_info": model_info,
                "system_info": self.get_system_info()
            }
            
            return config
            
        except Exception as e:
            print(f"Erro ao exportar configuração: {e}")
            return None
    
    def benchmark_model(self, model_name: str, test_prompts: List[str] = None) -> Dict:
        """Fazer benchmark de performance do modelo"""
        try:
            if not test_prompts:
                test_prompts = [
                    "Olá, como você está?",
                    "Explique o que é inteligência artificial.",
                    "Conte uma piada."
                ]
            
            if not self.load_model(model_name):
                return {"error": "Não foi possível carregar o modelo"}
            
            import time
            results = []
            
            for prompt in test_prompts:
                start_time = time.time()
                response = self.generate_response(model_name, prompt)
                end_time = time.time()
                
                results.append({
                    "prompt": prompt,
                    "response_length": len(response),
                    "time_seconds": end_time - start_time,
                    "tokens_per_second": len(response.split()) / (end_time - start_time)
                })
            
            # Calcular estatísticas
            avg_time = sum(r["time_seconds"] for r in results) / len(results)
            avg_tokens_per_sec = sum(r["tokens_per_second"] for r in results) / len(results)
            
            return {
                "model_name": model_name,
                "benchmark_date": datetime.now().isoformat(),
                "results": results,
                "average_time_seconds": avg_time,
                "average_tokens_per_second": avg_tokens_per_sec,
                "total_tests": len(test_prompts)
            }
            
        except Exception as e:
            return {"error": f"Erro no benchmark: {str(e)}"}
    
    def _get_model_directory_name(self, model_name: str) -> str:
        """Mapear nome do modelo para nome do diretório"""
        # Mapeamentos conhecidos
        mappings = {
            "DialoGPT Small": "microsoft_DialoGPT-small",
            "DialoGPT Medium": "microsoft_DialoGPT-medium", 
            "DialoGPT Large": "microsoft_DialoGPT-large",
            "GPT-2": "gpt2",
            "GPT-2 Medium": "gpt2-medium",
            "CodeBERT": "microsoft_CodeBERT-base",
            "DistilBERT Base": "distilbert-base-uncased"
        }
        
        return mappings.get(model_name, model_name.replace('/', '_'))
    
    def _find_similar_model_directory(self, model_name: str) -> Optional[Path]:
        """Encontrar diretório similar ao modelo"""
        try:
            # Procurar por diretórios que contenham parte do nome
            search_terms = model_name.lower().split()
            
            for model_dir in self.models_dir.iterdir():
                if model_dir.is_dir():
                    dir_name_lower = model_dir.name.lower()
                    
                    # Verificar se algum termo está no nome do diretório
                    for term in search_terms:
                        if term in dir_name_lower:
                            print(f"Encontrado diretório similar: {model_dir.name}")
                            return model_dir
            
            return None
            
        except Exception as e:
            print(f"Erro ao procurar diretório similar: {e}")
            return None
    
    def _get_display_name_from_directory(self, dir_name: str) -> str:
        """Mapear nome do diretório para nome de exibição"""
        # Mapeamentos reversos
        reverse_mappings = {
            "microsoft_DialoGPT-small": "DialoGPT Small",
            "microsoft_DialoGPT-medium": "DialoGPT Medium",
            "microsoft_DialoGPT-large": "DialoGPT Large",
            "gpt2": "GPT-2",
            "gpt2-medium": "GPT-2 Medium",
            "microsoft_CodeBERT-base": "CodeBERT",
            "distilbert-base-uncased": "DistilBERT Base"
        }
        
        return reverse_mappings.get(dir_name, dir_name)