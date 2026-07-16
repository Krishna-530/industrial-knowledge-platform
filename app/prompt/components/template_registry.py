from typing import Dict
from uuid import UUID
from app.prompt.interfaces import AbstractTemplateRegistry
from app.prompt.models.template import PromptTemplate, PromptVersion
import logging

logger = logging.getLogger(__name__)

class TemplateRegistry(AbstractTemplateRegistry):
    """
    Handles caching and loading of PromptTemplates from disk or memory.
    Does NOT make decisions on which template to use.
    """
    def __init__(self):
        # In-memory cache: (template_id, version_str) -> PromptTemplate
        self._cache: Dict[str, PromptTemplate] = {}

    def _get_cache_key(self, template_id: UUID, version: PromptVersion) -> str:
        return f"{template_id}_v{version.major}.{version.minor}"

    def get_template(self, template_id: UUID, version: PromptVersion) -> PromptTemplate:
        key = self._get_cache_key(template_id, version)
        if key in self._cache:
            return self._cache[key]
            
        # Simulated disk load. In reality, it would read from resources/prompts/
        # and parse the frontmatter to construct the PromptTemplate domain object.
        logger.info(f"Cache miss for template {key}. Loading from disk.")
        
        # Placeholder for actual disk load
        template = PromptTemplate(
            id=template_id,
            version=version,
            description="Dynamically loaded template",
            renderer="jinja2",
            variables=["context", "history", "query"],
            file_path=f"resources/prompts/{key}.j2",
            checksum="dummy_checksum"
        )
        
        self._cache[key] = template
        return template
