import os
from io import BytesIO
import zipfile
import gzip

def compress_image(file, quality=85):
    """Comprime imagens (PNG, JPG, JPEG, WEBP)."""
    from PIL import Image
    
    output = BytesIO()
    filename = file.filename
    ext = os.path.splitext(filename)[1].lower()
    
    # Abrir imagem
    img = Image.open(file)
    
    # Converter para RGB se necessário (para JPEG)
    if img.mode in ('RGBA', 'P') and ext in ('.jpg', '.jpeg'):
        img = img.convert('RGB')
    
    # Obter tamanho original
    file.seek(0, 2)
    original_size = file.tell()
    file.seek(0)
    
    # Nome base do arquivo sem extensão
    base_name = os.path.splitext(filename)[0]
    
    # Comprimir baseado no formato
    if ext in ('.jpg', '.jpeg'):
        img.save(output, format='JPEG', quality=quality, optimize=True)
        output_filename = base_name + '_compressed' + ext
        mimetype = 'image/jpeg'
    elif ext == '.png':
        img.save(output, format='PNG', optimize=True)
        output_filename = base_name + '_compressed.png'
        mimetype = 'image/png'
    elif ext == '.webp':
        img.save(output, format='WEBP', quality=quality, optimize=True)
        output_filename = base_name + '_compressed.webp'
        mimetype = 'image/webp'
    else:
        # Converter para JPEG para melhor compressão
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        img.save(output, format='JPEG', quality=quality, optimize=True)
        output_filename = base_name + '_compressed.jpg'
        mimetype = 'image/jpeg'
    
    compressed_size = output.tell()
    compression_ratio = ((original_size - compressed_size) / original_size) * 100 if original_size > 0 else 0
    
    output.seek(0)
    return output, output_filename, mimetype, original_size, compressed_size, compression_ratio


def compress_pdf(file, quality=75):
    """Comprime arquivos PDF.
    
    Args:
        file: Arquivo PDF
        quality: Qualidade das imagens internas (1-100, padrão 75)
    """
    import fitz  # PyMuPDF
    
    output = BytesIO()
    filename = file.filename
    
    # Obter tamanho original
    file.seek(0, 2)
    original_size = file.tell()
    file.seek(0)
    
    # Abrir PDF
    pdf_data = file.read()
    doc = fitz.open(stream=pdf_data, filetype="pdf")
    
    # Comprimir imagens no PDF e otimizar
    for page in doc:
        # Obter imagens da página
        image_list = page.get_images()
        for img_index, img in enumerate(image_list):
            xref = img[0]
            # Tentar comprimir a imagem
            try:
                base_image = doc.extract_image(xref)
                if base_image:
                    image_bytes = base_image["image"]
                    # Re-comprimir imagem com a qualidade especificada
                    from PIL import Image
                    pil_img = Image.open(BytesIO(image_bytes))
                    img_buffer = BytesIO()
                    if pil_img.mode in ('RGBA', 'P'):
                        pil_img = pil_img.convert('RGB')
                    pil_img.save(img_buffer, format='JPEG', quality=quality, optimize=True)
                    img_buffer.seek(0)
            except:
                pass
    
    # Salvar PDF otimizado
    doc.save(output, garbage=4, deflate=True, clean=True)
    doc.close()
    
    compressed_size = output.tell()
    compression_ratio = ((original_size - compressed_size) / original_size) * 100 if original_size > 0 else 0
    
    # Nome com sufixo _compressed
    base_name = os.path.splitext(filename)[0]
    output_filename = base_name + '_compressed.pdf'
    
    output.seek(0)
    return output, output_filename, 'application/pdf', original_size, compressed_size, compression_ratio


def compress_to_zip(file, compresslevel=9):
    """Comprime arquivo para ZIP.
    
    Args:
        file: Arquivo a comprimir
        compresslevel: Nível de compressão (1-9, padrão 9 = máximo)
    """
    output = BytesIO()
    filename = file.filename
    
    # Obter tamanho original
    file.seek(0, 2)
    original_size = file.tell()
    file.seek(0)
    
    # Criar ZIP com o nível de compressão especificado
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED, compresslevel=compresslevel) as zipf:
        zipf.writestr(filename, file.read())
    
    compressed_size = output.tell()
    compression_ratio = ((original_size - compressed_size) / original_size) * 100 if original_size > 0 else 0
    
    output_filename = os.path.splitext(filename)[0] + '_compressed.zip'
    
    output.seek(0)
    return output, output_filename, 'application/zip', original_size, compressed_size, compression_ratio


