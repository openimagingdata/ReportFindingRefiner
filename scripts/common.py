"""Common functionality for CLI scripts"""
import os
import argparse
from reportfindingrefiner.config import (
    DEFAULT_DB_PATH,
    DEFAULT_TABLE_NAME,
    DEFAULT_MODEL,
    DEFAULT_SEARCH_MODE,
    DEFAULT_LIMIT,
    DEFAULT_REPORTS_FOLDER
)

def setup_common_args(parser):
    """Add common arguments to a parser"""
    parser.add_argument(
        "--db-path", 
        default=DEFAULT_DB_PATH,
        help=f"Path to the LanceDB database (default: {DEFAULT_DB_PATH})"
    )
    parser.add_argument(
        "--table-name", 
        default=DEFAULT_TABLE_NAME,
        help=f"Name of the table in the database (default: {DEFAULT_TABLE_NAME})"
    )
    parser.add_argument(
        "--verbose", "-v", 
        action="store_true",
        help="Enable verbose output"
    )
    return parser

def setup_search_args(parser):
    """Add search-related arguments to a parser"""
    parser.add_argument(
        "--mode", 
        choices=["basic", "vector", "hybrid"],
        default=DEFAULT_SEARCH_MODE,
        help=f"Search mode to use (default: {DEFAULT_SEARCH_MODE})"
    )
    parser.add_argument(
        "--limit", 
        type=int,
        default=DEFAULT_LIMIT,
        help=f"Maximum number of results to return (default: {DEFAULT_LIMIT})"
    )
    return parser 