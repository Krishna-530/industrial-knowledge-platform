from abc import ABC, abstractmethod
from typing import Any, Dict
from app.tools.models.tool_context import ToolContext

class AbstractTool(ABC):
    @abstractmethod
    async def execute(self, arguments: Dict[str, Any], context: ToolContext) -> Any:
        """
        Executes the tool logic. 
        Returns an object that can be serialized.
        The ToolWorkflow will catch exceptions and handle truncation.
        """
