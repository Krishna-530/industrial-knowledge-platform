from app.llm.interfaces.pipeline import AbstractPipelineStage
from app.llm.models.context import ExecutionContext, ExecutionState
from app.llm.models.request import LLMRequest
from app.llm.models.errors import InvalidRequest

class ModelSelectionStage(AbstractPipelineStage):
    def __init__(self, provider_registry):
        self.registry = provider_registry
        # Minimal set of known supported groq models for this example
        self.supported_models = {
            "llama3-8b-8192",
            "llama3-70b-8192",
            "mixtral-8x7b-32768"
        }

    async def execute(self, context: ExecutionContext, state: ExecutionState, request: LLMRequest, stream: bool = False) -> None:
        state.current_stage = "MODEL_SELECTION"
        
        # We enforce Groq-only architecture for this phase
        state.selected_provider = "groq"
        requested_model = request.payload.model
        
        if requested_model not in self.supported_models:
            raise InvalidRequest(f"Model {requested_model} is not supported by the Groq integration.")
            
        state.selected_model = requested_model
