#!/usr/bin/env python3
"""
Script for viewing reports in the database.
"""

import argparse
import sys
import json
from reportfindingrefiner.services.report_service import ReportService
from common import setup_common_args

def main():
    parser = argparse.ArgumentParser(description="View reports in the database")
    parser = setup_common_args(parser)
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List all reports")
    
    # View command
    view_parser = subparsers.add_parser("view", help="View a specific report")
    view_parser.add_argument("report_id", help="ID of the report to view")
    view_parser.add_argument(
        "--format", 
        choices=["markdown", "json"],
        default="markdown",
        help="Output format (default: markdown)"
    )
    
    args = parser.parse_args()
    
    # Initialize the report service
    report_service = ReportService(
        db_path=args.db_path,
        table_name=args.table_name
    )
    
    try:
        if args.command == "list":
            # List all reports
            reports = report_service.get_all_reports()
            
            print(f"Found {len(reports)} reports:")
            for i, report in enumerate(reports, 1):
                print(f"{i}. {report['report_id']} - {report['fragment_count']} fragments")
            
        elif args.command == "view":
            # Get the fragments for the specified report
            fragments = report_service.get_report_fragments(args.report_id)
            
            if fragments.empty:
                print(f"❌ Report '{args.report_id}' not found!")
                return 1
            
            if args.format == "json":
                # Convert to JSON
                fragments_list = fragments.to_dict('records')
                # Remove vector field
                for f in fragments_list:
                    if 'vector' in f:
                        del f['vector']
                print(json.dumps(fragments_list, indent=2))
            else:
                # Get markdown representation
                markdown = report_service.get_report_as_markdown(args.report_id)
                print(markdown)
            
        else:
            parser.print_help()
            return 1
        
        return 0
        
    except Exception as e:
        print(f"❌ Error viewing reports: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main()) 