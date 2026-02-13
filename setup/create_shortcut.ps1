# Script PowerShell para criar atalho do Converter em modo silencioso
# Execute como: powershell -ExecutionPolicy Bypass -File create_shortcut.ps1

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = Split-Path -Parent $ScriptDir

# Caminhos
$PythonwPath = (Get-Command pythonw -ErrorAction SilentlyContinue).Source
if (-not $PythonwPath) {
    $PythonwPath = "C:\Users\SAPSD\AppData\Local\Programs\Python\Python314\pythonw.exe"
}
$ScriptPath = Join-Path $ProjectDir "run_silent.pyw"
$Desktop = [Environment]::GetFolderPath("Desktop")
$ShortcutPath = Join-Path $Desktop "Converter.lnk"

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
$Shortcut.Description = "Converter - Ferramenta de Conversão de Arquivos (Modo Silencioso)"
$Shortcut.WindowStyle = 7  # Minimizado
$Shortcut.Save()

Write-Host "=" * 60 -ForegroundColor Green
Write-Host "  Atalho criado com sucesso!" -ForegroundColor Green
Write-Host "  Local: $ShortcutPath" -ForegroundColor Cyan
Write-Host "  O programa será executado sem janela do terminal." -ForegroundColor Yellow
Write-Host "=" * 60 -ForegroundColor Green
