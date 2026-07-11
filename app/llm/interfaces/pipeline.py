from abc import ABC, abstractmethod
from typing import AsyncGenerator
from app.llm.models.context import ExecutionContext, ExecutionState

class AbstractPipelineStage(ABC):
    @abstractmethod
    async def execute(self, context: ExecutionContext, state: ExecutionState) -> None:
        pass

class AbstractMiddleware(ABC):
    @abstractmethod
    async def invoke(self, context: ExecutionContext, state: ExecutionState, next_call) -> None:
        pass
