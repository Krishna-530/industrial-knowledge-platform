import time
import logging
from datetime import datetime
from typing import List, Dict

from app.retrieval.schemas import KnowledgeDocument
from app.context.schemas import ContextConfig, ContextPayload, AssemblyReport, ContextFormat
from app.context.interfaces import AbstractContextFormatter
from app.context.pipeline.chunk_extractor import ChunkExtractor
from app.context.pipeline.chunk_selector import ChunkSelector
from app.context.pipeline.context_compressor import ContextCompressor
from app.context.pipeline.context_ranker import ContextRanker
from app.context.pipeline.context_budgeter import ContextBudgeter

logger = logging.getLogger(__name__)

class ContextService:
    """
    Orchestrates the 5-step pipeline for Context Assembly Engine.
    """
    def __init__(
        self,
        extractor: ChunkExtractor,
        selector: ChunkSelector,
        compressor: ContextCompressor,
        ranker: ContextRanker,
        budgeter: ContextBudgeter,
        formatters: Dict[ContextFormat, AbstractContextFormatter]
    ):
        self.extractor = extractor
        self.selector = selector
        self.compressor = compressor
        self.ranker = ranker
        self.budgeter = budgeter
        self.formatters = formatters

    def assemble(self, documents: List[KnowledgeDocument], config: ContextConfig) -> ContextPayload:
        start_time = time.time()
        
        formatter = self.formatters.get(config.formatter)
        if not formatter:
            raise ValueError(f"Formatter {config.formatter} not found")
            
        # 1. Extraction (Bridge) & Selection
        extracted_chunks = self.extractor.extract(documents)
        selected_chunks = self.selector.select(extracted_chunks)
        total_extracted = len(selected_chunks)
        
        # 2. Compression
        if config.compression_enabled:
            compressed_chunks, duplicates_omitted = self.compressor.compress(selected_chunks)
        else:
            compressed_chunks = selected_chunks
            duplicates_omitted = 0
            
        # 3. Ranking
        ranked_chunks = self.ranker.rank(compressed_chunks, config.ordering_strategy)
        
        # 4. Budgeting
        final_chunks, estimated_tokens, budget_omitted = self.budgeter.enforce_budget(ranked_chunks, config)
        
        # 5. Formatting
        formatted_context = formatter.format_chunks(final_chunks)
        
        # Metrics
        duration_ms = (time.time() - start_time) * 1000
        compression_ratio = 1.0 - (len(final_chunks) / total_extracted) if total_extracted > 0 else 0.0
        
        report = AssemblyReport(
            total_chunks_extracted=total_extracted,
            chunks_omitted_duplicates=duplicates_omitted,
            chunks_omitted_budget=budget_omitted,
            final_chunk_count=len(final_chunks),
            compression_ratio=compression_ratio,
            reasons=[]
        )
        
        payload = ContextPayload(
            context=formatted_context,
            estimated_tokens=estimated_tokens,
            token_counter=self.budgeter.token_counter.__class__.__name__,
            assembly_duration_ms=duration_ms,
            generated_at=datetime.utcnow(),
            report=report
        )
        
        logger.info({"event": "context_assembly_complete", "payload": payload.model_dump(mode="json")})
        return payload
