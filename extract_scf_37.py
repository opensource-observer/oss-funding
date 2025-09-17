#!/usr/bin/env python3
"""
Extract SCF #37 projects from the larger dataset
"""

import pandas as pd

def extract_scf_37():
    """Extract SCF #37 projects and create separate CSV"""
    
    # Read the large CSV file
    input_file = 'attached_assets/Awarded Submissions [Build only]-By Round (6)_1758108996237.csv'
    
    try:
        print(f"Loading {input_file}...")
        df = pd.read_csv(input_file)
        print(f"Total rows loaded: {len(df)}")
        
        # Filter for SCF #37 projects
        scf_37_projects = df[df['Round'] == 'SCF #37'].copy()
        print(f"Found {len(scf_37_projects)} SCF #37 projects")
        
        # Save to new CSV file
        output_file = 'SCF_37_Projects.csv'
        scf_37_projects.to_csv(output_file, index=False)
        print(f"Saved SCF #37 projects to {output_file}")
        
        # Show basic stats
        if len(scf_37_projects) > 0:
            print("\n=== SCF #37 Project Summary ===")
            
            # Status distribution
            if 'Status' in scf_37_projects.columns:
                print("\nStatus Distribution:")
                status_counts = scf_37_projects['Status'].value_counts()
                for status, count in status_counts.items():
                    print(f"  {status}: {count}")
            
            # Category distribution  
            if 'Category (from Project)' in scf_37_projects.columns:
                print("\nCategory Distribution:")
                category_counts = scf_37_projects['Category (from Project)'].value_counts()
                for category, count in category_counts.items():
                    print(f"  {category}: {count}")
            
            # Award amounts
            if 'Total Awarded (USD)' in scf_37_projects.columns:
                scf_37_projects['Total Awarded (USD)'] = scf_37_projects['Total Awarded (USD)'].replace('[\$,]', '', regex=True)
                scf_37_projects['Total Awarded (USD)'] = pd.to_numeric(scf_37_projects['Total Awarded (USD)'], errors='coerce')
                
                total_awarded = scf_37_projects['Total Awarded (USD)'].sum()
                avg_awarded = scf_37_projects['Total Awarded (USD)'].mean()
                
                print(f"\nFunding Information:")
                print(f"  Total Amount Awarded: ${total_awarded:,.2f}")
                print(f"  Average Award Amount: ${avg_awarded:,.2f}")
            
            # Project names
            print(f"\nProject Names:")
            project_names = scf_37_projects['Submission / Project'].tolist()
            for i, name in enumerate(project_names, 1):
                print(f"  {i}. {name}")
        
        return True
        
    except Exception as e:
        print(f"Error processing file: {e}")
        return False

if __name__ == "__main__":
    extract_scf_37()