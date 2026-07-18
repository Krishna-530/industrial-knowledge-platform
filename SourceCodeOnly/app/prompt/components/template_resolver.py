from uuid import UUID
from app.prompt.interfaces import AbstractTemplateRegistry
from app.prompt.models.template import PromptTemplate, PromptVersion
import logging

logger = logging.getLogger(__name__)

class TemplateResolver:
    """
    Selects the correct template and version based on configuration and fallback rules.
    """
    def __init__(self, registry: AbstractTemplateRegistry):
        self.registry = registry

    def resolve(self, template_id: UUID, requested_version: PromptVersion) -> PromptTemplate:
        # In a real system, this might check if requested_version is deprecated
        # and fallback to a newer version if allowed by policy.
        # For now, it simply fetches from the registry.
        
        template = self.registry.get_template(template_id, requested_version)
        
        if template.version.deprecated:
            logger.warning(f"Template {template_id} version {requested_version.major}.{requested_version.minor} is deprecated.")
            
        return template
