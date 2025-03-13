#!/usr/bin/env python3
"""
Script for managing finding models.
"""

import argparse
import sys
import json
from reportfindingrefiner.services.finding_model_service import FindingModelService
from reportfindingrefiner.models.finding_model import FindingModelBase
from common import setup_common_args, setup_search_args

def main():
    parser = argparse.ArgumentParser(description="Manage finding models")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List all finding models")
    list_parser = setup_common_args(list_parser)
    
    # View command
    view_parser = subparsers.add_parser("view", help="View a specific finding model")
    view_parser = setup_common_args(view_parser)
    view_parser.add_argument("name", help="Name of the finding model to view")
    view_parser.add_argument(
        "--format", 
        choices=["json", "markdown"],
        default="markdown",
        help="Output format (default: markdown)"
    )
    
    # Create command
    create_parser = subparsers.add_parser("create", help="Create a new finding model")
    create_parser = setup_common_args(create_parser)
    create_parser = setup_search_args(create_parser)
    create_parser.add_argument("name", help="Name of the finding")
    create_parser.add_argument(
        "--description", "-d",
        help="Description of the finding (if not provided, one will be generated)"
    )
    create_parser.add_argument(
        "--synonyms", "-s",
        nargs="+",
        help="Synonyms for the finding name"
    )
    create_parser.add_argument(
        "--use-context", "-c",
        action="store_true",
        help="Use context from searching reports"
    )
    
    args = parser.parse_args()
    
    # Initialize the finding model service
    finding_model_service = FindingModelService(
        db_path=args.db_path,
        table_name="findings",
        reports_table=args.table_name
    )
    
    try:
        if args.command == "list":
            # List all finding models
            models = finding_model_service.get_all_finding_models()
            
            print(f"Found {len(models)} finding models:")
            for i, model in enumerate(models, 1):
                print(f"{i}. {model['name']}")
            
        elif args.command == "view":
            # View a specific finding model
            model = finding_model_service.get_finding_model(args.name)
            
            if model is None:
                print(f"❌ Finding model '{args.name}' not found!")
                return 1
            
            if args.format == "json":
                print(json.dumps(model["model_data"], indent=2))
            else:
                # Create FindingModelBase instance for markdown rendering
                finding_model = FindingModelBase.model_validate(model["model_data"])
                print(finding_model.as_markdown())
                
                if "extended_detail" in model and model["extended_detail"]:
                    print("\n## Extended Detail\n")
                    print(model["extended_detail"])
            
        elif args.command == "create":
            # Check if description is provided or should be generated
            if args.description:
                description = args.description
            else:
                print(f"Generating description for '{args.name}'...")
                description = finding_model_service.generate_description(args.name)
                print(f"Generated description: {description}")
            
            # Generate outline
            if args.use_context:
                print(f"Generating outline with context for '{args.name}'...")
                outline = finding_model_service.generate_outline_with_context(
                    finding_name=args.name,
                    description=description,
                    search_mode=args.mode,
                    limit=args.limit,
                    synonyms=args.synonyms
                )
            else:
                print(f"Generating outline for '{args.name}'...")
                outline = finding_model_service.generate_outline(
                    finding_name=args.name,
                    description=description,
                    synonyms=args.synonyms
                )
            
            # Create FindingModelBase instance
            finding_model = FindingModelBase.model_validate(outline)
            
            # Save the model
            result = finding_model_service.save_finding_model(finding_model)
            
            print(f"✅ Successfully created finding model '{args.name}'!")
            print("\nPreview:")
            print(finding_model.as_markdown())
            
        else:
            parser.print_help()
            return 1
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        if hasattr(args, 'verbose') and args.verbose:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main()) 