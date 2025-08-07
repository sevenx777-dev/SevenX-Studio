#!/usr/bin/env python3
"""
Teste otimizado para chat com parâmetros melhorados
"""

import sys
import os
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.sevenx_engine import SevenXEngine
from src.core.config import Config

def test_optimized_chat():
    """Testar chat com parâmetros otimizados"""
    
    print("=" * 60)
    print("    Teste de Chat Otimizado - SevenX Studio")
    print("=" * 60)
    
    try:
        # Inicializar
        config = Config()
        engine = SevenXEngine(config.models_directory)
        
        print(f"📁 Diretório de modelos: {engine.models_dir}")
        print(f"💻 Device: {engine.device}")
        print()
        
        # Listar modelos
        models = engine.list_models()
        if not models:
            print("❌ Nenhum modelo encontrado!")
            print("💡 Vá para a aba 'Modelos' e baixe DialoGPT Small primeiro")
            return
        
        model_name = models[0].name
        print(f"🤖 Usando modelo: {model_name}")
        print(f"📊 Tamanho: {models[0].size / (1024*1024):.1f} MB")
        print()
        
        # Testar carregamento do modelo primeiro
        print("🔄 Testando carregamento do modelo...")
        if not engine.load_model(model_name):
            print("❌ Falha ao carregar modelo!")
            return
        
        print("✅ Modelo carregado com sucesso!")
        print()
        
    except Exception as e:
        print(f"❌ Erro na inicialização: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Parâmetros otimizados
    optimized_options = {
        "temperature": 0.8,      # Mais criativo
        "max_tokens": 200,       # Mais tokens
        "top_p": 0.95,          # Mais diversidade
    }
    
    # Testes com diferentes prompts
    test_prompts = [
        "Olá, como você está?",
        "Conte-me uma piada",
        "Qual é a capital do Brasil?",
        "Explique o que é inteligência artificial",
        "Como posso aprender programação?"
    ]
    
    print("🧪 Testando com parâmetros otimizados:")
    print(f"   Temperature: {optimized_options['temperature']}")
    print(f"   Max Tokens: {optimized_options['max_tokens']}")
    print(f"   Top P: {optimized_options['top_p']}")
    print()
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"📝 Teste {i}/5")
        print(f"Pergunta: {prompt}")
        print("-" * 40)
        
        try:
            # Gerar resposta
            messages = [{"role": "user", "content": prompt}]
            result = engine.chat(model_name, messages, optimized_options)
            
            if "error" in result:
                print(f"❌ Erro: {result['error']}")
            else:
                response = result.get("message", {}).get("content", "Sem resposta")
                print(f"Resposta: {response}")
                
                # Análise da resposta
                if len(response) < 10:
                    print("⚠️  Resposta muito curta")
                elif "phonophon" in response.lower() or len(set(response.split())) < 3:
                    print("⚠️  Possível delírio detectado")
                else:
                    print("✅ Resposta parece boa")
        
        except Exception as e:
            print(f"❌ Erro: {e}")
        
        print()
        print("=" * 60)
        print()
    
    print("🎯 Teste concluído!")
    print()
    print("💡 Dicas para melhorar:")
    print("- Se respostas muito curtas: Aumente max_tokens")
    print("- Se muito repetitivo: Aumente temperature")
    print("- Se sem sentido: Diminua temperature")
    print("- Use DialoGPT Small para melhor conversação")

if __name__ == "__main__":
    test_optimized_chat()
    input("\nPressione Enter para continuar...")