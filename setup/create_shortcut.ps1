# Script PowerShell para criar atalho do VestasLovePDF em modo silencioso
# Execute como: powershell -ExecutionPolicy Bypass -File create_shortcut.ps1
#
# Arquitetura do VestasLovePDF:
#   - Flask API com Blueprint pattern (app/api/v1/)
#   - Processadores com Strategy pattern (app/processors/)
#   - Core utilities (app/core/)
#   - Templates e static files (app/templates/, app/static/)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = Split-Path -Parent $ScriptDir

# Encontrar pythonw.exe
$PythonwPath = $null

# Tenta Get-Command primeiro
$PythonwCmd = Get-Command pythonw -ErrorAction SilentlyContinue
if ($PythonwCmd) {
    $PythonwPath = $PythonwCmd.Source
}

# Se não encontrou, tenta via python
if (-not $PythonwPath) {
    $PythonCmd = Get-Command python -ErrorAction SilentlyContinue
    if ($PythonCmd) {
        $PythonDir = Split-Path $PythonCmd.Source
        $PythonwPath = Join-Path $PythonDir "pythonw.exe"
        if (-not (Test-Path $PythonwPath)) {
            $PythonwPath = $null
        }
    }
}

# Se ainda não encontrou, verifica locais comuns do Windows
if (-not $PythonwPath) {
    $CommonPaths = @(
        "$env:LOCALAPPDATA\Programs\Python\Python*\pythonw.exe",
        "C:\Python*\pythonw.exe",
        "$env:ProgramFiles\Python*\pythonw.exe"
    )
    foreach ($Pattern in $CommonPaths) {
        $Found = Get-ChildItem $Pattern -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($Found) {
            $PythonwPath = $Found.FullName
            break
        }
    }
}

if (-not $PythonwPath) {
    Write-Host "Erro: pythonw.exe não encontrado!" -ForegroundColor Red
    Write-Host "Certifique-se de que o Python está instalado corretamente." -ForegroundColor Yellow
    exit 1
}

$ScriptPath = Join-Path $ProjectDir "run_silent.pyw"
$Desktop = [Environment]::GetFolderPath("Desktop")
$ShortcutPath = Join-Path $Desktop "VestasLovePDF.lnk"

# Verifica se o arquivo .pyw existe
if (-not (Test-Path $ScriptPath)) {
    Write-Host "Erro: Arquivo run_silent.pyw não encontrado em: $ScriptPath" -ForegroundColor Red
    exit 1
}

# Verifica estrutura do projeto
$RequiredDirs = @("app", "app\api", "app\api\v1", "app\templates")
foreach ($Dir in $RequiredDirs) {
    $DirPath = Join-Path $ProjectDir $Dir
    if (-not (Test-Path $DirPath)) {
        Write-Host "Aviso: Diretório não encontrado: $Dir" -ForegroundColor Yellow
    }
}

# Cria o atalho
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $PythonwPath
$Shortcut.Arguments = "`"$ScriptPath`""
$Shortcut.WorkingDirectory = $ProjectDir
$Shortcut.Description = "VestasLovePDF - Ferramenta de PDF e Conversão de Arquivos"
$Shortcut.WindowStyle = 7  # Minimizado
$Shortcut.Save()

Write-Host "=" * 60 -ForegroundColor Green
Write-Host "  Atalho criado com sucesso!" -ForegroundColor Green
Write-Host "  Local: $ShortcutPath" -ForegroundColor Cyan
Write-Host "  Pythonw: $PythonwPath" -ForegroundColor Cyan
Write-Host "  Script: $ScriptPath" -ForegroundColor Cyan
Write-Host "  O programa será executado sem janela do terminal." -ForegroundColor Yellow
Write-Host "=" * 60 -ForegroundColor Green
