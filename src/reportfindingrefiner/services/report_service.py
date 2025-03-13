import os
from typing import List, Dict, Any, Optional
import pandas as pd
import lancedb

from ..config import (
    DEFAULT_DB_PATH,
    DEFAULT_TABLE_NAME,
    DEFAULT_REPORTS_FOLDER
)
from ..section_splitter import SectionSplitter
from ..data_models import FragmentSchema
from ..section_splitter import create_fragments_from_reports
from ..services.ingestion import read_reports_from_folder

class ReportService:
    """
    Service for ingesting, managing, and retrieving reports and their fragments.
    This class centralizes all report-related functionality for both API and CLI.
    """
    
    def __init__(self, db_path: str = DEFAULT_DB_PATH, table_name: str = DEFAULT_TABLE_NAME):
        """Initialize the report service with database connection details"""
        self.db_path = db_path
        self.table_name = table_name
        self.db = None
        self.table = None
        self.splitter = SectionSplitter()
    
    def _ensure_connection(self):
        """Ensure connection to the database and table"""
        if self.db is None:
            # Make sure the directory exists
            os.makedirs(self.db_path, exist_ok=True)
            self.db = lancedb.connect(self.db_path)
        
        # Check if table exists and create it if needed
        if self.table is None:
            if self.table_name in self.db.table_names():
                self.table = self.db.open_table(self.table_name)
            else:
                self.table = self.db.create_table(
                    self.table_name,
                    schema=FragmentSchema,
                    mode="create"
                )
        
        return self.table
    
    def ingest_reports(self, reports_folder: str = DEFAULT_REPORTS_FOLDER) -> int:
        """
        Ingest reports from a folder into the database.
        
        Args:
            reports_folder: Path to folder containing report text files
            
        Returns:
            Number of fragments ingested
        """
        # Make sure the connection is established
        table = self._ensure_connection()
        
        # Read and process reports
        reports_list = read_reports_from_folder(reports_folder)
        all_fragments = create_fragments_from_reports(reports_list, self.splitter)
        
        # Prepare and insert documents
        docs = [{
            "report_id": frag.report_id,
            "section": frag.section,
            "sequence_number": frag.sequence_number,
            "text": frag.text
        } for frag in all_fragments]
        
        table.add(docs)
        return len(docs)
    
    def get_all_reports(self) -> List[Dict[str, Any]]:
        """
        Get all report IDs with their fragment counts
        
        Returns:
            List of dictionaries with report information
        """
        table = self._ensure_connection()
        df = table.to_pandas()
        
        # Get unique report IDs and count fragments
        report_stats = df.groupby('report_id').agg({
            'text': 'count'
        }).reset_index()
        
        return report_stats.rename(columns={'text': 'fragment_count'}).to_dict('records')
    
    def get_report_fragments(self, report_id: str) -> pd.DataFrame:
        """
        Get all fragments for a specific report
        
        Args:
            report_id: ID of the report to retrieve
            
        Returns:
            DataFrame containing the report fragments
        """
        table = self._ensure_connection()
        df = table.to_pandas()
        
        # Filter by report ID and sort by sequence number
        fragments = df[df['report_id'] == report_id].sort_values('sequence_number')
        return fragments
    
    def get_report_as_markdown(self, report_id: str) -> str:
        """
        Get a report formatted as markdown
        
        Args:
            report_id: ID of the report to retrieve
            
        Returns:
            Markdown-formatted report
        """
        fragments = self.get_report_fragments(report_id)
        
        markdown_report = f"# Report: {report_id}\n\n## Sections\n"
        
        current_section = None
        for _, fragment in fragments.iterrows():
            if fragment['section'] != current_section:
                current_section = fragment['section']
                markdown_report += f"\n### {current_section or 'Unknown Section'}\n\n"
            markdown_report += f"{fragment['text']}\n"
        
        return markdown_report
    
    def get_all_reports_as_markdown(self) -> Dict[str, str]:
        """
        Get all reports formatted as markdown
        
        Returns:
            Dictionary mapping report_id to markdown-formatted report
        """
        table = self._ensure_connection()
        df = table.to_pandas()
        
        # Get unique report IDs
        unique_reports = df['report_id'].unique()
        
        markdown_reports = {}
        for report_id in unique_reports:
            markdown_reports[report_id] = self.get_report_as_markdown(report_id)
        
        return markdown_reports 