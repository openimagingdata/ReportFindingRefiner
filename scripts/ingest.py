#!/usr/bin/env python3
"""
Script for ingesting reports into the database.
"""

import argparse
import sys
import os
from reportfindingrefiner.services.report_service import ReportService
from reportfindingrefiner.config import DEFAULT_REPORTS_FOLDER, DEFAULT_DB_PATH, DEFAULT_TABLE_NAME
from common import setup_common_args

def main():
    parser = argparse.ArgumentParser(description="Ingest reports into the database")
    parser = setup_common_args(parser)
    parser.add_argument(
        "--reports-folder", 
        default=DEFAULT_REPORTS_FOLDER,
        help=f"Path to the folder containing report files (default: {DEFAULT_REPORTS_FOLDER})"
    )
    parser.add_argument(
        "--force", "-f", 
        action="store_true",
        help="Force re-creation of the database table"
    )
    
    args = parser.parse_args()
    
    # Initialize the report service
    report_service = ReportService(
        db_path=args.db_path,
        table_name=args.table_name
    )
    
    try:
        print(f"Ingesting reports from {args.reports_folder}...")
        
        # Check if reports folder exists
        if not os.path.exists(args.reports_folder):
            print(f"Error: Reports folder '{args.reports_folder}' does not exist!")
            return 1
            
        # Ingest the reports
        num_fragments = report_service.ingest_reports(args.reports_folder)
        
        print(f"✅ Successfully ingested reports! Created {num_fragments} fragments.")
        return 0
        
    except Exception as e:
        print(f"❌ Error ingesting reports: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main()) 