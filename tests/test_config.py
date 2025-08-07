"""
Testes para o módulo de configuração
"""

import pytest
import tempfile
from pathlib import Path
import sys
import os

# Adicionar src ao path para imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.core.config import Config


def test_config_creation():
    """Testar criação de configuração"""
    config = Config()
    assert config is not None
    assert hasattr(config, 'settings')


def test_config_default_values():
    """Testar valores padrão da configuração"""
    config = Config()
    assert config.get('theme') == 'dark'
    assert config.get('language') == 'pt-BR'
    assert config.get('chat_settings.temperature') == 0.7


def test_config_set_get():
    """Testar set e get de configurações"""
    config = Config()
    
    # Testar set/get simples
    config.set('test_key', 'test_value')
    assert config.get('test_key') == 'test_value'
    
    # Testar set/get aninhado
    config.set('nested.key', 'nested_value')
    assert config.get('nested.key') == 'nested_value'


def test_config_directories():
    """Testar criação de diretórios"""
    config = Config()
    
    # Verificar se diretórios são criados
    assert config.config_dir.exists()
    assert config.models_dir.exists()
    assert config.logs_dir.exists()


def test_config_models_directory_property():
    """Testar propriedade models_directory"""
    config = Config()
    models_dir = config.models_directory
    assert isinstance(models_dir, Path)
    assert models_dir.exists()


def test_config_theme_property():
    """Testar propriedade theme"""
    config = Config()
    assert config.theme in ['dark', 'light']


def test_config_ollama_host_property():
    """Testar propriedade ollama_host"""
    config = Config()
    host = config.ollama_host
    assert isinstance(host, str)
    assert host.startswith('http')