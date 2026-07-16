import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.user_service import UserService
from api.v1.schemas.user import CreateUserRequest, UpdateUserRequest
from core.exceptions import ForbiddenError

@pytest.mark.asyncio
async def test_create_user(db_session: AsyncSession):
    # Setup test by getting an existing role (e.g. User role seeded by migration)
    from database.repositories.role import RoleRepository
    role_repo = RoleRepository(db_session)
    roles = await role_repo.list()
    assert len(roles) > 0
    role_id = roles[0].id

    service = UserService(db_session)
    req = CreateUserRequest(
        name="Test User",
        email="test@example.com",
        password="password123",
        role_id=role_id
    )
    user = await service.create_user(req)
    assert user.email == "test@example.com"
    assert user.is_active is True

@pytest.mark.asyncio
async def test_update_user(db_session: AsyncSession):
    from database.repositories.role import RoleRepository
    role_repo = RoleRepository(db_session)
    roles = await role_repo.list()
    role_id = roles[0].id

    service = UserService(db_session)
    req = CreateUserRequest(
        name="Update User",
        email="update@example.com",
        password="password123",
        role_id=role_id
    )
    user = await service.create_user(req)
    
    update_req = UpdateUserRequest(name="Updated Name")
    updated = await service.update_user(user.id, update_req)
    assert updated.name == "Updated Name"

@pytest.mark.asyncio
async def test_deactivate_self_fails(db_session: AsyncSession):
    from database.repositories.role import RoleRepository
    role_repo = RoleRepository(db_session)
    roles = await role_repo.list()
    role_id = roles[0].id

    service = UserService(db_session)
    req = CreateUserRequest(
        name="Self Deact User",
        email="selfdeact@example.com",
        password="password123",
        role_id=role_id
    )
    user = await service.create_user(req)
    
    with pytest.raises(ForbiddenError):
        await service.deactivate_user(user.id, user.id)
