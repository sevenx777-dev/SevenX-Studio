#!/usr/bin/env python3
"""
Teste específico para carregamento de modelos
"""

import sys
import os
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.ollama_client import SevenXEngine
from src.core.config import Config

def test_models():
    """Testar carregamento de modelos"""
    
    print("=" * 50)
    print("    Teste de Carregamento de Modelos")
    print("=" * 50)
    
    # Inicializar configuração
    config = Config()
    
    # Inicializar engine
    engine = SevenXEngine(config.models_directory)
    
    print(f"Diretório de modelos: {engine.models_dir}")
    print(f"Device: {engine.device}")
    print()
    
    # Listar modelos instalados
    print("Modelos instalados:")
    models = engine.list_models()
    
    if not models:
        print("❌ Nenhum modelo encontrado!")
        return
    
    for i, model in enumerate(models):
        print(f"{i+1}. {model.name}")
        print(f"   Tamanho: {model.size / (1024*1024):.1f} MB")
        print(f"   Caminho: {model.path}")
        print()
    
    # Testar carregamento do primeiro modelo
    if models:
        model_name = models[0].name
        print(f"Testando carregamento do modelo: {model_name}")
        print("-" * 30)
        
        success = engine.load_model(model_name)
        
        if success:
            print("✅ Modelo carregado com sucesso!")
            
            # Testar geração
            print("\nTestando geração de resposta...")
            prompt = "Olá, como você está?"
            response = engine.generate_response(model_name, prompt)
            
            print(f"Prompt: {prompt}")
            print(f"Resposta: {response}")
            
        else:
            print("❌ Falha ao carregar modelo!")
    
    print("\nModelos carregados na memória:")
    for name in engine.loaded_models.keys():
        print(f"✅ {name}")

if __name__ == "__main__":
    test_models()
    input("\nPressione Enter para continuar...")