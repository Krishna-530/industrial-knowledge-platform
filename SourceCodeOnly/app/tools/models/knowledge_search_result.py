from typing import List, Dict, Any
from pydantic import BaseModel

class KnowledgeSearchResult(BaseModel):
    chunks: List[Any]
    citations: List[Dict[str, Any]]
    retrieval_metadata: Dict[str, Any]
    
    def __str__(self):
        # Tools return objects that get serialized or cast to string
        # Since the PromptWorkflow formats it later, we just dump the JSON for the LLM 
        # or rely on PromptWorkflow parsing tool call results.
        return self.model_dump_json()
