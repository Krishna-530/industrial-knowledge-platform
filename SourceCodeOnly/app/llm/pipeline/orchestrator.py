from typing import List
from app.llm.interfaces.pipeline import AbstractPipelineStage, AbstractMiddleware
from app.llm.models.context import ExecutionContext, ExecutionState
from app.llm.models.request import LLMRequest

class LLMExecutionPipeline:
    def __init__(self, stages: List[AbstractPipelineStage], middlewares: List[AbstractMiddleware]):
        self.stages = stages
        self.middlewares = middlewares

    async def _execute_stages(self, context: ExecutionContext, state: ExecutionState, request: LLMRequest, stream: bool = False) -> any:
        # Note: In a real implementation we would pass `request` and `stream` cleanly.
        # Here we just iterate for demonstration. The final stage (ExecutionStage)
        # returns the ExecutionResult or AsyncGenerator.
        result = None
        for stage in self.stages:
            if hasattr(stage, 'execute') and getattr(stage.execute, '__code__', None) and 'request' in getattr(stage.execute, '__code__').co_varnames:
                result = await stage.execute(context, state, request, stream)
            else:
                await stage.execute(context, state)
        return result

    async def execute(self, context: ExecutionContext, state: ExecutionState, request: LLMRequest, stream: bool = False) -> any:
        # Build the middleware chain around the core stage execution
        
        async def core_execution(ctx, st):
            return await self._execute_stages(ctx, st, request, stream)

        current_call = core_execution
        
        # Wrap middlewares in reverse order
        for middleware in reversed(self.middlewares):
            def make_call(mw, next_c):
                async def wrapped_call(ctx, st):
                    return await mw.invoke(ctx, st, next_c)
                return wrapped_call
            current_call = make_call(middleware, current_call)
            
        return await current_call(context, state)
