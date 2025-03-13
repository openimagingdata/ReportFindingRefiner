"""
ReportFindingRefiner - A tool for processing and analyzing reports.

This package provides functionality for ingesting, processing, and searching reports.
"""

from .data_models import Report
from .services.ingestion import read_reports_from_folder, ingest_reports
from .section_splitter import SectionSplitter, create_fragments_from_reports

__version__ = "0.1.0"

__all__ = [
    "Report",
    "ingest_reports",
    "read_reports_from_folder",
    "SectionSplitter",
    "create_fragments_from_reports",
] 