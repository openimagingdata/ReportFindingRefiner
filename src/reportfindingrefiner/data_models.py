from typing import Optional, List
from pydantic import BaseModel

# For LanceDB schema
from lancedb.pydantic import LanceModel, Vector
from lancedb.embeddings import get_registry


class Report(BaseModel):
    """
    Represents the entire text of a radiology report.
    """
    id: str
    text: str


class Fragment(BaseModel):
    """
    Represents a chunk of text (one section or smaller) from a report.
    """
    report_id: str
    section: Optional[str]
    sequence_number: int
    text: str
    vector: Optional[List[float]] = None


# Create the embedding function (HuggingFace example).
# For a real open-source project, you might want to make this
# user-configurable or load from a config file.
embed_fcn = get_registry().get("huggingface").create(name="BAAI/bge-en-icl")


class FragmentSchema(LanceModel):
    """
    Schema for storing Fragment information in LanceDB.
    Uses LanceModel for auto-embedding fields and vector creation.
    """
    report_id: str
    section: Optional[str]
    sequence_number: int

    # This field is the source text that will be embedded
    text: str = embed_fcn.SourceField()

    # The resulting embedding vector
    vector: Vector(embed_fcn.ndims()) = embed_fcn.VectorField()  # type: ignore