from fastapi import APIRouter, Depends
from api.v1.schemas.auth import User
from dependencies.auth import get_current_user, RoleChecker

router = APIRouter()

@router.get("/me", response_model=User)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/admin")
async def get_admin_data(current_user: User = Depends(RoleChecker(["Admin"]))):
    return {
        "message": "Admin access granted",
        "data": {
            "secret": "Only admins can see this",
            "user": current_user.model_dump()
        }
    }
