#!/usr/bin/env python3
"""
Script avançado para build do SevenX Studio
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def run_command(cmd, description=""):
    """Executar comando e mostrar resultado"""
    print(f"\n🔄 {description}")
    print(f"Executando: {cmd}")
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ {description} - Sucesso")
        if result.stdout:
            print(result.stdout)
    else:
        print(f"❌ {description} - Erro")
        if result.stderr:
            print(result.stderr)
        return False
    
    return True

def create_build():
    """Criar build do executável"""
    
    print("=" * 50)
    print("    SevenX Studio - Build Avançado")
    print("=" * 50)
    
    # 1. Verificar ambiente virtual
    if not Path("venv").exists():
        print("❌ Ambiente virtual não encontrado!")
        print("Execute install.bat primeiro.")
        return False
    
    # 2. Ativar ambiente virtual
    if os.name == 'nt':  # Windows
        activate_cmd = "venv\\Scripts\\activate.bat &&"
    else:  # Linux/macOS
        activate_cmd = "source venv/bin/activate &&"
    
    # 3. Instalar PyInstaller
    if not run_command(f"{activate_cmd} pip install pyinstaller", "Instalando PyInstaller"):
        return False
    
    # 4. Criar ícone
    print("\n🎨 Criando ícone...")
    try:
        exec(open("create_icon.py").read())
    except Exception as e:
        print(f"⚠️ Erro ao criar ícone: {e}")
        print("Continuando sem ícone personalizado...")
    
    # 5. Limpar builds anteriores
    print("\n🧹 Limpando builds anteriores...")
    for folder in ["build", "dist"]:
        if Path(folder).exists():
            shutil.rmtree(folder)
            print(f"Removido: {folder}")
    
    # Remover arquivos .spec antigos
    for spec_file in Path(".").glob("*.spec"):
        spec_file.unlink()
        print(f"Removido: {spec_file}")
    
    # 6. Criar executável
    pyinstaller_cmd = f"""
    {activate_cmd} pyinstaller 
    --onefile 
    --windowed 
    --name "SevenX Studio"
    --add-data "src{os.pathsep}src"
    --hidden-import=torch
    --hidden-import=transformers
    --hidden-import=huggingface_hub
    --hidden-import=tokenizers
    --hidden-import=PyQt6
    --hidden-import=PyQt6.QtCore
    --hidden-import=PyQt6.QtWidgets
    --hidden-import=PyQt6.QtGui
    --hidden-import=requests
    --hidden-import=psutil
    --hidden-import=numpy
    --collect-all=transformers
    --collect-all=tokenizers
    --distpath=dist
    --workpath=build
    main.py
    """.replace('\n', ' ').strip()
    
    # Adicionar ícone se existir
    if Path("assets/icon.ico").exists():
        pyinstaller_cmd += " --icon=assets/icon.ico"
    
    if not run_command(pyinstaller_cmd, "Criando executável"):
        return False
    
    # 7. Verificar resultado
    exe_path = Path("dist") / "SevenX Studio.exe"
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"\n✅ Build concluído com sucesso!")
        print(f"📁 Executável: {exe_path}")
        print(f"📊 Tamanho: {size_mb:.1f} MB")
        
        # 8. Criar pasta de distribuição
        dist_folder = Path("SevenX_Studio_Portable")
        if dist_folder.exists():
            shutil.rmtree(dist_folder)
        
        dist_folder.mkdir()
        
        # Copiar executável
        shutil.copy2(exe_path, dist_folder / "SevenX Studio.exe")
        
        # Copiar arquivos importantes
        files_to_copy = ["README.md", "LICENSE", "INSTALL.md", "CHANGELOG.md"]
        for file in files_to_copy:
            if Path(file).exists():
                shutil.copy2(file, dist_folder)
        
        # Criar arquivo de informações
        with open(dist_folder / "INFO.txt", "w", encoding="utf-8") as f:
            f.write("""SevenX Studio - Versão Portátil

🚀 Como usar:
1. Execute "SevenX Studio.exe"
2. Vá para aba "Modelos"
3. Baixe um modelo (ex: DialoGPT-small)
4. Vá para aba "Chat" e comece a conversar!

📋 Requisitos:
- Windows 10/11
- 4GB+ RAM
- Conexão com internet (para download de modelos)

🆘 Suporte:
- Leia README.md para mais informações
- Veja INSTALL.md para troubleshooting

Versão: 1.0.0
Build: {Path.cwd().name}
""")
        
        print(f"📦 Pasta portátil criada: {dist_folder}")
        return True
    
    else:
        print("❌ Executável não foi criado!")
        return False

if __name__ == "__main__":
    success = create_build()
    
    if success:
        print("\n🎉 Build concluído com sucesso!")
        print("Execute o arquivo em dist/SevenX Studio.exe")
    else:
        print("\n💥 Build falhou!")
        print("Verifique os erros acima.")
    
    input("\nPressione Enter para continuar...")