from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field

class ProviderExecutionOptions(BaseModel):
    """
    Strict typing for provider-specific overrides, avoiding raw Dict[str, Any].
    """
    frequency_penalty: Optional[float] = None
    presence_penalty: Optional[float] = None
    logit_bias: Optional[Dict[str, int]] = None

class UniversalGenerationConfig(BaseModel):
    """
    Provider-agnostic execution config.
    """
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=None, gt=0)
    top_p: float = Field(default=1.0, ge=0.0, le=1.0)
    stop_sequences: List[str] = Field(default_factory=list)
    response_format: Optional[str] = None # e.g. "json_object"
    provider_options: ProviderExecutionOptions = Field(default_factory=ProviderExecutionOptions)
