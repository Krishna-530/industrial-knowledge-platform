import tempfile
from typing import AsyncGenerator
from app.processing.base import DocumentProcessor, ProcessingResult
from core.exceptions.processing import ProcessingFailedException

class MarkdownProcessor(DocumentProcessor):
    def supports(self, mime_type: str) -> bool:
        return mime_type in ("text/markdown", "text/x-markdown")

    async def process(self, file_stream: AsyncGenerator[bytes, None]) -> ProcessingResult:
        with tempfile.SpooledTemporaryFile(max_size=5_000_000, mode='w+b') as spooled_file:
            async for chunk in file_stream:
                spooled_file.write(chunk)
            
            spooled_file.seek(0)
            raw_bytes = spooled_file.read()
            raw_text = raw_bytes.decode('utf-8', errors='replace')
            
            character_count = len(raw_text)
            word_count = len(raw_text.split())
            try:
                raw_bytes = spooled_file.read()
                raw_text = raw_bytes.decode('utf-8', errors='replace')
                
                character_count = len(raw_text)
                word_count = len(raw_text.split())
                
                return ProcessingResult(
                    raw_text=raw_text,
                    page_count=None,
                    word_count=word_count,
                    character_count=character_count,
                    document_metadata={},
                    processing_metadata={"parser_library": "built-in", "parser_version": "1.0"},
                    detected_language=None
                )
            except Exception as e:
                raise ProcessingFailedException(f"Failed to process Markdown: {str(e)}")
