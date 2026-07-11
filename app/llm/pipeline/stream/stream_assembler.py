import json
from copy import deepcopy
from typing import AsyncGenerator, Dict, Any

class StreamAssembler:
    """
    Middleware that buffers and reconstructs fragmented chunks from the provider.
    Specifically useful for tool calls where JSON arguments arrive in tiny fragments.
    """
    async def assemble(self, raw_stream: AsyncGenerator[Any, None]) -> AsyncGenerator[Any, None]:
        buffer = {}
        
        async for chunk in raw_stream:
            # If it's a content delta, yield immediately
            if chunk.get("delta"):
                yield chunk
            
            # If it's a tool call delta, buffer and assemble it
            elif "tool_call_id" in chunk:
                tc_id = chunk["tool_call_id"]
                if tc_id not in buffer:
                    buffer[tc_id] = {
                        "id": tc_id,
                        "name": chunk.get("tool_name", ""),
                        "arguments": chunk.get("tool_arguments", "")
                    }
                else:
                    if "tool_name" in chunk:
                        buffer[tc_id]["name"] += chunk["tool_name"]
                    if "tool_arguments" in chunk:
                        buffer[tc_id]["arguments"] += chunk["tool_arguments"]
                        
            # If a finish_reason indicates the tool call is done, we yield the complete buffered object
            if chunk.get("finish_reason") == "tool_call" and buffer:
                # Yield all completed tool calls in this chunk
                yield {"assembled_tool_calls": list(buffer.values())}
                buffer.clear()
            elif chunk.get("finish_reason") in ("stop", "length", "content_filter"):
                yield chunk
