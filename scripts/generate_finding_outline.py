#!/usr/bin/env python

import argparse
from reportfindingrefiner.finding_model_tools import (
    generate_finding_description,
    generate_finding_outline
)
from reportfindingrefiner.config import DEFAULT_MODEL, DEFAULT_DB_PATH

def main():
    parser = argparse.ArgumentParser(description="Generate a finding model outline using the LLM.")
    parser.add_argument("--name", required=True, help="Name of the finding")
    parser.add_argument("--description", help="Optional description of the finding (if not provided, will be generated)")
    parser.add_argument("--synonyms", nargs="*", help="Optional synonyms for the finding")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="LLM model to use")
    parser.add_argument("--db_path", default=DEFAULT_DB_PATH, help="Path to LanceDB folder")
    args = parser.parse_args()

    try:
        # Generate description if not provided
        if not args.description:
            print("\nGenerating finding description...")
            args.description = generate_finding_description(
                finding_name=args.name,
                model=args.model
            )
            print("\nGenerated Description:")
            print("-" * 80)
            print(args.description)
            print("-" * 80)

        # Generate outline
        print("\nGenerating finding outline...")
        finding_model = generate_finding_outline(
            name=args.name,
            description=args.description,
            synonyms=args.synonyms,
            model=args.model,
            db_path=args.db_path
        )
        
        print("\nGenerated Finding Model:")
        print("-" * 80)
        print(finding_model.json(indent=2))
        print("-" * 80)

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()