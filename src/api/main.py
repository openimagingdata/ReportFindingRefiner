# FastAPI setup for interaction with Ollama
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
from typing import Optional, List
from jinja2 import Template
import os
import json
import lancedb

# Import reportfindingrefiner tools
from reportfindingrefiner.search import search_in_db
from reportfindingrefiner.config import (
    DEFAULT_MODEL,
    DEFAULT_DB_PATH,
    DEFAULT_TABLE_NAME,
    DEFAULT_SEARCH_MODE,
    DEFAULT_LIMIT
)
from reportfindingrefiner.models.finding_info import BaseFindingInfo
from reportfindingrefiner.models.finding_model import FindingModelBase
from reportfindingrefiner.ingestion import read_reports_from_folder, ingest_reports
from reportfindingrefiner.data_models import FragmentSchema, FindingModelSchema

# Initialize FastAPI app
app = FastAPI(title="Report Finding Refiner API")

# Global variables for DB connections
reports_db = None
findings_db = None
REPORTS_TABLE_NAME = "reports"
FINDINGS_TABLE_NAME = "findings"

@app.on_event("startup")
async def startup_event():
    """Initialize LanceDB connections and create tables on startup"""
    global reports_db, findings_db
    
    # Create DB directories if they don't exist
    os.makedirs(DEFAULT_DB_PATH, exist_ok=True)
    os.makedirs(os.path.join(DEFAULT_DB_PATH, "findings"), exist_ok=True)
    
    # Connect to DBs
    reports_db = lancedb.connect(DEFAULT_DB_PATH)
    findings_db = lancedb.connect(os.path.join(DEFAULT_DB_PATH, "findings"))
    
    # Initialize reports table if needed
    reports_folder = "./data/reports"
    if REPORTS_TABLE_NAME not in reports_db.table_names():
        if os.path.exists(reports_folder) and any(f.endswith('.txt') for f in os.listdir(reports_folder)):
            try:
                ingest_reports(
                    reports_folder=reports_folder,
                    db_path=DEFAULT_DB_PATH,
                    table_name=REPORTS_TABLE_NAME
                )
            except Exception as e:
                print(f"Error ingesting reports: {str(e)}")
    else:
        # Table exists, check for new reports
        existing_table = reports_db.open_table(REPORTS_TABLE_NAME)
        existing_reports = set(existing_table.to_pandas()['report_id'].unique())
        
        # Get list of reports in folder
        available_reports = {f for f in os.listdir(reports_folder) if f.endswith('.txt')}
        
        # Only ingest new reports if any exist
        new_reports = available_reports - existing_reports
        if new_reports:
            try:
                # Create a temporary table for new reports
                temp_table_name = f"{REPORTS_TABLE_NAME}_temp"
                ingest_reports(
                    reports_folder=reports_folder,
                    db_path=DEFAULT_DB_PATH,
                    table_name=temp_table_name
                )
                
                # Merge new reports into existing table
                temp_table = reports_db.open_table(temp_table_name)
                new_data = temp_table.to_pandas()
                new_data = new_data[new_data['report_id'].isin(new_reports)]
                existing_table.add(new_data.to_dict('records'))
                
                # Clean up temporary table
                reports_db.drop_table(temp_table_name)
                
                print(f"Ingested {len(new_reports)} new reports")
            except Exception as e:
                print(f"Error ingesting new reports: {str(e)}")
    
    # Initialize findings table if it doesn't exist
    if FINDINGS_TABLE_NAME not in findings_db.table_names():
        findings_db.create_table(
            FINDINGS_TABLE_NAME,
            schema=FindingModelSchema,
            mode="create"
        )

@app.get("/")
def read_root():
    return {
        "message": "Report Finding Refiner API",
        "reports_table": REPORTS_TABLE_NAME,
        "findings_table": FINDINGS_TABLE_NAME
    }

class Query(BaseModel):
    prompt: str
    model: str = DEFAULT_MODEL

@app.post("/chat")
async def chat(query: Query):
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": query.model, 
                "prompt": query.prompt,
                "stream": False
            }
        )
        response.raise_for_status()
        return {"generated_text": response.json()["response"]}
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error communicating with Ollama: {str(e)}")

class SearchQuery(BaseModel):
    query: str
    mode: str = DEFAULT_SEARCH_MODE
    limit: int = DEFAULT_LIMIT

