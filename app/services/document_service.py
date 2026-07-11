from typing import List, Tuple, Optional, AsyncGenerator
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from database.repositories.document import DocumentRepository
from database.repositories.version import VersionRepository
from database.repositories.user import UserRepository
from database.repositories.category import CategoryRepository
from database.repositories.tag import TagRepository
from api.v1.schemas.document import CreateDocumentRequest, UpdateDocumentRequest
from core.exceptions import EntityNotFoundError, ValidationException, ForbiddenError
from core.enums import DocumentStatus
from core.settings import Settings
from app.storage.service import StorageService

logger = logging.getLogger(__name__)

class DocumentService:
    def __init__(self, session: AsyncSession, storage_service: Optional[StorageService] = None):
        self.session = session
        self.document_repo = DocumentRepository(session)
        self.version_repo = VersionRepository(session)
        self.user_repo = UserRepository(session)
        self.category_repo = CategoryRepository(session)
        self.tag_repo = TagRepository(session)
        self.storage_service = storage_service
        self.settings = Settings()

    async def _validate_owner(self, owner_id: UUID):
        user = await self.user_repo.get_by_id(owner_id)
        if not user:
            raise EntityNotFoundError(message="Owner not found")
        if not user.is_active:
            raise ValidationException(message="Only active users may be assigned as document owners")

    async def _validate_category(self, category_id: UUID):
        category = await self.category_repo.get_by_id(category_id)
        if not category:
            raise EntityNotFoundError(message="Category not found")

    async def _validate_tags(self, tag_ids: List[UUID]) -> List:
        if len(tag_ids) != len(set(tag_ids)):
            raise ValidationException(message="Duplicate tags on the same document are rejected")
        
        tags = []
        for tag_id in tag_ids:
            tag = await self.tag_repo.get_by_id(tag_id)
            if not tag:
                raise EntityNotFoundError(message=f"Tag {tag_id} not found")
            tags.append(tag)
        return tags

    async def create_document(self, data: CreateDocumentRequest):
        await self._validate_owner(data.owner_id)
        await self._validate_category(data.category_id)
        tags = await self._validate_tags(data.tag_ids)

        doc = await self.document_repo.create(
            title=data.title,
            description=data.description,
            owner_id=data.owner_id,
            category_id=data.category_id,
            tags=tags
        )
        
        # Version Initialization Rule
        await self.version_repo.create(
            document_id=doc.id,
            version_number=1,
            uploaded_by=data.owner_id
        )

        await self.session.commit()
        
        # Refresh the doc to get versions and tags populated if needed
        await self.session.refresh(doc, ["tags", "versions"])
        return doc

    async def get_document(self, document_id: UUID):
        doc = await self.document_repo.get_by_id(document_id)
        if not doc:
            raise EntityNotFoundError(message="Document not found")
        return doc

    async def list_documents(
        self, 
        limit: int = 50, 
        offset: int = 0,
        owner_id: Optional[UUID] = None,
        category_id: Optional[UUID] = None,
        status: Optional[DocumentStatus] = None,
        title_search: Optional[str] = None
    ) -> Tuple[List, int]:
        return await self.document_repo.list(
            limit=limit, 
            offset=offset,
            owner_id=owner_id,
            category_id=category_id,
            status=status,
            title_search=title_search
        )

    async def update_document(self, document_id: UUID, data: UpdateDocumentRequest):
        doc = await self.get_document(document_id)
        
        if data.owner_id is not None:
            await self._validate_owner(data.owner_id)
        
        if data.category_id is not None:
            await self._validate_category(data.category_id)

        update_data = data.model_dump(exclude_unset=True)
        
        tags = None
        if "tag_ids" in update_data:
            tag_ids = update_data.pop("tag_ids")
            tags = await self._validate_tags(tag_ids)
            update_data["tags"] = tags

        if not update_data and tags is None:
            return doc

        updated = await self.document_repo.update(document_id, **update_data)
        await self.session.commit()
        return updated

    async def delete_document(self, document_id: UUID):
        # Database CASCADE handles versions and tags
        deleted = await self.document_repo.delete(document_id)
        if not deleted:
            raise EntityNotFoundError(message="Document not found")
        await self.session.commit()
        return True

    async def validate_and_lock_for_upload(self, document_id: UUID, content_length: Optional[int] = None):
        if content_length and content_length > self.settings.max_upload_size:
            raise ValidationException(message="File exceeds maximum upload size")
            
        doc = await self.document_repo.get_by_id_for_update(document_id)
        if not doc:
            raise EntityNotFoundError(message="Document not found")
        if doc.status == DocumentStatus.ARCHIVED:
            raise ForbiddenError(message="Cannot upload to an archived document")
            
        return doc

    async def create_document_version(self, document_id: UUID, version_number: int, user_id: UUID, storage_identifier: str, checksum: str):
        doc = await self.document_repo.get_by_id(document_id)
        doc.current_version = version_number
        
        version = await self.version_repo.create(
            document_id=document_id,
            version_number=version_number,
            uploaded_by=user_id,
            storage_identifier=storage_identifier,
            checksum=checksum
        )
        
        try:
            await self.session.commit()
            return version
        except Exception as e:
            logger.error({"event": "version_commit_failed", "error": str(e)})
            await self.session.rollback()
            raise

    async def get_download_stream(self, document_id: UUID, version_number: Optional[int] = None) -> Tuple[AsyncGenerator[bytes, None], str, int]:
        if version_number is None:
            version = await self.version_repo.get_latest_version(document_id)
        else:
            versions = await self.version_repo.list_by_document(document_id)
            version = next((v for v in versions if v.version_number == version_number), None)
            
        if not version or not version.storage_identifier:
            raise EntityNotFoundError(message="Document version or file not found")
            
        doc = await self.get_document(document_id)
            
        if not await self.storage_service.exists(document_id, version.storage_identifier):
            logger.warning({"event": "missing_file", "storage_identifier": version.storage_identifier})
            raise EntityNotFoundError(message="File missing from storage")
            
        file_size = await self.storage_service.provider.get_file_size(document_id, version.storage_identifier)
        stream = await self.storage_service.read_file(document_id, version.storage_identifier)
        filename = f"{doc.title}_v{version.version_number}"
        return stream, filename, file_size

