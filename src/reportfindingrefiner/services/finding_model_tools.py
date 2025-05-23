from typing import List, Optional
import requests
from jinja2 import Template
import lancedb
import os

from .config import (
    DEFAULT_MODEL,
    DEFAULT_DB_PATH,
    DEFAULT_LIMIT,
    DEFAULT_SEARCH_MODE
)
from .models.finding_model import FindingModelBase
from .data_models import FindingModelSchema

def generate_finding_description(finding_name: str, model: str = DEFAULT_MODEL) -> str:
    """Generate a description for a finding using the LLM"""
    try:
        # Load the description template
        with open("src/reportfindingrefiner/prompt_templates/get_finding_description.md.jinja") as f:
            template = Template(f.read())
            
        # Create the prompt
        prompt = template.render(finding_name=finding_name)
        
        # Query LLM
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": model, "prompt": prompt, "stream": False}
        )
        response.raise_for_status()
        
        # Clean and return the response
        raw_response = response.json()["response"].strip()
        cleaned_response = "\n".join(
            line for line in raw_response.split('\n')
            if not line.startswith('#') and line.strip()
        ).strip()
        
        return cleaned_response
        
    except Exception as e:
        raise Exception(f"Error generating finding description: {str(e)}")

def generate_finding_outline(
    name: str,
    description: str,
    synonyms: Optional[List[str]] = None,
    model: str = DEFAULT_MODEL,
    db_path: str = DEFAULT_DB_PATH
) -> FindingModelBase:
    """Generate a finding model outline using the LLM"""
    try:
        finding_info = {
            "name": name,
            "description": description,
            "synonyms": synonyms or []
        }
        
        # Load the model template
        with open("src/reportfindingrefiner/prompt_templates/get_finding_model_from_outline.md.jinja") as f:
            template = Template(f.read())
            
        # Create the prompt
        prompt = template.render(finding_info=finding_info)
        
        # Query LLM
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": model, "prompt": prompt, "stream": False}
        )
        response.raise_for_status()
        
        model_json = response.json()["response"]
        finding_model = FindingModelBase.model_validate_json(model_json)
        
        # Save to findings database
        findings_db = lancedb.connect(os.path.join(db_path, "findings"))
        findings_table = findings_db.open_table("findings")
        findings_table.add([{
            "model_name": finding_model.name,
            "model_data": model_json,
            "text": finding_model.as_markdown()
        }])
        
        return finding_model
        
    except Exception as e:
        raise Exception(f"Error generating finding outline: {str(e)}")

#TODO: Add a function to generate a finding model outline with context from similar reports
#TODO: consider saving the context to the finding model for QA purposes

def generate_finding_outline_with_context(
    name: str   ,
    description: str,
    synonyms: Optional[List[str]] = None,
    search_mode: str = DEFAULT_SEARCH_MODE,
    limit: int = DEFAULT_LIMIT,
    model: str = DEFAULT_MODEL,
    db_path: str = DEFAULT_DB_PATH
) -> FindingModelBase:
    """Generate a finding model outline using the LLM with context from similar reports"""
    try:
        finding_info = {
            "name": name,
            "description": description,
            "synonyms": synonyms or []
        }
        
        # Search for relevant context
        search_query = f"{name} {description}"
        reports_db = lancedb.connect(db_path)
        reports_table = reports_db.open_table("reports")
        
        # Perform search based on specified mode
        if search_mode == "basic":
            results = reports_table.search(search_query).limit(limit).to_list()
        elif search_mode == "hybrid":
            results = reports_table.search(search_query, query_type="hybrid").limit(limit).to_list()
        elif search_mode == "vector":
            results = reports_table.search(search_query, query_type="vector").limit(limit).to_list()
        else:
            raise ValueError(f"Unknown search mode: {search_mode}")

        context_docs = [r['text'] for r in results]
        
        # Generate model with context
        with open("src/reportfindingrefiner/prompt_templates/get_finding_model_with_context.md.jinja") as f:
            template = Template(f.read())
            
        prompt = template.render(
            finding_info=finding_info,
            context_documents=context_docs
        )
        
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": model, "prompt": prompt, "stream": False}
        )
        response.raise_for_status()
        
        model_json = response.json()["response"]
        finding_model = FindingModelBase.model_validate_json(model_json)
        
        # Save to findings database
        findings_db = lancedb.connect(os.path.join(db_path, "findings"))
        findings_table = findings_db.open_table("findings")
        findings_table.add([{
            "model_name": finding_model.name,
            "model_data": model_json,
            "text": finding_model.as_markdown()
        }])
        
        return finding_model
        
    except Exception as e:
        raise Exception(f"Error generating finding outline with context: {str(e)}")

def list_finding_models(db_path: str = DEFAULT_DB_PATH) -> List[dict]:
    """Retrieve all finding models from the database"""
    try:
        findings_db = lancedb.connect(os.path.join(db_path, "findings"))
        findings_table = findings_db.open_table("findings")
        df = findings_table.to_pandas()
        
        return [{
            "name": row["model_name"],
            "model": row["model_data"],
            "markdown_text": row["text"]
        } for _, row in df.iterrows()]
    except Exception as e:
        raise Exception(f"Error retrieving finding models: {str(e)}")