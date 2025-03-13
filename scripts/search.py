#!/usr/bin/env python3
"""
Script for searching reports in the database.
"""

import argparse
import sys
import json
from reportfindingrefiner.services.search_service import SearchService
from common import setup_common_args, setup_search_args

def format_result(result, show_full=False):
    """Format a search result for display"""
    # Create a copy without the vector field
    display_result = {k: v for k, v in result.items() if k != 'vector'}
    
    # Truncate text if not showing full results
    if not show_full and 'text' in display_result:
        text = display_result['text']
        if len(text) > 100:
            display_result['text'] = text[:100] + "..."
    
    return display_result

def main():
    parser = argparse.ArgumentParser(description="Search reports in the database")
    parser = setup_common_args(parser)
    parser = setup_search_args(parser)
    
    parser.add_argument(
        "query",
        help="The search query"
    )
    parser.add_argument(
        "--output", "-o",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)"
    )
    parser.add_argument(
        "--full", "-f",
        action="store_true",
        help="Show full text in results (default: truncated)"
    )
    parser.add_argument(
        "--compare",
        action="store_true",
        help="Compare search methods (basic, vector, hybrid)"
    )
    
    args = parser.parse_args()
    
    # Initialize the search service
    search_service = SearchService(
        db_path=args.db_path,
        table_name=args.table_name
    )
    
    try:
        if args.compare:
            # Compare search methods
            comparison = search_service.compare_search_methods(args.query, args.limit)
            
            if args.output == "json":
                # Format comparison for JSON output
                formatted_comparison = {
                    "query": comparison["query"],
                    "basic_results": [format_result(r, args.full) for r in comparison["basic_results"]],
                    "vector_results": [format_result(r, args.full) for r in comparison["vector_results"]],
                    "semantic_query": comparison["semantic_query"],
                    "semantic_results": [format_result(r, args.full) for r in comparison["semantic_results"]],
                    "overlap_count": comparison["overlap_count"],
                    "basic_total": comparison["basic_total"],
                    "vector_total": comparison["vector_total"]
                }
                print(json.dumps(formatted_comparison, indent=2))
            else:
                # Text output
                print(f"Search query: '{args.query}'")
                print("\nBasic search results:")
                for i, r in enumerate(comparison["basic_results"], 1):
                    print(f"{i}. {format_result(r, args.full)}")
                
                print("\nVector search results:")
                for i, r in enumerate(comparison["vector_results"], 1):
                    print(f"{i}. {format_result(r, args.full)}")
                
                print(f"\nSemantic query: '{comparison['semantic_query']}'")
                print("Results:")
                for i, r in enumerate(comparison["semantic_results"], 1):
                    print(f"{i}. {format_result(r, args.full)}")
                
                print(f"\nOverlap: {comparison['overlap_count']} results")
                print(f"Basic total: {comparison['basic_total']} results")
                print(f"Vector total: {comparison['vector_total']} results")
        else:
            # Regular search
            results = search_service.search(args.query, args.mode, args.limit)
            
            if args.output == "json":
                formatted_results = [format_result(r, args.full) for r in results]
                print(json.dumps(formatted_results, indent=2))
            else:
                print(f"Search query: '{args.query}' (mode: {args.mode})")
                print(f"Found {len(results)} results:")
                for i, result in enumerate(results, 1):
                    print(f"\n{i}. Report: {result.get('report_id', 'Unknown')}")
                    print(f"   Section: {result.get('section', 'Unknown')}")
                    
                    text = result.get('text', '')
                    if not args.full and len(text) > 100:
                        text = text[:100] + "..."
                    print(f"   Text: {text}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error searching reports: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main()) 