@echo off
chcp 65001 >nul
echo ============================================================
echo   Converter - Instalador
echo ============================================================
echo.

:: Verifica se o Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python não encontrado. Por favor, instale o Python primeiro.
    pause
    exit /b 1
)

:: Navega para o diretório do projeto
cd /d "%~dp0.."

:: Instala as dependências (usando --user para evitar problemas de permissão)
echo [1/3] Instalando dependências...
python -m pip install --user -r requirements.txt
if errorlevel 1 (
    echo [AVISO] Tentando instalação alternativa...
    python -m pip install --user flask pandas openpyxl
)

echo.
echo [2/3] Criando atalho na área de trabalho...

:: Cria o atalho usando PowerShell
powershell -ExecutionPolicy Bypass -File "%~dp0create_shortcut.ps1"

echo.
echo [3/3] Instalação concluída!
echo.
echo ============================================================
echo   O Converter foi instalado com sucesso!
echo   Um atalho foi criado na sua área de trabalho.
echo   O programa será executado em modo silencioso (sem terminal).
echo ============================================================
echo.
pause
