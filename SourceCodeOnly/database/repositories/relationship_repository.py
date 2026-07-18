import uuid
import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from database.models.relationship import Relationship, RelationshipEvidence, RelationshipStatus
from app.services.relationship_quality_service import RelationshipQualityService
from database.models.graph_outbox import GraphOutboxEvent, GraphOutboxEventType

logger = logging.getLogger(__name__)

class RelationshipRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def count_all(self) -> int:
        result = await self.session.execute(select(func.count(Relationship.id)))
        return result.scalar() or 0

    async def upsert_relationship(
        self,
        subject_id: uuid.UUID,
        predicate: str,
        object_id: uuid.UUID,
        chunk_id: uuid.UUID,
        confidence: float,
        supporting_text: str,
        metadata: Optional[dict] = None
    ) -> Relationship:
        
        # 1. Lookup existing Relationship
        stmt = select(Relationship).where(
            Relationship.subject_id == subject_id,
            Relationship.predicate == predicate,
            Relationship.object_id == object_id
        )
        result = await self.session.execute(stmt)
        relationship = result.scalar_one_or_none()
        
        if not relationship:
            # Create new canonical edge
            relationship = Relationship(
                subject_id=subject_id,
                predicate=predicate,
                object_id=object_id,
                quality_score=0.0,
                status=RelationshipStatus.DISCOVERED
            )
            self.session.add(relationship)
            await self.session.flush() # flush to get ID
            
        # 2. Add Evidence
        evidence = RelationshipEvidence(
            relationship_id=relationship.id,
            chunk_id=chunk_id,
            confidence=confidence,
            supporting_text=supporting_text,
            metadata_json=metadata
        )
        self.session.add(evidence)
        await self.session.flush()
        
        # 3. Calculate Quality Score
        evidence_count_stmt = select(func.count(RelationshipEvidence.id)).where(RelationshipEvidence.relationship_id == relationship.id)
        evidence_count = (await self.session.execute(evidence_count_stmt)).scalar()
        
        new_quality = RelationshipQualityService.calculate_score(
            base_confidence=confidence,
            evidence_count=evidence_count,
            provider_reliability_weight=1.0 # Could be dynamic based on provider
        )
        
        relationship.quality_score = new_quality
        if new_quality >= 0.7:
            relationship.status = RelationshipStatus.ACTIVE
            
        # 4. Emit Outbox Event (so Neo4j gets it)
        # We wrap it in EDGE_UPSERT
        payload = {
            "relationship_id": str(relationship.id),
            "subject_id": str(relationship.subject_id),
            "predicate": relationship.predicate,
            "object_id": str(relationship.object_id),
            "quality_score": relationship.quality_score,
            "status": relationship.status.value
        }
        
        outbox_event = GraphOutboxEvent(
            event_type=GraphOutboxEventType.EDGE_UPSERT,
            payload=payload
        )
        self.session.add(outbox_event)
        
        return relationship
