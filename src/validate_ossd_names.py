import pandas as pd
import json
import os
from pathlib import Path
from typing import List, Set, Dict
from ossdirectory import fetch_data
from ossdirectory.fetch import OSSDirectory

def get_all_csv_files(data_dir: str = "data") -> List[Path]:
    """Find all CSV files in the data directory recursively"""
    return list(Path(data_dir).rglob("*.csv"))

def load_project_names_from_csv(csv_path: Path) -> Set[str]:
    """Extract unique project names from a CSV file"""
    df = pd.read_csv(csv_path)
    if 'to_project_name' not in df.columns:
        return set()
    return set(df['to_project_name'].dropna().unique())

def get_valid_project_names(data: OSSDirectory) -> Set[str]:
    """Get set of valid project names from OSS Directory"""
    return {project['name'] for project in data.projects}

def update_project_name_in_csvs(old_name: str, new_name: str, csv_files: List[Path]) -> None:
    """Update project name in all CSV files where it appears"""
    for csv_path in csv_files:
        df = pd.read_csv(csv_path)
        if 'to_project_name' not in df.columns:
            continue
        
        if old_name in df['to_project_name'].values:
            df['to_project_name'] = df['to_project_name'].replace(old_name, new_name)
            df.to_csv(csv_path, index=False)
            print(f"Updated {old_name} to {new_name} in {csv_path}")

def main():
    # Load OSS Directory data
    data: OSSDirectory = fetch_data()
    valid_projects = get_valid_project_names(data)
    
    # Get all CSV files
    csv_files = get_all_csv_files()
    
    # Collect all unique project names from CSVs
    all_csv_projects: Set[str] = set()
    for csv_file in csv_files:
        all_csv_projects.update(load_project_names_from_csv(csv_file))
    
    # Find missing projects
    missing_projects = all_csv_projects - valid_projects
    
    if not missing_projects:
        print("All project names are valid!")
        return
    
    print("\nFound invalid project names:")
    for project in missing_projects:
        containing_files = [
            csv_file for csv_file in csv_files 
            if project in load_project_names_from_csv(csv_file)
        ]
        print(f"\n\n- {project} (found in:")
        for file in containing_files:
            print(f"  - {file}")
        
        while True:
            new_name = input(f"\nEnter valid project name for '{project}' (or 'skip' to continue): ").strip()
            
            if new_name.lower() == 'skip':
                break
                
            if new_name in valid_projects:
                update_project_name_in_csvs(project, new_name, csv_files)
                break
            else:
                print(f"'{new_name}' is not a valid project name. Please try again.")

if __name__ == "__main__":
    main()