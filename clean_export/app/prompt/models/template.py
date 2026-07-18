from pydantic import BaseModel
from typing import List
from uuid import UUID
from datetime import datetime

class PromptVersion(BaseModel):
    major: int
    minor: int
    deprecated: bool
    created_at: datetime

class PromptTemplate(BaseModel):
    id: UUID
    version: PromptVersion
    description: str
    renderer: str
    variables: List[str]
    file_path: str
    checksum: str
