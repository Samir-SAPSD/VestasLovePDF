/**
 * API Client - Vestas Love PDF
 * Funções para comunicação com a API v1
 */

const API_BASE = '/api/v1';

/**
 * Cliente API genérico
 */
const ApiClient = {
    /**
     * Faz uma requisição GET
     * @param {string} endpoint - Endpoint da API
     * @returns {Promise<Object>} Resposta da API
     */
    async get(endpoint) {
        const response = await fetch(`${API_BASE}${endpoint}`);
        return this._handleResponse(response);
    },

    /**
     * Faz uma requisição POST com JSON
     * @param {string} endpoint - Endpoint da API
     * @param {Object} data - Dados a enviar
     * @returns {Promise<Object>} Resposta da API
     */
    async postJson(endpoint, data) {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        return this._handleResponse(response);
    },

    /**
     * Faz uma requisição POST com FormData
     * @param {string} endpoint - Endpoint da API
     * @param {FormData} formData - FormData a enviar
     * @returns {Promise<Object>} Resposta da API
     */
    async postForm(endpoint, formData) {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            method: 'POST',
            body: formData
        });
        return this._handleResponse(response);
    },

    /**
     * Faz uma requisição POST e retorna um Blob (para downloads)
     * @param {string} endpoint - Endpoint da API
     * @param {FormData|Object} data - Dados a enviar
     * @param {boolean} isJson - Se true, envia como JSON
     * @returns {Promise<{blob: Blob, filename: string}>}
     */
    async postForDownload(endpoint, data, isJson = false) {
        const options = {
            method: 'POST'
        };

        if (isJson) {
            options.headers = { 'Content-Type': 'application/json' };
            options.body = JSON.stringify(data);
        } else {
            options.body = data;
        }

        const response = await fetch(`${API_BASE}${endpoint}`, options);
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error?.message || 'Erro ao processar arquivo');
        }

        const blob = await response.blob();
        const filename = this._extractFilename(response);

        return { blob, filename };
    },

    /**
     * Extrai o nome do arquivo do header Content-Disposition
     */
    _extractFilename(response) {
        const disposition = response.headers.get('Content-Disposition');
        if (disposition) {
            const matches = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/.exec(disposition);
            if (matches && matches[1]) {
                return matches[1].replace(/['"]/g, '');
            }
        }
        return 'download';
    },

    /**
     * Processa a resposta da API
     */
    async _handleResponse(response) {
        const data = await response.json();
        
        if (!response.ok || !data.success) {
            throw new Error(data.error?.message || 'Erro na requisição');
        }
        
        return data.data;
    }
};

/**
 * API de Compressão
 */
const CompressApi = {
    /**
     * Comprime um arquivo
     * @param {File} file - Arquivo a comprimir
     * @param {Object} options - Opções de compressão
     * @returns {Promise<{blob: Blob, filename: string}>}
     */
    async compress(file, options = {}) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('compression_type', options.compressionType || 'auto');
        formData.append('quality', options.quality || 85);

        return ApiClient.postForDownload('/compress/', formData);
    },

    /**
     * Estima o resultado da compressão
     * @param {File} file - Arquivo a analisar
     * @param {Object} options - Opções de compressão
     * @returns {Promise<Object>}
     */
    async estimate(file, options = {}) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('compression_type', options.compressionType || 'auto');
        formData.append('quality', options.quality || 85);

        return ApiClient.postForm('/compress/estimate', formData);
    },

    /**
     * Calcula a qualidade necessária para atingir um tamanho alvo
     * @param {File} file - Arquivo a analisar
     * @param {number} targetSize - Tamanho alvo
     * @param {string} targetUnit - Unidade (KB ou MB)
     * @param {string} compressionType - Tipo de compressão
     * @returns {Promise<Object>}
     */
    async calculateTargetQuality(file, targetSize, targetUnit = 'KB', compressionType = 'auto') {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('target_size', targetSize);
        formData.append('target_unit', targetUnit);
        formData.append('compression_type', compressionType);

        return ApiClient.postForm('/compress/target-quality', formData);
    },

    /**
     * Obtém formatos suportados
     * @returns {Promise<Object>}
     */
    async getFormats() {
        return ApiClient.get('/compress/formats');
    }
};

/**
 * API de Conversão
 */
const ConvertApi = {
    /**
     * Converte um arquivo
     * @param {File} file - Arquivo a converter
     * @param {string} convType - Tipo de conversão
     * @returns {Promise<{blob: Blob, filename: string}>}
     */
    async convert(file, convType) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('conv_type', convType);

        return ApiClient.postForDownload('/convert/', formData);
    },

    /**
     * Detecta o formato do arquivo
     * @param {File} file - Arquivo a analisar
     * @returns {Promise<Object>}
     */
    async detectFormat(file) {
        const formData = new FormData();
        formData.append('file', file);

        return ApiClient.postForm('/convert/detect', formData);
    },

    /**
     * Detecta versão do Excel
     * @param {File} file - Arquivo Excel
     * @returns {Promise<Object>}
     */
    async detectExcel(file) {
        const formData = new FormData();
        formData.append('file', file);

        return ApiClient.postForm('/convert/excel/detect', formData);
    }
};

