import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set

from ossdirectory import fetch_data
from ossdirectory.fetch import OSSDirectory


def fetch_oss_projects() -> Set[str]:
    """Fetch all project names from the OSS Directory."""
    data: OSSDirectory = fetch_data()
    return {project["name"] for project in data.projects}


def validate_csv(csv_path: Path, oss_projects: Set[str]) -> Dict[str, List[str]]:
    """
    Validate project names in CSV file against OSS Directory.

    Args:
        csv_path: Path to the CSV file
        oss_projects: Set of valid project names

    Returns:
        Dictionary with 'valid' and 'invalid' project lists
    """
    results = defaultdict(list)

    try:
        with csv_path.open("r", encoding="utf-8") as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                project_name = row.get("to_project_name", "").strip()
                if not project_name:
                    continue

                category = "valid" if project_name in oss_projects else "invalid"
                results[category].append(project_name)
    except FileNotFoundError:
        print(f"Error: File '{csv_path}' not found.")
        sys.exit(1)
    except csv.Error as e:
        print(f"Error reading CSV file: {e}")
        sys.exit(1)

    return dict(results)


def display_results(results: Dict[str, List[str]]) -> None:
    """Display validation results in a formatted way."""
    print("\nValidation Results:")
    print(f"Valid projects: {len(results.get('valid', []))}")
    print(f"Invalid projects: {len(results.get('invalid', []))}")

    if results.get("invalid"):
        print("\nThe following project names don't exist in the OSS Directory:")
        for project in sorted(results["invalid"]):
            print(f"- {project}")


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Validate project names in a CSV file against the OSS Directory."
    )
    parser.add_argument(
        "csv_file", type=Path, help="Path to the CSV file containing project names"
    )
    args = parser.parse_args()

    print("Fetching project data from OSS directory...")
    oss_projects = fetch_oss_projects()

    print(f"Validating projects in '{args.csv_file}'...")
    results = validate_csv(args.csv_file, oss_projects)

    display_results(results)

    sys.exit(1 if results.get("invalid") else 0)


if __name__ == "__main__":
    main()
