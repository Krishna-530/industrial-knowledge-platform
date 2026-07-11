import logging
from typing import AsyncGenerator
from app.processing.factory import processor_factory
from app.processing.base import ProcessingResult
from core.exceptions.processing import ProcessingFailedException, UnsupportedFormatError

logger = logging.getLogger(__name__)

class ProcessingService:
    """
    Pure extraction domain service.
    Owns ONLY processor selection and stream parsing.
    Has ZERO knowledge of databases or persistence.
    """
    
    async def extract_content(self, mime_type: str, stream: AsyncGenerator[bytes, None]) -> ProcessingResult:
        try:
            processor = processor_factory.get_processor(mime_type)
        except UnsupportedFormatError as e:
            logger.info({"event": "processing_unsupported", "mime_type": mime_type})
            raise e

        try:
            logger.info({"event": "extraction_started", "processor": type(processor).__name__})
            
            result = await processor.process(stream)
            
            return result
        except Exception as e:
            logger.error({"event": "extraction_failed", "error": str(e)})
            if isinstance(e, ProcessingFailedException):
                raise e
            raise ProcessingFailedException(message=f"Extraction failed: {str(e)}")
