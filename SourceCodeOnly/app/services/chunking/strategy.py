import abc
from typing import List, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter
import tiktoken

class AbstractChunkingStrategy(abc.ABC):
    @abc.abstractmethod
    def chunk(self, text: str) -> List[str]:
        pass

class RecursiveChunkingStrategy(AbstractChunkingStrategy):
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 100):
        # We use tiktoken for token-aware splitting to match OpenAI standards
        self.splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            encoding_name="cl100k_base",
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

    def chunk(self, text: str) -> List[str]:
        # Clean any null bytes or extreme whitespace before splitting
        cleaned_text = text.replace('\x00', '')
        return self.splitter.split_text(cleaned_text)
