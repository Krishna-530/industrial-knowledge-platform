import time
import logging
from typing import Dict, Any

from app.prompt.models.config import PromptConfig
from app.prompt.models.schemas import PromptPayload, PromptMessage, PromptRole, TextBlock
from app.prompt.components.template_resolver import TemplateResolver
from app.prompt.components.jinja_renderer import JinjaPromptRenderer
from app.prompt.components.prompt_builder import PromptBuilder
from app.prompt.validation.variable_validator import VariableValidator
from app.prompt.validation.prompt_validator import PromptValidator
from app.prompt.strategies.message_ordering import AbstractMessageOrderingStrategy

logger = logging.getLogger(__name__)

class PromptService:
    """
    Orchestrator for the Prompt Assembly Engine.
    Coordinates resolver, renderer, validators, and builders without performing the logic itself.
    """
    def __init__(
        self,
        resolver: TemplateResolver,
        renderer: JinjaPromptRenderer, # Can be AbstractPromptRenderer
        variable_validator: VariableValidator,
        prompt_validator: PromptValidator,
        ordering_strategy: AbstractMessageOrderingStrategy
    ):
        self.resolver = resolver
        self.renderer = renderer
        self.variable_validator = variable_validator
        self.prompt_validator = prompt_validator
        self.ordering_strategy = ordering_strategy

    def assemble(self, config: PromptConfig, variables: Dict[str, Any]) -> PromptPayload:
        start_time = time.time()
        
        # 1. Resolve Template
        template = self.resolver.resolve(config.template_id, config.template_version)
        
        # 2. Validate Inputs
        self.variable_validator.validate(template, variables)
        
        # 3. Render Content
        # In a real system, the renderer might return structured messages or a single string.
        # Here we simulate rendering a single system instruction string.
        rendered_content = self.renderer.render(template, variables)
        
        # 4. Construct Messages
        # This logic converts the raw rendered string into domain objects.
        # For simplicity, we just create a SYSTEM message from the template, 
        # and a USER message from the query.
        raw_messages = []
        
        system_block = TextBlock(text=rendered_content)
        raw_messages.append(PromptMessage(role=PromptRole.SYSTEM, content=[system_block]))
        
        if "query" in variables:
            user_block = TextBlock(text=variables["query"])
            raw_messages.append(PromptMessage(role=PromptRole.USER, content=[user_block]))
            
        # 5. Order Messages
        ordered_messages = self.ordering_strategy.order(raw_messages)
        
        # 6. Validate Payload Structure
        self.prompt_validator.validate(ordered_messages)
        
        # 7. Build Final Payload
        duration = (time.time() - start_time) * 1000
        builder = PromptBuilder()
        builder.add_messages(ordered_messages)
        
        # Note: Tool additions would happen here if config.include_tools is True.
        
        payload = builder.build(
            template=template,
            language=config.language,
            renderer_name=self.renderer.__class__.__name__,
            duration_ms=duration
        )
        
        logger.info({"event": "prompt_assembly_complete", "template_id": str(template.id)})
        return payload
