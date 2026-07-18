from typing import List, Optional
from pydantic import BaseModel, Field

class ExtractedEntity(BaseModel):
    name: str = Field(..., description="The name of the entity. Max length 100.", max_length=100)
    category: str = Field(..., description="Category of the entity (e.g. PERSON, ORGANIZATION, LOCATION, ASSET, CONCEPT)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score from 0.0 to 1.0")

class ExtractedEntityCollection(BaseModel):
    entities: List[ExtractedEntity] = Field(default_factory=list, description="List of extracted entities in this chunk")

class ExtractedRelationship(BaseModel):
    subject_name: str = Field(..., description="Name of the source entity")
    subject_category: str = Field(..., description="Category of the source entity")
    predicate: str = Field(..., description="Directional relationship type (e.g. LOCATED_IN, CAUSES, PRODUCES)")
    object_name: str = Field(..., description="Name of the target entity")
    object_category: str = Field(..., description="Category of the target entity")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score from 0.0 to 1.0")

class ExtractedRelationshipCollection(BaseModel):
    relationships: List[ExtractedRelationship] = Field(default_factory=list, description="List of extracted relationships in this chunk")
