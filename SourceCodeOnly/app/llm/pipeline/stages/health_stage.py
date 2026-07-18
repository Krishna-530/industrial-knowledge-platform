from app.llm.interfaces.pipeline import AbstractPipelineStage
from app.llm.models.context import ExecutionContext, ExecutionState
from app.llm.models.errors import ProviderUnavailable

class HealthStage(AbstractPipelineStage):
    def __init__(self, provider_registry):
        self.registry = provider_registry

    async def execute(self, context: ExecutionContext, state: ExecutionState) -> None:
        state.current_stage = "HEALTH"
        provider = self.registry.get_provider(state.selected_provider)
        
        # Fast fail if provider circuit breaker is open or health check fails
        if not await provider.health_check():
            raise ProviderUnavailable(f"Provider {state.selected_provider} is unhealthy")
