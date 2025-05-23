#!/usr/bin/env python

"""
Command-line script to demonstrate searching using the SearchService.
Usage:
    python scripts/search_reports.py --query "fatty liver" --mode hybrid
    python scripts/search_reports.py --query "fatty liver" --compare
"""

import argparse
import os
import json
from reportfindingrefiner.services.search_service import SearchService
from reportfindingrefiner.services.report_service import ReportService
from reportfindingrefiner.config import DEFAULT_DB_PATH

def main():
    parser = argparse.ArgumentParser(description="Search LanceDB for matching text.")
    parser.add_argument("--query", type=str, required=True, help="Search query string.")
    parser.add_argument("--mode", type=str, default="basic", choices=["basic", "hybrid", "vector"],
                        help="Search mode to use.")
    parser.add_argument("--db_path", type=str, default=DEFAULT_DB_PATH, help="Path to LanceDB folder.")
    parser.add_argument("--table_name", type=str, default="reports", help="LanceDB table name.")
    parser.add_argument("--reports_folder", type=str, default="./data/reports", help="Folder containing report text files.")
    parser.add_argument("--compare", action="store_true", help="Run comparison between search methods.")
    parser.add_argument("--limit", type=int, default=10, help="Maximum number of results to return.")
    args = parser.parse_args()

    # Create specific directory for search testing if needed
    os.makedirs(args.db_path, exist_ok=True)
    
    # Check if reports table exists, if not, ingest reports
    try:
        # Initialize the SearchService
        search_service = SearchService(db_path=args.db_path, table_name=args.table_name)
        
        # Try to connect and check if the table exists
        search_service._ensure_connection()
        
    except Exception as e:
        print(f"Error connecting to DB: {str(e)}")
        print(f"Ingesting reports from {args.reports_folder}...")
        
        # Initialize the ReportService to ingest reports
        report_service = ReportService(db_path=args.db_path, table_name=args.table_name)
        fragment_count = report_service.ingest_reports(args.reports_folder)
        print(f"Ingested {fragment_count} fragments.")

    if args.compare:
        # Use the compare_search_methods from SearchService
        comparison = search_service.compare_search_methods(args.query, limit=args.limit)
        
        # Print the results in a readable format
        print(f"\nSearch Query: '{comparison['query']}'\n")
        
        # Compare basic and vector matches
        basic_texts = {r['text'] for r in comparison['basic_results']}
        vector_texts = {r['text'] for r in comparison['vector_results']}
        
        print("Basic-only matches:")
        for text in comparison['basic_only']:
            print(f"- {text[:100]}...")
            
        print("\nBasic results:")
        for r in comparison['basic_results']:
            print(f"Text: {r['text'][:100]}...")
        
        print("\nVector-only matches:")
        for text in comparison['vector_only']:
            print(f"- {text[:100]}...")
            
        print("\nVector results:")
        for r in comparison['vector_results']:
            print(f"Text: {r['text'][:100]}...")
            
        print("\nOverlap:", comparison['overlap_count'])
        print("Basic total:", comparison['basic_total'])
        print("Vector total:", comparison['vector_total'])
        
        print(f"\nSemantic query test: '{comparison['semantic_query']}'")
        for r in comparison['semantic_results']:
            print(f"Distance: {r.get('_distance', 'N/A')}")
            print(f"Text: {r['text'][:100]}...\n")
    else:
        # Perform a regular search
        results = search_service.search(args.query, mode=args.mode, limit=args.limit)
        
        print(f"Search results using mode={args.mode}:")
        for r in results:
            print(f"Score: {r.get('_score', 'N/A')}, Text: {r['text'][:100]}..., Section: {r['section']}")
        
        # Save the results to a JSON file for reference
        with open(f"search_results_{args.mode}.json", "w") as f:
            json.dump([{k: str(v) for k, v in r.items()} for r in results], f, indent=2)
        print(f"\nResults saved to search_results_{args.mode}.json")

if __name__ == "__main__":
    main()