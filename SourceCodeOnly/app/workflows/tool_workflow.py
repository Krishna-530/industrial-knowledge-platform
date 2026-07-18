import asyncio
import time
import json
import uuid
from typing import List
from app.tools.tool_service import ToolService
from app.tools.models.tool_context import ToolContext
from app.tools.models.tool_result import ToolCallResult
from app.llm.models.response import ToolCallRequest

class ToolWorkflow:
    def __init__(self, tool_service: ToolService):
        self.tool_service = tool_service

    async def execute_tools(self, tool_requests: List[ToolCallRequest], context: ToolContext) -> List[ToolCallResult]:
        tasks = [self._execute_single_tool(req, context) for req in tool_requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        final_results = []
        for res in results:
            if isinstance(res, Exception):
                final_results.append(ToolCallResult(
                    tool_call_id="unknown",
                    tool_name="unknown",
                    execution_id=str(uuid.uuid4()),
                    content=f"System error executing tool: {str(res)}",
                    is_error=True,
                    status="SYSTEM_ERROR"
                ))
            else:
                final_results.append(res)
                
        return final_results

    async def _execute_single_tool(self, request: ToolCallRequest, context: ToolContext) -> ToolCallResult:
        start_time = time.time()
        execution_id = str(uuid.uuid4())
        
        registration = self.tool_service.get_registration(request.name)
        if not registration:
            return ToolCallResult(
                tool_call_id=request.id,
                tool_name=request.name,
                execution_id=execution_id,
                content=f"Error: Tool '{request.name}' not found.",
                is_error=True,
                status="NOT_FOUND",
                latency_ms=(time.time() - start_time) * 1000
            )
            
        manifest = registration.manifest
        
        try:
            # 1. Validate Access
            await self.tool_service.validate_access(manifest, context)
            
            # 2. Parse Arguments
            args = json.loads(request.arguments) if isinstance(request.arguments, str) else request.arguments
            
            # 3. Check for Cancellation before executing
            if context.cancellation_token.is_set():
                return ToolCallResult(
                    tool_call_id=request.id,
                    tool_name=manifest.id,
                    tool_version=manifest.version,
                    execution_id=execution_id,
                    content="Execution cancelled.",
                    is_error=True,
                    status="CANCELLED",
                    latency_ms=(time.time() - start_time) * 1000
                )
            
            # 4. Instantiate Tool via Factory
            tool = registration.factory.create()
            
            # 5. Execute with Timeout
            raw_result = await asyncio.wait_for(
                tool.execute(args, context),
                timeout=manifest.max_execution_time
            )
            
            # 6. Format and Truncate
            content = str(raw_result)
            truncated = False
            if len(content) > manifest.max_output_size:
                content = content[:manifest.max_output_size] + "...[TRUNCATED]"
                truncated = True
                
            return ToolCallResult(
                tool_call_id=request.id,
                tool_name=manifest.id,
                tool_version=manifest.version,
                execution_id=execution_id,
                content=content,
                is_error=False,
                status="SUCCESS",
                truncated=truncated,
                latency_ms=(time.time() - start_time) * 1000
            )
            
        except asyncio.TimeoutError:
            return ToolCallResult(
                tool_call_id=request.id,
                tool_name=manifest.id,
                tool_version=manifest.version,
                execution_id=execution_id,
                content=f"Error: Execution timed out after {manifest.max_execution_time}s.",
                is_error=True,
                status="TIMEOUT",
                latency_ms=(time.time() - start_time) * 1000
            )
        except Exception as e:
            return ToolCallResult(
                tool_call_id=request.id,
                tool_name=manifest.id,
                tool_version=manifest.version,
                execution_id=execution_id,
                content=f"Execution error: {str(e)}",
                is_error=True,
                status="ERROR",
                latency_ms=(time.time() - start_time) * 1000
            )
