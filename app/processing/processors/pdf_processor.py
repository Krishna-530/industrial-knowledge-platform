import tempfile
from typing import AsyncGenerator
from app.processing.base import DocumentProcessor, ProcessingResult
from core.exceptions.processing import ProcessingFailedException

class PdfProcessor(DocumentProcessor):
    def supports(self, mime_type: str) -> bool:
        return mime_type == "application/pdf"

    async def process(self, file_stream: AsyncGenerator[bytes, None]) -> ProcessingResult:
        with tempfile.SpooledTemporaryFile(max_size=5_000_000, mode='w+b') as spooled_file:
            async for chunk in file_stream:
                spooled_file.write(chunk)
                
            spooled_file.seek(0)
            
            try:
                import PyPDF2 as pypdf
            except ImportError:
                raise ProcessingFailedException("pypdf is required for PDF extraction but is not installed.")
                
            try:
                reader = pypdf.PdfReader(spooled_file)
                
                raw_text_parts = []
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        raw_text_parts.append(text)
                        
                raw_text = "\n\n".join(raw_text_parts)
                
                page_count = len(reader.pages)
                character_count = len(raw_text)
                word_count = len(raw_text.split())
                
                document_metadata = {}
                if reader.metadata:
                    document_metadata = {k: str(v) for k, v in reader.metadata.items()}
                    
                processing_metadata = {
                    "parser_library": "pypdf",
                    "parser_version": pypdf.__version__
                }
                
                return ProcessingResult(
                    raw_text=raw_text,
                    page_count=page_count,
                    word_count=word_count,
                    character_count=character_count,
                    document_metadata=document_metadata,
                    processing_metadata=processing_metadata,
                    detected_language=None
                )
            except Exception as e:
                raise ProcessingFailedException(f"Failed to process PDF: {str(e)}")
