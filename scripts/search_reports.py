#!/usr/bin/env python

"""
Command-line script to demonstrate searching.
Usage:
    python scripts/search_reports.py --query "fatty liver" --mode hybrid --reports_folder ./reports
    python scripts/search_reports.py --query "fatty liver" --compare --reports_folder ./reports
"""

import argparse
import os
from reportfindingrefiner.search import search_in_db, find_fragments_containing_text, compare_search_methods
from reportfindingrefiner.lance_db import connect_db, create_fragment_table
from reportfindingrefiner.ingestion import read_reports_from_folder, create_fragments_from_reports
from reportfindingrefiner.section_splitter import SectionSplitter

def setup_test_db(db_path: str, table_name: str, reports_folder: str):
    """Set up test database with reports if it doesn't exist"""
    db = connect_db(db_path)
    
    # Create and populate table
    table = create_fragment_table(db, table_name=table_name)
    
    # Read and process reports
    reports_list = read_reports_from_folder(reports_folder)
    splitter = SectionSplitter()
    all_fragments = create_fragments_from_reports(reports_list, splitter)
    
    # Prepare and insert documents
    docs = [{
        "report_id": frag.report_id,
        "section": frag.section,
        "sequence_number": frag.sequence_number,
        "text": frag.text
    } for frag in all_fragments]
    
    table.add(docs)
    return table

def main():
    parser = argparse.ArgumentParser(description="Search LanceDB for matching text.")
    parser.add_argument("--query", type=str, required=True, help="Search query string.")
    parser.add_argument("--mode", type=str, default="basic", choices=["basic", "hybrid", "vector"],
                        help="Search mode to use.")
    parser.add_argument("--db_path", type=str, default="./data/lancedb_search_test", help="Path to LanceDB folder.")
    parser.add_argument("--table_name", type=str, default="reports", help="LanceDB table name.")
    parser.add_argument("--reports_folder", type=str, required=True, help="Folder containing report text files.")
    parser.add_argument("--filter_only", action="store_true", help="Just filter rows, ignoring index-based search.")
    parser.add_argument("--compare", action="store_true", help="Run comparison between search methods.")
    args = parser.parse_args()

    # Create specific directory for search testing
    os.makedirs(args.db_path, exist_ok=True)
    
    try:
        db = connect_db(args.db_path)
        table = db.open_table(args.table_name)
    except FileNotFoundError:
        print(f"Creating new test database in {args.db_path}")
        table = setup_test_db(args.db_path, args.table_name, args.reports_folder)

    if args.compare:
        compare_search_methods(table, args.query)
    elif args.filter_only:
        db_results = find_fragments_containing_text(table, args.query)
        print(db_results)
    else:
        results = search_in_db(args.db_path, args.table_name, args.query, mode=args.mode)
        print(f"Search results using mode={args.mode}:")
        for r in results:
            print(f"Score: {r.get('_score', 'N/A')}, Text: {r['text']}, Section: {r['section']}")

if __name__ == "__main__":
    main()