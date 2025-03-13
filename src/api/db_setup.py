import os
import lancedb
from typing import Tuple

from reportfindingrefiner.config import (
    DEFAULT_DB_PATH,
    DEFAULT_TABLE_NAME,
    DEFAULT_REPORTS_FOLDER
)
from reportfindingrefiner.data_models import FragmentSchema, FindingModelSchema
from reportfindingrefiner.services.report_service import ReportService

def initialize_databases() -> Tuple[lancedb.db.LanceDBConnection, lancedb.db.LanceDBConnection]:
    """
    Initialize all required databases and tables. Returns tuple of (reports_db, findings_db).
    """
    print("\n🚀 Initializing databases...")
    
    # Create required directories
    os.makedirs(DEFAULT_DB_PATH, exist_ok=True)
    findings_db_path = os.path.join(DEFAULT_DB_PATH, "findings")
    os.makedirs(findings_db_path, exist_ok=True)
    os.makedirs("./data/reports", exist_ok=True)
    print("📁 Created required directories")
    
    # Connect to DBs
    reports_db = lancedb.connect(DEFAULT_DB_PATH)
    findings_db = lancedb.connect(findings_db_path)
    print("🔌 Connected to databases")
    
    # Initialize reports table if it doesn't exist
    if DEFAULT_TABLE_NAME not in reports_db.table_names():
        reports_db.create_table(
            DEFAULT_TABLE_NAME,
            schema=FragmentSchema,
            mode="create"
        )
        print(f"📊 Created new reports table: {DEFAULT_TABLE_NAME}")
        
    # Initialize findings table if it doesn't exist
    findings_table_name = "findings"
    if findings_table_name not in findings_db.table_names():
        findings_db.create_table(
            findings_table_name,
            schema=FindingModelSchema,
            mode="create"
        )
        print(f"📊 Created new findings table: {findings_table_name}")
    
    return reports_db, findings_db

def process_initial_reports() -> int:
    """
    Check for and process any reports in the reports folder.
    Returns the number of fragments ingested or 0 if none.
    """
    reports_folder = DEFAULT_REPORTS_FOLDER
    if os.path.exists(reports_folder) and any(f.endswith('.txt') for f in os.listdir(reports_folder)):
        print("\n📝 Found reports to process...")
        try:
            # Use the report service to ingest the reports
            report_service = ReportService(
                db_path=DEFAULT_DB_PATH,
                table_name=DEFAULT_TABLE_NAME
            )
            
            fragment_count = report_service.ingest_reports(reports_folder)
            print(f"✅ Ingested {fragment_count} fragments from {reports_folder}")
            return fragment_count
            
        except Exception as e:
            print(f"\n❌ Error during report ingestion: {str(e)}")
            return 0
    else:
        print("\n📝 No reports found in " + DEFAULT_REPORTS_FOLDER)