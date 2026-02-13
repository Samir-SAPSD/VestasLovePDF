# VestasLovePDF - Setup e Instalação

Ferramenta local para manipulação de PDFs e conversão de arquivos, similar ao iLovePDF.

## Funcionalidades

- **Conversor de Arquivos** - Converte entre diversos formatos
- **Conversor Excel** - Converte entre formatos de planilha (xlsx, xls, csv, ods)
- **Compressor de PDF** - Reduz o tamanho de arquivos PDF
- **Mesclador de PDF** - Une múltiplos PDFs em um único arquivo
- **Divisor de PDF** - Divide um PDF em múltiplos arquivos
- **OCR PDF** - Extrai texto de PDFs escaneados usando Tesseract OCR

## Opção 1: Instalação Rápida (Recomendado)

1. Execute o arquivo `install.bat`
2. Aguarde a instalação das dependências
3. Um atalho será criado automaticamente na área de trabalho
4. (Opcional) Instale o Tesseract OCR para habilitar a funcionalidade de OCR

## Opção 2: Instalação Manual

### Passo 1: Instalar dependências Python
```bash
pip install -r requirements.txt
```

### Passo 2: Instalar Tesseract OCR (para funcionalidade OCR)
Veja a seção [Instalação do Tesseract OCR](#instalação-do-tesseract-ocr) abaixo.

### Passo 3: Criar atalho manualmente
Execute no PowerShell:
```powershell
powershell -ExecutionPolicy Bypass -File setup/create_shortcut.ps1
```

## Opção 3: Criar Executável Standalone

Para criar um executável `.exe` que não precisa do Python instalado:

```bash
python setup/build_exe.py
```

O executável será gerado em `dist/VestasLovePDF.exe`

## Instalação do Tesseract OCR

A funcionalidade de OCR (Reconhecimento Óptico de Caracteres) requer o Tesseract OCR.

### Método Recomendado: Pasta Local (Windows)

O VestasLovePDF detecta automaticamente o Tesseract na pasta `tesseract/` do projeto.

**Passo 1:** Baixar e instalar o Tesseract
1. Acesse: https://github.com/UB-Mannheim/tesseract/wiki
2. Baixe o instalador mais recente (ex: `tesseract-ocr-w64-setup-5.x.x.exe`)
3. Execute o instalador
4. **Importante:** Marque os idiomas:
   - ☑ Portuguese
   - ☑ English

**Passo 2:** Copiar para a pasta do projeto
1. Abra o Explorador de Arquivos
2. Navegue até: `C:\Program Files\Tesseract-OCR`
3. Selecione **todo o conteúdo** (Ctrl+A)
4. Copie (Ctrl+C)
5. Cole na pasta `tesseract/` do projeto (Ctrl+V)

**Estrutura esperada:**
```
VestasLovePDF/
└── tesseract/
    ├── tesseract.exe
    ├── tessdata/
    │   ├── eng.traineddata
    │   ├── por.traineddata
    │   └── ...
    └── *.dll
```

> 💡 **Dica:** O `install.bat` pode fazer essa cópia automaticamente se o Tesseract já estiver instalado no sistema.

### Alternativa: Linux/macOS

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install tesseract-ocr tesseract-ocr-por tesseract-ocr-eng
```

**macOS:**
```bash
brew install tesseract tesseract-lang
```

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
- **Tesseract OCR** (opcional, para funcionalidade OCR)

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

### OCR não funciona
1. Verifique se a pasta `tesseract/` contém o arquivo `tesseract.exe`
2. Verifique se a pasta `tesseract/tessdata/` contém os arquivos de idioma (`.traineddata`)
3. Reinicie o VestasLovePDF após copiar os arquivos
4. Veja as instruções no modal de instalação dentro da funcionalidade OCR
