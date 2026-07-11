from typing import List
from app.context.interfaces import AbstractContextFormatter
from app.context.schemas import ContextChunk, FormattedContext, ContextFormat

class MarkdownContextFormatter(AbstractContextFormatter):
    """
    Formats the finalized chunks into a Markdown string.
    """
    def format_chunks(self, chunks: List[ContextChunk]) -> FormattedContext:
        parts = ["# Context Assembly"]
        for chunk in chunks:
            parts.append(f"## Chunk: {chunk.chunk_id}")
            parts.append(f"**Source**: {chunk.source_uri or 'unknown'}")
            parts.append("\n```text")
            parts.append(chunk.content)
            parts.append("```\n")
            
        return FormattedContext(
            formatted_string="\n".join(parts),
            format_type=ContextFormat.MARKDOWN
        )
