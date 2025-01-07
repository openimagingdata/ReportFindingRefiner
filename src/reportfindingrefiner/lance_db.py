import os
import lancedb
from typing import List
from .data_models import FragmentSchema

def connect_db(db_path: str = "./data/lancedb"):
    """
    Connect to LanceDB and return the database object.
    """
    return lancedb.connect(db_path)

def create_fragment_table(db, table_name: str = "table") -> lancedb.table:
    """
    Create or overwrite a LanceDB table with the FragmentSchema.
    """
    return db.create_table(table_name, schema=FragmentSchema, mode="overwrite")

def insert_fragments(table, docs: List[dict]) -> None:
    """
    Insert fragment documents into the specified LanceDB table.
    """
    table.add(docs)
    print(f"Inserted {len(docs)} fragments into {table}.")