import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from database.repositories.user import UserRepository
from database.repositories.role import RoleRepository
from core.exceptions import DuplicateEntityError

@pytest.mark.asyncio
async def test_user_repository_crud(db_session: AsyncSession):
    user_repo = UserRepository(db_session)
    role_repo = RoleRepository(db_session)
    
    # Get the seeded 'user' role
    role = await role_repo.get_by_name("user")
    assert role is not None
    
    # Create
    user = await user_repo.create(
        name="Test User", 
        email="test@example.com", 
        password_hash="hash", 
        role_id=role.id
    )
    assert user.id is not None
    assert user.email == "test@example.com"
    
    # Get by ID
    fetched_user = await user_repo.get_by_id(user.id)
    assert fetched_user is not None
    assert fetched_user.id == user.id
    
    # Get by Email
    fetched_user = await user_repo.get_by_email("test@example.com")
    assert fetched_user is not None
    
    # Update
    updated_user = await user_repo.update(user.id, name="Updated User")
    assert updated_user.name == "Updated User"
    
    # List
    users = await user_repo.list()
    assert len(users) >= 1
    
    # Delete
    deleted = await user_repo.delete(user.id)
    assert deleted is True
    assert await user_repo.get_by_id(user.id) is None

@pytest.mark.asyncio
async def test_duplicate_email(db_session: AsyncSession):
    user_repo = UserRepository(db_session)
    role_repo = RoleRepository(db_session)
    role = await role_repo.get_by_name("user")
    
    await user_repo.create(
        name="Test User", 
        email="dup@example.com", 
        password_hash="hash", 
        role_id=role.id
    )
    
    with pytest.raises(DuplicateEntityError):
        await user_repo.create(
            name="Another User", 
            email="dup@example.com", 
            password_hash="hash", 
            role_id=role.id
        )
