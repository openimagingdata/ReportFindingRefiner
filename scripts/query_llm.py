#!/usr/bin/env python

import argparse
from reportfindingrefiner.search import search_in_db
from reportfindingrefiner.llm_query import query_llm

def main():
    parser = argparse.ArgumentParser(description="Query an LLM with context from LanceDB.")
    parser.add_argument("--query", required=True, help="The query to ask the LLM.")
    parser.add_argument("--db_path", default="./data/lancedb", help="Path to LanceDB folder.")
    parser.add_argument("--table_name", default="table", help="LanceDB table name.")
    parser.add_argument("--model", default="llama3.3", help="Ollama model to use.")
    parser.add_argument("--limit", type=int, default=5, help="Number of context fragments to retrieve.")
    args = parser.parse_args()

#NOTE: add to args the type of search to use, for now just default to basic 
    # 1. Retrieve context documents
    results = search_in_db(args.db_path, args.table_name, args.query, mode="basic")[:args.limit]
    context_docs = [r['text'] for r in results]

    # 2. Query LLM
    answer = query_llm(args.query, context_docs, model=args.model)
    print("LLM Answer:\n", answer)

if __name__ == "__main__":
    main()