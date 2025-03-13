#!/usr/bin/env python

import argparse
import json
from reportfindingrefiner.finding_model_tools import list_finding_models
from reportfindingrefiner.config import DEFAULT_DB_PATH
import os

def main():
    parser = argparse.ArgumentParser(description="List all finding models in the database.")
    parser.add_argument("--format", choices=["summary", "full"], default="summary",
                      help="Output format (summary or full JSON)")
    parser.add_argument("--db_path", default=DEFAULT_DB_PATH, help="Path to LanceDB folder")
    args = parser.parse_args()

    try:
        # Check if database exists
        if not os.path.exists(os.path.join(args.db_path, "table")):
            print("\nNo finding models database found.")
            return

        models = list_finding_models(db_path=args.db_path)
        
        if not models:
            print("\nNo finding models found in the database.")
            return
            
        if args.format == "summary":
            print("\nFound Finding Models:")
            print("-" * 80)
            for model in models:
                print(f"Name: {model['name']}")
                # Use get() to safely access the text field with either name
                text = model.get('markdown_text') or model.get('text', 'No text available')
                print(f"Text: {text[:200]}...")
                print("-" * 40)
        else:
            print(json.dumps(models, indent=2))
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()