def compress_file(file, compression_type='auto', quality=85):
    """
    Comprime um arquivo baseado no tipo.
    
    Args:
        file: Arquivo enviado
        compression_type: 'auto', 'image', 'pdf', 'zip'
        quality: Qualidade para compressão (1-100 para imagens/PDF, 1-9 para ZIP)
    
    Returns:
        tuple: (output, filename, mimetype, original_size, compressed_size, compression_ratio)
    """
    filename = file.filename
    ext = os.path.splitext(filename)[1].lower()
    
    # Determinar tipo de compressão
    if compression_type == 'auto':
        if ext in ('.jpg', '.jpeg', '.png', '.webp', '.bmp', '.gif', '.tiff'):
            compression_type = 'image'
        elif ext == '.pdf':
            compression_type = 'pdf'
        else:
            compression_type = 'zip'
    
    # Executar compressão apropriada
    if compression_type == 'image':
        return compress_image(file, quality)
    elif compression_type == 'pdf':
        return compress_pdf(file, quality)
    else:
        # Para ZIP, converter quality (1-100) para compresslevel (1-9)
        compresslevel = max(1, min(9, round(quality / 11)))
        return compress_to_zip(file, compresslevel)


def get_supported_formats():
    """Retorna formatos suportados para compressão."""
    return {
        'image': {
            'extensions': ['.jpg', '.jpeg', '.png', '.webp', '.bmp', '.gif', '.tiff'],
            'description': 'Imagens (JPG, PNG, WebP, etc.)'
        },
        'pdf': {
            'extensions': ['.pdf'],
            'description': 'Documentos PDF'
        },
        'general': {
            'extensions': ['*'],
            'description': 'Qualquer arquivo (comprime para ZIP)'
        }
    }


