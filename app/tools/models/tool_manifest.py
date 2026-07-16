from enum import Enum
from typing import Dict, Any, List
from pydantic import BaseModel, Field

class ToolCategory(str, Enum):
    KNOWLEDGE = "KNOWLEDGE"
    SEARCH = "SEARCH"
    WORKSPACE = "WORKSPACE"
    CONVERSATION = "CONVERSATION"
    UTILITY = "UTILITY"
    SYSTEM = "SYSTEM"
    EXTERNAL = "EXTERNAL"
    MCP = "MCP"
    AGENT = "AGENT"

class ToolManifest(BaseModel):
    id: str
    version: str = "1.0.0"
    display_name: str
    description: str
    category: ToolCategory
    permissions: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    supports_streaming: bool = False
    supports_parallel: bool = True
    max_execution_time: float = 10.0
    max_output_size: int = 16384
    requires_confirmation: bool = False
    parameters_schema: Dict[str, Any]
    
    class Config:
        arbitrary_types_allowed = True
