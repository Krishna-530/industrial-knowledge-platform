from abc import ABC, abstractmethod
from typing import Dict, Any, List
from uuid import UUID

from app.prompt.models.template import PromptTemplate, PromptVersion
from app.prompt.models.schemas import PromptMessage

class AbstractTemplateRegistry(ABC):
    @abstractmethod
    def get_template(self, template_id: UUID, version: PromptVersion) -> PromptTemplate:
        pass

class AbstractPromptRenderer(ABC):
    @abstractmethod
    def render(self, template: PromptTemplate, variables: Dict[str, Any]) -> str:
        """
        Renders the raw string/payload from the template.
        For advanced templates, this might return JSON structure that represents multiple messages.
        For simple ones, it returns a string.
        """

class AbstractMessageOrderingStrategy(ABC):
    @abstractmethod
    def order(self, messages: List[PromptMessage]) -> List[PromptMessage]:
        pass
