from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status, UploadFile, File, Request, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from core.settings import Settings
from app.storage.local import LocalStorageProvider
from app.storage.service import StorageService

from api.v1.schemas.document import CreateDocumentRequest, UpdateDocumentRequest, DocumentResponse, DocumentListResponse
from core.enums import DocumentStatus
from database.engine import get_db_session
from dependencies.auth import get_current_user, RoleChecker
from app.services.document_service import DocumentService
from app.workflows.document_upload_workflow import DocumentUploadWorkflow
from api.v1.dependencies.providers import provide_document_upload_workflow

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(RoleChecker(["Admin"]))])
async def create_document(
    data: CreateDocumentRequest,
    db: AsyncSession = Depends(get_db_session)
):
    service = DocumentService(db)
    return await service.create_document(data)

@router.get("", response_model=DocumentListResponse, dependencies=[Depends(get_current_user)])
async def list_documents(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    owner: Optional[UUID] = Query(None),
    category: Optional[UUID] = Query(None),
    status: Optional[DocumentStatus] = Query(None),
    title_search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db_session)
):
    service = DocumentService(db)
    documents, total = await service.list_documents(
        limit=limit,
        offset=offset,
        owner_id=owner,
        category_id=category,
        status=status,
        title_search=title_search
    )
    return DocumentListResponse(items=documents, total=total)

@router.get("/{document_id}", response_model=DocumentResponse, dependencies=[Depends(get_current_user)])
async def get_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_db_session)
):
    service = DocumentService(db)
    return await service.get_document(document_id)

@router.patch("/{document_id}", response_model=DocumentResponse, dependencies=[Depends(RoleChecker(["Admin"]))])
async def update_document(
    document_id: UUID,
    data: UpdateDocumentRequest,
    db: AsyncSession = Depends(get_db_session)
):
    service = DocumentService(db)
    return await service.update_document(document_id, data)

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(RoleChecker(["Admin"]))])
async def delete_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_db_session)
):
    service = DocumentService(db)
    await service.delete_document(document_id)

@router.post("/{document_id}/upload", response_model=DocumentResponse, dependencies=[Depends(get_current_user)])
async def upload_document_version(
    document_id: UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db_session),
    user=Depends(get_current_user),
    workflow: DocumentUploadWorkflow = Depends(provide_document_upload_workflow)
):
    async def file_stream():
        # Ideally, we get chunk_size from settings or workflow, but here we can read manually
        while chunk := await file.read(1024 * 1024):
            yield chunk

    await workflow.execute(
        document_id=document_id,
        user_id=UUID(user.user_id),
        file_stream=file_stream(),
        content_type=file.content_type,
        content_length=file.size
    )
    
    # Return updated document
    return await service.get_document(document_id)

@router.get("/{document_id}/download", dependencies=[Depends(get_current_user)])
async def download_document(
    document_id: UUID,
    version: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db_session),
    storage_service: StorageService = Depends(get_storage_service)
):
    service = DocumentService(db, storage_service)
    stream, filename, file_size = await service.get_download_stream(document_id, version)
    
    return StreamingResponse(
        stream, 
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Length": str(file_size)
        }
    )
