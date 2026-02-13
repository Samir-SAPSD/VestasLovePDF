"""
Utilitário para unificação de PDFs.
"""
import fitz  # PyMuPDF
from io import BytesIO
import base64


def get_pdf_preview(file_content: bytes, page_number: int = 0, zoom: float = 1.0) -> str:
    """
    Gera uma imagem de preview de uma página específica do PDF.
    
    Args:
        file_content: Conteúdo binário do arquivo PDF
        page_number: Número da página (0-indexed)
        zoom: Fator de zoom para a imagem
        
    Returns:
        String base64 da imagem PNG
    """
    doc = fitz.open(stream=file_content, filetype="pdf")
    
    if page_number >= len(doc):
        page_number = 0
    
    page = doc.load_page(page_number)
    
    # Matriz de transformação para o zoom
    mat = fitz.Matrix(zoom, zoom)
    
    # Renderiza a página como imagem
    pix = page.get_pixmap(matrix=mat)
    
    # Converte para PNG
    img_bytes = pix.tobytes("png")
    
    doc.close()
    
    # Retorna como base64
    return base64.b64encode(img_bytes).decode('utf-8')


def get_pdf_page_count(file_content: bytes) -> int:
    """
    Retorna o número de páginas do PDF.
    
    Args:
        file_content: Conteúdo binário do arquivo PDF
        
    Returns:
        Número de páginas
    """
    doc = fitz.open(stream=file_content, filetype="pdf")
    count = len(doc)
    doc.close()
    return count


def rotate_pdf_page(file_content: bytes, rotation: int) -> bytes:
    """
    Retorna o conteúdo do PDF com todas as páginas rotacionadas.
    
    Args:
        file_content: Conteúdo binário do arquivo PDF
        rotation: Ângulo de rotação (90, 180, 270)
        
    Returns:
        Conteúdo binário do PDF rotacionado
    """
    doc = fitz.open(stream=file_content, filetype="pdf")
    
    for page in doc:
        page.set_rotation((page.rotation + rotation) % 360)
    
    output = BytesIO()
    doc.save(output)
    doc.close()
    
    output.seek(0)
    return output.read()


def merge_pdfs(pdf_list: list) -> tuple:
    """
    Unifica múltiplos PDFs em um único arquivo.
    
    Args:
        pdf_list: Lista de dicionários contendo:
            - content: bytes do PDF
            - rotation: rotação a aplicar (0, 90, 180, 270)
            
    Returns:
        Tuple contendo (BytesIO do PDF final, nome do arquivo, mimetype)
    """
    output_doc = fitz.open()
    
    for pdf_data in pdf_list:
        content = pdf_data['content']
        rotation = pdf_data.get('rotation', 0)
        
        # Abre o PDF fonte
        src_doc = fitz.open(stream=content, filetype="pdf")
        
        # Aplica rotação se necessário
        if rotation != 0:
            for page in src_doc:
                page.set_rotation((page.rotation + rotation) % 360)
        
        # Adiciona todas as páginas ao documento final
        output_doc.insert_pdf(src_doc)
        
        src_doc.close()
    
    # Salva o documento final
    output = BytesIO()
    output_doc.save(output)
    output_doc.close()
    
    output.seek(0)
    
    return output, "documento_unificado.pdf", "application/pdf"


def get_all_pdf_previews(file_content: bytes, zoom: float = 0.4) -> list:
    """
    Gera previews de todas as páginas do PDF.
    
    Args:
        file_content: Conteúdo binário do arquivo PDF
        zoom: Fator de zoom para as imagens
        
    Returns:
        Lista de strings base64 das imagens PNG
    """
    doc = fitz.open(stream=file_content, filetype="pdf")
    previews = []
    
    mat = fitz.Matrix(zoom, zoom)
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap(matrix=mat)
        img_bytes = pix.tobytes("png")
        previews.append(base64.b64encode(img_bytes).decode('utf-8'))
    
    doc.close()
    
    return previews


def split_pdf(file_content: bytes, split_points: list) -> list:
    """
    Separa um PDF em múltiplos arquivos baseado nos pontos de separação.
    
    Args:
        file_content: Conteúdo binário do arquivo PDF
        split_points: Lista de índices de páginas após as quais dividir (0-indexed)
        
    Returns:
        Lista de tuplas (BytesIO do PDF, nome sugerido)
    """
    doc = fitz.open(stream=file_content, filetype="pdf")
    total_pages = len(doc)
    
    # Sort split points and calculate page ranges
    sorted_splits = sorted(split_points)
    
    segments = []
    start_page = 0
    
    for split_after in sorted_splits:
        segments.append((start_page, split_after + 1))  # end is exclusive
        start_page = split_after + 1
    
    # Add final segment
    segments.append((start_page, total_pages))
    
    # Create PDFs for each segment
    result = []
    
    for idx, (start, end) in enumerate(segments):
        if start >= end:
            continue
            
        output_doc = fitz.open()
        output_doc.insert_pdf(doc, from_page=start, to_page=end - 1)
        
        output = BytesIO()
        output_doc.save(output)
        output_doc.close()
        
        output.seek(0)
        result.append((output, f"parte_{idx + 1}.pdf"))
    
    doc.close()
    
    return result
