from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database.engine import get_db_session
from app.services.chunking.service import ChunkingService
from app.services.chunking.strategy import RecursiveChunkingStrategy
from database.repositories.document_chunk_repository import DocumentChunkRepository

def provide_chunking_service(session: AsyncSession = Depends(get_db_session)) -> ChunkingService:
    strategy = RecursiveChunkingStrategy()
    repository = DocumentChunkRepository(session)
    return ChunkingService(strategy=strategy, repository=repository)
