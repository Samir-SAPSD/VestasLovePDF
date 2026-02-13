# -*- coding: utf-8 -*-
"""
Script para criar o executável do VestasLovePDF usando PyInstaller.
Execute este script para gerar o instalador.
"""
import subprocess
import sys
import os
import shutil

def main():
    # Diretório base do projeto
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(base_dir)
    
    print("=" * 60)
    print("  VestasLovePDF - Build do Executável")
    print("=" * 60)
    
    # Instalar dependências
    print("\n[1/4] Instalando dependências...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
    
    # Limpar builds anteriores
    print("\n[2/4] Limpando builds anteriores...")
    for folder in ["build", "dist"]:
        if os.path.exists(folder):
            shutil.rmtree(folder)
    
    # Criar executável com PyInstaller
    print("\n[3/4] Criando executável...")
    
    pyinstaller_args = [
        sys.executable, "-m", "PyInstaller",
        "--name=VestasLovePDF",
        "--onefile",
        "--windowed",  # Sem console (modo silencioso)
        "--add-data", f"app/templates;app/templates",
        "--add-data", f"app/static;app/static" if os.path.exists("app/static") else "",
        "--hidden-import=flask",
        "--hidden-import=pandas",
        "--hidden-import=openpyxl",
        "--hidden-import=jinja2",
        "--hidden-import=werkzeug",
        "--hidden-import=pytesseract",
        "--hidden-import=PIL",
        "--hidden-import=fitz",
        "--hidden-import=docx",
        "--collect-submodules=flask",
        "--collect-submodules=jinja2",
        "--collect-submodules=werkzeug",
        "--collect-submodules=PIL",
        "--collect-submodules=fitz",
        "run.py"
    ]
    
    # Remover argumentos vazios
    pyinstaller_args = [arg for arg in pyinstaller_args if arg]
    
    subprocess.run(pyinstaller_args, check=True)
    
    # Criar atalho
    print("\n[4/4] Criando atalho na área de trabalho...")
    create_shortcut()
    
    print("\n" + "=" * 60)
    print("  Build concluído com sucesso!")
    print("  Executável: dist/VestasLovePDF.exe")
    print("=" * 60)

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
