"""
Testes para o motor de IA
"""

import pytest
import tempfile
from pathlib import Path
import sys
import os

# Adicionar src ao path para imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.core.ollama_client import SevenXEngine, ModelInfo


def test_engine_creation():
    """Testar criação do motor de IA"""
    with tempfile.TemporaryDirectory() as temp_dir:
        engine = SevenXEngine(Path(temp_dir))
        assert engine is not None
        assert engine.models_dir.exists()


def test_engine_device_detection():
    """Testar detecção de device"""
    with tempfile.TemporaryDirectory() as temp_dir:
        engine = SevenXEngine(Path(temp_dir))
        assert engine.device in ['cpu', 'cuda']


def test_engine_is_available():
    """Testar se o motor está disponível"""
    with tempfile.TemporaryDirectory() as temp_dir:
        engine = SevenXEngine(Path(temp_dir))
        # Deve estar disponível se PyTorch funcionar
        available = engine.is_available()
        assert isinstance(available, bool)


def test_engine_list_models_empty():
    """Testar listagem de modelos vazia"""
    with tempfile.TemporaryDirectory() as temp_dir:
        engine = SevenXEngine(Path(temp_dir))
        models = engine.list_models()
        assert isinstance(models, list)
        assert len(models) == 0


def test_engine_get_available_models():
    """Testar obtenção de modelos disponíveis"""
    with tempfile.TemporaryDirectory() as temp_dir:
        engine = SevenXEngine(Path(temp_dir))
        available = engine.get_available_models()
        assert isinstance(available, list)
        assert len(available) > 0
        
        # Verificar estrutura do primeiro modelo
        if available:
            model = available[0]
            assert 'id' in model
            assert 'name' in model
            assert 'description' in model


def test_engine_model_directory_mapping():
    """Testar mapeamento de diretórios de modelos"""
    with tempfile.TemporaryDirectory() as temp_dir:
        engine = SevenXEngine(Path(temp_dir))
        
        # Testar mapeamentos conhecidos
        assert engine._get_model_directory_name("DialoGPT Small") == "microsoft_DialoGPT-small"
        assert engine._get_model_directory_name("GPT-2") == "gpt2"


def test_engine_display_name_mapping():
    """Testar mapeamento de nomes de exibição"""
    with tempfile.TemporaryDirectory() as temp_dir:
        engine = SevenXEngine(Path(temp_dir))
        
        # Testar mapeamentos reversos
        assert engine._get_display_name_from_directory("microsoft_DialoGPT-small") == "DialoGPT Small"
        assert engine._get_display_name_from_directory("gpt2") == "GPT-2"


def test_engine_system_info():
    """Testar informações do sistema"""
    with tempfile.TemporaryDirectory() as temp_dir:
        engine = SevenXEngine(Path(temp_dir))
        info = engine.get_system_info()
        
        assert isinstance(info, dict)
        assert 'device' in info
        assert 'cuda_available' in info
        assert 'loaded_models' in info
        assert 'models_directory' in info


@pytest.mark.skipif(not os.environ.get('RUN_SLOW_TESTS'), reason="Teste lento - requer download")
def test_engine_load_nonexistent_model():
    """Testar carregamento de modelo inexistente"""
    with tempfile.TemporaryDirectory() as temp_dir:
        engine = SevenXEngine(Path(temp_dir))
        result = engine.load_model("nonexistent_model")
        assert result is False


def test_model_info_creation():
    """Testar criação de ModelInfo"""
    model = ModelInfo(
        name="Test Model",
        size=1000,
        path="/test/path",
        modified_at="2025-01-01",
        details={},
        status="available"
    )
    
    assert model.name == "Test Model"
    assert model.size == 1000
    assert model.status == "available"