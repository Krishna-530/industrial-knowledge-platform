from typing import AsyncGenerator
from app.llm.interfaces.normalizer import AbstractStreamNormalizer
from app.llm.models.response import StreamChunk

class StreamNormalizerMiddleware:
    def __init__(self, normalizer: AbstractStreamNormalizer):
        self.normalizer = normalizer

    async def normalize_stream(self, assembled_stream: AsyncGenerator[any, None]) -> AsyncGenerator[StreamChunk, None]:
        async for raw_chunk in assembled_stream:
            yield self.normalizer.normalize_chunk(raw_chunk)
