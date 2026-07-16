from typing import Any, Dict
from app.tools.interfaces.abstract_tool import AbstractTool
from app.tools.models.tool_context import ToolContext
from app.tools.models.document_read_result import DocumentReadResult
from app.services.document_service import DocumentService
from core.exceptions.document import EntityNotFoundError
from core.exceptions.auth import ForbiddenError

class DocumentReaderTool(AbstractTool):
    def __init__(self, document_service: DocumentService):
        self.document_service = document_service
        
    async def execute(self, arguments: Dict[str, Any], context: ToolContext) -> Any:
        document_id = arguments.get("document_id")
        if not document_id:
            raise ValueError("Missing 'document_id' argument")
            
        try:
            # DocumentService will fetch the doc and ensure it belongs to context.workspace_id
            doc = await self.document_service.get_document(document_id)
            if doc.workspace_id != context.workspace_id:
                raise ForbiddenError("Access denied to this document")
                
            # For phase 8.2, we just return mocked content, in reality it fetches raw text
            return DocumentReadResult(
                document_id=document_id,
                text_content=f"Content for document {document_id}",
                metadata=doc.metadata if hasattr(doc, 'metadata') else {}
            )
        except EntityNotFoundError:
            raise ValueError(f"Document {document_id} not found")
