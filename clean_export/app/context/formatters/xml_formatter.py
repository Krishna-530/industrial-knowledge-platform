from typing import List
from app.context.interfaces import AbstractContextFormatter
from app.context.schemas import ContextChunk, FormattedContext, ContextFormat

class XMLContextFormatter(AbstractContextFormatter):
    """
    Formats the finalized chunks into an XML string.
    """
    def format_chunks(self, chunks: List[ContextChunk]) -> FormattedContext:
        parts = ["<context>"]
        for chunk in chunks:
            parts.append(f'  <chunk id="{chunk.chunk_id}">')
            parts.append(f'    <source>{chunk.source_uri or "unknown"}</source>')
            parts.append(f'    <content>{chunk.content}</content>')
            parts.append('  </chunk>')
        parts.append("</context>")
        
        return FormattedContext(
            formatted_string="\n".join(parts),
            format_type=ContextFormat.XML
        )
