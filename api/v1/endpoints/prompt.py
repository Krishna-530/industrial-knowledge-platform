from fastapi import APIRouter, Depends, Security
from pydantic import BaseModel
from typing import Dict, Any

from app.prompt.models.config import PromptConfig
from app.prompt.models.schemas import PromptPayload
from app.workflows.prompt_workflow import PromptWorkflow
from api.v1.dependencies.prompt import provide_prompt_workflow
from dependencies.auth import get_current_user

router = APIRouter(prefix="/prompt", tags=["Prompt Assembly"])

class APIPromptRequest(BaseModel):
    config: PromptConfig
    variables: Dict[str, Any]

@router.post("/assemble", response_model=PromptPayload)
async def assemble_prompt(
    payload: APIPromptRequest,
    current_user = Security(get_current_user),
    workflow: PromptWorkflow = Depends(provide_prompt_workflow)
):
    # Pass to workflow
    return await workflow.execute_assembly(payload.config, payload.variables)
