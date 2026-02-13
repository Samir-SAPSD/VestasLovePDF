# Tesseract OCR - Configuração Local

Esta pasta é destinada aos arquivos do Tesseract OCR para uso local no VestasLovePDF.

## Como Configurar

### Opção 1: Copiar instalação existente

Se você já tem o Tesseract instalado no sistema:

1. Localize a pasta de instalação (geralmente `C:\Program Files\Tesseract-OCR`)
2. Copie **todo o conteúdo** da pasta para cá
3. A estrutura deve ficar assim:

```
tesseract/
├── tesseract.exe
├── tessdata/
│   ├── eng.traineddata
│   ├── por.traineddata
│   └── ... (outros idiomas)
├── libtesseract-5.dll
└── ... (outros arquivos DLL)
```

### Opção 2: Download direto dos binários

1. Acesse: https://github.com/UB-Mannheim/tesseract/wiki
2. Baixe a versão mais recente (ex: `tesseract-ocr-w64-setup-5.x.x.exe`)
3. Execute o instalador e selecione os idiomas:
   - **Portuguese** (Português)
   - **English** (Inglês)
   - Outros que precisar
4. Após instalar, copie o conteúdo de `C:\Program Files\Tesseract-OCR` para esta pasta

### Opção 3: Versão portátil

1. Acesse: https://digi.bib.uni-mannheim.de/tesseract/
2. Baixe o arquivo ZIP da versão portátil (se disponível)
3. Extraia o conteúdo para esta pasta

## Verificar Instalação

Após copiar os arquivos, reinicie o VestasLovePDF e acesse a funcionalidade OCR.
O sistema detectará automaticamente o Tesseract nesta pasta.

## Idiomas Disponíveis

Para adicionar mais idiomas:

1. Baixe os arquivos `.traineddata` de: https://github.com/tesseract-ocr/tessdata
2. Coloque na pasta `tesseract/tessdata/`

Idiomas comuns:
- `por.traineddata` - Português
- `eng.traineddata` - Inglês
- `spa.traineddata` - Espanhol
- `fra.traineddata` - Francês
- `deu.traineddata` - Alemão

## Estrutura Esperada

```
tesseract/
├── README.md (este arquivo)
├── tesseract.exe (executável principal)
├── tessdata/
│   ├── eng.traineddata
│   ├── por.traineddata
│   ├── osd.traineddata
│   └── configs/
├── doc/
├── libtesseract-5.dll
├── libleptonica-6.dll
└── ... (outras DLLs necessárias)
```
