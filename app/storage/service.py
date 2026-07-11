import hashlib
from typing import AsyncGenerator, Tuple
from uuid import UUID
import logging
from app.storage.base import StorageProvider

logger = logging.getLogger(__name__)

class StorageService:
    def __init__(self, provider: StorageProvider):
        self.provider = provider

    async def save_file(self, document_id: UUID, file_stream: AsyncGenerator[bytes, None]) -> Tuple[str, int, str]:
        """
        Saves a file, computes SHA-256 checksum, and verifies integrity.
        Returns: (storage_identifier, bytes_written, checksum_hex)
        """
        storage_identifier = self.provider.generate_storage_identifier()
        hasher = hashlib.sha256()

        async def stream_wrapper() -> AsyncGenerator[bytes, None]:
            async for chunk in file_stream:
                hasher.update(chunk)
                yield chunk

        logger.info({"event": "storage_write_start", "storage_identifier": storage_identifier})
        
        try:
            bytes_written = await self.provider.save_file(
                document_id=document_id,
                storage_identifier=storage_identifier,
                file_stream=stream_wrapper()
            )
        except Exception as e:
            logger.error({"event": "storage_write_failed", "storage_identifier": storage_identifier, "error": str(e)})
            raise

        checksum = hasher.hexdigest()

        # Integrity verification
        if not await self.provider.exists(document_id, storage_identifier):
            raise Exception(f"Integrity check failed: File {storage_identifier} does not exist after write")
            
        actual_size = await self.provider.get_file_size(document_id, storage_identifier)
        if actual_size != bytes_written:
            # Cleanup on integrity failure
            await self.provider.delete_file(document_id, storage_identifier)
            raise Exception(f"Integrity check failed: Expected {bytes_written} bytes but found {actual_size} bytes")

        logger.info({
            "event": "storage_write_complete", 
            "storage_identifier": storage_identifier, 
            "bytes_written": bytes_written
        })
        
        return storage_identifier, bytes_written, checksum

    async def read_file(self, document_id: UUID, storage_identifier: str) -> AsyncGenerator[bytes, None]:
        logger.info({"event": "storage_read_start", "storage_identifier": storage_identifier})
        # Wrap generator to log errors, etc. if needed, or just return it
        # Note: read_file in base returns AsyncGenerator
        return await self.provider.read_file(document_id, storage_identifier)

    async def delete_file(self, document_id: UUID, storage_identifier: str) -> bool:
        logger.info({"event": "storage_delete", "storage_identifier": storage_identifier})
        return await self.provider.delete_file(document_id, storage_identifier)
    
    async def exists(self, document_id: UUID, storage_identifier: str) -> bool:
        return await self.provider.exists(document_id, storage_identifier)
