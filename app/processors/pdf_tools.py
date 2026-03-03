# -*- coding: utf-8 -*-
"""
PDF Tools Processors - Strategy implementation for PDF operations.
"""
from typing import List
from io import BytesIO
import base64
import zipfile
from app.processors.base import FileProcessor, ProcessResult, ProcessorRegistry

# Import existing PDF functions
from app.utils.pdf_merger import (
    get_pdf_preview,
    get_pdf_page_count,
    merge_pdfs,
    get_all_pdf_previews,
    split_pdf,
    extract_pages,
    split_by_range,
    parse_page_range
)


@ProcessorRegistry.register('pdf_merger')
class PDFMergerProcessor(FileProcessor):
    """
    Processor for merging multiple PDFs into one.
    """
    
    name = "pdf_merger"
    description = "Unifica múltiplos PDFs em um único arquivo"
    supported_formats = ['.pdf']
    
    def validate(self, file, options: dict = None) -> tuple:
        """
        For merger, validation is different - we validate list of files.
        """
        options = options or {}
        files = options.get('files', [])
        
        if len(files) < 2:
            return False, "É necessário pelo menos 2 arquivos para unificar"
        
        return True, None
    
    def process(self, file, options: dict = None) -> ProcessResult:
        """
        Merge multiple PDFs.
        
        Options:
            files: List of dicts with 'content' (base64) and 'rotation' keys
        """
        options = options or {}
        files = options.get('files', [])
        
        if len(files) < 2:
            return ProcessResult.failure("É necessário pelo menos 2 arquivos")
        
        try:
            # Calculate original total size
            original_size = 0
            pdf_list = []
            
            for file_data in files:
                content = base64.b64decode(file_data['content'])
                original_size += len(content)
                rotation = file_data.get('rotation', 0)
                pdf_list.append({'content': content, 'rotation': rotation})
            
            # Merge PDFs
            output, filename, mimetype = merge_pdfs(pdf_list)
            
            output.seek(0, 2)
            processed_size = output.tell()
            output.seek(0)
            
            return ProcessResult(
                success=True,
                output=output,
                filename=filename,
                mimetype=mimetype,
                original_size=original_size,
                processed_size=processed_size,
                metadata={
                    'files_merged': len(files),
                    'operation': 'merge'
                }
            )
        except Exception as e:
            return ProcessResult.failure(str(e))
    
    def get_preview(self, file_content: bytes, page_number: int = 0, zoom: float = 0.5) -> str:
        """Get base64 preview of a PDF page."""
        return get_pdf_preview(file_content, page_number, zoom)
    
    def get_page_count(self, file_content: bytes) -> int:
        """Get number of pages in a PDF."""
        return get_pdf_page_count(file_content)


