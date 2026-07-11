import uuid
import asyncio
from datetime import datetime, timezone, timedelta
from typing import AsyncGenerator
from app.llm.models.request import LLMRequest
from app.llm.models.context import ExecutionContext, ExecutionState
from app.llm.models.response import ExecutionResult, StreamChunk
from app.llm.pipeline.orchestrator import LLMExecutionPipeline
from app.llm.providers.normalizers.dummy_normalizer import DummyResponseNormalizer, DummyStreamNormalizer

class LLMWorkflow:
    def __init__(self, pipeline: LLMExecutionPipeline, response_normalizer: DummyResponseNormalizer, stream_normalizer: DummyStreamNormalizer):
        self.pipeline = pipeline
        self.response_normalizer = response_normalizer
        self.stream_normalizer = stream_normalizer

    async def execute(self, request: LLMRequest) -> ExecutionResult:
        context = ExecutionContext(
            request_id=uuid.uuid4(),
            trace_id=uuid.uuid4(),
            correlation_id=uuid.uuid4(),
            deadline=datetime.now(timezone.utc) + timedelta(seconds=60)
        )
        state = ExecutionState()
        raw_result = await self.pipeline.execute(context, state, request, stream=False)
        return self.response_normalizer.normalize(raw_result)

    async def stream(self, request: LLMRequest, cancellation_token: asyncio.Event) -> AsyncGenerator[StreamChunk, None]:
        context = ExecutionContext(
            request_id=uuid.uuid4(),
            trace_id=uuid.uuid4(),
            correlation_id=uuid.uuid4(),
            deadline=datetime.now(timezone.utc) + timedelta(seconds=60),
            cancellation_token=cancellation_token
        )
        state = ExecutionState()
        raw_stream = await self.pipeline.execute(context, state, request, stream=True)
        
        # stream normalization logic here in workflow wrapper
        async for chunk in raw_stream:
            yield self.stream_normalizer.normalize_chunk(chunk)
