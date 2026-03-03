# -*- coding: utf-8 -*-
"""
Base classes for file processors using Strategy Pattern.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, List, Optional, Dict
from io import BytesIO


@dataclass
class ProcessResult:
    """
    Standardized result from file processing operations.
    
    Attributes:
        success: Whether the operation was successful
        output: BytesIO output file (if applicable)
        filename: Output filename
        mimetype: MIME type of output file
        original_size: Original file size in bytes
        processed_size: Processed file size in bytes
        metadata: Additional metadata about the operation
        error: Error message if success is False
    """
    success: bool
    output: Optional[BytesIO] = None
    filename: Optional[str] = None
    mimetype: Optional[str] = None
    original_size: int = 0
    processed_size: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    
    @property
    def compression_ratio(self) -> float:
        """Returns compression ratio as percentage."""
        if self.original_size > 0:
            return ((self.original_size - self.processed_size) / self.original_size) * 100
        return 0.0
    
    @classmethod
    def failure(cls, error: str) -> 'ProcessResult':
        """Factory method for failed results."""
        return cls(success=False, error=error)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for API response."""
        result = {
            'success': self.success,
            'filename': self.filename,
            'mimetype': self.mimetype,
            'original_size': self.original_size,
            'processed_size': self.processed_size,
            'compression_ratio': round(self.compression_ratio, 2)
        }
        if self.metadata:
            result['metadata'] = self.metadata
        if self.error:
            result['error'] = self.error
        return result


class FileProcessor(ABC):
    """
    Abstract base class for all file processors.
    Implements the Strategy pattern for different file operations.
    """
    
    # Override in subclasses
    name: str = "base"
    description: str = "Base processor"
    supported_formats: List[str] = []
    
    @abstractmethod
    def validate(self, file, options: dict = None) -> tuple:
        """
        Validate if the file can be processed.
        
        Args:
            file: File object from request.files
            options: Processing options
            
        Returns:
            Tuple of (is_valid: bool, error_message: str or None)
        """
        pass
    
    @abstractmethod
    def process(self, file, options: dict = None) -> ProcessResult:
        """
        Process the file and return result.
        
        Args:
            file: File object from request.files
            options: Processing options
            
        Returns:
            ProcessResult with output file and metadata
        """
        pass
    
    def get_supported_formats(self) -> List[str]:
        """Returns list of supported file formats."""
        return self.supported_formats
    
    def get_file_extension(self, filename: str) -> str:
        """Extract file extension from filename."""
        import os
        return os.path.splitext(filename)[1].lower()
    
    def get_file_size(self, file) -> int:
        """Get file size in bytes."""
        file.seek(0, 2)
        size = file.tell()
        file.seek(0)
        return size


class ProcessorRegistry:
    """
    Registry for file processors.
    Implements Plugin Architecture pattern.
    
    Usage:
        @ProcessorRegistry.register('compressor')
        class CompressorProcessor(FileProcessor):
            ...
        
        # Get processor
        processor = ProcessorRegistry.get('compressor')
    """
    
    _processors: Dict[str, type] = {}
    
    @classmethod
    def register(cls, name: str):
        """
        Decorator to register a processor.
        
        Args:
            name: Unique name for the processor
        """
        def decorator(processor_class: type):
            if not issubclass(processor_class, FileProcessor):
                raise TypeError(f"{processor_class.__name__} must inherit from FileProcessor")
            cls._processors[name] = processor_class
            return processor_class
        return decorator
    
    @classmethod
    def get(cls, name: str) -> FileProcessor:
        """
        Get an instance of a registered processor.
        
        Args:
            name: Processor name
            
        Returns:
            Instance of the processor
            
        Raises:
            KeyError: If processor not found
        """
        if name not in cls._processors:
            raise KeyError(f"Processor '{name}' not found. Available: {list(cls._processors.keys())}")
        return cls._processors[name]()
    
    @classmethod
    def list_all(cls) -> Dict[str, dict]:
        """
        List all registered processors with their info.
        
        Returns:
            Dict with processor info
        """
        return {
            name: {
                'name': proc.name,
                'description': proc.description,
                'supported_formats': proc.supported_formats
            }
            for name, proc in cls._processors.items()
        }
    
    @classmethod
    def has(cls, name: str) -> bool:
        """Check if a processor is registered."""
        return name in cls._processors
