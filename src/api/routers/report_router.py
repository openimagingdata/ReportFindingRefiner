from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os

from reportfindingrefiner.config import (
    DEFAULT_DB_PATH,
    DEFAULT_TABLE_NAME
)
from reportfindingrefiner.services.report_service import ReportService

# Initialize router
router = APIRouter(tags=["reports"])

# Initialize service
report_service = ReportService(db_path=DEFAULT_DB_PATH, table_name=DEFAULT_TABLE_NAME)

class IngestRequest(BaseModel):
    reports_folder: str = "./data/reports"

@router.post("/ingest")
async def ingest_reports(request: IngestRequest):
    """
    Ingest reports from the specified folder.
    """
    try:
        if not os.path.exists(request.reports_folder):
            raise HTTPException(status_code=400, detail=f"Reports folder not found: {request.reports_folder}")
            
        fragment_count = report_service.ingest_reports(request.reports_folder)
        return {
            "message": f"Successfully ingested {fragment_count} fragments from {request.reports_folder}",
            "fragment_count": fragment_count,
            "reports_folder": request.reports_folder
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ingesting reports: {str(e)}")

@router.get("")
async def get_reports():
    """
    Get all reports with their fragment counts.
    """
    try:
        reports = report_service.get_all_reports()
        return {"reports": reports}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving reports: {str(e)}")

@router.get("/markdown")
async def get_reports_markdown():
    """
    Get all reports formatted as markdown.
    """
    try:
        markdown_reports = report_service.get_all_reports_as_markdown()
        return markdown_reports
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving markdown reports: {str(e)}")

@router.get("/markdown/{report_id}")
async def get_report_markdown(report_id: str):
    """
    Get a specific report formatted as markdown.
    """
    try:
        markdown_report = report_service.get_report_as_markdown(report_id)
        if not markdown_report:
            raise HTTPException(status_code=404, detail=f"Report not found: {report_id}")
        return {"report_id": report_id, "markdown": markdown_report}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving report: {str(e)}")

@router.get("/view/{report_id}")
async def view_report(report_id: str):
    """
    Get a specific report formatted as HTML for viewing.
    """
    try:
        markdown_report = report_service.get_report_as_markdown(report_id)
        if not markdown_report:
            raise HTTPException(status_code=404, detail=f"Report not found: {report_id}")
            
        # Simple conversion from markdown to HTML (for a real implementation, use a markdown library)
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Report: {report_id}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }}
                h1, h2, h3 {{ color: #333; }}
                pre {{ background-color: #f5f5f5; padding: 10px; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <pre>{markdown_report}</pre>
        </body>
        </html>
        """
        
        return HTMLResponse(content=html_content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error viewing report: {str(e)}") 