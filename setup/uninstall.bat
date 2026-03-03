@echo off
chcp 65001 >nul
echo ============================================================
echo   VestasLovePDF - Desinstalador
echo ============================================================
echo.
echo   Este script irá:
echo   - Remover o atalho da área de trabalho
echo   - Limpar cache do Python (__pycache__)
echo   - Remover builds (build/, dist/)
echo.
echo   Os arquivos do projeto NÃO serão removidos.
echo.
choice /C SN /M "Deseja continuar"
if errorlevel 2 goto :end

:: Navega para o diretório do projeto
cd /d "%~dp0.."

echo.
echo [1/4] Removendo atalho da área de trabalho...

:: Remove o atalho da área de trabalho
set "SHORTCUT=%USERPROFILE%\Desktop\VestasLovePDF.lnk"
if exist "%SHORTCUT%" (
    del "%SHORTCUT%"
    echo [OK] Atalho removido da área de trabalho.
) else (
    echo [INFO] Atalho não encontrado na área de trabalho.
)

echo.
echo [2/4] Limpando cache do Python...

:: Remove pastas __pycache__
for /d /r %%d in (__pycache__) do (
    if exist "%%d" (
        rd /s /q "%%d" 2>nul
    )
)
echo [OK] Cache do Python limpo.

echo.
echo [3/4] Removendo arquivos de build...

:: Remove pasta build
if exist "build" (
    rd /s /q "build"
    echo [OK] Pasta build/ removida.
) else (
    echo [INFO] Pasta build/ não encontrada.
)

:: Remove pasta dist
if exist "dist" (
    rd /s /q "dist"
    echo [OK] Pasta dist/ removida.
) else (
    echo [INFO] Pasta dist/ não encontrada.
)

:: Remove arquivos .spec do PyInstaller
if exist "*.spec" (
    del /q *.spec
    echo [OK] Arquivos .spec removidos.
)

echo.
echo [4/4] Verificação final...

:: Verifica se há processo do VestasLovePDF rodando
tasklist /FI "IMAGENAME eq pythonw.exe" 2>NUL | find /I /N "pythonw.exe" >nul
if not errorlevel 1 (
    echo [AVISO] pythonw.exe está em execução.
    echo [INFO] O VestasLovePDF pode estar rodando em segundo plano.
)

echo.
echo ============================================================
echo   Desinstalação concluída!
echo ============================================================
echo.
echo   Para remover completamente:
echo   1. Feche o VestasLovePDF se estiver rodando
echo   2. Delete a pasta do projeto manualmente
echo.
echo   Para desinstalar dependências Python:
echo   pip uninstall flask pandas openpyxl PyMuPDF pytesseract Pillow python-docx pdf2docx
echo ============================================================
echo.

:end
pause
