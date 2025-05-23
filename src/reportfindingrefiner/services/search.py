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

def compare_search_methods(table, query: str, limit: int = 5):
    """
    Compare results from different search methods for debugging.
    """
    # Create fresh FTS index for basic search
    table.create_fts_index("text", use_tantivy=False, replace=True)

    


    # Perform searches
    basic_results = table.search(query).limit(limit).to_list()
    vector_results = table.search(query, query_type="vector").limit(limit).to_list()
    
    print(f"\nSearch Query: '{query}'\n")
    
    # Compare result sets
    basic_texts = {r['text'] for r in basic_results}
    vector_texts = {r['text'] for r in vector_results}
    
    print("Basic-only matches:")
    for text in basic_texts - vector_texts:
        print(f"- {text[:100]}...")

    # print the basic results
    print("\nBasic results:")
    for r in basic_results:
        print(f"Text: {r['text'][:100]}...")
        
    print("\nVector-only matches:")
    for text in vector_texts - basic_texts:
        print(f"- {text[:100]}...")

    # print the vector results
    print("\nVector results:")
    for r in vector_results:
        print(f"Text: {r['text'][:100]}...")

        
    print("\nOverlap:", len(basic_texts & vector_texts))
    print("Basic total:", len(basic_texts))
    print("Vector total:", len(vector_texts))
    
    # Test semantic understanding with a variation of the original query
    semantic_query = f"complications related to {query}"  # Semantic variation of user query
    semantic_results = table.search(semantic_query, query_type="vector").limit(limit).to_list()
    
    print(f"\nSemantic query test: '{semantic_query}'")
    for r in semantic_results:
        print(f"Distance: {r.get('_distance', 'N/A')}")
        print(f"Text: {r['text'][:100]}...\n")

    # insepecting the score and distance
   