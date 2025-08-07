"""
Arquivo: ollama_client.py
Descrição: Cliente para interagir com a API do Ollama.
"""

import requests
import json
from typing import List, Dict, Generator, Optional

from .config import Config

class OllamaClient:
    """
    Cliente para listar modelos e gerar respostas em streaming
    a partir de um servidor Ollama.
    """
    def __init__(self, config: Config):
        self.config = config
        self.host = self.config.get("ollama_host", "http://localhost:11434")

    def is_server_reachable(self) -> bool:
        """Verifica se o servidor Ollama está acessível."""
        try:
            response = requests.get(self.host, timeout=2)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def list_models(self) -> List[Dict]:
        """Busca a lista de modelos disponíveis no servidor Ollama."""
        if not self.is_server_reachable():
            print("Servidor Ollama não está acessível.")
            return []
        
        try:
            response = requests.get(f"{self.host}/api/tags")
            response.raise_for_status()
            models_data = response.json().get("models", [])
            return [{"id": model["name"], "name": model["name"]} for model in models_data]
        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar modelos do Ollama: {e}")
            return []

    def chat_stream(self, model_id: str, messages: List[Dict], options: Optional[Dict] = None) -> Generator[str, None, None]:
        """
        Envia uma requisição de chat para o Ollama e retorna a resposta em streaming.
        """
        if not self.is_server_reachable():
            yield "Erro: Servidor Ollama não está acessível."
            return

        url = f"{self.host}/api/chat"
        payload = {
            "model": model_id,
            "messages": messages,
            "stream": True,
            "options": {
                "temperature": options.get("temperature", 0.7),
                "top_p": options.get("top_p", 0.9),
                "top_k": options.get("top_k", 40),
                "num_predict": options.get("max_tokens", 1024)
            }
        }

        try:
            # **MELHORIA**: Envia uma mensagem de status antes de esperar pela resposta.
            yield "A carregar o modelo, por favor aguarde... "
            
            with requests.post(url, json=payload, stream=True, timeout=600) as response:
                response.raise_for_status()
                
                first_chunk = True
                for line in response.iter_lines():
                    if line:
                        chunk = json.loads(line)
                        content = chunk.get("message", {}).get("content", "")
                        
                        # Limpa a mensagem de "A carregar..." no primeiro pedaço de texto real
                        if first_chunk:
                            yield f"\r{content}" # O '\r' ajuda a limpar a linha anterior em alguns terminais
                            first_chunk = False
                        else:
                            yield content
                        
                        if chunk.get("done"):
                            break

        except requests.exceptions.ReadTimeout:
            yield f"\rErro: O tempo de espera para carregar o modelo '{model_id}' expirou. Tente novamente."
        except requests.exceptions.RequestException as e:
            yield f"\rErro de comunicação com o Ollama: {e}"
        except Exception as e:
            yield f"\rErro inesperado ao processar resposta do Ollama: {e}"
