from abc import ABC, abstractmethod
from app.tools.interfaces.abstract_tool import AbstractTool

class ToolFactory(ABC):
    @abstractmethod
    def create(self) -> AbstractTool:
        pass