/**
 * API de PDF Tools
 */
const PdfApi = {
    /**
     * Obtém preview de um PDF para merge
     * @param {File} file - Arquivo PDF
     * @returns {Promise<{preview: string, pages: number}>}
     */
    async getMergePreview(file) {
        const formData = new FormData();
        formData.append('file', file);

        return ApiClient.postForm('/pdf/merge/preview', formData);
    },

    /**
     * Unifica múltiplos PDFs
     * @param {Array<{content: string, rotation: number}>} files - PDFs em base64
     * @param {Object} options - Opções (outputFilename, compression)
     * @returns {Promise<{blob: Blob, filename: string}>}
     */
    async merge(files, options = {}) {
        return ApiClient.postForDownload('/pdf/merge', { 
            files,
            outputFilename: options.outputFilename || 'merged',
            compression: options.compression || 'none'
        }, true);
    },

    /**
     * Carrega todas as páginas de um PDF para split
     * @param {File} file - Arquivo PDF
     * @returns {Promise<{previews: string[], pages: number}>}
     */
    async loadForSplit(file) {
        const formData = new FormData();
        formData.append('file', file);

        return ApiClient.postForm('/pdf/split/load', formData);
    },

    /**
     * Divide um PDF
     * @param {File} file - Arquivo PDF
     * @param {Object} options - Opções de divisão
     * @param {string} options.mode - Modo: 'select', 'range', 'markers'
     * @param {number[]} [options.pages] - Páginas selecionadas (modo select)
     * @param {number} [options.pagesPerFile] - Páginas por arquivo (modo range)
     * @param {string} [options.pageRange] - Range de páginas (modo range)
     * @param {number[]} [options.markers] - Pontos de corte (modo markers)
     * @returns {Promise<{blob: Blob, filename: string}>}
     */
    async split(file, options = {}) {
        // Converter file para base64
        const arrayBuffer = await file.arrayBuffer();
        const base64 = btoa(
            new Uint8Array(arrayBuffer)
                .reduce((data, byte) => data + String.fromCharCode(byte), '')
        );
        
        // Determinar splitPoints baseado no modo
        let splitPoints = [];
        if (options.mode === 'select' && options.pages) {
            splitPoints = options.pages;
        } else if (options.mode === 'markers' && options.markers) {
            splitPoints = options.markers;
        } else if (options.mode === 'range') {
            splitPoints = options.pagesPerFile || options.pageRange || [];
        }
        
        return ApiClient.postForDownload('/pdf/split', {
            content: base64,
            splitPoints: splitPoints,
            fileName: file.name,
            mode: options.mode,
            pagesPerFile: options.pagesPerFile,
            pageRange: options.pageRange
        }, true);
    }
};

/**
 * API de OCR
 */
const OcrApi = {
    /**
     * Verifica se o Tesseract está instalado
     * @returns {Promise<Object>}
     */
    async checkTesseract() {
        return ApiClient.get('/ocr/check');
    },

    /**
     * Obtém idiomas disponíveis
     * @returns {Promise<Object>}
     */
    async getLanguages() {
        return ApiClient.get('/ocr/languages');
    },

    /**
     * Obtém preview de um PDF para OCR
     * @param {File} file - Arquivo PDF
     * @returns {Promise<{preview: string, pages: number}>}
     */
    async getPreview(file) {
        const formData = new FormData();
        formData.append('file', file);

        return ApiClient.postForm('/ocr/preview', formData);
    },

    /**
     * Extrai texto de um PDF
     * @param {File} file - Arquivo PDF
     * @param {Object} options - Opções de OCR
     * @returns {Promise<Object>}
     */
    async extractText(file, options = {}) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('language', options.language || 'por');
        formData.append('dpi', options.dpi || 300);

        return ApiClient.postForm('/ocr/extract', formData);
    },

    /**
     * Converte PDF usando OCR
     * @param {File} file - Arquivo PDF
     * @param {Object} options - Opções de OCR
     * @returns {Promise<{blob: Blob, filename: string}>}
     */
    async convert(file, options = {}) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('language', options.language || 'por');
        formData.append('dpi', options.dpi || 300);
        formData.append('output_format', options.outputFormat || 'txt');

        return ApiClient.postForDownload('/ocr/convert', formData);
    }
};

// Expor globalmente
window.ApiClient = ApiClient;
window.CompressApi = CompressApi;
window.ConvertApi = ConvertApi;
window.PdfApi = PdfApi;
window.OcrApi = OcrApi;
