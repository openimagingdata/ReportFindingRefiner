import os
import requests
from typing import Dict, Any, Optional, List
from jinja2 import Template, Environment, FileSystemLoader
from pathlib import Path

from ..config import DEFAULT_MODEL, DEFAULT_API_BASE

class LLMService:
    """
    Service for interacting with language models.
    This class centralizes all LLM operations for both API and CLI.
    """
    
    def __init__(self, model: str = DEFAULT_MODEL, api_base: str = DEFAULT_API_BASE):
        """Initialize the LLM service"""
        self.model = model
        self.api_base = api_base
        
        # Set up Jinja environment for templates
        template_dir = Path(__file__).parent.parent / "prompt_templates"
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))
    
    def _load_template(self, template_name: str) -> Template:
        """Load a template by name"""
        return self.jinja_env.get_template(template_name)
    
    def query(self, prompt: str, model: Optional[str] = None) -> str:
        """
        Send a query to the LLM and return the response
        
        Args:
            prompt: The prompt to send to the LLM
            model: Optional model override
            
        Returns:
            The LLM's response text
        """
        model_to_use = model or self.model
        
        try:
            response = requests.post(
                f"{self.api_base}/generate",
                json={
                    "model": model_to_use, 
                    "prompt": prompt,
                    "stream": False
                }
            )
            response.raise_for_status()
            return response.json()["response"]
        except requests.RequestException as e:
            raise RuntimeError(f"Error communicating with LLM API: {str(e)}")
    
    def generate_finding_description(self, finding_name: str) -> str:
        """
        Generate a description for a finding
        
        Args:
            finding_name: Name of the finding
            
        Returns:
            Generated description
        """
        template = self._load_template("get_finding_description.md.jinja")
        prompt = template.render(finding_name=finding_name)
        return self.query(prompt)
    
    def generate_finding_outline(self, finding_name: str, description: str, synonyms: List[str] = None) -> Dict[str, Any]:
        """
        Generate an outline for a finding
        
        Args:
            finding_name: Name of the finding
            description: Description of the finding
            synonyms: List of synonyms for the finding name
            
        Returns:
            Dictionary containing the generated outline
        """
        template = self._load_template("get_finding_outline.md.jinja")
        prompt = template.render(
            finding_name=finding_name,
            description=description,
            synonyms=synonyms or []
        )
        response = self.query(prompt)
        
        try:
            # Attempt to parse the JSON response
            import json
            # Find the JSON part of the response (between ```json and ```)
            json_part = response.split("```json")[1].split("```")[0].strip()
            return json.loads(json_part)
        except (IndexError, json.JSONDecodeError) as e:
            raise ValueError(f"Failed to parse LLM response as JSON: {str(e)}")
    
    def generate_finding_outline_with_context(
        self, 
        finding_name: str, 
        description: str, 
        context_docs: List[Dict[str, Any]],
        synonyms: List[str] = None
    ) -> Dict[str, Any]:
        """
        Generate an outline for a finding with context documents
        
        Args:
            finding_name: Name of the finding
            description: Description of the finding
            context_docs: List of context documents to consider
            synonyms: List of synonyms for the finding name
            
        Returns:
            Dictionary containing the generated outline
        """
        template = self._load_template("get_finding_outline_with_context.md.jinja")
        prompt = template.render(
            finding_name=finding_name,
            description=description,
            context_docs=context_docs,
            synonyms=synonyms or []
        )
        response = self.query(prompt)
        
        try:
            # Attempt to parse the JSON response
            import json
            # Find the JSON part of the response (between ```json and ```)
            json_part = response.split("```json")[1].split("```")[0].strip()
            return json.loads(json_part)
        except (IndexError, json.JSONDecodeError) as e:
            raise ValueError(f"Failed to parse LLM response as JSON: {str(e)}")
    
    def query_with_context(self, query: str, context_docs: List[Dict[str, Any]]) -> str:
        """
        Query the LLM with context documents
        
        Args:
            query: The query to ask
            context_docs: List of context documents to consider
            
        Returns:
            The LLM's response
        """
        template = self._load_template("query_with_context.md.jinja")
        prompt = template.render(
            query=query,
            context_docs=context_docs
        )
        return self.query(prompt) 