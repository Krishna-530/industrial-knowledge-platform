import os
import uuid
import aiofiles
from typing import AsyncGenerator
from uuid import UUID
from app.storage.base import StorageProvider
import logging

logger = logging.getLogger(__name__)

class LocalStorageProvider(StorageProvider):
    def __init__(self, base_directory: str, chunk_size: int = 65536):
        self.base_directory = os.path.abspath(base_directory)
        self.chunk_size = chunk_size
        os.makedirs(self.base_directory, exist_ok=True)

    def _get_path(self, document_id: UUID, storage_identifier: str) -> str:
        # Structure: uploads/documents/<document_id>/<storage_identifier>
        safe_doc_id = str(document_id)
        # Ensure there are no path traversal components
        if ".." in storage_identifier or "/" in storage_identifier or "\\" in storage_identifier:
            raise ValueError("Invalid storage identifier")
            
        doc_dir = os.path.join(self.base_directory, "documents", safe_doc_id)
        return os.path.join(doc_dir, storage_identifier)

    async def save_file(self, document_id: UUID, storage_identifier: str, file_stream: AsyncGenerator[bytes, None]) -> int:
        file_path = self._get_path(document_id, storage_identifier)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        bytes_written = 0
        try:
            async with aiofiles.open(file_path, 'wb') as f:
                async for chunk in file_stream:
                    await f.write(chunk)
                    bytes_written += len(chunk)
            return bytes_written
        except Exception as e:
            logger.error(f"Failed to write file {file_path}: {e}")
            if os.path.exists(file_path):
                os.remove(file_path)
            raise

    async def read_file(self, document_id: UUID, storage_identifier: str) -> AsyncGenerator[bytes, None]:
        file_path = self._get_path(document_id, storage_identifier)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {storage_identifier}")
            
        async with aiofiles.open(file_path, 'rb') as f:
            while True:
                chunk = await f.read(self.chunk_size)
                if not chunk:
                    break
                yield chunk

    async def delete_file(self, document_id: UUID, storage_identifier: str) -> bool:
        file_path = self._get_path(document_id, storage_identifier)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                return True
            except OSError as e:
                logger.error(f"Failed to delete file {file_path}: {e}")
                return False
        return False

    async def exists(self, document_id: UUID, storage_identifier: str) -> bool:
        file_path = self._get_path(document_id, storage_identifier)
        return os.path.exists(file_path)

    async def get_file_size(self, document_id: UUID, storage_identifier: str) -> int:
        file_path = self._get_path(document_id, storage_identifier)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {storage_identifier}")
        return os.path.getsize(file_path)

    def generate_storage_identifier(self) -> str:
        return str(uuid.uuid4())
