from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from reportfindingrefiner.config import (
    DEFAULT_DB_PATH, 
    DEFAULT_MODEL,
    DEFAULT_SEARCH_MODE,
    DEFAULT_LIMIT
)
from reportfindingrefiner.services.finding_model_service import FindingModelService
from reportfindingrefiner.models.finding_model import FindingModelBase
from reportfindingrefiner.models.finding_info import BaseFindingInfo

# Initialize router
router = APIRouter(tags=["finding-models"])

# Initialize service
finding_model_service = FindingModelService(
    db_path=DEFAULT_DB_PATH, 
    table_name="findings",
    reports_table="reports"
)

class FindingNameRequest(BaseModel):
    finding_name: str
    model: str = DEFAULT_MODEL

class FindingOutlineRequest(BaseModel):
    finding_name: str
    description: str
    synonyms: Optional[List[str]] = None
    model: str = DEFAULT_MODEL

class FindingOutlineWithContextRequest(BaseModel):
    finding_name: str
    description: str
    synonyms: Optional[List[str]] = None
    search_mode: str = DEFAULT_SEARCH_MODE
    limit: int = 5
    model: str = DEFAULT_MODEL

class FinalizeFindingModelRequest(BaseModel):
    finding_model: FindingModelBase

@router.post("/description")
async def generate_finding_description(request: FindingNameRequest):
    """
    Generate a description for a finding.
    """
    try:
        description = finding_model_service.generate_description(request.finding_name)
        return {"finding_name": request.finding_name, "description": description}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating description: {str(e)}")

@router.post("/outline")
async def generate_finding_outline(request: FindingOutlineRequest):
    """
    Generate an outline for a finding.
    """
    try:
        outline = finding_model_service.generate_outline(
            finding_name=request.finding_name,
            description=request.description,
            synonyms=request.synonyms
        )
        return outline
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating outline: {str(e)}")

@router.post("/outline/with-context")
async def generate_finding_outline_with_context(request: FindingOutlineWithContextRequest):
    """
    Generate an outline for a finding with context from reports.
    """
    try:
        outline = finding_model_service.generate_outline_with_context(
            finding_name=request.finding_name,
            description=request.description,
            search_mode=request.search_mode,
            limit=request.limit,
            synonyms=request.synonyms
        )
        return outline
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating outline with context: {str(e)}")

@router.post("")
async def save_finding_model(request: FinalizeFindingModelRequest):
    """
    Save a finding model to the database.
    """
    try:
        result = finding_model_service.save_finding_model(request.finding_model)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving finding model: {str(e)}")

@router.get("")
async def get_all_finding_models():
    """
    Get all finding models.
    """
    try:
        models = finding_model_service.get_all_finding_models()
        return {"models": models}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving finding models: {str(e)}")

@router.get("/{model_name}")
async def get_finding_model(model_name: str):
    """
    Get a specific finding model by name.
    """
    try:
        model = finding_model_service.get_finding_model(model_name)
        if not model:
            raise HTTPException(status_code=404, detail=f"Finding model not found: {model_name}")
        return model
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving finding model: {str(e)}") 