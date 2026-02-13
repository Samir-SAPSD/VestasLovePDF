# Converter - Setup e Instalação

## Opção 1: Instalação Rápida (Recomendado)

1. Execute o arquivo `install.bat` como administrador
2. Aguarde a instalação das dependências
3. Um atalho será criado automaticamente na área de trabalho

## Opção 2: Instalação Manual

### Passo 1: Instalar dependências
```bash
pip install -r requirements.txt
```

### Passo 2: Criar atalho manualmente
Execute no PowerShell:
```powershell
powershell -ExecutionPolicy Bypass -File setup/create_shortcut.ps1
```

## Opção 3: Criar Executável Standalone

Para criar um executável `.exe` que não precisa do Python instalado:

```bash
python setup/build_exe.py
```

O executável será gerado em `dist/Converter.exe`

## Arquivos do Setup

| Arquivo | Descrição |
|---------|-----------|
| `install.bat` | Instalador principal (instala dependências + cria atalho) |
| `uninstall.bat` | Remove o atalho da área de trabalho |
| `create_shortcut.ps1` | Script PowerShell para criar o atalho |
| `build_exe.py` | Script para criar executável standalone com PyInstaller |

## Modo Silencioso

O atalho criado executa o programa usando `pythonw.exe` e o arquivo `run_silent.pyw`, que:
- **Não exibe janela do terminal/console**
- Abre automaticamente o navegador na interface web
- Encerra automaticamente quando o navegador é fechado

## Requisitos

- Python 3.10 ou superior
- Windows 10/11
- Conexão com internet (para instalação inicial)

## Solução de Problemas

### O atalho não funciona
1. Verifique se o Python está instalado corretamente
2. Execute `pip install -r requirements.txt` manualmente
3. Tente executar `run_silent.pyw` diretamente

### O programa não abre o navegador
1. Verifique se a porta 5000 não está em uso
2. Abra manualmente: http://127.0.0.1:5000

### Erro de dependências
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```
