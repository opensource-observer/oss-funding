import csv
import json
import yaml
import argparse
import os

def load_dao_metadata(yaml_file):
    with open(yaml_file, 'r') as file:
        dao_metadata = yaml.safe_load(file)
    return dao_metadata

def process_row(row, application_id):
    project_name = row['to_project_name']
    amount = float(row['amount'])
    funding_date = row['funding_date']
    metadata = json.loads(row['metadata'])

    application = {
        "type": "GrantApplication",
        "id": str(application_id),
        "grantPoolId": row['grant_pool_name'],  
        "grantPoolName": row['grant_pool_name'],  
        "projectsURI": metadata["application_url"],
        "projectId": project_name.lower().replace(" ", "-") if project_name else "unknown-project",
        "projectName": metadata["application_name"],
        "createdAt": funding_date + "T00:00:00Z",
        "contentURI": metadata["application_url"],
        "fundsAsked": [
            {
                "amount": amount,
                "denomination": "USD"
            }
        ],
        "fundsApproved": [
            {
                "amount": metadata["token_amount"],
                "denomination": metadata["token_unit"]
            }
        ]
    }

    return application

def generate_application_uri(csv_file):
    base_structure = {
        "@context": "http://www.daostar.org/schemas",
        "name": "Unknown Project",  
        "type": "DAO",
        "grant_pools": []
    }

    with open(csv_file, newline='', encoding='utf-8') as csvfile:
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

    return json.dumps(base_structure, indent=4)

def generate_grant_pool_json(yaml_file):
    dao_metadata = load_dao_metadata(yaml_file)
    grant_pool_json = {
        "@context": "http://www.daostar.org/schemas",
        "name": dao_metadata['name'],
        "type": dao_metadata['type'],
        "grantPools": []
    }
    
    for pool_name in dao_metadata['grant_pools']:
        grant_pool = {
            "type": "GrantPool",
            "id": pool_name,  
            "name": pool_name,
            "description": f"Grants pool for {pool_name}.", 
            "isOpen": False,
            "applicationsURI": f"https://{dao_metadata['name']}.org/applications/{pool_name}_example.json",  # Example
            "governanceURI": f"https://{dao_metadata['name']}.org/governance/{pool_name}_example.md",  # Example
            "attestationIssuersURI": f"https://{dao_metadata['name']}.org/attestations/{pool_name}_example.json",  # Example
            "requiredCredentials": ["DAO Attestation", "KYC"],  # Example credentials, can be modified
            "email": "rashmi@daostar.org",  # Example email
            "image": f"https://{dao_metadata['name']}.org/images/{pool_name}.png",  # Example image URL
            "coverImage": f"https://{dao_metadata['name']}.org/images/{pool_name}_cover.png"  # Example cover image URL
        }
        
        grant_pool_json["grantPools"].append(grant_pool)
    
    return json.dumps(grant_pool_json, indent=4)

def ensure_json_folder():
    folder_path = './daoip-5/json/'
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    return folder_path

def get_csv_filename_without_extension(csv_file_path):
    return os.path.splitext(os.path.basename(csv_file_path))[0]

def parse_arguments():
    parser = argparse.ArgumentParser(description='Generate Applications URI and/or Grants Pool JSON')
    
    parser.add_argument('--csv_file', type=str, required=True, help='Path to the CSV file containing project data')
    parser.add_argument('--yaml_file', type=str, help='Path to the YAML file containing metadata (required for grants pool generation)')
    
    parser.add_argument('--generate', type=str, choices=['applications', 'grants', 'both'], default='both',
                        help='Choose what to generate: applications, grants, or both')
    
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()

    csv_file = args.csv_file
    yaml_file = args.yaml_file

    json_folder = ensure_json_folder()

    if args.generate in ['applications', 'both']:
        applications_uri_json = generate_application_uri(csv_file)
        csv_filename = get_csv_filename_without_extension(csv_file)
        applications_file_name = os.path.join(json_folder, f"{csv_filename}_applications_uri.json")
        with open(applications_file_name, 'w') as outfile:
            outfile.write(applications_uri_json)
        print(f"Applications URI JSON has been generated and saved to {applications_file_name}")

    if args.generate in ['grants', 'both']:
        if not yaml_file:
            print("Error: YAML file is required for generating grants pool JSON")
        else:
            grant_pool_json = generate_grant_pool_json(yaml_file)
            grants_pool_file_name = os.path.join(json_folder, f"{get_csv_filename_without_extension(csv_file)}_grants_pool.json")
            with open(grants_pool_file_name, 'w') as outfile:
                outfile.write(grant_pool_json)
            print(f"Grants Pool JSON has been generated and saved to {grants_pool_file_name}")
