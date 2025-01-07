import os
import pymongo
from pymongo import MongoClient
from typing import List
from reportfindingrefiner.data_models import FindingModel

def get_mongo_client(uri: str = "mongodb://localhost:27017"):
    return MongoClient(uri)

def get_findings_collection(client: MongoClient, db_name: str = "radiology_db"):
    db = client[db_name]
    return db["findings"]

def save_finding(finding: FindingModel, collection):
    # Convert the Pydantic model to a dictionary for insertion
    doc = finding.dict()
    result = collection.insert_one(doc)
    return str(result.inserted_id)

def load_findings(collection) -> List[dict]:
    """Return all findings as dictionaries. Could also parse them back into Pydantic models."""
    return list(collection.find({}))