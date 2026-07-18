from typing import Dict, List
from app.processing.base import DocumentProcessor
from core.exceptions import UnsupportedFormatError

class ProcessorFactory:
    """
    Factory for selecting document processors based on MIME type.
    Uses dynamic registration to avoid if/else chains.
    """
    def __init__(self):
        self._registry: Dict[str, DocumentProcessor] = {}

    def register(self, mime_type: str, processor: DocumentProcessor) -> None:
        """Registers a processor instance for a specific MIME type."""
        self._registry[mime_type] = processor

    def unregister(self, mime_type: str) -> None:
        """Safely removes a registered processor."""
        self._registry.pop(mime_type, None)

    def supported_types(self) -> List[str]:
        """Returns a list of all supported MIME types."""
        return list(self._registry.keys())

    def get_processor(self, mime_type: str) -> DocumentProcessor:
        """
        Retrieves the appropriate processor.
        Raises UnsupportedFormatError if none is found.
        """
        processor = self._registry.get(mime_type)
        if not processor:
            raise UnsupportedFormatError(message=f"No processor registered for MIME type: {mime_type}")
        return processor

# Global factory instance
processor_factory = ProcessorFactory()