def format_size(size_bytes):
    """Formata tamanho em bytes para formato legível."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def estimate_compression(file, compression_type='auto', quality=85):
    """
    Estima o tamanho final após compressão.
    Faz a compressão real mas retorna apenas as estatísticas.
    """
    filename = file.filename
    ext = os.path.splitext(filename)[1].lower()
    
    # Determinar tipo de compressão
    if compression_type == 'auto':
        if ext in ('.jpg', '.jpeg', '.png', '.webp', '.bmp', '.gif', '.tiff'):
            compression_type = 'image'
        elif ext == '.pdf':
            compression_type = 'pdf'
        else:
            compression_type = 'zip'
    
    # Executar compressão para obter estatísticas
    try:
        if compression_type == 'image':
            output, output_filename, mimetype, original_size, compressed_size, ratio = compress_image(file, quality)
        elif compression_type == 'pdf':
            output, output_filename, mimetype, original_size, compressed_size, ratio = compress_pdf(file)
        else:
            output, output_filename, mimetype, original_size, compressed_size, ratio = compress_to_zip(file)
        
        return {
            'original_size': original_size,
            'original_size_formatted': format_size(original_size),
            'compressed_size': compressed_size,
            'compressed_size_formatted': format_size(compressed_size),
            'compression_ratio': round(ratio, 1),
            'savings': format_size(original_size - compressed_size) if original_size > compressed_size else '0 B',
            'output_filename': output_filename,
            'quality_used': quality,
            'compression_type': compression_type
        }
    except Exception as e:
        raise Exception(f"Erro ao estimar compressão: {str(e)}")


def calculate_quality_for_target_size(file, target_size_bytes, compression_type='auto'):
    """
    Calcula a qualidade necessária para atingir um tamanho alvo.
    Usa busca binária para encontrar a qualidade ideal.
    
    Returns:
        dict com: quality, estimated_size, quality_loss_percent, warning_level
    """
    from io import BytesIO
    
    filename = file.filename
    ext = os.path.splitext(filename)[1].lower()
    
    # Determinar tipo de compressão
    if compression_type == 'auto':
        if ext in ('.jpg', '.jpeg', '.png', '.webp', '.bmp', '.gif', '.tiff'):
            compression_type = 'image'
        elif ext == '.pdf':
            compression_type = 'pdf'
        else:
            compression_type = 'zip'
    
    # Obter tamanho original
    file.seek(0, 2)
    original_size = file.tell()
    file.seek(0)
    
    # Se o tamanho alvo é maior que o original, não faz sentido
    if target_size_bytes >= original_size:
        return {
            'error': 'O tamanho alvo deve ser menor que o tamanho original',
            'supports_custom_size': True
        }
    
    # Configurações baseadas no tipo de arquivo
    if compression_type == 'image':
        min_quality = 5
        max_quality = 100
        compress_func = lambda q: compress_image(file, q)
        quality_label = 'Qualidade da imagem'
    elif compression_type == 'pdf':
        min_quality = 10
        max_quality = 100
        compress_func = lambda q: compress_pdf(file, q)
        quality_label = 'Qualidade das imagens do PDF'
    else:  # zip
        # ZIP tem compresslevel de 1-9, mas vamos usar 1-100 e converter internamente
        min_quality = 11  # equivale a compresslevel 1
        max_quality = 100  # equivale a compresslevel 9
        compress_func = lambda q: compress_to_zip(file, max(1, min(9, round(q / 11))))
        quality_label = 'Nível de compressão'
    
    # Busca binária para encontrar a qualidade ideal
    best_quality = min_quality
    best_size = 0
    iterations = 0
    max_iterations = 12
    
    while min_quality <= max_quality and iterations < max_iterations:
        iterations += 1
        mid_quality = (min_quality + max_quality) // 2
        
        # Resetar posição do arquivo
        file.seek(0)
        
        # Testar compressão com essa qualidade
        try:
            output, _, _, _, compressed_size, _ = compress_func(mid_quality)
            
            if compressed_size <= target_size_bytes:
                best_quality = mid_quality
                best_size = compressed_size
                min_quality = mid_quality + 1
            else:
                max_quality = mid_quality - 1
        except Exception as e:
            break
    
    # Se não conseguiu atingir o tamanho, usar qualidade mínima
    if best_size == 0 or best_size > target_size_bytes:
        file.seek(0)
        try:
            if compression_type == 'image':
                output, _, _, _, best_size, _ = compress_image(file, 5)
                best_quality = 5
            elif compression_type == 'pdf':
                output, _, _, _, best_size, _ = compress_pdf(file, 10)
                best_quality = 10
            else:
                output, _, _, _, best_size, _ = compress_to_zip(file, 9)
                best_quality = 100
        except:
            return {
                'error': 'Não foi possível calcular a qualidade necessária',
                'supports_custom_size': True
            }
    
    # Calcular perda de qualidade (em relação a 100%)
    quality_loss_percent = 100 - best_quality
    
    # Determinar nível de aviso baseado no tipo
    if compression_type == 'zip':
        # Para ZIP, compressão alta não significa perda de qualidade
        warning_level = 'ok'
        warning_message = 'Compressão ZIP não causa perda de qualidade'
        quality_loss_percent = 0
    elif compression_type == 'pdf':
        if best_quality >= 50:
            warning_level = 'ok'
            warning_message = 'Qualidade das imagens do PDF aceitável'
        elif best_quality >= 30:
            warning_level = 'medium'
            warning_message = 'Imagens do PDF terão qualidade moderada'
        elif best_quality >= 15:
            warning_level = 'high'
            warning_message = 'Imagens do PDF terão qualidade baixa'
        else:
            warning_level = 'critical'
            warning_message = 'Imagens do PDF ficarão muito degradadas'
    else:  # image
        if best_quality >= 60:
            warning_level = 'ok'
            warning_message = 'Qualidade aceitável'
        elif best_quality >= 40:
            warning_level = 'medium'
            warning_message = 'Qualidade moderada - pode haver perda visível'
        elif best_quality >= 20:
            warning_level = 'high'
            warning_message = 'Qualidade baixa - haverá perda significativa de detalhes'
        else:
            warning_level = 'critical'
            warning_message = 'Qualidade muito baixa - a imagem pode ficar muito degradada'
    
    return {
        'supports_custom_size': True,
        'compression_type': compression_type,
        'recommended_quality': best_quality,
        'estimated_size': best_size,
        'estimated_size_formatted': format_size(best_size),
        'quality_loss_percent': quality_loss_percent,
        'quality_label': quality_label,
        'warning_level': warning_level,
        'warning_message': warning_message,
        'target_achievable': best_size <= target_size_bytes,
        'original_size': original_size,
        'original_size_formatted': format_size(original_size)
    }
