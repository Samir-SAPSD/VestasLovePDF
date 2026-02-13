@echo off
chcp 65001 >nul
echo ============================================================
echo   VestasLovePDF - Instalador
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
echo [1/4] Instalando dependências Python...
python -m pip install --user -r requirements.txt
if errorlevel 1 (
    echo [AVISO] Tentando instalação alternativa...
    python -m pip install --user flask pandas openpyxl pytesseract Pillow PyMuPDF python-docx
)

echo.
echo [2/4] Configurando Tesseract OCR...

:: Verifica se o Tesseract já está na pasta do projeto
set "LOCAL_TESSERACT=%~dp0..\tesseract\tesseract.exe"
if exist "%LOCAL_TESSERACT%" (
    echo [OK] Tesseract encontrado na pasta do projeto!
    goto :tesseract_ok
)

:: Verifica se o Tesseract está instalado no sistema
set "SYSTEM_TESSERACT=C:\Program Files\Tesseract-OCR\tesseract.exe"
if exist "%SYSTEM_TESSERACT%" (
    echo [INFO] Tesseract encontrado em: C:\Program Files\Tesseract-OCR
    echo.
    choice /C SN /M "Deseja copiar para a pasta do projeto (recomendado)"
    if errorlevel 2 goto :tesseract_skip
    
    echo Copiando arquivos do Tesseract...
    xcopy "C:\Program Files\Tesseract-OCR\*" "%~dp0..\tesseract\" /E /I /Q /Y
    echo [OK] Tesseract copiado com sucesso!
    goto :tesseract_ok
)

:: Verifica em Program Files (x86)
set "SYSTEM_TESSERACT_X86=C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"
if exist "%SYSTEM_TESSERACT_X86%" (
    echo [INFO] Tesseract encontrado em: C:\Program Files (x86)\Tesseract-OCR
    echo.
    choice /C SN /M "Deseja copiar para a pasta do projeto (recomendado)"
    if errorlevel 2 goto :tesseract_skip
    
    echo Copiando arquivos do Tesseract...
    xcopy "C:\Program Files (x86)\Tesseract-OCR\*" "%~dp0..\tesseract\" /E /I /Q /Y
    echo [OK] Tesseract copiado com sucesso!
    goto :tesseract_ok
)

:tesseract_not_found
echo.
echo ============================================================
echo   [INFO] Tesseract OCR não encontrado
echo ============================================================
echo.
echo   Para usar a funcionalidade de OCR:
echo.
echo   1. Baixe em: https://github.com/UB-Mannheim/tesseract/wiki
echo   2. Execute o instalador e marque: Portuguese, English
echo   3. Após instalar, copie o conteúdo de:
echo      C:\Program Files\Tesseract-OCR
echo   4. Para a pasta:
echo      %~dp0..\tesseract\
echo.
echo   A funcionalidade OCR ficará desabilitada até a configuração.
echo ============================================================
echo.
goto :tesseract_end

:tesseract_skip
echo [INFO] Tesseract não foi copiado. OCR usará instalação do sistema.
goto :tesseract_end

:tesseract_ok
echo.

:tesseract_end

echo.
echo [3/4] Criando atalho na área de trabalho...

:: Cria o atalho usando PowerShell
powershell -ExecutionPolicy Bypass -File "%~dp0create_shortcut.ps1"

echo.
echo [4/4] Instalação concluída!
echo.
echo ============================================================
echo   O VestasLovePDF foi instalado com sucesso!
echo   Um atalho foi criado na sua área de trabalho.
echo   O programa será executado em modo silencioso (sem terminal).
echo ============================================================
echo.
pause
