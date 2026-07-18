from typing import Any, Dict
from app.tools.interfaces.abstract_tool import AbstractTool
from app.tools.models.tool_context import ToolContext
import sys
import platform

class SystemInfoTool(AbstractTool):
    async def execute(self, arguments: Dict[str, Any], context: ToolContext) -> Any:
        return {
            "api_version": "1.0.0",
            "environment": "production",
            "os_family": platform.system(),
            "python_version": sys.version.split(" ")[0],
            "supported_features": ["streaming", "parallel_tools", "retrieval"]
        }
