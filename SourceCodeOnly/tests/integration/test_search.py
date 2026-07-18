import pytest
from app.search.schemas import SearchQuery

@pytest.mark.asyncio
async def test_search_schemas():
    query = SearchQuery(query_text="factory automation")
    assert query.query_text == "factory automation"
    assert query.language == "english"
    assert query.limit == 10
