import os
from typing import List
from .data_models import Report
from .section_splitter import SectionSplitter, create_fragments_from_reports
from .lance_db import connect_db, create_fragment_table, insert_fragments

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
    # 1. Connect to DB
    db = connect_db(db_path)

    # 2. Create or overwrite the table schema
    table = create_fragment_table(db, table_name=table_name)

    # 3. Read local .txt files
    reports_list = read_reports_from_folder(reports_folder)

    # 4. Create all fragments
    splitter = SectionSplitter()
    all_fragments = create_fragments_from_reports(reports_list, splitter)

    # 5. Prepare docs for insertion
    auto_inserts = []
    for frag in all_fragments:
        doc = {
            "report_id": frag.report_id,
            "section": frag.section,
            "sequence_number": frag.sequence_number,
            "text": frag.text
        }
        auto_inserts.append(doc)

    # 6. Insert into table (auto-embedding)
    insert_fragments(table, auto_inserts)

    # 7. Print an example
    print(table.head(5))