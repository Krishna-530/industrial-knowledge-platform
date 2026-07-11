import tempfile
from typing import AsyncGenerator
from app.processing.base import DocumentProcessor, ProcessingResult
from core.exceptions.processing import ProcessingFailedException

class DocxProcessor(DocumentProcessor):
    def supports(self, mime_type: str) -> bool:
        return mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

    async def process(self, file_stream: AsyncGenerator[bytes, None]) -> ProcessingResult:
        with tempfile.SpooledTemporaryFile(max_size=5_000_000, mode='w+b') as spooled_file:
            async for chunk in file_stream:
                spooled_file.write(chunk)
                
            spooled_file.seek(0)
            
            try:
                import docx
            except ImportError:
                raise ProcessingFailedException("python-docx is required for DOCX extraction but is not installed.")
                
            try:
                doc = docx.Document(spooled_file)
                
                raw_text_parts = [para.text for para in doc.paragraphs if para.text]
                raw_text = "\n\n".join(raw_text_parts)
                
                character_count = len(raw_text)
                word_count = len(raw_text.split())
                
                document_metadata = {}
                if doc.core_properties:
                    props = doc.core_properties
                    document_metadata = {
                        "author": props.author,
                        "title": props.title,
                        "subject": props.subject,
                        "category": props.category,
                        "keywords": props.keywords
                    }
                    document_metadata = {k: v for k, v in document_metadata.items() if v}
                    
                processing_metadata = {
                    "parser_library": "python-docx",
                    "parser_version": docx.__version__
                }
                
                return ProcessingResult(
                    raw_text=raw_text,
                    page_count=None,
                    word_count=word_count,
                    character_count=character_count,
                    document_metadata=document_metadata,
                    processing_metadata=processing_metadata,
                    detected_language=None
                )
            except Exception as e:
                raise ProcessingFailedException(f"Failed to process DOCX: {str(e)}")