@app.post("/search")
async def search_text(query: SearchQuery):
    try:
        results = search_in_db(
            db_path=DEFAULT_DB_PATH,
            table_name=REPORTS_TABLE_NAME,
            query_str=query.query,
            mode=query.mode
        )
        return {"results": results[:query.limit]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error performing search: {str(e)}")

class FindingModelQuery(BaseModel):
    finding_type: str
    context_docs: List[str]
    model: str = DEFAULT_MODEL

class FinalizeFindingModelRequest(BaseModel):
    """Request body for finalizing a FindingModel after generating an outline."""
    finding_model: FindingModelBase

@app.post("/findingmodel")
async def finalize_finding_model(request: FinalizeFindingModelRequest):
    """
    This endpoint takes the JSON returned by /findingmodel/outline
    (i.e. a fully-formed FindingModelBase), optionally calls a Jinja template
    to enrich or finalize the model, and then saves it to the LanceDB 'findings' table.
    """
    try:
        # Extract the posted FindingModelBase
        finding_model = request.finding_model

        with open("src/reportfindingrefiner/prompt_templates/get_finding_detail.md.jinja") as f:
            detail_template = Template(f.read())

        detail_prompt = detail_template.render(finding={
            "finding_name": finding_model.name,
            "description": finding_model.description,
            "synonyms": finding_model.synonyms,
        })

        # Query the LLM for more detail
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": DEFAULT_MODEL, "prompt": detail_prompt, "stream": False}
        )
        response.raise_for_status()

        # Unclear if this is needed, potentially refactor
        extended_detail = response.json()["response"].strip()

        model_json = finding_model.json()

        findings_table = findings_db.open_table(FINDINGS_TABLE_NAME)
        findings_table.add([{
            "model_name": finding_model.name,
            "model_data": model_json,
            "text": finding_model.as_markdown(),
            "extended_detail": extended_detail
        }])

        return {
            "finding_model": finding_model,
            "extended_detail": extended_detail
        }

    except requests.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error communicating with Ollama: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error finalizing finding model: {str(e)}"
        )
    

@app.get("/findingmodels")
async def get_finding_models():
    try:
        findings_table = findings_db.open_table(FINDINGS_TABLE_NAME)
        results = findings_table.to_pandas()
        return {"models": results.to_dict(orient="records")}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving finding models: {str(e)}"
        )

@app.get("/reports")
async def get_reports():
    """Return all processed reports in markdown format"""
    try:
        # Get reports table
        reports_table = reports_db.open_table(REPORTS_TABLE_NAME)
        df = reports_table.to_pandas()
        
        # Get unique report IDs
        unique_reports = df['report_id'].unique()
        
        markdown_reports = []
        for report_id in unique_reports:
            markdown_report = f"""
# Report: {report_id}

## Sections
"""
            # Get all fragments for this report, ordered by sequence number
            fragments = df[df['report_id'] == report_id].sort_values('sequence_number')
            
            current_section = None
            for _, fragment in fragments.iterrows():
                if fragment['section'] != current_section:
                    current_section = fragment['section']
                    markdown_report += f"\n### {current_section or 'Unknown Section'}\n\n"
                markdown_report += f"{fragment['text']}\n"
            
            markdown_reports.append(markdown_report)
        
        return {"reports": markdown_reports}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving reports: {str(e)}"
        )

@app.get("/fragments")
async def get_fragments():
    """Return all fragments in the database"""
    try:
        # Get reports table
        reports_table = reports_db.open_table(REPORTS_TABLE_NAME)
        df = reports_table.to_pandas()
        
        # Sort by report_id and sequence_number for consistent output
        df = df.sort_values(['report_id', 'sequence_number'])
        
        fragments_list = []
        for _, row in df.iterrows():
            fragment = {
                "report_id": row['report_id'],
                "section": row['section'],
                "sequence_number": row['sequence_number'],
                "text": row['text']
            }
            fragments_list.append(fragment)
            
        return {"fragments": fragments_list}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving fragments: {str(e)}"
        )

class FindingNameRequest(BaseModel):
    finding_name: str

@app.post("/findingmodel/description")
async def generate_finding_description(request: FindingNameRequest):
    """Generate a description for a finding using the LLM"""
    try:
        # Load the description template
        with open("src/reportfindingrefiner/prompt_templates/get_finding_description.md.jinja") as f:
            template = Template(f.read())
            
        # Create the prompt
        prompt = template.render(finding_name=request.finding_name)
        
        # Query LLM
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": DEFAULT_MODEL, "prompt": prompt, "stream": False}
        )
        response.raise_for_status()
        #JUST FOR DEBUGGING
        print("DEBUG -> response.text:", response.text)  
        raw_response = response.json()["response"].strip()
        
        # Get the response and clean it
        raw_response = response.json()["response"].strip()
        
        # Remove any markdown headers or formatting
        cleaned_response = "\n".join(
            line for line in raw_response.split('\n')
            if not line.startswith('#') and line.strip()
        ).strip()
        
        return {"description": cleaned_response}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating finding description: {str(e)}"
        )

@app.post("/findingmodel/outline")
async def generate_finding_outline(finding_info: BaseFindingInfo):
    """Generate a finding model outline using the LLM"""
    try:
        # Load the model template
        with open("src/reportfindingrefiner/prompt_templates/get_finding_model_from_outline.md.jinja") as f:
            template = Template(f.read())
            
        # Create the prompt
        prompt = template.render(finding_info=finding_info)
        
        # Query LLM
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": DEFAULT_MODEL, "prompt": prompt, "stream": False}
        )
        response.raise_for_status()
        
        model_json = response.json()["response"]
        finding_model = FindingModelBase.model_validate_json(model_json)
        
        # Save to findings database
        findings_table = findings_db.open_table(FINDINGS_TABLE_NAME)
        findings_table.add([{
            "model_name": finding_model.name,
            "model_data": model_json,
            "text": finding_model.as_markdown()
        }])
        
        return finding_model
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating finding outline: {str(e)}"
        )