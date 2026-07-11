import asyncio
from typing import AsyncGenerator
from app.llm.interfaces.pipeline import AbstractPipelineStage
from app.llm.models.context import ExecutionContext, ExecutionState
from app.llm.models.errors import ProviderError, RateLimited
from app.llm.pipeline.retry_policy import RetryPolicy
from app.llm.pipeline.retry_classifier import RetryClassifier, RetryAction
from app.llm.models.request import LLMRequest

import random

class ExecutionStage(AbstractPipelineStage):
    def __init__(self, provider_registry, retry_policy: RetryPolicy, retry_classifier: RetryClassifier):
        self.registry = provider_registry
        self.retry_policy = retry_policy
        self.retry_classifier = retry_classifier

    async def execute(self, context: ExecutionContext, state: ExecutionState, request: LLMRequest, stream: bool = False) -> any:
        state.current_stage = "EXECUTION"
        provider = self.registry.get_provider(state.selected_provider)
        
        # Track if we've yielded any chunks to the client
        chunks_yielded = False

        while state.retry_count <= self.retry_policy.max_retries:
            if context.cancellation_token.is_set():
                raise asyncio.CancelledError("Request was cancelled by client.")
            try:
                if stream:
                    async def stream_with_cancellation():
                        nonlocal chunks_yielded
                        async for chunk in provider.stream(context, state, request):
                            if context.cancellation_token.is_set():
                                raise asyncio.CancelledError("Stream cancelled by client.")
                            chunks_yielded = True
                            yield chunk
                    return stream_with_cancellation()
                else:
                    return await provider.generate(context, state, request)
            except Exception as e:
                # If we've already sent chunks to the client, we cannot retry streaming.
                if stream and chunks_yielded:
                    state.fatal_error = e
                    raise

                action = self.retry_classifier.classify(e)
                if action == RetryAction.FATAL or state.retry_count >= self.retry_policy.max_retries:
                    state.fatal_error = e
                    raise
                
                state.retry_count += 1
                
                # Check for Retry-After header if provided
                retry_after = getattr(e, 'retry_after', None)
                base_backoff = min(
                    self.retry_policy.base_backoff_ms * (2 ** (state.retry_count - 1)),
                    self.retry_policy.max_backoff_ms
                )
                
                # Jitter: 0-500ms
                jitter = random.uniform(0, 500)
                
                total_sleep = max(float(retry_after or 0) * 1000, base_backoff) + jitter
                await asyncio.sleep(total_sleep / 1000.0)
