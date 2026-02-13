# -*- coding: utf-8 -*-
"""
Script para executar o VestasLovePDF em modo silencioso (sem janela do terminal).
Use a extensão .pyw para que o Python execute sem console.
"""
import sys
import os

# Adiciona o diretório do script ao path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

from app.main import run_app

if __name__ == '__main__':
    run_app()
