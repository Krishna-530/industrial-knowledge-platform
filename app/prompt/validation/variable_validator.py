from typing import Dict, Any
from app.prompt.models.template import PromptTemplate

class VariableValidator:
    """
    Validates that all required variables are present before rendering.
    """
    def validate(self, template: PromptTemplate, variables: Dict[str, Any]) -> None:
        missing = []
        for var in template.variables:
            if var not in variables:
                missing.append(var)
                
        if missing:
            raise ValueError(f"Missing required variables for template {template.id}: {missing}")
