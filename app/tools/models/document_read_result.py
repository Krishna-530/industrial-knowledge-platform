from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class DocumentReadResult(BaseModel):
    document_id: str
    text_content: Optional[str] = None
    tables: List[Dict[str, Any]] = []
    metadata: Dict[str, Any] = {}
    citations: List[Dict[str, Any]] = []
    has_more: bool = False
    
    def __str__(self):
        return self.model_dump_json()
