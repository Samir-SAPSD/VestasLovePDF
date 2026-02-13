@echo off
chcp 65001 >nul
echo ============================================================
echo   Converter - Desinstalador
echo ============================================================
echo.

:: Remove o atalho da área de trabalho
set "SHORTCUT=%USERPROFILE%\Desktop\Converter.lnk"
if exist "%SHORTCUT%" (
    del "%SHORTCUT%"
    echo [OK] Atalho removido da área de trabalho.
) else (
    echo [INFO] Atalho não encontrado na área de trabalho.
)

echo.
echo ============================================================
echo   Desinstalação concluída!
echo   Os arquivos do programa não foram removidos.
echo   Para remover completamente, delete a pasta do projeto.
echo ============================================================
echo.
pause
