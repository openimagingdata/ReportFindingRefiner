import os
import json
from typing import List, Dict, Any, Optional
import lancedb

from ..config import DEFAULT_DB_PATH
from ..models.finding_model import FindingModelBase
from ..data_models import FindingModelSchema
from .llm_service import LLMService
from .search_service import SearchService

class FindingModelService:
    """
    Service for creating and managing finding models.
    This class centralizes all finding model operations for both API and CLI.
    """
    
    def __init__(
        self, 
        db_path: str = DEFAULT_DB_PATH, 
        table_name: str = "findings",
        reports_table: str = "reports"
    ):
        """Initialize the finding model service"""
        self.db_path = os.path.join(db_path, "findings")
        self.table_name = table_name
        self.reports_table = reports_table
        self.db = None
        self.table = None
        self.llm_service = LLMService()
        self.search_service = SearchService(db_path=db_path, table_name=reports_table)
    
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
                    schema=FindingModelSchema,
                    mode="create"
                )
        
        return self.table
    
    def generate_description(self, finding_name: str) -> str:
        """
        Generate a description for a finding
        
        Args:
            finding_name: Name of the finding
            
        Returns:
            Generated description
        """
        return self.llm_service.generate_finding_description(finding_name)
    
    def generate_outline(self, finding_name: str, description: str, synonyms: List[str] = None) -> Dict[str, Any]:
        """
        Generate an outline for a finding
        
        Args:
            finding_name: Name of the finding
            description: Description of the finding
            synonyms: List of synonyms for the finding name
            
        Returns:
            Dictionary containing the generated outline
        """
        return self.llm_service.generate_finding_outline(
            finding_name=finding_name,
            description=description,
            synonyms=synonyms
        )
    
    def generate_outline_with_context(
        self, 
        finding_name: str, 
        description: str,
        search_mode: str = "basic",
        limit: int = 5,
        synonyms: List[str] = None
    ) -> Dict[str, Any]:
        """
        Generate an outline with context from searching reports
        
        Args:
            finding_name: Name of the finding
            description: Description of the finding
            search_mode: Search mode to use ("basic", "vector", "hybrid")
            limit: Maximum number of context documents to include
            synonyms: List of synonyms for the finding name
            
        Returns:
            Dictionary containing the generated outline
        """
        # Search for context
        search_query = finding_name
        if synonyms:
            search_query = f"{search_query} OR {' OR '.join(synonyms)}"
        
        context_docs = self.search_service.search(search_query, mode=search_mode, limit=limit)
        
        # Generate outline with context
        return self.llm_service.generate_finding_outline_with_context(
            finding_name=finding_name,
            description=description,
            context_docs=context_docs,
            synonyms=synonyms
        )
    
    def save_finding_model(self, finding_model: FindingModelBase) -> Dict[str, Any]:
        """
        Save a finding model to the database
        
        Args:
            finding_model: The finding model to save
            
        Returns:
            The saved model data
        """
        table = self._ensure_connection()
        
        # Convert to JSON for storage
        model_json = finding_model.json()
        
        # Get extended detail from LLM
        extended_detail = self.llm_service.query(
            f"Provide additional detailed information about {finding_model.name}: {finding_model.description}"
        )
        
        # Store in database
        table.add([{
            "model_name": finding_model.name,
            "model_data": model_json,
            "text": finding_model.as_markdown(),
            "extended_detail": extended_detail
        }])
        
        return {
            "finding_model": finding_model,
            "extended_detail": extended_detail
        }
    
    def get_all_finding_models(self) -> List[Dict[str, Any]]:
        """
        Get all finding models from the database
        
        Returns:
            List of finding models
        """
        table = self._ensure_connection()
        
        # Query all models
        df = table.to_pandas()
        
        models = []
        for _, row in df.iterrows():
            try:
                model_data = json.loads(row['model_data'])
                model = {
                    "name": row['model_name'],
                    "model_data": model_data,
                    "extended_detail": row['extended_detail']
                }
                models.append(model)
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Error parsing model {row['model_name']}: {str(e)}")
        
        return models
    
    def get_finding_model(self, model_name: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific finding model by name
        
        Args:
            model_name: Name of the finding model to retrieve
            
        Returns:
            The finding model or None if not found
        """
        table = self._ensure_connection()
        
        # Query for specific model
        results = table.to_pandas()
        
        # Filter by name
        model_rows = results[results['model_name'] == model_name]
        
        if len(model_rows) == 0:
            return None
        
        # Get the first matching model
        row = model_rows.iloc[0]
        
        try:
            model_data = json.loads(row['model_data'])
            return {
                "name": row['model_name'],
                "model_data": model_data,
                "extended_detail": row['extended_detail']
            }
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error parsing model {row['model_name']}: {str(e)}")
            return None 