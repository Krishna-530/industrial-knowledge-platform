from typing import Any
from app.llm.interfaces.normalizer import AbstractResponseNormalizer, AbstractStreamNormalizer
from app.llm.models.response import ExecutionResult, StreamChunk, UsageMetrics, ProviderMetadata, FinishReason

class DummyResponseNormalizer(AbstractResponseNormalizer):
    def normalize(self, raw_response: Any) -> ExecutionResult:
        return ExecutionResult(
            id=raw_response["id"],
            content=raw_response.get("content", ""),
            tool_calls=[],
            finish_reason=FinishReason(raw_response.get("finish_reason", "stop")),
            usage=UsageMetrics(**raw_response.get("usage", {})),
            metadata=ProviderMetadata(
                provider_name="dummy",
                model_name="dummy_model",
                latency_ms=10.5
            )
        )

class DummyStreamNormalizer(AbstractStreamNormalizer):
    def normalize_chunk(self, raw_chunk: Any) -> StreamChunk:
        return StreamChunk(
            id=raw_chunk["id"],
            content_delta=raw_chunk.get("delta", ""),
            finish_reason=FinishReason(raw_chunk["finish_reason"]) if "finish_reason" in raw_chunk else None
        )
