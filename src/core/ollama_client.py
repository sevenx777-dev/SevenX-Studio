"""
Arquivo: ollama_client.py
Descrição: Cliente para interagir com a API do Ollama.
"""

import requests
import json
import time
from typing import List, Dict, Generator, Optional
from threading import Lock
import logging

from .config import Config

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OllamaClient:
    """
    Cliente para listar modelos e gerar respostas em streaming
    a partir de um servidor Ollama.
    """
    def __init__(self, config: Config):
        self.config = config
        self.host = self.config.get("ollama_host", "http://localhost:11434")
        self._lock = Lock()  # Para garantir acesso thread-safe
        self._last_request_time = 0
        self._request_interval = 0.1  # Intervalo mínimo entre requisições (segundos)

    def _rate_limit(self):
        """Aplica rate limiting para evitar sobrecarga do servidor."""
        current_time = time.time()
        time_since_last = current_time - self._last_request_time
        if time_since_last < self._request_interval:
            time.sleep(self._request_interval - time_since_last)
        self._last_request_time = time.time()

    def is_server_reachable(self) -> bool:
        """Verifica se o servidor Ollama está acessível."""
        try:
            # Primeiro tenta verificar se o endpoint básico está acessível
            response = requests.get(f"{self.host}/api/tags", timeout=3)
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            logger.debug(f"Servidor Ollama não acessível: {e}")
            return False

    def list_models(self) -> List[Dict]:
        """Busca a lista de modelos disponíveis no servidor Ollama."""
        if not self.is_server_reachable():
            logger.warning("Servidor Ollama não está acessível.")
            return []
        
        try:
            # Aplica rate limiting
            self._rate_limit()
            
            response = requests.get(f"{self.host}/api/tags", timeout=10)
            response.raise_for_status()
            
            models_data = response.json().get("models", [])
            models = []
            for model in models_data:
                models.append({
                    "id": model["name"],
                    "name": model["name"],
                    "modified_at": model.get("modified_at", ""),
                    "size": model.get("size", 0),
                    "digest": model.get("digest", "")
                })
            return models
        except requests.exceptions.Timeout:
            logger.error("Tempo limite excedido ao buscar modelos do Ollama")
            return []
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro de rede ao buscar modelos do Ollama: {e}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao decodificar JSON dos modelos: {e}")
            return []
        except Exception as e:
            logger.error(f"Erro inesperado ao buscar modelos do Ollama: {e}")
            return []

    def chat_stream(self, model_id: str, messages: List[Dict], options: Optional[Dict] = None) -> Generator[str, None, None]:
        """
        Envia uma requisição de chat para o Ollama e retorna a resposta em streaming.
        """
        if not self.is_server_reachable():
            yield "Erro: Servidor Ollama não está acessível."
            return

        # Validação de parâmetros
        if not model_id:
            yield "Erro: ID do modelo não especificado."
            return
            
        if not messages:
            yield "Erro: Nenhuma mensagem fornecida."
            return

        url = f"{self.host}/api/chat"
        
        # Preparar opções com valores padrão seguros
        opts = options or {}
        options_payload = {
            "temperature": max(0.0, min(2.0, opts.get("temperature", 0.7))),  # Limitar entre 0 e 2
            "top_p": max(0.0, min(1.0, opts.get("top_p", 0.9))),  # Limitar entre 0 e 1
            "top_k": max(1, opts.get("top_k", 40)),  # Valor mínimo de 1
            "num_predict": max(1, opts.get("max_tokens", 1024)),  # Valor mínimo de 1
            "repeat_penalty": max(0.0, opts.get("repeat_penalty", 1.1)),  # Limitar >= 0
            "presence_penalty": opts.get("presence_penalty", 0.0),
            "frequency_penalty": opts.get("frequency_penalty", 0.0),
        }
        
        # Remover opções None ou inválidas
        options_payload = {k: v for k, v in options_payload.items() if v is not None}

        payload = {
            "model": model_id,
            "messages": messages,
            "stream": True,
            "options": options_payload
        }

        try:
            # Aplica rate limiting
            self._rate_limit()
            
            # Envia uma mensagem de status antes de esperar pela resposta
            yield "Carregando modelo... "
            
            with requests.post(url, json=payload, stream=True, timeout=600) as response:
                response.raise_for_status()
                
                first_chunk = True
                content_buffer = ""
                
                for line in response.iter_lines():
                    if line:
                        try:
                            chunk = json.loads(line)
                            
                            # Verifica se há erro no chunk
                            if chunk.get("error"):
                                yield f"\rErro do Ollama: {chunk['error']}"
                                return
                                
                            content = chunk.get("message", {}).get("content", "")
                            
                            if content:
                                content_buffer += content
                                # Apenas yield quando temos conteúdo para enviar
                                yield content
                            
                            if chunk.get("done"):
                                break
                                
                        except json.JSONDecodeError as e:
                            logger.warning(f"Erro ao decodificar chunk JSON: {e}")
                            continue
                        except Exception as e:
                            logger.error(f"Erro ao processar chunk: {e}")
                            continue

        except requests.exceptions.ReadTimeout:
            yield f"\rErro: Tempo de espera excedido para o modelo '{model_id}'. Tente novamente."
        except requests.exceptions.ConnectionError:
            yield f"\rErro: Não foi possível conectar ao servidor Ollama em {self.host}. Verifique se o serviço está rodando."
        except requests.exceptions.RequestException as e:
            yield f"\rErro de comunicação com o Ollama: {e}"
        except Exception as e:
            logger.error(f"Erro inesperado ao processar resposta do Ollama: {e}")
            yield f"\rErro inesperado: {e}"

    def generate(self, model_id: str, prompt: str, options: Optional[Dict] = None) -> str:
        """
        Gera uma resposta completa (não streaming) a partir de um modelo.
        """
        if not self.is_server_reachable():
            return "Erro: Servidor Ollama não está acessível."
            
        if not model_id:
            return "Erro: ID do modelo não especificado."
            
        url = f"{self.host}/api/generate"
        
        # Preparar opções com valores padrão seguros
        opts = options or {}
        options_payload = {
            "temperature": max(0.0, min(2.0, opts.get("temperature", 0.7))),
            "top_p": max(0.0, min(1.0, opts.get("top_p", 0.9))),
            "top_k": max(1, opts.get("top_k", 40)),
            "num_predict": max(1, opts.get("max_tokens", 1024)),
            "repeat_penalty": max(0.0, opts.get("repeat_penalty", 1.1)),
        }
        
        # Remover opções None ou inválidas
        options_payload = {k: v for k, v in options_payload.items() if v is not None}

        payload = {
            "model": model_id,
            "prompt": prompt,
            "stream": False,
            "options": options_payload
        }

        try:
            # Aplica rate limiting
            self._rate_limit()
            
            response = requests.post(url, json=payload, timeout=600)
            response.raise_for_status()
            
            result = response.json()
            return result.get("response", "")
            
        except requests.exceptions.Timeout:
            return "Erro: Tempo de espera excedido."
        except requests.exceptions.RequestException as e:
            return f"Erro de comunicação com o Ollama: {e}"
        except json.JSONDecodeError as e:
            return f"Erro ao decodificar resposta do Ollama: {e}"
        except Exception as e:
            logger.error(f"Erro inesperado ao gerar resposta: {e}")
            return f"Erro inesperado: {e}"

    def pull_model(self, model_id: str) -> bool:
        """
        Baixa um modelo do Ollama (se necessário).
        """
        if not self.is_server_reachable():
            logger.error("Servidor Ollama não está acessível para baixar modelo.")
            return False
            
        if not model_id:
            logger.error("ID do modelo não especificado para download.")
            return False

        url = f"{self.host}/api/pull"
        payload = {"name": model_id}

        try:
            # Aplica rate limiting
            self._rate_limit()
            
            response = requests.post(url, json=payload, stream=True, timeout=3600)
            response.raise_for_status()
            
            # Processa o streaming de progresso
            for line in response.iter_lines():
                if line:
                    try:
                        chunk = json.loads(line)
                        if chunk.get("status") == "success":
                            logger.info(f"Modelo {model_id} baixado com sucesso.")
                            return True
                        elif chunk.get("status") == "error":
                            logger.error(f"Erro ao baixar modelo {model_id}: {chunk.get('error', 'Desconhecido')}")
                            return False
                    except json.JSONDecodeError:
                        continue
            
            return True  # Se não houve erro explícito
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao baixar modelo {model_id}: {e}")
            return False
        except Exception as e:
            logger.error(f"Erro inesperado ao baixar modelo {model_id}: {e}")
            return False

    def get_model_info(self, model_id: str) -> Dict:
        """
        Obtém informações detalhadas sobre um modelo específico.
        """
        if not self.is_server_reachable():
            return {"error": "Servidor Ollama não está acessível"}
            
        try:
            # Aplica rate limiting
            self._rate_limit()
            
            response = requests.get(f"{self.host}/api/show/{model_id}", timeout=10)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            return {"error": f"Erro ao buscar informações do modelo: {e}"}
        except json.JSONDecodeError as e:
            return {"error": f"Erro ao decodificar informações do modelo: {e}"}
        except Exception as e:
            return {"error": f"Erro inesperado ao buscar informações: {e}"}
