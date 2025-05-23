#!/usr/bin/env python

"""
Command-line script to ingest reports into LanceDB.
Usage:
    python scripts/ingest_reports.py
"""

from reportfindingrefiner.ingestion import ingest_reports

if __name__ == "__main__":
    # You might parse command-line args here (e.g., using argparse).
    # For now, just call with defaults:
    ingest_reports(
        reports_folder="./data/reports_10",
        db_path="./data/lancedb",
        table_name="table",
    )