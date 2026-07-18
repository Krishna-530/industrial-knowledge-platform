from pydantic import BaseModel
from typing import Dict

class ToolParameter(BaseModel):
    type: str
    description: str
    required: bool

class ToolDefinition(BaseModel):
    name: str
    description: str
    parameters: Dict[str, ToolParameter]
