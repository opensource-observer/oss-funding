import csv
import json
import math
import yaml
import argparse
import os


def nan_to_null(value):
    if isinstance(value, float) and math.isnan(value):
        return None
    raise TypeError(f"Object of type {type(value)} is not JSON serializable")


def load_dao_metadata(yaml_file):
    with open(yaml_file, 'r') as file:
        dao_metadata = yaml.safe_load(file)
    return dao_metadata

def validate_metadata(metadata):
    required_keys = ["application_url", "application_name", "token_amount", "token_unit"]
    for key in required_keys:
        if key not in metadata:
            print(f"Warning: Missing key '{key}' in metadata. Using default values.")

def process_row(row, application_id):
    project_name = row['to_project_name']
    # Use a default value (e.g., 0) if 'amount' is missing or invalid
    try:
        amount = float(row['amount'])
    except ValueError:
        amount = 0  # Default value for invalid or missing 'amount'    
    funding_date = row['funding_date']
    metadata = json.loads(row['metadata'])
    validate_metadata(metadata)

    application = {
        "type": "GrantApplication",
        "id": str(application_id),
        "grantPoolId": row['grant_pool_name'],  
        "grantPoolName": row['grant_pool_name'],  
        "projectsURI": metadata.get("application_url", "URL not available"),  # Default value if key is missing
        "projectId": project_name.lower().replace(" ", "-") if project_name else "unknown-project",
        "projectName": metadata.get("application_name", "Unnamed Project"),  # Default value
        "createdAt": funding_date + "T00:00:00Z",
        "contentURI": metadata.get("application_url", "Content URL not available"),
        "fundsAsked": [
            {
                "amount": amount,
                "denomination": "USD"
            }
        ],
        "fundsApproved": [
            {
                "amount": metadata.get("token_amount", "Unknown"),  # Default to 0
                "denomination": metadata.get("token_unit", "Unknown")  # Default to "Unknown"
            }
        ]
    }

    return application


def generate_application_uri(csv_file, dao_name, dao_type):
    base_structure = {
        "@context": "http://www.daostar.org/schemas",
        "name": dao_name.capitalize(),  
        "type": dao_type.capitalize(), 
        "grant_pools": []
    }

    with open(csv_file, newline='', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        application_id = 1  

        grant_pools_dict = {}

        for row in reader:
            grant_pool_name = row['grant_pool_name']
            if grant_pool_name not in grant_pools_dict:
                grant_pools_dict[grant_pool_name] = {
                    "type": "GrantPool",
                    "name": grant_pool_name,
                    "applications": []
                }
            
            application = process_row(row, application_id)
            grant_pools_dict[grant_pool_name]['applications'].append(application)
            application_id += 1

        base_structure['grant_pools'] = list(grant_pools_dict.values())

    return json.dumps(base_structure, indent=4, default=nan_to_null)

def generate_grant_pool_json(yaml_file, dao_name, dao_type):
    dao_metadata = load_dao_metadata(yaml_file)
    grant_pool_json = {
        "@context": "http://www.daostar.org/schemas",
        "name": dao_name.capitalize(), 
        "type": dao_type.capitalize(),
        "grantPools": []
    }
    
    for pool_name in dao_metadata['grant_pools']:
        grant_pool_name = pool_name['name']
        grant_pool = {
            "type": "GrantPool",
            "id": grant_pool_name,
            "name": grant_pool_name,
            "description": f"Grants pool for {grant_pool_name}",
            "isOpen": False,
            "applicationsURI": f"https://raw.githubusercontent.com/opensource-observer/oss-funding/refs/heads/main/daoip-5/json/{dao_metadata['name']}/{grant_pool_name}_applications_uri.json",  
            "requiredCredentials": ["DAO Attestation", "KYC"],  
        }
        
        grant_pool_json["grantPools"].append(grant_pool)
    
    return json.dumps(grant_pool_json, indent=4, default=nan_to_null)

def ensure_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)
    return path

def get_csv_filename_without_extension(csv_file_path):
    return os.path.splitext(os.path.basename(csv_file_path))[0]

def parse_arguments():
    parser = argparse.ArgumentParser(description='Generate Applications URI and/or Grants Pool JSON')
    
    parser.add_argument('--path', type=str, required=True, help='Root path of the folder to crawl')
    
    return parser.parse_args()

def find_files(root_path):
    yaml_file = None
    csv_files = []

    # Traverse the directory
    for dirpath, _, filenames in os.walk(root_path):
        for file in filenames:
            if file.endswith('.yaml') and yaml_file is None:
                yaml_file = os.path.join(dirpath, file)
            elif file.endswith('.csv') and 'uploads' in dirpath:
                csv_files.append(os.path.join(dirpath, file))
    
    if not yaml_file:
        raise FileNotFoundError("No YAML file found at the root of the directory")
    if not csv_files:
        raise FileNotFoundError("No CSV files found in the 'uploads' subdirectories")
    
    return yaml_file, csv_files


def create_folder_based_on_path(base_path, input_path):
    folder_name = os.path.basename(input_path.rstrip('/'))  # Get the last part of the provided path
    unique_folder_path = os.path.join(base_path, folder_name)
    return ensure_folder(unique_folder_path)

if __name__ == "__main__":
    args = parse_arguments()
    root_path = args.path
    
    yaml_file, csv_files = find_files(root_path)

    dao_metadata = load_dao_metadata(yaml_file)
    dao_name = dao_metadata.get('name', 'Unknown Project')  # Default to "Unknown Project" if not found
    dao_type = dao_metadata.get('type', 'DAO')  # Default to "DAO" if not found

    # Use relative path based on the project's structure
    base_json_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '../json'))
    json_folder = create_folder_based_on_path(base_json_folder, root_path)

    for csv_file in csv_files:
        csv_filename = get_csv_filename_without_extension(csv_file)

        applications_uri_json = generate_application_uri(csv_file, dao_name, dao_type)
        applications_file_name = os.path.join(json_folder, f"{csv_filename}_applications_uri.json")
        with open(applications_file_name, 'w') as outfile:
            outfile.write(applications_uri_json)
        print(f"Applications URI JSON has been generated and saved to {applications_file_name}")

    grants_pool_file_name = os.path.join(json_folder, 'grants_pool.json')
    grant_pool_json = generate_grant_pool_json(yaml_file, dao_name, dao_type)
    with open(grants_pool_file_name, 'w') as outfile:
        outfile.write(grant_pool_json)
    print(f"Grants Pool JSON has been generated and saved to {grants_pool_file_name}")
