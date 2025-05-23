import os
import lancedb
from typing import List
from .data_models import FragmentSchema
from tqdm import tqdm

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
    Shows progress during embedding and insertion.
    """
    total_docs = len(docs)
    batch_size = 32  # Optimal batch size for embedding
    
    print(f"\n💾 Starting embedding and insertion of {total_docs} fragments...")
    
    # Process in batches with progress bar
    with tqdm(total=total_docs, desc="Embedding fragments") as pbar:
        for i in range(0, total_docs, batch_size):
            batch = docs[i:min(i + batch_size, total_docs)]
            table.add(batch)
            pbar.update(len(batch))
    
    print("\n✅ Embedding and insertion complete!")