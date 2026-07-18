from app.llm.interfaces.pipeline import AbstractPipelineStage
from app.llm.models.context import ExecutionContext, ExecutionState
from app.llm.models.request import LLMRequest
from app.llm.pipeline.token_estimator import TokenEstimator
from app.llm.models.errors import ContextTooLarge

class ValidationStage(AbstractPipelineStage):
    def __init__(self, estimator: TokenEstimator, max_input_tokens: int = 128000):
        self.estimator = estimator
        self.max_input_tokens = max_input_tokens

    async def execute(self, context: ExecutionContext, state: ExecutionState, request: LLMRequest, stream: bool = False) -> None:
        state.current_stage = "VALIDATION"
        
        estimated_tokens = self.estimator.estimate_tokens(request.payload)
        
        if estimated_tokens > self.max_input_tokens:
            raise ContextTooLarge(f"Payload estimated at {estimated_tokens} tokens, exceeding max of {self.max_input_tokens}")
