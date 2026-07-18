import asyncio
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from app.llm.models.request import LLMRequest
from app.llm.models.response import ExecutionResult
from app.workflows.llm_workflow import LLMWorkflow
from api.v1.dependencies.llm import provide_llm_workflow

router = APIRouter()

@router.post("/generate", response_model=ExecutionResult)
async def generate(request: LLMRequest, workflow: LLMWorkflow = Depends(provide_llm_workflow)):
    """
    Generate a response from the AI Execution Engine.
    """
    try:
        return await workflow.execute(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stream")
async def stream(request: LLMRequest, http_request: Request, workflow: LLMWorkflow = Depends(provide_llm_workflow)):
    """
    Stream a response from the AI Execution Engine.
    """
    cancellation_token = asyncio.Event()

    async def watch_disconnect():
        while True:
            if await http_request.is_disconnected():
                cancellation_token.set()
                break
            await asyncio.sleep(1)

    async def generate_stream():
        try:
            async for chunk in workflow.stream(request, cancellation_token):
                yield f"data: {chunk.model_dump_json()}\n\n"
        except Exception as e:
            yield f"data: {{\"error\": \"{str(e)}\"}}\n\n"
        finally:
            yield "data: [DONE]\n\n"
            
    # Start the disconnect watcher in the background
    asyncio.create_task(watch_disconnect())
    return StreamingResponse(generate_stream(), media_type="text/event-stream")
