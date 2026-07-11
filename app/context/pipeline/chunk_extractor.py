import uuid
from typing import List
from app.retrieval.schemas import KnowledgeDocument
from app.context.schemas import ContextChunk

class ChunkExtractor:
    """
    Temporary bridge.
    Extracts simulated chunks from a whole KnowledgeDocument.
    When Retrieval directly returns chunks in Phase 7+, this layer will be bypassed.
    """
    def extract(self, docs: List[KnowledgeDocument]) -> List[ContextChunk]:
        chunks = []
        for doc in docs:
            # Simulated extraction: Treat the entire document content as 1 chunk for now, 
            # or split by basic paragraphs. 
            # To keep things simple and robust for this phase, we map 1 doc -> 1 chunk.
            
            content = doc.full_content or doc.highlight or ""
            
            chunk = ContextChunk(
                chunk_id=uuid.uuid4(),
                document_id=doc.document_id,
                version_id=doc.version_id,
                source_uri=doc.source_uri,
                page_number=None,
                section="Document Body",
                content=content,
                score=doc.score,
                token_estimate=0, # populated later
                chunk_index=0,
                retrieval_strategy="Simulated Whole Doc",
                rank_score=doc.score
            )
            chunks.append(chunk)
            
        return chunks
