#!/usr/bin/env python3
import pandas as pd
import json

def extract_autoaction():
    """Extract AutoAction project from SCF 29 CSV"""
    try:
        df = pd.read_csv('attached_assets/scf_29_1758450689275.csv', dtype=str, keep_default_na=False)
        
        # Find AutoAction in SCF #29
        autoaction_row = df[(df['Submission / Project'] == 'AutoAction') & (df['Round'] == 'SCF #29')]
        
        if autoaction_row.empty:
            print("AutoAction not found in SCF #29")
            return None
            
        # Convert to dictionary
        project_data = autoaction_row.iloc[0].to_dict()
        
        # Clean up the data
        for key, value in project_data.items():
            if pd.isna(value) or value == 'nan':
                project_data[key] = ""
        
        print(f"Found AutoAction:")
        print(f"Status: {project_data.get('Status', 'N/A')}")
        print(f"Total Awarded: {project_data.get('Total Awarded (USD)', 'N/A')}")
        print(f"Total Paid: {project_data.get('Total Paid (USD)', 'N/A')}")
        print(f"Category: {project_data.get('Category (from Project)', 'N/A')}")
        
        # Save data
        with open('/tmp/autoaction_data.json', 'w') as f:
            json.dump(project_data, f, indent=2)
        
        return project_data
        
    except Exception as e:
        print(f"Error extracting AutoAction: {e}")
        return None

if __name__ == "__main__":
    extract_autoaction()
    print("AutoAction data extracted!")