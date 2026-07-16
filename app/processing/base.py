from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Dict, AsyncGenerator

@dataclass
class ProcessingResult:
    raw_text: str
    page_count: Optional[int]
    word_count: Optional[int]
    character_count: Optional[int]
    document_metadata: Optional[Dict]
    processing_metadata: Optional[Dict]
    detected_language: Optional[str]

class DocumentProcessor(ABC):
    """
    Abstract interface for all document processors.
    Processors must have zero knowledge of databases, storage, or APIs.
    """
    
    @abstractmethod
    def supports(self, mime_type: str) -> bool:
        """Returns True if the processor supports the given MIME type."""

    @abstractmethod
    async def process(self, file_stream: AsyncGenerator[bytes, None]) -> ProcessingResult:
        """
        Consumes an async byte stream and returns extracted content and metadata.
        """
