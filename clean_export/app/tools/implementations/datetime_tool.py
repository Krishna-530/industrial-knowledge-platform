from typing import Any, Dict
from datetime import datetime, timezone
from app.tools.interfaces.abstract_tool import AbstractTool
from app.tools.models.tool_context import ToolContext

class DateTimeTool(AbstractTool):
    async def execute(self, arguments: Dict[str, Any], context: ToolContext) -> Any:
        # Simplistic date time retrieval, always UTC for now
        return datetime.now(timezone.utc).isoformat()
