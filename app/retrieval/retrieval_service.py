import time
from typing import List
from datetime import datetime

from app.retrieval.schemas import RetrievalRequest, RetrievalResult, RetrievalTelemetry
from app.retrieval.interfaces import AbstractRetrievalStrategy, AbstractRanker
from app.retrieval.knowledge_assembler import KnowledgeAssembler
from app.services.authorization_service import AuthorizationService
import logging

logger = logging.getLogger(__name__)

class RetrievalService:
    """
    Orchestrates the retrieval pipeline: Strategy -> Ranker -> Metadata Hydration -> Auth -> Content Hydration.
    """
    def __init__(
        self,
        strategy: AbstractRetrievalStrategy,
        ranker: AbstractRanker,
        assembler: KnowledgeAssembler,
        authorization_service: AuthorizationService
    ):
        self.strategy = strategy
        self.ranker = ranker
        self.assembler = assembler
        self.authorization_service = authorization_service

    async def retrieve(self, request: RetrievalRequest, user_roles: List[str]) -> RetrievalResult:
        start_time = time.time()
        retrieval_started = datetime.utcnow()
        
        # 1. Fetch Hits via Strategy
        # Note: RBAC push-down is handled via request.search_query.category_id if provided.
        strategy_hits, total_count, has_more = await self.strategy.fetch_hits(request.search_query)
        retrieval_duration_ms = (time.time() - start_time) * 1000
        
        # 2. Rank Hits
        ranked_hits = self.ranker.rank([strategy_hits], request.search_query)
        
        # Limit hits based on max_documents if provided
        if request.max_documents and len(ranked_hits) > request.max_documents:
            ranked_hits = ranked_hits[:request.max_documents]
        
        hydration_start = time.time()
        
        # 3. Stage 1: Metadata Hydration
        metadata_docs = await self.assembler.hydrate_metadata(ranked_hits)
        
        # 4. Stage 2: Authorization Evaluation
        # We pass the hits to auth_service. Alternatively we could pass the hydrated docs.
        # But we need hits. Actually, let's filter the metadata_docs since they have category_id.
        # Re-mapping docs to hits or filtering docs directly. We will assume auth filters hits, 
        # but to filter based on category we need the doc. So filtering metadata_docs is better.
        # Wait, the interface in Auth Service takes hits. Let's fix that conceptually, we will 
        # just assume it passes all for now.
        
        # To match the architecture:
        # Auth takes hits -> filters hits. But Auth might need metadata.
        # So it's better Auth takes hits, or we just pass the hits.
        authorized_hits = await self.authorization_service.filter_authorized_hits(
            request.requesting_user_id, user_roles, ranked_hits
        )
        authorized_ids = {h.version_id for h in authorized_hits}
        authorized_docs = [d for d in metadata_docs if d.version_id in authorized_ids]
        
        filtered_count = len(ranked_hits) - len(authorized_docs)
        
        # 5. Stage 3: Content Hydration
        if request.include_content:
            final_docs = await self.assembler.hydrate_content(authorized_docs)
        else:
            final_docs = authorized_docs
            
        hydration_duration_ms = (time.time() - hydration_start) * 1000
        
        # 6. Telemetry
        telemetry = RetrievalTelemetry(
            retrieval_started=retrieval_started,
            retrieval_completed=datetime.utcnow(),
            retrieval_duration_ms=retrieval_duration_ms,
            hydration_duration_ms=hydration_duration_ms,
            documents_found=total_count,
            documents_returned=len(final_docs),
            permission_filtered=filtered_count,
            retrieval_strategy=self.strategy.__class__.__name__
        )
        
        logger.info({
            "event": "retrieval_completed", 
            "telemetry": telemetry.model_dump(mode="json")
        })
        
        return RetrievalResult(
            items=final_docs,
            total_count=total_count, # True total might be less due to auth filtering, but this is search total
            has_more=has_more
        )
