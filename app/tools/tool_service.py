from typing import Optional
from app.tools.registry import ToolRegistry, ToolRegistration
from app.tools.security.permission_evaluator import ToolPermissionEvaluator
from app.tools.models.tool_manifest import ToolManifest
from app.tools.models.tool_context import ToolContext
from core.exceptions.auth import ForbiddenError

class ToolService:
    def __init__(self, registry: ToolRegistry, permission_evaluator: ToolPermissionEvaluator):
        self.registry = registry
        self.permission_evaluator = permission_evaluator

    def get_registration(self, tool_id: str) -> Optional[ToolRegistration]:
        return self.registry.get_registration(tool_id)

    async def validate_access(self, manifest: ToolManifest, context: ToolContext) -> None:
        """
        Validates whether the execution context has permission to run the tool.
        Raises ForbiddenError if denied.
        """
        has_access = await self.permission_evaluator.evaluate(manifest, context)
        if not has_access:
            raise ForbiddenError(f"Access denied to tool: {manifest.id}")
