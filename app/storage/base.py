from abc import ABC, abstractmethod
from typing import AsyncGenerator
from uuid import UUID

class StorageProvider(ABC):
    """
    Abstract interface for all storage providers.
    Does not depend on any business models or database transactions.
    """

    @abstractmethod
    async def save_file(self, document_id: UUID, storage_identifier: str, file_stream: AsyncGenerator[bytes, None]) -> int:
        """
        Saves a file stream to storage.
        Returns the total number of bytes written.
        """

    @abstractmethod
    async def read_file(self, document_id: UUID, storage_identifier: str) -> AsyncGenerator[bytes, None]:
        """
        Returns an async generator yielding chunks of the requested file.
        """

    @abstractmethod
    async def delete_file(self, document_id: UUID, storage_identifier: str) -> bool:
        """
        Deletes the physical file from storage.
        Returns True if deleted, False if it did not exist.
        """

    @abstractmethod
    async def exists(self, document_id: UUID, storage_identifier: str) -> bool:
        """
        Checks if the physical file exists in storage.
        """

    @abstractmethod
    async def get_file_size(self, document_id: UUID, storage_identifier: str) -> int:
        """
        Returns the exact byte size of the file in storage.
        Raises an exception if the file does not exist.
        """

    @abstractmethod
    def generate_storage_identifier(self) -> str:
        """
        Generates an opaque storage identifier string (e.g., a UUID string).
        """
