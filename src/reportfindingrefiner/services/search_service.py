from typing import List, Dict, Any, Optional
import pandas as pd
from ..lance_db import connect_db
from ..config import (
    DEFAULT_DB_PATH, 
    DEFAULT_TABLE_NAME,
    DEFAULT_LIMIT
)

class SearchService:
    """
    Service for searching report fragments in LanceDB.
    This class encapsulates all search functionality to provide a clean,
    consistent interface for both the API and CLI.
    """
    
    def __init__(self, db_path: str = DEFAULT_DB_PATH, table_name: str = DEFAULT_TABLE_NAME):
        """Initialize the search service with database connection details"""
        self.db_path = db_path
        self.table_name = table_name
        self.db = None
        self.table = None
        
    def _ensure_connection(self):
        """Ensure connection to the database and table"""
        if self.db is None:
            self.db = connect_db(self.db_path)
        if self.table is None:
            self.table = self.db.open_table(self.table_name)
        return self.table
    
    def search_basic(self, query: str, limit: int = DEFAULT_LIMIT) -> List[Dict[str, Any]]:
        """Perform a basic full-text search"""
        table = self._ensure_connection()
        # Create or replace an FTS index
        table.create_fts_index("text", use_tantivy=False, replace=True)
        return table.search(query).limit(limit).to_list()
    
    def search_vector(self, query: str, limit: int = DEFAULT_LIMIT) -> List[Dict[str, Any]]:
        """Perform a vector-based semantic search"""
        table = self._ensure_connection()
        return table.search(query, query_type="vector").limit(limit).to_list()
    
    def search_hybrid(self, query: str, limit: int = DEFAULT_LIMIT) -> List[Dict[str, Any]]:
        """Perform a hybrid (keyword + vector) search"""
        table = self._ensure_connection()
        return table.search(query, query_type="hybrid").limit(limit).to_list()
    
    def search(self, query: str, mode: str = "basic", limit: int = DEFAULT_LIMIT) -> List[Dict[str, Any]]:
        """
        High-level search function that determines which search method to use based on mode.
        
        Args:
            query: The search query string
            mode: Search mode - "basic", "vector", or "hybrid"
            limit: Maximum number of results to return
            
        Returns:
            List of matching documents
        """
        if mode == "basic":
            return self.search_basic(query, limit)
        elif mode == "vector":
            return self.search_vector(query, limit)
        elif mode == "hybrid":
            return self.search_hybrid(query, limit)
        else:
            raise ValueError(f"Unknown search mode: {mode}")
    
    def find_fragments_containing_text(self, search_text: str) -> pd.DataFrame:
        """
        Find fragments containing the exact text (case-insensitive substring match)
        
        Returns:
            DataFrame with matching fragments
        """
        table = self._ensure_connection()
        df = table.to_pandas()
        filtered = df[df['text'].str.contains(search_text, case=False, na=False)]
        return filtered[['text', 'section']]
    
    def compare_search_methods(self, query: str, limit: int = 5) -> Dict[str, Any]:
        """
        Compare results from different search methods for debugging
        
        Returns:
            Dictionary containing the comparison results
        """
        table = self._ensure_connection()
        
        # Create fresh FTS index for basic search
        table.create_fts_index("text", use_tantivy=False, replace=True)
        
        # Perform searches
        basic_results = table.search(query).limit(limit).to_list()
        vector_results = table.search(query, query_type="vector").limit(limit).to_list()
        
        # Extract text for comparison
        basic_texts = {r['text'] for r in basic_results}
        vector_texts = {r['text'] for r in vector_results}
        
        # Test semantic understanding with a variation of the original query
        semantic_query = f"complications related to {query}"
        semantic_results = table.search(semantic_query, query_type="vector").limit(limit).to_list()
        
        return {
            "query": query,
            "basic_results": basic_results,
            "vector_results": vector_results,
            "semantic_query": semantic_query,
            "semantic_results": semantic_results,
            "basic_only": list(basic_texts - vector_texts),
            "vector_only": list(vector_texts - basic_texts),
            "overlap_count": len(basic_texts & vector_texts),
            "basic_total": len(basic_texts),
            "vector_total": len(vector_texts)
        } 