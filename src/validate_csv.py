import csv
import sys
import requests
from typing import List, Dict

def fetch_oso_projects() -> List[str]:
    url = "https://www.opensource.observer/api/v1/graphql"
    query = """
    query projects {
      oso_projectsV1 {
        projectName
      }
    }
    """
    
    response = requests.post(url, json={"query": query})
    if response.status_code == 200:
        data = response.json()
        projects = [item["projectName"] for item in data["data"]["oso_projectsV1"]]
        return projects
    else:
        print(f"Error fetching data from OSO API: {response.status_code}")
        sys.exit(1)

def validate_csv(csv_file: str, oso_projects: List[str]) -> Dict[str, List[str]]:
    valid_projects = []
    invalid_projects = []
    
    with open(csv_file, 'r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            project_name = row.get('to_project_name', '').strip()
            if project_name:
                if project_name in oso_projects:
                    valid_projects.append(project_name)
                else:
                    invalid_projects.append(project_name)
    
    return {"valid": valid_projects, "invalid": invalid_projects}

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <csv_file>")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    
    print("Fetching project data from OSO API...")
    oso_projects = fetch_oso_projects()
    
    print("Validating projects in the CSV file...")
    results = validate_csv(csv_file, oso_projects)
    
    print("\nValidation Results:")
    print(f"Valid projects: {len(results['valid'])}")
    print(f"Invalid projects: {len(results['invalid'])}")
    
    if results['invalid']:
        print("\nThe following project names don't exist in the OSO database:")
        for project in results['invalid']:
            print(f"- {project}")

if __name__ == "__main__":
    main()