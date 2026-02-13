@echo off
chcp 65001 >nul
echo Configurando Tesseract OCR para VestasLovePDF...
echo.
powershell -ExecutionPolicy Bypass -File "%~dp0setup_tesseract.ps1"
