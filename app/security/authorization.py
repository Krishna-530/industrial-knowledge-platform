from typing import List, Union
from core.exceptions import ForbiddenError
from app.security.context import SecurityContext
from app.security.permissions import Permission

def require_permission(context: SecurityContext, required_permissions: Union[Permission, List[Permission]]) -> bool:
    """
    Evaluates whether the security context has the required permission(s).
    Raises ForbiddenError if authorization fails.
    """
    if context.is_admin:
        return True
        
    if isinstance(required_permissions, Permission):
        required_permissions = [required_permissions]
        
    for perm in required_permissions:
        if perm.value not in context.permissions:
            raise ForbiddenError(message=f"Missing required permission: {perm.value}")
            
    return True
