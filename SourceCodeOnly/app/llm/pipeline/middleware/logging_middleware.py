from app.llm.interfaces.pipeline import AbstractMiddleware
from app.llm.models.context import ExecutionContext, ExecutionState

class LoggingMiddleware(AbstractMiddleware):
    async def invoke(self, context: ExecutionContext, state: ExecutionState, next_call) -> any:
        # Pre-execution logging
        result = await next_call(context, state)
        # Post-execution logging
        return result
