# -*- coding: utf-8 -*-
"""
Script para criar o executável do VestasLovePDF usando PyInstaller.

Arquitetura do Projeto:
    - app/__init__.py: Application factory (create_app)
    - app/api/v1/: API endpoints (Blueprint pattern)
    - app/processors/: File processors (Strategy pattern)
    - app/core/: Core utilities (response, exceptions, middleware)
    - app/utils/: Legacy utility functions
    - app/static/: CSS e JavaScript
    - app/templates/: HTML templates

Execute: python setup/build_exe.py
"""
import subprocess
import sys
import os
import shutil


def check_requirements():
    """Verifica se o PyInstaller está instalado."""
    try:
        import PyInstaller
        return True
    except ImportError:
        return False


def main():
    # Diretório base do projeto
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(base_dir)
    
    print("=" * 60)
    print("  VestasLovePDF - Build do Executável")
    print("=" * 60)
    
    # Instalar dependências
    print("\n[1/5] Instalando dependências...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
    
    # Verificar PyInstaller
    if not check_requirements():
        print("[INFO] Instalando PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
    
    # Limpar builds anteriores
    print("\n[2/5] Limpando builds anteriores...")
    for folder in ["build", "dist"]:
        if os.path.exists(folder):
            shutil.rmtree(folder)
    
    # Remover arquivo .spec antigo
    spec_file = "VestasLovePDF.spec"
    if os.path.exists(spec_file):
        os.remove(spec_file)
    
    # Criar executável com PyInstaller
    print("\n[3/5] Criando executável...")
    
    # Construir lista de argumentos
    pyinstaller_args = [
        sys.executable, "-m", "PyInstaller",
        "--name=VestasLovePDF",
        "--onefile",
        "--windowed",  # Sem console (modo silencioso)
        
        # Adicionar arquivos estáticos e templates
        "--add-data", "app/templates;app/templates",
        "--add-data", "app/static;app/static",
        
        # Flask e extensões
        "--hidden-import=flask",
        "--hidden-import=flask_cors",
        "--hidden-import=jinja2",
        "--hidden-import=werkzeug",
        "--hidden-import=werkzeug.security",
        "--hidden-import=werkzeug.datastructures",
        
        # API e Core (nova arquitetura)
        "--hidden-import=app",
        "--hidden-import=app.main",
        "--hidden-import=app.config",
        "--hidden-import=app.api",
        "--hidden-import=app.api.v1",
        "--hidden-import=app.api.v1.compressor",
        "--hidden-import=app.api.v1.converter",
        "--hidden-import=app.api.v1.pdf_tools",
        "--hidden-import=app.api.v1.ocr",
        "--hidden-import=app.core",
        "--hidden-import=app.core.response",
        "--hidden-import=app.core.exceptions",
        "--hidden-import=app.core.middleware",
        "--hidden-import=app.processors",
        "--hidden-import=app.processors.base",
        "--hidden-import=app.processors.compressor",
        "--hidden-import=app.processors.converter",
        "--hidden-import=app.processors.pdf_tools",
        "--hidden-import=app.processors.ocr",
        
        # Utils (legacy)
        "--hidden-import=app.utils",
        "--hidden-import=app.utils.converters",
        "--hidden-import=app.utils.compressor",
        "--hidden-import=app.utils.pdf_merger",
        "--hidden-import=app.utils.ocr_pdf",
        
        # Processamento de arquivos
        "--hidden-import=pandas",
        "--hidden-import=openpyxl",
        "--hidden-import=xlrd",
        "--hidden-import=xlwt",
        "--hidden-import=odfpy",
        "--hidden-import=pyxlsb",
        "--hidden-import=pytesseract",
        "--hidden-import=PIL",
        "--hidden-import=PIL.Image",
        "--hidden-import=fitz",
        "--hidden-import=docx",
        "--hidden-import=pdf2docx",
        
        # Coletar submodules
        "--collect-submodules=flask",
        "--collect-submodules=flask_cors",
        "--collect-submodules=jinja2",
        "--collect-submodules=werkzeug",
        "--collect-submodules=PIL",
        "--collect-submodules=fitz",
        "--collect-submodules=pandas",
        "--collect-submodules=openpyxl",
        
        # Entry point
        "run.py"
    ]
    
    # Verificar se pasta static existe
    if not os.path.exists("app/static"):
        pyinstaller_args = [arg for arg in pyinstaller_args if "app/static" not in arg]
    
    subprocess.run(pyinstaller_args, check=True)
    
    # Copiar Tesseract se existir
    print("\n[4/5] Verificando Tesseract OCR...")
    copy_tesseract(base_dir)
    
    # Criar atalho
    print("\n[5/5] Criando atalho na área de trabalho...")
    create_shortcut()
    
    print("\n" + "=" * 60)
    print("  Build concluído com sucesso!")
    print("  Executável: dist/VestasLovePDF.exe")
    print("=" * 60)


def copy_tesseract(base_dir):
    """Copia Tesseract para a pasta dist se disponível."""
    tesseract_src = os.path.join(base_dir, "tesseract")
    tesseract_dst = os.path.join(base_dir, "dist", "tesseract")
    
    if os.path.exists(tesseract_src) and os.path.exists(os.path.join(tesseract_src, "tesseract.exe")):
        print("  Copiando Tesseract para dist...")
        shutil.copytree(tesseract_src, tesseract_dst)
        print("  [OK] Tesseract copiado!")
    else:
        print("  [INFO] Tesseract não encontrado na pasta do projeto.")
        print("  [INFO] Para incluir OCR, copie o Tesseract para a pasta 'tesseract/'.")

def create_shortcut():
    """Cria um atalho na área de trabalho para o executável."""
    try:
        import winreg
        
        # Obtém o caminho da área de trabalho
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders"
        )
        desktop = winreg.QueryValueEx(key, "Desktop")[0]
        winreg.CloseKey(key)
        
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        exe_path = os.path.join(base_dir, "dist", "VestasLovePDF.exe")
        shortcut_path = os.path.join(desktop, "VestasLovePDF.lnk")
        
        # Usa PowerShell para criar o atalho
        ps_script = f'''
        $WshShell = New-Object -ComObject WScript.Shell
        $Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
        $Shortcut.TargetPath = "{exe_path}"
        $Shortcut.WorkingDirectory = "{os.path.dirname(exe_path)}"
        $Shortcut.Description = "VestasLovePDF - Ferramenta de PDF e Conversão de Arquivos"
        $Shortcut.Save()
        '''
        
        subprocess.run(["powershell", "-Command", ps_script], check=True)
        print(f"  Atalho criado: {shortcut_path}")
        
    except Exception as e:
        print(f"  Aviso: Não foi possível criar o atalho automaticamente: {e}")

if __name__ == "__main__":
    main()
