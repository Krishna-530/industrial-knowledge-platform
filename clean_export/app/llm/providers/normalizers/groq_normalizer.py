from groq.types.chat import ChatCompletion, ChatCompletionChunk
from app.llm.interfaces.normalizer import AbstractResponseNormalizer, AbstractStreamNormalizer
from app.llm.models.response import ExecutionResult, StreamChunk, UsageMetrics, ProviderMetadata, FinishReason, ToolCallRequest

class GroqResponseNormalizer(AbstractResponseNormalizer):
    def normalize(self, raw_response: ChatCompletion) -> ExecutionResult:
        choice = raw_response.choices[0]
        
        tool_calls = []
        if choice.message.tool_calls:
            for tc in choice.message.tool_calls:
                tool_calls.append(ToolCallRequest(
                    id=tc.id,
                    name=tc.function.name,
                    arguments=tc.function.arguments
                ))
                
        finish_reason = choice.finish_reason
        if finish_reason == "tool_calls":
            finish_reason = "tool_call"
            
        return ExecutionResult(
            id=raw_response.id,
            content=choice.message.content or "",
            tool_calls=tool_calls,
            finish_reason=FinishReason(finish_reason or "stop"),
            usage=UsageMetrics(
                prompt_tokens=raw_response.usage.prompt_tokens,
                completion_tokens=raw_response.usage.completion_tokens,
                total_tokens=raw_response.usage.total_tokens
            ) if raw_response.usage else UsageMetrics(),
            metadata=ProviderMetadata(
                provider_name="groq",
                model_name=raw_response.model,
                latency_ms=0.0 # Could calculate if tracked around the call
            )
        )

class GroqStreamNormalizer(AbstractStreamNormalizer):
    def normalize_chunk(self, raw_chunk: ChatCompletionChunk) -> StreamChunk:
        if not raw_chunk.choices:
            return StreamChunk(id=raw_chunk.id, content_delta="")
            
        choice = raw_chunk.choices[0]
        
        finish_reason = choice.finish_reason
        if finish_reason == "tool_calls":
            finish_reason = "tool_call"
            
        content_delta = choice.delta.content or ""
        
        # In stream chunks, groq yields tool calls as deltas
        # The StreamAssembler actually already normalizes this slightly into our expected format if assembled,
        # but the abstract pipeline says Normalizer runs *after* Assembler.
        # So we should expect either raw chunks or assembled chunks.
        # Actually, StreamAssembler is yielding raw dicts for assembled tool calls!
        # Let's handle both.
        
        if isinstance(raw_chunk, dict) and "assembled_tool_calls" in raw_chunk:
            return StreamChunk(
                id=raw_chunk.get("id", "assembled"),
                content_delta="",
                finish_reason=FinishReason.TOOL_CALL,
                tool_call_delta=ToolCallRequest(**raw_chunk["assembled_tool_calls"][0]) # simplified for single
            )
            
        # For raw groq chunk mapping (before assembler finishes)

        if choice.delta.tool_calls:
            tc = choice.delta.tool_calls[0]
            if tc.function:
                # Return partial dict to match StreamAssembler logic
                return {
                    "tool_call_id": tc.id,
                    "tool_name": tc.function.name or "",
                    "tool_arguments": tc.function.arguments or "",
                    "finish_reason": finish_reason
                }
        
        # If it's a content delta
        return StreamChunk(
            id=raw_chunk.id if hasattr(raw_chunk, 'id') else "unknown",
            content_delta=content_delta,
            finish_reason=FinishReason(finish_reason) if finish_reason else None
        )
        
