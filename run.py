#!/usr/bin/env python3
"""
Script de execução do SevenX Studio
"""

import sys
import os

# Adicionar o diretório atual ao path
sys.path.insert(0, os.path.dirname(__file__))

# Importar e executar a aplicação principal
from main import main

if __name__ == "__main__":
    main()