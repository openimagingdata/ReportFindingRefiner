from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from reportfindingrefiner.config import (
    DEFAULT_DB_PATH,
    DEFAULT_TABLE_NAME, 
    DEFAULT_SEARCH_MODE,
    DEFAULT_LIMIT
)
from reportfindingrefiner.services.search_service import SearchService

# Initialize router
router = APIRouter(tags=["search"])

# Initialize service
search_service = SearchService(db_path=DEFAULT_DB_PATH, table_name=DEFAULT_TABLE_NAME)

# Define request models
class SearchQuery(BaseModel):
    query: str
    mode: str = DEFAULT_SEARCH_MODE
    limit: int = DEFAULT_LIMIT

@router.post("")
async def search_text(query: SearchQuery):
    """
    Search for text in reports using the specified search mode.
    """
    try:
        results = search_service.search(
            query=query.query,
            mode=query.mode,
            limit=query.limit
        )
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error performing search: {str(e)}")

@router.post("/compare")
async def compare_search_methods(query: SearchQuery):
    """
    Compare different search methods for the given query.
    """
    try:
        comparison = search_service.compare_search_methods(
            query=query.query,
            limit=query.limit
        )
        return comparison
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error comparing search methods: {str(e)}") 