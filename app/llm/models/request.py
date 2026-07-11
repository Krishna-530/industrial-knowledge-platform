from typing import Any
from pydantic import BaseModel
from app.prompt.models.schemas import PromptPayload
from app.llm.models.config import UniversalGenerationConfig

class LLMRequest(BaseModel):
    """
    Standard request payload containing the prompt and execution configuration.
    """
    payload: PromptPayload
    config: UniversalGenerationConfig
