"""
Configurações para build do SevenX Studio
"""

# Configurações do PyInstaller
PYINSTALLER_OPTIONS = {
    'name': 'SevenX Studio',
    'onefile': True,
    'windowed': True,  # Sem console
    'icon': 'assets/icon.ico',
    'add_data': [
        ('src', 'src'),
    ],
    'hidden_imports': [
        'torch',
        'transformers', 
        'huggingface_hub',
        'tokenizers',
        'PyQt6',
        'PyQt6.QtCore',
        'PyQt6.QtWidgets',
        'PyQt6.QtGui',
        'requests',
        'psutil',
        'numpy',
        'json',
        'pathlib',
        'datetime',
        'threading',
        'asyncio',
        'logging',
        'sqlite3',
    ],
    'collect_all': [
        'transformers',
        'tokenizers',
    ],
    'excludes': [
        'matplotlib',
        'scipy',
        'pandas',
        'jupyter',
        'notebook',
        'IPython',
        'tkinter',
    ],
    'optimize': 2,  # Otimização máxima
}

# Informações da aplicação
APP_INFO = {
    'name': 'SevenX Studio',
    'version': '1.0.0',
    'description': 'Local AI Model Management Platform',
    'author': 'SevenX Team',
    'copyright': '© 2024 SevenX Studio',
}

# Arquivos para incluir na distribuição
DIST_FILES = [
    'README.md',
    'LICENSE', 
    'INSTALL.md',
    'CHANGELOG.md',
]

# Configurações de otimização
OPTIMIZATION = {
    'upx': True,  # Compressão UPX
    'strip': True,  # Remover símbolos de debug
    'exclude_modules': [
        'test',
        'tests',
        'unittest',
        'doctest',
        'pdb',
        'pydoc',
    ]
}