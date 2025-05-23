import os
from typing import List
from .data_models import Report
from .section_splitter import SectionSplitter, create_fragments_from_report
from .lance_db import connect_db, create_fragment_table, insert_fragments
from tqdm import tqdm

def read_reports_from_folder(folder_path: str) -> List[Report]:
    """
    Read .txt files from a folder, return a list of `Report` objects.
    """
    reports = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            with open(os.path.join(folder_path, filename), "r", encoding="utf-8") as f:
                text = f.read()
                reports.append(Report(id=filename, text=text))
    return reports

def ingest_reports(
    reports_folder: str = "./reports",
    db_path: str = "./data/lancedb",
    table_name: str = "table",
) -> None:
    """
    Orchestrates reading from folder, creating fragments, and storing in LanceDB.
    """
    try:
        print(f"\n🔍 Scanning reports folder: {reports_folder}")
        
        # 1. Connect to DB
        db = connect_db(db_path)
        print(f"📦 Connected to database: {db_path}")

        # 2. Create or overwrite the table schema
        table = create_fragment_table(db, table_name=table_name)
        print(f"📋 Created/opened table: {table_name}")

        # 3. Read local .txt files
        reports_list = read_reports_from_folder(reports_folder)
        print(f"\n📄 Found {len(reports_list)} reports to process")

        # 4. Create all fragments
        splitter = SectionSplitter()
        print("\n🔄 Processing reports:")
        all_fragments = []
        
        for i, report in enumerate(reports_list, 1):
            print(f"\n⮡ Starting report {i}/{len(reports_list)}: {report.id}")
            
            # Process the report and show section splitting progress
            fragments = create_fragments_from_report(report, splitter)
            all_fragments.extend(fragments)
            
            # Show completion for this report
            print(f"✓ Completed report: {report.id} (created {len(fragments)} fragments)")

        # 5. Prepare docs for insertion
        print(f"\n📝 Preparing {len(all_fragments)} total fragments for insertion...")
        auto_inserts = []
        with tqdm(total=len(all_fragments), desc="Preparing fragments") as pbar:
            for frag in all_fragments:
                doc = {
                    "report_id": frag.report_id,
                    "section": frag.section,
                    "sequence_number": frag.sequence_number,
                    "text": frag.text
                }
                auto_inserts.append(doc)
                pbar.update(1)

        # 6. Insert into table (auto-embedding)
        print(f"\n💾 Starting database insertion...")
        insert_fragments(table, auto_inserts)

        print("\n✅ Report ingestion complete!")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user")
        raise

def insert_fragments(table, docs: List[dict]) -> None:
    """
    Insert fragment documents into the specified LanceDB table.
    """
    print(f"\n💾 Starting embedding and insertion of {len(docs)} fragments...")
    for i in tqdm(range(0, len(docs), 32), desc="Embedding fragments"):
        batch = docs[i:i+32]
        table.add(batch)
    print("✅ Embedding and insertion complete!")