from app.tools.models.tool_manifest import ToolManifest
from app.tools.models.tool_context import ToolContext

class ToolPermissionEvaluator:
    async def evaluate(self, manifest: ToolManifest, context: ToolContext) -> bool:
        """
        Evaluates whether the given workspace/user has permission to execute this tool.
        For phase 8.2 foundation, we just return True. 
        In production, this would cross-reference RBAC policies against manifest.permissions.
        """
        return True
