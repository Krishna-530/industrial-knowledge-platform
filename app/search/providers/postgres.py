import logging
from uuid import UUID
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, text, and_
from app.search.interfaces import AbstractSearchProvider
from app.search.schemas import SearchQuery, SearchResult, SearchResultPage
from database.models.document import Document
from database.models.document_version import DocumentVersion
from database.models.document_content import DocumentContent

logger = logging.getLogger(__name__)

class PostgresSearchProvider(AbstractSearchProvider):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def index_document(self, document_version_id: UUID, content: str, language: str, metadata: dict) -> None:
        await self.update_document(document_version_id, content, language, metadata)

    async def update_document(self, document_version_id: UUID, content: str, language: str, metadata: dict) -> None:
        try:
            stmt = text('''
                UPDATE document_contents
                SET search_vector = to_tsvector(:language, :content),
                    language = :language
                WHERE document_version_id = :version_id
            ''')
            await self.session.execute(stmt, {
                "language": language,
                "content": content,
                "version_id": document_version_id
            })
        except Exception as e:
            logger.error({"event": "postgres_update_document_failed", "error": str(e)})
            raise

    async def delete_document(self, document_version_id: UUID) -> None:
        stmt = text('''
            UPDATE document_contents
            SET search_vector = NULL
            WHERE document_version_id = :version_id
        ''')
        await self.session.execute(stmt, {"version_id": document_version_id})
        
    async def clear_previous_versions(self, document_id: UUID, exclude_version_id: UUID) -> None:
        stmt = text('''
            UPDATE document_contents dc
            SET search_vector = NULL
            FROM document_versions dv
            WHERE dc.document_version_id = dv.id
              AND dv.document_id = :document_id
              AND dv.id != :exclude_version_id
        ''')
        await self.session.execute(stmt, {
            "document_id": document_id,
            "exclude_version_id": exclude_version_id
        })

    async def rebuild_index(self, batch_size: int = 100) -> None:
        # Backfills search vectors from raw_text
        stmt = text('''
            UPDATE document_contents
            SET search_vector = to_tsvector(language, coalesce(raw_text, ''))
            WHERE search_vector IS NULL AND raw_text IS NOT NULL
        ''')
        await self.session.execute(stmt)

    async def search(self, query: SearchQuery) -> SearchResultPage:
        base_query = """
            FROM document_contents dc
            JOIN document_versions dv ON dc.document_version_id = dv.id
            JOIN documents d ON dv.document_id = d.id
            WHERE dc.search_vector @@ websearch_to_tsquery(:language, :query_text)
        """
        
        params = {
            "language": query.language,
            "query_text": query.query_text,
            "limit": query.limit,
            "offset": query.offset
        }
        
        if query.category_id:
            base_query += " AND d.category_id = :category_id"
            params["category_id"] = query.category_id
            
        if query.document_ids:
            base_query += " AND d.id = ANY(:document_ids)"
            params["document_ids"] = [str(did) for did in query.document_ids]
            
        count_stmt = text(f"SELECT COUNT(*) {base_query}")
        count_result = await self.session.execute(count_stmt, params)
        total_count = count_result.scalar()
        
        order_by = "score DESC"
        if query.sort_order == "date_desc":
            order_by = "d.created_at DESC"
        elif query.sort_order == "date_asc":
            order_by = "d.created_at ASC"
            
        select_stmt = text(f"""
            SELECT 
                d.id AS document_id,
                dv.id AS document_version_id,
                d.title AS title,
                d.category_id AS category_id,
                ts_rank_cd(dc.search_vector, websearch_to_tsquery(:language, :query_text)) AS score,
                ts_headline(:language, dc.raw_text, websearch_to_tsquery(:language, :query_text), 'StartSel=<b>, StopSel=</b>, MaxWords=35, MinWords=15') AS highlight
            {base_query}
            ORDER BY {order_by}
            LIMIT :limit OFFSET :offset
        """)
        
        result = await self.session.execute(select_stmt, params)
        items = []
        for row in result.mappings():
            items.append(SearchResult(
                document_id=row["document_id"],
                document_version_id=row["document_version_id"],
                score=float(row["score"]),
                highlight=row["highlight"],
                title=row["title"],
                category_id=row["category_id"]
            ))
            
        return SearchResultPage(
            items=items,
            total_count=total_count,
            has_more=(query.offset + query.limit) < total_count
        )

    async def health_check(self) -> bool:
        try:
            await self.session.execute(text("SELECT 1"))
            return True
        except:
            return False
