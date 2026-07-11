from typing import List, Dict, Tuple
from uuid import UUID
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.retrieval.schemas import SearchHit, KnowledgeDocument
from database.models.document_version import DocumentVersion
from database.models.document_content import DocumentContent

class KnowledgeAssembler:
    """
    Responsible for hydrating search hits into KnowledgeDocument DTOs.
    Performs batched queries to avoid N+1 problems.
    """
    def __init__(self, session: AsyncSession):
        self.session = session

    async def hydrate_metadata(self, hits: List[SearchHit]) -> List[KnowledgeDocument]:
        """
        Stage 1 Hydration: Fetches metadata without full document bodies.
        Returns partially hydrated KnowledgeDocument objects (full_content=None).
        """
        if not hits:
            return []
            
        version_ids = [hit.version_id for hit in hits]
        
        # Batch fetch versions with their parent document
        stmt = (
            select(DocumentVersion)
            .where(DocumentVersion.id.in_(version_ids))
            .options(selectinload(DocumentVersion.document))
        )
        result = await self.session.execute(stmt)
        versions_by_id = {v.id: v for v in result.scalars().all()}
        
        documents = []
        for hit in hits:
            version = versions_by_id.get(hit.version_id)
            if not version:
                continue # Edge case: deleted after indexing
                
            doc_record = version.document
            
            # Convert tags to a simple string list if available (already selectin-loaded in Document)
            tags = [tag.name for tag in getattr(doc_record, "tags", [])]
            metadata = {
                "category_id": str(doc_record.category_id),
                "tags": tags,
                "document_status": doc_record.status.value,
                "owner_id": str(doc_record.owner_id)
            }
            
            documents.append(KnowledgeDocument(
                document_id=hit.document_id,
                version_id=hit.version_id,
                title=doc_record.title,
                metadata=metadata,
                highlight=hit.highlight,
                full_content=None,
                score=hit.score,
                language=hit.language,
                version_number=version.version_number,
                indexed_at=None, # Future implementation or joined from DocumentContent
                retrieved_at=datetime.utcnow(),
                source_uri=version.storage_identifier,
                provider_name="PostgresFTS"
            ))
            
        return documents

    async def hydrate_content(self, documents: List[KnowledgeDocument]) -> List[KnowledgeDocument]:
        """
        Stage 3 Hydration: Fetches full content for authorized documents.
        Modifies documents in-place and returns them.
        """
        if not documents:
            return []
            
        version_ids = [doc.version_id for doc in documents]
        stmt = select(DocumentContent).where(DocumentContent.document_version_id.in_(version_ids))
        result = await self.session.execute(stmt)
        contents_by_version_id = {c.document_version_id: c for c in result.scalars().all()}
        
        for doc in documents:
            content_record = contents_by_version_id.get(doc.version_id)
            if content_record and content_record.raw_text:
                doc.full_content = content_record.raw_text
                doc.indexed_at = content_record.updated_at or content_record.created_at
                
        return documents
