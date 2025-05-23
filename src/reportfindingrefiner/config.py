import os
from pathlib import Path

DEFAULT_MODEL = "llama3.2"
DEFAULT_DB_PATH = os.getenv("REPORT_REFINER_DB_PATH", "./data/lancedb/")
DEFAULT_TABLE_NAME = "table"
DEFAULT_SEARCH_MODE = "basic"
DEFAULT_LIMIT = 10
DEFAULT_API_BASE = os.getenv("OLLAMA_API_BASE", "http://localhost:11434/api")

# Ensure paths are properly resolved
if not os.path.isabs(DEFAULT_DB_PATH):
    DEFAULT_DB_PATH = str(Path(__file__).parent.parent.parent / DEFAULT_DB_PATH)
