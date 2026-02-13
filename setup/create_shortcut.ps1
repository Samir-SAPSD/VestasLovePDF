# Script PowerShell para criar atalho do VestasLovePDF em modo silencioso
# Execute como: powershell -ExecutionPolicy Bypass -File create_shortcut.ps1

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = Split-Path -Parent $ScriptDir

# Caminhos
$PythonwPath = (Get-Command pythonw -ErrorAction SilentlyContinue).Source
if (-not $PythonwPath) {
    # Tenta encontrar pythonw.exe no PATH do sistema
    $PythonPath = (Get-Command python -ErrorAction SilentlyContinue).Source
    if ($PythonPath) {
        $PythonwPath = Join-Path (Split-Path $PythonPath) "pythonw.exe"
    }
}
$ScriptPath = Join-Path $ProjectDir "run_silent.pyw"
$Desktop = [Environment]::GetFolderPath("Desktop")
$ShortcutPath = Join-Path $Desktop "VestasLovePDF.lnk"

# Verifica se o arquivo .pyw existe
if (-not (Test-Path $ScriptPath)) {
    Write-Host "Erro: Arquivo run_silent.pyw não encontrado em: $ScriptPath" -ForegroundColor Red
    exit 1
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
Write-Host "  O programa será executado sem janela do terminal." -ForegroundColor Yellow
Write-Host "=" * 60 -ForegroundColor Green
