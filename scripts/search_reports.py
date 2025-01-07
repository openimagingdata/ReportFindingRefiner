#!/usr/bin/env python

"""
Command-line script to demonstrate searching.
Usage:
    python scripts/search_reports.py --query "fatty liver" --mode hybrid
"""

import argparse
from reportfindingrefiner.search import search_in_db, find_fragments_containing_text


def main():
    parser = argparse.ArgumentParser(description="Search LanceDB for matching text.")
    parser.add_argument("--query", type=str, required=True, help="Search query string.")
    parser.add_argument("--mode", type=str, default="basic", choices=["basic", "hybrid", "vector"],
                        help="Search mode to use.")
    parser.add_argument("--db_path", type=str, default="./data/lancedb", help="Path to LanceDB folder.")
    parser.add_argument("--table_name", type=str, default="table", help="LanceDB table name.")
    parser.add_argument("--filter_only", action="store_true", help="Just filter rows, ignoring index-based search.")
    args = parser.parse_args()

    # Connect and open table
    if args.filter_only:
        # Simple substring filter ignoring index
        db_results = find_fragments_containing_text(
            table=search_in_db(args.db_path, args.table_name, "", mode="basic"),  # or open table directly
            search_text=args.query
        )
        print(db_results)
    else:
        # Use chosen search mode
        results = search_in_db(args.db_path, args.table_name, args.query, mode=args.mode)
        print(f"Search results using mode={args.mode}:")
        for r in results:
            print(f"Score: {r.get('_score', 'N/A')}, Text: {r['text']}, Section: {r['section']}")

if __name__ == "__main__":
    main()