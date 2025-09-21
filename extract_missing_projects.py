#!/usr/bin/env python3
import pandas as pd
import json
from datetime import datetime

def extract_project_data(csv_file, project_name, round_name):
    """Extract project data from CSV file"""
    try:
        # Read CSV with proper handling of multiline fields
        df = pd.read_csv(csv_file, dtype=str, keep_default_na=False)
        
        # Find the project
        project_row = df[df['Submission / Project'] == project_name]
        
        if project_row.empty:
            print(f"Project '{project_name}' not found in {csv_file}")
            return None
            
        # Convert to dictionary
        project_data = project_row.iloc[0].to_dict()
        
        # Clean up the data
        for key, value in project_data.items():
            if pd.isna(value) or value == 'nan':
                project_data[key] = ""
        
        print(f"\nFound project: {project_name}")
        print(f"Round: {project_data.get('Round', 'N/A')}")
        print(f"Status: {project_data.get('Status', 'N/A')}")
        print(f"Total Awarded: {project_data.get('Total Awarded (USD)', 'N/A')}")
        print(f"Total Paid: {project_data.get('Total Paid (USD)', 'N/A')}")
        print(f"Category: {project_data.get('Category (from Project)', 'N/A')}")
        
        return project_data
        
    except Exception as e:
        print(f"Error reading {csv_file}: {e}")
        return None

# Extract missing projects
print("=== Extracting Missing Projects ===")

# SCF 35 - Stellar DeFi Dune Dashboards
stellar_dune = extract_project_data('attached_assets/scf_35_1758450689274.csv', 
                                   'Stellar DeFi Dune Dashboards', 'SCF #35')

# SCF 34 - Greep POS/ Greep pay
greep_pos = extract_project_data('attached_assets/scf_34_1758450689274.csv', 
                                'Greep POS/ Greep pay', 'SCF #34')

# Save extracted data
if stellar_dune:
    with open('/tmp/stellar_dune_data.json', 'w') as f:
        json.dump(stellar_dune, f, indent=2)
    print("Stellar DeFi Dune Dashboards data saved to /tmp/stellar_dune_data.json")

if greep_pos:
    with open('/tmp/greep_pos_data.json', 'w') as f:
        json.dump(greep_pos, f, indent=2)
    print("Greep POS data saved to /tmp/greep_pos_data.json")

print("\n=== Extraction Complete ===")