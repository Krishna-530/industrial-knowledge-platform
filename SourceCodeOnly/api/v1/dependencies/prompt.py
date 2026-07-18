from fastapi import Depends
from app.prompt.components.template_registry import TemplateRegistry
from app.prompt.components.template_resolver import TemplateResolver
from app.prompt.components.jinja_renderer import JinjaPromptRenderer
from app.prompt.strategies.message_ordering import StandardMessageOrderingStrategy
from app.prompt.validation.variable_validator import VariableValidator
from app.prompt.validation.prompt_validator import PromptValidator
from app.prompt.prompt_service import PromptService
from app.workflows.prompt_workflow import PromptWorkflow

# Maintain singleton-like registry for cache
_registry_instance = TemplateRegistry()

def provide_template_registry() -> TemplateRegistry:
    return _registry_instance

def provide_template_resolver(registry: TemplateRegistry = Depends(provide_template_registry)) -> TemplateResolver:
    return TemplateResolver(registry)

def provide_prompt_renderer() -> JinjaPromptRenderer:
    return JinjaPromptRenderer()

def provide_variable_validator() -> VariableValidator:
    return VariableValidator()

def provide_prompt_validator() -> PromptValidator:
    return PromptValidator()

def provide_message_ordering_strategy() -> StandardMessageOrderingStrategy:
    return StandardMessageOrderingStrategy()

def provide_prompt_service(
    resolver: TemplateResolver = Depends(provide_template_resolver),
    renderer: JinjaPromptRenderer = Depends(provide_prompt_renderer),
    variable_validator: VariableValidator = Depends(provide_variable_validator),
    prompt_validator: PromptValidator = Depends(provide_prompt_validator),
    ordering_strategy: StandardMessageOrderingStrategy = Depends(provide_message_ordering_strategy)
) -> PromptService:
    return PromptService(
        resolver=resolver,
        renderer=renderer,
        variable_validator=variable_validator,
        prompt_validator=prompt_validator,
        ordering_strategy=ordering_strategy
    )

def provide_prompt_workflow(
    prompt_service: PromptService = Depends(provide_prompt_service)
) -> PromptWorkflow:
    return PromptWorkflow(prompt_service)
