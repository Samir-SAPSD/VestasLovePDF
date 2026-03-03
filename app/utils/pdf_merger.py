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

def extract_pages(file_content: bytes, page_numbers: list) -> BytesIO:
    """
    Extract specific pages from a PDF into a new PDF.
    
    Args:
        file_content: Binary content of PDF file
        page_numbers: List of page numbers to extract (1-indexed)
        
    Returns:
        BytesIO with extracted pages PDF
    """
    doc = fitz.open(stream=file_content, filetype="pdf")
    output_doc = fitz.open()
    
    # Convert to 0-indexed and sort
    pages_0indexed = sorted([p - 1 for p in page_numbers if 0 < p <= len(doc)])
    
    for page_num in pages_0indexed:
        output_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
    
    output = BytesIO()
    output_doc.save(output)
    output_doc.close()
    doc.close()
    
    output.seek(0)
    return output


def split_by_range(file_content: bytes, pages_per_file: int) -> list:
    """
    Split a PDF into multiple files with a fixed number of pages each.
    
    Args:
        file_content: Binary content of PDF file
        pages_per_file: Number of pages per output file
        
    Returns:
        List of tuples (BytesIO of PDF, suggested name)
    """
    doc = fitz.open(stream=file_content, filetype="pdf")
    total_pages = len(doc)
    result = []
    
    for start in range(0, total_pages, pages_per_file):
        end = min(start + pages_per_file, total_pages)
        
        output_doc = fitz.open()
        output_doc.insert_pdf(doc, from_page=start, to_page=end - 1)
        
        output = BytesIO()
        output_doc.save(output)
        output_doc.close()
        
        output.seek(0)
        part_num = (start // pages_per_file) + 1
        result.append((output, f"parte_{part_num}.pdf"))
    
    doc.close()
    return result


def parse_page_range(range_str: str, total_pages: int) -> list:
    """
    Parse a page range string like "1-3, 5, 7-10" into a list of page numbers.
    
    Args:
        range_str: Range string
        total_pages: Total number of pages in the PDF
        
    Returns:
        List of page numbers (1-indexed)
    """
    pages = set()
    
    for part in range_str.split(','):
        part = part.strip()
        if not part:
            continue
            
        if '-' in part:
            try:
                start, end = part.split('-')
                start = int(start.strip())
                end = int(end.strip())
                for p in range(start, min(end + 1, total_pages + 1)):
                    if p > 0:
                        pages.add(p)
            except ValueError:
                continue
        else:
            try:
                p = int(part)
                if 0 < p <= total_pages:
                    pages.add(p)
            except ValueError:
                continue
    
    return sorted(list(pages))