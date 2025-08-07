#!/usr/bin/env python3
"""
Teste simples para verificar carregamento de modelo
"""

import sys
import os
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_simple_load():
    """Teste simples de carregamento"""
    
    print("🔍 Teste Simples de Carregamento")
    print("=" * 40)
    
    try:
        # Importar módulos
        print("📦 Importando módulos...")
        from src.core.sevenx_engine import SevenXEngine
        from src.core.config import Config
        print("✅ Módulos importados")
        
        # Criar configuração
        print("⚙️ Criando configuração...")
        config = Config()
        print(f"✅ Config criado: {config.models_directory}")
        
        # Criar engine
        print("🚀 Criando engine...")
        engine = SevenXEngine(config.models_directory)
        print(f"✅ Engine criado: {engine.device}")
        
        # Verificar se está disponível
        print("🔍 Verificando disponibilidade...")
        available = engine.is_available()
        print(f"✅ Disponível: {available}")
        
        # Listar modelos
        print("📋 Listando modelos...")
        models = engine.list_models()
        print(f"✅ Encontrados {len(models)} modelos")
        
        if not models:
            print("⚠️ Nenhum modelo encontrado!")
            print("💡 Baixe DialoGPT Small primeiro")
            return
        
        # Mostrar modelos
        for i, model in enumerate(models):
            print(f"   {i+1}. {model.name} ({model.size / (1024*1024):.1f} MB)")
        
        # Testar carregamento do primeiro modelo
        model_name = models[0].name
        print(f"\n🔄 Testando carregamento: {model_name}")
        
        success = engine.load_model(model_name)
        
        if success:
            print("✅ Modelo carregado com sucesso!")
            
            # Teste simples de geração
            print("🧪 Teste simples de geração...")
            try:
                response = engine.generate_response(
                    model_name, 
                    "Olá", 
                    {"temperature": 0.7, "max_tokens": 50}
                )
                print(f"📝 Resposta: {response[:100]}...")
                
                if len(response) > 5 and "erro" not in response.lower():
                    print("✅ Geração funcionando!")
                else:
                    print("⚠️ Resposta suspeita")
                    
            except Exception as e:
                print(f"❌ Erro na geração: {e}")
        else:
            print("❌ Falha ao carregar modelo!")
            
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple_load()
    input("\nPressione Enter para continuar...")