# Script PowerShell para configurar o Tesseract OCR no VestasLovePDF
# Execute como: powershell -ExecutionPolicy Bypass -File setup_tesseract.ps1

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = Split-Path -Parent $ScriptDir
$TesseractLocalDir = Join-Path $ProjectDir "tesseract"

Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "  VestasLovePDF - Configuração do Tesseract OCR" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

# Verificar se já existe Tesseract na pasta local
$LocalTesseract = Join-Path $TesseractLocalDir "tesseract.exe"
if (Test-Path $LocalTesseract) {
    Write-Host "[OK] Tesseract já está configurado na pasta do projeto!" -ForegroundColor Green
    Write-Host "     Local: $TesseractLocalDir" -ForegroundColor Gray
    Write-Host ""
    exit 0
}

# Procurar Tesseract instalado no sistema
$PossiblePaths = @(
    "C:\Program Files\Tesseract-OCR",
    "C:\Program Files (x86)\Tesseract-OCR",
    "$env:LOCALAPPDATA\Tesseract-OCR",
    "$env:LOCALAPPDATA\Programs\Tesseract-OCR"
)

$FoundPath = $null
foreach ($path in $PossiblePaths) {
    $testExe = Join-Path $path "tesseract.exe"
    if (Test-Path $testExe) {
        $FoundPath = $path
        break
    }
}

if ($FoundPath) {
    Write-Host "[INFO] Tesseract encontrado em: $FoundPath" -ForegroundColor Yellow
    Write-Host ""
    
    $response = Read-Host "Deseja copiar para a pasta do projeto? (S/N)"
    if ($response -match "^[Ss]") {
        Write-Host ""
        Write-Host "Copiando arquivos..." -ForegroundColor Cyan
        
        # Criar pasta de destino se não existir
        if (-not (Test-Path $TesseractLocalDir)) {
            New-Item -ItemType Directory -Path $TesseractLocalDir -Force | Out-Null
        }
        
        # Copiar todos os arquivos
        Copy-Item -Path "$FoundPath\*" -Destination $TesseractLocalDir -Recurse -Force
        
        Write-Host ""
        Write-Host "[OK] Tesseract copiado com sucesso!" -ForegroundColor Green
        Write-Host "     Local: $TesseractLocalDir" -ForegroundColor Gray
        
        # Verificar idiomas disponíveis
        $TessdataDir = Join-Path $TesseractLocalDir "tessdata"
        if (Test-Path $TessdataDir) {
            $langs = Get-ChildItem -Path $TessdataDir -Filter "*.traineddata" | Select-Object -ExpandProperty BaseName
            Write-Host ""
            Write-Host "     Idiomas disponíveis: $($langs -join ', ')" -ForegroundColor Gray
        }
    } else {
        Write-Host "[INFO] Operação cancelada." -ForegroundColor Yellow
    }
} else {
    Write-Host "[AVISO] Tesseract não encontrado no sistema!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Para configurar o OCR:" -ForegroundColor White
    Write-Host ""
    Write-Host "1. Baixe o instalador em:" -ForegroundColor White
    Write-Host "   https://github.com/UB-Mannheim/tesseract/wiki" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "2. Execute o instalador e marque os idiomas:" -ForegroundColor White
    Write-Host "   - Portuguese" -ForegroundColor Gray
    Write-Host "   - English" -ForegroundColor Gray
    Write-Host ""
    Write-Host "3. Após instalar, execute este script novamente" -ForegroundColor White
    Write-Host "   OU copie manualmente o conteúdo de:" -ForegroundColor White
    Write-Host "   C:\Program Files\Tesseract-OCR" -ForegroundColor Cyan
    Write-Host "   Para:" -ForegroundColor White
    Write-Host "   $TesseractLocalDir" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""
Read-Host "Pressione Enter para sair"
