#!/usr/bin/env python3
"""
Script para baixar DialoGPT Small automaticamente
"""

import sys
import os
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def download_dialogpt():
    """Baixar DialoGPT Small"""
    
    print("=" * 50)
    print("    Download DialoGPT Small")
    print("=" * 50)
    
    try:
        from src.core.ollama_client import SevenXEngine
        from src.core.config import Config
        
        # Inicializar
        config = Config()
        engine = SevenXEngine(config.models_directory)
        
        print(f"📁 Diretório: {engine.models_dir}")
        print()
        
        # Verificar se já existe
        models = engine.list_models()
        for model in models:
            if "DialoGPT" in model.name:
                print(f"✅ {model.name} já está instalado!")
                return True
        
        print("📥 Baixando DialoGPT Small...")
        print("⏱️ Isso pode demorar alguns minutos...")
        print()
        
        def progress_callback(progress, status):
            print(f"📊 {progress}% - {status}")
        
        # Baixar modelo
        success = engine.download_model("microsoft/DialoGPT-small", progress_callback)
        
        if success:
            print()
            print("✅ DialoGPT Small baixado com sucesso!")
            print("🎉 Agora você pode usar o chat!")
            return True
        else:
            print("❌ Falha no download!")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = download_dialogpt()
    
    if success:
        print("\n🚀 Próximos passos:")
        print("1. Execute: python main.py")
        print("2. Vá para aba 'Chat'")
        print("3. Selecione 'DialoGPT Small'")
        print("4. Comece a conversar!")
    else:
        print("\n💡 Tente baixar manualmente:")
        print("1. Abra o SevenX Studio")
        print("2. Vá para aba 'Modelos'")
        print("3. Baixe 'DialoGPT Small'")
    
    input("\nPressione Enter para continuar...")