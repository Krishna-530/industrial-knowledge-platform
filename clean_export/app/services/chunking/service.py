import logging
import hashlib
import uuid
import tiktoken
import time
from typing import List, Dict, Any
from app.services.chunking.strategy import AbstractChunkingStrategy
from database.models.document_chunk import DocumentChunk, ChunkStatus
from database.repositories.document_chunk_repository import DocumentChunkRepository

logger = logging.getLogger(__name__)

class ChunkValidationException(Exception):
    pass

class ChunkingService:
    def __init__(self, strategy: AbstractChunkingStrategy, repository: DocumentChunkRepository):
        self.strategy = strategy
        self.repository = repository
        self.encoder = tiktoken.get_encoding("cl100k_base")
        self.chunking_version = "v1"

    async def process_document(
        self, 
        document_id: uuid.UUID, 
        version_id: uuid.UUID, 
        text: str,
        base_metadata: Dict[str, Any] = None
    ) -> List[DocumentChunk]:
        
        start_time = time.perf_counter()
        logger.info({"event": "ChunkGenerationStarted", "version_id": str(version_id)})
        
        raw_chunks = self.strategy.chunk(text)
        document_chunks = []
        
        # Validation & Generation
        for idx, content in enumerate(raw_chunks):
            if not content.strip():
                continue
                
            try:
                content.encode('utf-8').decode('utf-8')
            except UnicodeError:
                logger.warning({"event": "ChunkValidationFailed", "reason": "invalid_utf8", "version_id": str(version_id)})
                continue

            token_count = len(self.encoder.encode(content))
            if token_count == 0:
                continue
                
            # Issue 2: Secure Checksum Strategy
            checksum_input = f"{version_id}:{idx}:{content}"
            checksum = hashlib.sha256(checksum_input.encode('utf-8')).hexdigest()
            
            # Issue 3 & 6: Metadata Population
            meta = {
                "chunk_index": idx,
                "token_count": token_count,
                "language": base_metadata.get("language", "unknown") if base_metadata else "unknown",
                "source_page": base_metadata.get("source_page") if base_metadata else None,
                "heading": base_metadata.get("heading") if base_metadata else None,
                "section": base_metadata.get("section_path") if base_metadata else None
            }
            
            chunk = DocumentChunk(
                document_id=document_id,
                document_version_id=version_id,
                chunk_index=idx,
                content=content,
                token_count=token_count,
                character_count=len(content),
                checksum=checksum,
                chunking_version=self.chunking_version,
                metadata_=meta,
                status=ChunkStatus.CHUNKED,
                language=meta["language"],
                source_page=meta["source_page"],
                heading=meta["heading"],
                section_path=meta["section"]
            )
            document_chunks.append(chunk)
            
        # Issue 1 & 4: Transaction Boundary & Bulk Inserts
        session = self.repository.session
        try:
            # Nested transaction allows rollback of just this phase
            async with session.begin_nested():
                # Idempotency: clear old chunks inside transaction
                deleted_count = await self.repository.delete_by_document_version(version_id)
                if deleted_count > 0:
                    logger.info({"event": "ChunkDeleted", "version_id": str(version_id), "deleted_count": deleted_count})
                
                # Bulk inserts
                batch_size = 500
                for i in range(0, len(document_chunks), batch_size):
                    batch = document_chunks[i:i + batch_size]
                    session.add_all(batch)
                    await session.flush()
                    
            await session.commit()
            logger.info({"event": "ChunkPersisted", "version_id": str(version_id), "count": len(document_chunks)})
        except Exception as e:
            logger.error({"event": "ChunkGenerationFailed", "version_id": str(version_id), "error": str(e)})
            await session.rollback()
            raise ChunkValidationException(f"Failed to persist chunks: {str(e)}")

        # Issue 9: Performance Metrics
        duration_ms = int((time.perf_counter() - start_time) * 1000)
        tokens = [c.token_count for c in document_chunks]
        avg_tokens = sum(tokens) / len(tokens) if tokens else 0
        
        logger.info({
            "event": "ChunkGenerationCompleted", 
            "version_id": str(version_id), 
            "chunk_count": len(document_chunks),
            "processing_ms": duration_ms,
            "avg_tokens": avg_tokens,
            "max_tokens": max(tokens) if tokens else 0,
            "min_tokens": min(tokens) if tokens else 0
        })
            
        return document_chunks
