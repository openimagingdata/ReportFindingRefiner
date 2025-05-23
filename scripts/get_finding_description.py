import argparse
from reportfindingrefiner.finding_model_tools import generate_finding_description
from reportfindingrefiner.config import DEFAULT_MODEL

def main():
    parser = argparse.ArgumentParser(description="Generate a description for a finding using the LLM.")
    parser.add_argument("--finding_name", required=True, help="Name of the finding to describe")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="LLM model to use")
    args = parser.parse_args()

    try:
        description = generate_finding_description(
            finding_name=args.finding_name,
            model=args.model
        )
        print("\nGenerated Description:")
        print("-" * 80)
        print(description)
        print("-" * 80)
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()