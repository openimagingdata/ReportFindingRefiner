from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from reportfindingrefiner.config import DEFAULT_MODEL
from reportfindingrefiner.services.llm_service import LLMService
from reportfindingrefiner.services.search_service import SearchService

# Initialize router
router = APIRouter(tags=["llm"])

# Initialize services
llm_service = LLMService(model=DEFAULT_MODEL)
search_service = SearchService()

class Query(BaseModel):
    prompt: str
    model: str = DEFAULT_MODEL

class QueryWithContextRequest(BaseModel):
    query: str
    search_query: str
    search_mode: str = "basic"
    search_limit: int = 5
    model: str = DEFAULT_MODEL

@router.post("/chat")
async def chat(query: Query):
    """
    Send a prompt to the LLM and get a response.
    """
    try:
        response = llm_service.query(prompt=query.prompt, model=query.model)
        return {"generated_text": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error communicating with LLM: {str(e)}")

@router.post("/query-with-context")
async def query_with_context(request: QueryWithContextRequest):
    """
    Query the LLM with context from a search query.
    """
    try:
        # First, search for context
        context_docs = search_service.search(
            query=request.search_query,
            mode=request.search_mode,
            limit=request.search_limit
        )
        
        # Then query the LLM with the context
        response = llm_service.query_with_context(
            query=request.query,
            context_docs=context_docs
        )
        
        return {
            "query": request.query,
            "search_query": request.search_query,
            "context_count": len(context_docs),
            "generated_text": response
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying with context: {str(e)}") 