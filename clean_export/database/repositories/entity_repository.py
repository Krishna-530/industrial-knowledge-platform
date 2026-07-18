import unicodedata
import uuid
from typing import Optional, List, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from database.models.entity import Entity, EntityAlias
from database.models.graph_outbox import GraphOutboxEvent
from core.enums import GraphOutboxEventType, GraphOutboxEventStatus

class EntityRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def normalize_entity_name(self, name: str) -> str:
        """
        Applies Unicode NFKC normalization, removes accents, and trims whitespace.
        """
        normalized = unicodedata.normalize('NFKC', name).strip().upper()
        # Remove accents
        return ''.join(c for c in unicodedata.normalize('NFD', normalized) if unicodedata.category(c) != 'Mn')

    async def count_all(self) -> int:
        result = await self.session.execute(select(func.count(Entity.id)))
        return result.scalar() or 0

    async def get_entity_by_canonical_name(self, name: str, category: str) -> Optional[Entity]:
        normalized_name = self.normalize_entity_name(name)
        stmt = select(EntityAlias).where(
            EntityAlias.alias_name == normalized_name
        )
        result = await self.session.execute(stmt)
        alias = result.scalars().first()
        
        if alias:
            return alias.canonical_entity
            
        stmt2 = select(Entity).where(
            Entity.display_name == normalized_name,
            Entity.category == category
        )
        result2 = await self.session.execute(stmt2)
        return result2.scalars().first()

    async def upsert_entity(self, name: str, category: str, confidence: float = 1.0) -> Entity:
        """
        Creates or retrieves an entity, handling deduplication.
        Emits a GraphOutboxEvent for syncing if a new entity is created.
        """
        normalized_name = self.normalize_entity_name(name)
        
        existing_entity = await self.get_entity_by_canonical_name(name, category)
        if existing_entity:
            return existing_entity
            
        # Create new Entity
        new_entity = Entity(
            display_name=normalized_name,
            category=category,
            confidence_score=confidence,
            source_document_count=1
        )
        self.session.add(new_entity)
        await self.session.flush() # flush to get the UUID
        
        # Also create a default self-alias mapping
        alias = EntityAlias(
            canonical_id=new_entity.id,
            alias_name=normalized_name
        )
        self.session.add(alias)
        
        # Log the outbox event for Neo4j synchronization
        await self.log_outbox_event(
            event_type=GraphOutboxEventType.NODE_UPSERT,
            payload={
                "id": str(new_entity.id),
                "name": new_entity.display_name,
                "category": new_entity.category,
                "confidence": new_entity.confidence_score
            }
        )
        
        return new_entity

    async def log_outbox_event(self, event_type: GraphOutboxEventType, payload: dict) -> GraphOutboxEvent:
        event = GraphOutboxEvent(
            event_type=event_type,
            payload=payload,
            status=GraphOutboxEventStatus.PENDING,
            graph_projection_version=1
        )
        self.session.add(event)
        return event

    async def get_pending_outbox_events(self, limit: int = 100) -> List[GraphOutboxEvent]:
        stmt = select(GraphOutboxEvent).where(
            GraphOutboxEvent.status == GraphOutboxEventStatus.PENDING
        ).order_by(GraphOutboxEvent.created_at).limit(limit)
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