@ProcessorRegistry.register('pdf_splitter')
class PDFSplitterProcessor(FileProcessor):
    """
    Processor for splitting a PDF into multiple files.
    Supports multiple modes: select, markers, range.
    """
    
    name = "pdf_splitter"
    description = "Separa um PDF em múltiplos arquivos"
    supported_formats = ['.pdf']
    
    def validate(self, file, options: dict = None) -> tuple:
        options = options or {}
        content = options.get('content')
        
        if not content:
            return False, "Conteúdo do PDF não fornecido"
        
        return True, None
    
    def process(self, file, options: dict = None) -> ProcessResult:
        """
        Split PDF with multiple modes.
        
        Options:
            content: Base64 encoded PDF content
            mode: 'select', 'markers', or 'range'
            selected_pages: List of pages to extract (mode=select)
            split_points: List of page numbers after which to split (mode=markers)
            pages_per_file: Number of pages per file (mode=range)
            page_range: Range string like "1-3, 5, 7-10" (mode=range)
            filename: Original filename for naming parts
        """
        options = options or {}
        content = base64.b64decode(options.get('content', ''))
        mode = options.get('mode', 'markers')
        original_filename = options.get('filename', 'documento')
        
        if not content:
            return ProcessResult.failure("Conteúdo do PDF não fornecido")
        
        try:
            original_size = len(content)
            base_name = original_filename.replace('.pdf', '').replace('.PDF', '')
            total_pages = get_pdf_page_count(content)
            
            if mode == 'select':
                # Extract selected pages into a single PDF
                selected_pages = options.get('selected_pages', [])
                if not selected_pages:
                    return ProcessResult.failure("Nenhuma página selecionada")
                
                output = extract_pages(content, selected_pages)
                output.seek(0, 2)
                processed_size = output.tell()
                output.seek(0)
                
                return ProcessResult(
                    success=True,
                    output=output,
                    filename=f"{base_name}_extraido.pdf",
                    mimetype='application/pdf',
                    original_size=original_size,
                    processed_size=processed_size,
                    metadata={
                        'pages_extracted': len(selected_pages),
                        'operation': 'extract'
                    }
                )
            
            elif mode == 'range':
                # Split by pages per file or custom range
                pages_per_file = options.get('pages_per_file')
                page_range = options.get('page_range', '')
                
                if page_range:
                    # Extract pages from range string
                    pages = parse_page_range(page_range, total_pages)
                    if not pages:
                        return ProcessResult.failure("Range de páginas inválido")
                    
                    output = extract_pages(content, pages)
                    output.seek(0, 2)
                    processed_size = output.tell()
                    output.seek(0)
                    
                    return ProcessResult(
                        success=True,
                        output=output,
                        filename=f"{base_name}_extraido.pdf",
                        mimetype='application/pdf',
                        original_size=original_size,
                        processed_size=processed_size,
                        metadata={
                            'pages_extracted': len(pages),
                            'operation': 'extract_range'
                        }
                    )
                elif pages_per_file and pages_per_file > 0:
                    # Split into multiple files
                    pdf_parts = split_by_range(content, pages_per_file)
                    
                    if len(pdf_parts) == 1:
                        # Only one part, return as PDF
                        output = pdf_parts[0][0]
                        output.seek(0, 2)
                        processed_size = output.tell()
                        output.seek(0)
                        
                        return ProcessResult(
                            success=True,
                            output=output,
                            filename=f"{base_name}.pdf",
                            mimetype='application/pdf',
                            original_size=original_size,
                            processed_size=processed_size,
                            metadata={
                                'operation': 'split_range'
                            }
                        )
                    
                    # Multiple parts - create ZIP
                    zip_buffer = BytesIO()
                    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                        for idx, (pdf_io, _) in enumerate(pdf_parts):
                            pdf_io.seek(0)
                            zip_file.writestr(f"{base_name}_parte_{idx + 1}.pdf", pdf_io.read())
                    
                    zip_buffer.seek(0, 2)
                    processed_size = zip_buffer.tell()
                    zip_buffer.seek(0)
                    
                    return ProcessResult(
                        success=True,
                        output=zip_buffer,
                        filename=f"{base_name}_separado.zip",
                        mimetype='application/zip',
                        original_size=original_size,
                        processed_size=processed_size,
                        metadata={
                            'parts_created': len(pdf_parts),
                            'pages_per_file': pages_per_file,
                            'operation': 'split_range'
                        }
                    )
                else:
                    return ProcessResult.failure("Especifique páginas por arquivo ou um range")
            
            else:  # mode == 'markers'
                # Split at specified marker points
                split_points = options.get('split_points', [])
                if not split_points:
                    return ProcessResult.failure("Nenhum ponto de separação definido")
                
                # Convert 1-indexed to 0-indexed
                split_points_0idx = [p - 1 for p in split_points if 0 < p < total_pages]
                
                if not split_points_0idx:
                    return ProcessResult.failure("Nenhum ponto de separação válido")
                
                pdf_parts = split_pdf(content, split_points_0idx)
                
                if len(pdf_parts) == 1:
                    # Only one part, return as PDF
                    output = pdf_parts[0][0]
                    output.seek(0, 2)
                    processed_size = output.tell()
                    output.seek(0)
                    
                    return ProcessResult(
                        success=True,
                        output=output,
                        filename=f"{base_name}.pdf",
                        mimetype='application/pdf',
                        original_size=original_size,
                        processed_size=processed_size,
                        metadata={
                            'operation': 'split_markers'
                        }
                    )
                
                # Multiple parts - create ZIP
                zip_buffer = BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    for idx, (pdf_io, _) in enumerate(pdf_parts):
                        pdf_io.seek(0)
                        zip_file.writestr(f"{base_name}_parte_{idx + 1}.pdf", pdf_io.read())
                
                zip_buffer.seek(0, 2)
                processed_size = zip_buffer.tell()
                zip_buffer.seek(0)
                
                return ProcessResult(
                    success=True,
                    output=zip_buffer,
                    filename=f"{base_name}_separado.zip",
                    mimetype='application/zip',
                    original_size=original_size,
                    processed_size=processed_size,
                    metadata={
                        'parts_created': len(pdf_parts),
                        'split_points': split_points,
                        'operation': 'split_markers'
                    }
                )
                
        except Exception as e:
            return ProcessResult.failure(str(e))
    
    def get_all_previews(self, file_content: bytes, zoom: float = 0.4) -> list:
        """Get previews of all pages in a PDF."""
        return get_all_pdf_previews(file_content, zoom)
    
    def get_page_count(self, file_content: bytes) -> int:
        """Get number of pages in a PDF."""
        return get_pdf_page_count(file_content)
