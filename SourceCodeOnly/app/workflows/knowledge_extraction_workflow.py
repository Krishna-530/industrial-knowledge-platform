import logging
from typing import List
from app.extraction.interfaces import AbstractKnowledgeExtractor

logger = logging.getLogger(__name__)

class KnowledgeExtractionWorkflow:
    def __init__(self, extractor: AbstractKnowledgeExtractor):
        self.extractor = extractor
        
    async def run_extraction(self, chunks: List[dict]) -> List[dict]:
        """
        Process chunks and extract facts.
        chunks: List of dictionaries with 'id' and 'text'. Assumes ordered.
        Returns a list of extracted facts ready for DB persistence.
        """
        all_facts = []
        
        for i, chunk in enumerate(chunks):
            current_text = chunk.get("text", "")
            current_id = chunk.get("id")
            
            # Context window: Previous Chunk + Current Chunk
            previous_text = chunks[i-1].get("text", "") if i > 0 else None
            
            try:
                extracted_facts = await self.extractor.extract(
                    current_chunk_text=current_text,
                    current_chunk_id=current_id,
                    previous_chunk_text=previous_text
                )
                
                # Append metadata
                for fact in extracted_facts:
                    all_facts.append({
                        "chunk_id": current_id,
                        "asset_id": fact.asset_id,
                        "property": fact.property,
                        "value": fact.value,
                        "start_offset": fact.start_offset,
                        "end_offset": fact.end_offset,
                        # the model and version would ideally be exposed from extractor
                        # we'll assume the persistence layer or caller fills in document_id
                    })
            except Exception as e:
                logger.error(f"Failed to extract facts for chunk {current_id}: {e}")
                # We do not fail the whole document if one chunk fails, 
                # but depending on business rules, we might want to.
                
        return all_facts
