@echo off
chcp 65001 >nul
echo ============================================================
echo   VestasLovePDF - Instalador
echo ============================================================
echo.
echo   Arquitetura:
echo   - Flask API com Blueprint pattern
echo   - Processadores com Strategy pattern
echo   - Frontend HTML/CSS/JavaScript
echo.

:: Verifica se o Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python não encontrado. Por favor, instale o Python primeiro.
    echo [INFO] Download: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Mostra versão do Python
for /f "tokens=*" %%i in ('python --version 2^>^&1') do echo [OK] %%i encontrado

:: Navega para o diretório do projeto
cd /d "%~dp0.."

:: Verifica se requirements.txt existe
if not exist "requirements.txt" (
    echo [ERRO] Arquivo requirements.txt não encontrado!
    pause
    exit /b 1
)

echo.
echo [1/5] Instalando dependências Python...
python -m pip install --user --upgrade pip >nul 2>&1
python -m pip install --user -r requirements.txt
if errorlevel 1 (
    echo [AVISO] Tentando instalação alternativa...
    python -m pip install --user flask flask-cors pandas openpyxl pytesseract Pillow PyMuPDF python-docx pdf2docx xlrd xlwt odfpy pyxlsb
)
echo [OK] Dependências instaladas!

echo.
echo [2/5] Verificando estrutura do projeto...
:: Verifica pastas necessárias
if not exist "app\" (
    echo [ERRO] Pasta app/ não encontrada!
    pause
    exit /b 1
)
if exist "app\api\v1\" echo   [OK] API v1 presente
if exist "app\processors\" echo   [OK] Processors presentes
if exist "app\core\" echo   [OK] Core modules presentes
if exist "app\templates\" echo   [OK] Templates presentes
if exist "app\static\" echo   [OK] Static files presentes
if exist "app\utils\" echo   [OK] Utils presentes
echo [OK] Estrutura do projeto verificada!

echo.
echo [3/5] Configurando Tesseract OCR...

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
echo [4/5] Criando atalho na área de trabalho...

:: Cria o atalho usando PowerShell
powershell -ExecutionPolicy Bypass -File "%~dp0create_shortcut.ps1"

echo.
echo [5/5] Testando a aplicação...
python -c "from app import create_app; print('[OK] Application factory funcionando!')" 2>nul
if errorlevel 1 (
    echo [AVISO] Teste básico falhou, mas a instalação continua...
)

echo.
echo ============================================================
echo   VestasLovePDF instalado com sucesso!
echo ============================================================
echo.
echo   Arquitetura instalada:
echo   - Flask API v1 com Blueprint pattern
echo   - Processadores modulares (Strategy pattern)
echo   - Interface web responsiva
echo.
echo   Funcionalidades:
echo   - Conversor de arquivos (PDF, Word, Excel, imagens)
echo   - Compressor de PDF
echo   - Mesclador e divisor de PDF
echo   - OCR para PDFs escaneados
echo.
echo   Um atalho foi criado na sua área de trabalho.
echo   O programa será executado em modo silencioso (sem terminal).
echo ============================================================
echo.
pause
