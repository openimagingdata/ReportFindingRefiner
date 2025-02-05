from typing import List
from .lance_db import connect_db
import pandas as pd

#TODO: Refactor this so that a new Index isnt created every time; move to search_in_db function

def basic_search(table, query: str, limit: int = 10):
    """
    Perform a basic full-text search.
    """
    # If needed, create or replace an FTS index:
    table.create_fts_index("text", use_tantivy=False, replace=True)
    return table.search(query).limit(limit).to_list()

def hybrid_search(table, query: str, limit: int = 10):
    """
    Perform a hybrid (keyword + vector) search.
    """
    return table.search(query, query_type="hybrid").limit(limit).to_list()

def vector_search(table, query: str, limit: int = 10):
    """
    Perform a vector-based semantic search.
    """
    return table.search(query, query_type="vector").limit(limit).to_list()

def find_fragments_containing_text(table, search_text: str):
    """
    Example of filtering the entire table by a substring match (case-insensitive).
    """
    df = table.to_pandas()
    filtered = df[df['text'].str.contains(search_text, case=False, na=False)]
    return filtered[['text', 'section']]

def search_in_db(db_path: str, table_name: str, query_str: str, mode: str = "basic"):
    """
    High-level function to connect to DB, run a search, and return results.
    """
    db = connect_db(db_path)
    table = db.open_table(table_name)

    if mode == "basic":
        return basic_search(table, query_str)
    elif mode == "hybrid":
        return hybrid_search(table, query_str)
    elif mode == "vector":
        return vector_search(table, query_str)
    else:
        raise ValueError(f"Unknown search mode: {mode}")