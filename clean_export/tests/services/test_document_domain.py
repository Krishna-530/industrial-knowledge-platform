import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.category_service import CategoryService
from app.services.tag_service import TagService
from app.services.document_service import DocumentService
from api.v1.schemas.category import CategoryRequest
from api.v1.schemas.tag import TagRequest
from api.v1.schemas.document import CreateDocumentRequest
from core.exceptions import EntityNotFoundError, ValidationException, ForbiddenError

@pytest.mark.asyncio
async def test_category_crud(db_session: AsyncSession):
    service = CategoryService(db_session)
    
    # Create
    req = CategoryRequest(name="Test Category", description="Description")
    cat = await service.create_category(req)
    assert cat.name == "Test Category"
    
    # Get
    fetched = await service.get_category(cat.id)
    assert fetched.name == "Test Category"
    
    # List
    cats, count = await service.list_categories()
    assert count > 0
    
    # Update
    update_req = CategoryRequest(name="Updated Category")
    updated = await service.update_category(cat.id, update_req)
    assert updated.name == "Updated Category"
    
    # Delete
    deleted = await service.delete_category(cat.id)
    assert deleted is True
    
    with pytest.raises(EntityNotFoundError):
        await service.get_category(cat.id)

@pytest.mark.asyncio
async def test_tag_crud(db_session: AsyncSession):
    service = TagService(db_session)
    
    # Create
    req = TagRequest(name="Test Tag")
    tag = await service.create_tag(req)
    assert tag.name == "Test Tag"
    
    # Delete
    deleted = await service.delete_tag(tag.id)
    assert deleted is True

@pytest.mark.asyncio
async def test_document_creation_and_rules(db_session: AsyncSession):
    # Setup dependencies
    cat_service = CategoryService(db_session)
    tag_service = TagService(db_session)
    doc_service = DocumentService(db_session)
    
    cat = await cat_service.create_category(CategoryRequest(name="Doc Cat"))
    tag1 = await tag_service.create_tag(TagRequest(name="Tag1"))
    tag2 = await tag_service.create_tag(TagRequest(name="Tag2"))
    
    # Assume a user exists from migrations (we get it from DB)
    from database.repositories.user import UserRepository
    user_repo = UserRepository(db_session)
    users = await user_repo.list()
    owner_id = users[0].id
    
    # Create Document
    doc_req = CreateDocumentRequest(
        title="My Document",
        description="A test doc",
        owner_id=owner_id,
        category_id=cat.id,
        tag_ids=[tag1.id, tag2.id]
    )
    doc = await doc_service.create_document(doc_req)
    
    assert doc.title == "My Document"
    assert doc.current_version == 1
    assert len(doc.tags) == 2
    
    # Verify version was created
    from database.repositories.version import VersionRepository
    version_repo = VersionRepository(db_session)
    versions = await version_repo.list_by_document(doc.id)
    assert len(versions) == 1
    assert versions[0].version_number == 1
    
    # Test Category Deletion restriction
    with pytest.raises(ForbiddenError):
        await cat_service.delete_category(cat.id)
    
    # Test Duplicate Tag Rejection
    doc_req_dup_tags = CreateDocumentRequest(
        title="Dup Tags",
        owner_id=owner_id,
        category_id=cat.id,
        tag_ids=[tag1.id, tag1.id]
    )
    with pytest.raises(ValidationException, match="Duplicate tags"):
        await doc_service.create_document(doc_req_dup_tags)
