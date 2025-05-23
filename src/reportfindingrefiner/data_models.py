from typing import Optional, List
from pydantic import BaseModel

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


def get_embedding_function():
    """Get the configured embedding function"""
    # This can be made configurable via environment variables
    return get_registry().get("huggingface").create(name="BAAI/bge-en-icl")


class FragmentSchema(LanceModel):
    """
    Schema for storing Fragment information in LanceDB.
    Uses LanceModel for auto-embedding fields and vector creation.
    """
    report_id: str
    section: Optional[str]
    sequence_number: int

    # This field is the source text that will be embedded
    text: str

    # The resulting embedding vector - will be set dynamically
    vector: Optional[Vector] = None

    @classmethod
    def with_embedding(cls):
        """Create schema with embedding configuration"""
        embed_fcn = get_embedding_function()
        
        # Create a new class with the embedding fields properly configured
        class ConfiguredFragmentSchema(LanceModel):
            report_id: str
            section: Optional[str]
            sequence_number: int
            text: str = embed_fcn.SourceField()
            vector: Vector(embed_fcn.ndims()) = embed_fcn.VectorField()  # type: ignore
            
        return ConfiguredFragmentSchema


class FindingModelSchema(LanceModel):
    """
    Schema for storing FindingModel information in LanceDB.
    Uses LanceModel for auto-embedding fields and vector creation.
    """
    model_name: str
    model_data: str  # JSON string of the full model
    text: str  # String representation for embedding
    vector: Optional[Vector] = None  # Will be set dynamically

    @classmethod
    def with_embedding(cls):
        """Create schema with embedding configuration"""
        embed_fcn = get_embedding_function()
        
        class ConfiguredFindingModelSchema(LanceModel):
            model_name: str
            model_data: str
            text: str = embed_fcn.SourceField()
            vector: Vector(embed_fcn.ndims()) = embed_fcn.VectorField()  # type: ignore
            
        return ConfiguredFindingModelSchema